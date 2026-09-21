#!/usr/bin/env bash
# Blocker-issue template for lane L5, plan file
# Code/implementation/lanes/L5-01-org-and-access.md.
# Usage:
#   bash access/tools/blocker.sh TASK_ID TITLE TRIGGER COMMAND OBSERVED EXPECTED REASON
# A STOP rule is absolute: file the blocker and stop. Do not work around it.
set -eu
if [ "$#" -ne 7 ]; then
  echo "usage: blocker.sh TASK_ID TITLE TRIGGER COMMAND OBSERVED EXPECTED REASON" >&2
  exit 64
fi
TASK_ID="$1"; TITLE="$2"; TRIGGER="$3"; CMD="$4"; OBS="$5"; EXP="$6"; WHY="$7"
BODY="task_id:                ${TASK_ID}
lane:                   L5
plan_file:              Code/implementation/lanes/L5-01-org-and-access.md
trigger:                ${TRIGGER}
command_run:            ${CMD}
observed_output:        ${OBS}
expected_output:        ${EXP}
blocked_because:        ${WHY}
requires_decision_from: L0 integrator"
if command -v gh >/dev/null 2>&1; then
  gh issue create --title "BLOCKER ${TASK_ID}: ${TITLE}" \
                  --label blocker --label lane-5 --body "${BODY}"
else
  mkdir -p access/checks/blockers
  OUT="access/checks/blockers/${TASK_ID}.blocker.txt"
  printf 'BLOCKER %s: %s\n%s\n' "${TASK_ID}" "${TITLE}" "${BODY}" > "${OUT}"
  echo "gh unavailable; blocker written to ${OUT}" >&2
fi
echo "BLOCKER FILED ${TASK_ID}"
