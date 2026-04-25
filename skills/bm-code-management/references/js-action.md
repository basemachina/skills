# JavaScript アクションのコード本体

`defineAction({ class: "javascript", code: readFile("./js-action-codes/xxx.ts") })` から参照される `.ts` / `.js` ファイルの作成・編集ガイド。

- 公式ドキュメント: <https://docs.basemachina.com/action/datasources/javascript_action/>
- 型定義: `node_modules/@basemachina/action/dist/*.d.ts`
- 型定義ファイルのダウンロード: <https://docs.basemachina.com/action/datasources/javascript_action/download_dts_file/>

**API・グローバル関数・型・引数の詳細は記憶で書かず、上記ドキュメントと型定義を都度参照する**。

## ワークフロー

1. **型と既存実装の確認**
   - `node_modules/@basemachina/action/dist/*.d.ts` を Glob してから Read し、`Handler` 型・組み込み関数の型シグネチャを確認する
   - 既存の `js-action-codes/*.ts`（あれば）を Read して export 形式・命名・エラー処理の流儀を把握する
2. **編集**
   - default export の関数として書き、JSDoc で `@type { import("@basemachina/action").Handler }` を付ける
   - 組み込み関数・引数・戻り値の詳細はドキュメントを Open（`/action/datasources/javascript_action/builtin_functions/...`）して都度確認する。記憶で書かない
   - 利用不可機能の制約（後述）に違反していないかをコードレビュー目線で確認する
3. **静的検査**: 検出した PM の TypeScript チェックコマンド（SKILL.md § パッケージマネージャー参照）で型エラーが無いことを確認する
4. **差分プレビュー**: `bm sync --dry` を実行し、`js-action-codes/<id>.ts` 由来の差分が「コード差分」として意図通りに出ているかを確認する
5. **引き渡し**: 編集ファイル一覧、影響アクション ID、注意点（破壊的か / 既存挙動を保つか）を構造化して返す

## 組み込み関数（詳細は docs を都度参照）

| 関数 | 公式ドキュメント |
| --- | --- |
| `executeAction` | <https://docs.basemachina.com/action/datasources/javascript_action/builtin_functions/execute_action/> |
| `createActionJob` | <https://docs.basemachina.com/action/datasources/javascript_action/builtin_functions/create_action_job/> |
| `wait` | <https://docs.basemachina.com/action/datasources/javascript_action/builtin_functions/wait/> |

引数・戻り値・エラー時の挙動は上記ページを Open して確認する。本ファイルには詳細を書かない（公式と乖離するため）。

## 引数の形

第 1 引数はパラメータオブジェクト、第 2 引数は事前定義パラメータ（`vars`, `secrets`, `currentUser`, `environment` など）。詳細は <https://docs.basemachina.com/action/parameter/predefined_parameter/> を参照。

## 利用不可機能（落とし穴）

`defineAction` の `parameters` で定義しても、JS アクションの第 1 引数で扱えない型がある。`bm sync --dry` ではエラーにならず、実行時に初めて発覚する。

- **JSON 値パラメータ**: 不可
- **SQL パラメータ**: 不可
- **ファイル / Web API**: 一部プロパティのみ対応

詳細は <https://docs.basemachina.com/action/datasources/javascript_action/> の制約セクションを都度確認する。

## エラーハンドリング

公式ドキュメント: <https://docs.basemachina.com/action/datasources/javascript_action/error_handlings/>

設計指針:

- **正常**: `return` で値を返す
- **異常 (単純)**: `throw new Error("メッセージ")`
- **異常 (詳細を結果として返したい)**: `ResultError` クラスで構造化エラーを返す。加工スクリプトや別アクションから判別しやすくなる

「複数の判定条件を message 文字列だけで分岐させる」設計はアンチパターン（呼び出し側で判別不能になる）。条件が複数あるなら `ResultError` のフィールドで分ける。

ジョブから `throw` した場合、ステータスは「エラー」になる（「実行完了」ではない）。

## 関連リンク

- 実行権限: <https://docs.basemachina.com/action/action_permission/>
- 事前定義パラメータ: <https://docs.basemachina.com/action/parameter/predefined_parameter/>
