# 04 — The Negative Test Catalogue

**Status:** normative. Part of the verification and merge protocol for the five-lane parallel build.
**Owner:** L0 Integrator. **Consumers:** L1–L5 lane developers, and CI.
**Conforms to:** `Code/implementation/PARTITION.md` (FROZEN).
**Source of truth:** `Research/MultiProduct_MasterSpec_v4.0.md` — Section 100 (acceptance tests AT-001…AT-110), Section 101 (invariants 1…111), Section 102 (edge cases EC-1…EC-112), Section 10 (decisions D1…D109).

---

## 0. Read this first — the inversion rule

Every test in this file is a **negative** test. It performs a forbidden action and asserts that the system **refused**.

```
NT PASS  =  the forbidden action was REFUSED.  The gate held.
NT FAIL  =  the forbidden action SUCCEEDED.    The gate is open. STOP.
```

This inverts the intuition of every other test you have written. A green suite here means *nothing got through*. If you find yourself "fixing" a negative test by making the forbidden action succeed, you have removed a security control. Open a blocker issue instead (Section 9).

A third outcome exists and is not a pass:

```
NT UNARMED = the gate cannot yet be exercised (headcount, phase, or dependency not reached).
```

`UNARMED` is recorded as `UNARMED`, never as `PASS`. This is the arming discipline of Section 52.2 applied to the test set (D77: an unarmed instrument cannot fail, and must not be counted as clean). An unarmed NT requires a live entry in `exceptions.yaml` with a mandatory expiry (invariant 77), a deactivation trigger, and an activation checklist row (Section 95.4). Section 95.4 is explicit that the checklist "is executed for real — including the negative tests — at each threshold, not assumed."

---

## 1. Doctrine — a check that can only pass is not a check

This specification states the principle in four separate places, for four different instruments. It is the same rule each time.

| # | Instrument | The rule as the spec states it | Anchor |
|---|---|---|---|
| 1 | The reconciler | "A run that reports zero findings, including the canary, is a FAILED run, not a clean one: it proves the instrument stopped looking, not that nothing drifted." | §53.1 seeded-canary rule; **AT-102**; **EC-109**; SIG-13 |
| 2 | The verification contract | "A verification contract that cannot fail is not a contract." Every `verification/contract.yaml` declares a seeded-defect case the contract MUST fail; a run in which it passes is a FAILED run. | §31.2; SIG-18; §103.1 |
| 3 | The plan-checker | "Watch the reason mix, not the rate. **Zero rejections means the gates are not working.**" | §103.1, Plan rejection rate |
| 4 | Code review | "Review rejection rate — very low may mean rubber-stamping; very high may mean weak plans." | §103.9 |

And once more, structurally, for branch protection itself: §11.1 warns that a design assuming Read is sufficient for cross-review "fails silently and produces exactly the outcome this operating system exists to prevent: **a gate that appears to be working and is not**." §11.3 answers it: "The Phase 1 completion check verifies this negatively."

**The rule this file enforces on every lane.** A gate is not delivered when it is configured. A gate is delivered when a negative test has demonstrated it refusing the thing it exists to refuse, and that demonstration has been recorded. A lane PR that adds a gate without adding its negative test is incomplete and is rejected at the merge train (Section 8).

**Why this file exists at all.** Five low-context AI developers build in parallel. None of them can see the whole system. A lane can configure a rule that looks correct in its own tree and is inert in the estate — a required status check emitted by a job with an `if:` condition (§33.2), a compensating check placed inside the ruleset it compensates for (D89), a CODEOWNERS entry naming an identity that holds no Write (§11.1). Every one of those reads green. The negative test is the only artifact in the build that can tell the difference.

---

## 2. The harness

### 2.1 Ownership of test material

Fixtures are owned by the lane that owns the gate. Directory-per-item, one file per fixture — PARTITION rule 3, so nothing conflicts on merge.

| Artifact | Path | Lane |
|---|---|---|
| Runner entrypoint | `Makefile` target `negative` | L0 |
| Per-lane driver | `<owned-path>/negative/run.sh` | owning lane |
| Per-test fixture | `<owned-path>/negative/NT-<nn>/` (one directory per test) | owning lane |
| Registry-gate fixtures | `validators/registry/negative/NT-<nn>/` | L1 |
| Pipeline/evidence fixtures | `tools/evidence/negative/NT-<nn>/` | L2 |
| Drift/reconciler fixtures | `validators/drift/negative/NT-<nn>/` | L3 |
| Record-schema fixtures | `tools/records/negative/NT-<nn>/` | L4 |
| Access/infra fixtures | `access/negative/NT-<nn>/` | L5 |
| Result records | `records/negative-tests/<date>-NT-<nn>.yaml` in `control-plane-records` | L4 writes the schema; the harness writes the records |

No lane writes another lane's fixture directory. A PR touching a foreign `negative/` path fails the lane-guard check exactly like any other foreign path (PARTITION rule 1, and NT-30 below).

**The cross-lane route for reading another lane's tool, named explicitly (B-08).** Eight negative
tests owned by L1, L2, L4 and L5 (including NT-06, NT-08, NT-13, NT-17, NT-20, NT-24, NT-27,
NT-29 — every one that shells out to `python3 reconciler/run.py ...`) invoke L3's reconciler CLI
directly. This is not the same defect as NT-03's misplaced fixture above: none of these NTs
*writes* into `reconciler/**`, and invoking a lane's declared CLI entrypoint as an external,
read-only consumer is the same shape protocol/01's contract C-02 already licenses for L1's
validator CLI. It is a gap only in that no contract file names `reconciler/run.py --check <name>
--format json` as a frozen interface the way C-02 names the validator's — so an L3-side flag
rename breaks eight other lanes' tests with no CCR gate to catch it first. **Named route:**
`reconciler/run.py`'s `--check`/`--once`/`--format json` surface is a cross-lane consumption
interface exactly like C-02's, and a Contract Change Request against it follows the same route
as any other contract change (protocol/01 §7.2-equivalent) whenever an NT's invocation of it
changes; it is not, and never becomes, a foreign-path write.

### 2.2 The identity cast

Several tests require more than one identity. Bind them once. These are real accounts in the organisation, not variables invented per test.

```bash
set -euo pipefail
export ORG="${ORG:?set ORG to the GitHub organisation login}"
export CP="${CP:-control-plane}"                 # §98.2 control-plane repository
export CPR="${CPR:-control-plane-records}"       # D89 records repository
export SANDBOX="${SANDBOX:?set SANDBOX to the disposable negative-test product repository}"
export ESTATE_DOMAIN="${ESTATE_DOMAIN:?set ESTATE_DOMAIN to the estate's product domain suffix, e.g. products.example.com}"

# Identities — §11.2 person classes, §40.1 secret tiers, §97.1 write path
export NT_AUTHOR="${NT_AUTHOR:?a human with Write on $SANDBOX}"
export NT_REVIEWER_WRITE="${NT_REVIEWER_WRITE:?a second human with Write on $SANDBOX}"
export NT_REVIEWER_READ="${NT_REVIEWER_READ:?a human with organisation base Read and no Team granting Write}"
export NT_MACHINE="${NT_MACHINE:?the background-layer machine account, §37.3}"
export GH_TOKEN_AUTHOR="${GH_TOKEN_AUTHOR:?}"
export GH_TOKEN_REVIEWER_WRITE="${GH_TOKEN_REVIEWER_WRITE:?}"
export GH_TOKEN_REVIEWER_READ="${GH_TOKEN_REVIEWER_READ:?}"
export GH_TOKEN_MACHINE="${GH_TOKEN_MACHINE:?}"
export GH_TOKEN_RECONCILER="${GH_TOKEN_RECONCILER:?the reconciler credential, §40.1 tier 5}"
export GH_TOKEN_RECORDS_WRITER="${GH_TOKEN_RECORDS_WRITER:?records-writer App token, scoped to $CPR only, D89}"
```

`$SANDBOX` is a disposable repository carrying the production branch-protection template verbatim (§11.3) and nothing of value. Never run the branch-protection negative tests against a live product repository: several of them leave an unmergeable pull request behind on purpose.

### 2.3 Output contract

**`GATE-RESULT` (per `protocol/00-test-strategy.md` §3) is the mandatory terminal line on stdout for every negative test, everywhere in this file — this is A2 of FD-098.** The `NT-<nn>` summary line below is retained — it is what a human reads, and what the result record's `refusal_evidence` (§2.5) is built from — but it is now **penultimate, advisory only**, and is no longer "last" or the thing the harness parses:

```
NT-<nn> <PASS|FAIL|UNARMED> :: <gate name> :: <what the system did>
GATE-RESULT gate=NT-<nn> level=T1 assertions=<n> failures=<n> negatives_run=<n> negatives_that_failed_correctly=<n>
```

Every `` `NT-<nn> PASS :: …` `` line shown in §4's worked examples below is written as it would appear **before** this reordering; read each as the penultimate line, with a `GATE-RESULT` line (per the template above) following it as the true last line of output. They are not individually rewritten below to avoid drowning thirty near-identical `GATE-RESULT` lines in prose that is otherwise about what each gate proves.

**Exit codes are owned by `protocol/00-test-strategy.md` §3, not restated here as a competing table.** That contract is `0`=PASS, `1`=FAIL (an assertion failed / here: the forbidden action was not refused), `2`=VACUOUS (ran, zero assertions), `3`=NON-DISCRIMINATING (a negative fixture passed the gate). This file previously defined its own three-way split — `2`=UNARMED, `3`=harness-error — which collided with `00`'s integers (FD-098 / `_98-DEEP-REVIEW.md` B-01). Resolved as follows:

* `FAIL` (gate open) → exit `1`, unchanged.
* `UNARMED` (§0 above: the gate cannot yet be exercised) is **not an exit code** under `00`'s contract — it is reported on the `NT-<nn>` summary line as the token `UNARMED` (see §2.5's result record `outcome: UNARMED`), and the harness must not conflate it with the VACUOUS meaning `00` gives exit `2`.
* Harness error / test did not run → exit `3` under `00`'s table (NON-DISCRIMINATING is the right read: an unrunnable negative test has not demonstrated a refusal, which is exactly what "did not discriminate" means), not the old exit `2`.

> **Runtime-behavior note, not applied here.** `make negative`'s actual exit-code wiring and any already-written `run.sh` driver still literally return the old `2`/`3` split described above. Renumbering that is a live-script behavior change and is deliberately **not** made in this documentation pass. Flagged as an outstanding mechanical follow-up task: audit `make negative`'s exit-code handling and every lane's `negative/run.sh` against `00-test-strategy.md` §3 and renumber, confirming no CI step keys off the old values first.

### 2.4 Invocation

```bash
set -euo pipefail
make negative                    # whole catalogue
make negative LANE=1             # one lane's tests
make negative NT=NT-06           # one test
make negative REPORT=1           # also writes records/negative-tests/ entries
```

### 2.5 The result record

```yaml
# records/negative-tests/2026-09-14-NT-06.yaml
record_schema_version: 1
id: NT-2026-09-14-006
product: control-plane
timestamp: 2026-09-14T09:14:22+00:00
test: NT-06
gate: reconciliation-seeded-canary
outcome: PASS                    # PASS | FAIL | UNARMED
refusal_evidence: "reconciler exited 2: FAILED RUN — canary CANARY-001 not reported"
positive_control: PASS           # the paired P-side, §6
executed_by: <person_id>         # person ID, never a display name — §91.8, NT-09
run_url: https://github.com/<org>/control-plane/actions/runs/<id>
```

`executed_by` carries a person ID. A display name here fails NT-09 against this very file. The catalogue is subject to its own rules.

---

## 3. The register

**`NT-<nn>` is not the canonical negative-test namespace** — `GATE-L<n>-<nnn>` is (FD-098, A3; `00-test-strategy.md` §4.1 rule 8). `NEGATIVE-TEST-CONCORDANCE.md` maps every `NT-<nn>` below onto its `GATE-L<n>-<nnn>` equivalent, using this register's own Owner column.

Merge-train order is L1 → L4 → L2 → L3 → L5 (PARTITION). The "Blocks" column names the merge hop that cannot proceed while the test is FAIL or UNARMED-without-exception.

