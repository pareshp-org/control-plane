#!/usr/bin/env bash
# Arming step AO-03. Spec Section 11.2, D101.
# Teams grant Write BEFORE branch protection is armed, from the Phase 1 interim
# assignment set. Membership is derived from the registries and arrives as a
# JSON input document; this script reads no registry (PARTITION rule 4).
#
# Usage: apply-teams.sh --input INPUT.json [--apply]
# Exit codes: 0 ok | 2 missing credentials in apply mode | 3 bad input
set -u
cd "$(git rev-parse --show-toplevel)"
APPLY=0
INPUT=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --input) shift; INPUT="${1:-}" ;;
    *) echo "usage: apply-teams.sh --input INPUT.json [--apply]" >&2; exit 3 ;;
  esac
  shift
done
[ -n "$INPUT" ] || { echo "APPLY-TEAMS: REFUSED - --input is required" >&2; exit 3; }
[ -f "$INPUT" ] || { echo "APPLY-TEAMS: REFUSED - input not found: $INPUT" >&2; exit 3; }
ORG="${ORG_LOGIN:-ORG-LOGIN-NOT-SET}"

if [ "$APPLY" -eq 1 ]; then
  [ "$ORG" != "ORG-LOGIN-NOT-SET" ] || {
    echo "APPLY-TEAMS: REFUSED - ORG_LOGIN is not set" >&2; exit 2; }
  gh auth status >/dev/null 2>&1 || {
    echo "APPLY-TEAMS: REFUSED - gh is not authenticated" >&2; exit 2; }
fi

SET=$(python -c "import json,sys;print(json.load(open(sys.argv[1]))['assignment_set'])" "$INPUT")
echo "assignment_set = ${SET}  (Phase 3 replaces the interim set - D101)"

GRANTS=$(python -c "
import json, sys
doc = json.load(open(sys.argv[1]))
for team in doc['teams']:
    for repo in team['repositories']:
        print('%s|%s|%s' % (team['slug'], team['permission'], repo))
" "$INPUT")

COUNT=0
while IFS='|' read -r SLUG PERM REPO; do
  [ -n "$SLUG" ] || continue
  COUNT=$((COUNT + 1))
  if [ "$APPLY" -eq 1 ]; then
    gh api -X PUT "/orgs/${ORG}/teams/${SLUG}/repos/${ORG}/${REPO}" -f permission="${PERM}"
    echo "APPLY team ${SLUG} -> ${REPO} (${PERM})"
  else
    echo "DRY-RUN gh api -X PUT /orgs/${ORG}/teams/${SLUG}/repos/${ORG}/${REPO} -f permission=${PERM}"
  fi
done <<EOT
${GRANTS}
EOT

if [ "$APPLY" -eq 1 ]; then
  echo "APPLY-TEAMS: APPLIED (${COUNT} grants)"
else
  echo "APPLY-TEAMS: DRY-RUN COMPLETE (${COUNT} grants)"
fi
