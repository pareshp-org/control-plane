#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-06 — deployment measures
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/deployments.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }

bash "$VS" --compute deployments >/dev/null || { echo "--compute deployments failed" >&2; exit 1; }

# Positive: a real fixture with one failed smoke and one rollback computes real rates
TMP=$(mktemp -d)
cat > "$TMP/DEP-1.yaml" <<'YAML'
record_schema_version: 1
id: DEP-2026-09-01-001
product: solvox
timestamp: 2026-09-01T10:00:00Z
smoke_result: pass
rollback_of: null
YAML
cat > "$TMP/DEP-2.yaml" <<'YAML'
record_schema_version: 1
id: DEP-2026-09-02-001
product: solvox
timestamp: 2026-09-02T10:00:00Z
smoke_result: fail
rollback_of: DEP-2026-09-01-001
YAML
OUT="$(python3 "$MOD" --store "$TMP" --json)"
echo "$OUT" | grep -q '"n": 2' || { echo "expected n=2: $OUT" >&2; rm -rf "$TMP"; exit 1; }
echo "$OUT" | grep -q '"deployment_failure_rate": 0.5' || { echo "expected failure rate 0.5: $OUT" >&2; rm -rf "$TMP"; exit 1; }
echo "$OUT" | grep -q '"rollback_rate": 0.5' || { echo "expected rollback rate 0.5: $OUT" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

# Negative fixture: a non-existent store must exit non-zero
if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --json >/dev/null 2>&1; then
  echo "neg-fixture: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-06 PASS"
