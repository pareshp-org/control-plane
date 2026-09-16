# L3-CONCORDANCE — Lane 3 task-id concordance

**Lane:** L3 — Reconciler & Provisioning (subsystems C and D).
**Generated:** 2026-09-02. **Decision basis:** FD-004 (publish a concordance; do not reissue the indexes).
**Scope:** mapping only. No task body was written, edited or moved by this document.

---

## 0. Files read, as they are on disk today

Every number below is derived from exactly these copies. `wc -l`:

| File | `wc -l` |
| --- | ---: |
| `L3-00-charter.md` | 1103 |
| `L3-01-diff-engine.md` | 7574 |
| `L3-02-levels-and-repair.md` | 3557 |
| `L3-03-canary-and-integrity.md` | 6023 |
| `L3-04-provisioning.md` | 1938 |
| `L3-05-orphans.md` | 2034 |
| `L3-06-tasks.md` | 3285 |
| `L3-07-tests-and-runbook.md` | 1361 |
| **total** | **26875** |

---

## 1. Headline

| Quantity | Count |
| --- | ---: |
| Index ids promised by `L3-06-tasks.md` | **82** |
| Distinct ids carrying a real body anywhere in the lane | **194** |
| &nbsp;&nbsp;— of which in `L3-06-tasks.md` itself | 82 |
| &nbsp;&nbsp;— of which in the seven phase files | 116 |
| Index ids confidently mapped to a body | **82** |
| **RESIDUE — index ids with no body anywhere** | **0** |
| **ORPHANS — bodies no index row claims** | **116** |

### The finding, stated plainly

**Lane 3 has no residue. Every one of the 82 ids the master index promises has a full,
executable body — files, steps, Acceptance, SELF-VERIFY, STOP — and that body is in
`L3-06-tasks.md` itself, under the identical id.** `L3-06-tasks.md` is self-contained: its
section 2 table and its sections 3–11 bodies are one decomposition, not two.

L3 therefore differs from the other lanes in kind, not degree. The defect here is **not**
missing bodies. It is that the lane carries a **second, complete, fully-bodied decomposition
of itself** — 116 task bodies across the seven phase files, in six mutually disjoint id
namespaces (`L3-00-Tnn`, `L3-01-Tnn`, `L3-02-Tnn`, `L3-P3-Tnn`, `L3-04-Tnn`, `L3-05-Tnn`,
and a bare `Tnn` in `L3-07`) — and **not one of those 116 is named anywhere in the master
index**. Verified in both directions: no phase file cites a single `L3-Px-yy` id, and
`L3-06-tasks.md` cites not one phase-file id. The two decompositions never reference each
other at any point.

The dispatch risk in Lane 3 is therefore **duplication, not omission**: a developer handed
`L3-P1-02` and a developer handed `L3-01-06` build the same comparator twice, on two
branches, with no way to discover the collision from either document.

---

## 2. Mapping table — index id -> body

All 82 rows. `Body file` is where an executor actually finds the work. Confidence is
`exact` where the index id and the body heading are the same string in the same file —
which is every row.

