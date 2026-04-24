---
name: bm-code-management
description: ユーザーが BaseMachina でアクション定義（`defineAction` / `defineConfig`）を TypeScript で編集し、`bm sync` で差分をプレビューするときに使う skill。アクション実行は扱わない。公式ドキュメント: https://docs.basemachina.com/preview/code_management/
allowed-tools: Bash(bm sync:*), Bash(bm --help:*), Bash(bm --version), Bash(npx tsc:*), Bash(npm outdated:*), Bash(npm i:*), Bash(yarn add:*), Bash(yarn outdated:*), Bash(yarn tsc:*), Bash(pnpm add:*), Bash(pnpm outdated:*), Bash(pnpm exec:*), Bash(bun add:*), Bash(bun outdated:*), Bash(bunx tsc:*), Read, Grep, Glob, Edit, Write
---

# BaseMachina コード管理 skill

コマンド・フラグ・型の詳細は記憶で書かず、公式ドキュメント（<https://docs.basemachina.com/preview/code_management/>）と SDK の型定義（`node_modules/@basemachina/sdk/dist/oac/index.d.ts`）を都度確認する。

## いつ使うか

- `defineAction` / `defineConfig` を新規作成・編集する
- `bm sync` で差分をプレビューしてユーザーに示す
- 認証切れや TypeScript 型エラーから復旧する

## ワークフロー

1. **編集**: `basemachina.config.ts` と既存の `src/actions/*.ts` を Read してパターンを把握し、必要な変更を Edit / Write する。書き方は公式ドキュメントの SDK セクションと `.d.ts` を確認する。
2. **品質チェック**:
   - `npx tsc --noEmit` で型エラーがないことを確認する。エラーが出たら「型エラー」セクションの手順で解消してから先に進む。
   - `bm sync --dry` を Bash で実行し、変更したアクション ID と差分種別（create / update / no-op）が編集意図と一致しているかを確認する。意図と異なる差分が出たら引き渡さず編集に戻る。フラグの詳細は `bm sync --help` を参照する。
3. **引き渡し**: 実行したコマンド・変更件数・注目すべきアクション ID を構造化してユーザーに返す。以降の進め方（PR 作成の要否、apply のタイミング等）はユーザーに委ねる。

## Pre-flight

1. `basemachina.config.ts` がカレントディレクトリのルートに存在することを確認する。無ければ `--config <path>` 指定またはプロジェクトルートへの移動を依頼する。
2. パッケージマネージャー（以降 PM）を「パッケージマネージャー」セクションの手順で 1 つに確定する。以降の install / outdated / 最新化コマンドはすべて確定した PM のものを使う。
3. `@basemachina/sdk` / `@basemachina/cli` のインストール状態を確認する（CLI は `bm --version` の成功、SDK は `package.json` の `dependencies` / `devDependencies` への記載で判定）。未インストールのパッケージがあればユーザーに「インストールしますか？」と確認し、yes の場合に限り skill が PM ごとの **dev 依存追加** コマンドを実行する。
4. PM ごとの **outdated** コマンドで `@basemachina/sdk` / `@basemachina/cli` の新バージョンの有無を確認する。新バージョンがあればユーザーに「更新しますか？」と確認し、yes の場合に限り skill が PM ごとの **最新化** コマンドを実行する。`package.json` を Read して devDependency に入っているパッケージには dev フラグを付ける。yarn berry のように outdated 相当が無い PM では確認をスキップし、ユーザーに任意のツールでの確認を促す。

## パッケージマネージャー

### 検出（優先度順）

1. **`package.json` の `packageManager` フィールド**を最優先で使う。例: `"packageManager": "pnpm@8.6.0"` → pnpm。Corepack 対応プロジェクトの公式指定であり最も信頼できる。
2. **ロックファイル**で判定する。`pnpm-lock.yaml` → pnpm / `yarn.lock` → yarn（リポジトリルートに `.yarnrc.yml` があれば berry、無ければ classic）/ `bun.lockb` または `bun.lock` → bun / `package-lock.json` → npm。
3. **どれも該当しないか複数ヒット**した場合はユーザーに「どの PM を使いますか？」と確認する。複数のロックファイルが共存している場合は「どれが正で、他は削除すべきか」も併せて確認する。`packageManager` フィールドとロックファイルが食い違う場合も同様に確認する。

### コマンド対応表

| 操作 | npm | yarn (classic) | yarn (berry) | pnpm | bun |
| --- | --- | --- | --- | --- | --- |
| dev 依存追加 | `npm i -D <pkg>` | `yarn add -D <pkg>` | `yarn add -D <pkg>` | `pnpm add -D <pkg>` | `bun add -d <pkg>` |
| 最新化（dep） | `npm i <pkg>@latest` | `yarn add <pkg>@latest` | `yarn add <pkg>@latest` | `pnpm add <pkg>@latest` | `bun add <pkg>@latest` |
| 最新化（devDep） | `npm i -D <pkg>@latest` | `yarn add -D <pkg>@latest` | `yarn add -D <pkg>@latest` | `pnpm add -D <pkg>@latest` | `bun add -d <pkg>@latest` |
| outdated 確認 | `npm outdated <pkg>` | `yarn outdated <pkg>` | （標準では無い。スキップ） | `pnpm outdated <pkg>` | `bun outdated <pkg>` |
| ローカルバイナリ実行（`tsc` 等） | `npx tsc` | `yarn tsc` | `yarn tsc` | `pnpm exec tsc` | `bunx tsc` |

`npx tsc --noEmit` を本ドキュメントで指定している箇所も、検出した PM の「ローカルバイナリ実行」コマンドに読み替える。

## 認証切れ

`bm sync` が `authentication required` 等で失敗したら、ユーザーに `bm login` の実行を依頼する。`bm login` はブラウザを開く interactive フローで、エージェントから実行すると state トークンの受け渡しで破綻する。

## 型エラー

`bm sync` が「設定ファイル読み込み」段階で失敗したら:

1. `npx tsc --noEmit` で全型エラーを一括表示する
2. `node_modules/@basemachina/sdk/dist/oac/index.d.ts` を Read して正しい型を確認する
3. 修正後に `bm sync` を再実行する

## 削除の挙動（論理削除）

`basemachina.config.ts` から import を外しても Web UI 上のアクション行や revision は残り、該当環境で無効化されるだけ（import を戻せば復元可）。「削除したい」と言われたら、この挙動を先に説明する。

## 参照先

- 公式ドキュメント: <https://docs.basemachina.com/preview/code_management/>
- SDK の型定義: `node_modules/@basemachina/sdk/dist/oac/index.d.ts`
- JavaScript アクション runtime 型: `node_modules/@basemachina/action/dist/*.d.ts`
- CLI のフラグ一覧: `bm sync --help`
