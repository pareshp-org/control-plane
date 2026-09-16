#!/usr/bin/env bash
# access/tests/at-090-founder-only.sh
# AT-090 - spec 100.6, 90.3, 90.4; invariant 106. Static half: Layer B is
# declared Founder-only and the named accepted-access record of 90.3 exists
# in the inventory. Live half is ASSISTED: the compensating audit trail and
# its review cadence.
set -uo pipefail
. access/tests/lib/assert.sh
PM=access/model/permission-matrix.yaml
if [ ! -f "$PM" ]; then l5_indeterminate "AT-090/static" "permission matrix absent: $PM"; l5_exit; fi
SCOPE="$(yq -r '.layers.B.scope // ""' "$PM")"
case "$SCOPE" in
  *Founder*) l5_pass "AT-090/static-founder-only" ;;
  *) l5_fail "AT-090/static-founder-only" "layers.B.scope is '$SCOPE'; spec 90.2 confines Layer B to the Founder" ;;
esac
ACC="$(grep -rliE 'accepted[_-]?risk|accepted[_-]?access' assets/inventory access/accepted-risks 2>/dev/null | head -n 1)"
if [ -n "$ACC" ]; then
  l5_pass "AT-090/static-accepted-access-record"
else
  l5_fail "AT-090/static-accepted-access-record" "no named accepted-access record for host-level administrative access (spec 90.3)"
fi
bash access/tests/lib/verify-evidence.sh AT-090
RC=$?
if [ "$RC" -eq 2 ]; then
  l5_indeterminate "AT-090/live" "awaiting human evidence"
elif [ "$RC" -eq 0 ]; then
  l5_pass "AT-090/live"
else
  l5_fail "AT-090/live" "evidence verification failed"
fi
l5_exit
