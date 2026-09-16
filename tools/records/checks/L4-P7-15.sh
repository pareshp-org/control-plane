#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-15 — estimate-vs-actual and forecast-calibration
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/estimates.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }
bash "$VS" --compute estimates >/dev/null || { echo "--compute estimates failed" >&2; exit 1; }

# elapsed (4.5) and elapsed_net_blocked (3.25) deliberately differ - the two ratios
# computed against point_value=3 must therefore differ too, proving no field swap.
TMP=$(mktemp -d)
cat > "$TMP/EST-1.yaml" <<'YAML'
record_schema_version: 1
id: EST-2026-09-12-031
product: solvox
timestamp: 2026-09-12T17:05:00Z
work_item: work-item/4388
band: M
point_value: 3
elapsed: 4.5
elapsed_net_blocked: 3.25
unit: days
YAML
OUT="$(python3 "$MOD" --store "$TMP" --json)"
ACC=$(echo "$OUT" | python3 -c "import json,sys;print(json.load(sys.stdin)['estimation_accuracy_ratio_avg'])")
CAL=$(echo "$OUT" | python3 -c "import json,sys;print(json.load(sys.stdin)['forecast_calibration_ratio_avg'])")
if [ "$ACC" = "$CAL" ]; then
  echo "elapsed and elapsed_net_blocked produced the SAME ratio - fields are confused: $OUT" >&2
  rm -rf "$TMP"
  exit 1
fi
rm -rf "$TMP"

if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --json >/dev/null 2>&1; then
  echo "positive-store-absent-check: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-15 PASS"
