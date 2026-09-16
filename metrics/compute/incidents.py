#!/usr/bin/env python3
"""metrics/compute/incidents.py (L4-P7-07)

MTTR, incident frequency by severity, and detection-to-response latency
from records/incidents/. Master Spec v4.0 §103.3 lines 9805-9809.
Detection-to-response latency is reported per severity, since each
product's declared support_model sets a different target per severity
band (this module reports the raw latency; interpreting it against a
product's support_model is the register/declaration's job, not this
computation's).

Usage: incidents.py --store <records/incidents path> --json
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
        emit(unbaselined(args.store, "incident_measures"))
        return 0

    by_severity = {}
    mttr_seconds = []
    detect_to_respond_seconds = []
    for path, doc in rows:
        if not isinstance(doc, dict):
            fail(args.store, "malformed-record:%s" % path)
        sev = doc.get("severity", "UNKNOWN")
        by_severity[sev] = by_severity.get(sev, 0) + 1
        detected = parse_ts(doc.get("detected"))
        responded = parse_ts(doc.get("responded"))
        resolved = parse_ts(doc.get("resolved"))
        if detected and resolved:
            mttr_seconds.append((resolved - detected).total_seconds())
        if detected and responded:
            detect_to_respond_seconds.append((responded - detected).total_seconds())

    result = {
        "store": args.store,
        "measure": "incident_measures",
        "n": len(rows),
        "frequency_by_severity": by_severity,
        "mttr_seconds_avg": round(sum(mttr_seconds) / len(mttr_seconds), 1) if mttr_seconds else None,
        "mttr_n": len(mttr_seconds),
        "detection_to_response_seconds_avg": (
            round(sum(detect_to_respond_seconds) / len(detect_to_respond_seconds), 1)
            if detect_to_respond_seconds else None
        ),
        "detection_to_response_n": len(detect_to_respond_seconds),
    }
    emit(result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
