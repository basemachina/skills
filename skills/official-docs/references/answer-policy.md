# Answer Policy

Use this policy after opening the relevant official pages.

## Required Behavior

- Answer from official pages that were actually opened and read in the current turn.
- Include the official URL or URLs used as sources.
- Keep quotations short. Prefer paraphrase plus a link.
- Separate confirmed facts from inference when the docs do not state something directly.
- If no official source confirms the answer, say so clearly instead of guessing.

## Handling Missing or Conflicting Docs

- If official docs are silent, answer: "公式 docs では確認できませんでした" and explain what was checked.
- If official pages conflict, prefer in this order:
  1. Current API reference or CLI reference
  2. Current product guide
  3. Release notes / migration guide for the relevant version
  4. Official GitHub repository docs
  5. Help center article
- Mention the conflict briefly and identify the source being treated as authoritative.

## Freshness

- For "latest", "current", "today", pricing, model lists, limits, compatibility, deprecations, and release status, always perform a fresh official lookup.
- Include exact dates when the user uses relative dates or when the docs provide release dates.
- If the official page has no visible update date, avoid claiming when it changed.

## Response Shape

- Start with the direct answer.
- Add only the details needed for the user's decision or next action.
- End with a short "Sources" list when multiple official pages were used.
- Do not cite non-official pages as evidence.
