# 01 — Cross-Lane Contract Tests

**Owner:** L0 Integrator. **Status:** binding on all five lanes.
**Scope:** the tests that catch two lanes diverging. Nothing else.

This document governs `contracts/**` — written by L0 in Phase 0 and FROZEN (PARTITION.md rule 2).
No lane may edit `contracts/**`, `contracts/fixtures/**` or `contracts/harness/**`. That restriction is
the whole point: a lane cannot be judged by a test it can rewrite.

---

## 0. Why this file exists

Five AI developers build in parallel. None has full context. Each one can produce a lane that is
internally consistent, fully green on its own tests, and wrong at every edge where it meets another
lane. Lane-local tests cannot see that. Only a test that holds *both sides of a boundary at once*
can, and that test must live outside both lanes.

The failure this file is designed to catch is not a crash. It is silence: L2 writes
`event_type: plan-approved`, L4's enum says `plan_approved`, both lanes pass their own suites, and
every metric derived from Gate 1 reads zero forever. The spec names that exact failure in
Section 97.3 and calls it splitting "every metric derived from it, silently."

---

## 1. The governing rule

> **A check that can only pass is not a check.**

This is the specification's own position, applied in at least four places, and every gate below
inherits it:

| Spec anchor | The rule as the spec states it |
| --- | --- |
| Section 53.1, seeded-canary rule | A permanent, deliberately planted mismatch exists at all times and every run MUST find it. A run reporting zero findings — the canary included — is a **FAILED** run, not a clean one |
| AT-102 | A reconciler that finds nothing is assumed broken, never assumed clean; raises SIG-13 and triggers the gap procedure |
| EC-109 | A run that completes "clean" while checking nothing — broken query, empty enumeration — is exposed by the canary. Silence is never taken as health |
| Section 103 (review-rejection-rate row) | "Very low may mean rubber-stamping; very high may mean weak plans" |
| Section 95.4 | The activation checklist is "executed for real — including the negative tests — at each threshold, not assumed" |
| AT-108 / AT-109 / AT-110 | The spec's own template for a proven gate: N attempts that MUST fail, followed by one operation that MUST succeed. Both halves, executed, never asserted |

**Consequences, binding on this protocol:**

1. Every contract test ships as a **triple** — producer conformance, consumer compatibility, and a
   negative proof that the pair can actually go red.
2. A contract with no exercised negative proof is a **dead gate** and is Blocking-class drift
   against the harness itself, not against any lane.
3. The suite records **how much it compared**, not only its verdict — the direct analogue of
   Section 53.1's per-registry comparison counts, so a silently narrowed suite is itself visible.
4. A full merge cycle that passes with zero failures **and** zero negative-proof executions is the
   rubber-stamping condition, and forces the mutation drill (§7.2).

---

## 2. The shape of a contract test

Every contract in `contracts/` gets exactly three test classes. All three are required; a contract
carrying only the first two does not ship.

| Class | ID form | Question it answers | Runs against |
| --- | --- | --- | --- |
| **Producer** | `P-<id>` | Does the lane that publishes this contract actually emit what the contract says? | The producer lane's real implementation, on the frozen valid corpus and the frozen invalid corpus |
| **Consumer** | `C-<id>.<lane>` | Does the lane that depends on this contract still work against it? | The consumer lane's real implementation, on the frozen corpus and on the producer's live output once it exists |
| **Negative** | `N-<id>` | Can this pair go red at all? | A frozen violation the suite MUST report. If it is reported as passing, the instrument is broken |

**The producer corpus is two-sided.** `valid/` instances the producer MUST accept or emit;
`invalid/` instances the producer MUST **reject**, each carrying a `# violates:` header naming the
exact rule id. A validator that accepts everything is not a validator, and the `invalid/` corpus is
what proves it is not one.

**The consumer test is fail-closed.** Feed the consumer an `invalid/` instance and the consumer must
error, refuse, or block — never continue with a default. Invariant 80 requires every control to be
explicitly classified fail-closed or fail-open; a consumer that silently degrades on malformed
contract input fails `C-<id>` regardless of what it does on good input.

---

## 3. The contract register

Twelve contracts. Each names one producer lane (two, where the spec splits the artifact) and its
consumers. Merge-train order is L1 → L4 → L2 → L3 → L5 (PARTITION.md).

