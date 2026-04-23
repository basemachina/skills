# basemachina/skills

BaseMachina 用の [Agent Skill](https://agentskills.io/specification) を配布するパブリックリポジトリ。

- ライセンス: Apache-2.0
- 対象エージェント: Claude Code / Codex CLI / Cursor / Copilot CLI / Gemini CLI 等 35 以上（[gh skill 対応一覧](https://cli.github.com/manual/gh_skill_install)）

## 収録 skill

| skill | 概要 |
| --- | --- |
| [`bm-code-management`](skills/bm-code-management/) | `defineAction` を編集し `bm sync` で差分をプレビューする skill |

## インストール

用途に応じて以下から選択してください。

### 1. `gh skill install`（cross-agent / 推奨）

GitHub CLI v2.90.0 以降に同梱される公式 Agent Skills インストーラ。35 以上のエージェントに対応しており、install 先ディレクトリをエージェントごとに自動解決します。

```bash
# Claude Code にユーザースコープで install
gh skill install basemachina/skills bm-code-management --agent claude-code --scope user

# プロジェクトスコープ（チーム共有）
gh skill install basemachina/skills bm-code-management --agent claude-code --scope project

# 特定のバージョンに pin
gh skill install basemachina/skills bm-code-management --pin v1.0.0

# 対話モードで選択
gh skill install
```

対応エージェント: `claude-code` / `codex` / `cursor` / `github-copilot` / `gemini-cli` / `warp` / `windsurf` ほか。

### 2. Claude Code plugin marketplace（Claude Code 特化 / auto-update 対応）

Claude Code ネイティブのマーケットプレイス経由。auto-update や `/plugin` 管理 UI と連携します。

**対話（Claude Code 内）**:

```shell
/plugin marketplace add basemachina/skills
/plugin install bm-skills@basemachina
```

**非対話 CLI**:

```bash
claude plugin marketplace add basemachina/skills
claude plugin install bm-skills@basemachina
```

install 後は `/reload-plugins` で読み込み直すと skill が有効になります。

### 3. チーム自動配布（`.claude/settings.json`）

プロジェクトルートの `.claude/settings.json` にマーケットプレイスを登録しておくと、チームメンバーがプロジェクトを trust した時点で marketplace が自動で追加されます。

```json
{
  "extraKnownMarketplaces": {
    "basemachina": {
      "source": {
        "source": "github",
        "repo": "basemachina/skills"
      }
    }
  },
  "enabledPlugins": {
    "bm-skills@basemachina": true
  }
}
```

### 4. Gemini CLI extensions

```bash
gemini extensions install https://github.com/basemachina/skills
```

更新は `gemini extensions update` で行います（auto-update を有効にする場合は `--auto-update`）。

### 5. Codex CLI

Codex CLI はスキャン対象ディレクトリが決まっているため、該当箇所に SKILL.md を配置します。

```bash
# ユーザースコープ
mkdir -p ~/.agents/skills
git clone --depth 1 https://github.com/basemachina/skills.git /tmp/bm-skills
cp -R /tmp/bm-skills/skills/bm-code-management ~/.agents/skills/

# または repo 直下の .agents/skills/ に置けばそのリポジトリ内でのみ有効
```

セッション内で `$skill-installer` が利用可能な場合はそちらからも install できます。配置後に `/skills` で認識を確認してください。

### 6. Cursor（rules として手動配置）

Cursor は現状 SKILL.md を native には読まないため、rule として配置します。

```bash
git clone --depth 1 https://github.com/basemachina/skills.git /tmp/bm-skills
mkdir -p ~/.cursor/rules
cp /tmp/bm-skills/skills/bm-code-management/SKILL.md ~/.cursor/rules/bm-code-management.mdc
```

Cursor Settings > Rules で読み込まれていることを確認してください。

### 7. 直接 git clone（fallback）

`gh` が使えない環境向けの最終手段。

```bash
git clone --depth 1 https://github.com/basemachina/skills.git /tmp/bm-skills
cp -R /tmp/bm-skills/skills/bm-code-management ~/.claude/skills/
```

install 先は各エージェントの skills ディレクトリ（`~/.claude/skills/` / `~/.agents/skills/` / `~/.cursor/rules/` / `.github/skills/` 等）に読み替えてください。

## アップデート

| インストール方法 | 更新コマンド |
| --- | --- |
| `gh skill install` | `gh skill update bm-code-management` または `gh skill update --all` |
| Claude Code plugin | `/plugin marketplace update basemachina` |
| Gemini CLI | `gemini extensions update` |
| 手動 `git clone` | 再度 install を実行（既存ディレクトリを削除してから） |

## アンインストール

| インストール方法 | コマンド |
| --- | --- |
| `gh skill install` | `gh skill uninstall bm-code-management` |
| Claude Code plugin | `/plugin uninstall bm-skills@basemachina` |
| Gemini CLI | `gemini extensions uninstall basemachina-skills` |
| 手動 | install 先ディレクトリを `rm -rf` |

## 関連リンク

- BaseMachina 公式ドキュメント: <https://docs.basemachina.com/preview/code_management/>
- Agent Skills Specification: <https://agentskills.io/specification>
- Claude Code plugins: <https://code.claude.com/docs/en/plugins>
- `gh skill` マニュアル: <https://cli.github.com/manual/gh_skill>
