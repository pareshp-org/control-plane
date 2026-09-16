#!/usr/bin/env bash
# Scheduled Scorecard scan. Repositories are enumerated from the registry, never
# from a list in this file (invariant 52: product count is never hard-coded).
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/scorecard/config.env
set -a; . ops-vm/scorecard/config.env; set +a
require_env SCORECARD_OUTPUT_DIR SCORECARD_TOKEN_FILE
install -d -m 0750 "$SCORECARD_OUTPUT_DIR"

repos=$(list-repositories --from-registry)   # published by lane L1/L3 provisioning
[ -n "$repos" ] || fail_closed "registry returned no repositories; refusing to scan an empty set"

rc=0
for r in $repos; do
  GITHUB_AUTH_TOKEN="$(cat "$SCORECARD_TOKEN_FILE")" \
    scorecard --repo="$r" --format=json > "$SCORECARD_OUTPUT_DIR/${r//\//_}.json" || rc=1
done
if [ "$rc" -eq 0 ]; then
  record_run scorecard ok "repos=$(echo "$repos" | wc -w)"
else
  record_run scorecard failed "one or more scans failed"
  notify/bin/notify-job-result.sh scorecard failed
fi
exit "$rc"
