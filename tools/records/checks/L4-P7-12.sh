#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-12 — security-review measures
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/security_reviews.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }
bash "$VS" --compute security_reviews >/dev/null || { echo "--compute security_reviews failed" >&2; exit 1; }

TMP=$(mktemp -d)
cat > "$TMP/SR-1.yaml" <<'YAML'
record_schema_version: 1
id: SR-2026-09-01-001
product: solvox
timestamp: 2026-09-01T00:00:00Z
reviewer: sec-1
subject: quarterly review
findings:
  - summary: unfixed thing
    severity: medium
    disposition: unfixed
YAML
if OUT=$(python3 "$MOD" --store "$TMP" --json 2>&1); then
  echo "neg-fixture: unfixed finding with no owner was accepted" >&2
  echo "$OUT" >&2
  rm -rf "$TMP"
  exit 1
fi
echo "$OUT" | grep -q "unfixed-finding-no-owner" || { echo "rejection did not name the real problem: $OUT" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --json >/dev/null 2>&1; then
  echo "positive-store-absent-check: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-12 PASS"
