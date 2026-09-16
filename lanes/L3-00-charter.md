> **[SUPERSEDED — FD-B1-L3 2026-09-02]**
> This file has been superseded by L3-06-tasks.md. Do not execute tasks from this file.
> Authoritative plan: Code/implementation/lanes/L3-06-tasks.md

# L3-00 — CHARTER: Reconciler & Provisioning

> **REFERENCE ONLY** — FD-098 (2026-09-09): Task bodies superseded by L3-06-tasks.md. This file is a design-note reference. Do not execute task bodies from this file.

**Lane:** L3 — Reconciler & Provisioning
**Branch prefix:** `lane/3/*`
**Subsystems:** C (Reconciliation engine), D (Provisioning and scaffolding)
**Repository:** `control-plane`
**Authority:** subordinate to `Code/implementation/PARTITION.md` (FROZEN). Where this file and PARTITION.md appear to differ, PARTITION.md wins and the difference is a blocker.
**Spec of record:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines)

---

## 0. The one paragraph that governs every task in this lane

Spec Section 99.6, risk 6 (lines 9276–9294) names this lane's output the most dangerous code in the system:

> "Reconciliation auto-repair as the most dangerous code — a write-scope, org-admin automation whose bug loosens security or locks everyone out; **the reconciler is the highest-privilege identity in the system**"

The mitigation named in the same row is binding on every task here and is not open to interpretation: **detect-only first; repair classes enabled one at a time; the stricter-only rule enforced in code and tested; the reconciler's own credential in the top secrets tier with its compromise treated as a security incident.** Section 98.2 Phase 3 (lines 9006–9090) says the same thing operationally — *"Auto-repair is not built here … because auto-repair is the riskiest code in the system"* — and Section 98.3 (lines 9091–9108) defers Level 3 to early hardening. Therefore:

| Standing rule | Source | Consequence for this lane |
| --- | --- | --- |
| Auto-repair may only move the system toward the declared, **stricter** state | Invariant 81 (line 9558); Section 53.3 (lines 4700–4703) | Every repair-class task ships its stricter-only guard **and** a negative test proving a loosening repair is refused |
| Where actual is stricter than declared, raise Level 2 — never relax | Section 53.3 (4700–4703); AT-033 (line 9347) | No code path exists that relaxes a control |
| Reconciliation never modifies production runtime configuration, never modifies data, never rotates or writes secrets | Section 53.3 (4700–4703) | Enforced by credential scope (AT-110) *and* by code |
| Detect-and-block ships before any repair | Section 99.4 item 6 (lines 9248–9263); Section 98.2 Phase 3; Section 98.3 | Phase order in this lane is fixed: detect → block → repair, one repair class at a time |
| A run that finds nothing is a FAILED run | Section 53.1 seeded-canary rule (4653–4689); AT-102 (line 9351) | The canary check is built in the same task as the first run loop, never later |
| Fail closed for Blocking-class checks; fail open with an alert for Green-class checks | Section 64.2 (lines 5448–5468) | Every check declares its class in code; an unclassified check is refused by this lane's own validator |

---

## 1. Scope

### 1.1 In scope

**Subsystem C — Reconciliation engine.** Spec Section 99.2, line 9190:

> "| C | Reconciliation engine | Scheduled diff of declared versus actual GitHub state; graded responses at Levels 1–5 (Detect / Warn / Auto-repair / Block / Escalate); automatic expiry revocation; orphan detection at blocking severity; auto-repair only toward stricter declared state | L | A, B, D |"

Concretely, this lane builds:

1. The declared-versus-actual comparison set of Section 53.1 (lines 4653–4689) — 17 table rows plus 2 prose-declared Blocking rows from §53.1 — 19 comparison entries total. <!-- 19 per FD-061 (L3-01 authoritative); charter's prior 23 (which added 4 §40.1/D107 prose rows) is superseded. -->
2. The five graded response levels of Section 53.2 (lines 4690–4699).
3. The auto-repair rule and its stricter-only guard, Section 53.3 (lines 4700–4703).
4. The four-class drift severity scale and budget evaluation, Section 53.4 (lines 4704–4723).
5. The seeded canary and per-registry comparison counts, Section 53.1 (4653–4689), tested by AT-102 (line 9351).
6. The independent control verifier's assertion logic, Section 53.1 (4653–4689) — the logic only; its schedule and its separate credential are L5/L2 (see §4).
7. Automatic expiry revocation — assignment `end_date`, temporary access, exception expiry — Sections 53.1, 53.2 Level 3, 26.4 (lines 2526–2534), invariant 58 (line 9529).
8. Orphan detection over all 16 orphan types of Section 12.2 (lines 990–1011), at the declared severities, invariant 57 (line 9528).
9. The records-repository anchor: head-SHA and commit-count capture, descendant proof, signed-commit assertion — Section 40.1 / D107 (lines 3644–3686; D107 at line 10205).
10. The `control-plane/blocking-drift` check-run publisher, Section 11.3 (lines 860–875) and Section 40.1's check-run scope paragraph.
11. The control-loop gap procedure as executable steps, Section 53.7 (lines 4735–4745).
12. Run records, `external-cause` annotation, and `acknowledged_by` / `acknowledged_at` on every finding, Section 53.1 (4653–4689).

**Subsystem D — Provisioning and scaffolding.** Spec Section 99.2, line 9191:

> "| D | Provisioning and scaffolding | Create-product, add-person, change-role, remove-person operations: repo from template, Teams from registries, generated CODEOWNERS, branch protection, environments with scoped secrets, registration in every surface with zero hand-editing | L | A, B |"

Concretely, this lane builds the four scaffolding operations of Section 12.6 (lines 1098–1108), against the create-product flow of Section 19.1 (lines 1826–1882), the new-person lifecycle of Section 12.1 (lines 892–947), the exit lifecycle of Section 12.2 (lines 948–1012), the CODEOWNERS generation rules of Sections 11.3 and 17.3 (lines 860–875; 1668–1693), and the safe defaults of Section 64.1 (lines 5433–5447).

### 1.2 Explicitly out of scope for L3

| Not ours | Owner | Why |
| --- | --- | --- |
| Registry and product JSON Schemas, referential-integrity validators | L1 (`schemas/**`, `validators/registry/**`) | PARTITION.md row L1 |
| Drift-class *configuration values* and tolerances (they live in `os-health.yaml`) | L1 (`registries/**`) | Section 53.4 (4704–4723) puts class assignment in configuration; Section 52.6 (4613–4648) puts `os-health.yaml` in the registries |
| Any GitHub Actions workflow file, including the scheduled reconciliation trigger and the independent verifier's workflow | L2 (`.github/workflows/**`, `templates/workflows/**`) | PARTITION.md row L2 |
| The reusable workflow library and the digest invariant | L2 | Subsystem E |
| Record and event *schemas*, the record stores themselves, metrics | L4 (`schemas/records/**`, `metrics/**`, `tools/records/**`, all of `control-plane-records`) | PARTITION.md row L4 |
| The access model itself — org base Read, Teams-derived Write, branch-protection template content, secret tiers, ops-VM configuration, notification routing | L5 (`access/**`, `infra/**`, `ops-vm/**`, `notify/**`) | PARTITION.md row L5 |
| `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` | L0 | PARTITION.md row L0 |

**L3 never edits a foreign path.** A PR from `lane/3/*` touching anything outside §2 fails the lane-guard check with no exception (PARTITION.md rule 1).

---

## 2. Owned paths (exclusive)

```
reconciler/**
tools/provision/**
validators/drift/**
```

Nothing else. These three globs are copied verbatim from PARTITION.md line 19 and are frozen.

### 2.1 Internal layout this lane commits to

> **Layout per FD-B1-L3 (FD-045 superseded 2026-09-02).** The authoritative package tree is defined in `L3-06-tasks.md` (FD-B1-L3, 2026-09-02). This table reflects that authoritative layout; the charter's prior layout is superseded where they conflict.

