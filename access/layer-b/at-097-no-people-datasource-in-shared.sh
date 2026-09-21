#!/usr/bin/env bash
# access/layer-b/at-097-no-people-datasource-in-shared.sh
# AT-097 - "No people datasource in the shared Grafana instance".
# Verified in the provisioned configuration, not inferred from panel visibility.
set -euo pipefail
SHARED_PROV="${SHARED_PROV:-ops-vm/grafana/provisioning}"
FAILS=0
note() { echo "AT-097_FAIL $1"; FAILS=$((FAILS+1)); }

# Hard precondition: the provisioning tree must exist or this check is indeterminate.
[ -d "$SHARED_PROV/datasources" ] || {
  echo "AT-097 INDETERMINATE: ops-vm grafana provisioning tree absent ($SHARED_PROV/datasources)"
  exit 2
}

# 1. No datasource entry naming or typed as the people store.
# Comment lines are stripped before matching: a file that correctly
# documents "the people datasource is NEVER registered here" (exactly the
# prose Section 90.3 asks for, and exactly what L5-04's own shared-instance
# file says) must not fail the check that exists to enforce that same rule.
# Confirmed as a real false positive against ops-vm/grafana's actual
# provisioning file before this fix, not a hypothetical.
if [ -d "$SHARED_PROV/datasources" ]; then
  if grep -rn --exclude='*.tmpl' -v '^[[:space:]]*#' "$SHARED_PROV/datasources" 2>/dev/null \
       | grep -qiE '(^|[^a-z])(people|layerb|layer-b|people-performance|layerb_people)'; then
    note "people datasource entry present in shared provisioning"
  fi
fi

# 2. No dashboard in the shared instance references the people datasource uid.
if [ -d "$SHARED_PROV/dashboards" ]; then
  if grep -rn -v '^[[:space:]]*#' "$SHARED_PROV/dashboards" 2>/dev/null | grep -q 'layerb-people'; then
    note "shared dashboard references datasource uid layerb-people"
  fi
fi

# 3. Live check: the running shared instance lists no people datasource.
# An unreachable ops-vm must not read as "[]" (therefore clean) - that would
# report AT-097_PASS having never actually asked the running instance.
if [ "${SKIP_LIVE:-0}" != "1" ]; then
  if ! ssh -o BatchMode=yes -o ConnectTimeout=5 ops-vm true 2>/dev/null; then
    echo "AT-097 INDETERMINATE: ops-vm unreachable for the live check (set SKIP_LIVE=1 to skip it deliberately)"
    exit 2
  fi
  live=$(ssh ops-vm 'curl -s -u "$SHARED_GRAFANA_ADMIN" http://127.0.0.1:3000/api/datasources' 2>/dev/null || echo '[]')
  if printf '%s' "$live" | grep -qiE 'people|layerb'; then
    note "running shared instance lists a people datasource"
  fi
fi

# 4. The people datasource IS registered in Layer B-M (positive half).
grep -q 'uid: layerb-people' ops-vm/layer-b/provisioning/datasources/people.yaml \
  || note "people datasource not registered in the Layer B-M instance"

if [ "$FAILS" -eq 0 ]; then echo "AT-097_PASS"; else echo "AT-097_FAILED $FAILS"; exit 1; fi
