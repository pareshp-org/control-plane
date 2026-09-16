# Registry: exceptions

## What this registry holds

Bootstrap exceptions — temporary deviations from governance rules that have been
explicitly approved for a bounded period. Each entry records the exception ID, the rule
being waived, the approver, the expiry date, and the remediation plan.

## File format

One YAML file per item, named `<id>.yaml`.
Example: `exc-001-single-seat-bootstrap.yaml`

## Schema reference

`schemas/registry/exceptions.v1.schema.json`
