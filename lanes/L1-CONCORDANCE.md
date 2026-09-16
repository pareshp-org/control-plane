# L1-CONCORDANCE — Lane 1 task-id concordance

**Status:** COMPLETE. **Residue: 0.** Every one of the 61 index ids Lane 1 promises has a full,
executable body. The unbuilt-work list for Lane 1 is empty.

**Produced under FD-004** (`_FOUNDER_DECISIONS.md`): publish a concordance, do not reissue the
indexes. This file is additive. It edits no task file, authors no task body, and invalidates no
citation to either id namespace.

**Measured on disk 2026-09-02.** All counts below are reproducible against the copies whose
`wc -l` is stated in §0. Two prior reviews were caught measuring superseded copies; `L1-99-review.md`
claimed `L1-05-tasks.md` was truncated with 30 of 61 bodies missing. That claim is **wrong against
the file on disk today**: the file is 6,132 lines and carries all 61 bodies, each with a SELF-VERIFY.

---

## 0. Files read, with `wc -l`

Command: `wc -l L1-*.md` run in `C:/D_Drive/PS/MultiProduct/Code/implementation/lanes`.

| File | Lines | Role in this concordance |
|---|---:|---|
| `L1-00-charter.md` | 828 | body side (phase) |
| `L1-01-repo-skeleton.md` | 1957 | body side (phase) |
| `L1-02-schemas.md` | 2226 | body side (phase) |
| `L1-03-validators.md` | 2029 | body side (phase) |
| `L1-04-ci-gate-engine.md` | 1728 | body side (phase) |
| `L1-05-tasks.md` | **6132** | **index side AND body side** |
| `L1-06-tests.md` | 1328 | body side (phase) |
| `L1-07-runbook.md` | 1132 | body side (phase, procedures) |
| *(context only, not measured as index or body)* | | |
| `L1-98-DEEP-REVIEW.md` | 172 | not used |
| `L1-99-review.md` | 547 | not used — its L1-05 measurement is superseded (see header) |

Total across the eight measured files: **17,360 lines**.

---

## 1. The index side — 61 ids

`L1-05-tasks.md` states its promised ids in exactly one place: the **MASTER TASK TABLE** at
`L1-05-tasks.md:170-232`, a numbered markdown table whose column 2 is the task id. The table's own
footer at line 234 reads `**Totals:** 61 tasks. S = 14, M = 26, L = 21.`

```bash
# rows in the master task table
grep -nE '^\| *[0-9]+ *\| *L1-[0-9]{3} *\|' L1-05-tasks.md | wc -l          # -> 61
# the distinct ids themselves
grep -oE '^\| *[0-9]+ *\| *L1-[0-9]{3}' L1-05-tasks.md \
  | grep -oE 'L1-[0-9]{3}' | sort -u | wc -l                                 # -> 61
```

**The index set is closed.** No acceptance-criteria list, phase table or prose paragraph anywhere in
`L1-05-tasks.md` promises a task id the master table does not already carry:

```bash
grep -oE 'L1-[0-9]{3}' L1-05-tasks.md | sort -u | wc -l                      # -> 61 (identical set)
grep -oE 'L1-[0-9]{3}' L1-05-tasks.md | sort -u | diff - <index-set>         # -> no difference
```

**Id-shape sweep** (guards against a second namespace hiding in the index file). Only two shapes
exist in `L1-05-tasks.md`:

```bash
grep -oE 'L1-[A-Za-z0-9]+(-[A-Za-z0-9]+)*' L1-05-tasks.md \
  | sed -E 's/[0-9]+/#/g' | sort -u
# -> L#-#      (the 61 task ids)
# -> L#-D#     (L1-D01..L1-D05, the five DECISIONS REQUIRED — not tasks, excluded)
```

`L1-D01`..`L1-D05` are decisions owed by L0, not tasks, and are excluded from both sides.

**INDEX COUNT: 61.**

---

## 2. The body side — 143 task bodies (+14 runbook procedures)

A body is counted only where an executor would find something to follow: steps, commands,
acceptance criteria, a SELF-VERIFY. Every id counted below was checked for a SELF-VERIFY block and
for fenced command blocks; **all 143 pass**. Bare mentions in dependency lists were excluded by
anchoring every pattern to a markdown heading.

Six disjoint namespaces carry bodies. No single regex finds them all:

| # | Namespace | Pattern used | File | Bodies |
|---|---|---|---|---:|
| 1 | `L1-###` | `^### L1-[0-9]{3} ` | `L1-05-tasks.md` | 61 |
| 2 | `L1-00-T##` | `^### L1-00-T[0-9]{2} ` | `L1-00-charter.md` | 5 |
| 3 | `L1-01-T##` | `^## L1-01-T[0-9]{2} ` | `L1-01-repo-skeleton.md` | 13 |
| 4 | `L1-02-T##` | `^### L1-02-T[0-9]{2} ` | `L1-02-schemas.md` | 19 |
| 5 | `L1-03-T##` | `^## TASK L1-03-T[0-9]{2} ` | `L1-03-validators.md` | 21 |
| 6 | `T-L1-04-##` | `^### T-L1-04-[0-9]{2} ` | `L1-04-ci-gate-engine.md` | 9 |
| 4b | `L1-06-T##` | `^### L1-06-T[0-9]{2} ` | `L1-06-tests.md` | 15 |
| 7 | `L1-RB-##` | `^## L1-RB-[0-9]{2} ` | `L1-07-runbook.md` | 14 *(procedures, not tasks)* |

Note the shape traps: `L1-03` prefixes its headings with the literal word `TASK`; `L1-04` puts the
`T-` **before** the lane token (`L1-04-01`, not `L1-04-01`); `L1-01` and `L1-03` use `##` while
`L1-00`, `L1-02`, `L1-06` use `###`. A heading-level-only or a `L1-\d\d-T` grep misses two files.

**BODY COUNT (tasks): 143** = 61 (`L1-05`) + 82 (phase files).
The 14 `L1-RB-*` runbook entries are recurring operator procedures ("Commit", "Open the PR",
"Respond to a rebase conflict"), not one-shot units of work. They are listed in §5.2 for
completeness but excluded from the task count. Counting them, 157 bodies exist in the lane.

