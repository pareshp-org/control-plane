#!/usr/bin/env bash
# SIG-34: the scheduled organisation export missing, failed, or not
# restore-tested within its 90-day window is RED (Section 52.2).
set -euo pipefail
F="${1:-/var/lib/ops-vm/metrics/org-export-freshness.prom}"
R="${2:-/var/lib/ops-vm/metrics/org-export-restore-test.prom}"
now=$(date -u +%s)
rc=0
if [ ! -f "$F" ]; then echo "export: NO-RUN-RECORDED -> RED"; rc=2
else
  ts=$(awk '{print $2}' "$F"); age=$(( (now - ts) / 86400 ))
  if [ "$age" -ge 1 ]; then echo "export: last success ${age}d ago -> RED"; rc=2
  else echo "export: last success ${age}d ago -> OK"; fi
fi
if [ ! -f "$R" ]; then echo "restore-test: NO-RUN-RECORDED -> RED"; rc=2
else
  ts=$(awk '{print $2}' "$R"); age=$(( (now - ts) / 86400 ))
  if [ "$age" -ge 90 ]; then echo "restore-test: ${age}d ago -> RED"; rc=2
  else echo "restore-test: ${age}d ago -> OK"; fi
fi
[ "$rc" -eq 0 ] && echo "EXPORT-STALENESS: PASS" || echo "EXPORT-STALENESS: RED"
exit "$rc"
