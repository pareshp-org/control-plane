# 09 — Fixtures and Test Data

**Status: binding.** Part of the verification and merge protocol for the five-lane parallel build.
Conforms to `implementation/PARTITION.md` (FROZEN). Spec: `Research/MultiProduct_MasterSpec_v4.0.md`.

---

## 1. Scope, and the one rule this file exists to enforce

Five lanes build in parallel. No lane has full context. The only thing standing between "L3 built a
reconciler" and "L3 built a reconciler that reports clean because it stopped looking" is a corpus of
test data that both lanes' gates run against, where **some of the data is deliberately wrong and the
gate is required to say so**.

The specification holds this position in four places, and this file is the fifth:

| Where | The rule |
| --- | --- |
| Section 53.1, the seeded-canary rule | A permanent seeded drift record exists at all times and every reconciliation run MUST find it. A run reporting zero findings, canary included, is a **FAILED** run. |
| AT-102 | The same rule as an executable acceptance test: a reconciler that finds nothing is assumed broken, never assumed clean. Raises SIG-13 and triggers the gap procedure. |
| Section 31.2 | Every `verification/contract.yaml` declares a seeded-defect case the contract MUST fail. A run in which the seeded defect passes is a FAILED run. A contract that cannot fail is not a contract. |
| Section 103.1 (plan-checker) and Section 103.9 (Review Network Quality) | Zero rejections means the gates are not working; and for code review, "very low may mean rubber-stamping". |

**The fixture rule that follows.** Every gate any lane ships is proven able to fail by at least one
fixture that it must reject. A gate with zero negative fixtures is an **unproven gate**, and an
unproven gate is Blocking on the merge train — it does not matter how green it is. A negative fixture
that a gate accepts is a **failed run of that gate**, not a passing run of the suite.

---

## 2. Ownership

| Thing | Owner | Repository / path | Mutability |
| --- | --- | --- | --- |
| The shared fixture corpus | **L0 Integrator** | `control-plane`, `contracts/fixtures/**` | Written in Phase 0, then FROZEN. No lane edits it, ever. |
| Fixture provenance and its review | **L0 Integrator**, standing in for the verification authority of Section 38.3 | `contracts/fixtures/**` + a `policies.yaml` entry naming L0 as owner and the cadence | Reviewed on the verification-contract cadence |
| Lane-local test data | The owning lane | `<lane-owned-root>/testdata/**` | Additive-only, inside paths that lane already owns |
| The fixture canary `NEG-CANARY-000` | **L0 Integrator** | `contracts/fixtures/neg/canary/NEG-CANARY-000/` | Permanent. Never repaired. Never quarantined. |
| The generated fixture index | Nobody — it is generated | `derived/fixture-index.json`, git-ignored | Never committed (invariant 46: derived data is computed, never hand-maintained) |

`contracts/fixtures/**` sits inside `contracts/**`, which PARTITION §"Non-negotiable anti-conflict
rules" rule 2 already assigns to L0 and freezes in Phase 0 — "Lanes code against it and against
generated stubs/fixtures." No new top-level owner is introduced and no row of the FROZEN ownership
table changes. The fixture corpus is a contract artifact and is governed exactly like one.

**Provenance is fixed and narrow.** Section 38.3 permits `synthetic`, `consented-and-recorded` or
`de-identified`. In this build corpus, **`synthetic` is the only legal value** and the linter rejects
the other two. A build fixture has no legitimate need for real data, git history is append-only, and
invariant 111 has no rotation-equivalent remedy after the fact — the S19 intake gate of Section 96.6
exists because there is no way back.

---

## 3. Directory convention — why fixtures cannot collide across lanes

Four properties, each of which alone removes a class of merge conflict.

**P1. One file per fixture. No index, ever.** PARTITION rule 3 — "No shared mutable file, ever. No
lane appends to a shared index, list, or registry-of-everything. Directory-per-item only." A fixture
is a directory containing its own files and its own `fixture.yaml`. There is no `fixtures.yaml`
listing them, because that file would be the one place five lanes touch on the same day. Discovery is
by filesystem walk; the index is generated at run time into `derived/fixture-index.json` and is
git-ignored.

**P2. Ids are namespaced by owner, so two lanes cannot mint the same id.** A lane may only create ids
in its own prefix. This is checked by `make fixtures-lint`, not left to discipline.

| Prefix | Minted by | Lives under |
| --- | --- | --- |
| `fx-…` | L0 only | `contracts/fixtures/core/**` |
| `NEG-…` | L0 only | `contracts/fixtures/neg/**` |
| `l1-…` | L1 only | `validators/registry/testdata/**` |
| `l2-…` | L2 only | `tools/evidence/testdata/**` |
| `l3-…` | L3 only | `reconciler/testdata/**`, `validators/drift/testdata/**` |
| `l4-…` | L4 only | `tools/records/testdata/**`, `schemas/records/testdata/**` |
| `l5-…` | L5 only | `access/testdata/**`, `infra/testdata/**` |

**P3. Every lane-local `testdata/` root sits inside a path that lane already owns exclusively.** The
lane-guard CI check of PARTITION rule 1 therefore polices fixture placement for free — a lane writing
a fixture into another lane's `testdata/` fails the same check that catches a lane writing that
lane's source. No new enforcement is needed.

**P4. Negative fixtures are foldered by the gate they must fail, one directory per case.** Two lanes
adding negative cases for different gates never touch the same directory, and two cases for the same
gate are two sibling directories, not two entries in one file.

```
control-plane/
  contracts/
    fixtures/
      core/                                # the shared corpus — L0, FROZEN
        org/
          people.yaml
          roles.yaml
          topology.yaml
          platform.yaml
          policies.yaml
          exceptions.yaml
          os-health.yaml
          economics.yaml
        products/
          fx-svc-core/product.yaml
          fx-svc-core/verification/contract.yaml
          fx-svc-edge/…
          fx-app-mobile/…
          fx-lib-sdk/…
          fx-batch-etl/…
          fx-hosted-onprem/…
          fx-wl-partner/…
          fx-site-docs/…
        records/                           # one file per record, per Section 97.2
          deployments/…  uat/…  incidents/…  restore-tests/…
          decisions/…    decisions/pending/…
          deletion-requests/…  security-reviews/…  support/…  eval/…
        events/                            # one file per event, per Section 97.3
          2026-08-27/EVT-2026-08-27-000001.yaml
        canary/
          drift-canary.yaml                # the Section 53.1 seeded drift record
      neg/                                 # negative corpus — L0, FROZEN
        <GATE-ID>/
          <CASE-ID>/
            fixture.yaml                   # parent + mutation + expected rejection
            <the mutated artifact>
        canary/
          NEG-CANARY-000/…
  validators/registry/testdata/            # L1 only
  tools/evidence/testdata/                 # L2 only
  reconciler/testdata/                     # L3 only
  validators/drift/testdata/               # L3 only
  tools/records/testdata/                  # L4 only
  access/testdata/                         # L5 only
  infra/testdata/                          # L5 only
```

