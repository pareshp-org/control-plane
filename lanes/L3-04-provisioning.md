> **[SUPERSEDED — FD-B1-L3 2026-09-02]**
> This file has been superseded by L3-06-tasks.md. Do not execute tasks from this file.
> Authoritative plan: Code/implementation/lanes/L3-06-tasks.md

# L3 — PHASE 4: PROVISIONING AND SCAFFOLDING (Subsystem D)

> **FD-087 (2026-09-09):** L3-04 split into two phases per bootstrap constraint:
> - **L3-04-DRY**: Bootstrap phase — dry-run only, no live GitHub org API calls
> - **L3-04-LIVE**: Post-bootstrap phase — live org provisioning (runs after bootstrap constraint lifts)
> 
> Bootstrap constraint source: L3-06 §0.4 — "no live org calls during bootstrap phase"

**Lane:** L3 Reconciler & Provisioning · **Branch prefix:** `lane/3/*` · **Subsystem:** D (Section 99.2)
**Paths this phase writes (exclusively owned by L3 per the FROZEN PARTITION):** `tools/provision/**`
**Also owned by L3, read but not written in this phase:** `reconciler/**`, `validators/drift/**`
**Repository:** `control-plane`

---

## 0. Read this before task 1

### 0.1 What this phase is

Subsystem D of Section 99.2: *"Create-product, add-person, change-role, remove-person operations: repo from template, Teams from registries, generated CODEOWNERS, branch protection, environments with scoped secrets, registration in every surface with zero hand-editing."*

The bar is set by Section 19.1 and is not negotiable:

> **"A new product must be boring to create. That is a feature."**
> **"If a human must edit a dashboard to add a product, that is a defect in the operating system, not a task."**

Section 12.6 sets the same bar for people: *"No ordinary personnel or product change should require hand-editing files across twenty repositories. If it does, the scaffolding is incomplete and that is a platform defect."*

### 0.2 Why this phase is written defensively

Section 99.6 risk 6 names the reconciler *"the highest-privilege identity in the system"* and *"the most dangerous code"*. The provisioning CLI sits beside it in the same fifth secrets tier (Section 40.1) and creates the very controls the reconciler later enforces — branch protection, CODEOWNERS, environments, Teams. A provisioning bug does not merely mis-provision; it manufactures a gate that appears to be working and is not, which is the exact failure Section 11.1 exists to prevent.

Eight **binding safety rules** therefore apply to every line of code written in this phase. They are implemented once in the gateway (task `L3-04-02`) and re-proved in the phase gate (`L3-04-18`).

| # | Rule | Spec basis |
| --- | --- | --- |
| **SR-1** | The CLI issues **no HTTP DELETE, ever.** Not for a repository, a team, a membership, an environment, a ruleset or a branch. | Invariant 47 (append-only); Section 99.6 risk 6 |
| **SR-2** | The CLI **never reads or writes a secret value.** Any request path containing `/secrets` or `/codespaces/secrets` is refused before it is sent. Secret values reach environments through tracked manual-step issues only. | Section 40.1 (five tiers, a secret never moves down a tier); Section 53.3 |
| **SR-3** | The CLI **never modifies organisation settings.** `PATCH /orgs/{org}` and every `/orgs/{org}/settings*` path is refused. | Section 40.3; AT-110's boundary reasoning applied to the sibling credential |
| **SR-4** | The CLI **never writes a workflow file.** Any content write under `.github/workflows/` is refused. A workflow-file change pushed by a machine identity is Blocking drift. | Section 53.1; Section 40.3 |
| **SR-5** | The CLI **never writes to the records repository.** `records/**` and `events/**` are reached only by dispatching the records-writer workflow. | Section 40.1 (D89); Section 97.1 (D76 as amended by D89) |
| **SR-6** | **Stricter-only.** Where actual platform state is already stricter than the template, the CLI does **not** apply the template. It records a Level-2 finding and continues. | Invariant 81; Section 53.3; AT-033 |
| **SR-7** | **`plan` is the default mode.** `--mode apply` requires an explicit flag **and** a `--decision-record` argument that resolves to a real record id. | Invariant 79; Section 64.1; Section 26.4 (authority delta needs a linked decision record in the same commit) |
| **SR-8** | **Idempotent and resumable.** Every operation converges on re-run: no duplicate Team, no duplicate issue, no duplicate registry entry, no second repository. | Section 19.1 ("boring to create"); Section 53.2 Level 3 ("safe, idempotent, reversible") |

**A task that cannot satisfy all eight does not ship. It STOPs.**

### 0.3 Environment the executor must have before task 1

`$PROVISION_SANDBOX_ORG` is set to the Q10 value (confirmed sandbox org).

Run this once. Every value must print. If any prints `MISSING`, **STOP** and open the blocker issue in §0.7.

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
export CP="$HOME/work/control-plane"
export PROVISION_SANDBOX_ORG="${PROVISION_SANDBOX_ORG:-MISSING}"
export PROVISION_RUN_DIR="$HOME/.provision-runs"
mkdir -p "$PROVISION_RUN_DIR"

echo "CP=$CP"
[ -d "$CP/.git" ] && echo "control-plane=OK" || echo "control-plane=MISSING"
[ -d "$CP/contracts" ] && echo "contracts=OK" || echo "contracts=MISSING"
[ -d "$CP/reconciler" ] && echo "reconciler=OK" || echo "reconciler=MISSING"
command -v gh   >/dev/null && echo "gh=OK"   || echo "gh=MISSING"
command -v git  >/dev/null && echo "git=OK"  || echo "git=MISSING"
command -v make >/dev/null && echo "make=OK" || echo "make=MISSING"
command -v python3 >/dev/null && echo "python3=OK" || echo "python3=MISSING"
python3 -c 'import sys; print("py=OK" if sys.version_info[:2]>=(3,12) else "py=MISSING")'
echo "sandbox_org=$PROVISION_SANDBOX_ORG"
gh auth status >/dev/null 2>&1 && echo "gh_auth=OK" || echo "gh_auth=MISSING"
```

**Never run any task in this phase against the production GitHub organisation.** Every task in this phase targets `$PROVISION_SANDBOX_ORG`. Production execution is an operations act performed by a `devops`-capability holder (Section 9; Section 19.1 "the executor is named"), not a build act.

> **RESOLVED (FD-046, 2026-09-06):** Live org replaced by mocked stub per Founder decision. See `contracts/stubs/`.

### 0.4 Standard lane procedures

Task `L3-04-01` creates `tools/provision/scripts/lane.sh`. From `L3-04-02` onward, every task begins and ends with these two calls. They are deterministic: `lane_start` branches from `integration` if the previous task's branch is already merged there, and from the previous task's branch otherwise.

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
# start a task branch
source "$CP/tools/provision/scripts/lane.sh"
lane_start <TASK-SUFFIX> <PREV-TASK-SUFFIX>   # e.g. lane_start 04-t05 04-t04

# open the pull request when the task's SELF-VERIFY passes
lane_pr <TASK-SUFFIX> "<pr title>"
```

`lane.sh` contents are given verbatim in `L3-04-01`.

### 0.5 Exit-code contract for the `provision` CLI

Fixed for the whole phase. Every task's tests assert against it.

| Code | Meaning |
| --- | --- |
| `0` | Operation completed (in `plan` mode: a plan was produced) |
| `2` | **STOP** — a precondition, contract or safety rule refused the operation. Nothing was written. |
| `3` | Drift or convergence failure — the platform did not reach declared state; a finding was emitted |
| `4` | Safety-rule violation attempted and blocked (SR-1..SR-8). Always accompanied by a `SAFETY-REFUSED:` line on stderr |

### 0.6 CLI surface built by this phase (fixed; no task may add a verb)

```
provision create-product          --product-id … (L3-04-13)
provision preprovision-person     --person-id …  (L3-04-14)
provision add-person              --person-id …  (L3-04-15)
provision change-role             --person-id …  (L3-04-16)
provision remove-person           --person-id …  (L3-04-17)
provision verify-scaffold         --repo …       (L3-04-10)
provision verify-surfaces         --product-id … (L3-04-12)
provision verify-credential-envelope            (L3-04-02)
```

### 0.7 Canonical blocker-issue template

Every STOP rule in this phase files this issue and then **stops all work on the task**. Do not improvise a workaround. Do not widen a path. Do not disable a check.

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
gh issue create \
  --repo "$(gh repo view --json nameWithOwner -q .nameWithOwner)" \
  --title "BLOCKER L3-04-<TASK>: <one-line condition>" \
  --label "blocker,lane-3,phase-4" \
  --body "$(cat <<'EOF'
