# Advanced: shared helper composition

> **Reader's contract**
> - **What**: Extract shared utility code across multiple JS Server Actions into a `lib/` directory without breaking the bundler or producing stale revisions.
> - **Prereq**: `defineAction.md` §5 (JS Server Action handlers), §9 (`readFile`).
> - **Out of scope**: SDK-level helpers (`@basemachina/action` — already available). Server Action runtime details (that's a BaseMachina platform concern).

## 1. Why extract helpers

Typical JS handlers accumulate near-duplicate code: error-mapping, fetch wrappers, date formatting, argument validation. Moving these to a shared `lib/` makes updates uniform. But the BaseMachina platform bundles each handler independently, so there are **bundler-specific constraints** to honor.

## 2. Directory layout

```
src/
├── actions/
│   ├── list-users.ts                     # defineAction, references lib via code string
│   ├── send-email.ts
│   └── js-action-codes/
│       ├── list-users.js                 # imports from ../lib
│       ├── send-email.js
│       └── lib/                          # shared helpers
│           ├── fetch-with-retry.js
│           ├── error-map.js
│           └── format-date.js
```

Put `lib/` next to the handlers it serves so relative imports work consistently.

## 3. Writing a shared helper

```js
// src/actions/js-action-codes/lib/fetch-with-retry.js
export async function fetchWithRetry(url, opts = {}, retries = 3) {
  for (let attempt = 0; attempt < retries; attempt++) {
    const r = await fetch(url, opts);
    if (r.ok) return r;
    if (attempt === retries - 1) throw new Error(`HTTP ${r.status} for ${url}`);
    await new Promise((res) => setTimeout(res, 100 * 2 ** attempt));
  }
}
```

Export named functions (not default). Consumer handlers:

```js
// src/actions/js-action-codes/list-users.js
import { fetchWithRetry } from "./lib/fetch-with-retry.js";

export default async (args, { vars }) => {
  const r = await fetchWithRetry(`${vars.API}/users`);
  return await r.json();
};
```

## 4. Bundler gotchas

The BaseMachina platform bundles each JS Server Action into a single file at sync time.

### 4.1 Use relative imports, always

**Do**: `import { x } from "./lib/x.js";`
**Don't**: `import { x } from "lib/x.js";` (path resolution differs between local Node and the platform bundler).

Always include the `.js` extension (ESM strict mode).

### 4.2 Side-effect-free imports only

**Don't**: write modules that execute code at import time:

```js
// lib/init.js — BAD
console.log("loaded!");
const cache = new Map();
fetch("/warmup");                           // runs at import, before handler invoke
export const get = () => cache.get("x");
```

The bundler preserves top-level statements. A side-effect import runs at every cold-start of the handler. Move warmup / caching into an exported factory:

```js
// lib/init.js — GOOD
export const createCache = () => new Map();
```

### 4.3 Do not re-use action IDs for helper modules

The bundler treats `lib/*.js` as plain ES modules; they don't need `defineAction`. Don't accidentally write:

```js
// lib/utils.js — DON'T
import { defineAction } from "@basemachina/sdk/oac";    // wrong file for this
```

`defineAction` belongs only in `src/actions/*.ts`. Helpers in `lib/` are runtime-only JS.

### 4.4 Revision churn when helpers change

When you edit a `lib/*.js` helper used by N actions, **all N actions get an `updated` revision** in the next dry-run. This is correct behavior (their bundled output changed), but can produce a large diff from a tiny edit.

- Plan helper changes as their own PR, separate from action-logic PRs, to keep reviews focused.
- Use `bm sync --dry-run` to preview the full list of affected actions before merging the helper edit.

## 5. Anti-pattern: "shared helper" TypeScript file for actions

**Don't** extract shared TypeScript logic from `defineAction`s into a single TS file and import it:

```ts
// src/shared/action-factory.ts — anti-pattern if you're trying to DRY defineAction
export function makeJsAction(id, name, codePath) {
  return defineAction({ id, name, class: "javascript", code: readFile(codePath) });
}
```

This creates layers of indirection that obscure the dry-run diff and make reviews harder. `defineAction` is already flat and intentionally repetitive — keep it that way.

Acceptable: a helper that returns a `parameters` array or a `code` string is fine. A helper that returns the whole `defineAction` object is not.

## 6. Testing helpers

- Write unit tests for `lib/*.js` with your preferred runner (Vitest / Jest / Node's `test`). Do this in `test/` at the repo root — the bundler only sees `src/actions/`, so tests don't get shipped.
- The BaseMachina platform does not run JS tests in sync. CI runs tests separately (see `templates/github-actions/bm-sync.yml`).

## 7. See also

- `defineAction.md` §5, §9 — handler and `readFile` basics
- `skip-deploy-patterns.md` — staging helpers + actions rollout
- `errors.md` §3 — when a bundle-time error appears in dry-run
