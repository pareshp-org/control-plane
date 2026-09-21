#!/usr/bin/env python3
"""Publishes assets/published/expiry-watch.v1.json (Sections 49.1, 49.2, 92.6).

L5-00-charter.md Section 7.2 names this exact artifact as what Lane 3 needs:
"Every expiry date and its configurable lead time (>= 30 days). Feeds C's
expiry revocation cadence and the delegation-expiry warning of Section 10.1."
Section 7.3 names it for Lane 2 too, alongside notify/published/routing.v1.json.

This is the deadline-watch job's PUBLICATION half. The operational sweep that
runs on the ops VM, writes a human-readable report and Prometheus metrics, and
never pages anyone already exists at ops-vm/jobs/expiry_check.py (L5-04-11).
This script does not duplicate that sweep; it reads the same two source
directories -- assets/inventory/*.yaml (Section 49.1) and
assets/deadlines/*.yaml (Section 49.2) -- as data only, and emits the single
generated, never-hand-edited cross-lane artifact those sources are missing.

Wait surface only (Section 92.11): this script emits zero push events, always.

Usage: publish_expiry_watch.py [--as-of YYYY-MM-DD] [--check]

--check verifies an existing assets/published/expiry-watch.v1.json is exactly
what a fresh regeneration would produce (drift guard), and never writes.
"""
import argparse
import datetime
import json
import os
import sys

import yaml

INVENTORY = os.path.join("assets", "inventory")
DEADLINES = os.path.join("assets", "deadlines")
PUBLISHED = os.path.join("assets", "published", "expiry-watch.v1.json")


def load_dir(path):
    rows = []
    if not os.path.isdir(path):
        return rows
    for name in sorted(os.listdir(path)):
        if not name.endswith(".yaml"):
            continue
        with open(os.path.join(path, name), "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle)
        if isinstance(doc, dict):
            rows.append((name, doc))
    return rows


def watch_rows():
    """Static rows only: id, kind, owner, date, lead days. No run-time state."""
    rows = []
    for name, doc in load_dir(INVENTORY):
        rows.append({
            "id": str(doc.get("asset_id", name)),
            "kind": "asset",
            "sub_kind": str(doc.get("asset_class", "")),
            "owner": str(doc.get("owner", "")),
            "date": str(doc.get("expiry_date", "")),
            "lead_days": doc.get("alert_days"),
            "spec_reference": str(doc.get("spec_reference", "")),
        })
    for name, doc in load_dir(DEADLINES):
        rows.append({
            "id": str(doc.get("deadline_id", name)),
            "kind": "deadline",
            "sub_kind": str(doc.get("deadline_class", "")),
            "owner": str(doc.get("owner", "")),
            "date": str(doc.get("announced_deadline", "")),
            "lead_days": doc.get("alert_lead_days"),
            "spec_reference": str(doc.get("spec_reference", "")),
        })
    rows.sort(key=lambda r: (r["kind"], r["id"]))
    return rows


def render(rows):
    return {
        "artifact": "expiry-watch",
        "version": 1,
        "generated": "by assets/publish_expiry_watch.py; never hand-edited",
        "spec_reference": "49.1, 49.2, 92.6",
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--as-of", dest="as_of", default=None)
    parser.add_argument("--check", dest="check", action="store_true")
    args = parser.parse_args()

    if args.as_of:
        try:
            today = datetime.date.fromisoformat(args.as_of)
        except ValueError:
            print("EXPIRY-PUBLISH: BLOCKED (--as-of %r is not YYYY-MM-DD)"
                  % args.as_of)
            return 2
    else:
        today = datetime.datetime.now(datetime.timezone.utc).date()

    rows = watch_rows()
    assets = [r for r in rows if r["kind"] == "asset"]
    deadlines = [r for r in rows if r["kind"] == "deadline"]

    due, bad = 0, 0
    for row in rows:
        lead = row["lead_days"]
        if isinstance(lead, bool) or not isinstance(lead, int):
            print("BLOCKED %s: lead days %r is not an integer"
                  % (row["id"], lead))
            bad += 1
            continue
        try:
            when = datetime.date.fromisoformat(row["date"])
        except (TypeError, ValueError):
            print("BLOCKED %s: date %r is not YYYY-MM-DD"
                  % (row["id"], row["date"]))
            bad += 1
            continue
        remaining = (when - today).days
        if remaining <= lead:
            due += 1
            print("DUE %s %s owner=%s date=%s days_remaining=%d lead=%d"
                  % (row["kind"], row["id"], row["owner"], row["date"],
                     remaining, lead))

    if bad:
        print("EXPIRY-PUBLISH: FAIL (%d unreadable rows)" % bad)
        return 1

    payload = render(rows)

    if args.check:
        if not os.path.exists(PUBLISHED):
            print("EXPIRY-PUBLISH-CHECK: FAIL (%s does not exist)" % PUBLISHED)
            return 1
        with open(PUBLISHED, "r", encoding="utf-8") as handle:
            on_disk = json.load(handle)
        # "generated" carries no timestamp, so a byte-for-byte compare of the
        # meaningful fields is a legitimate drift guard, not a flaky one.
        on_disk_rows = on_disk.get("rows")
        if on_disk_rows != rows:
            print("EXPIRY-PUBLISH-CHECK: FAIL (published artifact does not "
                  "match a fresh regeneration)")
            return 1
        print("EXPIRY-PUBLISH-CHECK: PASS (%d rows)" % len(rows))
        return 0

    os.makedirs(os.path.dirname(PUBLISHED), exist_ok=True)
    with open(PUBLISHED, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("PUBLISHED: %s (%d rows)" % (PUBLISHED, len(rows)))
    print("EXPIRY-PUBLISH: %d assets, %d deadlines, %d due"
          % (len(assets), len(deadlines), due))
    print("SURFACE: wait-surface only - platform operations queue "
          "(Section 92.6)")
    print("PUSH-EVENTS-EMITTED: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
