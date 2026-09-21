#!/usr/bin/env bash
# The post-patch smoke checklist of Section 51.4, followed by the mandated
# immediate reconciliation run. The patch is not recorded as complete until both
# pass clean. This script records no completion; it prints a verdict.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_env GRAFANA_SHARED_URL GRAFANA_SHARED_TOKEN GRAFANA_LAYERB_URL \
            GRAFANA_LAYERB_TOKEN CAPABILITY_HOLDERS_FILE
fail=0
ops-vm/checks/grafana-provisioned.sh "$GRAFANA_SHARED_URL" "$GRAFANA_SHARED_TOKEN" || fail=1
ops-vm/checks/grafana-provisioned.sh "$GRAFANA_LAYERB_URL" "$GRAFANA_LAYERB_TOKEN" || fail=1
ops-vm/checks/alert-test-fires.sh "$GRAFANA_SHARED_URL" "$GRAFANA_SHARED_TOKEN" || fail=1
ops-vm/checks/layerb-allowlist-matches-holders.sh ops-vm/layerb/access-list.yaml "$CAPABILITY_HOLDERS_FILE" || fail=1
if [ "$fail" -ne 0 ]; then echo "POST-PATCH-SMOKE: FAIL (checklist)"; exit 1; fi
OPS_VM_TRIGGER=post-patch-smoke ops-vm/jobs/run-reconcile.sh full \
  || { echo "POST-PATCH-SMOKE: FAIL (mandated reconciliation run)"; exit 1; }
echo "POST-PATCH-SMOKE: PASS"
