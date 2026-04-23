# Anti-patterns

> **Reader's contract**
> - **What**: The 7 misunderstandings that most often cause agent-driven damage or user confusion when using `bm sync` + code management.
> - **Prereq**: None. This file is the shared source of truth between `SKILL.md` and `templates/AGENTS.md`.
> - **Out of scope**: Advanced patterns (see `advanced/*`). Happy-path workflows (see `dry-run.md` and `defineAction.md`).

This list is what you flag, refuse, or correct when the user proposes one of these. It is duplicated verbatim in `SKILL.md` (the `Anti-Patterns to Flag` section) and referenced from `templates/AGENTS.md`.

## 1. Running `bm sync` without `--dry-run` from an agent

**Don't**: invoke `bm sync` (apply) from an agent session. Not even once.
**Do**: run `bm sync --dry-run` and hand off to CI for the apply.

**Why**: The applied state is hard to roll back. CI has the PR context, human review, and the audit trail. An agent-run apply doesn't.

**What to say to the user**: "Apply is CI-only. I'll run `bm sync --dry-run` and report the diff — please open a PR, and CI will apply on merge."

## 2. Thinking `deleted` means physical delete

**Don't**: tell the user that removing an action from `basemachina.config.ts` deletes its DB row.
**Do**: explain it is a **logical delete** — the target environment sets `enabled = false`, the `actions` row stays, and all revisions are preserved.

**Why**: users often panic when a large-scope dry-run shows many `deleted` entries. Knowing it's logical is usually enough to calm the panic and also to decide whether the 50 % safeguard applies (it does).

**What to say**: "This is a logical delete: `dev.enabled = false`. The action row and revisions remain; you can re-enable by restoring the import."

## 3. Adding `skipDeploy: true` to a `defineAction` today

**Don't**: add `skipDeploy: true` (or any other non-SDK field) to `defineAction`. The current SDK's `defineAction` uses `ExcessOnly` type-strict rejection and will fail to compile.
**Do**: for temporary deploy-skip needs, toggle the action's deploy state in the Web UI. When the SDK ships `skipDeploy`, this reference (`advanced/skip-deploy-patterns.md`) will describe the intended flows.

**Why**: `skipDeploy` is a planned deploy-time gate, not a feature flag — but it is not yet part of `@basemachina/sdk/oac`'s `JavaScriptActionConfig` or `GrpcActionConfig`. Adding it to code today blocks the entire `bm sync` (dry-run fails at TS compile).

**What to say**: "`skipDeploy` is planned but not in the current SDK. Your `defineAction` will not compile if you add it. Until it ships, use the Web UI's deploy toggle or manage rollout via branch flow."

## 4. Thinking the first OAC sync wipes Web-UI-managed assets

**Don't**: warn the user that the first dry-run's churn of `updated` entries means data loss.
**Do**: explain that the churn is **metadata only**: `lastModifiedVia` flips from `WEB` to `OAC`. No content is deleted or overwritten.

**Why**: The first sync against a previously-Web-UI-managed project necessarily shows every action as "updated" because the source-of-truth flag flips. Users interpret the churn as destructive.

**What to say**: "The first OAC sync shows churn because `lastModifiedVia` flips `WEB → OAC` for every action. Content is preserved; only the source-of-truth flag changes. This is expected exactly once per project."

## 5. Auto-adding `--force` to bypass the 50 % safeguard

**Don't**: pass `--force` to `bm sync` when the CLI prints `大量のアクションが無効化されます。--force で実行してください`.
**Do**: report the warning verbatim, show the dry-run diff, and ask the user whether the scope is intentional.

**Why**: The safeguard exists because a 50 %-scale disable is almost always a mistake (deleted import, wrong branch, bad merge). Bypassing it autonomously defeats the safeguard.

**What to say**: "The CLI triggered the 50 % safeguard: {exact message}. This skill will not add `--force`. Please review the dry-run diff below and confirm the scope is intentional."

## 6. Querying environment IDs from the CLI

**Don't**: promise the user you can list environment IDs via the CLI.
**Do**: direct the user to the Web UI (Environments page) to copy the ID, then set it as an env var (e.g., `STAGING_ENV_ID`) for commands like `bm sync --env "$STAGING_ENV_ID" --dry-run`.

**Why**: there is no `bm envs list` command. Environments are Web-UI-managed resources.

**What to say**: "Environment IDs aren't exposed via the CLI. Please copy the ID from the Web UI's Environments page. I'll use it in the `--env` flag."

## 7. Generating the PR body from dry-run output

**Don't**: write the PR title / description / rationale. That is the host agent's job (the Claude Code / Codex session that wraps this skill).
**Do**: provide the dry-run output in a structured, paste-ready format (see `dry-run.md` §7) and let the host agent compose the PR body.

**Why**: The PR body needs to cite the PR's intent, link tickets, mention reviewers, etc. — context this skill does not have. This skill's job is the dry-run result, not narrative.

**What to say**: "Here's the dry-run output, structured for your PR body. The host agent (or you) can use it to compose the description."

## Shared with `templates/AGENTS.md`

These same 7 items appear in the **customer repo's** `AGENTS.md` as a compact reminder that persists in the repo even when this skill isn't actively loaded. The customer-repo copy is shorter; this reference is the long-form source of truth.

When you change an entry here, also update:

- `SKILL.md` `Anti-Patterns to Flag` section (between the `<!-- build-agents-md:anti-patterns -->` markers)
- `templates/AGENTS.md`

Phase 2 will automate this with `scripts/build-agents-md.sh`. Phase 1 requires manual sync.