| ID | Contract file under `contracts/` | Producer | Consumers | Spec anchor |
| --- | --- | --- | --- | --- |
| C-01 | `C-01-registry-schema.contract.yaml` | **L1** | L2, L3, L4, L5 | §99.2 A+B, §15, §60.2 |
| C-02 | `C-02-validator-cli.contract.yaml` | **L1** | L2, L3 | §99.2 B |
| C-03 | `C-03-record-envelope.contract.yaml` | **L4** | L2, L3, L5 | §97.1, §97.2 |
| C-04 | `C-04-event-envelope.contract.yaml` | **L4** (envelope) + **L1** (`platform.yaml` enum) | L2, L3, L4, L5 | §97.3, §60.2 |
| C-05 | `C-05-workflow-interface.contract.yaml` | **L2** | L3, L5 | §99.2 E, §33 |
| C-06 | `C-06-status-check-names.contract.yaml` | **L2** | L5, L3 | §53.1, D101 |
| C-07 | `C-07-access-model.contract.yaml` | **L5** | L3, L1 | §90, §53.1, §37.3 |
| C-08 | `C-08-drift-finding.contract.yaml` | **L3** | L4, L5 | §53.1–§53.4, AT-102 |
| C-09 | `C-09-metric-source.contract.yaml` | **L4** | L2, L3, L5 | §97.1, §97.2 |
| C-10 | `C-10-notification.contract.yaml` | **L5** | L2, L3, L4 | §92.11 |
| C-11 | `C-11-secret-tiers.contract.yaml` | **L5** | L2, L3 | §40.1, §40.3, D89 |
| C-12 | `C-12-version-floor.contract.yaml` | **L1** | L2, L3, L4, L5 | §60.1, §60.2 |

Note the five cross-lane dependencies — **C-07, C-10, C-11 are produced by L5, which merges last, and consumed
by L3, which merges before it**; C-05 and C-06 are produced by L2 and consumed by L3 and L5 during development.
These dependencies are legal only because of the fixture strategy in §5. Without it they are the exact place
two lanes diverge in silence.

---

## 4. Per-contract test specifications

Each entry gives the producer test, the consumer tests, the negative proof, and the literal command
that runs that contract alone.

### C-01 — Registry and product schemas (L1 → all)

| | |
| --- | --- |
| **Contract surface** | `schemas/registry/**`, `schemas/product/**` shapes; required fields; referential rules |
| **P-01** | L1's validator accepts all of `contracts/fixtures/C-01/valid/` and rejects **all** of `invalid/`, emitting the rule id named in each fixture's `# violates:` header. A rejection with the wrong rule id fails. |
| **C-01.L2** | The CI reusable workflow reaches the *same verdict* as L1's validator on the whole corpus. L2 must not reimplement validation — a second implementation is a divergence generator. |
| **C-01.L3** | `tools/provision/create-product` output validates under L1's validator **unmodified**. Covers AT-001 (add product 21 is scaffolding plus onboarding) and invariant 52 (product count never hard-coded). |
| **C-01.L4** | Every registry field a metric reads exists in the schema (invariant 46, invariant 49). |
| **C-01.L5** | Every team and role name in `access/**` resolves against `registries/roles.yaml`. |
| **N-01** | `invalid/_canary-onboarded-without-verification-contract.yaml` — invariant 1. Any lane that accepts it fails. Also carries AT-047 (`coverage_window` not covered by rota members fails contract validation) and AT-049 (`ai_runtime_dependency` with no suite under `verification/`) as separate `invalid/` cases. |

```bash
bash contracts/harness/run-contract-tests.sh --contract C-01
```

### C-02 — Validator CLI interface (L1 → L2, L3)

The argv, exit codes and JSON report shape of L1's validator, because L2 and L3 shell out to it.

| | |
| --- | --- |
| **P-02** | The validator's `--help` surface and JSON report match `contracts/C-02-validator-cli.contract.yaml` field for field; exit codes are exactly `0` pass, `1` schema violation, `2` referential violation, `3` input not found. |
| **C-02.L2 / C-02.L3** | Each caller is invoked against the frozen corpus and must branch correctly on all four exit codes. A caller that treats any non-zero as a generic failure fails: it cannot distinguish "your file is wrong" from "I could not find your file", and that distinction is what stops a missing input reading as a clean run (EC-109 in miniature). |
| **N-02** | A stub validator that always exits `0` is substituted on `PATH`; both consumer tests MUST go red. If they stay green, the consumers are not reading exit codes at all. |

```bash
bash contracts/harness/run-contract-tests.sh --contract C-02
```

### C-03 — Record envelope (L4 → L2, L3, L5)

| | |
| --- | --- |
| **Contract surface** | §97.2: every record carries `record_schema_version`, `id`, `product`, `timestamp`; UTC with offset; never edits in place — corrections are follow-up records (invariant 47) |
| **P-03** | L4's schemas validate the golden corpus; reject a record with a local-time timestamp; reject a second record reusing an existing `id` with different content (the append-only test). |
| **C-03.L2** | The deployment record emitted by `deploy-production.yml` validates. **And the write is a failing step**: the harness points the writer at an unwritable path and asserts the deploy workflow **fails**. §97.2 is explicit — a deploy whose record cannot be written is a deploy whose evidence chain does not close, and the eleven questions of §32 are unanswerable for it afterwards. A trailing best-effort write fails this test. |
| **C-03.L3** | The reconciliation run record validates (see also C-08). |
| **C-03.L5** | Asset-expiry and notification records validate. |
| **N-03** | `invalid/_canary-record-edited-in-place.yaml` must be rejected by L4's schema **and** must cause every consumer writer to refuse. Covers invariant 47 and AT-088 (source re-read failure never downgrades verified data). |

