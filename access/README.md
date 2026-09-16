# `access/` — the access-control architecture (subsystem L, spec §99.2)

Owned exclusively by lane **L5** (`Code/implementation/PARTITION.md`, FROZEN).
No other lane writes any path under `access/`.

## What lives here

| Directory | Holds | Spec |
|---|---|---|
| `model/` | Permission model, person-class → Team → Write derivation; organisation-level declared state (base Read, 2FA, Owner continuity); the §11.1 verified permission-semantics table; Teams derivation rules | §11, §11.1, §11.2 |
| `codeowners/` | The human-only CODEOWNERS generator and its machine-identity denylist | §11.3, D53 |
| `branch-protection/` | The §11.3 branch-protection checklist as declared state, with the unarmed and armed profiles of §95.2 | §11.3, §95.2 |
| `environments/` | The deployment branch and tag policy for every environment | §33.4 |
| `plan-tier/` | The §11.4 plan-tier facts and the checker that proves nothing depends on an Enterprise-only feature | §11.4, D73 |
| `arming/` | The D101 arming order and the gate that refuses an unsatisfiable arming | D101, §98.2 |
| `runbooks/` | The `gh` apply runbooks. Dry-run by default; `--apply` requires credentials no build agent holds | §98.2 |
| `checks/` | The Phase 1 access completion check and the negative-test register | §98.2 |
| `schemas/` | One JSON Schema per configuration document. Each declares `x-target` | — |
| `tools/` | Validators, renderers and the blocker helper | — |
| `testdata/` | Fixtures. Never applied to a real organisation | — |

## Binding rules for anything added here

1. **No repository names.** §11: repositories are enumerated dynamically from the
   product registry; no script contains a hard-coded list of repository names.
2. **No organisation login.** Supplied at apply time in `$ORG_LOGIN`.
3. **No secrets, no tokens, no API keys.** §101 invariant 84.
4. **Every YAML document under `access/` (outside `testdata/`) has a schema in
   `access/schemas/` declaring it as `x-target`.** `access/tools/validate_access_config.py`
   fails on any document that does not.
5. **Read-only approval never satisfies branch protection.** §11.1. Any document
   here that implies otherwise is wrong.
