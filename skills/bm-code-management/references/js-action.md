# JavaScript アクションのコード本体

`defineAction({ class: "javascript", code: readFile("./js-action-codes/xxx.ts") })` から参照される `.ts` / `.js` ファイルの作成・編集ガイド。

組み込み関数の引数仕様、エラーハンドリングの推奨パターン、利用不可機能、事前定義パラメータなどは**すべて公式ドキュメントを都度 Open する**。記憶で書かない。

- 総覧: <https://docs.basemachina.com/action/datasources/javascript_action/>
- 組み込み関数（`executeAction` / `createActionJob` / `wait` 等）: 上記ページ配下の各リンク
- エラーハンドリング: <https://docs.basemachina.com/action/datasources/javascript_action/error_handlings/>
- 型定義のダウンロード: <https://docs.basemachina.com/action/datasources/javascript_action/download_dts_file/>
- 事前定義パラメータ: <https://docs.basemachina.com/action/parameter/predefined_parameter/>

## ワークフロー

1. **型と既存実装の確認**
   - `node_modules/@basemachina/action/dist/*.d.ts` を Glob してから Read し、`Handler` 型と組み込み関数の型シグネチャを確認する（docs だけでは最新シグネチャを取りこぼす可能性がある）
   - 既存の `js-action-codes/*.ts` を Read し、project 固有の export 形式・命名・エラー処理の流儀を踏襲する
2. **編集**
   - default export の関数として書き、JSDoc で `@type { import("@basemachina/action").Handler }` を付ける
   - 組み込み関数の引数・戻り値・エラー時挙動は docs を Open して都度確認する
3. **静的検査**: 検出した PM の TypeScript チェックコマンド（SKILL.md § パッケージマネージャー）で型エラーが無いことを確認する
4. **差分プレビュー**: `bm sync --dry` を実行し、`js-action-codes/<id>.ts` 由来の差分が「コード差分」として意図通りに出ているかを確認する
5. **引き渡し**: 編集ファイル一覧、影響アクション ID、注意点を構造化して返す
