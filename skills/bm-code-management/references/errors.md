# Error recovery reference

> **Reader's contract**
> - **What**: Decode a `bm` CLI error message, identify the error category, and apply the right recovery.
> - **Prereq**: `bm` CLI installed. For auth errors, you'll direct the user to run `bm login`.
> - **Out of scope**: Writing `defineAction` (see `defineAction.md`), reading dry-run output (see `dry-run.md`).

Errors come in three categories, following the platform's GitOps error model:

| Category | HTTP | Meaning | Alert? |
| --- | --- | --- | --- |
| **ConfigError** | 400 | User-side config / flag problem | No |
| **ConflictError** | 409 | State diverged between plan and apply | No |
| **SystemError** | 500 | Platform bug or outage, includes `requestId` | Yes (automatic) |

If the error is a `SystemError`, alerting is handled server-side. Tell the user the requestId and suggest contacting support if it recurs.

## 1. Substring table

Match on the **substring** the CLI printed, then look up the row. Substrings are Japanese because the CLI's current locale is `ja`; the English column is the canonical translation.

| Substring | English | Category | Cause | What to do |
| --- | --- | --- | --- | --- |
| `大量のアクションが無効化されます。--force で実行してください` | A large number of actions will be disabled. Run with `--force` | Safeguard (not an error) | ≥ 50 % of OAC-managed actions would be disabled in this sync | Report to user, DO NOT auto-add `--force`. See `dry-run.md` §safeguard |
| `開発環境へは --env なしの bm sync を使用してください` | Use `bm sync` without `--env` for the development environment | ConfigError (400) | `--env <dev-env-id>` was passed | Re-run without `--env` |
| `--from は --env と一緒に使用してください` | `--from` must be used with `--env` | ConfigError (400) | `--from` passed without `--env` | Add `--env <target>` or remove `--from` |
| `環境が見つかりません: <envId>` | Environment not found: `<envId>` | ConfigError (400) | Unknown or mistyped env id | Confirm env id in the Web UI |
| `プロジェクトに開発環境が設定されていません` | No development environment is configured for this project | ConfigError (400) | Project has no dev env | Create a dev env in the Web UI first |
| `authentication required` / `token expired` / `unauthorized` | Token missing or expired | Auth | Credentials file stale | Ask user to run `bm login` (see §2) |
| `checksum mismatch` / `state changed since plan` | State diverged | ConflictError (409) | Someone else modified the target between plan and apply | Re-run `bm sync --dry-run`; if clean, re-open PR |
| `予期しないエラーが発生しました (requestId: ...)` | Unexpected error (requestId: …) | SystemError (500) | Server bug | Capture requestId; retry once; escalate to support if it recurs |
| `TypeScript compile error` / `cannot find module '@basemachina/sdk'` | TS compile or module resolution | ConfigError (400, caught client-side) | `defineAction` type mismatch or missing deps | Run `npx tsc --noEmit`, fix types, re-run |
| `lastModifiedVia: WEB → OAC` (informational) | Source-of-truth flipped on first sync | Not an error | First OAC sync against a Web-UI-managed project | Expected churn; explain to user |

## 2. Auth expired

Symptoms:

- `bm sync --dry-run` returns "authentication required" / "unauthorized" / "token expired"
- `~/.basemachina/credentials.json` has a past `expiresAt` (tokens are 17-hour)

**Do NOT run `bm login` yourself.** The login flow opens a browser, waits for a user-interactive redirect, and posts a state-protected callback. An agent-initiated login would hang and may cause a state mismatch.

Ask the user:

> "Your bm CLI auth looks expired. Please run `bm login [--subdomain <name>]` in your terminal. After that, I'll re-run the dry-run."

Wait for the user to confirm before retrying the sync.

## 3. Syntax / type errors in `defineAction`

When `bm sync --dry-run` fails in the "loading config" stage, the underlying cause is typically a TS compile error in `basemachina.config.ts` or an imported `actions/*.ts`.

Diagnosis:

1. Run `npx tsc --noEmit` to surface every type error, not just the first.
2. Read `node_modules/@basemachina/sdk/dist/**/*.d.ts` (grep for the specific field name in the error message) — type signatures change across SDK minor versions.
3. Verify all fields on `defineAction` are allowed for the chosen `class` (see `defineAction.md` §4).

Common type mistakes:

- Using `class: "javascript_server"` (wrong) instead of `class: "javascript"` (the SDK's actual literal)
- Adding fields not in the SDK (e.g., `skipDeploy`, `resource` for SQL/REST — the SDK currently supports only `javascript` and `grpc`); `defineAction` uses `ExcessOnly` to reject unknown fields
- Missing `dataSource` or `fullMethodName` on `class: "grpc"`
- Using `parameter type: "SQL"` or `"VAR"` (neither exist in the SDK; real types are TEXT / NUMBER / BOOL / DATE / FILE / JSON / SYSTEM_VALUE / ARRAY / TUPLE)
- Re-using an `id` across two actions (runtime error, caught at sync rather than compile)

## 4. ConflictError 409

`ConflictError` means the target state changed between your plan and your apply. Nothing was written; the fix is always "re-plan".

For an agent flow:

1. Re-run `bm sync --dry-run` and report the new diff.
2. If the diff matches what the user expected, CI will apply cleanly on merge.
3. If the diff now includes unexpected items (someone else changed the env in the Web UI), ask the user how to proceed — don't try to reconcile autonomously.

## 5. SystemError 500

The CLI will print something like:

```
予期しないエラーが発生しました (requestId: 01HXYZ...)
```

- The platform has **already alerted** on this requestId; you do not need to escalate manually.
- Do not auto-retry more than once. Report the requestId to the user.
- This is a BaseMachina-side problem, not a user-config problem. The user should contact support with the requestId if it persists.

## 6. Init / setup errors

| Symptom | Cause | Fix |
| --- | --- | --- |
| `bm: command not found` | `@basemachina/cli` not installed | `npm i -D @basemachina/cli` in the bm project |
| `cannot find module '@basemachina/sdk'` | `@basemachina/sdk` not installed | `npm i -D @basemachina/sdk` |
| `@basemachina:registry 404` | Missing private registry token for `@basemachina` npm scope | Configure `.npmrc` with `@basemachina:registry=https://npm.pkg.github.com` + `GITHUB_TOKEN` |
| `basemachina.config.ts not found` | Running from outside project root | Pass `--config <path>` or `cd` to the root |

## 7. See also

- `dry-run.md` — what successful dry-run output looks like
- `defineAction.md` — getting the types right in the first place
- `anti-patterns.md` — "delete ≠ physical delete", "first sync ≠ wipe", etc., for user-misunderstanding errors
