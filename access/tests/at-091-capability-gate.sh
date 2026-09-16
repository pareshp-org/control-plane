#!/usr/bin/env bash
# access/tests/at-091-capability-gate.sh
# AT-091 - spec 100.6, 90.4, D109; invariant 106. Access follows the
# capability, not the role name, and the capability is not delegable.
set -uo pipefail
. access/tests/lib/assert.sh
PM=access/model/permission-matrix.yaml
GATE=access/tools/check_people_intelligence_gate.py
command -v python3 >/dev/null 2>&1 || { l5_indeterminate "AT-091" "python3 not on PATH"; l5_exit; }
if [ ! -f "$GATE" ]; then l5_indeterminate "AT-091" "capability gate absent: $GATE"; l5_exit; fi
if [ ! -f "$PM" ]; then l5_indeterminate "AT-091" "permission matrix absent: $PM"; l5_exit; fi
OUT="$(python3 "$GATE" --selftest 2>&1)"
if echo "$OUT" | grep -qF 'L5-T14 SELF-VERIFY PASS'; then
  l5_pass "AT-091/gate-selftest"
else
  l5_fail "AT-091/gate-selftest" "capability gate selftest did not pass: $OUT"
fi
ABS="$(yq -r '.machine_identity_row.absolute // ""' "$PM")"
if [ "$ABS" = "true" ]; then
  l5_pass "AT-091/machine-identity-absolute"
else
  l5_fail "AT-091/machine-identity-absolute" "machine_identity_row.absolute is '$ABS'; spec 90.2 makes it absolute"
fi
# A prose record of D109 itself ("is not delegable", "is removed",
# "prohibited", "forbidden") documents the absence of delegation and must not
# be mistaken for a live declaration of one -- otherwise the check that
# proves D109 would fail on the very line that states D109.
DELEG="$(grep -rniE 'people[_-]intelligence' access --include='*.yaml' 2>/dev/null \
  | grep -Ei 'delegate|assignment_type' \
  | grep -Eiv 'is removed|not delegable|prohibited|forbidden' || true)"
if [ -z "$DELEG" ]; then
  l5_pass "AT-091/not-delegable"
else
  l5_fail "AT-091/not-delegable" "a Lane 5 declaration names a delegate or assignment type for people-intelligence (D109): $DELEG"
fi
l5_exit
