# Contributing

`basemachina/skills` への貢献ガイド。

## 全体方針

本リポジトリは **monorepo** で、`skills/<slug>/` 配下に 1 skill が閉じる。
skill 間の共有資産は Phase 2 で `_shared/` に切り出す予定（Phase 1 では同居 skill がないため不要）。

## 新しい skill を追加する

1. `skills/<your-skill-slug>/` を作成し、以下の最小構成を置く:
   - `SKILL.md` — 300 行以下、cross-vendor minimal frontmatter
   - `skill.json` — name / version / description / compatibility
2. 必要に応じて `references/`、`templates/`、`evals/` を追加する。
3. `CHANGELOG.md` に `## <your-skill-slug>` セクションを追加し、v1.0.0 エントリを記載する。
4. git tag は `<your-skill-slug>/vX.Y.Z` 形式でリリースする。

## SKILL.md の書き方

### Frontmatter（必須）

```yaml
---
name: <skill-slug>
description: <when to use + scope + out-of-scope を 1 段落で>
allowed-tools: <Tool-pattern リスト>
---
```

- **`name`**: kebab-case、`skills/` 配下のディレクトリ名と一致させる。
- **`description`**: 「いつ使う」「スコープ」「対象外」を 1 段落で書く。エージェントがこの skill を自動起動するかの判断材料になるので、キーワードを豊富に含める。
- **`allowed-tools`**: `Bash(command:*)` 形式で許可コマンドを明示する。Codex CLI では無視されるため、本文での自然言語ガードレールを必ず二重化する。

### Claude 固有 frontmatter の使用禁止

cross-vendor 互換性のため、以下の Claude Code 固有フィールドは使わない:

- `when_to_use` / `paths` / `hooks` / `context`
- `disable-model-invocation` / `argument-hint`

また、`` !`<command>` `` の inline preprocessing（Claude Code 固有）も使わない。
代わりに本文で「エージェントが自分で `<command>` を Bash で実行せよ」と明示する。

### 行数制限

- `SKILL.md` は **300 行以下**。越える内容は `references/` に切り出す。
- `references/` は **1 階層**までが原則。例外的に `references/advanced/` のみ 2 階層目を許容する。

### Anti-Patterns 節のマーカー

Anti-Patterns 表は `<!-- build-agents-md:anti-patterns -->` / `<!-- /build-agents-md:anti-patterns -->` で囲む。
Phase 2 で `scripts/build-agents-md.sh` がこのマーカーから抽出して `templates/AGENTS.md` を自動生成する。

## references の書き方

各 `references/*.md` は先頭に **Reader's contract** を 3 行で書く:

```markdown
> **Reader's contract**
> - What: このファイルを読むと何ができるようになるか
> - Prereq: 前提知識・前提ファイル
> - Out of scope: このファイルには書かれていないこと（代わりにどこを見るか）
```

`references` は **自己完結** して独立に読めること。SKILL.md を前提にしない。

## evals を追加する

1. `skills/<slug>/evals/cases/<NN>-<short-name>.yaml` を作成する。
2. `prompt` / `prereq_fixtures` / `expected_behavior.must` / `expected_behavior.must_not` / `grader_hints.deterministic` / `grader_hints.llm_judge` を埋める。
3. 必要なら `skills/<slug>/evals/fixtures/` にフィクスチャを追加する。
4. **決定論的チェック（substring match）のみ PR blocker**、LLM judge は advisory。

詳細は `skills/<slug>/evals/README.md` を参照。

## dogfooding フィードバック

Slack `p1776682725.424589`（コード管理フィードバックスレ）に `[eval-case] summary / prompt / expected / actual` 形式で投稿する。
週次で `evals/cases/` に case 化する運用とする（Phase 1 は手動、Phase 2 で Slack bot 自動化）。

## ローカル lint

push 前に `.github/workflows/lint.yml` と同等の検証をローカルで実行して CI fail を予防する:

```bash
# markdownlint
npx markdownlint-cli 'skills/**/*.md' 'README.md' 'CHANGELOG.md' 'CONTRIBUTING.md'

# SKILL.md の行数が 300 以下か
wc -l skills/*/SKILL.md

# skill.json の JSON schema 検証（schema は lint.yml に inline）
npx ajv-cli validate -s <inline-schema> -d skills/*/skill.json
```

## PR

- branch 名: `<skill-slug>/<short-description>` または `meta/<short-description>`
- `gh pr create --draft` で作成する。

## 顧客 `AGENTS.md` テンプレの更新

`templates/AGENTS.md` を更新する際は:

1. `<!-- managed-by: <slug>@X.Y.Z -->` マーカーの version を `skill.json` の `version` と揃える（lint で検証）。
2. `CHANGELOG.md` に追記する。
3. 既に commit 済みの顧客 repo は Pre-flight checklist で drift 警告される設計なので、顧客側の更新タイミングはユーザー主導。
