#!/usr/bin/env bash
# Mutation: grant the unattended personal-agent identity direct-push permission
# on the fixture's default branch by removing the branch-protection rule that
# blocks non-admin direct pushes to the default branch.
# Expected result: IT-021-N1 flips from PASS to FAIL.
# Spec: protocol/03-invariant-tests.md §6.5 (MUTATION-NEEDED IT-021-N1).
set -euo pipefail
REPO="${FIXTURE_REPO:?}"
# Remove the required pull-request-reviews restriction so direct pushes are
# permitted. Also disable enforce_admins so the unattended identity can push.
gh api --method PUT \
  "repos/${REPO}/branches/main/protection" \
  --field required_status_checks=null \
  --field enforce_admins=false \
  --field required_pull_request_reviews=null \
  --field restrictions=null
echo "IT-021-N1 mutation applied: direct-push to default branch now permitted for unattended identity in ${REPO}"