## Blocked task
Task id: L3-04-T<NN>
Lane: L3 (Reconciler & Provisioning), Phase 4 (Provisioning & Scaffolding)
Owned path: tools/provision/**

## STOP rule that fired
<paste the exact STOP rule text from the task>

## Command run
<paste the exact command>

## Actual output
```
<paste stdout and stderr verbatim, unedited>
```

## Expected output
<paste the SELF-VERIFY expected line from the task>

## What I did NOT do
- I did not modify any path outside tools/provision/**.
- I did not disable, weaken or skip any check.
- I did not run anything against a non-sandbox GitHub organisation.

## Decision needed from L0
<state the single question that unblocks this, or "none — this is an environment fault">
EOF
)"
```

---

## 1. DECISION REQUIRED — three items for L0

These three cannot be settled inside this lane. Each carries a **provisional binding default** so the executor is never blocked; if L0 publishes an override under `contracts/`, the override wins and the affected tasks are re-run.

### DECISION REQUIRED — D-L3-04-01: implementation language and runtime for `tools/provision/**`

Section 99.1 names *"a provisioning and scaffolding CLI"* and Section 99.5 fixes the git host, CI, dashboards, boards and records substrate — but no implementation language. Choosing one is a cross-lane decision (L2's reusable workflows must invoke it; L5's operations VM must run it).

* **Provisional binding default:** Python 3.12, standard library only, plus `PyYAML` pinned by hash in `tools/provision/requirements.txt`. All GitHub access via the `gh` CLI as a subprocess (never a bespoke HTTP client), so the credential surface is one environment variable and every call is loggable in one place — which is what makes SR-1..SR-5 enforceable at a single choke point.
* **Entry point:** `python -m provision` from `$CP/tools/provision`.
* **If L0 overrides:** all tasks in this phase are re-run from `L3-04-01`; no partial port.

### Binding: D-L3-04-02 adopted — the provisioning CLI credential's permission set and its asset-inventory entry

Section 40.1 requires that *"each credential's exact permission set is published in its inventory entry and in this section"*, and Section 49.1 requires an inventory entry carrying rotation cadence, named rotator (a `devops`-capability holder), runbook link and out-of-window alert-config owner. The inventory lives in `assets/**`, which the FROZEN PARTITION assigns to **L5**. L3 cannot write it.

* **What L0 must obtain from L5:** an `assets.yaml` entry for the provisioning CLI credential naming its exact fine-grained permission set, its rotation cadence, its rotator and its behavioural envelope (Section 40.1).
* **Provisional binding default for this phase:** the CLI declares, asserts and self-tests the *minimum* set the tasks below actually need — nothing more — in `tools/provision/provision/security/envelope.yaml`, and `provision verify-credential-envelope` (task `L3-04-02`) proves the credential cannot exceed it. That file is L3-owned and is the input L5 transcribes into the inventory.

### DECISION REQUIRED — D-L3-04-03: where `product-template` declares its seed-data and migration-directory paths

Section 33.1 makes the required-file list binding — *"Required-file presence is checked, not assumed"* — and names `.env.example`, `docker-compose.dev.yml`, `Makefile`, **seed data**, **migration directory**, `verification/`, `AGENTS.md`, and either `product.yaml` or a pointer. Two of those eight are described by role, not by path. `product-template` is not an L3-owned repository, so L3 cannot define them there.

* **What L0 must settle:** the canonical, checkable path (or declaration) for seed data and for the migration directory in `product-template`.
* **Provisional binding default for this phase:** `tools/provision/provision/conformance/required_files.yaml` (L3-owned) fixes them as `seed/` and `migrations/`, and the scaffold verifier fails a repository that has neither. If L0 settles differently, only `required_files.yaml` changes and `L3-04-10` is re-run.

---

## 2. Task index

| Task id | Title | Size | Depends on |
| --- | --- | --- | --- |
| `L3-04-01` | Package skeleton, lane helper, lane-guard proof | S | — |
| `L3-04-02` | GitHub call gateway, safety rules SR-1..SR-8, credential envelope | M | T01 |
| `L3-04-03` | Contract-bound resolvers (registry paths, event enum, template ref) | M | T02 |
| `L3-04-04` | Idempotent step engine, run ledger, manual-step issue emitter | M | T03 |
| `L3-04-05` | create-product step: preflight and repository from template | M | T04 |
| `L3-04-06` | create-product step: GitHub Team from assignments | S | T05 |
| `L3-04-07` | create-product step: generated CODEOWNERS, humans-only negative check | M | T06 |
| `L3-04-08` | create-product step: branch protection from template | M | T07 |
| `L3-04-09` | create-product step: environments, deployment branch and tag policy, scoped secrets | M | T08 |
| `L3-04-10` | create-product step: scaffold conformance — ten commands, three endpoints, verification skeleton | M | T05 |
| `L3-04-11` | create-product step: registry entry, CONFIGURE checklist, alert channel and support mailbox | M | T04, T10 |
| `L3-04-12` | create-product step: surface-registration verifier (no hand-edited dashboards) | M | T11 |
| `L3-04-13` | `provision create-product` orchestrator and AT-001 rehearsal | L | T05–T12 |
| `L3-04-14` | `provision preprovision-person` — the T-minus-one-week checklist | M | T04 |
| `L3-04-15` | `provision add-person` | L | T13, T14 |
| `L3-04-16` | `provision change-role` | M | T15 |
| `L3-04-17` | `provision remove-person`, orphan gate, exit record | L | T15 |
| `L3-04-18` | Phase gate: destructive-guard suite, idempotence proof, phase evidence | M | T13, T16, T17 |

---

## L3-04-01 — Package skeleton, lane helper, lane-guard proof

**Size:** S · **Depends on:** — · **Owns:** `tools/provision/**`

### Files created

<!-- LAYOUT ALIGNMENT (FD-045, 2026-09-06): The authoritative phase-file (L3-06-tasks.md, 116-task plan) places provisioner modules flat in tools/provision/ (e.g. tools/provision/cli.py, tools/provision/codeowners.py) with no nested provision/ subpackage and entrypoint python -m tools.provision.cli. This superseded file uses a nested tools/provision/provision/ package instead. The phase-file layout is canonical; any re-implementation must follow L3-06-tasks.md tasks L3-P4-01 through L3-P4-10. -->

| Path | Contract |
| --- | --- |
| `tools/provision/README.md` | One screen: what the CLI is, the eight safety rules, the exit codes, how to run it |
| `tools/provision/requirements.txt` | `PyYAML==6.0.2` with `--hash=` pin |
| `tools/provision/pytest.ini` | `testpaths = tests`, `addopts = -q` |
| `tools/provision/provision/__init__.py` | `__version__ = "0.1.0"` |
| `tools/provision/provision/__main__.py` | `from provision.cli import main; raise SystemExit(main())` |
| `tools/provision/provision/cli.py` | argparse root. Registers only the eight verbs of §0.6; unknown verb → exit 2 |
| `tools/provision/provision/errors.py` | `Stop(Exception)`→2, `DriftError`→3, `SafetyRefusal`→4 |
| `tools/provision/scripts/lane.sh` | `lane_start` / `lane_pr` (verbatim below) |
| `tools/provision/tests/test_cli_surface.py` | Asserts exactly the eight verbs exist and no more |
| `tools/provision/tests/test_exit_codes.py` | Asserts the §0.5 mapping |

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
export CP="$HOME/work/control-plane"
cd "$CP"
git fetch origin
git checkout -B lane/3/04-t01 origin/integration
mkdir -p tools/provision/provision tools/provision/scripts tools/provision/tests
```

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
cat > "$CP/tools/provision/scripts/lane.sh" <<'EOF'
#!/usr/bin/env bash
# L3 lane helper. Deterministic branch selection: integration if PREV is merged, else PREV.
set -euo pipefail
: "${CP:?CP must be set to the control-plane checkout}"

lane_start() {
  local task="$1" prev="${2:-}"
  cd "$CP"
  git fetch origin --prune
  local base="origin/integration"
  if [ -n "$prev" ] && git rev-parse --verify -q "origin/lane/3/$prev" >/dev/null; then
    if ! git merge-base --is-ancestor "origin/lane/3/$prev" origin/integration; then
      base="origin/lane/3/$prev"
    fi
  fi
  git checkout -B "lane/3/$task" "$base"
  echo "LANE-START: lane/3/$task from $base"
}

lane_guard() {
  cd "$CP"
  local foreign
  foreign="$(git diff --name-only origin/integration...HEAD | grep -v '^tools/provision/' || true)"
  if [ -n "$foreign" ]; then
    echo "LANE-GUARD: FAIL"; echo "$foreign"; return 1
  fi
  echo "LANE-GUARD: PASS"
}

lane_pr() {
  local task="$1" title="$2"
  cd "$CP"
  lane_guard
  git fetch origin --prune
  git rebase origin/integration
  git push -u origin "lane/3/$task" --force-with-lease
  gh pr create --base integration --head "lane/3/$task" \
    --title "L3-$task: $title" \
    --body "Lane L3 (Reconciler & Provisioning), Phase 4. Touches tools/provision/** only. Merge in train order L1 -> L4 -> L2 -> L3 -> L5."
  echo "LANE-PR: opened for lane/3/$task"
}
EOF
chmod +x "$CP/tools/provision/scripts/lane.sh"
```

Write the remaining files listed above, then:

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
cd "$CP/tools/provision"
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt --require-hashes
pip install pytest
python -m pytest -q
```

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
cd "$CP"
git add tools/provision
git commit -m "L3-04-01: provisioning CLI package skeleton, lane helper, verb surface lock"
source "$CP/tools/provision/scripts/lane.sh"
lane_pr 04-t01 "provisioning CLI skeleton"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Package imports and reports its version | `cd "$CP/tools/provision" && python -c "import provision; print(provision.__version__)"` | `0.1.0` |
| A2 | Exactly the eight verbs of §0.6 exist | `cd "$CP/tools/provision" && python -m provision --list-verbs \| sort \| tr '\n' ' '` | `add-person change-role create-product preprovision-person remove-person verify-credential-envelope verify-scaffold verify-surfaces ` |
| A3 | An unknown verb exits 2 | `cd "$CP/tools/provision" && python -m provision frobnicate; echo "exit=$?"` | `exit=2` |
| A4 | Every changed path is L3-owned | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |
| A5 | Tests pass | `cd "$CP/tools/provision" && python -m pytest -q >/dev/null && echo OK` | `OK` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && python -c "import provision; assert provision.__version__=='0.1.0'" \
  && [ "$(python -m provision --list-verbs | wc -l)" -eq 8 ] \
  && python -m provision frobnicate >/dev/null 2>&1; [ $? -eq 2 ] \
  && python -m pytest -q >/dev/null \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-01: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-01: PASS`

### STOP rule

**If `$CP/.git` does not exist, or `origin/integration` does not exist, or `python3` is below 3.12 — do not proceed.** Do not clone a different repository, do not create `integration` yourself, do not install a different interpreter. File the §0.7 blocker with title `BLOCKER L3-04-01: environment precondition unmet`.

---

## L3-04-02 — GitHub call gateway, safety rules SR-1..SR-8, credential envelope

**Size:** M · **Depends on:** `L3-04-01` · **Owns:** `tools/provision/**`

This is the choke point. **Every** GitHub interaction in the whole phase goes through `ghclient.call()`. No task may call `gh` or `subprocess` directly; `L3-04-18` proves it by grep.

### Files created

| Path | Contract |
| --- | --- |
| `tools/provision/provision/core/ghclient.py` | `call(method, path, body=None, *, mode)` → dict. Refuses per the allowlist below. Appends every attempt to the run ledger. |
| `tools/provision/provision/security/allowlist.yaml` | The verb+path allowlist, verbatim below |
| `tools/provision/provision/security/envelope.yaml` | The minimum credential permission set (input to D-L3-04-02) |
| `tools/provision/provision/security/refusals.py` | SR-1..SR-5 predicates, each a pure function of `(method, path, body)` |
| `tools/provision/provision/core/ledger.py` | Append-only JSONL at `$PROVISION_RUN_DIR/<run-id>/calls.jsonl` |
| `tools/provision/provision/ops/verify_credential_envelope.py` | `provision verify-credential-envelope` |
| `tools/provision/tests/test_refusals.py` | One test per refusal, 24 cases minimum |
| `tools/provision/tests/test_gateway_ledger.py` | Ledger records refusals as well as sends |

### The allowlist — copy verbatim

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
cat > "$CP/tools/provision/provision/security/allowlist.yaml" <<'EOF'
# The ONLY GitHub calls tools/provision may make. Anything absent is refused (exit 4).
# Basis: Section 40.1 (least-privilege fifth-tier credential), Section 99.6 risk 6.
version: 1
allowed:
  # --- read ---
  - {method: GET,  path: "/repos/*"}
  - {method: GET,  path: "/orgs/*"}
  - {method: GET,  path: "/users/*"}
  # --- create-product ---
  - {method: POST, path: "/repos/*/*/generate"}
  - {method: PATCH, path: "/repos/*/*", fields: [private, delete_branch_on_merge, has_issues]}
  - {method: POST, path: "/orgs/*/teams"}
  - {method: PUT,  path: "/orgs/*/teams/*/memberships/*"}
  - {method: PUT,  path: "/orgs/*/teams/*/repos/*/*"}
  - {method: PUT,  path: "/repos/*/*/branches/*/protection"}
  - {method: POST, path: "/repos/*/*/rulesets"}
  - {method: PUT,  path: "/repos/*/*/rulesets/*"}
  - {method: PUT,  path: "/repos/*/*/environments/*"}
  - {method: POST, path: "/repos/*/*/environments/*/deployment-branch-policies"}
  # --- issues (checklists, manual steps) ---
  - {method: POST, path: "/repos/*/*/issues"}
  - {method: PATCH, path: "/repos/*/*/issues/*", fields: [state, body, labels]}
  # --- registry pull requests on control-plane ---
  - {method: POST, path: "/repos/*/*/git/refs"}
  - {method: PUT,  path: "/repos/*/*/contents/*"}
  - {method: POST, path: "/repos/*/*/pulls"}
  # --- people ---
  - {method: PUT,  path: "/orgs/*/memberships/*", fields: [role]}
  # --- records: dispatch only, never a direct write (SR-5) ---
  - {method: POST, path: "/repos/*/*/actions/workflows/*/dispatches"}
refused_always:
  - reason: "SR-1 no deletion"          match: {method: DELETE}
  - reason: "SR-2 no secret access"     match: {path_contains: "/secrets"}
  - reason: "SR-3 no org settings"      match: {method: PATCH, path: "/orgs/*"}
  - reason: "SR-3 no org settings"      match: {path_contains: "/orgs/*/settings"}
  - reason: "SR-4 no workflow writes"   match: {path_contains: "/contents/.github/workflows"}
  - reason: "SR-5 no records writes"    match: {path_contains: "/contents/records/"}
  - reason: "SR-5 no events writes"     match: {path_contains: "/contents/events/"}
EOF
```

### Behavioural rules (non-interpretive; implement exactly)

1. `call()` resolves `refused_always` **first**. A match raises `SafetyRefusal`, prints `SAFETY-REFUSED: <reason> <METHOD> <path>` to stderr, appends a ledger line with `"sent": false`, and exits 4.
2. A call matching no `allowed` entry is refused identically with reason `not-on-allowlist`.
3. `PATCH` calls whose allowlist entry declares `fields:` are refused if the body contains any key outside that list.
4. In `mode == "plan"`, no non-GET call is sent. Each is printed as `PLAN <METHOD> <path>` and ledgered with `"sent": false, "mode": "plan"`.
5. In `mode == "apply"`, a non-GET call is sent via `gh api -X <METHOD> <path> --input -`. Every call is ledgered with method, path, body-key list (**never body values** — SR-2 applies to logs too), response status and UTC timestamp with offset (Section 97.1: *"Every record and event timestamp is stored in UTC with its offset"*).
6. `call()` never retries a non-GET automatically. A 5xx on a non-GET raises `DriftError` (exit 3) and the run is resumable via the step ledger of `L3-04-04`.
7. `provision verify-credential-envelope` reads `envelope.yaml`, attempts each of the six probes below against `$PROVISION_SANDBOX_ORG`, and requires all six to be **refused by the gateway before reaching GitHub**.

### The six envelope probes (mirrors the reasoning of AT-110 for the sibling credential)

| # | Probe | Must produce |
| --- | --- | --- |
| P1 | `DELETE /repos/$ORG/anything` | `SAFETY-REFUSED: SR-1 no deletion` |
| P2 | `PUT /repos/$ORG/x/actions/secrets/FOO` | `SAFETY-REFUSED: SR-2 no secret access` |
| P3 | `PUT /repos/$ORG/x/environments/production/secrets/FOO` | `SAFETY-REFUSED: SR-2 no secret access` |
| P4 | `PATCH /orgs/$ORG` | `SAFETY-REFUSED: SR-3 no org settings` |
| P5 | `PUT /repos/$ORG/x/contents/.github/workflows/ci.yml` | `SAFETY-REFUSED: SR-4 no workflow writes` |
| P6 | `PUT /repos/$ORG/records/contents/records/x.yaml` | `SAFETY-REFUSED: SR-5 no records writes` |

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t02 04-t01
# ... write the files listed above ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest -q
cd "$CP" && git add tools/provision
git commit -m "L3-04-02: GitHub call gateway with SR-1..SR-8 refusals and credential envelope probe"
lane_pr 04-t02 "GitHub call gateway and safety rules"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | All six envelope probes are refused | `cd "$CP/tools/provision" && python -m provision verify-credential-envelope \| tail -1` | `ENVELOPE: 6/6 REFUSED` |
| A2 | Envelope check exits 0 when all six refuse | `cd "$CP/tools/provision" && python -m provision verify-credential-envelope >/dev/null; echo "exit=$?"` | `exit=0` |
| A3 | A refusal exits 4 | `cd "$CP/tools/provision" && python -c "from provision.core.ghclient import call; call('DELETE','/repos/x/y',mode='apply')" 2>/dev/null; echo "exit=$?"` | `exit=4` |
| A4 | `plan` mode sends nothing | `cd "$CP/tools/provision" && python -m provision create-product --product-id demo --mode plan --dry-ledger \| grep -c '"sent": true'` | `0` |
| A5 | No body values in the ledger | `grep -c '"body_values"' "$PROVISION_RUN_DIR"/*/calls.jsonl \|\| echo 0` | `0` |
| A6 | Refusal tests cover every `refused_always` row | `cd "$CP/tools/provision" && python -m pytest tests/test_refusals.py -q >/dev/null && echo OK` | `OK` |
| A7 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && [ "$(python -m provision verify-credential-envelope | tail -1)" = "ENVELOPE: 6/6 REFUSED" ] \
  && python -m pytest tests/test_refusals.py tests/test_gateway_ledger.py -q >/dev/null \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-02: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-02: PASS`

### STOP rule

**If any of the six probes is NOT refused by the gateway — that is, if a probe reaches GitHub — do not proceed and do not run any further task in this phase.** A gateway that lets a probe through is the Section 99.6 risk-6 failure in its build form. File the §0.7 blocker with title `BLOCKER L3-04-02: credential envelope probe P<n> was not refused` and stop.

---

## L3-04-03 — Contract-bound resolvers (registry paths, event enum, template ref)

**Size:** M · **Depends on:** `L3-04-02` · **Owns:** `tools/provision/**`

The FROZEN PARTITION rule 2 is *contract-first*: L3 codes against `contracts/**` and never edits it. This task builds the readers. **No path, filename, event type or schema shape may be hard-coded in any later task.**

### Files created

| Path | Contract |
| --- | --- |
| `tools/provision/provision/core/contracts.py` | `product_registry_path(product_id)`, `people_registry_path()`, `event_types()`, `records_writer_workflow()`, `product_template_ref()`, `branch_protection_template()`, `environment_template()`, `codeowners_rules()` — each reads `$CP/contracts/**` and raises `Stop` if unresolvable |
| `tools/provision/tests/test_contracts_resolver.py` | Each resolver raises `Stop` (exit 2) on a fixture with the key absent; each returns the value on a fixture with it present |
| `tools/provision/fixtures/contracts-present/` | Minimal positive fixture |
| `tools/provision/fixtures/contracts-absent/` | Empty directory fixture |

### Behavioural rules

1. Every resolver takes `contracts_root` (default `$CP/contracts`) so tests run against fixtures.
2. A resolver that cannot find its key raises `Stop("contract key <name> is not declared under contracts/")` → exit 2. **It never falls back to a guess.** Section 64.1: where a value is missing, the resolution is denial.
3. `event_types()` returns the closed enum declared for the platform (Section 97.3: *"the enum is declared in `platform.yaml` … control-plane CI rejects any event whose `event_type` is absent from it"*). Every later task that emits an event validates against this set first and STOPs if its type is absent. The types this phase needs, all present in the Section 97.3 taxonomy: `product_created`, `person_added`, `person_role_changed`, `person_departed`, `orphan_detected`, `orphan_resolved`, `onboarding_phase_completed`, `lifecycle_transition`.
4. `product_registry_path()` must resolve to a **directory-per-item** path. If the contract declares a single shared list file, raise `Stop` — the FROZEN PARTITION anti-conflict rule 3 forbids a shared mutable index, and so does the merge model.

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t03 04-t02
# ... write the files ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_contracts_resolver.py -q
cd "$CP" && git add tools/provision
git commit -m "L3-04-03: contract-bound resolvers for registry paths, event enum and templates"
lane_pr 04-t03 "contract-bound resolvers"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Every resolver STOPs on the absent fixture | `cd "$CP/tools/provision" && python -m pytest tests/test_contracts_resolver.py -q >/dev/null && echo OK` | `OK` |
| A2 | No hard-coded registry path anywhere in the package | `cd "$CP/tools/provision" && grep -rn "registries/" provision/ --include='*.py' \| grep -v contracts.py \| wc -l` | `0` |
| A3 | Every event type used in this phase is in the resolved enum | `cd "$CP/tools/provision" && python -m provision --check-event-types \| tail -1` | `EVENT-TYPES: 8/8 DECLARED` |
| A4 | A shared-list registry contract is rejected | `cd "$CP/tools/provision" && python -m pytest tests/test_contracts_resolver.py::test_shared_list_rejected -q >/dev/null && echo OK` | `OK` |
| A5 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && python -m pytest tests/test_contracts_resolver.py -q >/dev/null \
  && [ "$(grep -rn 'registries/' provision/ --include='*.py' | grep -vc contracts.py)" = "0" ] \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-03: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-03: PASS`

### STOP rule

**If `contracts/` does not declare the product registry path, the people registry path, the event-type enum, or the records-writer workflow — do not invent them.** Do not create a file under `registries/`, `schemas/` or `contracts/`; those belong to L1 and L0 and a PR touching them fails the lane-guard check. File the §0.7 blocker with title `BLOCKER L3-04-03: contracts/ does not declare <key>` and the question *"Which contract key carries `<key>`?"*.

---

## L3-04-04 — Idempotent step engine, run ledger, manual-step issue emitter

**Size:** M · **Depends on:** `L3-04-03` · **Owns:** `tools/provision/**`

Section 19.1 permits, explicitly, that *"where the provider offers no automation, tracked manual steps [are] emitted as issues so neither is silently missing"*. This task builds the mechanism that makes a manual step a **tracked artifact**, never a memory.

### Files created

| Path | Contract |
| --- | --- |
| `tools/provision/provision/core/steps.py` | `Step` (id, title, `check()`, `apply()`), `run(steps, mode)`; each step is check-then-apply |
| `tools/provision/provision/core/runstate.py` | Run ledger at `$PROVISION_RUN_DIR/<run-id>/steps.jsonl`; `--resume` replays and skips `done` |
| `tools/provision/provision/core/manualstep.py` | `emit(repo, step_id, title, body, labels)` — idempotent by a `provision-step:<step_id>` marker line |
| `tools/provision/provision/templates/manual-step-issue.md` | Issue body template |
| `tools/provision/tests/test_steps_idempotence.py` | Running the same step list twice produces zero second-run applies |
| `tools/provision/tests/test_manualstep_idempotence.py` | Second `emit()` with the same `step_id` creates no second issue |

### Behavioural rules

1. Every step implements `check()` returning one of `SATISFIED`, `NEEDS_APPLY`, `STRICTER_THAN_DECLARED`, `CONFLICT`.
2. `STRICTER_THAN_DECLARED` → **never apply** (SR-6, invariant 81, Section 53.3). Print `LEVEL-2: <step_id> actual state stricter than declared; not applied` and continue. This is the auto-loosening prohibition of AT-033 implemented in the provisioner rather than only in the reconciler.
3. `CONFLICT` → raise `Stop` (exit 2). Never resolve a conflict by overwriting.
4. In `plan` mode every step runs `check()` only and prints `PLAN <step_id> <state>`.
5. `run()` writes one ledger line per step: `{step_id, state, action, run_id, occurred_at}` with `occurred_at` in UTC with offset.
6. Manual-step issues carry the marker `<!-- provision-step:<step_id> -->` on the first line of the body; `emit()` searches open **and closed** issues for that marker before creating. A closed marker issue counts as satisfied.
7. Manual-step issues are labelled `provision-manual-step` and name the capability required to complete them (`devops` for infrastructure, `platform-admin` for organisation acts — Section 9).

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t04 04-t03
# ... write the files ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_steps_idempotence.py tests/test_manualstep_idempotence.py -q
cd "$CP" && git add tools/provision
git commit -m "L3-04-04: idempotent step engine, run ledger, tracked manual-step issues"
lane_pr 04-t04 "step engine and manual-step tracking"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Second run of an identical step list applies nothing | `cd "$CP/tools/provision" && python -m pytest tests/test_steps_idempotence.py -q >/dev/null && echo OK` | `OK` |
| A2 | `STRICTER_THAN_DECLARED` never applies | `cd "$CP/tools/provision" && python -m pytest tests/test_steps_idempotence.py::test_stricter_not_applied -q >/dev/null && echo OK` | `OK` |
| A3 | Duplicate manual-step emit creates no second issue | `cd "$CP/tools/provision" && python -m pytest tests/test_manualstep_idempotence.py -q >/dev/null && echo OK` | `OK` |
| A4 | Ledger timestamps carry an offset | `grep -o '"occurred_at": "[^"]*"' "$PROVISION_RUN_DIR"/*/steps.jsonl \| grep -cv 'Z"\|+00:00"'` | `0` |
| A5 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && python -m pytest tests/test_steps_idempotence.py tests/test_manualstep_idempotence.py -q >/dev/null \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-04: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-04: PASS`

