#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-02 — source discipline, every measure names its record store (invariant 46)
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
[[ -f "$VS" ]] || { echo "ABSENT: $VS" >&2; exit 1; }

# Positive: default run passes against the real register
bash "$VS" >/dev/null || { echo "default run failed" >&2; exit 1; }

# neg: a measure with source: "" is rejected
TMP=$(mktemp -d)
cp "$VS" "$TMP/validate-sources.sh"
cat > "$TMP/metric-declarations.yaml" <<'YAML'
$schema: urn:multiproduct:schemas/metric-declarations/v1
version: 1
metrics:
  - id: TEST-002
    source: ""
YAML
if OUT="$(bash "$TMP/validate-sources.sh" 2>&1)"; then
  echo "neg-fixture: expected rejection of empty source did not occur" >&2
  echo "$OUT" >&2
  rm -rf "$TMP"
  exit 1
fi
if ! printf '%s' "$OUT" | grep -q "no source"; then
  echo "neg-fixture: rejection did not name the missing source" >&2
  echo "$OUT" >&2
  rm -rf "$TMP"
  exit 1
fi
rm -rf "$TMP"
echo "CHECK L4-P7-02 PASS"
