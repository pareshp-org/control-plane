#!/usr/bin/env bash
# Generates the Operating System Health Report (Section 52.1) on the schedule of
# Section 51.2. Calibration values are read from os-health.yaml by the
# generator; this wrapper encodes none of them.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
OUT=/var/lib/ops-vm/health
install -d -m 0750 "$OUT"
start=$(date -u +%s)
set +e
os-health-report --output "$OUT/report.json" --emit-metrics "$OUT/health.prom"
rc=$?
set -e
now=$(date -u +%s)
if [ "$rc" -eq 0 ]; then
  printf 'ops_vm_job_last_success_timestamp{job_name="health-report"} %s\n' "$now" > "$OUT/health-freshness.prom"
  record_run health-report ok "seconds=$((now-start))"
else
  record_run health-report failed "rc=$rc"
  notify/bin/notify-job-result.sh health-report failed
fi
exit "$rc"
