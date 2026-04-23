# `bm-code-management` evals

This directory contains the **eval cases** for the `bm-code-management` skill and a minimal **fixture bm project** used as the workspace context for each case.

## Structure

```
evals/
├── README.md                           # this file
├── grader.md                           # input / output schema + deterministic checks
├── cases/
│   ├── 01-add-sql-action.yaml          # one case per YAML file
│   ├── 02-skipDeploy-explain.yaml
│   └── ...                             # 13 total
└── fixtures/
    └── sample-project/                 # minimal bm project used as the eval workspace
        ├── basemachina.config.ts
        ├── package.json
        ├── tsconfig.json
        └── src/
            └── actions/
                ├── list-users.ts
                └── js-action-codes/
                    └── list-users.js
```

## Running evals locally (day-1 Phase 1)

Phase 1 ships **YAML schema validation only** via `.github/workflows/evals.yml`. That CI job confirms:

- Each `cases/*.yaml` has required fields (`prompt`, `expected_behavior.must`, `expected_behavior.must_not`, `grader_hints.deterministic`).
- `grader_hints.deterministic` follows the allowed operator vocabulary (`must_contain` / `must_not_contain` / `must_call_bash_matching` / `must_not_call_bash_matching`).

LLM-based execution (Claude Code headless running against each fixture) is **Phase 1.5**. The harness will integrate with `empirical-prompt-tuning` once the team decides on a runner. The schema on disk is forward-compatible so no rewrites are needed.

## A/B comparison methodology (target for Phase 1.5)

For every case, the harness runs the prompt twice against the fixture:

- **with-skill**: host agent has `bm-code-management` installed
- **without-skill**: host agent has no BaseMachina skill loaded

Both responses are scored on:

1. **Deterministic checks** (PR blocker) — substring match against `grader_hints.deterministic`. A case **must pass** these checks for the PR to merge.
2. **LLM judge** (advisory) — a separate agent scores the response against `expected_behavior.must` / `must_not`. Produces a 0-1 score and a comment, posted as a PR review comment but **does not block merge**.

This split follows Vercel's empirical finding that LLM judges are too non-deterministic to block, while targeted substring matches against known "red flag" commands (e.g. `bm sync` without `--dry-run`) are reliably detectable.

## Adding a new case

1. Copy an existing `cases/NN-*.yaml` as a starting point.
2. Fill in `prompt`, `expected_behavior`, `grader_hints.deterministic`.
3. If new fixture files are needed, add them under `fixtures/` (and reference via `prereq_fixtures`).
4. Run the CI's schema check locally: `npx ajv-cli validate -s <schema> -d skills/bm-code-management/evals/cases/<new>.yaml`.
5. Commit and open a PR; `evals.yml` will validate the YAML.

## Dogfooding → case pipeline

Internal Slack thread `p1776682725.424589` is the intake channel for code-management feedback. Post in the format:

```
[eval-case] summary / prompt / expected / actual
```

Weekly review converts high-signal items into YAML cases under `cases/`. Phase 1 is manual; Phase 2 will automate via a Slack bot (see spec §5.8).

## See also

- `grader.md` — schemas and deterministic-check vocabulary
- `.github/workflows/evals.yml` — the CI job
- `../SKILL.md` — the skill under test
