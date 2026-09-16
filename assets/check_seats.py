#!/usr/bin/env python3
"""Seat-rule guard (Sections 39.1, 35.2, 35.6).

  S1 expiry_date equals renewal_date (the seat expires when it renews)
  S2 billing_cycle is monthly or annual
  S3 runtime is on the approved runtime list under access/ai-toolchain/runtimes/
     (skipped with a printed marker when that directory does not yet exist)
  S4 holder resolves in the people registry when present, and is not departed
"""
import os
import sys

import yaml

INVENTORY = os.path.join("assets", "inventory")
RUNTIMES = os.path.join("access", "ai-toolchain", "runtimes")
PEOPLE_DIR = os.path.join("registries", "people")


def approved_runtimes():
    if not os.path.isdir(RUNTIMES):
        return None
    return set(
        name[: -len(".yaml")]
        for name in os.listdir(RUNTIMES)
        if name.endswith(".yaml")
    )


def active_people():
    if not os.path.isdir(PEOPLE_DIR):
        return None
    out = set()
    for name in sorted(os.listdir(PEOPLE_DIR)):
        if not name.endswith(".yaml") or name.startswith("_"):
            continue
        with open(os.path.join(PEOPLE_DIR, name), "r",
                  encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        if not isinstance(doc, dict):
            continue
        status = str(doc.get("status") or doc.get("access_status") or
                     "active").lower()
        if status in ("departed", "revoked", "inactive"):
            continue
        pid = doc.get("id") or doc.get("github_login")
        if pid is not None:
            out.add(str(pid))
    return out


def main():
    runtimes = approved_runtimes()
    if runtimes is None:
        print("RUNTIME-CHECK: SKIPPED (%s absent)" % RUNTIMES)
    else:
        print("RUNTIME-CHECK: ACTIVE (%d approved runtimes)" % len(runtimes))
    people = active_people()
    if people is None:
        print("HOLDER-CHECK: SKIPPED (%s absent)" % PEOPLE_DIR)
    else:
        print("HOLDER-CHECK: ACTIVE (%d active people)" % len(people))
    errors = 0
    seats = 0
    if os.path.isdir(INVENTORY):
        for name in sorted(os.listdir(INVENTORY)):
            if not name.endswith(".yaml"):
                continue
            with open(os.path.join(INVENTORY, name), "r",
                      encoding="utf-8") as handle:
                doc = yaml.safe_load(handle) or {}
            if not isinstance(doc, dict) or \
                    doc.get("asset_class") != "ai_subscription_seat":
                continue
            seats += 1
            if str(doc.get("expiry_date")) != str(doc.get("renewal_date")):
                print("FAIL %s: S1 expiry_date != renewal_date" % name)
                errors += 1
            if doc.get("billing_cycle") not in ("monthly", "annual"):
                print("FAIL %s: S2 billing_cycle %r is not monthly|annual"
                      % (name, doc.get("billing_cycle")))
                errors += 1
            if runtimes is not None and str(doc.get("runtime")) not in runtimes:
                print("FAIL %s: S3 runtime %r is not on the approved list"
                      % (name, doc.get("runtime")))
                errors += 1
            if people is not None and str(doc.get("holder")) not in people:
                print("FAIL %s: S4 holder %r is not an active person"
                      % (name, doc.get("holder")))
                errors += 1
    print("SEAT-COUNT: %d" % seats)
    if errors:
        print("SEAT-CHECK: FAIL (%d errors)" % errors)
        return 1
    print("SEAT-CHECK: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
