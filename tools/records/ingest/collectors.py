#!/usr/bin/env python3
"""INGEST --collectors limb. Master Spec 99.2 line 9196."""
import sys, yaml

NAMES = ["devlake", "prometheus", "scorecard"]


def fail(msg):
    print("INGEST FAIL collectors %s" % msg)
    sys.exit(1)


def main():
    try:
        d = yaml.safe_load(open("metrics/ingest/collectors.yaml", encoding="utf-8"))
    except Exception as e:
        print("INGEST ERROR collectors-unreadable:%s" % type(e).__name__)
        sys.exit(3)
    if d.get("closed_set") is not True:
        fail("collector-set-not-closed")
    c = d.get("collectors") or {}
    if sorted(c) != NAMES:
        fail("collectors-not-the-three-of-line-9196")
    if c["devlake"].get("cadence") != "nightly" or c["scorecard"].get("cadence") != "nightly":
        fail("nightly-cadence-missing")
    if c["devlake"].get("window_start_utc") != "04:00":
        fail("devlake-window-not-0400")
    if c["devlake"].get("window_complete_utc") != "06:00":
        fail("devlake-refresh-not-0600")
    if c["scorecard"].get("window_start_utc") != "02:00":
        fail("scorecard-scan-not-0200")
    if c["devlake"].get("coverage_confirmation_required") is not True:
        fail("devlake-coverage-confirmation-not-required")
    p = c["prometheus"]
    if p.get("scrape_interval_declared_by_l4") is not False:
        fail("l4-declares-a-scrape-interval-it-must-not-invent")
    if p.get("scrape_interval_owner_lane") != "L5":
        fail("scrape-interval-owner-not-L5")
    for n in NAMES:
        if c[n].get("installed_by_lane") != "L5" or c[n].get("installed_at_path") != "ops-vm/**":
            fail("collector-installation-not-routed-to-L5")
        if not (c[n].get("declaration_file") or "").startswith("metrics/ingest/"):
            fail("declaration-file-outside-metrics-ingest")
    if sorted(d.get("not_a_record_store") or []) != NAMES:
        fail("collectors-claimed-as-record-stores")
    if d.get("rendering_subsystem") != "H":
        fail("rendering-subsystem-not-H")
    if d.get("rendering_subsystem_lane") != "UNASSIGNED-D-L4-P5-03":
        fail("H-claimed-by-a-lane-without-L0")
    print("INGEST OK collectors=3 nightly=2 scrape=1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
