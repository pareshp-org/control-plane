#!/usr/bin/env bash
# Arming steps AO-05 (unarmed) and AO-08 (armed). Spec Section 11.3,
# Section 95.2, Section 98.2, D101.
#
# The D101 gate is enforced here, twice:
#   1. check_arming_order.py must pass before anything is applied.
#   2. In apply mode with --profile armed, every repository must already have at
#      least one Team holding push, maintain or admin. Arming a
#      Code-Owner-and-approval gate on a repository where no Team holds Write
#      leaves nobody whose approval counts.
#
# Usage: apply-branch-protection.sh --profile {unarmed,armed}
#          [--contexts a,b] [--arming-config PATH] [--apply]
# Exit codes: 0 ok | 2 missing credentials | 3 no Team grants Write | 4 arming order rejected
set -u
cd "$(git rev-parse --show-toplevel)"
APPLY=0
PROFILE=""
CONTEXTS=""
ARMING_CONFIG="access/arming/arming-order.yaml"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --profile) shift; PROFILE="${1:-}" ;;
    --contexts) shift; CONTEXTS="${1:-}" ;;
    --arming-config) shift; ARMING_CONFIG="${1:-}" ;;
    *) echo "usage: apply-branch-protection.sh --profile {unarmed,armed} [--contexts a,b] [--arming-config PATH] [--apply]" >&2; exit 4 ;;
  esac
  shift
done
case "$PROFILE" in
  unarmed|armed) : ;;
  *) echo "APPLY-BRANCH-PROTECTION: REFUSED - --profile must be unarmed or armed" >&2; exit 4 ;;
esac

if ! python access/tools/check_arming_order.py --config "$ARMING_CONFIG" >/dev/null 2>&1; then
  echo "APPLY-BRANCH-PROTECTION: REFUSED - the declared arming order is unsatisfiable" >&2
  python access/tools/check_arming_order.py --config "$ARMING_CONFIG" >&2 || true
  exit 4
fi

PAYLOAD=$(python access/tools/render_protection_payload.py --profile "$PROFILE" --contexts "$CONTEXTS")
ORG="${ORG_LOGIN:-ORG-LOGIN-NOT-SET}"

if [ "$APPLY" -eq 0 ]; then
  echo "$PAYLOAD"
  echo "DRY-RUN gh api --paginate /orgs/${ORG}/repos --jq .[].name   # Section 11: never a hard-coded list"
  echo "DRY-RUN gh api -X PUT /repos/${ORG}/REPO/branches/DEFAULT/protection --input -"
  echo "APPLY-BRANCH-PROTECTION: DRY-RUN COMPLETE (profile=${PROFILE})"
  exit 0
fi

[ "$ORG" != "ORG-LOGIN-NOT-SET" ] || {
  echo "APPLY-BRANCH-PROTECTION: REFUSED - ORG_LOGIN is not set" >&2; exit 2; }
gh auth status >/dev/null 2>&1 || {
  echo "APPLY-BRANCH-PROTECTION: REFUSED - gh is not authenticated" >&2; exit 2; }

COUNT=0
for REPO in $(gh api --paginate "/orgs/${ORG}/repos" --jq '.[].name'); do
  if [ "$PROFILE" = "armed" ]; then
    WRITERS=$(gh api "/repos/${ORG}/${REPO}/teams" \
      --jq '[.[] | select(.permission=="push" or .permission=="maintain" or .permission=="admin")] | length')
    if [ "${WRITERS}" -eq 0 ]; then
      echo "APPLY-BRANCH-PROTECTION: REFUSED on ${REPO} - no Team holds Write." >&2
      echo "  Arming a Code-Owner-and-approval gate here leaves nobody whose" >&2
      echo "  approval counts (D101, Section 98.2). Run apply-teams.sh first." >&2
      exit 3
    fi
  fi
  BRANCH=$(gh api "/repos/${ORG}/${REPO}" --jq '.default_branch')
  printf '%s' "$PAYLOAD" | gh api -X PUT "/repos/${ORG}/${REPO}/branches/${BRANCH}/protection" --input -
  COUNT=$((COUNT + 1))
  echo "APPLY ${REPO}:${BRANCH} profile=${PROFILE}"
done
echo "APPLY-BRANCH-PROTECTION: APPLIED (${COUNT} repositories, profile=${PROFILE})"