```bash
bash contracts/harness/run-contract-tests.sh --contract C-03
```

### C-04 — Event envelope and the `event_type` enum (L4 + L1 → all four writers)

This is the highest-value contract in the register. Four lanes write events; the envelope schema is
L4's; the enum lives in `platform.yaml`, which is L1's. Two producers, four consumers, one
identifier namespace.

| | |
| --- | --- |
| **P-04a** | L4's envelope schema rejects an event missing any of `event_schema_version`, `event_id`, `event_type`, `occurred_at`, `recorded_at`, `actor`, `product`. §97.3: an event missing any envelope field is rejected **at write time**. |
| **P-04b** | L1's `registries/platform.yaml` enum is a superset of the frozen taxonomy in `contracts/C-04-event-types.txt`. Retired identifiers are marked retired and **never removed** — the events carrying them are append-only and stay readable. |
| **C-04.all** | Static extraction of every literal `event_type` value from `.github/workflows/**` (L2), `reconciler/**` (L3), `tools/records/**` (L4) and `notify/**`, `ops-vm/**` (L5). Every extracted value must appear in the enum. Every enum value with no writer is reported as an unwritten type — not a failure, but recorded, because a type nothing emits makes its metric read zero. |
| **N-04** | `contracts/fixtures/C-04/canary/emit-bad-type.sh` emits `plan-approved` (hyphen). The suite MUST report it. If the extraction pass returns clean while the canary emitter is present, the extractor stopped looking — INSTRUMENT FAILURE, exit 3, not a lane failure. |

```bash
bash contracts/harness/run-contract-tests.sh --contract C-04
```

### C-05 — Reusable workflow interface (L2 → L3, L5)

| | |
| --- | --- |
| **Contract surface** | The `workflow_call` inputs, secrets and outputs of the eight workflows of §99.2 E: `ci`, `build`, `deploy-staging`, `deploy-production`, `migrate`, `restore-test`, `org-export`, `background-queue` |
| **P-05** | Each workflow's `workflow_call` block matches the contract exactly — no undeclared required input, no silently removed one. |
| **C-05.L3** | Caller files generated by `tools/provision/**` reference only declared inputs **and pin by tag** (invariant 85: reusable workflows consumed by pinned tag). A caller on `@main` fails. |
| **C-05.L5** | `infra/**` and `ops-vm/**` schedules invoke only declared inputs; third-party actions pinned to full commit SHAs (invariant 85). |
| **N-05** | `invalid/caller-undeclared-input.yml` and `invalid/caller-mutable-ref.yml` must both fail. |

```bash
bash contracts/harness/run-contract-tests.sh --contract C-05
```

### C-06 — Required status check names (L2 → L5, L3)

The contract D101 exists to prevent: branch protection requiring status checks before any workflow
emitted them.

| | |
| --- | --- |
| **P-06** | L2 publishes the exact set of job names its `pull_request`-triggered workflows emit, as `contracts/C-06-status-check-names.contract.yaml`. |
| **C-06.L5** | Every entry in `access/branch-protection/branch-protection.yaml`'s `required_status_checks.catalogue` appears in that set. A required check nobody emits blocks every PR forever and is indistinguishable, at the lane level, from a broken lane. |
| **C-06.L3** | The reconciler's declared-vs-actual comparison for branch protection (§53.1 row: *Branch protection template / Actual branch protection / **Alert immediately; block deployment on the affected repository***) reads the same names from the same file. Both directions are asserted: no orphan requirement, no unrequired gate. |
| **N-06** | `invalid/protection-requires-phantom-check.yaml` requires `verify-digest-chain` while no `pull_request` workflow emits it. The suite MUST fail. This is the one negative proof that maps to a real, already-observed failure mode (D101). |

```bash
bash contracts/harness/run-contract-tests.sh --contract C-06
```

### C-07 — Access model and CODEOWNERS generation (L5 → L3, L1)

