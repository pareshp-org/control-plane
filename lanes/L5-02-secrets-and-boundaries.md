<!-- Task IDs renamed to charter format L5-FF-TT by Session 12 (FD-037 corollary) -->
> **[AUTHORITATIVE — FD-B1-L5 2026-09-02]**
> This is the authoritative task plan for Lane 5. All competing plans are superseded.

# L5 — ACCESS, INFRA AND OPS · PHASE 2 — SECRETS AND TRUST BOUNDARIES

Lane: **L5 Access, Infra & Ops** (subsystems K, L, M, Q, R of spec Section 99.2).
Branch prefix: `lane/5/*`. Owned paths: `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**`.
Repository: `control-plane` (per PARTITION.md, Repositories table).

This file contains **fourteen executable tasks**. Every task is mechanical. No task asks the executor
to design, choose, name a person, pick a threshold, or interpret the specification. Every value that
would require judgement is read from a frozen L0 input file (see **Frozen inputs** below); if that
file is missing or shaped differently, the task **STOPs** and files a blocker.

---

## 1. What this phase builds

| # | Thing | Spec anchor |
|---|---|---|
| 1 | The five secret tiers as machine-readable configuration, with the exact contents and locations of the Section 40.1 table | §40.1 |
| 2 | The **never-moves-down-a-tier** rule as an executable check, with a production credential below the production tier classed as a security incident under §43 rather than a cleanup task | §40.1, §43, invariant 25 |
| 3 | Fifth-tier machine-credential inventory entries — rotation cadence (initial value quarterly), named rotator (a DevOps-capability holder), runbook link, declared behavioural envelope, and the named owner of that envelope's alert configuration | §40.1 "Fifth-tier operations", §49.1 |
| 4 | The **behavioural envelope** of D96 — required signed run record naming the scheduled trigger, run-count ceiling per day (initial value: twice the scheduled run count), expected source host, published per-run API-call counts — and its evaluator, which classes a run outside the envelope as Blocking drift | §40.1 "The behavioural envelope", D96, §53.4 |
| 5 | The one-page rotation runbook and the rotation-completion gate: a rotation is not recordable as done until a manual reconciliation run completes clean, AT-110 re-executes, and re-escrow is confirmed | §40.1, §14.4 "Escrow mechanics", AT-110 |
| 6 | The **first** workstation trust boundary of §40.3 as a declared, checkable statement | §40.3, invariants 24 / 26 |
| 7 | The **second** boundary added by D95 — a fully compromised engineering workstation must not yield the control-plane machine-credential store — with the credential held so that VM-root does not passively read it, and a hardware-key-gated second factor on the operations-VM shell path | §40.3, §51.4, §51.5, D95, §99.6 risk 6 |
| 8 | Separation of the fifth-tier rotator from the holder of host root, or the recorded accepted risk with a named holder and a dated review where headcount does not permit it | §40.3, §90.3 (accepted-risk shape), §54.2 |
| 9 | The API-key-free check — `env \| grep -i api_key` returns empty, across shell profiles and repository `.env` files — at onboarding and quarterly | §40.2, §36.6, §98.2 Phase 1, invariant 84 |
| 10 | The §43.4 containment hook: compromise of a workstation holding DevOps access triggers rotation of **every** fifth-tier machine credential as a named step | §43.4 |

**Subsystem mapping (§99.2).** Item 9 is subsystem **K** (AI runtime contract enforcement — "API-key-free
checks at onboarding and quarterly"). Items 1–3, 6–8, 10 are subsystem **L** (access-control architecture —
"five secret tiers"). Items 7 and the on-host verifier are subsystem **M** (operations VM). Item 3's
inventory entries are subsystem **Q** (asset inventory). Envelope alert routing is subsystem **R**.

**Not in this file.** Reconciler code (L3), workflow wiring (L2 owns `.github/workflows/**`), record
schemas and record writes (L4 owns `records/**`), registry schemas (L1). Where a check produced here
must run in CI, this file produces the **script** in an owned path and records a handoff (Section 9);
it never writes a workflow file.

---

## 2. Frozen inputs — read before task 1

L0 freezes `contracts/**` in Phase 0 (PARTITION.md, rule 2). This lane consumes exactly one contract
file. **The executor never edits it and never creates it.**

`contracts/access/access-inputs.yaml` — required shape:

```yaml
schema_version: 1
secret_name_registry:
  production: ["<literal secret name>", ...]     # names held in GitHub Environment: production
  staging:    ["<literal secret name>", ...]     # names held in GitHub Environment: staging
  control_plane: ["<literal secret name>", ...]  # names of fifth-tier machine credentials
fifth_tier:
  reconciler:        &entry
    rotator: "<people.yaml id of a DevOps-capability holder>"
    envelope_alert_owner: "<people.yaml id>"
    expected_source_host: "<hostname>"
    scheduled_runs_per_day: <integer>
    permission_set: ["<literal permission string>", ...]
  provisioning-cli:   { <same five keys> }
  organisation-export-token: { <same five keys> }
  records-writer:     { <same five keys> }
  layer-b-backup:     { <same five keys> }
ops_vm:
  hostname: "<hostname>"
  host_root_holder: "<people.yaml id>"
  shell_second_factor_key_ids: ["<sk- key comment/id>", ...]
checks:
  api_key_free:
    owner: "<people.yaml id>"
    shell_profile_paths: ["<absolute path>", ...]
# layer_b_admin_group — admin group for Layer B access control (FD-038 / Q9).
# The GitHub team slug (e.g. "my-org/layer-b-admins") whose members hold
# administrative rights over the Layer B Grafana instance on the operations VM.
# Read by L5-03 task L5-03-09 to scope the administrative allowlist sync and
# by L5-03-11 to bound the named accepted-access record.
# Type: string (GitHub team slug). Required: true.
layer_b_admin_group: "<github-org/layer-b-team-slug>"
# layer_b — session limits, capability-holders artifact path, and host admin access
# record for the Layer B-M Grafana instance.
# Q9 resolved — this block is the 6th key L5-03 reads that was absent from the
# original 5-key shape (schema_version, secret_name_registry, fifth_tier, ops_vm,
# checks). All six dotted paths L5-03 reads are sub-keys here:
#   layer_b.session.max_lifetime_duration        (L5-03-08)
#   layer_b.session.max_inactive_lifetime_duration (L5-03-08)
#   layer_b.capability_holders_artifact           (L5-03-09)
#   layer_b.host_admin_access.holder_login        (L5-03-11)
#   layer_b.host_admin_access.expiry              (L5-03-11)
#   layer_b.host_admin_access.review_cadence_days (L5-03-11)
# These values are not derivable from the other 5 keys; they are Founder decisions
# and L0-frozen calibration values (Section 84.5, Section 54.2, Section 90.3).
layer_b:
  session:
    # Rendered into ops-vm/layer-b/grafana.ini [auth] block by L5-03-08.
    # Use Grafana duration strings, e.g. "720h" (30 days), "24h".
    max_lifetime_duration: "<Grafana auth.login_maximum_lifetime_duration string>"
    max_inactive_lifetime_duration: "<Grafana auth.login_maximum_inactive_lifetime_duration string>"
  # Repo-relative path to L1's published capability-holders artifact.
  # Consumed by L5-03-09 sync-allowlist.sh and check-non-delegable.sh.
  capability_holders_artifact: "<repo-relative path to published capability-holders artifact>"
  host_admin_access:
    # The single named holder of VM-root and Grafana-admin on layerb-host.
    # Naming the holder is a Founder decision (Section 90.3, Section 54.2).
    holder_login: "<people.yaml id>"
    # Bounded expiry date (RFC3339). An entry with no expiry is undocumented
    # policy (Section 54.2). Initial review cadence is quarterly (Section 84.5).
    expiry: "<RFC3339 date, e.g. 2027-01-01>"
    review_cadence_days: <integer, initial value 90>
```

**Preflight — run once, before task L5-02-01.**

```bash
set -euo pipefail
export CONTROL_PLANE_ROOT=/c/D_Drive/PS/MultiProduct/control-plane
cd "$CONTROL_PLANE_ROOT"
python3 -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 12) else 1)" \
  || { echo "STOP: Python 3.12 required (FD-005); got $(python3 --version 2>&1)"; exit 1; }
test -f contracts/access/access-inputs.yaml && echo "INPUT-PRESENT" || echo "INPUT-MISSING"
python -c "import yaml; print('PYYAML-OK')"
```

Expected output, both lines, in this order:

```
INPUT-PRESENT
PYYAML-OK
```

**STOP if either line differs.** `INPUT-MISSING` → blocker, class `missing-contract`. A `ModuleNotFoundError`
→ run `python -m pip install "PyYAML==6.0.2"` once, then re-run the preflight; if the install fails,
blocker, class `toolchain`.

---

## 3. Working environment — identical for every task

```bash
set -euo pipefail
export CONTROL_PLANE_ROOT=/c/D_Drive/PS/MultiProduct/control-plane
cd "$CONTROL_PLANE_ROOT"
```

Shell is **Git Bash** (POSIX `sh` syntax; forward slashes; `/dev/null`). Python is `python3` on PATH,
version 3.12 exact (FD-005). Every path in this file is repository-relative to `$CONTROL_PLANE_ROOT` unless it starts with `/`.

**Branch, commit and PR — the same three blocks in every task, with only the slug changing.**

Open:

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-<slug>
```

Close:

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add <exact paths listed in the task>
git commit -m "L5-P2-<NN>: <task title> (Section 40.x)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-<slug>
gh pr create --base integration \
  --title "L5-P2-<NN> <task title>" \
  --body "Lane 5, Phase 2, task L5-P2-<NN>. Spec: <anchors>. Paths: <paths>. Self-verify output pasted below."
```

If `git rebase origin/integration` reports a conflict in **any file this lane does not own**, abort with
`git rebase --abort` and STOP (class `foreign-path-conflict`). A lane never resolves another lane's file.

---

## 4. Conventions

**Size legend.** S = under half a day. M = half a day to two days. L = two to five days.

**Acceptance criteria** are a table. Every row has a command and an exact required output. "Exit 0" alone
is never an acceptance criterion.

**SELF-VERIFY** is a single copy-pasteable block whose output must match the quoted block character for
character, except where a line is explicitly marked `<varies>`.

**STOP rule.** Each task names the conditions under which the executor must not proceed. On any STOP:
do not commit, do not push, do not "work around". File the blocker below and move to the next task whose
dependencies are already satisfied.

**Blocker issue template** — file with `gh issue create --label lane-5,blocker`:

```
Title: [L5-P2-<NN>] BLOCKED — <one line>

Task id:        L5-P2-<NN>
Lane:           L5 (access/**, infra/**, ops-vm/**, notify/**, assets/**)
Branch:         lane/5/p2-<slug>   (not pushed)
Blocker class:  missing-contract | shape-mismatch | toolchain | foreign-path-conflict |
                needs-decision | host-unreachable | tpm-absent
What I ran:     <the exact command>
What I expected: <the exact expected output from this file>
What I got:      <verbatim output>
Spec anchor:    <section / D id / AT id from the task header>
Decision needed from L0: <one sentence, or "none — environment fault">
```

---

## 5. Task index

| Task id | Title | Size | Depends on |
|---|---|---|---|
| L5-02-01 | Secret-tier registry — the five tiers, exact contents and locations | S | — |
| L5-02-02 | Tier registry schema and validator | M | T01 |
| L5-02-03 | The never-moves-down-a-tier check | M | T01, T02 |
| L5-02-04 | Fifth-tier credential inventory entries (five credentials) | M | T01 |
| L5-02-05 | Behavioural-envelope declaration and credential schema (D96) | M | T04 |
| L5-02-06 | Envelope evaluator — a run outside the envelope is Blocking | M | T05 |
| L5-02-07 | The one-page credential-rotation runbook | M | T04 |
| L5-02-08 | Rotation-completion gate (clean reconciliation + AT-110 + re-escrow) | M | T07 |
| L5-02-09 | The two trust boundaries, declared and checkable (§40.3, D95) | M | T01 |
| L5-02-10 | Ops-VM credential-store holding and hardware-key shell gate | L | T09 |
| L5-02-11 | Rotator / host-root separation, or the recorded accepted risk | M | T04, T09 |
| L5-02-12 | The API-key-free check — onboarding and quarterly | M | T01 |
| L5-02-13 | Workstation-compromise containment hook (§43.4) | S | T07, T12 |
| L5-02-14 | Phase 2 exit gate — one command runs every check | M | T03, T06, T08, T10, T11, T12, T13 |

---

## 6. Spec anchors — every identifier used below, with its line range

Cited once here so no task has to search. Every identifier was read from
`Research/MultiProduct_MasterSpec_v4.0.md`. None is invented. A task that finds an anchor absent or
different at the cited lines has hit a STOP condition (class `shape-mismatch`) — it does not renumber.

| Anchor | Lines | What it fixes for this phase |
|---|---|---|
| §40.1 Five secret tiers | 3644–3686 | The five-row tier table (Tier / Location / Contains) copied verbatim in T01; the never-moves-down rule and its §43 classification; "Fifth-tier operations" — rotation cadence initial value quarterly, named rotator a DevOps-capability holder, runbook link, declared behavioural envelope, named owner of that envelope's alert configuration; "The behavioural envelope" — signed run record naming the scheduled trigger, run-count ceiling per day at twice the scheduled run count, expected source host, published per-run API-call counts; the clean-reconciliation condition; the §14.4 escrow as re-issue source |
| §40.2 Boundary rules | 3687–3694 | `env \| grep -i api_key` must return empty; shell profiles and repository `.env` files checked at onboarding and re-checked quarterly; provider-SSO federation with no long-lived key, which is *why* the tiers remain exactly five; the declared-boundary attestation |
| §40.3 The workstation trust boundary | 3695–3704 | Boundary 1 (production) verbatim; boundary 2 (control-plane machine-credential store) verbatim; the three technical enforcements — a separate OS user or secret agent that a passive root shell does not read, a second factor on top of the private network path, rotator/host-root separation or a recorded accepted risk |
| §43.1 The flow | 3853–3870 | DETECT → CLASSIFY → CONTAIN → PRESERVE EVIDENCE → ROTATE CREDENTIALS. "Do not rotate before capturing" fixes the step order of the T13 checklist |
| §43.4 Compromised workstation | 3928–3931 | "compromise of a workstation holding DevOps access triggers rotation of every fifth-tier machine credential" as a **named step, not an inference** |
| §14.4 Escrow mechanics | 1256–1267 | Re-escrow of the replacement is a **blocking step in the rotation runbook (Section 40.1)**: a rotation is not recordable as done until the replacement is escrowed |
| §45.3 The organisation export | 4064–4080 | The write-only, object-locked discipline reused by the compensating control of T11 |
| §49.1 Expiry-tracked assets | 4338–4348 | The inventory carries an entry for each control-plane machine credential: rotation cadence (initial value quarterly), named rotator (DevOps-capability holder), runbook link, out-of-window alert-config owner; every entry carries an expiry date, a named owner and an alert threshold of at least 30 days |
| §51.4 Control-plane patching | 4487–4498 | Every control-plane surface is reachable only over a private network path with SSO in front of it; the second factor of T10 sits **on top of** that path, never instead of it |
| §51.5 The disposable operations VM | 4500–4502 | The VM "holds no production credentials, no deploy keys and no environment access — but it does hold the fifth-tier machine-credential store of Section 40.1, including the reconciler credential and the organisation-export token, which is why the second trust boundary of Section 40.3 exists" |
| §53.4 Drift classes | 4704–4716 | The single severity scale: Green / Amber / Red / **Blocking**. A run outside the envelope is Blocking. No other severity vocabulary exists anywhere in the system |
| §54.2 Exception rules | 4787–4797 | Expiry is mandatory; every exception names a compensating control and the store its execution lands in; an accepted risk with no named holder, no compensating control and no expiry is undocumented policy |
| §64.2 Fail-closed versus fail-open | 5448–5468 | Every control this phase produces carries exactly one classification |
| §84.5 KPI calibration review | 7450–7470 | The cadence the accepted-risk review and the envelope recalibration run on |
| §90.3 Datasource-level enforcement | 7975–7989 | The **shape** of a recorded accepted risk: named holder, an explicit statement of what the holder does *not* thereby hold, a compensating control the holder cannot silently defeat, and a dated review. Borrowed by T11 for the rotator/host-root concentration |
| §36.6 Pre-flight secret stripping and the no-API-keys check | 3232–3238 | The same `env \| grep -i api_key` rule stated for the AI toolchain; no vendor API keys exist anywhere in the estate |
| §98.2 Phase 1 | 9010–9024 | "Verify `env \| grep -i api_key` returns empty on every machine, including shell profiles and repository `.env` files" (line 9015) |
| §99.6 risk 6 | 9276–9294 | "the reconciler is the highest-privilege identity in the system" — the reason boundary 2 exists |
| D95 | 10188 | The second boundary, the passive-root-read condition, and the Layer B host separation |
| D96 | 10189 | Behavioural rather than temporal detection: per-run caps, an expected-source assertion, a run-count ceiling and a signed run record; a run without a matching scheduled trigger is Blocking; published per-run API-call counts |
| D89 | 10182–10190 (Appendix A) | No bypass actor exists on the control-plane repository |
| D107 | 10182–10213 (Appendix A) | Append-only enforced on the records repository |
| AT-110 | 9438–9439 | "The reconciler credential is provably bounded" — six attempts, all six fail, then a normal reconciliation run completes. **Re-executed at every rotation, on the same gate as 40.1's clean-reconciliation condition.** The spec carries this row twice, at 9438 and 9439; that duplication is a known spec defect — cite the range, never renumber |
| Invariant 24 | 9486 | The production database is inaccessible from developer machines |
| Invariant 25 | 9487 | Production secrets are environment-scoped and never present locally |
| Invariant 26 | 9488 | A fully compromised workstation must not yield production access |
| Invariant 79 | 9556 | New people, products and tools default to minimum privilege and draft state |
| Invariant 80 | 9557 | Every control is explicitly classified fail-closed or fail-open |
| Invariant 84 | 9564 | API keys remain absent from developer environments |
| Invariant 87 | 9567 | Every architecture and security policy is enforced by the platform wherever the platform can enforce it |

### 6.1 The one substitution the executor makes, and the only one

Throughout Section 3 the branch, commit and PR blocks are written with `<NN>` and `<slug>`. **`<NN>` is the
task's index suffix exactly as it appears in Section 5** — `T01`, `T02`, … `T14` — so the commit subject for
task `L5-02-01` begins `L5-02-01:` and the blocker title is `[L5-02-01]`. `<slug>` is given literally in
each task's header row. No other substitution is made anywhere in this file.

### 6.2 Paths this phase writes, and the ones it must not

This phase writes **only** under these four roots, all of which L5 owns exclusively (PARTITION.md line 21):

| Root written here | Files |
|---|---|
| `access/secrets/**` | tier registry, fifth-tier credential entries, envelopes, checks, runbooks, boundaries, host declarations, incident checklist, gate |
| `access/fail-closed/**` | one classification file per control this phase produces (§64.2, invariant 80) |
| `access/published/**` | `secret-tiers.v1.json` — the one artifact this phase publishes for other lanes |
| `infra/network/**` | the operations-VM shell-gate declaration and its host-side verifier (§51.4 private path plus the §40.3 second factor) |

It writes nothing under `ops-vm/**`, `notify/**` or `assets/**`. Those roots are L5's, but they belong to
other L5 phase files, and a second file writing them would break the additive-only discipline. In
particular:

| Path this phase must NOT write | Owner | What this phase does instead |
|---|---|---|
| `assets/inventory/machine-credential-*.yaml` | L5 phase 5, task L5-05-02 | T04 emits the §49.1 field set into `access/published/secret-tiers.v1.json`; L5-05-02 reads it |
| `ops-vm/credentials/**`, `ops-vm/systemd/**` | L5 phase 4, task L5-04-07 | T10 declares the holding requirement and ships the verifier; phase 4 provisions the store |
| `infra/hosts/**`, `infra/layer-b/**` | L5 phase 3, tasks L5-03-02, L5-03-05 | T09 declares boundary 2; phase 3 separates the Layer B host under the same decision (D95) |
| `contracts/**` | L0, frozen at Phase 0 | Read only. A needed change is a Contract Change Request, never an edit |
| `.github/workflows/**` | L2 | Every check here is a script in an owned path plus a handoff row in Section 9 |
| `reconciler/**` | L3 | T06 publishes an exit contract the reconciler consumes; it contains no reconciler code |

---

## 7. The fourteen tasks

Execute in index order. Each task's `Depends on` row lists the task ids whose PRs must already be merged to
`integration`. A task whose dependency is unmerged is not blocked — it is simply not yet startable; move to
the next task whose dependencies are satisfied, exactly as Section 4 says.

---

## L5-02-01 — Secret-tier registry: the five tiers, exact contents and locations

| Field | Value |
|---|---|
| Task id | `L5-02-01` |
| Size | S |
| Depends on | — |
| Slug | `tier-registry` |
| Subsystem | L (access-control architecture) |
| Spec | §40.1 lines 3644–3656; §40.2 line 3689 (why there are exactly five) |
| Writes | `access/secrets/README.md`, `access/secrets/tiers/tier-1-developer.yaml`, `access/secrets/tiers/tier-2-ci.yaml`, `access/secrets/tiers/tier-3-staging.yaml`, `access/secrets/tiers/tier-4-production.yaml`, `access/secrets/tiers/tier-5-control-plane.yaml` |

### Purpose

Turn the §40.1 table into five machine-readable files — one file per tier, never one shared file
(PARTITION.md rule 3). The `location` and `contains` strings are **copied from the spec table**, not
paraphrased: every later check in this phase compares against them, and a paraphrase makes the comparison
meaningless. `rank` is what makes "never moves down a tier" computable: *down* means toward a lower rank.

There are exactly five tiers and no sixth. §40.2 states why: human infrastructure access is
provider-SSO-federated with no long-lived key, "which is why the five secret tiers of Section 40.1 remain
exactly five". A task that finds itself wanting a sixth tier has hit a STOP condition.

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-tier-registry
mkdir -p access/secrets/tiers
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/README.md <<'MDEOF'
# access/secrets — the five secret tiers and the two trust boundaries

Spec: Section 40 (Secrets and Production Access), lines 3644-3704 of
Research/MultiProduct_MasterSpec_v4.0.md.

This tree is DECLARATION plus CHECKS. It holds no secret value, no credential
handle and no host address that is not already public configuration. Nothing
here is provisioned by this tree: Lane 5 phase 4 provisions the fifth-tier
store on the operations VM, Lane 2 executes the checks in CI, Lane 3 reconciles
declared state against actual state.

Layout:

  tiers/       one file per secret tier (five files, Section 40.1)
  fifth-tier/  one file per control-plane machine credential (five files)
  envelope/    the behavioural envelope per credential, plus its evaluator (D96)
  runbooks/    the one-page rotation runbook and the rotation record shape
  checks/      the executable boundary and hygiene checks
  boundaries/  the two Section 40.3 trust boundaries, declared and checkable
  separation/  rotator / host-root separation, or the recorded accepted risk
  host/        what the operations VM must do with the fifth tier (D95)
  incident/    the Section 43.4 containment hook
  gate/        the phase exit gate
  testdata/    fixtures, including every negative test this phase executes

Two rules govern every file here.

1. A secret never moves down a tier. A production credential appearing anywhere
   below the production tier is a security incident under Section 43, not a
   cleanup task (Section 40.1, line 3656).
2. Every control in this tree carries exactly one classification, fail-closed or
   fail-open, in access/fail-closed/ (Section 64.2, invariant 80). Where a check
   cannot read its input it fails closed: it reports a failure, never a pass.
MDEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/tiers/tier-1-developer.yaml <<'YAMLEOF'
# access/secrets/tiers/tier-1-developer.yaml
# Section 40.1, table at lines 3648-3654. Location and contains are copied from
# the spec table verbatim. Do not paraphrase: the checks compare strings.
schema_version: 1
tier_id: developer
rank: 1
tier: "Developer"
location: ".env.local, git-ignored"
contains: "Local-only values. Never real production credentials"
spec_anchor: "Section 40.1"
spec_lines: "3648-3654"
holds_production_credentials: false
downward_move_from_here: not-possible   # rank 1 is the bottom of the scale
YAMLEOF

cat > access/secrets/tiers/tier-2-ci.yaml <<'YAMLEOF'
# access/secrets/tiers/tier-2-ci.yaml
# Section 40.1, table at lines 3648-3654.
schema_version: 1
tier_id: ci
rank: 2
tier: "CI"
location: "GitHub Actions secrets"
contains: "Build-time and scan credentials"
spec_anchor: "Section 40.1"
spec_lines: "3648-3654"
holds_production_credentials: false
# Section 40.3, line 3699: a branch push executes CI, so a compromised
# workstation yields execution with CI-tier credentials. The compensating
# controls named there bound that exposure; they are declared in
# access/secrets/boundaries/boundary-1-production.yaml.
compensating_controls:
  - "default GITHUB_TOKEN is read-only"
  - "scan and build credentials are environment-gated where the platform supports it"
  - "a workflow-file change pushed by a machine identity is Blocking drift"
YAMLEOF

cat > access/secrets/tiers/tier-3-staging.yaml <<'YAMLEOF'
# access/secrets/tiers/tier-3-staging.yaml
# Section 40.1, table at lines 3648-3654.
schema_version: 1
tier_id: staging
rank: 3
tier: "Staging"
location: "GitHub Environment: staging"
contains: "Staging-scoped credentials only"
spec_anchor: "Section 40.1"
spec_lines: "3648-3654"
holds_production_credentials: false
YAMLEOF

cat > access/secrets/tiers/tier-4-production.yaml <<'YAMLEOF'
# access/secrets/tiers/tier-4-production.yaml
# Section 40.1, table at lines 3648-3654.
schema_version: 1
tier_id: production
rank: 4
tier: "Production"
location: "GitHub Environment: production"
contains: "Production credentials, accessible only to the production deployment workflow"
spec_anchor: "Section 40.1"
spec_lines: "3648-3654"
holds_production_credentials: true
# Section 40.1, line 3656 - carried as this file's own fields so the check that
# reads them cannot drift from the sentence it enforces.
downward_move_class: security-incident
downward_move_authority: "Section 43 (Security Incident Workflow)"
downward_move_is_cleanup_task: false
# Section 40.3, line 3699.
enforced_by: "production secrets exist only in the production GitHub Environment, accessible only to the production deployment workflow, which requires an approval from someone other than the actor"
invariants: [24, 25, 26]
YAMLEOF

cat > access/secrets/tiers/tier-5-control-plane.yaml <<'YAMLEOF'
# access/secrets/tiers/tier-5-control-plane.yaml
# Section 40.1, table at lines 3648-3654; fifth-tier operations at line 3683;
# the behavioural envelope at line 3685; Section 51.5 line 4502 for what the
# operations VM does and does not hold.
schema_version: 1
tier_id: control_plane
rank: 5
tier: "Control plane"
location: "Machine-credential store on the hosts that use them"
contains: "Machine credentials - the reconciler, the provisioning CLI, the organisation-export token, the records-writer credential, the Layer B backup credential. Each is a least-privilege GitHub App or fine-grained PAT (the backup credential, an append-only object-store credential), rotated on a schedule, and bounded by the behavioural envelope declared below"
spec_anchor: "Section 40.1"
spec_lines: "3648-3654"
holds_production_credentials: false
members:
  - reconciler
  - provisioning-cli
  - organisation-export-token
  - records-writer
  - layer-b-backup
member_entries_at: "access/secrets/fifth-tier/"
# Section 51.5, line 4502.
host_holds_not:
  - "production credentials"
  - "deploy keys"
  - "environment access"
# Section 40.3, line 3701 - the second boundary exists because of this tier.
guarded_by_boundary: boundary-2-control-plane
# Section 40.1, line 3683.
rotation_cadence_initial_value: quarterly
rotation_runbook: "access/secrets/runbooks/rotate-fifth-tier-credential.md"
reissue_source: "Section 14.4 escrow"
YAMLEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/secrets/README.md access/secrets/tiers
git commit -m "L5-02-01: secret-tier registry, the five tiers of Section 40.1 (Section 40.1)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-tier-registry
gh pr create --base integration \
  --title "L5-02-01 Secret-tier registry — the five tiers, exact contents and locations" \
  --body "Lane 5, Phase 2, task L5-02-01. Spec: Section 40.1 lines 3644-3656. Paths: access/secrets/README.md, access/secrets/tiers/**. Self-verify output pasted below."
