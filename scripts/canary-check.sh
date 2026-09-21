#!/usr/bin/env bash
# canary-check.sh — registry canary drift detection (FD-106/PFD-026)
# Checks that the __CANARY__ sentinel in registries/people/_canary.yaml is unmodified
set -euo pipefail

CANARY_FILE="${1:-registries/people/_canary.yaml}"

if [[ ! -f "$CANARY_FILE" ]]; then
  echo "CANARY FAIL: $CANARY_FILE not found"
  exit 1
fi

if grep -q "__CANARY__" "$CANARY_FILE"; then
  echo "CANARY PASS: sentinel intact in $CANARY_FILE"
  exit 0
else
  echo "CANARY FAIL: sentinel __CANARY__ missing from $CANARY_FILE — possible drift"
  exit 1
fi
