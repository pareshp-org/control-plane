# L2-CONCORDANCE — Lane 2 task-id concordance

**Lane:** L2 — Pipeline & Evidence (subsystems E and F).

**Purpose:** close `L2-99-review.md` defects **B1/B2** by publishing, in one place, which task id in the master tasks file corresponds to which task body, and where that body lives. Per **FD-004** this file is *additive*: it edits no task file, reissues no index, and invalidates no citation.

> **This file writes no task bodies.** It maps ids to bodies that already exist.

---

## 0. Files measured, as they are on disk

Measured 2026-09-02. Every number below is derived from exactly these copies.

| File | `wc -l` | Role in this concordance |
| --- | ---: | --- |
| `L2-00-charter.md` | 952 | body side — §11 holds `L2-T001`–`L2-T006` |
| `L2-01-reusable-workflows.md` | 2477 | body side — §3 holds `L2-P1-T00`–`L2-P1-T15` (a disjoint namespace; **the master index names none of them**) |
| `L2-02-digest-invariant.md` | 2277 | body side — §3 holds `L2-T520`–`L2-T528`, `L2-T200`–`L2-T202`, `L2-T400`–`L2-T405` |
| `L2-03-production-gates.md` | 3195 | body side — §7 holds `L2-T170`–`L2-T177`, `L2-T370`–`L2-T371`, `L2-T570`–`L2-T572` |
| `L2-04-evidence-chain.md` | 3410 | body side — §6 holds `L2-T500`–`L2-T516` |
| `L2-05-tasks.md` | 3800 | **index side** (§2 table, 76 rows; §2.1 pointer table, 32 rows) **and** body side (§§3–5, 70 bodies) |
| `L2-06-tests.md` | 2177 | body side — §10 holds `L2-T600`–`L2-T611`, `L2-T220`, `L2-T221` |
| `L2-07-runbook.md` | 1690 | neither — 15 `L2-RB-nn` procedures, not task ids; excluded from both counts |
| **total** | **19978** | |

---

## 1. Headline numbers

| Quantity | Count |
| --- | ---: |
| Distinct task ids the master file (`L2-05-tasks.md`) states | **113** |
| — of which in the §2 execution table (“all 76 tasks”) | 76 |
| — of which added by the §2.1 pointer table | 26 |
| — of which added by the §2.1 / §10 n.2 *range* statements | 11 |
| Distinct task ids carrying a real body anywhere in the lane | **154** |
| Index ids confidently mapped to a body | **113** |
| **RESIDUE — index ids with no body anywhere** | **0** |
| **ORPHANS — bodies no master-index row claims** | **41** |

**The finding, in one sentence.** Lane 2's residue is **zero**: every task id the master file names already has an executable body somewhere in the lane, because `L2-05-tasks.md` §2.1 had already reconciled the two decompositions by hand. Lane 2's defect is the *other* direction — **41 task bodies exist that the dispatch list does not name**, sixteen of them a complete second decomposition of the reusable-workflow library in `L2-01`.

Because §2.1 already renumbered every colliding id, **id equality is a sound match key in this lane** — unlike L1/L3/L4/L5, no cross-namespace semantic matching was needed for the mapped set. Every row below is `high` confidence for that reason, and each was confirmed by opening the body heading at the cited line.

---

## 2. Mapping table — index id → body

### 2.1 The §2 execution table, rows 1–76

