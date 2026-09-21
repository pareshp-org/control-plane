#!/usr/bin/env python3
"""Advance the rolling restore rotation (Section 94.7).

Reads, as data and read-only:
  * the product registry, for each product's id and
    classification.reliability_criticality
  * the newest passing record per product under the restore-test record store

Computes days since each product's newest passing restore test and compares it
against that product's required window. The windows are the ones Section 44.2
and invariant 4 state literally: a 90-day floor for every product, tightened to
30 days where reliability_criticality is critical. No window is chosen here and
none is loosened (invariant 4).

Emits the next-due product id per line on stdout, most overdue first.
Exit codes: 0 computed; 1 fail-closed (missing input, unknown criticality).
"""
import datetime
import json
import os
import sys

import yaml

FLOOR_DAYS = 90        # invariant 4: the rolling 90-day floor for every product
CRITICAL_DAYS = 30     # Section 44.2: critical tightens to 30 days


def window_for(criticality):
    if criticality == "critical":
        return CRITICAL_DAYS
    if criticality in ("high", "medium", "low"):
        return FLOOR_DAYS
    raise ValueError("unknown reliability_criticality %r" % criticality)


def main():
    reg = os.environ.get("PRODUCT_REGISTRY_FILE", "")
    recs = os.environ.get("RESTORE_RECORD_DIR", "")
    if not reg or not os.path.isfile(reg):
        print("RESTORE-ROTATION: FAIL-CLOSED (PRODUCT_REGISTRY_FILE absent)")
        return 1
    if not recs or not os.path.isdir(recs):
        print("RESTORE-ROTATION: FAIL-CLOSED (RESTORE_RECORD_DIR absent)")
        return 1
    with open(reg, "r", encoding="utf-8") as fh:
        products = yaml.safe_load(fh) or {}
    rows = products.get("products", [])
    if not rows:
        print("RESTORE-ROTATION: FAIL-CLOSED (registry lists no products)")
        return 1
    newest = {}
    for name in os.listdir(recs):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(recs, name), "r", encoding="utf-8") as fh:
            rec = json.load(fh)
        if rec.get("result") != "pass":
            continue
        pid, when = rec.get("product"), rec.get("at", "")[:10]
        if not pid or not when:
            continue
        if pid not in newest or when > newest[pid]:
            newest[pid] = when
    today = datetime.date.today()
    due = []
    for row in rows:
        pid = row.get("id")
        try:
            win = window_for(row.get("classification", {}).get("reliability_criticality"))
        except ValueError as exc:
            print("RESTORE-ROTATION: FAIL-CLOSED (%s: %s)" % (pid, exc))
            return 1
        last = newest.get(pid)
        if last is None:
            due.append((10 ** 6, pid, "no-passing-record", win))
            continue
        age = (today - datetime.date.fromisoformat(last)).days
        if age >= win:
            due.append((age, pid, last, win))
    for age, pid, last, win in sorted(due, reverse=True):
        print("%s\tlast=%s\twindow=%dd\tage=%s" % (pid, last, win, age))
    print("RESTORE-ROTATION: %d due of %d products" % (len(due), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
