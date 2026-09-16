#!/usr/bin/env python3
"""Fail-closed classification register checker (Section 64.2, invariant 80).

Invariant 80: "Every control is explicitly classified fail-closed or
fail-open. Unclassified controls fail CI."

Two checks, both fail-closed:

  1. The register itself (access/fail-closed/classification-register.yaml)
     carries all twelve Section 64.2 rows, each with a non-empty
     classification in {fail-closed, fail-open, mixed}.
  2. Every one-file-per-control declaration already committed under
     access/fail-closed/*.yaml (the PARTITION-rule-3 pattern this phase
     uses) resolves to a row the register names, and its own
     `classification:` field agrees with that row's classification --
     catching the case where a per-control file and the register disagree
     about the same control.

Usage:  check_fail_closed_register.py [--selftest]
"""
import glob
import os
import sys

import yaml

REGISTER_PATH = os.path.join("access", "fail-closed", "classification-register.yaml")
FAIL_CLOSED_DIR = os.path.join("access", "fail-closed")
EXPECTED_ROW_COUNT = 12
VALID_CLASSIFICATIONS = {"fail-closed", "fail-open", "mixed"}


def load_yaml(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except (OSError, yaml.YAMLError):
        return None


def check_register(doc):
    findings = []
    if not isinstance(doc, dict):
        return (["register is not a mapping"], True)
    rows = doc.get("rows")
    if not isinstance(rows, list):
        return (["register has no rows list"], True)
    if len(rows) != EXPECTED_ROW_COUNT:
        findings.append(
            "register has %d rows, spec 64.2 declares exactly %d controls"
            % (len(rows), EXPECTED_ROW_COUNT))
    seen = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            findings.append("rows[%d] is not a mapping" % i)
            continue
        name = row.get("control")
        if not name:
            findings.append("rows[%d] has no control name" % i)
            continue
        if name in seen:
            findings.append("rows[%d] duplicates control %r" % (i, name))
        seen.add(name)
        cls = row.get("classification")
        if cls not in VALID_CLASSIFICATIONS:
            findings.append(
                "control %r has classification %r, not one of %s "
                "(invariant 80: unclassified controls fail CI)"
                % (name, cls, sorted(VALID_CLASSIFICATIONS)))
    return (findings, False)


def check_per_control_files(register):
    """Every access/fail-closed/*.yaml other than the register itself must
    resolve to a row and agree with it."""
    findings = []
    rows_by_name = {r.get("control"): r for r in (register.get("rows") or [])
                     if isinstance(r, dict)}
    cross_ref = {
        entry.get("file"): entry.get("row")
        for entry in (register.get("per_control_files_already_classified") or [])
        if isinstance(entry, dict)
    }
    for path in sorted(glob.glob(os.path.join(FAIL_CLOSED_DIR, "*.yaml"))):
        base = os.path.basename(path)
        if os.path.abspath(path) == os.path.abspath(REGISTER_PATH):
            continue
        doc = load_yaml(path)
        if not isinstance(doc, dict):
            findings.append("%s is unreadable or not a mapping" % path)
            continue
        control_cls = doc.get("classification")
        if control_cls not in VALID_CLASSIFICATIONS:
            findings.append(
                "%s has classification %r, not a valid value (invariant 80)"
                % (path, control_cls))
            continue
        row_name = cross_ref.get(base)
        if row_name is None:
            findings.append(
                "%s is not cross-referenced in the register's "
                "per_control_files_already_classified list" % base)
            continue
        row = rows_by_name.get(row_name)
        if row is None:
            findings.append(
                "%s cross-references row %r, which the register does not "
                "declare" % (base, row_name))
            continue
        row_cls = row.get("classification")
        if row_cls != control_cls and not (row_cls == "mixed"):
            findings.append(
                "%s declares classification %r but its register row %r says %r"
                % (base, control_cls, row_name, row_cls))
    return findings


def selftest():
    register = load_yaml(REGISTER_PATH)
    if register is None:
        print("SELFTEST FAIL: %s unreadable" % REGISTER_PATH)
        return 2
    findings, fail_closed = check_register(register)
    if findings or fail_closed:
        print("SELFTEST FAIL: the committed register itself does not pass:")
        for f in findings:
            print("  - %s" % f)
        return 1

    cross_findings = check_per_control_files(register)
    if cross_findings:
        print("SELFTEST FAIL: cross-reference check fails against the committed tree:")
        for f in cross_findings:
            print("  - %s" % f)
        return 1

    # Negative fixture 1: an unclassified control.
    import copy
    mutated = copy.deepcopy(register)
    mutated["rows"][0]["classification"] = "sometimes"
    bad_findings, _ = check_register(mutated)
    if not bad_findings:
        print("SELFTEST FAIL: an invalid classification value was not caught")
        return 1

    # Negative fixture 2: a per-control file that disagrees with its row.
    mutated2 = copy.deepcopy(register)
    for row in mutated2["rows"]:
        if row.get("control") == "Secret access":
            row["classification"] = "fail-open"
    mismatch_findings = check_per_control_files(mutated2)
    if not mismatch_findings:
        print("SELFTEST FAIL: a register/per-control-file classification "
              "mismatch was not caught")
        return 1

    print("L5-T10 SELF-VERIFY PASS")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()

    register = load_yaml(REGISTER_PATH)
    if register is None:
        print("RESULT FAIL register-unreadable %s" % REGISTER_PATH)
        return 2

    findings, fail_closed = check_register(register)
    findings += check_per_control_files(register)

    for f in findings:
        print("FINDING %s" % f)
    if findings:
        print("RESULT FAIL")
        return 2 if fail_closed else 1
    print("RESULT PASS (%d controls classified, all per-control files consistent)"
          % EXPECTED_ROW_COUNT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
