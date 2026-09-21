#!/usr/bin/env python3
"""Generate notify/published/routing.v1.json from the route files.

Generated, never hand-edited (L5-00-charter.md: the Actions webhook step in
every workflow reads this artifact and nothing else). Deterministic: sorted
keys, stable ordering, no timestamps.
"""
import json
import os
import sys

import yaml

ROUTING = os.path.join("notify", "routing")
CHANNELS = os.path.join("notify", "channels")
OUT = os.path.join("notify", "published", "routing.v1.json")

FIELDS = ["route_id", "push_class", "event_type", "taxonomy_source",
          "recipient", "destination_channel", "carries_clock",
          "coalesce_into_morning_digest"]


def main():
    if not os.path.isdir(ROUTING):
        print("ROUTING-PUBLISH: BLOCKED (%s absent)" % ROUTING)
        return 2
    rows = []
    classes = set()
    for name in sorted(os.listdir(ROUTING)):
        if not name.endswith(".yaml"):
            continue
        with open(os.path.join(ROUTING, name), "r",
                  encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        row = {}
        for field in FIELDS:
            row[field] = doc.get(field)
        classes.add(str(doc.get("push_class")))
        rows.append(row)
    rows.sort(key=lambda r: str(r["route_id"]))

    channels = {}
    if os.path.isdir(CHANNELS):
        for name in sorted(os.listdir(CHANNELS)):
            if not name.endswith(".yaml"):
                continue
            with open(os.path.join(CHANNELS, name), "r",
                      encoding="utf-8") as handle:
                doc = yaml.safe_load(handle) or {}
            cid = str(doc.get("channel_id", ""))
            if cid:
                channels[cid] = {
                    "configuration_key": doc.get("configuration_key"),
                    "destination": doc.get("destination"),
                }

    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump({
            "artifact": "routing",
            "version": 1,
            "generated": "by notify/publish_routing.py; never hand-edited",
            "spec_reference": "92.11, 92.1, 42.2, 46.5",
            "closed_push_list": True,
            "channels": channels,
            "routes": rows,
        }, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("ROUTING-PUBLISH: %d routes, %d classes" % (len(rows),
                                                      len(classes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
