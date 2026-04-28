# basemachina/skills

BaseMachina のコード管理作業で使う Agent Skill コレクションです。

## 収録 skill

| skill | 使う場面 |
| --- | --- |
| [`bm-code-management`](skills/bm-code-management/) | `defineAction` / `defineConfig` の編集、JavaScript アクションのコード本体作成、ビューコードとコード取得設定の連携、`bm sync --dry` による差分確認 |

この skill は、BaseMachina のコード管理 repo を編集するときのガードレールです。アクションの実行、本番反映、ビュー設定そのものの変更は扱いません。

## インストール方法

### GitHub CLI で install する

GitHub CLI v2.90.0 以降を使える場合は、`gh skill` で install できます。agent ごとの配置先、scope、version pin、update を CLI に任せられるため、複数のエージェントで同じ skill を使いたい場合に扱いやすい方法です。

`gh skill` は preview 機能なので、細かい挙動は今後変わる可能性があります。

まず内容を確認します。

```bash
gh skill preview basemachina/skills bm-code-management
```

使うエージェントと scope を明示して install します。

```bash
# Codex で、ユーザー全体に install
gh skill install basemachina/skills bm-code-management --agent codex --scope user

# Codex で、現在の repo だけに install
gh skill install basemachina/skills bm-code-management --agent codex --scope project
```

`--agent` には `github-copilot` / `claude-code` / `cursor` / `codex` / `gemini` / `antigravity` を指定できます。非対話実行では `--agent` と `--scope` を明示すると、意図しない場所への install を避けられます。

### Claude Code plugin として install する

Claude Code では plugin marketplace としても利用できます。

```shell
/plugin marketplace add basemachina/skills
/plugin install bm-skills@basemachina
```

marketplace を更新する場合:

```shell
/plugin marketplace update basemachina
```

plugin を削除する場合:

```shell
/plugin uninstall bm-skills@basemachina
```

## `gh skill` でのバージョン固定

version を指定しない場合、`gh skill install` は latest tagged release を使います。release がない場合は default branch の HEAD を使います。

特定 version に固定したい場合は、release tag または commit SHA を指定します。`v0.1.0` release 後に固定する例:

```bash
gh skill install basemachina/skills bm-code-management@v0.1.0 --agent codex --scope user

# または
gh skill install basemachina/skills bm-code-management --pin v0.1.0 --agent codex --scope user
```

release 前の状態を固定したい場合は、tag の代わりに commit SHA を指定してください。

## `gh skill` での更新

install 済みの skill は `gh skill update` で更新できます。

```bash
# 更新があるか確認
gh skill update --dry-run

# 全 skill を確認なしで更新
gh skill update --all
```

pin された skill は通常の update 対象から外れます。pin を外して更新する場合は `--unpin` を使います。

```bash
gh skill update --unpin
```

## `gh skill` で install した skill の削除

GitHub CLI v2.90.0 の `gh skill` には uninstall / remove コマンドがありません。削除したい場合は、install 先の `bm-code-management` ディレクトリを削除してください。

主な install 先は以下です。

| agent | user scope | project scope |
| --- | --- | --- |
| GitHub Copilot | `~/.copilot/skills` | `.agents/skills` |
| Claude Code | `~/.claude/skills` | `.claude/skills` |
| Cursor | `~/.cursor/skills` | `.agents/skills` |
| Codex | `~/.codex/skills` | `.agents/skills` |
| Gemini CLI | `~/.gemini/skills` | `.agents/skills` |
| Antigravity | `~/.gemini/antigravity/skills` | `.agents/skills` |

## ライセンス

MIT

## 関連リンク

- BaseMachina コード管理: <https://docs.basemachina.com/preview/code_management/>
- BaseMachina ビューコードの Git 管理: <https://docs.basemachina.com/view/code_editor/git_management/>
- Agent Skills Specification: <https://agentskills.io/specification>
- GitHub CLI `gh skill`: <https://cli.github.com/manual/gh_skill>
- Claude Code plugins: <https://code.claude.com/docs/en/discover-plugins>
