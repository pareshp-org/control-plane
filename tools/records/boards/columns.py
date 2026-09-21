#!/usr/bin/env python3
"""BOARDS --columns limb. Master Spec 29.1 lines 2623-2639."""
import sys, yaml

FLOW = ["Backlog", "Ready", "Planned", "In Progress", "In Review", "Verify", "Done"]
INFLIGHT = ["Planned", "In Progress", "In Review", "Verify"]
VIEWS = ["current work", "ready work", "future work", "by owner", "by reviewer",
         "by product", "by priority", "by blocked state", "by lifecycle status",
         "by impact scope"]


def fail(msg):
    print("BOARDS FAIL columns %s" % msg)
    sys.exit(1)


def main():
    try:
        d = yaml.safe_load(open("metrics/boards/board-conventions.yaml", encoding="utf-8"))
    except Exception as e:
        print("BOARDS ERROR board-conventions-unreadable:%s" % type(e).__name__)
        sys.exit(3)
    if d.get("flow_columns") != FLOW:
        fail("flow-columns-not-the-seven-of-line-2628")
    if d.get("backlog_and_ready_are_distinct") is not True:
        fail("backlog-ready-collapsed")
    if d.get("in_flight_columns") != INFLIGHT:
        fail("in-flight-set-wrong")
    ns = d.get("non_column_states") or {}
    if set(ns) != {"Blocked", "Deploy"}:
        fail("non-column-states-not-exactly-Blocked-and-Deploy")
    b = ns["Blocked"]
    if b.get("kind") != "flag" or b.get("is_column") is not False:
        fail("Blocked-is-not-a-flag")
    if b.get("applies_to") != INFLIGHT:
        fail("Blocked-applies-to-wrong-columns")
    if b.get("surfaced_in_view") != "by blocked state":
        fail("Blocked-view-missing")
    dep = ns["Deploy"]
    if dep.get("is_column") is not False or dep.get("hand_moved") is not False:
        fail("Deploy-hand-moved-or-column")
    if dep.get("rendered_from") != "records/deployments/":
        fail("Deploy-not-rendered-from-deployment-records")
    for c in FLOW:
        if c in ns:
            fail("column-also-declared-a-non-column-state")
    t = d.get("board_topology") or {}
    pb, pf = t.get("product_board") or {}, t.get("portfolio_board") or {}
    if pb.get("cardinality") != "one-per-product" or pb.get("role") != "execution-truth":
        fail("product-board-not-execution-truth")
    if pf.get("role") != "aggregated-planning-and-capacity-view":
        fail("portfolio-board-claims-execution-truth")
    if pf.get("hand_maintained_duplicate_cards") is not False:
        fail("duplicate-cards-permitted")
    if pf.get("views") != VIEWS:
        fail("portfolio-views-not-the-ten-of-line-2634")
    if sorted(d.get("aggregation_modes") or {}) != ["aggregated", "single_project_fallback"]:
        fail("both-aggregation-modes-not-declared")
    if not d.get("selected_mode") or d.get("selected_mode").startswith("PENDING"):
        fail("selected-mode-not-answered")
    if d.get("aggregation_confirmed") is not False:
        fail("aggregation-claimed-confirmed-without-evidence")
    ex = (d.get("queue_of_record") or {}).get("excluded") or []
    if not any(e.get("id") == "background-worker-harness-internal-dispatch-queue"
               and e.get("never_execution_truth") is True for e in ex):
        fail("D70-carve-out-missing")
    print("BOARDS OK columns=7 inflight=4 nonstate=2 views=10 modes=2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
