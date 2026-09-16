#!/usr/bin/env bash
# Shared library for every operations-VM job. Fail closed (invariant 80).
set -euo pipefail

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >&2; }

fail_closed() { log "FAIL-CLOSED: $*"; exit 1; }

require_env() {
  local missing=0 k
  for k in "$@"; do
    if [ -z "${!k:-}" ]; then log "missing required key: $k"; missing=1; fi
  done
  [ "$missing" -eq 0 ] || fail_closed "required configuration is absent"
}

require_file() { [ -f "$1" ] || fail_closed "required file absent: $1"; }

# Every job writes its result; a clean run is recorded as clean (Section 53.1).
record_run() {
  local job="$1" status="$2" detail="${3:-}"
  local out="${OPS_VM_RUN_DIR:-/var/lib/ops-vm/runs}"
  mkdir -p "$out"
  printf 'job: %s\nstatus: %s\nat: %s\nhost: %s\ndetail: %s\n' \
    "$job" "$status" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(hostname)" "$detail" \
    > "$out/$(date -u +%Y%m%dT%H%M%SZ)-$job.yaml"
}
