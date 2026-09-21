#!/usr/bin/env bash
# audit-log.sh — L5 audit trail writer (FD-083)
# Usage: bash scripts/audit-log.sh --event <type> --actor <login> --detail "..."
set -euo pipefail

EVENT=""
ACTOR="${GITHUB_ACTOR:-bendrohit-eng}"
DETAIL=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --event) EVENT="$2"; shift 2;;
    --actor) ACTOR="$2"; shift 2;;
    --detail) DETAIL="$2"; shift 2;;
    *) shift;;
  esac
done

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
LOG_DIR="records/audit"
mkdir -p "$LOG_DIR"

echo "${TIMESTAMP} | ${ACTOR} | ${EVENT} | ${DETAIL}" >> "$LOG_DIR/audit.log"
echo "AUDIT: ${TIMESTAMP} ${ACTOR} ${EVENT}"