Every fixture directory carries a `fixture.yaml`:

```yaml
# contracts/fixtures/neg/CONTRACT-VALIDATE/NEG-CONTRACT-011/fixture.yaml
fixture_schema_version: 1
id: NEG-CONTRACT-011
kind: negative                     # positive | negative
provenance: synthetic              # the only legal value in this corpus
owner: L0
parent: fx-svc-core                # the positive fixture this mutates
mutation: "operations.coverage_window set to null while support_model remains 24x7"
must_be_rejected_by:               # gate ids; at least one is mandatory for kind: negative
  - CONTRACT-VALIDATE
expected_reason_contains: "coverage_window"
cites:
  - "Section 15.5"
  - "Section 15.6"
  - "AT-047"
  - "invariant 31"
```

---

## 4. The fixture organisation

One organisation, `fx-org`. It exists so that every lane resolves identity, authority, capability and
capacity against the same declared state, and so that a lane that quietly invented its own people
model fails the moment it meets the shared corpus.

### 4.1 Fixture people — `contracts/fixtures/core/org/people.yaml`

Spans every employment type of Section 7 and every work-arrangement shape of Section 7.3. Fourteen
entries. Ids are stable and never reused (Section 7.1).

| id | role | `employment_type` | `availability` | `access_status` | `arrangement` | timezone | `fte` | schedule shape | why it is in the corpus |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fx-founder-1` | founder | employee | active | provisioned | hybrid | `Asia/Kolkata` | 1.0 | mon–fri | Holds `people-intelligence`; the only holder (invariant 106, AT-090) |
| `fx-lead-1` | team_lead | employee | active | provisioned | onsite | `Asia/Kolkata` | 1.0 | mon–fri | Escalation resolution target through `topology.yaml` |
| `fx-lead-2` | team_lead | employee | active | provisioned | remote | `Europe/Lisbon` | 1.0 | mon–fri | Acting Team Lead designate, dormant capability (AT-003, invariant 35) |
| `fx-dev-1` | developer | employee | active | provisioned | hybrid | `Asia/Kolkata` | 1.0 | mon–fri | `primary_owner` on `fx-svc-core` |
| `fx-dev-2` | developer | employee | active | provisioned | remote | `America/New_York` | 1.0 | mon–fri, `accepted_coverage_window` set | Funded rota member; the far-timezone half of the 24x7 window (Section 47.9, AT-047) |
| `fx-dev-3` | developer | employee | on_leave | provisioned | onsite | `Asia/Kolkata` | 0.6 | **mon/wed/fri only — tue and thu omitted** | Part-time is configuration, not an exception (Section 7.3); open leave record in `records/leave/` |
| `fx-dev-4` | developer | employee | active | **suspended** | remote | `Asia/Kolkata` | 1.0 | mon–fri | `suspended` is legal only with `active` or `on_leave` (Section 7.1); carries a review-by date |
| `fx-qa-1` | qa | employee | active | provisioned | hybrid | `Asia/Kolkata` | 1.0 | mon–fri | Verification authority; `verification_responsibility` on every product |
| `fx-int-1` | developer | **intern** | active | provisioned | onsite | `Asia/Kolkata` | 0.5 | mon–fri half days | Non-employee: `end_date` mandatory (Section 7.1) |
| `fx-con-1` | developer | **contractor** | active | provisioned | remote | `Europe/Berlin` | 0.8 | mon–thu | `scope.repositories_only: true`, no ownership, no production (AT-008, EC-10) |
| `fx-sec-1` | specialist | **temporary_specialist** | active | provisioned | remote | `Europe/Berlin` | 0.4 | tue/thu | Single capability `security-review`, scoped to two products (EC-11) |
| `fx-cons-1` | specialist | **consultant** | active | provisioned | remote | `Australia/Sydney` | 0.2 | wed only | The extreme fractional-FTE and antipodal-timezone case |
| `fx-dev-9` | developer | employee | **departed** | **revoked** | — | — | — | `work_arrangement` absent | Departure is a state, not a deletion (Section 7.1); id never reused; historical approvals stay interpretable (AT-017) |
| `fx-con-9` | developer | contractor | active | **revoked** | remote | `Europe/Berlin` | 0.5 | mon–fri | Non-employee past `end_date`: the second legal `revoked` pairing (Section 7.1); reconciliation revoked it with no human action (AT-018, AT-036, invariant 58) |

**Work-arrangement shapes deliberately covered.** Full-time onsite; full-time hybrid; full-time remote
in a distant timezone; part-time with omitted weekdays; fractional FTE at 0.5, 0.4, 0.2; a member with
`accepted_coverage_window` set and members with it `null`; and a person with no `work_arrangement`
block at all (`fx-dev-9`, departed) so the fail-closed path of Section 7.3 has something to resolve
against. Every timezone is an IANA identifier — Section 7.3 forbids UTC offsets, and
`NEG-PEOPLE-004` proves the check.

### 4.2 Assignments and delegations

`fx-svc-core` carries `primary_owner`, `cross_reviewer`, `backup_owner`, `incident_responder`
(primary and backup) and `verification_responsibility`, so invariant 7 resolves. The corpus also
carries one live instance of each dated delegation type of Section 10.1 that a lane's validator must
handle: `plan_approval_delegate`, `production_approval_delegate`, `registry_owner_delegate`,
`verification_delegate`, `incident_coordination_delegate`, `cross_review_shadow`, `mentor`,
`founder_decision_delegate` — each with a mandatory `end_date`, one of them within 14 days of expiry
so the advance-warning path of Section 10.1 has an input. `founder_decision_delegate` is the positive
instance `NEG-ASSIGN-001` (§7.1) names as its `parent`.

---

## 5. Fixture products — one per conformance profile

Eight products, matching the eight live products of the real portfolio, and spanning all seven
`conformance_profile` values of Section 15.7. Every rule written against the service interface must be
seen to validate against a profile's *equivalent evidence* instead — a `client-app` is never failed
for lacking a health endpoint, and a `service` cannot escape availability evidence by mis-declaring.

| Product | `conformance_profile` | Repos | `reliability_criticality` | `class` | `support_model` | Equivalent evidence the corpus carries | Why this one exists |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `fx-svc-core` | `service` | 3 (api, web, mobile) | critical | commercial | **24x7** | Health + version endpoints, availability signals, deploy and restore evidence | AT-010 (one product, three repositories); Section 15.6 funded-rota blocker satisfied by `fx-dev-2` + `fx-lead-2`; canary-set member (Section 61.3) |
| `fx-svc-edge` | `service` | 1 | high | internal | business-hours | Same as above, single repo | Carries `conflict_check: waived-with-decision` on a 99.5% commitment — the honest waiver of Section 21.4 and D82, never a false pass |
| `fx-app-mobile` | `client-app` | 1 | high | commercial | extended | Crash-free-session telemetry, store version adoption, `rollback_method: halt-staged-rollout`, a declared remote kill-switch flag | The live requirement of Section 15.7; exercises `staged_rollout.stages_pct`, `observation_window_hours`, `crash_free_sessions.sev1_below_pct` / `sev2_below_pct` |
| `fx-lib-sdk` | `library` | 1 | medium | internal | business-hours | Published registry version + consumer contract tests | AT-009 / EC-38: the operating system does not change for a stack with no serving interface (S17) |
| `fx-batch-etl` | `batch` | 1 | high | regulated | business-hours | Job success records + data-freshness signals instead of availability | `data.classification: regulated`, `residency: eu`, `regulatory_notification_hours: 72` — the deletion and breach paths need a regulated product to resolve (AT-105) |
| `fx-hosted-onprem` | `customer-hosted` | 1 | medium | commercial | business-hours | Customer-attested deploy and restore records | S16: the recorded-exemption-with-compensating-control branch of Section 15.7 |
| `fx-wl-partner` | `white-label` | 2 | medium | commercial | business-hours | A per-deployment environment list (three deployments) | The one profile whose evidence is per-deployment rather than per-product |
| `fx-site-docs` | `static-site` | 1 | low | internal | business-hours | Build reproducibility; `recovery: not-applicable` permitted | Proves the restore-cadence check (invariant 4) does not fire where the profile exempts it |

Every positive product contract validates clean against every gate, including `restore_tested` dates
backed by a matching record in `contracts/fixtures/core/records/restore-tests/` — a declared date with
no matching record is a Blocking row of Section 53.1, and `NEG-CONTRACT-016` proves the check fires.

---

## 6. Fixture records, events and evidence

L2 and L4 need inputs that exist before either lane's writer does.

| Store | Fixture content | Cited |
| --- | --- | --- |
| `events/` | One file per event, one directory per day. At least one event of every `event_type` L1–L5 emit in Phase 1, all present in the fixture `platform.yaml` enum. Full envelope on every one. | Section 97.3 |
| `records/deployments/` | Three: one clean digest promotion, one rollback (`rollback_of` populated), one whose `approved_by` differs from the deploying actor | Section 32, invariants 12 and 22 |
| `records/uat/` | Two, written through the RECORD-VERIFICATION-RESULT shape | Section 97.2 |
| `records/restore-tests/` | One per product with a `restore_tested` date, plus one with an integrity-check result and a named verifier | Section 44.3, 44.5 |
| `records/decisions/` and `records/decisions/pending/` | One decided, one pending, so queue depth and age are computable | Section 103.8 |
| `records/deletion-requests/` | One with all four timestamps (`requested`, `verified`, `executed`, `confirmed`), a named executor and a subprocessor propagation checklist | AT-105, Section 97.2 |
| `records/support/` | Two, constructed by identifier only — customer referenced as `customer-ref-017`, never by name or content | Section 22.2, invariant 111 |
| `records/security-reviews/`, `records/eval/`, `records/launches/`, `records/onboarding/`, `records/incidents/`, `records/postmortems/`, `records/leave/`, `records/bootstrap-log/` | One representative record each | Section 97.2, 95.4 |
| `contracts/fixtures/core/canary/drift-canary.yaml` | The permanently planted, clearly labelled mismatch every reconciliation run must find | Section 53.1, AT-102 |

All timestamps are UTC with offset (Section 97.1). Every record carries `record_schema_version`; every
event carries `event_schema_version`. No record in the corpus is ever edited in place — corrections in
the fixture set are follow-up records, because that is what invariant 47 requires of the real ones.

---

## 7. The negative corpus

One directory per case. Each `must_be_rejected_by` a named gate. **Every row below is mandatory** —
the lane that owns the gate cannot merge to `integration` until its gate rejects its rows.

### 7.1 L1 — registries, contracts, schemas (gate `CONTRACT-VALIDATE`, `PEOPLE-VALIDATE`)

| Case | Mutation of the positive parent | Must be rejected because |
| --- | --- | --- |
| `NEG-CONTRACT-001` | `classification.reliability_criticality` deleted | Section 15.5 — missing required field |
| `NEG-CONTRACT-002` | `restore_tested` backdated beyond the 90-day floor | Section 15.4, invariant 4 |
| `NEG-CONTRACT-003` | assignment references `fx-dev-9` (departed) | Section 15.5 |
| `NEG-CONTRACT-004` | assignment `end_date` in the past | Section 15.5, invariant 58 |
| `NEG-CONTRACT-005` | `dependencies.internal` names a service absent from the registry | Section 15.5, invariant 64 |
| `NEG-CONTRACT-006` | `contract_version: 99` | Section 15.5, invariant 73 |
| `NEG-CONTRACT-007` | `data.residency: eu` with `infrastructure.region: us-east-1`, no recorded resolution | Section 15.5 |
| `NEG-CONTRACT-008` | commitment conflicting with declared RTO/`detection_expectation`, `conflict_check: passed` | Section 15.5, 21.4, D82 |
| `NEG-CONTRACT-009` | `ai_runtime_dependency` block, no `verification/ai-eval/` suite | Section 15.5, **AT-049** |
| `NEG-CONTRACT-010` | `launch_status: launched`, `intake_channel` and `triager` null | Section 15.5, AT-048 |
| `NEG-CONTRACT-011` | `support_model: 24x7`, `coverage_window: null` | Section 15.5, 15.6, invariant 31 |
| `NEG-CONTRACT-012` | `coverage_window` with one hour uncovered by active rota members' accepted windows | Section 47.9, **AT-047** |
| `NEG-CONTRACT-013` | `conformance_profile: client-app` with no `staged_rollout` and no kill-switch declaration | Section 15.7, 15.5 |
| `NEG-CONTRACT-014` | `conformance_profile: library` on a product that serves HTTP traffic — profile mis-declared to escape availability evidence | Section 15.7 |
| `NEG-CONTRACT-015` | `recovery:` block present, no `restore-production.yml` | Section 15.5, **AT-103** |
| `NEG-CONTRACT-016` | `restore_tested` date with no matching record in `records/restore-tests/` | Section 53.1 (Blocking) |
| `NEG-CONTRACT-017` | `operations.detection_expectation` differing from the value `support_model` implies | Section 15.1, 42.2 |
| `NEG-PEOPLE-001` | contractor with `end_date: null` | Section 7.1 |
| `NEG-PEOPLE-002` | `availability: departed` with `access_status: provisioned` | Section 7.1 |
| `NEG-PEOPLE-003` | `access_status: suspended` with `availability: departed` | Section 7.1 |
| `NEG-PEOPLE-004` | `work_arrangement.timezone: "+05:30"` | Section 7.3 — IANA identifier, never an offset |
| `NEG-PEOPLE-005` | `fte: 0` on one person, `fte: 1.4` on another | Section 7 — `0 < fte <= 1` |
| `NEG-PEOPLE-006` | rota member with no `work_arrangement` block | Section 7.3 — the validator fails closed |
| `NEG-PEOPLE-007` | new person minted with id `fx-dev-9` | Section 7.1 — identifiers are never reused |
| `NEG-PEOPLE-008` | suspension whose review-by date has passed | Section 7.1 — Red drift |
| `NEG-PEOPLE-009` | new entry carrying `production-approval` at creation | Section 7.1, invariant 79 — new people enter at minimum authority |
| `NEG-ASSIGN-001` | `founder_decision_delegate` whose scope names a promotion decision | Section 10.1, D108, AT-071 |
| `NEG-ASSIGN-002` | assignment granting `people-intelligence` | **AT-090**, **AT-091**, invariant 106 |
| `NEG-ASSIGN-003` | `plan_approval_delegate` with `end_date: null` | Section 10.1, invariant 58 |
| `NEG-EXC-001` | `exceptions.yaml` entry with no expiry | invariant 77, **AT-037** |
| `NEG-EXC-002` | closed exception reopened for the same scope under a fresh id, renewal count reset to 0 | **AT-038** |
| `NEG-INV-001` | an invariant with no enforcement classification; a `mechanical` one naming a check that does not exist; a `policy` one naming no live `policies.yaml` entry | Section 101 preamble |

### 7.2 L2 — pipeline and evidence (gate `PIPELINE-VALIDATE`, `EVIDENCE-CHAIN`)

| Case | Mutation | Must be rejected because |
| --- | --- | --- |
| `NEG-WF-001` | required-check job carries an `if:` condition | Section 33.2 — a skipped job reports a conclusion branch protection counts as satisfied |
| `NEG-WF-002` | required-check workflow behind a path filter | Section 33.2 — a skipped workflow never reports at all |
| `NEG-WF-003` | third-party action pinned by tag instead of full commit SHA | invariant 85 |
| `NEG-WF-004` | reusable workflow consumed by branch ref instead of pinned tag | invariant 85, Section 33.2 |
| `NEG-WF-005` | `verification/contract.yaml` of the form `verify: exit 0`, mapped one-to-one to every requirement, **with no seeded-defect case** | Section 31.2 — a contract that cannot fail is not a contract; raises SIG-18 |
| `NEG-WF-006` | seeded-defect case present but **passing** | Section 31.2 — a run in which the seeded defect passes is a FAILED run |
| `NEG-WF-007` | deployment-record write as a trailing best-effort step rather than a required, failing step | Section 97.2 |
| `NEG-WF-008` | production artifact rebuilt rather than promoted by digest | invariants 22 and 23, Section 32 |
| `NEG-WF-009` | merged PR carrying a `skipped` conclusion on a required context | Section 33.2 — Blocking drift |
| `NEG-WF-010` | evidence chain closed with item 10/11 absent on a `client-app`, and no substituted store-adoption or crash-free evidence | Section 32, 15.7 |

### 7.3 L3 — reconciler, provisioning, drift (gate `RECONCILE`, `DRIFT-VALIDATE`)

| Case | Mutation | Must be rejected because |
| --- | --- | --- |
| `NEG-RECON-000` | the seeded canary removed from the comparison set, so the run reports zero findings | **AT-102**, Section 53.1 — a clean run that missed the canary is a FAILED run, raises SIG-13 |
| `NEG-RECON-001` | comparison set silently narrowed; per-registry comparison counts drop | Section 53.1 — the narrowing is itself visible drift |
| `NEG-RECON-002` | branch-protection JSON differing from the committed template | Section 53.1 — Alert immediately, block deployment |
| `NEG-RECON-003` | a machine identity present in a CODEOWNERS file | Section 53.1 independent control verifier, invariant 18 |
| `NEG-RECON-004` | workflow file changed by a machine identity | Section 53.1 — Blocking regardless of content; Level 4 |
| `NEG-RECON-005` | the Renovate bypass ruleset naming a bypass actor on the ruleset carrying the diff-path check | Section 53.1 — Blocking; D89 |
| `NEG-RECON-006` | `platform.yaml` workflow version against a moved `workflows/*` tag resolving to a different SHA | Section 53.1 — Blocking on any change |
| `NEG-RECON-007` | actual production control **stricter** than declared | **AT-033**, invariant 81 — raise for human review, never relax |
| `NEG-RECON-008` | environment with no deployment branch and tag policy | Section 53.1, D91 |
| `NEG-RECON-009` | declared `infrastructure:` boundary past its attestation window | Section 53.1 — Blocking; Section 40.2 |
| `NEG-RECON-010` | the independent control verifier absent for one cycle | Section 53.1 — Level 5 |
| `NEG-RECON-011` | six writes from the reconciler credential: an Actions secret, an environment, a workflow file, an organisation setting, `records/**`, and Layer B | **AT-110** — all six must fail, and the credential must still complete a normal run |
| `NEG-RECON-012` | a merged registry change applied to the fleet without a clean canary cycle first | Section 26.4, invariant 72, **AT-023**/`AT-024` |
| `NEG-RECON-013` | authority delta — a capability added — with no linked decision record id in the commit | Section 26.4 |
| `NEG-RECON-014` | expired non-employee access still provisioned after the run | Section 53.1 Level 4, **AT-036**, invariant 58 |

