#!/usr/bin/env bash
# Mutation: suppress the freeze signal in the repair class so that when a
# repair class writes incorrect state it continues running instead of halting
# and raising a Level 5 escalation.
# Expected result: IT-537-N1 flips from PASS to FAIL.
# Spec: protocol/03-invariant-tests.md §8.5 (MUTATION-NEEDED IT-537-N1).
set -euo pipefail
REPAIR_CLASS="${FIXTURE_REPO_ROOT:?}/reconciler/repair/repair-class.sh"
# No-op the freeze signal emission so the class does not halt on bad state.
sed -i 's/\(emit_freeze_signal\|raise_level_5\|freeze_class\)/: # MUTATED-SUPPRESSED/g' \
  "$REPAIR_CLASS"
echo "IT-537-N1 mutation applied: freeze signal suppressed in repair class at $REPAIR_CLASS"
