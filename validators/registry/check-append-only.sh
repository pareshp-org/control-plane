#!/usr/bin/env bash
# check-append-only.sh — day-one append-only guard for registries/**.
#
# Enforces rules A1-A4 of schemas/registry/CONVENTIONS.md, which transcribe
# spec Section 63.1 ("state transitions with start_date and end_date -
# effective-dating, never in-place mutation"), Section 7.1 ("Departure is a
# state, not a deletion... Their identifier is never reused") and invariant
# 101.7 #47 ("History is append-only... state changes are recorded, not
# overwritten").
#
# Scope, deliberately narrow: this guard proves that history was not destroyed.
# It does NOT validate schemas, referential integrity or date rules - that is
# phase L1-02 (subsystem B, Section 99.2).
#
# Usage:  validators/registry/check-append-only.sh [BASE_REF]
# BASE_REF defaults to origin/integration.
# Exit 0 = APPEND_ONLY_OK. Exit 1 = APPEND_ONLY_VIOLATION. Exit 2 = usage error.

set -euo pipefail

BASE_REF="${1:-origin/integration}"

if ! git rev-parse --verify --quiet "$BASE_REF" >/dev/null; then
  echo "APPEND_ONLY_ERROR: base ref not found: $BASE_REF" >&2
  exit 2
fi

BASE="$(git merge-base "$BASE_REF" HEAD)"
VIOLATIONS=0

# --- A3/A5: a registry file is never deleted or renamed away. ---
DELETED="$(git diff --diff-filter=DR --name-only "$BASE" HEAD -- registries/ || true)"
if [ -n "$DELETED" ]; then
  echo "APPEND_ONLY_VIOLATION: registry file deleted or renamed:"
  echo "$DELETED" | sed 's/^/  /'
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# --- A1: an id line is never removed or changed. ---
REMOVED_IDS="$(git diff --unified=0 "$BASE" HEAD -- registries/ \
  | grep -E '^-[^-]' \
  | grep -E '^-[[:space:]]*(-[[:space:]]+)?id:' || true)"
if [ -n "$REMOVED_IDS" ]; then
  echo "APPEND_ONLY_VIOLATION: id removed or rewritten (rule A1, ids are never reused):"
  echo "$REMOVED_IDS" | sed 's/^/  /'
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# --- A2: a start_date is never removed or rewritten; intervals close, never move. ---
REMOVED_STARTS="$(git diff --unified=0 "$BASE" HEAD -- registries/ \
  | grep -E '^-[^-]' \
  | grep -E '^-[[:space:]]*start_date:' || true)"
if [ -n "$REMOVED_STARTS" ]; then
  echo "APPEND_ONLY_VIOLATION: start_date removed or rewritten (rule A2):"
  echo "$REMOVED_STARTS" | sed 's/^/  /'
  VIOLATIONS=$((VIOLATIONS + 1))
fi

if [ "$VIOLATIONS" -gt 0 ]; then
  echo ""
  echo "Corrections are follow-up entries, never in-place rewrites (rule A4,"
  echo "spec Section 97.2). Close the old interval with end_date and add a new entry."
  exit 1
fi

echo "APPEND_ONLY_OK"
exit 0
