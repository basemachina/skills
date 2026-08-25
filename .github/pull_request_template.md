## 概要

<!-- ユーザーから見た変更結果を1〜2文で説明してください。 -->

## 背景

<!-- 解決する問題と、この変更範囲が適切である理由を説明してください。 -->

## 変更内容

<!-- skill、reference、metadata、validationの変更を列挙してください。 -->

## 参照した公式ドキュメント

<!-- 仕様や互換性の変更根拠となる現在の公式ページを記載してください。 -->

## 検証

- [ ] `python3 scripts/validate-skills.py`
- [ ] `gh skill publish --dry-run`
- [ ] `claude plugin validate --strict .`

## Checklist

- [ ] 1つの明確な目的に絞られている
- [ ] skill descriptionに発火条件と対象外が明記されている
- [ ] 正規URLの現在の公式ドキュメントを参照している
- [ ] 破壊的操作やproduction変更にguardrailがある
- [ ] pluginのversionとmetadataが一致している
