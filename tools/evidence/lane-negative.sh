#!/usr/bin/env bash
# THE Lane 2 negative entry point. Path fixed by protocol/00-test-strategy.md section 2.
# A negative fixture that PASSES its gate exits 3 and blocks the merge train.
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1
. tools/evidence/tests/lib/harness.sh

MODE="${1:---all}"; TARGET="${2:-}"
neg_one() {         # neg_one <GATE-ID>
  local g="$1"
  local decl="tools/evidence/gates/${g}.yaml"
  [ -f "$decl" ] || { printf 'GATE-DECLARATION-MISSING %s\n' "$g" >&2; return 1; }
  local want
  want="$(python3 -c "import sys,yaml;print(yaml.safe_load(open(sys.argv[1]))['negative']['expect_exit'])" "$decl")"
  local script="tools/evidence/tests/x2/${g}/negative.sh"
  [ -f "$script" ] || script="tools/evidence/tests/x1/${g}/negative.sh"
  [ -f "$script" ] || { printf 'GATE-UNARMED %s no negative case\n' "$g" >&2; return 1; }
  h_negative "$g" "$want" bash "$script"
}

case "$MODE" in
  --gate|--task) neg_one "$TARGET" || true; h_result "$TARGET"; exit $? ;;
  --all)
    for d in tools/evidence/gates/GATE-L2-*.yaml; do
      [ -e "$d" ] || { printf 'NO GATE DECLARATIONS FOUND\n' >&2; h_result ALL; exit $?; }
      neg_one "$(basename "$d" .yaml)" || true
    done
    h_result ALL; exit $? ;;
  *) printf 'usage: lane-negative.sh --all|--gate <ID>|--task <ID>\n' >&2; exit 1 ;;
esac
