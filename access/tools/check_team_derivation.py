#!/usr/bin/env python
"""Assert the Section 11.2 Teams model and its two anti-drift properties.

Six assertions:
  TD-1  all six Section 11.2 person classes are present, exactly once each
  TD-2  the background machine layer may not merge, holds no environment access,
        and never appears in CODEOWNERS
  TD-3  the Cross-Reviewer minimum permission is Write, and it agrees with
        access/model/permission-semantics.yaml rather than restating it
  TD-4  no repository name appears anywhere in the document (Section 11)
  TD-5  the Phase 1 grant is the interim assignment set replaced at Phase 3 (D101)
  TD-6  every Team shape grants Write, since a Team that grants nothing arms nothing

Usage: check_team_derivation.py [--config PATH] [--semantics PATH]
Exit 0 on success, 1 on any failed assertion.
"""
import argparse
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT = os.path.join(ROOT, "access", "model", "teams.yaml")
SEMANTICS = os.path.join(ROOT, "access", "model", "permission-semantics.yaml")

EXPECTED_CLASSES = [
    "founder",
    "team_lead_or_acting_team_lead",
    "qa",
    "developer",
    "contractor_or_temporary_specialist",
    "background_machine_layer",
]

# owner/repo, exactly two path segments -- the shape a repository name takes.
REPO_SHAPE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def walk_strings(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield str(key)
            for item in walk_strings(value):
                yield item
    elif isinstance(node, list):
        for value in node:
            for item in walk_strings(value):
                yield item
    elif isinstance(node, str):
        yield node


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT)
    parser.add_argument("--semantics", default=SEMANTICS)
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)
    with open(args.semantics, "r", encoding="utf-8") as handle:
        semantics = yaml.safe_load(handle)

    classes = [entry.get("id") for entry in doc.get("person_classes", [])]
    machine = {}
    for entry in doc.get("person_classes", []):
        if entry.get("id") == "background_machine_layer":
            machine = entry

    repo_shaped = sorted(set(
        text for text in walk_strings(doc)
        if REPO_SHAPE.match(text) and not text.endswith((".yaml", ".json", ".py", ".sh", ".md"))
    ))

    assertions = [
        ("TD-1", "all six Section 11.2 person classes present exactly once",
         classes == EXPECTED_CLASSES),
        ("TD-2", "the background machine layer may not merge, has no environment access "
                 "and never appears in CODEOWNERS",
         machine.get("may_merge") is False
         and machine.get("environment_access") == "none"
         and machine.get("never_appears_in_codeowners") is True),
        ("TD-3", "the Cross-Reviewer minimum permission is Write and agrees with Section 11.1",
         doc.get("cross_reviewer", {}).get("minimum_permission") == "write"
         and semantics.get("therefore", {}).get("cross_reviewer_minimum_permission") == "write"),
        ("TD-4", "no repository name appears in the document (Section 11)",
         repo_shaped == []),
        ("TD-5", "the Phase 1 grant is the interim assignment set, replaced at Phase 3 (D101)",
         doc.get("phase_1_interim", {}).get("assignment_set") == "interim"
         and doc.get("phase_1_interim", {}).get("decision") == "D101"),
        ("TD-6", "every Team shape grants Write",
         bool(doc.get("team_shapes"))
         and all(shape.get("grants") == "write" for shape in doc["team_shapes"])),
    ]

    failed = 0
    for ident, statement, ok in assertions:
        if not ok:
            print("FAIL %s: %s" % (ident, statement))
            failed += 1
    if repo_shaped and failed:
        print("       repository-shaped strings found: %s" % ", ".join(repo_shaped))
    if failed:
        print("TEAM-DERIVATION: FAIL (%d of %d assertions)" % (failed, len(assertions)))
        return 1
    print("TEAM-DERIVATION: PASS (%d assertions)" % len(assertions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
