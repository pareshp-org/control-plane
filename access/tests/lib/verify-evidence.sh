#!/usr/bin/env bash
# access/tests/lib/verify-evidence.sh
# Verifies a human evidence file. AI executor runs this; it never writes
# evidence (Section 1.1).
#
# Identity separation ("The human's login must differ from the machine
# identity that committed the test") is checked login-to-login, via the
# GitHub API against the commit that last touched access/tests/ -- never by
# comparing a GitHub login to a local git commit e-mail address, which can
# match or fail to match either identity for reasons unrelated to who
# actually committed what. A comparison that cannot be resolved is reported
# INDETERMINATE, never treated as satisfied.
set -uo pipefail
CHECK_ID="${1:?usage: verify-evidence.sh CHECK_ID}"
F="$(ls -1 access/tests/evidence/${CHECK_ID}-*.json 2>/dev/null | sort | tail -n 1)"
[ -n "${F:-}" ] || { echo "INCOMPLETE $CHECK_ID :: no evidence file"; exit 2; }
for k in check_id result executed_by executed_at observed spec_clause revalidate_after_days; do
  v="$(jq -r --arg k "$k" '.[$k] // empty' "$F")"
  [ -n "$v" ] || { echo "FAIL $CHECK_ID :: evidence missing field $k"; exit 1; }
done
[ "$(jq -r .check_id "$F")" = "$CHECK_ID" ] || { echo "FAIL $CHECK_ID :: check_id mismatch"; exit 1; }
[ "$(jq -r .result "$F")" = "pass" ] || { echo "FAIL $CHECK_ID :: recorded result is not pass"; exit 1; }
HUMAN="$(jq -r .executed_by "$F")"

SHA="$(git log -1 --format=%H -- access/tests/ 2>/dev/null || true)"
if [ -z "$SHA" ]; then
  echo "INDETERMINATE $CHECK_ID :: cannot resolve the commit that last touched access/tests/"
  exit 2
fi
SLUG="$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || true)"
if [ -z "$SLUG" ]; then
  echo "INDETERMINATE $CHECK_ID :: cannot resolve the repository slug via gh -- identity separation is unverifiable and is never assumed satisfied"
  exit 2
fi
COMMITTER_LOGIN="$(gh api "repos/$SLUG/commits/$SHA" --jq '.author.login // empty' 2>/dev/null || true)"
if [ -z "$COMMITTER_LOGIN" ]; then
  echo "INDETERMINATE $CHECK_ID :: cannot resolve the committing GitHub login via the API -- identity separation is unverifiable"
  exit 2
fi
if [ "$COMMITTER_LOGIN" = "$HUMAN" ]; then
  echo "FAIL $CHECK_ID :: evidence author ($HUMAN) equals the GitHub login that committed the test"
  exit 1
fi

AGE_DAYS=$(( ( $(date -u +%s) - $(date -u -d "$(jq -r .executed_at "$F")" +%s) ) / 86400 ))
MAX="$(jq -r .revalidate_after_days "$F")"
[ "$AGE_DAYS" -le "$MAX" ] || { echo "INCOMPLETE $CHECK_ID :: evidence is ${AGE_DAYS}d old, limit ${MAX}d"; exit 2; }
echo "PASS $CHECK_ID"