| NT | Gate | Forbidden action | Owner | Blocks | Spec anchors |
|---|---|---|---|---|---|
| **NT-01** | No self-approval | Author approves and merges own PR | L5 | integration→main | inv **9**, inv **12**, §11.3, §27.2, §95.4 |
| **NT-02** | Code Owner review is human-Write | Read-only identity's approval satisfies protection | L5 | integration→main | §11.1, §11.3, §95.4 |
| **NT-03** | Human-only CODEOWNERS | Machine-account approval satisfies protection | L5 | integration→main | §11.3, §37.3, **D53**, inv **18** |
| **NT-04** | Artifact immutability | Deploy a digest staging never verified | L2 | L2→integration | inv **22**, §32 item 5/11, §33.4, §53.2 L4 |
| **NT-05** | Privileged-workflow isolation | Run a privileged workflow on a shared-pool runner | L2 | L2→integration | §36.3, **D87**, §53.1 (3 Blocking rows) |
| **NT-06** | Seeded reconciliation canary | Reconciler completes reporting zero findings | L3 | L3→integration | **AT-102**, §53.1, **EC-109**, SIG-13 |
| **NT-07** | Capability vocabulary is closed | Grant a capability with no row in the §9 table | L1 | L1→integration | §9.1, §64.1, inv **79** |
| **NT-08** | Role defaults carry no authority | `roles.yaml` default includes a founder-class capability | L1 | L1→integration | §9.1, **D109**, inv **106**, **AT-090** |
| **NT-09** | Records are de-identified | Record body carries a display name | L4 | L4→integration | §91.8, **D88**, §97.2, inv **111** |
| **NT-10** | Bypass is one identity's grant | Foreign-identity commit on a bypass-actor branch | L2/L3 | L2→integration | §33.2, §53.1, **D89**, **D74** |
| NT-11 | Required checks are real | A required check reports `skipped`/`neutral` and merge proceeds | L2 | L2→integration | §33.2 path filters, §53.1 |
| NT-12 | `workflows/*` tags are immutable | Move a consumed workflow tag to a new SHA | L2 | L2→integration | §33.2, §53.1, inv **72**, inv **85** |
| NT-13 | Verification contract discriminates | Seeded-defect case passes and the run reports clean | L2 | L2→integration | §31.2, SIG-18, §103.1 |
| NT-14 | Machine cannot touch enforcement | Machine identity pushes a workflow-file change | L3 | L3→integration | inv **18**, §33.2, §53.1, §53.2 L4 |
| NT-15 | Actor gate on privileged dispatch | Machine account dispatches `deploy-production.yml` | L2 | L2→integration | §37.3, inv **18**, **D71** |
| NT-16 | Reconciler credential is bounded | Reconciler writes a secret, environment, workflow or record | L3 | L3→integration | **AT-110**, §99.6 risk 6, §40.1 |
| NT-17 | No auto-loosening | Reconciler relaxes a stricter-than-declared control | L3 | L3→integration | **AT-033**, inv **81**, §53.3 |
| NT-18 | Exceptions expire | Register an exception with no expiry | L1 | L1→integration | inv **77**, **AT-036**, **AT-037**, **AT-039** |
| NT-19 | Environment ref policy | Deploy to `production` from a non-default, non-tag ref | L5 | L5→integration | §33.4, §40.3, §53.1 |
| NT-20 | Records repo is append-only | Force-push or delete on `control-plane-records` | L4 | L4→integration | **D107**, inv **47**, §63.1 |
| NT-21 | Records-writer is scoped | Records-writer token writes to `control-plane` | L4 | L4→integration | **D89**, §97.1, §40.1 |
| NT-22 | Layer B is not delegable | Create an assignment granting `people-intelligence` | L1 | L1→integration | **AT-090**, **AT-091**, inv **106**, **D109** |
| NT-23 | Authority delta needs a decision | Registry diff adds a capability with no decision record ID | L1 | L1→integration | §26.4, SIG-05 rationale |
| NT-24 | Plan-checker rejects | Submit a plan with no verify command / no recovery strategy | L2 | L2→integration | §30.2, §28.1, §103.1 |
| NT-25 | Independent control verifier | Verifier runs under the credential it verifies | L3 | L3→integration | §53.1 independent verifier, §37.3 |
| NT-26 | Restore claim needs evidence | `restore_tested` date with no matching record | L1 | L1→integration | §53.1, inv **3**, inv **4**, **AT-035** |
| NT-27 | Write-freshness detector | A record store silently stops being written | L4 | L4→integration | §97.2, §53.1, §52.3 |
| NT-28 | Ephemeral privileged runners | Non-ephemeral runner registered in the `privileged` group | L5 | L5→integration | §36.3, **D87**, §53.1 |
| NT-29 | No customer data in git | Commit a fixture with no declared provenance | L2 | L2→integration | inv **111**, §38.3, §96.6 S19 |
| NT-30 | Lane guard | A lane PR edits a foreign lane's path | L0 | every hop | PARTITION rules 1, 2, 4 |
| NT-31 | Contract freeze | A lane PR edits `contracts/**` | L0 | every hop | PARTITION rule 2 |
| NT-32 | The catalogue can fail | Every NT is proven able to emit FAIL | L0 | integration→main | §1 doctrine, §53.1, §31.2 |

---

## 4. The ten load-bearing tests

Each block gives the exact setup, the exact command, and the exact output that proves the gate held.

---

### NT-01 — A self-approved PR must fail

**Gate.** Invariant 9: "No self-approval, enforced mechanically by requiring approval of the most recent reviewable push." §11.3 arms it: *require at least 1 approving review*, *require review from Code Owners*, *require approval of the most recent reviewable push*, *dismiss stale approvals*. §95.4 names this as the first verification at the 2-humans-with-Write threshold: "A self-approved PR fails branch protection."

**Why it is load-bearing.** GitHub refuses a self-review at the API, but that refusal alone is not the gate — an author who holds Write can still attempt the merge, and on a repository where the approval count is 0 or the ruleset was applied without `require_last_push_approval`, the merge succeeds. The test asserts refusal at *both* points.

**Setup.**

```bash
set -euo pipefail
cd "$(mktemp -d)"
gh repo clone "$ORG/$SANDBOX" . -- --depth=1
git switch -c nt-01-self-approve
printf 'nt-01 %s\n' "$(date -u +%FT%TZ)" > nt-01.txt
git add nt-01.txt
git -c user.name="$NT_AUTHOR" -c user.email="$NT_AUTHOR@users.noreply.github.com" \
    commit -m "NT-01 self-approval negative test"
git push -u origin nt-01-self-approve
PR=$(GH_TOKEN="$GH_TOKEN_AUTHOR" gh pr create --repo "$ORG/$SANDBOX" \
      --base main --head nt-01-self-approve \
      --title "NT-01 self-approval negative test" --body "negative test; do not merge" \
      | grep -oE '[0-9]+$')
```

**Command — part A: the author attempts to approve their own PR.**

```bash
GH_TOKEN="$GH_TOKEN_AUTHOR" gh api -X POST \
  "/repos/$ORG/$SANDBOX/pulls/$PR/reviews" -f event=APPROVE 2>&1 | tee nt-01-a.txt
```

**Required output A.**

```
gh: Unprocessable Entity (HTTP 422)
{"message":"Unprocessable Entity","errors":["Can not approve your own pull request"],...}
```

**Command — part B: the author attempts the merge anyway.**

```bash
set -euo pipefail
GH_TOKEN="$GH_TOKEN_AUTHOR" gh api -X PUT \
  "/repos/$ORG/$SANDBOX/pulls/$PR/merge" -f merge_method=squash 2>&1 | tee nt-01-b.txt || true
GH_TOKEN="$GH_TOKEN_AUTHOR" gh pr view "$PR" --repo "$ORG/$SANDBOX" \
  --json mergeable,mergeStateStatus,reviewDecision
```

**Required output B.**

```
gh: Method Not Allowed (HTTP 405)
{"message":"At least 1 approving review is required by reviewers with write access.",...}

{"mergeable":"MERGEABLE","mergeStateStatus":"BLOCKED","reviewDecision":"REVIEW_REQUIRED"}
```

**Command — part C: assert the protection rule that produces this is actually set.**

```bash
set -euo pipefail
GH_TOKEN="$GH_TOKEN_AUTHOR" gh api "/repos/$ORG/$SANDBOX/branches/main/protection" \
  --jq '{
    approvals: .required_pull_request_reviews.required_approving_review_count,
    codeowners: .required_pull_request_reviews.require_code_owner_reviews,
    last_push: .required_pull_request_reviews.require_last_push_approval,
    dismiss_stale: .required_pull_request_reviews.dismiss_stale_reviews,
    admins: .enforce_admins.enabled
  }'
```

**Required output C.**

```json
{"approvals":1,"codeowners":true,"last_push":true,"dismiss_stale":true,"admins":true}
```

**Verdict.** PASS requires all three: 422 on A, 405 with `mergeStateStatus: BLOCKED` on B, and every field `true`/`1` on C. Any merge that succeeds, or `last_push: false`, is **FAIL — GATE OPEN**.

`NT-01 PASS :: no-self-approval :: review 422 "Can not approve your own pull request"; merge 405; BLOCKED`

**Teardown.** `gh pr close "$PR" --repo "$ORG/$SANDBOX" --delete-branch` — the PR is closed, never merged, and the closure is recorded (§37.5: failed and rejected output is retained; the record of why is the point).

---

### NT-02 — A Read-only approval must not satisfy protection

**Gate.** §11.1, the verified permission table: *Approval counts toward required approving reviews* — Read: **No**, Triage: **No**, Write: **Yes**. And the consequence the spec spells out: a Cross-Reviewer holding only Read "can submit a review that visually reads as an approval — but that approval does **not** satisfy branch protection. The merge stays blocked." §95.4 lists it verbatim: "a Read-only approval does not satisfy it."

**Why it is load-bearing.** This is the spec's own named example of a gate that appears to be working and is not. The approval is *visible in the UI as a green check on the reviewer's row*. Only the merge attempt reveals the truth. If a lane provisions Cross-Reviewers with Read on the theory that least privilege demands it, every cross-review in the estate becomes decorative and nothing detects it. §11.1 closes with: "Therefore Cross-Reviewers require Write on the repositories they review."

**Setup.** Reuse or recreate the PR pattern from NT-01, authored by `$NT_AUTHOR`. Confirm the reviewer's actual permission first — the test is meaningless if the account silently holds Write.

```bash
GH_TOKEN="$GH_TOKEN_AUTHOR" gh api \
  "/repos/$ORG/$SANDBOX/collaborators/$NT_REVIEWER_READ/permission" --jq .permission
# required: read
```

**Command.**

```bash
set -euo pipefail
# 1. the Read-only identity approves — this SUCCEEDS, and that is the trap
GH_TOKEN="$GH_TOKEN_REVIEWER_READ" gh api -X POST \
  "/repos/$ORG/$SANDBOX/pulls/$PR/reviews" -f event=APPROVE -f body="NT-02" \
  --jq '{state, user: .user.login}'

# 2. the approval is visible
GH_TOKEN="$GH_TOKEN_AUTHOR" gh api "/repos/$ORG/$SANDBOX/pulls/$PR/reviews" \
  --jq '.[] | {user: .user.login, state}'

# 3. the merge must still be refused
GH_TOKEN="$GH_TOKEN_AUTHOR" gh api -X PUT \
  "/repos/$ORG/$SANDBOX/pulls/$PR/merge" -f merge_method=squash 2>&1 || true

# 4. the review decision must not have moved
GH_TOKEN="$GH_TOKEN_AUTHOR" gh pr view "$PR" --repo "$ORG/$SANDBOX" \
  --json reviewDecision,mergeStateStatus
```

**Required output.**

```
{"state":"APPROVED","user":"<NT_REVIEWER_READ>"}          <-- step 1: the approval exists
{"user":"<NT_REVIEWER_READ>","state":"APPROVED"}          <-- step 2: and is visible

gh: Method Not Allowed (HTTP 405)                          <-- step 3: and counts for nothing
{"message":"At least 1 approving review is required by reviewers with write access.",...}

{"reviewDecision":"REVIEW_REQUIRED","mergeStateStatus":"BLOCKED"}
```

**Verdict.** PASS requires the approval to be *recorded* and the merge to be *refused*. If step 3 merges, the estate's cross-review network is decorative: **FAIL — GATE OPEN**, and escalate immediately, because it means Read-holding reviewers are counting somewhere.

`NT-02 PASS :: read-approval-does-not-count :: APPROVED recorded; merge 405; reviewDecision REVIEW_REQUIRED`

**Paired positive control — mandatory.** §95.4 requires the third clause too: "a Write-holding cross-reviewer approval does." Run P-02 (Section 6) in the same execution. Without it, NT-02 passes identically on a repository where *no* approval works — a broken CI, a misconfigured ruleset, a wrong base branch. A negative test that cannot distinguish "the gate held" from "everything is broken" proves nothing.

---

### NT-03 — A machine-account approval must not satisfy protection

**Gate.** §11.3: "CODEOWNERS is generated to contain human identities only — no machine account ever appears in it — so a machine-account approval can never satisfy branch protection: the required Code Owner review must come from a human. **The Phase 1 completion check verifies this negatively.**" §37.3 states the same closure from the machine side: the machine account *does* hold Write on whitelisted repositories, so the permission model alone does not close the approval path — human-only CODEOWNERS does. D53 records the decision.

**Why it is load-bearing.** The machine account holds Write. Write is exactly the permission whose approval *does* count (§11.1). The only thing standing between a background-layer identity and a satisfied gate is the content of a generated file. That file is regenerated by the reconciler on every run (§53.1, Level 3 auto-repair), which means a single generator regression re-opens this path silently and estate-wide. This test must run against the *generated* CODEOWNERS, not a reviewed one.

**Setup.**

```bash
set -euo pipefail
# Assert the generator's output first — the file, not the intention
GH_TOKEN="$GH_TOKEN_AUTHOR" gh api \
  "/repos/$ORG/$SANDBOX/contents/.github/CODEOWNERS" --jq '.content' \
  | base64 -d > nt-03-codeowners.txt
grep -F "$NT_MACHINE" nt-03-codeowners.txt && { echo "NT-03 FAIL :: machine in CODEOWNERS"; exit 1; }
```

