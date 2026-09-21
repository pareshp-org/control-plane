#!/usr/bin/env bash
# Post-provision / post-patch assertion: dashboards provision from JSON and the
# instance's datasources connect (Section 51.4 post-patch smoke checklist).
set -euo pipefail
BASE="${1:?usage: grafana-provisioned.sh <base-url> <api-token>}"
TOKEN="${2:?}"
ds=$(curl -sf -H "Authorization: Bearer $TOKEN" "$BASE/api/datasources" | python3 -c 'import sys,json;print(len(json.load(sys.stdin)))')
[ "$ds" -ge 1 ] || { echo "GRAFANA-PROVISIONED: FAIL (no datasources)"; exit 1; }
for uid in $(curl -sf -H "Authorization: Bearer $TOKEN" "$BASE/api/datasources" | python3 -c 'import sys,json;[print(d["uid"]) for d in json.load(sys.stdin)]'); do
  st=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $TOKEN" "$BASE/api/datasources/uid/$uid/health")
  [ "$st" = "200" ] || { echo "GRAFANA-PROVISIONED: FAIL (datasource $uid health $st)"; exit 1; }
done
curl -sf -H "Authorization: Bearer $TOKEN" "$BASE/api/dashboards/uid/control-plane-stack" >/dev/null \
  || { echo "GRAFANA-PROVISIONED: FAIL (control-plane-stack dashboard absent)"; exit 1; }
echo "GRAFANA-PROVISIONED: PASS"
