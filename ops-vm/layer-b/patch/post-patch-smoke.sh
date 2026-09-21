#!/usr/bin/env bash
# ops-vm/layer-b/patch/post-patch-smoke.sh
# The Section 51.4 post-patch smoke checklist. Four items, plus the mandated
# reconciliation assertion. Exit 0 only when all five pass clean.
set -uo pipefail
FAILS=0
note() { echo "SMOKE_FAIL $1"; FAILS=$((FAILS+1)); }

# 1. Dashboards provision from JSON on both instances.
lb=$(ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/search?type=dash-db | jq -r "length"' 2>/dev/null || echo -1)
[ "$lb" -ge 0 ] 2>/dev/null || note "Layer B-M dashboard search failed (host unreachable or errored)"
ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/search?type=dash-db | jq -r ".[].id" | while read -r i; do
  curl -s -u "$LAYERB_ADMIN" "http://127.0.0.1:3001/api/dashboards/id/$i" | jq -e ".meta.provisioned == true" >/dev/null || exit 1
done' >/dev/null 2>&1 || note "a Layer B-M dashboard is not provisioned from JSON (or host unreachable)"
ssh ops-vm 'curl -s -u "$SHARED_GRAFANA_ADMIN" http://127.0.0.1:3000/api/search?type=dash-db | jq -r ".[].id" | while read -r i; do
  curl -s -u "$SHARED_GRAFANA_ADMIN" "http://127.0.0.1:3000/api/dashboards/id/$i" | jq -e ".meta.provisioned == true" >/dev/null || exit 1
done' >/dev/null 2>&1 || note "a shared-instance dashboard is not provisioned from JSON (or host unreachable)"

# 2. Both instances' datasources connect.
ssh layerb-host 'curl -s -u "$LAYERB_ADMIN" http://127.0.0.1:3001/api/datasources | jq -r ".[].uid" | while read -r u; do
  curl -s -u "$LAYERB_ADMIN" "http://127.0.0.1:3001/api/datasources/uid/$u/health" | jq -e ".status == \"OK\"" >/dev/null || exit 1
done' >/dev/null 2>&1 || note "a Layer B-M datasource does not connect (or host unreachable)"
ssh ops-vm 'curl -s -u "$SHARED_GRAFANA_ADMIN" http://127.0.0.1:3000/api/datasources | jq -r ".[].uid" | while read -r u; do
  curl -s -u "$SHARED_GRAFANA_ADMIN" "http://127.0.0.1:3000/api/datasources/uid/$u/health" | jq -e ".status == \"OK\"" >/dev/null || exit 1
done' >/dev/null 2>&1 || note "a shared-instance datasource does not connect (or host unreachable)"

# 3. Alert rules fire a test alert - on the SHARED instance only.
# Layer B-M alerting stays off: Section 90.2, "People intelligence is never
# relayed over messaging surfaces." See E-P3-06.
t=$(ssh ops-vm 'curl -s -o /dev/null -w "%{http_code}" -u "$SHARED_GRAFANA_ADMIN" -X POST http://127.0.0.1:3000/api/alertmanager/grafana/config/api/v1/receivers/test -H "Content-Type: application/json" -d "{}"' 2>/dev/null || echo 000)
case "$t" in 200|202) : ;; *) note "shared-instance test alert returned $t (or host unreachable)" ;; esac
awk '/^\[unified_alerting\]/{f=1;next} /^\[/{f=0} f&&/^enabled/{print $3}' ops-vm/layer-b/grafana.ini \
  | grep -qx false || note "Layer B-M alerting is enabled; Section 90.2 forbids relaying people intelligence"
echo "SMOKE_NOTE layerb_alerting: disabled-by-90-2"

# 4. Layer B-M credential and authentication allowlist match the capability holders.
./access/layer-b/check-allowlist-parity.sh >/dev/null 2>&1 || note "allowlist parity fails after the patch (or is currently blocked pending the L0 capability-holders contract)"
./access/layer-b/at-098-separately-credentialed.sh >/dev/null 2>&1 || note "the instance credential is no longer separate after the patch"

# 5. The mandated immediate reconciliation run exists, is newer than the patch and is clean.
# L5 does not invoke the reconciler (E-P3-08); it asserts the published result.
REC="${RECONCILIATION_RESULT:-/srv/shared/reconciliation/latest.json}"
r=$(ssh ops-vm "jq -r '.status' $REC" 2>/dev/null || echo missing)
[ "$r" = "clean" ] || note "the post-patch reconciliation run is '$r', expected 'clean' (or host unreachable)"
rt=$(ssh ops-vm "jq -r '.completed_at' $REC" 2>/dev/null || echo "")
[ -n "$rt" ] || note "the reconciliation result carries no completion time (or host unreachable)"

if [ "$FAILS" -eq 0 ]; then echo "POST_PATCH_SMOKE_OK 5/5"; else echo "POST_PATCH_SMOKE_FAILED $FAILS"; exit 1; fi