### 7.4 L4 — records, events, metrics (gate `RECORD-VALIDATE`, `EVENT-VALIDATE`)

| Case | Mutation | Must be rejected because |
| --- | --- | --- |
| `NEG-EVT-001` | event missing an envelope field (`actor` deleted) | Section 97.3 — rejected at write time |
| `NEG-EVT-002` | `event_type` absent from the `platform.yaml` enum | Section 97.3 — control-plane CI rejects |
| `NEG-EVT-003` | `event_type: "Gate 1 approval"` free text, plus a renamed shipped identifier | Section 97.3 — identifiers, not prose; never renamed once shipped |
| `NEG-EVT-004` | timestamp in runner-local time with no offset | Section 97.1 |
| `NEG-EVT-005` | two events appended to one shared period file | Section 97.3, PARTITION rule 3 |
| `NEG-REC-001` | a record edited in place rather than corrected by a follow-up record | invariant 47, Section 97.2 |
| `NEG-REC-002` | record written without `record_schema_version` | Section 97.2 |
| `NEG-REC-003` | `events/`, `records/deployments/` and `records/uat/` each past their declared write-freshness interval | Section 53.1 — Blocking for exactly these three; Section 97.2 |
| `NEG-REC-004` | deletion-request record with three of four timestamps and no named executor | **AT-105**, Section 97.2 |
| `NEG-REC-005` | production-restore record with no `integrity_check` result and no named verifier | Section 44.5, Section 53.1 — Red |
| `NEG-REC-006` | dashboard metric that names no record store | Section 97.1, invariant 49 |
| `NEG-REC-007` | a derived figure hand-maintained in a committed file | invariant 46 |
| `NEG-REC-008` | support record carrying customer data by copy rather than by identifier | invariant 111, Section 22.2 |
| `NEG-REC-009` | fixture file with no declared provenance, and a manifest entry with no file | Section 38.3 — the fixture-provenance check |
| `NEG-REC-010` | support record closed with a fix shipped and no reply to the customer | **AT-104** |
| `NEG-REC-011` | bootstrap-log entry older than the staleness window | Section 95.4 — Blocking |

