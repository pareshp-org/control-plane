#!/usr/bin/env bash
# The monitoring stack's own heartbeat to the external watchdog (D94, 51.5).
# This host EMITS the heartbeat; it never evaluates it. Evaluation is the whole
# point of putting the watchdog elsewhere: a dead observer emits exactly what a
# healthy estate emits (Section 46.6, Monitoring stack unavailable).
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/deadman/deadman.env
set -a; . ops-vm/deadman/deadman.env; set +a
require_env DEADMAN_CHECKIN_URL DEADMAN_METRICS_DIR
install -d -m 0750 "$DEADMAN_METRICS_DIR"
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$DEADMAN_CHECKIN_URL" || echo 000)
case "$code" in
  2*) printf 'ops_vm_deadman_last_checkin_timestamp %s\n' "$(date -u +%s)" \
        > "$DEADMAN_METRICS_DIR/deadman.prom"
      record_run deadman-heartbeat ok "http=$code" ;;
  *)  record_run deadman-heartbeat failed "http=$code"
      fail_closed "watchdog check-in failed with http $code; the switch will fire on its own grace period" ;;
esac