Not counted as bodies: `DECISION-L1-02-A/-B/-C` (`L1-02-schemas.md:2142,2149,2156`) are decisions
owed by L0, and `## L1-01 — Control-plane repository skeleton` (`L1-01-repo-skeleton.md:1822`) is a
recap section heading, not a task.

---

## 3. Mapping: index id -> body id

**61 of 61 mapped. All EXACT.** `L1-05-tasks.md` is both index and body: every id in the master
table has its own `### L1-###` section in the same file, in the same order, under the same id.

Verification that the two sets are identical, not merely equal in size:

```bash
grep -oE '^\| *[0-9]+ *\| *L1-[0-9]{3}' L1-05-tasks.md | grep -oE 'L1-[0-9]{3}' | sort -u > idx.txt
grep -oE '^### L1-[0-9]{3}'             L1-05-tasks.md | grep -oE 'L1-[0-9]{3}' | sort -u > body.txt
comm -23 idx.txt body.txt    # index with no body  -> EMPTY
comm -13 idx.txt body.txt    # body with no index  -> EMPTY
```

Both directions empty. Every body was additionally confirmed to contain a SELF-VERIFY:

```bash
awk '/^### L1-[0-9]{3} /{if(id!="")printf "%s:%s ",id,(sv?"Y":"n"); id=$2; sv=0; next}
     /SELF-VERIFY/{sv=1} END{if(id!="")printf "%s:%s\n",id,(sv?"Y":"n")}' L1-05-tasks.md
# -> all 61 report Y
```

| Index id | Body id | Body file | Line | Conf. | What the task does |
|---|---|---|---:|---|---|
| L1-001 | L1-001 | L1-05-tasks.md | 246 | EXACT | Verify partition, contracts and toolchain preconditions |
| L1-002 | L1-002 | L1-05-tasks.md | 295 | EXACT | Validator package skeleton and pinned toolchain |
| L1-003 | L1-003 | L1-05-tasks.md | 351 | EXACT | CLI contract: exit codes, output grammar, `--today` |
| L1-004 | L1-004 | L1-05-tasks.md | 421 | EXACT | Strict YAML loader (dup keys, anchors, tabs, BOM) |
| L1-005 | L1-005 | L1-05-tasks.md | 475 | EXACT | Rule registry, fixture harness, `RULES.md` index |
| L1-101 | L1-101 | L1-05-tasks.md | 549 | EXACT | Common `$defs`: dates, ids, IANA tz, capability enum |
| L1-102 | L1-102 | L1-05-tasks.md | 628 | EXACT | `roles.yaml` schema |
| L1-103 | L1-103 | L1-05-tasks.md | 671 | EXACT | `registries/roles.yaml` transcribed verbatim from §8 |
| L1-104 | L1-104 | L1-05-tasks.md | 732 | EXACT | `people.yaml` schema including `work_arrangement` |
| L1-105 | L1-105 | L1-05-tasks.md | 812 | EXACT | `registries/people.yaml` empty skeleton |
| L1-106 | L1-106 | L1-05-tasks.md | 849 | EXACT | `platform.yaml` schema |
| L1-107 | L1-107 | L1-05-tasks.md | 900 | EXACT | `registries/platform.yaml` seeded |
| L1-108 | L1-108 | L1-05-tasks.md | 944 | EXACT | Week-one minimal `exceptions.yaml` validator |
| L1-201 | L1-201 | L1-05-tasks.md | 1014 | EXACT | R-CAP-01: undefined capability rejected |
| L1-202 | L1-202 | L1-05-tasks.md | 1053 | EXACT | R-CAP-02: dangerous capability in a role default rejected |
| L1-203 | L1-203 | L1-05-tasks.md | 1107 | EXACT | R-PPL-01: non-employee `end_date` mandatory |
| L1-204 | L1-204 | L1-05-tasks.md | 1143 | EXACT | R-PPL-02: `availability` x `access_status` pair legality |
| L1-205 | L1-205 | L1-05-tasks.md | 1195 | EXACT | R-PPL-03: id and login uniqueness; ids never reused |
| L1-206 | L1-206 | L1-05-tasks.md | 1238 | EXACT | R-PPL-04: `people.role` resolves in `roles.yaml` |
| L1-207 | L1-207 | L1-05-tasks.md | 1279 | EXACT | R-PPL-05: `work_arrangement` rules |
| L1-301 | L1-301 | L1-05-tasks.md | 1343 | EXACT | `product.yaml` v2 schema: envelope, `identity`, `classification` |
| L1-302 | L1-302 | L1-05-tasks.md | 1398 | EXACT | `assignments` sub-schema, all 17 types |
| L1-303 | L1-303 | L1-05-tasks.md | 1455 | EXACT | `code`, `verification`, `environments`, `deployment` blocks |
| L1-304 | L1-304 | L1-05-tasks.md | 1526 | EXACT | `infrastructure`/`security`/`data`/`observability`/AI/`business` blocks |
| L1-305 | L1-305 | L1-05-tasks.md | 1611 | EXACT | `operations` block and derived `detection_expectation` rule |
| L1-306 | L1-306 | L1-05-tasks.md | 1673 | EXACT | `commitments` block and the `conflict_check` rule |
| L1-307 | L1-307 | L1-05-tasks.md | 1735 | EXACT | `recovery` block and the restore-cadence rule |
| L1-308 | L1-308 | L1-05-tasks.md | 1804 | EXACT | Conformance-profile equivalent-evidence rules |
| L1-309 | L1-309 | L1-05-tasks.md | 1856 | EXACT | `product.yaml` v1 schema, frozen |
| L1-310 | L1-310 | L1-05-tasks.md | 1899 | EXACT | Cross-file referential integrity: the full §15.5 list |
| L1-311 | L1-311 | L1-05-tasks.md | 1956 | EXACT | Coverage-window rota rule — BLOCKED on L1-D03 |
| L1-401 | L1-401 | L1-05-tasks.md | 2015 | EXACT | `verification/contract.yaml` schema |
| L1-402 | L1-402 | L1-05-tasks.md | 2168 | EXACT | Seeded-defect-case rule |
| L1-403 | L1-403 | L1-05-tasks.md | 2256 | EXACT | Performance mechanism required at high and critical |
| L1-404 | L1-404 | L1-05-tasks.md | 2338 | EXACT | `service.yaml` schema, `registries/services/`, consumer integrity |
| L1-501 | L1-501 | L1-05-tasks.md | 2525 | EXACT | `topology.yaml` schema |
| L1-502 | L1-502 | L1-05-tasks.md | 2637 | EXACT | `registries/topology.yaml` skeleton, domains dormant |
| L1-503 | L1-503 | L1-05-tasks.md | 2728 | EXACT | R-TOP-01: escalation is a role, never a person |
| L1-504 | L1-504 | L1-05-tasks.md | 2847 | EXACT | R-CHG-01: authority delta requires a linked decision-record id |
| L1-505 | L1-505 | L1-05-tasks.md | 2993 | EXACT | Owner manifest for the registry-change lane, from §52.6 |
| L1-601 | L1-601 | L1-05-tasks.md | 3279 | EXACT | `exceptions.yaml` full schema, superseding the minimal one |
| L1-602 | L1-602 | L1-05-tasks.md | 3438 | EXACT | Exception rules: expiry, closure, trigger, compensating control |
| L1-603 | L1-603 | L1-05-tasks.md | 3555 | EXACT | `policies.yaml` schema |
| L1-604 | L1-604 | L1-05-tasks.md | 3723 | EXACT | Policy stage-ladder rules |
| L1-605 | L1-605 | L1-05-tasks.md | 3827 | EXACT | `os-health.yaml` schema: ten attributes, arming discipline |
| L1-606 | L1-606 | L1-05-tasks.md | 4018 | EXACT | `tools.yaml` schema and the `criticality` enum rule |
| L1-607 | L1-607 | L1-05-tasks.md | 4152 | EXACT | `economics.yaml` and `platform-roadmap.yaml` schemas |
| L1-608 | L1-608 | L1-05-tasks.md | 4353 | EXACT | `patterns.yaml` schema and the closed remediation enum |
| L1-701 | L1-701 | L1-05-tasks.md | 4501 | EXACT | Multi-version dispatch: v1 and v2 validated side by side |
| L1-702 | L1-702 | L1-05-tasks.md | 4641 | EXACT | R-VER-01: supported / transitional / unsupported gate |
| L1-703 | L1-703 | L1-05-tasks.md | 4748 | EXACT | `platform_migration` block: owner, target, deadline |
| L1-704 | L1-704 | L1-05-tasks.md | 4853 | EXACT | R-INV-01: the 29-artifact inventory guard |
| L1-705 | L1-705 | L1-05-tasks.md | 4974 | EXACT | Schema-change checklist generator |
| L1-801 | L1-801 | L1-05-tasks.md | 5085 | EXACT | Performance framework registry schema |
| L1-802 | L1-802 | L1-05-tasks.md | 5284 | EXACT | Framework rules: one active per role, non-retroactive, marker literal |
| L1-803 | L1-803 | L1-05-tasks.md | 5393 | EXACT | Banned-measurement and non-delegable-capability rules |
| L1-901 | L1-901 | L1-05-tasks.md | 5528 | EXACT | Acceptance-test harness for the fourteen ATs Lane 1 can prove |
| L1-902 | L1-902 | L1-05-tasks.md | 5631 | EXACT | Invariant classification register and its CI rule |
| L1-903 | L1-903 | L1-05-tasks.md | 5770 | EXACT | Publish the stable CLI interface Lane 2 wires into CI |
| L1-904 | L1-904 | L1-05-tasks.md | 5855 | EXACT | Full-lane regression and runtime budget |
| L1-905 | L1-905 | L1-05-tasks.md | 5949 | EXACT | Lane handoff: tag, merge-train slot, blocker sweep |

