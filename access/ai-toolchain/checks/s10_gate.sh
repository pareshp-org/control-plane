#!/usr/bin/env bash
# Section 96.6 S10 / Section 36.6: no AI-assisted session opens a repository
# until that repository's committed-secrets check has passed. Fails closed.
# Usage: s10_gate.sh <repo-id> <s10-record-path>
set -u
if [ "$#" -ne 2 ]; then
  echo "USAGE: s10_gate.sh <repo-id> <s10-record-path>"
  exit 2
fi
REPO="$1"; RECORD="$2"
if [ ! -f "$RECORD" ]; then
  echo "S10-GATE: BLOCKED (no recorded S10 pass for $REPO)"
  exit 3
fi
if ! grep -q '^s10_result: pass$' "$RECORD"; then
  echo "S10-GATE: BLOCKED (S10 has not passed for $REPO)"
  exit 3
fi
echo "S10-GATE: PASS ($REPO)"
exit 0
