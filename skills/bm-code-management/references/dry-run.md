# `bm sync --dry-run` reference

> **Reader's contract**
> - **What**: Run `bm sync` in preview mode, interpret the 5 diff categories, and handle the 50 % safeguard and first-time Web → OAC switchover correctly.
> - **Prereq**: `bm` CLI installed and authenticated (`bm login` completed out-of-band). A bm project with `basemachina.config.ts`.
> - **Out of scope**: Applying changes (CI-only). Writing `defineAction` (see `defineAction.md`). Error recovery (see `errors.md`).

This skill **never** runs `bm sync` without `--dry-run`. Apply is CI. That is not negotiable.

## 1. Three command shapes

| Shape | Purpose | Target |
| --- | --- | --- |
| `bm sync --dry-run` | Push preview: compare config ↔ dev environment | Dev only |
| `bm sync --env <env-id> --dry-run` | Deploy preview: compare source env ↔ target env | Named environment (stg / prd) |
| `bm sync --env <target-id> --from <source-id> --dry-run` | 3-branch deploy preview: promote from explicit source | Named environment with explicit source |

All three accept `--config <path>` for running outside the project root. Run `bm sync --help` yourself to confirm flags — do not rely on memory.

### Typical invocations

```bash
# From the project root, preview the dev push
bm sync --dry-run

# Preview promotion from dev-via-config to staging
bm sync --env "$STAGING_ENV_ID" --dry-run

# Preview promotion from an explicit source env to target
bm sync --env "$PRD_ENV_ID" --from "$STG_ENV_ID" --dry-run

# Run from a different cwd
bm sync --dry-run --config ./path/to/bm-project/basemachina.config.ts
```

## 2. Output format

### 2.a Text format (current, v1 CLI)

Dry-run output groups changes into five categories. Always summarize back to the user using these exact labels.

| Category | Meaning | Typical cause |
| --- | --- | --- |
| **created** | A new action was added to config | New `defineAction` registered in `basemachina.config.ts` |
| **updated** | Existing action's code or parameters changed | Source edit; triggers new revision |
| **deleted** | Action removed from config (**logical** delete) | Action import removed from `defineConfig` → target env `enabled=false`, `actions` row preserved |
| **disabled** | Enabled flag flipped `true → false` in a target environment | Happens during `--env` deploy when source has the action disabled |
| **re-enabled** | Enabled flag flipped `false → true` | Opposite of `disabled` |

Planned behavior: once the SDK ships `skipDeploy`, changes to that flag alone will **not** appear in the diff (the flag will control deploy behavior, not revisions). Today the field does not exist. See `advanced/skip-deploy-patterns.md`.

### 2.b JSON format (future, TBD)

A structured `--json` output is planned but not shipped in v1. When it lands:

- Emit `{ created: [...], updated: [...], deleted: [...], disabled: [...], re-enabled: [...] }`
- Each entry carries `{ id, name, class, checksum }` for deterministic parsing

Until then, parse the text format. If an upcoming `bm sync --help` shows `--json`, prefer it and update this reference.

## 3. The 50 % safeguard

When the number of actions about to be **disabled** (deleted + disabled categories combined) reaches **≥ 50 %** of the project's total OAC-managed actions, the CLI aborts with:

> `大量のアクションが無効化されます。--force で実行してください`

### How to respond

- **Do NOT auto-add `--force`.** Report the warning back to the user verbatim along with the dry-run diff and ask whether the scope is intentional.
- If the user confirms scope and asks you to proceed, the apply still happens in CI. CI's job is to pass `--force` only when a human-authored PR description explicitly justifies it. This skill never passes `--force`.
- If the user is surprised, re-Read `basemachina.config.ts` — they likely deleted an import they didn't mean to.

## 4. First-time Web → OAC switchover

On the first `bm sync` against a project whose actions were previously Web-UI-managed, expect:

- A churn of **updated** entries with a `lastModifiedVia: WEB → OAC` note for each.
- **No physical deletion** of anything. The Web UI's data is preserved; only the "source of truth" flag flips.
- The action row, all revisions, and enabled flags stay intact.

**Anti-pattern (flag it)**: users often interpret the first-sync churn as "OAC overwrote my Web UI work" and reach for a rollback. It did not overwrite anything. Explain `lastModifiedVia` and show them the dry-run diff is purely metadata-flag transitions on the first run.

See `anti-patterns.md` §first-OAC for the exact wording to use with the user.

## 5. Environment promotion (`--env` / `--from`)

For environments beyond dev:

- **Target**: always passed via `--env <target-env-id>`. Omitting `--env` targets dev; passing a non-dev id without `--env` is a ConfigError.
- **Source**: implicit (from config) or explicit via `--from <source-env-id>`.
- The diff is computed between source and target across two dimensions today: revision and `enabled` flag. (A third dimension, `skipDeploy`, is planned — see `advanced/skip-deploy-patterns.md`.)
- When the planned `skipDeploy` ships, entries marked `skipDeploy: true` at the source will be **skipped entirely** on the target (not written to the target env).

### 3-branch operational flow

For dev → stg → prd promotion, see `advanced/three-branch-ops.md`. The headline: use `--from` to pin the source environment when the git branch is not the natural source, and always `--dry-run` first.

## 6. `--config`

Pass `--config ./path/to/basemachina.config.ts` to sync from outside the project root. Useful when the agent's cwd is elsewhere. `--config` does not change how diffs are computed — only how the config is resolved.

## 7. Reporting dry-run results

When you present dry-run output to the user, structure it as:

1. **Command executed** (verbatim, including `--dry-run`).
2. **Total count**: N created, M updated, P deleted, Q disabled, R re-enabled.
3. **Notable items**: list the first 3-5 entries per non-empty category with their `id` and `name`.
4. **Safeguard status**: "50 % safeguard NOT triggered" or "50 % safeguard TRIGGERED — {message}. This skill will not add --force."
5. **Next step**: "Commit and open a PR. CI will apply on merge."

Do not author the PR body. That is the host agent's job (see `anti-patterns.md` §pr-body).

## 8. Edge cases

- **Dry-run reports 0 changes** but you just edited a file → check that the file is imported into `basemachina.config.ts`. Orphan files are not synced.
- **Dry-run reports `created` for an action you thought already existed** → the `id` field changed. BaseMachina identifies actions by `id`, not by file path.
- **Dry-run fails at the "loading config" stage** → `defineAction` type error. See `errors.md` §syntax.
- **Dry-run hangs** → cancel, check network to the gateway, re-run. Never escalate to an apply-class command.

## 9. See also

- `errors.md` — decoding specific error messages
- `anti-patterns.md` — the 7 DO / DON'T shared with AGENTS.md
- `advanced/three-branch-ops.md` — `--from` semantics
- `advanced/skip-deploy-patterns.md` — how `skipDeploy` interacts with the diff
