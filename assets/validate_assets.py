#!/usr/bin/env python3
"""Validator for the operational asset inventory (Spec Section 49.1).

Rules, all mechanical:
  R1 asset_id equals the filename stem and is [a-z0-9-]+
  R2 asset_class is in the closed set
  R3 owner is non-empty and is not the literal "unassigned"
  R4 expiry_date parses as ISO-8601 YYYY-MM-DD
  R5 alert_days is an int >= 30            (Section 49.1: "at least 30 days")
  R6 all common fields present
  R7 class-conditional fields present
  R8 owner resolves in the people registry when it exists (read-only)

The people registry (registries/people/, L1-owned, PARTITION.md line 17) is
directory-per-item: one file per person under registries/people/<id>.yaml,
each carrying at minimum an `id` field. This validator reads it as data only
-- it is never imported as source and never edited here (boundary rule B-4).
The `_canary.yaml` drift sentinel (FD-106) is not a person and is excluded.
"""
import datetime
import os
import re
import sys

import yaml

CLASSES = {
    "machine_credential", "encryption_key", "host", "ci_runner",
    "ai_subscription_seat", "detection_leg", "certificate", "domain",
    "oauth_credential", "signing_certificate", "vendor_contract",
    "founder_account", "intake_channel",
}

COMMON = ["asset_id", "asset_class", "owner", "expiry_date",
          "alert_days", "cost_band", "spec_reference"]

CONDITIONAL = {
    "machine_credential": ["rotation_cadence", "rotator", "runbook",
                           "behavioural_envelope",
                           "envelope_alert_config_owner"],
    "encryption_key": ["holder", "rotation_cadence", "escrow_row",
                       "read_access_list"],
    "host": ["hostname", "machine_account", "owned_controls", "patch_cadence",
             "site", "power", "network"],
    "ci_runner": ["hostname", "patch_cadence", "site", "power", "network",
                  "runner_group", "on_operations_vm"],
    "ai_subscription_seat": ["vendor", "runtime", "holder", "renewal_date",
                             "billing_cycle", "tier"],
    "detection_leg": ["mechanism", "runs_off_operations_vm", "routes_to"],
}

ID_RE = re.compile(r"^[a-z0-9-]+$")
INVENTORY = os.path.join("assets", "inventory")
PEOPLE_DIR = os.path.join("registries", "people")


def load_people():
    """Read-only consumption of the L1-owned people registry.

    registries/people/ is directory-per-item (PARTITION.md rule 3): one file
    per person, named <id>.yaml. Never edited here.
    """
    if not os.path.isdir(PEOPLE_DIR):
        return None
    known = set()
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
            known.add(str(pid))
    return known


def check(path, known_people):
    errors = []
    stem = os.path.basename(path)[: -len(".yaml")]
    with open(path, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)
    if not isinstance(doc, dict):
        return ["R6 file is not a YAML mapping"]
    for field in COMMON:
        if field not in doc:
            errors.append("R6 missing common field: %s" % field)
    if doc.get("asset_id") != stem:
        errors.append("R1 asset_id %r != filename stem %r"
                      % (doc.get("asset_id"), stem))
    if not ID_RE.match(str(doc.get("asset_id", ""))):
        errors.append("R1 asset_id is not [a-z0-9-]+")
    klass = doc.get("asset_class")
    if klass not in CLASSES:
        errors.append("R2 asset_class %r not in the closed set" % klass)
    owner = str(doc.get("owner", "")).strip()
    if not owner or owner == "unassigned":
        errors.append("R3 owner is empty or unassigned")
    try:
        datetime.date.fromisoformat(str(doc.get("expiry_date")))
    except (TypeError, ValueError):
        errors.append("R4 expiry_date %r is not ISO-8601 YYYY-MM-DD"
                      % doc.get("expiry_date"))
    alert = doc.get("alert_days")
    if isinstance(alert, bool) or not isinstance(alert, int) or alert < 30:
        errors.append("R5 alert_days %r is not an integer >= 30" % alert)
    for field in CONDITIONAL.get(klass, []):
        if field not in doc:
            errors.append("R7 asset_class %s missing field: %s"
                          % (klass, field))
    if known_people is not None and owner and owner not in known_people:
        errors.append("R8 owner %r does not resolve in %s"
                      % (owner, PEOPLE_DIR))
    return errors


def main():
    known = load_people()
    if known is None:
        print("OWNER-RESOLUTION: SKIPPED (%s absent)" % PEOPLE_DIR)
    else:
        print("OWNER-RESOLUTION: ACTIVE (%d people)" % len(known))
    if not os.path.isdir(INVENTORY):
        print("ASSET-VALIDATE: FAIL (%s absent)" % INVENTORY)
        return 1
    files = sorted(
        os.path.join(INVENTORY, name)
        for name in os.listdir(INVENTORY)
        if name.endswith(".yaml")
    )
    total = 0
    for path in files:
        errors = check(path, known)
        if errors:
            total += len(errors)
            for err in errors:
                print("FAIL %s: %s" % (path, err))
        else:
            print("OK %s" % path)
    if total:
        print("ASSET-VALIDATE: FAIL (%d errors)" % total)
        return 1
    print("ASSET-VALIDATE: PASS (%d files)" % len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