| | |
| --- | --- |
| **P-07** | `access/model/organisation.yaml`, `access/model/owner-continuity.yaml`, `access/model/permission-semantics.yaml` and `access/model/teams.yaml` all validate; **every control carries an explicit `fail_closed: true\|false`** — invariant 80, and an unclassified control is rejected by the §99.2 B gate engine. Secret tiers enumerate exactly five (§40.1). |
| **C-07.L3** | The CODEOWNERS renderer (`tools/provision/provision/codeowners/render.py`, exercised via `python -m provision create-product` step `cp-04-codeowners`, or directly through the `tests/test_codeowners_render.py` golden-file suite) run against the frozen registry fixtures produces **byte-identical** output to `contracts/fixtures/C-07/expected/CODEOWNERS`. Byte-identical, because §53.1 has reconciliation regenerate this file and alert if hand-edited — a generator whose output drifts by a comment makes every subsequent run report false drift. |
| **C-07.L3b** | **No machine identity appears in any generated CODEOWNERS.** This is the machine-authority wall of §37.3 and the assertion the independent control verifier of §53.1 makes from off the operations VM under a different credential. Invariant 18. |
| **C-07.L1** | Registry role names referenced by the access model exist and are not departed. |
| **N-07** | `invalid/registry-with-records-writer-as-owner.yaml` names the records-writer machine credential as a product owner. The CODEOWNERS renderer MUST fail — not warn, not filter it out silently. A generator that quietly drops the entry hides the registry defect that produced it. |

```bash
bash contracts/harness/run-contract-tests.sh --contract C-07
```

### C-08 — Drift finding and reconciliation run record (L3 → L4, L5)

| | |
| --- | --- |
| **Contract surface** | Finding fields: `class` ∈ {Green, Amber, Red, Blocking} — §53.4 states there is exactly one drift severity scale and **no other severity vocabulary exists anywhere in this system**; `level` ∈ 1–5 (§53.2); `acknowledged_by`, `acknowledged_at`; run-record fields `per_registry_comparison_counts`, `canary_found`, optional `external_cause` |
| **P-08** | The schema **rejects a run record with `findings: 0` and `canary_found: false`**. That record is a FAILED run, not a clean one (AT-102, §53.1, EC-109). It also rejects any severity token outside the four-value scale — a lane inventing `critical` or `warning` splits every drift metric. |
| **C-08.L4** | The metric layer computes SIG-13 from the run-record store. A run record it cannot parse must raise, never read as zero findings (AT-032, self-observability). |
| **C-08.L5** | `notify/routing/*.yaml` has a route for each of the four classes; Blocking routes to a pushed event under the §92.11 notification contract. |
| **N-08** | `contracts/fixtures/C-08/canary/run-zero-findings.yaml` — a syntactically perfect run record claiming a clean sweep with the canary unfound. Producer schema MUST reject it; consumer metric MUST surface it as a failed run. If either reports it healthy, that lane has reimplemented the exact failure AT-102 exists to prevent. |

```bash
bash contracts/harness/run-contract-tests.sh --contract C-08
```

### C-09 — Metric source declaration (L4 → L2, L3, L5)

§97.1: "every dashboard metric names the record store it derives from. A metric that cannot name its
store does not ship." Invariant 49: "Every operating-system metric has an owner and a defined
response, or it is deleted."

| | |
| --- | --- |
| **P-09** | Every metric in `metrics/**` declares `store`, `owner`, `response`, and a `write_freshness_interval` for its store. Any metric missing one fails. |
| **C-09.all** | For every declared store, at least one **other lane** declares a writer for it. A store with a reader and no writer is an orphan metric that will render zero and be indistinguishable from health — §97.2 names this precisely: a silently failing record write "renders every count-shaped derived metric as zero … which is indistinguishable from health". Blocking for `events/`, `records/deployments/` and `records/uat/` per §53.1. |
| **N-09** | `invalid/metric-names-nonexistent-store.yaml` and `invalid/metric-with-no-owner.yaml` must both fail. Plus `invalid/metric-store-with-no-writer.yaml` — the divergence case: L4 built the dashboard, L2 never wrote the store. |

```bash
bash contracts/harness/run-contract-tests.sh --contract C-09
```

### C-10 — Notification contract (L5 → L2, L3, L4)

| | |
| --- | --- |
| **P-10** | Every file under `notify/routing/*.yaml` validates; every paging route names an armed signal. §92.11 and §97.3 both require a new event type to be a **governed addition** before anything may page a person. |
| **C-10.all** | Every notification any lane emits names a route id declared under `notify/routing/*.yaml`. An undeclared route id is a notification that goes nowhere. |
| **N-10** | `invalid/emitter-undeclared-route.yml` must fail. Second negative: a route declared as paging against an **unarmed** signal must fail — §52.2 arming discipline; an unarmed signal cannot breach, so a page wired to one can only ever be silence. |

```bash
bash contracts/harness/run-contract-tests.sh --contract C-10
```

### C-11 — Secret tiers and credential bounds (L5 → L2, L3)

