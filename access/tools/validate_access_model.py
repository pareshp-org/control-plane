#!/usr/bin/env python3
"""Access-model validator (L5-T12, spec 11, 40, 64, 90).

Validates each of the seven access-model documents named in
access/schema/access-model.schema.json against its per-stem JSON Schema.

Stem -> committed file mapping (see the "$comment" in each per-stem schema
for the rationale where the committed filename differs from the stem name):

    github-permissions -> access/model/permission-semantics.yaml
    permission-model    -> access/model/teams.yaml
    branch-protection    -> access/branch-protection/branch-protection.yaml
    secret-tiers         -> access/published/secret-tiers.v1.json
    permission-matrix    -> access/model/permission-matrix.yaml
    fail-closed           -> access/fail-closed/classification-register.yaml
    safe-defaults          -> access/model/safe-defaults.yaml

A model file that does not exist is a FAILURE, never a skip (fail-closed,
spec 64.2 row 1).

Usage:
    validate_access_model.py                  # validate all seven, in order
    validate_access_model.py --only <stem>     # validate one stem
    validate_access_model.py --only <stem> --path <file>
                                                # validate <file> against
                                                # <stem>'s schema instead of
                                                # the committed file -- used
                                                # only by access/tests/
                                                # test_access_model.py to
                                                # exercise negative cases
                                                # without mutating committed
                                                # files.

On success: prints "ACCESS MODEL OK: <n> file(s)" and exits 0.
On any failure: prints one "ACCESS MODEL FAIL: <path>: <message>" line per
failure and exits 1.
"""
import argparse
import json
import os
import sys

import yaml
from jsonschema import Draft202012Validator

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SCHEMA_PATH = os.path.join(REPO_ROOT, "access", "schema", "access-model.schema.json")

STEM_FILES = {
    "github-permissions": os.path.join("access", "model", "permission-semantics.yaml"),
    "permission-model": os.path.join("access", "model", "teams.yaml"),
    "branch-protection": os.path.join("access", "branch-protection", "branch-protection.yaml"),
    "secret-tiers": os.path.join("access", "published", "secret-tiers.v1.json"),
    "permission-matrix": os.path.join("access", "model", "permission-matrix.yaml"),
    "fail-closed": os.path.join("access", "fail-closed", "classification-register.yaml"),
    "safe-defaults": os.path.join("access", "model", "safe-defaults.yaml"),
}

STEM_ORDER = (
    "github-permissions",
    "permission-model",
    "branch-protection",
    "secret-tiers",
    "permission-matrix",
    "fail-closed",
    "safe-defaults",
)


def rel(path):
    return os.path.relpath(path, REPO_ROOT).replace(os.sep, "/")


def load_schema_document():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_document(path):
    """Load a YAML or JSON document by extension. Raises on a missing or
    unparsable file; the caller turns that into a fail-closed failure."""
    with open(path, "r", encoding="utf-8") as handle:
        if path.endswith(".json"):
            return json.load(handle)
        return yaml.safe_load(handle)


def validate_stem(stem, schema_document, override_path=None):
    """Validate one stem's document. Returns (ok, path_for_message, message)."""
    abs_path = os.path.join(REPO_ROOT, override_path) if override_path else \
        os.path.join(REPO_ROOT, STEM_FILES[stem])
    message_path = override_path if override_path else STEM_FILES[stem].replace(os.sep, "/")

    if not os.path.exists(abs_path):
        return False, message_path, "file not found"

    try:
        document = load_document(abs_path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return False, message_path, "could not parse: %s" % exc

    schema = schema_document[stem]
    errors = sorted(
        Draft202012Validator(schema).iter_errors(document),
        key=lambda e: [str(p) for p in e.path],
    )
    if errors:
        first = errors[0]
        location = "/".join(str(p) for p in first.path) or "<root>"
        return False, message_path, "%s: %s" % (location, first.message)

    return True, message_path, None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=STEM_ORDER, default=None,
                         help="validate only this stem")
    parser.add_argument("--path", default=None,
                         help="validate this file against --only's schema "
                              "instead of the committed file (test use only)")
    args = parser.parse_args(argv)

    if args.path and not args.only:
        print("ACCESS MODEL FAIL: --path requires --only")
        return 1

    if not os.path.exists(SCHEMA_PATH):
        print("ACCESS MODEL FAIL: %s: schema document not found" % rel(SCHEMA_PATH))
        return 1

    schema_document = load_schema_document()

    stems = [args.only] if args.only else list(STEM_ORDER)

    failures = []
    checked = 0
    for stem in stems:
        override = args.path if (args.only and stem == args.only) else None
        ok, path_for_message, message = validate_stem(stem, schema_document, override)
        checked += 1
        if not ok:
            failures.append("ACCESS MODEL FAIL: %s: %s" % (path_for_message, message))

    if failures:
        for line in failures:
            print(line)
        return 1

    print("ACCESS MODEL OK: %d file(s)" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
