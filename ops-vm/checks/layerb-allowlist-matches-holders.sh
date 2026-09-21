#!/usr/bin/env bash
# Section 90.4 post-patch item: the Founder-only Layer B instance's credential
# and authentication allowlist match the capability holders. Both sides are read
# as declared data; this check never edits either.
set -euo pipefail
ALLOW="${1:-ops-vm/layerb/access-list.yaml}"
HOLDERS="${2:?usage: layerb-allowlist-matches-holders.sh <access-list.yaml> <holders-file>}"
[ -f "$ALLOW" ]   || { echo "LAYERB-ALLOWLIST: FAIL (no $ALLOW)"; exit 1; }
[ -f "$HOLDERS" ] || { echo "LAYERB-ALLOWLIST: FAIL-CLOSED (no capability-holder list: $HOLDERS)"; exit 1; }
a=$(awk '/^ *- login: */{print $3}' "$ALLOW" | sort -u)
h=$(sort -u "$HOLDERS")
if [ "$a" = "$h" ]; then echo "LAYERB-ALLOWLIST: PASS"; exit 0; fi
echo "LAYERB-ALLOWLIST: FAIL"
echo "in allowlist, not a holder:"; comm -23 <(echo "$a") <(echo "$h")
echo "holder, not in allowlist:";   comm -13 <(echo "$a") <(echo "$h")
exit 1
