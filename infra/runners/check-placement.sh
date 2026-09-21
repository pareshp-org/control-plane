#!/usr/bin/env bash
# Estate side of RUNNER-PLACEMENT-1 (Section 49.1): no ci_runner inventory entry
# sits on the operations VM.
set -euo pipefail
DIR="${1:-assets/inventory}"
[ -d "$DIR" ] || { echo "RUNNER-PLACEMENT: FAIL-CLOSED (no inventory directory: $DIR)"; exit 1; }
found=0; bad=0
for f in "$DIR"/*.yaml; do
  [ -e "$f" ] || continue
  grep -q '^asset_class: ci_runner$' "$f" || continue
  found=$((found + 1))
  v=$(awk -F': *' '/^on_operations_vm:/{print $2; exit}' "$f" | tr -d '"')
  case "$v" in
    false) ;;
    true) echo "runner located on the operations VM: $f"; bad=1 ;;
    *) echo "no on_operations_vm declaration: $f"; bad=1 ;;
  esac
done
if [ "$bad" -eq 0 ]; then echo "RUNNER-PLACEMENT: PASS ($found ci_runner entries)"; else echo "RUNNER-PLACEMENT: FAIL"; exit 1; fi
