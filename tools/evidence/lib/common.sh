#!/usr/bin/env bash
# Lane 2 / subsystem F shared library.
# Spec: MultiProduct_MasterSpec_v4.0.md Section 32 (lines 2803-2828).
# RULE (PARTITION.md rule 4): nothing in tools/evidence/ may reference a path
# under the schemas, registries, reconciler, metrics or access trees owned by
# other lanes. Every foreign path is resolved from contracts/ at runtime.
set -euo pipefail

EV_FAIL_PREFIX="EVIDENCE-FAIL"
EV_OK_PREFIX="EVIDENCE-OK"

ev_die() {            # ev_die <EXACT_TOKEN> <human text>
  printf '%s %s: %s\n' "$EV_FAIL_PREFIX" "$1" "$2" >&2
  exit 1
}

ev_ok() {             # ev_ok <EXACT_TOKEN>
  printf '%s %s\n' "$EV_OK_PREFIX" "$1"
}

ev_require_file() {   # ev_require_file <path> <TOKEN>
  [ -f "$1" ] || ev_die "$2" "required file absent: $1"
}

ev_require_cmd() {    # ev_require_cmd <binary>
  command -v "$1" >/dev/null 2>&1 || ev_die "MISSING_TOOL" "$1 not on PATH"
}

# UTC with offset, per Section 97.1 (line 8838): "Every record and event
# timestamp is stored in UTC with its offset".
ev_now_utc() { date -u +%Y-%m-%dT%H:%M:%S+00:00; }
