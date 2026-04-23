#!/usr/bin/env bash
# build-agents-md.sh — Phase 1 stub
#
# Planned behavior (Phase 2):
#   Extract the Anti-Patterns table from each skill's SKILL.md between
#   `<!-- build-agents-md:anti-patterns -->` and `<!-- /build-agents-md:anti-patterns -->`
#   markers and regenerate the corresponding section in `templates/AGENTS.md`.
#
#   This keeps the SKILL.md (full form) and templates/AGENTS.md (compact form) in sync
#   automatically, eliminating the drift that Phase 1 handles via manual review.
#
# Phase 1 scope:
#   This script is a stub. Run it to confirm the markers exist in each SKILL.md;
#   actual regeneration is deferred until we have >1 skill and measurable drift.
#
# Usage:
#   ./scripts/build-agents-md.sh           # report marker status for every skill
#   ./scripts/build-agents-md.sh <slug>    # limit to one skill (still stub output)

set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
target_slug="${1:-}"

echo "build-agents-md.sh (Phase 1 stub)"
echo "root: $ROOT"
echo

found=0
missing=0
while IFS= read -r -d '' skill_md; do
  skill_dir=$(dirname "$skill_md")
  slug=$(basename "$skill_dir")
  if [ -n "$target_slug" ] && [ "$slug" != "$target_slug" ]; then
    continue
  fi
  if grep -q '<!-- build-agents-md:anti-patterns -->' "$skill_md" &&
     grep -q '<!-- /build-agents-md:anti-patterns -->' "$skill_md"; then
    echo "✓ $slug: markers present in SKILL.md"
    found=$((found + 1))
  else
    echo "✗ $slug: marker(s) missing in SKILL.md"
    missing=$((missing + 1))
  fi
done < <(find "$ROOT/skills" -name SKILL.md -print0)

echo
echo "result: $found skill(s) with markers, $missing without"
echo "Phase 2 will replace this stub with the actual extraction + regeneration."
[ "$missing" -eq 0 ]
