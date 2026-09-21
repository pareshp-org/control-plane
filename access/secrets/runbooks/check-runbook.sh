#!/usr/bin/env bash
# access/secrets/runbooks/check-runbook.sh
# "One page" is a requirement, so it is checked (Section 40.1 line 3683).
# Also proves the three BLOCKING steps and all ten step ids are present, and
# that every fifth-tier entry links this exact runbook.
set -eu
RB=access/secrets/runbooks/rotate-fifth-tier-credential.md
FAIL=0
if [ ! -f "$RB" ]; then echo "RUNBOOK missing $RB"; echo "RESULT FAIL"; exit 2; fi
LINES=$(wc -l < "$RB" | tr -d ' ')
echo "RUNBOOK-LINES $LINES"
if [ "$LINES" -gt 120 ]; then echo "RUNBOOK too long: one page is 120 lines"; FAIL=1; fi
for n in 01 02 03 04 05 06 07 08 09 10; do
  grep -q "STEP-$n " "$RB" || { echo "RUNBOOK missing STEP-$n"; FAIL=1; }
done
BLOCKING=$(grep -c 'BLOCKING' "$RB" || true)
echo "BLOCKING-STEPS $BLOCKING"
[ "$BLOCKING" -eq 3 ] || { echo "RUNBOOK expected exactly 3 BLOCKING steps"; FAIL=1; }
grep -q 'Section 14.4' "$RB" || { echo "RUNBOOK does not cite the Section 14.4 re-escrow"; FAIL=1; }
grep -q 'AT-110' "$RB" || { echo "RUNBOOK does not re-execute AT-110"; FAIL=1; }
grep -q 'CLEAN' "$RB" || { echo "RUNBOOK does not require a clean reconciliation run"; FAIL=1; }
LINKED=0
if compgen -G "access/secrets/fifth-tier/*.yaml" > /dev/null; then
  LINKED=$(grep -l "$RB" access/secrets/fifth-tier/*.yaml 2>/dev/null | wc -l | tr -d ' ')
fi
echo "ENTRIES-LINKING-RUNBOOK $LINKED"
[ "$LINKED" -eq 5 ] || { echo "RUNBOOK not linked by all five fifth-tier entries"; FAIL=1; }
if [ "$FAIL" -eq 0 ]; then echo "RESULT PASS"; else echo "RESULT FAIL"; exit 1; fi
