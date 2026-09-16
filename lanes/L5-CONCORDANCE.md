# L5-CONCORDANCE — task-id concordance for Lane 5

**Purpose.** Lane 5 carries two peer decompositions of itself under disjoint id namespaces and no
concordance in either direction. This file is that concordance. Per **FD-004** it is *additive*:
it edits no task file, authors no task body, and leaves both decompositions valid.

**Generated:** 2026-09-02. Measured against the copies on disk on that date — see §1.

---

## 1. Files read, as measured on disk

`wc -l` over the lane, run in `Code/implementation/lanes/`:

| File | Lines | Role in this concordance |
|---|---:|---|
| `L5-00-charter.md` | 821 | phase file (body side) |
| `L5-01-org-and-access.md` | 5635 | phase file (body side) |
| `L5-02-secrets-and-boundaries.md` | 5186 | phase file (body side) |
| `L5-03-layer-b.md` | 3753 | phase file (body side) |
| `L5-04-ops-vm.md` | 5143 | phase file (body side) |
| `L5-05-assets-ai-notify.md` | 4563 | phase file (body side) |
| `L5-06-tasks.md` | 4568 | **master tasks file — index side AND body side** |
| `L5-07-tests-and-runbook.md` | 2491 | phase file (body side) |
| **Total (8 files)** | **32160** | |

Not read for enumeration (review artifacts, not task carriers): `L5-98-DEEP-REVIEW.md` (220),
`L5-99-review.md` (713). Lane total including these: 33093.

---

## 2. Headline numbers

| Quantity | Count |
|---|---:|
| Index ids promised by `L5-06-tasks.md` | **59** |
| Distinct ids carrying a real body anywhere in the lane | **152** |
| Index ids confidently mapped to a body | **59** |
| **RESIDUE — index ids with no body anywhere** | **0** |
| Bodies no index row claims by id | **93** |
| — of those 93, semantically covered by an index row (duplicate decomposition) | 64 |
| — of those 93, **covered by no index row at all (untracked work)** | **29** |

### 2.1 The structural finding for L5, stated plainly

**Lane 5 is not shaped like L1/L3/L4.** In those lanes the master tasks file is an index whose
bodies live elsewhere. In L5, `L5-06-tasks.md` carries a **full body for every one of the 59 ids it
promises** — each with a `### L5-Tnn` heading, a Files list, command blocks, an Acceptance-criteria
table and a SELF-VERIFY block, 41–148 lines apiece. Verified mechanically in §4.

Therefore **the L5 id-level residue is zero.** There is no index id in Lane 5 whose body is missing.
The `L5-99-review.md` claim that 76 of 152 bodies were missing is wrong on the copy measured here:
all 152 are present.

**The real L5 defect is the inverse of the other lanes' defect.** It is not missing bodies. It is
**29 fully-specified task bodies in the phase files that no index row names or covers** (§7.2). A
dispatcher working from `L5-06-tasks.md` alone — which is exactly how the plan says to dispatch —
will never dispatch them. That is Lane 5's true unbuilt-and-untracked work.

---

## 3. INDEX SIDE — enumeration (59 ids)

The master tasks file states its promised ids in exactly one place: **§4 THE MASTER TASK TABLE**
(lines 126–191), a 59-row markdown table, columns
`# | ID | Phase | Mode | Title | Files touched | Deps | Size | Acceptance command`.

Two other places restate ids but promise no new ones: §4.1 (ASSISTED collection, 6 rows — all a
subset of the 59) and the `Deps` column. Union of all three = the same 59.

Set: `L5-T01` … `L5-T59`, contiguous, no gaps, no duplicates.

```bash
# index ids, from the table body only
sed -n '133,191p' L5-06-tasks.md | awk -F'|' '{gsub(/ /,"",$3); print $3}' | sort -u -V
# union check: every L5-T id mentioned anywhere in the file
grep -oE 'L5-T[0-9]+' L5-06-tasks.md | sort -u -V | wc -l     # -> 59
```

Both yield 59. The index namespace is closed.

---

## 4. BODY SIDE — enumeration (152 ids)

A *body* here means text an executor could follow: steps/commands, an acceptance-criteria table,
and a SELF-VERIFY (or equivalent) block. A bare mention in a `Deps` column is not a body.

Five distinct heading grammars carry bodies. No single regex finds them all:

| # | File | Grammar | Heading level | Bodies |
|---|---|---|---|---:|
| 1 | `L5-06-tasks.md` | `L5-Tnn` | `###` | 59 |
| 2 | `L5-00-charter.md` | `L5-00-nn` | `###` | 1 |
| 3 | `L5-01-org-and-access.md` | `L5-01-Tnn` | `##` | 15 |
| 4 | `L5-02-secrets-and-boundaries.md` | `L5-P2-Tnn` | `##` | 14 |
| 5 | `L5-03-layer-b.md` | `L5-P3-nn` (backticked) | `##` | 13 |
| 6 | `L5-04-ops-vm.md` | `L5-04-Tnn` | `##` | 19 |
| 7 | `L5-05-assets-ai-notify.md` | `L5-05-000` / `L5-05-Qnn` / `L5-05-Knn` / `L5-05-Rnn` (backticked) | `##` | 17 |
| 8 | `L5-07-tests-and-runbook.md` | `L5-07-Tnn` | `###` | 14 |
| | | | **Total** | **152** |

