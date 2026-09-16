#!/usr/bin/env bash
# check-prerequisites.sh — Phase 0 pre-flight check (L3-04, FD-087)
# Usage: bash scripts/provision/check-prerequisites.sh (run from anywhere; paths
#        below are anchored to the repo root, not to the caller's cwd)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

PASS=0
FAIL=0

# Generic check: runs $CMD (only ever built from trusted, static text — never
# from a value that could contain shell metacharacters) and reports PASS/FAIL.
check() {
  local NAME="$1"; local CMD="$2"
  if eval "$CMD" &>/dev/null; then
    echo "PASS: $NAME"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $NAME"
    FAIL=$((FAIL + 1))
  fi
}

pass() { echo "PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAIL: $1"; FAIL=$((FAIL + 1)); }

echo "=== Phase 0 Prerequisites Check ==="
check "gh CLI installed"       "gh --version"

# GITHUB_TOKEN is untrusted, attacker-influenceable content (it can contain
# arbitrary characters, including shell metacharacters). Never let it pass
# through eval — compare it directly with a real [[ ]] test instead.
if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  pass "GITHUB_TOKEN set"
else
  fail "GITHUB_TOKEN set"
fi

check "gh auth valid"          "gh auth status"
check "git installed"          "git --version"

# bash 4+: verify the interpreter's OWN reported major version via
# BASH_VERSINFO. Merely checking that `bash --version` exits 0 only proves
# some bash exists — a bash 3.x would incorrectly PASS that check.
if [[ "${BASH_VERSINFO[0]}" -ge 4 ]]; then
  pass "bash 4+"
else
  fail "bash 4+ (detected bash ${BASH_VERSINFO[0]}.${BASH_VERSINFO[1]}.${BASH_VERSINFO[2]}, need 4.0.0+)"
fi

check "project-config.sh"      "test -f \"$ROOT_DIR/contracts/project-config.sh\""
check "run-phase-0.sh"         "test -f \"$ROOT_DIR/run-phase-0.sh\""
check "canary intact"          "bash \"$ROOT_DIR/scripts/canary-check.sh\" \"$ROOT_DIR/registries/people/_canary.yaml\""

echo ""
echo "Result: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]] && echo "READY to run Phase 0" || echo "Fix failures before running Phase 0"
[[ $FAIL -eq 0 ]]