### 7.5 L5 — access, infra, ops (gate `ACCESS-VALIDATE`, `INFRA-VALIDATE`)

| Case | Mutation | Must be rejected because |
| --- | --- | --- |
| `NEG-ACC-001` | a self-approved PR | invariant 9, Section 95.4 activation checklist |
| `NEG-ACC-002` | approval from a Read-only holder | Section 95.4 — must not satisfy branch protection |
| `NEG-ACC-003` | approving reviewer is a Write holder who is **not** the routed one | Section 23.2 — the per-PR reviewer-matrix check, not a membership comparison |
| `NEG-ACC-004` | deploy attempted by the actor who granted its production approval | invariant 12, Section 95.4 |
| `NEG-ACC-005` | a machine identity listed as a ruleset bypass actor on `control-plane` | D89, PARTITION repositories table |
| `NEG-ACC-006` | `deploy-production.yml`, `migrate.yml` and the rollback workflow dispatched by the machine account | Section 37.3 actor gate, invariant 18 |
| `NEG-ACC-007` | a privileged workflow resolving to a shared-pool runner label | D87, Section 39.5 — Blocking |
| `NEG-ACC-008` | a self-hosted runner in the `privileged` group registered non-ephemerally | D87 — Blocking |
| `NEG-ACC-009` | a branch-push-triggered workflow admitted to the `privileged` group | D87 — Blocking |
| `NEG-ACC-010` | the people datasource present in the shared Grafana provisioned configuration | **AT-097**, D75, invariant 109 |
| `NEG-ACC-011` | a shared-instance credential used against the Founder-only instance | **AT-098**, D75 |
| `NEG-ACC-012` | four attempts from the ops console's own OS user: a control-plane write, a `records/` write, a board mutation, a Layer B read | **AT-108** — all four must fail, and a Layer A read query must still succeed |
| `NEG-ACC-013` | from inside the background worker container: a non-allowlisted external host, and the Layer B store | **AT-109** — both refused at the host egress layer, not by harness configuration |
| `NEG-ACC-014` | a commit authored by an identity other than the declared bypass actor on a branch merging under that bypass | Section 53.1 — Blocking |
| `NEG-ACC-015` | a peer attempting to read another person's evidence | **AT-096**, invariant 108 |

