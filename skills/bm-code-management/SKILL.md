---
name: bm-code-management
description: Use this skill when the user edits BaseMachina action or config code with the bm CLI. Plan changes, write or modify defineAction/defineConfig in TypeScript, and validate every change with `bm sync --dry-run` before handing off to CI. SDK currently supports `class: "javascript"` and `class: "grpc"` via `defineAction`; other action kinds (MySQL, PostgreSQL, REST, GraphQL) are managed via the Web UI until SDK support ships. Covers environment promotion with `--env` / `--from`, common error recovery, and the first Web → OAC switchover. Does NOT execute `bm sync` without `--dry-run`, does NOT run `bm hotfix` / `bm unpin`, does NOT open PRs, does NOT execute actions.
allowed-tools: Bash(bm sync:*), Bash(bm --help:*), Bash(bm --version), Bash(bm sync --help), Bash(bm login --help), Read, Grep, Glob, Edit, Write
---

# BaseMachina Code Management

## Preview default, apply only via CI

- **Always run `bm sync --dry-run` first.** Never run `bm sync` without `--dry-run` from this skill.
- **Never run `bm hotfix`, `bm unpin`, or any command that mutates a live environment.**
- **Never pass `--force` autonomously.** The 50 % safeguard requires human intent.
- Applying is CI's job. If the user asks to apply, explain apply is CI-only and offer dry-run.

## When to use

