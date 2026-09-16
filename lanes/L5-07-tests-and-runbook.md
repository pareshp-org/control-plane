# L5-07 — Lane 5 Test Strategy and Daily Runbook

**Lane:** L5 Access, Infra & Ops — subsystems K, L, M, Q, R (spec Section 99.2).
**Owned paths (exclusive, per `implementation/PARTITION.md`):** `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**`.
**Repository:** `control-plane`. **Branch prefix:** `lane/5/*`. **Merge train position:** last (L1 → L4 → L2 → L3 → **L5**).
**Executor:** Sonnet-4.6-class AI developer, no repo context, no judgment authority — except where a task is marked **ASSISTED** or **HUMAN-GATED**, where the named human executes the privileged step.

This file contains two things and nothing else:

1. **The Lane 5 test strategy** — how access configuration is tested *negatively*, with the Phase 1 completion checks of spec Section 98.2 executed for real, plus the Section 100 acceptance tests this lane satisfies, each named by its real AT id.
2. **The Lane 5 daily runbook** — the literal daily command sequence, and the explicit rule for ASSISTED tasks where a human executes.

---

## 0. Shell contract (read before any task)

Every fenced-bash block in this file assumes:

* the shell is `bash` (Git Bash on Windows is supported; PowerShell is not);
* `CONTROL_PLANE_ROOT` is exported and points at the `control-plane` working copy root;
* `gh` (GitHub CLI) is installed and authenticated as the identity the task names;
* `jq`, `yq`, `git` and `curl` are on `PATH`.

Step 0 of every task is literally this block. Run it. If it prints `STOP`, do not proceed — open a blocker issue using the template in Section 8.

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT" || { echo "STOP: CONTROL_PLANE_ROOT path does not exist"; exit 1; }
for t in gh jq yq git curl; do
  command -v "$t" >/dev/null 2>&1 || { echo "STOP: missing tool $t"; exit 1; }
done
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "STOP: not a git repository"; exit 1; }
echo "SHELL-CONTRACT OK"
```

Expected output, exactly one line:

```
SHELL-CONTRACT OK
```

---

## 1. Execution modes — and the ASSISTED rule

Lane 5 is the only lane whose subject matter is *privilege*. A large part of it cannot be executed by an AI developer, because executing it requires holding organisation-owner authority, a second human GitHub account, a hardware security key, or shell on the operations VM. Pretending otherwise produces exactly the failure spec Section 11.1 names: a gate that appears to be working and is not.

Every Lane 5 task therefore carries exactly one **execution mode**.

| Mode | Who runs the privileged step | What the AI executor does | What the AI executor must never do |
| --- | --- | --- | --- |
| **AUTO** | Nobody — no privileged step exists | Writes the files, runs the commands, records the result | — |
| **ASSISTED** | A named human, at a terminal or in the GitHub UI | Writes the test, emits a **human-action card**, halts, then verifies the returned evidence file mechanically | Perform the privileged step; simulate it; mark the test passed from a dry run; edit or author the evidence file |
| **HUMAN-GATED** | The L0 human lead only | Nothing but open the blocker issue | Any part of the task |

### 1.1 The ASSISTED rule, stated in full and binding

> **An ASSISTED task is complete only when a human-produced evidence file exists, is signed by the executing human's GitHub login, and passes `access/tests/lib/verify-evidence.sh`. The AI executor writes the test and the card; it never writes the evidence.**

Mechanics, in order, no deviation:

1. The AI executor writes the test script into its owned path and commits it.
2. The AI executor generates a **human-action card** at `access/tests/human-actions/<TASK-ID>-<CHECK-ID>.md` from the template in Section 1.2 and commits it.
3. The AI executor prints `ASSISTED-HALT <TASK-ID> <CHECK-ID>` and **stops the task there**. It opens no PR beyond the one carrying the test and the card.
4. The named human performs the step and writes `access/tests/evidence/<CHECK-ID>-<UTC-DATE>.json` by hand (or by the recorder script the card names), with the fields of Section 1.3.
5. On the next lane cycle, the AI executor runs `access/tests/lib/verify-evidence.sh <CHECK-ID>`. Only a `PASS` line completes the task.

Corollaries, each binding:

* **A dry run is not evidence.** If the test script can be run with `--dry-run`, its output is `DRY-RUN` and is never accepted by the verifier.
* **A missing evidence file is not a failure of the test; it is an incomplete task.** The executor reports `INCOMPLETE`, never `FAIL`, and never proceeds to a dependent task.
* **The human's login must differ from the machine identity that committed the test.** `verify-evidence.sh` enforces this; a match is `FAIL`, not `PASS`.
* **Evidence expires.** Any evidence file whose `executed_at` is older than its declared `revalidate_after_days` is stale and the check reverts to `INCOMPLETE`.

### 1.2 Human-action card template

```markdown
# HUMAN ACTION REQUIRED — <TASK-ID> / <CHECK-ID>

**Executor:** <role: Founder | organisation Owner | DevOps-capability holder>
**Why a human:** <one line: the privilege the step requires>
**Spec clause:** <Section n.n, verbatim quote of the clause being tested>
**Expected result:** <the negative or positive outcome that constitutes a pass>

## Steps
1. <literal step>
2. <literal step>

## Record the result
Run:
    bash access/tests/lib/record-evidence.sh <CHECK-ID> <pass|fail> "<observed>"
Then commit the produced file under access/tests/evidence/ on branch lane/5/07-evidence.
```

### 1.3 Evidence file schema (`access/tests/evidence/<CHECK-ID>-<UTC-DATE>.json`)

| Field | Type | Rule |
| --- | --- | --- |
| `check_id` | string | Matches the filename prefix and a row in `access/tests/coverage.yaml` |
| `result` | enum | `pass` or `fail` — no third value |
| `executed_by` | string | GitHub login of the human who performed the step |
| `executed_at` | string | UTC ISO-8601, seconds precision |
| `observed` | string | What actually happened, in the human's words |
| `spec_clause` | string | The Section reference the card quoted |
| `revalidate_after_days` | integer | From the coverage manifest row |

---

## 2. Preconditions produced by other Lane 5 files

This file writes tests; it does not write the configuration under test. Each precondition below is an artifact another Lane 5 file produces inside a Lane-5-owned path. Every task naming a precondition begins by running its check command; a non-zero exit is a **STOP**, not a workaround.

| ID | Artifact that must exist | Check command | Subsystem |
| --- | --- | --- | --- |
| PRE-A | `access/branch-protection/control-plane.yaml` | `test -f access/branch-protection/control-plane.yaml` | L |
| PRE-B | `access/codeowners/generate-codeowners.sh` | `test -x access/codeowners/generate-codeowners.sh` | L |
| PRE-C | `access/permission-model/teams.yaml` | `test -f access/permission-model/teams.yaml` | L |
| PRE-D | `access/secret-tiers/tiers.yaml` | `test -f access/secret-tiers/tiers.yaml` | L |
| PRE-E | `ops-vm/grafana/shared/provisioning/datasources/` | `test -d ops-vm/grafana/shared/provisioning/datasources` | L, M |
| PRE-F | `ops-vm/grafana/founder/provisioning/datasources/` | `test -d ops-vm/grafana/founder/provisioning/datasources` | L, M |
| PRE-G | `infra/hermes/background-worker.yaml` | `test -f infra/hermes/background-worker.yaml` | K |
| PRE-H | `infra/hermes/ops-console.yaml` | `test -f infra/hermes/ops-console.yaml` | K |
| PRE-I | `infra/egress/background-host-allowlist.conf` | `test -f infra/egress/background-host-allowlist.conf` | K |
| PRE-J | `infra/systemd/background-window-stop.service` | `test -f infra/systemd/background-window-stop.service` | K |
| PRE-K | `assets/inventory/` (one file per asset) | `test -d assets/inventory` | Q |
| PRE-L | `notify/routing/push-list.yaml` | `test -f notify/routing/push-list.yaml` | R |
| PRE-M | `access/ai-runtime/approved-runtimes.yaml` | `test -f access/ai-runtime/approved-runtimes.yaml` | K |
| PRE-N | `ops-vm/org-export/export.sh` | `test -x ops-vm/org-export/export.sh` | M |

Out-of-lane dependencies, named so the executor never reaches for them:

| ID | Artifact | Owner | Rule |
| --- | --- | --- | --- |
| EXT-1 | `validators/registry/exceptions.py` (or equivalent entrypoint) | **L1** | Lane 5 invokes it; Lane 5 never edits it |
| EXT-2 | The reconciler credential and `reconciler/**` | **L3** | Lane 5 supplies the bounding test harness only (`AT-110/static`); L3 owns the live verdict (`AT-110/live`) |
| EXT-3 | `control-plane-records` repository rulesets | **L4** | Lane 5 asserts nothing there; PARTITION gives L4 all of that repository |
| EXT-4 | `.github/workflows/**` | **L2** | Lane 5 reads workflow files in tests; Lane 5 never writes them |

---

## 3. Test strategy

### 3.1 The doctrine: every access control is proved by its refusal

Three rules govern every test in this lane.

1. **A control is untested until it has refused something.** Spec Section 11.1 states the failure mode in terms: a Cross-Reviewer holding only Read can submit a review that *visually reads as an approval* and does not satisfy branch protection. A test that only shows the happy path cannot tell an armed gate from an unarmed one. Every check in Section 3.2 that can be phrased negatively is phrased negatively, and each negative check is paired with exactly one positive control so that a uniformly broken environment cannot pass by refusing everything.
2. **Fail-closed, and say which.** Invariant 80 requires every control to be explicitly classified fail-closed or fail-open. Every test script in this lane exits non-zero on any condition it cannot evaluate, and prints `INDETERMINATE` rather than `PASS`. A check that cannot reach its subject fails; it never reports zero findings (the same rule spec Section 40.1 applies to metric checks that cannot reach the records repository).
3. **Executed, not asserted.** Spec Section 98.2's Phase 1 completion check ends the Read-only clause with "executed for real once headcount permits, per the activation checklist" and the machine-account clause with "the check is executed negatively". AT-110 states the principle generally: "The system's most privileged identity (Section 99.6, risk 6) is the one whose boundary must be executed rather than asserted." Nothing in this lane is marked complete from a configuration file that *says* the right thing.

### 3.2 The Phase 1 negative-check matrix — spec Section 98.2, executed

Thirteen checks. Each maps to a literal clause of the Phase 1 completion check of Section 98.2, or to the two-humans-with-Write row of the activation checklist in Section 95.4. `Revalidate` is the standing re-execution interval; the check reverts to `INCOMPLETE` when its evidence ages past it.

| ID | Clause tested (spec) | Shape | Mode | Revalidate |
| --- | --- | --- | --- | --- |
| NC-01 | "no direct human push to any default branch succeeds on the control-plane repository" (98.2) | Negative | ASSISTED | 90 d |
| NC-02 | "A self-approved PR fails branch protection" (95.4, 2-humans row; invariant 9; 11.3 most-recent-push rule) | **Negative** | ASSISTED | 90 d |
| NC-03 | "an approval from a Read-only account does **not** satisfy branch protection" (98.2; 11.1) | **Negative** | ASSISTED | 90 d |
| NC-04 | "an approval from a Write-holding Cross-Reviewer does" (98.2) — the positive control for NC-03 | Positive | ASSISTED | 90 d |
| NC-05 | "an approval from a machine account does **not** satisfy branch protection — CODEOWNERS is generated to contain human identities only, and the check is executed negatively" (98.2; 11.3) | **Negative** | ASSISTED (live) + AUTO (static) | 90 d |
| NC-06 | "the reconciler credential's declared repair scope (Section 26.4) is the **only** machine write path admitted — the records-writer holds no credential on this repository at all" (98.2; 40.1, D89); PARTITION: "NO machine bypass actor (D89)" | **Negative** | ASSISTED | 90 d |
| NC-07 | "organisation-enforced 2FA is verified active, with hardware keys or passkeys for the Founder, organisation Owners and platform-admin holders" (98.2; 11.2) | Positive | ASSISTED | 90 d |
| NC-08 | "no API key present anywhere" (98.2); `env \| grep -i api_key` returns empty including shell profiles and repository `.env` files (40.2, 36.6); invariant 84 | **Negative** | AUTO (per machine) + ASSISTED (fleet attestation) | 90 d |
| NC-09 | "the minimal `exceptions.yaml` schema validator (expiry, owner, deactivation trigger present) is active in control-plane CI and rejects a deliberately malformed exception" (98.2; invariant 77) | **Negative** | AUTO | 30 d |
| NC-10 | "Teams granting Write exist before branch protection is armed, so that no window opens in which no approval can satisfy the gate" (98.2; 11.2) | Ordering | ASSISTED | 90 d |
| NC-11 | "a workflow pushed to a non-default branch declaring `environment: production` obtains no environment secret, executed negatively" (98.2; 33.4, 11.3 deployment branch policy) | **Negative** | ASSISTED | 90 d |
| NC-12 | "a second organisation Owner or an escrowed break-glass Owner credential exists with a named escrow custodian" (98.2; 11.2; invariant 39; AT-022) | Positive | HUMAN-GATED | 90 d |
| NC-13 | "the organisation export's first run is scheduled in Phase 2, or its absence is recorded as a dated accepted risk (D80)" (98.2; SIG-34) | Either-or | AUTO | 30 d |

Two boundaries are stated once so no task crosses them:

* **NC-06 is scoped to the `control-plane` repository only.** The `control-plane-records` repository's no-bypass ruleset (D107) is L4's path per PARTITION and is verified by L4. Lane 5 asserts nothing about it.
* **NC-09 invokes L1's validator (EXT-1).** Lane 5 owns the malformed fixture and the assertion; it never edits the validator.

### 3.3 Acceptance-test coverage — real AT ids from spec Section 100

Only tests Lane 5's subsystems actually satisfy are listed. Each row names the test file Lane 5 produces and the task that produces it.

| AT id | Test (spec Section 100) | Subsystem | Test file (Lane-5-owned) | Task | Mode |
| --- | --- | --- | --- | --- | --- |
| AT-011 | AI provider changes | K | `access/tests/at-011-provider-swap.sh` | L5-07-13 | AUTO |
| AT-017 | A person leaves — the asset-owner leg only ("Asset owners participate in orphan detection", 49.1) | Q | `assets/tests/at-017-asset-owner-orphan.sh` | L5-07-11 | AUTO |
| AT-022 | Founder continuity activates — the break-glass Owner credential leg | L | `access/tests/at-022-breakglass-owner.sh` | L5-07-09 | HUMAN-GATED |
| AT-029 | The entire control plane is unreachable | M | `ops-vm/tests/at-029-control-plane-unreachable.sh` | L5-07-14 | ASSISTED |
| AT-035 | GitHub organisation export restores | M | `ops-vm/tests/at-035-org-export-restore.sh` | L5-07-14 | ASSISTED |
| AT-049 | `ai_runtime_dependency` evaluation enforcement | K | `access/tests/at-049-eval-suite-required.sh` | L5-07-13 | AUTO |
| AT-089 | Layer B is unreachable from general surfaces | L | `access/tests/at-089-096-layerb-reach.sh` | L5-07-10 | AUTO |
| AT-090 | Individual people intelligence is Founder-only | L | `access/tests/at-090-founder-only.sh` | L5-07-10 | AUTO + ASSISTED |
| AT-091 | The `people-intelligence` capability gates Layer B | L | `access/tests/at-091-capability-gate.sh` | L5-07-10 | AUTO |
| AT-092 | The Team Lead cannot reach the Founder people views | L | `access/tests/at-089-096-layerb-reach.sh` | L5-07-10 | AUTO |
| AT-096 | Employees cannot access each other's data | L | `access/tests/at-089-096-layerb-reach.sh` | L5-07-10 | AUTO |
| AT-097 | No people datasource in the shared Grafana instance | L, M | `ops-vm/tests/at-097-shared-no-people-ds.sh` | L5-07-08 | AUTO |
| AT-098 | The Founder-only instance is separately credentialed | L, M | `ops-vm/tests/at-098-founder-instance-cred.sh` | L5-07-08 | AUTO + ASSISTED |
| AT-100 | Conduct-protocol access separation | L | `access/tests/at-100-conduct-separation.sh` | L5-07-10 | AUTO |
| AT-106 | Gate 1 notification and turnaround — the push-event leg | R | `notify/tests/at-106-gate1-push.sh` | L5-07-12 | AUTO |
| AT-107 | A scheduled eval regression blocks pin adoption | K | `access/tests/at-107-eval-regression-blocks-pin.sh` | L5-07-13 | AUTO |
| AT-108 | The founder ops console is provably read-only | K, M | `ops-vm/tests/at-108-console-readonly.sh` | L5-07-06 | ASSISTED |
| AT-109 | The background cage egress wall holds | K | `infra/tests/at-109-egress-wall.sh` | L5-07-07 | ASSISTED |
| AT-110/static | The reconciler credential is provably bounded — static analysis, organisation structure checks (owned by L5) | L | `access/tests/at-110-reconciler-bounds.sh` | L5-07-09 | AUTO |
| AT-110/live | The reconciler credential is provably bounded — live system checks, credential probes (owned by L3) | L | `access/tests/at-110-reconciler-bounds.sh` | L5-07-09 | ASSISTED |

> **Note (§4.10):** Today two evidence registries both emit a PASS. After the split: L5 emits `AT-110/static` verdict, L3 emits `AT-110/live` verdict.

Explicitly **out of Lane 5's scope**, recorded so the executor does not attempt them: AT-093, AT-094, AT-095 and AT-099 are view-layer and people-engine tests (subsystems H and P), and AT-102 and AT-033 are reconciler tests (subsystem C, lane L3).

### 3.4 Invariants and signals the suite is answerable for

Lane 5's tests are the mechanical enforcement named by these invariants of spec Section 101: **9** (no self-approval), **18** (background layer cannot merge, approve, deploy or reach production credentials), **24**, **25**, **26** (workstation trust boundary), **77** (every exception has an expiry), **79** (minimum privilege by default), **80** (fail-closed classification), **84** (API keys absent from developer environments), **87** (platform-enforced where the platform can enforce), **106**, **107**, **108**, **109** (access and privacy).

Signals the suite feeds or verifies (spec Section 52.2): **SIG-03** permission drift, **SIG-13** failed reconciliations, **SIG-34** organisation export staleness, **SIG-36** control-plane patch staleness, **SIG-39** bootstrap exception unclosed, **SIG-42** AI-eval regression, **SIG-46** audit-log review staleness.

---

## 4. Tasks

Sizes: **S** under half a day, **M** half a day to two days, **L** two to five days, for the AI executor.

### L5-07-01 — Test harness skeleton and evidence machinery — S — AUTO

**Depends on:** none.
**Writes:** `access/tests/lib/assert.sh`, `access/tests/lib/verify-evidence.sh`, `access/tests/lib/record-evidence.sh`, `access/tests/lane5.sh`, `access/tests/evidence/.gitkeep`, `access/tests/human-actions/.gitkeep`.

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout -B lane/5/07-harness origin/integration
mkdir -p access/tests/lib access/tests/evidence access/tests/human-actions access/tests/fixtures
mkdir -p infra/tests ops-vm/tests notify/tests assets/tests
touch access/tests/evidence/.gitkeep access/tests/human-actions/.gitkeep

cat > access/tests/lib/assert.sh <<'SH'
#!/usr/bin/env bash
# Lane 5 assertion library. Fail-closed: anything unevaluable is INDETERMINATE.
set -uo pipefail
L5_FAILURES=0
l5_pass()          { echo "PASS $1"; }
l5_fail()          { echo "FAIL $1 :: $2"; L5_FAILURES=$((L5_FAILURES+1)); }
l5_indeterminate() { echo "INDETERMINATE $1 :: $2"; L5_FAILURES=$((L5_FAILURES+1)); }
# l5_refuses ID DESC CMD... : passes only when CMD exits non-zero (the control refused)
l5_refuses() {
  local id="$1"; local desc="$2"; shift 2
  if "$@" >/dev/null 2>&1; then l5_fail "$id" "$desc was PERMITTED and must be refused"
  else l5_pass "$id"; fi
}
# l5_permits ID DESC CMD... : the paired positive control
l5_permits() {
  local id="$1"; local desc="$2"; shift 2
  if "$@" >/dev/null 2>&1; then l5_pass "$id"
  else l5_fail "$id" "$desc was REFUSED and must be permitted"; fi
}
l5_exit() { if [ "$L5_FAILURES" -eq 0 ]; then echo "SUITE OK"; exit 0; else echo "SUITE FAILURES=$L5_FAILURES"; exit 1; fi; }
SH

cat > access/tests/lib/record-evidence.sh <<'SH'
#!/usr/bin/env bash
# Run by a HUMAN only. Writes one evidence file. Never run by the AI executor.
set -euo pipefail
CHECK_ID="${1:?usage: record-evidence.sh CHECK_ID RESULT OBSERVED}"
RESULT="${2:?usage: record-evidence.sh CHECK_ID RESULT OBSERVED}"
OBSERVED="${3:?usage: record-evidence.sh CHECK_ID RESULT OBSERVED}"
case "$RESULT" in pass|fail) ;; *) echo "STOP: result must be pass or fail"; exit 1;; esac
WHO="$(gh api user --jq .login)"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DAY="$(date -u +%Y-%m-%d)"
CLAUSE="$(yq -r ".checks[] | select(.check_id == \"$CHECK_ID\") | .spec_clause" access/tests/coverage.yaml)"
REVAL="$(yq -r ".checks[] | select(.check_id == \"$CHECK_ID\") | .revalidate_after_days" access/tests/coverage.yaml)"
[ -n "$CLAUSE" ] && [ "$CLAUSE" != "null" ] || { echo "STOP: $CHECK_ID is not in access/tests/coverage.yaml"; exit 1; }
OUT="access/tests/evidence/${CHECK_ID}-${DAY}.json"
jq -n --arg c "$CHECK_ID" --arg r "$RESULT" --arg w "$WHO" --arg t "$NOW" \
      --arg o "$OBSERVED" --arg s "$CLAUSE" --argjson d "$REVAL" \
  '{check_id:$c,result:$r,executed_by:$w,executed_at:$t,observed:$o,spec_clause:$s,revalidate_after_days:$d}' > "$OUT"
echo "WROTE $OUT"
SH

cat > access/tests/lib/verify-evidence.sh <<'SH'
#!/usr/bin/env bash
# Verifies a human evidence file. AI executor runs this; it never writes evidence.
set -uo pipefail
CHECK_ID="${1:?usage: verify-evidence.sh CHECK_ID}"
F="$(ls -1 access/tests/evidence/${CHECK_ID}-*.json 2>/dev/null | sort | tail -n 1)"
[ -n "${F:-}" ] || { echo "INCOMPLETE $CHECK_ID :: no evidence file"; exit 2; }
for k in check_id result executed_by executed_at observed spec_clause revalidate_after_days; do
  v="$(jq -r --arg k "$k" '.[$k] // empty' "$F")"
  [ -n "$v" ] || { echo "FAIL $CHECK_ID :: evidence missing field $k"; exit 1; }
done
[ "$(jq -r .check_id "$F")" = "$CHECK_ID" ] || { echo "FAIL $CHECK_ID :: check_id mismatch"; exit 1; }
[ "$(jq -r .result "$F")" = "pass" ] || { echo "FAIL $CHECK_ID :: recorded result is not pass"; exit 1; }
HUMAN="$(jq -r .executed_by "$F")"
COMMITTER="$(git log -1 --format=%ae -- access/tests/ 2>/dev/null || echo unknown)"
case "$COMMITTER" in *"$HUMAN"*) echo "FAIL $CHECK_ID :: evidence author equals test committer"; exit 1;; esac
AGE_DAYS=$(( ( $(date -u +%s) - $(date -u -d "$(jq -r .executed_at "$F")" +%s) ) / 86400 ))
MAX="$(jq -r .revalidate_after_days "$F")"
[ "$AGE_DAYS" -le "$MAX" ] || { echo "INCOMPLETE $CHECK_ID :: evidence is ${AGE_DAYS}d old, limit ${MAX}d"; exit 2; }
echo "PASS $CHECK_ID"
SH

cat > access/tests/lane5.sh <<'SH'
#!/usr/bin/env bash
# Runs every Lane 5 test script in every Lane-5-owned path.
set -uo pipefail
RC=0
for d in access/tests infra/tests ops-vm/tests notify/tests assets/tests; do
  [ -d "$d" ] || continue
  for f in "$d"/*.sh; do
    [ -e "$f" ] || continue
    echo "--- $f"
    bash "$f" || RC=1
  done
done
if [ "$RC" -eq 0 ]; then echo "LANE5 SUITE OK"; else echo "LANE5 SUITE FAIL"; fi
exit "$RC"
SH

chmod +x access/tests/lib/*.sh access/tests/lane5.sh
git add access/tests infra/tests ops-vm/tests notify/tests assets/tests
git commit -m "L5-07-01: lane 5 test harness, evidence machinery and suite runner"
git push -u origin lane/5/07-harness
gh pr create --base integration --head lane/5/07-harness \
  --title "L5-07-01 lane 5 test harness" --body "Adds access/tests harness, evidence verifier and suite runner. Lane 5 paths only."
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | Harness files exist and are executable | `test -x access/tests/lane5.sh && test -x access/tests/lib/verify-evidence.sh && echo OK` | `OK` |
| 2 | Suite runs with zero tests and reports OK | `bash access/tests/lane5.sh \| tail -n 1` | `LANE5 SUITE OK` |
| 3 | Verifier returns INCOMPLETE for an absent evidence file | `bash access/tests/lib/verify-evidence.sh NC-99; echo "rc=$?"` | `INCOMPLETE NC-99 :: no evidence file` then `rc=2` |
| 4 | No file outside Lane 5 paths was touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^(access|infra|ops-vm|notify|assets)/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash access/tests/lane5.sh | tail -n 1
bash access/tests/lib/verify-evidence.sh NC-99; echo "rc=$?"
git diff --name-only origin/integration...HEAD | grep -Ev '^(access|infra|ops-vm|notify|assets)/' | wc -l
```

Expected output, exactly:

```
LANE5 SUITE OK
INCOMPLETE NC-99 :: no evidence file
rc=2
0
```

**STOP rule** — if criterion 4 prints anything other than `0`, do not push and do not open a PR: the lane-guard check will fail and the branch has touched a foreign path. Open a blocker issue (Section 8).

---

### L5-07-02 — The coverage manifest and its self-check — S — AUTO

**Depends on:** L5-07-01.
**Writes:** `access/tests/coverage.yaml`, `access/tests/check-coverage.sh`.

Every row is copied literally from Sections 3.2 and 3.3 of this file. The executor invents no row, no AT id and no clause.

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout -B lane/5/07-coverage origin/integration

cat > access/tests/coverage.yaml <<'YAML'
# Lane 5 test coverage manifest. Rows are copied from implementation/lanes/L5-07-tests-and-runbook.md.
# check_id : NC-* = Phase 1 completion checks (spec 98.2 / 95.4); AT-* = acceptance tests (spec 100)
checks:
  - {check_id: NC-01, spec_clause: "Section 98.2 Phase 1", test_file: access/tests/phase1/nc-01-no-direct-push.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: NC-02, spec_clause: "Section 95.4 two-humans row", test_file: access/tests/phase1/nc-02-self-approval.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: NC-03, spec_clause: "Section 98.2 Phase 1", test_file: access/tests/phase1/nc-03-readonly-approval.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: NC-04, spec_clause: "Section 98.2 Phase 1", test_file: access/tests/phase1/nc-04-write-approval.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: NC-05, spec_clause: "Section 98.2 Phase 1", test_file: access/tests/phase1/nc-05-machine-approval.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: NC-06, spec_clause: "Section 40.1 D89", test_file: access/tests/phase1/nc-06-no-bypass-actor.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: NC-07, spec_clause: "Section 11.2", test_file: access/tests/phase1/nc-07-2fa.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: NC-08, spec_clause: "Section 40.2 and 36.6", test_file: access/tests/phase1/nc-08-no-api-keys.sh, mode: AUTO, revalidate_after_days: 90}
  - {check_id: NC-09, spec_clause: "Section 98.2 Phase 1", test_file: access/tests/phase1/nc-09-malformed-exception.sh, mode: AUTO, revalidate_after_days: 30}
  - {check_id: NC-10, spec_clause: "Section 98.2 Phase 1", test_file: access/tests/phase1/nc-10-teams-before-protection.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: NC-11, spec_clause: "Section 33.4 and 98.2", test_file: access/tests/phase1/nc-11-env-secret-denied.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: NC-12, spec_clause: "Section 11.2 and AT-022", test_file: access/tests/at-022-breakglass-owner.sh, mode: HUMAN-GATED, revalidate_after_days: 90}
  - {check_id: NC-13, spec_clause: "Section 98.2 Phase 1 D80", test_file: access/tests/phase1/nc-13-org-export-scheduled.sh, mode: AUTO, revalidate_after_days: 30}
  - {check_id: AT-011, spec_clause: "Section 100.1", test_file: access/tests/at-011-provider-swap.sh, mode: AUTO, revalidate_after_days: 90}
  - {check_id: AT-017, spec_clause: "Section 49.1", test_file: assets/tests/at-017-asset-owner-orphan.sh, mode: AUTO, revalidate_after_days: 90}
  - {check_id: AT-022, spec_clause: "Section 100.2", test_file: access/tests/at-022-breakglass-owner.sh, mode: HUMAN-GATED, revalidate_after_days: 90}
  - {check_id: AT-029, spec_clause: "Section 100.3", test_file: ops-vm/tests/at-029-control-plane-unreachable.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: AT-035, spec_clause: "Section 100.3", test_file: ops-vm/tests/at-035-org-export-restore.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: AT-049, spec_clause: "Section 100.4", test_file: access/tests/at-049-eval-suite-required.sh, mode: AUTO, revalidate_after_days: 30}
  - {check_id: AT-089, spec_clause: "Section 100.6", test_file: access/tests/at-089-096-layerb-reach.sh, mode: AUTO, revalidate_after_days: 30}
  - {check_id: AT-090, spec_clause: "Section 100.6", test_file: access/tests/at-090-founder-only.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: AT-091, spec_clause: "Section 100.6", test_file: access/tests/at-091-capability-gate.sh, mode: AUTO, revalidate_after_days: 30}
  - {check_id: AT-092, spec_clause: "Section 100.6", test_file: access/tests/at-089-096-layerb-reach.sh, mode: AUTO, revalidate_after_days: 30}
  - {check_id: AT-096, spec_clause: "Section 100.6", test_file: access/tests/at-089-096-layerb-reach.sh, mode: AUTO, revalidate_after_days: 30}
  - {check_id: AT-097, spec_clause: "Section 100.6", test_file: ops-vm/tests/at-097-shared-no-people-ds.sh, mode: AUTO, revalidate_after_days: 30}
  - {check_id: AT-098, spec_clause: "Section 100.6", test_file: ops-vm/tests/at-098-founder-instance-cred.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: AT-100, spec_clause: "Section 100.6", test_file: access/tests/at-100-conduct-separation.sh, mode: AUTO, revalidate_after_days: 30}
  - {check_id: AT-106, spec_clause: "Section 100.4", test_file: notify/tests/at-106-gate1-push.sh, mode: AUTO, revalidate_after_days: 30}
  - {check_id: AT-107, spec_clause: "Section 100.4", test_file: access/tests/at-107-eval-regression-blocks-pin.sh, mode: AUTO, revalidate_after_days: 30}
  - {check_id: AT-108, spec_clause: "Section 100.6", test_file: ops-vm/tests/at-108-console-readonly.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: AT-109, spec_clause: "Section 100.6", test_file: infra/tests/at-109-egress-wall.sh, mode: ASSISTED, revalidate_after_days: 90}
  - {check_id: AT-110, spec_clause: "Section 100.6", test_file: access/tests/at-110-reconciler-bounds.sh, mode: ASSISTED, revalidate_after_days: 90}
YAML

cat > access/tests/check-coverage.sh <<'SH'
#!/usr/bin/env bash
# Fails when a manifest row names a missing test file, or when a Lane 5 test file
# is named by no manifest row. Fail-closed in both directions.
set -uo pipefail
RC=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  [ -f "$f" ] || { echo "FAIL coverage :: manifest names missing test file $f"; RC=1; }
done < <(yq -r '.checks[].test_file' access/tests/coverage.yaml | sort -u)
while IFS= read -r f; do
  case "$f" in */lib/*|*/lane5.sh|*/check-coverage.sh) continue;; esac
  yq -r '.checks[].test_file' access/tests/coverage.yaml | grep -qxF "$f" \
    || { echo "FAIL coverage :: test file $f is in no manifest row"; RC=1; }