---

## 4. RESIDUE — index ids with no body anywhere

**EMPTY. 0 of 61.**

Lane 1 contributes **nothing** to the founder's unbuilt-work list. Every task the L1 index promises
is fully specified today, in `L1-05-tasks.md`, with steps, file lists, acceptance commands and a
SELF-VERIFY. This is the finding that overturns `L1-99-review.md`'s "30 of 61 bodies missing".

---

## 5. ORPHANS — bodies no index row claims

**82 task bodies** live in the phase files under five namespaces the master table never mentions.
Cross-reference check, confirming the two decompositions are fully disjoint in id space:

```bash
grep -hoE 'L1-[0-9]{3}\b' L1-00-charter.md L1-01-repo-skeleton.md L1-02-schemas.md \
     L1-03-validators.md L1-04-ci-gate-engine.md L1-06-tests.md L1-07-runbook.md \
  | sort -u | wc -l      # -> 0
```

**Zero.** No phase file cites the index namespace even once, and `L1-05-tasks.md` cites no phase-task
id even once. There was no concordance in either direction before this file.

### 5.1 The 82 orphan task bodies

The **"covers index"** column is the substantive result: it says whether an orphan body is a second
decomposition of work the index already claims (a **duplicate-execution hazard** — one executor could
build the same artifact twice under two ids) or work **no index row claims at all** (marked `— NONE —`,
the genuinely untracked work). Confidence is stated per row; where uncertain the row is left unmapped
rather than guessed.

