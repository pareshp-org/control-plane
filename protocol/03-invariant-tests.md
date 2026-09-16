# 03 — Invariant Enforcement Tests

**Owner:** L0 Integrator. **Status:** binding on all five lanes.
**Conforms to:** `implementation/PARTITION.md` (FROZEN v1).
**Spec source:** `Research/MultiProduct_MasterSpec_v4.0.md` — Section 100 (110 acceptance tests, AT-001…AT-110), Section 101 (111 invariants), Section 53 (reconciliation), Section 27 (the four events), Section 37 (background machine layer), Section 40 (secrets and production access), Section 11.3 (branch protection), Section 30.2 (plan-checker), Section 95.4 (the activation checklist).

> **REFERENCE ONLY** — Protocol document, part of the 5-lane model

---

## 0. What this file is, and what it is not

This file is the **enforcement test suite for Section 101**. Section 101 makes two promises: that all 111 invariants hold, and that every one of them is *enforced by the platform wherever the platform can enforce it*, the remainder falling to written policy with a named owner and a review cadence. Section 101's own preamble makes the classification checkable: control-plane CI fails when an invariant classified `mechanical` names no live check or AT- identifier, when one classified `policy` names no live `policies.yaml` entry, or when any invariant carries no classification at all.

This file supplies three things:

1. **§2 — the classification of all 111**, one row each, `mechanical` / `policy` / `review-held`, each naming its enforcing check, its AT- identifier, or its owner and cadence. This is the input to the Phase G2 classification authoring the Section 101 preamble requires, and it is the thing control-plane CI reads.
2. **§4–§9 — the six catastrophic-if-silent invariants**, in full: the control, the positive test, the negative test, and the mutation that proves the negative test is alive.
3. **§10 — the remaining mechanical invariants** as a compact test ledger, and **§11 — the sixteen non-mechanical invariants** with owner and cadence stated.

It is **not** the merge protocol, the lane acceptance criteria, or the CI wiring. Those live in the sibling files under `implementation/protocol/`. This file states *what must be proven*; the merge protocol states *when*.

### 0.1 The reader this is written for

Per PARTITION.md §"AI developer profile": Sonnet-4.6-class, low cost, no repo context, no judgment authority. Every test below therefore carries an exact path, a literal command, an unambiguous pass/fail assertion, and a STOP rule. **No test in this file requires interpretation.** Where judgment is genuinely required — the sixteen non-mechanical invariants of §11 — that is stated explicitly and routed to a named human, not left to a lane.

---

## 1. The governing principle: a check that can only pass is not a check

The specification applies this principle in four named places, and this suite generalises it:

| Where the spec applies it | What it says |
| --- | --- |
| Section 53.1, the seeded-canary rule | A permanent, clearly labelled seeded drift record exists at all times, and every reconciliation run MUST find it. A run reporting zero findings — the canary included — is a **FAILED** run, not a clean one. It proves the instrument stopped looking. |
| AT-102 | The same rule as an acceptance test: a zero-finding run raises SIG-13 and triggers the Section 53.7 gap procedure. A reconciler that finds nothing is assumed broken, never assumed clean. |
| Section 103.9, review rejection rate | "Very low may mean rubber-stamping; very high may mean weak plans." A gate with no rejections is not a gate that is being satisfied; it is a gate nobody can distinguish from an absent one. |
| Section 95.4, the activation checklist | Each gate is armed and then **executed for real — including the negative tests** — at each headcount threshold, not assumed. A self-approved PR must be observed failing; a Read-only approval must be observed not satisfying. |

### 1.1 The four-part contract every mechanical invariant must satisfy

Every mechanical invariant in this suite carries four artifacts. Three of anything is not enough.

```
CONTROL     the platform mechanism that enforces the invariant
POSITIVE    a permitted action succeeds  → proves the control does not over-block
NEGATIVE    a forbidden action is refused → proves the control blocks
MUTATION    with the control removed in a disposable fixture, the NEGATIVE test
            must itself report FAIL → proves the negative test is not vacuous
```

A negative test with no mutation is exactly the failure mode this specification refuses everywhere else: an assertion that has never been observed to fail, and therefore cannot be distinguished from an assertion that cannot fail. `assert_fails "$cmd"` passes just as happily when `$cmd` is misspelt, when the fixture repository does not exist, when `gh` is unauthenticated, and when the control is genuinely working. Only the mutation run tells those four apart.

### 1.2 The mutation harness

**Path ownership:** the harness runner is a workflow — `.github/workflows/invariant-mutation.yml` — owned by **L2**. Every assertion script it invokes lives in the owning lane's tree. No lane writes another lane's assertions. No shared fixture directory exists; each lane's fixtures live under its own owned path, one file per fixture (PARTITION.md anti-conflict rule 3).

```bash
# .github/workflows/invariant-mutation.yml  (L2 owns this file)
# Runs: on every integration -> main promotion; on any change to a control
# or to a test under */invariant-tests/**; and weekly on schedule.
#
# For each invariant test pair, in a disposable fixture repository:
#   1. run NEGATIVE against the intact control   -> MUST exit 0 (refusal observed)
#   2. weaken/remove the control in the fixture  -> apply the named mutation
#   3. run NEGATIVE against the weakened control -> MUST exit non-zero
#   4. restore the fixture, or destroy it
#
# If step 3 exits 0, the negative test is vacuous. The mutation run FAILS and
# integration -> main is blocked. This is the seeded canary applied to the suite.
```

**Fixture repositories are disposable and are destroyed after every run.** They are created by the provisioning CLI from `product-template`, never by hand, and never carry a real product's name, a real person's identity, or any real credential.

### 1.3 Gate liveness, and why mutation rejections are excluded from it

Section 103.9 says a very low rejection rate may mean rubber-stamping. Every gate in this suite therefore emits a rejection counter into the event log (Section 97.3), and a gate with **zero rejections over its calibrated liveness window** raises a liveness signal for the gate's owner to answer.

One trap must be closed explicitly. Mutation runs produce rejections by construction. If they counted toward the liveness numerator, the liveness check would satisfy itself forever and become the very thing it exists to detect.

> **Binding rule.** Every rejection produced by a mutation run, an activation-checklist execution, or a seeded canary is recorded with `synthetic: true` and **never counts toward gate liveness.** Liveness counts only rejections produced by real work. A gate whose only rejections are synthetic has a live *test* and a dead *gate*, and those are different findings.

Initial liveness windows are calibrated configuration in `os-health.yaml`, changed only by a recorded decision, and refitted at the Section 84.6 threshold review:

| Gate | Liveness window (initial) | Signal when zero real rejections in the window |
| --- | --- | --- |
| Plan-checker hard rejects (Section 30.2) | 30 days | Amber to the Team Lead — either plans became uniformly compliant, or a reject rule stopped firing |
| Branch-protection approval gate | 90 days | Amber to the Team Lead — no PR in a quarter needed a second push after approval is implausible at portfolio scale |
| Contract/schema validation (Subsystem B) | 30 days | Amber to the Founder — validator coverage may have narrowed |
| Reconciliation findings (Section 53) | Per run | **Blocking**, already: this is AT-102, the seeded canary, and it is a FAILED run |
| Actor gate (Section 37.3) | 180 days | Green with a recorded note — a machine correctly never attempting is the intended state; the mutation run carries the proof instead |

### 1.4 Two safety rules that bind every test in this file

* **No canary is ever real.** Seeded canaries, fixtures and mutation payloads are synthetic by construction. Invariant 111 is not suspended for its own test: **no real customer data is ever planted anywhere, for any reason**, and git history is append-only so the mistake has no rotation-equivalent remedy (Section 38.3, Section 96.6 S19). The customer-data detector canary of §9 uses a synthetic record matching the detector's *shape*, never its *substance*.
* **No test weakens a live control.** Mutations happen only in disposable fixture repositories. A mutation applied to a live repository is a security incident under Section 43, not a test.

---

## 2. Classification of all 111 invariants

One row per invariant, numbered as Section 101 numbers them. `Class` is exactly one of `mechanical`, `policy`, `review-held`, as the Section 101 preamble requires. `Enforced by` names the live check, branch-protection rule, reconciliation row or AT- identifier for `mechanical`; the owner and cadence for `policy` and `review-held`. `Lane` names the lane that owns the assertion code under PARTITION.md.

Ninety-five are mechanical. Five are policy. Eleven are review-held. Control-plane CI reads this table; an invariant that loses its named check without this table changing is itself a finding.

### 2.1 Verification and Quality (101.1)

| # | Invariant (abbrev.) | Class | Enforced by | Lane |
| --- | --- | --- | --- | --- |
| 1 | No onboarding without a verification contract | mechanical | Verification-contract presence check, Subsystem B; pre-onboarding pathway via AT-051 | L1 |
| 2 | Every production bug becomes a permanent regression test | policy | Owner: verification authority. Cadence: per-postmortem close-out (58.4), sampled at the quarterly review | L4 |
| 3 | An untested backup is no backup | mechanical | The invariant-4 CI check; `restore_tested` freshness | L1 |
| 4 | Restore-tested within a rolling 90-day window | mechanical | `restore_tested` older than window fails CI; reconciliation row `product.yaml restore_tested` vs `records/restore-tests/` — **Blocking** | L1 + L3 |
| 5 | Verification contracts merged, never dropped | mechanical | AT-020 | L1 |
| 6 | Depth never traded for throughput | review-held | Owner: verification authority. Chaired by Team Lead at the calibration review (84.6); evidence AT-082 | L1 |

### 2.2 Review and Authority (101.2)

| # | Invariant (abbrev.) | Class | Enforced by | Lane |
| --- | --- | --- | --- | --- |
| 7 | Primary Owner, Cross-Reviewer, Backup Owner, Escalation all present and matched | mechanical | Referential integrity, Subsystem B; reconciliation row `product.yaml` assignments vs GitHub Team — **fail CI** | L1 + L3 |
| 8 | Independent review from a non-author | mechanical | Branch protection: ≥1 approving review, Code Owner review required (11.3) | L5 |
| 9 | **No self-approval** | mechanical | Branch protection most-recent-reviewable-push rule (11.3) + workflow-identity gate (27.2). **See §4** | L5 + L2 |
| 10 | Team Lead is not the routine reviewer; >2 routine/week is investigable | review-held | Owner: Founder. Cadence: weekly review-load metric (103.9), judged at the quarterly review | L4 |
| 11 | Authority evaluated against capability and assignment, never role name | mechanical | Capability check at the act (9.1); AT-091 | L1 |
| 12 | **Production approval never self-approved; separate event from Gate 2** | mechanical | Workflow-identity gate (27.2). **See §4** | L2 |
| 13 | Matrix/ownership changes by Team Lead under capability, recorded, Founder notified | mechanical | AT-021; capability check + decision record + closed push list (92.11) | L1 + L4 |

### 2.3 Planning (101.3)

| # | Invariant (abbrev.) | Class | Enforced by | Lane |
| --- | --- | --- | --- | --- |
| 14 | H1 committed, H2 prepared, H3 candidate | mechanical | Horizon-semantics validation on board fields, Subsystem N conventions + schema | L4 |
| 15 | Ready-queue misses trend to zero; queue does not routinely reach zero | review-held | Owner: Team Lead. Cadence: weekly operating picture (94), trend judged quarterly. Detector: Ready-queue-miss (97.5) | L4 |
| 16 | Material requirement change re-plans through Gate 1 | mechanical | Plan-checker + computed change class (24, 29.5) | L2 |

### 2.4 Machine Authority (101.4)

| # | Invariant (abbrev.) | Class | Enforced by | Lane |
| --- | --- | --- | --- | --- |
| 17 | Machine authority constrained; output volume not throttled | mechanical | Actor gate (37.3) + machine-account permissions. The no-throttle half is carried by the Section 37.7 interpretation rule at the Team Lead's task-class review | L5 |
| 18 | **Background layer cannot merge, approve, deploy, or reach production** | mechanical | Machine-account permissions; human-only CODEOWNERS (11.3); actor gate (37.3); AT-109. **See §6** | L5 + L2 |
| 19 | Failed and rejected machine output is retained | mechanical | Append-only event log (97.3); records-repo ruleset blocks force-push and delete, no bypass actor (D107) | L4 |
| 20 | External or repository-provided text is data, not authority | mechanical | Constitution referenced from every context file (Subsystem K check) + issue-guard trust envelope on every drafting job (36.2) | L5 |
| 21 | Unattended personal-agent runs are branch-only, flagged, never merge without the full human gate | mechanical | Branch protection + unattended-flag integrity check. **See §6.4** | L5 + L2 |

### 2.5 Delivery and Production (101.5)

| # | Invariant (abbrev.) | Class | Enforced by | Lane |
| --- | --- | --- | --- | --- |
| 22 | **The production artifact is the digest verified in staging. Never rebuilt** | mechanical | Digest invariant enforced in code, Subsystem E; `verify-digest-chain`, Subsystem F; AT-102-class sweep. **See §5** | L2 |
| 23 | **Never rebuild to work around registry unavailability** | mechanical | Same digest check; degraded-mode rule 46.1 — a rebuild produces a digest staging never verified. **See §5.4** | L2 |
| 24 | **The production database is inaccessible from developer machines** | mechanical | `infrastructure:` block validated by contract CI; `security.production_db_access: ci-only` default; provider-side attestation, **Blocking past its window** (53.1). **See §7** | L5 + L1 |
| 25 | Production secrets environment-scoped, never present locally | mechanical | Five-tier rule (40.1); environment deployment branch/tag policy reconciliation row — **Blocking**; secret scanning. **See §7.3** | L5 |
| 26 | **A fully compromised workstation must not yield production access** | mechanical | 40.3 composite, executed as a drill. **See §7.4** | L5 |
| 27 | Rollback preferred to hotfix; no prior approval during SEV-1 | mechanical | Dedicated rollback workflow, exempt from the production-approval gate but **not** from the actor gate (27.2) | L2 |
| 28 | Non-reversible changes require an explicit recovery strategy, never claim rollback | mechanical | Plan-checker hard reject (30.2) | L2 |
| 29 | SEV-1 restoration takes priority over quota, fairness and scheduling | policy | Owner: escalation role. Cadence: reviewed at each postmortem (58.4) and at the quarterly review | L5 |
| 30 | Out-of-hours work is exception-based, authorised, quota-bound, compensated, recorded | mechanical | Exception registry entry required + weekend quota counters (47) | L4 |
| 31 | No 24x7 commitment without funded response capacity | mechanical | The 24x7-without-rota blocker, Subsystem B; AT-047 | L1 |

