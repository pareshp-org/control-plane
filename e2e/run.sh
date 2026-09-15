#!/usr/bin/env bash
# e2e/run.sh — end-to-end test runner for Phase 0 contracts.
# Full body authored per L0-01-phase-0-contracts.md §L0-P0-026.
set -euo pipefail
: "${E2E_RUN_ID:?Set E2E_RUN_ID before running}"
echo "E2E_RUN_ID=$E2E_RUN_ID"
echo "Running contract harness..."
bash contracts/harness/run-contract-tests.sh
