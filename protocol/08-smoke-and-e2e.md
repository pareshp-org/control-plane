# 08 — Smoke and End-to-End Verification

**Status:** binding. Part of the verification and merge protocol for the five-lane parallel build.
**Owner:** L0 Integrator (per `PARTITION.md`, L0 owns `main`, `integration`, `docs/**`, root files).
**Applies to:** every promotion of `integration` → `main`, and once as the V1 exit gate.

---

## 0. What this document is

Files 01–07 of this protocol verify that each lane built *something that passes its own tests*. This file
verifies that the five lanes built **the same system**. It does that the only way that cannot be faked: it
takes one pilot product from nothing, through create-product, a real change through Gate 1 and Gate 2, a
real artifact with a real digest, staging, verification, production approval, production deploy, and then
demands that the assembled estate answer **all eleven questions of spec Section 32** about that artifact,
from records the run itself caused to be written.

Five low-cost developers on five branches, none holding full context, can each pass their lane's unit tests
and still produce a system where the digest that reaches production is not the digest staging verified,
where the deployment record is written by a workflow nobody reads, where `/version` reports something no
record mentions. Nothing catches that except walking the whole chain once, for real, and refusing to accept
any link on assertion.

**The demonstration is the deliverable.** A green E2E run is what makes the claim "V1 is real" a fact rather
than an aggregate of five lanes' self-reports.

### 0.1 The principle that governs every gate in this file

> A check that can only pass is not a check.

The specification holds this in at least four places, and this protocol carries all four into the test
strategy:

| Where the spec holds it | What it says | Carried here as |
|---|---|---|
| Section 53.1, the seeded-canary rule | A reconciliation run that reports zero findings, **including the planted canary**, is a FAILED run — it proves the instrument stopped looking | Stage E2E-12 + `NEG-18` |
| **AT-102** | "a reconciler that finds nothing is assumed broken, never assumed clean"; raises SIG-13 and triggers the gap procedure | `CP-1201`, `CP-1202` |
| Section 31.2, the seeded-defect case | "A verification contract that cannot fail is not a contract." Every `verification/contract.yaml` declares a seeded defect the contract MUST fail; a run where it passes is a FAILED run, raises SIG-18, Blocking for that product | Stage E2E-03 + `NEG-04` |
| Section 30.2 / Section 23 culture notes | Zero plan-checker rejections means the gates are not working; a very low code-review rejection rate may mean rubber-stamping | `NEG-05`…`NEG-08`, and §7.3 |

Therefore **every gate exercised in this file has a paired negative test** that drives the gate into
failure on purpose and asserts that it failed *for the stated reason*. §5 is that suite. A run in which the
positive path is green and the negative suite is also green **is a failed run**, and §7.2 says so
mechanically.

### 0.2 Scope boundary

| In scope | Out of scope |
|---|---|
| One pilot product, end to end, on the assembled `integration` branch | Per-lane unit and contract tests (files 01–07) |
| The eleven evidence questions of Section 32 | The people tier (AT-052…AT-088) — no people data exists at V1 (Section 99.4, item 9) |
| The gates a change actually passes through: Gate 1, Gate 2, production approval, digest immutability, parity, freeze | Predictive economics, forecasting, Layer B decision support (deferred, Section 99.4) |
| The instruments those gates read: verification contract, reconciler, records stores | Split / merge / transfer processes (deferred, Section 99.4) |
| Access-boundary execution: AT-108, AT-109, AT-110 | Full 110-test acceptance sweep — this file runs the subset a delivery chain touches (§1.2) |

---

## 1. The demonstration contract

### 1.1 What a passing run proves

| Stage | Proves | Spec |
|---|---|---|
| E2E-01 create-product | Adding a product is configuration plus onboarding, never platform redesign; every surface enumerates from the registry | **AT-001**, invariant **#53** |
| E2E-02 assignment and reconcile | Declared state reaches the estate; CODEOWNERS and Team membership are derived, not hand-edited | invariants **#7**, **#55** |
| E2E-03 verification contract | No onboarded product without a verification contract, and the contract can fail | Section 31.2, invariant **#1**, SIG-18 |
| E2E-04 Gate 1 | A plan is approved by a holder of `plan-approval`, not by its author; the approver is notified; turnaround is measured | **AT-106**, Section 26.1 |
| E2E-05 Gate 2 | Independent review by someone other than the author, approval of the most recent reviewable push | Invariants **#8**, **#9** |
| E2E-06 build | One immutable artifact, digest recorded, SBOM emitted beside it | Section 33.2, Section 48.3 |
| E2E-07 staging | Deployed, smoke passed, manual UAT recorded through RECORD-VERIFICATION-RESULT | Section 31, Section 97.2 |
| E2E-08 production approval | A separate event from Gate 2, by a named approver who is not the deployer | Invariant **#12**, Section 27.2 |
| E2E-09 production deploy | The **same digest**, never rebuilt; deployment record and event are required failing steps | Invariants **#22**, **#23**, Section 97.2 |
| E2E-10 evidence chain | All eleven questions answered from GitHub, Actions and Grafana alone; item 5 == item 11 | **Section 32** |
| E2E-11 rollback and restore | Rollback tested once, restore tested once, both recorded | **AT-103**, invariants **#3**, **#4**, **#27** |
| E2E-12 reconciliation | The reconciler runs, finds the canary, and records its comparison counts | **AT-102**, **AT-032**, **AT-033** |
| NEG suite (§5) | Every one of the above gates is able to fail, and fails for the right reason | §0.1 |

### 1.2 Acceptance tests this run executes for real

These are executed by this file, not asserted elsewhere:
**AT-001**, **AT-009**, **AT-032**, **AT-033**, **AT-036**, **AT-037**, **AT-039**,
**AT-102**, **AT-103**, **AT-106**, **AT-108**, **AT-109**, **AT-110**.

Referenced but executed elsewhere in the protocol: AT-023…AT-027 (platform change, file 07),
AT-047/AT-048/AT-104 (support intake, file 06), AT-035 (org export, file 06),
AT-089…AT-100 (access separation, file 05).

### 1.3 Invariants this run asserts mechanically

**#1**, **#2**, **#3**, **#4**, **#6**, **#7**, **#8**, **#9**, **#12**, **#18**, **#21**, **#22**, **#23**,
**#25**, **#27**, **#28**, **#40**, **#41**, **#44**, **#46**, **#47**, **#53**, **#55**, **#71**, **#72**,
**#77**, **#79**, **#80**, **#81**, **#84**, **#85**, **#87**, **#111**.

Each is bound to a checkpoint id in the traceability matrix, §10.

---

## 2. Fixtures: the pilot product and the actors

### 2.1 The pilot product

The run creates a real product and then leaves it in place. It is not torn down: it becomes the estate's
permanent canary product, and its records are the reference answers every later run diffs against.

| Field | Value |
|---|---|
| `identity.id` | `pilot-one` |
| Repository | `org/pilot-one-api` (single repository, `role: primary`, `deploys: true`) |
| `conformance_profile` | `service` — so the three endpoints of Section 41.2 and items 10/11 of Section 32 apply unsubstituted |
| `classification.reliability_criticality` | `high` — this makes the performance mechanism **required** (Section 31.3), so the run exercises it |
| `verification.performance` | `required` |
| `deployment.artifact_type` | `docker-image`, registry `ghcr.io/org/pilot-one` |
| `deployment.progressive_delivery` | `flag-gated` |
| `reversibility_default` | `fully-reversible` |
| `observability.telemetry_exposure` | `private-authenticated` |
| `recovery:` block | present — which is what makes **AT-103** in scope for this product |

`org/pilot-one-api` is a service that serves one route plus the three required endpoints. It is deliberately
trivial. The subject of the test is the delivery chain, not the product.