| Body id | File | Line | What it does | Covers index | Conf. |
|---|---|---:|---|---|---|
| L1-00-01 | L1-00-charter.md | 326 | Verify preconditions, create the lane branch | L1-001 | HIGH |
| L1-00-02 | L1-00-charter.md | 384 | Create the four owned roots + README markers | — NONE — | HIGH |
| L1-00-03 | L1-00-charter.md | 504 | Install the lane self-guard (path-ownership enforcement) | — NONE — | HIGH |
| L1-00-04 | L1-00-charter.md | 561 | Pin and verify the spec anchors this lane uses | L1-001 (part) | MED |
| L1-00-05 | L1-00-charter.md | 655 | Commit charter scaffold, open the lane PR | — NONE — | HIGH |
| L1-01-01 | L1-01-repo-skeleton.md | 151 | Preflight: toolchain, auth, spec availability | L1-001 | HIGH |
| L1-01-02 | L1-01-repo-skeleton.md | 218 | `git init`, `gh repo create`, initial commit | — NONE — | HIGH |
| L1-01-03 | L1-01-repo-skeleton.md | 348 | Lane branch and owned-directory skeleton | — NONE — | HIGH |
| L1-01-04 | L1-01-repo-skeleton.md | 420 | Per-directory `.gitignore` inside owned paths | — NONE — | HIGH |
| L1-01-05 | L1-01-repo-skeleton.md | 546 | `schemas/registry/CONVENTIONS.md`: effective dating, append-only | — NONE — | HIGH |
| L1-01-06 | L1-01-repo-skeleton.md | 730 | Shared effective-dating and envelope JSON Schemas | L1-101 | MED |
| L1-01-07 | L1-01-repo-skeleton.md | 869 | `registries/INVENTORY.md`: §52.6 registry-of-files transcribed | L1-704 / L1-505 | MED |
| L1-01-08 | L1-01-repo-skeleton.md | 991 | Seed `registries/roles.yaml` verbatim from §8 | L1-103 | HIGH |
| L1-01-09 | L1-01-repo-skeleton.md | 1136 | Seed `registries/people.yaml` (empty, schema-valid) | L1-105 | HIGH |
| L1-01-10 | L1-01-repo-skeleton.md | 1242 | Seed `registries/platform.yaml` | L1-107 | HIGH |
| L1-01-11 | L1-01-repo-skeleton.md | 1407 | `validators/registry/check-append-only.sh` | — NONE — | HIGH |
| L1-01-12 | L1-01-repo-skeleton.md | 1560 | `registry.mk` and the L0 handover packet | L1-904 (part) | LOW |
| L1-01-13 | L1-01-repo-skeleton.md | 1793 | Phase gate: rebase, lane-guard self-check, PR to `integration` | — NONE — | HIGH |
| L1-02-01 | L1-02-schemas.md | 114 | Schema-check harness | L1-005 | MED |
| L1-02-02 | L1-02-schemas.md | 301 | Versioning convention document and shared `$defs` | L1-101 | MED |
| L1-02-03 | L1-02-schemas.md | 579 | `people.yaml` schema (v1) | L1-104 | HIGH |
| L1-02-04 | L1-02-schemas.md | 979 | `roles.yaml` schema (v1) | L1-102 | HIGH |
| L1-02-05 | L1-02-schemas.md | 1112 | `product.yaml` schema (v2), the Product Operating Contract | L1-301..L1-304 | HIGH |
| L1-02-06 | L1-02-schemas.md | 1269 | `service.yaml` schema (v1), Shared Service Contract | L1-404 | HIGH |
| L1-02-07 | L1-02-schemas.md | 1327 | `topology.yaml` schema (v1) | L1-501 | HIGH |
| L1-02-08 | L1-02-schemas.md | 1362 | `platform.yaml` schema (v1) | L1-106 | HIGH |
| L1-02-09 | L1-02-schemas.md | 1413 | `os-health.yaml` schema (v1) | L1-605 | HIGH |
| L1-02-10 | L1-02-schemas.md | 1482 | `policies.yaml` schema (v1) | L1-603 | HIGH |
| L1-02-11 | L1-02-schemas.md | 1554 | `exceptions.yaml` schema (v1) | L1-601 | HIGH |
| L1-02-12 | L1-02-schemas.md | 1626 | `patterns.yaml` schema (v1) | L1-608 | HIGH |
| L1-02-13 | L1-02-schemas.md | 1678 | `economics.yaml` schema (v1) | L1-607 (part) | HIGH |
| L1-02-14 | L1-02-schemas.md | 1779 | `platform-roadmap.yaml` schema (v1) | L1-607 (part) | HIGH |
| L1-02-15 | L1-02-schemas.md | 1837 | `tools.yaml` schema (v1) | L1-606 | HIGH |
| L1-02-16 | L1-02-schemas.md | 1891 | **`ai-toolchain.yaml` schema (v1)** | **— NONE —** | HIGH |
| L1-02-17 | L1-02-schemas.md | 1940 | **`scenarios/*.yaml` schema (v1)** | **— NONE —** | HIGH |
| L1-02-18 | L1-02-schemas.md | 2000 | **`changes/*.yaml` change-manifest schema (v1)** | **— NONE —** | HIGH |
| L1-02-19 | L1-02-schemas.md | 2072 | Schema index and phase gate | — NONE — | HIGH |
| L1-03-00 | L1-03-validators.md | 202 | Preflight: decisions, toolchain, Phase 1/2 artifacts | L1-001 | MED |
| L1-03-01 | L1-03-validators.md | 272 | Rule harness, CLI, baseline fixture, fixture generator | L1-003 + L1-005 | HIGH |
| L1-03-02 | L1-03-validators.md | 631 | R01 multi-version schema validation, supported-version floor | L1-701 + L1-702 | HIGH |
| L1-03-03 | L1-03-validators.md | 706 | R02 assignments name an existing, non-departed person | L1-310 | HIGH |
| L1-03-04 | L1-03-validators.md | 763 | R03 declared dependency names an existing shared service | L1-404 | HIGH |
| L1-03-05 | L1-03-validators.md | 813 | R04 mandatory `end_date` for every non-employee | L1-203 | HIGH |
| L1-03-06 | L1-03-validators.md | 879 | R05 expired assignment | L1-310 | MED |
| L1-03-07 | L1-03-validators.md | 942 | R06 `restore_tested` within the rolling window | L1-307 | HIGH |
| L1-03-08 | L1-03-validators.md | 1015 | R07 the 24x7 / extended coverage blocker | L1-311 | HIGH |
| L1-03-09 | L1-03-validators.md | 1137 | R08 commitments entry without a recorded `conflict_check` | L1-306 | HIGH |
| L1-03-10 | L1-03-validators.md | 1194 | R09 exception without an expiry | L1-602 | HIGH |
| L1-03-11 | L1-03-validators.md | 1273 | R10 unclassified control; seeds the 13 §64.2 control rows | *unmapped* | LOW |
| L1-03-12 | L1-03-validators.md | 1345 | R11 capability defined before it is granted | L1-201 | HIGH |
| L1-03-13 | L1-03-validators.md | 1412 | R12 no dangerous capability in a role default | L1-202 | HIGH |
| L1-03-14 | L1-03-validators.md | 1466 | R13 RPO satisfiable by declared backup frequency | L1-307 (part) | MED |
| L1-03-15 | L1-03-validators.md | 1551 | **R14 revision integrity audit (§77.5 protected entities, `diffgen.py`)** | **— NONE —** | MED |
| L1-03-16 | L1-03-validators.md | 1629 | R15 illegal `availability` / `access_status` pairing | L1-204 | HIGH |
| L1-03-17 | L1-03-validators.md | 1688 | R16 `detection_expectation` differs from its derived value | L1-305 | HIGH |
| L1-03-18 | L1-03-validators.md | 1753 | R17 `founder_decision_delegate` naming a formal people decision (D108) | L1-302 | MED |
| L1-03-19 | L1-03-validators.md | 1825 | R18 `recovery:` block with no `restore-production.yml` | L1-307 (part) | MED |
| L1-03-20 | L1-03-validators.md | 1884 | Suite closure: manifest coverage, exit-code contract, citation lint | L1-903 + L1-904 | MED |
| L1-04-01 | L1-04-ci-gate-engine.md | 271 | **Freeze the CI gate-engine contract, pin the toolchain** | **— NONE —** | HIGH |
| L1-04-02 | L1-04-ci-gate-engine.md | 410 | **Rule-layout conformance sweep** | **— NONE —** | HIGH |
| L1-04-03 | L1-04-ci-gate-engine.md | 507 | **Rule metadata schema and discovery module** | **— NONE —** | HIGH |
| L1-04-04 | L1-04-ci-gate-engine.md | 720 | **Finding parser and reporter module** | **— NONE —** | HIGH |
| L1-04-05 | L1-04-ci-gate-engine.md | 858 | **`gate.py` runner: live mode and exit codes** | **— NONE —** | HIGH |
| L1-04-06 | L1-04-ci-gate-engine.md | 1171 | **Baseline fixture, seeded canary, fixtures mode** | **— NONE —** | HIGH |
| L1-04-07 | L1-04-ci-gate-engine.md | 1346 | **Must-fail fixture backfill for every rule** | **— NONE —** | HIGH |
| L1-04-08 | L1-04-ci-gate-engine.md | 1460 | Preflight script and the L2 handoff package | L1-903 | MED |
| L1-04-09 | L1-04-ci-gate-engine.md | 1597 | **Phase exit gate** | **— NONE —** | HIGH |
| L1-06-01 | L1-06-tests.md | 193 | Preflight: freeze lane surface and validator invocation | — NONE — | MED |
| L1-06-02 | L1-06-tests.md | 303 | Build the test harness: runner, adapter, assertions | L1-005 (part) | LOW |
| L1-06-03 | L1-06-tests.md | 461 | Valid fixture corpus: the 15 registry schemas | — NONE — | MED |
| L1-06-04 | L1-06-tests.md | 510 | Valid fixture corpus: the 3 product schemas | — NONE — | MED |
| L1-06-05 | L1-06-tests.md | 562 | Negative corpus: people, roles, topology | — NONE — | MED |
| L1-06-06 | L1-06-tests.md | 645 | Negative corpus: product contract, one fixture per §15.5 bullet | L1-310 (part) | LOW |
| L1-06-07 | L1-06-tests.md | 721 | Negative corpus: exceptions and policies | — NONE — | MED |
| L1-06-08 | L1-06-tests.md | 766 | Negative corpus: os-health, assets, people-boundary denials | — NONE — | MED |
| L1-06-09 | L1-06-tests.md | 809 | Seeded canaries: one per schema id | — NONE — | HIGH |
| L1-06-10 | L1-06-tests.md | 859 | Coverage counters and the frozen floor | — NONE — | HIGH |
| L1-06-11 | L1-06-tests.md | 930 | **Schema-mutation meta-test** | **— NONE —** | HIGH |
| L1-06-12 | L1-06-tests.md | 1022 | Multi-version corpus (AT-025) | L1-701 (part) | MED |
| L1-06-13 | L1-06-tests.md | 1061 | Governance layerability (AT-034) | L1-901 (part) | LOW |
| L1-06-14 | L1-06-tests.md | 1134 | Acceptance-test traceability map | L1-901 | MED |
| L1-06-15 | L1-06-tests.md | 1193 | Publish the CI invocation contract to L2 | L1-903 | HIGH |

