#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-01 — eight attributes per declared measure
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
[[ -f "$VS" ]] || { echo "ABSENT: $VS" >&2; exit 1; }

# Positive: --attributes passes against the real (currently empty) register
bash "$VS" --attributes >/dev/null || { echo "--attributes failed" >&2; exit 1; }

# Assertion: validate-sources.sh contains the --attributes branch
grep -q -- '--attributes' "$VS" || { echo "--attributes branch missing from validate-sources.sh" >&2; exit 1; }

# Negative fixture (neg): a measure missing 'owner' must be rejected.
# validate-sources.sh resolves its declarations file relative to its OWN
# directory, so copying it alongside a bad metric-declarations.yaml in a
# sandbox exercises the real --attributes logic against a real fixture.
TMP=$(mktemp -d)
cp "$VS" "$TMP/validate-sources.sh"
cat > "$TMP/metric-declarations.yaml" <<'YAML'
$schema: urn:multiproduct:schemas/metric-declarations/v1
version: 1
metrics:
  - id: TEST-001
    definition: "test"
    source: "records/deployments/"
    time_window: "30d"
    baseline: "unbaselined"
    expected_interpretation: "lower is better"
    known_limitations: "none"
    action_on_breach: "page on-call"
YAML
# owner is deliberately absent above.
if OUT="$(bash "$TMP/validate-sources.sh" --attributes 2>&1)"; then
  echo "neg-fixture: expected rejection did not occur" >&2
  echo "$OUT" >&2
  rm -rf "$TMP"
  exit 1
fi
if ! printf '%s' "$OUT" | grep -q "missing attribute(s): owner"; then
  echo "neg-fixture: rejection did not name the missing 'owner' attribute" >&2
  echo "$OUT" >&2
  rm -rf "$TMP"
  exit 1
fi
rm -rf "$TMP"
echo "CHECK L4-P7-01 PASS"