`L5-00-charter.md:516` `### L5-FF-TT — <imperative title>` is the **authoring template**, not a
body; it is excluded. Every one of the 152 was checked for span plus acceptance and verify markers.

Master file result: 59/59 bodies, span 41–148 lines, `AC>=1` and `SV>=1` on every one. Smallest is
`L5-T03` (41 lines). Phase files result: 93/93 bodies, span 83–540 lines, acceptance and verify
markers on every one. Commands in §8 (items 6 and 7).

**Cross-namespace citation check.** Across all seven phase files, exactly **one** index id is ever
cited (`L5-T14`, in `L5-03-layer-b.md`). This is the mechanical proof that no concordance existed:

```bash
grep -ohE 'L5-T[0-9]+' L5-00-charter.md L5-01-*.md L5-02-*.md L5-03-*.md L5-04-*.md \
  L5-05-*.md L5-07-*.md | sort -u -V     # -> L5-T14, and nothing else
```

---

## 5. MAPPING TABLE — index id to body id (all 59, exact)

Every index id maps to a body **in the master tasks file itself**, by exact id match. Confidence is
`EXACT` throughout: same file, same id string, heading directly above the body.

| Index id | Body id | Body file | Line | Conf | What the task does |
|---|---|---|---:|---|---|
| L5-T01 | L5-T01 | L5-06-tasks.md | 210 | EXACT | Lane tree + `infra/OWNERSHIP.md` ownership manifest |
| L5-T02 | L5-T02 | L5-06-tasks.md | 265 | EXACT | Python toolchain pin, venv bootstrap, `$L5PY` |
| L5-T03 | L5-T03 | L5-06-tasks.md | 309 | EXACT | Lane path-guard self-check script |
| L5-T04 | L5-T04 | L5-06-tasks.md | 351 | EXACT | Read-only contract-input inventory + checker |
| L5-T05 | L5-T05 | L5-06-tasks.md | 430 | EXACT | GitHub permission semantics as data (§11.1) |
| L5-T06 | L5-T06 | L5-06-tasks.md | 502 | EXACT | Person-class permission model (§11.2) |
| L5-T07 | L5-T07 | L5-06-tasks.md | 580 | EXACT | Branch-protection declaration (§11.3) |
| L5-T08 | L5-T08 | L5-06-tasks.md | 665 | EXACT | Five secret tiers + fifth-tier envelope (§40.1) |
| L5-T09 | L5-T09 | L5-06-tasks.md | 750 | EXACT | Layer A/B data-category permission matrix (§90.2) |
| L5-T10 | L5-T10 | L5-06-tasks.md | 825 | EXACT | Fail-closed classification register (§64.2, inv 80) |
| L5-T11 | L5-T11 | L5-06-tasks.md | 887 | EXACT | Safe-defaults register (§64.1, inv 79) |
| L5-T12 | L5-T12 | L5-06-tasks.md | 929 | EXACT | Access-model validator, JSON schemas, test suite |
| L5-T13 | L5-T13 | L5-06-tasks.md | 973 | EXACT | Machine-identity boundary checker (§90.2, inv 106) |
| L5-T14 | L5-T14 | L5-06-tasks.md | 1020 | EXACT | `people-intelligence` non-delegability checker (D109, AT-091) |
| L5-T15 | L5-T15 | L5-06-tasks.md | 1068 | EXACT | ASSISTED: org-settings arming + evidence capture |
| L5-T16 | L5-T16 | L5-06-tasks.md | 1138 | EXACT | ASSISTED: ops-VM image digest / version lock |
| L5-T17 | L5-T17 | L5-06-tasks.md | 1287 | EXACT | Compose stack rendered from the lock |
| L5-T18 | L5-T18 | L5-06-tasks.md | 1350 | EXACT | Host provisioning + fifth-tier credential isolation |
| L5-T19 | L5-T19 | L5-06-tasks.md | 1461 | EXACT | Platform SLO register (§51.2) |
| L5-T20 | L5-T20 | L5-06-tasks.md | 1540 | EXACT | Patch cadence + post-patch smoke checklist (§51.4) |
| L5-T21 | L5-T21 | L5-06-tasks.md | 1625 | EXACT | Off-VM detection leg, dead-man heartbeat (§51.5, D94) |
| L5-T22 | L5-T22 | L5-06-tasks.md | 1728 | EXACT | Rebuild runbook source + 4-hour clock (§45.4) |
| L5-T23 | L5-T23 | L5-06-tasks.md | 1816 | EXACT | ASSISTED: VM provisioning, private path, object-locked bucket |
| L5-T24 | L5-T24 | L5-06-tasks.md | 1895 | EXACT | Runtime capability + vendor checklist config (§35.1, §35.6) |
| L5-T25 | L5-T25 | L5-06-tasks.md | 2003 | EXACT | No-API-keys check (§36.6, inv 84) |
| L5-T26 | L5-T26 | L5-06-tasks.md | 2066 | EXACT | Extension / MCP-server pin checker (§36.3, inv 85) |
| L5-T27 | L5-T27 | L5-06-tasks.md | 2127 | EXACT | Constitution-reference checker (§36.1) |
| L5-T28 | L5-T28 | L5-06-tasks.md | 2183 | EXACT | Pre-flight secret-strip wrapper (§36.6) |
| L5-T29 | L5-T29 | L5-06-tasks.md | 2262 | EXACT | Per-product AI-restriction checker (§36.4) |
| L5-T30 | L5-T30 | L5-06-tasks.md | 2322 | EXACT | AI-eval scheduled runner + SIG-42 emission (§38.3, AT-107) |
| L5-T31 | L5-T31 | L5-06-tasks.md | 2410 | EXACT | Model-regression benchmark record template (§35.5) |
| L5-T32 | L5-T32 | L5-06-tasks.md | 2501 | EXACT | Quarterly workstation check bundle (§36.3, §36.6) |
| L5-T33 | L5-T33 | L5-06-tasks.md | 2590 | EXACT | Asset inventory entry schema, 16 classes (§49.1) |
| L5-T34 | L5-T34 | L5-06-tasks.md | 2668 | EXACT | Seed the 11 inventory entries |
| L5-T35 | L5-T35 | L5-06-tasks.md | 2759 | EXACT | Inventory validator + tests |
| L5-T36 | L5-T36 | L5-06-tasks.md | 2818 | EXACT | Deadline watch job (§49.1, §49.2) |
| L5-T37 | L5-T37 | L5-06-tasks.md | 2878 | EXACT | Vendor-deadline entries + deprecation feed (§49.2) |
| L5-T38 | L5-T38 | L5-06-tasks.md | 2959 | EXACT | Asset-owner orphan feed (§49.1) |
| L5-T39 | L5-T39 | L5-06-tasks.md | 3027 | EXACT | Closed push-event list (§92.11) |
| L5-T40 | L5-T40 | L5-06-tasks.md | 3109 | EXACT | Channel register (§92.11, §42.2, §47) |
| L5-T41 | L5-T41 | L5-06-tasks.md | 3187 | EXACT | Router CLI, fail-closed on an unlisted event |
| L5-T42 | L5-T42 | L5-06-tasks.md | 3248 | EXACT | Layer-B content guard on the router (§90.2) |
| L5-T43 | L5-T43 | L5-06-tasks.md | 3307 | EXACT | Phone-escalation path artifact + presence check (§42.2) |
| L5-T44 | L5-T44 | L5-06-tasks.md | 3379 | EXACT | No-paging-apps check (§99.2 row R) |
| L5-T45 | L5-T45 | L5-06-tasks.md | 3439 | EXACT | ASSISTED: messaging webhook creation + secret storage |
| L5-T46 | L5-T46 | L5-06-tasks.md | 3516 | EXACT | Founder-only Grafana instance provisioning (D75) |
| L5-T47 | L5-T47 | L5-06-tasks.md | 3574 | EXACT | Shared-instance people-datasource absence check (AT-097) |
| L5-T48 | L5-T48 | L5-06-tasks.md | 3636 | EXACT | Separate-credential check (AT-098) |
| L5-T49 | L5-T49 | L5-06-tasks.md | 3695 | EXACT | Layer B allowlist derivation + comparison scope (§90.4) |
| L5-T50 | L5-T50 | L5-06-tasks.md | 3775 | EXACT | Layer B access log + session lifetime (§90.3) |
| L5-T51 | L5-T51 | L5-06-tasks.md | 3857 | EXACT | Layer B at-rest + backup discipline config (§51.4) |
| L5-T52 | L5-T52 | L5-06-tasks.md | 3937 | EXACT | Self-view generator + public-key registry (§90.6) |
| L5-T53 | L5-T53 | L5-06-tasks.md | 4003 | EXACT | ASSISTED: per-person public-key registration, annual re-key |
| L5-T54 | L5-T54 | L5-06-tasks.md | 4066 | EXACT | Layer B restore-protocol instrument (§45.4) |
| L5-T55 | L5-T55 | L5-06-tasks.md | 4158 | EXACT | Access acceptance harness (AT-089/090/091/092/093/094/097/098) |
| L5-T56 | L5-T56 | L5-06-tasks.md | 4222 | EXACT | ASSISTED: AT-110 reconciler-credential bound execution |
| L5-T57 | L5-T57 | L5-06-tasks.md | 4295 | EXACT | Invariant classification map for L5 invariants |
| L5-T58 | L5-T58 | L5-06-tasks.md | 4371 | EXACT | Workflow-request handoff bundle to L2 |
| L5-T59 | L5-T59 | L5-06-tasks.md | 4470 | EXACT | Lane integration readiness report + PR |