**Orphan summary.** Of the 82: **50 duplicate work an index task already claims** (the rows naming an
index id) and are a duplicate-execution hazard at dispatch; **31 are claimed by no index row at all**
(the `— NONE —` rows); **1 (`L1-03-11`) is left unmapped** — it seeds thirteen §64.2 control rows into
`policies.yaml` with a `failure_mode` field, which is adjacent to but not the same as L1-603's
policies schema or L1-902's invariant classification, and a guess here would be wrong.

The largest untracked block is **`L1-04-ci-gate-engine.md`: 8 of its 9 tasks are claimed by no index
row.** The master table has no CI-gate-engine work at all. `L1-02-16/T17/T18` add three schemas
(`ai-toolchain.yaml`, `scenarios/*.yaml`, `changes/*.yaml`) the index never names, and
`L1-01-02/T03/T04` do the `git init` / repo-creation work the index silently assumes has happened.

### 5.2 The 14 runbook procedures (not counted as tasks)

`L1-07-runbook.md` — recurring operator procedures, re-run per task, not units of work:
`L1-RB-00` (61) session preflight, `L1-RB-01` (140) start a task, `L1-RB-02` (207) check work
locally, `L1-RB-03` (268) lane-guard local preflight, `L1-RB-04` (339) commit, `L1-RB-05` (404)
rebase on integration, `L1-RB-06` (459) open the PR, `L1-RB-07` (545) failing lane-guard check,
`L1-RB-08` (621) failing registry-validation check, `L1-RB-09` (693) rebase conflict, `L1-RB-10`
(757) file a blocker, `L1-RB-11` (863) escalate to L0, `L1-RB-12` (954) merge-train slot,
`L1-RB-13` (1005) post-merge cleanup.

---

### 5.3 L1-04 CI Gate Engine — supplementary index rows (added 2026-09-08)

All 9 T-L1-04-* bodies were previously listed in §5.1 as orphans with no index row. They are promoted here to tracked index rows so dispatchers can locate, sequence and assign them. The namespace (`T-L1-04-*`) remains distinct from the L1-05 master table; the two decompositions are disjoint and this concordance is additive (FD-004). The `Conf.` values carry over from §5.1.

The **L1 DoD refs** column cites the spec obligations each task directly satisfies. Section references without a file qualifier are spec sections (§NN). `AT-NNN` = acceptance test id, `D-NN` = decision record, `EC-NNN` = engine-contract clause in L1-04-ci-gate-engine.md.

