#!/usr/bin/env python3
"""metrics/compute/uat.py (L4-P7-09)

UAT coverage (count of UAT executions naming a work_item) and pass rate,
from records/uat/. Master Spec v4.0 Section 97.2 line 8848.

Usage: uat.py --store <records/uat path> --json
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import emit, fail, read_store, unbaselined  # noqa: E402


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--store", required=True)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        rows = read_store(args.store)
    except FileNotFoundError:
        fail(args.store, "store-absent")
        return 1

    if not rows:
        emit(unbaselined(args.store, "uat_measures"))
        return 0

    passed = 0
    with_work_item = 0
    for path, doc in rows:
        if not isinstance(doc, dict) or doc.get("result") not in ("pass", "fail"):
            fail(args.store, "malformed-record:%s" % path)
        if doc.get("result") == "pass":
            passed += 1
        if doc.get("work_item"):
            with_work_item += 1

    emit({
        "store": args.store,
        "measure": "uat_measures",
        "n": len(rows),
        "pass_rate": round(passed / len(rows), 4),
        "coverage_with_work_item": with_work_item,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
