#!/usr/bin/env python3
"""metrics/compute/status_requests.py (L4-P7-17)

Count of Coordination-category status-request events from the event log,
by ISO week - derived, never hand-counted. Master Spec v4.0 §103.13 line
9969. The Coordination category's status-request identifier is
status_request_received (n=73 in metrics/taxonomy/event-types.yaml); any
other event_type is excluded, regardless of how similar its payload
looks.

Usage: status_requests.py --store <events path> --json
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import emit, fail, parse_ts, read_store, unbaselined  # noqa: E402

STATUS_REQUEST_EVENT_TYPE = "status_request_received"


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

    matching = [
        doc for _p, doc in rows
        if isinstance(doc, dict) and doc.get("event_type") == STATUS_REQUEST_EVENT_TYPE
    ]
    if not matching:
        emit(unbaselined(args.store, "status_request_measures"))
        return 0

    by_week = {}
    for doc in matching:
        occurred = parse_ts(doc.get("occurred_at"))
        if occurred:
            iso = occurred.isocalendar()
            key = "%04d-W%02d" % (iso[0], iso[1])
            by_week[key] = by_week.get(key, 0) + 1

    emit({
        "store": args.store,
        "measure": "status_request_measures",
        "event_type": STATUS_REQUEST_EVENT_TYPE,
        "n": len(matching),
        "count_by_week": by_week,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
