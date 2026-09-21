#!/usr/bin/env bash
# Section 45.4 clock semantics: starts at provision-start, stops at
# dashboards-green, INCLUDING the Layer B restore, target under 4 hours.
set -euo pipefail
R="${1:?usage: drill-clock.sh <drill-record.yaml>}"
[ -f "$R" ] || { echo "DRILL-CLOCK: FAIL (no $R)"; exit 1; }
g() { awk -F': *' -v k="$1" '$0 ~ "^ *"k":" {print $2; exit}' "$R" | tr -d '"'; }
lb=$(g layer_b_restored); el=$(g elapsed_minutes); tg=$(g target_minutes)
om=$(g omitted_steps)
fail=0
[ "$lb" = "true" ] || { echo "layer_b_restored is not true - a rebuild that leaves Layer B unrestored has not finished"; fail=1; }
case "$el" in ''|*[!0-9]*) echo "elapsed_minutes is not an integer"; fail=1 ;; esac
[ "$tg" = "240" ] || { echo "target_minutes is not 240"; fail=1; }
case "$om" in ''|'[]') ;; *) echo "omitted_steps is not empty - an omitted step is a test failure"; fail=1 ;; esac
if [ "$fail" -eq 0 ] && [ "$el" -ge "$tg" ]; then echo "elapsed ${el}m is not under the ${tg}m target"; fail=1; fi
if [ "$fail" -eq 0 ]; then echo "DRILL-CLOCK: PASS"; else echo "DRILL-CLOCK: FAIL"; exit 1; fi