| Path | Holds |
| --- | --- |
| `reconciler/README.md` | Lane-facing scope statement for subsystem C |
| `reconciler/SAFETY.md` | The standing safety contract (§0), transcribed with citations |
| `reconciler/CREDENTIAL-ENVELOPE.md` | The fifth-tier envelope and the AT-110 six-attempt negative test |
| `reconciler/PHASE1-ENTRY.md` | Phase 1 entry gate record |
| `reconciler/__init__.py` | Package marker (`__version__ = "0.1.0"`) |
| `reconciler/pyproject.toml` | Project metadata; `requires-python = "==3.12.*"` |
| `reconciler/requirements.in` | Unpinned dependency list |
| `reconciler/requirements.txt` | Hash-pinned dependencies (generated via `pip-compile --generate-hashes`) |
| `reconciler/model.py` | `DriftClass`, `Level`, `Finding` dataclass, `security_floor()` |
| `reconciler/loader.py` | Declared-state loader (reads registries via fixture or live adapter) |
| `reconciler/counts.py` | Per-registry comparison-count computation |
| `reconciler/orchestrator.py` | Run orchestrator: drives comparators, assembles `RunRecord` |
| `reconciler/api/__init__.py` | API client sub-package marker |
| `reconciler/api/client.py` | Read-only GitHub REST API client (no write methods) |
| `reconciler/api/tests/` | API client tests (includes `test_client_readonly.py`) |
| `reconciler/comparators/__init__.py` | Comparator sub-package marker |
| `reconciler/comparators/base.py` | Abstract `Comparator` base class |
| `reconciler/comparators/registry.py` | `@comparator` decorator and `COMPARATORS` registry |
| `reconciler/comparators/manifest.yaml` | Frozen Section 53.1 table — one row per comparator |
| `reconciler/comparators/section-53-1.frozen.md` | Spec-table snapshot for test assertion |
| `reconciler/comparators/tests/` | Per-comparator tests |
| `reconciler/repair/**` | Repair classes, one file per class, each with its stricter-only guard |
| `reconciler/canary.py` | Seeded-canary assertion and the zero-findings FAIL rule |
| `reconciler/anchor.py` | Records-repository head-SHA anchor and descendant proof |
| `reconciler/gap/**` | The Section 53.7 gap procedure |
| `reconciler/fixtures/` | Test fixture data mirroring the declared/actual registry shape |
| `reconciler/tests/` | Integration and unit tests |
| `tools/provision/README.md` | Lane-facing scope statement for subsystem D |
| `tools/provision/OPERATIONS.md` | The four operations and their enumerated required outputs |
| `tools/provision/cli.py` | `provision` CLI entry point (dry-run default) |
| `tools/provision/create_product.py` | `create-product` orchestrator |
| `tools/provision/add_person.py` | `add-person` orchestrator |
| `tools/provision/change_role.py` | `change-role` operation |
| `tools/provision/remove_person.py` | `remove-person` operation |
| `tools/provision/codeowners.py` | CODEOWNERS generator (human identities only) |
| `tools/provision/tests/` | Provisioning CLI tests |
| `validators/drift/README.md` | Lane-facing scope statement for the drift validators |
| `validators/drift/CLASSES.md` | The four drift classes and five levels, transcribed |
| `validators/drift/__init__.py` | Validator sub-package marker |
| `validators/drift/schema/` | JSON Schema definitions for drift findings and run records |
| `validators/drift/schema_check.py` | Schema validation runner |
| `validators/drift/verifier.py` | Independent control verifier entry point |
| `validators/drift/tests/` | Drift validator tests |

---

## 3. Subsystem mapping to Section 99.2

| Subsystem | Spec line | Complexity per 99.2 | Depends on (per 99.2) | Lane that supplies the dependency |
| --- | --- | --- | --- | --- |
| C — Reconciliation engine | 9190 | L (three to eight weeks) | A, B, D | A → L1 registries; B → L1 validators; D → L3 itself |
| D — Provisioning and scaffolding | 9191 | L (three to eight weeks) | A, B | A → L1 registries; B → L1 validators |

Section 99.2's dependency spine, line 9209: *"A (registries) → B (validation) → C (reconciliation) and D (provisioning)"*. This is why the merge train places L1 ahead of L3 (§6).

Section 99.2 also assigns two named build-surface tools partly to this lane:

| Named tool | Subsystem column in 99.2 | L3's share |
| --- | --- | --- |
| Draft-PR-only verification | J, C | The **C** half: the assertion that branch protection and CODEOWNERS still restrict the background machine account to draft pull requests, GitHub-side. Lives in `validators/drift/verifier/**`. The J half (cage, harness) is not this lane's and is not built in the Foundation tier. |
| Change-matrix scaffold | O | **Not ours.** Listed here only so no executor claims it: subsystem O is not in L3's mapping. |

---

## 4. What this lane consumes

### 4.1 From `contracts/**` (L0, frozen in Phase 0)

L3 codes against the frozen contracts and never edits them. A needed change is a Contract Change Request, never an edit (PARTITION.md rule 2).

| Contract L3 consumes | Why L3 needs it | Spec anchor |
| --- | --- | --- |
| The finding envelope (fields, including `acknowledged_by`, `acknowledged_at`, drift class, level, evidence, age) | Every check emits it | Section 53.1 (4653–4689) |
| The run-record envelope (including `external-cause`, per-registry comparison counts, canary result) | Every run writes one, clean or not | Section 53.1 (4653–4689) |
| The repair-record envelope | Level 3 writes one per repair | Section 53.2 (4690–4699); Section 26.4 (2526–2534) |
| The event names this lane emits | Emission points | Section 97.3 event taxonomy; enum declared in `platform.yaml` |
| The exact check-run name held at failure on product repositories | The blocking mechanism | Section 11.3 (860–875): `control-plane/blocking-drift` |
| The scaffolding-operation invocation contract (arguments in, artifacts out, exit codes) | So L2 workflows and L5 ops-VM schedules can call it | Sections 12.6 (1098–1108), 19.1 (1826–1882) |
| The reconciler entrypoint contract (arguments, exit codes, output location) | So L5 can schedule it off the ops VM and L2 can invoke the verifier | Section 94.7 (8550–8579) |

### 4.2 From Lane 1 (schemas and registries)

L3 reads L1 output **only** through `contracts/**` or a published artifact — never by reaching into L1's source tree (PARTITION.md rule 4).

| Consumed | Used for |
| --- | --- |
| `schemas/registry/**` — people, roles, assignments, topology, platform, exceptions, policies, os-health | Declared-side of every comparison |
| `schemas/product/**` — the Product Operating Contract, Section 15.1 | `product.yaml` assignments, lifecycle, environments, `restore_tested`, commitments, `infrastructure:` boundary |
| `validators/registry/**` outputs (pass/fail, not source) | L3 refuses to reconcile a registry that failed L1 validation — fail closed, Section 64.2 (5448–5468) |
| `os-health.yaml` drift-class assignments and tolerances | Class lookup, Section 53.4 (4704–4723). L3 **reads**; L1 owns the file |

### 4.3 From Lane 5 (access model)

Section 99.2 line 9202 gives subsystem L (access-control architecture) dependency `A, D` — L5 depends on L3's provisioning; L3 in turn reconciles against L5's declared access model. The seam is one-directional at build time and is mediated by `contracts/**`.

| Consumed from L5 | Used for |
| --- | --- |
| The branch-protection template (declared side) | Comparison row 5, Section 53.1; Section 11.3 checklist (860–875) |
| The environment configuration template and the deployment branch/tag policy | Comparison rows 7 and 8, Section 53.1; Section 33.4 (2887–2912) |
| The permission model — org base Read, Teams-derived Write, the person-class table | Comparison rows 1–3; Section 11.2 (839–859) |
| The five secret tiers and the reconciler credential's declared permission set and behavioural envelope | `reconciler/CREDENTIAL-ENVELOPE.md`; AT-110 (line 9439); Section 40.1 (3644–3686) |
| The ops-VM host identity and private-path requirement | The `expected source host` field of the behavioural envelope, Section 40.1 |
| The ruleset bypass-actor lists and their declared scopes | Comparison row 14 and prose row (b); Sections 53.1, 33.2, 40.1 / D89 (line 10182) |

### 4.4 From Lane 2 and Lane 4 (indirect)

| Consumed | From | Note |
| --- | --- | --- |
| The scheduled trigger that invokes the reconciler and the independent verifier | L2 workflows | L3 supplies the callable; L2 supplies the schedule. Section 94.7 (8550–8579): *"Reconciliation | Nightly and on registry change"* |
| Workflow template versions and the `workflows/*` tag→SHA resolution | L2 | Comparison rows 6 and 13, Section 53.1 |
| The records repository's default-branch head | L4 / `control-plane-records` | Read-only, for the anchor. L3 **never writes** `records/**` — AT-110 attempt 5 (line 9439) |
| Record-store write-freshness windows | L4 | Comparison row 15, Section 53.1 |

---

## 5. What this lane publishes

