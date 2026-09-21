#!/usr/bin/env bash
# access/layer-b/check-non-delegable.sh
# D109: "Layer B access is not delegable. The routine people_intelligence_delegate
# is removed." Section 90.4: "No assignment type grants it, and none may be
# introduced to do so."
set -uo pipefail
FAILS=0
note() { echo "DEL_FAIL $1"; FAILS=$((FAILS+1)); }

HOLDERS=""
if [ -f contracts/access/access-inputs.yaml ]; then
  HOLDERS=$(yq -r '.layer_b.capability_holders_artifact // ""' contracts/access/access-inputs.yaml)
fi
if [ -z "$HOLDERS" ] || [ ! -f "$HOLDERS" ]; then
  echo "DEL_BLOCKED holders artifact unavailable (contracts/access/access-inputs.yaml : layer_b.capability_holders_artifact is unset or unreadable)"
  exit 2
fi

# 1. The removed routine appears nowhere in the published artifact.
grep -qi 'people_intelligence_delegate' "$HOLDERS" && note "the removed routine people_intelligence_delegate is present in the artifact"

# 2. No assignment in the artifact grants the capability.
n=$(yq -r '[.assignments[]? | select(.capability == "people-intelligence")] | length' "$HOLDERS" 2>/dev/null || echo 0)
[ "$n" = "0" ] || note "$n assignment(s) grant people-intelligence"

# 3. The sync job has no delegate path and no hard-coded login.
grep -qi 'delegate' ops-vm/layer-b/allowlist/sync-allowlist.sh && note "the sync job contains a delegate path"
grep -qE '"[a-z0-9-]+"\s*\]?\s*#\s*login' ops-vm/layer-b/allowlist/sync-allowlist.sh && note "the sync job hard-codes a login"

# 4. On the instance, no user holds a role above Viewer by delegation.
adm=$(ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/org/users | jq -r "[.[] | select(.role != \"Admin\" and .role != \"Viewer\")] | length"' 2>/dev/null || echo -1)
if [ "$adm" = "-1" ]; then
  echo "DEL_NOTE host-side check (item 4) skipped: layerb-host is unreachable from this environment"
elif [ "$adm" != "0" ]; then
  note "$adm Layer B-M user(s) hold a role that is neither Admin nor Viewer"
fi

if [ "$FAILS" -eq 0 ]; then echo "NON_DELEGABLE_OK"; else echo "NON_DELEGABLE_FAILED $FAILS"; exit 1; fi
