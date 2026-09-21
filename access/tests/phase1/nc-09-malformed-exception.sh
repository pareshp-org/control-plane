#!/usr/bin/env bash
# access/tests/phase1/nc-09-malformed-exception.sh
# NC-09 - spec 98.2 Phase 1: the minimal exceptions.yaml schema validator
# (expiry, owner, deactivation trigger present) is active in control-plane CI
# and rejects a deliberately malformed exception. Invariant 77.
# The validator is L1-owned (EXT-1). This test invokes it and never edits it.
set -uo pipefail
. access/tests/lib/assert.sh
VAL="validators/registry/validate-exceptions.sh"
if [ ! -x "$VAL" ]; then
  l5_indeterminate "NC-09" "L1 validator $VAL absent or not executable"
  l5_exit
fi
l5_refuses "NC-09/negative" "malformed exception with no expiry, owner or trigger" "$VAL" access/tests/fixtures/exception-malformed.yaml
l5_permits "NC-09/positive" "well-formed exception" "$VAL" access/tests/fixtures/exception-wellformed.yaml
l5_exit
