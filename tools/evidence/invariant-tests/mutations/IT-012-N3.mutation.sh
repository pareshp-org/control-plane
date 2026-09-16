#!/usr/bin/env bash
# Mutation: remove the gate-2-vs-production-approval separation check from the
# fixture workflow deploy-production.yml so a Gate-2-only approval record passes
# the production-approval gate.
# Expected result: IT-012-N3 flips from PASS to FAIL.
# Spec: protocol/03-invariant-tests.md section 4.4 (MUTATION-NEEDED IT-012-N3),
# section 4.2's IT-012-N3 case ("A PR approved at Gate 2, with NO production-
# approval record, must not deploy").
set -euo pipefail
WORKFLOW="${FIXTURE_REPO_ROOT:?FIXTURE_REPO_ROOT must be exported by the mutation harness}/.github/workflows/deploy-production.yml"
[ -f "$WORKFLOW" ] || { echo "IT-012-N3 mutation FAILED: $WORKFLOW does not exist" >&2; exit 1; }

cp "$WORKFLOW" "$WORKFLOW.pre-mutation"

# Remove the line(s) that distinguish a Gate-2 record from a production-
# approval record: any line naming the record/approval type AND naming either
# "production" or "gate-2"/"gate_2"/"gate2", plus any line naming the literal
# DIGEST_GATE2_ONLY token this test dispatches with. Matched independently of
# comparison operator (==, !=, case, grep) since the real fixture's exact
# phrasing is not frozen by any merged task yet.
python3 - "$WORKFLOW" <<'PYEOF'
import re, sys
path = sys.argv[1]
# newline='' on both read and write: preserve the file's own line endings
# byte-for-byte so a no-op run is provably a no-op, not a false CRLF<->LF diff.
lines = open(path, encoding="utf-8", newline='').read().splitlines(keepends=True)
type_kw = re.compile(r'record[._-]?type|approval[._-]?type', re.I)
gate2_kw = re.compile(r'gate[._-]?2|gate2', re.I)
prod_kw = re.compile(r'production', re.I)
literal_kw = re.compile(r'GATE2_ONLY|GATE_2_ONLY', re.I)
kept = []
for line in lines:
    is_separation_check = (type_kw.search(line) and (gate2_kw.search(line) or prod_kw.search(line))) \
        or literal_kw.search(line)
    if is_separation_check:
        continue
    kept.append(line)
open(path, "w", encoding="utf-8", newline='').write("".join(kept))
PYEOF

if cmp -s "$WORKFLOW" "$WORKFLOW.pre-mutation"; then
  echo "IT-012-N3 mutation FAILED: no matching separation-check line found in $WORKFLOW" >&2
  mv "$WORKFLOW.pre-mutation" "$WORKFLOW"
  exit 1
fi

rm -f "$WORKFLOW.pre-mutation"
echo "IT-012-N3 mutation applied: gate-2-vs-production-approval separation check removed from $WORKFLOW"