**59 of 59 mapped. Confidence EXACT on all.**

---

## 6. RESIDUE — index ids with no body anywhere

**EMPTY. Zero rows.**

| Index id | What the index promises | Why nothing matches |
|---|---|---|
| — | — | — |

No index id in Lane 5 lacks a body. This is not an optimistic reading: the §4 mechanical check shows
all 59 bodies present in `L5-06-tasks.md` with acceptance criteria and a SELF-VERIFY block, minimum
span 41 lines. **Lane 5's contribution to the founder's index-side residue is 0.**

---

## 7. ORPHANS — bodies no index row claims

All 93 phase-file bodies are orphans at the id level: no index row names any of them, and the phase
files cite an index id exactly once in 27,592 lines. Bare id-mismatch is not decision-useful on its
own, so each orphan is classified by **what it does**:

- **COVERED** — an index row builds the same thing under a different name. Duplicate decomposition;
  the work is tracked, and L0 dispatches it once, from whichever decomposition is chosen. 64 bodies.
- **UNCLAIMED** — no index row covers this work at all. If dispatch runs from `L5-06-tasks.md`,
  nobody builds it. **29 bodies.** This is Lane 5's actionable finding.

### 7.1 COVERED orphans (64) — duplicate decomposition, already tracked

| Body id | File | Line | Index twin | Conf | What it does |
|---|---|---:|---|---|---|
| L5-00-01 | L5-00-charter.md | 661 | L5-T01 | HIGH | Create L5 lane skeleton + publication directories |
| L5-01-01 | L5-01-org-and-access.md | 115 | L5-T01 | HIGH | Lane skeleton, preflight, blocker helper |
| L5-01-02 | L5-01-org-and-access.md | 321 | L5-T12 | HIGH | Access-config schema harness + validator |
| L5-01-03 | L5-01-org-and-access.md | 528 | L5-T15 | MED | `organisation.yaml`: single org, base Read, enforced 2FA — the declarative half of T15's arming |
| L5-01-04 | L5-01-org-and-access.md | 833 | L5-T05 | HIGH | `permission-semantics.yaml`, the §11.1 verified table |
| L5-01-05 | L5-01-org-and-access.md | 1195 | L5-T06 | HIGH | `teams.yaml`, the §11.2 person-class table |
| L5-01-07 | L5-01-org-and-access.md | 2158 | L5-T07 | HIGH | `branch-protection.yaml`, §11.3, unarmed/armed profiles |
| L5-01-12 | L5-01-org-and-access.md | 4146 | L5-T15 | MED | Apply runbooks, `gh` commands in arming order |
| L5-01-15 | L5-01-org-and-access.md | 5445 | L5-T59 | HIGH | Lane integration PR |
| L5-02-01 | L5-02-secrets-and-boundaries.md | 272 | L5-T08 | HIGH | Secret-tier registry: five tiers, contents, locations |
| L5-02-02 | L5-02-secrets-and-boundaries.md | 525 | L5-T08 | MED | Tier registry schema + validator |
| L5-02-04 | L5-02-secrets-and-boundaries.md | 1183 | L5-T34 | MED | Fifth-tier credential inventory entries (five credentials) |
| L5-02-05 | L5-02-secrets-and-boundaries.md | 1550 | L5-T08 | MED | Behavioural-envelope declaration + credential schema (D96) |
| L5-02-10 | L5-02-secrets-and-boundaries.md | 3225 | L5-T18 | HIGH | Ops-VM credential-store holding, hardware-key shell gate |
| L5-02-12 | L5-02-secrets-and-boundaries.md | 4041 | L5-T25 | HIGH | API-key-free check: onboarding and quarterly |
| L5-02-14 | L5-02-secrets-and-boundaries.md | 4728 | L5-T59 | MED | Phase 2 exit gate: one command runs every check |
| L5-03-01 | L5-03-layer-b.md | 114 | L5-T01 | MED | Phase preflight, workspace, phase manifest |
| L5-03-03 | L5-03-layer-b.md | 468 | L5-T46 | HIGH | Provision second Founder-only Grafana (Layer B-M) |
| L5-03-04 | L5-03-layer-b.md | 740 | L5-T47 | HIGH | People datasource in Layer B-M only; absence proof (AT-097) |
| L5-03-05 | L5-03-layer-b.md | 952 | L5-T51 | HIGH | Encrypt people-data store at rest + checksum manifest |
| L5-03-06 | L5-03-layer-b.md | 1193 | L5-T51 | HIGH | Restricted backup credential, object-locked backup target |
| L5-03-07 | L5-03-layer-b.md | 1501 | L5-T50 | HIGH | Layer B access log + host file-access audit shipped off-host |
| L5-03-08 | L5-03-layer-b.md | 1747 | L5-T50 | HIGH | Session-lifetime limits; no standing unattended sessions |
| L5-03-09 | L5-03-layer-b.md | 1996 | L5-T49 | HIGH | Allowlist sync, non-delegability, reconciliation comparison scope |
| L5-03-10 | L5-03-layer-b.md | 2327 | L5-T52 | HIGH | Layer B-S generated encrypted per-person self-view |
| L5-03-12 | L5-03-layer-b.md | 2978 | L5-T55 | MED | People-tier hard gate: acceptance-test runner + gate artifact |
| L5-03-13 | L5-03-layer-b.md | 3400 | L5-T20 | MED | Post-patch smoke checklist + Layer B alert routing |
| L5-04-01 | L5-04-ops-vm.md | 173 | L5-T16 | HIGH | Ops-VM tree, pinned component manifest, shared shell library |
| L5-04-02 | L5-04-ops-vm.md | 377 | L5-T18 | HIGH | Base provisioning, private network path, SSO front door |
| L5-04-03 | L5-04-ops-vm.md | 590 | L5-T17 | HIGH | Shared stack compose: Grafana, Prometheus (FD-112: DevLake deferred) |
| L5-04-05 | L5-04-ops-vm.md | 1034 | L5-T46 | HIGH | Layer B second Grafana: host placement, encryption at rest |
| L5-04-06 | L5-04-ops-vm.md | 1254 | L5-T51 | HIGH | Layer B backup: append-only credential to object-locked storage |
| L5-04-11 | L5-04-ops-vm.md | 2235 | L5-T36 | HIGH | Asset inventory store + expiry-check job |
| L5-04-12 | L5-04-ops-vm.md | 2580 | L5-T54 | MED | Restore-rotation scheduler |
| L5-04-14 | L5-04-ops-vm.md | 3230 | L5-T21 | HIGH | D94 external dead-man switch, off-VM liveness leg |
| L5-04-15 | L5-04-ops-vm.md | 3512 | L5-T20 | HIGH | Patch cadence, singleton patch driver, post-patch smoke |
| L5-04-16 | L5-04-ops-vm.md | 3973 | L5-T22 | HIGH | Rebuild driver, step manifest, generated runbook |
| L5-04-17 | L5-04-ops-vm.md | 4288 | L5-T22 | MED | Quarterly rebuild drill: 4-h clock, VM-stop, zero-resources evidence |
| L5-05-00 | L5-05-assets-ai-notify.md | 129 | L5-T02 | HIGH | Phase toolchain preflight |
| L5-05-01 | L5-05-assets-ai-notify.md | 213 | L5-T33 | HIGH | Asset-entry schema, inventory directory, validator |
| L5-05-02 | L5-05-assets-ai-notify.md | 518 | L5-T34 | HIGH | Machine-credential + org-export encryption-key entries |
| L5-05-03 | L5-05-assets-ai-notify.md | 720 | L5-T34 | HIGH | The two Hermes host entries |
| L5-05-04 | L5-05-assets-ai-notify.md | 857 | L5-T34 | HIGH | Self-hosted runner-estate inventory entries |
| L5-05-05 | L5-05-assets-ai-notify.md | 1068 | L5-T34 | HIGH | Off-VM detection-leg entries |
| L5-05-06 | L5-05-assets-ai-notify.md | 1175 | L5-T34 | HIGH | AI subscription seat entry + seat rules |
| L5-05-07 | L5-05-assets-ai-notify.md | 1379 | L5-T37 | HIGH | Vendor deadline-watch entries + lead-time validator |
| L5-05-08 | L5-05-assets-ai-notify.md | 1751 | L5-T36 | HIGH | Daily expiry-and-deadline check job (wait-surface only) |
| L5-05-09 | L5-05-assets-ai-notify.md | 2034 | L5-T24 | HIGH | `ai-toolchain` config pinned by full SHA (also feeds L5-T26) |
| L5-05-10 | L5-05-assets-ai-notify.md | 2400 | L5-T27 | HIGH | Constitution file + every-context-file reference check |
| L5-05-11 | L5-05-assets-ai-notify.md | 2650 | L5-T28 | HIGH | Secret-stripping pre-flight + no-API-keys check (also L5-T25) |
| L5-05-12 | L5-05-assets-ai-notify.md | 2864 | L5-T31 | HIGH | Model-regression benchmark manifest + runner wrapper |
| L5-05-13 | L5-05-assets-ai-notify.md | 3202 | L5-T40 | HIGH | Channel configuration + phone-escalation path (also L5-T43) |
| L5-05-14 | L5-05-assets-ai-notify.md | 3496 | L5-T39 | HIGH | The closed push list of §92.11 |
| L5-05-15 | L5-05-assets-ai-notify.md | 3861 | L5-T41 | HIGH | The notification router CLI |
| L5-05-16 | L5-05-assets-ai-notify.md | 4154 | L5-T44 | HIGH | Closed-list guard — nothing off-list may page a person |
| L5-07-01 | L5-07-tests-and-runbook.md | 217 | L5-T55 | MED | Test harness skeleton + evidence machinery |
| L5-07-02 | L5-07-tests-and-runbook.md | 353 | L5-T55 | MED | Coverage manifest + its self-check |
| L5-07-03 | L5-07-tests-and-runbook.md | 462 | L5-T25 | HIGH | NC-08: the no-API-keys check, executed |
| L5-07-08 | L5-07-tests-and-runbook.md | 1034 | L5-T47/T48 | HIGH | AT-097 and AT-098: Grafana instance separation |
| L5-07-09 | L5-07-tests-and-runbook.md | 1151 | L5-T56 | HIGH | AT-110 reconciler bounds (its AT-022 half is unclaimed — see §7.2) |
| L5-07-10 | L5-07-tests-and-runbook.md | 1346 | L5-T55 | HIGH | AT-089/090/091/092/096/100 Layer B reach + conduct separation |
| L5-07-11 | L5-07-tests-and-runbook.md | 1566 | L5-T38 | HIGH | AT-017: the asset-owner orphan leg |
| L5-07-12 | L5-07-tests-and-runbook.md | 1682 | L5-T39 | MED | AT-106: Gate 1 notification, the push-event leg |
| L5-07-13 | L5-07-tests-and-runbook.md | 1790 | L5-T30 | HIGH | AT-011, AT-049, AT-107: the AI runtime contract |

