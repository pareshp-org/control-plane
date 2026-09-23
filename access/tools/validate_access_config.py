#!/usr/bin/env python
"""Validate every access/** configuration document against its JSON Schema.

Discovery rule, binding: every access/schemas/*.schema.json declares "x-target",
the repository-relative path of the single YAML document it governs. There is no
shared index; adding a document means adding a schema file. Any YAML document
under access/ that no schema targets is a FAILURE, not an omission -- an
unvalidated access declaration is declared state nothing checks.

Exit 0 on success, 1 on any failure.
"""
import glob
import json
import os
import sys

import yaml
from jsonschema import Draft202012Validator

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SCHEMA_GLOB = os.path.join(ROOT, "access", "schemas", "*.schema.json")
CONFIG_GLOB = os.path.join(ROOT, "access", "**", "*.yaml")
EXCLUDED = (
    os.path.join(ROOT, "access", "testdata") + os.sep,
    # access/secrets/** is L5 phase 2's own tree (lanes/L5-02-secrets-and-
    # boundaries.md): it declares and validates itself through
    # access/secrets/schemas/*.schema.json and access/secrets/tools/
    # validate_tiers.py (plus this phase's own per-check validators), a
    # deliberately separate regime from access/schemas/*.schema.json so that
    # each phase file's tooling governs only the tree it owns.
    os.path.join(ROOT, "access", "secrets") + os.sep,
    os.path.join(ROOT, "access", "tests") + os.sep,
    os.path.join(ROOT, "access", "ai-toolchain") + os.sep,
    os.path.join(ROOT, "access", "fail-closed") + os.sep,
    os.path.join(ROOT, "access", "invariants") + os.sep,
    os.path.join(ROOT, "access", "layer-b") + os.sep,
    os.path.join(ROOT, "access", "accepted-risks") + os.sep,
)


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def main():
    failures = []
    targets = set()
    schemas = sorted(glob.glob(SCHEMA_GLOB))
    if not schemas:
        print("FAIL no schema files found under access/schemas/")
        print("ACCESS CONFIG VALIDATION FAILED (1)")
        return 1
    for schema_path in schemas:
        try:
            with open(schema_path, "r", encoding="utf-8") as handle:
                schema = json.load(handle)
        except ValueError as exc:
            failures.append("%s is not valid JSON: %s" % (rel(schema_path), exc))
            continue
        target = schema.get("x-target")
        if not target:
            failures.append("%s declares no x-target" % rel(schema_path))
            continue
        target_abs = os.path.abspath(os.path.join(ROOT, target.replace("/", os.sep)))
        targets.add(target_abs)
        if not os.path.exists(target_abs):
            failures.append("%s targets a missing document: %s" % (rel(schema_path), target))
            continue
        with open(target_abs, "r", encoding="utf-8") as handle:
            document = yaml.safe_load(handle)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(document),
            key=lambda err: list(err.path),
        )
        if errors:
            for err in errors:
                where = "/".join(str(part) for part in err.path) or "(root)"
                failures.append("%s: %s at %s" % (target, err.message, where))
        else:
            print("PASS schema %s" % target)
    for config_path in sorted(glob.glob(CONFIG_GLOB, recursive=True)):
        config_abs = os.path.abspath(config_path)
        if config_abs.startswith(EXCLUDED):
            continue
        if config_abs not in targets:
            failures.append("unschemad access document: %s" % rel(config_abs))
    if failures:
        for failure in failures:
            print("FAIL %s" % failure)
        print("ACCESS CONFIG VALIDATION FAILED (%d)" % len(failures))
        return 1
    print("ACCESS CONFIG VALIDATION PASSED (%d documents)" % len(targets))
    return 0


if __name__ == "__main__":
    sys.exit(main())
