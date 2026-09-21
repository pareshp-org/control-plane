#!/usr/bin/env bash
# Section 49.1: every entry carries an alert threshold of at least 30 days.
# The floor is a specification constant and is checked, never remembered.
set -euo pipefail
DIR="${1:?usage: inventory-alert-lead-floor.sh <inventory-dir>}"
bad=0
for f in "$DIR"/*.yaml; do
  [ -e "$f" ] || continue
  v=$(awk -F': *' '/^alert_days:/{print $2}' "$f" | tr -d '"' | head -1)
  case "$v" in
    ''|*[!0-9]*) echo "no integer alert_days: $f"; bad=1; continue ;;
  esac
  if [ "$v" -lt 30 ]; then echo "alert_days $v below the Section 49.1 floor: $f"; bad=1; fi
done
if [ "$bad" -eq 0 ]; then echo "ALERT-LEAD-FLOOR: PASS"; else echo "ALERT-LEAD-FLOOR: FAIL"; exit 1; fi
