#!/usr/bin/env bash
# infra/tools/lane_guard_check.sh
# Lane 5 path-guard self-check (PARTITION.md rule 1, row "L5 Access, Infra &
# Ops": access/**, infra/**, ops-vm/**, notify/**, assets/**).
#
# A hard gate, not advice: it inspects the actual staged or committed diff
# for a foreign path and refuses to print PASS if one is found. Two modes:
#
#   staged        inspect `git diff --cached --name-only` (pre-commit use)
#   integration   inspect `git diff --name-only <merge-base>...HEAD` against
#                 the integration branch (pre-PR use; default branch name is
#                 overridable via LANE_GUARD_BASE)
#
# Exit 0  every changed path falls under an owned prefix -> "PATH GUARD PASS"
# Exit 1  a foreign path is present -> "PATH GUARD FAIL: <path>" per line
# Exit 2  git itself could not be inspected (fail-closed, never a silent pass)
set -u

OWNED_PREFIXES=(access/ infra/ ops-vm/ notify/ assets/)
MODE="${1:-staged}"
BASE="${LANE_GUARD_BASE:-integration}"

is_owned() {
  local path="$1" prefix
  for prefix in "${OWNED_PREFIXES[@]}"; do
    case "$path" in
      "$prefix"*) return 0 ;;
    esac
  done
  return 1
}

case "$MODE" in
  staged)
    CHANGED="$(git diff --cached --name-only 2>&1)"
    RC=$?
    ;;
  integration)
    MERGE_BASE="$(git merge-base "$BASE" HEAD 2>&1)"
    if [ $? -ne 0 ]; then
      echo "PATH GUARD FAIL-CLOSED: cannot resolve merge-base against $BASE: $MERGE_BASE"
      exit 2
    fi
    CHANGED="$(git diff --name-only "$MERGE_BASE"...HEAD 2>&1)"
    RC=$?
    ;;
  *)
    echo "USAGE: lane_guard_check.sh [staged|integration]"
    exit 2
    ;;
esac

if [ "$RC" -ne 0 ]; then
  echo "PATH GUARD FAIL-CLOSED: git diff failed: $CHANGED"
  exit 2
fi

FOREIGN=0
while IFS= read -r path; do
  [ -z "$path" ] && continue
  if ! is_owned "$path"; then
    echo "PATH GUARD FAIL: $path"
    FOREIGN=1
  fi
done <<< "$CHANGED"

if [ "$FOREIGN" -eq 1 ]; then
  echo "PATH GUARD RESULT FAIL"
  exit 1
fi
echo "PATH GUARD PASS"
echo "L5-T03 SELF-VERIFY PASS"
exit 0
