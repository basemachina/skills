# ビューコード・コード取得設定連携

コードエディターのビューコードを、コード管理 repo に同居させる作業のガイド。

ビューの設定はコード管理の直接対象外。ビュー内コードだけを repo で管理し、コード取得設定を有効化したビューがアクション経由で取得する、という運用として扱う。

## 参照先

- ビューコードの Git 管理: <https://docs.basemachina.com/view/code_editor/git_management/>
- コード取得設定との連携: <https://docs.basemachina.com/preview/code_management/examples/view_code_fetch/>
- 設定ファイル: <https://docs.basemachina.com/preview/code_management/configuration/>
- CI/CD: <https://docs.basemachina.com/preview/code_management/ci_cd/>
- `@basemachina/view` 型定義: <https://docs.basemachina.com/view/code_editor/download_dts_file/>

## ワークフロー

1. **境界確認**: 依頼がビュー設定の変更なのか、repo 内のビューコード変更なのかを切り分ける。ビュー設定そのものは BaseMachina UI 側の管理対象として扱う
2. **既存構成確認**: `views/`、build script、ストレージアップロード workflow、コード取得用アクションの有無を確認する。無ければ公式 docs の構成例を参照して、必要最小の追加にする
3. **型設定確認**: `.tsx` を扱う場合は `tsconfig.json` の `jsx: "react-jsx"`、`views/**/*.tsx` 相当の include、`react` / `@types/react` のインストール状態を確認する
4. **取得経路確認**: GCS / S3 / GitHub API などの取得元はプロジェクト既存の運用を優先する。未決定なら docs の選択肢を示してユーザーに確認する
5. **検査**: 検出した PM の TypeScript チェックと、必要なら view build script を実行する。`bm sync --dry` はコード取得用アクションなど BaseMachina 設定側の差分確認に使う

## CI/CD の扱い

PR では `bm sync --dry` による差分確認、マージ後や環境デプロイでは CI が `bm sync` / `bm sync <環境ID>` とビューコードの build・アップロードを担う前提で説明する。エージェントから本番反映やストレージアップロードを実行しない。