### 7.2 UNCLAIMED orphans (29) — work no index row covers

**This is Lane 5's contribution to the founder's untracked-work list.** Each has a complete,
dispatchable body. None is named or covered by any of the 59 index rows. Verified by a keyword sweep
of the index table (§8, command 9): `CODEOWNERS`, `deployment`, `plan-tier`, `break-glass`, `escrow`,
`transition`, `rotation`, `trust bound`, `host-root`, `containment`, `Renovate`, `scorecard`,
`health`, `export`, `D87`, `NC-0*`, `AT-022`, `AT-029`, `AT-035` all return **0 hits** in the table.

| Body id | File | Line | What it does | Note |
|---|---|---:|---|---|
| L5-01-06 | L5-01-org-and-access.md | 1637 | Human-only CODEOWNERS generator with executed negative tests | Also a **PARTITION conflict**: §1.2 of the index lists `CODEOWNERS` as an **L0-owned** path Lane 5 must never write |
| L5-01-08 | L5-01-org-and-access.md | 2699 | `deployment-policies.yaml` — the §33.4 deployment branch and tag policy | |
| L5-01-09 | L5-01-org-and-access.md | 3083 | `plan-tier.yaml` — the §11.4 table with a depended-on checker | |
| L5-01-10 | L5-01-org-and-access.md | 3444 | D101 arming order and the arming-order gate | L5-T15 arms org settings but ships no order gate |
| L5-01-11 | L5-01-org-and-access.md | 3872 | Owner continuity and break-glass escrow declaration | Pairs with AT-022, also unclaimed |
| L5-01-13 | L5-01-org-and-access.md | 4626 | Phase 1 access completion check: offline assertions + negative-test register | Partially overlaps L5-T55; the NC register has no index home |
| L5-01-14 | L5-01-org-and-access.md | 5068 | Per-repository transition note template and generator (§95.4) | |
| L5-02-03 | L5-02-secrets-and-boundaries.md | 837 | The never-moves-down-a-tier check | |
| L5-02-06 | L5-02-secrets-and-boundaries.md | 1879 | Envelope evaluator: a run outside the envelope is Blocking | L5-T08 declares the envelope; nothing evaluates it |
| L5-02-07 | L5-02-secrets-and-boundaries.md | 2269 | The one-page credential-rotation runbook | |
| L5-02-08 | L5-02-secrets-and-boundaries.md | 2496 | Rotation-completion gate (clean reconciliation + AT-110 + re-escrow) | |
| L5-02-09 | L5-02-secrets-and-boundaries.md | 2797 | The two trust boundaries, declared and checkable (§40.3, D95) | Distinct from L5-T13's §90.2 machine-identity boundary |
| L5-02-11 | L5-02-secrets-and-boundaries.md | 3643 | Rotator / host-root separation, or the recorded accepted risk | |
| L5-02-13 | L5-02-secrets-and-boundaries.md | 4421 | Workstation-compromise containment hook (§43.4) | |
| L5-03-02 | L5-03-layer-b.md | 278 | D95 host separation: declare and check the Layer B host boundary | L5-T46 provisions the instance; nothing declares or checks the host boundary |
| L5-03-11 | L5-03-layer-b.md | 2762 | The named accepted-access record for host-level administrative access | |
| L5-04-04 | L5-04-ops-vm.md | 810 | Grafana provisioning from git: datasource, dashboard provider, stack dashboard | Index covers the Layer B Grafana only, never the shared instance |
| L5-04-07 | L5-04-ops-vm.md | 1454 | Reconciliation host: units, credential store, freshness telemetry | Index names the reconciler credential (L5-T56) but never builds its host |
| L5-04-08 | L5-04-ops-vm.md | 1716 | Health computation job and report freshness | |
| L5-04-09 | L5-04-ops-vm.md | 1855 | Scorecard scheduled scan runner | |
| L5-04-10 | L5-04-ops-vm.md | 1988 | Renovate self-hosted runner | |
| L5-04-13 | L5-04-ops-vm.md | 2847 | Organisation export runner and staleness telemetry | Tested by L5-07-04 (NC-13) and L5-07-14 (AT-035); built by no index row |
| L5-04-18 | L5-04-ops-vm.md | 4579 | Self-hosted runner estate: groups, placement rule, inventory entries | L5-05-Q04 / L5-T34 record the *entries*; nothing builds the estate |
| L5-04-19 | L5-04-ops-vm.md | 4835 | D87 privileged/build pool separation and its three Blocking drift checks | |
| L5-07-04 | L5-07-tests-and-runbook.md | 563 | NC-09 and NC-13: exception-validator negative, org-export schedule | |
| L5-07-05 | L5-07-tests-and-runbook.md | 680 | NC-01..NC-07, NC-10, NC-11: the live branch-protection negatives (ASSISTED, size L) | The index carries no negative-test task at all |
| L5-07-06 | L5-07-tests-and-runbook.md | 839 | AT-108: the founder ops console is provably read-only | **Scope conflict**: index §1.3 declares AT-108 **out of Lane 5 scope**, routed to L0 |
| L5-07-07 | L5-07-tests-and-runbook.md | 936 | AT-109: the background cage egress wall holds | **Scope conflict**: index §1.3 declares AT-109 **out of Lane 5 scope**, routed to L0 |
| L5-07-14 | L5-07-tests-and-runbook.md | 1999 | AT-029 and AT-035: control-plane loss and the organisation-export restore | 492 lines, the largest body in the lane; no index row |

