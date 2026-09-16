#!/usr/bin/env bash
# access/layer-b/check-owned-roots.sh
# Fails if the branch/working tree changes any file outside the five roots
# L5 owns under the FROZEN partition contract (PARTITION.md rule 1).
#
# Usage: check-owned-roots.sh [BASE]
#   BASE defaults to origin/integration, the lane's PR-merge-target convention
#   assumed by lanes/L5-03-layer-b.md Section 1. This repository has no
#   "origin" remote and no "integration" branch - every L5 task in this
#   session commits directly to the repository's own trunk - so when BASE
#   does not resolve to a real commit, this script does not silently report
#   OK; it falls back to the actual question a pre-commit guard needs
#   answered here: every path currently staged for the next commit
#   (git add the task's files, then run this script, then commit).
set -euo pipefail
BASE="${1:-origin/integration}"
BAD=0

FILES=""
if git rev-parse --verify --quiet "${BASE}^{commit}" >/dev/null 2>&1; then
  FILES="$(git diff --name-only "${BASE}...HEAD" 2>/dev/null || git diff --name-only "${BASE}" HEAD)"
else
  # No integration ref in this repository (see usage note above). Check what
  # is staged for the next commit, not the whole working tree - unrelated
  # lanes routinely leave their own untracked scratch files lying around,
  # and those are not this guard's concern.
  FILES="$(git diff --name-only --cached)"
fi

while IFS= read -r f; do
  [ -n "$f" ] || continue
  case "$f" in
    access/*|infra/*|ops-vm/*|notify/*|assets/*) : ;;
    *) echo "FOREIGN_PATH $f"; BAD=1 ;;
  esac
done <<< "$FILES"

if [ "$BAD" -eq 0 ]; then echo "OWNED_ROOTS_OK"; else echo "OWNED_ROOTS_FAIL"; exit 1; fi
