#!/usr/bin/env python3
"""metrics/compute/eval.py (L4-P7-11)

Eval pass rate from records/eval/, plus SIG-42 regression detection: a
scored dimension falling more than 5 percentage points below its recorded
baseline (Master Spec v4.0 SIG-42, line 4571) is a regression. Multiple
regressed dimensions in ONE run on ONE product coalesce into exactly one
triage event per (product, run) - never one per dimension (§38.3 lines
3433-3434).

Usage: eval.py --store <records/eval path> [--tolerance-pp 5] --json
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import emit, fail, read_store, unbaselined  # noqa: E402

DEFAULT_TOLERANCE_PP = 5.0


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--store", required=True)
    p.add_argument("--tolerance-pp", type=float, default=DEFAULT_TOLERANCE_PP)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        rows = read_store(args.store)
    except FileNotFoundError:
        fail(args.store, "store-absent")
        return 1

    if not rows:
        emit(unbaselined(args.store, "eval_measures"))
        return 0

    passed = 0
    triage_events = []
    for path, doc in rows:
        if not isinstance(doc, dict):
            fail(args.store, "malformed-record:%s" % path)
        if doc.get("result") == "pass":
            passed += 1
        regressed_dims = [
            d.get("dimension")
            for d in (doc.get("dimensions") or [])
            if isinstance(d, dict)
            and d.get("baseline") is not None
            and d.get("score") is not None
            and (d["baseline"] - d["score"]) > args.tolerance_pp
        ]
        if regressed_dims:
            # ONE triage event per (product, run), naming every regressed
            # dimension - never one event per dimension.
            triage_events.append({
                "record_id": doc.get("id"),
                "product": doc.get("product"),
                "regressed_dimensions": regressed_dims,
                "signal_id": "SIG-42",
            })

    emit({
        "store": args.store,
        "measure": "eval_measures",
        "n": len(rows),
        "pass_rate": round(passed / len(rows), 4),
        "sig42_triage_events": triage_events,
        "sig42_triage_event_count": len(triage_events),
    })
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
