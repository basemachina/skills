# `defineAction` / `defineConfig` reference

> **Reader's contract**
> - **What**: Write `defineAction` for the **two classes the SDK currently supports** (`javascript` and `grpc`), register actions in `defineConfig`, and pick the right JS Server Action result type.
> - **Prereq**: A bm project with `@basemachina/sdk` installed (`"@basemachina/sdk": "latest"` + `"@basemachina/cli": "latest"`). `basemachina.config.ts` at the project root.
> - **Out of scope**: CLI flags (see `dry-run.md`), error recovery (see `errors.md`), env-specific branching (see `advanced/env-specific-actions.md`).

> **⚠ SDK status (v0.x)**
> `@basemachina/sdk/oac` exports `defineAction` that accepts **only** `class: "javascript"` or `class: "grpc"`. The Web UI supports more kinds (MySQL / PostgreSQL / REST / GraphQL / etc.), but those are not available via `defineAction` yet.
> **Do not generate `class: "mysql"` / `"postgresql"` / `"restapi"` / `"graphql"` — TypeScript will reject them (the `defineAction` type uses `ExcessOnly` to reject unknown fields and unions only the 2 supported classes). Use the Web UI for those until SDK support ships.**

Do not rely on memory for type signatures. Before writing code, Read `node_modules/@basemachina/sdk/dist/oac/index.d.ts` to confirm the current shape.

## 1. Project skeleton

The minimum bm project has three parts: a config file at the project root, per-action TypeScript files, and (for JavaScript actions) their JavaScript handler files.

```
my-bm-project/
├── basemachina.config.ts                # defineConfig with project.id + actions[]
├── package.json                         # @basemachina/sdk + @basemachina/cli
├── tsconfig.json                        # extends @basemachina/sdk/tsconfig.json
└── src/
    └── actions/
        ├── list-users.ts                # defineAction (javascript)
        ├── lookup-user.ts               # defineAction (grpc)
        └── js-action-codes/             # JavaScript action handlers
            ├── list-users.js
            └── send-email.js
```

`actions/` and `js-action-codes/` names are conventional; the path you pass to `readFile()` is what matters.

## 2. `defineConfig`

```ts
import { defineConfig } from "@basemachina/sdk/oac";
import { listUsersAction } from "./src/actions/list-users";
import { lookupUserAction } from "./src/actions/lookup-user";

export default defineConfig({
  project: { id: "<your-project-id>" },
  actions: [listUsersAction, lookupUserAction],
});
```

- `project.id` is a BaseMachina-internal ID visible in the Web UI. There is no CLI command to list it.
- `actions` is a flat array. Split imports across files for readability; the bundler flattens them.
- **`OacConfig` has exactly two fields**: `project` + `actions`. There are no `views` / `environments` / `secrets` fields — do not invent them.

## 3. `defineAction` common shape

Every action, regardless of class, shares these fields:

```ts
{
  id: string;                         // unique within the project, kebab-case
  name: string;                       // human-readable, shown in the Web UI
  class: "javascript" | "grpc";       // the class discriminator
  parameters?: ParameterConfig[];     // optional
  // ...class-specific fields (see §4 and §5)
}
```

`defineAction` is an **identity function** that enforces types at compile time. It rejects unknown fields via `ExcessOnly`, so adding e.g. `skipDeploy: true` will cause a TS error today.

### Parameter input types (9, discriminated union on `type`)

The SDK's `ParameterConfig` (for JavaScript actions) unions:

- `TEXT` — free text, with optional `regexValidation`, `selectOptions`, `multiline`, `minLength`/`maxLength`, `masterDataFetchSettingId`
- `NUMBER` — numeric, with `min` / `max`
- `BOOL` — `formatType: "RAW"` (boolean) or `"STRING"` (`trueValue` / `falseValue`)
- `DATE` — with `includeTime` / `format` / `useUnixTimestamp`
- `FILE` — file upload, `maxBytes` optional
- `JSON` — typed JSON, with `valueType: "TEXT" | "NUMBER" | "DATE"`
- `SYSTEM_VALUE` — system-supplied value (not user input)
- `ARRAY` — recursive array, `childElement` of any Element type, `minItems` / `maxItems`
- `TUPLE` — heterogeneous fixed-length tuple, `tupleElements` array with `{ label, childElement }`

gRPC actions use a slightly narrower union (`ParameterConfig$1`) that excludes `FILE`.

**`SQL` and `VAR` do not exist as parameter types.** If you see them in older docs, they are not part of the current SDK.

Inspect `node_modules/@basemachina/sdk/dist/oac/index.d.ts` for every field. The per-type shape evolves across SDK minor versions.

## 4. `class: "javascript"`

```ts
import { defineAction, readFile } from "@basemachina/sdk/oac";

export const listUsersAction = defineAction({
  id: "list-users",
  name: "List users",
  class: "javascript",
  code: readFile("./js-action-codes/list-users.js"),
  parameters: [
    { type: "TEXT", name: "email", required: true },
  ],
});
```

