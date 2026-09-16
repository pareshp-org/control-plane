#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-20 — attention-ledger measures
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/attention_measures.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }
bash "$VS" --compute attention_measures >/dev/null || { echo "--compute attention_measures failed" >&2; exit 1; }

# Positive: a self-reported entry keeps its label in the aggregate.
TMP=$(mktemp -d)
cat > "$TMP/entry-1.yaml" <<'YAML'
category: founder_coordination
hours: 4.5
month: "2026-09"
provenance: self-reported
YAML
OUT="$(python3 "$MOD" --store "$TMP" --json)"
echo "$OUT" | grep -q '"self-reported"' || { echo "self-reported label lost in the aggregate: $OUT" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

# Negative fixture: an entry with hours but no provenance label is rejected outright.
TMP2=$(mktemp -d)
cat > "$TMP2/entry-2.yaml" <<'YAML'
category: founder_coordination
hours: 4.5
month: "2026-09"
YAML
if OUT=$(python3 "$MOD" --store "$TMP2" --json 2>&1); then
  echo "neg-fixture: an entry with no provenance label was accepted" >&2
  echo "$OUT" >&2
  rm -rf "$TMP2"
  exit 1
fi
echo "$OUT" | grep -q "entry-missing-or-invalid-provenance" || { echo "rejection did not name the real problem: $OUT" >&2; rm -rf "$TMP2"; exit 1; }
rm -rf "$TMP2"

if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --json >/dev/null 2>&1; then
  echo "positive-store-absent-check: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-20 PASS"
