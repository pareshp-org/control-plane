#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-10 — support load and first-response by severity
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
MOD="$CP_DIR/metrics/compute/support.py"
[[ -f "$MOD" ]] || { echo "ABSENT: $MOD" >&2; exit 1; }
bash "$VS" --compute support >/dev/null || { echo "--compute support failed" >&2; exit 1; }

# timestamp (record-write time) deliberately differs from received (intake time) -
# the negative case this proves: computing off `timestamp` would give 7200s, not 900s.
TMP=$(mktemp -d)
cat > "$TMP/SUP-1.yaml" <<'YAML'
record_schema_version: 1
id: SUP-2026-09-01-001
product: solvox
timestamp: 2026-09-01T02:00:00Z
message_id: mailbox/1
triage_classification: question
detection_source: customer
severity_at_intake: question
received: 2026-09-01T00:00:00Z
first_response: 2026-09-01T00:15:00Z
YAML
OUT="$(python3 "$MOD" --store "$TMP" --json)"
echo "$OUT" | grep -q '"question": 900.0' || { echo "expected 900s first-response anchored to received, not timestamp: $OUT" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

if python3 "$MOD" --store "$CP_DIR/records/does-not-exist" --json >/dev/null 2>&1; then
  echo "neg-fixture: non-existent store did not fail" >&2
  exit 1
fi
echo "CHECK L4-P7-10 PASS"