---

## 8. The fixture canary and the five meta-gates

These are the gates on the gates. They run in the merge train before any lane's own suite is trusted.

### FG-1 — The canary must be rejected

`NEG-CANARY-000` is a permanently planted negative fixture, clearly labelled, present in every full
gate run. It is a `product.yaml` missing `classification.reliability_criticality` **and** carrying a
`support_model: 24x7` with `coverage_window: null` — invalid under Section 15.5 by two independent
routes, so a gate must be very broken to accept it.

A full gate run in which `NEG-CANARY-000` is accepted, or in which it was not evaluated at all, is a
**FAILED run**. It is never repaired, never quarantined, never skipped for speed. This is Section
53.1's seeded-canary rule and AT-102 applied to the build's own instrument.

### FG-2 — Every negative fixture must be rejected; every positive fixture must pass

A negative fixture that passes means the gate stopped discriminating. A positive fixture that fails
means either the fixture or the gate is wrong — both stop the merge train, and neither is resolved by
editing the fixture, which is FROZEN. It is resolved by a Fixture Change Request (§10) or by fixing
the gate.

### FG-3 — Coverage: no gate ships with zero negative fixtures

Every gate id a lane declares must appear in the `must_be_rejected_by` list of at least one negative
fixture. A gate with none is an **unproven gate** and is Blocking. This is Section 103.1's rule —
"zero rejections means the gates are not working" — carried into the build: a plan-checker that has
never rejected anything, and a lane gate that has never rejected anything, are the same defect.

### FG-4 — Counts are recorded, so a silently narrowed suite is visible

Every run writes, per lane and per gate, how many positive fixtures it evaluated and how many negative
fixtures it evaluated and rejected. A count that falls between two runs on `integration` is itself a
finding, exactly as Section 53.1 requires per-registry comparison counts of the reconciler. The counts
go into `records/` as a run record with `record_schema_version`, not into a log nobody reads.

### FG-5 — A negative fixture may not drift into validity

Each negative fixture declares `parent` and `mutation`. The harness asserts that the diff between the
negative artifact and its positive parent is **exactly** the declared mutation. When L0 amends a
positive parent, any negative child whose diff no longer matches fails immediately — which is how a
negative fixture is stopped from quietly becoming a valid document that every gate correctly accepts.

---

## 9. Commands

Literal. Run from the `control-plane` checkout root. `jq` and `yq` are the only external tools.