```

### Acceptance criteria

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | Exactly five tier files exist, no more | `ls access/secrets/tiers/*.yaml \| wc -l` | `5` |
| 2 | Ranks are 1..5 with no gap and no duplicate | `python -c "import glob,yaml;print(sorted(yaml.safe_load(open(f))['rank'] for f in glob.glob('access/secrets/tiers/*.yaml')))"` | `[1, 2, 3, 4, 5]` |
| 3 | The production tier's location is the spec string | `python -c "import yaml;print(yaml.safe_load(open('access/secrets/tiers/tier-4-production.yaml'))['location'])"` | `GitHub Environment: production` |
| 4 | The fifth tier's location is the spec string | `python -c "import yaml;print(yaml.safe_load(open('access/secrets/tiers/tier-5-control-plane.yaml'))['location'])"` | `Machine-credential store on the hosts that use them` |
| 5 | Exactly one tier declares that it holds production credentials | `python -c "import glob,yaml;print(sum(1 for f in glob.glob('access/secrets/tiers/*.yaml') if yaml.safe_load(open(f))['holds_production_credentials']))"` | `1` |
| 6 | A downward move is classed as a security incident, not a cleanup task | `python -c "import yaml;d=yaml.safe_load(open('access/secrets/tiers/tier-4-production.yaml'));print(d['downward_move_class'],d['downward_move_is_cleanup_task'])"` | `security-incident False` |
| 7 | The fifth tier lists exactly the five §40.1 machine credentials | `python -c "import yaml;print(','.join(yaml.safe_load(open('access/secrets/tiers/tier-5-control-plane.yaml'))['members']))"` | `reconciler,provisioning-cli,organisation-export-token,records-writer,layer-b-backup` |
| 8 | No file outside `access/secrets/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/secrets/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python - <<'PYEOF'
import glob, yaml
files = sorted(glob.glob('access/secrets/tiers/*.yaml'))
tiers = [yaml.safe_load(open(f, encoding='utf-8')) for f in files]
tiers.sort(key=lambda t: t['rank'])
print("TIER-COUNT %d" % len(tiers))
for t in tiers:
    print("TIER %d %s | %s" % (t['rank'], t['tier_id'], t['location']))
print("PROD-TIER-RANK %d" % [t['rank'] for t in tiers if t['holds_production_credentials']][0])
print("FIFTH-TIER-MEMBERS %d" % len(tiers[-1]['members']))
print("L5-02-01 SELF-VERIFY PASS")
PYEOF
```

Expected output, exactly:

```
TIER-COUNT 5
TIER 1 developer | .env.local, git-ignored
TIER 2 ci | GitHub Actions secrets
TIER 3 staging | GitHub Environment: staging
TIER 4 production | GitHub Environment: production
TIER 5 control_plane | Machine-credential store on the hosts that use them
PROD-TIER-RANK 4
FIFTH-TIER-MEMBERS 5
L5-02-01 SELF-VERIFY PASS
```

### STOP rule

STOP — do not commit, do not push, file the blocker of Section 4 — if any of these hold:

* `access/secrets/tiers/` already exists on `integration` with different content. Another branch owns it.
  Class `foreign-path-conflict`.
* The executor believes a sixth tier is needed. §40.2 line 3689 states why there are exactly five; adding
  one is a specification change. Class `needs-decision`.
* SELF-VERIFY prints anything other than the block above, character for character. Class `shape-mismatch`.

---

## L5-02-02 — Tier registry schema and validator

| Field | Value |
|---|---|
| Task id | `L5-02-02` |
| Size | M |
| Depends on | `L5-02-01` |
| Slug | `tier-validator` |
| Subsystem | L |
| Spec | §40.1 lines 3644–3656; invariant 87 line 9567 |
| Writes | `access/secrets/schemas/secret-tier.schema.json`, `access/secrets/tools/validate_tiers.py`, `access/secrets/testdata/tiers-bad-rank/tier-x.yaml`, `access/secrets/testdata/tiers-bad-location/tier-y.yaml` |

### Purpose

A declaration nothing validates is prose. This task makes the tier registry machine-checked and proves the
validator **rejects** as well as accepts — an unexecuted negative test is not a test.

**The validator uses no library the preflight did not prove.** The preflight of Section 2 proves `python`
and `PyYAML` and nothing else. `validate_tiers.py` therefore reads `secret-tier.schema.json` with the
standard-library `json` module and implements the small subset it needs — `required`, `type`, `enum`,
`const`, `minimum`, `maximum` — itself. It imports no JSON-Schema library. Adding a dependency is a
Contract Change Request, not an edit.

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-tier-validator
mkdir -p access/secrets/schemas access/secrets/tools \
         access/secrets/testdata/tiers-bad-rank access/secrets/testdata/tiers-bad-location
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/schemas/secret-tier.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "access/secrets/schemas/secret-tier.schema.json",
  "title": "Secret tier (Section 40.1, lines 3648-3654)",
  "description": "One file per tier. Five files exist and no sixth: Section 40.2 line 3689 states that provider-SSO federation with no long-lived key is why the tiers remain exactly five.",
  "type": "object",
  "required": [
    "schema_version",
    "tier_id",
    "rank",
    "tier",
    "location",
    "contains",
    "spec_anchor",
    "spec_lines",
    "holds_production_credentials"
  ],
  "properties": {
    "schema_version": { "type": "integer", "const": 1 },
    "tier_id": {
      "type": "string",
      "enum": ["developer", "ci", "staging", "production", "control_plane"]
    },
    "rank": { "type": "integer", "minimum": 1, "maximum": 5 },
    "tier": {
      "type": "string",
      "enum": ["Developer", "CI", "Staging", "Production", "Control plane"]
    },
    "location": { "type": "string" },
    "contains": { "type": "string" },
    "spec_anchor": { "type": "string", "const": "Section 40.1" },
    "spec_lines": { "type": "string", "const": "3648-3654" },
    "holds_production_credentials": { "type": "boolean" }
  }
}
JSONEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/tools/validate_tiers.py <<'PYEOF'
#!/usr/bin/env python3
"""Validate access/secrets/tiers/*.yaml against secret-tier.schema.json.

Section 40.1, lines 3648-3654. Invariant 87: enforced by the platform wherever
the platform can enforce it.

Uses only the standard library plus PyYAML - the two things the phase preflight
proves. It implements the schema subset it needs (required, type, enum, const,
minimum, maximum) rather than importing a schema-validation library, because
adding a dependency is a Contract Change Request, not an edit.

Fail-closed (invariant 80): an unreadable schema, an unreadable tier file or a
missing directory is a FAILURE, never a pass.

Usage:  validate_tiers.py [<tiers-dir>]
Prints one RESULT line last and exits 0 only when every rule holds.
"""
import glob
import json
import os
import sys

import yaml

SCHEMA = os.path.join("access", "secrets", "schemas", "secret-tier.schema.json")
EXPECTED_LOCATIONS = {
    "developer": ".env.local, git-ignored",
    "ci": "GitHub Actions secrets",
    "staging": "GitHub Environment: staging",
    "production": "GitHub Environment: production",
    "control_plane": "Machine-credential store on the hosts that use them",
}
EXPECTED_RANKS = {
    "developer": 1,
    "ci": 2,
    "staging": 3,
    "production": 4,
    "control_plane": 5,
}
TYPES = {
    "object": dict,
    "string": str,
    "integer": int,
    "boolean": bool,
    "array": list,
}


def check_node(value, node, path, errors):
    kind = node.get("type")
    if kind is not None:
        expected = TYPES[kind]
        if expected is int and isinstance(value, bool):
            errors.append("%s: expected integer, got boolean" % path)
            return
        if not isinstance(value, expected):
            errors.append("%s: expected %s, got %s"
                          % (path, kind, type(value).__name__))
            return
    if "const" in node and value != node["const"]:
        errors.append("%s: expected const %r, got %r" % (path, node["const"], value))
    if "enum" in node and value not in node["enum"]:
        errors.append("%s: %r not in enum %r" % (path, value, node["enum"]))
    if "minimum" in node and isinstance(value, int) and value < node["minimum"]:
        errors.append("%s: %r below minimum %r" % (path, value, node["minimum"]))
    if "maximum" in node and isinstance(value, int) and value > node["maximum"]:
        errors.append("%s: %r above maximum %r" % (path, value, node["maximum"]))


def validate_one(doc, schema, path, errors):
    if not isinstance(doc, dict):
        errors.append("%s: document is not a mapping" % path)
        return
    for key in schema.get("required", []):
        if key not in doc:
            errors.append("%s: missing required key %r" % (path, key))
    props = schema.get("properties", {})
    for key, value in doc.items():
        if key in props:
            check_node(value, props[key], "%s:%s" % (path, key), errors)


def main(argv):
    tiers_dir = argv[1] if len(argv) > 1 else os.path.join("access", "secrets", "tiers")
    errors = []
    if not os.path.isfile(SCHEMA):
        print("RESULT FAIL schema-unreadable %s" % SCHEMA)
        return 2
    try:
        with open(SCHEMA, "r", encoding="utf-8") as handle:
            schema = json.load(handle)
    except Exception as exc:                                    # fail closed
        print("RESULT FAIL schema-unparseable %s" % exc)
        return 2
    files = sorted(glob.glob(os.path.join(tiers_dir, "*.yaml")))
    if not files:
        print("RESULT FAIL no-tier-files %s" % tiers_dir)
        return 2
    docs = {}
    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                doc = yaml.safe_load(handle)
        except Exception as exc:                                # fail closed
            errors.append("%s: unparseable (%s)" % (path, exc))
            continue
        validate_one(doc, schema, path, errors)
        if isinstance(doc, dict) and "tier_id" in doc:
            docs.setdefault(doc["tier_id"], []).append((path, doc))
    for tier_id, entries in sorted(docs.items()):
        if len(entries) > 1:
            errors.append("tier_id %r declared in %d files" % (tier_id, len(entries)))
        path, doc = entries[0]
        if doc.get("rank") != EXPECTED_RANKS.get(tier_id):
            errors.append("%s: rank %r is not the Section 40.1 table position %r"
                          % (path, doc.get("rank"), EXPECTED_RANKS.get(tier_id)))
        if doc.get("location") != EXPECTED_LOCATIONS.get(tier_id):
            errors.append("%s: location is not the Section 40.1 table string" % path)
    for tier_id in sorted(set(EXPECTED_RANKS) - set(docs)):
        errors.append("tier %r has no file" % tier_id)
    for tier_id in sorted(set(docs) - set(EXPECTED_RANKS)):
        errors.append("tier %r is not one of the five tiers of Section 40.1" % tier_id)
    holders = sorted(tid for tid, entries in docs.items()
                     if entries[0][1].get("holds_production_credentials"))
    if holders != ["production"]:
        errors.append("exactly one tier must hold production credentials; got %r"
                      % holders)
    if errors:
        for line in errors:
            print("ERROR %s" % line)
        print("RESULT FAIL %d" % len(errors))
        return 1
    print("RESULT PASS 5")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
PYEOF
chmod +x access/secrets/tools/validate_tiers.py
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/testdata/tiers-bad-rank/tier-x.yaml <<'YAMLEOF'
# NEGATIVE FIXTURE. This file MUST fail validate_tiers.py.
# It puts the production tier at rank 2, which would make a staging credential
# read as "above" production and silently invert the never-moves-down check.
schema_version: 1
tier_id: production
rank: 2
tier: "Production"
location: "GitHub Environment: production"
contains: "Production credentials, accessible only to the production deployment workflow"
spec_anchor: "Section 40.1"
spec_lines: "3648-3654"
holds_production_credentials: true
YAMLEOF

cat > access/secrets/testdata/tiers-bad-location/tier-y.yaml <<'YAMLEOF'
# NEGATIVE FIXTURE. This file MUST fail validate_tiers.py.
# The location is paraphrased rather than copied from the Section 40.1 table.
schema_version: 1
tier_id: control_plane
rank: 5
tier: "Control plane"
location: "on the ops box"
contains: "Machine credentials"
spec_anchor: "Section 40.1"
spec_lines: "3648-3654"
holds_production_credentials: false
YAMLEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/secrets/schemas access/secrets/tools/validate_tiers.py access/secrets/testdata
git commit -m "L5-02-02: tier registry schema, validator and two executed negative fixtures (Section 40.1)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-tier-validator
gh pr create --base integration \
  --title "L5-02-02 Tier registry schema and validator" \
  --body "Lane 5, Phase 2, task L5-02-02. Spec: Section 40.1 lines 3644-3656, invariant 87 line 9567. Paths: access/secrets/schemas/**, access/secrets/tools/validate_tiers.py, access/secrets/testdata/**. Self-verify output pasted below."
```

### Acceptance criteria

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | The real registry validates | `python access/secrets/tools/validate_tiers.py` | `RESULT PASS 5` |
| 2 | It exits 0 | `python access/secrets/tools/validate_tiers.py >/dev/null; echo $?` | `0` |
| 3 | Negative fixture 1 (wrong rank) is rejected with five findings | `python access/secrets/tools/validate_tiers.py access/secrets/testdata/tiers-bad-rank \| tail -1` | `RESULT FAIL 5` |
| 4 | Negative fixture 1 exits 1 | `python access/secrets/tools/validate_tiers.py access/secrets/testdata/tiers-bad-rank >/dev/null; echo $?` | `1` |
| 5 | Negative fixture 2 (paraphrased location) exits 1 | `python access/secrets/tools/validate_tiers.py access/secrets/testdata/tiers-bad-location >/dev/null; echo $?` | `1` |
| 6 | The validator fails closed on a missing directory | `python access/secrets/tools/validate_tiers.py access/secrets/testdata/nope \| tail -1` | `RESULT FAIL no-tier-files access/secrets/testdata/nope` |
| 7 | The validator imports no schema-validation library | `grep -c jsonschema access/secrets/tools/validate_tiers.py` | `0` |
| 8 | No file outside `access/secrets/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/secrets/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python access/secrets/tools/validate_tiers.py | tail -1
python access/secrets/tools/validate_tiers.py access/secrets/testdata/tiers-bad-rank >/dev/null 2>&1; echo "NEG-RANK-EXIT $?"
python access/secrets/tools/validate_tiers.py access/secrets/testdata/tiers-bad-location >/dev/null 2>&1; echo "NEG-LOCATION-EXIT $?"
python access/secrets/tools/validate_tiers.py access/secrets/testdata/nope >/dev/null 2>&1; echo "FAIL-CLOSED-EXIT $?"
echo "L5-02-02 SELF-VERIFY PASS"
```

Expected output, exactly:

```
RESULT PASS 5
NEG-RANK-EXIT 1
NEG-LOCATION-EXIT 1
FAIL-CLOSED-EXIT 2
L5-02-02 SELF-VERIFY PASS
```

### STOP rule

STOP — do not commit, do not push, file the blocker of Section 4 — if any of these hold:

* Either negative fixture **passes** the validator. A validator that accepts a paraphrased §40.1 string
  cannot enforce the rule it exists for. Class `shape-mismatch`.
* `python access/secrets/tools/validate_tiers.py` raises a traceback instead of printing a `RESULT` line.
  A traceback is not a fail-closed result. Class `toolchain`.
* The executor is tempted to install a schema-validation package to shorten the validator. Class
  `needs-decision` — the dependency set is a contract, and this file's preflight pins exactly PyYAML.

---

## L5-02-03 — The never-moves-down-a-tier check

| Field | Value |
|---|---|
| Task id | `L5-02-03` |
| Size | M |
| Depends on | `L5-02-01`, `L5-02-02` |
| Slug | `downward-move` |
| Subsystem | L |
| Spec | §40.1 line 3656; §43 (Security Incident Workflow) lines 3853–3870; §53.4 lines 4704–4716; invariant 25 line 9487; invariant 80 line 9557 |
| Writes | `access/secrets/checks/check_no_downward_move.py`, `access/secrets/checks/check-no-downward-move.sh`, `access/secrets/checks/downward-move.classification.yaml`, `access/secrets/testdata/downward-move/clean/access-inputs.yaml`, `access/secrets/testdata/downward-move/collision/access-inputs.yaml`, `access/secrets/testdata/downward-move/envleak/access-inputs.yaml`, `access/secrets/testdata/downward-move/envleak/workstation/.env.local` |

### Purpose

§40.1 line 3656 is one sentence and two rules: *"A secret never moves down a tier. A production credential
appearing anywhere below the production tier is a security incident under Section 43 (Security Incident
Workflow), not a cleanup task."* The second half is the half that gets lost. A check that files a
housekeeping ticket has implemented the first rule and discarded the second, so this check emits the
classification in its own output and carries it in a declaration file beside it.

Two detections, both mechanical:

1. **Registry collision.** A secret name declared in the tier of rank *R* must not appear in any tier of
   rank below *R*. Ranks come from T01; names come from the frozen contract's `secret_name_registry`.
2. **Filesystem leak.** No production-tier secret name appears in any file named `.env`, `.env.*` or
   `*.env` anywhere under the scan root. The scan walks the **filesystem**, not the git index, precisely
   because the developer tier is `.env.local`, *git-ignored* — a check that only reads tracked files cannot
   see the tier the rule is about.

The check never prints a secret *value*; it has none to print. It prints names, because a finding that does
not say which credential moved is not actionable.

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-downward-move
mkdir -p access/secrets/checks \
         access/secrets/testdata/downward-move/clean \
         access/secrets/testdata/downward-move/collision \
         access/secrets/testdata/downward-move/envleak/workstation
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/checks/check_no_downward_move.py <<'PYEOF'
#!/usr/bin/env python3
"""The never-moves-down-a-tier check.

Section 40.1, line 3656:
  "A secret never moves down a tier. A production credential appearing anywhere
   below the production tier is a security incident under Section 43 (Security
   Incident Workflow), not a cleanup task."

Two detections:
  R1 registry-collision - a name declared in a tier of rank R also appears in a
     tier of lower rank.
  R2 env-file-leak      - a production-tier name appears in a file named .env,
     .env.* or *.env under the scan root. The scan walks the FILESYSTEM, not
     the git index, because the developer tier is .env.local and git-ignored.

Fail-closed (invariant 80): a missing or unparseable input is exit 2, never a
pass. A finding is exit 1 and is a SECURITY INCIDENT, not a cleanup task.

Usage:  check_no_downward_move.py [<inputs.yaml> [<scan-root>]]
Defaults: contracts/access/access-inputs.yaml  and  .
"""
import os
import sys

import yaml

TIERS_DIR = os.path.join("access", "secrets", "tiers")
TIER_KEYS = {"ci": 2, "staging": 3, "production": 4, "control_plane": 5}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def load_ranks():
    """Ranks come from the T01 registry, never from a constant here."""
    ranks = {}
    if not os.path.isdir(TIERS_DIR):
        return None
    for name in sorted(os.listdir(TIERS_DIR)):
        if not name.endswith(".yaml"):
            continue
        with open(os.path.join(TIERS_DIR, name), "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        if isinstance(doc, dict) and "tier_id" in doc and "rank" in doc:
            ranks[doc["tier_id"]] = doc["rank"]
    return ranks or None


def env_files(root):
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            if filename == ".env" or filename.startswith(".env.") \
               or filename.endswith(".env"):
                hits.append(os.path.join(dirpath, filename))
    return sorted(hits)


def main(argv):
    inputs = argv[1] if len(argv) > 1 else os.path.join(
        "contracts", "access", "access-inputs.yaml")
    scan_root = argv[2] if len(argv) > 2 else "."
    if not os.path.isfile(inputs):
        print("RESULT FAIL inputs-unreadable %s" % inputs)
        return 2
    try:
        with open(inputs, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
    except Exception as exc:                                    # fail closed
        print("RESULT FAIL inputs-unparseable %s" % exc)
        return 2
    registry = doc.get("secret_name_registry")
    if not isinstance(registry, dict):
        print("RESULT FAIL no-secret-name-registry %s" % inputs)
        return 2
    ranks = load_ranks()
    if ranks is None:
        print("RESULT FAIL tier-registry-unreadable %s" % TIERS_DIR)
        return 2
    for key in TIER_KEYS:
        if key not in ranks:
            print("RESULT FAIL tier-missing-from-registry %s" % key)
            return 2

    findings = []
    placed = {}
    for key in sorted(registry):
        if key not in TIER_KEYS:
            print("RESULT FAIL unknown-tier-key %s" % key)
            return 2
        for name in registry.get(key) or []:
            placed.setdefault(str(name), []).append(key)

    # R1 - a name held at rank R must not appear at any lower rank.
    for name, keys in sorted(placed.items()):
        if len(keys) < 2:
            continue
        top = max(ranks[k] for k in keys)
        for key in sorted(keys):
            if ranks[key] < top:
                findings.append(
                    "FINDING R1 registry-collision %s held at rank %d also declared in tier %s (rank %d)"
                    % (name, top, key, ranks[key]))

    # R2 - no production-tier name in any .env file under the scan root.
    production = [str(n) for n in (registry.get("production") or [])]
    for path in env_files(scan_root):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                body = handle.read()
        except Exception as exc:                                # fail closed
            print("RESULT FAIL env-file-unreadable %s (%s)" % (path, exc))
            return 2
        for name in production:
            if name and name in body:
                findings.append(
                    "FINDING R2 env-file-leak %s appears in %s" % (name, path))

    for line in findings:
        print(line)
    print("FINDINGS %d" % len(findings))
    if findings:
        print("CLASS security-incident")
        print("AUTHORITY Section 43 (Security Incident Workflow)")
        print("DRIFT-CLASS Blocking")
        print("IS-CLEANUP-TASK false")
        print("RESULT FAIL")
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
PYEOF
chmod +x access/secrets/checks/check_no_downward_move.py
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/checks/check-no-downward-move.sh <<'SHEOF'
#!/usr/bin/env bash
# access/secrets/checks/check-no-downward-move.sh
# Wrapper so Lane 2 has one stable command to wire into a workflow and Lane 3
# has one stable exit contract to reconcile against.
#
#   exit 0  no finding
#   exit 1  finding - SECURITY INCIDENT under Section 43, not a cleanup task
#   exit 2  input unreadable - FAIL CLOSED (invariant 80)
set -eu
python access/secrets/checks/check_no_downward_move.py "$@"
SHEOF
chmod +x access/secrets/checks/check-no-downward-move.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/checks/downward-move.classification.yaml <<'YAMLEOF'
# access/secrets/checks/downward-move.classification.yaml
# Section 40.1 line 3656; Section 43; Section 53.4 lines 4704-4716.
schema_version: 1
control_id: secret-tier-downward-move
title: "A secret never moves down a tier"
implemented_by: "access/secrets/checks/check-no-downward-move.sh"
classification: fail-closed          # Section 64.2, invariant 80
on_input_unreadable: fail            # exit 2, never a pass
finding_class: security-incident     # NOT a cleanup task - Section 40.1 line 3656
finding_authority: "Section 43 (Security Incident Workflow)"
finding_drift_class: Blocking        # Section 53.4 - the only severity scale
response_time: immediate
detections:
  - id: R1
    name: registry-collision
    reads: "contracts/access/access-inputs.yaml secret_name_registry"
  - id: R2
    name: env-file-leak
    reads: "every .env, .env.* and *.env file under the scan root, walked on the filesystem because the developer tier is git-ignored"
invariants: [25, 80]
executed_by: "Lane 2 workflow (handoff HO-01); also runnable by hand"
YAMLEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/testdata/downward-move/clean/access-inputs.yaml <<'YAMLEOF'
# POSITIVE FIXTURE. Disjoint tiers. check_no_downward_move.py MUST pass.
schema_version: 1
secret_name_registry:
  production: ["FIXTURE_PROD_DB_URL", "FIXTURE_PROD_SIGNING_KEY"]
  staging: ["FIXTURE_STAGING_DB_URL"]
  ci: ["FIXTURE_SCAN_TOKEN"]
  control_plane: ["FIXTURE_RECONCILER_APP_ID"]
YAMLEOF

cat > access/secrets/testdata/downward-move/collision/access-inputs.yaml <<'YAMLEOF'
# NEGATIVE FIXTURE (R1). A production credential name is also declared in the
# staging tier - the exact "moves down a tier" condition of Section 40.1
# line 3656. check_no_downward_move.py MUST fail with exit 1.
schema_version: 1
secret_name_registry:
  production: ["FIXTURE_PROD_DB_URL", "FIXTURE_PROD_SIGNING_KEY"]
  staging: ["FIXTURE_STAGING_DB_URL", "FIXTURE_PROD_DB_URL"]
  ci: ["FIXTURE_SCAN_TOKEN"]
  control_plane: ["FIXTURE_RECONCILER_APP_ID"]
YAMLEOF

cat > access/secrets/testdata/downward-move/envleak/access-inputs.yaml <<'YAMLEOF'
# NEGATIVE FIXTURE (R2), registry half. The registry itself is clean; the leak
# is on the filesystem, in the git-ignored developer tier.
schema_version: 1
secret_name_registry:
  production: ["FIXTURE_PROD_DB_URL"]
  staging: ["FIXTURE_STAGING_DB_URL"]
  ci: ["FIXTURE_SCAN_TOKEN"]
  control_plane: ["FIXTURE_RECONCILER_APP_ID"]
YAMLEOF

cat > access/secrets/testdata/downward-move/envleak/workstation/.env.local <<'ENVEOF'
# NEGATIVE FIXTURE (R2), filesystem half. A production credential NAME has
# appeared in the developer tier. The value here is the literal string
# "not-a-real-value" - this fixture carries no credential.
FIXTURE_PROD_DB_URL=not-a-real-value
ENVEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/secrets/checks access/secrets/testdata/downward-move
git commit -m "L5-02-03: the never-moves-down-a-tier check, classed as a security incident (Section 40.1)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-downward-move
gh pr create --base integration \
  --title "L5-02-03 The never-moves-down-a-tier check" \
  --body "Lane 5, Phase 2, task L5-02-03. Spec: Section 40.1 line 3656, Section 43, Section 53.4, invariants 25 and 80. Paths: access/secrets/checks/**, access/secrets/testdata/downward-move/**. Self-verify output pasted below."
```

### Acceptance criteria

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | The clean fixture passes | `python access/secrets/checks/check_no_downward_move.py access/secrets/testdata/downward-move/clean/access-inputs.yaml access/secrets/testdata/downward-move/clean \| tail -1` | `RESULT PASS` |
| 2 | The clean fixture exits 0 | `python access/secrets/checks/check_no_downward_move.py access/secrets/testdata/downward-move/clean/access-inputs.yaml access/secrets/testdata/downward-move/clean >/dev/null; echo $?` | `0` |
| 3 | The R1 collision fixture is detected | `python access/secrets/checks/check_no_downward_move.py access/secrets/testdata/downward-move/collision/access-inputs.yaml access/secrets/testdata/downward-move/collision \| grep -c '^FINDING R1'` | `1` |
| 4 | The R1 fixture exits 1 | `python access/secrets/checks/check_no_downward_move.py access/secrets/testdata/downward-move/collision/access-inputs.yaml access/secrets/testdata/downward-move/collision >/dev/null; echo $?` | `1` |
| 5 | The R2 env-file leak is detected | `python access/secrets/checks/check_no_downward_move.py access/secrets/testdata/downward-move/envleak/access-inputs.yaml access/secrets/testdata/downward-move/envleak \| grep -c '^FINDING R2'` | `1` |
| 6 | A finding is classed as a security incident, not a cleanup task | `python access/secrets/checks/check_no_downward_move.py access/secrets/testdata/downward-move/collision/access-inputs.yaml access/secrets/testdata/downward-move/collision \| grep '^IS-CLEANUP-TASK'` | `IS-CLEANUP-TASK false` |
| 7 | A finding carries the §53.4 class | `python access/secrets/checks/check_no_downward_move.py access/secrets/testdata/downward-move/collision/access-inputs.yaml access/secrets/testdata/downward-move/collision \| grep '^DRIFT-CLASS'` | `DRIFT-CLASS Blocking` |
| 8 | The check fails closed on a missing input | `python access/secrets/checks/check_no_downward_move.py access/secrets/testdata/downward-move/nope.yaml . >/dev/null; echo $?` | `2` |
| 9 | The real contract passes on the real repository | `bash access/secrets/checks/check-no-downward-move.sh \| tail -1` | `RESULT PASS` |
| 10 | No file outside `access/secrets/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/secrets/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
D=access/secrets/testdata/downward-move
python access/secrets/checks/check_no_downward_move.py $D/clean/access-inputs.yaml $D/clean | tail -1
python access/secrets/checks/check_no_downward_move.py $D/collision/access-inputs.yaml $D/collision | grep -E '^(FINDINGS|CLASS|DRIFT-CLASS|IS-CLEANUP-TASK|RESULT)'
python access/secrets/checks/check_no_downward_move.py $D/envleak/access-inputs.yaml $D/envleak | grep -E '^(FINDINGS|RESULT)'
python access/secrets/checks/check_no_downward_move.py $D/nope.yaml . >/dev/null 2>&1; echo "FAIL-CLOSED-EXIT $?"
bash access/secrets/checks/check-no-downward-move.sh | tail -1
echo "L5-02-03 SELF-VERIFY PASS"
```

Expected output, exactly:

```
RESULT PASS
FINDINGS 1
CLASS security-incident
DRIFT-CLASS Blocking
IS-CLEANUP-TASK false
RESULT FAIL
FINDINGS 1
RESULT FAIL
FAIL-CLOSED-EXIT 2
RESULT PASS
L5-02-03 SELF-VERIFY PASS
```

### STOP rule

STOP — do not commit, do not push, file the blocker of Section 4 — if any of these hold:

* **Criterion 9 fails on the real contract.** A real `RESULT FAIL` here is not a task failure: it is a
  live finding that a production credential name sits below the production tier. Do not "fix" the
  registry, do not delete the offending file, do not rewrite history. §40.1 line 3656 classifies this as a
  **security incident under §43**, and §43.1 orders the response DETECT → CLASSIFY → CONTAIN → PRESERVE
  EVIDENCE → ROTATE, with *"Do not delete. Do not force-push. Do not rotate before capturing."* File the
  blocker, class `needs-decision`, title it `security incident: production credential below production
  tier`, paste the `FINDING` lines verbatim, and stop.
* The clean fixture fails, or either negative fixture passes. Class `shape-mismatch`.
* The contract's `secret_name_registry` carries a key that is not one of `production`, `staging`, `ci`,
  `control_plane`. The check exits 2 by design. Class `shape-mismatch`.

---

## L5-02-04 — Fifth-tier credential inventory entries (five credentials)

| Field | Value |
|---|---|
| Task id | `L5-02-04` |
| Size | M |
| Depends on | `L5-02-01` |
| Slug | `fifth-tier` |
| Subsystem | L, feeding Q |
| Spec | §40.1 line 3683 ("Fifth-tier operations"); §49.1 lines 4338–4342; §14.4 lines 1256–1267; §51.5 line 4502; D89; D107 |
| Writes | `access/secrets/tools/emit_fifth_tier.py`, `access/secrets/schemas/fifth-tier-credential.schema.json`, `access/secrets/fifth-tier/reconciler.yaml`, `access/secrets/fifth-tier/provisioning-cli.yaml`, `access/secrets/fifth-tier/organisation-export-token.yaml`, `access/secrets/fifth-tier/records-writer.yaml`, `access/secrets/fifth-tier/layer-b-backup.yaml` |

### Purpose

§40.1 line 3683 names five machine credentials and, for each, five things the record must carry: rotation
cadence (initial value quarterly), named rotator (a holder of the DevOps capability), a link to the
rotation runbook, its declared behavioural envelope, and **the named owner of that envelope's alert
configuration** — "so the alert on a run outside the envelope is itself an owned control, not an unowned
hope."

**The executor names nobody.** Every person id is read from the frozen contract. The emitter is the task:
one command reads `contracts/access/access-inputs.yaml` and writes five files. If the contract is missing a
rotator, an alert-config owner, a source host, a schedule or a permission set for any of the five, the
emitter refuses to write anything at all and the STOP rule fires — a partially populated fifth tier is
worse than none, because it reads as complete.

**Two fields are deliberately not narrowed.** §40.1 says each credential is "a least-privilege GitHub App
or fine-grained PAT (the backup credential, an append-only object-store credential)". For the backup
credential the spec fixes the kind; for the records-writer it fixes it too ("a GitHub App installation
token whose fine-grained `contents: write` is scoped to this repository alone"). For the other three it
permits either, so the entry carries the spec's own phrase and `kind_narrowed: false`. Narrowing it is a
recorded decision by L0, not an executor's choice.

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-fifth-tier
mkdir -p access/secrets/fifth-tier access/secrets/schemas access/secrets/tools
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/schemas/fifth-tier-credential.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "access/secrets/schemas/fifth-tier-credential.schema.json",
  "title": "Fifth-tier machine credential (Section 40.1, line 3683)",
  "description": "One file per control-plane machine credential. The five required record fields are rotation cadence, named rotator, runbook link, declared behavioural envelope, and the named owner of that envelope's alert configuration.",
  "type": "object",
  "required": [
    "schema_version",
    "credential_id",
    "tier_id",
    "rank",
    "location",
    "kind",
    "kind_narrowed",
    "host",
    "rotation_cadence",
    "rotator",
    "rotator_capability_required",
    "runbook",
    "envelope",
    "envelope_alert_owner",
    "permission_set",
    "reissue_source",
    "compromise_class",
    "spec_anchor",
    "spec_lines"
  ],
  "properties": {
    "schema_version": { "type": "integer", "const": 1 },
    "credential_id": {
      "type": "string",
      "enum": [
        "reconciler",
        "provisioning-cli",
        "organisation-export-token",
        "records-writer",
        "layer-b-backup"
      ]
    },
    "tier_id": { "type": "string", "const": "control_plane" },
    "rank": { "type": "integer", "const": 5 },
    "location": {
      "type": "string",
      "const": "Machine-credential store on the hosts that use them"
    },
    "kind": { "type": "string" },
    "kind_narrowed": { "type": "boolean" },
    "host": { "type": "string" },
    "rotation_cadence": { "type": "string", "const": "quarterly" },
    "rotator": { "type": "string" },
    "rotator_capability_required": { "type": "string", "const": "devops" },
    "runbook": {
      "type": "string",
      "const": "access/secrets/runbooks/rotate-fifth-tier-credential.md"
    },
    "envelope": { "type": "string" },
    "envelope_alert_owner": { "type": "string" },
    "permission_set": { "type": "array", "minItems": 1 },
    "reissue_source": { "type": "string", "const": "Section 14.4 escrow" },
    "compromise_class": { "type": "string", "const": "security-incident" },
    "spec_anchor": { "type": "string", "const": "Section 40.1" },
    "spec_lines": { "type": "string", "const": "3683" }
  }
}
JSONEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/tools/emit_fifth_tier.py <<'PYEOF'
#!/usr/bin/env python3
"""Emit the five fifth-tier credential entries from the frozen contract.

Section 40.1 line 3683 ("Fifth-tier operations"); Section 49.1 lines 4338-4342;
Section 14.4 lines 1256-1267 (the escrow is the re-issue source); Section 51.5
line 4502 (why this tier lives on the operations VM).

This program CHOOSES NOTHING. Every person id, host and permission string is
read from contracts/access/access-inputs.yaml. If any of the five credentials
is missing any required contract value, nothing is written at all: a partially
populated fifth tier reads as complete and is worse than none.

Usage:  emit_fifth_tier.py [<inputs.yaml> [<out-dir>]]
Defaults: contracts/access/access-inputs.yaml  and  access/secrets/fifth-tier
"""
import os
import sys

import yaml

ORDER = [
    "reconciler",
    "provisioning-cli",
    "organisation-export-token",
    "records-writer",
    "layer-b-backup",
]
REQUIRED = [
    "rotator",
    "envelope_alert_owner",
    "expected_source_host",
    "scheduled_runs_per_day",
    "permission_set",
]
SPEC_KIND = "least-privilege GitHub App or fine-grained PAT"
KIND = {
    "reconciler": (SPEC_KIND, False),
    "provisioning-cli": (SPEC_KIND, False),
    "organisation-export-token": (SPEC_KIND, False),
    "records-writer": (
        "GitHub App installation token whose fine-grained contents: write is scoped to the records repository alone",
        True),
    "layer-b-backup": ("append-only object-store credential", True),
}
NOTES = {
    "reconciler": [
        "Section 99.6 risk 6: the reconciler is the highest-privilege identity in the system.",
        "Its declared bounds are executed by AT-110, not asserted, and re-executed at every rotation.",
        "Section 26.4: the declared repair scope is the only machine write path on the control-plane repository.",
        "D89: no bypass actor exists on the control-plane repository.",
        "It additionally holds check-run write on product repositories for exactly one named check; a check run carries status only, writes no repository content, approves nothing, and satisfies no gate a human is required to satisfy (Section 40.1).",
    ],
    "provisioning-cli": [
        "Provisioning applies declared access state; it never authors it.",
    ],
    "organisation-export-token": [
        "Section 45.3: the organisation export is the off-site anchor; its target is object-locked.",
        "Section 40.3: this token plus the reconciler credential are why the second trust boundary exists.",
    ],
    "records-writer": [
        "D89: the record stores live in their own repository; this credential holds nothing on the control-plane repository at all.",
        "D107: append-only is enforced by a no-bypass ruleset, signed commits and a per-run SHA anchor - not by review.",
    ],
    "layer-b-backup": [
        "Section 51.4: append-only and write-only, to object-locked versioned storage in a different provider and credential domain than the operations VM.",
        "The party who can write the backup can neither read it nor destroy backup history.",
        "Custody of the backup encryption key is the Section 14.4 escrow.",
    ],
}


def fail(message):
    print("RESULT FAIL %s" % message)
    return 2


def main(argv):
    inputs = argv[1] if len(argv) > 1 else os.path.join(
        "contracts", "access", "access-inputs.yaml")
    out_dir = argv[2] if len(argv) > 2 else os.path.join(
        "access", "secrets", "fifth-tier")
    if not os.path.isfile(inputs):
        return fail("inputs-unreadable %s" % inputs)
    try:
        with open(inputs, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
    except Exception as exc:                                    # fail closed
        return fail("inputs-unparseable %s" % exc)
    block = doc.get("fifth_tier")
    if not isinstance(block, dict):
        return fail("no-fifth_tier-block %s" % inputs)
    missing = []
    for cred in ORDER:
        entry = block.get(cred)
        if not isinstance(entry, dict):
            missing.append("%s: absent" % cred)
            continue
        for key in REQUIRED:
            value = entry.get(key)
            if value is None or value == "" or value == []:
                missing.append("%s: %s" % (cred, key))
    if missing:
        for line in missing:
            print("MISSING %s" % line)
        return fail("%d-missing-contract-values" % len(missing))

    os.makedirs(out_dir, exist_ok=True)
    for cred in ORDER:
        entry = block[cred]
        kind, narrowed = KIND[cred]
        lines = []
        lines.append("# %s/%s.yaml" % (out_dir, cred))
        lines.append("# Generated by access/secrets/tools/emit_fifth_tier.py from")
        lines.append("# contracts/access/access-inputs.yaml. Do not hand-edit: re-run the emitter.")
        lines.append("# Section 40.1 line 3683; Section 49.1 lines 4338-4342.")
        lines.append("schema_version: 1")
        lines.append("credential_id: %s" % cred)
        lines.append("tier_id: control_plane")
        lines.append("rank: 5")
        lines.append('location: "Machine-credential store on the hosts that use them"')
        lines.append('kind: "%s"' % kind)
        lines.append("kind_narrowed: %s" % ("true" if narrowed else "false"))
        if not narrowed:
            lines.append('kind_narrowing_authority: "L0 - Section 40.1 permits either; narrowing is a recorded decision, never an executor choice"')
        lines.append('host: "%s"' % entry["expected_source_host"])
        lines.append("rotation_cadence: quarterly")
        lines.append('rotation_cadence_status: "calibrated configuration; initial value quarterly (Section 40.1 line 3683)"')
        lines.append('rotator: "%s"' % entry["rotator"])
        lines.append("rotator_capability_required: devops")
        lines.append('runbook: "access/secrets/runbooks/rotate-fifth-tier-credential.md"')
        lines.append('envelope: "access/secrets/envelope/%s.envelope.yaml"' % cred)
        lines.append('envelope_alert_owner: "%s"' % entry["envelope_alert_owner"])
        lines.append("scheduled_runs_per_day: %d" % int(entry["scheduled_runs_per_day"]))
        lines.append("permission_set:")
        for permission in entry["permission_set"]:
            lines.append('  - "%s"' % permission)
        lines.append('permission_set_published_at: "access/published/secret-tiers.v1.json"')
        lines.append('reissue_source: "Section 14.4 escrow"')
        lines.append("compromise_class: security-incident")
        lines.append('compromise_authority: "Section 43 (Security Incident Workflow)"')
        lines.append('inventory_entry_owner: "L5-05-02 -> assets/inventory/machine-credential-%s.yaml"' % cred)
        lines.append('spec_anchor: "Section 40.1"')
        lines.append('spec_lines: "3683"')
        lines.append("notes:")
        for note in NOTES[cred]:
            lines.append('  - "%s"' % note)
        body = "\n".join(lines) + "\n"
        with open(os.path.join(out_dir, "%s.yaml" % cred), "w",
                  encoding="utf-8", newline="\n") as handle:
            handle.write(body)
        print("WROTE %s/%s.yaml" % (out_dir, cred))
    print("RESULT PASS %d" % len(ORDER))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
PYEOF
chmod +x access/secrets/tools/emit_fifth_tier.py
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python access/secrets/tools/emit_fifth_tier.py
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/secrets/tools/emit_fifth_tier.py access/secrets/schemas/fifth-tier-credential.schema.json access/secrets/fifth-tier
git commit -m "L5-02-04: fifth-tier credential entries for the five control-plane machine credentials (Section 40.1)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-fifth-tier
gh pr create --base integration \
  --title "L5-02-04 Fifth-tier credential inventory entries (five credentials)" \
  --body "Lane 5, Phase 2, task L5-02-04. Spec: Section 40.1 line 3683, Section 49.1 lines 4338-4342, Section 14.4, Section 51.5, D89, D107. Paths: access/secrets/fifth-tier/**, access/secrets/tools/emit_fifth_tier.py, access/secrets/schemas/fifth-tier-credential.schema.json. Self-verify output pasted below."
```

### Acceptance criteria

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | Exactly five entries exist | `ls access/secrets/fifth-tier/*.yaml \| wc -l` | `5` |
| 2 | The five ids are the §40.1 five | `python -c "import glob,os;print(','.join(sorted(os.path.basename(p)[:-5] for p in glob.glob('access/secrets/fifth-tier/*.yaml'))))"` | `layer-b-backup,organisation-export-token,provisioning-cli,reconciler,records-writer` |
| 3 | Every entry carries a non-empty rotator | `python -c "import glob,yaml;print(sum(1 for f in glob.glob('access/secrets/fifth-tier/*.yaml') if (yaml.safe_load(open(f)).get('rotator') or '').strip()))"` | `5` |
| 4 | Every entry carries a named envelope-alert owner | `python -c "import glob,yaml;print(sum(1 for f in glob.glob('access/secrets/fifth-tier/*.yaml') if (yaml.safe_load(open(f)).get('envelope_alert_owner') or '').strip()))"` | `5` |
| 5 | Every entry's rotation cadence is quarterly | `python -c "import glob,yaml;print(set(yaml.safe_load(open(f))['rotation_cadence'] for f in glob.glob('access/secrets/fifth-tier/*.yaml')))"` | `{'quarterly'}` |
| 6 | Every entry links the one rotation runbook | `python -c "import glob,yaml;print(set(yaml.safe_load(open(f))['runbook'] for f in glob.glob('access/secrets/fifth-tier/*.yaml')))"` | `{'access/secrets/runbooks/rotate-fifth-tier-credential.md'}` |
| 7 | Every entry publishes a non-empty permission set | `python -c "import glob,yaml;print(min(len(yaml.safe_load(open(f))['permission_set']) for f in glob.glob('access/secrets/fifth-tier/*.yaml')))"` | a number `>= 1` |
| 8 | The re-issue source is the §14.4 escrow on all five | `python -c "import glob,yaml;print(set(yaml.safe_load(open(f))['reissue_source'] for f in glob.glob('access/secrets/fifth-tier/*.yaml')))"` | `{'Section 14.4 escrow'}` |
| 9 | The emitter is idempotent — a re-run changes nothing | `python access/secrets/tools/emit_fifth_tier.py >/dev/null && git diff --exit-code -- access/secrets/fifth-tier >/dev/null; echo $?` | `0` |
| 10 | The emitter refuses a contract missing a value | `printf 'schema_version: 1\nfifth_tier:\n  reconciler: {}\n' > /tmp/bad.yaml; python access/secrets/tools/emit_fifth_tier.py /tmp/bad.yaml /tmp/out >/dev/null; echo $?` | `2` |
| 11 | The refused run wrote nothing | `test -d /tmp/out; echo $?` | `1` |
| 12 | No file outside `access/secrets/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/secrets/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python - <<'PYEOF'
import glob, os, yaml
paths = sorted(glob.glob('access/secrets/fifth-tier/*.yaml'))
print("FIFTH-TIER-ENTRIES %d" % len(paths))
for path in paths:
    d = yaml.safe_load(open(path, encoding='utf-8'))
    print("ENTRY %s cadence=%s rotator=%s alert_owner=%s perms=%d"
          % (d['credential_id'], d['rotation_cadence'],
             'set' if str(d['rotator']).strip() else 'MISSING',
             'set' if str(d['envelope_alert_owner']).strip() else 'MISSING',
             len(d['permission_set'])))
print("RUNBOOKS %d" % len(set(yaml.safe_load(open(p, encoding='utf-8'))['runbook'] for p in paths)))
print("REISSUE %s" % list(set(yaml.safe_load(open(p, encoding='utf-8'))['reissue_source'] for p in paths))[0])
PYEOF
python access/secrets/tools/emit_fifth_tier.py >/dev/null && git diff --exit-code -- access/secrets/fifth-tier >/dev/null && echo "IDEMPOTENT yes"
echo "L5-02-04 SELF-VERIFY PASS"
```

Expected output, exactly (the `perms=` counts are `<varies>` — they come from the contract):

```
FIFTH-TIER-ENTRIES 5
ENTRY layer-b-backup cadence=quarterly rotator=set alert_owner=set perms=<varies>
ENTRY organisation-export-token cadence=quarterly rotator=set alert_owner=set perms=<varies>
ENTRY provisioning-cli cadence=quarterly rotator=set alert_owner=set perms=<varies>
ENTRY reconciler cadence=quarterly rotator=set alert_owner=set perms=<varies>
ENTRY records-writer cadence=quarterly rotator=set alert_owner=set perms=<varies>
RUNBOOKS 1
REISSUE Section 14.4 escrow
IDEMPOTENT yes
L5-02-04 SELF-VERIFY PASS
```

Any `MISSING` in place of `set` is a failure, and so is any `perms=0`.

### STOP rule

STOP — do not commit, do not push, file the blocker of Section 4 — if any of these hold:

* The emitter prints one or more `MISSING` lines. The contract does not name a rotator, an alert-config
  owner, a source host, a schedule or a permission set for some credential. **Do not name a person, do not
  guess a host, do not write an empty list.** Class `missing-contract`; the decision needed from L0 is
  "supply the missing `fifth_tier` values in `contracts/access/access-inputs.yaml`".
* The contract names a rotator who does not hold the DevOps capability. The entry requires
  `rotator_capability_required: devops` and §40.1 line 3683 says the rotator *is* a DevOps-capability
  holder. Class `needs-decision`.
* Criterion 9 fails — a re-run of the emitter changes files. The emitter is not deterministic and the
  published artifact of T14 cannot be byte-reproducible. Class `shape-mismatch`.

---

## L5-02-05 — Behavioural-envelope declaration and credential schema (D96)

| Field | Value |
|---|---|
| Task id | `L5-02-05` |
| Size | M |
| Depends on | `L5-02-04` |
| Slug | `envelope-declare` |
| Subsystem | L |
| Spec | §40.1 line 3685 ("The behavioural envelope"); D96 line 10189; §53.4 lines 4704–4716; §51.2 (the schedule the ceiling is computed from) |
| Writes | `access/secrets/schemas/envelope.schema.json`, `access/secrets/schemas/run-record.schema.json`, `access/secrets/tools/emit_envelopes.py`, `access/secrets/envelope/reconciler.envelope.yaml`, `access/secrets/envelope/provisioning-cli.envelope.yaml`, `access/secrets/envelope/organisation-export-token.envelope.yaml`, `access/secrets/envelope/records-writer.envelope.yaml`, `access/secrets/envelope/layer-b-backup.envelope.yaml` |

### Purpose

D96 retires temporal detection and says why: *"'Use outside its scheduled window' is near-vacuous for a
credential that legitimately fires hourly, nightly and on every registry merge, and is silent entirely for
read-side abuse."* §40.1 line 3685 puts the same point sharply — the complement of the window "is nearly
empty, an attacker simply acts inside the hour, and an alert that cannot fire is a gate that appears to be
working and is not."

The envelope replaces it with four clauses, and this task declares all four per credential:

| Clause | Value | Source |
|---|---|---|
| `signed_run_record` | required, and it names the scheduled trigger; a run with no matching trigger record is **Blocking** | §40.1 line 3685, D96 |
| `run_count_ceiling_per_day` | **computed**: `2 × scheduled_runs_per_day` from the contract. Calibrated configuration; recalibrated whenever the schedule changes | §40.1 line 3685 |
| `expected_source_host` | the contract's `expected_source_host` for that credential | §40.1 line 3685, §40.3 line 3703 |
| `published_api_call_counts` | required, per run, so read-side abuse surfaces as a volume anomaly rather than as nothing | §40.1 line 3685, D96 |

The ceiling is **computed, never chosen**: the executor supplies no number anywhere in this task.

**One clause of D96 is deliberately out of scope and routed to L0.** D96 also names "per-run caps on
objects mutated". §40.1's own envelope list at line 3685 has four items and does not include it, and the
frozen contract of Section 2 carries no key for it. The envelope files therefore record
`objects_mutated_cap: not-in-envelope-v1` with the escalation id `E-P2-01` (Section 10). The executor does
not invent a cap.

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-envelope-declare
mkdir -p access/secrets/envelope access/secrets/schemas access/secrets/tools
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/schemas/envelope.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "access/secrets/schemas/envelope.schema.json",
  "title": "Behavioural envelope for a fifth-tier credential (Section 40.1 line 3685, D96)",
  "description": "Behavioural, not temporal. A run outside the envelope is Blocking drift on the single severity scale of Section 53.4.",
  "type": "object",
  "required": [
    "schema_version",
    "credential_id",
    "temporal_window_rule",
    "signed_run_record",
    "run_count_ceiling_per_day",
    "expected_source_host",
    "published_api_call_counts",
    "outside_envelope_class",
    "alert_config_owner",
    "spec_anchor",
    "decision"
  ],
  "properties": {
    "schema_version": { "type": "integer", "const": 1 },
    "credential_id": { "type": "string" },
    "temporal_window_rule": { "type": "string", "const": "retired" },
    "signed_run_record": { "type": "object" },
    "run_count_ceiling_per_day": { "type": "object" },
    "expected_source_host": { "type": "object" },
    "published_api_call_counts": { "type": "object" },
    "outside_envelope_class": { "type": "string", "const": "Blocking" },
    "alert_config_owner": { "type": "string" },
    "spec_anchor": { "type": "string", "const": "Section 40.1" },
    "decision": { "type": "string", "const": "D96" }
  }
}
JSONEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/schemas/run-record.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "access/secrets/schemas/run-record.schema.json",
  "title": "Signed run record for a fifth-tier credential (Section 40.1 line 3685, D96)",
  "description": "One record per run. It names the scheduled trigger, so a run without a matching trigger record raises immediately. It publishes the run's API-call count, so read-side abuse surfaces as a volume anomaly.",
  "type": "object",
  "required": [
    "schema_version",
    "credential_id",
    "run_id",
    "scheduled_trigger",
    "source_host",
    "started_at",
    "finished_at",
    "api_call_count",
    "signature",
    "signer"
  ],
  "properties": {
    "schema_version": { "type": "integer", "const": 1 },
    "credential_id": { "type": "string" },
    "run_id": { "type": "string" },
    "scheduled_trigger": {
      "type": "string",
      "description": "The id of the schedule entry that caused this run. A run whose value is empty, absent or unmatched by any declared trigger is Blocking."
    },
    "source_host": { "type": "string" },
    "started_at": { "type": "string" },
    "finished_at": { "type": "string" },
    "api_call_count": { "type": "integer", "minimum": 0 },
    "signature": { "type": "string" },
    "signer": { "type": "string" }
  }
}
JSONEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/tools/emit_envelopes.py <<'PYEOF'
#!/usr/bin/env python3
"""Emit one behavioural envelope per fifth-tier credential.

Section 40.1 line 3685; D96 line 10189; Section 53.4 lines 4704-4716.

The run-count ceiling is COMPUTED - twice the scheduled run count - never
chosen. The expected source host and the alert-config owner are read from the
fifth-tier entries written by L5-02-04, which read them from the frozen
contract. This program supplies no value of its own.

Usage:  emit_envelopes.py [<fifth-tier-dir> [<out-dir>]]
Defaults: access/secrets/fifth-tier  and  access/secrets/envelope
"""
import glob
import os
import sys

import yaml

MULTIPLIER = 2   # Section 40.1 line 3685: "twice the scheduled run count"


def main(argv):
    src = argv[1] if len(argv) > 1 else os.path.join(
        "access", "secrets", "fifth-tier")
    out_dir = argv[2] if len(argv) > 2 else os.path.join(
        "access", "secrets", "envelope")
    paths = sorted(glob.glob(os.path.join(src, "*.yaml")))
    if not paths:
        print("RESULT FAIL no-fifth-tier-entries %s" % src)
        return 2
    entries = []
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                doc = yaml.safe_load(handle) or {}
        except Exception as exc:                                # fail closed
            print("RESULT FAIL entry-unparseable %s (%s)" % (path, exc))
            return 2
        for key in ("credential_id", "host", "envelope_alert_owner",
                    "scheduled_runs_per_day"):
            if not doc.get(key) and doc.get(key) != 0:
                print("RESULT FAIL entry-missing %s:%s" % (path, key))
                return 2
        runs = int(doc["scheduled_runs_per_day"])
        if runs < 1:
            print("RESULT FAIL non-positive-schedule %s" % path)
            return 2
        entries.append(doc)

    os.makedirs(out_dir, exist_ok=True)
    for doc in entries:
        cred = doc["credential_id"]
        runs = int(doc["scheduled_runs_per_day"])
        ceiling = MULTIPLIER * runs
        lines = []
        lines.append("# %s/%s.envelope.yaml" % (out_dir, cred))
        lines.append("# Generated by access/secrets/tools/emit_envelopes.py.")
        lines.append("# Do not hand-edit: re-run the emitter.")
        lines.append("# Section 40.1 line 3685; D96 line 10189; Section 53.4.")
        lines.append("schema_version: 1")
        lines.append("credential_id: %s" % cred)
        lines.append("spec_anchor: \"Section 40.1\"")
        lines.append("spec_lines: \"3685\"")
        lines.append("decision: D96")
        lines.append("temporal_window_rule: retired")
        lines.append('temporal_window_rule_reason: "Use outside its scheduled window is near-vacuous for a credential that legitimately fires hourly, nightly and on every registry merge, and is silent entirely for read-side abuse (D96)"')
        lines.append("signed_run_record:")
        lines.append("  required: true")
        lines.append("  must_name: scheduled_trigger")
        lines.append('  schema: "access/secrets/schemas/run-record.schema.json"')
        lines.append("  unmatched_run_class: Blocking")
        lines.append('  rationale: "any run without a matching trigger record raises immediately"')
        lines.append("run_count_ceiling_per_day:")
        lines.append("  scheduled_runs_per_day: %d" % runs)
        lines.append("  multiplier: %d" % MULTIPLIER)
        lines.append("  value: %d" % ceiling)
        lines.append("  computed: true")
        lines.append('  status: "calibrated configuration; initial value twice the scheduled run count"')
        lines.append('  recalibrate_when: "the schedule changes"')
        lines.append("  breach_class: Blocking")
        lines.append("expected_source_host:")
        lines.append('  value: "%s"' % doc["host"])
        lines.append("  breach_class: Blocking")
        lines.append('  rationale: "the credential is expected to be used from the host that holds it (Section 40.3 line 3703), so the envelope is host-aware and not only time-aware"')
        lines.append("published_api_call_counts:")
        lines.append("  required: true")
        lines.append("  per: run")
        lines.append("  absent_class: Blocking")
        lines.append('  rationale: "read-side abuse - enumerating and cloning every private repository - emits no webhook and no event-log entry, so it must surface as a volume anomaly rather than as nothing"')
        lines.append("objects_mutated_cap: not-in-envelope-v1")
        lines.append('objects_mutated_cap_escalation: "E-P2-01 - D96 names per-run caps on objects mutated; the Section 40.1 line 3685 envelope list does not, and the frozen contract carries no key for it. L0 decides."')
        lines.append("outside_envelope_class: Blocking")
        lines.append('severity_scale: "Section 53.4 lines 4704-4716 - the only severity scale in the system"')
        lines.append('alert_config_owner: "%s"' % doc["envelope_alert_owner"])
        lines.append("alert_config_owner_is_named_control: true")
        lines.append('alert_config_owner_rationale: "so the alert on a run outside the envelope is itself an owned control, not an unowned hope (Section 40.1 line 3683)"')
        lines.append('evaluator: "access/secrets/envelope/check-envelope.sh"')
        body = "\n".join(lines) + "\n"
        with open(os.path.join(out_dir, "%s.envelope.yaml" % cred), "w",
                  encoding="utf-8", newline="\n") as handle:
            handle.write(body)
        print("WROTE %s/%s.envelope.yaml ceiling=%d" % (out_dir, cred, ceiling))
    print("RESULT PASS %d" % len(entries))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
PYEOF
chmod +x access/secrets/tools/emit_envelopes.py
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python access/secrets/tools/emit_envelopes.py
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/secrets/schemas/envelope.schema.json access/secrets/schemas/run-record.schema.json \
        access/secrets/tools/emit_envelopes.py access/secrets/envelope
git commit -m "L5-02-05: behavioural envelope per fifth-tier credential, D96 (Section 40.1)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-envelope-declare
gh pr create --base integration \
  --title "L5-02-05 Behavioural-envelope declaration and credential schema (D96)" \
  --body "Lane 5, Phase 2, task L5-02-05. Spec: Section 40.1 line 3685, D96 line 10189, Section 53.4. Paths: access/secrets/envelope/**, access/secrets/schemas/envelope.schema.json, access/secrets/schemas/run-record.schema.json, access/secrets/tools/emit_envelopes.py. Self-verify output pasted below."
```

### Acceptance criteria

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | Exactly five envelopes exist, one per credential | `ls access/secrets/envelope/*.envelope.yaml \| wc -l` | `5` |
| 2 | Temporal detection is retired on all five | `python -c "import glob,yaml;print(set(yaml.safe_load(open(f))['temporal_window_rule'] for f in glob.glob('access/secrets/envelope/*.envelope.yaml')))"` | `{'retired'}` |
| 3 | A run outside the envelope is Blocking on all five | `python -c "import glob,yaml;print(set(yaml.safe_load(open(f))['outside_envelope_class'] for f in glob.glob('access/secrets/envelope/*.envelope.yaml')))"` | `{'Blocking'}` |
| 4 | The signed run record is required and names the trigger | `python -c "import glob,yaml;print(set((yaml.safe_load(open(f))['signed_run_record']['required'],yaml.safe_load(open(f))['signed_run_record']['must_name']) for f in glob.glob('access/secrets/envelope/*.envelope.yaml')))"` | `{(True, 'scheduled_trigger')}` |
| 5 | Every ceiling is exactly twice the scheduled run count | `python -c "import glob,yaml;print(all(yaml.safe_load(open(f))['run_count_ceiling_per_day']['value']==2*yaml.safe_load(open(f))['run_count_ceiling_per_day']['scheduled_runs_per_day'] for f in glob.glob('access/secrets/envelope/*.envelope.yaml')))"` | `True` |
| 6 | Every ceiling is marked computed, not chosen | `python -c "import glob,yaml;print(set(yaml.safe_load(open(f))['run_count_ceiling_per_day']['computed'] for f in glob.glob('access/secrets/envelope/*.envelope.yaml')))"` | `{True}` |
| 7 | Every envelope names an expected source host | `python -c "import glob,yaml;print(sum(1 for f in glob.glob('access/secrets/envelope/*.envelope.yaml') if yaml.safe_load(open(f))['expected_source_host']['value'].strip()))"` | `5` |
| 8 | Per-run API-call counts are required on all five | `python -c "import glob,yaml;print(set(yaml.safe_load(open(f))['published_api_call_counts']['required'] for f in glob.glob('access/secrets/envelope/*.envelope.yaml')))"` | `{True}` |
| 9 | Every envelope names its alert-config owner | `python -c "import glob,yaml;print(sum(1 for f in glob.glob('access/secrets/envelope/*.envelope.yaml') if yaml.safe_load(open(f))['alert_config_owner'].strip()))"` | `5` |
| 10 | The emitter is idempotent | `python access/secrets/tools/emit_envelopes.py >/dev/null && git diff --exit-code -- access/secrets/envelope >/dev/null; echo $?` | `0` |
| 11 | The emitter fails closed with no fifth-tier entries | `python access/secrets/tools/emit_envelopes.py /tmp/absent /tmp/out2 >/dev/null; echo $?` | `2` |
| 12 | No file outside `access/secrets/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/secrets/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python - <<'PYEOF'
import glob, yaml
paths = sorted(glob.glob('access/secrets/envelope/*.envelope.yaml'))
print("ENVELOPES %d" % len(paths))
ok = True
for path in paths:
    d = yaml.safe_load(open(path, encoding='utf-8'))
    c = d['run_count_ceiling_per_day']
    ok = ok and c['value'] == 2 * c['scheduled_runs_per_day']
    print("ENVELOPE %s temporal=%s outside=%s signed=%s host=%s apicounts=%s"
          % (d['credential_id'], d['temporal_window_rule'],
             d['outside_envelope_class'], d['signed_run_record']['required'],
             'set' if d['expected_source_host']['value'].strip() else 'MISSING',
             d['published_api_call_counts']['required']))
print("CEILINGS-ARE-DOUBLE %s" % ok)
PYEOF
python access/secrets/tools/emit_envelopes.py >/dev/null && git diff --exit-code -- access/secrets/envelope >/dev/null && echo "IDEMPOTENT yes"
echo "L5-02-05 SELF-VERIFY PASS"
```

Expected output, exactly:

```
ENVELOPES 5
ENVELOPE layer-b-backup temporal=retired outside=Blocking signed=True host=set apicounts=True
ENVELOPE organisation-export-token temporal=retired outside=Blocking signed=True host=set apicounts=True
ENVELOPE provisioning-cli temporal=retired outside=Blocking signed=True host=set apicounts=True
ENVELOPE reconciler temporal=retired outside=Blocking signed=True host=set apicounts=True
ENVELOPE records-writer temporal=retired outside=Blocking signed=True host=set apicounts=True
CEILINGS-ARE-DOUBLE True
IDEMPOTENT yes
L5-02-05 SELF-VERIFY PASS
```

### STOP rule

STOP — do not commit, do not push, file the blocker of Section 4 — if any of these hold:

* Any `scheduled_runs_per_day` in the contract is zero or absent. A ceiling of zero would make every run a
  breach and a ceiling computed from nothing is not computed. Class `missing-contract`.
* The executor is tempted to write a run-count ceiling by hand because the computed one "looks wrong".
  The multiplier is fixed at 2 by §40.1 line 3685; changing it is a calibration decision on the §84.5
  cadence. Class `needs-decision`.
* `CEILINGS-ARE-DOUBLE` prints `False`. Class `shape-mismatch`.

---

## L5-02-06 — Envelope evaluator: a run outside the envelope is Blocking

| Field | Value |
|---|---|
| Task id | `L5-02-06` |
| Size | M |
| Depends on | `L5-02-05` |
| Slug | `envelope-evaluate` |
| Subsystem | L |
| Spec | §40.1 line 3685; D96 line 10189; §53.4 lines 4704–4716; §53.1 (a clean run is recorded as clean); invariant 80 line 9557 |
| Writes | `access/secrets/envelope/evaluate_envelope.py`, `access/secrets/envelope/check-envelope.sh`, `access/secrets/testdata/envelope/envelopes/fixture-cred.envelope.yaml`, `access/secrets/testdata/envelope/triggers/t1.yaml`, `access/secrets/testdata/envelope/triggers/t2.yaml`, `access/secrets/testdata/envelope/triggers/t3.yaml`, `access/secrets/testdata/envelope/triggers/t4.yaml`, `access/secrets/testdata/envelope/runs-clean/*.yaml`, `access/secrets/testdata/envelope/runs-no-trigger/r1.yaml`, `access/secrets/testdata/envelope/runs-over-ceiling/*.yaml`, `access/secrets/testdata/envelope/runs-wrong-host/r1.yaml`, `access/secrets/testdata/envelope/runs-no-counts/r1.yaml`, `access/secrets/testdata/envelope/runs-unsigned/r1.yaml` |

### Purpose

The declaration of T05 is inert until something evaluates runs against it. This task ships that evaluator
and executes it against six fixtures — one clean and one per breach clause — so that every clause is proven
to fire rather than asserted to.

Five clauses, each a **Blocking** finding on the single severity scale of §53.4:

| Id | Clause | Breach |
|---|---|---|
| `E1` | signed run record naming the scheduled trigger | the run names a trigger with no matching trigger record |
| `E2` | run-count ceiling per day | more runs on one calendar day than `2 × scheduled_runs_per_day` |
| `E3` | expected source host | the run's `source_host` is not the envelope's `expected_source_host` |
| `E4` | published per-run API-call counts | the run publishes no `api_call_count` |
| `E5` | the run record is signed | `signature` or `signer` is empty |

The evaluator reads three directories — envelopes, run records, trigger records — and nothing else. It
contains no reconciler code and imports nothing from `reconciler/**` (PARTITION rule 4); Lane 3 consumes it
by its exit contract, published in Section 9.

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-envelope-evaluate
mkdir -p access/secrets/envelope \
         access/secrets/testdata/envelope/envelopes \
         access/secrets/testdata/envelope/triggers \
         access/secrets/testdata/envelope/runs-clean \
         access/secrets/testdata/envelope/runs-no-trigger \
         access/secrets/testdata/envelope/runs-over-ceiling \
         access/secrets/testdata/envelope/runs-wrong-host \
         access/secrets/testdata/envelope/runs-no-counts \
         access/secrets/testdata/envelope/runs-unsigned
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/envelope/evaluate_envelope.py <<'PYEOF'
#!/usr/bin/env python3
"""Evaluate fifth-tier credential runs against their behavioural envelopes.

Section 40.1 line 3685; D96 line 10189. A run outside the envelope is Blocking
drift on the single severity scale of Section 53.4.

Clauses, all Blocking:
  E1 unmatched-trigger        the run names a trigger with no trigger record
  E2 run-count-ceiling        more runs in one day than 2 x scheduled runs
  E3 unexpected-source-host   source_host is not the expected source host
  E4 missing-api-call-count   the run publishes no per-run API-call count
  E5 unsigned-run-record      signature or signer is empty

Fail-closed (invariant 80): an unreadable envelope, run record or trigger
record is exit 2. A directory that exists and is empty of runs is NOT a pass by
default - see --allow-empty-runs, which the scheduled caller never passes.

Usage:
  evaluate_envelope.py <envelope-dir> <runs-dir> <triggers-dir> [--allow-empty-runs]

Exit 0 clean, 1 one or more Blocking findings, 2 input fault.
"""
import glob
import os
import sys

import yaml


def load_dir(path, label, errors):
    docs = []
    if not os.path.isdir(path):
        errors.append("%s-dir-missing %s" % (label, path))
        return docs
    for name in sorted(os.listdir(path)):
        if not (name.endswith(".yaml") or name.endswith(".yml")):
            continue
        full = os.path.join(path, name)
        try:
            with open(full, "r", encoding="utf-8") as handle:
                doc = yaml.safe_load(handle)
        except Exception as exc:                                # fail closed
            errors.append("%s-unparseable %s (%s)" % (label, full, exc))
            continue
        if not isinstance(doc, dict):
            errors.append("%s-not-a-mapping %s" % (label, full))
            continue
        doc["__path"] = full
        docs.append(doc)
    return docs


def day_of(value):
    return str(value)[:10]


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = set(a for a in argv[1:] if a.startswith("--"))
    if len(args) != 3:
        print("RESULT FAIL usage evaluate_envelope.py <envelope-dir> <runs-dir> <triggers-dir>")
        return 2
    env_dir, runs_dir, trig_dir = args
    errors = []
    envelopes = load_dir(env_dir, "envelope", errors)
    runs = load_dir(runs_dir, "run", errors)
    triggers = load_dir(trig_dir, "trigger", errors)
    if errors:
        for line in errors:
            print("INPUT-FAULT %s" % line)
        print("RESULT FAIL input-fault")
        return 2
    if not envelopes:
        print("RESULT FAIL no-envelopes %s" % env_dir)
        return 2
    if not runs and "--allow-empty-runs" not in flags:
        print("RESULT FAIL no-run-records %s" % runs_dir)
        return 2

    by_cred = {}
    for env in envelopes:
        cred = env.get("credential_id")
        if not cred:
            print("RESULT FAIL envelope-without-credential_id %s" % env["__path"])
            return 2
        by_cred[cred] = env
    trigger_ids = set()
    for trig in triggers:
        tid = trig.get("trigger_id")
        cred = trig.get("credential_id")
        if tid and cred:
            trigger_ids.add((str(cred), str(tid)))

    findings = []
    counts = {}
    for run in sorted(runs, key=lambda r: str(r.get("run_id"))):
        cred = str(run.get("credential_id") or "")
        run_id = str(run.get("run_id") or os.path.basename(run["__path"]))
        env = by_cred.get(cred)
        if env is None:
            findings.append(("E0", cred, run_id, "no envelope declared for this credential"))
            continue
        trigger = str(run.get("scheduled_trigger") or "")
        if not trigger or (cred, trigger) not in trigger_ids:
            findings.append(("E1", cred, run_id,
                             "scheduled_trigger %r matches no trigger record" % trigger))
        host = str(run.get("source_host") or "")
        expected = str(env["expected_source_host"]["value"])
        if host != expected:
            findings.append(("E3", cred, run_id,
                             "source_host %r is not the expected source host %r"
                             % (host, expected)))
        if run.get("api_call_count") is None:
            findings.append(("E4", cred, run_id,
                             "no api_call_count published for this run"))
        if not str(run.get("signature") or "").strip() \
           or not str(run.get("signer") or "").strip():
            findings.append(("E5", cred, run_id, "run record is not signed"))
        counts.setdefault((cred, day_of(run.get("started_at"))), []).append(run_id)

    for (cred, day), run_ids in sorted(counts.items()):
        ceiling = int(by_cred[cred]["run_count_ceiling_per_day"]["value"])
        if len(run_ids) > ceiling:
            findings.append(("E2", cred, day,
                             "%d runs on %s exceeds the ceiling of %d"
                             % (len(run_ids), day, ceiling)))

    for clause, cred, subject, detail in sorted(findings):
        print("DRIFT Blocking %s %s %s - %s" % (clause, cred, subject, detail))
    print("FINDINGS %d" % len(findings))
    if findings:
        print("CLASS Blocking")
        print("SCALE Section 53.4")
        print("RESULT FAIL")
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
PYEOF
chmod +x access/secrets/envelope/evaluate_envelope.py
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/envelope/check-envelope.sh <<'SHEOF'
#!/usr/bin/env bash
# access/secrets/envelope/check-envelope.sh
# The stable exit contract Lane 3 reconciles against and Lane 2 wires (HO-02).
#
#   exit 0  every run is inside its envelope
#   exit 1  one or more runs are outside - Blocking drift (Section 53.4)
#   exit 2  input fault - FAIL CLOSED (invariant 80)
#
# Usage: check-envelope.sh <runs-dir> <triggers-dir>
# Envelopes always come from access/secrets/envelope.
set -eu
if [ "$#" -ne 2 ]; then
  echo "usage: check-envelope.sh <runs-dir> <triggers-dir>" >&2
  exit 2
fi
python access/secrets/envelope/evaluate_envelope.py access/secrets/envelope "$1" "$2"
SHEOF
chmod +x access/secrets/envelope/check-envelope.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
T=access/secrets/testdata/envelope
cat > $T/envelopes/fixture-cred.envelope.yaml <<'YAMLEOF'
# FIXTURE envelope. Deterministic by design: two scheduled runs a day, so the
# ceiling is four. Never generated from the contract, so the fixtures do not
# move when the contract changes.
schema_version: 1
credential_id: fixture-cred
spec_anchor: "Section 40.1"
spec_lines: "3685"
decision: D96
temporal_window_rule: retired
signed_run_record:
  required: true
  must_name: scheduled_trigger
  unmatched_run_class: Blocking
run_count_ceiling_per_day:
  scheduled_runs_per_day: 2
  multiplier: 2
  value: 4
  computed: true
expected_source_host:
  value: "fixture-host"
  breach_class: Blocking
published_api_call_counts:
  required: true
  per: run
  absent_class: Blocking
outside_envelope_class: Blocking
alert_config_owner: "fixture-owner"
YAMLEOF

for n in 1 2 3 4; do
cat > $T/triggers/t$n.yaml <<YAMLEOF
schema_version: 1
trigger_id: t$n
credential_id: fixture-cred
scheduled_for: "2026-03-02T0${n}:00:00Z"
YAMLEOF
done
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
T=access/secrets/testdata/envelope
new_run () {  # new_run <dir> <file> <run_id> <trigger> <host> <count> <sig>
  cat > "$1/$2" <<YAMLEOF
schema_version: 1
credential_id: fixture-cred
run_id: "$3"
scheduled_trigger: "$4"
source_host: "$5"
started_at: "2026-03-02T0${3#r}:05:00Z"
finished_at: "2026-03-02T0${3#r}:09:00Z"
api_call_count: $6
signature: "$7"
signer: "fixture-signer"
YAMLEOF
}

new_run $T/runs-clean r1.yaml r1 t1 fixture-host 118 sig-r1
new_run $T/runs-clean r2.yaml r2 t2 fixture-host 121 sig-r2

new_run $T/runs-no-trigger r1.yaml r1 t-does-not-exist fixture-host 118 sig-r1

new_run $T/runs-over-ceiling r1.yaml r1 t1 fixture-host 118 sig-r1
new_run $T/runs-over-ceiling r2.yaml r2 t2 fixture-host 118 sig-r2
new_run $T/runs-over-ceiling r3.yaml r3 t3 fixture-host 118 sig-r3
new_run $T/runs-over-ceiling r4.yaml r4 t4 fixture-host 118 sig-r4
new_run $T/runs-over-ceiling r5.yaml r5 t1 fixture-host 118 sig-r5

new_run $T/runs-wrong-host r1.yaml r1 t1 someones-laptop 118 sig-r1

new_run $T/runs-unsigned r1.yaml r1 t1 fixture-host 118 ""
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
T=access/secrets/testdata/envelope
cat > $T/runs-no-counts/r1.yaml <<'YAMLEOF'
# NEGATIVE FIXTURE E4. No api_call_count is published, so read-side abuse
# would surface as nothing (Section 40.1 line 3685).
schema_version: 1
credential_id: fixture-cred
run_id: "r1"
scheduled_trigger: "t1"
source_host: "fixture-host"
started_at: "2026-03-02T01:05:00Z"
finished_at: "2026-03-02T01:09:00Z"
signature: "sig-r1"
signer: "fixture-signer"
YAMLEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/secrets/envelope/evaluate_envelope.py access/secrets/envelope/check-envelope.sh access/secrets/testdata/envelope
git commit -m "L5-02-06: envelope evaluator, five clauses, six executed fixtures (Section 40.1, D96)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-envelope-evaluate
gh pr create --base integration \
  --title "L5-02-06 Envelope evaluator — a run outside the envelope is Blocking" \
  --body "Lane 5, Phase 2, task L5-02-06. Spec: Section 40.1 line 3685, D96 line 10189, Section 53.4. Paths: access/secrets/envelope/evaluate_envelope.py, access/secrets/envelope/check-envelope.sh, access/secrets/testdata/envelope/**. Self-verify output pasted below."
```

### Acceptance criteria

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | The clean fixture passes | `python access/secrets/envelope/evaluate_envelope.py access/secrets/testdata/envelope/envelopes access/secrets/testdata/envelope/runs-clean access/secrets/testdata/envelope/triggers \| tail -1` | `RESULT PASS` |
| 2 | E1 fires on an unmatched trigger | `python access/secrets/envelope/evaluate_envelope.py access/secrets/testdata/envelope/envelopes access/secrets/testdata/envelope/runs-no-trigger access/secrets/testdata/envelope/triggers \| grep -c '^DRIFT Blocking E1'` | `1` |
| 3 | E2 fires above the ceiling | `python access/secrets/envelope/evaluate_envelope.py access/secrets/testdata/envelope/envelopes access/secrets/testdata/envelope/runs-over-ceiling access/secrets/testdata/envelope/triggers \| grep -c '^DRIFT Blocking E2'` | `1` |
| 4 | E3 fires on an unexpected source host | `python access/secrets/envelope/evaluate_envelope.py access/secrets/testdata/envelope/envelopes access/secrets/testdata/envelope/runs-wrong-host access/secrets/testdata/envelope/triggers \| grep -c '^DRIFT Blocking E3'` | `1` |
| 5 | E4 fires when no API-call count is published | `python access/secrets/envelope/evaluate_envelope.py access/secrets/testdata/envelope/envelopes access/secrets/testdata/envelope/runs-no-counts access/secrets/testdata/envelope/triggers \| grep -c '^DRIFT Blocking E4'` | `1` |
| 6 | E5 fires on an unsigned run record | `python access/secrets/envelope/evaluate_envelope.py access/secrets/testdata/envelope/envelopes access/secrets/testdata/envelope/runs-unsigned access/secrets/testdata/envelope/triggers \| grep -c '^DRIFT Blocking E5'` | `1` |
| 7 | Every finding carries the Blocking class | `python access/secrets/envelope/evaluate_envelope.py access/secrets/testdata/envelope/envelopes access/secrets/testdata/envelope/runs-wrong-host access/secrets/testdata/envelope/triggers \| grep '^CLASS'` | `CLASS Blocking` |
| 8 | Breach fixtures exit 1 | `python access/secrets/envelope/evaluate_envelope.py access/secrets/testdata/envelope/envelopes access/secrets/testdata/envelope/runs-no-trigger access/secrets/testdata/envelope/triggers >/dev/null; echo $?` | `1` |
| 9 | The evaluator fails closed on a missing runs directory | `python access/secrets/envelope/evaluate_envelope.py access/secrets/testdata/envelope/envelopes /tmp/no-such-runs access/secrets/testdata/envelope/triggers >/dev/null; echo $?` | `2` |
| 10 | An empty runs directory is not silently a pass | `mkdir -p /tmp/emptyruns && python access/secrets/envelope/evaluate_envelope.py access/secrets/testdata/envelope/envelopes /tmp/emptyruns access/secrets/testdata/envelope/triggers \| tail -1` | `RESULT FAIL no-run-records /tmp/emptyruns` |
| 11 | The wrapper enforces its two arguments | `bash access/secrets/envelope/check-envelope.sh >/dev/null 2>&1; echo $?` | `2` |
| 12 | No file outside `access/secrets/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/secrets/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
E=access/secrets/testdata/envelope/envelopes
G=access/secrets/testdata/envelope/triggers
for d in runs-clean runs-no-trigger runs-over-ceiling runs-wrong-host runs-no-counts runs-unsigned; do
  R=access/secrets/testdata/envelope/$d
  printf '%s ' "$d"
  python access/secrets/envelope/evaluate_envelope.py "$E" "$R" "$G" | grep -E '^(FINDINGS|RESULT)' | tr '\n' ' '
  echo
done
python access/secrets/envelope/evaluate_envelope.py "$E" /tmp/no-such-runs "$G" >/dev/null 2>&1; echo "FAIL-CLOSED-EXIT $?"
echo "L5-02-06 SELF-VERIFY PASS"
```

Expected output, exactly:

```
runs-clean FINDINGS 0 RESULT PASS 
runs-no-trigger FINDINGS 1 RESULT FAIL 
runs-over-ceiling FINDINGS 1 RESULT FAIL 
runs-wrong-host FINDINGS 1 RESULT FAIL 
runs-no-counts FINDINGS 1 RESULT FAIL 
runs-unsigned FINDINGS 1 RESULT FAIL 
FAIL-CLOSED-EXIT 2
L5-02-06 SELF-VERIFY PASS
```

(Each fixture line ends with one trailing space, produced by `tr '\n' ' '`.)

### STOP rule

STOP — do not commit, do not push, file the blocker of Section 4 — if any of these hold:

* Any breach fixture reports `FINDINGS 0`. A clause that does not fire is a gate that appears to be working
  and is not — the exact failure §40.1 line 3685 exists to prevent. Class `shape-mismatch`.
* The clean fixture reports a finding. A false positive on a legitimate run trains its reader to ignore the
  alert. Class `shape-mismatch`.
* The executor is tempted to add a time-window clause "as well". D96 retired it; re-adding it is a
  specification change. Class `needs-decision`.

---

## L5-02-07 — The one-page credential-rotation runbook

| Field | Value |
|---|---|
| Task id | `L5-02-07` |
| Size | M |
| Depends on | `L5-02-04` |
| Slug | `rotation-runbook` |
| Subsystem | L |
| Spec | §40.1 line 3683 ("A one-page rotation runbook lives in the control-plane repository"); §14.4 line 1266 (re-escrow is a blocking step in the rotation runbook); AT-110 lines 9438–9439; §43.1 lines 3853–3870 |
| Writes | `access/secrets/runbooks/rotate-fifth-tier-credential.md`, `access/secrets/runbooks/rotation-record.template.yaml`, `access/secrets/runbooks/check-runbook.sh` |

### Purpose

§40.1 says three things about rotation that a prose runbook usually loses: it is **one page**; after any
rotation **a manual reconciliation run must complete clean before the rotation is recorded as done** — "a
credential that rotates but no longer reconciles has not been rotated, it has been broken"; and AT-110 is
**re-executed at every rotation, on the same gate**. §14.4 line 1266 adds the third blocking step:
re-escrow of the replacement, because "a rotation is not recordable as done until the replacement is
escrowed".

"One page" is made checkable rather than aspirational: `check-runbook.sh` fails if the runbook exceeds 120
lines, if any of the ten step ids is missing, or if the count of `BLOCKING` markers is not exactly three.

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-rotation-runbook
mkdir -p access/secrets/runbooks
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/runbooks/rotate-fifth-tier-credential.md <<'MDEOF'
# Rotate a fifth-tier machine credential

Section 40.1 line 3683. One page. Applies to all five control-plane machine
credentials without variation. Cadence: quarterly (calibrated configuration,
initial value). On a workstation compromise this runbook is executed for ALL
five credentials as a named step (Section 43.4; access/secrets/incident/).

Inputs: the credential id, its entry in access/secrets/fifth-tier/, its envelope
in access/secrets/envelope/. Actor: the entry's named `rotator`.

STEP-01 Confirm you are the named rotator for this credential and that you hold
the DevOps capability. If you are not, stop; a rotation by anyone else is not a
rotation, it is an unrecorded credential change.

STEP-02 Open the rotation record from
access/secrets/runbooks/rotation-record.template.yaml. Fill rotation_id,
credential_id, rotator and rotated_at before touching the credential. State is
`in-progress` until the gate of L5-02-08 permits `done`.

STEP-03 If this rotation follows a suspected compromise, capture evidence FIRST:
logs, audit records, artifact digests, access history. Section 43.1 - "Do not
delete. Do not force-push. Do not rotate before capturing."

STEP-04 Issue the replacement with EXACTLY the permission set published in the
credential's fifth-tier entry. Do not widen it "while you are in there". A
widened permission set is drift the moment it is issued.

STEP-05 Install the replacement into the fifth-tier store on the credential's
expected source host, under the separate OS user or secret agent declared in
access/secrets/host/credential-store.yaml. Never onto a workstation.

STEP-06 BLOCKING - Re-escrow. Deposit the replacement with the Section 14.4
escrow custodian and record the confirmation in the rotation record. Section
14.4 line 1266: a rotation is not recordable as done until the replacement is
escrowed. Re-escrow the encryption key too where the credential has one.

STEP-07 BLOCKING - Run a manual reconciliation run to completion. It must
complete CLEAN. Section 40.1: a credential that rotates but no longer
reconciles has not been rotated, it has been broken. Record the run id and its
result in the rotation record.

STEP-08 BLOCKING - Re-execute AT-110. Six attempts from the credential itself -
a GitHub Actions secret write, an environment write, a workflow-file change, an
organisation-settings change, a records/** write, and any Layer B access - and
all six must FAIL; the credential must then still complete a normal
reconciliation run. Record executed_at, result and attempts_failed.

STEP-09 Revoke the superseded credential and confirm the revocation. Until this
step both credentials authenticate, and the envelope's run-count ceiling is the
only thing standing between you and an unnoticed second user.

STEP-10 Run the rotation-completion gate:
  bash access/secrets/checks/rotation-complete.sh <rotation-record.yaml>
Only when it prints ROTATION-DONE-PERMITTED may the record be set to `done`.
If the schedule changed as part of this rotation, re-run
access/secrets/tools/emit_envelopes.py so the run-count ceiling is recalibrated,
and commit the regenerated envelope.

If any blocking step above fails: the rotation is NOT done. The credential is
broken, not rotated. Restore the previous credential from the Section 14.4
escrow, leave the rotation record at `in-progress`, and file a blocker.
MDEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/runbooks/rotation-record.template.yaml <<'YAMLEOF'
# access/secrets/runbooks/rotation-record.template.yaml
# One record per rotation. Copy, fill, and run the gate of L5-02-08 against it.
# Timestamps are UTC in the form YYYY-MM-DDTHH:MM:SSZ - exactly 20 characters.
schema_version: 1
rotation_id: ""                 # e.g. rot-2026Q1-reconciler
credential_id: ""               # one of the five ids in access/secrets/fifth-tier/
rotator: ""                     # the entry's named rotator; a DevOps-capability holder
rotated_at: ""                  # when the replacement was installed (STEP-05)
reconciliation:                 # STEP-07, BLOCKING
  run_id: ""
  completed_at: ""
  result: ""                    # clean | dirty
at110:                          # STEP-08, BLOCKING - AT-110 re-executed
  executed_at: ""
  result: ""                    # pass | fail
  attempts_failed: 0            # must be 6: all six attempts must fail
re_escrow:                      # STEP-06, BLOCKING - Section 14.4 line 1266
  confirmed: false
  custodian: ""
  confirmed_at: ""
revocation:
  superseded_credential_revoked: false
  revoked_at: ""
state: in-progress              # done only when the gate permits it
YAMLEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/runbooks/check-runbook.sh <<'SHEOF'
#!/usr/bin/env bash
# access/secrets/runbooks/check-runbook.sh
# "One page" is a requirement, so it is checked (Section 40.1 line 3683).
# Also proves the three BLOCKING steps and all ten step ids are present, and
# that every fifth-tier entry links this exact runbook.
set -eu
RB=access/secrets/runbooks/rotate-fifth-tier-credential.md
FAIL=0
if [ ! -f "$RB" ]; then echo "RUNBOOK missing $RB"; echo "RESULT FAIL"; exit 2; fi
LINES=$(wc -l < "$RB" | tr -d ' ')
echo "RUNBOOK-LINES $LINES"
if [ "$LINES" -gt 120 ]; then echo "RUNBOOK too long: one page is 120 lines"; FAIL=1; fi
for n in 01 02 03 04 05 06 07 08 09 10; do
  grep -q "STEP-$n " "$RB" || { echo "RUNBOOK missing STEP-$n"; FAIL=1; }
done
BLOCKING=$(grep -c 'BLOCKING' "$RB" || true)
echo "BLOCKING-STEPS $BLOCKING"
[ "$BLOCKING" -eq 3 ] || { echo "RUNBOOK expected exactly 3 BLOCKING steps"; FAIL=1; }
grep -q 'Section 14.4' "$RB" || { echo "RUNBOOK does not cite the Section 14.4 re-escrow"; FAIL=1; }
grep -q 'AT-110' "$RB" || { echo "RUNBOOK does not re-execute AT-110"; FAIL=1; }
grep -q 'CLEAN' "$RB" || { echo "RUNBOOK does not require a clean reconciliation run"; FAIL=1; }
LINKED=$(grep -l "$RB" access/secrets/fifth-tier/*.yaml | wc -l | tr -d ' ')
echo "ENTRIES-LINKING-RUNBOOK $LINKED"
[ "$LINKED" -eq 5 ] || { echo "RUNBOOK not linked by all five fifth-tier entries"; FAIL=1; }
if [ "$FAIL" -eq 0 ]; then echo "RESULT PASS"; else echo "RESULT FAIL"; exit 1; fi
SHEOF
chmod +x access/secrets/runbooks/check-runbook.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/secrets/runbooks
git commit -m "L5-02-07: the one-page fifth-tier rotation runbook and its checker (Section 40.1, Section 14.4)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-rotation-runbook
gh pr create --base integration \
  --title "L5-02-07 The one-page credential-rotation runbook" \
  --body "Lane 5, Phase 2, task L5-02-07. Spec: Section 40.1 line 3683, Section 14.4 line 1266, AT-110 lines 9438-9439, Section 43.1. Paths: access/secrets/runbooks/**. Self-verify output pasted below."
```

### Acceptance criteria

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | The runbook is one page | `wc -l < access/secrets/runbooks/rotate-fifth-tier-credential.md` | a number `<= 120` |
| 2 | All ten step ids are present | `for n in 01 02 03 04 05 06 07 08 09 10; do grep -c "STEP-$n " access/secrets/runbooks/rotate-fifth-tier-credential.md; done \| sort -u` | `1` |
| 3 | Exactly three steps are BLOCKING | `grep -c BLOCKING access/secrets/runbooks/rotate-fifth-tier-credential.md` | `3` |
| 4 | Re-escrow is one of them | `grep -c 'BLOCKING - Re-escrow' access/secrets/runbooks/rotate-fifth-tier-credential.md` | `1` |
| 5 | A clean reconciliation run is one of them | `grep -c 'BLOCKING - Run a manual reconciliation run' access/secrets/runbooks/rotate-fifth-tier-credential.md` | `1` |
| 6 | AT-110 re-execution is one of them | `grep -c 'BLOCKING - Re-execute AT-110' access/secrets/runbooks/rotate-fifth-tier-credential.md` | `1` |
| 7 | Evidence capture precedes rotation | `grep -c 'Do not rotate before capturing' access/secrets/runbooks/rotate-fifth-tier-credential.md` | `1` |
| 8 | All five fifth-tier entries link this runbook | `grep -l 'access/secrets/runbooks/rotate-fifth-tier-credential.md' access/secrets/fifth-tier/*.yaml \| wc -l` | `5` |
| 9 | The record template carries the three gate blocks | `python -c "import yaml;d=yaml.safe_load(open('access/secrets/runbooks/rotation-record.template.yaml'));print(sorted(k for k in d if k in ('reconciliation','at110','re_escrow')))"` | `['at110', 're_escrow', 'reconciliation']` |
| 10 | The checker passes | `bash access/secrets/runbooks/check-runbook.sh \| tail -1` | `RESULT PASS` |
| 11 | No file outside `access/secrets/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/secrets/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash access/secrets/runbooks/check-runbook.sh
echo "L5-02-07 SELF-VERIFY PASS"
```

Expected output, exactly:

```
RUNBOOK-LINES <varies>
BLOCKING-STEPS 3
ENTRIES-LINKING-RUNBOOK 5
RESULT PASS
L5-02-07 SELF-VERIFY PASS
```

`RUNBOOK-LINES` is the only `<varies>` line: any value **at or below 120** is acceptable and the checker
enforces that bound itself. Every other line must match exactly.

### STOP rule

STOP — do not commit, do not push, file the blocker of Section 4 — if any of these hold:

* `BLOCKING-STEPS` is not `3`. Fewer means a blocking condition was dropped; more means a step was
  promoted to blocking without authority. Class `shape-mismatch`.
* `ENTRIES-LINKING-RUNBOOK` is not `5`. Either T04 was not merged, or an entry points at a different
  runbook. Class `shape-mismatch`.
* The executor wants to split the runbook into several pages "for clarity". §40.1 line 3683 says one page;
  the rotation happens under time pressure and a multi-page runbook is a runbook nobody finishes. Class
  `needs-decision`.

---

## L5-02-08 — Rotation-completion gate (clean reconciliation + AT-110 + re-escrow)

| Field | Value |
|---|---|
| Task id | `L5-02-08` |
| Size | M |
| Depends on | `L5-02-07` |
| Slug | `rotation-gate` |
| Subsystem | L |
| Spec | §40.1 line 3683; §14.4 line 1266; AT-110 lines 9438–9439; invariant 80 line 9557 |
| Writes | `access/secrets/checks/rotation_complete.py`, `access/secrets/checks/rotation-complete.sh`, `access/secrets/testdata/rotation/complete.yaml`, `access/secrets/testdata/rotation/dirty-reconciliation.yaml`, `access/secrets/testdata/rotation/at110-not-reexecuted.yaml`, `access/secrets/testdata/rotation/no-re-escrow.yaml`, `access/secrets/testdata/rotation/at110-stale.yaml` |

### Purpose

Three conditions must hold before a rotation may be recorded as done, and each comes from a different
sentence of the specification:

| Gate | Condition | Source |
|---|---|---|
| `G1` | a manual reconciliation run completed **clean**, at or after `rotated_at` | §40.1 line 3683 |
| `G2` | **AT-110 re-executed**, result `pass`, all six attempts failed, at or after `rotated_at` | AT-110 lines 9438–9439 — "re-executed at every rotation, on the same gate as 40.1's clean-reconciliation condition" |
| `G3` | **re-escrow confirmed** by a named custodian, at or after `rotated_at` | §14.4 line 1266 |

`at or after rotated_at` is the clause that stops the most common false completion: pasting last quarter's
clean reconciliation into this quarter's record. The gate therefore compares timestamps, not booleans
alone, and the `at110-stale.yaml` fixture proves it.

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-rotation-gate
mkdir -p access/secrets/checks access/secrets/testdata/rotation
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/checks/rotation_complete.py <<'PYEOF'
#!/usr/bin/env python3
"""The rotation-completion gate.

Section 40.1 line 3683: after any rotation a manual reconciliation run must
complete clean before the rotation is recorded as done - "a credential that
rotates but no longer reconciles has not been rotated, it has been broken."
AT-110 lines 9438-9439: re-executed at every rotation, on the same gate.
Section 14.4 line 1266: re-escrow is a blocking step; a rotation is not
recordable as done until the replacement is escrowed.

Fail-closed (invariant 80): an unreadable or malformed record is exit 2.

Usage: rotation_complete.py <rotation-record.yaml>
Exit 0 done permitted, 1 not done, 2 input fault.
"""
import os
import sys

import yaml

STAMP_LEN = 20   # YYYY-MM-DDTHH:MM:SSZ


def stamp_ok(value):
    text = str(value or "")
    return len(text) == STAMP_LEN and text.endswith("Z") and text[10] == "T"


def main(argv):
    if len(argv) != 2:
        print("RESULT FAIL usage rotation_complete.py <rotation-record.yaml>")
        return 2
    path = argv[1]
    if not os.path.isfile(path):
        print("RESULT FAIL record-unreadable %s" % path)
        return 2
    try:
        with open(path, "r", encoding="utf-8") as handle:
            rec = yaml.safe_load(handle) or {}
    except Exception as exc:                                    # fail closed
        print("RESULT FAIL record-unparseable %s" % exc)
        return 2
    if not isinstance(rec, dict):
        print("RESULT FAIL record-not-a-mapping %s" % path)
        return 2
    for key in ("rotation_id", "credential_id", "rotator", "rotated_at",
                "reconciliation", "at110", "re_escrow"):
        if key not in rec:
            print("RESULT FAIL record-missing-key %s" % key)
            return 2
    rotated_at = str(rec.get("rotated_at") or "")
    if not stamp_ok(rotated_at):
        print("RESULT FAIL bad-rotated_at %r" % rotated_at)
        return 2

    blocked = []
    recon = rec.get("reconciliation") or {}
    if str(recon.get("result") or "") != "clean":
        blocked.append("G1 reconciliation.result is %r, not 'clean' - the credential is broken, not rotated"
                       % recon.get("result"))
    elif not stamp_ok(recon.get("completed_at")):
        blocked.append("G1 reconciliation.completed_at is not a UTC stamp")
    elif str(recon.get("completed_at")) < rotated_at:
        blocked.append("G1 reconciliation completed BEFORE the rotation (%s < %s)"
                       % (recon.get("completed_at"), rotated_at))

    at110 = rec.get("at110") or {}
    if str(at110.get("result") or "") != "pass":
        blocked.append("G2 at110.result is %r, not 'pass'" % at110.get("result"))
    elif int(at110.get("attempts_failed") or 0) != 6:
        blocked.append("G2 at110.attempts_failed is %r; AT-110 makes six attempts and all six must fail"
                       % at110.get("attempts_failed"))
    elif not stamp_ok(at110.get("executed_at")):
        blocked.append("G2 at110.executed_at is not a UTC stamp")
    elif str(at110.get("executed_at")) < rotated_at:
        blocked.append("G2 AT-110 was executed BEFORE this rotation (%s < %s) - it must be RE-executed"
                       % (at110.get("executed_at"), rotated_at))

    escrow = rec.get("re_escrow") or {}
    if escrow.get("confirmed") is not True:
        blocked.append("G3 re_escrow.confirmed is not true - Section 14.4 line 1266")
    elif not str(escrow.get("custodian") or "").strip():
        blocked.append("G3 re_escrow.custodian is empty - the escrow has a named custodian")
    elif not stamp_ok(escrow.get("confirmed_at")):
        blocked.append("G3 re_escrow.confirmed_at is not a UTC stamp")
    elif str(escrow.get("confirmed_at")) < rotated_at:
        blocked.append("G3 re-escrow was confirmed BEFORE the rotation (%s < %s)"
                       % (escrow.get("confirmed_at"), rotated_at))

    for line in blocked:
        print("BLOCKED %s" % line)
    print("GATES-BLOCKED %d" % len(blocked))
    if blocked:
        print("ROTATION-NOT-DONE")
        print("RESULT FAIL")
        return 1
    print("ROTATION-DONE-PERMITTED")
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
PYEOF
chmod +x access/secrets/checks/rotation_complete.py

cat > access/secrets/checks/rotation-complete.sh <<'SHEOF'
#!/usr/bin/env bash
# access/secrets/checks/rotation-complete.sh
# STEP-10 of the rotation runbook. The only thing that may set a rotation
# record to `done`.
#   exit 0  ROTATION-DONE-PERMITTED
#   exit 1  ROTATION-NOT-DONE
#   exit 2  input fault - FAIL CLOSED
set -eu
python access/secrets/checks/rotation_complete.py "$@"
SHEOF
chmod +x access/secrets/checks/rotation-complete.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
R=access/secrets/testdata/rotation
cat > $R/complete.yaml <<'YAMLEOF'
# POSITIVE FIXTURE. All three gates satisfied, all three after rotated_at.
schema_version: 1
rotation_id: "rot-fixture-01"
credential_id: "fixture-cred"
rotator: "fixture-rotator"
rotated_at: "2026-03-02T09:00:00Z"
reconciliation: { run_id: "rec-1", completed_at: "2026-03-02T09:40:00Z", result: clean }
at110: { executed_at: "2026-03-02T09:55:00Z", result: pass, attempts_failed: 6 }
re_escrow: { confirmed: true, custodian: "fixture-custodian", confirmed_at: "2026-03-02T09:20:00Z" }
revocation: { superseded_credential_revoked: true, revoked_at: "2026-03-02T10:00:00Z" }
state: in-progress
YAMLEOF

cat > $R/dirty-reconciliation.yaml <<'YAMLEOF'
# NEGATIVE FIXTURE G1. Rotated, but reconciliation did not come back clean.
schema_version: 1
rotation_id: "rot-fixture-02"
credential_id: "fixture-cred"
rotator: "fixture-rotator"
rotated_at: "2026-03-02T09:00:00Z"
reconciliation: { run_id: "rec-2", completed_at: "2026-03-02T09:40:00Z", result: dirty }
at110: { executed_at: "2026-03-02T09:55:00Z", result: pass, attempts_failed: 6 }
re_escrow: { confirmed: true, custodian: "fixture-custodian", confirmed_at: "2026-03-02T09:20:00Z" }
state: in-progress
YAMLEOF

cat > $R/at110-not-reexecuted.yaml <<'YAMLEOF'
# NEGATIVE FIXTURE G2. AT-110 records a pass but only five attempts failed -
# the sixth succeeded, so the credential is not bounded.
schema_version: 1
rotation_id: "rot-fixture-03"
credential_id: "fixture-cred"
rotator: "fixture-rotator"
rotated_at: "2026-03-02T09:00:00Z"
reconciliation: { run_id: "rec-3", completed_at: "2026-03-02T09:40:00Z", result: clean }
at110: { executed_at: "2026-03-02T09:55:00Z", result: pass, attempts_failed: 5 }
re_escrow: { confirmed: true, custodian: "fixture-custodian", confirmed_at: "2026-03-02T09:20:00Z" }
state: in-progress
YAMLEOF

cat > $R/no-re-escrow.yaml <<'YAMLEOF'
# NEGATIVE FIXTURE G3. Everything else is clean; the replacement was never
# escrowed. Section 14.4 line 1266 makes this alone enough to block.
schema_version: 1
rotation_id: "rot-fixture-04"
credential_id: "fixture-cred"
rotator: "fixture-rotator"
rotated_at: "2026-03-02T09:00:00Z"
reconciliation: { run_id: "rec-4", completed_at: "2026-03-02T09:40:00Z", result: clean }
at110: { executed_at: "2026-03-02T09:55:00Z", result: pass, attempts_failed: 6 }
re_escrow: { confirmed: false, custodian: "", confirmed_at: "" }
state: in-progress
YAMLEOF

cat > $R/at110-stale.yaml <<'YAMLEOF'
# NEGATIVE FIXTURE G2. Last quarter's AT-110 result pasted into this quarter's
# record. It passed - in December, before this rotation existed.
schema_version: 1
rotation_id: "rot-fixture-05"
credential_id: "fixture-cred"
rotator: "fixture-rotator"
rotated_at: "2026-03-02T09:00:00Z"
reconciliation: { run_id: "rec-5", completed_at: "2026-03-02T09:40:00Z", result: clean }
at110: { executed_at: "2025-12-01T11:00:00Z", result: pass, attempts_failed: 6 }
re_escrow: { confirmed: true, custodian: "fixture-custodian", confirmed_at: "2026-03-02T09:20:00Z" }
state: in-progress
YAMLEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/secrets/checks/rotation_complete.py access/secrets/checks/rotation-complete.sh access/secrets/testdata/rotation
git commit -m "L5-02-08: rotation-completion gate - clean reconciliation, AT-110 re-execution, re-escrow (Section 40.1, Section 14.4)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-rotation-gate
gh pr create --base integration \
  --title "L5-02-08 Rotation-completion gate (clean reconciliation + AT-110 + re-escrow)" \
  --body "Lane 5, Phase 2, task L5-02-08. Spec: Section 40.1 line 3683, Section 14.4 line 1266, AT-110 lines 9438-9439. Paths: access/secrets/checks/rotation_complete.py, access/secrets/checks/rotation-complete.sh, access/secrets/testdata/rotation/**. Self-verify output pasted below."
```

### Acceptance criteria

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | The complete fixture is permitted | `bash access/secrets/checks/rotation-complete.sh access/secrets/testdata/rotation/complete.yaml \| grep '^ROTATION-'` | `ROTATION-DONE-PERMITTED` |
| 2 | It exits 0 | `bash access/secrets/checks/rotation-complete.sh access/secrets/testdata/rotation/complete.yaml >/dev/null; echo $?` | `0` |
| 3 | A dirty reconciliation blocks | `bash access/secrets/checks/rotation-complete.sh access/secrets/testdata/rotation/dirty-reconciliation.yaml \| grep -c '^BLOCKED G1'` | `1` |
| 4 | Five of six AT-110 attempts failing blocks | `bash access/secrets/checks/rotation-complete.sh access/secrets/testdata/rotation/at110-not-reexecuted.yaml \| grep -c '^BLOCKED G2'` | `1` |
| 5 | A missing re-escrow blocks | `bash access/secrets/checks/rotation-complete.sh access/secrets/testdata/rotation/no-re-escrow.yaml \| grep -c '^BLOCKED G3'` | `1` |
| 6 | A stale AT-110 result blocks | `bash access/secrets/checks/rotation-complete.sh access/secrets/testdata/rotation/at110-stale.yaml \| grep -c 'must be RE-executed'` | `1` |
| 7 | Every negative fixture exits 1 | `for f in dirty-reconciliation at110-not-reexecuted no-re-escrow at110-stale; do bash access/secrets/checks/rotation-complete.sh access/secrets/testdata/rotation/$f.yaml >/dev/null; echo $?; done \| sort -u` | `1` |
| 8 | The gate fails closed on a missing record | `bash access/secrets/checks/rotation-complete.sh /tmp/no-such-record.yaml >/dev/null 2>&1; echo $?` | `2` |
| 9 | STEP-10 of the runbook names this gate | `grep -c 'access/secrets/checks/rotation-complete.sh' access/secrets/runbooks/rotate-fifth-tier-credential.md` | `1` |
| 10 | No file outside `access/secrets/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/secrets/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for f in complete dirty-reconciliation at110-not-reexecuted no-re-escrow at110-stale; do
  printf '%s ' "$f"
  bash access/secrets/checks/rotation-complete.sh access/secrets/testdata/rotation/$f.yaml \
    | grep -E '^(GATES-BLOCKED|ROTATION-)' | tr '\n' ' '
  echo
done
bash access/secrets/checks/rotation-complete.sh /tmp/no-such-record.yaml >/dev/null 2>&1; echo "FAIL-CLOSED-EXIT $?"
echo "L5-02-08 SELF-VERIFY PASS"
```

Expected output, exactly:

```
complete GATES-BLOCKED 0 ROTATION-DONE-PERMITTED 
dirty-reconciliation GATES-BLOCKED 1 ROTATION-NOT-DONE 
at110-not-reexecuted GATES-BLOCKED 1 ROTATION-NOT-DONE 
no-re-escrow GATES-BLOCKED 1 ROTATION-NOT-DONE 
at110-stale GATES-BLOCKED 1 ROTATION-NOT-DONE 
FAIL-CLOSED-EXIT 2
L5-02-08 SELF-VERIFY PASS
```

### STOP rule

STOP — do not commit, do not push, file the blocker of Section 4 — if any of these hold:

* The complete fixture is blocked, or any negative fixture is permitted. Class `shape-mismatch`.
* The executor wants to make one of the three gates a warning "because the reconciler is not built yet".
  It is not built yet in this lane's dependency order, and that is exactly why the gate is written now and
  executed at the first real rotation. Class `needs-decision`.
* AT-110 cannot be executed because the reconciler does not exist on `integration` yet. That is not a
  blocker for **this** task — this task builds the gate, not the test. It becomes a blocker only when a
  real rotation is attempted; record it then, class `needs-decision`.

---

## L5-02-09 — The two trust boundaries, declared and checkable (§40.3, D95)

| Field | Value |
|---|---|
| Task id | `L5-02-09` |
| Size | M |
| Depends on | `L5-02-01` |
| Slug | `boundaries` |
| Subsystem | L |
| Spec | §40.3 lines 3695–3704; D95 line 10188; §51.5 line 4502; §99.6 risk 6 lines 9276–9294; invariants 24, 25, 26 lines 9486–9488 |
| Writes | `access/secrets/boundaries/boundary-1-production.yaml`, `access/secrets/boundaries/boundary-2-control-plane.yaml`, `access/secrets/boundaries/check_boundaries.py`, `access/secrets/boundaries/check-boundaries.sh` |

### Purpose

§40.3 states two boundaries as block quotes, and the second one exists because the first is silent about
the system's highest-privilege identity:

> A fully compromised developer workstation must not yield production database access, production
> credentials, or the ability to deploy to production.

> A fully compromised engineering workstation must not yield the control-plane machine-credential store.

The second is D95's addition. §40.3 explains the gap it closes: the reconciler credential and the
organisation-export token live in the fifth tier on the operations VM, "so a cached session or key from a
workstation to that host reaches organisation-admin-equivalent write across every repository without ever
touching production — and does so from the host the credential is expected to be used from, which is why
the behavioural envelope of 40.1 is host- and volume-aware rather than only time-aware."

This task turns both quotes into declaration files and ships a checker with a repository-side half. It
provisions nothing: the three technical enforcements §40.3 names are built by T10 (the separate OS user or
secret agent, and the second factor) and T11 (rotator/host-root separation).

**The checker has two phases and says which it ran.** `--phase declare` runs only the assertions whose
inputs exist at T09 time; `--phase complete` (the default) runs all of them and is what T14's exit gate
calls. A checker that silently passes because its target file does not exist yet is the failure this file
exists to prevent, so the phase is printed in the output.

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-boundaries
mkdir -p access/secrets/boundaries
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/boundaries/boundary-1-production.yaml <<'YAMLEOF'
# access/secrets/boundaries/boundary-1-production.yaml
# Section 40.3 line 3697. The statement is the spec's block quote, verbatim.
schema_version: 1
boundary_id: boundary-1-production
statement: "A fully compromised developer workstation must not yield production database access, production credentials, or the ability to deploy to production."
statement_source: "Section 40.3, line 3697 (block quote)"
enforced_technically: true
enforced_behaviourally: false
enforcement:
  - "production secrets exist only in the production GitHub Environment"
  - "accessible only to the production deployment workflow"
  - "which requires an approval from someone other than the actor (Section 27)"
what_a_compromise_does_yield:
  - "source code"
  - "the ability to open a pull request"
  - "the ability to push a branch"
  - "execution with CI-tier credentials, because a branch push executes CI"
what_a_compromise_does_not_yield:
  - "production"
ci_tier_compensating_controls:
  - "the default GITHUB_TOKEN is read-only"
  - "scan and build credentials are environment-gated where the platform supports it"
  - "a workflow-file change pushed by a machine identity is Blocking drift"
invariants: [24, 25, 26]
assertions:
  - id: B1-A1
    statement: "No secret name held at the production tier appears in any tier below it."
    checked_by: "access/secrets/checks/check-no-downward-move.sh"
    phase: declare
  - id: B1-A2
    statement: "Exactly one tier declares holds_production_credentials, and it is the production tier."
    checked_by: "access/secrets/boundaries/check_boundaries.py"
    phase: declare
  - id: B1-A3
    statement: "No fifth-tier credential declares a workstation as its expected source host."
    checked_by: "access/secrets/boundaries/check_boundaries.py"
    phase: complete
  - id: B1-A4
    statement: "Human infrastructure access is provider-SSO-federated with no long-lived key, which is why the five secret tiers remain exactly five."
    declared_default: "security.production_db_access: ci-only"
    verification_method: attestation
    verification_reason: "reconciliation compares declared state against GitHub state and never leaves it, so the provider side is verified by attestation rather than reconciliation (Section 40.2)"
    attestation_cadence: monthly
    attestation_cadence_status: "calibrated configuration; run with the Section 49 asset-inventory sweep; recalibrated if an attestation ever finds drift"
    attestation_owner_resolved_by: "the product contract's infrastructure block (Lane 1). This lane declares the rule; it never names the owner"
    expired_or_failed_attestation_class: Blocking
    phase: declare
YAMLEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/boundaries/boundary-2-control-plane.yaml <<'YAMLEOF'
# access/secrets/boundaries/boundary-2-control-plane.yaml
# Section 40.3 line 3701; D95 line 10188. The statement is the spec's block
# quote, verbatim. This is the boundary D95 ADDED, and the reason it exists is
# that the first boundary is silent about the highest-privilege identity in the
# system (Section 99.6, risk 6).
schema_version: 1
boundary_id: boundary-2-control-plane
statement: "A fully compromised engineering workstation must not yield the control-plane machine-credential store."
statement_source: "Section 40.3, line 3701 (block quote)"
decision: D95
added_by_decision: true
why_it_exists: "Section 99.6 risk 6 - the reconciler is the highest-privilege identity in the system, and the first boundary says nothing about it"
blast_radius_if_absent: "a cached session or key from a workstation to the operations VM reaches organisation-admin-equivalent write across every repository without ever touching production, and does so from the host the credential is expected to be used from"
consequence_for_the_envelope: "which is why the behavioural envelope of Section 40.1 is host- and volume-aware rather than only time-aware"
what_the_ops_vm_holds: "the fifth-tier machine-credential store of Section 40.1, including the reconciler credential and the organisation-export token (Section 51.5 line 4502)"
what_the_ops_vm_does_not_hold:
  - "production credentials"
  - "deploy keys"
  - "environment access"
enforced_technically: true
enforcement:
  - id: E1
    statement: "The fifth-tier credentials sit under a separate OS user or secret agent that a passive root shell does not read."
    declared_in: "access/secrets/host/credential-store.yaml"
    built_by: "L5-02-10"
  - id: E2
    statement: "Shell access to the operations VM requires a second factor on top of the private network path of Section 51.4."
    declared_in: "infra/network/ops-vm-shell-gate.yaml"
    built_by: "L5-02-10"
  - id: E3
    statement: "The rotator of a fifth-tier credential and the holder of host root on the machine that stores it are separated where headcount permits; where it does not, the concentration is a recorded accepted risk with a named holder and a dated review, never an unstated default."
    declared_in: "access/secrets/separation/"
    built_by: "L5-02-11"
assertions:
  - id: B2-A1
    statement: "No fifth-tier credential declares a workstation as its expected source host."
    phase: complete
  - id: B2-A2
    statement: "No private-key block and no GitHub token prefix appears anywhere under access/ or infra/."
    phase: declare
  - id: B2-A3
    statement: "The credential-store declaration exists and sets passive_root_read: false."
    phase: complete
  - id: B2-A4
    statement: "The shell-gate declaration exists, requires a hardware-backed key type, and forbids password authentication."
    phase: complete
  - id: B2-A5
    statement: "The separation result exists and is either 'separated' or a complete accepted risk with a named holder, a compensating control and a dated review."
    phase: complete
related_boundary_in_lane: "L5 phase 3 separates the Layer B store from the shared host under the same decision (D95); see L5-03-02"
YAMLEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/boundaries/check_boundaries.py <<'PYEOF'
#!/usr/bin/env python3
"""Check the repository-side half of the two Section 40.3 trust boundaries.

Section 40.3 lines 3695-3704; D95 line 10188; Section 51.5 line 4502.

Phases:
  --phase declare   run only the assertions whose inputs exist once T09 lands
  --phase complete  run every assertion (the default; used by the T14 gate)

The phase is always printed, because a checker that passes silently only
because its target file does not exist yet is the failure this whole file
exists to prevent.

Fail-closed (invariant 80): a missing boundary declaration is exit 2.

Usage:  check_boundaries.py [--phase declare|complete]
Exit 0 all assertions hold, 1 an assertion fails, 2 input fault.
"""
import glob
import os
import sys

import yaml

B1 = os.path.join("access", "secrets", "boundaries", "boundary-1-production.yaml")
B2 = os.path.join("access", "secrets", "boundaries", "boundary-2-control-plane.yaml")
TIERS = os.path.join("access", "secrets", "tiers")
FIFTH = os.path.join("access", "secrets", "fifth-tier")
STORE = os.path.join("access", "secrets", "host", "credential-store.yaml")
GATE = os.path.join("infra", "network", "ops-vm-shell-gate.yaml")
SEP = os.path.join("access", "secrets", "separation", "separation.result.yaml")
WORKSTATION_MARKERS = ("laptop", "workstation", "macbook", "desktop", "dev-machine")
LEAK_MARKERS = ("BEGIN OPENSSH PRIVATE KEY", "BEGIN RSA PRIVATE KEY",
                "BEGIN EC PRIVATE KEY", "ghp_", "github_pat_", "ghs_")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def main(argv):
    phase = "complete"
    if "--phase" in argv:
        idx = argv.index("--phase")
        if idx + 1 >= len(argv):
            print("RESULT FAIL usage --phase declare|complete")
            return 2
        phase = argv[idx + 1]
    if phase not in ("declare", "complete"):
        print("RESULT FAIL unknown-phase %s" % phase)
        return 2
    for path in (B1, B2):
        if not os.path.isfile(path):
            print("RESULT FAIL boundary-declaration-missing %s" % path)
            return 2
    b1 = load(B1)
    b2 = load(B2)
    if not b1.get("statement") or not b2.get("statement"):
        print("RESULT FAIL boundary-without-statement")
        return 2

    results = []

    # B1-A2 - exactly one tier holds production credentials, and it is production.
    holders = []
    for path in sorted(glob.glob(os.path.join(TIERS, "*.yaml"))):
        doc = load(path)
        if doc.get("holds_production_credentials"):
            holders.append(doc.get("tier_id"))
    results.append(("B1-A2", holders == ["production"],
                    "tiers holding production credentials: %r" % holders))

    # B2-A2 - no private key block and no token prefix under access/ or infra/.
    leaks = []
    for root in ("access", "infra"):
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for filename in filenames:
                full = os.path.join(dirpath, filename)
                if os.path.abspath(full) == os.path.abspath(__file__):
                    continue          # this file names the markers it hunts for
                try:
                    with open(full, "r", encoding="utf-8", errors="ignore") as handle:
                        body = handle.read()
                except Exception:
                    continue
                for marker in LEAK_MARKERS:
                    if marker in body:
                        leaks.append("%s (%s)" % (full, marker))
    results.append(("B2-A2", not leaks, "leaks: %r" % leaks))

    if phase == "complete":
        # B1-A3 / B2-A1 - no fifth-tier credential is expected on a workstation.
        bad_hosts = []
        entries = sorted(glob.glob(os.path.join(FIFTH, "*.yaml")))
        if not entries:
            results.append(("B1-A3", False, "no fifth-tier entries found"))
            results.append(("B2-A1", False, "no fifth-tier entries found"))
        else:
            for path in entries:
                host = str(load(path).get("host") or "").lower()
                if not host:
                    bad_hosts.append("%s: empty host" % path)
                for marker in WORKSTATION_MARKERS:
                    if marker in host:
                        bad_hosts.append("%s: host %r looks like a workstation"
                                         % (path, host))
            results.append(("B1-A3", not bad_hosts, "bad hosts: %r" % bad_hosts))
            results.append(("B2-A1", not bad_hosts, "bad hosts: %r" % bad_hosts))

        # B2-A3 - the credential store does not passively yield to root.
        if not os.path.isfile(STORE):
            results.append(("B2-A3", False, "%s absent (built by L5-02-10)" % STORE))
        else:
            store = load(STORE)
            results.append(("B2-A3", store.get("passive_root_read") is False,
                            "passive_root_read=%r" % store.get("passive_root_read")))

        # B2-A4 - the shell gate requires a hardware-backed second factor.
        if not os.path.isfile(GATE):
            results.append(("B2-A4", False, "%s absent (built by L5-02-10)" % GATE))
        else:
            gate = load(GATE)
            second = gate.get("second_factor") or {}
            sshd = gate.get("sshd_required_settings") or {}
            ok = (bool(second.get("key_types_allowed"))
                  and all(str(k).startswith("sk-")
                          for k in second.get("key_types_allowed"))
                  and str(sshd.get("PasswordAuthentication")) == "no"
                  and gate.get("private_network_path_required") is True)
            results.append(("B2-A4", ok,
                            "key_types=%r PasswordAuthentication=%r private_path=%r"
                            % (second.get("key_types_allowed"),
                               sshd.get("PasswordAuthentication"),
                               gate.get("private_network_path_required"))))

        # B2-A5 - separation resolved, one way or the other.
        if not os.path.isfile(SEP):
            results.append(("B2-A5", False, "%s absent (built by L5-02-11)" % SEP))
        else:
            sep = load(SEP)
            state = str(sep.get("state") or "")
            if state == "separated":
                results.append(("B2-A5", True, "state=separated"))
            elif state == "accepted-risk":
                ok = bool(str(sep.get("holder") or "").strip()) \
                    and bool(str(sep.get("compensating_control") or "").strip()) \
                    and bool(str(sep.get("review_date") or "").strip())
                results.append(("B2-A5", ok, "state=accepted-risk holder=%r review=%r"
                                % (sep.get("holder"), sep.get("review_date"))))
            else:
                results.append(("B2-A5", False, "state=%r" % state))

    print("PHASE %s" % phase)
    failed = 0
    for name, ok, detail in results:
        print("ASSERTION %s %s %s" % (name, "OK" if ok else "FAIL", detail if not ok else ""))
        if not ok:
            failed += 1
    print("ASSERTIONS %d" % len(results))
    print("FAILED %d" % failed)
    if failed:
        print("RESULT FAIL")
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
PYEOF
chmod +x access/secrets/boundaries/check_boundaries.py

cat > access/secrets/boundaries/check-boundaries.sh <<'SHEOF'
#!/usr/bin/env bash
# access/secrets/boundaries/check-boundaries.sh
# The repository-side half of the two Section 40.3 trust boundaries.
# The host-side halves are access/secrets/host/check-credential-store.sh and
# infra/network/check-shell-gate.sh (L5-02-10).
#   exit 0  every assertion holds
#   exit 1  an assertion fails
#   exit 2  a boundary declaration is missing - FAIL CLOSED
set -eu
python access/secrets/boundaries/check_boundaries.py "$@"
SHEOF
chmod +x access/secrets/boundaries/check-boundaries.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/secrets/boundaries
git commit -m "L5-02-09: the two Section 40.3 trust boundaries, declared and checkable (Section 40.3, D95)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-boundaries
gh pr create --base integration \
  --title "L5-02-09 The two trust boundaries, declared and checkable (Section 40.3, D95)" \
  --body "Lane 5, Phase 2, task L5-02-09. Spec: Section 40.3 lines 3695-3704, D95 line 10188, Section 51.5 line 4502, Section 99.6 risk 6, invariants 24/25/26. Paths: access/secrets/boundaries/**. Self-verify output pasted below."
```

### Acceptance criteria

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | Boundary 1's statement is the spec's block quote | `python -c "import yaml;print(yaml.safe_load(open('access/secrets/boundaries/boundary-1-production.yaml'))['statement'])"` | `A fully compromised developer workstation must not yield production database access, production credentials, or the ability to deploy to production.` |
| 2 | Boundary 2's statement is the spec's block quote | `python -c "import yaml;print(yaml.safe_load(open('access/secrets/boundaries/boundary-2-control-plane.yaml'))['statement'])"` | `A fully compromised engineering workstation must not yield the control-plane machine-credential store.` |
| 3 | Boundary 2 attributes itself to D95 | `python -c "import yaml;d=yaml.safe_load(open('access/secrets/boundaries/boundary-2-control-plane.yaml'));print(d['decision'],d['added_by_decision'])"` | `D95 True` |
| 4 | Boundary 2 names the three §40.3 technical enforcements | `python -c "import yaml;print(len(yaml.safe_load(open('access/secrets/boundaries/boundary-2-control-plane.yaml'))['enforcement']))"` | `3` |
| 5 | Boundary 1 is declared technically, not behaviourally, enforced | `python -c "import yaml;d=yaml.safe_load(open('access/secrets/boundaries/boundary-1-production.yaml'));print(d['enforced_technically'],d['enforced_behaviourally'])"` | `True False` |
| 6 | Boundary 1 records what a compromise *does* yield | `python -c "import yaml;print(len(yaml.safe_load(open('access/secrets/boundaries/boundary-1-production.yaml'))['what_a_compromise_does_yield']))"` | `4` |
| 7 | The declare-phase check passes now | `bash access/secrets/boundaries/check-boundaries.sh --phase declare \| tail -1` | `RESULT PASS` |
| 8 | The complete-phase check fails now, naming its missing inputs | `bash access/secrets/boundaries/check-boundaries.sh --phase complete >/dev/null; echo $?` | `1` |
| 9 | The checker prints which phase it ran | `bash access/secrets/boundaries/check-boundaries.sh --phase declare \| head -1` | `PHASE declare` |
| 10 | The checker fails closed if a declaration is deleted | `mv access/secrets/boundaries/boundary-2-control-plane.yaml /tmp/b2.yaml; bash access/secrets/boundaries/check-boundaries.sh --phase declare >/dev/null 2>&1; echo $?; mv /tmp/b2.yaml access/secrets/boundaries/boundary-2-control-plane.yaml` | `2` |
| 11 | No file outside `access/secrets/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/secrets/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash access/secrets/boundaries/check-boundaries.sh --phase declare | grep -E '^(PHASE|ASSERTIONS|FAILED|RESULT)'
bash access/secrets/boundaries/check-boundaries.sh --phase complete >/dev/null 2>&1; echo "COMPLETE-PHASE-EXIT $?"
python - <<'PYEOF'
import yaml
b1 = yaml.safe_load(open('access/secrets/boundaries/boundary-1-production.yaml', encoding='utf-8'))
b2 = yaml.safe_load(open('access/secrets/boundaries/boundary-2-control-plane.yaml', encoding='utf-8'))
print("B1 %s" % b1['statement'])
print("B2 %s" % b2['statement'])
print("B2-DECISION %s" % b2['decision'])
print("B2-ENFORCEMENTS %d" % len(b2['enforcement']))
PYEOF
echo "L5-02-09 SELF-VERIFY PASS"
```

Expected output, exactly:

```
PHASE declare
ASSERTIONS 2
FAILED 0
RESULT PASS
COMPLETE-PHASE-EXIT 1
B1 A fully compromised developer workstation must not yield production database access, production credentials, or the ability to deploy to production.
B2 A fully compromised engineering workstation must not yield the control-plane machine-credential store.
B2-DECISION D95
B2-ENFORCEMENTS 3
L5-02-09 SELF-VERIFY PASS
```

`COMPLETE-PHASE-EXIT 1` is **correct at this point**: T10 and T11 have not landed, so `B2-A3`, `B2-A4` and
`B2-A5` cannot hold yet. T14 re-runs the same command and requires `0`.

### STOP rule

STOP — do not commit, do not push, file the blocker of Section 4 — if any of these hold:

* Assertion `B2-A2` fails: a private-key block or a GitHub token prefix is present under `access/` or
  `infra/`. That is a **security incident under §43**, not a task failure. Do not delete the file, do not
  force-push, do not rotate before capturing (§43.1). File the blocker, class `needs-decision`, and stop.
* Either block quote does not match the spec at lines 3697 and 3701 character for character. Class
  `shape-mismatch` — the boundary is the sentence; a paraphrase is a different boundary.
* `COMPLETE-PHASE-EXIT` is `0` at this task. That would mean T10 and T11 outputs already exist on
  `integration` from some other source. Class `foreign-path-conflict`.

---

## L5-02-10 — Ops-VM credential-store holding and hardware-key shell gate

| Field | Value |
|---|---|
| Task id | `L5-02-10` |
| Size | L |
| Depends on | `L5-02-09` |
| Slug | `host-holding` |
| Subsystem | L, M |
| Spec | §40.3 line 3703; D95 line 10188; §51.4 lines 4487–4498 (the private network path); §51.5 line 4502; §90.3 line 7982 (the compensating-control pattern); §45.3 (the write-only discipline) |
| Writes | `access/secrets/host/credential-store.yaml`, `access/secrets/host/check-credential-store.sh`, `access/secrets/tools/emit_shell_gate.py`, `infra/network/ops-vm-shell-gate.yaml`, `infra/network/check-shell-gate.sh` |

### Purpose

§40.3 line 3703 names two of the three technical enforcements of boundary 2, and this task declares both
and ships their host-side verifiers:

1. *"the fifth-tier credentials sit under a separate OS user or secret agent that a passive root shell does
   not read"*
2. *"shell access to the operations VM requires a second factor on top of the private network path of
   Section 51.4"*

Read the first one exactly as written. It says **passive**. Root on a host can always escalate actively —
become the owning user, attach to the agent, read process memory. D95 does not claim root containment and
neither does this declaration; it claims that a root shell that merely looks does not find the credential.
The declaration says so in its own `honest_limit` field, and names the compensating control for the active
case: host-level auditing shipped to a destination the host holds no credential to alter — the same
write-only discipline §45.3 gives the organisation export and §90.3 gives the Layer B store path.

Read the second one exactly as written too. It says **on top of**. The private network path of §51.4 is not
the second factor; it is the path the second factor sits on. A declaration that treats the VPN as the
second factor has one factor.

**Nothing here is provisioned by this task.** `ops-vm/credentials/**` and the systemd units belong to
L5-04-07; this task writes the requirement and the verifier that proves phase 4 met it.

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-host-holding
mkdir -p access/secrets/host access/secrets/tools infra/network
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/host/credential-store.yaml <<'YAMLEOF'
# access/secrets/host/credential-store.yaml
# Section 40.3 line 3703, enforcement E1 of boundary 2; D95 line 10188.
# DECLARATION ONLY. ops-vm/credentials/** and the systemd units that consume
# this store are provisioned by L5-04-07. This file states the requirement and
# names the verifier that proves phase 4 met it.
schema_version: 1
boundary: boundary-2-control-plane
enforcement_id: E1
decision: D95
store_path: "/var/lib/ops-vm/creds"
owner_os_user: "cp-creds"
directory_mode: "0700"
file_mode: "0600"
passive_root_read: false
mechanism: "the store is owned by a separate OS user; service units receive the credential through systemd LoadCredential= / SetCredential= (or an equivalent secret-agent socket), so the process that needs it gets it and an interactive root shell does not read it by looking"
honest_limit: "root can still escalate ACTIVELY - become the owning user, attach to the agent, or read process memory. Section 40.3 requires that a passive root shell does not read the store; it does not claim root containment, and neither does this file."
compensating_control_for_active_root:
  control: "host-level file-access auditing on the store path"
  shipped_to: "a destination the host holds no credential to alter"
  discipline: "append-only, write-only, object-locked - the same discipline the organisation export uses (Section 45.3), applied to the store path the way Section 90.3 applies it to the Layer B store"
  cannot_be_silently_defeated_by: "the holder of host root"
never:
  - "no fifth-tier credential is ever placed on a workstation"
  - "no fifth-tier credential is ever committed to any repository"
  - "no fifth-tier credential value ever appears in the service user's login-shell environment"
  - "no fifth-tier credential is ever readable by a world- or group-readable file"
verifier: "access/secrets/host/check-credential-store.sh"
provisioned_by: "L5-04-07 (ops-vm/credentials/**)"
spec_anchor: "Section 40.3"
spec_lines: "3703"
YAMLEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/host/check-credential-store.sh <<'SHEOF'
#!/usr/bin/env bash
# access/secrets/host/check-credential-store.sh
# The HOST-SIDE half of boundary 2, enforcement E1 (Section 40.3 line 3703).
# Run ON the operations VM, or over ssh:
#   ssh <ops-vm> 'bash -s' < access/secrets/host/check-credential-store.sh
#
#   exit 0  every host assertion holds
#   exit 1  an assertion fails
#   exit 2  the host cannot be inspected - FAIL CLOSED (blocker class host-unreachable)
set -u
STORE=/var/lib/ops-vm/creds
USER_EXPECTED=cp-creds
FAIL=0

if [ ! -d "$STORE" ]; then
  echo "HOST-CHECK H1 FAIL store directory $STORE absent"
  echo "RESULT FAIL"
  exit 2
fi

OWNER=$(stat -c '%U' "$STORE" 2>/dev/null || echo UNKNOWN)
MODE=$(stat -c '%a' "$STORE" 2>/dev/null || echo UNKNOWN)
if [ "$OWNER" = "$USER_EXPECTED" ]; then echo "HOST-CHECK H1 OK owner=$OWNER"; else echo "HOST-CHECK H1 FAIL owner=$OWNER expected=$USER_EXPECTED"; FAIL=1; fi
if [ "$MODE" = "700" ]; then echo "HOST-CHECK H2 OK mode=$MODE"; else echo "HOST-CHECK H2 FAIL mode=$MODE expected=700"; FAIL=1; fi

LOOSE=$(find "$STORE" -type f ! -perm 600 2>/dev/null | wc -l | tr -d ' ')
if [ "$LOOSE" = "0" ]; then echo "HOST-CHECK H3 OK no-loose-modes"; else echo "HOST-CHECK H3 FAIL $LOOSE files not mode 600"; FAIL=1; fi

# The credential reaches the service through systemd credentials, not through a
# file the service unit cats in an ExecStart line.
UNITS=$(systemctl list-units --type=service --all --no-legend 2>/dev/null | awk '{print $1}' | grep -c '^reconcile-' || true)
CREDS=$(systemctl cat 'reconcile-*.service' 2>/dev/null | grep -c -E 'LoadCredential=|SetCredential=' || true)
if [ "$UNITS" = "0" ]; then
  echo "HOST-CHECK H4 FAIL no reconcile-* service units on this host"
  FAIL=1
elif [ "$CREDS" -ge 1 ]; then
  echo "HOST-CHECK H4 OK systemd-credential-delivery"
else
  echo "HOST-CHECK H4 FAIL no LoadCredential=/SetCredential= in reconcile-* units"
  FAIL=1
fi

# No credential value in the system manager environment.
ENVHITS=$(systemctl show-environment 2>/dev/null | grep -c -i -E 'token|secret|api_key|password' || true)
if [ "$ENVHITS" = "0" ]; then echo "HOST-CHECK H5 OK clean-manager-environment"; else echo "HOST-CHECK H5 FAIL $ENVHITS credential-shaped entries in the manager environment"; FAIL=1; fi

# The store path is audited, and the audit leaves the host.
AUDIT=$(auditctl -l 2>/dev/null | grep -c "$STORE" || true)
if [ "$AUDIT" -ge 1 ]; then echo "HOST-CHECK H6 OK store-path-audited"; else echo "HOST-CHECK H6 FAIL no audit rule on $STORE"; FAIL=1; fi

echo "HOST-FAILURES $FAIL"
if [ "$FAIL" -eq 0 ]; then echo "RESULT PASS"; exit 0; else echo "RESULT FAIL"; exit 1; fi
SHEOF
chmod +x access/secrets/host/check-credential-store.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/tools/emit_shell_gate.py <<'PYEOF'
#!/usr/bin/env python3
"""Emit infra/network/ops-vm-shell-gate.yaml from the frozen contract.

Section 40.3 line 3703, enforcement E2 of boundary 2: "shell access to the
operations VM requires a second factor on top of the private network path of
Section 51.4."

"On top of" is load-bearing. The private network path is not the second factor;
it is the path the second factor sits on. Both are required, separately.

Key ids and the hostname come from contracts/access/access-inputs.yaml. This
program names no host and no key of its own.

Usage: emit_shell_gate.py [<inputs.yaml> [<out-path>]]
"""
import os
import sys

import yaml

ALLOWED_KEY_TYPES = [
    "sk-ssh-ed25519@openssh.com",
    "sk-ecdsa-sha2-nistp256@openssh.com",
]


def main(argv):
    inputs = argv[1] if len(argv) > 1 else os.path.join(
        "contracts", "access", "access-inputs.yaml")
    out = argv[2] if len(argv) > 2 else os.path.join(
        "infra", "network", "ops-vm-shell-gate.yaml")
    if not os.path.isfile(inputs):
        print("RESULT FAIL inputs-unreadable %s" % inputs)
        return 2
    try:
        with open(inputs, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
    except Exception as exc:                                    # fail closed
        print("RESULT FAIL inputs-unparseable %s" % exc)
        return 2
    block = doc.get("ops_vm")
    if not isinstance(block, dict):
        print("RESULT FAIL no-ops_vm-block %s" % inputs)
        return 2
    hostname = str(block.get("hostname") or "").strip()
    keys = block.get("shell_second_factor_key_ids") or []
    if not hostname:
        print("RESULT FAIL ops_vm.hostname-empty")
        return 2
    if not keys:
        print("RESULT FAIL ops_vm.shell_second_factor_key_ids-empty")
        return 2

    lines = []
    lines.append("# infra/network/ops-vm-shell-gate.yaml")
    lines.append("# Generated by access/secrets/tools/emit_shell_gate.py. Do not hand-edit.")
    lines.append("# Section 40.3 line 3703 (boundary 2, enforcement E2);")
    lines.append("# Section 51.4 lines 4487-4498 (the private network path it sits on top of).")
    lines.append("schema_version: 1")
    lines.append("boundary: boundary-2-control-plane")
    lines.append("enforcement_id: E2")
    lines.append("decision: D95")
    lines.append('host: "%s"' % hostname)
    lines.append("private_network_path_required: true")
    lines.append('private_network_path_source: "Section 51.4 - every control-plane surface is reachable only over a private network path with SSO in front of it"')
    lines.append("private_network_path_is_the_second_factor: false")
    lines.append('private_network_path_note: "Section 40.3 says the second factor is ON TOP OF the private path. Treating the path as the factor leaves one factor."')
    lines.append("second_factor:")
    lines.append("  mechanism: hardware-backed-ssh-key")
    lines.append("  key_types_allowed:")
    for key_type in ALLOWED_KEY_TYPES:
        lines.append('    - "%s"' % key_type)
    lines.append("  touch_required: true")
    lines.append("  no_touch_required_permitted: false")
    lines.append("  authorized_key_ids:")
    for key in keys:
        lines.append('    - "%s"' % key)
    lines.append("sshd_required_settings:")
    lines.append('  PasswordAuthentication: "no"')
    lines.append('  KbdInteractiveAuthentication: "no"')
    lines.append('  PermitRootLogin: "no"')
    lines.append('  AuthenticationMethods: "publickey"')
    lines.append('  PubkeyAuthentication: "yes"')
    lines.append('verifier: "infra/network/check-shell-gate.sh"')
    lines.append('spec_anchor: "Section 40.3"')
    lines.append('spec_lines: "3703"')
    body = "\n".join(lines) + "\n"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(body)
    print("WROTE %s keys=%d" % (out, len(keys)))
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
PYEOF
chmod +x access/secrets/tools/emit_shell_gate.py
python access/secrets/tools/emit_shell_gate.py
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > infra/network/check-shell-gate.sh <<'SHEOF'
#!/usr/bin/env bash
# infra/network/check-shell-gate.sh
# The HOST-SIDE half of boundary 2, enforcement E2 (Section 40.3 line 3703).
# Run ON the operations VM, or over ssh:
#   ssh <ops-vm> 'bash -s' < infra/network/check-shell-gate.sh
#
#   exit 0  the shell gate holds
#   exit 1  an assertion fails
#   exit 2  sshd cannot be inspected - FAIL CLOSED (blocker class host-unreachable)
set -u
FAIL=0
CFG=$(sshd -T 2>/dev/null)
if [ -z "$CFG" ]; then
  echo "GATE-CHECK G0 FAIL sshd -T produced nothing"
  echo "RESULT FAIL"
  exit 2
fi
want () {  # want <key> <value> <id>
  got=$(printf '%s\n' "$CFG" | awk -v k="$1" '$1==k {print $2; exit}')
  if [ "$got" = "$2" ]; then
    echo "GATE-CHECK $3 OK $1=$got"
  else
    echo "GATE-CHECK $3 FAIL $1=$got expected=$2"
    FAIL=1
  fi
}
want passwordauthentication no G1
want kbdinteractiveauthentication no G2
want permitrootlogin no G3
want pubkeyauthentication yes G4

# Every authorized key on the host is hardware-backed, and none waives touch.
KEYS=$(cat /home/*/.ssh/authorized_keys /root/.ssh/authorized_keys 2>/dev/null | grep -v '^#' | grep -v '^$' || true)
TOTAL=$(printf '%s\n' "$KEYS" | grep -c . || true)
SK=$(printf '%s\n' "$KEYS" | grep -c 'sk-ssh-ed25519@openssh.com\|sk-ecdsa-sha2-nistp256@openssh.com' || true)
NOTOUCH=$(printf '%s\n' "$KEYS" | grep -c 'no-touch-required' || true)
if [ "$TOTAL" = "0" ]; then
  echo "GATE-CHECK G5 FAIL no authorized keys found to inspect"
  FAIL=1
