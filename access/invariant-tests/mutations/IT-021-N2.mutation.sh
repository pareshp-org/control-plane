#!/usr/bin/env bash
# Mutation: remove the Code-Owner-approval requirement from the fixture branch
# protection on the default branch so a flagged-unattended PR can merge without
# the full human gate sequence (Code Owner approval on the most recent push).
# Expected result: IT-021-N2 flips from PASS to FAIL.
# Spec: protocol/03-invariant-tests.md §6.5 (MUTATION-NEEDED IT-021-N2).
set -euo pipefail
REPO="${FIXTURE_REPO:?}"
# Disable require_code_owner_reviews on the default branch protection rule.
gh api --method PATCH \
  "repos/${REPO}/branches/main/protection/required_pull_request_reviews" \
  --field require_code_owner_reviews=false
echo "IT-021-N2 mutation applied: Code-Owner-approval requirement removed from PR gate in ${REPO}"
