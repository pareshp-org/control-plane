#!/usr/bin/env bash
# Bring up the shared stack from pinned digests. Idempotent; a rebuild replays it.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/stack/versions.env
require_file ops-vm/stack/network.env
ops-vm/checks/versions-pinned.sh ops-vm/stack/versions.env
set -a; . ops-vm/stack/versions.env; . ops-vm/stack/network.env; set +a

install -d -m 0750 /etc/ops-vm /etc/ops-vm/targets
envsubst < ops-vm/prometheus/prometheus.yml.tmpl > /etc/ops-vm/prometheus.yml

docker compose -f ops-vm/stack/compose.shared.yml --env-file ops-vm/stack/versions.env pull
docker compose -f ops-vm/stack/compose.shared.yml --env-file ops-vm/stack/versions.env up -d
ops-vm/checks/stack-loopback-only.sh
record_run stack-up ok