| | |
| --- | --- |
| **P-11** | The five tiers of §40.1 are enumerated; each carries an owner, a rotation cadence and an **expiry date** (§97.2 requires the expiry, not only the cadence, so the 30-day asset alert of §49 fires on it). |
| **C-11.L2** | No workflow references a secret from a tier it is not entitled to. The records-writer credential's `contents: write` is scoped to the records repository alone and reaches **no registry at all** (D89). |
| **C-11.L3** | The reconciler credential's declared scopes exclude, statically: Actions secrets, environments, workflow files, `records/**`, and any Layer B path. This is the static half of AT-110 — the executed half (six attempts that fail, then a normal run that completes) belongs to the runtime gate, not to this suite, and this suite asserts only that the *declaration* never widens. Also asserts no machine bypass actor exists on `control-plane` (PARTITION.md, D89). |
| **N-11** | `invalid/workflow-references-reconciler-credential.yml` must fail. `invalid/records-writer-with-registry-scope.yaml` must fail. |

```bash
bash contracts/harness/run-contract-tests.sh --contract C-11
```

### C-12 — Version floor and multi-version support (L1 → all)

Invariant 73 and AT-025: contract schemas are versioned, both versions supported simultaneously,
**simultaneous fleet migration is never required.**

| | |
| --- | --- |
| **P-12** | `registries/platform.yaml` `supported_contract_versions` lists every version any lane emits. |
| **C-12.all** | Every schema and writer in every lane declares a version present in that list. |
| **C-12.multiversion** | **Every validator accepts every supported version, not only the current one.** The corpus holds a v1 instance and a v2 instance of each versioned contract; both must validate while both are supported. |
| **N-12** | This is the subtle one. `invalid/_canary-v1-dropped.yaml` is a valid v1 instance. If a lane has quietly dropped v1 support while `platform.yaml` still declares it supported, this fixture fails validation and the suite reports it. Without this negative the multi-version test is exactly a check that can only pass: a validator that only ever sees current-version input passes forever while the fleet-migration invariant has already been broken. |

```bash
bash contracts/harness/run-contract-tests.sh --contract C-12
```

---

## 5. Fixture strategy — how a consumer lane develops before the producer ships

The merge train is L1 → L4 → L2 → L3 → L5. Five contracts run against that order (C-05, C-06, C-07,
C-10, C-11). L3 must build the reconciler and provisioning against L5's access model, secret tiers
and notification routes weeks before L5 merges anything. That is not a scheduling problem to be
solved by waiting; it is the reason `contracts/**` is frozen in Phase 0.

### 5.1 The tree

```
contracts/
  register.yaml                        # every contract, producer, consumers, mutation, counts
  C-01-registry-schema.contract.yaml   # …one per contract
  C-04-event-types.txt                 # the frozen §97.3 taxonomy
  fixtures/
    C-07/
      valid/access-model-minimal.yaml
      valid/access-model-full.yaml
      invalid/registry-with-records-writer-as-owner.yaml   # violates: INV-018
      invalid/control-without-failclosed.yaml              # violates: INV-080
      expected/CODEOWNERS                                  # byte-exact generator target
      stub/emit-access-model.sh                            # runnable fake producer
      MANIFEST.yaml                                        # provenance, frozen_at, contract_version
    _canary/
      C-04-emit-bad-type.sh
      C-08-run-zero-findings.yaml
      C-12-v1-dropped.yaml
  harness/
    run-contract-tests.sh
    expected-counts.tsv                # the comparison-count baseline
    mutations/                         # one real violating diff per contract
```

### 5.2 The stub producer

Every contract ships a `stub/` — a runnable script that emits a frozen valid instance. A consumer
lane runs its full loop against stubs from day one:

```bash
make stub-env
# materialises every contract stub into .contract-stubs/ and prints the exported paths
# e.g. CONTRACT_ACCESS_MODEL=.contract-stubs/C-07/access-model-full.yaml
```

```bash
set -euo pipefail
# L3, week 1, with nothing of L5 merged anywhere:
make stub-env
CONTRACT_ACCESS_MODEL=.contract-stubs/C-07/access-model-full.yaml \
  python -m reconciler.cli run --fixture fixture-a --summary
bash contracts/harness/run-contract-tests.sh --contract C-07 --side consumer --lane L3
```

The consumer test is green on stubs. That is a real signal — it proves the consumer conforms to the
frozen contract — and it is explicitly **not** a claim that the producer has shipped. The suite
reports the distinction in its output: `C-07.L3 PASS (against stub)` versus
`C-07.L3 PASS (against live producer)`. A cycle in which a contract has only ever been exercised
against stubs is reported at the bottom of every run, so "we never actually met" is never invisible.

### 5.3 Four rules that make fixtures safe

1. **A consumer lane never hand-writes a fixture for another lane's contract.** A locally invented
   fixture is precisely the mechanism by which two lanes diverge: the consumer encodes its guess,
   passes its own tests, and meets reality at merge. The lane-guard check fails any file under a
   lane-owned `**/fixtures/**` path unless it is registered in `register.yaml` under
   `lane_local_fixtures:` as a lane-internal unit fixture with no cross-lane meaning.