```bash
# Full fixture gate. Run before every lane PR to integration, and by the merge train.
make fixtures-all
```

`Makefile` targets, owned by L0 (PARTITION: `Makefile` is an L0 root file):

```bash
set -euo pipefail
# 1. Structure and identity: namespaces, one-file-per-fixture, no shared index, provenance.
make fixtures-lint

# 2. Positives pass every gate.
make fixtures-positive

# 3. Negatives are rejected by their named gates; the canary is rejected.
make fixtures-negative

# 4. Every declared gate id is named by at least one negative fixture.
make fixtures-coverage

# 5. Every negative artifact differs from its parent by exactly its declared mutation.
make fixtures-mutate

# 6. Regenerate the run-time index (git-ignored; never committed).
make fixtures-index
```

`fixtures-all` is declared as a Makefile rule with the six targets above as prerequisites, in the same
order:

```makefile
fixtures-all: fixtures-lint fixtures-positive fixtures-negative fixtures-coverage fixtures-mutate fixtures-index
```

No shell composition is needed beyond that declaration: Make's own prerequisite semantics already give
`fixtures-all` its stop-on-first-failure behaviour (a prerequisite that exits non-zero stops the rule
before the next one runs) and its aggregate exit code (`make`'s own exit code is that of the first
prerequisite that failed, or `0` if all six passed).

### 9.1 `fixtures-lint`

```bash
#!/usr/bin/env bash
set -euo pipefail
root="contracts/fixtures"
# The eight lane-local testdata roots this file's own §3 P2 table declares.
lane_roots="validators/registry/testdata tools/evidence/testdata reconciler/testdata validators/drift/testdata tools/records/testdata schemas/records/testdata access/testdata infra/testdata"
fail=0

# A. No shared index may exist anywhere in the corpus (PARTITION rule 3).
if find "$root" -type f \( -name 'fixtures.yaml' -o -name 'index.yaml' -o -name 'index.json' \) | grep -q .; then
  echo "FAIL: a shared fixture index exists; directory-per-item only"; fail=1
fi

# Roots to scan for checks B and D: the L0 corpus plus whichever lane-local
# testdata roots already exist (a lane that has written nothing yet must not
# abort the script for the other four).
scan_roots="$root"
for d in $lane_roots; do
  [ -d "$d" ] && scan_roots="$scan_roots $d"
done

# B. Every fixture directory has exactly one fixture.yaml, with synthetic
#    provenance, a kind of 'positive' or 'negative', and (for negatives) a
#    named gate and a parent. Checked on the L0 corpus AND on every
#    lane-local testdata root — the fixtures lanes actually author, not only
#    the frozen corpus no lane may touch.
while IFS= read -r f; do
  id=$(yq -r '.id' "$f")
  kind=$(yq -r '.kind' "$f")
  prov=$(yq -r '.provenance' "$f")
  [ "$prov" = "synthetic" ] || { echo "FAIL $id: provenance='$prov'; only 'synthetic' is legal (S38.3, inv-111)"; fail=1; }
  case "$f" in
    "$root"/*)
      case "$id" in
        fx-*|NEG-*) ;;
        *) echo "FAIL $id: id outside the L0 namespace under $root"; fail=1 ;;
      esac
      ;;
  esac
  case "$kind" in
    positive|negative) ;;
    *) echo "FAIL $id: kind='$kind'; must be 'positive' or 'negative'"; fail=1 ;;
  esac
  if [ "$kind" = "negative" ]; then
    n=$(yq -r '.must_be_rejected_by | length' "$f")
    [ "$n" -ge 1 ] || { echo "FAIL $id: negative fixture names no gate (FG-3)"; fail=1; }
    [ "$(yq -r '.parent' "$f")" != "null" ] || { echo "FAIL $id: negative fixture declares no parent (FG-5)"; fail=1; }
  fi
done < <(find $scan_roots -name fixture.yaml)

# C. Lane-local testdata ids stay inside their own namespace.
if [ -f contracts/fixtures/ownership.yaml ]; then
  for n in 1 2 3 4 5; do
    while IFS= read -r d; do
      [ -d "$d" ] || continue
      while IFS= read -r f; do
        id=$(yq -r '.id' "$f")
        case "$id" in
          l${n}-*) ;;
          *) echo "FAIL $id in $d: id outside the L$n namespace"; fail=1 ;;
        esac
      done < <(find "$d" -name fixture.yaml)
    done < <(yq -r ".lanes.\"L$n\".testdata_roots[]" contracts/fixtures/ownership.yaml)
  done
else
  echo "FAIL: contracts/fixtures/ownership.yaml not found; cannot check lane-local id namespaces (check C)"; fail=1
fi

# D. No customer data, ever (invariant 111, S96.6 S19 gate) — the L0 corpus
#    and every lane-local testdata root.
if grep -rIlEi '@(gmail|yahoo|outlook|hotmail)\.|[0-9]{12,19}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY' $scan_roots | grep -q .; then
  echo "FAIL: candidate real-data pattern inside the fixture corpus (inv-111)"; fail=1
fi

exit "$fail"
```

### 9.2 `fixtures-negative` — the gate that must be able to fail

