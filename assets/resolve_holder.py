#!/usr/bin/env python3
"""Resolve a selector to exactly one person id. Read-only over registries/.

Usage: resolve_holder.py capability:devops
       resolve_holder.py role:founder

Prints one of:
  RESOLVE: <person-id>
  RESOLVE: NONE (<reason>)
  RESOLVE: AMBIGUOUS (<n> holders: a, b, ...)
Exit 0 only on a single resolution.

Resolution order:
  1. Direct match against a person's `capabilities` list (for
     capability:<x>) or `role`/`roles` (for role:<x>), read from
     registries/people/<id>.yaml (directory-per-item, L1-owned).
  2. If nothing matches directly, fall back to an *active* single-owner
     bootstrap exception: registries/policies/lane-ownership.yaml records
     that, in bootstrap, one person holds every lane seat, under an
     exception recorded in registries/exceptions/. Holding every lane seat
     subsumes every narrower capability and role, so during an active,
     unexpired bootstrap exception every selector resolves to that one
     person -- this is read from real registry data, never invented. Once
     real per-person capability data exists and a query matches directly,
     step 1 takes over and this fallback stops mattering.

This program chooses nothing itself: an absent, ambiguous, expired or
malformed exception is NONE, never a guess.
"""
import datetime
import os
import sys

import yaml

PEOPLE_DIR = os.path.join("registries", "people")
POLICIES_DIR = os.path.join("registries", "policies")
EXCEPTIONS_DIR = os.path.join("registries", "exceptions")


def load_people():
    people = {}
    if not os.path.isdir(PEOPLE_DIR):
        return people
    for name in sorted(os.listdir(PEOPLE_DIR)):
        if not name.endswith(".yaml") or name.startswith("_"):
            continue
        with open(os.path.join(PEOPLE_DIR, name), "r",
                  encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        if isinstance(doc, dict) and doc.get("id"):
            people[str(doc["id"])] = doc
    return people


def direct_hits(kind, value, people):
    hits = []
    for pid, body in people.items():
        status = str(body.get("status") or body.get("access_status") or
                     "active").lower()
        if status in ("departed", "revoked", "inactive"):
            continue
        if kind == "capability":
            pool = list(body.get("capabilities") or [])
        elif kind == "role":
            pool = list(body.get("roles") or [])
            if body.get("role"):
                pool.append(body["role"])
        else:
            return None
        if value in [str(x) for x in pool]:
            hits.append(pid)
    return hits


def _load_yaml_dir(path):
    rows = []
    if not os.path.isdir(path):
        return rows
    for name in sorted(os.listdir(path)):
        if not name.endswith(".yaml") or name.startswith("_"):
            continue
        with open(os.path.join(path, name), "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        if isinstance(doc, dict):
            rows.append((os.path.join(path, name), doc))
    return rows


def bootstrap_sole_holder(people, today):
    """Read-only: resolve the single active single-owner bootstrap exception.

    Looks for a lane-ownership policy that names a bootstrap single-owner
    exception, then an active, unexpired exception record naming the
    holder. Returns (person_id, None) on a clean unambiguous resolution, or
    (None, reason) otherwise. Never guesses among multiple candidates.
    """
    policies = [doc for _p, doc in _load_yaml_dir(POLICIES_DIR)
                if "bootstrap" in str(doc.get("description", "")).lower()
                and "all" in str(doc.get("description", "")).lower()
                and "seat" in str(doc.get("description", "")).lower()]
    if not policies:
        return None, "no bootstrap single-owner lane-ownership policy found"
    exception_refs = set(str(p.get("exception_ref")) for p in policies
                         if p.get("exception_ref"))
    if not exception_refs:
        return None, "bootstrap policy names no exception_ref"

    candidates = []
    for path, doc in _load_yaml_dir(EXCEPTIONS_DIR):
        if str(doc.get("id")) not in exception_refs:
            continue
        if str(doc.get("status", "")).lower() != "active":
            continue
        expires = doc.get("expires")
        try:
            if expires and datetime.date.fromisoformat(str(expires)) < today:
                continue
        except ValueError:
            continue
        holder = doc.get("granted_by")
        if not holder:
            continue
        candidates.append((str(holder), path))

    if not candidates:
        return None, "no active, unexpired bootstrap exception found"
    holders = sorted(set(h for h, _p in candidates))
    if len(holders) > 1:
        return None, "ambiguous bootstrap exceptions naming different holders: %s" % ", ".join(holders)
    holder = holders[0]
    if holder not in people:
        return None, "bootstrap exception names %r, which is not an active person entry" % holder
    return holder, None


def main():
    if len(sys.argv) != 2 or ":" not in sys.argv[1]:
        print("RESOLVE: NONE (usage: capability:<x> | role:<y>)")
        return 2
    kind, value = sys.argv[1].split(":", 1)
    if kind not in ("capability", "role"):
        print("RESOLVE: NONE (unknown selector kind %r)" % kind)
        return 2

    people = load_people()
    if not people:
        print("RESOLVE: NONE (%s has no active person entries)" % PEOPLE_DIR)
        return 2

    hits = direct_hits(kind, value, people)
    if hits:
        if len(hits) > 1:
            print("RESOLVE: AMBIGUOUS (%d holders: %s)"
                  % (len(hits), ", ".join(sorted(hits))))
            return 2
        print("RESOLVE: %s" % hits[0])
        return 0

    today = datetime.datetime.now(datetime.timezone.utc).date()
    holder, reason = bootstrap_sole_holder(people, today)
    if holder is None:
        print("RESOLVE: NONE (no active holder of %s; %s)"
              % (sys.argv[1], reason))
        return 2
    print("RESOLVE: %s" % holder)
    return 0


if __name__ == "__main__":
    sys.exit(main())
