#!/usr/bin/env bash
# THE Lane 2 positive entry point. Path fixed by protocol/00-test-strategy.md section 2.
# Usage: lane-verify.sh --all | --gate <GATE-ID> | --task <task-id>
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1
. tools/evidence/tests/lib/harness.sh

MODE="${1:---all}"; TARGET="${2:-}"
run_one() {         # run_one <GATE-ID>
  local g="$1"
  local decl="tools/evidence/gates/${g}.yaml"
  [ -f "$decl" ] || { printf 'GATE-DECLARATION-MISSING %s\n' "$g" >&2; H_FAILURES=$((H_FAILURES+1)); H_ASSERTIONS=$((H_ASSERTIONS+1)); return 1; }
  local script="tools/evidence/tests/x2/${g}/positive.sh"
  [ -f "$script" ] || script="tools/evidence/tests/x1/${g}/positive.sh"
  [ -f "$script" ] || { printf 'GATE-UNARMED %s no positive case\n' "$g" >&2; H_FAILURES=$((H_FAILURES+1)); H_ASSERTIONS=$((H_ASSERTIONS+1)); return 1; }
  h_assert_exit "$g" 0 bash "$script"
}

case "$MODE" in
  --gate) run_one "$TARGET"; h_result "$TARGET"; exit $? ;;
  --task) run_one "$TARGET"; h_result "$TARGET"; exit $? ;;
  --all)
    for d in tools/evidence/gates/GATE-L2-*.yaml; do
      [ -e "$d" ] || { printf 'NO GATE DECLARATIONS FOUND\n' >&2; h_result ALL; exit $?; }
      g="$(basename "$d" .yaml)"
      run_one "$g" || true
    done
    h_result ALL; exit $? ;;
  *) printf 'usage: lane-verify.sh --all|--gate <ID>|--task <ID>\n' >&2; exit 1 ;;
esac
