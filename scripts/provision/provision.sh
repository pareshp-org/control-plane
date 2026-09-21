#!/usr/bin/env bash
# provision.sh — L3 provisioning CLI (L3-04, FD-087)
# Usage: bash scripts/provision/provision.sh <command> [options]
# Commands: create-product, list-products, check-product
# Mode: --mode dry|apply (default: dry — safe during bootstrap)
set -euo pipefail

CONFIG="$(dirname "$0")/../../contracts/project-config.sh"
if [[ ! -f "$CONFIG" ]]; then
  echo "ERROR: $CONFIG not found. provision.sh requires contracts/project-config.sh (exports ORG and check_org())." >&2
  exit 1
fi
# shellcheck source=/dev/null
source "$CONFIG"
check_org

COMMAND="${1:-help}"
MODE="dry"
PRODUCT_ID=""
PRODUCT_NAME=""
REPO_NAME=""

shift || true
while [[ $# -gt 0 ]]; do
  case $1 in
    --mode) MODE="$2"; shift 2;;
    --product-id) PRODUCT_ID="$2"; shift 2;;
    --product-name) PRODUCT_NAME="$2"; shift 2;;
    --repo) REPO_NAME="$2"; shift 2;;
    *) shift;;
  esac
done

run_live() {
  if [[ "$MODE" == "apply" ]]; then
    echo "[APPLY] $*"
    eval "$*"
  else
    echo "[DRY-RUN] Would run: $*"
  fi
}

case "$COMMAND" in
  create-product)
    [[ -z "$PRODUCT_ID" || -z "$PRODUCT_NAME" ]] && {
      echo "Usage: provision create-product --product-id <id> --product-name <name> --mode dry|apply"
      exit 2
    }
    echo "=== Create Product: $PRODUCT_ID ($PRODUCT_NAME) ==="

    # Step 1: Create product record (DRY-safe)
    RECORD_FILE="records/products/${PRODUCT_ID}.yaml"
    if [[ "$MODE" == "apply" ]]; then
      mkdir -p records/products
      cat > "$RECORD_FILE" <<EOF
id: "$PRODUCT_ID"
name: "$PRODUCT_NAME"
created: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
status: "bootstrapping"
EOF
      echo "Created: $RECORD_FILE"
    else
      echo "[DRY-RUN] Would create: $RECORD_FILE"
    fi

    # Step 2: Create capability entry (DRY-safe)
    CAP_FILE="registries/capabilities/${PRODUCT_ID}.yaml"
    if [[ "$MODE" == "apply" ]]; then
      mkdir -p registries/capabilities
      cat > "$CAP_FILE" <<EOF
id: "CAP-$(printf '%04d' $RANDOM)"
name: "$PRODUCT_NAME"
owner_lane: "L3"
status: "planned"
EOF
      echo "Created: $CAP_FILE"
    else
      echo "[DRY-RUN] Would create: $CAP_FILE"
    fi

    # Step 3: Create GitHub repo (LIVE - requires GITHUB_TOKEN)
    # This is L3-04-13 LIVE task — do not run during bootstrap without explicit --mode apply
    if [[ "$MODE" == "apply" ]]; then
      echo "WARNING: Creating live GitHub repo requires GITHUB_TOKEN"
      run_live "gh repo create ${ORG:-pareshp-org}/${REPO_NAME:-$PRODUCT_ID} --public --description '$PRODUCT_NAME product repo'"
    else
      echo "[DRY-RUN] Would create GitHub repo: ${ORG:-pareshp-org}/${REPO_NAME:-$PRODUCT_ID}"
    fi

    echo "Done: create-product $PRODUCT_ID (mode=$MODE)"
    ;;

  list-products)
    echo "=== Product List ==="
    shopt -s nullglob
    PRODUCT_FILES=(records/products/*.yaml)
    shopt -u nullglob
    if [[ ${#PRODUCT_FILES[@]} -eq 0 ]]; then
      echo "(no products yet)"
    else
      for f in "${PRODUCT_FILES[@]}"; do
        echo "  $(basename "$f" .yaml)"
      done
    fi
    ;;

  check-product)
    [[ -z "$PRODUCT_ID" ]] && { echo "Usage: provision check-product --product-id <id>"; exit 2; }
    RECORD_FILE="records/products/${PRODUCT_ID}.yaml"
    if [[ -f "$RECORD_FILE" ]]; then
      echo "FOUND: $RECORD_FILE"
      cat "$RECORD_FILE"
    else
      echo "NOT FOUND: $RECORD_FILE"
      exit 1
    fi
    ;;

  help)
    echo "L3 Provisioning CLI (FD-087)"
    echo ""
    echo "Commands:"
    echo "  create-product --product-id <id> --product-name <name> [--repo <name>] --mode dry|apply"
    echo "  list-products"
    echo "  check-product --product-id <id>"
    echo ""
    echo "Mode: 'dry' (default) is safe during bootstrap. 'apply' makes live changes."
    echo "See L3-04-provisioning.md for task breakdown (L3-04-13 is the only LIVE task)."
    ;;

  *)
    echo "ERROR: Unknown command: $COMMAND" >&2
    echo "" >&2
    echo "Commands: create-product, list-products, check-product" >&2
    echo "Run with no arguments (or 'help') to see full usage." >&2
    exit 2
    ;;
esac
