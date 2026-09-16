# L1-99 — COHERENCE REVIEW OF LANE 1 (Registries & Contracts)

> **SUPERSEDED — 2026-09-02**  
> D1 ("30 of 61 L1-05 task bodies missing") verified false at triage: all 61 bodies present.  
> **Do not act on this finding.** Re-derive against current files before acting on any item.

**Reviewed:** `L1-00-charter.md`, `L1-01-repo-skeleton.md`, `L1-02-schemas.md`, `L1-03-validators.md`, `L1-04-ci-gate-engine.md`, `L1-05-tasks.md`, `L1-06-tests.md`, `L1-07-runbook.md` (8 files, 12,213 lines) against `PARTITION.md` and `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md`.

**Reviewer profile assumed for every judgment below:** PARTITION.md line 44 — *"Sonnet-4.6-class, low cost, no repo context, no judgment authority."*

---

## VERDICT

> ## **BLOCKED — DO NOT DISPATCH**
>
> Lane 1 is not one plan. It is **five independent, mutually exclusive plans for the same subsystem**, written against three incompatible file-naming conventions, two programming languages, and three separately-frozen CLI contracts that collide on the same file paths. Dispatching them in parallel produces guaranteed merge destruction inside L1 before the merge train ever reaches L4. On top of that, the document that calls itself the lane's authoritative atomic task list is **missing 30 of its 61 task bodies**.
>
> **8 blocking defects, 7 high, 6 medium, 4 low. 25 total.**
>
> The citation layer is the one part of this lane that is sound: all 25 pinned spec anchors resolve exactly, and every AT-, SIG-, D- and invariant identifier cited anywhere in L1 exists in the spec. **No invented identifier was found.** The failure is structural, not evidentiary.

---

## SUMMARY BY CHECK

| # | Check | Result |
|---|---|---|
| 1 | Path-ownership violations | **1 real write outside owned prefixes** (D9), plus 2 scope violations (D10, D13) |
| 2 | Dangling dependencies | **No dangling task ids**; but 3 dangling *file-path* references that gate STOP rules (D5), and 1 undeclared task dependency (D17) |
| 3 | Missing controls | Every task body that exists carries SELF-VERIFY **and** a STOP rule — 127/127. **But 30 declared tasks have no body at all**, therefore no controls (D1) |
| 4 | Internal disagreement | **Catastrophic.** Five task-id schemes, 127 bodies vs 61 declared, 3 frozen CLI contracts, 3 schema layouts, 2 languages, 4 contradicted field definitions (D2–D8, D11–D14) |
| 5 | Judgment leakage | 4 instances requiring design; 1 requiring org credentials and not marked ASSISTED (D10, D15, D18, plus D-J below) |
| 6 | Citation integrity | **PASS.** 25/25 anchors resolve; 40 AT ids, 17 SIG ids, 24 D ids, 32 invariant numbers all exist; 13 sampled content claims all verified correct. 2 soft issues (D23, D24) |
| 7 | Executability | Both sampled complex tasks fail for different reasons (D7, D18) |

---

# DEFECT LIST — WORST FIRST

---

## D1 — BLOCKING — `L1-05-tasks.md` is truncated: 30 of 61 task bodies are missing

**File:** `lanes/L1-05-tasks.md`
**Task ids:** `L1-401`, `L1-402`, `L1-403`, `L1-404`, `L1-501`, `L1-502`, `L1-503`, `L1-504`, `L1-505`, `L1-601`, `L1-602`, `L1-603`, `L1-604`, `L1-605`, `L1-606`, `L1-607`, `L1-608`, `L1-701`, `L1-702`, `L1-703`, `L1-704`, `L1-705`, `L1-801`, `L1-802`, `L1-803`, `L1-901`, `L1-902`, `L1-903`, `L1-904`, `L1-905` — **30 tasks.**

**Problem.** The master table at §2 declares 61 tasks and states *"Totals: 61 tasks."* The document body ends at line 2003 with `L1-311` and the horizontal rule that would introduce `L1-401`. Phases **L1.4 Verification, L1.5 Topology, L1.6 Governance, L1.7 Versioning, L1.8 People and L1.9 Close do not exist.** Every one of those 30 tasks therefore has: no COMMANDS, no schema shape, no fixture list, no SELF-VERIFY, no CORRECT OUTPUT, no STOP rule — only a one-line table row and a pytest count the executor cannot possibly hit.

This is not recoverable by an executor. `L1-905` (lane handoff, the merge-train tag) and `L1-904` (full-lane regression) are the tasks that close the lane, and they are absent. `_DAMAGE.md` does not list this file; the damage report is itself incomplete.

**Correction.** Author the 30 missing task bodies to the standard already set by `L1-001`–`L1-311`, or delete the rows from the master table and re-scope the lane. Add `L1-05-tasks.md` to `_DAMAGE.md`. **Nothing in L1 dispatches until this is closed.**

---

## D2 — BLOCKING — Five mutually exclusive implementations of subsystem B, three of them writing the same files

**Files:** `L1-02-schemas.md` §L1-02-01; `L1-03-validators.md` §0 and §4; `L1-04-ci-gate-engine.md` §1.1–§1.7; `L1-05-tasks.md` §L1-003; `L1-06-tests.md` §0 and §L1-06-01.

**Problem.** Each document independently designs, and independently *freezes*, the validator that L2 wires into CI. They are incompatible at every level:

