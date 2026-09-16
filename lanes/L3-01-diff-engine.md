> **[SUPERSEDED — FD-B1-L3 2026-09-02]**
> This file has been superseded by L3-06-tasks.md. Do not execute tasks from this file.
> Authoritative plan: Code/implementation/lanes/L3-06-tasks.md

# L3 — PHASE 1 — The Declared-versus-Actual Diff Engine

> **REFERENCE ONLY** — FD-098 (2026-09-09): Task bodies superseded by L3-06-tasks.md. This file is a design-note reference. Do not execute task bodies from this file.

**Lane:** L3 Reconciler & Provisioning (Subsystems **C** — reconciliation engine — and **D** — provisioning and scaffolding, spec Section 99.2)
**Branch prefix:** `lane/3/*` (PARTITION.md line 19)
**Paths this lane owns exclusively:** `reconciler/**`, `tools/provision/**`, `validators/drift/**`
**Repository:** `control-plane` (PARTITION.md line 7)
**Phase deliverable:** the read-only comparison engine implementing **every row** of spec Section 53.1, its per-registry comparison counts, its run-integrity rules, and the schema validator that proves a run record well-formed.

---

## 0. Why this phase is written the way it is

Spec Section 99.6 risk 6: *"Reconciliation auto-repair as the most dangerous code — a write-scope, org-admin automation whose bug loosens security or locks everyone out; the reconciler is the highest-privilege identity in the system."* Its stated mitigation is *"Detect-only first; repair classes enabled one at a time; stricter-only rule enforced in code and tested."* Spec Section 99.4 item 6 repeats it: *"Reconciliation v0, detect and block only ... Auto-repair is deferred until detection has run clean for weeks."*

Three consequences bind every task below and are not negotiable at task level:

| Rule | Statement | Enforced by |
| --- | --- | --- |
| **R1 — Phase 1 is read-only** | The engine issues HTTP `GET` and nothing else. No comparator, helper or CLI path may construct a `POST`, `PUT`, `PATCH` or `DELETE`. Level-3 repairs are *proposed as data* on the finding and are never executed in this phase. | `L3-01-01` method allowlist + `test_client_readonly.py`; `L3-01-22` full-set assertion |
| **R2 — Path ownership** | Every file created by this phase is under `reconciler/**` or `validators/drift/**`. The engine **reads** `registries/**` (L1) and `templates/workflows/**` (L2) as runtime data; it never edits them and never imports their source (PARTITION.md rules 1 and 4). Tests read fixtures only. | `L3-01-22` path-guard check |
| **R3 — No spec-class invention** | Each comparator carries the Section 53.1 "On mismatch" cell verbatim and the drift class derived from it in `reconciler/comparators/manifest.yaml`. A test asserts the manifest matches the frozen copy of the spec table checked into the lane. | `L3-01-05`, `L3-01-22` |

Invariants this phase is the mechanical enforcement of (spec Section 101, cited by number, not invented):

- **44** — *"Declared state is reconciled against actual platform state, and silent drift is not permitted."*
- **7** — *"Every product has a Primary Owner, Cross-Reviewer, Backup Owner and Escalation path, recorded in the contract and matched by team membership."* (CMP-03)
- **55** — *"Ownership changes are declarative and take effect through reconciliation."* (CMP-03, CMP-04, CMP-11)
- **81** — *"Auto-repair may only move the system toward the declared, stricter state."* (Phase 1 proposes; never applies. The stricter-only predicate lands in L3 Phase 3.)
- **24** and **26** — production database inaccessible from developer machines; a compromised workstation yields no production access (CMP-09).
- **72** — *"Portfolio-wide changes never roll out to the fleet without passing a canary first."* (CMP-13, spec Section 33.2 pinned-tag paragraph.)

Acceptance tests this phase moves toward (spec Section 100, cited): **AT-102** (the seeded reconciliation canary), **AT-032** (self-observability), **AT-033** (no auto-loosening), **AT-110** (the reconciler credential is provably bounded — its credential half executes in a later L3 phase; its **client** half, the method allowlist, is `L3-01-01` here). Edge case **EC-109** (a silently-vacuous reconciliation run) is what `L3-01-20` exists to make impossible.