Trigger keywords: *bm sync*, *dry-run*, *defineAction*, *defineConfig*, *bm.ts*, *basemachina.config.ts*, *actions/*, *codes/*, *js-action-codes/*, *skipDeploy*, *OAC*, *operations-as-code*, *@basemachina/sdk*, *@basemachina/action*.

- Adding a new action (`defineAction` with `class: "javascript"` or `class: "grpc"`) and registering it in `basemachina.config.ts`
- Editing an existing action's `code`, parameters, or gRPC body template
- Deleting an action (= logical disable, not physical delete — see Anti-Patterns)
- Running `bm sync --dry-run` to preview created / updated / deleted / disabled / re-enabled diff
- Interpreting dry-run output, including the 50 % safeguard warning
- Recovering from common errors (auth expired, TS compile failure, ConfigError, ConflictError)
- Standing up a fresh bm project directory (`basemachina.config.ts` / `src/actions/` / `src/actions/js-action-codes/`)
- Using `@basemachina/action` helpers (`executeAction` / `rawExecuteAction`) in JavaScript action handlers
- Choosing the right JavaScript-action result type (`userError` / `resultError` / `systemError` / `success`)
- Writing `defineAction` for the 2 SDK-supported classes (`javascript` / `grpc`)
- Explaining the first Web → OAC switchover (`lastModifiedVia` churn)
- Environment promotion dry-run (`bm sync --env <id> --dry-run`, `--from <branch>` for 3-branch ops)

## When NOT to use

Refuse with the listed template and redirect the user to the alternative.

| Category | Refusal template |
| --- | --- |
| Production apply | "Apply is CI-only. I'll run `bm sync --dry-run` to preview changes — please create a PR and CI will apply on merge." |
| `bm hotfix` / `bm unpin` | "Hotfix / unpin is out of scope for this skill. See `docs.basemachina.com/code-management` for the hotfix workflow." |
| Executing actions (not editing) | "Running actions is handled by `public-api-mcp-skills`. This skill only edits action definitions and previews sync." |
| Generating PR body | "PR body is your agent's responsibility. I can provide the dry-run output for you to paste." |

## Pre-flight checklist

Run these before any editing or sync work.

1. **Project detection**: confirm `bm.ts` or `basemachina.config.ts` exists at the current working directory root.
2. **CLI sanity**: run `bm --version` in Bash. If the command is missing or auth is expired, stop and ask the user to install or `bm login` (do NOT run `bm login` yourself).
3. **AGENTS.md version marker**: read the repository root `AGENTS.md` and confirm `<!-- managed-by: bm-code-management@X.Y.Z -->` matches this skill's `skill.json` version. On drift, warn the user and recommend re-copying `templates/AGENTS.md`.
4. **Scope alignment**: restate the user's intent in one sentence. For destructive operations (delete, rename, mass disable), get explicit confirmation.
5. **Preview declaration**: declare to the user "I will only run `bm sync` with `--dry-run`. Apply happens in CI."

## Workflow: iterate → validate → (Execute is CI)

1. **Iterate**: Read the existing `bm.ts` / `actions/*.ts` to locate the patterns in use, then Edit / Write as requested. Match the existing imports and `defineAction` shape — do not guess. Reference `references/defineAction.md` for action-class-specific patterns.
2. **Validate**: Run `bm sync --dry-run` (or `bm sync --env <id> --dry-run`, or `bm sync --env <id> --from <branch> --dry-run`). Parse the output into created / updated / deleted / disabled / re-enabled. If the 50 % safeguard fires, STOP — never add `--force` yourself. See `references/dry-run.md`.
3. **Formalize**: Report the dry-run result to the user so they can commit and open a PR. CI applies on merge. Do NOT author the PR body; that is the host agent's responsibility.

## Retrieval Sources

Do NOT rely on memory for CLI flags or SDK types. Fetch them fresh each run.

| Information | How to retrieve |
| --- | --- |
| bm CLI flags | `bm --help`, `bm sync --help`, `bm login --help` via Bash |
| bm CLI version | `bm --version` via Bash |
| SDK type definitions | Read `node_modules/@basemachina/sdk/dist/**/*.d.ts` (grep for `defineAction`, `defineConfig`) |
| `@basemachina/action` helper types | Read `node_modules/@basemachina/action/dist/**/*.d.ts` |
| Official docs (canonical) | https://docs.basemachina.com/code-management |
| Detailed patterns & anti-patterns | `references/*.md` in this skill |

## Decision table

| User asks | Do this | Reference |
| --- | --- | --- |
| "Add a new JavaScript action" | Read existing `src/actions/*.ts`, Write new `src/actions/<slug>.ts` with `class: "javascript"`, register in `basemachina.config.ts`, run `bm sync --dry-run` | `references/defineAction.md` |
| "Add a new MySQL / REST / GraphQL action" | Explain SDK does not yet support these via `defineAction`; manage via Web UI until SDK ships the config | `references/defineAction.md` §6 |
| "Remove this action" | Confirm logical-delete semantics, remove the import + registration from `basemachina.config.ts`, run `bm sync --dry-run`, expect `disabled` diff | `references/anti-patterns.md` §deletion |
| "Why did sync say N actions disabled?" | Parse dry-run output, explain logical delete vs 50 % safeguard | `references/dry-run.md` |
| "Promote to staging" | Run `bm sync --env <stg-id> --from <source-env-id> --dry-run` | `references/advanced/three-branch-ops.md` |
| "Apply skipDeploy to this action" | Explain `skipDeploy` is NOT in the current SDK. Describe planned usage; do not add the field today | `references/advanced/skip-deploy-patterns.md` |
| "Auth error from bm sync" | Ask user to run `bm login` (do not run yourself) | `references/errors.md` §auth |
| "Dry-run says 50 % disabled — force it?" | Refuse `--force` auto-add, require human review | `references/dry-run.md` §safeguard |
| "Initial OAC setup wiped my Web-managed stuff" | Explain `lastModifiedVia: WEB → OAC`, no physical delete | `references/dry-run.md` §first-OAC |

<!-- build-agents-md:anti-patterns -->
## Anti-Patterns to Flag

| Anti-pattern | Correct behavior |
| --- | --- |
| Running `bm sync` without `--dry-run` from an agent | Dry-run always. CI applies. |
| Thinking deleting `src/actions/foo.ts` physically deletes the DB row | Logical delete only: `dev.enabled = false`. Revisions and `actions` row remain. |
| Adding `skipDeploy: true` to `defineAction` today | SDK does not yet accept this field (TS compile error). Use the Web UI's deploy toggle until SDK ships. |
| Thinking the first OAC sync wipes Web-UI-managed assets | No. `lastModifiedVia` switches `WEB → OAC`, content preserved. Expect churn on first sync. |
| Auto-adding `--force` when the 50 % safeguard fires | Never auto-force. Require human review. |
| Querying environment IDs via the CLI | There is no list command. Fetch from the Web UI. |
| Making this skill generate the PR body | PR body is the host agent's job. This skill only provides dry-run output. |
<!-- /build-agents-md:anti-patterns -->

## Edge Cases

- **Not a bm project**: `bm.ts` / `basemachina.config.ts` absent → stop and tell the user to run from a bm project root or pass `--config <path>`.
- **CLI missing**: `bm --version` fails → tell the user to install `@basemachina/cli` (`npm i -D @basemachina/cli`).
- **Auth expired**: `bm sync --dry-run` returns an auth error → ask the user to run `bm login`. Do NOT run it yourself (browser flow + state token).
- **Dry-run shows no diff** when you expected one → re-confirm the edit landed on disk (`git diff`), re-check `basemachina.config.ts` registration.
- **Edits outside `actions/` / `codes/` / `bm.ts` / `basemachina.config.ts`**: they will not appear in the dry-run output. That is expected; `bm sync` only tracks those paths.

## References

### Basic

- [`references/defineAction.md`](references/defineAction.md) — `defineAction` / `defineConfig` for all 5 action classes, 4 result types, parameter input types
- [`references/dry-run.md`](references/dry-run.md) — 3 command shapes, output categories, 50 % safeguard, first OAC switchover
- [`references/errors.md`](references/errors.md) — substring → cause → recovery flat table
- [`references/anti-patterns.md`](references/anti-patterns.md) — the 7 DO / DON'T shared between this skill and `templates/AGENTS.md`

### Advanced

- [`references/advanced/env-specific-actions.md`](references/advanced/env-specific-actions.md) — env-aware `defineAction` patterns
- [`references/advanced/skip-deploy-patterns.md`](references/advanced/skip-deploy-patterns.md) — 4 planned `skipDeploy` flows + 1 anti-pattern (SDK support pending)
- [`references/advanced/three-branch-ops.md`](references/advanced/three-branch-ops.md) — dev / stg / prd promotion, `--from` semantics
- [`references/advanced/helper-composition.md`](references/advanced/helper-composition.md) — shared `lib/` util extraction, bundler gotchas
