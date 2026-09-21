#!/usr/bin/env bash
# Section 94.7: the sweep runs daily. Degrade openly rather than show a stale
# sweep as current (Section 51.2).
set -euo pipefail
F="${1:-/var/lib/ops-vm/inventory/expiry-freshness.prom}"
if [ ! -f "$F" ]; then echo "EXPIRY-CHECK: NO-RUN-RECORDED -> AMBER (render stale banner)"; exit 1; fi
ts=$(awk '{print $2}' "$F"); age=$(( ( $(date -u +%s) - ts ) / 3600 ))
if [ "$age" -ge 24 ]; then echo "EXPIRY-CHECK: age=${age}h -> AMBER (render stale banner)"; exit 1; fi
echo "EXPIRY-CHECK: age=${age}h -> OK"