| Doc | Entry point | Invocation | Exit codes | Rule identity | Rule storage |
|---|---|---|---|---|---|
| L1-02 | `validators/registry/schema-check/check.mjs` | `node check.mjs` | n/a | n/a | `schemas/**` only |
| L1-03 | `validators/registry/cli.py` | `python -m validators.registry.cli --root <p> --as-of <d> --records-root <p> --format json --rule Rxx` | 0/1/2 | `R01`…`R18`, findings `R07.1` | `rules/r07_coverage_rota.py` |
| L1-04 | `validators/registry/gate.py` | `python3 validators/registry/gate.py --root . --mode all --report <p>` | 0/1/2/**3** | directory name | `rules/<id>/rule.yaml` + `check.py` |
| L1-05 | `validators/registry/cli.py` | `python -m validators.registry.cli validate --file <p> --dir <p> --today <d> --format text` | 0/1/2/**3, different meanings** | `R-CAP-01`, `R-PPL-02`, `R-REF-01` | `rules/r_cap_01.py` |
| L1-07 | `validators/registry/run-all.sh` | `bash validators/registry/run-all.sh` | — | — | — |

**`validators/registry/cli.py` is authored twice, by L1-03-01 and by L1-05-L1-003, with different and explicitly frozen argument grammars.** L1-05-L1-003 states: *"This CLI is the only interface Lane 2 may call. Its grammar is frozen from this task onward."* L1-03 §0 states: *"L1 Phase 3 publishes exactly one machine surface. Nothing else in the repo may be assumed to be a public entry point."* Both cannot be true. `validators/registry/README.md` is authored three times (L1-00-02, L1-04-01, L1-05-L1-903); `requirements.txt` twice (L1-04-01, L1-05-L1-002); `rules/__init__.py` three times (L1-03-01, L1-05-L1-002, L1-05-L1-005).

Exit code `3` means **GATE CANARY FAILURE** in L1-04 and **internal error** in L1-05. An L2 workflow keyed to one silently mis-gates the other.

**Correction.** L0 must pick exactly one engine design and delete the other four. The surviving design's invocation contract, exit-code table and rule-id grammar go into `contracts/**` (this is already L1-04's `D-2` and L1-06's `DR-L1-06-B`, neither of which any document waits on). Every other L1 document is then rewritten against it. This is the single largest piece of work required before dispatch.

---

## D3 — BLOCKING — No single task-id scheme; the "atomic task list" is not the lane's task list

**Files:** all eight.

**Problem.** Lane 1 uses **five** incompatible id schemes, and `L1-05-tasks.md` §0 tells the executor the opposite of the truth:

> *"You are the Lane 1 executor. Work top to bottom. Do not skip. Do not reorder. **Do not open another document to decide what to do next — everything you need is here.**"*

| Document | Scheme | Bodies |
|---|---|---|
| `L1-00-charter.md` | `L1-00-01` … `L1-00-05` | 5 |
| `L1-01-repo-skeleton.md` | `L1-01-01` … `L1-01-13` | 13 |
| `L1-02-schemas.md` | `L1-02-01` … `L1-02-19` | 19 |
| `L1-03-validators.md` | `L1-03-00` … `L1-03-20` | 21 |
| `L1-04-ci-gate-engine.md` | `L1-04-01` … `L1-04-09` | 9 |
| `L1-05-tasks.md` | `L1-001` … `L1-905` | 31 of 61 declared |
| `L1-06-tests.md` | `L1-06-01` … `L1-06-15` | 15 |
| `L1-07-runbook.md` | `L1-RB-00` … `L1-RB-13` | 14 |

**127 task bodies exist. The document that claims to be complete declares 61 and delivers 31.** `L1-05-tasks.md` contains not one reference to `L1-01-T*`, `L1-02-T*`, `L1-03-T*`, `T-L1-04-*` or `L1-06-T*`. An executor handed L1-05 and told to work top-to-bottom will re-author, from scratch and differently, work that five other documents already specify — and vice versa.

**Correction.** Declare one document the dispatch surface. Either (a) `L1-05-tasks.md` absorbs the phase documents and they become reference-only, or (b) `L1-05-tasks.md` is deleted and the phase documents get a single ordering index. Renumber to one scheme. Publish the mapping in the charter §14 summary card.

---

## D4 — BLOCKING — Two validator languages inside one lane

> **RESOLVED — 2026-09-02 — Session 5 / FD-005**
>
> D4 (*"Node.js vs Python conflict"*) was resolved in Session 5 via FD-005. `lanes/L1-02-schemas.md` received 117 replacements: the T01 harness was rewritten (`check.mjs` → `check.py`), 87 invocation replacements applied, 20 `node -e` → `python3 -c` replacements applied. The lane now uses Python exclusively for the schema-check harness. The finding below is preserved for audit but is no longer a dispatch blocker.

**Files:** `L1-02-schemas.md` (110 Node/npm/ajv references, 1 Python) vs `L1-03-validators.md` (125 Python, 0 Node), `L1-04-ci-gate-engine.md` (43 Python), `L1-05-tasks.md` (Python, pinned).
**Task ids:** `L1-02-01` (creates `validators/registry/schema-check/package.json` + `check.mjs`) vs `L1-05-L1-002` (creates `validators/registry/requirements.txt` pinning `jsonschema==4.23.0`, `ruamel.yaml==0.18.6`, `pytest==8.3.3`).

**Problem.** `L1-05-L1-001`'s STOP rule is:

```
grep -rniE "node|typescript|deno|ajv|golang|rust" contracts/ ... && echo "TOOLCHAIN CONFLICT"
```

with the instruction *"L0's frozen `contracts/**` names a non-Python validator toolchain; that overturns L1-D01 and every task below."* The conflict is not in `contracts/**` — it is inside Lane 1's own plan, and no STOP rule looks there. Meanwhile `L1-03`'s `validator_runtime` decision key and `L1-04`'s `D-3` both assume Python, and `L1-02-19`'s phase gate is `node -e "require('./schemas/registry/index.json')..."`. Two dependency ecosystems will be installed in the same `validators/registry/` tree.

**Correction.** L0 answers `L1-D01` / `L1-03 validator_runtime` / `L1-04 D-3` once, in `contracts/**`. Rewrite `L1-02-schemas.md`'s harness in the chosen language. Do not let the executor discover this.

---

## D5 — BLOCKING — Three incompatible schema-file layouts; downstream STOP rules gate on paths no task ever creates

**Files:** `L1-00-charter.md` §3.1; `L1-02-schemas.md` §0.1 and §1; `L1-05-tasks.md` §L1-101/L1-102/L1-104/L1-106/L1-301/L1-401/L1-404; `L1-03-validators.md` §L1-03-08; `L1-06-tests.md` §2.

| Artifact | Charter §3.1 | L1-02 | L1-05 |
|---|---|---|---|
| people | `schemas/registry/people.v1.schema.json` | `schemas/registry/people/v1/people.schema.json` | `schemas/registry/people.registry.v1.schema.json` |
| roles | `schemas/registry/roles.v1.schema.json` | `schemas/registry/roles/v1/roles.schema.json` | `schemas/registry/roles.registry.v1.schema.json` |
| product | `schemas/product/product.v1.schema.json` | `schemas/product/product/v2/product.schema.json` | `schemas/product/product.contract.v2.schema.json` |
| verification | `schemas/product/verification-contract.v1.schema.json` | not in phase 2 | `schemas/product/verification.contract.v1.schema.json` |
| service | `schemas/product/service.v1.schema.json` | `schemas/product/service/v1/service.schema.json` | **`schemas/registry/service.v1.schema.json`** (different tree) |
| capabilities | `schemas/registry/capabilities.v1.schema.json` | — | **file deliberately not created** (L1-D02 puts the enum in `common/defs.v1.schema.json`) |
| shared defs | `validators/registry/_meta/` | `schemas/registry/_common/v1/common.schema.json` | `schemas/registry/common/defs.v1.schema.json` |

**Consequences that are already load-bearing:**

* `L1-03-08`'s STOP rule reads: *"If `schemas/registry/people.v1.schema.json` has no `rotas` property, or `schemas/product/product.v2.schema.json` has no `operations.coverage_window` …"*. **Neither filename is produced by any L1 task in any document.** The precondition is unevaluable, so the STOP either always fires or the executor guesses a path — which is exactly the judgment PARTITION line 47 forbids.
* `L1-00-charter.md` §6 publishes *"The complete capability vocabulary (`schemas/registry/capabilities.v1.schema.json`)"* to L3 and L5 as a cross-lane artifact. `L1-05-L1-D02` decides that file will never exist. L3 and L5 are being promised a file the lane has decided not to build.

**Correction.** L0 fixes one naming convention and one directory layout in `contracts/**` (this is L1-06's `DR-L1-06-A`, already raised and never answered). Rewrite the charter §3.1 table, `L1-02` §0.1, and every `L1-05` FILES field against it. Re-point `L1-03-08`'s STOP rule at a real path.

---

## D6 — BLOCKING — The entire test phase deadlocks on its own first task

**File:** `lanes/L1-06-tests.md`
**Task id:** `L1-06-01`

**Problem.** T01 gates the other 14 tasks on two conditions, both of which are unsatisfiable given what L1 actually builds:

1. **Schema-set diff.** Acceptance criterion 2 requires
   `find schemas/registry schemas/product -maxdepth 1 -name '*.schema.json' -printf '%f\n' | sed 's/\.schema\.json$//' | sort` to equal exactly the 18 ids `people roles topology platform os-health policies exceptions patterns economics platform-roadmap tools ai-toolchain change-manifest scenario assets product-contract verification-contract shared-service`.
   L1-02 nests schemas at depth 3 (`registry/people/v1/people.schema.json`) so `-maxdepth 1` finds **zero** files. L1-05 emits `people.registry.v1.schema.json`, which strips to the id `people.registry.v1`, not `people`. **The diff can never be empty under either convention.**
2. **Validator discovery.** T01 searches `validators/registry` at `-maxdepth 2` for a file named exactly `validate`, `validate.sh`, `validate.py` or `validate.js`. L1-03 and L1-05 produce `cli.py`; L1-04 produces `gate.py`; L1-07 references `run-all.sh`. **The search returns 0 candidates**, and T01's STOP fires on `0 or more than 1 line`.

Either branch files a blocker and halts the phase at task 1 of 15. The corpus, the canaries, the coverage floors, the mutation harness and the L2 CI contract are all downstream of it.

**Correction.** Close D2 and D5 first, then rewrite T01's `schema-ids.txt` and its entrypoint-discovery glob against the surviving convention. T01 should read the entrypoint from `contracts/**`, not discover it by filename guessing.

---

## D7 — BLOCKING — `L1-03`'s baseline fixture cannot validate clean, and every L1-03 fixture is derived from it

**File:** `lanes/L1-03-validators.md`
**Task ids:** `L1-03-01` (creates the baseline), and by inheritance `T02`–`T20` (all use `make-fixture.sh`, which copies it)

**Problem.** `L1-03-01` step 6 writes a literal `validators/registry/fixtures/_baseline/products/product-1/product.yaml` declaring `contract_version: 2` (line 480). Acceptance criterion 1 is:

> `python -m validators.registry.cli --root validators/registry/fixtures/_baseline --as-of 2026-08-27 --format json` → **stdout exactly `[]`, `EXIT=0`**

That baseline contains `contract_version, platform_compatibility, conformance_profile, identity, classification, assignments, escalation, dependencies, recovery, operations, commitments, business` — **twelve blocks.** The v2 product schema makes ten *more* blocks required, in both competing designs:

* `L1-05-L1-303`: `code`, `verification`, `environments`, `deployment`, `reversibility_default` — all `required`.
* `L1-05-L1-304`: `infrastructure`, `security`, `ai_restrictions`, `data`, `observability`, `automated_containment` — all `required`.
* `L1-02-05` §"Top-level blocks" lists the same ten.

R01 (multi-version schema validation, `L1-03-02`) runs the real schema against this tree. It will emit ten or more findings. **The baseline is red on the day it is authored, criterion 1 is unreachable, and every `fail-<case>` fixture in tasks T02–T20 — which is the baseline plus one delta plus an `expected.json` naming exactly one code — will carry ten unrelated errors and fail its exact-match assertion.**

This is the executability failure for the first of the two most complex tasks I checked.

**Correction.** Extend the baseline `product.yaml` to a complete, schema-valid v2 contract covering all 22 blocks, authored **after** D5 fixes the schema, and add an explicit acceptance step that re-runs criterion 1 whenever `schemas/product/**` changes. The same applies to the baseline `people.yaml`, which uses `accepted_coverage_window: null` as a scalar while `L1-03-08` later replaces it with an object (see D14).

---

## D8 — BLOCKING — The charter forbids three artifacts that two other L1 documents build

**Files:** `L1-00-charter.md` §12 (DECISION REQUIRED #1 and #3) vs `L1-02-schemas.md` §L1-02-16/T17/T18 and `L1-06-tests.md` §2.1

**Problem.** The charter escalates `ai-toolchain.yaml`, `changes/*.yaml` and `scenarios/*.yaml` to L0 as unassigned, and issues a binding instruction:

> **DECISION REQUIRED #1** — *"**L1 default pending answer.** Do not create it. Do not reference it in any validator."*
> **DECISION REQUIRED #3** — *"No lane in PARTITION owns `changes/**` or `scenarios/**`. … **Blocks.** …"*

`L1-02-16` creates `schemas/registry/ai-toolchain/v1/ai-toolchain.schema.json`. `L1-02-17` creates `schemas/registry/scenarios/v1/scenario.schema.json`. `L1-02-18` creates `schemas/registry/changes/v1/change-manifest.schema.json`. `L1-06-tests.md` §2.1 lists `ai-toolchain`, `change-manifest` and `scenario` as ids 12, 13 and 14 of the 18 the corpus asserts must be present on disk, and `L1-06-01` STOPS if they are absent.

So the charter says "if you create it, you have violated the lane" and L1-06 says "if you have not created it, STOP." Both fire.

**Correction.** L0 answers charter DECISION #1 and #3 in `contracts/**`. Until then, remove T16/T17/T18 from `L1-02` and ids 12–14 from `L1-06` §2.1, dropping the id count from 18 to 15. If L0 assigns them to L1, delete the charter's blocking default instead.

---

## D9 — HIGH — Real path-ownership violation: `schemas/.gitignore`

**File:** `lanes/L1-01-repo-skeleton.md`
**Task id:** `L1-01-04`, command block line 461

```bash
set -euo pipefail
cat > schemas/.gitignore <<'EOF'
```

**Problem.** L1 owns `schemas/registry/**` and `schemas/product/**`. It does **not** own `schemas/` itself. `schemas/.gitignore` matches none of the four owned prefixes, so it fails the lane-guard regex `^(schemas/registry/|schemas/product/|registries/|validators/registry/)` that this same lane installs in `L1-00-03`, uses in `L1-04` §3.2, and asserts in `L1-01-03` criterion 3.

The task's own §0.2 states the rule it then breaks: *"Any other path — including `Makefile`, `.gitignore`, `README.md`, `CODEOWNERS`, `docs/**`, `contracts/**` — belongs to L0 Integrator."* Its rationale — *"Git honours a `.gitignore` in any directory, so this lane's ignore rules live in its own directories"* — is correct in principle and wrong in execution: `schemas/` is not one of its own directories.

Worse, **T04's acceptance criteria do not catch it.** Criterion 1 counts three `.gitignore` files (passes), criterion 2 only checks for a *root* `.gitignore` (passes). The violation is silent until the PR hits the lane-guard CI check, at which point every subsequent L1 branch rebased on `integration` inherits a foreign path and fails too.

**Correction.** Replace the single `schemas/.gitignore` with two files: `schemas/registry/.gitignore` and `schemas/product/.gitignore`, with identical content. Update T04's file list, criterion 1 to `4`, and add a criterion asserting `git ls-files | grep -vcE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)'` returns `0`.

---

## D10 — HIGH — Repository and branch creation is estate work, needs org credentials, is not marked ASSISTED, and contradicts the charter

**File:** `lanes/L1-01-repo-skeleton.md`
**Task id:** `L1-01-02`

**Problem.** Three separate faults in one task.

1. **Credential/console work handed to a low-cost agent.** T02 runs `gh repo create "$CP_ORG/$CP_REPO" --private --source . --push`, requiring an authenticated `gh` session with organisation repo-creation rights, and then `git branch integration main && git push -u origin integration`. This is exactly the class of work that the review criteria require to be flagged **ASSISTED** — a human with console/credential access performs it. T02 carries a DECISION REQUIRED for the *value* of `CP_ORG` but nothing about the *permission* to act, and its STOP rule anticipates `HTTP 403` as a runtime surprise rather than a precondition.
2. **It creates `integration`,** which PARTITION line 22 assigns to **L0 Integrator** (`main`, `integration`). L1 does not own the branch model.
3. **It directly contradicts the charter.** `L1-00-01` STOPS unless `contracts/` exists and is non-empty *and* `git rev-parse --verify integration` succeeds — i.e. it asserts L0 has already landed Phase 0 and created `integration`. `L1-01-02` assumes neither exists and creates both. Two L1 documents disagree on whether the repository exists at the moment the lane starts.

**Correction.** Move repository creation, `integration` branch creation and org configuration to L0 Phase 0 (or to L5 if the estate is L5's), and mark whatever remains **ASSISTED**. Reduce `L1-01-02` to a clone-and-verify task with the same preconditions as `L1-00-01`. Delete the `gh repo create` branch entirely.

---

## D11 — HIGH — The 29-artifact rule is violated by four `registries/**` files, one of them by the document that states the rule

**Files:** `L1-05-tasks.md` §0.7 (the rule) vs `L1-05-tasks.md` §L1-505, §L1-704, §L1-902; `L1-01-repo-skeleton.md` §L1-01-07; `L1-04-ci-gate-engine.md` §1.1

**Problem.** `L1-05` §0.7 is unambiguous, and it is right about the spec (§52.6 line 4615: *"This table is the complete inventory — twenty-nine entries"*):

> *"**No task in this lane creates a thirtieth control-plane artifact.** Anything that looks like it needs one is a STOP. … Files under `registries/**` do [count]."*

Five tasks then create new `registries/**` files:

| Task | File | Document |
|---|---|---|
| `L1-01-07` | `registries/INVENTORY.md` | L1-01 |
| `L1-05-L1-505` | `registries/OWNERS.yaml` | L1-05 |
| `L1-05-L1-704` | `registries/INVENTORY.yaml` | L1-05 |
| `L1-05-L1-902` | `registries/invariants.yaml` | L1-05 |
| `L1-04-06` | `registries/canary/seeded-canary.yaml` | L1-04 |

Three of the five are created by the very document whose §0.7 forbids them. `INVENTORY.md` and `INVENTORY.yaml` are also the same artifact authored twice in two formats by two documents.

**Correction.** Either relocate all five under `validators/registry/**` (which §0.7 explicitly exempts: *"Schemas, validators and fixtures are not control-plane artifacts"*), or raise a single DECISION REQUIRED to L0 asking whether §52.6's inventory admits tooling manifests. Do not leave a STOP rule the plan's own tasks trip.

---

## D12 — HIGH — `schemas/registry/index.json` is a shared mutable index, banned by PARTITION rule 3

**File:** `lanes/L1-02-schemas.md`
**Task id:** `L1-02-19`

**Problem.** T19 creates `schemas/registry/index.json`, a single file enumerating every schema in the lane, and the phase-exit gate reads it:

```bash
set -euo pipefail
node -e "require('./schemas/registry/index.json').schemas.forEach(...)"
```

PARTITION.md line 27: *"**No shared mutable file, ever.** No lane appends to a shared index, list, or registry-of-everything. Directory-per-item only … This is why merges cannot conflict."*

`L1-02` §1 states T03–T18 *"are mutually independent and may be executed in any order after T02. They are separate branches and separate PRs."* Sixteen parallel branches each appending an entry to `index.json` is the precise merge-conflict generator PARTITION rule 3 exists to prevent. `L1-04-ci-gate-engine.md` §0 even lists *"No shared mutable index — directory-per-item only | PARTITION rule 3"* as an obligation it implements — while a sibling L1 document builds one.

The same objection applies to `validators/registry/RULES.md` in `L1-05`, which twelve tasks are each told to append rows to, and to `validators/registry/rules_manifest.yaml` in `L1-03`, edited by eighteen tasks.

**Correction.** Replace `index.json` with directory-per-item discovery (glob `schemas/**/*.schema.json` at gate time). Replace `RULES.md` and `rules_manifest.yaml` appends with per-rule sidecar files that a generator reads. Keep the completeness test; drop the shared file.

---

## D13 — HIGH — L1-06 claims the operational asset inventory, which the charter assigns to L5

**File:** `lanes/L1-06-tests.md`
**Task ids:** `L1-06-01` (schema id 15, `assets`), `L1-06-08` (title: *"Negative corpus: os-health, **assets**, and the people-boundary denials"*; fixture `assets/asset-no-owner-no-expiry` at line 1252)

**Problem.** `L1-00-charter.md` §4 "Explicitly NOT owned — do not touch" states:

> `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**` | **L5** | Section 49 (4334–4369) asset inventory is L5's `assets/**`.

`L1-06` §2.1 nonetheless lists `assets` as id 15 of the 18 schema ids the corpus asserts must exist, anchored to §39.1/§49.1, and `L1-06-01` STOPS if it is missing. The schema file itself would sit inside an owned prefix, so lane-guard will not catch it — this is a *scope* violation that only a human reading the charter detects, which makes it more dangerous, not less. It also guarantees a duplicate: L5 is presumably authoring the same schema.

**Correction.** Remove `assets` from `L1-06` §2.1 (18 ids → 17, or 14 after D8) and delete the asset fixtures from `L1-06-08`. If L1 is genuinely meant to own the asset-inventory *schema* while L5 owns the *data*, the charter §4 row must be changed by L0 first.

---

## D14 — HIGH — Four field definitions are contradicted between L1 documents

**Files:** `L1-02-schemas.md` §L1-02-05 vs `L1-05-tasks.md` §L1-301/L1-303/L1-307; `L1-03-validators.md` §L1-03-08 vs `L1-05-tasks.md` §L1-104

| Field | One document says | The other says | Severity |
|---|---|---|---|
| `classification.class` | **closed enum** `internal\|experimental\|commercial\|strategic\|regulated\|legacy` (L1-02-05) | **open string.** L1-301's STOP: *"file the blocker if you are about to constrain `classification.class` to an enum. That breaks §15.3 and invariant 53"* | Direct, named contradiction — one document's deliverable is the other's STOP condition |
| `recovery` when absent | `object \| **`not-applicable`** (string literal)` (L1-02-05) | `object or **null**` (L1-307) | Fixtures written for one fail the other |
| `verification.automated` | `const: required` (L1-02-05) | `enum [required, optional, not-applicable]` (L1-303) | L1-03's baseline uses `required`; L1-02 forbids the other two |
| `work_arrangement.accepted_coverage_window` | **object** `{days, start, end, timezone}` (L1-03-08, which rewrites the baseline with exactly that shape) | **`string or null`** (L1-104 schema shape) | The rota validator reads a type the schema rejects |

**Problem.** These are not stylistic. `L1-301`'s STOP rule instructs the executor to file a blocker on seeing precisely what `L1-02-05` instructs a different executor to write. Whichever lands second on `integration` breaks the other's fixtures.

**Correction.** Reconcile all four against the spec before dispatch. On `classification.class`, §15.3 and invariant 53 (*"New products are configuration plus onboarding, never platform redesign"*) side with L1-05: the enum in L1-02-05 is wrong and must be relaxed to a string with the six values documented as illustrative.

---

## D15 — HIGH — `L1-03-08` invents the rota shape that `L1-05-D03` declares a hard block

**Files:** `L1-03-validators.md` §L1-03-08 vs `L1-05-tasks.md` §1 (DECISION REQUIRED L1-D03) and §L1-311

**Problem.** `L1-05-D03` is marked **HARD BLOCK** and is correct on the facts. §52.6's `people.yaml` row does require *"per-product rota membership for funded coverage — each member's accepted window, the paging-path identifier and the funding decision record (Section 47.9)"*, and §47.9 names those three things without ever spelling their field names. L1-05 concludes, rightly:

> *"choosing between them, and naming the three fields §47.9 describes but does not name … is schema design. §15.5 and AT-047 both hang a CI failure on the result, so guessing produces a validator that fails the acceptance test."* — `L1-311` is not startable until L0 answers.

`L1-03-08` guesses all of them anyway, and hard-codes the guess into the baseline fixture:

```yaml
rotas:
  - product: product-1
    paging_path: pager-primary-p1
    funding_decision_record: records/decisions/2026-03-04-fund-p1-rota.yaml
    members: [dev-a, dev-b]
```

plus `accepted_coverage_window` as a four-key object. Four invented field names (`rotas`, `paging_path`, `funding_decision_record`, `members`) and one changed field type, authored by a lane member with, per PARTITION line 44, *"no judgment authority."*

**Correction.** `L1-03-08` must carry the same hard block as `L1-311`, citing `L1-D03`. Remove `rotas: []` and the object-valued `accepted_coverage_window` from the `L1-03-01` baseline until L0 answers. This is the highest-value single L0 decision in the lane — it gates AT-047, invariant 31, SIG-14 and two tasks in two documents.

---

## D16 — MEDIUM — Six arithmetic errors in acceptance criteria that will deadlock a literal executor

**File:** `lanes/L1-05-tasks.md`

| Task | Stated | Actual | Evidence |
|---|---|---|---|
| §2 Totals | *"S = 14, M = 26, L = 21"* | **S = 11, M = 31, L = 19** | Counted from the master table's Size column; total 61 is right, the split is not |
| `L1-106` | CORRECT OUTPUT `REQ=6` | **5** | Top-level required properties are `platform_version`, `supported_contract_versions`, `reusable_workflow_versions`, `canary_set`, `event_type`. The executor will invent a sixth or loop |
| `L1-301` | *"exactly 15 functions"*, `15 passed` | **14** fixture cases listed | 2 valid + 12 invalid |
| `L1-307` | *"exactly 14 functions"*, `14 passed` | **16** fixture cases listed | 3 valid + 11 invalid + 2 boundary valid (`high_exactly_90`, `critical_exactly_30`) |
| `L1-310` | *"exactly 26 functions"*, `26 passed` | **16** fixture cases listed | 1 valid + 15 named cases. Ten tests have no fixture |
| `L1-901` | *"the **14** ATs Lane 1 can prove"*, `14 passed` | Charter §9.2 lists **13** | Charter: AT-001, 007, 008, 009, 016, 025, 034, 047, 049, 051, 071, 075, 090 |

**Problem.** Every one of these is a `CORRECT OUTPUT` block the executor is told to match *"character for character"* (§0 step 3). A mismatch triggers §0 step 4 — re-run twice, then file a blocker — so each of these six is a guaranteed, avoidable blocker. `L1-307` additionally lists `high_91_days` and `high_exactly_91` as separate cases testing the same condition, and likewise `critical_31_days`/`critical_exactly_31`.

**Correction.** Recount and correct all six. Add a mechanical check: for every task, `count(fixture cases) == stated test count`.

---

## D17 — MEDIUM — `L1-310` has an undeclared dependency on a task that runs five positions later

**File:** `lanes/L1-05-tasks.md`
**Task ids:** `L1-310` (row 30) and `L1-404` (row 35)

**Problem.** `L1-310`'s rule `R-REF-03` is defined as: *"`dependencies.internal[]` absent from `registries/services/*/service.yaml` ids"*. The directory `registries/services/` and the service schema are created by `L1-404`, which the master table places at row 35 with `DEPENDS: L1-302`. `L1-310` declares `DEPENDS: L1-309, L1-206`. Working strictly top-to-bottom as §0 instructs, the executor reaches `L1-310` with no `registries/services/` in the tree; the `service_missing/` fixture and the `valid/fully_resolved/` fixture both become unwritable.

No dangling *task ids* were found anywhere in L1 — every `DEPENDS` value resolves, and no dependency points forward. This is the one ordering fault.

**Correction.** Add `L1-404` to `L1-310`'s DEPENDS, and move `L1-404` above `L1-310` in the master table (it only needs `L1-302`, so this is a legal reorder).

---

## D18 — MEDIUM — Executability: `L1-05` describes ~200 fixture directories it never shows, with no baseline to derive them from

**File:** `lanes/L1-05-tasks.md`
**Task id:** `L1-310` (second of the two most complex tasks checked), and systemically `L1-101`–`L1-311`

**Problem.** `L1-05-tasks.md` contains **one** YAML code block in 2,003 lines — the `expect.yaml` example in `L1-005`. It contains no example `people.yaml`, no example `product.yaml`, no baseline fixture tree.

`L1-310` asks for 16 fixture directories. Each must contain a `product.yaml` that is **fully valid under the v2 schema** — 22 required top-level blocks accumulated across `L1-301`, `L1-302`, `L1-303`, `L1-304`, `L1-305`, `L1-306` and `L1-307` — because `L1-005`'s harness *"asserts the produced error set equals the expected set **exactly** — no extra errors, no missing errors."* A single missing block in any fixture produces an extra error and fails the case.

To build one such fixture the executor must reconstruct a complete v2 contract by merging seven separate prose tables spread across 600 lines, with no worked example and no way to check the result other than running a validator it also has to write. That is reconstruction from specification, not execution — and it must be done ~200 times.

By contrast `L1-03-01` **does** ship a literal baseline (`heredoc`s for `platform.yaml`, `roles.yaml`, `people.yaml`, `exceptions.yaml`, `service.yaml`, `product.yaml`) and a `make-fixture.sh` that copies it, so every later L1-03 fixture is baseline-plus-one-delta. I verified `L1-03-08`'s `str.replace()` surgery against that literal baseline and the strings match exactly, indentation included — that part is genuinely executable. **L1-03's pattern is the one L1-05 should adopt.**

**Correction.** Add a task, before `L1-301`, that writes a literal, complete, schema-valid `fixtures/_baseline/` tree and a `make-fixture.sh`. Re-express every fixture case in `L1-301`–`L1-311` as *baseline plus one named delta*. This also fixes D7.

---

## D19 — MEDIUM — Broken relative spec path in `L1-101`

**File:** `lanes/L1-05-tasks.md`
**Task id:** `L1-101`

```bash
set -euo pipefail
sed -n '689,730p' ../MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md 2>/dev/null || echo "SPEC NOT LOCAL - use the token lists printed in this task"
```

**Problem.** §0.1 sets `REPO_ROOT="$HOME/work/control-plane"` and every command block starts `cd "$REPO_ROOT"`. From there, `../MultiProduct/Research/…` resolves to `$HOME/work/MultiProduct/Research/…`, which does not exist. The `2>/dev/null ||` fallback masks the failure, so the executor silently proceeds on the in-document token list — which is, fortunately, correct (verified: 27 capability tokens, matching §9 lines 687–724 exactly). But the same broken idiom in a task where the in-document list were wrong would propagate a silent error.

`L1-01-repo-skeleton.md` §0.4 does this correctly: `export SPEC="/c/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"` with a `SPEC_OK`/`SPEC_MISSING` assertion.

**Correction.** Adopt L1-01's `$SPEC` convention across `L1-05`, and make a missing spec a STOP rather than a silent fallback. Also note the line range: `689,730` brackets the §9 table (which starts at 687), so the ranges are approximately but not exactly the charter's pinned anchors.

---

## D20 — MEDIUM — Four different repository-root conventions

**Files:** all five task-bearing documents

| Document | Variable | Value |
|---|---|---|
| `L1-00-charter.md` | none | *"root of the `control-plane` repository working tree"* |
| `L1-01-repo-skeleton.md` | `CP_ROOT` | `/c/D_Drive/PS/MultiProduct/control-plane` |
| `L1-03-validators.md` | `CP` | `$HOME/work/control-plane` |
| `L1-04-ci-gate-engine.md` | `CONTROL_PLANE_ROOT` | unset, never defined |
| `L1-05-tasks.md` | `REPO_ROOT` | `$HOME/work/control-plane` |
| `L1-06-tests.md` | `REPO_ROOT` | inherited, never defined in-file |

**Problem.** An executor moving between documents in one session has to re-export a differently-named variable pointing at a differently-located clone. `L1-01` clones to `/c/D_Drive/...`; `L1-03` and `L1-05` expect `$HOME/work/`. `L1-04` and `L1-06` never define theirs at all — `L1-06-01`'s very first line is `cd "$REPO_ROOT"` against an unset variable, which in `bash` without `set -u` silently `cd`s to `$HOME`.

**Correction.** One variable name, one location, defined once in the charter §11 conventions table, referenced by every document.

---

## D21 — LOW — `L1-002` FILES field disagrees with the master table, and duplicates a file `L1-005` also creates

**File:** `lanes/L1-05-tasks.md`
**Task ids:** `L1-002`, `L1-005`

**Problem.** Master table row 2 lists three files for `L1-002`; the task body's FILES field lists five, adding `validators/registry/rules/__init__.py` and `validators/registry/tests/__init__.py`. `L1-005`'s FILES field then lists `validators/registry/rules/__init__.py` again as something it creates. §0.3's postamble requires `git status --porcelain` after `git add` to show each file as `A ` or `M `; the second creation will show `M `, which the instruction does permit, but the file's authoritative content is now ambiguous between two tasks.

**Correction.** Align the master table with the body. Assign `rules/__init__.py` to exactly one task (`L1-005`, which defines its `discover()` contract) and have `L1-002` create only the directory.

---

## D22 — LOW — Three different lists of the acceptance tests L1 satisfies

**Files:** `L1-00-charter.md` §9.2 (13 ATs), `L1-05-tasks.md` §L1-901 (14 ATs), `L1-06-tests.md` §6 (a third list, plus `at-map.yaml` in `L1-06-14`)

**Problem.** The charter is the lane's accountability register — `DoD-5` requires *"Every AT in §9.2 of this charter has a fixture pair"*. If `L1-901` proves 14 and `L1-06-14` maps a different set, DoD-5 is unprovable because there is no agreed denominator.

**Correction.** The charter §9.2 table is authoritative. Make `L1-901` and `L1-06-14` read from it. All ATs cited are real (verified against spec §100, lines 9295–9442) — this is a count and set-membership disagreement, not a fabrication.

---

## D23 — LOW — Citation: the "ten §74.5 tokens" of D108 are nine in the spec

**File:** `lanes/L1-05-tasks.md`
**Task id:** `L1-302`

**Problem.** The task instructs: *"Encode `scope.decisions` … with a `not: {contains: {enum: [...]}}` over the **ten** §74.5 tokens: `recognition`, `promotion`, `role-change-employment`, `hiring`, `formal-warning`, `improvement-plan`, `exit-consideration`, `compensation`, `permanent-headcount`, `people-intelligence`."*

Spec §10.1's `founder_decision_delegate` row names **nine**: *"recognition, promotion, role change affecting employment responsibility or status, hiring, formal warning, improvement plan, exit consideration, compensation and permanent headcount."* The tenth, `people-intelligence`, comes from §74.5's "Layer B access delegation — **Not delegable** (D109)" row, which is a different decision (D109, not D108).

**This is handled correctly** — the task carries a conditional STOP requiring the executor to file `BLOCKER L1 L1-302: the D108 excluded-decision token list must be fixed by L0 from Section 74.5` and ship the list marked provisional. The defect is only that the prose asserts "the ten §74.5 tokens" as fact when nine come from §10.1 and one from D109.

**Correction.** Reword to *"nine tokens from the §10.1 `founder_decision_delegate` row plus `people-intelligence` from D109/§74.5, provisional pending L0."* Keep the STOP.

---

## D24 — LOW — Two invariant citations do not support the rule they are attached to

**File:** `lanes/L1-05-tasks.md`
**Task id:** `L1-004`

**Problem.** The strict YAML loader (rules `L-YML-01`…`L-YML-09`: duplicate keys, anchors, merge keys, tabs, BOM, multi-document, non-mapping root, trailing newline, encoding) cites **`SPEC: §5.2; invariant 45; invariant 47`**. Invariant 45 is *"No artifact becomes a dumping ground; the source-of-truth hierarchy resolves every conflict."* Invariant 47 is *"History is append-only for state, decisions, approvals and records."* Both exist and are quoted correctly elsewhere in the lane; neither concerns YAML parse ambiguity.

**Correction.** Cite §5.1 (registries as declared source of truth) and §64.1/invariant 80 (fail-closed on a malformed value), which do support the rule. Low severity — the rules themselves are sound and well specified.

---

## D-J — JUDGMENT LEAKAGE SUMMARY (check 5)

Four instances where a low-cost executor is required to design, choose or interpret. All four are named above; collected here for the dispatch decision.

| # | File / task | What the executor must invent | Escalated? |
|---|---|---|---|
| J1 | `L1-03-08` | The `rotas[]` block shape: 4 field names + a field type change (D15) | **No** — invented silently |
| J2 | `L1-03-08` acceptance criterion 4 | *"a fixture with `timezone: Europe/Dublin` … produces the same verdict whether `--as-of` falls in January or July"* — no command creates this fixture, no expected literal output is given, and the DST-correct interval union over `zoneinfo` is genuine algorithm design | **No** |
| J3 | `L1-02-09/T13/T14` | Field names for `os-health.yaml`, `economics.yaml`, `platform-roadmap.yaml` — the spec sections are prose, not YAML blocks | **Yes** — `DECISION-L1-02-C`, "ratification of planner-fixed field names". Adequate |
| J4 | `L1-06-05`–`T09` | Each `must_contain` string is *"recorded once, from the real validator output, at the moment the fixture is authored"* — choosing which substring of a diagnostic is stable is a judgment call, against a validator that does not exist yet (D6) | **Partially** — `DR-L1-06-B` raises the diagnostic-format question but the task proceeds regardless |

**ASSISTED marking.** `L1-01-02` (D10) is the one L1 task needing credentials and console access — org-level `gh repo create`, org membership, branch creation on a protected model. It is **not marked ASSISTED** and must be.

---

## CITATION INTEGRITY — FULL RESULT (check 6)

**PASS.** This is the strongest part of Lane 1 and should be preserved through any rewrite.

**Anchors.** I executed `L1-00-04`'s `check_spec_anchors.sh` logic against the frozen spec. **All 25 pinned anchors resolve to the exact line asserted** — §7→543, §8→634, §9→687, §10→725, §15→1284, §20→2027, §21→2113, §26.4→2526, §31→2741, §38.1→3373, §44.1→3963, §52.6→4613, §54→4746, §55→4830, §60→5119, §62.1→5289, §64.1→5433, §66.2→5508, §68.1→5624, §77→6339, §91.2→8079, §96.2→8720, §99.2→9184, §100→9295, §101→9443. Zero `ANCHOR-DRIFT`.

**Identifiers.** Every identifier cited anywhere in the eight L1 files exists in the spec:

* **40 AT ids** cited, all within AT-001…AT-110.
* **17 SIG ids** cited, all within SIG-01…SIG-46.
* **24 D ids** cited, all within D1…D112. (`D01`–`D05` are L1's own decision ids, not spec ids.)
* **32 invariant numbers** cited, all within 1…111.

**Sampled content claims — all verified correct against the spec text:**

| Claim | Where | Verified |
|---|---|---|
| 27 capability tokens, that exact list, that order | `L1-101` | §9 table, lines 687–724 — 27 exactly ✓ |
| 8 dangerous capabilities | `L1-101`, `L1-202` | §8 D106 bullet names exactly those 8 ✓ |
| 17 assignment types, that list | `L1-101`, `L1-302` | §10.1 *"in one table (17 types)"* ✓ |
| 9 types requiring non-null `end_date` | `L1-302` | §10.1 "Expires cleanly" column: 7 "mandatory" + 2 "on `end_date`" ✓ |
| 11 roles, `founder` default carries 3 dangerous capabilities | `L1-103` | §8 YAML block ✓ — and the D106 contradiction `L1-103` flags is real and correctly refuses to resolve it |
| Error pointers `/roles/0/default_capabilities/3,5,6` | `L1-202` | Indices of `lifecycle-decision`, `exceptional-approval`, `people-intelligence` in the §8 `founder` list ✓ |
| 7 conformance profiles | `L1-301`, `L1-308` | §15.7 table ✓ (note §15.1's inline comment shows only 4 — §15.7 governs) |
| 11 exception types | `L1-108` | §54.1 YAML comment block ✓ |
| "twenty-nine entries" | `L1-05` §0.7 | §52.6 line 4615 verbatim ✓ |
| AT-009, AT-016, AT-025, AT-034, AT-047, AT-049, AT-071, AT-075, AT-090, AT-102, AT-014, AT-077, AT-078 | charter §9.2, L1-05, L1-06 | §100 rows, all quoted accurately ✓ |
| Invariants 4, 7, 11, 31, 37, 50, 51, 52, 58, 73, 77, 78, 79, 80, 96, 98/99, 106 | charter §9.1 | §101, all abbreviated accurately ✓ |
| §52.6 `people.yaml` row names per-product rota without field names | `L1-D03` | Verified — the hard block is legitimate ✓ |
| `ai-toolchain.yaml`, `changes/*.yaml`, `scenarios/*.yaml`, Leave records are in §52.6 with no PARTITION owner | charter §12 #1, #3 | Verified — both DECISION REQUIRED items are legitimate ✓ |

**No invented identifier was found anywhere in Lane 1.** The two soft issues are D23 (a count attributed to the wrong section) and D24 (two invariants cited for a rule they do not govern).

---

## WHAT IS GOOD, AND SHOULD SURVIVE THE REWRITE

Stated so the rework does not discard it:

1. **`L1-00-charter.md` is excellent** — the owned-path table, the DoD-1…DoD-11 command-provable checklist, the invariant/AT/SIG/D accountability tables, and the spec-anchor drift check (`L1-00-04`) are all correct and verified. Keep it as the lane's constitution.
2. **Every task body that exists carries both a SELF-VERIFY block and a STOP rule.** 127/127. This is rare and it is right.
3. **`L1-103`'s unconditional blocker** on the §8-vs-D106 `founder` contradiction is exactly the correct handling of a real spec contradiction: transcribe verbatim, refuse to resolve, state both candidate resolutions without choosing, `xfail` the dependent fixture, keep going.
4. **`L1-05-D03`'s hard block** on the rota shape is correctly identified and correctly refused.
5. **`L1-03-01`'s literal baseline fixture + `make-fixture.sh`** is the right pattern for the whole lane (D18).
6. **`L1-04`'s negative-test discipline** — the universal must-fail recipe (*"overwrite the first file its `applies_to` matches with the literal `INVALID: [`"*) is genuinely judgment-free and mechanically constructible for any rule. Preserve it whichever engine survives D2.
7. **`L1-05-L1-204`'s instruction** — *"Do not invent a verdict for any pairing not covered by the three rules above — an uncovered pairing produces zero errors, and that is correct"* — is model phrasing for a no-judgment executor.

---

## MINIMUM SET TO UNBLOCK

| Order | Action | Closes |
|---|---|---|
| 1 | L0 picks **one** validator engine, language, invocation contract and exit-code table; writes it to `contracts/**` | D2, D4, D6 |
| 2 | L0 fixes **one** schema naming convention and directory layout in `contracts/**` | D5, D6 |
| 3 | Author the 30 missing `L1-05` task bodies, or delete the rows and re-scope | D1 |
| 4 | Collapse to one task-id scheme and one dispatch surface | D3, D20, D22 |
| 5 | L0 answers charter DECISION #1 and #3 (`ai-toolchain`, `changes`, `scenarios`) and `L1-D03` (rota shape) | D8, D15 |
| 6 | Move repo/branch creation to L0 or L5; mark residual credential work **ASSISTED** | D10 |
| 7 | Split `schemas/.gitignore`; add the lane-guard assertion to `L1-01-04` | D9 |
| 8 | Replace `index.json`, `RULES.md` appends and `rules_manifest.yaml` appends with directory-per-item | D12 |
| 9 | Add a literal baseline fixture task before `L1-301`; re-express all fixtures as baseline-plus-delta | D7, D18 |
| 10 | Recount the six arithmetic errors; reconcile the four contradicted field definitions | D14, D16 |

---

**Reviewed against:** `PARTITION.md` (frozen, v1) and `MultiProduct_MasterSpec_v4.0.md` (10,214 lines).
**Files read in full:** 8 L1 documents, 12,213 lines.
**Verdict: BLOCKED.**
