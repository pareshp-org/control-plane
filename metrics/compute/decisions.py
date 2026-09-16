#!/usr/bin/env python3
"""metrics/compute/decisions.py (L4-P7-13)

Decision latency (prompt_received -> decided) from records/decisions/;
pending-decision queue depth and age from records/decisions/pending/.
Master Spec v4.0 §97.2 lines 8865-8866; §103.13 line 9972.

Usage: decisions.py --store <records/decisions path> --pending-store <records/decisions/pending path> [--as-of ISODATE] --json
"""
import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import emit, fail, parse_date, read_store, unbaselined  # noqa: E402


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--store", required=True)
    p.add_argument("--pending-store", default=None)
    p.add_argument("--as-of", default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        decided_rows = read_store(args.store)
    except FileNotFoundError:
        fail(args.store, "store-absent")
        return 1

    as_of = datetime.date.fromisoformat(args.as_of) if args.as_of else datetime.date.today()

    latencies_days = []
    for path, doc in decided_rows:
        if not isinstance(doc, dict):
            fail(args.store, "malformed-record:%s" % path)
        prompt_received = parse_date(doc.get("prompt_received"))
        decided = doc.get("decided")
        if prompt_received and not decided:
            fail(args.store, "decided-record-missing-decided-timestamp:%s" % path)
        decided_date = parse_date(decided)
        if prompt_received and decided_date:
            latencies_days.append((decided_date - prompt_received).days)

    result = {
        "store": args.store,
        "measure": "decision_measures",
        "n": len(decided_rows),
        "decision_latency_days_avg": (
            round(sum(latencies_days) / len(latencies_days), 2) if latencies_days else None
        ),
        "decision_latency_n": len(latencies_days),
    }

    if args.pending_store:
        try:
            pending_rows = read_store(args.pending_store)
        except FileNotFoundError:
            fail(args.pending_store, "pending-store-absent")
            return 1
        ages_days = []
        for path, doc in pending_rows:
            if not isinstance(doc, dict):
                fail(args.pending_store, "malformed-record:%s" % path)
            prompt_received = parse_date(doc.get("prompt_received"))
            if prompt_received:
                ages_days.append((as_of - prompt_received).days)
        result["pending_queue_depth"] = len(pending_rows)
        result["pending_queue_age_days_max"] = max(ages_days) if ages_days else None

    if not decided_rows and not (args.pending_store and result.get("pending_queue_depth")):
        emit(unbaselined(args.store, "decision_measures"))
        return 0

    emit(result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
