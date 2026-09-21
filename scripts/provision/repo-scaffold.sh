#!/usr/bin/env bash
# repo-scaffold.sh — scaffold a standard product repo structure (L3-04, FD-087)
# Usage: bash scripts/provision/repo-scaffold.sh --product-id <id> --mode dry|apply
set -euo pipefail

PRODUCT_ID=""
MODE="dry"

while [[ $# -gt 0 ]]; do
  case $1 in
    --product-id) PRODUCT_ID="$2"; shift 2;;
    --mode) MODE="$2"; shift 2;;
    *) shift;;
  esac
done

[[ -z "$PRODUCT_ID" ]] && { echo "Usage: $0 --product-id <id> [--mode dry|apply]"; exit 2; }

SCAFFOLD_DIRS=(
  "src/"
  "tests/"
  "docs/"
  ".github/workflows/"
)

echo "=== Repo Scaffold: $PRODUCT_ID (mode=$MODE) ==="
for D in "${SCAFFOLD_DIRS[@]}"; do
  if [[ "$MODE" == "apply" ]]; then
    mkdir -p "records/products/${PRODUCT_ID}/${D}"
    echo "Created: records/products/${PRODUCT_ID}/${D}"
  else
    echo "[DRY-RUN] Would create: ${PRODUCT_ID}/${D}"
  fi
done
