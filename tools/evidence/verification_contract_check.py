#!/usr/bin/env python3
"""
tools.evidence.verification_contract_check
L2-T546: Verification-contract check (§31, §31.3)

Exit codes per §0.4: 0=OK, 2=FAIL, 3=ERROR
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required", file=sys.stderr)
    print("ERROR verification_contract_check checked=0 failed=0")
    sys.exit(3)

TOOL_ID = "verification_contract_check"
CHECKED = 4

HIGH_CRITICALITY = {"high", "critical"}


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def check(contract_path: str, criticality: str) -> int:
    """
    Returns number of failed conditions (0-4).
    Raises SystemExit(3) on ERROR.
    """
    # Condition 1: verification contract file exists at path and is parseable
    if not os.path.exists(contract_path):
        print(f"ERROR: contract file not found: {contract_path}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    try:
        with open(contract_path, "r", encoding="utf-8") as fh:
            contract = yaml.safe_load(fh)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot parse contract: {exc}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    if not isinstance(contract, dict):
        print("ERROR: contract is not a YAML mapping", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    failed = 0

    # Condition 1 passed by reaching here.

    # Condition 2: coverage_map is declared
    if not contract.get("coverage_map"):
        print(
            "FAIL: no coverage_map declared in verification contract",
            file=sys.stderr,
        )
        failed += 1

    # Condition 3: seeded_defect_case / seeded_defect_cases is declared
    has_seeded = bool(contract.get("seeded_defect_cases") or contract.get("seeded_defect_case"))
    if not has_seeded:
        print(
            "FAIL: no seeded_defect_cases or seeded_defect_case declared in verification contract",
            file=sys.stderr,
        )
        failed += 1

    # Condition 4: performance_mechanism declared if criticality is 'high' or 'critical' (§31.3)
    if criticality.lower() in HIGH_CRITICALITY:
        if not contract.get("performance_mechanism"):
            print(
                f"FAIL: reliability_criticality is '{criticality}' but "
                "no performance_mechanism is declared (§31.3)",
                file=sys.stderr,
            )
            failed += 1
    # For low/medium/standard criticality: absence of performance_mechanism is optional and permitted

    return failed


def main() -> None:
    parser = argparse.ArgumentParser(description="Check verification contract against §31/§31.3 rules")
    parser.add_argument("--contract", required=True, help="Path to verification/contract.yaml")
    parser.add_argument("--criticality", required=True, help="Reliability criticality level (low, medium, standard, high, critical)")
    parser.add_argument("--summary", action="store_true", help="Print summary line per §0.4")
    args = parser.parse_args()

    failed = check(args.contract, args.criticality)

    if failed == 0:
        _summary("OK", CHECKED, 0)
        sys.exit(0)
    else:
        _summary("FAIL", CHECKED, failed)
        sys.exit(2)


if __name__ == "__main__":
    main()
