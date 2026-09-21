#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-04 — baseline markers, AT-046
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
BASELINES_PY="$CP_DIR/metrics/register/baselines.py"
BASELINES_YAML="$CP_DIR/metrics/register/baselines.yaml"
[[ -f "$VS" ]] || { echo "ABSENT: $VS" >&2; exit 1; }
[[ -f "$BASELINES_PY" ]] || { echo "ABSENT: $BASELINES_PY" >&2; exit 1; }
[[ -f "$BASELINES_YAML" ]] || { echo "ABSENT: $BASELINES_YAML" >&2; exit 1; }

# Positive: --at046 passes against the real register
bash "$VS" --at046 >/dev/null || { echo "--at046 failed" >&2; exit 1; }

# neg: a measure with neither baseline nor unbaselined must be rejected
TMP=$(mktemp -d)
cat > "$TMP/baselines.yaml" <<'YAML'
version: 1
baselines:
  - measure_id: TEST-004
YAML
if OUT="$(python3 "$BASELINES_PY" "$TMP/baselines.yaml" 2>&1)"; then
  echo "neg-fixture: expected rejection did not occur" >&2
  echo "$OUT" >&2
  rm -rf "$TMP"
  exit 1
fi
if ! printf '%s' "$OUT" | grep -q "carries neither baseline nor unbaselined"; then
  echo "neg-fixture: rejection did not name the missing baseline/unbaselined marker" >&2
  echo "$OUT" >&2
  rm -rf "$TMP"
  exit 1
fi
rm -rf "$TMP"
echo "CHECK L4-P7-04 PASS"
