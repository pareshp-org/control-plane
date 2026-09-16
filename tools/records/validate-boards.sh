#!/usr/bin/env bash
# BOARDS dispatcher. Lane 4, Phase 5. Output contract: L4-06-tasks.md section 0.5.
set -eu
cd "$(dirname "$0")/../.."
PY="${L4_PY:-python}"
case "${1:-}" in
  --columns)  exec "$PY" tools/records/boards/columns.py ;;
  --horizons) exec "$PY" tools/records/boards/horizons.py ;;
  --ready)    exec "$PY" tools/records/boards/ready.py ;;
  --estimate-capture) exec "$PY" tools/records/estimate_capture.py --selftest ;;
  "")
    for f in tools/records/boards/columns.py tools/records/boards/horizons.py tools/records/boards/ready.py; do
      [ -f "$f" ] || { echo "BOARDS ERROR missing-limb"; exit 3; }
      "$PY" "$f" >/dev/null || { echo "BOARDS FAIL limb"; exit 1; }
    done
    if [ -f tools/records/estimate_capture.py ]; then
      "$PY" tools/records/estimate_capture.py --selftest >/dev/null || { echo "BOARDS FAIL limb"; exit 1; }
    fi
    echo "BOARDS OK"
    ;;
  *) echo "BOARDS ERROR unknown-limb"; exit 3 ;;
esac
