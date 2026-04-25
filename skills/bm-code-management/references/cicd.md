# GitHub Actions / OIDC / 環境別反映

GitHub Actions による BaseMachina コード管理の運用構築・改修ガイド。

- 公式ドキュメント（CI/CD）: <https://docs.basemachina.com/preview/code_management/ci_cd/>
- 2 ブランチ運用: <https://docs.basemachina.com/preview/code_management/examples/two_branch/>
- 3 ブランチ運用: <https://docs.basemachina.com/preview/code_management/examples/three_branch/>
- `bm sync` CLI: <https://docs.basemachina.com/preview/code_management/cli/sync/>
- 環境設定: <https://docs.basemachina.com/admin/environment/what_is_environment/>

**workflow YAML の完全形・OIDC の手順詳細は docs を都度参照**し、本ファイルにはエージェント特有のガードレールと意思決定ポイントだけを書く。

## 重要なガードレール（IMPORTANT）

1. **エージェントはローカルから `bm sync`（`--dry` なし）を実行しない**。実反映は CI 経由か、ユーザーが手動で実行する。SKILL.md の `allowed-tools` でも `bm sync --dry:*` のみ許可している
2. **環境 ID を伴う sync を workflow に書く前に、対象環境（特に `prd`）と影響範囲をユーザーに確認する**。マージ時に発火するため PR 経由の事故が起きやすい
3. **OIDC の `Audience` は basemachina 側の信頼ポリシー設定と完全一致させる**。`core.getIDToken("https://basemachina.com")` で発行する文字列を CI と basemachina 管理画面の双方で揃える
4. **既存 workflow を改修する場合、もとの runner permission・branch trigger を変えない**。安易に絞ると CI 失敗、緩めると本番への意図しない反映を招く
5. **エージェントから本番反映の workflow を `gh workflow run` でトリガーしない**。発火条件はあくまで PR マージに委ねる

## ワークフロー

1. **運用パターン選択**: 2 ブランチ（`main` = 開発, `prd` = 本番）または 3 ブランチ（`main` / `stg` / `prd`）のどちらかをユーザーに確認する。全体像は公式ドキュメント（two_branch / three_branch）を Open して確認する
2. **既存資産の把握**: `.github/workflows/` を Glob して既存 workflow を Read する。basemachina の OIDC 信頼ポリシーがすでに設定されているかをユーザーに確認する（CI 側だけ書いても通らない）
3. **workflow ファイル作成・編集**:
   - 公式ドキュメントの手順（`id-token: write` などの permission、Node.js 20、`actions/github-script@v7` での `BM_OIDC_TOKEN` 取得、`npx bm sync --dry` / `npx bm sync` の使い分け）に沿って書く
   - 環境別ジョブ（`sync-dev.yml` / `sync-stg.yml` / `sync-prd.yml` 等）の分割は運用パターンに合わせる
   - PR トリガー: `bm sync --dry`、push（マージ）トリガー: `bm sync [<env-id>] [--from <src-env-id>]`
4. **検証**: workflow 構文の確認は `gh workflow view` などで行う。実際の実反映 workflow をエージェントから手動実行しない
5. **引き渡し**: 作成 / 変更した workflow ファイル一覧、必要なリポジトリ secrets / variables、basemachina 管理画面側で確認すべき項目（OIDC 信頼ポリシーの Audience, environment ID）を構造化して返す

## OIDC セットアップ確認チェックリスト

公式ドキュメント（<https://docs.basemachina.com/preview/code_management/ci_cd/>）の手順に従いつつ、以下を**すべて**確認する。

- [ ] workflow の `permissions` に `id-token: write` がある
- [ ] PR にコメントを返す step があるなら `pull-requests: write` がある
- [ ] `core.getIDToken(<audience>)` の `<audience>` と basemachina 側の信頼ポリシーの Audience が一致している
- [ ] basemachina 側に GitHub Actions の OIDC 信頼ポリシーが登録済み（リポジトリ・ブランチ条件含む）
- [ ] 環境変数名は `BM_OIDC_TOKEN`（ローカルの `~/.basemachina/credentials.json` より優先される）

## 環境別 sync の書き方

詳細とフラグ仕様は <https://docs.basemachina.com/preview/code_management/cli/sync/> を都度参照する。要点だけ:

- 開発環境（デフォルト）: `npx bm sync` / 差分確認は `npx bm sync --dry`
- 検証・本番環境: `npx bm sync <env-id>` / 差分確認は `npx bm sync --dry <env-id>`
- 上流環境からの同期（3 ブランチ運用の `stg` → `prd`）: `npx bm sync <prd-env-id> --from <stg-env-id>`

`<env-id>` は basemachina 管理画面の environment 設定から取得する。スキルが記憶している既知 ID は無いので、ユーザーまたは管理画面から都度取得する。

## 認証エラーの切り分け

CI で `authentication required` 系の失敗が出たら以下を順に確認する。

1. workflow に `id-token: write` permission があるか
2. `core.getIDToken(<audience>)` の audience が basemachina 側設定と一致しているか
3. basemachina 側 OIDC 信頼ポリシーの「対象リポジトリ」「対象ブランチ / 環境」条件が、今走っているジョブと整合しているか
4. `BM_OIDC_TOKEN` が export されているか（step 順序ミス）

ローカル実行時の認証切れは SKILL.md § 認証 の手順に従う。
