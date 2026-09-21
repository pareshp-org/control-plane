#!/usr/bin/env python3
"""metrics/compute/restore.py (L4-P7-08)

Restore-test freshness (days since the most recent PASSING restore test,
against the 90-day rolling floor of Section 44.2 line 3997 - tightened per
product when reliability_criticality demands it, which this module
reports as a ratio against 90 so a caller can re-apply a tighter product
floor) and failed-restore-test count (target zero), both from
records/restore-tests/. Master Spec v4.0 §44.2 lines 3993-4002; §103.3
lines 9810-9811.

Usage: restore.py --store <records/restore-tests path> [--floor-days 90] --json
"""
import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import emit, fail, parse_ts, read_store, unbaselined  # noqa: E402

DEFAULT_FLOOR_DAYS = 90


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--store", required=True)
    p.add_argument("--floor-days", type=int, default=DEFAULT_FLOOR_DAYS)
    p.add_argument("--as-of", default=None, help="ISO date; default: today (UTC)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        rows = read_store(args.store)
    except FileNotFoundError:
        fail(args.store, "store-absent")
        return 1

    if not rows:
        emit(unbaselined(args.store, "restore_measures"))
        return 0

    as_of = (
        datetime.datetime.fromisoformat(args.as_of)
        if args.as_of
        else datetime.datetime.utcnow()
    )

    failed = 0
    last_pass_ts = None
    for path, doc in rows:
        if not isinstance(doc, dict):
            fail(args.store, "malformed-record:%s" % path)
        if doc.get("result") != "pass" or doc.get("integrity_check_result") != "pass":
            failed += 1
            continue
        ts = parse_ts(doc.get("timestamp"))
        if ts and (last_pass_ts is None or ts > last_pass_ts):
            last_pass_ts = ts

    freshness_days = (as_of - last_pass_ts).days if last_pass_ts else None
    result = {
        "store": args.store,
        "measure": "restore_measures",
        "n": len(rows),
        "failed_restore_tests": failed,
        "days_since_last_pass": freshness_days,
        "floor_days": args.floor_days,
        "within_floor": (freshness_days is not None and freshness_days <= args.floor_days),
    }
    emit(result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
