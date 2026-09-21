#!/usr/bin/env python3
"""Channel and escalation-path guard (Spec Sections 92.11, 42.2, 46.5, 47.5).

Rules, all mechanical:
  C1 channel_id / escalation_id equals the filename stem
  C2 every channel declares destination: from-configuration and a non-empty
     configuration_key (Section 92.11: a configuration value, never a
     hard-coded destination)
  C3 no literal destination anywhere in notify/channels or notify/escalation:
     no URL, no email address, no @handle, no run of 7 or more digits
  C4 developer_paging_app_required is false everywhere
     (Section 99.2 row R: no paging apps for developers)
  C5 every channel declares messaging_outage_fallback:
     section-42.2-phone-path (Section 46.5)
  C6 the phone path declares ordered positions founder then team-lead,
     contact_numbers_held: outside-the-repository, a non-empty fallback,
     and is_alert_path_when_channel_unavailable: true
"""
import os
import re
import sys

import yaml

CHANNELS = os.path.join("notify", "channels")
ESCALATION = os.path.join("notify", "escalation")

LITERALS = [
    ("URL", re.compile(r"https?://")),
    ("email address", re.compile(r"[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("@handle", re.compile(r"(?<![A-Za-z0-9._%-])@[A-Za-z0-9._-]{2,}")),
    ("digit run", re.compile(r"[0-9]{7,}")),
]


def files(path):
    if not os.path.isdir(path):
        return []
    return [os.path.join(path, n) for n in sorted(os.listdir(path))
            if n.endswith(".yaml")]


def main():
    errors = 0
    channel_files = files(CHANNELS)
    escalation_files = files(ESCALATION)
    if not channel_files:
        print("CHANNEL-CHECK: FAIL (no channel files under %s)" % CHANNELS)
        return 1

    for path in channel_files + escalation_files:
        stem = os.path.basename(path)[: -len(".yaml")]
        with open(path, "r", encoding="utf-8") as handle:
            raw = handle.read()
        doc = yaml.safe_load(raw) or {}
        ident = doc.get("channel_id") or doc.get("escalation_id")
        if ident != stem:
            print("FAIL %s: C1 id %r != filename stem %r"
                  % (path, ident, stem))
            errors += 1
        for label, pattern in LITERALS:
            if pattern.search(raw):
                print("FAIL %s: C3 literal destination present (%s)"
                      % (path, label))
                errors += 1
        if doc.get("developer_paging_app_required") is not False:
            print("FAIL %s: C4 developer_paging_app_required is not false"
                  % path)
            errors += 1

    for path in channel_files:
        with open(path, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        if str(doc.get("destination")) != "from-configuration":
            print("FAIL %s: C2 destination %r is not from-configuration"
                  % (path, doc.get("destination")))
            errors += 1
        if not str(doc.get("configuration_key", "")).strip():
            print("FAIL %s: C2 configuration_key is empty" % path)
            errors += 1
        if str(doc.get("messaging_outage_fallback")) != \
                "section-42.2-phone-path":
            print("FAIL %s: C5 messaging_outage_fallback %r is not "
                  "section-42.2-phone-path"
                  % (path, doc.get("messaging_outage_fallback")))
            errors += 1

    phone = os.path.join(ESCALATION, "phone-path.yaml")
    if not os.path.exists(phone):
        print("FAIL %s: C6 the Section 42.2 phone path is absent" % phone)
        errors += 1
    else:
        with open(phone, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        positions = doc.get("positions")
        expected = [(1, "founder"), (2, "team-lead")]
        actual = []
        if isinstance(positions, list):
            for row in positions:
                if isinstance(row, dict):
                    actual.append((row.get("position"), str(row.get("role"))))
        if actual != expected:
            print("FAIL %s: C6 positions %r are not [(1, 'founder'), "
                  "(2, 'team-lead')]" % (phone, actual))
            errors += 1
        if str(doc.get("contact_numbers_held")) != "outside-the-repository":
            print("FAIL %s: C6 contact_numbers_held is not "
                  "outside-the-repository" % phone)
            errors += 1
        if not str(doc.get("fallback", "")).strip():
            print("FAIL %s: C6 fallback is empty" % phone)
            errors += 1
        if doc.get("is_alert_path_when_channel_unavailable") is not True:
            print("FAIL %s: C6 the phone path is not declared the alert path "
                  "when the channel is unavailable (Section 46.5)" % phone)
            errors += 1

    print("CHANNELS: %d declared" % len(channel_files))
    print("ESCALATION-PATHS: %d declared" % len(escalation_files))
    if errors:
        print("CHANNEL-CHECK: FAIL (%d errors)" % errors)
        return 1
    print("CHANNEL-CHECK: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
