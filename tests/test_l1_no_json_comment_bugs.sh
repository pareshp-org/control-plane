#!/usr/bin/env bash
# tests/test_l1_no_json_comment_bugs.sh
#
# Standalone regression test (not pytest) for the JSON-comment-in-heredoc bug
# class found (and, concurrently with this test being written, fixed) this
# session: a raw `cat > *.json <<'EOF'` ... `EOF` block writing a literal
# JSON file body, with a shell-style "#"-prefixed comment line pasted inside
# the JSON body between the markers. JSON has no comment syntax, so such a
# line makes the emitted file invalid JSON — the kind of bug that is silent
# at write time and only surfaces later when something tries to parse the
# file (a validator, jq, a schema check, ...).
#
# This test scans lanes/L1-05-tasks.md for that exact shape: it locates every
# `cat > <path>.json <<'DELIM'` (or `<<"DELIM"` / `<<DELIM`, with or without
# `cat >>`) heredoc start, reads forward to the matching closing-delimiter
# line, and flags any line inside the body whose first non-whitespace
# character is '#'. It does not flag '#' appearing inside a JSON string
# value (e.g. a URL fragment) — only a line that, once its leading
# whitespace is stripped, actually begins with '#'.
#
# Usage: bash tests/test_l1_no_json_comment_bugs.sh
# Exit 0 = pass (no such lines found), exit 1 = fail (violations printed).
#
# NOTE: this guards lanes/L1-05-tasks.md specifically, per the incident this
# session. If a concurrent fix pass for this bug class hasn't landed yet
# when this test is run, it will legitimately still fail — that is the
# correct, honest result, not a bug in the test.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET="$ROOT_DIR/lanes/L1-05-tasks.md"

fail_setup() { echo "FAIL: $*" >&2; exit 1; }

[ -f "$TARGET" ] || fail_setup "cannot find $TARGET"

# --- Scan for heredoc-comment violations ------------------------------------
# Implemented in awk for line-accurate, single-pass scanning of a 20k+ line
# file. State machine:
#   not in a heredoc -> line matches a `cat > .../*.json ... <<[-]'DELIM'`
#                        start -> remember DELIM, enter heredoc, record start
#                        line number for reporting.
#   in a heredoc      -> line equals DELIM exactly (start of line; a `<<-`
#                        form additionally tolerates leading tabs) -> close
#                        the heredoc.
#                     -> otherwise, if the line's first non-blank char is
#                        '#', record a violation (with the offending line
#                        number and the heredoc's start line/target file for
#                        context).
violations=$(awk '
  BEGIN { in_heredoc = 0 }
  {
    line = $0
    if (!in_heredoc) {
      # Match: cat > <something>.json <something> << [-] [quote] DELIM [quote]  (end of line)
      if (match(line, /cat[ \t]*>>?[ \t]*[^ \t]*\.json[^ \t]*[ \t]*<<-?[ \t]*["'"'"']?[A-Za-z_][A-Za-z0-9_]*["'"'"']?[ \t]*$/)) {
        # Pull the delimiter word out of the matched text.
        seg = substr(line, RSTART, RLENGTH)
        dash = (seg ~ /<<-/)
        # Strip everything through the last quote-or-<< marker, leaving DELIM[quote]?
        sub(/^.*<<-?[ \t]*/, "", seg)
        gsub(/["'"'"']/, "", seg)
        delim = seg
        in_heredoc = 1
        allow_leading_ws = dash
        start_line = NR
        start_text = line
        next
      }
    } else {
      test = line
      if (allow_leading_ws) sub(/^\t+/, "", test)
      if (test == delim) {
        in_heredoc = 0
        next
      }
      trimmed = line
      sub(/^[ \t]+/, "", trimmed)
      if (trimmed ~ /^#/) {
        printf("%d: comment line inside JSON heredoc opened at line %d (%s): %s\n", NR, start_line, start_text, line)
      }
      next
    }
  }
' "$TARGET")

if [ -n "$violations" ]; then
  echo "FAIL: found #-comment line(s) inside raw JSON heredoc(s) in $TARGET" >&2
  echo "$violations" >&2
  echo "" >&2
  n=$(printf '%s\n' "$violations" | grep -c .)
  echo "FAIL: $n violation(s) found — JSON has no comment syntax; these heredocs will emit invalid JSON." >&2
  exit 1
fi

echo "PASS: no #-comment lines found inside raw *.json heredocs in lanes/L1-05-tasks.md"
exit 0
