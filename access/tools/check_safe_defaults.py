#!/usr/bin/env python3
"""Safe-defaults register checker (Section 64.1, invariant 79).

Invariant 79: "New people, products and tools default to minimum privilege
and draft state."

Checks:
  1. The register (access/model/safe-defaults.yaml) declares all six
     Section 64.1 categories, each with at least one default and the
     top-level "configuration error must never grant excess authority" rule.
  2. Two concrete cross-checks against already-committed Lane 5 declarations,
     so this is not just a data file nobody reads against reality:
       - machine_accounts: access/model/permission-matrix.yaml's
         machine_identity_row is still absolute (a machine account default
         of "no dangerous capabilities" is meaningless if the matrix grants
         one).
       - repositories: access/branch-protection/branch-protection.yaml
         actually declares an `unarmed` profile (branch protection "applied
         from template at creation", i.e. before any grant).

Usage:  check_safe_defaults.py [--selftest]
"""
import copy
import os
import sys

import yaml

REGISTER_PATH = os.path.join("access", "model", "safe-defaults.yaml")
MATRIX_PATH = os.path.join("access", "model", "permission-matrix.yaml")
BRANCH_PROTECTION_PATH = os.path.join("access", "branch-protection", "branch-protection.yaml")
EXPECTED_CATEGORY_IDS = [
    "people", "products", "repositories", "tools_and_integrations",
    "machine_accounts", "non_employees",
]


def load_yaml(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except (OSError, yaml.YAMLError):
        return None


def check_register_shape(doc):
    findings = []
    if not isinstance(doc, dict):
        return (["register is not a mapping"], True)
    categories = doc.get("categories")
    if not isinstance(categories, list):
        return (["register has no categories list"], True)
    ids = [c.get("id") for c in categories if isinstance(c, dict)]
    missing = [cid for cid in EXPECTED_CATEGORY_IDS if cid not in ids]
    if missing:
        findings.append("register is missing categories: %r" % missing)
    for c in categories:
        if not isinstance(c, dict):
            continue
        if not c.get("defaults"):
            findings.append("category %r has no defaults" % c.get("id"))
    if not doc.get("rule"):
        findings.append("register has no top-level 'configuration error must "
                         "never grant excess authority' rule")
    return (findings, False)


def check_machine_accounts_cross_ref():
    matrix = load_yaml(MATRIX_PATH)
    if matrix is None:
        return ["%s unreadable - cannot verify the machine_accounts default "
                "against a real declaration" % MATRIX_PATH]
    mi = (matrix or {}).get("machine_identity_row")
    if not isinstance(mi, dict) or mi.get("absolute") is not True:
        return ["permission-matrix.yaml's machine_identity_row is not "
                "absolute; the machine_accounts safe-default has nothing "
                "real backing it"]
    return []


def check_repositories_cross_ref():
    bp = load_yaml(BRANCH_PROTECTION_PATH)
    if bp is None:
        return ["%s unreadable - cannot verify the repositories default "
                "against a real declaration" % BRANCH_PROTECTION_PATH]
    profiles = (bp or {}).get("profiles") or {}
    if "unarmed" not in profiles:
        return ["branch-protection.yaml declares no 'unarmed' profile; the "
                "repositories safe-default ('branch protection applied from "
                "template at creation') has nothing real backing it"]
    return []


def selftest():
    register = load_yaml(REGISTER_PATH)
    if register is None:
        print("SELFTEST FAIL: %s unreadable" % REGISTER_PATH)
        return 2
    findings, fail_closed = check_register_shape(register)
    if findings or fail_closed:
        print("SELFTEST FAIL: the committed register itself does not pass:")
        for f in findings:
            print("  - %s" % f)
        return 1

    live_findings = check_machine_accounts_cross_ref() + check_repositories_cross_ref()
    if live_findings:
        print("SELFTEST FAIL: cross-reference checks fail against the committed tree:")
        for f in live_findings:
            print("  - %s" % f)
        return 1

    # Negative fixture 1: drop a category.
    mutated = copy.deepcopy(register)
    mutated["categories"] = [c for c in mutated["categories"] if c.get("id") != "people"]
    bad, _ = check_register_shape(mutated)
    if not bad:
        print("SELFTEST FAIL: a dropped category was not caught")
        return 1

    # Negative fixture 2: drop the top-level rule.
    mutated2 = copy.deepcopy(register)
    mutated2.pop("rule", None)
    bad2, _ = check_register_shape(mutated2)
    if not bad2:
        print("SELFTEST FAIL: a dropped top-level rule was not caught")
        return 1

    print("L5-T11 SELF-VERIFY PASS")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()

    register = load_yaml(REGISTER_PATH)
    if register is None:
        print("RESULT FAIL register-unreadable %s" % REGISTER_PATH)
        return 2

    findings, fail_closed = check_register_shape(register)
    findings += check_machine_accounts_cross_ref()
    findings += check_repositories_cross_ref()

    for f in findings:
        print("FINDING %s" % f)
    if findings:
        print("RESULT FAIL")
        return 2 if fail_closed else 1
    print("RESULT PASS (6 safe-default categories, cross-checks consistent)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
