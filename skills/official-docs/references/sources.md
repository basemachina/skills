# 公式参照元

公式 URL を確認するときの優先ソース一覧。ここに無いサービスでも、回答前に運営元の公式ドメインを特定してから検索する。

## 優先順位

1. 公式 API リファレンス / 開発者ドキュメント
2. 公式ガイド / チュートリアル / 概念説明
3. 公式リリースノート / 変更履歴 / 移行ガイド
4. 公式 GitHub リポジトリのドキュメント / README / examples
5. 公式ヘルプセンター / サポート記事

非公式記事、個人ブログ、Q&A サイト、SNS、検索結果スニペットは根拠にしない。

## よく使う公式ドメイン

| 製品 / 組織 | 公式ドキュメント / 参照元 |
| --- | --- |
| BaseMachina | `https://docs.basemachina.com/` |
| OpenAI API | `https://platform.openai.com/docs/` |
| OpenAI Help | `https://help.openai.com/` |
| Anthropic Claude | `https://docs.claude.com/` |
| Anthropic API | `https://docs.anthropic.com/` |
| GitHub | `https://docs.github.com/` |
| GitHub CLI | `https://cli.github.com/manual/` |
| GitHub Skills spec | `https://agentskills.io/` |
| Microsoft Learn | `https://learn.microsoft.com/` |
| Google Cloud | `https://cloud.google.com/docs/` |
| AWS | `https://docs.aws.amazon.com/` |
| npm | `https://docs.npmjs.com/` |
| pnpm | `https://pnpm.io/` |
| Node.js | `https://nodejs.org/docs/` |
| TypeScript | `https://www.typescriptlang.org/docs/` |
| React | `https://react.dev/` |
| Next.js | `https://nextjs.org/docs/` |

## 検索パターン

- `site:platform.openai.com/docs file search vector stores` のように、公式ドメインに限定して検索する。
- バージョン依存の質問では、バージョン番号やリリース系列を検索語に含める。
- CLI の挙動は、ブログ内の例より公式コマンドリファレンスを優先する。
- SDK の挙動は、可能ならドキュメントと生成された API リファレンスの両方を確認する。
- 廃止予定や破壊的変更は、メインのガイドに加えて公式リリースノートと移行ガイドを検索する。
