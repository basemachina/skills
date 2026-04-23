# Advanced: environment-specific `defineAction`

> **Reader's contract**
> - **What**: Write a single `defineAction` that behaves differently per environment (dev / stg / prd) using env context and `skipDeploy`.
> - **Prereq**: `defineAction.md` (basic shape), `dry-run.md` (`--env` / `--from`).
> - **Out of scope**: Changing action IDs per env (anti-pattern, see §4). Branching the config file itself (use the tsconfig-level `--config`).

## 1. Env context inside an action

JavaScript Server Actions receive `{ vars, secrets }` at runtime. Configure these per-environment in the Web UI, then branch on them from inside the handler:

```js
// src/actions/js-action-codes/send-notification.js
import { executeAction } from "@basemachina/action";

export default async (args, { vars, secrets }) => {
  const endpoint = vars.NOTIFY_ENDPOINT;   // different URL per env
  const isProd = vars.ENV === "prd";

  if (isProd) {
    // production-only behavior
    return await executeAction("send-slack", { text: args.message });
  }
  // dev / stg: log only
  return { success: { logged: args.message } };
};
```

- `vars.ENV` is a convention; pick any key you set in the Web UI per env.
- Secrets (`secrets.SLACK_TOKEN`) are separate from vars and not logged.
- Type definitions for the runtime context live in `node_modules/@basemachina/action/dist/*.d.ts`.

## 2. Using the Web-UI deploy toggle for env-scoped rollout (Phase 1 SDK)

The current SDK has no `skipDeploy` field. For WIP-in-dev rollouts, use the Web UI's per-environment deploy toggle, or simply gate promotion via branch flow (see `three-branch-ops.md`).

Planned `skipDeploy` support is documented at `advanced/skip-deploy-patterns.md` for when the SDK ships it. Do **not** add the field to `defineAction` today — it will not compile.

## 3. Env-specific gRPC `dataSource`

For gRPC actions, `dataSource` is a Web-UI-managed ID that points to a different backend per environment. The action file itself stays the same:

```ts
// src/actions/lookup-user.ts
import { defineAction } from "@basemachina/sdk/oac";

export const lookupUserAction = defineAction({
  id: "lookup-user",
  name: "Lookup user",
  class: "grpc",
  dataSource: "<grpc-data-source-id>",    // same ID across environments; the ID's target differs per env via Web UI config
  fullMethodName: "users.v1.UserService/GetUser",
  body: { payload: '{ "id": "{{ user_id }}" }' },
  parameters: [{ type: "TEXT", name: "user_id", required: true }],
});
```

- Configure the data source (identified by `dataSource: "..."`) once per environment in the Web UI (dev → dev-grpc, stg → stg-grpc, prd → prd-grpc).
- The action code is identical across environments; only the data source binding differs.
- For non-`grpc` / non-`javascript` action kinds (MySQL / REST / GraphQL), manage them entirely via the Web UI until SDK support ships.

## 4. Anti-pattern: env-specific `id`s

**Don't** write `id: "lookup-user-dev"` vs `id: "lookup-user-prd"`. That creates two separate actions, breaks promotion flows (`--from <dev-env>` won't match), and duplicates audit history.

**Do** keep `id` constant across environments. Branch behavior inside the handler (`vars.ENV`) for JavaScript actions, or rely on the Web-UI-configured per-env data source for gRPC.

If you see env-qualified IDs in a legacy project, propose renaming as a separate PR (not bundled with behavior changes) so the dry-run diff is reviewable.

## 5. Anti-pattern: environment-check at the `defineAction` level

**Don't** try to conditionally register:

```ts
// DON'T
export default defineConfig({
  project: { id: "..." },
  actions: [
    ...(process.env.ENV === "prd" ? [prodOnlyAction] : []),
  ],
});
```

The config is evaluated once at `bm sync` time; `process.env.ENV` there is the agent's local env, not the BaseMachina environment. This produces wildly different syncs depending on where the CLI runs.

**Do** register all actions unconditionally and use runtime `vars.ENV` branching (for JavaScript actions) or per-env Web-UI toggling.

## 6. See also

- `skip-deploy-patterns.md` — the 4 legitimate `skipDeploy` flows
- `three-branch-ops.md` — promoting across dev / stg / prd with `--from`
- `helper-composition.md` — sharing env-aware utility code
