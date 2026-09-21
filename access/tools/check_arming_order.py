#!/usr/bin/env python
"""The D101 arming-order gate.

Refuses an arming order that cannot be satisfied. The failure it exists to
prevent is named in Section 98.2 and Section 95.4: arming a
Code-Owner-and-approval gate while no Team grants Write leaves nobody whose
approval counts, and the team experiences its merges mysteriously breaking.

Assertions:
  AOG-1  every step that arms a gate transitively requires a step that grants Write
  AOG-2  every Write-granting step has a strictly lower index than every arming step
  AOG-3  no step requires a step with a higher index
  AOG-4  indexes run 1..N with no gap or duplicate, and each id matches its index
  AOG-5  the arming step requires the CODEOWNERS generation step

Usage: check_arming_order.py [--config PATH]
Exit 0 on success, 1 on any failed assertion.
"""
import argparse
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT = os.path.join(ROOT, "access", "arming", "arming-order.yaml")
CODEOWNERS_STEP_MARKER = "generate_codeowners.py"


def transitive_requires(steps_by_id, start_id, seen=None):
    if seen is None:
        seen = set()
    for required in steps_by_id.get(start_id, {}).get("requires", []):
        if required in seen:
            continue
        seen.add(required)
        transitive_requires(steps_by_id, required, seen)
    return seen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT)
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)

    steps = doc.get("steps", [])
    by_id = dict((step["id"], step) for step in steps)
    arming = [step for step in steps if step.get("arms_a_gate")]
    granting = [step for step in steps if step.get("grants_write")]

    aog1 = bool(arming) and bool(granting)
    for step in arming:
        reached = transitive_requires(by_id, step["id"])
        if not any(by_id.get(ident, {}).get("grants_write") for ident in reached):
            aog1 = False

    aog2 = bool(arming) and bool(granting)
    for grant in granting:
        for arm in arming:
            if not grant["index"] < arm["index"]:
                aog2 = False

    aog3 = True
    for step in steps:
        for required in step.get("requires", []):
            if required not in by_id or by_id[required]["index"] >= step["index"]:
                aog3 = False

    indexes = sorted(step["index"] for step in steps)
    aog4 = indexes == list(range(1, len(steps) + 1))
    for step in steps:
        if step["id"] != "AO-%02d" % step["index"]:
            aog4 = False

    codeowners_ids = [step["id"] for step in steps
                      if CODEOWNERS_STEP_MARKER in str(step.get("declared_in", ""))]
    aog5 = bool(codeowners_ids) and bool(arming)
    for step in arming:
        reached = transitive_requires(by_id, step["id"])
        if not any(ident in reached for ident in codeowners_ids):
            aog5 = False

    assertions = [
        ("AOG-1", "every arming step transitively requires a Write-granting step", aog1),
        ("AOG-2", "every Write-granting step precedes every arming step", aog2),
        ("AOG-3", "no step requires a step with a higher index", aog3),
        ("AOG-4", "indexes run 1..N with no gap or duplicate and ids match", aog4),
        ("AOG-5", "the arming step requires CODEOWNERS generation", aog5),
    ]

    failed = 0
    for ident, statement, ok in assertions:
        if not ok:
            print("FAIL %s: %s" % (ident, statement))
            failed += 1
    if failed:
        print("ARMING-ORDER: FAIL (%d of %d assertions)" % (failed, len(assertions)))
        return 1
    print("ARMING-ORDER: PASS (%d assertions)" % len(assertions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
