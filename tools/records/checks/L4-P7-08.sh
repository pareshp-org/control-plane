#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-08 — restore measures (freshness, failed tests)
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/restore.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }
bash "$VS" --compute restore >/dev/null || { echo "--compute restore failed" >&2; exit 1; }

TMP=$(mktemp -d)
cat > "$TMP/RST-1.yaml" <<'YAML'
record_schema_version: 1
id: RST-2026-09-01-001
product: solvox
timestamp: 2026-09-01T00:00:00Z
result: fail
restore_environment: sandbox
integrity_check: row-counts
integrity_check_result: fail
verifier: qa-1
YAML
OUT="$(python3 "$MOD" --store "$TMP" --as-of 2026-09-05T00:00:00 --json)"
echo "$OUT" | grep -q '"failed_restore_tests": 1' || { echo "expected 1 failed test: $OUT" >&2; rm -rf "$TMP"; exit 1; }
echo "$OUT" | grep -q '"days_since_last_pass": null' || { echo "expected no passing restore, days_since_last_pass=null: $OUT" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --json >/dev/null 2>&1; then
  echo "neg-fixture: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-08 PASS"
