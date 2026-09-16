#!/usr/bin/env bash
# Quarterly control-plane rebuild drill (Sections 45.4, 51.2, 51.5).
# Order matters and is not an implementation choice:
#   1. stop the VM and verify the off-VM legs fire (Section 51.5)
#   2. rebuild from the manifest, executed as written (Section 45.4) -- the
#      manifest is ops-vm/rebuild/runbook.src.md (L5-04-16), checked against
#      infra/hosts/ops-vm.yaml's rebuild_target_hours by
#      ops-vm/tools/rebuild_clock.py; this script never re-types that number.
#   3. the Layer B restore is performed by a human, never by this script
#   4. verify the clock, the legs and the zero-resources evidence
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
REC="${1:?usage: drill.sh <drill-record.yaml>}"
require_file "$REC"
require_env DRILL_VM_STOP_CMD DRILL_VM_START_CMD

log "drill: stopping the operations VM - the legs are verified by stopping it, not by rebuilding it"
$DRILL_VM_STOP_CMD
log "drill: the VM is stopped; both off-VM legs must now fire off this host"
$DRILL_VM_START_CMD

log "drill: rebuilding from the manifest, executed as written"
python3 ops-vm/tools/rebuild_clock.py --validate ops-vm/rebuild/runbook.src.md \
  || fail_closed "rebuild runbook did not validate; a step the runbook omits is a test failure, not an operator improvisation (Section 45.4)"

ops-vm/checks/drill-offvm-legs-fired.sh "$REC"
ops-vm/checks/drill-clock.sh "$REC"
ops-vm/checks/drill-zero-resources.sh "$REC"
record_run rebuild-drill ok "record=$REC"
echo "DRILL: PASS"
