#!/usr/bin/env python3
"""metrics/compute/learning_loop.py (L4-P7-14, SIG-47)

Counts open postmortems older than 30 days with unclosed generated items
(from records/postmortems/) and resolved incidents with no linked
regression-test item (from records/incidents/, cross-referenced against
their postmortem's items list). Master Spec v4.0 §52.2 line 4571; §58.4
lines 5017-5047. D-L4-TL-4 decided: this signal is SIG-47, never SIG-43
(the Founder-operating-load signal SIG-43 is unrelated).

A postmortem with no `items` key at all still counts as open if it has no
`closed` date and is old enough - an absent items list is not evidence of
closure, it is evidence of nothing tracked, which is exactly the case
this measure exists to surface.

Usage: learning_loop.py --store <records/postmortems path> [--incidents-store <records/incidents path>] [--as-of ISODATE] [--stale-days 30] --json
"""
import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import emit, fail, parse_date, read_store, unbaselined  # noqa: E402

SIGNAL_ID = "SIG-47"


def postmortem_is_open_and_stale(doc, as_of, stale_days):
    if doc.get("closed"):
        return False
    due = parse_date(doc.get("due"))
    age_days = (as_of - due).days if due else None
    items = doc.get("items") or []
    unclosed_items = [i for i in items if i.get("status") not in ("closed", "deferred")]
    # No items declared at all is not closure evidence - stays open by default
    # unless the postmortem itself explicitly permits zero tracked work
    # (line 5044) AND is not stale yet.
    is_stale = age_days is not None and age_days > stale_days
    return is_stale and (not items or unclosed_items)


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--store", required=True)
    p.add_argument("--incidents-store", default=None)
    p.add_argument("--as-of", default=None)
    p.add_argument("--stale-days", type=int, default=30)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        pm_rows = read_store(args.store)
    except FileNotFoundError:
        fail(args.store, "store-absent")
        return 1

    as_of = datetime.date.fromisoformat(args.as_of) if args.as_of else datetime.date.today()

    open_stale_count = 0
    for path, doc in pm_rows:
        if not isinstance(doc, dict):
            fail(args.store, "malformed-record:%s" % path)
        if postmortem_is_open_and_stale(doc, as_of, args.stale_days):
            open_stale_count += 1

    unlinked_incidents = 0
    if args.incidents_store:
        try:
            inc_rows = read_store(args.incidents_store)
        except FileNotFoundError:
            fail(args.incidents_store, "incidents-store-absent")
            return 1
        pm_by_ref = {}
        for path, doc in pm_rows:
            pm_by_ref[os.path.basename(path)] = doc
        for path, doc in inc_rows:
            if not isinstance(doc, dict):
                fail(args.incidents_store, "malformed-record:%s" % path)
            if not doc.get("resolved"):
                continue
            pm_ref = doc.get("postmortem")
            linked_pm = pm_by_ref.get(os.path.basename(pm_ref)) if pm_ref else None
            has_regression_test = linked_pm and any(
                i.get("type") == "regression_test" for i in (linked_pm.get("items") or [])
            )
            if not has_regression_test:
                unlinked_incidents += 1

    if not pm_rows:
        result = unbaselined(args.store, "learning_loop_measures")
        result["signal_id"] = SIGNAL_ID
        emit(result)
        return 0

    emit({
        "store": args.store,
        "measure": "learning_loop_measures",
        "signal_id": SIGNAL_ID,
        "n": len(pm_rows),
        "open_stale_postmortems": open_stale_count,
        "incidents_without_linked_regression_test": unlinked_incidents,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
