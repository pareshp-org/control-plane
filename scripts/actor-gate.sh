#!/usr/bin/env bash
# actor-gate.sh — FD-086 (PFD-012), actor-gate canonical form
# Fails if PR actor is not in the allowed list.
set -euo pipefail
ALLOWED_ACTORS=("bendrohit-eng")
ACTOR="${PR_ACTOR:-${GITHUB_ACTOR:-unknown}}"

is_allowed_actor() {
  local candidate="${1,,}" allowed
  for allowed in "${ALLOWED_ACTORS[@]}"; do
    [[ "$candidate" == "${allowed,,}" ]] && return 0
  done
  return 1
}

if is_allowed_actor "$ACTOR"; then
  echo "ACTOR-GATE PASS: $ACTOR is authorized"
  exit 0
else
  echo "ACTOR-GATE FAIL: $ACTOR is not in the authorized list: ${ALLOWED_ACTORS[*]}"
  exit 1
fi