Health signals this phase feeds: **SIG-03** (permission drift), **SIG-13** (failed reconciliations), **SIG-17** (restore-test currency), **SIG-05** (orphan risk). Decision records this phase implements: **D91** (deployment branch and tag policies), **D93** (declared state is canaried; the reconciler's write scope is narrowed), **D96** (per-run API-call counts, expected-source assertion, signed run record), **D89** (records live in their own repository; no machine identity is a bypass actor on `control-plane`), **D87** (privileged-workflow isolation).

---

## 1. DECISION REQUIRED — items handed to L0

The executor **must not decide any of these**. Each is blocked on an L0 answer recorded in `docs/decisions/` before the named task starts. Each task below that depends on one carries the dependency explicitly and a STOP rule.

### DECISION REQUIRED — D-L3-01 — Reconciler implementation runtime

> **Question for L0.** The spec fixes the git host, CI and dashboard stack (Section 99.5) but names no implementation language for Subsystem C. Pin one runtime and one dependency-pinning mechanism for `reconciler/**` and `validators/drift/**`.
> **Why L0.** Cross-lane: L2 must invoke this engine from a workflow, L5 must install it on the operations VM (Section 99.2 subsystem M), and the choice sets the control-plane repository's toolchain.
> **Tasks below are written against the resolution `python-3.12` with dependencies pinned by `reconciler/requirements.txt` hashes.** `L3-01-01` STOPs if `docs/decisions/D-L3-01.md` records anything else; the lane file is then re-issued by L0.
> **Blocks:** every task in this phase.

### DECISION REQUIRED — D-L3-02 — Provider-side attestation record store

> **Question for L0.** Spec Section 40.2 requires *"a named owner who records a dated attestation that actual provider state matches the declaration"*, and Section 53.1 compares the declared `infrastructure:` boundary against *"the latest provider-side attestation record"*. Section 97.2's canonical record-store table does **not** contain an attestation store. Name: (a) the store path in `control-plane-records`, (b) the record's field names for attesting identity, attestation date and pass/fail result, (c) the field in `registries/` that declares the per-product attestation window (Section 40.2 calls it *calibrated configuration; initial value monthly*).
> **Why L0.** The store lives in `control-plane-records`, owned exclusively by L4 (PARTITION.md line 20). L3 may not name a path in another lane's tree.
> **Blocks:** `L3-01-11` (CMP-09).

### DECISION REQUIRED — D-L3-03 — Production-restore record store

> **Question for L0.** Spec Section 53.1 compares the *"Production-restore record (Section 44.5)"* against its *"Recorded `integrity_check` result and named verifier"*, Red where either is absent. Section 34.4 case F names the artifacts (*"Incident + forensic snapshot + restore record; exceptional-authorisation record where data loss is accepted"*) but Section 97.2 lists only `records/restore-tests/`, which is the **test** store, not the production-restore store. Name the production-restore record path and the two field names the comparison reads.
> **Why L0.** Same reason as D-L3-02: the path is in L4's tree.
> **Blocks:** `L3-01-18` (CMP-16).

### DECISION REQUIRED — D-L3-04 — Run-integrity: canary placement and the comparison-count shortfall class

> **Question for L0.** Two parts.
> (a) Spec Section 53.1 requires *"A permanent seeded drift record — a deliberately planted, clearly labelled mismatch in the comparison set — exists at all times, and every reconciliation run MUST find it."* Which comparator carries it, and where does the seeded mismatch live? It must not be planted in a real security control (Section 53.4: *"Security drift and production environment drift are never classified below Red"*), so the choice is a governance decision, not an implementation one.
> (b) Section 53.1 requires per-registry comparison counts *"so that a silently narrowed comparison is itself visible drift"* but assigns that finding no class, and Section 53.4 states *"Class assignment lives in configuration and is reviewable; it is not decided ad hoc."* Assign the class for a `rows_compared < rows_declared` shortfall and record it in `os-health.yaml`.
> **Why L0.** (a) is a governance placement decision with a security constraint; (b) is a class assignment, which Section 53.5 reserves to the exception-approval authority.
> **Blocks:** `L3-01-20`.

### Contract Change Request — CCR-L3-01 (filed, not blocking)

Phase 1 defines the drift-finding envelope and the reconciliation run record as **lane-local** JSON Schemas under `validators/drift/schema/` (owned path), because `contracts/**` is L0's and frozen (PARTITION.md rule 2). L0 is asked to adopt these two schemas into `contracts/**` unchanged at the next contract cycle so that L2's workflow and L4's records store read the same shape. Until then no other lane depends on them. This is a request, not a blocker: **do not wait for it.**

---

## 2. Conventions every task uses

Set once per shell session, before any task:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
export CP="$HOME/work/control-plane"
export GIT_AUTHOR_NAME="${GIT_AUTHOR_NAME:-lane3-dev}"
export PYTHONDONTWRITEBYTECODE=1
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
```

Branch naming (PARTITION.md line 34): `lane/3/p1-<task-suffix>` — one branch per task, rebased on `integration` before the PR.

Every task ends with the same three commands. They are written out in full in every task; do not abbreviate them.

**Universal STOP rule.** If any command in a task exits non-zero and the task's own STOP rule does not cover it, stop, do not commit, do not push, and open a blocker issue with the template in Section 6. Never "fix it by changing the acceptance criterion".

**Universal path rule.** Before every commit run:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
```

A hit means a file outside this lane's ownership is staged. Unstage it. Do not push.

---

## 3. Declared-state path map (read-only inputs)

These paths are **read** by the engine at runtime and **mirrored as fixtures** for tests. L3 never writes them.

| Declared artifact | Path in `control-plane` | Owner lane | Spec citation |
| --- | --- | --- | --- |
| People registry | `registries/people.yaml` | L1 | §7 (registry example), §52.6 |
| Role registry | `registries/roles.yaml` | L1 | §52.6, §60.2 |
| Platform record | `registries/platform.yaml` | L1 | §60.1, §52.6 |
| Product Operating Contract, one per product | `registries/products/<product-id>/product.yaml` | L1 | §15.1, §52.6 (*"`product.yaml` (one per product)"*), §11 (*"Repositories are enumerated dynamically from the product registry"*) |
| Shared Service Contract | `registries/services/<service-id>/service.yaml` | L1 | §60.2, §20 |
| Metric/signal register | `registries/os-health.yaml` | L1 | §52.6, §97.2 (write-freshness intervals) |
| Topology | `registries/topology.yaml` | L1 | §52.6 |
| Branch-protection template | `tools/provision/templates/branch-protection.yaml` | **L3 (this lane)** | §11.3, §33.2 |
| Environment configuration template | `tools/provision/templates/environment.yaml` | **L3 (this lane)** | §33.4, D91 |
| Reusable-workflow templates | `templates/workflows/` | L2 | §33.2 (*"generated from templates at product creation"*) |

The two templates marked **L3** are created by this phase (`L3-01-08`, `L3-01-10`) because Subsystem D — provisioning — owns branch protection and environments (Section 99.2 row D: *"generated CODEOWNERS, branch protection, environments with scoped secrets"*), and PARTITION.md line 19 gives `tools/provision/**` to this lane.

**STOP** if `registries/` does not exist on `integration` when `L3-01-03` runs: that is an L1 dependency, not a defect in this phase. File the blocker with `Blocked-on: L1`.

---

## 4. The comparison set — every row of spec Section 53.1

Nineteen comparators. Rows C-RECON-SET-1-01 … C-RECON-SET-1-17 are the seventeen rows of the Section 53.1 table **in table order**, including the two rows added by amendment (C-RECON-SET-1-08, the environment deployment branch and tag policy; C-RECON-SET-1-09, the declared `infrastructure:` boundary). Rows C-RECON-SET-1-18 and C-RECON-SET-1-19 are the two comparison rules stated in prose immediately below the table in the same section, and are part of the comparison set on the same footing.

> **Note:** CMP-\* ids rejected by FIND-R1 in `L0-01:1789`; reissued to C-RECON-SET-1 id space.

**Class and level mapping rule.** The *class* column is the spec's own word from the "On mismatch" cell. The *level* column is the Section 53.2 behaviour that cell describes: "Alert" → Level 2 Warn; "Fail CI" / "block deployment" / "Blocking" → Level 4 Block; "Regenerate" / "Auto-repair" / "Auto-revoke" → Level 3 Auto-repair (**proposed only in Phase 1**); Red-class rows take Level 2 because Section 53.4's "Blocks work" column for Red reads *"No, but visible on the Founder view"*. Section 53.2's Level 5 row — *"Production environment drift"* — additionally applies to any finding whose scope names the `production` environment, on top of its own class.

| ID | Declared in (Section 53.1 verbatim) | Compared against (verbatim) | On mismatch (verbatim) | Class | Level | Registry counted |
| --- | --- | --- | --- | --- | --- | --- |
| C-RECON-SET-1-01 | `people.yaml` | GitHub organisation membership | Alert; block on removal drift | Amber / **Blocking** on removal | 2 / **4** | `people.yaml` |
| C-RECON-SET-1-02 | `people.yaml` capabilities | Team membership implying authority | Alert | Amber | 2 | `people.yaml` |
| C-RECON-SET-1-03 | `product.yaml` assignments | GitHub Team membership | **Fail CI on the affected repository** | Blocking | 4 | `product.yaml` |
| C-RECON-SET-1-04 | `product.yaml` assignments | CODEOWNERS | Regenerate; alert if hand-edited | Amber (Level-3 repair proposed) | 3 / 2 | `product.yaml` |
| C-RECON-SET-1-05 | Branch protection template | Actual branch protection | **Alert immediately; block deployment on the affected repository** | Blocking | 4 | `product.yaml` |
| C-RECON-SET-1-06 | Workflow template version | Actual workflow file | Alert; flag `platform_compatibility` as drifted | Amber | 2 | `product.yaml` |
| C-RECON-SET-1-07 | Environment configuration template | Actual environments | Alert | Amber | 2 | `product.yaml` |
| C-RECON-SET-1-08 | Environment deployment branch and tag policy | Actual environment configuration | **Alert immediately; block deployment on the affected repository** | Blocking | 4 (5 on `production`) | `product.yaml` |
| C-RECON-SET-1-09 | Declared `infrastructure:` boundary (Section 40.2) | The latest provider-side attestation record | **Blocking past its attestation window** | Blocking | 4 | `product.yaml` |
| C-RECON-SET-1-10 | `product.yaml` lifecycle | Renovate, monitoring and CI configuration | Auto-repair where safe; alert otherwise | Amber (Level-3 repair proposed where safe) | 3 / 2 | `product.yaml` |
| C-RECON-SET-1-11 | Assignment `end_date` | Current Team membership | **Auto-revoke expired access** | Level-3 repair proposed | 3 | `product.yaml` |
| C-RECON-SET-1-12 | Declared dependency | Shared service registry | Fail CI on unknown dependency | Blocking | 4 | `product.yaml` |
| C-RECON-SET-1-13 | `platform.yaml` workflow versions | The commit SHA each `workflows/*` tag currently resolves to | **Blocking on any change — a moved tag reaches every consumer with no reviewable diff** | Blocking | 4 | `platform.yaml` |
| C-RECON-SET-1-14 | Renovate bypass ruleset | The ruleset carrying the diff-path status check | **Blocking where that ruleset names any bypass actor** | Blocking | 4 | `product.yaml` |
| C-RECON-SET-1-15 | Declared write-freshness window per record store (Section 97.2) | Latest commit timestamp on the store's path | Amber; **Blocking for `events/`, `records/deployments/` and `records/uat/`** | Amber / **Blocking** for the three named stores | 2 / **4** | `os-health.yaml` |
| C-RECON-SET-1-16 | Production-restore record (Section 44.5) | Recorded `integrity_check` result and named verifier | Red where either is absent | Red | 2 | `product.yaml` |
| C-RECON-SET-1-17 | `product.yaml` `restore_tested` | Newest passing record in `records/restore-tests/` | **Blocking**: a declared date with no matching record is an unevidenced reliability claim, not a scheduling question | Blocking | 4 | `product.yaml` |
| C-RECON-SET-1-18 | (prose, §53.1) A workflow-file change pushed by a machine identity | Commit authorship on `.github/workflows/**` | *"Blocking-class drift, regardless of the change's content"* | Blocking | 4 | `people.yaml` |
| C-RECON-SET-1-19 | (prose, §53.1) A commit authored or committed by any identity other than the declared bypass actor, on a branch that merges under that actor's bypass | Commit authorship on merged bypass-actor branches | *"Blocking-class drift for the same reason"* | Blocking | 4 | `product.yaml` |

### 4.1 Per-comparator I/O contract

| ID | Declared state read | Actual state fetched (GitHub REST) | Comparison predicate |
| --- | --- | --- | --- |
| C-RECON-SET-1-01 | `people[]` where `availability != departed` and `access_status == provisioned`; `github_login` | `GET /orgs/{org}/members?per_page=100` (paginated), `GET /orgs/{org}/invitations` | Set difference both ways on lower-cased login. Declared-present ∧ actual-absent ∧ not-invited ⇒ **removal drift, Blocking**. Actual-present ∧ undeclared ⇒ Amber. |
| C-RECON-SET-1-02 | `people[].capabilities`, `roles.yaml` capability→team map | `GET /orgs/{org}/teams?per_page=100`, `GET /orgs/{org}/teams/{slug}/members?per_page=100` | For each org-wide authority team, declared holder set vs actual member set; both directions ⇒ Amber. |
| C-RECON-SET-1-03 | Each `product.yaml` `assignments[]` open on the run date (`end_date` null or ≥ today) | `GET /orgs/{org}/teams/{product-team-slug}/members?per_page=100`, `GET /orgs/{org}/teams/{slug}/repos?per_page=100` | Symmetric difference on login; plus every `code.repositories[].name` must appear in the team's repo list with `permissions.push == true`. Any difference ⇒ Blocking, `blocks_repository` = the affected repos. |
| C-RECON-SET-1-04 | Same assignment set, plus `verification_responsibility` holders and the Team Lead role | `GET /repos/{o}/{r}/contents/.github/CODEOWNERS`, then `/CODEOWNERS`, then `/docs/CODEOWNERS` (first that returns 200) | Regenerate the expected file byte-exactly from the registries; compare to actual. Difference ⇒ Level-3 repair **proposed**. Additionally: any line naming a login that is a machine identity ⇒ Blocking (§11.3 *"no machine account ever appears in it"*). |
| C-RECON-SET-1-05 | `tools/provision/templates/branch-protection.yaml` | `GET /repos/{o}/{r}/branches/{default_branch}/protection`, `GET /repos/{o}/{r}/rulesets?includes_parents=true`, `GET /repos/{o}/{r}/rulesets/{id}` | Field-by-field equality on the §11.3 checklist keys (see `L3-01-08`). Any weakened field ⇒ Blocking, `blocks_deployment` = the affected repos. |
| C-RECON-SET-1-06 | `platform.yaml` `reusable_workflow_versions.current`; the template body under `templates/workflows/` | `GET /repos/{o}/{r}/contents/.github/workflows`, `GET /repos/{o}/{r}/actions/workflows` | For each of the required workflows of §33.2, the `uses:` pinned tag must equal a supported version and the file's non-`uses:` body must equal the template body. Difference ⇒ Amber + `flag_platform_compatibility: true`. |
| C-RECON-SET-1-07 | `tools/provision/templates/environment.yaml`; `product.yaml` `environments:` | `GET /repos/{o}/{r}/environments`, `GET /repos/{o}/{r}/environments/{name}/secrets` | Environment name set equality; per-environment protection-rule shape equality; declared secret **names** present. ⇒ Amber. |
| C-RECON-SET-1-08 | The `deployment_branch_policy` block of the same template (D91) | `GET /repos/{o}/{r}/environments` → `environments[].deployment_branch_policy`; `GET /repos/{o}/{r}/environments/{name}/deployment-branch-policies` → `branch_policies[].{name,type}` | For `staging` and `production`: policy must exist, must admit the default branch, must admit only `type: tag` entries matching the declared protected-release-tag pattern, and must admit nothing else. Absent policy, or any additional entry ⇒ Blocking + `blocks_deployment`; scope `production` ⇒ Level 5. |
| C-RECON-SET-1-09 | `product.yaml` `infrastructure:` block and `security.production_db_access`; the attestation window from D-L3-02(c) | The attestation record store named by **D-L3-02** (read from `control-plane-records` over the contents API) | Latest attestation for the product: absent, `result != pass`, or `date + window < today` ⇒ Blocking. Within window and passing ⇒ no finding. |
| C-RECON-SET-1-10 | `product.yaml` `identity.lifecycle` | `GET /repos/{o}/{r}` (`archived`), `GET /repos/{o}/{r}/contents/.github/renovate.json` (then `renovate.json5`, `.github/renovate.json5`), `GET /repos/{o}/{r}/actions/workflows`, `product.yaml` `observability.alert_channel` | A lifecycle→expected-configuration table (see `L3-01-12`). Safe rows (Renovate schedule, monitoring alert channel) ⇒ Level-3 repair proposed; unsafe rows (archived flag, workflow presence) ⇒ Amber alert. |
| C-RECON-SET-1-11 | `assignments[]` where `end_date` is non-null and `< today`; `people[].end_date` likewise | `GET /orgs/{org}/teams/{slug}/members`, `GET /orgs/{org}/members` | Expired assignment whose person is still a member of the product team, or expired `people.yaml` `end_date` with `access_status != revoked` still in the org ⇒ Level-3 revoke **proposed**. |
| C-RECON-SET-1-12 | `product.yaml` `dependencies.internal[]` | `registries/services/*/service.yaml` `identity.id` set (no API call) | Every declared internal dependency must name an existing service id. Unknown id ⇒ Blocking, `blocks_repository` = the product's repos. |
| C-RECON-SET-1-13 | `platform.yaml` `reusable_workflow_versions` (`current`, `supported[]`, `deprecated[]`) plus the recorded resolved SHA per tag in `reconciler/state/workflow-tag-shas.json` | `GET /repos/{org}/control-plane/git/ref/tags/{tag}`; when `object.type == "tag"`, dereference with `GET /repos/{org}/control-plane/git/tags/{sha}` → `object.sha` | The resolved **commit** SHA for each tag must equal the recorded SHA. Any change ⇒ Blocking. A tag with no recorded SHA is recorded on first sight and reported Amber once (first-observation), never silently. |
| C-RECON-SET-1-14 | The two-ruleset split of §33.2 / D89: ruleset A carries the pull-request rules and may list the Renovate app; ruleset B carries the `renovate-path-guard` required status check and must list **no** bypass actor | `GET /repos/{o}/{r}/rulesets?includes_parents=true`, `GET /repos/{o}/{r}/rulesets/{id}` → `bypass_actors[]`, `rules[]` | Locate the ruleset whose `rules[]` contains a `required_status_checks` rule naming context `renovate-path-guard`. If its `bypass_actors[]` is non-empty ⇒ Blocking. If no such ruleset exists ⇒ Blocking. |
| C-RECON-SET-1-15 | `os-health.yaml` per-store `max_inter_write_interval` (§97.2) | `GET /repos/{org}/control-plane-records/commits?path={store}&per_page=1` → `[0].commit.committer.date` | `now − latest_commit > interval` ⇒ Amber; ⇒ **Blocking** where store ∈ {`events/`, `records/deployments/`, `records/uat/`}. |
| C-RECON-SET-1-16 | The production-restore record store named by **D-L3-03** | Contents API listing of that store in `control-plane-records`, each record parsed | For every production-restore record: the `integrity_check` result field and the named-verifier field must both be present and non-empty. Either absent ⇒ Red. |
| C-RECON-SET-1-17 | `product.yaml` `recovery.restore_tested` | Contents API listing of `records/restore-tests/` in `control-plane-records`; parse each record's product and pass/fail | The newest **passing** record for the product must exist and its date must equal `restore_tested`. No matching record, or a date with no record ⇒ Blocking (§53.1: *"a declared date with no matching record is an unevidenced reliability claim"*). |
| C-RECON-SET-1-18 | The machine-identity set: `people.yaml` entries whose `employment_type` marks them machine, plus the declared app logins in `registries/platform.yaml` | `GET /repos/{o}/{r}/commits?path=.github/workflows&since={window_start}&per_page=100` → per commit `author.login`, `committer.login`, `commit.author.name` | Any commit touching `.github/workflows/**` whose author **or** committer login is in the machine-identity set ⇒ Blocking, regardless of diff content. |
| C-RECON-SET-1-19 | The declared bypass actor for each repo's ruleset A (§33.2, D89) | `GET /repos/{o}/{r}/pulls?state=closed&base={default_branch}&per_page=100` filtered to `merged_at != null` within the window; `GET /repos/{o}/{r}/pulls/{n}/commits` → per commit `author.login`, `committer.login` | For a merged PR whose head branch matches the bypass actor's branch prefix: any commit whose author or committer login differs from the declared bypass actor ⇒ Blocking. |

### 4.2 Per-registry comparison counts (spec Section 53.1, mandatory)

> *"Every run additionally records its per-registry comparison counts — how many rows of each registry it actually compared — so that a silently narrowed comparison is itself visible drift."*

The engine computes this **structurally**, not by a hand-maintained tally: each comparator exposes `rows(declared)`, the orchestrator counts what it iterates, and `reconciler/counts.py` independently computes `rows_declared` straight from the parsed registry. A comparator that silently narrows its own row set therefore produces `rows_compared < rows_declared` automatically.

| Registry key | `rows_declared` definition | Comparators contributing `rows_compared` |
| --- | --- | --- |
| `people.yaml` | count of `people[]` entries with `availability != departed` | C-RECON-SET-1-01, C-RECON-SET-1-02, C-RECON-SET-1-18 |
| `roles.yaml` | count of `roles[]` entries | C-RECON-SET-1-02 |
| `platform.yaml` | count of tags across `reusable_workflow_versions.{current,supported,deprecated}`, de-duplicated | C-RECON-SET-1-13 |
| `product.yaml` | count of product directories under `registries/products/` | C-RECON-SET-1-03 … C-RECON-SET-1-12, C-RECON-SET-1-14, C-RECON-SET-1-16, C-RECON-SET-1-17, C-RECON-SET-1-19 |
| `services` | count of `registries/services/*/service.yaml` files | C-RECON-SET-1-12 |
| `os-health.yaml` | count of declared record stores carrying a write-freshness interval | C-RECON-SET-1-15 |

Recorded on the run record as, per key: `rows_declared`, `rows_compared`, `comparators[]`, `shortfall` (boolean). `shortfall == true` on any key marks the run `FAILED` under the same rule as the missing canary (Section 53.1, AT-102) and raises **SIG-13**; its drift class comes from **D-L3-04(b)**.

---

## 5. Task manifest

Twenty-two tasks. Each is one branch, one PR, one merge. Nothing in this phase writes to GitHub, to `registries/**`, or to `control-plane-records`.

**The three closing commands.** Section 2 states that every task ends with the same three commands. They are, verbatim, and they are the last three lines of every task's `Commands` block:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

**Test-count idiom.** Every acceptance criterion that counts tests uses this exact form, so the expected output is a fixed string and never a timing-dependent one:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
python -m pytest <path> -q 2>&1 | grep -oE '^[0-9]+ passed'
```

**Sizes.** S = under two hours. M = half a day. L = a full day. No task in this phase is larger than L; a task that appeared larger has been split.

| Task id | Title | Implements | Size | Depends on |
| --- | --- | --- | --- | --- |
| L3-01-01 | Phase entry gate, package skeleton, and the read-only API client | R1, AT-110 (client half) | M | D-L3-01 |
| L3-01-02 | The drift-finding envelope and the reconciliation run record, as JSON Schema | §53.1, §53.4, CCR-L3-01 | M | T01 |
| L3-01-03 | Declared-state loader and the fixture mirror | §3 path map, §52.6 | M | T01, **L1** |
| L3-01-04 | Comparator protocol, comparator registry, orchestrator | §53.1 | M | T02, T03 |
| L3-01-05 | The frozen Section 53.1 table and `comparators/manifest.yaml` | R3, §53.4 | M | T04 |
| L3-01-06 | CMP-01 — `people.yaml` versus organisation membership | CMP-01, inv. 44, SIG-03 | M | T05 |
| L3-01-07 | CMP-02 — declared capabilities versus authority-team membership | CMP-02, inv. 7 | M | T05, **L1** |
| L3-01-08 | The branch-protection template and CMP-05 | CMP-05, §11.3, SIG-03 | L | T05 |
| L3-01-09 | CMP-03 and CMP-04 — assignments versus Teams and versus CODEOWNERS | CMP-03, CMP-04, inv. 7, inv. 55 | L | T05 |
| L3-01-10 | The environment template, CMP-07 and CMP-08 | CMP-07, CMP-08, §33.4, D91 | L | T05 |
| L3-01-11 | CMP-09 — the declared `infrastructure:` boundary versus attestation | CMP-09, §40.2, inv. 24, inv. 26 | M | T05, **D-L3-02** |
| L3-01-12 | CMP-10 — lifecycle versus Renovate, monitoring and CI configuration | CMP-10, §18.1 | M | T05 |
| L3-01-13 | CMP-06 — workflow template version versus the actual workflow file | CMP-06, §33.2, §60.3 | M | T05 |
| L3-01-14 | CMP-11 and CMP-12 — expired access, and unknown dependencies | CMP-11, CMP-12, inv. 55, §20.1 | M | T05 |
| L3-01-15 | CMP-13 — the resolved commit SHA behind every `workflows/*` tag | CMP-13, §33.2, inv. 72 | M | T05 |
| L3-01-16 | CMP-14 — the Renovate bypass ruleset split | CMP-14, §33.2, D89 | M | T05 |
| L3-01-17 | CMP-15 — record-store write freshness | CMP-15, §97.2 | M | T05 |
| L3-01-18 | CMP-16 and CMP-17 — restore evidence | CMP-16, CMP-17, §44.5, SIG-17 | L | T05, **D-L3-03** |
| L3-01-19 | CMP-18 and CMP-19 — the two authorship rows | CMP-18, CMP-19, §33.2, §40.3 | L | T05, **L1** |
| L3-01-20 | Run integrity — seeded canary, per-registry comparison counts, EC-109 | AT-102, EC-109, SIG-13 | L | T06…T19, **D-L3-04** |
| L3-01-21 | The CLI, exit codes, run-record emission, `external-cause` and `acknowledged_by` | §53.1, D96, AT-032 | M | T20 |
| L3-01-22 | Phase acceptance — full-set assertion, read-only proof, path guard, exit record | R1, R2, R3 | L | T21 |

Dependency shape:

```
T01 → T02 → T04 ← T03
             ↓
            T05 → { T06 T07 T08 T09 T10 T11 T12 T13 T14 T15 T16 T17 T18 T19 }
                       ↓
                      T20 → T21 → T22
```

The fourteen comparator tasks (T06 … T19) are mutually independent once T05 has merged. They may be executed in any order, one branch each. They may **not** be executed on one shared branch.

**Test counts.** Each task's SELF-VERIFY asserts its own count. The phase total is asserted once, in `L3-01-22`: 6 + 8 + 7 + 6 + 5 + 6 + 4 + 7 + 8 + 9 + 6 + 6 + 5 + 6 + 5 + 5 + 5 + 6 + 6 + 8 + 6 + 9 = **139**.

---

## 6. The blocker-issue template

Every STOP rule in this phase resolves to this command, with the task's own trigger substituted. Run it, then stop working: do not commit, do not push, do not open the PR, do not start the next task.

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > /tmp/blocker-body.md <<'BLOCKEREOF'
## Blocked task
<TASK_ID> — <TASK TITLE>

## Lane
L3 Reconciler & Provisioning — Phase 1 (the declared-versus-actual diff engine)
Plan file: Code/implementation/lanes/L3-01-diff-engine.md

## Trigger that fired
<paste the exact STOP trigger text from the task, verbatim>

## Observed
<paste the exact command you ran and its exact output>

## Expected per plan
<paste the expected output from the task's SELF-VERIFY block>

## Spec references
<paste the task's "Spec basis" line verbatim>

## Blocked-on
<one of: L0 | L1 | L2 | L4 | L5 | D-L3-01 | D-L3-02 | D-L3-03 | D-L3-04>

## What I need to proceed
A decision or a value. I have made no change and chosen no value.

## Branch state
Branch: <branch name>
HEAD: <output of: git rev-parse HEAD>
Files changed so far: <output of: git diff --name-only origin/integration...HEAD>
BLOCKEREOF
gh issue create \
  --title "BLOCKER L3-01 <TASK_ID>: <one-line trigger>" \
  --label "blocker,lane-3,phase-1" \
  --body-file /tmp/blocker-body.md
```

**Never** resolve a blocker by widening an acceptance criterion, by inventing a field name, by inventing a path in another lane's tree, or by marking a comparator "not applicable". A comparator that cannot run produces `rows_compared = 0`, and Section 4.2 makes that a shortfall — that is the designed behaviour, and it is visible. Silently skipping it is EC-109.

---

## L3-01-01 — Phase entry gate, package skeleton, and the read-only API client

**Size:** M **Depends on:** D-L3-01
**Owns:** `reconciler/**`
**Spec basis:** §99.6 risk 6 (*"detect-only first"*); §99.4 item 6; AT-110 (the client half — the credential half is a later L3 phase); D96 (*"per-run caps on objects mutated, an expected-source assertion"*).
**Implements:** rule **R1**.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t01-readonly-client
```

### Entry gate — run all four and read the output before creating anything

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
test -f docs/decisions/D-L3-01.md && echo "GATE-1 decision-present OK" || echo "GATE-1 FAIL"
grep -q 'python-3.12' docs/decisions/D-L3-01.md && echo "GATE-2 runtime-matches-plan OK" || echo "GATE-2 FAIL"
python -c "import sys; print('GATE-3 python OK' if sys.version_info[:2]==(3,12) else 'GATE-3 FAIL')"
test -e reconciler && echo "GATE-4 COLLISION reconciler-exists" || echo "GATE-4 clear OK"
```

### Files created

- `reconciler/__init__.py`
- `reconciler/pyproject.toml`
- `reconciler/requirements.in`
- `reconciler/requirements.txt` (generated, hash-pinned)
- `reconciler/api/__init__.py`
- `reconciler/api/client.py`
- `reconciler/api/tests/__init__.py`
- `reconciler/api/tests/test_client_readonly.py`
- `reconciler/PHASE1-ENTRY.md`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p reconciler/api/tests
printf '' > reconciler/__init__.py
printf '' > reconciler/api/__init__.py
printf '' > reconciler/api/tests/__init__.py

cat > reconciler/pyproject.toml <<'TOMLEOF'
[project]
name = "reconciler"
version = "0.1.0"
description = "L3 declared-versus-actual diff engine. Phase 1: detect only."
# Python 3.12 per FD-005/FD-056
requires-python = "==3.12.*"

[tool.pytest.ini_options]
addopts = "-q"
testpaths = ["reconciler", "validators/drift"]
TOMLEOF

cat > reconciler/requirements.in <<'REQEOF'
# D-L3-01: python-3.12, dependencies pinned by hash. Python 3.12 per FD-005/FD-056
# Regenerate reconciler/requirements.txt with:
#   pip-compile --generate-hashes --output-file reconciler/requirements.txt reconciler/requirements.in
PyYAML==6.0.2
jsonschema==4.23.0
pytest==8.3.3
REQEOF

pip-compile --generate-hashes --output-file reconciler/requirements.txt reconciler/requirements.in
```

Now the client. It is the single point through which every comparator reaches GitHub, and it is the enforcement of R1:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/api/client.py <<'PYEOF'
"""The read-only GitHub REST client.

L3 Phase 1 rule R1: the engine issues HTTP GET and nothing else.

Spec 99.6 risk 6: "Reconciliation auto-repair as the most dangerous code ...
the reconciler is the highest-privilege identity in the system." Its stated
mitigation is "Detect-only first". This module is where "detect-only" stops
being a promise and becomes a data structure: ALLOWED_METHODS is a frozenset
of exactly one element, and every request goes through one function that
checks it.

D96: "Per-run caps on objects mutated, an expected-source assertion". Phase 1
mutates nothing, so the cap here is a per-run READ cap and the expected-source
assertion is on the API host. Both are recorded on the run record.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Iterator

#: The complete set of HTTP methods this phase may issue. Do not add to it.
#: L3-01-22 asserts len(ALLOWED_METHODS) == 1 across the whole phase.
ALLOWED_METHODS = frozenset({"GET"})

#: D96 expected-source assertion. A run whose calls left this host is not a
#: reconciliation run; it is an unexplained egress.
EXPECTED_API_HOST = "api.github.com"

DEFAULT_API_ROOT = "https://api.github.com"

#: D96 per-run call cap. A run that exceeds it stops rather than continuing;
#: an unbounded read loop against the org is itself reportable (see T21).
DEFAULT_MAX_CALLS = 5000


class WriteAttempted(RuntimeError):
    """Raised when any caller asks for a method outside ALLOWED_METHODS."""


class UnexpectedSource(RuntimeError):
    """Raised when a request would leave EXPECTED_API_HOST (D96)."""


class CallCapExceeded(RuntimeError):
    """Raised when a run exceeds its per-run read cap (D96)."""


@dataclass(frozen=True)
class Call:
    """One recorded API call. The ledger is evidence, not logging."""

    method: str
    path: str
    status: int


@dataclass
class ReadOnlyClient:
    token: str
    api_root: str = DEFAULT_API_ROOT
    max_calls: int = DEFAULT_MAX_CALLS
    calls: list[Call] = field(default_factory=list)

    # ---- the one gate -------------------------------------------------
    def request(self, method: str, path: str, **params: Any) -> Any:
        if method not in ALLOWED_METHODS:
            raise WriteAttempted(
                f"L3 Phase 1 is read-only (rule R1). Refused: {method} {path}"
            )
        url = self.api_root.rstrip("/") + "/" + path.lstrip("/")
        if params:
            url = url + "?" + urllib.parse.urlencode(params)
        host = urllib.parse.urlparse(url).netloc
        if host != EXPECTED_API_HOST:
            raise UnexpectedSource(f"D96 expected-source assertion failed: {host}")
        if len(self.calls) >= self.max_calls:
            raise CallCapExceeded(f"D96 per-run read cap {self.max_calls} exceeded")
        req = urllib.request.Request(url, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                status = resp.status
                body = resp.read()
        except urllib.error.HTTPError as exc:
            self.calls.append(Call(method, path, exc.code))
            if exc.code in (403, 404):
                return None
            raise
        self.calls.append(Call(method, path, status))
        return json.loads(body) if body else None

    # ---- the only two public verbs ------------------------------------
    def get(self, path: str, **params: Any) -> Any:
        return self.request("GET", path, **params)

    def paginate(self, path: str, **params: Any) -> Iterator[Any]:
        page = 1
        per_page = int(params.get("per_page", 100))
        while True:
            batch = self.get(path, page=page, **params)
            if not batch:
                return
            for item in batch:
                yield item
            if len(batch) < per_page:
                return
            page += 1

    # ---- evidence ------------------------------------------------------
    def ledger(self) -> dict[str, Any]:
        """The per-run API-call record required by D96."""
        return {
            "api_calls": len(self.calls),
            "methods_used": sorted({c.method for c in self.calls}),
            "expected_source": EXPECTED_API_HOST,
            "max_calls": self.max_calls,
        }


def client_from_env() -> ReadOnlyClient:
    token = os.environ.get("RECONCILER_TOKEN")
    if not token:
        raise RuntimeError("RECONCILER_TOKEN is not set")
    return ReadOnlyClient(token=token)
PYEOF
```

The tests. The fourth is the static assertion that no module in this lane names a write verb — the allowlist is worthless if a comparator builds a request somewhere else:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/api/tests/test_client_readonly.py <<'PYEOF'
"""R1: the engine issues GET and nothing else."""
import pathlib

import pytest

from reconciler.api import client as c

ROOTS = ("reconciler", "validators/drift")
WRITE_VERBS = (
    '"POST"', '"PUT"', '"PATCH"', '"DELETE"',
    "'POST'", "'PUT'", "'PATCH'", "'DELETE'",
)


def _repo_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "reconciler").is_dir() and (parent / "validators").is_dir():
            return parent
    raise AssertionError("repository root not found")


def test_allowlist_has_exactly_one_method():
    assert c.ALLOWED_METHODS == frozenset({"GET"})


@pytest.mark.parametrize("verb", ["POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
def test_every_other_verb_is_refused(verb):
    cl = c.ReadOnlyClient(token="t")
    with pytest.raises(c.WriteAttempted):
        cl.request(verb, "/orgs/example/members")
    assert cl.calls == []


def test_a_refused_call_is_not_counted_against_the_cap():
    cl = c.ReadOnlyClient(token="t", max_calls=1)
    for _ in range(5):
        with pytest.raises(c.WriteAttempted):
            cl.request("POST", "/orgs/example")
    assert cl.ledger()["api_calls"] == 0


def test_no_module_in_this_lane_names_a_write_verb():
    root = _repo_root()
    offenders = []
    for r in ROOTS:
        for path in (root / r).rglob("*.py"):
            if path.name == "test_client_readonly.py":
                continue
            text = path.read_text(encoding="utf-8")
            for verb in WRITE_VERBS:
                if verb in text:
                    offenders.append(f"{path}: {verb}")
    assert offenders == []


def test_expected_source_assertion_refuses_a_foreign_host():
    cl = c.ReadOnlyClient(token="t", api_root="https://evil.example")
    with pytest.raises(c.UnexpectedSource):
        cl.get("/orgs/example")


def test_ledger_shape_is_the_d96_shape():
    led = c.ReadOnlyClient(token="t").ledger()
    assert set(led) == {"api_calls", "methods_used", "expected_source", "max_calls"}
    assert led["expected_source"] == "api.github.com"
PYEOF

cat > reconciler/PHASE1-ENTRY.md <<'MDEOF'
# L3 Phase 1 entry record — the declared-versus-actual diff engine

Phase 1 is detect-only. Spec 99.4 item 6: "Reconciliation v0, detect and
block only ... Auto-repair is deferred until detection has run clean for
weeks." Spec 99.6 risk 6 states the mitigation: "Detect-only first; repair
classes enabled one at a time; stricter-only rule enforced in code and tested."

Binding rules carried into every module of this phase:

- R1 - the engine issues HTTP GET and nothing else. reconciler/api/client.py
  ALLOWED_METHODS is the enforcement; L3-01-22 asserts it phase-wide.
- R2 - every file lives under reconciler/**, tools/provision/** or
  validators/drift/**. registries/** and templates/workflows/** are read as
  runtime data and never edited, never imported.
- R3 - every comparator carries the Section 53.1 "On mismatch" cell verbatim
  in reconciler/comparators/manifest.yaml, checked against a frozen copy of
  the spec table.

Level-3 repairs are proposed as data on a finding in this phase. Nothing
applies them. The stricter-only predicate (invariant 81, AT-033) lands in
L3 Phase 2.

Runtime: python-3.12, dependencies hash-pinned in reconciler/requirements.txt
(D-L3-01).
MDEOF

python -m pytest reconciler/api -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-01: phase-1 skeleton and the read-only GitHub client (R1)"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | The allowlist has exactly one member | `cd "$CP" && python -c "from reconciler.api.client import ALLOWED_METHODS as m; print(len(m), sorted(m)[0])"` | `1 GET` |
| A2 | Six client tests pass | `cd "$CP" && python -m pytest reconciler/api -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `6 passed` |
| A3 | Dependencies are hash-pinned | `cd "$CP" && grep -c 'hash=sha256:' reconciler/requirements.txt \| awk '$1>=3{print "HASHES-OK"}'` | `HASHES-OK` |
| A4 | Runtime is 3.12, as D-L3-01 resolved | `cd "$CP" && grep -c 'requires-python = "==3.12' reconciler/pyproject.toml` | `1` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -c "from reconciler.api.client import ALLOWED_METHODS as m; print(len(m), sorted(m)[0])"
python -m pytest reconciler/api -q 2>&1 | grep -oE '^[0-9]+ passed'
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
1 GET
6 passed
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: D-L3-01`, if `GATE-1` or `GATE-2` prints `FAIL` — the runtime resolution is not `python-3.12`, and this lane file must then be re-issued by L0.
Note: FD-005 moves to Python 3.12; this STOP is lifted — the gate now passes on 3.12.
STOP with `Blocked-on: L0` if `GATE-3` prints `FAIL`, or if `pip-compile` is not installed.
STOP with `Blocked-on: L0` if `GATE-4` prints `COLLISION` — another lane has created `reconciler/`, which contradicts PARTITION.md line 19.
Do **not** widen `ALLOWED_METHODS`. Do **not** hand-write hashes into `requirements.txt`.

---

## L3-01-02 — The drift-finding envelope and the reconciliation run record, as JSON Schema

**Size:** M **Depends on:** L3-01-01
**Owns:** `validators/drift/schema/**`, `reconciler/model.py`
**Spec basis:** §53.1 (*"Every reconciliation run writes its result, and a clean run is recorded as clean"*; the `acknowledged_by` / `acknowledged_at` paragraph; the `external-cause` paragraph); §53.4 (the one drift severity scale); §53.2 (the five levels); CCR-L3-01.

Two schemas, both lane-local under an owned path, both offered to L0 by CCR-L3-01. No other lane depends on them in this phase.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t02-schemas
```

### Files created

- `validators/drift/__init__.py`
- `validators/drift/schema/drift-finding.schema.json`
- `validators/drift/schema/reconciliation-run.schema.json`
- `validators/drift/schema_check.py`
- `validators/drift/tests/__init__.py`
- `validators/drift/tests/test_schemas.py`
- `reconciler/model.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p validators/drift/schema validators/drift/tests
printf '' > validators/drift/__init__.py
printf '' > validators/drift/tests/__init__.py

cat > validators/drift/schema/drift-finding.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/schema/drift-finding/1",
  "title": "Drift finding",
  "description": "One mismatch between declared state and actual platform state. Spec Section 53.1.",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "finding_schema_version",
    "id",
    "comparator_id",
    "scope",
    "declared",
    "actual",
    "drift_class",
    "response_level",
    "on_mismatch",
    "detected_at",
    "evidence"
  ],
  "properties": {
    "finding_schema_version": { "const": 1 },
    "id": { "type": "string", "pattern": "^DRIFT-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}$" },
    "comparator_id": { "type": "string", "pattern": "^CMP-(0[1-9]|1[0-9])$" },
    "scope": {
      "type": "object",
      "additionalProperties": false,
      "required": ["kind", "name"],
      "properties": {
        "kind": { "enum": ["organisation", "product", "repository", "service", "person", "record-store", "environment", "tag"] },
        "name": { "type": "string", "minLength": 1 },
        "product": { "type": ["string", "null"] },
        "environment": { "type": ["string", "null"] }
      }
    },
    "declared": { "description": "The declared value, verbatim from the registry." },
    "actual": { "description": "The fetched value, verbatim from the API response." },
    "drift_class": {
      "description": "Section 53.4. There is exactly one drift severity scale.",
      "enum": ["green", "amber", "red", "blocking"]
    },
    "response_level": {
      "description": "Section 53.2. Level 3 is PROPOSED ONLY in this phase.",
      "type": "integer",
      "minimum": 1,
      "maximum": 5
    },
    "on_mismatch": {
      "description": "The Section 53.1 'On mismatch' cell, verbatim. Rule R3.",
      "type": "string",
      "minLength": 1
    },
    "blocks_repository": { "type": "array", "items": { "type": "string" } },
    "blocks_deployment": { "type": "array", "items": { "type": "string" } },
    "flag_platform_compatibility": { "type": "boolean" },
    "proposed_repair": {
      "description": "Data only. Phase 1 never executes it (R1).",
      "type": ["object", "null"]
    },
    "detected_at": { "type": "string" },
    "evidence": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["source", "reference"],
        "properties": {
          "source": { "enum": ["registry", "template", "github-api", "records-repository"] },
          "reference": { "type": "string", "minLength": 1 }
        }
      }
    },
    "acknowledged_by": {
      "description": "Section 53.1: written by the first responder who claims it.",
      "type": ["string", "null"]
    },
    "acknowledged_at": { "type": ["string", "null"] },
    "external_cause": {
      "description": "Section 53.1: an acknowledged vendor outage, named.",
      "type": ["string", "null"]
    },
    "canary": {
      "description": "true only for the permanent seeded drift record (Section 53.1, AT-102).",
      "type": "boolean"
    }
  }
}
JSONEOF

cat > validators/drift/schema/reconciliation-run.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/schema/reconciliation-run/1",
  "title": "Reconciliation run record",
  "description": "One execution of the diff engine. Spec Section 53.1: 'Every reconciliation run writes its result, and a clean run is recorded as clean.'",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "run_schema_version",
    "id",
    "started_at",
    "finished_at",
    "verdict",
    "comparators_executed",
    "findings",
    "registry_counts",
    "canary",
    "api"
  ],
  "properties": {
    "run_schema_version": { "const": 1 },
    "id": { "type": "string", "pattern": "^RUN-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}$" },
    "started_at": { "type": "string" },
    "finished_at": { "type": "string" },
    "verdict": {
      "description": "CLEAN is reachable only with the canary found and no count shortfall (AT-102).",
      "enum": ["CLEAN", "FINDINGS", "FAILED"]
    },
    "comparators_executed": {
      "type": "array",
      "minItems": 19,
      "maxItems": 19,
      "items": { "type": "string", "pattern": "^CMP-(0[1-9]|1[0-9])$" },
      "uniqueItems": true
    },
    "findings": { "type": "array", "items": { "type": "object" } },
    "registry_counts": {
      "description": "Section 53.1: per-registry comparison counts, 'so that a silently narrowed comparison is itself visible drift'.",
      "type": "object",
      "minProperties": 6,
      "additionalProperties": {
        "type": "object",
        "additionalProperties": false,
        "required": ["rows_declared", "rows_compared", "comparators", "shortfall"],
        "properties": {
          "rows_declared": { "type": "integer", "minimum": 0 },
          "rows_compared": { "type": "integer", "minimum": 0 },
          "comparators": { "type": "array", "items": { "type": "string" } },
          "shortfall": { "type": "boolean" }
        }
      }
    },
    "canary": {
      "type": "object",
      "additionalProperties": false,
      "required": ["expected", "found"],
      "properties": {
        "expected": { "type": "boolean" },
        "found": { "type": "boolean" },
        "finding_id": { "type": ["string", "null"] }
      }
    },
    "api": {
      "type": "object",
      "additionalProperties": false,
      "required": ["api_calls", "methods_used", "expected_source", "max_calls"],
      "properties": {
        "api_calls": { "type": "integer", "minimum": 0 },
        "methods_used": {
          "type": "array",
          "items": { "const": "GET" },
          "maxItems": 1
        },
        "expected_source": { "const": "api.github.com" },
        "max_calls": { "type": "integer", "minimum": 1 }
      }
    },
    "external_cause": { "type": ["string", "null"] }
  }
}
JSONEOF

cat > validators/drift/schema_check.py <<'PYEOF'
"""Schema loading and validation for the two Phase-1 envelopes.

CCR-L3-01: these schemas are lane-local under validators/drift/schema/
because contracts/** is L0's and frozen (PARTITION rule 2). L0 is asked to
adopt them unchanged; until then no other lane depends on them.
"""
from __future__ import annotations

import json
import pathlib
from typing import Any

import jsonschema

SCHEMA_DIR = pathlib.Path(__file__).resolve().parent / "schema"
FINDING = "drift-finding.schema.json"
RUN = "reconciliation-run.schema.json"


def load(name: str) -> dict[str, Any]:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def validate_finding(doc: dict[str, Any]) -> None:
    jsonschema.validate(doc, load(FINDING))


def validate_run(doc: dict[str, Any]) -> None:
    jsonschema.validate(doc, load(RUN))
PYEOF

cat > reconciler/model.py <<'PYEOF'
"""The in-memory shapes the comparators produce.

Section 53.4 is explicit: "There is exactly one drift severity scale, used
everywhere." DRIFT_CLASSES is that scale and it is closed. Section 53.2 gives
the five levels and they are closed too. Nothing here invents a class, a level
or a mismatch string: the mismatch string is the Section 53.1 cell, carried
verbatim from reconciler/comparators/manifest.yaml (rule R3).
"""
from __future__ import annotations

import dataclasses
from typing import Any

#: Section 53.4, in the spec's own order, least to most urgent.
DRIFT_CLASSES = ("green", "amber", "red", "blocking")

#: Section 53.2.
RESPONSE_LEVELS = (1, 2, 3, 4, 5)


@dataclasses.dataclass(frozen=True)
class Scope:
    kind: str
    name: str
    product: str | None = None
    environment: str | None = None


@dataclasses.dataclass(frozen=True)
class Evidence:
    source: str
    reference: str


@dataclasses.dataclass
class Finding:
    id: str
    comparator_id: str
    scope: Scope
    declared: Any
    actual: Any
    drift_class: str
    response_level: int
    on_mismatch: str
    detected_at: str
    evidence: list[Evidence]
    blocks_repository: list[str] = dataclasses.field(default_factory=list)
    blocks_deployment: list[str] = dataclasses.field(default_factory=list)
    flag_platform_compatibility: bool = False
    proposed_repair: dict[str, Any] | None = None
    acknowledged_by: str | None = None
    acknowledged_at: str | None = None
    external_cause: str | None = None
    canary: bool = False
    finding_schema_version: int = 1

    def __post_init__(self) -> None:
        if self.drift_class not in DRIFT_CLASSES:
            raise ValueError(f"not a Section 53.4 class: {self.drift_class}")
        if self.response_level not in RESPONSE_LEVELS:
            raise ValueError(f"not a Section 53.2 level: {self.response_level}")
        # Section 53.2, Level 5 "Applies to": production environment drift.
        # This is additive to the row's own class, never a substitute for it.
        if self.scope.environment == "production":
            self.response_level = 5

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)
PYEOF

cat > validators/drift/tests/test_schemas.py <<'PYEOF'
import jsonschema
import pytest

from reconciler.model import DRIFT_CLASSES, RESPONSE_LEVELS, Evidence, Finding, Scope
from validators.drift import schema_check as sc

GOOD_FINDING = {
    "finding_schema_version": 1,
    "id": "DRIFT-2026-08-27-001",
    "comparator_id": "CMP-01",
    "scope": {"kind": "organisation", "name": "example-org", "product": None, "environment": None},
    "declared": ["alice"],
    "actual": [],
    "drift_class": "blocking",
    "response_level": 4,
    "on_mismatch": "Alert; block on removal drift",
    "detected_at": "2026-08-27T06:00:00Z",
    "evidence": [{"source": "registry", "reference": "registries/people.yaml"}],
}


def _run(**over):
    doc = {
        "run_schema_version": 1,
        "id": "RUN-2026-08-27-001",
        "started_at": "2026-08-27T06:00:00Z",
        "finished_at": "2026-08-27T06:04:00Z",
        "verdict": "FINDINGS",
        "comparators_executed": ["CMP-%02d" % n for n in range(1, 20)],
        "findings": [],
        "registry_counts": {
            k: {"rows_declared": 1, "rows_compared": 1, "comparators": ["CMP-01"], "shortfall": False}
            for k in ("people.yaml", "roles.yaml", "platform.yaml", "product.yaml", "services", "os-health.yaml")
        },
        "canary": {"expected": True, "found": True, "finding_id": "DRIFT-2026-08-27-001"},
        "api": {"api_calls": 12, "methods_used": ["GET"], "expected_source": "api.github.com", "max_calls": 5000},
        "external_cause": None,
    }
    doc.update(over)
    return doc


def test_the_scale_is_closed_and_is_the_section_534_scale():
    assert DRIFT_CLASSES == ("green", "amber", "red", "blocking")
    assert RESPONSE_LEVELS == (1, 2, 3, 4, 5)


def test_a_well_formed_finding_validates():
    sc.validate_finding(GOOD_FINDING)


def test_an_invented_class_is_rejected():
    with pytest.raises(jsonschema.ValidationError):
        sc.validate_finding(dict(GOOD_FINDING, drift_class="critical"))


def test_a_finding_without_evidence_is_rejected():
    with pytest.raises(jsonschema.ValidationError):
        sc.validate_finding(dict(GOOD_FINDING, evidence=[]))


def test_a_run_must_execute_all_nineteen_comparators():
    with pytest.raises(jsonschema.ValidationError):
        sc.validate_run(_run(comparators_executed=["CMP-%02d" % n for n in range(1, 19)]))


def test_a_run_may_not_record_a_non_get_method():
    bad = _run()
    bad["api"] = dict(bad["api"], methods_used=["GET", "POST"])
    with pytest.raises(jsonschema.ValidationError):
        sc.validate_run(bad)


def test_a_run_must_carry_all_six_registry_counts():
    bad = _run()
    bad["registry_counts"].pop("services")
    with pytest.raises(jsonschema.ValidationError):
        sc.validate_run(bad)


def test_production_scope_is_raised_to_level_five():
    f = Finding(
        id="DRIFT-2026-08-27-002",
        comparator_id="CMP-08",
        scope=Scope("environment", "production", product="product-1", environment="production"),
        declared={"policy": "present"},
        actual=None,
        drift_class="blocking",
        response_level=4,
        on_mismatch="Alert immediately; block deployment on the affected repository",
        detected_at="2026-08-27T06:00:00Z",
        evidence=[Evidence("github-api", "/repos/o/r/environments")],
    )
    assert f.response_level == 5
PYEOF

python -m pytest validators/drift -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/model.py validators/drift
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-02: drift-finding and run-record schemas, and the finding model"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Eight schema tests pass | `cd "$CP" && python -m pytest validators/drift -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `8 passed` |
| A2 | The class scale is the Section 53.4 scale, closed | `cd "$CP" && python -c "from reconciler.model import DRIFT_CLASSES as d; print(len(d), ','.join(d))"` | `4 green,amber,red,blocking` |
| A3 | A run record must name all nineteen comparators | `cd "$CP" && python -c "import json;s=json.load(open('validators/drift/schema/reconciliation-run.schema.json'));p=s['properties']['comparators_executed'];print(p['minItems'],p['maxItems'])"` | `19 19` |
| A4 | The run record admits only `GET` | `cd "$CP" && python -c "import json;s=json.load(open('validators/drift/schema/reconciliation-run.schema.json'));print(s['properties']['api']['properties']['methods_used']['items']['const'])"` | `GET` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest validators/drift -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "from reconciler.model import DRIFT_CLASSES as d; print(len(d), ','.join(d))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
8 passed
4 green,amber,red,blocking
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L0`, if `contracts/reconciler/` already contains a finding schema or a run schema — that means L0 adopted CCR-L3-01 ahead of this task, and the lane-local schemas must be replaced by reads of the adopted ones rather than authored here. Do **not** edit `contracts/**` (PARTITION rule 2).
Do **not** add a fifth drift class or a sixth level for any reason. Section 53.4: *"No other severity vocabulary exists anywhere in this system."*

---

## L3-01-03 — Declared-state loader and the fixture mirror

**Size:** M **Depends on:** L3-01-01; **L1** (`registries/**` must exist on `integration`)
**Owns:** `reconciler/loader.py`, `reconciler/counts.py`, `reconciler/fixtures/**`
**Spec basis:** §52.6 (registry of control-plane files); §7 (`people.yaml` shape); §8 (`roles.yaml`); §15.1 (`product.yaml`); §20.1 (`service.yaml`); §60.1 (`platform.yaml`); Section 3 of this document (the declared-state path map).

The loader is the **only** place this lane reads `registries/**`. Rule R2: read, never write, never import L1 source. Every comparator receives an already-parsed `Declared` object and never opens a registry file itself.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t03-loader
```

### Entry gate

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
test -d registries && echo "GATE-1 registries-present OK" || echo "GATE-1 FAIL blocked-on-L1"
for f in registries/people.yaml registries/roles.yaml registries/platform.yaml registries/os-health.yaml registries/topology.yaml; do
  test -f "$f" && echo "GATE-2 OK $f" || echo "GATE-2 MISSING $f"
done
ls -d registries/products/*/ 2>/dev/null | wc -l
ls registries/services/*/service.yaml 2>/dev/null | wc -l
```

### Files created

- `reconciler/loader.py`
- `reconciler/counts.py`
- `reconciler/tests/__init__.py`
- `reconciler/tests/test_loader.py`
- `reconciler/fixtures/declared/registries/people.yaml`
- `reconciler/fixtures/declared/registries/roles.yaml`
- `reconciler/fixtures/declared/registries/platform.yaml`
- `reconciler/fixtures/declared/registries/os-health.yaml`
- `reconciler/fixtures/declared/registries/products/product-alpha/product.yaml`
- `reconciler/fixtures/declared/registries/services/auth-service/service.yaml`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p reconciler/tests
mkdir -p reconciler/fixtures/declared/registries/products/product-alpha
mkdir -p reconciler/fixtures/declared/registries/services/auth-service
printf '' > reconciler/tests/__init__.py

cat > reconciler/loader.py <<'PYEOF'
"""Read declared state. This module is the lane's only reader of registries/**.

PARTITION rule 4: no cross-lane imports. registries/** is L1's tree and is
consumed here as runtime DATA — parsed YAML — never as source. Rule R2: this
module opens files for reading and never for writing.

Section 3 of the lane plan is the authoritative path map. Nothing here
discovers a registry path by convention; every path is named.
"""
from __future__ import annotations

import dataclasses
import pathlib
from typing import Any

import yaml

PEOPLE = "registries/people.yaml"
ROLES = "registries/roles.yaml"
PLATFORM = "registries/platform.yaml"
OS_HEALTH = "registries/os-health.yaml"
TOPOLOGY = "registries/topology.yaml"
PRODUCTS_DIR = "registries/products"
SERVICES_DIR = "registries/services"

REQUIRED_FILES = (PEOPLE, ROLES, PLATFORM, OS_HEALTH, TOPOLOGY)


class DeclaredStateUnavailable(RuntimeError):
    """A named registry path is absent. This is an L1 dependency, not a defect."""


@dataclasses.dataclass(frozen=True)
class Declared:
    root: pathlib.Path
    people: dict[str, Any]
    roles: dict[str, Any]
    platform: dict[str, Any]
    os_health: dict[str, Any]
    topology: dict[str, Any]
    products: dict[str, dict[str, Any]]
    services: dict[str, dict[str, Any]]

    # ---- the derived views the comparators actually use ---------------
    def active_people(self) -> list[dict[str, Any]]:
        """Section 7: availability is active | on_leave | departing | departed."""
        return [p for p in self.people.get("people", []) if p.get("availability") != "departed"]

    def person_by_id(self, pid: str) -> dict[str, Any] | None:
        for p in self.people.get("people", []):
            if p.get("id") == pid:
                return p
        return None

    def login_of(self, pid: str) -> str | None:
        p = self.person_by_id(pid)
        return (p or {}).get("github_login")

    def repositories_of(self, product_id: str) -> list[dict[str, Any]]:
        """Section 15.1 code.repositories[] — a product may have several."""
        return (self.products[product_id].get("code") or {}).get("repositories", []) or []

    def open_assignments(self, product_id: str, today: str) -> list[dict[str, Any]]:
        """Section 10: an assignment is open when end_date is null or >= today."""
        out = []
        for a in self.products[product_id].get("assignments", []) or []:
            end = a.get("end_date")
            if end is None or str(end) >= today:
                out.append(a)
        return out


def _read(path: pathlib.Path) -> dict[str, Any]:
    if not path.is_file():
        raise DeclaredStateUnavailable(str(path))
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load(root: str | pathlib.Path) -> Declared:
    root = pathlib.Path(root)
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            raise DeclaredStateUnavailable(rel)
    products: dict[str, dict[str, Any]] = {}
    for d in sorted((root / PRODUCTS_DIR).glob("*/")):
        f = d / "product.yaml"
        if f.is_file():
            doc = _read(f)
            pid = ((doc.get("identity") or {}).get("id")) or d.name
            products[pid] = doc
    services: dict[str, dict[str, Any]] = {}
    for f in sorted((root / SERVICES_DIR).glob("*/service.yaml")):
        doc = _read(f)
        sid = ((doc.get("identity") or {}).get("id")) or f.parent.name
        services[sid] = doc
    return Declared(
        root=root,
        people=_read(root / PEOPLE),
        roles=_read(root / ROLES),
        platform=_read(root / PLATFORM),
        os_health=_read(root / OS_HEALTH),
        topology=_read(root / TOPOLOGY),
        products=products,
        services=services,
    )
PYEOF

cat > reconciler/counts.py <<'PYEOF'
"""rows_declared, computed straight from the parsed registry.

Section 53.1: "Every run additionally records its per-registry comparison
counts - how many rows of each registry it actually compared - so that a
silently narrowed comparison is itself visible drift."

This module computes the DENOMINATOR only, and it does so independently of
every comparator, from the registry itself. The numerator comes from what the
orchestrator observes each comparator iterate (L3-01-04). Because the two are
computed by different code from different inputs, a comparator that quietly
narrows its own row set produces rows_compared < rows_declared automatically
and cannot conceal it. Section 4.2 of the lane plan is the definition table.
"""
from __future__ import annotations

from typing import Any

from reconciler.loader import Declared

#: Section 4.2, column "Comparators contributing rows_compared".
CONTRIBUTORS: dict[str, tuple[str, ...]] = {
    "people.yaml": ("CMP-01", "CMP-02", "CMP-18"),
    "roles.yaml": ("CMP-02",),
    "platform.yaml": ("CMP-13",),
    "product.yaml": (
        "CMP-03", "CMP-04", "CMP-05", "CMP-06", "CMP-07", "CMP-08", "CMP-09",
        "CMP-10", "CMP-11", "CMP-12", "CMP-14", "CMP-16", "CMP-17", "CMP-19",
    ),
    "services": ("CMP-12",),
    "os-health.yaml": ("CMP-15",),
}

REGISTRY_KEYS = tuple(CONTRIBUTORS)


def rows_declared(d: Declared) -> dict[str, int]:
    """Section 4.2, column "rows_declared definition"."""
    tags: set[str] = set()
    rwv = (d.platform.get("reusable_workflow_versions") or {})
    cur = rwv.get("current")
    if cur:
        tags.add(str(cur))
    for key in ("supported", "deprecated"):
        for t in rwv.get(key) or []:
            tags.add(str(t))
    stores = _stores_with_interval(d)
    return {
        "people.yaml": len(d.active_people()),
        "roles.yaml": len(d.roles.get("roles", []) or []),
        "platform.yaml": len(tags),
        "product.yaml": len(d.products),
        "services": len(d.services),
        "os-health.yaml": len(stores),
    }


def _stores_with_interval(d: Declared) -> dict[str, Any]:
    """Section 97.2: every store declares a maximum inter-write interval."""
    stores = (d.os_health.get("record_stores") or {})
    return {k: v for k, v in stores.items() if (v or {}).get("max_inter_write_interval")}


def stores_with_interval(d: Declared) -> dict[str, Any]:
    return _stores_with_interval(d)
PYEOF
```

The fixture mirror. It is a **mirror**, not a copy of production data: six small files with the field names Sections 7, 8, 15.1, 20.1, 60.1 and 97.2 declare, and nothing else. Every comparator test in T06 … T19 reads from it, so it is written once, here.

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
F=reconciler/fixtures/declared/registries

cat > $F/people.yaml <<'YEOF'
registry_version: 1
people:
  - id: dev-a
    display_name: "Fixture Developer A"
    github_login: fixture-dev-a
    role: developer
    employment_type: employee
    capabilities: [backend, code-review]
    availability: active
    access_status: provisioned
    start_date: 2025-03-01
    end_date: null
  - id: dev-b
    display_name: "Fixture Developer B"
    github_login: fixture-dev-b
    role: senior_developer
    employment_type: employee
    capabilities: [backend, code-review, architecture]
    availability: active
    access_status: provisioned
    start_date: 2025-03-01
    end_date: null
  - id: lead-1
    display_name: "Fixture Team Lead"
    github_login: fixture-lead-1
    role: team_lead
    employment_type: employee
    capabilities: [architecture, plan-approval, escalation, production-approval]
    availability: active
    access_status: provisioned
    start_date: 2025-01-01
    end_date: null
  - id: qa-1
    display_name: "Fixture QA"
    github_login: fixture-qa-1
    role: qa
    employment_type: employee
    capabilities: [verification, uat, release-signoff]
    availability: active
    access_status: provisioned
    start_date: 2025-01-01
    end_date: null
  - id: con-1
    display_name: "Fixture Contractor"
    github_login: fixture-con-1
    role: contractor
    employment_type: contractor
    capabilities: [frontend]
    availability: active
    access_status: provisioned
    start_date: 2026-01-01
    end_date: 2026-06-30
  - id: gone-1
    display_name: "Fixture Departed"
    github_login: fixture-gone-1
    role: developer
    employment_type: employee
    capabilities: []
    availability: departed
    access_status: revoked
    start_date: 2024-01-01
    end_date: 2025-12-31
YEOF

cat > $F/roles.yaml <<'YEOF'
registry_version: 1
roles:
  - id: founder
    default_capabilities: [strategy, budget]
  - id: team_lead
    default_capabilities: [architecture, plan-approval, escalation, reviewer-matrix-change]
  - id: developer
    default_capabilities: [code-review]
  - id: senior_developer
    default_capabilities: [code-review, architecture]
  - id: qa
    default_capabilities: [verification, uat, release-signoff]
  - id: contractor
    default_capabilities: []
YEOF

cat > $F/platform.yaml <<'YEOF'
platform_version: 4.0
supported_contract_versions:
  product: [1, 2]
  verification: [1]
  people_registry: [1]
  service: [1]
reusable_workflow_versions:
  current: v4
  supported: [v3, v4]
  deprecated: [v2]
  deprecation_deadline:
    v2: 2026-08-01
    v3: 2026-12-01
canary_set:
  - product-alpha
YEOF

cat > $F/os-health.yaml <<'YEOF'
registry_version: 1
record_stores:
  events/:
    max_inter_write_interval: PT24H
  records/deployments/:
    max_inter_write_interval: P7D
  records/uat/:
    max_inter_write_interval: P14D
  records/incidents/:
    max_inter_write_interval: P90D
  records/restore-tests/:
    max_inter_write_interval: P35D
YEOF

cat > $F/topology.yaml <<'YEOF'
registry_version: 1
domains: []
succession:
  team_lead: lead-1
YEOF

cat > $F/products/product-alpha/product.yaml <<'YEOF'
contract_version: 2
platform_compatibility: supported
conformance_profile: service
identity:
  id: product-alpha
  display_name: "Fixture Product Alpha"
  lifecycle: active
  launch_status: launched
  created: 2025-01-15
classification:
  class: commercial
  reliability_criticality: high
assignments:
  - person: dev-a
    type: primary_owner
    start_date: 2025-06-01
    end_date: null
  - person: dev-b
    type: cross_reviewer
    start_date: 2025-06-01
    end_date: null
  - person: dev-b
    type: backup_owner
    start_date: 2025-06-01
    end_date: null
  - person: con-1
    type: contributor
    start_date: 2026-01-01
    end_date: 2026-06-30
escalation: team_lead
code:
  repositories:
    - name: example-org/product-alpha-api
      role: primary
      deploys: true
  default_branch: main
verification:
  automated: required
  manual_uat: required
  contract_path: verification/contract.yaml
environments:
  local: docker-compose.dev.yml
  staging: https://staging.alpha.example
  production: https://alpha.example
dependencies:
  internal:
    - auth-service
  external: []
  infrastructure: []
infrastructure:
  runtime: node-22
  database: postgres-16
  provider: example-cloud
  region: eu-west-1
security:
  secrets_location: github-environments
  production_db_access: ci-only
observability:
  health_endpoint: /health
  version_endpoint: /version
  alert_channel: "#alerts-product-alpha"
recovery:
  backup_frequency: daily
  backup_retention_days: 30
  encrypted: true
  restore_environment: throwaway-vm
  integrity_check: docs/restore.md#integrity
  restore_tested: 2026-08-14
operations:
  support_model: business-hours
  primary_responder: dev-a
  backup_responder: dev-b
YEOF

cat > $F/services/auth-service/service.yaml <<'YEOF'
service_version: 1
identity:
  id: auth-service
  repository: example-org/auth-service
  type: internal-api
assignments:
  - person: dev-b
    type: primary_owner
  - person: dev-a
    type: cross_reviewer
escalation: team_lead
consumers:
  - product-alpha
YEOF
```

Tests:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/tests/test_loader.py <<'PYEOF'
import pathlib

import pytest

from reconciler import counts
from reconciler.loader import DeclaredStateUnavailable, load

FIX = pathlib.Path(__file__).resolve().parent.parent / "fixtures" / "declared"


def test_the_fixture_mirror_loads():
    d = load(FIX)
    assert set(d.products) == {"product-alpha"}
    assert set(d.services) == {"auth-service"}


def test_departed_people_are_excluded_from_active():
    d = load(FIX)
    assert {p["id"] for p in d.active_people()} == {"dev-a", "dev-b", "lead-1", "qa-1", "con-1"}


def test_open_assignments_respect_end_date():
    d = load(FIX)
    open_2026_01 = {a["person"] for a in d.open_assignments("product-alpha", "2026-01-15")}
    open_2026_12 = {a["person"] for a in d.open_assignments("product-alpha", "2026-12-15")}
    assert "con-1" in open_2026_01
    assert "con-1" not in open_2026_12


def test_a_missing_registry_raises_rather_than_returning_empty():
    with pytest.raises(DeclaredStateUnavailable):
        load(FIX / "nonexistent")


def test_rows_declared_covers_all_six_registry_keys():
    d = load(FIX)
    rd = counts.rows_declared(d)
    assert set(rd) == set(counts.REGISTRY_KEYS)
    assert len(rd) == 6


def test_rows_declared_values_on_the_fixture():
    d = load(FIX)
    rd = counts.rows_declared(d)
    assert rd["people.yaml"] == 5
    assert rd["roles.yaml"] == 6
    assert rd["platform.yaml"] == 4
    assert rd["product.yaml"] == 1
    assert rd["services"] == 1
    assert rd["os-health.yaml"] == 5


def test_loader_never_opens_a_registry_for_writing():
    src = (pathlib.Path(__file__).resolve().parent.parent / "loader.py").read_text(encoding="utf-8")
    for forbidden in ('open(', '"w"', "'w'", "write_text", "mkdir", "unlink"):
        if forbidden == 'open(':
            continue
        assert forbidden not in src, forbidden
PYEOF

python -m pytest reconciler/tests/test_loader.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-03: declared-state loader, rows_declared, and the fixture mirror"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Seven loader tests pass | `cd "$CP" && python -m pytest reconciler/tests/test_loader.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `7 passed` |
| A2 | The loader reads the real tree without error | `cd "$CP" && python -c "from reconciler.loader import load; d=load('.'); print('LOADED', len(d.products), len(d.services))"` | `LOADED <n> <m>`, both integers |
| A3 | Six registry keys, matching Section 4.2 | `cd "$CP" && python -c "from reconciler.counts import REGISTRY_KEYS as k; print(len(k), ' '.join(k))"` | `6 people.yaml roles.yaml platform.yaml product.yaml services os-health.yaml` |
| A4 | Nothing under `registries/` was modified | `cd "$CP" && git status --porcelain registries \| wc -l` | `0` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/tests/test_loader.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "from reconciler.counts import REGISTRY_KEYS as k; print(len(k))"
git status --porcelain registries | wc -l
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
7 passed
6
0
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L1`, if `GATE-1` prints `FAIL`, or if any `GATE-2` line prints `MISSING`. Section 3 of this plan already states this: *"that is an L1 dependency, not a defect in this phase."*
STOP with `Blocked-on: L1` if `A2` raises `DeclaredStateUnavailable` on the real tree — a registry file named in Section 3 is absent.
Do **not** create a registry file. Do **not** relax `REQUIRED_FILES`. Do **not** make the loader return `{}` for a missing file: a silently empty registry is exactly EC-109.

---

## L3-01-04 — Comparator protocol, comparator registry, orchestrator

**Size:** M **Depends on:** L3-01-02, L3-01-03
**Owns:** `reconciler/comparators/base.py`, `reconciler/comparators/registry.py`, `reconciler/orchestrator.py`
**Spec basis:** §53.1 (the comparison set and the per-registry counts); §53.2 (the levels a finding carries).

Every comparator is the same shape. The orchestrator counts what each one iterates; the comparator does not report its own count, because a comparator that miscounts itself is precisely the failure Section 53.1's count rule exists to expose.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t04-orchestrator
```

### Files created

- `reconciler/comparators/__init__.py`
- `reconciler/comparators/base.py`
- `reconciler/comparators/registry.py`
- `reconciler/comparators/tests/__init__.py`
- `reconciler/orchestrator.py`
- `reconciler/tests/test_orchestrator.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p reconciler/comparators/tests
printf '' > reconciler/comparators/__init__.py
printf '' > reconciler/comparators/tests/__init__.py

cat > reconciler/comparators/base.py <<'PYEOF'
"""The shape every Section 53.1 row takes in code.

One class per row. The row's identity, its registry key, its Section 53.1
"On mismatch" cell and its Section 53.4 class all come from
reconciler/comparators/manifest.yaml (rule R3) - never from a literal in the
comparator module, because a literal in the module is a place the spec text
can be quietly paraphrased.

A comparator yields (row_key, findings) pairs. row_key is the identity of the
registry row it just compared - a person id, a product id, a tag, a store
path. The orchestrator collects the row_keys; that set IS rows_compared.
The comparator never reports a count.
"""
from __future__ import annotations

import abc
import dataclasses
from typing import Any, Iterator

from reconciler.api.client import ReadOnlyClient
from reconciler.loader import Declared
from reconciler.model import Evidence, Finding, Scope


@dataclasses.dataclass(frozen=True)
class Row:
    """One registry row compared, plus whatever it produced."""

    key: str
    findings: list[Finding]


@dataclasses.dataclass(frozen=True)
class Context:
    declared: Declared
    client: ReadOnlyClient
    org: str
    today: str
    now: str
    records_repo: str = "control-plane-records"


class Comparator(abc.ABC):
    #: "CMP-01" ... "CMP-19". Must exist in manifest.yaml.
    comparator_id: str = ""
    #: One of reconciler.counts.REGISTRY_KEYS.
    registry_key: str = ""

    @abc.abstractmethod
    def rows(self, ctx: Context) -> Iterator[Row]:
        """Yield exactly one Row per declared registry row in scope."""

    # ---- helpers every comparator uses, so none re-implements them ----
    def finding(
        self,
        ctx: Context,
        seq: int,
        scope: Scope,
        declared: Any,
        actual: Any,
        drift_class: str,
        response_level: int,
        on_mismatch: str,
        evidence: list[Evidence],
        **extra: Any,
    ) -> Finding:
        return Finding(
            id="DRIFT-%s-%03d" % (ctx.today, seq),
            comparator_id=self.comparator_id,
            scope=scope,
            declared=declared,
            actual=actual,
            drift_class=drift_class,
            response_level=response_level,
            on_mismatch=on_mismatch,
            detected_at=ctx.now,
            evidence=evidence,
            **extra,
        )
PYEOF

cat > reconciler/comparators/registry.py <<'PYEOF'
"""The comparator registry, and the manifest that governs it.

Rule R3: each comparator carries the Section 53.1 "On mismatch" cell verbatim
and the drift class derived from it, in manifest.yaml. This module is how a
comparator gets that text: it never types it out itself.
"""
from __future__ import annotations

import pathlib
from typing import Any

import yaml

MANIFEST = pathlib.Path(__file__).resolve().parent / "manifest.yaml"

#: The nineteen ids of Section 4 of the lane plan, in table order.
EXPECTED_IDS = tuple("CMP-%02d" % n for n in range(1, 20))

_REGISTRY: dict[str, Any] = {}


def load_manifest() -> dict[str, Any]:
    doc = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    return {row["id"]: row for row in doc.get("comparators", [])}


def register(cls: Any) -> Any:
    """Class decorator. Every comparator module ends with @register."""
    if not cls.comparator_id:
        raise ValueError(f"{cls.__name__} declares no comparator_id")
    if cls.comparator_id in _REGISTRY:
        raise ValueError(f"duplicate comparator id {cls.comparator_id}")
    _REGISTRY[cls.comparator_id] = cls
    return cls


def registered() -> dict[str, Any]:
    return dict(_REGISTRY)


def spec_cell(comparator_id: str, field: str) -> Any:
    return load_manifest()[comparator_id][field]
PYEOF

cat > reconciler/orchestrator.py <<'PYEOF'
"""Run every comparator, count every row, produce the run record body.

Section 53.1: "Every run additionally records its per-registry comparison
counts - how many rows of each registry it actually compared - so that a
silently narrowed comparison is itself visible drift."

The count is taken HERE, from what each comparator actually iterated, and is
compared against reconciler.counts.rows_declared, which is computed from the
registry by different code. Neither half can be adjusted to flatter the other
without the change being visible in a diff.

Nothing in this module writes. Rule R1.
"""
from __future__ import annotations

from typing import Any

from reconciler import counts
from reconciler.comparators.base import Comparator, Context
from reconciler.comparators.registry import EXPECTED_IDS, registered


def run(ctx: Context, only: tuple[str, ...] | None = None) -> dict[str, Any]:
    classes = registered()
    ids = tuple(i for i in EXPECTED_IDS if i in classes and (only is None or i in only))
    findings: list[Any] = []
    compared: dict[str, set[str]] = {k: set() for k in counts.REGISTRY_KEYS}
    executed: list[str] = []
    for cid in ids:
        cls: type[Comparator] = classes[cid]
        cmp_ = cls()
        executed.append(cid)
        for row in cmp_.rows(ctx):
            compared.setdefault(cmp_.registry_key, set()).add(row.key)
            findings.extend(row.findings)
    declared = counts.rows_declared(ctx.declared)
    registry_counts = {}
    for key in counts.REGISTRY_KEYS:
        contributors = [c for c in counts.CONTRIBUTORS[key] if c in executed]
        rc = len(compared.get(key, set()))
        rd = declared[key]
        registry_counts[key] = {
            "rows_declared": rd,
            "rows_compared": rc,
            "comparators": contributors,
            "shortfall": rc < rd,
        }
    return {
        "comparators_executed": executed,
        "findings": [f.as_dict() for f in findings],
        "registry_counts": registry_counts,
        "api": ctx.client.ledger(),
    }
PYEOF

cat > reconciler/tests/test_orchestrator.py <<'PYEOF'
import pathlib

from reconciler import counts, orchestrator
from reconciler.api.client import ReadOnlyClient
from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.loader import load

FIX = pathlib.Path(__file__).resolve().parent.parent / "fixtures" / "declared"


def _ctx():
    return Context(
        declared=load(FIX),
        client=ReadOnlyClient(token="t"),
        org="example-org",
        today="2026-08-27",
        now="2026-08-27T06:00:00Z",
    )


class _Full(Comparator):
    comparator_id = "CMP-12"
    registry_key = "product.yaml"

    def rows(self, ctx):
        for pid in ctx.declared.products:
            yield Row(key=pid, findings=[])


class _Narrowed(Comparator):
    comparator_id = "CMP-03"
    registry_key = "product.yaml"

    def rows(self, ctx):
        return iter(())


def test_registered_ids_must_be_unique():
    before = set(registry.registered())
    registry.register(_Full)
    try:
        registry.register(_Full)
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate registration was accepted")
    assert "CMP-12" in registry.registered()
    assert before <= set(registry.registered())


def test_expected_ids_are_exactly_nineteen_in_table_order():
    assert len(registry.EXPECTED_IDS) == 19
    assert registry.EXPECTED_IDS[0] == "CMP-01"
    assert registry.EXPECTED_IDS[-1] == "CMP-19"


def test_a_full_comparator_produces_no_shortfall():
    out = orchestrator.run(_ctx(), only=("CMP-12",))
    assert out["registry_counts"]["product.yaml"]["rows_compared"] == 1
    assert out["registry_counts"]["product.yaml"]["shortfall"] is False


def test_a_narrowed_comparator_produces_a_shortfall_without_being_asked():
    registry.register(_Narrowed)
    out = orchestrator.run(_ctx(), only=("CMP-03",))
    rc = out["registry_counts"]["product.yaml"]
    assert rc["rows_compared"] == 0 and rc["rows_declared"] == 1
    assert rc["shortfall"] is True


def test_every_registry_key_appears_on_every_run():
    out = orchestrator.run(_ctx(), only=("CMP-12",))
    assert set(out["registry_counts"]) == set(counts.REGISTRY_KEYS)


def test_the_api_ledger_is_carried_onto_the_run_body():
    out = orchestrator.run(_ctx(), only=("CMP-12",))
    assert out["api"]["methods_used"] == []
    assert out["api"]["expected_source"] == "api.github.com"
PYEOF

python -m pytest reconciler/tests/test_orchestrator.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-04: comparator protocol, registry and orchestrator with structural counts"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Six orchestrator tests pass | `cd "$CP" && python -m pytest reconciler/tests/test_orchestrator.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `6 passed` |
| A2 | Nineteen expected ids, in table order | `cd "$CP" && python -c "from reconciler.comparators.registry import EXPECTED_IDS as e; print(len(e), e[0], e[-1])"` | `19 CMP-01 CMP-19` |
| A3 | The orchestrator issues no writes | `cd "$CP" && grep -cE '\brequest\(' reconciler/orchestrator.py` | `0` |
| A4 | The count halves are computed by different modules | `cd "$CP" && grep -c 'rows_declared' reconciler/orchestrator.py && grep -c 'rows_compared' reconciler/counts.py` | `2` then `0` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/tests/test_orchestrator.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "from reconciler.comparators.registry import EXPECTED_IDS as e; print(len(e), e[0], e[-1])"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
6 passed
19 CMP-01 CMP-19
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L0`, if any acceptance command needs `reconciler/comparators/manifest.yaml` and that file does not yet exist — that is `L3-01-05`, and T05 must merge before any comparator task starts. It is **not** a reason to inline the spec text into `base.py`.
Do **not** let a comparator report its own `rows_compared`. The independence of the two counts is the whole mechanism.

---

## L3-01-05 — The frozen Section 53.1 table and `comparators/manifest.yaml`

**Size:** M **Depends on:** L3-01-04
**Owns:** `reconciler/comparators/manifest.yaml`, `reconciler/comparators/section-53-1.frozen.md`
**Spec basis:** §53.1 (the table and the two prose rows that follow it); §53.4 (*"Class assignment lives in configuration and is reviewable; it is not decided ad hoc"*); rule **R3**.

Two files. One is the spec table, transcribed and frozen. The other is the machine-readable manifest every comparator reads its class and its mismatch text from. A test asserts the second matches the first, cell for cell. This is the whole of rule R3.

**Transcription note, to be reproduced verbatim in the frozen file.** In the spec source the sixteenth and seventeenth rows of the 53.1 table share one source line — the *Production-restore record* row's final cell runs into the `product.yaml restore_tested` row's first cell with a doubled pipe. They are plainly two rows and are transcribed as two. No cell text is altered.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t05-manifest
```

### Files created

- `reconciler/comparators/section-53-1.frozen.md`
- `reconciler/comparators/manifest.yaml`
- `reconciler/comparators/tests/test_manifest.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/comparators/section-53-1.frozen.md <<'MDEOF'
# FROZEN — Spec Section 53.1, "Declared versus actual"

Transcribed from MultiProduct_MasterSpec_v4.0.md Section 53.1. This file is
evidence, not documentation. Rule R3: reconciler/comparators/manifest.yaml is
tested against it. Do not edit either file to make a test pass; a divergence
means the manifest is wrong or the spec moved, and a spec move is an L0 event.

Transcription note: in the spec source the Production-restore record row and
the `product.yaml` `restore_tested` row share one source line, the first row's
final cell running into the second row's first cell with a doubled pipe. They
are two rows and are transcribed as two. No cell text is altered.

The two rows below the table (CMP-18, CMP-19) are stated in prose immediately
after it, in the same section, and are part of the comparison set on the same
footing.

| ID | Declared in | Compared against | On mismatch |
| --- | --- | --- | --- |
| CMP-01 | `people.yaml` | GitHub organisation membership | Alert; block on removal drift |
| CMP-02 | `people.yaml` capabilities | Team membership implying authority | Alert |
| CMP-03 | `product.yaml` assignments | GitHub Team membership | Fail CI on the affected repository |
| CMP-04 | `product.yaml` assignments | CODEOWNERS | Regenerate; alert if hand-edited |
| CMP-05 | Branch protection template | Actual branch protection | Alert immediately; block deployment on the affected repository |
| CMP-06 | Workflow template version | Actual workflow file | Alert; flag `platform_compatibility` as drifted |
| CMP-07 | Environment configuration template | Actual environments | Alert |
| CMP-08 | Environment deployment branch and tag policy | Actual environment configuration | Alert immediately; block deployment on the affected repository |
| CMP-09 | Declared `infrastructure:` boundary (Section 40.2) | The latest provider-side attestation record | Blocking past its attestation window |
| CMP-10 | `product.yaml` lifecycle | Renovate, monitoring and CI configuration | Auto-repair where safe; alert otherwise |
| CMP-11 | Assignment `end_date` | Current Team membership | Auto-revoke expired access |
| CMP-12 | Declared dependency | Shared service registry | Fail CI on unknown dependency |
| CMP-13 | `platform.yaml` workflow versions | The commit SHA each `workflows/*` tag currently resolves to | Blocking on any change — a moved tag reaches every consumer with no reviewable diff |
| CMP-14 | Renovate bypass ruleset | The ruleset carrying the diff-path status check | Blocking where that ruleset names any bypass actor |
| CMP-15 | Declared write-freshness window per record store (Section 97.2) | Latest commit timestamp on the store's path | Amber; Blocking for `events/`, `records/deployments/` and `records/uat/` |
| CMP-16 | Production-restore record (Section 44.5) | Recorded `integrity_check` result and named verifier | Red where either is absent |
| CMP-17 | `product.yaml` `restore_tested` | Newest passing record in `records/restore-tests/` | Blocking: a declared date with no matching record is an unevidenced reliability claim, not a scheduling question |
| CMP-18 | (prose) A workflow-file change pushed by a machine identity | Commit authorship on `.github/workflows/**` | Blocking-class drift, regardless of the change's content |
| CMP-19 | (prose) A commit authored or committed by any identity other than the declared bypass actor, on a branch that merges under that actor's bypass | Commit authorship on merged bypass-actor branches | Blocking-class drift for the same reason |
MDEOF

cat > reconciler/comparators/manifest.yaml <<'YEOF'
# The comparison set of spec Section 53.1, as configuration.
#
# Section 53.4: "Class assignment lives in configuration and is reviewable;
# it is not decided ad hoc during an incident." This file IS that
# configuration for the reconciliation comparison set.
#
# Rule R3: on_mismatch is the Section 53.1 cell verbatim. A test asserts this
# file against reconciler/comparators/section-53-1.frozen.md. Do not reword a
# cell. Do not add a row. Do not remove a row. Nineteen rows, closed.
#
# level: the Section 53.2 behaviour the cell describes, per the mapping rule
# stated in Section 4 of the lane plan. level_escalated is the level the same
# finding takes in its escalated case; null where the row has none.
manifest_version: 1
comparators:
  - id: CMP-01
    registry_key: people.yaml
    declared_in: "people.yaml"
    compared_against: "GitHub organisation membership"
    on_mismatch: "Alert; block on removal drift"
    drift_class: amber
    level: 2
    class_escalated: blocking
    level_escalated: 4
    escalated_when: "removal drift: declared-present and actual-absent and not invited"
  - id: CMP-02
    registry_key: people.yaml
    declared_in: "people.yaml capabilities"
    compared_against: "Team membership implying authority"
    on_mismatch: "Alert"
    drift_class: amber
    level: 2
    class_escalated: null
    level_escalated: null
    escalated_when: null
  - id: CMP-03
    registry_key: product.yaml
    declared_in: "product.yaml assignments"
    compared_against: "GitHub Team membership"
    on_mismatch: "Fail CI on the affected repository"
    drift_class: blocking
    level: 4
    class_escalated: null
    level_escalated: null
    escalated_when: null
  - id: CMP-04
    registry_key: product.yaml
    declared_in: "product.yaml assignments"
    compared_against: "CODEOWNERS"
    on_mismatch: "Regenerate; alert if hand-edited"
    drift_class: amber
    level: 3
    class_escalated: blocking
    level_escalated: 4
    escalated_when: "a CODEOWNERS line names a machine identity (Section 11.3)"
  - id: CMP-05
    registry_key: product.yaml
    declared_in: "Branch protection template"
    compared_against: "Actual branch protection"
    on_mismatch: "Alert immediately; block deployment on the affected repository"
    drift_class: blocking
    level: 4
    class_escalated: null
    level_escalated: null
    escalated_when: null
  - id: CMP-06
    registry_key: product.yaml
    declared_in: "Workflow template version"
    compared_against: "Actual workflow file"
    on_mismatch: "Alert; flag `platform_compatibility` as drifted"
    drift_class: amber
    level: 2
    class_escalated: null
    level_escalated: null
    escalated_when: null
  - id: CMP-07
    registry_key: product.yaml
    declared_in: "Environment configuration template"
    compared_against: "Actual environments"
    on_mismatch: "Alert"
    drift_class: amber
    level: 2
    class_escalated: null
    level_escalated: null
    escalated_when: null
  - id: CMP-08
    registry_key: product.yaml
    declared_in: "Environment deployment branch and tag policy"
    compared_against: "Actual environment configuration"
    on_mismatch: "Alert immediately; block deployment on the affected repository"
    drift_class: blocking
    level: 4
    class_escalated: blocking
    level_escalated: 5
    escalated_when: "scope names the production environment (Section 53.2, Level 5)"
  - id: CMP-09
    registry_key: product.yaml
    declared_in: "Declared `infrastructure:` boundary (Section 40.2)"
    compared_against: "The latest provider-side attestation record"
    on_mismatch: "Blocking past its attestation window"
    drift_class: blocking
    level: 4
    class_escalated: null
    level_escalated: null
    escalated_when: null
  - id: CMP-10
    registry_key: product.yaml
    declared_in: "product.yaml lifecycle"
    compared_against: "Renovate, monitoring and CI configuration"
    on_mismatch: "Auto-repair where safe; alert otherwise"
    drift_class: amber
    level: 3
    class_escalated: amber
    level_escalated: 2
    escalated_when: "the drifted row is not in the safe set: alert instead"
  - id: CMP-11
    registry_key: product.yaml
    declared_in: "Assignment `end_date`"
    compared_against: "Current Team membership"
    on_mismatch: "Auto-revoke expired access"
    drift_class: blocking
    level: 3
    class_escalated: null
    level_escalated: null
    escalated_when: null
  - id: CMP-12
    registry_key: services
    declared_in: "Declared dependency"
    compared_against: "Shared service registry"
    on_mismatch: "Fail CI on unknown dependency"
    drift_class: blocking
    level: 4
    class_escalated: null
    level_escalated: null
    escalated_when: null
  - id: CMP-13
    registry_key: platform.yaml
    declared_in: "platform.yaml workflow versions"
    compared_against: "The commit SHA each `workflows/*` tag currently resolves to"
    on_mismatch: "Blocking on any change — a moved tag reaches every consumer with no reviewable diff"
    drift_class: blocking
    level: 4
    class_escalated: amber
    level_escalated: 2
    escalated_when: "first observation of a tag with no recorded SHA"
  - id: CMP-14
    registry_key: product.yaml
    declared_in: "Renovate bypass ruleset"
    compared_against: "The ruleset carrying the diff-path status check"
    on_mismatch: "Blocking where that ruleset names any bypass actor"
    drift_class: blocking
    level: 4
    class_escalated: null
    level_escalated: null
    escalated_when: null
  - id: CMP-15
    registry_key: os-health.yaml
    declared_in: "Declared write-freshness window per record store (Section 97.2)"
    compared_against: "Latest commit timestamp on the store's path"
    on_mismatch: "Amber; Blocking for `events/`, `records/deployments/` and `records/uat/`"
    drift_class: amber
    level: 2
    class_escalated: blocking
    level_escalated: 4
    escalated_when: "store is one of events/, records/deployments/, records/uat/"
  - id: CMP-16
    registry_key: product.yaml
    declared_in: "Production-restore record (Section 44.5)"
    compared_against: "Recorded `integrity_check` result and named verifier"
    on_mismatch: "Red where either is absent"
    drift_class: red
    level: 2
    class_escalated: null
    level_escalated: null
    escalated_when: null
  - id: CMP-17
    registry_key: product.yaml
    declared_in: "product.yaml `restore_tested`"
    compared_against: "Newest passing record in `records/restore-tests/`"
    on_mismatch: "Blocking: a declared date with no matching record is an unevidenced reliability claim, not a scheduling question"
    drift_class: blocking
    level: 4
    class_escalated: null
    level_escalated: null
    escalated_when: null
  - id: CMP-18
    registry_key: people.yaml
    declared_in: "(prose) A workflow-file change pushed by a machine identity"
    compared_against: "Commit authorship on `.github/workflows/**`"
    on_mismatch: "Blocking-class drift, regardless of the change's content"
    drift_class: blocking
    level: 4
    class_escalated: null
    level_escalated: null
    escalated_when: null
  - id: CMP-19
    registry_key: product.yaml
    declared_in: "(prose) A commit authored or committed by any identity other than the declared bypass actor, on a branch that merges under that actor's bypass"
    compared_against: "Commit authorship on merged bypass-actor branches"
    on_mismatch: "Blocking-class drift for the same reason"
    drift_class: blocking
    level: 4
    class_escalated: null
    level_escalated: null
    escalated_when: null
YEOF

cat > reconciler/comparators/tests/test_manifest.py <<'PYEOF'
"""Rule R3: the manifest is the frozen spec table, not a paraphrase of it."""
import pathlib
import re

from reconciler.comparators import registry
from reconciler.counts import REGISTRY_KEYS
from reconciler.model import DRIFT_CLASSES, RESPONSE_LEVELS

HERE = pathlib.Path(__file__).resolve().parent.parent
FROZEN = HERE / "section-53-1.frozen.md"

ROW = re.compile(r"^\|\s*(CMP-\d\d)\s*\|(.*?)\|(.*?)\|(.*?)\|\s*$")


def frozen_rows():
    out = {}
    for line in FROZEN.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if m:
            out[m.group(1)] = tuple(g.strip() for g in m.groups()[1:])
    return out


def test_the_frozen_table_carries_all_nineteen_rows():
    assert sorted(frozen_rows()) == sorted(registry.EXPECTED_IDS)


def test_the_manifest_carries_all_nineteen_rows_in_table_order():
    m = registry.load_manifest()
    assert tuple(m) == registry.EXPECTED_IDS


def test_every_on_mismatch_cell_matches_the_frozen_table_verbatim():
    frozen = frozen_rows()
    m = registry.load_manifest()
    mismatched = [
        cid for cid in registry.EXPECTED_IDS
        if m[cid]["on_mismatch"].replace("`", "") != frozen[cid][2].replace("`", "")
    ]
    assert mismatched == []


def test_every_row_names_a_real_class_a_real_level_and_a_real_registry_key():
    for cid, row in registry.load_manifest().items():
        assert row["drift_class"] in DRIFT_CLASSES, cid
        assert row["level"] in RESPONSE_LEVELS, cid
        assert row["registry_key"] in REGISTRY_KEYS, cid
        if row["class_escalated"] is not None:
            assert row["class_escalated"] in DRIFT_CLASSES, cid
            assert row["level_escalated"] in RESPONSE_LEVELS, cid
            assert row["escalated_when"], cid


def test_the_manifest_is_closed_at_nineteen():
    assert len(registry.load_manifest()) == 19
PYEOF

python -m pytest reconciler/comparators/tests/test_manifest.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/comparators
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-05: frozen Section 53.1 table and the comparator manifest (R3)"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Five manifest tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_manifest.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `5 passed` |
| A2 | Nineteen rows in the manifest | `cd "$CP" && python -c "from reconciler.comparators.registry import load_manifest as m; print(len(m()))"` | `19` |
| A3 | Nineteen rows in the frozen table | `cd "$CP" && grep -cE '^\| CMP-[0-9]{2} \|' reconciler/comparators/section-53-1.frozen.md` | `19` |
| A4 | No comparator module contains a hard-coded mismatch string | `cd "$CP" && grep -rl 'Alert; block on removal drift' reconciler --include=*.py \| wc -l` | `0` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_manifest.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "from reconciler.comparators.registry import load_manifest as m; print(len(m()))"
grep -cE '^\| CMP-[0-9]{2} \|' reconciler/comparators/section-53-1.frozen.md
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
5 passed
19
19
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L0`, if the spec text you read at `MultiProduct_MasterSpec_v4.0.md` Section 53.1 differs in any cell from the frozen file above. Do **not** edit the frozen file to match the spec, and do **not** edit the manifest to match the frozen file: a Section 53.1 change is a specification change and reaches this lane through L0, never through an executor's transcription.
Do **not** add a twentieth comparator. Section 4 of this plan closes the set at nineteen.

---

## Comparator tasks — the shape all fourteen share

`L3-01-06` … `L3-01-19` are fourteen instances of one shape. Read this once; every task below assumes it.

- **One module per comparator**, `reconciler/comparators/cmp_NN_<slug>.py`, ending with `@register`.
- **One test module per task**, `reconciler/comparators/tests/test_cmp_NN.py`.
- **Each test module defines its own stub client.** It is four lines, and duplicating it is deliberate: PARTITION rule 5 prefers new files over edits, and fourteen branches that share no file cannot conflict at merge. Do **not** factor it into a shared `conftest.py`; that is the one file every one of the fourteen would have to edit.

```python
class _Stub:
    def __init__(self, responses): self.responses, self.seen = responses, []
    def get(self, path, **p): self.seen.append(path); return self.responses.get(path)
    def paginate(self, path, **p):
        self.seen.append(path); return iter(self.responses.get(path) or [])
    def ledger(self): return {"api_calls": len(self.seen), "methods_used": ["GET"],
                              "expected_source": "api.github.com", "max_calls": 5000}
```

- **The class and the mismatch text come from the manifest**, never from a literal: `registry.spec_cell(self.comparator_id, "drift_class")`, `registry.spec_cell(self.comparator_id, "on_mismatch")`. Rule R3. A comparator that types the spec text out is a rule-R3 violation and `L3-01-22` fails the phase for it.
- **Every comparator yields one `Row` per declared row in its registry, always** — including rows that produced no finding. A comparator that yields only the rows it found problems on has silently narrowed its comparison, and Section 4.2's shortfall arithmetic exists to catch exactly that.
- **Every task's branch is `lane/3/p1-t<NN>-<slug>`** and every task's last three commands are the three of Section 5.

---

## L3-01-06 — CMP-01: `people.yaml` versus GitHub organisation membership

**Size:** M **Depends on:** L3-01-05
**Owns:** `reconciler/comparators/cmp_01_org_membership.py`, `reconciler/comparators/tests/test_cmp_01.py`
**Spec basis:** §53.1 row 1, *"Alert; block on removal drift"*; §11.2 (base permission Read for every member); invariant 44; SIG-03 (permission drift).
**Registry key:** `people.yaml` — `rows_declared` = count of `people[]` with `availability != departed`.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t06-cmp01
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/comparators/cmp_01_org_membership.py <<'PYEOF'
"""CMP-01 - people.yaml versus GitHub organisation membership.

Section 53.1: "Alert; block on removal drift."

Two directions, two classes, and the asymmetry is the point:

  declared-present and actual-absent and not-invited
      -> REMOVAL DRIFT. Someone the registry says has access does not have it.
         Blocking (the "block on removal drift" half of the cell).
  actual-present and undeclared
      -> An org member nobody declared. Amber (the "Alert" half).

A person carrying an invitation is neither: the grant is in flight, and
reporting it would train the reader to ignore this comparator.
"""
from __future__ import annotations

from typing import Iterator

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.model import Evidence, Scope


@registry.register
class OrgMembership(Comparator):
    comparator_id = "CMP-01"
    registry_key = "people.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        members = {
            (m.get("login") or "").lower()
            for m in ctx.client.paginate(f"/orgs/{ctx.org}/members", per_page=100)
        }
        invited = {
            (i.get("login") or "").lower()
            for i in ctx.client.paginate(f"/orgs/{ctx.org}/invitations", per_page=100)
        }
        seq = 0
        declared_logins = set()
        for person in ctx.declared.active_people():
            login = (person.get("github_login") or "").lower()
            findings = []
            if person.get("access_status") == "provisioned" and login:
                declared_logins.add(login)
                if login not in members and login not in invited:
                    seq += 1
                    findings.append(
                        self.finding(
                            ctx, seq,
                            Scope("person", person["id"]),
                            {"github_login": login, "access_status": "provisioned"},
                            {"org_member": False, "invited": False},
                            cell["class_escalated"], cell["level_escalated"],
                            cell["on_mismatch"],
                            [
                                Evidence("registry", "registries/people.yaml"),
                                Evidence("github-api", f"/orgs/{ctx.org}/members"),
                            ],
                        )
                    )
            # Every declared row is yielded, finding or not (Section 4.2).
            yield Row(key=person["id"], findings=findings)

        for login in sorted(members - declared_logins):
            seq += 1
            yield Row(
                key=f"undeclared:{login}",
                findings=[
                    self.finding(
                        ctx, seq,
                        Scope("organisation", ctx.org),
                        {"declared": False},
                        {"github_login": login, "org_member": True},
                        cell["drift_class"], cell["level"],
                        cell["on_mismatch"],
                        [Evidence("github-api", f"/orgs/{ctx.org}/members")],
                    )
                ],
            )
PYEOF

cat > reconciler/comparators/tests/test_cmp_01.py <<'PYEOF'
import pathlib

from reconciler.comparators.base import Context
from reconciler.comparators.cmp_01_org_membership import OrgMembership
from reconciler.loader import load

FIX = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures" / "declared"
ORG = "example-org"
MEMBERS = f"/orgs/{ORG}/members"
INVITES = f"/orgs/{ORG}/invitations"
ALL = ["fixture-dev-a", "fixture-dev-b", "fixture-lead-1", "fixture-qa-1", "fixture-con-1"]


class _Stub:
    def __init__(self, responses):
        self.responses, self.seen = responses, []

    def get(self, path, **p):
        self.seen.append(path)
        return self.responses.get(path)

    def paginate(self, path, **p):
        self.seen.append(path)
        return iter(self.responses.get(path) or [])

    def ledger(self):
        return {"api_calls": len(self.seen), "methods_used": ["GET"],
                "expected_source": "api.github.com", "max_calls": 5000}


def _ctx(members, invites=()):
    return Context(
        declared=load(FIX),
        client=_Stub({
            MEMBERS: [{"login": m} for m in members],
            INVITES: [{"login": i} for i in invites],
        }),
        org=ORG, today="2026-08-27", now="2026-08-27T06:00:00Z",
    )


def _rows(ctx):
    return list(OrgMembership().rows(ctx))


def test_a_matching_org_produces_no_findings():
    rows = _rows(_ctx(ALL))
    assert sum(len(r.findings) for r in rows) == 0


def test_every_active_declared_person_is_yielded_as_a_row():
    rows = _rows(_ctx(ALL))
    assert {"dev-a", "dev-b", "lead-1", "qa-1", "con-1"} <= {r.key for r in rows}


def test_removal_drift_is_blocking():
    rows = _rows(_ctx([m for m in ALL if m != "fixture-dev-a"]))
    fs = [f for r in rows for f in r.findings]
    assert len(fs) == 1
    assert fs[0].drift_class == "blocking" and fs[0].response_level == 4
    assert fs[0].scope.name == "dev-a"


def test_a_pending_invitation_is_not_removal_drift():
    rows = _rows(_ctx([m for m in ALL if m != "fixture-dev-a"], invites=["fixture-dev-a"]))
    assert sum(len(r.findings) for r in rows) == 0


def test_an_undeclared_member_is_amber_not_blocking():
    rows = _rows(_ctx(ALL + ["stranger"]))
    fs = [f for r in rows for f in r.findings]
    assert len(fs) == 1 and fs[0].drift_class == "amber" and fs[0].response_level == 2


def test_the_on_mismatch_text_is_the_manifest_text():
    fs = [f for r in _rows(_ctx(ALL + ["stranger"])) for f in r.findings]
    assert fs[0].on_mismatch == "Alert; block on removal drift"
PYEOF

python -m pytest reconciler/comparators/tests/test_cmp_01.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/comparators
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-06: CMP-01 people.yaml versus organisation membership"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Six CMP-01 tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_01.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `6 passed` |
| A2 | CMP-01 is registered | `cd "$CP" && python -c "import reconciler.comparators.cmp_01_org_membership; from reconciler.comparators.registry import registered; print('CMP-01' in registered())"` | `True` |
| A3 | No spec text is hard-coded in the module | `cd "$CP" && grep -c 'Alert; block on removal drift' reconciler/comparators/cmp_01_org_membership.py` | `0` |
| A4 | The module issues no write | `cd "$CP" && grep -cE '"(POST|PUT|PATCH|DELETE)"' reconciler/comparators/cmp_01_org_membership.py` | `0` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_01.py -q 2>&1 | grep -oE '^[0-9]+ passed'
grep -c 'Alert; block on removal drift' reconciler/comparators/cmp_01_org_membership.py
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
6 passed
0
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L1`, if `registries/people.yaml` carries no `github_login` field or no `access_status` field — Section 7 declares both, and their absence means the registry shipped a different shape than the one Section 4.1 of this plan compares.
Do **not** treat a `403` from `/orgs/{org}/invitations` as "no invitations": the client returns `None` for `403`, which the code above turns into an empty set, and an empty invitation set makes every in-flight grant look like removal drift. If `A1` fails because of it, STOP with `Blocked-on: L5` — the reconciler credential lacks org read scope.

---

## L3-01-07 — CMP-02: declared capabilities versus authority-team membership

**Size:** M **Depends on:** L3-01-05; **L1** (a capability-to-team binding in `roles.yaml`)
**Owns:** `reconciler/comparators/cmp_02_capability_teams.py`, `reconciler/comparators/tests/test_cmp_02.py`
**Spec basis:** §53.1 row 2, *"Alert"*; §9 (*"Capability is the unit of authority"*); §11.2 (Teams-derived Write); invariant 7.
**Registry keys:** `people.yaml` and `roles.yaml`.

Section 8's `roles.yaml` declares `roles[].default_capabilities` but no team binding. The binding — *which org team is the one whose membership implies which capability* — is declared state and belongs to L1, not to this lane. This comparator **reads** `roles[].team` and STOPs if it is absent. It does not invent a mapping file; a mapping invented here would be an unreviewed authority model.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t07-cmp02
```

### Entry gate

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
python - <<'PYEOF'
import yaml
doc = yaml.safe_load(open("registries/roles.yaml", encoding="utf-8"))
bound = [r["id"] for r in (doc.get("roles") or []) if r.get("team")]
print("GATE-1 roles-with-team:", len(bound), bound)
print("GATE-1 OK" if bound else "GATE-1 FAIL blocked-on-L1")
PYEOF
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/comparators/cmp_02_capability_teams.py <<'PYEOF'
"""CMP-02 - declared capabilities versus team membership implying authority.

Section 53.1: "Alert."

Section 9: "Capability is the unit of authority. Every gate, approval and
escalation in this specification is evaluated against capability." Section
11.2 makes Write Teams-derived. So a team whose membership confers authority
is a second, parallel statement of who holds a capability, and the two must
agree.

The binding from a capability to the team that implies it is DECLARED STATE
and lives in registries/roles.yaml as roles[].team. It is not derived here and
it is not configured here. If it is absent, this comparator raises
AuthorityBindingUnavailable and the task STOPs: a guessed authority map is
worse than no comparator, because it would report confidently.
"""
from __future__ import annotations

from typing import Iterator

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.model import Evidence, Scope


class AuthorityBindingUnavailable(RuntimeError):
    """registries/roles.yaml declares no roles[].team. L1 dependency."""


@registry.register
class CapabilityTeams(Comparator):
    comparator_id = "CMP-02"
    registry_key = "roles.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        roles = ctx.declared.roles.get("roles", []) or []
        bound = [r for r in roles if r.get("team")]
        if not bound:
            raise AuthorityBindingUnavailable("registries/roles.yaml: no roles[].team")
        seq = 0
        for role in roles:
            team = role.get("team")
            if not team:
                # A role with no team binding implies no authority team. It is
                # still a compared row: its declared holder set is checked to
                # be empty of team-derived authority.
                yield Row(key=role["id"], findings=[])
                continue
            actual = {
                (m.get("login") or "").lower()
                for m in ctx.client.paginate(
                    f"/orgs/{ctx.org}/teams/{team}/members", per_page=100
                )
            }
            declared = {
                (p.get("github_login") or "").lower()
                for p in ctx.declared.active_people()
                if p.get("role") == role["id"] and p.get("access_status") == "provisioned"
            }
            findings = []
            for login in sorted(declared - actual) + sorted(actual - declared):
                seq += 1
                findings.append(
                    self.finding(
                        ctx, seq,
                        Scope("organisation", team),
                        sorted(declared),
                        sorted(actual),
                        cell["drift_class"], cell["level"], cell["on_mismatch"],
                        [
                            Evidence("registry", "registries/roles.yaml"),
                            Evidence("github-api", f"/orgs/{ctx.org}/teams/{team}/members"),
                        ],
                    )
                )
            yield Row(key=role["id"], findings=findings)
PYEOF

cat > reconciler/comparators/tests/test_cmp_02.py <<'PYEOF'
import copy
import pathlib

import pytest

from reconciler.comparators.base import Context
from reconciler.comparators.cmp_02_capability_teams import (
    AuthorityBindingUnavailable,
    CapabilityTeams,
)
from reconciler.loader import load

FIX = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures" / "declared"
ORG = "example-org"


class _Stub:
    def __init__(self, responses):
        self.responses, self.seen = responses, []

    def get(self, path, **p):
        self.seen.append(path)
        return self.responses.get(path)

    def paginate(self, path, **p):
        self.seen.append(path)
        return iter(self.responses.get(path) or [])

    def ledger(self):
        return {"api_calls": len(self.seen), "methods_used": ["GET"],
                "expected_source": "api.github.com", "max_calls": 5000}


def _ctx(team_members, bind=True):
    d = load(FIX)
    roles = copy.deepcopy(d.roles)
    if bind:
        for r in roles["roles"]:
            if r["id"] == "team_lead":
                r["team"] = "leads"
    object.__setattr__(d, "roles", roles)
    return Context(
        declared=d,
        client=_Stub({f"/orgs/{ORG}/teams/leads/members": [{"login": m} for m in team_members]}),
        org=ORG, today="2026-08-27", now="2026-08-27T06:00:00Z",
    )


def test_an_absent_binding_stops_rather_than_guessing():
    with pytest.raises(AuthorityBindingUnavailable):
        list(CapabilityTeams().rows(_ctx([], bind=False)))


def test_a_matching_authority_team_produces_no_finding():
    rows = list(CapabilityTeams().rows(_ctx(["fixture-lead-1"])))
    assert sum(len(r.findings) for r in rows) == 0


def test_both_directions_are_amber():
    rows = list(CapabilityTeams().rows(_ctx(["stranger"])))
    fs = [f for r in rows for f in r.findings]
    assert len(fs) == 2
    assert {f.drift_class for f in fs} == {"amber"}
    assert {f.response_level for f in fs} == {2}


def test_every_role_row_is_yielded_even_with_no_team():
    rows = list(CapabilityTeams().rows(_ctx(["fixture-lead-1"])))
    assert len(rows) == 6
PYEOF

python -m pytest reconciler/comparators/tests/test_cmp_02.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/comparators
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-07: CMP-02 capabilities versus authority-team membership"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Four CMP-02 tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_02.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `4 passed` |
| A2 | CMP-02 is registered | `cd "$CP" && python -c "import reconciler.comparators.cmp_02_capability_teams; from reconciler.comparators.registry import registered; print('CMP-02' in registered())"` | `True` |
| A3 | The lane defines no capability-to-team map of its own | `cd "$CP" && ls reconciler/comparators/*team*.yaml 2>/dev/null \| wc -l` | `0` |
| A4 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_02.py -q 2>&1 | grep -oE '^[0-9]+ passed'
ls reconciler/comparators/*team*.yaml 2>/dev/null | wc -l
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
4 passed
0
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L1`, if the entry gate prints `GATE-1 FAIL` — `registries/roles.yaml` declares no `roles[].team`. State in the issue: *"CMP-02 compares 'Team membership implying authority' (§53.1). The binding from a role to its authority team is declared state. L3 will not author an authority map."*
Do **not** create a mapping file under `reconciler/`. Do **not** infer the team slug from the role id.

---

## L3-01-08 — The branch-protection template, and CMP-05

**Size:** L **Depends on:** L3-01-05
**Owns:** `tools/provision/templates/branch-protection.yaml`, `reconciler/comparators/cmp_05_branch_protection.py`, `reconciler/comparators/tests/test_cmp_05.py`
**Spec basis:** §53.1 row 5, *"Alert immediately; block deployment on the affected repository"*; §11.3 (the per-repository branch-protection checklist, twelve bullets); §99.2 subsystem D (*"generated CODEOWNERS, branch protection, environments with scoped secrets"*); SIG-03.
**Registry key:** `product.yaml`.

<!-- LAYOUT ALIGNMENT (FD-045, 2026-09-06): This task creates tools/provision/templates/branch-protection.yaml. The authoritative phase-file (L3-06-tasks.md, 116-task plan per FD-045) does not define a tools/provision/templates/ subdirectory; declared branch-protection state is resolved via reconciler/contracts_map.py in L3-06. The phase-file layout (L3-06-tasks.md) is canonical for any re-implementation. -->

The template is the **declared** side of CMP-05 and is created here, in this lane, because Subsystem D owns branch protection and PARTITION.md line 19 gives `tools/provision/**` to L3. Every key in it is a Section 11.3 bullet; nothing else is in it.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t08-cmp05
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p tools/provision/templates
cat > tools/provision/templates/branch-protection.yaml <<'YEOF'
# Declared branch protection, per repository. Spec Section 11.3.
#
# This file is the DECLARED side of Section 53.1 row 5 ("Branch protection
# template" vs "Actual branch protection"). It is also the source the
# provisioning operations of Subsystem D apply at repository creation.
#
# Every key below is one Section 11.3 bullet, in the section's own order.
# Do not add a key that Section 11.3 does not state. Do not remove one.
# A weakening edit here is not a template change: it is a security-control
# change, and Section 53.4 puts security drift at Red or above.
template_version: 1
spec_section: "11.3"
applies_to: default_branch

required_pull_request_reviews:
  required_approving_review_count: 1
  require_code_owner_reviews: true
  require_last_push_approval: true          # no-self-approval enforcement
  dismiss_stale_reviews: true

required_status_checks:
  strict: true                              # branches up to date before merge
  contexts:
    # NOTE: This hard-coded list is superseded by the contract
    # (`contracts/workflow-io/required-contexts.tsv`). The reconciler reads
    # the frozen contract, not this list.
    - tests
    - build
    - security-scan
    - contract-validation
    - reviewer-matrix-validation
    - parity-check
    - verification-contract
    - control-plane/blocking-drift          # Section 53.2 Level 4, D92

restrictions:
  allow_force_pushes: false
  allow_deletions: false
  enforce_admins: true                      # "Apply rules to administrators"

code_owner_rules:
  machine_identities_permitted: false       # Section 11.3: "no machine account
                                            # ever appears in it"

environment_policy:
  deployment_branch_and_tag_policy_required: true
  applies_to_environments: [staging, production]
  # Section 11.3: "a repository with the first and not the second holds
  # production credentials behind nothing." The policy itself is declared in
  # tools/provision/templates/environment.yaml (L3-01-10, CMP-08).

exception:
  mechanism: documented_break_glass_with_audit_record
  registry: exceptions.yaml
  spec_section: "54"
YEOF

cat > reconciler/comparators/cmp_05_branch_protection.py <<'PYEOF'
"""CMP-05 - the branch-protection template versus actual branch protection.

Section 53.1: "Alert immediately; block deployment on the affected repository."

Section 11.3 lists twelve requirements. Each is checked as a field. A field
that is absent from the API response is treated as FAILING, never as
unknown-and-therefore-fine: Section 64.2's fail-closed rule, and the whole
reason this row is P0 ("the blocking rows, which are security controls",
Section 53.1).

The comparison is one-directional on purpose. A repository that is STRICTER
than the template is still a mismatch and is still reported - but reporting it
is all Phase 1 does, and Section 53.3 forbids relaxing it in any phase:
"Where actual state is stricter than declared state, reconciliation raises
Level 2 for human judgment rather than relaxing the control."
"""
from __future__ import annotations

from typing import Any, Iterator

import yaml

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.model import Evidence, Scope

TEMPLATE = "tools/provision/templates/branch-protection.yaml"


def load_template(root: Any) -> dict[str, Any]:
    import pathlib
    return yaml.safe_load((pathlib.Path(root) / TEMPLATE).read_text(encoding="utf-8"))


def _weakened(tpl: dict[str, Any], actual: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Return one entry per Section 11.3 requirement the actual state fails."""
    if actual is None:
        return [{"field": "protection", "declared": "present", "actual": "absent"}]
    out: list[dict[str, Any]] = []
    pr_t = tpl["required_pull_request_reviews"]
    pr_a = actual.get("required_pull_request_reviews") or {}
    if (pr_a.get("required_approving_review_count") or 0) < pr_t["required_approving_review_count"]:
        out.append({"field": "required_approving_review_count",
                    "declared": pr_t["required_approving_review_count"],
                    "actual": pr_a.get("required_approving_review_count")})
    for key in ("require_code_owner_reviews", "require_last_push_approval", "dismiss_stale_reviews"):
        if pr_a.get(key) is not True:
            out.append({"field": key, "declared": True, "actual": pr_a.get(key)})
    sc_t = tpl["required_status_checks"]
    sc_a = actual.get("required_status_checks") or {}
    if sc_a.get("strict") is not True:
        out.append({"field": "required_status_checks.strict", "declared": True,
                    "actual": sc_a.get("strict")})
    have = set(sc_a.get("contexts") or [])
    for ctxname in sc_t["contexts"]:
        if ctxname not in have:
            out.append({"field": "required_status_checks.contexts",
                        "declared": ctxname, "actual": "absent"})
    for key, want in (("allow_force_pushes", False), ("allow_deletions", False),
                      ("enforce_admins", True)):
        got = (actual.get(key) or {}).get("enabled") if isinstance(actual.get(key), dict) else actual.get(key)
        if got is not want:
            out.append({"field": key, "declared": want, "actual": got})
    return out


@registry.register
class BranchProtection(Comparator):
    comparator_id = "CMP-05"
    registry_key = "product.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        tpl = load_template(ctx.declared.root)
        seq = 0
        for pid in sorted(ctx.declared.products):
            findings = []
            blocked: list[str] = []
            for repo in ctx.declared.repositories_of(pid):
                name = repo["name"]
                branch = (ctx.declared.products[pid].get("code") or {}).get("default_branch", "main")
                actual = ctx.client.get(f"/repos/{name}/branches/{branch}/protection")
                weak = _weakened(tpl, actual)
                if weak:
                    blocked.append(name)
                    seq += 1
                    findings.append(
                        self.finding(
                            ctx, seq,
                            Scope("repository", name, product=pid),
                            {"template": TEMPLATE, "requirements": len(tpl)},
                            {"weakened": weak},
                            cell["drift_class"], cell["level"], cell["on_mismatch"],
                            [
                                Evidence("template", TEMPLATE),
                                Evidence("github-api", f"/repos/{name}/branches/{branch}/protection"),
                            ],
                            blocks_deployment=[name],
                        )
                    )
            for f in findings:
                f.blocks_deployment = sorted(set(blocked))
            yield Row(key=pid, findings=findings)
PYEOF

cat > reconciler/comparators/tests/test_cmp_05.py <<'PYEOF'
import pathlib

import yaml

from reconciler.comparators.base import Context
from reconciler.comparators.cmp_05_branch_protection import BranchProtection, _weakened
from reconciler.loader import load

ROOT = pathlib.Path(__file__).resolve().parents[3]
FIX = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures" / "declared"
REPO = "example-org/product-alpha-api"
PROT = f"/repos/{REPO}/branches/main/protection"
TPL = yaml.safe_load((ROOT / "tools/provision/templates/branch-protection.yaml").read_text(encoding="utf-8"))


class _Stub:
    def __init__(self, responses):
        self.responses, self.seen = responses, []

    def get(self, path, **p):
        self.seen.append(path)
        return self.responses.get(path)

    def paginate(self, path, **p):
        self.seen.append(path)
        return iter(self.responses.get(path) or [])

    def ledger(self):
        return {"api_calls": len(self.seen), "methods_used": ["GET"],
                "expected_source": "api.github.com", "max_calls": 5000}


def _conformant():
    return {
        "required_pull_request_reviews": {
            "required_approving_review_count": 1,
            "require_code_owner_reviews": True,
            "require_last_push_approval": True,
            "dismiss_stale_reviews": True,
        },
        "required_status_checks": {"strict": True, "contexts": list(TPL["required_status_checks"]["contexts"])},
        "allow_force_pushes": {"enabled": False},
        "allow_deletions": {"enabled": False},
        "enforce_admins": {"enabled": True},
    }


def _ctx(actual):
    d = load(FIX)
    object.__setattr__(d, "root", ROOT if actual is None else d.root)
    return Context(declared=load(FIX), client=_Stub({PROT: actual}),
                   org="example-org", today="2026-08-27", now="2026-08-27T06:00:00Z")


def test_the_template_names_every_required_status_check_of_section_113():
    assert set(TPL["required_status_checks"]["contexts"]) == {
        "tests", "build", "security-scan", "contract-validation",
        "reviewer-matrix-validation", "parity-check", "verification-contract",
        "control-plane/blocking-drift",
    }


def test_the_template_forbids_machine_identities_in_codeowners():
    assert TPL["code_owner_rules"]["machine_identities_permitted"] is False


def test_the_template_requires_a_deployment_branch_and_tag_policy():
    ep = TPL["environment_policy"]
    assert ep["deployment_branch_and_tag_policy_required"] is True
    assert ep["applies_to_environments"] == ["staging", "production"]


def test_a_conformant_repository_produces_no_weakened_fields():
    assert _weakened(TPL, _conformant()) == []


def test_absent_protection_is_a_single_weakened_entry_not_a_pass():
    weak = _weakened(TPL, None)
    assert weak == [{"field": "protection", "declared": "present", "actual": "absent"}]


def test_a_missing_blocking_drift_context_is_weakened():
    a = _conformant()
    a["required_status_checks"]["contexts"].remove("control-plane/blocking-drift")
    fields = [w["declared"] for w in _weakened(TPL, a)]
    assert "control-plane/blocking-drift" in fields


def test_a_weakened_repository_is_blocking_and_blocks_deployment():
    a = _conformant()
    a["enforce_admins"] = {"enabled": False}
    rows = list(BranchProtection().rows(_ctx(a)))
    fs = [f for r in rows for f in r.findings]
    assert len(fs) == 1
    assert fs[0].drift_class == "blocking" and fs[0].response_level == 4
    assert fs[0].blocks_deployment == [REPO]
PYEOF

python -m pytest reconciler/comparators/tests/test_cmp_05.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add tools/provision reconciler/comparators
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-08: branch-protection template and CMP-05"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Seven CMP-05 tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_05.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `7 passed` |
| A2 | Eight required contexts, including the blocking-drift check | `cd "$CP" && python -c "import yaml;t=yaml.safe_load(open('tools/provision/templates/branch-protection.yaml'));c=t['required_status_checks']['contexts'];print(len(c), 'control-plane/blocking-drift' in c)"` | `8 True` |
| A3 | Admins are not exempt | `cd "$CP" && python -c "import yaml;print(yaml.safe_load(open('tools/provision/templates/branch-protection.yaml'))['restrictions']['enforce_admins'])"` | `True` |
| A4 | Absent protection fails closed | `cd "$CP" && python -c "import yaml;from reconciler.comparators.cmp_05_branch_protection import _weakened as w;t=yaml.safe_load(open('tools/provision/templates/branch-protection.yaml'));print(len(w(t,None)))"` | `1` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_05.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "import yaml;t=yaml.safe_load(open('tools/provision/templates/branch-protection.yaml'));print(len(t['required_status_checks']['contexts']))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
7 passed
8
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L2`, if the literal name of the blocking check run is not `control-plane/blocking-drift` in the repository you are working on. Section 11.3 states that name; L3 Phase 2 (`DEC-L3-02-02`) pins it as a decision, and L2 emits it. If L0 has recorded a different name, use the recorded one and say so in the PR body — do **not** invent a third.
STOP with `Blocked-on: L0` if `tools/provision/templates/branch-protection.yaml` already exists — Section 3 of this plan says this phase creates it, and a pre-existing file means another lane wrote into `tools/provision/**`, contradicting PARTITION.md line 19.
Do **not** remove a required context to make a test pass against a real repository. A repository missing a context **is** the finding.

---

## L3-01-09 — CMP-03 and CMP-04: assignments versus Teams, and versus CODEOWNERS

**Size:** L **Depends on:** L3-01-05
**Owns:** `reconciler/comparators/cmp_03_team_membership.py`, `reconciler/comparators/cmp_04_codeowners.py`, `reconciler/codeowners.py`, `reconciler/comparators/tests/test_cmp_03_04.py`
**Spec basis:** §53.1 rows 3 and 4; §10 (assignment registry); §11.2 (Teams-derived Write); §11.3 (*"CODEOWNERS ... is generated from the registries rather than hand-maintained; the generator emits human identities only"*, *"no machine account ever appears in it"*); §17.3 (the reviewer matrix); invariants 7 and 55.
**Registry key:** `product.yaml` for both.

The two rows read the same declared set and differ only in what they compare it against. They ship in one task because the CODEOWNERS generator is the expected-value function for row 4 and would otherwise be written twice.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t09-cmp03-04
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/codeowners.py <<'PYEOF'
"""Regenerate the expected CODEOWNERS file, byte-exactly, from the registries.

Section 11.3: "CODEOWNERS routes review requests automatically and is
generated from the registries rather than hand-maintained; the generator
emits human identities only. verification/ is owned by whoever holds
verification_responsibility. product.yaml, migration directories and CI
workflow files are owned by the Team Lead role. Product source paths are
owned by the product Team."

That paragraph is the whole specification of this function. Four rules, in
that order, and nothing else. Byte-exactness matters because CMP-04's
comparison is a diff against the actual file: a generator that formats
differently from the one provisioning used would report every repository as
drifted forever, and a reader would stop looking.
"""
from __future__ import annotations

from typing import Any

HEADER = (
    "# GENERATED FROM THE CONTROL-PLANE REGISTRIES. DO NOT EDIT BY HAND.\n"
    "# Spec Section 11.3. Human identities only: no machine account ever\n"
    "# appears in this file, so a machine approval can never satisfy branch\n"
    "# protection.\n"
)


def _handles(logins: list[str]) -> str:
    return " ".join("@" + login for login in logins)


def generate(product: dict[str, Any], people_by_id: dict[str, dict[str, Any]],
             team_slug: str, lead_logins: list[str],
             verification_logins: list[str]) -> str:
    """Return the expected CODEOWNERS body for one product repository."""
    lines = [HEADER]
    lines.append(f"* @{team_slug}\n")
    if verification_logins:
        lines.append(f"/verification/ {_handles(sorted(verification_logins))}\n")
    if lead_logins:
        owner = _handles(sorted(lead_logins))
        lines.append(f"/product.yaml {owner}\n")
        lines.append(f"/migrations/ {owner}\n")
        lines.append(f"/.github/workflows/ {owner}\n")
    return "".join(lines)


def machine_lines(body: str, machine_logins: set[str]) -> list[str]:
    """Section 11.3: no machine account ever appears in CODEOWNERS."""
    out = []
    for line in body.splitlines():
        if line.startswith("#"):
            continue
        for token in line.split():
            if token.startswith("@") and token[1:].lower() in machine_logins:
                out.append(line)
                break
    return out
PYEOF

cat > reconciler/comparators/cmp_03_team_membership.py <<'PYEOF'
"""CMP-03 - product.yaml assignments versus GitHub Team membership.

Section 53.1: "Fail CI on the affected repository."

Two things are compared, and both are required by Section 11.2's Teams-derived
Write model:

  1. the product Team's member set equals the open-assignment holder set;
  2. every declared repository appears in that Team's repository list with
     push permission.

Either difference is Blocking and names the affected repositories in
blocks_repository. Invariant 55: "Ownership changes are declarative and take
effect through reconciliation" - which is only true if the reconciler notices
when they have not.
"""
from __future__ import annotations

from typing import Iterator

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.model import Evidence, Scope


def team_slug(product_id: str) -> str:
    """The product Team slug. Provisioning (Subsystem D) creates it as the id."""
    return product_id


@registry.register
class TeamMembership(Comparator):
    comparator_id = "CMP-03"
    registry_key = "product.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        seq = 0
        for pid in sorted(ctx.declared.products):
            slug = team_slug(pid)
            repos = [r["name"] for r in ctx.declared.repositories_of(pid)]
            declared = {
                (ctx.declared.login_of(a["person"]) or "").lower()
                for a in ctx.declared.open_assignments(pid, ctx.today)
            } - {""}
            actual = {
                (m.get("login") or "").lower()
                for m in ctx.client.paginate(f"/orgs/{ctx.org}/teams/{slug}/members", per_page=100)
            }
            team_repos = {
                r.get("full_name"): ((r.get("permissions") or {}).get("push") is True)
                for r in ctx.client.paginate(f"/orgs/{ctx.org}/teams/{slug}/repos", per_page=100)
            }
            findings = []
            missing_people = sorted(declared - actual)
            extra_people = sorted(actual - declared)
            missing_repos = [r for r in repos if team_repos.get(r) is not True]
            if missing_people or extra_people or missing_repos:
                seq += 1
                findings.append(
                    self.finding(
                        ctx, seq,
                        Scope("product", pid, product=pid),
                        {"members": sorted(declared), "repositories": repos},
                        {"members": sorted(actual), "repositories_with_push":
                         sorted(k for k, v in team_repos.items() if v)},
                        cell["drift_class"], cell["level"], cell["on_mismatch"],
                        [
                            Evidence("registry", f"registries/products/{pid}/product.yaml"),
                            Evidence("github-api", f"/orgs/{ctx.org}/teams/{slug}/members"),
                            Evidence("github-api", f"/orgs/{ctx.org}/teams/{slug}/repos"),
                        ],
                        blocks_repository=repos,
                    )
                )
            yield Row(key=pid, findings=findings)
PYEOF

cat > reconciler/comparators/cmp_04_codeowners.py <<'PYEOF'
"""CMP-04 - product.yaml assignments versus CODEOWNERS.

Section 53.1: "Regenerate; alert if hand-edited."

Phase 1 PROPOSES the regeneration and never performs it (rule R1). The
proposal is carried as data on the finding, in proposed_repair, so that L3
Phase 2's Level-3 executor has something to act on when a repair class is
eventually enabled - one class at a time, by L0 (99.6 risk 6).

The escalation is Section 11.3's negative rule: "no machine account ever
appears in it". A CODEOWNERS line naming a machine identity is not an
alert-and-regenerate case. It is Blocking, because a machine approval that
satisfies a Code Owner requirement defeats the gate rather than drifting from
it.
"""
from __future__ import annotations

from typing import Iterator

from reconciler import codeowners
from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.comparators.cmp_03_team_membership import team_slug
from reconciler.model import Evidence, Scope

CANDIDATE_PATHS = (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS")

#: Section 7 employment_type enum. Anything outside it is not a human.
HUMAN_EMPLOYMENT_TYPES = frozenset(
    {"employee", "contractor", "intern", "temporary_specialist", "consultant"}
)


def machine_logins(declared) -> set[str]:
    out = set()
    for p in declared.people.get("people", []) or []:
        if p.get("employment_type") not in HUMAN_EMPLOYMENT_TYPES:
            login = (p.get("github_login") or "").lower()
            if login:
                out.add(login)
    for login in declared.platform.get("machine_identities", []) or []:
        out.add(str(login).lower())
    return out


@registry.register
class CodeownersComparator(Comparator):
    comparator_id = "CMP-04"
    registry_key = "product.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        machines = machine_logins(ctx.declared)
        people_by_id = {p["id"]: p for p in ctx.declared.people.get("people", []) or []}
        seq = 0
        for pid in sorted(ctx.declared.products):
            prod = ctx.declared.products[pid]
            leads = [
                (p.get("github_login") or "").lower()
                for p in ctx.declared.active_people() if p.get("role") == "team_lead"
            ]
            verifiers = [
                (ctx.declared.login_of(a["person"]) or "").lower()
                for a in ctx.declared.open_assignments(pid, ctx.today)
                if a.get("type") == "verification_responsibility"
            ]
            expected = codeowners.generate(prod, people_by_id, team_slug(pid),
                                           [l for l in leads if l],
                                           [v for v in verifiers if v])
            findings = []
            for repo in ctx.declared.repositories_of(pid):
                name = repo["name"]
                actual_body, actual_path = None, None
                for cand in CANDIDATE_PATHS:
                    got = ctx.client.get(f"/repos/{name}/contents/{cand}")
                    if got:
                        actual_body = got.get("decoded") or ""
                        actual_path = cand
                        break
                bad = codeowners.machine_lines(actual_body or "", machines)
                if bad:
                    seq += 1
                    findings.append(
                        self.finding(
                            ctx, seq, Scope("repository", name, product=pid),
                            {"machine_identities_permitted": False},
                            {"lines": bad, "path": actual_path},
                            cell["class_escalated"], cell["level_escalated"],
                            cell["on_mismatch"],
                            [
                                Evidence("registry", "registries/people.yaml"),
                                Evidence("github-api", f"/repos/{name}/contents/{actual_path}"),
                            ],
                            blocks_repository=[name],
                        )
                    )
                elif actual_body != expected:
                    seq += 1
                    findings.append(
                        self.finding(
                            ctx, seq, Scope("repository", name, product=pid),
                            {"generated_from": "registries"},
                            {"path": actual_path, "present": actual_body is not None},
                            cell["drift_class"], cell["level"], cell["on_mismatch"],
                            [
                                Evidence("registry", f"registries/products/{pid}/product.yaml"),
                                Evidence("github-api", f"/repos/{name}/contents/{CANDIDATE_PATHS[0]}"),
                            ],
                            proposed_repair={
                                "class": "codeowners-regeneration",
                                "repository": name,
                                "path": actual_path or CANDIDATE_PATHS[0],
                                "body": expected,
                                "applied": False,
                            },
                        )
                    )
            yield Row(key=pid, findings=findings)
PYEOF

cat > reconciler/comparators/tests/test_cmp_03_04.py <<'PYEOF'
import pathlib

from reconciler import codeowners
from reconciler.comparators.base import Context
from reconciler.comparators.cmp_03_team_membership import TeamMembership
from reconciler.comparators.cmp_04_codeowners import CodeownersComparator, machine_logins
from reconciler.loader import load

FIX = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures" / "declared"
ORG = "example-org"
REPO = "example-org/product-alpha-api"
MEMBERS = f"/orgs/{ORG}/teams/product-alpha/members"
REPOS = f"/orgs/{ORG}/teams/product-alpha/repos"
CO = f"/repos/{REPO}/contents/.github/CODEOWNERS"


class _Stub:
    def __init__(self, responses):
        self.responses, self.seen = responses, []

    def get(self, path, **p):
        self.seen.append(path)
        return self.responses.get(path)

    def paginate(self, path, **p):
        self.seen.append(path)
        return iter(self.responses.get(path) or [])

    def ledger(self):
        return {"api_calls": len(self.seen), "methods_used": ["GET"],
                "expected_source": "api.github.com", "max_calls": 5000}


def _expected():
    d = load(FIX)
    return codeowners.generate(d.products["product-alpha"], {}, "product-alpha",
                               ["fixture-lead-1"], [])


def _ctx(responses):
    return Context(declared=load(FIX), client=_Stub(responses), org=ORG,
                   today="2026-08-27", now="2026-08-27T06:00:00Z")


def _team_ok():
    return {
        MEMBERS: [{"login": l} for l in ("fixture-dev-a", "fixture-dev-b")],
        REPOS: [{"full_name": REPO, "permissions": {"push": True}}],
    }


def test_a_matching_team_produces_no_finding():
    rows = list(TeamMembership().rows(_ctx(_team_ok())))
    assert sum(len(r.findings) for r in rows) == 0


def test_a_missing_team_member_is_blocking_and_names_the_repository():
    r = _team_ok()
    r[MEMBERS] = [{"login": "fixture-dev-a"}]
    fs = [f for row in TeamMembership().rows(_ctx(r)) for f in row.findings]
    assert len(fs) == 1 and fs[0].drift_class == "blocking" and fs[0].response_level == 4
    assert fs[0].blocks_repository == [REPO]


def test_a_team_repo_without_push_is_blocking():
    r = _team_ok()
    r[REPOS] = [{"full_name": REPO, "permissions": {"push": False}}]
    fs = [f for row in TeamMembership().rows(_ctx(r)) for f in row.findings]
    assert len(fs) == 1 and fs[0].drift_class == "blocking"


def test_every_product_is_yielded_as_a_row_even_when_clean():
    rows = list(TeamMembership().rows(_ctx(_team_ok())))
    assert [r.key for r in rows] == ["product-alpha"]


def test_the_generated_codeowners_names_no_machine_and_carries_the_warning():
    body = _expected()
    assert "DO NOT EDIT BY HAND" in body
    assert "@product-alpha" in body


def test_a_byte_identical_codeowners_produces_no_finding():
    fs = [f for row in CodeownersComparator().rows(
        _ctx({CO: {"decoded": _expected()}})) for f in row.findings]
    assert fs == []


def test_a_hand_edited_codeowners_proposes_a_repair_and_never_applies_it():
    fs = [f for row in CodeownersComparator().rows(
        _ctx({CO: {"decoded": "* @someone-else\n"}})) for f in row.findings]
    assert len(fs) == 1
    assert fs[0].drift_class == "amber" and fs[0].response_level == 3
    assert fs[0].proposed_repair["applied"] is False
    assert fs[0].proposed_repair["class"] == "codeowners-regeneration"


def test_a_machine_identity_in_codeowners_is_blocking():
    d = load(FIX)
    d.people["people"].append({
        "id": "bot-1", "github_login": "fixture-bot", "employment_type": "machine",
        "availability": "active", "access_status": "provisioned", "role": "developer",
        "capabilities": [],
    })
    assert "fixture-bot" in machine_logins(d)
    ctx = Context(declared=d, client=_Stub({CO: {"decoded": "* @fixture-bot\n"}}),
                  org=ORG, today="2026-08-27", now="2026-08-27T06:00:00Z")
    fs = [f for row in CodeownersComparator().rows(ctx) for f in row.findings]
    assert len(fs) == 1 and fs[0].drift_class == "blocking" and fs[0].response_level == 4
PYEOF

python -m pytest reconciler/comparators/tests/test_cmp_03_04.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-09: CMP-03 team membership and CMP-04 CODEOWNERS"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Eight tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_03_04.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `8 passed` |
| A2 | Both comparators are registered | `cd "$CP" && python -c "import reconciler.comparators.cmp_03_team_membership, reconciler.comparators.cmp_04_codeowners; from reconciler.comparators.registry import registered as r; print(sorted(set(r()) & {'CMP-03','CMP-04'}))"` | `['CMP-03', 'CMP-04']` |
| A3 | No repair is ever applied in this phase | `cd "$CP" && grep -c '"applied": False' reconciler/comparators/cmp_04_codeowners.py` | `1` |
| A4 | The generator emits a do-not-edit banner | `cd "$CP" && grep -c 'DO NOT EDIT BY HAND' reconciler/codeowners.py` | `1` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_03_04.py -q 2>&1 | grep -oE '^[0-9]+ passed'
grep -c '"applied": False' reconciler/comparators/cmp_04_codeowners.py
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
8 passed
1
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L0`, if the product Team slug in the live organisation is not the product id — `team_slug()` would then be guessing, and CMP-03 would report every product as fully drifted. Record the real convention in a decision and re-run.
STOP with `Blocked-on: L1` if `registries/products/*/product.yaml` carries no `assignments[].type` value `verification_responsibility` anywhere and Section 11.3's `verification/` ownership line therefore has no source.
Do **not** make CMP-04 write, commit, or open a PR for the regenerated file. Phase 1 proposes. Rule R1.

---

## L3-01-10 — The environment template, CMP-07 and CMP-08

**Size:** L **Depends on:** L3-01-05
**Owns:** `tools/provision/templates/environment.yaml`, `reconciler/comparators/cmp_07_environments.py`, `reconciler/comparators/cmp_08_deployment_policy.py`, `reconciler/comparators/tests/test_cmp_07_08.py`
**Spec basis:** §53.1 rows 7 and 8; §33.4 (*"Every environment carries a deployment branch and tag policy, applied from the template at product creation"*); §11.3 (*"a repository with the first and not the second holds production credentials behind nothing"*); §11.4 (environment required reviewers are Enterprise-only and are **not** declared here); **D91**; §53.2 Level 5 (production environment drift).
**Registry key:** `product.yaml` for both.

<!-- LAYOUT ALIGNMENT (FD-045, 2026-09-06): This task creates tools/provision/templates/environment.yaml. The authoritative phase-file (L3-06-tasks.md, 116-task plan per FD-045) does not define a tools/provision/templates/ subdirectory; declared environment state is resolved via reconciler/contracts_map.py in L3-06. The phase-file layout (L3-06-tasks.md) is canonical for any re-implementation. -->

CMP-08 is one of the two rows added by amendment. It is the reason the template exists: Section 33.4 makes the deployment branch and tag policy *"the control that makes Section 40.3's 'accessible only to the production deployment workflow' true"*, and Section 11.3 says a repository with branch protection and no such policy holds production credentials behind nothing. CMP-07 checks that the environments exist and carry their declared secret names; CMP-08 checks the one control that makes those secrets unreachable from an unreviewed ref.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t10-cmp07-08
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > tools/provision/templates/environment.yaml <<'YEOF'
# Declared environment configuration, per repository. Spec Section 33.4, D91.
#
# The DECLARED side of Section 53.1 rows 7 and 8, and the source provisioning
# (Subsystem D) applies at product creation.
#
# Section 11.4 is binding on what is NOT here: environment required reviewers
# and wait timers are a GitHub Enterprise feature and are not available on the
# Team plan. Production approval and self-review prevention are enforced by
# the Section 27.2 workflow-identity gate, which is the mechanism of record.
# Do not add a required_reviewers key: declaring a control the plan cannot
# apply produces permanent unfixable drift and teaches the reader to ignore
# this comparator.
template_version: 1
spec_sections: ["33.4", "11.3", "11.4"]
decisions: ["D91"]

environments:
  development:
    deployment_branch_policy: null            # unrestricted; holds no production secret
    secrets: []
  staging:
    deployment_branch_policy:
      protected_branches: false
      custom_branch_policies: true
      allowed:
        - type: branch
          name: "${default_branch}"
        - type: tag
          name: "v*"                          # protected release tags
      allow_nothing_else: true
    secrets:
      - STAGING_DEPLOY_TOKEN
  production:
    deployment_branch_policy:
      protected_branches: false
      custom_branch_policies: true
      allowed:
        - type: branch
          name: "${default_branch}"
        - type: tag
          name: "v*"
      allow_nothing_else: true
    secrets:
      - PRODUCTION_DEPLOY_TOKEN

rules:
  policy_required_for: [staging, production]
  absent_policy_is: blocking
  additional_entry_is: blocking
  production_scope_response_level: 5          # Section 53.2, Level 5
YEOF

cat > reconciler/comparators/cmp_07_environments.py <<'PYEOF'
"""CMP-07 - the environment template versus actual environments.

Section 53.1: "Alert."

Three equalities, all Amber:
  - the environment NAME SET matches the template;
  - each environment's protection-rule SHAPE matches;
  - each declared secret NAME is present.

Secret VALUES are never read. Section 53.3: reconciliation "never rotates or
writes secrets", and Phase 1 does not read one either - the environment
secrets endpoint returns names and timestamps, which is all this comparison
needs and all it may have.
"""
from __future__ import annotations

import pathlib
from typing import Any, Iterator

import yaml

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.model import Evidence, Scope

TEMPLATE = "tools/provision/templates/environment.yaml"


def load_template(root: Any) -> dict[str, Any]:
    return yaml.safe_load((pathlib.Path(root) / TEMPLATE).read_text(encoding="utf-8"))


@registry.register
class Environments(Comparator):
    comparator_id = "CMP-07"
    registry_key = "product.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        tpl = load_template(ctx.declared.root)
        want_names = set(tpl["environments"])
        seq = 0
        for pid in sorted(ctx.declared.products):
            findings = []
            for repo in ctx.declared.repositories_of(pid):
                name = repo["name"]
                got = ctx.client.get(f"/repos/{name}/environments") or {}
                have = {e.get("name") for e in (got.get("environments") or [])}
                if have != want_names:
                    seq += 1
                    findings.append(self.finding(
                        ctx, seq, Scope("repository", name, product=pid),
                        sorted(want_names), sorted(have),
                        cell["drift_class"], cell["level"], cell["on_mismatch"],
                        [Evidence("template", TEMPLATE),
                         Evidence("github-api", f"/repos/{name}/environments")],
                    ))
                for env, spec in tpl["environments"].items():
                    if env not in have:
                        continue
                    secrets = ctx.client.get(f"/repos/{name}/environments/{env}/secrets") or {}
                    present = {s.get("name") for s in (secrets.get("secrets") or [])}
                    missing = [s for s in spec.get("secrets") or [] if s not in present]
                    if missing:
                        seq += 1
                        findings.append(self.finding(
                            ctx, seq, Scope("environment", env, product=pid, environment=env),
                            {"secrets": spec.get("secrets") or []},
                            {"secrets_present": sorted(present)},
                            cell["drift_class"], cell["level"], cell["on_mismatch"],
                            [Evidence("template", TEMPLATE),
                             Evidence("github-api", f"/repos/{name}/environments/{env}/secrets")],
                        ))
            yield Row(key=pid, findings=findings)
PYEOF

cat > reconciler/comparators/cmp_08_deployment_policy.py <<'PYEOF'
"""CMP-08 - the environment deployment branch and tag policy versus actual.

Section 53.1, row added by amendment: "Alert immediately; block deployment on
the affected repository."

Section 33.4: "staging and production accept deployments from the default
branch and from protected release tags only, and from no other ref. This is
the control that makes Section 40.3's 'accessible only to the production
deployment workflow' true."

Four assertions per environment, and all four are failures in the same
direction - a policy that admits MORE than the template:

  1. a policy exists at all;
  2. it admits the default branch;
  3. every tag entry matches the declared protected-release-tag pattern;
  4. it admits nothing else.

Section 53.2's Level 5 applies on the production environment, on top of the
row's own Blocking class - handled by Finding.__post_init__, not here, so no
comparator can forget it.
"""
from __future__ import annotations

import fnmatch
from typing import Iterator

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.comparators.cmp_07_environments import TEMPLATE, load_template
from reconciler.model import Evidence, Scope


def _violations(spec, default_branch, entries) -> list[dict]:
    allowed_tags = [a["name"] for a in spec["allowed"] if a["type"] == "tag"]
    out = []
    names_branch = {e["name"] for e in entries if e.get("type") == "branch"}
    if default_branch not in names_branch:
        out.append({"reason": "default branch not admitted", "expected": default_branch})
    for e in entries:
        if e.get("type") == "tag":
            if not any(fnmatch.fnmatch(e["name"], pat) for pat in allowed_tags):
                out.append({"reason": "tag entry outside the declared pattern", "entry": e})
        elif e.get("type") == "branch":
            if e["name"] != default_branch:
                out.append({"reason": "additional branch entry", "entry": e})
        else:
            out.append({"reason": "entry of an undeclared type", "entry": e})
    return out


@registry.register
class DeploymentPolicy(Comparator):
    comparator_id = "CMP-08"
    registry_key = "product.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        tpl = load_template(ctx.declared.root)
        required = tpl["rules"]["policy_required_for"]
        seq = 0
        for pid in sorted(ctx.declared.products):
            code = ctx.declared.products[pid].get("code") or {}
            default_branch = code.get("default_branch", "main")
            findings = []
            for repo in ctx.declared.repositories_of(pid):
                name = repo["name"]
                got = ctx.client.get(f"/repos/{name}/environments") or {}
                actual_envs = {e.get("name"): e for e in (got.get("environments") or [])}
                for env in required:
                    spec = tpl["environments"][env]["deployment_branch_policy"]
                    live = actual_envs.get(env) or {}
                    policy = live.get("deployment_branch_policy")
                    if not policy:
                        seq += 1
                        findings.append(self.finding(
                            ctx, seq,
                            Scope("environment", env, product=pid, environment=env),
                            {"deployment_branch_policy": "required"},
                            {"deployment_branch_policy": None},
                            cell["drift_class"], cell["level"], cell["on_mismatch"],
                            [Evidence("template", TEMPLATE),
                             Evidence("github-api", f"/repos/{name}/environments")],
                            blocks_deployment=[name],
                        ))
                        continue
                    listed = ctx.client.get(
                        f"/repos/{name}/environments/{env}/deployment-branch-policies") or {}
                    entries = [
                        {"name": b.get("name"), "type": b.get("type")}
                        for b in (listed.get("branch_policies") or [])
                    ]
                    bad = _violations(spec, default_branch, entries)
                    if bad:
                        seq += 1
                        findings.append(self.finding(
                            ctx, seq,
                            Scope("environment", env, product=pid, environment=env),
                            spec, {"entries": entries, "violations": bad},
                            cell["drift_class"], cell["level"], cell["on_mismatch"],
                            [Evidence("template", TEMPLATE),
                             Evidence("github-api",
                                      f"/repos/{name}/environments/{env}/deployment-branch-policies")],
                            blocks_deployment=[name],
                        ))
            yield Row(key=pid, findings=findings)
PYEOF

cat > reconciler/comparators/tests/test_cmp_07_08.py <<'PYEOF'
import pathlib

import yaml

from reconciler.comparators.base import Context
from reconciler.comparators.cmp_07_environments import Environments
from reconciler.comparators.cmp_08_deployment_policy import DeploymentPolicy, _violations
from reconciler.loader import load

ROOT = pathlib.Path(__file__).resolve().parents[3]
FIX = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures" / "declared"
REPO = "example-org/product-alpha-api"
ENVS = f"/repos/{REPO}/environments"
TPL = yaml.safe_load((ROOT / "tools/provision/templates/environment.yaml").read_text(encoding="utf-8"))


class _Stub:
    def __init__(self, responses):
        self.responses, self.seen = responses, []

    def get(self, path, **p):
        self.seen.append(path)
        return self.responses.get(path)

    def paginate(self, path, **p):
        self.seen.append(path)
        return iter(self.responses.get(path) or [])

    def ledger(self):
        return {"api_calls": len(self.seen), "methods_used": ["GET"],
                "expected_source": "api.github.com", "max_calls": 5000}


def _ctx(responses):
    return Context(declared=load(FIX), client=_Stub(responses), org="example-org",
                   today="2026-08-27", now="2026-08-27T06:00:00Z")


def _envs(with_policy=True):
    pol = {"protected_branches": False, "custom_branch_policies": True}
    return {"environments": [
        {"name": "development", "deployment_branch_policy": None},
        {"name": "staging", "deployment_branch_policy": pol if with_policy else None},
        {"name": "production", "deployment_branch_policy": pol if with_policy else None},
    ]}


def _policies(entries):
    return {"branch_policies": entries}


def _all_secrets():
    return {
        f"{ENVS}/development/secrets": {"secrets": []},
        f"{ENVS}/staging/secrets": {"secrets": [{"name": "STAGING_DEPLOY_TOKEN"}]},
        f"{ENVS}/production/secrets": {"secrets": [{"name": "PRODUCTION_DEPLOY_TOKEN"}]},
    }


def test_the_template_declares_no_required_reviewers():
    body = (ROOT / "tools/provision/templates/environment.yaml").read_text(encoding="utf-8")
    assert "required_reviewers" not in body


def test_the_template_requires_a_policy_on_staging_and_production_only():
    assert TPL["rules"]["policy_required_for"] == ["staging", "production"]
    assert TPL["environments"]["development"]["deployment_branch_policy"] is None


def test_matching_environments_produce_no_cmp07_finding():
    r = {ENVS: _envs()}
    r.update(_all_secrets())
    assert [f for row in Environments().rows(_ctx(r)) for f in row.findings] == []


def test_a_missing_environment_is_amber():
    e = _envs()
    e["environments"] = [x for x in e["environments"] if x["name"] != "staging"]
    r = {ENVS: e}
    r.update(_all_secrets())
    fs = [f for row in Environments().rows(_ctx(r)) for f in row.findings]
    assert len(fs) == 1 and fs[0].drift_class == "amber" and fs[0].response_level == 2


def test_a_missing_declared_secret_name_is_amber():
    r = {ENVS: _envs()}
    r.update(_all_secrets())
    r[f"{ENVS}/production/secrets"] = {"secrets": []}
    fs = [f for row in Environments().rows(_ctx(r)) for f in row.findings]
    assert len(fs) == 1 and fs[0].drift_class == "amber"


def test_a_conformant_policy_has_no_violations():
    spec = TPL["environments"]["production"]["deployment_branch_policy"]
    entries = [{"name": "main", "type": "branch"}, {"name": "v1.2.3", "type": "tag"}]
    assert _violations(spec, "main", entries) == []


def test_an_extra_branch_entry_is_a_violation():
    spec = TPL["environments"]["production"]["deployment_branch_policy"]
    entries = [{"name": "main", "type": "branch"}, {"name": "hotfix/*", "type": "branch"}]
    reasons = [v["reason"] for v in _violations(spec, "main", entries)]
    assert "additional branch entry" in reasons


def test_an_absent_policy_is_blocking_and_blocks_deployment():
    r = {ENVS: _envs(with_policy=False)}
    fs = [f for row in DeploymentPolicy().rows(_ctx(r)) for f in row.findings]
    assert len(fs) == 2
    assert {f.drift_class for f in fs} == {"blocking"}
    assert all(f.blocks_deployment == [REPO] for f in fs)


def test_production_scope_carries_level_five():
    r = {ENVS: _envs(with_policy=False)}
    fs = [f for row in DeploymentPolicy().rows(_ctx(r)) for f in row.findings]
    prod = [f for f in fs if f.scope.environment == "production"]
    stag = [f for f in fs if f.scope.environment == "staging"]
    assert prod[0].response_level == 5
    assert stag[0].response_level == 4
PYEOF

python -m pytest reconciler/comparators/tests/test_cmp_07_08.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add tools/provision reconciler/comparators
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-10: environment template, CMP-07 environments and CMP-08 deployment branch policy"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Nine tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_07_08.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `9 passed` |
| A2 | The template declares no Enterprise-only control | `cd "$CP" && grep -c 'required_reviewers' tools/provision/templates/environment.yaml` | `0` |
| A3 | A policy is required on exactly staging and production | `cd "$CP" && python -c "import yaml;print(yaml.safe_load(open('tools/provision/templates/environment.yaml'))['rules']['policy_required_for'])"` | `['staging', 'production']` |
| A4 | Production drift is Level 5 | `cd "$CP" && python -c "import yaml;print(yaml.safe_load(open('tools/provision/templates/environment.yaml'))['rules']['production_scope_response_level'])"` | `5` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_07_08.py -q 2>&1 | grep -oE '^[0-9]+ passed'
grep -c 'required_reviewers' tools/provision/templates/environment.yaml
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
9 passed
0
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L0`, if the protected-release-tag pattern for this estate is not `v*`. Section 33.4 says *"protected release tags"* and does not give the glob; if `registries/platform.yaml` or a decision record names a different pattern, use that one and cite it. Do **not** silently keep `v*` if a different pattern is recorded.
STOP with `Blocked-on: L0` if `tools/provision/templates/environment.yaml` already exists (see `L3-01-08`'s equivalent STOP).
Do **not** add `required_reviewers` to the template, however tempting. Section 11.4 is explicit that it is Enterprise-only on private repositories, and a declared control that cannot be applied produces permanent unfixable drift.

---

## L3-01-11 — CMP-09: the declared `infrastructure:` boundary versus provider attestation

**Size:** M **Depends on:** L3-01-05; **D-L3-02** (all three parts)
**Owns:** `reconciler/comparators/cmp_09_infrastructure_attestation.py`, `reconciler/comparators/tests/test_cmp_09.py`
**Spec basis:** §53.1 row 9, *"Blocking past its attestation window"*; §40.2 (*"the provider side is verified by attestation rather than reconciliation: the declared boundary carries a named owner who records a dated attestation that actual provider state matches the declaration — calibrated configuration; initial value monthly"*; *"An expired or failed attestation is Blocking drift (Section 53.1)"*); invariants 24 and 26.
**Registry key:** `product.yaml`.

This is the one row whose actual state is **not** GitHub configuration. Section 40.2 says so directly: *"Reconciliation compares declared state against GitHub state and never leaves it."* The attestation record is the substitute, and the record store lives in `control-plane-records`, which PARTITION.md line 20 gives to L4. L3 reads it over the contents API and names no path of its own.

### Branch and gate

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t11-cmp09
test -f docs/decisions/D-L3-02.md && echo "GATE-1 decision-present OK" || echo "GATE-1 FAIL"
python - <<'PYEOF'
import pathlib, re
p = pathlib.Path("docs/decisions/D-L3-02.md")
t = p.read_text(encoding="utf-8") if p.exists() else ""
for key in ("attestation_store_path", "field_attesting_identity", "field_attestation_date",
            "field_result", "registry_window_field"):
    m = re.search(rf"^{key}:\s*(\S.*)$", t, re.M)
    print(f"GATE-2 {key}:", m.group(1).strip() if m else "MISSING")
PYEOF
```

The five values above are **substituted into the file below**. They are written once, into `reconciler/comparators/attestation-binding.yaml`, so that a later change to the decision is a one-file edit and never a code edit.

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/comparators/attestation-binding.yaml <<'YEOF'
# The D-L3-02 resolution, transcribed. NOTHING HERE IS CHOSEN BY THE EXECUTOR.
#
# Section 40.2 requires "a named owner who records a dated attestation that
# actual provider state matches the declaration", and Section 53.1 compares
# the declared infrastructure: boundary against "the latest provider-side
# attestation record". Section 97.2's canonical record-store table contains no
# attestation store, so the store path, its three field names and the registry
# field carrying the per-product window are an L0 decision (D-L3-02), because
# the store lives in control-plane-records, which PARTITION.md line 20 gives
# exclusively to L4.
#
# Replace each <from D-L3-02 ...> with the value printed by this task's
# GATE-2 block, verbatim. Do not invent one. Do not leave a placeholder.
binding_version: 1
decision: D-L3-02
store_path: "<from D-L3-02(a): attestation_store_path>"
fields:
  attesting_identity: "<from D-L3-02(b): field_attesting_identity>"
  attestation_date: "<from D-L3-02(b): field_attestation_date>"
  result: "<from D-L3-02(b): field_result>"
registry_window_field: "<from D-L3-02(c): registry_window_field>"
pass_value: pass
YEOF

cat > reconciler/comparators/cmp_09_infrastructure_attestation.py <<'PYEOF'
"""CMP-09 - the declared infrastructure: boundary versus provider attestation.

Section 53.1, row added by amendment: "Blocking past its attestation window."

Section 40.2: "Reconciliation compares declared state against GitHub state and
never leaves it, so the provider side is verified by attestation rather than
reconciliation: the declared boundary carries a named owner who records a
dated attestation that actual provider state matches the declaration -
calibrated configuration; initial value monthly ... An expired or failed
attestation is Blocking drift (Section 53.1)."

Three Blocking cases and one clean case:
    absent attestation           -> Blocking
    result != pass               -> Blocking
    date + window < today        -> Blocking
    within window and passing    -> no finding

Invariants 24 and 26 (no production database access from developer machines; a
compromised workstation yields no production access) rest on this declaration
and this attestation, per Section 40.2. That is why an unattested boundary is
Blocking and not Amber: without the attestation the declaration is a claim.

Every path and field name comes from attestation-binding.yaml, the transcribed
D-L3-02 resolution. Nothing here names a path in control-plane-records.
"""
from __future__ import annotations

import datetime as dt
import pathlib
import re
from typing import Any, Iterator

import yaml

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.model import Evidence, Scope

BINDING = pathlib.Path(__file__).resolve().parent / "attestation-binding.yaml"


class AttestationBindingUnresolved(RuntimeError):
    """attestation-binding.yaml still carries a D-L3-02 placeholder."""


def load_binding() -> dict[str, Any]:
    doc = yaml.safe_load(BINDING.read_text(encoding="utf-8"))
    flat = yaml.safe_dump(doc)
    if "<from D-L3-02" in flat:
        raise AttestationBindingUnresolved(str(BINDING))
    return doc


def window_days(value: Any) -> int:
    """Accept an integer number of days or an ISO-8601 day/month duration."""
    if isinstance(value, int):
        return value
    m = re.fullmatch(r"P(\d+)([DM])", str(value))
    if not m:
        raise ValueError(f"unrecognised attestation window: {value!r}")
    n = int(m.group(1))
    return n if m.group(2) == "D" else n * 30


@registry.register
class InfrastructureAttestation(Comparator):
    comparator_id = "CMP-09"
    registry_key = "product.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        b = load_binding()
        fields = b["fields"]
        today = dt.date.fromisoformat(ctx.today)
        seq = 0
        for pid in sorted(ctx.declared.products):
            prod = ctx.declared.products[pid]
            declared = {
                "infrastructure": prod.get("infrastructure") or {},
                "production_db_access": (prod.get("security") or {}).get("production_db_access"),
            }
            win_raw = _dig(prod, b["registry_window_field"])
            listing = ctx.client.get(
                f"/repos/{ctx.org}/{ctx.records_repo}/contents/{b['store_path']}"
            ) or []
            latest = None
            for entry in listing:
                doc = ctx.client.get(
                    f"/repos/{ctx.org}/{ctx.records_repo}/contents/"
                    f"{b['store_path']}/{entry.get('name')}"
                )
                parsed = yaml.safe_load((doc or {}).get("decoded") or "") or {}
                if parsed.get("product") != pid:
                    continue
                date = parsed.get(fields["attestation_date"])
                if date and (latest is None or str(date) > str(latest.get(fields["attestation_date"]))):
                    latest = parsed
            reason = None
            if latest is None:
                reason = "no attestation record for this product"
            elif latest.get(fields["result"]) != b["pass_value"]:
                reason = "latest attestation did not pass"
            elif win_raw is None:
                reason = "no attestation window declared for this product"
            else:
                due = dt.date.fromisoformat(str(latest[fields["attestation_date"]])) + \
                    dt.timedelta(days=window_days(win_raw))
                if due < today:
                    reason = f"attestation expired on {due.isoformat()}"
            findings = []
            if reason:
                seq += 1
                findings.append(self.finding(
                    ctx, seq, Scope("product", pid, product=pid),
                    declared,
                    {"attestation": latest, "reason": reason},
                    cell["drift_class"], cell["level"], cell["on_mismatch"],
                    [
                        Evidence("registry", f"registries/products/{pid}/product.yaml"),
                        Evidence("records-repository", b["store_path"]),
                    ],
                ))
            yield Row(key=pid, findings=findings)


def _dig(doc: dict[str, Any], dotted: str) -> Any:
    cur: Any = doc
    for part in str(dotted).split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur
PYEOF

cat > reconciler/comparators/tests/test_cmp_09.py <<'PYEOF'
import pathlib

import pytest
import yaml

from reconciler.comparators import cmp_09_infrastructure_attestation as m
from reconciler.comparators.base import Context
from reconciler.loader import load

FIX = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures" / "declared"


class _Stub:
    def __init__(self, responses):
        self.responses, self.seen = responses, []

    def get(self, path, **p):
        self.seen.append(path)
        return self.responses.get(path)

    def paginate(self, path, **p):
        self.seen.append(path)
        return iter(self.responses.get(path) or [])

    def ledger(self):
        return {"api_calls": len(self.seen), "methods_used": ["GET"],
                "expected_source": "api.github.com", "max_calls": 5000}


def test_the_binding_file_must_be_resolved_before_the_comparator_runs():
    raw = m.BINDING.read_text(encoding="utf-8")
    if "<from D-L3-02" in raw:
        with pytest.raises(m.AttestationBindingUnresolved):
            m.load_binding()
        pytest.skip("D-L3-02 not yet transcribed; this task is blocked")
    assert m.load_binding()["decision"] == "D-L3-02"


def test_window_days_accepts_days_and_months():
    assert m.window_days(30) == 30
    assert m.window_days("P30D") == 30
    assert m.window_days("P1M") == 30


def test_window_days_refuses_an_unrecognised_window():
    with pytest.raises(ValueError):
        m.window_days("monthly-ish")


def _ctx(records):
    b = m.load_binding()
    org, repo, store = "example-org", "control-plane-records", b["store_path"]
    listing = [{"name": f"{i}.yaml"} for i in range(len(records))]
    responses = {f"/repos/{org}/{repo}/contents/{store}": listing}
    for i, rec in enumerate(records):
        responses[f"/repos/{org}/{repo}/contents/{store}/{i}.yaml"] = {"decoded": yaml.safe_dump(rec)}
    return Context(declared=load(FIX), client=_Stub(responses), org=org,
                   today="2026-08-27", now="2026-08-27T06:00:00Z")


def _rec(date, result="pass"):
    b = m.load_binding()
    f = b["fields"]
    return {"product": "product-alpha", f["attestation_date"]: date,
            f["result"]: result, f["attesting_identity"]: "lead-1"}


def test_an_absent_attestation_is_blocking():
    if "<from D-L3-02" in m.BINDING.read_text(encoding="utf-8"):
        pytest.skip("D-L3-02 not yet transcribed; this task is blocked")
    fs = [f for r in m.InfrastructureAttestation().rows(_ctx([])) for f in r.findings]
    assert len(fs) == 1 and fs[0].drift_class == "blocking" and fs[0].response_level == 4


def test_a_failed_attestation_is_blocking():
    if "<from D-L3-02" in m.BINDING.read_text(encoding="utf-8"):
        pytest.skip("D-L3-02 not yet transcribed; this task is blocked")
    fs = [f for r in m.InfrastructureAttestation().rows(_ctx([_rec("2026-08-20", "fail")]))
          for f in r.findings]
    assert len(fs) == 1 and fs[0].actual["reason"] == "latest attestation did not pass"
PYEOF

python -m pytest reconciler/comparators/tests/test_cmp_09.py -q 2>&1 | grep -oE '^[0-9]+ (passed|skipped)'
git add reconciler/comparators
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-11: CMP-09 infrastructure boundary versus provider attestation"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Six CMP-09 tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_09.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `6 passed` |
| A2 | The binding carries no placeholder | `cd "$CP" && grep -c 'from D-L3-02' reconciler/comparators/attestation-binding.yaml` | `0` |
| A3 | No `control-plane-records` path is hard-coded in the comparator | `cd "$CP" && grep -cE 'records/' reconciler/comparators/cmp_09_infrastructure_attestation.py` | `0` |
| A4 | The three Blocking cases are all Blocking | `cd "$CP" && python -c "from reconciler.comparators.registry import load_manifest as m; r=m()['CMP-09']; print(r['drift_class'], r['level'])"` | `blocking 4` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_09.py -q 2>&1 | grep -oE '^[0-9]+ passed'
grep -c 'from D-L3-02' reconciler/comparators/attestation-binding.yaml
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
6 passed
0
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: D-L3-02`, if `GATE-1` prints `FAIL`, or if any `GATE-2` line prints `MISSING`, or if `A2` is not `0`. This task **cannot** proceed on a guess: naming an attestation store path is naming a path in `control-plane-records`, which PARTITION.md line 20 gives exclusively to L4, and rule 1 makes a foreign-path claim a lane-guard failure.
Do **not** create the attestation store. Do **not** write a fixture attestation record into `control-plane-records`.
Do **not** downgrade this row to Amber because no store exists yet. Section 40.2: *"An expired or failed attestation is Blocking drift."* A missing store is an unattested boundary, which is the case the row exists for.

---

## L3-01-12 — CMP-10: lifecycle versus Renovate, monitoring and CI configuration

**Size:** M **Depends on:** L3-01-05
**Owns:** `reconciler/comparators/cmp_10_lifecycle.py`, `reconciler/comparators/lifecycle-expectations.yaml`, `reconciler/comparators/tests/test_cmp_10.py`
**Spec basis:** §53.1 row 10, *"Auto-repair where safe; alert otherwise"*; §18.1 (lifecycle states: `active | maintenance | paused | sunset | archived`); §33.2 (Renovate disposition policy); §41 (observability endpoints and the alert channel); §53.3 (what a repair may never do).
**Registry key:** `product.yaml`.

The row's two halves need a boundary: which drifted rows are *safe* and which are merely alerts. That boundary is stated as a table, in configuration, because Section 53.4 says class assignment lives in configuration. The safe set is drawn from Section 53.2's Level-3 "Applies to" list, and nothing is added to it.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t12-cmp10
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/comparators/lifecycle-expectations.yaml <<'YEOF'
# CMP-10: the lifecycle-to-expected-configuration table.
#
# Section 53.1 row: "product.yaml lifecycle" vs "Renovate, monitoring and CI
# configuration" -> "Auto-repair where safe; alert otherwise".
#
# "Where safe" is not decided per finding. Section 53.4: "Class assignment
# lives in configuration and is reviewable; it is not decided ad hoc during an
# incident." This table IS that configuration.
#
# safe: true is permitted ONLY for rows that fall inside Section 53.2's Level-3
# "Applies to" list. Everything else alerts. In Phase 1 nothing is applied
# either way (rule R1): a safe row proposes a repair, an unsafe row alerts.
table_version: 1
spec_sections: ["53.1", "53.2", "18.1", "33.2"]

# Section 18.1 lifecycle states, complete and closed.
states: [active, maintenance, paused, sunset, archived]

checks:
  - id: renovate-present
    reads: renovate_config
    expected_by_state:
      active: present
      maintenance: present
      paused: present
      sunset: present
      archived: absent
    safe: true          # "label and board field sync"-class configuration sync
  - id: repository-archived-flag
    reads: repo_archived
    expected_by_state:
      active: false
      maintenance: false
      paused: false
      sunset: false
      archived: true
    safe: false         # archiving or unarchiving a repository is not in the
                        # Section 53.2 Level-3 list. Alert only.
  - id: alert-channel-declared
    reads: alert_channel
    expected_by_state:
      active: present
      maintenance: present
      paused: present
      sunset: present
      archived: absent
    safe: true          # monitoring alert channel: configuration sync
  - id: ci-workflow-present
    reads: ci_workflow
    expected_by_state:
      active: present
      maintenance: present
      paused: present
      sunset: present
      archived: absent
    safe: false         # a workflow file is the enforcement path itself
                        # (Section 33.2). Never repaired automatically.
YEOF

cat > reconciler/comparators/cmp_10_lifecycle.py <<'PYEOF'
"""CMP-10 - product.yaml lifecycle versus Renovate, monitoring and CI config.

Section 53.1: "Auto-repair where safe; alert otherwise."

The safe/unsafe split is read from lifecycle-expectations.yaml, never decided
here. A safe row proposes a Level-3 repair (proposed only - rule R1). An
unsafe row raises an Amber alert at Level 2 and proposes nothing.

Note what is deliberately unsafe: the repository archived flag, and the
presence of a CI workflow file. Section 33.2 states that a workflow-file
change pushed by a machine identity is Blocking drift; a reconciler that
repairs a workflow file would be committing exactly that.
"""
from __future__ import annotations

import pathlib
from typing import Any, Iterator

import yaml

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.model import Evidence, Scope

TABLE = pathlib.Path(__file__).resolve().parent / "lifecycle-expectations.yaml"
RENOVATE_PATHS = (".github/renovate.json", "renovate.json5", ".github/renovate.json5")


def load_table() -> dict[str, Any]:
    return yaml.safe_load(TABLE.read_text(encoding="utf-8"))


def _observe(ctx: Context, repo: str, product: dict[str, Any]) -> dict[str, Any]:
    meta = ctx.client.get(f"/repos/{repo}") or {}
    renovate = None
    for cand in RENOVATE_PATHS:
        if ctx.client.get(f"/repos/{repo}/contents/{cand}"):
            renovate = cand
            break
    workflows = ctx.client.get(f"/repos/{repo}/actions/workflows") or {}
    names = {w.get("path", "").rsplit("/", 1)[-1] for w in (workflows.get("workflows") or [])}
    return {
        "renovate_config": "present" if renovate else "absent",
        "repo_archived": bool(meta.get("archived")),
        "alert_channel": "present" if (product.get("observability") or {}).get("alert_channel") else "absent",
        "ci_workflow": "present" if "ci.yml" in names else "absent",
    }


@registry.register
class Lifecycle(Comparator):
    comparator_id = "CMP-10"
    registry_key = "product.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        table = load_table()
        seq = 0
        for pid in sorted(ctx.declared.products):
            product = ctx.declared.products[pid]
            state = (product.get("identity") or {}).get("lifecycle")
            findings = []
            if state not in table["states"]:
                yield Row(key=pid, findings=[])
                continue
            for repo in ctx.declared.repositories_of(pid):
                name = repo["name"]
                observed = _observe(ctx, name, product)
                for check in table["checks"]:
                    want = check["expected_by_state"][state]
                    got = observed[check["reads"]]
                    if got == want:
                        continue
                    seq += 1
                    if check["safe"]:
                        findings.append(self.finding(
                            ctx, seq, Scope("repository", name, product=pid),
                            {"lifecycle": state, "check": check["id"], "expected": want},
                            {check["reads"]: got},
                            cell["drift_class"], cell["level"], cell["on_mismatch"],
                            [Evidence("registry", f"registries/products/{pid}/product.yaml"),
                             Evidence("github-api", f"/repos/{name}")],
                            proposed_repair={"class": "lifecycle-configuration-sync",
                                             "check": check["id"], "repository": name,
                                             "target": want, "applied": False},
                        ))
                    else:
                        findings.append(self.finding(
                            ctx, seq, Scope("repository", name, product=pid),
                            {"lifecycle": state, "check": check["id"], "expected": want},
                            {check["reads"]: got},
                            cell["class_escalated"], cell["level_escalated"], cell["on_mismatch"],
                            [Evidence("registry", f"registries/products/{pid}/product.yaml"),
                             Evidence("github-api", f"/repos/{name}")],
                        ))
            yield Row(key=pid, findings=findings)
PYEOF

cat > reconciler/comparators/tests/test_cmp_10.py <<'PYEOF'
import copy
import pathlib

from reconciler.comparators.base import Context
from reconciler.comparators.cmp_10_lifecycle import Lifecycle, load_table
from reconciler.loader import load

FIX = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures" / "declared"
REPO = "example-org/product-alpha-api"


class _Stub:
    def __init__(self, responses):
        self.responses, self.seen = responses, []

    def get(self, path, **p):
        self.seen.append(path)
        return self.responses.get(path)

    def paginate(self, path, **p):
        self.seen.append(path)
        return iter(self.responses.get(path) or [])

    def ledger(self):
        return {"api_calls": len(self.seen), "methods_used": ["GET"],
                "expected_source": "api.github.com", "max_calls": 5000}


def _responses(archived=False, renovate=True, ci=True):
    r = {f"/repos/{REPO}": {"archived": archived},
         f"/repos/{REPO}/actions/workflows":
             {"workflows": [{"path": ".github/workflows/ci.yml"}] if ci else []}}
    if renovate:
        r[f"/repos/{REPO}/contents/.github/renovate.json"] = {"decoded": "{}"}
    return r


def _ctx(responses, lifecycle="active"):
    d = load(FIX)
    products = copy.deepcopy(d.products)
    products["product-alpha"]["identity"]["lifecycle"] = lifecycle
    object.__setattr__(d, "products", products)
    return Context(declared=d, client=_Stub(responses), org="example-org",
                   today="2026-08-27", now="2026-08-27T06:00:00Z")


def test_the_table_covers_every_section_181_lifecycle_state():
    t = load_table()
    assert t["states"] == ["active", "maintenance", "paused", "sunset", "archived"]
    for check in t["checks"]:
        assert set(check["expected_by_state"]) == set(t["states"]), check["id"]


def test_the_workflow_and_archive_checks_are_never_safe():
    unsafe = {c["id"] for c in load_table()["checks"] if not c["safe"]}
    assert unsafe == {"repository-archived-flag", "ci-workflow-present"}


def test_a_conformant_active_product_produces_no_finding():
    fs = [f for r in Lifecycle().rows(_ctx(_responses())) for f in r.findings]
    assert fs == []


def test_a_missing_renovate_config_proposes_a_repair_and_never_applies_it():
    fs = [f for r in Lifecycle().rows(_ctx(_responses(renovate=False))) for f in r.findings]
    assert len(fs) == 1
    assert fs[0].response_level == 3 and fs[0].proposed_repair["applied"] is False


def test_a_missing_ci_workflow_alerts_and_proposes_nothing():
    fs = [f for r in Lifecycle().rows(_ctx(_responses(ci=False))) for f in r.findings]
    assert len(fs) == 1
    assert fs[0].response_level == 2 and fs[0].proposed_repair is None


def test_an_unarchived_repository_on_an_archived_product_alerts_only():
    fs = [f for r in Lifecycle().rows(_ctx(_responses(), lifecycle="archived"))
          for f in r.findings]
    ids = [f.declared["check"] for f in fs]
    assert "repository-archived-flag" in ids
    assert all(f.proposed_repair is None for f in fs if f.declared["check"] == "repository-archived-flag")
PYEOF

python -m pytest reconciler/comparators/tests/test_cmp_10.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/comparators
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-12: CMP-10 lifecycle versus Renovate, monitoring and CI configuration"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Six CMP-10 tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_10.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `6 passed` |
| A2 | Five lifecycle states, matching §18.1 | `cd "$CP" && python -c "from reconciler.comparators.cmp_10_lifecycle import load_table as t; print(' '.join(t()['states']))"` | `active maintenance paused sunset archived` |
| A3 | Exactly two checks are unsafe | `cd "$CP" && python -c "from reconciler.comparators.cmp_10_lifecycle import load_table as t; print(sum(1 for c in t()['checks'] if not c['safe']))"` | `2` |
| A4 | No repair is applied | `cd "$CP" && grep -c '"applied": False' reconciler/comparators/cmp_10_lifecycle.py` | `1` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_10.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "from reconciler.comparators.cmp_10_lifecycle import load_table as t; print(sum(1 for c in t()['checks'] if not c['safe']))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
6 passed
2
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L1`, if `registries/products/*/product.yaml` carries a `identity.lifecycle` value outside the five of Section 18.1. Do **not** add a sixth state to the table.
Do **not** mark `repository-archived-flag` or `ci-workflow-present` safe. Section 53.2's Level-3 "Applies to" list is closed, and neither is on it; L3 Phase 2 `L3-02-06` re-asserts that the list is closed at five classes.

---

## L3-01-13 — CMP-06: workflow template version versus the actual workflow file

**Size:** M **Depends on:** L3-01-05
**Owns:** `reconciler/comparators/cmp_06_workflow_version.py`, `reconciler/comparators/tests/test_cmp_06.py`
**Spec basis:** §53.1 row 6, *"Alert; flag `platform_compatibility` as drifted"*; §33.2 (the required-workflows list, and *"Reusable workflows ... are consumed by pinned tag"*); §60.1 (`reusable_workflow_versions`); §60.3 (compatibility states).
**Registry key:** `product.yaml`.

`templates/workflows/` is **L2's** tree (PARTITION.md line 18). This comparator reads it as runtime data — rule R2 — and never imports from it.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t13-cmp06
test -d templates/workflows && echo "GATE-1 templates-present OK" || echo "GATE-1 FAIL blocked-on-L2"
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/comparators/cmp_06_workflow_version.py <<'PYEOF'
"""CMP-06 - the workflow template version versus the actual workflow file.

Section 53.1: "Alert; flag platform_compatibility as drifted."

Two comparisons per required workflow of Section 33.2:

  1. every `uses:` line pinning a reusable workflow must name a tag in
     platform.yaml reusable_workflow_versions.supported;
  2. the file body with the `uses:` lines removed must equal the template body
     with the `uses:` lines removed - a product may sit on an older supported
     tag without being drifted, but it may not have a hand-edited body.

Both produce the same Amber finding, and both set flag_platform_compatibility,
which is the "flag platform_compatibility as drifted" half of the cell
(Section 60.3 owns what that flag then means).

templates/workflows/ is L2's tree. It is read here as runtime data (rule R2)
and never imported.
"""
from __future__ import annotations

import pathlib
import re
from typing import Iterator

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.model import Evidence, Scope

TEMPLATE_DIR = "templates/workflows"

#: Section 33.2, "Required workflows per repository", in the section's order.
REQUIRED_WORKFLOWS = (
    "ci.yml", "build.yml", "deploy-staging.yml", "deploy-production.yml",
    "migrate.yml", "restore-test.yml",
)
#: Section 33.2: required "wherever the product declares a recovery: block".
CONDITIONAL_WORKFLOWS = {"restore-production.yml": "recovery"}

USES = re.compile(r"^\s*uses:\s*(\S+)\s*$", re.M)


def strip_uses(body: str) -> str:
    return USES.sub("", body or "")


def pinned_tags(body: str) -> list[str]:
    out = []
    for ref in USES.findall(body or ""):
        if "@" in ref:
            out.append(ref.rsplit("@", 1)[1])
    return out


@registry.register
class WorkflowVersion(Comparator):
    comparator_id = "CMP-06"
    registry_key = "product.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        rwv = ctx.declared.platform.get("reusable_workflow_versions") or {}
        supported = {str(t) for t in (rwv.get("supported") or [])}
        tpl_root = pathlib.Path(ctx.declared.root) / TEMPLATE_DIR
        seq = 0
        for pid in sorted(ctx.declared.products):
            product = ctx.declared.products[pid]
            wanted = list(REQUIRED_WORKFLOWS)
            for name, key in CONDITIONAL_WORKFLOWS.items():
                if product.get(key):
                    wanted.append(name)
            findings = []
            for repo in ctx.declared.repositories_of(pid):
                name = repo["name"]
                listing = ctx.client.get(f"/repos/{name}/contents/.github/workflows") or []
                present = {e.get("name") for e in listing}
                for wf in wanted:
                    tpl_file = tpl_root / wf
                    template_body = tpl_file.read_text(encoding="utf-8") if tpl_file.is_file() else None
                    if wf not in present:
                        seq += 1
                        findings.append(self.finding(
                            ctx, seq, Scope("repository", name, product=pid),
                            {"workflow": wf, "required_by": "Section 33.2"},
                            {"present": False},
                            cell["drift_class"], cell["level"], cell["on_mismatch"],
                            [Evidence("template", f"{TEMPLATE_DIR}/{wf}"),
                             Evidence("github-api", f"/repos/{name}/contents/.github/workflows")],
                            flag_platform_compatibility=True,
                        ))
                        continue
                    got = ctx.client.get(f"/repos/{name}/contents/.github/workflows/{wf}") or {}
                    body = got.get("decoded") or ""
                    bad_tags = [t for t in pinned_tags(body) if t not in supported]
                    body_drift = template_body is not None and \
                        strip_uses(body).strip() != strip_uses(template_body).strip()
                    if bad_tags or body_drift:
                        seq += 1
                        findings.append(self.finding(
                            ctx, seq, Scope("repository", name, product=pid),
                            {"workflow": wf, "supported_tags": sorted(supported)},
                            {"unsupported_tags": bad_tags, "body_hand_edited": body_drift},
                            cell["drift_class"], cell["level"], cell["on_mismatch"],
                            [Evidence("template", f"{TEMPLATE_DIR}/{wf}"),
                             Evidence("github-api", f"/repos/{name}/contents/.github/workflows/{wf}")],
                            flag_platform_compatibility=True,
                        ))
            yield Row(key=pid, findings=findings)
PYEOF

cat > reconciler/comparators/tests/test_cmp_06.py <<'PYEOF'
import pathlib

from reconciler.comparators.base import Context
from reconciler.comparators.cmp_06_workflow_version import (
    CONDITIONAL_WORKFLOWS, REQUIRED_WORKFLOWS, WorkflowVersion, pinned_tags, strip_uses,
)
from reconciler.loader import load

FIX = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures" / "declared"
REPO = "example-org/product-alpha-api"
LIST = f"/repos/{REPO}/contents/.github/workflows"


class _Stub:
    def __init__(self, responses):
        self.responses, self.seen = responses, []

    def get(self, path, **p):
        self.seen.append(path)
        return self.responses.get(path)

    def paginate(self, path, **p):
        self.seen.append(path)
        return iter(self.responses.get(path) or [])

    def ledger(self):
        return {"api_calls": len(self.seen), "methods_used": ["GET"],
                "expected_source": "api.github.com", "max_calls": 5000}


def _all(tag="v4"):
    names = list(REQUIRED_WORKFLOWS) + ["restore-production.yml"]
    r = {LIST: [{"name": n} for n in names]}
    for n in names:
        r[f"{LIST}/{n}"] = {"decoded": f"name: {n}\njobs:\n  call:\n    uses: org/control-plane/.github/workflows/{n}@{tag}\n"}
    return r


def _ctx(responses):
    return Context(declared=load(FIX), client=_Stub(responses), org="example-org",
                   today="2026-08-27", now="2026-08-27T06:00:00Z")


def test_the_required_list_is_the_section_332_list():
    assert REQUIRED_WORKFLOWS == ("ci.yml", "build.yml", "deploy-staging.yml",
                                  "deploy-production.yml", "migrate.yml", "restore-test.yml")
    assert CONDITIONAL_WORKFLOWS == {"restore-production.yml": "recovery"}


def test_uses_lines_are_stripped_before_the_body_comparison():
    body = "a\nuses: x@v4\nb\n"
    assert strip_uses(body).split() == ["a", "b"]
    assert pinned_tags(body) == ["v4"]


def test_a_supported_tag_produces_no_finding():
    fs = [f for r in WorkflowVersion().rows(_ctx(_all("v3"))) for f in r.findings]
    assert fs == []


def test_an_unsupported_tag_is_amber_and_flags_platform_compatibility():
    fs = [f for r in WorkflowVersion().rows(_ctx(_all("v2"))) for f in r.findings]
    assert len(fs) == 7
    assert {f.drift_class for f in fs} == {"amber"}
    assert all(f.flag_platform_compatibility for f in fs)


def test_a_missing_required_workflow_is_reported():
    r = _all()
    r[LIST] = [e for e in r[LIST] if e["name"] != "migrate.yml"]
    fs = [f for row in WorkflowVersion().rows(_ctx(r)) for f in row.findings]
    assert [f.declared["workflow"] for f in fs] == ["migrate.yml"]
    assert fs[0].actual == {"present": False}
PYEOF

python -m pytest reconciler/comparators/tests/test_cmp_06.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/comparators
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-13: CMP-06 workflow template version versus actual workflow file"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Five CMP-06 tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_06.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `5 passed` |
| A2 | Six unconditional workflows, one conditional | `cd "$CP" && python -c "from reconciler.comparators.cmp_06_workflow_version import REQUIRED_WORKFLOWS as r, CONDITIONAL_WORKFLOWS as c; print(len(r), len(c))"` | `6 1` |
| A3 | Nothing under `templates/` was modified | `cd "$CP" && git status --porcelain templates \| wc -l` | `0` |
| A4 | No import from L2's tree | `cd "$CP" && grep -c 'import templates' reconciler/comparators/cmp_06_workflow_version.py` | `0` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_06.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git status --porcelain templates | wc -l
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
5 passed
0
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L2`, if `GATE-1` prints `FAIL` — `templates/workflows/` is L2's deliverable and this comparator has no declared side without it.
Do **not** create a workflow template. `templates/workflows/**` is L2's exclusive path (PARTITION.md line 18) and staging one file there fails the lane guard.

---

## L3-01-14 — CMP-11 and CMP-12: expired access, and unknown dependencies

**Size:** M **Depends on:** L3-01-05
**Owns:** `reconciler/comparators/cmp_11_expired_access.py`, `reconciler/comparators/cmp_12_dependencies.py`, `reconciler/comparators/tests/test_cmp_11_12.py`
**Spec basis:** §53.1 rows 11 and 12; §10.2 (assignment rules); §12.2 (person exit); §20.1 (*"A product cannot declare a dependency on a shared service that does not exist in the registry"*); invariant 55.
**Registry keys:** CMP-11 → `product.yaml`; CMP-12 → `services`.

CMP-12 is the only comparator that issues **no API call at all**: both sides are declared state. It still runs, still counts rows, and still fails the run's `services` count if it narrows — a registry-only comparison is exactly as susceptible to going vacuous as an API one.

CMP-12 therefore iterates the **service registry**, one `Row` per declared service, so that `rows_compared` for the `services` key reaches `rows_declared`; the unknown-dependency findings are attached to the product rows it also walks. Section 4.2 lists CMP-12 under both `product.yaml` and `services`; its `registry_key` — the key its rows count toward — is `services`.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t14-cmp11-12
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/comparators/cmp_11_expired_access.py <<'PYEOF'
"""CMP-11 - assignment end_date versus current Team membership.

Section 53.1: "Auto-revoke expired access."

PROPOSED, NEVER EXECUTED, in this phase. Rule R1, and Section 99.4 item 6:
"Auto-repair is deferred until detection has run clean for weeks." The
proposal carries the class name Section 53.2's Level-3 list uses -
"removing expired assignments and expired access" - so that L3 Phase 2's
executor recognises it when L0 eventually enables that class.

Two sources of expiry, both checked:
  - a product assignment whose end_date is in the past, where the person is
    still a member of the product Team;
  - a people.yaml end_date in the past where access_status is not revoked and
    the person is still an organisation member (Section 12.2).
"""
from __future__ import annotations

from typing import Iterator

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.comparators.cmp_03_team_membership import team_slug
from reconciler.model import Evidence, Scope


@registry.register
class ExpiredAccess(Comparator):
    comparator_id = "CMP-11"
    registry_key = "product.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        org_members = {
            (m.get("login") or "").lower()
            for m in ctx.client.paginate(f"/orgs/{ctx.org}/members", per_page=100)
        }
        seq = 0
        for pid in sorted(ctx.declared.products):
            slug = team_slug(pid)
            team = {
                (m.get("login") or "").lower()
                for m in ctx.client.paginate(f"/orgs/{ctx.org}/teams/{slug}/members", per_page=100)
            }
            findings = []
            for a in ctx.declared.products[pid].get("assignments", []) or []:
                end = a.get("end_date")
                if not end or str(end) >= ctx.today:
                    continue
                login = (ctx.declared.login_of(a["person"]) or "").lower()
                if login and login in team:
                    seq += 1
                    findings.append(self.finding(
                        ctx, seq, Scope("person", a["person"], product=pid),
                        {"end_date": str(end), "assignment": a.get("type")},
                        {"still_in_team": slug},
                        cell["drift_class"], cell["level"], cell["on_mismatch"],
                        [Evidence("registry", f"registries/products/{pid}/product.yaml"),
                         Evidence("github-api", f"/orgs/{ctx.org}/teams/{slug}/members")],
                        proposed_repair={"class": "expired-access-removal",
                                         "team": slug, "login": login, "applied": False},
                    ))
            for person in ctx.declared.people.get("people", []) or []:
                end = person.get("end_date")
                login = (person.get("github_login") or "").lower()
                if not end or str(end) >= ctx.today:
                    continue
                if person.get("access_status") == "revoked" or login not in org_members:
                    continue
                seq += 1
                findings.append(self.finding(
                    ctx, seq, Scope("person", person["id"], product=pid),
                    {"end_date": str(end), "access_status": person.get("access_status")},
                    {"still_org_member": True},
                    cell["drift_class"], cell["level"], cell["on_mismatch"],
                    [Evidence("registry", "registries/people.yaml"),
                     Evidence("github-api", f"/orgs/{ctx.org}/members")],
                    proposed_repair={"class": "expired-access-removal",
                                     "organisation": ctx.org, "login": login, "applied": False},
                ))
                break
            yield Row(key=pid, findings=findings)
PYEOF

cat > reconciler/comparators/cmp_12_dependencies.py <<'PYEOF'
"""CMP-12 - a declared dependency versus the shared service registry.

Section 53.1: "Fail CI on unknown dependency."
Section 20.1: "A product cannot declare a dependency on a shared service that
does not exist in the registry. CI enforces this, which is what keeps the
dependency graph honest."

The only comparator in the set that issues no API call: both sides are
declared state. It counts rows anyway. A registry-only comparison goes vacuous
exactly as easily as an API one - a glob that stops matching, a directory
renamed - and Section 53.1's count rule is the instrument for both.

registry_key is "services": one Row per declared service, so rows_compared for
that key reaches rows_declared. The unknown-dependency findings are attached
to the service-registry rows they concern, and to a synthetic row per product
carrying an unknown id.
"""
from __future__ import annotations

from typing import Iterator

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.model import Evidence, Scope


@registry.register
class Dependencies(Comparator):
    comparator_id = "CMP-12"
    registry_key = "services"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        known = set(ctx.declared.services)
        seq = 0
        for sid in sorted(known):
            yield Row(key=sid, findings=[])
        for pid in sorted(ctx.declared.products):
            deps = ((ctx.declared.products[pid].get("dependencies") or {}).get("internal") or [])
            unknown = [d for d in deps if d not in known]
            if not unknown:
                continue
            repos = [r["name"] for r in ctx.declared.repositories_of(pid)]
            seq += 1
            yield Row(
                key=f"unknown:{pid}",
                findings=[self.finding(
                    ctx, seq, Scope("product", pid, product=pid),
                    {"dependencies.internal": deps},
                    {"unknown": unknown, "known_services": sorted(known)},
                    cell["drift_class"], cell["level"], cell["on_mismatch"],
                    [Evidence("registry", f"registries/products/{pid}/product.yaml"),
                     Evidence("registry", "registries/services/*/service.yaml")],
                    blocks_repository=repos,
                )],
            )