```bash
#!/usr/bin/env bash
set -euo pipefail
# The eight lane-local testdata roots this file's own §3 P2 table declares,
# scanned alongside the L0 negative corpus so a lane's own Route A fixtures
# are actually run against their named gate, not only the frozen corpus.
lane_roots="validators/registry/testdata tools/evidence/testdata reconciler/testdata validators/drift/testdata tools/records/testdata schemas/records/testdata access/testdata infra/testdata"
neg_roots="contracts/fixtures/neg"
for d in $lane_roots; do
  [ -d "$d" ] && neg_roots="$neg_roots $d"
done
evaluated=0; rejected=0; canary_seen=0; canary_rejected=0; fail=0

while IFS= read -r f; do
  id=$(yq -r '.id' "$f"); dir=$(dirname "$f")
  [ "$(yq -r '.kind' "$f")" = "negative" ] || continue
  for gate in $(yq -r '.must_be_rejected_by[]' "$f"); do
    evaluated=$((evaluated+1))
    if ./bin/gate "$gate" "$dir" >"/tmp/$id.$gate.out" 2>&1; then
      echo "FAIL $id: gate $gate ACCEPTED a negative fixture — the gate stopped discriminating"
      fail=1
    else
      rejected=$((rejected+1))
      [ "$id" = "NEG-CANARY-000" ] && canary_rejected=1
      want=$(yq -r '.expected_reason_contains // ""' "$f")
      if [ -n "$want" ] && ! grep -qF "$want" "/tmp/$id.$gate.out"; then
        echo "FAIL $id: gate $gate rejected, but not for the declared reason ('$want')"
        fail=1
      fi
    fi
  done
  [ "$id" = "NEG-CANARY-000" ] && canary_seen=1
done < <(find $neg_roots -name fixture.yaml)

# FG-1: the canary must have been evaluated AND rejected.
if [ "$canary_seen" -ne 1 ]; then
  echo "FAIL: NEG-CANARY-000 was not evaluated. A run that did not see the canary is a FAILED run (AT-102, S53.1)."
  fail=1
fi

# FG-4: record the counts so a silently narrowed suite is visible.
# canary_rejected is set only when NEG-CANARY-000 was actually rejected — an
# accepted or unevaluated canary must never be recorded as rejected (FG-1).
printf 'record_schema_version: 1\nid: FXRUN-%s\nevaluated: %s\nrejected: %s\ncanary_rejected: %s\n' \
  "$(date -u +%Y%m%dT%H%M%SZ)" "$evaluated" "$rejected" "$canary_rejected" \
  > "records/fixture-runs/$(date -u +%Y-%m-%d)-$(git rev-parse --short HEAD).yaml"

echo "fixtures-negative: evaluated=$evaluated rejected=$rejected canary=$canary_seen"
exit "$fail"
```

### 9.3 `fixtures-coverage` — no unproven gates

```bash
#!/usr/bin/env bash
set -euo pipefail
# The eight lane-local testdata roots this file's own §3 P2 table declares.
lane_roots="validators/registry/testdata tools/evidence/testdata reconciler/testdata validators/drift/testdata tools/records/testdata schemas/records/testdata access/testdata infra/testdata"
# Every gate id any lane declares must be named by at least one negative fixture.
declared=$(yq -r '.gates[].id' contracts/gates.yaml | sort -u)
[ -n "$declared" ] || { echo "FAIL: contracts/gates.yaml declares zero gates — coverage of nothing is not coverage"; exit 1; }
proven_roots="contracts/fixtures/neg"
for d in $lane_roots; do
  [ -d "$d" ] && proven_roots="$proven_roots $d"
done
proven=$(find $proven_roots -name fixture.yaml 2>/dev/null \
         | xargs -r yq -r '.must_be_rejected_by[]?' | sort -u)
missing=$(comm -23 <(echo "$declared") <(echo "$proven"))
if [ -n "$missing" ]; then
  echo "FAIL: gates with zero negative fixtures — unproven, therefore Blocking (FG-3, S103.1):"
  echo "$missing"
  exit 1
fi
echo "fixtures-coverage: $(echo "$declared" | wc -l) gates, all proven able to fail"
```

### 9.4 `fixtures-mutate` — a negative may not drift into validity

```bash
#!/usr/bin/env bash
set -euo pipefail
# The eight lane-local testdata roots this file's own §3 P2 table declares —
# a Route A negative fixture's drift-from-parent must be checked too, not
# only the L0 corpus.
lane_roots="validators/registry/testdata tools/evidence/testdata reconciler/testdata validators/drift/testdata tools/records/testdata schemas/records/testdata access/testdata infra/testdata"
neg_roots="contracts/fixtures/neg"
for d in $lane_roots; do
  [ -d "$d" ] && neg_roots="$neg_roots $d"
done
fail=0
while IFS= read -r f; do
  [ "$(yq -r '.kind' "$f")" = "negative" ] || continue
  id=$(yq -r '.id' "$f"); parent=$(yq -r '.parent' "$f"); dir=$(dirname "$f")
  pdir=$(find contracts/fixtures/core -type d -name "$parent" | head -n1)
  [ -n "$pdir" ] || { echo "FAIL $id: parent '$parent' not found"; fail=1; continue; }
  actual=$(diff -ru "$pdir" "$dir" --exclude=fixture.yaml | grep -c '^[+-][^+-]' || true)
  declared=$(yq -r '.mutation_line_count // 0' "$f")
  if [ "$declared" -ne 0 ] && [ "$actual" -ne "$declared" ]; then
    echo "FAIL $id: diff from parent is $actual changed lines, declared $declared (FG-5) — the fixture may have drifted into validity"
    fail=1
  fi
done < <(find $neg_roots -name fixture.yaml)
exit "$fail"
```

### 9.5 `fixtures-positive` — every positive fixture must pass every declared gate

```bash
#!/usr/bin/env bash
set -euo pipefail
declared=$(yq -r '.gates[].id' contracts/gates.yaml | sort -u)
evaluated=0; fail=0
while IFS= read -r dir; do
  id=$(basename "$dir")
  while IFS= read -r gate; do
    [ -n "$gate" ] || continue
    evaluated=$((evaluated+1))
    if ! ./bin/gate "$gate" "$dir" >"/tmp/$id.$gate.out" 2>&1; then
      echo "FAIL $id: gate $gate REJECTED a positive fixture — either the fixture or the gate is wrong (FG-2); file an FXR or fix the gate, do not edit the FROZEN fixture"
      fail=1
    fi
  done <<< "$declared"
done < <(find contracts/fixtures/core/products -mindepth 1 -maxdepth 1 -type d)
echo "fixtures-positive: evaluated=$evaluated"
exit "$fail"
```

### 9.6 `fixtures-index` — regenerate the run-time index (git-ignored; never committed)

```bash
#!/usr/bin/env bash
set -euo pipefail
mkdir -p derived
{
  echo '{'
  printf '  "generated_at": "%s",\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo '  "fixtures": ['
  first=1
  while IFS= read -r f; do
    id=$(yq -r '.id' "$f"); kind=$(yq -r '.kind' "$f"); dir=$(dirname "$f")
    [ "$first" -eq 1 ] && first=0 || echo ','
    printf '    {"id": "%s", "kind": "%s", "path": "%s"}' "$id" "$kind" "$dir"
  done < <(find contracts/fixtures -name fixture.yaml 2>/dev/null)
  echo
  echo '  ]'
  echo '}'
} > derived/fixture-index.json
echo "fixtures-index: wrote derived/fixture-index.json (git-ignored; invariant 46)"
```

---

## 10. Adding a fixture without colliding

Two routes. Pick by one question: **does another lane need to see it?**

### Route A — lane-local (default, needs no coordination)

The fixture exercises only your own gate. Write it under your own `testdata/` root, in your own id
namespace. Nothing outside your lane reads it, the lane-guard check confirms placement, and no other
lane can touch the same directory.

