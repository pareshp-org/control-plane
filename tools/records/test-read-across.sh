#!/usr/bin/env bash
# tools/records/test-read-across.sh -- charter-named entry point, DoD-16.
# Master Spec v4.0 Section 40.1 line 3671: a check that cannot reach the
# records repository fails closed rather than reporting zero.
# This is the one command in this lane whose PASS is a non-zero exit
# (L4-06-tasks.md section 4.2): read-across correctly failing closed on
# an unreachable root makes this wrapper exit 1. A zero exit here means
# read-across returned a count instead of failing closed -- a STOP.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ "${1:-}" = "--unreachable" ]; then
  out="$(RECORDS_ROOT="/nonexistent/l4/unreachable" "$HERE/read-across" --count events 2>&1)"; rc=$?
  echo "$out"
  if [ "$rc" -ne 0 ] && printf '%s' "$out" | grep -q 'FAIL-CLOSED'; then exit 1; fi
  echo "READ-ACROSS DID NOT FAIL CLOSED"; exit 0
fi
echo "usage: test-read-across.sh --unreachable"; exit 2
