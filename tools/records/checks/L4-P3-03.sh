#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P3-03 — retire-never-remove mechanism, validate-taxonomy.sh --retirement
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VT="$CP_DIR/tools/records/validate-taxonomy.sh"
PY="${L4_PY:-python}"

[[ -f "$VT" ]] || { echo "ABSENT: $VT" >&2; exit 1; }
[[ -f "$CP_DIR/metrics/taxonomy/RETIREMENT.md" ]] || { echo "ABSENT: metrics/taxonomy/RETIREMENT.md" >&2; exit 1; }
grep -q -- '--retirement' "$VT" || { echo "--retirement mode missing from validate-taxonomy.sh" >&2; exit 1; }

# Positive: the real repo's current taxonomy removes nothing relative to origin/integration.
CP_ROOT="$CP_DIR" L4_PY="$PY" bash "$VT" --retirement 2>&1 | grep -q '^RETIREMENT OK' \
  || { echo "real-repo retirement check did not print RETIREMENT OK" >&2; exit 1; }

# Self-contained sandbox: build a two-commit taxonomy history so the mechanism
# can be proved without depending on the real repo's git log.
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/metrics/taxonomy"
git -C "$TMP" init -q
git -C "$TMP" -c user.email=l4@example.invalid -c user.name=L4 config user.email l4@example.invalid
git -C "$TMP" -c user.email=l4@example.invalid -c user.name=L4 config user.name L4

cat > "$TMP/metrics/taxonomy/event-types.yaml" <<'YAML'
taxonomy_version: 1
identifier_count: 2
event_types:
  - { n: 1, id: alpha_shipped, entry: "alpha", payload_required: [] }
  - { n: 2, id: beta_shipped,  entry: "beta",  payload_required: [] }
YAML
git -C "$TMP" add -A
git -C "$TMP" -c user.email=l4@example.invalid -c user.name=L4 commit -q -m "v1: alpha_shipped, beta_shipped"
BASELINE_SHA="$(git -C "$TMP" rev-parse HEAD)"

# Positive fixture: alpha_shipped is retired but its row stays present.
cat > "$TMP/metrics/taxonomy/event-types.yaml" <<'YAML'
taxonomy_version: 1
identifier_count: 2
event_types:
  - { n: 1, id: alpha_shipped, entry: "alpha", payload_required: [], retired: true }
  - { n: 2, id: beta_shipped,  entry: "beta",  payload_required: [] }
YAML
git -C "$TMP" add -A
git -C "$TMP" -c user.email=l4@example.invalid -c user.name=L4 commit -q -m "v2: retire alpha_shipped"

OUT="$(CP_ROOT="$TMP" L4_PY="$PY" bash "$VT" --retirement "$BASELINE_SHA" 2>&1)" \
  || { echo "retirement-with-flag was rejected, expected acceptance" >&2; echo "$OUT" >&2; exit 1; }
printf '%s' "$OUT" | grep -q '^RETIREMENT OK 2$' \
  || { echo "unexpected output for accepted retirement: $OUT" >&2; exit 1; }

# Negative fixture (neg_fixture): removing alpha_shipped outright, rather than
# marking it retired, must be rejected — this is the bad_fixture that proves
# the check can fail, not only pass.
cat > "$TMP/metrics/taxonomy/event-types.yaml" <<'YAML'
taxonomy_version: 1
identifier_count: 1
event_types:
  - { n: 2, id: beta_shipped, entry: "beta", payload_required: [] }
YAML
git -C "$TMP" add -A
git -C "$TMP" -c user.email=l4@example.invalid -c user.name=L4 commit -q -m "bad_fixture: delete alpha_shipped outright"

if OUT="$(CP_ROOT="$TMP" L4_PY="$PY" bash "$VT" --retirement "$BASELINE_SHA" 2>&1)"; then
  echo "neg_fixture: expected rejection of outright removal did not occur" >&2
  echo "$OUT" >&2
  exit 1
fi
printf '%s' "$OUT" | grep -q 'alpha_shipped' \
  || { echo "neg_fixture: rejection did not name the removed identifier" >&2; echo "$OUT" >&2; exit 1; }

echo "CHECK L4-P3-03 PASS"