elif [ "$TOTAL" = "$SK" ]; then
  echo "GATE-CHECK G5 OK all $TOTAL authorized keys are hardware-backed"
else
  echo "GATE-CHECK G5 FAIL $((TOTAL - SK)) of $TOTAL authorized keys are not hardware-backed"
  FAIL=1
fi
if [ "$NOTOUCH" = "0" ]; then
  echo "GATE-CHECK G6 OK no-touch-required absent"
else
  echo "GATE-CHECK G6 FAIL $NOTOUCH keys waive the touch requirement"
  FAIL=1
fi

# The gate sits ON TOP OF the private path; the host must not answer publicly.
PUB=$(ss -lntp 2>/dev/null | awk '$4 ~ /(^0\.0\.0\.0:22$|^\[::\]:22$)/' | wc -l | tr -d ' ')
if [ "$PUB" = "0" ]; then
  echo "GATE-CHECK G7 OK sshd is not bound to a wildcard address"
else
  echo "GATE-CHECK G7 FAIL sshd answers on a wildcard address; the private path of Section 51.4 is not in front of it"
  FAIL=1
fi

echo "GATE-FAILURES $FAIL"
if [ "$FAIL" -eq 0 ]; then echo "RESULT PASS"; exit 0; else echo "RESULT FAIL"; exit 1; fi
SHEOF
chmod +x infra/network/check-shell-gate.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/secrets/host access/secrets/tools/emit_shell_gate.py infra/network
git commit -m "L5-02-10: fifth-tier holding requirement and the hardware-key shell gate (Section 40.3, D95)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-host-holding
gh pr create --base integration \
  --title "L5-02-10 Ops-VM credential-store holding and hardware-key shell gate" \
  --body "Lane 5, Phase 2, task L5-02-10. Spec: Section 40.3 line 3703, D95 line 10188, Section 51.4, Section 51.5, Section 90.3, Section 45.3. Paths: access/secrets/host/**, access/secrets/tools/emit_shell_gate.py, infra/network/**. Self-verify output pasted below."
