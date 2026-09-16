#!/usr/bin/env bash
# scripts/verify-all.sh — single entry-point verification gate.
# Runs, in order: concordance check (5 lanes), canary check, registry
# validator CLI, and the pytest suite. Reports a clear pass/fail summary
# and exits 1 if ANY step failed.
#
# Note: deliberately NOT using `set -e` — every step must run even if an
# earlier one fails, so we get a full report in one pass.
set -uo pipefail

# Resolve repo root (this script lives in scripts/, repo root is its parent)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR" || { echo "FATAL: cannot cd to repo root ($ROOT_DIR)"; exit 1; }

TOTAL=4
PASSED=0
STEP_NUM=0
SUMMARY=""

run_step() {
  local name="$1"; shift
  STEP_NUM=$((STEP_NUM + 1))
  echo "=== [$STEP_NUM/$TOTAL] $name ==="
  echo "+ $*"
  "$@"
  local rc=$?
  if [ "$rc" -eq 0 ]; then
    PASSED=$((PASSED + 1))
    SUMMARY="${SUMMARY}  [PASS] $name
"
    echo "--- $name: PASS ---"
  else
    SUMMARY="${SUMMARY}  [FAIL] $name (exit $rc)
"
    echo "--- $name: FAIL (exit $rc) ---"
  fi
  echo
}

# 1. Concordance check — all 5 lanes must show OK
run_step "concordance-check (lanes)" bash "$ROOT_DIR/_concordance-check.sh" lanes

# 2. Canary check
run_step "canary-check" bash "$ROOT_DIR/scripts/canary-check.sh" registries/people/_canary.yaml

# 3. Registry validator CLI (must report PASS)
run_step "registry validator CLI" python -m validators.registry.cli \
  --root . \
  --as-of "$(date +%Y-%m-%d)" \
  --records-root records/ \
  --format json

# 4. pytest suite
run_step "pytest" python -m pytest tests/ --tb=short -q

echo "=================================================="
echo "VERIFY-ALL SUMMARY"
echo "=================================================="
printf '%s' "$SUMMARY"
echo "=================================================="
echo "=== ${PASSED}/${TOTAL} CHECKS PASSED ==="
echo "=================================================="

if [ "$PASSED" -eq "$TOTAL" ]; then
  exit 0
else
  exit 1
fi
