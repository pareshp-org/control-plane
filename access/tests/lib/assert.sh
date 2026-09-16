#!/usr/bin/env bash
# access/tests/lib/assert.sh
# Lane 5 assertion library (L5-07-01). Fail-closed: anything unevaluable is
# INDETERMINATE, never PASS. Doctrine: L5-07-tests-and-runbook.md Section 3.1.
set -uo pipefail
L5_FAILURES=0
L5_INDETERMINATE=0
l5_pass()          { echo "PASS $1"; }
l5_fail()          { echo "FAIL $1 :: $2"; L5_FAILURES=$((L5_FAILURES+1)); }
# INDETERMINATE (a subsystem gap, or evidence still awaited) is tracked
# separately from L5_FAILURES -- it is never a real FAIL, and must never be
# reported as one. l5_exit below gives it rc=2, distinct from FAIL's rc=1.
l5_indeterminate() { echo "INDETERMINATE $1 :: $2"; L5_INDETERMINATE=$((L5_INDETERMINATE+1)); }
# l5_refuses ID DESC CMD... : passes only when CMD exits non-zero (the control refused)
l5_refuses() {
  local id="$1"; local desc="$2"; shift 2
  if "$@" >/dev/null 2>&1; then l5_fail "$id" "$desc was PERMITTED and must be refused"
  else l5_pass "$id"; fi
}
# l5_permits ID DESC CMD... : the paired positive control
l5_permits() {
  local id="$1"; local desc="$2"; shift 2
  if "$@" >/dev/null 2>&1; then l5_pass "$id"
  else l5_fail "$id" "$desc was REFUSED and must be permitted"; fi
}
l5_exit() {
  # Precedence: a real FAIL always wins (rc=1), regardless of how many
  # INDETERMINATE results also accumulated. Only when there are zero real
  # failures does an accumulated INDETERMINATE make the script report
  # rc=2 instead of rc=0 -- INCOMPLETE must never override a known FAIL,
  # and a legitimate-INDETERMINATE-only run must never be reported as FAIL.
  if [ "$L5_FAILURES" -gt 0 ]; then
    echo "SUITE FAILURES=$L5_FAILURES"; exit 1
  elif [ "$L5_INDETERMINATE" -gt 0 ]; then
    echo "SUITE INCOMPLETE=$L5_INDETERMINATE"; exit 2
  else
    echo "SUITE OK"; exit 0
  fi
}
