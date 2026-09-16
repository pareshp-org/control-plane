# Registry: policies

## What this registry holds

Governance policies that define rules, thresholds, and decision criteria for the
Multi-Product Engineering OS. Each entry captures the policy ID, scope, enforcement
level, and the decisions or FDs it fulfills.

## File format

One YAML file per item, named `<id>.yaml`.
Example: `pol-merge-gate.yaml`, `pol-lane-capacity.yaml`

## Schema reference

`schemas/registry/policies.v1.schema.json`
