---
name: bm-public-api
description: "BaseMachina の公開API（REST API）を外部システム・CI/CD・自社スクリプトから呼び出すコードを書くときの skill。アクションの実行、アクション一覧・詳細取得、環境一覧取得を HTTP で行う。`bm login` の JWT や GitHub Actions / Google Cloud / AWS / 自社 OIDC IdP の ID Token を使った認証セットアップ、OIDC 信頼ポリシーの設定値、RFC 9457 形式のエラーハンドリングを扱う。「公開API」「public API」「アクションを API で実行」「外部システムや CI から BaseMachina のアクションを呼び出す」「BaseMachina を curl で叩く」といった相談で使う。アクション定義の編集や `bm sync`（設定のコード管理）は bm-code-management、docs の仕様検索は basemachina-docs を使う。公式ドキュメント: https://docs.basemachina.com/preview/public_api/"
license: MIT
allowed-tools: "Read Grep Glob Edit Write WebSearch WebFetch"
---

# BaseMachina 公開API skill

公開APIは、ベースマキナのリソースを外部システムから操作する REST API。環境の一覧取得、アクションの一覧・詳細取得・実行を HTTP で行える。

エンドポイント・パラメーター・レスポンス・トークンの取得手順は記憶で書かず、公式ドキュメント（<https://docs.basemachina.com/preview/public_api/>）と API リファレンス（<https://docs.basemachina.com/preview/public_api/reference/>）を都度確認する。公開APIは開発中の機能で、仕様が変わる可能性がある。

## いつ使うか

- 自社バックエンド・スクリプト・ツールに、ベースマキナのアクション実行を組み込むコードを書く
- CI/CD のジョブから公開API を呼び出して定型作業を自動化する
- 公開API の認証（`bm login` の JWT、または外部 OIDC ID Token）をセットアップする
- 公開API のレスポンスやエラー（RFC 9457 形式）を扱うコードを書く
- 公開API の呼び出しが `401` / `403` / `422` などで失敗する原因を切り分ける

## いつ使わないか

- アクション定義（`defineAction` / `defineConfig`）の編集や `bm sync` での反映 → `bm-code-management`
- ベースマキナの機能・制約・仕様の一般的な質問 → `basemachina-docs`
- アクションやデータソースの設定変更（作成・編集・削除）。公開API はこれらを提供しない。設定変更は管理画面またはコード管理で行う

## ガードレール（最重要）

公開API の **アクション実行（`executions` エンドポイント）には副作用がある**。メール送信、DB 書き込み、外部サービス呼び出しなど、取り消せない操作がアクション本体で起きうる。

- エージェントは公開API を**呼び出すコードを書く**。実際の呼び出し、特に `executions` の実行はユーザーまたは CI に委ねる
- この skill の `allowed-tools` に `curl` 等の HTTP 実行ツールは含めない。動作確認はユーザーに依頼し、対象の環境ID・アクションID・引数を明示して引き渡す
- コードを引き渡すときは「このアクションを実行すると何が起きるか（副作用）」を必ず添える

## 領域選択（navigation）

ユーザーの作業内容に応じて、以下の reference を**必要なものだけ**読み込む。

| 作業 | 読むべき reference |
| --- | --- |
| トークンの取得方法、OIDC 信頼ポリシーの設定、`401` 認証エラーの切り分け | [`references/authentication.md`](references/authentication.md) |
| エンドポイントの選択、リクエスト/レスポンスの組み立て、エラーコードの分岐、リトライ | [`references/calling.md`](references/calling.md) |

認証コードと呼び出しコードの両方を書く場合は、両方を順次 Read する。

## 共通: エンドポイントとベースURL

- ベースURL の形は `https://platform.basemachina.com/public/v1/projects/{project_id}/environments/{environment_id}/...`
- 提供操作は **環境の一覧取得** と、アクションの **一覧取得・詳細取得・実行** のみ
- アクションは **識別子、またはアクションID** で参照する。一覧・詳細レスポンスの `id` を、実行時の `action_id` にそのまま使う
- 正確なメソッド・パス・クエリパラメーター・レスポンス構造は API リファレンス（<https://docs.basemachina.com/preview/public_api/reference/>）を Open して確認する

## 共通: 認証シナリオ

公開API は `Authorization: Bearer <token>` で保護されている。呼び出し元に応じてトークンの種類が変わる。

| 呼び出し元 | 使うトークン |
| --- | --- |
| ローカル端末からの検証・開発 | `bm login` で取得した JWT |
| GitHub Actions など CI/CD | CI が発行する外部 OIDC ID Token |
| Google Cloud / AWS 上のワークロード | メタデータサーバー / IAM が発行する OIDC ID Token |
| 自社 IdP（Auth0 / Okta / Kubernetes など）配下 | その IdP の OIDC ID Token |

シナリオ別の取得手順と OIDC 信頼ポリシーの設定値は [`references/authentication.md`](references/authentication.md) を読む。

## 共通: 引き渡し

コードを書き終えたら、以下を構造化してユーザーに返す。

- 書いたファイルと、それが担う処理（認証 / 呼び出し / エラー処理）
- 呼び出す環境ID・アクションID（または識別子）・引数
- `executions` を含む場合、そのアクションの副作用と「実行はユーザー/CI に委ねる」旨
- 動作確認に必要な前提（`bm login` 済みか、OIDC 信頼ポリシー設定済みか）

## 参照先

- 公開APIとは: <https://docs.basemachina.com/preview/public_api/>
- 認証して呼び出す: <https://docs.basemachina.com/preview/public_api/authentication/>
- API リファレンス: <https://docs.basemachina.com/preview/public_api/reference/>
- OIDC 信頼ポリシーの設定: <https://docs.basemachina.com/preview/code_management/getting_started/>
- `bm login`: <https://docs.basemachina.com/preview/code_management/cli/login/>
