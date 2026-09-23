#!/usr/bin/env bash
# ops-vm/tests/at-108-console-readonly.sh
# AT-108 - spec 100.6. Static half asserts the spec 37.8 cage keys; the live
# half (four refusals plus one positive control) is ASSISTED and must run
# from the ops console's own OS user and credentials on the ops-console VPS.
set -uo pipefail
. access/tests/lib/assert.sh
CFG=infra/hermes/ops-console.yaml
if [ ! -f "$CFG" ]; then
  l5_indeterminate "AT-108/static" "PRE-H missing: $CFG (subsystem J, unassigned in PARTITION v1 as of this writing -- see lanes/L5-98-DEEP-REVIEW.md B-14)"
  l5_exit
fi
chk() {
  local key="$1" want="$2" got
  got="$(yq -r "$key" "$CFG")"
  if [ "$got" = "$want" ]; then l5_pass "AT-108/static$key"; else l5_fail "AT-108/static$key" "expected $want, got '$got'"; fi
}
chk '.memory.memory_enabled' 'false'
chk '.model.background_review.enabled' 'false'
chk '.approvals.cron_mode' 'deny'
chk '.security.allow_lazy_installs' 'false'
chk '.gateway.unauthorized_dm_behavior' 'ignore'
ALLOW="$(yq -r '.gateway.sender_allowlist | length' "$CFG" 2>/dev/null || echo 0)"
if [ "$ALLOW" -ge 1 ]; then l5_pass "AT-108/static-allowlist"; else l5_fail "AT-108/static-allowlist" "sender allowlist is empty"; fi
HOME_DIR="$(yq -r '.hermes_home // ""' "$CFG")"
OS_USER="$(yq -r '.os_user // ""' "$CFG")"
if [ -n "$HOME_DIR" ] && [ -n "$OS_USER" ]; then
  l5_pass "AT-108/static-isolation"
else
  l5_fail "AT-108/static-isolation" "instance declares no separate os_user and HERMES_HOME (spec 37.8)"
fi
bash access/tests/lib/verify-evidence.sh AT-108
RC=$?
if [ "$RC" -eq 2 ]; then
  l5_indeterminate "AT-108/live" "awaiting human evidence"
elif [ "$RC" -eq 0 ]; then
  l5_pass "AT-108/live"
else
  l5_fail "AT-108/live" "evidence verification failed"
fi
l5_exit
