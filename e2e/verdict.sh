#!/usr/bin/env bash
# e2e/verdict.sh — emit PASS/FAIL verdict for the most recent e2e run.
# Full body authored per L0-01-phase-0-contracts.md §L0-P0-026.
set -euo pipefail
: "${E2E_RUN_ID:?Set E2E_RUN_ID before running}"
python3 contracts/ci/verify_contracts.py | tail -1
