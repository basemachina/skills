# basemachina/skills

BaseMachina を使った開発で利用する Agent Skill コレクションです。

## 収録 skill

| skill | 使う場面 |
| --- | --- |
| [`basemachina-docs`](skills/basemachina-docs/) | BaseMachina 公式ドキュメントを調査し、仕様・使い方・制約・コード例を根拠 URL 付きで回答 |
| [`bm-code-management`](skills/bm-code-management/) | `defineAction` / `defineView` / `defineConfig` の編集、`bm pull`、アクション・ビューコードの編集、`bm sync --dry` による差分確認 |
| [`bm-public-api`](skills/bm-public-api/) | 公開API（REST API）を外部システムや CI/CD から呼び出すコードの作成、認証、レスポンス・エラーハンドリング |

`basemachina-docs` は現行仕様の調査、`bm-code-management` はコード管理 repo の安全な編集、`bm-public-api` は公開API クライアントの実装に使います。副作用のあるアクション実行と、`--dry` を付けない `bm sync` はエージェントから実行しません。

## GitHub CLI でインストールする

`gh skill` は preview 機能です。利用前に `gh skill --help` で現在の GitHub CLI が対応していることを確認してください。

まず内容を確認します。

```bash
gh skill preview basemachina/skills basemachina-docs
gh skill preview basemachina/skills bm-code-management
gh skill preview basemachina/skills bm-public-api
```

Codex のユーザースコープへインストールする例:

```bash
gh skill install basemachina/skills basemachina-docs --agent codex --scope user
gh skill install basemachina/skills bm-code-management --agent codex --scope user
gh skill install basemachina/skills bm-public-api --agent codex --scope user
```

repo 単位で使う場合は `--scope project` を指定します。対応 agent の最新一覧は `gh skill install --help` で確認してください。

version を省略すると、latest release tag、次に default branch の HEAD の順で解決されます。再現性が必要な場合は release tag または commit SHA に固定します。

```bash
gh skill install basemachina/skills bm-code-management@v1.0.2 --agent codex --scope user
gh skill install basemachina/skills bm-public-api --pin v1.0.2 --agent codex --scope user
```

更新の確認と適用:

```bash
gh skill update --dry-run
gh skill update --all
```

pin された skill は通常の更新対象から外れます。pin を外す場合は `gh skill update --unpin` を使います。

## Claude Code plugin としてインストールする

```text
/plugin marketplace add basemachina/skills
/plugin install bm-skills@basemachina
```

更新または削除:

```text
/plugin marketplace update basemachina
/plugin uninstall bm-skills@basemachina
```

Claude Code 向け metadata は `.claude-plugin/plugin.json`、ChatGPT / Codex 共通 plugin 向け metadata は `.codex-plugin/plugin.json` で管理しています。この repo は MCP server、hook、実行ファイル、外部 plugin 依存を同梱しません。

## 開発

Pull Request の作成前に以下を実行してください。

```bash
python3 scripts/validate-skills.py
gh skill publish --dry-run
claude plugin validate --strict .
```

仕様や互換性を変更する場合は、根拠にした最新の公式ドキュメントを Pull Request に記載してください。

## ライセンス

MIT

## 関連リンク

- BaseMachina 公式ドキュメント: <https://docs.basemachina.com/>
- BaseMachina コード管理: <https://docs.basemachina.com/code_management/>
- BaseMachina 公開API: <https://docs.basemachina.com/public_api/>
- BaseMachina Remote MCP: <https://docs.basemachina.com/remote_mcp/>
- Agent Skills Specification: <https://agentskills.io/specification>
- OpenAI Skills: <https://developers.openai.com/codex/skills>
- OpenAI Plugins: <https://developers.openai.com/plugins/build/plugins>
- GitHub CLI `gh skill`: <https://cli.github.com/manual/gh_skill>
- Claude Code plugins: <https://code.claude.com/docs/en/plugins>
- Claude Code plugin marketplaces: <https://code.claude.com/docs/en/plugin-marketplaces>
