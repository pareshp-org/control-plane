#!/usr/bin/env python3
"""Validates the Lane 5 invariant-classification map (Spec Section 101 preamble).

Section 101's preamble is the rule this mechanises: every invariant is
EXACTLY ONE of
  mechanical   -- names the CI check, branch-protection rule, reconciliation
                  row or AT- identifier that enforces it
  policy       -- names the policies.yaml entry carrying its owner, review
                  date and enforcement mechanism
  review-held  -- names the standing review that reads it and the role that
                  chairs it

Rules, all mechanical:
  M1 every entry carries `classification`, exactly one of the three values
  M2 a `mechanical` entry's `enforcer` resolves: every ';'-separated
     reference is either a repository file path that exists, or an AT-*
     identifier present in access/tests/coverage.yaml
  M3 a `policy` entry is refused: policies.yaml is not a Lane 5 path
     (registries/policies/** is L1's; this lane owns no policies.yaml)
  M4 invariant numbers are unique and lie in 1..111 (Section 101's own range)

Usage: validate_invariant_map.py [--map PATH]
"""
import argparse
import os
import sys

import yaml

DEFAULT_MAP = os.path.join("access", "invariants", "l5-invariant-map.yaml")
COVERAGE = os.path.join("access", "tests", "coverage.yaml")

CLASSIFICATIONS = {"mechanical", "policy", "review-held"}


def load_at_ids():
    if not os.path.exists(COVERAGE):
        return set()
    with open(COVERAGE, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle) or {}
    return {str(row.get("check_id")) for row in doc.get("checks", [])
            if row.get("check_id")}


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--map", dest="map_path", default=DEFAULT_MAP)
    args = parser.parse_args()

    if not os.path.exists(args.map_path):
        print("INVARIANT MAP FAIL: %s does not exist" % args.map_path)
        return 1

    with open(args.map_path, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle) or {}

    invariants = doc.get("invariants")
    if not isinstance(invariants, list) or not invariants:
        print("INVARIANT MAP FAIL: no invariants declared")
        return 1

    at_ids = load_at_ids()
    seen_numbers = set()
    mechanical_count = 0
    unresolved = 0

    for entry in invariants:
        if not isinstance(entry, dict):
            print("INVARIANT MAP FAIL: a row is not a mapping")
            return 1
        number = entry.get("number")
        if not isinstance(number, int) or isinstance(number, bool):
            print("INVARIANT MAP FAIL: a row's number %r is not an integer"
                  % number)
            return 1
        if not (1 <= number <= 111):
            print("INVARIANT MAP FAIL: %s: number is out of Section 101's "
                  "1..111 range" % number)
            return 1
        if number in seen_numbers:
            print("INVARIANT MAP FAIL: %s: invariant number appears more "
                  "than once" % number)
            return 1
        seen_numbers.add(number)

        classification = entry.get("classification")
        if classification not in CLASSIFICATIONS:
            print("INVARIANT MAP FAIL: %s: classification %r is not one of "
                  "%s" % (number, classification, sorted(CLASSIFICATIONS)))
            return 1

        if classification == "policy":
            print("INVARIANT MAP FAIL: %s: policy classification is L0's, "
                  "not lane 5's" % number)
            return 1

        if classification == "review-held":
            # Not built by any Lane 5 task today; still requires a named
            # review and chair, checked the same way a mechanical enforcer
            # is checked for presence, just not for file existence.
            if not str(entry.get("enforcer", "")).strip():
                print("INVARIANT MAP FAIL: %s: review-held entry names no "
                      "standing review" % number)
                return 1
            continue

        # classification == "mechanical"
        mechanical_count += 1
        enforcer = str(entry.get("enforcer", "")).strip()
        if not enforcer:
            print("INVARIANT MAP FAIL: %s: mechanical entry names no "
                  "enforcer" % number)
            return 1
        refs = [r.strip() for r in enforcer.split(";") if r.strip()]
        if not refs:
            print("INVARIANT MAP FAIL: %s: enforcer resolves to no "
                  "references" % number)
            return 1
        for ref in refs:
            if ref.startswith("AT-") or ref.startswith("NC-"):
                if ref not in at_ids:
                    print("INVARIANT MAP FAIL: %s: enforcer %s does not "
                          "resolve (not in %s)" % (number, ref, COVERAGE))
                    unresolved += 1
                continue
            if not os.path.exists(ref):
                print("INVARIANT MAP FAIL: %s: enforcer %s does not "
                      "resolve" % (number, ref))
                unresolved += 1

    if unresolved:
        return 1

    print("INVARIANT MAP OK: %d invariants, %d mechanical, %d unresolved"
          % (len(invariants), mechanical_count, unresolved))
    return 0


if __name__ == "__main__":
    sys.exit(main())
