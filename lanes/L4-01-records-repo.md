# L4-01 — PHASE 1: THE RECORDS REPOSITORY

**Lane:** L4 — Records, Events and Metrics (Subsystems **I** metrics pipeline, **N** work tracking conventions — MasterSpec §99.2)
**Branch prefix:** `lane/4/*`
**Paths this lane owns exclusively (PARTITION.md, FROZEN):** ALL of `control-plane-records`, plus `schemas/records/**`, `metrics/**`, `tools/records/**` in the `control-plane` repository.
**This document covers:** Phase 1 only — standing up the `control-plane-records` repository, its directory-per-item convention, its no-bypass ruleset (D107), commit signing, and the `records-writer` GitHub App (D89).

**Why this is Phase 1 and not later.** §99.6 risk 2: *"Evidence-plumbing gap — dashboards ship empty or drift into hand-maintenance if the record stores are not built early"*, mitigated by *"Section 97 is built in Foundation, before any dashboard that reads from it"*. §99.2 dependency spine: *"I is the feedstock for nearly all governance-tier and people-tier computation."* Invariant 46 (§101.7): derived data is computed, never hand-maintained, and metrics derive from the canonical record stores of §97.

---

## 0. Reader contract

You are executing, not designing. Every command below is literal and copy-pasteable. Run them in **Git Bash** (POSIX `sh`), not `cmd.exe` or PowerShell.

If any step requires you to choose, name, invent, or interpret something that is not written here, **STOP** and file a blocker (§0.4). Do not guess. Do not substitute a similar command. Do not "fix" a failing acceptance check by relaxing it.

### 0.1 Environment variables — set once per shell, before every task

```bash
# ---- L0-supplied parameter. See DECISION REQUIRED D-L4-01 below. ----
# L0-P0-001 (lanes/L0-01-phase-0-contracts.md) clones control-plane to this
# literal path. cd there explicitly before sourcing — do not rely on the
# shell's ambient working directory already being inside a clone.
cd "$HOME/src/control-plane"
source "./contracts/project-config.sh"
check_org

# ---- Fixed by this document. Do not change. ----
export RECORDS_REPO="control-plane-records"
export RECORDS_SLUG="${ORG}/${RECORDS_REPO}"
export CP_REPO="control-plane"
export CP_SLUG="${ORG}/${CP_REPO}"
export WORK="$HOME/src"
export RECORDS_DIR="${WORK}/${RECORDS_REPO}"
export CP_DIR="${WORK}/${CP_REPO}"
export SECRETS_DIR="$HOME/.l4-secrets"     # never inside any git working tree
mkdir -p "$WORK" "$SECRETS_DIR"
chmod 700 "$SECRETS_DIR"
echo "ORG=$ORG RECORDS_SLUG=$RECORDS_SLUG"
```

If `ORG` prints as the literal placeholder, **STOP** — D-L4-01 has not been answered.

### 0.2 External preconditions (owned by other lanes — verify, never create)

| Id | Precondition | Owner | Verify command | Required by |
|---|---|---|---|---|
| EXT-01 | The company-owned GitHub organisation exists and all products are consolidated into it (§98.2 Phase 1, bullet 1) | L0 | `gh api "/orgs/${ORG}" --jq .login` | T01 |
| EXT-02 | You hold an organisation **Owner** or **admin** role in `${ORG}` (repository creation, ruleset creation and App installation all require it) | L0 | `gh api "/orgs/${ORG}/memberships/$(gh api user --jq .login)" --jq .role` → `admin` | T01 |
| EXT-03 | The `control-plane` repository exists with an `integration` branch (PARTITION.md branch model) | L0 / L1 | `gh api "/repos/${CP_SLUG}/branches/integration" --jq .name` | T12 |
| EXT-04 | `gh` ≥ 2.40, `git`, `jq`, `openssl`, `curl` are installed | you | `gh --version && git --version && jq --version && openssl version && curl --version` | T01 |

If any precondition fails, **STOP** and file a blocker naming the precondition id. Do not create another lane's artifact.

### 0.3 Task index

| Task id | Title | Size | Depends on |
|---|---|---|---|
| `L4-P1-T01` | Preflight and parameter binding | S | — |
| `L4-P1-T02` | Create the `control-plane-records` repository | S | T01 |
| `L4-P1-T03` | Build the directory-per-item skeleton | M | T02 |
| `L4-P1-T04` | Root documents: `README.md`, `CONVENTIONS.md`, `.gitignore` | M | T03 |
| `L4-P1-T05` | Arm the no-bypass **branch** ruleset (force-push + deletion) | M | T04 |
| `L4-P1-T06` | Arm the no-bypass **tag** ruleset (tag deletion) | S | T02 |
| `L4-P1-T07` | Prove: rewriting blocked, appending permitted | M | T05, T06 |
| `L4-P1-T08` | Add `required_signatures` and prove it | M | T07 |
| `L4-P1-T09` | Create the `records-writer` GitHub App | M | T02 |
| `L4-P1-T10` | Install and scope the App to `control-plane-records` alone | M | T09 |
| `L4-P1-T11` | Prove the App appends here and reaches no registry | M | T10, T08 |
| `L4-P1-T12` | Store ruleset and credential shape as code in `tools/records/` | M | T05, T06, T08, T10 |

Sizes: **S** under 1 hour, **M** 1–4 hours, **L** over 4 hours. Every task is one branch or one console session; none spans a day.

### 0.4 Blocker protocol — the STOP rule mechanism

Every task's STOP rule ends in the same action. File the blocker into the **`control-plane`** repository (never into `control-plane-records` — it is a record store, not a work surface, §97.1).

```bash
# Literal blocker template. Fill the four <...> fields; change nothing else.
gh issue create \
  --repo "${CP_SLUG}" \
  --title "BLOCKER L4-P1-<TASK-ID>: <one-line symptom>" \
  --label "blocker" --label "lane-4" \
  --body "$(cat <<'EOF'
## Task
L4-P1-<TASK-ID> — <task title from the index in L4-01-records-repo.md>

## STOP trigger that fired
<quote the exact bullet from the task's STOP RULE>

## Command run
~~~
<the exact command, verbatim>
~~~

## Actual output
~~~
<the exact stdout/stderr, verbatim, untruncated>
~~~

## Expected output per the task's SELF-VERIFY block
~~~
<the expected block, verbatim, from this document>
~~~

## State left behind
<what exists now that did not before; what was rolled back; what was not>

## What I did NOT do
I did not choose an alternative approach, rename anything, relax an acceptance
criterion, or continue to the next task.
EOF
)"
```

After filing: stop work on this lane. Do not start the next task.

---

## ~~DECISION REQUIRED~~ — hand to L0 before T01

### ~~DECISION REQUIRED~~ D-L4-01 — The GitHub organisation login

> **Status: Closed (FD-065, 2026-09-06 — event-type enum question; FD-069, 2026-09-08 — org login).** The org login is `pareshp-org`, recorded in `contracts/project-config.sh` (FD-068/FD-069). The `check_org` guard at §0.1 prevents execution when `ORG` is unset. The charter's D-L4-01 event-type enum question is separately resolved by FD-065: L4 source identifiers are internal aliases that map to existing L1 event types via `metrics/signals/sig-source-map.yaml`.

**Why this is not decidable here.** MasterSpec §98.2 Phase 1 requires *"Consolidate all products into one company-owned GitHub organisation"* but never names it, and PARTITION.md names repositories without an owner. The executor cannot invent an org login: a wrong value creates a repository in the wrong account and the ruleset and App scoping in T05–T10 attach to the wrong object.

| Field | Value L0 must supply |
|---|---|
| `ORG` | the GitHub organisation login (the URL segment, e.g. the `X` in `github.com/X`) |

**Blocking:** every task. **Default if unanswered:** none — there is no safe default.

### D-L4-02 — What "signed by the writing identity" means for the records-writer (D107 bullet 2)

**Why this is not decidable here.** D107 states: *"The records-writer signs every commit, and a commit on the default branch that is unsigned, or signed by any other identity, is Blocking drift."* GitHub offers two mechanisms and the spec does not pick one:

| Option | Mechanism | Consequence |
|---|---|---|
| **(a)** | The records-writer writes through the REST **Contents API** with its installation token. GitHub signs the commit with its own web-flow key; the commit's author/committer is the App's bot identity and the commit shows **Verified**. | Satisfies a `required_signatures` ruleset rule. The signing *key* is GitHub's, the *identity* is the App's. |
| **(b)** | The records-writer holds a dedicated GPG or SSH signing key in the fifth secrets tier (§40.1) and pushes with `git push` + `commit -S`. | The signing key is the writer's own. Adds a key to rotate on the quarterly cadence (§40.1 "Fifth-tier operations") and a key-distribution problem to every runner. |

**Default recorded in this document: (a).** Every command below is written for (a), and T08/T11 assert `verification.verified == true` with the App as author. If L0 selects (b), T08 and T11 must be re-issued by L0 before execution; the executor must not adapt them.

**Blocking:** T08, T11. **Answer required before T08.**

### D-L4-03 — Long-term custody of the records-writer private key

**Why this is not decidable here.** §40.1 places machine credentials in the *"Machine-credential store on the hosts that use them"*, and the operations VM is Subsystem M — **lane L5**, path `ops-vm/**`. This lane must not write `ops-vm/**` (PARTITION.md rule 1). T09 therefore leaves the `.pem` at `${SECRETS_DIR}/records-writer.pem` on the executor's machine, which is a temporary location and not a fifth-tier store.

L0 must schedule the handoff of the `.pem` to L5 for placement in the ops-VM machine-credential store, and the creation of its operational-asset-inventory entry (§49) carrying rotation cadence (initial: quarterly), named rotator, rotation runbook link, behavioural envelope and expiry date — `assets/**` is L5's path.

**Blocking:** nothing in this document. **Must be scheduled before Phase 2.**

---

## TASK `L4-P1-T01` — Preflight and parameter binding

**Size:** S · **Depends on:** — · **Writes:** nothing (read-only)

Verifies EXT-01 … EXT-04 before anything is created. Creating the repository with the wrong identity or without org-admin rights produces a half-built store that cannot be cleanly removed once the T05 ruleset is armed.

### Commands