| # | Index id | Body id | Body file | Line | Conf. | What the task does |
| ---: | --- | --- | --- | ---: | --- | --- |
| 1 | `L2-T001` | `L2-T001` | `L2-00-charter.md` | 355 | high | Create the lane branch and the owned-path skeleton |
| 2 | `L2-T002` | `L2-T002` | `L2-00-charter.md` | 422 | high | Pin the consumed contract surface |
| 3 | `L2-T003` | `L2-T003` | `L2-00-charter.md` | 505 | high | Publish the required-status-check name registry |
| 4 | `L2-T004` | `L2-T004` | `L2-00-charter.md` | 609 | high | Author the lane-guard workflow |
| 5 | `L2-T005` | `L2-T005` | `L2-00-charter.md` | 728 | high | Author the merge-train preflight check |
| 6 | `L2-T006` | `L2-T006` | `L2-00-charter.md` | 822 | high | Rebase and open the lane PR |
| 7 | `L2-T530` | `L2-T530` | `L2-05-tasks.md` | 427 | high | Evidence toolchain skeleton |
| 8 | `L2-T531` | `L2-T531` | `L2-05-tasks.md` | 475 | high | Action-pin resolver and applier |
| 9 | `L2-T532` | `L2-T532` | `L2-05-tasks.md` | 513 | high | Action pin ledger |
| 10 | `L2-T533` | `L2-T533` | `L2-05-tasks.md` | 562 | high | Workflow lint: pinning, permissions, no-if: |
| 11 | `L2-T534` | `L2-T534` | `L2-05-tasks.md` | 615 | high | Required-context ↔ job cross-check |
| 12 | `L2-T535` | `L2-T535` | `L2-05-tasks.md` | 665 | high | Run-conclusion assertor: no skipped, no neutral |
| 13 | `L2-T536` | `L2-T536` | `L2-05-tasks.md` | 712 | high | Delta-gate engine |
| 14 | `L2-T100` | `L2-T100` | `L2-05-tasks.md` | 762 | high | ci.yml reusable scaffold |
| 15 | `L2-T101` | `L2-T101` | `L2-05-tasks.md` | 801 | high | ci.yml: unit-tests, integration-tests |
| 16 | `L2-T102` | `L2-T102` | `L2-05-tasks.md` | 840 | high | ci.yml: interim build job |
| 17 | `L2-T103` | `L2-T103` | `L2-05-tasks.md` | 879 | high | ci.yml: security-scan, delta-gated |
| 18 | `L2-T104` | `L2-T104` | `L2-05-tasks.md` | 920 | high | ci.yml: licence-scan, delta-gated |
| 19 | `L2-T105` | `L2-T105` | `L2-05-tasks.md` | 959 | high | ci.yml: slopsquat-check at execute time |
| 20 | `L2-T106` | `L2-T106` | `L2-05-tasks.md` | 998 | high | ci.yml: contract-validation and §33.1 required-file presence |
| 21 | `L2-T107` | `L2-T107` | `L2-05-tasks.md` | 1050 | high | ci.yml: registry-validation |
| 22 | `L2-T108` | `L2-T108` | `L2-05-tasks.md` | 1089 | high | ci.yml: parity-check |
| 23 | `L2-T109` | `L2-T109` | `L2-05-tasks.md` | 1128 | high | Extend lane-guard.yml with lint and context cross-check |
| 24 | `L2-T110` | `L2-T110` | `L2-05-tasks.md` | 1167 | high | renovate-path-guard.yml |
| 25 | `L2-T111` | `L2-T111` | `L2-05-tasks.md` | 1213 | high | control-plane-ci.yml — §15.5 control-plane validation |
| 26 | `L2-T537` | `L2-T537` | `L2-05-tasks.md` | 1250 | high | Negative-test harness for the two guards |
| 27 | `L2-T112` | `L2-T112` | `L2-05-tasks.md` | 1299 | high | publish-workflow-tag.yml — immutable workflows/vN release |
| 28 | `L2-T300` | `L2-T300` | `L2-05-tasks.md` | 1340 | high | Template tree and placeholder contract |
| 29 | `L2-T539` | `L2-T539` | `L2-05-tasks.md` | 1387 | high | Template renderer and placeholder lint |
| 30 | `L2-T301` | `L2-T301` | `L2-05-tasks.md` | 1439 | high | templates/workflows/ci.yml |
| 31 | `L2-T538` | `L2-T538` | `L2-05-tasks.md` | 1492 | high | SBOM-beside-digest assertion |
| 32 | `L2-T120` | `L2-T120` | `L2-05-tasks.md` | 1537 | high | build.yml — immutable artifact, digest, SBOM |
| 33 | `L2-T121` | `L2-T121` | `L2-05-tasks.md` | 1579 | high | ci.yml: delegate build to build.yml |
| 34 | `L2-T302` | `L2-T302` | `L2-05-tasks.md` | 1618 | high | templates/workflows/build.yml |
| 35 | `L2-T540` | `L2-T540` | `L2-05-tasks.md` | 1658 | high | Time gate: Friday freeze and core hours |
| 36 | `L2-T541` | `L2-T541` | `L2-05-tasks.md` | 1705 | high | Actor gate: human identity plus capability |
| 37 | `L2-T542` | `L2-T542` | `L2-05-tasks.md` | 1757 | high | Workflow-identity gate: approver ≠ deployer |
| 38 | `L2-T543` | `L2-T543` | `L2-05-tasks.md` | 1804 | high | Digest invariant: requested versus staging-verified |
| 39 | `L2-T544` | `L2-T544` | `L2-05-tasks.md` | 1862 | high | Records-write client |
| 40 | `L2-T545` | `L2-T545` | `L2-05-tasks.md` | 1910 | high | Event writer: one file per event, bound envelope |
| 41 | `L2-T130` | `L2-T130` | `L2-05-tasks.md` | 1959 | high | deploy-staging.yml |
| 42 | `L2-T131` | `L2-T131` | `L2-05-tasks.md` | 2008 | high | deploy-production.yml |
| 43 | `L2-T132` | `L2-T132` | `L2-05-tasks.md` | 2063 | high | migrate.yml — cases A–G |
| 44 | `L2-T133` | `L2-T133` | `L2-05-tasks.md` | 2118 | high | The rollback workflow |
| 45 | `L2-T134` | `L2-T134` | `L2-05-tasks.md` | 2169 | high | restore-test.yml — one workflow, two targets |
| 46 | `L2-T136` | `L2-T136` | `L2-05-tasks.md` | 2216 | high | org-export.yml |
| 47 | `L2-T137` | `L2-T137` | `L2-05-tasks.md` | 2263 | high | background-queue.yml |
| 48 | `L2-T546` | `L2-T546` | `L2-05-tasks.md` | 2304 | high | Verification-contract check |
| 49 | `L2-T517` | `L2-T517` | `L2-05-tasks.md` | 2349 | high | Seeded-defect execution and SIG-18 |
| 50 | `L2-T138` | `L2-T138` | `L2-05-tasks.md` | 2395 | high | ci.yml: verification-contract, seeded-defect-case |
| 51 | `L2-T518` | `L2-T518` | `L2-05-tasks.md` | 2437 | high | Conformance-profile evidence substitution |
| 52 | `L2-T519` | `L2-T519` | `L2-05-tasks.md` | 2491 | high | Evidence chain — the eleven questions |
| 53 | `L2-T550` | `L2-T550` | `L2-05-tasks.md` | 2555 | high | verify-digest-chain sweep |
| 54 | `L2-T139` | `L2-T139` | `L2-05-tasks.md` | 2602 | high | verify-digest-chain.yml — sweep and recovery gate |
| 55 | `L2-T551` | `L2-T551` | `L2-05-tasks.md` | 2641 | high | /version digest-match monitor |
| 56 | `L2-T140` | `L2-T140` | `L2-05-tasks.md` | 2693 | high | version-monitor.yml |
| 57 | `L2-T552` | `L2-T552` | `L2-05-tasks.md` | 2730 | high | Restore-rotation scheduler computation |
| 58 | `L2-T141` | `L2-T141` | `L2-05-tasks.md` | 2774 | high | restore-rotation.yml |
| 59 | `L2-T142` | `L2-T142` | `L2-05-tasks.md` | 2813 | high | record-verification-result.yml dispatch |
| 60 | `L2-T553` | `L2-T553` | `L2-05-tasks.md` | 2853 | high | The eight "shipped" conditions |
| 61 | `L2-T143` | `L2-T143` | `L2-05-tasks.md` | 2909 | high | canary-exercise.yml |
| 62 | `L2-T554` | `L2-T554` | `L2-05-tasks.md` | 2957 | high | Actor-gate-is-step-0 assertion |
| 63 | `L2-T303` | `L2-T303` | `L2-05-tasks.md` | 3000 | high | templates/workflows/deploy-staging.yml |
| 64 | `L2-T304` | `L2-T304` | `L2-05-tasks.md` | 3039 | high | templates/workflows/deploy-production.yml |
| 65 | `L2-T305` | `L2-T305` | `L2-05-tasks.md` | 3079 | high | templates/workflows/migrate.yml |
| 66 | `L2-T306` | `L2-T306` | `L2-05-tasks.md` | 3118 | high | templates/workflows/restore-test.yml |
| 67 | `L2-T307` | `L2-T307` | `L2-05-tasks.md` | 3157 | high | templates/workflows/restore-production.yml |
| 68 | `L2-T308` | `L2-T308` | `L2-05-tasks.md` | 3201 | high | templates/workflows/background-queue.yml |
| 69 | `L2-T309` | `L2-T309` | `L2-05-tasks.md` | 3240 | high | The rollback workflow template |
| 70 | `L2-T311` | `L2-T311` | `L2-05-tasks.md` | 3279 | high | templates/workflows/MANIFEST.yaml |
| 71 | `L2-T144` | `L2-T144` | `L2-05-tasks.md` | 3334 | high | control-plane-ci.yml: recovery: ⇒ restore-production.yml and template drift |
| 72 | `L2-T700` | `L2-T700` | `L2-05-tasks.md` | 3373 | high | Execute AT-024 — a shared CI workflow breaks |
| 73 | `L2-T701` | `L2-T701` | `L2-05-tasks.md` | 3417 | high | Execute AT-029 — the control plane is unreachable |
| 74 | `L2-T702` | `L2-T702` | `L2-05-tasks.md` | 3460 | high | Execute AT-035 — the organisation export restores |
| 75 | `L2-T703` | `L2-T703` | `L2-05-tasks.md` | 3506 | high | Execute AT-103 — production restore, no hand-held credential |
| 76 | `L2-T555` | `L2-T555` | `L2-05-tasks.md` | 3550 | high | DoD acceptance matrix and lane handoff |

