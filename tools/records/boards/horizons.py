#!/usr/bin/env python3
"""BOARDS --horizons limb. Master Spec 29.2 lines 2641-2651."""
import sys, yaml

H1COLS = ["Planned", "In Progress", "In Review", "Verify"]
H3 = ["major features", "technical debt", "migrations", "architecture evolution",
      "customer requests", "security work", "integrations", "platform upgrades",
      "lifecycle decisions"]


def fail(msg):
    print("BOARDS FAIL horizons %s" % msg)
    sys.exit(1)


def main():
    try:
        d = yaml.safe_load(open("metrics/boards/horizons.yaml", encoding="utf-8"))
        b = yaml.safe_load(open("metrics/boards/board-conventions.yaml", encoding="utf-8"))
    except Exception as e:
        print("BOARDS ERROR horizons-input-unreadable:%s" % type(e).__name__)
        sys.exit(3)
    h = d.get("horizons") or {}
    if sorted(h) != ["H1", "H2", "H3"]:
        fail("not-exactly-three-horizons")
    if h["H1"].get("status") != "Committed" or h["H1"].get("owner") != "Developers":
        fail("H1-not-committed-to-developers")
    if h["H1"].get("contains_columns") != H1COLS:
        fail("H1-columns-not-the-in-flight-four")
    if h["H1"].get("contains_columns") != b.get("in_flight_columns"):
        fail("H1-columns-disagree-with-board-conventions")
    if h["H1"].get("contains_pipeline_stage") != "Deploy":
        fail("H1-omits-Deploy")
    if h["H1"].get("contains_blocked_flagged_items") is not True:
        fail("H1-omits-blocked-items")
    if h["H2"].get("status") != "Prepared" or h["H2"].get("committed") is not False:
        fail("H2-not-prepared-uncommitted")
    if h["H2"].get("owner") != "Team Lead" or h["H3"].get("owner") != "Team Lead":
        fail("H2-or-H3-not-owned-by-Team-Lead")
    if h["H3"].get("status") != "Candidate" or h["H3"].get("is_a_commitment") is not False:
        fail("H3-treated-as-a-commitment")
    if h["H3"].get("contains") != H3:
        fail("H3-content-list-not-the-nine-of-line-2647")
    u = d.get("unplanned_rule") or {}
    if u.get("is_a_flag") is not True or u.get("is_a_category") is not False:
        fail("unplanned-declared-as-a-category")
    if "without H2 preparation" not in (u.get("condition") or ""):
        fail("unplanned-condition-not-H2-preparation")
    f = d.get("founder_rule") or {}
    if f.get("rearranges_individual_developer_tasks") is not False:
        fail("founder-rearranges-developer-tasks")
    if "decision record" not in (f.get("priority_change_recording") or ""):
        fail("founder-priority-change-not-recorded-as-a-decision-record")
    print("BOARDS OK horizons=3 h1cols=4 h3items=9")
    return 0


if __name__ == "__main__":
    sys.exit(main())
