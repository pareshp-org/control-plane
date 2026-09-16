#!/usr/bin/env bash
# access/tests/at-110-reconciler-bounds.sh
# AT-110 - spec 100.6. Lane 5 supplies the BOUNDING HARNESS only (EXT-2): the
# reconciler credential and reconciler/** belong to L3. The static half
# asserts the declared bound in Lane-5-owned configuration; the live half
# (six refusals plus one positive control) is ASSISTED and is executed by a
# named human.
set -uo pipefail
. access/tests/lib/assert.sh
INV=assets/inventory/machine-credential-reconciler.yaml
if [ ! -f "$INV" ]; then
  l5_indeterminate "AT-110/static" "PRE-K missing: $INV (spec 40.1, 49.1)"
  l5_exit
fi
for k in rotation_cadence rotator runbook behavioural_envelope envelope_alert_config_owner; do
  v="$(yq -r ".$k // \"\"" "$INV")"
  if [ -n "$v" ] && [ "$v" != "null" ]; then
    l5_pass "AT-110/static-$k"
  else
    l5_fail "AT-110/static-$k" "the reconciler credential entry declares no $k (spec 40.1)"
  fi
done
# Negative: no Lane 5 access declaration may grant the reconciler credential a
# write outside its Section 26.4 repair scope. The six AT-110 attempts name
# the forbidden surfaces; four of them are declared in Lane-5-owned files and
# are checked here.
SCOPE="$(grep -rniE 'reconciler' access/permission-model access/branch-protection access/secret-tiers \
         access/model access/secrets/tiers access/codeowners 2>/dev/null \
         | grep -Ei 'actions[_-]?secret|environment|workflow|org(anisation)?[_-]?settings|layer[_-]?b' || true)"
if [ -z "$SCOPE" ]; then
  l5_pass "AT-110/static-no-write-outside-repair-scope"
else
  l5_fail "AT-110/static-no-write-outside-repair-scope" "a Lane 5 declaration grants the reconciler a write outside Section 26.4 repair scope: $SCOPE"
fi
bash access/tests/lib/verify-evidence.sh AT-110
RC=$?
if [ "$RC" -eq 2 ]; then
  l5_indeterminate "AT-110/live" "awaiting human evidence"
elif [ "$RC" -eq 0 ]; then
  l5_pass "AT-110/live"
else
  l5_fail "AT-110/live" "evidence verification failed"
fi
l5_exit
