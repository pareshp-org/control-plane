#!/usr/bin/env bash
# Arming steps AO-01 and AO-02. Spec Section 11, Section 11.2, Section 98.2.
# Dry-run by default. --apply requires $ORG_LOGIN and an authenticated gh.
#
# Usage: apply-organisation.sh [--apply]
# Exit codes: 0 ok | 2 missing credentials in apply mode | 5 owner continuity unsatisfied
set -u
cd "$(git rev-parse --show-toplevel)"
APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1
ORG="${ORG_LOGIN:-ORG-LOGIN-NOT-SET}"

if [ "$APPLY" -eq 1 ]; then
  if [ "$ORG" = "ORG-LOGIN-NOT-SET" ]; then
    echo "APPLY-ORGANISATION: REFUSED - ORG_LOGIN is not set" >&2; exit 2
  fi
  gh auth status >/dev/null 2>&1 || {
    echo "APPLY-ORGANISATION: REFUSED - gh is not authenticated" >&2; exit 2; }
fi

CALLS=0
run () {  # run <gh args...>
  CALLS=$((CALLS + 1))
  if [ "$APPLY" -eq 1 ]; then
    echo "APPLY $*"
    "$@"
  else
    echo "DRY-RUN $*"
  fi
}

# Base permission Read (Section 11.2).
run gh api -X PATCH "/orgs/${ORG}" -f default_repository_permission=read
# Organisation-enforced two-factor authentication (Section 11.2, D53).
run gh api -X PATCH "/orgs/${ORG}" -F two_factor_requirement_enabled=true
# No machine approval satisfies a gate (D53): Actions may not approve pull requests.
run gh api -X PUT "/orgs/${ORG}/actions/permissions/workflow" -F can_approve_pull_request_reviews=false

# AO-02 - owner continuity. Section 98.2 makes this a Phase 1 completion condition.
CALLS=$((CALLS + 1))
if [ "$APPLY" -eq 1 ]; then
  OWNERS=$(gh api --paginate "/orgs/${ORG}/members?role=admin" --jq 'length' | awk '{s+=$1} END {print s+0}')
  echo "APPLY owner count = ${OWNERS}"
  if [ "${OWNERS}" -lt 2 ] && [ "${ESCROW_ATTESTED:-no}" != "yes" ]; then
    echo "APPLY-ORGANISATION: REFUSED - one organisation Owner and no attested" >&2
    echo "  escrowed break-glass Owner credential. Section 98.2 makes a second" >&2
    echo "  Owner or an escrowed credential with a named escrow custodian a" >&2
    echo "  Phase 1 completion condition; the consolidation week is when" >&2
    echo "  total-loss exposure peaks." >&2
    exit 5
  fi
else
  echo "DRY-RUN gh api --paginate /orgs/${ORG}/members?role=admin  # owner continuity, AO-02"
fi

if [ "$APPLY" -eq 1 ]; then
  echo "APPLY-ORGANISATION: APPLIED (${CALLS} calls)"
else
  echo "APPLY-ORGANISATION: DRY-RUN COMPLETE (${CALLS} calls)"
fi
