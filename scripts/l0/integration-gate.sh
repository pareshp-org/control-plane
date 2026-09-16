#!/usr/bin/env bash
# integration-gate.sh — L0-05 integration gate (FD-082 normalized)
# Usage: bash scripts/l0/integration-gate.sh [--product <id>] (works from any
# invocation cwd — all checks below run relative to the implementation root
# (this script's own location, via BASH_SOURCE), not the caller's cwd)
# Runs the 12-question Q-gate (Q1-Q12) check for dispatch readiness
set -euo pipefail

IMPL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$IMPL_ROOT"

PRODUCT="${1:-all}"

echo "=== L0-05 Integration Gate: $PRODUCT ==="
echo "FD-014 gate: triage + lane coherence reviews must clear"
echo ""

# Q1-Q12 gate checks (FD-071..081, all answered in Session 14)
GATE_PASS=0
GATE_FAIL=0

q_check() {
  local QID="$1"; local DESC="$2"; local CMD="$3"
  if eval "$CMD" &>/dev/null; then
    echo "PASS $QID: $DESC"
    GATE_PASS=$((GATE_PASS + 1))
  else
    echo "FAIL $QID: $DESC"
    GATE_FAIL=$((GATE_FAIL + 1))
  fi
}

q_check Q1  "project-config.sh exists"    "test -f contracts/project-config.sh"
q_check Q2  "run-phase-0.sh exists"       "test -f run-phase-0.sh"
q_check Q3  "concordance check passes"    "bash _concordance-check.sh lanes"
q_check Q4  "canary intact"               "bash scripts/canary-check.sh registries/people/_canary.yaml"
q_check Q5  "schemas/ populated"          "ls schemas/registry/*.json"
q_check Q6  "registries/ initialized"     "ls registries/people/_canary.yaml"
q_check Q7  "records/ initialized"        "ls records/board/snapshot.yaml"
q_check Q8  "lane-guard.yml exists"       "test -f .github/workflows/lane-guard.yml"
q_check Q9  "validators/cli.py exists"    "test -f validators/registry/cli.py"
q_check Q10 "CODEOWNERS exists"           "test -f .github/CODEOWNERS"
q_check Q11 "INDEX.md exists"             "test -f master/INDEX.md || test -f INDEX.md"
q_check Q12 "FOUNDER_DECISIONS.md exists" "test -f _FOUNDER_DECISIONS.md"

echo ""
echo "Gate result: $GATE_PASS/$((GATE_PASS + GATE_FAIL)) checks pass"
[[ $GATE_FAIL -eq 0 ]] && echo "INTEGRATION GATE: PASS" || echo "INTEGRATION GATE: FAIL ($GATE_FAIL failures)"
[[ $GATE_FAIL -eq 0 ]]
