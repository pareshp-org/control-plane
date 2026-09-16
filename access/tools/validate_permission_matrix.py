#!/usr/bin/env python3
"""Validate access/model/permission-matrix.yaml against Section 90.2.

Section 90.2 (spec lines 7951-7984) prints a 4-column table of 26
data-category rows, plus a machine-identities row held separately because it
is absolute rather than four-valued. This checker fails closed: a missing
file, an unparsable document, a wrong row count or a non-absolute
machine-identity row is a hard failure, never a silent pass.

Usage:  validate_permission_matrix.py [--selftest]
Exit 0 PASS, 1 FAIL, 2 fail-closed (input missing/unreadable).
"""
import copy
import sys

import yaml

MATRIX_PATH = "access/model/permission-matrix.yaml"
EXPECTED_ROW_COUNT = 26
EXPECTED_COLUMNS = ["founder", "team_lead", "employee", "peer"]
EXPECTED_MACHINE_IDENTITIES = [
    "reconciler",
    "provisioning-cli",
    "ops-console",
    "background-agents",
    "background-machine-layer",
]


def load(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except (OSError, yaml.YAMLError):
        return None


def check(doc):
    """Return (findings, is_fail_closed). findings=[] means PASS."""
    findings = []
    if not isinstance(doc, dict):
        return (["document is not a mapping"], True)

    if doc.get("document") != "permission-matrix":
        findings.append("document key is not 'permission-matrix'")

    if doc.get("columns") != EXPECTED_COLUMNS:
        findings.append(
            "columns is %r, expected %r" % (doc.get("columns"), EXPECTED_COLUMNS))

    rows = doc.get("rows")
    if not isinstance(rows, list):
        return (findings + ["rows is missing or not a list"], True)

    if len(rows) != EXPECTED_ROW_COUNT:
        findings.append(
            "rows has %d entries, spec 90.2 transcribes exactly %d "
            "data-category rows (the machine-identities row is separate)"
            % (len(rows), EXPECTED_ROW_COUNT))

    seen = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            findings.append("rows[%d] is not a mapping" % i)
            continue
        cat = row.get("data_category")
        if not cat:
            findings.append("rows[%d] has no data_category" % i)
        elif cat in seen:
            findings.append("rows[%d] duplicates data_category %r" % (i, cat))
        else:
            seen.add(cat)
        for col in EXPECTED_COLUMNS:
            if col not in row or not row[col]:
                findings.append("rows[%d] (%s) missing column %s" % (i, cat, col))

    mi = doc.get("machine_identity_row")
    if not isinstance(mi, dict):
        return (findings + ["machine_identity_row is missing or not a mapping"], True)

    # Section 90.2: the machine-identities row is absolute.
    if mi.get("absolute") is not True:
        findings.append(
            "machine_identity_row.absolute is %r; spec 90.2 makes it absolute"
            % mi.get("absolute"))
    for col in EXPECTED_COLUMNS:
        if str(mi.get(col, "")).strip().lower() != "no":
            findings.append(
                "machine_identity_row.%s is %r; spec 90.2 requires 'No' in "
                "every column, unconditionally" % (col, mi.get(col)))

    declared_identities = mi.get("machine_identities")
    if declared_identities != EXPECTED_MACHINE_IDENTITIES:
        findings.append(
            "machine_identity_row.machine_identities is %r, expected the "
            "five identities %r (spec 90.2's four named identities plus the "
            "background-machine-layer person class, per spec 90.1)"
            % (declared_identities, EXPECTED_MACHINE_IDENTITIES))

    return (findings, False)


def selftest():
    """Exercise the checker against a mutated (invalid) copy of the real
    document, proving a real defect is actually caught -- not just that the
    committed file happens to validate."""
    doc = load(MATRIX_PATH)
    if doc is None:
        print("SELFTEST FAIL: %s unreadable" % MATRIX_PATH)
        return 2

    findings, fail_closed = check(doc)
    if findings or fail_closed:
        print("SELFTEST FAIL: the committed document itself does not pass:")
        for f in findings:
            print("  - %s" % f)
        return 1

    # Negative case 1: flip the absolute machine-identity row.
    mutated = copy.deepcopy(doc)
    mutated["machine_identity_row"]["absolute"] = False
    findings, _ = check(mutated)
    if not any("absolute" in f for f in findings):
        print("SELFTEST FAIL: flipping machine_identity_row.absolute was not caught")
        return 1

    # Negative case 2: grant a machine identity a "Yes".
    mutated = copy.deepcopy(doc)
    mutated["machine_identity_row"]["founder"] = "Yes"
    findings, _ = check(mutated)
    if not any("founder" in f for f in findings):
        print("SELFTEST FAIL: granting the machine-identity row 'Yes' was not caught")
        return 1

    # Negative case 3: drop a row.
    mutated = copy.deepcopy(doc)
    mutated["rows"].pop()
    findings, _ = check(mutated)
    if not any("rows has" in f for f in findings):
        print("SELFTEST FAIL: a dropped row was not caught")
        return 1

    print("L5-T09 SELF-VERIFY PASS")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()

    doc = load(MATRIX_PATH)
    if doc is None:
        print("RESULT FAIL matrix-unreadable %s" % MATRIX_PATH)
        return 2
    findings, fail_closed = check(doc)
    for f in findings:
        print("FINDING %s" % f)
    if findings:
        print("RESULT FAIL")
        return 2 if fail_closed else 1
    print("RESULT PASS (%d data-category rows + machine-identity row)"
          % EXPECTED_ROW_COUNT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
