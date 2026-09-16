#!/usr/bin/env bash
# The subsystem-F negative-test suite. Section 95.4: a check that has never been
# shown to fail is not a check.
#
# Every case below asserts an EXIT CODE, not a log line, so a reworded message
# never silently turns a failing case into a passing one.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
F="$HERE/fixtures"
M="$F/map.fixture.yaml"
D="sha256:aaaa000000000000000000000000000000000000000000000000000000000001"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PASS=0; FAIL=0

check() {   # check <name> <expected-rc> <command...>
  local name="$1" want="$2"; shift 2
  "$@" > "$WORK/out.txt" 2>&1
  local got=$?
  if [ "$got" = "$want" ]; then
    printf 'PASS %-42s rc=%s\n' "$name" "$got"; PASS=$((PASS+1))
  else
    printf 'FAIL %-42s want=%s got=%s\n' "$name" "$want" "$got"; sed 's/^/     | /' "$WORK/out.txt"; FAIL=$((FAIL+1))
  fi
}

# --- the eleven-question assembler (Section 32) ------------------------------
check "query/closed-chain-closes"        0 "$HERE/evidence-query" --map "$M" \
  --records "$F/closed" --observations "$F/closed/observations.jsonl" \
  --platform "$F/closed/platform.yaml" --product fixture-product --digest "$D"
check "query/missing-approval-opens"     1 "$HERE/evidence-query" --map "$M" \
  --records "$F/broken-missing-approval" --observations "$F/closed/observations.jsonl" \
  --platform "$F/closed/platform.yaml" --product fixture-product --digest "$D"
check "query/digest-mismatch-opens"      1 "$HERE/evidence-query" --map "$M" \
  --records "$F/broken-digest-mismatch" --observations "$F/broken-digest-mismatch/observations.jsonl" \
  --platform "$F/closed/platform.yaml" --product fixture-product --digest "$D"

# --- the sweep (Section 99.2 line 9215) --------------------------------------
check "sweep/clean-estate"               0 "$HERE/verify-digest-chain" \
  --records "$F/closed" --observations "$F/closed/observations.jsonl" \
  --findings-out "$WORK/f1.json"
check "sweep/digest-mismatch-blocks"     3 "$HERE/verify-digest-chain" \
  --records "$F/broken-digest-mismatch" --observations "$F/broken-digest-mismatch/observations.jsonl" \
  --findings-out "$WORK/f2.json"
check "sweep/self-approved-blocks"       3 "$HERE/verify-digest-chain" \
  --records "$F/broken-self-approved" --observations "$F/closed/observations.jsonl" \
  --findings-out "$WORK/f3.json"
check "sweep/missing-approval-blocks"    3 "$HERE/verify-digest-chain" \
  --records "$F/broken-missing-approval" --observations "$F/closed/observations.jsonl" \
  --findings-out "$WORK/f4.json"
: > "$WORK/empty.jsonl"
check "sweep/zero-observations-is-error" 2 "$HERE/verify-digest-chain" \
  --records "$F/closed" --observations "$WORK/empty.jsonl" --findings-out "$WORK/f5.json"

# --- the seeded canary (Section 53.1 line 4680) ------------------------------
check "canary/must-be-found"             3 "$HERE/verify-digest-chain" \
  --records "$HERE/canary/records" --observations "$HERE/canary/observations.jsonl" \
  --findings-out "$WORK/f6.json"

# --- the collector (Section 41.2) --------------------------------------------
check "collect/strict-flags-unobserved"  4 env EV_FETCH="$F/stub-fetch.sh" \
  "$HERE/collect-version.sh" --targets "$F/targets.fixture.yaml" \
  --out "$WORK/obs.jsonl" --strict
check "collect/no-digest-field-refused"  2 env EV_FETCH="$F/stub-fetch.sh" \
  "$HERE/collect-version.sh" --targets "$F/targets-no-field.fixture.yaml" \
  --out "$WORK/obs2.jsonl"

# --- the gate (Section 46.1 line 4126; Section 53.2 line 4697) ---------------
check "gate/clean-permits"               0 "$HERE/deploy-gate.sh" --mode deploy \
  --records "$F/closed" --observations "$F/closed/observations.jsonl" --product fixture-product
check "gate/mismatch-blocks"             3 "$HERE/deploy-gate.sh" --mode deploy \
  --records "$F/broken-digest-mismatch" --observations "$F/broken-digest-mismatch/observations.jsonl" \
  --product fixture-product
check "gate/broken-sweep-blocks"         3 "$HERE/deploy-gate.sh" --mode deploy \
  --records "$WORK/does-not-exist" --observations "$F/closed/observations.jsonl" \
  --product fixture-product

# --- the escalation (Section 92.11 line 8276) --------------------------------
check "escalate/clean-does-nothing"      0 "$HERE/escalate-digest-mismatch.sh" \
  --findings "$WORK/f1.json" --event-types "$F/event-types.fixture.yaml" \
  --event-id EVT-2026-01-05-000020 --actor selftest \
  --run-url https://example.invalid/runs/selftest --out-dir "$WORK/esc"
check "escalate/mismatch-escalates"      3 "$HERE/escalate-digest-mismatch.sh" \
  --findings "$WORK/f2.json" --event-types "$F/event-types.fixture.yaml" \
  --event-id EVT-2026-01-05-000021 --actor selftest \
  --run-url https://example.invalid/runs/selftest --out-dir "$WORK/esc"

printf 'SELFTEST pass=%d fail=%d\n' "$PASS" "$FAIL"
if [ "$FAIL" != "0" ]; then echo "SELFTEST_FAIL"; exit 1; fi
if [ "$PASS" != "16" ]; then echo "SELFTEST_CASE_COUNT_CHANGED pass=$PASS"; exit 1; fi
echo "SELFTEST_PASS"