```

### Acceptance criteria

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | The store declaration denies passive root reads | `python -c "import yaml;print(yaml.safe_load(open('access/secrets/host/credential-store.yaml'))['passive_root_read'])"` | `False` |
| 2 | The declaration states its honest limit rather than claiming root containment | `python -c "import yaml;print('root containment' in yaml.safe_load(open('access/secrets/host/credential-store.yaml'))['honest_limit'])"` | `True` |
| 3 | The compensating control ships off-host | `python -c "import yaml;print(yaml.safe_load(open('access/secrets/host/credential-store.yaml'))['compensating_control_for_active_root']['shipped_to'])"` | `a destination the host holds no credential to alter` |
| 4 | The shell gate requires the private path **and** a second factor | `python -c "import yaml;d=yaml.safe_load(open('infra/network/ops-vm-shell-gate.yaml'));print(d['private_network_path_required'],d['private_network_path_is_the_second_factor'])"` | `True False` |
| 5 | Only hardware-backed key types are allowed | `python -c "import yaml;print(all(k.startswith('sk-') for k in yaml.safe_load(open('infra/network/ops-vm-shell-gate.yaml'))['second_factor']['key_types_allowed']))"` | `True` |
| 6 | Touch cannot be waived | `python -c "import yaml;d=yaml.safe_load(open('infra/network/ops-vm-shell-gate.yaml'))['second_factor'];print(d['touch_required'],d['no_touch_required_permitted'])"` | `True False` |
| 7 | Password authentication is off | `python -c "import yaml;print(yaml.safe_load(open('infra/network/ops-vm-shell-gate.yaml'))['sshd_required_settings']['PasswordAuthentication'])"` | `no` |
| 8 | At least one authorised key id came from the contract | `python -c "import yaml;print(len(yaml.safe_load(open('infra/network/ops-vm-shell-gate.yaml'))['second_factor']['authorized_key_ids'])>=1)"` | `True` |
| 9 | The gate emitter is idempotent | `python access/secrets/tools/emit_shell_gate.py >/dev/null && git diff --exit-code -- infra/network/ops-vm-shell-gate.yaml >/dev/null; echo $?` | `0` |
| 10 | The boundary checker's complete phase now passes `B2-A3` and `B2-A4` | `bash access/secrets/boundaries/check-boundaries.sh --phase complete \| grep -c -E '^ASSERTION B2-A[34] FAIL'` | `0` |
| 11 | Both host verifiers are executable shell, not prose | `head -1 access/secrets/host/check-credential-store.sh infra/network/check-shell-gate.sh \| grep -c '#!/usr/bin/env bash'` | `2` |
| 12 | No file outside `access/secrets/` and `infra/network/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cvE '^(access/secrets/|infra/network/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python - <<'PYEOF'
import yaml
s = yaml.safe_load(open('access/secrets/host/credential-store.yaml', encoding='utf-8'))
g = yaml.safe_load(open('infra/network/ops-vm-shell-gate.yaml', encoding='utf-8'))
print("PASSIVE-ROOT-READ %s" % s['passive_root_read'])
print("OWNER-OS-USER %s" % s['owner_os_user'])
print("COMPENSATING-CONTROL-SHIPS-OFF-HOST %s"
      % (s['compensating_control_for_active_root']['shipped_to']
         == 'a destination the host holds no credential to alter'))
