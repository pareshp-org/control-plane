#!/usr/bin/env bash
set -euo pipefail

echo "=== 1. Verifying pins ==="
bash .github/workflows/_pins/verify-pins.sh

echo "=== 2. Verifying L2-T171 (actor-gate.yml) ==="
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/actor-gate.yml'))"
test "$(grep -c '@@' .github/workflows/actor-gate.yml)" = "0"
test "$(grep -cE '^\s*(if:|paths:|paths-ignore:)' .github/workflows/actor-gate.yml)" = "0"
test "$(grep -cE 'gh api .*(-X |--method )(POST|PUT|PATCH|DELETE)' .github/workflows/actor-gate.yml)" = "0"
for t in ACTOR_GATE_INPUT_UNRESOLVED ACTOR_GATE_REGISTRY_UNREADABLE ACTOR_NOT_HUMAN ACTOR_NOT_ACTIVE ACTOR_CAPABILITY_MISSING ACTOR_GATE_PASS; do
  grep -q "$t" .github/workflows/actor-gate.yml || exit 1
done
echo "L2-T171 OK"

echo "=== 3. Verifying L2-T174 (workflow-identity-gate.yml) ==="
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/workflow-identity-gate.yml'))"
test "$(grep -c '@@' .github/workflows/workflow-identity-gate.yml)" = "0"
test "$(grep -c 'APPROVER_EQUALS_DEPLOYER' .github/workflows/workflow-identity-gate.yml)" = "1"
test "$(grep -cE '^\s*(if:|paths:|paths-ignore:|continue-on-error:)' .github/workflows/workflow-identity-gate.yml)" = "0"
test "$(grep -ciE 'required.reviewer|environment protection rule' .github/workflows/workflow-identity-gate.yml)" = "0"
test "$(python3 -c "import yaml;d=yaml.safe_load(open('.github/workflows/workflow-identity-gate.yml'));print(d['jobs']['workflow-identity-gate']['steps'][-1]['name'])")" \
     = "Refuse while an open verification block exists"
for t in IDENTITY_GATE_INPUT_UNRESOLVED IDENTITY_GATE_REGISTRY_UNREADABLE \
         IDENTITY_GATE_RECORDS_UNREADABLE DEPLOYER_UNRESOLVED APPROVER_UNRESOLVED \
         NO_APPROVAL_RECORD APPROVAL_DIGEST_MISMATCH APPROVER_NOT_CAPABLE \
         VERIFICATION_BLOCK_STORE_UNRESOLVED VERIFICATION_BLOCK_OPEN IDENTITY_GATE_PASS; do
  grep -q "$t" .github/workflows/workflow-identity-gate.yml || exit 1
done
echo "L2-T174 OK"

echo "=== 4. Verifying L2-T175 (production-gate-chain.yml) ==="
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/production-gate-chain.yml'))"
test "$(grep -c '@@' .github/workflows/production-gate-chain.yml)" = "0"
test "$(grep -cE '^\s*(if:|paths:|paths-ignore:)' .github/workflows/production-gate-chain.yml)" = "0"
python3 -c "
import yaml
d = yaml.safe_load(open('.github/workflows/production-gate-chain.yml'))
jobs = list(d['jobs'].keys())
assert jobs == ['actor-gate', 'runner-tier-assert', 'env-policy-assert', 'workflow-identity-gate']
assert d['jobs']['runner-tier-assert']['needs'] == 'actor-gate'
assert d['jobs']['env-policy-assert']['needs'] == 'runner-tier-assert'
assert d['jobs']['workflow-identity-gate']['needs'] == 'env-policy-assert'
"
echo "L2-T175 OK"

echo "=== 5. Verifying L2-T176 (rollback.yml) ==="
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/rollback.yml'))"
test "$(grep -c '@@' .github/workflows/rollback.yml)" = "0"
test "$(grep -c 'workflow-identity-gate' .github/workflows/rollback.yml)" = "0"
test "$(grep -cE '^\s*(if:|paths:|paths-ignore:)' .github/workflows/rollback.yml)" = "0"
test "$(python3 -c "import yaml;print(list(yaml.safe_load(open('.github/workflows/rollback.yml'))['jobs'])[0])")" = "actor-gate"
test "$(grep -c 'required_capabilities: incident-response,production-approval' .github/workflows/rollback.yml)" = "1"
test "$(grep -c 'machine_dispatch_class: none' .github/workflows/rollback.yml)" = "1"
test "$(grep -cE 'runner-tier-assert\.yml|env-policy-assert\.yml' .github/workflows/rollback.yml)" = "2"
for t in ROLLBACK_INPUT_UNRESOLVED ROLLBACK_RECORDS_UNREADABLE ROLLBACK_DIGEST_NEVER_APPROVED \
         ROLLBACK_DIGEST_NEVER_DEPLOYED ROLLBACK_TARGET_UNRESOLVED MIGRATION_BOUNDARY_UNRESOLVED \
         ROLLBACK_CONFIRMATION_MISMATCH EXCEPTIONAL_AUTH_STORE_UNRESOLVED ROLLBACK_EVENT_TYPE_UNRESOLVED; do
  grep -q "$t" .github/workflows/rollback.yml || exit 1
done
echo "L2-T176 OK"

echo "=== 6. Verifying L2-P1-T04 (gate-freeze.yml) ==="
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/gate-freeze.yml'))"
test "$(grep -c '@@' .github/workflows/gate-freeze.yml)" = "0"
test "$(grep -cE '^\s*(if:|paths:|paths-ignore:)' .github/workflows/gate-freeze.yml)" = "0"
test "$(grep -c 'Condition [AB],' .github/workflows/gate-freeze.yml)" = "2"
test "$(grep -c '^          # Exception ' .github/workflows/gate-freeze.yml)" = "2"
test "$(grep -c 'DECISION REQUIRED L2/P1/DEC-C unanswered' .github/workflows/gate-freeze.yml)" = "1"
echo "L2-P1-T04 OK"

echo "=== 7. Privileged posture checker ==="
python3 tools/evidence/assert-privileged-workflows.py

echo "=== ALL PRODUCTION GATE WORKFLOWS VERIFIED ==="