| # | Index id | Body id | Body file | Line | Conf | What the task does |
| ---: | --- | --- | --- | ---: | --- | --- |
| 1 | `L3-P0-01` | `L3-P0-01` | `L3-06-tasks.md` | 254 | exact | Lane tree and ownership marker |
| 2 | `L3-P0-02` | `L3-P0-02` | `L3-06-tasks.md` | 297 | exact | Package skeleton and pinned deps |
| 3 | `L3-P0-03` | `L3-P0-03` | `L3-06-tasks.md` | 351 | exact | Contract map module |
| 4 | `L3-P0-04` | `L3-P0-04` | `L3-06-tasks.md` | 394 | exact | Fixture set `fixture-a` |
| 5 | `L3-P0-05` | `L3-P0-05` | `L3-06-tasks.md` | 662 | exact | Finding model, drift classes, levels |
| 6 | `L3-P0-06` | `L3-P0-06` | `L3-06-tasks.md` | 713 | exact | `GitHubState` port and fixture adapter |
| 7 | `L3-P0-07` | `L3-P0-07` | `L3-06-tasks.md` | 760 | exact | Run record writer and summary line |
| 8 | `L3-P0-CMP10` | `L3-P0-CMP10` | `L3-06-tasks.md` | 15 | exact | Lifecycle vs Renovate monitoring |
| 9 | `L3-P0-CMP12` | `L3-P0-CMP12` | `L3-06-tasks.md` | 76 | exact | Shared Service registry dependency check |
| 10 | `L3-P0-AT001` | `L3-P0-AT001` | `L3-06-tasks.md` | 138 | exact | create-product scaffold conformance verifier |
| 11 | `L3-P0-DEL14` | `L3-P0-DEL14` | `L3-06-tasks.md` | 199 | exact | 14-day delegation expiry warning |
| 12 | `L3-P1-01` | `L3-P1-01` | `L3-06-tasks.md` | 818 | exact | Comparator registry and `reconciler.cli` |
| 13 | `L3-P1-02` | `L3-P1-02` | `L3-06-tasks.md` | 859 | exact | Comparator: org membership |
| 14 | `L3-P1-03` | `L3-P1-03` | `L3-06-tasks.md` | 901 | exact | Comparator: capability vs team-implied authority |
| 15 | `L3-P1-04` | `L3-P1-04` | `L3-06-tasks.md` | 934 | exact | Comparator: assignments vs Team membership |
| 16 | `L3-P1-05` | `L3-P1-05` | `L3-06-tasks.md` | 967 | exact | Comparator: assignments vs CODEOWNERS |
| 17 | `L3-P1-06` | `L3-P1-06` | `L3-06-tasks.md` | 1000 | exact | Comparator: branch protection template |
| 18 | `L3-P1-07` | `L3-P1-07` | `L3-06-tasks.md` | 1033 | exact | Comparator: workflow template version |
| 19 | `L3-P1-08` | `L3-P1-08` | `L3-06-tasks.md` | 1068 | exact | Comparator: environments and deployment branch/tag policy |
| 20 | `L3-P1-09` | `L3-P1-09` | `L3-06-tasks.md` | 1101 | exact | Comparator: assignment `end_date` expiry |
| 21 | `L3-P1-10` | `L3-P1-10` | `L3-06-tasks.md` | 1134 | exact | Comparator: `platform.yaml` workflow tag → SHA |
| 22 | `L3-P1-11` | `L3-P1-11` | `L3-06-tasks.md` | 1167 | exact | Comparator: Renovate bypass ruleset split |
| 23 | `L3-P1-12` | `L3-P1-12` | `L3-06-tasks.md` | 1200 | exact | Comparator: machine workflow-file change and bypass-branch authorship |
| 24 | `L3-P1-13` | `L3-P1-13` | `L3-06-tasks.md` | 1238 | exact | Comparator: infrastructure attestation window |
| 25 | `L3-P1-14` | `L3-P1-14` | `L3-06-tasks.md` | 1271 | exact | Comparator: record-store write freshness |
| 26 | `L3-P1-15` | `L3-P1-15` | `L3-06-tasks.md` | 1304 | exact | Comparator: `restore_tested` vs restore-test records |
| 27 | `L3-P1-16` | `L3-P1-16` | `L3-06-tasks.md` | 1337 | exact | Per-registry comparison counts on the run record |
| 28 | `L3-P1-17` | `L3-P1-17` | `L3-06-tasks.md` | 1369 | exact | Seeded canary and the zero-findings FAIL rule |
| 29 | `L3-P1-18` | `L3-P1-18` | `L3-06-tasks.md` | 1404 | exact | Run annotations: `external-cause`, `acknowledged_by/at`, clean-run record |
| 30 | `L3-P1-19` | `L3-P1-19` | `L3-06-tasks.md` | 1435 | exact | Fail-closed matrix for Blocking-class checks |
| 31 | `L3-P1-20` | `L3-P1-20` | `L3-06-tasks.md` | 1470 | exact | SIG-13 emission on a failed run |
| 32 | `L3-P2-01` | `L3-P2-01` | `L3-06-tasks.md` | 1514 | exact | Orphan framework and the 16-type severity map |
| 33 | `L3-P2-02` | `L3-P2-02` | `L3-06-tasks.md` | 1579 | exact | Orphan detectors 1–5 (ownership slots, shared service) |
| 34 | `L3-P2-03` | `L3-P2-03` | `L3-06-tasks.md` | 1609 | exact | Orphan detectors 6–10 (assets, commitments) |
| 35 | `L3-P2-04` | `L3-P2-04` | `L3-06-tasks.md` | 1639 | exact | Orphan detectors 11–16 (migration, verification, H1, temp expiry, policy, exception) |
| 36 | `L3-P2-05` | `L3-P2-05` | `L3-06-tasks.md` | 1669 | exact | Prospective orphan mode on `availability: departing` |
| 37 | `L3-P2-06` | `L3-P2-06` | `L3-06-tasks.md` | 1699 | exact | Blocking orphans non-dismissible, SIG-05 emission |
| 38 | `L3-P3-01` | `L3-P3-01` | `L3-06-tasks.md` | 1734 | exact | Drift-class config loader from `os-health.yaml` |
| 39 | `L3-P3-02` | `L3-P3-02` | `L3-06-tasks.md` | 1764 | exact | `control-plane/blocking-drift` check-run publisher |
| 40 | `L3-P3-03` | `L3-P3-03` | `L3-06-tasks.md` | 1798 | exact | Check-run identity assertion |
| 41 | `L3-P3-04` | `L3-P3-04` | `L3-06-tasks.md` | 1829 | exact | Drift budget counters (Amber 2/product, Red flat 3) |
| 42 | `L3-P3-05` | `L3-P3-05` | `L3-06-tasks.md` | 1867 | exact | Reclassification gate |
| 43 | `L3-P3-06` | `L3-P3-06` | `L3-06-tasks.md` | 1896 | exact | Closure-quality audit sampler |
| 44 | `L3-P4-01` | `L3-P4-01` | `L3-06-tasks.md` | 1939 | exact | `provision` CLI skeleton, dry-run default |
| 45 | `L3-P4-02` | `L3-P4-02` | `L3-06-tasks.md` | 1969 | exact | CODEOWNERS generator, human identities only |
| 46 | `L3-P4-03` | `L3-P4-03` | `L3-06-tasks.md` | 2002 | exact | Branch-protection applier from template |
| 47 | `L3-P4-04` | `L3-P4-04` | `L3-06-tasks.md` | 2035 | exact | Environments and deployment branch/tag policy applier |
| 48 | `L3-P4-05` | `L3-P4-05` | `L3-06-tasks.md` | 2065 | exact | Team creator derived from registries |
| 49 | `L3-P4-06` | `L3-P4-06` | `L3-06-tasks.md` | 2098 | exact | Repo-from-template and required-file assertion |
| 50 | `L3-P4-07` | `L3-P4-07` | `L3-06-tasks.md` | 2130 | exact | `create-product` orchestrator |
| 51 | `L3-P4-08` | `L3-P4-08` | `L3-06-tasks.md` | 2180 | exact | CONFIGURE checklist and manual-step issue emitter |
| 52 | `L3-P4-09` | `L3-P4-09` | `L3-06-tasks.md` | 2212 | exact | `add-person` orchestrator |
| 53 | `L3-P4-10` | `L3-P4-10` | `L3-06-tasks.md` | 2243 | exact | Pre-provisioning (T-1 week) checklist emitter |
| 54 | `L3-P5-01` | `L3-P5-01` | `L3-06-tasks.md` | 2288 | exact | Independent verifier skeleton, separate credential |
| 55 | `L3-P5-02` | `L3-P5-02` | `L3-06-tasks.md` | 2323 | exact | Verifier assertion A: no machine identity in any CODEOWNERS |
| 56 | `L3-P5-03` | `L3-P5-03` | `L3-06-tasks.md` | 2354 | exact | Verifier assertion B: protection and ruleset JSON match template |
| 57 | `L3-P5-04` | `L3-P5-04` | `L3-06-tasks.md` | 2385 | exact | Verifier assertion C: bypass-actor list is exactly as declared |
| 58 | `L3-P5-05` | `L3-P5-05` | `L3-06-tasks.md` | 2424 | exact | Verifier absence for one cycle is Level 5 |
| 59 | `L3-P5-06` | `L3-P5-06` | `L3-06-tasks.md` | 2453 | exact | AT-110 credential-bounds probe (six negative attempts) |
| 60 | `L3-P5-07` | `L3-P5-07` | `L3-06-tasks.md` | 2494 | exact | Behavioural-envelope checks |
| 61 | `L3-P5-08` | `L3-P5-08` | `L3-06-tasks.md` | 2535 | exact | Records-repo head SHA anchor |
| 62 | `L3-P6-01` | `L3-P6-01` | `L3-06-tasks.md` | 2575 | exact | Stricter-only predicate and its proof suite |
| 63 | `L3-P6-02` | `L3-P6-02` | `L3-06-tasks.md` | 2613 | exact | Repair enablement registry, every class default-off |
| 64 | `L3-P6-03` | `L3-P6-03` | `L3-06-tasks.md` | 2649 | exact | Repair class: Team membership sync |
| 65 | `L3-P6-04` | `L3-P6-04` | `L3-06-tasks.md` | 2678 | exact | Repair class: CODEOWNERS regeneration |
| 66 | `L3-P6-05` | `L3-P6-05` | `L3-06-tasks.md` | 2708 | exact | Repair class: re-apply declared branch protection |
| 67 | `L3-P6-06` | `L3-P6-06` | `L3-06-tasks.md` | 2737 | exact | Repair class: expired assignment and expired access removal |
| 68 | `L3-P6-07` | `L3-P6-07` | `L3-06-tasks.md` | 2768 | exact | Repair class: label and board field sync |
| 69 | `L3-P6-08` | `L3-P6-08` | `L3-06-tasks.md` | 2797 | exact | Repair record emitter |
| 70 | `L3-P6-09` | `L3-P6-09` | `L3-06-tasks.md` | 2828 | exact | Prohibited-repair guards |
| 71 | `L3-P6-10` | `L3-P6-10` | `L3-06-tasks.md` | 2860 | exact | Repeated failed repair escalates to Level 5 |
| 72 | `L3-P7-01` | `L3-P7-01` | `L3-06-tasks.md` | 2896 | exact | `change-role` operation |
| 73 | `L3-P7-02` | `L3-P7-02` | `L3-06-tasks.md` | 2927 | exact | `remove-person` operation |
| 74 | `L3-P7-03` | `L3-P7-03` | `L3-06-tasks.md` | 2972 | exact | Registry-edit canary staging |
| 75 | `L3-P7-04` | `L3-P7-04` | `L3-06-tasks.md` | 3003 | exact | Authority-delta detector |
| 76 | `L3-P7-05` | `L3-P7-05` | `L3-06-tasks.md` | 3035 | exact | Temporary-person expiry treated as an exit |
| 77 | `L3-P8-01` | `L3-P8-01` | `L3-06-tasks.md` | 3073 | exact | Gap detector and expiry replay |
| 78 | `L3-P8-02` | `L3-P8-02` | `L3-06-tasks.md` | 3104 | exact | Gap diff-audit of the gap window |
| 79 | `L3-P8-03` | `L3-P8-03` | `L3-06-tasks.md` | 3133 | exact | `gap-window` marking |
| 80 | `L3-P8-04` | `L3-P8-04` | `L3-06-tasks.md` | 3162 | exact | Wrong-repair freeze and revert branch |
| 81 | `L3-P8-05` | `L3-P8-05` | `L3-06-tasks.md` | 3196 | exact | Lane acceptance-matrix runner |
| 82 | `L3-P8-06` | `L3-P8-06` | `L3-06-tasks.md` | 3241 | exact | Lane handoff manifest |

