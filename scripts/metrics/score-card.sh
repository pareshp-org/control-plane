#!/usr/bin/env bash
# score-card.sh — L4 metrics dump viewer (FD-085)
# Prints the raw recorded-metrics YAML for a product/period (or all products).
# NOTE: despite the historical "scorecard generator" name, this performs no
# scoring, aggregation, or threshold comparison — it is a read-only dump of
# whatever record-metric.sh wrote. Use validate-metrics.sh to check that a
# record exists and parses; this script does not re-check that.
#
# TODO(real scoring): no lane task currently defines weighted-metric-vs-target
# scoring for the records/metrics/<product>/<period>.yaml records this script
# reads. The nearest analog is lanes/L4-03-metric-register.md Phase 7
# (L4-P7-01..L4-P7-20), which computes each §103 measure against its own
# threshold from metrics/register + metrics/compute declarations — but that
# pipeline is a separate, schema-driven system (metric-declarations.yaml with
# an owner/source/threshold per measure) that does not read or write this
# script's records/metrics/*.yaml format, and it deliberately keeps measures
# separate rather than blending them into one composite score (see
# L4-05-pipeline-and-boards.md D-L4-P5-01/D-L4-P5-02: weights and thresholds
# are calibrated values owned by L0/L1, never invented by a lane). Before
# this script could compute a real score, an L0/L1 decision would need to
# define, per metric, a target and a weight — schemas/metrics/snapshot.v1
# .schema.json's `metrics` field is currently untyped free-form YAML with no
# such attributes. Until that decision exists, this script stays a dump.
# Usage: bash scripts/metrics/score-card.sh [product-id|all] [YYYY-MM]
# Args are positional (not --product/--period flags, unlike record-metric.sh).
set -euo pipefail
shopt -s nullglob

PRODUCT="${1:-all}"
PERIOD="${2:-$(date +%Y-%m)}"

# Warn (don't fail) if a metrics file exists but isn't parseable YAML with a
# metrics: block — previously such a file was cat'd verbatim with no warning.
check_well_formed() {
  python -c "
import sys, yaml
doc = yaml.safe_load(open(sys.argv[1])) or {}
sys.exit(0 if isinstance(doc.get('metrics'), dict) and doc['metrics'] else 1)
" "$1" 2>/dev/null || echo "WARNING: $1 is not parseable YAML with a non-empty metrics: block"
}

echo "=== Metrics dump: $PRODUCT / $PERIOD ==="
echo ""

if [[ "$PRODUCT" == "all" ]]; then
  for DIR in records/metrics/*/; do
    PROD=$(basename "$DIR")
    METRIC_FILE="$DIR${PERIOD}.yaml"
    if [[ -f "$METRIC_FILE" ]]; then
      echo "--- $PROD ---"
      check_well_formed "$METRIC_FILE"
      cat "$METRIC_FILE"
      echo ""
    else
      echo "--- $PROD --- (no data for $PERIOD)"
    fi
  done
else
  METRIC_FILE="records/metrics/$PRODUCT/${PERIOD}.yaml"
  if [[ -f "$METRIC_FILE" ]]; then
    check_well_formed "$METRIC_FILE"
    cat "$METRIC_FILE"
  else
    echo "No metrics found for product=$PRODUCT period=$PERIOD"
    echo "Record with: bash scripts/metrics/record-metric.sh --product $PRODUCT --metric <name> --value <n>"
  fi
fi
