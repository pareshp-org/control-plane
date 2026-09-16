# Registry: people

## What this registry holds

Named individuals (and the canary sentinel) who hold seats, assignments, or named roles
within the Multi-Product Engineering OS. Each entry records identity, current role, and
lane assignments so that CMP-01 and CMP-03 can resolve person references at runtime.

## File format

One YAML file per item, named `<id>.yaml`.
Example: `l0-founder.yaml`, `__canary__.yaml`

## Schema reference

`schemas/registry/people.v1.schema.json`

## Special files

- `_canary.yaml` — drift-detection sentinel (FD-106, PFD-026). Do not remove or rename.