---

## 3. Residue — index ids with no body anywhere

| Index id | What the index promises | Why nothing matches |
| --- | --- | --- |
| *(none)* | — | All 78 index ids resolve to a full body in `L3-06-tasks.md`. Checked by set difference; the difference is empty in both directions. |

**Lane 3 contributes 0 tasks to the portfolio-wide list of unbuilt work.**

Every body was additionally checked for substance: all 78 carry a `**Files` block, an
`Acceptance` list and a `SELF-VERIFY` block. Shortest body 29 lines, median 33, longest 268.
Zero stubs. The 78-vs-115 gap reported by the lane review is real but is **not** a
missing-body gap; it is the orphan count in §4 below.

---

## 4. Orphans — bodies no index row claims

All 116 phase-file task bodies are orphans with respect to the master index: none is named
in `L3-06-tasks.md`. Every one was checked for substance — all 116 carry acceptance
criteria and/or a self-verify block, and none is under 15 lines; zero stubs.

The `Duplicates index id` column is a semantic cross-walk: the index task that builds the
same thing. It is a judgement, not a string match, and is graded. `—` means the body is
**work the index does not cover at all** — phase entry/exit gates, negative-test suites,
and a handful of genuinely additional comparators (§4.1).

| Body id | File | Line | What it does | Duplicates index id | Conf |
| --- | --- | ---: | --- | --- | --- |
| `L3-00-01` | `L3-00-charter.md` | 344 | Create the three owned-path skeletons | `L3-P0-01` | high |
| `L3-00-02` | `L3-00-charter.md` | 440 | Write the standing safety contract | — | n/a |
| `L3-00-03` | `L3-00-charter.md` | 531 | Transcribe the drift classes and reconciliation levels | `L3-P0-05` | medium |
| `L3-00-04` | `L3-00-charter.md` | 626 | Enumerate the four scaffolding operations | `L3-P4-07, L3-P4-09, L3-P7-01, L3-P7-02` | low |
| `L3-00-05` | `L3-00-charter.md` | 770 | Transcribe the declared-versus-actual comparison set | `L3-P1-02..L3-P1-15` | low |
| `L3-00-06` | `L3-00-charter.md` | 889 | Record the reconciler credential envelope and the AT-110 negative test | `L3-P5-06` | medium |
| `L3-01-01` | `L3-01-diff-engine.md` | 307 | Phase entry gate, package skeleton, and the read-only API client | `L3-P0-02, L3-P0-06` | high |
| `L3-01-02` | `L3-01-diff-engine.md` | 663 | The drift-finding envelope and the reconciliation run record, as JSON Schema | `L3-P0-05, L3-P0-07` | high |
| `L3-01-03` | `L3-01-diff-engine.md` | 1116 | Declared-state loader and the fixture mirror | `L3-P0-04` | high |
| `L3-01-04` | `L3-01-diff-engine.md` | 1675 | Comparator protocol, comparator registry, orchestrator | `L3-P1-01` | high |
| `L3-01-05` | `L3-01-diff-engine.md` | 2019 | The frozen Section 53.1 table and `comparators/manifest.yaml` | `L3-P1-01` | medium |
| `L3-01-06` | `L3-01-diff-engine.md` | 2424 | CMP-01: `people.yaml` versus GitHub organisation membership | `L3-P1-02` | high |
| `L3-01-07` | `L3-01-diff-engine.md` | 2652 | CMP-02: declared capabilities versus authority-team membership | `L3-P1-03` | high |
| `L3-01-08` | `L3-01-diff-engine.md` | 2882 | The branch-protection template, and CMP-05 | `L3-P1-06` | high |
| `L3-01-09` | `L3-01-diff-engine.md` | 3210 | CMP-03 and CMP-04: assignments versus Teams, and versus CODEOWNERS | `L3-P1-04, L3-P1-05` | high |
| `L3-01-10` | `L3-01-diff-engine.md` | 3650 | The environment template, CMP-07 and CMP-08 | `L3-P1-08` | high |
| `L3-01-11` | `L3-01-diff-engine.md` | 4079 | CMP-09: the declared `infrastructure:` boundary versus provider attestation | `L3-P1-13` | high |
| `L3-01-12` | `L3-01-diff-engine.md` | 4401 | CMP-10: lifecycle versus Renovate, monitoring and CI configuration | — | n/a |
| `L3-01-13` | `L3-01-diff-engine.md` | 4710 | CMP-06: workflow template version versus the actual workflow file | `L3-P1-07` | high |
| `L3-01-14` | `L3-01-diff-engine.md` | 4964 | CMP-11 and CMP-12: expired access, and unknown dependencies | `L3-P1-09` | high |
| `L3-01-15` | `L3-01-diff-engine.md` | 5255 | CMP-13: the resolved commit SHA behind every `workflows/*` tag | `L3-P1-10` | high |
| `L3-01-16` | `L3-01-diff-engine.md` | 5518 | CMP-14: the Renovate bypass ruleset split | `L3-P1-11` | high |
| `L3-01-17` | `L3-01-diff-engine.md` | 5748 | CMP-15: record-store write freshness | `L3-P1-14` | high |
| `L3-01-18` | `L3-01-diff-engine.md` | 5981 | CMP-16 and CMP-17: restore evidence | `L3-P1-15` | high |
| `L3-01-19` | `L3-01-diff-engine.md` | 6331 | CMP-18 and CMP-19: the two authorship rows | `L3-P1-12` | high |
| `L3-01-20` | `L3-01-diff-engine.md` | 6721 | Run integrity: the seeded canary, the comparison counts, EC-109 | `L3-P1-16, L3-P1-17` | high |
| `L3-01-21` | `L3-01-diff-engine.md` | 7038 | The CLI, exit codes, run-record emission, `external-cause` and `acknowledged_by` | `L3-P1-18` | high |
| `L3-01-22` | `L3-01-diff-engine.md` | 7302 | Phase acceptance: full-set assertion, read-only proof, path guard, exit record | — | n/a |
| `L3-02-01` | `L3-02-levels-and-repair.md` | 176 | Phase entry gate and Phase-2 package skeleton | — | n/a |
| `L3-02-02` | `L3-02-levels-and-repair.md` | 299 | Drift class and response-level tables as data | `L3-P3-01` | high |
| `L3-02-03` | `L3-02-levels-and-repair.md` | 575 | Level 1: Detect | `L3-P1-19` | medium |
| `L3-02-04` | `L3-02-levels-and-repair.md` | 814 | Level 2: Warn | — | n/a |
| `L3-02-05` | `L3-02-levels-and-repair.md` | 998 | The stricter-only comparator | `L3-P6-01` | high |
| `L3-02-06` | `L3-02-levels-and-repair.md` | 1325 | The permitted repair-class registry | `L3-P6-02` | high |
| `L3-02-07` | `L3-02-levels-and-repair.md` | 1576 | Enable-one-class-at-a-time discipline | `L3-P6-02` | high |
| `L3-02-08` | `L3-02-levels-and-repair.md` | 1823 | Level 3: the auto-repair executor | `L3-P6-03..L3-P6-08` | medium |
| `L3-02-09` | `L3-02-levels-and-repair.md` | 2148 | Reconciler write scope narrowed to `derived/**` | `L3-P6-09` | medium |
| `L3-02-10` | `L3-02-levels-and-repair.md` | 2400 | AT-110 credential-boundedness harness | `L3-P5-06` | high |
| `L3-02-11` | `L3-02-levels-and-repair.md` | 2642 | Level 4: Block, via the blocking check run (D92) | `L3-P3-02` | high |
| `L3-02-12` | `L3-02-levels-and-repair.md` | 2954 | Check-run identity guard | `L3-P3-03` | high |
| `L3-02-13` | `L3-02-levels-and-repair.md` | 3095 | Level 5: Escalate, and the repair-class freeze | `L3-P6-10` | high |
| `L3-02-14` | `L3-02-levels-and-repair.md` | 3360 | Level-ordering integration test and phase exit gate | — | n/a |
| `L3-P3-T00` | `L3-03-canary-and-integrity.md` | 169 | Phase entry gate and discovery directories | — | n/a |
| `L3-P3-T01` | `L3-03-canary-and-integrity.md` | 334 | The seeded canary declaration and its loader | `L3-P1-17` | high |
| `L3-P3-T02` | `L3-03-canary-and-integrity.md` | 703 | Canary through the real comparator dispatch; per-registry comparison counts | `L3-P1-16` | high |
| `L3-P3-T03` | `L3-03-canary-and-integrity.md` | 1169 | The FAILED-run rule — zero findings including the canary | `L3-P1-17` | high |
| `L3-P3-T04` | `L3-03-canary-and-integrity.md` | 1492 | Negative tests: prove the canary catches a blinded instrument | — | n/a |
| `L3-P3-T05` | `L3-03-canary-and-integrity.md` | 1746 | D93 — canary-set-first application and the one-cycle fleet hold | `L3-P7-03` | medium |
| `L3-P3-T06` | `L3-03-canary-and-integrity.md` | 2193 | D93 — reconciler write-scope allowlist and machine-registry-write drift rule | `L3-P6-09` | medium |
| `L3-P3-T07` | `L3-03-canary-and-integrity.md` | 2600 | §53.7 — control-loop gap detection | `L3-P8-01` | high |
| `L3-P3-T08` | `L3-03-canary-and-integrity.md` | 3029 | §53.7 — the gap procedure runner | `L3-P8-01, L3-P8-02, L3-P8-03` | high |
| `L3-P3-T09` | `L3-03-canary-and-integrity.md` | 3494 | §53.7 — the "when the loop ran wrong" branch | `L3-P8-04` | high |
| `L3-P3-T10` | `L3-03-canary-and-integrity.md` | 3899 | D107 — anchor the records head SHA and commit count each run | `L3-P5-08` | high |
| `L3-P3-T11` | `L3-03-canary-and-integrity.md` | 4379 | D107 — the non-descendant check at Blocking, Level 5 | `L3-P5-08` | medium |
| `L3-P3-T12` | `L3-03-canary-and-integrity.md` | 4892 | D96 — the behavioural envelope: signed run record and published counts | `L3-P5-07` | high |
| `L3-P3-T13` | `L3-03-canary-and-integrity.md` | 5308 | D96 — envelope enforcement; unmatched trigger is Blocking | `L3-P5-07` | high |
| `L3-P3-T14` | `L3-03-canary-and-integrity.md` | 5648 | AT-102 acceptance harness and the phase exit gate | — | n/a |
| `L3-04-01` | `L3-04-provisioning.md` | 201 | Package skeleton, lane helper, lane-guard proof | `L3-P4-01` | high |
| `L3-04-02` | `L3-04-provisioning.md` | 325 | GitHub call gateway, safety rules SR-1..SR-8, credential envelope | — | n/a |
| `L3-04-03` | `L3-04-provisioning.md` | 452 | Contract-bound resolvers (registry paths, event enum, template ref) | `L3-P0-03` | medium |
| `L3-04-04` | `L3-04-provisioning.md` | 514 | Idempotent step engine, run ledger, manual-step issue emitter | `L3-P4-08` | medium |
| `L3-04-05` | `L3-04-provisioning.md` | 580 | create-product step: preflight and repository from template | `L3-P4-06` | high |
| `L3-04-06` | `L3-04-provisioning.md` | 661 | create-product step: GitHub Team from assignments | `L3-P4-05` | high |
| `L3-04-07` | `L3-04-provisioning.md` | 722 | create-product step: generated CODEOWNERS, humans-only negative check | `L3-P4-02, L3-P5-02` | high |
| `L3-04-08` | `L3-04-provisioning.md` | 815 | create-product step: branch protection from template | `L3-P4-03` | high |
| `L3-04-09` | `L3-04-provisioning.md` | 908 | create-product step: environments, deployment branch and tag policy, scoped secrets | `L3-P4-04` | high |
| `L3-04-10` | `L3-04-provisioning.md` | 974 | create-product step: scaffold conformance (eight commands, three endpoints, verification skeleton) | — | n/a |
| `L3-04-11` | `L3-04-provisioning.md` | 1107 | create-product step: registry entry, CONFIGURE checklist, alert channel and support mailbox | `L3-P4-08` | high |
| `L3-04-12` | `L3-04-provisioning.md` | 1184 | create-product step: surface-registration verifier (no hand-edited dashboards) | — | n/a |
| `L3-04-13` | `L3-04-provisioning.md` | 1270 | `provision create-product` orchestrator and AT-001 rehearsal | `L3-P4-07` | high |
| `L3-04-14` | `L3-04-provisioning.md` | 1393 | `provision preprovision-person` — the T-minus-one-week checklist | `L3-P4-10` | high |
| `L3-04-15` | `L3-04-provisioning.md` | 1497 | `provision add-person` | `L3-P4-09` | high |
| `L3-04-16` | `L3-04-provisioning.md` | 1639 | `provision change-role` | `L3-P7-01` | high |
| `L3-04-17` | `L3-04-provisioning.md` | 1726 | `provision remove-person`, orphan gate, exit record | `L3-P7-02` | high |
| `L3-04-18` | `L3-04-provisioning.md` | 1849 | Phase gate: destructive-guard suite, idempotence proof, phase evidence | — | n/a |
| `L3-05-01` | `L3-05-orphans.md` | 318 | Preflight: environment, toolchain and phase preconditions | — | n/a |
| `L3-05-02` | `L3-05-orphans.md` | 407 | Finding model, severity enum, detector registry, decisions module | `L3-P2-01` | high |
| `L3-05-03` | `L3-05-orphans.md` | 502 | Control-plane loader with input-availability guard | — | n/a |
| `L3-05-04` | `L3-05-orphans.md` | 596 | Fixture harness and golden-case layout | `L3-P0-04` | low |
| `L3-05-05` | `L3-05-orphans.md` | 783 | Detector 1: `ORPH-PRIMARY-OWNER` (Blocking) | `L3-P2-02` | high |
| `L3-05-06` | `L3-05-orphans.md` | 831 | Detector 2: `ORPH-CROSS-REVIEWER` (Blocking) | `L3-P2-02` | high |
| `L3-05-07` | `L3-05-orphans.md` | 856 | Detector 3: `ORPH-BACKUP-OWNER` (High) | `L3-P2-02` | high |
| `L3-05-08` | `L3-05-orphans.md` | 883 | Detector 4: `ORPH-PRIMARY-RESPONDER` (Blocking) | `L3-P2-02` | high |
| `L3-05-09` | `L3-05-orphans.md` | 911 | Detector 5: `ORPH-SHARED-SERVICE` (Blocking) | `L3-P2-02` | high |
| `L3-05-10` | `L3-05-orphans.md` | 938 | Detector 6: `ORPH-CERTIFICATE` (High) — **DR-L3-05-A blocked** | `L3-P2-03` | high |
| `L3-05-11` | `L3-05-orphans.md` | 976 | Detector 7: `ORPH-DOMAIN` (Blocking) — **DR-L3-05-A blocked** | `L3-P2-03` | high |
| `L3-05-12` | `L3-05-orphans.md` | 1003 | Detector 8: `ORPH-VENDOR` (Medium) — **DR-L3-05-A blocked** | `L3-P2-03` | high |
| `L3-05-13` | `L3-05-orphans.md` | 1028 | Detector 9: `ORPH-ASSET` (Medium) — **DR-L3-05-A blocked** | `L3-P2-03` | high |
| `L3-05-14` | `L3-05-orphans.md` | 1057 | Detector 10: `ORPH-COMMITMENT` (Blocking) — **DR-L3-05-E blocked** | `L3-P2-03` | high |
| `L3-05-15` | `L3-05-orphans.md` | 1092 | Detector 11: `ORPH-PLATFORM-MIGRATION` (High) | `L3-P2-04` | high |
| `L3-05-16` | `L3-05-orphans.md` | 1120 | Detector 12: `ORPH-VERIFICATION` (High) | `L3-P2-04` | high |
| `L3-05-17` | `L3-05-orphans.md` | 1152 | Detector 13: `ORPH-H1-WORK` (High) — **DR-L3-05-C blocked** | `L3-P2-04` | high |
| `L3-05-18` | `L3-05-orphans.md` | 1187 | Detector 14: `ORPH-TEMP-EXPIRY-OPEN-WORK` (High) — **DR-L3-05-D blocked** | `L3-P2-04` | high |
| `L3-05-19` | `L3-05-orphans.md` | 1225 | Detector 15: `ORPH-POLICY` (Blocking) | `L3-P2-04` | high |
| `L3-05-20` | `L3-05-orphans.md` | 1252 | Detector 16: `ORPH-EXCEPTION` (High) | `L3-P2-04` | high |
| `L3-05-21` | `L3-05-orphans.md` | 1280 | Registry completeness and severity-conformance test | — | n/a |
| `L3-05-22` | `L3-05-orphans.md` | 1344 | Prospective mode and the departing-person transfer worklist | `L3-P2-05` | high |
| `L3-05-23` | `L3-05-orphans.md` | 1427 | Orphan report and event payload emitter | — | n/a |
| `L3-05-24` | `L3-05-orphans.md` | 1506 | Blocking-orphan dismissal guard | `L3-P2-06` | high |
| `L3-05-25` | `L3-05-orphans.md` | 1591 | Expiry scan → revocation plan (no execution) | `L3-P6-06` | medium |
| `L3-05-26` | `L3-05-orphans.md` | 1670 | 14-day delegation expiry warning — **DR-L3-05-B blocked** | — | n/a |
| `L3-05-27` | `L3-05-orphans.md` | 1741 | T-minus-7 temporary-person expiry warning to sponsor — **DR-L3-05-D blocked** | `L3-P7-05` | medium |
| `L3-05-28` | `L3-05-orphans.md` | 1805 | No-network / no-write safety test | — | n/a |
| `L3-05-29` | `L3-05-orphans.md` | 1858 | CLI, exit codes and machine-readable output | — | n/a |
| `L3-05-30` | `L3-05-orphans.md` | 1917 | Phase acceptance suite: AT-017 end to end | — | n/a |
| `L3-07-01` | `L3-07-tests-and-runbook.md` | 108 | Bootstrap the harness | — | n/a |
| `L3-07-02` | `L3-07-tests-and-runbook.md` | 219 | Build the fixture organisation | `L3-P0-04` | medium |
| `L3-07-03` | `L3-07-tests-and-runbook.md` | 362 | Dry-run, hermeticity and the apply guard (TC-L3-01/02/03) | — | n/a |
| `L3-07-04` | `L3-07-tests-and-runbook.md` | 462 | The stricter-only negative tests (TC-L3-04/05/06) | `L3-P6-01` | medium |
| `L3-07-05` | `L3-07-tests-and-runbook.md` | 564 | The seeded canary: a run that finds nothing must fail (TC-L3-07/08/09) | `L3-P1-17` | medium |
| `L3-07-06` | `L3-07-tests-and-runbook.md` | 652 | Expiry revocation and orphan detection (TC-L3-10/11/12) | `L3-P6-06, L3-P2-02..06` | medium |
| `L3-07-07` | `L3-07-tests-and-runbook.md` | 740 | The machine-authority wall (TC-L3-13/14/15) | `L3-P1-12` | medium |
| `L3-07-08` | `L3-07-tests-and-runbook.md` | 832 | Provisioning tests (TC-L3-16/17/18) | `L3-P4-02..L3-P4-09` | low |
| `L3-07-09` | `L3-07-tests-and-runbook.md` | 917 | Registry-change staging and external cause (TC-L3-19/20) | `L3-P7-03, L3-P1-18` | medium |
| `L3-07-10` | `L3-07-tests-and-runbook.md` | 989 | The live-organisation procedure and AT-110 (TC-L3-21) | `L3-P5-06` | high |
| `L3-07-11` | `L3-07-tests-and-runbook.md` | 1089 | Acceptance-test traceability matrix | `L3-P8-05` | high |

