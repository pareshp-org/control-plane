# FROZEN PARTITION CONTRACT — v1
# Authoritative. Every implementation document must conform. Do not redesign.

## Repositories
| Repo | Holds | Notes |
|---|---|---|
| `control-plane` | registries, contracts, schemas, validators, reconciler, provisioning, reusable workflows, access/infra config | Full branch protection. NO machine bypass actor (D89) |
| `control-plane-records` | `records/**`, `events/**` | No review protection; no-bypass ruleset blocks force-push/delete (D107) |
| `product-template` | scaffold consumed by create-product | |
| `<product>` xN | the eight live products | onboarded per-product, not built |

## The five build lanes — STRICT path ownership
A lane may edit ONLY paths it owns. Enforced by CODEOWNERS + the lane-guard CI check.

| Lane | Branch prefix | Subsystems | OWNS (exclusively) |
|---|---|---|---|
| **L1 Registries & Contracts** | `lane/1/*` | A, B | `schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**` |
| **L2 Pipeline & Evidence** | `lane/2/*` | E, F | `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**` |
| **L3 Reconciler & Provisioning** | `lane/3/*` | C, D | `reconciler/**`, `tools/provision/**`, `validators/drift/**` |
| **L4 Records, Events & Metrics** | `lane/4/*` | I, N | ALL of `control-plane-records`, plus `schemas/records/**`, `metrics/**`, `tools/records/**` |
| **L5 Access, Infra & Ops** | `lane/5/*` | K, L, M, Q, R | `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**` |
| **L0 Integrator** (human/lead) | `main`, `integration` | — | `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` |

## Non-negotiable anti-conflict rules
1. **One owner per path.** No path appears in two lanes. A lane PR touching a foreign path FAILS the lane-guard check. No exceptions.
2. **Contract-first.** `contracts/**` is written by L0 in Phase 0 and FROZEN. Lanes code against it and against generated stubs/fixtures. A lane needing a contract change files a Contract Change Request; it never edits `contracts/**`.
3. **No shared mutable file, ever.** No lane appends to a shared index, list, or registry-of-everything. Directory-per-item only (one file per event, per record, per schema). This is why merges cannot conflict.
4. **No cross-lane imports.** A lane consumes another lane's output only through `contracts/**` or a published artifact — never by reaching into its source tree.
5. **Additive-only within a lane.** Prefer new files over editing existing ones. Editing is allowed only inside owned paths.

## Branch & merge model
- `main` — protected, releasable. Only `integration` merges here.
- `integration` — daily merge target. Lanes merge here via PR.
- `lane/N/<phase>-<task>` — one branch per task, short-lived (< 1 day), rebased on `integration` before PR.
- **Merge train:** lanes merge to `integration` in fixed order L1 → L4 → L2 → L3 → L5 (dependency order), once per cycle. `integration` → `main` when the full gate passes.
- A lane NEVER merges another lane's branch. A lane NEVER rebases another lane's branch.

## Dependency order (why the merge train is ordered)
L1 (schemas) and L4 (record schemas) produce what everything validates against.
L2 (workflows) consumes L1 schemas. L3 (reconciler) consumes L1 + L5 access model.
L5 (access/infra) is independent at build time, integrates last.

## AI developer profile — write for this reader
Sonnet-4.6-class, low cost, no repo context, no judgment authority.
Every task MUST have: exact file paths, literal copy-pasteable commands, complete acceptance criteria,
a self-verify command whose output is unambiguous, and a STOP rule ("if X, do not proceed — open a blocker issue").
No task may require designing, choosing, or interpreting. If a task needs judgment, it belongs to L0.
