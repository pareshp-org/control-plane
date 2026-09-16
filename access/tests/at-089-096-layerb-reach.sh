#!/usr/bin/env bash
# access/tests/at-089-096-layerb-reach.sh
# AT-089, AT-092, AT-096 - spec 100.6, 90.2, 90.3; invariants 107, 108, 109.
# Verified in the declared permission matrix and the PROVISIONED
# configuration of the shared instance - never inferred from panel
# visibility (D75, spec 99.5).
#
# access/tests/at-096-no-peer-access.sh's live SSH-based clauses are already
# built by L5-03 at access/layer-b/at-096-no-peer-access.sh; this script
# integrates the declared-permission-matrix leg into the Lane 5
# coverage/evidence harness rather than duplicating that live check.
set -uo pipefail
. access/tests/lib/assert.sh
PM=access/model/permission-matrix.yaml
SHARED=ops-vm/grafana
if [ ! -f "$PM" ]; then l5_indeterminate "AT-089" "permission matrix absent: $PM (spec 90.2)"; l5_exit; fi
if [ ! -d "$SHARED/provisioning" ]; then l5_indeterminate "AT-089" "PRE-E missing: $SHARED/provisioning"; l5_exit; fi
GSR="$(yq -r '.general_surface_rule // ""' "$PM")"
if [ -n "$GSR" ] && [ "$GSR" != "null" ]; then
  l5_pass "AT-089/general-surface-rule"
else
  l5_fail "AT-089/general-surface-rule" "the matrix declares no general_surface_rule (invariant 109)"
fi
PERSONVAR="$(find "$SHARED" -type f -exec grep -vE '^[[:space:]]*#' {} + 2>/dev/null \
             | grep -niE '"name"[[:space:]]*:[[:space:]]*"(person|person_id|employee|employee_id)"' || true)"
if [ -z "$PERSONVAR" ]; then
  l5_pass "AT-089/no-per-person-drilldown"
else
  l5_fail "AT-089/no-per-person-drilldown" "shared instance declares a per-person variable: $PERSONVAR"
fi
ROW='.rows[] | select(.data_category == "Individual utilisation detail")'
TL="$(yq -r "$ROW | .team_lead // \"\"" "$PM")"
PEER="$(yq -r "$ROW | .peer // \"\"" "$PM")"
EMP="$(yq -r "$ROW | .employee // \"\"" "$PM")"
if [ "$TL" = "No" ]; then l5_pass "AT-092/team-lead-denied"; else l5_fail "AT-092/team-lead-denied" "matrix gives the Team Lead '$TL' on individual utilisation detail; spec 90.2 says No"; fi
if [ "$PEER" = "No" ]; then l5_pass "AT-096/peer-denied"; else l5_fail "AT-096/peer-denied" "matrix gives a peer '$PEER'; spec 90.2 says No"; fi
if [ "$EMP" = "Own only" ]; then l5_pass "AT-096/own-only"; else l5_fail "AT-096/own-only" "matrix gives an employee '$EMP'; spec 90.2 says Own only"; fi
l5_exit
