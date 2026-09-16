#!/usr/bin/env bash
# access/secrets/checks/rotation-complete.sh
# STEP-10 of the rotation runbook. The only thing that may set a rotation
# record to `done`.
#   exit 0  ROTATION-DONE-PERMITTED
#   exit 1  ROTATION-NOT-DONE
#   exit 2  input fault - FAIL CLOSED
set -eu
python access/secrets/checks/rotation_complete.py "$@"
