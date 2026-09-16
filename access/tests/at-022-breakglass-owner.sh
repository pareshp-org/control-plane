#!/usr/bin/env bash
# access/tests/at-022-breakglass-owner.sh
# AT-022 and NC-12 - spec 100.2, 14.4 components 1, 2 and 4, invariant 39.
# HUMAN-GATED. This script performs NO part of the continuity drill. It
# asserts only what the Lane-5-owned inventory must already declare, then
# verifies the drill record the L0 human lead produces. It can never report
# PASS from configuration alone.
set -uo pipefail
. access/tests/lib/assert.sh
if [ ! -d assets/inventory ]; then
  l5_indeterminate "AT-022/static" "PRE-K missing: assets/inventory"
  l5_exit
fi
ESCROW="$(grep -rliE 'escrow' assets/inventory 2>/dev/null | head -n 1)"
if [ -n "$ESCROW" ]; then
  l5_pass "AT-022/static-escrow-recorded"
else
  l5_fail "AT-022/static-escrow-recorded" "no asset entry records the escrow or its custodian (spec 14.4 escrow mechanics)"
fi
ACCTS="$(grep -rlE 'asset_class:[[:space:]]*founder_account' assets/inventory 2>/dev/null | wc -l | tr -d ' ')"
if [ "$ACCTS" -ge 1 ]; then
  l5_pass "AT-022/static-founder-account-inventory"
else
  l5_fail "AT-022/static-founder-account-inventory" "no founder_account entry exists; spec 14.4 component 2 requires every founder-only account enumerated"
fi
bash access/tests/lib/verify-evidence.sh AT-022
RC=$?
if [ "$RC" -eq 2 ]; then
  l5_indeterminate "AT-022/drill" "awaiting the L0 continuity drill record"
elif [ "$RC" -eq 0 ]; then
  l5_pass "AT-022/drill"
else
  l5_fail "AT-022/drill" "drill evidence verification failed"
fi
l5_exit