**Note on rows 1–6.** `L2-05-tasks.md` §3 carries a six-line *index stub* for `L2-T001`–`L2-T006` (lines 391, 397, 403, 409, 415, 421) that says verbatim “is not defined here”. Those stubs are **not** counted as bodies; the bodies are the charter's, as mapped above.

### 2.2 The §2.1 pointer table — 26 further ids the master indexes but does not body

(`L2-T001`–`L2-T006` appear in §2.1 as well and are already mapped in §2.1 above.)

| Index id | Body id | Body file | Line | Conf. | What the task does |
| --- | --- | --- | ---: | --- | --- |
| `L2-T500` | `L2-T500` | `L2-04-evidence-chain.md` | 156 | high | Phase-4 branch and the tools/evidence module skeleton |
| `L2-T501` | `L2-T501` | `L2-04-evidence-chain.md` | 259 | high | Pin the phase-4 consumed contract surface |
| `L2-T502` | `L2-T502` | `L2-04-evidence-chain.md` | 318 | high | Author tools/evidence/eleven-questions.yaml |
| `L2-T503` | `L2-T503` | `L2-04-evidence-chain.md` | 441 | high | Author the fixture estate: one closed chain and four broken variants |
| `L2-T504` | `L2-T504` | `L2-04-evidence-chain.md` | 584 | high | Implement tools/evidence/evidence-query |
| `L2-T505` | `L2-T505` | `L2-04-evidence-chain.md` | 794 | high | Conformance-profile substitution and S18 equivalence |
| `L2-T506` | `L2-T506` | `L2-04-evidence-chain.md` | 926 | high | Implement tools/evidence/verify-digest-chain — the comparison core |
| `L2-T507` | `L2-T507` | `L2-04-evidence-chain.md` | 1124 | high | Implement tools/evidence/collect-version.sh — the /version observation collector |
| `L2-T508` | `L2-T508` | `L2-04-evidence-chain.md` | 1408 | high | Implement tools/evidence/build-deployment-record.sh |
| `L2-T509` | `L2-T509` | `L2-04-evidence-chain.md` | 1729 | high | Author .github/workflows/emit-deployment-record.yml |
| `L2-T510` | `L2-T510` | `L2-04-evidence-chain.md` | 1975 | high | Wire the emitter into deploy-staging.yml and deploy-production.yml |
| `L2-T511` | `L2-T511` | `L2-04-evidence-chain.md` | 2073 | high | Author .github/workflows/verify-digest-chain.yml — the scheduled sweep |
| `L2-T512` | `L2-T512` | `L2-04-evidence-chain.md` | 2347 | high | Implement the P0 escalation path |
| `L2-T513` | `L2-T513` | `L2-04-evidence-chain.md` | 2634 | high | Implement tools/evidence/deploy-gate.sh |
| `L2-T514` | `L2-T514` | `L2-04-evidence-chain.md` | 2793 | high | Author .github/workflows/evidence-selftest.yml |
| `L2-T515` | `L2-T515` | `L2-04-evidence-chain.md` | 3047 | high | Append-only and effective-dating assertion |
| `L2-T516` | `L2-T516` | `L2-04-evidence-chain.md` | 3189 | high | Phase-4 roll-up, self-verify sweep and lane PR |
| `L2-T520` | `L2-T520` | `L2-02-digest-invariant.md` | 113 | high | Branch, and the flat-record reader |
| `L2-T521` | `L2-T521` | `L2-02-digest-invariant.md` | 205 | high | The artifact-identity format library |
| `L2-T522` | `L2-T522` | `L2-02-digest-invariant.md` | 300 | high | Compute the S18 platform-rebuild identity (D78) |
| `L2-T523` | `L2-T523` | `L2-02-digest-invariant.md` | 417 | high | THE DIGEST INVARIANT |
| `L2-T524` | `L2-T524` | `L2-02-digest-invariant.md` | 562 | high | Artifact publication check, and the never-rebuild rule |
| `L2-T525` | `L2-T525` | `L2-02-digest-invariant.md` | 633 | high | SBOM beside the digest |
| `L2-T171` | `L2-T171` | `L2-03-production-gates.md` | 259 | high | The actor gate (P3-C) |
| `L2-T172` | `L2-T172` | `L2-03-production-gates.md` | 479 | high | The runner-tier assertion (P3-D) |
| `L2-T173` | `L2-T173` | `L2-03-production-gates.md` | 645 | high | The environment deployment-policy assertion (P3-E) |