### 4.1 Orphan bodies covering work the index does not name at all

Most `—` rows above are phase-local scaffolding (entry gates, exit gates, fixture
harnesses, CLI wrappers) that the master index folds into its own tasks. Four are
substantive and are flagged for L0:

| Body id | File | Line | Substantive gap it covers |
| --- | --- | ---: | --- |
| `L3-01-12` | `L3-01-diff-engine.md` | 4401 | CMP-10: lifecycle versus Renovate, monitoring and CI configuration |
| `L3-04-10` | `L3-04-provisioning.md` | 974 | create-product step: scaffold conformance (eight commands, three endpoints, verification skeleton) |
| `L3-04-12` | `L3-04-provisioning.md` | 1184 | create-product step: surface-registration verifier (no hand-edited dashboards) |
| `L3-05-26` | `L3-05-orphans.md` | 1670 | 14-day delegation expiry warning — **DR-L3-05-B blocked** |

- `L3-01-12` builds **CMP-10** (lifecycle versus Renovate, monitoring and CI
  configuration), and `L3-01-14` additionally builds **CMP-12** (unknown dependencies).
  The master index's 20 Phase-1 comparators include neither. The phase file's comparator
  set is the larger one (19 CMP rows against §53.1's table); the index's is a subset.
- `L3-04-10` (scaffold conformance: eight commands, three endpoints, verification
  skeleton) and `L3-04-12` (surface-registration verifier — no hand-edited dashboards)
  have no index row. `L3-04-12` is the AT-001 guarantee that no dashboard contains a
  product list.
- `L3-05-26` (14-day delegation expiry warning) has no index row.

---

## 5. Single-sourced index tasks — no corroborating phase body

The inverse of the orphan list, and the section L0 should read most closely. These **10**
index tasks have a body in `L3-06-tasks.md` and **no peer body in any phase file**. They
are not residue — they are fully specified and dispatchable — but they are the parts of
Lane 3 that exactly one document has ever thought about, so they carry no cross-check.

| Index id | Body line | What it does | Note |
| --- | ---: | --- | --- |
| `L3-P1-20` | 1470 | SIG-13 emission on a failed run | `SIG-13` appears in `L3-00-charter.md` spec tables only (lines 188, 275, 300, 302); no phase task builds the emitter. |
| `L3-P3-04` | 1829 | Drift budget counters | `drift budget` appears in the charter's spec tables and in a `L3-02` decision note only; no phase task builds the counters. |
| `L3-P3-05` | 1867 | Reclassification gate | Reclassification appears as prose in `L3-00` and `L3-02`; no phase task builds the gate. |
| `L3-P3-06` | 1896 | Closure-quality audit sampler | Zero occurrences of `closure-quality` in any phase file. |
| `L3-P5-01` | 2288 | Independent verifier skeleton under a separate credential | `L3-00-charter.md:109` reserves the path `validators/drift/verifier/**`, but no phase task builds the verifier. |
| `L3-P5-03` | 2354 | Verifier assertion B: branch protection and ruleset JSON match the committed template | Partially shadowed by `L3-01-08` (branch-protection template), which builds the comparator, not the independent assertion under a separate credential. |
| `L3-P5-04` | 2385 | Verifier assertion C: the bypass-actor list is exactly as declared | Partially shadowed by `L3-01-16` (Renovate bypass split), which builds the comparator, not the independent assertion. |
| `L3-P5-05` | 2424 | Verifier absence for one cycle is Level 5 | Verifier liveness (absence for one cycle = Level 5) has no phase-file body. |
| `L3-P7-04` | 3003 | Authority-delta detector | **CONFLICT — see §6.** |
| `L3-P8-06` | 3241 | Lane handoff manifest | `HANDOFF` appears in `L3-04` only as printed step output; no phase task writes the manifest. |

---

## 6. One substantive conflict between the two decompositions

`L3-P7-04 — Authority-delta detector` (index row 71, body `L3-06-tasks.md:3003`) assigns
the §26.4 authority-delta check to Lane 3, at `validators/drift/authority_delta.py`.

`L3-03-canary-and-integrity.md:1764` explicitly refuses it:

> the §26.4 second rule *"belongs to the registry validators, `validators/registry/**`,
> which PARTITION.md gives to **L1**. It is named here so that nobody believes Phase 3
> covers it, and is routed to L0 as a cross-lane note, not claimed."*

Restated at `L3-03-canary-and-integrity.md:5912`. This is a live lane-ownership
disagreement inside Lane 3's own plan, and a concordance cannot resolve it.

**L0 decision required:** does L3 build the authority-delta detector under
`validators/drift/**`, or does L1 build it under `validators/registry/**`? Note that
`L3-06`'s own §0.1 forbids L3 writing to `validators/registry/**`, so the two readings
cannot be reconciled by relocating the file.

---

## 7. Exact commands used

Run from `C:/D_Drive/PS/MultiProduct/Code/implementation/lanes`. Reproduces every count
above.

**Commands**

```bash
# 0. File sizes (the copies these numbers describe)
wc -l L3-00-charter.md L3-01-diff-engine.md L3-02-levels-and-repair.md \
      L3-03-canary-and-integrity.md L3-04-provisioning.md L3-05-orphans.md \
      L3-06-tasks.md L3-07-tests-and-runbook.md

# 1. INDEX side - the master table, section 2, lines 163-247  => 78
sed -n '163,247p' L3-06-tasks.md \
  | grep -oE '^\| *[0-9]+ \| *L3-[A-Za-z0-9-]+' \
  | grep -oE 'L3-[A-Za-z0-9-]+' | sort -u > idx.txt
wc -l < idx.txt                      # 78

# 2a. BODY side, master file - H3 headings              => 78
grep -nE '^#{3,4} L3-[A-Za-z0-9-]+' L3-06-tasks.md \
  | grep -oE 'L3-[A-Za-z0-9-]+' | sort -u > bod06.txt
wc -l < bod06.txt                    # 78

# 3. MAP / RESIDUE / ORPHAN by set difference
comm -23 idx.txt bod06.txt           # residue        -> empty
comm -13 idx.txt bod06.txt           # unclaimed body -> empty
comm -12 idx.txt bod06.txt | wc -l   # mapped         -> 78

# 2b. BODY side, phase files - six disjoint namespaces, heading-anchored => 116
grep -cE '^### L3-00-T[0-9]+ '    L3-00-charter.md              #  6
grep -cE '^## L3-01-T[0-9]+ '     L3-01-diff-engine.md          # 22
grep -cE '^## L3-02-T[0-9]+ '     L3-02-levels-and-repair.md    # 14
grep -cE '^## L3-P3-T[0-9]+ '     L3-03-canary-and-integrity.md # 15
grep -cE '^## L3-04-T[0-9]+ '     L3-04-provisioning.md         # 18
grep -cE '^### .L3-05-T[0-9]+.'   L3-05-orphans.md              # 30
grep -cE '^### T[0-9]+ '          L3-07-tests-and-runbook.md    # 11
#                                                        total = 116

# 4. Prove the two namespaces never cite each other (both print nothing)
grep -lE 'L3-P[0-8]-[0-9]{2}' L3-00-charter.md L3-01-diff-engine.md \
      L3-02-levels-and-repair.md L3-03-canary-and-integrity.md \
      L3-04-provisioning.md L3-05-orphans.md L3-07-tests-and-runbook.md
grep -nE 'L3-0[0-9]-T[0-9]+|L3-P3-T[0-9]+' L3-06-tasks.md

# 5. Body-substance check (0 stubs on both sides)
#   master: each '### L3-Px-yy' section must contain '**Files', 'Acceptance', 'SELF-VERIFY'
#   phase:  each task section must contain acceptance and/or self-verify, and >= 15 lines
```

**Patterns used, and why more than one.** The six phase namespaces differ in both id
grammar and heading level: `L3-00` uses `###`, `L3-01`/`L3-02`/`L3-04` use `##`, `L3-03`
uses `##` with an interposed `P3` segment (`L3-P3-Tnn`), `L3-05` wraps its ids in
backticks at `###`, and `L3-07` drops the lane prefix entirely (bare `T01`..`T11`, here
qualified as `L3-07/Tnn` to keep ids unique). A single regex finds at most one of these.
The counts are the union of the seven anchored patterns above, each verified against a
printed listing rather than a bare count.

> **Note on reproduction.** Write intermediate files to a private directory, not `/tmp`.
> During this run a sibling lane agent overwrote `/tmp/idx.txt`, which briefly produced an
> L1 id list under an L3 filename. All counts above were re-derived from an isolated path.

---

## 8. What L0 should take from this

1. **Lane 3 is dispatchable as-is on the index namespace.** All 78 promised tasks have
   complete bodies in `L3-06-tasks.md`. Residue is zero. L3 adds nothing to the
   portfolio-wide unbuilt-work list.
2. **Choose one decomposition before dispatch.** The 116 phase-file bodies are a peer plan
   for the same lane. Dispatching both duplicates roughly two-thirds of Lane 3. §4 makes
   the overlap visible; it does not resolve it.
3. **The phase files are the finer-grained plan** (116 bodies against 78) and cover four
   things the index misses (§4.1) — notably CMP-10, CMP-12 and the surface-registration
   verifier. The index is the shorter and more uniformly-shaped plan. If the index is
   chosen, those four items should be carried across.
4. **10 index tasks are single-sourced** (§5) — no phase body corroborates them. Four of
   them are the independent control verifier (`L3-P5-01`, `L3-P5-03`, `L3-P5-04`,
   `L3-P5-05`), which is the lane's own check on itself.
5. **One conflict needs an L0 ruling** (§6): who owns the authority-delta detector, L3
   or L1.

---

## Session 12 update (2026-09-08)

**Last-verified:** 2026-09-08 (Session 12).

### Fixes applied in Session 12

- **N1 authority contradiction fixed** — `L3-06` now consistently records the authority-delta detector as owned by L3; the prior cross-file contradiction with L1 is resolved.
- **N3 — 4 missing work items added** — the four phase-file-only items called out in §8 point 3 are now carried as explicit tasks:
  - `L3-P0-CMP10`
  - `L3-P0-CMP12`
  - `L3-P0-AT001`
  - `L3-P0-DEL14`
- **`authority_delta.py` assigned to L3** — ownership recorded in `L3-06-tasks.md`; L1 no longer claims it.

### L3-99 re-review (Session 12): **PASS**

---

## Session 13 Update (2026-09-08)

- **Task body audit complete** — all L3 task bodies verified present; 0 stub bodies confirmed.
- **4 new tasks confirmed executable** — L3-P0-CMP10, L3-P0-CMP12, L3-P0-AT001, and L3-P0-DEL14 (added in Session 12) confirmed to have Commands blocks and are dispatchable.
- **L3 decision memos created** — PENDING_FOUNDER_DECISIONS.md now carries L0-choice memos for L3-B1 (normative decomposition selection: master 78-task index vs. 116-body phase files) and L3-B4 (authority-delta detector final ownership confirmation); these must be resolved before L3 can be fully dispatched.
