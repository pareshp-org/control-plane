#!/usr/bin/env python3
"""metrics/compute/support.py (L4-P7-10)

Support load (count) and first-response latency by severity, from
records/support/. Master Spec v4.0 §103.4 line 9825; §22.4 lines
2238-2249; AT-104 line 9387. The first-response clock anchors to the
`received` field (the board's own intake timestamp, Section 22.2 line
2214) - NEVER to `timestamp` (the record-write timestamp, which can lag
intake) and never to any ingest-event timestamp.

Usage: support.py --store <records/support path> --json
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import emit, fail, parse_ts, read_store, unbaselined  # noqa: E402


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
        emit(unbaselined(args.store, "support_measures"))
        return 0

    load_by_severity = {}
    first_response_by_severity = {}
    for path, doc in rows:
        if not isinstance(doc, dict):
            fail(args.store, "malformed-record:%s" % path)
        sev = doc.get("severity_at_intake", "UNKNOWN")
        load_by_severity[sev] = load_by_severity.get(sev, 0) + 1
        received = parse_ts(doc.get("received"))
        first_response = parse_ts(doc.get("first_response"))
        if received and first_response:
            first_response_by_severity.setdefault(sev, []).append(
                (first_response - received).total_seconds()
            )

    avg_first_response = {
        sev: round(sum(vals) / len(vals), 1) for sev, vals in first_response_by_severity.items()
    }
    emit({
        "store": args.store,
        "measure": "support_measures",
        "n": len(rows),
        "load_by_severity": load_by_severity,
        "first_response_seconds_avg_by_severity": avg_first_response,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
