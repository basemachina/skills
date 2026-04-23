# Advanced: `skipDeploy` patterns

> **Reader's contract**
> - **What**: How `skipDeploy` is intended to work across 4 legitimate flows, plus the anti-pattern (permanently-skipped dead code).
> - **Prereq**: `defineAction.md`, `dry-run.md`.
> - **Out of scope**: Runtime feature flags (BaseMachina has no LaunchDarkly-style runtime gate; `skipDeploy` is a deploy-time gate).

> **⚠ SDK status (v0.x)**
> `skipDeploy` is **not yet present** in `@basemachina/sdk/oac`'s `ActionConfig`. Adding `skipDeploy: true` to `defineAction` today produces a TypeScript compile error (`defineAction` uses `ExcessOnly` rejection). This reference documents the planned flows so the design is ready when the field ships in a future SDK minor release. Until then, use the Web UI's deploy toggle or branch-flow gating.

## What `skipDeploy` will do (planned)

- `skipDeploy: true` in `defineAction` sets `dev.skip_deploy = true` for that action.
- During `bm sync --env <target> --dry-run` (deploy), if the source has `skip_deploy=true`, the target update is **entirely skipped** — the action is not written to the target env.
- Dev is **still** reflected. `skipDeploy` only controls the downstream deploy.
- `skipDeploy` changes alone do **not** appear in the dry-run diff (the flag controls behavior, not revisions).

See `advanced/three-branch-ops.md` for how this interacts with `--env` / `--from`.

## Legitimate pattern 1: WIP early-merge

Merge unfinished code to `main` without deploying it to stg/prd. The action runs in dev for internal testing.

```ts
export const wipRefundAction = defineAction({
  id: "stripe-refund",
  name: "Stripe refund [WIP]",
  class: "javascript",
  skipDeploy: true,                       // ← main merged but stg/prd not deployed
  code: readFile("./js-action-codes/stripe-refund.js"),
});
```

When ready:

1. Flip `skipDeploy: false`.
2. `bm sync --env "$STG_ENV_ID" --from "$DEV_ENV_ID" --dry-run` — confirm the action appears as `created` in the stg diff.
3. Merge, CI deploys to stg.
4. Repeat for prd.

## Legitimate pattern 2: Code-only sync (dry runs and experiments)

Sync the action to dev for local / dev-env experiments, but never promote. The action stays dev-exclusive:

```ts
export const debugDumpAction = defineAction({
  id: "debug-dump",
  name: "Debug: dump request context",
  class: "javascript",
  skipDeploy: true,                       // permanently dev-only
  code: readFile("./js-action-codes/debug-dump.js"),
});
```

- Clearly label the name `[dev-only]` / `[debug]` to communicate intent.
- Document the deliberate `skipDeploy` in the code's top comment.

Beware the anti-pattern (§5) if the action grows and nobody remembers it's dev-only.

## Legitimate pattern 3: Staged 3-branch rollout

In a dev → stg → prd workflow, keep the action `skipDeploy: false` but gate promotion via branch flow:

- On `main` (dev-tracking branch): action is live in dev.
- PR to `stg` branch: CI runs `bm sync --env "$STG_ENV_ID" --from "$DEV_ENV_ID"` on merge.
- PR to `prd` branch: CI runs `bm sync --env "$PRD_ENV_ID" --from "$STG_ENV_ID"` on merge.

`skipDeploy` does NOT help here directly, but combine it with pattern 1 for actions that need to land on `main` but not yet roll out of dev. See `three-branch-ops.md`.

## Legitimate pattern 4: A/B with one side hidden

Two action variants (`search-v1` and `search-v2`), where only one ships. Keep both in code, mark the unfinished one `skipDeploy: true`:

```ts
export const searchV1 = defineAction({
  id: "search-v1",
  name: "Search",
  class: "grpc",
  dataSource: "<search-grpc-id>",
  fullMethodName: "search.v1.SearchService/Search",
  body: { payload: '{ "q": "{{ q }}" }' },
  parameters: [{ type: "TEXT", name: "q" }],
});

export const searchV2 = defineAction({
  id: "search-v2",
  name: "Search (v2 experimental)",
  class: "grpc",
  dataSource: "<search-v2-grpc-id>",
  fullMethodName: "search.v2.SearchService/Search",
  body: { payload: '{ "q": "{{ q }}" }' },
  skipDeploy: true,                       // (planned field) not deployed to stg/prd yet
  parameters: [{ type: "TEXT", name: "q" }],
});
```

When v2 is ready, flip `v2.skipDeploy = false` and (in the same PR or a subsequent one) drop v1. The Web UI audit trail retains both.

## Anti-pattern: permanent `skipDeploy: true` → dead code

`skipDeploy: true` actions that never flip back become dead weight. Symptoms:

- The action exists in `basemachina.config.ts` for 6+ months with `skipDeploy: true`.
- No one on the team can explain what it's for.
- Changes to the handler haven't been tested outside of dev.

**How to fix**:

- If still needed → promote (flip `skipDeploy: false`, dry-run, ship).
- If abandoned → delete the import from `basemachina.config.ts` (logical delete; revisions are preserved, can be re-imported later).
- If genuinely dev-only → add a top-of-file comment `// skipDeploy: dev-only utility, owner: @name, reason: <...>` and a lint exception.

## Checklist when adding `skipDeploy: true`

- [ ] Intent documented in the action's `name` suffix (`[WIP]` / `[debug]` / `[dev-only]`) or a code comment.
- [ ] Owner and expected flip date identified (if temporary).
- [ ] `bm sync --dry-run` shows it appears in dev only (for deploy-target `--env` dry-runs, it should not appear).
- [ ] The next step to promote (or retire) is captured in a ticket.

## See also

- `env-specific-actions.md` — env-scoped behavior within a single action
- `three-branch-ops.md` — `--from` for promotion flows
