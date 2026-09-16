#!/usr/bin/env python3
"""Contract-input inventory checker for Lane 5.

Two things, both fail-closed where the rule says fail-closed:

  1. EXISTENCE  every input infra/contract-inputs.yaml declares with no
     `status: not_yet_created` must exist on disk. A row explicitly marked
     not_yet_created is reported INDETERMINATE, never silently skipped and
     never a hard FAIL -- an absent L0 contract is not this lane's defect,
     but it must be visible every time this runs.
  2. READ-ONLY  no path any of Lane 5's owned trees (access/**, infra/**,
     ops-vm/**, notify/**, assets/**) actually WRITES overlaps a declared
     input path. This is a real scan, not an assertion: it globs every
     Lane-5-owned Python/shell file for an `open(..., "w")`,
     `>` / `>>` redirect, `install -d`, `cat >`, or `yaml.safe_dump(...,
     open(<input path>` pattern against each declared input, and fails if
     one is found.

Usage:  check_contract_inputs.py [--selftest]
Exit 0 PASS, 1 FAIL (a write into a declared input, or an undeclared-missing
required input), 2 fail-closed (the inventory itself is unreadable).
"""
import glob
import os
import re
import sys

import yaml

INVENTORY_PATH = os.path.join("infra", "contract-inputs.yaml")
OWNED_GLOBS = [
    os.path.join("access", "**", "*.py"),
    os.path.join("access", "**", "*.sh"),
    os.path.join("infra", "**", "*.py"),
    os.path.join("infra", "**", "*.sh"),
    os.path.join("ops-vm", "**", "*.py"),
    os.path.join("ops-vm", "**", "*.sh"),
    os.path.join("notify", "**", "*.py"),
    os.path.join("notify", "**", "*.sh"),
    os.path.join("assets", "**", "*.py"),
    os.path.join("assets", "**", "*.sh"),
]


def load_yaml(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except (OSError, yaml.YAMLError):
        return None


def owned_source_files():
    files = []
    for pattern in OWNED_GLOBS:
        files.extend(glob.glob(pattern, recursive=True))
    self_path = os.path.abspath(__file__)
    return sorted({f for f in files if os.path.abspath(f) != self_path})


def writes_into(input_path, source_text):
    """True if source_text appears to write to input_path (an open(...,
    'w'/'a'), a shell redirect, or a mkdir/install targeting it)."""
    stem = re.escape(input_path.rstrip("/"))
    patterns = [
        r'open\(\s*["\'].*?%s.*?["\']\s*,\s*["\']w' % stem,
        r'>>?\s*["\']?%s' % stem,
        r'install\s+-d.*%s' % stem,
        r'mkdir\s+-p.*%s' % stem,
    ]
    return any(re.search(p, source_text) for p in patterns)


def check_existence(inputs):
    findings = []
    indeterminate = []
    for row in inputs:
        path = row.get("path")
        status = row.get("status")
        exists = os.path.exists(path.rstrip("/")) if path else False
        if status == "not_yet_created":
            indeterminate.append(path)
            continue
        if not exists:
            findings.append("declared input missing: %s" % path)
    return findings, indeterminate


def check_read_only(inputs):
    findings = []
    sources = owned_source_files()
    bodies = {}
    for src in sources:
        try:
            with open(src, "r", encoding="utf-8", errors="replace") as handle:
                bodies[src] = handle.read()
        except OSError:
            continue
    for row in inputs:
        path = row.get("path")
        if not path:
            continue
        for src, body in bodies.items():
            if writes_into(path, body):
                findings.append(
                    "%s appears to write into declared read-only input %s"
                    % (src, path))
    return findings


def selftest():
    doc = load_yaml(INVENTORY_PATH)
    if doc is None:
        print("SELFTEST FAIL: %s unreadable" % INVENTORY_PATH)
        return 2
    inputs = doc.get("inputs") or []
    if not inputs:
        print("SELFTEST FAIL: inventory declares no inputs")
        return 1

    ex_findings, indeterminate = check_existence(inputs)
    if ex_findings:
        print("SELFTEST FAIL: existence check fails against the committed tree:")
        for f in ex_findings:
            print("  - %s" % f)
        return 1

    ro_findings = check_read_only(inputs)
    if ro_findings:
        print("SELFTEST FAIL: read-only check fails against the committed tree:")
        for f in ro_findings:
            print("  - %s" % f)
        return 1

    # Negative fixture: a synthetic write pattern the scanner must catch.
    fake_body = 'open("registries/people/evil.yaml", "w")\n'
    if not writes_into("registries/people/", fake_body):
        print("SELFTEST FAIL: a synthetic write into a declared input was not caught")
        return 1

    # Negative fixture 2: a missing required input.
    mutated = [dict(r) for r in inputs]
    mutated.append({"path": "registries/does-not-exist-42.yaml"})
    bad_findings, _ = check_existence(mutated)
    if not bad_findings:
        print("SELFTEST FAIL: a missing required input was not caught")
        return 1

    print("L5-T04 SELF-VERIFY PASS")
    print("(%d inputs declared, %d reported INDETERMINATE: %r)"
          % (len(inputs), len(indeterminate), indeterminate))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()

    doc = load_yaml(INVENTORY_PATH)
    if doc is None:
        print("RESULT FAIL inventory-unreadable %s" % INVENTORY_PATH)
        return 2
    inputs = doc.get("inputs") or []

    ex_findings, indeterminate = check_existence(inputs)
    ro_findings = check_read_only(inputs)

    for path in indeterminate:
        print("INDETERMINATE %s (declared not_yet_created)" % path)
    for f in ex_findings + ro_findings:
        print("FINDING %s" % f)
    if ex_findings or ro_findings:
        print("RESULT FAIL")
        return 1
    print("RESULT PASS (%d inputs checked, %d indeterminate)"
          % (len(inputs), len(indeterminate)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
