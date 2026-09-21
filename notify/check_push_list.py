#!/usr/bin/env python3
"""Push-list guard (Spec Sections 92.11, 97.3; D79).

Rules, all mechanical:
  P1 route_id equals the filename stem
  P2 push_class is one of the eight closed Section 92.11 classes
  P3 the distinct push_class set is exactly those eight
  P4 every route names a non-empty event_type and taxonomy_source
  P5 destination_channel is non-empty and is a configuration-backed channel
     name, never a literal destination
  P6 pending_founder_decision declares the D79 coalescing rule
  P7 every event_type resolves in registries/platform.yaml when that file
     exists (read-only consumption of an L1-owned registry; skipped with a
     printed marker when absent -- boundary rule B-4)
"""
import os
import re
import sys

import yaml

ROUTING = os.path.join("notify", "routing")
PLATFORM = os.path.join("registries", "platform.yaml")

CLASSES = {
    "gate_1_submission", "gate_2_request", "verification_block_unblock",
    "blocking_class_drift", "expiry_warning", "launch_sign_off_request",
    "pending_founder_decision", "support_first_touch_breach",
}

LITERAL = re.compile(r"https?://|[0-9]{7,}")


def enum_types():
    """Read-only consumption of an L1-owned registry. Never edited here."""
    if not os.path.exists(PLATFORM):
        return None
    with open(PLATFORM, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle) or {}
    for key in ("event_types", "event_type_enum"):
        value = doc.get(key)
        if isinstance(value, list):
            return set(str(v) for v in value)
        if isinstance(value, dict):
            return set(str(k) for k in value.keys())
    return set()


def main():
    known = enum_types()
    if known is None:
        print("TAXONOMY-RESOLUTION: SKIPPED "
              "(registries/platform.yaml absent)")
    else:
        print("TAXONOMY-RESOLUTION: ACTIVE (%d event types)" % len(known))

    if not os.path.isdir(ROUTING):
        print("PUSH-LIST: FAIL (%s absent)" % ROUTING)
        return 1
    names = sorted(n for n in os.listdir(ROUTING) if n.endswith(".yaml"))
    errors = 0
    seen = set()
    unresolved = []
    for name in names:
        path = os.path.join(ROUTING, name)
        stem = name[: -len(".yaml")]
        with open(path, "r", encoding="utf-8") as handle:
            raw = handle.read()
        doc = yaml.safe_load(raw) or {}
        if doc.get("route_id") != stem:
            print("FAIL %s: P1 route_id %r != filename stem %r"
                  % (path, doc.get("route_id"), stem))
            errors += 1
        klass = str(doc.get("push_class"))
        if klass not in CLASSES:
            print("FAIL %s: P2 push_class %r is not one of the eight closed "
                  "Section 92.11 classes" % (path, doc.get("push_class")))
            errors += 1
        else:
            seen.add(klass)
        for field in ("event_type", "taxonomy_source"):
            if not str(doc.get(field, "")).strip():
                print("FAIL %s: P4 %s is empty" % (path, field))
                errors += 1
        dest = str(doc.get("destination_channel", "")).strip()
        if not dest:
            print("FAIL %s: P5 destination_channel is empty" % path)
            errors += 1
        if LITERAL.search(raw):
            print("FAIL %s: P5 literal destination present" % path)
            errors += 1
        if klass == "pending_founder_decision" and \
                not str(doc.get("d79_rule", "")).strip():
            print("FAIL %s: P6 the D79 coalescing rule is not declared"
                  % path)
            errors += 1
        etype = str(doc.get("event_type", "")).strip()
        if known is not None and etype and etype not in known:
            unresolved.append((path, etype))

    missing = sorted(CLASSES - seen)
    for klass in missing:
        print("FAIL: P3 closed class %s has no route" % klass)
        errors += 1

    for path, etype in unresolved:
        print("FAIL %s: P7 event_type %r is absent from the %s enum — an "
              "event absent from the taxonomy cannot page anyone "
              "(Section 92.11)" % (path, etype, PLATFORM))
        errors += 1

    print("PUSH-ROUTES: %d" % len(names))
    print("PUSH-CLASSES: %d of 8" % len(seen & CLASSES))
    if errors:
        print("PUSH-LIST: FAIL (%d errors)" % errors)
        return 1
    print("PUSH-LIST: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