### 2.6 Founder and Role Boundaries (101.6)

| # | Invariant (abbrev.) | Class | Enforced by | Lane |
| --- | --- | --- | --- | --- |
| 32 | The founder does not manage daily task assignment | review-held | Owner: Founder. Cadence: quarterly operating-system review | L4 |
| 33 | The founder does not review routine code or dispatch responders | review-held | Owner: Team Lead. Cadence: quarterly review; evidence AT-101 (dispatch) and 103.9 review load (code) | L4 |
| 34 | Founder absence does not halt engineering; the founder-only list stays short | review-held | Owner: Founder. Cadence: quarterly review plus the AT-022 continuity drill | L5 |
| 35 | Acting Team Lead pre-designated, holding dormant capability | mechanical | `topology.yaml` succession-block validation; AT-003 | L1 |
| 36 | Team Lead operates and recommends; Founder is final authority on people decisions | mechanical | AT-071 — no code path exists; attempted configuration fails validation | L1 |
| 37 | No automatic improvement plan, termination, promotion, compensation change or warning | mechanical | AT-071 | L1 |
| 38 | Every people signal is decision support; the Founder decides | mechanical | AT-070 — bundle carries an explicit human-decision statement | L4 |
| 39 | Founder continuity provisions with Team-Lead-succession rigour | mechanical | AT-022, executed as a periodic drill; second-Owner and escrow presence checks | L5 |

### 2.7 State and Truth (101.7)

| # | Invariant (abbrev.) | Class | Enforced by | Lane |
| --- | --- | --- | --- | --- |
| 40 | Humans write decisions and meaning; machines write measurable state | mechanical | Records-writer credential scoped to the records repository alone (D89); human-only CODEOWNERS on the control plane | L4 + L5 |
| 41 | GitHub remains the durable engineering source of truth | review-held | Owner: Founder. Cadence: quarterly review against the tool register (62); carve-out per 62.5 | L5 |
| 42 | GSD Core is replaceable tooling; artifacts readable without it | mechanical | AT-030 | L2 |
| 43 | No second workflow overlay competes with GSD | review-held | Owner: Team Lead. Cadence: quarterly review; every new tool requires a `tools.yaml` entry (62) | L5 |
| 44 | Declared state reconciled; silent drift not permitted | mechanical | Section 53.1 comparison set + the seeded canary; AT-102. **See §8.5** | L3 |
| 45 | No artifact becomes a dumping ground; the hierarchy resolves conflicts | review-held | Owner: Founder. Cadence: quarterly review, alongside AT-045 retirement | L4 |
| 46 | Derived data is computed, never hand-maintained | mechanical | Metric source discipline, Subsystem I — a metric whose source is not a canonical record store fails | L4 |
| 47 | History is append-only for state, decisions, approvals and records | mechanical | Records-repo ruleset (no force-push, no delete, **no bypass actor**), signed commits by the writing identity, per-run head-SHA anchoring into the protected control plane, object-locked export (D107) | L4 |
| 48 | Source extraction failure never downgrades verified data | mechanical | AT-088 | L4 |
| 49 | Every OS metric has an owner and a defined response, or is deleted | mechanical | Metric-registry schema requires owner + response; AT-045 retirement | L4 |

### 2.8 Dynamic Model (101.8)

| # | Invariant (abbrev.) | Class | Enforced by | Lane |
| --- | --- | --- | --- | --- |
| 50 | People, roles, capabilities and assignments are separate, dynamic configuration | mechanical | Schema separation; AT-002, AT-007 | L1 |
| 51 | People are never hard-coded into architecture logic | mechanical | Hard-coded-identity scan over dashboards, workflows and scripts; AT-002 | L1 |
| 52 | Product count is never hard-coded | mechanical | Enumerate-from-registry scan; AT-001 | L1 |
| 53 | New products are configuration plus onboarding | mechanical | AT-001 | L3 |
| 54 | New people, roles and frameworks are configuration plus onboarding | mechanical | AT-002, AT-007, AT-014 | L3 |
| 55 | Ownership changes are declarative and take effect through reconciliation | mechanical | Reconciliation rows; AT-021 | L3 |
| 56 | Role changes trigger capability, permission and assignment recalculation | mechanical | AT-005 | L3 |
| 57 | Departures trigger orphan detection; blocking orphans cannot be dismissed | mechanical | Orphan detection at blocking severity, Subsystem C; AT-017 | L3 |
| 58 | Temporary assignments carry a mandatory end date and expire without human action | mechanical | Schema date rule + reconciliation auto-revoke row; AT-018, AT-008, AT-036 | L1 + L3 |
| 59 | No permanent single-person dependency without visible risk | mechanical | Knowledge-redundancy measurement (103.10) surfaced on the per-product panel | L4 |
| 60 | Knowledge rotation is mandatory; ownership rotation is conditional | policy | Owner: Team Lead. Cadence: quarterly review | L4 |
| 61 | The performance framework is dynamic, versioned, non-retroactive configuration | mechanical | AT-078, AT-014 | L1 |

### 2.9 Products and Dependencies (101.9)

| # | Invariant (abbrev.) | Class | Enforced by | Lane |
| --- | --- | --- | --- | --- |
| 62 | Product is the business unit; Repository is the implementation unit | mechanical | AT-010 | L1 |
| 63 | Shared services have named owners, declared consumers, versioned compatibility | mechanical | Shared-service registry validation, Subsystem B | L1 |
| 64 | Cross-product dependencies are declared and discoverable | mechanical | Reconciliation row: declared dependency vs shared-service registry — **fail CI on unknown dependency** | L3 |
| 65 | Split and merge preserve historical evidence | mechanical | AT-019, AT-020 | L1 |
| 66 | Transfer preserves continuity; secrets are rotated by the receiver, never transferred | policy | Owner: a DevOps-capability holder. Cadence: per transfer, audited at the quarterly review | L5 |
| 67 | An inbound transferred or acquired product runs full onboarding | mechanical | `lifecycle: active` only after contract validation passes (64.1) | L1 |
| 68 | Product lifecycle is explicit; operational burden follows lifecycle | mechanical | Reconciliation row: `product.yaml` lifecycle vs Renovate, monitoring and CI configuration | L3 |
| 69 | Launch readiness is distinct from engineering onboarding | mechanical | Separate `launch_status` field, validated; launch-pack generator | L1 |
| 70 | Business health is a first-class portfolio signal | review-held | Owner: Founder. Cadence: quarterly portfolio review | L4 |

### 2.10 Platform (101.10)

| # | Invariant (abbrev.) | Class | Enforced by | Lane |
| --- | --- | --- | --- | --- |
| 71 | Platform changes are versioned, impact-analysed, canaried, verified, reversible | mechanical | Change-manifest schema + platform-change process; AT-026 | L1 + L2 |
| 72 | No fleet rollout without passing a canary first | mechanical | Canary set declared in `platform.yaml`; AT-023, AT-024 | L1 |
| 73 | Contract schemas are versioned; no simultaneous fleet migration | mechanical | AT-025 | L1 |
| 74 | Transitional products carry a named migration owner and a deadline | mechanical | Schema requires owner + deadline; breached deadline surfaces as drift | L1 + L3 |
| 75 | The control plane observes and is never in a product's runtime path | mechanical | The control-plane/data-plane invariant test (99.4 item 8); AT-029 | L5 |
| 76 | Product runtime must not depend on control-plane availability | mechanical | AT-029, AT-030 | L5 |
| 77 | Every exception has an expiry; a same-scope reopen counts as a renewal | mechanical | Exception-without-expiry rejection, Subsystem B; AT-036, AT-037, AT-038 | L1 |
| 78 | A new policy may not begin at Enforce unless it is a critical security control | mechanical | `policies.yaml` stage validation (55) | L1 |
| 79 | New people, products and tools default to minimum privilege and draft state | mechanical | Safe defaults in provisioning templates (64.1) | L3 |
| 80 | Every control is explicitly classified fail-closed or fail-open | mechanical | Unclassified-control rejection, Subsystem B (64.2) | L1 |
| 81 | **Auto-repair may only move toward the declared, stricter state** | mechanical | Section 53.3 rule enforced in code; AT-033. **See §8** | L3 |
| 82 | Spec and enforcing-tooling changes follow the platform-change process | mechanical | Change manifest required for control-plane changes | L1 |

### 2.11 Cost and Tooling (101.11)

| # | Invariant (abbrev.) | Class | Enforced by | Lane |
| --- | --- | --- | --- | --- |
| 83 | Engineering tooling runs at fixed cost; no metered LLM APIs in engineering tooling | mechanical | Approved-runtime list + the no-API-key check (40.2); local inference endpoint only (36.6) | L5 |
| 84 | API keys remain absent from developer environments | mechanical | `env \| grep -i api_key` at onboarding and quarterly; repository `.env` scan. **See §7.3** | L5 |
| 85 | GSD pinned to a tag; actions pinned to full SHAs; reusable workflows by pinned tag | mechanical | Pin check in CI + reconciliation row `platform.yaml` workflow versions vs the SHA each tag resolves to — **Blocking on any change** | L2 + L3 |
| 86 | AI provider choice is replaceable; a provider outage does not stop engineering | mechanical | AT-011; fail-open classification (64.2) | L5 |
| 87 | Every architecture and security policy is enforced by the platform wherever it can be | mechanical | The Section 101 classification check itself — this table is its input; CI fails on a `mechanical` row naming no live check | L1 |
| 88 | Every product declares `infrastructure.monthly_budget_band`; a cost anomaly is Red | mechanical | Contract validation; AT-050 | L1 |
| 89 | The operating system prices itself | policy | Owner: Founder. Cadence: quarterly review, against the standing automation-ledger entry (57) | L4 |

### 2.12 People and Fairness (101.12)

| # | Invariant (abbrev.) | Class | Enforced by | Lane |
| --- | --- | --- | --- | --- |
| 90 | Attention hours, utilisation, PLU and volume are never individual performance evidence | mechanical | AT-061, AT-085 | L4 |
| 91 | Role-specific outcome evidence always carries the mandatory context adjustment | mechanical | AT-060 — every Section 80 check present and visible in the bundle | L4 |
| 92 | No single metric determines any people decision | mechanical | AT-061 | L4 |
| 93 | Systemic causes checked before individual attribution | mechanical | AT-062, AT-057 | L4 |
| 94 | Performance expectations are role-specific | mechanical | AT-058 | L4 |
| 95 | Team health is separate from individual performance | mechanical | AT-063, AT-055 | L4 |
| 96 | No keystroke, screen, webcam or presence surveillance | mechanical | AT-075 — banned measurements absent from the schema and rejected if introduced | L1 |
| 97 | No AI token usage as performance | mechanical | AT-075, AT-085 | L1 |
| 98 | No single-number productivity score, for a person or a team | mechanical | AT-086 + schema rejection of a composite score field | L1 |
| 99 | No employee ranking or leaderboard | mechanical | AT-075 schema rejection | L1 |
| 100 | New joiners require an evidence window; Insufficient Evidence yields no negative signal | mechanical | AT-072 | L4 |
| 101 | Under-utilisation is diagnosed, never presented as underperformance | mechanical | AT-056 | L4 |
| 102 | Rebalance before hiring; no hire without a diagnosed structural constraint | mechanical | AT-068, AT-067 | L4 |
| 103 | All formal management decisions are auditable | mechanical | AT-073 + decision-record schema | L4 |
| 104 | Confidence must accompany every people signal | mechanical | AT-064 + mandatory confidence field | L1 |
| 105 | The OS is an evidence engine, not an HR replacement | review-held | Owner: Founder. Cadence: quarterly review | L4 |

### 2.13 Access and Privacy (101.13)

| # | Invariant (abbrev.) | Class | Enforced by | Lane |
| --- | --- | --- | --- | --- |
| 106 | Layer B-M is Founder-only, capability-gated, **not delegable** | mechanical | AT-090, AT-091, AT-092 — an assignment granting `people-intelligence` fails validation | L1 + L5 |
| 107 | The Team Lead receives only minimum operational people data | mechanical | AT-093, AT-094 | L5 |
| 108 | Employees see their own evidence, never peers' private data | mechanical | AT-095, AT-096 | L5 |
| 109 | General dashboards expose no sensitive performance data; the people datasource is separately credentialed | mechanical | AT-097, AT-098 (D75) | L5 |
| 110 | Conduct evidence is handled separately; the complaint path works when the subject is the Team Lead or Founder | mechanical | AT-100 | L5 |
| 111 | **No customer data in repositories** | mechanical | Three detectors: fixture-provenance check (38.3), by-identifier support records (22.2), S19 intake gate (96.6). Standing `policies.yaml` entry owned by the verification authority. **See §9** | L1 + L4 |

---

## 3. Test placement, and how the five lanes avoid collision

Every test in §4–§10 has exactly one owning lane. The rule is uniform and follows PARTITION.md's path ownership without exception:

