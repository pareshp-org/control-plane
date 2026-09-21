#!/usr/bin/env bash
# Lane 2 — flat-record key reader.
# Records are flat top-level YAML key/value documents; the deployment-record
# shape is printed in MultiProduct_MasterSpec_v4.0.md Section 97.2 (lines 8843-8926).
# Dependency-free by design: this runs inside the production digest gate, and a
# missing interpreter must never be the reason the gate cannot answer.
# Contract: record_key <file> <key>
#   exit 0 -> the single value is printed on stdout with no trailing newline
#   exit 3 -> the file is unreadable, or the key is absent or repeated
# There is no default-value path. Ambiguity is failure (Lane 2 rule P2-B).

record_key() {
  local f="$1" k="$2" n raw
  if [ ! -f "$f" ]; then
    printf 'RECORD_UNREADABLE file=%s\n' "$f" >&2
    return 3
  fi
  n="$(grep -cE "^${k}:[[:space:]]" "$f" 2>/dev/null || true)"
  if [ "$n" != "1" ]; then
    printf 'RECORD_UNPARSEABLE file=%s key=%s occurrences=%s\n' "$f" "$k" "$n" >&2
    return 3
  fi
  raw="$(grep -E "^${k}:[[:space:]]" "$f" | sed -E "s/^${k}:[[:space:]]+//")"
  raw="$(printf '%s' "$raw" | sed -E 's/[[:space:]]+#.*$//')"
  raw="$(printf '%s' "$raw" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')"
  raw="$(printf '%s' "$raw" | sed -E 's/^"(.*)"$/\1/; s/^'"'"'(.*)'"'"'$/\1/')"
  printf '%s' "$raw"
  return 0
}

# record_filename_ok <path>
# A record filename carrying whitespace is rejected rather than word-split.
record_filename_ok() {
  case "$1" in
    *[[:space:]]*) printf 'RECORD_FILENAME_INVALID file=%s\n' "$1" >&2; return 3 ;;
    *) return 0 ;;
  esac
}