done < <(find access/tests infra/tests ops-vm/tests notify/tests assets/tests -name '*.sh' 2>/dev/null | sort)
if [ "$RC" -eq 0 ]; then echo "COVERAGE OK"; else echo "COVERAGE FAIL"; fi
exit "$RC"
SH
chmod +x access/tests/check-coverage.sh
git add access/tests
git commit -m "L5-07-02: lane 5 coverage manifest and its self-check"
git push -u origin lane/5/07-coverage
gh pr create --base integration --head lane/5/07-coverage --title "L5-07-02 coverage manifest" --body "Maps every NC and AT id to its Lane-5-owned test file."
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | Manifest parses and has the expected row count | `yq -r '.checks \| length' access/tests/coverage.yaml` | `32` |
| 2 | All thirteen NC rows present | `yq -r '.checks[].check_id' access/tests/coverage.yaml \| grep -c '^NC-'` | `13` |
| 3 | Every AT id in the manifest exists in spec Section 100 | see SELF-VERIFY | `AT-IDS OK` |
| 4 | Only the three legal modes appear | `yq -r '.checks[].mode' access/tests/coverage.yaml \| sort -u \| tr '\n' ' '` | `ASSISTED AUTO HUMAN-GATED ` |

**SELF-VERIFY** (export `SPEC` to the absolute path of `MultiProduct_MasterSpec_v4.0.md` first)

```bash
set -euo pipefail
yq -r '.checks | length' access/tests/coverage.yaml
yq -r '.checks[].check_id' access/tests/coverage.yaml | grep -c '^NC-'
yq -r '.checks[].check_id' access/tests/coverage.yaml | grep '^AT-' | sort -u \
  | while read -r id; do grep -q "| $id |" "$SPEC" || { echo "BAD $id"; exit 1; }; done && echo "AT-IDS OK"
yq -r '.checks[].mode' access/tests/coverage.yaml | sort -u | tr '\n' ' '; echo
```

Expected output, exactly:

```
32
13
AT-IDS OK
ASSISTED AUTO HUMAN-GATED 
```

**STOP rule** — if any line prints `BAD AT-xxx`, an AT id was invented. Do not commit. Open a blocker issue naming the id.

---

### L5-07-03 — NC-08: the no-API-keys check, executed — S — AUTO

**Depends on:** L5-07-02.
**Writes:** `access/tests/phase1/nc-08-no-api-keys.sh`.
**Spec:** Section 98.2 Phase 1 ("no API key present anywhere"); Section 40.2 and Section 36.6 (`env | grep -i api_key` must return empty; shell profiles and repository `.env` files checked at onboarding and re-checked quarterly); invariant 84.

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout -B lane/5/07-nc08 origin/integration
mkdir -p access/tests/phase1

cat > access/tests/phase1/nc-08-no-api-keys.sh <<'SH'
#!/usr/bin/env bash
# NC-08 - spec 98.2 Phase 1, 40.2, 36.6, invariant 84.
# Negative check: nothing on this machine may present an API key.
# Scope: process environment, shell profiles, every .env under the working copy.
set -uo pipefail
. access/tests/lib/assert.sh

ENVHITS="$(env | grep -i 'api_key' || true)"
if [ -z "$ENVHITS" ]; then
  l5_pass "NC-08/env"
else
  l5_fail "NC-08/env" "environment presents: $(echo "$ENVHITS" | cut -d= -f1 | tr '\n' ' ')"
fi

PHITS=0
for p in .bashrc .bash_profile .profile .zshrc .zprofile .config/fish/config.fish; do
  f="$HOME/$p"
  [ -f "$f" ] || continue
  if grep -Eiq 'api[_-]?key' "$f"; then
    l5_fail "NC-08/profile" "$f references an api key"
    PHITS=1
  fi
done
[ "$PHITS" -eq 0 ] && l5_pass "NC-08/profiles"

EHITS=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  if grep -Eiq 'api[_-]?key' "$f"; then
    l5_fail "NC-08/dotenv" "$f references an api key"
    EHITS=1
  fi
done < <(find . -name '.env' -o -name '.env.*' 2>/dev/null | grep -v '/node_modules/')
[ "$EHITS" -eq 0 ] && l5_pass "NC-08/dotenv"

# Positive control. Spec 36.6: every Hermes instance points at the estate's own local
# inference endpoint and model.api_key carries a self-minted control-plane token,
# never a vendor API key. Spec 35.2: the only approved provider value is custom.
if [ -f infra/hermes/background-worker.yaml ]; then
  PROV="$(yq -r '.model.provider // ""' infra/hermes/background-worker.yaml)"
  if [ "$PROV" = "custom" ]; then
    l5_pass "NC-08/hermes-provider"
  else
    l5_fail "NC-08/hermes-provider" "model.provider is '$PROV'; spec 35.2 requires custom"
  fi
  BASE="$(yq -r '.model.base_url // ""' infra/hermes/background-worker.yaml)"
  case "$BASE" in
    http://*|https://*) l5_pass "NC-08/hermes-base-url" ;;
    *) l5_indeterminate "NC-08/hermes-base-url" "model.base_url is not set to the LAN endpoint" ;;
  esac
fi
l5_exit
SH
chmod +x access/tests/phase1/nc-08-no-api-keys.sh
bash access/tests/phase1/nc-08-no-api-keys.sh
git add access/tests/phase1/nc-08-no-api-keys.sh
git commit -m "L5-07-03: NC-08 no-API-keys check (spec 98.2, 40.2, 36.6, invariant 84)"
git push -u origin lane/5/07-nc08
gh pr create --base integration --head lane/5/07-nc08 --title "L5-07-03 NC-08 no-API-keys" --body "Phase 1 completion check, executed."
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | Script exists and is executable | `test -x access/tests/phase1/nc-08-no-api-keys.sh && echo OK` | `OK` |
| 2 | The check passes on this machine | `bash access/tests/phase1/nc-08-no-api-keys.sh \| tail -n 1` | `SUITE OK` |
| 3 | The check actually refuses a planted key | see SELF-VERIFY | `SUITE FAILURES=1` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash access/tests/phase1/nc-08-no-api-keys.sh | tail -n 1
env DEMO_API_KEY=planted bash access/tests/phase1/nc-08-no-api-keys.sh | tail -n 1
```

Expected output, exactly:

```
SUITE OK
SUITE FAILURES=1
```

**STOP rule** — if line 1 prints `SUITE FAILURES=n`, an API key is present on this machine. Do **not** delete it and do not proceed. Spec Section 40.1 makes a credential in the wrong tier a security incident under Section 43, not a cleanup task. Open a blocker issue immediately and stop the lane.

---

### L5-07-04 — NC-09 and NC-13: exception-validator negative, org-export schedule — S — AUTO

**Depends on:** L5-07-02. **Preconditions:** EXT-1, PRE-N.
**Writes:** `access/tests/fixtures/exception-malformed.yaml`, `access/tests/fixtures/exception-wellformed.yaml`, `access/tests/phase1/nc-09-malformed-exception.sh`, `access/tests/phase1/nc-13-org-export-scheduled.sh`.
**Spec:** Section 98.2 Phase 1; invariant 77 ("Every exception has an expiry; an exception without one is invalid and fails CI"); Section 54.2; D80; SIG-34.

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout -B lane/5/07-nc09-nc13 origin/integration
mkdir -p access/tests/phase1 access/tests/fixtures

cat > access/tests/fixtures/exception-malformed.yaml <<'YAML'
# Deliberately malformed: no expiry, no owner, no deactivation trigger.
# Spec 98.2 Phase 1 requires control-plane CI to REJECT this.
exceptions:
  - id: EXC-LANE5-FIXTURE-BAD
    scope: control-plane/branch-protection
    reason: fixture for NC-09
YAML

cat > access/tests/fixtures/exception-wellformed.yaml <<'YAML'
# Positive control for NC-09: expiry, owner and deactivation trigger all present.
exceptions:
  - id: EXC-LANE5-FIXTURE-GOOD
    scope: control-plane/branch-protection
    reason: fixture for NC-09 positive control
    owner: founder
    expires_on: 2099-12-31
    deactivation_trigger: two humans hold Write
YAML

cat > access/tests/phase1/nc-09-malformed-exception.sh <<'SH'
#!/usr/bin/env bash
# NC-09 - spec 98.2 Phase 1: the minimal exceptions.yaml schema validator (expiry,
# owner, deactivation trigger present) is active in control-plane CI and rejects a
# deliberately malformed exception. Invariant 77.
# The validator is L1-owned (EXT-1). This test invokes it and never edits it.
set -uo pipefail
. access/tests/lib/assert.sh
VAL="validators/registry/validate-exceptions.sh"
if [ ! -x "$VAL" ]; then
  l5_indeterminate "NC-09" "L1 validator $VAL absent or not executable"
  l5_exit
fi
l5_refuses "NC-09/negative" "malformed exception with no expiry, owner or trigger" "$VAL" access/tests/fixtures/exception-malformed.yaml
l5_permits "NC-09/positive" "well-formed exception" "$VAL" access/tests/fixtures/exception-wellformed.yaml
l5_exit
SH

cat > access/tests/phase1/nc-13-org-export-scheduled.sh <<'SH'
#!/usr/bin/env bash
# NC-13 - spec 98.2 Phase 1: the organisation export's first run is scheduled in
# Phase 2 via a systemd timer (L5-04 writes ops-vm/systemd/org-export.timer), OR
# its absence is recorded as a dated accepted risk (D80). Exactly one of the two
# must hold. Feeds SIG-34 (organisation export staleness).
# NOTE: ops-vm/org-export/schedule.yaml is never created by any task; L5-04 writes
# ops-vm/systemd/org-export.timer instead. When the export schedule is deliberately
# deferred, L5-02 or L5-04 should create access/accepted-risks/org-export-absent.yaml.
# SELF-VERIFY: create a non-empty ops-vm/systemd/org-export.timer → expect NC-13 PASS.
set -uo pipefail
. access/tests/lib/assert.sh
SCHED=0
RISK=0
# L5-04 writes the timer to ops-vm/systemd/org-export.timer (not org-export/schedule.yaml).
if [ -f ops-vm/systemd/org-export.timer ] && [ -s ops-vm/systemd/org-export.timer ]; then
  SCHED=1
fi
if [ -f access/accepted-risks/org-export-absent.yaml ]; then
  D2="$(yq -r '.review_on // ""' access/accepted-risks/org-export-absent.yaml)"
  O2="$(yq -r '.owner // ""' access/accepted-risks/org-export-absent.yaml)"
  case "$D2" in ????-??-??) [ -n "$O2" ] && RISK=1 ;; esac
fi
TOTAL=$((SCHED + RISK))
if [ "$TOTAL" -eq 1 ]; then
  l5_pass "NC-13"
elif [ "$TOTAL" -eq 0 ]; then
  l5_fail "NC-13" "neither ops-vm/systemd/org-export.timer nor a dated owned accepted risk exists"
else
  l5_fail "NC-13" "both a scheduled export (timer) and an accepted risk for its absence exist"
fi
l5_exit
SH
chmod +x access/tests/phase1/nc-09-malformed-exception.sh access/tests/phase1/nc-13-org-export-scheduled.sh
bash access/tests/phase1/nc-09-malformed-exception.sh
bash access/tests/phase1/nc-13-org-export-scheduled.sh
git add access/tests
git commit -m "L5-07-04: NC-09 malformed-exception negative and NC-13 org-export schedule check"
git push -u origin lane/5/07-nc09-nc13
gh pr create --base integration --head lane/5/07-nc09-nc13 --title "L5-07-04 NC-09 and NC-13" --body "Phase 1 completion checks, executed."
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | Both fixtures exist | `test -f access/tests/fixtures/exception-malformed.yaml && test -f access/tests/fixtures/exception-wellformed.yaml && echo OK` | `OK` |
| 2 | NC-09 refuses the malformed fixture and permits the well-formed one | `bash access/tests/phase1/nc-09-malformed-exception.sh \| tail -n 1` | `SUITE OK` |
| 3 | NC-13 resolves to exactly one branch | `bash access/tests/phase1/nc-13-org-export-scheduled.sh \| head -n 1` | `PASS NC-13` |
| 4 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^(access|infra|ops-vm|notify|assets)/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash access/tests/phase1/nc-09-malformed-exception.sh | tail -n 1
bash access/tests/phase1/nc-13-org-export-scheduled.sh | tail -n 1
git diff --name-only origin/integration...HEAD | grep -Ev '^(access|infra|ops-vm|notify|assets)/' | wc -l
```

