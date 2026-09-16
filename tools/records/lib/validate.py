#!/usr/bin/env python3
"""L4 record validator. Master Spec v4.0 Section 97.2, Section 97.3.

Usage: validate.py <schema.json> <record.yaml> [<record.yaml> ...]
Exit 0 and print "VALID <path>" per file, or exit 1 and print "INVALID <path>: <error>".
A file that cannot be read or parsed is INVALID, never skipped (fail closed).
"""
import json
import pathlib
import sys

import yaml
from jsonschema import Draft202012Validator, RefResolver


class _NoImplicitDatesLoader(yaml.SafeLoader):
    """PyYAML's SafeLoader auto-converts ISO8601-looking scalars (both full
    timestamps and bare dates) into datetime.datetime / datetime.date objects
    via the implicit tag:yaml.org,2002:timestamp resolver. Every record and
    event field in this schema family (timestamp_utc, date_utc) is declared
    "type": "string" with a pattern (Section 97.1 line 8839) - the record
    files themselves are the source of truth, not a parsed Python type. If
    left on, a syntactically valid timestamp like 2026-09-14T02:11:00Z fails
    "type": "string" every time, which would make the base-defs probe fixture
    itself always INVALID. Strip that implicit resolver so scalars matching
    the timestamp form stay plain strings; every other implicit resolver
    (bool, int, float, null, merge) is preserved unchanged.
    """


_NoImplicitDatesLoader.yaml_implicit_resolvers = {
    key: [
        (tag, regexp)
        for tag, regexp in resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_yaml(text):
    return yaml.load(text, Loader=_NoImplicitDatesLoader)


def main(argv):
    if len(argv) < 3:
        print("USAGE: validate.py <schema.json> <record.yaml> [...]")
        return 2
    schema_path = pathlib.Path(argv[1]).resolve()
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print("INVALID <schema>: %s: %s" % (schema_path, exc))
        return 1
    base = schema_path.parent.as_uri() + "/"
    store = {}
    for sibling in schema_path.parent.glob("*.json"):
        try:
            store[sibling.as_uri()] = json.loads(sibling.read_text(encoding="utf-8"))
            store[sibling.name] = json.loads(sibling.read_text(encoding="utf-8"))
        except Exception:
            pass
    resolver = RefResolver(base_uri=base, referrer=schema, store=store)
    validator = Draft202012Validator(schema, resolver=resolver)
    failed = 0
    for target in argv[2:]:
        path = pathlib.Path(target)
        try:
            data = load_yaml(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print("INVALID %s: unreadable: %s" % (target, exc))
            failed += 1
            continue
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        if errors:
            first = errors[0]
            where = "/".join(str(p) for p in first.path) or "<root>"
            print("INVALID %s: %s: %s" % (target, where, first.message))
            failed += 1
        else:
            print("VALID %s" % target)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
