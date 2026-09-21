#!/usr/bin/env python3
"""BOARDS --ready limb. Master Spec 29.3 lines 2653-2666."""
import sys, yaml

IDS = ["clear_requirement", "product_identified", "priority", "intended_person",
       "verification_path", "dependencies_understood",
       "architecture_decisions_resolved", "impact_scope_proposed",
       "acceptance_criteria", "enough_context_to_begin"]
PIPE = ["Idea", "Defined", "Verification understood", "Architecture resolved",
        "Ready", "Assigned", "Executed"]
EXEMPT = ["spike", "incident", "debt-remediation"]


def fail(msg):
    print("BOARDS FAIL ready %s" % msg)
    sys.exit(1)


def main():
    try:
        d = yaml.safe_load(open("metrics/boards/ready-definition.yaml", encoding="utf-8"))
    except Exception as e:
        print("BOARDS ERROR ready-definition-unreadable:%s" % type(e).__name__)
        sys.exit(3)
    if d.get("conjunction") != "all":
        fail("conjunction-not-all")
    c = d.get("criteria") or []
    if [x.get("id") for x in c] != IDS:
        fail("criteria-not-the-ten-of-line-2655")
    for x in c:
        if not (x.get("text") or "").strip():
            fail("criterion-has-no-text")
    if d.get("pipeline") != PIPE:
        fail("pipeline-not-the-seven-of-lines-2658-2659")
    pt = d.get("planning_target") or {}
    if pt.get("ready_items_per_developer") != 2:
        fail("planning-target-not-two")
    if pt.get("is_absolute_invariant") is not False:
        fail("planning-target-declared-an-invariant")
    hr = d.get("hard_requirement") or {}
    if "trend to zero" not in (hr.get("statement") or ""):
        fail("hard-requirement-not-trend-to-zero")
    if hr.get("artificial_fragmentation_permitted") is not False:
        fail("artificial-fragmentation-permitted")
    rd = d.get("ready_draft_delegation") or {}
    if rd.get("drafting_permitted_by") != "Primary Owner":
        fail("ready-draft-delegation-wrong-drafter")
    if rd.get("ready_transition_authority") != "Team Lead":
        fail("ready-authority-not-retained-by-Team-Lead")
    if rd.get("authority_delegated") is not False:
        fail("ready-authority-delegated")
    ec = d.get("estimate_capture") or {}
    if ec.get("capture_point") != "ready_confirmation":
        fail("estimate-capture-point-not-ready-confirmation")
    if ec.get("applies_to") != "normal_planned_work":
        fail("estimate-capture-not-limited-to-normal-planned-work")
    if ec.get("estimate_exempt_classes") != EXEMPT:
        fail("exempt-classes-not-the-three-of-line-2665")
    if ec.get("item_class_inferred") is not False:
        fail("item-class-inference-permitted")
    if ec.get("band_vocabulary_home") != "registries/economics.yaml":
        fail("band-vocabulary-not-in-economics-yaml")
    if ec.get("hours_precise") is not False:
        fail("hours-precise-estimates-permitted")
    print("BOARDS OK ready=10 pipeline=7 exempt=3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