### 2.3 Ids the master states only as a *range*

Not rows in any master table. §2.1 bullet 1 states “`L2-03-production-gates.md` §7 owns `L2-T170`–`L2-T177` and `L2-T570`–`L2-T572`”, and §2.1's closing paragraph states “`L2-T526`–`L2-T528` are `L2-02`'s alone”. Expanding those ranges yields eleven further promised ids. All eleven have bodies.

| Index id | Body id | Body file | Line | Conf. | What the task does |
| --- | --- | --- | ---: | --- | --- |
| `L2-T170` | `L2-T170` | `L2-03-production-gates.md` | 155 | high | Phase 3 precondition gate and contract pin |
| `L2-T174` | `L2-T174` | `L2-03-production-gates.md` | 839 | high | The workflow-identity gate (P3-A) |
| `L2-T175` | `L2-T175` | `L2-03-production-gates.md` | 1210 | high | The production gate chain |
| `L2-T176` | `L2-T176` | `L2-03-production-gates.md` | 1410 | high | The rollback reusable workflow (P3-B) |
| `L2-T177` | `L2-T177` | `L2-03-production-gates.md` | 2983 | high | Rebase, open the phase PR, exit |
| `L2-T570` | `L2-T570` | `L2-03-production-gates.md` | 2121 | high | apply-production-gates — the idempotent template-wiring tool |
| `L2-T571` | `L2-T571` | `L2-03-production-gates.md` | 2346 | high | assert-privileged-workflows — the posture assertion (DoD-05) |
| `L2-T572` | `L2-T572` | `L2-03-production-gates.md` | 2668 | high | Phase 3 negative-test suite |
| `L2-T526` | `L2-T526` | `L2-02-digest-invariant.md` | 712 | high | The single build script: build once, record the digest, emit the SBOM |
| `L2-T527` | `L2-T527` | `L2-02-digest-invariant.md` | 874 | high | Test doubles and record fixtures |
| `L2-T528` | `L2-T528` | `L2-02-digest-invariant.md` | 1032 | high | The negative-test harness |