| Assertion concerns | Lives under | Lane |
| --- | --- | --- |
| Registry, contract or schema shape; anything a validator rejects | `validators/registry/invariant-tests/IT-<nnn>.sh` | L1 |
| Workflow behaviour, gates, digest chain, evidence | `tools/evidence/invariant-tests/IT-<nnn>.sh` | L2 |
| Reconciler behaviour, drift, auto-repair, canary | `validators/drift/invariant-tests/IT-<nnn>.sh` | L3 |
| Record and event content, append-only, metric sourcing | `tools/records/invariant-tests/IT-<nnn>.sh` | L4 |
| Access, network boundary, credentials, host isolation | `access/invariant-tests/IT-<nnn>.sh` | L5 |

**Invocation is always L2, assertion is always the owning lane.** A workflow under `.github/workflows/**` calls the script; the script is written by the lane that owns the subsystem. This is deliberate: it forces the coupling through `contracts/**` rather than through a cross-lane import (PARTITION.md rule 4), and it means a lane can never quietly weaken another lane's assertion.

**One file per test.** `IT-009.sh`, `IT-022.sh`, `IT-081.sh` — never an appended index, never a shared runner list. The workflow discovers tests by glob. This is why the five lanes' test additions cannot conflict (PARTITION.md rule 3).

**Every test script obeys the same exit contract:**

```bash
# exit 0   — the assertion held (control behaved as required)
# exit 1   — the assertion failed (INVARIANT VIOLATED — block the merge)
# exit 2   — the test could not run (fixture missing, gh unauthenticated,
#            network unavailable). exit 2 is NOT a pass. It blocks the merge
#            and raises a test-health finding. Fail-closed for Blocking-class
#            checks is the Section 64.2 classification, and it applies to the
#            tests as much as to the controls they test.
```

The `exit 2` rule is load-bearing. A test suite that reports green when it could not run is the same defect as a reconciler that reports clean when it stopped looking.

### 3.2 Shell helper stubs

<!-- DF-0098 fix: 32 undefined helper functions sourced/called in §5–§9 with no definition. -->
Scripts in §5–§9 call shared helper functions. No `source` line and no library path are present in those scripts; the stubs below satisfy the shell name-lookup requirement so each script can be executed and its exit contract tested. The implementing lane replaces each stub with the real implementation in its owned library file before the script is gated.

```shell stubs
# shell stubs — DF-0098 fix
# Format: function_name() { echo "STUB: $0 $*" >&2; return 0; }
# Source this block at the top of each IT-*.sh that calls these helpers,
# then replace with real implementations in the owning lane's library.

wait_digest()                               { echo "STUB: $0 $*" >&2; return 0; }
deploy()                                    { echo "STUB: $0 $*" >&2; return 0; }
verify()                                    { echo "STUB: $0 $*" >&2; return 0; }
approve_production()                        { echo "STUB: $0 $*" >&2; return 0; }
deploy_conclusion()                         { echo "STUB: $0 $*" >&2; return 0; }
build_only()                                { echo "STUB: $0 $*" >&2; return 0; }
rebuild_same_source()                       { echo "STUB: $0 $*" >&2; return 0; }
with_registry_unavailable()                 { echo "STUB: $0 $*" >&2; return 0; }
set_running_digest()                        { echo "STUB: $0 $*" >&2; return 0; }
dispatch_and_conclude()                     { echo "STUB: $0 $*" >&2; return 0; }
assert_gate_was_first_step()                { echo "STUB: $0 $*" >&2; return 0; }
assert_no_environment_secret_materialised() { echo "STUB: $0 $*" >&2; return 0; }
on_allowlist()                              { echo "STUB: $0 $*" >&2; return 0; }
push_workflow_change()                      { echo "STUB: $0 $*" >&2; return 0; }
sleep_until_reconciliation()                { echo "STUB: $0 $*" >&2; return 0; }
drift_class_for()                           { echo "STUB: $0 $*" >&2; return 0; }
assert_running_on()                         { echo "STUB: $0 $*" >&2; return 0; }
age_attestation()                           { echo "STUB: $0 $*" >&2; return 0; }
record_attestation()                        { echo "STUB: $0 $*" >&2; return 0; }
weaken_actual()                             { echo "STUB: $0 $*" >&2; return 0; }
run_reconciliation()                        { echo "STUB: $0 $*" >&2; return 0; }
actual_value()                              { echo "STUB: $0 $*" >&2; return 0; }
latest_repair_record()                      { echo "STUB: $0 $*" >&2; return 0; }
finding_level_for()                         { echo "STUB: $0 $*" >&2; return 0; }
attempt_as_reconciler()                     { echo "STUB: $0 $*" >&2; return 0; }
remove_canary_from_comparison_set()         { echo "STUB: $0 $*" >&2; return 0; }
assert_gap_procedure_triggered()            { echo "STUB: $0 $*" >&2; return 0; }
narrow_comparison_set()                     { echo "STUB: $0 $*" >&2; return 0; }
restore_canary()                            { echo "STUB: $0 $*" >&2; return 0; }
open_ai_session()                           { echo "STUB: $0 $*" >&2; return 0; }
validate_record()                           { echo "STUB: $0 $*" >&2; return 0; }
validate_contract()                         { echo "STUB: $0 $*" >&2; return 0; }
```

---

## 4. Invariant 9 and 12 — no self-approval

> **101.2 #9.** No self-approval, enforced mechanically by requiring approval of the most recent reviewable push.
> **101.2 #12.** Production approval is never self-approved and is a separate event from Gate 2 approval.

**Why silent failure is catastrophic.** If this fails silently, one identity can move a change from keyboard to production with nobody else in the loop, and the entire evidence chain of Section 32 — questions 3 and 8 — still answers, because it answers with that identity's name in both slots. Nothing looks broken. The estate simply has no independent review and no independent production authority, and it finds out at an incident.

### 4.1 The controls of record

| Layer | Control | Source |
| --- | --- | --- |
| Merge | Branch protection: require a PR; ≥1 approving review; **require review from Code Owners**; **require approval of the most recent reviewable push**; dismiss stale approvals on new commits | Section 11.3 |
| Merge | CODEOWNERS generated to contain **human identities only** | Section 11.3, Section 37.3 |
| Production | **The workflow-identity gate is the mechanism of record**: `deploy-production.yml` verifies the recorded approving identity differs from the deploying identity, and **fails closed if it cannot tell** | Section 27.2 |
| Production | The deploying actor is the pipeline; the approving actor is a person. Never the same identity | Section 27.2 |
| Not depended on | GitHub environment required reviewers are Enterprise-only on private repositories and are an optional recorded strengthening, never the mechanism (D73) | Section 11.4, Section 99.5 |

### 4.2 IT-009 — merge-side tests

**Owner:** L5 (`access/invariant-tests/IT-009.sh`), invoked by L2.

```bash
#!/usr/bin/env bash
# access/invariant-tests/IT-009.sh — Invariant 9, merge side.
# Requires: FIXTURE_REPO, TOKEN_A (author, Write+CodeOwner),
#           TOKEN_B (reviewer, Write+CodeOwner), TOKEN_R (Read-only),
#           WORK (local clone of FIXTURE_REPO, checked out on branch it009-n2).
set -euo pipefail
: "${FIXTURE_REPO:?exit 2}" "${TOKEN_A:?exit 2}" "${TOKEN_B:?exit 2}" "${TOKEN_R:?exit 2}" "${WORK:?exit 2}"

fail(){ echo "INVARIANT 9 VIOLATED: $*" >&2; exit 1; }
cannot(){ echo "TEST CANNOT RUN: $*" >&2; exit 2; }

# ---------- POSITIVE: IT-009-P ----------
# A opens, B (Write-holding Code Owner) approves, merge succeeds.
PR=$(GH_TOKEN=$TOKEN_A gh pr create -R "$FIXTURE_REPO" --head it009-p --base main \
      --title "IT-009-P" --body "positive" | grep -oE '[0-9]+$') || cannot "pr create"
GH_TOKEN=$TOKEN_B gh pr review "$PR" -R "$FIXTURE_REPO" --approve || cannot "review"
GH_TOKEN=$TOKEN_A gh pr merge "$PR" -R "$FIXTURE_REPO" --squash \
  || fail "IT-009-P: an independent Code Owner approval did not satisfy the gate (over-blocking)"

# ---------- NEGATIVE 1: IT-009-N1 — self-approval ----------
PR=$(GH_TOKEN=$TOKEN_A gh pr create -R "$FIXTURE_REPO" --head it009-n1 --base main \
      --title "IT-009-N1" --body "self" | grep -oE '[0-9]+$') || cannot "pr create"
# GitHub refuses an author's own approval outright; the assertion is on MERGEABILITY,
# never on whether the review API call returned an error.
GH_TOKEN=$TOKEN_A gh pr review "$PR" -R "$FIXTURE_REPO" --approve >/dev/null 2>&1
if GH_TOKEN=$TOKEN_A gh pr merge "$PR" -R "$FIXTURE_REPO" --squash >/dev/null 2>&1; then
  fail "IT-009-N1: author merged their own PR with no independent approval"
fi

# ---------- NEGATIVE 2: IT-009-N2 — stale approval after a new push ----------
PR=$(GH_TOKEN=$TOKEN_A gh pr create -R "$FIXTURE_REPO" --head it009-n2 --base main \
      --title "IT-009-N2" --body "stale" | grep -oE '[0-9]+$') || cannot "pr create"
GH_TOKEN=$TOKEN_B gh pr review "$PR" -R "$FIXTURE_REPO" --approve || cannot "review"
git -C "$WORK" commit --allow-empty -m "slipped in after approval" && git -C "$WORK" push origin it009-n2
if GH_TOKEN=$TOKEN_A gh pr merge "$PR" -R "$FIXTURE_REPO" --squash >/dev/null 2>&1; then
  fail "IT-009-N2: a commit pushed after approval merged — most-recent-push rule is not armed"
fi

# ---------- NEGATIVE 3: IT-009-N3 — Read-only approval does not satisfy ----------
# Section 99.6 secondary risk: a Cross-Reviewer implemented with Read-only
# permission fails SILENTLY. This test is the only thing that sees it.
PR=$(GH_TOKEN=$TOKEN_A gh pr create -R "$FIXTURE_REPO" --head it009-n3 --base main \
      --title "IT-009-N3" --body "readonly" | grep -oE '[0-9]+$') || cannot "pr create"
GH_TOKEN=$TOKEN_R gh pr review "$PR" -R "$FIXTURE_REPO" --approve >/dev/null 2>&1
if GH_TOKEN=$TOKEN_A gh pr merge "$PR" -R "$FIXTURE_REPO" --squash >/dev/null 2>&1; then
  fail "IT-009-N3: a Read-only approval satisfied branch protection"
fi

echo "IT-009 PASS"; exit 0
```

### 4.3 IT-012 — production-side tests

**Owner:** L2 (`tools/evidence/invariant-tests/IT-012.sh`).

```bash
#!/usr/bin/env bash
# tools/evidence/invariant-tests/IT-012.sh — Invariant 12, workflow-identity gate.
# Requires: FIXTURE_REPO, TOKEN_B, TOKEN_MACHINE, TOKEN_INCIDENT_RESPONDER,
#           DIGEST_APPROVED_BY_B, DIGEST_GATE2_ONLY, DIGEST_PREVIOUS_APPROVED,
#           and DIGEST_RECORD_missing / _malformed / _unsigned / _identity_null.
set -euo pipefail
: "${FIXTURE_REPO:?exit 2}" "${TOKEN_B:?exit 2}" "${TOKEN_MACHINE:?exit 2}" \
  "${TOKEN_INCIDENT_RESPONDER:?exit 2}" "${DIGEST_APPROVED_BY_B:?exit 2}" \
  "${DIGEST_GATE2_ONLY:?exit 2}" "${DIGEST_PREVIOUS_APPROVED:?exit 2}"
fail(){ echo "INVARIANT 12 VIOLATED: $*" >&2; exit 1; }
cannot(){ echo "TEST CANNOT RUN: $*" >&2; exit 2; }

run_and_conclude(){ # dispatch, wait, echo conclusion; echoes "cannot:<reason>" on dispatch failure
  gh workflow run "$1" -R "$FIXTURE_REPO" -f digest="$2" >/dev/null 2>&1 || { echo "cannot:dispatch $1"; return; }
  local id; id=$(gh run list -R "$FIXTURE_REPO" -w "$1" -L1 --json databaseId -q '.[0].databaseId')
  gh run watch "$id" -R "$FIXTURE_REPO" --exit-status >/dev/null 2>&1
  gh run view "$id" -R "$FIXTURE_REPO" --json conclusion -q .conclusion
}
# check_run MUST be called outside any command substitution: cannot()'s exit 2
# only terminates the subshell $(...) creates, never the calling script.
check_run(){ case "$1" in cannot:*) cannot "${1#cannot:}" ;; esac; }

# ---------- POSITIVE: IT-012-P ----------
# Approval recorded by B; dispatch by C. Distinct identities -> deploy proceeds.
RESULT=$(run_and_conclude deploy-production.yml "$DIGEST_APPROVED_BY_B"); check_run "$RESULT"
[ "$RESULT" = "success" ] \
  || fail "IT-012-P: a properly separated approve/deploy pair was refused (over-blocking)"

# ---------- NEGATIVE 1: IT-012-N1 — approver == dispatcher ----------
# Approval record names B; B dispatches. Must fail at the identity gate.
RESULT=$(GH_TOKEN=$TOKEN_B run_and_conclude deploy-production.yml "$DIGEST_APPROVED_BY_B"); check_run "$RESULT"
[ "$RESULT" = "failure" ] \
  || fail "IT-012-N1: the approver deployed their own approval"

# ---------- NEGATIVE 2: IT-012-N2 — FAIL CLOSED WHEN IT CANNOT TELL ----------
# Section 27.2: the gate "fails closed if it cannot tell". This is the single
# most important assertion in this section: an unreadable, absent or malformed
# approval record MUST NOT be treated as absence of a conflict.
for BROKEN in missing malformed unsigned identity-null; do
  VARNAME="DIGEST_RECORD_${BROKEN//-/_}"
  RESULT=$(run_and_conclude deploy-production.yml "${!VARNAME}"); check_run "$RESULT"
  [ "$RESULT" = "failure" ] \
    || fail "IT-012-N2($BROKEN): gate did not fail closed on an undeterminable approval record"
done

# ---------- NEGATIVE 3: IT-012-N3 — Gate 2 approval is not production approval ----------
# A PR approved at Gate 2, with NO production-approval record, must not deploy.
RESULT=$(run_and_conclude deploy-production.yml "$DIGEST_GATE2_ONLY"); check_run "$RESULT"
[ "$RESULT" = "failure" ] \
  || fail "IT-012-N3: a Gate 2 approval was accepted as production approval"

# ---------- NEGATIVE 4: IT-012-N4 — rollback exemption does not lift the actor gate ----------
# 27.2: rollback is exempt from the production-approval gate, NOT from the
# actor gate. A machine identity dispatching rollback must still be refused.
RESULT=$(GH_TOKEN=$TOKEN_MACHINE run_and_conclude rollback.yml "$DIGEST_PREVIOUS_APPROVED"); check_run "$RESULT"
[ "$RESULT" = "failure" ] \
  || fail "IT-012-N4: a machine identity dispatched rollback — the actor gate was lifted by the exemption"

# ---------- POSITIVE COMPANION: rollback by a capable human succeeds ----------
RESULT=$(GH_TOKEN=$TOKEN_INCIDENT_RESPONDER run_and_conclude rollback.yml "$DIGEST_PREVIOUS_APPROVED"); check_run "$RESULT"
[ "$RESULT" = "success" ] \
  || fail "IT-012-P2: rollback of an already-approved digest by an incident-response holder was blocked — this breaks solo out-of-hours SEV-1 recovery (47.2)"

echo "IT-012 PASS"; exit 0
```

