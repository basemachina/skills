---
name: basemachina-docs
description: "現在のBaseMachina公式ドキュメントを調査し、根拠付きで回答するskill。機能、設定、エラー、制約、移行、アクション、ビュー、Bridge、コード管理、JavaScriptアクション、公開API、OpenAPI、Remote MCP、OAuth/OIDC、サービスアカウント、レビュー依頼、CLI、SDKについて公式仕様の確認が必要なときに使う。"
license: MIT
allowed-tools: "WebSearch WebFetch Bash(curl:*) Bash(rg:*) Read Grep Glob"
---

# BaseMachina 公式ドキュメント調査

現在の [BaseMachina 公式ドキュメント](https://docs.basemachina.com/) を source of truth とする。変更されうる仕様を記憶だけで断定しない。

## 調査手順

1. 質問から対象領域、機能名・API 名、エラー文、環境、version を抽出する
2. `https://docs.basemachina.com/llms-full.txt` を一時ファイルへ取得し、`rg` で関連箇所を探す
3. 該当する正規 URL の個別ページを直接開き、必要な節を読む。検索キャッシュと現在のページが異なる場合は現在のページを採用する
4. 公開API の質問ではガイドと現在の OpenAPI schema の両方を確認する
5. guide、reference、troubleshooting、release note に仕様が分かれる場合は複数の公式ページを照合する
6. 現在利用できる仕様と preview・今後追加予定の仕様を区別し、docs にない実装詳細を推測しない

検索例:

```bash
docs_cache="$(mktemp -t basemachina-llms-full.XXXXXX)"
curl -L --fail https://docs.basemachina.com/llms-full.txt -o "$docs_cache"
rg -n -i "public api|remote mcp|defineView|bm pull" "$docs_cache"
```

公式 source を取得できない場合はその制約を明示し、未確認情報を現行仕様として断定しない。

## 回答方針

- ユーザーが指定した言語で簡潔に回答し、確認した公式 URL を含める
- docs で確認できた事実と推論を分ける
- docs に見つからない内容は、その旨を明示する
- コード例は import 元、前提 package、実行場所、認証方式を docs の表記に合わせる
- 非公式記事や検索 snippet は公式ページを探す導線としてのみ使う

## 優先 source

- [BaseMachina 公式ドキュメント](https://docs.basemachina.com/)
- [AI 向け全文](https://docs.basemachina.com/llms-full.txt)
- [コード管理](https://docs.basemachina.com/code_management/)
- [公開API](https://docs.basemachina.com/public_api/)
- [公開API OpenAPI schema](https://docs.basemachina.com/openapi/public_api.yaml)
- [Remote MCP](https://docs.basemachina.com/remote_mcp/)
