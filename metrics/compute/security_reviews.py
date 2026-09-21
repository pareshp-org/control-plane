#!/usr/bin/env python3
"""metrics/compute/security_reviews.py (L4-P7-12)

Finding count by severity and unfixed-finding age from
records/security-reviews/. Master Spec v4.0 §97.2 lines 8858, 8884;
§52.2 line 4575. An unfixed finding with no owner is a malformed record
(the schema requires one to track it visibly) and is rejected outright
rather than silently aged with an unknown owner.

Usage: security_reviews.py --store <records/security-reviews path> [--as-of ISODATE] --json
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
    p.add_argument("--as-of", default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        rows = read_store(args.store)
    except FileNotFoundError:
        fail(args.store, "store-absent")
        return 1

    if not rows:
        emit(unbaselined(args.store, "security_review_measures"))
        return 0

    as_of = datetime.date.fromisoformat(args.as_of) if args.as_of else datetime.date.today()

    count_by_severity = {}
    unfixed_ages_days = []
    for path, doc in rows:
        if not isinstance(doc, dict):
            fail(args.store, "malformed-record:%s" % path)
        for finding in doc.get("findings") or []:
            sev = finding.get("severity", "UNKNOWN")
            count_by_severity[sev] = count_by_severity.get(sev, 0) + 1
            disposition = (finding.get("disposition") or "").lower()
            is_fixed = disposition in ("fixed", "resolved", "closed")
            if not is_fixed:
                if not finding.get("owner"):
                    fail(args.store, "unfixed-finding-no-owner:%s" % path)
                due = parse_date(finding.get("due"))
                if due:
                    unfixed_ages_days.append((as_of - due).days)

    emit({
        "store": args.store,
        "measure": "security_review_measures",
        "n": len(rows),
        "finding_count_by_severity": count_by_severity,
        "unfixed_finding_count": len(unfixed_ages_days),
        "unfixed_finding_age_days_max": max(unfixed_ages_days) if unfixed_ages_days else None,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
