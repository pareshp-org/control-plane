#!/usr/bin/env bash
# Daily expiry-and-deadline sweep (Section 94.7). Wait surface only: reaching an
# alert threshold renders on the report; only the sweep's own failure pushes
# (Sections 92.11, 44.3).
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/inventory/inventory.env
set -a; . ops-vm/inventory/inventory.env; set +a
require_env INVENTORY_DIR DEADLINES_DIR INVENTORY_REPORT_DIR
set +e
python3 ops-vm/jobs/expiry_check.py
rc=$?
set -e
now=$(date -u +%s)
if [ "$rc" -eq 0 ]; then
  printf 'ops_vm_job_last_success_timestamp{job_name="expiry-check"} %s\n' "$now" \
    > "$INVENTORY_REPORT_DIR/expiry-freshness.prom"
  record_run expiry-check ok "report=$INVENTORY_REPORT_DIR/expiry-report.txt"
else
  record_run expiry-check failed "rc=$rc"
  notify/bin/notify-job-result.sh expiry-check failed "rc=$rc"
fi
exit "$rc"
