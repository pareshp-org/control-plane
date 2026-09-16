#!/usr/bin/env python3
"""metrics/compute/deployments.py (L4-P7-06)

Deployment frequency, deployment failure rate, rollback rate and
merged-but-not-deployed, all derived from records/deployments/ (and the
event log for merge_completed events, for the last measure). Master Spec
v4.0 §103.2 lines 9791-9798; §32 lines 2803-2829. Never a hand-maintained
number: every figure below is counted from the record/event files
themselves, nothing is looked up in a config file.

Usage: deployments.py --store <records/deployments path> [--events <events path>] --json
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import emit, fail, parse_ts, read_store, unbaselined  # noqa: E402


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--store", required=True)
    p.add_argument("--events", default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        rows = read_store(args.store)
    except FileNotFoundError:
        fail(args.store, "store-absent")
        return 1

    if not rows:
        emit(unbaselined(args.store, "deployment_measures"))
        return 0

    total = len(rows)
    failed = 0
    rolled_back = 0
    dates = []
    for path, doc in rows:
        if not isinstance(doc, dict):
            fail(args.store, "malformed-record:%s" % path)
        if doc.get("smoke_result") == "fail":
            failed += 1
        if doc.get("rollback_of") not in (None, "null"):
            rolled_back += 1
        ts = parse_ts(doc.get("timestamp"))
        if ts:
            dates.append(ts.date())

    span_days = (max(dates) - min(dates)).days + 1 if len(dates) >= 2 else 1
    frequency_per_day = round(total / span_days, 4)

    merged_not_deployed = None
    if args.events and os.path.isdir(args.events):
        merged = 0
        deployed_digests = {
            (doc.get("digest") or {}).get("digest") if isinstance(doc.get("digest"), dict) else None
            for _p, doc in rows
        }
        for path, doc in read_store(args.events):
            if isinstance(doc, dict) and doc.get("event_type") == "merge_completed":
                merged += 1
        merged_not_deployed = max(merged - total, 0)

    result = {
        "store": args.store,
        "measure": "deployment_measures",
        "n": total,
        "deployment_frequency_per_day": frequency_per_day,
        "deployment_failure_rate": round(failed / total, 4),
        "rollback_rate": round(rolled_back / total, 4),
    }
    if merged_not_deployed is not None:
        result["merged_but_not_deployed"] = merged_not_deployed
    emit(result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
