#!/usr/bin/env bash
# Emit one conforming ci_runner inventory entry.
# Usage: new_runner_entry.sh <hostname> <owner> <site> <power> <network> <group> <cost_band> <expiry_date>
set -euo pipefail
if [ "$#" -ne 8 ]; then
  echo "USAGE: new_runner_entry.sh <hostname> <owner> <site> <power> <network> <group> <cost_band> <expiry_date>"
  exit 2
fi
HOST="$1"; OWNER="$2"; SITE="$3"; POWER="$4"; NET="$5"; GROUP="$6"; BAND="$7"; EXP="$8"
OUT="assets/inventory/ci-runner-${HOST}.yaml"
cat > "$OUT" <<INNER
asset_id: ci-runner-${HOST}
asset_class: ci_runner
owner: ${OWNER}
expiry_date: "${EXP}"
alert_days: 30
cost_band: ${BAND}
spec_reference: "49.1, 46, D80, D87"
hostname: ${HOST}
patch_cadence: quarterly
site: ${SITE}
power: ${POWER}
network: ${NET}
runner_group: ${GROUP}
on_operations_vm: false
INNER
echo "RUNNER-ENTRY: WROTE ${OUT}"
