#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-17 — status-request count from the event log
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/status_requests.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }
bash "$VS" --compute status_requests >/dev/null || { echo "--compute status_requests failed" >&2; exit 1; }

TMP=$(mktemp -d)
mkdir -p "$TMP/2026-09-01"
cat > "$TMP/2026-09-01/EVT-2026-09-01-000001.yaml" <<'YAML'
event_schema_version: 1
event_id: EVT-2026-09-01-000001
event_type: status_request_received
occurred_at: 2026-09-01T00:00:00Z
recorded_at: 2026-09-01T00:00:00Z
actor: dev-a
product: solvox
subject_ref: records/work/1.yaml
payload: {}
YAML
cat > "$TMP/2026-09-01/EVT-2026-09-01-000002.yaml" <<'YAML'
event_schema_version: 1
event_id: EVT-2026-09-01-000002
event_type: work_item_created
occurred_at: 2026-09-01T01:00:00Z
recorded_at: 2026-09-01T01:00:00Z
actor: dev-a
product: solvox
subject_ref: records/work/2.yaml
payload: {}
YAML
OUT="$(python3 "$MOD" --store "$TMP" --json)"
echo "$OUT" | grep -q '"n": 1' || { echo "non-Coordination event was counted, expected n=1: $OUT" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --json >/dev/null 2>&1; then
  echo "positive-store-absent-check: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-17 PASS"
