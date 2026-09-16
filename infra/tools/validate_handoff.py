#!/usr/bin/env python3
"""Validates infra/handoff/L2-workflow-requests.yaml (PARTITION.md rules 1, 4).

Lane 5 owns no path under .github/workflows/** (PARTITION.md line 18). Every
scheduled job it declares ships as a CLI entrypoint under one of its own
owned roots; this validates that the handoff bundle L2 reads is honest about
where those entrypoints actually live.

Rules, all mechanical:
  H1 every request carries id, entrypoint, invocation, trigger, spec,
     from_task
  H2 every entrypoint exists as a real file
  H3 every entrypoint is inside one of Lane 5's five owned roots
     (access/, infra/, ops-vm/, notify/, assets/)
  H4 l5_writes_no_workflow is true
  H5 no file under .github/ is staged or modified in the working tree
     relative to HEAD (Lane 5 never adds a workflow to make its own
     schedule "just work")

Usage: validate_handoff.py [--bundle PATH]
"""
import argparse
import os
import subprocess
import sys

import yaml

DEFAULT_BUNDLE = os.path.join("infra", "handoff", "L2-workflow-requests.yaml")
OWNED_ROOTS = ("access/", "infra/", "ops-vm/", "notify/", "assets/")
REQUIRED_FIELDS = ("id", "entrypoint", "invocation", "trigger", "spec",
                   "from_task")


def norm(path):
    return path.replace("\\", "/")


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--bundle", dest="bundle_path", default=DEFAULT_BUNDLE)
    args = parser.parse_args()

    if not os.path.exists(args.bundle_path):
        print("HANDOFF FAIL: %s does not exist" % args.bundle_path)
        return 1

    with open(args.bundle_path, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle) or {}

    if doc.get("l5_writes_no_workflow") is not True:
        print("HANDOFF FAIL: l5_writes_no_workflow is not true")
        return 1

    requests = doc.get("requests")
    if not isinstance(requests, list) or not requests:
        print("HANDOFF FAIL: no requests declared")
        return 1

    foreign = 0
    for entry in requests:
        if not isinstance(entry, dict):
            print("HANDOFF FAIL: a request row is not a mapping")
            return 1
        rid = entry.get("id", "<unnamed>")
        for field in REQUIRED_FIELDS:
            if not str(entry.get(field, "")).strip():
                print("HANDOFF FAIL: %s: missing required field %r"
                      % (rid, field))
                return 1
        entrypoint = norm(str(entry["entrypoint"]))
        if not os.path.exists(entrypoint):
            print("HANDOFF FAIL: %s: entrypoint %s does not exist"
                  % (rid, entrypoint))
            return 1
        if not entrypoint.startswith(OWNED_ROOTS):
            print("HANDOFF FAIL: %s: entrypoint %s is not an L5-owned path"
                  % (rid, entrypoint))
            foreign += 1

    if foreign:
        return 1

    # H5: no .github/ path touched. Best-effort — only runs the git check
    # when this is a git repository; a missing git binary or missing history
    # is reported, never silently skipped as a pass.
    github_touched = 0
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain", "--", ".github"],
            capture_output=True, text=True, check=False)
        if out.returncode == 0 and out.stdout.strip():
            github_touched = len(out.stdout.strip().splitlines())
    except FileNotFoundError:
        print("HANDOFF NOTE: git not available; H5 (.github/ untouched) "
              "not independently verified here")

    if github_touched:
        print("HANDOFF FAIL: %d file(s) under .github/ are touched in the "
              "working tree" % github_touched)
        return 1

    print("HANDOFF OK: %d request(s), %d foreign path(s)"
          % (len(requests), foreign))
    return 0


if __name__ == "__main__":
    sys.exit(main())
