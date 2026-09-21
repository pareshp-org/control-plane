#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-14 — learning-loop measures (SIG-47)
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/learning_loop.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }
bash "$VS" --compute learning_loop >/dev/null || { echo "--compute learning_loop failed" >&2; exit 1; }

# A postmortem with NO items list at all, 60 days old, not closed - must still count as open.
TMP=$(mktemp -d)
cat > "$TMP/PM-1.yaml" <<'YAML'
record_schema_version: 1
id: PM-2026-07-01-001
product: solvox
timestamp: 2026-07-01T00:00:00Z
incident: records/incidents/x.yaml
due: 2026-07-06
root_cause: code
YAML
OUT="$(python3 "$MOD" --store "$TMP" --as-of 2026-09-01 --json)"
echo "$OUT" | grep -q '"open_stale_postmortems": 1' || { echo "expected 1 open stale postmortem despite no items list: $OUT" >&2; rm -rf "$TMP"; exit 1; }
echo "$OUT" | grep -q '"signal_id": "SIG-47"' || { echo "signal id must be SIG-47: $OUT" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --json >/dev/null 2>&1; then
  echo "positive-store-absent-check: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-14 PASS"
