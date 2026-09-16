#!/usr/bin/env python
"""Render the literal GitHub branch-protection API payload for one profile.

Published interface (plan file section 0.3). Consumed by L3 provisioning and by
access/runbooks/apply-branch-protection.sh. It never talks to GitHub: it turns
access/branch-protection/branch-protection.yaml plus a profile name into the JSON
body of PUT /repos/{owner}/{repo}/branches/{branch}/protection.

The required-status-check context list starts EMPTY (Section 98.2). Contexts are
supplied explicitly with --contexts and must be drawn from the declared
catalogue: a context no workflow emits blocks every pull request indefinitely.

Usage:
  render_protection_payload.py --profile {unarmed,armed} [--contexts a,b]
                               [--config PATH]
Exit codes:
  0  payload written to stdout as JSON
  3  bad arguments or unreadable configuration
  4  a requested context is not in the declared catalogue
"""
import argparse
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT = os.path.join(ROOT, "access", "branch-protection", "branch-protection.yaml")


def row(doc, ident):
    for entry in doc["checklist"]:
        if entry["id"] == ident:
            return entry
    sys.stderr.write("RENDER-ERROR checklist row %s missing\n" % ident)
    sys.exit(3)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=["unarmed", "armed"], required=True)
    parser.add_argument("--contexts", default="")
    parser.add_argument("--config", default=DEFAULT)
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)

    catalogue = [entry["context"] for entry in doc["required_status_checks"]["catalogue"]]
    requested = [item.strip() for item in args.contexts.split(",") if item.strip()]
    unknown = [item for item in requested if item not in catalogue]
    if unknown:
        sys.stderr.write("RENDER-ERROR context not in the declared catalogue: %s\n"
                         % ", ".join(unknown))
        return 4

    profile = args.profile
    payload = {
        "required_status_checks": {
            "strict": bool(doc["required_status_checks"]["strict"]),
            "contexts": requested,
        },
        "enforce_admins": bool(row(doc, "BP-09")[profile]),
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": bool(row(doc, "BP-05")[profile]),
            "require_code_owner_reviews": bool(row(doc, "BP-03")[profile]),
            "required_approving_review_count": int(row(doc, "BP-02")[profile]),
            "require_last_push_approval": bool(row(doc, "BP-04")[profile]),
        },
        "restrictions": None,
        "allow_force_pushes": not bool(row(doc, "BP-08")[profile]),
        "allow_deletions": not bool(row(doc, "BP-08")[profile]),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