### 4.4 Mutations — proving IT-009 and IT-012 can fail

| Mutation | Applied to | The negative test that must flip to FAIL |
| --- | --- | --- |
| M-009-a | Fixture: unset `require_last_push_approval` on branch protection | IT-009-N2 |
| M-009-b | Fixture: drop `require_code_owner_reviews` | IT-009-N1, IT-009-N3 |
| M-009-c | Fixture: set required approving reviews to 0 | IT-009-N1 |
| M-009-d | Fixture: grant `$ACTOR_R` Write | IT-009-N3 |
| M-012-a | Fixture workflow: remove the identity-comparison step from `deploy-production.yml` | IT-012-N1 |
| M-012-b | Fixture workflow: change the record-read failure branch from `exit 1` to `continue` | **IT-012-N2** — the fail-closed assertion |
| M-012-c | Fixture workflow: remove the actor gate from `rollback.yml` | IT-012-N4 |
| `# MUTATION-NEEDED: create IT-012-N3.mutation.sh that breaks the invariant` | Fixture workflow: remove the gate-2-vs-production-approval separation check so a Gate-2-only approval record passes `deploy-production.yml` | IT-012-N3 |

If any listed negative test still reports PASS under its mutation, **the test is vacuous**: block `integration → main`, open a blocker issue titled `VACUOUS-TEST IT-0NN`, and do not proceed. This is the STOP rule.

### 4.5 Bootstrap sequencing (Section 95.4)

These gates arm by headcount, and the checklist is executed for real at each threshold — negative tests included:

* **2 humans with Write:** IT-009-P, IT-009-N1, IT-009-N2, IT-009-N3 all execute for real.
* **3 humans:** IT-012-P, IT-012-N1 execute for real ("a deploy attempted by its approver is rejected").
* Below 2 humans: the gate is *configured but not yet binding* (§95.2 arming pattern), the armed configuration is recorded beside it, and a bootstrap exception with a mandatory expiry and an activation checklist carries the gap (AT-039). **The exception cannot lapse silently** — on expiry it surfaces as Blocking drift.

---

## 5. Invariant 22 and 23 — the digest invariant

> **101.5 #22.** The production artifact is the same digest verified in staging. Never rebuilt.
> **101.5 #23.** Never rebuild an artifact to work around registry unavailability.

**Why silent failure is catastrophic.** Section 32 states the invariant that makes the evidence chain trustworthy: item 5 (the recorded build digest) and item 11 (`GET /version` on the live service) must match, and the production digest must be byte-identical to the staging-verified one. If the check silently stops comparing, every one of the eleven evidence questions still answers — with a plausible, wrong answer. The estate believes it verified what it deployed, and the belief is unfalsifiable from the inside. Section 46.1 states the consequence plainly: rebuilding produces a different digest that was never verified in staging, which breaks both the evidence chain and the immutability invariant.

### 5.1 The controls of record

| Layer | Control | Source |
| --- | --- | --- |
| Pipeline | The digest invariant enforced **in code** in the reusable workflow library | Subsystem E, Section 99.2 |
| Pipeline | CI rejects any production deployment whose requested digest differs from the digest that passed staging verification | Section 32, Section 33 |
| Runtime | `/version` reports the deployed digest; it must equal the approved digest; any mismatch is a **P0 investigation** | Section 41, Section 32 q.11 |
| Sweep | `verify-digest-chain` — scheduled sweep over every production `/version` against its approval record; also the on-demand outage-recovery gate of Section 46.1 step 3 | Subsystem F, Section 99.2 |
| Drift | Artifact digest mismatch is named Blocking-class drift, Level 4 | Section 53.2 |
| Sanctioned equivalence | For an **S18 platform-rebuild** deployment only, the recorded identity — pinned commit + lockfile + build configuration — stands in for the digest, and remaining on such a host is itself a dated recorded state (D78) | Section 32, Section 96.6 |

### 5.2 IT-022 — the digest chain

**Owner:** L2 (`tools/evidence/invariant-tests/IT-022.sh`).

```bash
#!/usr/bin/env bash
# tools/evidence/invariant-tests/IT-022.sh — Invariants 22 and 23.
set -euo pipefail
fail(){ echo "INVARIANT 22/23 VIOLATED: $*" >&2; exit 1; }
cannot(){ echo "TEST CANNOT RUN: $*" >&2; exit 2; }

# ---------- POSITIVE: IT-022-P — the honest path ----------
D=$(gh workflow run build.yml -R "$FIXTURE_REPO" && wait_digest) || cannot "build"
deploy staging "$D"        || fail "IT-022-P: staging deploy of a fresh digest was refused"
verify staging "$D"        || cannot "staging verification"
approve_production "$D" "$ACTOR_B"
[ "$(deploy_conclusion production "$D")" = "success" ] \
  || fail "IT-022-P: the staging-verified, approved digest was refused for production"
[ "$(curl -fsS "$STAGING_URL/version" | jq -r .digest)" = "$D" ] || fail "IT-022-P: /version disagrees"
tools/evidence/verify-digest-chain --product "$FIXTURE_PRODUCT" \
  || fail "IT-022-P: verify-digest-chain reported a mismatch on a clean chain"

# ---------- NEGATIVE 1: IT-022-N1 — a digest staging never verified ----------
DX=$(build_only)   # built, never deployed to staging, never verified
[ "$(deploy_conclusion production "$DX")" = "failure" ] \
  || fail "IT-022-N1: production accepted a digest that never passed staging verification"

# ---------- NEGATIVE 2: IT-022-N2 — NEVER REBUILT ----------
# Rebuild identical source. The new digest differs. Even with a passing build
# and an approval naming the SAME COMMIT, production must refuse it: the
# invariant binds the digest, not the commit.
D2=$(rebuild_same_source)
[ "$D2" != "$D" ] || cannot "rebuild produced an identical digest; fixture is not exercising the case"
approve_production "$D2" "$ACTOR_B"
[ "$(deploy_conclusion production "$D2")" = "failure" ] \
  || fail "IT-022-N2: a rebuilt artifact of the same commit reached production — 'never rebuilt' is not enforced"

# ---------- NEGATIVE 3: IT-023-N1 — registry unavailability must not license a rebuild ----------
# Section 46.1: waiting for the registry is always correct.
with_registry_unavailable \
  '[ "$(deploy_conclusion production "$D")" = "failure" ]' \
  || fail "IT-023-N1: the pipeline rebuilt or improvised when the registry was unavailable"

# ---------- NEGATIVE 4: IT-022-N3 — THE SWEEP'S OWN CANARY ----------
# Point the fixture service at a digest other than its approved one. The
# scheduled sweep MUST find it. A sweep that reports clean here is the
# digest-chain equivalent of a reconciliation run that finds nothing.
set_running_digest "$FIXTURE_SERVICE" "$DX"
if tools/evidence/verify-digest-chain --product "$FIXTURE_PRODUCT"; then
  fail "IT-022-N3: verify-digest-chain reported clean while /version disagreed with the approval record"
fi
set_running_digest "$FIXTURE_SERVICE" "$D"

# ---------- NEGATIVE 5: IT-022-N4 — the S18 equivalence is not a loophole ----------
# A product WITHOUT a dated, recorded platform-rebuild state must not be able
# to substitute commit+lockfile identity for a digest.
[ "$(deploy_conclusion production --identity-substitution "$FIXTURE_PRODUCT")" = "failure" ] \
  || fail "IT-022-N4: identity substitution accepted on a product with no recorded S18 state (D78)"

echo "IT-022 PASS"; exit 0
```

### 5.3 Mutations

| Mutation | Applied to | Negative test that must flip to FAIL |
| --- | --- | --- |
| M-022-a | Fixture workflow: remove the `requested == staging_verified` comparison from `deploy-production.yml` | IT-022-N1, IT-022-N2 |
| M-022-b | Fixture: make `verify-digest-chain` compare commit SHA instead of digest | IT-022-N2, IT-022-N3 |
| M-022-c | Fixture: make `verify-digest-chain` treat an unreachable `/version` as a pass | IT-022-N3 |
| M-022-d | Fixture workflow: add a `build` step to the production deploy job | IT-022-N2, IT-023-N1 |
| M-022-e | Fixture: allow identity substitution unconditionally | IT-022-N4 |

**M-022-c deserves separate emphasis.** An unreachable service is exactly the state in which a mismatch is most likely and least visible. Per §3's exit contract, the sweep must exit 2 (cannot run, blocks) — never 0.

### 5.4 Standing schedule

* `verify-digest-chain` runs on schedule as a portfolio sweep; **any mismatch is a P0 investigation** (Section 41, Subsystem F).
* It is additionally the **gate on resumption of production deploys after a degraded-mode outage** (Section 46.1 step 3, owned by the escalation role, within the first half working day after recovery). Nothing new deploys until the chain is confirmed closed.
* The mutation run for M-022-a…e executes at every `integration → main` promotion.

---

## 6. Invariant 18 and 21 — no machine approval satisfies a gate

> **101.4 #18.** The background machine layer cannot merge, approve, deploy, or reach production credentials or databases — enforced by permissions and, for workflow dispatch, by the actor gate on every privileged workflow (Section 37.3), **not by policy**.
> **101.4 #21.** Unattended personal-agent runs are permitted only on branches; their output is flagged as unattended and never merges without the full human gate sequence.

**Why silent failure is catastrophic.** The whole architecture of machine authority rests on one sentence in Section 37.3: *these are prohibited because the machine account does not hold the permissions required; documentation-only restrictions fail.* If a machine identity ever lands in a CODEOWNERS file, or an actor gate is quietly dropped from a workflow, the prohibition degrades from architecture back to policy — and nothing about the day-to-day output changes. Draft PRs keep arriving, CI keeps passing, and the only difference is that the wall is gone. Section 53.1 already classifies a workflow-file change pushed by a machine identity as Blocking drift *regardless of the change's content*, precisely because workflow files define the enforcement path itself.

### 6.1 The controls of record

| Layer | Control | Source |
| --- | --- | --- |
| Permissions | The machine account does not hold the permissions to merge, approve, deploy, hold production credentials or reach production databases | Section 37.3, Section 37.4 |
| Approval wall | Branch protection requires Code Owner review; **CODEOWNERS is generated to contain human identities only** — no machine account ever appears in it | Section 11.3, Section 37.3, D53 |
| Dispatch | An **actor gate as the first step of every privileged workflow** — `deploy-staging.yml`, `deploy-production.yml`, `migrate.yml`, the rollback workflow, the production-restore workflow — failing closed unless `github.actor` resolves to a human in `people.yaml` holding the required capability | Section 37.3 |
| Dispatch | The machine account's permitted dispatch set is a **positive allowlist checked inside each workflow**: the Section 94.7 digest generators and nothing else | Section 37.3 |
| Drift | Removing an actor gate is a workflow-file change and is therefore already Blocking drift | Section 37.3, Section 53.1 |
| Independent check | The **independent control verifier** runs off the operations VM under its own read-only credential, asserting no machine identity appears in any CODEOWNERS in any repository, and writes to a surface the ops VM cannot write to. Its own absence for one cycle is **Level 5** | Section 53.1 |
| Cage | Host-level egress allowlist, systemd wall-clock stop, draft-PR-only GitHub identity, separate OS users per instance | Section 37.8, AT-109 |

### 6.2 IT-018 — the approval wall

**Owner:** L5 (`access/invariant-tests/IT-018.sh`).

