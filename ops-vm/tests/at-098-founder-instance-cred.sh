#!/usr/bin/env bash
# ops-vm/tests/at-098-founder-instance-cred.sh
# AT-098 - spec 100.6 / 90.3 / 90.4 (D75). Static half: the two instances are
# distinct hosts with distinct credentials, and the founder instance
# declares its own authentication restriction. Live half is ASSISTED: a
# shared-instance login must grant nothing there, and a direct query without
# that instance's credential must be denied.
#
# The runbook's draft check compares an http_port key in two grafana.ini
# files; only one grafana.ini exists on disk (ops-vm/layer-b/grafana.ini) --
# the shared instance is configured through ops-vm/stack/compose.shared.yml
# environment variables, and instance separation there is by HOST
# (ops-vm vs. layerb-host, D95), not by a differing internal port (Grafana's
# default 3000 inside both containers is unremarkable). Adapted to what is
# actually on disk (lanes/L5-98-DEEP-REVIEW.md B-05's fix direction).
set -uo pipefail
. access/tests/lib/assert.sh
F=ops-vm/layer-b/grafana.ini
STACK=ops-vm/stack/compose.shared.yml
if [ ! -f "$F" ]; then l5_indeterminate "AT-098/static" "founder grafana.ini absent: $F"; l5_exit; fi
if [ ! -f "$STACK" ]; then l5_indeterminate "AT-098/static" "shared stack definition absent: $STACK"; l5_exit; fi
ROOT_URL="$(grep -E '^root_url' "$F" | head -n 1)"
case "$ROOT_URL" in
  *layerb-host*) l5_pass "AT-098/distinct-host" ;;
  *) l5_fail "AT-098/distinct-host" "founder instance's root_url does not name a distinct host (layerb-host), got: $ROOT_URL" ;;
esac
FOUNDER_ADMIN="$(grep -E '^admin_user' "$F" | head -n 1 | sed 's/.*=[[:space:]]*//')"
SHARED_ADMIN="$(grep -oE 'GF_SECURITY_ADMIN_USER:[[:space:]]*"?[^"[:space:]]*' "$STACK" | sed 's/.*"//' || true)"
if [ -n "$FOUNDER_ADMIN" ] && [ "$FOUNDER_ADMIN" != "admin" ] && [ "$FOUNDER_ADMIN" != "$SHARED_ADMIN" ]; then
  l5_pass "AT-098/distinct-credential"
else
  l5_fail "AT-098/distinct-credential" "founder instance's admin_user ('$FOUNDER_ADMIN') is not distinct from the shared instance's"
fi
if grep -qiE 'allow(ed)?[_-]?users|allowlist|auth' "$F"; then
  l5_pass "AT-098/auth-restriction"
else
  l5_fail "AT-098/auth-restriction" "founder instance declares no authentication restriction"
fi
bash access/tests/lib/verify-evidence.sh AT-098
RC=$?
if [ "$RC" -eq 2 ]; then
  l5_indeterminate "AT-098/live" "awaiting human evidence"
elif [ "$RC" -eq 0 ]; then
  l5_pass "AT-098/live"
else
  l5_fail "AT-098/live" "evidence verification failed"
fi
l5_exit
