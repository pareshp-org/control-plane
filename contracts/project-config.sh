#!/usr/bin/env bash
# Project configuration — single source of truth for all plan scripts.
# FD-068 (2026-09-08): edit ONLY this file to propagate org/login changes.
# Run `source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"` at top of every script.

# ── Org ──────────────────────────────────────────────────────────────────────
export ORG="pareshp-org"                  # GitHub org login (FD-069, 2026-09-08); https://github.com/pareshp-org — upgrade to Team ($4/mo) to enable Phase 0
export CP="control-plane"                 # Primary repo name
export CPR="control-plane-records"        # Records repo name

# ── People ───────────────────────────────────────────────────────────────────
export L0_LOGIN="bendrohit-eng"           # Founder / L0 Integrator GitHub login (FD-067)

# ── Schema ───────────────────────────────────────────────────────────────────
export SCHEMA_URN="urn:multiproduct:schemas"   # Schema $id prefix (FD-050)

# ── Guard ────────────────────────────────────────────────────────────────────
# Fail loudly if ORG is called without being set.
check_org() { : "${ORG:?ERROR: set ORG in contracts/project-config.sh before running Phase 0}"; }
