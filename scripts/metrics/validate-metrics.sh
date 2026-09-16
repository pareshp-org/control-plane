#!/usr/bin/env bash
# validate-metrics.sh — L4 metric validation (FD-085)
# Checks that active products have a metric record for the current period,
# and that the record is parseable YAML with a non-empty `metrics:` block.
# (Note: the >=0.5-in-30-days figure from FD-031/PFD-031 is the staffing
# FLOOR_FTE obligation implemented in scripts/l4/scheduling.py and checked by
# `make schedule-check` — it is unrelated to this script and is not checked
# here; a prior version of this header incorrectly implied otherwise.)
set -euo pipefail
shopt -s nullglob

PERIOD=$(date +%Y-%m)
MISSING=0
INVALID=0
TOTAL=0

echo "=== Metric Validation: $PERIOD ==="

for PRODUCT_FILE in registries/capabilities/*.yaml; do
  [[ -f "$PRODUCT_FILE" ]] || continue
  PROD=$(basename "$PRODUCT_FILE" .yaml)
  [[ "$PROD" == "_canary" || "$PROD" == ".gitkeep" ]] && continue
  TOTAL=$((TOTAL + 1))
  METRIC_FILE="records/metrics/$PROD/${PERIOD}.yaml"
  if [[ ! -f "$METRIC_FILE" ]]; then
    echo "MISSING: $PROD has no metrics for $PERIOD"
    MISSING=$((MISSING + 1))
  elif ! python -c "
import sys, yaml
doc = yaml.safe_load(open(sys.argv[1])) or {}
sys.exit(0 if isinstance(doc.get('metrics'), dict) and doc['metrics'] else 1)
" "$METRIC_FILE" 2>/dev/null; then
    echo "INVALID: $PROD metrics file for $PERIOD is not parseable YAML with a non-empty metrics: block"
    INVALID=$((INVALID + 1))
  else
    echo "OK: $PROD"
  fi
done

echo ""
echo "Summary: $((TOTAL - MISSING - INVALID))/$TOTAL products have valid metrics for $PERIOD"
[[ $MISSING -eq 0 && $INVALID -eq 0 ]] && exit 0 || exit 1
