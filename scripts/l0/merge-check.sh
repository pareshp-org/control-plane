#!/usr/bin/env bash
# merge-check.sh — L0-03 merge train gate (FD-082 normalized)
# Usage: bash scripts/l0/merge-check.sh --branch <name> [--target main]
# CHK=ABSENT means the check wasn't run; ADMIT requires PASS (fixed: CHK=NONE was fail-open)
set -euo pipefail

BRANCH="${1:-}"
TARGET="${2:-main}"

while [[ $# -gt 0 ]]; do
  case $1 in
    --branch) BRANCH="$2"; shift 2;;
    --target) TARGET="$2"; shift 2;;
    *) shift;;
  esac
done

[[ -z "$BRANCH" ]] && { echo "Usage: $0 --branch <name> [--target main]"; exit 2; }

echo "=== Merge Train Gate: $BRANCH → $TARGET ==="

CHECKS_PASS=0
CHECKS_FAIL=0
CHK="ABSENT"

# Check 1: Branch exists
if git rev-parse --verify "$BRANCH" &>/dev/null; then
  echo "PASS: branch '$BRANCH' exists"
  CHECKS_PASS=$((CHECKS_PASS + 1))
else
  echo "FAIL: branch '$BRANCH' not found"
  CHECKS_FAIL=$((CHECKS_FAIL + 1))
fi

# Check 2: Actor gate
ALLOWED_ACTORS=("bendrohit-eng")
ACTOR="${GITHUB_ACTOR:-$(git config user.name 2>/dev/null || echo unknown)}"
ACTOR_ALLOWED=1
for allowed in "${ALLOWED_ACTORS[@]}"; do
  if [[ "${ACTOR,,}" == "${allowed,,}" ]]; then
    ACTOR_ALLOWED=0
    break
  fi
done
if [[ "$ACTOR_ALLOWED" -eq 0 ]]; then
  echo "PASS: actor '$ACTOR' is authorized"
  CHECKS_PASS=$((CHECKS_PASS + 1))
else
  echo "FAIL: actor '$ACTOR' is not in the authorized list: ${ALLOWED_ACTORS[*]}"
  CHECKS_FAIL=$((CHECKS_FAIL + 1))
fi

# Check 3: Canary
if bash scripts/canary-check.sh registries/people/_canary.yaml 2>/dev/null; then
  CHK="PASS"
  CHECKS_PASS=$((CHECKS_PASS + 1))
else
  CHK="FAIL"
  CHECKS_FAIL=$((CHECKS_FAIL + 1))
fi

echo ""
echo "CHK=$CHK"
if [[ "$CHK" == "PASS" && $CHECKS_FAIL -eq 0 ]]; then
  echo "ADMIT: $BRANCH → $TARGET"
  exit 0
elif [[ "$CHK" == "ABSENT" ]]; then
  echo "BLOCKED: CHK=ABSENT — ADMIT requires PASS (L0-03 fix: CHK=NONE was fail-open)"
  exit 1
else
  echo "BLOCKED: $CHECKS_FAIL check(s) failed, CHK=$CHK"
  exit 1
fi
