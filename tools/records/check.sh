#!/usr/bin/env bash
set -eu
# check.sh — dispatch a per-task check file.
# Normal:  check.sh <TASK-ID>           runs checks/<TASK-ID>.sh
# Audit:   check.sh --audit <TASK-ID>   validates minimum check-file requirements
#                                        before running; the phase-exit gate uses this mode.
AUDIT=0
if [ "${1:-}" = "--audit" ]; then AUDIT=1; shift; fi
T="${1:?usage: check.sh [--audit] <TASK-ID>}"
D="$(cd "$(dirname "$0")" && pwd)"
F="$D/checks/${T}.sh"
if [ ! -f "$F" ]; then echo "CHECK ${T} ERROR no-check-file"; exit 3; fi
if [ "$AUDIT" -eq 1 ]; then
  LINES="$(wc -l < "$F")"
  if [ "$LINES" -lt 10 ]; then
    echo "CHECK ${T} ERROR audit-too-short lines=${LINES} min=10"; exit 3
  fi
  if ! grep -qE '(grep[[:space:]]|\[[[:space:]].*[=!]|[[:space:]]-eq[[:space:]]|[[:space:]]-ne[[:space:]])' "$F"; then
    echo "CHECK ${T} ERROR audit-no-assertion"; exit 3
  fi
  if ! grep -qiE '(negative|fixture.*fail|bad_fixture|neg_fixture|# neg)' "$F"; then
    echo "CHECK ${T} ERROR audit-no-negative-fixture"; exit 3
  fi
fi
if bash "$F" >/dev/null 2>&1; then echo "CHECK ${T} PASS"; exit 0; fi
echo "CHECK ${T} FAIL"; exit 1
