#!/usr/bin/env python3
"""metrics/register/ownership.py

Owner-and-response completeness gate (L4-P7-05, Master Spec v4.0 Section
101 invariant 49, line 9530). Every declared measure must carry both a
non-empty `owner` and a non-empty `action_on_breach`. A measure with
either absent or empty is treated as absent from the register, not
present-and-flagged: it fails the gate outright (exit 1), it is never
printed as a warning that a caller could ignore.

Usage: ownership.py <metric-declarations.yaml>
Exit 0 on success (silent; the caller prints OWNERSHIP OK).
Exit 1 with one OWNERSHIP FAIL line per violation on failure.
"""
import sys

import yaml


def main(argv):
    if not argv:
        print("usage: ownership.py <metric-declarations.yaml>")
        return 2
    decl_path = argv[0]
    try:
        doc = yaml.safe_load(open(decl_path, encoding="utf-8")) or {}
    except Exception as exc:
        print("OWNERSHIP FAIL: unreadable: %s" % exc)
        return 1

    metrics = doc.get("metrics") or []
    errs = []
    for m in metrics:
        mid = m.get("id", "<unnamed>")
        owner = (m.get("owner") or "").strip()
        action = (m.get("action_on_breach") or "").strip()
        if not owner:
            errs.append("measure %s has no owner" % mid)
        if not action:
            errs.append("measure %s has no action_on_breach" % mid)

    if errs:
        for e in errs:
            print("OWNERSHIP FAIL: %s" % e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
