---
name: bm-public-api
description: "BaseMachina の公開API（REST API）を外部システム・CI/CD・自社スクリプトから呼び出すコードを書くときの skill。アクションの実行、アクション一覧・詳細取得、環境一覧取得を HTTP で行う。`bm login` の JWT や、GitHub Actions / Google Cloud / AWS / 自社 OIDC IdP の ID Token をトークン交換した認証セットアップ、レスポンスとエラーのハンドリングを扱う。「公開API」「public API」「アクションを API で実行」「外部システムや CI から BaseMachina のアクションを呼び出す」「BaseMachina を curl で叩く」といった相談で使う。アクション定義の編集や `bm sync`（設定のコード管理）は bm-code-management、docs の仕様検索は basemachina-docs を使う。公式ドキュメント: https://docs.basemachina.com/preview/public_api/"
license: MIT
allowed-tools: "Read Grep Glob Edit Write WebSearch WebFetch"
---

# BaseMachina 公開API skill

公開APIは、ベースマキナのリソースを外部システムから操作する REST API。環境の一覧取得、アクションの一覧・詳細取得・実行を HTTP で行える。

エンドポイント・リクエスト/レスポンス形式・認証手順・エラーコードは記憶で書かず、公式ドキュメント（<https://docs.basemachina.com/preview/public_api/>）と API リファレンス（<https://docs.basemachina.com/preview/public_api/reference/>）を都度 Open して確認する。公開API は開発中の機能で、仕様が変わる可能性がある。

## いつ使うか

- 自社バックエンド・スクリプト・ツールに、ベースマキナのアクション実行を組み込むコードを書く
- CI/CD のジョブから公開API を呼び出して定型作業を自動化する
- 公開API の認証（`bm login` の JWT、または外部 OIDC のトークン交換）をセットアップする
- 公開API のレスポンスやエラーを扱うコードを書く
- 公開API の呼び出しが認証エラー等で失敗する原因を切り分ける

## いつ使わないか

- アクション定義（`defineAction` / `defineConfig`）の編集や `bm sync` での反映 → `bm-code-management`
- ベースマキナの機能・制約・仕様の一般的な質問 → `basemachina-docs`
- アクションやデータソースの設定変更（作成・編集・削除）。公開API はリソースの取得と実行のみで、設定変更は提供しない。設定変更は管理画面またはコード管理で行う

## ガードレール（最重要）

公開API のアクション実行（`executions`）には**副作用がある**。メール送信、DB 書き込み、外部サービス呼び出しなど、取り消せない操作がアクション本体で起きうる。

- エージェントは公開API を**呼び出すコードを書く**。実際の呼び出し、特に `executions` の実行はユーザーまたは CI に委ねる
- この skill の `allowed-tools` に `curl` 等の HTTP 実行ツールは含めない。動作確認はユーザーに依頼する
- コードを引き渡すときは、対象アクションを実行すると何が起きるか（副作用）を必ず添える

## ワークフロー

1. **対象アクションの確認**: 呼び出す環境とアクションを特定する。アクションは識別子またはアクションID で参照する。一部のアクション（ファイルパラメーターを持つもの等）は公開API から実行できないため、対象が該当しないかを docs で確認する
2. **認証方式の選択**: 下記「認証の選び方」で `bm login` の JWT か、外部 OIDC のトークン交換かを決める
3. **呼び出しコードの作成**: エンドポイントのメソッド・パス・クエリパラメーター・リクエスト/レスポンス構造は API リファレンスを Open して確認し、それに沿って書く
4. **エラー処理**: エラーは RFC 9457 Problem Details 形式で返り、`code` フィールドで分類される。`code` で分岐するコードにする。各 `code` の意味と HTTP ステータスは API リファレンスを参照する。`4xx` はリクエスト側の問題なのでリトライ対象にしない
5. **引き渡し**: 書いたファイルと役割、呼び出す環境ID・アクションID（識別子）・引数、`executions` を含む場合は副作用、動作確認の前提（`bm login` 済みか、OIDC 信頼ポリシー設定済みか）を構造化して返す

## 認証の選び方

公開API のエンドポイントは `Authorization: Bearer <token>` で保護されている。`Bearer` に渡せるトークンは呼び出し元によって変わる。

- **ローカル端末からの検証・開発**: `bm login` で取得した JWT を**そのまま** `Authorization: Bearer` に使える（トークン交換は不要）。`bm login` はブラウザ対話フローなのでエージェントから実行せず、未ログインならユーザーに依頼する
- **CI/CD・クラウド・自社IdP からの呼び出し**: 外部 OIDC IdP の ID Token は**そのままでは公開API に使えない**。①呼び出し元で ID Token を取得し、②トークン交換エンドポイントでベースマキナのアクセストークンに交換し、③そのアクセストークンを `Authorization: Bearer` に使う、という手順になる。交換を省いて ID Token を直接渡すと `401` になる。アクセストークンには有効期限があり、期限まで使い回して切れたら再交換する。事前にプロジェクトへのサービスアカウント割り当てと OIDC 信頼ポリシーの登録が必要で、これはエージェントの作業対象外なので未設定ならユーザーに依頼する

シナリオ別（GitHub Actions / Google Cloud / AWS / 自社IdP）の ID Token 取得手順、トークン交換エンドポイントのパス・リクエスト/レスポンス形式、OIDC 信頼ポリシーの設定値は、docs の「認証して呼び出す」を Open して確認する。

## 参照先

- 公開APIとは: <https://docs.basemachina.com/preview/public_api/>
- 認証して呼び出す: <https://docs.basemachina.com/preview/public_api/authentication/>
- API リファレンス（エンドポイント・パラメーター・レスポンス・エラーコード）: <https://docs.basemachina.com/preview/public_api/reference/>
- サービスアカウントと OIDC 信頼ポリシーの設定: <https://docs.basemachina.com/preview/service_account/>
- `bm login`: <https://docs.basemachina.com/preview/code_management/cli/login/>
