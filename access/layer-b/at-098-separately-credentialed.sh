#!/usr/bin/env bash
# access/layer-b/at-098-separately-credentialed.sh
# AT-098 - "The Founder-only instance is separately credentialed":
# reaching it requires its own credential; a shared-instance login grants
# nothing there, and a direct query without that instance's credential is denied.
#
# This test has no repository-side half: every one of its four clauses is a
# live property of the two running Grafana instances. Run against real
# infrastructure. An unreachable host is reported as indeterminate, never as
# a pass - AT-098 has not "passed" just because nothing answered.
set -euo pipefail
FAILS=0
note() { echo "AT-098_FAIL $1"; FAILS=$((FAILS+1)); }

if ! ssh -o BatchMode=yes -o ConnectTimeout=5 layerb-host true 2>/dev/null; then
  echo "AT-098 INDETERMINATE: layerb-host unreachable"; exit 2
fi

# a) No credential at all -> denied.
c1=$(ssh layerb-host 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001/api/datasources')
[ "$c1" = "401" ] || note "no-credential query returned $c1, expected 401"

# b) The shared instance's admin credential -> denied on Layer B-M.
c2=$(ssh layerb-host 'curl -s -o /dev/null -w "%{http_code}" -u "$SHARED_GRAFANA_ADMIN" http://127.0.0.1:3001/api/datasources')
[ "$c2" = "401" ] || note "shared-instance credential returned $c2 on Layer B-M, expected 401"

# c) A direct datasource query without the instance credential -> denied.
c3=$(ssh layerb-host 'curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:3001/api/ds/query -H "Content-Type: application/json" -d "{}"')
[ "$c3" = "401" ] || note "unauthenticated ds/query returned $c3, expected 401"

# d) The two instances do not share an admin credential file.
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 ops-vm true 2>/dev/null; then
  echo "AT-098 INDETERMINATE: ops-vm unreachable (cannot confirm clause d, distinct credential files)"; exit 2
fi
same=$(ssh layerb-host 'sha256sum /srv/layerb/secrets/admin_password 2>/dev/null | cut -d" " -f1' || echo x)
other=$(ssh ops-vm 'sha256sum /srv/shared/secrets/admin_password 2>/dev/null | cut -d" " -f1' || echo y)
[ "$same" != "$other" ] || note "the two instances share an admin credential"

if [ "$FAILS" -eq 0 ]; then echo "AT-098_PASS"; else echo "AT-098_FAILED $FAILS"; exit 1; fi
