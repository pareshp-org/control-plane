#!/usr/bin/env python3
"""Prove the Section 43.4 containment hook cannot fall behind.

Three assertions:
  K1 the C-04 credential list is EXACTLY the set of fifth-tier entries on disk
  K2 C-04 is a named step, not an inference (Section 43.4)
  K3 evidence preservation precedes rotation (Section 43.1)

K1 is the one that matters over time: add a sixth fifth-tier credential and
this check fails until the containment checklist names it too.

Fail-closed (invariant 80): a missing checklist or an empty fifth-tier
directory is exit 2.

Usage: check_containment.py [<checklist.yaml> [<fifth-tier-dir>]]
"""
import glob
import os
import sys

import yaml


def main(argv):
    checklist = argv[1] if len(argv) > 1 else os.path.join(
        "access", "secrets", "incident", "containment-checklist.yaml")
    fifth = argv[2] if len(argv) > 2 else os.path.join(
        "access", "secrets", "fifth-tier")
    if not os.path.isfile(checklist):
        print("RESULT FAIL checklist-unreadable %s" % checklist)
        return 2
    try:
        with open(checklist, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
    except Exception as exc:                                    # fail closed
        print("RESULT FAIL checklist-unparseable %s" % exc)
        return 2
    steps = {str(s.get("id")): s for s in (doc.get("steps") or [])}
    rotate = steps.get("C-04")
    if rotate is None:
        print("RESULT FAIL no-C-04-rotation-step")
        return 2
    entries = sorted(os.path.basename(p)[:-5]
                     for p in glob.glob(os.path.join(fifth, "*.yaml")))
    if not entries:
        print("RESULT FAIL no-fifth-tier-entries %s" % fifth)
        return 2

    failed = 0
    listed = sorted(str(c) for c in (rotate.get("credentials") or []))
    if listed == entries:
        print("ASSERTION K1 OK %d credentials enumerated" % len(entries))
    else:
        print("ASSERTION K1 FAIL checklist=%r fifth-tier=%r" % (listed, entries))
        failed += 1

    if rotate.get("named_step") is True \
       and rotate.get("inferred_from_generic_rule") is False:
        print("ASSERTION K2 OK named-step-not-inference")
    else:
        print("ASSERTION K2 FAIL C-04 is not declared a named step")
        failed += 1

    preserve = [s for s in steps.values() if s.get("phase") == "preserve-evidence"]
    if preserve and min(int(s["order"]) for s in preserve) < int(rotate["order"]):
        print("ASSERTION K3 OK evidence-precedes-rotation")
    else:
        print("ASSERTION K3 FAIL rotation is ordered before evidence capture")
        failed += 1

    print("FAILED %d" % failed)
    if failed:
        print("RESULT FAIL")
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