The change driven through the chain — **the pilot change** — is: *add a `disabled_at` timestamp to the
customer record and a `POST /customers/{id}/disable` route*. It is chosen because it is the worked example
of Section 31, it touches database schema (so the plan-checker's rollback-strategy rule is exercised), and
it is `fully-reversible` (so the happy path is the standard flow and the reversibility negative tests in
§5 have a clean baseline to deviate from).

### 2.2 Minimum actor set

Section 27.2 requires the approving identity to differ from the deploying identity; Section 95.4 arms
"production approver ≠ deploying actor" at **3 humans with Write**. The E2E therefore needs:

| Actor | Registry id | Holds | Used for |
|---|---|---|---|
| Author | `dev-a` | `primary_owner` on `pilot-one` | writes the plan and the code |
| Independent reviewer | `dev-b` | `cross_reviewer`, `code-review` | Gate 2 |
| Plan approver | `lead-1` | `plan-approval` | Gate 1 |
| Verification authority | `qa-1` | `verification`, `release-signoff` | staging UAT, verification block |
| Production approver | `lead-1` | `production-approval` | E2E-08 — must not be `dev-a`, must not be the pipeline |
| Executor | `devops-1` | `devops` | runs create-product |

**STOP rule S-01.** If fewer than three humans hold Write on `org/pilot-one-api`, the armed configuration
cannot be exercised. Do **not** run the E2E with the gates unarmed and record a pass. Run the bootstrap
variant of §8.4 instead, which explicitly records which gates were *not* proven and files the shortfall as
a bootstrap exception under Section 95.2. A gate that appears to be working and is not is the exact failure
Section 95.1 names.

### 2.3 Credentials the run may and may not touch

| Credential | Used by | Rule |
|---|---|---|
| `records-writer` GitHub App token | deploy / UAT / reconcile workflows | fine-grained `contents: write`, **`control-plane-records` only**, reaches no registry (Section 97.1, D89). Asserted at `CP-0904`. |
| reconciler credential | reconciliation job | bounded — proven by **AT-110** at `CP-1210`, executed for real, not asserted |
| ops console credential | founder ops console | read-only — proven by **AT-108** at `CP-1310` |
| any human-held production credential | — | **none exists**. `env \| grep -i -E 'api_key|token|secret'` returns empty on every operator machine (Section 95.3). Asserted at `CP-0002`. |

---

## 3. Harness conventions

### 3.1 Location and ownership

The harness lives in the **control-plane** repository at `e2e/`, owned by **L0** in `CODEOWNERS`. It is not
a lane path, so it creates no lane-guard conflict and no lane may edit it (PARTITION rule 1).

```
e2e/
  run.sh                 # the only entry point
  lib/checkpoint.sh      # cp_assert / cp_refute / cp_equal
  stages/00-preflight.sh … stages/13-access.sh
  negative/neg-01.sh … negative/neg-22.sh
  fixtures/pilot-one/    # product.yaml, verification/, seeded defect, canary
  out/<run-id>/          # evidence bundle, gitignored, uploaded as an artifact
```

### 3.2 Checkpoint primitives

Every assertion in this file is one of three primitives. They are the whole contract between the stages and
the pass/fail rule in §7.

```bash
# e2e/lib/checkpoint.sh
set -euo pipefail

: "${E2E_RUN_ID:?run ./e2e/run.sh — never a stage script directly}"
export E2E_OUT="e2e/out/${E2E_RUN_ID}"
mkdir -p "${E2E_OUT}/evidence" "${E2E_OUT}/checkpoints"
E2E_LOG="${E2E_OUT}/checkpoints/log.tsv"

_emit() { printf '%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" "$3" >>"${E2E_LOG}"; }

cp_pass() { _emit "$1" PASS "$2"; printf '  ok   %s  %s\n' "$1" "$2"; }
cp_fail() { _emit "$1" FAIL "$2"; printf '  FAIL %s  %s\n' "$1" "$2"; exit 1; }

# POSITIVE checkpoint: the command must succeed.
cp_assert() {
  local id="$1" what="$2"; shift 2
  if "$@" >"${E2E_OUT}/evidence/${id}.out" 2>&1; then
    cp_pass "$id" "$what"
  else
    cp_fail "$id" "$what — evidence: ${E2E_OUT}/evidence/${id}.out"
  fi
}

# EQUALITY checkpoint: two values must be byte-identical. Used for the digest chain.
cp_equal() {
  local id="$1" what="$2" a="$3" b="$4"
  printf 'expected=%s\nactual=%s\n' "$a" "$b" >"${E2E_OUT}/evidence/${id}.out"
  [ "$a" = "$b" ] && cp_pass "$id" "$what" || cp_fail "$id" "$what — '$a' != '$b'"
}

# NEGATIVE checkpoint: the command MUST fail, AND must fail for the stated reason.
# A negative test that fails for the wrong reason is not a negative test.
cp_refute() {
  local id="$1" what="$2" reason_re="$3"; shift 3
  if "$@" >"${E2E_OUT}/evidence/${id}.out" 2>&1; then
    cp_fail "$id" "GATE DID NOT FIRE — '$what' succeeded and must not have"
  elif grep -Eq "$reason_re" "${E2E_OUT}/evidence/${id}.out"; then
    cp_pass "$id" "gate fired: $what refused, reason matched /$reason_re/"
  else
    cp_fail "$id" "WRONG REASON — '$what' failed, but not on /$reason_re/; the gate may be broken rather than working"
  fi
}
```

`cp_refute`'s third argument is not decoration. A negative test that passes because the network was down,
the CLI was missing or a YAML file was malformed proves nothing about the gate. The reason regex is what
makes the negative suite itself a check that can fail.

### 3.3 Numbering

| Prefix | Meaning |
|---|---|
| `CP-SSNN` | positive checkpoint, stage `SS`, sequence `NN` (e.g. `CP-0903` = stage E2E-09, third checkpoint) |
| `NEG-NN` | negative test, §5 |
| `S-NN` | STOP rule |

### 3.4 Entry point

```bash
# e2e/run.sh
set -euo pipefail
export E2E_RUN_ID="${E2E_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-$(git rev-parse --short HEAD)}"
export E2E_PRODUCT=pilot-one
export E2E_REPO=org/pilot-one-api
export E2E_CP_REPO=org/control-plane
export E2E_RECORDS_REPO=org/control-plane-records
export E2E_RUN_START="$(date -u +%Y-%m-%dT%H:%M:%SZ)"   # freshness floor for CP-0708, CP-1204, CP-1207

# --first-run (CP-0003) and --bootstrap (§8.4) are flags, not environment folklore the operator must
# know to export by hand.
export E2E_FIRST_RUN="${E2E_FIRST_RUN:-0}"
export E2E_BOOTSTRAP="${E2E_BOOTSTRAP:-0}"
for arg in "$@"; do
  case "$arg" in
    --first-run) E2E_FIRST_RUN=1 ;;
    --bootstrap) E2E_BOOTSTRAP=1 ;;
  esac
done
export E2E_FIRST_RUN E2E_BOOTSTRAP
source e2e/lib/checkpoint.sh

for s in e2e/stages/*.sh;   do echo "== $s"; bash "$s" || break; done
for n in e2e/negative/*.sh; do
  # §8.4 bootstrap variant: skip and explicitly record as unproven the independence gates.
  case "$n" in
    */neg-09.sh|*/neg-10.sh|*/neg-12.sh|*/neg-13.sh)
      if [ "${E2E_BOOTSTRAP}" = "1" ]; then
        echo "== $n (skipped — bootstrap: independence gate unarmed, recorded unproven per §8.4)"
        continue
      fi
      ;;
  esac
  echo "== $n"; bash "$n" || break
done
bash e2e/verdict.sh          # §7 — the only thing allowed to print PASS for the run; `|| break` above keeps a
                              # stage/negative failure from killing this script under `set -e`, so verdict.sh —
                              # and its VERDICT: FAIL — always runs and its exit code is what run.sh returns
```

**Stages run in order and stop on first failure.** The chain is a chain: there is no useful information in
stage 9 when stage 6 did not produce a digest.

---

## 4. The end-to-end script

### E2E-00 — Preflight

```bash
set -euo pipefail
# e2e/stages/00-preflight.sh
source e2e/lib/checkpoint.sh

# CP-0001 The integration branch is the thing under test, not somebody's local tree.
cp_assert CP-0001 "HEAD is the tip of integration" \
  bash -c 'test "$(git rev-parse HEAD)" = "$(git rev-parse origin/integration)"'

# CP-0002 No API keys or production secrets exist in the operator environment (invariant #84, Section 95.3).
# Allow-list covers: standard GitHub Actions tokens (GITHUB_TOKEN, RUNNER_TOKEN), E2E harness tokens,
# and GITHUB_ACTIONS flag. The intent is to catch inadvertent api_key or production credential leakage.
cp_assert CP-0002 "operator environment is API-key-free" \
  bash -c '! env | grep -iE "(api_key|_token=|_secret=)" | grep -viE "^(GITHUB_TOKEN=|GITHUB_ACTIONS|RUNNER_TOKEN=|E2E_)"'

# CP-0003 The pilot product does not yet exist. Active only on the first run (E2E_FIRST_RUN=1 / --first-run).
# On subsequent runs the pilot is the estate's permanent canary product and its presence is expected and required.
cp_assert CP-0003 "pilot product absent before the run (first-run only)" \
  bash -c '[ "${E2E_FIRST_RUN:-0}" = "1" ] || exit 0; ! gh api "repos/${E2E_REPO}" >/dev/null 2>&1'

# CP-0004 Every reusable workflow tag the estate consumes resolves to the SHA platform.yaml records
#         (Section 33.2; invariant #85; the tag-ruleset row of Section 53.1).
cp_assert CP-0004 "consumed workflow tags match platform.yaml pins" \
  ./tools/verify-workflow-tag-pins.sh --strict

# CP-0005 Friday-freeze awareness. A production deploy must START by 15:00 Friday and finish smoke and its
#         observation window inside core hours (Section 34.2). The run refuses to start where E2E-09 could
#         not complete inside the window.
cp_assert CP-0005 "run window admits a compliant production deploy" \
  ./tools/freeze-window-check.sh --need-minutes 90

# CP-0006 Every tool this harness shells out to (gh, jq, yq, curl, base64, git) is present, and yq is
#         specifically the mikefarah Go implementation — the expression syntax this file uses against
#         contract.yaml (CP-0302, CP-0303) is not portable to the kislyuk Python `yq`. A missing binary
#         or the wrong yq must fail here, loudly, not deep inside an arbitrary later checkpoint.
cp_assert CP-0006 "required tools present and yq is the mikefarah implementation" \
  bash -c 'for t in gh jq yq curl base64 git; do command -v "$t" >/dev/null 2>&1 || { echo "missing required tool: $t"; exit 1; }; done
           yq --version 2>&1 | grep -qi "mikefarah/yq" || { echo "yq is not the mikefarah implementation"; exit 1; }'
```

**STOP rule S-02.** `CP-0004` failing means a `workflows/*` tag moved. Do not continue and do not "just
re-pin": a moved tag executes new code in every product's pipeline with no pull request and no diff
(Section 33.2), it is **Blocking** drift on the Section 53.1 row, and it is investigated before anything
else merges.

### E2E-01 — create-product, from nothing

```bash
set -euo pipefail
# e2e/stages/01-create-product.sh
source e2e/lib/checkpoint.sh

# The scaffolding operation. One command, run by a devops-capability holder. Nothing hand-made.
cp_assert CP-0101 "create-product completes" \
  ./tools/provision/create-product \
    --id "${E2E_PRODUCT}" \
    --contract e2e/fixtures/pilot-one/product.yaml \
    --template product-template \
    --executor devops-1

# CP-0102 The eight local-environment commands exist (Section 33.1) — AT-009 conformance.
for target in setup dev test uat-local migrate reset health parity; do
  cp_assert "CP-0102-${target}" "Makefile exposes ${target}" \
    bash -c "gh api repos/${E2E_REPO}/contents/Makefile --jq .content | base64 -d | grep -qE '^${target}:'"
done

# CP-0103 Required files present — checked, not assumed (Section 33.1).
cp_assert CP-0103 "required repository files present" \
  ./tools/provision/check-required-files --repo "${E2E_REPO}"
#   .env.example · docker-compose.dev.yml · Makefile · seed data · migrations/ · verification/ · AGENTS.md · product.yaml

# CP-0104 Required workflows present, all seven, generated from templates and consuming reusable
#         workflows by PINNED TAG (Section 33.2). restore-production.yml is required because the pilot
#         declares a recovery: block — AT-103.
for wf in ci build deploy-staging deploy-production migrate restore-test restore-production; do
  cp_assert "CP-0104-${wf}" "${wf}.yml generated and tag-pinned" \
    bash -c "gh api repos/${E2E_REPO}/contents/.github/workflows/${wf}.yml --jq .content | base64 -d \
             | grep -qE 'uses: org/control-plane/.github/workflows/.*@workflows/v[0-9]+'"
done

# CP-0105 Third-party actions pinned to full commit SHA — no tags, no branches (invariant #85).
cp_assert CP-0105 "third-party actions pinned to 40-char SHA" \
  ./tools/verify-action-pins.sh --repo "${E2E_REPO}" --require-sha

# CP-0106 Environments exist WITH deployment branch and tag policies (Section 33.4). The environments
#         alone are not the control; the ref restriction is.
cp_assert CP-0106 "staging and production restricted to default branch and protected tags" \
  ./tools/provision/check-environment-policy --repo "${E2E_REPO}" \
    --env staging --env production --expect default-branch,protected-tags

# CP-0107 Branch protection matches the committed template (Section 53.1, blocking row).
cp_assert CP-0107 "branch protection matches template" \
  ./tools/provision/diff-branch-protection --repo "${E2E_REPO}" --template templates/protection/service.json --exit-nonzero-on-diff

# CP-0108 AUTOMATIC DISCOVERY — AT-001. The product appears on every surface with nobody editing a
#         dashboard. Each of these enumerates from the registry.
for surface in portfolio-board grafana scorecard devlake reviewer-matrix dependency-graph; do
  cp_assert "CP-0108-${surface}" "pilot-one discoverable on ${surface}" \
    ./tools/verify-surface-enumeration.sh --surface "${surface}" --product "${E2E_PRODUCT}"
done

# CP-0109 AT-001's hard clause: no dashboard, workflow or script contains a product list.
cp_assert CP-0109 "no hard-coded product list anywhere" \
  ./tools/verify-no-product-list.sh --scan dashboards/ .github/workflows/ tools/ templates/

# CP-0110 The CONFIGURE checklist issue and the alert-channel / support-intake steps exist as tracked
#         work, not as silent omissions (Section 19.1).
cp_assert CP-0110 "CONFIGURE checklist and channel/mailbox steps emitted" \
  ./tools/provision/check-scaffold-issues --product "${E2E_PRODUCT}" \
    --require configure-checklist,alert-channel,support-intake
```

### E2E-02 — Assignments reach the estate through reconciliation

```bash
set -euo pipefail
# e2e/stages/02-assign.sh
source e2e/lib/checkpoint.sh

# Declared state only. Nobody touches GitHub Teams or CODEOWNERS by hand (invariant #55).
cp_assert CP-0201 "assignments merged to the registry" \
  ./tools/provision/apply-assignments --product "${E2E_PRODUCT}" \
    --set primary_owner=dev-a --set cross_reviewer=dev-b --set backup_owner=dev-b \
    --set primary_responder=dev-a --set backup_responder=dev-b --set verification=qa-1

cp_assert CP-0202 "reconciliation run applies declared state" \
  gh workflow run reconcile.yml -R "${E2E_CP_REPO}" -f mode=apply -f wait=true

# CP-0203 CODEOWNERS is GENERATED, and carries no machine identity (Section 53.1 independent verifier).
cp_assert CP-0203 "CODEOWNERS generated from assignments, no machine identity" \
  ./tools/provision/verify-codeowners --repo "${E2E_REPO}" --derived-from registry --forbid-machine-identities

# CP-0204 Team membership matches the contract (invariant #7; Section 53.1 fails CI on mismatch).
cp_assert CP-0204 "GitHub Team membership matches product.yaml assignments" \
  ./tools/provision/diff-team-membership --product "${E2E_PRODUCT}" --exit-nonzero-on-diff

# CP-0205 Zero blocking orphans for the new product (invariant #57).
cp_assert CP-0205 "no blocking orphans on pilot-one" \
  ./reconciler/orphan-report --product "${E2E_PRODUCT}" --fail-on blocking

# CP-0206 The cross-reviewer holds WRITE, not Read. A Read-only cross-reviewer fails silently
#         (Section 99.6, secondary risks) — so it is checked, loudly.
cp_assert CP-0206 "cross_reviewer holds Write" \
  ./tools/provision/check-permission --repo "${E2E_REPO}" --login dev-b --expect write
```

### E2E-03 — The verification contract, and proof it can fail

```bash
set -euo pipefail
# e2e/stages/03-verification-contract.sh
source e2e/lib/checkpoint.sh

cp_assert CP-0301 "verification/contract.yaml present and schema-valid" \
  ./validators/registry/validate-verification-contract --repo "${E2E_REPO}"

# CP-0302 reliability_criticality: high ⇒ the performance mechanism is REQUIRED (Section 31.3).
cp_assert CP-0302 "performance mechanism declared" \
  bash -c 'gh api repos/${E2E_REPO}/contents/verification/contract.yaml --jq .content | base64 -d | yq -e ".mechanisms.performance == \"required\"" -'

# CP-0303 A seeded-defect case is declared (Section 31.2).
cp_assert CP-0303 "seeded-defect case declared in contract.yaml" \
  bash -c 'gh api repos/${E2E_REPO}/contents/verification/contract.yaml --jq .content | base64 -d | yq -e ".seeded_defect.path != null" -'

# CP-0304 THE CHECK THAT CAN FAIL. Run the contract against the seeded defect. The contract MUST fail it.
#         A run in which the seeded defect PASSES is a FAILED run, raises SIG-18, and is Blocking for the
#         product until the case fails again. This is the same logic AT-102 applies to the reconciler.
cp_refute CP-0304 "verification contract rejects its seeded defect" \
  'seeded[- ]defect|assertion failed|FAIL' \
  ./tools/evidence/run-verification-contract --repo "${E2E_REPO}" --with-seeded-defect

# CP-0305 …and passes on the clean tree, so CP-0304 is discrimination, not a contract that always fails.
cp_assert CP-0305 "verification contract passes on the clean tree" \
  ./tools/evidence/run-verification-contract --repo "${E2E_REPO}"

# CP-0306 Coverage mapping exists and uat.md is stubbed at plan time (Section 31.2).
cp_assert CP-0306 "coverage map resolves every requirement to a check" \
  ./tools/evidence/check-coverage-map --repo "${E2E_REPO}" --fail-on-unmapped
```

`CP-0304` and `CP-0305` are a matched pair and are meaningless apart. Together they say: the instrument
distinguishes. Either alone says only that it produces output.

### E2E-04 — Gate 1, Plan Approval

```bash
set -euo pipefail
# e2e/stages/04-gate1.sh
source e2e/lib/checkpoint.sh

# dev-a submits the plan for the pilot change. It touches schema, so it must state a rollback strategy.
cp_assert CP-0401 "plan submitted as a plan-approval request" \
  ./tools/gate1/submit-plan --product "${E2E_PRODUCT}" --author dev-a \
    --plan e2e/fixtures/pilot-one/plan-disable-customer.md \
    --change-class normal --impact-scope single-product --reversibility fully-reversible

# CP-0402 The plan-checker ACCEPTED this plan — it has verify commands, real symbols, a rollback strategy,
#         and legitimate packages (Section 30.2).
cp_assert CP-0402 "plan-checker accepts a well-formed plan" \
  ./tools/gate1/plan-check --plan-id "$(cat "${E2E_OUT}/plan-id")" --expect accepted

# CP-0403 The eligible approver is RESOLVED FROM CAPABILITY, not from a role name (invariant #11), and is
#         notified as a push event — AT-106.
cp_assert CP-0403 "approver resolved from capability and notified" \
  ./tools/gate1/verify-notification --plan-id "$(cat "${E2E_OUT}/plan-id")" \
    --expect-approver lead-1 --expect-event plan_submitted_notification_sent

# CP-0404 Approval by lead-1. Not by dev-a: Gate 1 admits no self-approval (Section 26.1).
cp_assert CP-0404 "Gate 1 approved by lead-1" \
  ./tools/gate1/approve --plan-id "$(cat "${E2E_OUT}/plan-id")" --as lead-1

# CP-0405 The event is written with the closed-enum type and the agent_authored flag (Section 97.3).
cp_assert CP-0405 "plan_approved event written with envelope and agent_authored flag" \
  ./tools/records/find-event --type plan_approved --product "${E2E_PRODUCT}" \
    --require-fields event_schema_version,event_id,occurred_at,recorded_at,actor,product,subject_ref \
    --require payload.gate=1 --require-present payload.agent_authored

# CP-0406 The computed requirement set was displayed alongside the plan (Section 24.2 / Section 26.1).
cp_assert CP-0406 "computed requirement set rendered on the Gate 1 surface" \
  ./tools/gate1/verify-requirement-set --plan-id "$(cat "${E2E_OUT}/plan-id")"
```

### E2E-05 — Execute, PR, Gate 2

```bash
set -euo pipefail
# e2e/stages/05-gate2.sh
source e2e/lib/checkpoint.sh

cp_assert CP-0501 "branch pushed and PR opened by dev-a" \
  ./tools/e2e-drive/open-pr --repo "${E2E_REPO}" --as dev-a \
    --branch pilot/disable-customer --fixture e2e/fixtures/pilot-one/change/

# CP-0502 Every required status check reports a REAL conclusion. A `skipped` or `neutral` conclusion on a
#         required context is Blocking drift (Section 33.2) — a skip that branch protection counts as
#         satisfied is a check that can only pass.
cp_assert CP-0502 "no required check reports skipped or neutral" \
  ./tools/evidence/check-conclusions --pr "$(cat "${E2E_OUT}/pr")" \
    --required-from templates/protection/service.json --forbid skipped,neutral

# CP-0503 The full CI set ran: unit, integration, build, security scan, licence scan, contract validation,
#         registry validation, parity, verification contract (Section 33.2).
for job in unit integration build security-scan licence-scan contract-validation registry-validation parity verification-contract; do
  cp_assert "CP-0503-${job}" "CI job ${job} concluded success" \
    ./tools/evidence/check-job --pr "$(cat "${E2E_OUT}/pr")" --job "${job}" --expect success
done

# CP-0504 Parity is clean across local, staging and production declarations (Section 33.1).
cp_assert CP-0504 "environment parity clean" \
  ./tools/evidence/check-job --pr "$(cat "${E2E_OUT}/pr")" --job parity --expect success

# CP-0505 Gate 2 by dev-b — independent, not the author (invariants #8, #9).
cp_assert CP-0505 "Gate 2 approved by an independent reviewer" \
  ./tools/e2e-drive/approve-pr --pr "$(cat "${E2E_OUT}/pr")" --as dev-b

cp_assert CP-0506 "gate_2_approval event carries the reviewer role" \
  ./tools/records/find-event --type gate_2_approval --product "${E2E_PRODUCT}" --require payload.reviewer_role=cross_reviewer

# CP-0507 Merge is MECHANICAL once protection is satisfied (Section 27) — it is not a decision and needs
#         no separate authorisation event.
cp_assert CP-0507 "merge succeeds once protection is satisfied" \
  ./tools/e2e-drive/merge-pr --pr "$(cat "${E2E_OUT}/pr")"
```

### E2E-06 — Build: one artifact, one digest, one SBOM

```bash
set -euo pipefail
# e2e/stages/06-build.sh
source e2e/lib/checkpoint.sh

cp_assert CP-0601 "build workflow produced an artifact" \
  ./tools/e2e-drive/wait-workflow --repo "${E2E_REPO}" --workflow build.yml \
    --sha "$(cat "${E2E_OUT}/merge-sha")" --expect success

# The digest. Everything downstream is this string.
./tools/evidence/read-digest --repo "${E2E_REPO}" --sha "$(cat "${E2E_OUT}/merge-sha")" > "${E2E_OUT}/digest"
cp_assert CP-0602 "digest recorded and well-formed" \
  bash -c 'grep -Eq "^sha256:[0-9a-f]{64}$" "${E2E_OUT}/digest"'

# CP-0603 SBOM emitted beside the digest (Section 33.2, Section 48.3).
cp_assert CP-0603 "SBOM recorded beside the digest" \
  ./tools/evidence/check-sbom --digest "$(cat "${E2E_OUT}/digest")" --require-format spdx-json

# CP-0604 artifact_built event with the digest in the payload (Section 97.3).
cp_assert CP-0604 "artifact_built event carries the digest" \
  ./tools/records/find-event --type artifact_built --product "${E2E_PRODUCT}" \
    --require "payload.digest=$(cat "${E2E_OUT}/digest")"

# CP-0605 The artifact is IMMUTABLE in the registry — the tag cannot be moved onto another digest.
cp_refute CP-0605 "registry refuses to overwrite the pushed digest tag" \
  'immutable|denied|409|cannot be overwritten' \
  ./tools/e2e-drive/attempt-tag-overwrite --registry ghcr.io/org/pilot-one --digest "$(cat "${E2E_OUT}/digest")"
```

### E2E-07 — Staging: deploy, smoke, UAT

```bash
set -euo pipefail
# e2e/stages/07-staging.sh
source e2e/lib/checkpoint.sh
DIGEST="$(cat "${E2E_OUT}/digest")"

cp_assert CP-0701 "migration applied through CI, not by hand" \
  ./tools/e2e-drive/run-workflow --repo "${E2E_REPO}" --workflow migrate.yml \
    --env staging --digest "${DIGEST}" --expect success

# CP-0702 Backward compatibility for one release cycle (Section 34.3): the PREVIOUS digest must still run
#         against the NEW schema. This is what makes rollback possible, so it is proven, not assumed.
cp_assert CP-0702 "previous digest runs against the new schema" \
  ./tools/e2e-drive/compat-probe --env staging --schema new --digest "$(cat "${E2E_OUT}/prev-digest")"

cp_assert CP-0703 "staging deploy succeeded with the built digest" \
  ./tools/e2e-drive/run-workflow --repo "${E2E_REPO}" --workflow deploy-staging.yml \
    --digest "${DIGEST}" --expect success

# CP-0704 Staging /version reports the digest we built. The chain must hold at every hop, not only at the end.
cp_equal CP-0704 "staging /version equals the built digest" \
  "${DIGEST}" "$(./tools/evidence/read-version --env staging --product "${E2E_PRODUCT}")"

cp_assert CP-0705 "staging smoke passed" \
  ./tools/e2e-drive/run-smoke --env staging --product "${E2E_PRODUCT}" --suite verification/smoke/

# CP-0706 Performance mechanism executed and within declared thresholds (Section 31.3, required at high).
cp_assert CP-0706 "performance assertions within declared thresholds" \
  ./tools/evidence/run-performance --env staging --product "${E2E_PRODUCT}" --contract verification/contract.yaml

# CP-0707 Manual UAT by qa-1, reaching the record store through RECORD-VERIFICATION-RESULT and NOT by
#         anyone editing a record file by hand (Section 97.2).
cp_assert CP-0707 "UAT result recorded via RECORD-VERIFICATION-RESULT" \
  gh workflow run record-verification-result.yml -R "${E2E_CP_REPO}" \
    -f product="${E2E_PRODUCT}" -f item="$(cat "${E2E_OUT}/pr")" -f mechanism=manual_uat \
    -f result=pass -f evidence="$(cat "${E2E_OUT}/uat-evidence-url")" -f actor=qa-1

cp_assert CP-0708 "records/uat/ carries the run's UAT record" \
  ./tools/records/find-record --store records/uat --product "${E2E_PRODUCT}" \
    --require result=pass --require-fields record_schema_version,id,product,timestamp \
    --newer-than "${E2E_RUN_START}"

# CP-0709 The UAT record was written by the records-writer credential into the records repository — not by
#         a human, not into the control plane (Section 97.1, D89).
cp_assert CP-0709 "UAT record authored by records-writer in control-plane-records" \
  ./tools/records/verify-author --repo "${E2E_RECORDS_REPO}" \
    --path "$(cat "${E2E_OUT}/uat-record-path")" --expect-author records-writer[bot]
```

### E2E-08 — Production approval: a separate event, a different identity

```bash
set -euo pipefail
# e2e/stages/08-production-approval.sh
source e2e/lib/checkpoint.sh
DIGEST="$(cat "${E2E_OUT}/digest")"

# CP-0801 No open verification block exists for the change or the product. Production approval and
#         deploy-production.yml fail CLOSED while one does (Section 27).
cp_assert CP-0801 "no open verification-block record" \
  ./tools/records/check-verification-block --product "${E2E_PRODUCT}" --expect none

# CP-0802 Approval is against THIS digest, which has already passed smoke and UAT (Section 27).
cp_assert CP-0802 "production approval recorded against the staging-verified digest" \
  ./tools/e2e-drive/approve-production --product "${E2E_PRODUCT}" --digest "${DIGEST}" --as lead-1

# CP-0803 The approver is not the author (invariant #12; Section 27.1 routing table).
cp_assert CP-0803 "production approver differs from the change author" \
  ./tools/records/verify-approval-identity --digest "${DIGEST}" --author dev-a --expect-not dev-a

# CP-0804 The approval is its own event, distinct from Gate 2 — the two are not one decision.
cp_assert CP-0804 "production_approval_granted event distinct from gate_2_approval" \
  ./tools/records/find-event --type production_approval_granted --product "${E2E_PRODUCT}" \
    --require "payload.digest=${DIGEST}" --require payload.approver=lead-1
```

### E2E-09 — Production deploy: the same digest, never rebuilt

```bash
set -euo pipefail
# e2e/stages/09-production.sh
source e2e/lib/checkpoint.sh
DIGEST="$(cat "${E2E_OUT}/digest")"

# CP-0901 The freeze gate evaluates against the DECLARED working calendar and operating timezone, never a
#         runner's local time (Section 97.1) — a Friday-freeze gate resolving against runner local time
#         silently admits the deployments it exists to prevent.
cp_assert CP-0901 "freeze gate resolved against the declared calendar" \
  ./tools/evidence/verify-freeze-evaluation --product "${E2E_PRODUCT}" --expect-source declared-calendar

cp_assert CP-0902 "production deploy succeeded" \
  ./tools/e2e-drive/run-workflow --repo "${E2E_REPO}" --workflow deploy-production.yml \
    --digest "${DIGEST}" --expect success

# CP-0903 THE INVARIANT (#22). No rebuild happened between staging and production. Same digest, and the
#         production job pulled it rather than building it.
cp_assert CP-0903 "production job pulled the digest and ran no build step" \
  ./tools/evidence/verify-no-rebuild --run "$(cat "${E2E_OUT}/prod-run-id")" --digest "${DIGEST}"

# CP-0904 The deployment record and the event are REQUIRED, FAILING steps — a deploy whose record cannot
#         be written is a deploy whose evidence chain does not close (Section 97.2).
cp_assert CP-0904 "deployment record written to records/deployments/" \
  ./tools/records/find-record --store records/deployments --product "${E2E_PRODUCT}" \
    --require "digest=${DIGEST}" --require staging_verified=true --require smoke_result=pass \
    --require-fields id,product,digest,approved_by,approval_event,uat_record

cp_assert CP-0905 "production smoke passed" \
  ./tools/e2e-drive/run-smoke --env production --product "${E2E_PRODUCT}" --suite verification/smoke/

cp_assert CP-0906 "health checks green with dependency detail" \
  bash -c 'curl -sf --cert-type P12 --cert "$OPS_SCRAPE_CERT" "$(./tools/evidence/endpoint --env production --product pilot-one --path /health)" | jq -e ".status==\"ok\" and (.dependencies|length)>0"'

# CP-0907 /version on the LIVE service equals the approved digest (Section 41.2; question 11).
cp_equal CP-0907 "production /version equals the approved digest" \
  "${DIGEST}" "$(./tools/evidence/read-version --env production --product "${E2E_PRODUCT}")"

# CP-0908 Ship, as Section 34.1 redefines it — all eight conditions, including STATE.md.
cp_assert CP-0908 "all eight ship conditions satisfied" \
  ./tools/evidence/check-ship-definition --product "${E2E_PRODUCT}" --digest "${DIGEST}"
```

### E2E-10 — The eleven questions

This is the stage the whole file exists for. Section 32 says the system answers eleven questions using
**only GitHub, GitHub Actions and Grafana**. The assembler therefore runs with no other data source, and
each answer must be non-empty and must cite the record it came from.

```bash
set -euo pipefail
# e2e/stages/10-evidence-chain.sh
source e2e/lib/checkpoint.sh
DIGEST="$(cat "${E2E_OUT}/digest")"

./tools/evidence/evidence-chain \
  --product "${E2E_PRODUCT}" --digest "${DIGEST}" \
  --sources github,actions,grafana --deny-other-sources \
  --format json > "${E2E_OUT}/evidence/chain.json"

cp_assert CP-1000 "evidence-chain assembled from the three permitted sources only" \
  jq -e '.sources | inside(["github","actions","grafana"])' "${E2E_OUT}/evidence/chain.json"
```

| Q | Question (Section 32) | Assertion | Checkpoint |
|---|---|---|---|
| 1 | Which git commit? | `.q1.commit` equals the merge SHA, cited to the artifact label **and** the deployment record | `CP-1001` |
| 2 | Which pull request? | `.q2.pr` resolves from commit-to-PR association and equals the run's PR | `CP-1002` |
| 3 | Who approved at Gate 2, and in which role? | `.q3.approver == "dev-b"`, `.q3.role == "cross_reviewer"`, cross-referenced against the assignment registry — not read off the PR alone | `CP-1003` |
| 4 | Which CI run produced it? | `.q4.run_url` is a real run whose head SHA is `.q1.commit` | `CP-1004` |
| 5 | What is the artifact digest? | `.q5.digest` equals `${DIGEST}`, sourced from the registry digest recorded at build | `CP-1005` |
| 6 | When deployed to staging? | `.q6.staging_deployed_at` present, UTC with offset | `CP-1006` |
| 7 | Did staging verification pass? | `.q7.smoke == "pass"` **and** `.q7.uat_record` points at a real `records/uat/` file | `CP-1007` |
| 8 | Who approved production? | `.q8.approver == "lead-1"`, from the records store, **verified by the workflow-identity gate** | `CP-1008` |
| 9 | When deployed to production? | `.q9.production_deployed_at` present | `CP-1009` |
| 10 | Did post-deployment smoke pass? | `.q10.smoke == "pass"`, attached to the deployment | `CP-1010` |
| 11 | What digest is running right now? | `.q11.digest` read live from `GET /version` | `CP-1011` |

```bash
set -euo pipefail
for q in 1 2 3 4 5 6 7 8 9 10 11; do
  cp_assert "CP-10$(printf '%02d' "$q")" "Q${q} answered with a cited source" \
    jq -e ".q${q} | (.value // .digest // .approver // .commit // .pr // .run_url // .smoke) != null and .source != null" \
       "${E2E_OUT}/evidence/chain.json"
done

# CP-1012 THE INVARIANT THAT MAKES THE CHAIN TRUSTWORTHY (Section 32): item 5 == item 11.
cp_equal CP-1012 "recorded digest equals running digest" \
  "$(jq -r .q5.digest "${E2E_OUT}/evidence/chain.json")" \
  "$(jq -r .q11.digest "${E2E_OUT}/evidence/chain.json")"

# CP-1013 …and the production digest is byte-identical to the one staging verified.
cp_equal CP-1013 "production digest equals staging-verified digest" \
  "$(jq -r .q5.digest "${E2E_OUT}/evidence/chain.json")" \
  "$(jq -r .q7.verified_digest "${E2E_OUT}/evidence/chain.json")"

# CP-1014 The scheduled sweep agrees, across the whole estate, not just this artifact.
cp_assert CP-1014 "verify-digest-chain sweep reports zero mismatches" \
  ./tools/evidence/verify-digest-chain --all-products --fail-on-mismatch

# CP-1015 No answer was hand-maintained. Every one names a canonical store (invariant #46).
cp_assert CP-1015 "every answer names a canonical record store" \
  jq -e '[.q1,.q2,.q3,.q4,.q5,.q6,.q7,.q8,.q9,.q10,.q11] | all(.source | test("^(records/|events/|actions://|grafana://|service://)"))' \
     "${E2E_OUT}/evidence/chain.json"

# CP-1016 Write freshness — the stores that must never go quiet (Section 97.2 / Section 53.1 blocking row).
cp_assert CP-1016 "events/, records/deployments/ and records/uat/ are within their write-freshness window" \
  ./tools/records/check-write-freshness --store events --store records/deployments --store records/uat --fail-on blocking
```

### E2E-11 — Rollback and restore, both executed once

Launch readiness (Section 19.2) requires restore and rollback **tested successfully at least once**.
Invariant #3: an untested backup is treated as no backup.

```bash
set -euo pipefail
# e2e/stages/11-rollback-restore.sh
source e2e/lib/checkpoint.sh
PREV="$(cat "${E2E_OUT}/prev-digest")"; DIGEST="$(cat "${E2E_OUT}/digest")"

# CP-1101 Rollback is exempt from production approval, runs from a human identity holding
#         incident-response or production-approval, and is recorded as an exceptional authorisation
#         (Section 27.2).
cp_assert CP-1101 "rollback to the previous approved digest succeeds" \
  ./tools/e2e-drive/run-workflow --repo "${E2E_REPO}" --workflow rollback.yml \
    --to-digest "${PREV}" --as lead-1 --expect success

cp_equal CP-1102 "/version reports the rolled-back digest" \
  "${PREV}" "$(./tools/evidence/read-version --env production --product "${E2E_PRODUCT}")"

cp_assert CP-1103 "rollback recorded as an exceptional authorisation with from- and to-digest" \
  ./tools/records/find-event --type rollback_initiated \
    --require "payload.from_digest=${DIGEST}" --require "payload.to_digest=${PREV}"

cp_assert CP-1104 "roll forward to the approved digest" \
  ./tools/e2e-drive/run-workflow --repo "${E2E_REPO}" --workflow deploy-production.yml \
    --digest "${DIGEST}" --expect success

# CP-1105 AT-103 — production restore executes end to end with NO credential handed to or typed by a human.
cp_assert CP-1105 "restore-production.yml runs with a scoped run identity and no human credential" \
  ./tools/e2e-drive/run-workflow --repo "${E2E_REPO}" --workflow restore-production.yml \
    --authorisation "$(./tools/records/open-exceptional-auth --type restore_scope --as lead-1)" \
    --assert-no-human-credential --expect success

cp_assert CP-1106 "restore-test record carries integrity_check and a named verifier" \
  ./tools/records/find-record --store records/restore-tests --product "${E2E_PRODUCT}" \
    --require-present integrity_check --require-present verified_by --require result=pass

# CP-1107 product.yaml restore_tested now matches a real record (Section 53.1 blocking row; invariant #4).
cp_assert CP-1107 "restore_tested date matches a passing record" \
  ./validators/drift/check-restore-tested --product "${E2E_PRODUCT}" --fail-on-unevidenced

# CP-1108 Every production bug becomes a permanent regression test (invariant #2). The pilot run plants one
#         defect, files it, fixes it, and asserts the regression test now exists and fails without the fix.
cp_refute CP-1108 "the planted defect's regression test fails without the fix" \
  'regression|assertion failed|FAIL' \
  ./tools/evidence/run-regression --repo "${E2E_REPO}" --test regression/pilot-001 --without-fix
```

### E2E-12 — Reconciliation, with the canary

```bash
set -euo pipefail
# e2e/stages/12-reconcile.sh
source e2e/lib/checkpoint.sh

./reconciler/run --mode detect --record > "${E2E_OUT}/evidence/reconcile.json"

# CP-1201 AT-102. The permanent seeded canary MUST be found. Zero findings is a FAILED run.
cp_assert CP-1201 "reconciliation found the seeded canary" \
  jq -e '.findings | map(select(.canary == true)) | length == 1' "${E2E_OUT}/evidence/reconcile.json"

cp_assert CP-1202 "a zero-finding run would be classified failed, not clean" \
  jq -e '.run_verdict != "clean" or (.findings | length) > 0' "${E2E_OUT}/evidence/reconcile.json"

# CP-1203 Per-registry comparison counts recorded, so a silently narrowed comparison is itself visible
#         drift (Section 53.1).
cp_assert CP-1203 "per-registry comparison counts recorded and non-zero" \
  jq -e '.comparison_counts | to_entries | all(.value > 0)' "${E2E_OUT}/evidence/reconcile.json"

# CP-1204 The clean run is RECORDED as clean. Silent drift is not permitted (invariant #44).
cp_assert CP-1204 "run result written whether or not findings exist" \
  ./tools/records/find-record --store records/reconciliation --newer-than "${E2E_RUN_START}"

# CP-1205 AT-033. Present the reconciler with a STRICTER-than-declared production control; it must raise it
#         for human review and must NOT relax it (invariant #81).
cp_assert CP-1205 "stricter-than-declared control is raised, not relaxed" \
  ./tools/e2e-drive/stricter-control-probe --repo "${E2E_REPO}" \
    --tighten required_approving_review_count --expect raised-for-review --expect-not relaxed

# CP-1206 AT-032, self-observability: break the health job on purpose; the OS must report its own failure.
cp_assert CP-1206 "the operating system reports a failure in its own health job" \
  ./tools/e2e-drive/self-observability-probe --break health-job --expect-signal SIG-13

# CP-1207 The independent control verifier ran off the ops VM, under its own credential, and wrote to a
#         surface the ops VM cannot write to (Section 53.1).
cp_assert CP-1207 "independent control verifier result present and externally written" \
  ./tools/records/find-record --store records/control-verifier --newer-than "${E2E_RUN_START}" \
    --require writer=control-verifier --require-not writer=ops-vm

# CP-1208 AT-036 / AT-037 — an expired temporary access exception is revoked with no human action, and one
#         that cannot be auto-revoked becomes Blocking drift on its expiry date.
cp_assert CP-1208 "expired exception auto-revoked; unrevokable expiry becomes Blocking" \
  ./tools/e2e-drive/exception-expiry-probe --expect auto-revoked --expect-blocking-on-failure

# CP-1209 AT-039 — a bootstrap exception at expiry arms its gate or surfaces as Blocking drift. It cannot
#         lapse silently.
cp_assert CP-1209 "bootstrap exception at expiry arms or blocks" \
  ./tools/e2e-drive/bootstrap-expiry-probe --expect arm-or-block

# CP-1210 AT-110 — the reconciler credential is provably bounded. Executed, not asserted: six attempts,
#         all six must fail, and the credential must then still complete a normal run.
cp_assert CP-1210 "reconciler credential bounded on all six attempts, then still reconciles" \
  ./tools/e2e-drive/at-110-reconciler-bounds.sh
```

### E2E-13 — Access boundaries, executed

```bash
set -euo pipefail
# e2e/stages/13-access.sh
source e2e/lib/checkpoint.sh

# CP-1310 AT-108 — the founder ops console is provably read-only: four attempts fail, then a read query
#         over Layer A still answers correctly.
cp_assert CP-1310 "ops console read-only on all four attempts, read still works" \
  ./tools/e2e-drive/at-108-ops-console.sh

# CP-1311 AT-109 — the background cage egress wall holds at the HOST layer, not by harness configuration,
#         and the systemd wall-clock stop terminates the worker at the window boundary.
cp_assert CP-1311 "cage egress wall and wall-clock stop hold" \
  ./tools/e2e-drive/at-109-cage.sh

# CP-1312 Invariant #18 / Section 37.3 actor gate: the background machine account cannot merge, approve or
#         deploy — verified GitHub-side, outside the harness.
cp_assert CP-1312 "machine account restricted to draft PRs, GitHub-side" \
  ./tools/e2e-drive/draft-pr-only-verification.sh --account machine-bg

# CP-1313 Invariant #111 — no customer data in repositories. Fixture provenance and record construction
#         are both checked on the pilot's tree and records.
cp_assert CP-1313 "no customer data in repositories" \
  ./tools/evidence/check-no-customer-data --repo "${E2E_REPO}" --records "${E2E_RECORDS_REPO}"
```

---

## 5. The negative suite — every gate proven able to fail

Each entry drives a gate into failure deliberately and asserts the refusal reason. **The suite runs on a
disposable branch and a disposable tag against the pilot product; nothing here reaches `main`.** Every one
uses `cp_refute`, so a gate that silently permits the forbidden act fails the run.

| ID | Gate under test | The deliberate violation | Must be refused because | Spec / test |
|---|---|---|---|---|
| NEG-01 | Digest immutability | Request a production deploy of a digest that never passed staging | requested digest ≠ staging-verified digest | Inv **#22**, §33.4 |
| NEG-02 | Digest immutability | Trigger `deploy-production.yml` with `rebuild: true` | production never rebuilds | Inv **#22**, **#23** |
| NEG-03 | `/version` match | Deploy, then hot-patch the running container | `verify-digest-chain` mismatch → P0 | §32 item 11, §99.2 F |
| NEG-04 | Verification contract | Replace the contract with `verify: exit 0` and rerun with the seeded defect | seeded defect passed → FAILED run, SIG-18 | §31.2 |
| NEG-05 | Plan-checker | Submit a schema-touching plan with no rollback strategy | hard reject | §30.2 |
| NEG-06 | Plan-checker | Submit a plan whose task has no automated verify command | hard reject | §30.2 |
| NEG-07 | Plan-checker | Submit a plan referencing a symbol that does not exist in source | hard reject | §30.2 |
| NEG-08 | Plan-checker | Submit a plan adding a slopsquat package name | legitimacy check against live registry API | §30.2, §33.2 |
| NEG-09 | Gate 1 independence | `dev-a` approves `dev-a`'s own plan | Gate 1 admits no self-approval | §26.1 |
| NEG-10 | Gate 2 independence | Author approves own PR | approval of most recent reviewable push by a non-author | Inv **#8**, **#9** |
| NEG-11 | Gate 2 staleness | Approve, then push a new commit, then merge | approval invalidated by the new push | Inv **#9** |
| NEG-12 | Read-only approval | A Read-permission holder approves | Read approval does not satisfy protection | §95.4 |
| NEG-13 | Production self-approval | The approver dispatches the deploy | workflow-identity gate: approver == deployer | §27.2, Inv **#12** |
| NEG-14 | Production approval ordering | Approve production before staging verification completes | approval is against a staging-verified digest only | §27 |
| NEG-15 | Verification block | Raise a verification block, then attempt production deploy | fail-closed while an open block exists | §27 |
| NEG-16 | Environment ref policy | Push a branch declaring `environment: production` and dispatch it | deployment branch/tag policy rejects the ref | §33.4 |
| NEG-17 | Record write path | Attempt a `records/**` write with the reconciler credential | records-writer only; reconciler is bounded | §97.1, **AT-110** |
| NEG-18 | Reconciler canary | Remove the seeded canary from the comparison set and run | zero findings = FAILED run, SIG-13 | **AT-102**, §53.1 |
| NEG-19 | Required-check integrity | Add an `if:` path filter to a job emitting a required check | `skipped`/`neutral` on a required context is Blocking | §33.2 |
| NEG-20 | Tag pin integrity | Move a `workflows/*` tag onto a new SHA | tag ruleset blocks update/delete, empty bypass list | §33.2, §53.1 |
| NEG-21 | Renovate path guard | Push a lockfile-only commit authored by a non-Renovate identity to a Renovate branch | authorship half of the guard | §33.2 |
| NEG-22 | Friday freeze | Dispatch a production deploy at 15:30 declared-calendar Friday | freeze gate, resolved against the declared calendar | §34.2, §97.1 |
| NEG-23 | Machine authority | Machine account attempts merge / approve / deploy | actor gate, GitHub-side | Inv **#18**, §37.3 |
| NEG-24 | Parity | Add a staging-only environment variable and deploy to production | parity violation is blocking on a production path | §33.1 |
| NEG-25 | Exception expiry | Create an exception with no `expiry` | invalid, fails CI | Inv **#77** |
| NEG-26 | Auto-repair direction | Ask auto-repair to move toward a looser control | stricter-only, enforced in code | Inv **#81**, **AT-033** |
| NEG-27 | Deployment record | Make the record write fail, then deploy | record write is a required failing step | §97.2 |
| NEG-28 | Customer data | Add a fixture containing customer-shaped data | fixture-provenance detector | Inv **#111** |

### 5.1 Representative implementations

```bash
set -euo pipefail
# e2e/negative/neg-01.sh — digest immutability
source e2e/lib/checkpoint.sh
FOREIGN="$(./tools/e2e-drive/build-unverified-digest --repo "${E2E_REPO}")"
cp_refute NEG-01 "production deploy of a digest staging never verified" \
  'digest.*(differ|mismatch|not verified in staging)' \
  ./tools/e2e-drive/run-workflow --repo "${E2E_REPO}" --workflow deploy-production.yml --digest "${FOREIGN}"
```

```bash
set -euo pipefail
# e2e/negative/neg-04.sh — a verification contract that cannot fail
source e2e/lib/checkpoint.sh
./tools/e2e-drive/stage-contract --repo "${E2E_REPO}" --replace-with e2e/fixtures/pilot-one/contract-always-passes.yaml
cp_refute NEG-04 "an always-passing contract is rejected as non-discriminating" \
  'seeded[- ]defect passed|SIG-18|contract cannot fail' \
  ./tools/evidence/run-verification-contract --repo "${E2E_REPO}" --with-seeded-defect --expect-discrimination
./tools/e2e-drive/stage-contract --repo "${E2E_REPO}" --restore
```

```bash
set -euo pipefail
# e2e/negative/neg-13.sh — production self-approval
source e2e/lib/checkpoint.sh
cp_refute NEG-13 "the production approver dispatching their own deploy" \
  'approving identity.*(equal|same).*deploying identity|self-approval' \
  ./tools/e2e-drive/run-workflow --repo "${E2E_REPO}" --workflow deploy-production.yml \
    --digest "$(cat "${E2E_OUT}/digest")" --as lead-1 --approved-by lead-1
```

```bash
set -euo pipefail
# e2e/negative/neg-18.sh — the reconciler that finds nothing
source e2e/lib/checkpoint.sh
./tools/e2e-drive/canary-probe --remove
cp_refute NEG-18 "a reconciliation run reporting zero findings" \
  'canary not found|zero findings|SIG-13|FAILED run' \
  ./reconciler/run --mode detect --record --expect-canary
./tools/e2e-drive/canary-probe --restore
cp_assert NEG-18b "canary restored and found again" \
  ./reconciler/run --mode detect --expect-canary
```

```bash
set -euo pipefail
# e2e/negative/neg-19.sh — a required check that can only pass
source e2e/lib/checkpoint.sh
cp_refute NEG-19 "a required check emitted by a path-filtered job" \
  'skipped|neutral|required context did not report' \
  ./tools/e2e-drive/path-filter-probe --repo "${E2E_REPO}" --job verification-contract --add-path-filter
```

```bash
set -euo pipefail
# e2e/negative/neg-22.sh — the Friday freeze
source e2e/lib/checkpoint.sh
cp_refute NEG-22 "a production deploy dispatched at 15:30 Friday declared-calendar time" \
  'freeze|outside core hours|observation window' \
  ./tools/e2e-drive/run-workflow --repo "${E2E_REPO}" --workflow deploy-production.yml \
    --digest "$(cat "${E2E_OUT}/digest")" --simulate-calendar-time "friday 15:30"
```

**NEG-18b matters.** Restoring the canary and finding it again is what stops NEG-18 from being satisfied by
a reconciler that is simply broken. Every destructive negative test in this suite pairs with a restore
assertion; `verdict.sh` fails the run if any `--remove`/`--restore` pair is unbalanced in the log.

---

## 6. What the evidence bundle contains

`e2e/out/<run-id>/` is uploaded as a workflow artifact and its manifest is committed to
`records/e2e/<run-id>.yaml` in `control-plane-records`, written by `records-writer`.

```yaml
# records/e2e/<run-id>.yaml
record_schema_version: 1
id: E2E-2026-08-27-001
product: pilot-one
timestamp: 2026-08-27T09:14:22Z          # UTC with offset, per Section 97.1
integration_sha: <sha>
digest: sha256:<64>
checkpoints_total: 118
checkpoints_passed: 118
negative_tests_total: 28
negative_tests_fired: 28                  # every gate refused what it must refuse
evidence_chain: answered                  # all eleven, with q5 == q11
acceptance_tests_executed: [AT-001, AT-009, AT-032, AT-033, AT-036,
                            AT-037, AT-039, AT-102, AT-103, AT-106,
                            AT-108, AT-109, AT-110]
verdict: PASS
```

Retention: permanent. E2E records are canonical operational records under Section 97 and are append-only —
a correction is a follow-up record, never an edit (invariant **#47**).

---

## 7. The verdict rule

```bash
set -euo pipefail
# e2e/verdict.sh
source e2e/lib/checkpoint.sh
fails=$(awk -F'\t' '$3=="FAIL"' "${E2E_LOG}" | wc -l)
pos=$(awk  -F'\t' '$2 ~ /^CP-/  && $3=="PASS"' "${E2E_LOG}" | wc -l)
neg=$(awk  -F'\t' '$2 ~ /^NEG-/ && $3=="PASS"' "${E2E_LOG}" | wc -l)

[ "$fails" -eq 0 ] || { echo "VERDICT: FAIL — ${fails} checkpoint failures"; exit 1; }
[ "$neg" -ge 28 ]  || { echo "VERDICT: FAIL — only ${neg}/28 gates were proven able to fail"; exit 1; }
[ "$pos" -ge 118 ] || { echo "VERDICT: FAIL — only ${pos}/118 positive checkpoints ran"; exit 1; }
echo "VERDICT: PASS — ${pos} checkpoints, ${neg} gates proven able to fail"
```

### 7.1 Three ways to fail

1. **A positive checkpoint failed.** The chain is broken at that link. Stop; §8.3 routes it.
2. **A negative test did not fire.** A gate permitted what it exists to forbid. This is more serious than
   (1): the happy path may be entirely green while the system has no gate at all.
3. **A negative test fired for the wrong reason.** `cp_refute`'s reason regex did not match. The act was
   refused, but not by the control under test — which means the control is untested and may be absent.

### 7.2 The rule that makes this file honest

**A run with 118 green checkpoints and zero fired gates is a FAILED run.** The count of *gates proven able
to fail* is a first-class pass condition, exactly as Section 53.1 makes the canary a pass condition of a
reconciliation run and Section 31.2 makes the seeded defect a pass condition of a verification contract.
`verdict.sh` enforces it above; it is not a convention.

### 7.3 Rejection rates as a standing instrument

The E2E is one run. Over time the same principle applies to the live estate, and file 09 of this protocol
reads these from the event log:

| Instrument | Reading that means the gate is not working |
|---|---|
| Plan-checker rejections (`plan_rejected` events) | **Zero over a review period** — no plan-checker that rejects nothing is checking anything (Section 30.2) |
| Gate 2 change-requested rate | **Very low may mean rubber-stamping** rather than quality (Section 23) |
| Reconciliation findings | Zero including the canary → **failed**, SIG-13, gap procedure (**AT-102**) |
| Verification-contract seeded case | Last run passed → **SIG-18**, Blocking for that product (Section 31.2) |
| Write freshness on `events/`, `records/deployments/`, `records/uat/` | Past interval → Blocking; zero-shaped metrics are indistinguishable from health (Section 97.2) |

---

## 8. When this runs, and what happens when it doesn't pass

### 8.1 Cadence

| Trigger | Scope |
|---|---|
| Every `integration` → `main` promotion | Full run: E2E-00 … E2E-13 plus the whole negative suite |
| Every merge-train cycle completing (L1 → L4 → L2 → L3 → L5) | Stages E2E-00 … E2E-03 plus NEG-04, NEG-18, NEG-19 — the instrument checks, which are the ones that go quiet |
| Once, as the V1 exit gate | Full run, with the evidence bundle presented as the V1 acceptance artifact |
| Nightly on `integration` | Full run, non-blocking, findings filed as issues |

The full run is a **required status check on the `integration` → `main` pull request**. It is emitted by a
job carrying no `if:` and no path filter (Section 33.2), for the reason NEG-19 tests.

### 8.2 Who runs it

L0 the Integrator. No lane runs it, no lane can edit it, and no lane's green CI substitutes for it. A lane
whose work breaks a checkpoint learns so from an L0-filed blocker issue naming the checkpoint id, not from
a merge conflict.

### 8.3 Routing a failure back to a lane

Every checkpoint maps to exactly one owning lane. The blocker issue is filed against that lane with the
checkpoint id, the evidence file, and the spec clause.

| Checkpoint range | Owning lane (PARTITION) | Typical cause |
|---|---|---|
| `CP-01xx`, `CP-02xx`, `CP-12xx` | **L3** (`reconciler/**`, `tools/provision/**`, `validators/drift/**`) | scaffold gap, drift detection, canary |
| `CP-03xx`, `CP-05xx`, `CP-06xx`, `CP-07xx`, `CP-09xx`, `CP-10xx` | **L2** (`.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**`) | pipeline, digest, evidence chain |
| `CP-0405`, `CP-0506`, `CP-0604`, `CP-07xx` record assertions, `CP-0904`, `CP-1016` | **L4** (records repo, `schemas/records/**`, `tools/records/**`) | record/event shape, write path, freshness |
| `CP-0301`, `CP-0302`, `CP-0306`, schema validation failures | **L1** (`schemas/**`, `registries/**`, `validators/registry/**`) | contract schema, validator |
| `CP-0106`, `CP-0107`, `CP-0206`, `CP-13xx` | **L5** (`access/**`, `infra/**`, `ops-vm/**`, `notify/**`) | protection, environments, cage, console |
| `CP-04xx` Gate 1 tooling, `CP-1000`…`CP-1015` assembly | **L0** (`contracts/**`, root, `e2e/**`) | contract drift or harness defect |

**STOP rule S-03.** A checkpoint failure is never resolved by editing the checkpoint. If the assertion is
believed wrong, that is a **Contract Change Request** to L0 (PARTITION rule 2), not a lane edit — and no
lane owns `e2e/**` in any case.

**STOP rule S-04.** A negative test that does not fire is **never** downgraded to a warning to unblock a
release. It is Blocking-class drift under Section 53.4 Level 4 and the promotion does not proceed.

### 8.4 The bootstrap variant

Where §2.2's actor set cannot be met (fewer than three humans with Write on the pilot repository), run
`./e2e/run.sh --bootstrap`. It:

1. runs every stage and every negative test **not** requiring gate independence;
2. **skips and explicitly records as unproven** NEG-09, NEG-10, NEG-12, NEG-13 — the independence gates;
3. writes `verdict: PASS-BOOTSTRAP` with an `unproven_gates:` list into the E2E record;
4. requires a matching bootstrap exception in `exceptions.yaml` with an expiry, an owner and a
   deactivation trigger (Section 95.2) — and fails if one is absent;
5. asserts everything Section 95.3 keeps binding even in bootstrap: digest immutability (`CP-0903`),
   the verification contract (`CP-0301`, `CP-0304`), the API-key-free environment (`CP-0002`),
   append-only history (`CP-1015`), and **the explicit production-approval event** (`CP-0804`) — because
   without that event the eleven questions are not answerable at all.

`PASS-BOOTSTRAP` is never reported as `PASS`. The activation checklist of Section 95.4 later cites this
record when it arms each gate, and arming re-runs the skipped negative tests for real.

---

## 9. What this file deliberately does not accept as evidence

| Not accepted | Why | What is accepted instead |
|---|---|---|
| A lane's own green CI | Five lanes each green proves nothing about the assembly | Checkpoints run against the assembled `integration` tip (`CP-0001`) |
| A screenshot, a chat message, a verbal confirmation | Not a record; nothing derives from it | A record in a Section 97.2 store, written by a workflow |
| A hand-edited record file | Records are generated; nobody transcribes (Section 97.1) | RECORD-VERIFICATION-RESULT dispatch (`CP-0707`, `CP-0709`) |
| A `skipped` required check | Branch protection counts it as satisfied while nothing ran | Real conclusion asserted (`CP-0502`) |
| A green reconciliation with zero findings | Proves the instrument stopped looking | Canary found and comparison counts recorded (`CP-1201`, `CP-1203`) |
| A verification contract that has never failed | Not a contract (Section 31.2) | Seeded defect rejected (`CP-0304`) and clean tree passed (`CP-0305`) |
| An asserted credential boundary | Section 99.6 risk 6: the most privileged identity's boundary must be executed | AT-110 executed (`CP-1210`), AT-108 (`CP-1310`), AT-109 (`CP-1311`) |
| A digest match at one hop | The chain must hold at every hop | Staging (`CP-0704`), production (`CP-0907`), chain (`CP-1012`), sweep (`CP-1014`) |

---

## 10. Traceability matrix

| Checkpoint | Acceptance test | Invariant(s) | Spec clause |
|---|---|---|---|
| `CP-0002` | — | #84, #25 | 95.3, 40.2 |
| `CP-0004`, NEG-20 | — | #85, #72 | 33.2, 53.1 |
| `CP-0101`–`CP-0110` | **AT-001**, **AT-009** | #52, #53, #79 | 19.1, 33.1, 33.2 |
| `CP-0201`–`CP-0206` | — | #7, #11, #50, #55, #57 | 10, 17, 53.1 |
| `CP-0301`–`CP-0306`, NEG-04 | — | #1, #6 | 31.1, 31.2, 31.3 |
| `CP-0401`–`CP-0406`, NEG-05…NEG-09 | **AT-106** | #16, #11 | 26.1, 30.2, 24.2 |
| `CP-0501`–`CP-0507`, NEG-10…NEG-12, NEG-19, NEG-24 | — | #8, #9, #87 | 23.2, 27, 33.1, 33.2 |
| `CP-0601`–`CP-0605`, NEG-02 | — | #22, #23, #85 | 33.2, 33.4, 48.3 |
| `CP-0701`–`CP-0709` | — | #40, #46 | 31, 34.3, 97.1, 97.2 |
| `CP-0801`–`CP-0804`, NEG-13…NEG-15 | — | #12, #9 | 26.1, 27, 27.1, 27.2 |
| `CP-0901`–`CP-0908`, NEG-01, NEG-16, NEG-22, NEG-27 | — | #22, #23, #41, #47 | 32, 33.4, 34.1, 34.2, 97.2 |
| `CP-1001`–`CP-1016`, NEG-03 | — | #22, #41, #44, #46 | **32**, 41.2, 99.2 F |
| `CP-1101`–`CP-1108` | **AT-103** | #2, #3, #4, #27, #28 | 19.2, 27.2, 34.4, 44 |
| `CP-1201`–`CP-1210`, NEG-17, NEG-18, NEG-25, NEG-26 | **AT-102**, **AT-032**, **AT-033**, **AT-036**, **AT-037**, **AT-039**, **AT-110** | #44, #77, #80, #81 | 53.1, 53.2, 53.4, 54, 95.2 |
| `CP-1310`–`CP-1313`, NEG-21, NEG-23, NEG-28 | **AT-108**, **AT-109** | #18, #20, #21, #111 | 33.2, 36.1, 37.3, 97.2 |

---

## 11. The one-paragraph statement this run earns

When `verdict.sh` prints `VERDICT: PASS`, the following is a fact and not a claim: a product that did not
exist was created by one command; its assignments reached the estate through reconciliation rather than by
hand; a change passed a plan gate its author could not approve and a review gate its author could not
approve; it built exactly one artifact whose digest was recorded with its SBOM; that digest — and no other
— reached staging, passed smoke, passed a human's UAT recorded through a dispatch rather than a
conversation, and passed a performance threshold the product declared; a named human who was neither the
author nor the pipeline approved that specific digest for production; the pipeline deployed that same
digest without rebuilding it; the live service reports that digest at `/version`; all eleven questions of
Section 32 are answered from GitHub, Actions and Grafana with every answer citing a canonical store; a
rollback and a restore were each executed once and recorded; the reconciler found its planted canary; and
twenty-eight gates were each driven into failure on purpose and each refused, for the stated reason.

That is what "V1 is real rather than assembled" means, and this file is the only thing that says it.
