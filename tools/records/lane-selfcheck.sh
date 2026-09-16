#!/usr/bin/env bash
# tools/records/lane-selfcheck.sh
# Lane 4's own path-ownership guard (L4-06-tasks.md section 0.2 / PARTITION.md rule 1
# line 25). In control-plane, L4 may create or edit files only under schemas/records/**,
# metrics/**, tools/records/**. Run before every commit and every push.
# Output contract: L4-06-tasks.md section 0.5 - one final line, exit 0/1/3.
#   --paths            Checks the working tree's uncommitted changes (git status --porcelain)
#                       against the owned prefixes. Prints PATHS OK or PATHS FAIL <path>.
#   --paths <base>...<head>   Same check against a committed range instead.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
CP="$(cd "$HERE/../.." && pwd)"
cd "$CP"

OWNED_REGEX='^(schemas/records/|metrics/|tools/records/)'

case "${1:-}" in
  --paths)
    shift
    if [ "${1:-}" != "" ]; then
      changed="$(git diff --name-only "$1" 2>/dev/null)" || { echo "PATHS ERROR unreadable-range:$1"; exit 3; }
    else
      # Uncommitted changes: staged, unstaged, and untracked.
      changed="$( { git diff --name-only HEAD 2>/dev/null; git ls-files --others --exclude-standard 2>/dev/null; } | sort -u )"
    fi
    foreign="$(printf '%s\n' "$changed" | grep -vE "$OWNED_REGEX" | grep -v '^$' || true)"
    if [ -n "$foreign" ]; then
      echo "PATHS FAIL $(printf '%s' "$foreign" | tr '\n' ' ')"
      exit 1
    fi
    echo "PATHS OK"
    ;;
  "")
    echo "PATHS ERROR no-mode"
    exit 3
    ;;
  *)
    echo "PATHS ERROR unknown-mode:$1"
    exit 3
    ;;
esac
