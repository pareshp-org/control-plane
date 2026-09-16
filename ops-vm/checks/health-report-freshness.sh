#!/usr/bin/env bash
# Section 51.2: health report refreshed daily; Amber on staleness. Degrade
# openly rather than show stale data as current.
set -euo pipefail
F=/var/lib/ops-vm/health/health-freshness.prom
if [ ! -f "$F" ]; then echo "HEALTH-REPORT: NO-RUN-RECORDED -> AMBER (render stale banner)"; exit 1; fi
ts=$(awk '{print $2}' "$F"); age=$(( ( $(date -u +%s) - ts ) / 3600 ))
if [ "$age" -ge 24 ]; then
  echo "HEALTH-REPORT: age=${age}h -> AMBER (render stale banner)"; exit 1
fi
echo "HEALTH-REPORT: age=${age}h -> OK"