print("PRIVATE-PATH-REQUIRED %s" % g['private_network_path_required'])
print("PRIVATE-PATH-IS-THE-FACTOR %s" % g['private_network_path_is_the_second_factor'])
print("HARDWARE-KEYS-ONLY %s"
      % all(k.startswith('sk-') for k in g['second_factor']['key_types_allowed']))
print("TOUCH-WAIVABLE %s" % g['second_factor']['no_touch_required_permitted'])
print("AUTHORIZED-KEYS %d" % len(g['second_factor']['authorized_key_ids']))
PYEOF
python access/secrets/tools/emit_shell_gate.py >/dev/null && git diff --exit-code -- infra/network/ops-vm-shell-gate.yaml >/dev/null && echo "IDEMPOTENT yes"
bash access/secrets/boundaries/check-boundaries.sh --phase complete | grep -E '^ASSERTION B2-A[34]' | sed 's/  *$//'
echo "L5-02-10 SELF-VERIFY PASS"
```

Expected output, exactly (`AUTHORIZED-KEYS` is `<varies>` — it is the length of the contract's list, and
must be at least 1):

```
PASSIVE-ROOT-READ False
OWNER-OS-USER cp-creds
COMPENSATING-CONTROL-SHIPS-OFF-HOST True
PRIVATE-PATH-REQUIRED True
PRIVATE-PATH-IS-THE-FACTOR False
HARDWARE-KEYS-ONLY True
TOUCH-WAIVABLE False
AUTHORIZED-KEYS <varies>
IDEMPOTENT yes
ASSERTION B2-A3 OK
ASSERTION B2-A4 OK
L5-02-10 SELF-VERIFY PASS
```

### Host-side execution — separate, and not part of this commit

The two host verifiers run against a live operations VM. Run them once the VM exists (phase 4, task
L5-04-02), from a host with the private-path access of §51.4:

```bash
set -euo pipefail
ssh "$OPS_VM_ALIAS" 'bash -s' < access/secrets/host/check-credential-store.sh
ssh "$OPS_VM_ALIAS" 'bash -s' < infra/network/check-shell-gate.sh
```

Each must end `RESULT PASS`. A failure here is a live boundary-2 breach, not a script bug.

### STOP rule

STOP — do not commit, do not push, file the blocker of Section 4 — if any of these hold:

* `contracts/access/access-inputs.yaml` carries no `ops_vm.shell_second_factor_key_ids`, or the list is
  empty. **Do not invent a key id and do not fall back to password authentication.** Class
  `missing-contract`.
* The available hardware does not support `sk-` key types, or no hardware key exists to enrol. Class
  `tpm-absent`; the decision needed from L0 is whether to procure keys or record a dated
  `policy_waiver` exception under §54.2 with an expiry, an owner and a deactivation trigger.
* Either host verifier cannot reach the operations VM when it is run. Class `host-unreachable` — the
  verifiers fail closed by design and a `RESULT FAIL` from an unreachable host is not a pass.
* The executor is tempted to treat the VPN as the second factor to make the gate pass. §40.3 line 3703 says
  the factor is **on top of** the private path. Class `needs-decision`.

---

## L5-02-11 — Rotator / host-root separation, or the recorded accepted risk

| Field | Value |
|---|---|
| Task id | `L5-02-11` |
| Size | M |
| Depends on | `L5-02-04`, `L5-02-09` |
| Slug | `separation` |
| Subsystem | L |
| Spec | §40.3 line 3703 (third enforcement); §90.3 line 7982 (the accepted-risk shape); §54.2 lines 4787–4797 (expiry and compensating control are mandatory); §84.5 (the review cadence) |
| Writes | `access/secrets/separation/check_separation.py`, `access/secrets/separation/check-separation.sh`, `access/secrets/separation/accepted-risk.template.yaml`, `access/secrets/separation/separation.result.yaml`, `access/secrets/testdata/separation/separated/access-inputs.yaml`, `access/secrets/testdata/separation/concentrated/access-inputs.yaml`, `access/secrets/testdata/separation/concentrated-with-record/access-inputs.yaml`, `access/secrets/testdata/separation/concentrated-with-record/rotator-hostroot.yaml`, `access/secrets/testdata/separation/incomplete-record/access-inputs.yaml`, `access/secrets/testdata/separation/incomplete-record/rotator-hostroot.yaml` |

### Purpose

§40.3 line 3703 closes with the enforcement that is easiest to let slide: *"the rotator of a fifth-tier
credential and the holder of host root on the machine that stores it are separated where headcount permits
— where it does not, the concentration is a recorded accepted risk with a named holder and a dated review,
never an unstated default."*

At small headcount the two are frequently the same person, and that is permitted. What is **not** permitted
is silence. So this task computes the answer from the contract and forces exactly one of three states:

| State | Meaning | Exit |
|---|---|---|
| `separated` | no credential's rotator is the host-root holder | 0 |
| `accepted-risk` | at least one is, **and** a complete accepted-risk record exists | 0 |
| `UNRESOLVED` | at least one is, and no complete record exists — an unstated default | 1 |

The accepted-risk record's required shape is borrowed from §90.3's host-level acceptance, which states the
pattern in full, and from §54.2, which makes expiry and a compensating control mandatory: *"An accepted
risk with no named holder, no compensating control and no expiry is undocumented policy."*

**The executor never authors the record.** It is supplied by L0 at
`contracts/access/accepted-risks/rotator-hostroot.yaml`. This task ships the template so L0 knows the exact
shape, validates whatever L0 supplied, and STOPs if the concentration exists and nothing was supplied.

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-separation
mkdir -p access/secrets/separation \
         access/secrets/testdata/separation/separated \
         access/secrets/testdata/separation/concentrated \
         access/secrets/testdata/separation/concentrated-with-record \
         access/secrets/testdata/separation/incomplete-record
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/separation/accepted-risk.template.yaml <<'YAMLEOF'
# access/secrets/separation/accepted-risk.template.yaml
# THE SHAPE L0 MUST SUPPLY at contracts/access/accepted-risks/rotator-hostroot.yaml
# when headcount does not permit separating a fifth-tier rotator from the holder
# of host root (Section 40.3 line 3703).
#
# The shape is not invented here. It is the accepted-risk pattern Section 90.3
# line 7982 states in full for host-level administrative access, plus the two
# things Section 54.2 makes mandatory for every exception - an expiry and a
# compensating control. Section 54.2: "An accepted risk with no named holder, no
# compensating control and no expiry is undocumented policy."
#
# THIS FILE IS A TEMPLATE. It is never itself the record. A lane never writes
# contracts/**; L0 does (PARTITION rule 2).
schema_version: 1
risk_id: "rotator-hostroot-concentration"
statement: "The rotator of one or more fifth-tier machine credentials also holds host root on the machine that stores them."
holder: ""                       # the person id who holds both. Named, never implied
does_not_confer: ""              # what holding both does NOT grant - state it explicitly
compensating_control: ""         # a control the holder cannot silently defeat
compensating_control_store: ""   # where its executions land, so reconciliation can compare
compensating_control_cadence: "" # how often it runs
review_date: ""                  # a DATE, not "periodically"
review_cadence: "quarterly"      # calibrated configuration, Section 84.5
expiry: ""                       # mandatory - Section 54.2
deactivation_trigger: ""         # what would end this concentration, e.g. a second DevOps holder
owner: ""                        # who owns the review
accepted_by: ""                  # the decider
accepted_at: ""                  # UTC stamp
YAMLEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/separation/check_separation.py <<'PYEOF'
#!/usr/bin/env python3
"""Rotator / host-root separation, or the recorded accepted risk.

Section 40.3 line 3703; Section 90.3 line 7982 (the accepted-risk shape);
Section 54.2 lines 4787-4797 (expiry and compensating control are mandatory).

Three states and no fourth:
  separated     no fifth-tier rotator is the host-root holder            exit 0
  accepted-risk at least one is, and a COMPLETE record exists            exit 0
  UNRESOLVED    at least one is, and no complete record exists           exit 1

An UNRESOLVED result is exactly what Section 40.3 calls "an unstated default",
which it forbids. It is a decision for L0, never for the executor.

Usage:
  check_separation.py [<inputs.yaml> [<accepted-risk.yaml>]] [--write]

--write emits access/secrets/separation/separation.result.yaml.
Exit 0 resolved, 1 unresolved or incomplete record, 2 input fault.
"""
import os
import sys

import yaml

REQUIRED_RECORD_FIELDS = [
    "risk_id",
    "statement",
    "holder",
    "does_not_confer",
    "compensating_control",
    "compensating_control_store",
    "compensating_control_cadence",
    "review_date",
    "review_cadence",
    "expiry",
    "deactivation_trigger",
    "owner",
    "accepted_by",
    "accepted_at",
]
RESULT_PATH = os.path.join("access", "secrets", "separation",
                           "separation.result.yaml")


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    write = "--write" in argv
    inputs = args[0] if args else os.path.join(
        "contracts", "access", "access-inputs.yaml")
    record_path = args[1] if len(args) > 1 else os.path.join(
        "contracts", "access", "accepted-risks", "rotator-hostroot.yaml")
    if not os.path.isfile(inputs):
        print("RESULT FAIL inputs-unreadable %s" % inputs)
        return 2
    try:
        with open(inputs, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
    except Exception as exc:                                    # fail closed
        print("RESULT FAIL inputs-unparseable %s" % exc)
        return 2
    fifth = doc.get("fifth_tier")
    ops = doc.get("ops_vm")
    if not isinstance(fifth, dict) or not isinstance(ops, dict):
        print("RESULT FAIL contract-shape fifth_tier/ops_vm")
        return 2
    root_holder = str(ops.get("host_root_holder") or "").strip()
    if not root_holder:
        print("RESULT FAIL ops_vm.host_root_holder-empty")
        return 2

    collisions = []
    for cred in sorted(fifth):
        entry = fifth.get(cred) or {}
        rotator = str(entry.get("rotator") or "").strip()
        if not rotator:
            print("RESULT FAIL rotator-empty %s" % cred)
            return 2
        if rotator == root_holder:
            collisions.append(cred)
            print("CONCENTRATION %s rotator=%s is also host_root_holder" % (cred, rotator))

    state = None
    holder = ""
    review = ""
    if not collisions:
        state = "separated"
        print("SEPARATION separated")
    else:
        if not os.path.isfile(record_path):
            print("SEPARATION UNRESOLVED no accepted-risk record at %s" % record_path)
            print("QUOTE Section 40.3: never an unstated default")
            print("RESULT FAIL")
            return 1
        try:
            with open(record_path, "r", encoding="utf-8") as handle:
                rec = yaml.safe_load(handle) or {}
        except Exception as exc:                                # fail closed
            print("RESULT FAIL record-unparseable %s" % exc)
            return 2
        missing = [f for f in REQUIRED_RECORD_FIELDS
                   if not str(rec.get(f) or "").strip()]
        if missing:
            for field in missing:
                print("RECORD-INCOMPLETE %s" % field)
            print("QUOTE Section 54.2: An accepted risk with no named holder, no compensating control and no expiry is undocumented policy")
            print("SEPARATION accepted-risk-incomplete")
            print("RESULT FAIL")
            return 1
        state = "accepted-risk"
        holder = str(rec["holder"])
        review = str(rec["review_date"])
        print("SEPARATION accepted-risk holder=%s review=%s" % (holder, review))

    if write:
        lines = []
        lines.append("# %s" % RESULT_PATH)
        lines.append("# Generated by access/secrets/separation/check_separation.py.")
        lines.append("# Section 40.3 line 3703. Do not hand-edit: re-run the checker.")
        lines.append("schema_version: 1")
        lines.append("boundary: boundary-2-control-plane")
        lines.append("enforcement_id: E3")
        lines.append("state: %s" % state)
        if collisions:
            lines.append("concentrated_credentials:")
            for cred in collisions:
                lines.append("  - %s" % cred)
        else:
            lines.append("concentrated_credentials: []")
        lines.append('holder: "%s"' % holder)
        lines.append('review_date: "%s"' % review)
        if state == "accepted-risk":
            lines.append('compensating_control: "see contracts/access/accepted-risks/rotator-hostroot.yaml"')
        else:
            lines.append('compensating_control: ""')
        lines.append('spec_anchor: "Section 40.3"')
        lines.append('spec_lines: "3703"')
        os.makedirs(os.path.dirname(RESULT_PATH), exist_ok=True)
        with open(RESULT_PATH, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(lines) + "\n")
        print("WROTE %s" % RESULT_PATH)
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
PYEOF
chmod +x access/secrets/separation/check_separation.py

cat > access/secrets/separation/check-separation.sh <<'SHEOF'
#!/usr/bin/env bash
# access/secrets/separation/check-separation.sh
# Boundary 2, enforcement E3 (Section 40.3 line 3703).
#   exit 0  separated, or a complete accepted-risk record exists
#   exit 1  UNRESOLVED - an unstated default, which Section 40.3 forbids
#   exit 2  input fault - FAIL CLOSED
set -eu
python access/secrets/separation/check_separation.py "$@"
SHEOF
chmod +x access/secrets/separation/check-separation.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
S=access/secrets/testdata/separation
cat > $S/separated/access-inputs.yaml <<'YAMLEOF'
# POSITIVE FIXTURE. Rotators and the host-root holder are different people.
schema_version: 1
fifth_tier:
  reconciler: { rotator: "person-a" }
  provisioning-cli: { rotator: "person-a" }
  organisation-export-token: { rotator: "person-b" }
  records-writer: { rotator: "person-a" }
  layer-b-backup: { rotator: "person-b" }
ops_vm:
  host_root_holder: "person-c"
YAMLEOF

cat > $S/concentrated/access-inputs.yaml <<'YAMLEOF'
# NEGATIVE FIXTURE. One rotator is also the host-root holder and no record
# exists - "an unstated default", which Section 40.3 forbids.
schema_version: 1
fifth_tier:
  reconciler: { rotator: "person-c" }
  provisioning-cli: { rotator: "person-a" }
  organisation-export-token: { rotator: "person-b" }
  records-writer: { rotator: "person-a" }
  layer-b-backup: { rotator: "person-b" }
ops_vm:
  host_root_holder: "person-c"
YAMLEOF

cp $S/concentrated/access-inputs.yaml $S/concentrated-with-record/access-inputs.yaml
cp $S/concentrated/access-inputs.yaml $S/incomplete-record/access-inputs.yaml

cat > $S/concentrated-with-record/rotator-hostroot.yaml <<'YAMLEOF'
# POSITIVE FIXTURE. The concentration exists AND is recorded in full, which is
# what Section 40.3 permits where headcount does not allow separation.
schema_version: 1
risk_id: "rotator-hostroot-concentration"
statement: "The reconciler credential's rotator also holds host root on the operations VM."
holder: "person-c"
does_not_confer: "Holding both does not confer people-intelligence, does not confer Layer B access, and does not make this person a bypass actor on the control-plane repository."
compensating_control: "host-level file-access auditing on the fifth-tier store path, shipped off-host"
compensating_control_store: "the object-locked audit destination the host holds no credential to alter"
compensating_control_cadence: "continuous, reviewed on the calibration cadence"
review_date: "2026-06-30"
review_cadence: "quarterly"
expiry: "2026-09-30"
deactivation_trigger: "a second DevOps-capability holder is onboarded"
owner: "person-b"
accepted_by: "founder"
accepted_at: "2026-03-02T09:00:00Z"
YAMLEOF

cat > $S/incomplete-record/rotator-hostroot.yaml <<'YAMLEOF'
# NEGATIVE FIXTURE. A record exists but carries no compensating control and no
# expiry - Section 54.2: "undocumented policy".
schema_version: 1
risk_id: "rotator-hostroot-concentration"
statement: "The reconciler credential's rotator also holds host root on the operations VM."
holder: "person-c"
does_not_confer: "nothing further"
compensating_control: ""
compensating_control_store: ""
compensating_control_cadence: ""
review_date: ""
review_cadence: "quarterly"
expiry: ""
deactivation_trigger: ""
owner: "person-b"
accepted_by: "founder"
accepted_at: "2026-03-02T09:00:00Z"
YAMLEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python access/secrets/separation/check_separation.py --write
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/secrets/separation access/secrets/testdata/separation
git commit -m "L5-02-11: rotator/host-root separation, or the recorded accepted risk (Section 40.3, Section 90.3, Section 54.2)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-separation
gh pr create --base integration \
  --title "L5-02-11 Rotator / host-root separation, or the recorded accepted risk" \
  --body "Lane 5, Phase 2, task L5-02-11. Spec: Section 40.3 line 3703, Section 90.3 line 7982, Section 54.2 lines 4787-4797, Section 84.5. Paths: access/secrets/separation/**, access/secrets/testdata/separation/**. Self-verify output pasted below."
```

