#!/usr/bin/env bash
# Section 51.5: the quarterly drill verifies both off-VM legs fire BY STOPPING
# THE VM, not merely by rebuilding it. Both legs must route to the messaging
# channel and to the Section 42.2 phone path.
set -euo pipefail
R="${1:?usage: drill-offvm-legs-fired.sh <drill-record.yaml>}"
[ -f "$R" ] || { echo "DRILL-OFFVM-LEGS: FAIL (no $R)"; exit 1; }
fail=0
for k in vm_stopped_at vm_restarted_at; do
  v=$(awk -F': *' -v k="$k" '$0 ~ "^ *"k":" {print $2; exit}' "$R" | tr -d '"')
  [ -n "$v" ] || { echo "$k is empty - the VM was not stopped, so the legs were not verified"; fail=1; }
done
for k in external_uptime_check_fired dead_mans_switch_fired routed_to_messaging_channel routed_to_phone_path; do
  v=$(awk -F': *' -v k="$k" '$0 ~ "^ *"k":" {print $2; exit}' "$R" | tr -d '"')
  [ "$v" = "true" ] || { echo "$k is not true"; fail=1; }
done
if [ "$fail" -eq 0 ]; then echo "DRILL-OFFVM-LEGS: PASS"; else echo "DRILL-OFFVM-LEGS: FAIL"; exit 1; fi
