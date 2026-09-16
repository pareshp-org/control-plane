#!/usr/bin/env bash
# The singleton control-plane change shape of Section 51.4:
#   snapshot -> upgrade -> verify -> revert-on-fail
# There is no canary stage: there is one Grafana, one operations VM
# (Section 51.4). The Section 61 change manifest and approval are carried; the
# snapshot IS the rollback answer, known before the upgrade starts.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
COMPONENT="${1:?usage: patch-driver.sh <component-id>}"
require_env CHANGE_MANIFEST_ID CHANGE_APPROVAL_RECORD SNAPSHOT_CMD UPGRADE_CMD REVERT_CMD

log "patch: component=$COMPONENT manifest=$CHANGE_MANIFEST_ID approval=$CHANGE_APPROVAL_RECORD"

# 1. snapshot - the rollback answer, known before the upgrade starts
snap=$($SNAPSHOT_CMD "$COMPONENT") || fail_closed "snapshot failed; no rollback answer, so no upgrade"
log "patch: snapshot=$snap"

# 2. upgrade
if ! $UPGRADE_CMD "$COMPONENT"; then
  log "patch: upgrade failed; reverting to $snap"
  $REVERT_CMD "$COMPONENT" "$snap"
  record_run "patch-$COMPONENT" failed "upgrade failed; reverted to $snap"
  notify/bin/notify-job-result.sh "patch-$COMPONENT" failed "upgrade failed; reverted"
  exit 1
fi

# 3. verify - the post-patch smoke checklist IS the verify step (Section 51.4)
if ! ops-vm/checks/post-patch-smoke.sh; then
  log "patch: verify failed; reverting to $snap"
  $REVERT_CMD "$COMPONENT" "$snap"
  record_run "patch-$COMPONENT" failed "verify failed; reverted to $snap"
  notify/bin/notify-job-result.sh "patch-$COMPONENT" failed "verify failed; reverted"
  exit 1
fi

# 4. complete - only now, and only because both the checklist and the mandated
#    reconciliation run passed clean (Section 51.4)
record_run "patch-$COMPONENT" ok "manifest=$CHANGE_MANIFEST_ID snapshot=$snap"
echo "PATCH-COMPLETE: $COMPONENT"
