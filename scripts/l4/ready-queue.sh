#!/usr/bin/env bash
# ready-queue.sh — L4 ready queue miss event (FD-091/PFD-017)
# Emitted when a ready item is not started within the timing window
# Usage: bash scripts/l4/ready-queue.sh --check
# NOTE: --window-days is not implemented (WINDOW is fixed below); do not pass it.
set -euo pipefail

WINDOW=3  # days — FD-091/PFD-017: emit event after this many days in ready state
CHECK_MODE="${1:---check}"

echo "=== L4 Ready Queue Check ==="
echo "Window: $WINDOW days (FD-091/PFD-017)"
echo ""

# Read open work items
WORK_FILE="records/work/open.yaml"
if [[ ! -f "$WORK_FILE" ]]; then
  echo "No work file: $WORK_FILE"
  exit 0
fi

READY_COUNT=$(python3 -c "
import yaml
d = yaml.safe_load(open('$WORK_FILE'))
items = d.get('items', [])
ready = [i for i in items if i.get('column') == 'ready']
print(len(ready))
" 2>/dev/null || echo 0)

echo "Ready items: $READY_COUNT"
if [[ $READY_COUNT -eq 0 ]]; then
  echo "No ready items — queue miss check not needed"
else
  echo "TODO: check each ready item's age against $WINDOW day window (Phase 1)"
fi

echo ""
echo "Done"
