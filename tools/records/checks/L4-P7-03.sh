#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-03 — arming discipline: empty store renders unbaselined, never a miss (D77)
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
ARMING="$CP_DIR/metrics/register/arming.py"
[[ -f "$VS" ]] || { echo "ABSENT: $VS" >&2; exit 1; }
[[ -f "$ARMING" ]] || { echo "ABSENT: $ARMING" >&2; exit 1; }

# Positive: --arming passes against the real register
bash "$VS" --arming >/dev/null || { echo "--arming failed" >&2; exit 1; }

# neg: a store with zero records must render ARMING unbaselined, never a threshold breach
TMP=$(mktemp -d)
mkdir -p "$TMP/empty-store"
OUT="$(python3 "$ARMING" --store "$TMP/empty-store" 2>&1)"
RC=$?
if [ "$RC" != "0" ]; then
  echo "neg-fixture: arming.py failed on a genuinely empty store" >&2
  echo "$OUT" >&2
  rm -rf "$TMP"
  exit 1
fi
if [ "$OUT" != "ARMING unbaselined" ]; then
  echo "neg-fixture: empty store did not render unbaselined: $OUT" >&2
  rm -rf "$TMP"
  exit 1
fi
rm -rf "$TMP"
echo "CHECK L4-P7-03 PASS"
