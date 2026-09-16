#!/usr/bin/env bash
# Emit one conforming ai_subscription_seat inventory entry (Section 39.1).
# Usage: new_seat_entry.sh <holder> <vendor> <runtime> <renewal_date> <billing_cycle> <tier> <cost_band> <owner>
set -euo pipefail
if [ "$#" -ne 8 ]; then
  echo "USAGE: new_seat_entry.sh <holder> <vendor> <runtime> <renewal_date> <billing_cycle> <tier> <cost_band> <owner>"
  exit 2
fi
HOLDER="$1"; VENDOR="$2"; RUNTIME="$3"; RENEW="$4"; CYCLE="$5"; TIER="$6"; BAND="$7"; OWNER="$8"
OUT="assets/inventory/ai-seat-${HOLDER}.yaml"
cat > "$OUT" <<INNER
asset_id: ai-seat-${HOLDER}
asset_class: ai_subscription_seat
owner: ${OWNER}
expiry_date: "${RENEW}"
alert_days: 30
cost_band: ${BAND}
spec_reference: "39.1, 49.1"
vendor: ${VENDOR}
runtime: ${RUNTIME}
holder: ${HOLDER}
renewal_date: "${RENEW}"
billing_cycle: ${CYCLE}
tier: ${TIER}
INNER
echo "SEAT-ENTRY: WROTE ${OUT}"