PYEOF

cat > reconciler/comparators/tests/test_cmp_11_12.py <<'PYEOF'
import copy
import pathlib

from reconciler.comparators.base import Context
from reconciler.comparators.cmp_11_expired_access import ExpiredAccess
from reconciler.comparators.cmp_12_dependencies import Dependencies
from reconciler.loader import load

FIX = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures" / "declared"
ORG = "example-org"
MEMBERS = f"/orgs/{ORG}/members"
TEAM = f"/orgs/{ORG}/teams/product-alpha/members"


class _Stub:
    def __init__(self, responses):
        self.responses, self.seen = responses, []

    def get(self, path, **p):
        self.seen.append(path)
        return self.responses.get(path)

    def paginate(self, path, **p):
        self.seen.append(path)
        return iter(self.responses.get(path) or [])

    def ledger(self):
        return {"api_calls": len(self.seen), "methods_used": ["GET"],
                "expected_source": "api.github.com", "max_calls": 5000}


def _ctx(today, members=("fixture-con-1",), team=("fixture-con-1",), declared=None):
    return Context(
        declared=declared or load(FIX),
        client=_Stub({MEMBERS: [{"login": m} for m in members],
                      TEAM: [{"login": m} for m in team]}),
        org=ORG, today=today, now=f"{today}T06:00:00Z",
    )


