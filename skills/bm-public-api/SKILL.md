---
name: bm-public-api
description: "BaseMachinaの公開API（REST API）を外部system、CI/CD、自社scriptから呼び出すcodeを書くskill。環境・actionの一覧と詳細、action実行、review依頼の作成・状態取得・承認後実行を扱う。`bm login`のJWT、GitHub Actions・Google Cloud・AWS・自社OIDC IdPのID Token交換、response・error処理、OpenAPI client生成を実装するときに使う。action定義や`bm sync`はbm-code-management、仕様調査だけならbasemachina-docsを使う。実際のAPI呼び出しは行わない。"
license: MIT
allowed-tools: "Read Grep Glob Edit Write WebSearch WebFetch"
---

# BaseMachina 公開API

公開APIはBaseMachinaのresourceを外部systemから操作するREST API。現在のendpoint、request・response、error codeは記憶で書かず、[公式ガイド](https://docs.basemachina.com/public_api/)、[API reference](https://docs.basemachina.com/public_api/reference/)、[OpenAPI schema](https://docs.basemachina.com/openapi/public_api.yaml)を都度確認する。

## 対象

- 有効な環境の一覧取得
- actionの一覧・詳細取得
- review不要actionの実行
- review必須actionに対するreview依頼の作成・状態取得・承認後実行
- `bm login`のJWTまたは外部OIDC ID Token交換による認証
- response・error処理、OpenAPIからのclient生成

action・datasourceなどの設定作成・編集・削除は公開APIの対象外。管理画面または`bm-code-management`を使う。

## Guardrail

action実行には、mail送信、DB書き込み、外部service呼び出しなど取り消せない副作用がありうる。review依頼の作成も承認workflowや通知を開始しうる。

- APIを呼び出すcodeだけを書く。実際のrequest、特に`executions`とreview依頼作成はユーザーまたはCIに委ねる
- `allowed-tools`に`curl`などのHTTP実行toolを含めない
- 引き渡し時に対象環境・action・引数・想定される副作用を明記する
- retryを一律に実装しない。HTTP method、idempotency、副作用、現在のAPI referenceを確認して判断する

## Workflow

1. 対象project、環境、actionを特定する。actionは識別子またはaction IDで参照する
2. [公開APIから実行できないaction](https://docs.basemachina.com/public_api/#%E5%85%AC%E9%96%8Bapi%E3%81%8B%E3%82%89%E5%AE%9F%E8%A1%8C%E3%81%A7%E3%81%8D%E3%81%AA%E3%81%84%E3%82%A2%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%B3)に該当しないか確認する
3. local検証なら`bm login`のJWT、CI・cloudなら外部OIDC ID Token交換を選ぶ
4. method、path、query、request・response schemaをOpenAPIで確認してcodeを書く
5. review不要actionはexecution endpointを使う。review必須actionは直接実行すると`403 forbidden`になるため、review依頼を作成し、状態を取得して、承認済みかつ自動実行されていない場合にreview依頼のexecution endpointを使う
6. `auto_execute_on_approval`を指定する場合は、承認後に誰が実行する設計かを明確にし、二重実行を避ける
7. 通常endpointのRFC 9457 Problem Detailsと、`/token`のOAuth error responseを分けて処理する
8. 変更file、endpoint、環境・action ID、引数、副作用、認証前提、ユーザーまたはCIへ残した動作確認を報告する

## 認証

`/token`以外のendpointは`Authorization: Bearer <token>`で保護される。

- **local開発**: `bm login`で取得したJWTをそのままBearer tokenに使う。browser対話flowは自動化せず、未loginならユーザーに依頼する
- **CI/CD・cloud・自社IdP**: 外部OIDC ID Tokenをそのまま送らず、`/token`でBaseMachina access tokenへ交換する。事前にprojectへのservice account割り当てとOIDC trust policyが必要

ID Token取得、token交換のrequest・response、Issuer・Audience・Bound Claimsは[認証ガイド](https://docs.basemachina.com/public_api/authentication/)と[service account](https://docs.basemachina.com/service_account/)で確認する。access tokenは`expires_in`まで再利用し、期限切れ後に再交換する。

## 主なsource

- [公開APIとは](https://docs.basemachina.com/public_api/)
- [認証して呼び出す](https://docs.basemachina.com/public_api/authentication/)
- [API reference](https://docs.basemachina.com/public_api/reference/)
- [OpenAPI schema](https://docs.basemachina.com/openapi/public_api.yaml)
- [service accountとOIDC trust policy](https://docs.basemachina.com/service_account/)
- [`bm login`](https://docs.basemachina.com/code_management/cli/login/)
