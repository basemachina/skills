# 公開API の認証セットアップ

公開API へのリクエストには `Authorization: Bearer <token>` を付ける。トークンの取得手順・OIDC 信頼ポリシーの設定値・サンプルコードは**公式ドキュメントを都度 Open する**。記憶で書かない。

- 認証して呼び出す: <https://docs.basemachina.com/preview/public_api/authentication/>
- OIDC 信頼ポリシーの設定: <https://docs.basemachina.com/preview/code_management/getting_started/>
- `bm login`: <https://docs.basemachina.com/preview/code_management/cli/login/>

## トークンの 2 系統

- **`bm login` で取得した JWT**: 公開API がそのまま受け付ける。ブラウザでログインしたユーザーの権限で実行される
- **外部 OIDC IdP が発行した ID Token**: 公開API が検証し、内部でサービスアカウント JWT に交換する。サービスアカウントの権限で実行される

外部 OIDC を使う場合、IdP が `/.well-known/openid-configuration` を公開し、ID Token が信頼ポリシーの `Issuer` / `Audience` / `Bound Claims` を満たせば認証が通る。呼び出し元のサービスは特定の種類に限定されない。

## シナリオ別の取得方法

ユーザーの呼び出し元を確認し、該当シナリオの手順を docs で確認してからコードを書く。

| 呼び出し元 | トークン取得手段 | 注意点 |
| --- | --- | --- |
| ローカル端末 | `bm login` → `~/.basemachina/credentials.json` の `token` | 検証・開発向け。`bm login` はブラウザ対話フローなのでエージェントから実行しない |
| GitHub Actions | `actions/github-script` + `@actions/core` の `getIDToken(audience)` | コード管理の `bm sync` と違い、公式の `bm-action` は使わない。`permissions: id-token: write` が要る |
| Google Cloud（Cloud Run / GKE / GCE / Cloud Functions） | `google-auth-library` の `getIdTokenClient(audience)` | メタデータサーバー経由。サービスアカウント鍵をアプリに置かない |
| AWS（EC2 / Lambda / ECS） | AWS IAM Outbound Identity Federation、`sts:GetWebIdentityToken` | IAM ロールに `sts:GetWebIdentityToken` の許可が要る。Issuer はアカウント固有 URL |
| 自社 OIDC IdP（Auth0 / Okta / Keycloak / Kubernetes など） | 各 IdP の ID Token 発行機能 | `/.well-known/openid-configuration` と JWKS が HTTPS 公開され、`iss` / `aud` / 信頼ポリシー用 claim を含むこと |

## OIDC 信頼ポリシー

外部 OIDC ID Token を使う場合、事前に以下が必要。

- プロジェクトにサービスアカウントが作成・割り当て済み
- 呼び出し元の IdP に合わせた OIDC 信頼ポリシーが登録済み

信頼ポリシーは `Issuer` / `Audience` / `Bound Claims` の 3 項目で構成される。設定はプロジェクト設定の「コード管理」セクションで行う（コード管理機能を使わない場合も同じ場所）。各シナリオの設定値は docs の表を参照する。設定自体はエージェントの作業対象外なので、未設定ならユーザーに設定を依頼する。

## トークンの寿命

- `bm login` の JWT は `credentials.json` の `expiresAt` で期限を持つ。期限切れは公開API が `401 unauthorized` を返す。再度 `bm login` で上書き取得する
- 外部 OIDC ID Token の有効期限は IdP に依存する（GitHub Actions は短命、Google Cloud / AWS は 1 時間程度）。公開API はリクエストごとにトークンを検証・交換するため、リクエストごとに新しい ID Token を取得するコードにする

## `401` の切り分け

公開API が `401 unauthorized` を返すときの典型原因:

- トークンの欠落（`Authorization` ヘッダー未付与）
- トークンの期限切れ（`bm login` JWT なら再ログイン、OIDC なら再取得）
- OIDC ID Token の検証失敗（信頼ポリシーの `Issuer` / `Audience` / `Bound Claims` と ID Token の claim が不一致）

権限不足は `401` ではなく `403 forbidden` で返る。両者を取り違えないこと。
