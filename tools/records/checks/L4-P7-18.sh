#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-18 — onboarding, launch and demo cadence measures
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/lifecycle_cadence.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }
bash "$VS" --compute lifecycle_cadence >/dev/null || { echo "--compute lifecycle_cadence failed" >&2; exit 1; }

TMP=$(mktemp -d)
cat > "$TMP/ONB-1.yaml" <<'YAML'
record_schema_version: 1
id: ONB-2026-09-25-006
product: solvox
timestamp: 2026-09-25T16:00:00Z
phase: first-accepted-pr
completed: 2026-09-25
judgment_step: false
owner: qa-1
YAML
if OUT=$(python3 "$MOD" --store "$TMP" --json 2>&1); then
  echo "neg-fixture: milestone record missing first_accepted_pr was accepted" >&2
  echo "$OUT" >&2
  rm -rf "$TMP"
  exit 1
fi
echo "$OUT" | grep -q "milestone-record-missing-first-accepted-pr" || { echo "rejection did not name the real problem: $OUT" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --json >/dev/null 2>&1; then
  echo "positive-store-absent-check: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-18 PASS"