Plus one **partial**: the AT-022 (break-glass Owner) half of `L5-07-09` is unclaimed even though its
AT-110 half maps cleanly to L5-T56.

### 7.3 What L0 must decide about the 29

Three distinct decisions, not one:

1. **Two are scope conflicts, not gaps** — `L5-07-06` (AT-108) and `L5-07-07` (AT-109). The index
   says they are L0's; the phase file writes them as Lane 5 tasks. Decide who owns them before
   dispatch; do not let both stand.
2. **One is a PARTITION violation** — `L5-01-06` writes `CODEOWNERS`, which the index's own §1.2
   forbids Lane 5 to touch. Lane-guard CI would fail that PR.
3. **The other 26 are genuinely untracked build work** — specified, dispatchable, and invisible to
   anyone reading the master task list.

---

## 8. Exact commands, for regeneration

Run from `Code/implementation/lanes/` (Git Bash / POSIX sh).

```bash
# 1. file measurements (the header table)
wc -l L5-*.md

# 2. INDEX side — ids from the master task table body
sed -n '133,191p' L5-06-tasks.md | awk -F'|' '{gsub(/ /,"",$3); print $3}' | sort -u -V

# 3. INDEX side — union check across the whole master file
grep -oE 'L5-T[0-9]+' L5-06-tasks.md | sort -u -V | wc -l

# 4. namespace discovery — collapse digits to '#' to see the grammars per file
for f in L5-0*.md; do echo "=== $f"; \
  grep -oE 'L5[-_][A-Za-z0-9][A-Za-z0-9-]*' "$f" | sed -E 's/[0-9]+/#/g' \
  | sort | uniq -c | sort -rn | head -20; done

# 5. BODY side — all task headings, both heading levels, backticked and not
grep -nE '^#{2,5} `?L5[-_]' L5-00-charter.md L5-01-org-and-access.md \
  L5-02-secrets-and-boundaries.md L5-03-layer-b.md L5-04-ops-vm.md \
  L5-05-assets-ai-notify.md L5-06-tasks.md L5-07-tests-and-runbook.md