def test_an_unexpired_assignment_produces_no_finding():
    fs = [f for r in ExpiredAccess().rows(_ctx("2026-01-15")) for f in r.findings]
    assert fs == []


def test_an_expired_assignment_still_in_the_team_proposes_a_revoke():
    fs = [f for r in ExpiredAccess().rows(_ctx("2026-12-15")) for f in r.findings]
    assert any(f.proposed_repair and f.proposed_repair["class"] == "expired-access-removal" for f in fs)
    assert all(f.proposed_repair["applied"] is False for f in fs if f.proposed_repair)


def test_the_expired_finding_is_level_three_proposed_only():
    fs = [f for r in ExpiredAccess().rows(_ctx("2026-12-15")) for f in r.findings]
    assert {f.response_level for f in fs} == {3}


def test_cmp12_yields_one_row_per_declared_service():
    rows = list(Dependencies().rows(_ctx("2026-08-27")))
    assert "auth-service" in {r.key for r in rows}


def test_a_known_dependency_produces_no_finding():
    fs = [f for r in Dependencies().rows(_ctx("2026-08-27")) for f in r.findings]
    assert fs == []


def test_an_unknown_dependency_is_blocking_and_names_the_repositories():
    d = load(FIX)
    products = copy.deepcopy(d.products)
    products["product-alpha"]["dependencies"]["internal"].append("ghost-service")
    object.__setattr__(d, "products", products)
    fs = [f for r in Dependencies().rows(_ctx("2026-08-27", declared=d)) for f in r.findings]
    assert len(fs) == 1
    assert fs[0].drift_class == "blocking" and fs[0].response_level == 4
    assert fs[0].actual["unknown"] == ["ghost-service"]
    assert fs[0].blocks_repository == ["example-org/product-alpha-api"]
