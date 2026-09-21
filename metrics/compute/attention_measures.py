#!/usr/bin/env python3
"""metrics/compute/attention_measures.py (L4-P7-20)

Founder coordination time, Team Lead coordination hours, engineering
hours per product per month, QA verification hours, and Founder total OS
ritual hours - all derived from the attention ledger (metrics/attention/,
Master Spec v4.0 §103.13 lines 9962-9982). Any figure whose underlying
entries include self-reported hours carries the `provenance:
self-reported` label PERMANENTLY - an aggregate built from a mix of
self-reported and derived entries is downgraded to self-reported as a
whole, and an entry that itself is self-reported but has lost that label
is malformed and rejected rather than silently aggregated as if it were
derived.

Usage: attention_measures.py --store <metrics/attention path> --json

Ledger entry shape this module expects (one YAML file per entry):
  category: founder_coordination | team_lead_coordination | engineering |
            qa_verification | os_ritual
  product: <slug>            (required for the engineering category)
  hours: <number>
  month: <YYYY-MM>
  provenance: self-reported | derived
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import emit, fail, read_store, unbaselined  # noqa: E402

CATEGORIES = {
    "founder_coordination", "team_lead_coordination", "engineering",
    "qa_verification", "os_ritual",
}


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--store", required=True)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        rows = read_store(args.store)
    except FileNotFoundError:
        fail(args.store, "store-absent")
        return 1

    if not rows:
        emit(unbaselined(args.store, "attention_measures"))
        return 0

    totals = {}       # (category, product-or-None) -> hours
    provenance = {}    # same key -> set of provenances seen
    for path, doc in rows:
        if not isinstance(doc, dict):
            fail(args.store, "malformed-entry:%s" % path)
        category = doc.get("category")
        if category not in CATEGORIES:
            fail(args.store, "unknown-category:%s:%s" % (path, category))
        hours = doc.get("hours")
        if hours is None:
            fail(args.store, "entry-missing-hours:%s" % path)
        entry_provenance = doc.get("provenance")
        if entry_provenance not in ("self-reported", "derived"):
            fail(args.store, "entry-missing-or-invalid-provenance:%s" % path)
        product = doc.get("product") if category == "engineering" else None
        key = (category, product)
        totals[key] = totals.get(key, 0) + hours
        provenance.setdefault(key, set()).add(entry_provenance)

    measures = []
    for (category, product), hours in totals.items():
        # A group with ANY self-reported member is self-reported as a whole -
        # the label never gets diluted away by mixing in derived entries.
        label = "self-reported" if "self-reported" in provenance[(category, product)] else "derived"
        measures.append({
            "category": category,
            "product": product,
            "hours": round(hours, 2),
            "provenance": label,
        })

    emit({
        "store": args.store,
        "measure": "attention_measures",
        "n": len(rows),
        "measures": measures,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
