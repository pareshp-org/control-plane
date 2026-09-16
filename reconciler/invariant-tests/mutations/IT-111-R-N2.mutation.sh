#!/usr/bin/env bash
# Mutation: allow a free-text 'reproduction_notes' field in the fixture records
# schema so an incident record with a non-synthetic reproduction fixture passes
# schema validation (violating §38.3).
# Expected result: IT-111-R-N2 flips from PASS to FAIL.
# Spec: protocol/03-invariant-tests.md §9.3 (MUTATION-NEEDED IT-111-R-N2).
set -euo pipefail
SCHEMA="${FIXTURE_REPO_ROOT:?}/tools/records/schema/incident-record.yaml"
python3 - "$SCHEMA" << 'PY'
import sys, yaml
schema = yaml.safe_load(open(sys.argv[1]))
# Allow the prohibited free-text field by adding it to the schema properties
# and removing the additionalProperties: false guard that would block it.
schema.setdefault('properties', {})['reproduction_notes'] = {'type': 'string'}
schema.pop('additionalProperties', None)
yaml.dump(schema, open(sys.argv[1], 'w'), allow_unicode=True)
print('reproduction_notes added to schema')
PY
echo "IT-111-R-N2 mutation applied: free-text reproduction_notes field allowed in incident record schema at $SCHEMA"
