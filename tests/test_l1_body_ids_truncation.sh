#!/usr/bin/env bash
# tests/test_l1_body_ids_truncation.sh
#
# Standalone regression test (not pytest) for the L1 body_ids() truncation
# bug fixed this session: the L1 heading-id regex in _concordance-check.sh
# was `[0-9]{3}` (exactly 3 digits), which truncated a 4-digit heading like
# "### L1-1001" down to "### L1-100" — colliding with the real "L1-100"
# heading, and `sort -u` then silently collapsed the two into one, under-
# counting the L1 body by exactly 1 (true count 157, was seen as 156). See
# _concordance-check.sh lines ~61-65 for the incident writeup, and line 33
# for the fix ([0-9]{3,4}).
#
# This test does NOT hand-copy the regex (a copy could silently drift from
# the real script and stop testing anything). Instead it extracts the LIVE
# body_ids() function straight out of _concordance-check.sh and runs it
# against a small fixture lane directory, so a future regression to
# exactly-3-digits is caught for real.
#
# Usage: bash tests/test_l1_body_ids_truncation.sh
# Exit 0 = pass, exit 1 = fail (message printed).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CC="$ROOT_DIR/_concordance-check.sh"

fail() { echo "FAIL: $*" >&2; exit 1; }

[ -f "$CC" ] || fail "cannot find _concordance-check.sh at $CC"

# --- Extract the live body_ids() function definition from the script -------
# (from the "body_ids(){" line through its closing "sort -u; }" line)
func_src=$(awk '
  /^body_ids\(\)\{/ { flag=1 }
  flag { print }
  flag && index($0, "sort -u; }") > 0 { flag=0 }
' "$CC")

[ -n "$func_src" ] || fail "could not extract body_ids() from $CC (has it moved or been renamed?)"
printf '%s\n' "$func_src" | grep -q '^body_ids(){' \
  || fail "extraction did not start at 'body_ids(){' — got:
$func_src"
printf '%s\n' "$func_src" | grep -q 'sort -u; }$' \
  || fail "extraction did not end at the closing brace — got:
$func_src"

# --- Build a minimal fixture lane directory ---------------------------------
TMPDIR_FIXTURE=$(mktemp -d) || fail "mktemp -d failed"
trap 'rm -rf "$TMPDIR_FIXTURE"' EXIT

# body_ids()'s L1 case does `awk 'NR>=240'` before matching, so fixture
# headings must live at/after line 240 to be seen at all. We include both a
# 3-digit id (L1-100) and a 4-digit id (L1-1001) so this test also catches
# the collision case: the bug didn't just truncate, it truncated L1-1001
# into the SAME string as the real L1-100 heading, and sort -u then hid the
# loss entirely. A test that only checked "L1-1001 is absent" would miss a
# regression that reintroduces the collision without dropping the count in
# an obvious way, so we assert both ids are present, distinct, and that the
# total is exactly 2.
{
  for i in $(seq 1 245); do echo "filler line $i"; done
  echo "### L1-100"
  echo "### L1-1001"
} > "$TMPDIR_FIXTURE/L1-05-tasks.md"

# --- Load ONLY the extracted function (no other top-level script code runs,
# so this never touches real lane files), then call it -----------------------
eval "$func_src"

L="$TMPDIR_FIXTURE"
result=$(body_ids L1)

echo "$result" | grep -qx 'L1-1001' \
  || fail "body_ids() did not extract the full 'L1-1001' id — got:
$result"

echo "$result" | grep -qx 'L1-100' \
  || fail "expected 'L1-100' to also be present (and distinct from L1-1001) — got:
$result"

n=$(printf '%s\n' "$result" | grep -c .)
[ "$n" -eq 2 ] || fail "expected exactly 2 distinct ids (L1-100, L1-1001), got $n:
$result"

echo "PASS: body_ids() L1 pattern extracts 'L1-1001' in full, distinct from 'L1-100' (no truncation)"
exit 0