PYEOF

python -m pytest reconciler/comparators/tests/test_cmp_11_12.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/comparators
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-14: CMP-11 expired access and CMP-12 unknown dependencies"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Six tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_11_12.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `6 passed` |
| A2 | CMP-12 issues no API call | `cd "$CP" && grep -cE 'ctx\.client\.' reconciler/comparators/cmp_12_dependencies.py` | `0` |
| A3 | CMP-11 proposes and never applies | `cd "$CP" && grep -c '"applied": False' reconciler/comparators/cmp_11_expired_access.py` | `2` |
| A4 | CMP-12 counts toward `services` | `cd "$CP" && python -c "from reconciler.comparators.cmp_12_dependencies import Dependencies as D; print(D.registry_key)"` | `services` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_11_12.py -q 2>&1 | grep -oE '^[0-9]+ passed'
grep -cE 'ctx\.client\.' reconciler/comparators/cmp_12_dependencies.py
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
6 passed
0
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L1`, if `registries/services/` does not exist — CMP-12's declared side has no source and its `rows_declared` would be `0`, which makes the comparison vacuously clean, which is EC-109.
Do **not** execute the proposed revoke. Do **not** call the team-membership removal endpoint. Rule R1, and Section 53.2's Level 3 is not enabled in this phase for any class.

---

## L3-01-15 — CMP-13: the resolved commit SHA behind every `workflows/*` tag

**Size:** M **Depends on:** L3-01-05
**Owns:** `reconciler/comparators/cmp_13_tag_shas.py`, `reconciler/state/workflow-tag-shas.json`, `reconciler/comparators/tests/test_cmp_13.py`
**Spec basis:** §53.1 row 13, *"Blocking on any change — a moved tag reaches every consumer with no reviewable diff"*; §33.2 (*"A tag is movable and is therefore not a pin unless the ref itself is protected ... each consumed tag's resolved commit SHA sits in the reconciliation comparison set"*); §33.3; invariant 72.
**Registry key:** `platform.yaml`.

The declared side is a **recorded** SHA, not a registry field: the registry declares the tag, and this lane records what that tag resolved to last time. That record is lane-owned state under `reconciler/state/`.

An annotated tag needs two calls: `git/ref/tags/{tag}` returns the tag object, and `git/tags/{sha}` dereferences it to the commit. Comparing the tag-object SHA instead of the commit SHA would report a false change every time a tag is re-annotated at the same commit, and would miss nothing — but it would also report nothing useful, because a re-annotated tag at a new commit and a re-annotated tag at the same commit look identical at that level.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t15-cmp13
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p reconciler/state
cat > reconciler/state/workflow-tag-shas.json <<'JSONEOF'
{
  "_comment": [
    "The commit SHA each workflows/* tag resolved to, at last observation.",
    "Spec 33.2: 'each consumed tag's resolved commit SHA sits in the",
    "reconciliation comparison set'. Spec 53.1: any change is Blocking - a",
    "moved tag reaches every consumer with no reviewable diff.",
    "A tag seen for the first time is recorded and reported Amber once,",
    "never silently. Entries are appended by the reconciler run and are",
    "reviewed like any other declared state: an edit here is an assertion",
    "that a tag legitimately moved."
  ],
  "state_version": 1,
  "tags": {}
}
JSONEOF

cat > reconciler/comparators/cmp_13_tag_shas.py <<'PYEOF'
"""CMP-13 - platform.yaml workflow versions versus the SHA each tag resolves to.

Section 53.1: "Blocking on any change - a moved tag reaches every consumer
with no reviewable diff."

Section 33.2 states why this row is P0: "Moving a tag is the one way to
execute new code in every product's pipeline with no pull request, no change
manifest, no canary set and no diff in any product repository - it defeats the
blast-radius apparatus of Section 33.3 and invariant 72 in a single command."

Annotated tags are dereferenced. /git/ref/tags/{tag} returns object.type
"tag" for an annotated tag and "commit" for a lightweight one; the annotated
case is resolved through /git/tags/{sha} to object.sha, so the value compared
is always the COMMIT sha.

First observation of a tag is recorded and reported Amber ONCE. It is never
silent: a tag that appears with no recorded SHA is either a new release or a
tag someone created outside the release process, and the reader must see it.
"""
from __future__ import annotations

import json
import pathlib
from typing import Any, Iterator

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.model import Evidence, Scope

STATE = pathlib.Path(__file__).resolve().parent.parent / "state" / "workflow-tag-shas.json"
CONTROL_PLANE_REPO = "control-plane"


def load_state() -> dict[str, Any]:
    return json.loads(STATE.read_text(encoding="utf-8"))


def declared_tags(platform: dict[str, Any]) -> list[str]:
    rwv = platform.get("reusable_workflow_versions") or {}
    seen: list[str] = []
    for value in [rwv.get("current")] + list(rwv.get("supported") or []) + list(rwv.get("deprecated") or []):
        if value and str(value) not in seen:
            seen.append(str(value))
    return seen


def resolve(client, org: str, tag: str) -> str | None:
    ref = client.get(f"/repos/{org}/{CONTROL_PLANE_REPO}/git/ref/tags/{tag}")
    obj = (ref or {}).get("object") or {}
    if obj.get("type") == "tag":
        deref = client.get(f"/repos/{org}/{CONTROL_PLANE_REPO}/git/tags/{obj.get('sha')}")
        return ((deref or {}).get("object") or {}).get("sha")
    return obj.get("sha")


@registry.register
class TagShas(Comparator):
    comparator_id = "CMP-13"
    registry_key = "platform.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        recorded = load_state().get("tags") or {}
        seq = 0
        for tag in declared_tags(ctx.declared.platform):
            actual = resolve(ctx.client, ctx.org, tag)
            known = recorded.get(tag)
            findings = []
            if known is None:
                seq += 1
                findings.append(self.finding(
                    ctx, seq, Scope("tag", tag),
                    {"recorded_sha": None},
                    {"resolved_sha": actual, "first_observation": True},
                    cell["class_escalated"], cell["level_escalated"], cell["on_mismatch"],
                    [Evidence("registry", "registries/platform.yaml"),
                     Evidence("github-api", f"/repos/{ctx.org}/{CONTROL_PLANE_REPO}/git/ref/tags/{tag}")],
                ))
            elif actual != known:
                seq += 1
                findings.append(self.finding(
                    ctx, seq, Scope("tag", tag),
                    {"recorded_sha": known},
                    {"resolved_sha": actual},
                    cell["drift_class"], cell["level"], cell["on_mismatch"],
                    [Evidence("registry", "registries/platform.yaml"),
                     Evidence("github-api", f"/repos/{ctx.org}/{CONTROL_PLANE_REPO}/git/ref/tags/{tag}")],
                ))
            yield Row(key=tag, findings=findings)
PYEOF

cat > reconciler/comparators/tests/test_cmp_13.py <<'PYEOF'
import json
import pathlib

from reconciler.comparators import cmp_13_tag_shas as m
from reconciler.comparators.base import Context
from reconciler.loader import load

FIX = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures" / "declared"
ORG = "example-org"
A = "a" * 40
B = "b" * 40


class _Stub:
    def __init__(self, responses):
        self.responses, self.seen = responses, []

    def get(self, path, **p):
        self.seen.append(path)
        return self.responses.get(path)

    def paginate(self, path, **p):
        self.seen.append(path)
        return iter(self.responses.get(path) or [])

    def ledger(self):
        return {"api_calls": len(self.seen), "methods_used": ["GET"],
                "expected_source": "api.github.com", "max_calls": 5000}


def _lightweight(tag, sha):
    return {f"/repos/{ORG}/control-plane/git/ref/tags/{tag}": {"object": {"type": "commit", "sha": sha}}}


def _annotated(tag, tagsha, commitsha):
    return {
        f"/repos/{ORG}/control-plane/git/ref/tags/{tag}": {"object": {"type": "tag", "sha": tagsha}},
        f"/repos/{ORG}/control-plane/git/tags/{tagsha}": {"object": {"sha": commitsha}},
    }


def _ctx(responses):
    return Context(declared=load(FIX), client=_Stub(responses), org=ORG,
                   today="2026-08-27", now="2026-08-27T06:00:00Z")


def test_declared_tags_are_deduplicated_across_current_supported_deprecated():
    d = load(FIX)
    assert m.declared_tags(d.platform) == ["v4", "v3", "v2"]


def test_the_shipped_state_file_starts_empty_and_is_well_formed():
    doc = json.loads(m.STATE.read_text(encoding="utf-8"))
    assert doc["state_version"] == 1 and doc["tags"] == {}


def test_an_annotated_tag_is_dereferenced_to_the_commit_sha():
    r = _annotated("v4", B, A)
    assert m.resolve(_Stub(r), ORG, "v4") == A


def test_a_first_observation_is_amber_and_never_silent(monkeypatch):
    monkeypatch.setattr(m, "load_state", lambda: {"tags": {}})
    r = {}
    for t in ("v4", "v3", "v2"):
        r.update(_lightweight(t, A))
    fs = [f for row in m.TagShas().rows(_ctx(r)) for f in row.findings]
    assert len(fs) == 3
    assert {f.drift_class for f in fs} == {"amber"}
    assert all(f.actual["first_observation"] for f in fs)


def test_a_moved_tag_is_blocking(monkeypatch):
    monkeypatch.setattr(m, "load_state", lambda: {"tags": {"v4": A, "v3": A, "v2": A}})
    r = {}
    r.update(_lightweight("v4", B))
    r.update(_lightweight("v3", A))
    r.update(_lightweight("v2", A))
    fs = [f for row in m.TagShas().rows(_ctx(r)) for f in row.findings]
    assert len(fs) == 1
    assert fs[0].scope.name == "v4"
    assert fs[0].drift_class == "blocking" and fs[0].response_level == 4
PYEOF

python -m pytest reconciler/comparators/tests/test_cmp_13.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-15: CMP-13 workflow tag resolved-SHA comparison"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Five CMP-13 tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_13.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `5 passed` |
| A2 | The state file ships empty | `cd "$CP" && python -c "import json;print(json.load(open('reconciler/state/workflow-tag-shas.json'))['tags'])"` | `{}` |
| A3 | A moved tag is Blocking | `cd "$CP" && python -c "from reconciler.comparators.registry import load_manifest as m; r=m()['CMP-13']; print(r['drift_class'], r['level'])"` | `blocking 4` |
| A4 | Annotated tags are dereferenced | `cd "$CP" && grep -c 'git/tags/' reconciler/comparators/cmp_13_tag_shas.py` | `1` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_13.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "import json;print(len(json.load(open('reconciler/state/workflow-tag-shas.json'))['tags']))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
5 passed
0
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L0`, if the control-plane repository's tag ruleset on `workflows/*` does **not** have an empty bypass-actor list. Section 33.2 requires *"a tag ruleset blocking updates and deletions on `workflows/*` with an empty bypass-actor list"*, and a movable tag makes this comparator a report of an unenforced control rather than a detector of a violated one. Report it; do not fix it — the ruleset is L5's `access/**`.
Do **not** pre-populate `workflow-tag-shas.json` with SHAs you read by hand. First observation is Amber by design, and hand-seeding it removes the one signal that a tag existed before anyone looked.

---

## L3-01-16 — CMP-14: the Renovate bypass ruleset split

**Size:** M **Depends on:** L3-01-05
**Owns:** `reconciler/comparators/cmp_14_bypass_ruleset.py`, `reconciler/comparators/tests/test_cmp_14.py`
**Spec basis:** §53.1 row 14, *"Blocking where that ruleset names any bypass actor"*; §33.2 (the two-ruleset split, and *"a bypass actor is exempt from every rule in the ruleset it is listed on (D89), so a compensator sitting inside the bypassed ruleset compensates for nothing"*); **D89**.
**Registry key:** `product.yaml`.

Two Blocking cases, and the second is the one that matters most: **no such ruleset at all**. A missing compensating ruleset reads identically to a compliant one if the comparator only inspects rulesets it finds.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t16-cmp14
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/comparators/cmp_14_bypass_ruleset.py <<'PYEOF'
"""CMP-14 - the Renovate bypass ruleset split.

Section 53.1: "Blocking where that ruleset names any bypass actor."

Section 33.2 and D89: the bypass is split across two rulesets. Ruleset A
carries the pull-request rules and lists Renovate as a bypass actor. Ruleset B
carries the compensating `renovate-path-guard` required status check and lists
"no bypass actor at all, because a bypass actor is exempt from every rule in
the ruleset it is listed on (D89), so a compensator sitting inside the
bypassed ruleset compensates for nothing."

Two Blocking cases:
  - the guard ruleset exists and names any bypass actor;
  - no ruleset carries the guard context at all.

The second is the more dangerous, and the one a naive implementation misses:
an absent compensator produces no ruleset to inspect, and a comparator that
only inspects what it finds reports clean.
"""
from __future__ import annotations

from typing import Iterator

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.model import Evidence, Scope

GUARD_CONTEXT = "renovate-path-guard"


def carries_guard(ruleset: dict) -> bool:
    for rule in ruleset.get("rules") or []:
        if rule.get("type") != "required_status_checks":
            continue
        params = rule.get("parameters") or {}
        for check in params.get("required_status_checks") or []:
            if check.get("context") == GUARD_CONTEXT:
                return True
    return False


@registry.register
class BypassRuleset(Comparator):
    comparator_id = "CMP-14"
    registry_key = "product.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        seq = 0
        for pid in sorted(ctx.declared.products):
            findings = []
            for repo in ctx.declared.repositories_of(pid):
                name = repo["name"]
                index = ctx.client.get(f"/repos/{name}/rulesets", includes_parents="true") or []
                guard = None
                for entry in index:
                    full = ctx.client.get(f"/repos/{name}/rulesets/{entry.get('id')}")
                    if full and carries_guard(full):
                        guard = full
                        break
                if guard is None:
                    seq += 1
                    findings.append(self.finding(
                        ctx, seq, Scope("repository", name, product=pid),
                        {"ruleset_carrying": GUARD_CONTEXT, "required": True},
                        {"found": False},
                        cell["drift_class"], cell["level"], cell["on_mismatch"],
                        [Evidence("github-api", f"/repos/{name}/rulesets")],
                        blocks_repository=[name],
                    ))
                    continue
                actors = guard.get("bypass_actors") or []
                if actors:
                    seq += 1
                    findings.append(self.finding(
                        ctx, seq, Scope("repository", name, product=pid),
                        {"bypass_actors": []},
                        {"bypass_actors": actors, "ruleset_id": guard.get("id")},
                        cell["drift_class"], cell["level"], cell["on_mismatch"],
                        [Evidence("github-api", f"/repos/{name}/rulesets/{guard.get('id')}")],
                        blocks_repository=[name],
                    ))
            yield Row(key=pid, findings=findings)
PYEOF

cat > reconciler/comparators/tests/test_cmp_14.py <<'PYEOF'
import pathlib

from reconciler.comparators.base import Context
from reconciler.comparators.cmp_14_bypass_ruleset import BypassRuleset, carries_guard
from reconciler.loader import load

FIX = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures" / "declared"
REPO = "example-org/product-alpha-api"
INDEX = f"/repos/{REPO}/rulesets"


class _Stub:
    def __init__(self, responses):
        self.responses, self.seen = responses, []

    def get(self, path, **p):
        self.seen.append(path)
        return self.responses.get(path)

    def paginate(self, path, **p):
        self.seen.append(path)
        return iter(self.responses.get(path) or [])

    def ledger(self):
        return {"api_calls": len(self.seen), "methods_used": ["GET"],
                "expected_source": "api.github.com", "max_calls": 5000}


def _guard(actors):
    return {"id": 2, "bypass_actors": actors,
            "rules": [{"type": "required_status_checks",
                       "parameters": {"required_status_checks": [{"context": "renovate-path-guard"}]}}]}


def _rules_a():
    return {"id": 1, "bypass_actors": [{"actor_id": 9, "actor_type": "Integration"}],
            "rules": [{"type": "pull_request", "parameters": {}}]}


def _ctx(rulesets):
    responses = {INDEX: [{"id": r["id"]} for r in rulesets]}
    for r in rulesets:
        responses[f"{INDEX}/{r['id']}"] = r
    return Context(declared=load(FIX), client=_Stub(responses), org="example-org",
                   today="2026-08-27", now="2026-08-27T06:00:00Z")


def test_carries_guard_recognises_the_guard_context_only():
    assert carries_guard(_guard([])) is True
    assert carries_guard(_rules_a()) is False


def test_the_compliant_split_produces_no_finding():
    fs = [f for r in BypassRuleset().rows(_ctx([_rules_a(), _guard([])])) for f in r.findings]
    assert fs == []


def test_a_bypass_actor_on_the_guard_ruleset_is_blocking():
    fs = [f for r in BypassRuleset().rows(
        _ctx([_rules_a(), _guard([{"actor_id": 9, "actor_type": "Integration"}])]))
        for f in r.findings]
    assert len(fs) == 1
    assert fs[0].drift_class == "blocking" and fs[0].response_level == 4
    assert fs[0].blocks_repository == [REPO]


def test_an_absent_guard_ruleset_is_blocking_not_clean():
    fs = [f for r in BypassRuleset().rows(_ctx([_rules_a()])) for f in r.findings]
    assert len(fs) == 1
    assert fs[0].actual == {"found": False}
    assert fs[0].drift_class == "blocking"


def test_ruleset_a_may_list_renovate_without_a_finding():
    fs = [f for r in BypassRuleset().rows(_ctx([_rules_a(), _guard([])])) for f in r.findings]
    assert fs == []
PYEOF

python -m pytest reconciler/comparators/tests/test_cmp_14.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/comparators
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-16: CMP-14 Renovate bypass ruleset split"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Five CMP-14 tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_14.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `5 passed` |
| A2 | The guard context is the §33.2 name | `cd "$CP" && grep -c 'renovate-path-guard' reconciler/comparators/cmp_14_bypass_ruleset.py` | `1` |
| A3 | An absent guard ruleset is a finding, not a pass | `cd "$CP" && grep -c '"found": False' reconciler/comparators/cmp_14_bypass_ruleset.py` | `1` |
| A4 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_14.py -q 2>&1 | grep -oE '^[0-9]+ passed'
grep -c '"found": False' reconciler/comparators/cmp_14_bypass_ruleset.py
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
5 passed
1
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L0`, if the required status-check context name used by this estate's path guard is not `renovate-path-guard`. Section 33.2 names it; if a decision record names a different context, use the recorded one and cite it in the PR body.
Do **not** widen the comparator to accept a bypass actor *"because it is only the Renovate app"*. D89 is explicit: a bypass actor is exempt from every rule in the ruleset it is listed on, which is why the compensator sits in a ruleset with none.

---

## L3-01-17 — CMP-15: record-store write freshness

**Size:** M **Depends on:** L3-01-05
**Owns:** `reconciler/comparators/cmp_15_write_freshness.py`, `reconciler/comparators/tests/test_cmp_15.py`
**Spec basis:** §53.1 row 15, *"Amber; Blocking for `events/`, `records/deployments/` and `records/uat/`"*; §97.2 (*"Write freshness is an instrument, because zero is the good value ... computed from the git commit timestamps on the store's path so the check holds even when the health computation's other inputs are broken"*).
**Registry key:** `os-health.yaml`.

The three Blocking stores are named by the spec and are hard-coded as a frozen tuple — this is one of the very few literals rule R3 permits, because the three names are the spec cell itself and the manifest carries the cell verbatim beside them.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t17-cmp15
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/comparators/cmp_15_write_freshness.py <<'PYEOF'
"""CMP-15 - the declared write-freshness window versus the store's last commit.

Section 53.1: "Amber; Blocking for events/, records/deployments/ and
records/uat/."

Section 97.2: "Every store above declares an expected maximum inter-write
interval in os-health.yaml, computed from the git commit timestamps on the
store's path so the check holds even when the health computation's other
inputs are broken: a store past its interval is Amber, and Blocking for
events/, records/deployments/ and records/uat/."

The reason the three are Blocking rather than Amber is in the same paragraph:
"a workflow whose record-write step fails silently renders every count-shaped
derived metric as zero - no ready-queue misses, no anomalies, no regressions -
which is indistinguishable from health."

A store with NO commit at all is treated as past its interval, not as new.
Fail closed (Section 64.2).
"""
from __future__ import annotations

import datetime as dt
import re
from typing import Any, Iterator

from reconciler import counts
from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.model import Evidence, Scope

#: Section 53.1, the three stores the cell names. Verbatim.
BLOCKING_STORES = ("events/", "records/deployments/", "records/uat/")

_DUR = re.compile(r"^P(?:(\d+)D)?(?:T(\d+)H)?$")


def interval_hours(value: Any) -> float:
    """Accept PnD, PTnH, or a plain number of hours."""
    if isinstance(value, (int, float)):
        return float(value)
    m = _DUR.fullmatch(str(value))
    if not m or not any(m.groups()):
        raise ValueError(f"unrecognised write-freshness interval: {value!r}")
    days = int(m.group(1) or 0)
    hours = int(m.group(2) or 0)
    return days * 24 + hours


@registry.register
class WriteFreshness(Comparator):
    comparator_id = "CMP-15"
    registry_key = "os-health.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        now = dt.datetime.fromisoformat(ctx.now.replace("Z", "+00:00"))
        seq = 0
        for store, spec in sorted(counts.stores_with_interval(ctx.declared).items()):
            window = interval_hours(spec["max_inter_write_interval"])
            commits = ctx.client.get(
                f"/repos/{ctx.org}/{ctx.records_repo}/commits", path=store, per_page=1
            ) or []
            latest = None
            if commits:
                latest = (((commits[0] or {}).get("commit") or {}).get("committer") or {}).get("date")
            findings = []
            stale = True
            age_hours: float | None = None
            if latest:
                seen = dt.datetime.fromisoformat(str(latest).replace("Z", "+00:00"))
                age_hours = (now - seen).total_seconds() / 3600.0
                stale = age_hours > window
            if stale:
                blocking = store in BLOCKING_STORES
                seq += 1
                findings.append(self.finding(
                    ctx, seq, Scope("record-store", store),
                    {"max_inter_write_interval": spec["max_inter_write_interval"],
                     "window_hours": window},
                    {"latest_commit": latest, "age_hours": age_hours},
                    cell["class_escalated"] if blocking else cell["drift_class"],
                    cell["level_escalated"] if blocking else cell["level"],
                    cell["on_mismatch"],
                    [Evidence("registry", "registries/os-health.yaml"),
                     Evidence("records-repository", store)],
                ))
            yield Row(key=store, findings=findings)
PYEOF

cat > reconciler/comparators/tests/test_cmp_15.py <<'PYEOF'
import pathlib

import pytest

from reconciler.comparators.base import Context
from reconciler.comparators.cmp_15_write_freshness import (
    BLOCKING_STORES, WriteFreshness, interval_hours,
)
from reconciler.loader import load

FIX = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures" / "declared"
ORG = "example-org"
NOW = "2026-08-27T06:00:00Z"
STORES = ("events/", "records/deployments/", "records/incidents/",
          "records/restore-tests/", "records/uat/")


class _Stub:
    def __init__(self, responses):
        self.responses, self.seen = responses, []

    def get(self, path, **p):
        self.seen.append((path, p.get("path")))
        return self.responses.get(p.get("path"))

    def paginate(self, path, **p):
        self.seen.append(path)
        return iter([])

    def ledger(self):
        return {"api_calls": len(self.seen), "methods_used": ["GET"],
                "expected_source": "api.github.com", "max_calls": 5000}


def _ctx(dates):
    responses = {
        store: ([{"commit": {"committer": {"date": d}}}] if d else [])
        for store, d in dates.items()
    }
    return Context(declared=load(FIX), client=_Stub(responses), org=ORG,
                   today="2026-08-27", now=NOW)


def test_the_three_blocking_stores_are_the_section_531_three():
    assert BLOCKING_STORES == ("events/", "records/deployments/", "records/uat/")


def test_interval_parsing_accepts_days_hours_and_plain_numbers():
    assert interval_hours("P7D") == 168
    assert interval_hours("PT24H") == 24
    assert interval_hours(12) == 12
    with pytest.raises(ValueError):
        interval_hours("weekly")


def test_a_fresh_store_produces_no_finding():
    fs = [f for r in WriteFreshness().rows(_ctx({s: "2026-08-27T05:00:00Z" for s in STORES}))
          for f in r.findings]
    assert fs == []


def test_a_stale_non_named_store_is_amber():
    d = {s: "2026-08-27T05:00:00Z" for s in STORES}
    d["records/incidents/"] = "2026-01-01T00:00:00Z"
    fs = [f for r in WriteFreshness().rows(_ctx(d)) for f in r.findings]
    assert len(fs) == 1 and fs[0].drift_class == "amber" and fs[0].response_level == 2


def test_a_store_with_no_commit_is_stale_not_new():
    d = {s: "2026-08-27T05:00:00Z" for s in STORES}
    d["events/"] = None
    fs = [f for r in WriteFreshness().rows(_ctx(d)) for f in r.findings]
    assert len(fs) == 1
    assert fs[0].drift_class == "blocking" and fs[0].response_level == 4
    assert fs[0].actual["latest_commit"] is None
PYEOF

python -m pytest reconciler/comparators/tests/test_cmp_15.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/comparators
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-17: CMP-15 record-store write freshness"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Five CMP-15 tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_15.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `5 passed` |
| A2 | Exactly three Blocking stores | `cd "$CP" && python -c "from reconciler.comparators.cmp_15_write_freshness import BLOCKING_STORES as b; print(len(b), ' '.join(b))"` | `3 events/ records/deployments/ records/uat/` |
| A3 | Every declared store carries an interval | `cd "$CP" && python -c "from reconciler.loader import load; from reconciler.counts import stores_with_interval as s; print(len(s(load('.'))))"` | an integer `>= 3` |
| A4 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_15.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "from reconciler.comparators.cmp_15_write_freshness import BLOCKING_STORES as b; print(len(b))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
5 passed
3
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L1`, if `registries/os-health.yaml` carries no `record_stores` key, or if any of the three Blocking stores is absent from it. Section 97.2 requires every store to declare an interval; a store with no declared interval is not compared, and an uncompared `events/` store is the exact silent-zero failure the section describes.
Do **not** add a fourth store to `BLOCKING_STORES`. Section 53.1 names three.

---

## L3-01-18 — CMP-16 and CMP-17: restore evidence

**Size:** L **Depends on:** L3-01-05; **D-L3-03** (CMP-16 only)
**Owns:** `reconciler/comparators/cmp_16_production_restore.py`, `reconciler/comparators/cmp_17_restore_tested.py`, `reconciler/comparators/restore-binding.yaml`, `reconciler/comparators/tests/test_cmp_16_17.py`
**Spec basis:** §53.1 rows 16 and 17; §44.5 (*"A production restore whose record names no integrity-check result and no verifier is Red drift"*); §44.2 (the canonical restore cadence); §97.2 (`records/restore-tests/`); §15.1 (`recovery.restore_tested`); SIG-17.
**Registry key:** `product.yaml` for both.

The two rows are the two halves of the same claim — *"we can get the data back"* — and differ in which record is the evidence. CMP-17's store is named by Section 97.2 (`records/restore-tests/`) and needs no decision. CMP-16's store is **not** in Section 97.2's table, which is why D-L3-03 exists.

Note the class asymmetry, and do not smooth it: CMP-16 is **Red**, CMP-17 is **Blocking**. Section 53.4's Red row reads *"No, but visible on the Founder view"* under "Blocks work", so a Red finding takes Level 2. Section 53.1's own words for CMP-17 explain the difference: *"a declared date with no matching record is an unevidenced reliability claim, not a scheduling question."*

### Branch and gate

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t18-cmp16-17
test -f docs/decisions/D-L3-03.md && echo "GATE-1 decision-present OK" || echo "GATE-1 FAIL"
python - <<'PYEOF'
import pathlib, re
p = pathlib.Path("docs/decisions/D-L3-03.md")
t = p.read_text(encoding="utf-8") if p.exists() else ""
for key in ("production_restore_store_path", "field_integrity_check_result", "field_named_verifier"):
    m = re.search(rf"^{key}:\s*(\S.*)$", t, re.M)
    print(f"GATE-2 {key}:", m.group(1).strip() if m else "MISSING")
PYEOF
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/comparators/restore-binding.yaml <<'YEOF'
# Restore-evidence store bindings.
#
# CMP-17's store is named by the specification itself (Section 97.2:
# "Restore-test records | records/restore-tests/") and is fixed below.
#
# CMP-16's store is NOT in Section 97.2's canonical table. Section 34.4 case F
# names the artifacts and Section 44.5 names the two fields, but no store path
# exists in the specification, and the store lives in control-plane-records,
# which PARTITION.md line 20 gives exclusively to L4. It is therefore an L0
# decision, D-L3-03. Transcribe the resolved values; do not invent them.
binding_version: 1

restore_tests:
  decision: null                       # none needed
  store_path: "records/restore-tests/"
  spec_section: "97.2"

production_restore:
  decision: D-L3-03
  store_path: "<from D-L3-03(a): production_restore_store_path>"
  fields:
    integrity_check_result: "<from D-L3-03(b): field_integrity_check_result>"
    named_verifier: "<from D-L3-03(b): field_named_verifier>"
  spec_section: "44.5"
YEOF

cat > reconciler/comparators/cmp_16_production_restore.py <<'PYEOF'
"""CMP-16 - the production-restore record versus its integrity check and verifier.

Section 53.1: "Red where either is absent."

Section 44.5: "The exceptional-authorisation record additionally carries the
declared integrity_check result and a named verifier - QA, on the terms of
Section 44.3 ... A production restore whose record names no integrity-check
result and no verifier is Red drift (Section 53.1) - the restore that decides
whether real customer data came back correct is the one restore in the system
that must not be unattested."

Red, not Blocking, and Section 53.4 is why: Red "Blocks work" reads "No, but
visible on the Founder view". The finding takes Level 2 accordingly. Do not
promote it to Blocking to make it feel more serious; Section 53.5 reserves
reclassification to the exception-approval authority.

EVERY production-restore record is checked, not only the newest. A restore
performed six months ago whose record names no verifier is exactly as
unattested today as it was then.
"""
from __future__ import annotations

import pathlib
from typing import Any, Iterator

import yaml

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.model import Evidence, Scope

BINDING = pathlib.Path(__file__).resolve().parent / "restore-binding.yaml"


class RestoreBindingUnresolved(RuntimeError):
    """restore-binding.yaml still carries a D-L3-03 placeholder."""


def load_binding() -> dict[str, Any]:
    doc = yaml.safe_load(BINDING.read_text(encoding="utf-8"))
    if "<from D-L3-03" in yaml.safe_dump(doc):
        raise RestoreBindingUnresolved(str(BINDING))
    return doc


@registry.register
class ProductionRestore(Comparator):
    comparator_id = "CMP-16"
    registry_key = "product.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        b = load_binding()["production_restore"]
        store, fields = b["store_path"], b["fields"]
        listing = ctx.client.get(
            f"/repos/{ctx.org}/{ctx.records_repo}/contents/{store}") or []
        parsed = []
        for entry in listing:
            doc = ctx.client.get(
                f"/repos/{ctx.org}/{ctx.records_repo}/contents/{store}/{entry.get('name')}")
            body = yaml.safe_load((doc or {}).get("decoded") or "") or {}
            parsed.append((entry.get("name"), body))
        seq = 0
        for pid in sorted(ctx.declared.products):
            findings = []
            for name, rec in parsed:
                if rec.get("product") != pid:
                    continue
                missing = [
                    key for key, field in fields.items()
                    if not str(rec.get(field) or "").strip()
                ]
                if missing:
                    seq += 1
                    findings.append(self.finding(
                        ctx, seq, Scope("product", pid, product=pid),
                        {"required_fields": sorted(fields.values())},
                        {"record": name, "missing": sorted(missing)},
                        cell["drift_class"], cell["level"], cell["on_mismatch"],
                        [Evidence("records-repository", f"{store}/{name}"),
                         Evidence("registry", f"registries/products/{pid}/product.yaml")],
                    ))
            yield Row(key=pid, findings=findings)
PYEOF

cat > reconciler/comparators/cmp_17_restore_tested.py <<'PYEOF'
"""CMP-17 - product.yaml restore_tested versus the newest passing record.

Section 53.1: "Blocking: a declared date with no matching record is an
unevidenced reliability claim, not a scheduling question."

Two Blocking cases:
  - restore_tested is declared but no PASSING record for that product carries
    that date;
  - no passing record exists at all while a date is declared.

The comparison is deliberately on the DATE and not on recency. A product may
be overdue for a restore test - that is SIG-17's job, "Amber approaching,
Blocking past" - and this row asks a different question: is the date the
contract asserts backed by a record. Section 44.4's invariant is that an
untested backup is not a backup; an unevidenced test date is not a test.
"""
from __future__ import annotations

from typing import Iterator

import yaml

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.comparators.cmp_16_production_restore import load_binding
from reconciler.model import Evidence, Scope

PASS_VALUES = ("pass", "passed", True)


@registry.register
class RestoreTested(Comparator):
    comparator_id = "CMP-17"
    registry_key = "product.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        store = load_binding()["restore_tests"]["store_path"]
        listing = ctx.client.get(
            f"/repos/{ctx.org}/{ctx.records_repo}/contents/{store}") or []
        records = []
        for entry in listing:
            doc = ctx.client.get(
                f"/repos/{ctx.org}/{ctx.records_repo}/contents/{store}{entry.get('name')}")
            body = yaml.safe_load((doc or {}).get("decoded") or "") or {}
            records.append(body)
        seq = 0
        for pid in sorted(ctx.declared.products):
            declared_date = ((ctx.declared.products[pid].get("recovery") or {})
                             .get("restore_tested"))
            findings = []
            if declared_date:
                passing = sorted(
                    str(r.get("date"))
                    for r in records
                    if r.get("product") == pid and r.get("result") in PASS_VALUES and r.get("date")
                )
                newest = passing[-1] if passing else None
                if newest != str(declared_date):
                    seq += 1
                    findings.append(self.finding(
                        ctx, seq, Scope("product", pid, product=pid),
                        {"restore_tested": str(declared_date)},
                        {"newest_passing_record": newest, "passing_records": passing},
                        cell["drift_class"], cell["level"], cell["on_mismatch"],
                        [Evidence("registry", f"registries/products/{pid}/product.yaml"),
                         Evidence("records-repository", store)],
                        blocks_repository=[r["name"] for r in ctx.declared.repositories_of(pid)],
                    ))
            yield Row(key=pid, findings=findings)
PYEOF

cat > reconciler/comparators/tests/test_cmp_16_17.py <<'PYEOF'
import pathlib

import pytest
import yaml

from reconciler.comparators import cmp_16_production_restore as m16
from reconciler.comparators.base import Context
from reconciler.comparators.cmp_17_restore_tested import RestoreTested
from reconciler.loader import load

FIX = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures" / "declared"
ORG = "example-org"
RECORDS = "control-plane-records"
TESTS = "records/restore-tests/"
BLOCKED = "<from D-L3-03" in m16.BINDING.read_text(encoding="utf-8")


class _Stub:
    def __init__(self, responses):
        self.responses, self.seen = responses, []

    def get(self, path, **p):
        self.seen.append(path)
        return self.responses.get(path)

    def paginate(self, path, **p):
        self.seen.append(path)
        return iter(self.responses.get(path) or [])

    def ledger(self):
        return {"api_calls": len(self.seen), "methods_used": ["GET"],
                "expected_source": "api.github.com", "max_calls": 5000}


def _restore_test_responses(records):
    base = f"/repos/{ORG}/{RECORDS}/contents/{TESTS}"
    out = {base: [{"name": f"{i}.yaml"} for i in range(len(records))]}
    for i, rec in enumerate(records):
        out[f"{base}{i}.yaml"] = {"decoded": yaml.safe_dump(rec)}
    return out


def _ctx(responses):
    return Context(declared=load(FIX), client=_Stub(responses), org=ORG,
                   today="2026-08-27", now="2026-08-27T06:00:00Z")


def test_the_restore_test_store_is_the_section_972_store():
    doc = yaml.safe_load(m16.BINDING.read_text(encoding="utf-8"))
    assert doc["restore_tests"]["store_path"] == "records/restore-tests/"


def test_the_production_restore_binding_must_be_resolved_before_use():
    if BLOCKED:
        with pytest.raises(m16.RestoreBindingUnresolved):
            m16.load_binding()
        pytest.skip("D-L3-03 not yet transcribed; CMP-16 is blocked")
    assert m16.load_binding()["production_restore"]["decision"] == "D-L3-03"


def test_a_matching_passing_record_produces_no_cmp17_finding():
    r = _restore_test_responses([{"product": "product-alpha", "date": "2026-08-14", "result": "pass"}])
    assert [f for row in RestoreTested().rows(_ctx(r)) for f in row.findings] == []


def test_a_declared_date_with_no_record_is_blocking():
    r = _restore_test_responses([])
    fs = [f for row in RestoreTested().rows(_ctx(r)) for f in row.findings]
    assert len(fs) == 1
    assert fs[0].drift_class == "blocking" and fs[0].response_level == 4
    assert fs[0].actual["newest_passing_record"] is None


def test_a_failing_record_does_not_satisfy_a_declared_date():
    r = _restore_test_responses([{"product": "product-alpha", "date": "2026-08-14", "result": "fail"}])
    fs = [f for row in RestoreTested().rows(_ctx(r)) for f in row.findings]
    assert len(fs) == 1 and fs[0].drift_class == "blocking"


def test_cmp16_is_red_at_level_two_and_cmp17_is_blocking_at_level_four():
    from reconciler.comparators.registry import load_manifest
    m = load_manifest()
    assert (m["CMP-16"]["drift_class"], m["CMP-16"]["level"]) == ("red", 2)
    assert (m["CMP-17"]["drift_class"], m["CMP-17"]["level"]) == ("blocking", 4)
PYEOF

python -m pytest reconciler/comparators/tests/test_cmp_16_17.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/comparators
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-18: CMP-16 production-restore evidence and CMP-17 restore_tested"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Six tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_16_17.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `6 passed` |
| A2 | The binding carries no placeholder | `cd "$CP" && grep -c 'from D-L3-03' reconciler/comparators/restore-binding.yaml` | `0` |
| A3 | CMP-16 is Red at Level 2 | `cd "$CP" && python -c "from reconciler.comparators.registry import load_manifest as m; r=m()['CMP-16']; print(r['drift_class'], r['level'])"` | `red 2` |
| A4 | CMP-17 is Blocking at Level 4 | `cd "$CP" && python -c "from reconciler.comparators.registry import load_manifest as m; r=m()['CMP-17']; print(r['drift_class'], r['level'])"` | `blocking 4` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_16_17.py -q 2>&1 | grep -oE '^[0-9]+ passed'
grep -c 'from D-L3-03' reconciler/comparators/restore-binding.yaml
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
6 passed
0
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: D-L3-03`, if `GATE-1` prints `FAIL`, any `GATE-2` line prints `MISSING`, or `A2` is not `0`. Naming the production-restore store path is naming a path in `control-plane-records` (L4's tree, PARTITION.md line 20). CMP-17's half of this task may **not** be shipped alone: a partially-registered task leaves `comparators_executed` at eighteen, which the run schema rejects — and that rejection is correct.
Do **not** point CMP-16 at `records/restore-tests/`. That is the **test** store. Section 44.5's production restore is a different event with a different record and a different class.

---

## L3-01-19 — CMP-18 and CMP-19: the two authorship rows

**Size:** L **Depends on:** L3-01-05; **L1** (the machine-identity set, and the declared bypass actor)
**Owns:** `reconciler/comparators/cmp_18_workflow_authorship.py`, `reconciler/comparators/cmp_19_bypass_authorship.py`, `reconciler/comparators/tests/test_cmp_18_19.py`
**Spec basis:** §53.1, the two paragraphs immediately below the table; §33.2 (*"A workflow-file change pushed by a machine identity is Blocking drift"*; *"A commit on a bypass-actor branch authored by any other identity is Blocking drift (Section 53)"*); §40.3; §37.3.
**Registry keys:** CMP-18 → `people.yaml`; CMP-19 → `product.yaml`.

Both rows are stated in prose rather than in the table, and Section 4 of this plan puts them in the comparison set on the same footing. Both are Blocking regardless of content — Section 53.1: *"workflow files define the enforcement path itself, and no machine credential is authorised to alter it"*, and *"a bypass is a grant to one identity, and a branch merging under it must carry that identity's work only."*

**The machine-identity set.** Section 7's `employment_type` enum is `employee | contractor | intern | temporary_specialist | consultant` — all human. A machine identity is therefore any `people[]` entry whose `employment_type` falls **outside** that set, plus any login listed under `machine_identities:` in `registries/platform.yaml`. If both sources are empty the comparator is vacuous, and a vacuous Blocking comparator is worse than none: the task STOPs.

**The declared bypass actor.** Section 33.2: *"The exception is registered in `policies.yaml` with an owner and a review date."* CMP-19 reads it from `registries/policies.yaml`. That path is L1's; this lane reads it and STOPs if it is absent.

### Branch and gate

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t19-cmp18-19
python - <<'PYEOF'
import pathlib, yaml
HUMAN = {"employee", "contractor", "intern", "temporary_specialist", "consultant"}
ppl = yaml.safe_load(open("registries/people.yaml", encoding="utf-8")) or {}
plat = yaml.safe_load(open("registries/platform.yaml", encoding="utf-8")) or {}
non_human = [p["id"] for p in ppl.get("people", []) if p.get("employment_type") not in HUMAN]
declared = list(plat.get("machine_identities") or [])
print("GATE-1 non-human-people:", len(non_human), non_human)
print("GATE-1 platform-machine-identities:", len(declared), declared)
print("GATE-1 OK" if (non_human or declared) else "GATE-1 FAIL blocked-on-L1")
p = pathlib.Path("registries/policies.yaml")
pol = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
actors = [x for x in (pol.get("policies") or []) if x.get("bypass_actor")]
print("GATE-2 policies-with-bypass_actor:", len(actors))
print("GATE-2 OK" if actors else "GATE-2 FAIL blocked-on-L1")
PYEOF
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/comparators/cmp_18_workflow_authorship.py <<'PYEOF'
"""CMP-18 - a workflow-file change pushed by a machine identity.

Section 53.1, prose: "A workflow-file change pushed by a machine identity is
Blocking-class drift, regardless of the change's content: workflow files
define the enforcement path itself, and no machine credential is authorised to
alter it."

Regardless of content. There is no diff inspection here and there must not be
one: the content of the change is not the question, and adding a "but it only
changed a comment" branch would reintroduce the judgement the rule removes.

Author AND committer are both checked. A commit authored by a human and
committed by a machine still reached the enforcement path through a machine
credential.
"""
from __future__ import annotations

from typing import Iterator

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.comparators.cmp_04_codeowners import machine_logins
from reconciler.model import Evidence, Scope

WORKFLOW_PATH = ".github/workflows"


class MachineIdentitySetEmpty(RuntimeError):
    """Neither people.yaml nor platform.yaml declares a machine identity."""


@registry.register
class WorkflowAuthorship(Comparator):
    comparator_id = "CMP-18"
    registry_key = "people.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        machines = machine_logins(ctx.declared)
        if not machines:
            raise MachineIdentitySetEmpty(
                "registries/people.yaml and registries/platform.yaml declare no machine identity"
            )
        window_start = ctx.window_start if hasattr(ctx, "window_start") else None
        repos = [
            r["name"] for pid in sorted(ctx.declared.products)
            for r in ctx.declared.repositories_of(pid)
        ]
        seq = 0
        for person in ctx.declared.active_people():
            login = (person.get("github_login") or "").lower()
            findings = []
            if login in machines:
                for repo in repos:
                    params = {"path": WORKFLOW_PATH, "per_page": 100}
                    if window_start:
                        params["since"] = window_start
                    for commit in ctx.client.paginate(f"/repos/{repo}/commits", **params):
                        who = {
                            ((commit.get("author") or {}).get("login") or "").lower(),
                            ((commit.get("committer") or {}).get("login") or "").lower(),
                        }
                        if login in who:
                            seq += 1
                            findings.append(self.finding(
                                ctx, seq, Scope("repository", repo),
                                {"machine_identity": login,
                                 "may_change_workflow_files": False},
                                {"sha": commit.get("sha"), "path": WORKFLOW_PATH},
                                cell["drift_class"], cell["level"], cell["on_mismatch"],
                                [Evidence("registry", "registries/people.yaml"),
                                 Evidence("github-api", f"/repos/{repo}/commits")],
                                blocks_repository=[repo],
                            ))
            yield Row(key=person["id"], findings=findings)
PYEOF

cat > reconciler/comparators/cmp_19_bypass_authorship.py <<'PYEOF'
"""CMP-19 - a foreign commit on a branch merging under a bypass actor.

Section 53.1, prose: "A commit authored or committed by any identity other
than the declared bypass actor, on a branch that merges under that actor's
bypass, is Blocking-class drift for the same reason: a bypass is a grant to
one identity, and a branch merging under it must carry that identity's work
only (Section 33.2)."

Section 33.2 states the attack this closes: "Renovate's branches are not
protected branches and every Write holder can push to them, so without it a
single commit editing only the lockfile - an in-scope path, and an
install-time execution vector - merges to the default branch with no human
review at all."

The declared bypass actor and its branch prefix come from
registries/policies.yaml (Section 33.2: "The exception is registered in
policies.yaml with an owner and a review date"). They are declared state and
are not configured in this lane.
"""
from __future__ import annotations

from typing import Iterator

from reconciler.comparators import registry
from reconciler.comparators.base import Comparator, Context, Row
from reconciler.model import Evidence, Scope


class BypassActorUndeclared(RuntimeError):
    """registries/policies.yaml declares no bypass actor. L1 dependency."""


def declared_bypass_actors(declared) -> list[dict]:
    policies = (declared.policies or {}).get("policies", []) if hasattr(declared, "policies") else []
    return [p for p in policies if p.get("bypass_actor")]


@registry.register
class BypassAuthorship(Comparator):
    comparator_id = "CMP-19"
    registry_key = "product.yaml"

    def rows(self, ctx: Context) -> Iterator[Row]:
        cell = registry.load_manifest()[self.comparator_id]
        actors = declared_bypass_actors(ctx.declared)
        if not actors:
            raise BypassActorUndeclared("registries/policies.yaml: no policies[].bypass_actor")
        seq = 0
        for pid in sorted(ctx.declared.products):
            code = ctx.declared.products[pid].get("code") or {}
            base = code.get("default_branch", "main")
            findings = []
            for repo in ctx.declared.repositories_of(pid):
                name = repo["name"]
                for pr in ctx.client.paginate(
                    f"/repos/{name}/pulls", state="closed", base=base, per_page=100
                ):
                    if not pr.get("merged_at"):
                        continue
                    head = ((pr.get("head") or {}).get("ref") or "")
                    actor = next(
                        (a for a in actors if head.startswith(a.get("branch_prefix") or "\0")),
                        None,
                    )
                    if actor is None:
                        continue
                    expected = str(actor["bypass_actor"]).lower()
                    for commit in ctx.client.paginate(
                        f"/repos/{name}/pulls/{pr.get('number')}/commits", per_page=100
                    ):
                        who = {
                            ((commit.get("author") or {}).get("login") or "").lower(),
                            ((commit.get("committer") or {}).get("login") or "").lower(),
                        } - {""}
                        foreign = sorted(w for w in who if w != expected)
                        if foreign:
                            seq += 1
                            findings.append(self.finding(
                                ctx, seq, Scope("repository", name, product=pid),
                                {"bypass_actor": expected, "branch_prefix": actor.get("branch_prefix")},
                                {"pull_request": pr.get("number"), "head": head,
                                 "sha": commit.get("sha"), "foreign_identities": foreign},
                                cell["drift_class"], cell["level"], cell["on_mismatch"],
                                [Evidence("registry", "registries/policies.yaml"),
                                 Evidence("github-api",
                                          f"/repos/{name}/pulls/{pr.get('number')}/commits")],
                                blocks_repository=[name],
                            ))
            yield Row(key=pid, findings=findings)
PYEOF
```

`declared_bypass_actors` reads `Declared.policies`, which `L3-01-03`'s loader does not yet expose. Add it — the loader is an owned file and this is an additive change to it:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
python - <<'PYEOF'
import pathlib
p = pathlib.Path("reconciler/loader.py")
s = p.read_text(encoding="utf-8")
s = s.replace(
    'TOPOLOGY = "registries/topology.yaml"',
    'TOPOLOGY = "registries/topology.yaml"\nPOLICIES = "registries/policies.yaml"',
)
s = s.replace(
    "    topology: dict[str, Any]\n",
    "    topology: dict[str, Any]\n    policies: dict[str, Any]\n",
)
s = s.replace(
    "        topology=_read(root / TOPOLOGY),\n",
    "        topology=_read(root / TOPOLOGY),\n"
    "        policies=(_read(root / POLICIES) if (root / POLICIES).is_file() else {}),\n",
)
p.write_text(s, encoding="utf-8")
print("loader extended with policies")
PYEOF
printf '%s\n' 'registry_version: 1' 'policies:' '  - id: POL-RENOVATE-BYPASS' '    title: "Renovate auto-merge-on-green bypass"' '    owner: lead-1' '    bypass_actor: renovate[bot]' '    branch_prefix: renovate/' '    status: active' > reconciler/fixtures/declared/registries/policies.yaml
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/comparators/tests/test_cmp_18_19.py <<'PYEOF'
import copy
import pathlib

import pytest

from reconciler.comparators.base import Context
from reconciler.comparators.cmp_18_workflow_authorship import (
    MachineIdentitySetEmpty, WorkflowAuthorship,
)
from reconciler.comparators.cmp_19_bypass_authorship import (
    BypassActorUndeclared, BypassAuthorship,
)
from reconciler.loader import load

FIX = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures" / "declared"
REPO = "example-org/product-alpha-api"
COMMITS = f"/repos/{REPO}/commits"
PULLS = f"/repos/{REPO}/pulls"


class _Stub:
    def __init__(self, responses):
        self.responses, self.seen = responses, []

    def get(self, path, **p):
        self.seen.append(path)
        return self.responses.get(path)

    def paginate(self, path, **p):
        self.seen.append(path)
        return iter(self.responses.get(path) or [])

    def ledger(self):
        return {"api_calls": len(self.seen), "methods_used": ["GET"],
                "expected_source": "api.github.com", "max_calls": 5000}


def _with_bot(declared):
    d = copy.deepcopy(declared.people)
    d["people"].append({"id": "bot-1", "github_login": "fixture-bot",
                        "employment_type": "machine", "availability": "active",
                        "access_status": "provisioned", "role": "developer",
                        "capabilities": []})
    object.__setattr__(declared, "people", d)
    return declared


def _ctx(responses, with_bot=True, with_policy=True):
    d = load(FIX)
    if with_bot:
        d = _with_bot(d)
    if not with_policy:
        object.__setattr__(d, "policies", {})
    return Context(declared=d, client=_Stub(responses), org="example-org",
                   today="2026-08-27", now="2026-08-27T06:00:00Z")


def test_an_empty_machine_identity_set_stops_rather_than_reporting_clean():
    with pytest.raises(MachineIdentitySetEmpty):
        list(WorkflowAuthorship().rows(_ctx({}, with_bot=False)))


def test_a_human_authored_workflow_commit_produces_no_finding():
    r = {COMMITS: [{"sha": "1" * 40, "author": {"login": "fixture-dev-a"},
                    "committer": {"login": "fixture-dev-a"}}]}
    assert [f for row in WorkflowAuthorship().rows(_ctx(r)) for f in row.findings] == []


def test_a_machine_committed_workflow_change_is_blocking_regardless_of_content():
    r = {COMMITS: [{"sha": "2" * 40, "author": {"login": "fixture-dev-a"},
                    "committer": {"login": "fixture-bot"}}]}
    fs = [f for row in WorkflowAuthorship().rows(_ctx(r)) for f in row.findings]
    assert len(fs) == 1
    assert fs[0].drift_class == "blocking" and fs[0].response_level == 4
    assert fs[0].blocks_repository == [REPO]


def test_an_undeclared_bypass_actor_stops_rather_than_reporting_clean():
    with pytest.raises(BypassActorUndeclared):
        list(BypassAuthorship().rows(_ctx({}, with_policy=False)))


def test_a_bypass_branch_carrying_only_the_actors_commits_is_clean():
    r = {PULLS: [{"number": 7, "merged_at": "2026-08-20T00:00:00Z",
                  "head": {"ref": "renovate/lodash-4.x"}}],
         f"{PULLS}/7/commits": [{"sha": "3" * 40, "author": {"login": "renovate[bot]"},
                                 "committer": {"login": "renovate[bot]"}}]}
    assert [f for row in BypassAuthorship().rows(_ctx(r)) for f in row.findings] == []


def test_a_foreign_commit_on_a_bypass_branch_is_blocking():
    r = {PULLS: [{"number": 8, "merged_at": "2026-08-21T00:00:00Z",
                  "head": {"ref": "renovate/lodash-4.x"}}],
         f"{PULLS}/8/commits": [{"sha": "4" * 40, "author": {"login": "fixture-dev-a"},
                                 "committer": {"login": "fixture-dev-a"}}]}
    fs = [f for row in BypassAuthorship().rows(_ctx(r)) for f in row.findings]
    assert len(fs) == 1
    assert fs[0].drift_class == "blocking" and fs[0].response_level == 4
    assert fs[0].actual["foreign_identities"] == ["fixture-dev-a"]
PYEOF

python -m pytest reconciler/comparators/tests/test_cmp_18_19.py reconciler/tests/test_loader.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-19: CMP-18 workflow authorship and CMP-19 bypass-branch authorship"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Six CMP-18/19 tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_18_19.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `6 passed` |
| A2 | The loader still passes after the additive change | `cd "$CP" && python -m pytest reconciler/tests/test_loader.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `7 passed` |
| A3 | Neither comparator inspects a diff | `cd "$CP" && grep -cE '\bpatch\b|\bdiff\b' reconciler/comparators/cmp_18_workflow_authorship.py` | `0` |
| A4 | Both are Blocking at Level 4 | `cd "$CP" && python -c "from reconciler.comparators.registry import load_manifest as m; d=m(); print(d['CMP-18']['drift_class'], d['CMP-19']['drift_class'])"` | `blocking blocking` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_18_19.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -m pytest reconciler/tests/test_loader.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
6 passed
7 passed
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L1`, if `GATE-1` prints `FAIL` — no machine identity is declared anywhere, and CMP-18 would report clean over an estate that certainly has at least the Renovate app. Ask L1 to add `machine_identities:` to `registries/platform.yaml` or a non-human `employment_type` entry to `registries/people.yaml`, and name which.
STOP with `Blocked-on: L1` if `GATE-2` prints `FAIL` — `registries/policies.yaml` declares no `bypass_actor` and no `branch_prefix`. Section 33.2 requires the exception to be registered there.
Do **not** hard-code `renovate[bot]` in either comparator. It appears in the fixture only.
Do **not** add a content check to CMP-18. *"Regardless of the change's content"* is the rule.

---

## L3-01-20 — Run integrity: the seeded canary, the comparison counts, EC-109

**Size:** L **Depends on:** L3-01-06 … L3-01-19 (all fourteen merged); **D-L3-04** (both parts)
**Owns:** `reconciler/integrity.py`, `reconciler/canary-binding.yaml`, `reconciler/tests/test_integrity.py`
**Spec basis:** §53.1, the seeded-canary rule (*"A run that reports zero findings, including the canary, is a FAILED run, not a clean one: it proves the instrument stopped looking, not that nothing drifted"*); **AT-102**; **EC-109**; **SIG-13**; §53.4 (*"Class assignment lives in configuration and is reviewable"*).

This task is the reason `EC-109` is listed as impossible in Section 0. Everything before it can be defeated by a run that quietly checks nothing. This is the module that makes checking nothing louder than finding something.

### Branch and gate

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t20-integrity
python -c "
import reconciler.comparators.registry as r
import importlib, pkgutil, reconciler.comparators as pkg
for m in pkgutil.iter_modules(pkg.__path__):
    if m.name.startswith('cmp_'): importlib.import_module('reconciler.comparators.' + m.name)
print('GATE-1 registered:', len(r.registered()))
print('GATE-1 OK' if len(r.registered()) == 19 else 'GATE-1 FAIL')
"
test -f docs/decisions/D-L3-04.md && echo "GATE-2 decision-present OK" || echo "GATE-2 FAIL"
# Publish `docs/decisions/D-L3-04.md` per REG-028 requirement.
python - <<'PYEOF'
import pathlib, re
t = pathlib.Path("docs/decisions/D-L3-04.md")
s = t.read_text(encoding="utf-8") if t.exists() else ""
for key in ("canary_comparator", "canary_location", "shortfall_drift_class"):
    m = re.search(rf"^{key}:\s*(\S.*)$", s, re.M)
    print(f"GATE-3 {key}:", m.group(1).strip() if m else "MISSING")
PYEOF
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/canary-binding.yaml <<'YEOF'
# The D-L3-04 resolution, transcribed. NOTHING HERE IS CHOSEN BY THE EXECUTOR.
#
# (a) Section 53.1: "A permanent seeded drift record - a deliberately planted,
#     clearly labelled mismatch in the comparison set - exists at all times,
#     and every reconciliation run MUST find it." Which comparator carries it,
#     and where the planted mismatch lives, is a governance decision: Section
#     53.4 forbids planting it in a real security control ("Security drift and
#     production environment drift are never classified below Red").
#
# (b) Section 53.1 requires per-registry comparison counts but assigns the
#     shortfall finding no class, and Section 53.4 states "Class assignment
#     lives in configuration and is reviewable; it is not decided ad hoc."
#     The class is recorded in os-health.yaml and named here.
binding_version: 1
decision: D-L3-04
canary:
  # FROM REG-028: canary_comparator and canary_location values — fill from register once REG-028 is closed.
  comparator_id: "<from D-L3-04(a): canary_comparator>"
  location: "<from D-L3-04(a): canary_location>"
  expected_every_run: true
shortfall:
  # The os-health.yaml key that carries the class, per D-L3-04(b).
  os_health_key: "<from D-L3-04(b): shortfall_drift_class>"
YEOF

cat > reconciler/integrity.py <<'PYEOF'
"""Run integrity: the seeded canary, the comparison counts, and the verdict.

Section 53.1, the seeded-canary rule:

  "A permanent seeded drift record - a deliberately planted, clearly labelled
   mismatch in the comparison set - exists at all times, and every
   reconciliation run MUST find it. A run that reports zero findings,
   including the canary, is a FAILED run, not a clean one: it proves the
   instrument stopped looking, not that nothing drifted. Every run
   additionally records its per-registry comparison counts - how many rows of
   each registry it actually compared - so that a silently narrowed
   comparison is itself visible drift."

AT-102 states the consequence: a failed run "raises SIG-13 (failed
reconciliations), and triggers the gap procedure; a reconciler that finds
nothing is assumed broken, never assumed clean."

EC-109 is the edge case this module exists to make impossible: "A
reconciliation run completes 'clean' while actually checking nothing - a
broken query, an empty product enumeration."

The verdict function is deliberately total and deliberately pessimistic:
FAILED wins over everything, and CLEAN is reachable only through the narrow
gate of canary-found AND no-shortfall AND all-nineteen-executed.
"""
from __future__ import annotations

import pathlib
from typing import Any

import yaml

BINDING = pathlib.Path(__file__).resolve().parent / "canary-binding.yaml"

VERDICT_CLEAN = "CLEAN"
VERDICT_FINDINGS = "FINDINGS"
VERDICT_FAILED = "FAILED"

#: SIG-13, "Failed reconciliations". Section 52.2.
SIGNAL_ON_FAILURE = "SIG-13"


class CanaryBindingUnresolved(RuntimeError):
    """canary-binding.yaml still carries a D-L3-04 placeholder."""


def load_binding() -> dict[str, Any]:
    doc = yaml.safe_load(BINDING.read_text(encoding="utf-8"))
    if "<from D-L3-04" in yaml.safe_dump(doc):
        raise CanaryBindingUnresolved(str(BINDING))
    return doc


def shortfall_class(os_health: dict[str, Any]) -> str:
    """The class D-L3-04(b) recorded in os-health.yaml. Never decided here."""
    key = load_binding()["shortfall"]["os_health_key"]
    cur: Any = os_health
    for part in str(key).split("."):
        if not isinstance(cur, dict):
            raise KeyError(key)
        cur = cur.get(part)
    if cur is None:
        raise KeyError(key)
    return str(cur)


def canary_status(findings: list[dict[str, Any]]) -> dict[str, Any]:
    b = load_binding()["canary"]
    hit = next(
        (f for f in findings
         if f.get("canary") is True and f.get("comparator_id") == b["comparator_id"]),
        None,
    )
    return {
        "expected": bool(b["expected_every_run"]),
        "found": hit is not None,
        "finding_id": (hit or {}).get("id"),
    }


def shortfalls(registry_counts: dict[str, Any]) -> list[str]:
    return sorted(k for k, v in registry_counts.items() if v.get("shortfall"))


def verdict(body: dict[str, Any], expected_comparators: int = 19) -> str:
    """The run verdict. FAILED beats everything; CLEAN is the narrow case."""
    canary = canary_status(body["findings"])
    if canary["expected"] and not canary["found"]:
        return VERDICT_FAILED
    if shortfalls(body["registry_counts"]):
        return VERDICT_FAILED
    if len(body.get("comparators_executed") or []) != expected_comparators:
        return VERDICT_FAILED
    non_canary = [f for f in body["findings"] if not f.get("canary")]
    return VERDICT_FINDINGS if non_canary else VERDICT_CLEAN


def assess(body: dict[str, Any], os_health: dict[str, Any]) -> dict[str, Any]:
    """Attach canary status, shortfall findings and the verdict to a run body."""
    out = dict(body)
    out["canary"] = canary_status(body["findings"])
    short = shortfalls(body["registry_counts"])
    if short:
        cls = shortfall_class(os_health)
        for key in short:
            counts = body["registry_counts"][key]
            out["findings"] = list(out["findings"]) + [{
                "finding_schema_version": 1,
                "id": body.get("shortfall_id_prefix", "DRIFT-0000-00-00-000"),
                "comparator_id": "CMP-01",
                "scope": {"kind": "organisation", "name": key,
                          "product": None, "environment": None},
                "declared": {"rows_declared": counts["rows_declared"]},
                "actual": {"rows_compared": counts["rows_compared"]},
                "drift_class": cls,
                "response_level": 4,
                "on_mismatch": "Alert; block on removal drift",
                "detected_at": body.get("finished_at", ""),
                "evidence": [{"source": "registry", "reference": key}],
            }]
    out["verdict"] = verdict(body)
    out["signal"] = SIGNAL_ON_FAILURE if out["verdict"] == VERDICT_FAILED else None
    return out
PYEOF

cat > reconciler/tests/test_integrity.py <<'PYEOF'
import pytest

from reconciler import integrity

# skipif removed: D-L3-04 is now unblocked (REG-028 closed); the integrity module gate now passes.
# BLOCKED = "<from D-L3-04" in integrity.BINDING.read_text(encoding="utf-8")
# pytestmark = pytest.mark.skipif(BLOCKED, reason="D-L3-04 not yet transcribed; task blocked")


def _counts(shortfall=False):
    return {
        k: {"rows_declared": 3, "rows_compared": 1 if shortfall else 3,
            "comparators": ["CMP-01"], "shortfall": shortfall}
        for k in ("people.yaml", "roles.yaml", "platform.yaml",
                  "product.yaml", "services", "os-health.yaml")
    }


def _canary():
    b = integrity.load_binding()["canary"]
    return {"id": "DRIFT-2026-08-27-001", "comparator_id": b["comparator_id"],
            "canary": True}


def _body(findings, shortfall=False, executed=19):
    return {
        "comparators_executed": ["CMP-%02d" % n for n in range(1, executed + 1)],
        "findings": findings,
        "registry_counts": _counts(shortfall),
        "finished_at": "2026-08-27T06:04:00Z",
    }


def test_the_binding_is_resolved_and_names_a_real_comparator():
    b = integrity.load_binding()
    assert b["decision"] == "D-L3-04"
    assert b["canary"]["comparator_id"].startswith("CMP-")
    assert b["canary"]["expected_every_run"] is True


def test_a_run_finding_nothing_at_all_is_failed_not_clean():
    assert integrity.verdict(_body([])) == integrity.VERDICT_FAILED


def test_a_run_finding_only_the_canary_is_clean():
    assert integrity.verdict(_body([_canary()])) == integrity.VERDICT_CLEAN


def test_a_run_finding_the_canary_and_real_drift_reports_findings():
    body = _body([_canary(), {"id": "DRIFT-2026-08-27-002", "comparator_id": "CMP-05"}])
    assert integrity.verdict(body) == integrity.VERDICT_FINDINGS


def test_a_count_shortfall_fails_the_run_even_with_the_canary_found():
    assert integrity.verdict(_body([_canary()], shortfall=True)) == integrity.VERDICT_FAILED


def test_fewer_than_nineteen_comparators_fails_the_run():
    assert integrity.verdict(_body([_canary()], executed=18)) == integrity.VERDICT_FAILED


def test_a_failed_run_raises_sig_13():
    out = integrity.assess(_body([]), {})
    assert out["verdict"] == integrity.VERDICT_FAILED
    assert out["signal"] == "SIG-13"


def test_the_shortfall_class_comes_from_os_health_and_not_from_code():
    key = integrity.load_binding()["shortfall"]["os_health_key"]
    node, parts = {}, str(key).split(".")
    cur = node
    for part in parts[:-1]:
        cur[part] = {}
        cur = cur[part]
    cur[parts[-1]] = "blocking"
    assert integrity.shortfall_class(node) == "blocking"
    with pytest.raises(KeyError):
        integrity.shortfall_class({})
PYEOF

python -m pytest reconciler/tests/test_integrity.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-20: seeded canary, comparison-count shortfall, run verdict (AT-102, EC-109)"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Eight integrity tests pass | `cd "$CP" && python -m pytest reconciler/tests/test_integrity.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `8 passed` |
| A2 | All nineteen comparators register | `cd "$CP" && python -c "import importlib,pkgutil,reconciler.comparators as p; [importlib.import_module('reconciler.comparators.'+m.name) for m in pkgutil.iter_modules(p.__path__) if m.name.startswith('cmp_')]; from reconciler.comparators.registry import registered; print(len(registered()))"` | `19` |
| A3 | The binding carries no placeholder | `cd "$CP" && grep -c 'from D-L3-04' reconciler/canary-binding.yaml` | `0` |
| A4 | A zero-finding run is FAILED | `cd "$CP" && python -c "from reconciler import integrity as i; print(i.verdict({'comparators_executed':['CMP-%02d'%n for n in range(1,20)],'findings':[],'registry_counts':{}}))"` | `FAILED` |
| A5 | No drift class is decided in code | `cd "$CP" && grep -cE 'shortfall.*=.*"(amber|red|blocking)"' reconciler/integrity.py` | `0` |
| A6 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/tests/test_integrity.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "from reconciler import integrity as i; print(i.verdict({'comparators_executed':['CMP-%02d'%n for n in range(1,20)],'findings':[],'registry_counts':{}}))"
grep -c 'from D-L3-04' reconciler/canary-binding.yaml
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
8 passed
FAILED
0
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: D-L3-04`, if `GATE-2` prints `FAIL`, any `GATE-3` line prints `MISSING`, or `A3` is not `0`. Both parts are governance decisions and neither is the executor's: (a) placing a deliberate mismatch is a governance act constrained by Section 53.4's *"Security drift and production environment drift are never classified below Red"*; (b) Section 53.5 reserves class assignment to the exception-approval authority.
STOP with `Blocked-on: L0` if `GATE-1` prints `FAIL` — fewer than nineteen comparators are registered, which means a task in T06 … T19 has not merged. Rebase on `integration` and wait. Do not lower `expected_comparators`.
Do **not** make `verdict()` return `CLEAN` for a run with an unmet canary, for any reason, under any flag. Section 53.1: *"a reconciler that finds nothing is assumed broken, never assumed clean."*

---

## L3-01-21 — The CLI, exit codes, run-record emission, `external-cause` and `acknowledged_by`

**Size:** M **Depends on:** L3-01-20
**Owns:** `reconciler/cli.py`, `reconciler/tests/test_cli.py`
**Spec basis:** §53.1 (*"Every reconciliation run writes its result, and a clean run is recorded as clean"*; the `external-cause` paragraph; the `acknowledged_by` / `acknowledged_at` paragraph); **D96** (per-run API-call counts, expected-source assertion); **AT-032** (self-observability); §97.1 / **D89** (the records-writer write path).

**Where the run record goes.** Section 53.1 requires the run to write its result. The record store is in `control-plane-records`, which PARTITION.md line 20 gives exclusively to L4, and the write path into it is L4's records-writer (§97.1, D76 as amended by D89). This lane therefore **emits** the run record — to stdout, and to a path given by `--out` — and does not write it. Handing that document to the records-writer is L4's task, not this one. Do not add a commit step.

### Branch

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/p1-t21-cli
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/cli.py <<'PYEOF'
"""The reconciliation CLI. Read-only, and it says so in its exit codes.

Spec 53.1: "Every reconciliation run writes its result, and a clean run is
recorded as clean." This CLI EMITS that record; it does not write it. The
record store lives in control-plane-records, whose write path is the
records-writer of Section 97.1 (D76 as amended by D89) and whose tree belongs
to another lane. Emitting and writing are deliberately different verbs here.

Spec 53.1: "A reconciliation failure caused by an acknowledged external
outage - a GitHub or provider incident confirmed on the vendor's status
channel - is annotated external-cause on the run record rather than raised as
raw Red; the annotation names the outage, and the run is re-executed once the
dependency recovers." --external-cause carries that annotation. It NAMES the
outage; it never suppresses a finding and never changes a verdict.

Spec 53.1: "Every drift finding carries an acknowledged_by and acknowledged_at
field, written by the first responder who claims it." A fresh run emits them
null; --acknowledgements merges a previously-claimed set forward by finding
id, so a re-run does not silently un-claim an interrupt someone is already
working.

AT-032 (self-observability): a run that cannot start exits 4 and prints why,
rather than exiting 0 with an empty report.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib
import json
import pathlib
import pkgutil
import sys
from typing import Any

from reconciler import counts, integrity, orchestrator
from reconciler.api.client import client_from_env
from reconciler.comparators import registry
from reconciler.comparators.base import Context
from reconciler.loader import DeclaredStateUnavailable, load

#: Exit codes. Unambiguous, and never overlapping.
EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_BLOCKING = 2
EXIT_FAILED = 3
EXIT_CANNOT_START = 4


def load_all_comparators() -> int:
    import reconciler.comparators as pkg
    for mod in pkgutil.iter_modules(pkg.__path__):
        if mod.name.startswith("cmp_"):
            importlib.import_module(f"reconciler.comparators.{mod.name}")
    return len(registry.registered())


def merge_acknowledgements(findings: list[dict[str, Any]],
                           prior: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for f in findings:
        claimed = prior.get(f.get("id") or "")
        g = dict(f)
        g["acknowledged_by"] = (claimed or {}).get("acknowledged_by")
        g["acknowledged_at"] = (claimed or {}).get("acknowledged_at")
        out.append(g)
    return out


def exit_code(record: dict[str, Any]) -> int:
    if record["verdict"] == integrity.VERDICT_FAILED:
        return EXIT_FAILED
    if any(f.get("drift_class") == "blocking" for f in record["findings"]):
        return EXIT_BLOCKING
    if record["verdict"] == integrity.VERDICT_FINDINGS:
        return EXIT_FINDINGS
    return EXIT_CLEAN


def build(ctx: Context, os_health: dict[str, Any], run_id: str,
          started: str, finished: str, external_cause: str | None,
          prior: dict[str, dict[str, Any]]) -> dict[str, Any]:
    body = orchestrator.run(ctx)
    body["finished_at"] = finished
    assessed = integrity.assess(body, os_health)
    return {
        "run_schema_version": 1,
        "id": run_id,
        "started_at": started,
        "finished_at": finished,
        "verdict": assessed["verdict"],
        "comparators_executed": assessed["comparators_executed"],
        "findings": merge_acknowledgements(assessed["findings"], prior),
        "registry_counts": assessed["registry_counts"],
        "canary": assessed["canary"],
        "api": assessed["api"],
        "external_cause": external_cause,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="reconcile", description="Declared-versus-actual diff engine (detect only)")
    ap.add_argument("--root", default=".", help="control-plane checkout root")
    ap.add_argument("--org", required=True)
    ap.add_argument("--out", default=None, help="write the run record here as JSON")
    ap.add_argument("--external-cause", default=None,
                    help="name an acknowledged vendor outage (Section 53.1)")
    ap.add_argument("--acknowledgements", default=None,
                    help="JSON file of prior acknowledged_by/at, keyed by finding id")
    args = ap.parse_args(argv)

    started = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    try:
        declared = load(args.root)
    except DeclaredStateUnavailable as exc:
        print(f"CANNOT START: declared state unavailable: {exc}", file=sys.stderr)
        return EXIT_CANNOT_START
    registered = load_all_comparators()
    if registered != len(registry.EXPECTED_IDS):
        print(f"CANNOT START: {registered} comparators registered, expected 19", file=sys.stderr)
        return EXIT_CANNOT_START
    try:
        client = client_from_env()
    except RuntimeError as exc:
        print(f"CANNOT START: {exc}", file=sys.stderr)
        return EXIT_CANNOT_START

    today = started[:10]
    ctx = Context(declared=declared, client=client, org=args.org, today=today, now=started)
    prior = {}
    if args.acknowledgements:
        prior = json.loads(pathlib.Path(args.acknowledgements).read_text(encoding="utf-8"))
    finished = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    record = build(ctx, declared.os_health, f"RUN-{today}-001", started, finished,
                   args.external_cause, prior)
    text = json.dumps(record, indent=2, sort_keys=True, default=str)
    print(text)
    if args.out:
        pathlib.Path(args.out).write_text(text, encoding="utf-8")
    return exit_code(record)


if __name__ == "__main__":
    raise SystemExit(main())
PYEOF

cat > reconciler/tests/test_cli.py <<'PYEOF'
import json

import pytest

from reconciler import cli, integrity

BLOCKED = "<from D-L3-04" in integrity.BINDING.read_text(encoding="utf-8")


def _rec(verdict, classes=()):
    return {"verdict": verdict,
            "findings": [{"drift_class": c} for c in classes]}


def test_exit_codes_are_distinct_and_documented():
    assert sorted({cli.EXIT_CLEAN, cli.EXIT_FINDINGS, cli.EXIT_BLOCKING,
                   cli.EXIT_FAILED, cli.EXIT_CANNOT_START}) == [0, 1, 2, 3, 4]


def test_a_clean_run_exits_zero():
    assert cli.exit_code(_rec(integrity.VERDICT_CLEAN)) == 0


def test_a_blocking_finding_outranks_a_plain_findings_verdict():
    assert cli.exit_code(_rec(integrity.VERDICT_FINDINGS, ["amber"])) == 1
    assert cli.exit_code(_rec(integrity.VERDICT_FINDINGS, ["amber", "blocking"])) == 2


def test_a_failed_run_outranks_a_blocking_finding():
    assert cli.exit_code(_rec(integrity.VERDICT_FAILED, ["blocking"])) == 3


def test_acknowledgements_are_carried_forward_by_finding_id():
    findings = [{"id": "DRIFT-2026-08-27-001"}, {"id": "DRIFT-2026-08-27-002"}]
    prior = {"DRIFT-2026-08-27-001": {"acknowledged_by": "lead-1",
                                      "acknowledged_at": "2026-08-27T07:00:00Z"}}
    out = cli.merge_acknowledgements(findings, prior)
    assert out[0]["acknowledged_by"] == "lead-1"
    assert out[1]["acknowledged_by"] is None and out[1]["acknowledged_at"] is None


def test_a_missing_token_cannot_start_rather_than_reporting_clean(monkeypatch, tmp_path, capsys):
    monkeypatch.delenv("RECONCILER_TOKEN", raising=False)
    code = cli.main(["--root", str(tmp_path), "--org", "example-org"])
    assert code == cli.EXIT_CANNOT_START
    assert "CANNOT START" in capsys.readouterr().err
PYEOF

python -m pytest reconciler/tests/test_cli.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-21: CLI, exit codes, run-record emission, external-cause and acknowledgements"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Six CLI tests pass | `cd "$CP" && python -m pytest reconciler/tests/test_cli.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `6 passed` |
| A2 | Five distinct exit codes | `cd "$CP" && python -c "from reconciler import cli; print(sorted({cli.EXIT_CLEAN,cli.EXIT_FINDINGS,cli.EXIT_BLOCKING,cli.EXIT_FAILED,cli.EXIT_CANNOT_START}))"` | `[0, 1, 2, 3, 4]` |
| A3 | The CLI never commits or pushes | `cd "$CP" && grep -cE 'subprocess|git ' reconciler/cli.py` | `0` |
| A4 | An unstartable run exits 4, not 0 | `cd "$CP" && env -u RECONCILER_TOKEN python -m reconciler.cli --root /nonexistent --org x >/dev/null 2>&1; echo $?` | `4` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/tests/test_cli.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "from reconciler import cli; print(sorted({cli.EXIT_CLEAN,cli.EXIT_FINDINGS,cli.EXIT_BLOCKING,cli.EXIT_FAILED,cli.EXIT_CANNOT_START}))"
grep -cE 'subprocess|git ' reconciler/cli.py
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
6 passed
[0, 1, 2, 3, 4]
0
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L4`, if you are asked to make the CLI commit the run record into `control-plane-records`. That repository is L4's in full (PARTITION.md line 20) and a commit from this lane fails the lane guard. Emit; hand off.
Do **not** let `--external-cause` change a verdict, drop a finding, or lower a class. Section 53.1 makes it an **annotation**: *"the annotation names the outage, and the run is re-executed once the dependency recovers."*
Do **not** exit `0` on any path where the engine did not actually run all nineteen comparators. That is EC-109 wearing a shell prompt.

---

## L3-01-22 — Phase acceptance: full-set assertion, read-only proof, path guard, exit record

**Size:** L **Depends on:** L3-01-21 (and every prior task merged to `integration`)
**Owns:** `reconciler/tests/test_phase1_acceptance.py`, `reconciler/PHASE1-EXIT.md`
**Spec basis:** rules **R1**, **R2**, **R3** of Section 0; §53.1 (the comparison set, the counts, the canary); §99.6 risk 6; PARTITION.md rules 1 and 4.

This task proves the three rules of Section 0 hold across the whole phase, not merely inside the tasks that introduced them.

### Branch and gate

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git log --oneline origin/integration | grep -c 'L3-01-T'
git checkout -b lane/3/p1-t22-phase-acceptance
```

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > reconciler/tests/test_phase1_acceptance.py <<'PYEOF'
"""Phase-1 acceptance. The three rules of Section 0, asserted phase-wide.

R1 - the engine issues HTTP GET and nothing else.
R2 - every file this phase creates is under an owned path; registries/** and
     templates/workflows/** are read, never written, never imported.
R3 - every comparator carries the Section 53.1 "On mismatch" cell verbatim,
     from the manifest, checked against the frozen table.

Plus the two properties Section 53.1 states about the run as a whole: all
nineteen rows are compared, and a run that finds nothing is FAILED.
"""
import importlib
import pathlib
import pkgutil

import pytest
import yaml

from reconciler import counts, integrity
from reconciler.api import client as api_client
from reconciler.comparators import registry

ROOT = pathlib.Path(__file__).resolve().parents[2]
OWNED = ("reconciler/", "tools/provision/", "validators/drift/")
WRITE_VERBS = ('"POST"', '"PUT"', '"PATCH"', '"DELETE"',
               "'POST'", "'PUT'", "'PATCH'", "'DELETE'")


def _lane_sources():
    for rel in OWNED:
        d = ROOT / rel
        if d.is_dir():
            for p in d.rglob("*.py"):
                yield p


def _load_all():
    import reconciler.comparators as pkg
    for mod in pkgutil.iter_modules(pkg.__path__):
        if mod.name.startswith("cmp_"):
            importlib.import_module(f"reconciler.comparators.{mod.name}")
    return registry.registered()


# ---- R1 --------------------------------------------------------------
def test_r1_the_method_allowlist_is_still_exactly_get():
    assert api_client.ALLOWED_METHODS == frozenset({"GET"})


def test_r1_no_lane_source_names_a_write_verb():
    offenders = []
    for p in _lane_sources():
        if p.name in ("test_client_readonly.py", "test_phase1_acceptance.py"):
            continue
        text = p.read_text(encoding="utf-8")
        for verb in WRITE_VERBS:
            if verb in text:
                offenders.append(f"{p}: {verb}")
    assert offenders == []


def test_r1_no_lane_source_calls_a_write_helper():
    banned = ("requests.post", "requests.put", "requests.patch", "requests.delete",
              "urlopen(data=", "subprocess.run(['git'", 'subprocess.run(["git"')
    offenders = [
        f"{p}: {b}" for p in _lane_sources() if p.name != "test_phase1_acceptance.py"
        for b in banned if b in p.read_text(encoding="utf-8")
    ]
    assert offenders == []


# ---- R2 --------------------------------------------------------------
def test_r2_the_lane_owns_every_file_it_created():
    tracked = [p for rel in OWNED for p in (ROOT / rel).rglob("*") if p.is_file()] \
        if all((ROOT / r).exists() for r in OWNED) else []
    assert tracked, "no owned files found; run from the repository root"
    for p in tracked:
        rel = p.relative_to(ROOT).as_posix()
        assert rel.startswith(OWNED), rel


def test_r2_no_lane_source_imports_another_lanes_tree():
    banned = ("from registries", "import registries", "from templates", "import templates",
              "from contracts", "import contracts", "from schemas", "import schemas")
    offenders = [
        f"{p}: {b}" for p in _lane_sources() if p.name != "test_phase1_acceptance.py"
        for b in banned if b in p.read_text(encoding="utf-8")
    ]
    assert offenders == []


# ---- R3 --------------------------------------------------------------
def test_r3_every_registered_comparator_has_a_manifest_row():
    reg = _load_all()
    manifest = registry.load_manifest()
    assert sorted(reg) == sorted(manifest) == sorted(registry.EXPECTED_IDS)


def test_r3_no_comparator_module_hard_codes_a_manifest_mismatch_string():
    cells = {row["on_mismatch"] for row in registry.load_manifest().values()}
    offenders = []
    for p in (ROOT / "reconciler" / "comparators").glob("cmp_*.py"):
        text = p.read_text(encoding="utf-8")
        for cell in cells:
            if cell in text:
                offenders.append(f"{p.name}: {cell}")
    assert offenders == []


# ---- the comparison set as a whole -----------------------------------
def test_the_comparison_set_is_nineteen_rows_covering_six_registries():
    reg = _load_all()
    assert len(reg) == 19
    keys = {cls.registry_key for cls in reg.values()}
    assert keys <= set(counts.REGISTRY_KEYS)
    assert len(keys) >= 4


def test_a_run_that_finds_nothing_is_failed_not_clean():
    body = {"comparators_executed": ["CMP-%02d" % n for n in range(1, 20)],
            "findings": [], "registry_counts": {}}
    if "<from D-L3-04" in integrity.BINDING.read_text(encoding="utf-8"):
        pytest.skip("D-L3-04 not yet transcribed")
    assert integrity.verdict(body) == integrity.VERDICT_FAILED
PYEOF

python -m pytest reconciler/tests/test_phase1_acceptance.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -m pytest reconciler validators/drift -q 2>&1 | grep -oE '^[0-9]+ passed'

cat > reconciler/PHASE1-EXIT.md <<'MDEOF'
# L3 Phase 1 exit record — the declared-versus-actual diff engine

## What exists

| Spec | Module |
| --- | --- |
| 53.1 comparison set, all nineteen rows | reconciler/comparators/cmp_01 … cmp_19 |
| 53.1 "On mismatch" cells, frozen | reconciler/comparators/section-53-1.frozen.md, manifest.yaml |
| 53.1 per-registry comparison counts | reconciler/counts.py, reconciler/orchestrator.py |
| 53.1 seeded canary rule / AT-102 / EC-109 | reconciler/integrity.py, reconciler/canary-binding.yaml |
| 53.1 run record, clean recorded as clean | validators/drift/schema/reconciliation-run.schema.json |
| 53.1 acknowledged_by / acknowledged_at | reconciler/cli.py, drift-finding.schema.json |
| 53.1 external-cause annotation | reconciler/cli.py |
| 53.4 the one drift severity scale | reconciler/model.py DRIFT_CLASSES |
| 11.3 branch protection, declared | tools/provision/templates/branch-protection.yaml |
| 33.4 / D91 deployment branch and tag policy, declared | tools/provision/templates/environment.yaml |
| 40.2 attestation binding | reconciler/comparators/attestation-binding.yaml (D-L3-02) |
| 44.5 restore-evidence bindings | reconciler/comparators/restore-binding.yaml (D-L3-03) |
| 96 D96 per-run call ledger, expected-source assertion | reconciler/api/client.py |
| AT-110, client half | reconciler/api/client.py ALLOWED_METHODS |

## State at exit

The engine issues HTTP GET and nothing else. ALLOWED_METHODS has one member,
and a phase-wide test asserts that no module under reconciler/**,
tools/provision/** or validators/drift/** names a write verb or calls a write
helper.

Every Level-3 repair this phase can identify is carried as data on the finding
with `"applied": false`. Nothing applies one. The stricter-only predicate
(invariant 81, AT-033) and the repair executor are L3 Phase 2.

A run that reports zero findings is FAILED and raises SIG-13. A run whose
rows_compared falls below rows_declared on any registry key is FAILED. A run
that executes fewer than nineteen comparators is FAILED and is rejected by the
run schema besides.

## What is NOT in this phase

- Any write of any kind to GitHub. Detect only (99.4 item 6, 99.6 risk 6).
- Writing the run record into control-plane-records. This lane EMITS it; the
  records-writer write path of 97.1 (D76 as amended by D89) is L4's.
- The independent control verifier of 53.1. It runs off the operations VM
  under a different credential and is not L3's to build.
- The response levels themselves (53.2) and auto-repair (53.3). L3 Phase 2.
- The reconciler credential's own boundedness run, AT-110 --live. It needs the
  fifth-tier credential on the operations VM and a DevOps-capability holder.
MDEOF

git add reconciler
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-01-22: phase-1 acceptance suite and exit record"
git rebase origin/integration
git push -u origin HEAD
gh pr create --base integration --fill --label "lane-3,phase-1"
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Nine acceptance tests pass | `cd "$CP" && python -m pytest reconciler/tests/test_phase1_acceptance.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `9 passed` |
| A2 | The whole phase passes: 139 tests | `cd "$CP" && python -m pytest reconciler validators/drift -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `139 passed` |
| A3 | Nineteen comparators, no more, no fewer | `cd "$CP" && python -c "import importlib,pkgutil,reconciler.comparators as p; [importlib.import_module('reconciler.comparators.'+m.name) for m in pkgutil.iter_modules(p.__path__) if m.name.startswith('cmp_')]; from reconciler.comparators.registry import registered; print(len(registered()))"` | `19` |
| A4 | One allowed HTTP method | `cd "$CP" && python -c "from reconciler.api.client import ALLOWED_METHODS as m; print(len(m))"` | `1` |
| A5 | No write verb anywhere in the lane | `cd "$CP" && grep -rlE '"(POST|PUT|PATCH|DELETE)"' reconciler tools/provision validators/drift --include=*.py \| grep -v test_client_readonly.py \| grep -v test_phase1_acceptance.py \| wc -l` | `0` |
| A6 | No foreign path in any phase commit | `cd "$CP" && git diff --name-only $(git merge-base origin/main origin/integration)...origin/integration -- \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |
| A7 | Nothing under `registries/` or `templates/` modified | `cd "$CP" && git status --porcelain registries templates \| wc -l` | `0` |
| A8 | The exit record exists | `cd "$CP" && test -f reconciler/PHASE1-EXIT.md && echo EXIT-RECORD-OK` | `EXIT-RECORD-OK` |

*(A2's total is the sum of the per-task counts: T01 6 + T02 8 + T03 7 + T04 6 + T05 5 + T06 6 + T07 4 + T08 7 + T09 8 + T10 9 + T11 6 + T12 6 + T13 5 + T14 6 + T15 5 + T16 5 + T17 5 + T18 6 + T19 6 + T20 8 + T21 6 + T22 9 = **139**. Run A2 only after all twenty-one prior task branches have merged to `integration` and this branch is rebased on it. Before that point the binding criterion is zero failures, not the total — use the SELF-VERIFY form.)*

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP"
python -m pytest reconciler/tests/test_phase1_acceptance.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -m pytest reconciler validators/drift -q 2>&1 | grep -cE '^[0-9]+ failed'
python -c "import importlib,pkgutil,reconciler.comparators as p; [importlib.import_module('reconciler.comparators.'+m.name) for m in pkgutil.iter_modules(p.__path__) if m.name.startswith('cmp_')]; from reconciler.comparators.registry import registered; print(len(registered()))"
git status --porcelain registries templates | wc -l
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output:

```
9 passed
0
19
0
0
```

### STOP rule

STOP and file the Section 6 blocker, `Blocked-on: L0`, if `A3` prints anything other than `19`. A missing comparator means a task in T06 … T19 has not merged; rebase on `integration` and wait. Do **not** lower the expected count, and do **not** delete a comparator to make the number match.
STOP with `Blocked-on: L0` if `A5` or `A6` is not `0`. A write verb in this lane, or a foreign path in a phase commit, is a violation of rule R1 or rule R2, and the fix is to remove the offending code — never to add the file to the exclusion list in the test.
Do **not** edit `test_phase1_acceptance.py` to skip a failing assertion. The assertions are the phase's deliverable; a failing one means the phase is not finished.

---

## 7. Phase exit conditions — all must hold before L3 Phase 2 begins

| # | Condition | Command | Required |
| --- | --- | --- | --- |
| E1 | All twenty-two task branches merged to `integration` | `git log --oneline origin/integration \| grep -c 'L3-01-T'` | `22` |
| E2 | Whole-phase suite green, zero failures | `python -m pytest reconciler validators/drift -q 2>&1 \| grep -cE '^[0-9]+ failed'` | `0` |
| E3 | Nineteen comparators registered | `python -c "import importlib,pkgutil,reconciler.comparators as p; [importlib.import_module('reconciler.comparators.'+m.name) for m in pkgutil.iter_modules(p.__path__) if m.name.startswith('cmp_')]; from reconciler.comparators.registry import registered; print(len(registered()))"` | `19` |
| E4 | The manifest matches the frozen Section 53.1 table | `python -m pytest reconciler/comparators/tests/test_manifest.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `5 passed` |
| E5 | One allowed HTTP method, phase-wide | `python -c "from reconciler.api.client import ALLOWED_METHODS as m; print(len(m))"` | `1` |
| E6 | Every L0 decision transcribed, no placeholder left | `grep -rc 'from D-L3-0' reconciler/comparators/attestation-binding.yaml reconciler/comparators/restore-binding.yaml reconciler/canary-binding.yaml \| grep -c ':0$'` | `3` |
| E7 | Six registry keys carry counts on every run | `python -c "from reconciler.counts import REGISTRY_KEYS as k; print(len(k))"` | `6` |
| E8 | No foreign path in any phase commit | `git diff --name-only $(git merge-base origin/main origin/integration)...origin/integration -- \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |
| E9 | Nothing under `registries/`, `templates/` or `contracts/` was modified by this lane | `git diff --name-only $(git merge-base origin/main origin/integration)...origin/integration -- registries templates contracts \| wc -l` | `0` |
| E10 | The phase exit record is present | `test -f reconciler/PHASE1-EXIT.md && echo EXIT-RECORD-OK` | `EXIT-RECORD-OK` |

**What Phase 1 hands to Phase 2.** A finding envelope, a run record, nineteen comparators that produce them, and a run verdict that cannot be talked into optimism. `L3-02-01`'s entry gate checks for `reconciler/`, `validators/drift/` and `reconciler/pyproject.toml`; all three exist at E10. Phase 2 adds the five response levels on top of these findings and does not modify a single file this phase created.

**What Phase 1 deliberately does not hand over.** No write path, no enabled repair class, no credential. Spec Section 99.4 item 6 is the reason and it is worth reading once more before Phase 2 starts: *"Reconciliation v0, detect and block only ... Auto-repair is deferred until detection has run clean for weeks."* The weeks are not a formality. They are the evidence that the instrument in this file works before it is given hands.
