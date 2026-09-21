#!/usr/bin/env bash
# access/tests/phase1/nc-11-env-secret-denied.sh
# NC-11 - ASSISTED. The privileged step is performed by a named human; this
# script verifies only the returned evidence file. See L5-07-tests-and-runbook.md
# Section 1.1.
set -uo pipefail
. access/tests/lib/assert.sh
bash access/tests/lib/verify-evidence.sh NC-11
RC=$?
if [ "$RC" -eq 0 ]; then
  l5_pass "NC-11"
elif [ "$RC" -eq 2 ]; then
  echo "INCOMPLETE NC-11 :: awaiting human evidence"
  exit 2
else
  l5_fail "NC-11" "evidence verification failed"
fi
l5_exit
