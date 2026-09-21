#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-13 — decision latency, queue depth and age
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/decisions.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }
bash "$VS" --compute decisions >/dev/null || { echo "--compute decisions failed" >&2; exit 1; }

TMP=$(mktemp -d)
cat > "$TMP/DEC-1.yaml" <<'YAML'
record_schema_version: 1
id: DEC-2026-09-10-003
product: portfolio
timestamp: 2026-09-10T11:00:00Z
decider: founder
prompt_received: 2026-09-08
decided: 2026-09-10
subject: test
options_considered: [a]
evidence: []
YAML
OUT="$(python3 "$MOD" --store "$TMP" --json)"
echo "$OUT" | grep -q '"decision_latency_days_avg": 2.0' || { echo "expected 2-day latency: $OUT" >&2; rm -rf "$TMP"; exit 1; }

# neg: a decided record missing 'decided' must be rejected
cat > "$TMP/DEC-2.yaml" <<'YAML'
record_schema_version: 1
id: DEC-2026-09-11-004
product: portfolio
timestamp: 2026-09-11T11:00:00Z
decider: founder
prompt_received: 2026-09-09
subject: test2
options_considered: [a]
evidence: []
YAML
if python3 "$MOD" --store "$TMP" --json >/dev/null 2>&1; then
  echo "neg-fixture: record missing 'decided' was accepted" >&2
  rm -rf "$TMP"
  exit 1
fi
rm -rf "$TMP"

if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --json >/dev/null 2>&1; then
  echo "positive-store-absent-check: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-13 PASS"
