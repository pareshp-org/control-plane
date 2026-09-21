#!/usr/bin/env python3
"""metrics/compute/lifecycle_cadence.py (L4-P7-18)

Onboarding time to first accepted PR (records/onboarding/), launch
cadence (records/launches/), and demo cadence (records/demos/). Master
Spec v4.0 §97.2 lines 8871-8874.

Convention this module fixes (onboarding.schema.json's `phase` field is
deliberately not an enum, Section 96.6 line 8781): the milestone record
for this measure is the onboarding record whose `phase` is literally
"first-accepted-pr". Such a record exists specifically to report that
milestone and MUST carry `first_accepted_pr`; one that does not is
malformed for this measure and is rejected outright, never silently
skipped. Onboarding records for any other phase are counted but not
required to carry first_accepted_pr.

Usage: lifecycle_cadence.py --store <records/onboarding path>
       [--launches-store <path>] [--demos-store <path>] --json
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import emit, fail, parse_date, read_store, unbaselined  # noqa: E402

MILESTONE_PHASE = "first-accepted-pr"


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--store", required=True)
    p.add_argument("--launches-store", default=None)
    p.add_argument("--demos-store", default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        onb_rows = read_store(args.store)
    except FileNotFoundError:
        fail(args.store, "store-absent")
        return 1

    first_pr_days = []
    for path, doc in onb_rows:
        if not isinstance(doc, dict):
            fail(args.store, "malformed-record:%s" % path)
        if doc.get("phase") == MILESTONE_PHASE:
            if not doc.get("first_accepted_pr"):
                fail(args.store, "milestone-record-missing-first-accepted-pr:%s" % path)
            completed = parse_date(doc.get("completed"))
            first_pr = parse_date(doc.get("first_accepted_pr"))
            if completed and first_pr:
                first_pr_days.append((first_pr - completed).days)

    result = {
        "store": args.store,
        "measure": "lifecycle_cadence_measures",
        "n": len(onb_rows),
        "onboarding_time_to_first_pr_days_avg": (
            round(sum(first_pr_days) / len(first_pr_days), 2) if first_pr_days else None
        ),
    }

    for label, store in (("launch_cadence_n", args.launches_store), ("demo_cadence_n", args.demos_store)):
        if store:
            try:
                rows = read_store(store)
            except FileNotFoundError:
                fail(store, "store-absent")
                return 1
            result[label] = len(rows)

    if not onb_rows and not any(result.get(k) for k in ("launch_cadence_n", "demo_cadence_n")):
        emit(unbaselined(args.store, "lifecycle_cadence_measures"))
        return 0

    emit(result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
