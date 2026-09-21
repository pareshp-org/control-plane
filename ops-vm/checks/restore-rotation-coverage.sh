#!/usr/bin/env bash
# SIG-17 restore-test currency: Amber approaching, Blocking past (Section 52.2).
# Reads the rotation's own output; encodes no window of its own.
set -euo pipefail
F="${1:-/var/lib/ops-vm/restore-rotation/due.txt}"
[ -f "$F" ] || { echo "RESTORE-COVERAGE: NO-RUN-RECORDED -> BLOCKING"; exit 4; }
past=$(grep -vc '^RESTORE-ROTATION:' "$F" || true)
if [ "$past" -gt 0 ]; then
  echo "RESTORE-COVERAGE: $past product(s) past window -> BLOCKING"
  grep -v '^RESTORE-ROTATION:' "$F"
  exit 4
fi
echo "RESTORE-COVERAGE: 0 past window -> OK"
