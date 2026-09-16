#!/usr/bin/env bash
# infra/tools/readiness.sh
# L5 lane readiness. Runs every network-free, host-free gate this lane can
# prove from the repository alone, in dependency order. Fail closed
# (invariant 80): any non-zero gate is reported, and the run's own exit
# code is non-zero whenever any gate fails. See infra/READINESS.md for the
# gates this script cannot run from here (live-host AT tests) and for the
# ASSISTED / DECISION-REQUIRED items outstanding.
set -uo pipefail
pass=0; fail=0
FAILED_LABELS=""
run() { # run "<label>" <command...>
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    pass=$((pass+1))
  else
    fail=$((fail+1))
    FAILED_LABELS="$FAILED_LABELS $label"
    echo "GATE FAIL: $label"
  fi
}

run "owned-roots"          bash access/layer-b/check-owned-roots.sh
run "test-coverage"        bash access/tests/check-coverage.sh
run "ai-toolchain-pins"    python3 access/ai-toolchain/validate_toolchain.py
run "notify-channels"      python3 notify/check_channels.py
run "notify-closed-list"   python3 notify/check_closed_list.py
run "notify-push-list"     python3 notify/check_push_list.py
run "layerb-post-patch"    bash access/layer-b/check-post-patch.sh
run "team-derivation"      python3 access/tools/check_team_derivation.py
run "arming-order"         python3 access/tools/check_arming_order.py
run "secret-tiers"         python3 access/secrets/tools/validate_tiers.py
run "deadline-watch"       python3 assets/validate_deadlines.py
run "seat-check"           python3 assets/check_seats.py
run "runner-estate"        python3 assets/check_runner_estate.py
run "asset-inventory"      python3 assets/validate_assets.py
run "invariant-map"        python3 access/tools/validate_invariant_map.py
run "l2-handoff"           python3 infra/tools/validate_handoff.py

total=$((pass+fail))
echo "L5 READINESS: $pass/$total PASS"
if [ -n "$FAILED_LABELS" ]; then
  echo "L5 READINESS FAILING GATES:$FAILED_LABELS"
fi
[ "$fail" -eq 0 ]
