#!/usr/bin/env python3
"""End-to-end closed-list guard (Spec Section 92.11).

  G1 every route's push_class is one of the eight closed classes
  G2 the distinct class set is exactly those eight, and the route count is 11
  G3 no literal destination in any .yaml or .md under notify/channels,
     notify/escalation or notify/routing (Section 92.11: a configuration
     value, never a hard-coded destination)
  G4 every route's destination_channel names a channel declared under
     notify/channels/ that carries a configuration_key
  G5 notify/route.py REFUSES every probe event type that is not on the list
  G6 no push_class is declared in any file outside notify/routing/
  G7 no route mentions a detection leg or an expiry finding -- alert traffic
     (Section 51.5) and the expiry wait surface (Section 92.6) are not push
     events
  G8 notify/published/routing.v1.json matches a fresh regeneration
"""
import os
import re
import subprocess
import sys

import yaml

NOTIFY = "notify"
ROUTING = os.path.join(NOTIFY, "routing")
CHANNELS = os.path.join(NOTIFY, "channels")
ESCALATION = os.path.join(NOTIFY, "escalation")
PUBLISHED = os.path.join(NOTIFY, "published", "routing.v1.json")

CLASSES = {
    "gate_1_submission", "gate_2_request", "verification_block_unblock",
    "blocking_class_drift", "expiry_warning", "launch_sign_off_request",
    "pending_founder_decision", "support_first_touch_breach",
}
EXPECTED_ROUTES = 11

LITERAL = re.compile(r"https?://|[0-9]{7,}")

# Real Section 97.3 taxonomy identifiers that are deliberately NOT on the
# closed push list. The router must refuse every one of them.
OFF_LIST_PROBES = [
    "restore_test_executed",
    "credential_rotated",
    "asset_owner_reassigned",
    "orphan_detected",
    "model_benchmark_completed",
    "background_layer_pr_created",
]

FORBIDDEN_IN_ROUTES = ["detection-leg", "detection_leg", "dead-mans-switch",
                       "expiry-watch", "expiring assets"]


def yaml_files(path):
    if not os.path.isdir(path):
        return []
    return [os.path.join(path, n) for n in sorted(os.listdir(path))
            if n.endswith(".yaml")]


def text_files(path):
    if not os.path.isdir(path):
        return []
    return [os.path.join(path, n) for n in sorted(os.listdir(path))
            if n.endswith(".yaml") or n.endswith(".md")]


def main():
    errors = 0
    routes = []
    for path in yaml_files(ROUTING):
        with open(path, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        routes.append((path, doc))

    seen = set()
    for path, doc in routes:
        klass = str(doc.get("push_class"))
        if klass not in CLASSES:
            print("FAIL %s: G1 push_class %r is outside the eight closed "
                  "classes" % (path, doc.get("push_class")))
            errors += 1
        else:
            seen.add(klass)
    if seen != CLASSES:
        print("FAIL: G2 class set is %d of 8 (missing: %s)"
              % (len(seen), ", ".join(sorted(CLASSES - seen)) or "none"))
        errors += 1
    if len(routes) != EXPECTED_ROUTES:
        print("FAIL: G2 route count is %d, expected %d"
              % (len(routes), EXPECTED_ROUTES))
        errors += 1

    for path in text_files(CHANNELS) + text_files(ESCALATION) + \
            text_files(ROUTING):
        with open(path, "r", encoding="utf-8") as handle:
            raw = handle.read()
        if LITERAL.search(raw):
            print("FAIL %s: G3 literal destination present" % path)
            errors += 1

    keys = {}
    for path in yaml_files(CHANNELS):
        with open(path, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        cid = str(doc.get("channel_id", ""))
        if cid:
            keys[cid] = str(doc.get("configuration_key", "")).strip()
    for path, doc in routes:
        channel = str(doc.get("destination_channel", ""))
        if not keys.get(channel):
            print("FAIL %s: G4 destination_channel %r has no channel with a "
                  "configuration_key" % (path, channel))
            errors += 1

    refused = 0
    for probe in OFF_LIST_PROBES:
        result = subprocess.run(
            [sys.executable, os.path.join(NOTIFY, "route.py"),
             "--event-type", probe],
            capture_output=True, text=True)
        if result.returncode == 3 and "REFUSED" in result.stdout:
            refused += 1
        else:
            print("FAIL: G5 route.py did not refuse off-list event %r "
                  "(exit %d)" % (probe, result.returncode))
            errors += 1
    print("OFF-LIST-PROBES-REFUSED: %d of %d"
          % (refused, len(OFF_LIST_PROBES)))

    for dirpath, _dirnames, filenames in os.walk(NOTIFY):
        if os.path.abspath(dirpath) == os.path.abspath(ROUTING):
            continue
        for name in sorted(filenames):
            if not name.endswith(".yaml"):
                continue
            path = os.path.join(dirpath, name)
            with open(path, "r", encoding="utf-8") as handle:
                if re.search(r"^push_class:", handle.read(), re.M):
                    print("FAIL %s: G6 a push route is declared outside %s"
                          % (path, ROUTING))
                    errors += 1

    for path, _doc in routes:
        with open(path, "r", encoding="utf-8") as handle:
            raw = handle.read()
        for token in FORBIDDEN_IN_ROUTES:
            if token in raw:
                print("FAIL %s: G7 %r appears in a push route; alert traffic "
                      "(Section 51.5) and the expiry wait surface "
                      "(Section 92.6) are not push events" % (path, token))
                errors += 1

    if not os.path.exists(PUBLISHED):
        print("FAIL: G8 %s is absent" % PUBLISHED)
        errors += 1
    else:
        with open(PUBLISHED, "r", encoding="utf-8") as handle:
            before = handle.read()
        subprocess.run([sys.executable,
                        os.path.join(NOTIFY, "publish_routing.py")],
                       capture_output=True, text=True)
        with open(PUBLISHED, "r", encoding="utf-8") as handle:
            after = handle.read()
        if before != after:
            print("FAIL: G8 %s was hand-edited; it does not match a fresh "
                  "regeneration" % PUBLISHED)
            errors += 1

    print("CLOSED-LIST: %d routes, %d classes" % (len(routes), len(seen)))
    if errors:
        print("CLOSED-LIST-GUARD: FAIL (%d errors)" % errors)
        return 1
    print("CLOSED-LIST-GUARD: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
