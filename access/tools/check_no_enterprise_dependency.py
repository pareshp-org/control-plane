#!/usr/bin/env python
"""Prove that nothing in access/** depends on a GitHub Enterprise-only feature.

Spec Section 99.6: "Plan-tier posture is settled (D73): branch protection on
private repositories requires the Team plan - non-negotiable, verified.
Environment required reviewers are Enterprise-only and are not depended on."

Four assertions:
  PT-A1  no row is both enterprise_only and enterprise_mechanism_depended_on
  PT-A2  the deployment-policies document declares required reviewers unused
  PT-A3  the deployment-policies document declares wait timers unused
  PT-A4  the environment payload renderer reports required_reviewers_used false
         for every environment -- executed, not asserted

Usage: check_no_enterprise_dependency.py [--config PATH]
Exit 0 on success, 1 on any failed assertion.
"""
import argparse
import json
import os
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT = os.path.join(ROOT, "access", "plan-tier", "plan-tier.yaml")
DEPLOY = os.path.join(ROOT, "access", "environments", "deployment-policies.yaml")
RENDER = os.path.join(ROOT, "access", "tools", "render_environment_payload.py")


def renders_without_reviewers():
    for environment in ("development", "staging", "production"):
        result = subprocess.run(
            [sys.executable, RENDER, "--environment", environment,
             "--default-branch", "main", "--release-tag-pattern", "v*"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            return False
        payload = json.loads(result.stdout.decode("utf-8"))
        if payload.get("required_reviewers_used") is not False:
            return False
        if "reviewers" in json.dumps(payload["environment_payload"]):
            return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT)
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)
    with open(DEPLOY, "r", encoding="utf-8") as handle:
        deploy = yaml.safe_load(handle)

    offenders = [row["id"] for row in doc["rows"]
                 if row["enterprise_only"] and row["enterprise_mechanism_depended_on"]]

    assertions = [
        ("PT-A1", "no row depends on an Enterprise-only mechanism", offenders == []),
        ("PT-A2", "environment required reviewers are declared unused",
         deploy["required_reviewers"]["used"] is False),
        ("PT-A3", "environment wait timers are declared unused",
         deploy["wait_timers"]["used"] is False),
        ("PT-A4", "the environment payload renderer depends on no reviewer feature",
         renders_without_reviewers()),
    ]

    failed = 0
    for ident, statement, ok in assertions:
        if not ok:
            print("FAIL %s: %s" % (ident, statement))
            failed += 1
    if offenders:
        print("       offending rows: %s" % ", ".join(offenders))
    if failed:
        print("PLAN-TIER: FAIL (%d of %d assertions)" % (failed, len(assertions)))
        return 1
    print("PLAN-TIER: PASS (%d assertions)" % len(assertions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
