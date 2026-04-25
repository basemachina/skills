# basemachina/skills

BaseMachina 用の [Agent Skill](https://agentskills.io/specification) を配布するパブリックリポジトリ。

- ライセンス: Apache-2.0
- 対象エージェント: Claude Code / Codex CLI / Cursor / GitHub Copilot CLI / Gemini CLI など、Agent Skill 仕様をサポートする各種エージェント（エージェントごとの install 先は下記の「インストール」セクションおよび[`gh skill` manual](https://cli.github.com/manual/gh_skill) を参照）

## 収録 skill

| skill | 概要 |
| --- | --- |
| [`bm-code-management`](skills/bm-code-management/) | `defineAction` / `defineConfig` を TypeScript で編集し、`bm sync --dry` で差分をプレビューする skill（アクション実行は扱わない） |
| [`bm-js-action`](skills/bm-js-action/) | JavaScript アクションの**コード本体**（`./js-action-codes/*.ts`）を作成・編集する skill。`executeAction` / `createActionJob` / `wait` / `ResultError` の取り扱いを含む |
| [`bm-cicd-setup`](skills/bm-cicd-setup/) | GitHub Actions による BaseMachina コード管理の運用（OIDC 認証、`bm sync` の環境別反映、2 / 3 ブランチパターン）を構築・改修する skill |

## インストール

用途に応じて以下から選択してください。以下の例ではコマンド引数に `bm-code-management` を指定していますが、他の skill（`bm-js-action`, `bm-cicd-setup`）も同様に skill 名を差し替えれば install できます。引数を省略する形式（`npx skills add basemachina/skills` など）であれば対話的にすべての skill を選択できます。

### 1. `npx skills`（Node.js さえあれば install 可 / 推奨）

Vercel Labs の [`skills`](https://github.com/vercel-labs/skills) CLI 経由。Node.js 18+ があれば追加ツール不要で、対話的に skill を選択して install できます。

```bash
# 対話形式で skill を選択して install（プロジェクトスコープ）
npx skills add basemachina/skills

# ユーザー（グローバル）スコープに install
npx skills add basemachina/skills --global

# 特定の skill だけを確認なしで install
npx skills add basemachina/skills --skill bm-code-management --yes

# 特定のエージェント向けに install
npx skills add basemachina/skills --agent claude-code
```

対応エージェント一覧は [vercel-labs/skills](https://github.com/vercel-labs/skills) を参照（Claude Code / Codex / Cursor / GitHub Copilot / Gemini CLI / Warp / Windsurf などを含む）。

### 2. `gh skill install`（cross-agent）

GitHub CLI v2.90.0 以降に同梱される公式 Agent Skills インストーラ。`--agent` で指定したエージェントごとに install 先ディレクトリを自動解決します（対応エージェントは [`gh skill install` manual](https://cli.github.com/manual/gh_skill_install) 参照）。

```bash
# Claude Code にユーザースコープで install
gh skill install basemachina/skills bm-code-management --agent claude-code --scope user

# プロジェクトスコープ（チーム共有）
gh skill install basemachina/skills bm-code-management --agent claude-code --scope project

# 特定の git tag または commit SHA に pin（タグが切られている場合のみ）
gh skill install basemachina/skills bm-code-management --pin <tag-or-sha>

# 対話モードで選択
gh skill install
```

対応エージェント: `claude-code` / `codex` / `cursor` / `github-copilot` / `gemini-cli` / `warp` / `windsurf` ほか。

### 3. Claude Code plugin marketplace（Claude Code 特化 / auto-update 対応）

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

### 4. チーム自動配布（`.claude/settings.json`）

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

### 5. Gemini CLI（`gemini skills install`）

Gemini CLI の Agent Skills サブコマンド経由で install します。`gemini extensions install` は `gemini-extension.json` を持つ repo 向けで、本 repo は skill コレクションなので使えません。

```bash
# 全 skill を install（デフォルトは user スコープ）
gemini skills install https://github.com/basemachina/skills.git

# workspace スコープ（このリポジトリのみで有効）
gemini skills install https://github.com/basemachina/skills.git --scope workspace
```

`gemini skills list` で認識されていることを確認してください。更新は再度 `gemini skills install` を実行します。

### 6. Codex CLI

Codex CLI はスキャン対象ディレクトリが決まっているため、該当箇所に SKILL.md を配置します。

```bash
# ユーザースコープ
mkdir -p ~/.agents/skills
tmp=$(mktemp -d) && git clone --depth 1 https://github.com/basemachina/skills.git "$tmp"
cp -R "$tmp/skills/bm-code-management" ~/.agents/skills/
rm -rf "$tmp"

# または repo 直下の .agents/skills/ に置けばそのリポジトリ内でのみ有効
```

セッション内で `$skill-installer` が利用可能な場合はそちらからも install できます。配置後に `/skills` で認識を確認してください。

### 7. Cursor（rules として手動配置）

Cursor は現状 SKILL.md を native には読まないため、プロジェクトの `.cursor/rules/` に `.mdc` として配置します（Cursor 公式がサポートするのは project スコープのみ）。

```bash
tmp=$(mktemp -d) && git clone --depth 1 https://github.com/basemachina/skills.git "$tmp"
mkdir -p .cursor/rules
cp "$tmp/skills/bm-code-management/SKILL.md" .cursor/rules/bm-code-management.mdc
rm -rf "$tmp"
```

Cursor Settings の Rules 画面で読み込まれていることを確認してください。全プロジェクトで共通利用したい場合は、Cursor Settings の User Rules に内容を貼り付ける運用が公式サポートされています。

### 8. 直接 git clone（fallback）

`gh` が使えない環境向けの最終手段。

```bash
tmp=$(mktemp -d) && git clone --depth 1 https://github.com/basemachina/skills.git "$tmp"
mkdir -p ~/.claude/skills
cp -R "$tmp/skills/bm-code-management" ~/.claude/skills/
rm -rf "$tmp"
```

install 先は各エージェントの skills ディレクトリに読み替えてください。

- Claude Code（user）: `~/.claude/skills/`
- Claude Code（project）: `.claude/skills/`
- Codex CLI（user）: `~/.agents/skills/`
- Codex CLI（project）: `.agents/skills/`
- GitHub Copilot CLI（user）: `~/.copilot/skills/`
- GitHub Copilot CLI（project）: `.github/skills/`
- Gemini CLI（user）: `~/.gemini/skills/`
- Gemini CLI（project）: `.gemini/skills/`
- Cursor（project）: `.cursor/rules/`（`.mdc` 拡張子）

## アップデート

| インストール方法 | 更新コマンド |
| --- | --- |
| `npx skills` | `npx skills update` または `npx skills update bm-code-management` |
| `gh skill install` | `gh skill update bm-code-management` または `gh skill update --all` |
| Claude Code plugin | `/plugin marketplace update basemachina` |
| Gemini CLI | 再度 `gemini skills install` を実行（`uninstall` → `install` でも可） |
| 手動 `git clone` | 再度 install を実行（既存ディレクトリを削除してから） |

## アンインストール

| インストール方法 | コマンド |
| --- | --- |
| `npx skills` | `npx skills remove bm-code-management` |
| `gh skill install` | `gh skill` には `uninstall` サブコマンドが無い。install 先ディレクトリ（`~/.claude/skills/bm-code-management` 等）を `rm -rf` で削除する |
| Claude Code plugin | `/plugin uninstall bm-skills@basemachina` |
| Gemini CLI | `gemini skills uninstall bm-code-management --scope workspace`（user スコープなら `--scope user`） |
| 手動 | install 先ディレクトリを `rm -rf` |

## 関連リンク

- BaseMachina 公式ドキュメント: <https://docs.basemachina.com/preview/code_management/>
- Agent Skills Specification: <https://agentskills.io/specification>
- Claude Code plugins: <https://code.claude.com/docs/en/plugins>
- `gh skill` マニュアル: <https://cli.github.com/manual/gh_skill>
- `skills` CLI（Vercel Labs）: <https://github.com/vercel-labs/skills> / skill ディレクトリ: <https://skills.sh/>
