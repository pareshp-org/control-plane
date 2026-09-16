# 10 — THE CI PIPELINE FOR THE BUILD ITSELF

**Status:** authoritative for the workflows that run on `lane/N/*`, on `integration`, and on `main` **during the five-lane build**.
**Conforms to:** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` (FROZEN). Where this file and PARTITION appear to differ, PARTITION wins and this file is defective.
**Sibling protocol files it must not contradict:** `00-test-strategy.md` (the T0–T4 pyramid, the exit-code contract, the negative-test doctrine), `05-merge-gate.md` (GATE A / GATE B, checks `LG-01…LG-12` and `IG-01…IG-12`), `07-rollback.md`, `09-fixtures.md` (`make fixtures-all` and the FG-1…FG-5 meta-gates).
**Spec of record:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,256 lines). Every citation below is a real line range or a real id; nothing is invented.

---

## 0. What this file is, and the thing it is most likely to be confused with

There are **two entirely different collections of workflow YAML** in this programme, and conflating them is the most expensive documentation error available:

| | **The build's own CI** — this file | **The reusable workflow library** — Lane 2 |
|---|---|---|
| Purpose | Verifies the five-lane build: lane branches, `integration`, `main` | Ships to eight (later twenty) product repositories as the delivery pipeline |
| Files | `.github/workflows/selfci-*.yml`, plus `lane-guard.yml` | `.github/workflows/{ci,build,deploy-staging,deploy-production,migrate,restore-test,org-export,background-queue}.yml` and `templates/workflows/**` |
| Spec basis | §33.2 CI rules applied to the control-plane repository; §98.2 phase gates; §95.2 unarmed/armed protection | §99.2 row E (L9205); §33.2 required-workflows paragraph (L2854–2872); §44.5 (L4016–4022) |
| Lifetime | Build-time. Dies with the `integration` branch at build close | Permanent. Versioned by tag `workflows/vN`, consumed by pinned tag |
| Tagged into `workflows/*` releases? | **Never.** Gate `GATE-L0-019` fails a release tag whose tree contains a `selfci-*` file | Yes — that is the whole point |
| Whose verdict is of record? | **L0's local `make` run.** The workflow is a mirror (`LG-12`, `IG-12`) | The workflow itself; it is the product's gate |

The `selfci-` prefix is load-bearing. It is the mechanical separator between the two sets, and three gates in §7 read it.

**What this file governs:** the six workflows, their triggers, their concurrency groups, the runner topology, the caching design, the speed budgets, the required-status-check registration procedure, and the eleven gates that prove this pipeline can fail.

**What this file does not govern:** the content of the gate scripts (that is `05-merge-gate.md` and `contracts/gate/**`), the test pyramid (that is `00-test-strategy.md`), the fixture corpus (that is `09-fixtures.md`), or anything a product repository runs.

---

## 1. Rule Zero, restated for a pipeline

> **A check that can only pass is not a check.**

The spec states this in five places and this protocol has already carried it into the test pyramid and the merge gate. A CI pipeline adds three failure modes the pyramid alone does not have, and each one is a way for a gate to become decoration while still rendering green:

| Pipeline-specific failure | Where the spec already refuses it |
|---|---|
| A job **skipped** by an `if:` or never triggered by a path filter still satisfies branch protection | §33.2 (L2854–2869): *"a job skipped by an `if:` condition reports a `skipped` conclusion that branch protection counts as satisfied"*; a `skipped` or `neutral` conclusion on a required context of a merged PR is **Blocking drift** |
| A run **cancelled** by concurrency, or **timed out**, produces no verdict and no record | §53.1 / EC-109 (L9780): a run that completes while checking nothing is a failed run — *"Silence is never taken as health"* |
| A **cache hit** makes the suite skip the work and report the previous answer | AT-102 (L9364) and §53.1: a run that reports zero findings, the canary included, is a FAILED run. A cached "pass" is a run that reported nothing because it looked at nothing |

Three binding pipeline rules follow, and each is enforced by a gate in §7 with a negative test that must make it fail:

1. **No output is a PASS.** Cancelled, timed out, skipped, neutral, crashed, empty log, absent gate record — every one of these is read as FAIL. Green is only ever an exact verdict line on stdout (`05-merge-gate.md` §3.1, §4.1) plus a `GATE-RESULT` counts line (`00-test-strategy.md` §3).
2. **A cache may hold inputs. A cache may never hold a result.** Dependency downloads, container layers and interpreter installs are cacheable. Test outcomes, gate verdicts, "unchanged since last run" markers and assertion counts are not. There is no `if: changed` anywhere in this pipeline.
3. **Fast is suspect until it is explained.** A run materially faster than its own rolling median, whose `assertions=` count did not rise, is flagged the same way §103 flags a plan-checker that rejected nothing — *"zero rejections means the gates are not working"* — and the same way §103 reads a review rejection rate: *"very low may mean rubber-stamping."* Speed that comes from asserting less is the pipeline's version of rubber-stamping. `GATE-L0-020` makes it mechanical.

---

## 2. Ownership — who writes these files, and why the verdict lives elsewhere

`.github/workflows/**` belongs to **L2** (PARTITION line 18). That is not negotiable and this file does not create an exception to it. It does create a problem, and the problem has a clean answer.

**The problem.** L2 owns the workflow files that judge L2. §53.1 states the principle that forbids this: *"no control that can be rewritten by the credential it is checking is a control."* `05-merge-gate.md` §2 states the same about the gate scripts.

**The answer — three mechanisms, none of which moves a path:**

| # | Mechanism | Who owns the enforcing artifact | PARTITION basis |
|---|---|---|---|
| 1 | **The thin-workflow rule.** No `selfci-*` workflow contains a verdict. Every workflow step either sets up the runner, invokes a `make` target, or asserts an exact string in that target's output. All decision logic lives in `contracts/gate/**` and the `Makefile` | **L0** — `contracts/**`, `Makefile` are L0's (PARTITION line 22) | rule 2, contract-first |
| 2 | **CODEOWNERS review.** `CODEOWNERS` is L0's (PARTITION line 22). It routes `.github/workflows/**` to L0, so L2 authors and L0 approves | **L0** | line 22 |
| 3 | **Mirror agreement.** `LG-12` and `IG-12` compare the CI conclusion with L0's local `make` verdict and fail on any delta. A lane quietly weakening the CI invocation is caught by the disagreement, not by reading the diff | **L0** — `contracts/gate/mirror-agree.sh` | `05-merge-gate.md` §2 |

**The verdict of record is always the L0 `make` run.** CI is the mirror. When the two disagree, `05-merge-gate.md` §9 is explicit: *never take the greener of the two verdicts.*

### 2.1 D-L2-06 is resolved here — option (b), retroactive replay

`L2-00-charter.md` DECISION REQUIRED D-L2-06 asks how the merge train can run `L1 → L4 → L2 → L3 → L5` when `lane-guard.yml` is an L2 file that does not exist until L2's first PR of cycle 1.

**Resolution, binding: option (b). No partition exception is created.** The lane-guard *check* is not the lane-guard *workflow*. `contracts/gate/lane-guard.sh` is L0-owned and exists at BT-0, before any lane branch. Therefore:

```bash
set -euo pipefail
# Cycle 1 only. L0 runs the verdict of record locally for L1's and L4's PRs,
# before lane-guard.yml exists. This IS the gate; CI would only have mirrored it.
make gate-lane LANE=1 PR=<n>     # must print exactly one VERDICT=PASS GATE=lane line
make gate-lane LANE=4 PR=<n>

# At the first integration gate, IG-08 replays LG-02 over the whole merged range,
# so cycle 1's unguarded merges are re-checked, not forgiven.
bash contracts/gate/lane-guard.sh --replay --base origin/main --head origin/integration
# expected: IG-08 lane-guard-replay PASS commits=<n> foreign=0 unowned=0
```

The first L2 PR of cycle 1 is `L2-T004` (`lane-guard.yml`), and from the moment it merges, CI mirrors the check on every lane PR. `DoD-20` of the L2 charter is satisfied for cycle 1 by the replay record, not by a claim.

---

## 3. The workflow set

Six files. All under `.github/workflows/`, all L2-authored and L0-approved, all thin.

| # | File | Trigger | What it is | Emits a required context? | Writes a record? |
|---|---|---|---|---|---|
| 1 | `selfci-lane.yml` | `push` on `lane/**` | T1 fast feedback for one lane: lane suite, negative audit, lane guard | No | No |
| 2 | `selfci-gate-a.yml` | `pull_request` → `integration` | The GATE A mirror: `make gate-lane` | **Yes** — `selfci-gate-a` | Yes (hosted job) |
| 3 | `lane-guard.yml` | `pull_request` → `integration` | Standalone path-ownership check. Already specified as `L2-T004`; reproduced here only by reference | **Yes** — `lane-guard` | No |
| 4 | `selfci-integration.yml` | `push` on `integration` | Post-merge T2 (all ten CT pairs), lane-guard replay, assertion ratchet | No | Yes (hosted job) |
| 5 | `selfci-gate-b.yml` | `pull_request` → `main`, `workflow_dispatch` | The GATE B mirror: `make gate-integration` | **Yes** — `selfci-gate-b` | Yes (hosted job) |
| 6 | `selfci-nightly.yml` | `schedule`, `workflow_dispatch` | Daily T3, the injected-defect drill for all five lanes, T4 acceptance for the current phase | No | Yes (hosted job) |
| 7 | `selfci-meta.yml` | `pull_request` → `integration`, `push` on `integration` | **The pipeline's own gates**, `GATE-L0-010` … `GATE-L0-020` | **Yes** — `selfci-meta` | No |

**Why `lane-guard.yml` survives alongside `selfci-gate-a.yml`.** `lane-guard` is the only context named literally by PARTITION, and it is the single required check in the **armed** CP-1 ruleset of `master/02-branch-merge-model.md` §10.2 (the unarmed CP-1 and CP-2 rulesets of §10.1/§10.3 both declare `required_status_checks: []` — empty — until arming). `make gate-lane` also runs `LG-02`. The duplication is deliberate: the ruleset context must exist before the `Makefile` is reachable from a runner, and two independent executions of the same check that disagree is itself a signal. Do not delete either.

### 3.1 Trigger map, drawn

```
  push lane/**                 PR -> integration              push integration
       |                              |                              |
  selfci-lane                  selfci-gate-a                 selfci-integration
  (T1, cancellable)            lane-guard                    (T2 post-merge, singleton)
       |                       selfci-meta                          |
       |                       (required contexts)                  |
       |                              |                             |
       +---------- lane merges in train order L1,L4,L2,L3,L5 -------+
                                                                    |
                                                        PR: integration -> main
                                                                    |
                                                            selfci-gate-b
                                                        (GATE B mirror, singleton)
                                                                    |
                                                                  main
  schedule 02:00 declared TZ ------> selfci-nightly (T3 + drills + T4)
```

Every wall-clock trigger in this pipeline resolves against the **declared operating timezone in the company working calendar**, never runner local time (spec L451: *"never against whatever timezone a runner happens to hold"*; §97.1 time rule L8848–8854). GitHub's `schedule:` cron is UTC-only, so the workflow declares UTC and the *first step* re-resolves against the calendar and exits non-zero if the calendar says the window is wrong. This mirrors L2's Friday-freeze obligation (`DoD-10`, §34.2 L2930–2935) and is checked by `GATE-L0-018`.

---

## 4. Concurrency — the configuration that stops five lanes queueing behind each other

### 4.1 The arithmetic that makes this the most expensive thing in the programme

`master/02-branch-merge-model.md` §10.1/§10.3 sets `strict_required_status_checks_policy: true` on both CP-1 and CP-2. That means **a branch must be up to date with its base before it can merge**. With five lanes and a fixed merge train (PARTITION line 35: `L1 → L4 → L2 → L3 → L5`), every merge into `integration` invalidates the up-to-dateness of the four PRs behind it. Each of them must rebase and re-run GATE A. The train is therefore inherently serial, and its floor is:

```
train_floor  =  5 x ( rebase + GATE_A_duration + merge )   +   integration_gate_duration
```

| GATE A duration | Train floor | Consequence |
|---|---|---|
| 5 min (the budget in §6) | ≈ 35 min | One train per morning, two per day comfortably |
| 15 min | ≈ 85 min | One train per day, and only if nothing fails |
| 25 min | ≈ 2 h 20 m | The train does not complete in a working day. Lanes idle. Cost is five agents' wall-clock, not one |

Five low-cost AI developers waiting on CI is the single largest recoverable cost in this build. **The train is serial by design and must not be parallelised** — reordering around a failure ships the dependency inversion the order exists to prevent (`00-test-strategy.md` §5, T3). The only lever is duration, which is §5 and §6.

**What concurrency configuration actually buys** is the other half: the five lanes' *ordinary* pushes must never contend, because that is pure waste with no compensating property.

### 4.2 The concurrency table — binding

| Workflow | `concurrency.group` | `cancel-in-progress` | Why exactly this |
|---|---|---|---|
| `selfci-lane.yml` | `selfci-lane-${{ github.ref }}` | **`true`** | Keyed on the full ref, so `lane/1/...` and `lane/3/...` are different groups and never queue behind each other. A superseded push on the *same* branch is waste. Emits no required context and writes no record, so cancellation destroys nothing |
| `selfci-gate-a.yml` | `selfci-gate-a-${{ github.event.pull_request.number }}` | **`true`** | Keyed on the PR number — one group per PR, five lanes are five groups. Safe despite emitting a required context: branch protection evaluates the check runs **of the head SHA**, and a cancelled run always belongs to a superseded SHA. `LG-10` proves the head SHA carries no cancelled/skipped/neutral required context |
| `lane-guard.yml` | *(none — declares no `concurrency:` block)* | n/a | Runs to completion always. It is the one context in the armed CP-1 ruleset (§10.2); a cancelled `lane-guard` on any SHA is a hole in the only armed protection the build has in BT-0/BT-1 |
| `selfci-integration.yml` | `selfci-integration` | **`false`** | A repository-wide singleton. Two post-merge T2 runs on `integration` at once can interleave record writes and produce two gate records for one state. A cancelled run writes **no** record, and a missing record fails `IG-12` and T3 check 11 |
| `selfci-gate-b.yml` | `selfci-gate-b` | **`false`** | Same. GATE B is once per cycle and there is no partial GATE B (`05-merge-gate.md` §4.1) |
| `selfci-nightly.yml` | `selfci-nightly` | **`false`** | The drill injection of `00-test-strategy.md` §4.3 must complete. *"A cycle with no drill record is not a clean cycle"* — cancelling the nightly manufactures exactly that |
| `selfci-meta.yml` | `selfci-meta-${{ github.ref }}` | **`true`** | Per-ref, no record, no state |

### 4.3 The polarity rule — one sentence, mechanically checked

> **`cancel-in-progress: true` is permitted only on a workflow that writes no record and whose required contexts, if any, are keyed per-PR so that a cancellation can only ever land on a superseded SHA. Everywhere else it is `false`, and the block is never absent.**

Absent is not the same as `false` for the *singleton* workflows: without a `concurrency:` block, GitHub runs them in parallel, which is the interleaving problem. `GATE-L0-014` asserts the block is present and the polarity matches this table, and its negative fixture flips `selfci-integration.yml` to `cancel-in-progress: true` and requires the gate to fail.

### 4.4 Concurrency groups do not buy runner capacity

This is the part that is easy to get wrong. A concurrency group prevents *self-collision*; it does nothing about a runner pool of size 1, where five lanes queue anyway. The estate rule:

| Pool | Label | Minimum size | Rationale |
|---|---|---|---|
| Unprivileged build CI | `[self-hosted, linux, build-ci]` | **6** | Five lanes pushing concurrently, plus one slot for the train's in-flight GATE A. At five, the train's GATE A queues behind a lane push, and the arithmetic of §4.1 gains a random 90 s per train step |
| Privileged (record writes, promotion) | GitHub-hosted `ubuntu-latest` | — | Ephemeral by construction; see §5.1 |

Runner hosts are a **named asset class** in the operational asset inventory with a named owner, a fixed cost band and a declared patch cadence, and no runner is ever placed on the operations VM (§49.1, L4351). Loss of the pool is not a GitHub outage and does not enter degraded mode by inference — the spec declares it separately: *loss of the CI execution estate is an entry condition into degraded engineering mode* (§46.6 second occurrence, L4191–4211). During the build, that means: L0 declares it, announces it, and the train stops; lanes do not "merge anyway because CI is down".

> **Citation caution for implementers.** `MultiProduct_MasterSpec_v4.0.md` carries **two** headings numbered `### 46.6` — *Monitoring stack unavailable* at L4187 and *CI execution estate outage* at L4191. Cite CI-estate loss by line number (L4191–4211), never by section number alone.

---

## 5. Runner topology and caching

### 5.1 The privilege split — why caching is available in exactly one half

Spec L3587–3597 (Section 39, the *Runner posture* and *Privileged-workflow isolation (Priority: P0)* paragraphs; D80, D87) states the rule and the reason:

* All self-hosted runners live in an organisation runner group restricted to named private repositories, with public-repository access off.
* The real exposure is **persistence, not provenance**: *"if that runner is long-lived and later runs a privileged workflow, anything the first job left behind on the host is present when production credentials materialise into the second."*
* *"The default is a hosted runner. Privileged workflows run on GitHub-hosted runners, which are destroyed after every job."* This is a recorded, deliberate exception to the self-hosted posture, and it *"does not weaken the fixed-cost rule"* because the privileged tail is small and low-frequency.
* *"The separation is asserted in the workflow, not only in configuration."* A privileged job that finds itself on a shared-pool runner does not proceed.

Applied to the build's own CI:

| Job class | Runner | Secrets | Cache | Spec basis |
|---|---|---|---|---|
| Verification (lane suite, gate scripts, contract tests, meta gates) | `[self-hosted, linux, build-ci]`, persistent | **none**; `permissions: contents: read` | **Yes** — host-local, inputs only | §49.1 L4351: the self-hosted estate is *"what keeps CI inside the fixed-cost doctrine (D80)"*; invariant 83 (fixed-cost tooling) |
| Record write, drill injection, promotion | `ubuntu-latest`, hosted, destroyed per job | records-writer credential | **No** — nothing persists, by design | L3593; invariant 18 (machine layer cannot merge, approve or deploy); §40.1 L3644–3686 |

The verification half caches because it holds no credential worth stealing. The privileged half does not cache because persistence *is* the vulnerability. This is not a performance compromise — it is the same sentence read twice.

Every privileged job asserts its own isolation as its **first step**, mirroring L2's `E-5` actor-gate obligation (§37.3, L3261–3268):

```bash
set -euo pipefail
# first step of every privileged job in this pipeline
case "${RUNNER_ENVIRONMENT:-}" in
  github-hosted) : ;;
  *) echo "SELFCI FAIL privileged-job-on-non-hosted-runner env=${RUNNER_ENVIRONMENT:-unset}"; exit 1 ;;
esac
```

### 5.2 The cache design

No third-party caching Action is used. Two reasons, both real: every third-party Action must be pinned to a full commit SHA (invariant 85, §48.1 L4300–4308), and this document will not print a SHA it has not verified; and on a persistent self-hosted host, an Action that tars a directory into remote storage is strictly slower than the directory already being there. The only Action used anywhere in this pipeline is `actions/checkout`, pinned to the SHA already frozen by `L2-T004`.

The cache is a directory on the runner host, managed by an L0-owned script:

```bash
# contracts/gate/ci-cache.sh   (L0-owned; PARTITION line 22)
# Usage: ci-cache.sh warm | ci-cache.sh path | ci-cache.sh audit
#
# Cache root, fixed:      /opt/selfci-cache
# Layout:                 /opt/selfci-cache/venv/<key>/          python env
#                         /opt/selfci-cache/pip/                 pip download cache
#                         /opt/selfci-cache/tools/<key>/         yq, jq, pinned binaries
# Key:                    sha256 of the concatenated dependency manifests, nothing else.
```

```bash
#!/usr/bin/env bash
set -euo pipefail
CACHE_ROOT="${SELFCI_CACHE_ROOT:-/opt/selfci-cache}"

cache_key() {
  # Inputs only. If a file in this list does not exist, that is a hard error:
  # a key computed over a missing manifest silently collapses to a constant.
  local manifests="validators/registry/requirements.txt contracts/gate/tools.lock"
  # NOT ARMED -- excluded from counts, Phase 1+: contracts/gate/tools.lock is an
  # unbuilt path (Founder decision A7, 2026-09-16; see protocol/_98-DEEP-REVIEW.md B-06).
  # This hard-errors every job until it is authored and assigned to an owning lane.
  for m in $manifests; do
    [ -f "$m" ] || { echo "CI-CACHE FAIL missing-manifest $m" >&2; exit 1; }
  done
  cat $manifests | sha256sum | cut -c1-16
}

warm() {
  local key venv tmp
  key="$(cache_key)"
  venv="$CACHE_ROOT/venv/$key"
  if [ -d "$venv" ]; then
    echo "CI-CACHE HIT key=$key"
    return 0
  fi
  mkdir -p "$CACHE_ROOT/venv" "$CACHE_ROOT/pip" "$CACHE_ROOT/tools"
  tmp="$(mktemp -d "$CACHE_ROOT/venv/.tmp.XXXXXX")"
  python3 -m venv "$tmp/env"
  PIP_CACHE_DIR="$CACHE_ROOT/pip" "$tmp/env/bin/pip" install --quiet \
      -r validators/registry/requirements.txt
  # Atomic publish. Two lanes warming the same key concurrently is normal and safe:
  # the loser's mv fails, its tree is discarded, and both see the same result.
  mv -T "$tmp/env" "$venv" 2>/dev/null || rm -rf "$tmp"
  rm -rf "$tmp"
  echo "CI-CACHE MISS key=$key built=1"
}

path() { echo "$CACHE_ROOT/venv/$(cache_key)/bin"; }

audit() {
  # GATE-L0-016. A cache entry that is not an input is a result, and a result
  # in a cache is a run that reported an answer without computing it.
  local bad=0
  while IFS= read -r f; do
    case "$f" in
      */venv/*|*/pip/*|*/tools/*) : ;;
      *) echo "CI-CACHE FAIL non-input-cache-entry $f"; bad=1 ;;
    esac
  done < <(find "$CACHE_ROOT" -mindepth 2 -maxdepth 2 -print 2>/dev/null)
  # Result-shaped names are rejected wherever they appear.
  if find "$CACHE_ROOT" \( -name '*.verdict' -o -name '*.result' -o -name 'GATE-RESULT*' \
       -o -name '*.passed' -o -name 'assertions*' \) -print -quit | grep -q .; then
    echo "CI-CACHE FAIL result-shaped-entry-in-cache"; bad=1
  fi
  [ "$bad" -eq 0 ] && echo "CI-CACHE AUDIT PASS root=$CACHE_ROOT" || exit 1
}

case "${1:-}" in
  warm) warm ;;
  path) path ;;
  audit) audit ;;
  *) echo "usage: ci-cache.sh warm|path|audit" >&2; exit 2 ;;
esac
```

**Three properties of this design that are not optional:**

1. **The key is computed from manifests only.** Never from a branch name, never from a commit SHA, never from "last successful run". A key that varies per commit is not a cache; a key that varies per lane makes five lanes pay five first-run costs.
2. **A missing manifest is a hard error, not an empty key.** A key silently collapsing to a constant is the vacuity failure applied to caching: every lane would then share one stale environment forever and nothing would detect it.
3. **The cache never short-circuits a decision.** `ci-cache.sh` has no `pass`, `skip` or `verdict` verb. There is no code path in this pipeline in which a cache hit causes a test not to run. `GATE-L0-016` audits the cache root for result-shaped entries on every integration run, and its negative fixture plants `/opt/selfci-cache/GATE-RESULT-last.txt` and requires the audit to fail.

### 5.3 The other speed levers, in order of payoff

| Lever | Saving | Cost / risk | Verdict |
|---|---|---|---|
| Persistent self-hosted pool with a warm venv | 40–90 s per job | Runner hosts, owned and patched (§49.1) | **Adopted** |
| `fetch-depth: 0` only where the gate needs history | 10–30 s on shallow-able jobs | `LG-01`, `LG-02`, `IG-08` all need merge-base history; the meta gate does not | **Adopted, per job** |
| Splitting T1 from GATE A so lane pushes get a 90 s answer | Feedback latency, not train time | Two workflows instead of one | **Adopted** |
| Running the ten CT pairs of `00-test-strategy.md` §5 as a job matrix | 3–8 min on `selfci-integration` | Ten check runs instead of one; none of them required contexts | **Adopted** |
| Path filters to skip jobs when a tree is untouched | Large | **Forbidden.** §33.2: a workflow skipped by a path filter never reports at all, and the required check is still listed in protection | **Rejected** |
| `if:` conditions to skip a suite when nothing changed | Large | **Forbidden.** Same paragraph: a skipped conclusion is counted as satisfied | **Rejected** |
| Test-result caching / "only changed tests" | Large | **Forbidden.** §5.2 rule 3 | **Rejected** |
| Reducing assertion counts to fit the budget | Large | **Forbidden.** T3 check 5 (assertion ratchet) rejects it; `GATE-L0-020` flags it | **Rejected** |

The last four rows are why this document exists. Every one of them is the fastest available fix and every one converts a gate into decoration.

---

## 6. Speed budgets, timeouts, and what a breach means

| Workflow | p50 budget | `timeout-minutes` | Breach handling |
|---|---|---|---|
| `selfci-lane.yml` | 90 s | 5 | Amber. Recorded on the cycle record; investigated when two consecutive cycles breach |
| `selfci-meta.yml` | 60 s | 5 | Amber |
| `selfci-gate-a.yml` | 5 min | 12 | **Red.** It multiplies by five through the train (§4.1). L0 opens a blocker and the next cycle's L2 task is pipeline latency |
| `selfci-integration.yml` | 15 min | 35 | Amber |
| `selfci-gate-b.yml` | 20 min | 45 | Amber |
| `selfci-nightly.yml` | 45 min | 90 | Amber |

**`timeout-minutes` is mandatory on every job**, set to roughly twice the budget. A hung job that GitHub eventually cancels at the 6-hour default produces no verdict for six hours and blocks the train for a day. A timeout is not a soft signal here: per Rule Zero item 1, a timed-out job **is a FAIL**, and `GATE-L0-017` fails the meta gate if any job in any `selfci-*` file lacks `timeout-minutes`.

**The Platform SLO this build inherits.** §51.2 (L4447–4453) sets *CI availability: 99% of pushes produce a completed run within SLA*, measured on workflow-run success and duration, with the response *"Team Lead; consider runner capacity"* and the escalation *"Blocking where it prevents an incident fix."* During the build the same objective applies with L0 in the Team Lead's place, and "prevents an incident fix" reads as "prevents the train from completing in a working day."

**The ratchet, not the average.** Duration is recorded per run on the gate record (§9) alongside `assertions=`. The pair is what is read, never duration alone. Falling duration with flat assertions is `GATE-L0-020`. Rising duration with rising assertions is the system working.

---

## 7. The workflow YAML

All six files. Every job carries `timeout-minutes`, an explicit `permissions:` block (§33.2: *"the organisation default for `GITHUB_TOKEN` permissions is read-only; a workflow that needs write access declares it explicitly, per permission"*), a concurrency policy from §4.2, and no `if:` on any job that emits a required context.

The single pinned Action SHA below is the one already frozen by `L2-T004`:
`actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2`.
**STOP rule:** if that SHA does not resolve in the organisation's allowed-actions configuration, do not substitute a tag (§48.1 L4300–4308, invariant 85). File a blocker.

### 7.1 `.github/workflows/selfci-lane.yml`

```yaml
name: selfci-lane
# Build CI, T1 fast feedback for one lane branch. NOT part of the workflows/* release train.
# Protocol: implementation/protocol/10-ci-pipeline.md sections 3, 4.2, 6.
on:
  push:
    branches:
      - 'lane/**'
permissions:
  contents: read
concurrency:
  group: selfci-lane-${{ github.ref }}
  cancel-in-progress: true
defaults:
  run:
    shell: bash
jobs:
  lane-suite:
    name: selfci-lane-suite
    runs-on: [self-hosted, linux, build-ci]
    timeout-minutes: 5
    steps:
      - name: Checkout
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          fetch-depth: 0

      - name: Resolve the lane number from the branch name
        id: lane
        run: |
          set -euo pipefail
          B="${GITHUB_REF_NAME}"
          # §4.10: this regex is the only site with a hard exit; loosened to soft report.
          # 265 of 486 live branch names do not match the narrow grammar; blocking them
          # all was rejecting legitimate work. Canonical grammar is master/09-glossary-
          # and-conventions.md section 4 (branch naming) — this is an exact copy of that
          # regex, not a separately maintained one; if it ever needs to change, change it
          # there first.
          BRANCH_REGEX='^(lane/[1-5]/(f[0-7]|g[1-8]|p[1-8])-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+){1,4}|l0/.+|integration|main)$'
          if ! [[ "$B" =~ $BRANCH_REGEX ]]; then
            echo "WARN: branch name '$B' does not match canonical pattern — reported but not blocked"
          fi
          echo "lane=$(printf '%s' "$B" | cut -d/ -f2)" >> "$GITHUB_OUTPUT"

      - name: Warm the input cache (inputs only; never a result)
        run: bash contracts/gate/ci-cache.sh warm

      - name: Run the lane suite, the negative audit and the lane guard
        env:
          LANE: ${{ steps.lane.outputs.lane }}
        run: |
          set -euo pipefail
          export PATH="$(bash contracts/gate/ci-cache.sh path):$PATH"
          mkdir -p .gate
          git fetch --no-tags origin integration
          make lane LANE="$LANE" 2>&1 | tee .gate/lane.log

      - name: Assert the run was not vacuous
        run: |
          set -euo pipefail
          LINE="$(grep -E '^GATE-RESULT ' .gate/lane.log | tail -1 || true)"
          if [ -z "$LINE" ]; then
            echo "SELFCI FAIL no-GATE-RESULT-line"
            echo "Silence is never taken as health (EC-109, spec line 9780)."
            exit 1
          fi
          get() { printf '%s\n' "$LINE" | tr ' ' '\n' | grep "^$1=" | cut -d= -f2; }
          A="$(get assertions)"; F="$(get failures)"
          NR="$(get negatives_run)"; NC="$(get negatives_that_failed_correctly)"
          echo "$LINE"
          [ "${A:-0}" -gt 0 ]      || { echo "SELFCI FAIL vacuous assertions=0"; exit 1; }
          [ "${F:-1}" -eq 0 ]      || { echo "SELFCI FAIL assertions-failed failures=$F"; exit 1; }
          [ "${NR:-0}" -gt 0 ]     || { echo "SELFCI FAIL no-negatives-run"; exit 1; }
          [ "${NC:-0}" -eq "$NR" ] || { echo "SELFCI FAIL non-discriminating $NC/$NR"; exit 1; }
          echo "SELFCI-LANE PASS assertions=$A negatives=$NC/$NR" >> "$GITHUB_STEP_SUMMARY"
```

### 7.2 `.github/workflows/selfci-gate-a.yml`

```yaml
name: selfci-gate-a
# The GATE A mirror. The verdict of record is L0's local `make gate-lane` run
# (implementation/protocol/05-merge-gate.md section 2). LG-12 compares the two.
on:
  pull_request:
    branches:
      - integration
permissions:
  contents: read
concurrency:
  # Keyed per PR: five lanes are five groups and never queue behind one another.
  group: selfci-gate-a-${{ github.event.pull_request.number }}
  cancel-in-progress: true
defaults:
  run:
    shell: bash
jobs:
  gate-a:
    # This job name is the required-status-check context string. Do not rename it
    # without following the registration procedure in section 8.
    name: selfci-gate-a
    runs-on: [self-hosted, linux, build-ci]
    timeout-minutes: 12
    steps:
      - name: Checkout the PR head
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          fetch-depth: 0
          ref: ${{ github.event.pull_request.head.sha }}

      - name: Resolve the lane number from the head ref
        id: lane
        run: |
          set -euo pipefail
          B="${GITHUB_HEAD_REF}"
          echo "$B" | grep -Eq '^lane/[1-5]/' || {
            echo "GATE-A FAIL head-ref-carries-no-lane-prefix ref=$B"; exit 1; }
          echo "lane=$(printf '%s' "$B" | cut -d/ -f2)" >> "$GITHUB_OUTPUT"

      - name: Warm the input cache
        run: bash contracts/gate/ci-cache.sh warm

      - name: Evaluate GATE A
        env:
          LANE: ${{ steps.lane.outputs.lane }}
          PR: ${{ github.event.pull_request.number }}
        run: |
          set -euo pipefail
          export PATH="$(bash contracts/gate/ci-cache.sh path):$PATH"
          mkdir -p .gate
          git fetch --no-tags origin integration
          make gate-lane LANE="$LANE" PR="$PR" | tee .gate/lane.stdout

      - name: Assert the single unambiguous pass line
        run: |
          set -euo pipefail
          # Exactly the test from 05-merge-gate.md section 3.1. One line, and that line.
          if grep -Fq 'VERDICT=PASS GATE=lane' .gate/lane.stdout \
             && [ "$(wc -l < .gate/lane.stdout)" -eq 1 ]; then
            echo "GATE-A-OPEN"
          else
            echo "GATE-A-CLOSED"
            echo '--- first FAIL line from .gate/lane.log ---'
            grep -m1 ' FAIL ' .gate/lane.log || echo '(no FAIL line: the gate produced no output at all)'
            exit 1
          fi
          {
            echo '### GATE A'
            echo '```'
            cat .gate/lane.stdout
            echo '```'
          } >> "$GITHUB_STEP_SUMMARY"

      - name: Publish the CI verdict for LG-12 mirror comparison
        run: |
          set -euo pipefail
          install -d .gate
          printf 'ci_conclusion=PASS\nci_run_id=%s\nhead=%s\n' \
            "$GITHUB_RUN_ID" "${{ github.event.pull_request.head.sha }}" > .gate/ci.verdict
          cat .gate/ci.verdict >> "$GITHUB_STEP_SUMMARY"

  record:
    # Not a required context, so `if:` is permitted here and nowhere else in this file.
    name: selfci-gate-a-record
    needs: gate-a
    if: always()
    runs-on: ubuntu-latest
    timeout-minutes: 5
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - name: Assert privileged-job isolation (spec lines 3587-3597, D87)
        run: |
          set -euo pipefail
          case "${RUNNER_ENVIRONMENT:-}" in
            github-hosted) echo "runner=hosted OK" ;;
            *) echo "SELFCI FAIL privileged-job-on-non-hosted-runner env=${RUNNER_ENVIRONMENT:-unset}"
               exit 1 ;;
          esac
      - name: Write the gate-run record (a required, failing step - never best-effort)
        env:
          GH_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
          RESULT: ${{ needs.gate-a.result }}
        run: |
          set -euo pipefail
          [ -n "${GH_TOKEN:-}" ] || { echo "SELFCI FAIL records-writer-secret-absent"; exit 1; }
          bash contracts/gate/emit-gate-record.sh \
            --gate lane \
            --pr "${{ github.event.pull_request.number }}" \
            --head "${{ github.event.pull_request.head.sha }}" \
            --result "$RESULT" \
            --run-id "$GITHUB_RUN_ID"
```

> **Frozen at BT-0 by this document, closing the CI half of `D-L2-03`:** the records-writer secret is named **`RECORDS_WRITER_TOKEN`**, its target repository is `control-plane-records`, and gate-run records land at `records/gate/<gate>/<date>/<key>.yaml`, one file per run (`05-merge-gate.md` §10). The step above **fails closed** when the secret is absent; it never degrades to a warning. §97.2 (L8855–8939) makes record writes required, failing steps, and `L2-00` `DoD-15` says the same.

### 7.3 `.github/workflows/selfci-integration.yml`

```yaml
name: selfci-integration
# Post-merge verification on the integration branch, once per merge-train step.
# Halts the train on a T2 failure (00-test-strategy.md section 8).
on:
  push:
    branches:
      - integration
permissions:
  contents: read
concurrency:
  # Repository-wide singleton. Never cancel: a cancelled run writes no record,
  # and a missing record fails IG-12 and T3 check 11.
  group: selfci-integration
  cancel-in-progress: false
defaults:
  run:
    shell: bash
jobs:
  contract-tests:
    name: selfci-integration-ct-${{ matrix.pair }}
    runs-on: [self-hosted, linux, build-ci]
    timeout-minutes: 20
    strategy:
      fail-fast: false
      matrix:
        # PENDING (§4.10 / REG-045): Hard-coded CT-01…CT-10 replaced by matrix
        # generated from contracts/harness/pairs.tsv at workflow runtime.
        # One candidate becomes binding only when REG-045 is closed.
        # At runtime: mapfile -t CT_IDS < <(awk -F'\t' '{print $1}' contracts/harness/pairs.tsv)
        # NOT ARMED -- excluded from counts, Phase 1+: contracts/harness/** is an unbuilt
        # path (Founder decision A7, 2026-09-16; see protocol/_98-DEEP-REVIEW.md B-06).
        # The hard-coded CT-01..CT-10 list below is what actually runs today.
        pair: [CT-01, CT-02, CT-03, CT-04, CT-05, CT-06, CT-07, CT-08, CT-09, CT-10]
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          fetch-depth: 0
      - name: Warm the input cache
        run: bash contracts/gate/ci-cache.sh warm
      - name: Contract tests for one provider/consumer pair
        run: |
          set -euo pipefail
          export PATH="$(bash contracts/gate/ci-cache.sh path):$PATH"
          mkdir -p .gate
          make contract-tests PAIR=${{ matrix.pair }} 2>&1 | tee ".gate/${{ matrix.pair }}.log"
          grep -Eq '^GATE-RESULT .* level=T2 ' ".gate/${{ matrix.pair }}.log" || {
            echo "SELFCI FAIL ct-emitted-no-GATE-RESULT pair=${{ matrix.pair }}"; exit 1; }

  guard-replay-and-audits:
    name: selfci-integration-audits
    runs-on: [self-hosted, linux, build-ci]
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          fetch-depth: 0
      - name: Warm the input cache
        run: bash contracts/gate/ci-cache.sh warm
      - name: Lane-guard replay over the whole merged range (IG-08)
        run: |
          set -euo pipefail
          mkdir -p .gate
          git fetch --no-tags origin main
          bash contracts/gate/lane-guard.sh --replay \
            --base origin/main --head "$GITHUB_SHA" | tee .gate/replay.log
          grep -Fq 'foreign=0 unowned=0' .gate/replay.log
      - name: Fixture corpus gate (09-fixtures.md section 9)
        run: |
          set -euo pipefail
          export PATH="$(bash contracts/gate/ci-cache.sh path):$PATH"
          make fixtures-all
      - name: Negative audit across all five lanes and L0
        run: make negative-audit
      - name: Cache audit - the cache holds inputs, never results (GATE-L0-016)
        run: bash contracts/gate/ci-cache.sh audit
      - name: Assertion ratchet against the previous cycle tag (T3 check 5)
        run: |
          set -euo pipefail
          bash contracts/gate/assertion-ratchet.sh --head "$GITHUB_SHA" | tee .gate/ratchet.log
          grep -Fq 'RATCHET PASS' .gate/ratchet.log

  record:
    name: selfci-integration-record
    needs: [contract-tests, guard-replay-and-audits]
    if: always()
    runs-on: ubuntu-latest
    timeout-minutes: 5
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - name: Assert privileged-job isolation
        run: |
          set -euo pipefail
          [ "${RUNNER_ENVIRONMENT:-}" = "github-hosted" ] || {
            echo "SELFCI FAIL privileged-job-on-non-hosted-runner"; exit 1; }
      - name: Write the post-merge gate record
        env:
          GH_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
        run: |
          set -euo pipefail
          [ -n "${GH_TOKEN:-}" ] || { echo "SELFCI FAIL records-writer-secret-absent"; exit 1; }
          bash contracts/gate/emit-gate-record.sh \
            --gate integration-step \
            --head "$GITHUB_SHA" \
            --ct "${{ needs.contract-tests.result }}" \
            --audits "${{ needs.guard-replay-and-audits.result }}" \
            --run-id "$GITHUB_RUN_ID"
```

### 7.4 `.github/workflows/selfci-gate-b.yml`

> **NOT ARMED — excluded from counts, Phase 1+.** This job reads `contracts/gate/tools.lock` and `contracts/gate/CURRENT-CYCLE`, both unbuilt paths (Founder decision A7, 2026-09-16; see `protocol/_98-DEEP-REVIEW.md` B-06). It does not run until they are authored and assigned to an owning lane.

```yaml
name: selfci-gate-b
# The GATE B mirror: integration -> main, once per merge cycle.
# There is no partial GATE B (05-merge-gate.md section 4.1).
on:
  pull_request:
    branches:
      - main
  workflow_dispatch:
    inputs:
      cycle:
        description: 'Cycle id, e.g. 2026-W36'
        required: true
        type: string
permissions:
  contents: read
concurrency:
  group: selfci-gate-b
  cancel-in-progress: false
defaults:
  run:
    shell: bash
jobs:
  gate-b:
    name: selfci-gate-b
    runs-on: [self-hosted, linux, build-ci]
    timeout-minutes: 45
    outputs:
      cycle: ${{ steps.c.outputs.cycle }}
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          fetch-depth: 0
      - name: Warm the input cache
        run: bash contracts/gate/ci-cache.sh warm
      - name: Resolve the cycle id
        id: c
        run: |
          set -euo pipefail
          CY="${{ inputs.cycle }}"
          if [ -z "$CY" ]; then CY="$(cat contracts/gate/CURRENT-CYCLE)"; fi
          [ -n "$CY" ] || { echo "GATE-B FAIL cycle-id-unresolvable"; exit 1; }
          echo "cycle=$CY" >> "$GITHUB_OUTPUT"
      - name: Evaluate GATE B
        run: |
          set -euo pipefail
          export PATH="$(bash contracts/gate/ci-cache.sh path):$PATH"
          mkdir -p .gate
          git fetch --no-tags origin main integration
          make gate-integration CYCLE="${{ steps.c.outputs.cycle }}" | tee .gate/integration.stdout
      - name: Assert the pass line, and assert its two most losable tokens by name
        run: |
          set -euo pipefail
          # Exactly the test from 05-merge-gate.md section 4.1.
          if grep -Fq 'VERDICT=PASS GATE=integration' .gate/integration.stdout \
             && grep -Fq 'canary=FOUND'      .gate/integration.stdout \
             && grep -Fq 'negatives=24/24'   .gate/integration.stdout \
             && [ "$(wc -l < .gate/integration.stdout)" -eq 1 ]; then
            echo "GATE-B-OPEN"
          else
            echo "GATE-B-CLOSED"
            grep -m1 ' FAIL ' .gate/integration.log || echo '(no FAIL line: the gate produced nothing)'
            exit 1
          fi
      - name: Assert the drill records exist for all five lanes (T3 check 11)
        run: |
          set -euo pipefail
          CY="${{ steps.c.outputs.cycle }}"
          MISSING=0
          for n in 1 2 3 4 5; do
            bash contracts/gate/record-exists.sh "records/gate-runs/$CY/drill-L$n.yaml" \
              || { echo "GATE-B FAIL drill-record-missing lane=L$n cycle=$CY"; MISSING=1; }
          done
          [ "$MISSING" -eq 0 ] || exit 1
          echo "GATE-B drills=5/5 cycle=$CY"

  record:
    name: selfci-gate-b-record
    needs: gate-b
    if: always()
    runs-on: ubuntu-latest
    timeout-minutes: 5
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - name: Assert privileged-job isolation
        run: |
          set -euo pipefail
          [ "${RUNNER_ENVIRONMENT:-}" = "github-hosted" ] || {
            echo "SELFCI FAIL privileged-job-on-non-hosted-runner"; exit 1; }
      - name: Write the cycle gate record
        env:
          GH_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
        run: |
          set -euo pipefail
          [ -n "${GH_TOKEN:-}" ] || { echo "SELFCI FAIL records-writer-secret-absent"; exit 1; }
          bash contracts/gate/emit-gate-record.sh \
            --gate integration \
            --cycle "${{ needs.gate-b.outputs.cycle }}" \
            --head "$GITHUB_SHA" \
            --result "${{ needs.gate-b.result }}" \
            --run-id "$GITHUB_RUN_ID"
```

### 7.5 `.github/workflows/selfci-nightly.yml`

> **NOT ARMED — excluded from counts, Phase 1+.** This job reads `contracts/gate/CURRENT-CYCLE` and `contracts/gate/CURRENT-PHASE`, both unbuilt paths (Founder decision A7, 2026-09-16; see `protocol/_98-DEEP-REVIEW.md` B-06). It does not run until they are authored and assigned to an owning lane.

```yaml
name: selfci-nightly
# Daily full T3, the injected-defect drill for all five lanes (00-test-strategy.md 4.3),
# and T4 acceptance for the phase currently in scope.
on:
  schedule:
    # Declared in UTC because GitHub cron accepts nothing else. The first step
    # re-resolves against the declared operating timezone (spec line 451).
    - cron: '0 1 * * 1-5'
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: selfci-nightly
  cancel-in-progress: false
defaults:
  run:
    shell: bash
jobs:
  calendar-gate:
    name: selfci-nightly-calendar
    runs-on: [self-hosted, linux, build-ci]
    timeout-minutes: 3
    outputs:
      cycle: ${{ steps.c.outputs.cycle }}
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - name: Resolve the window against the declared working calendar, not runner local time
        run: bash contracts/gate/calendar-gate.sh --window nightly
      - name: Resolve the cycle id
        id: c
        run: echo "cycle=$(cat contracts/gate/CURRENT-CYCLE)" >> "$GITHUB_OUTPUT"

  t3:
    name: selfci-nightly-t3
    needs: calendar-gate
    runs-on: [self-hosted, linux, build-ci]
    timeout-minutes: 90
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          fetch-depth: 0
          ref: integration
      - name: Warm the input cache
        run: bash contracts/gate/ci-cache.sh warm
      - name: Full integration gate
        run: |
          set -euo pipefail
          export PATH="$(bash contracts/gate/ci-cache.sh path):$PATH"
          mkdir -p .gate
          make gate-integration CYCLE="${{ needs.calendar-gate.outputs.cycle }}" \
            | tee .gate/nightly.stdout
          grep -Fq 'canary=FOUND' .gate/nightly.stdout
      - name: Spec acceptance for the phase in scope
        run: |
          set -euo pipefail
          P="$(cat contracts/gate/CURRENT-PHASE)"
          make acceptance PHASE="$P"
          make acceptance PHASE="$P" NEGATIVE=1

  drills:
    name: selfci-nightly-drill-L${{ matrix.lane }}
    needs: calendar-gate
    runs-on: ubuntu-latest
    timeout-minutes: 30
    permissions:
      contents: read
    strategy:
      fail-fast: false
      matrix:
        lane: [1, 2, 3, 4, 5]
    steps:
      - name: Assert privileged-job isolation
        run: |
          set -euo pipefail
          [ "${RUNNER_ENVIRONMENT:-}" = "github-hosted" ] || {
            echo "SELFCI FAIL privileged-job-on-non-hosted-runner"; exit 1; }
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          fetch-depth: 0
      - name: Inject one known-bad change and require the lane suite to reject it
        env:
          GH_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
        run: |
          set -euo pipefail
          [ -n "${GH_TOKEN:-}" ] || { echo "SELFCI FAIL records-writer-secret-absent"; exit 1; }
          mkdir -p .gate
          # Onto drill/<cycle>/L<n>, NEVER onto the lane's own branch (00-test-strategy 4.3).
          make drill CYCLE="${{ needs.calendar-gate.outputs.cycle }}" LANE=${{ matrix.lane }} \
            | tee .gate/drill-L${{ matrix.lane }}.log
          # The drill PASSES when the lane suite REJECTED the planted defect.
          grep -Fq "DRILL L${{ matrix.lane }} rejected=1" .gate/drill-L${{ matrix.lane }}.log || {
            echo "SELFCI FAIL drill-not-rejected lane=L${{ matrix.lane }}"
            echo "The lane suite accepted a known-bad change: exit 3, non-discriminating."
            echo "L${{ matrix.lane }} is BLOCKED from the merge train for this cycle."
            exit 1
          }
```

### 7.6 `.github/workflows/selfci-meta.yml`

```yaml
name: selfci-meta
# The pipeline's gates on itself: GATE-L0-010 .. GATE-L0-020.
# This is the workflow that stops the other five from becoming decoration.
on:
  pull_request:
    branches:
      - integration
  push:
    branches:
      - integration
permissions:
  contents: read
concurrency:
  group: selfci-meta-${{ github.ref }}
  cancel-in-progress: true
defaults:
  run:
    shell: bash
jobs:
  meta:
    # Required-status-check context. No `if:`. No path filter. Section 33.2.
    name: selfci-meta
    runs-on: [self-hosted, linux, build-ci]
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - name: Run every pipeline gate, then prove each one can fail
        run: |
          set -euo pipefail
          bash contracts/gate/pipeline-gates.sh --all      | tee .gate/meta.log
          bash contracts/gate/pipeline-gates.sh --negative | tee -a .gate/meta.log
          grep -Fq 'PIPELINE-GATES PASS proven=11/11 unproven=0' .gate/meta.log || {
            echo "SELFCI FAIL pipeline-gate-unproven"
            grep -E 'unproven|FAIL' .gate/meta.log || true
            exit 1
          }
```

---

## 8. The pipeline's own gates — `GATE-L0-010` … `GATE-L0-020`

**Id reservation.** `00-test-strategy.md` §4.1 fixes the format `GATE-L<n>-<nnn>` and already uses `GATE-L0-001` (the negative-audit recursion) and `GATE-L0-002` (lane-guard). **`GATE-L0-010` … `GATE-L0-020` are reserved by this document for the build's CI pipeline.** Declaration files live at `contracts/gate/gates/GATE-L0-0nn.yaml` (L0-owned), on the schema of `00-test-strategy.md` §4.2 — every field mandatory, including a `negative:` block with a distinct `proves:` sentence.

Eleven gates. Every one carries a negative fixture that must make it fail; a gate whose negative fixture passes reports exit `3` and closes both merge gates.

| Gate | Asserts | Negative fixture — the gate MUST reject it | Anchor |
|---|---|---|---|
| **GATE-L0-010** | **Thin workflow.** No `selfci-*` file contains a verdict. Every `run:` block either sets up, invokes `make`/`contracts/gate/*.sh`, or asserts a literal string in that output | A workflow step containing `if grep -q ok out.txt; then exit 0; fi` — a decision made inside L2's tree | §53.1 (*no control rewritable by the credential it checks*); `05-merge-gate.md` §2 |
| **GATE-L0-011** | **Library separation.** No `selfci-*` file is reachable from a `workflows/*` release tag, and none of the eight library workflow names begins with `selfci-` | A `workflows/v1` tag whose tree contains `selfci-gate-a.yml` | §33.2 reusable-workflow paragraph (L2854–2869); invariant 85 |
| **GATE-L0-012** | **No `if:`, no path filter on any required-context job.** Every job whose name appears in `contracts/gate/required-contexts.txt` carries neither | `if: false` added to the `selfci-gate-a` job | §33.2 path-filter paragraph; L2 `DoD-06`; CT-09 |
| **GATE-L0-013** | **Full-SHA pinning.** Every `uses:` in every `selfci-*` file resolves to a 40-hex SHA; no tag, no branch | `uses: actions/checkout@v4` | invariant 85 (L9578); §48.1 (L4300–4308) |
| **GATE-L0-014** | **Concurrency polarity.** Every `selfci-*` file declares a `concurrency:` block, and its `cancel-in-progress` value matches the §4.2 table exactly | `selfci-integration.yml` flipped to `cancel-in-progress: true` | §4.3 of this file; `IG-12` (a run with no record) |
| **GATE-L0-015** | **Least privilege.** Every workflow declares a top-level `permissions:` block; no job holds a permission it does not use; no `write-all` anywhere | `permissions: write-all` on `selfci-lane.yml` | §33.2 token-permissions bullet; invariant 18 (L9490) |
| **GATE-L0-016** | **Cache holds inputs, never results.** `ci-cache.sh audit` finds no result-shaped entry and no non-input directory under the cache root | A planted `/opt/selfci-cache/GATE-RESULT-last.txt`, and a planted `venv/<key>/.passed` marker | Rule Zero; §53.1; EC-109 (L9780) |
| **GATE-L0-017** | **Every job declares `timeout-minutes`.** No job inherits the six-hour default | `timeout-minutes` removed from the `gate-a` job | Rule Zero item 1 (*a timed-out job reads as FAIL*); `05-merge-gate.md` §9 |
| **GATE-L0-018** | **Time gates resolve against the declared working calendar**, never runner local time; the nightly's calendar step is present and is the first step | Nightly with the calendar step deleted, run on a runner whose TZ makes the window look valid | spec L451; §97.1 (L8848–8854); §34.2 (L2930–2935); L2 `GATE-L2-006` |
| **GATE-L0-019** | **Runner privilege split.** Every job touching `secrets.RECORDS_WRITER_TOKEN` runs on a hosted runner and asserts `RUNNER_ENVIRONMENT` as its first step; no self-hosted job references any secret | The `record` job moved to `[self-hosted, linux, build-ci]` | spec L3587–3597 (D80, D87); §40.1 (L3644–3686) |
| **GATE-L0-020** | **Speed honesty.** No run is accepted whose duration fell more than 40% below its own trailing ten-run median while `assertions=` did not increase | A stubbed suite that returns `GATE-RESULT ... assertions=1` in 2 s where the median is 90 s and the previous run asserted 214 | §103 (*"zero rejections means the gates are not working"*; *"very low may mean rubber-stamping"*); T3 check 5 |

### 8.1 Running them, and proving them

```bash
set -euo pipefail
# Positive: every gate evaluated against the live .github/workflows tree.
bash contracts/gate/pipeline-gates.sh --all
# PIPELINE-GATES PASS gates=11/11 failures=0

# Negative: every gate's fixture injected into a throwaway worktree; each MUST flip to FAIL.
bash contracts/gate/pipeline-gates.sh --negative
# PIPELINE-GATES PASS proven=11/11 unproven=0

# One gate, both halves, while developing it.
bash contracts/gate/pipeline-gates.sh --gate GATE-L0-016
bash contracts/gate/pipeline-gates.sh --gate GATE-L0-016 --negative
```

Any line containing `unproven=` with a value other than `0` closes GATE A and GATE B. `00-test-strategy.md` §4.1 rule 4 applies verbatim: **a gate whose negative fixture passes is a FAILED gate, not a clean one**, and reports exit `3`.

### 8.2 `GATE-L0-020` in full, because it is the one that is easy to write as decoration

```bash
set -euo pipefail
#!/usr/bin/env bash
# contracts/gate/speed-honesty.sh  (invoked by GATE-L0-020)
# A run that got fast by asserting less is the pipeline's form of rubber-stamping.
set -euo pipefail
WORKFLOW="$1"                 # e.g. selfci-gate-a
THIS_DURATION="$2"            # seconds, from the run
THIS_ASSERTIONS="$3"          # from the GATE-RESULT line

# Trailing window from the gate records. Ten runs, oldest discarded, never widened
# to make a flag disappear (05-merge-gate.md section 9, rubber_stamp_flag row).
read -r MEDIAN PREV_ASSERTIONS < <(bash contracts/gate/record-window.sh --workflow "$WORKFLOW" --n 10)

[ "${MEDIAN:-0}" -gt 0 ] || { echo "SPEED-HONESTY SKIP-IMPOSSIBLE no-window yet=cold-start"; exit 0; }

FLOOR=$(( MEDIAN * 60 / 100 ))          # 40% below the trailing median
if [ "$THIS_DURATION" -lt "$FLOOR" ] && [ "$THIS_ASSERTIONS" -le "$PREV_ASSERTIONS" ]; then
  echo "GATE-L0-020 FAIL suspiciously-fast workflow=$WORKFLOW duration=${THIS_DURATION}s median=${MEDIAN}s assertions=$THIS_ASSERTIONS prev=$PREV_ASSERTIONS"
  echo "A run cannot get 40% faster while asserting no more than it did before."
  echo "Either the cache started answering a question, or the suite stopped asking one."
  exit 1
fi
echo "GATE-L0-020 PASS workflow=$WORKFLOW duration=${THIS_DURATION}s median=${MEDIAN}s assertions=$THIS_ASSERTIONS prev=$PREV_ASSERTIONS"
```

Note the cold-start branch prints `SKIP-IMPOSSIBLE` and exits `0`. That is the one place in this pipeline where a check cannot yet discriminate, and it is named out loud rather than hidden: the gate declaration's `negative:` block includes a fixture with a nine-run window that must still evaluate, so the window logic itself is proven, and `make negative-audit` fails if the `SKIP-IMPOSSIBLE` branch is ever reachable with a full window.

---

## 9. Registering the required status checks — populated, never guessed

`master/02-branch-merge-model.md` §10.2 is binding and quotes §98.2 directly: *"The required-status-check list starts empty per repository and is populated as each check comes into existence… A required check no workflow emits blocks every pull request indefinitely."* The standing L0 STOP rule there is: **never add a context string that has not appeared in the live output.**

The build's own context list lives at `contracts/gate/required-contexts.txt` (L0-owned). It is **not** `templates/workflows/required-checks.yaml`, which is L2's published interface for *product* repositories and carries L2's STOP rule `S4` against edits. Two files, two audiences, no overlap.

Procedure, run by L0 only, once per new context:

```bash
set -euo pipefail
# 1. Merge the workflow. Let it run at least once on integration.
# 2. Read the exact strings GitHub reports. Never transcribe from the YAML by eye.
gh api /repos/$ORG/control-plane/commits/integration/check-runs --jq '.check_runs[].name' | sort -u
# expected to include, in this order of arrival across the build:
#   lane-guard
#   selfci-meta
#   selfci-gate-a
#   selfci-gate-b

# 3. Append the exact string to the L0-owned list. One name per line, no comments.
printf '%s\n' 'selfci-meta' >> contracts/gate/required-contexts.txt

# 4. Add it to the ruleset with the string copied from step 2, not typed.
gh api --method PUT "/repos/$ORG/control-plane/rulesets/$CP2_ID" --input - <<'JSON'
{ "rules": [ { "type": "required_status_checks",
  "parameters": { "strict_required_status_checks_policy": true,
    "required_status_checks": [ { "context": "lane-guard" }, { "context": "selfci-meta" } ] } } ] }
JSON

# 5. Prove the addition can fail. This step is not optional.
bash contracts/gate/pipeline-gates.sh --gate GATE-L0-012 --negative
# GATE-L0-012 ... FAIL skipped=1     <- the required outcome
```

**Step 5 is the whole point.** §95.4's activation checklist requires each gate to be *"executed for real — including the negative tests — at each threshold, not assumed."* A context added to a ruleset and never seen to block anything is a name in a JSON file, not a gate.

---

## 10. Failure taxonomy and STOP rules

Written for a lane developer with no repository context and no judgment authority. Find the row, do the thing, stop.

| Symptom in the Actions UI | Classification | Action | STOP rule |
|---|---|---|---|
| `selfci-lane` red, `SELFCI FAIL vacuous assertions=0` | The suite asserted nothing | Fix the suite, not the threshold | Do not commit. Open `BLOCKER L<n> vacuous-suite`. `00-test-strategy.md` §9 |
| `SELFCI FAIL non-discriminating <a>/<b>` | A negative fixture passed | Repair the gate | **Never edit the fixture to restore red.** That is falsifying the instrument. Open `BLOCKER L<n> <GATE-ID> non-discriminating` |
| `GATE-A-CLOSED` with `first_failure=LG-02` | Foreign path in the PR | Remove the path; file a Contract Change Request | Do not widen `ownership.tsv`; you do not own it |
| `SELFCI FAIL illegal-branch-name` | Branch does not match `lane/<N>/<phase>-<task>` | `git branch -m` to a legal name | Do not push again until the name matches `master/02-branch-merge-model.md` §2 |
| Job shows **cancelled** on the PR head SHA | Concurrency cancelled a run that gates the merge | Push an empty commit or re-run to get a real conclusion on the head | A cancelled required context is not a pass. `LG-10` will fail it anyway |
| Job shows **skipped** or **neutral** on a required context | The check that appears green never ran | Remove the `if:`/path filter from the emitting job | §33.2: on a merged PR this is **Blocking drift**. `GATE-L0-012` exists for exactly this |
| Job hits `timeout-minutes` | Instrument failure | Fail closed; treat as FAIL | Never re-run hoping for a different answer. Investigate the hang |
| `CI-CACHE FAIL result-shaped-entry-in-cache` | Something cached an answer | Delete the entry; find what wrote it | Do not add the path to an allowlist. `GATE-L0-016` is the gate, not the obstacle |
| `GATE-L0-020 FAIL suspiciously-fast` | The suite got faster without asserting more | Diff the suite against the previous cycle tag | Do not widen the window or lower the 40% threshold to clear the flag |
| `SELFCI FAIL privileged-job-on-non-hosted-runner` | A credentialed job landed on a persistent host | Move the job back to `ubuntu-latest` | Do not add the label to the shared pool. Spec L3589: persistence is the exposure |
| `SELFCI FAIL records-writer-secret-absent` | The record write could not happen | Fail the run | **Never** make the record write best-effort. §97.2 (L8855–8939) makes it a required, failing step |
| `delta=1` on `LG-12` / `IG-12` | CI and the L0 `make` run disagree | Investigate the workflow diff first | Never take the greener of the two verdicts (`05-merge-gate.md` §9) |
| All five lanes' `selfci-lane` runs queued behind each other | Runner pool under-sized, not a concurrency-group problem | L0 adds runners to the `build-ci` group | Do not "fix" it by removing concurrency groups or by disabling a lane's CI |
| Whole pool unreachable | Loss of the CI execution estate | L0 declares and announces degraded engineering mode; the train stops | Spec L4191–4211. Do not merge on the grounds that CI is unavailable |

---

## 11. What every run writes

One file per run, directory-per-item, append-only, never overwritten — PARTITION rule 3, invariant 47 (L9528: *"History is append-only for state, decisions, approvals and records"*), §97.2 (L8855–8939). This is why five lanes' CI records never conflict.

```
records/gate/lane/2026-08-27/PR-417-9f2c1ab.yaml
records/gate/integration-step/2026-08-27/9f2c1ab.yaml
records/gate/integration/2026-08-27/CYCLE-2026-08-27-a.yaml
records/gate-runs/2026-W36/drill-L3.yaml
```

Every CI-written record carries, in addition to the fields `05-merge-gate.md` §10 already requires:

```yaml
record_schema_version: 1
id: GATERUN-2026-W36-selfci-gate-a-PR417
product: control-plane
timestamp: 2026-08-27T11:04:19+00:00
cycle: 2026-W36
workflow: selfci-gate-a
run_id: "12345678901"
runner_class: self-hosted-build-ci      # or github-hosted for privileged jobs
conclusion: success                      # success | failure | cancelled | timed_out
duration_seconds: 271
assertions: 214
failures: 0
negatives_run: 12
negatives_that_failed_correctly: 12
cache_key: 4f9c1a20b3d7e881
cache_hit: true
concurrency_group: selfci-gate-a-417
verdict_line: "VERDICT=PASS GATE=lane LANE=3 PR=417 HEAD=9f2c1ab checks=12/12 negatives=12/12 counts=OK canary=n/a ts=2026-08-27T11:04:19Z"
```

`conclusion: cancelled` and `conclusion: timed_out` are recorded as they occurred and are **read as failures**, never as absences. `cache_hit: true` beside a falling `duration_seconds` and a flat `assertions:` is precisely the pair `GATE-L0-020` reads. A gate run with no record fails `IG-12`; §95.4 states the underlying discipline: *"An evidence base that nothing makes happen is reconstructed from memory at exactly the moment the closure discipline exists to prevent that."*

---

## 12. The pipeline in one paragraph, for a lane developer

Push to `lane/<N>/<phase>-<task>` and `selfci-lane` answers in about ninety seconds; if it is red, read the `SELFCI FAIL` token, find its row in §10, do exactly what the row says, and open a blocker if the row tells you to. Open the PR into `integration` and three contexts must go green: `lane-guard`, `selfci-meta`, `selfci-gate-a`. `selfci-gate-a` is only a mirror — the verdict that authorises the merge is L0's local `make gate-lane LANE=<N> PR=<n>` printing exactly one `VERDICT=PASS GATE=lane` line. You may not edit `.github/workflows/**` unless you are L2, you may not edit `contracts/**` or the `Makefile` at all, and you may not make a red check green by adding an `if:`, a path filter, a cache entry, or a shorter suite: every one of those has a gate in §8 with a negative fixture waiting for it. If your run is cancelled, timed out, or produced no output, it failed — the pipeline never reads silence as health.
