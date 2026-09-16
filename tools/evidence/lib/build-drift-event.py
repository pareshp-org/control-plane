#!/usr/bin/env python3
"""Build the Blocking-class drift event for a digest-chain mismatch.

Spec: Section 92.11 line 8276 - "Blocking-class drift" is on the closed push
list, and "Every push event exists in the Section 97 event taxonomy - an event
absent from the taxonomy cannot page anyone." Section 97.3 lines 8931-8944 -
the binding event envelope. Section 53.2 line 4697 - Level 4, Block.
Section 41.2 line 3729 - "any mismatch is a P0 investigation".

This module chooses NO severity and writes NO incident record: the incident
record store is written by the incident workflow (Section 97.2 line 8846) and
its shape is Lane 4's.
"""
import argparse, json, os, sys

try:
    import yaml
except ImportError:
    print("EVIDENCE-FAIL MISSING_TOOL: python3 yaml module not installed", file=sys.stderr)
    sys.exit(2)


def die(token, text):
    print("EVIDENCE-FAIL %s: %s" % (token, text), file=sys.stderr)
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser()
    for flag in ("--findings", "--event-types", "--event-id", "--actor",
                 "--run-url", "--now", "--out-dir"):
        ap.add_argument(flag, required=True)
    a = ap.parse_args()

    if not os.path.isfile(a.findings):
        die("FINDINGS_ABSENT", a.findings)
    result = json.load(open(a.findings, encoding="utf-8"))
    findings = result.get("findings") or []
    if not findings:
        print("EVIDENCE-OK NO_ESCALATION")
        return 0

    types = (yaml.safe_load(open(a.event_types, encoding="utf-8")) or {}).get("map") or {}
    event_type = types.get("drift_detected")
    if not event_type:
        die("EVENT_TYPE_UNRESOLVED",
            "no identifier under map.drift_detected in %s "
            "(DECISION REQUIRED D-L2-08)" % a.event_types)

    products = sorted({f.get("product") for f in findings if f.get("product")})
    event = {
        "event_schema_version": 1,
        "event_id": a.event_id,
        "event_type": event_type,
        "occurred_at": a.now,
        "recorded_at": a.now,
        "actor": a.actor,
        "product": products[0] if len(products) == 1 else "estate",
        "subject_ref": a.run_url,
        "payload": {
            # Section 53.4 line 4715: this is the only severity vocabulary that
            # exists anywhere in this system. No SEV value is chosen here.
            "drift_class": "Blocking",
            "reconciliation_level": 4,
            "detector": "verify-digest-chain",
            "spec": "Section 32 line 2823; Section 41.2 line 3729; "
                    "Section 53.2 line 4697",
            "push_list_entry": "Blocking-class drift (Section 92.11 line 8276)",
            "products_affected": products,
            "findings_count": len(findings),
            "findings": findings,
        },
    }
    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "drift-event.yaml"), "w", encoding="utf-8") as fh:
        yaml.safe_dump(event, fh, default_flow_style=False, sort_keys=True)
    print("EVIDENCE-FAIL P0_ESCALATION_REQUIRED findings=%d" % len(findings))
    return 3


if __name__ == "__main__":
    sys.exit(main())
