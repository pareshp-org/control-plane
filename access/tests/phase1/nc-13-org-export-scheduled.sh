#!/usr/bin/env bash
# access/tests/phase1/nc-13-org-export-scheduled.sh
# NC-13 - spec 98.2 Phase 1: the organisation export's first run is scheduled
# in Phase 2 via a systemd timer, OR its absence is recorded as a dated
# accepted risk (D80). Exactly one of the two must hold. Feeds SIG-34
# (organisation export staleness).
# ops-vm/systemd/org-export.timer is the real artifact L5-04 writes (verified
# on disk at the time this check was written; the runbook's earlier draft
# named a different, unwritten path -- ops-vm/org-export/schedule.yaml --
# per lanes/L5-98-DEEP-REVIEW.md B-05).
set -uo pipefail
. access/tests/lib/assert.sh
SCHED=0
RISK=0
if [ -f ops-vm/systemd/org-export.timer ] && [ -s ops-vm/systemd/org-export.timer ]; then
  SCHED=1
fi
if [ -f access/accepted-risks/org-export-absent.yaml ]; then
  D2="$(yq -r '.review_on // ""' access/accepted-risks/org-export-absent.yaml)"
  O2="$(yq -r '.owner // ""' access/accepted-risks/org-export-absent.yaml)"
  case "$D2" in ????-??-??) [ -n "$O2" ] && RISK=1 ;; esac
fi
TOTAL=$((SCHED + RISK))
if [ "$TOTAL" -eq 1 ]; then
  l5_pass "NC-13"
elif [ "$TOTAL" -eq 0 ]; then
  l5_fail "NC-13" "neither ops-vm/systemd/org-export.timer nor a dated owned accepted risk exists"
else
  l5_fail "NC-13" "both a scheduled export (timer) and an accepted risk for its absence exist"
fi
l5_exit
