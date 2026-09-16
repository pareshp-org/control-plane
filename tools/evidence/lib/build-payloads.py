#!/usr/bin/env python3
"""Build the deployment-record and event payloads for one deploy.

Spec: Section 97.2 lines 8892-8903 (the representative deployment record);
Section 97.3 lines 8931-8944 (the binding event envelope).

The record's field NAMES come from the eleven-question map, so the writer of
this phase writes exactly the names the reader of L2-T504 reads. Nothing here
hard-codes a path into the records or events trees - PARTITION.md rule 4.
"""
import argparse, os, sys

try:
    import yaml
except ImportError:
    print("EVIDENCE-FAIL MISSING_TOOL: python3 yaml module not installed", file=sys.stderr)
    sys.exit(2)


def die(token, text):
    print("EVIDENCE-FAIL %s: %s" % (token, text), file=sys.stderr)
    sys.exit(2)


def field_for(mapping, n, token):
    entry = mapping.get(n) or mapping.get(str(n))
    if not entry or not entry.get("record_field"):
        die(token, "map declares no record_field for question %s" % n)
    return entry["record_field"]


def main():
    ap = argparse.ArgumentParser()
    for flag in ("--map", "--event-types", "--record-id", "--event-id", "--product",
                 "--environment", "--digest", "--commit", "--run-url", "--actor",
                 "--approved-by", "--staging-verified", "--smoke-result",
                 "--uat-record", "--now", "--out-dir"):
        ap.add_argument(flag, required=True)
    a = ap.parse_args()

    mapping = (yaml.safe_load(open(a.map, encoding="utf-8")) or {}).get("map") or {}
    if not mapping:
        die("MAP_ABSENT", "no map: block in %s" % a.map)

    types_doc = yaml.safe_load(open(a.event_types, encoding="utf-8")) or {}
    types = types_doc.get("map") or {}
    event_type = types.get("version_digest_confirmed")
    if not event_type:
        die("EVENT_TYPE_UNRESOLVED",
            "no identifier under map.version_digest_confirmed in %s "
            "(DECISION REQUIRED D-L2-08)" % a.event_types)

    f_commit = field_for(mapping, 1, "MAP_INCOMPLETE")
    f_digest = field_for(mapping, 5, "MAP_INCOMPLETE")
    f_deployed_at = field_for(mapping, 9, "MAP_INCOMPLETE")
    f_staging_verified = field_for(mapping, 7, "MAP_INCOMPLETE")
    f_approved_by = field_for(mapping, 8, "MAP_INCOMPLETE")
    f_smoke = field_for(mapping, 10, "MAP_INCOMPLETE")
    entry9 = mapping.get(9) or mapping.get("9")
    f_environment = entry9.get("filter_field")
    if not f_environment:
        die("MAP_INCOMPLETE", "map declares no filter_field for question 9")

    def opt(v):
        return None if v in (None, "", "none", "null") else v

    record = {
        "record_schema_version": 1,
        "id": a.record_id,
        "product": a.product,
        f_environment: a.environment,
        f_commit: a.commit,
        f_digest: a.digest,
        f_deployed_at: a.now,
        f_staging_verified: (a.staging_verified == "true"),
        f_approved_by: opt(a.approved_by),
        f_smoke: opt(a.smoke_result),
        "approval_event": a.run_url,
        "uat_record": opt(a.uat_record),
        "deployed_by": a.actor,
        "rollback_of": None,
    }

    # Section 97.3 lines 8931-8944: the envelope is binding and an event missing
    # any envelope field is rejected at write time.
    event = {
        "event_schema_version": 1,
        "event_id": a.event_id,
        "event_type": event_type,
        "occurred_at": a.now,
        "recorded_at": a.now,
        "actor": a.actor,
        "product": a.product,
        "subject_ref": a.record_id,
        "payload": {
            "environment": a.environment,
            "digest": a.digest,
            "commit": a.commit,
            "run_url": a.run_url,
            "approved_by": opt(a.approved_by),
            "smoke_result": opt(a.smoke_result),
        },
    }

    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "record.yaml"), "w", encoding="utf-8") as fh:
        yaml.safe_dump(record, fh, default_flow_style=False, sort_keys=True)
    with open(os.path.join(a.out_dir, "event.yaml"), "w", encoding="utf-8") as fh:
        yaml.safe_dump(event, fh, default_flow_style=False, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
