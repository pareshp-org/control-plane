#!/usr/bin/env python3
"""Material requirement change - the re-plan decision. Master Spec 29.5 lines 2674-2703.

THIS MODULE DECIDES AND LINKS; IT DOES NOT WRITE RECORDS OR EVENTS. The Phase 4 writers
(record-write, event-append) perform the actual persisted write; this module reads a
requirement-change assessment, applies the line-2699 mandatory-trigger rules from
metrics/boards/replan-definition.yaml, and - when re-plan is mandatory - produces the
event payload that links to the item's *existing* estimate record and the Blocked-flag
directive (line 2701). It never fabricates an estimate-record path: a re-plan verdict
with no real, existing estimate record on disk is refused.
"""
import argparse
import json
import os
import sys

import yaml

DEFINITION = "metrics/boards/replan-definition.yaml"
EVENT_TYPE = "replan_triggered"
BLOCKED_REASON = "re-plan"
TRIGGER_KEYS = [
    "verification_path_changes",
    "impact_scope_widens",
    "reversibility_class_worsens",
    "change_becomes_architecture_class",
    "estimated_scope_growth_exceeds",
]


def err(reason):
    print("REPLAN ERROR %s" % reason)
    sys.exit(3)


def fail(reason):
    print("REPLAN FAIL %s" % reason)
    sys.exit(1)


def load_definition():
    try:
        d = yaml.safe_load(open(DEFINITION, encoding="utf-8"))
    except Exception:
        err("definition-unreadable")
    if sorted(d.get("mandatory_replan_triggers") or []) != sorted(TRIGGER_KEYS):
        err("trigger-set-drifted")
    if "estimated_scope_growth_threshold" not in d:
        err("threshold-missing")
    return d


def triggers_fired(assessment, defn):
    """Line 2699: verification path changes; impact scope widens; reversibility class
    worsens; the change becomes architecture-class; or estimated scope grows by more
    than the declared threshold. Every field is read, never inferred or defaulted true."""
    growth = assessment.get("estimated_scope_growth_ratio")
    return {
        "verification_path_changes": assessment.get("verification_path_changes") is True,
        "impact_scope_widens": assessment.get("impact_scope_widens") is True,
        "reversibility_class_worsens": assessment.get("reversibility_class_worsens") is True,
        "change_becomes_architecture_class": assessment.get(
            "change_becomes_architecture_class") is True,
        "estimated_scope_growth_exceeds": bool(
            growth is not None and growth > defn["estimated_scope_growth_threshold"]),
    }


def decide(assessment, defn):
    estimate_record = assessment.get("estimate_record")
    if not estimate_record:
        err("missing-estimate-record")
    if not os.path.isfile(estimate_record):
        fail("estimate-record-not-found:%s" % estimate_record)
    item = assessment.get("item")
    if not item:
        err("missing-item")

    fired = triggers_fired(assessment, defn)
    if any(fired.values()):
        on = defn["on_replan"]
        return {
            "verdict": "re_plan",
            "item": item,
            "product": assessment.get("product"),
            "fired_triggers": sorted(k for k, v in fired.items() if v),
            "event_type": on["event_type"],
            "estimate_record": estimate_record,
            "blocked_flag": {"set": True, "reason": on["blocked_flag"]["reason"]},
            "execution": on["execution"],
            "gate": defn["decision_gate"],
        }
    below = defn["below_threshold_action"]
    return {
        "verdict": "update_in_place",
        "item": item,
        "product": assessment.get("product"),
        "fired_triggers": [],
        "event_type": None,
        "estimate_record": estimate_record,
        "blocked_flag": {"set": False, "reason": None},
        "execution": "continue",
        "noted_in": below["noted_in"],
    }


def run(args):
    defn = load_definition()
    try:
        assessment = yaml.safe_load(open(args.input, encoding="utf-8")) or {}
    except FileNotFoundError:
        err("input-not-found:%s" % args.input)
    rec = decide(assessment, defn)
    print(json.dumps(rec, sort_keys=True))
    if rec["verdict"] == "re_plan":
        print("REPLAN OK re_plan item=%s linked=%s reason=%s" % (
            rec["item"], rec["estimate_record"], rec["blocked_flag"]["reason"]))
    else:
        print("REPLAN OK update_in_place item=%s" % rec["item"])
    return 0


def selftest():
    defn = load_definition()
    if defn.get("estimated_scope_growth_threshold") != 0.5:
        fail("threshold-drifted")
    on = defn.get("on_replan") or {}
    if on.get("event_type") != EVENT_TYPE:
        fail("event-type-drifted")
    if on.get("links_to") != "estimate_record":
        fail("linkage-target-drifted")
    bf = on.get("blocked_flag") or {}
    if bf.get("set") is not True or bf.get("reason") != BLOCKED_REASON:
        fail("blocked-flag-drifted")
    if on.get("execution") != "stopped":
        fail("execution-not-stopped")
    if len(defn.get("mandatory_replan_triggers") or []) != 5:
        fail("trigger-count-not-five")
    below = defn.get("below_threshold_action") or {}
    if below.get("update_in_place") is not True or below.get("gate_1_required") is not False:
        fail("below-threshold-action-drifted")
    print("BOARDS OK replan=1 triggers=5 threshold=0.5")
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--input")
    a = p.parse_args()
    if a.selftest:
        return selftest()
    if not a.input:
        err("no-input")
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
