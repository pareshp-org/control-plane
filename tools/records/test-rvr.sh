#!/usr/bin/env bash
# tools/records/test-rvr.sh — proves charter DoD-9.
# Master Spec v4.0 Section 97.2 line 8871.
# Runs against a throwaway clone of the records repository; the real store is untouched.
set -u
: "${CP_ROOT:?CP_ROOT not set}"
: "${CPR_ROOT:?CPR_ROOT not set}"
SANDBOX="$(mktemp -d)"
cp -R "$CPR_ROOT/." "$SANDBOX/"
export CPR_ROOT="$SANDBOX"
git -C "$SANDBOX" config user.email "records-writer@test.invalid"
git -C "$SANDBOX" config user.name "records-writer-test"
H="$CP_ROOT/tools/records/record-verification-result"
PASSED=0; FAILED=0
t() { # t <label> <expect-exit> <command...>
  label="$1"; want="$2"; shift 2
  "$@" >/tmp/rvrout.$$ 2>&1; got=$?
  if [ "$got" = "$want" ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); echo "RVR CASE FAIL $label want-exit=$want got-exit=$got"; cat /tmp/rvrout.$$; fi
  rm -f /tmp/rvrout.$$
}
t armed-pass            0 "$H" demoprod ITEM-1 manual_verification pass https://example.invalid/run/1 lead-1
t armed-fail            0 "$H" demoprod ITEM-2 restore_test_confirmation fail https://example.invalid/run/2 qa-1
t unknown-mechanism     2 "$H" demoprod ITEM-3 not_a_mechanism pass https://example.invalid/run/3 lead-1
t unarmed-mechanism     3 "$H" demoprod ITEM-4 support_loop_closure pass https://example.invalid/run/4 lead-1
t bad-result            2 "$H" demoprod ITEM-5 manual_verification maybe https://example.invalid/run/5 lead-1
t bad-evidence-link     2 "$H" demoprod ITEM-6 manual_verification pass not-a-url lead-1
t empty-product         2 "$H" "" ITEM-7 manual_verification pass https://example.invalid/run/7 lead-1
t wrong-arity           2 "$H" demoprod ITEM-8 manual_verification pass
RECS=$(find "$SANDBOX/records/uat" "$SANDBOX/records/restore-tests" -name '*.yaml' | wc -l | tr -d ' ')
EVTS=$(find "$SANDBOX/events" -name 'EVT-*.yaml' | wc -l | tr -d ' ')
if [ "$RECS" != "2" ]; then echo "RVR CASE FAIL record-count want=2 got=$RECS"; FAILED=$((FAILED+1)); else PASSED=$((PASSED+1)); fi
if [ "$EVTS" != "2" ]; then echo "RVR CASE FAIL event-count want=2 got=$EVTS"; FAILED=$((FAILED+1)); else PASSED=$((PASSED+1)); fi
rm -rf "$SANDBOX"
if [ "$FAILED" != "0" ]; then echo "RVR FAIL $PASSED passed $FAILED failed"; exit 1; fi
echo "RVR OK"
