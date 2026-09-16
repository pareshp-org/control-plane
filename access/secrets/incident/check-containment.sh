#!/usr/bin/env bash
# access/secrets/incident/check-containment.sh
# Section 43.4: the containment hook must name every fifth-tier credential.
#   exit 0  the enumeration is complete and correctly ordered
#   exit 1  an assertion fails
#   exit 2  input fault - FAIL CLOSED
set -eu
python access/secrets/incident/check_containment.py "$@"
