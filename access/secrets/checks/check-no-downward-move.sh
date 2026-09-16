#!/usr/bin/env bash
# access/secrets/checks/check-no-downward-move.sh
# Wrapper so Lane 2 has one stable command to wire into a workflow and Lane 3
# has one stable exit contract to reconcile against.
#
#   exit 0  no finding
#   exit 1  finding - SECURITY INCIDENT under Section 43, not a cleanup task
#   exit 2  input unreadable - FAIL CLOSED (invariant 80)
set -eu
python access/secrets/checks/check_no_downward_move.py "$@"
