# TS 設定（`defineAction` / `defineConfig`）

`basemachina.config.ts` および `src/actions/*.ts` の編集ガイド。

- 公式ドキュメント: <https://docs.basemachina.com/preview/code_management/>
- 設定ファイル: <https://docs.basemachina.com/preview/code_management/configuration/>
- `defineConfig`: <https://docs.basemachina.com/preview/code_management/sdk/define_config/>
- `defineAction`: <https://docs.basemachina.com/preview/code_management/sdk/define_action/>
- `readFile`: <https://docs.basemachina.com/preview/code_management/sdk/read_file/>
- SDK の型定義: `node_modules/@basemachina/sdk/dist/oac/index.d.ts`

## ワークフロー

1. **編集**: `basemachina.config.ts` と既存の `src/actions/*.ts` を Read してパターンを把握し、必要な変更を Edit / Write する。書き方は公式ドキュメントの SDK セクションと `.d.ts` を確認する
2. **型チェック**: 検出した PM の TypeScript チェックコマンド（`npx tsc --noEmit` 等。SKILL.md § パッケージマネージャー参照）でエラーがないことを確認する。エラーが出たら下記「型エラー」の手順で解消してから先に進む
3. **差分プレビュー**: `bm sync --dry` を実行し、変更したアクション ID と差分種別（create / update / no-op）が編集意図と一致しているかを確認する。意図と異なる差分が出たら引き渡さず編集に戻る
4. **引き渡し**: 実行したコマンド・変更件数・注目すべきアクション ID を構造化してユーザーに返す。実反映（PR / CI 経由）はユーザーまたは CI/CD 運用に委ねる

## 型エラー

`bm sync --dry` が「設定ファイル読み込み」段階で失敗したら:

1. PM 検出済みの TypeScript チェックコマンドで全型エラーを一括表示する
2. `node_modules/@basemachina/sdk/dist/oac/index.d.ts` を Read して正しい型を確認する
3. 修正後に `bm sync --dry` を再実行する

## JS アクションの宣言

`defineAction` の `class` フィールドで `"javascript"` を指定し、`code: readFile("./js-action-codes/<id>.ts")` で本体ファイルを参照する形式。**コード本体ファイルの書き方は `references/js-action.md` を参照**。

```ts
defineAction({
  id: "create-user",
  class: "javascript",
  code: readFile("./js-action-codes/create-user.ts"),
  // ...
});
```

## 削除の挙動（論理削除）

`basemachina.config.ts` から import を外しても Web UI 上のアクション行や revision は残り、該当環境で無効化されるだけ（import を戻せば復元可）。「削除したい」と言われたら、この挙動を先に説明する。
