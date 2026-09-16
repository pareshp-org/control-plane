#!/usr/bin/env python3
"""Runner-estate guard (Sections 49.1, 46; D80, D87).

  E1 no ci_runner entry sits on the operations VM
  E2 every ci_runner entry declares site, power and network
  E3 every ci_runner entry names a runner_group declared under infra/runners/groups/
  E4 the roster count is printed, never implied
"""
import os
import sys

import yaml

INVENTORY = os.path.join("assets", "inventory")
GROUPS = os.path.join("infra", "runners", "groups")


def main():
    groups = set()
    if os.path.isdir(GROUPS):
        for name in os.listdir(GROUPS):
            if name.endswith(".yaml"):
                with open(os.path.join(GROUPS, name), "r",
                          encoding="utf-8") as handle:
                    doc = yaml.safe_load(handle) or {}
                if doc.get("group"):
                    groups.add(str(doc["group"]))
    errors = 0
    count = 0
    if not os.path.isdir(INVENTORY):
        print("RUNNER-GROUPS: %d declared (%s)"
              % (len(groups), ", ".join(sorted(groups)) or "none"))
        print("RUNNER-ESTATE: 0 hosts declared")
        print("RUNNER-CHECK: PASS")
        return 0
    for name in sorted(os.listdir(INVENTORY)):
        if not name.endswith(".yaml"):
            continue
        with open(os.path.join(INVENTORY, name), "r",
                  encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        if doc.get("asset_class") != "ci_runner":
            continue
        count += 1
        if doc.get("on_operations_vm") is not False:
            print("FAIL %s: E1 runner declared on the operations VM" % name)
            errors += 1
        for field in ("site", "power", "network"):
            if not str(doc.get(field, "")).strip():
                print("FAIL %s: E2 missing %s dependency" % (name, field))
                errors += 1
        if str(doc.get("runner_group", "")) not in groups:
            print("FAIL %s: E3 runner_group %r not declared under %s"
                  % (name, doc.get("runner_group"), GROUPS))
            errors += 1
    print("RUNNER-GROUPS: %d declared (%s)"
          % (len(groups), ", ".join(sorted(groups)) or "none"))
    print("RUNNER-ESTATE: %d hosts declared" % count)
    if errors:
        print("RUNNER-CHECK: FAIL (%d errors)" % errors)
        return 1
    print("RUNNER-CHECK: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
