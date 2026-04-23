# Changelog

skill 別に semver を管理する。monorepo の git tag は `<skill-slug>/vX.Y.Z` 形式（例: `bm-code-management/v1.0.0`）。

## bm-code-management

### v1.0.0 — 2026-04-23

Initial release.

- Plan → Validate 専用 skill。`bm sync --dry-run` でのみ同期を検証し、apply は CI に委ねる設計。
- `SKILL.md` は cross-vendor minimal frontmatter（`name` / `description` / `allowed-tools`）で Claude Code と Codex CLI の双方で動作する前提。
- `references/` 基本 4 本（`defineAction.md` / `dry-run.md` / `errors.md` / `anti-patterns.md`）+ `references/advanced/` 4 本（`env-specific-actions.md` / `skip-deploy-patterns.md` / `three-branch-ops.md` / `helper-composition.md`）。
- `templates/AGENTS.md` — 顧客 repo に commit 推奨の薄い常時ガードレール。`<!-- managed-by: bm-code-management@1.0.0 -->` マーカー付きで drift 検知可能。
- `templates/github-actions/bm-sync.yml` — PR で `bm sync --dry-run`、merge で `bm sync` を実行する CI テンプレ。
- 対象: JS Server Action（4 種 result type）、SQL（MySQL / PostgreSQL）、REST、gRPC、環境プロモーション、`skipDeploy`、3 ブランチ運用、共通 helper 抽出。
- 非対象: `bm hotfix` / `bm unpin` / action 実行（`public-api-mcp-skills` の責務）/ PR 本文生成 / Git 操作。
