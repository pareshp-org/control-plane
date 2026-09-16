#!/usr/bin/env python3
"""INGEST --scorecard limb. Master Spec 99.2 line 9196; 92.3 line 8300."""
import sys
import yaml

PATH = "metrics/ingest/scorecard.yaml"
CONDITIONS = ["below_minimum", "decrease"]
ARRIVES = ["decision_prompt", "owned_line_on_reliability_dimension"]
UNARMED = "unarmed — not yet instrumented"   # 52.2 line 4524


def fail(msg):
    print("INGEST FAIL scorecard %s" % msg)
    sys.exit(1)


def main():
    try:
        d = yaml.safe_load(open(PATH, encoding="utf-8"))
        col = yaml.safe_load(open("metrics/ingest/collectors.yaml",
                                  encoding="utf-8"))["collectors"]["scorecard"]
    except Exception as e:
        print("INGEST ERROR scorecard-unreadable:%s" % type(e).__name__)
        sys.exit(3)

    if d.get("cadence") != col.get("cadence"):
        fail("cadence-diverges-from-collectors-yaml")
    if d.get("window_start_utc") != col.get("window_start_utc"):
        fail("scan-window-diverges-from-collectors-yaml")
    if d.get("produces") != "Risk score per product":
        fail("produces-not-the-line-8395-string")

    if d.get("source_kind") != "collector":
        fail("scorecard-claimed-as-record-store")
    if d.get("is_source_of_truth") is not False:
        fail("collector-claimed-as-source-of-truth")
    if d.get("source_store") != "PENDING-D-L4-P5-01":
        fail("source-store-bound-without-L0")

    cond = d.get("drop_conditions") or []
    if sorted(c.get("name") for c in cond) != CONDITIONS:
        fail("drop-conditions-not-decrease-and-below-minimum")
    for c in cond:
        if not c.get("definition") or not c.get("spec_line"):
            fail("drop-condition-without-definition-or-anchor:%s" % c.get("name"))
    if not d.get("routing_threshold") or d.get("routing_threshold").startswith("PENDING"):
        fail("routing-threshold-not-answered")

    r = d.get("routing") or {}
    if r.get("never") != "browse_raw_scores":
        fail("raw-score-browsing-not-forbidden")
    if sorted(r.get("arrives_as") or []) != ARRIVES:
        fail("routing-not-the-two-forms-of-line-8300")
    if sorted(r.get("line_names") or []) != ["drop", "owner_already_acting", "product"]:
        fail("owned-line-does-not-name-product-drop-and-owner")

    if d.get("floor_key") != "security.scorecard_minimum":
        fail("floor-key-renamed")
    if d.get("floor_value_declared_by_l4") is not False:
        fail("l4-declares-a-scorecard-minimum-that-is-l1s")

    if d.get("private_repo_behaviour_confirmed") is not False:
        fail("private-repo-behaviour-confirmed-without-assisted-evidence")
    if d.get("evidence_authored_by_lane_4") is not False:
        fail("lane-4-claims-authorship-of-assisted-evidence")
    if d.get("arming_state") != UNARMED:
        fail("arming-string-not-frozen-vocabulary")

    print("INGEST OK scorecard conditions=2 pending=2 arming=unarmed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
