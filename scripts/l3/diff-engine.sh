#!/usr/bin/env bash
# diff-engine.sh — L3-01 diff engine (FD-087)
# Computes diffs between registry snapshots and records
# Usage: bash scripts/l3/diff-engine.sh [--from <date>] [--to <date>]
set -euo pipefail

FROM_DATE=""
TO_DATE="$(date +%Y-%m-%d)"

while [[ $# -gt 0 ]]; do
  case $1 in
    --from) FROM_DATE="$2"; shift 2;;
    --to) TO_DATE="$2"; shift 2;;
    *) shift;;
  esac
done

echo "=== L3-01 Diff Engine ==="
if [[ -z "$FROM_DATE" ]]; then
  echo "Period: (unset) → $TO_DATE"
else
  echo "Period: $FROM_DATE → $TO_DATE"
fi
echo ""

# Diff people registry changes
echo "People registry diff:"
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  echo "  No git repo"
elif git diff --quiet --exit-code -- "registries/people/" 2>/dev/null; then
  echo "  No changes"
else
  echo "  Changes detected (git diff for date range not available — use git log):"
  git diff --name-only -- "registries/people/" 2>/dev/null | sed 's/^/    /'
fi

# Diff records changes
echo ""
echo "Records diff:"
echo "  board/snapshot.yaml: $(wc -l < records/board/snapshot.yaml 2>/dev/null || echo 'N/A') lines"
echo "  work/open.yaml: $(wc -l < records/work/open.yaml 2>/dev/null || echo 'N/A') lines"
echo ""
echo "Note: Full diff engine implementation in L3 Phase 1 (L3-01 tasks)"