### Acceptance criteria

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | The separated fixture resolves | `python access/secrets/separation/check_separation.py access/secrets/testdata/separation/separated/access-inputs.yaml /tmp/none.yaml \| grep '^SEPARATION'` | `SEPARATION separated` |
| 2 | The concentrated fixture with no record is UNRESOLVED | `python access/secrets/separation/check_separation.py access/secrets/testdata/separation/concentrated/access-inputs.yaml /tmp/none.yaml \| grep -c '^SEPARATION UNRESOLVED'` | `1` |
| 3 | …and exits 1 | `python access/secrets/separation/check_separation.py access/secrets/testdata/separation/concentrated/access-inputs.yaml /tmp/none.yaml >/dev/null; echo $?` | `1` |
| 4 | A complete record resolves the concentration | `python access/secrets/separation/check_separation.py access/secrets/testdata/separation/concentrated-with-record/access-inputs.yaml access/secrets/testdata/separation/concentrated-with-record/rotator-hostroot.yaml \| grep -c '^SEPARATION accepted-risk holder=person-c'` | `1` |
| 5 | An incomplete record does not | `python access/secrets/separation/check_separation.py access/secrets/testdata/separation/incomplete-record/access-inputs.yaml access/secrets/testdata/separation/incomplete-record/rotator-hostroot.yaml \| grep -c '^SEPARATION accepted-risk-incomplete'` | `1` |
| 6 | The incomplete record names every missing field | `python access/secrets/separation/check_separation.py access/secrets/testdata/separation/incomplete-record/access-inputs.yaml access/secrets/testdata/separation/incomplete-record/rotator-hostroot.yaml \| grep -c '^RECORD-INCOMPLETE'` | `6` |
| 7 | The §54.2 sentence is quoted, not paraphrased | `python access/secrets/separation/check_separation.py access/secrets/testdata/separation/incomplete-record/access-inputs.yaml access/secrets/testdata/separation/incomplete-record/rotator-hostroot.yaml \| grep -c 'undocumented policy'` | `1` |
| 8 | The result file exists and carries one of the two resolved states | `python -c "import yaml;print(yaml.safe_load(open('access/secrets/separation/separation.result.yaml'))['state'] in ('separated','accepted-risk'))"` | `True` |
| 9 | The checker fails closed on a missing contract | `python access/secrets/separation/check_separation.py /tmp/no-such.yaml >/dev/null 2>&1; echo $?` | `2` |
| 10 | The boundary checker's `B2-A5` now passes | `bash access/secrets/boundaries/check-boundaries.sh --phase complete \| grep -c '^ASSERTION B2-A5 FAIL'` | `0` |
| 11 | No file outside `access/secrets/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/secrets/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
S=access/secrets/testdata/separation
python access/secrets/separation/check_separation.py $S/separated/access-inputs.yaml /tmp/none.yaml | grep '^SEPARATION'
python access/secrets/separation/check_separation.py $S/concentrated/access-inputs.yaml /tmp/none.yaml | grep '^SEPARATION'
python access/secrets/separation/check_separation.py $S/concentrated-with-record/access-inputs.yaml $S/concentrated-with-record/rotator-hostroot.yaml | grep '^SEPARATION'
python access/secrets/separation/check_separation.py $S/incomplete-record/access-inputs.yaml $S/incomplete-record/rotator-hostroot.yaml | grep -cE '^RECORD-INCOMPLETE'
python -c "import yaml;print('REAL-STATE %s' % yaml.safe_load(open('access/secrets/separation/separation.result.yaml'))['state'])"
echo "L5-02-11 SELF-VERIFY PASS"
```

