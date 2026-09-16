#!/usr/bin/env bash
# ops-vm/layer-b/accesslog/review.sh
# The Section 84.5 calibration-cadence review of the access log.
# It counts and summarises. It never renders evidence.
set -euo pipefail
DIR="${LAYERB_MNT:-/srv/layerb/encrypted}/accesslog"
SINCE_DAYS="${1:-90}"
[ -d "$DIR" ] || { echo "ACCESSLOG_MISSING"; exit 1; }
n=$(find "$DIR" -name '*.yaml' -mtime "-$SINCE_DAYS" | wc -l | tr -d ' ')
# Two independent pitfalls here, both confirmed by actually running this
# against fixtures rather than assumed away:
#   1. `grep pattern $(find ...)` with zero matching files leaves grep with
#      no file operand, so it reads stdin and hangs a non-interactive script
#      forever. `find -exec grep ... +` fixes this: it simply skips invoking
#      grep when there is nothing to hand it.
#   2. Under `set -e -o pipefail` (both in force here), grep's ordinary
#      "found nothing" exit status of 1 - not an error, just no matches -
#      still propagates through the pipe to wc/tr and aborts the script on
#      the assignment itself, one line before the summary it computed would
#      ever print. `(... || true)` absorbs exactly that "no matches" case
#      without hiding a real failure, since find and wc/tr do not fail here.
actors=$(find "$DIR" -name '*.yaml' -mtime "-$SINCE_DAYS" -exec grep -h '^actor:' {} + 2>/dev/null || true)
actors=$(printf '%s\n' "$actors" | sort -u | grep -c '^actor:' || true)
machine=$(find "$DIR" -name '*.yaml' -exec grep -hE '^actor: ".*(\[bot\]|reconciler|records-writer)' {} + 2>/dev/null || true)
machine=$(printf '%s\n' "$machine" | grep -c '^actor:' || true)
echo "ACCESSLOG_REVIEW events=$n distinct_actors=$actors machine_actors=$machine"
[ "$machine" -eq 0 ] || { echo "MACHINE_ACTOR_PRESENT"; exit 1; }
