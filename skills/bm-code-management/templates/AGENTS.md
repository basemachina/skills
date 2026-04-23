<!-- managed-by: bm-code-management@1.0.0 -->
# AGENTS.md

## BaseMachina code management

### Always

- Before any `bm sync`, run `bm sync --dry-run` first.
- Preview default. Apply is CI-only (see `.github/workflows/bm-sync.yml`).
- Keep `basemachina.config.ts` at the project root. Actions live under `src/actions/`. JS handlers under `src/actions/js-action-codes/`.
- Edit code locally, never from the BaseMachina Web UI while code management is active for this project.

### Never

- Never run `bm sync` without `--dry-run` from an agent.
- Never run `bm hotfix` or `bm unpin` from an agent.
- Never pass `--force` autonomously. The 50 % safeguard requires human intent.
- Never hardcode secrets in `src/actions/**/*.ts` or `src/actions/js-action-codes/**/*.js` (use `vars` / `secrets` runtime context).
- Never edit `node_modules/@basemachina/**`.

### When unsure

- Run `bm sync --dry-run --config ./basemachina.config.ts` and inspect the diff first.
- See the skill's `references/anti-patterns.md` before "removing" an action (it's a logical delete).
- See `references/dry-run.md` for the 50 % safeguard and first OAC switchover.

### Out of scope for this skill

- `bm hotfix` / `bm unpin` / action execution / PR body generation.
- For action execution via MCP, use the `public-api-mcp-skills` skill.
- For hotfix workflows, see `docs.basemachina.com/code-management`.

## Recommended skill

```
gh skill install basemachina/skills@bm-code-management
```

## Project-specific rules

<!-- Add project-specific guardrails below. Examples: preferred action naming, internal deployment windows, specific environments to avoid. -->
- TODO: document project conventions here
