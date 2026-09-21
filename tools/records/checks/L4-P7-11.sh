#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-11 — eval measures and SIG-42 regression coalescing
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/eval.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }
bash "$VS" --compute eval >/dev/null || { echo "--compute eval failed" >&2; exit 1; }

# Two dimensions regress on the SAME run - must coalesce into exactly ONE triage event.
TMP=$(mktemp -d)
cat > "$TMP/EVAL-1.yaml" <<'YAML'
record_schema_version: 1
id: EVAL-2026-09-01-001
product: solvox
timestamp: 2026-09-01T00:00:00Z
suite: verification/ai-eval
trigger: scheduled
model_pin: m1
result: fail
regression: true
dimensions:
  - dimension: grounding
    score: 80.0
    baseline: 90.0
  - dimension: refusal
    score: 70.0
    baseline: 92.0
YAML
OUT="$(python3 "$MOD" --store "$TMP" --json)"
echo "$OUT" | grep -q '"sig42_triage_event_count": 1' || { echo "expected exactly 1 coalesced triage event, not one per dimension: $OUT" >&2; rm -rf "$TMP"; exit 1; }
echo "$OUT" | grep -q 'grounding' || { echo "expected both dimensions named in the single event: $OUT" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --json >/dev/null 2>&1; then
  echo "neg-fixture: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-11 PASS"