Expected output, exactly (`REAL-STATE` is `<varies>` between the two resolved values, `separated` or
`accepted-risk`; `UNRESOLVED` never appears here because it fires the STOP rule instead):

```
SEPARATION separated
SEPARATION UNRESOLVED no accepted-risk record at /tmp/none.yaml
SEPARATION accepted-risk holder=person-c review=2026-06-30
6
REAL-STATE <varies>
L5-02-11 SELF-VERIFY PASS
```

### STOP rule

STOP — do not commit, do not push, file the blocker of Section 4 — if any of these hold:

* The real contract yields `SEPARATION UNRESOLVED`. A rotator is also the host-root holder and no accepted
  risk is recorded. **Do not write the record, do not reassign the rotator, do not pick a different
  person.** §40.3 permits the concentration and forbids leaving it unstated; naming the holder, the
  compensating control and the review date is a Founder-level decision. Class `needs-decision`; the
  decision needed from L0 is "supply `contracts/access/accepted-risks/rotator-hostroot.yaml` in the shape
  of `access/secrets/separation/accepted-risk.template.yaml`, or reassign the rotator in the contract".
* The record L0 supplied is incomplete. Class `needs-decision`; paste the `RECORD-INCOMPLETE` lines.
* Any fixture result differs from the expected block. Class `shape-mismatch`.

---

## L5-02-12 — The API-key-free check: onboarding and quarterly

| Field | Value |
|---|---|
| Task id | `L5-02-12` |
| Size | M |
| Depends on | `L5-02-01` |
| Slug | `no-api-keys` |
| Subsystem | K (AI runtime contract enforcement) |
| Spec | §40.2 line 3691; §36.6 line 3235; §98.2 Phase 1 line 9015; invariant 84 line 9564; invariant 80 line 9557 |
| Writes | `access/secrets/checks/no_api_keys.py`, `access/secrets/checks/no-api-keys.sh`, `access/secrets/checks/no-api-keys.schedule.yaml`, `access/secrets/checks/no-api-keys.record.template.yaml`, `access/secrets/testdata/no-api-keys/clean/profile.sh`, `access/secrets/testdata/no-api-keys/clean/repo/.env`, `access/secrets/testdata/no-api-keys/dirty/profile.sh`, `access/secrets/testdata/no-api-keys/dirty/repo/.env` |

### Purpose

§40.2 line 3691 is a one-line rule with three surfaces: *"`env | grep -i api_key` must return empty. Shell
profiles and repository `.env` files are checked during onboarding and re-checked quarterly."* §36.6
restates it for the AI toolchain and gives the reason it is not merely hygiene: *"Some AI tools silently
prefer an API key over subscription authentication when one is present, producing metered billing with no
warning — this check protects the fixed-cost rule of Section 35 as well as the credential boundary."*
§98.2 Phase 1 line 9015 makes it a Foundation-week verification. Invariant 84 makes it permanent.

Three probes, one per surface:

| Probe | Surface | Source |
|---|---|---|
| `P1` | the live process environment | `env \| grep -i api_key` |
| `P2` | every shell profile named in the contract | "Shell profiles … are checked" |
| `P3` | every `.env`, `.env.*` and `*.env` file under the scan root | "repository `.env` files" |

**The check prints names, never values.** A finding names the variable and the file it lives in; the value
is never read into the output, because a check that leaks the credential it found has moved the credential
to a fourth place.

**It fails closed.** A profile path the contract names, which exists but cannot be read, is exit 2. A check
that quietly skips what it cannot read reports clean and is not.

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-no-api-keys
mkdir -p access/secrets/checks \
         access/secrets/testdata/no-api-keys/clean/repo \
         access/secrets/testdata/no-api-keys/dirty/repo
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/checks/no_api_keys.py <<'PYEOF'
#!/usr/bin/env python3
"""The API-key-free check.

Section 40.2 line 3691: "No API keys in developer environments. env | grep -i
api_key must return empty. Shell profiles and repository .env files are checked
during onboarding and re-checked quarterly."
Section 36.6 line 3235 restates it for the AI toolchain: some tools silently
prefer an API key over subscription authentication when one is present,
producing metered billing with no warning.
Section 98.2 Phase 1 line 9015 makes it a Foundation-week verification.
Invariant 84: API keys remain absent from developer environments.

Probes:
  P1 the live process environment
  P2 every shell profile path given with --profiles
  P3 every .env, .env.* and *.env file under --scan-root

Findings name the VARIABLE and the FILE. They never print the value.

Fail-closed (invariant 80): a named profile that exists but cannot be read is
exit 2. Skipping it would report clean.

Usage:
  no_api_keys.py [--profiles a,b,c] [--scan-root DIR] [--skip-env]

--skip-env exists only so the fixtures are deterministic on any machine. The
scheduled run never passes it; no-api-keys.schedule.yaml says so.

Exit 0 clean, 1 one or more findings, 2 input fault.
"""
import os
import sys

NEEDLE = "api_key"
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def option(argv, name, default=None):
    if name in argv:
        idx = argv.index(name)
        if idx + 1 < len(argv):
            return argv[idx + 1]
    return default


def names_in_text(body):
    hits = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        name = line.split("=", 1)[0].strip()
        if NEEDLE in name.lower():
            hits.append(name)
    return hits


