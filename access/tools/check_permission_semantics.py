#!/usr/bin/env python
"""Assert the seven load-bearing facts of spec Section 11.1.

The table in access/model/permission-semantics.yaml is transcribed from
the specification. These assertions exist so that an edit which "simplifies" it
fails a check rather than failing silently in production, where the symptom is a
gate that appears to be working and is not.

Usage: check_permission_semantics.py [--config PATH]
Exit 0 on success, 1 on any failed assertion.
"""
import argparse
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT = os.path.join(ROOT, "access", "model", "permission-semantics.yaml")


def cap(doc, cap_id):
    for entry in doc.get("capabilities", []):
        if entry.get("id") == cap_id:
            return entry.get("by_level", {})
    return {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT)
    args = parser.parse_args()
    with open(args.config, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)

    review = cap(doc, "submit_a_review")
    counts = cap(doc, "approval_counts_toward_required_approving_reviews")
    push = cap(doc, "push_branches_to_the_repository")
    therefore = doc.get("therefore", {})

    assertions = [
        ("PS-1", "a Read holder can submit a review",
         review.get("read") is True),
        ("PS-2", "a Read holder's approval does NOT count toward required approving reviews",
         counts.get("read") is False),
        ("PS-3", "a Triage holder's approval does NOT count either",
         counts.get("triage") is False),
        ("PS-4", "a Write holder's approval DOES count",
         counts.get("write") is True),
        ("PS-5", "Read cannot push branches and Write can",
         push.get("read") is False and push.get("write") is True),
        ("PS-6", "the Cross-Reviewer minimum permission is Write",
         therefore.get("cross_reviewer_minimum_permission") == "write"),
        ("PS-7", "least privilege is preserved by branch protection, not by withholding Write",
         therefore.get("least_privilege_preserved_by") == "branch_protection"
         and therefore.get("least_privilege_not_preserved_by") == "withholding_write"),
    ]

    failed = 0
    for ident, statement, ok in assertions:
        if not ok:
            print("FAIL %s: %s" % (ident, statement))
            failed += 1
    if failed:
        print("PERMISSION-SEMANTICS: FAIL (%d of %d assertions)" % (failed, len(assertions)))
        return 1
    print("PERMISSION-SEMANTICS: PASS (%d assertions)" % len(assertions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
