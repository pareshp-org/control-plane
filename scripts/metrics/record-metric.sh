#!/usr/bin/env bash
# record-metric.sh — L4 metric record writer (FD-085, L4-02)
# Usage: bash scripts/metrics/record-metric.sh --product <id> --metric <name> --value <n> --period <YYYY-MM>
set -euo pipefail

PRODUCT=""
METRIC=""
VALUE=""
PERIOD=$(date +%Y-%m)

while [[ $# -gt 0 ]]; do
  case $1 in
    --product) PRODUCT="$2"; shift 2;;
    --metric) METRIC="$2"; shift 2;;
    --value) VALUE="$2"; shift 2;;
    --period) PERIOD="$2"; shift 2;;
    *) shift;;
  esac
done

[[ -z "$PRODUCT" || -z "$METRIC" || -z "$VALUE" ]] && {
  echo "Usage: $0 --product <id> --metric <name> --value <n> [--period YYYY-MM]"
  exit 2
}

# PRODUCT/METRIC become path components and YAML mapping keys, and PERIOD
# becomes a path component too — restrict all three so they can't traverse
# paths or break YAML syntax.
ID_RE='^[A-Za-z0-9_.-]+$'
PERIOD_RE='^[0-9]{4}-[0-9]{2}$'
[[ "$PRODUCT" =~ $ID_RE ]] || { echo "Error: --product must match $ID_RE, got: $PRODUCT" >&2; exit 2; }
[[ "$METRIC" =~ $ID_RE ]] || { echo "Error: --metric must match $ID_RE, got: $METRIC" >&2; exit 2; }
[[ "$VALUE" =~ ^-?[0-9]+([.][0-9]+)?$ ]] || { echo "Error: --value must be numeric, got: $VALUE" >&2; exit 2; }
[[ "$PERIOD" =~ $PERIOD_RE ]] || { echo "Error: --period must match YYYY-MM, got: $PERIOD" >&2; exit 2; }

mkdir -p "records/metrics/$PRODUCT"
OUTFILE="records/metrics/$PRODUCT/${PERIOD}.yaml"

# Append, update in place, or create metric record
if [[ -f "$OUTFILE" ]]; then
  # METRIC is matched as a literal key, not a live regex: ID_RE permits '.'
  # (a regex any-char wildcard), which previously let e.g. --metric cost.usd
  # match and rewrite an unrelated key like costXusd. Escape regex
  # metacharacters so the grep/sed patterns match METRIC's literal text.
  METRIC_RE=$(printf '%s' "$METRIC" | sed 's/[.[\^$*]/\\&/g')
  if grep -qE "^  ${METRIC_RE}: " "$OUTFILE"; then
    # Metric already recorded for this period — overwrite its value in place
    # instead of appending a duplicate YAML key (which silently corrupted the
    # document: the second `key: value` line for the same key was undefined
    # behavior for any YAML parser reading this file).
    sed -i "s|^  ${METRIC_RE}: .*|  ${METRIC}: ${VALUE}|" "$OUTFILE"
  else
    echo "  $METRIC: $VALUE" >> "$OUTFILE"
  fi
else
  cat > "$OUTFILE" <<EOF
# Metric record — product: $PRODUCT, period: $PERIOD (FD-085, L4-02)
# Schema: schemas/metrics/snapshot.v1.schema.json
id: "${PRODUCT}-${PERIOD}"
product_id: "$PRODUCT"
period: "$PERIOD"
generated_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
metrics:
  $METRIC: $VALUE
EOF
fi

echo "METRIC RECORDED: $PRODUCT/$METRIC=$VALUE for $PERIOD"
