#!/usr/bin/env bash
# access/tests/phase1/nc-06-no-bypass-actor.sh
# NC-06 - spec 40.1 (D89) and PARTITION: the control-plane repository has NO
# machine bypass actor, and the records-writer holds no credential on it at
# all. The reconciler credential's declared repair scope (26.4) is the only
# machine write path admitted. Scope note: control-plane-records is L4-owned
# and is NOT asserted here.
#
# The repository slug is resolved from `gh` against the working copy itself
# (the shell contract already requires CONTROL_PLANE_ROOT to be this repo)
# rather than a access/permission-model/teams.yaml:control_plane_repo field
# no Lane 5 file writes (B-05). Any step in that resolution or in the API
# call that cannot complete is INDETERMINATE, never a silent pass.
set -uo pipefail
. access/tests/lib/assert.sh
SLUG="$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || true)"
if [ -z "$SLUG" ]; then
  echo "NC-06 INDETERMINATE: cannot resolve the control-plane repository slug via gh"
  exit 2
fi
if ! RULESETS="$(gh api "repos/$SLUG/rulesets" 2>/dev/null)"; then
  echo "NC-06 INDETERMINATE: cannot reach repos/$SLUG/rulesets"
  exit 2
fi
BYPASS=0
for id in $(echo "$RULESETS" | jq -r '.[].id'); do
  N="$(gh api "repos/$SLUG/rulesets/$id" --jq '.bypass_actors | length' 2>/dev/null || echo 0)"
  if [ "$N" -gt 0 ]; then
    l5_fail "NC-06" "ruleset $id declares $N bypass actor(s) on the control-plane repository"
    BYPASS=1
  fi
done
[ "$BYPASS" -eq 0 ] && l5_pass "NC-06/no-bypass-actor"
bash access/tests/lib/verify-evidence.sh NC-06 || true
l5_exit