# 6. body-reality check, master file (span / SELF-VERIFY / acceptance per body)
awk '/^### L5-T[0-9]{2} /{if(id!=""){printf "%s\tlines=%d\tSV=%d\tAC=%d\n",id,n,sv,ac}
  id=$2;n=0;sv=0;ac=0;next}{if(id!=""){n++;if($0~/SELF-VERIFY/)sv++;if($0~/Acceptance criteria/)ac++}}
  END{if(id!="")printf "%s\tlines=%d\tSV=%d\tAC=%d\n",id,n,sv,ac}' L5-06-tasks.md

# 7. body-reality check, phase files
for f in L5-00-charter.md L5-01-org-and-access.md L5-02-secrets-and-boundaries.md \
         L5-03-layer-b.md L5-04-ops-vm.md L5-05-assets-ai-notify.md L5-07-tests-and-runbook.md; do
  awk -v F="$f" '
  /^#{2,3} `?L5-(00|01|04|05|07)-[A-Z0-9]|^#{2,3} `?L5-P[23]-[A-Z0-9]/{
    if(id!=""){printf "%s\t%s\t%d\t%d\t%d\t%d\n",F,id,ln,n,sv,ac}
    line=$0;gsub(/^#+ /,"",line);gsub(/`/,"",line);split(line,a," ");id=a[1];ln=NR;n=0;sv=0;ac=0;next}
  {if(id!=""){n++;if($0~/SELF-VERIFY|SELF_VERIFY/)sv++;if($0~/[Aa]cceptance/)ac++}}
  END{if(id!="")printf "%s\t%s\t%d\t%d\t%d\t%d\n",F,id,ln,n,sv,ac}' "$f"; done

# 8. proof that no concordance existed — index ids cited in phase files
grep -ohE 'L5-T[0-9]+' L5-00-charter.md L5-01-*.md L5-02-*.md L5-03-*.md \
  L5-04-*.md L5-05-*.md L5-07-*.md | sort -u -V

# 9. UNCLAIMED verification — keyword sweep of the index table only (lines 126-207)
for k in CODEOWNERS deployment plan-tier break-glass escrow transition 'never-moves' \
         'trust bound' host-root containment Renovate scorecard health export D87 \
         'NC-0\|NC-1' 'AT-029\|AT-035' AT-022; do
  printf '%-24s ' "$k"; sed -n '126,207p' L5-06-tasks.md | grep -ci "$k"; done
```

**Patterns used for the body sweep (union of five grammars):**
`^### L5-T[0-9]{2} ` · `^## L5-01-T[0-9]{2}` · `^## L5-P2-T[0-9]{2}` ·
`` ^## `L5-P3-[0-9]{2}` `` · `^## L5-04-T[0-9]{2}` · `` ^## `L5-05-(000|Q|K|R)[0-9]{2}` `` ·
`^### L5-07-T[0-9]{2}` · `^### L5-00-[0-9]{2}`.

Heading-level-only or backtick-naive greps under-report: `L5-03` and `L5-05` backtick their ids,
`L5-01/02/03/04/05` use `##` while `L5-00/06/07` use `###`.

---

## 9. Caveats on confidence

- All 59 index-to-body mappings are **EXACT** (same file, same id) and carry no interpretive risk.
- The §7 orphan classification is **interpretive**. COVERED/UNCLAIMED was judged on what the task
  builds, cross-checked against the index's `Files touched` column and the keyword sweep. Nine
  COVERED rows are marked MED — the phase body and its index twin overlap substantially but are not
  identical in scope; L0 should read both before deciding which to dispatch.
- No row was mapped on sequence or phase number alone. Where the work did not clearly match, the
  body was left UNCLAIMED rather than force-fitted — per the standing rule that a wrong mapping is
  worse than an honest gap.
- **No task body was written, edited, or moved by this work.** This file is additive.

---

## Session 12 update (2026-09-08)

**Last-verified:** 2026-09-08 (Session 12).

### Fixes applied in Session 12

- **B-02 task-ID rename complete** — 78 task IDs renamed from the legacy flat format to the canonical `L5-FF-TT` format. IDs updated across `L5-01-org-and-access.md`, `L5-02-secrets-and-boundaries.md`, `L5-03-layer-b.md`, `L5-04-ops-vm.md`, and `L5-05-assets-ai-notify.md`. All cross-references within those files updated to match.

### L5-99 re-review (Session 12): **PASS**

---

## Session 13 Update (2026-09-08)

- **5 Phase 1 orphan bodies added to L5-06 index** — five previously untracked Phase 1 bodies from the phase files are now indexed in `L5-06-tasks.md`; these were in the 29 UNCLAIMED orphan set (§7.2).
- **L5-01-06 PARTITION violation corrected** — the task body was writing to a path outside L5's owned directory tree; the violation is marked and the path corrected.
- **21 orphans in L5-02..L5-07 noted** — after the 5 Phase 1 additions, 21 untracked orphan bodies remain across L5-02 through L5-07; these will be indexed in a follow-on agent pass.
- **FD-079..081 being written** — founder decisions Q9 (L5 dispatch order), Q10 (L5 phase-file normative status), and Q11 (L5-01-06 PARTITION resolution) are in progress as of this session.
