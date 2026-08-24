---
name: bm-code-management
description: "BaseMachinaのコード管理repoを編集・レビューするskill。`defineAction`、`defineView`、`defineConfig`のTypeScript設定、`readFile`で読み込むJavaScriptアクション・ビューコード、`bm pull`によるWeb UIからの取り込み、型チェック、安全な`bm sync --dry` previewを扱う。アクション実行や`--dry`なしの環境変更には使わない。"
license: MIT
allowed-tools: "Bash(bm sync --dry:*) Bash(bm --help:*) Bash(bm --version) Bash(npx tsc:*) Bash(yarn tsc:*) Bash(pnpm exec tsc:*) Bash(bunx tsc:*) Bash(npm i:*) Bash(yarn add:*) Bash(pnpm add:*) Bash(bun add:*) Bash(npm outdated:*) Bash(yarn outdated:*) Bash(pnpm outdated:*) Bash(bun outdated:*) Read Grep Glob Edit Write"
---

# BaseMachina コード管理

コマンド、flag、設定 field は [コード管理の公式ドキュメント](https://docs.basemachina.com/code_management/) とインストール済み SDK の型定義で確認する。変更されうる詳細を記憶だけで書かない。

## 作業領域を選ぶ

依頼に必要な reference だけを読む。

| 作業 | reference |
| --- | --- |
| `basemachina.config.ts`、`defineAction`、`defineView`、`defineConfig`の編集、ID変更、`bm pull`・`bm sync`の確認 | [`references/ts-config.md`](references/ts-config.md) |
| `executeAction`、`createActionJob`、`wait`、`ResultError`などを使うJavaScriptアクションコードの編集 | [`references/js-action.md`](references/js-action.md) |
| コードエディター・ビジュアルエディターのビュー、外部から取得するビューコードの編集 | [`references/view-code.md`](references/view-code.md) |

複数領域にまたがる変更では、該当するreferenceをすべて読む。

## Pre-flight

1. `basemachina.config.ts`を探す。カレントディレクトリにない場合は`--config <path>`を使うかproject rootへ移動する
2. `package.json#packageManager`、次にlockfileからpackage managerを1つに決める。情報が食い違う場合はユーザーに確認する
3. `@basemachina/sdk`と`@basemachina/cli`を確認する。JavaScriptアクションでは`@basemachina/action`、ビューでは`@basemachina/view`、`react`、`@types/react`、JSX設定も確認する
4. 設定 field の追加・変更前にインストール済みSDKの型を読む
5. dependencyの追加・更新は事前にユーザーへ確認する

## Package managerコマンド

| 操作 | npm | Yarn | pnpm | Bun |
| --- | --- | --- | --- | --- |
| dev dependency追加 | `npm i -D <pkg>` | `yarn add -D <pkg>` | `pnpm add -D <pkg>` | `bun add -d <pkg>` |
| dependency更新 | `npm i <pkg>@latest` | `yarn add <pkg>@latest` | `pnpm add <pkg>@latest` | `bun add <pkg>@latest` |
| dev dependency更新 | `npm i -D <pkg>@latest` | `yarn add -D <pkg>@latest` | `pnpm add -D <pkg>@latest` | `bun add -d <pkg>@latest` |
| 更新確認 | `npm outdated <pkg>` | `yarn outdated <pkg>` | `pnpm outdated <pkg>` | `bun outdated <pkg>` |
| TypeScript実行 | `npx tsc` | `yarn tsc` | `pnpm exec tsc` | `bunx tsc` |

Yarn Berryには同等の標準`outdated` workflowがない。利用中のrepoでは別のpackage managerへ切り替えず、更新確認をskipしたことを報告する。

## Guardrail

- `bm sync`は必ず`--dry`を付ける。development・staging・productionを問わず、非dry-run syncを実行しない
- disableの確認には`bm sync --dry --with-disable`を使う。`--with-disable`なしでは、configから消えたaction・viewは変更されない
- 環境間previewでは`--dry`を維持し、target、`--from`、`--with-disable`、`--pin-version`をユーザーと確認する
- JavaScriptアクション・ビューのsourceは`git diff`でも確認する。dry-runではcode本文の差分が省略されることがある
- 実反映はreview済みCIまたはユーザーの明示操作に委ねる
- testを含め、BaseMachina actionを実行しない

詳細は[`bm sync`](https://docs.basemachina.com/code_management/cli/sync/)と[CI/CD](https://docs.basemachina.com/code_management/ci_cd/)を確認する。

## `bm pull`

- configにまだないWeb管理action・viewを取り込む
- action定義は`src/actions/`、view定義は`src/views/`、code本文は各生成directoryに作成され、config、`src/bm-refs.ts`、`type.d.ts`も更新される
- action・view定義とcode本文は新規作成のみ。既存definitionへ後続のWeb UI変更を上書きしない
- コード取得設定が有効なコードエディターviewは対象外で、Web UIと外部code取得workflowで管理を続ける
- 書き込み前に対話確認がある。実行前にユーザーへ確認し、生成ファイルをすべてreviewする

詳細は[`bm pull`](https://docs.basemachina.com/code_management/cli/pull/)を確認する。

## 認証

local dry-runまたはpullで認証を求められた場合は、ユーザーに`bm login`の実行を依頼する。browserを使う対話flowは自動化しない。CIではlocal credentialをコピーせず、公式のOIDC・service account手順に従う。

## 引き渡し

以下を報告する。

- 変更file
- 影響するaction・view ID
- validation commandと結果
- dry-run summary
- disable、ID変更、同期元環境、version pinの意図
- CIまたはユーザーへ残した実反映手順

## 主なsource

- [コード管理](https://docs.basemachina.com/code_management/)
- [設定ファイル](https://docs.basemachina.com/code_management/configuration/)
- [`defineAction`](https://docs.basemachina.com/code_management/sdk/define_action/)
- [`defineView`](https://docs.basemachina.com/code_management/sdk/define_view/)
- [`defineConfig`](https://docs.basemachina.com/code_management/sdk/define_config/)
- [`readFile`](https://docs.basemachina.com/code_management/sdk/read_file/)
- [`bm pull`](https://docs.basemachina.com/code_management/cli/pull/)
- [`bm sync`](https://docs.basemachina.com/code_management/cli/sync/)
- [CI/CD](https://docs.basemachina.com/code_management/ci_cd/)
- SDK型定義: `node_modules/@basemachina/sdk/dist/oac/index.d.ts`
- JavaScript action runtime型: `node_modules/@basemachina/action/dist/*.d.ts`
