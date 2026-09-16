#!/usr/bin/env bash
# break-glass.sh — L0 emergency access procedure (AT-022, PFD-006 — deferred, no FD issued)
# Usage: bash scripts/break-glass.sh --reason "description" --duration 4h
# REQUIRES: bendrohit-eng GitHub login (or break-glass second owner once PFD-006 resolved)
set -euo pipefail

ALLOWED_ACTORS=("bendrohit-eng")
REASON=""
DURATION="4h"
ACTOR="${GITHUB_ACTOR:-$(git config user.name 2>/dev/null || echo unknown)}"

while [[ $# -gt 0 ]]; do
  case $1 in
    --reason) REASON="$2"; shift 2;;
    --duration) DURATION="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 2;;
  esac
done

if [[ -z "$REASON" ]]; then
  echo "ERROR: --reason is required for break-glass"
  exit 2
fi

# Reject characters that could corrupt or inject extra fields into the YAML record.
if [[ "$REASON" == *$'\n'* || "$REASON" == *'"'* || "$DURATION" == *$'\n'* || "$DURATION" == *'"'* ]]; then
  echo "ERROR: --reason/--duration must not contain quote or newline characters"
  exit 2
fi

is_allowed_actor() {
  local candidate="${1,,}" allowed
  for allowed in "${ALLOWED_ACTORS[@]}"; do
    [[ "$candidate" == "${allowed,,}" ]] && return 0
  done
  return 1
}

if ! is_allowed_actor "$ACTOR"; then
  echo "BREAK-GLASS DENIED: actor '$ACTOR' is not authorized (allowed: ${ALLOWED_ACTORS[*]})"
  echo "Only the L0 owner may invoke break-glass (see PFD-006 for second-owner status)."
  exit 1
fi

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
RECORD_FILE="records/exceptions/break-glass-${TIMESTAMP//[:T]/-}.yaml"

mkdir -p records/exceptions
cat > "$RECORD_FILE" <<EOF
# Break-glass record — AT-022 (PFD-006 — deferred, no FD issued)
id: "BG-${TIMESTAMP//[:T-]/}"
reason: "$REASON"
actor: "$ACTOR"
duration: "$DURATION"
granted_by: "$ACTOR"
timestamp: "$TIMESTAMP"
expires: "$(date -u -d "+${DURATION}" +%Y-%m-%d 2>/dev/null || date -u +%Y-%m-%d)"
status: "ACTIVE"
EOF

echo "BREAK-GLASS ACTIVATED"
echo "Record: $RECORD_FILE"
echo "Actor: $ACTOR"
echo "Reason: $REASON"
echo "Duration: $DURATION"
echo ""
echo "IMPORTANT: Notify L5 owner (bendrohit-eng) immediately."
echo "Record must be reviewed within 24h per AT-022."