**Command.**

```bash
set -euo pipefail
# 1. the machine account approves
GH_TOKEN="$GH_TOKEN_MACHINE" gh api -X POST \
  "/repos/$ORG/$SANDBOX/pulls/$PR/reviews" -f event=APPROVE -f body="NT-03" \
  --jq '{state, user: .user.login}'

# 2. the merge must be refused for want of a CODE OWNER review specifically
GH_TOKEN="$GH_TOKEN_AUTHOR" gh api -X PUT \
  "/repos/$ORG/$SANDBOX/pulls/$PR/merge" -f merge_method=squash 2>&1 || true

# 3. and the estate-wide assertion: no machine identity in any CODEOWNERS anywhere
# Fixture lives under access/negative/ (L5-owned), matching NT-03's own ownership row
# above (line 146) and §2.1's rule that a fixture lives with the lane that owns the gate
# under test — never under validators/drift/** (L3), which is a foreign path for this
# test (B-08: this was the one fixture in the file misplaced against its own §2.1 rule).
python3 access/negative/NT-03/assert_codeowners_human_only.py --org "$ORG" --all-repos
```

**Required output.**

```
{"state":"APPROVED","user":"<NT_MACHINE>"}

gh: Method Not Allowed (HTTP 405)
{"message":"Changes must be approved by a code owner: Review required by an approver...",...}

assert_codeowners_human_only: 9 repositories scanned, 9 CODEOWNERS files read,
  machine identities found: 0
  identities cross-checked against people.yaml: 14/14 resolve to a person with access_status: active
NT-03 PASS :: human-only-codeowners :: machine APPROVED recorded; merge 405 code-owner required; 0 machine identities estate-wide
```

**Verdict.** The count line is not decoration. `9 repositories scanned, 9 CODEOWNERS files read` is what stops a silently narrowed scan reporting `machine identities found: 0` because it read nothing — the same failure mode §53.1 closes with its per-registry comparison counts. A scan reporting zero findings **and** zero files read is **FAIL — HARNESS ERROR**, exit 3.

**Note for L5.** The scanner runs off the operations VM under the independent verifier's own read-only credential (§53.1, "The independent control verifier"), not under the reconciler's. See NT-25.

---

### NT-04 — A digest mismatch must be rejected

**Gate.** Invariant 22: "The production artifact is the same digest verified in staging. Never rebuilt." §32: "item 5 and item 11 must match, and the digest deployed to production must be byte-identical to the one verified in staging. **CI rejects any production deployment where the requested digest differs from the digest that passed staging verification.**" §33.4 marks artifact immutability P0. §53.2 lists "artifact digest mismatch" as Level 4 Blocking drift.

**Why it is load-bearing.** This is the join between the evidence chain and reality. If it does not hold, every one of the eleven questions in §32 can be answered correctly about an artifact that is not the one running.

**Setup.** Take a real staging-verified digest from the sandbox product, then construct a second, different, well-formed digest.

```bash
set -euo pipefail
GOOD=$(gh api "/repos/$ORG/$SANDBOX/deployments?environment=staging&per_page=1" \
        --jq '.[0].payload.digest')
echo "staging-verified digest: $GOOD"
BAD="sha256:$(printf 'nt-04-%s' "$(date -u +%s)" | sha256sum | cut -c1-64)"
echo "mismatched digest:       $BAD"
test "$GOOD" != "$BAD"
```

**Command.**

```bash
set -euo pipefail
GH_TOKEN="$GH_TOKEN_AUTHOR" gh workflow run deploy-production.yml \
  --repo "$ORG/$SANDBOX" --ref main -f digest="$BAD" -f reason="NT-04 negative test"
sleep 20
RUN=$(gh run list --repo "$ORG/$SANDBOX" --workflow deploy-production.yml \
        --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN" --repo "$ORG/$SANDBOX" --exit-status || rc=$?; echo "exit=${rc:-0}"
gh run view "$RUN" --repo "$ORG/$SANDBOX" --log-failed | grep -A3 'digest'
```

**Required output.**

```
exit=1
assert-digest-matches-staging  FAILURE
  requested digest : sha256:3f1c...  (input)
  staging-verified : sha256:9ab4...  (records/deployments/<id>.yaml, environment: staging)
  ERROR: requested digest was not verified in staging. Refusing to deploy.
  invariant 22 (§101.5); §32 evidence chain item 5; §33.4
  This deployment is Blocking-class drift if it recurs (§53.2 Level 4).
```

**Verdict.** PASS requires: workflow conclusion `failure`, failure at the digest assertion step (not at a later step, and not at checkout), no `production` deployment record written, and no environment secret materialised into the job.

```bash
# no deployment record was written
gh api "/repos/$ORG/$CPR/contents/records/deployments" --jq '.[].name' | grep -c "$BAD" # required: 0
```

`NT-04 PASS :: artifact-immutability :: deploy-production refused mismatched digest at assert-digest-matches-staging; no production record written`

**Second half of the same gate.** Also assert the *live* half — §32 item 11. A digest running in production that differs from the last recorded production deployment is drift, not a deploy question:

```bash
curl -fsS "https://$SANDBOX.$ESTATE_DOMAIN/version" --max-time 10 | jq -r .digest
gh api "/repos/$ORG/$CPR/contents/records/deployments" --jq 'last.name'
# the two must agree; disagreement is Level 5 (§53.2, production environment drift)
```

---

### NT-05 — A privileged workflow on a shared runner must fail

**Gate.** §36.3, Privileged-workflow isolation (P0). The privileged workflows are a closed set: `deploy-production.yml`, `migrate.yml`, the rollback workflow, and the per-product production-restore workflow. "**The separation is asserted in the workflow, not only in configuration.** Each privileged workflow fails closed unless the runner it resolved to carries the `privileged` label or is hosted; a privileged workflow that finds itself on a shared-pool runner does not proceed." D87 records the reasoning: "Persistence, not provenance, is the exposure" — the background machine account holds Write, a branch push executes CI, and a long-lived runner carries whatever the first job left behind into the next privileged job.

**Why it is load-bearing.** Configuration alone cannot hold this. Runner labels are assigned outside the repository; a group can be widened by an org admin with no diff in any repo. The in-workflow assertion is the only control that travels with the code, and the only one a negative test can exercise.

**Setup.** Do not modify the real privileged workflow. Copy it into the fixture tree and point the copy at a shared-pool label.

```bash
set -euo pipefail
mkdir -p tools/evidence/negative/NT-05
cp .github/workflows/deploy-production.yml tools/evidence/negative/NT-05/nt-05-shared-runner.yml
# retarget the runner, change nothing else
sed -i 's/^\( *runs-on: \).*$/\1[self-hosted, shared-pool]/' \
  tools/evidence/negative/NT-05/nt-05-shared-runner.yml
grep -n 'runs-on\|assert-runner-tier' tools/evidence/negative/NT-05/nt-05-shared-runner.yml
```

**Command.**

```bash
set -euo pipefail
cp tools/evidence/negative/NT-05/nt-05-shared-runner.yml .github/workflows/
git add .github/workflows/nt-05-shared-runner.yml
git commit -m "NT-05 privileged workflow on shared runner (negative test)"
git push -u origin nt-05-shared-runner
GOOD=$(gh api "/repos/$ORG/$SANDBOX/deployments?environment=staging&per_page=1" \
        --jq '.[0].payload.digest')
gh workflow run nt-05-shared-runner.yml --repo "$ORG/$SANDBOX" --ref nt-05-shared-runner \
  -f digest="$GOOD" -f reason="NT-05 negative test"
RUN=$(gh run list --repo "$ORG/$SANDBOX" --workflow nt-05-shared-runner.yml \
        --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN" --repo "$ORG/$SANDBOX" --exit-status || rc=$?; echo "exit=${rc:-0}"
gh run view "$RUN" --repo "$ORG/$SANDBOX" --log-failed | head -20
```

**Required output.**

```
exit=1
assert-runner-tier  FAILURE
  RUNNER_ENVIRONMENT = self-hosted
  runner labels      = self-hosted, shared-pool
  required           = hosted runner, OR self-hosted with label 'privileged'
  ERROR: privileged workflow resolved to a shared-pool runner. Failing closed.
  §36.3 privileged-workflow isolation (P0); D87
```

The step must be the **first** step of the job — before checkout, before any secret is read. Verify:

```bash
gh run view "$RUN" --repo "$ORG/$SANDBOX" --json jobs \
  --jq '.jobs[0].steps[] | {number, name, conclusion}' | head -5
# required: step 1 is assert-runner-tier with conclusion "failure";
# no step named "checkout", "login", or any step consuming an environment secret ran
```

**Command — part B: the three reconciliation Blocking rows.** §53.1 carries three for this posture. Exercise each.

```bash
python3 reconciler/run.py --check runner-posture --explain
```

**Required output B.**

```
runner-posture: 3 rules evaluated
  [1] self-hosted runner in group 'privileged' registered non-ephemerally ... 1 FINDING  (Blocking)
      runner 'privileged-02' registered without --ephemeral
  [2] privileged workflow resolving to a shared-pool label ................ 1 FINDING  (Blocking)
      <sandbox>/.github/workflows/nt-05-shared-runner.yml -> [self-hosted, shared-pool]
  [3] branch-push-triggered workflow admitted to group 'privileged' ....... 0 findings
runner-posture: BLOCKING drift open — deployment blocked on 1 repository (§53.2 Level 4)
```

**Verdict.** PASS requires: the workflow failed closed at step 1, no secret was read, and rules [1] and [2] each produced a finding. A `runner-posture: 3 rules evaluated, 0 findings` while the fixture is in place is **FAIL** — the drift rows are inert.

**Teardown.** Delete the fixture workflow from `.github/workflows/` and close the branch. Leave the copy in `tools/evidence/negative/NT-05/` — it is the test asset.

---

### NT-06 — A reconciliation run finding nothing must fail

**Gate.** **AT-102**, the seeded reconciliation canary: "Every reconciliation run must find the deliberately seeded canary drift. A run reporting zero findings — the canary included — is a **failed** run, raises SIG-13 (failed reconciliations), and triggers the gap procedure; a reconciler that finds nothing is assumed broken, never assumed clean." §53.1 states the rule and adds the second half: "Every run additionally records its per-registry comparison counts — how many rows of each registry it actually compared — so that a silently narrowed comparison is itself visible drift." **EC-109** names the failure mode: a silently-vacuous run — a broken query, an empty product enumeration.

**Why it is the single most important test in the set.** The reconciler is the instrument that checks every other control. Every gate in this catalogue is re-verified continuously by it and by nothing else. A reconciler that reports clean because it stopped looking makes the entire estate report healthy while every wall is down. This test is the only thing between that state and a green dashboard.

**Setup — the canary must exist, permanently, and be labelled.**

```bash
cat validators/drift/negative/NT-06/canary.yaml
```

```yaml
# validators/drift/negative/NT-06/canary.yaml
# PERMANENT SEEDED DRIFT — §53.1 seeded-canary rule, AT-102.
# This mismatch is deliberate, is clearly labelled, and is NEVER repaired.
# Auto-repair MUST skip it (§53.3); Level 3 must not touch it.
canary_id: CANARY-001
comparison_row: "product.yaml assignments vs GitHub Team membership"
seeded_mismatch:
  declared: "person nt-canary-001 holds cross_reviewer on product canary-sentinel"
  actual:   "person nt-canary-001 is not a member of team canary-sentinel"
expected_finding_class: alert          # never Blocking — the canary must not block the estate
must_be_reported_by: every reconciliation run
on_absence_from_run_output: FAILED RUN, raise SIG-13, trigger the §53.7 gap procedure
```

**Command — part A: the normal run must find it.**

```bash
set -euo pipefail
python3 reconciler/run.py --once --format json | tee nt-06-run.json
jq -r '.findings[] | select(.canary_id=="CANARY-001") | .canary_id' nt-06-run.json
jq -r '.run.status, .run.finding_count, .run.comparison_counts' nt-06-run.json
```

**Required output A.**

```
CANARY-001
"completed"
7
{
  "people.yaml": 14,
  "product.yaml/assignments": 41,
  "CODEOWNERS": 9,
  "branch-protection": 9,
  "environments": 27,
  "workflow-template-versions": 9,
  "exceptions.yaml": 6,
  "restore-tests": 9
}
```

**Command — part B: the negative test proper. Blind the reconciler and assert it fails.**

```bash
set -euo pipefail
# Run against a sandbox comparison set with the canary row removed —
# this simulates the vacuous run of EC-109 without touching the live canary.
python3 reconciler/run.py --once --comparison-set validators/drift/negative/NT-06/blinded/ \
  --format json | tee nt-06-blind.json || rc=$?; echo "exit=${rc:-0}"
jq -r '.run.status, .run.failure_reason, .run.signal' nt-06-blind.json
```

**Required output B.**

```
exit=2
"FAILED"
"canary CANARY-001 was not reported by this run; a run that finds nothing is assumed broken, not clean (AT-102, §53.1)"
"SIG-13"
```

**Command — part C: a silently narrowed comparison must also fail.** This is the half most implementations miss. The canary catches an instrument that stopped looking *entirely*; the comparison counts catch one that stopped looking *at most things*.

