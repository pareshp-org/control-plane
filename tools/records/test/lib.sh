#!/usr/bin/env bash
# L4 test assertion library. Output grammar is fixed by L4-07-tests-and-runbook.md section 1.4.
set -u
L4_PASS=0; L4_FAIL=0; L4_SKIP=0

pass() { L4_PASS=$((L4_PASS+1)); echo "PASS $1 $2"; }
fail() { L4_FAIL=$((L4_FAIL+1)); echo "FAIL $1 expected=$2 actual=$3"; }
skip() { L4_SKIP=$((L4_SKIP+1)); echo "SKIP $1 $2"; }

assert_eq() { # id expected actual
  if [ "$2" = "$3" ]; then pass "$1" "eq=$2"; else fail "$1" "$2" "$3"; fi
}
assert_exit() { # id expected_code cmd...
  local id="$1" want="$2"; shift 2
  "$@" >/dev/null 2>&1; local got=$?
  if [ "$got" = "$want" ]; then pass "$id" "exit=$got"; else fail "$id" "exit=$want" "exit=$got"; fi
}
assert_rejects() { # id cmd... : passes only when the command exits NON-zero
  local id="$1"; shift
  if "$@" >/dev/null 2>&1; then fail "$id" "non-zero-exit" "exit=0"; else pass "$id" "rejected"; fi
}
assert_last_line() { # id expected_line cmd...
  local id="$1" want="$2"; shift 2
  local got; got="$("$@" 2>/dev/null | tail -1)"
  if [ "$got" = "$want" ]; then pass "$id" "line=$got"; else fail "$id" "$want" "$got"; fi
}
summary() { # suite-id
  if [ "$L4_FAIL" -eq 0 ]; then
    echo "SUITE $1 OK $L4_PASS/$((L4_PASS+L4_FAIL))"; return 0
  else
    echo "SUITE $1 FAIL $L4_FAIL of $((L4_PASS+L4_FAIL))"; return 1
  fi
}
