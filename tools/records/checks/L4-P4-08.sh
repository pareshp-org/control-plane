#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P4-08 - read-across, the fail-closed cross-repository reader
# Charter DoD-16. Master Spec v4.0 Section 40.1 line 3671: a check that
# cannot reach the records repository fails closed rather than
# reporting zero.
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"
RA="$CP_DIR/tools/records/read-across"
RAPY="$CP_DIR/tools/records/read_across.py"
TRA="$CP_DIR/tools/records/test-read-across.sh"

[[ -x "$RA"   ]] || { echo "ABSENT-OR-NOT-EXECUTABLE: $RA" >&2; exit 1; }
[[ -f "$RAPY" ]] || { echo "ABSENT: $RAPY" >&2; exit 1; }
[[ -x "$TRA"  ]] || { echo "ABSENT-OR-NOT-EXECUTABLE: $TRA" >&2; exit 1; }

# Positive: a reachable, empty store is a legitimate zero, never fail-closed.
TMP="$(mktemp -d)"
mkdir -p "$TMP/events"
if OUT="$(RECORDS_ROOT="$TMP" "$RA" --count events 2>&1)"; then RC=0; else RC=$?; fi
[ "$RC" -eq 0 ] || { echo "expected exit 0 on reachable empty store, got $RC: $OUT" >&2; rm -rf "$TMP"; exit 1; }
printf '%s' "$OUT" | grep -q '^COUNT 0 ' || { echo "expected a zero count line, got: $OUT" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

# Negative fixture (bad_fixture): an unreachable records root must fail
# closed and must never be reported as a success or as a count of zero.
if OUT="$(RECORDS_ROOT="/nonexistent/l4/bad_fixture" "$RA" --count events 2>&1)"; then RC=0; else RC=$?; fi
[ "$RC" -ne 0 ] || { echo "neg-fixture: unreachable root did not fail" >&2; exit 1; }
printf '%s' "$OUT" | grep -q 'FAIL-CLOSED' || { echo "neg-fixture: unreachable root did not print FAIL-CLOSED: $OUT" >&2; exit 1; }

# The charter-named entry point proves the identical contract end to end.
if bash "$TRA" --unreachable >/dev/null 2>&1; then RC=0; else RC=$?; fi
[ "$RC" -ne 0 ] || { echo "test-read-across.sh --unreachable exited 0; the one command whose pass is non-zero must not" >&2; exit 1; }

echo "CHECK L4-P4-08 PASS"
