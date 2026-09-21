#!/usr/bin/env bash
# Local view only. A stale value here is informative; the authoritative decision
# is the watchdog's, off this host (D94).
set -euo pipefail
F="${1:-/var/lib/ops-vm/metrics/deadman.prom}"
[ -f "$F" ] || { echo "DEADMAN-LOCAL: NO-CHECKIN-RECORDED (authoritative view is off-VM)"; exit 1; }
ts=$(awk '{print $2}' "$F"); age=$(( $(date -u +%s) - ts ))
echo "DEADMAN-LOCAL: last check-in ${age}s ago (authoritative view is off-VM)"
