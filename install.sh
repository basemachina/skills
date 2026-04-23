#!/usr/bin/env sh
set -eu

# basemachina/skills 手動 install スクリプト
#
# Usage:
#   install.sh <skill-name> [--agent <agent>] [--scope user|project] [--ref <git-ref>]
#
# Example:
#   curl -fsSL https://raw.githubusercontent.com/basemachina/skills/main/install.sh \
#     | sh -s -- bm-code-management --agent claude-code --scope user

REPO="basemachina/skills"
DEFAULT_REF="main"

usage() {
  cat <<'EOF'
Usage: install.sh <skill-name> [--agent <agent>] [--scope user|project] [--ref <git-ref>]

Agents:
  claude-code    ~/.claude/skills/ (user) or .claude/skills/ (project)
  codex          ~/.agents/skills/ (user) or .agents/skills/ (project)
  copilot        ~/.github/skills/ (user) or .github/skills/ (project)
  cursor         ~/.cursor/rules/ (user) or .cursor/rules/ (project)  [SKILL.md を rule として配置]

Scope:
  user     $HOME 配下（全プロジェクトで利用）
  project  カレントディレクトリ配下（そのプロジェクトのみ）

Cross-agent インストーラとしては gh skill install を推奨:
  gh skill install basemachina/skills <skill-name> --agent <agent> --scope <scope>
EOF
}

SKILL=""
AGENT="claude-code"
SCOPE="user"
REF="$DEFAULT_REF"

while [ $# -gt 0 ]; do
  case "$1" in
    --agent)
      AGENT="$2"
      shift 2
      ;;
    --scope)
      SCOPE="$2"
      shift 2
      ;;
    --ref)
      REF="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "unknown option: $1" >&2
      usage
      exit 2
      ;;
    *)
      if [ -z "$SKILL" ]; then
        SKILL="$1"
      else
        echo "unexpected argument: $1" >&2
        usage
        exit 2
      fi
      shift
      ;;
  esac
done

if [ -z "$SKILL" ]; then
  echo "error: skill-name が必要です" >&2
  usage
  exit 2
fi

case "$AGENT" in
  claude-code) SUBDIR=".claude/skills" ;;
  codex)       SUBDIR=".agents/skills" ;;
  copilot)     SUBDIR=".github/skills" ;;
  cursor)      SUBDIR=".cursor/rules" ;;
  *)
    echo "error: 未知の agent '$AGENT'" >&2
    exit 2
    ;;
esac

case "$SCOPE" in
  user)    TARGET_ROOT="$HOME" ;;
  project) TARGET_ROOT="$(pwd)" ;;
  *)
    echo "error: scope は user または project" >&2
    exit 2
    ;;
esac

TARGET_DIR="$TARGET_ROOT/$SUBDIR/$SKILL"

if [ -e "$TARGET_DIR" ]; then
  echo "error: $TARGET_DIR は既に存在します（削除してから再実行してください）" >&2
  exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "→ $REPO@$REF から skills/$SKILL を取得" >&2
git clone --depth 1 --branch "$REF" --filter=blob:none --sparse \
  "https://github.com/$REPO.git" "$TMP/repo" >/dev/null 2>&1
(cd "$TMP/repo" && git sparse-checkout set "skills/$SKILL" >/dev/null)

SRC="$TMP/repo/skills/$SKILL"
if [ ! -d "$SRC" ]; then
  echo "error: skills/$SKILL が $REPO に存在しません" >&2
  exit 1
fi

mkdir -p "$(dirname "$TARGET_DIR")"
cp -R "$SRC" "$TARGET_DIR"

echo "✓ $SKILL を $TARGET_DIR に install しました" >&2
