#!/usr/bin/env bash
# tools/records/check.sh <task-id>
# Dispatches to tools/records/checks/<task-id>.sh. Every L4 metric-register
# and compute task (L4-P3-06, L4-P7-01..L4-P7-20) is proved by exactly one
# such file; this is the one entry point every task's SELF-VERIFY calls.
set -euo pipefail
TASK="${1:?usage: check.sh <task-id>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
CHECK="$HERE/checks/${TASK}.sh"
if [ ! -f "$CHECK" ]; then
  echo "CHECK $TASK ERROR no-check-file"
  exit 3
fi
bash "$CHECK"