2. **The fixture is the contract; code moves to the fixture, never the reverse.** When the producer
   ships and its output disagrees with the fixture, the fix is on the producer side or it is a
   Contract Change Request to L0. Editing a fixture to match code that just broke it converts the
   gate into a check that can only pass, permanently, and does so in a one-line diff that reads as
   housekeeping. `contracts/**` is CODEOWNERS-protected to L0 for this reason alone.
3. **Every fixture declares provenance.** `MANIFEST.yaml` carries `fixture_provenance: synthetic`
   for every file. Invariant 111 forbids customer data in git and names fixtures explicitly — "not
   in fixtures, not in support records, not in incident evidence" — and this suite enforces the same
   rule for `contracts/fixtures/**`, modelled on §38.3's shape (§38.3 itself binds only
   `verification/ai-eval/fixtures/`): a fixture with no provenance declaration is a CI failure here
   too. History is append-only, so this is the one prohibition with no remedy after the fact. The
   suite fails on a fixture file with no manifest entry and on a manifest entry with no file.
4. **A fixture that is never exercised is an unproven fixture.** Each fixture carries `frozen_at` and
   a per-cycle exercise count. `--fixture-parity` fails a fixture untouched for a full cycle: an
   unrun fixture is a check that cannot fail because it never runs at all.

### 5.4 Parity — the handoff from stub to live producer

The moment a producer lane merges to `integration`, its stub stops being the reference:

```bash
bash contracts/harness/run-contract-tests.sh --fixture-parity
```

This re-validates every fixture against the **real** producer implementation and compares the stub's
output against the producer's output field by field. Divergence is **Blocking** and stops the train
(§6). It is triaged as a contract question, never patched at the fixture:

| Parity outcome | Resolution | Who acts |
| --- | --- | --- |
| Producer disagrees with the frozen contract | Producer lane fixes the producer | Producer lane |
| Consumer built against a misread of the contract | Consumer lane fixes the consumer | Consumer lane |
| The contract itself is wrong or under-specified | Contract Change Request; L0 edits `contracts/**`; every consumer re-runs | L0 only |
| Stub drifted from the contract | L0 regenerates the stub from the contract | L0 only |

---

## 6. Instrument integrity — the suite proving it is still looking

Two mechanisms, both lifted directly from §53.1, applied to this harness rather than to the
reconciler.

### 6.1 The seeded canary

`contracts/fixtures/_canary/` holds a permanent, clearly labelled set of violations — one per
high-risk contract. **Every full run MUST report every one of them.** A run that reports zero
findings, canary included, is a FAILED run: it proves the harness stopped looking, not that the
lanes agree.

The verdict is separated from lane failures by exit code, because they demand different responses:

| Exit | Verdict | Meaning | Response |
| --- | --- | --- | --- |
| 0 | `PASS` | All producer and consumer tests green, all canaries reported, counts at baseline | Train proceeds |
| 1 | `CONTRACT-FAILURE` | Two lanes diverge | Train frozen (§7) |
| 2 | `FIXTURE-PARITY-FAILURE` | Producer disagrees with the frozen fixture | Train frozen (§5.4) |
| 3 | `INSTRUMENT-FAILURE` | A canary was not reported, or comparison counts shrank | **Train frozen and no lane result from this run is evidence for anything.** Level 5 escalation (§53.2) |
| 4 | `HARNESS-ERROR` | The suite could not run | Treated as exit 3. A suite that cannot run is not a suite that passed |

Exit 3 is the strictest state in this protocol. A green suite whose canary went unreported is worse
than a red one, because it is a green light with nothing behind it.

### 6.2 Comparison counts

§53.1 requires every reconciliation run to record its per-registry comparison counts "so that a
silently narrowed comparison is itself visible drift." The suite does the same. Every run prints,
and diffs against `contracts/harness/expected-counts.tsv`:

```
C-01  valid=7   invalid=5   consumers=4  canaries=1
C-04  valid=3   invalid=4   consumers=4  canaries=1
...
```

A count **below** baseline is exit 3, not a warning. Counts rise only through an L0 commit to
`expected-counts.tsv` accompanying the new fixtures. A lane cannot shrink the suite by deleting a
fixture; the deletion shows up as a narrowed comparison before it shows up as a passing run.

Machine-readable last line, always:

```
CONTRACT-SUITE: PASS contracts=12 producer=12/12 consumer=27/27 negative=41/41 canary=6/6 counts=OK
```

---

## 7. The negative-proof suite

### 7.1 Standing negative proofs

`--negative-proof` runs every `N-<id>` and asserts each turns its pair red. It is part of the full
run, not an optional extra. A contract whose negative proof passes the suite (i.e. the violation was
*not* caught) is reported as `DEAD-GATE` and exits 3 — the gate exists, runs, reports green, and
cannot fail. That is the condition this whole protocol is built to detect.

