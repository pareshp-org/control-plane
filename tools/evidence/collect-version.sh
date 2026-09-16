#!/usr/bin/env bash
# collect-version.sh - the GET /version observation collector.
#
# Spec: Section 32 question 11 (line 2821); Section 41.2 (lines 3717-3730) -
# "the digest it reports must equal the approved digest, and any mismatch is a
# P0 investigation". Section 53.1 (line 4680) - a run whose comparison set
# silently narrowed is itself drift, so an unreachable target still emits a line.
#
# TRANSPORT IS NOT DECIDED HERE. The runner and the scrape credential are
# DECISION REQUIRED D-L2-09; the caller supplies them. This script reads a
# bearer token, if any, from EV_VERSION_TOKEN and names no secret at all.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/lib/common.sh"

TARGETS=""; OUT=""; ONLY=""; STRICT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --targets)  TARGETS="${2:-}"; shift 2 ;;
    --out)      OUT="${2:-}";     shift 2 ;;
    --product)  ONLY="${2:-}";    shift 2 ;;
    --strict)   STRICT=1;         shift ;;
    *) ev_die "BAD_ARG" "unknown argument: $1" ;;
  esac
done
[ -n "$TARGETS" ] || ev_die "BAD_ARG" "--targets is required"
[ -n "$OUT" ]     || ev_die "BAD_ARG" "--out is required"
ev_require_file "$TARGETS" "TARGETS_ABSENT"
ev_require_cmd python3

# EV_FETCH lets the fixture suite substitute a deterministic stand-in for the
# network. Unset, the real transport is curl.
ev_fetch() {   # ev_fetch <url>  -> body on stdout, non-zero on transport failure
  if [ -n "${EV_FETCH:-}" ]; then "$EV_FETCH" "$1"; return $?; fi
  ev_require_cmd curl
  local -a auth=()
  if [ -n "${EV_VERSION_TOKEN:-}" ]; then
    auth=(--header "Authorization: Bearer ${EV_VERSION_TOKEN}")
  fi
  curl --fail --silent --show-error --max-time 10 ${auth[@]+"${auth[@]}"} "$1"
}

ROWS="$(python3 "$HERE/lib/read-targets.py" "$TARGETS" "$ONLY")" || exit 2

: > "$OUT"
INCOMPLETE=0
ERRFILE="$(mktemp)"
trap 'rm -f "$ERRFILE"' EXIT
while IFS=$'\t' read -r PRODUCT URL FIELD PROFILE; do
  [ -n "$PRODUCT" ] || continue
  BODY=""
  ERR=""
  : > "$ERRFILE"
  if ! BODY="$(ev_fetch "$URL" 2>"$ERRFILE")"; then
    ERR="$(head -c 200 "$ERRFILE" | tr '\n' ' ')"
    [ -n "$ERR" ] || ERR="transport failure"
    BODY=""
  fi
  printf '%s' "$BODY" | python3 "$HERE/lib/emit-observation.py" \
      "$PRODUCT" "$FIELD" "$PROFILE" "$(ev_now_utc)" "$ERR" "$URL" >> "$OUT"
  if [ -n "$ERR" ]; then INCOMPLETE=$((INCOMPLETE+1)); fi
done <<< "$ROWS"

if [ "$INCOMPLETE" -gt 0 ]; then
  printf '%s OBSERVATION_INCOMPLETE: %d target(s) unobserved\n' \
    "$EV_FAIL_PREFIX" "$INCOMPLETE" >&2
  if [ "$STRICT" = "1" ]; then exit 4; fi
fi
ev_ok "OBSERVATIONS_COLLECTED count=$(wc -l < "$OUT" | tr -d ' ')"
