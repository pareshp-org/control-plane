#!/usr/bin/env bash
# access/tests/at-049-eval-suite-required.sh
# AT-049 - spec 100.4 and 38.1: a product declaring ai_runtime_dependency
# without an evaluation suite under verification/ fails CI. The validator is
# L1-owned (EXT-1): this test invokes it and never edits validators/** or
# schemas/**.
#
# The real enforcement is a JSON-Schema requirement inside
# schemas/product/product.contract.v2.schema.json
# (ai_runtime_dependency.required: [providers, evaluation]) -- L1 exercises
# it through pytest (validators/registry/tests/test_product_platform_blocks.py),
# not a single-file CLI. access/tests/lib/validate_product_schema.py reads
# that same schema (never edits it) so this task can shell out to a real
# file path the way its own design assumes. The baseline is L1's own
# committed, schema-valid fixture
# (validators/registry/fixtures/product/platform/valid/service_full/product.yaml,
# read-only); this task's own ai_runtime_dependency and evaluation blocks are
# merged onto temporary copies of it -- never onto the committed file itself.
set -uo pipefail
. access/tests/lib/assert.sh
VALIDATE="access/tests/lib/validate_product_schema.py"
BASELINE="validators/registry/fixtures/product/platform/valid/service_full/product.yaml"
PY=""
command -v python3 >/dev/null 2>&1 && PY=python3
[ -z "$PY" ] && command -v python >/dev/null 2>&1 && PY=python
if [ -z "$PY" ]; then l5_indeterminate "AT-049" "no python interpreter on PATH"; l5_exit; fi
if [ ! -f "$BASELINE" ]; then l5_indeterminate "AT-049" "EXT-1 baseline fixture absent: $BASELINE"; l5_exit; fi

if "$PY" "$VALIDATE" "$BASELINE" >/dev/null 2>&1; then
  l5_pass "AT-049/baseline-control"
else
  l5_indeterminate "AT-049" "L1's baseline fixture is not clean; the negative below would be unreadable"
  l5_exit
fi

MERGE() {  # MERGE BASE BLOCK... OUT  -- merges each BLOCK yaml onto BASE, writes OUT
  local out="${!#}"
  "$PY" - "$out" "$@" <<'PYEOF'
import sys
import yaml
argv = sys.argv[1:]
out_path = argv[0]
base_path = argv[1]
block_paths = argv[2:-1]
with open(base_path, encoding="utf-8") as f:
    doc = yaml.safe_load(f)
for bp in block_paths:
    with open(bp, encoding="utf-8") as f:
        block = yaml.safe_load(f)
    doc.update(block)
with open(out_path, "w", encoding="utf-8") as f:
    yaml.safe_dump(doc, f)
PYEOF
}

TMP="$(mktemp -d)"
NEG="$TMP/negative.yaml"
POS="$TMP/positive.yaml"
MERGE "$BASELINE" access/tests/fixtures/at-049-ai-runtime-dependency.yaml "$NEG"
l5_refuses "AT-049/no-eval-suite" "a product declaring ai_runtime_dependency with no verification/ai-eval suite" \
  "$PY" "$VALIDATE" "$NEG"

"$PY" - "$POS" "$NEG" access/tests/fixtures/at-049-eval-scenario.yaml <<'PYEOF'
import sys
import yaml
out_path, neg_path, eval_path = sys.argv[1], sys.argv[2], sys.argv[3]
with open(neg_path, encoding="utf-8") as f:
    doc = yaml.safe_load(f)
with open(eval_path, encoding="utf-8") as f:
    block = yaml.safe_load(f)
doc["ai_runtime_dependency"].update(block)
with open(out_path, "w", encoding="utf-8") as f:
    yaml.safe_dump(doc, f)
PYEOF
l5_permits "AT-049/with-eval-suite" "the same product once the evaluation suite exists" \
  "$PY" "$VALIDATE" "$POS"
rm -rf "$TMP"
l5_exit