---

## 3. RESIDUE — index ids with no body anywhere

| Index id | What the index promises | Why nothing matches |
| --- | --- | --- |
| *(none)* | — | **Residue is zero.** All 113 ids the master file states resolve to a body. |

**Read this carefully before quoting it.** Zero residue means *no promised id lacks an executable body*. It does **not** mean Lane 2 is dispatchable. Two things still stand between L2 and dispatch, and neither is residue:

1. **`L2-99-review.md` defect B1 is open.** Which decomposition is normative for the lane as a whole — the master file's seventy-six-task list or the phase files' — is L0's call and has not been made. §2.1 settles *where each id's body lives*; it does not settle *which list an executor works*.
2. **41 orphan bodies (§4).** Work that will be executed but appears on no dispatch list, including a complete sixteen-task second build of the reusable-workflow library.

---

## 4. ORPHANS — bodies the master index does not claim

All 41 carry a full body (steps, commands, acceptance criteria, SELF-VERIFY). All 41 are indexed *locally* by their own phase file, so they are not invisible — they are invisible **to `L2-05-tasks.md`**, which is the lane's execution order and the file an executor is told to work top to bottom.

### 4.1 `L2-01-reusable-workflows.md` — a complete second decomposition (16 bodies)

`L2-05-tasks.md` contains the string `L2-P1` **zero times**. This is the sharpest instance of the lane's defect: sixteen fully-bodied tasks building the same eight reusable workflows the master table builds under `L2-T100`–`L2-T144`, in a namespace the master file has never heard of. The last column names the master task that produces the same artifact — a *duplication* map, not a dependency map.

