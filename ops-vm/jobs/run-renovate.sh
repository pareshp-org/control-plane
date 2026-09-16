#!/usr/bin/env bash
# One self-hosted Renovate pass. Repositories are enumerated from the registry,
# never listed in this file or in config.js (invariant 52).
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/renovate/renovate.env
set -a; . ops-vm/renovate/renovate.env; set +a
require_env RENOVATE_TOKEN_FILE RENOVATE_REPO_LIMIT RENOVATE_LOG_DIR
require_file "$RENOVATE_TOKEN_FILE"

repos=$(list-repositories --from-registry)   # published by lane L1/L3 provisioning
[ -n "$repos" ] || fail_closed "registry returned no repositories; refusing to run Renovate over an empty set"
count=$(echo "$repos" | wc -w)
[ "$count" -le "$RENOVATE_REPO_LIMIT" ] \
  || fail_closed "registry returned $count repositories, above the confirmed self-hosted repository limit $RENOVATE_REPO_LIMIT (Section 30.3 unverified-capability list)"

install -d -m 0750 "$RENOVATE_LOG_DIR"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
set +e
RENOVATE_TOKEN="$(cat "$RENOVATE_TOKEN_FILE")" \
RENOVATE_CONFIG_FILE=ops-vm/renovate/config.js \
RENOVATE_REPOSITORIES="$(echo "$repos" | tr ' ' ',')" \
  renovate > "$RENOVATE_LOG_DIR/renovate-$stamp.log" 2>&1
rc=$?
set -e
if [ "$rc" -eq 0 ]; then
  record_run renovate ok "repos=$count"
else
  record_run renovate failed "repos=$count rc=$rc"
  notify/bin/notify-job-result.sh renovate failed "rc=$rc"
fi
exit "$rc"