def env_files(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            if filename == ".env" or filename.startswith(".env.") \
               or filename.endswith(".env"):
                found.append(os.path.join(dirpath, filename))
    return sorted(found)


def main(argv):
    profiles = [p for p in (option(argv, "--profiles", "") or "").split(",") if p]
    scan_root = option(argv, "--scan-root", ".")
    skip_env = "--skip-env" in argv

    findings = []
    p1 = 0
    if not skip_env:
        for name in sorted(os.environ):
            if NEEDLE in name.lower():
                findings.append("FINDING P1 %s present in the process environment" % name)
                p1 += 1

    p2 = 0
    for path in profiles:
        if not os.path.exists(path):
            print("PROFILE-ABSENT %s" % path)
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                body = handle.read()
        except Exception as exc:                                # fail closed
            print("RESULT FAIL profile-unreadable %s (%s)" % (path, exc))
            return 2
        for name in names_in_text(body):
            findings.append("FINDING P2 %s assigned in %s" % (name, path))
            p2 += 1

    p3 = 0
    for path in env_files(scan_root):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                body = handle.read()
        except Exception as exc:                                # fail closed
            print("RESULT FAIL env-file-unreadable %s (%s)" % (path, exc))
            return 2
        for name in names_in_text(body):
            findings.append("FINDING P3 %s assigned in %s" % (name, path))
            p3 += 1

    for line in findings:
        print(line)
    print("PROBE P1 %d" % p1)
    print("PROBE P2 %d" % p2)
    print("PROBE P3 %d" % p3)
    print("FINDINGS %d" % len(findings))
    if findings:
        print("INVARIANT 84 BREACHED")
        print("RESULT FAIL")
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
PYEOF
chmod +x access/secrets/checks/no_api_keys.py

cat > access/secrets/checks/no-api-keys.sh <<'SHEOF'
#!/usr/bin/env bash
# access/secrets/checks/no-api-keys.sh
# The onboarding and quarterly run (Section 40.2 line 3691, Section 36.6,
# Section 98.2 Phase 1 line 9015, invariant 84).
# Profile paths come from the contract; this wrapper never hard-codes one.
#   exit 0  clean
#   exit 1  an API key is present somewhere it must not be
#   exit 2  a named profile could not be read - FAIL CLOSED
set -eu
PROFILES=$(python -c "import yaml;c=yaml.safe_load(open('contracts/access/access-inputs.yaml',encoding='utf-8'));print(','.join(((c.get('checks') or {}).get('api_key_free') or {}).get('shell_profile_paths') or []))")
python access/secrets/checks/no_api_keys.py --profiles "$PROFILES" --scan-root "${1:-.}"
SHEOF
chmod +x access/secrets/checks/no-api-keys.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python - <<'PYEOF'
import yaml

contract = yaml.safe_load(open('contracts/access/access-inputs.yaml', encoding='utf-8')) or {}
block = ((contract.get('checks') or {}).get('api_key_free') or {})
owner = str(block.get('owner') or '').strip()
paths = block.get('shell_profile_paths') or []
assert owner, "STOP L5-02-12: contracts checks.api_key_free.owner is empty"
assert paths, "STOP L5-02-12: contracts checks.api_key_free.shell_profile_paths is empty"

lines = [
    "# access/secrets/checks/no-api-keys.schedule.yaml",
    "# Generated from contracts/access/access-inputs.yaml. Do not hand-edit.",
    "# Section 40.2 line 3691; Section 36.6 line 3235; Section 98.2 Phase 1 line 9015.",
    "schema_version: 1",
    "control_id: no-api-keys",
    'statement: "env | grep -i api_key must return empty"',
    "surfaces:",
    '  - "the live process environment"',
    '  - "shell profiles"',
    '  - "repository .env files"',
    "runs_at:",
    "  - trigger: onboarding",
    '    source: "Section 40.2 line 3691; Section 98.2 Phase 1 line 9015"',
    "  - trigger: quarterly",
    '    source: "Section 40.2 line 3691 - re-checked quarterly"',
    'owner: "%s"' % owner,
    "shell_profile_paths:",
]
for path in paths:
    lines.append('  - "%s"' % path)
lines += [
    "invariant: 84",
    'also_protects: "the fixed-cost rule of Section 35 - some AI tools silently prefer an API key over subscription authentication when one is present, producing metered billing with no warning (Section 40.2, Section 36.6)"',
    "classification: fail-closed",
    'scheduled_run_flags: "none - the scheduled run never passes --skip-env"',
    'implemented_by: "access/secrets/checks/no-api-keys.sh"',
    'record_template: "access/secrets/checks/no-api-keys.record.template.yaml"',
    'estate_note: "No vendor API keys exist anywhere in the estate (Section 36.6). A Hermes instance credential is a self-minted control-plane token held in the fifth secrets tier, not a vendor API key."',
]
open('access/secrets/checks/no-api-keys.schedule.yaml', 'w',
     encoding='utf-8', newline='\n').write("\n".join(lines) + "\n")
print("WROTE access/secrets/checks/no-api-keys.schedule.yaml owner=%s profiles=%d"
      % (owner, len(paths)))
PYEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/checks/no-api-keys.record.template.yaml <<'YAMLEOF'
# access/secrets/checks/no-api-keys.record.template.yaml
# One record per execution - at onboarding, and quarterly thereafter.
# It records the RESULT. It never records a value that was found.
schema_version: 1
run_id: ""
trigger: ""              # onboarding | quarterly
machine: ""              # the machine checked
operator: ""             # who ran it
ran_at: ""               # UTC stamp
probes:
  p1_process_environment: ""   # pass | fail
  p2_shell_profiles: ""        # pass | fail
  p3_repository_env_files: ""  # pass | fail
findings: 0
finding_names: []        # VARIABLE NAMES ONLY - never values
result: ""               # pass | fail
YAMLEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
N=access/secrets/testdata/no-api-keys
cat > $N/clean/profile.sh <<'SHEOF'
# POSITIVE FIXTURE - a shell profile with no API key in it.
export EDITOR=vi
export PATH="$HOME/bin:$PATH"
export CONTROL_PLANE_ROOT=/c/D_Drive/PS/MultiProduct/control-plane
SHEOF

cat > $N/clean/repo/.env <<'ENVEOF'
# POSITIVE FIXTURE - a repository .env with no API key in it.
DATABASE_URL=postgres://localhost/dev
LOG_LEVEL=debug
ENVEOF

cat > $N/dirty/profile.sh <<'SHEOF'
# NEGATIVE FIXTURE - a shell profile carrying a vendor API key.
# The value is the literal string below; this fixture carries no credential.
export EDITOR=vi
export EXAMPLE_VENDOR_API_KEY=fixture-not-a-real-value
SHEOF

cat > $N/dirty/repo/.env <<'ENVEOF'
# NEGATIVE FIXTURE - a repository .env carrying a vendor API key.
DATABASE_URL=postgres://localhost/dev
OTHER_VENDOR_API_KEY=fixture-not-a-real-value
ENVEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/secrets/checks access/secrets/testdata/no-api-keys
git commit -m "L5-02-12: the API-key-free check, onboarding and quarterly (Section 40.2, Section 36.6, invariant 84)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-no-api-keys
gh pr create --base integration \
  --title "L5-02-12 The API-key-free check — onboarding and quarterly" \
  --body "Lane 5, Phase 2, task L5-02-12. Spec: Section 40.2 line 3691, Section 36.6 line 3235, Section 98.2 Phase 1 line 9015, invariant 84. Paths: access/secrets/checks/**, access/secrets/testdata/no-api-keys/**. Self-verify output pasted below."
```

### Acceptance criteria

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | The clean fixture passes | `python access/secrets/checks/no_api_keys.py --profiles access/secrets/testdata/no-api-keys/clean/profile.sh --scan-root access/secrets/testdata/no-api-keys/clean --skip-env \| tail -1` | `RESULT PASS` |
| 2 | The dirty profile is detected | `python access/secrets/checks/no_api_keys.py --profiles access/secrets/testdata/no-api-keys/dirty/profile.sh --scan-root access/secrets/testdata/no-api-keys/dirty --skip-env \| grep -c '^FINDING P2'` | `1` |
| 3 | The dirty `.env` is detected | `python access/secrets/checks/no_api_keys.py --profiles access/secrets/testdata/no-api-keys/dirty/profile.sh --scan-root access/secrets/testdata/no-api-keys/dirty --skip-env \| grep -c '^FINDING P3'` | `1` |
| 4 | It exits 1 on a finding | `python access/secrets/checks/no_api_keys.py --profiles access/secrets/testdata/no-api-keys/dirty/profile.sh --scan-root access/secrets/testdata/no-api-keys/dirty --skip-env >/dev/null; echo $?` | `1` |
| 5 | A finding names the invariant | `python access/secrets/checks/no_api_keys.py --profiles access/secrets/testdata/no-api-keys/dirty/profile.sh --scan-root access/secrets/testdata/no-api-keys/dirty --skip-env \| grep '^INVARIANT'` | `INVARIANT 84 BREACHED` |
| 6 | No value is ever printed | `python access/secrets/checks/no_api_keys.py --profiles access/secrets/testdata/no-api-keys/dirty/profile.sh --scan-root access/secrets/testdata/no-api-keys/dirty --skip-env \| grep -c 'fixture-not-a-real-value'` | `0` |
| 7 | The schedule declares both triggers | `python -c "import yaml;print([r['trigger'] for r in yaml.safe_load(open('access/secrets/checks/no-api-keys.schedule.yaml'))['runs_at']])"` | `['onboarding', 'quarterly']` |
| 8 | The schedule names an owner | `python -c "import yaml;print(bool(yaml.safe_load(open('access/secrets/checks/no-api-keys.schedule.yaml'))['owner'].strip()))"` | `True` |
| 9 | The schedule names invariant 84 | `python -c "import yaml;print(yaml.safe_load(open('access/secrets/checks/no-api-keys.schedule.yaml'))['invariant'])"` | `84` |
| 10 | The scheduled run does not skip the environment probe | `python -c "import yaml;print(yaml.safe_load(open('access/secrets/checks/no-api-keys.schedule.yaml'))['scheduled_run_flags'])"` | `none - the scheduled run never passes --skip-env` |
| 11 | The real repository is clean | `bash access/secrets/checks/no-api-keys.sh access/model \| tail -1` | `RESULT PASS` |
| 12 | The record template records names, not values | `python -c "import yaml;print(yaml.safe_load(open('access/secrets/checks/no-api-keys.record.template.yaml'))['finding_names'])"` | `[]` |
| 13 | No file outside `access/secrets/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/secrets/'` | `0` |

Criterion 11 scans `access/model` rather than the whole tree, because the negative fixtures of this task
live under `access/secrets/testdata/` by design and would be found by a whole-tree scan. The whole-tree
run belongs to the machine being onboarded, not to this repository check.

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
N=access/secrets/testdata/no-api-keys
python access/secrets/checks/no_api_keys.py --profiles $N/clean/profile.sh --scan-root $N/clean --skip-env | grep -E '^(PROBE|FINDINGS|RESULT)'
python access/secrets/checks/no_api_keys.py --profiles $N/dirty/profile.sh --scan-root $N/dirty --skip-env | grep -E '^(PROBE|FINDINGS|INVARIANT|RESULT)'
python access/secrets/checks/no_api_keys.py --profiles $N/dirty/profile.sh --scan-root $N/dirty --skip-env | grep -c 'fixture-not-a-real-value'
python -c "import yaml;d=yaml.safe_load(open('access/secrets/checks/no-api-keys.schedule.yaml'));print('TRIGGERS',','.join(r['trigger'] for r in d['runs_at']),'INVARIANT',d['invariant'],'OWNER',('set' if d['owner'].strip() else 'MISSING'))"
echo "L5-02-12 SELF-VERIFY PASS"
```

Expected output, exactly:

```
PROBE P1 0
PROBE P2 0
PROBE P3 0
FINDINGS 0
RESULT PASS
PROBE P1 0
PROBE P2 1
PROBE P3 1
FINDINGS 2
INVARIANT 84 BREACHED
RESULT FAIL
0
TRIGGERS onboarding,quarterly INVARIANT 84 OWNER set
L5-02-12 SELF-VERIFY PASS
```

### STOP rule

STOP — do not commit, do not push, file the blocker of Section 4 — if any of these hold:

* The generating block asserts: `contracts/access/access-inputs.yaml` names no `checks.api_key_free.owner`
  or no `shell_profile_paths`. **Do not name an owner and do not guess a profile path.** Class
  `missing-contract`.
* Criterion 6 returns anything but `0`. A check that prints the key it found has moved the key. Class
  `shape-mismatch`.
* A real machine's run reports `INVARIANT 84 BREACHED`. That is a live finding, not a task failure: remove
  the key from the profile, re-authenticate the tool by subscription, and re-run. If the tool cannot work
  without an API key, that is a §35 fixed-cost decision for L0 — class `needs-decision`.

---

## L5-02-13 — Workstation-compromise containment hook (§43.4)

| Field | Value |
|---|---|
| Task id | `L5-02-13` |
| Size | S |
| Depends on | `L5-02-07`, `L5-02-12` |
| Slug | `containment` |
| Subsystem | L |
| Spec | §43.4 lines 3928–3931; §43.1 lines 3853–3870; §40.3 lines 3695–3704; §36.3 (the approved extension and MCP-server list) |
| Writes | `access/secrets/incident/workstation-compromise.md`, `access/secrets/incident/containment-checklist.yaml`, `access/secrets/incident/check_containment.py`, `access/secrets/incident/check-containment.sh` |

### Purpose

§43.4 makes one step explicit precisely because it is the step a generic checklist loses: *"compromise of a
workstation holding DevOps access triggers rotation of **every** fifth-tier machine credential as a named
step, not as an inference from the generic 'rotate every credential they could reach'."*

So the checklist names all five credentials, and `check_containment.py` compares that list against the
directory of fifth-tier entries. If a sixth credential is ever added, the containment checklist fails until
it is added there too. That is the whole point: the enumeration must not be able to fall behind silently.

§43.1 fixes the order. Containment comes before investigating; evidence preservation comes before
remediating; and rotation comes after evidence capture — *"Do not delete. Do not force-push. Do not rotate
before capturing."* The checklist's step numbers encode that order and the checker asserts it.

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-containment
mkdir -p access/secrets/incident
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/incident/workstation-compromise.md <<'MDEOF'
# Containment: compromised engineering workstation

Section 43.4 lines 3928-3931, on the Section 43.1 flow. Malicious intent is not
assumed - the overwhelmingly likely cause is a phished credential or a
compromised device, and the mechanism is identical either way.

Order is not negotiable (Section 43.1):
DETECT -> CLASSIFY -> CONTAIN -> PRESERVE EVIDENCE -> ROTATE CREDENTIALS.

C-01 CONTAIN the person account: set access_status: suspended. One revocation
path, exercised for more than one reason.

C-02 CONTAIN the host reachability. Revoke EVERY cached session, SSH key and
private-path credential reaching the operations VM from that workstation.
Section 43.4 names the operations VM explicitly, because the second trust
boundary of Section 40.3 is what bounds this blast radius.

C-03 PRESERVE EVIDENCE before remediating: logs, audit records, artifact
digests, access history. Do not delete. Do not force-push. Do not rotate before
capturing. Rotation destroys the authentication trail you are about to need.

C-04 ROTATE EVERY FIFTH-TIER MACHINE CREDENTIAL - a named step, not an
inference. If the workstation held DevOps access, all five rotate:
reconciler, provisioning-cli, organisation-export-token, records-writer,
layer-b-backup. Each rotation runs the one-page runbook at
access/secrets/runbooks/rotate-fifth-tier-credential.md and is not done until
access/secrets/checks/rotation-complete.sh permits it - clean reconciliation,
AT-110 re-executed, re-escrow confirmed.

C-05 RE-REVIEW any change authored from that machine in the suspected window.

C-06 RE-RUN the API-key-free check on the rebuilt machine before it is used
again: bash access/secrets/checks/no-api-keys.sh

C-07 REVIEW the approved extension and MCP-server list of Section 36.3. It
exists precisely to keep this blast radius from silently growing; a compromise
is when it gets read, not when it gets written.

What this incident does NOT reach, and why that is a designed property rather
than luck: production (boundary 1, Section 40.3 line 3697) and - once C-02 and
C-04 complete - the control-plane machine-credential store (boundary 2, Section
40.3 line 3701, D95).
MDEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/incident/containment-checklist.yaml <<'YAMLEOF'
# access/secrets/incident/containment-checklist.yaml
# Section 43.4 lines 3928-3931 on the Section 43.1 flow.
schema_version: 1
incident_type: compromised-workstation
flow: "DETECT -> CLASSIFY -> CONTAIN -> PRESERVE EVIDENCE -> ROTATE CREDENTIALS"
flow_source: "Section 43.1 lines 3853-3870"
malicious_intent_assumed: false
steps:
  - id: C-01
    order: 1
    phase: contain
    action: "Suspend the person account (access_status: suspended)"
  - id: C-02
    order: 2
    phase: contain
    action: "Revoke every cached session, SSH key and private-path credential reaching the operations VM"
    named_in_spec: true
  - id: C-03
    order: 3
    phase: preserve-evidence
    action: "Capture logs, audit records, artifact digests and access history. Do not delete. Do not force-push. Do not rotate before capturing"
  - id: C-04
    order: 4
    phase: rotate
    action: "Rotate EVERY fifth-tier machine credential"
    named_step: true
    inferred_from_generic_rule: false
    spec_quote: "compromise of a workstation holding DevOps access triggers rotation of every fifth-tier machine credential as a named step, not as an inference from the generic rotate every credential they could reach"
    credentials:
      - reconciler
      - provisioning-cli
      - organisation-export-token
      - records-writer
      - layer-b-backup
    runbook: "access/secrets/runbooks/rotate-fifth-tier-credential.md"
    completion_gate: "access/secrets/checks/rotation-complete.sh"
  - id: C-05
    order: 5
    phase: remediate
    action: "Re-review any change authored from that machine in the suspected window"
  - id: C-06
    order: 6
    phase: remediate
    action: "Re-run the API-key-free check on the rebuilt machine"
    check: "access/secrets/checks/no-api-keys.sh"
  - id: C-07
    order: 7
    phase: remediate
    action: "Review the approved extension and MCP-server list (Section 36.3)"
bounded_by:
  - boundary-1-production
  - boundary-2-control-plane
YAMLEOF
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/incident/check_containment.py <<'PYEOF'
#!/usr/bin/env python3
"""Prove the Section 43.4 containment hook cannot fall behind.

Three assertions:
  K1 the C-04 credential list is EXACTLY the set of fifth-tier entries on disk
  K2 C-04 is a named step, not an inference (Section 43.4)
  K3 evidence preservation precedes rotation (Section 43.1)

K1 is the one that matters over time: add a sixth fifth-tier credential and
this check fails until the containment checklist names it too.

Fail-closed (invariant 80): a missing checklist or an empty fifth-tier
directory is exit 2.

Usage: check_containment.py [<checklist.yaml> [<fifth-tier-dir>]]
"""
import glob
import os
import sys

import yaml


def main(argv):
    checklist = argv[1] if len(argv) > 1 else os.path.join(
        "access", "secrets", "incident", "containment-checklist.yaml")
    fifth = argv[2] if len(argv) > 2 else os.path.join(
        "access", "secrets", "fifth-tier")
    if not os.path.isfile(checklist):
        print("RESULT FAIL checklist-unreadable %s" % checklist)
        return 2
    try:
        with open(checklist, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
    except Exception as exc:                                    # fail closed
        print("RESULT FAIL checklist-unparseable %s" % exc)
        return 2
    steps = {str(s.get("id")): s for s in (doc.get("steps") or [])}
    rotate = steps.get("C-04")
    if rotate is None:
        print("RESULT FAIL no-C-04-rotation-step")
        return 2
    entries = sorted(os.path.basename(p)[:-5]
                     for p in glob.glob(os.path.join(fifth, "*.yaml")))
    if not entries:
        print("RESULT FAIL no-fifth-tier-entries %s" % fifth)
        return 2

    failed = 0
    listed = sorted(str(c) for c in (rotate.get("credentials") or []))
    if listed == entries:
        print("ASSERTION K1 OK %d credentials enumerated" % len(entries))
    else:
        print("ASSERTION K1 FAIL checklist=%r fifth-tier=%r" % (listed, entries))
        failed += 1

    if rotate.get("named_step") is True \
       and rotate.get("inferred_from_generic_rule") is False:
        print("ASSERTION K2 OK named-step-not-inference")
    else:
        print("ASSERTION K2 FAIL C-04 is not declared a named step")
        failed += 1

    preserve = [s for s in steps.values() if s.get("phase") == "preserve-evidence"]
    if preserve and min(int(s["order"]) for s in preserve) < int(rotate["order"]):
        print("ASSERTION K3 OK evidence-precedes-rotation")
    else:
        print("ASSERTION K3 FAIL rotation is ordered before evidence capture")
        failed += 1

    print("FAILED %d" % failed)
    if failed:
        print("RESULT FAIL")
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
PYEOF
chmod +x access/secrets/incident/check_containment.py

cat > access/secrets/incident/check-containment.sh <<'SHEOF'
#!/usr/bin/env bash
# access/secrets/incident/check-containment.sh
# Section 43.4: the containment hook must name every fifth-tier credential.
#   exit 0  the enumeration is complete and correctly ordered
#   exit 1  an assertion fails
#   exit 2  input fault - FAIL CLOSED
set -eu
python access/secrets/incident/check_containment.py "$@"
SHEOF
chmod +x access/secrets/incident/check-containment.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/secrets/incident
git commit -m "L5-02-13: workstation-compromise containment hook, rotation of every fifth-tier credential as a named step (Section 43.4)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-containment
gh pr create --base integration \
  --title "L5-02-13 Workstation-compromise containment hook (Section 43.4)" \
  --body "Lane 5, Phase 2, task L5-02-13. Spec: Section 43.4 lines 3928-3931, Section 43.1 lines 3853-3870, Section 40.3, Section 36.3. Paths: access/secrets/incident/**. Self-verify output pasted below."
```

### Acceptance criteria

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | The checker passes | `bash access/secrets/incident/check-containment.sh \| tail -1` | `RESULT PASS` |
| 2 | C-04 enumerates all five credentials | `python -c "import yaml;d=yaml.safe_load(open('access/secrets/incident/containment-checklist.yaml'));print(len([s for s in d['steps'] if s['id']=='C-04'][0]['credentials']))"` | `5` |
| 3 | C-04 is a named step, not an inference | `python -c "import yaml;d=yaml.safe_load(open('access/secrets/incident/containment-checklist.yaml'));s=[x for x in d['steps'] if x['id']=='C-04'][0];print(s['named_step'],s['inferred_from_generic_rule'])"` | `True False` |
| 4 | Evidence capture precedes rotation | `bash access/secrets/incident/check-containment.sh \| grep -c '^ASSERTION K3 OK'` | `1` |
| 5 | The enumeration cannot fall behind | `mkdir -p /tmp/f6 && cp access/secrets/fifth-tier/*.yaml /tmp/f6/ && cp access/secrets/fifth-tier/reconciler.yaml /tmp/f6/sixth-credential.yaml && bash access/secrets/incident/check-containment.sh access/secrets/incident/containment-checklist.yaml /tmp/f6 \| grep -c '^ASSERTION K1 FAIL'` | `1` |
| 6 | …and that case exits 1 | `bash access/secrets/incident/check-containment.sh access/secrets/incident/containment-checklist.yaml /tmp/f6 >/dev/null; echo $?` | `1` |
| 7 | The runbook is named as the rotation procedure | `python -c "import yaml;d=yaml.safe_load(open('access/secrets/incident/containment-checklist.yaml'));print([s for s in d['steps'] if s['id']=='C-04'][0]['runbook'])"` | `access/secrets/runbooks/rotate-fifth-tier-credential.md` |
| 8 | The operations VM is named in containment, not inferred | `grep -c 'operations VM' access/secrets/incident/workstation-compromise.md` | `2` |
| 9 | The §43.1 ordering sentence is quoted | `grep -c 'Do not rotate before capturing' access/secrets/incident/workstation-compromise.md` | `1` |
| 10 | The checker fails closed on a missing checklist | `bash access/secrets/incident/check-containment.sh /tmp/no-such.yaml >/dev/null 2>&1; echo $?` | `2` |
| 11 | No file outside `access/secrets/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/secrets/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash access/secrets/incident/check-containment.sh
mkdir -p /tmp/f6 && cp access/secrets/fifth-tier/*.yaml /tmp/f6/ \
  && cp access/secrets/fifth-tier/reconciler.yaml /tmp/f6/sixth-credential.yaml
bash access/secrets/incident/check-containment.sh access/secrets/incident/containment-checklist.yaml /tmp/f6 | grep -E '^(ASSERTION K1|RESULT)'
echo "L5-02-13 SELF-VERIFY PASS"
```

Expected output, exactly:

```
ASSERTION K1 OK 5 credentials enumerated
ASSERTION K2 OK named-step-not-inference
ASSERTION K3 OK evidence-precedes-rotation
FAILED 0
RESULT PASS
ASSERTION K1 FAIL checklist=['layer-b-backup', 'organisation-export-token', 'provisioning-cli', 'reconciler', 'records-writer'] fifth-tier=['layer-b-backup', 'organisation-export-token', 'provisioning-cli', 'reconciler', 'records-writer', 'sixth-credential']
RESULT FAIL
L5-02-13 SELF-VERIFY PASS
```

### STOP rule

STOP — do not commit, do not push, file the blocker of Section 4 — if any of these hold:

* `ASSERTION K1` fails against the real fifth-tier directory. Either an entry is missing from the
  checklist or one was added to `access/secrets/fifth-tier/` outside this phase. Class `shape-mismatch`.
* `ASSERTION K3` fails. Rotation ordered before evidence capture destroys the authentication trail the
  incident needs — §43.1 forbids it in as many words. Class `shape-mismatch`.
* The executor wants to shorten C-04 to "rotate anything they could reach". That is precisely the generic
  inference §43.4 replaced with a named step. Class `needs-decision`.

---

## L5-02-14 — Phase 2 exit gate: one command runs every check

| Field | Value |
|---|---|
| Task id | `L5-02-14` |
| Size | M |
| Depends on | `L5-02-03`, `L5-02-06`, `L5-02-08`, `L5-02-10`, `L5-02-11`, `L5-02-12`, `L5-02-13` |
| Slug | `exit-gate` |
| Subsystem | L, K |
| Spec | §64.2 lines 5448–5468; invariant 80 line 9557; §40.1 lines 3644–3686; §40.3 lines 3695–3704; AT-110 lines 9438–9439 |
| Writes | `access/fail-closed/secret-tier-downward-move.yaml`, `access/fail-closed/fifth-tier-envelope-evaluator.yaml`, `access/fail-closed/rotation-completion-gate.yaml`, `access/fail-closed/workstation-trust-boundaries.yaml`, `access/fail-closed/no-api-keys.yaml`, `access/fail-closed/workstation-compromise-containment.yaml`, `access/secrets/tools/publish_secret_tiers.py`, `access/published/secret-tiers.v1.json`, `access/secrets/gate/phase2-gate.sh`, `access/secrets/gate/phase2.gate.json` |

### Purpose

Three jobs, one task:

1. **Classify every control this phase produced.** §64.2 and invariant 80 require every control to be
   explicitly classified fail-closed or fail-open. Six controls, six files, one per control — never one
   register file (PARTITION rule 3).
2. **Publish `access/published/secret-tiers.v1.json`.** The charter names this artifact as the one AT-110
   executes against and as the artifact Lane 3 reads to know which tier a credential lives in. It is
   generated, byte-reproducible, and never hand-edited.
3. **Ship one command that runs everything.** A phase whose checks must be remembered individually is a
   phase that will be half-run.

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p2-exit-gate
mkdir -p access/fail-closed access/published access/secrets/gate access/secrets/tools
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
write_fc () {  # write_fc <file> <control_id> <title> <implemented_by> <closed_means> <spec>
cat > "access/fail-closed/$1" <<YAMLEOF
# access/fail-closed/$1
# Section 64.2 lines 5448-5468; invariant 80: every control is explicitly
# classified fail-closed or fail-open. One file per control (PARTITION rule 3).
schema_version: 1
control_id: $2
title: "$3"
classification: fail-closed
implemented_by: "$4"
closed_means: "$5"
on_input_unreadable: fail
on_check_error: fail
spec_anchor: "$6"
phase: L5-P2
YAMLEOF
}

write_fc secret-tier-downward-move.yaml secret-tier-downward-move \
  "A secret never moves down a tier" \
  "access/secrets/checks/check-no-downward-move.sh" \
  "an unreadable contract or env file reports FAIL, never PASS; a finding is a security incident under Section 43" \
  "Section 40.1 line 3656"

write_fc fifth-tier-envelope-evaluator.yaml fifth-tier-envelope-evaluator \
  "A run outside the behavioural envelope is Blocking" \
  "access/secrets/envelope/check-envelope.sh" \
  "an unreadable envelope, an unreadable run record or an empty run directory reports FAIL, never PASS" \
  "Section 40.1 line 3685, D96"

write_fc rotation-completion-gate.yaml rotation-completion-gate \
  "A rotation is not done until reconciliation is clean, AT-110 is re-executed and re-escrow is confirmed" \
  "access/secrets/checks/rotation-complete.sh" \
  "a missing or malformed rotation record reports ROTATION-NOT-DONE, never permitted" \
  "Section 40.1 line 3683, Section 14.4 line 1266, AT-110"

write_fc workstation-trust-boundaries.yaml workstation-trust-boundaries \
  "The two Section 40.3 trust boundaries hold" \
  "access/secrets/boundaries/check-boundaries.sh; access/secrets/host/check-credential-store.sh; infra/network/check-shell-gate.sh" \
  "a missing boundary declaration, an unreachable host or an uninspectable sshd reports FAIL, never PASS" \
  "Section 40.3 lines 3695-3704, D95"

write_fc no-api-keys.yaml no-api-keys \
  "API keys remain absent from developer environments" \
  "access/secrets/checks/no-api-keys.sh" \
  "a named shell profile that exists and cannot be read reports FAIL, never PASS" \
  "Section 40.2 line 3691, Section 36.6 line 3235, invariant 84"

write_fc workstation-compromise-containment.yaml workstation-compromise-containment \
  "Compromise of a workstation holding DevOps access rotates every fifth-tier credential" \
  "access/secrets/incident/check-containment.sh" \
  "a missing checklist or an unenumerated credential reports FAIL, never PASS" \
  "Section 43.4 lines 3928-3931"
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/tools/publish_secret_tiers.py <<'PYEOF'
#!/usr/bin/env python3
"""Publish access/published/secret-tiers.v1.json.

Charter L5-00 Section 7: this is the artifact Lane 3 reads to know which tier a
credential lives in, and the one AT-110 executes the published permission set
against (Section 40.1 lines 3644-3686; Section 40.3 lines 3695-3704).

Deterministic by construction: sorted keys, two-space indent, LF newlines, no
timestamp. Re-running it must produce no diff - that is what makes publication
byte-reproducible.

Usage: publish_secret_tiers.py [--check]
--check verifies the file on disk equals what would be generated, and writes
nothing.
"""
import glob
import json
import os
import sys

import yaml

OUT = os.path.join("access", "published", "secret-tiers.v1.json")


def read_all(pattern):
    docs = []
    for path in sorted(glob.glob(pattern)):
        with open(path, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        docs.append(doc)
    return docs


def build():
    tiers = read_all(os.path.join("access", "secrets", "tiers", "*.yaml"))
    creds = read_all(os.path.join("access", "secrets", "fifth-tier", "*.yaml"))
    envelopes = {}
    for env in read_all(os.path.join("access", "secrets", "envelope", "*.envelope.yaml")):
        envelopes[env["credential_id"]] = env
    payload = {
        "artifact": "secret-tiers",
        "version": 1,
        "spec_anchor": "Section 40.1 lines 3644-3686; Section 40.3 lines 3695-3704",
        "tiers": [
            {
                "tier_id": t["tier_id"],
                "rank": t["rank"],
                "tier": t["tier"],
                "location": t["location"],
                "contains": t["contains"],
                "holds_production_credentials": bool(t["holds_production_credentials"]),
            }
            for t in sorted(tiers, key=lambda d: d["rank"])
        ],
        "downward_move": {
            "permitted": False,
            "class": "security-incident",
            "authority": "Section 43 (Security Incident Workflow)",
            "is_cleanup_task": False,
        },
        "fifth_tier_credentials": [],
        "boundaries": [
            {
                "boundary_id": "boundary-1-production",
                "statement": "A fully compromised developer workstation must not yield production database access, production credentials, or the ability to deploy to production.",
            },
            {
                "boundary_id": "boundary-2-control-plane",
                "statement": "A fully compromised engineering workstation must not yield the control-plane machine-credential store.",
                "decision": "D95",
            },
        ],
        "at110": {
            "artifact_under_test": OUT,
            "attempts": 6,
            "all_must_fail": True,
            "re_executed_at_every_rotation": True,
        },
    }
    for cred in sorted(creds, key=lambda d: d["credential_id"]):
        cid = cred["credential_id"]
        env = envelopes.get(cid, {})
        payload["fifth_tier_credentials"].append({
            "credential_id": cid,
            "tier_id": cred["tier_id"],
            "rank": cred["rank"],
            "kind": cred["kind"],
            "kind_narrowed": bool(cred["kind_narrowed"]),
            "host": cred["host"],
            "rotation_cadence": cred["rotation_cadence"],
            "rotator": cred["rotator"],
            "runbook": cred["runbook"],
            "envelope_alert_owner": cred["envelope_alert_owner"],
            "permission_set": list(cred["permission_set"]),
            "reissue_source": cred["reissue_source"],
            "envelope": {
                "temporal_window_rule": env.get("temporal_window_rule"),
                "signed_run_record_required": (env.get("signed_run_record") or {}).get("required"),
                "run_count_ceiling_per_day": (env.get("run_count_ceiling_per_day") or {}).get("value"),
                "expected_source_host": (env.get("expected_source_host") or {}).get("value"),
                "published_api_call_counts": (env.get("published_api_call_counts") or {}).get("required"),
                "outside_envelope_class": env.get("outside_envelope_class"),
            },
        })
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main(argv):
    body = build()
    if "--check" in argv:
        if not os.path.isfile(OUT):
            print("RESULT FAIL published-artifact-absent %s" % OUT)
            return 2
        with open(OUT, "r", encoding="utf-8") as handle:
            current = handle.read()
        if current != body:
            print("RESULT FAIL published-artifact-stale %s" % OUT)
            return 1
        print("RESULT PASS reproducible")
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(body)
    print("WROTE %s" % OUT)
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
PYEOF
chmod +x access/secrets/tools/publish_secret_tiers.py
python access/secrets/tools/publish_secret_tiers.py
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > access/secrets/gate/phase2-gate.sh <<'SHEOF'
#!/usr/bin/env bash
# access/secrets/gate/phase2-gate.sh
# The L5 phase 2 exit gate. One command, every check this phase produced.
# Writes access/secrets/gate/phase2.gate.json - deterministic, no timestamp,
# so a re-run produces no diff.
#
#   exit 0  L5-P2 EXIT GATE PASS
#   exit 1  one or more gates failed
set -u
FAILURES=0
RESULTS=""

run () {  # run <id> <command...>
  id="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "GATE $id PASS"
    RESULTS="$RESULTS{\"id\":\"$id\",\"status\":\"pass\"},"
  else
    echo "GATE $id FAIL"
    RESULTS="$RESULTS{\"id\":\"$id\",\"status\":\"fail\"},"
    FAILURES=$((FAILURES + 1))
  fi
}

T=access/secrets/testdata
run G01-tier-registry        python access/secrets/tools/validate_tiers.py
run G02-downward-move        bash access/secrets/checks/check-no-downward-move.sh
run G03-fifth-tier-entries   python access/secrets/tools/emit_fifth_tier.py
run G04-envelopes            python access/secrets/tools/emit_envelopes.py
run G05-envelope-evaluator   python access/secrets/envelope/evaluate_envelope.py "$T/envelope/envelopes" "$T/envelope/runs-clean" "$T/envelope/triggers"
run G06-rotation-runbook     bash access/secrets/runbooks/check-runbook.sh
run G07-rotation-gate        bash access/secrets/checks/rotation-complete.sh "$T/rotation/complete.yaml"
run G08-boundaries           bash access/secrets/boundaries/check-boundaries.sh --phase complete
run G09-separation           bash access/secrets/separation/check-separation.sh
run G10-no-api-keys          python access/secrets/checks/no_api_keys.py --profiles "$T/no-api-keys/clean/profile.sh" --scan-root "$T/no-api-keys/clean" --skip-env
run G11-containment          bash access/secrets/incident/check-containment.sh
run G12-publication          python access/secrets/tools/publish_secret_tiers.py --check
run G13-generated-clean      git diff --exit-code -- access/secrets/fifth-tier access/secrets/envelope access/published

printf '{\n  "artifact": "l5-p2-exit-gate",\n  "gates": [%s],\n  "failures": %d\n}\n' \
  "${RESULTS%,}" "$FAILURES" > access/secrets/gate/phase2.gate.json

echo "GATE-FAILURES $FAILURES"
if [ "$FAILURES" -eq 0 ]; then
  echo "L5-P2 EXIT GATE PASS"
  exit 0
fi
echo "L5-P2 EXIT GATE FAIL"
exit 1
SHEOF
chmod +x access/secrets/gate/phase2-gate.sh
bash access/secrets/gate/phase2-gate.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add access/fail-closed access/published access/secrets/gate access/secrets/tools/publish_secret_tiers.py
git commit -m "L5-02-14: fail-closed register, published secret-tiers artifact and the phase 2 exit gate (Section 64.2, Section 40.1)"
git fetch origin
git rebase origin/integration
git push -u origin lane/5/p2-exit-gate
gh pr create --base integration \
  --title "L5-02-14 Phase 2 exit gate — one command runs every check" \
  --body "Lane 5, Phase 2, task L5-02-14. Spec: Section 64.2 lines 5448-5468, invariant 80, Section 40.1, Section 40.3, AT-110. Paths: access/fail-closed/**, access/published/secret-tiers.v1.json, access/secrets/gate/**, access/secrets/tools/publish_secret_tiers.py. Self-verify output pasted below."
```

### Acceptance criteria

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | Six controls are classified, one file each | `ls access/fail-closed/*.yaml \| wc -l` | `6` |
| 2 | Every one is fail-closed | `python -c "import glob,yaml;print(set(yaml.safe_load(open(f))['classification'] for f in glob.glob('access/fail-closed/*.yaml')))"` | `{'fail-closed'}` |
| 3 | Every one names what it does when it cannot read its input | `python -c "import glob,yaml;print(set(yaml.safe_load(open(f))['on_input_unreadable'] for f in glob.glob('access/fail-closed/*.yaml')))"` | `{'fail'}` |
| 4 | The published artifact lists five tiers | `python -c "import json;print(len(json.load(open('access/published/secret-tiers.v1.json'))['tiers']))"` | `5` |
| 5 | …and five fifth-tier credentials | `python -c "import json;print(len(json.load(open('access/published/secret-tiers.v1.json'))['fifth_tier_credentials']))"` | `5` |
| 6 | …and both boundary statements | `python -c "import json;print(len(json.load(open('access/published/secret-tiers.v1.json'))['boundaries']))"` | `2` |
| 7 | …and the AT-110 shape | `python -c "import json;d=json.load(open('access/published/secret-tiers.v1.json'))['at110'];print(d['attempts'],d['all_must_fail'],d['re_executed_at_every_rotation'])"` | `6 True True` |
| 8 | Publication is byte-reproducible | `python access/secrets/tools/publish_secret_tiers.py --check \| tail -1` | `RESULT PASS reproducible` |
| 9 | Every published credential carries a non-empty permission set | `python -c "import json;print(min(len(c['permission_set']) for c in json.load(open('access/published/secret-tiers.v1.json'))['fifth_tier_credentials'])>=1)"` | `True` |
| 10 | The gate runs thirteen checks | `bash access/secrets/gate/phase2-gate.sh \| grep -c '^GATE G'` | `13` |
| 11 | The gate passes | `bash access/secrets/gate/phase2-gate.sh \| tail -1` | `L5-P2 EXIT GATE PASS` |
| 12 | The gate artifact carries no timestamp | `grep -c -E '[0-9]{4}-[0-9]{2}-[0-9]{2}' access/secrets/gate/phase2.gate.json` | `0` |
| 13 | Re-running the gate produces no diff | `bash access/secrets/gate/phase2-gate.sh >/dev/null; git diff --exit-code -- access/secrets/gate/phase2.gate.json >/dev/null; echo $?` | `0` |
| 14 | No file outside `access/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash access/secrets/gate/phase2-gate.sh
python access/secrets/tools/publish_secret_tiers.py --check | tail -1
python -c "import glob,yaml;print('FAIL-CLOSED-CONTROLS %d' % len(glob.glob('access/fail-closed/*.yaml')))"
python -c "import json;d=json.load(open('access/published/secret-tiers.v1.json'));print('PUBLISHED tiers=%d creds=%d boundaries=%d' % (len(d['tiers']),len(d['fifth_tier_credentials']),len(d['boundaries'])))"
echo "L5-02-14 SELF-VERIFY PASS"
```

Expected output, exactly:

```
GATE G01-tier-registry PASS
GATE G02-downward-move PASS
GATE G03-fifth-tier-entries PASS
GATE G04-envelopes PASS
GATE G05-envelope-evaluator PASS
GATE G06-rotation-runbook PASS
GATE G07-rotation-gate PASS
GATE G08-boundaries PASS
GATE G09-separation PASS
GATE G10-no-api-keys PASS
GATE G11-containment PASS
GATE G12-publication PASS
GATE G13-generated-clean PASS
GATE-FAILURES 0
L5-P2 EXIT GATE PASS
RESULT PASS reproducible
FAIL-CLOSED-CONTROLS 6
PUBLISHED tiers=5 creds=5 boundaries=2
L5-02-14 SELF-VERIFY PASS
```

### STOP rule

STOP — do not commit, do not push, file the blocker of Section 4 — if any of these hold:

* Any `GATE Gnn FAIL`. Re-run that gate's own command directly to read its output, and apply **that
  task's** STOP rule; do not modify the gate script to skip the check. Class depends on the failing gate.
* `G13-generated-clean` fails. A generated file was hand-edited. Re-run the emitter that owns it
  (`emit_fifth_tier.py`, `emit_envelopes.py`, `emit_shell_gate.py`, `publish_secret_tiers.py`) and commit
  the regenerated file. Class `shape-mismatch`.
* `G08-boundaries` fails on `B2-A3`, `B2-A4` or `B2-A5`. T10 or T11 is not merged to `integration` yet.
  This is a sequencing fault, not a defect: wait for the merge train. Do not weaken the gate.

---

## 8. Phase exit checklist

Phase 2 is complete when **every row** below holds against `integration` after the L5 rebase. Each maps to
a Definition-of-Done row of `L5-00-charter.md` §10 where one applies.

| # | Statement | Proving command | Required output | Charter DoD |
|---|---|---|---|---|
| X-01 | The five tiers exist with the §40.1 contents and locations | `python access/secrets/tools/validate_tiers.py` | `RESULT PASS 5` | — |
| X-02 | No secret has moved down a tier, on disk or in the registry | `bash access/secrets/checks/check-no-downward-move.sh \| tail -1` | `RESULT PASS` | — |
| X-03 | Five fifth-tier credentials carry cadence, rotator, runbook, envelope and alert owner | `python access/secrets/tools/emit_fifth_tier.py \| tail -1` | `RESULT PASS 5` | DoD-12 |
| X-04 | Five behavioural envelopes exist, each with the four §40.1 clauses | `python access/secrets/tools/emit_envelopes.py \| tail -1` | `RESULT PASS 5` | DoD-12 |
| X-05 | Every envelope clause fires on breach and is silent on a clean run | six fixture runs of `evaluate_envelope.py` (T06 SELF-VERIFY) | the T06 expected block | — |
| X-06 | The rotation runbook is one page and carries exactly three blocking steps | `bash access/secrets/runbooks/check-runbook.sh \| tail -1` | `RESULT PASS` | — |
| X-07 | A rotation cannot be recorded done without clean reconciliation, AT-110 and re-escrow | `bash access/secrets/checks/rotation-complete.sh access/secrets/testdata/rotation/complete.yaml \| grep '^ROTATION-'` | `ROTATION-DONE-PERMITTED` | — |
| X-08 | Both §40.3 boundaries are declared verbatim and every assertion holds | `bash access/secrets/boundaries/check-boundaries.sh --phase complete \| tail -1` | `RESULT PASS` | — |
| X-09 | The fifth tier is held so a passive root shell does not read it, behind a hardware-key second factor | `ssh "$OPS_VM_ALIAS" 'bash -s' < access/secrets/host/check-credential-store.sh \| tail -1` and the same for `infra/network/check-shell-gate.sh` | `RESULT PASS` twice | — |
| X-10 | Rotator/host-root separation is resolved, one way or the other | `bash access/secrets/separation/check-separation.sh \| grep '^SEPARATION'` | `SEPARATION separated` or `SEPARATION accepted-risk …` | — |
| X-11 | `env \| grep -i api_key` is empty on every checked surface | `bash access/secrets/checks/no-api-keys.sh access/model \| tail -1` | `RESULT PASS` | — |
| X-12 | A workstation compromise rotates every fifth-tier credential as a named step | `bash access/secrets/incident/check-containment.sh \| tail -1` | `RESULT PASS` | — |
| X-13 | Every control this phase produced is classified fail-closed | `python -c "import glob,yaml;print(set(yaml.safe_load(open(f))['classification'] for f in glob.glob('access/fail-closed/*.yaml')))"` | `{'fail-closed'}` | DoD-08 |
| X-14 | Publication is byte-reproducible | `python access/secrets/tools/publish_secret_tiers.py --check \| tail -1` | `RESULT PASS reproducible` | DoD-06 |
| X-15 | One command runs everything and passes | `bash access/secrets/gate/phase2-gate.sh \| tail -1` | `L5-P2 EXIT GATE PASS` | — |
| X-16 | The lane touched no foreign path across all fourteen branches | `git diff --name-only origin/integration...HEAD \| grep -cvE '^(access/|infra/network/)'` | `0` | DoD-02 |

**X-09 is the only row that needs a live host.** It is executed once the operations VM exists (phase 4,
L5-04-02). Until then it is recorded as pending with the task id that will discharge it — never marked
passed, and never quietly dropped.

---

## 9. Cross-lane handoffs

Every check this phase produces is a **script in an L5-owned path**. L5 owns no path under
`.github/workflows/**`, so nothing here schedules itself: L5 declares, L2 executes, L3 reconciles
(`L5-00-charter.md` §2.3). Each row below is a published interface — a path plus an exit contract — and is
consumed as an artifact, never by reaching into this lane's source tree (PARTITION rule 4).

| Id | Artifact | Exit contract | Consumed by | For |
|---|---|---|---|---|
| HO-01 | `access/secrets/checks/check-no-downward-move.sh` | `0` clean · `1` finding, a security incident under §43 · `2` fail-closed | **L2** | A control-plane CI check on every pull request |
| HO-02 | `access/secrets/envelope/check-envelope.sh <runs-dir> <triggers-dir>` | `0` inside envelope · `1` Blocking drift · `2` fail-closed | **L3** (drift rows), **L2** (scheduled run) | D96 envelope-breach rows in the reconciler's drift set |
| HO-03 | `access/published/secret-tiers.v1.json` | JSON; `fifth_tier_credentials[].permission_set` is the published bound | **L3** (provisioning and reconciliation), **AT-110** | Which tier a credential lives in, and the permission set AT-110 executes against |
| HO-04 | `access/secrets/checks/rotation-complete.sh <record>` | `0` done permitted · `1` not done · `2` fail-closed | **L4** | The record store's rotation records may only close on a `0` |
| HO-05 | `access/secrets/checks/no-api-keys.sh` | `0` clean · `1` invariant 84 breached · `2` fail-closed | **L2** (quarterly run), **L0** (onboarding) | §98.2 Phase 1 verification and the quarterly re-check |
| HO-06 | `access/secrets/fifth-tier/*.yaml` field set, mirrored in HO-03 | YAML | **L5 phase 5**, task L5-05-02 | The §49.1 asset-inventory entries — cadence, rotator, runbook, envelope, alert owner |
| HO-07 | `access/secrets/host/check-credential-store.sh`, `infra/network/check-shell-gate.sh` | `0` boundary holds · `1` breach · `2` host unreachable | **L5 phase 4**, task L5-04-07 | The verifier phase 4's provisioning must satisfy |
| HO-08 | `access/secrets/incident/containment-checklist.yaml` | YAML, `steps[].id` stable | **L0** (incident runbooks), **L4** (incident records) | §43.4 containment, with the C-04 enumeration machine-checked |
| HO-09 | `access/fail-closed/*.yaml` | one file per control | **L5 phase 7** (`L5-07`), **L0** | DoD-08 and the invariant-80 classification map |

**What this phase consumes, and from where.** Exactly one file: `contracts/access/access-inputs.yaml`,
frozen by L0 at Phase 0 (Section 2). Nothing else crosses a lane boundary inward. In particular this phase
reads no registry, imports no reconciler code, and writes no workflow.

---

## 10. Escalations to L0 — decisions this phase must not make

Each item is inside L5's owned paths but outside L5's authority. The task named files a blocker (Section 4)
and stops; it never resolves the item itself.

| Id | Item | Why it is L0's | Raised by | Spec anchor |
|---|---|---|---|---|
| E-P2-01 | The **per-run cap on objects mutated**. D96 names it as part of behavioural detection; §40.1's own envelope list at line 3685 has four clauses and omits it, and the frozen contract carries no key for it. The envelopes record `objects_mutated_cap: not-in-envelope-v1` rather than invent a number | A calibrated threshold, and a contract-shape change | T05 | D96 line 10189; §40.1 line 3685 |
| E-P2-02 | Narrowing `kind` from "least-privilege GitHub App **or** fine-grained PAT" to one of the two, for the reconciler, the provisioning CLI and the organisation-export token | §40.1 permits either; choosing is a recorded decision, not an executor's pick | T04 | §40.1 line 3654 |
| E-P2-03 | The named holder, compensating control, expiry and dated review of the **rotator / host-root concentration**, where headcount does not permit separation | §40.3 requires a recorded acceptance with a named holder; §90.3 gives the shape; naming a person is a Founder decision | T11 | §40.3 line 3703; §90.3 line 7982; §54.2 |
| E-P2-04 | Procuring hardware keys, or recording a dated `policy_waiver` exception, where no `sk-` capable key exists to enrol on the operations VM shell path | An exception with a mandatory expiry, an owner and a deactivation trigger | T10 | §40.3 line 3703; §54.2; §51.4 |
| E-P2-05 | Recalibration of the run-count ceiling multiplier away from 2, or of the quarterly rotation cadence | Both are marked calibrated configuration, refit on the §84.5 cadence — never adjusted mid-task | T05, T04 | §40.1 lines 3683, 3685; §99.3 item 7 |
| E-P2-06 | Any missing value in `contracts/access/access-inputs.yaml` — a rotator, an envelope alert owner, an expected source host, a schedule, a permission set, a shell-gate key id, the API-key-free check's owner or profile paths | `contracts/**` is L0's and frozen (PARTITION rule 2). A lane files a Contract Change Request; it never edits | T04, T05, T10, T11, T12 | PARTITION.md lines 22, 26 |
| E-P2-07 | The scheduling surface for HO-01, HO-02 and HO-05. L5 owns no path under `.github/workflows/**`, so these scripts have no schedule until L2 wires them | Path ownership is frozen | T03, T06, T12 | PARTITION.md line 21; `L5-00-charter.md` §2.3 |
| E-P2-08 | Subsystems **G, H, J, O and P** are assigned to no lane in PARTITION v1. Where a control in this phase touches one — the background host's egress wall (J) beside the fifth-tier credential it holds is the live case — this phase declares the owned control and claims nothing | L5 does not claim unassigned subsystems | T09, T10 | §99.2 lines 9184–9231; `L5-00-charter.md` §3.2, E-02 |
| E-P2-09 | The duplicate **AT-110** rows at spec lines 9438 and 9439. This file cites the range and does not renumber | A specification defect | T08, T14 | §100.6 lines 9421–9441; `L5-00-charter.md` E-10 |

---

## 11. Definition of done for this file

Phase 2 of lane L5 is complete when all fourteen task branches have merged to `integration` in index order,
every row of Section 8 holds, and `bash access/secrets/gate/phase2-gate.sh` prints `L5-P2 EXIT GATE PASS`
on a clean checkout of `integration`.

Two things this phase deliberately did **not** do, recorded here so no later reader mistakes them for
omissions. It did not provision the fifth-tier store — `ops-vm/credentials/**` is L5-04-07's, and this
phase wrote only the requirement and the verifier that proves phase 4 met it. And it did not execute
AT-110 — the reconciler does not exist on `integration` at this point in the merge train, so this phase
built the gate that will re-execute AT-110 at every rotation, on the same gate as §40.1's
clean-reconciliation condition, and left the first execution to the phase that builds the reconciler.

Everything else in Section 1 is built, checked by a command with an unambiguous output, and published.

**End of L5 Phase 2 — Secrets and Trust Boundaries.**
