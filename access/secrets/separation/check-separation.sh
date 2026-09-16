#!/usr/bin/env bash
# access/secrets/separation/check-separation.sh
# Boundary 2, enforcement E3 (Section 40.3 line 3703).
#   exit 0  separated, or a complete accepted-risk record exists
#   exit 1  UNRESOLVED - an unstated default, which Section 40.3 forbids
#   exit 2  input fault - FAIL CLOSED
set -eu
python access/secrets/separation/check_separation.py "$@"
