#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-07 — incident measures
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/incidents.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }
bash "$VS" --compute incidents >/dev/null || { echo "--compute incidents failed" >&2; exit 1; }

TMP=$(mktemp -d)
cat > "$TMP/INC-1.yaml" <<'YAML'
record_schema_version: 1
id: INC-2026-09-01-001
product: solvox
timestamp: 2026-09-01T00:00:00Z
severity: SEV-2
detected: 2026-09-01T00:00:00Z
detection_source: alert
responded: 2026-09-01T01:00:00Z
resolved: 2026-09-01T03:00:00Z
customer_impact: partial
pre_onboarding: false
YAML
OUT="$(python3 "$MOD" --store "$TMP" --json)"
echo "$OUT" | grep -q '"mttr_seconds_avg": 10800.0' || { echo "expected 3h MTTR: $OUT" >&2; rm -rf "$TMP"; exit 1; }
echo "$OUT" | grep -q '"detection_to_response_seconds_avg": 3600.0' || { echo "expected 1h detect-to-respond: $OUT" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --json >/dev/null 2>&1; then
  echo "neg-fixture: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-07 PASS"
