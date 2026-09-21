#!/usr/bin/env python3
"""Flatten a version-targets file to TAB-separated rows for collect-version.sh.

Argv: targets.yaml [product-filter]
Emits: product<TAB>url<TAB>digest_field<TAB>conformance_profile

A target that declares no digest_field is an input error, never a default:
Section 41.2 (line 3722) declares the endpoint, not the shape of its body.
"""
import sys, yaml

doc = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
only = sys.argv[2] if len(sys.argv) > 2 else ""
targets = doc.get("targets") or []
if not targets:
    print("EVIDENCE-FAIL NO_TARGETS: target list is empty", file=sys.stderr)
    sys.exit(2)
rows = []
for t in targets:
    product = str(t.get("product", "")).strip()
    url = str(t.get("url", "")).strip()
    field = str(t.get("digest_field", "")).strip()
    profile = str(t.get("conformance_profile", "service")).strip()
    if not product or not url:
        print("EVIDENCE-FAIL TARGET_INCOMPLETE: %s" % (product or url or "<empty>"),
              file=sys.stderr)
        sys.exit(2)
    if not field:
        print("EVIDENCE-FAIL DIGEST_FIELD_UNDECLARED: %s" % product, file=sys.stderr)
        sys.exit(2)
    if only and product != only:
        continue
    rows.append("\t".join([product, url, field, profile]))
if not rows:
    print("EVIDENCE-FAIL NO_TARGETS: no target matched the product filter",
          file=sys.stderr)
    sys.exit(2)
print("\n".join(rows))
