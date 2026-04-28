---
name: bm-code-management
description: "BaseMachina のコード管理を扱うときの skill。`defineAction` / `defineConfig` の TypeScript 設定編集、JavaScript アクションのコード本体（`readFile(...)` 参照先）の作成・編集、コードエディターのビューコードをコード取得設定と同じ repo で扱う作業、`bm sync --dry` での差分プレビューを 1 つのドメインとして扱う。アクション実行や本番反映は扱わない。詳細は領域ごとに `references/` に分割。公式ドキュメント: https://docs.basemachina.com/preview/code_management/"
allowed-tools: "Bash(bm sync --dry:*) Bash(bm --help:*) Bash(bm --version) Bash(npx tsc:*) Bash(yarn tsc:*) Bash(pnpm exec tsc:*) Bash(bunx tsc:*) Bash(npm i:*) Bash(yarn add:*) Bash(pnpm add:*) Bash(bun add:*) Bash(npm outdated:*) Bash(yarn outdated:*) Bash(pnpm outdated:*) Bash(bun outdated:*) Read Grep Glob Edit Write"
---

# BaseMachina コード管理 skill

コマンド・フラグ・型・ビュー連携の詳細は記憶で書かず、公式ドキュメント（<https://docs.basemachina.com/preview/code_management/>）と SDK / runtime の型定義（`node_modules/@basemachina/sdk` / `@basemachina/action`）を都度確認する。

## いつ使うか

- `defineAction` / `defineConfig` を新規作成・編集する
- JavaScript アクションのコード本体を新規作成・編集する
- コードエディターのビューコードを同じ repo に置き、コード取得設定と組み合わせる
- `bm sync --dry` で差分をプレビューしてユーザーに示す
- 認証切れや TypeScript 型エラーから復旧する

## いつ使わないか

- アクションの**実行**（テスト含む）
- ビュー設定そのもののコード管理。公式 docs 上、ビューの設定はコード管理対象外で、ビュー内コードのみコード取得設定と組み合わせて同居できる
- **本番への実反映**（`bm sync` を `--dry` 抜きで叩く操作）。実反映は CI 経由、または明示的なユーザー操作に委ねる

## 領域選択（navigation）

ユーザーの作業内容に応じて、以下の reference を**必要なものだけ**読み込む。

| 作業 | 読むべき reference |
| --- | --- |
| `basemachina.config.ts` / `defineAction` / `defineConfig` を編集 | [`references/ts-config.md`](references/ts-config.md) |
| JavaScript アクションのコード本体を書く・直す（`executeAction` / `createActionJob` / `wait` / `ResultError` など） | [`references/js-action.md`](references/js-action.md) |
| `views/**/*.tsx` / `@basemachina/view` / コード取得設定 / ビューコードの build・配置 | [`references/view-code.md`](references/view-code.md) |

複数領域に跨る場合（例: TS 設定で JS アクションを宣言し、コード本体も書く）は、該当する reference を順次 Read する。

## 共通: Pre-flight

1. `basemachina.config.ts` がカレントディレクトリのルートに存在することを確認する。無ければ `--config <path>` 指定またはプロジェクトルートへの移動を依頼する
2. 下記「パッケージマネージャー」の手順で PM を 1 つに確定する。以降の install / outdated / 最新化 / TypeScript チェックはすべて確定した PM のものを使う
3. `@basemachina/sdk` / `@basemachina/cli` のインストール状態を確認する（CLI は `bm --version` の成功、SDK は `package.json` の `dependencies` / `devDependencies` への記載で判定）。未インストールがあればユーザーに「インストールしますか？」と確認し、yes の場合に限り PM ごとの **dev 依存追加** コマンドを実行する
4. PM ごとの **outdated** コマンドで `@basemachina/sdk` / `@basemachina/cli` の新バージョンの有無を確認する。新バージョンがあればユーザーに「更新しますか？」と確認し、yes の場合に限り PM ごとの **最新化** コマンドを実行する。`package.json` を Read して devDependency に入っているパッケージには dev フラグを付ける。yarn berry など outdated 相当が無い PM では確認をスキップしてユーザーに任意ツールでの確認を促す
5. JS アクションを扱う場合は `@basemachina/action`（runtime 型定義）のインストールも併せて確認する
6. ビューコードを扱う場合は `@basemachina/view` の docs、`tsconfig.json` の JSX 設定、`react` / `@types/react` のインストール状態を確認する

