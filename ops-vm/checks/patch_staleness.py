#!/usr/bin/env python3
"""SIG-36 control-plane patch staleness (Sections 51.4, 52.2, 62.1).

Grading, taken literally from the specification:
  Amber  when a component is beyond its declared cadence
  Red    when it is beyond twice its declared cadence (SIG-36)

Two structural rules of Section 51.4 are asserted rather than assumed:
  * every component declares current_version, cadence_days and last_patched;
    a component missing any of them cannot be graded and fails closed
  * the component marked tightest_in_stack carries the tightest cadence in the
    stack - no other component may declare a shorter cadence

Exit codes: 0 all within cadence; 2 Amber; 3 Red; 1 fail-closed.
"""
import datetime
import sys

import yaml


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "ops-vm/patch/cadence.yaml"
    try:
        doc = yaml.safe_load(open(path, "r", encoding="utf-8")) or {}
    except OSError as exc:
        print("PATCH-STALENESS: FAIL-CLOSED (%s)" % exc)
        return 1
    comps = doc.get("components") or []
    if not comps:
        print("PATCH-STALENESS: FAIL-CLOSED (no components declared)")
        return 1
    today = datetime.date.today()
    graded, tightest = [], None
    for c in comps:
        cid = c.get("id", "<unnamed>")
        for key in ("current_version", "cadence_days", "last_patched"):
            if c.get(key) in (None, ""):
                print("PATCH-STALENESS: FAIL-CLOSED (%s has no %s)" % (cid, key))
                return 1
        try:
            cad = int(c["cadence_days"])
            last = datetime.date.fromisoformat(str(c["last_patched"]))
        except (TypeError, ValueError):
            print("PATCH-STALENESS: FAIL-CLOSED (%s has an unreadable cadence "
                  "or last_patched date)" % cid)
            return 1
        if c.get("tightest_in_stack"):
            tightest = (cid, cad)
        graded.append((cid, cad, (today - last).days))
    if tightest is None:
        print("PATCH-STALENESS: FAIL-CLOSED (no component is marked "
              "tightest_in_stack; Section 51.4 requires the Layer B datasource "
              "to carry the tightest cadence in the stack)")
        return 1
    for cid, cad, _age in graded:
        if cid != tightest[0] and cad < tightest[1]:
            print("PATCH-STALENESS: FAIL-CLOSED (%s declares a cadence of %dd, "
                  "tighter than the Layer B cadence of %dd; Section 51.4 makes "
                  "Layer B the tightest in the stack)" % (cid, cad, tightest[1]))
            return 1
    rc = 0
    for cid, cad, age in sorted(graded):
        if age >= 2 * cad:
            print("%s: %dd since patch, cadence %dd -> RED" % (cid, age, cad))
            rc = 3
        elif age >= cad:
            print("%s: %dd since patch, cadence %dd -> AMBER" % (cid, age, cad))
            rc = max(rc, 2)
        else:
            print("%s: %dd since patch, cadence %dd -> OK" % (cid, age, cad))
    print("PATCH-STALENESS: %s" % {0: "PASS", 2: "AMBER", 3: "RED"}[rc])
    return rc


if __name__ == "__main__":
    sys.exit(main())
