#!/usr/bin/env bash
# Mutation: on gap close, skip re-running expiries whose end_date fell inside
# the gap window. Assignments that expired during the gap remain provisioned
# instead of being revoked on gap close.
# Expected result: IT-537-N3 flips from PASS to FAIL.
# Spec: protocol/03-invariant-tests.md §8.5 (MUTATION-NEEDED IT-537-N3).
set -euo pipefail
GAP_CLOSE="${FIXTURE_REPO_ROOT:?}/reconciler/gap-close.sh"
# Remove the expiry-replay loop that processes end_dates inside the gap window.
sed -i '/replay.*gap.*expir\|expir.*gap.*replay\|gap_window.*end_date\|end_date.*gap_window/Id' \
  "$GAP_CLOSE"
echo "IT-537-N3 mutation applied: gap-window expiry replay skipped in gap-close at $GAP_CLOSE"