```bash
set -euo pipefail
git fetch origin
git checkout -b lane/3/f3-04-drift-fixture-runner-shared-pool origin/integration
mkdir -p reconciler/testdata/neg/DRIFT-VALIDATE/l3-neg-runner-shared-pool
cat > reconciler/testdata/neg/DRIFT-VALIDATE/l3-neg-runner-shared-pool/fixture.yaml <<'YAML'
fixture_schema_version: 1
id: l3-neg-runner-shared-pool
kind: negative
provenance: synthetic
owner: L3
parent: fx-svc-core
mutation: "privileged workflow runs-on changed to the shared-pool label"
mutation_line_count: 2
must_be_rejected_by: [DRIFT-VALIDATE]
expected_reason_contains: "privileged"
cites: ["D87", "Section 39.5", "Section 53.1"]
YAML
# copy the parent artifact and apply exactly the declared mutation, then:
make fixtures-lint fixtures-negative fixtures-mutate
git add reconciler/testdata && git commit -m "$(cat <<'EOF'
test(reconciler): add negative fixture for shared-pool privileged runner

Adds a negative fixture under DRIFT-VALIDATE asserting that a privileged
workflow's runs-on changed to the shared-pool label is rejected.

Task-Id: L3-F3-04
Lane: L3
Phase: F3
Spec: D87, §39.5, §53.1
AT: none
Invariant: none
Agent-Authored: true
Self-Verify: make fixtures-lint fixtures-negative fixtures-mutate
EOF
)"
```

**STOP rule.** `STOP: if make fixtures-lint reports an id outside your namespace, or if git status
shows a modified file outside your lane's OWNS list, do not proceed — open a blocker issue titled
"BLOCKER [L3-F3-04]: <condition>" and make no further commits on this branch.` (canonical form,
`master/09-glossary-and-conventions.md` §7.3). Revert the working tree with `git reset --hard
origin/integration` before filing the issue; your branch will fail the lane-guard check anyway, so
failing it locally is cheaper.

### Route B — shared (a Fixture Change Request to L0)

The fixture must be seen by more than one lane, or it changes anything under `contracts/fixtures/**`.
`contracts/**` is FROZEN and written by L0 only (PARTITION rule 2). A lane never edits it — it files
an FXR, exactly as it files a Contract Change Request.

```bash
set -euo pipefail
gh issue create \
  --repo <org>/control-plane \
  --title "FXR: add negative fixture for <gate-id>" \
  --label "fxr,lane/<N>" \
  --body "$(cat <<'MD'
## Fixture Change Request

**Requesting lane:** L<N>
**Kind:** negative
**Parent fixture:** fx-<parent-id>
**Mutation (exact):** <one sentence; must be mechanically diffable>
**Gate(s) that must reject it:** <GATE-ID>
**Spec citation:** <Section x.y> / <AT-nnn> / <invariant n>
**Why lane-local is insufficient:** <which other lane must also read this fixture>
**Provenance:** synthetic
MD
)"
```

L0 writes the fixture, re-records the corpus digest —

```bash
find contracts/fixtures -type f | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -d' ' -f1 \
  > contracts/gate/FIXTURES.sha256
```

— stating the old and new digests in the FXR, runs `make fixtures-all`, and merges it to
`integration` **before** the lane that requested it merges. Skipping the re-record is not survivable:
`contracts/gate/FIXTURES.sha256` is the digest `lanes/L0-05-integration-gate.md` freezes and
`LG-06`/`IG-03` check on every run, so any fixture change that lands without it flips `fixtures_match`
to `0` and fails the very next gate run. The merge train order of PARTITION (L1 → L4 → L2 → L3 → L5)
is unchanged; FXRs land in L0's own pass ahead of the train.

**Never do these.** Each is a merge conflict or a silent corruption waiting to happen:

| Do not | Because |
| --- | --- |
| Edit any file under `contracts/fixtures/**` from a lane branch | FROZEN; L0 owns it (PARTITION rule 2). The lane-guard check fails the PR. |
| Add a `fixtures.yaml` / index / list of any kind | PARTITION rule 3 — the one file five lanes touch on the same day |
| Commit `derived/fixture-index.json` | invariant 46 — derived data is computed, never hand-maintained; and it regenerates differently per lane |
| Repair, quarantine or skip `NEG-CANARY-000` | FG-1 — that is the exact failure the canary exists to detect |
| Fix a failing positive fixture by editing the fixture | FG-2 — either the gate is wrong or the fixture is; file an FXR, do not edit FROZEN data |
| Weaken a negative fixture until the gate passes it | FG-2/FG-5 — this converts a real gate into a decorative one |
| Put anything but `provenance: synthetic` in the corpus | Section 38.3, invariant 111, S19 (Section 96.6) — there is no remedy after the fact |
| Reuse a fixture person id after marking one departed | Section 7.1 — identifiers are never reused; `NEG-PEOPLE-007` proves it |

---

## 11. Merge-train obligations

Before a lane's PR to `integration` is eligible:

1. `make fixtures-all` passes on the lane branch rebased on `integration`.
2. `make fixtures-coverage` shows **zero** unproven gates for the gates that lane declares (FG-3).
3. The run record in `records/fixture-runs/` shows a negative-evaluation count **not lower** than the
   previous run on `integration` for that lane (FG-4). A drop is a finding, not a speed-up.
4. `NEG-CANARY-000` is recorded as evaluated and rejected (FG-1).

Before `integration` → `main`:

5. All five lanes' gates have run against the full shared corpus, not only their own `testdata/`.
6. Every AT- identifier cited in this file has an executed result — AT-003, AT-008, AT-009, AT-010,
   AT-017, AT-018, AT-023, AT-024, AT-033, AT-036, AT-037, AT-038, AT-047, AT-048, AT-049, AT-071,
   AT-090, AT-091, AT-096, AT-097, AT-098, AT-102, AT-103, AT-104, AT-105, AT-108, AT-109, AT-110 —
   executed for real, never assumed, on the Section 95.4 standard: the checklist is executed
   including the negative tests, not assumed.

**STOP rule for the integrator.** `STOP: if the full gate run reports zero rejections across the
entire negative corpus, do not proceed — open a blocker issue titled "BLOCKER [<task-id>]: full gate
run reported zero rejections" and make no further commits on this branch.` (canonical form,
`master/09-glossary-and-conventions.md` §7.3). Do not merge and do not celebrate: zero rejections
means the harness is not running the negatives. Run `make fixtures-negative` alone and confirm the
evaluated count is non-zero before anything else is believed.
