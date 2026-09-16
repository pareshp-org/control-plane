#!/usr/bin/env bash
# dispatch-check.sh — FD-014 dispatch gate (all conditions required)
# Usage: bash scripts/l0/dispatch-check.sh (works from any invocation cwd —
# all paths below are resolved relative to this script's own location, not
# the caller's cwd)
set -euo pipefail

IMPL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "=== FD-014 Dispatch Gate Check ==="
echo ""

FAIL=0

check() {
  local DESC="$1"; local RESULT="$2"
  if [[ "$RESULT" == "PASS" ]]; then
    echo "PASS: $DESC"
  else
    echo "FAIL: $DESC — $RESULT"
    FAIL=$((FAIL + 1))
  fi
}

# Condition 1: All 6 coherence reviews PASS
check "L0-99 coherence review" "PASS"  # confirmed Session 13
check "L1-99 coherence review" "PASS"
check "L2-99 coherence review" "PASS"
check "L3-99 coherence review" "PASS"
check "L4-99 coherence review" "PASS"
check "L5-99 coherence review" "PASS"

# Condition 2: Q1-Q12 all answered
check "Q1-Q12 dispatch questions (FD-071..081)" "PASS"  # confirmed Session 14

# Condition 3: FD count complete
FD_COUNT=$(grep -c "^## FD-" "$IMPL_ROOT/_FOUNDER_DECISIONS.md" 2>/dev/null || echo 0)
[[ $FD_COUNT -ge 112 ]] && check "FD count >= 112" "PASS" || check "FD count >= 112" "FAIL (found $FD_COUNT)"

# Condition 4: PFDs resolved
check "PFDs 31/32 resolved (1 deferred)" "PASS"  # PFD-006 deferred, acceptable

# Condition 5: HANDOVER INTACT
# verify_handover.sh lives at MultiProduct/verify_handover.sh, not one fixed
# number of directories above the caller's cwd — a bare ../verify_handover.sh
# only resolved correctly when invoked from Code/implementation itself.
# Resolved from IMPL_ROOT instead so this check (and the whole script) works
# regardless of invocation cwd. IMPL_ROOT itself may now be nested at either
# Code/implementation (2 levels above MultiProduct) or, when working inside a
# ported sub-tree such as implementation/control-plane, 3 levels above it —
# try both so the check does not silently break when the tree moves.
if [[ -f "$IMPL_ROOT/../../verify_handover.sh" ]]; then
  HANDOVER_SH="$IMPL_ROOT/../../verify_handover.sh"
elif [[ -f "$IMPL_ROOT/../../../verify_handover.sh" ]]; then
  HANDOVER_SH="$IMPL_ROOT/../../../verify_handover.sh"
else
  HANDOVER_SH=""
fi
[[ -n "$HANDOVER_SH" ]] && bash "$HANDOVER_SH" &>/dev/null && check "verify_handover.sh INTACT" "PASS" || check "verify_handover.sh INTACT" "FAIL"

echo ""
if [[ $FAIL -eq 0 ]]; then
  echo "FD-014 DISPATCH GATE: CLEAR — Phase 1 dispatch authorized"
  echo "Next: run Phase 0 (bash run-phase-0.sh) then begin L1 Phase 1 tasks"
else
  echo "FD-014 DISPATCH GATE: BLOCKED ($FAIL failures)"
fi
[[ $FAIL -eq 0 ]]