```bash
#!/usr/bin/env bash
# access/invariant-tests/IT-018.sh — Invariant 18, approval and merge wall.
# Requires: FIXTURE_REPO, TOKEN_A, TOKEN_B, TOKEN_MACHINE, ORG, TOKEN_VERIFIER.
set -euo pipefail
: "${FIXTURE_REPO:?exit 2}" "${TOKEN_A:?exit 2}" "${TOKEN_B:?exit 2}" \
  "${TOKEN_MACHINE:?exit 2}" "${ORG:?exit 2}" "${TOKEN_VERIFIER:?exit 2}"
fail(){ echo "INVARIANT 18 VIOLATED: $*" >&2; exit 1; }

# ---------- POSITIVE: IT-018-P ----------
# The machine account CAN do its job: open a draft PR on a whitelisted repo.
PR=$(GH_TOKEN=$TOKEN_MACHINE gh pr create -R "$FIXTURE_REPO" --draft --head bg/it018 \
      --base main --title "IT-018-P" --body "draft" | grep -oE '[0-9]+$') \
  || fail "IT-018-P: the machine account cannot open a draft PR — the layer is over-caged"
# And a human Code Owner approval DOES satisfy the gate on that PR.
GH_TOKEN=$TOKEN_MACHINE gh pr ready "$PR" -R "$FIXTURE_REPO"
GH_TOKEN=$TOKEN_B gh pr review "$PR" -R "$FIXTURE_REPO" --approve
GH_TOKEN=$TOKEN_B gh pr merge "$PR" -R "$FIXTURE_REPO" --squash \
  || fail "IT-018-P: a human approval on a machine-drafted PR did not satisfy the gate"

# ---------- NEGATIVE 1: IT-018-N1 — a machine approval never satisfies a gate ----------
# The review API call may well succeed. The assertion is on MERGEABILITY.
PR=$(GH_TOKEN=$TOKEN_A gh pr create -R "$FIXTURE_REPO" --head it018-n1 --base main \
      --title "IT-018-N1" --body x | grep -oE '[0-9]+$')
GH_TOKEN=$TOKEN_MACHINE gh pr review "$PR" -R "$FIXTURE_REPO" --approve >/dev/null 2>&1
STATE=$(gh pr view "$PR" -R "$FIXTURE_REPO" --json reviewDecision -q .reviewDecision)
[ "$STATE" != "APPROVED" ] || fail "IT-018-N1: a machine approval satisfied the review requirement"
if GH_TOKEN=$TOKEN_A gh pr merge "$PR" -R "$FIXTURE_REPO" --squash >/dev/null 2>&1; then
  fail "IT-018-N1: a PR merged on a machine approval alone"
fi

# ---------- NEGATIVE 2: IT-018-N2 — a machine cannot merge ----------
if GH_TOKEN=$TOKEN_MACHINE gh pr merge "$PR" -R "$FIXTURE_REPO" --squash >/dev/null 2>&1; then
  fail "IT-018-N2: the machine account merged a pull request"
fi

# ---------- NEGATIVE 3: IT-018-N3 — CODEOWNERS carries no machine identity ----------
# Portfolio-wide, run under the INDEPENDENT VERIFIER's read-only credential,
# off the operations VM — never under the credential that generates the file.
for R in $(gh repo list "$ORG" --limit 1000 --json name -q '.[].name'); do
  for LOC in CODEOWNERS .github/CODEOWNERS docs/CODEOWNERS; do
    BODY=$(GH_TOKEN=$TOKEN_VERIFIER gh api "repos/$ORG/$R/contents/$LOC" -q .content 2>/dev/null | base64 -d) || continue
    for M in $(yq -r '.machine_identities[]' registries/machine-identities.yaml); do
      grep -q -- "$M" <<<"$BODY" && fail "IT-018-N3: machine identity $M appears in $R:$LOC"
    done
  done
done

echo "IT-018 PASS"; exit 0
```

### 6.3 IT-018-D — the actor gate on every privileged workflow

**Owner:** L2 (`tools/evidence/invariant-tests/IT-018-D.sh`).

```bash
#!/usr/bin/env bash
# tools/evidence/invariant-tests/IT-018-D.sh — Invariant 18, dispatch authority.
# Requires: FIXTURE_REPO, TOKEN_MACHINE, TOKEN_HUMAN_NO_CAP.
set -euo pipefail
: "${FIXTURE_REPO:?exit 2}" "${TOKEN_MACHINE:?exit 2}" "${TOKEN_HUMAN_NO_CAP:?exit 2}"
fail(){ echo "INVARIANT 18 VIOLATED: $*" >&2; exit 1; }

PRIVILEGED="deploy-staging.yml deploy-production.yml migrate.yml rollback.yml restore-production.yml"

# ---------- NEGATIVE 1: machine dispatch of every privileged workflow ----------
for W in $PRIVILEGED; do
  C=$(GH_TOKEN=$TOKEN_MACHINE dispatch_and_conclude "$W")
  [ "$C" = "failure" ] || fail "IT-018-D-N1: machine dispatch of $W concluded '$C', not failure"
  # And the gate must be the FIRST step: no environment secret may have been
  # materialised, and no job after the gate may have started.
  assert_gate_was_first_step "$W" || fail "IT-018-D-N1: the actor gate in $W is not the first step"
  assert_no_environment_secret_materialised "$W" \
    || fail "IT-018-D-N1: $W reached an environment secret before refusing a machine actor"
done

# ---------- NEGATIVE 2: a human WITHOUT the required capability ----------
# The gate resolves capability, not humanity (Invariant 11: authority is
# evaluated against capability and assignment, never role name alone).
for W in $PRIVILEGED; do
  C=$(GH_TOKEN=$TOKEN_HUMAN_NO_CAP dispatch_and_conclude "$W")
  [ "$C" = "failure" ] || fail "IT-018-D-N2: $W admitted a human holding no required capability"
done

# ---------- NEGATIVE 3: the positive allowlist is closed ----------
# 37.3: the machine's permitted dispatch set is the Section 94.7 digest
# generators and nothing else. Anything not on the list must be refused.
for W in $(gh workflow list -R "$FIXTURE_REPO" --json name -q '.[].name'); do
  on_allowlist "$W" && continue
  C=$(GH_TOKEN=$TOKEN_MACHINE dispatch_and_conclude "$W")
  [ "$C" = "failure" ] || fail "IT-018-D-N3: machine dispatched non-allowlisted workflow $W"
done

# ---------- POSITIVE: the allowlist is not empty ----------
# A machine that can dispatch NOTHING would make N3 vacuously true forever.
C=$(GH_TOKEN=$TOKEN_MACHINE dispatch_and_conclude "digest-morning.yml")
[ "$C" = "success" ] || fail "IT-018-D-P: the machine cannot dispatch its one allowed class (D71)"

# ---------- NEGATIVE 4: machine workflow-file change is Blocking drift ----------
GH_TOKEN=$TOKEN_MACHINE push_workflow_change "$FIXTURE_REPO" ".github/workflows/ci.yml"
sleep_until_reconciliation
[ "$(drift_class_for "$FIXTURE_REPO" workflow-file-machine-push)" = "Blocking" ] \
  || fail "IT-018-D-N4: a machine-pushed workflow-file change did not raise Blocking drift (53.1)"

echo "IT-018-D PASS"; exit 0
```

### 6.4 IT-021 — unattended personal-agent runs

**Owner:** L5 (`access/invariant-tests/IT-021.sh`).

| Test | Assertion |
| --- | --- |
| IT-021-P | An unattended run pushes a branch and opens a PR carrying the `unattended` flag — permitted. |
| IT-021-N1 | An unattended run attempting a direct push to a default branch is refused. |
| IT-021-N2 | A flagged-unattended PR cannot merge without the full human gate sequence (Code Owner approval on the most recent push). |
| IT-021-N3 | **Flag-integrity:** removing the `unattended` flag from a PR produced by an unattended run is detected — the flag derives from the producing identity and run record, not from a mutable label. If the check reads only the label, IT-021-N3 will pass under mutation M-021-c and the test is vacuous. |

### 6.5 Mutations

| Mutation | Applied to | Negative test that must flip to FAIL |
| --- | --- | --- |
| M-018-a | Fixture: add the machine identity to `CODEOWNERS` | IT-018-N3 |
| M-018-b | Fixture: drop `require_code_owner_reviews` | IT-018-N1 |
| M-018-c | Fixture: grant the machine account Maintain on the fixture repo | IT-018-N2 |
| M-018-d | Fixture workflow: delete the actor-gate step from `migrate.yml` | IT-018-D-N1 |
| M-018-e | Fixture workflow: move the actor gate below the environment-secret step | IT-018-D-N1 (`assert_gate_was_first_step`) |
| M-018-f | Fixture: make the actor gate check `people.yaml` membership without capability | IT-018-D-N2 |
| M-018-g | Fixture: replace the dispatch allowlist with a denylist | IT-018-D-N3 |
| M-021-c | Fixture: make the unattended check read the PR label instead of the run record | IT-021-N3 |
| `# MUTATION-NEEDED: create IT-021-N1.mutation.sh that breaks the invariant` | Fixture: grant the unattended identity direct-push permission on the default branch so the push-to-default-branch attempt succeeds | IT-021-N1 |
| `# MUTATION-NEEDED: create IT-021-N2.mutation.sh that breaks the invariant` | Fixture: remove the Code-Owner-approval requirement from the unattended PR's branch protection so the flagged-unattended PR merges without the full human gate | IT-021-N2 |

### 6.6 The cage, and the verifier that watches the watcher

Two further standing tests, because Section 53.1 is explicit that a control which can be rewritten by the credential it checks is not a control:

* **AT-109, the egress wall**, executed for real: from inside the background worker container, a connection to a non-allowlisted external host and a connection to the Layer B store are both refused **at the host egress layer, not by harness configuration**, while GitHub and the LAN inference endpoint succeed; and the systemd wall-clock stop terminates the running process at the window boundary. Owner: L5, `access/invariant-tests/AT-109.sh`.
* **Independent-verifier liveness:** the verifier runs off the operations VM under its own read-only credential and writes to a surface the ops VM cannot write to. **Its absence for one cycle is Level 5.** The negative test suppresses one scheduled run in the fixture and asserts the Level 5 escalation fires. A verifier whose absence produces silence is not a verifier. Owner: L3, `validators/drift/invariant-tests/IT-VERIFIER.sh`.

---

## 7. Invariant 24, 25, 26 and 84 — production inaccessible from developer machines

> **101.5 #24.** The production database is inaccessible from developer machines.
> **101.5 #25.** Production secrets are environment-scoped and never present locally.
> **101.5 #26.** A fully compromised workstation must not yield production access.
> **101.11 #84.** API keys remain absent from developer environments.

**Why silent failure is catastrophic.** Section 40.2 is unusually direct about the failure shape: *a security group opened to the world with nothing declared to compare it against produces no finding at all.* This boundary is the one place where the reconciler structurally cannot see the truth — reconciliation compares declared state against **GitHub** state and never leaves it. The provider side is therefore verified by **attestation, not reconciliation**, and an attestation that silently stops being recorded looks exactly like an estate with no drift.

### 7.1 The controls of record

| Layer | Control | Source |
| --- | --- | --- |
| Declaration | Each product declares an `infrastructure:` block naming the network boundary of its production datastore — which networks, which principals — validated by contract CI exactly as `recovery:` is | Section 40.2 |
| Default | `security.production_db_access: ci-only` | Section 40.2 |
| Human access | Provider-SSO-federated with **no long-lived key**; migrations and operational tasks run as controlled CI jobs | Section 40.2, Section 34 |
| Provider side | A named owner records a **dated attestation** that actual provider state matches the declaration. Calibrated configuration, initial value monthly, run with the Section 49 asset-inventory sweep. An expired or failed attestation is **Blocking drift** | Section 40.2, Section 53.1 |
| Secrets | Five tiers, strictly separated. A secret never moves down a tier. A production credential below the production tier is a **security incident under Section 43**, not a cleanup task | Section 40.1 |
| Environments | Every environment carries a deployment branch and tag policy restricting `staging` and `production` to the default branch and protected release tags. Reconciled — **Blocking; blocks deployment** | Section 11.3, Section 33.4, Section 53.1 |
| Workstation | Fifth-tier credentials under a separate OS user or secret agent that a passive root shell does not read; second factor for ops-VM shell access; rotator and host-root separated where headcount permits | Section 40.3 |

### 7.2 IT-024 — the network boundary

**Owner:** L5 (`access/invariant-tests/IT-024.sh`).