## 共通: パッケージマネージャー

### 検出（優先度順）

1. **`package.json` の `packageManager` フィールド**を最優先で使う。例: `"packageManager": "pnpm@8.6.0"` → pnpm。Corepack 対応プロジェクトの公式指定であり最も信頼できる
2. **ロックファイル**で判定する。`pnpm-lock.yaml` → pnpm / `yarn.lock` → yarn（ルートに `.yarnrc.yml` があれば berry、無ければ classic）/ `bun.lockb` または `bun.lock` → bun / `package-lock.json` → npm
3. **どれも該当しないか複数ヒット**した場合はユーザーに「どの PM を使いますか？」と確認する。複数のロックファイルが共存していたら「どれが正で、他は削除すべきか」も併せて確認する。`packageManager` フィールドとロックファイルが食い違う場合も同様に確認する

### コマンド対応表

| 操作 | npm | yarn (classic) | yarn (berry) | pnpm | bun |
| --- | --- | --- | --- | --- | --- |
| dev 依存追加 | `npm i -D <pkg>` | `yarn add -D <pkg>` | `yarn add -D <pkg>` | `pnpm add -D <pkg>` | `bun add -d <pkg>` |
| 最新化（dep） | `npm i <pkg>@latest` | `yarn add <pkg>@latest` | `yarn add <pkg>@latest` | `pnpm add <pkg>@latest` | `bun add <pkg>@latest` |
| 最新化（devDep） | `npm i -D <pkg>@latest` | `yarn add -D <pkg>@latest` | `yarn add -D <pkg>@latest` | `pnpm add -D <pkg>@latest` | `bun add -d <pkg>@latest` |
| outdated 確認 | `npm outdated <pkg>` | `yarn outdated <pkg>` | （標準では無い。スキップ） | `pnpm outdated <pkg>` | `bun outdated <pkg>` |
| ローカルバイナリ実行（`tsc` 等） | `npx tsc` | `yarn tsc` | `yarn tsc` | `pnpm exec tsc` | `bunx tsc` |

各 reference 内で `tsc` 等を指している箇所は、検出した PM の「ローカルバイナリ実行」コマンドに読み替える。

## 共通: `bm sync` の使い分け（ガードレール）

- **エージェントから実行できるのは `bm sync --dry` のみ**（`allowed-tools` で制限）
- 差分の意図が編集と一致するかを必ずユーザーに引き渡し、実反映は CI またはユーザー手動操作に委ねる
- JavaScript アクションの `code` 本文は dry-run 出力では省略されるため、本文差分の確認には `git diff` を使う
- フラグ詳細は `bm sync --help` または <https://docs.basemachina.com/preview/code_management/cli/sync/> を参照する
- CI/CD の運用詳細は <https://docs.basemachina.com/preview/code_management/ci_cd/> を参照する。PR では `bm sync --dry`、マージ後や環境デプロイでは CI が `bm sync` / `bm sync <環境ID>` を担う前提で説明する

## 共通: 認証

`bm sync --dry` がローカルで `authentication required` 等で失敗したら、ユーザーに `bm login` の実行を依頼する。`bm login` はブラウザを開く interactive フローで、エージェントから実行すると state トークンの受け渡しで破綻する。

## 参照先

- 公式ドキュメント（コード管理トップ）: <https://docs.basemachina.com/preview/code_management/>
- 設定ファイル: <https://docs.basemachina.com/preview/code_management/configuration/>
- `bm sync` CLI: <https://docs.basemachina.com/preview/code_management/cli/sync/>
- CI/CD: <https://docs.basemachina.com/preview/code_management/ci_cd/>
- JS アクション: <https://docs.basemachina.com/action/datasources/javascript_action/>
- ビューコードの Git 管理: <https://docs.basemachina.com/view/code_editor/git_management/>
- コード取得設定との連携: <https://docs.basemachina.com/preview/code_management/examples/view_code_fetch/>
- SDK の型定義: `node_modules/@basemachina/sdk/dist/oac/index.d.ts`
- JS アクション runtime 型: `node_modules/@basemachina/action/dist/*.d.ts`
- CLI のフラグ一覧: `bm sync --help`
