---
name: bm-js-action
description: "BaseMachina の JavaScript アクションの**コード本体**（`defineAction({ class: \"javascript\", code: readFile(\"./js-action-codes/xxx.ts\") })` から参照される `.ts` / `.js` ファイル）を新規作成・編集するときに使う skill。`executeAction` / `createActionJob` / `wait` などの組み込み関数や `ResultError` を扱う。`defineAction` / `defineConfig` などの**TypeScript 設定**側と `bm sync --dry` 実行は `bm-code-management` skill、CI/CD 反映は `bm-cicd-setup` skill に委譲する。公式ドキュメント: https://docs.basemachina.com/action/datasources/javascript_action/"
allowed-tools: "Bash(bm sync --dry:*) Bash(bm --help:*) Bash(bm --version) Bash(npx tsc:*) Bash(yarn tsc:*) Bash(pnpm exec tsc:*) Bash(bunx tsc:*) Read Grep Glob Edit Write"
---

# BaseMachina JavaScript アクション skill

JavaScript アクションのコード本体を書く skill。**API・グローバル関数・型・引数の詳細は記憶で書かず、公式ドキュメントと `@basemachina/action` の型定義を都度参照する**。

- 公式ドキュメント（JS アクション）: <https://docs.basemachina.com/action/datasources/javascript_action/>
- 型定義: `node_modules/@basemachina/action/dist/*.d.ts`

## いつ使うか

- `./js-action-codes/*.ts`（`readFile` から参照される JS アクション本体）を新規作成・編集する
- 別アクション呼び出し（`executeAction`）、ジョブ化（`createActionJob`）、待機（`wait`）を組み合わせるロジックを書く
- エラー時の挙動を `throw` / `ResultError` で設計する

## いつ使わないか

- `defineAction` / `defineConfig` の編集や `bm sync --dry` 実行 → `bm-code-management`
- GitHub Actions / OIDC / 環境別 sync → `bm-cicd-setup`

## ワークフロー

1. **型と既存実装の確認**
   - `node_modules/@basemachina/action/dist/*.d.ts` を Glob してから Read し、`Handler` 型・組み込み関数の型シグネチャを確認する
   - 既存の `js-action-codes/*.ts`（あれば）を Read して export 形式・命名・エラー処理の流儀を把握する
2. **編集**
   - default export の関数として書き、JSDoc で `@type { import("@basemachina/action").Handler }` を付ける
   - 組み込み関数・引数・戻り値の詳細はドキュメントを Open（`/action/datasources/javascript_action/builtin_functions/...`）して都度確認する。記憶で書かない
   - 利用不可機能の制約（後述）に違反していないかをコードレビュー目線で確認する
3. **静的検査**
   - `tsc --noEmit` を検出した PM 経由で実行する（PM 検出は `bm-code-management` skill の手順に従う。本 skill 単体で動かす場合は `package.json` の `packageManager` → ロックファイルの順で判定する）
4. **差分プレビュー**
   - `bm sync --dry` を実行し、`js-action-codes/<id>.ts` 由来の差分が「コード差分」として意図通りに出ているかを確認する
   - フラグの詳細は `bm sync --help` または公式ドキュメント（<https://docs.basemachina.com/preview/code_management/cli/sync/>）を参照する。実反映（`--dry` なしの `bm sync`）は本 skill では実行しない
5. **引き渡し**
   - 編集ファイル一覧、影響アクション ID、注意点（破壊的か / 既存の挙動を保つか）を構造化して返す。実反映は `bm-cicd-setup` skill またはユーザー判断に委ねる

## 組み込み関数（詳細は docs を都度参照）

| 関数 | 公式ドキュメント |
| --- | --- |
| `executeAction` | <https://docs.basemachina.com/action/datasources/javascript_action/builtin_functions/execute_action/> |
| `createActionJob` | <https://docs.basemachina.com/action/datasources/javascript_action/builtin_functions/create_action_job/> |
| `wait` | <https://docs.basemachina.com/action/datasources/javascript_action/builtin_functions/wait/> |

引数・戻り値・エラー時の挙動は上記ドキュメントを Open して確認する。skill 内には詳細を書かない（公式と乖離するため）。

## 引数の形

第 1 引数はパラメータオブジェクト、第 2 引数は事前定義パラメータ（`vars`, `secrets`, `currentUser`, `environment` など）。詳細は <https://docs.basemachina.com/action/parameter/predefined_parameter/> を参照。

## 利用不可機能（落とし穴）

`defineAction` の `parameters` で定義しても、JS アクションの第 1 引数で扱えない型がある。`bm sync --dry` ではエラーにならず、実行時に初めて発覚する。

- **JSON 値パラメータ**: 不可
- **SQL パラメータ**: 不可
- **ファイル / Web API**: 一部プロパティのみ対応

詳細は <https://docs.basemachina.com/action/datasources/javascript_action/> の「制約」を都度確認する。

## エラーハンドリング

公式ドキュメント: <https://docs.basemachina.com/action/datasources/javascript_action/error_handlings/>

設計指針（推奨パターン。詳細は docs 参照）:

- **正常**: `return` で値を返す
- **異常 (単純)**: `throw new Error("メッセージ")`
- **異常 (詳細を結果として返したい)**: `ResultError` クラスで構造化エラーを返す。加工スクリプトや別アクションから判別しやすくなる

「複数の判定条件を message 文字列だけで分岐させる」設計はアンチパターン（呼び出し側で判別不能になる）。条件が複数あるなら `ResultError` のフィールドで分ける。

ジョブから `throw` した場合、ステータスは「エラー」になる（「実行完了」ではない）。

## bm CLI 認証

`bm sync --dry` が `authentication required` 等で失敗したら、ユーザーに `bm login` の実行を依頼する。`bm login` はブラウザを開く interactive フローなのでエージェントから実行しない。

## 参照先

- JS アクション総覧: <https://docs.basemachina.com/action/datasources/javascript_action/>
- 型定義ファイルのダウンロード: <https://docs.basemachina.com/action/datasources/javascript_action/download_dts_file/>
- 事前定義パラメータ: <https://docs.basemachina.com/action/parameter/predefined_parameter/>
- 実行権限: <https://docs.basemachina.com/action/action_permission/>
- 関連 skill: `bm-code-management`（TS 設定 + bm sync --dry） / `bm-cicd-setup`（CI/CD と環境別反映）
- ローカル型定義: `node_modules/@basemachina/action/dist/*.d.ts`
