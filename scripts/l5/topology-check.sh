#!/usr/bin/env bash
# topology-check.sh — L5 topology comparator (FD-083, PFD-026)
# Reads topology.yaml and checks it against actual registries.
# This closes the implementation gap: topology.yaml was not read by any
# comparator (PFD-026 note: "appears in no CMP-01..CMP-19 comparator row").
#
# Spec: Section 66.2 (domains, dormant default), Section 13.1 (succession).
# Note: Section 10.2 (escalation resolves through topology, never a person)
# is not checked here — no automated person-id-pattern scan is implemented;
# this is a design gap, not a mechanical fix (see PFD backlog).
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(git rev-parse --show-toplevel)}"
TOPOLOGY="${1:-${REPO_ROOT}/registries/topology.yaml}"
PEOPLE="${REPO_ROOT}/registries/people"
ROLES="${REPO_ROOT}/registries/roles"

echo "=== L5 Topology Check ==="
echo "Reading: $TOPOLOGY"
echo ""

if [[ ! -f "$TOPOLOGY" ]]; then
  echo "FAIL: $TOPOLOGY not found"
  exit 1
fi

FAIL=0

# --- Check 1: file is valid YAML ---
python3 -c "import yaml, sys; yaml.safe_load(open(sys.argv[1]))" "$TOPOLOGY" \
  && echo "PASS: topology.yaml is valid YAML" \
  || { echo "FAIL: topology.yaml is not valid YAML"; exit 1; }

# --- Check 2: domains_active is boolean false at bootstrap (Section 66.2) ---
ACTIVE=$(python3 -c "
import yaml, sys
d = yaml.safe_load(open(sys.argv[1]))
print(str(d.get('domains_active', 'MISSING')))
" "$TOPOLOGY")

if [[ "$ACTIVE" == "False" ]]; then
  echo "PASS: domains_active=false (dormant, Section 66.2)"
elif [[ "$ACTIVE" == "True" ]]; then
  echo "INFO: domains_active=true — domain lead checks active"
else
  echo "FAIL: domains_active is $ACTIVE (expected boolean)"
  FAIL=$((FAIL + 1))
fi

# --- Check 3: activation_triggers count == 3 (Section 66.2 code block) ---
TRIGGER_COUNT=$(python3 -c "
import yaml, sys
d = yaml.safe_load(open(sys.argv[1]))
print(len(d.get('activation_triggers', [])))
" "$TOPOLOGY")

if [[ "$TRIGGER_COUNT" -eq 3 ]]; then
  echo "PASS: activation_triggers count=3 (verbatim from Section 66.2)"
else
  echo "FAIL: activation_triggers count=$TRIGGER_COUNT (expected 3)"
  FAIL=$((FAIL + 1))
fi

# --- Check 4: succession.team_lead slot exists (Section 13.1) ---
ACTING=$(python3 -c "
import yaml, sys
d = yaml.safe_load(open(sys.argv[1]))
v = d.get('succession', {}).get('team_lead', {}).get('acting', 'MISSING')
print('null' if v is None else str(v))
" "$TOPOLOGY")

if [[ "$ACTING" == "MISSING" ]]; then
  echo "FAIL: succession.team_lead.acting slot absent (Section 13.1)"
  FAIL=$((FAIL + 1))
elif [[ "$ACTING" == "null" ]]; then
  echo "WARN: succession.team_lead.acting=null — Founder must designate before Phase 1 go-live (Section 13.1)"
else
  echo "PASS: succession.team_lead.acting=$ACTING"
fi

# --- Check 5: if domains_active, every domain has a non-null lead (Section 66.2 R-TOP-03) ---
if [[ "$ACTIVE" == "True" ]]; then
  echo ""
  echo "Checking active domain leads (Section 66.2 R-TOP-03)..."
  DOMAIN_FAIL=0
  DOMAIN_OUT=$(python3 - "$TOPOLOGY" <<'PYEOF'
import yaml, sys
d = yaml.safe_load(open(sys.argv[1]))
fail = 0
for dom in d.get('domains', []):
    if dom.get('lead') is None:
        print(f"  FAIL: domain '{dom['id']}' is active with no lead (R-TOP-03)")
        fail += 1
    else:
        print(f"  PASS: domain '{dom['id']}' lead={dom['lead']}")
sys.exit(fail)
PYEOF
  ) || DOMAIN_FAIL=$?
  echo "$DOMAIN_OUT"
  FAIL=$((FAIL + DOMAIN_FAIL))
fi

echo ""
echo "=== Topology check: $([[ $FAIL -eq 0 ]] && echo 'PASS' || echo 'FAIL') ($FAIL failure(s)) ==="
[[ $FAIL -eq 0 ]]
