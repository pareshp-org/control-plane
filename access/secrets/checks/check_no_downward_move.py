#!/usr/bin/env python3
"""The never-moves-down-a-tier check.

Section 40.1, line 3656:
  "A secret never moves down a tier. A production credential appearing anywhere
   below the production tier is a security incident under Section 43 (Security
   Incident Workflow), not a cleanup task."

Two detections:
  R1 registry-collision - a name declared in a tier of rank R also appears in a
     tier of lower rank.
  R2 env-file-leak      - a production-tier name appears in a file named .env,
     .env.* or *.env under the scan root. The scan walks the FILESYSTEM, not
     the git index, because the developer tier is .env.local and git-ignored.

Fail-closed (invariant 80): a missing or unparseable input is exit 2, never a
pass. A finding is exit 1 and is a SECURITY INCIDENT, not a cleanup task.

Usage:  check_no_downward_move.py [<inputs.yaml> [<scan-root>]]
Defaults: contracts/access/access-inputs.yaml  and  .
"""
import os
import sys

import yaml

TIERS_DIR = os.path.join("access", "secrets", "tiers")
TIER_KEYS = {"ci": 2, "staging": 3, "production": 4, "control_plane": 5}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def load_ranks():
    """Ranks come from the T01 registry, never from a constant here."""
    ranks = {}
    if not os.path.isdir(TIERS_DIR):
        return None
    for name in sorted(os.listdir(TIERS_DIR)):
        if not name.endswith(".yaml"):
            continue
        with open(os.path.join(TIERS_DIR, name), "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        if isinstance(doc, dict) and "tier_id" in doc and "rank" in doc:
            ranks[doc["tier_id"]] = doc["rank"]
    return ranks or None


def env_files(root):
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            if filename == ".env" or filename.startswith(".env.") \
               or filename.endswith(".env"):
                hits.append(os.path.join(dirpath, filename))
    return sorted(hits)


def main(argv):
    inputs = argv[1] if len(argv) > 1 else os.path.join(
        "contracts", "access", "access-inputs.yaml")
    scan_root = argv[2] if len(argv) > 2 else "."
    if not os.path.isfile(inputs):
        print("RESULT FAIL inputs-unreadable %s" % inputs)
        return 2
    try:
        with open(inputs, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
    except Exception as exc:                                    # fail closed
        print("RESULT FAIL inputs-unparseable %s" % exc)
        return 2
    registry = doc.get("secret_name_registry")
    if not isinstance(registry, dict):
        print("RESULT FAIL no-secret-name-registry %s" % inputs)
        return 2
    ranks = load_ranks()
    if ranks is None:
        print("RESULT FAIL tier-registry-unreadable %s" % TIERS_DIR)
        return 2
    for key in TIER_KEYS:
        if key not in ranks:
            print("RESULT FAIL tier-missing-from-registry %s" % key)
            return 2

    findings = []
    placed = {}
    for key in sorted(registry):
        if key not in TIER_KEYS:
            print("RESULT FAIL unknown-tier-key %s" % key)
            return 2
        for name in registry.get(key) or []:
            placed.setdefault(str(name), []).append(key)

    # R1 - a name held at rank R must not appear at any lower rank.
    for name, keys in sorted(placed.items()):
        if len(keys) < 2:
            continue
        top = max(ranks[k] for k in keys)
        for key in sorted(keys):
            if ranks[key] < top:
                findings.append(
                    "FINDING R1 registry-collision %s held at rank %d also declared in tier %s (rank %d)"
                    % (name, top, key, ranks[key]))

    # R2 - no production-tier name in any .env file under the scan root.
    production = [str(n) for n in (registry.get("production") or [])]
    for path in env_files(scan_root):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                body = handle.read()
        except Exception as exc:                                # fail closed
            print("RESULT FAIL env-file-unreadable %s (%s)" % (path, exc))
            return 2
        for name in production:
            if name and name in body:
                findings.append(
                    "FINDING R2 env-file-leak %s appears in %s" % (name, path))

    for line in findings:
        print(line)
    print("FINDINGS %d" % len(findings))
    if findings:
        print("CLASS security-incident")
        print("AUTHORITY Section 43 (Security Incident Workflow)")
        print("DRIFT-CLASS Blocking")
        print("IS-CLEANUP-TASK false")
        print("RESULT FAIL")
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
