---
name: bm-cicd-setup
description: "BaseMachina コード管理を GitHub Actions に組み込むときの skill。OIDC 認証セットアップ、`bm sync --dry`（PR 時）と `bm sync`（マージ時の環境反映）の使い分け、2 ブランチ / 3 ブランチ運用パターンの選定、`<env-id>` 指定や `--from` フラグの取り扱いをガイドする。`defineAction` / `defineConfig` の編集は `bm-code-management` skill、JS アクションのコード本体は `bm-js-action` skill に委譲する。公式ドキュメント: https://docs.basemachina.com/preview/code_management/ci_cd/"
allowed-tools: "Bash(bm sync --dry:*) Bash(bm --help:*) Bash(bm --version) Bash(gh workflow:*) Bash(gh run list:*) Bash(gh secret list:*) Read Grep Glob Edit Write"
---

# BaseMachina CI/CD セットアップ skill

GitHub Actions による BaseMachina コード管理の運用を構築・改修する skill。**workflow YAML の完全形・OIDC の手順詳細は docs を都度参照**し、skill 側にはエージェント特有のガードレールと意思決定ポイントだけを置く。

- 公式ドキュメント（CI/CD）: <https://docs.basemachina.com/preview/code_management/ci_cd/>
- 2 ブランチ運用: <https://docs.basemachina.com/preview/code_management/examples/two_branch/>
- 3 ブランチ運用: <https://docs.basemachina.com/preview/code_management/examples/three_branch/>
- `bm sync` CLI: <https://docs.basemachina.com/preview/code_management/cli/sync/>

## いつ使うか

- BaseMachina コード管理用の GitHub Actions workflow を**新規作成**する
- 既存 workflow に**環境追加**（stg / prd など）する
- OIDC 認証エラーや CI 上の `bm sync` 失敗を**復旧**する

## いつ使わないか

- `defineAction` / `defineConfig` の TS 設定編集や `bm sync --dry` をローカルで叩いて差分を見る → `bm-code-management`
- JS アクションのコード本体 `./js-action-codes/*.ts` の編集 → `bm-js-action`

## 重要なガードレール（IMPORTANT）

1. **エージェントはローカルから `bm sync`（`--dry` なし）を実行しない**。実反映は CI 経由か、ユーザーが手動で実行する。`allowed-tools` でも `bm sync --dry:*` のみを許可している
2. **環境 ID を伴う sync を workflow に書く前に、対象環境（特に `prd`）と影響範囲をユーザーに確認する**。書き換えはマージ時に発火するため、PR 経由の事故が起きやすい
3. **OIDC の `Audience` は basemachina 側の信頼ポリシー設定と完全一致させる**。`core.getIDToken("https://basemachina.com")` で発行する文字列を CI と basemachina 管理画面の双方で揃える
4. **既存 workflow を改修する場合は、もとの runner permission・branch trigger を変えない**。安易に絞ると CI 失敗、緩めると本番への意図しない反映を招く

## ワークフロー

1. **運用パターン選択**
   - 2 ブランチ（`main` = 開発, `prd` = 本番）または 3 ブランチ（`main` / `stg` / `prd`）のどちらかをユーザーに確認する
   - パターンの全体像は <https://docs.basemachina.com/preview/code_management/examples/two_branch/> または <https://docs.basemachina.com/preview/code_management/examples/three_branch/> を Open して確認する
2. **既存資産の把握**
   - `.github/workflows/` を Glob して既存 workflow を Read する
   - basemachina の OIDC 信頼ポリシーがすでに設定されているかをユーザーに確認する（CI 側だけ書いても通らない）
3. **workflow ファイル作成・編集**
   - 公式ドキュメントの手順（`id-token: write` などの permission、Node.js 20、`actions/github-script@v7` での `BM_OIDC_TOKEN` 取得、`npx bm sync --dry` / `npx bm sync` の使い分け）に沿って書く
   - 環境別ジョブ（`sync-dev.yml` / `sync-stg.yml` / `sync-prd.yml` 等）の分割は運用パターンに合わせる
   - PR トリガー: `bm sync --dry`、push（マージ）トリガー: `bm sync [<env-id>] [--from <src-env-id>]` を使う
4. **検証**
   - workflow 構文の文法的な確認は `gh workflow view` などで行う
   - **エージェントから本番反映の workflow を `gh workflow run` でトリガーしない**。発火条件はあくまで PR マージに委ねる
5. **引き渡し**
   - 作成 / 変更した workflow ファイル一覧、必要なリポジトリ secrets / variables、basemachina 管理画面側で確認すべき項目（OIDC 信頼ポリシーの Audience, environment ID）を構造化して返す

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

`<env-id>` は basemachina 管理画面の environment 設定から取得する。skill が記憶している既知 ID は無いので、ユーザーまたは管理画面から都度取得する。

## 認証エラーの切り分け

CI で `authentication required` 系の失敗が出たら以下を順に確認する。

1. workflow に `id-token: write` permission があるか
2. `core.getIDToken(<audience>)` の audience が basemachina 側設定と一致しているか
3. basemachina 側 OIDC 信頼ポリシーの「対象リポジトリ」「対象ブランチ / 環境」条件が、今走っているジョブと整合しているか
4. `BM_OIDC_TOKEN` が export されているか（step 順序ミス）

ローカル実行時の `authentication required` は `bm login`（ブラウザ起動の interactive フロー）で復旧する。エージェントから `bm login` は実行しない。

## 参照先

- CI/CD 総覧: <https://docs.basemachina.com/preview/code_management/ci_cd/>
- 2 ブランチ運用: <https://docs.basemachina.com/preview/code_management/examples/two_branch/>
- 3 ブランチ運用: <https://docs.basemachina.com/preview/code_management/examples/three_branch/>
- `bm sync` CLI: <https://docs.basemachina.com/preview/code_management/cli/sync/>
- 環境設定: <https://docs.basemachina.com/admin/environment/what_is_environment/>
- 関連 skill: `bm-code-management`（TS 設定 + bm sync --dry） / `bm-js-action`（JS アクションのコード本体）
