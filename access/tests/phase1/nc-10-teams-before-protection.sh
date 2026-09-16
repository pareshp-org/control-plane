#!/usr/bin/env bash
# access/tests/phase1/nc-10-teams-before-protection.sh
# NC-10 - ASSISTED. The privileged step is performed by a named human; this
# script verifies only the returned evidence file. See L5-07-tests-and-runbook.md
# Section 1.1.
set -uo pipefail
. access/tests/lib/assert.sh
bash access/tests/lib/verify-evidence.sh NC-10
RC=$?
if [ "$RC" -eq 0 ]; then
  l5_pass "NC-10"
elif [ "$RC" -eq 2 ]; then
  echo "INCOMPLETE NC-10 :: awaiting human evidence"
  exit 2
else
  l5_fail "NC-10" "evidence verification failed"
fi
l5_exit
