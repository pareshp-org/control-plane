#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-09 — UAT coverage and pass rate
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/uat.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }
bash "$VS" --compute uat >/dev/null || { echo "--compute uat failed" >&2; exit 1; }

TMP=$(mktemp -d)
cat > "$TMP/UAT-1.yaml" <<'YAML'
record_schema_version: 1
id: UAT-2026-09-01-001
product: solvox
timestamp: 2026-09-01T00:00:00Z
result: pass
executed_by: qa-1
uat_contract: verification/uat.md@abc
environment: staging
work_item: work-item/1
YAML
cat > "$TMP/UAT-2.yaml" <<'YAML'
record_schema_version: 1
id: UAT-2026-09-01-002
product: solvox
timestamp: 2026-09-01T00:00:00Z
result: fail
executed_by: qa-1
uat_contract: verification/uat.md@abc
environment: staging
YAML
OUT="$(python3 "$MOD" --store "$TMP" --json)"
echo "$OUT" | grep -q '"pass_rate": 0.5' || { echo "expected pass rate 0.5: $OUT" >&2; rm -rf "$TMP"; exit 1; }
echo "$OUT" | grep -q '"coverage_with_work_item": 1' || { echo "expected coverage 1: $OUT" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --json >/dev/null 2>&1; then
  echo "neg-fixture: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-09 PASS"
