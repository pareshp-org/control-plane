#!/usr/bin/env bash
# infra/tests/at-109-egress-wall.sh
# AT-109 - spec 100.6. Static half proves the wall lives OUTSIDE the harness.
# The live half (two refusals, two permits, one wall-clock stop) is ASSISTED
# and must be executed from inside the background worker container.
set -uo pipefail
. access/tests/lib/assert.sh
ALLOW=infra/egress/background-host-allowlist.conf
STOPU=infra/systemd/background-window-stop.service
WORKER=infra/hermes/background-worker.yaml
if [ ! -f "$ALLOW" ]; then l5_indeterminate "AT-109/static" "PRE-I missing: $ALLOW (subsystem J, unassigned in PARTITION v1 as of this writing, lanes/L5-98-DEEP-REVIEW.md B-14)"; l5_exit; fi
if [ ! -f "$STOPU" ]; then l5_indeterminate "AT-109/static" "PRE-J missing: $STOPU"; l5_exit; fi
BAD=0
while IFS= read -r line; do
  case "$line" in ''|'#'*) continue ;; esac
  case "$line" in
    *github*|*mirror*|*inference*|*localhost*|10.*|192.168.*|172.1[6-9].*|172.2[0-9].*|172.3[01].*) ;;
    *) l5_fail "AT-109/static-allowlist" "unexpected egress destination: $line"; BAD=1 ;;
  esac
done < "$ALLOW"
[ "$BAD" -eq 0 ] && l5_pass "AT-109/static-allowlist"
if grep -qE 'OnCalendar|RuntimeMaxSec|ExecStop' "$STOPU"; then
  l5_pass "AT-109/static-stop-is-systemd"
else
  l5_fail "AT-109/static-stop-is-systemd" "unit declares no wall-clock stop mechanism"
fi
if [ -f "$WORKER" ] && yq -e '.egress // .network_allowlist' "$WORKER" >/dev/null 2>&1; then
  l5_fail "AT-109/static-wall-outside" "harness config declares egress control; spec 37.8 puts the wall outside the harness"
else
  l5_pass "AT-109/static-wall-outside"
fi
bash access/tests/lib/verify-evidence.sh AT-109
RC=$?
if [ "$RC" -eq 2 ]; then
  l5_indeterminate "AT-109/live" "awaiting human evidence"
elif [ "$RC" -eq 0 ]; then
  l5_pass "AT-109/live"
else
  l5_fail "AT-109/live" "evidence verification failed"
fi
l5_exit
