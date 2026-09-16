#!/usr/bin/env bash
# Executed negative tests for the human-only CODEOWNERS rule (Section 11.3).
# Section 98.2: "an approval from a machine account does NOT satisfy branch
# protection - CODEOWNERS is generated to contain human identities only, and the
# check is executed negatively." This script is that execution.
set -u
cd "$(git rev-parse --show-toplevel)"
GEN="access/codeowners/generate_codeowners.py"
FIX="access/testdata/codeowners"
PASS=0
FAIL=0

expect_exit () {  # expect_exit <label> <expected-code> <input-file>
  local label="$1" expected="$2" input="$3" rc
  python "$GEN" --org example-org --input "$input" >/dev/null 2>&1
  rc=$?
  if [ "$rc" -eq "$expected" ]; then
    PASS=$((PASS + 1))
  else
    echo "FAIL ${label}: expected exit ${expected}, got ${rc}"
    FAIL=$((FAIL + 1))
  fi
}

expect_exit "CO-1 valid human input emits"           0 "${FIX}/reference-input.json"
expect_exit "CO-2 bot login refused"                 2 "${FIX}/machine-login-input.json"
expect_exit "CO-3 non-human kind refused"            2 "${FIX}/machine-kind-input.json"
expect_exit "CO-4 named machine credential refused"  2 "${FIX}/named-credential-input.json"
expect_exit "CO-5 machine-shaped team slug refused"  2 "${FIX}/machine-team-input.json"

# CO-6: a refusal emits nothing at all on stdout.
OUT=$(python "$GEN" --org example-org --input "${FIX}/machine-login-input.json" 2>/dev/null || true)
if [ -z "$OUT" ]; then
  PASS=$((PASS + 1))
else
  echo "FAIL CO-6: a refusal wrote to stdout"; FAIL=$((FAIL + 1))
fi

# CO-7: a missing --org is an input error, never a guessed organisation.
python "$GEN" --input "${FIX}/reference-input.json" >/dev/null 2>&1
RC7=$?
if [ "$RC7" -eq 3 ]; then
  PASS=$((PASS + 1))
else
  echo "FAIL CO-7: missing --org exited ${RC7}, expected 3"; FAIL=$((FAIL + 1))
fi

# CO-8: the emitted file carries no machine identity of any refused shape.
HITS=$(python "$GEN" --org example-org --input "${FIX}/reference-input.json" \
       | grep -Eic 'bot\]|renovate|dependabot|github-actions|records-writer|reconciler' || true)
if [ "$HITS" = "0" ]; then
  PASS=$((PASS + 1))
else
  echo "FAIL CO-8: a machine identity appears in the emitted file"; FAIL=$((FAIL + 1))
fi

if [ "$FAIL" -ne 0 ]; then
  echo "CODEOWNERS-NEGATIVE-TESTS: FAIL (${FAIL} of $((PASS + FAIL)) cases)"
  exit 1
fi
echo "CODEOWNERS-NEGATIVE-TESTS: PASS (${PASS} cases)"