| Body id | File | Line | What it does | Same artifact as (master) |
| --- | --- | ---: | --- | --- |
| `L2-P1-T00` | `L2-01-reusable-workflows.md` | 172 | Lane bootstrap and library skeleton | `L2-T001` / `L2-T530` |
| `L2-P1-T01` | `L2-01-reusable-workflows.md` | 262 | Third-party action pin manifest, applier and verifier | `L2-T531`, `L2-T532` |
| `L2-P1-T02` | `L2-01-reusable-workflows.md` | 418 | Record and event emitter shims | `L2-T544`, `L2-T545` |
| `L2-P1-T03` | `L2-01-reusable-workflows.md` | 531 | gate-actor.yml, the §37.3 actor gate | `L2-T541` (actor gate) |
| `L2-P1-T04` | `L2-01-reusable-workflows.md` | 647 | gate-freeze.yml, the §34.2 Friday-freeze time gate | `L2-T540` (time gate) |
| `L2-P1-T05` | `L2-01-reusable-workflows.md` | 803 | ci.yml | `L2-T100`–`L2-T108` |
| `L2-P1-T06` | `L2-01-reusable-workflows.md` | 1022 | build.yml | `L2-T120` |
| `L2-P1-T07` | `L2-01-reusable-workflows.md` | 1153 | deploy-staging.yml | `L2-T130` |
| `L2-P1-T08` | `L2-01-reusable-workflows.md` | 1271 | deploy-production.yml | `L2-T131` |
| `L2-P1-T09` | `L2-01-reusable-workflows.md` | 1479 | migrate.yml | `L2-T132` |
| `L2-P1-T10` | `L2-01-reusable-workflows.md` | 1642 | restore-production.yml (the engine) | **no master task** — the master builds only the *template* `L2-T307`, never the engine |
| `L2-P1-T11` | `L2-01-reusable-workflows.md` | 1827 | restore-test.yml (the same engine, isolated target) | `L2-T134` |
| `L2-P1-T12` | `L2-01-reusable-workflows.md` | 1935 | org-export.yml | `L2-T136` |
| `L2-P1-T13` | `L2-01-reusable-workflows.md` | 2060 | background-queue.yml | `L2-T137` |
| `L2-P1-T14` | `L2-01-reusable-workflows.md` | 2194 | Per-product caller templates | `L2-T300`–`L2-T311` |
| `L2-P1-T15` | `L2-01-reusable-workflows.md` | 2320 | Cut workflows/v1; request the tag ruleset and the platform.yaml entry | `L2-T112` |

### 4.2 `L2-02-digest-invariant.md` — 9 bodies outside the master's grant

§2.1 grants `L2-02` only `L2-T520`–`L2-T528`. Its §3 also bodies nine ids in the workflow and template bands that the master file never names.

| Body id | File | Line | What it does | Same artifact as (master) |
| --- | --- | ---: | --- | --- |
| `L2-T200` | `L2-02-digest-invariant.md` | 1157 | The reusable build workflow | `L2-T120` (`build.yml`) |
| `L2-T201` | `L2-02-digest-invariant.md` | 1354 | The reusable digest-gate workflow | `L2-T543` + `L2-T131` (digest invariant on the deploy path) |
| `L2-T202` | `L2-02-digest-invariant.md` | 1530 | Control-plane self-test workflow | `L2-T111` (`control-plane-ci.yml`) |
| `L2-T400` | `L2-02-digest-invariant.md` | 1609 | The artifact registry conventions | — none (artifact registry conventions) |
| `L2-T401` | `L2-02-digest-invariant.md` | 1757 | Per-product build template, container products | `L2-T302` (`templates/workflows/build.yml`) |
| `L2-T402` | `L2-02-digest-invariant.md` | 1838 | Per-product build template, S18 platform-rebuild products | — none (S18 platform-rebuild build template) |
| `L2-T403` | `L2-02-digest-invariant.md` | 1923 | The canonical digest-gate call fragment | — none (digest-gate call fragment) |
| `L2-T404` | `L2-02-digest-invariant.md` | 2002 | File the required-context composition blocker | — none (files decision blocker D-L2-07) |
| `L2-T405` | `L2-02-digest-invariant.md` | 2087 | Phase gate: prove everything, rebase, open the PR | — none (phase-PR gate) |

### 4.3 `L2-03-production-gates.md` — 2 template bodies outside the master's grant

§2.1 grants `L2-03` the ranges `L2-T170`–`L2-T177` and `L2-T570`–`L2-T572`. The `L2-T370`–`L2-T399` template band it reserves in its own §1 is named nowhere in the master file.

