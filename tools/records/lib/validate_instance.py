#!/usr/bin/env python3
"""tools/records/lib/validate_instance.py
Write-time instance check. Master Spec v4.0 Section 97.1 line 8839 (UTC with offset),
Section 97.2 line 8890 (record envelope), Section 97.3 lines 8933-8945 (event envelope).
Usage: validate_instance.py <record|event> <schema-path-or-dash> <instance-file>
Full JSON Schema validation is the schema phase's job; this is the write-time gate."""
import json, os, pathlib, re, sys
import yaml

KIND, SCHEMA, PATH = sys.argv[1], sys.argv[2], sys.argv[3]
RECORD_ENVELOPE = ["record_schema_version", "id", "product", "timestamp"]
EVENT_ENVELOPE = ["event_schema_version", "event_id", "event_type", "occurred_at",
                  "recorded_at", "actor", "product", "subject_ref", "payload"]
TS = re.compile(r"^\s*[A-Za-z0-9_]+:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\S*)\s*$")
OFFSET = re.compile(r"(Z|[+-]\d{2}:\d{2})$")


class _NoImplicitDatesLoader(yaml.SafeLoader):
    """See tools/records/lib/validate.py for the full rationale: PyYAML's
    SafeLoader auto-converts ISO8601-looking scalars into datetime objects,
    which fails every "type": "string" timestamp/date field. Strip that one
    implicit resolver so record.base.schema.json's timestamp_utc/date_utc
    patterns see plain strings, matching the write-time gate this script is."""


_NoImplicitDatesLoader.yaml_implicit_resolvers = {
    key: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def fail(msg):
    print("VALIDATE FAIL %s %s" % (msg, PATH))
    sys.exit(1)

text = open(PATH, encoding="utf-8").read()
try:
    doc = yaml.load(text, Loader=_NoImplicitDatesLoader)
except Exception as exc:
    fail("unparseable %s" % exc)
if not isinstance(doc, dict):
    fail("not-a-mapping")
for key in (EVENT_ENVELOPE if KIND == "event" else RECORD_ENVELOPE):
    if key not in doc:
        fail("missing-envelope-field:%s" % key)
for line in text.splitlines():
    m = TS.match(line)
    if m and not OFFSET.search(m.group(1)):
        fail("timestamp-without-utc-offset:%s" % m.group(1))
if SCHEMA != "-" and os.path.exists(SCHEMA):
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    for key in schema.get("required", []):
        if key not in doc:
            fail("missing-schema-required-field:%s" % key)
    try:
        import jsonschema
        from jsonschema import Draft202012Validator, RefResolver
    except ImportError:
        jsonschema = None
    if jsonschema is not None:
        # A bare jsonschema.validate(instance, schema) leaves $ref resolution to
        # jsonschema's default retriever, which treats a relative ref like
        # "record.base.schema.json#/$defs/..." (every store schema does this) or
        # "event-type.enum.json" (the event envelope does this) as a literal URL
        # to fetch over the network - it is neither, and always raises an
        # Unresolvable/unknown-url-type error before any real validation runs.
        # Build the same sibling-schema-directory resolver lib/validate.py uses,
        # so every $ref inside schemas/records/ resolves locally instead.
        schema_dir = os.path.dirname(os.path.abspath(SCHEMA))
        store = {}
        for name in os.listdir(schema_dir):
            if name.endswith(".json"):
                try:
                    sib = json.load(open(os.path.join(schema_dir, name), encoding="utf-8"))
                except Exception:
                    continue
                store[name] = sib
                store[pathlib.Path(os.path.join(schema_dir, name)).as_uri()] = sib
        resolver = RefResolver(base_uri=pathlib.Path(schema_dir).as_uri() + "/", referrer=schema, store=store)
        try:
            Draft202012Validator(schema, resolver=resolver).validate(
                json.loads(json.dumps(doc, default=str))
            )
        except jsonschema.ValidationError as exc:
            fail("schema:%s" % exc.message)
print("VALIDATE OK")
