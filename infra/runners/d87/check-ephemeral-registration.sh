#!/usr/bin/env bash
# D87 Blocking row 1: a self-hosted runner in the privileged group registered
# non-ephemerally. Input is a runner listing in the form
#   <name>\t<group>\t<ephemeral true|false>\t<writable_shared_volume true|false>
# produced read-only from the platform; this check never registers a runner.
set -euo pipefail
L="${1:?usage: check-ephemeral-registration.sh <runner-listing.tsv>}"
[ -f "$L" ] || { echo "D87-ROW-1: FAIL-CLOSED (no runner listing: $L)"; exit 4; }
bad=0
while IFS=$'\t' read -r name group eph vol; do
  [ -n "${name:-}" ] || continue
  [ "$group" = "privileged" ] || continue
  [ "$eph" = "true" ] || { echo "non-ephemeral runner in the privileged group: $name"; bad=1; }
  [ "$vol" = "false" ] || { echo "writable shared volume on a privileged runner: $name"; bad=1; }
done < "$L"
if [ "$bad" -eq 0 ]; then echo "D87-ROW-1: PASS"; else echo "D87-ROW-1: BLOCKING"; exit 4; fi
