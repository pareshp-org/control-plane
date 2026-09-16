#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-05 — owner-and-response completeness gate (invariant 49)
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
OWNERSHIP_PY="$CP_DIR/metrics/register/ownership.py"
[[ -f "$VS" ]] || { echo "ABSENT: $VS" >&2; exit 1; }
[[ -f "$OWNERSHIP_PY" ]] || { echo "ABSENT: $OWNERSHIP_PY" >&2; exit 1; }

# Positive: --ownership passes against the real register
bash "$VS" --ownership >/dev/null || { echo "--ownership failed" >&2; exit 1; }

# neg: a measure with owner: "" is rejected
TMP=$(mktemp -d)
cat > "$TMP/metric-declarations.yaml" <<'YAML'
$schema: urn:multiproduct:schemas/metric-declarations/v1
version: 1
metrics:
  - id: TEST-005
    owner: ""
    action_on_breach: "page on-call"
YAML
if OUT="$(python3 "$OWNERSHIP_PY" "$TMP/metric-declarations.yaml" 2>&1)"; then
  echo "neg-fixture: expected rejection of empty owner did not occur" >&2
  echo "$OUT" >&2
  rm -rf "$TMP"
  exit 1
fi
if ! printf '%s' "$OUT" | grep -q "has no owner"; then
  echo "neg-fixture: rejection did not name the missing owner" >&2
  echo "$OUT" >&2
  rm -rf "$TMP"
  exit 1
fi
rm -rf "$TMP"
echo "CHECK L4-P7-05 PASS"