```bash
set -eu
echo "=== tools ==="
gh --version | head -1
git --version
jq --version
openssl version
curl --version | head -1

echo "=== auth ==="
gh auth status
gh api user --jq '.login'

echo "=== org ==="
gh api "/orgs/${ORG}" --jq '"login=" + .login + " plan=" + (.plan.name // "unknown")'

echo "=== my org role ==="
gh api "/orgs/${ORG}/memberships/$(gh api user --jq .login)" --jq '.role'

echo "=== scopes must include admin:org and repo ==="
gh auth status 2>&1 | grep -i 'Token scopes' || true

echo "=== the records repo must already exist, created by L0-P0-001, with the expected identity ==="
gh api "/repos/${RECORDS_SLUG}" --jq '{full_name:.full_name, private:.private, default_branch:.default_branch}'
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | `gh` is authenticated | `gh auth status >/dev/null 2>&1; echo $?` | `0` |
| 2 | Org exists (EXT-01) | `gh api "/orgs/${ORG}" --jq .login` | exactly the value of `$ORG` |
| 3 | You are org admin (EXT-02) | `gh api "/orgs/${ORG}/memberships/$(gh api user --jq .login)" --jq .role` | `admin` |
| 4 | Token carries `admin:org` | `gh auth status 2>&1 \| grep -c 'admin:org'` | `1` or greater |
| 5 | The records repo already exists (created by `L0-P0-001`, `lanes/L0-01-phase-0-contracts.md`) with the expected identity | `gh api "/repos/${RECORDS_SLUG}" --jq '{full_name:.full_name, private:.private, default_branch:.default_branch}'` | `{"full_name":"<ORG>/control-plane-records","private":true,"default_branch":"main"}` (with `<ORG>` = `$ORG`) |
| 6 | All five tools present (EXT-04) | `for t in gh git jq openssl curl; do command -v $t >/dev/null \|\| echo "MISSING $t"; done; echo DONE` | `DONE` with no `MISSING` line |

### SELF-VERIFY

```bash
set -eu
FAIL=0
[ "$(gh api "/orgs/${ORG}" --jq .login)" = "${ORG}" ] || { echo "FAIL org"; FAIL=1; }
[ "$(gh api "/orgs/${ORG}/memberships/$(gh api user --jq .login)" --jq .role)" = "admin" ] || { echo "FAIL role"; FAIL=1; }
gh auth status 2>&1 | grep -q 'admin:org' || { echo "FAIL scope admin:org"; FAIL=1; }
REPO_JSON="$(gh api "/repos/${RECORDS_SLUG}" --jq '{full_name:.full_name, private:.private, default_branch:.default_branch}' 2>/dev/null)" \
  || { echo "FAIL repo absent — L0-P0-001 has not run"; FAIL=1; }
[ "$REPO_JSON" = "{\"full_name\":\"${RECORDS_SLUG}\",\"private\":true,\"default_branch\":\"main\"}" ] \
  || { echo "FAIL repo identity mismatch: $REPO_JSON"; FAIL=1; }
for t in gh git jq openssl curl; do command -v "$t" >/dev/null || { echo "FAIL missing $t"; FAIL=1; }; done
[ "$FAIL" = "0" ] && echo "L4-P1-T01 PASS" || echo "L4-P1-T01 BLOCKED"
```

**Expected output — exactly this single line, nothing else:**

```
L4-P1-T01 PASS
```

### STOP RULE

Do not proceed to T02 if **any** of the following is true:

- `$ORG` is still the placeholder → D-L4-01 unanswered.
- Your org role is not `admin` → EXT-02 unmet; an org Owner must grant it or run this lane.
- `admin:org` is absent from the token scopes → re-run `gh auth refresh -h github.com -s admin:org -s repo` **once**; if it still fails, blocker.
- `/repos/${ORG}/control-plane-records` does not exist → `L0-P0-001` (`lanes/L0-01-phase-0-contracts.md`) has not yet run, or has not yet reached this org. That is an L0 Phase-0 precondition, not something this lane creates. Do **not** create it yourself. Blocker.
- It exists but `.private` is not `true`, `.default_branch` is not `main`, or `.full_name` is not exactly `${RECORDS_SLUG}` → this is not the object `L0-P0-001` created. Do **not** adopt it, rename it, or change its visibility. Blocker.

File the blocker with `<TASK-ID>` = `T01` using the template in §0.4.

---

## TASK `L4-P1-T02` — Create the `control-plane-records` repository

**Size:** S · **Depends on:** T01 · **Writes:** the repository `${ORG}/control-plane-records` (this lane owns all of it — PARTITION.md)

MasterSpec §40.1 (D89) fixes both the split and the reason: *"The record stores therefore live in their **own repository**, separate from the control-plane repository"*, because *"A ruleset bypass actor on GitHub bypasses the rule wherever the rule applies; bypass is not scoped by path."* §45.1 lists *"The records repository in full"* in the minimum reconstruction set.

Visibility is **private**: §40.3 describes the estate's repositories as private repositories under branch protection, and §45.3 treats org-wide export and detection on that basis.

### Commands

```bash
set -eu
# L0-P0-001 (lanes/L0-01-phase-0-contracts.md) already creates this repository
# as part of Phase 0. This step is therefore idempotent: it creates the
# repository only if T01's identity check did not already find it, and never
# overwrites or recreates a repository that already carries the right identity.
if gh api "/repos/${RECORDS_SLUG}" --silent 2>/dev/null; then
  echo "${RECORDS_SLUG} already exists (created by L0-P0-001) — skipping gh repo create."
else
  gh repo create "${RECORDS_SLUG}" \
    --private \
    --add-readme \
    --description "Append-only operational records and event stores (MasterSpec Section 97). Separate from control-plane by D89. Rewriting blocked by ruleset, appending permitted (D107)."
fi

gh api "/repos/${RECORDS_SLUG}" \
  --jq '{full_name:.full_name, private:.private, default_branch:.default_branch, archived:.archived}'
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | Repository exists under the org with the frozen name | `gh api "/repos/${RECORDS_SLUG}" --jq .full_name` | `$ORG/control-plane-records` |
| 2 | Repository is private | `gh api "/repos/${RECORDS_SLUG}" --jq .private` | `true` — **Note:** Declared as a lane convention (not spec-mandated). The private-repo requirement is a lane convention for security. |
| 3 | Default branch is `main` | `gh api "/repos/${RECORDS_SLUG}" --jq .default_branch` | `main` |
| 4 | Not archived | `gh api "/repos/${RECORDS_SLUG}" --jq .archived` | `false` |
| 5 | No ruleset exists yet (T05/T06 add them) | `gh api "/repos/${RECORDS_SLUG}/rulesets" --jq 'length'` | `0` |
| 6 | No branch protection was applied (D89: *"No protection rules — the store is append-only by convention and by the write path, not by review"*) | `gh api "/repos/${RECORDS_SLUG}/branches/main/protection" --silent 2>/dev/null; echo $?` | non-zero |

### SELF-VERIFY

```bash
set -eu
FAIL=0
[ "$(gh api "/repos/${RECORDS_SLUG}" --jq .full_name)"      = "${RECORDS_SLUG}" ] || { echo "FAIL full_name"; FAIL=1; }
[ "$(gh api "/repos/${RECORDS_SLUG}" --jq .private)"        = "true" ]           || { echo "FAIL private"; FAIL=1; }
[ "$(gh api "/repos/${RECORDS_SLUG}" --jq .default_branch)" = "main" ]           || { echo "FAIL default_branch"; FAIL=1; }
[ "$(gh api "/repos/${RECORDS_SLUG}" --jq .archived)"       = "false" ]          || { echo "FAIL archived"; FAIL=1; }
[ "$(gh api "/repos/${RECORDS_SLUG}/rulesets" --jq 'length')"  = "0" ]              || { echo "FAIL rulesets not empty"; FAIL=1; }
[ "$FAIL" = "0" ] && echo "L4-P1-T02 PASS" || echo "L4-P1-T02 BLOCKED"
```

**Expected output — exactly this single line:**

```
L4-P1-T02 PASS
```

### STOP RULE

Do not proceed to T03 if:

- `gh repo create` runs (the pre-check found the repository absent) and still fails, for any reason other than the idempotency case above → blocker with the full error text.
- The default branch is anything other than `main` → every ruleset condition and every command below assumes `main`. Do **not** rename it yourself. Blocker.
- `.private` is `false` → do **not** flip it yourself. Blocker.
- You are tempted to add branch protection, required reviews, or a CODEOWNERS file here → **do not**. D89 states this repository carries no protection rules; review protection here would make the records-writer unable to append, which is the entire point of the split. If instructed otherwise by anything other than this document, blocker.

`<TASK-ID>` = `T02`.

---

## TASK `L4-P1-T03` — Build the directory-per-item skeleton

**Size:** M · **Depends on:** T02 · **Writes:** `control-plane-records` (all paths)

This is the anti-conflict mechanism. PARTITION.md rule 3: *"No shared mutable file, ever. No lane appends to a shared index, list, or registry-of-everything. Directory-per-item only (one file per event, per record, per schema). This is why merges cannot conflict."* MasterSpec §97.3: *"written as its own file, one file per event, never a concurrent append to a shared period file, so parallel workflow runs never contend for the same file; period views are derived by aggregation."*

The seventeen record directories are transcribed from the canonical-record-store table in §97.2 and the artifact-inventory row at §99/§97 listing `records/` and `events/`. `exceptions.yaml`, `policies.yaml` and `patterns.yaml` appear in the same §97.2 table but live in the **control-plane** repository, not here — do not create them.

**Pre-existing content from `L0-P0-001`.** Before this task runs, `L0-P0-001` (`lanes/L0-01-phase-0-contracts.md`) has already pushed `README.md`, a root-level `records/.gitkeep` and a root-level `events/.gitkeep` to this repository's `main` branch. This task's clone therefore starts from that content, not an empty repository. The loop below still adds all 19 of its own markers (17 record-store subdirectories, `events/`, `bootstrap/`); writing `events/.gitkeep` replaces L0-P0-001's placeholder file at that same path, but the root-level `records/.gitkeep` is not one of the 19 and is untouched by this task. The post-task tracked-`.gitkeep` count is therefore **20**, not 19 — see the acceptance criteria below.

### Commands

```bash
set -eu
cd "${WORK}"
rm -rf "${RECORDS_DIR}"
gh repo clone "${RECORDS_SLUG}" "${RECORDS_DIR}"
cd "${RECORDS_DIR}"

git config user.name  "$(gh api user --jq '.name // .login')"
git config user.email "$(gh api user --jq '.login')@users.noreply.github.com"

# The nineteen canonical stores (MasterSpec Section 97.2, Section 97.3, plus
# bootstrap/). 19 per FD-059 (bootstrap/ counts as a store).
cat > /tmp/l4-dirs.txt <<'EOF'
records/incidents
records/postmortems
records/uat
records/estimates
records/deployments
records/restore-tests
records/decisions
records/decisions/pending
records/breaches
records/deletion-requests
records/security-reviews
records/eval
records/launches
records/demos
records/support
records/onboarding
records/leave
events
bootstrap
EOF

while read -r d; do
  [ -z "$d" ] && continue
  mkdir -p "$d"
  : > "$d/.gitkeep"
done < /tmp/l4-dirs.txt

git add -A
git commit -m "Create the canonical record and event store skeleton (MasterSpec 97.2, 97.3)

Directory-per-item: one file per record, one file per event, never a
concurrent append to a shared period file (97.3; PARTITION.md rule 3)."
git push origin main

git ls-files | sort
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | Exactly 20 `.gitkeep` files are tracked (this task's own 19 markers, plus the root-level `records/.gitkeep` `L0-P0-001` already committed) | `git -C "${RECORDS_DIR}" ls-files \| grep -c '\.gitkeep$'` | `20` |
| 2 | Every listed directory is tracked, none missing | `while read -r d; do git -C "${RECORDS_DIR}" ls-files --error-unmatch "$d/.gitkeep" >/dev/null 2>&1 \|\| echo "MISSING $d"; done < /tmp/l4-dirs.txt; echo DONE` | `DONE` with no `MISSING` line |
| 3 | No `exceptions.yaml`, `policies.yaml` or `patterns.yaml` here (they live in `control-plane`) | `git -C "${RECORDS_DIR}" ls-files \| grep -cE '^(exceptions|policies|patterns)\.yaml$'` | `0` |
| 4 | No shared index / aggregate file was created | `git -C "${RECORDS_DIR}" ls-files \| grep -cE '(index|all|_all|aggregate)\.(ya?ml|json|csv)$'` | `0` |
| 5 | Skeleton is on the remote default branch | `git -C "${RECORDS_DIR}" rev-parse HEAD` and `gh api "/repos/${RECORDS_SLUG}/commits/main" --jq .sha` | the two SHAs are identical |
| 6 | `events/` is a directory, not a file | `git -C "${RECORDS_DIR}" ls-files events/ \| head -1` | `events/.gitkeep` |

### SELF-VERIFY

```bash
set -eu
cd "${RECORDS_DIR}"
FAIL=0
N=$(git ls-files | grep -c '\.gitkeep$')
[ "$N" = "20" ] || { echo "FAIL gitkeep count=$N expected 20"; FAIL=1; }
while read -r d; do
  [ -z "$d" ] && continue
  git ls-files --error-unmatch "$d/.gitkeep" >/dev/null 2>&1 || { echo "FAIL missing $d"; FAIL=1; }
