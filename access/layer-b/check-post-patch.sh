#!/usr/bin/env bash
# access/layer-b/check-post-patch.sh
set -uo pipefail
FAILS=0
note() { echo "PP_FAIL $1"; FAILS=$((FAILS+1)); }

# The change shape has no canary stage and names the smoke script as verify.
[ "$(yq -r '.change_shape.canary_stage' infra/layer-b/patch-cadence.yaml)" = "false" ] \
  || note "the change shape declares a canary stage; the control plane has no canary set"
[ "$(yq -r '.change_shape.verify_step' infra/layer-b/patch-cadence.yaml)" = "ops-vm/layer-b/patch/post-patch-smoke.sh" ] \
  || note "the verify step does not name the smoke checklist"
[ "$(yq -r '.change_shape.steps | join(",")' infra/layer-b/patch-cadence.yaml)" = "snapshot,upgrade,verify,revert-on-fail" ] \
  || note "the change shape is not snapshot,upgrade,verify,revert-on-fail"

# Every component carries the elevated cadence and the expedited security path.
n=$(yq -r '[.components[] | select(.cadence == "tightest-in-stack" and .security_path == "expedited")] | length' infra/layer-b/patch-cadence.yaml)
[ "$n" = "3" ] || note "$n of 3 components carry the elevated cadence"

# Push discipline: exactly one Layer B route pushes, and it is the Blocking one.
p=$(grep -l '^push: true' notify/routes/layer-b-*.yaml | wc -l | tr -d ' ')
[ "$p" = "1" ] || note "$p Layer B routes declare push: true, expected 1"
[ "$(yq -r '.push_list_entry' notify/routes/layer-b-gate-red.yaml)" = "Blocking-class drift" ] \
  || note "the pushing route is not on the closed push list of Section 92.11"
[ "$(yq -r '.push' notify/routes/layer-b-patch-stale.yaml)" = "false" ] \
  || note "the Amber staleness route pages; Amber is not on the push list"

# No Layer B route may carry content.
for f in notify/routes/layer-b-*.yaml; do
  [ "$(yq -r '.prohibited_payload_fields | length' "$f")" -ge 2 ] \
    || note "$f does not prohibit Layer B content in its payload"
done

if [ "$FAILS" -eq 0 ]; then echo "POST_PATCH_DECL_OK 8/8"; else echo "POST_PATCH_DECL_FAILED $FAILS"; exit 1; fi
