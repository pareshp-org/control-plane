#!/usr/bin/env bash
# Mutation: make the fixture provenance checker skip files that carry no
# 'provenance:' key, treating absence as implicitly declared. A fixture tree
# with no provenance declaration (fixtures/tree-fixture-undeclared) must then
# pass CI instead of failing IT-111-N1.
# Expected result: IT-111-N1 flips from PASS to FAIL.
# Spec: protocol/03-invariant-tests.md section 9.3 (MUTATION-NEEDED IT-111-N1),
# section 9.2's IT-111-N1 case, invoked as
# `validators/registry/fixture-provenance.sh --tree fixtures/tree-fixture-undeclared`.
set -euo pipefail
CHECKER="${FIXTURE_REPO_ROOT:?FIXTURE_REPO_ROOT must be exported by the mutation harness}/validators/registry/fixture-provenance.sh"
[ -f "$CHECKER" ] || { echo "IT-111-N1 mutation FAILED: $CHECKER does not exist" >&2; exit 1; }

cp "$CHECKER" "$CHECKER.pre-mutation"

# Insert a guard immediately before the per-file provenance check call: if the
# file carries no 'provenance:' key at all, skip it without flagging it as
# undeclared. This is the exact loophole section 9.3 / section 38.3 describe --
# absence is treated as implicit declaration instead of a rejection.
# The call site's exact shape is not frozen by any merged task yet, so this
# mutation matches the two shapes the checker is documented to take:
#   1. a shell function call:   check_provenance_for_file "$f"   (or similar)
#   2. a per-file loop body that calls the checker recursively on each file
# and inserts the same short-circuit guard immediately before it.
PATCHED=0
if grep -qE '^\s*check_provenance_for_file\b' "$CHECKER"; then
  sed -i -E 's/^(\s*)(check_provenance_for_file\s+"?\$[A-Za-z_]+"?.*)$/\1grep -q "provenance:" "$f" \&\& \2/' "$CHECKER"
  PATCHED=1
elif grep -qE '^\s*(check_provenance|provenance_check|validate_provenance)\b' "$CHECKER"; then
  sed -i -E 's/^(\s*)((check_provenance|provenance_check|validate_provenance)\s+.*)$/\1grep -q "provenance:" "$f" \&\& \2/' "$CHECKER"
  PATCHED=1
fi

if [ "$PATCHED" -eq 0 ] || cmp -s "$CHECKER" "$CHECKER.pre-mutation"; then
  echo "IT-111-N1 mutation FAILED: no per-file provenance check call site found in $CHECKER" >&2
  mv "$CHECKER.pre-mutation" "$CHECKER"
  exit 1
fi

rm -f "$CHECKER.pre-mutation"
echo "IT-111-N1 mutation applied: provenance checker now skips files with no provenance key in $CHECKER"
