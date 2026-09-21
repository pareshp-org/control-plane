#!/usr/bin/env python3
"""metrics/compute/_lib.py

Shared helpers for the L4-P7-06..20 compute modules. Every module reads
real record/event files from a store directory and reports honestly: an
absent store is a hard failure (exit non-zero, never a silent zero); an
existing-but-empty store renders every count/rate as "unbaselined"
(Master Spec v4.0 D77, §103 preamble line 9789) rather than a 0 that a
threshold could misread as a miss.

Every timestamp field in a record is a plain ISO8601 string (Section 97.1
line 8839) - never let PyYAML's implicit timestamp resolver silently turn
one into a datetime object, which is exactly the class of bug fixed in
tools/records/lib/validate.py earlier in this lane's Phase 2 work.
"""
import datetime
import json
import os
import sys

import yaml


class NoImplicitDatesLoader(yaml.SafeLoader):
    pass


NoImplicitDatesLoader.yaml_implicit_resolvers = {
    key: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_yaml(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.load(fh, Loader=NoImplicitDatesLoader)


def read_store(store_path, ignored=(".gitkeep", "README.md", "CONTRIBUTING.md")):
    """Yield (filename, parsed-doc) for every non-housekeeping file directly
    under store_path, recursively (events/ nests by day). Raises FileNotFoundError
    if store_path itself does not exist - callers must not swallow that."""
    if not os.path.isdir(store_path):
        raise FileNotFoundError(store_path)
    out = []
    for root, _dirs, files in os.walk(store_path):
        for name in sorted(files):
            if name in ignored:
                continue
            full = os.path.join(root, name)
            try:
                doc = load_yaml(full)
            except Exception as exc:
                raise ValueError("unreadable record %s: %s" % (full, exc))
            out.append((full, doc))
    return out


def parse_ts(value):
    """Parse a Section 97.1 UTC-with-offset timestamp string into a naive UTC
    datetime for arithmetic. Returns None if value is falsy."""
    if not value:
        return None
    v = str(value)
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    dt = datetime.datetime.fromisoformat(v)
    if dt.tzinfo is not None:
        dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    return dt


def parse_date(value):
    if not value:
        return None
    return datetime.date.fromisoformat(str(value))


def emit(result):
    print(json.dumps(result, sort_keys=True))


def fail(store, message):
    print(json.dumps({"error": message, "store": store}, sort_keys=True))
    sys.exit(1)


def unbaselined(store, measure):
    """D77: an existing-but-empty store renders unbaselined, never a miss."""
    return {"store": store, "measure": measure, "baseline": "unbaselined", "n": 0}
