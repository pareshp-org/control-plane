#!/usr/bin/env bash
# ops-vm/layer-b/check-instance.sh
# Usage: check-instance.sh repo | check-instance.sh host
set -euo pipefail
MODE="${1:-repo}"
INI="ops-vm/layer-b/grafana.ini"
COMPOSE="ops-vm/layer-b/compose.yaml"
fail() { echo "INST_FAIL $1"; exit 1; }
ini_get() { awk -v s="[$1]" -v k="$2" '$0==s{f=1;next} /^\[/{f=0} f&&$1==k{print $3; exit}' "$INI"; }

if [ "$MODE" = "repo" ]; then
  [ "$(ini_get auth.anonymous enabled)" = "false" ] || fail "anonymous access not disabled"
  [ "$(ini_get auth.basic enabled)" = "false" ]     || fail "basic auth not disabled"
  [ "$(ini_get users allow_sign_up)" = "false" ]    || fail "sign-up not disabled"
  [ "$(ini_get security admin_user)" = "layerb-admin" ] || fail "instance does not carry its own admin credential"
  [ "$(ini_get unified_alerting enabled)" = "false" ] || fail "alerting enabled - Section 90.2 forbids relaying people intelligence"
  grep -q 'allowUiUpdates: false' ops-vm/layer-b/provisioning/dashboards/layer-b.yaml || fail "UI updates not disabled"
  grep -q '127.0.0.1:3001:3000' "$COMPOSE" || fail "instance not bound to the private path"
  grep -q '0.0.0.0:' "$COMPOSE" && fail "instance publishes on 0.0.0.0"
  if grep -nE '(password|secret)[[:space:]]*[:=][[:space:]]*[^$#[:space:]]' "$COMPOSE" \
     | grep -vE '__FILE|secrets:|file:' | grep -q .; then
    fail "literal secret in compose"
  fi
  echo "INST_REPO_OK 8/8"
  exit 0
fi

if [ "$MODE" = "host" ]; then
  # An unreachable alias must read as INDETERMINATE, never as a passing
  # criterion: "docker inspect failed" and "grafana-layerb is not running"
  # are different facts, and criterion 8 (no route from ops-vm) must not be
  # satisfied merely because ops-vm itself could not be reached to ask.
  if ! ssh -o BatchMode=yes -o ConnectTimeout=5 layerb-host true 2>/dev/null; then
    echo "INST_HOST_INDETERMINATE layerb-host unreachable"; exit 2
  fi
  up=$(ssh layerb-host 'docker inspect -f "{{.State.Running}}" grafana-layerb 2>/dev/null' || echo false)
  [ "$up" = "true" ] || fail "grafana-layerb not running on layerb-host"
  code=$(ssh layerb-host 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001/api/org' || echo 000)
  [ "$code" = "401" ] || fail "unauthenticated /api/org returned $code, expected 401"
  if ! ssh -o BatchMode=yes -o ConnectTimeout=5 ops-vm true 2>/dev/null; then
    echo "INST_HOST_INDETERMINATE ops-vm unreachable (cannot confirm criterion 8, no route)"; exit 2
  fi
  ext=$(ssh ops-vm 'curl -s -o /dev/null -m 5 -w "%{http_code}" http://layerb-host:3001/api/org' || echo 000)
  [ "$ext" = "000" ] || fail "Layer B-M reachable from ops-vm on $ext, expected no route"
  echo "INST_HOST_OK 3/3"
  exit 0
fi
fail "unknown mode $MODE"
