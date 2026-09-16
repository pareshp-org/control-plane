#!/usr/bin/env bash
# rename-product-workflow.sh — rename P<N> placeholder to real product ID
# Usage: bash scripts/l0/rename-product-workflow.sh --from P1 --to myproduct --name "My Product"
# (works from any invocation cwd — all paths below are resolved relative to
# the implementation root, this script's own location via BASH_SOURCE, not
# the caller's cwd)
set -euo pipefail

IMPL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$IMPL_ROOT"

FROM=""
TO=""
NAME=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --from) FROM="$2"; shift 2;;
    --to) TO="$2"; shift 2;;
    --name) NAME="$2"; shift 2;;
    *) shift;;
  esac
done

[[ -z "$FROM" || -z "$TO" || -z "$NAME" ]] && {
  echo "Usage: $0 --from P1 --to <product-id> --name '<Product Name>'"
  exit 2
}

TEMPLATE=".github/workflows/product-template.yml"
FROM_FILE=".github/workflows/product-${FROM}.yml"
TO_FILE=".github/workflows/product-${TO}.yml"

echo "=== Rename Product Workflow: $FROM → $TO ($NAME) ==="

if [[ "$FROM_FILE" == "$TO_FILE" ]]; then
  echo "Error: --from and --to resolve to the same file ($FROM_FILE); nothing to rename."
  exit 2
fi

if [[ -f "$FROM_FILE" ]]; then
  cp "$TEMPLATE" "$TO_FILE"
  # Strip the template's always-false dispatch guard (see product-template.yml
  # header) and restore the real per-job `if` condition it documents inline.
  sed -i -E "s/^([[:space:]]*)if: false # TEMPLATE GUARD.*Real condition: (.*)\$/\1if: \2/" "$TO_FILE"
  # Drop the now-stale "TEMPLATE SAFETY GUARD" header block — it no longer
  # applies once the guard above has been lifted for this real product file.
  sed -i "/^#\$/,/^# in its place is preserved as a trailing comment on the same line)\.\$/d" "$TO_FILE"
  # Replace placeholders
  sed -i "s/PRODUCT_ID/${TO}/g" "$TO_FILE"
  sed -i "s/PRODUCT_NAME/${NAME}/g" "$TO_FILE"
  rm "$FROM_FILE"
  echo "Created: $TO_FILE"
  echo "Removed: $FROM_FILE"

  # Also update facts.tsv if it exists
  if [[ -f "facts.tsv" ]]; then
    sed -i "s/Product-${FROM#P}\\b/$NAME/g" facts.tsv
    echo "Updated: facts.tsv"
  fi
else
  echo "Source not found: $FROM_FILE"
  exit 1
fi
