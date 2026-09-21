#!/usr/bin/env bash
# D87 Blocking row 3: a branch-push-triggered workflow admitted to the privileged
# group. Input is an admission listing in the form
#   <workflow-file>\t<trigger>\t<runner-group>
set -euo pipefail
L="${1:?usage: check-no-branch-push-in-privileged.sh <admissions.tsv>}"
[ -f "$L" ] || { echo "D87-ROW-3: FAIL-CLOSED (no admission listing: $L)"; exit 4; }
bad=0
while IFS=$'\t' read -r wf trig group; do
  [ -n "${wf:-}" ] || continue
  [ "$group" = "privileged" ] || continue
  [ "$trig" != "push" ] || { echo "branch-push-triggered workflow admitted to the privileged group: $wf"; bad=1; }
done < "$L"
if [ "$bad" -eq 0 ]; then echo "D87-ROW-3: PASS"; else echo "D87-ROW-3: BLOCKING"; exit 4; fi
