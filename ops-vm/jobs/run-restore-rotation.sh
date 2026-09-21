#!/usr/bin/env bash
# Nightly: advance the rolling restore rotation and open the restore-verification
# task for the next product due (Section 94.7). The task is opened through the
# published CLI; this host never edits .github/workflows/** or records/**.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_env PRODUCT_REGISTRY_FILE RESTORE_RECORD_DIR
OUT=/var/lib/ops-vm/restore-rotation
install -d -m 0750 "$OUT"
set +e
python3 ops-vm/jobs/restore_rotation.py > "$OUT/due.txt"
rc=$?
set -e
if [ "$rc" -ne 0 ]; then
  cat "$OUT/due.txt"
  record_run restore-rotation failed "rc=$rc"
  notify/bin/notify-job-result.sh restore-rotation failed "rc=$rc"
  exit "$rc"
fi
next=$(grep -v '^RESTORE-ROTATION:' "$OUT/due.txt" | head -1 | cut -f1 || true)
if [ -n "$next" ]; then
  open-restore-verification --product "$next" --due "$(date -u +%F)"
  record_run restore-rotation ok "opened=$next"
else
  # Section 53.1: a clean run is recorded as clean.
  record_run restore-rotation ok "no product outside its window"
fi
exit 0
