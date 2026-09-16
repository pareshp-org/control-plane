#!/usr/bin/env bash
# Section 51.2: the off-VM liveness leg routes to the messaging channel and the
# Section 42.2 phone path DIRECTLY, never through the operations VM.
set -euo pipefail
fail=0
for f in "$@"; do
  [ -f "$f" ] || { echo "missing: $f"; fail=1; continue; }
  grep -q '^  - messaging_channel$'      "$f" || { echo "$f: no messaging_channel route"; fail=1; }
  grep -q '^  - phone_escalation_path$'  "$f" || { echo "$f: no phone_escalation_path route"; fail=1; }
  grep -q '^runs_off_operations_vm: true$' "$f" || { echo "$f: runs_off_operations_vm is not true"; fail=1; }
  if grep -qiE 'via_ops_vm|through_ops_vm|relay: *ops-vm' "$f"; then echo "$f: routes through the operations VM"; fail=1; fi
done
if [ "$fail" -eq 0 ]; then echo "DEADMAN-ROUTES-DIRECT: PASS"; else echo "DEADMAN-ROUTES-DIRECT: FAIL"; exit 1; fi