| Published artifact | Consumed by | Contract surface |
| --- | --- | --- |
| The reconciler entrypoint (callable, exit-coded) | L5 ops-VM schedule; L2 workflow trigger | `contracts/**` reconciler entrypoint contract |
| Drift findings and run records (written to the records repository through the declared write path, never by L3's own credential) | L4 metrics; the Founder view; SIG-02, SIG-03, SIG-05, SIG-13 | Finding and run-record envelopes in `contracts/**` |
| The `control-plane/blocking-drift` check run on product repositories | Branch protection required-status-check list (L5) | Section 11.3 (860–875) |
| Repair records | Section 26.4 repair-record lane (2526–2534); the gap procedure's enumeration step (53.7) | Repair-record envelope |
| The records-repository head-SHA anchor written into the control-plane repository | D107 (line 10205); the append-only proof | Anchor record shape in `contracts/**` |
| The four scaffolding CLIs | The DevOps-capability holder (Section 19.1, 1826–1882); the Founder or `platform-admin` holder (Section 12.1, 892–947) | Scaffolding-operation invocation contract |
| The generated CODEOWNERS content (human identities only) | Every product repository; the negative Phase 1 completion check | Sections 11.3, 17.3, 37.3 (3261–3268) |
| The independent control verifier's assertion library | L2's scheduled verifier workflow, run under a different credential | Section 53.1 (4653–4689) |
| The 16-type orphan report | Founder view product-attention dimension; SIG-05 | Section 12.2 (990–1011) |

---

## 6. Merge-train position

PARTITION.md line 35: **L1 → L4 → L2 → L3 → L5.** L3 is **fourth of five**.

| Rule | Binding text |
| --- | --- |
| Branch naming | `lane/3/<phase>-<task>`, one branch per task, short-lived (< 1 day) |
| Rebase | Rebased on `integration` before every PR |
| Target | PR to `integration` only. Never to `main`. Never merges or rebases another lane's branch |
| Cadence | Once per cycle, in train order, after L2 has merged and before L5 |
| Promotion | `integration` → `main` is L0's, when the full gate passes |

**Why fourth.** PARTITION.md line 40: *"L3 (reconciler) consumes L1 + L5 access model."* L1 and L4 land the schemas everything validates against; L2 lands the workflows that trigger L3's callable; L3 lands; L5 lands the access model and infra last. L3 therefore codes against L5's *declared* templates via `contracts/**` during the cycle and reconciles against L5's *merged* templates from the following cycle onward. An L3 task that cannot proceed without an unmerged L5 artifact is a blocker, not a reason to reach into `access/**`.

---

## 7. Spec sections this lane implements

### 7.1 Primary — the sections L3 is accountable for

| Spec section | Lines | What L3 builds from it | Owned path |
| --- | --- | --- | --- |
| 53. Reconciliation and the Drift Budget (whole) | 4649–4745 | The engine | `reconciler/**`, `validators/drift/**` |
| 53.1 Declared versus actual | 4653–4689 | 17 table rows + 2 prose Blocking rows = **19 §53.1 comparison entries**; seeded canary; per-registry comparison counts; independent control verifier; `external-cause`; `acknowledged_by`/`acknowledged_at` | `reconciler/checks/**`, `reconciler/canary/**`, `validators/drift/verifier/**` |
| 40.1 / D107 — four prose Blocking rows | 3644–3686; D107 at 10205 | 4 prose Blocking comparison entries (unsigned records-repo commit; non-descendant head; foreign check-run publisher; out-of-envelope credential run) — these rows are tracked as supplementary checks but are NOT counted in the **19 comparison entries** per FD-061 (L3-01 authoritative). <!-- Was "completing the 23 comparison entries" — superseded by FD-061. --> | `reconciler/checks/**` |
| 53.2 The five reconciliation levels | 4690–4699 | Level 1 Detect, 2 Warn, 3 Auto-repair, 4 Block, 5 Escalate | `reconciler/levels/**` |
| 53.3 The auto-repair rule | 4700–4703 | The stricter-only guard and its negative test | `reconciler/repair/**` |
| 53.4 Drift classes and the drift budget | 4704–4723 | Green / Amber / Red / Blocking classification and budget evaluation (Amber ≤ 2 per product; Red flat at 3 portfolio-wide) | `validators/drift/CLASSES.md`, `reconciler/levels/**` |
| 53.5 Reclassification authority | 4724–4727 | No informal downgrade path exists in code | `reconciler/levels/**` |
| 53.6 Calibration and closure quality | 4728–4734 | Closure records what changed and links evidence; recurrence-in-same-scope reopen | `reconciler/levels/**` |
| 53.7 The control-loop gap procedure | 4735–4745 | Replay expiries; diff-audit the window; re-run standing checks; Level 5 incident; `gap-window` marking; the ran-wrong branch | `reconciler/gap/**` |
| 12.2 Person exit lifecycle — the reconciliation block and the 16 orphan types | 948–1012 (orphan table 990–1011) | Orphan detection, prospective mode on `departing` | `reconciler/checks/**`, `tools/provision/remove-person/**` |
| 12.6 Scaffolding operations | 1098–1108 | The four operations | `tools/provision/**` |
| 19.1 Product creation | 1826–1882 | `create product` end to end, including the CONFIGURE checklist issue and the tracked-manual-step issues | `tools/provision/create-product/**` |
| 12.1 New person lifecycle | 892–947 | `add person`, including the onboarding checklist issue and `cross_review_shadow` registration | `tools/provision/add-person/**` |
| 64.1 Safe defaults | 5433–5447 | Provisioning defaults: private repos, protection at creation, no environment access, no third-party app access, `launch_status: pre-launch`, mandatory `end_date` for non-employees | `tools/provision/**` |
| 64.2 Fail-closed versus fail-open | 5448–5468 | Every check declares its class; unclassified is refused | `validators/drift/**` |
| 26.4 The registry-change lane (second and third paragraphs) | 2526–2534 | Level-3 repairs write under the reconciler credential and bypass the human owner-review lane; the canary-set-first staging rule for merged registry changes | `reconciler/repair/**` |

### 7.2 Secondary — sections L3 reads to build correctly but does not own

| Spec section | Lines | Why L3 reads it |
| --- | --- | --- |
| 11.1 GitHub permission semantics — verified, not assumed | 817–838 | Cross-Reviewers require Write; a Read-only reviewer fails silently — the comparison must detect it |
| 11.2 The permission model | 839–859 | Declared side of Team membership comparison |
| 11.3 Branch protection configuration, per repository | 860–875 | Comparison row 5; the `control-plane/blocking-drift` required check; CODEOWNERS human-identities-only rule |
| 11.4 Implementation dependencies — plan-tier facts | 876–887 | Environment required reviewers are Enterprise-only (D73, line 10156) — never assumed present |
| 17.3 The reviewer matrix / 17.4 Who changes ownership | 1668–1693 / 1694–1697 | CODEOWNERS generation source; matrix machine-validation against Teams |
| 33.4 Artifacts and environments | 2887–2912 | Comparison rows 7 and 8 |
| 37.3 Prohibited by architecture, not by policy | 3261–3268 | Draft-PR-only verification; CODEOWNERS never contains a machine identity; actor-gate removal is Blocking drift |
| 40.1 Five secret tiers | 3644–3686 | The reconciler credential's tier, permission set, behavioural envelope, check-run scope; D89 and D107 mechanics |
| 40.2 Boundary rules | 3687–3694 | Comparison row 9 — the `infrastructure:` boundary is verified by **attestation**, never by reconciliation reaching the provider |
| 52.6 Registry of control-plane files | 4613–4648 | Which artifact lives in which repository; twenty-nine entries |
| 94.7 Machine activity | 8550–8579 | Cadence: nightly and on registry change |
| 96.2 Pre-onboarding operating mode | 8720–8760 | A stub `product.yaml` is a legitimate declared state; AT-051 |
| 98.2 Foundation Phases 1–7 (Phase 1 and Phase 3 completion checks) | 9006–9090 | The reconciler credential's declared repair scope is the only machine write path on the control-plane repository |
| 98.3 Early hardening | 9091–9108 | Auto-repair sequencing |
| 99.2 The subsystem architecture | 9184–9231 | This lane's definition |
| 99.4 The minimal honest V1 | 9248–9263 | Item 6 — reconciliation v0 is detect and block only |
| 99.6 Top build risks | 9276–9294 | Risk 6 — §0 of this charter |

### 7.3 Acceptance tests this lane must make pass

| AT | Line | Domain | L3's obligation |
| --- | --- | --- | --- |
| AT-001 | 9305 | Extensibility | `create product` plus onboarding; no product list in any script L3 writes |
| AT-002 | 9306 | Extensibility | `add person`; reconciliation grants access |
| AT-008 | 9312 | Extensibility | Reconciliation revokes on the end date **without human action** |
| AT-017 | 9326 | Lifecycle | Exit lifecycle; orphan detection surfaces every unowned responsibility; blocking orphans cannot be dismissed unresolved |
| AT-018 | 9327 | Lifecycle | Temporary assignment expiry removed without human action |
| AT-021 | 9330 | Lifecycle | Permanent ownership change recorded as a decision; Founder-view notification generated |
| AT-032 | 9346 | Platform | Self-observability — the OS detects a failure in its own reconciliation |
| AT-033 | 9347 | Platform | **No auto-loosening** — a stricter-than-declared production control is raised for human review, never relaxed |
| AT-034 | 9348 | Platform | The reconciliation engine is core-resident machinery and is never removed |
| AT-036 | 9358 | Governance | A temporary access exception expires and is revoked with no human action |
| AT-037 | 9359 | Governance | An exception that cannot be auto-revoked becomes Blocking drift on its expiry date |
| AT-051 | 9373 | Governance | A breached pre-onboarding deadline surfaces as drift |
| AT-102 | 9351 | Platform | The seeded reconciliation canary — a zero-finding run is a **failed** run, raises SIG-13, triggers the gap procedure |
| AT-110 | 9439 | Access | The reconciler credential is provably bounded — six attempts fail, then a normal run still completes |

### 7.4 Invariants this lane enforces

| # | Line | Invariant | Where L3 enforces it |
| --- | --- | --- | --- |
| 44 | 9512 | Declared state is reconciled against actual platform state, and silent drift is not permitted | `reconciler/checks/**`, run record on every run |
| 53 | 9524 | New products are configuration plus onboarding, never platform redesign | `tools/provision/create-product/**` |
| 55 | 9526 | Ownership changes are declarative and take effect through reconciliation | `reconciler/checks/**` |
| 56 | 9527 | Role changes trigger capability, permission and assignment recalculation | `tools/provision/change-role/**` |
| 57 | 9528 | Departures trigger orphan detection, and blocking orphans cannot be dismissed unresolved | `reconciler/checks/**`, `tools/provision/remove-person/**` |
| 58 | 9529 | Temporary assignments carry a mandatory end date and expire without human action | `reconciler/repair/**` |
| 77 | 9554 | Every exception has an expiry; an exception without one is invalid | Expiry revocation and the AT-037 Blocking path |
| 79 | 9556 | New people, products and tools default to minimum privilege and draft state | `tools/provision/**` |
| 80 | 9557 | Every control is explicitly classified fail-closed or fail-open | `validators/drift/**` |
| 81 | 9558 | **Auto-repair may only move the system toward the declared, stricter state** | `reconciler/repair/**` stricter-only guard + negative test |

### 7.5 Health signals this lane feeds

| SIG | Line | Signal | Source column says |
| --- | --- | --- | --- |
| SIG-02 | 4531 | Stale assignment or allocation | Registries |
| SIG-03 | 4532 | Permission drift | **Reconciliation** |
| SIG-05 | 4534 | Orphan risk | Registries |
| SIG-13 | 4542 | Failed reconciliations | **Reconciliation** |

L3 emits SIG-03 and SIG-13 directly and supplies the detection that raises SIG-02 and SIG-05.

---

## 8. Definition of Done (lane level)

L3 is done when every row below is true and provable by the command in its right-hand column, run from the `control-plane` repository root on `integration`.

| # | Condition | Proof command |
| --- | --- | --- |
| D1 | All 19 comparison entries of Section 53.1 exist as checks, each declaring a drift class and a fail-closed/fail-open classification | `ls reconciler/checks | wc -l` prints `19`; `grep -Lq -e 'drift_class:' reconciler/checks/*` prints nothing | <!-- 19 per FD-061 (L3-01 authoritative); was 23 -->
| D2 | All five levels of Section 53.2 exist | `ls reconciler/levels | wc -l` prints `5` |
| D3 | The stricter-only guard exists and its negative test refuses a loosening repair | the lane's repair test suite exits `0` and its output contains `LOOSENING-REPAIR-REFUSED` |
| D4 | No repair class writes production runtime configuration, data, or secrets | `grep -rniE 'secret|rotate|production-runtime' reconciler/repair/` returns only lines inside refusal guards |
| D5 | The seeded canary is checked on every run and a zero-finding run fails | canary test suite exits `0` and prints `ZERO-FINDINGS-RUN-FAILED` |
| D6 | Per-registry comparison counts are written on every run | run-record fixture contains a `comparison_counts` block |
| D7 | All 16 orphan types of Section 12.2 are detected at their declared severities | orphan test suite exits `0` and prints `ORPHAN-TYPES=16` |
| D8 | All four scaffolding operations exist with their enumerated outputs | `ls tools/provision | grep -c -E 'create-product|add-person|change-role|remove-person'` prints `4` |
| D9 | The CODEOWNERS generator emits human identities only, proven negatively | codeowners test suite exits `0` and prints `MACHINE-IDENTITY-REJECTED` |
| D10 | The independent control verifier's assertions exist under `validators/drift/verifier/` and reference no ops-VM-writable path | `ls validators/drift/verifier | wc -l` is ≥ 1; `grep -rn 'ops-vm' validators/drift/verifier/` returns nothing |
| D11 | AT-110's six negative attempts are encoded as an executable checklist | `grep -c '^- \[ \] attempt' reconciler/CREDENTIAL-ENVELOPE.md` prints `6` |
| D12 | The gap procedure's five steps plus the ran-wrong branch exist | `ls reconciler/gap | wc -l` is ≥ 1; `grep -c 'gap-window' reconciler/gap/*` is ≥ 1 |
| D13 | No file outside the three owned globs was changed by any `lane/3/*` branch | `git diff --name-only origin/integration...HEAD | grep -vE '^(reconciler/|tools/provision/|validators/drift/)'` prints nothing |
| D14 | Every task in every L3 phase file has a merged PR to `integration` | `gh pr list --state merged --search "head:lane/3/"` lists them |

---

## 9. Charter-phase tasks

**Preconditions for every task below.** The executor works from the `control-plane` repository root, on one branch at a time, with `origin/integration` fetched. Run this once before starting any task:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
git fetch origin
git rev-parse --verify origin/integration
```

If `git rev-parse` fails, STOP and file a blocker (§9.7).

**All six tasks touch disjoint files.** Each creates its own branch from `origin/integration` and opens its own PR. Do not wait for a sibling PR to merge unless a task's Dependencies row says to.

---

### L3-00-01 — Create the three owned-path skeletons

| Field | Value |
| --- | --- |
| Task id | `L3-00-01` |
| Size | S |
| Dependencies | none |
| Files created | `reconciler/README.md`, `tools/provision/README.md`, `validators/drift/README.md` |

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -e
git fetch origin
git checkout -B lane/3/00-t01 origin/integration
mkdir -p reconciler tools/provision validators/drift

cat > reconciler/README.md <<'EOF'
# reconciler/ — Subsystem C, Reconciliation engine

Owned exclusively by Lane 3 (`lane/3/*`). Source of truth for scope:
Code/implementation/PARTITION.md line 19, and MasterSpec v4.0 Section 99.2 line 9190.

Scheduled diff of declared versus actual GitHub state; graded responses at
Levels 1-5 (Detect / Warn / Auto-repair / Block / Escalate); automatic expiry
revocation; orphan detection at blocking severity; auto-repair only toward
stricter declared state.

Read reconciler/SAFETY.md before changing anything in this directory.
EOF

cat > tools/provision/README.md <<'EOF'
# tools/provision/ — Subsystem D, Provisioning and scaffolding

Owned exclusively by Lane 3 (`lane/3/*`). Source of truth for scope:
Code/implementation/PARTITION.md line 19, and MasterSpec v4.0 Section 99.2 line 9191.

Create-product, add-person, change-role, remove-person operations: repo from
template, Teams from registries, generated CODEOWNERS, branch protection,
environments with scoped secrets, registration in every surface with zero
hand-editing.

Safe defaults are binding here: MasterSpec v4.0 Section 64.1, lines 5433-5447.
EOF

cat > validators/drift/README.md <<'EOF'
# validators/drift/ — drift validators and the independent control verifier

Owned exclusively by Lane 3 (`lane/3/*`). Source of truth for scope:
Code/implementation/PARTITION.md line 19.

Holds: the four drift classes and five reconciliation levels as fixed
vocabulary (CLASSES.md); the independent control verifier's assertion logic
(verifier/); local shape checks for findings this lane emits (finding-schema/).

Does NOT hold registry schemas or registry validators - those are Lane 1
(`validators/registry/**`).
EOF

git add reconciler/README.md tools/provision/README.md validators/drift/README.md
git commit -m "L3-00-01: create owned-path skeletons for reconciler, provisioning and drift validators"
git push -u origin lane/3/00-t01
gh pr create --base integration --head lane/3/00-t01 --title "L3-00-01: owned-path skeletons" --body "Lane 3 charter phase. Creates reconciler/, tools/provision/, validators/drift/ README scope statements. Touches no foreign path."
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Exactly three files created | `git diff --name-only origin/integration...HEAD \| wc -l` | `3` |
| A2 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |
| A3 | Each README names its subsystem and its spec line | `grep -c 'Section 99.2' reconciler/README.md tools/provision/README.md` | `reconciler/README.md:1` and `tools/provision/README.md:1` |
| A4 | The drift README disclaims L1's paths | `grep -c 'validators/registry' validators/drift/README.md` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
echo "--- files ---"; git diff --name-only origin/integration...HEAD
echo "--- foreign ---"; git diff --name-only origin/integration...HEAD | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' || echo NONE
echo "--- count ---"; git diff --name-only origin/integration...HEAD | wc -l
```

Expected output, exactly:

```
--- files ---
reconciler/README.md
tools/provision/README.md
validators/drift/README.md
--- foreign ---
NONE
--- count ---
3
```

**STOP rule.** If `--- foreign ---` prints anything other than `NONE`, or `--- count ---` prints anything other than `3`: do not push, do not open a PR, run `git reset --hard origin/integration`, and file a blocker using the template in §9.7 with `TASK: L3-00-01` and `SYMPTOM:` set to the literal output.

---

### L3-00-02 — Write the standing safety contract

| Field | Value |
| --- | --- |
| Task id | `L3-00-02` |
| Size | S |
| Dependencies | `L3-00-01` (merged) |
| File created | `reconciler/SAFETY.md` |

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -e
git fetch origin
git checkout -B lane/3/00-t02 origin/integration

cat > reconciler/SAFETY.md <<'EOF'
# reconciler/SAFETY.md - standing safety contract

Binding on every change under reconciler/. Not advisory.

MasterSpec v4.0 Section 99.6 risk 6 (lines 9276-9294): the reconciler is the
highest-privilege identity in the system, and auto-repair is the most
dangerous code in it.

## Rules

- [ ] R1 Auto-repair may only move the system toward the declared, stricter state.
      Source: invariant 81 (line 9558); Section 53.3 (lines 4700-4703).
- [ ] R2 Where actual state is stricter than declared, raise Level 2 for human
      judgment. Never relax. Source: Section 53.3; AT-033 (line 9347).
- [ ] R3 Reconciliation never modifies production runtime configuration, never
      modifies data, and never rotates or writes secrets. Source: Section 53.3.
- [ ] R4 Detect and block ship before any repair; repair classes are enabled one
      at a time. Source: Section 99.4 item 6 (lines 9248-9263); Section 98.2
      Phase 3 (lines 9006-9090); Section 98.3 (lines 9091-9108).
- [ ] R5 A run that reports zero findings, canary included, is a FAILED run.
      Source: Section 53.1 seeded-canary rule (lines 4653-4689); AT-102 (line 9351).
- [ ] R6 Blocking-class checks fail closed; Green-class checks fail open with an
      alert. An unclassified check is refused. Source: Section 64.2 (lines
      5448-5468); invariant 80 (line 9557).
- [ ] R7 The reconciler writes no record store. records/** and events/** live in
      the records repository under the records-writer credential.
      Source: Section 40.1 (lines 3644-3686), D89 (line 10182); AT-110 attempt 5.
- [ ] R8 A repair class discovered to have written incorrect state is Level 5:
      freeze the class, enumerate its repairs in the window, revert or
      human-confirm each, mark the window's records gap-window.
      Source: Section 53.7 (lines 4735-4745); Section 53.2 (lines 4690-4699).

## Change rule

A pull request touching reconciler/repair/ that does not tick R1, R2 and R3 in
its description is rejected. A new repair class ships with a negative test that
proves a loosening repair is refused.
EOF

git add reconciler/SAFETY.md
git commit -m "L3-00-02: standing safety contract for the highest-privilege identity"
git push -u origin lane/3/00-t02
gh pr create --base integration --head lane/3/00-t02 --title "L3-00-02: reconciler safety contract" --body "Transcribes MasterSpec Section 99.6 risk 6, Section 53.3, invariants 80 and 81, AT-033, AT-102, AT-110 into a binding checklist. Eight rules R1-R8."
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Exactly eight rules | `grep -c '^- \[ \] R' reconciler/SAFETY.md` | `8` |
| A2 | Rules are numbered R1..R8 with no gap | `grep -o '^- \[ \] R[0-9]' reconciler/SAFETY.md \| tr -d '\- [] '` | `R1` `R2` `R3` `R4` `R5` `R6` `R7` `R8` on eight lines |
| A3 | The stricter-only rule cites invariant 81 | `grep -c 'invariant 81' reconciler/SAFETY.md` | `1` |
| A4 | The zero-findings rule cites AT-102 | `grep -c 'AT-102' reconciler/SAFETY.md` | `1` |
| A5 | Only one file changed | `git diff --name-only origin/integration...HEAD` | `reconciler/SAFETY.md` |

**SELF-VERIFY**

```bash
set -euo pipefail
echo "RULES=$(grep -c '^- \[ \] R' reconciler/SAFETY.md)"
echo "INV81=$(grep -c 'invariant 81' reconciler/SAFETY.md)"
echo "AT102=$(grep -c 'AT-102' reconciler/SAFETY.md)"
echo "FILES=$(git diff --name-only origin/integration...HEAD | wc -l)"
```

Expected output, exactly:

```
RULES=8
INV81=1
AT102=1
FILES=1
```

**STOP rule.** If any value differs from the expected output above: do not push, run `git reset --hard origin/integration`, and file a blocker using §9.7 with `TASK: L3-00-02`. Do not edit the rule text to make the count match — the count is derived from the spec, and a mismatch means the transcription is wrong.

---

### L3-00-03 — Transcribe the drift classes and reconciliation levels

| Field | Value |
| --- | --- |
| Task id | `L3-00-03` |
| Size | S |
| Dependencies | `L3-00-01` (merged) |
| File created | `validators/drift/CLASSES.md` |

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -e
git fetch origin
git checkout -B lane/3/00-t03 origin/integration

cat > validators/drift/CLASSES.md <<'EOF'
# Drift classes and reconciliation levels - fixed vocabulary

MasterSpec v4.0 Section 53.4 (lines 4704-4723) states there is exactly one
drift severity scale, used everywhere, and that no other severity vocabulary
exists anywhere in this system. This file is that vocabulary. It is not
extended by any lane.

## The four drift classes (Section 53.4, lines 4704-4723)

| Class | Meaning | Response time | Who acts | Blocks work |
| --- | --- | --- | --- | --- |
| Green | Within tolerance; recorded only | None | Nobody | No |
| Amber | Real but non-urgent; scheduled remediation | Next planning cycle, H2 | Owner | No |
| Red | Material risk to security, reliability or continuity | Within 2 business days | Owner plus Team Lead | No, but visible on the Founder view |
| Blocking | Unsafe to proceed | Immediate | Team Lead or escalation role | Yes - CI or deployment path blocked |

Retired vocabulary maps here exactly once: dangerous drift is Blocking,
correctable drift is auto-repairable (Level 3), informational drift is Level 1.

## The five reconciliation levels (Section 53.2, lines 4690-4699)

| Level | Behaviour | Applies to |
| --- | --- | --- |
| Level 1 - Detect | Record the finding with evidence and age. No notification. | Green-class drift |
| Level 2 - Warn | Raise on the health report and notify the owner. No block. | Amber-class drift |
| Level 3 - Auto-repair | Reconcile actual back to declared automatically, then record the repair. | Safe, idempotent, reversible repairs only |
| Level 4 - Block | Fail CI or block the deployment path until resolved. | Blocking-class drift |
| Level 5 - Escalate | Create an incident and notify the escalation role, then the Founder if unresolved within its response time. | Production environment drift, credential exposure, repeated failed auto-repair, a repair class found to have written incorrect state, the reconciliation job itself failing |

## Non-negotiables attached to this vocabulary

- Security drift and production environment drift are never classified below
  Red, regardless of apparent impact. (Section 53.4)
- Class assignment lives in configuration and is reviewable; it is not decided
  ad hoc during an incident. The configuration file is os-health.yaml, owned by
  Lane 1. Lane 3 reads it and never writes it. (Sections 53.4, 52.6 lines 4613-4648)
- Reclassifying a finding downward requires the same authority as approving an
  exception for it and is recorded as a decision. There is no informal path from
  Red to Amber. (Section 53.5, lines 4724-4727)
- Blocking-class checks fail closed; Green-class checks fail open with an alert.
  (Section 64.2, lines 5448-5468)
EOF

git add validators/drift/CLASSES.md
git commit -m "L3-00-03: transcribe the four drift classes and five reconciliation levels"
git push -u origin lane/3/00-t03
gh pr create --base integration --head lane/3/00-t03 --title "L3-00-03: drift classes and reconciliation levels" --body "Fixed vocabulary from MasterSpec Sections 53.2, 53.4, 53.5, 64.2. Four classes, five levels. No other severity vocabulary exists."
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Exactly four class rows | `grep -cE '^\| (Green|Amber|Red|Blocking) \|' validators/drift/CLASSES.md` | `4` |
| A2 | Exactly five level rows | `grep -c '^| Level [1-5] ' validators/drift/CLASSES.md` | `5` |
| A3 | The os-health.yaml ownership disclaimer is present | `grep -c 'owned by Lane 1' validators/drift/CLASSES.md` | `1` |
| A4 | The no-informal-downgrade rule is present | `grep -c 'no informal path from' validators/drift/CLASSES.md` | `1` |
| A5 | Only one file changed | `git diff --name-only origin/integration...HEAD \| wc -l` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
echo "CLASSES=$(grep -cE '^\| (Green|Amber|Red|Blocking) \|' validators/drift/CLASSES.md)"
echo "LEVELS=$(grep -c '^| Level [1-5] ' validators/drift/CLASSES.md)"
echo "L1OWN=$(grep -c 'owned by Lane 1' validators/drift/CLASSES.md)"
echo "FILES=$(git diff --name-only origin/integration...HEAD | wc -l)"
```

Expected output, exactly:

```
CLASSES=4
LEVELS=5
L1OWN=1
FILES=1
```

**STOP rule.** If `CLASSES` is not `4` or `LEVELS` is not `5`: the transcription is wrong. Do not push. Run `git reset --hard origin/integration` and file a blocker using §9.7 with `TASK: L3-00-03`. Do not invent a fifth class or a sixth level — Section 53.4 states no other severity vocabulary exists.

---

### L3-00-04 — Enumerate the four scaffolding operations

| Field | Value |
| --- | --- |
| Task id | `L3-00-04` |
| Size | M |
| Dependencies | `L3-00-01` (merged) |
| File created | `tools/provision/OPERATIONS.md` |

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -e
git fetch origin
git checkout -B lane/3/00-t04 origin/integration

cat > tools/provision/OPERATIONS.md <<'EOF'
# The four scaffolding operations

MasterSpec v4.0 Section 12.6 (lines 1098-1108): "Conceptual operations,
implemented as scripts in the control-plane repository. Not an application."

Binding rule from the same section: "No ordinary personnel or product change
should require hand-editing files across twenty repositories. If it does, the
scaffolding is incomplete and that is a platform defect."

## OP-1 create product

Executor: a DevOps-capability holder. Trigger: the scaffolding request issue
opened automatically by the Founder's decision record (Section 19.1, lines
1826-1882). Creation never depends on a remembered conversation.

- [ ] out-1 repository or repository set from the standard template
- [ ] out-2 product.yaml at current contract_version
- [ ] out-3 GitHub Team
- [ ] out-4 CODEOWNERS generated from assignments, human identities only
- [ ] out-5 branch protection from template
- [ ] out-6 environments: development, staging, production
- [ ] out-7 CI workflows consuming reusable workflows by pinned tag
- [ ] out-8 verification/ skeleton
- [ ] out-9 local environment contract - the eight commands
- [ ] out-10 health, version and metrics endpoints
- [ ] out-11 alert channel and support intake mailbox, or tracked manual-step issues
- [ ] out-12 registration: portfolio board, Grafana, Scorecard, DevLake, dependency graph
- [ ] out-13 a CONFIGURE checklist issue enumerating every CONFIGURE item of Section 19.1

Safe defaults, binding (Section 64.1, lines 5433-5447): repositories private;
branch protection applied from template at creation; no environment access; no
third-party app access; launch_status pre-launch; production environment created
without secrets and without approvers until explicitly configured.

## OP-2 add person

Executor: the Founder or a holder of the platform-admin capability; the
organisation invitation itself requires organisation Owner rights (Section 12.1,
lines 892-947).

- [ ] out-1 people.yaml entry
- [ ] out-2 organisation invitation
- [ ] out-3 Team membership per assignments
- [ ] out-4 capability grants, explicit and never inherited wholesale
- [ ] out-5 AI runtime assignment honouring per-product ai_restrictions
- [ ] out-6 onboarding checklist issue
- [ ] out-7 registration in the review network view

Safe defaults, binding (Section 64.1): minimum privileges; no production access;
no environment access; no production-approval capability. Non-employees:
end_date mandatory, scope mandatory, organisation-wide read not granted.

## OP-3 change role

- [ ] out-1 role update
- [ ] out-2 capability recalculation
- [ ] out-3 permission recalculation
- [ ] out-4 reviewer matrix reassessment
- [ ] out-5 ownership reassessment prompt
- [ ] out-6 incident responder reassessment
- [ ] out-7 dashboard update

## OP-4 remove person

- [ ] out-1 access revocation
- [ ] out-2 Team removal
- [ ] out-3 environment access revocation
- [ ] out-4 AI runtime deactivation
- [ ] out-5 reviewer matrix recalculation
- [ ] out-6 orphan detection over all 16 orphan types (Section 12.2, lines 990-1011)
- [ ] out-7 an exit record

Prospective mode: orphan detection runs immediately when availability becomes
departing, against the declared end_date, emitting the transfer worklist
(Section 12.2). Temporary-person expiry is an exit and triggers the same exit
record and orphan scan.

## Build order

Section 98.2 Phase 3 (lines 9006-9090) ships Scaffolding v0 - OP-1 and OP-2 -
because a portfolio of eight products crosses the pays-for-itself threshold
immediately (Section 99.4 item 3). Section 98.3 (lines 9091-9108) places OP-3
and OP-4 in early hardening: "the rest follow the first role change and the
first departure".
EOF

git add tools/provision/OPERATIONS.md
git commit -m "L3-00-04: enumerate create-product, add-person, change-role and remove-person outputs"
git push -u origin lane/3/00-t04
gh pr create --base integration --head lane/3/00-t04 --title "L3-00-04: the four scaffolding operations" --body "Enumerates the required outputs of each of the four Section 12.6 operations, with Section 19.1 and 12.1 detail and Section 64.1 safe defaults. Build order per Sections 98.2 and 98.3."
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Exactly four operations | `grep -c '^## OP-' tools/provision/OPERATIONS.md` | `4` |
| A2 | create product enumerates 13 outputs | `sed -n '/^## OP-1/,/^## OP-2/p' tools/provision/OPERATIONS.md \| grep -c '^- \[ \] out-'` | `13` |
| A3 | add person enumerates 7 outputs | `sed -n '/^## OP-2/,/^## OP-3/p' tools/provision/OPERATIONS.md \| grep -c '^- \[ \] out-'` | `7` |
| A4 | change role enumerates 7 outputs | `sed -n '/^## OP-3/,/^## OP-4/p' tools/provision/OPERATIONS.md \| grep -c '^- \[ \] out-'` | `7` |
| A5 | remove person enumerates 7 outputs | `sed -n '/^## OP-4/,/^## Build order/p' tools/provision/OPERATIONS.md \| grep -c '^- \[ \] out-'` | `7` |
| A6 | The 16-orphan-type reference is present | `grep -c '16 orphan types' tools/provision/OPERATIONS.md` | `1` |
| A7 | Only one file changed | `git diff --name-only origin/integration...HEAD \| wc -l` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
echo "OPS=$(grep -c '^## OP-' tools/provision/OPERATIONS.md)"
echo "OP1=$(sed -n '/^## OP-1/,/^## OP-2/p' tools/provision/OPERATIONS.md | grep -c '^- \[ \] out-')"
echo "OP2=$(sed -n '/^## OP-2/,/^## OP-3/p' tools/provision/OPERATIONS.md | grep -c '^- \[ \] out-')"
echo "OP3=$(sed -n '/^## OP-3/,/^## OP-4/p' tools/provision/OPERATIONS.md | grep -c '^- \[ \] out-')"
echo "OP4=$(sed -n '/^## OP-4/,/^## Build order/p' tools/provision/OPERATIONS.md | grep -c '^- \[ \] out-')"
echo "FILES=$(git diff --name-only origin/integration...HEAD | wc -l)"
```

Expected output, exactly:

```
OPS=4
OP1=13
OP2=7
OP3=7
OP4=7
FILES=1
```

**STOP rule.** If any count differs: do not push, run `git reset --hard origin/integration`, and file a blocker using §9.7 with `TASK: L3-00-04` and the literal output. Do not add or remove an output line to make a count match — the outputs are enumerated by Sections 12.6, 19.1 and 12.1 and are not this task's to choose.

---

### L3-00-05 — Transcribe the declared-versus-actual comparison set

| Field | Value |
| --- | --- |
| Task id | `L3-00-05` |
| Size | M |
| Dependencies | `L3-00-01` (merged), `L3-00-03` (merged — supplies the class vocabulary) |
| File created | `reconciler/COMPARISON-SET.md` |

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -e
git fetch origin
git checkout -B lane/3/00-t05 origin/integration

cat > reconciler/COMPARISON-SET.md <<'EOF'
# The comparison set - declared versus actual

MasterSpec v4.0 Section 53.1 (lines 4653-4689). Nineteen entries per FD-061
(L3-01 authoritative; charter's prior 23 which included 4 §40.1/D107 prose rows
is superseded). One check file under reconciler/checks/ per entry. Class
vocabulary is fixed by validators/drift/CLASSES.md.

## Table rows (Section 53.1, lines 4653-4689)

| # | Declared in | Compared against | On mismatch |
| --- | --- | --- | --- |
| C-RECON-SET-1-01 | people.yaml | GitHub organisation membership | Alert; block on removal drift |
| C-RECON-SET-1-02 | people.yaml capabilities | Team membership implying authority | Alert |
| C-RECON-SET-1-03 | product.yaml assignments | GitHub Team membership | Fail CI on the affected repository |
| C-RECON-SET-1-04 | product.yaml assignments | CODEOWNERS | Regenerate; alert if hand-edited |
| C-RECON-SET-1-05 | Branch protection template | Actual branch protection | Alert immediately; block deployment on the affected repository |
| C-RECON-SET-1-06 | Workflow template version | Actual workflow file | Alert; flag platform_compatibility as drifted |
| C-RECON-SET-1-07 | Environment configuration template | Actual environments | Alert |
| C-RECON-SET-1-08 | Environment deployment branch and tag policy | Actual environment configuration | Alert immediately; block deployment on the affected repository |
| C-RECON-SET-1-09 | Declared infrastructure boundary (Section 40.2) | The latest provider-side attestation record | Blocking past its attestation window |
| C-RECON-SET-1-10 | product.yaml lifecycle | Renovate, monitoring and CI configuration | Auto-repair where safe; alert otherwise |
| C-RECON-SET-1-11 | Assignment end_date | Current Team membership | Auto-revoke expired access |
| C-RECON-SET-1-12 | Declared dependency | Shared service registry | Fail CI on unknown dependency |
| C-RECON-SET-1-13 | platform.yaml workflow versions | The commit SHA each workflows/* tag currently resolves to | Blocking on any change |
| C-RECON-SET-1-14 | Renovate bypass ruleset | The ruleset carrying the diff-path status check | Blocking where that ruleset names any bypass actor |
| C-RECON-SET-1-15 | Declared write-freshness window per record store (Section 97.2) | Latest commit timestamp on the store's path | Amber; Blocking for events/, records/deployments/ and records/uat/ |
| C-RECON-SET-1-16 | Production-restore record (Section 44.5) | Recorded integrity_check result and named verifier | Red where either is absent |
| C-RECON-SET-1-17 | product.yaml restore_tested | Newest passing record in records/restore-tests/ | Blocking |

## Prose-declared Blocking rows

| # | Condition | Source |
| --- | --- | --- |
| C-RECON-SET-1-18 | A workflow-file change pushed by a machine identity, regardless of the change's content | Section 53.1, lines 4653-4689 |
| C-RECON-SET-1-19 | A commit authored or committed by any identity other than the declared bypass actor, on a branch that merges under that actor's bypass | Section 53.1; Section 33.2 |

<!-- Entries C-RECON-SET-1-20 through C-RECON-SET-1-23 (§40.1/D107 prose rows:
     unsigned records-repo commit; non-descendant head; foreign check-run publisher;
     out-of-envelope credential run) are removed from the comparison-set count per
     FD-061 (19 per FD-061; L3-01 authoritative). These conditions remain as
     supplementary checks in reconciler/checks/ but are not part of the 19-entry set. -->

## Run-level obligations, not comparison entries

- The seeded canary must be found on every run. A run reporting zero findings,
  canary included, is a FAILED run, raises SIG-13, and triggers the gap
  procedure. (Section 53.1; AT-102, line 9351)
- Every run records its per-registry comparison counts, so a silently narrowed
  comparison is itself visible drift. (Section 53.1)
- Every run writes its result, and a clean run is recorded as clean. Silent
  drift is not permitted. (Section 53.1; invariant 44, line 9512)
- A failure caused by an acknowledged external outage is annotated
  external-cause on the run record rather than raised as raw Red, and the run is
  re-executed once the dependency recovers. (Section 53.1)
- Every drift finding carries acknowledged_by and acknowledged_at, written by
  the first responder who claims it. (Section 53.1)

## Boundary note on C09

Section 40.2 (lines 3687-3694): reconciliation compares declared state against
GitHub state and never leaves it. The provider side is verified by attestation,
not by reconciliation. C09 checks the attestation record's presence, date and
result - it never reaches a cloud provider.
EOF

git add reconciler/COMPARISON-SET.md
git commit -m "L3-00-05: transcribe the 19-entry declared-versus-actual comparison set (FD-061)"
git push -u origin lane/3/00-t05
gh pr create --base integration --head lane/3/00-t05 --title "L3-00-05: the comparison set" --body "Seventeen table rows from MasterSpec Section 53.1 plus two prose-declared Blocking rows from Section 53.1. Nineteen entries, C01-C19, per FD-061 (L3-01 authoritative), plus five run-level obligations."
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Exactly 19 numbered entries | `grep -c '^| C-RECON-SET-1-[0-9][0-9] ' reconciler/COMPARISON-SET.md` | `19` | <!-- 19 per FD-061 (L3-01 authoritative); was 23 --> |
| A2 | Numbering is C-RECON-SET-1-01..C-RECON-SET-1-19 with no gap and no duplicate | `grep -o '^| C-RECON-SET-1-[0-9][0-9] ' reconciler/COMPARISON-SET.md \| tr -d '\| ' \| sort \| uniq \| wc -l` | `19` | <!-- 19 per FD-061 --> |
| A3 | Seventeen entries are table rows | `sed -n '/^## Table rows/,/^## Prose-declared/p' reconciler/COMPARISON-SET.md \| grep -c '^| C-RECON-SET-1-[0-9][0-9] '` | `17` |
| A4 | Two entries are prose-declared | `sed -n '/^## Prose-declared/,/^## Run-level/p' reconciler/COMPARISON-SET.md \| grep -c '^| C-RECON-SET-1-[0-9][0-9] '` | `2` | <!-- 19 per FD-061; was 6 (included 4 §40.1/D107 rows) --> |
| A5 | The C09 attestation boundary note is present | `grep -c 'never reaches a cloud provider' reconciler/COMPARISON-SET.md` | `1` |
| A6 | The canary obligation is present | `grep -c 'FAILED run' reconciler/COMPARISON-SET.md` | `1` |
| A7 | Only one file changed | `git diff --name-only origin/integration...HEAD \| wc -l` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
echo "TOTAL=$(grep -c '^| C-RECON-SET-1-[0-9][0-9] ' reconciler/COMPARISON-SET.md)"
echo "UNIQUE=$(grep -o '^| C-RECON-SET-1-[0-9][0-9] ' reconciler/COMPARISON-SET.md | tr -d '| ' | sort | uniq | wc -l)"
echo "TABLE=$(sed -n '/^## Table rows/,/^## Prose-declared/p' reconciler/COMPARISON-SET.md | grep -c '^| C-RECON-SET-1-[0-9][0-9] ')"
echo "PROSE=$(sed -n '/^## Prose-declared/,/^## Run-level/p' reconciler/COMPARISON-SET.md | grep -c '^| C-RECON-SET-1-[0-9][0-9] ')"
echo "FILES=$(git diff --name-only origin/integration...HEAD | wc -l)"
```

Expected output, exactly:

```
TOTAL=19
UNIQUE=19
TABLE=17
PROSE=2
FILES=1
```

<!-- 19 per FD-061 (L3-01 authoritative). TOTAL and PROSE were 23 and 6 before FD-061. -->

**STOP rule.** If `TOTAL` and `UNIQUE` differ, an id is duplicated — fix the duplicate id only, then re-run SELF-VERIFY. If any other value differs from expected: do not push, run `git reset --hard origin/integration`, and file a blocker using §9.7 with `TASK: L3-00-05` and the literal output. Never add a twentieth entry — a new comparison row is a spec change and belongs to L0. <!-- Per FD-061 the limit is 19, not 23. -->

---

### L3-00-06 — Record the reconciler credential envelope and the AT-110 negative test

| Field | Value |
| --- | --- |
| Task id | `L3-00-06` |
| Size | M |
| Dependencies | `L3-00-01` (merged), `L3-00-02` (merged — supplies the safety contract this file operationalises) |
| File created | `reconciler/CREDENTIAL-ENVELOPE.md` |

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -e
git fetch origin
git checkout -B lane/3/00-t06 origin/integration

cat > reconciler/CREDENTIAL-ENVELOPE.md <<'EOF'
# The reconciler credential - tier, scope, envelope and proof

MasterSpec v4.0 Section 40.1 (lines 3644-3686) places the reconciler credential
in the fifth secrets tier, on the machine-credential store of the host that uses
it. Section 99.6 risk 6 (lines 9276-9294) names it the highest-privilege
identity in the system.

## Tier and store

Tier: Control plane (fifth). Location: machine-credential store on the
operations VM. Form: a least-privilege GitHub App or fine-grained PAT.
Rotation: on a schedule; initial value quarterly (Section 40.1).
A secret never moves down a tier.

The exact permission set is published in the credential's operational asset
inventory entry and in Section 40.1 - "so that over-scoping is visible on the
page rather than latent in the provisioning". Lane 5 owns the inventory entry;
Lane 3 reads it.

## Declared write scope

Section 98.2 Phase 1 completion check (lines 9006-9090): on the control-plane
repository, "the reconciler credential's declared repair scope (Section 26.4) is
the ONLY machine write path admitted", and a reconciler write outside its
declared scope is Blocking drift.

Section 40.1 check-run scope: the credential additionally holds check-run write
on product repositories, used for exactly one named check. A check run carries
status only - it writes no repository content, approves nothing, and satisfies
no gate a human is required to satisfy.

## Behavioural envelope (Section 40.1)

Four declared components; a run outside the envelope is Blocking drift (C23):

- [ ] env-1 a required signed run record naming the scheduled trigger
- [ ] env-2 a run-count ceiling per day - calibrated configuration, initial
      value twice the scheduled run count, recalibrated whenever the schedule changes
- [ ] env-3 an expected source host
- [ ] env-4 published per-run API-call counts, so read-side abuse surfaces as a
      volume anomaly rather than as nothing

## AT-110 - the credential is provably bounded (line 9439)

Six attempts must FAIL from the reconciler's own credential; the credential must
then still complete a normal reconciliation run. Executed for real at the phase
that builds the reconciler and re-executed at every rotation.

- [ ] attempt 1 write to a GitHub Actions secret - MUST FAIL
- [ ] attempt 2 write to an environment - MUST FAIL
- [ ] attempt 3 workflow-file change - MUST FAIL
- [ ] attempt 4 organisation-settings change - MUST FAIL
- [ ] attempt 5 write to records/** - MUST FAIL
- [ ] attempt 6 any Layer B access - MUST FAIL
- [ ] attempt 7 a normal reconciliation run - MUST SUCCEED

## Rotation gate (Section 40.1)

After any rotation, a manual reconciliation run must complete clean before the
rotation is recorded as done - "a credential that rotates but no longer
reconciles has not been rotated, it has been broken." AT-110 is re-executed on
the same gate.

## Compromise

Section 99.6 risk 6: the reconciler's own credential sits in the top secrets
tier "with its compromise treated as a security incident" - Section 43, not a
cleanup task. Re-issue source, should the operations VM be lost, is the Section
14.4 escrow (Section 40.1).
EOF

git add reconciler/CREDENTIAL-ENVELOPE.md
git commit -m "L3-00-06: reconciler credential tier, declared scope, behavioural envelope and AT-110 proof"
git push -u origin lane/3/00-t06
gh pr create --base integration --head lane/3/00-t06 --title "L3-00-06: reconciler credential envelope" --body "Fifth-tier placement, declared write scope, the four behavioural-envelope components, and AT-110's six must-fail attempts plus the must-succeed run. Sources: MasterSpec Sections 40.1, 26.4, 98.2, 99.6 risk 6, AT-110."
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Exactly six must-fail attempts | `grep -c 'MUST FAIL' reconciler/CREDENTIAL-ENVELOPE.md` | `6` |
| A2 | Exactly one must-succeed attempt | `grep -c 'MUST SUCCEED' reconciler/CREDENTIAL-ENVELOPE.md` | `1` |
| A3 | Seven checklist attempt lines | `grep -c '^- \[ \] attempt' reconciler/CREDENTIAL-ENVELOPE.md` | `7` |
| A4 | Four envelope components | `grep -c '^- \[ \] env-' reconciler/CREDENTIAL-ENVELOPE.md` | `4` |
| A5 | The rotation gate is present | `grep -c 'has not been rotated, it has been broken' reconciler/CREDENTIAL-ENVELOPE.md` | `1` |
| A6 | AT-110 is cited by id | `grep -c 'AT-110' reconciler/CREDENTIAL-ENVELOPE.md` | `2` |
| A7 | Only one file changed | `git diff --name-only origin/integration...HEAD \| wc -l` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
echo "FAIL=$(grep -c 'MUST FAIL' reconciler/CREDENTIAL-ENVELOPE.md)"
echo "SUCCEED=$(grep -c 'MUST SUCCEED' reconciler/CREDENTIAL-ENVELOPE.md)"
echo "ATTEMPTS=$(grep -c '^- \[ \] attempt' reconciler/CREDENTIAL-ENVELOPE.md)"
echo "ENV=$(grep -c '^- \[ \] env-' reconciler/CREDENTIAL-ENVELOPE.md)"
echo "FILES=$(git diff --name-only origin/integration...HEAD | wc -l)"
```

Expected output, exactly:

```
FAIL=6
SUCCEED=1
ATTEMPTS=7
ENV=4
FILES=1
```

**STOP rule.** If `FAIL` is not `6`: AT-110 names exactly six attempts (line 9439) and the transcription is wrong. Do not push, run `git reset --hard origin/integration`, and file a blocker using §9.7 with `TASK: L3-00-06`. Do not soften any `MUST FAIL` to a weaker word — AT-110's whole point is that this boundary is executed rather than asserted.

---

### 9.7 Blocker-issue template

File this verbatim, filling every field. Do not proceed past a STOP rule without filing it.

```
TITLE: [L3 BLOCKER] <TASK-ID> — <one-line symptom>

LANE: L3 — Reconciler & Provisioning
TASK: <task id, e.g. L3-00-05>
BRANCH: <branch name, e.g. lane/3/00-t05>
OWNED PATHS TOUCHED: <exact file list from `git diff --name-only origin/integration...HEAD`>

SYMPTOM:
<paste the literal SELF-VERIFY output that failed, unedited>

EXPECTED:
<paste the task's Expected output block, unedited>

SPEC ANCHOR:
<the section and line range the task cites for the value that mismatched>

WHAT I DID NOT DO:
I did not push. I did not open a PR. I did not edit any file outside
reconciler/**, tools/provision/**, validators/drift/**. I did not change the
expected value to make the check pass.

DECISION NEEDED FROM: L0 Integrator
```

---

## 10. DECISION REQUIRED — handed to L0

These items require designing, choosing or interpreting. Per PARTITION.md line 47, they are not this lane's to settle. Each blocks the named downstream task until L0 answers into `contracts/**`.

### DR-L3-01 — The blocking check-run name and its required-status-check registration

**Question.** Section 11.3 (lines 860–875) names `control-plane/blocking-drift` as a required status check, and Section 40.1 grants the reconciler check-run write for "exactly one named check". The check's exact context string, and its addition to each repository's required-status-check list, must be settled once. Branch-protection configuration is L5 (`access/**`); the check name is a cross-lane contract.
**Why L3 cannot decide.** L3 would be choosing a value two other lanes must match, and Section 98.2 Phase 1 warns that "a required check no workflow emits blocks every pull request indefinitely".
**Needed in `contracts/**`.** The literal context string, and the phase at which it is added to the required list.
**Blocks.** Every `reconciler/levels/` Level-4 task.

### DR-L3-02 — Which repair class is enabled first, and its enabling order

**Question.** Section 99.6 risk 6 requires "repair classes enabled one at a time". Section 53.2 Level 3 lists five candidate repair classes (Team membership sync, CODEOWNERS regeneration, label and board field sync, re-applying declared branch protection, removing expired assignments and expired access). The order is a risk judgment, not a spec fact.
**Why L3 cannot decide.** Choosing which org-admin write goes live first is exactly the judgment the partition reserves for L0.
**Needed in `contracts/**`.** An ordered list of the five classes with the gate each must pass before the next is enabled.
**Blocks.** Every `reconciler/repair/` task after the stricter-only guard.

### DR-L3-03 — The seeded canary's content and location

**Question.** Section 53.1 requires "a permanent seeded drift record — a deliberately planted, clearly labelled mismatch in the comparison set". What is planted, where, and how it is labelled so no operator mistakes it for real drift, is a design choice.
**Why L3 cannot decide.** The canary must be planted in a registry (L1) or an access artifact (L5) and read by L3 — a three-lane contract.
**Needed in `contracts/**`.** The canary's declared location, its label, and the comparison entry (C01–C19) it is expected to trip. <!-- Range updated to C01–C19 per FD-061 (was C01–C23). -->
**Blocks.** `reconciler/canary/**`, and therefore AT-102.

### DR-L3-04 — The `gap-window` mark's carrier

**Question.** Section 53.7 requires every record produced during a gap window to carry the `gap-window` mark until re-verified. Records are L4's; the mark is set by L3's gap procedure.
**Why L3 cannot decide.** The field lives in a record schema L3 does not own and must not edit.
**Needed in `contracts/**`.** The field name, its allowed values, and the clearing procedure.
**Blocks.** `reconciler/gap/**`.

### DR-L3-05 — The independent verifier's write surface

**Question.** Section 53.1 requires the independent control verifier to write "its result to a surface the operations VM cannot write to", under its own read-only fine-grained credential, off the operations VM. That surface is not named in the spec.
**Why L3 cannot decide.** It is a credential-and-infrastructure choice spanning L5 (credential, infra) and L2 (the scheduled workflow).
**Needed in `contracts/**`.** The named surface, the credential's identity, and the invocation contract for L3's assertion library.
**Blocks.** `validators/drift/verifier/**` beyond the assertion logic itself.

---

## Open Decision Register

Consolidates all L3 open decisions from L3-01 through L3-06. Canonical IDs are from the originating file; old aliases are listed for cross-reference. All decisions require L0 answer recorded in `contracts/**` before blocked tasks may start. DEC-L3-02-02 is RESOLVED per spec §11.3; all others remain OPEN.

| Canonical ID | Old aliases / cross-refs | Question (one line) | Status |
| --- | --- | --- | --- |
| D-L3-01 | L3-D1 (L3-06), D-L3-04-01 (L3-04) | Implementation runtime, version, dependency-pinning mechanism for `reconciler/**` and `validators/drift/**` | OPEN — written against python-3.12 (FD-005/FD-056); L0 must ratify |
| D-L3-02 | — | Provider-side attestation record store path and field names in `control-plane-records` | OPEN — blocks L3-01-11 |
| D-L3-03 | — | Production-restore record store path in `control-plane-records` | OPEN — blocks L3-01-18 |
| D-L3-04 | — | Seeded-canary placement (which comparator) and comparison-count shortfall class | OPEN — blocks L3-01-20 |
| L3-D2 | — | The five `contracts/**` paths Lane 3 reads (drift finding, run record, repair record, branch-protection template, environment template) | OPEN — blocks L3-P0-03 and all dependants |
| L3-D3 | — | Reconciler machine identity form (GitHub App vs fine-grained PAT) and test organisation login | OPEN — blocks L3-P5-06, L3-P5-07, L3-P8-05, L3-P8-06 |
| L3-D4 | — | Drift class for orphan severities `High` and `Medium` (§12.2 uses vocabulary §53.4 does not map) | OPEN — interim behaviour defined in L3-06 §5; blocks nothing |
| DEC-L3-02-01 | — | Red-class drift response level (§53.4 defines Red but §53.2 names no level for it) | OPEN — blocks L3-02-02, T04, T14 |
| DEC-L3-02-02 | DR-L3-01 (L3-00 §10) | Literal name of the blocking check run | **RESOLVED: check-run name = `control-plane/blocking-drift` per spec §11.3 line 867** |
| DEC-L3-02-03 | D-L3-02 (partial), D-L3-03 (partial), L3-D2 (partial) | Record store path and schema id for run records and repair records | OPEN — blocks L3-02-03, T04, T08, T13 |
| DEC-L3-02-04 | — | Does §53.1 "auto-repair where safe" row create a sixth repair class? | OPEN — blocks L3-02-06 |
| DR-3.1 | DR-L3-04 (L3-00 §10) | Anchor destination path and reconciler write-scope allowlist under `derived/**` | OPEN — interim default: `derived/anchors/records-head.yaml`; blocks L3-03 anchor tasks |
| DR-3.2 | DR-L3-03 (L3-00 §10) | Drift class of the permanent seeded canary finding | OPEN — interim default: Green, not budget-counted; blocks L3-03 canary tasks |
| DR-L3-02 | — | Which repair class is enabled first and in what order (five classes, §53.2 Level 3) | OPEN — blocks all `reconciler/repair/**` tasks after stricter-only guard |
| DR-L3-05 | — | Independent verifier write surface (credential, destination, invocation contract) | OPEN — blocks `validators/drift/verifier/**` beyond assertion logic |
| DR-L3-05-A | — | Operational asset inventory location and type vocabulary | OPEN — blocks L3-05-10..T13 and fixture-a assets.yaml |
| DR-L3-05-B | — | Which assignment types are "delegation-type" (14-day warning) | OPEN — blocks L3-05-26 |
| DR-L3-05-C | — | Board snapshot source and shape for H1 items | OPEN — blocks L3-05-17 |
| DR-L3-05-D | — | "Open gate-relevant work" input surface | OPEN — blocks L3-05-18, T27 |
| DR-L3-05-E | — | How a customer commitment's owner resolves | OPEN — blocks L3-05-14 |
| DR-L3-07-A | — | Lane 3 test-harness interface contract | OPEN — blocks L3-07-01 |
| DR-L3-07-B | — | Authorisation to touch the live organisation in acceptance tests | OPEN — blocks L3-07 live-mode tasks |

---

## 11. Lane self-check before any L3 PR

Run this from the `control-plane` repository root on any `lane/3/*` branch. It must print `LANE-GUARD-OK` and nothing else on the last line.

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
git fetch origin
FOREIGN=$(git diff --name-only origin/integration...HEAD | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' || true)
if [ -n "$FOREIGN" ]; then
  echo "LANE-GUARD-FAIL"
  echo "$FOREIGN"
else
  echo "LANE-GUARD-OK"
fi
```

If it prints `LANE-GUARD-FAIL`, do not push. Remove the foreign changes and re-run. If the foreign change is genuinely needed, it is a Contract Change Request to L0, never an edit (PARTITION.md rule 2).
