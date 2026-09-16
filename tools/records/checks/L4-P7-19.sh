#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-19 — undeclared weekend activations, the residual
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/weekend_residual.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }
bash "$VS" --compute weekend_residual >/dev/null || { echo "--compute weekend_residual failed" >&2; exit 1; }

TMP=$(mktemp -d)
mkdir -p "$TMP/events/2026-09-05" "$TMP/events/2026-09-06"
cat > "$TMP/calendar.yaml" <<'YAML'
record_schema_version: 1
id: LV-2026-01-01-000
product: portfolio
timestamp: 2026-01-01T00:00:00Z
operating_timezone: UTC
working_days: [Monday, Tuesday, Wednesday, Thursday, Friday]
core_hours_start: "09:00"
core_hours_end: "18:00"
public_holidays: []
YAML
# Saturday 2026-09-05 at 10:00 -> out of hours (not a working day)
cat > "$TMP/events/2026-09-05/EVT-2026-09-05-000001.yaml" <<'YAML'
event_schema_version: 1
event_id: EVT-2026-09-05-000001
event_type: work_item_moved_to_ready
occurred_at: 2026-09-05T10:00:00Z
recorded_at: 2026-09-05T10:00:00Z
actor: dev-a
product: solvox
subject_ref: records/work/1.yaml
payload: {}
YAML
# Sunday 2026-09-06 - a WEEKDAY equivalent for this fixture's calendar test:
# use a Monday inside working hours (2026-09-07 10:00) to prove exclusion.
mkdir -p "$TMP/events/2026-09-07"
cat > "$TMP/events/2026-09-07/EVT-2026-09-07-000001.yaml" <<'YAML'
event_schema_version: 1
event_id: EVT-2026-09-07-000001
event_type: work_item_moved_to_ready
occurred_at: 2026-09-07T10:00:00Z
recorded_at: 2026-09-07T10:00:00Z
actor: dev-a
product: solvox
subject_ref: records/work/2.yaml
payload: {}
YAML
OUT="$(python3 "$MOD" --store "$TMP/events" --calendar "$TMP/calendar.yaml" --json)"
echo "$OUT" | grep -q '"out_of_hours_events": 1' || { echo "an in-hours event was not excluded, expected 1 out-of-hours: $OUT" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --calendar "$CP_DIR/records/CONTRIBUTING.md" --json >/dev/null 2>&1; then
  echo "positive-store-absent-check: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-19 PASS"