done < /tmp/l4-dirs.txt
[ "$(git ls-files | grep -cE '^(exceptions|policies|patterns)\.yaml$')" = "0" ] || { echo "FAIL registry file present"; FAIL=1; }
[ "$(git rev-parse HEAD)" = "$(gh api "/repos/${RECORDS_SLUG}/commits/main" --jq .sha)" ] || { echo "FAIL not pushed"; FAIL=1; }
[ "$FAIL" = "0" ] && echo "L4-P1-T03 PASS" || echo "L4-P1-T03 BLOCKED"
```

**Expected output — exactly this single line:**

```
L4-P1-T03 PASS
```

### STOP RULE

Do not proceed to T04 if:

- The `.gitkeep` count is anything other than 20 (this task's 19 markers plus the root-level `records/.gitkeep` `L0-P0-001` already committed) → you added or omitted a directory. Do **not** add a store that is not in `/tmp/l4-dirs.txt`; the §97.2 table is the complete inventory and a new store is a governed addition, not an executor's choice. Blocker.
- `git push origin main` is rejected → nothing should be blocking it yet (T05 has not run). Blocker with the full rejection text.
- You believe a store from §97.2 is missing from the list → do **not** add it. Blocker naming the store and the §97.2 row.

`<TASK-ID>` = `T03`.

---

## TASK `L4-P1-T04` — Root documents: `README.md`, `CONVENTIONS.md`, `.gitignore`

**Size:** M · **Depends on:** T03 · **Writes:** `control-plane-records/README.md`, `/CONVENTIONS.md`, `/.gitignore`

`CONVENTIONS.md` is the written form of the rules a future writer must not violate: UTC timestamps (§97.1), `record_schema_version` on every record (§97.2), corrections as follow-up records never in-place edits (§97.2, §63.1, invariant 47), one file per event (§97.3), and the write-path split (§97.1, D89).

### Commands

```bash
set -eu
cd "${RECORDS_DIR}"

cat > README.md <<'EOF'
# control-plane-records

Append-only operational records and event stores for the operating system.

This repository exists **separately from `control-plane`** by decision **D89**
(MasterSpec Section 40.1): a GitHub ruleset bypass actor bypasses the rule
wherever the rule applies and is not scoped by path, so a credential able to
write `records/**` inside `control-plane` would in fact be an unscoped write
credential on `people.yaml`, `roles.yaml`, `exceptions.yaml` and `policies.yaml`.
Splitting the store makes that violation impossible rather than merely
observable.

## What is here

| Tree | Holds |
|---|---|
| `records/` | The canonical record stores of MasterSpec Section 97.2 |
| `events/` | The append-only event log of Section 97.3, one file per event |
| `bootstrap/` | Write-path proof artifacts from Phase 1 setup. Not a record store. |

## Protection posture

- **No review protection.** No branch protection, no required reviews, no
  CODEOWNERS. The store is append-only by convention and by the write path,
  not by review (D89).
- **Rewriting is blocked absolutely.** A repository ruleset with **no bypass
  actor** blocks force pushes, branch deletion and tag deletion, and requires
  verified signatures. Ordinary appends are fast-forward commits and are
  unaffected (**D107**).
- **History is anchored elsewhere.** The reconciler records this repository's
  default-branch head SHA and commit count into the fully protected
  `control-plane` repository once per run; a head that does not descend from the
  last anchor is Blocking drift at Level 5 (D107, Section 53.2).

> The records repository is unprotected against *review*, deliberately, and
> protected against *rewriting*, absolutely.

## Rules before you write anything

Read `CONVENTIONS.md`. It is binding.
EOF

cat > CONVENTIONS.md <<'EOF'
# Binding conventions for `control-plane-records`

Source: MasterSpec v4.0 Sections 97.1, 97.2, 97.3, 97.6, 63.1; invariants 46 and
47 (Section 101.7); decisions D76, D89, D107; PARTITION.md rule 3.

## 1. Directory-per-item. No shared mutable file, ever.

One file per record. One file per event. Never a concurrent append to a shared
period file, an index, a list, or a registry-of-everything. Period views and
aggregates are **derived by aggregation at read time** and are never stored here
(Section 97.3; PARTITION.md rule 3).

Adding an index file to this repository is a defect, not an optimisation.

## 2. Nothing is ever edited in place, and nothing is ever deleted.

Records never edit in place; **corrections are follow-up records** (Section
97.2). State transitions are effective-dated with `start_date` and `end_date`,
never mutated (Section 63.1). Invariant 47: history is append-only for state,
decisions, approvals and records.

A mistaken record stays. Write the correcting record beside it.

## 3. Time is written one way.

Every record and event timestamp is stored in **UTC with its offset**, so
records written by any host, runner or human compare directly (Section 97.1).
Never a runner's local time. Any rule expressed in business days or working
hours resolves against the declared working calendar and operating timezone
held in `records/leave/` — never against the runner clock.

## 4. Every record carries the envelope.

Every record carries `record_schema_version`, `id`, `product` and `timestamp`.
An absent `record_schema_version` reads as version 1, but the field is stated
explicitly on every record written from Phase 1 onward (Section 97.2).

Every event carries the full envelope, and an event missing any envelope field
is **rejected at write time** (Section 97.3):
`event_schema_version`, `event_id`, `event_type`, `occurred_at`, `recorded_at`,
`actor`, `product`, `subject_ref`, `payload`.

`event_type` is drawn from the closed enum declared in `platform.yaml` in the
`control-plane` repository — never free text, never renamed once shipped
(Section 97.3).

## 5. Path and filename conventions

| Tree | Path shape | Example (from Section 97.2 / 97.3) |
|---|---|---|
| Incidents | `records/incidents/YYYY-MM-DD-<product>-NNN.yaml` | `records/incidents/2026-09-14-solvox-001.yaml` |
| Postmortems | `records/postmortems/YYYY-MM-DD-<product>.yaml` | `records/postmortems/2026-09-16-solvox.yaml` |
| Decisions | `records/decisions/DEC-YYYY-MM-DD-NNN.yaml` | `records/decisions/DEC-2026-09-10-003.yaml` |
| Pending decisions | `records/decisions/pending/DEC-YYYY-MM-DD-NNN.yaml` | moves to `records/decisions/` when decided |
| Deployments | `records/deployments/DEP-YYYY-MM-DD-NNN.yaml` | `DEP-2026-09-12-014` |
| Demos | `records/demos/DEMO-YYYY-MM-DD-NNN.yaml` | `DEMO-2026-09-11-002` |
| Events | `events/YYYY-MM-DD/EVT-YYYY-MM-DD-NNNNNN.yaml` | `events/2026-09-14/EVT-2026-09-14-000317.yaml` |

The date partition under `events/` is a directory, created on demand by the
writer. It is not an index and carries no state of its own.

## 6. The write path is split by author (Section 97.1, D89)

| Author | Path |
|---|---|
| Workflows | The **records-writer** GitHub App installation token, `contents: write` scoped to this repository alone, reaching no registry at all. It writes records; **it approves nothing** (D76 as amended by D89). |
| Humans | Ordinary pull requests through the normal review lane. |

Nobody edits a record file by hand to report a manual result. Manual results
reach the store only through the **RECORD-VERIFICATION-RESULT**
`workflow_dispatch` (Section 97.2).

## 7. Commits are signed

The default branch requires verified signatures. The records-writer writes
through the REST Contents API, whose commits GitHub signs and marks Verified
with the App as author. A commit on the default branch that is unsigned, or
signed by any other identity, is **Blocking drift** (D107).

Consequence for humans: a plain `git push` of a locally unsigned commit to
`main` here will be rejected by the ruleset. Sign your commits or write through
the API.

## 8. What this repository is not

Not a work surface. Blocker issues, planning and discussion belong in
`control-plane`. Not a place for registries: `exceptions.yaml`, `policies.yaml`
and `patterns.yaml` live in `control-plane` even though Section 97.2 lists them
beside these stores.

## 9. Retention

Append-only permanence applies to state, decisions, approvals and canonical
records — everything in Section 97.2 keeps its full history with effective
dating. Raw activity telemetry may be aggregated or discarded after its declared
diagnostic window; retention classes are declared in the control plane and owned
by the Founder (Section 97.6, Section 63.1, invariant 47).
EOF

cat > .gitignore <<'EOF'
# Credentials must never enter this repository.
*.pem
*.key
*.p12
*.pfx
.env
.env.*
EOF

git add README.md CONVENTIONS.md .gitignore
git commit -m "Add README, binding CONVENTIONS and credential .gitignore

Transcribes MasterSpec 97.1/97.2/97.3/97.6, 63.1, invariant 47, D76/D89/D107."
git push origin main
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | All three root files tracked | `git -C "${RECORDS_DIR}" ls-files README.md CONVENTIONS.md .gitignore \| wc -l` | `3` |
| 2 | `CONVENTIONS.md` states the directory-per-item rule | `grep -c 'No shared mutable file, ever' "${RECORDS_DIR}/CONVENTIONS.md"` | `1` |
| 3 | `CONVENTIONS.md` states the UTC rule | `grep -c 'UTC with its offset' "${RECORDS_DIR}/CONVENTIONS.md"` | `1` |
| 4 | `CONVENTIONS.md` states the no-in-place-edit rule | `grep -c 'corrections are follow-up records' "${RECORDS_DIR}/CONVENTIONS.md"` | `1` |
| 5 | `.gitignore` blocks private keys | `grep -c '^\*\.pem$' "${RECORDS_DIR}/.gitignore"` | `1` |
| 6 | Pushed to remote | `[ "$(git -C "${RECORDS_DIR}" rev-parse HEAD)" = "$(gh api "/repos/${RECORDS_SLUG}/commits/main" --jq .sha)" ] && echo SYNCED` | `SYNCED` |

### SELF-VERIFY

```bash
set -eu
cd "${RECORDS_DIR}"
FAIL=0
[ "$(git ls-files README.md CONVENTIONS.md .gitignore | wc -l | tr -d ' ')" = "3" ] || { echo "FAIL root files"; FAIL=1; }
for s in "No shared mutable file, ever" "UTC with its offset" "corrections are follow-up records" "records-writer"; do
  grep -q "$s" CONVENTIONS.md || { echo "FAIL CONVENTIONS missing: $s"; FAIL=1; }
done
grep -q '^\*\.pem$' .gitignore || { echo "FAIL gitignore pem"; FAIL=1; }
[ "$(git rev-parse HEAD)" = "$(gh api "/repos/${RECORDS_SLUG}/commits/main" --jq .sha)" ] || { echo "FAIL not pushed"; FAIL=1; }
[ "$FAIL" = "0" ] && echo "L4-P1-T04 PASS" || echo "L4-P1-T04 BLOCKED"
```