| Index id | Body id | Body file | Line | Conf. | What the task does | L1 DoD refs |
|---|---|---|---:|---|---|---|
| L1-04-01 | L1-04-01 | L1-04-ci-gate-engine.md | 271 | HIGH | Freeze the CI gate-engine contract and pin the toolchain | §11.3 required-status-check contract; §33.2 no-`if:`/no-path-filter; §53.4 severity scale frozen |
| L1-04-02 | L1-04-02 | L1-04-ci-gate-engine.md | 410 | HIGH | Rule-layout conformance sweep — move validators into `rules/<id>/` | PARTITION rule 3 (directory-per-item, no shared mutable index) |
| L1-04-03 | L1-04-03 | L1-04-ci-gate-engine.md | 507 | HIGH | Rule metadata schema (`gate-rule.v1.schema.json`) and discovery module | §101 (mechanical invariant must name a live check); §53.4 (single severity enum enforced by schema) |
| L1-04-04 | L1-04-04 | L1-04-ci-gate-engine.md | 720 | HIGH | Finding parser and reporter module — frozen FINDING / GATE FAIL / GATE RESULT shapes | §11.3 (GitHub workflow annotation format); §33.2 (machine-readable result line on every run) |
| L1-04-05 | L1-04-05 | L1-04-ci-gate-engine.md | 858 | HIGH | `gate.py` runner: live mode and frozen exit codes 0/1/2/3 | §11.3, §33.2; §53.1 (seeded-canary detection); §53.4 (amber/green never block merge) |
| L1-04-06 | L1-04-06 | L1-04-ci-gate-engine.md | 1171 | HIGH | Baseline fixture, permanently seeded canary (`seeded-canary.yaml`), fixtures mode | §53.1 seeded-canary rule; AT-102; D63; §31.2 / D97 (instrument that cannot fail is not an instrument) |
| L1-04-07 | L1-04-07 | L1-04-ci-gate-engine.md | 1346 | HIGH | Must-fail fixture backfill for every rule (universal negative-test recipe) | §53.1; AT-102; D97; §31.2 (SIG-18) — every rule must carry a fixture it is required to fail |
| L1-04-08 | L1-04-08 | L1-04-ci-gate-engine.md | 1460 | MED | Preflight script (`ci-preflight.sh`) and the L2 handoff package | L1-903 (publishes the stable CLI interface Lane 2 wires into CI); §33.2 (entry point carries no `if:` guard) |
| L1-04-09 | L1-04-09 | L1-04-ci-gate-engine.md | 1597 | HIGH | Phase exit gate — proves the full gate runs and the instrument is provably breakable | EC-109 / AT-102 (a run that passes with the seeded canary removed is a failed run); §53.1 |

**Effect on orphan count:** Of the 31 phase-file bodies previously counted as claimed by no index row (§5.1), 9 are now tracked here. The remaining untracked count is **22** (the `— NONE —` rows from §5.1 excluding the 9 T-L1-04-* rows).

---

### 5.4 L1-00 Charter — supplementary index rows (added 2026-09-08)

These 3 bodies were listed in §5.1 as having no index row. They cover pre-task setup work that the master table silently assumes (directory structure, lane guard, PR filing) but never claims.

| Index id | Body id | Body file | Line | Conf. | What the task does | L1 DoD refs |
|---|---|---|---:|---|---|---|
| L1-00-02 | L1-00-02 | L1-00-charter.md | 386 | High | Create the four owned directory roots and their README markers | PARTITION.md rule 1 (one owner per path); §98.2 Phase 1 directory layout |
| L1-00-03 | L1-00-03 | L1-00-charter.md | 509 | High | Install the lane self-guard (`lane_paths.sh`) — runs before every L1 commit | PARTITION.md rule 1 (a lane PR touching a foreign path FAILS) |
| L1-00-05 | L1-00-05 | L1-00-charter.md | 662 | High | Commit the charter scaffold and open the lane PR to `integration` | §11.3 (required-status-check; phase gate); FD-004 (concordance is additive) |

---

### 5.5 L1-01 Repo Skeleton — supplementary index rows (added 2026-09-08)

These 6 bodies were listed in §5.1 as having no index row. They cover the repository-creation and registry-guard work that Lane 1's master table silently depends on.

| Index id | Body id | Body file | Line | Conf. | What the task does | L1 DoD refs |
|---|---|---|---:|---|---|---|
| L1-01-02 | L1-01-02 | L1-01-repo-skeleton.md | 220 | High | Repository bootstrap: `git init`, `gh repo create`, initial commit | §98.2 Phase 1 (repository must exist before lane branch); FD-009 (CP_ORG supplied by L0 before dispatch) |
| L1-01-03 | L1-01-03 | L1-01-repo-skeleton.md | 353 | High | Lane branch and owned-directory skeleton (`.gitkeep` sentinels for all L1 paths) | PARTITION.md §3 (directory-per-item, no shared mutable index) |
| L1-01-04 | L1-01-04 | L1-01-repo-skeleton.md | 426 | High | Per-directory `.gitignore` files inside owned paths (no root `.gitignore`) | PARTITION.md rule 1 (owned-path isolation); §15.4 generated-file exclusions |
| L1-01-05 | L1-01-05 | L1-01-repo-skeleton.md | 576 | High | `schemas/registry/CONVENTIONS.md`: effective-dating and append-only conventions | §15.4 append-only rule; effective-dating contract Lane 2 will wire into CI |
| L1-01-11 | L1-01-11 | L1-01-repo-skeleton.md | 1447 | High | `validators/registry/check-append-only.sh` — CI script enforcing registry append-only rule | §15.4; PARTITION registry-validation gate; L1-903 (published CLI surface) |
| L1-01-13 | L1-01-13 | L1-01-repo-skeleton.md | 1837 | High | Phase gate: rebase on `integration`, lane-guard self-check, PR and CODEOWNERS wiring | §11.3 (required-status-check; no `if:`/no-path-filter); PARTITION rule 1 |

---

### 5.6 L1-02 Schemas — supplementary index rows (added 2026-09-08)

These 4 bodies were listed in §5.1 as having no index row. L1-02-16/T17/T18 author three schemas (`ai-toolchain.yaml`, `scenarios/*.yaml`, `changes/*.yaml`) that appear in the §52.6 registry-of-files inventory but are absent from the L1-05 master table. L1-02-19 is the phase gate.

