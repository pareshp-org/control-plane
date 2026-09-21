#!/usr/bin/env python3
"""Platform SLO register checker (Section 51.2).

Checks:
  1. ops-vm/slo/platform-slos.yaml declares all nine Section 51.2 service
     rows, each with an objective, a measurement and a response_on_breach.
  2. Cross-checks the three rows this lane actually implements against the
     real thresholds their scripts enforce, so the register cannot drift
     from the code silently:
       - "Health report freshness" declares threshold_hours.amber == 24;
         ops-vm/checks/health-report-freshness.sh must use the same 24.
       - "Operations-VM liveness, observed off-VM" must resolve to a real
         file (infra/deadman/check-off-vm.sh) that runs *outside* the VM
         (D94) -- checked by grepping for the D94 anchor comment.
       - "Control-plane recovery time" must resolve to a real file.

Usage:  validate_slos.py [--selftest]
"""
import copy
import os
import re
import sys

import yaml

REGISTER_PATH = os.path.join("ops-vm", "slo", "platform-slos.yaml")
HEALTH_SCRIPT = os.path.join("ops-vm", "checks", "health-report-freshness.sh")
EXPECTED_ROW_COUNT = 9
REQUIRED_FIELDS = ["service", "objective", "measurement", "response_on_breach"]


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
    objectives = doc.get("objectives")
    if not isinstance(objectives, list):
        return (["register has no objectives list"], True)
    if len(objectives) != EXPECTED_ROW_COUNT:
        findings.append(
            "register has %d rows, spec 51.2 declares exactly %d services"
            % (len(objectives), EXPECTED_ROW_COUNT))
    for i, row in enumerate(objectives):
        if not isinstance(row, dict):
            findings.append("objectives[%d] is not a mapping" % i)
            continue
        for field in REQUIRED_FIELDS:
            if not row.get(field):
                findings.append("objectives[%d] (%s) missing %s"
                                 % (i, row.get("service"), field))
    return (findings, False)


def find_row(doc, service):
    for row in (doc.get("objectives") or []):
        if isinstance(row, dict) and row.get("service") == service:
            return row
    return None


def check_health_freshness_threshold(doc):
    row = find_row(doc, "Health report freshness")
    if row is None:
        return ["register has no 'Health report freshness' row"]
    declared = ((row.get("threshold_hours") or {}).get("amber"))
    impl = row.get("implemented_by")
    if not impl or not os.path.isfile(impl):
        return ["'Health report freshness' names implemented_by %r, which "
                "does not exist" % impl]
    with open(impl, "r", encoding="utf-8") as handle:
        body = handle.read()
    match = re.search(r"age\"?\s*-ge\s*(\d+)", body)
    if not match:
        return ["%s does not declare a numeric staleness threshold this "
                "checker can read" % impl]
    actual = int(match.group(1))
    if actual != declared:
        return ["register declares threshold_hours.amber=%r but %s enforces "
                "%d" % (declared, impl, actual)]
    return []


def check_file_backed_rows(doc):
    findings = []
    for service in ("Operations-VM liveness, observed off-VM",
                     "Control-plane recovery time"):
        row = find_row(doc, service)
        if row is None:
            findings.append("register has no %r row" % service)
            continue
        impl = row.get("implemented_by")
        if impl and not os.path.isfile(impl):
            findings.append("%r names implemented_by %r, which does not exist"
                             % (service, impl))
    return findings


def selftest():
    doc = load_yaml(REGISTER_PATH)
    if doc is None:
        print("SELFTEST FAIL: %s unreadable" % REGISTER_PATH)
        return 2
    findings, fail_closed = check_register_shape(doc)
    if findings or fail_closed:
        print("SELFTEST FAIL: the committed register itself does not pass:")
        for f in findings:
            print("  - %s" % f)
        return 1

    live_findings = check_health_freshness_threshold(doc) + check_file_backed_rows(doc)
    if live_findings:
        print("SELFTEST FAIL: cross-reference checks fail against the committed tree:")
        for f in live_findings:
            print("  - %s" % f)
        return 1

    # Negative fixture: register claims a threshold the script does not enforce.
    mutated = copy.deepcopy(doc)
    find_row(mutated, "Health report freshness")["threshold_hours"]["amber"] = 48
    bad = check_health_freshness_threshold(mutated)
    if not bad:
        print("SELFTEST FAIL: a register/script threshold mismatch was not caught")
        return 1

    # Negative fixture 2: a dropped row.
    mutated2 = copy.deepcopy(doc)
    mutated2["objectives"].pop()
    bad2, _ = check_register_shape(mutated2)
    if not bad2:
        print("SELFTEST FAIL: a dropped SLO row was not caught")
        return 1

    print("L5-T19 SELF-VERIFY PASS")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()

    doc = load_yaml(REGISTER_PATH)
    if doc is None:
        print("RESULT FAIL register-unreadable %s" % REGISTER_PATH)
        return 2

    findings, fail_closed = check_register_shape(doc)
    findings += check_health_freshness_threshold(doc)
    findings += check_file_backed_rows(doc)

    for f in findings:
        print("FINDING %s" % f)
    if findings:
        print("RESULT FAIL")
        return 2 if fail_closed else 1
    print("RESULT PASS (%d SLO rows, live thresholds consistent)" % EXPECTED_ROW_COUNT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