```bash
bash contracts/harness/run-contract-tests.sh --negative-proof
```

### 7.2 The mutation drill

Standing negatives prove the fixtures are checked. The mutation drill proves the **lanes' real code**
is checked. `contracts/harness/mutations/` holds one real violating diff per contract — a patch that
makes the producer emit a wrong field, or the consumer accept a bad one.

```bash
bash contracts/harness/run-contract-tests.sh --mutation-drill
```

For each contract: apply the mutation in a scratch worktree, run that contract's tests, assert the
verdict is red, revert. A mutation that leaves the suite green means that contract's tests never
touch the code path they claim to cover. That is Blocking against the harness.

**When the drill is mandatory.** At every `integration` → `main` promotion, and additionally whenever
a full merge cycle completes with **zero contract-test failures and zero negative-proof executions**.
That combination is the rubber-stamping condition — the spec's own reading of a suspiciously clean
gate: "very low may mean rubber-stamping" (§103 review-rejection-rate row), "a reconciler that finds
nothing is assumed broken, never assumed clean" (AT-102). Five lanes with no shared context do not
agree perfectly for a whole cycle. A cycle that says they did is a claim about the instrument.

### 7.3 Every divergence becomes a permanent fixture

Invariant 2 — every production bug becomes a permanent regression test — applies here without
amendment. Every real divergence this suite catches is added by L0 to the relevant `invalid/`
corpus, with its `# violates:` rule id, before the fix merges. `expected-counts.tsv` rises by one.
The suite is designed to get stricter every cycle; a suite whose counts never rise is a suite that
never caught anything.

---

## 8. The merge-train blocking rule

> **A contract test failure blocks the merge train, not one lane.**

### 8.1 Why the train and not the lane

A contract failure is a statement about a *relation between two lanes*, not about a location. When
L2 emits `plan-approved` and L4's enum says `plan_approved`, the failure signature is identical
whichever side is wrong, and nothing in the failure tells you which. Blocking only the lane that
happened to be merging teaches everyone that the other side was fine — which is exactly the
half-diagnosis that lets a divergence survive into `main`. So:

1. On exit 1, 2, 3 or 4, **`integration` is frozen.** No lane merges. Not the failing lane, not the
   four uninvolved ones.
2. The finding is recorded as **Blocking**-class drift (§53.4). Blocking has no budget and no
   response-time negotiation: response is immediate, and it blocks work by definition.
3. **L0 triages within one business day** and the outcome is exactly one of the four rows in §5.4.
   Only L0 may conclude that the contract, rather than a lane, was wrong.
4. The train restarts from the top of the order (L1 → L4 → L2 → L3 → L5), not from where it stopped.
   A lane that merged earlier in the same cycle re-runs the suite, because the fix may have moved
   the boundary underneath it.

### 8.2 What no lane may do

| Forbidden | Why |
| --- | --- |
| Edit `contracts/**`, `contracts/fixtures/**`, `contracts/harness/**` | The gate would then be writable by the party it judges. CODEOWNERS-enforced to L0; the lane-guard check fails the PR |
| Add `continue-on-error`, `if: always()`, or `\|\| true` around the contract gate | Converts the gate to a check that can only pass. Any such change to the gate's invocation is Blocking |
| Delete or narrow a fixture | Caught by the comparison-count baseline as exit 3 before it is caught as a green run |
| "Fix" a failing contract test by changing the expected value | This is the single most likely wrong move an unsupervised lane makes. It is why §5.3 rule 2 exists |
| Merge past a red suite because "it's the other lane's problem" | It is not knowable from the failure whose problem it is (§8.1) |

### 8.3 The only bypass

A dated entry in `exceptions.yaml`, opened by L0, carrying a **mandatory expiry** (invariant 77: an
exception without one is invalid and fails CI), a named owner, a deactivation trigger, and a named
compensating control whose executions land in a named store on a named cadence (§54). On expiry it
becomes Blocking drift and appears on the Founder view (AT-037). A same-scope exception reopened
after closure counts as a renewal; a fresh id does not reset the count (AT-038).

**Never available for exit 3.** An instrument failure cannot be waived, because a waiver against a
broken instrument waives an unknown quantity. §53.7's gap procedure applies instead: treat the window
since the last known-good run as unverified rather than presumed clean, re-run all checks, confirm the
canaries, and mark every result produced in that window `gap-window` until re-verified.

### 8.4 STOP rules for lane developers

Written for the reader PARTITION.md describes — no repo context, no judgment authority. Every
blocker filed from this section uses the template at master/09 §7.1 verbatim — no other title,
label set, or body shape is valid.

