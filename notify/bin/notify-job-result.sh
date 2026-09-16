#!/usr/bin/env bash
# The single job-result notifier every operations-VM job calls.
# Section 92.11: a push event is delivered to the designated messaging channel,
# which is a configuration value and never a hard-coded destination.
# Section 44.3: job and backup failures alert on the product discipline.
# Usage: notify-job-result.sh <job-name> <ok|failed> [detail]
set -euo pipefail
JOB="${1:?usage: notify-job-result.sh <job-name> <ok|failed> [detail]}"
STATUS="${2:?usage: notify-job-result.sh <job-name> <ok|failed> [detail]}"
DETAIL="${3:-}"
case "$STATUS" in
  ok|failed) ;;
  *) echo "NOTIFY: FAIL-CLOSED (status must be ok or failed; got '$STATUS')"; exit 1 ;;
esac
CFG="${NOTIFY_ENV_FILE:-notify/bin/notify.env}"
[ -f "$CFG" ] || { echo "NOTIFY: FAIL-CLOSED (no $CFG)"; exit 1; }
set -a; . "$CFG"; set +a
[ -n "${DESIGNATED_CHANNEL_WEBHOOK_URL:-}" ] \
  || { echo "NOTIFY: FAIL-CLOSED (DESIGNATED_CHANNEL_WEBHOOK_URL is empty)"; exit 1; }
body=$(printf '{"job":"%s","status":"%s","host":"%s","at":"%s","detail":"%s"}' \
  "$JOB" "$STATUS" "$(hostname)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$DETAIL")
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 \
  -H 'Content-Type: application/json' --data "$body" "$DESIGNATED_CHANNEL_WEBHOOK_URL" || echo 000)
case "$code" in
  2*) echo "NOTIFY: SENT $JOB $STATUS" ;;
  *)  echo "NOTIFY: FAIL-CLOSED (webhook http $code)"; exit 1 ;;
esac
