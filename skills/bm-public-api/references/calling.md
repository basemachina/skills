# 公開API の呼び出しとエラーハンドリング

エンドポイントの正確なメソッド・パス・クエリパラメーター・レスポンス構造は **API リファレンスを都度 Open する**。記憶で書かない。公開API は開発中で仕様が変わりうる。

- 公開APIとは: <https://docs.basemachina.com/preview/public_api/>
- API リファレンス: <https://docs.basemachina.com/preview/public_api/reference/>

## エンドポイント

公開API が提供するのは以下のみ。設定の作成・編集・削除は提供しない。

- 環境の一覧取得（有効化されている環境のみ返る）
- アクションの一覧取得
- アクションの詳細取得
- アクションの実行

ベースURL の形は `https://platform.basemachina.com/public/v1/projects/{project_id}/environments/{environment_id}/...`。`project_id` と `environment_id` を URL パスに埋める。アクションは一覧・詳細レスポンスの `id`（識別子または自動生成のアクションID）で参照する。

## リクエスト

- POST 時は `Content-Type: application/json` を必ず付ける（他の型は `415` で弾かれる）
- アクション実行の引数はリクエストボディの `arguments` オブジェクトに入れる:

```
{
  "arguments": {
    "user_id": "usr_01H..."
  }
}
```

引数のキーは対象アクションの定義に合わせる。詳細取得エンドポイントでアクションのパラメーター定義を確認できる。

## 公開API から実行できないアクション

以下は `executions` を呼んでも実行できない。コードを書く前に対象アクションがこれに該当しないか確認する。

| 種別 | 返るコード |
| --- | --- |
| ファイルパラメーターを持つアクション | `422 argument_invalid` |
| 旧 JavaScript アクション | `422 argument_invalid` |
| 無効化されたアクション | `404 not_found` |

これらはアクション実行画面から実行する必要がある。

## エラーハンドリング

エラーは RFC 9457 Problem Details 形式（`Content-Type: application/problem+json`）で返り、`code` フィールドで分類される。`code` で分岐するコードを書く。

| `code` | HTTP | 主な原因 | 対応 |
| --- | --- | --- | --- |
| `unauthorized` | 401 | トークン欠落・期限切れ・検証失敗 | トークンを再取得（`references/authentication.md`） |
| `bad_request` | 400 | URL パスやリクエストの文法不正 | URL・リクエスト構造を見直す |
| `forbidden` | 403 | プロジェクト・アクションへの権限不足 | 権限・サービスアカウントを確認 |
| `not_found` | 404 | リソースが存在しない、または無効化済み | ID と有効化状態を確認 |
| `method_not_allowed` | 405 | 許可されていない HTTP メソッド | メソッドを確認 |
| `state_conflict` | 409 | アクションの状態不整合 | 状態を確認 |
| `payload_too_large` | 413 | リクエストボディのサイズ超過 | ボディを縮小 |
| `unsupported_media_type` | 415 | `Content-Type` が `application/json` 以外 | ヘッダーを修正 |
| `argument_invalid` | 422 | 引数・クエリのバリデーション違反、または実行不可アクションの呼び出し | 引数定義・対象アクション種別を確認 |
| `javascript_action_error` | 422 | JavaScript アクションのコードが投げた業務エラー | アクション側のエラー内容を確認 |
| `data_source_error` | 422 | データソースなど接続先のエラー | `data_source.status` に接続先 HTTP ステータスが入る場合がある |
| `internal_error` | 500 | gateway 内部の不具合 | 時間をおいて再試行 |
| `service_unavailable` | 503 | ベースマキナ側の一時障害 | `Retry-After` ヘッダーに従ってリトライ |

各 `code` の発生条件とレスポンス例は API リファレンスの各エンドポイント定義で確認する。

## リトライ

- `503 service_unavailable` は `Retry-After` ヘッダーに従ってリトライしてよい
- `4xx` はリクエスト側の問題なので、原因を直さずに再送しても同じ結果になる。リトライ対象にしない
- リトライを実装する場合、OIDC ID Token は短命なので、リトライのたびにトークンを取り直すか、リトライ全体が有効期限内に収まるようにする
