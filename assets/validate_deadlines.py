#!/usr/bin/env python3
"""Validator for the vendor deadline watch (Spec Section 49.2).

Rules, all mechanical:
  D1 deadline_id equals the filename stem and is [a-z0-9-]+
  D2 deadline_class is in the closed four-value set of Section 49.2
  D3 owner is non-empty and is not the literal "unassigned"
  D4 announced_deadline parses as ISO-8601 YYYY-MM-DD
  D5 alert_lead_days is an int >= 30       (Section 49.2 floor)
  D6 lead_time_rationale is present and non-empty when alert_lead_days > 30
  D7 alert_lead_days >= migration_effort_estimate_days
     (Section 49.2's worked example: the five-month alert exceeds the
      two-month rewrite; an alert that fires after the estimated work no
      longer fits is not an alert)
  D8 all fields present; pattern_class is the literal vendor-deprecation
  D9 owner resolves in the people registry when it exists
     (read-only consumption of an L1-owned registry, never edited here)
"""
import datetime
import os
import re
import sys

import yaml

CLASSES = {
    "api_sunset", "app_store_policy",
    "auth_mechanism_change", "vendor_contract_change",
}

REQUIRED = ["deadline_id", "deadline_class", "vendor", "owner", "product",
            "announced_deadline", "alert_lead_days", "lead_time_rationale",
            "migration_effort_estimate_days", "announcement_reference",
            "pattern_class", "spec_reference"]

ID_RE = re.compile(r"^[a-z0-9-]+$")
DEADLINES = os.path.join("assets", "deadlines")
PEOPLE_DIR = os.path.join("registries", "people")


def load_people():
    """Read-only consumption of the L1-owned people registry. Never edited here."""
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


def as_int(value):
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def check(path, known_people):
    errors = []
    stem = os.path.basename(path)[: -len(".yaml")]
    with open(path, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)
    if not isinstance(doc, dict):
        return ["D8 file is not a YAML mapping"]
    for field in REQUIRED:
        if field not in doc:
            errors.append("D8 missing field: %s" % field)
    if doc.get("deadline_id") != stem:
        errors.append("D1 deadline_id %r != filename stem %r"
                      % (doc.get("deadline_id"), stem))
    if not ID_RE.match(str(doc.get("deadline_id", ""))):
        errors.append("D1 deadline_id is not [a-z0-9-]+")
    if doc.get("deadline_class") not in CLASSES:
        errors.append("D2 deadline_class %r not in the closed set"
                      % doc.get("deadline_class"))
    owner = str(doc.get("owner", "")).strip()
    if not owner or owner == "unassigned":
        errors.append("D3 owner is empty or unassigned")
    if not str(doc.get("vendor", "")).strip():
        errors.append("D8 vendor is empty")
    if not str(doc.get("announcement_reference", "")).strip():
        errors.append("D8 announcement_reference is empty")
    try:
        datetime.date.fromisoformat(str(doc.get("announced_deadline")))
    except (TypeError, ValueError):
        errors.append("D4 announced_deadline %r is not ISO-8601 YYYY-MM-DD"
                      % doc.get("announced_deadline"))
    lead = as_int(doc.get("alert_lead_days"))
    if lead is None or lead < 30:
        errors.append("D5 alert_lead_days %r is not an integer >= 30"
                      % doc.get("alert_lead_days"))
    if lead is not None and lead > 30:
        if not str(doc.get("lead_time_rationale", "")).strip():
            errors.append("D6 alert_lead_days > 30 without a "
                          "lead_time_rationale")
    effort = as_int(doc.get("migration_effort_estimate_days"))
    if effort is None or effort < 0:
        errors.append("D7 migration_effort_estimate_days %r is not an "
                      "integer >= 0" % doc.get("migration_effort_estimate_days"))
    elif lead is not None and lead < effort:
        errors.append("D7 alert_lead_days %d is below the migration effort "
                      "estimate of %d days" % (lead, effort))
    if str(doc.get("pattern_class")) != "vendor-deprecation":
        errors.append("D8 pattern_class %r is not the literal "
                      "vendor-deprecation" % doc.get("pattern_class"))
    if known_people is not None and owner and owner not in known_people:
        errors.append("D9 owner %r does not resolve in %s"
                      % (owner, PEOPLE_DIR))
    return errors


def main():
    known = load_people()
    if known is None:
        print("OWNER-RESOLUTION: SKIPPED (%s absent)" % PEOPLE_DIR)
    else:
        print("OWNER-RESOLUTION: ACTIVE (%d people)" % len(known))
    if not os.path.isdir(DEADLINES):
        print("DEADLINE-VALIDATE: FAIL (%s absent)" % DEADLINES)
        return 1
    files = sorted(
        os.path.join(DEADLINES, name)
        for name in os.listdir(DEADLINES)
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
        print("DEADLINE-VALIDATE: FAIL (%d errors)" % total)
        return 1
    print("DEADLINE-VALIDATE: PASS (%d files)" % len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
