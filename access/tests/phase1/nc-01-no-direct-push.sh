#!/usr/bin/env bash
# access/tests/phase1/nc-01-no-direct-push.sh
# NC-01 - ASSISTED. The privileged step is performed by a named human; this
# script verifies only the returned evidence file. See L5-07-tests-and-runbook.md
# Section 1.1.
set -uo pipefail
. access/tests/lib/assert.sh
bash access/tests/lib/verify-evidence.sh NC-01
RC=$?
if [ "$RC" -eq 0 ]; then
  l5_pass "NC-01"
elif [ "$RC" -eq 2 ]; then
  echo "INCOMPLETE NC-01 :: awaiting human evidence"
  exit 2
else
  l5_fail "NC-01" "evidence verification failed"
fi
l5_exit
