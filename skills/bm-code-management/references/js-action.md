# JavaScriptアクションコード

`defineAction({ type: "javascript", code: readFile("...") })`から参照される`.ts`または`.js`を編集するときに使う。

固定directoryを前提にしない。download templateでは通常`src/actions/js-action-codes/`に置かれるが、対象definitionの`readFile(...)`と既存repo構成を正とする。

## 確認するsource

- [JavaScriptアクション](https://docs.basemachina.com/action/datasources/javascript_action/)
- [エラーハンドリング](https://docs.basemachina.com/action/datasources/javascript_action/error_handlings/)
- [型定義のdownload](https://docs.basemachina.com/action/datasources/javascript_action/download_dts_file/)
- [事前定義parameter](https://docs.basemachina.com/action/parameter/predefined_parameter/)
- runtime型: `node_modules/@basemachina/action/dist/*.d.ts`

`executeAction`、`createActionJob`、`wait`などの組み込み関数を使う前に、該当する公式ページを開き、現在の引数、戻り値、失敗時の挙動、非対応条件を確認する。

## Workflow

1. インストール済み`@basemachina/action`のdeclarationで`Handler`と組み込み関数のsignatureを確認する
2. 対象`defineAction`、`readFile(...)`の参照先、周辺実装を読み、repoのexport・命名・error処理に合わせる
3. default exportのhandlerを書く。JavaScript fileでは`@type { import("@basemachina/action").Handler }` JSDocを付ける
4. 検出したpackage managerでTypeScript checkを実行する
5. source全文は`git diff`で確認し、`bm sync --dry`は対象action IDと差分種別の確認にだけ使う
6. 変更file、action ID、validation結果、ユーザーによるruntime testが必要な挙動を報告する
