#!/usr/bin/env bash
# notify/tests/at-106-gate1-push.sh
# AT-106 (push-event leg) - spec 100.4 and 92.11. Lane 5 owns subsystem R, the
# routing contract. This test asserts the closed push list: Gate 1 is on it,
# the destination is configuration rather than a literal, the breach route
# and the re-request route are declared, and an event that is not on the
# list resolves to nothing.
#
# notify/** is now real, richer than the runbook's draft single
# push-list.yaml (lanes/L5-98-DEEP-REVIEW.md B-05): one route file per event
# under notify/routing/<route-id>.yaml, enforced by notify/check_push_list.py
# and resolved at runtime by notify/route.py. This test exercises those real
# tools and the real gate-1-submission.yaml route rather than grepping a
# file no task writes.
set -uo pipefail
. access/tests/lib/assert.sh
ROUTE=notify/routing/gate-1-submission.yaml
GUARD=notify/check_push_list.py
RESOLVER=notify/route.py
if [ ! -f "$ROUTE" ]; then l5_indeterminate "AT-106" "PRE-L missing: $ROUTE"; l5_exit; fi
if [ ! -f "$GUARD" ]; then l5_indeterminate "AT-106" "closed-list guard missing: $GUARD"; l5_exit; fi
if [ ! -f "$RESOLVER" ]; then l5_indeterminate "AT-106" "route resolver missing: $RESOLVER"; l5_exit; fi
command -v python3 >/dev/null 2>&1 && PY=python3 || PY=python

PUSH_CLASS="$(yq -r '.push_class // ""' "$ROUTE")"
if [ "$PUSH_CLASS" = "gate_1_submission" ]; then
  l5_pass "AT-106/gate-1-on-push-list"
else
  l5_fail "AT-106/gate-1-on-push-list" "gate-1-submission.yaml's push_class is '$PUSH_CLASS', expected gate_1_submission (spec 92.11)"
fi

if "$PY" "$GUARD" 2>&1 | grep -qF 'PUSH-LIST: PASS'; then
  l5_pass "AT-106/list-declares-itself-closed"
else
  l5_fail "AT-106/list-declares-itself-closed" "the closed-list guard does not report PUSH-LIST: PASS"
fi

BREACH="$(yq -r '.turnaround_breach_action // ""' "$ROUTE")"
if echo "$BREACH" | grep -qi 'escalation'; then
  l5_pass "AT-106/breach-routes-to-escalation-role"
else
  l5_fail "AT-106/breach-routes-to-escalation-role" "no escalation-role route for a breached turnaround target (AT-106)"
fi

REROUTE="$(yq -r '.reroute_targets // ""' "$ROUTE")"
if echo "$REROUTE" | grep -qF 'plan_approval_delegate'; then
  l5_pass "AT-106/re-request-route"
else
  l5_fail "AT-106/re-request-route" "the re-request route to an active plan_approval_delegate is not declared (AT-106)"
fi

# Negative 1: the destination is a configuration value, never a hard-coded one.
l5_refuses "AT-106/no-hard-coded-destination" "a literal webhook URL in the gate-1 route" \
  grep -Eq 'https?://' "$ROUTE"

# Negative 2: the list is closed - an event absent from it resolves to nothing.
if "$PY" "$RESOLVER" --event-type lane5_not_a_real_event >/dev/null 2>&1; then
  l5_fail "AT-106/closed-list" "an event absent from the push list resolved a destination"
else
  l5_pass "AT-106/closed-list"
fi
l5_exit
