#!/usr/bin/env bash
# Lane 2 test harness. Counter contract: protocol/00-test-strategy.md section 3.
# Exit codes belong to the ENTRY POINTS only, not to tools/evidence programs,
# whose OK/FAIL/ERROR contract is L2-05-tasks.md section 0.4.
set -uo pipefail

H_ASSERTIONS=0
H_FAILURES=0
H_NEG_RUN=0
H_NEG_CORRECT=0
H_LEVEL="T1"

h_assert_exit() {   # h_assert_exit <label> <expected-exit> <command...>
  local label="$1"; local want="$2"; shift 2
  H_ASSERTIONS=$((H_ASSERTIONS + 1))
  "$@" >/dev/null 2>&1
  local got=$?
  if [ "$got" != "$want" ]; then
    H_FAILURES=$((H_FAILURES + 1))
    printf 'ASSERT-FAIL %s expected_exit=%s got_exit=%s\n' "$label" "$want" "$got" >&2
    return 1
  fi
  return 0
}

h_assert_stderr_has() {  # h_assert_stderr_has <label> <token> <command...>
  local label="$1"; local token="$2"; shift 2
  H_ASSERTIONS=$((H_ASSERTIONS + 1))
  local err
  err="$("$@" 2>&1 >/dev/null)"
  case "$err" in
    *"$token"*) return 0 ;;
    *) H_FAILURES=$((H_FAILURES + 1))
       printf 'ASSERT-FAIL %s missing_token=%s\n' "$label" "$token" >&2
       return 1 ;;
  esac
}

h_negative() {      # h_negative <gate-id> <expected-exit> <command...>
  local gate="$1"; local want="$2"; shift 2
  H_NEG_RUN=$((H_NEG_RUN + 1))
  "$@" >/dev/null 2>&1
  local got=$?
  if [ "$got" = "$want" ]; then
    H_NEG_CORRECT=$((H_NEG_CORRECT + 1))
    return 0
  fi
  printf 'NON-DISCRIMINATING %s expected_exit=%s got_exit=%s\n' "$gate" "$want" "$got" >&2
  return 1
}

h_result() {        # h_result <gate-id-or-ALL>; prints the last stdout line, sets exit code
  printf 'GATE-RESULT gate=%s level=%s assertions=%s failures=%s negatives_run=%s negatives_that_failed_correctly=%s\n' \
    "$1" "$H_LEVEL" "$H_ASSERTIONS" "$H_FAILURES" "$H_NEG_RUN" "$H_NEG_CORRECT"
  if [ "$H_NEG_RUN" -gt 0 ] && [ "$H_NEG_CORRECT" != "$H_NEG_RUN" ]; then return 3; fi
  if [ "$H_ASSERTIONS" = "0" ] && [ "$H_NEG_RUN" = "0" ]; then return 2; fi
  if [ "$H_FAILURES" != "0" ]; then return 1; fi
  return 0
}