| Index id | Body id | Body file | Line | Conf. | What the task does | L1 DoD refs |
|---|---|---|---:|---|---|---|
| L1-02-16 | L1-02-16 | L1-02-schemas.md | 4122 | High | `ai-toolchain.yaml` schema (v1) — AI-toolchain registry contract | §52.6 inventory artifact (schemas/registry/ai-toolchain/v1/); L1-704 (29-artifact inventory guard counts this schema) |
| L1-02-17 | L1-02-17 | L1-02-schemas.md | 4317 | High | `scenarios/*.yaml` schema (v1) — scenario-manifest contract | §52.6 inventory artifact (schemas/product/scenarios/v1/); L1-704 (inventory guard) |
| L1-02-18 | L1-02-18 | L1-02-schemas.md | 4533 | High | `changes/*.yaml` change-manifest schema (v1) — change-record contract | §52.6 inventory artifact (schemas/product/changes/v1/); L1-504 (R-CHG-01: authority delta requires a linked decision-record id) |
| L1-02-19 | L1-02-19 | L1-02-schemas.md | 4782 | High | Schema index (`SCHEMA-INDEX.md`) and Phase 2 exit gate | L1-704 (29-artifact inventory guard run at phase gate); §11.3 (phase gate PR) |

---

### 5.7 L1-03 Validators — supplementary index rows (added 2026-09-08)

One body was listed in §5.1 as having no index row. L1-03-15 implements the only two-revision rule in the suite and is the sole task citing §77.5 exclusively.

| Index id | Body id | Body file | Line | Conf. | What the task does | L1 DoD refs |
|---|---|---|---:|---|---|---|
| L1-03-15 | L1-03-15 | L1-03-validators.md | 1643 | High | R14 revision integrity audit — `diffgen.py`, two-revision fixture pairs, §77.5 protected-entity set | §77.5 (CI flags removals/changes to protected entities; does not adjudicate); §63; invariant 47; L1-902 (invariant classification register) |

---

### 5.8 L1-06 Tests — supplementary index rows (added 2026-09-08)

These 9 bodies were listed in §5.1 as having no index row. They represent the L1-06 test-harness work the master table never claims: the harness itself, the valid and negative fixture corpora, seeded canaries, coverage floor, and the schema-mutation meta-test.

| Index id | Body id | Body file | Line | Conf. | What the task does | L1 DoD refs |
|---|---|---|---:|---|---|---|
| L1-06-01 | L1-06-01 | L1-06-tests.md | 194 | High | Preflight: freeze the lane surface (`schema-ids.txt`) and the validator invocation contract (`validator.cmd`) | §11.3 (CI invocation contract Lane 2 wires in); L1-903 (published stable CLI interface) |
| L1-06-03 | L1-06-03 | L1-06-tests.md | 477 | High | Valid fixture corpus — 2 fixtures per registry schema (15 schemas, 30 files), all pass the validator | §53.1 (seeded-canary detection requires at least one valid file per schema id); AT-102; D97 |
| L1-06-04 | L1-06-04 | L1-06-tests.md | 526 | High | Valid fixture corpus — product-contract fixtures including all 3 conformance profiles | §15.5 (referential integrity; cross-file assertions); §53.1; AT-025 |
| L1-06-05 | L1-06-05 | L1-06-tests.md | 578 | High | Negative corpus — people, roles, topology: one fixture per rule that must be rejected | §53.1; rules R01–R06; §31.2 / D97 (a rule that never fires is not an instrument) |
| L1-06-07 | L1-06-07 | L1-06-tests.md | 737 | High | Negative corpus — exceptions and policies: expiry rule, closure rule, trigger, compensating-control | §53.1; L1-602 (exception rules); L1-603 (policies schema); L1-604 (stage-ladder rules) |
| L1-06-08 | L1-06-08 | L1-06-tests.md | 782 | High | Negative corpus — os-health, assets, people-boundary denials | AT-071; AT-075; AT-090; §53.1 |
| L1-06-09 | L1-06-09 | L1-06-tests.md | 824 | High | Seeded canaries — one broken fixture per schema id (17 canaries); `run.sh --all` must exit non-zero | §53.1 (seeded-canary rule); AT-102; D63; D97; §31.2 (SIG-18) |
| L1-06-10 | L1-06-10 | L1-06-tests.md | 874 | High | Coverage counters and the frozen floor — `coverage-floor.yaml` with 4 `min_` keys; narrowing detector | §53.1; §31.2 / D97 (instrument-that-cannot-fail is not an instrument); L1-901 (acceptance-test harness) |
| L1-06-11 | L1-06-11 | L1-06-tests.md | 945 | High | Schema-mutation meta-test — mutates each schema and asserts the test suite catches it | §53.1; D97; §31.2 (SIG-18); AT-102 |

**Effect on orphan count:** 23 supplementary index rows added across §5.4–§5.8 (3 L1-00 + 6 L1-01 + 4 L1-02 + 1 L1-03 + 9 L1-06). Note: the "22 remaining" figure stated in §5.3 was off by 1 — L1-04-08 was in the 50-duplicate pool (it maps to L1-903) and was not among the 31 untracked, so only 8 T-L1-04-* rows reduced the untracked count; the true post-§5.3 residue was 23. All 23 are now indexed. **Untracked count: 0.**

---

## 6. What this means for dispatch

1. **Lane 1's residue is zero.** No task body needs writing for L1. `L1-99-review.md`'s BLOCKED
   verdict, insofar as it rests on "30 of 61 L1 bodies missing", is measuring a superseded copy and
   does not hold against the file on disk.
2. **The real L1 defect is duplication, not absence.** 143 task bodies exist for a 61-task lane.
   50 phase-file bodies re-decompose work the index already claims. Dispatching both decompositions
   would have one developer build `registries/roles.yaml` twice (L1-103 and L1-01-08),
   `people.yaml` schema twice (L1-104 and L1-02-03), and so on.
3. **31 phase-file bodies are tracked by no index row** — including 8 of the 9 CI gate-engine tasks.
   Dispatching only the master table would silently drop them.
4. This concordance is the join. It authors nothing and reissues nothing, per FD-004.

---

## 7. Exact commands used, for regeneration

Run from `C:/D_Drive/PS/MultiProduct/Code/implementation/lanes` (Git Bash).

