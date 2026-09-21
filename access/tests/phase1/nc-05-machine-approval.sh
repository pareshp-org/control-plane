#!/usr/bin/env bash
# access/tests/phase1/nc-05-machine-approval.sh
# NC-05 - spec 98.2 Phase 1 and 11.3: an approval from a machine account does
# NOT satisfy branch protection, because CODEOWNERS is generated to contain
# human identities only. Static half runs here; the live negative (a machine
# account's review actually submitted against a real PR) is ASSISTED.
#
# Uses the real generator and its own committed negative/positive fixtures
# (access/codeowners/generate_codeowners.py, access/testdata/codeowners/*)
# rather than the draft path access/codeowners/generate-codeowners.sh and a
# access/permission-model/teams.yaml machine_accounts list, neither of which
# any Lane 5 file writes (lanes/L5-98-DEEP-REVIEW.md B-05).
set -uo pipefail
. access/tests/lib/assert.sh
GEN="access/codeowners/generate_codeowners.py"
NEG="access/testdata/codeowners/machine-kind-input.json"
POS="access/testdata/codeowners/reference-input.json"
if [ ! -f "$GEN" ] || [ ! -f "$NEG" ] || [ ! -f "$POS" ]; then
  l5_indeterminate "NC-05/static" "PRE-B missing: $GEN, $NEG or $POS"
  l5_exit
fi
if python "$GEN" --org test-org --input "$NEG" >/dev/null 2>&1; then
  l5_fail "NC-05/static" "the generator emitted CODEOWNERS for an input naming a machine-kind identity"
else
  l5_pass "NC-05/static"
fi
if python "$GEN" --org test-org --input "$POS" >/dev/null 2>&1; then
  l5_pass "NC-05/static-positive-control"
else
  l5_fail "NC-05/static-positive-control" "the generator refused a clean, all-human input"
fi
bash access/tests/lib/verify-evidence.sh NC-05
RC=$?
if [ "$RC" -eq 2 ]; then
  l5_indeterminate "NC-05/live" "awaiting human evidence"
elif [ "$RC" -eq 0 ]; then
  l5_pass "NC-05/live"
else
  l5_fail "NC-05/live" "evidence verification failed"
fi
l5_exit
