# View definitionとcode

コードエディター・ビジュアルエディターのviewと、外部から取得するview codeを扱う。

## 管理方法を選ぶ

### 直接コード管理

コード管理対象のviewには`defineView`を使う。

- コードエディターでは`type: "codeEditor"`と`code`を指定し、通常は`readFile(...)`で読み込む
- ビジュアルエディターでは`type: "visualEditor"`と`config`を指定し、必要に応じて`queryParameters`を追加する
- `defineConfig`の`views`または`developmentViews`へ追加する
- 意図したID変更では`previousId`を使う
- TypeScriptと`bm sync --dry`で検証する

### 外部code取得workflow

storage上のcodeをaction経由で読み込む設定が意図されている場合だけ、code取得workflowを使う。

- view code、build、storage upload、環境別pathを既存repoの運用に合わせる
- code取得設定が有効なコードエディターviewはWeb管理として扱う。`bm pull`の対象外
- production storageへのuploadや非dry-runのBaseMachina syncを実行しない

## TypeScript確認

- actionとviewを同じrepoで扱う場合は`@basemachina/sdk/tsconfig.code.json`を継承する
- `.tsx`では`jsx: "react-jsx"`とview fileを含むinclude patternを確認する
- 型参照に必要な`react`、`@types/react`、`@basemachina/view`を確認する
- 大きなvisual editor `config`を編集する前にインストール済みSDK型を読む

## Workflow

1. viewが直接コード管理か、外部code取得設定かを特定する
2. 現在のdefinition、`readFile(...)`参照先、build script、CI workflowを読む
3. 選んだ管理方法を維持する最小の変更を行う
4. TypeScriptと既存のview build commandを実行する
5. 直接コード管理では`bm sync --dry`と`git diff`で確認する
6. 外部code取得では、CIまたはユーザーが行うbuild・upload手順を報告する

## 主なsource

- [`defineView`](https://docs.basemachina.com/code_management/sdk/define_view/)
- [`defineConfig`](https://docs.basemachina.com/code_management/sdk/define_config/)
- [`readFile`](https://docs.basemachina.com/code_management/sdk/read_file/)
- [設定ファイル](https://docs.basemachina.com/code_management/configuration/)
- [コード取得設定との連携](https://docs.basemachina.com/code_management/examples/view_code_fetch/)
- [ビューコードのGit管理](https://docs.basemachina.com/view/code_editor/git_management/)
- [`@basemachina/view`型定義](https://docs.basemachina.com/view/code_editor/download_dts_file/)
