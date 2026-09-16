#!/usr/bin/env bash
# Emit one conforming vendor deadline-watch entry (Section 49.2).
# Every value is supplied by the caller. This script chooses nothing.
# Usage: new_deadline_entry.sh <deadline_id> <class> <vendor> <owner> <product> \
#                             <announced_deadline> <alert_lead_days> \
#                             <migration_effort_estimate_days> <reference> <rationale>
set -euo pipefail
if [ "$#" -ne 10 ]; then
  echo "USAGE: new_deadline_entry.sh <deadline_id> <class> <vendor> <owner> <product> <announced_deadline> <alert_lead_days> <migration_effort_estimate_days> <reference> <rationale>"
  exit 2
fi
ID="$1"; CLASS="$2"; VENDOR="$3"; OWNER="$4"; PRODUCT="$5"
WHEN="$6"; LEAD="$7"; EFFORT="$8"; REF="$9"; WHY="${10}"
case "$CLASS" in
  api_sunset|app_store_policy|auth_mechanism_change|vendor_contract_change) ;;
  *) echo "REFUSED: deadline_class '${CLASS}' is not one of the four Section 49.2 classes"; exit 2 ;;
esac
OUT="assets/deadlines/${ID}.yaml"
cat > "$OUT" <<INNER
deadline_id: ${ID}
deadline_class: ${CLASS}
vendor: ${VENDOR}
owner: ${OWNER}
product: ${PRODUCT}
announced_deadline: "${WHEN}"
alert_lead_days: ${LEAD}
lead_time_rationale: "${WHY}"
migration_effort_estimate_days: ${EFFORT}
announcement_reference: "${REF}"
pattern_class: vendor-deprecation
spec_reference: "49.2"
INNER
echo "DEADLINE-ENTRY: WROTE ${OUT}"
