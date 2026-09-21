#!/usr/bin/env bash
# access/layer-b/check-session-limits.sh
# Usage: check-session-limits.sh repo | check-session-limits.sh host
set -uo pipefail
MODE="${1:-repo}"
INI="ops-vm/layer-b/grafana.ini"
CONTRACT="contracts/access/access-inputs.yaml"
FAILS=0
note() { echo "SESS_FAIL $1"; FAILS=$((FAILS+1)); }
ini_get() { awk -v s="[$1]" -v k="$2" '$0==s{f=1;next} /^\[/{f=0} f&&$1==k{print $3; exit}' "$INI"; }

if [ "$MODE" = "repo" ]; then
  if [ ! -f "$CONTRACT" ]; then
    echo "SESS_BLOCKED $CONTRACT is absent (L0 Phase-0 frozen input not yet published); the two duration keys cannot be verified against it"
    exit 2
  fi
  life=$(ini_get auth login_maximum_lifetime_duration)
  idle=$(ini_get auth login_maximum_inactive_lifetime_duration)
  [ -n "$life" ] || note "login_maximum_lifetime_duration is empty - the limit is not declared"
  [ -n "$idle" ] || note "login_maximum_inactive_lifetime_duration is empty - the limit is not declared"
  [ "$life" = "$(yq -r '.layer_b.session.max_lifetime_duration // ""' "$CONTRACT")" ] \
    || note "rendered max lifetime does not match the frozen contract"
  [ "$idle" = "$(yq -r '.layer_b.session.max_inactive_lifetime_duration // ""' "$CONTRACT")" ] \
    || note "rendered inactive lifetime does not match the frozen contract"
  [ "$(ini_get auth.anonymous enabled)" = "false" ] || note "SUS-4 anonymous access is enabled"
  [ "$(ini_get auth token_rotation_interval_minutes)" = "10" ] || note "token rotation interval is not 10"
  [ "$(yq -r '.standing_unattended_session.prohibited | length' ops-vm/layer-b/session/session-limits.yaml)" = "4" ] \
    || note "the standing-unattended-session prohibition does not carry its four rows"
  if [ "$FAILS" -eq 0 ]; then echo "SESS_REPO_OK 7/7"; else echo "SESS_REPO_FAILED $FAILS"; exit 1; fi
  exit 0
fi

if [ "$MODE" = "host" ]; then
  A='-u "$LAYERB_ADMIN"'
  sa=$(ssh layerb-host "curl -s $A 'http://127.0.0.1:3001/api/serviceaccounts/search?perpage=100' | jq -r '.totalCount // 0'" 2>/dev/null || echo "")
  if [ -z "$sa" ]; then echo "SESS_HOST_UNREACHABLE layerb-host is not reachable from this environment"; exit 2; fi
  [ "$sa" = "0" ] || note "SUS-1 $sa service account(s) on Layer B-M"
  ak=$(ssh layerb-host "curl -s $A http://127.0.0.1:3001/api/auth/keys | jq -r 'length'" 2>/dev/null || echo -1)
  [ "$ak" = "0" ] || note "SUS-2 $ak API key(s) on Layer B-M"
  stale=$(ssh layerb-host "curl -s $A http://127.0.0.1:3001/api/admin/settings | jq -r '.auth.login_maximum_lifetime_duration // \"\"'" 2>/dev/null || echo "")
  [ -n "$stale" ] || note "SUS-3 the running instance reports no maximum session lifetime"
  anon=$(ssh layerb-host "curl -s $A http://127.0.0.1:3001/api/admin/settings | jq -r '.\"auth.anonymous\".enabled // \"true\"'" 2>/dev/null || echo true)
  [ "$anon" = "false" ] || note "SUS-4 the running instance permits anonymous access"
  if [ "$FAILS" -eq 0 ]; then echo "SESS_HOST_OK 4/4"; else echo "SESS_HOST_FAILED $FAILS"; exit 1; fi
  exit 0
fi
note "unknown mode $MODE"; exit 1
