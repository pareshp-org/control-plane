# AI toolchain — approved runtimes and the pin rule

One file per runtime under `access/ai-toolchain/runtimes/<runtime-id>.yaml`
(PARTITION.md rule 3: directory-per-item, never a shared mutable list). This
realises the `ai-toolchain.yaml` artifact of Spec Section 36.3 with the same
field set.

Enforced by `access/ai-toolchain/validate_toolchain.py`.

## The closed approved-runtime list — Spec Section 35.2

`claude-code`, `codex`, `antigravity`, `cursor`, `kilo-code`, `hermes-agent`.

Adding or removing a runtime is a configuration change with a recorded
decision (Section 35.2). It is never an executor's edit: a runtime that is
not on this list is a blocker issue with `action_requested: L0 decision`.

## The pin rule — Spec Section 36.3, invariant 85

> every extension and MCP server is pinned by full commit SHA or content
> checksum, never by tag — a tag is movable and is therefore not a pin

Accepted pin forms, and no others:

| Form | Pattern |
|---|---|
| Full commit SHA | 40 lower-case hex characters |
| Content checksum | `sha256:` followed by 64 lower-case hex characters |

Rejected, always: a tag, a branch name, `latest`, a semantic version, a
marketplace version string on its own.

Anything not on the list is not installed. Approval is a recorded decision
naming the source pin and the access the component holds (Section 36.3).

## Runtime field table

| Field | Rule |
|---|---|
| `runtime_id` | equal to the filename stem, and on the closed list above |
| `approved_extensions` | list; every entry carries `name` and a pinned `source`; empty is the Section 36.3 default |
| `approved_mcp_servers` | list; same rule |
| `model_configuration.vendor_api_key` | the literal `forbidden` on every runtime (Section 36.6, invariant 84) |

## Runtime-specific bindings

| Runtime | Binding |
|---|---|
| `kilo-code` | `credit_based_billing: forbidden` — it must be configured against a subscription provider, not its own credit-based billing (Section 35.2) |
| `hermes-agent` | `source_pin: 8e9459c97f707047be5915a5c8b4c503756daa9b`, full SHA; pinned-checkout install; `curl_pipe_installer: never`; `self_update_command: never`; installs fetch from the company mirror at the pin; `model_configuration.provider: custom` against the LAN inference endpoint (Sections 35.2, 36.3) |

## What this directory does not decide

The concrete `model_artefact_checksum` for the quantised open-weight model an
inference endpoint serves is operational data, supplied when that endpoint is
provisioned. The validator enforces its **form** when it is present and never
invents its value.

The extension and MCP-server lists ship empty, which is the Section 36.3
default. Adding an entry is a recorded approval decision naming the source pin
and the access held — an L0 decision, never a local edit.