Expected output, exactly:

```
SUITE OK
SUITE OK
0
```

**STOP rule** — if NC-09 prints `FAIL NC-09/negative`, the malformed exception was **accepted** and invariant 77 is unenforced. Do not "fix" the fixture, and do not edit `validators/**` — that is L1's path under PARTITION. Open a blocker issue against L1 and stop.

---

### L5-07-05 — NC-01..NC-07, NC-10, NC-11: the live branch-protection negatives — L — ASSISTED

**Depends on:** L5-07-02. **Preconditions:** PRE-A, PRE-B, PRE-C.
**Writes:** `access/tests/phase1/nc-01-no-direct-push.sh`, `nc-02-self-approval.sh`, `nc-03-readonly-approval.sh`, `nc-04-write-approval.sh`, `nc-05-machine-approval.sh`, `nc-06-no-bypass-actor.sh`, `nc-07-2fa.sh`, `nc-10-teams-before-protection.sh`, `nc-11-env-secret-denied.sh`, and one human-action card per check under `access/tests/human-actions/`.

These nine checks require organisation-owner authority and, for NC-02/03/04, two distinct human GitHub accounts. **The AI executor writes the scripts and the cards and stops.** See Section 1.1. The static, machine-runnable halves of NC-05 and NC-06 run now; their live halves are ASSISTED.

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout -B lane/5/07-phase1-live origin/integration
mkdir -p access/tests/phase1 access/tests/human-actions

cat > access/tests/phase1/nc-05-machine-approval.sh <<'SH'
#!/usr/bin/env bash
# NC-05 - spec 98.2 Phase 1 and 11.3: an approval from a machine account does NOT
# satisfy branch protection, because CODEOWNERS is generated to contain human
# identities only. Static half runs here; the live negative is ASSISTED.
set -uo pipefail
. access/tests/lib/assert.sh
if [ ! -x access/codeowners/generate-codeowners.sh ]; then
  l5_indeterminate "NC-05/static" "PRE-B missing: access/codeowners/generate-codeowners.sh"
  l5_exit
fi
OUT="$(mktemp)"
if ! bash access/codeowners/generate-codeowners.sh > "$OUT" 2>/dev/null; then
  l5_indeterminate "NC-05/static" "CODEOWNERS generator exited non-zero"
  l5_exit
fi
MACHINES="$(yq -r '.machine_accounts[]? // empty' access/permission-model/teams.yaml 2>/dev/null)"
if [ -z "$MACHINES" ]; then
  l5_indeterminate "NC-05/static" "teams.yaml declares no machine_accounts list"
  l5_exit
fi
HIT=0
for m in $MACHINES; do
  if grep -qF "$m" "$OUT"; then
    l5_fail "NC-05/static" "generated CODEOWNERS contains machine identity $m"
    HIT=1
  fi
done
[ "$HIT" -eq 0 ] && l5_pass "NC-05/static"
bash access/tests/lib/verify-evidence.sh NC-05 || true
l5_exit
SH

cat > access/tests/phase1/nc-06-no-bypass-actor.sh <<'SH'
#!/usr/bin/env bash
# NC-06 - spec 40.1 (D89) and PARTITION: the control-plane repository has NO machine
# bypass actor, and the records-writer holds no credential on it at all. The reconciler
# credential's declared repair scope (26.4) is the only machine write path admitted.
# Scope note: control-plane-records is L4-owned and is NOT asserted here.
set -uo pipefail
. access/tests/lib/assert.sh
REPO="$(yq -r '.control_plane_repo // ""' access/permission-model/teams.yaml 2>/dev/null)"
if [ -z "$REPO" ]; then
  l5_indeterminate "NC-06" "teams.yaml declares no control_plane_repo"
  l5_exit
fi
if ! RULESETS="$(gh api "repos/$REPO/rulesets" 2>/dev/null)"; then
  echo "NC-06 INDETERMINATE: cannot reach repos/$REPO/rulesets"
  exit 2
fi
BYPASS=0
for id in $(echo "$RULESETS" | jq -r '.[].id'); do
  N="$(gh api "repos/$REPO/rulesets/$id" --jq '.bypass_actors | length' 2>/dev/null || echo 0)"
  if [ "$N" -gt 0 ]; then
    l5_fail "NC-06" "ruleset $id declares $N bypass actor(s) on the control-plane repository"
    BYPASS=1
  fi
done
[ "$BYPASS" -eq 0 ] && l5_pass "NC-06/no-bypass-actor"
bash access/tests/lib/verify-evidence.sh NC-06 || true
l5_exit
SH

for pair in "nc-01-no-direct-push NC-01" "nc-02-self-approval NC-02" "nc-03-readonly-approval NC-03" \
            "nc-04-write-approval NC-04" "nc-07-2fa NC-07" "nc-10-teams-before-protection NC-10" \
            "nc-11-env-secret-denied NC-11"; do
  FILE="$(echo "$pair" | cut -d' ' -f1)"
  CHECK="$(echo "$pair" | cut -d' ' -f2)"
  cat > "access/tests/phase1/$FILE.sh" <<SH
#!/usr/bin/env bash
# $CHECK - ASSISTED. The privileged step is performed by a named human; this script
# verifies only the returned evidence file. See L5-07 Section 1.1.
set -uo pipefail
. access/tests/lib/assert.sh
bash access/tests/lib/verify-evidence.sh $CHECK
RC=\$?
if [ "\$RC" -eq 0 ]; then
  l5_pass "$CHECK"
elif [ "\$RC" -eq 2 ]; then
  echo "INCOMPLETE $CHECK :: awaiting human evidence"
  exit 2
else
  l5_fail "$CHECK" "evidence verification failed"
