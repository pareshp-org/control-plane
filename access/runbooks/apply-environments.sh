#!/usr/bin/env bash
# Arming step AO-06. Spec Section 33.4, Section 11.3 bullet BP-10.
# Every environment carries a deployment branch and tag policy. A repository
# with branch protection and no deployment branch policy holds production
# credentials behind nothing.
#
# Usage: apply-environments.sh [--release-tag-pattern PATTERN] [--apply]
# Exit codes: 0 ok | 2 missing credentials in apply mode
set -u
cd "$(git rev-parse --show-toplevel)"
APPLY=0
TAGS="v*"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --release-tag-pattern) shift; TAGS="${1:-v*}" ;;
    *) echo "usage: apply-environments.sh [--release-tag-pattern PATTERN] [--apply]" >&2; exit 2 ;;
  esac
  shift
done
ORG="${ORG_LOGIN:-ORG-LOGIN-NOT-SET}"
ENVIRONMENTS="development staging production"

if [ "$APPLY" -eq 0 ]; then
  for ENV in $ENVIRONMENTS; do
    python access/tools/render_environment_payload.py --environment "$ENV" \
      --default-branch DEFAULT --release-tag-pattern "$TAGS"
  done
  echo "DRY-RUN gh api --paginate /orgs/${ORG}/repos --jq .[].name   # Section 11"
  echo "APPLY-ENVIRONMENTS: DRY-RUN COMPLETE (3 environments)"
  exit 0
fi

[ "$ORG" != "ORG-LOGIN-NOT-SET" ] || {
  echo "APPLY-ENVIRONMENTS: REFUSED - ORG_LOGIN is not set" >&2; exit 2; }
gh auth status >/dev/null 2>&1 || {
  echo "APPLY-ENVIRONMENTS: REFUSED - gh is not authenticated" >&2; exit 2; }

COUNT=0
for REPO in $(gh api --paginate "/orgs/${ORG}/repos" --jq '.[].name'); do
  BRANCH=$(gh api "/repos/${ORG}/${REPO}" --jq '.default_branch')
  for ENV in $ENVIRONMENTS; do
    RENDERED=$(python access/tools/render_environment_payload.py --environment "$ENV" \
      --default-branch "$BRANCH" --release-tag-pattern "$TAGS")
    printf '%s' "$RENDERED" \
      | python -c "import json,sys;print(json.dumps(json.load(sys.stdin)['environment_payload']))" \
      | gh api -X PUT "/repos/${ORG}/${REPO}/environments/${ENV}" --input -
    printf '%s' "$RENDERED" \
      | python -c "import json,sys
for policy in json.load(sys.stdin)['deployment_branch_policies']:
    print(json.dumps(policy))" \
      | while read -r POLICY; do
          printf '%s' "$POLICY" | gh api -X POST \
            "/repos/${ORG}/${REPO}/environments/${ENV}/deployment-branch-policies" --input -
        done
    COUNT=$((COUNT + 1))
    echo "APPLY ${REPO}:${ENV}"
  done
done
echo "APPLY-ENVIRONMENTS: APPLIED (${COUNT} environments)"