**Expected output — exactly this single line:**

```
L4-P1-T04 PASS
```

### STOP RULE

Do not proceed to T05 if:

- Any heredoc was altered, abbreviated or reworded. These documents are transcriptions of binding spec text; paraphrasing them changes what future writers are told. Re-run the task verbatim.
- The push is rejected → blocker with the full rejection text.
- You are tempted to add a `CODEOWNERS` file → **do not**. This repository carries no review protection (D89).

`<TASK-ID>` = `T04`.

---

## TASK `L4-P1-T05` — Arm the no-bypass **branch** ruleset

**Size:** M · **Depends on:** T04 · **Writes:** ruleset on `${RECORDS_SLUG}`; local file `/tmp/records-append-only.json`

D107, verbatim: *"A repository ruleset on the records repository's default branch blocks force pushes, branch deletion and tag deletion, with **no bypass actor**. Ordinary appends are unaffected — they are fast-forward commits, which the ruleset permits. The credential can therefore write freely and cannot rewrite."*

`required_signatures` is added separately in **T08** so that T07's negative tests attribute their rejections to exactly one rule.

### Commands

```bash
set -eu
cat > /tmp/records-append-only.json <<'EOF'
{
  "name": "records-append-only",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {
    "ref_name": {
      "include": ["~DEFAULT_BRANCH"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" }
  ]
}
EOF

gh api --method POST "/repos/${RECORDS_SLUG}/rulesets" \
  --input /tmp/records-append-only.json \
  --jq '{id:.id, name:.name, target:.target, enforcement:.enforcement}'

export BRANCH_RS_ID="$(gh api "/repos/${RECORDS_SLUG}/rulesets" \
  --jq '.[] | select(.name=="records-append-only") | .id')"
echo "BRANCH_RS_ID=${BRANCH_RS_ID}"
echo "export BRANCH_RS_ID=${BRANCH_RS_ID}" >> "${SECRETS_DIR}/l4-ids.env"

gh api "/repos/${RECORDS_SLUG}/rulesets/${BRANCH_RS_ID}" \
  --jq '{name:.name, target:.target, enforcement:.enforcement, bypass_count:(.bypass_actors|length), rules:([.rules[].type]|sort)}'
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | Ruleset exists with the frozen name | `gh api "/repos/${RECORDS_SLUG}/rulesets" --jq '.[] \| select(.name=="records-append-only") \| .name'` | `records-append-only` |
| 2 | It is **active**, not evaluate/disabled | `gh api "/repos/${RECORDS_SLUG}/rulesets/${BRANCH_RS_ID}" --jq .enforcement` | `active` |
| 3 | **No bypass actor** (D107, D89) | `gh api "/repos/${RECORDS_SLUG}/rulesets/${BRANCH_RS_ID}" --jq '.bypass_actors \| length'` | `0` |
| 4 | It carries exactly the two rewrite-blocking rules | `gh api "/repos/${RECORDS_SLUG}/rulesets/${BRANCH_RS_ID}" --jq '[.rules[].type]\|sort'` | `["deletion","non_fast_forward"]` |
| 5 | It targets the default branch | `gh api "/repos/${RECORDS_SLUG}/rulesets/${BRANCH_RS_ID}" --jq '.conditions.ref_name.include'` | `["~DEFAULT_BRANCH"]` |
| 6 | It does **not** carry a `pull_request` rule (no review protection — D89) | `gh api "/repos/${RECORDS_SLUG}/rulesets/${BRANCH_RS_ID}" --jq '[.rules[].type] \| index("pull_request") // "none"'` | `"none"` |

### SELF-VERIFY

```bash
set -eu
. "${SECRETS_DIR}/l4-ids.env"
OUT="$(gh api "/repos/${RECORDS_SLUG}/rulesets/${BRANCH_RS_ID}" \
  --jq '{enforcement:.enforcement,bypass:(.bypass_actors|length),rules:([.rules[].type]|sort),include:.conditions.ref_name.include}')"
echo "$OUT"
[ "$OUT" = '{"enforcement":"active","bypass":0,"rules":["deletion","non_fast_forward"],"include":["~DEFAULT_BRANCH"]}' ] \
  && echo "L4-P1-T05 PASS" || echo "L4-P1-T05 BLOCKED"
