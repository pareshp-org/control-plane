#!/usr/bin/env bash
# access/secrets/envelope/check-envelope.sh
# The stable exit contract Lane 3 reconciles against and Lane 2 wires (HO-02).
#
#   exit 0  every run is inside its envelope
#   exit 1  one or more runs are outside - Blocking drift (Section 53.4)
#   exit 2  input fault - FAIL CLOSED (invariant 80)
#
# Usage: check-envelope.sh <runs-dir> <triggers-dir>
# Envelopes always come from access/secrets/envelope.
set -eu
if [ "$#" -ne 2 ]; then
  echo "usage: check-envelope.sh <runs-dir> <triggers-dir>" >&2
  exit 2
fi
python access/secrets/envelope/evaluate_envelope.py access/secrets/envelope "$1" "$2"