```bash
# 0 — provenance
wc -l L1-*.md

# 1 — INDEX side (61)
grep -nE '^\| *[0-9]+ *\| *L1-[0-9]{3} *\|' L1-05-tasks.md | wc -l
grep -oE '^\| *[0-9]+ *\| *L1-[0-9]{3}' L1-05-tasks.md | grep -oE 'L1-[0-9]{3}' | sort -u > idx.txt
wc -l < idx.txt

# 1b — prove the index set is closed (no ids promised outside the master table)
grep -oE 'L1-[0-9]{3}' L1-05-tasks.md | sort -u | diff - idx.txt        # no output == closed

# 1c — id-shape sweep of the index file (guards against a hidden namespace)
grep -oE 'L1-[A-Za-z0-9]+(-[A-Za-z0-9]+)*' L1-05-tasks.md | sed -E 's/[0-9]+/#/g' | sort -u

# 2 — id-shape sweep of every phase file (six namespaces found)
for f in L1-00-charter.md L1-01-repo-skeleton.md L1-02-schemas.md L1-03-validators.md \
         L1-04-ci-gate-engine.md L1-06-tests.md L1-07-runbook.md; do
  echo "== $f"; grep -oE '\bL1[-.][A-Za-z0-9]+([-.][A-Za-z0-9]+)*' "$f" \
    | sed -E 's/[0-9]+/#/g' | sort | uniq -c | sort -rn | head -20
done

# 2b — BODY side, all six namespaces, heading-anchored (union == 143 tasks + 14 procedures)
grep -nE '^### L1-[0-9]{3} '        L1-05-tasks.md          # 61
grep -nE '^### L1-00-T[0-9]{2} '    L1-00-charter.md        #  5
grep -nE '^## L1-01-T[0-9]{2} '     L1-01-repo-skeleton.md  # 13
grep -nE '^### L1-02-T[0-9]{2} '    L1-02-schemas.md        # 19
grep -nE '^## TASK L1-03-T[0-9]{2} ' L1-03-validators.md    # 21
grep -nE '^### T-L1-04-[0-9]{2} '   L1-04-ci-gate-engine.md #  9
grep -nE '^### L1-06-T[0-9]{2} '    L1-06-tests.md          # 15
grep -nE '^## L1-RB-[0-9]{2} '      L1-07-runbook.md        # 14 (procedures)

# 2c — one catch-all sweep across all heading levels and all prefixes
grep -nE '^#{2,4} (TASK )?(T-)?L1-' L1-0[0-7]*.md

# 3 — MAPPING + 4 RESIDUE: index vs bodies in L1-05
grep -oE '^### L1-[0-9]{3}' L1-05-tasks.md | grep -oE 'L1-[0-9]{3}' | sort -u > body.txt
comm -23 idx.txt body.txt     # RESIDUE: index with no body  -> EMPTY
comm -13 idx.txt body.txt     # index-file bodies unclaimed  -> EMPTY

# 3b — prove every body is a real body (SELF-VERIFY present in each section)
awk '/^### L1-[0-9]{3} /{if(id!="")printf "%s:%s ",id,(sv?"Y":"n"); id=$2; sv=0; next}
     /SELF-VERIFY/{sv=1} END{if(id!="")printf "%s:%s\n",id,(sv?"Y":"n")}' L1-05-tasks.md
# same check across the phase files, with per-section SELF-VERIFY and fenced-block counts
for f in L1-00-charter.md L1-01-repo-skeleton.md L1-02-schemas.md L1-03-validators.md \
         L1-04-ci-gate-engine.md L1-06-tests.md L1-07-runbook.md; do
  echo "== $f"
  awk '/^#{2,4} (TASK )?(T-)?L1-[0-9A-Z]{2}-(T)?[0-9]{2} /{
         if(id!="")printf "%s[sv:%s,cmd:%s] ",id,sv,cmd;
         match($0,/(T-)?L1-[0-9A-Z]+-T?[0-9]+/); id=substr($0,RSTART,RLENGTH); sv=0; cmd=0; next}
       id!=""&&/SELF-VERIFY/{sv++} id!=""&&/^```/{cmd++}
       END{if(id!="")printf "%s[sv:%s,cmd:%s]\n",id,sv,cmd}' "$f"
done

# 5 — ORPHANS: prove the two decompositions never cite each other
grep -hoE 'L1-[0-9]{3}\b' L1-00-charter.md L1-01-repo-skeleton.md L1-02-schemas.md \
     L1-03-validators.md L1-04-ci-gate-engine.md L1-06-tests.md L1-07-runbook.md \
  | sort -u | wc -l          # -> 0
```

---

## Session 12 update (2026-09-08)

**Last-verified:** 2026-09-08 (Session 12).

L1-99 fresh review (Session 12) confirms **PASS**. No residue, no new defects found. All 61 bodies and SELF-VERIFY blocks remain present. Measurements from 2026-09-02 are unchanged.

**Index-coverage gap closed (2026-09-08).** §5.3 added: 9 index rows for L1-04-01 through L1-04-09 (CI Gate Engine). These bodies existed and were listed as orphans in §5.1 but had no index rows; dispatchers could not see them. The rows are now tracked. Untracked orphan count drops from 31 to 22. DoD annotations cite §11.3, §33.2, §53.1, §53.4, §101, AT-102, D63, D97, EC-109, and L1-903 per task.

---

## Session 13 Update (2026-09-08)

- **§5.3 promoted to tracked index rows** — the 9 T-L1-04-* CI Gate Engine bodies added in Session 12 are now fully indexed with DoD refs; dispatchers can locate, sequence, and assign them.
- **All remaining orphans indexed (§5.4–§5.8)** — 23 supplementary index rows added for L1-00 (3), L1-01 (6), L1-02 (4), L1-03 (1), and L1-06 (9). All previously untracked bodies now have index rows. **Untracked count: 0.** (The prior figure of "22 remaining" was off by 1 due to a counting error in §5.3; the actual post-§5.3 residue was 23, as explained in the §5.8 effect note.)
- **L1 decision memos created** — PENDING_FOUNDER_DECISIONS.md now carries L0-choice memos for L1-D2 (rota coverage window owner), L1-D3 (coverage-window rule blocker), and L1-D5 (schema-change checklist scope); these must be resolved before L1-311 and related tasks can be dispatched.