```

**Expected output — exactly these two lines:**

```
{"enforcement":"active","bypass":0,"rules":["deletion","non_fast_forward"],"include":["~DEFAULT_BRANCH"]}
L4-P1-T05 PASS
```

### STOP RULE

Do not proceed to T06 if:

- `bypass_actors` is anything but empty. A bypass actor is exempt from **every** rule in the ruleset it is listed on (D89), so one entry voids the whole control. Do not add yourself, the org admin role, or the App. Blocker.
- `enforcement` is `evaluate` or `disabled` → a ruleset that reads armed and is not is exactly the silent-gate failure §99.6 risk 5 names. Blocker.
- The API returns `403` or `404` on `POST /rulesets` → the token lacks admin rights on the repository (EXT-02). Blocker.
- More than one ruleset named `records-append-only` exists → a partial prior run. Do **not** delete either. Blocker.

`<TASK-ID>` = `T05`.

---

## TASK `L4-P1-T06` — Arm the no-bypass **tag** ruleset

**Size:** S · **Depends on:** T02 · **Writes:** ruleset on `${RECORDS_SLUG}`; `/tmp/records-tags-immutable.json`

D107 requires tag deletion to be blocked as well as branch deletion. GitHub expresses tag rules in a ruleset with `"target": "tag"`, which is a separate object from the branch ruleset.

### Commands

```bash
set -eu
cat > /tmp/records-tags-immutable.json <<'EOF'
{
  "name": "records-tags-immutable",
  "target": "tag",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {
    "ref_name": {
      "include": ["~ALL"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" }
  ]
}
EOF

gh api --method POST "/repos/${RECORDS_SLUG}/rulesets" \
  --input /tmp/records-tags-immutable.json \
  --jq '{id:.id, name:.name, target:.target}'

export TAG_RS_ID="$(gh api "/repos/${RECORDS_SLUG}/rulesets" \
  --jq '.[] | select(.name=="records-tags-immutable") | .id')"
echo "TAG_RS_ID=${TAG_RS_ID}"
echo "export TAG_RS_ID=${TAG_RS_ID}" >> "${SECRETS_DIR}/l4-ids.env"

gh api "/repos/${RECORDS_SLUG}/rulesets" --jq '[.[] | {name,target,enforcement}]'
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | Tag ruleset exists | `gh api "/repos/${RECORDS_SLUG}/rulesets/${TAG_RS_ID}" --jq .name` | `records-tags-immutable` |
| 2 | Target is `tag` | `gh api "/repos/${RECORDS_SLUG}/rulesets/${TAG_RS_ID}" --jq .target` | `tag` |
| 3 | No bypass actor | `gh api "/repos/${RECORDS_SLUG}/rulesets/${TAG_RS_ID}" --jq '.bypass_actors \| length'` | `0` |
| 4 | Active | `gh api "/repos/${RECORDS_SLUG}/rulesets/${TAG_RS_ID}" --jq .enforcement` | `active` |
| 5 | Applies to all tags | `gh api "/repos/${RECORDS_SLUG}/rulesets/${TAG_RS_ID}" --jq '.conditions.ref_name.include'` | `["~ALL"]` |
| 6 | Exactly two rulesets exist on the repository | `gh api "/repos/${RECORDS_SLUG}/rulesets" --jq 'length'` | `2` |

### SELF-VERIFY

```bash
set -eu
. "${SECRETS_DIR}/l4-ids.env"
OUT="$(gh api "/repos/${RECORDS_SLUG}/rulesets/${TAG_RS_ID}" \
  --jq '{target:.target,enforcement:.enforcement,bypass:(.bypass_actors|length),rules:([.rules[].type]|sort),include:.conditions.ref_name.include}')"
echo "$OUT"
N="$(gh api "/repos/${RECORDS_SLUG}/rulesets" --jq 'length')"
[ "$OUT" = '{"target":"tag","enforcement":"active","bypass":0,"rules":["deletion","non_fast_forward"],"include":["~ALL"]}' ] \
  && [ "$N" = "2" ] && echo "L4-P1-T06 PASS" || echo "L4-P1-T06 BLOCKED"
```

**Expected output — exactly these two lines:**

```
{"target":"tag","enforcement":"active","bypass":0,"rules":["deletion","non_fast_forward"],"include":["~ALL"]}
L4-P1-T06 PASS
```

### STOP RULE

Do not proceed to T07 if the ruleset count is not exactly `2`, if either ruleset carries a bypass actor, or if `POST` fails. Blocker with the full API response body. `<TASK-ID>` = `T06`.

---

## TASK `L4-P1-T07` — Prove: rewriting blocked, appending permitted

**Size:** M · **Depends on:** T05, T06 · **Writes:** one commit to `bootstrap/` in `control-plane-records`

§99.6 risk 5: *"GitHub tier or behaviour dependencies failing silently — an unavailable protection feature reproduces the silent-gate failure"*, mitigated by a *"Verify-before-Phase-1 checklist"*. A ruleset that exists is not a ruleset that works. This task executes it **negatively** — the same discipline §98.2 Phase 1 applies to its own completion checks.

Three proofs: (a) a force push is rejected, (b) a ref deletion is rejected, (c) an ordinary fast-forward append succeeds.

### Commands

```bash
set -eu
cd "${RECORDS_DIR}"
git fetch origin
git checkout main
git reset --hard origin/main
BASE_SHA="$(git rev-parse HEAD)"
echo "BASE_SHA=${BASE_SHA}"

# ---------- (c) POSITIVE: a fast-forward append must succeed ----------
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
mkdir -p bootstrap
cat > "bootstrap/t07-append-proof.yaml" <<EOF
proof: fast-forward-append-permitted
decision: D107
written_at: ${STAMP}
note: >-
  Ordinary appends are fast-forward commits, which the ruleset permits.
EOF
git add bootstrap/t07-append-proof.yaml
git commit -m "bootstrap: prove fast-forward append is permitted (D107)"
git push origin main
APPEND_SHA="$(git rev-parse HEAD)"
echo "APPEND_RESULT=OK APPEND_SHA=${APPEND_SHA}"

# ---------- (a) NEGATIVE: a force push must be rejected ----------
git checkout -B t07-rewrite "${BASE_SHA}"
git commit --allow-empty -m "bootstrap: rewrite attempt that MUST be rejected"
set +e
git push --force origin "HEAD:main" > /tmp/t07-force.log 2>&1
FORCE_RC=$?
set -e
echo "FORCE_RC=${FORCE_RC}"
cat /tmp/t07-force.log

# ---------- (b) NEGATIVE: deleting the default branch ref must be rejected ----------
set +e
gh api --method DELETE "/repos/${RECORDS_SLUG}/git/refs/heads/main" > /tmp/t07-delete.log 2>&1
DELETE_RC=$?
set -e
echo "DELETE_RC=${DELETE_RC}"
cat /tmp/t07-delete.log

# ---------- cleanup of the local rewrite branch only ----------
git checkout main
git branch -D t07-rewrite
git fetch origin
git reset --hard origin/main
echo "HEAD_NOW=$(git rev-parse HEAD)"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The fast-forward append reached the remote | `gh api "/repos/${RECORDS_SLUG}/contents/bootstrap/t07-append-proof.yaml" --jq .name` | `t07-append-proof.yaml` |
| 2 | The force push failed | `echo $FORCE_RC` (captured above) | non-zero |
| 3 | The force push was rejected **by the ruleset**, not by a network error | `grep -ciE 'cannot force-push|non-fast-forward|GH013|rule violations' /tmp/t07-force.log` | `1` or greater |
| 4 | The ref deletion failed | `echo $DELETE_RC` | non-zero |
| 5 | The ref deletion was rejected by the ruleset | `grep -ciE 'rule violations|deletion|protected' /tmp/t07-delete.log` | `1` or greater |
| 6 | `main` still points at the appended commit — no rewrite occurred | `gh api "/repos/${RECORDS_SLUG}/commits/main" --jq .sha` equals `$APPEND_SHA` | the two SHAs are identical |
| 7 | The rewrite branch was not left on the remote | `gh api "/repos/${RECORDS_SLUG}/branches" --jq '[.[].name]'` | `["main"]` |

### SELF-VERIFY

```bash
set -eu
cd "${RECORDS_DIR}"
FAIL=0
gh api "/repos/${RECORDS_SLUG}/contents/bootstrap/t07-append-proof.yaml" --jq .name >/dev/null 2>&1 \
  || { echo "FAIL append did not land"; FAIL=1; }
grep -qiE 'cannot force-push|non-fast-forward|GH013|rule violations' /tmp/t07-force.log \
  || { echo "FAIL force push was NOT rejected by the ruleset"; FAIL=1; }
grep -qiE 'rule violations|deletion|protected|"status": *"4' /tmp/t07-delete.log \
  || { echo "FAIL branch deletion was NOT rejected"; FAIL=1; }
[ "$(gh api "/repos/${RECORDS_SLUG}/branches" --jq '[.[].name]')" = '["main"]' ] \
  || { echo "FAIL stray remote branch"; FAIL=1; }
[ "$FAIL" = "0" ] && echo "L4-P1-T07 PASS" || echo "L4-P1-T07 BLOCKED"
```

**Expected output — exactly this single line:**

```
L4-P1-T07 PASS
```

### STOP RULE

Do not proceed to T08 if:

- **The force push SUCCEEDED.** This is the most serious failure in this document: append-only is asserted and not enforced, which is the exact condition D107 exists to remove. Immediately re-run T05's SELF-VERIFY, then file a blocker titled `BLOCKER L4-P1-T07: force push succeeded against records-append-only ruleset` and stop the entire lane.
- The append was rejected → appends must be unaffected (D107). Blocker; do **not** weaken the ruleset to make the append pass.
- The branch deletion succeeded → blocker, and note in the issue that `main` must be restored from `$BASE_SHA`, which is printed in the task output.
- Rejection text does not match either grep pattern → do not assume success from a non-zero exit alone; a non-zero exit could be a network failure. Blocker with `/tmp/t07-force.log` and `/tmp/t07-delete.log` attached verbatim.

`<TASK-ID>` = `T07`.

---

## TASK `L4-P1-T08` — Add `required_signatures` and prove it

**Size:** M · **Depends on:** T07 · **Blocked by:** D-L4-02 must be answered · **Writes:** the branch ruleset; one commit to `bootstrap/` via the API

D107, verbatim: *"Commits are signed by the writing identity. The records-writer signs every commit, and a commit on the default branch that is unsigned, or signed by any other identity, is Blocking drift."*

**Read this before running.** After this task, a plain `git push` of a locally unsigned commit to `main` in `control-plane-records` will be rejected. Every remaining write in this document goes through the REST Contents API, whose commits GitHub signs and marks Verified.

### Commands

```bash
set -eu
. "${SECRETS_DIR}/l4-ids.env"

cat > /tmp/records-append-only.json <<'EOF'
{
  "name": "records-append-only",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {
    "ref_name": {
      "include": ["~DEFAULT_BRANCH"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_signatures" }
  ]
}
EOF

gh api --method PUT "/repos/${RECORDS_SLUG}/rulesets/${BRANCH_RS_ID}" \
  --input /tmp/records-append-only.json \
  --jq '{name:.name, bypass:(.bypass_actors|length), rules:([.rules[].type]|sort)}'

# ---------- NEGATIVE: an unsigned local commit must now be rejected ----------
cd "${RECORDS_DIR}"
git fetch origin && git reset --hard origin/main
git -c commit.gpgsign=false commit --allow-empty -m "bootstrap: unsigned commit that MUST be rejected"
set +e
git push origin main > /tmp/t08-unsigned.log 2>&1
UNSIGNED_RC=$?
set -e
echo "UNSIGNED_RC=${UNSIGNED_RC}"
cat /tmp/t08-unsigned.log
git reset --hard origin/main

# ---------- POSITIVE: an API-written commit must be accepted and Verified ----------
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
CONTENT="$(printf 'proof: api-write-is-signed\ndecision: D107\nwritten_at: %s\n' "${STAMP}" | base64 -w0 2>/dev/null || printf 'proof: api-write-is-signed\ndecision: D107\nwritten_at: %s\n' "${STAMP}" | base64)"
gh api --method PUT "/repos/${RECORDS_SLUG}/contents/bootstrap/t08-signature-proof.yaml" \
  -f message="bootstrap: prove API writes satisfy required_signatures (D107)" \
  -f content="${CONTENT}" \
  --jq '{sha:.commit.sha, verified:.commit.verification.verified, reason:.commit.verification.reason}'
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The branch ruleset now carries all three rules | `gh api "/repos/${RECORDS_SLUG}/rulesets/${BRANCH_RS_ID}" --jq '[.rules[].type]\|sort'` | `["deletion","non_fast_forward","required_signatures"]` |
| 2 | Still no bypass actor after the update | `gh api "/repos/${RECORDS_SLUG}/rulesets/${BRANCH_RS_ID}" --jq '.bypass_actors\|length'` | `0` |
| 3 | The unsigned push was rejected | `echo $UNSIGNED_RC` | non-zero |
| 4 | Rejected specifically for signatures | `grep -ciE 'verified signature|signature' /tmp/t08-unsigned.log` | `1` or greater |
| 5 | The API-written commit landed | `gh api "/repos/${RECORDS_SLUG}/contents/bootstrap/t08-signature-proof.yaml" --jq .name` | `t08-signature-proof.yaml` |
| 6 | That commit is **Verified** | `gh api "/repos/${RECORDS_SLUG}/commits/main" --jq .commit.verification.verified` | `true` |

### SELF-VERIFY

```bash
set -eu
. "${SECRETS_DIR}/l4-ids.env"
FAIL=0
R="$(gh api "/repos/${RECORDS_SLUG}/rulesets/${BRANCH_RS_ID}" --jq '{bypass:(.bypass_actors|length),rules:([.rules[].type]|sort)}')"
echo "$R"
[ "$R" = '{"bypass":0,"rules":["deletion","non_fast_forward","required_signatures"]}' ] || { echo "FAIL ruleset shape"; FAIL=1; }
grep -qiE 'signature' /tmp/t08-unsigned.log || { echo "FAIL unsigned push not rejected for signatures"; FAIL=1; }
[ "$(gh api "/repos/${RECORDS_SLUG}/commits/main" --jq .commit.verification.verified)" = "true" ] || { echo "FAIL head not verified"; FAIL=1; }
gh api "/repos/${RECORDS_SLUG}/contents/bootstrap/t08-signature-proof.yaml" --jq .name >/dev/null || { echo "FAIL proof file absent"; FAIL=1; }
[ "$FAIL" = "0" ] && echo "L4-P1-T08 PASS" || echo "L4-P1-T08 BLOCKED"
```

**Expected output — exactly these two lines:**

```
{"bypass":0,"rules":["deletion","non_fast_forward","required_signatures"]}
L4-P1-T08 PASS
```

### STOP RULE

Do not proceed to T09 if:

- **D-L4-02 has not been answered by L0.** This task hard-codes option (a). Do not run it on your own authority.
- The unsigned push SUCCEEDED → `required_signatures` is not enforcing. Blocker.
- The API-written commit is **not** Verified → option (a) does not hold on this org's plan; that is a platform-behaviour finding of the §99.6 risk 5 class, and L0 must re-decide D-L4-02. Blocker, and state `verification.reason` verbatim in the issue.
- The `PUT` returns `422` → do not retry with a modified body. Blocker with the response.
- You are tempted to remove `required_signatures` so a later step is easier → **do not**. Blocker instead.

`<TASK-ID>` = `T08`.

---

## TASK `L4-P1-T09` — Create the `records-writer` GitHub App

**Size:** M · **Depends on:** T02 · **Writes:** a GitHub App in `${ORG}`; `${SECRETS_DIR}/records-writer.pem`; `${SECRETS_DIR}/l4-ids.env`

§40.1 fifth secrets tier, verbatim: *"The records-writer credential: a GitHub App installation token whose fine-grained `contents: write` is scoped to this repository alone"*. §97.1: it *"reaches no registry at all (D89)"*. D76 as amended: *"the credential writes records; it approves nothing."*

**GitHub App creation is a console operation.** There is no `gh` command that creates an App from nothing; the REST API only converts a manifest handed back by the browser flow. The console steps below are fully determined — every field value is given. Do not improvise a field.

### Console steps — perform in this exact order

Open `https://github.com/organizations/$ORG/settings/apps/new` (substitute your `$ORG`), then set exactly these values:

| Field | Value to enter |
|---|---|
| GitHub App name | `records-writer-$ORG` (GitHub App names are globally unique; the `-$ORG` suffix is required to avoid a collision, and is the only part that varies) |
| Description | `Fifth-tier machine credential. Writes records/** and events/** in control-plane-records only. Reaches no registry (D89). Approves nothing (D76 as amended by D89).` |
| Homepage URL | `https://github.com/$ORG/control-plane-records` |
| Webhook → Active | **unchecked** |
| Repository permissions → **Contents** | **Read and write** |
| Repository permissions → **Metadata** | **Read-only** (GitHub sets this mandatorily; leave it) |
| Every other repository permission | **No access** |
| Organization permissions | **No access** — all of them |
| Account permissions | **No access** — all of them |
| Where can this GitHub App be installed? | **Only on this account** |

Click **Create GitHub App**. On the resulting settings page, click **Generate a private key** and save the downloaded `.pem`.

### Commands — run immediately after the console steps

```bash
set -eu
# Move the downloaded key out of Downloads and out of every git working tree.
# Adjust only the source path if your browser saved it elsewhere.
mv "$HOME/Downloads/"records-writer-*.private-key.pem "${SECRETS_DIR}/records-writer.pem"
chmod 600 "${SECRETS_DIR}/records-writer.pem"

# Read the App id and slug from the App settings page (both are shown there),
# then bind them here. These two values are not secrets.
read -r -p "App ID (integer, from the App settings page): " APP_ID
read -r -p "App slug (the URL segment of the App settings page): " APP_SLUG
export APP_ID APP_SLUG
{
  echo "export APP_ID=${APP_ID}"
  echo "export APP_SLUG=${APP_SLUG}"
} >> "${SECRETS_DIR}/l4-ids.env"

# The App's own record, readable without an installation.
gh api "/apps/${APP_SLUG}" --jq '{slug:.slug, name:.name, permissions:.permissions, events:.events}'

# Prove the key is a usable RSA private key.
openssl rsa -in "${SECRETS_DIR}/records-writer.pem" -check -noout
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The App exists and is readable | `gh api "/apps/${APP_SLUG}" --jq .slug` | the value of `$APP_SLUG` |
| 2 | Permissions are exactly `contents: write` + `metadata: read` | `gh api "/apps/${APP_SLUG}" --jq '.permissions'` | `{"contents":"write","metadata":"read"}` |
| 3 | It requests **no** organisation permission | `gh api "/apps/${APP_SLUG}" --jq '[.permissions\|keys[]]\|sort'` | `["contents","metadata"]` |
| 4 | It subscribes to no events (nothing to receive; it writes) | `gh api "/apps/${APP_SLUG}" --jq '.events'` | `[]` |
| 5 | The private key is valid RSA | `openssl rsa -in "${SECRETS_DIR}/records-writer.pem" -check -noout` | `RSA key ok` |
| 6 | The key is **not** inside any git working tree | `git -C "${RECORDS_DIR}" ls-files \| grep -c '\.pem$'; git -C "${RECORDS_DIR}" status --porcelain \| grep -c '\.pem'` | `0` then `0` |
| 7 | The key file is not world-readable | `stat -c '%a' "${SECRETS_DIR}/records-writer.pem" 2>/dev/null \|\| echo 600` | `600` |

### SELF-VERIFY

```bash
set -eu
. "${SECRETS_DIR}/l4-ids.env"
FAIL=0
P="$(gh api "/apps/${APP_SLUG}" --jq '.permissions')"
echo "$P"
[ "$P" = '{"contents":"write","metadata":"read"}' ] || { echo "FAIL permissions are not exactly contents:write + metadata:read"; FAIL=1; }
[ "$(gh api "/apps/${APP_SLUG}" --jq '.events')" = "[]" ] || { echo "FAIL app subscribes to events"; FAIL=1; }
openssl rsa -in "${SECRETS_DIR}/records-writer.pem" -check -noout | grep -q 'RSA key ok' || { echo "FAIL private key"; FAIL=1; }
[ "$(git -C "${RECORDS_DIR}" ls-files | grep -c '\.pem$')" = "0" ] || { echo "FAIL pem tracked in git"; FAIL=1; }
[ "$FAIL" = "0" ] && echo "L4-P1-T09 PASS" || echo "L4-P1-T09 BLOCKED"
```

**Expected output — exactly these two lines:**

```
{"contents":"write","metadata":"read"}
L4-P1-T09 PASS
```

### STOP RULE

Do not proceed to T10 if:

- The permission object is anything other than `{"contents":"write","metadata":"read"}` — including a *read-only* `contents`, an added `issues`, `pull_requests`, `administration`, `members`, `workflows`, or any organisation permission. Over-scoping this credential re-creates exactly the unscoped-write condition D89 removed. Return to the App settings page, set every other permission to **No access**, re-run the SELF-VERIFY. If it still does not match, blocker.
- **The `.pem` was committed anywhere, or pasted into any file inside a git working tree.** Treat this as a credential exposure: it is a security incident under §43, not a cleanup task (§40.1). File the blocker, state which repository and which commit, and stop the lane.
- `Where can this GitHub App be installed?` was set to *Any account* → the credential is offerable outside the org. Change it to **Only on this account** and re-verify.
- You cannot find the App id or slug → they are on the App settings page URL and body. Do not guess. Blocker.

`<TASK-ID>` = `T09`.

---

## TASK `L4-P1-T10` — Install and scope the App to `control-plane-records` alone

**Size:** M · **Depends on:** T09 · **Writes:** an App installation in `${ORG}`; `${CP_DIR}/tools/records/rw-token.sh` (uncommitted until T12)

D89 is a scoping decision, and scoping is what this task proves. An App with `contents: write` installed on *All repositories* is precisely the unscoped write credential the decision exists to eliminate.

### Console steps

1. Open `https://github.com/organizations/$ORG/settings/apps/<APP_SLUG>/installations`.
2. Click **Install** next to your organisation.
3. Select **Only select repositories**.
4. In the repository picker choose **exactly one** repository: `control-plane-records`.
5. Click **Install**.

### Commands

```bash
set -eu
. "${SECRETS_DIR}/l4-ids.env"

# Installation identity and scoping, from the org side.
gh api "/orgs/${ORG}/installations" \
  --jq '.installations[] | select(.app_slug=="'"${APP_SLUG}"'") | {id, app_slug, repository_selection, permissions}'

export INSTALLATION_ID="$(gh api "/orgs/${ORG}/installations" \
  --jq '.installations[] | select(.app_slug=="'"${APP_SLUG}"'") | .id')"
echo "INSTALLATION_ID=${INSTALLATION_ID}"
echo "export INSTALLATION_ID=${INSTALLATION_ID}" >> "${SECRETS_DIR}/l4-ids.env"

# Token minting helper. Written to its final owned path; T12 commits it.
mkdir -p "${CP_DIR}/tools/records"
cat > "${CP_DIR}/tools/records/rw-token.sh" <<'EOF'
#!/usr/bin/env bash
# Mints a short-lived records-writer installation token.
# MasterSpec Section 40.1 fifth secrets tier; D89.
# Requires: APP_ID, INSTALLATION_ID, RW_PEM (path to the private key).
# Prints the token on stdout and nothing else. Never log the output.
set -euo pipefail

: "${APP_ID:?APP_ID not set}"
: "${INSTALLATION_ID:?INSTALLATION_ID not set}"
: "${RW_PEM:?RW_PEM not set}"
[ -r "${RW_PEM}" ] || { echo "rw-token.sh: cannot read ${RW_PEM}" >&2; exit 2; }

b64url() { openssl base64 -A | tr '+/' '-_' | tr -d '='; }

now="$(date +%s)"
header='{"alg":"RS256","typ":"JWT"}'
payload="$(printf '{"iat":%d,"exp":%d,"iss":"%s"}' "$((now - 60))" "$((now + 540))" "${APP_ID}")"
unsigned="$(printf '%s' "${header}" | b64url).$(printf '%s' "${payload}" | b64url)"
signature="$(printf '%s' "${unsigned}" | openssl dgst -sha256 -sign "${RW_PEM}" -binary | b64url)"
jwt="${unsigned}.${signature}"

curl -sS -X POST \
  -H "Authorization: Bearer ${jwt}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/app/installations/${INSTALLATION_ID}/access_tokens" \
| { command -v jq >/dev/null && jq -r '.token' || sed -n 's/.*"token": *"\([^"]*\)".*/\1/p'; }
EOF
chmod +x "${CP_DIR}/tools/records/rw-token.sh"

# Mint a token and enumerate exactly what the installation can reach.
export RW_PEM="${SECRETS_DIR}/records-writer.pem"
RW_TOKEN="$("${CP_DIR}/tools/records/rw-token.sh")"
[ -n "${RW_TOKEN}" ] || { echo "TOKEN MINT FAILED"; exit 1; }

curl -sS -H "Authorization: Bearer ${RW_TOKEN}" \
     -H "Accept: application/vnd.github+json" \
     https://api.github.com/installation/repositories \
| jq -c '{total_count, repos: [.repositories[].full_name]}'
```

> `${CP_DIR}` must be a clone of `control-plane` (EXT-03). If it is absent, run
> `gh repo clone "${CP_SLUG}" "${CP_DIR}"` first.

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The installation exists on the org | `gh api "/orgs/${ORG}/installations" --jq '[.installations[]\|select(.app_slug=="'"$APP_SLUG"'")]\|length'` | `1` |
| 2 | Scoping is **selected**, not *all* | `gh api "/orgs/${ORG}/installations" --jq '.installations[]\|select(.app_slug=="'"$APP_SLUG"'")\|.repository_selection'` | `selected` |
| 3 | Installation permissions are unchanged from the App | `gh api "/orgs/${ORG}/installations" --jq '.installations[]\|select(.app_slug=="'"$APP_SLUG"'")\|.permissions'` | `{"contents":"write","metadata":"read"}` |
| 4 | Token minting works | `RW_PEM="${SECRETS_DIR}/records-writer.pem" "${CP_DIR}/tools/records/rw-token.sh" \| cut -c1-4` | `ghs_` |
| 5 | The installation reaches **exactly one** repository | `curl -sS -H "Authorization: Bearer $RW_TOKEN" https://api.github.com/installation/repositories \| jq '.total_count'` | `1` |
| 6 | That one repository is `control-plane-records` | `curl -sS -H "Authorization: Bearer $RW_TOKEN" https://api.github.com/installation/repositories \| jq -c '[.repositories[].full_name]'` | `["$ORG/control-plane-records"]` |
| 7 | The helper never writes the token to disk | `grep -c 'RW_TOKEN\|>>' "${CP_DIR}/tools/records/rw-token.sh"` | `0` |

### SELF-VERIFY

```bash
set -eu
. "${SECRETS_DIR}/l4-ids.env"
export RW_PEM="${SECRETS_DIR}/records-writer.pem"
FAIL=0
SEL="$(gh api "/orgs/${ORG}/installations" --jq '.installations[]|select(.app_slug=="'"${APP_SLUG}"'")|.repository_selection')"
[ "$SEL" = "selected" ] || { echo "FAIL repository_selection=$SEL"; FAIL=1; }
RW_TOKEN="$("${CP_DIR}/tools/records/rw-token.sh")"
REPOS="$(curl -sS -H "Authorization: Bearer ${RW_TOKEN}" -H "Accept: application/vnd.github+json" \
  https://api.github.com/installation/repositories | jq -c '{n:.total_count,r:[.repositories[].full_name]}')"
echo "$REPOS"
[ "$REPOS" = "{\"n\":1,\"r\":[\"${RECORDS_SLUG}\"]}" ] || { echo "FAIL installation is not scoped to control-plane-records alone"; FAIL=1; }
[ "$FAIL" = "0" ] && echo "L4-P1-T10 PASS" || echo "L4-P1-T10 BLOCKED"
```

**Expected output — exactly these two lines (with your org substituted):**

```
{"n":1,"r":["$ORG/control-plane-records"]}
L4-P1-T10 PASS
```

### STOP RULE

Do not proceed to T11 if:

- `repository_selection` is `all` → **uninstall immediately** from the org settings page and reinstall with **Only select repositories**. If it still reads `all`, blocker.
- `total_count` is greater than `1`, or the list contains any repository other than `control-plane-records` — `control-plane` above all. This is the D89 violation condition itself. Remove the extra repositories from the installation, re-run SELF-VERIFY; if it does not clear, blocker and stop the lane.
- The token mint prints nothing or an error → do **not** paste the `.pem` into any online JWT tool. Blocker with the curl response body, redacting nothing except any `token` value.
- Any command you ran echoed the token into a log, a file, a shell history export or an issue body → treat as credential exposure under §43, revoke the key from the App settings page, and blocker.

`<TASK-ID>` = `T10`.

---

## TASK `L4-P1-T11` — Prove the App appends here and reaches no registry

**Size:** M · **Depends on:** T10, T08 · **Writes:** two commits to `bootstrap/` in `control-plane-records`, written by the App

§40.1, verbatim, on why the split was made: *"the credential cannot reach a registry, so the violation the old rule tried to detect becomes impossible rather than merely observable"*. This task executes that claim, positively and negatively.

### Commands

```bash
set -eu
. "${SECRETS_DIR}/l4-ids.env"
export RW_PEM="${SECRETS_DIR}/records-writer.pem"
RW_TOKEN="$("${CP_DIR}/tools/records/rw-token.sh")"

api() { curl -sS -H "Authorization: Bearer ${RW_TOKEN}" -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" "$@"; }

STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DAY="$(date -u +%Y-%m-%d)"

# ---------- POSITIVE 1: append a record-shaped file ----------
BODY_R="$(printf 'proof: records-writer-can-append-a-record\nwritten_at: %s\ndecision: D89\n' "${STAMP}" | base64 -w0 2>/dev/null || printf 'proof: records-writer-can-append-a-record\nwritten_at: %s\ndecision: D89\n' "${STAMP}" | base64)"
api -X PUT "https://api.github.com/repos/${RECORDS_SLUG}/contents/bootstrap/t11-record-write-proof.yaml" \
  -d "$(jq -nc --arg m "bootstrap: records-writer append proof (record path)" --arg c "${BODY_R}" '{message:$m,content:$c}')" \
  | jq -c '{path:.content.path, author:.commit.author.name, verified:.commit.verification.verified}'

# ---------- POSITIVE 2: append an event-shaped file under a date partition ----------
BODY_E="$(printf 'proof: records-writer-can-append-an-event\nwritten_at: %s\nsection: "97.3"\n' "${STAMP}" | base64 -w0 2>/dev/null || printf 'proof: records-writer-can-append-an-event\nwritten_at: %s\nsection: "97.3"\n' "${STAMP}" | base64)"
api -X PUT "https://api.github.com/repos/${RECORDS_SLUG}/contents/bootstrap/t11-event-write-proof.yaml" \
  -d "$(jq -nc --arg m "bootstrap: records-writer append proof (event path)" --arg c "${BODY_E}" '{message:$m,content:$c}')" \
  | jq -c '{path:.content.path, verified:.commit.verification.verified}'

# ---------- NEGATIVE 1: the credential must not READ control-plane ----------
CP_READ="$(api -o /dev/null -w '%{http_code}' "https://api.github.com/repos/${CP_SLUG}/contents/README.md")"
echo "CP_READ_STATUS=${CP_READ}"

# ---------- NEGATIVE 2: the credential must not WRITE control-plane ----------
CP_WRITE="$(api -o /tmp/t11-cpwrite.log -w '%{http_code}' -X PUT \
  "https://api.github.com/repos/${CP_SLUG}/contents/people.yaml" \
  -d "$(jq -nc '{message:"MUST BE REJECTED", content:"IyBtdXN0IG5vdCBsYW5kCg=="}')")"
echo "CP_WRITE_STATUS=${CP_WRITE}"
cat /tmp/t11-cpwrite.log

# ---------- NEGATIVE 3: the credential must not be able to approve anything ----------
PR_SCOPE="$(api -o /dev/null -w '%{http_code}' "https://api.github.com/repos/${RECORDS_SLUG}/pulls")"
echo "PULLS_STATUS=${PR_SCOPE}   # informational; the App holds no pull_requests permission"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | The record-path append landed | `gh api "/repos/${RECORDS_SLUG}/contents/bootstrap/t11-record-write-proof.yaml" --jq .name` | `t11-record-write-proof.yaml` |
| 2 | The event-path append landed | `gh api "/repos/${RECORDS_SLUG}/contents/bootstrap/t11-event-write-proof.yaml" --jq .name` | `t11-event-write-proof.yaml` |
| 3 | Both commits are Verified (D107 + T08) | `gh api "/repos/${RECORDS_SLUG}/commits/main" --jq .commit.verification.verified` | `true` |
| 4 | The head commit's author is the App, not a human | `gh api "/repos/${RECORDS_SLUG}/commits/main" --jq '.author.type'` | `Bot` |
| 5 | The credential cannot **read** `control-plane` | `echo $CP_READ` | `404` |
| 6 | The credential cannot **write** `control-plane` | `echo $CP_WRITE` | `404` |
| 7 | No file was created in `control-plane` | `gh api "/repos/${CP_SLUG}/commits" --jq '.[0].commit.message' \| grep -c 'MUST BE REJECTED'` | `0` |
| 8 | The App holds no permission that could approve | `gh api "/apps/${APP_SLUG}" --jq '[.permissions\|keys[]]\|sort'` | `["contents","metadata"]` |

### SELF-VERIFY

```bash
set -eu
. "${SECRETS_DIR}/l4-ids.env"
export RW_PEM="${SECRETS_DIR}/records-writer.pem"
RW_TOKEN="$("${CP_DIR}/tools/records/rw-token.sh")"
FAIL=0
for f in t11-record-write-proof.yaml t11-event-write-proof.yaml; do
  gh api "/repos/${RECORDS_SLUG}/contents/bootstrap/${f}" --jq .name >/dev/null 2>&1 \
    || { echo "FAIL append missing: ${f}"; FAIL=1; }
done
[ "$(gh api "/repos/${RECORDS_SLUG}/commits/main" --jq .commit.verification.verified)" = "true" ] \
  || { echo "FAIL head not verified"; FAIL=1; }
[ "$(gh api "/repos/${RECORDS_SLUG}/commits/main" --jq '.author.type')" = "Bot" ] \
  || { echo "FAIL head author is not the App"; FAIL=1; }
CPR="$(curl -sS -o /dev/null -w '%{http_code}' -H "Authorization: Bearer ${RW_TOKEN}" \
       -H "Accept: application/vnd.github+json" "https://api.github.com/repos/${CP_SLUG}/contents/README.md")"
CPW="$(curl -sS -o /dev/null -w '%{http_code}' -X PUT -H "Authorization: Bearer ${RW_TOKEN}" \
       -H "Accept: application/vnd.github+json" "https://api.github.com/repos/${CP_SLUG}/contents/people.yaml" \
       -d '{"message":"MUST BE REJECTED","content":"IyBtdXN0IG5vdCBsYW5kCg=="}')"
echo "control-plane read=${CPR} write=${CPW}"
[ "$CPR" = "404" ] || { echo "FAIL credential can see control-plane (status ${CPR})"; FAIL=1; }
[ "$CPW" = "404" ] || { echo "FAIL credential can attempt writes to control-plane (status ${CPW})"; FAIL=1; }
[ "$FAIL" = "0" ] && echo "L4-P1-T11 PASS" || echo "L4-P1-T11 BLOCKED"
```

**Expected output — exactly these two lines:**

```
control-plane read=404 write=404
L4-P1-T11 PASS
```

### STOP RULE

Do not proceed to T12 if:

- **`control-plane` write returned `200` or `201`.** A file was created in the control-plane repository by a machine credential. This is the D89 violation in the concrete, and §98.2 Phase 1's completion check states plainly that *"the records-writer holds no credential on this repository at all"*. Do not delete the file (invariant 47 forbids rewriting history to hide it). File the blocker, name the commit SHA, and stop the entire lane.
- `control-plane` read returned `200` → the installation is over-scoped; return to T10.
- `control-plane` read or write returned `403` rather than `404` → the credential *is* reaching the repository and being denied at permission level rather than not seeing it at all. That is a weaker property than D89 requires. Blocker.
- Either append failed → the write path does not work, which makes every downstream store empty and reproduces §99.6 risk 2 exactly. Blocker.
- The head commit's author type is not `Bot` → the write did not go through the installation token. Blocker.

`<TASK-ID>` = `T11`.

---

## TASK `L4-P1-T12` — Store ruleset and credential shape as code in `tools/records/`

**Size:** M · **Depends on:** T05, T06, T08, T10 · **Writes:** `control-plane` on branch `lane/4/p1-records-repo`, paths `tools/records/**` only

§45.1 minimum reconstruction set requires *"Branch protection and ruleset configuration, expressed as code where the platform permits, otherwise documented in the control-plane repository."* This task puts the live configuration under version control so the repository is rebuildable, and gives the reconciler a declared shape to compare against.

`tools/records/**` is owned exclusively by this lane (PARTITION.md). **Touch no other path in `control-plane`.**

### Commands

```bash
set -eu
. "${SECRETS_DIR}/l4-ids.env"

[ -d "${CP_DIR}/.git" ] || gh repo clone "${CP_SLUG}" "${CP_DIR}"
cd "${CP_DIR}"
git fetch origin
git checkout integration
git pull --ff-only
git checkout -b lane/4/p1-records-repo

mkdir -p tools/records/rulesets
cp /tmp/records-append-only.json    tools/records/rulesets/records-append-only.json
cp /tmp/records-tags-immutable.json tools/records/rulesets/records-tags-immutable.json

cat > tools/records/README.md <<'EOF'
# tools/records — records-repository configuration as code

Owned by lane L4 (PARTITION.md). Nothing here is edited by another lane.

| File | What it is |
|---|---|
| `rulesets/records-append-only.json` | The live **branch** ruleset on `control-plane-records` default branch. No bypass actor. Blocks force push and deletion; requires verified signatures (D107). |
| `rulesets/records-tags-immutable.json` | The live **tag** ruleset. No bypass actor. Blocks tag deletion (D107). |
| `records-writer-app.md` | The declared shape of the records-writer credential (Section 40.1 fifth tier, D89). Contains no secret. |
| `rw-token.sh` | Mints a short-lived installation token from the App id, installation id and private key supplied by the caller. Holds no secret. |

Kept here because MasterSpec Section 45.1 places *"Branch protection and ruleset
configuration, expressed as code where the platform permits"* in the minimum
reconstruction set, and the records repository is itself listed there in full.

## Reapplying after a rebuild

```
gh api --method POST "/repos/$ORG/control-plane-records/rulesets" \
  --input tools/records/rulesets/records-append-only.json
gh api --method POST "/repos/$ORG/control-plane-records/rulesets" \
  --input tools/records/rulesets/records-tags-immutable.json
```
EOF

cat > tools/records/records-writer-app.md <<EOF
# records-writer — declared credential shape

Fifth secrets tier (MasterSpec Section 40.1). Decision **D89**; supersedes the
path-scoped-bypass mechanism of **D76** in part.

| Property | Declared value |
|---|---|
| Kind | GitHub App installation token |
| App slug | \`${APP_SLUG}\` |
| App id | \`${APP_ID}\` |
| Installation id | \`${INSTALLATION_ID}\` |
| Repository permissions | \`contents: write\`, \`metadata: read\` — nothing else |
| Organisation permissions | none |
| Repository selection | **selected**, exactly one repository: \`${RECORDS_SLUG}\` |
| Reaches any registry? | **No.** \`people.yaml\`, \`roles.yaml\`, \`exceptions.yaml\` and \`policies.yaml\` live in \`control-plane\`, where this credential has no installation at all. |
| Approves anything? | **No.** It writes records; it approves nothing (D76 as amended by D89). |
| Bypass actor anywhere? | **No.** Neither ruleset on the records repository lists any bypass actor. |
| Rotation cadence | Quarterly (Section 40.1, "Fifth-tier operations", initial value) |
| Private key location | Machine-credential store on the host that uses it (Section 40.1). **Never in any repository.** |

## Not declared here

The operational-asset-inventory entry required by Section 49 — named rotator,
rotation runbook link, behavioural envelope, envelope-alert owner, expiry date —
lives in \`assets/**\`, owned by lane L5. See DECISION REQUIRED **D-L4-03** in
\`Code/implementation/lanes/L4-01-records-repo.md\`.

## Verification of the declaration above

\`\`\`bash
gh api "/orgs/$ORG/installations" \\
  --jq '.installations[] | select(.app_slug=="${APP_SLUG}") | {repository_selection, permissions}'
# expected: {"repository_selection":"selected","permissions":{"contents":"write","metadata":"read"}}
\`\`\`
EOF

# rw-token.sh was written to its final path in T10; ensure it is present and executable.
test -x tools/records/rw-token.sh
grep -q 'RW_PEM' tools/records/rw-token.sh

# Nothing outside tools/records may be staged.
git add tools/records
git status --porcelain

git commit -m "L4 Phase 1: records-repository ruleset and credential shape as code

Stores the live control-plane-records rulesets and the declared records-writer
credential shape under tools/records/ per MasterSpec 45.1 (minimum
reconstruction set). D89, D107.

Lane: L4. Paths touched: tools/records/** only."

git push -u origin lane/4/p1-records-repo

gh pr create --repo "${CP_SLUG}" --base integration --head lane/4/p1-records-repo \
  --title "L4 P1: control-plane-records ruleset and records-writer shape as code" \
  --body "Lane L4, Phase 1, task L4-P1-T12.

Adds \`tools/records/**\` only (lane-owned path, PARTITION.md).

- \`rulesets/records-append-only.json\` — live branch ruleset, no bypass actor, blocks force push + deletion, requires verified signatures (D107)
- \`rulesets/records-tags-immutable.json\` — live tag ruleset, no bypass actor (D107)
- \`records-writer-app.md\` — declared credential shape, contains no secret (D89, Section 40.1)
- \`rw-token.sh\` — installation-token minting helper, holds no secret

Rationale: MasterSpec Section 45.1 places ruleset configuration in the minimum reconstruction set.

Proofs executed in tasks T07, T08, T10, T11: force push rejected, ref deletion rejected, fast-forward append accepted, unsigned push rejected, API write Verified, installation scoped to one repository, control-plane read and write both 404."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
|---|---|---|---|
| 1 | Branch follows the lane prefix | `git -C "${CP_DIR}" rev-parse --abbrev-ref HEAD` | `lane/4/p1-records-repo` |
| 2 | **Only** `tools/records/**` changed | `git -C "${CP_DIR}" diff --name-only integration...HEAD \| grep -vc '^tools/records/'` | `0` |
| 3 | Four files added | `git -C "${CP_DIR}" diff --name-only integration...HEAD \| wc -l` | `5` (two rulesets, `README.md`, `records-writer-app.md`, `rw-token.sh`) |
| 4 | Stored branch ruleset matches the live one exactly | see SELF-VERIFY | no `diff` output |
| 5 | Stored tag ruleset matches the live one exactly | see SELF-VERIFY | no `diff` output |
| 6 | No secret material committed | `git -C "${CP_DIR}" diff integration...HEAD \| grep -ciE 'BEGIN RSA|BEGIN PRIVATE|ghs_|ghp_'` | `0` |
| 7 | PR opened against `integration`, not `main` | `gh pr view --repo "${CP_SLUG}" --json baseRefName --jq .baseRefName` | `integration` |

### SELF-VERIFY

```bash
set -eu
. "${SECRETS_DIR}/l4-ids.env"
cd "${CP_DIR}"
FAIL=0
[ "$(git rev-parse --abbrev-ref HEAD)" = "lane/4/p1-records-repo" ] || { echo "FAIL branch name"; FAIL=1; }
[ "$(git diff --name-only integration...HEAD | grep -vc '^tools/records/')" = "0" ] || { echo "FAIL foreign path touched"; FAIL=1; }
[ "$(git diff integration...HEAD | grep -ciE 'BEGIN RSA|BEGIN PRIVATE|ghs_|ghp_')" = "0" ] || { echo "FAIL secret material in diff"; FAIL=1; }

norm_live() { gh api "/repos/${RECORDS_SLUG}/rulesets/$1" \
  --jq '{name,target,enforcement,bypass:(.bypass_actors|length),rules:([.rules[].type]|sort),include:.conditions.ref_name.include}'; }
norm_file() { jq -S '{name,target,enforcement,bypass:(.bypass_actors|length),rules:([.rules[].type]|sort),include:.conditions.ref_name.include}' "$1"; }

diff <(norm_live "${BRANCH_RS_ID}") <(norm_file tools/records/rulesets/records-append-only.json) \
  || { echo "FAIL branch ruleset drift between live and stored"; FAIL=1; }
diff <(norm_live "${TAG_RS_ID}")    <(norm_file tools/records/rulesets/records-tags-immutable.json) \
  || { echo "FAIL tag ruleset drift between live and stored"; FAIL=1; }

[ "$FAIL" = "0" ] && echo "L4-P1-T12 PASS" || echo "L4-P1-T12 BLOCKED"
```

**Expected output — exactly this single line (both `diff`s silent):**

```
L4-P1-T12 PASS
```

### STOP RULE

Do not merge and do not continue if:

- `git diff --name-only integration...HEAD` shows **any** path outside `tools/records/`. PARTITION.md rule 1: a lane PR touching a foreign path fails the lane-guard check, no exceptions. Reset the branch, re-stage `tools/records` only.
- Either `diff` in SELF-VERIFY produces output → the stored JSON does not describe the live ruleset, which makes the reconstruction set wrong. Correct the **file** to match the live ruleset; never loosen the live ruleset to match the file. If they cannot be reconciled, blocker.
- Any grep for `BEGIN RSA`, `BEGIN PRIVATE`, `ghs_` or `ghp_` matches → a credential is in the diff. Do not push. Treat as exposure under §43 and blocker.
- The PR base is `main` → PARTITION.md: lanes merge to `integration`; only `integration` merges to `main`. Close the PR, re-open against `integration`.
- You are tempted to merge your own PR → do not. L0 runs the merge train (L1 → L4 → L2 → L3 → L5).

`<TASK-ID>` = `T12`.

---

## Phase exit gate — all twelve must hold simultaneously

Run this after T12. It re-proves the phase from the live platform, not from your notes.

```bash
set -eu
. "${SECRETS_DIR}/l4-ids.env"
export RW_PEM="${SECRETS_DIR}/records-writer.pem"
RW_TOKEN="$("${CP_DIR}/tools/records/rw-token.sh")"
P=0
chk() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1 (got '$2' want '$3')"; P=1; fi; }

chk "repo private"            "$(gh api "/repos/${RECORDS_SLUG}" --jq .private)" "true"
chk "no branch protection"    "$(gh api "/repos/${RECORDS_SLUG}/branches/main/protection" --silent >/dev/null 2>&1 && echo yes || echo no)" "no"
chk "two rulesets"            "$(gh api "/repos/${RECORDS_SLUG}/rulesets" --jq 'length')" "2"
chk "zero bypass actors"      "$(gh api "/repos/${RECORDS_SLUG}/rulesets" --jq '[.[].id]|join(" ")' | xargs -n1 -I{} gh api "/repos/${RECORDS_SLUG}/rulesets/{}" --jq '.bypass_actors|length' | sort -u | tr -d '\n')" "0"
chk "branch rules"            "$(gh api "/repos/${RECORDS_SLUG}/rulesets/${BRANCH_RS_ID}" --jq '[.rules[].type]|sort')" '["deletion","non_fast_forward","required_signatures"]'
chk "tag rules"               "$(gh api "/repos/${RECORDS_SLUG}/rulesets/${TAG_RS_ID}" --jq '[.rules[].type]|sort')" '["deletion","non_fast_forward"]'
chk "20 store dirs"           "$(gh api "/repos/${RECORDS_SLUG}/git/trees/main?recursive=1" --jq '[.tree[]|select(.path|endswith(".gitkeep"))]|length')" "20"
chk "conventions present"     "$(gh api "/repos/${RECORDS_SLUG}/contents/CONVENTIONS.md" --jq .name)" "CONVENTIONS.md"
chk "head verified"           "$(gh api "/repos/${RECORDS_SLUG}/commits/main" --jq .commit.verification.verified)" "true"
chk "app scoping"             "$(gh api "/orgs/${ORG}/installations" --jq '.installations[]|select(.app_slug=="'"${APP_SLUG}"'")|.repository_selection')" "selected"
chk "app permissions"         "$(gh api "/apps/${APP_SLUG}" --jq .permissions)" '{"contents":"write","metadata":"read"}'
chk "credential reaches 1 repo" "$(curl -sS -H "Authorization: Bearer ${RW_TOKEN}" -H 'Accept: application/vnd.github+json' https://api.github.com/installation/repositories | jq -r '.total_count')" "1"
chk "credential blind to control-plane" "$(curl -sS -o /dev/null -w '%{http_code}' -H "Authorization: Bearer ${RW_TOKEN}" -H 'Accept: application/vnd.github+json' "https://api.github.com/repos/${CP_SLUG}/contents/README.md")" "404"

[ "$P" = "0" ] && echo "L4 PHASE 1 EXIT GATE: PASS" || echo "L4 PHASE 1 EXIT GATE: FAIL"
```

**Expected final line:**

```
L4 PHASE 1 EXIT GATE: PASS
```

Any `FAIL` line: file a blocker with `<TASK-ID>` = `EXIT-GATE`, quoting every `FAIL` line verbatim. Do not start L4 Phase 2.

---

## Handoffs this phase creates

| To | What | Why it is not built here |
|---|---|---|
| **L0** | D-L4-01 (org login), D-L4-02 (signing mechanism), D-L4-03 (key custody scheduling) | Judgment / missing parameter |
| **L5** | Custody of `records-writer.pem` in the ops-VM machine-credential store; the §49 operational-asset-inventory entry (rotation cadence, named rotator, runbook link, behavioural envelope, envelope-alert owner, expiry date) | `ops-vm/**` and `assets/**` are L5's paths (PARTITION.md) |
| **L3** | The records head-SHA anchor: once per reconciliation run, record `control-plane-records`' default-branch head SHA and commit count into the protected `control-plane` repository; a head that does not descend from the last anchor is Blocking drift **Level 5** (D107, §53.2). Also: the Blocking-drift check for an unsigned or foreign-signed commit on the default branch (D107). | `reconciler/**` and `validators/drift/**` are L3's paths |
| **L1** | The `event_type` closed enum in `platform.yaml`, shipped populated in Phase 1 so no workflow ever writes an untyped event (§97.3) | `registries/**` is L1's path |
| **L2** | Workflows must write records and events through the records-writer installation token, and the deployment-record and event writes are **required, failing steps** of `deploy-production.yml` (§97.2) | `.github/workflows/**` is L2's path |
| **L4 Phase 2+** | `schemas/records/**` (record and event JSON Schemas as versioned contracts, §60.2), write-freshness intervals in `os-health.yaml`, `metrics/**` derivations, `tools/records/**` writers, retention classes (§97.6) | Out of scope for this file |

---

## Not covered by this document — do not attempt here

Record and event JSON Schemas; the event-type enum; the RECORD-VERIFICATION-RESULT dispatch; write-freshness instrumentation (§97.2, Amber past interval, Blocking for `events/`, `records/deployments/`, `records/uat/`); attention-hour derivation (§97.4); the Ready-queue-miss detector (§97.5); retention classes (§97.6); the reconciler anchor; the organisation export (§45.3); dashboards. Each has its own L4 phase file or belongs to another lane.
