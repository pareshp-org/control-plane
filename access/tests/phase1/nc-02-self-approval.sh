#!/usr/bin/env bash
# access/tests/phase1/nc-02-self-approval.sh
# NC-02 - ASSISTED. The privileged step is performed by a named human; this
# script verifies only the returned evidence file. See L5-07-tests-and-runbook.md
# Section 1.1.
set -uo pipefail
. access/tests/lib/assert.sh
bash access/tests/lib/verify-evidence.sh NC-02
RC=$?
if [ "$RC" -eq 0 ]; then
  l5_pass "NC-02"
elif [ "$RC" -eq 2 ]; then
  echo "INCOMPLETE NC-02 :: awaiting human evidence"
  exit 2
else
  l5_fail "NC-02" "evidence verification failed"
fi
l5_exit