| Body id | File | Line | What it does | Same artifact as (master) |
| --- | --- | ---: | --- | --- |
| `L2-T370` | `L2-03-production-gates.md` | 1843 | The per-product rollback workflow template | `L2-T309` (the rollback workflow template) |
| `L2-T371` | `L2-03-production-gates.md` | 1998 | The rollback exemption declaration | — none (machine-readable rollback exemption declaration) |

### 4.4 `L2-06-tests.md` — the whole lane test suite, 14 bodies, 0 master rows

The master §2 table contains **no test-suite task at all**. All fourteen are genuinely new work with no master duplicate — they are not redundant, they are simply untracked by the dispatch list. This is the one orphan group that should be *added* to the dispatch list rather than adjudicated against a duplicate.

| Body id | File | Line | What it does |
| --- | --- | ---: | --- |
| `L2-T600` | `L2-06-tests.md` | 549 | The two fixed entry points and the counter harness |
| `L2-T601` | `L2-06-tests.md` | 729 | The eleven gate declarations and the negative-corpus forwarder |
| `L2-T602` | `L2-06-tests.md` | 859 | The fixture estate |
| `L2-T604` | `L2-06-tests.md` | 955 | Tiers X1 and X2 for the six declared-minimum gates |
| `L2-T605` | `L2-06-tests.md` | 1056 | N1: a self-approved deploy MUST fail |
| `L2-T606` | `L2-06-tests.md` | 1156 | N2: a digest mismatch MUST be rejected |
| `L2-T607` | `L2-06-tests.md` | 1262 | N3: a privileged workflow on a shared runner MUST fail |
| `L2-T608` | `L2-06-tests.md` | 1392 | N4: a deploy from a non-default ref MUST be refused |
| `L2-T609` | `L2-06-tests.md` | 1508 | N5: a machine-account approval MUST NOT satisfy the gate |
| `L2-T603` | `L2-06-tests.md` | 1630 | The workflow_dispatch harness (X3), fail-closed while D-L2-11 is open |
| `L2-T221` | `L2-06-tests.md` | 1738 | fixture-dispatch.yml, the X3 driver |
| `L2-T610` | `L2-06-tests.md` | 1820 | The AT coverage map |
| `L2-T611` | `L2-06-tests.md` | 1921 | Coverage floor, vacuity proof and the drill target |
| `L2-T220` | `L2-06-tests.md` | 2033 | lane-suite.yml, the CI trigger for the lane suite |

### 4.5 Deliberately not counted as orphans

* `L2-07-runbook.md` `L2-RB-00`–`L2-RB-14` (15 procedures, lines 116–1528). These are *procedures* an executor applies to every task, not units of work with their own branch and PR. Excluded from both sides. Note only that `L2-05-tasks.md` cites none of them.
* The six `### L2-T001`–`L2-T006` blocks in `L2-05-tasks.md` §3 (lines 391–421). Explicit index stubs, six lines each, no steps and no acceptance criteria — index, not body.
* Range endpoints in `L2-05-tasks.md` §0.9 and `L2-00-charter.md` §12 (`L2-T099`, `L2-T299`, `L2-T499`, `L2-T599`, `L2-T649`, `L2-T699`, `L2-T799`). Namespace boundaries, never task ids.

---

## 5. Namespaces found in Lane 2

Four disjoint grammars. A heading-only grep on any one of them under-reports.

| Grammar | Where | Bodies |
| --- | --- | ---: |
| `L2-Tnnn` | charter §11, `L2-02` §3, `L2-03` §7, `L2-04` §6, `L2-05` §§3–5, `L2-06` §10 | 138 |
| `L2-P1-Tnn` | `L2-01` §3 only | 16 |
| `L2-RB-nn` | `L2-07` only | 15 (procedures, not tasks) |
| `D-L2-nn`, `L2/P1/DEC-x` | decision registers in six files | not tasks |

**Where heading-only greps would have lied.** `grep '^### L2-T'` over `L2-01-reusable-workflows.md` returns **zero** — the file's sixteen bodies are all `### \`L2-P1-Tnn\``, backticked and in a different namespace. That single omission is the whole 16-body orphan group.

---

## 6. Exact commands used

Run from `C:/D_Drive/PS/MultiProduct/Code/implementation/lanes` in Git Bash.