```bash
set -euo pipefail
python3 reconciler/run.py --once --comparison-set validators/drift/negative/NT-06/narrowed/ \
  --format json | tee nt-06-narrow.json || rc=$?; echo "exit=${rc:-0}"
jq -r '.run.status, .run.failure_reason' nt-06-narrow.json
```

**Required output C.**

```
exit=2
"FAILED"
"comparison count regression: product.yaml/assignments compared 3 rows, expected >= 41 (last 5 runs: 41,41,41,41,41). A narrowed comparison is drift (§53.1)."
```

Note that run C **does** report the canary — it is still in the set — and still fails. That is the point: finding the canary is necessary and not sufficient.

**Command — part D: the gap procedure must actually fire.**

```bash
gh api "/repos/$ORG/$CPR/contents/records/incidents" --jq '.[].name' | tail -1
gh api "/repos/$ORG/$CP/issues?labels=SIG-13&state=open" --jq '.[] | {number, title}'
```

**Required output D.**

```
2026-09-14-control-plane-sig13-001.yaml
{"number":118,"title":"SIG-13 failed reconciliation — vacuous run detected, §53.7 gap procedure open"}
```

**Verdict.** PASS requires all four parts. Specifically: exit 2 on B **and** C, SIG-13 raised, and a gap-procedure record written. A reconciler that returns exit 0 on B is the most dangerous single defect this build can ship: **FAIL — STOP THE MERGE TRAIN.**

`NT-06 PASS :: seeded-canary :: normal run reports CANARY-001; blinded run FAILED exit 2 SIG-13; narrowed run FAILED on comparison-count regression`

**Auto-repair must not eat the canary.** §53.3 restricts Level 3 to "safe, idempotent, reversible repairs". Assert the canary survives a repair cycle:

```bash
python3 reconciler/run.py --once --auto-repair
python3 reconciler/run.py --once --format json | jq -r '.findings[] | select(.canary_id=="CANARY-001") | .canary_id'
# required: CANARY-001 — still present after auto-repair
```

A reconciler that repairs its own canary reports clean forever from the second run onward. That is a vacuous instrument with extra steps.

---

### NT-07 — A capability granted without a definition must fail CI

**Gate.** §9.1: "**Every capability is defined before it is granted.** The table above is the complete capability vocabulary. A capability appearing in a `roles.yaml` default, in a `people.yaml` grant, or in any assignment type without a row in this table fails control-plane CI validation. This closes the fail-open path the safe-defaults rule of Section 64.1 exists to remove: an undefined capability is a grant with no defined authority, and **the resolution for an undefined value is denial, never permission**."

**Why it is load-bearing.** Authority checks read capability (§9.1, and invariant 11: "Authority is evaluated against capability and assignment, never against role name alone"). A misspelled capability — `production_approval` for `production-approval`, `securityreview` for `security-review` — creates a grant that resolves to nothing, or, in a permissive resolver, to everything. Invariant 79: new people, products and tools default to minimum privilege.

**Setup.** Three fixtures, one per injection point named in §9.1.

```bash
ls validators/registry/negative/NT-07/
```

```
people-undefined-grant.yaml      # a person granted 'deploy-everything'
roles-undefined-default.yaml     # a role default listing 'prod_approval'
assignment-undefined-type.yaml   # an assignment type conferring 'release-manager'
```

```yaml
# validators/registry/negative/NT-07/people-undefined-grant.yaml
people:
  - id: nt-07-subject
    github_login: nt-07-subject
    access_status: active
    capabilities:
      - code-review          # defined, §9
      - deploy-everything    # NOT in the §9 table — must be rejected
```

**Command.**

```bash
set -euo pipefail
for f in validators/registry/negative/NT-07/*.yaml; do
  rc=0; python3 validators/registry/validate-registries.py --file "$f" --strict || rc=$?
  echo "  exit=$rc <- $f"
done
```

**Required output.**

```
ERROR capability-undefined: people[nt-07-subject].capabilities[1] = 'deploy-everything'
  not present in the capability vocabulary (§9). An undefined capability is a grant with
  no defined authority; the resolution for an undefined value is denial (§9.1, §64.1).
  known vocabulary: 27 capabilities loaded from contracts/capabilities.yaml
validate-registries: 1 error, 0 warnings
  exit=1 <- validators/registry/negative/NT-07/people-undefined-grant.yaml

ERROR capability-undefined: roles[team_lead].default_capabilities[2] = 'prod_approval'
  not present in the capability vocabulary (§9). Did you mean 'production-approval'?
validate-registries: 1 error, 0 warnings
  exit=1 <- validators/registry/negative/NT-07/roles-undefined-default.yaml

ERROR capability-undefined: assignment_types[release_manager].confers[0] = 'release-manager'
  not present in the capability vocabulary (§9).
validate-registries: 1 error, 0 warnings
  exit=1 <- validators/registry/negative/NT-07/assignment-undefined-type.yaml
```

**Verdict.** PASS requires exit 1 on all three, each naming the injection point. The `known vocabulary: 27 capabilities loaded` line is the anti-vacuity assertion: a validator that loaded an empty vocabulary would reject everything, including valid grants, and would pass this test for the wrong reason. Assert it positively:

```bash
python3 validators/registry/validate-registries.py --print-vocabulary | wc -l   # required: 27
```

`NT-07 PASS :: capability-vocabulary-closed :: 3/3 undefined grants rejected exit 1; vocabulary 27 rows loaded`

---

### NT-08 — A role default carrying a dangerous capability must fail

**Gate.** §9.1, two rules, both about defaults specifically:

- "**`people-intelligence` is held by the Founder and is not delegable** (D109) … No role default other than `founder` includes it; no reconciliation, scaffolding or onboarding path grants it implicitly."
- "Founder-class capabilities (`strategy`, `budget`, `hiring`, `lifecycle-decision`, `customer-commitment`, `exceptional-approval`) may be delegated only through dated founder-delegation assignments (§10; §14) — **never through role defaults**."

Invariant 106 makes Layer B access "absolute" at the application and datasource layers. **AT-090** requires that "an attempt to create an assignment granting `people-intelligence` fails validation."

**Why it is load-bearing.** A role default is the quietest possible grant. It is written once, applies to every current and future holder of the role, is invisible on any individual person record, and is re-applied automatically by reconciliation on every role change (invariant 56). A dangerous capability in a default is a standing, silent, self-propagating grant — the exact shape D109 removed when it deleted the routine `people_intelligence_delegate`.

**Setup.** Seven fixtures — one per founder-class capability, plus `people-intelligence`.

```bash
ls validators/registry/negative/NT-08/
```

```
roles-tl-people-intelligence.yaml
roles-tl-exceptional-approval.yaml
roles-tl-strategy.yaml
roles-tl-budget.yaml
roles-tl-hiring.yaml
roles-tl-lifecycle-decision.yaml
roles-tl-customer-commitment.yaml
```

```yaml
# validators/registry/negative/NT-08/roles-tl-people-intelligence.yaml
roles:
  - id: team_lead
    default_capabilities:
      - code-review
      - architecture
      - reviewer-matrix-change
      - people-intelligence      # D109: not delegable, and never a role default. MUST FAIL.
```

**Command.**

```bash
set -euo pipefail
for f in validators/registry/negative/NT-08/*.yaml; do
  python3 validators/registry/validate-registries.py --file "$f" --strict >/dev/null 2>&1 \
    && { echo "NT-08 FAIL :: accepted $f"; exit 1; } \
    || echo "  refused: $(basename "$f")"
done
python3 validators/registry/validate-registries.py \
  --file validators/registry/negative/NT-08/roles-tl-people-intelligence.yaml --strict
```

**Required output.**

```
  refused: roles-tl-budget.yaml
  refused: roles-tl-customer-commitment.yaml
  refused: roles-tl-exceptional-approval.yaml
  refused: roles-tl-hiring.yaml
  refused: roles-tl-lifecycle-decision.yaml
  refused: roles-tl-people-intelligence.yaml
  refused: roles-tl-strategy.yaml

ERROR founder-class-capability-in-role-default:
  roles[team_lead].default_capabilities[3] = 'people-intelligence'
  people-intelligence is Founder-held and NOT DELEGABLE (D109, §9.1, invariant 106).
  No role default other than 'founder' may include it, and no assignment type may confer it (AT-090).
  Continuity under incapacity runs through the §14.4 sealed contingency credential
  as a recorded break-glass event, never a standing grant.
validate-registries: 1 error, 0 warnings
```

**Command — part B: the positive boundary.** The rule is "no role default *other than* `founder`". Assert the founder role still resolves, or the validator is simply banning the string:

```bash
python3 validators/registry/validate-registries.py --file registries/roles.yaml --strict \
  --explain-capability people-intelligence
```

**Required output B.**

```
people-intelligence: granted by 1 role default: founder
  holders resolving today: 1  (founder)
  delegable: false (D109)
  assignment types conferring it: 0 (AT-090)
validate-registries: 0 errors, 0 warnings
```

**Verdict.** PASS requires 7/7 refusals **and** the founder default resolving cleanly. A validator that refuses all eight has banned the capability rather than gated it, and Layer B then has no legitimate holder: **FAIL**.

`NT-08 PASS :: role-defaults-carry-no-founder-class-authority :: 7/7 refused; founder default resolves, 1 holder, delegable false`

---

### NT-09 — A record carrying a display name must fail validation

**Gate.** §91.8, stated as the one part of the erasure commitment that genuinely holds: "**names are forbidden in record bodies at schema-validation time** — a record carrying a display name where a person ID belongs fails control-plane CI, because the de-identification of the record stores is the one part of this that genuinely does hold." D88 records the honesty: purging a `display_name` from a tracked file is a commit, the prior value stays in git history, and history is not rewritten because rewriting it would destroy the evidence chain (invariant 47, §63.1). §97.2 requires every record to carry `record_schema_version`, `id`, `product`, `timestamp` and to never edit in place.

**Why it is load-bearing.** Every other privacy control in this system degrades gracefully. This one does not: a name written into an append-only store cannot be removed without an authorised history-rewrite exception, and §96.6 S19 states there is "no rotation-equivalent remedy" once customer or personal data lands in git. Schema validation is the *only* moment this is preventable. After merge it is permanent.

**Setup.** Fixtures spanning the stores most likely to attract a name — incidents, support, decisions, deletion requests, negative-test records themselves.

```bash
ls tools/records/negative/NT-09/
```

```
incident-with-display-name.yaml
support-with-customer-name.yaml
decision-with-display-name.yaml
deletion-request-with-name.yaml
negative-test-with-display-name.yaml
```

```yaml
# tools/records/negative/NT-09/incident-with-display-name.yaml
record_schema_version: 1
id: INC-2026-09-14-099
product: canary-sentinel
timestamp: 2026-09-14T11:02:00+00:00
severity: SEV-2
primary_responder: "Example Developer A"     # display name where a person ID belongs — MUST FAIL
detected_by: monitoring
```

**Command.**

```bash
set -euo pipefail
for f in tools/records/negative/NT-09/*.yaml; do
  rc=0; python3 tools/records/validate-record.py --file "$f" --schema-dir schemas/records/ --strict || rc=$?
  echo "  exit=$rc <- $(basename "$f")"
done
```

**Required output.**

```
ERROR person-name-in-record-body: incidents[INC-2026-09-14-099].primary_responder
  value "Example Developer A" matches a display_name in people.yaml (person id: dev-a).
  Records carry stable person IDs, never names (§91.8, D88, §97.2).
  Expected: primary_responder: dev-a
  Rationale: git history is append-only (invariant 47) and is not rewritten (§63.1);
  a name merged here is permanent. This is the only point at which it is preventable.
validate-record: 1 error
  exit=1 <- incident-with-display-name.yaml

ERROR customer-name-in-record-body: support[SUP-2026-09-14-014].reporter
  free-text personal name detected where a customer identifier belongs.
  Support records reference customer data by identifier, never by copy (invariant 111, §22.2).
validate-record: 1 error
  exit=1 <- support-with-customer-name.yaml

... (3 more, all exit=1)
```

**Command — part B: the detector must be a matcher, not a denylist of five strings.** Assert coverage:

```bash
python3 tools/records/validate-record.py --self-test --schema-dir schemas/records/
```

**Required output B.**

```
person-name detector self-test:
  people.yaml display_names loaded ............. 14
  record schemas scanned ....................... 21
  person-ID-typed fields identified ............ 38
  fields checked against the name matcher ...... 38/38
  synthetic name injections detected ........... 38/38
  synthetic person-ID controls falsely flagged .. 0/38
validate-record: self-test PASS
```

**Verdict.** PASS requires 5/5 fixture rejections and a clean self-test with `38/38` detected and `0/38` false positives. `fields checked ... 3/38` is a narrowed detector reporting clean — the §53.1 comparison-count failure mode, in a different instrument.

`NT-09 PASS :: records-de-identified :: 5/5 named records refused; detector self-test 38/38 fields, 0 false positives`

---

### NT-10 — A commit on a bypass branch by a foreign identity must be flagged

**Gate.** Two rules, one in the pipeline and one in the reconciler.

