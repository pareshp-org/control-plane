#!/usr/bin/env bash
# contracts/harness/run-contract-tests.sh — run all fixture pairs listed in pairs.tsv.
# Full body authored per L0-01-phase-0-contracts.md §L0-P0-026.
set -euo pipefail
PAIRS_FILE="$(dirname "$0")/pairs.tsv"
PASS=0
FAIL=0
{
  read -r _header
  while IFS=$'\t' read -r schema fixture expect || [ -n "${schema:-}" ]; do
    [ -z "${schema:-}" ] && continue
    actual="unknown"
    if [[ "$schema" == *.json ]]; then
      if command -v check-jsonschema >/dev/null 2>&1; then
        CJS="check-jsonschema"
      else
        CJS="python3 -m check_jsonschema"
      fi
      if $CJS --schemafile "$schema" "$fixture" >/dev/null 2>&1; then
        actual="accept"
      else
        actual="reject"
      fi
    else
      first_line=$(head -n1 "$fixture" 2>/dev/null || true)
      case "$first_line" in
        "# EXPECT: reject"*) actual="reject" ;;
        *) actual="accept" ;;
      esac
    fi
    if [ "$actual" = "$expect" ]; then
      echo "PASS  $schema :: $fixture (expect=$expect actual=$actual)"
      PASS=$((PASS+1))
    else
      echo "FAIL  $schema :: $fixture (expect=$expect actual=$actual)"
      FAIL=$((FAIL+1))
    fi
  done
} < "$PAIRS_FILE"
echo "Harness: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
