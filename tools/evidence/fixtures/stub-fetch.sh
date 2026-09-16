#!/usr/bin/env bash
# Deterministic stand-in for the /version network fetch. Selected by EV_FETCH.
# Synthetic only: every host is under .invalid (RFC 2606), every digest is a
# fixture digest. Section 38.3 line 3468 - fixtures carry no real data.
set -euo pipefail
case "${1:-}" in
  https://ok.invalid/version)
    printf '{"digest":"sha256:aaaa000000000000000000000000000000000000000000000000000000000001","build":"fixture"}' ;;
  https://drift.invalid/version)
    printf '{"digest":"sha256:bbbb000000000000000000000000000000000000000000000000000000000009","build":"fixture"}' ;;
  https://down.invalid/version)
    echo "stub: connection refused" >&2; exit 7 ;;
  *)
    echo "stub: unknown target ${1:-}" >&2; exit 6 ;;
esac