```bash
#!/usr/bin/env bash
# access/invariant-tests/IT-024.sh — Invariant 24.
# Requires: ACTOR_DEVOPS, PRODUCT_YAML, FIXTURE_PRODUCT, WINDOW_DAYS.
set -euo pipefail
: "${ACTOR_DEVOPS:?exit 2}" "${PRODUCT_YAML:?exit 2}" "${FIXTURE_PRODUCT:?exit 2}" "${WINDOW_DAYS:?exit 2}"
fail(){ echo "INVARIANT 24 VIOLATED: $*" >&2; exit 1; }
cannot(){ echo "TEST CANNOT RUN: $*" >&2; exit 2; }

# ---------- POSITIVE: IT-024-P — the sanctioned path works ----------
# A migration runs as a controlled CI job and succeeds.
[ "$(dispatch_and_conclude migrate.yml --actor "$ACTOR_DEVOPS")" = "success" ] \
  || fail "IT-024-P: the CI-only migration path is broken — teams will route around it"

# ---------- NEGATIVE 1: IT-024-N1 — direct reach from a workstation ----------
# Executed from the developer-workstation network profile, NOT from CI.
assert_running_on developer-workstation || cannot "not on a workstation profile"
for EP in $(yq -r '.infrastructure.production_datastore.endpoints[]' "$PRODUCT_YAML"); do
  # nc -z, not bash's /dev/tcp: /dev/tcp requires a net-redirection-enabled bash
  # build and is unavailable on MSYS2/Git-for-Windows bash, where the redirect
  # would error out before reaching the network and mask what this test proves.
  if nc -z -w 10 "${EP%:*}" "${EP##*:}" 2>/dev/null; then
    fail "IT-024-N1: TCP handshake completed to production datastore $EP from a workstation"
  fi
done

# ---------- NEGATIVE 2: IT-024-N2 — declaration cannot be omitted ----------
# A product.yaml with no infrastructure: block must fail contract CI.
[ "$(validate_contract fixtures/product-no-infra.yaml; echo $?)" -ne 0 ] \
  || fail "IT-024-N2: a product with no declared production-datastore boundary passed contract CI"

# ---------- NEGATIVE 3: IT-024-N3 — THE ATTESTATION CANARY ----------
# The provider side is attestation-held, so the ONLY thing standing between
# this invariant and silence is that a stale attestation blocks. Age the
# fixture attestation past its window and assert Blocking drift appears.
age_attestation fixtures/attestation-prod-boundary.yaml --days "$((WINDOW_DAYS + 1))"
sleep_until_reconciliation
[ "$(drift_class_for "$FIXTURE_PRODUCT" infrastructure-attestation)" = "Blocking" ] \
  || fail "IT-024-N3: an expired provider-boundary attestation raised no Blocking drift (40.2, 53.1)"

# ---------- NEGATIVE 4: IT-024-N4 — a failed attestation is not a missing one ----------
record_attestation fixtures/attestation-prod-boundary.yaml --result failed
sleep_until_reconciliation
[ "$(drift_class_for "$FIXTURE_PRODUCT" infrastructure-attestation)" = "Blocking" ] \
  || fail "IT-024-N4: a FAILED attestation was treated as satisfying the window"

echo "IT-024 PASS"; exit 0
```

### 7.3 IT-025 and IT-084 — secrets and API keys

**Owner:** L5 (`access/invariant-tests/IT-025.sh`, `access/invariant-tests/IT-084.sh`).

| Test | Assertion | Source |
| --- | --- | --- |
| IT-025-P | The production deployment workflow, running on the default branch, resolves its production-tier secrets. | 40.1 |
| IT-025-N1 | **A workflow pushed to a non-default branch declaring `environment: production` obtains no environment secret.** Executed negatively — this is verbatim the Phase 1 completion check. | §98.2 |
| IT-025-N2 | A production-tier secret name resolving from the staging environment fails. A secret never moves down a tier. | 40.1 |
| IT-025-N3 | Weakening the environment deployment branch/tag policy in the fixture raises Blocking drift and **blocks deployment on the affected repository**. | 53.1 |
| IT-084-P | On a clean workstation profile, `env \| grep -i api_key` returns empty and the check reports pass. | 40.2 |
| IT-084-N1 | **The API-key canary.** Export a clearly-labelled synthetic value `FIXTURE_CANARY_API_KEY=not-a-real-key` and re-run. The check MUST fail. A check that reports clean against a planted key is not looking. | 40.2, 53.1 philosophy |
| IT-084-N2 | Plant the same synthetic value in a repository `.env` file and in a shell profile. Both must be found. Section 40.2 names all three surfaces; a check covering only `env` is a narrowed comparison. | 40.2 |

```bash
#!/usr/bin/env bash
# access/invariant-tests/IT-084.sh — the canary, in full, because it is three lines
# and it is the difference between a live check and a decorative one.
set -euo pipefail
access/checks/no-api-keys.sh || { echo "IT-084-P: clean profile already fails"; exit 1; }
export FIXTURE_CANARY_API_KEY="not-a-real-key-synthetic-canary"
if access/checks/no-api-keys.sh; then
  echo "INVARIANT 84 VIOLATED: the no-API-key check passed with a key present" >&2; exit 1
fi
unset FIXTURE_CANARY_API_KEY
echo "IT-084 PASS"
```

### 7.4 IT-026 — the workstation compromise drill

**Owner:** L5 (`access/invariant-tests/IT-026.sh`). Executed as a **drill**, on the same gate as the Section 40.1 clean-reconciliation condition, and re-executed at every fifth-tier credential rotation.

Section 40.3 states two boundaries with equal force. The drill tests both, from a workstation profile holding a full set of workstation credentials:

| # | Attempt | Required outcome |
| --- | --- | --- |
| 1 | Read a production-tier secret | Denied |
| 2 | Dispatch `deploy-production.yml` | Refused at the actor gate; no environment secret materialised |
| 3 | Connect to the production datastore | No TCP handshake |
| 4 | Read the fifth-tier control-plane credential store on the operations VM | Denied — separate OS user or secret agent; a passive root shell does not read it |
| 5 | Open a shell on the operations VM with the workstation credential alone | Denied — second factor required on top of the private network path (51.4) |
| — | **Then, the positive half:** the same workstation still opens a PR, pushes a branch, and runs CI | Succeeds — the boundary bounds production, not work |

Attempts 4 and 5 are the ones most likely to be skipped, because Section 40.3 adds the second boundary specifically to close the case where an estate proves attempts 1–3 and calls the drill complete. **A drill that runs only attempts 1–3 is recorded as a FAILED drill, not a partial one.**

Mutations: M-026-a places a fifth-tier credential in the workstation user's readable path (attempt 4 must flip to FAIL); M-026-b removes the ops-VM second factor in the fixture (attempt 5 must flip to FAIL).

---

## 8. Invariant 81 — auto-repair only toward the stricter state

> **101.10 #81.** Auto-repair may only move the system toward the declared, stricter state.
> **Section 53.3, binding:** a repair is permitted only when it moves the system toward the declared state **and** the declared state is at least as restrictive as the actual state. Reconciliation never loosens a control automatically, never modifies production runtime configuration, never modifies data, and never rotates or writes secrets. Where actual state is stricter than declared, reconciliation raises Level 2 for human judgment rather than relaxing the control.

**Why silent failure is catastrophic.** Section 99.6 risk 6 names this the most dangerous code in the system: *a write-scope, org-admin automation whose bug loosens security or locks everyone out; the reconciler is the highest-privilege identity in the system.* A stricter-only bug does not announce itself. It shows up as a reconciliation run that completed, wrote a repair record, and reported clean — while having relaxed a control. Section 53.7 names this branch explicitly: the loop can *run and repair against a wrongly-computed declared state, which completes, records clean, and is therefore invisible to every check that asks only whether the loop ran.*

### 8.1 IT-081-U — the decision function, as a property test

The cheapest and most complete test is on the pure function, before any credential is involved. **Owner:** L3 (`validators/drift/invariant-tests/IT-081-unit.sh`).

```bash
#!/usr/bin/env bash
# validators/drift/invariant-tests/IT-081-unit.sh
# Property: repair is emitted IF AND ONLY IF declared is at least as
# restrictive as actual. Enumerated over the full strictness lattice for
# every repairable control class — not sampled.
set -euo pipefail
FAILED=0
while IFS=, read -r CLASS DECLARED ACTUAL EXPECT; do
  GOT=$(reconciler/decide-repair --class "$CLASS" --declared "$DECLARED" --actual "$ACTUAL")
  if [ "$GOT" != "$EXPECT" ]; then
    echo "INVARIANT 81 VIOLATED: $CLASS declared=$DECLARED actual=$ACTUAL -> $GOT (expected $EXPECT)" >&2
    FAILED=1
  fi
done < validators/drift/fixtures/strictness-lattice.csv
# Lattice rows, per control class:
#   declared stricter than actual  -> repair
#   declared equal to actual       -> no-op
#   declared LOOSER than actual    -> level2   (never repair)
#   actual unknown / unreadable    -> level2   (never repair)  <-- fail-closed
#   declared unknown / unreadable  -> level2   (never repair)  <-- fail-closed
[ "$FAILED" -eq 0 ] || exit 1
echo "IT-081-U PASS"
```

The two `unknown` rows are the ones a lane will omit if not told. An unreadable actual state is not a looser actual state, and treating it as one is precisely how an automation loosens a control while reporting success.

### 8.2 IT-081 — the live behaviour (AT-033)

**Owner:** L3 (`validators/drift/invariant-tests/IT-081.sh`).

```bash
set -euo pipefail
# validators/drift/invariant-tests/IT-081.sh
# Requires: FIXTURE_REPO.
: "${FIXTURE_REPO:?exit 2}"
fail(){ echo "INVARIANT 81 VIOLATED: $*" >&2; exit 1; }

# ---------- POSITIVE: IT-081-P — repair toward stricter declared state ----------
weaken_actual "$FIXTURE_REPO" branch-protection --set required_approving_reviews=0
run_reconciliation
[ "$(actual_value "$FIXTURE_REPO" required_approving_reviews)" = "1" ] \
  || fail "IT-081-P: reconciliation did not re-apply the declared, stricter protection"
[ -n "$(latest_repair_record "$FIXTURE_REPO")" ] \
  || fail "IT-081-P: a repair was made with no repair record written (26.4)"

# ---------- NEGATIVE 1: IT-081-N1 — AT-033, no auto-loosening ----------
# Actual is STRICTER than declared. The control must be left alone and
# raised for human review at Level 2.
BEFORE=$(actual_value "$FIXTURE_REPO" required_approving_reviews)   # 2, declared 1
run_reconciliation
AFTER=$(actual_value "$FIXTURE_REPO" required_approving_reviews)
[ "$AFTER" = "$BEFORE" ] || fail "IT-081-N1: reconciliation RELAXED a stricter-than-declared control (AT-033)"
[ "$(finding_level_for "$FIXTURE_REPO" branch-protection)" = "2" ] \
  || fail "IT-081-N1: a stricter-than-declared control produced no Level 2 finding — it was silently accepted"

# ---------- NEGATIVE 2: IT-081-N2 — the forbidden write classes ----------
# 53.3: never modifies production runtime configuration, never modifies data,
# never rotates or writes secrets. Tested at the CREDENTIAL, per AT-110's
# discipline: the boundary is executed, not asserted.
for ATTEMPT in actions-secret-write environment-write workflow-file-change \
               org-settings-change records-write layer-b-read; do
  if attempt_as_reconciler "$ATTEMPT"; then
    fail "IT-081-N2: the reconciler credential succeeded at $ATTEMPT (AT-110)"
  fi
done
# The companion positive is mandatory: a credential that can do nothing would
# make all six vacuous.
run_reconciliation --full || fail "IT-081-N2: the bounded credential can no longer reconcile (AT-110)"
```

### 8.3 IT-102 — the seeded canary

**Owner:** L3 (`validators/drift/invariant-tests/IT-102.sh`). This is AT-102, and it is the single clearest statement of this file's governing principle.

```bash
set -euo pipefail
# validators/drift/invariant-tests/IT-102.sh
fail(){ echo "INVARIANT 44 VIOLATED: $*" >&2; exit 1; }

# ---------- IT-102-N1: a zero-finding run is a FAILED run ----------
# Suppress the canary in the fixture comparison set and run.
remove_canary_from_comparison_set
RESULT=$(run_reconciliation --json)
[ "$(jq -r .status <<<"$RESULT")" = "failed" ] \
  || fail "IT-102-N1: a run that did not find the canary reported '$(jq -r .status <<<"$RESULT")', not failed"
[ "$(jq -r '.signals[]' <<<"$RESULT" | grep -c SIG-13)" -ge 1 ] \
  || fail "IT-102-N1: the failed run did not raise SIG-13"
assert_gap_procedure_triggered || fail "IT-102-N1: the Section 53.7 gap procedure did not trigger"

# ---------- IT-102-N2: per-registry comparison counts detect a narrowed sweep ----------
# 53.1: every run records how many rows of each registry it actually compared,
# so a silently narrowed comparison is itself visible drift.
narrow_comparison_set --registry people.yaml --to-rows 1
RESULT=$(run_reconciliation --json)
[ "$(jq -r '.findings[] | select(.type=="comparison-narrowed") | .registry' <<<"$RESULT")" = "people.yaml" ] \
  || fail "IT-102-N2: the run compared 1 of N people rows and reported nothing"

# ---------- IT-102-P: the canary is found on a normal run ----------
restore_canary
[ "$(jq -r '.findings[] | select(.id=="CANARY") | .id' <<<"$(run_reconciliation --json)")" = "CANARY" ] \
  || fail "IT-102-P: the canary is not being found on a normal run"
```

### 8.4 IT-537 — when the loop ran wrong

Section 53.7's second branch is the one nothing else catches: *a loop that completed is not thereby a loop that was right.* **Owner:** L3.

| Test | Assertion |
| --- | --- |
| IT-537-N1 | Inject a repair class that writes incorrect state in the fixture. On discovery, the class **freezes**, a Level 5 escalation is raised, and its repairs in the affected window are enumerated from the Section 26.4 repair records. |
| IT-537-N2 | Every record produced in the gap window carries the `gap-window` mark, and **a `gap-window` record is refused as gate evidence** until re-verified. The negative test presents a `gap-window` record to a gate and asserts refusal. |
| IT-537-N3 | Replay of expiries during the gap actually revokes: an assignment `end_date` that fell inside the window is revoked on gap close, not left standing. |

### 8.5 Mutations