- `code: string` — the JavaScript source. Use `readFile("./js-action-codes/<file>.js")` (path resolved relative to the calling `.ts` file) or a literal template-string for trivial handlers.
- `parameters`: `ParameterConfig[]` from §3.

### Handler file shape

```js
// src/actions/js-action-codes/list-users.js
import { executeAction } from "@basemachina/action";

/** @type { import("@basemachina/action").Handler } */
export default async (
  args,                              // declared parameters from defineAction.parameters
  { currentUser, vars, secrets },    // context
) => {
  const results = await executeAction("fetch-users", { limit: args.limit });
  if (!results[0].success) {
    return { userError: "Upstream returned no data" };
  }
  return results[0].success;
};
```

- `args` matches the `parameters` schema shape from `defineAction`.
- `currentUser` is the invoking principal (includes email, id).
- `vars` / `secrets` are environment-scoped key-value stores configured in the Web UI.
- `executeAction(id, params)` calls another action by id and returns the structured result.
- `rawExecuteAction({ actionId, actionClass, args })` is the lower-level form that requires passing `actionClass` explicitly.

Consult `node_modules/@basemachina/action/dist/*.d.ts` for the canonical `Handler` / `executeAction` signatures.

### Result types (decision tree)

The return value's **shape** determines how the platform surfaces the outcome. Pick the right one — surfacing affects alerting, user-visible messaging, and audit.

| Return shape | When | User sees | Alert? |
| --- | --- | --- | --- |
| `return { success: ... }` or `return <anything>` | Happy path | The value | No |
| `return { userError: "..." }` | Expected user-caused failure (bad input, permission) | The message | No |
| `return { resultError: "..." }` | Expected business-logic failure (not a user fault, not a bug) | The message | No |
| `return { systemError: "..." }` or `throw` | Unexpected platform/bug/upstream outage | Generic error | Yes (platform-level) |

Decision tree:

1. Is the failure due to **user input** or **permission**? → `userError`.
2. Is it a **known business case** (stock sold out, refund not allowed) that isn't the user's fault? → `resultError`.
3. Is it a **bug or infra problem** (upstream 500, panic, invariant violation)? → `systemError` or `throw`.
4. Otherwise → happy path, return the value directly or `{ success: ... }`.

## 5. `class: "grpc"`

```ts
import { defineAction } from "@basemachina/sdk/oac";

export const lookupUserAction = defineAction({
  id: "lookup-user",
  name: "Lookup user by id",
  class: "grpc",
  dataSource: "<grpc-data-source-id>",
  fullMethodName: "users.v1.UserService/GetUser",
  headers: [
    { name: "X-Trace-Id", value: "{{ trace_id }}" },
  ],
  body: {
    payload: '{\n  "id": "{{ user_id }}"\n}',
  },
  parameters: [
    { type: "TEXT", name: "user_id", required: true },
    { type: "TEXT", name: "trace_id" },
  ],
});
```

- `dataSource: string` — the gRPC data source ID configured in the Web UI. There is no CLI command to list data sources; copy from the Web UI.
- `fullMethodName: string` — fully-qualified method, formatted as `{package}.{Service}/{Method}` (e.g., `users.v1.UserService/GetUser`).
- `headers?: { name: string; value: string }[]` — optional, values can template via `{{ param_name }}`.
- `body.payload: string` — JSON template, values interpolated via `{{ param_name }}` Mustache-style placeholders.
- `parameters?: ParameterConfig$1[]` — the gRPC-parameter variant (`FILE` excluded).

## 6. Action classes the SDK does NOT yet support

The following exist in the Web UI but are **not** part of `defineAction`'s type union in the current SDK:

- `mysql`
- `postgresql`
- `restapi`
- `graphql`

For these, **do not attempt to generate `defineAction` code**. Current TypeScript will fail to compile. Continue managing them via the Web UI until the SDK publishes corresponding configs.

This skill's Phase 1 scope is what the SDK ships today. When support lands, this reference will update with matching sections.

## 7. `readFile` helper

`readFile("./relative/path.js")` is resolved from the `.ts` file that calls it (not from `cwd`). Put handler `.js` files next to the `defineAction` file (for example, `src/actions/js-action-codes/`).

Do NOT try to `import { someCode } from "./handler.js"` — the handler runs on the BaseMachina platform, not in the bundler. Always pass the source as a string via `readFile`.

## 8. Where canonical types live

- `@basemachina/sdk/oac` — `defineConfig`, `defineAction`, `readFile`. Types live in `node_modules/@basemachina/sdk/dist/oac/index.d.ts`.
- `@basemachina/action` — `Handler`, `executeAction`, `rawExecuteAction`. Types live in `node_modules/@basemachina/action/dist/*.d.ts`.

When the SDK version bumps, re-Read the `.d.ts` files and diff against the patterns above; this reference will lag by one minor version.

## 9. See also

- `dry-run.md` — how to validate the changes you just wrote
- `errors.md` — when the `defineAction` you wrote fails validation
- `advanced/env-specific-actions.md` — when the same action needs different behavior per environment
- `advanced/skip-deploy-patterns.md` — planned `skipDeploy` flows (not yet shipped in SDK)
