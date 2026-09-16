#!/usr/bin/env bash
# INGEST dispatcher. Lane 4, Phase 5. Output contract: L4-06-tasks.md section 0.5.
set -eu
cd "$(dirname "$0")/../.."
PY="${L4_PY:-python}"
run() { [ -f "$1" ] || { echo "INGEST ERROR missing-limb"; exit 3; }; exec "$PY" "$1"; }
case "${1:-}" in
  --collectors)   run tools/records/ingest/collectors.py ;;
  --devlake)      run tools/records/ingest/devlake.py ;;
  --prometheus)   run tools/records/ingest/prometheus.py ;;
  --scorecard)    run tools/records/ingest/scorecard.py ;;
  --source-kinds) run tools/records/ingest/source_kind.py ;;
  --freshness)    run tools/records/ingest/freshness.py ;;
  "")
    n=0
    for f in collectors devlake prometheus scorecard source_kind freshness; do
      p="tools/records/ingest/${f}.py"
      [ -f "$p" ] || { echo "INGEST ERROR missing-limb"; exit 3; }
      "$PY" "$p" >/dev/null || { echo "INGEST FAIL limb"; exit 1; }
      n=$((n+1))
    done
    echo "INGEST OK limbs=${n}"
    ;;
  *) echo "INGEST ERROR unknown-limb"; exit 3 ;;
esac
