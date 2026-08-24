# TypeScript設定

`basemachina.config.ts`、action・view definition、`readFile`で読み込むcodeの編集に使う。

## 確認するsource

- [コード管理](https://docs.basemachina.com/code_management/)
- [設定ファイル](https://docs.basemachina.com/code_management/configuration/)
- [`defineConfig`](https://docs.basemachina.com/code_management/sdk/define_config/)
- [`defineAction`](https://docs.basemachina.com/code_management/sdk/define_action/)
- [`defineView`](https://docs.basemachina.com/code_management/sdk/define_view/)
- [`readFile`](https://docs.basemachina.com/code_management/sdk/read_file/)
- [`bm pull`](https://docs.basemachina.com/code_management/cli/pull/)
- [`bm sync`](https://docs.basemachina.com/code_management/cli/sync/)
- SDK型: `node_modules/@basemachina/sdk/dist/oac/index.d.ts`

## 設定rule

- deploy対象のaction・viewは`actions`・`views`に置く
- development限定のdefinitionは`developmentActions`・`developmentViews`に置く。development環境には反映されるが、環境間syncからは除外される
- 同じIDを通常arrayとdevelopment限定arrayの両方へ置かない
- 既存action・viewのID変更には`previousId`を使う。`bm sync --dry`でrenameを確認し、反映後のfollow-upで`previousId`を削除する
- `readFile(...)`のpathはdefinition fileからの相対path。既存repoの慣習を確認して配置する
- 複雑なvisual editor viewの`config`を手書きする前に、インストール済み型定義を読む

## Workflow

1. 現在のconfigと隣接definitionを読む
2. definition、import、config arrayへ必要最小の一貫した変更を行う
3. repoのTypeScript checkを実行する
4. `bm sync --dry`を実行し、create、update、ID change、re-enable、no-change、migration、skipを編集意図と照合する
5. JavaScript action・view code本文は`git diff`で確認する
6. 影響ID、validation結果、CIまたはユーザーへ残した非dry-run手順を報告する

## Configから外した場合とdisable

configからaction・viewを削除しても、defaultではBaseMachina環境は変更されない。

- `--with-disable`なしでは、configにないコード管理action・viewは変更されない
- `bm sync --dry --with-disable`で、development環境でdisable予定のコード管理項目をpreviewする
- 非dry-runの`--with-disable`は有効状態を変更するが、action・view dataやIDを削除しない
- definitionを戻してsyncするとdevelopment環境で再度有効化される
- configにないWeb管理項目は、`--with-disable`を使ってもWeb管理のまま残る

このskillから非dry-runのdisableを実行しない。

## Pullの挙動

`bm pull`はconfigにまだない対象Web管理definitionを取り込む。action・view definition、code file、参照定数、型、import、config arrayを生成・更新する。既存definition fileを上書きせず、config済みaction・viewに対する後続のWeb UI変更も取り込まない。
