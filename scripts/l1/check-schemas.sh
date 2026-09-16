#!/usr/bin/env bash
# check-schemas.sh — L1-02 schema validation (FD-096)
# Validates all schema files are valid JSON with required fields
set -euo pipefail
shopt -s nullglob

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMPL_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$IMPL_ROOT"

FAIL=0
PASS=0

echo "=== L1-02 Schema Check ==="

for SCHEMA_FILE in schemas/**/*.json schemas/*.json; do
  [[ -f "$SCHEMA_FILE" ]] || continue

  # Check valid JSON
  if python3 -c "import json,sys; json.load(sys.stdin)" < "$SCHEMA_FILE" 2>/dev/null; then
    # Check required fields
    HAS_ID=$(python3 -c "import json,sys; d=json.load(sys.stdin); print('ok' if '\$id' in d else 'missing')" < "$SCHEMA_FILE")
    if [[ "$HAS_ID" == "ok" ]]; then
      echo "PASS: $SCHEMA_FILE"
      PASS=$((PASS + 1))
    else
      echo "FAIL: $SCHEMA_FILE — missing \$id"
      FAIL=$((FAIL + 1))
    fi
  else
    echo "FAIL: $SCHEMA_FILE — invalid JSON"
    FAIL=$((FAIL + 1))
  fi
done

[[ $((PASS + FAIL)) -gt 0 ]] || { echo "FAIL: no schema files found under schemas/"; exit 1; }

echo ""
echo "Schema check: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]]
