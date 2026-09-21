#!/usr/bin/env python3
"""Rebuild-runbook 4-hour clock validator (Section 45.4).

Reads the runbook's own markdown table (never a hand-typed second copy of
the numbers) and checks, fail-closed:

  1. Every step's "Performed by" file reference exists on disk. A runbook
     step naming a file that does not exist cannot execute -- this is
     exactly the defect lanes/L5-98-DEEP-REVIEW.md B-21 found in an earlier
     attempt (timers no step ever installed).
  2. The sum of every step's estimated minutes is strictly less than the
     target, read from infra/hosts/ops-vm.yaml's rebuild_target_hours --
     never a second, independently-typed "4" in this file.
  3. Step ids run R01..RNN with no gap and no duplicate.

Usage:  rebuild_clock.py --validate <runbook.src.md> [--selftest]
Exit 0 PASS, 1 FAIL, 2 fail-closed (runbook or host declaration unreadable).
"""
import glob
import os
import re
import sys

import yaml

HOST_DECL_PATH = os.path.join("infra", "hosts", "ops-vm.yaml")
ROW_RE = re.compile(
    r"^\|\s*(R\d+)\s*\|(?P<action>[^|]*)\|(?P<by>[^|]*)\|\s*(?P<minutes>\d+)\s*\|\s*$")
FILE_REF_RE = re.compile(r"`([^`]+\.(?:sh|py|yaml|service|timer))`")


def load_target_hours():
    try:
        with open(HOST_DECL_PATH, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
    except (OSError, yaml.YAMLError):
        return None
    hours = doc.get("rebuild_target_hours")
    return hours if isinstance(hours, (int, float)) else None


def parse_steps(runbook_path):
    try:
        with open(runbook_path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError:
        return None
    steps = []
    for line in lines:
        m = ROW_RE.match(line.rstrip("\n"))
        if not m:
            continue
        step_id = m.group(1)
        minutes = int(m.group("minutes"))
        refs = FILE_REF_RE.findall(m.group("by"))
        steps.append({"id": step_id, "minutes": minutes, "refs": refs,
                       "raw": line.rstrip("\n")})
    return steps


def check_file_refs(steps):
    findings = []
    for step in steps:
        for ref in step["refs"]:
            if "*" in ref:
                if not glob.glob(ref):
                    findings.append("%s references glob %r, which matches "
                                     "no file" % (step["id"], ref))
                continue
            if not os.path.exists(ref):
                findings.append("%s references %r, which does not exist"
                                 % (step["id"], ref))
    return findings


def check_ids_contiguous(steps):
    findings = []
    numbers = []
    seen = set()
    for step in steps:
        n = int(step["id"][1:])
        if n in seen:
            findings.append("duplicate step id %s" % step["id"])
        seen.add(n)
        numbers.append(n)
    if numbers and (sorted(numbers) != list(range(min(numbers), max(numbers) + 1))):
        findings.append("step ids are not contiguous: %r" % sorted(numbers))
    return findings


def check_total_under_target(steps, target_hours):
    if target_hours is None:
        return (["%s has no numeric rebuild_target_hours" % HOST_DECL_PATH], True)
    total_minutes = sum(s["minutes"] for s in steps)
    target_minutes = target_hours * 60
    if total_minutes >= target_minutes:
        return (["total estimated minutes %d is not strictly under the "
                  "%d-minute (%.0f hour) target from %s"
                  % (total_minutes, target_minutes, target_hours, HOST_DECL_PATH)], False)
    return ([], False)


def validate(runbook_path):
    steps = parse_steps(runbook_path)
    if steps is None:
        return (["%s unreadable" % runbook_path], True)
    if not steps:
        return (["%s declares no parseable steps" % runbook_path], True)

    findings = check_file_refs(steps)
    findings += check_ids_contiguous(steps)

    target_hours = load_target_hours()
    total_findings, fail_closed = check_total_under_target(steps, target_hours)
    findings += total_findings

    return (findings, fail_closed)


def selftest():
    runbook = os.path.join("ops-vm", "rebuild", "runbook.src.md")
    findings, fail_closed = validate(runbook)
    if findings or fail_closed:
        print("SELFTEST FAIL: the committed runbook itself does not pass:")
        for f in findings:
            print("  - %s" % f)
        return 1

    # Negative fixture: a step referencing a file that does not exist.
    import tempfile
    bad_row = "| R99 | Do something | `ops-vm/tools/does-not-exist.sh` | 5 |\n"
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tmp:
        tmp.write("| Step | Action | Performed by | Estimated minutes |\n")
        tmp.write("|---|---|---|---|\n")
        tmp.write("| R01 | x | `ops-vm/lib/common.sh` | 10 |\n")
        tmp.write(bad_row)
        tmp_path = tmp.name
    try:
        bad_findings, _ = validate(tmp_path)
        if not bad_findings:
            print("SELFTEST FAIL: a step referencing a nonexistent file was not caught")
            return 1
    finally:
        os.remove(tmp_path)

    # Negative fixture: a total that exceeds the target.
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tmp:
        tmp.write("| Step | Action | Performed by | Estimated minutes |\n")
        tmp.write("|---|---|---|---|\n")
        tmp.write("| R01 | x | `ops-vm/lib/common.sh` | 300 |\n")
        tmp_path2 = tmp.name
    try:
        over_findings, _ = validate(tmp_path2)
        if not over_findings:
            print("SELFTEST FAIL: an over-budget total was not caught")
            return 1
    finally:
        os.remove(tmp_path2)

    print("L5-T22 SELF-VERIFY PASS")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--validate" not in argv:
        print("USAGE: rebuild_clock.py --validate <runbook.src.md>")
        return 2
    runbook_path = argv[argv.index("--validate") + 1]

    findings, fail_closed = validate(runbook_path)
    for f in findings:
        print("FINDING %s" % f)
    if findings:
        print("RESULT FAIL")
        return 2 if fail_closed else 1
    print("RESULT PASS (rebuild runbook clocks in under target)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
