#!/usr/bin/env bash
# Verifies every spec line-range citation used by Lane 1 still resolves.
# Usage: check_spec_anchors.sh <path-to-MultiProduct_MasterSpec_v4.0.md>
set -euo pipefail
SPEC="${1:?usage: check_spec_anchors.sh <spec-file>}"
TSV="$(dirname "$0")/spec-anchors.tsv"
fail=0
while IFS=$'\t' read -r re want id; do
  case "$re" in \#*|'') continue;; esac
  got="$(grep -n -m1 -E "$re" "$SPEC" | cut -d: -f1)"
  if [ "$got" != "$want" ]; then
    echo "ANCHOR-DRIFT: section $id expected line $want, found '${got:-none}'"
    fail=1
  fi
done < "$TSV"
if [ "$fail" -ne 0 ]; then echo "SPEC-ANCHORS-FAIL"; exit 1; fi
echo "SPEC-ANCHORS-PASS"
exit 0
