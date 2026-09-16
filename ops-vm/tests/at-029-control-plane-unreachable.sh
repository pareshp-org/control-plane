#!/usr/bin/env bash
# ops-vm/tests/at-029-control-plane-unreachable.sh
# AT-029 - spec 100.3, 45.2, 46.1, 51.3. Static half proves the two
# properties the drill depends on: detection lives OFF the operations VM,
# and no product runtime path touches it. The live half (VM down, products
# serving, manual rollback) is ASSISTED.
set -uo pipefail
. access/tests/lib/assert.sh
UP=assets/inventory/detection-leg-external-uptime.yaml
DM=assets/inventory/detection-leg-dead-mans-switch.yaml
if [ ! -f "$UP" ] || [ ! -f "$DM" ]; then
  l5_indeterminate "AT-029/static" "PRE-K missing an off-VM detection leg: $UP or $DM (spec 51.5)"
  l5_exit
fi
OFFVM=0
for f in "$UP" "$DM"; do
  v="$(yq -r '.runs_off_operations_vm // ""' "$f")"
  if [ "$v" != "true" ]; then
    l5_fail "AT-029/static-detection-off-vm" "$f does not declare runs_off_operations_vm: true (spec 45.2, 51.5)"
    OFFVM=1
  fi
done
[ "$OFFVM" -eq 0 ] && l5_pass "AT-029/static-detection-off-vm"
# spec 45.2, 51.3: flag only workflows that TARGET the ops-vm as a deployment
# environment or runner host — not workflows that merely reference ops-vm script
# paths as arguments (e.g. L5-04's contract with L2 calls ops-vm/export/put.sh
# as a run: argument, which is permitted). Grep for runner/host/ssh directives.
RUNTIME="$(grep -rlE '(runs-on[[:space:]]*:[[:space:]]*.*ops-vm|environment[[:space:]]*:[[:space:]]*.*ops-vm|ssh[[:space:]].*ops-vm)' .github/workflows 2>/dev/null || true)"
if [ -z "$RUNTIME" ]; then
  l5_pass "AT-029/static-no-runtime-dependency"
else
  l5_fail "AT-029/static-no-runtime-dependency" "a workflow deploys to or runs on the operations VM (spec 45.2, 51.3 — runner/host dependency, not a script-path reference): $RUNTIME"
fi
RT="$(ls .github/workflows 2>/dev/null | grep -c 'restore-test')"
if [ "$RT" -ge 1 ]; then
  l5_pass "AT-029/static-restore-test-workflow-present"
else
  l5_fail "AT-029/static-restore-test-workflow-present" "no restore-test workflow exists (spec 99.2 row E); the quarterly drill has no runner"
fi
bash access/tests/lib/verify-evidence.sh AT-029
RC=$?
if [ "$RC" -eq 2 ]; then
  l5_indeterminate "AT-029/live" "awaiting human evidence"
elif [ "$RC" -eq 0 ]; then
  l5_pass "AT-029/live"
else
  l5_fail "AT-029/live" "evidence verification failed"
fi
l5_exit
