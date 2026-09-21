#!/usr/bin/env python3
"""Publish access/published/secret-tiers.v1.json.

Charter L5-00 Section 7: this is the artifact Lane 3 reads to know which tier a
credential lives in, and the one AT-110 executes the published permission set
against (Section 40.1 lines 3644-3686; Section 40.3 lines 3695-3704).

Deterministic by construction: sorted keys, two-space indent, LF newlines, no
timestamp. Re-running it must produce no diff - that is what makes publication
byte-reproducible.

Usage: publish_secret_tiers.py [--check]
--check verifies the file on disk equals what would be generated, and writes
nothing.
"""
import glob
import json
import os
import sys

import yaml

OUT = os.path.join("access", "published", "secret-tiers.v1.json")


def read_all(pattern):
    docs = []
    for path in sorted(glob.glob(pattern)):
        with open(path, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        docs.append(doc)
    return docs


def build():
    tiers = read_all(os.path.join("access", "secrets", "tiers", "*.yaml"))
    creds = read_all(os.path.join("access", "secrets", "fifth-tier", "*.yaml"))
    envelopes = {}
    for env in read_all(os.path.join("access", "secrets", "envelope", "*.envelope.yaml")):
        envelopes[env["credential_id"]] = env
    payload = {
        "artifact": "secret-tiers",
        "version": 1,
        "spec_anchor": "Section 40.1 lines 3644-3686; Section 40.3 lines 3695-3704",
        "tiers": [
            {
                "tier_id": t["tier_id"],
                "rank": t["rank"],
                "tier": t["tier"],
                "location": t["location"],
                "contains": t["contains"],
                "holds_production_credentials": bool(t["holds_production_credentials"]),
            }
            for t in sorted(tiers, key=lambda d: d["rank"])
        ],
        "downward_move": {
            "permitted": False,
            "class": "security-incident",
            "authority": "Section 43 (Security Incident Workflow)",
            "is_cleanup_task": False,
        },
        "fifth_tier_credentials": [],
        "boundaries": [
            {
                "boundary_id": "boundary-1-production",
                "statement": "A fully compromised developer workstation must not yield production database access, production credentials, or the ability to deploy to production.",
            },
            {
                "boundary_id": "boundary-2-control-plane",
                "statement": "A fully compromised engineering workstation must not yield the control-plane machine-credential store.",
                "decision": "D95",
            },
        ],
        "at110": {
            "artifact_under_test": OUT,
            "attempts": 6,
            "all_must_fail": True,
            "re_executed_at_every_rotation": True,
        },
    }
    for cred in sorted(creds, key=lambda d: d["credential_id"]):
        cid = cred["credential_id"]
        env = envelopes.get(cid, {})
        payload["fifth_tier_credentials"].append({
            "credential_id": cid,
            "tier_id": cred["tier_id"],
            "rank": cred["rank"],
            "kind": cred["kind"],
            "kind_narrowed": bool(cred["kind_narrowed"]),
            "host": cred["host"],
            "rotation_cadence": cred["rotation_cadence"],
            "rotator": cred["rotator"],
            "runbook": cred["runbook"],
            "envelope_alert_owner": cred["envelope_alert_owner"],
            "permission_set": list(cred["permission_set"]),
            "reissue_source": cred["reissue_source"],
            "envelope": {
                "temporal_window_rule": env.get("temporal_window_rule"),
                "signed_run_record_required": (env.get("signed_run_record") or {}).get("required"),
                "run_count_ceiling_per_day": (env.get("run_count_ceiling_per_day") or {}).get("value"),
                "expected_source_host": (env.get("expected_source_host") or {}).get("value"),
                "published_api_call_counts": (env.get("published_api_call_counts") or {}).get("required"),
                "outside_envelope_class": env.get("outside_envelope_class"),
            },
        })
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main(argv):
    body = build()
    if "--check" in argv:
        if not os.path.isfile(OUT):
            print("RESULT FAIL published-artifact-absent %s" % OUT)
            return 2
        with open(OUT, "r", encoding="utf-8") as handle:
            current = handle.read()
        if current != body:
            print("RESULT FAIL published-artifact-stale %s" % OUT)
            return 1
        print("RESULT PASS reproducible")
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(body)
    print("WROTE %s" % OUT)
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
