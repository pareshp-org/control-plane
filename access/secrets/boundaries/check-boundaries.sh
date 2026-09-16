#!/usr/bin/env bash
# access/secrets/boundaries/check-boundaries.sh
# The repository-side half of the two Section 40.3 trust boundaries.
# The host-side halves are access/secrets/host/check-credential-store.sh and
# infra/network/check-shell-gate.sh (L5-02-10).
#   exit 0  every assertion holds
#   exit 1  an assertion fails
#   exit 2  a boundary declaration is missing - FAIL CLOSED
set -eu
python access/secrets/boundaries/check_boundaries.py "$@"
