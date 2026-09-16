# Registry: capabilities

## What this registry holds

Declared product or platform capabilities — discrete, versioned units of what the system
can do. Each entry names the capability, its owning product, maturity level, and any
dependencies on other capabilities.

## File format

One YAML file per item, named `<id>-<slug>.yaml`, where `<id>` matches the
enforced `id` format `CAP-NNNN` (see Schema reference below).
Example: `CAP-0002-auth-sso.yaml` (with `id: CAP-0002`), `CAP-0003-billing-metered.yaml` (with `id: CAP-0003`)

## Schema reference

`schemas/registry/capabilities.v1.schema.json`
