#!/usr/bin/env bash
# tools/records/test-deploy-emit.sh
# Master Spec v4.0 Section 97.2 line 8867 - required, failing steps, proved.
set -u
: "${CP_ROOT:?CP_ROOT not set}"; : "${CPR_ROOT:?CPR_ROOT not set}"
SANDBOX="$(mktemp -d)"
cp -R "$CPR_ROOT/." "$SANDBOX/"
export CPR_ROOT="$SANDBOX"
git -C "$SANDBOX" config user.email "records-writer@test.invalid"
git -C "$SANDBOX" config user.name "records-writer-test"
D="$CP_ROOT/tools/records/deploy-emit"
FAILED=0
FULL="digest=sha256:deadbeef approved_by=lead-1 approval_event=https://example.invalid/run/9 staging_verified=true uat_record=records/uat/UAT-x.yaml smoke_result=pass rollback_of=null"
# 1. Happy path writes exactly one record and one event, in one commit.
BEFORE_COMMITS=$(git -C "$SANDBOX" rev-list --count HEAD)
if ! $D record_production_deployed demoprod dev-1 ref $FULL >/dev/null 2>&1; then
  echo "DEPLOY CASE FAIL happy-path-nonzero"; FAILED=$((FAILED+1)); fi
RECS=$(find "$SANDBOX/records/deployments" -name 'DEP-*.yaml' | wc -l | tr -d ' ')
EVTS=$(find "$SANDBOX/events" -name 'EVT-*.yaml' | wc -l | tr -d ' ')
AFTER_COMMITS=$(git -C "$SANDBOX" rev-list --count HEAD)
[ "$RECS" = "1" ] || { echo "DEPLOY CASE FAIL record-count want=1 got=$RECS"; FAILED=$((FAILED+1)); }
[ "$EVTS" = "1" ] || { echo "DEPLOY CASE FAIL event-count want=1 got=$EVTS"; FAILED=$((FAILED+1)); }
[ "$((AFTER_COMMITS-BEFORE_COMMITS))" = "1" ] || { echo "DEPLOY CASE FAIL commit-count want=1 got=$((AFTER_COMMITS-BEFORE_COMMITS))"; FAILED=$((FAILED+1)); }
# 2. Store removed: the step must fail non-zero and write nothing.
mv "$SANDBOX/records/deployments" "$SANDBOX/records/deployments.hidden"
$D record_production_deployed demoprod dev-1 ref $FULL >/dev/null 2>&1
[ "$?" != "0" ] || { echo "DEPLOY CASE FAIL unwritable-store-returned-zero"; FAILED=$((FAILED+1)); }
mv "$SANDBOX/records/deployments.hidden" "$SANDBOX/records/deployments"
STRAY=$(git -C "$SANDBOX" status --porcelain | wc -l | tr -d ' ')
[ "$STRAY" = "0" ] || { echo "DEPLOY CASE FAIL residue-after-failure count=$STRAY"; FAILED=$((FAILED+1)); }
# 3. Unknown event type in the taxonomy path: the pair must roll back, no orphan record.
BEFORE_RECS=$(find "$SANDBOX/records/deployments" -name 'DEP-*.yaml' | wc -l | tr -d ' ')
CP_ROOT_SAVED="$CP_ROOT"
( export CP_ROOT="$(mktemp -d)"; mkdir -p "$CP_ROOT/metrics/taxonomy" "$CP_ROOT/schemas/records" "$CP_ROOT/tools/records"
  cp -R "$CP_ROOT_SAVED/tools/records/." "$CP_ROOT/tools/records/"
  cp -R "$CP_ROOT_SAVED/schemas/records/." "$CP_ROOT/schemas/records/" 2>/dev/null
  printf 'event_types: []\n' > "$CP_ROOT/metrics/taxonomy/event-types.yaml"
  "$CP_ROOT/tools/records/deploy-emit" record_production_deployed demoprod dev-1 ref $FULL >/dev/null 2>&1 ) 
AFTER_RECS=$(find "$SANDBOX/records/deployments" -name 'DEP-*.yaml' | wc -l | tr -d ' ')
[ "$BEFORE_RECS" = "$AFTER_RECS" ] || { echo "DEPLOY CASE FAIL orphan-record-after-event-failure"; FAILED=$((FAILED+1)); }
rm -rf "$SANDBOX"
if [ "$FAILED" != "0" ]; then echo "DEPLOY-EMIT FAIL $FAILED"; exit 1; fi
echo "DEPLOY-EMIT OK 6/6"
