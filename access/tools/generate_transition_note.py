#!/usr/bin/env python
"""Render the per-repository transition note of spec Section 95.4.

"The note is the difference between a team that experiences governance arriving
 and a team that experiences its merges mysteriously breaking."

Two rules are enforced in code rather than trusted:

  1. Where the review routing does not yet exist, the note SAYS SO and names the
     date Phase 3 populates the assignment registries. It never publishes a
     routing nothing can resolve. Claiming an available routing while the
     routing fields are empty is refused (exit 3).
  2. The same-day response commitment runs for exactly the two weeks after
     branch protection lands (Section 95.4). A window that is not 14 days is
     refused (exit 3).

Usage: generate_transition_note.py --input INPUT.json [--template PATH]
Exit codes: 0 note on stdout | 3 input refused
"""
import argparse
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
TEMPLATE = os.path.join(ROOT, "access", "runbooks", "transition-note.template.md")

APPROVAL = {
    "unarmed": ("A review is requested automatically from the Code Owners. "
                "No approving review is required to merge yet; that arms later."),
    "armed": ("One approving review is required, it must come from a Code Owner, "
              "and it must approve the most recent reviewable push. "
              "A review from an account holding only Read does not count."),
}


def refuse(reason):
    sys.stderr.write("TRANSITION-NOTE-REFUSED %s\n" % reason)
    sys.exit(3)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--template", default=TEMPLATE)
    args = parser.parse_args()

    if not os.path.exists(args.input):
        refuse("input document not found: %s" % args.input)
    with open(args.input, "r", encoding="utf-8") as handle:
        try:
            doc = json.load(handle)
        except ValueError as exc:
            refuse("input document is not valid JSON: %s" % exc)

    try:
        lands = datetime.date(*[int(part) for part in doc["protection_lands_on"].split("-")])
        until = datetime.date(*[int(part) for part in doc["same_day_response_until"].split("-")])
    except (KeyError, TypeError, ValueError):
        refuse("protection_lands_on and same_day_response_until must both be YYYY-MM-DD")
    if (until - lands).days != 14:
        refuse("the same-day response commitment must run exactly 14 days from "
               "protection_lands_on (Section 95.4); got %d" % (until - lands).days)

    routing = doc["review_routing"]
    if routing["available"]:
        if not routing.get("primary_owner") or not routing.get("cross_reviewer"):
            refuse("review_routing.available is true but the routing is empty. "
                   "Section 95.4: never publish a routing nothing can resolve.")
        routing_section = (
            "- Primary Owner: %s\n- Cross-Reviewer: %s\n\n"
            "A Cross-Reviewer holds Write on this repository. That is not a "
            "privilege escalation: an approval from an account holding only Read "
            "does not satisfy branch protection, so a Read-only cross-review "
            "leaves the merge blocked."
            % (routing["primary_owner"], routing["cross_reviewer"])
        )
    else:
        routing_section = (
            "**The review routing for this repository does not exist yet.** The "
            "assignment registries are populated at Phase 3, on %s. Until then, "
            "review requests route to the Code Owners generated from the interim "
            "assignment set, and this note deliberately publishes no routing "
            "table rather than one nothing can resolve."
            % routing["populated_on"]
        )

    with open(args.template, "r", encoding="utf-8") as handle:
        text = handle.read()

    replacements = [
        ("{{PRODUCT_ID}}", doc["product_id"]),
        ("{{PROFILE}}", doc["profile"]),
        ("{{PROTECTION_LANDS_ON}}", doc["protection_lands_on"]),
        ("{{SAME_DAY_RESPONSE_UNTIL}}", doc["same_day_response_until"]),
        ("{{ASK_WHEN_BLOCKED}}", doc["ask_when_blocked"]),
        ("{{APPROVAL_SENTENCE}}", APPROVAL[doc["profile"]]),
        ("{{ROUTING_SECTION}}", routing_section),
        ("{{NEXT_GATE_SENTENCE}}",
         "Gate %s arms at %s. Effect: %s."
         % (doc["next_gate"]["id"], doc["next_gate"]["arms_at"],
            doc["next_gate"]["effect"])),
    ]
    for token, value in replacements:
        text = text.replace(token, value)

    if "{{" in text:
        refuse("an unfilled template token remains: a note with a placeholder is "
               "not a note")

    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