### STOP rule

**If a step's `check()` cannot distinguish `SATISFIED` from `NEEDS_APPLY` without performing a write — do not write to find out.** Read-then-decide is the only permitted order. File the §0.7 blocker with title `BLOCKER L3-04-04: step <id> has no read-only check path`.

---

## L3-04-05 — create-product step: preflight and repository from template

**Size:** M · **Depends on:** `L3-04-04` · **Owns:** `tools/provision/**`

### Spec basis

Section 19.1 CREATE PRODUCT, line 1: *"repository or repository set from the standard template"*. Section 11.3: *"New repositories are created private, with branch protection applied from the template at creation, no environment access and no third-party app access — safe defaults, activation explicit (Section 64)."* Section 16 / invariant 62 / AT-010: a product may have several repositories; the contract is one, the repositories are many.

### Files created

| Path | Contract |
| --- | --- |
| `tools/provision/provision/steps/preflight.py` | Step `cp-01-preflight` |
| `tools/provision/provision/steps/repo_from_template.py` | Step `cp-02-repo` (runs once per declared repository) |
| `tools/provision/tests/test_preflight.py` | |
| `tools/provision/tests/test_repo_from_template.py` | |

### `cp-01-preflight` — refuses to start unless all of these hold

| Check | Refusal (exit 2) if |
| --- | --- |
| `--product-id` matches `^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$` | malformed |
| `--product-id` is not already present in the product registry | already registered (identifiers are never reused — Section 15.1 `identity.id`: *"stable, never reused"*) |
| `--scaffolding-issue` resolves to an open issue | absent — Section 19.1: *"the Founder's decision record automatically opens the scaffolding request issue, which is the trigger — creation never depends on someone remembering a conversation"* |
| `--decision-record` resolves to a record id | absent (SR-7; Section 26.4) |
| `--conformance-profile` ∈ {`service`,`client-app`,`library`,`batch`,`customer-hosted`,`white-label`,`static-site`} | outside the set (Section 15.7) |
| `--reliability-criticality` ∈ {`low`,`medium`,`high`,`critical`} | outside the set (Section 15.1) |
| `--classification-class` ∈ {`internal`,`experimental`,`commercial`,`strategic`,`regulated`,`legacy`} | outside the set (Section 15.1) |
| Target organisation equals `$PROVISION_SANDBOX_ORG` unless `--i-am-operations` is passed | mismatch |
| Every named repository is absent in the target org | any exists (never adopt silently) |

### `cp-02-repo` — behavioural rules

