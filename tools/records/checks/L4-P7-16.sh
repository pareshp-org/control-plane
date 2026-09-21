#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-16 — Ready-queue-miss rolling count and trend
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/rqm.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }
bash "$VS" --compute rqm >/dev/null || { echo "--compute rqm failed" >&2; exit 1; }

TMP=$(mktemp -d)
mkdir -p "$TMP/2026-09-01"
cat > "$TMP/2026-09-01/EVT-2026-09-01-000001.yaml" <<'YAML'
event_schema_version: 1
event_id: EVT-2026-09-01-000001
event_type: ready_queue_miss_recorded
occurred_at: 2026-09-01T00:00:00Z
recorded_at: 2026-09-01T00:00:00Z
actor: dev-a
product: solvox
subject_ref: records/work/1.yaml
payload:
  sig06_counted: true
YAML
cat > "$TMP/2026-09-01/EVT-2026-09-01-000002.yaml" <<'YAML'
event_schema_version: 1
event_id: EVT-2026-09-01-000002
event_type: ready_queue_miss_recorded
occurred_at: 2026-09-01T01:00:00Z
recorded_at: 2026-09-01T01:00:00Z
actor: dev-a
product: solvox
subject_ref: records/work/2.yaml
payload:
  reason: ready_bypass
  sig06_counted: false
YAML
OUT="$(python3 "$MOD" --store "$TMP" --as-of 2026-09-15T00:00:00 --json)"
echo "$OUT" | grep -q '"rolling_30d_count": 1' || { echo "ready_bypass event must be excluded, expected count 1: $OUT" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --json >/dev/null 2>&1; then
  echo "positive-store-absent-check: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-16 PASS"
