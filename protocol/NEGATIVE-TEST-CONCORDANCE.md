# NEGATIVE-TEST CONCORDANCE

**Status:** normative. Settles dispatch-gate item **A3** (FD-098) and closes `_98-DEEP-REVIEW.md` **B-03**
("Six rival, unjoined namespaces for the same negative-test estate ... five lanes will build the same
assertion three to six times under six ids in six trees, and `make negative-audit` — the only auditor —
sees none of them") and the related half of **B-10**.
**Owner:** L0 Integrator. **Conforms to:** `PARTITION.md` (FROZEN).

---

## 0. The ruling

**`GATE-L<n>-<nnn>` (`n` = 0–5) is the canonical negative-test identity namespace, corpus-wide, effective
immediately.** It is the only namespace with a declaration schema (`00-test-strategy.md` §4.2), a
mandatory `negative:` block, and a real auditor (`make negative-audit`, §4.1 rule 5). Every other
namespace below is **non-canonical**: retained where it already exists (renaming a live script's
identifiers is a runtime-behavior change, held to the same caution as A1 and A2 — see §4), but not to be
used for anything new, and mapped here onto its `GATE-L<n>-<nnn>` equivalent so that:

* a lane asking "has this control already got a test somewhere?" finds the answer in one table instead
  of grepping six trees;
* `make negative-audit` can eventually be pointed at the old fixtures too, via this table, instead of
  seeing zero of them (the exact failure B-03 names); and
* nobody builds a seventh namespace by accident.

**One gate, one canonical id, however many old aliases cite it.** Where two old-namespace tests turn out
to exercise the same control under different names, they are **the same gate** below — this is not
"the file with more tests wins", it is the corpus discovering it built one thing twice.

---

## 1. The canonical table

One row per `GATE-L<n>-<nnn>`. The **Source** column marks whether the id already existed in
`00-test-strategy.md` §7's representative gate catalogue (**existing**) or is minted here for the first
time because no canonical id previously covered this control (**new, this file**). The **Old-namespace
aliases** column is the concordance proper: every id, in every other namespace, that tests this same
control today, and exactly where it lives.

### GATE-L0-* (cross-lane, L0-owned)

| Canonical id | Source | What it proves | Old-namespace aliases (file : location) |
|---|---|---|---|
| `GATE-L0-001` | existing (`00` §4.1) | `make negative-audit` itself rejects a gate declaration with no `negative:` block — the doctrine's own recursive proof | none |
| `GATE-L0-002` | existing (already named in `05-merge-gate.md` §6: *"`LG-02` ... has its own negative test (`GATE-L0-002`)"*) | A lane PR touching a foreign path fails `lane-guard` | `NT-30` (`04-negative-tests.md` §3 register, §4 not detailed inline but named `Lane guard`) |
| `GATE-L0-003` | **new, this file** | A lane PR touching `contracts/**` fails lane-guard as FROZEN | `NT-31` (`04-negative-tests.md` §3 register, "Contract freeze") |
| `GATE-L0-004` | **new, this file** | Every one of the 32 catalogued negative tests is itself proven able to report FAIL under mutation (the catalogue's own anti-vacuity proof) | `NT-32` (`04-negative-tests.md` §3 register, "The catalogue can fail") |

### GATE-L1-* (Registries & Contracts)

| Canonical id | Source | What it proves | Old-namespace aliases (file : location) |
|---|---|---|---|
| `GATE-L1-001` | existing | An exception with no `expiry` fails CI | `NT-18` (`04` §3 register + §4 worked test); `NEG-25` (`08-smoke-and-e2e.md` §10 table, "Exception expiry") |
| `GATE-L1-002` | existing | An assignment naming a departed/nonexistent person fails CI | none found elsewhere |
| `GATE-L1-003` | existing | `restore_tested` older than the 90-day floor fails CI | `NT-26` (`04` §3 register, "Restore claim needs evidence" — extends this gate to the *no-matching-record* case, not only the stale-date case); `NEG-CONTRACT-002` (`09-fixtures.md` §9's worked table, "backdated beyond the 90-day floor"); `NEG-CONTRACT-016` (`09` §9, "`restore_tested` date with no matching record" — same extension as `NT-26`) |
| `GATE-L1-004` | existing | A 24×7 `coverage_window` not covered by active rota members fails contract validation | `NEG-CONTRACT-011`, `NEG-CONTRACT-012` (`09` §9 worked table) |
| `GATE-L1-005` | existing | An invariant carrying no enforcement classification fails CI | none found elsewhere |
| `GATE-L1-006` | existing | `ai_runtime_dependency` with no `verification/` suite fails CI | `NEG-CONTRACT-009` (`09` §9 worked table); partially, `N-01`'s composite fixture (`01-contract-tests.md` §4 C-01, which bundles this case together with two others — see `GATE-L1-011` below) |
| `GATE-L1-007` | existing | An authority delta with no linked decision-record id fails CI | `NT-23` (`04` §3 register + §4 worked test) |
| `GATE-L1-008` | existing | No product list is hard-coded in any schema/validator/dashboard | none found elsewhere |
| `GATE-L1-009` | existing | An assignment granting `people-intelligence` fails validation | `NT-22` (`04` §3 register + §4 worked test) |
| `GATE-L1-010` | existing | Banned surveillance measurements are absent from the schema | none found elsewhere |
| `GATE-L1-011` | **new, this file** | Onboarding without a verification contract fails CI (invariant 1) | `N-01` (`01` §4, C-01 — the invariant-1 sub-case of that composite canary; the fixture's other two sub-cases are `GATE-L1-004` and `GATE-L1-006` above) |
| `GATE-L1-012` | **new, this file** | Capability vocabulary is closed: an undefined capability in any grant point is denied, never permitted | `NT-07` (`04` §3 register + §4 worked test) |
| `GATE-L1-013` | **new, this file** | A role default carrying a founder-class capability (incl. `people-intelligence`) fails CI | `NT-08` (`04` §3 register + §4 worked test) |
| `GATE-L1-014` | **new, this file** | Fixture-provenance detector (invariant 111, detector 1 of 3, §38.3): a fixture with no declared `synthetic` provenance, or carrying customer-shaped data, is rejected | `IT-111` (`03-invariant-tests.md` §9.2, detectors 1 and 3 — L1's half); `NEG-28` (`08` §10 table, "Add a fixture containing customer-shaped data ... fixture-provenance detector" — this is L1's detector, not L4's; see `GATE-L4-006` for the distinct records-body detector) |
| `GATE-L1-015` | **new, this file** | Gate 1 (the plan-checker's own approval step) admits no self-approval | `NEG-09` (`08` §10 table, "`dev-a` approves `dev-a`'s own plan") — **note:** this is Gate 1 (planning), a distinct mechanism from Gate 2/merge self-approval (`GATE-L5-011`) and from production self-approval (`GATE-L2-013`); do not conflate the three |
| `GATE-L1-016` | **new, this file** | A registry naming the records-writer machine credential as a product owner is rejected by the CODEOWNERS renderer, not silently filtered | `N-07` (`01` §4, C-07) |
| `GATE-L1-017` | **new, this file** | A product that has silently dropped support for a `platform.yaml`-declared version still fails the multi-version validator | `N-12` (`01` §4, C-12) |

### GATE-L2-* (Pipeline & Evidence)

| Canonical id | Source | What it proves | Old-namespace aliases (file : location) |
|---|---|---|---|
| `GATE-L2-001` | existing | A production deploy whose digest differs from the staging-verified digest is rejected; production is never rebuilt to work around registry unavailability | `NT-04` (`04` §3 register + §4 worked test); `IT-022` (`03` §5.2, invariants 22/23 — the whole digest-chain suite, including the `verify-digest-chain` sweep); `NEG-01`, `NEG-02`, `NEG-03` (`08` §10 table — digest immutability, never-rebuild, and the `/version`-mismatch runtime sweep respectively) |
| `GATE-L2-002` | existing | Every required-check name is emitted by a job with no `if:` and no path filter | `NT-11` (`04` §3 register + §4 worked test); `NEG-19` (`08` §10 table) |
| `GATE-L2-003` | existing | The verification contract's seeded-defect case FAILS the contract | `NT-13` (`04` §3 register + §4 worked test); `NEG-04` (`08` §10 table). **Rolled up at the DoD level** (not a duplicate id, a higher-level aggregate reading of this same gate): `DT-06`, `DL-05`, `DV-05` (`11-definition-of-done.md`) |
| `GATE-L2-004` | existing | Privileged workflows fail closed when the actor is not a capability-holding human | `NT-15` (`04` §3 register + §4 worked test); `IT-018-D` (`03` §6.3) |
| `GATE-L2-005` | existing | A branch workflow declaring `environment: production` obtains no environment secret | none found elsewhere (distinct from `GATE-L5-014`'s deploy-ref policy) |
| `GATE-L2-006` | existing | Time gates (e.g. the Friday freeze) resolve against the declared working calendar, never runner local time | `NEG-22` (`08` §10 table) |
| `GATE-L2-007` | existing | A moved `workflows/*` tag is Blocking drift | `NT-12` (`04` §3 register + §4 worked test); `NEG-20` (`08` §10 table) |
| `GATE-L2-008` | existing | All eleven evidence-chain questions are answerable; a best-effort deployment-record write that silently failed is a FAILED deploy | `NEG-27` (`08` §10 table) |
| `GATE-L2-009` | **new, this file** | A privileged workflow resolving to a shared-pool runner fails closed at its first step, before checkout | `NT-05` (`04` §3 register + §4 worked test) |
| `GATE-L2-010` | **new, this file** | A foreign-identity commit lands on a bypass-actor branch (e.g. a non-Renovate identity pushing to a Renovate lockfile branch) and is caught by the authorship half of the guard | `NT-10` (`04` §3 register, "Bypass is one identity's grant"); `NEG-21` (`08` §10 table, "Renovate path guard") |
| `GATE-L2-011` | **new, this file** | The plan-checker hard-rejects: no rollback strategy, no verify command, an undeclared symbol, a slopsquat package name | `NT-24` (`04` §3 register + §4 worked test); `NEG-05`, `NEG-06`, `NEG-07`, `NEG-08` (`08` §10 table) |
| `GATE-L2-012` | **new, this file** | No customer data in git: a commit-scanning detector distinct from `GATE-L1-014`'s fixture-provenance check and `GATE-L4-006`'s records-body check | `NT-29` (`04` §3 register + §4 worked test) |
| `GATE-L2-013` | **new, this file** | Production approval is never self-approved and is a separate event from Gate 2 (invariant 12); the workflow-identity gate fails closed when it cannot tell | `IT-012` (`03` §4.3); `NEG-13` (`08` §10 table, "the approver dispatches the deploy") |
| `GATE-L2-014` | **new, this file** | Production approval cannot be recorded against a digest before that digest passed staging verification | `NEG-14` (`08` §10 table) |
| `GATE-L2-015` | **new, this file** | An open verification block fails closed against a production deploy attempt | `NEG-15` (`08` §10 table) |
| `GATE-L2-016` | **new, this file** | A staging-only environment variable reaching a production deploy is a Blocking parity violation | `NEG-24` (`08` §10 table) |

### GATE-L3-* (Reconciler & Provisioning)

| Canonical id | Source | What it proves | Old-namespace aliases (file : location) |
|---|---|---|---|
| `GATE-L3-001` | existing | Every reconciliation run finds the seeded canary; zero findings is a FAILED run raising SIG-13; a silently narrowed comparison also fails | `NT-06` (`04` §3 register + §4 worked test, the file's own "single most important test"); `IT-102` (`03` §8.3, "the single clearest statement of this file's governing principle"); `NEG-18` (+ the `NEG-18b` positive-restoration companion) (`08` §10 table + §11 negative-proof block). **Rolled up at the DoD level:** `DI-06`, `DG-06`, `DV-06` |
| `GATE-L3-002` | existing | Every run records its per-registry comparison counts | none found elsewhere as a standalone id (folded into the `GATE-L3-001` worked tests above, e.g. `03`'s "Command — part C: a silently narrowed comparison must also fail") |
| `GATE-L3-003` | existing | Auto-repair moves only toward the declared, stricter state | `NT-17` (`04` §3 register + §4 worked test); `IT-081`, `IT-081-U` (`03` §8.1–§8.2, the property-test and live-behaviour halves of this one gate); `NEG-26` (`08` §10 table) |
| `GATE-L3-004` | existing | The reconciler credential is bounded: privileged writes all fail, then a normal run still completes | `NT-16` (`04` §3 register + §4 worked test); `NEG-17` (`08` §10 table) |
| `GATE-L3-005` | existing | An expired assignment is revoked with no human action | none found elsewhere |
| `GATE-L3-006` | existing | Blocking orphans cannot be dismissed unresolved | none found elsewhere |
| `GATE-L3-007` | existing | The independent control verifier runs off a different host under a different credential from the reconciler | `NT-25` (`04` §3 register + §4 worked test) |
| `GATE-L3-008` | existing | `create-product` / `add-person` complete with zero hand-editing | none found elsewhere |
| `GATE-L3-009` | existing | A merged registry change reaches only its declared canary set, for one cycle | none found elsewhere |
| `GATE-L3-010` | **new, this file** | A machine identity's push to a workflow file is caught as Blocking drift (`workflow-file-changed-by-machine-identity`), even though the push itself succeeds at the git layer | `NT-14` (`04` §3 register + §4 worked test) |
| `GATE-L3-011` | **new, this file** | Section 53.7's second branch: a reconciliation loop that *completed* against a wrongly-computed declared state is not thereby a loop that was *right* — completing and reporting clean is not the same as being correct | `IT-537` (`03` §8.4 — note the id itself does not fit the `IT-<invariant-number>` convention the rest of the file uses; it is not a real invariant number, and should not be copied forward as a pattern) |

### GATE-L4-* (Records, Events & Metrics)

| Canonical id | Source | What it proves | Old-namespace aliases (file : location) |
|---|---|---|---|
| `GATE-L4-001` | existing | A store past its declared write-freshness interval is Amber/Blocking, never green | `NT-27` (`04` §3 register + §4 worked test) |
| `GATE-L4-002` | existing | A count-shaped metric reading zero against a stale store is a failure, not health | none found elsewhere |
| `GATE-L4-003` | existing | The records-writer credential is scoped to the records repository alone | `NT-21` (`04` §3 register + §4 worked test) |
| `GATE-L4-004` | existing | Records are append-only; a correction is a follow-up record, never an in-place edit | `NT-20` (`04` §3 register + §4 worked test) |
| `GATE-L4-005` | existing | Every dashboard metric names the record store it derives from | none found elsewhere |
| `GATE-L4-006` | existing | No customer data in records (invariant 111, detector 2 of 3, §22.2 — by-identifier support records, distinct from `GATE-L1-014`'s fixture-provenance detector) | `IT-111-R` (`03` §9.2, "L4 ... for detector 2") |
| `GATE-L4-007` | existing | Every record carries `record_schema_version`, `id`, `product`, `timestamp` | none found elsewhere |
| `GATE-L4-008` | existing | Manual results reach stores only through `RECORD-VERIFICATION-RESULT` | none found elsewhere |
| `GATE-L4-009` | **new, this file** | A record carrying a display name where a person id belongs fails schema validation | `NT-09` (`04` §3 register + §4 worked test) |

### GATE-L5-* (Access, Infra & Ops)

| Canonical id | Source | What it proves | Old-namespace aliases (file : location) |
|---|---|---|---|
| `GATE-L5-001` | existing | Layer B is unreachable from general surfaces by any path | none found elsewhere |
| `GATE-L5-002` | existing | No people datasource entry exists in the shared Grafana provisioning | none found elsewhere |
| `GATE-L5-003` | existing | The Founder-only instance requires its own credential | none found elsewhere |
| `GATE-L5-004` | existing | `people-intelligence` gates Layer B; expiry closes access through reconciliation | none found elsewhere |
| `GATE-L5-005` | existing | The Team Lead is denied at both the dashboard and the datasource layer | none found elsewhere |
| `GATE-L5-006` | existing | The founder ops console is provably read-only | none found elsewhere |
| `GATE-L5-007` | existing | The background cage egress wall holds; the wall-clock stop terminates the process | none found elsewhere |
| `GATE-L5-008` | existing | `env \| grep -i api_key` returns empty everywhere, including shell profiles and `.env` files | `IT-084` (`03` §7.3) |
| `GATE-L5-009` | existing | The operations VM rebuilds from GitHub in under 4 hours | none found elsewhere |
| `GATE-L5-010` | existing | Every expiry-tracked asset carries an owner, an expiry and a lead alert | none found elsewhere |
| `GATE-L5-011` | **new, this file** | No self-approval, merge side: an author cannot approve or merge their own PR; a stale approval after a new push does not satisfy the gate | `NT-01` (`04` §3 register + §4 worked test, the file's canonical example); `IT-009` (`03` §4.2, incl. its N1/N2/N3 sub-cases — self-approval, stale-approval, read-only-approval); `NEG-10`, `NEG-11` (`08` §10 table — Gate 2 independence and staleness) |
| `GATE-L5-012` | **new, this file** | A Read-only identity's approval is recorded but does not satisfy branch protection | `NT-02` (`04` §3 register + §4 worked test); `NEG-12` (`08` §10 table). (`IT-009`'s N3 sub-case above also exercises this; both are retained as aliases of the one gate.) |
| `GATE-L5-013` | **new, this file** | A machine-account approval, and machine-account merge/approve/deploy generally, never satisfies branch protection or the actor gate | `NT-03` (`04` §3 register + §4 worked test); `IT-018` (`03` §6.2, "the approval wall"); `NEG-23` (`08` §10 table, "Machine authority ... actor gate, GitHub-side") |
| `GATE-L5-014` | **new, this file** | A deploy to `production` from a non-default, non-tag ref is rejected by the environment/deployment-branch policy | `NT-19` (`04` §3 register + §4 worked test); `NEG-16` (`08` §10 table) |
| `GATE-L5-015` | **new, this file** | A non-ephemeral runner registered in the `privileged` group is Blocking drift | `NT-28` (`04` §3 register + §4 worked test) |
| `GATE-L5-016` | **new, this file** | Unattended personal-agent runs are branch-only, flagged, and never merge without the full human gate sequence (invariant 21) | `IT-021` (`03` §6.4) |
| `GATE-L5-017` | **new, this file** | The production database is inaccessible from developer machines (invariant 24) | `IT-024` (`03` §7.2) |
| `GATE-L5-018` | **new, this file** | Production secrets are environment-scoped and never present locally (invariant 25) | `IT-025` (`03` §7.3) |
| `GATE-L5-019` | **new, this file** | A fully compromised workstation does not yield production access (invariant 26, executed as a drill) | `IT-026` (`03` §7.4) |

---

## 2. Namespace-by-namespace notes

For each namespace: its grammar, the one file it lives in today, and what — if anything — this table
could not map.

### `N-<nn>` — `01-contract-tests.md` §4

One per contract pair (`N-01` ↔ `C-01`, … `N-12` ↔ `C-12`); each is the pair's seeded-canary fixture,
not a general-purpose negative test. All twelve are mapped above (§1), several as aliases of an existing
gate (`N-01` is a three-way composite — see `GATE-L1-004`, `GATE-L1-006`, `GATE-L1-011`) and the rest as
newly minted `GATE-L1-*` ids. Nothing in this namespace was left unmapped.

### `IT-<nnn>[-suffix]` — `03-invariant-tests.md` §4–§9

One script per invariant (or invariant pair), named by invariant number, with `-N1`/`-N2`/… sub-cases
inside the one script and occasional named suffixes (`-D`, `-U`, `-R`). All sixteen top-level ids are
mapped above. `IT-537` is the one irregular id in the file (not an invariant number — see `GATE-L3-011`'s
note) and should not be used as a precedent for minting more ids outside the `IT-<invariant-number>`
convention going forward, since that convention is itself superseded by `GATE-L<n>-<nnn>`.

### `NT-<nn>` — `04-negative-tests.md` §3–§8

The most complete of the six namespaces already: every one of `NT-01`…`NT-32` carries an owner, a
"blocks" hop and a spec anchor in its own register table (§3). All 32 are mapped above.

### `NEG-<nn>` — `08-smoke-and-e2e.md` §10

Twenty-eight ids, each a row in one flat table (§10) with a mechanism, a required result and a spec
anchor; `NEG-18b` is a positive companion to `NEG-18`, not a 29th independent test. All 28, plus the
`NEG-18b` companion, are mapped above.

### `NEG-<DOMAIN>-<nnn>` — `09-fixtures.md` §7–§9 (e.g. `NEG-CONTRACT-011`, `NEG-PEOPLE-004`, `NEG-ASSIGN-001`)

**This namespace is not the same kind of thing as the other five, and is not being folded into
`GATE-L<n>-<nnn>` wholesale.** It names *fixture instances* (`contracts/fixtures/neg/**`, one directory
per case — PARTITION rule 3), not *tests*. Each fixture's `fixture.yaml` already carries a
`must_be_rejected_by:` list of **gate ids** (`09` §9.3's `fixtures-coverage` script reads
`contracts/gates.yaml`'s `.gates[].id` directly) — so once `contracts/gates.yaml` is populated per the
`00` §4.2 schema, every fixture in this namespace cites a `GATE-L<n>-<nnn>` id *by construction*, with no
renaming needed. The only outstanding item is an audit, not a rename: confirm every existing
`must_be_rejected_by` entry actually spells a `GATE-L<n>-<nnn>` id and not an invented one. §1 above maps
the handful of `09` fixtures this session could tie to a specific control from the anchors given
(`NEG-CONTRACT-002`, `NEG-CONTRACT-009`, `NEG-CONTRACT-011`, `NEG-CONTRACT-012`, `NEG-CONTRACT-016`,
`NEG-09`, `NEG-28`) as illustration; the file's own count (per `_98-DEEP-REVIEW.md` B-14, roughly 88 cases
under `contracts/fixtures/neg/**`) was not enumerated exhaustively here — that sweep is mechanical once
`contracts/gates.yaml` exists (§4 below) and is a poor use of a hand-written concordance in the meantime.

### `DT-<nn>` / `DP-<nn>` / `DL-<nn>` / `DI-<nn>` / `DV-<nn>` / `DG-<nn>` — `11-definition-of-done.md`

**This namespace is also not folded in wholesale, for a different reason: most of these 61 ids are not
tests of a single control at all.** They are the six-level Definition-of-Done checklist (§0.1: task,
phase, lane, integration, v1, programme) — roll-up questions like "did every acceptance criterion produce
its exact `expect` string" (`DT-02`) or "did the founder view render with zero hand-maintained numbers"
(`DV-07`) that have no `GATE-L<n>-<nnn>` counterpart because no single gate covers them; forcing one would
manufacture a false duplicate. **The genuine duplicates — where a DoD-level check is explicitly a
higher-level reading of one specific gate already in §1 — are called out as "rolled up" cross-references
next to that gate above:** `DT-06`/`DL-05`/`DV-05` under `GATE-L2-003`, and `DI-06`/`DG-06`/`DV-06` under
`GATE-L3-001`. `DI-01` ("GATE B open") and `DI-04` ("fixture gate ... `make fixtures-all` green") are not
aliases needing a mapping at all — they already invoke `05-merge-gate.md`'s GATE B and `09-fixtures.md`'s
meta-gates by their own real names. Every other `DT`/`DP`/`DL`/`DI`/`DV`/`DG` id is a DoD-specific
composite with no duplicate elsewhere in the corpus, and is left as-is.

---

## 3. What this table does not do

**No script anywhere is renamed by this file.** Per the same caution applied to A1 and A2: this corpus is
"deeply cross-referenced and prone to breaking in surprising ways", and none of the machinery this table
describes exists yet as a real script (`_98-DEEP-REVIEW.md` B-06 — `bin/gate`, `contracts/gate/**`,
`reconciler/run.py` and everything else cited above is still specification, not code). Renaming is
therefore not a live-behavior risk today, but it is still real work with a real ordering dependency:
`contracts/gates.yaml` and the `gates/<GATE-ID>.yaml` declaration files (`00` §4.2) do not exist yet
either, and minting the eighteen new `GATE-L<n>-*` ids in §1 is a **documentation-level act** — it makes
the map exist — while **authoring `gates/GATE-L1-011.yaml` etc. and wiring `contracts/gates.yaml` is the
mechanical follow-up task** this file hands to whichever lane implements the Phase-0 gate machinery.
Until that happens, the old ids keep working exactly as their own files describe; this table is what a
lane consults before adding a nineteenth way to test the same thing.