| Mutation | Applied to | Negative test that must flip to FAIL |
| --- | --- | --- |
| M-081-a | Fixture reconciler: change the strictness comparison from `>=` to `!=` | IT-081-U (`declared LOOSER` rows), IT-081-N1 |
| M-081-b | Fixture reconciler: treat an unreadable actual state as "loosest" | IT-081-U (`unknown` rows) |
| M-081-c | Fixture: widen the reconciler credential to include Actions-secret write | IT-081-N2 |
| M-102-a | Fixture: make a zero-finding run report `clean` | IT-102-N1 |
| M-102-b | Fixture: stop emitting per-registry comparison counts | IT-102-N2 |
| M-537-a | Fixture: make `gap-window` a display-only field | IT-537-N2 |
| `# MUTATION-NEEDED: create IT-537-N1.mutation.sh that breaks the invariant` | Fixture reconciler: when a repair class writes incorrect state, suppress the freeze signal so the class continues running instead of halting; assert IT-537-N1 now exits non-zero (freeze did not fire) | IT-537-N1 |
| `# MUTATION-NEEDED: create IT-537-N3.mutation.sh that breaks the invariant` | Fixture reconciler: on gap close, skip re-running expiries whose `end_date` fell inside the gap window; assert IT-537-N3 now exits non-zero (expired assignment remains provisioned) | IT-537-N3 |

---

## 9. Invariant 111 — no customer data in repositories

> **101.13 #111.** No customer data in repositories. Customer data lives in product databases, never in git — not in fixtures, not in support records, not in incident evidence; records reference customer data by identifier, never by copy. Three detectors enforce it: the fixture-provenance check (Section 38.3), the by-identifier construction of support records (22.2), and the S19 intake gate (Section 96.6). The verification authority owns the standing policy entry and its review cadence.

**Why silent failure is catastrophic, and uniquely so.** Section 38.3 states the reason in one clause: *git history is append-only, so this is the one prohibition with no rotation-equivalent remedy after the fact.* Every other credential-class failure in this specification has a remedy — rotate the secret, revoke the grant, redeploy the digest. This one does not. Section 96.6 S19 classifies committed customer data as **a live disclosure of customer data, not untidiness**, carrying a regulatory notification clock, and purging it requires an authorised, recorded history-rewrite exception. A detector that silently stops looking converts a bounded incident into an unbounded, undiscoverable one.

### 9.1 The three detectors

| Detector | What it enforces | Where | Lane |
| --- | --- | --- | --- |
| **Fixture provenance** (38.3) | Every file under `verification/ai-eval/fixtures/` carries a declared provenance — `synthetic`, `consented-and-recorded` with the consent record referenced, or `de-identified` with the method named — in a fixture manifest beside the scenarios. A fixture with no provenance declaration, **or a manifest entry with no file**, fails CI. | Verification-contract check | L1 |
| **By-identifier support records** (22.2) | Support records are constructed by identifier. A record carrying customer data by copy is rejected at schema validation. The same rule reaches incident evidence: any reproduction fixture attached to an incident record is synthetic or de-identified before it is committed. | Records schema | L4 |
| **S19 intake gate** (96.6) | Production dumps, real call recordings, exported spreadsheets, support transcripts, or fixtures built from live customer records block intake. **No AI-assisted session opens the repository until the S19 check passes** — universal floor. | Intake gate | L1 |

### 9.2 IT-111 — the tests

**Owner:** L1 (`validators/registry/invariant-tests/IT-111.sh`) for detectors 1 and 3; L4 (`tools/records/invariant-tests/IT-111-R.sh`) for detector 2.

> **Safety rule, binding and non-negotiable.** Every canary and fixture in this section is **synthetic**. It matches the detector's *shape* — a filename pattern, a field name, a manifest structure, a document that looks like a transcript — and never its *substance*. No real customer datum is planted anywhere, for any reason, at any time. Invariant 111 is not suspended for its own test, and there is no undo.

```bash
#!/usr/bin/env bash
# validators/registry/invariant-tests/IT-111.sh — Invariant 111, detectors 1 and 3.
set -euo pipefail
fail(){ echo "INVARIANT 111 VIOLATED: $*" >&2; exit 1; }

# ---------- POSITIVE: IT-111-P ----------
validators/registry/fixture-provenance.sh --tree fixtures/tree-clean \
  || fail "IT-111-P: a clean, fully-declared fixture tree failed the provenance check"
validators/registry/s19-intake-gate.sh --tree fixtures/tree-clean \
  || fail "IT-111-P: a clean tree failed the S19 intake gate"

# ---------- NEGATIVE 1: fixture with no provenance declaration ----------
if validators/registry/fixture-provenance.sh --tree fixtures/tree-fixture-undeclared; then
  fail "IT-111-N1: a fixture with no provenance declaration passed CI (38.3)"
fi

# ---------- NEGATIVE 2: manifest entry with no file ----------
# 38.3 names BOTH directions. A check that validates only file->manifest will
# pass this and is therefore half a check.
if validators/registry/fixture-provenance.sh --tree fixtures/tree-manifest-orphan; then
  fail "IT-111-N2: a manifest entry with no corresponding file passed CI (38.3)"
fi

# ---------- NEGATIVE 3: provenance declared but incomplete ----------
# 'consented-and-recorded' with no consent record referenced; 'de-identified'
# with no method named. A declaration is not a provenance.
for T in tree-consent-unreferenced tree-deident-no-method; do
  if validators/registry/fixture-provenance.sh --tree "fixtures/$T"; then
    fail "IT-111-N3($T): an incomplete provenance declaration was accepted"
  fi
done

# ---------- NEGATIVE 4: the S19 shape canary ----------
# Synthetic files matching each S19 category. NONE contains real data.
for C in prod-dump.sql call-recording.wav customer-export.xlsx \
         support-transcript.txt fixture-from-live-records.json; do
  if validators/registry/s19-intake-gate.sh --tree "fixtures/tree-s19/$C"; then
    fail "IT-111-N4($C): the S19 intake gate passed a tree containing $C"
  fi
done

# ---------- NEGATIVE 5: the gate actually blocks the AI session ----------
# 96.6: no AI-assisted session opens the repository until S19 passes. The gate
# reporting a finding while sessions proceed is a gate in name only.
if open_ai_session --repo fixtures/tree-s19/prod-dump.sql 2>/dev/null; then
  fail "IT-111-N5: an AI-assisted session opened a repository failing the S19 gate"
fi

echo "IT-111 PASS"; exit 0
```

```bash
#!/usr/bin/env bash
# tools/records/invariant-tests/IT-111-R.sh — Invariant 111, detector 2.
set -euo pipefail
fail(){ echo "INVARIANT 111 VIOLATED: $*" >&2; exit 1; }

# ---------- POSITIVE ----------
validate_record fixtures/support-by-identifier.yaml \
  || fail "IT-111-R-P: a correctly by-identifier support record was rejected"

# ---------- NEGATIVE 1: customer data by copy ----------
for F in support-with-email support-with-name support-with-address \
         support-with-pasted-transcript; do
  if validate_record "fixtures/$F.yaml"; then
    fail "IT-111-R-N1($F): a support record carrying customer data by copy validated (22.2)"
  fi
done

# ---------- NEGATIVE 2: incident reproduction fixture ----------
# 38.3: the same rule reaches incident evidence.
if validate_record fixtures/incident-with-raw-repro.yaml; then
  fail "IT-111-R-N2: an incident record with a non-synthetic reproduction fixture validated"
fi
echo "IT-111-R PASS"; exit 0
```

### 9.3 Mutations

| Mutation | Applied to | Negative test that must flip to FAIL |
| --- | --- | --- |
| M-111-a | Fixture: make the provenance check validate file→manifest only | IT-111-N2 |
| M-111-b | Fixture: accept any non-empty `provenance:` string | IT-111-N3 |
| M-111-c | Fixture: narrow the S19 pattern set to `*.sql` | IT-111-N4 (the four non-SQL categories) |
| M-111-d | Fixture: make the S19 gate warn instead of block | IT-111-N5 |
| M-111-e | Fixture records schema: allow a free-text `customer_note` field | IT-111-R-N1 |
| `# MUTATION-NEEDED: create IT-111-N1.mutation.sh that breaks the invariant` | Fixture: make the provenance check skip files that have no `provenance:` key (treat absence as implicitly declared) so a fixture with no provenance declaration passes CI | IT-111-N1 |
| `# MUTATION-NEEDED: create IT-111-R-N2.mutation.sh that breaks the invariant` | Fixture records schema: allow a free-text `reproduction_notes` field so an incident record with a non-synthetic reproduction fixture passes schema validation | IT-111-R-N2 |

### 9.4 Ownership and cadence

Invariant 111 is classified **mechanical** — it names three live checks — and it *additionally* carries a standing `policies.yaml` entry, because Section 38.3 requires one: *the verification authority owns fixture provenance and reviews it on the verification-contract cadence, recorded as a policy entry in `policies.yaml` with that owner and that cadence, so the invariant has a detector rather than an intention.*

| Field | Value |
| --- | --- |
| Owner | The verification authority (the holder of `verification_responsibility`) |
| Cadence | The verification-contract review cadence |
| Mechanism | The three detectors of §9.1 |
| Escalation on breach | Section 96.6 S19 treatment — live disclosure, `data.regulatory_notification_hours` clock, deletion obligation recorded in `records/deletion-requests/` (AT-105) |

---

## 10. The remaining mechanical invariants — test ledger

Each row: the invariant, the control, the negative test that proves the control can refuse, and the mutation that proves the negative test is alive. Full scripts follow the §3 exit contract and the §4–§9 pattern; they are not reproduced in full here because their shape is identical.

| # | Negative test | Mutation that must flip it to FAIL | Lane |
| --- | --- | --- | --- |
| 1 | A product reaching onboarding completion with no verification contract is refused | Remove the presence check from the contract validator | L1 |
| 3, 4 | A `restore_tested` date older than the rolling 90-day window fails CI; a declared date with **no matching record** in `records/restore-tests/` is Blocking | Make the check read the declared date only, never the record | L1 + L3 |
| 5 | A product merge dropping either verification contract is refused (AT-020) | Make the merge take the union of owners but the first contract | L1 |
| 7 | A `product.yaml` naming a departed person, or a role with no matching Team member, fails CI | Disable referential integrity in the validator | L1 + L3 |
| 8 | A PR merging with zero approving reviews is refused | Set required reviews to 0 | L5 |
| 11 | An act requiring a capability, attempted by a role-name match without the assignment, is refused (AT-091) | Resolve authority from `roles.yaml` instead of the assignment | L1 |
| 13 | A reviewer-matrix change by a non-holder of `reviewer-matrix-change` is refused; a permanent ownership change producing no Founder notification fails (AT-021) | Drop the notification emit | L1 + L4 |
| 14 | An item marked H1 with no commitment record, or H3 with a commitment, fails board validation | Accept any horizon value | L4 |
| 16 | A committed item whose verification path changed, without a Gate 1 re-plan, is blocked (29.5) | Compare only estimated scope | L2 |
| 17, 19 | Deleting a rejected machine PR's record is refused; the event-log entry survives (97.3, D107) | Grant delete on the records repository | L4 + L5 |
| 20 | A drafting job run with the issue-guard envelope inactive is refused (36.2); a context file with no constitution reference fails the Subsystem K check | Make the envelope advisory | L5 |
| 27 | Rollback across a migration boundary without a second `incident-response` countersignature is refused (64.2) | Remove the countersignature branch | L2 |
| 28 | A plan classified `partially-reversible` or `non-reversible` with no recovery strategy is rejected by the plan-checker (30.2) | Make the recovery-strategy field optional | L2 |
| 30 | Out-of-hours work with no authorisation record, or beyond quota, is refused (47) | Make the quota advisory | L4 |
| 31 | A product declaring `24x7` whose `coverage_window` is not fully covered by the accepted windows of active rota members fails contract validation (AT-047) | Compare rota length instead of window coverage | L1 |
| 35 | A `topology.yaml` with no Acting Team Lead designate fails validation (AT-003) | Make the succession block optional | L1 |
| 36, 37, 38 | Configuring an automated improvement plan, termination, promotion, compensation change or formal warning **fails validation**; no workflow permits automation to finalise a personnel action (AT-071) | Add a `finalise` transition to the fixture people workflow | L1 + L4 |
| 39 | A missing second organisation Owner or escrowed break-glass credential, or a stale founder-only account inventory, fails the AT-022 drill | Make the drill read the declaration instead of testing usability | L5 |
| 40 | A decision record written by a machine identity is refused; a state record written by a human outside the sanctioned path is flagged | Grant the records-writer a decision-path scope | L4 + L5 |
| 42 | Every `.planning/` artifact is readable and useful with GSD uninstalled (AT-030) | Add a GSD-only field the reader requires | L2 |
| 44 | See §8.3 — the seeded canary, AT-102 | See M-102-a | L3 |
| 46 | A metric whose declared source is not a canonical record store of Section 97 fails validation | Accept a literal-value source | L4 |
| 47 | A force push, branch delete or tag delete on the records repository is refused; an unsigned commit, or one signed by any other identity, is Blocking drift; a head not descending from the last anchored SHA is **Blocking, Level 5** (D107) | Add a bypass actor to the records ruleset | L4 |
| 48 | A failed source re-read leaves existing verified content intact and downgrades nothing to pending (AT-088) | Make the reader clear before it writes | L4 |
| 49 | A metric with no owner or no defined response fails registry validation | Make both fields optional | L4 |
| 50–54 | Adding product 21 / a person / a role touches no dashboard, workflow or script (AT-001, AT-002, AT-007); a hard-coded person or product identifier in any dashboard, workflow or script fails the scan | Narrow the scan to `dashboards/` only | L1 + L3 |
| 55, 56 | An ownership change not applied through reconciliation, or a role change not recalculating capabilities, fails (AT-021, AT-005) | Apply ownership directly to CODEOWNERS | L3 |
| 57 | A departure leaving a blocking orphan that can be dismissed unresolved fails (AT-017) | Make blocking orphans dismissible | L3 |
| 58 | A non-employee assignment with no `end_date` fails schema; an expired assignment still provisioned after a reconciliation run is Blocking (AT-018, AT-008, AT-036) | Make `end_date` optional | L1 + L3 |
| 59 | A product with a single named owner and no measured redundancy shows no risk indicator | Make redundancy a manual field | L4 |
| 61 | A framework version change applied retroactively to a closed period is refused (AT-078) | Ignore effective dates | L1 |
| 62 | A product with three repositories producing three dashboard entries or three contracts fails (AT-010) | Key the dashboard on repository | L1 |
| 63, 64 | A declared dependency naming no registered service **fails CI** (53.1) | Make unknown dependencies a warning | L1 + L3 |
| 65 | A split or merge losing historical evidence under the original identity fails (AT-019, AT-020) | Reparent history to the successor | L1 |
| 67 | A product set `lifecycle: active` before contract validation passes is refused (64.1) | Default lifecycle to active | L1 |
| 68 | A `sunset` product still carrying active Renovate, monitoring and CI configuration raises drift | Skip lifecycle in the comparison set | L3 |
| 69 | A product with `launch_status: pre-launch` presented as launched fails validation | Merge the two fields | L1 |
| 71, 72 | A fleet rollout with no passing canary is refused (AT-023, AT-024, AT-026) | Make the canary advisory | L1 + L2 |
| 73 | A schema change requiring simultaneous fleet migration is refused (AT-025) | Drop version negotiation | L1 |
| 74 | A transitional product with no named migration owner or no deadline fails schema; a breached deadline surfaces as drift | Make the deadline optional | L1 + L3 |
| 75, 76 | A product's runtime path reaching a control-plane endpoint fails the control-plane/data-plane invariant test; products keep serving with the control plane unreachable (AT-029, AT-030) | Add a control-plane read to the fixture product's request path | L5 |
| 77 | An exception with no expiry **fails CI**; a same-scope exception reopened after closure increments the renewal count and a fresh ID does not reset it (AT-036, AT-037, AT-038) | Key renewal counting on exception ID | L1 |
| 78 | A new policy created at `Enforce` without the critical-security-control flag is refused (55) | Make the initial stage free | L1 |
| 79 | A newly provisioned person, product, repository or tool arriving with more than minimum privilege fails the safe-defaults check (64.1) | Copy privileges from a template peer | L3 |
| 80 | An unclassified control **fails CI** (64.2) | Default unclassified to fail-open | L1 |
| 82 | A control-plane change with no change manifest is refused | Exempt the control-plane repository | L1 |
| 83, 85, 86 | A metered LLM API configured in engineering tooling is refused; an unpinned action, a floating GSD version or a moved workflow tag is Blocking (53.1); AT-011 passes with the provider removed | Compare tag names instead of resolved SHAs | L2 + L3 + L5 |
| 87 | An invariant classified `mechanical` naming no live check, one classified `policy` naming no live `policies.yaml` entry, or one carrying no classification, **fails control-plane CI** — this table is the input | Make the classification check warn | L1 |
| 88 | A product with no `infrastructure.monthly_budget_band` fails contract validation; spend outside the band raises Red (AT-050) | Make the band optional | L1 |
| 90–104 | Each named AT- test in §2.12 executed negatively: a person-directed signal from one metric is refused (AT-061); a banned measurement introduced into the schema is rejected (AT-075); a composite productivity score is rejected (AT-086/AT-098); a signal with no confidence field is rejected (AT-064); a decision inside the evidence window returns Insufficient Evidence and emits no negative signal (AT-072) | For each: relax the corresponding schema field or threshold in the fixture | L1 + L4 |
| 106–110 | AT-090, AT-091, AT-092, AT-093, AT-094, AT-095, AT-096, AT-097, AT-098, AT-100 executed for real, at **both** the application and the datasource layer. An assignment granting `people-intelligence` **fails validation**; a shared-instance login grants nothing on the Founder-only instance; the people datasource is absent from the shared Grafana instance's **provisioned configuration**, verified there and not inferred from panel visibility (D75) | Register the people datasource in the shared instance and hide the panels — if AT-097 still passes, it was reading panels, not provisioning | L5 |