fi
l5_exit
SH
done
chmod +x access/tests/phase1/*.sh
git add access/tests/phase1 access/tests/human-actions
git commit -m "L5-07-05: Phase 1 live negative checks NC-01..NC-07, NC-10, NC-11"
git push -u origin lane/5/07-phase1-live
gh pr create --base integration --head lane/5/07-phase1-live --title "L5-07-05 Phase 1 live negatives" --body "Scripts and human-action cards. Live execution is ASSISTED."
echo "ASSISTED-HALT L5-07-05 NC-01,NC-02,NC-03,NC-04,NC-05,NC-06,NC-07,NC-10,NC-11"
```

**The nine human-action cards.** Each is written into `access/tests/human-actions/L5-07-05-<CHECK>.md` using the Section 1.2 template, with the row below copied verbatim into Steps and Expected result. The executor copies; it does not compose.

| Check | Human | Steps (literal) | Pass condition |
| --- | --- | --- | --- |
| NC-01 | organisation Owner | On the control-plane repository, run `git push origin HEAD:main` from a human account holding Write | The push is **rejected** by branch protection (Section 98.2) |
| NC-02 | Human A (Write) | Human A opens a PR; Human A approves their own PR; Human A attempts merge | Merge is **blocked** — most-recent-push approval refuses the author's own approval (11.3; invariant 9; 95.4) |
| NC-03 | Human A (Write) + Human B (**Read only**) | Human A opens a PR; Human B submits an approving review; attempt merge | Merge stays **blocked** — a Read approval does not count (11.1) |
| NC-04 | Human A (Write) + Human B (Write, Cross-Reviewer) | Same PR; Human B, now holding Write, approves | Merge becomes **permitted** — the paired positive control for NC-03 |
| NC-05 (live) | organisation Owner | Have the machine account submit an approving review on a PR whose CODEOWNERS path applies | Merge stays **blocked**; the required Code Owner review is unsatisfied (11.3) |
| NC-06 (live) | organisation Owner | Attempt a push to the control-plane default branch using the records-writer credential | **Rejected** — and the credential must not be installed on this repository at all (40.1, D89) |
| NC-07 | organisation Owner | Read organisation security settings; list Owners and platform-admin holders with their second factor | 2FA enforcement **active**; each listed identity uses a hardware key or passkey (11.2) |
| NC-10 | organisation Owner | Compare the creation timestamp of the Write-granting Teams with the branch-protection arming timestamp | Teams timestamp is **earlier** (98.2: no window opens in which no approval can satisfy the gate) |
| NC-11 | organisation Owner | Push a workflow declaring `environment: production` to a **non-default** branch and run it | The run obtains **no** environment secret (33.4 deployment branch policy) |

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | Nine cards exist | `ls access/tests/human-actions/L5-07-05-*.md \| wc -l` | `9` |
| 2 | Eleven Phase 1 NC scripts exist (nine here plus NC-08, NC-09, NC-13 from T03/T04 gives twelve) | `ls access/tests/phase1/nc-*.sh \| wc -l` | `12` |
| 3 | Every ASSISTED check reports INCOMPLETE before evidence, never PASS | `bash access/tests/phase1/nc-02-self-approval.sh; echo "rc=$?"` | `INCOMPLETE NC-02 :: awaiting human evidence` then `rc=2` |
| 4 | The static half of NC-05 passes | `bash access/tests/phase1/nc-05-machine-approval.sh \| head -n 1` | `PASS NC-05/static` |
| 5 | NC-06 finds zero bypass actors | `bash access/tests/phase1/nc-06-no-bypass-actor.sh \| head -n 1` | `PASS NC-06/no-bypass-actor` |

**SELF-VERIFY**

```bash
set -euo pipefail
ls access/tests/human-actions/L5-07-05-*.md | wc -l
ls access/tests/phase1/nc-*.sh | wc -l
bash access/tests/phase1/nc-02-self-approval.sh; echo "rc=$?"
bash access/tests/phase1/nc-05-machine-approval.sh | head -n 1
bash access/tests/phase1/nc-06-no-bypass-actor.sh | head -n 1
```

Expected output, exactly:

```
9
12
INCOMPLETE NC-02 :: awaiting human evidence
rc=2
PASS NC-05/static
PASS NC-06/no-bypass-actor
```

**SELF-VERIFY negative — API failure must produce INDETERMINATE (exit 2), never PASS**

```bash
set -euo pipefail
# Stub 'gh' and 'yq' so nc-06 reaches the API call with a known repo, then fails.
TMPBIN=$(mktemp -d)
TMPWORK=$(mktemp -d)
printf '#!/usr/bin/env sh\nexit 1\n' > "$TMPBIN/gh"; chmod +x "$TMPBIN/gh"
printf '#!/usr/bin/env sh\necho "org/ctrl-plane"\n' > "$TMPBIN/yq"; chmod +x "$TMPBIN/yq"
mkdir -p "$TMPWORK/access/permission-model" "$TMPWORK/access/tests/lib"
printf 'control_plane_repo: org/ctrl-plane\n' > "$TMPWORK/access/permission-model/teams.yaml"
# Minimal assert.sh stubs — nc-06 hits exit 2 before any l5_* call in the API-fail path.
printf 'l5_pass() { echo "PASS $*"; }\nl5_fail() { echo "FAIL $*"; exit 1; }\n' \
  > "$TMPWORK/access/tests/lib/assert.sh"
printf 'l5_indeterminate() { echo "INDET $*"; }\nl5_exit() { exit 0; }\n' \
  >> "$TMPWORK/access/tests/lib/assert.sh"
printf 'verify_evidence() { return 0; }\n' >> "$TMPWORK/access/tests/lib/assert.sh"
cp access/tests/phase1/nc-06-no-bypass-actor.sh "$TMPWORK/"
NC6_RC=0
NC6_OUT=$(cd "$TMPWORK" && PATH="$TMPBIN:$PATH" bash nc-06-no-bypass-actor.sh 2>&1) || NC6_RC=$?
rm -rf "$TMPBIN" "$TMPWORK"
printf 'nc06-api-fail=[msg=%s rc=%s]\n' "$(printf '%s' "$NC6_OUT" | head -1)" "$NC6_RC"
```

Expected output:

```
nc06-api-fail=[msg=NC-06 INDETERMINATE: cannot reach repos/org/ctrl-plane/rulesets rc=2]
```

**STOP rule** — if `rc=0` or the message contains `PASS`, the API-error path is returning a false pass. The `|| echo '[]'` bypass form must be replaced with the `if ! RULESETS=...` fail-closed form above.

**STOP rules**

* `FAIL NC-05/static` — the CODEOWNERS generator emits a machine identity, which Section 11.3 forbids. Do not hand-edit CODEOWNERS. Open a blocker issue against the L5 file owning `access/codeowners/**` and stop.
* `FAIL NC-06` — a bypass actor exists on the control-plane repository, contradicting PARTITION ("NO machine bypass actor (D89)") and Section 40.1. Remediation is HUMAN-GATED. Open a blocker issue at Blocking severity and stop the lane.
* The AI executor may under no circumstance create a GitHub account, elevate a Team, change a repository role, or perform any step in the card table.

---

### L5-07-06 — AT-108: the founder ops console is provably read-only — M — ASSISTED

**Depends on:** L5-07-02. **Preconditions:** PRE-H.
**Writes:** `ops-vm/tests/at-108-console-readonly.sh`, `access/tests/human-actions/L5-07-06-AT-108.md`.
**Spec:** AT-108 (Section 100.6) — "From the ops console's own OS user and credentials, four attempts are made — a control-plane write, a `records/` write, a board mutation, and any Layer B access — and all four fail; the console then still answers a read query over Layer A operational data correctly. Hermes proposes; the platform disposes (D69, D71)." Section 37.8 (cage configuration contract, Priority P0); Section 49.1 (the ops-console VPS holds a Layer A read-only credential only).

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout -B lane/5/07-at108 origin/integration
mkdir -p ops-vm/tests access/tests/human-actions

cat > ops-vm/tests/at-108-console-readonly.sh <<'SH'
#!/usr/bin/env bash
# AT-108 - spec 100.6. Static half asserts the spec 37.8 cage keys; the live half
# (four refusals plus one positive control) is ASSISTED and must run from the ops
# console's own OS user and credentials on the ops-console VPS.
set -uo pipefail
. access/tests/lib/assert.sh
CFG=infra/hermes/ops-console.yaml
if [ ! -f "$CFG" ]; then
  l5_indeterminate "AT-108/static" "PRE-H missing: $CFG"
  l5_exit
fi
chk() {
  local key="$1" want="$2" got
  got="$(yq -r "$key // \"\"" "$CFG")"
  if [ "$got" = "$want" ]; then l5_pass "AT-108/static$key"; else l5_fail "AT-108/static$key" "expected $want, got '$got'"; fi
}
chk '.memory.memory_enabled' 'false'
chk '.model.background_review.enabled' 'false'
chk '.approvals.cron_mode' 'deny'
chk '.security.allow_lazy_installs' 'false'
chk '.gateway.unauthorized_dm_behavior' 'ignore'
ALLOW="$(yq -r '.gateway.sender_allowlist | length' "$CFG" 2>/dev/null || echo 0)"
if [ "$ALLOW" -ge 1 ]; then l5_pass "AT-108/static-allowlist"; else l5_fail "AT-108/static-allowlist" "sender allowlist is empty"; fi
HOME_DIR="$(yq -r '.hermes_home // ""' "$CFG")"
OS_USER="$(yq -r '.os_user // ""' "$CFG")"
if [ -n "$HOME_DIR" ] && [ -n "$OS_USER" ]; then
  l5_pass "AT-108/static-isolation"
else
  l5_fail "AT-108/static-isolation" "instance declares no separate os_user and HERMES_HOME (spec 37.8)"
fi
bash access/tests/lib/verify-evidence.sh AT-108
RC=$?
if [ "$RC" -eq 2 ]; then echo "INCOMPLETE AT-108 :: awaiting human evidence"; exit 2; fi
if [ "$RC" -eq 0 ]; then l5_pass "AT-108/live"; else l5_fail "AT-108/live" "evidence verification failed"; fi
l5_exit
SH
chmod +x ops-vm/tests/at-108-console-readonly.sh
bash ops-vm/tests/at-108-console-readonly.sh
git add ops-vm/tests access/tests/human-actions
git commit -m "L5-07-06: AT-108 founder ops console read-only test"
git push -u origin lane/5/07-at108
gh pr create --base integration --head lane/5/07-at108 --title "L5-07-06 AT-108" --body "Static cage assertions plus the human-action card for the four refusals."
echo "ASSISTED-HALT L5-07-06 AT-108"
```

**Human-action card content — copied verbatim into `access/tests/human-actions/L5-07-06-AT-108.md`.** Executor: the DevOps-capability holder, from the console's own OS user.

| # | Attempt | Required outcome |
| --- | --- | --- |
| 1 | Control-plane write: an empty commit and push to the control-plane repository | **Refused** |
| 2 | `records/` write: an empty commit and push to the records repository | **Refused** |
| 3 | Board mutation: edit any Project item field via `gh project item-edit` | **Refused** |
| 4 | Layer B access: request the Founder-only Grafana instance's `/api/datasources` | **Refused** (non-2xx) |
| 5 | Positive control: ask the console one Layer A operational question (open drift count for a named product) | **Answered correctly**, with a link back to the authoritative surface |

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | All seven static assertions pass | `bash ops-vm/tests/at-108-console-readonly.sh \| grep -c '^PASS AT-108/static'` | `7` |
| 2 | The live half is INCOMPLETE, never PASS, before evidence | `bash ops-vm/tests/at-108-console-readonly.sh >/dev/null 2>&1; echo "rc=$?"` | `rc=2` |
| 3 | The card lists all five attempts | `grep -c '^| [1-5] ' access/tests/human-actions/L5-07-06-AT-108.md` | `5` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash ops-vm/tests/at-108-console-readonly.sh | grep -c '^PASS AT-108/static'
bash ops-vm/tests/at-108-console-readonly.sh >/dev/null 2>&1; echo "rc=$?"
grep -c '^| [1-5] ' access/tests/human-actions/L5-07-06-AT-108.md
```

Expected output, exactly:

```
7
rc=2
5
```

**STOP rule** — any `FAIL AT-108/static` means the console instance violates the Section 37.8 cage configuration contract, which is Priority P0. Do not edit `infra/hermes/ops-console.yaml` from this task; it is another L5 file's deliverable. Open a blocker issue and stop.

---

### L5-07-07 — AT-109: the background cage egress wall holds — M — ASSISTED

**Depends on:** L5-07-02. **Preconditions:** PRE-G, PRE-I, PRE-J.
**Writes:** `infra/tests/at-109-egress-wall.sh`, `access/tests/human-actions/L5-07-07-AT-109.md`.
**Spec:** AT-109 (Section 100.6) — "From inside the background worker container, a connection to a non-allowlisted external host and a connection to the Layer B store are both refused at the host egress layer — not by harness configuration — while connections to GitHub and to the LAN inference endpoint succeed; and during the test the systemd wall-clock stop terminates the running process at the window boundary (D69)." Section 37.8 ("the only security boundary against an adversarial LLM is the operating system"); Section 49.1 (the wall-clock hard stop is a host property, never a harness setting).

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout -B lane/5/07-at109 origin/integration
mkdir -p infra/tests access/tests/human-actions

cat > infra/tests/at-109-egress-wall.sh <<'SH'
#!/usr/bin/env bash
# AT-109 - spec 100.6. Static half proves the wall lives OUTSIDE the harness.
# The live half (two refusals, two permits, one wall-clock stop) is ASSISTED and
# must be executed from inside the background worker container.
set -uo pipefail
. access/tests/lib/assert.sh
ALLOW=infra/egress/background-host-allowlist.conf
STOPU=infra/systemd/background-window-stop.service
if [ ! -f "$ALLOW" ]; then l5_indeterminate "AT-109/static" "PRE-I missing: $ALLOW"; l5_exit; fi
if [ ! -f "$STOPU" ]; then l5_indeterminate "AT-109/static" "PRE-J missing: $STOPU"; l5_exit; fi
BAD=0
while IFS= read -r line; do
  case "$line" in ''|'#'*) continue ;; esac
  case "$line" in
    *github*|*mirror*|*inference*|*localhost*|10.*|192.168.*|172.1[6-9].*|172.2[0-9].*|172.3[01].*) ;;
    *) l5_fail "AT-109/static-allowlist" "unexpected egress destination: $line"; BAD=1 ;;
  esac
done < "$ALLOW"
[ "$BAD" -eq 0 ] && l5_pass "AT-109/static-allowlist"
if grep -qE 'OnCalendar|RuntimeMaxSec|ExecStop' "$STOPU"; then
  l5_pass "AT-109/static-stop-is-systemd"
else
  l5_fail "AT-109/static-stop-is-systemd" "unit declares no wall-clock stop mechanism"
fi
if yq -e '.egress // .network_allowlist' infra/hermes/background-worker.yaml >/dev/null 2>&1; then
  l5_fail "AT-109/static-wall-outside" "harness config declares egress control; spec 37.8 puts the wall outside the harness"
else
  l5_pass "AT-109/static-wall-outside"
fi
bash access/tests/lib/verify-evidence.sh AT-109
RC=$?
if [ "$RC" -eq 2 ]; then echo "INCOMPLETE AT-109 :: awaiting human evidence"; exit 2; fi
if [ "$RC" -eq 0 ]; then l5_pass "AT-109/live"; else l5_fail "AT-109/live" "evidence verification failed"; fi
l5_exit
SH
chmod +x infra/tests/at-109-egress-wall.sh
bash infra/tests/at-109-egress-wall.sh
git add infra/tests access/tests/human-actions
git commit -m "L5-07-07: AT-109 background cage egress wall test"
git push -u origin lane/5/07-at109
gh pr create --base integration --head lane/5/07-at109 --title "L5-07-07 AT-109" --body "Static wall-outside-the-harness assertions plus the human-action card."
echo "ASSISTED-HALT L5-07-07 AT-109"
```

**Human-action card content — copied verbatim.** Executor: the DevOps-capability holder, from inside the background worker container.

| # | Attempt | Required outcome |
| --- | --- | --- |
| 1 | Connect to a non-allowlisted external host | **Refused at the host egress layer** |
| 2 | Connect to the Layer B store | **Refused at the host egress layer** |
| 3 | Connect to GitHub | **Succeeds** |
| 4 | Connect to the LAN inference endpoint | **Succeeds** |
| 5 | Start a long-running task before the window boundary and observe it at the boundary | The systemd wall-clock stop **terminates** the process at the boundary |

The evidence file's `observed` field must state, for attempts 1 and 2, that the refusal came from the host firewall or the Docker egress override rather than from the harness. An evidence file that cannot distinguish the two is recorded as `fail`.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | Three static assertions pass | `bash infra/tests/at-109-egress-wall.sh \| grep -c '^PASS AT-109/static'` | `3` |
| 2 | Live half INCOMPLETE before evidence | `bash infra/tests/at-109-egress-wall.sh >/dev/null 2>&1; echo "rc=$?"` | `rc=2` |
| 3 | Card lists all five attempts | `grep -c '^| [1-5] ' access/tests/human-actions/L5-07-07-AT-109.md` | `5` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash infra/tests/at-109-egress-wall.sh | grep -c '^PASS AT-109/static'
bash infra/tests/at-109-egress-wall.sh >/dev/null 2>&1; echo "rc=$?"
grep -c '^| [1-5] ' access/tests/human-actions/L5-07-07-AT-109.md
```

Expected output, exactly:

```
3
rc=2
5
```

**STOP rule** — if `AT-109/static-wall-outside` fails, the egress wall has been implemented inside the harness. Section 37.8 is explicit that harness configuration is "a heuristic, not containment". Open a blocker issue; never accept a harness setting as the wall.

---

### L5-07-08 — AT-097 and AT-098: Grafana instance separation — M — AUTO + ASSISTED

**Depends on:** L5-07-02. **Preconditions:** PRE-E, PRE-F.
**Writes:** `ops-vm/tests/at-097-shared-no-people-ds.sh`, `ops-vm/tests/at-098-founder-instance-cred.sh`, `access/tests/human-actions/L5-07-08-AT-098.md`.
**Spec:** AT-097 — "no datasource entry and no dashboard reference exist there, verified in the provisioned configuration, not inferred from panel visibility (D75)". AT-098 — "a shared-instance login grants nothing there, and a direct query without that instance's credential is denied (D75)". Section 90.3 (the Layer B boundary is instance separation, not folder membership); Section 99.5 (panel-hiding is explicitly insufficient); invariant 109.

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout -B lane/5/07-at097-098 origin/integration
mkdir -p ops-vm/tests access/tests/human-actions

cat > ops-vm/tests/at-097-shared-no-people-ds.sh <<'SH'
#!/usr/bin/env bash
# AT-097 - spec 100.6 / 90.3 (D75). Verified in the PROVISIONED CONFIGURATION:
# no datasource entry and no dashboard reference to the people datasource may
# exist in the shared instance.
set -uo pipefail
. access/tests/lib/assert.sh
SHARED=ops-vm/grafana/shared
FOUNDER=ops-vm/grafana/founder
if [ ! -d "$SHARED/provisioning/datasources" ]; then l5_indeterminate "AT-097" "PRE-E missing"; l5_exit; fi
if [ ! -d "$FOUNDER/provisioning/datasources" ]; then l5_indeterminate "AT-097" "PRE-F missing"; l5_exit; fi
TOKENS="$(grep -rhoE '(uid|name):[[:space:]]*[A-Za-z0-9_-]+' "$FOUNDER/provisioning/datasources" | awk '{print $2}' | sort -u)"
if [ -z "$TOKENS" ]; then l5_indeterminate "AT-097" "founder instance declares no datasource to look for"; l5_exit; fi
HIT=0
for tok in $TOKENS; do
  if grep -rqF "$tok" "$SHARED" 2>/dev/null; then
    l5_fail "AT-097" "shared instance provisioning references the people datasource token '$tok'"
    HIT=1
  fi
done
[ "$HIT" -eq 0 ] && l5_pass "AT-097/no-people-datasource-in-shared"
if grep -rqiE 'people|layer[_-]?b' "$SHARED/provisioning" 2>/dev/null; then
  l5_fail "AT-097/naming" "shared provisioning mentions people or Layer B"
else
  l5_pass "AT-097/naming"
fi
l5_exit
SH

cat > ops-vm/tests/at-098-founder-instance-cred.sh <<'SH'
#!/usr/bin/env bash
# AT-098 - spec 100.6 / 90.3 / 90.4 (D75). Static half: the two instances are
# distinct and the founder instance declares its own authentication restriction.
# Live half is ASSISTED: a shared-instance login must grant nothing there, and a
# direct query without that instance's credential must be denied.
set -uo pipefail
. access/tests/lib/assert.sh
S=ops-vm/grafana/shared/grafana.ini
F=ops-vm/grafana/founder/grafana.ini
if [ ! -f "$S" ] || [ ! -f "$F" ]; then l5_indeterminate "AT-098/static" "one or both grafana.ini absent"; l5_exit; fi
SP="$(grep -E '^http_port' "$S" | head -n 1)"
FP="$(grep -E '^http_port' "$F" | head -n 1)"
if [ -n "$SP" ] && [ -n "$FP" ] && [ "$SP" != "$FP" ]; then
  l5_pass "AT-098/distinct-instances"
else
  l5_fail "AT-098/distinct-instances" "instances do not declare distinct http_port"
fi
if grep -qiE 'allow(ed)?[_-]?users|allowlist|auth' "$F"; then
  l5_pass "AT-098/auth-restriction"
else
  l5_fail "AT-098/auth-restriction" "founder instance declares no authentication restriction"
fi
bash access/tests/lib/verify-evidence.sh AT-098
RC=$?
if [ "$RC" -eq 2 ]; then echo "INCOMPLETE AT-098 :: awaiting human evidence"; exit 2; fi
if [ "$RC" -eq 0 ]; then l5_pass "AT-098/live"; else l5_fail "AT-098/live" "evidence verification failed"; fi
l5_exit
SH
chmod +x ops-vm/tests/at-097-shared-no-people-ds.sh ops-vm/tests/at-098-founder-instance-cred.sh
bash ops-vm/tests/at-097-shared-no-people-ds.sh
bash ops-vm/tests/at-098-founder-instance-cred.sh
git add ops-vm/tests access/tests/human-actions
git commit -m "L5-07-08: AT-097 and AT-098 Grafana instance separation"
git push -u origin lane/5/07-at097-098
gh pr create --base integration --head lane/5/07-at097-098 --title "L5-07-08 AT-097 and AT-098" --body "Instance-level Layer B separation verified in provisioned configuration (D75)."
echo "ASSISTED-HALT L5-07-08 AT-098"
```

**Human-action card content for AT-098 — copied verbatim.** Executor: the Founder, over the private path of Section 51.4.

| # | Attempt | Required outcome |
| --- | --- | --- |
| 1 | Log in to the shared Grafana instance, then open the Founder-only instance in the same session | **No access** — the shared session grants nothing |
| 2 | Query the Founder-only instance's datasource API with no credential | **Denied** |
| 3 | Repeat with the Founder-only instance's own credential | **Succeeds** — the positive control |

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | Shared instance references no people datasource token | `bash ops-vm/tests/at-097-shared-no-people-ds.sh \| tail -n 1` | `SUITE OK` |
| 2 | Two static AT-098 assertions pass | `bash ops-vm/tests/at-098-founder-instance-cred.sh \| grep -c '^PASS AT-098/'` | `2` |
| 3 | AT-098 live half INCOMPLETE before evidence | `bash ops-vm/tests/at-098-founder-instance-cred.sh >/dev/null 2>&1; echo "rc=$?"` | `rc=2` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash ops-vm/tests/at-097-shared-no-people-ds.sh | tail -n 1
bash ops-vm/tests/at-098-founder-instance-cred.sh | grep -c '^PASS AT-098/'
bash ops-vm/tests/at-098-founder-instance-cred.sh >/dev/null 2>&1; echo "rc=$?"
```

Expected output, exactly:

```
SUITE OK
2
rc=2
```

**STOP rule** — an AT-097 failure means sensitive people data is reachable from the shared instance. Section 90.3 holds that any user able to query the people datasource has full access to it. Treat as a Section 43 security incident, open a blocker issue at Blocking severity, and stop the lane. Do not hide the panel: Section 99.5 states panel-hiding is explicitly insufficient.

---

### L5-07-09 — AT-110 and AT-022: the reconciler credential's bounds and the break-glass Owner — M — ASSISTED (AT-110) + HUMAN-GATED (AT-022)

**Depends on:** L5-07-02. **Preconditions:** PRE-C, PRE-D, PRE-K. **Out-of-lane:** EXT-2.
**Writes:** `access/tests/at-110-reconciler-bounds.sh`, `access/tests/at-022-breakglass-owner.sh`, `access/tests/human-actions/L5-07-09-AT-110.md`, `access/tests/human-actions/L5-07-09-AT-022.md`.
**Spec:** AT-110 (Section 100.6) — "From the reconciler's own credential, six attempts are made — a write to a GitHub Actions secret, a write to an environment, a workflow-file change, an organisation-settings change, a `records/**` write, and any Layer B access — and all six fail; the credential then still completes a normal reconciliation run. Executed for real at the phase that builds the reconciler and re-executed at every rotation… The system's most privileged identity (Section 99.6, risk 6) is the one whose boundary must be executed rather than asserted." Section 26.4 (the reconciler credential writes Level-3 auto-repairs and derived-field transitions directly — that is its declared repair scope, and nothing else is in it); Section 40.1 (the five control-plane machine credentials, rotation cadence, named rotator, runbook, behavioural envelope, envelope alert-config owner); Section 49.1 (each machine credential carries an inventory entry). AT-022 (Section 100.2) — "the second organisation Owner or escrowed break-glass owner credential is verified usable; the founder-only account inventory is current; Layer B contingency access functions. Verified by periodic drill, not assumed." Section 14.4 components 1, 2 and 4 and the escrow mechanics; invariant 39; NC-12.

Two boundaries bind this task and are stated before its first command:

* **EXT-2.** The reconciler credential and `reconciler/**` belong to L3. Lane 5 supplies the bounding test harness and the human-action card; Lane 5 never issues, holds, rotates or exercises that credential, and never edits `reconciler/**`. The positive control of AT-110 — "the credential then still completes a normal reconciliation run" — is executed by L3 under its own live-organisation gate and arrives here only as the human's evidence file.
* **AT-022 is HUMAN-GATED.** Per Section 1, the AI executor performs no part of the continuity drill. It writes the evidence verifier — machinery of Section 1.1, not a step of the drill — and it opens the routing block below. It never creates an account, never authenticates a dormant Owner credential, and never opens an escrow.

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout -B lane/5/07-at110-at022 origin/integration
mkdir -p access/tests access/tests/human-actions

cat > access/tests/at-110-reconciler-bounds.sh <<'SH'
#!/usr/bin/env bash
# AT-110 - spec 100.6. Lane 5 supplies the BOUNDING HARNESS only (EXT-2): the
# reconciler credential and reconciler/** belong to L3. The static half asserts the
# declared bound in Lane-5-owned configuration; the live half (six refusals plus one
# positive control) is ASSISTED and is executed by a named human.
set -uo pipefail
. access/tests/lib/assert.sh
INV=assets/inventory/machine-credential-reconciler.yaml
if [ ! -f "$INV" ]; then
  l5_indeterminate "AT-110/static" "PRE-K missing: $INV (spec 40.1, 49.1)"
  l5_exit
fi
for k in rotation_cadence rotator runbook behavioural_envelope envelope_alert_config_owner; do
  v="$(yq -r ".$k // \"\"" "$INV")"
  if [ -n "$v" ] && [ "$v" != "null" ]; then
    l5_pass "AT-110/static-$k"
  else
    l5_fail "AT-110/static-$k" "the reconciler credential entry declares no $k (spec 40.1)"
  fi
done
# Negative: no Lane 5 access declaration may grant the reconciler credential a write
# outside its Section 26.4 repair scope. The six AT-110 attempts name the forbidden
# surfaces; four of them are declared in Lane-5-owned files and are checked here.
SCOPE="$(grep -rniE 'reconciler' access/permission-model access/branch-protection access/secret-tiers 2>/dev/null \
         | grep -Ei 'actions[_-]?secret|environment|workflow|org(anisation)?[_-]?settings|layer[_-]?b' || true)"
if [ -z "$SCOPE" ]; then
  l5_pass "AT-110/static-no-write-outside-repair-scope"
else
  l5_fail "AT-110/static-no-write-outside-repair-scope" "a Lane 5 declaration grants the reconciler a write outside Section 26.4 repair scope: $SCOPE"
fi
bash access/tests/lib/verify-evidence.sh AT-110
RC=$?
if [ "$RC" -eq 2 ]; then echo "INCOMPLETE AT-110 :: awaiting human evidence"; exit 2; fi
if [ "$RC" -eq 0 ]; then l5_pass "AT-110/live"; else l5_fail "AT-110/live" "evidence verification failed"; fi
l5_exit
SH

cat > access/tests/at-022-breakglass-owner.sh <<'SH'
#!/usr/bin/env bash
# AT-022 and NC-12 - spec 100.2, 14.4 components 1, 2 and 4, invariant 39.
# HUMAN-GATED. This script performs NO part of the continuity drill. It asserts only
# what the Lane-5-owned inventory must already declare, then verifies the drill record
# the L0 human lead produces. It can never report PASS from configuration alone.
set -uo pipefail
. access/tests/lib/assert.sh
if [ ! -d assets/inventory ]; then
  l5_indeterminate "AT-022/static" "PRE-K missing: assets/inventory"
  l5_exit
fi
ESCROW="$(grep -rliE 'escrow' assets/inventory 2>/dev/null | head -n 1)"
if [ -n "$ESCROW" ]; then
  l5_pass "AT-022/static-escrow-recorded"
else
  l5_fail "AT-022/static-escrow-recorded" "no asset entry records the escrow or its custodian (spec 14.4 escrow mechanics)"
fi
ACCTS="$(grep -rlE 'asset_class:[[:space:]]*founder_account' assets/inventory 2>/dev/null | wc -l | tr -d ' ')"
if [ "$ACCTS" -ge 1 ]; then
  l5_pass "AT-022/static-founder-account-inventory"
else
  l5_fail "AT-022/static-founder-account-inventory" "no founder_account entry exists; spec 14.4 component 2 requires every founder-only account enumerated"
fi
bash access/tests/lib/verify-evidence.sh AT-022
RC=$?
if [ "$RC" -eq 2 ]; then echo "INCOMPLETE AT-022 :: awaiting the L0 continuity drill record"; exit 2; fi
if [ "$RC" -eq 0 ]; then l5_pass "AT-022/drill"; else l5_fail "AT-022/drill" "drill evidence verification failed"; fi
l5_exit
SH

cat > access/tests/human-actions/L5-07-09-AT-110.md <<'MD'
# HUMAN ACTION REQUIRED — L5-07-09 / AT-110

**Executor:** DevOps-capability holder, supervised, from the reconciler's own credential
**Why a human:** the step requires holding the reconciler credential, which no AI executor may hold (Section 99.6, risk 6)
**Spec clause:** Section 100.6, AT-110 — "From the reconciler's own credential, six attempts are made — a write to a GitHub Actions secret, a write to an environment, a workflow-file change, an organisation-settings change, a `records/**` write, and any Layer B access — and all six fail; the credential then still completes a normal reconciliation run."
**Expected result:** attempts 1 to 6 are refused; attempt 7 succeeds.

## Steps
| # | Attempt | Required outcome |
| --- | --- | --- |
| 1 | Write a GitHub Actions secret on the control-plane repository | **Refused** |
| 2 | Write an environment (create or modify) on the control-plane repository | **Refused** |
| 3 | Change a workflow file under `.github/workflows/` | **Refused** |
| 4 | Change an organisation setting | **Refused** |
| 5 | Write to `records/**` in the control-plane-records repository | **Refused** |
| 6 | Access Layer B — the Founder-only Grafana instance or the people-data store | **Refused** |
| 7 | Positive control: run one normal reconciliation to completion (executed by L3 under its own live-organisation gate, EXT-2) | **Completes** |

## Record the result
Run:
    bash access/tests/lib/record-evidence.sh AT-110 pass "<observed, naming which side refused each of attempts 1-6>"
Then commit the produced file under access/tests/evidence/ on branch lane/5/07-evidence.
MD

cat > access/tests/human-actions/L5-07-09-AT-022.md <<'MD'
# HUMAN ACTION REQUIRED — L5-07-09 / AT-022

**Executor:** the L0 human lead only — HUMAN-GATED, see Section 1
**Why a human:** the step exercises organisation-owner recovery and a sealed escrow; no AI executor may touch either
**Spec clause:** Section 100.2, AT-022 — "the second organisation Owner or escrowed break-glass owner credential is verified usable; the founder-only account inventory is current; Layer B contingency access functions. Verified by periodic drill, not assumed."
**Expected result:** all four legs below verify in one drill.

## Steps
| # | Leg | Required outcome |
| --- | --- | --- |
| 1 | The standing delegation trigger (Section 14.3) activates | **Activates** as declared |
| 2 | The second organisation Owner, or the escrowed break-glass Owner credential, authenticates | **Usable** — the dormant-account authentication alert fires and is seen |
| 3 | The founder-only account inventory is compared against the operational asset inventory | **Current** — no unlisted founder-only account |
| 4 | Layer B contingency access (the sealed contingency credential of Section 14.4 component 4) decrypts its canary blob | **Functions**, without opening any document |

## Record the result
Run:
    bash access/tests/lib/record-evidence.sh AT-022 pass "<observed, one line per leg>"
Then commit the produced file under access/tests/evidence/ on branch lane/5/07-evidence.
MD

chmod +x access/tests/at-110-reconciler-bounds.sh access/tests/at-022-breakglass-owner.sh
bash access/tests/at-110-reconciler-bounds.sh
bash access/tests/at-022-breakglass-owner.sh
git add access/tests/at-110-reconciler-bounds.sh access/tests/at-022-breakglass-owner.sh access/tests/human-actions
git commit -m "L5-07-09: AT-110 reconciler bounding harness and AT-022 continuity drill verifier"
git push -u origin lane/5/07-at110-at022
gh pr create --base integration --head lane/5/07-at110-at022 --title "L5-07-09 AT-110 and AT-022" --body "Bounding harness plus human-action cards. AT-110 live is ASSISTED; AT-022 is HUMAN-GATED (L0)."
echo "ASSISTED-HALT L5-07-09 AT-110"
echo "HUMAN-GATED-HALT L5-07-09 AT-022"
```

**DECISION REQUIRED → L0 — DR-L5-07-A: the AT-022 continuity drill.**

> AT-022 needs three things no executor in this lane may decide or supply: **who** holds the second organisation Owner account or the escrowed break-glass credential; **who** is the named escrow custodian of Section 14.4; and **when** the periodic drill runs. Section 1 classes the whole drill HUMAN-GATED, and PARTITION gives no lane authority over organisation ownership.
>
> **What is blocked:** AT-022 and NC-12 stay `INCOMPLETE`.
> **Default if L0 does not answer:** `INCOMPLETE` — never `PASS`, never `FAIL`. The executor does not retry, does not simulate the drill, and does not proceed to any task that depends on AT-022.
> **Route:** blocker issue, template B-2 of Section 8, `component: access`, `action_requested: L0 decision`.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | Both scripts exist and are executable | `test -x access/tests/at-110-reconciler-bounds.sh && test -x access/tests/at-022-breakglass-owner.sh && echo OK` | `OK` |
| 2 | Six AT-110 static assertions pass | `bash access/tests/at-110-reconciler-bounds.sh \| grep -c '^PASS AT-110/static'` | `6` |
| 3 | AT-110's live half is INCOMPLETE, never PASS, before evidence | `bash access/tests/at-110-reconciler-bounds.sh >/dev/null 2>&1; echo "rc=$?"` | `rc=2` |
| 4 | AT-022 reports INCOMPLETE from configuration alone | `bash access/tests/at-022-breakglass-owner.sh \| tail -n 1` | `INCOMPLETE AT-022 :: awaiting the L0 continuity drill record` |
| 5 | The AT-110 card lists all seven attempts | `grep -c '^| [1-7] ' access/tests/human-actions/L5-07-09-AT-110.md` | `7` |
| 6 | The AT-022 card lists all four legs | `grep -c '^| [1-4] ' access/tests/human-actions/L5-07-09-AT-022.md` | `4` |
| 7 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^(access|infra|ops-vm|notify|assets)/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash access/tests/at-110-reconciler-bounds.sh | grep -c '^PASS AT-110/static'
bash access/tests/at-110-reconciler-bounds.sh >/dev/null 2>&1; echo "rc=$?"
bash access/tests/at-022-breakglass-owner.sh | tail -n 1
grep -c '^| [1-7] ' access/tests/human-actions/L5-07-09-AT-110.md
grep -c '^| [1-4] ' access/tests/human-actions/L5-07-09-AT-022.md
git diff --name-only origin/integration...HEAD | grep -Ev '^(access|infra|ops-vm|notify|assets)/' | wc -l
```

Expected output, exactly:

```
6
rc=2
INCOMPLETE AT-022 :: awaiting the L0 continuity drill record
7
4
0
```

**STOP rules**

* `FAIL AT-110/static-no-write-outside-repair-scope` — a Lane 5 access declaration grants the reconciler credential a write the six AT-110 attempts require to fail. Section 40.1 treats a credential in the wrong tier as a security incident under Section 43, not a cleanup task. Open a blocker issue with template B-2 at Blocking severity and stop the lane. Do not edit `reconciler/**` — that is L3's path under PARTITION.
* `FAIL AT-022/static-*` — the continuity inventory is incomplete and invariant 39 is unmet. Open a blocker issue against the Lane 5 file owning `assets/inventory/**`; do not author an inventory entry from this task.
* The AI executor may under no circumstance hold, mint, rotate or authenticate the reconciler credential, the break-glass Owner credential or any escrowed credential.

---

### L5-07-10 — AT-089, AT-090, AT-091, AT-092, AT-096 and AT-100: Layer B reach and conduct separation — M — AUTO + ASSISTED

**Depends on:** L5-07-02. **Preconditions:** PRE-C, PRE-E, PRE-F, PRE-K.
**Writes:** `access/tests/at-089-096-layerb-reach.sh`, `access/tests/at-090-founder-only.sh`, `access/tests/at-091-capability-gate.sh`, `access/tests/at-100-conduct-separation.sh`, `access/tests/human-actions/L5-07-10-AT-090.md`.
**Spec:** AT-089, AT-092, AT-096 (Section 100.6) — "Peers and general dashboards cannot reach Layer B data by any path"; "Access is denied at both the dashboard and the datasource level"; "Any attempt is denied". AT-090 — "Only the Founder can access full individual people intelligence at the application and datasource layers; no delegate exists, and an attempt to create an assignment granting `people-intelligence` fails validation… Host-level administrative access is out of this test's scope and is tested instead against the named accepted-access record of Section 90.3: its holder is named in the asset inventory, its compensating audit trail is live and shipping off-host, and its review is within cadence." AT-091 — "Access follows the capability, not the role name." AT-100 — "Conduct evidence is held separately and is inaccessible to performance-review pack generation." Section 90.3 (datasource-level enforcement; instance separation, not folder membership); Section 90.4 (`people-intelligence` is not delegable, D109); Section 99.5 (panel-hiding is explicitly insufficient); invariants 106, 107, 108, 109, 110.

Lane 5 tests the **enforcement** legs — capability, datasource and instance — because those are subsystem L. It tests no view.

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout -B lane/5/07-layerb origin/integration
mkdir -p access/tests access/tests/human-actions

cat > access/tests/at-089-096-layerb-reach.sh <<'SH'
#!/usr/bin/env bash
# AT-089, AT-092, AT-096 - spec 100.6, 90.2, 90.3; invariants 107, 108, 109.
# Verified in the declared permission matrix and the PROVISIONED configuration of the
# shared instance - never inferred from panel visibility (D75, spec 99.5).
set -uo pipefail
. access/tests/lib/assert.sh
PM=access/model/permission-matrix.yaml
SHARED=ops-vm/grafana/shared
if [ ! -f "$PM" ]; then l5_indeterminate "AT-089" "permission matrix absent: $PM (spec 90.2)"; l5_exit; fi
if [ ! -d "$SHARED/provisioning" ]; then l5_indeterminate "AT-089" "PRE-E missing: $SHARED/provisioning"; l5_exit; fi
GSR="$(yq -r '.general_surface_rule // ""' "$PM")"
if [ -n "$GSR" ] && [ "$GSR" != "null" ]; then
  l5_pass "AT-089/general-surface-rule"
else
  l5_fail "AT-089/general-surface-rule" "the matrix declares no general_surface_rule (invariant 109)"
fi
PERSONVAR="$(grep -rniE '"name"[[:space:]]*:[[:space:]]*"(person|person_id|employee|employee_id)"' "$SHARED" 2>/dev/null || true)"
if [ -z "$PERSONVAR" ]; then
  l5_pass "AT-089/no-per-person-drilldown"
else
  l5_fail "AT-089/no-per-person-drilldown" "shared instance declares a per-person variable: $PERSONVAR"
fi
ROW='.rows[] | select(.data_category == "Individual utilisation detail")'
TL="$(yq -r "$ROW | .team_lead // \"\"" "$PM")"
PEER="$(yq -r "$ROW | .peer // \"\"" "$PM")"
EMP="$(yq -r "$ROW | .employee // \"\"" "$PM")"
if [ "$TL" = "No" ]; then l5_pass "AT-092/team-lead-denied"; else l5_fail "AT-092/team-lead-denied" "matrix gives the Team Lead '$TL' on individual utilisation detail; spec 90.2 says No"; fi
if [ "$PEER" = "No" ]; then l5_pass "AT-096/peer-denied"; else l5_fail "AT-096/peer-denied" "matrix gives a peer '$PEER'; spec 90.2 says No"; fi
if [ "$EMP" = "Own only" ]; then l5_pass "AT-096/own-only"; else l5_fail "AT-096/own-only" "matrix gives an employee '$EMP'; spec 90.2 says Own only"; fi
l5_exit
SH

cat > access/tests/at-091-capability-gate.sh <<'SH'
#!/usr/bin/env bash
# AT-091 - spec 100.6, 90.4, D109; invariant 106. Access follows the capability, not
# the role name, and the capability is not delegable.
set -uo pipefail
. access/tests/lib/assert.sh
PM=access/model/permission-matrix.yaml
GATE=access/tools/check_people_intelligence_gate.py
command -v python3 >/dev/null 2>&1 || { l5_indeterminate "AT-091" "python3 not on PATH"; l5_exit; }
if [ ! -f "$GATE" ]; then l5_indeterminate "AT-091" "capability gate absent: $GATE"; l5_exit; fi
if [ ! -f "$PM" ]; then l5_indeterminate "AT-091" "permission matrix absent: $PM"; l5_exit; fi
OUT="$(python3 "$GATE" --selftest 2>&1)"
if echo "$OUT" | grep -qF 'L5-T14 SELF-VERIFY PASS'; then
  l5_pass "AT-091/gate-selftest"
else
  l5_fail "AT-091/gate-selftest" "capability gate selftest did not pass: $OUT"
fi
ABS="$(yq -r '.machine_identity_row.absolute // ""' "$PM")"
if [ "$ABS" = "true" ]; then
  l5_pass "AT-091/machine-identity-absolute"
else
  l5_fail "AT-091/machine-identity-absolute" "machine_identity_row.absolute is '$ABS'; spec 90.2 makes it absolute"
fi
DELEG="$(grep -rniE 'people[_-]intelligence' access --include='*.yaml' 2>/dev/null | grep -Ei 'delegate|assignment_type' || true)"
if [ -z "$DELEG" ]; then
  l5_pass "AT-091/not-delegable"
else
  l5_fail "AT-091/not-delegable" "a Lane 5 declaration names a delegate or assignment type for people-intelligence (D109): $DELEG"
fi
l5_exit
SH

cat > access/tests/at-090-founder-only.sh <<'SH'
#!/usr/bin/env bash
# AT-090 - spec 100.6, 90.3, 90.4; invariant 106. Static half: Layer B is declared
# Founder-only and the named accepted-access record of 90.3 exists in the inventory.
# Live half is ASSISTED: the compensating audit trail and its review cadence.
set -uo pipefail
. access/tests/lib/assert.sh
PM=access/model/permission-matrix.yaml
if [ ! -f "$PM" ]; then l5_indeterminate "AT-090/static" "permission matrix absent: $PM"; l5_exit; fi
SCOPE="$(yq -r '.layers.B.scope // ""' "$PM")"
case "$SCOPE" in
  *Founder*) l5_pass "AT-090/static-founder-only" ;;
  *) l5_fail "AT-090/static-founder-only" "layers.B.scope is '$SCOPE'; spec 90.2 confines Layer B to the Founder" ;;
esac
ACC="$(grep -rliE 'accepted[_-]?risk|accepted[_-]?access' assets/inventory access/accepted-risks 2>/dev/null | head -n 1)"
if [ -n "$ACC" ]; then
  l5_pass "AT-090/static-accepted-access-record"
else
  l5_fail "AT-090/static-accepted-access-record" "no named accepted-access record for host-level administrative access (spec 90.3)"
fi
bash access/tests/lib/verify-evidence.sh AT-090
RC=$?
if [ "$RC" -eq 2 ]; then echo "INCOMPLETE AT-090 :: awaiting human evidence"; exit 2; fi
if [ "$RC" -eq 0 ]; then l5_pass "AT-090/live"; else l5_fail "AT-090/live" "evidence verification failed"; fi
l5_exit
SH

cat > access/tests/at-100-conduct-separation.sh <<'SH'
#!/usr/bin/env bash
# AT-100 - spec 100.6, 90.4, 88; invariant 110. Conduct evidence is held separately
# and holding people-intelligence never grants conduct-record access.
set -uo pipefail
. access/tests/lib/assert.sh
GATE=access/tools/check_people_intelligence_gate.py
command -v python3 >/dev/null 2>&1 || { l5_indeterminate "AT-100" "python3 not on PATH"; l5_exit; }
if [ ! -f "$GATE" ]; then l5_indeterminate "AT-100" "capability gate absent: $GATE"; l5_exit; fi
OUT="$(python3 "$GATE" --selftest 2>&1)"
if echo "$OUT" | grep -qF 'L5-T14 SELF-VERIFY PASS'; then
  l5_pass "AT-100/conduct-carve-out"
else
  l5_fail "AT-100/conduct-carve-out" "the gate selftest, which covers conduct-record access by a capability holder, did not pass: $OUT"
fi
CONDUCT="$(grep -rli 'conduct' ops-vm/grafana 2>/dev/null || true)"
if [ -z "$CONDUCT" ]; then
  l5_pass "AT-100/no-conduct-datasource"
else
  l5_fail "AT-100/no-conduct-datasource" "a Grafana instance references conduct data: $CONDUCT"
fi
l5_exit
SH

cat > access/tests/human-actions/L5-07-10-AT-090.md <<'MD'
# HUMAN ACTION REQUIRED — L5-07-10 / AT-090

**Executor:** the Founder, over the private path of Section 51.4
**Why a human:** the step reads the Layer B host's live audit configuration and its review record; no AI executor may reach that host
**Spec clause:** Section 100.6, AT-090 — "Host-level administrative access is out of this test's scope and is tested instead against the named accepted-access record of Section 90.3: its holder is named in the asset inventory, its compensating audit trail is live and shipping off-host, and its review is within cadence."
**Expected result:** all three legs below hold.

## Steps
| # | Leg | Required outcome |
| --- | --- | --- |
| 1 | Compare the host-level administrative holders — OS accounts, sudoers, SSH authorised keys, backup-store read list — against the named accepted-access record | **Match**; a holder in neither list is Blocking drift (spec 90.4) |
| 2 | Confirm host-level file-access auditing on the store path is running and shipping to a destination the host holds no credential to alter | **Live and off-host** |
| 3 | Confirm the accepted-access record's dated review is within its cadence | **Within cadence** |

## Record the result
Run:
    bash access/tests/lib/record-evidence.sh AT-090 pass "<observed, one line per leg>"
Then commit the produced file under access/tests/evidence/ on branch lane/5/07-evidence.
MD

chmod +x access/tests/at-089-096-layerb-reach.sh access/tests/at-090-founder-only.sh \
         access/tests/at-091-capability-gate.sh access/tests/at-100-conduct-separation.sh
bash access/tests/at-089-096-layerb-reach.sh
bash access/tests/at-091-capability-gate.sh
bash access/tests/at-090-founder-only.sh
bash access/tests/at-100-conduct-separation.sh
git add access/tests/at-089-096-layerb-reach.sh access/tests/at-090-founder-only.sh \
        access/tests/at-091-capability-gate.sh access/tests/at-100-conduct-separation.sh \
        access/tests/human-actions
git commit -m "L5-07-10: AT-089, AT-090, AT-091, AT-092, AT-096, AT-100 Layer B enforcement tests"
git push -u origin lane/5/07-layerb
gh pr create --base integration --head lane/5/07-layerb --title "L5-07-10 Layer B reach and conduct separation" --body "Capability, datasource and instance enforcement legs only. AT-090's host-level leg is ASSISTED."
echo "ASSISTED-HALT L5-07-10 AT-090"
```

**DECISION REQUIRED → L0 — DR-L5-07-B: the view-layer and people-engine legs, and the conduct complaint path.**

> Three legs of these acceptance tests are outside every path PARTITION v1 assigns, and this task claims none of them:
>
> | Leg | Subsystem | PARTITION v1 status |
> | --- | --- | --- |
> | "Access is denied at the **dashboard** level" (AT-092), and the general-dashboard reach of AT-089 as rendered | **H** — dashboards and views | **Unassigned** |
> | The people-intelligence computation that AT-090 and AT-096 protect | **P** — people intelligence engine | **Unassigned** |
> | The conduct complaint path functioning when the subject is the Team Lead or the Founder (AT-100, Section 88.4 external-adviser custody) | Conduct store, no owning lane | **Unassigned** |
>
> Lane 5 owns and tests the capability, datasource and instance legs, which is where Section 90.3 puts the boundary ("the Layer B boundary is instance separation, not folder membership"). **L0 must assign H, P and the conduct store before the dashboard-level and engine-level legs can be executed by anyone.** The executor does not build them, does not stub them, and does not widen these four scripts to cover them.
>
> **Default if L0 does not answer:** the four scripts here stand as written; the unassigned legs remain unexecuted and are reported as such in the lane review. **Route:** blocker issue, template B-1 of Section 8, `action_requested: L0 partition decision`.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | All four scripts exist and are executable | `ls access/tests/at-089-096-layerb-reach.sh access/tests/at-090-founder-only.sh access/tests/at-091-capability-gate.sh access/tests/at-100-conduct-separation.sh \| wc -l` | `4` |
| 2 | The five AT-089/092/096 assertions pass | `bash access/tests/at-089-096-layerb-reach.sh \| grep -c '^PASS AT-0'` | `5` |
| 3 | The three AT-091 assertions pass | `bash access/tests/at-091-capability-gate.sh \| tail -n 1` | `SUITE OK` |
| 4 | AT-090's static half passes and its live half is INCOMPLETE | `bash access/tests/at-090-founder-only.sh \| tail -n 1` | `INCOMPLETE AT-090 :: awaiting human evidence` |
| 5 | AT-100 passes both assertions | `bash access/tests/at-100-conduct-separation.sh \| tail -n 1` | `SUITE OK` |
| 6 | The AT-090 card lists all three legs | `grep -c '^| [1-3] ' access/tests/human-actions/L5-07-10-AT-090.md` | `3` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash access/tests/at-089-096-layerb-reach.sh | grep -c '^PASS AT-0'
bash access/tests/at-091-capability-gate.sh | tail -n 1
bash access/tests/at-090-founder-only.sh | tail -n 1
bash access/tests/at-100-conduct-separation.sh | tail -n 1
grep -c '^| [1-3] ' access/tests/human-actions/L5-07-10-AT-090.md
```

Expected output, exactly:

```
5
SUITE OK
INCOMPLETE AT-090 :: awaiting human evidence
SUITE OK
3
```

**STOP rules**

* `FAIL AT-089/no-per-person-drilldown` or `FAIL AT-092/team-lead-denied` — sensitive people data is reachable from a general surface. Section 90.3 holds that any user able to query the people datasource has full access to it, and Section 99.5 states panel-hiding is explicitly insufficient. Treat as a Section 43 security incident, open a blocker issue with template B-2 at Blocking severity, and stop the lane. Do not hide a panel and do not edit the dashboard.
* `FAIL AT-091/not-delegable` — a Lane 5 declaration contradicts D109. Do not delete the declaration from this task; it belongs to the Lane 5 file that wrote it. Open a blocker issue naming the file and the line.
* `INDETERMINATE AT-091` because `access/tools/check_people_intelligence_gate.py` is absent — the gate is another Lane 5 file's deliverable. Open a blocker issue against it; never re-implement the gate inside a test.

---

### L5-07-11 — AT-017: the asset-owner orphan leg — S — AUTO

**Depends on:** L5-07-02. **Preconditions:** PRE-K.
**Writes:** `assets/tests/at-017-asset-owner-orphan.sh`, `assets/tests/fixtures/asset-owner-departed.yaml`, `assets/tests/fixtures/asset-owner-active.yaml`.
**Spec:** AT-017 (Section 100.2) — "orphan detection surfaces every unowned responsibility; blocking orphans cannot be dismissed unresolved". Section 49.1 — "**Asset owners participate in orphan detection.** A departing person who owned a certificate or a domain leaves an orphaned asset, and the exit lifecycle (Section 12, Person Lifecycles) surfaces it alongside orphaned products and reviews"; each entry carries an expiry date, a named owner and an alert threshold of at least 30 days.

Only the **asset-owner leg** of AT-017 is Lane 5's. The exit lifecycle, revocation and succession legs are subsystems C and D (lane L3) and are not touched here.

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout -B lane/5/07-at017 origin/integration
mkdir -p assets/tests/fixtures

cat > assets/tests/fixtures/asset-owner-departed.yaml <<'YAML'
# AT-017 negative fixture. The owner has left; the exit lifecycle left the entry
# unowned. Spec 49.1 requires this state to SURFACE, so the validator must refuse it.
asset_id: at-017-orphan-fixture
asset_class: certificate
owner: unassigned
expiry_date: 2099-12-31
alert_days: 30
cost_band: none
spec_reference: "49.1"
YAML

cat > assets/tests/fixtures/asset-owner-active.yaml <<'YAML'
# AT-017 positive control. Identical entry with a resolving owner. __OWNER__ is
# substituted at run time from assets/resolve_holder.py; it is never hand-filled.
asset_id: at-017-owned-fixture
asset_class: certificate
owner: __OWNER__
expiry_date: 2099-12-31
alert_days: 30
cost_band: none
spec_reference: "49.1"
YAML

cat > assets/tests/at-017-asset-owner-orphan.sh <<'SH'
#!/usr/bin/env bash
# AT-017 (asset-owner leg) - spec 100.2 and 49.1: "Asset owners participate in orphan
# detection." An asset left unowned by a departure must SURFACE; an owned one must not.
# The check runs against a copy of the inventory in a temporary root; it never writes
# a fixture into assets/inventory/.
set -uo pipefail
. access/tests/lib/assert.sh
command -v python3 >/dev/null 2>&1 || { l5_indeterminate "AT-017" "python3 not on PATH"; l5_exit; }
if [ ! -f assets/validate_assets.py ]; then l5_indeterminate "AT-017" "assets/validate_assets.py absent"; l5_exit; fi
if [ ! -d assets/inventory ]; then l5_indeterminate "AT-017" "PRE-K missing: assets/inventory"; l5_exit; fi
BASE="$(python3 assets/validate_assets.py | tail -n 1)"
case "$BASE" in
  "ASSET-VALIDATE: PASS"*) l5_pass "AT-017/inventory-baseline-clean" ;;
  *) l5_indeterminate "AT-017" "the live inventory is not clean before the test: $BASE"; l5_exit ;;
esac
TMP="$(mktemp -d)"
mkdir -p "$TMP/assets"
cp -r assets/. "$TMP/assets/"
cp assets/tests/fixtures/asset-owner-departed.yaml "$TMP/assets/inventory/at-017-orphan-fixture.yaml"
l5_refuses "AT-017/orphan-surfaces" "an asset whose owner departed and was not reassigned" \
  bash -c 'cd "$1" && python3 assets/validate_assets.py' _ "$TMP"
rm -f "$TMP/assets/inventory/at-017-orphan-fixture.yaml"
OWNER="$(python3 assets/resolve_holder.py capability:devops 2>/dev/null | sed 's/^RESOLVE: //')"
case "${OWNER:-NONE}" in
  ''|NONE|AMBIGUOUS) l5_indeterminate "AT-017/positive-control" "resolve_holder.py returned '${OWNER:-empty}'; do not invent an owner"; l5_exit ;;
esac
sed "s/__OWNER__/$OWNER/" assets/tests/fixtures/asset-owner-active.yaml > "$TMP/assets/inventory/at-017-owned-fixture.yaml"
l5_permits "AT-017/owned-asset-passes" "an identical asset with a resolving owner" \
  bash -c 'cd "$1" && python3 assets/validate_assets.py' _ "$TMP"
rm -rf "$TMP"
l5_exit
SH
chmod +x assets/tests/at-017-asset-owner-orphan.sh
bash assets/tests/at-017-asset-owner-orphan.sh
git add assets/tests
git commit -m "L5-07-11: AT-017 asset-owner orphan leg (spec 49.1)"
git push -u origin lane/5/07-at017
gh pr create --base integration --head lane/5/07-at017 --title "L5-07-11 AT-017 asset-owner orphan" --body "Negative: an unowned asset must surface. Positive control: an owned asset must not."
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | Script and both fixtures exist | `ls assets/tests/at-017-asset-owner-orphan.sh assets/tests/fixtures/asset-owner-departed.yaml assets/tests/fixtures/asset-owner-active.yaml \| wc -l` | `3` |
| 2 | The orphan surfaces and the owned asset passes | `bash assets/tests/at-017-asset-owner-orphan.sh \| tail -n 1` | `SUITE OK` |
| 3 | Three assertions pass, not two | `bash assets/tests/at-017-asset-owner-orphan.sh \| grep -c '^PASS AT-017'` | `3` |
| 4 | The test wrote no fixture into the real inventory | `ls assets/inventory \| grep -c 'at-017'` | `0` |
| 5 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^(access|infra|ops-vm|notify|assets)/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash assets/tests/at-017-asset-owner-orphan.sh | tail -n 1
bash assets/tests/at-017-asset-owner-orphan.sh | grep -c '^PASS AT-017'
ls assets/inventory | grep -c 'at-017'
git diff --name-only origin/integration...HEAD | grep -Ev '^(access|infra|ops-vm|notify|assets)/' | wc -l
```

Expected output, exactly:

```
SUITE OK
3
0
0
```

**STOP rules**

* `FAIL AT-017/orphan-surfaces` — the validator **accepted** an unowned asset. Section 49.1's orphan participation is unenforced and AT-017's asset-owner leg cannot pass. Do not weaken the fixture and do not edit `assets/validate_assets.py` from this task; it is another Lane 5 file's deliverable. Open a blocker issue with template B-1 naming both files.
* `INDETERMINATE AT-017/positive-control` — `resolve_holder.py` printed `NONE` or `AMBIGUOUS`. Do not invent, guess or pick a person. Open a blocker issue, `component: assets`, `blocking_dependency: L1 registries`, quoting the resolver output verbatim.
* If criterion 4 prints anything other than `0`, a fixture was written into the live inventory. Remove it with `git restore` before committing, and re-run the whole SELF-VERIFY.

---

### L5-07-12 — AT-106: Gate 1 notification, the push-event leg — S — AUTO

**Depends on:** L5-07-02. **Preconditions:** PRE-L.
**Writes:** `notify/tests/at-106-gate1-push.sh`.
**Spec:** AT-106 (Section 100.4) — "A Gate 1 submission notifies its resolved approver as a push event; breaching the approval turnaround target auto-raises the item's Blocked flag routed to the escalation role — a capacity signal, never a personal one — and the author may re-request to an active `plan_approval_delegate` or the Acting Team Lead designate as a recorded routing event." Section 92.11 — the push list is **closed**; push events go "to the designated messaging channel — a configuration value, never a hard-coded destination"; "If something appears urgent enough to page a person and is not on the push list, the correct response is a governed addition to the push list and the event taxonomy, never an ad-hoc alert." Section 97.3 — an event absent from the taxonomy cannot page anyone.

Lane 5 owns subsystem R, the **routing contract**. It does not own the Gate 1 submission event producer.

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout -B lane/5/07-at106 origin/integration
mkdir -p notify/tests

cat > notify/tests/at-106-gate1-push.sh <<'SH'
#!/usr/bin/env bash
# AT-106 (push-event leg) - spec 100.4 and 92.11. Lane 5 owns subsystem R, the routing
# contract. This test asserts the closed push list: Gate 1 is on it, the destination is
# configuration rather than a literal, the breach route and the re-request route are
# declared, and an event that is not on the list resolves to nothing.
set -uo pipefail
. access/tests/lib/assert.sh
PL=notify/routing/push-list.yaml
if [ ! -f "$PL" ]; then l5_indeterminate "AT-106" "PRE-L missing: $PL"; l5_exit; fi
if grep -Eqi 'gate[ _-]?1' "$PL"; then
  l5_pass "AT-106/gate-1-on-push-list"
else
  l5_fail "AT-106/gate-1-on-push-list" "the closed push list carries no Gate 1 entry (spec 92.11)"
fi
if grep -Eqi 'closed' "$PL"; then
  l5_pass "AT-106/list-declares-itself-closed"
else
  l5_fail "AT-106/list-declares-itself-closed" "the list does not declare itself closed (spec 92.11)"
fi
if grep -Eqi 'escalation' "$PL"; then
  l5_pass "AT-106/breach-routes-to-escalation-role"
else
  l5_fail "AT-106/breach-routes-to-escalation-role" "no escalation-role route for a breached turnaround target (AT-106)"
fi
if grep -qF 'plan_approval_delegate' "$PL"; then
  l5_pass "AT-106/re-request-route"
else
  l5_fail "AT-106/re-request-route" "the re-request route to an active plan_approval_delegate is not declared (AT-106)"
fi
# Negative 1: the destination is a configuration value, never a hard-coded one.
l5_refuses "AT-106/no-hard-coded-destination" "a literal webhook URL in the push list" \
  grep -Eq 'https?://' "$PL"
# Negative 2: the list is closed - an event absent from it resolves to nothing.
l5_refuses "AT-106/closed-list" "an event absent from the push list resolving a destination" \
  grep -qF 'lane5_not_a_real_event' "$PL"
l5_exit
SH
chmod +x notify/tests/at-106-gate1-push.sh
bash notify/tests/at-106-gate1-push.sh
git add notify/tests
git commit -m "L5-07-12: AT-106 Gate 1 push-event routing contract (spec 92.11)"
git push -u origin lane/5/07-at106
gh pr create --base integration --head lane/5/07-at106 --title "L5-07-12 AT-106 Gate 1 push" --body "Closed-push-list assertions, including the two negatives: no hard-coded destination, nothing off the list pages anyone."
```

**DECISION REQUIRED → L0 — DR-L5-07-C: the Gate 1 submission event producer.**

> AT-106 begins with "a Gate 1 submission notifies **its resolved approver**". The submission event and the approver resolution belong to **subsystem G — plan-checker and Gate 1 tooling**, which is **unassigned in PARTITION v1**. Lane 5 owns subsystem R and tests the routing contract only; it does not produce the event and does not resolve the approver.
>
> **What is blocked:** the end-to-end leg of AT-106 — a real Gate 1 submission arriving at a real approver — cannot be executed by any lane until G is assigned.
> **Default if L0 does not answer:** this test stands as the routing-contract half; the end-to-end half is reported unexecuted in the lane review. The executor does not build a Gate 1 producer, does not stub one, and does not fabricate an approver.
> **Route:** blocker issue, template B-1 of Section 8, `action_requested: L0 partition decision`.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | Script exists and is executable | `test -x notify/tests/at-106-gate1-push.sh && echo OK` | `OK` |
| 2 | All six assertions pass | `bash notify/tests/at-106-gate1-push.sh \| grep -c '^PASS AT-106'` | `6` |
| 3 | The suite is clean | `bash notify/tests/at-106-gate1-push.sh \| tail -n 1` | `SUITE OK` |
| 4 | The closed-list negative actually refuses | see SELF-VERIFY | `SUITE FAILURES=1` |
| 5 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^(access|infra|ops-vm|notify|assets)/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash notify/tests/at-106-gate1-push.sh | grep -c '^PASS AT-106'
bash notify/tests/at-106-gate1-push.sh | tail -n 1
cp notify/routing/push-list.yaml /tmp/l5-push-list.bak
printf '\n# lane5_not_a_real_event\n' >> notify/routing/push-list.yaml
bash notify/tests/at-106-gate1-push.sh | tail -n 1
cp /tmp/l5-push-list.bak notify/routing/push-list.yaml
git diff --name-only origin/integration...HEAD | grep -Ev '^(access|infra|ops-vm|notify|assets)/' | wc -l
```

Expected output, exactly:

```
6
SUITE OK
SUITE FAILURES=1
0
```

**STOP rules**

* `FAIL AT-106/no-hard-coded-destination` — the push list carries a literal URL. Section 92.11 makes the messaging channel a configuration value. Do not edit `notify/routing/push-list.yaml` from this task; it is another Lane 5 file's deliverable. Open a blocker issue with template B-1 naming the line.
* `FAIL AT-106/closed-list` — a token that is on no governed list resolves a destination, so the list is not closed and anything can page a person. Open a blocker issue at Blocking severity with template B-1 and stop the task.
* After the SELF-VERIFY, confirm `git status --short notify/routing/push-list.yaml` prints nothing. The temporary line is restored, never committed; if it is still present, restore it with `git restore notify/routing/push-list.yaml` before committing.

---

### L5-07-13 — AT-011, AT-049 and AT-107: the AI runtime contract — M — AUTO

**Depends on:** L5-07-02. **Preconditions:** PRE-M. **Out-of-lane:** EXT-1 (the validator is invoked, never edited), EXT-4 (`.github/workflows/**` is read, never written).
**Writes:** `access/tests/at-011-provider-swap.sh`, `access/tests/at-049-eval-suite-required.sh`, `access/tests/at-107-eval-regression-blocks-pin.sh`, `access/tests/fixtures/at-049-ai-runtime-dependency.yaml`, `access/tests/fixtures/at-049-eval-scenario.yaml`, `access/tests/fixtures/at-107-eval-baseline.json`, `access/tests/fixtures/at-107-eval-regression.json`, `access/tests/fixtures/at-107-eval-within-tolerance.json`.
**Spec:** AT-011 (Section 100.1) — "The approved runtime list is configuration. GSD, verification, GitHub, CI, production, ownership and review routing are all unchanged." Section 35.2 (the approved list: Claude Code, Codex, Antigravity, Cursor, Kilo Code, and Hermes Agent pinned at commit `8e9459c97f707047be5915a5c8b4c503756daa9b`, D69); Section 35.3 ("If a provider change would require changing any of those, the coupling is a defect to be removed"). AT-049 (Section 100.4) — "A product declaring an `ai_runtime_dependency` block without an evaluation suite under `verification/` fails CI, and a pinned-model change cannot merge without the suite passing." AT-107 (Section 100.4) — "A regression detected by the AI-eval scheduled runner creates the category-five incident (external model behaviour change), raises SIG-42, and blocks adoption of the new model pin until the evaluation suite passes or a recorded exception accepts the change." Section 38.1 ("Pin model snapshots, never floating aliases"); SIG-42, whose initial value is "any scored dimension falling more than 5 percentage points below its recorded baseline" (Section 52.2).

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout -B lane/5/07-ai-runtime origin/integration
mkdir -p access/tests/fixtures

cat > access/tests/fixtures/at-049-ai-runtime-dependency.yaml <<'YAML'
# AT-049 fixture block. Appended to a copy of L1's baseline product contract so the
# product declares a runtime AI dependency. Spec 38.1 requires a pinned snapshot.
ai_runtime_dependency:
  provider: fixture-provider
  pinned_model: fixture-model-2026-01-01
  monthly_cost_ceiling: 10
YAML

cat > access/tests/fixtures/at-049-eval-scenario.yaml <<'YAML'
# AT-049 positive control. Copied into <product>/verification/ai-eval/ so the same
# contract now carries the evaluation suite Section 38.1 requires.
scenarios:
  - id: at-049-fixture-scenario
    prompt: "fixture"
    expected: "fixture"
    scored_dimensions: [accuracy]
YAML

cat > access/tests/fixtures/at-107-eval-baseline.json <<'JSON'
{"run": "baseline", "scored_dimensions": {"accuracy": 92.0}}
JSON

cat > access/tests/fixtures/at-107-eval-regression.json <<'JSON'
{"run": "candidate-pin", "scored_dimensions": {"accuracy": 85.0}}
JSON

cat > access/tests/fixtures/at-107-eval-within-tolerance.json <<'JSON'
{"run": "candidate-pin", "scored_dimensions": {"accuracy": 90.5}}
JSON

cat > access/tests/at-011-provider-swap.sh <<'SH'
#!/usr/bin/env bash
# AT-011 - spec 100.1, 35.2, 35.3. The approved runtime list is CONFIGURATION: the
# names live in one file and nowhere else, so a provider change touches nothing else.
set -uo pipefail
. access/tests/lib/assert.sh
LIST=access/ai-runtime/approved-runtimes.yaml
if [ ! -f "$LIST" ]; then l5_indeterminate "AT-011" "PRE-M missing: $LIST"; l5_exit; fi
MISSING=""
for r in "Claude Code" "Codex" "Antigravity" "Cursor" "Kilo Code" "Hermes"; do
  grep -qiF "$r" "$LIST" || MISSING="$MISSING [$r]"
done
if [ -z "$MISSING" ]; then
  l5_pass "AT-011/list-is-complete"
else
  l5_fail "AT-011/list-is-complete" "approved runtimes missing from the list:$MISSING (spec 35.2)"
fi
if grep -qF '8e9459c97f707047be5915a5c8b4c503756daa9b' "$LIST"; then
  l5_pass "AT-011/hermes-pinned"
else
  l5_fail "AT-011/hermes-pinned" "Hermes Agent is not pinned at the commit spec 35.2 names (D69)"
fi
# Negative: no runtime name may appear outside the list. A name anywhere else is the
# coupling spec 35.3 calls a defect to be removed.
COUPLED="$(grep -rniE 'claude code|antigravity|kilo code' \
            .github/workflows access/model access/branch-protection access/permission-model \
            infra ops-vm notify 2>/dev/null || true)"
if [ -z "$COUPLED" ]; then
  l5_pass "AT-011/no-coupling-outside-the-list"
else
  l5_fail "AT-011/no-coupling-outside-the-list" "a runtime name is referenced outside the approved-runtime list: $COUPLED"
fi
l5_exit
SH

cat > access/tests/at-049-eval-suite-required.sh <<'SH'
#!/usr/bin/env bash
# AT-049 - spec 100.4 and 38.1: a product declaring ai_runtime_dependency without an
# evaluation suite under verification/ fails CI. The validator is L1-owned (EXT-1):
# this test invokes it against a temporary copy of L1's own baseline fixture and never
# edits validators/**.
set -uo pipefail
. access/tests/lib/assert.sh
BASE=validators/registry/fixtures/_baseline
AS_OF=2026-08-27   # L1's documented baseline as-of date
PY=""
command -v python3 >/dev/null 2>&1 && PY=python3
[ -z "$PY" ] && command -v python >/dev/null 2>&1 && PY=python
if [ -z "$PY" ]; then l5_indeterminate "AT-049" "no python interpreter on PATH"; l5_exit; fi
if [ ! -d "$BASE" ]; then l5_indeterminate "AT-049" "EXT-1 baseline fixture absent: $BASE"; l5_exit; fi
CLEAN="$(mktemp -d)"; cp -r "$BASE"/. "$CLEAN"/
if "$PY" -m validators.registry.cli --root "$CLEAN" --as-of "$AS_OF" --format json >/dev/null 2>&1; then
  l5_pass "AT-049/baseline-control"
else
  l5_indeterminate "AT-049" "L1's baseline fixture is not clean; the negative below would be unreadable"
  rm -rf "$CLEAN"; l5_exit
fi
NEG="$(mktemp -d)"; cp -r "$BASE"/. "$NEG"/
cat access/tests/fixtures/at-049-ai-runtime-dependency.yaml >> "$NEG/products/product-1/product.yaml"
l5_refuses "AT-049/no-eval-suite" "a product declaring ai_runtime_dependency with no verification/ai-eval suite" \
  "$PY" -m validators.registry.cli --root "$NEG" --as-of "$AS_OF" --format json
POS="$(mktemp -d)"; cp -r "$NEG"/. "$POS"/
mkdir -p "$POS/products/product-1/verification/ai-eval"
cp access/tests/fixtures/at-049-eval-scenario.yaml "$POS/products/product-1/verification/ai-eval/scenarios.yaml"
l5_permits "AT-049/with-eval-suite" "the same product once the evaluation suite exists" \
  "$PY" -m validators.registry.cli --root "$POS" --as-of "$AS_OF" --format json
rm -rf "$CLEAN" "$NEG" "$POS"
l5_exit
SH

cat > access/tests/at-107-eval-regression-blocks-pin.sh <<'SH'
#!/usr/bin/env bash
# AT-107 - spec 100.4: a regression detected by the AI-eval scheduled runner raises
# SIG-42 and blocks adoption of the new model pin. Tolerance is SIG-42's initial value
# (spec 52.2): more than 5 percentage points below the recorded baseline.
set -uo pipefail
. access/tests/lib/assert.sh
TOL=5
LIST=access/ai-runtime/approved-runtimes.yaml
if [ ! -f "$LIST" ]; then l5_indeterminate "AT-107" "PRE-M missing: $LIST"; l5_exit; fi
if grep -qF 'SIG-42' "$LIST"; then
  l5_pass "AT-107/sig-42-declared"
else
  l5_fail "AT-107/sig-42-declared" "the runtime configuration names no SIG-42 route for an eval regression"
fi
if grep -Eq '(^|[^0-9])5([^0-9]|$)' "$LIST"; then
  l5_pass "AT-107/tolerance-declared"
else
  l5_fail "AT-107/tolerance-declared" "the declared regression tolerance of 5 percentage points (SIG-42) is absent"
fi
FLOATING="$(grep -niF -e 'latest' -e '-preview' -e 'stable' "$LIST" 2>/dev/null || true)"
if [ -z "$FLOATING" ]; then
  l5_pass "AT-107/no-floating-alias"
else
  l5_fail "AT-107/no-floating-alias" "a model identifier uses a floating alias; spec 38.1 requires pinned snapshots: $FLOATING"
fi
score() { jq -r --arg d accuracy '.scored_dimensions[$d]' "$1"; }
B="$(score access/tests/fixtures/at-107-eval-baseline.json)"
R="$(score access/tests/fixtures/at-107-eval-regression.json)"
W="$(score access/tests/fixtures/at-107-eval-within-tolerance.json)"
blocks() { awk -v b="$1" -v c="$2" -v t="$TOL" 'BEGIN { exit ((b - c) > t) ? 0 : 1 }'; }
if blocks "$B" "$R"; then
  l5_pass "AT-107/regression-blocks-pin"
else
  l5_fail "AT-107/regression-blocks-pin" "a drop from $B to $R exceeds the ${TOL}pp tolerance and was not classified as a regression"
fi
if blocks "$B" "$W"; then
  l5_fail "AT-107/within-tolerance-adopts" "a run within tolerance ($B to $W) was wrongly classified as a regression"
else
  l5_pass "AT-107/within-tolerance-adopts"
fi
l5_exit
SH
chmod +x access/tests/at-011-provider-swap.sh access/tests/at-049-eval-suite-required.sh \
         access/tests/at-107-eval-regression-blocks-pin.sh
bash access/tests/at-011-provider-swap.sh
bash access/tests/at-049-eval-suite-required.sh
bash access/tests/at-107-eval-regression-blocks-pin.sh
git add access/tests/at-011-provider-swap.sh access/tests/at-049-eval-suite-required.sh \
        access/tests/at-107-eval-regression-blocks-pin.sh access/tests/fixtures
git commit -m "L5-07-13: AT-011, AT-049 and AT-107 AI runtime contract tests"
git push -u origin lane/5/07-ai-runtime
gh pr create --base integration --head lane/5/07-ai-runtime --title "L5-07-13 AT-011, AT-049, AT-107" --body "Provider-swap coupling negative, eval-suite CI negative against L1's validator, and the SIG-42 pin-adoption block."
```

**Boundary, stated once.** AT-107's incident and records legs — the category-five incident record and the `records/eval/` run history — live in the `control-plane-records` repository, which PARTITION gives entirely to **L4** (EXT-3). Lane 5 asserts nothing there. What Lane 5 owns is the runtime configuration that declares the tolerance, the SIG-42 route and the pin, and the arithmetic that decides whether a candidate pin is adoptable.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | Three scripts and five fixtures exist | `ls access/tests/at-011-provider-swap.sh access/tests/at-049-eval-suite-required.sh access/tests/at-107-eval-regression-blocks-pin.sh access/tests/fixtures/at-049-*.yaml access/tests/fixtures/at-107-*.json \| wc -l` | `8` |
| 2 | AT-011's three assertions pass | `bash access/tests/at-011-provider-swap.sh \| tail -n 1` | `SUITE OK` |
| 3 | AT-049 refuses the no-suite contract and permits the with-suite one | `bash access/tests/at-049-eval-suite-required.sh \| grep -c '^PASS AT-049'` | `3` |
| 4 | AT-107's five assertions pass | `bash access/tests/at-107-eval-regression-blocks-pin.sh \| grep -c '^PASS AT-107'` | `5` |
| 5 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -Ev '^(access|infra|ops-vm|notify|assets)/' \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash access/tests/at-011-provider-swap.sh | tail -n 1
bash access/tests/at-049-eval-suite-required.sh | grep -c '^PASS AT-049'
bash access/tests/at-107-eval-regression-blocks-pin.sh | grep -c '^PASS AT-107'
bash access/tests/at-107-eval-regression-blocks-pin.sh | tail -n 1
git diff --name-only origin/integration...HEAD | grep -Ev '^(access|infra|ops-vm|notify|assets)/' | wc -l
```

Expected output, exactly:

```
SUITE OK
3
5
SUITE OK
0
```

**STOP rules**

* `FAIL AT-049/no-eval-suite` — the validator **accepted** a product declaring `ai_runtime_dependency` with no evaluation suite. AT-049's CI leg is unenforced. Do not "fix" the fixture and do not edit `validators/**`; that is L1's path under PARTITION. Open a blocker issue against L1 with template B-1 and stop.
* `FAIL AT-011/no-coupling-outside-the-list` — a runtime name is wired into CI, access configuration or infrastructure, so changing provider would change more than configuration. Section 35.3 calls that coupling a defect to be removed. Open a blocker issue naming every file and line the check printed; remove nothing yourself outside this task's own paths.
* `FAIL AT-107/no-floating-alias` — a model identifier floats. Section 38.1 requires pinned snapshots so a model change is a visible, reviewed change. Open a blocker issue against the Lane 5 file owning `access/ai-runtime/**`.

---

### L5-07-14 — AT-029 and AT-035: control-plane loss and the organisation-export restore — M — ASSISTED

**Depends on:** L5-07-02. **Preconditions:** PRE-E, PRE-K, PRE-N. **Out-of-lane:** EXT-4 (`.github/workflows/**` is read, never written).
**Writes:** `ops-vm/tests/at-029-control-plane-unreachable.sh`, `ops-vm/tests/at-035-org-export-restore.sh`, `access/tests/human-actions/L5-07-14-AT-029.md`, `access/tests/human-actions/L5-07-14-AT-035.md`.
**Spec:** AT-029 (Section 100.3) — "All products continue serving customers, and a production rollback can still be executed via the documented manual path." Section 45.2 (control-plane outage: products keep running, CI keeps running, deployment keeps running; machine detection stops for every product simultaneously and the outage is raised by the off-VM liveness leg of Section 51.5 "and by nothing on the VM"); Section 46.1 (the manual path: locally cached digests on the production host plus a pull-only registry credential); Section 51.3 ("Nothing in a product's runtime path touches the operations VM"). AT-035 (Section 100.3) — "The scheduled organisation export restores successfully to an independent environment, each data class through its own recorded mechanism per Section 45.3 — Projects boards via their GraphQL dump, never assumed present in a migration archive — and the restore test is recorded within the same rolling 90-day discipline as product backups (D80)." Section 45.3 (append-only write-only credential; object-locked versioned storage; encryption with a key held outside GitHub; restore-test environments wiped after each test); SIG-34.

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout -B lane/5/07-at029-at035 origin/integration
mkdir -p ops-vm/tests access/tests/human-actions

cat > ops-vm/tests/at-029-control-plane-unreachable.sh <<'SH'
#!/usr/bin/env bash
# AT-029 - spec 100.3, 45.2, 46.1, 51.3. Static half proves the two properties the
# drill depends on: detection lives OFF the operations VM, and no product runtime path
# touches it. The live half (VM down, products serving, manual rollback) is ASSISTED.
set -uo pipefail
. access/tests/lib/assert.sh
UP=assets/inventory/detection-leg-external-uptime.yaml
DM=assets/inventory/detection-leg-dead-mans-switch.yaml
if [ ! -f "$UP" ] || [ ! -f "$DM" ]; then
  l5_indeterminate "AT-029/static" "PRE-K missing an off-VM detection leg: $UP or $DM (spec 51.5)"
  l5_exit
fi
OFFVM=0
for f in "$UP" "$DM"; do
  v="$(yq -r '.runs_off_operations_vm // ""' "$f")"
  if [ "$v" != "true" ]; then
    l5_fail "AT-029/static-detection-off-vm" "$f does not declare runs_off_operations_vm: true (spec 45.2, 51.5)"
    OFFVM=1
  fi
done
[ "$OFFVM" -eq 0 ] && l5_pass "AT-029/static-detection-off-vm"
# spec 45.2, 51.3: flag only workflows that TARGET the ops-vm as a deployment
# environment or runner host — not workflows that merely reference ops-vm script
# paths as arguments (e.g. L5-04's contract with L2 calls ops-vm/export/put.sh
# as a run: argument, which is permitted). Grep for runner/host/ssh directives.
RUNTIME="$(grep -rlE '(runs-on[[:space:]]*:[[:space:]]*.*ops-vm|environment[[:space:]]*:[[:space:]]*.*ops-vm|ssh[[:space:]].*ops-vm)' .github/workflows 2>/dev/null || true)"
if [ -z "$RUNTIME" ]; then
  l5_pass "AT-029/static-no-runtime-dependency"
else
  l5_fail "AT-029/static-no-runtime-dependency" "a workflow deploys to or runs on the operations VM (spec 45.2, 51.3 — runner/host dependency, not a script-path reference): $RUNTIME"
fi
RT="$(ls .github/workflows 2>/dev/null | grep -c 'restore-test')"
if [ "$RT" -ge 1 ]; then
  l5_pass "AT-029/static-restore-test-workflow-present"
else
  l5_fail "AT-029/static-restore-test-workflow-present" "no restore-test workflow exists (spec 99.2 row E); the quarterly drill has no runner"
fi
bash access/tests/lib/verify-evidence.sh AT-029
RC=$?
if [ "$RC" -eq 2 ]; then echo "INCOMPLETE AT-029 :: awaiting human evidence"; exit 2; fi
if [ "$RC" -eq 0 ]; then l5_pass "AT-029/live"; else l5_fail "AT-029/live" "evidence verification failed"; fi
l5_exit
SH

cat > ops-vm/tests/at-035-org-export-restore.sh <<'SH'
#!/usr/bin/env bash
# AT-035 - spec 100.3 and 45.3 (D80). Static half proves the export's four declared
# properties; the live half (restore to an independent environment, decrypt, wipe) is
# ASSISTED and is executed by a named human.
set -uo pipefail
. access/tests/lib/assert.sh
EXP=ops-vm/org-export/export.sh
if [ ! -x "$EXP" ]; then l5_indeterminate "AT-035/static" "PRE-N missing or not executable: $EXP"; l5_exit; fi
if grep -qiE 'graphql' "$EXP"; then
  l5_pass "AT-035/static-projects-graphql-dump"
else
  l5_fail "AT-035/static-projects-graphql-dump" "the export declares no separate Projects v2 GraphQL dump; spec 45.3 forbids assuming boards are in the migration archive"
fi
if grep -qiE 'object.?lock|append.?only|write.?only' "$EXP"; then
  l5_pass "AT-035/static-write-only-object-locked"
else
  l5_fail "AT-035/static-write-only-object-locked" "the export declares no append-only, write-only credential against object-locked storage (spec 45.3)"
fi
if grep -qiE 'encrypt' "$EXP"; then
  l5_pass "AT-035/static-encrypted"
else
  l5_fail "AT-035/static-encrypted" "the export declares no encryption; spec 45.3 requires a key held outside GitHub"
fi
KEY=assets/inventory/org-export-encryption-key.yaml
TOK=assets/inventory/machine-credential-organisation-export-token.yaml
if [ -f "$KEY" ] && [ -f "$TOK" ]; then
  l5_pass "AT-035/static-inventory-entries"
else
  l5_fail "AT-035/static-inventory-entries" "the export key or its token has no asset entry (spec 45.3, 49.1)"
fi
WIN="$(yq -r '.checks[] | select(.check_id == "AT-035") | .revalidate_after_days' access/tests/coverage.yaml)"
if [ "$WIN" = "90" ]; then
  l5_pass "AT-035/static-90-day-window"
else
  l5_fail "AT-035/static-90-day-window" "the restore-test clock is ${WIN}d; D80 sets a rolling 90-day discipline"
fi
bash access/tests/lib/verify-evidence.sh AT-035
RC=$?
if [ "$RC" -eq 2 ]; then echo "INCOMPLETE AT-035 :: awaiting human evidence"; exit 2; fi
if [ "$RC" -eq 0 ]; then l5_pass "AT-035/live"; else l5_fail "AT-035/live" "evidence verification failed"; fi
l5_exit
SH

cat > access/tests/human-actions/L5-07-14-AT-029.md <<'MD'
# HUMAN ACTION REQUIRED — L5-07-14 / AT-029

**Executor:** DevOps-capability holder, with the Founder informed before the window opens
**Why a human:** the step stops the operations VM and executes a production rollback; no AI executor may do either
**Spec clause:** Section 100.3, AT-029 — "All products continue serving customers, and a production rollback can still be executed via the documented manual path."
**Expected result:** the control plane is unreachable for the whole window, and every leg below holds.

## Steps
| # | Attempt | Required outcome |
| --- | --- | --- |
| 1 | Stop the operations VM for the declared window | Control plane **unreachable** — dashboards, Scorecard, DevLake and reconciliation all down |
| 2 | Poll each product's `/health` endpoint directly for the window | **Serving** throughout (spec 45.2) |
| 3 | Execute a production rollback on the named drill product using only the locally cached digest and the pull-only registry credential | **Succeeds** without the pipeline, the dashboard or the board (spec 46.1) |
| 4 | Confirm the outage was raised by the off-VM liveness leg and by nothing on the VM | **Raised off-VM** (spec 45.2, 51.5) |

## Record the result
Run:
    bash access/tests/lib/record-evidence.sh AT-029 pass "<observed, one line per leg, naming the drill product>"
Then commit the produced file under access/tests/evidence/ on branch lane/5/07-evidence.
MD

cat > access/tests/human-actions/L5-07-14-AT-035.md <<'MD'
# HUMAN ACTION REQUIRED — L5-07-14 / AT-035

**Executor:** DevOps-capability holder; the encryption key is opened by its named holder
**Why a human:** the step restores the organisation archive into an independent environment and opens the escrowed key; no AI executor may hold that key
**Spec clause:** Section 100.3, AT-035 — "The scheduled organisation export restores successfully to an independent environment, each data class through its own recorded mechanism per Section 45.3 — Projects boards via their GraphQL dump, never assumed present in a migration archive — and the restore test is recorded within the same rolling 90-day discipline as product backups (D80)."
**Expected result:** the archive decrypts and restores, and the environment is destroyed on evidence.

## Steps
| # | Attempt | Required outcome |
| --- | --- | --- |
| 1 | Decrypt the most recent export with the key held outside GitHub | **Decrypts** — a restore that cannot decrypt is a failed restore test (spec 45.3) |
| 2 | Restore repositories, issues, pull requests and review records into a clean, independent environment | **Recoverable**, not merely present |
| 3 | Restore the Projects v2 boards from their own GraphQL dump | **Recoverable** through their own mechanism |
| 4 | Confirm the export's write credential cannot read, overwrite or delete previous runs | **Refused** on all three |
| 5 | Wipe the restore-test environment and record the provider's post-test resource listing | **Zero resources** remaining |

## Record the result
Run:
    bash access/tests/lib/record-evidence.sh AT-035 pass "<observed, one line per leg, with the zero-resources listing referenced>"
Then commit the produced file under access/tests/evidence/ on branch lane/5/07-evidence.
MD

chmod +x ops-vm/tests/at-029-control-plane-unreachable.sh ops-vm/tests/at-035-org-export-restore.sh
bash ops-vm/tests/at-029-control-plane-unreachable.sh
bash ops-vm/tests/at-035-org-export-restore.sh
git add ops-vm/tests access/tests/human-actions
git commit -m "L5-07-14: AT-029 control-plane-unreachable and AT-035 org-export restore tests"
git push -u origin lane/5/07-at029-at035
gh pr create --base integration --head lane/5/07-at029-at035 --title "L5-07-14 AT-029 and AT-035" --body "Static preconditions for both drills plus the two human-action cards. Both live halves are ASSISTED."
echo "ASSISTED-HALT L5-07-14 AT-029,AT-035"
```

**DECISION REQUIRED → L0 — DR-L5-07-D: the AT-029 drill product and window.**

> AT-029's legs 2 and 3 run against a live product: PARTITION states the eight products are "onboarded per-product, not built", so no lane owns a product repository and no executor in this lane may choose which product carries a rollback drill, or when production may be taken through one. L0 must name (a) the drill product, (b) the DevOps human executing, and (c) the authorised window.
>
> **What is blocked:** AT-029 stays `INCOMPLETE`; its static half stands.
> **Default if L0 does not answer:** `INCOMPLETE` — never `PASS`. The executor does not choose a product, does not shorten the window, and does not run legs 2 and 3 against a fixture and call it AT-029.
> **Route:** blocker issue, template B-1 of Section 8, `action_requested: L0 decision`.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | Both scripts exist and are executable | `test -x ops-vm/tests/at-029-control-plane-unreachable.sh && test -x ops-vm/tests/at-035-org-export-restore.sh && echo OK` | `OK` |
| 2 | AT-029's three static assertions pass | `bash ops-vm/tests/at-029-control-plane-unreachable.sh \| grep -c '^PASS AT-029/static'` | `3` |
| 3 | AT-035's five static assertions pass | `bash ops-vm/tests/at-035-org-export-restore.sh \| grep -c '^PASS AT-035/static'` | `5` |
| 4 | Both live halves are INCOMPLETE, never PASS, before evidence | `bash ops-vm/tests/at-029-control-plane-unreachable.sh >/dev/null 2>&1; echo "rc=$?"` | `rc=2` |
| 5 | The AT-029 card lists four legs and the AT-035 card five | `grep -c '^| [1-4] ' access/tests/human-actions/L5-07-14-AT-029.md; grep -c '^| [1-5] ' access/tests/human-actions/L5-07-14-AT-035.md` | `4` then `5` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash ops-vm/tests/at-029-control-plane-unreachable.sh | grep -c '^PASS AT-029/static'
bash ops-vm/tests/at-035-org-export-restore.sh | grep -c '^PASS AT-035/static'
bash ops-vm/tests/at-029-control-plane-unreachable.sh >/dev/null 2>&1; echo "rc=$?"
bash ops-vm/tests/at-035-org-export-restore.sh >/dev/null 2>&1; echo "rc=$?"
grep -c '^| [1-4] ' access/tests/human-actions/L5-07-14-AT-029.md
grep -c '^| [1-5] ' access/tests/human-actions/L5-07-14-AT-035.md
```

Expected output, exactly:

```
3
5
rc=2
rc=2
4
5
```

**STOP rules**

* `FAIL AT-029/static-no-runtime-dependency` — a product path references the operations VM, which Section 51.3 forbids outright and on which Section 45.2's "products keep running" depends. Do not edit `.github/workflows/**`; EXT-4 gives that tree to L2. Open a blocker issue against L2 with template B-1 at Blocking severity and stop the task.
* `FAIL AT-035/static-encrypted` or `FAIL AT-035/static-write-only-object-locked` — the export is not protected the way Section 45.3 requires, so the event that takes the organisation can also take the export. Open a blocker issue with template B-2 at Blocking severity against the Lane 5 file owning `ops-vm/org-export/**` and stop the lane.
* The AI executor may under no circumstance stop the operations VM, execute a production rollback, open the export encryption key, or delete a restore-test environment.

---

## 5. The Lane 5 daily runbook

Everything below is literal. Run it from the root of the `control-plane` working copy. `<TASK>` is a task id from Section 4 with the `L5-07-` prefix dropped and lowercased, e.g. `L5-07-11` → `07-t11`; branch names follow the ones each task's command block already names.

### 5.1 Start of day

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git switch integration
git pull --ff-only
bash access/tests/lane5.sh | tail -n 1
bash access/tests/check-coverage.sh | tail -n 1
```

Expected, two lines: `LANE5 SUITE OK` and `COVERAGE OK`. `LANE5 SUITE FAIL` before you have written anything today is a **STOP**: something merged yesterday broke a control. Open a blocker issue (Section 8) before starting any new task.

If `git pull --ff-only` fails, `integration` has local commits. Do not merge and do not force. Run `git log --oneline origin/integration..integration` and file blocker template B-1 — a lane never rewrites `integration` (PARTITION, branch and merge model).

### 5.2 Start a task

```bash
set -euo pipefail
git switch integration
git pull --ff-only
git switch -c lane/5/07-t11          # the branch name the task's own block names
git status --short                    # expect: no output
```

Then run the task's fenced block from its first line, in order, without reordering and without skipping the `bash <script>` lines that execute the test before it is committed.

### 5.3 Verify before you commit

```bash
set -euo pipefail
# 1. The whole suite, not only today's test
bash access/tests/lane5.sh | tail -n 1

# 2. The coverage manifest in both directions
bash access/tests/check-coverage.sh | tail -n 1

# 3. The lane-guard pre-check - run this EVERY time, before every commit
git add -A
git diff --cached --name-only \
  | grep -Ev '^(access|infra|ops-vm|notify|assets)/' \
  | tee /tmp/l5-foreign-paths.txt
wc -l < /tmp/l5-foreign-paths.txt      # expect: 0
```

`0` means every staged path is Lane 5's. Any other number means the PR will fail the lane-guard check (PARTITION rule 1) — fix it now, per Section 5.5, not after the PR opens.

A new test script that is in no `coverage.yaml` row makes step 2 print `COVERAGE FAIL`. Lane 5 adds no test file the manifest does not name, and names no file it has not written.

### 5.4 Open the PR

```bash
set -euo pipefail
git commit -m "L5-07-11: AT-017 asset-owner orphan leg (spec 49.1)"
git push -u origin HEAD
gh pr create --base integration --head "$(git branch --show-current)" \
  --title "L5-07-11 AT-017 asset-owner orphan" \
  --body "Lane: L5 (Access, Infra & Ops)
Task: L5-07-11
Paths touched: assets/** only
Suite: LANE5 SUITE OK
Coverage: COVERAGE OK
Spec: Section 49.1, AT-017
SELF-VERIFY output pasted below."
gh pr checks --watch
```

Then **stop**. Do not run `gh pr merge`. `integration` is merged by L0 in the fixed train order L1 → L4 → L2 → L3 → **L5**, and Lane 5 is last. A lane never merges its own PR into the train and never merges or rebases another lane's branch.

### 5.5 A failing lane-guard check

```bash
set -euo pipefail
gh pr checks | grep -i lane-guard
gh pr diff --name-only | grep -Ev '^(access|infra|ops-vm|notify|assets)/'
```

The second command prints the offending paths. For each one:

| Situation | Action |
| --- | --- |
| Touched by accident (formatter, editor, a stray `git add -A`) | `git restore --source=origin/integration --staged --worktree <path>`, then re-run Section 5.3 |
| New and should never have been created | `git rm --cached <path> && rm <path>`, then re-run Section 5.3 |
| Genuinely needed in another lane's path | **Do not edit it.** File blocker template B-3 and continue the task without that change |
| Under `contracts/**`, `validators/**`, `.github/workflows/**` or `reconciler/**` | **Never.** These are EXT-1, EXT-2 and EXT-4. File blocker template B-3 |

Re-verify, then force-push with lease:

```bash
set -euo pipefail
git diff --name-only origin/integration...HEAD \
  | grep -Ev '^(access|infra|ops-vm|notify|assets)/' | wc -l   # expect: 0
git push --force-with-lease
gh pr checks --watch
```

### 5.6 The ASSISTED cycle — where a human executes

This is the operational form of Section 1.1 and it has exactly three moves.

**Move 1 — emit and halt.** The task's block writes the test and the human-action card, commits both, prints `ASSISTED-HALT <TASK-ID> <CHECK-ID>` and stops. Nothing else in that task runs.

```bash
set -euo pipefail
gh issue create \
  --title "HUMAN ACTION: <CHECK-ID> for <TASK-ID>" \
  --label lane-5 --label human-action \
  --body "Card: access/tests/human-actions/<TASK-ID>-<CHECK-ID>.md
Executor named on the card. The AI executor has halted at ASSISTED-HALT and will not proceed.
Return path: bash access/tests/lib/record-evidence.sh <CHECK-ID> <pass|fail> \"<observed>\"
then commit the evidence file on branch lane/5/07-evidence."
```

**Move 2 — the human executes.** The named human performs the card's steps and runs `record-evidence.sh`. The AI executor does not run it, does not edit its output, and does not open the evidence file to "tidy" it.

**Move 3 — verify, next cycle.**

```bash
set -euo pipefail
git fetch origin && git switch integration && git pull --ff-only
bash access/tests/lib/verify-evidence.sh <CHECK-ID>; echo "rc=$?"
```

| Output | Meaning | Action |
| --- | --- | --- |
| `PASS <CHECK-ID>`, `rc=0` | The control refused what it must refuse | The task completes; record it in the PR body |
| `INCOMPLETE <CHECK-ID> :: no evidence file`, `rc=2` | The human has not executed yet | Report `INCOMPLETE`. Never `FAIL`. Do not proceed to a dependent task |
| `INCOMPLETE <CHECK-ID> :: evidence is Nd old, limit Md`, `rc=2` | The evidence expired (Section 1.1) | Re-issue the human-action card; the check reverts to `INCOMPLETE` |
| `FAIL <CHECK-ID> :: evidence author equals test committer`, `rc=1` | The separation of Section 1.1 was broken | Open a blocker issue with template B-2. Never re-run the recorder yourself |
| `FAIL <CHECK-ID> :: recorded result is not pass`, `rc=1` | The control did **not** refuse | Blocker issue, template B-2, Blocking severity. Stop the lane |

### 5.7 End of day

```bash
set -euo pipefail
git push -u origin HEAD                # never leave work only on the local machine
gh pr view --json number,statusCheckRollup -q '.number, (.statusCheckRollup[].conclusion)'
bash access/tests/lane5.sh | tail -n 1
```

A Lane 5 branch is short-lived — under one working day (PARTITION, branch and merge model). A branch older than one working day is itself a blocker: file template B-1 saying so rather than carrying it.

---

## 6. The revalidation sweep

Evidence expires (Section 1.1). Run this sweep at the start of every lane cycle and on the first working day of every month. It writes nothing and adds no file to the tree.

```bash
set -u
cd "$CONTROL_PLANE_ROOT"
STALE=0
for id in $(yq -r '.checks[].check_id' access/tests/coverage.yaml); do
  out="$(bash access/tests/lib/verify-evidence.sh "$id" 2>&1)"
  case "$out" in
    PASS*) : ;;
    INCOMPLETE*) echo "$out"; STALE=$((STALE+1)) ;;
    *) echo "$out"; STALE=$((STALE+1)) ;;
  esac
done
echo "REVALIDATION STALE=$STALE"
```

Every line printed before the summary is a check whose evidence is absent or aged past its `revalidate_after_days`. Each one is re-issued as a human-action card through Section 5.6, in the order Section 3.2 lists them. `REVALIDATION STALE=0` is the only state in which Lane 5 may report the Phase 1 completion check of spec Section 98.2 as met.

The AUTO checks — NC-08, NC-09, NC-13, AT-011, AT-017, AT-049, AT-089, AT-091, AT-092, AT-096, AT-097, AT-100, AT-106, AT-107 — carry no evidence file; they are re-executed by `access/tests/lane5.sh` on every cycle, which is what their 30-day revalidation window means.

---

## 7. DECISION REQUIRED → L0, collected

Every routing block in Section 4, in one table, so L0 sees the whole set at once. None of these may be decided by the executor; each one's default is the same — the check stays `INCOMPLETE`, never `PASS`, never `FAIL`.

| ID | Raised in | What L0 must decide | Blocked until answered |
| --- | --- | --- | --- |
| DR-L5-07-A | L5-07-09 | Who holds the second organisation Owner or the escrowed break-glass credential; who is the named escrow custodian (Section 14.4); when the continuity drill runs | AT-022, NC-12 |
| DR-L5-07-B | L5-07-10 | Assignment of subsystems **H** (dashboards and views) and **P** (people intelligence engine), and of the conduct store — all unassigned in PARTITION v1 | The dashboard-level leg of AT-092 and AT-089; the engine-level leg of AT-090 and AT-096; the complaint-path leg of AT-100 |
| DR-L5-07-C | L5-07-12 | Assignment of subsystem **G** (plan-checker and Gate 1 tooling), unassigned in PARTITION v1 | The end-to-end leg of AT-106 |
| DR-L5-07-D | L5-07-14 | The AT-029 drill product, the executing DevOps human, and the authorised window | AT-029 |

Subsystems **G, H, J, O and P** are unassigned in PARTITION v1. Lane 5 states the dependency where it meets one and claims none of them. No task in this file builds, stubs or simulates any part of an unassigned subsystem, and no executor widens a Lane 5 test to cover one.

---

## 8. The blocker-issue template

Every STOP rule in this file ends here. File blockers in the `control-plane` repository, from inside the working copy so `gh` infers the repository. Never continue a task past its STOP rule, and never edit a test to make a STOP rule stop firing.

### B-1 — Standard blocker

```bash
set -euo pipefail
gh issue create \
  --title "BLOCKER L5-07-T<nn>: <the STOP rule that fired, in one line>" \
  --label blocker --label lane-5 \
  --body "Lane: L5 (Access, Infra & Ops)
Task: L5-07-T<nn>
STOP rule that fired: <quote it from the task, verbatim>

Command run (verbatim):
<paste>

Observed (verbatim):
<paste>

Expected:
<paste the task's 'Expected output, exactly' block>

Spec citation: <Section n.n / AT-nnn / invariant nn / SIG-nn / D-nn - quote it>
Owning lane of any foreign path involved (PARTITION.md): <L0 / L1 / L2 / L3 / L4>
Action taken: Lane 5 work stopped at commit $(git rev-parse --short HEAD).
No test was modified, no foreign path was edited, no privileged step was attempted.
Decision needed from: L0 Integrator."
```

### B-2 — Security-class blocker (a control that did not refuse)

Use this whenever a negative check reports that something forbidden was **permitted**, whenever evidence separation is broken, and for every STOP rule in this file that names Section 43.

```bash
set -euo pipefail
gh issue create \
  --title "SECURITY BLOCKER L5-07-T<nn>: <control> did not refuse <action>" \
  --label blocker --label lane-5 --label security \
  --body "Lane: L5 (Access, Infra & Ops)
Task: L5-07-T<nn>
Check id: <NC-nn or AT-nnn>
Severity: Blocking

What was permitted that must be refused:
<one sentence>

Command run (verbatim):
<paste>

Observed (verbatim):
<paste>

Spec citation: <Section 11.1 / 11.3 / 40.1 / 90.3 / 98.2 / invariant n - quote it>
Action taken: the whole lane is stopped at commit $(git rev-parse --short HEAD).
Nothing was retried, no configuration was 'fixed' from the test, no evidence was authored.
Section 40.1 treats a credential in the wrong tier as a security incident under Section 43,
not as a build defect. Decision needed from: L0 Integrator."
```

### B-3 — Contract Change Request (a foreign path is genuinely needed)

```bash
set -euo pipefail
gh issue create \
  --title "CCR from L5-07: <the change needed in a path Lane 5 does not own>" \
  --label contract-change-request --label lane-5 \
  --body "Requesting lane: L5
Task: L5-07-T<nn>
Path needed (owned by another lane or by L0): <path>
Owning lane per PARTITION.md: <L0 / L1 / L2 / L3 / L4>
Out-of-lane dependency id from Section 2 of L5-07: <EXT-1 / EXT-2 / EXT-3 / EXT-4>
Why Lane 5 needs it: <one paragraph, factual>
Proposed content: <exact text or diff>
Lane 5 has NOT edited the path. PARTITION rule 2: a lane needing a contract change files a
Contract Change Request; it never edits contracts/**."
```

---

## 9. Dependency graph and sizes

| Task | Title | Size | Mode | Depends on |
| --- | --- | --- | --- | --- |
| L5-07-01 | Test harness skeleton and evidence machinery | S | AUTO | none |
| L5-07-02 | The coverage manifest and its self-check | S | AUTO | T01 |
| L5-07-03 | NC-08: the no-API-keys check, executed | S | AUTO | T02 |
| L5-07-04 | NC-09 and NC-13: exception-validator negative, org-export schedule | S | AUTO | T02 |
| L5-07-05 | NC-01..NC-07, NC-10, NC-11: the live branch-protection negatives | L | ASSISTED | T02 |
| L5-07-06 | AT-108: the founder ops console is provably read-only | M | ASSISTED | T02 |
| L5-07-07 | AT-109: the background cage egress wall holds | M | ASSISTED | T02 |
| L5-07-08 | AT-097 and AT-098: Grafana instance separation | M | AUTO + ASSISTED | T02 |
| L5-07-09 | AT-110 and AT-022: reconciler bounds and the break-glass Owner | M | ASSISTED + HUMAN-GATED | T02 |
| L5-07-10 | AT-089, AT-090, AT-091, AT-092, AT-096, AT-100: Layer B reach and conduct separation | M | AUTO + ASSISTED | T02 |
| L5-07-11 | AT-017: the asset-owner orphan leg | S | AUTO | T02 |
| L5-07-12 | AT-106: Gate 1 notification, the push-event leg | S | AUTO | T02 |
| L5-07-13 | AT-011, AT-049 and AT-107: the AI runtime contract | M | AUTO | T02 |
| L5-07-14 | AT-029 and AT-035: control-plane loss and the organisation-export restore | M | ASSISTED | T02 |

T01 → T02 is the only hard chain. Every task from T03 to T14 depends on T02 alone and on nothing else in this file, so they run in any order and in parallel on their own branches — which is what keeps a Lane 5 branch under one working day. The ASSISTED and HUMAN-GATED tasks (T05, T06, T07, T09, T10, T14) halt at their card and are completed on a later cycle by Section 5.6; they never block an AUTO task.

---

## 10. Standing rules for anyone extending this suite

1. A new Lane 5 test goes in `access/tests/`, `infra/tests/`, `ops-vm/tests/`, `notify/tests/` or `assets/tests/` — nowhere else (PARTITION rule 1) — and it goes into `access/tests/coverage.yaml` in the same commit, or `check-coverage.sh` fails in both directions by design.
2. A test is never weakened to make a build pass, and a STOP rule is never edited to stop firing. The test is the enforcement; spec Section 11.1's failure mode is a gate that appears to be working and is not.
3. Every new check that can be phrased negatively is phrased negatively and ships with exactly one paired positive control, so a uniformly broken environment cannot pass by refusing everything (Section 3.1).
4. Anything unevaluable prints `INDETERMINATE` and exits non-zero. A check that cannot reach its subject fails; it never reports zero findings.
5. The AI executor never writes an evidence file, never performs a step on a human-action card, and never marks an ASSISTED check passed from a dry run. `INCOMPLETE` is the honest state and it is never upgraded by hand.
6. No task in this file claims a path, a repository or a subsystem PARTITION v1 has not assigned to Lane 5. Where a leg needs G, H, J, O or P, it is routed to L0 through Section 7 and left unexecuted — never stubbed, never simulated, never quietly rescoped.

---

## 11. Pending mutation script deliverables

The tasks in this section create the mutation scripts listed as `MUTATION-NEEDED` in `protocol/03-invariant-tests.md` §6.5. Each script mutates the fixture so the named negative test flips from PASS to FAIL, proving the test is not vacuous.

### L5-IT021-N1 — Create IT-021-N1.mutation.sh — S — AUTO

**Depends on:** L5-07-01.
**Writes:** `access/invariant-tests/mutations/IT-021-N1.mutation.sh`.
**Spec:** `protocol/03-invariant-tests.md` §6.5 (`# MUTATION-NEEDED: create IT-021-N1.mutation.sh`). The mutation grants the unattended personal-agent identity direct-push permission on the fixture's default branch so the push-to-default-branch attempt succeeds. Under the mutation IT-021-N1 must flip from PASS to FAIL.

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout -B lane/5/it021-n1-mutation origin/integration
mkdir -p access/invariant-tests/mutations

cat > access/invariant-tests/mutations/IT-021-N1.mutation.sh << 'EOF'
#!/usr/bin/env bash
# Mutation: grant the unattended personal-agent identity direct-push permission
# on the fixture's default branch by removing the branch-protection rule that
# blocks non-admin direct pushes to the default branch.
# Expected result: IT-021-N1 flips from PASS to FAIL.
# Spec: protocol/03-invariant-tests.md §6.5 (MUTATION-NEEDED IT-021-N1).
set -euo pipefail
REPO="${FIXTURE_REPO:?}"
# Remove the required pull-request-reviews restriction so direct pushes are
# permitted. Also disable enforce_admins so the unattended identity can push.
gh api --method PUT \
  "repos/${REPO}/branches/main/protection" \
  --field required_status_checks=null \
  --field enforce_admins=false \
  --field required_pull_request_reviews=null \
  --field restrictions=null
echo "IT-021-N1 mutation applied: direct-push to default branch now permitted for unattended identity in ${REPO}"
EOF
chmod +x access/invariant-tests/mutations/IT-021-N1.mutation.sh
git add access/invariant-tests/mutations/IT-021-N1.mutation.sh
git commit -m "L5-IT021-N1: create IT-021-N1.mutation.sh (grant unattended identity direct-push permission)"
git push -u origin lane/5/it021-n1-mutation
gh pr create --base integration --head lane/5/it021-n1-mutation \
  --title "L5-IT021-N1: IT-021-N1 mutation script (unattended direct-push permission)" \
  --body "Creates IT-021-N1.mutation.sh per protocol/03-invariant-tests.md §6.5."
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | Script exists and is executable | `test -x access/invariant-tests/mutations/IT-021-N1.mutation.sh && echo OK` | `OK` |

**SELF-VERIFY**

```bash
test -x access/invariant-tests/mutations/IT-021-N1.mutation.sh && \
echo "IT-021-N1.mutation.sh present and executable"
```

Expected output, exactly: `IT-021-N1.mutation.sh present and executable`

**STOP rule:** If applying the mutation does not cause IT-021-N1 to exit non-zero, the test is vacuous. File a blocker titled `VACUOUS-TEST IT-021-N1` and stop the lane immediately.

---

### L5-IT021-N2 — Create IT-021-N2.mutation.sh — S — AUTO

**Depends on:** L5-07-01.
**Writes:** `access/invariant-tests/mutations/IT-021-N2.mutation.sh`.
**Spec:** `protocol/03-invariant-tests.md` §6.5 (`# MUTATION-NEEDED: create IT-021-N2.mutation.sh`). The mutation removes the Code-Owner-approval requirement from the unattended PR's branch protection so a flagged-unattended PR can merge without the full human gate sequence (Code Owner approval on the most recent push). Under the mutation IT-021-N2 must flip from PASS to FAIL.

**Commands**

```bash
set -u
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout -B lane/5/it021-n2-mutation origin/integration
mkdir -p access/invariant-tests/mutations

cat > access/invariant-tests/mutations/IT-021-N2.mutation.sh << 'EOF'
#!/usr/bin/env bash
# Mutation: remove the Code-Owner-approval requirement from the fixture branch
# protection on the default branch so a flagged-unattended PR can merge without
# the full human gate sequence (Code Owner approval on the most recent push).
# Expected result: IT-021-N2 flips from PASS to FAIL.
# Spec: protocol/03-invariant-tests.md §6.5 (MUTATION-NEEDED IT-021-N2).
set -euo pipefail
REPO="${FIXTURE_REPO:?}"
# Disable require_code_owner_reviews on the default branch protection rule.
gh api --method PATCH \
  "repos/${REPO}/branches/main/protection/required_pull_request_reviews" \
  --field require_code_owner_reviews=false
echo "IT-021-N2 mutation applied: Code-Owner-approval requirement removed from PR gate in ${REPO}"
EOF
chmod +x access/invariant-tests/mutations/IT-021-N2.mutation.sh
git add access/invariant-tests/mutations/IT-021-N2.mutation.sh
git commit -m "L5-IT021-N2: create IT-021-N2.mutation.sh (remove CodeOwner approval from unattended PR)"
git push -u origin lane/5/it021-n2-mutation
gh pr create --base integration --head lane/5/it021-n2-mutation \
  --title "L5-IT021-N2: IT-021-N2 mutation script (remove CodeOwner approval requirement)" \
  --body "Creates IT-021-N2.mutation.sh per protocol/03-invariant-tests.md §6.5."
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
| --- | --- | --- | --- |
| 1 | Script exists and is executable | `test -x access/invariant-tests/mutations/IT-021-N2.mutation.sh && echo OK` | `OK` |

**SELF-VERIFY**

```bash
test -x access/invariant-tests/mutations/IT-021-N2.mutation.sh && \
echo "IT-021-N2.mutation.sh present and executable"
```

Expected output, exactly: `IT-021-N2.mutation.sh present and executable`

**STOP rule:** If applying the mutation does not cause IT-021-N2 to exit non-zero, the test is vacuous. File a blocker titled `VACUOUS-TEST IT-021-N2` and stop the lane immediately.
7. Nothing here is complete from a configuration file that says the right thing. AT-110 states the principle for the whole lane: the boundary of the most privileged identity must be executed rather than asserted.
