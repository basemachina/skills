---
name: basemachina-docs
description: "BaseMachina公式ドキュメントを検索して、機能仕様・設定手順・制約・トラブルシューティング・コード例を根拠付きで回答する skill。BaseMachina、ベースマキナ、アクション、ビュー、bridge、コード管理、JavaScriptアクション、@basemachina/view、@basemachina/sdk について質問されたときに使う。"
license: MIT
allowed-tools: "WebSearch WebFetch Bash(curl:*) Bash(rg:*) Read Grep Glob"
---

# BaseMachina 公式ドキュメント回答

BaseMachina の仕様・使い方・制約・コード例は記憶で断定せず、公式ドキュメント（<https://docs.basemachina.com/>）を source of truth として確認してから回答する。

## いつ使うか

- BaseMachina / ベースマキナの機能、設定、エラー、制約、移行、最新仕様について質問された
- アクション、JavaScript アクション、データソース、ビュー、bridge、コード管理、CLI、SDK、`@basemachina/view`、`@basemachina/sdk` に関する説明やコード例が必要
- 「公式 docs ではどうなっているか」「最新の仕様を確認して」など、根拠付き回答が必要

## いつ使わないか

- ユーザーが明示的に「検索しないで」「手元の情報だけで」と依頼している
- ローカル repo の実装、未公開仕様、DB、運用ログだけを根拠にすべき調査
- BaseMachina 以外の一般的な技術相談

## 調査手順

1. 質問から対象領域、機能名、API 名、UI 名、エラー文、バージョンや環境を抽出する
2. まず公式の AI 向け全文ソース `https://docs.basemachina.com/llms-full.txt` を取得して検索する
   - 例: `curl -L --fail https://docs.basemachina.com/llms-full.txt -o /tmp/basemachina-llms-full.txt`
   - 例: `rg -n -i "executeAction|createActionJob|JavaScript action" /tmp/basemachina-llms-full.txt`
3. 見つかった見出し・URL・本文近辺を読み、必要なら該当する個別公式ページも開いて確認する
4. `llms-full.txt` で足りない場合だけ、`docs.basemachina.com` に限定して追加検索する
5. 仕様が分かれる場合は、ガイド、API リファレンス、CLI リファレンス、リリースノート、トラブルシューティングなど複数の公式ページを照合する

検索・閲覧できない場合は、その制約を明示し、公式確認なしに断定しない。

## 回答方針

- 日本語で簡潔に回答し、確認した公式 URL を含める
- 公式ドキュメントで確認できた事実と、そこからの推論を分けて書く
- 公式ドキュメントに見つからない内容は「公式ドキュメントでは確認できない」と明示する
- コード例を書くときは、import 元、前提パッケージ、実行場所を docs 上の表記に合わせる
- 非公式記事、個人ブログ、Q&A、検索スニペットは公式ページへの導線としてだけ使う

## 優先ソース

- 公式ドキュメント: <https://docs.basemachina.com/>
- AI 向け全文: <https://docs.basemachina.com/llms-full.txt>
- AI 向け索引: <https://docs.basemachina.com/llms.txt>