§33.2, the Renovate disposition policy: the bypass is "**split across two rulesets**". Ruleset A carries the pull-request rules and lists Renovate as a bypass actor. Ruleset B carries the compensating `renovate-path-guard` required status check and lists **no bypass actor at all** — "because a bypass actor is exempt from every rule in the ruleset it is listed on (D89), so a compensator sitting inside the bypassed ruleset compensates for nothing." The guard fails any Renovate pull request where either is true: the diff touches a file outside the declared manifest and lockfile paths, or "**any commit on the branch was authored or committed by an identity other than the Renovate app**". The spec then says why the authorship half is not optional: "Renovate's branches are not protected branches and every Write holder can push to them, so without it a single commit editing only the lockfile — an in-scope path, and an install-time execution vector — merges to the default branch with no human review at all."

§53.1: "A commit authored or committed by any identity other than the declared bypass actor, on a branch that merges under that actor's bypass, is Blocking-class drift for the same reason: a bypass is a grant to one identity, and a branch merging under it must carry that identity's work only."

**Why it is load-bearing.** This is the estate's one sanctioned hole in required human review. Everything else in this catalogue defends a wall; this defends the one authorised door. And it is a *path* bypass in a system where GitHub does not scope bypass by path — the exact reasoning that forced D89 to move the record stores into their own repository.

**Setup — assert the two-ruleset split first.** If the compensator sits in the bypassed ruleset, the rest of this test is theatre.

```bash
set -euo pipefail
gh api "/repos/$ORG/$SANDBOX/rulesets" --jq '.[] | {id, name}'
A=$(gh api "/repos/$ORG/$SANDBOX/rulesets" --jq '.[] | select(.name=="pr-rules") | .id')
B=$(gh api "/repos/$ORG/$SANDBOX/rulesets" --jq '.[] | select(.name=="renovate-path-guard") | .id')
gh api "/repos/$ORG/$SANDBOX/rulesets/$A" --jq '{name, bypass: [.bypass_actors[].actor_id]}'
gh api "/repos/$ORG/$SANDBOX/rulesets/$B" --jq '{name, bypass: [.bypass_actors[].actor_id],
                                                  checks: [.rules[] | select(.type=="required_status_checks")
                                                           | .parameters.required_status_checks[].context]}'
```

**Required setup output.**

```
{"id":41,"name":"pr-rules"}
{"id":42,"name":"renovate-path-guard"}
{"name":"pr-rules","bypass":[<renovate-app-id>]}
{"name":"renovate-path-guard","bypass":[],"checks":["renovate-path-guard"]}
```

`"bypass":[]` on ruleset B is non-negotiable. A non-empty list there is **FAIL — GATE OPEN**, D89 violated, and the merge train stops.

**Command — part A: foreign commit on a bypass branch, in-scope path only.** This is the attack the spec names: a lockfile-only edit, which passes the path half of the guard.

```bash
set -euo pipefail
git switch -c renovate/nt-10-foreign-commit origin/main
# an IN-SCOPE path — the path half of the guard will not catch this
printf '\n# nt-10 %s\n' "$(date -u +%FT%TZ)" >> package-lock.json
git add package-lock.json
git -c user.name="$NT_AUTHOR" -c user.email="$NT_AUTHOR@users.noreply.github.com" \
    commit -m "NT-10 foreign commit on bypass branch"
git push -u origin renovate/nt-10-foreign-commit
PR10=$(GH_TOKEN="$GH_TOKEN_AUTHOR" gh pr create --repo "$ORG/$SANDBOX" \
        --base main --head renovate/nt-10-foreign-commit \
        --title "NT-10 foreign commit on bypass branch" --body "negative test" \
        | grep -oE '[0-9]+$')
sleep 30
gh pr checks "$PR10" --repo "$ORG/$SANDBOX" || true
gh run view --repo "$ORG/$SANDBOX" \
  "$(gh run list --repo "$ORG/$SANDBOX" --workflow renovate-path-guard.yml --limit 1 \
      --json databaseId --jq '.[0].databaseId')" --log-failed
```

**Required output A.**

```
renovate-path-guard    fail    12s

assert-branch-authorship  FAILURE
  branch            : renovate/nt-10-foreign-commit
  declared bypass actor : renovate[bot] (app id <renovate-app-id>)
  commits on branch : 1
  foreign commits   : 1
    e3a91c2  author=<NT_AUTHOR>  committer=<NT_AUTHOR>  files=[package-lock.json]
  ERROR: a bypass is a grant to one identity; a branch merging under it must carry
  that identity's work only (§53.1, §33.2).
  NOTE: every path in this diff is IN SCOPE. The path check alone would have passed.
        A lockfile edit is an install-time execution vector (§33.2).
```

**Command — part B: the merge must be refused.**

```bash
GH_TOKEN="$GH_TOKEN_AUTHOR" gh api -X PUT \
  "/repos/$ORG/$SANDBOX/pulls/$PR10/merge" -f merge_method=squash 2>&1
```

**Required output B.**

```
gh: Method Not Allowed (HTTP 405)
{"message":"Required status check \"renovate-path-guard\" is failing.",...}
```

**Command — part C: the reconciler must raise Blocking drift independently.** The guard is a status check; the drift row is the second detector, and it must fire even if the check were removed.

```bash
python3 reconciler/run.py --check bypass-branch-authorship --format json | jq -r '.findings[]'
```

**Required output C.**

```json
{
  "class": "Blocking",
  "rule": "bypass-branch-foreign-authorship",
  "repository": "<sandbox>",
  "branch": "renovate/nt-10-foreign-commit",
  "bypass_actor": "renovate[bot]",
  "foreign_identities": ["<NT_AUTHOR>"],
  "commits": ["e3a91c2"],
  "anchor": "§53.1; §33.2; D89",
  "effect": "control-plane/blocking-drift check held at failure on <sandbox>"
}
```

**Command — part D: the out-of-scope path half, for completeness.**

```bash
set -euo pipefail
git switch -c renovate/nt-10-foreign-path origin/main
printf 'nt-10\n' > src/nt-10.txt          # OUT of the declared manifest/lockfile paths
git add src/nt-10.txt && git commit -m "NT-10 out-of-scope path" && git push -u origin HEAD
# required: renovate-path-guard fails on assert-diff-paths, naming src/nt-10.txt
```

**Verdict.** PASS requires: ruleset B with an empty bypass list, the guard failing on **authorship** for an in-scope-only diff, the merge refused 405, a Blocking drift finding from the reconciler, and the path half failing on D. Anything less and the one authorised door in the estate is unlatched.

`NT-10 PASS :: bypass-branch-single-identity :: ruleset B bypass=[]; guard failed on authorship with in-scope diff; merge 405; Blocking drift raised`

---

## 5. The remaining catalogue

Same contract: setup, command, refusal evidence. Condensed because the mechanism is the same shape.

### NT-11 — A skipped required check must not count as satisfied
**Anchor:** §33.2 — "A job skipped by an `if:` condition reports a `skipped` conclusion that branch protection counts as satisfied … **Every required check name is therefore emitted by a job carrying no `if:` and no path filter** … A `skipped` or `neutral` conclusion on a required context of a merged pull request is Blocking drift."
```bash
set -euo pipefail
# fixture: a copy of ci.yml whose security-scan job carries `if: false`
cp tools/evidence/negative/NT-11/ci-skipped-check.yml .github/workflows/
git checkout -b nt-11
git add .github/workflows/ci-skipped-check.yml
git commit -m "NT-11" && git push -u origin nt-11
PR11=$(gh pr create --repo "$ORG/$SANDBOX" --base main --head nt-11 --title NT-11 --body negative \
        | grep -oE '[0-9]+$')
gh pr checks --repo "$ORG/$SANDBOX" "$PR11"
python3 reconciler/run.py --check required-check-conclusions --format json | jq -r '.findings[].class'
```
**Refusal evidence:**
```
security-scan   skipped   0s
assert-no-conditional-required-checks  FAILURE
  required context 'security-scan' was emitted by a job carrying `if: false`
  a skipped conclusion is not a result (§33.2). Refusing.
Blocking
```
Also assert the static half in CI: `python3 tools/evidence/assert_required_checks_unconditional.py --repo "$ORG/$SANDBOX"` must report `required contexts: 8; emitted by unconditional jobs: 8/8`.

`NT-11 PASS :: required-checks-are-real :: security-scan skipped conclusion flagged FAILURE by assert-no-conditional-required-checks; reconciler raised Blocking; static check 8/8 unconditional`

### NT-12 — A moved `workflows/*` tag must be blocked
**Anchor:** §33.2 — the control-plane repository carries "a **tag ruleset blocking updates and deletions on `workflows/*` with an empty bypass-actor list**". Moving a tag "is the one way to execute new code in every product's pipeline with no pull request, no change manifest, no canary set and no diff in any product repository — it defeats the blast-radius apparatus of Section 33.3 and invariant 72 in a single command". §53.1 puts each consumed tag's resolved SHA in the comparison set, **Blocking on any change**.
```bash
set -euo pipefail
git -C "$CP" tag -f workflows/v3 HEAD && git -C "$CP" push --force origin workflows/v3 2>&1
gh api "/repos/$ORG/$CP/rulesets" --jq '.[] | select(.target=="tag") | {name, bypass:[.bypass_actors[]]}'
python3 reconciler/run.py --check workflow-tag-sha --format json | jq -r '.findings[]'
```
**Refusal evidence:**
```
remote: error: GH013: Repository rule violations found for refs/tags/workflows/v3.
remote:   - Cannot update tag: tag ruleset "workflows-immutable"
! [remote rejected] workflows/v3 -> workflows/v3 (push declined due to repository rule violations)
{"name":"workflows-immutable","bypass":[]}
{"class":"Blocking","rule":"workflow-tag-sha-moved","tag":"workflows/v3",
 "declared":"a1b2c3d","actual":"e4f5g6h","anchor":"§53.1; invariant 72; invariant 85"}
```

`NT-12 PASS :: workflow-tags-immutable :: tag move rejected GH013 (workflows-immutable, bypass=[]); reconciler raised Blocking on SHA drift`

### NT-13 — A verification contract whose seeded defect passes is a failed run
**Anchor:** §31.2 — "A verification contract that cannot fail is not a contract." Every `contract.yaml` declares a seeded-defect case the contract MUST fail. "A run in which the seeded defect passes is a **FAILED run**, not a clean one." Raises SIG-18, Blocking for that product. §103.1 requires "every contract's seeded-defect case failing" as the coverage target.
```bash
set -euo pipefail
python3 tools/evidence/run-verification-contract.py --product "$SANDBOX" --format json | \
  jq -r '.run.status, .seeded_defect.case_id, .seeded_defect.result'
# then the negative: neuter the contract to `verify: exit 0` in the fixture tree
python3 tools/evidence/run-verification-contract.py \
  --contract tools/evidence/negative/NT-13/contract-exit-zero.yaml --format json | \
  jq -r '.run.status, .run.failure_reason, .run.signal'; echo "exit=$?"
```
**Refusal evidence:**
```
"completed"   "SD-001"   "failed-as-required"

"FAILED"
"seeded-defect case SD-001 PASSED; the contract has stopped discriminating (§31.2)"
"SIG-18"
exit=2
```
This is the same instrument-health rule as NT-06, applied to the thing Gate 2, the §32 evidence chain and Level 2 maturity all read.

`NT-13 PASS :: verification-contract-discriminates :: normal run's seeded defect SD-001 failed-as-required; neutered contract reported FAILED exit 2, SIG-18`

### NT-14 — A machine identity must not change a workflow file
**Anchor:** invariant 18; §33.2 — "A workflow-file change pushed by a machine identity is Blocking drift"; §53.1 — "regardless of the change's content: workflow files define the enforcement path itself, and no machine credential is authorised to alter it"; §53.2 Level 4. §37.3 adds: "Removing an actor gate is a workflow-file change and is therefore already Blocking drift."
```bash
set -euo pipefail
SHA=$(gh api "/repos/$ORG/$SANDBOX/contents/.github/workflows/ci.yml" --jq .sha)
GH_TOKEN="$GH_TOKEN_MACHINE" gh api -X PUT \
  "/repos/$ORG/$SANDBOX/contents/.github/workflows/ci.yml" \
  -f message="NT-14" -f content="$(base64 -w0 < .github/workflows/ci.yml)" \
  -f sha="$SHA" -f branch=nt-14 2>&1
python3 reconciler/run.py --check machine-workflow-write --format json | jq -r '.findings[].class'
```
**Refusal evidence:** the push may succeed (the machine holds Write on whitelisted repositories — §37.3 is explicit about that) and the drift row is what closes it:
```
{"class":"Blocking","rule":"workflow-file-changed-by-machine-identity",
 "actor":"<NT_MACHINE>","file":".github/workflows/ci.yml","content_reviewed":"not-applicable",
 "effect":"nothing else merges on <sandbox> until investigated (§33.2)"}
```
PASS requires the Blocking finding **and** the `control-plane/blocking-drift` required check held at failure. A merge that proceeds is FAIL.

`NT-14 PASS :: machine-cannot-touch-enforcement :: machine push to ci.yml succeeded but reconciler raised Blocking workflow-file-changed-by-machine-identity; blocking-drift check held`