**Title:** `BLOCKER [<task-id>]: <one line, imperative, ≤ 60 chars>`
**Labels:** `blocker`, `lane/<N>`, `phase/<phase-lower>`
**Body:**

```markdown
## Task
<task-id>

## STOP condition that fired
<the exact sentence from the task file>

## What I observed
<the exact command run and its exact output>

## What I need decided
<one question, answerable yes/no or by naming one option from a list>

## Options I can see
1. <option>
2. <option>

## What I have NOT done
<confirm no foreign path was touched, no convention was invented, no branch was pushed>
```

- **If `make contract-test` fails on your branch:** do not modify anything under `contracts/`. Do not
  disable the check. Run `--contract <id> --verbose`, read which contract and which side failed,
  and open a blocker issue titled `BLOCKER [<task-id>]: contract <id> failed, <producer-lane>↔<consumer-lane>`,
  labelled `--label blocker --label lane/<N> --label phase/<phase-lower>`, with the full last line of
  the suite output in **What I observed**. Then stop.
- **If the failure names a contract your lane does not produce:** it is still your blocker to file.
  Do not assume the other lane knows.
- **If the suite exits 3:** stop immediately, file the blocker titled
  `BLOCKER [<task-id>]: contract suite exited 3, instrument failure`, labelled
  `--label blocker --label lane/<N> --label phase/<phase-lower>`, and do not merge anything,
  including work that passed before. Nothing from that run is evidence.
- **If you believe the contract is wrong:** file a Contract Change Request. Never edit `contracts/**`.
  A lane that needs a contract change never makes one (PARTITION.md rule 2).

---

## 9. Command index

Every command is literal and runs from the repository root of `control-plane`.

```bash
# The one command. Full suite: all producers, all consumers, all negative proofs,
# canaries and comparison counts. This is the merge-train gate.
make contract-test
```

`make contract-test` is exactly:

```bash
bash contracts/harness/run-contract-tests.sh --all --report json:contract-report.json
```

Narrower invocations:

```bash
set -euo pipefail
# One contract, both sides
bash contracts/harness/run-contract-tests.sh --contract C-04

# One side of one contract, for one lane — the lane developer's inner loop
bash contracts/harness/run-contract-tests.sh --contract C-07 --side consumer --lane L3

# Everything my lane consumes (run before opening any PR)
bash contracts/harness/run-contract-tests.sh --side consumer --lane L3

# Everything my lane produces
bash contracts/harness/run-contract-tests.sh --side producer --lane L1

# Negative proofs only — every gate must be shown able to fail
bash contracts/harness/run-contract-tests.sh --negative-proof

# Mutation drill — required at every integration → main promotion
bash contracts/harness/run-contract-tests.sh --mutation-drill

# Fixture parity — required the first cycle after any producer lane merges
bash contracts/harness/run-contract-tests.sh --fixture-parity

# Materialise stubs for developing against an unshipped producer
make stub-env

# Explain a failure
bash contracts/harness/run-contract-tests.sh --contract C-04 --verbose --explain
```

Gate wiring, in the `integration` branch protection required checks (declared in L5's
`access/branch-protection/branch-protection.yaml`, emitted as a job by L2, both asserted by C-06):

```bash
# job name emitted by .github/workflows/contract-tests.yml, and the exact string
# that must appear in required_status_checks:
contract-tests
```

---

## 10. Coverage map

Every contract test traces to at least one acceptance test or invariant. Ids are quoted from
Section 100 and Section 101 as written.

| Contract | Acceptance tests | Invariants (§101) |
| --- | --- | --- |
| C-01 | AT-001, AT-002, AT-009, AT-047, AT-049, AT-051 | 1, 7, 52, 53, 54 |
| C-02 | AT-032 | 87 |
| C-03 | AT-105, AT-088 | 46, 47, 48, 111 |
| C-04 | AT-032 | 46, 49 |
| C-05 | AT-024, AT-026, AT-103 | 22, 71, 72, 85 |
| C-06 | AT-024, AT-033 | 44, 87 |
| C-07 | AT-021, AT-089, AT-091, AT-097, AT-098, AT-110 | 18, 79, 80, 106, 109 |
| C-08 | AT-032, AT-033, AT-102, AT-036, AT-037 | 44, 45, 81 |
| C-09 | AT-046, AT-032 | 46, 49 |
| C-10 | AT-106, AT-107 | 49 |
| C-11 | AT-108, AT-109, AT-110, AT-103 | 18, 24, 25, 26, 84 |
| C-12 | AT-025, AT-023 | 73, 74, 85 |
| Harness itself (canary, counts, mutation drill) | AT-102, AT-032, EC-109 | 44, 87 |

The harness row is the one that matters most. Twelve gates that report green prove nothing on their
own; the canary, the comparison counts and the mutation drill are what make the other twelve rows
mean anything at all.
