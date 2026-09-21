#!/usr/bin/env bash
# scripts/l2/gate-check.sh — Local CI gate check (L2).
# Runs the same checks that GitHub Actions lane-guard.yml runs, locally.
# Usage: bash scripts/l2/gate-check.sh [--lane L1]
set -uo pipefail

LANE="${1:-}"
IMPL_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== L2 Gate Check (local) ==="
echo "IMPL_ROOT: $IMPL_ROOT"
echo ""

# Check 1: Concordance
echo "[1/3] Running concordance check..."
if bash "$IMPL_ROOT/_concordance-check.sh" "$IMPL_ROOT/lanes" 2>&1; then
    echo "  PASS: concordance"
else
    echo "  FAIL: concordance — fix lane index/body mismatches before submitting PR"
    exit 1
fi

# Check 2: Validator CLI
echo "[2/3] Running validator (all 18 rules)..."
if cd "$IMPL_ROOT" && python -m validators.registry.cli \
    --root "$IMPL_ROOT" \
    --as-of "$(date +%Y-%m-%d)" \
    --records-root "$IMPL_ROOT/records" \
    --format json 2>&1 | python -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  Status: {d['status']} ({d.get('rules_run', '?')} rules)\")
for f in d.get('findings', []):
    print(f\"  {f}\")
if d['status'] == 'ERROR':
    print(f\"  Error: {d.get('error', 'unknown error')}\")
sys.exit(0 if d['status']=='PASS' else 1)
"; then
    echo "  PASS: validator"
else
    echo "  FAIL: validator — fix registry violations before submitting PR"
    exit 1
fi

# Check 3: Canary
echo "[3/3] Checking canary sentinel..."
if bash "$IMPL_ROOT/scripts/canary-check.sh" \
    "$IMPL_ROOT/registries/people/_canary.yaml" 2>&1; then
    echo "  PASS: canary"
else
    echo "  FAIL: canary — _canary.yaml sentinel corrupted"
    exit 1
fi

echo ""
echo "=== ALL L2 GATE CHECKS PASSED ==="
