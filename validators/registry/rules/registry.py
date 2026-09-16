"""Rule registry — loads and runs rules R01-R18 (FD-094, Option B)"""
import importlib
from pathlib import Path

RULES = [
    "r01_people_id_uniqueness",
    "r02_role_reference_valid",
    "r03_lane_assignment_valid",
    "r04_capability_id_format",
    "r05_capability_owner_lane_valid",
    "r06_platform_type_valid",
    "r07_exception_expiry_future",
    "r08_people_required_fields",
    "r09_no_duplicate_capabilities",
    "r10_policy_enforced_by_valid",
    "r11_canary_intact",
    "r12_commitment_owner_exists",
    "r13_no_empty_registries",
    "r14_schema_version_match",
    "r15_role_id_uniqueness",
    "r16_fte_range_valid",
    "r17_platform_id_uniqueness",
    "r18_exception_granted_by_authorized",
]

def load_rule(rule_id):
    """Load a rule module by ID (e.g. 'R01' or 'r01_people_id_uniqueness')"""
    if rule_id.upper().startswith("R"):
        idx = int(rule_id[1:]) - 1
        if 0 <= idx < len(RULES):
            module_name = RULES[idx]
        else:
            raise ValueError(f"Unknown rule: {rule_id}")
    else:
        module_name = rule_id
    return importlib.import_module(f"validators.registry.rules.{module_name}")

def run_all(registry_root, as_of, records_root=None):
    """Run all rules. Returns list of (rule_name, passed, findings)."""
    results = []
    for module_name in RULES:
        mod = importlib.import_module(f"validators.registry.rules.{module_name}")
        passed, findings = mod.check(registry_root, as_of, records_root)
        results.append((module_name, passed, findings))
    return results
