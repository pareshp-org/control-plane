#!/usr/bin/env python3
"""access/tests/lib/validate_product_schema.py

Validates one product.yaml against the real, L1-owned
schemas/product/product.contract.v2.schema.json -- the same schema and the
same Draft202012Validator/Registry construction
validators/registry/tests/test_product_platform_blocks.py uses, mirrored
here because that schema is exercised through pytest fixtures, not a
single-file CLI entrypoint L5-07's AT-049 can shell out to directly (EXT-1:
"or equivalent entrypoint" -- this reads the schema, it never edits it).

Usage: validate_product_schema.py PRODUCT_YAML
Exit 0 if the document validates clean; 1 if jsonschema reports any error;
2 if the schema files themselves cannot be found or loaded.
"""
import json
import os
import sys

try:
    import jsonschema
    import yaml
    from referencing import Registry, Resource
except ImportError as exc:  # pragma: no cover - environment gap, fail closed
    print(f"INDETERMINATE :: missing dependency: {exc}", file=sys.stderr)
    sys.exit(2)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def _load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    if len(sys.argv) != 2:
        print("usage: validate_product_schema.py PRODUCT_YAML", file=sys.stderr)
        return 2
    target = sys.argv[1]
    try:
        defs_schema = _load(os.path.join(ROOT, "schemas", "registry", "common", "defs.v1.schema.json"))
        assignments_schema = _load(os.path.join(ROOT, "schemas", "registry", "common", "assignments.v1.schema.json"))
        product_schema = _load(os.path.join(ROOT, "schemas", "product", "product.contract.v2.schema.json"))
    except OSError as exc:
        print(f"INDETERMINATE :: cannot load a schema file: {exc}", file=sys.stderr)
        return 2
    registry = Registry().with_resources([
        ("common/defs.v1.schema.json", Resource.from_contents(defs_schema)),
        (assignments_schema["$id"], Resource.from_contents(assignments_schema)),
        (product_schema["$id"], Resource.from_contents(product_schema)),
    ])
    validator = jsonschema.Draft202012Validator(product_schema, registry=registry)
    with open(target, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)
    errors = list(validator.iter_errors(doc))
    for err in errors:
        print(f"SCHEMA-ERROR {'/'.join(str(p) for p in err.path)}: {err.message}", file=sys.stderr)
    if errors:
        print(f"PRODUCT-SCHEMA: FAIL ({len(errors)} errors)")
        return 1
    print("PRODUCT-SCHEMA: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