1. Create each repository with `POST /repos/{template_owner}/{template_repo}/generate`, body `{"owner": org, "name": repo, "private": true, "include_all_branches": false}`. The template ref comes from `contracts.product_template_ref()` (`L3-04-03`) — **never a literal**, because Section 99.2 subsystem E consumes reusable workflows *by pinned tag* and the template must be pinned on the same discipline (invariant 85).
2. Then `PATCH /repos/{org}/{repo}` with **only** `{"private": true, "delete_branch_on_merge": true, "has_issues": true}` — the field allowlist of `L3-04-02` refuses anything else.
3. No third-party app is installed and no environment is created here (Section 11.3 safe defaults).
4. `check()` returns `SATISFIED` when the repository exists, is private, and its generated tree contains `Makefile` — so a resumed run does not re-generate.

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t05 04-t04
# ... write the files ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_preflight.py tests/test_repo_from_template.py -q
cd "$CP" && git add tools/provision
git commit -m "L3-04-05: create-product preflight and repository-from-template step"
lane_pr 04-t05 "create-product: preflight and repo from template"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Preflight refuses a reused product id | `cd "$CP/tools/provision" && python -m pytest tests/test_preflight.py::test_reused_id_refused -q >/dev/null && echo OK` | `OK` |
| A2 | Preflight refuses without a scaffolding issue | `cd "$CP/tools/provision" && python -m pytest tests/test_preflight.py::test_no_scaffolding_issue_refused -q >/dev/null && echo OK` | `OK` |
| A3 | Preflight refuses a non-sandbox org without `--i-am-operations` | `cd "$CP/tools/provision" && python -m pytest tests/test_preflight.py::test_non_sandbox_refused -q >/dev/null && echo OK` | `OK` |
| A4 | Every one of the seven conformance profiles is accepted | `cd "$CP/tools/provision" && python -m provision create-product --list-accepted-profiles \| wc -l` | `7` |
| A5 | Repo step is idempotent (second check returns SATISFIED) | `cd "$CP/tools/provision" && python -m pytest tests/test_repo_from_template.py::test_second_check_satisfied -q >/dev/null && echo OK` | `OK` |
| A6 | Template ref is never a literal | `cd "$CP/tools/provision" && grep -rn "product-template" provision/steps/ \| wc -l` | `0` |
| A7 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && python -m pytest tests/test_preflight.py tests/test_repo_from_template.py -q >/dev/null \
  && [ "$(python -m provision create-product --list-accepted-profiles | wc -l)" -eq 7 ] \
  && [ "$(grep -rc 'product-template' provision/steps/ | awk -F: '{s+=$2} END{print s+0}')" = "0" ] \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-05: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-05: PASS`

### STOP rule

**If a repository with the requested name already exists in the target organisation — do not adopt it, do not rename it, do not delete it (SR-1).** File the §0.7 blocker with title `BLOCKER L3-04-05: target repository already exists` and stop.

---

## L3-04-06 — create-product step: GitHub Team from assignments

**Size:** S · **Depends on:** `L3-04-05` · **Owns:** `tools/provision/**`

### Spec basis

Section 11.2: *"One Team per product, named for the product, containing everyone holding a current assignment on it… **Team membership is derived from the registries and reconciled continuously** — a mismatch between `people.yaml`, `product.yaml` and actual GitHub Team membership fails CI and raises a drift finding (Section 53)."* Section 53.1 row: `product.yaml assignments` vs GitHub Team membership → **Fail CI on the affected repository**.

### Files created

`tools/provision/provision/steps/team.py` (step `cp-03-team`), `tools/provision/tests/test_team_step.py`.

### Behavioural rules

1. `POST /orgs/{org}/teams` with `{"name": product_id, "privacy": "closed"}`. If a team with that slug exists, `check()` returns `SATISFIED` — never create a second.
2. `PUT /orgs/{org}/teams/{slug}/repos/{org}/{repo}` with `{"permission": "push"}` for each declared repository. Write is granted **through Teams**, never directly to a person (Section 11.2), and Write is required — a Read-only cross-reviewer *"fails silently"* (Section 11.1; Section 99.6 secondary risks).
3. Membership is added only for assignment types the registry declares active on this product at creation. **No membership is added for a person whose `people.yaml` `availability` is `departing` or `departed`, or whose `access_status` is `revoked` or `suspended`** (Section 7.1; SIG-02).
4. The step **never removes** a member. Removal is reconciliation's job at Level 3 (Section 53.2) and SR-1 forbids it here.
5. A product with zero `primary_owner` or zero `cross_reviewer` assignments raises `Stop` — that is a Blocking orphan on arrival (Section 12.2 orphan table; SIG-05; invariant 7).

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t06 04-t05
# ... write the files ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_team_step.py -q
cd "$CP" && git add tools/provision
git commit -m "L3-04-06: create-product GitHub Team step, membership derived from registries"
lane_pr 04-t06 "create-product: Team from assignments"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Existing team is not duplicated | `cd "$CP/tools/provision" && python -m pytest tests/test_team_step.py::test_no_duplicate_team -q >/dev/null && echo OK` | `OK` |
| A2 | Departed/revoked people are not added | `cd "$CP/tools/provision" && python -m pytest tests/test_team_step.py::test_inactive_excluded -q >/dev/null && echo OK` | `OK` |
| A3 | Repository permission granted is exactly `push` | `cd "$CP/tools/provision" && grep -c '"permission": "push"' provision/steps/team.py` | `1` |
| A4 | Zero owner or zero cross-reviewer STOPs | `cd "$CP/tools/provision" && python -m pytest tests/test_team_step.py::test_missing_owner_stops -q >/dev/null && echo OK` | `OK` |
| A5 | No removal call exists | `cd "$CP/tools/provision" && grep -rn "DELETE" provision/steps/team.py \| wc -l` | `0` |
| A6 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && python -m pytest tests/test_team_step.py -q >/dev/null \
  && [ "$(grep -c 'DELETE' provision/steps/team.py || true)" = "0" ] \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-06: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-06: PASS`

### STOP rule

**If the registry declares an assignment naming a `github_login` that does not exist in the organisation — do not invite them from this step.** Organisation invitation is `add-person`'s act (Section 12.1), and doing it here would grant access outside the person lifecycle. File the §0.7 blocker with title `BLOCKER L3-04-06: assignment names a person with no organisation membership`.

---

## L3-04-07 — create-product step: generated CODEOWNERS, humans-only negative check

**Size:** M · **Depends on:** `L3-04-06` · **Owns:** `tools/provision/**`

### Spec basis, quoted because every clause is load-bearing

Section 11.3: *"**Require review from Code Owners.** CODEOWNERS is generated to contain human identities only — no machine account ever appears in it — so a machine-account approval can never satisfy branch protection: the required Code Owner review must come from a human. The Phase 1 completion check verifies this negatively."*

Section 11.3, routing: *"`verification/` is owned by whoever holds `verification_responsibility`. `product.yaml`, migration directories and CI workflow files are owned by the Team Lead role. Product source paths are owned by the product Team."*

Section 53.1, the independent control verifier: *"asserting that no machine identity appears in any CODEOWNERS file in any repository"*. Section 37.3 makes the same prohibition architectural rather than policy.

### Files created

| Path | Contract |
| --- | --- |
| `tools/provision/provision/steps/codeowners.py` | Step `cp-04-codeowners` |
| `tools/provision/provision/codeowners/render.py` | Pure function: `(registries, repo_role) -> CODEOWNERS text` |
| `tools/provision/provision/codeowners/negative_check.py` | The negative check, runnable standalone |
| `tools/provision/tests/test_codeowners_render.py` | Golden-file tests, one per repository role |
| `tools/provision/tests/test_codeowners_negative.py` | The negative check fails on every seeded machine identity |
| `tools/provision/fixtures/codeowners/expected-primary.CODEOWNERS` | Golden file |

### Rendering rules (implement exactly; no other line may be emitted)

```
# GENERATED BY tools/provision — DO NOT EDIT.
# Source: <product registry path> @ <commit sha>
# Basis: Section 11.3. Human identities only (no machine account, ever).

*                        @<org>/<product-id>
/product.yaml            @<org>/<team-lead-team>
/migrations/             @<org>/<team-lead-team>
/.github/workflows/      @<org>/<team-lead-team>
/verification/           @<verification_responsibility github_login>
```

> **Note:** This CODEOWNERS entry for `/migrations/` duplicates `L5-01`'s generator. File as a new register entry — this is a PARTITION rule 1 question, not REG-040's.

1. Order is fixed and the last matching rule wins in GitHub's CODEOWNERS semantics, so the specific paths follow the catch-all. Do not reorder.
2. The Team Lead org-wide Team slug comes from the contract resolver, not a literal (Section 11.2: *"Two organisation-wide Teams grant Write to the Team Lead role and the QA role"*).
3. `verification/` owner is the person holding the `verification_responsibility` assignment (Section 10.1). If none is assigned, raise `Stop` — that is orphan type *"Verification responsibility unassigned"* (Section 12.2) and shipping a repository without it violates invariant 1's neighbourhood.
4. `check()` compares the rendered text byte-for-byte against the file in the repository. Any difference where the file lacks the `GENERATED BY` header is `CONFLICT` (hand-edited — Section 53.1 row: *"Regenerate; alert if hand-edited"* — the provisioner raises `Stop`; regeneration is reconciliation's Level-3 act, not the provisioner's).

### The negative check (this is the whole point of the task)

`provision`'s `negative_check.py` takes a CODEOWNERS text plus the organisation and asserts, for **every** principal:

* a `@user` principal resolves to an entry in the people registry, **and**
* a `@org/team` principal expands to members that **all** resolve to entries in the people registry.

Any principal that does not resolve to a people-registry entry fails the check. A machine account has no `people.yaml` entry by construction (Section 7 is an *operational identity* registry for people), so this test is the negative verification Section 11.3 demands, and it holds transitively through Teams — which a naive "no known bot names" check would not.

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t07 04-t06
# ... write the files ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_codeowners_render.py tests/test_codeowners_negative.py -q
cd "$CP" && git add tools/provision
git commit -m "L3-04-07: generated CODEOWNERS with transitive humans-only negative check"
lane_pr 04-t07 "create-product: generated CODEOWNERS"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Rendered output matches the golden file byte-for-byte | `cd "$CP/tools/provision" && python -m pytest tests/test_codeowners_render.py -q >/dev/null && echo OK` | `OK` |
| A2 | A direct machine principal fails the negative check | `cd "$CP/tools/provision" && python -m pytest tests/test_codeowners_negative.py::test_direct_machine_fails -q >/dev/null && echo OK` | `OK` |
| A3 | A machine hidden **inside a Team** fails the negative check | `cd "$CP/tools/provision" && python -m pytest tests/test_codeowners_negative.py::test_machine_in_team_fails -q >/dev/null && echo OK` | `OK` |
| A4 | Hand-edited CODEOWNERS is a `CONFLICT`, not an overwrite | `cd "$CP/tools/provision" && python -m pytest tests/test_codeowners_render.py::test_hand_edited_conflicts -q >/dev/null && echo OK` | `OK` |
| A5 | Missing `verification_responsibility` STOPs | `cd "$CP/tools/provision" && python -m pytest tests/test_codeowners_render.py::test_no_verification_owner_stops -q >/dev/null && echo OK` | `OK` |
| A6 | Rendered file carries exactly five rule lines | `cd "$CP/tools/provision" && python -m provision verify-scaffold --render-codeowners-fixture \| grep -c '^[*/]'` | `5` |
| A7 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && python -m pytest tests/test_codeowners_render.py tests/test_codeowners_negative.py -q >/dev/null \
  && [ "$(python -m provision verify-scaffold --render-codeowners-fixture | grep -c '^[*/]')" -eq 5 ] \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-07: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-07: PASS`

### STOP rule

**If the negative check cannot expand a Team's membership — because the credential lacks `members: read` — do not skip the check and do not fall back to a name-pattern heuristic.** A CODEOWNERS check that cannot see through Teams is a gate that appears to be working and is not (Section 11.1). File the §0.7 blocker with title `BLOCKER L3-04-07: cannot expand team membership for the CODEOWNERS negative check` and route the question to D-L3-04-02.

---

## L3-04-08 — create-product step: branch protection from template

**Size:** M · **Depends on:** `L3-04-07` · **Owns:** `tools/provision/**`

### Spec basis — Section 11.3, transcribed as the checklist this step applies

| # | Rule | Applied as |
| --- | --- | --- |
| 1 | Require a pull request before merging | `required_pull_request_reviews` present |
| 2 | Require at least 1 approving review | `required_approving_review_count: 1` |
| 3 | Require review from Code Owners | `require_code_owner_reviews: true` |
| 4 | Require approval of the most recent reviewable push | `require_last_push_approval: true` — *"mechanically prevents an author's own approval"*, the enforcement behind invariant 9 |
| 5 | Dismiss stale approvals when new commits are pushed | `dismiss_stale_reviews: true` |
| 6 | Require status checks to pass | the eight checks below |
| 7 | Require branches to be up to date before merging | `strict: true` |
| 8 | Block force pushes and deletions on the default branch | `allow_force_pushes: false`, `allow_deletions: false` |
| 9 | Apply rules to administrators | `enforce_admins: true` |

The eight required status checks, verbatim from Section 11.3 — *"tests, build, security scan, contract validation, reviewer matrix validation, parity check, verification contract, and `control-plane/blocking-drift`"*:

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
cat > "$CP/tools/provision/provision/protection/required-checks.yaml" <<'EOF'
# Section 11.3, required status checks. Names are resolved from contracts/ at run
# time; this file fixes the SET, not the strings. A missing name is a STOP.
version: 1
required_status_checks:
  - tests
  - build
  - security-scan
  - contract-validation
  - reviewer-matrix-validation
  - parity-check
  - verification-contract
  - control-plane/blocking-drift   # the check the reconciler holds at failure
                                   # while Blocking-class drift is open (53.2)
EOF
```

### Files created

`tools/provision/provision/steps/protection.py` (step `cp-05-protection`), `tools/provision/provision/protection/required-checks.yaml`, `tools/provision/provision/protection/compare.py`, `tools/provision/tests/test_protection_apply.py`, `tools/provision/tests/test_protection_stricter_only.py`.

### Behavioural rules

1. Read the branch-protection template through `contracts.branch_protection_template()`. **Never hard-code the JSON body** — Section 53.1 compares *"Branch protection template"* against *"Actual branch protection"*, and a second copy of the template inside the provisioner is a second source of truth that will drift.
2. `compare.py` classifies actual-vs-template per field into `EQUAL`, `WEAKER`, `STRICTER`. If **any** field is `STRICTER`, the whole step returns `STRICTER_THAN_DECLARED` and applies nothing (SR-6; invariant 81; AT-033: *"Reconciliation presented with a stricter-than-declared production control raises it for human review and does not relax it"* — the provisioner honours the same rule).
3. Apply via `PUT /repos/{org}/{repo}/branches/{default}/protection`. Never `DELETE .../protection` (SR-1).
4. On a mismatch remaining after apply, exit 3 with `DRIFT: branch-protection <field>` — Section 53.1 classifies branch-protection mismatch as *"Alert immediately; block deployment on the affected repository"*.
5. If a required status-check name is not declared in `contracts/`, raise `Stop`. A protection rule requiring a check that no workflow emits blocks every merge forever; a protection rule silently missing a check is Section 11.4's silent-gate failure. Both are refused.

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t08 04-t07
# ... write the files ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_protection_apply.py tests/test_protection_stricter_only.py -q
cd "$CP" && git add tools/provision
git commit -m "L3-04-08: branch protection from template with stricter-only comparison"
lane_pr 04-t08 "create-product: branch protection"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | All nine Section 11.3 rules are asserted | `cd "$CP/tools/provision" && python -m provision verify-scaffold --list-protection-rules \| wc -l` | `9` |
| A2 | Exactly eight required status checks | `cd "$CP/tools/provision" && python -c "import yaml;print(len(yaml.safe_load(open('provision/protection/required-checks.yaml'))['required_status_checks']))"` | `8` |
| A3 | `control-plane/blocking-drift` is one of them | `cd "$CP/tools/provision" && grep -c 'control-plane/blocking-drift' provision/protection/required-checks.yaml` | `1` |
| A4 | A stricter actual state is never overwritten | `cd "$CP/tools/provision" && python -m pytest tests/test_protection_stricter_only.py -q >/dev/null && echo OK` | `OK` |
| A5 | Template body is not duplicated in code | `cd "$CP/tools/provision" && grep -rn "require_last_push_approval" provision/ --include='*.py' \| wc -l` | `0` |
| A6 | Undeclared check name STOPs | `cd "$CP/tools/provision" && python -m pytest tests/test_protection_apply.py::test_undeclared_check_stops -q >/dev/null && echo OK` | `OK` |
| A7 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && [ "$(python -m provision verify-scaffold --list-protection-rules | wc -l)" -eq 9 ] \
  && [ "$(python -c "import yaml;print(len(yaml.safe_load(open('provision/protection/required-checks.yaml'))['required_status_checks']))")" -eq 8 ] \
  && python -m pytest tests/test_protection_apply.py tests/test_protection_stricter_only.py -q >/dev/null \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-08: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-08: PASS`

### STOP rule

**If the GitHub plan tier refuses branch protection on the private repository — do not create the repository public to make protection work, and do not proceed without protection.** Section 11.4 records this as *"the one item that forces a paid plan"* and Section 99.6 risk 5 names silent tier failure as a top build risk. File the §0.7 blocker with title `BLOCKER L3-04-08: branch protection unavailable on this plan tier`.

---

## L3-04-09 — create-product step: environments, deployment branch and tag policy, scoped secrets

**Size:** M · **Depends on:** `L3-04-08` · **Owns:** `tools/provision/**`

### Spec basis

Section 19.1: *"environments: development, staging, production"*. Section 33.4: *"**GitHub Environments** — `development`, `staging`, `production` — with environment-scoped secrets. **Every environment carries a deployment branch and tag policy, applied from the template at product creation**: `staging` and `production` accept deployments from the default branch and from protected release tags only, and from no other ref."*

Section 33.4 states exactly why: *"Without it, any Write holder … pushes a branch carrying a workflow that declares `environment: production`, and GitHub hands that job the environment's secrets from an unreviewed ref."* Section 11.4 / D73: environment **required reviewers** are Enterprise-only and are **not** depended on; production approval is the Section 27.2 workflow-identity gate.

### Files created

`tools/provision/provision/steps/environments.py` (step `cp-06-environments`), `tools/provision/provision/environments/policy.py`, `tools/provision/provision/templates/secret-manual-step.md`, `tools/provision/tests/test_environments.py`.

### Behavioural rules

1. Create exactly three environments via `PUT /repos/{org}/{repo}/environments/{name}` for `development`, `staging`, `production`. No fourth. A `white-label` product's per-deployment environment list (Section 15.7) is a **configure-stage** item and is emitted as a CONFIGURE checklist row by `L3-04-11`, not created here.
2. For `staging` and `production`, set `deployment_branch_policy: {"protected_branches": false, "custom_branch_policies": true}` and then `POST .../deployment-branch-policies` twice: once for the default branch name, once with `type: tag` for the protected release-tag pattern taken from `contracts.environment_template()`.
3. For `development`, apply the template's declared policy if the template declares one; otherwise apply none and record `LEVEL-1: development environment carries the platform default policy`. Section 33.4 binds `staging` and `production` by name; the provisioner applies exactly what is written and records the rest rather than inventing a rule.
4. **No secret value is created, read, echoed, logged or defaulted** (SR-2). For each secret name the environment template declares as required, emit one manual-step issue per environment titled `Set <ENV> secret <NAME> for <product-id>`, labelled `provision-manual-step`, naming the `devops` capability (Section 9) and citing Section 40.1's tier boundary in the body. Section 19.1 explicitly sanctions this shape: *"tracked manual steps emitted as issues so neither is silently missing"*.
5. No environment reviewer is configured, and the step **asserts** none exists: relying on one would build the production gate on an Enterprise-only feature (Section 11.4, D73). If a reviewer is present on a pre-existing environment, that is `STRICTER_THAN_DECLARED` → do not remove it (SR-1, SR-6), record Level 2.
6. `check()` returns `SATISFIED` only when all three environments exist **and** `staging` and `production` each carry both branch-policy entries. A missing tag policy is not a partial pass — Section 53.1 lists *"Environment deployment branch and tag policy"* mismatch as *"Alert immediately; block deployment on the affected repository"*.

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t09 04-t08
# ... write the files ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_environments.py -q
cd "$CP" && git add tools/provision
git commit -m "L3-04-09: three environments with deployment branch and tag policy; secrets by tracked manual step only"
lane_pr 04-t09 "create-product: environments and deployment policy"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Exactly three environments are created | `cd "$CP/tools/provision" && python -m provision verify-scaffold --list-environments \| tr '\n' ' '` | `development production staging ` |
| A2 | staging and production each get two branch-policy entries | `cd "$CP/tools/provision" && python -m pytest tests/test_environments.py::test_two_policies_each -q >/dev/null && echo OK` | `OK` |
| A3 | No secret-writing code path exists | `cd "$CP/tools/provision" && grep -rn "/secrets" provision/ --include='*.py' \| grep -v security/ \| wc -l` | `0` |
| A4 | A secret manual-step issue is emitted per required name per environment | `cd "$CP/tools/provision" && python -m pytest tests/test_environments.py::test_secret_manual_steps -q >/dev/null && echo OK` | `OK` |
| A5 | A missing tag policy is not `SATISFIED` | `cd "$CP/tools/provision" && python -m pytest tests/test_environments.py::test_missing_tag_policy_not_satisfied -q >/dev/null && echo OK` | `OK` |
| A6 | An existing environment reviewer is never removed | `cd "$CP/tools/provision" && python -m pytest tests/test_environments.py::test_reviewer_not_removed -q >/dev/null && echo OK` | `OK` |
| A7 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && [ "$(python -m provision verify-scaffold --list-environments | wc -l)" -eq 3 ] \
  && [ "$(grep -rn '/secrets' provision/ --include='*.py' | grep -vc security/)" = "0" ] \
  && python -m pytest tests/test_environments.py -q >/dev/null \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-09: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-09: PASS`

### STOP rule

**If deployment branch policies are unavailable on the target plan — do not create the environments anyway.** Section 33.4 is explicit that deployment branch policies *are* available on the Team plan and are not the Enterprise feature Section 11.4 excludes; an environment holding production credentials without a ref restriction *"holds production credentials behind nothing"*. File the §0.7 blocker with title `BLOCKER L3-04-09: deployment branch policy unavailable` and stop.

---

## L3-04-10 — create-product step: scaffold conformance (ten commands, three endpoints, verification skeleton)

**Size:** M · **Depends on:** `L3-04-05` · **Owns:** `tools/provision/**`

### Spec basis

Section 33.1, the eight commands and the required-file list; Section 41.2, the three endpoints; Section 31.1, the `verification/` structure; Section 15.7, profile-aware evidence — *"a `client-app` product is not failed for lacking a health endpoint"*.

### Files created

| Path | Contract |
| --- | --- |
| `tools/provision/provision/steps/scaffold.py` | Step `cp-07-scaffold` |
| `tools/provision/provision/conformance/required_files.yaml` | Verbatim below (input to D-L3-04-03) |
| `tools/provision/provision/conformance/make_targets.yaml` | Verbatim below |
| `tools/provision/provision/conformance/endpoints.yaml` | Verbatim below |
| `tools/provision/provision/ops/verify_scaffold.py` | `provision verify-scaffold --repo <org/repo> --profile <profile>` |
| `tools/provision/tests/test_verify_scaffold.py` | One passing fixture and one fixture missing each item |

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
cat > "$CP/tools/provision/provision/conformance/make_targets.yaml" <<'EOF'
# Section 33.1, the Local Environment Contract. Ten commands, every repository.
# "Someone moving between products must not learn a new setup."
version: 1
targets:
  - {name: setup,     behaviour: "Install dependencies, create .env.local from .env.example, prepare local services"}
  - {name: dev,       behaviour: "Start the application and all local dependencies"}
  - {name: test,      behaviour: "Run the full automated verification suite"}
  - {name: uat-local, behaviour: "Start with seeded data ready for manual UAT"}
  - {name: migrate,   behaviour: "Apply database migrations"}
  - {name: reset,     behaviour: "Tear down and rebuild local state from scratch"}
  - {name: health,    behaviour: "Report local service health"}
  - {name: parity,    behaviour: "Compare local configuration schema against staging and production declarations"}
  - {name: deploy,    behaviour: "Deploy the application to the configured target environment"}
  - {name: restore,   behaviour: "Restore local state from a known-good backup or snapshot"}
EOF

cat > "$CP/tools/provision/provision/conformance/endpoints.yaml" <<'EOF'
# Section 41.2, the three required endpoints. Applies where conformance_profile
# exposes the service interface: `service` (default) and `white-label`.
# Other profiles meet the Section 15.7 equivalent evidence instead and are
# NEVER failed for lacking an endpoint their shape cannot serve.
version: 1
applies_to_profiles: [service, white-label]
endpoints:
  - {path: /health,  provides: "Liveness plus dependency health, distinguishing internal from external failure",
     product_yaml_field: observability.health_endpoint}
  - {path: /version, provides: "Deployed artifact digest and build metadata",
     product_yaml_field: observability.version_endpoint}
  - {path: /metrics, provides: "Prometheus format",
     product_yaml_field: observability.metrics, expected_value: prometheus}
required_field:
  # 41.2: "because the field is required, a product cannot reach launch readiness
  # without answering the question"
  - {field: observability.telemetry_exposure, allowed: [private-authenticated, public],
     note: "estate declared posture is private-authenticated; `public` is a recorded Founder decision"}
EOF

cat > "$CP/tools/provision/provision/conformance/required_files.yaml" <<'EOF'
# Section 33.1: "Required files in every repository". Presence is CHECKED, not assumed.
# seed_data and migration_directory paths are the provisional default of
# DECISION REQUIRED D-L3-04-03 until L0 settles them in product-template.
version: 1
files:
  - .env.example
  - docker-compose.dev.yml
  - Makefile
  - AGENTS.md
directories:
  - verification/
  - seed/            # D-L3-04-03 provisional
  - migrations/      # D-L3-04-03 provisional
one_of:
  - [product.yaml, .product-pointer]   # "either product.yaml or a pointer to the product it belongs to"
verification_skeleton:                  # Section 31.1
  - verification/contract.yaml
  - verification/automated/
  - verification/uat.md
  - verification/smoke/
EOF
```

### Behavioural rules

1. `verify-scaffold` clones the repository shallowly to a temp dir under `$PROVISION_RUN_DIR` and runs three groups: files, make targets, endpoints.
2. Make targets: for each of the ten, run `make -C <clone> -n <target>`. `-n` prints without executing; a non-zero exit means the target does not exist. Report `MAKE-TARGET <name> MISSING` and fail.
3. Endpoints: applied **only** when `conformance_profile` ∈ `applies_to_profiles`. For other profiles print `ENDPOINTS: n/a for profile <p>` and pass. This is Section 15.7 honoured literally, and AT-009 depends on it.
4. Verification skeleton: all four paths of Section 31.1 must exist. Additionally, `verification/contract.yaml` must declare at least one **seeded-defect case** (Section 31.2: *"A verification contract that cannot fail is not a contract"*). A contract with none fails with `SEEDED-DEFECT: ABSENT` — a scaffold that ships without it produces SIG-18 on day one.
5. `performance` mechanism: if `classification.reliability_criticality` is `high` or `critical`, `verification/contract.yaml` must declare the performance mechanism (Section 31.3: *"the verification-contract check in CI fails if it is absent"*). Otherwise it is optional.
6. `verify-scaffold` exits 0 on full pass, 3 on any missing item, and prints one line per failure. It never repairs.

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t10 04-t05
# ... write the files ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_verify_scaffold.py -q
cd "$CP" && git add tools/provision
git commit -m "L3-04-10: scaffold conformance - ten make targets, three endpoints, verification skeleton"
lane_pr 04-t10 "create-product: scaffold conformance"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Exactly ten make targets are checked | `cd "$CP/tools/provision" && python -m provision verify-scaffold --list-targets \| tr '\n' ' '` | `setup dev test uat-local migrate reset health parity deploy restore ` |
| A2 | Exactly three endpoints are checked | `cd "$CP/tools/provision" && python -m provision verify-scaffold --list-endpoints \| tr '\n' ' '` | `/health /version /metrics ` |
| A3 | A `client-app` profile is not failed for endpoints | `cd "$CP/tools/provision" && python -m provision verify-scaffold --repo fixture --profile client-app \| grep -c 'ENDPOINTS: n/a for profile client-app'` | `1` |
| A4 | A missing make target fails with exit 3 | `cd "$CP/tools/provision" && python -m pytest tests/test_verify_scaffold.py::test_missing_target_exit3 -q >/dev/null && echo OK` | `OK` |
| A5 | A contract with no seeded-defect case fails | `cd "$CP/tools/provision" && python -m pytest tests/test_verify_scaffold.py::test_no_seeded_defect_fails -q >/dev/null && echo OK` | `OK` |
| A6 | `high` criticality without a performance mechanism fails | `cd "$CP/tools/provision" && python -m pytest tests/test_verify_scaffold.py::test_perf_required_for_high -q >/dev/null && echo OK` | `OK` |
| A7 | The verifier never writes to the target repo | `cd "$CP/tools/provision" && grep -rn "call(" provision/ops/verify_scaffold.py \| grep -vc "'GET'"` | `0` |
| A8 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && [ "$(python -m provision verify-scaffold --list-targets | wc -l)" -eq 10 ] \
  && [ "$(python -m provision verify-scaffold --list-endpoints | wc -l)" -eq 3 ] \
  && python -m pytest tests/test_verify_scaffold.py -q >/dev/null \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-10: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-10: PASS`

### STOP rule

**If `product-template` does not carry all ten make targets, or does not carry the Section 31.1 verification skeleton — do not add them to the generated repository from `tools/provision`.** `product-template` is not an L3-owned repository, and patching each generated repo instead of the template is exactly the hand-editing Section 12.6 calls a platform defect. File the §0.7 blocker with title `BLOCKER L3-04-10: product-template is missing <item>` and route it to L0 alongside D-L3-04-03.

---

## L3-04-11 — create-product step: registry entry, CONFIGURE checklist, alert channel and support mailbox

**Size:** M · **Depends on:** `L3-04-04`, `L3-04-10` · **Owns:** `tools/provision/**`

### Spec basis

Section 19.1: *"alert channel and support intake mailbox created — or, where the provider offers no automation, tracked manual steps emitted as issues so neither is silently missing"*, and the CONFIGURE stage: *"the scaffold emits a CONFIGURE checklist issue enumerating every item below"*. Section 26.4: registry edits travel the registry-change lane — CI schema validation plus owner review plus a linked decision record where required, and *"an **authority delta** … fails CI without a linked decision record ID in the same commit"*.

### Files created

`tools/provision/provision/steps/registry_entry.py` (step `cp-08-registry`), `tools/provision/provision/steps/checklists.py` (step `cp-09-configure-checklist`), `tools/provision/provision/templates/configure-checklist.md`, `tools/provision/tests/test_registry_entry.py`, `tools/provision/tests/test_configure_checklist.py`.

### Registry-entry rules

1. The entry is written to the **directory-per-item** path returned by `contracts.product_registry_path(product_id)` — one file, never an append to a shared index (FROZEN PARTITION anti-conflict rule 3).
2. The write is a **pull request** on the control-plane repository: `POST /git/refs` → `PUT /contents/<path>` → `POST /pulls`. Never a direct push. Section 40.1 is unambiguous: on the control-plane repository *"**No bypass actor exists**"*.
3. The PR body carries the `--decision-record` id and the `--scaffolding-issue` link. A create-product PR adding assignments **is** an authority delta (it confers Write through the product Team), so the decision-record id is mandatory (Section 26.4).
4. The step **does not** apply the registry to the estate. Section 26.4: *"a merged registry change is applied by the next reconciliation run to the declared canary set only"*. The provisioner declares; the reconciler applies. Print `HANDOFF: registry entry declared; reconciliation applies on the next run`.
5. `check()` returns `SATISFIED` if the path already exists on `main` **or** an open PR already adds it. Re-running never opens a second PR.

### CONFIGURE checklist — one row per Section 19.1 CONFIGURE item, no more, no fewer

```
environments · verification contract · observability · backups
· classification · budget band · support intake
```

The issue body renders exactly these seven rows plus, per Section 19.1, the note that `infrastructure.monthly_budget_band` is *"set by the Founder as a provisional estimate, refined at the first cost review — Section 50"*. Each row names the capability that closes it (`devops`, `verification`, or Founder-class per Section 9) and links the product registry path.

### Alert channel and support intake mailbox

1. `observability.alert_channel` and `operations.intake_channel` are declared fields (Section 15.1). The step reads them from the pending registry entry.
2. Where the messaging or mail provider exposes no API the CLI is allowed to call, emit one manual-step issue each, per Section 19.1. **Both must exist by the end of scaffolding, as an artifact or as a tracked issue — never as neither.** The step exits 3 if either is absent from both the platform and the manual-step set.
3. The intake channel is an operational asset with a named owner (Section 22.2, Section 49.1). Emit a manual-step row asking L5's asset-inventory owner to record it — L3 does not write `assets/**`.

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t11 04-t10
# ... write the files ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_registry_entry.py tests/test_configure_checklist.py -q
cd "$CP" && git add tools/provision
git commit -m "L3-04-11: product registry entry by PR, CONFIGURE checklist, alert channel and intake mailbox tracking"
lane_pr 04-t11 "create-product: registry entry and CONFIGURE checklist"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Registry write is a PR, never a direct push | `cd "$CP/tools/provision" && grep -c "POST', '/repos/\*/\*/pulls" provision/steps/registry_entry.py \|\| grep -c "'/pulls'" provision/steps/registry_entry.py` | `1` |
| A2 | Missing `--decision-record` STOPs | `cd "$CP/tools/provision" && python -m pytest tests/test_registry_entry.py::test_missing_decision_record_stops -q >/dev/null && echo OK` | `OK` |
| A3 | Re-run opens no second PR | `cd "$CP/tools/provision" && python -m pytest tests/test_registry_entry.py::test_no_second_pr -q >/dev/null && echo OK` | `OK` |
| A4 | The CONFIGURE checklist has exactly seven rows | `cd "$CP/tools/provision" && grep -c '^- \[ \] ' provision/templates/configure-checklist.md` | `7` |
| A5 | Both alert channel and intake mailbox are accounted for | `cd "$CP/tools/provision" && python -m pytest tests/test_configure_checklist.py::test_channel_and_mailbox_accounted -q >/dev/null && echo OK` | `OK` |
| A6 | Step does not apply state to the estate | `cd "$CP/tools/provision" && python -m provision create-product --explain-step cp-08-registry \| grep -c 'HANDOFF: registry entry declared'` | `1` |
| A7 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && [ "$(grep -c '^- \[ \] ' provision/templates/configure-checklist.md)" -eq 7 ] \
  && python -m pytest tests/test_registry_entry.py tests/test_configure_checklist.py -q >/dev/null \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-11: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-11: PASS`

### STOP rule

**If `contracts/` declares the product registry as a single shared file rather than a directory-per-item — do not write to it.** A shared mutable index breaks the merge model (FROZEN PARTITION anti-conflict rule 3) and would make two concurrent create-product runs conflict. File the §0.7 blocker with title `BLOCKER L3-04-11: product registry contract is a shared list, not directory-per-item` and route to L1 via L0.

---

## L3-04-12 — create-product step: surface-registration verifier (no hand-edited dashboards)

**Size:** M · **Depends on:** `L3-04-11` · **Owns:** `tools/provision/**`

### Spec basis — the sentence this task exists to enforce

Section 19.1: *"**Automatic discovery is mandatory.** A new product must appear in the portfolio board, Grafana, Scorecard, DevLake, the reviewer matrix and the dependency graph without anyone hand-editing a dashboard. Every one of those surfaces enumerates from the product registry. If a human must edit a dashboard to add a product, that is a defect in the operating system, not a task."*

Also: Section 11 (*"Repositories are enumerated dynamically from the product registry. No workflow, dashboard or script contains a hard-coded list of repository names"*), invariant 52, AT-001 (*"No dashboard, workflow or script contains a product list"*), Section 20.2 (the dependency graph is a query over declarations — *"No graph database is introduced"*), Section 92.3 (dashboards are provisioned JSON in git).

**This task adds no registration call. Registration is a consequence of the registry entry.** The task builds the verifier that proves it.

### Files created

`tools/provision/provision/steps/surfaces.py` (step `cp-10-surfaces`), `tools/provision/provision/ops/verify_surfaces.py`, `tools/provision/provision/surfaces/surfaces.yaml`, `tools/provision/tests/test_verify_surfaces.py`.

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
cat > "$CP/tools/provision/provision/surfaces/surfaces.yaml" <<'EOF'
# The six surfaces Section 19.1 names. Each must ENUMERATE from the product
# registry. This file declares what to assert, never a product list.
version: 1
surfaces:
  - {id: portfolio-board,   enumerates_from: product_registry, live_probe: board_items}
  - {id: grafana,           enumerates_from: product_registry, live_probe: dashboard_variable}
  - {id: scorecard,         enumerates_from: product_registry, live_probe: scan_targets}
  - {id: devlake,           enumerates_from: product_registry, live_probe: ingest_connections}
  - {id: reviewer-matrix,   enumerates_from: product_registry, live_probe: matrix_rows}
  - {id: dependency-graph,  enumerates_from: product_registry, live_probe: graph_nodes}
EOF
```

### The two checks

**Static (always runs, no live infrastructure needed).** For every product id in the registry, grep the whole `control-plane` working tree for a literal occurrence of that id outside the registry directory itself and outside `records/`/`events/`. Any hit in a dashboard JSON, workflow, script or config file is a **defect**, reported as:

```
HARD-CODED-PRODUCT: <path>:<line> contains product id '<id>'
```

and exits 3. This is AT-001 and invariant 52 made mechanical. It is the single cheapest guard against the failure Section 19.1 calls a defect, and it runs with no dashboard server in existence.

**Live (`--live`).** For each surface, resolve its enumeration source from the surface's own provisioned configuration and assert it equals the product registry path from `contracts.product_registry_path`. Then probe the surface for the new product id. If a surface is unreachable, print `SURFACE <id> UNREACHABLE` and exit 3 — **never** print a pass. Section 92.3 and Section 64.2 both require visible degradation; a green tick for an unreachable surface is worse than no tick.

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t12 04-t11
# ... write the files ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_verify_surfaces.py -q
cd "$CP" && python tools/provision/-m 2>/dev/null; cd "$CP/tools/provision" && python -m provision verify-surfaces --static --root "$CP"
cd "$CP" && git add tools/provision
git commit -m "L3-04-12: surface-registration verifier; hard-coded product list is a build failure"
lane_pr 04-t12 "create-product: surface-registration verifier"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Exactly six surfaces are asserted | `cd "$CP/tools/provision" && python -m provision verify-surfaces --list \| wc -l` | `6` |
| A2 | The control-plane tree contains no hard-coded product id | `cd "$CP/tools/provision" && python -m provision verify-surfaces --static --root "$CP" \| tail -1` | `SURFACES-STATIC: 0 HARD-CODED` |
| A3 | A seeded hard-coded id is detected | `cd "$CP/tools/provision" && python -m pytest tests/test_verify_surfaces.py::test_seeded_hardcode_detected -q >/dev/null && echo OK` | `OK` |
| A4 | An unreachable surface never reports pass | `cd "$CP/tools/provision" && python -m pytest tests/test_verify_surfaces.py::test_unreachable_is_failure -q >/dev/null && echo OK` | `OK` |
| A5 | The step makes no surface-specific write call | `cd "$CP/tools/provision" && grep -rn "call(" provision/steps/surfaces.py \| grep -vc "'GET'"` | `0` |
| A6 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && [ "$(python -m provision verify-surfaces --list | wc -l)" -eq 6 ] \
  && [ "$(python -m provision verify-surfaces --static --root "$CP" | tail -1)" = "SURFACES-STATIC: 0 HARD-CODED" ] \
  && python -m pytest tests/test_verify_surfaces.py -q >/dev/null \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-12: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-12: PASS`

### STOP rule

**If the static check reports `HARD-CODED-PRODUCT` in a path outside `tools/provision/**` — do not fix it.** That path belongs to another lane and a PR touching it fails the lane-guard check. File the §0.7 blocker with title `BLOCKER L3-04-12: hard-coded product list found in <path>` quoting the exact `path:line`, and route it to the owning lane through L0. Note in the body that this is the Section 19.1 defect condition, not a task.

---

## L3-04-13 — `provision create-product` orchestrator and AT-001 rehearsal

**Size:** L · **Depends on:** `L3-04-05` … `L3-04-12` · **Owns:** `tools/provision/**`

### The literal CLI signature (fixed; no task may extend it)

```
provision create-product
  --product-id            <slug>                       # ^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$
  --display-name          <"Human Readable Name">
  --conformance-profile   service|client-app|library|batch|customer-hosted|white-label|static-site
  --classification-class  internal|experimental|commercial|strategic|regulated|legacy
  --reliability-criticality low|medium|high|critical
  --business-criticality  high|medium|low
  --repositories          <name>:<role>:<deploys>[,<name>:<role>:<deploys>...]
  --escalation            team_lead
  --scaffolding-issue     <issue-url>                  # Section 19.1 trigger
  --decision-record       DEC-YYYY-MM-DD-NNN           # Section 26.4
  --mode                  plan|apply                   # default: plan  (SR-7)
  [--resume]                                           # replay the run ledger
  [--i-am-operations]                                  # required for a non-sandbox org
```

### The step order (fixed; the orchestrator runs exactly these ten, in this order)

| # | Step id | From task | Section 19.1 line it satisfies |
| --- | --- | --- | --- |
| 1 | `cp-01-preflight` | T05 | the trigger, the executor, the identity rules |
| 2 | `cp-02-repo` | T05 | *repository or repository set from the standard template* |
| 3 | `cp-03-team` | T06 | *GitHub Team* |
| 4 | `cp-04-codeowners` | T07 | *CODEOWNERS generated from assignments* |
| 5 | `cp-05-protection` | T08 | *branch protection from template* |
| 6 | `cp-06-environments` | T09 | *environments: development, staging, production* + scoped secrets |
| 7 | `cp-07-scaffold` | T10 | *CI workflows … verification/ skeleton … the eight commands … health, version and metrics endpoints* |
| 8 | `cp-08-registry` | T11 | *product.yaml at current contract_version* + the registry entry |
| 9 | `cp-09-configure-checklist` | T11 | the CONFIGURE checklist issue, alert channel, support intake mailbox |
| 10 | `cp-10-surfaces` | T12 | *registered: portfolio board · Grafana · Scorecard · DevLake · dependency graph* |

### Orchestrator rules

1. `plan` mode prints one `PLAN <step-id> <state>` line per step and a final `PLAN: <n> steps, <a> apply, <s> satisfied, <m> manual`. It performs no write of any kind.
2. `apply` mode runs steps in order, halting on the first `Stop` (exit 2) or `DriftError` (exit 3). `--resume` replays the ledger and re-checks each `done` step before skipping it — a ledger is a hint, never a substitute for a check.
3. On full success the orchestrator emits **one** event of type `product_created` via the records-writer workflow dispatch (SR-5; Section 97.1, Section 97.3). The type is validated against `contracts.event_types()` first; absent → `Stop`.
4. `lifecycle` is written as `active` **only after** the VALIDATE stage of Section 19.1 passes, which is not this phase's act. The orchestrator writes `lifecycle: pre-launch`-compatible state per Section 15.8 and prints `HANDOFF: launch readiness is a separate gate (Section 19.2)`. Nothing in this phase sets `launch_status: launched`.
5. The final line of a successful `apply` is exactly `CREATE-PRODUCT: COMPLETE <product-id> steps=10 manual=<n>`.

### AT-001 rehearsal

Section 100.1 AT-001 — *"Add product 21 … Every surface enumerates from the registry … No dashboard, workflow or script contains a product list"*. The rehearsal script runs create-product twice against `$PROVISION_SANDBOX_ORG` for a fresh id and asserts the second run applies nothing.

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
cat > "$CP/tools/provision/tests/at001_rehearsal.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${PROVISION_SANDBOX_ORG:?}"
ID="at001-$(date -u +%Y%m%d%H%M%S)"
cd "$CP/tools/provision"
python -m provision create-product --product-id "$ID" --display-name "AT-001 Rehearsal" \
  --conformance-profile service --classification-class experimental \
  --reliability-criticality low --business-criticality low \
  --repositories "$ID-api:primary:true" --escalation team_lead \
  --scaffolding-issue "$AT001_ISSUE" --decision-record "$AT001_DECISION" --mode apply
FIRST=$?
python -m provision create-product --product-id "$ID" --display-name "AT-001 Rehearsal" \
  --conformance-profile service --classification-class experimental \
  --reliability-criticality low --business-criticality low \
  --repositories "$ID-api:primary:true" --escalation team_lead \
  --scaffolding-issue "$AT001_ISSUE" --decision-record "$AT001_DECISION" --mode plan \
  | tee /tmp/at001-second.txt
grep -q "apply 0" /tmp/at001-second.txt || { echo "AT-001: SECOND RUN NOT IDEMPOTENT"; exit 1; }
python -m provision verify-surfaces --static --root "$CP" | tail -1
python -m provision verify-scaffold --repo "$PROVISION_SANDBOX_ORG/$ID-api" --profile service >/dev/null
echo "AT-001 REHEARSAL: PASS"
EOF
chmod +x "$CP/tools/provision/tests/at001_rehearsal.sh"
```

### Commands

> ⚠ L3-04-LIVE: Do not run during bootstrap. Run after bootstrap constraint lifts.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t13 04-t12
# ... write provision/ops/create_product.py and wire the ten steps ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest -q
CP="$CP" ./tests/at001_rehearsal.sh
cd "$CP" && git add tools/provision
git commit -m "L3-04-13: create-product orchestrator, ten fixed steps, AT-001 rehearsal"
lane_pr 04-t13 "create-product orchestrator"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Exactly ten steps, in the fixed order | `cd "$CP/tools/provision" && python -m provision create-product --list-steps \| tr '\n' ' '` | `cp-01-preflight cp-02-repo cp-03-team cp-04-codeowners cp-05-protection cp-06-environments cp-07-scaffold cp-08-registry cp-09-configure-checklist cp-10-surfaces ` |
| A2 | `plan` is the default mode | `cd "$CP/tools/provision" && python -m provision create-product --product-id x --show-mode` | `mode=plan` |
| A3 | `--mode apply` without `--decision-record` exits 2 | `cd "$CP/tools/provision" && python -m provision create-product --product-id x --mode apply >/dev/null 2>&1; echo "exit=$?"` | `exit=2` |
| A4 | AT-001 rehearsal passes and is idempotent | `CP="$CP" "$CP/tools/provision/tests/at001_rehearsal.sh" \| tail -1` | `AT-001 REHEARSAL: PASS` |
| A5 | Exactly one workflow-dispatch call per successful run (T02 rule 5 / SR-2 forbids body values in calls.jsonl; assert dispatch path, not body field) | `grep -c '"path": ".*/actions/workflows/.*/dispatches"' "$PROVISION_RUN_DIR"/*/calls.jsonl` | `1` |
| A6 | Nothing in this phase sets `launch_status: launched` | `cd "$CP/tools/provision" && grep -rn "launched" provision/ --include='*.py' \| wc -l` | `0` |
| A7 | Success line is exact | `CP="$CP" ./tests/at001_rehearsal.sh \| grep -c '^CREATE-PRODUCT: COMPLETE '` | `1` |
| A8 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && [ "$(python -m provision create-product --list-steps | wc -l)" -eq 10 ] \
  && [ "$(python -m provision create-product --product-id x --show-mode)" = "mode=plan" ] \
  && python -m pytest -q >/dev/null \
  && [ "$(CP="$CP" ./tests/at001_rehearsal.sh | tail -1)" = "AT-001 REHEARSAL: PASS" ] \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-13: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-13: PASS`

### STOP rule

**If the second (idempotence) run reports any step as `apply` — do not "fix" it by making the step skip on a ledger entry alone.** A step whose `check()` cannot see its own prior effect is not idempotent, it is merely forgetful, and on a resumed run after a partial failure it will do the wrong thing. File the §0.7 blocker with title `BLOCKER L3-04-13: step <id> is not check-idempotent`.

---

## L3-04-14 — `provision preprovision-person` — the T-minus-one-week checklist

**Size:** M · **Depends on:** `L3-04-04` · **Owns:** `tools/provision/**`

### Spec basis — Section 12.1, quoted in full because the list is binding

> *"At one week before the start date (T-minus-one-week) the operator works a pre-provisioning checklist: GitHub account confirmed, hardware ready, email account created, AI-runtime choice asked of the joiner, the runtime seat purchased, and an asset-inventory entry recorded for issued hardware (Section 49)."*

Also Section 12.1: *"The `add person` scaffolding operation (Section 12.6) is executed by the Founder or by a holder of the `platform-admin` capability; the organisation invitation itself requires organisation Owner rights."*

### The literal CLI signature

```
provision preprovision-person
  --person-id   <slug>
  --start-date  YYYY-MM-DD
  --mode        plan|apply           # default: plan
  [--issue-repo <org/repo>]          # defaults to the control-plane repo
```

### Files created

`tools/provision/provision/ops/preprovision.py`, `tools/provision/provision/templates/preprovision-checklist.md`, `tools/provision/provision/people/preprovision_gate.py`, `tools/provision/tests/test_preprovision.py`.

### The checklist template — exactly six rows, transcribed from Section 12.1

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
cat > "$CP/tools/provision/provision/templates/preprovision-checklist.md" <<'EOF'
<!-- provision-step:preprovision:{person_id} -->
# Pre-provisioning — {person_id} — due {t_minus_one_week} (start date {start_date})

Section 12.1. Worked by the Founder or a holder of the `platform-admin` capability
(Section 9). The organisation invitation itself requires organisation Owner rights
and is NOT part of this checklist — it belongs to `provision add-person`.

- [ ] GitHub account confirmed
- [ ] Hardware ready
- [ ] Email account created
- [ ] AI-runtime choice asked of the joiner (approved list, Section 35.2 — their choice)
- [ ] Runtime seat purchased (asset entry required, Section 39.1)
- [ ] Asset-inventory entry recorded for issued hardware (Section 49)

## Not on this checklist, deliberately
- Organisation invitation, Team membership, capability grants — `provision add-person`.
- Self-view key exchange — handed once, in person (Section 12.1, Section 90.6).
- The conduct-adviser name and the Section 81.8 fairness rules — named items on the
  ONBOARDING checklist issue (Section 12.1), emitted by `provision add-person`.

Close this issue only when every box is ticked. `provision add-person` reads this
issue's state and fails closed if it is open (Section 64.1; invariant 80).
EOF
```

### Behavioural rules

1. `t_minus_one_week` = `start_date - 7 days`, resolved against the person's declared working calendar and operating timezone where the registry already carries one (Section 97.1: *"never against a runner's local time"*; Section 7.3 `work_arrangement.timezone`). Where the person has no registry entry yet, resolve against the estate operating timezone from the leave records per Section 6.4 and print which calendar was used.
2. Exactly one issue per person id, idempotent via the `provision-step:preprovision:<person_id>` marker (`L3-04-04`).
3. `preprovision_gate.state(person_id)` returns `OPEN`, `CLOSED` or `ABSENT`. `add-person` consumes it.
4. Rows 5 and 6 name assets that live in `assets/**` (L5). The template asks the operator to record them; L3 never writes them.
5. The command emits no event. Onboarding phase events belong to `add-person` and the onboarding workflow (`onboarding_phase_completed`, Section 97.3).

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t14 04-t13
# ... write the files ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_preprovision.py -q
cd "$CP" && git add tools/provision
git commit -m "L3-04-14: T-minus-one-week pre-provisioning checklist command"
lane_pr 04-t14 "add-person: T-7 pre-provisioning checklist"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Exactly six checklist rows | `cd "$CP/tools/provision" && grep -c '^- \[ \] ' provision/templates/preprovision-checklist.md` | `6` |
| A2 | The six rows match Section 12.1 verbatim in order | `cd "$CP/tools/provision" && python -m pytest tests/test_preprovision.py::test_six_rows_verbatim -q >/dev/null && echo OK` | `OK` |
| A3 | Due date is start date minus seven days | `cd "$CP/tools/provision" && python -m provision preprovision-person --person-id demo --start-date 2026-09-14 --mode plan \| grep -c 'due 2026-09-07'` | `1` |
| A4 | Second run creates no second issue | `cd "$CP/tools/provision" && python -m pytest tests/test_preprovision.py::test_idempotent -q >/dev/null && echo OK` | `OK` |
| A5 | Gate returns `ABSENT` when no issue exists | `cd "$CP/tools/provision" && python -m pytest tests/test_preprovision.py::test_gate_absent -q >/dev/null && echo OK` | `OK` |
| A6 | The calendar used is printed, never assumed | `cd "$CP/tools/provision" && python -m provision preprovision-person --person-id demo --start-date 2026-09-14 --mode plan \| grep -c '^CALENDAR: '` | `1` |
| A7 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && [ "$(grep -c '^- \[ \] ' provision/templates/preprovision-checklist.md)" -eq 6 ] \
  && [ "$(python -m provision preprovision-person --person-id demo --start-date 2026-09-14 --mode plan | grep -c 'due 2026-09-07')" -eq 1 ] \
  && python -m pytest tests/test_preprovision.py -q >/dev/null \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-14: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-14: PASS`

### STOP rule

**If no working calendar or operating timezone can be resolved — do not fall back to the runner's local time.** Section 97.1 names that fallback as the mechanism by which a wall-clock gate silently admits what it exists to prevent. File the §0.7 blocker with title `BLOCKER L3-04-14: no working calendar resolvable for the T-7 date`.

---

## L3-04-15 — `provision add-person`

**Size:** L · **Depends on:** `L3-04-13`, `L3-04-14` · **Owns:** `tools/provision/**`

### Spec basis

Section 12.6: *"`add person` produces: `people.yaml` entry; organisation invitation; Team membership per assignments; capability grants; AI runtime assignment honouring per-product `ai_restrictions`; onboarding checklist issue; and registration in the review network view."*
Section 12.1 lifecycle, Section 7.1 registry rules, Section 11.2 permission model, Section 26.4 registry-change lane, AT-002, EC-1, EC-10, EC-11.

### The literal CLI signature

```
provision add-person
  --person-id        <slug>                                  # stable, never reused (Section 7.1)
  --display-name     <"Human Readable Name">
  --github-login     <login>
  --role             <role-id from roles.yaml>
  --employment-type  employee|contractor|intern|temporary_specialist|consultant
  --capabilities     <cap>[,<cap>...]                        # explicit; never inherited wholesale
  --ai-runtime       <approved-runtime>|none
  --start-date       YYYY-MM-DD
  [--end-date        YYYY-MM-DD]                             # MANDATORY for every non-employee
  [--scope-products  <product-id>[,<product-id>...]]
  [--scope-repositories-only]
  [--sponsor         <person-id>]                            # MANDATORY for temporary_specialist
  --decision-record  DEC-YYYY-MM-DD-NNN
  --mode             plan|apply                              # default: plan
```

### The nine steps (fixed order)

| # | Step id | Rule |
| --- | --- | --- |
| 1 | `ap-01-preflight` | See the refusal table below |
| 2 | `ap-02-registry-pr` | Write the `people.yaml` entry via PR on the registry-change lane. `availability: active`, `access_status: pending` — Section 12.1's ADDED state, exactly |
| 3 | `ap-03-invitation` | `PUT /orgs/{org}/memberships/{login}` with `{"role": "member"}` — **base Read only** (Section 11.2). Never `admin`. |
| 4 | `ap-04-capabilities` | Capabilities are declared in the same PR as step 2; **no capability is granted by this CLI outside the registry**. Authority derives from the registry (invariant 11, Section 9.1) |
| 5 | `ap-05-ai-runtime` | Record `ai_runtime` from the approved list. For each product in `--scope-products`, read that product's `ai_restrictions` (Section 36.4) and refuse a runtime the product restricts — Section 12.1: *"Onboarding on each product honours that product's declared `ai_restrictions` … constrained at onboarding, not discovered later"* |
| 6 | `ap-06-onboarding-issue` | Emit the onboarding checklist issue (contents below) |
| 7 | `ap-07-shadow-assignments` | Where `cross_review_shadow` assignments are supplied, declare them in the same registry PR — Section 12.1: *"The shadow phase is recorded, not informal"* |
| 8 | `ap-08-reconcile-handoff` | Print `HANDOFF: Team membership and Write are applied by reconciliation from the merged registry (Section 26.4, Section 11.2)`. **This CLI never adds a Team membership for a person directly.** |
| 9 | `ap-09-event` | Emit `person_added` via the records-writer dispatch (SR-5) |

### `ap-01-preflight` refusal table (each exits 2)

| Condition | Basis |
| --- | --- |
| The pre-provisioning issue for this person is `OPEN` or `ABSENT` | Section 12.1 T-7 checklist; fail-closed (Section 64.1, invariant 80) |
| `--person-id` already exists in the people registry, in **any** availability state | Section 7.1: *"Their identifier is never reused"* |
| `employment_type` is not `employee` and `--end-date` is absent | Section 7.1: *"`end_date` is mandatory for every non-employee"*; Section 12.4: *"CI fails if null"* |
| `employment_type` is `temporary_specialist` and `--sponsor` is absent | Section 12.4: *"Mandatory `sponsor:` field"* |
| Any requested capability has no row in the Section 9 capability table | Section 9.1: *"A capability appearing in a … `people.yaml` grant … without a row in this table fails control-plane CI validation"* |
| `people-intelligence` is requested for anyone | Section 9.1 / D109: held by the Founder, **not delegable**; *"no reconciliation, scaffolding or onboarding path grants it implicitly"* |
| A `primary_owner`, `cross_reviewer` or `backup_owner` assignment is requested for a temporary person | Section 12.4: **Ownership: Never** |
| `production-approval` or any environment access is requested for a temporary person | Section 12.4: **Production: Never** |
| `--mode apply` without `--decision-record` | SR-7; Section 26.4 authority delta |
| The target org is not `$PROVISION_SANDBOX_ORG` and `--i-am-operations` is absent | §0.3 |

### The onboarding checklist issue — rows are transcribed from Section 12.1 and 12.7

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
cat > "$CP/tools/provision/provision/templates/onboarding-checklist.md" <<'EOF'
<!-- provision-step:onboarding:{person_id} -->
# Onboarding — {person_id} — start {start_date}

## Who protects you (Section 12.1, Section 81.8) — read on day one
- [ ] External conduct-adviser contact read and acknowledged: {conduct_adviser}
- [ ] Section 81.8 fairness rules read and acknowledged

## Lifecycle (Section 12.1)
- [ ] Self-view encryption key exchanged in person (Section 90.6)
- [ ] Constitution read
- [ ] AGENTS.md read on the first product
- [ ] `make setup` run
- [ ] `make test` run
- [ ] No API keys present: `env | grep -i api_key` returns empty (Section 40.2, invariant 84)

## Milestone targets (Section 12.7 — rendered automatically, visible to you)
| Milestone | Target band |
| --- | --- |
| Local setup working on first product (`make setup`, `make dev`, `make test`) | Day 1 |
| First test executed against a real product | Day 1-2 |
| First cross-review submitted | Week 1 |
| First accepted PR merged | Week 1-2 |
| First Ready item taken independently | Week 2-3 |
| First independent product work as owner or co-owner | Week 4-8 |
| First incident participation | First quarter |

The two workstation-local milestones leave no machine trace and are recorded as a
one-line human confirmation on this issue (Section 12.7). Everything else is derived.

Cross-review shadow first; ownership later (Section 12.1). Write is granted on
exactly the repositories your assignments name, by reconciliation, not by hand.
EOF
```

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t15 04-t14
# ... write provision/ops/add_person.py, provision/people/*.py, templates, tests ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_add_person.py -q
cd "$CP" && git add tools/provision
git commit -m "L3-04-15: add-person - registry PR, base-Read invitation, ai_restrictions honoured, onboarding checklist"
lane_pr 04-t15 "add-person"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Nine steps in the fixed order | `cd "$CP/tools/provision" && python -m provision add-person --list-steps \| tr '\n' ' '` | `ap-01-preflight ap-02-registry-pr ap-03-invitation ap-04-capabilities ap-05-ai-runtime ap-06-onboarding-issue ap-07-shadow-assignments ap-08-reconcile-handoff ap-09-event ` |
| A2 | An open pre-provisioning checklist blocks add-person | `cd "$CP/tools/provision" && python -m pytest tests/test_add_person.py::test_open_preprovision_blocks -q >/dev/null && echo OK` | `OK` |
| A3 | Non-employee without `--end-date` exits 2 | `cd "$CP/tools/provision" && python -m pytest tests/test_add_person.py::test_non_employee_needs_end_date -q >/dev/null && echo OK` | `OK` |
| A4 | `people-intelligence` is always refused | `cd "$CP/tools/provision" && python -m pytest tests/test_add_person.py::test_people_intelligence_refused -q >/dev/null && echo OK` | `OK` |
| A5 | Temporary person cannot receive ownership or production | `cd "$CP/tools/provision" && python -m pytest tests/test_add_person.py::test_temporary_no_ownership_no_production -q >/dev/null && echo OK` | `OK` |
| A6 | Org role granted is exactly `member` | `cd "$CP/tools/provision" && grep -c '"role": "member"' provision/ops/add_person.py` | `1` |
| A7 | No direct Team-membership call in add-person | `cd "$CP/tools/provision" && grep -rn "teams/.*memberships" provision/ops/add_person.py \| wc -l` | `0` |
| A8 | An `ai_restrictions`-violating runtime is refused | `cd "$CP/tools/provision" && python -m pytest tests/test_add_person.py::test_ai_restrictions_honoured -q >/dev/null && echo OK` | `OK` |
| A9 | Onboarding issue names the conduct adviser and fairness rules | `cd "$CP/tools/provision" && grep -c 'conduct-adviser\|conduct_adviser' provision/templates/onboarding-checklist.md` | `2` |
| A10 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && [ "$(python -m provision add-person --list-steps | wc -l)" -eq 9 ] \
  && [ "$(grep -rn 'teams/.*memberships' provision/ops/add_person.py | wc -l)" -eq 0 ] \
  && python -m pytest tests/test_add_person.py -q >/dev/null \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-15: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-15: PASS`

### STOP rule

**If the operation would grant Write to any repository directly, rather than through a Team derived from the registry — stop.** Section 11.2 makes Teams the only Write path, and Section 53.1 makes registry-vs-Team mismatch a CI failure on the affected repository. A direct grant creates permanent, invisible, unreconciled access. File the §0.7 blocker with title `BLOCKER L3-04-15: add-person would grant Write outside the Team path`.

---

## L3-04-16 — `provision change-role`

**Size:** M · **Depends on:** `L3-04-15` · **Owns:** `tools/provision/**`

### Spec basis — Section 12.3, the flow transcribed as steps

```
ROLE CHANGE DECIDED → people.yaml role updated → CAPABILITY RECALCULATION →
PERMISSION RECALCULATION → REVIEWER MATRIX REASSESSMENT → OWNERSHIP REASSESSMENT →
INCIDENT RESPONDER REASSESSMENT → PERFORMANCE-FRAMEWORK MAPPING CONFIRMED →
DASHBOARD UPDATE — automatic
```

Section 12.3: *"**No manual editing across repositories.** A role change is a registry edit plus reconciliation."* And: *"A role change affecting employment responsibility or status is a Founder decision; assignment changes within a role are Team Lead decisions (Section 74)."* Section 12.6, `change role`. AT-005, EC-9.

### The literal CLI signature

```
provision change-role
  --person-id           <slug>
  --new-role            <role-id from roles.yaml>
  --effective-date      YYYY-MM-DD
  [--add-capabilities   <cap>[,<cap>...]]
  [--remove-capabilities <cap>[,<cap>...]]
  --decision-record     DEC-YYYY-MM-DD-NNN
  --mode                plan|apply        # default: plan
```

### The eight steps (fixed order)

| # | Step id | Rule |
| --- | --- | --- |
| 1 | `cr-01-preflight` | Person exists, is not `departed`; new role exists in the role registry; every added capability has a Section 9 row; `people-intelligence` is refused unconditionally (D109); `--decision-record` present |
| 2 | `cr-02-registry-pr` | Single PR updating `role`, `capabilities`, effective-dated to `--effective-date`. This is an authority delta and the decision-record id goes in the same commit (Section 26.4) |
| 3 | `cr-03-capability-diff` | Print the explicit before/after capability set. Section 12.3: *"new role defaults reviewed; explicit grants confirmed; capabilities no longer appropriate are removed"* — the CLI prints the diff; the human confirms it in the PR |
| 4 | `cr-04-permission-handoff` | Print `HANDOFF: Team membership is adjusted by reconciliation (Section 12.3)`. **No Team call is made.** |
| 5 | `cr-05-reviewer-matrix-prompt` | Emit a prompt issue for the `reviewer-matrix-change` capability holder: does the change alter review load or knowledge distribution? (Section 12.3; invariant 13 — the Team Lead executes, and every permanent ownership change generates a Founder-view notification: visibility, not approval) |
| 6 | `cr-06-ownership-prompt` | Emit an ownership-reassessment prompt. Section 12.3: *"moving to Team Lead or QA usually means shedding ownership"* |
| 7 | `cr-07-responder-prompt` | Emit an incident-responder reassessment prompt |
| 8 | `cr-08-framework-mapping` | Assert a performance-framework mapping exists for the new role instance, effective-dated to the change (Section 12.3, Section 86.3). Absent → exit 3 with `MAPPING-MISSING`. This is SIG-23 territory and must not pass silently |

Plus: emit `person_role_changed` (Section 97.3), and print `DASHBOARDS: automatic (enumerated from the registry)` — Section 12.3's last line is *"DASHBOARD UPDATE — automatic"*, so there is nothing to do, and the CLI says so rather than doing something.

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t16 04-t15
# ... write provision/ops/change_role.py and tests ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_change_role.py -q
cd "$CP" && git add tools/provision
git commit -m "L3-04-16: change-role - registry edit plus reconciliation, four reassessment prompts, framework mapping assertion"
lane_pr 04-t16 "change-role"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Eight steps in the fixed order | `cd "$CP/tools/provision" && python -m provision change-role --list-steps \| tr '\n' ' '` | `cr-01-preflight cr-02-registry-pr cr-03-capability-diff cr-04-permission-handoff cr-05-reviewer-matrix-prompt cr-06-ownership-prompt cr-07-responder-prompt cr-08-framework-mapping ` |
| A2 | Exactly one registry PR is opened | `cd "$CP/tools/provision" && python -m pytest tests/test_change_role.py::test_single_pr -q >/dev/null && echo OK` | `OK` |
| A3 | No repository or Team is edited directly | `cd "$CP/tools/provision" && grep -rn "teams/\|/branches/\|/environments/" provision/ops/change_role.py \| wc -l` | `0` |
| A4 | Missing framework mapping exits 3 | `cd "$CP/tools/provision" && python -m pytest tests/test_change_role.py::test_missing_mapping_exit3 -q >/dev/null && echo OK` | `OK` |
| A5 | The capability diff is printed before/after | `cd "$CP/tools/provision" && python -m provision change-role --person-id demo --new-role team_lead --effective-date 2026-09-01 --mode plan \| grep -c '^CAPABILITY-DIFF '` | `1` |
| A6 | Effective dating is honoured, never retroactive | `cd "$CP/tools/provision" && python -m pytest tests/test_change_role.py::test_effective_dated_not_retroactive -q >/dev/null && echo OK` | `OK` |
| A7 | Three reassessment prompts are emitted | `cd "$CP/tools/provision" && python -m provision change-role --person-id demo --new-role qa --effective-date 2026-09-01 --mode plan \| grep -c '^PROMPT '` | `3` |
| A8 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && [ "$(python -m provision change-role --list-steps | wc -l)" -eq 8 ] \
  && [ "$(grep -rn 'teams/\|/branches/\|/environments/' provision/ops/change_role.py | wc -l)" -eq 0 ] \
  && python -m pytest tests/test_change_role.py -q >/dev/null \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-16: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-16: PASS`

### STOP rule

**If the role change would remove a capability that is the person's only qualification for an assignment they still hold — do not remove it and do not silently keep it.** Exit 3 with `CONFLICT: capability <cap> still required by assignment <type> on <product>` and file the §0.7 blocker with title `BLOCKER L3-04-16: capability removal would orphan an active assignment`. Resolution is a Team Lead act under `reviewer-matrix-change` (invariant 13), not a provisioning decision.

---

## L3-04-17 — `provision remove-person`, orphan gate, exit record

**Size:** L · **Depends on:** `L3-04-15` · **Owns:** `tools/provision/**`

### Spec basis

Section 12.2, the exit lifecycle in full; the 16-orphan table; *"**Orphan detection runs immediately when `availability` becomes `departing`**, in prospective mode against the declared `end_date`: it emits the transfer worklist"*; *"Person record RETAINED — never deleted, identifier never reused"*. Section 12.6, `remove person`. Invariant 57, SIG-05, AT-017, AT-018, EC-6.

**Critical boundary:** Section 12.2 assigns the revocations to reconciliation — *"RECONCILIATION EXECUTES: remove from organisation · remove from every GitHub Team · revoke every environment access · revoke production capability · deactivate AI runtime · …"*. `remove-person` therefore **declares the state and verifies convergence**. It revokes nothing itself. This also keeps SR-1 intact.

### The literal CLI signature

```
provision remove-person
  --person-id       <slug>
  --stage           departing|departed
  --end-date        YYYY-MM-DD              # required for --stage departing
  --decision-record DEC-YYYY-MM-DD-NNN
  --mode            plan|apply              # default: plan
  [--verify-convergence]                    # --stage departed only
```

### Stage `departing` — five steps

| # | Step id | Rule |
| --- | --- | --- |
| 1 | `rp-01-preflight` | Person exists and is `active` or `on_leave`; `--end-date` present and not in the past; `--decision-record` present |
| 2 | `rp-02-registry-pr` | Single PR: `availability: departing`, `end_date: <date>`. Legal pairing enforced per Section 7.1 |
| 3 | `rp-03-prospective-orphans` | Run the orphan detector in **prospective** mode against `--end-date` and write the **transfer worklist**. Section 12.2: the knowledge-transfer window *"works from a generated list for the notice period, not from memory"* |
| 4 | `rp-04-succession-check` | If the person appears in a `topology.yaml` succession block, emit a Founder-decision prompt immediately. Section 12.2: *"succession is never left vacant by a departure"* |
| 5 | `rp-05-event` | Emit `orphan_detected` per prospective orphan found (Section 97.3) |

### Stage `departed` — six steps

| # | Step id | Rule |
| --- | --- | --- |
| 6 | `rp-06-registry-pr` | `availability: departed`, `access_status: revoked`. **The record is retained; nothing is deleted** (Section 7.1, invariant 47) |
| 7 | `rp-07-reconcile-handoff` | Print the nine revocations Section 12.2 assigns to reconciliation, each with `HANDOFF:` prefix. Make no revocation call. |
| 8 | `rp-08-converge` | With `--verify-convergence`, poll (read-only) until org membership, every Team membership, every environment access and the AI-runtime seat show revoked. Timeout → exit 3 `DRIFT: revocation not converged for <person-id>` (SIG-02, SIG-03) |
| 9 | `rp-09-orphans` | Run the orphan detector in **actual** mode. Exit 3 while any **Blocking** orphan remains. Section 12.2: blocking orphans *"cannot be dismissed without resolution"*; invariant 57 |
| 10 | `rp-10-exit-record` | Dispatch the records-writer workflow with the exit record payload (SR-5). The record links the transfer worklist, the resolved orphans and the closing review-period segment (Section 12.2: *"The departing person's review-period segment closes at `end_date`"*) |
| 11 | `rp-11-event` | Emit `person_departed` |

### The orphan gate adapter

`tools/provision/provision/lifecycle/orphan_gate.py` is the **only** place `remove-person` touches the detector. It exposes:

```python
ORPHAN_DETECTOR_CMD: list[str]   # discovered, never guessed — see the STOP rule
def scan(person_id: str, *, prospective: bool, as_of: str | None) -> list[Orphan]: ...
def blocking(orphans: list[Orphan]) -> list[Orphan]: ...
```

The 16 orphan types and their severities are the detector's, not this task's — `orphan_gate.py` re-asserts only the **count** and the **severity vocabulary**, so a detector that silently narrows its comparison set is caught here too (the reasoning of Section 53.1's seeded-canary and per-registry comparison counts):

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
cat > "$CP/tools/provision/provision/lifecycle/orphan_types.yaml" <<'EOF'
# Section 12.2 orphan table. This file asserts the SHAPE the detector must return.
# Detection logic belongs to the reconciler (subsystem C), never here.
version: 1
expected_type_count: 16
severity_vocabulary: [Blocking, High, Medium]   # Section 53.4 scale; no other words exist
blocking_types:
  - product-with-no-primary-owner
  - product-with-no-cross-reviewer
  - product-with-no-primary-responder
  - shared-service-with-no-owner
  - domain-with-no-owner
  - customer-commitment-with-no-owner
  - policy-with-no-owner
EOF
```

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t17 04-t16
# discover the detector entry point BEFORE writing the adapter:
ls "$CP/reconciler" && grep -rln "orphan" "$CP/reconciler" | head -20
# ... write provision/ops/remove_person.py, provision/lifecycle/*, tests ...
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_remove_person.py tests/test_orphan_gate.py -q
cd "$CP" && git add tools/provision
git commit -m "L3-04-17: remove-person - departing/departed stages, prospective transfer worklist, blocking orphan gate, exit record"
lane_pr 04-t17 "remove-person and orphan gate"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | Eleven steps across the two stages | `cd "$CP/tools/provision" && python -m provision remove-person --list-steps \| wc -l` | `11` |
| A2 | `departing` produces a transfer worklist | `cd "$CP/tools/provision" && python -m pytest tests/test_remove_person.py::test_departing_emits_worklist -q >/dev/null && echo OK` | `OK` |
| A3 | The person record is never deleted | `cd "$CP/tools/provision" && grep -rn "DELETE\|remove_entry\|del people\[" provision/ops/remove_person.py \| wc -l` | `0` |
| A4 | A remaining Blocking orphan exits 3 | `cd "$CP/tools/provision" && python -m pytest tests/test_remove_person.py::test_blocking_orphan_exit3 -q >/dev/null && echo OK` | `OK` |
| A5 | No revocation call is made by the CLI | `cd "$CP/tools/provision" && grep -rn "call(" provision/ops/remove_person.py \| grep -vc "'GET'\|dispatches\|/pulls\|/contents/\|/git/refs\|/issues"` | `0` |
| A6 | Nine reconciliation handoffs are printed | `cd "$CP/tools/provision" && python -m provision remove-person --person-id demo --stage departed --mode plan \| grep -c '^HANDOFF: '` | `9` |
| A7 | The orphan-type shape assertion is 16 with a three-word severity vocabulary | `cd "$CP/tools/provision" && python -c "import yaml;d=yaml.safe_load(open('provision/lifecycle/orphan_types.yaml'));print(d['expected_type_count'],len(d['severity_vocabulary']))"` | `16 3` |
| A8 | A succession designate raises a Founder prompt | `cd "$CP/tools/provision" && python -m pytest tests/test_remove_person.py::test_succession_prompt -q >/dev/null && echo OK` | `OK` |
| A9 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && [ "$(python -m provision remove-person --list-steps | wc -l)" -eq 11 ] \
  && [ "$(python -m provision remove-person --person-id demo --stage departed --mode plan | grep -c '^HANDOFF: ')" -eq 9 ] \
  && [ "$(python -c "import yaml;d=yaml.safe_load(open('provision/lifecycle/orphan_types.yaml'));print(d['expected_type_count'])")" = "16" ] \
  && python -m pytest tests/test_remove_person.py tests/test_orphan_gate.py -q >/dev/null \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-04-17: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-17: PASS`

### STOP rules (two)

**STOP-1 — orphan detector not discoverable.** Run `ls "$CP/reconciler"` and `grep -rln orphan "$CP/reconciler"`. If no orphan-detection entry point exists, **do not write one in `tools/provision/`**. Orphan detection is subsystem C (Section 99.2) and belongs to an earlier L3 phase under `reconciler/**`; a second implementation would be a second source of truth for a Blocking-severity control. File the §0.7 blocker with title `BLOCKER L3-04-17: orphan detector entry point not found under reconciler/` and ask *"What is the orphan detector's CLI entry point and its prospective-mode flag?"*.

**STOP-2 — the detector returns fewer than 16 types or a severity word outside {Blocking, High, Medium}.** Do not map the unknown word onto a known one and do not lower `expected_type_count`. Section 53.4 is explicit that *"No other severity vocabulary exists anywhere in this system"*, and a narrowed comparison set is itself visible drift (Section 53.1). File the §0.7 blocker with title `BLOCKER L3-04-17: orphan detector shape does not match Section 12.2`.

---

## L3-04-18 — Phase gate: destructive-guard suite, idempotence proof, phase evidence

**Size:** M · **Depends on:** `L3-04-13`, `L3-04-16`, `L3-04-17` · **Owns:** `tools/provision/**`

This task proves, mechanically, that the phase honoured its own safety posture. Section 99.6 risk 6's mitigation is *"stricter-only rule enforced in code and tested"* — this is the test.

### Files created

`tools/provision/tests/test_phase_gate.py`, `tools/provision/tests/phase_gate.sh`, `tools/provision/PHASE-4-EVIDENCE.md`.

### The eleven gate assertions

| # | Assertion | Command | Expected |
| --- | --- | --- | --- |
| G1 | Every GitHub call goes through the gateway | `grep -rn "subprocess\|gh api" provision/ --include='*.py' \| grep -v core/ghclient.py \| wc -l` | `0` |
| G2 | No HTTP DELETE anywhere (SR-1) | `grep -rn "'DELETE'\|\"DELETE\"" provision/ --include='*.py' \| grep -v security/ \| wc -l` | `0` |
| G3 | No secret path anywhere (SR-2) | `grep -rn "/secrets" provision/ --include='*.py' \| grep -v security/ \| wc -l` | `0` |
| G4 | No org-settings write (SR-3) | `grep -rn "PATCH.*'/orgs/" provision/ --include='*.py' \| grep -v security/ \| wc -l` | `0` |
| G5 | No workflow-file write (SR-4) | `grep -rn "contents/.github/workflows" provision/ --include='*.py' \| grep -v security/ \| wc -l` | `0` |
| G6 | No direct records/events write (SR-5) | `grep -rn "contents/records/\|contents/events/" provision/ --include='*.py' \| grep -v security/ \| wc -l` | `0` |
| G7 | Stricter-only is tested for every applying step | `python -m pytest -k stricter -q \| tail -1` | ends with `passed` and count ≥ `4` |
| G8 | `plan` is the default for all five operations | `python -m provision --show-default-modes \| grep -c '=plan'` | `5` |
| G9 | All four operations are idempotent on re-run | `./tests/phase_gate.sh --idempotence \| tail -1` | `IDEMPOTENCE: 4/4 PASS` |
| G10 | Credential envelope still refuses all six probes | `python -m provision verify-credential-envelope \| tail -1` | `ENVELOPE: 6/6 REFUSED` |
| G11 | No hard-coded product or person list | `python -m provision verify-surfaces --static --root "$CP" \| tail -1` | `SURFACES-STATIC: 0 HARD-CODED` |

### `PHASE-4-EVIDENCE.md` — required contents

A single table, one row per task `L3-04-01`..`L3-04-18`, each with: task id, the SELF-VERIFY line captured verbatim, the merge-commit SHA of its PR into `integration`, and the UTC-with-offset timestamp of capture (Section 97.1). No prose. A row whose SELF-VERIFY line is not the exact expected string is a gate failure.

### Commands

> ✓ L3-04-DRY: Safe to run during bootstrap.
**Commands**

```bash
set -euo pipefail
source "$CP/tools/provision/scripts/lane.sh"
lane_start 04-t18 04-t17
cd "$CP/tools/provision" && . .venv/bin/activate
python -m pytest -q
./tests/phase_gate.sh --all | tee "$PROVISION_RUN_DIR/phase4-gate.txt"
# write PHASE-4-EVIDENCE.md from the captured SELF-VERIFY lines
cd "$CP" && git add tools/provision
git commit -m "L3-04-18: phase gate - destructive-guard suite, idempotence proof, phase evidence"
lane_pr 04-t18 "L3 Phase 4 gate and evidence"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| A1 | All eleven gate assertions pass | `cd "$CP/tools/provision" && ./tests/phase_gate.sh --all \| tail -1` | `PHASE-GATE: 11/11 PASS` |
| A2 | Evidence file has eighteen task rows | `cd "$CP/tools/provision" && grep -c '^\| L3-04-T' PHASE-4-EVIDENCE.md` | `18` |
| A3 | Every recorded SELF-VERIFY line reads `PASS` | `cd "$CP/tools/provision" && grep -c 'SELF-VERIFY L3-04-T[0-9]*: PASS' PHASE-4-EVIDENCE.md` | `18` |
| A4 | Full test suite green | `cd "$CP/tools/provision" && python -m pytest -q >/dev/null && echo OK` | `OK` |
| A5 | Lane guard clean across the whole phase | `cd "$CP" && git diff --name-only origin/integration...HEAD \| grep -vc '^tools/provision/'` | `0` |
| A6 | PR is open against `integration` | `cd "$CP" && gh pr view lane/3/04-t18 --json baseRefName -q .baseRefName` | `integration` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CP/tools/provision" \
  && [ "$(./tests/phase_gate.sh --all | tail -1)" = "PHASE-GATE: 11/11 PASS" ] \
  && [ "$(grep -c 'SELF-VERIFY L3-04-T[0-9]*: PASS' PHASE-4-EVIDENCE.md)" -eq 18 ] \
  && python -m pytest -q >/dev/null \
  && [ "$(cd "$CP" && git diff --name-only origin/integration...HEAD | grep -vc '^tools/provision/')" = "0" ] \
  && echo "SELF-VERIFY L3-04-18: PASS"
```

**Expected output (last line, exactly):** `SELF-VERIFY L3-04-18: PASS`

### STOP rule

**If any gate assertion fails — do not weaken the assertion, do not add an exclusion to the grep, and do not merge.** Every one of G1..G11 is a direct transcription of a binding rule. A phase that ships with a weakened guard is exactly the Section 99.6 risk-6 outcome: a write-scope automation whose safety property is asserted rather than executed. File the §0.7 blocker with title `BLOCKER L3-04-18: phase gate assertion G<n> failed` and stop. Merging into `integration` happens in train order (L1 → L4 → L2 → **L3** → L5) and is L0's act, never this lane's.

---

## 3. What this phase deliberately does not do

Stated so the executor does not helpfully add it.

| Not done here | Where it belongs |
| --- | --- |
| Applying declared state to the estate (Team membership, revocations, protection repair) | Reconciliation, subsystem C — Section 26.4, Section 53.2 Level 3 |
| Orphan **detection** logic and the 16-type table | Subsystem C, an earlier L3 phase under `reconciler/**` |
| Launch readiness, the evidence pack, `launch_status: launched` | Section 19.2 — a separate gate, after this phase |
| Product split, merge, transfer | Sections 19.3–19.5; Section 99.4 defers them explicitly |
| Writing `registries/**`, `schemas/**`, `contracts/**` | L1 and L0 — the FROZEN PARTITION forbids it |
| Writing `assets/**`, `access/**`, `infra/**`, `notify/**` | L5 |
| Writing `records/**`, `events/**` | L4, through the records-writer credential only (D89) |
| Writing `.github/workflows/**` | L2 |
| The self-view key exchange | Handed once, in person — Section 12.1, Section 90.6. Never automated. |
| Any formal people decision | Invariant 37, AT-071: no code path to one exists, and none is added here |
