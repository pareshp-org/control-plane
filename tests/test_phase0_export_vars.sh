#!/usr/bin/env bash
# tests/test_phase0_export_vars.sh
#
# Standalone regression test (not pytest) for the "variable not exported,
# invisible in bash -c subprocess" bug class found in run-phase-0.sh's
# REPO_VISIBILITY. REPO_VISIBILITY is set once near the top of the script
# and then relied on later (e.g. in the `gh repo create ... --$REPO_VISIBILITY`
# calls). If it is assigned as a bare shell variable (`REPO_VISIBILITY="public"`)
# instead of an exported one (`export REPO_VISIBILITY="public"`), it stays a
# shell-local variable of run-phase-0.sh's own process: any child process
# spawned as `bash -c '...'` (or any other subprocess that does not inherit
# non-exported shell variables) sees an EMPTY REPO_VISIBILITY rather than
# "public"/"private", silently breaking flag construction like --$REPO_VISIBILITY.
#
# This test does not hand-copy the value. It locates the live REPO_VISIBILITY
# assignment line in run-phase-0.sh and asserts the line itself begins with
# "export " — a simple but effective regression guard for this bug class.
#
# Usage: bash tests/test_phase0_export_vars.sh
# Exit 0 = pass, exit 1 = fail (message printed).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RP0="$ROOT_DIR/run-phase-0.sh"

fail() { echo "FAIL: $*" >&2; exit 1; }

[ -f "$RP0" ] || fail "cannot find run-phase-0.sh at $RP0"

# --- Locate the REPO_VISIBILITY assignment line(s) --------------------------
# Match lines that ASSIGN to REPO_VISIBILITY (with an optional leading
# "export "), not lines that merely READ it (e.g. "${REPO_VISIBILITY:-public}"
# or "--$REPO_VISIBILITY"). An assignment line looks like:
#   REPO_VISIBILITY="public"
#   export REPO_VISIBILITY="public"
assign_lines=$(grep -nE '^[[:space:]]*(export[[:space:]]+)?REPO_VISIBILITY=' "$RP0")

[ -n "$assign_lines" ] \
  || fail "could not find a REPO_VISIBILITY assignment line in $RP0 (has it been renamed or removed?)"

n_assign=$(printf '%s\n' "$assign_lines" | grep -c .)
[ "$n_assign" -eq 1 ] \
  || fail "expected exactly 1 REPO_VISIBILITY assignment line, found $n_assign:
$assign_lines"

# Strip the "N:" line-number prefix grep -n adds, keep the source text.
assign_line="${assign_lines#*:}"

# --- The actual regression guard: the assignment must be exported -----------
# A bare "REPO_VISIBILITY=..." is invisible to any `bash -c` (or similar)
# subprocess; only "export REPO_VISIBILITY=..." makes it visible there.
printf '%s\n' "$assign_line" | grep -qE '^[[:space:]]*export[[:space:]]+REPO_VISIBILITY=' \
  || fail "REPO_VISIBILITY is assigned but not exported — invisible to bash -c subprocesses. Line was:
$assign_line
Fix: change it to start with 'export ' (e.g. export REPO_VISIBILITY=\"public\")."

echo "PASS: REPO_VISIBILITY assignment in run-phase-0.sh is exported (visible to subprocesses)"
exit 0
