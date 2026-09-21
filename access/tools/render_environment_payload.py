#!/usr/bin/env python
"""Render the GitHub environment payload and its deployment branch policies.

Turns access/environments/deployment-policies.yaml plus one environment name into
the literal bodies of:
  PUT  /repos/{owner}/{repo}/environments/{name}
  POST /repos/{owner}/{repo}/environments/{name}/deployment-branch-policies

It never emits a "reviewers" key and never emits a wait timer. Environment
required reviewers are Enterprise-only on private repositories and are not
depended on; production approval is the Section 27.2 workflow-identity gate (D73).

Usage:
  render_environment_payload.py --environment {development,staging,production}
                                --default-branch NAME
                                --release-tag-pattern PATTERN
                                [--config PATH]
Exit codes:
  0  JSON written to stdout
  3  bad arguments, unreadable configuration, or an unknown environment
"""
import argparse
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT = os.path.join(ROOT, "access", "environments", "deployment-policies.yaml")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", required=True)
    parser.add_argument("--default-branch", default="main")
    parser.add_argument("--release-tag-pattern", default="v*")
    parser.add_argument("--config", default=DEFAULT)
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)

    match = None
    for entry in doc["environments"]:
        if entry["name"] == args.environment:
            match = entry
    if match is None:
        sys.stderr.write("RENDER-ERROR unknown environment %r\n" % args.environment)
        return 3

    if match["restricted"]:
        environment_payload = {
            "deployment_branch_policy": {
                "protected_branches": False,
                "custom_branch_policies": True,
            }
        }
        policies = []
        for ref in match["accepted_refs"]:
            if ref["value"] == "the_repository_default_branch":
                policies.append({"name": args.default_branch, "type": "branch"})
            elif ref["value"] == "protected_release_tags":
                policies.append({"name": args.release_tag_pattern, "type": "tag"})
    else:
        environment_payload = {"deployment_branch_policy": None}
        policies = []

    out = {
        "environment": match["name"],
        "environment_payload": environment_payload,
        "deployment_branch_policies": policies,
        "required_reviewers_used": bool(doc["required_reviewers"]["used"]),
        "approval_mechanism": match.get("approval_mechanism", "not_applicable"),
    }
    sys.stdout.write(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
