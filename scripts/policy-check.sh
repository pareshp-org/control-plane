#!/usr/bin/env bash
# policy-check.sh — L5 policy enforcement gate (FD-104/PFD-024)
# Usage: bash scripts/policy-check.sh --policy <id> --subject <id>
set -euo pipefail

POLICY=""
SUBJECT=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --policy) POLICY="$2"; shift 2;;
    --subject) SUBJECT="$2"; shift 2;;
    *) shift;;
  esac
done

echo "POLICY-CHECK (stub): policy=$POLICY subject=$SUBJECT"
echo "TODO: implement against registries/policies/ per FD-104"
# Stub always passes during bootstrap
exit 0
