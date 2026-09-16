#!/usr/bin/env bash
# deploy-gate.sh - fails closed while the evidence chain is not confirmed closed.
#
# Spec:
#   Section 53.2 line 4697 - Level 4, Block: "Fail CI or block the deployment
#     path until resolved." Artifact digest mismatch is a Level 4 row.
#   Section 46.1 line 4126 - "Completion of step 3 - the digest-vs-approval
#     verification, executed by the named build-surface script
#     verify-digest-chain - gates resumption of production deploys: nothing new
#     deploys until the evidence chain is confirmed closed."
#   Section 37.3 line 3268 - the three capabilities: production-approval,
#     incident-response, devops. This script READS the capability name from the
#     published contract; it never chooses one and never authorises one.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/lib/common.sh"
# This script's own runtime contract fixes every input-error refusal at
# exit 2, distinct from common.sh's generic exit 1 and from this script's
# own exit 3 (blocked). Redefined locally after sourcing, same fix as
# L2-T508 and L2-T512.
ev_die() { printf '%s %s: %s\n' "$EV_FAIL_PREFIX" "$1" "$2" >&2; exit 2; }

MODE=""; RECORDS=""; OBSERVATIONS=""; PRODUCT=""; CAPABILITY=""
CAP_CONTRACT="contracts/product/capabilities.yaml"
while [ $# -gt 0 ]; do
  case "$1" in
    --mode)                   MODE="${2:-}";         shift 2 ;;
    --records)                RECORDS="${2:-}";      shift 2 ;;
    --observations)           OBSERVATIONS="${2:-}"; shift 2 ;;
    --product)                PRODUCT="${2:-}";      shift 2 ;;
    --capability)             CAPABILITY="${2:-}";   shift 2 ;;
    --capabilities-contract)  CAP_CONTRACT="${2:-}"; shift 2 ;;
    *) ev_die "BAD_ARG" "unknown argument: $1" ;;
  esac
done
case "$MODE" in
  deploy|recovery) ;;
  *) ev_die "MODE_UNRECOGNISED" "--mode must be deploy or recovery" ;;
esac
[ -n "$RECORDS" ]      || ev_die "BAD_ARG" "--records is required"
[ -n "$OBSERVATIONS" ] || ev_die "BAD_ARG" "--observations is required"
ev_require_file "$OBSERVATIONS" "OBSERVATIONS_ABSENT"

if [ "$MODE" = "deploy" ]; then
  [ -n "$PRODUCT" ] || ev_die "BAD_ARG" "--product is required in deploy mode"
fi

if [ "$MODE" = "recovery" ]; then
  # Section 46.1: the escalation role owns the six recovery steps. The gate
  # refuses to run for a capability the contract does not publish.
  [ -n "$CAPABILITY" ] || ev_die "CAPABILITY_UNDECLARED" \
    "--capability is required in recovery mode (Section 37.3 line 3268)"
  ev_require_file "$CAP_CONTRACT" "CAPABILITIES_CONTRACT_ABSENT"
  grep -qE "(^|[^a-z-])${CAPABILITY}([^a-z-]|$)" "$CAP_CONTRACT" \
    || ev_die "CAPABILITY_UNPUBLISHED" \
       "$CAPABILITY is not published in $CAP_CONTRACT"
  # Recovery sweeps the estate. A per-product sweep would resume deploys on the
  # strength of one product's chain, which Section 46.1 does not permit.
  PRODUCT=""
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
ARGS=(--records "$RECORDS" --observations "$OBSERVATIONS" --findings-out "$TMP/findings.json")
if [ -n "$PRODUCT" ]; then ARGS+=(--product "$PRODUCT"); fi

set +e
"$HERE/verify-digest-chain" "${ARGS[@]}" > "$TMP/sweep.log" 2>&1
RC=$?
set -e
cat "$TMP/sweep.log"

case "$RC" in
  0)
    if [ "$MODE" = "deploy" ]; then ev_ok "DEPLOY_PERMITTED product=$PRODUCT";
    else ev_ok "RESUMPTION_PERMITTED capability=$CAPABILITY"; fi
    exit 0 ;;
  3)
    COUNT="$(python3 -c "import json;print(len(json.load(open('$TMP/findings.json'))['findings']))")"
    printf '%s DEPLOY_BLOCKED: Blocking-class drift, %s finding(s); Section 53.2 Level 4\n' \
      "$EV_FAIL_PREFIX" "$COUNT" >&2
    exit 3 ;;
  *)
    # A broken sweep is not a clean sweep (Section 53.1 line 4680).
    printf '%s DEPLOY_BLOCKED: sweep did not complete (rc=%s)\n' "$EV_FAIL_PREFIX" "$RC" >&2
    exit 3 ;;
esac
