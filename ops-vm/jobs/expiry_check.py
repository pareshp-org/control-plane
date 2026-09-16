#!/usr/bin/env python3
"""Daily expiry-and-deadline sweep on the operations VM (Section 94.7).

Reads the asset inventory and the deadline watch as data (never as source),
computes days-to-expiry per entry against the entry's own owner-set alert lead,
and writes a report plus Prometheus text. Wait surface only: this program never
sends a notification (Section 92.11).

Exit codes:
  0  sweep completed; entries within their alert lead are listed on the report
  1  sweep could not run (missing directory, unreadable or malformed entry)
"""
import datetime
import os
import sys

import yaml

FLOOR_DAYS = 30  # Section 49.1: "an alert threshold of at least 30 days"


def load(directory):
    out = []
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".yaml"):
            continue
        path = os.path.join(directory, name)
        with open(path, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle)
        if not isinstance(doc, dict):
            raise ValueError("%s is not a mapping" % path)
        out.append((path, doc))
    return out


def main():
    inv = os.environ.get("INVENTORY_DIR", "")
    dea = os.environ.get("DEADLINES_DIR", "")
    rep = os.environ.get("INVENTORY_REPORT_DIR", "")
    for key, value in (("INVENTORY_DIR", inv), ("DEADLINES_DIR", dea),
                       ("INVENTORY_REPORT_DIR", rep)):
        if not value:
            print("EXPIRY-SWEEP: FAIL-CLOSED (%s is empty)" % key)
            return 1
        if key != "INVENTORY_REPORT_DIR" and not os.path.isdir(value):
            print("EXPIRY-SWEEP: FAIL-CLOSED (%s is not a directory: %s)"
                  % (key, value))
            return 1
    os.makedirs(rep, exist_ok=True)
    today = datetime.date.today()
    rows, due, bad = [], 0, 0
    try:
        entries = load(inv) + load(dea)
    except Exception as exc:                      # malformed entry: fail closed
        print("EXPIRY-SWEEP: FAIL-CLOSED (%s)" % exc)
        return 1
    for path, doc in entries:
        aid = doc.get("asset_id") or doc.get("deadline_id") or path
        owner = doc.get("owner", "")
        raw = str(doc.get("expiry_date", doc.get("deadline_date", "")))
        lead = doc.get("alert_days", doc.get("alert_lead_days"))
        if not owner or owner == "unassigned":
            print("EXPIRY-SWEEP: FAIL-CLOSED (%s has no named owner)" % aid)
            bad += 1
            continue
        try:
            when = datetime.date.fromisoformat(raw)
        except ValueError:
            print("EXPIRY-SWEEP: FAIL-CLOSED (%s expiry %r is not ISO-8601)"
                  % (aid, raw))
            bad += 1
            continue
        try:
            lead = int(lead)
        except (TypeError, ValueError):
            print("EXPIRY-SWEEP: FAIL-CLOSED (%s has no integer alert lead)" % aid)
            bad += 1
            continue
        if lead < FLOOR_DAYS:
            print("EXPIRY-SWEEP: FAIL-CLOSED (%s alert lead %d is below the "
                  "Section 49.1 floor of %d)" % (aid, lead, FLOOR_DAYS))
            bad += 1
            continue
        days = (when - today).days
        rows.append((aid, owner, raw, lead, days))
        if days <= lead:
            due += 1
    if bad:
        print("EXPIRY-SWEEP: FAIL (%d unusable entries)" % bad)
        return 1
    stamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    with open(os.path.join(rep, "expiry-report.txt"), "w", encoding="utf-8") as fh:
        fh.write("# expiry sweep %s\n" % stamp)
        for aid, owner, raw, lead, days in rows:
            state = "DUE" if days <= lead else "ok"
            fh.write("%s\t%s\t%s\tlead=%d\tdays=%d\t%s\n"
                     % (aid, owner, raw, lead, days, state))
    with open(os.path.join(rep, "expiry.prom"), "w", encoding="utf-8") as fh:
        for aid, owner, raw, lead, days in rows:
            fh.write('ops_vm_asset_days_to_expiry{asset_id="%s",owner="%s"} %d\n'
                     % (aid, owner, days))
        fh.write("ops_vm_assets_within_alert_lead %d\n" % due)
    print("EXPIRY-SWEEP: PASS (%d entries, %d within alert lead)"
          % (len(rows), due))
    return 0


if __name__ == "__main__":
    sys.exit(main())
