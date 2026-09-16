#!/usr/bin/env python3
"""metrics/compute/rqm.py (L4-P7-16)

30-day rolling Ready-queue-miss count and trend from the event log
(events/), excluding ready_bypass events (Section 97.5 line 8986: a
full-Ready bypass is a board-hygiene finding, never counted toward
SIG-06 - tools/records/rqm-emit already stamps sig06_counted: false on
those). Master Spec v4.0 §52.2 line 4541; §29.4 line 2670; §101 invariant
15 line 9484: this is declared a TEAM LEAD capacity signal, never an
individual one - the output never names a person, only counts and dates.

Usage: rqm.py --store <events path> [--as-of ISODATE] --json
"""
import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import emit, fail, parse_ts, read_store, unbaselined  # noqa: E402


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--store", required=True)
    p.add_argument("--as-of", default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        rows = read_store(args.store)
    except FileNotFoundError:
        fail(args.store, "store-absent")
        return 1

    as_of = (
        datetime.datetime.fromisoformat(args.as_of)
        if args.as_of
        else datetime.datetime.utcnow()
    )
    window_start = as_of - datetime.timedelta(days=30)

    rqm_events = [
        doc for _p, doc in rows
        if isinstance(doc, dict) and doc.get("event_type") == "ready_queue_miss_recorded"
    ]
    if not rqm_events:
        emit(unbaselined(args.store, "rqm_measures"))
        return 0

    counted = []
    for doc in rqm_events:
        payload = doc.get("payload") or {}
        if payload.get("sig06_counted") is False or payload.get("reason") == "ready_bypass":
            continue
        occurred = parse_ts(doc.get("occurred_at"))
        if occurred and window_start <= occurred <= as_of:
            counted.append(occurred)

    prev_window_start = window_start - datetime.timedelta(days=30)
    prev_count = 0
    for doc in rqm_events:
        payload = doc.get("payload") or {}
        if payload.get("sig06_counted") is False or payload.get("reason") == "ready_bypass":
            continue
        occurred = parse_ts(doc.get("occurred_at"))
        if occurred and prev_window_start <= occurred < window_start:
            prev_count += 1

    trend = None
    if prev_count:
        trend = round((len(counted) - prev_count) / prev_count, 4)

    emit({
        "store": args.store,
        "measure": "rqm_measures",
        "signal_id": "SIG-06",
        "scope": "team_lead_capacity",
        "rolling_30d_count": len(counted),
        "prior_30d_count": prev_count,
        "trend_vs_prior_window": trend,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
