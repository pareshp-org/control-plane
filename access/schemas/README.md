# `access/schemas/`

One JSON Schema per configuration document under `access/`.

**Every schema MUST declare `x-target`** — the repository-relative path of the
single YAML document it governs. `access/tools/validate_access_config.py`
discovers documents through `x-target` and through nothing else. There is no
index file, because a shared mutable index is exactly what PARTITION rule 3
forbids: directory-per-item only.

A YAML document under `access/` that no schema targets fails validation. That is
deliberate. An access declaration nothing validates is declared state nothing
checks, and §101 invariant 87 requires every security policy to be enforced by
the platform wherever the platform can enforce it.

`access/testdata/` is excluded from the unschemad-document check; fixtures are
inputs to tests, not declared state.

Schemas are Draft 2020-12. Every schema sets `"additionalProperties": false` at
every object level, so a typo in a key is a failure rather than a silently
ignored line.
