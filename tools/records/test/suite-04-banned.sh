#!/usr/bin/env bash
# AT-075 (line 9406) against the banned list of Section 91.2 (lines 8081-8092).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../../.." && pwd)"
. "$HERE/lib.sh"
BM="$CP/tools/records/fixtures/negative/at075"

# Limb 1 — absent from the schemas and the metrics tree.
i=0
for token in keystroke screen_monitor activity_surveillance webcam \
             hours_online hours_at_desk token_usage ide_active flight_risk surveillance_scor ; do
  i=$((i+1)); id="$(printf 'BM-ABS-%02d' "$i")"
  # Excludes validate-sources.sh itself: its --check-declaration limb (added
  # for this suite) necessarily NAMES these tokens as denylist patterns to
  # check against, the same way L4-T205's denied-property-names.txt names
  # "name" without itself being a schema that declares that property.
  n="$(grep -rli "$token" "$CP/schemas/records" "$CP/metrics" \
        --exclude-dir=fixtures --exclude-dir=negative \
        --exclude=validate-sources.sh 2>/dev/null | wc -l | tr -d ' ')"
  assert_eq "$id" "0" "$n"
done

# Limb 2 — rejected if introduced.
i=0
for f in "$BM"/BM-*.yaml; do
  i=$((i+1)); id="$(printf 'BM-REJ-%02d' "$i")"
  assert_rejects "$id" bash "$CP/metrics/register/validate-sources.sh" --check-declaration "$f"
done

summary "04-banned"