### NT-15 — The machine account must not dispatch a privileged workflow
**Anchor:** §37.3 — "On GitHub, pushing a branch and triggering a `workflow_dispatch` are the same permission, and D71 positively authorises the machine layer to dispatch — so Write alone would let the machine account run `migrate.yml`, `deploy-production.yml` and the rollback workflow." The closure is "an **actor gate as the first step of every privileged workflow**", failing closed unless `github.actor` resolves to a human in `people.yaml` holding the required capability. The machine's permitted dispatch set is "a **positive allowlist checked inside each workflow**": the §94.7 digest generators and nothing else.
```bash
set -euo pipefail
for wf in deploy-production.yml deploy-staging.yml migrate.yml rollback.yml restore-production.yml; do
  GH_TOKEN="$GH_TOKEN_MACHINE" gh workflow run "$wf" --repo "$ORG/$SANDBOX" --ref main \
    -f reason="NT-15" 2>&1 | tail -1
  RUN=$(gh run list --repo "$ORG/$SANDBOX" --workflow "$wf" --limit 1 --json databaseId --jq '.[0].databaseId')
  gh run view "$RUN" --repo "$ORG/$SANDBOX" --json conclusion --jq "\"$wf: \" + .conclusion"
done
```
**Refusal evidence (each of the five):**
```
assert-human-actor  FAILURE
  github.actor = <NT_MACHINE>
  resolves in people.yaml : NO
  required capability     : production-approval | incident-response | devops
  permitted machine dispatch allowlist : [digest-generator-*]  (§94.7)
  ERROR: privileged workflow dispatched by a non-human identity. Failing closed. (§37.3, invariant 18)
deploy-production.yml: failure
```
All five must fail at step 1, before checkout.

`NT-15 PASS :: actor-gate-on-privileged-dispatch :: 5/5 privileged workflows failed closed at assert-human-actor before checkout`

### NT-16 — The reconciler credential must be provably bounded
**Anchor:** **AT-110** verbatim: "From the reconciler's own credential, six attempts are made — a write to a GitHub Actions secret, a write to an environment, a workflow-file change, an organisation-settings change, a `records/**` write, and any Layer B access — and all six fail; the credential then still completes a normal reconciliation run. Executed for real at the phase that builds the reconciler and re-executed at every rotation … The system's most privileged identity (§99.6, risk 6) is the one whose boundary must be executed rather than asserted."
```bash
python3 validators/drift/negative/NT-16/reconciler_boundary.py --token-env GH_TOKEN_RECONCILER
```
**Refusal evidence:**
```
AT-110 reconciler credential boundary — 6 attempts
  [1] PUT /repos/<org>/<sandbox>/actions/secrets/NT16 .......... 403 Forbidden   REFUSED
  [2] PUT /repos/<org>/<sandbox>/environments/production ....... 403 Forbidden   REFUSED
  [3] PUT .github/workflows/ci.yml ............................. 403 Forbidden   REFUSED
  [4] PATCH /orgs/<org> ........................................ 403 Forbidden   REFUSED
  [5] PUT <records-repo>/records/incidents/nt-16.yaml .......... 404 Not Found   REFUSED (out of installation scope, D89)
  [6] Layer B datasource query ................................. connection refused at egress   REFUSED
  6/6 refused.
  positive control: full reconciliation run under the same credential ... completed, 7 findings, canary CANARY-001 present
AT-110 PASS
```

The positive control is required by AT-110's own wording ("the credential then still completes a normal reconciliation run") and by §1: six refusals from a revoked token would look identical.

`NT-16 PASS :: reconciler-credential-bounded :: 6/6 privileged attempts refused; positive control completed 7 findings, canary present`

### NT-17 — Reconciliation must not auto-loosen
**Anchor:** **AT-033** — "Reconciliation presented with a stricter-than-declared production control raises it for human review and does not relax it." Invariant 81 — "Auto-repair may only move the system toward the declared, stricter state." §53.3.
```bash
set -euo pipefail
# tighten actual state above declared: require 2 approvals where the template declares 1
gh api -X PUT "/repos/$ORG/$SANDBOX/branches/main/protection" \
  --input validators/drift/negative/NT-17/stricter-than-declared.json
python3 reconciler/run.py --once --auto-repair --format json | jq -r '.repairs[], .findings[]'
gh api "/repos/$ORG/$SANDBOX/branches/main/protection" \
  --jq .required_pull_request_reviews.required_approving_review_count
```
**Refusal evidence:**
```
{"class":"Alert","rule":"stricter-than-declared","repository":"<sandbox>",
 "declared":1,"actual":2,"action":"raised for human review; NOT repaired",
 "anchor":"AT-033; invariant 81; §53.3"}
2
```
The final `2` is the assertion: the stricter control survived the repair cycle. A `1` means the reconciler loosened production and is **FAIL**.

`NT-17 PASS :: no-auto-loosening :: stricter-than-declared raised Alert for human review; required_approving_review_count still 2 after auto-repair`

### NT-18 — An exception without an expiry must fail CI
**Anchor:** invariant 77 — "Every exception has an expiry; an exception without one is invalid and fails CI. An exception re-opened for the same scope after closure counts as a renewal — a fresh ID does not reset the count." **AT-036**, **AT-037**, **AT-038**, **AT-039**.
```bash
set -euo pipefail
python3 validators/registry/validate-registries.py \
  --file validators/registry/negative/NT-18/exception-no-expiry.yaml --strict || true
python3 validators/registry/validate-registries.py \
  --file validators/registry/negative/NT-18/exception-reopened-same-scope.yaml --strict || true
python3 reconciler/run.py --check exception-expiry --as-of 2026-12-01 --format json | jq -r '.findings[]'
```
**Refusal evidence:**
```
ERROR exception-no-expiry: exceptions[EXC-2026-014] has no `expires` field (invariant 77). exit=1
ERROR exception-renewal-not-counted: exceptions[EXC-2026-015] scope matches closed EXC-2026-009;
  renewal_count must be 2, found 0. A fresh ID does not reset it (invariant 77, AT-038). exit=1
{"class":"Blocking","rule":"exception-expired-unrevoked","id":"EXC-2026-011",
 "expired":"2026-11-14","anchor":"AT-037: appears on the Founder view"}
```

`NT-18 PASS :: exceptions-expire :: missing-expiry and unreset-renewal fixtures both exit=1; reconciler raised Blocking on expired unrevoked exception`

### NT-19 — An environment must refuse an unapproved ref
**Anchor:** §33.4 — "Every environment carries a deployment branch and tag policy … `staging` and `production` accept deployments from the default branch and from protected release tags only, and from no other ref. This is the control that makes §40.3's *accessible only to the production deployment workflow* true. Without it, any Write holder … pushes a branch carrying a workflow that declares `environment: production`, and GitHub hands that job the environment's secrets from an unreviewed ref."
```bash
set -euo pipefail
git switch -c nt-19-unapproved-ref origin/main
cp access/negative/NT-19/claims-production-env.yml .github/workflows/
git add -A && git commit -m "NT-19" && git push -u origin nt-19-unapproved-ref
gh workflow run claims-production-env.yml --repo "$ORG/$SANDBOX" --ref nt-19-unapproved-ref
RUN=$(gh run list --repo "$ORG/$SANDBOX" --workflow claims-production-env.yml \
        --limit 1 --json databaseId --jq '.[0].databaseId')
gh run view "$RUN" --repo "$ORG/$SANDBOX" --log
gh api "/repos/$ORG/$SANDBOX/environments/production" --jq .deployment_branch_policy
```
**Refusal evidence:**
```
Branch "nt-19-unapproved-ref" is not allowed to deploy to production due to environment protection rules.
The deployment was rejected or didn't satisfy other protection rules.
{"protected_branches":false,"custom_branch_policies":true}
# and the policy contents:
{"branch_policies":[{"name":"main","type":"branch"},{"name":"v*","type":"tag"}]}
```
No secret is present in the job log. A repository with branch protection and no deployment branch policy "holds production credentials behind nothing" (§11.3) — assert both, always.

`NT-19 PASS :: environment-ref-policy :: deployment from unapproved ref rejected by environment protection; no secret present in job log`

### NT-20 — The records repository must refuse a rewrite
**Anchor:** **D107** — "a ruleset with no bypass actor blocks force push and deletion while permitting fast-forward commits; commits are signed by the writing identity and an unsigned or foreign-signed commit is Blocking drift; and the reconciler anchors the records head SHA into the protected control-plane repository each run, so a head that does not descend from the last anchor is proof of rewriting at Level 5." Invariant 47; §63.1.
```bash
set -euo pipefail
# Safety contract (B-16): `reset --hard` below discards a commit from the LOCAL
# records clone before the (expected-to-be-refused) force-push attempt. Save the
# SHA first and restore the clone on every exit path — this drill must not leave
# the operator holding a clone one commit behind origin with no teardown.
RECORDS_SHA_BEFORE="$(git -C "$CPR" rev-parse HEAD)"
restore_records_clone() { git -C "$CPR" reset --hard "$RECORDS_SHA_BEFORE"; }
trap restore_records_clone EXIT

git -C "$CPR" reset --hard HEAD~1 && git -C "$CPR" push --force origin main 2>&1 || true
git -C "$CPR" push origin --delete records-archive 2>&1 || true
gh api "/repos/$ORG/$CPR/rulesets" --jq '.[] | {name, bypass:[.bypass_actors[]], rules:[.rules[].type]}'
python3 reconciler/run.py --check records-head-anchor --format json | jq -r '.findings[]'
```
**Refusal evidence:**
```
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote:   - Cannot force-push to this branch          ! [remote rejected] main -> main
remote:   - Cannot delete this branch                 ! [remote rejected] records-archive
{"name":"records-no-bypass","bypass":[],"rules":["non_fast_forward","deletion","required_signatures"]}
{"class":"Level5","rule":"records-head-does-not-descend-from-anchor",
 "last_anchor":"7d1e4aa","current_head":"c02f918","anchor":"D107; invariant 47"}
```
`"bypass":[]` is the whole control. D89 removed review protection from this repository so the writer could append without review; D107 is what stops that from meaning "anyone can rewrite history".

`NT-20 PASS :: records-repo-append-only :: force-push and branch deletion both rejected GH013 (bypass=[]); reconciler raised Level5 on non-descending head`

### NT-21 — The records-writer credential must reach nothing else
**Anchor:** D89 — records and events move to a separate repository "written by a GitHub App token scoped to that repository alone", because "a ruleset bypass actor bypasses the rule wherever the rule applies; GitHub does not scope bypass by path", so the prior design was "an unscoped write credential on the repository holding every file from which authority is resolved". §97.1; §40.1 tier 5.
```bash
set -euo pipefail
GH_TOKEN="$GH_TOKEN_RECORDS_WRITER" gh api -X PUT \
  "/repos/$ORG/$CP/contents/registries/people.yaml" -f message="NT-21" -f content="$(echo x|base64)" 2>&1
GH_TOKEN="$GH_TOKEN_RECORDS_WRITER" gh api -X POST \
  "/repos/$ORG/$SANDBOX/pulls/$PR/reviews" -f event=APPROVE 2>&1
GH_TOKEN="$GH_TOKEN_RECORDS_WRITER" gh api "/installation/repositories" --jq '.repositories[].name'
```
**Refusal evidence:**
```
gh: Not Found (HTTP 404)          <- control-plane is outside the installation
gh: Resource not accessible by integration (HTTP 403)   <- approves nothing (§97.1, D76 as amended by D89)
control-plane-records             <- installation scope: exactly one repository
```

`NT-21 PASS :: records-writer-scoped :: control-plane write 404, review approval 403; installation scope exactly control-plane-records`

### NT-22 — `people-intelligence` must not be assignable
**Anchor:** **AT-090** — "an attempt to create an assignment granting `people-intelligence` fails validation"; **AT-091**; invariant 106; D109. AT-090 also carries the warning this catalogue exists to honour: "A test that cannot pass on the architecture it governs gets reinterpreted, and a reinterpreted access-control test is how the boundary erodes."
```bash
set -euo pipefail
python3 validators/registry/validate-registries.py \
  --file validators/registry/negative/NT-22/assignment-grants-layer-b.yaml --strict
python3 validators/registry/validate-registries.py --explain-capability people-intelligence \
  --print-grant-paths
```
**Refusal evidence:**
```
ERROR capability-not-delegable: assignments[ASG-2026-031].confers = 'people-intelligence'
  not delegable (D109, invariant 106, AT-090). No assignment type may confer it.
  Continuity under Founder incapacity runs through the §14.4 sealed contingency credential.
grant paths for people-intelligence:
  role defaults ......... 1 (founder)
  person grants ......... 1 (founder)
  assignment types ...... 0
  reconciliation paths .. 0
  scaffolding paths ..... 0
  onboarding paths ...... 0
```
The zeros are the assertion (§9.1: "no reconciliation, scaffolding or onboarding path grants it implicitly"). Pair with the datasource half — **AT-097**, **AT-098**: the people datasource must be absent from the shared Grafana instance's *provisioned configuration*, "verified in the provisioned configuration, not inferred from panel visibility (D75)".

`NT-22 PASS :: layer-b-not-delegable :: assignment granting people-intelligence rejected capability-not-delegable; all non-founder grant paths 0`

