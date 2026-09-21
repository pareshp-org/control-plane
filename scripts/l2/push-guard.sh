#!/usr/bin/env bash
# scripts/l2/push-guard.sh — Pre-push guard for L2 CI/CD lane.
# Blocks push if concordance or validator fails.
# Usage: bash scripts/l2/push-guard.sh
# Install: cp scripts/l2/push-guard.sh .git/hooks/pre-push && chmod +x .git/hooks/pre-push
set -uo pipefail

IMPL_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== L2 Push Guard ==="

# Block if actor is not authorized
ACTOR="${GITHUB_ACTOR:-$(git config user.name || echo unknown)}"
ALLOWED="bendrohit-eng"
if [[ "$ACTOR" != "$ALLOWED" ]]; then
    echo "BLOCK: actor '$ACTOR' is not in the authorized push list (FD-083)"
    echo "       Authorized: $ALLOWED"
    exit 1
fi

# Run gate check
bash "$IMPL_ROOT/scripts/l2/gate-check.sh" || exit 1

echo "=== Push guard PASSED ==="
