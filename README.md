# basemachina/skills

BaseMachina 用の Agent Skill を **Claude Code / Codex CLI など** cross-vendor に配布するためのパブリックリポジトリ。

- ライセンス: Apache-2.0
- 配布方式: `gh skill install` / `npx skills add` / 手動 `git clone`
- 対象エージェント: Claude Code, Codex CLI, Cursor, Copilot CLI, Gemini CLI 等（`SKILL.md` の cross-vendor minimal frontmatter 準拠）

## 収録 skill

| skill | 概要 | 状態 |
| --- | --- | --- |
| [`bm-code-management`](skills/bm-code-management/) | `bm sync --dry-run` + `defineAction` の書き方に特化した **設定者向け** skill。Plan → Validate のみ実行、Apply は CI に委譲 | v1.0.0 |

## インストール

推奨は `gh skill install`。Apache-2.0 のため fork / 改変可。

### 1. GitHub CLI（推奨）

```bash
gh skill install basemachina/skills@bm-code-management
```

- Claude Code / Codex CLI / Cursor / Copilot / Gemini CLI / Antigravity で共通に利用可能
- skill は `~/.claude/skills/bm-code-management/` と `~/.agents/skills/bm-code-management/` に配置される

### 2. Skills.sh（Supabase / Vercel / Stripe 互換）

```bash
npx skills add basemachina/skills --skill bm-code-management
```

### 3. 手動 clone（air-gapped / CI fallback）

```bash
git clone https://github.com/basemachina/skills.git /tmp/basemachina-skills
cp -R /tmp/basemachina-skills/skills/bm-code-management ~/.claude/skills/
cp -R /tmp/basemachina-skills/skills/bm-code-management ~/.agents/skills/
```

## バージョン固定・更新

```bash
# 特定バージョンに pin
gh skill pin basemachina/skills@bm-code-management@1.0.0

# 最新に更新
gh skill update basemachina/skills@bm-code-management
```

git tag は `<skill-slug>/vX.Y.Z` 形式（例: `bm-code-management/v1.0.0`）。
`CHANGELOG.md` に skill 別のセクションを用意し、semver で管理する。

## 顧客 repo に AGENTS.md を commit する（推奨）

skill とペアで使う `templates/AGENTS.md` を顧客 repo の root にコピーしておくと、skill を明示ロードしなくても AI エージェントに常時ガードレールが届く。

```bash
cp ~/.claude/skills/bm-code-management/templates/AGENTS.md ./AGENTS.md
git add AGENTS.md && git commit -m "chore: add AGENTS.md from bm-code-management skill"
```

`AGENTS.md` 冒頭の `<!-- managed-by: bm-code-management@1.0.0 -->` マーカーは skill version と照合され、drift があれば Pre-flight で警告される設計になっている。

## 設計原則

1. **Plan → Validate → (Execute is CI)** — skill は `bm sync --dry-run` のみ実行、apply は CI
2. **cross-vendor minimal** — `SKILL.md` の frontmatter は `name` + `description` + `allowed-tools` のみ、Claude 固有フィールド非使用
3. **AGENTS.md（常時）と SKILL.md（特定ワークフロー）の責務分離** — Vercel の実測で 100 % 達成パターン
4. **Retrieval-first** — CLI 引数や SDK 型は skill 本文に埋め込まず、エージェントが `bm --help` や `*.d.ts` を都度取得する前提

## Dogfooding とフィードバック

社内 `oac-poc` リポジトリで先行 dogfooding を行い、Slack `p1776682725.424589` （コード管理フィードバックスレ）に以下のフォーマットで投稿する:

```
[eval-case] summary / prompt / expected / actual
```

週次レビューで `evals/cases/` に YAML ケース化し、回帰防止の Gate として CI に組み込む。Phase 1 は手動、Phase 2 で Slack bot 経由の自動化を検討。

## ロードマップ

| Phase | 時期 | 主な内容 |
| --- | --- | --- |
| **Phase 1** (v1.0.0) | 2026-04 | 初期リリース。`bm-code-management` skill + `templates/AGENTS.md` + evals + lint/evals CI |
| **Phase 1.1** | 2-4 週後 | `VoltAgent/awesome-agent-skills` への掲載マージ、Slack → eval case 化運用の定着 |
| **Phase 1.5** | CLI PR2 / PR4 リリース後 | cross-vendor smoke CI（Codex CLI headless）、evals を LLM 実行で advisory 評価、`bm sync --env` / 3-branch ops の実装追従 |
| **Phase 2** (v2.0.0) | SDK 拡張後 | `_shared/` 共有資産、`scripts/build-agents-md.sh` 本実装、`templates/AGENTS.md.partial.md`、`bm-hotfix` / `bm-review` など追加 skill |

## 外部登録

- `VoltAgent/awesome-agent-skills` への掲載 PR を提出する（Phase 1.1 でマージ想定）
- `docs.basemachina.com/code-management` に install 手順を追記する

## 関連リンク

- 公式ドキュメント: https://docs.basemachina.com/code-management
- 対になる利用者向け skill: `public-api-mcp-skills`（MCP 経由でアクションを実行）
- Contributing: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Changelog: [`CHANGELOG.md`](CHANGELOG.md)

## Security

機密情報は commit しない。`templates/` / `evals/fixtures/` に書かれた `project.id` 等はすべて dummy 値。
本番 project id / env id は顧客 repo 側の env vars / vault で管理する。