### NT-23 — An authority delta with no decision record must fail CI
**Anchor:** §26.4 — "an **authority delta** — a diff that adds a capability, adds an assignment type conferring Write, or changes `access_status` — fails CI without a linked decision record ID in the same commit. Schema validation proves a registry edit is well-formed; neither it nor a single owner review proves it was intended, and where a wrong revocation is caught by orphan risk (SIG-05), **a wrong grant has no detector at all**."
```bash
set -euo pipefail
git switch -c nt-23 && git apply validators/registry/negative/NT-23/adds-capability.patch
git commit -am "add capability" && git push -u origin nt-23   # note: no decision ID in the message
PR23=$(gh pr create --repo "$ORG/$CP" --base integration --head nt-23 \
        --title "NT-23 authority delta" --body "negative test; no decision ID" \
        | grep -oE '[0-9]+$')
gh pr checks --repo "$ORG/$CP" "$PR23"
```
**Refusal evidence:**
```
authority-delta-guard   fail
  diff adds capability 'production-approval' to people[dev-b]
  linked decision record ID in commit or PR body: NONE
  ERROR: an authority delta requires a decision record ID in the same commit (§26.4).
  A wrong grant has no other detector.
```
Also assert the staging half of §26.4: a merged registry change applies to the declared canary set only, with the fleet held one reconciliation cycle.
```bash
python3 reconciler/run.py --once --format json | jq -r '.run.applied_scope'
# required: "canary-set (2 products); fleet held 1 cycle pending clean canary run"
```

`NT-23 PASS :: authority-delta-needs-decision :: capability-adding commit with no decision ID failed authority-delta-guard; applied_scope confirms canary-set staging`

### NT-24 — The plan-checker must reject
**Anchor:** §30.2 hard rejects — no automated verify command; symbols that do not exist in source; unaddressed decision; slopsquat failure; schema task with no rollback strategy; `partially-reversible`/`non-reversible` with no recovery strategy (§28.1). §103.1: "**Zero rejections means the gates are not working.**"
```bash
set -euo pipefail
for f in tools/evidence/negative/NT-24/*.plan.md; do
  python3 tools/evidence/plan-check.py --plan "$f" --format json | jq -r '.verdict, .reason'
done
python3 tools/evidence/plan-check.py --rejection-stats --window 30d
```
**Refusal evidence:**
```
"REJECT" "task 3 has no automated verify command (§30.2)"
"REJECT" "symbol `OrderService.reconcile` not found in source (§30.2)"
"REJECT" "decision D-2026-041 is unaddressed (§30.2)"
"REJECT" "package 'requessts' failed the slopsquat legitimacy check against the live registry API (§30.2)"
"REJECT" "task 5 touches database schema and states no rollback strategy (§30.2, §34.3)"
"REJECT" "change is non-reversible and states no recovery strategy (§28.1, §30.2)"
6/6 hard-reject classes exercised.
rejection stats, trailing 30d: 14 rejections across 6 reason classes
  WARNING would fire at 0: zero rejections means the gates are not working (§103.1)
```
The stats line is the doctrine made mechanical: the checker reports its own rejection rate, and a sustained zero is a signal about the checker, not a compliment to the planners.

`NT-24 PASS :: plan-checker-rejects :: 6/6 hard-reject classes exercised; trailing-30d rejection rate 14 across 6 classes, nonzero`

### NT-25 — The control verifier must not run under the credential it verifies
**Anchor:** §53.1, the independent control verifier — "Reconciliation regenerates CODEOWNERS and re-applies branch protection, and is also the only thing that checks them — an instrument that can rewrite the wall it inspects and then report the wall intact. The seeded canary catches an instrument that stopped looking; it does not catch one that reports falsely. A second verifier therefore runs **off the operations VM and under a different credential** … It writes its result to a surface the operations VM cannot write to, and its own absence for one cycle is Level 5."
```bash
python3 validators/drift/negative/NT-25/assert_verifier_independence.py
```
**Refusal evidence:**
```
independent-control-verifier independence check
  verifier host              : github-hosted runner (control-plane repo scheduled workflow)   OK
  verifier host != ops VM    : OK
  verifier credential        : fine-grained PAT 'control-verifier' (read-only)                OK
  credential != reconciler   : OK
  verifier can write reconciler's result surface : NO                                          OK
  ops VM can write verifier's result surface     : NO                                          OK
  verifier absence for 1 cycle escalates         : Level 5                                     OK
  NEGATIVE: attempt verifier run under GH_TOKEN_RECONCILER ... REFUSED
    "verifier refuses to run under the credential it verifies (§53.1)"
  verifier assertions this run:
    no machine identity in any CODEOWNERS ......... 9/9 repositories, 0 machine identities
    branch protection matches template ............ 9/9
    ruleset bypass-actor list == §40.1/§33.2 set ... 9/9 exact match
```

`NT-25 PASS :: independent-control-verifier :: verifier host/credential independent of reconciler; run under GH_TOKEN_RECONCILER REFUSED; 9/9 assertions confirmed`

