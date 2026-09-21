#!/usr/bin/env python3
"""metrics/compute/estimates.py (L4-P7-15)

Estimation accuracy and forecast-calibration inputs from
records/estimates/. Master Spec v4.0 §29.3 line 2667; §97.2 line 8850.
Estimation accuracy uses `elapsed_net_blocked` (net of recorded Blocked
time - what the Estimation Accuracy KPI calls actual effort). Forecast
calibration uses `elapsed` (raw elapsed, what forecast calibration
reads). The two are never confused: this module reports both ratios
against `point_value` separately so a caller cannot accidentally swap
them.

Usage: estimates.py --store <records/estimates path> --json
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import emit, fail, read_store, unbaselined  # noqa: E402


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
        emit(unbaselined(args.store, "estimate_measures"))
        return 0

    accuracy_ratios = []
    calibration_ratios = []
    for path, doc in rows:
        if not isinstance(doc, dict):
            fail(args.store, "malformed-record:%s" % path)
        point_value = doc.get("point_value")
        elapsed = doc.get("elapsed")
        elapsed_net_blocked = doc.get("elapsed_net_blocked")
        if point_value in (None, 0) or elapsed is None or elapsed_net_blocked is None:
            fail(args.store, "incomplete-estimate-record:%s" % path)
        accuracy_ratios.append(elapsed_net_blocked / point_value)
        calibration_ratios.append(elapsed / point_value)

    emit({
        "store": args.store,
        "measure": "estimate_measures",
        "n": len(rows),
        "estimation_accuracy_ratio_avg": round(sum(accuracy_ratios) / len(accuracy_ratios), 4),
        "forecast_calibration_ratio_avg": round(sum(calibration_ratios) / len(calibration_ratios), 4),
    })
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