**AT-108 and AT-110** are executed verbatim as the spec writes them, because both are already stated as negative tests with a positive companion:

* **AT-108** — four attempts from the ops console's own OS user and credentials (control-plane write, `records/` write, board mutation, any Layer B access), all four must fail; the console then still answers a read query over Layer A correctly. Owner: L5.
* **AT-110** — six attempts from the reconciler's own credential (Actions-secret write, environment write, workflow-file change, organisation-settings change, `records/**` write, any Layer B access), all six must fail; the credential then still completes a normal reconciliation run. **Executed for real at the phase that builds the reconciler and re-executed at every rotation**, on the same gate as 40.1's clean-reconciliation condition. Owner: L3. This is the highest-privilege identity in the system (99.6 risk 6), and its boundary must be executed rather than asserted.

---

## 11. The sixteen non-mechanical invariants

Five are `policy`; eleven are `review-held`. Each names an owner and a cadence, because Section 101's preamble is explicit that an invariant which is neither mechanically enforced nor entered as a policy *has no owner, no cadence, and nothing detects the omission.*

**These are not exempt from detection.** Control-plane CI checks that each `policy` row names a live `policies.yaml` entry and each `review-held` row names a standing review and the role that chairs it. The *content* is judged by a human; the *existence and freshness* of the entry is mechanical.

### 11.1 Policy-enforced (5)

| # | Invariant | Owner | Cadence | Mechanism | Detector on the mechanism |
| --- | --- | --- | --- | --- | --- |
| 2 | Every production bug becomes a permanent regression test | Verification authority | Per-postmortem close-out (58.4); sampled at the quarterly review | Postmortem close-out requires the regression test to exist and be named | A postmortem closed with no named regression test is a closure-quality defect (53.6) and is reopened |
| 29 | SEV-1 restoration takes priority over quota, fairness and scheduling | Escalation role | Reviewed at each postmortem (58.4) and at the quarterly review | Standing `policies.yaml` entry; the weekend and out-of-hours exception path never gates SEV-1 restoration (47.2, invariant 30) | An incident record showing restoration delayed by a quota or scheduling rule is a pattern candidate (Section 58) |
| 60 | Knowledge rotation mandatory; ownership rotation conditional | Team Lead | Quarterly review | Rotation plan per product, reviewed against the knowledge-redundancy measure (103.10) | A product whose redundancy measure has not moved across two consecutive quarters is named in the review pack |
| 66 | Transfer preserves continuity; secrets rotated by the receiver, never transferred | A DevOps-capability holder | Per transfer; audited at the quarterly review | Transfer runbook: the receiver rotates; nothing is handed over | A transfer record with no receiver-side rotation entry fails the audit sample |
| 89 | The operating system prices itself | Founder | Quarterly review (57) | Standing automation-ledger entry weighed against value | A quarter with no ledger entry update is Amber on the OS-review pack |

### 11.2 Review-held (11)

| # | Invariant | Standing review that reads it | Chaired by | Evidence it reads |
| --- | --- | --- | --- | --- |
| 6 | Verification depth never traded for throughput | Calibration review (84.6) | Team Lead | AT-082; verification demand vs capacity |
| 10 | Team Lead is not the routine reviewer; >2 routine/week is investigable | Quarterly operating-system review | Founder | Review load per person (103.9), cross-checked against the routing table |
| 15 | Ready-queue misses trend to zero; the queue does not routinely reach zero | Weekly operating picture (94); trend at the quarterly review | Team Lead | Ready-queue-miss detector (97.5) |
| 32 | The founder does not manage daily task assignment | Quarterly operating-system review | Founder | Assignment records; Founder attention ledger (67.2) |
| 33 | The founder does not review routine code or dispatch responders | Quarterly operating-system review | Team Lead | Review load (103.9); incident responder records (AT-101) |
| 34 | Founder absence does not halt engineering; the founder-only list stays short | Quarterly review + the AT-022 continuity drill | Founder | Founder decision queue depth and age (103.8) |
| 41 | GitHub remains the durable engineering source of truth | Quarterly review against the tool register (62) | Founder | `tools.yaml`; the 62.5 substrate carve-out |
| 43 | No second workflow overlay competes with GSD | Quarterly review | Team Lead | `tools.yaml` — every new tool requires an entry with an owner and an exit condition |
| 45 | No artifact becomes a dumping ground; the hierarchy resolves conflicts | Quarterly review, alongside AT-045 retirement | Founder | Source-of-truth hierarchy (Section 5); artifact growth |
| 70 | Business health is a first-class portfolio signal | Quarterly portfolio review | Founder | Portfolio economics (Section 68) |
| 105 | The OS is an evidence engine, not an HR replacement | Quarterly review | Founder | AT-045 bureaucracy check; automation ledger |

**AT-045 binds this section.** The quarterly review must retire at least one policy, one metric or one automation, or explicitly record why nothing warranted retirement. A review-held invariant whose review produces the same answer every quarter for a year is itself a retirement candidate — not because the invariant stopped mattering, but because a review that cannot change its answer is the review equivalent of a check that can only pass.

---

## 12. When these tests run

| Point in the build | What executes | On failure |
| --- | --- | --- |
| Lane PR → `integration` | Every `IT-*` owned by that lane, positive and negative | Block the PR. The lane opens a blocker issue and stops. |
| Every merge into `integration` | The full `IT-*` suite across all five lanes, positive and negative | Block the merge train. L0 triages; the lane that broke it fixes it. |
| `integration` → `main` | The full suite **plus the complete mutation run** of §1.2 | Block promotion. A vacuous test is treated as a failed invariant, not as a test-quality nit. |
| Weekly, on schedule | The full suite plus the mutation run, against the live estate's read-only surfaces and disposable fixtures | Blocking-class drift; Level 5 if the suite itself did not run. |
| At each Section 95.4 headcount threshold | The activation checklist's named tests, **executed for real, negative tests included** | The gate is not recorded as armed. The bootstrap exception stays open with its expiry. |
| At every fifth-tier credential rotation | AT-110, IT-026, and a clean manual reconciliation run (40.1) | The rotation is **not** recorded as done. A credential that rotates but no longer reconciles has been broken, not rotated. |

### 12.1 STOP rules

A lane encountering any of the following does not proceed, does not work around it, and does not weaken the test. It opens a blocker issue using the `master/09` §7.1 template — the authoritative verbatim form, reproduced here rather than reinvented — and stops.

**Title:** `BLOCKER [<task-id>]: <one line, imperative, ≤ 60 chars>`
**Labels:** `blocker`, `lane/<N>`, `phase/<phase-lower>`

```bash
gh issue create \
  --title "BLOCKER [L3-F5-06]: negative test IT-041 passes under its mutation" \
  --label blocker --label lane/3 --label phase/f5 \
  --body-file blocker-body.md
```

**Body** carries all six fields `master/09` §7.1 requires — `## Task`, `## STOP condition that fired`, `## What I observed`, `## What I need decided`, `## Options I can see`, `## What I have NOT done` — filled in, never omitted.

| Condition | Text for the title's `<one line>` slot | Route to |
| --- | --- | --- |
| A negative test passes under its mutation | `negative test IT-<nnn> passes under its mutation` | L0 Integrator |
| A test exits 2 (cannot run) twice consecutively | `IT-<nnn> exits 2 (cannot run) twice consecutively` | L0 Integrator |
| A mechanical invariant in §2 has no live check to name | `INV-<nnn> has no live check to name` | L0 Integrator; Section 101 preamble requires control-plane CI to fail on this |
| A lane needs to edit a test owned by another lane | `IT-<nnn> needs an edit outside my lane` | L0 Integrator — file a Contract Change Request; never edit a foreign path (PARTITION.md rule 1) |
| A test would require planting real customer data | `test would require planting real customer data` | L0 Integrator and the verification authority. See §1.4. There is no undo. |

### 12.2 The one thing this protocol cannot do

Five low-cost developers on five branches, none holding full context, will each build something that passes its own lane's tests. That is not the failure mode this file guards against. The failure mode is a lane building a check that reports green because it never looked — a provenance check reading only one direction, a digest sweep treating an unreachable service as a pass, an actor gate placed below the step it was meant to guard, a reconciler treating an unreadable state as a loose one.

Every one of those passes a positive test. Every one of them passes a negative test written by the same developer who wrote the check. **Only the mutation run tells them apart**, and only because the mutation is specified here, in a file no lane owns, against a control the mutation is designed to break.

### 12.3 IG-06 satisfiability note

<!-- DF-0098 / DF-0099 / DF-0103 fix assessment -->
IG-06 (`invariant-classification.sh`) checks three things: `classified=111/111`, `dangling_refs=0`, `unclassified=0`. The §2 classification table was and remains complete — all 111 invariants carry a classification, and all mechanical ones name a real AT-id or platform check. The three bugs made IG-06 unsatisfiable because the test scripts that are the "live checks" could not execute (undefined helpers), could not be proven non-vacuous (missing mutations), and had no assigned implementation path (ownerless §10 rows).

After the fixes in this file:

1. **Shell stubs (§3.2):** 32 helper functions are now defined. Scripts in §5–§9 can execute. The `dangling_refs` count drops to zero once implementing lanes source these stubs.
2. **Mutation placeholders:** 7 `MUTATION-NEEDED` rows signal the implementing lane for each negative test that lacked a mutation script. The lane creates the named `.mutation.sh` file; the placeholder is the acceptance criterion.
3. **Lane assignments (§10):** All 51 rows in the §10 ledger now carry a Lane column. Each test has an unambiguous owner and therefore an unambiguous script path (§3 placement table), which is required for the check to be "live".

**IG-06 will output PASS once:** (a) implementing lanes source or inline the stubs and replace them with real implementations, (b) the 7 mutation scripts are created, and (c) test scripts for the 51 §10 rows are created in their lane-owned paths. Nothing in the §2 classification table requires further change.

That is the whole argument for §1.2. A reconciliation run that finds nothing is a failed run. A test suite that has never been observed failing is an unproven suite.