### NT-26 — A restore claim with no record must be Blocking
**Anchor:** §53.1 — `product.yaml` `restore_tested` vs the newest passing record in `records/restore-tests/`: "**Blocking**: a declared date with no matching record is an unevidenced reliability claim, not a scheduling question." Invariant 3 ("An untested backup is treated as no backup"), invariant 4, **AT-035**.
```bash
python3 reconciler/run.py --check restore-evidence --format json | jq -r '.findings[]'
```
**Refusal evidence:**
```
{"class":"Blocking","rule":"restore-tested-without-record","product":"canary-sentinel",
 "declared_restore_tested":"2026-08-30","matching_record":null,
 "anchor":"§53.1; invariant 3; invariant 4",
 "effect":"deployment blocked on canary-sentinel"}
```
Also assert the currency half (B-17 — the mechanism, reusing protocol/08 CP-1106/CP-1107's own tools rather than inventing a third): a `restore_tested` date older than the rolling 90-day window fails CI (invariant 4), and the production-restore record must carry a recorded `integrity_check` result and a named verifier or it renders Red (§53.1, §44.5).
```bash
set -euo pipefail
./validators/drift/check-restore-tested --product canary-sentinel --window-days 90 --fail-on-stale
# required: non-zero exit and "STALE: restore_tested older than 90-day window" on a
# product whose declared date predates today by more than 90 days
./tools/records/find-record --store records/restore-tests --product canary-sentinel \
  --require-present integrity_check --require-present verified_by --require result=pass
# required: non-zero exit — RENDER RED — if either field is absent or result != pass
```

`NT-26 PASS :: restore-claim-needs-evidence :: declared restore_tested with no matching record raised Blocking; deployment blocked on canary-sentinel; currency check STALE on a >90-day date; missing-field record RENDER RED`

### NT-27 — A store that stops being written must be detected
**Anchor:** §97.2 — "**Write freshness is an instrument, because zero is the good value.** … Without it, a workflow whose record-write step fails silently renders every count-shaped derived metric as zero — no ready-queue misses, no anomalies, no regressions — which is indistinguishable from health, and the presentation discipline of §52.3 then gives that silence no screen space." Amber generally; **Blocking** for `events/`, `records/deployments/`, `records/uat/` (§53.1).
```bash
python3 reconciler/run.py --check write-freshness --as-of 2026-09-30 --format json | jq -r '.findings[]'
```
**Refusal evidence:**
```
{"class":"Blocking","store":"records/deployments/","declared_max_interval":"72h",
 "last_commit_on_path":"2026-09-21T04:02:11+00:00","age":"9d","anchor":"§97.2; §53.1"}
{"class":"Amber","store":"records/estimates/","declared_max_interval":"7d","age":"11d"}
```
Second assertion, from the same paragraph: the deployment-record and event writes are **required, failing steps** of `deploy-production.yml`, not trailing best-effort ones. Exercise it by making the record write fail in the fixture and requiring the deploy job to fail with it.

`NT-27 PASS :: write-freshness-detector :: records/deployments/ stale 9d raised Blocking; records/estimates/ stale 11d raised Amber`

### NT-28 — A non-ephemeral runner in the `privileged` group must be flagged
**Anchor:** §36.3 and D87 — the declared exception is a self-hosted runner registered `--ephemeral`, "a fresh container or virtual machine per job, with no writable shared volume", in a group labelled `privileged` "that never accepts a branch-push-triggered job". §53.1 carries the row.
```bash
python3 reconciler/run.py --check runner-posture --format json | jq -r '.findings[] | select(.rule|startswith("runner"))'
gh api "/orgs/$ORG/actions/runner-groups" --jq '.runner_groups[] | {name, visibility, allows_public_repositories}'
```
**Refusal evidence:**
```
{"class":"Blocking","rule":"runner-non-ephemeral-in-privileged-group","runner":"privileged-02"}
{"name":"privileged","visibility":"selected","allows_public_repositories":false}
{"name":"shared-pool","visibility":"selected","allows_public_repositories":false}
```
`allows_public_repositories: false` on every group is the D80 runner posture; assert it here rather than assuming it.

`NT-28 PASS :: ephemeral-privileged-runners :: non-ephemeral runner privileged-02 raised Blocking; both runner groups confirm allows_public_repositories=false`

### NT-29 — A fixture without declared provenance must fail CI
**Anchor:** invariant 111 — "No customer data in repositories … not in fixtures, not in support records, not in incident evidence." §38.3 — every file under `verification/ai-eval/fixtures/` carries a declared provenance (`synthetic`, `consented-and-recorded`, or `de-identified` with the method named); "a fixture with no provenance declaration, or a manifest entry with no file, fails CI." §96.6 S19 is the intake gate.
```bash
set -euo pipefail
python3 tools/evidence/assert-fixture-provenance.py --product "$SANDBOX" --strict
python3 tools/evidence/assert-fixture-provenance.py \
  --fixtures tools/evidence/negative/NT-29/ --strict; echo "exit=$?"
```
**Refusal evidence:**
```
ERROR fixture-no-provenance: verification/ai-eval/fixtures/call-03.json has no manifest entry (§38.3)
ERROR manifest-entry-no-file: manifest declares fixtures/call-09.json; file absent (§38.3)
ERROR provenance-value-invalid: fixtures/call-04.json provenance 'probably fine'
  permitted: synthetic | consented-and-recorded (consent record referenced) | de-identified (method named)
assert-fixture-provenance: 3 errors
exit=1
```
§38.3 is explicit that this is "the one prohibition with no rotation-equivalent remedy after the fact" — git history is append-only. Like NT-09, CI is the only moment.

`NT-29 PASS :: no-customer-data-in-git :: 3/3 provenance violations rejected exit 1 (missing declaration, missing file, invalid value)`

### NT-30 — A lane PR touching a foreign path must fail the lane guard
**Anchor:** PARTITION rule 1: "**One owner per path.** No path appears in two lanes. A lane PR touching a foreign path FAILS the lane-guard check. No exceptions." Rule 4: no cross-lane imports.
```bash
set -euo pipefail
git switch -c lane/2/nt-30 origin/integration
printf '# nt-30\n' >> schemas/registry/product.schema.json   # L1's path, from an L2 branch
git commit -am "NT-30 foreign path" && git push -u origin lane/2/nt-30
PR30=$(gh pr create --repo "$ORG/$CP" --base integration --head lane/2/nt-30 --title NT-30 --body negative \
        | grep -oE '[0-9]+$')
gh pr checks --repo "$ORG/$CP" "$PR30"
```
**Refusal evidence:**
```
lane-guard   fail   6s
  branch lane/2/nt-30 -> lane L2 (owns: .github/workflows/**, templates/workflows/**, tools/evidence/**)
  foreign paths in diff:
    schemas/registry/product.schema.json  -> owned by L1
  ERROR: a lane may edit only paths it owns (PARTITION rule 1). No exceptions.
  Remedy: file a Contract Change Request; do not edit another lane's tree (PARTITION rules 2, 4).
```
Also assert the CODEOWNERS half (B-17) — the foreign path must additionally require L1's review, so two independent mechanisms hold, not one:
```bash
set -euo pipefail
gh api "/repos/$ORG/$CP/contents/.github/CODEOWNERS" --jq '.content' | base64 -d \
  | grep -E '^schemas/registry/' | grep -q '@org/lane-1' \
  && echo "CODEOWNERS-CHECK: schemas/registry/** requires @org/lane-1" || exit 1
gh pr view "$PR30" --repo "$ORG/$CP" --json reviewRequests \
  --jq '.reviewRequests[].login, .reviewRequests[].name' | grep -q lane-1
# required: both commands succeed — the pattern names L1's team AND that team is a
# requested reviewer on this PR, so the foreign-path PR is blocked by two independent
# mechanisms (lane-guard AND branch-protection Code Owner review), never by lane-guard alone
```

`NT-30 PASS :: lane-guard :: foreign-path PR failed lane-guard naming schemas/registry/product.schema.json owned by L1; CODEOWNERS independently requires @org/lane-1 review on the same PR`

### NT-31 — A lane PR editing `contracts/**` must fail
**Anchor:** PARTITION rule 2: "**Contract-first.** `contracts/**` is written by L0 in Phase 0 and FROZEN. Lanes code against it and against generated stubs/fixtures. A lane needing a contract change files a Contract Change Request; it never edits `contracts/**`."
```bash
set -euo pipefail
git switch -c lane/3/nt-31 origin/integration
printf '\n' >> contracts/reconciler.contract.yaml
git commit -am "NT-31 contract edit" && git push -u origin lane/3/nt-31
PR31=$(gh pr create --repo "$ORG/$CP" --base integration --head lane/3/nt-31 --title NT-31 --body negative \
        | grep -oE '[0-9]+$')
gh pr checks --repo "$ORG/$CP" "$PR31"
```
**Refusal evidence:**
```
lane-guard   fail
  contracts/** is FROZEN and L0-owned (PARTITION rule 2)
  diff touches: contracts/reconciler.contract.yaml
  ERROR: file a Contract Change Request. A lane never edits contracts/**.
```

`NT-31 PASS :: contract-freeze :: PR touching contracts/reconciler.contract.yaml failed lane-guard as FROZEN L0-owned`

### NT-32 — The catalogue itself must be able to fail
**Anchor:** §1 of this file, and the doctrine it carries from §53.1 and §31.2. A negative test that cannot emit FAIL is exactly the instrument this catalogue exists to detect.

Every NT ships with a **mutation fixture**: a deliberately weakened copy of the gate, held beside the test, against which the NT must report FAIL. Running the catalogue in mutation mode inverts every expectation.

```bash
make negative MUTATE=1
```
**Required output.**

```
mutation mode: each NT is run against its weakened-gate fixture; FAIL is the required outcome.
  NT-01 against branch-protection-without-last-push-approval ....... FAIL as required
  NT-02 against protection-counting-read-approvals ................. FAIL as required
  NT-03 against codeowners-including-machine ....................... FAIL as required
  NT-04 against deploy-without-digest-assertion .................... FAIL as required
  NT-05 against privileged-workflow-without-runner-assertion ....... FAIL as required
  NT-06 against reconciler-with-canary-check-removed ............... FAIL as required
  NT-07 against validator-with-open-vocabulary ..................... FAIL as required
  NT-08 against validator-without-founder-class-rule ............... FAIL as required
  NT-09 against record-schema-without-name-detector ................ FAIL as required
  NT-10 against single-ruleset-bypass (D89 violation) .............. FAIL as required
  NT-11 .. NT-31 ................................................... FAIL as required (21/21)
  32/32 negative tests proven able to fail.
NT-32 PASS :: catalogue-falsifiability :: 32/32 mutation fixtures produced FAIL
```

An NT that reports PASS in mutation mode is not a test. Delete it and rewrite it, and treat the gate it claimed to cover as unverified until the replacement fails correctly.

---

## 6. Paired positive controls — required, not optional

Every negative test asserts a refusal. A refusal proves the gate held **only if the permitted action succeeds under the same conditions**. Otherwise "refused" and "everything is broken" are the same observation. §95.4 builds this into the checklist itself: at the two-humans threshold it requires all three clauses — self-approval fails, Read-only approval does not satisfy, "**and a Write-holding cross-reviewer approval does**".

| P | Permitted action that MUST succeed | Pairs with |
|---|---|---|
| P-01/02/03 | A Write-holding, human, non-author Code Owner approval satisfies protection and the PR merges | NT-01, NT-02, NT-03 |
| P-04 | Deploying the exact staging-verified digest succeeds and writes a deployment record | NT-04 |
| P-05 | The same privileged workflow on a hosted runner passes `assert-runner-tier` | NT-05 |
| P-06 | A normal reconciliation run completes, reports CANARY-001, and records its comparison counts | NT-06 |
| P-07 | A grant of a defined capability validates clean | NT-07 |
| P-08 | The `founder` role default carrying `people-intelligence` validates clean, 1 holder | NT-08 |
| P-09 | A record carrying person IDs validates clean | NT-09 |
| P-10 | A genuine Renovate-only branch passes `renovate-path-guard` and auto-merges on green | NT-10 |
| P-15 | A human holding `production-approval` dispatches `deploy-production.yml` and passes `assert-human-actor` | NT-15 |
| P-16 | The reconciler credential completes a normal run (AT-110's own requirement) | NT-16 |
| P-24 | A well-formed plan passes the plan-checker and reaches Gate 1 | NT-24 |
| P-30 | A lane PR touching only its own paths passes lane-guard | NT-30, NT-31 |

A negative test whose paired positive control also fails is recorded as **HARNESS ERROR (exit 3)**, never PASS.

---

## 7. Binding to the merge train

Merge order is fixed: **L1 → L4 → L2 → L3 → L5** (PARTITION). Each hop carries the negative tests for the gates that lane owns, plus every previously-passing test re-run — a gate can be re-opened by a later lane's change, and only re-execution detects it.

| Hop | Must be PASS before the merge | Rationale |
|---|---|---|
| L1 → integration | NT-07, NT-08, NT-18, NT-22, NT-23, NT-26, NT-30, NT-31 | Registries define the vocabulary every other gate reads |
| L4 → integration | NT-09, NT-20, NT-21, NT-27 + all L1 tests re-run | Record stores are where every gate's evidence lands |
| L2 → integration | NT-04, NT-05, NT-10, NT-11, NT-12, NT-13, NT-15, NT-24, NT-29 + all above re-run | The pipeline is the enforcement path |
| L3 → integration | NT-06, NT-14, NT-16, NT-17, NT-25 + all above re-run | The reconciler checks everything, including itself |
| L5 → integration | NT-01, NT-02, NT-03, NT-19, NT-28 + all above re-run | Access and infra are the outermost wall |
| integration → main | **All 32, plus NT-32 in mutation mode, plus every paired positive control** | §11.3, §33.2, §53.1 |

**The `integration → main` gate is not a formality.** The full catalogue plus mutation mode plus positive controls is the only point in this build where anyone sees the whole system at once. Nobody has full context; this run is the substitute for that context.

**Recording.** Every hop writes one result record per NT to `records/negative-tests/`. The merge decision cites the records, never a person's recollection — §95.4: "a closure decision references log entries, never memory."

---

## 8. Bootstrap handling

Several tests need identities that do not yet exist. §95.4 arms gates by headcount, and Section 0 of this file forbids counting an unarmed test as clean.

| Threshold | Newly armed | Newly runnable |
|---|---|---|
| 2 humans with Write | No self-approval; Gate 2 independent review; most-recent-push approval | **NT-01, NT-02, NT-03** and P-01/02/03 |
| 3 humans | Production approver ≠ deploying actor; cross-review matrix with real routing | NT-04's approver half; NT-15's P-side; NT-19 |
| QA role filled | Independent verification authority; release sign-off; UAT ownership | NT-13's ownership half; NT-27's `records/uat/` row |
| 4+ humans | Backup Owner coverage; knowledge-redundancy floor; responder rotation | orphan-detection assertions in NT-26's neighbourhood |

Below a threshold, the affected NT reports `UNARMED` — a summary-line token per §2.3, not an exit code under `00-test-strategy.md` §3's contract — and requires an `exceptions.yaml` entry of `type: bootstrap` carrying a mandatory expiry, a deactivation trigger and an activation-checklist row (§54.1, §95.2, invariant 77). SIG-39 fires on any bootstrap exception past expiry with its gate still unarmed. Every reconciler, validator and pipeline test — NT-04 through NT-14 and NT-16 through NT-32 — is runnable at headcount 1 and carries no bootstrap relief.

---

## 9. STOP rules

Stop and open a blocker issue. Do not work around, do not "fix" the test, do not merge.

| Condition | Action |
|---|---|
| Any NT reports **FAIL** | STOP the merge train at the current hop. Open a blocker labelled `gate-open`. The gate is live-open in the estate, not just in the branch. |
| NT-06 reports FAIL | STOP everything. The instrument that verifies every other gate is unreliable; every green result in this file becomes unproven. Raise SIG-13 and run the §53.7 gap procedure to establish what the vacuous window may have missed. |
| NT-32 reports any NT as PASS in mutation mode | That NT is not a test. Delete it, rewrite it, and mark its gate unverified. |
| A paired positive control fails | Record exit 3 (HARNESS ERROR). Do not record the NT as PASS. |
| An NT cannot run (missing identity, missing fixture, missing credential) | Exit 3. An unrunnable test is not a passing test. |
| A lane proposes weakening a gate to make an NT pass | Refuse. File a Contract Change Request (PARTITION rule 2). No lane has authority to relax a control. |
| An NT is UNARMED with no live `exceptions.yaml` entry | STOP. Invariant 77: an exception without an expiry is invalid and fails CI. |
| Test material must be written outside your lane's owned paths | STOP. Open a blocker. Do not edit a foreign path — that is NT-30's own failure condition. |

**Blocker issue template.**

```
Title: [gate-open] NT-<nn> FAIL — <gate name>
Body:
  NT: NT-<nn>
  Gate: <gate name>
  Spec anchors: <AT-xxx / invariant nn / §x.y / Dnn>
  Forbidden action attempted: <one line>
  What the system did instead of refusing: <verbatim output>
  Paired positive control: PASS | FAIL
  Blast radius: <which repositories / identities / environments are affected right now>
  Merge train: stopped at <hop>
  Owning lane: L<n>
```

---

## 10. Traceability

Every NT resolves to at least one numbered acceptance test or invariant. No NT is justified by this file alone.

| NT | Acceptance tests | Invariants | Sections | Decisions |
|---|---|---|---|---|
| NT-01 | AT-021 (routing) | 9, 12 | 11.3, 23.1, 27.2, 95.4 | D73 |
| NT-02 | — | 8, 9 | 11.1, 11.2, 11.3, 95.4 | — |
| NT-03 | — | 18, 87 | 11.3, 37.3, 40.1 | D53 |
| NT-04 | AT-024, AT-026 | 22, 23 | 32, 33.4, 53.2 | D78 |
| NT-05 | AT-109 | 18, 26 | 36.3, 40.3, 53.1 | D80, D87 |
| NT-06 | **AT-102**, AT-032, AT-033 | 44, 87 | 53.1, 53.2, 53.7 | — |
| NT-07 | AT-002, AT-007 | 11, 50, 79 | 9, 9.1, 64.1 | — |
| NT-08 | AT-081, **AT-090** | 106, 107 | 9.1, 10.3, 14.4, 90 | D109 |
| NT-09 | AT-105 | 47, 111 | 91.8, 97.2, 63.1 | D59, D88 |
| NT-10 | AT-024 | 44, 85 | 33.2, 53.1 | D74, D89 |
| NT-11 | AT-032 | 87 | 33.2, 53.1 | — |
| NT-12 | AT-023, AT-024, AT-027 | 71, 72, 85 | 33.2, 33.3, 61.5 | — |
| NT-13 | AT-049 | 1, 6 | 31.2, 103.1 | — |
| NT-14 | AT-032 | 18, 40 | 33.2, 37.3, 53.1 | D71 |
| NT-15 | AT-103 | 17, 18 | 37.3, 27.2, 94.7 | D69, D71 |
| NT-16 | **AT-110** | 24, 25, 26 | 40.1, 53.1, 99.6 | — |
| NT-17 | **AT-033** | 81, 44 | 53.1, 53.3, 64.1 | — |
| NT-18 | AT-036, AT-037, AT-038, AT-039 | 77 | 54.1, 54.2, 95.2 | — |
| NT-19 | AT-029 | 25, 26 | 33.4, 40.2, 40.3 | D73 |
| NT-20 | AT-035 | 47 | 63.1, 97.1 | D107 |
| NT-21 | — | 18, 40 | 40.1, 97.1 | D76, D89 |
| NT-22 | **AT-090**, AT-091, AT-092, AT-097, AT-098 | 106, 108, 109 | 9.1, 90.2, 90.5, 92.1 | D75, D109 |
| NT-23 | AT-002, AT-008 | 55, 79 | 26.4, 53.1 | — |
| NT-24 | AT-011 | 16, 28 | 28.1, 30.2, 34.3, 103.1 | — |
| NT-25 | AT-032, AT-110 | 44, 87 | 53.1, 37.3 | — |
| NT-26 | AT-035 | 3, 4 | 44.2, 44.5, 53.1 | D80 |
| NT-27 | AT-032 | 46, 49 | 52.3, 97.2, 53.1 | D77 |
| NT-28 | AT-109 | 26 | 36.3, 49.1, 53.1 | D80, D87 |
| NT-29 | AT-049, AT-105 | 111 | 38.3, 96.6, 22.2 | — |
| NT-30 | — | — | PARTITION 1, 4 | — |
| NT-31 | AT-025 | 73 | PARTITION 2; 60.2 | — |
| NT-32 | **AT-102** | 87 | 31.2, 53.1, 95.4, 103.1 | — |

---

## 11. The one-paragraph summary for a lane developer

You own some gates. For each one, write a test that does the forbidden thing and asserts the refusal, with the exact refusal text in the expected output. Write a second test that does the permitted thing and asserts it succeeds. Write a weakened copy of your gate and prove your negative test fails against it. Put all three in `<your-owned-path>/negative/NT-<nn>/`. If the negative test cannot fail, you have not tested anything. If the positive control cannot pass, you have not tested anything either. If your gate needs an identity or a path you do not own, stop and open a blocker — do not reach into another lane's tree. A gate you configured but never watched refuse something is not a gate; it is a note about a gate.
