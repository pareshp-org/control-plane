#!/usr/bin/env bash
# access/tests/at-100-conduct-separation.sh
# AT-100 - spec 100.6, 90.4, 88; invariant 110. Conduct evidence is held
# separately and holding people-intelligence never grants conduct-record
# access.
set -uo pipefail
. access/tests/lib/assert.sh
GATE=access/tools/check_people_intelligence_gate.py
command -v python3 >/dev/null 2>&1 || { l5_indeterminate "AT-100" "python3 not on PATH"; l5_exit; }
if [ ! -f "$GATE" ]; then l5_indeterminate "AT-100" "capability gate absent: $GATE"; l5_exit; fi
OUT="$(python3 "$GATE" --selftest 2>&1)"
if echo "$OUT" | grep -qF 'L5-T14 SELF-VERIFY PASS'; then
  l5_pass "AT-100/conduct-carve-out"
else
  l5_fail "AT-100/conduct-carve-out" "the gate selftest, which covers conduct-record access by a capability holder, did not pass: $OUT"
fi
CONDUCT="$(grep -rli 'conduct' ops-vm/grafana 2>/dev/null || true)"
if [ -z "$CONDUCT" ]; then
  l5_pass "AT-100/no-conduct-datasource"
else
  l5_fail "AT-100/no-conduct-datasource" "a Grafana instance references conduct data: $CONDUCT"
fi
l5_exit
