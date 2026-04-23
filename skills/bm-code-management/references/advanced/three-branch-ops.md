# Advanced: 3-branch operations (`--env` / `--from`)

> **Reader's contract**
> - **What**: Run a dev → stg → prd promotion flow using `bm sync --env <target> --from <source> --dry-run`, detect version drift between environments, and stage a rollout safely.
> - **Prereq**: `dry-run.md` (basic command shapes), `skip-deploy-patterns.md` (how `skipDeploy` interacts).
> - **Out of scope**: `bm hotfix` (separate skill, Phase 2). Branch protection rules / GitHub Actions (user's repo concern, see `templates/github-actions/bm-sync.yml`).

## 1. The 3-branch mental model

A typical BaseMachina repo has three branches, each paired with an environment:

| Branch | Environment | Purpose |
| --- | --- | --- |
| `main` (or `dev`) | dev | Source of truth for actions; `bm sync` (no `--env`) targets this |
| `stg` | stg | Pre-production; PR to merge from `main` |
| `prd` | prd | Production; PR to merge from `stg` |

CI on each branch runs a matching `bm sync` command. See `templates/github-actions/bm-sync.yml` for the baseline shape.

## 2. `--from` semantics

`bm sync --env <target> [--from <source>]` computes a diff between `<source>` and `<target>`.

- **Without `--from`**: source is inferred from the current config (effectively the `main` / dev environment).
- **With `--from <source-env-id>`**: source is pinned to that environment's current state (not config). Use when the git branch is not the natural source (e.g., promoting from stg to prd on the prd branch, where `main` is not stg).

### Typical flow

```bash
# Step 1: verify dev ↔ main are in sync (on `main` branch, in a PR)
bm sync --dry-run

# Step 2: promote dev → stg (on `stg` branch, in a PR from main)
bm sync --env "$STG_ENV_ID" --from "$DEV_ENV_ID" --dry-run

# Step 3: promote stg → prd (on `prd` branch, in a PR from stg)
bm sync --env "$PRD_ENV_ID" --from "$STG_ENV_ID" --dry-run
```

Each step always includes `--dry-run` in this skill. CI performs the apply without `--dry-run` on merge.

## 3. Version drift detection

When stg and prd have drifted (for example, a hotfix was applied to prd but not cherry-picked to stg), the dry-run diff will show unexpected `updated` / `deleted` entries.

### How to diagnose

1. Run `bm sync --env "$PRD_ENV_ID" --from "$STG_ENV_ID" --dry-run` and capture the diff.
2. Cross-check each `updated` action against `git log -- actions/<id>.ts` on the `stg` branch.
3. If the diff contains actions that were never edited on `stg`, a hotfix exists on prd that's not in `stg`'s branch. Ask the user about it — do not auto-overwrite.

### Escape hatch (user-driven, not agent-driven)

- If hotfix → backport: cherry-pick the hotfix commit to `stg` (and `main`), re-PR.
- If hotfix → supersede: accept the drift intentionally; note it in the PR body.

Either way, this skill's job is to surface the drift in the dry-run report; the decision is the user's.

## 4. `skipDeploy` interaction (planned, not in current SDK)

Once the SDK ships `skipDeploy`, it will mean the action is **not written** to the target during a `--env` deploy — the action will not show up in the stg/prd diff at all. See `skip-deploy-patterns.md` for the planned flows.

**Phase 1 (current)**: the field does not exist. An action either promotes or doesn't promote based on whether the config registers it. To stage a dev-only action without an SDK `skipDeploy`, keep it registered only in a dev-scoped branch, or manage promotion manually in the Web UI.

## 5. 3-branch CI template outline

See `templates/github-actions/bm-sync.yml` for the actual workflow file. The shape is:

```yaml
on:
  pull_request: { branches: [main, stg, prd] }
  push:         { branches: [main, stg, prd] }

jobs:
  sync:
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - name: Dry-run
        if: github.event_name == 'pull_request'
        run: |
          case "$GITHUB_BASE_REF" in
            main) npx bm sync --dry-run ;;
            stg)  npx bm sync --env "$STG_ENV_ID" --from "$DEV_ENV_ID" --dry-run ;;
            prd)  npx bm sync --env "$PRD_ENV_ID" --from "$STG_ENV_ID" --dry-run ;;
          esac
      - name: Apply
        if: github.event_name == 'push'
        run: |
          case "$GITHUB_REF_NAME" in
            main) npx bm sync ;;
            stg)  npx bm sync --env "$STG_ENV_ID" --from "$DEV_ENV_ID" ;;
            prd)  npx bm sync --env "$PRD_ENV_ID" --from "$STG_ENV_ID" ;;
          esac
```

Env IDs (`DEV_ENV_ID`, `STG_ENV_ID`, `PRD_ENV_ID`) come from repo variables, obtained from the Web UI. No CLI command lists them.

## 6. Common mistakes

- **Running `bm sync` (no `--env`) on the `prd` branch** → this syncs from config against the dev env, which is not what you want on `prd`. The CI template's `case $GITHUB_REF_NAME` dispatch prevents this.
- **Omitting `--from` on the prd branch** → implicit source may fall back to config (dev), and you'll promote dev-latest over stg, skipping any stg-only review signal.
- **Adding a new action on `prd` branch directly** → this creates it on prd without ever existing on dev/stg. Merge from stg → prd instead.

## 7. See also

- `dry-run.md` — the three command shapes
- `skip-deploy-patterns.md` — planned `skipDeploy: true` flows (SDK support pending)
- `env-specific-actions.md` — per-env behavior within a single action
- `templates/github-actions/bm-sync.yml` — the CI template
