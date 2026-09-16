#!/usr/bin/env bash
# assert-append-only.sh - Section 99.2 row F deliverable F-c, "append-only
# history with effective dating".
#
# Spec:
#   Section 63.1 line 5409 - "state transitions with start_date and end_date -
#     effective-dating, never in-place mutation - plus git history in the
#     control-plane repository as the durable record."
#   Section 97.2 line 8888 - records "never edit in place (corrections are
#     follow-up records)".
#   Section 97.3 line 8929 - one file per event, "never a concurrent append to a
#     shared period file".
#   Section 97.6 line 8990 - the scope of append-only permanence.
#   D107 - the no-bypass ruleset on the records repository is the enforcement;
#     this script is the check that runs before the ruleset ever has to.
#
# Store prefixes are PASSED IN. This script hard-codes no path into the
# records or events trees - PARTITION.md rule 4.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/lib/common.sh"

DIFF=""
PREFIXES=()
while [ $# -gt 0 ]; do
  case "$1" in
    --diff)         DIFF="${2:-}";        shift 2 ;;
    --store-prefix) PREFIXES+=("${2:-}"); shift 2 ;;
    *) ev_die "BAD_ARG" "unknown argument: $1" ;;
  esac
done
[ -n "$DIFF" ] || ev_die "BAD_ARG" "--diff is required"
[ "${#PREFIXES[@]}" -gt 0 ] || ev_die "BAD_ARG" "at least one --store-prefix is required"
ev_require_file "$DIFF" "DIFF_ABSENT"

VIOLATIONS=0
CHECKED=0
while IFS=$'\t' read -r STATUS PATH1 PATH2; do
  [ -n "${STATUS:-}" ] || continue
  for P in "${PREFIXES[@]}"; do
    case "$PATH1" in
      "$P"*)
        CHECKED=$((CHECKED+1))
        case "$STATUS" in
          A) ;;
          M) printf '%s APPEND_ONLY_VIOLATION: in-place edit of %s\n' "$EV_FAIL_PREFIX" "$PATH1" >&2
             VIOLATIONS=$((VIOLATIONS+1)) ;;
          D) printf '%s APPEND_ONLY_VIOLATION: deletion of %s\n' "$EV_FAIL_PREFIX" "$PATH1" >&2
             VIOLATIONS=$((VIOLATIONS+1)) ;;
          R*) printf '%s APPEND_ONLY_VIOLATION: rename of %s to %s\n' "$EV_FAIL_PREFIX" "$PATH1" "${PATH2:-?}" >&2
             VIOLATIONS=$((VIOLATIONS+1)) ;;
          *) printf '%s APPEND_ONLY_VIOLATION: status %s on %s\n' "$EV_FAIL_PREFIX" "$STATUS" "$PATH1" >&2
             VIOLATIONS=$((VIOLATIONS+1)) ;;
        esac ;;
    esac
  done
done < "$DIFF"

if [ "$VIOLATIONS" -gt 0 ]; then
  printf '%s APPEND_ONLY_FAILED violations=%d\n' "$EV_FAIL_PREFIX" "$VIOLATIONS" >&2
  exit 5
fi
ev_ok "APPEND_ONLY checked=$CHECKED"