```bash
# 0. The measured copies
wc -l L2-0*.md

# 1. INDEX side - three statements, unioned
#    (a) the section-2 execution table, rows 1-76
awk 'NR>=222 && NR<=304' L2-05-tasks.md \
  | grep -oE "^\| *[0-9]+ \| L2-T[0-9]{3}" | grep -oE "L2-T[0-9]{3}" | sort -u      # 76
#    (b) the section-2.1 pointer table, left column
sed -n '304,360p' L2-05-tasks.md \
  | grep -oE "^\| .L2-T[0-9]{3}." | grep -oE "L2-T[0-9]{3}" | sort -u               # 32, 6 shared with (a)
#    (c) the section-2.1 / section-10 note-2 RANGE statements, expanded:
#        L2-T170..L2-T177, L2-T570..L2-T572, L2-T526..L2-T528                        # +11 new
#    union -> 113

# 2. BODY side - several patterns, unioned; ## and ### both, backticks optional
for f in L2-00-charter.md L2-01-reusable-workflows.md L2-02-digest-invariant.md \
         L2-03-production-gates.md L2-04-evidence-chain.md L2-06-tests.md; do
  grep -nE "^#{2,4} .?L2-(T[0-9]{3}|P1-T[0-9]{2}).?" "$f" | sed "s|^|$f:|"
done
#    L2-05-tasks.md: skip section 3's six index stubs (lines 391-421); take from 427 on
awk 'NR>=427' L2-05-tasks.md | grep -nE "^### L2-T[0-9]{3}"
#    -> 154 distinct body ids

# 3. Body-ness check - a body has an acceptance block and a SELF-VERIFY
for f in L2-0*.md; do printf '%-32s SELF-VERIFY=%s Acceptance=%s\n' "$f" \
  "$(grep -ciE 'SELF-VERIFY' $f)" "$(grep -ciE '^\*?\*?Acceptance' $f)"; done
#    L2-05-tasks.md -> Acceptance=70, i.e. 76 headings minus the 6 stubs

# 4. Table-row scan, to prove no Lane 2 body hides in a table (the L4-06 failure mode)
grep -nE "^\| .?L2-(T[0-9]{3}|P1-T[0-9]{2})" L2-0*.md | wc -l   # index rows only, no bodies

# 5. The two set differences
comm -23 INDEX.txt BODY.txt          # RESIDUE -> empty
comm -13 INDEX.txt BODY.txt          # ORPHANS -> 41
comm -12 INDEX.txt BODY.txt | wc -l  # MAPPED  -> 113
```

---

## 7. What this changes for dispatch

1. **Nothing needs to be written.** Residue is zero. No task body is missing from Lane 2. L2 contributes **0** to the founder's cross-lane unbuilt-work list.
2. **`L2-99-review.md` B1 is still open and still blocks.** L0 must declare which decomposition is normative. This concordance narrows that decision to one question: *are the 41 orphan bodies in scope for cycle 1, and if so under which id?*
3. **The 16 `L2-P1-T*` bodies are the decision that actually matters.** They build the same eight reusable workflows as `L2-T100`–`L2-T144`. If both lists dispatch, one executor authors the same workflow files twice on two branches. One of the two must be marked superseded — an L0 call, and this file does not make it. One asymmetry worth L0's attention: `L2-P1-T10` builds `restore-production.yml` itself, and the master list builds only its *template* (`L2-T307`). Retiring `L2-01` wholesale would drop that engine.
4. **`L2-06-tests.md`'s 14 bodies should simply be appended to the dispatch list under their existing ids.** They duplicate nothing, and the master table has no test tasks at all.

---

## Session 12 update (2026-09-08)

**Last-verified:** 2026-09-08 (Session 12).

### Measurement update

| File | Previous `wc -l` | Updated `wc -l` |
| --- | ---: | ---: |
| `L2-05-tasks.md` | 3,800 | **10,738** |

All other file sizes unchanged from the 2026-09-02 measurement.

### Structural fixes applied in Session 12

- **DO-NOT-DISPATCH** header retracted — the blanket block was removed; individual task-level gates remain where applicable.
- **SUPERSEDED banners narrowed** — broad file-level SUPERSEDED notices replaced with section-scoped annotations so only the genuinely retired sections are marked.
- **FD-053 propagated** — the founder decision is now cited in every affected task body within L2-05.

### L2-99 re-review (Session 12): **PASS**

---

## Session 13 Update (2026-09-08)

- **Task body audit complete** — all L2 task bodies verified present; 0 stub bodies confirmed (concurrent agent results pending final count).
- **L2 decision memos created** — PENDING_FOUNDER_DECISIONS.md now carries L0-choice memos for L2-B1 (normative decomposition selection: master 76-task list vs. phase files), L2-B3 (L2-P1-T10 restore-production.yml engine — retire or retain), and L2-B6 (test-suite orphans in L2-06: add to dispatch list or adjudicate); these must be resolved before L2 can be fully dispatched.
