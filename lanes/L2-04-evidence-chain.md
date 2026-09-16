<!-- PARTIAL-SUPERSEDED (FD-B1-L2 + FD-044, 2026-09-02):
     The L2-P1-Txx namespace tasks and actor-gate implementation in this file are superseded by L2-05-tasks.md.
     The task bodies in this file for IDs that L2-05 §2.1 directs you here are STILL AUTHORITATIVE — execute from this file.
     Do NOT execute any L2-P1-Txx or actor-gate tasks from this file. -->

# L2-04 — LANE 2, PHASE 4: THE EVIDENCE CHAIN (SUBSYSTEM F)

**Lane:** L2 Pipeline & Evidence · **Subsystem:** F — Evidence chain store and query (spec §99.2 row F, L9193)
**Branch prefix:** `lane/2/*` · **Task-id range used here:** `L2-T500`–`L2-T516` (reserved for subsystem F by L2-00 charter §12)
**Owned paths touched by this document:** `tools/evidence/**` and `.github/workflows/**` only.

> **Read before executing anything in this file, in this order:**
> 1. `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` — in full.
> 2. `C:/D_Drive/PS/MultiProduct/Code/implementation/lanes/L2-00-charter.md` — sections 2, 6, 9, 10, 12.
> 3. Spec `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` §32, lines 2803–2828: `sed -n '2803,2828p'`.
> 4. Spec §97.2 lines 8843–8926 and §97.3 lines 8927–8953: the record stores and the event envelope.
>
> Nothing in this document requires interpretation. Where a value is not stated in the spec or in `contracts/**`, it is a DECISION REQUIRED for L0 (section 4 below) — never a judgment call for the executor.

Set once per shell session, before any task in this file:

**Commands**

```bash
set -euo pipefail
export CONTROL_PLANE_ROOT="<absolute path to the control-plane repo working copy>"
cd "$CONTROL_PLANE_ROOT"
git rev-parse --is-inside-work-tree || { echo "NOT A GIT REPO — STOP"; exit 1; }
export SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
```

---

## 1. WHAT THIS PHASE BUILDS, AND WHAT IT DOES NOT

Subsystem F is defined by exactly three deliverables in §99.2 row F (L9193):

| # | Spec text (L9193) | Built by tasks |
|---|---|---|
| F-a | "The eleven-question answerability for any production artifact" | `L2-T502`, `L2-T503`, `L2-T504`, `L2-T505` |
| F-b | "`/version` digest-match monitoring (100%; any mismatch is a P0 investigation)" | `L2-T506`, `L2-T507`, `L2-T511`, `L2-T512`, `L2-T513` |
| F-c | "append-only history with effective dating" | `L2-T515` |

Plus the named build-surface tool of §99.2 (L9215), which the spec assigns to subsystem F by name:

> `verify-digest-chain` — the digest-vs-approval audit script (scheduled sweep, and run on demand as the outage-recovery gate of Section 46.1) | Scheduled sweep comparing every production `/version` digest against its approval record; any mismatch is a P0 investigation | F

And the record-emission half that makes the chain closeable at all — §97.2 (L8843–8926): *"the deployment-record and event writes are **required, failing steps** of `deploy-production.yml` rather than trailing best-effort ones: a deploy whose record cannot be written is a deploy whose evidence chain does not close, and the eleven questions of Section 32 are unanswerable for it afterwards."* Built by `L2-T508`, `L2-T509`, `L2-T510`.

**Explicitly NOT built here.** Do not create any of these; each belongs to another lane and creating it fails lane-guard:

| Not built here | Owner | Why |
|---|---|---|
| The record *schemas* for `records/deployments/`, `records/uat/`, `events/` | L4 (`schemas/records/**`) | PARTITION.md line 20. L2 owns the write step; L4 owns the record shape (L2-00 charter §4.3) |
| Anything under `metrics/**` | L4 | PARTITION.md line 20 |
| The Grafana dashboard/panel JSON that presents digest-match | L5 (subsystem H is downstream of F; §99.2 dependency spine L9226) | L2 publishes; L2 does not present (L2-00 charter §3) |
| Prometheus scrape configuration for `/version` | L4 (subsystem I, §99.2 L9200) / L5 `infra/**` | PARTITION.md lines 20–21 |
| The incident *record* shape in `records/incidents/` | L4 | §97.2 L8843–8926 |
| Branch protection placement of any required check | L5 `access/**` | L2-00 charter §4.4 |
| `deploy-staging.yml` / `deploy-production.yml` bodies | L2 subsystem-E documents | Same lane, different document — `L2-T510` edits them at a named anchor only, and STOPs if the anchor is absent |

**Order dependency inside the lane.** §99.2's dependency spine (L9226) reads `E (workflows) → F (evidence chain) → H/I`. Subsystem E must already have produced `deploy-staging.yml`, `deploy-production.yml` and the digest invariant before `L2-T510` and `L2-T513` can be wired. Every task below that depends on an E artifact says so and carries a STOP rule for its absence.

---

## 2. THE ELEVEN QUESTIONS AND THE EXACT STORE EACH ANSWER READS FROM

This table is the authoritative mapping for this lane. It is transcribed from spec §32 (L2809–2821, the Source column) resolved against §97.2 (L8843–8926, the canonical record stores) and §97.3 (L8927–8953, the event log). It is turned into a machine-readable file by task `L2-T502`. **Do not add, remove or reorder a row.**

| # | Question (§32 L2811–2821) | §32 "Source" column, verbatim | Store this lane reads | Repository holding it | Owner of the store |
|---|---|---|---|---|---|
| 1 | Which git commit? | Artifact label and deployment record | `records/deployments/` — the record for this deployment; cross-checked against the OCI artifact label on the digest | `control-plane-records` | L4 |
| 2 | Which pull request? | Commit-to-PR association | GitHub REST — the platform's own records, not a record store (§32 L2827: "from the platform's own records, never from hand-maintained state") | GitHub | platform |
| 3 | Who approved it at Gate 2, and in which role? | PR review record cross-referenced with the assignment registry | GitHub REST PR reviews, joined to `registries/` assignments read through `contracts/**` | GitHub + `control-plane` | platform + L1 |
| 4 | Which CI run produced it? | Workflow run linked to the commit | GitHub Actions REST; the run URL is also carried on the deployment record | GitHub | platform |
| 5 | What is the artifact digest? | Registry digest, recorded at build | `records/deployments/` — the `digest` field (§97.2 example, L8896) | `control-plane-records` | L4 |
| 6 | When was it deployed to staging? | Staging deployment record | `records/deployments/` — the staging record for this digest | `control-plane-records` | L4 |
| 7 | Did staging verification pass? | Smoke result and UAT record in the workflow run | `records/deployments/` `smoke_result` + `staging_verified` (L8897, L8899) and the `records/uat/` record it references via `uat_record` (L8900) | `control-plane-records` | L4 |
| 8 | Who approved production? | Production-approval record in the records store (Section 97), verified by the workflow-identity gate (Section 27.2) | `records/deployments/` `approved_by` + `approval_event` (L8897–8898); the gate itself is §27.2 (L2567–2576) and is subsystem E's code | `control-plane-records` | L4 |
| 9 | When was it deployed to production? | Production deployment record | `records/deployments/` — the production record for this digest | `control-plane-records` | L4 |
| 10 | Did post-deployment smoke pass? | Smoke result attached to the deployment | `records/deployments/` `smoke_result` (L8901) on the production record | `control-plane-records` | L4 |
| 11 | What digest is running right now? | `GET /version` on the live service | A live observation, not a store: `GET /version` (§41.2, L3717–3730), recorded as an event in `events/` at observation time | live service, then `control-plane-records` | L2 observes, L4 stores |

**The invariant this table exists to prove** (§32 L2823, verbatim): *"item 5 and item 11 must match, and the digest deployed to production must be byte-identical to the one verified in staging."* Restated as invariant 22 (§101.5, L9484): *"The production artifact is the same digest verified in staging. Never rebuilt."*

**Two sanctioned substitutions, both mechanical, neither a judgment call:**

1. **Conformance profile (§15.7, L1587–1606; §32 L2825).** Questions 10 and 11 are "the evidence of the service conformance profile". A product whose `conformance_profile` is not `service` substitutes its declared equivalent evidence and *the chain closes on that evidence instead*. Implemented by `L2-T505` from the §15.7 table, transcribed literally.
2. **S18 platform-rebuild equivalence (§32 L2823; §96.6 S18, L8825; D78, L10161).** For an S18 product the recorded identity — pinned commit SHA plus lockfile plus recorded build configuration — *stands in for the digest throughout this chain*. Implemented by `L2-T505`. The digest invariant is **not waived**; the identity is substituted.

**Read-path rule, binding on every task in this document.** L2 never opens a file under `schemas/records/**`, never hard-codes a path under `records/**`, and never imports from another lane's tree (PARTITION.md rule 4). Every store path and every record field name is resolved at runtime from the contract file pinned by `L2-T501`. A script in `tools/evidence/` containing the literal string `schemas/records/` is wrong and must be re-done.

---

## 3. WHAT THIS PHASE CONSUMES FROM `contracts/**`

| Contract file (path as declared by L0) | Used by | If absent |
|---|---|---|
| `contracts/evidence/eleven-question-map.yaml` — the binding of each §32 question onto L4's record field names | `L2-T502`, `L2-T504` | STOP — DECISION REQUIRED **D-L2-07** below. Build against the lane fixture and file the blocker on the wiring task only |
| `contracts/records/` — store paths, records repository name, records-writer secret name (charter D-L2-03) | `L2-T508`, `L2-T509`, `L2-T511` | STOP — charter STOP RULE `S1`, cite §97.1 L8836–8842 |
| The `event_type` enum identifiers for the two events this phase writes | `L2-T509`, `L2-T512` | STOP — DECISION REQUIRED **D-L2-08** below |
| `conformance_profile` enumeration and the `classification.reliability_criticality` field name | `L2-T505` | STOP — charter STOP RULE `S1`, cite §15.7 L1587–1606 |
| The `/version` observation transport: runner label and scrape-credential secret name | `L2-T507`, `L2-T511` | STOP — DECISION REQUIRED **D-L2-09** below |
| Capability names `production-approval`, `incident-response`, `devops` | `L2-T513` | STOP — charter STOP RULE `S1`, cite §37.3 L3261–3268 |

---

## 4. DECISION REQUIRED — HANDED TO L0

<!-- DECISIONS SUPERSEDED (FD-044): Decision IDs D-L2-07/08/09 in this file are superseded by L2-05-tasks.md §1. Do not reference these IDs in new work. -->

Lane 2 must not resolve any of these. File each as a Contract Change Request using the charter's blocker template (L2-00 §10). Never edit `contracts/**` (PARTITION.md rule 2).

### DECISION REQUIRED D-L2-07 — The eleven-question field binding

**Question:** `contracts/` must publish, for each of §32's eleven questions, the *record field name* that answers it on L4's deployment and UAT record schemas.
**Why L2 cannot decide:** §97.2 (L8892–8903) labels its deployment record a *representative* schema. It names `id`, `product`, `digest`, `approved_by`, `approval_event`, `staging_verified`, `uat_record`, `smoke_result`, `rollback_of` — and does **not** name a field for the git commit (question 1), the pull request (question 2), the CI run (question 4), the environment discriminator (questions 6 and 9) or the deploy timestamps (questions 6 and 9). Those field names are L4's to define. Inventing them is a cross-lane import (PARTITION.md rule 4) and silently breaks on L4's first schema revision.
**What L0 must publish:** `contracts/evidence/eleven-question-map.yaml`, one entry per question number 1–11, each carrying `store`, `record_field` (or `source: github-api` with the API path), and `required: true|false`.
**Blocks:** live wiring of `L2-T504`. Does **not** block building it — `L2-T503` ships a lane-owned fixture map of identical shape so the engine is built and tested now.

### DECISION REQUIRED D-L2-08 — The two `event_type` identifiers this phase writes

**Question:** the exact enum identifiers for the events §97.3's taxonomy (L8952) calls "`/version` digest confirmed" and "drift detected by severity".
**Why L2 cannot decide:** §97.3 (L8948) is explicit — *"Every entry in the taxonomy below has exactly one stable `event_type` identifier — lower-case, underscore-separated, never renamed once shipped. The enum is declared in `platform.yaml`"* — and `registries/**` is L1's (PARTITION.md line 17). §97.3 also states control-plane CI rejects any event whose `event_type` is absent from the enum, so a guessed identifier makes every sweep run fail closed at write time.
**Blocks:** `L2-T509` event write, `L2-T512` escalation event.

### DECISION REQUIRED D-L2-09 — The `/version` observation transport

**Question:** from which runner, under which credential, does the scheduled sweep perform `GET /version`?
**Why L2 cannot decide:** §41.2 (L3728–3730) declares the estate's posture `private-authenticated` — *"the endpoints are reachable only over the private path from the operations VM, with a per-product scrape credential"*. A GitHub-hosted runner therefore cannot reach `/version`. The two candidate transports are (a) a self-hosted runner on the operations VM (`ops-vm/**` is L5's, PARTITION.md line 21) or (b) reading the observation from the Prometheus scrape of subsystem I (§99.2 L9200, L4's `metrics/**`). Both are foreign paths. Choosing between them is a design act.
**What L0 must publish:** the runner label and the scrape-credential secret name, or the read interface of the alternative observation source.
**Blocks:** live scheduling of `L2-T511`. Does **not** block `L2-T506` — the comparison core reads an observations file and is fully testable offline.

**No SIG identifier exists for digest mismatch.** The unified signal table (§52.2, L4520–4587) assigns none. Do not invent one. The escalation mechanism is the one the spec actually names: **artifact digest mismatch is Blocking-class drift** (§53.2 Level 4, L4697) — *"Fail CI or block the deployment path until resolved"* — with drift-class response "Immediate / Team Lead or escalation role / Yes — CI or deployment path blocked" (§53.4), and Blocking-class drift is on the closed push list of §92.11 (L8276).

---

## 5. TASK INDEX

**This file is authoritative for `L2-T500`–`L2-T516`.** Those seventeen ids were also carrying bodies in `L2-05-tasks.md` for different units of work (`L2-99-review.md` defect **B2**). The bodies in §6 below are the definitions of record; `L2-05-tasks.md` §2.1 now carries an index entry for each and has renumbered its own, different work to `L2-T530`–`L2-T546`. No id in this table is defined anywhere else in Lane 2.

| Task | Title | Size | Depends on |
|---|---|---|---|
| `L2-T500` | Phase-4 branch and the `tools/evidence` module skeleton | S | `L2-T001` |
| `L2-T501` | Pin the phase-4 consumed contract surface | S | `L2-T500` |
| `L2-T502` | Author `tools/evidence/eleven-questions.yaml` — the §32 question→store table as data | M | `L2-T500` |
| `L2-T503` | Author the fixture estate: one closed chain and four broken variants | M | `L2-T502` |
| `L2-T504` | Implement `tools/evidence/evidence-query` — the eleven-question assembler | L | `L2-T502`, `L2-T503` |
| `L2-T505` | Conformance-profile substitution (§15.7) and S18 equivalence (D78) | M | `L2-T504` |
| `L2-T506` | Implement `tools/evidence/verify-digest-chain` — the comparison core | L | `L2-T503` |
| `L2-T507` | Implement `tools/evidence/collect-version.sh` — the `/version` observation collector | M | `L2-T501` |
| `L2-T508` | Implement `tools/evidence/build-deployment-record.sh` — the record and event payload builder | M | `L2-T501` |
| `L2-T509` | Author `.github/workflows/emit-deployment-record.yml` — the required, failing emitter | M | `L2-T508` |
| `L2-T510` | Wire the emitter into `deploy-staging.yml` and `deploy-production.yml` at the named anchor | S | `L2-T509` |
| `L2-T511` | Author `.github/workflows/verify-digest-chain.yml` — the scheduled sweep | M | `L2-T506`, `L2-T507` |
| `L2-T512` | Implement the P0 escalation path: Blocking-drift finding, incident, push event | M | `L2-T511` |
| `L2-T513` | Implement `tools/evidence/deploy-gate.sh` — block-on-mismatch and the §46.1 recovery gate | M | `L2-T506` |
| `L2-T514` | Author `.github/workflows/evidence-selftest.yml` — the fixture suite as a required check | M | `L2-T504`, `L2-T506`, `L2-T513` |
| `L2-T515` | Append-only and effective-dating assertion (§63.1, §97.6) | S | `L2-T506` |
| `L2-T516` | Phase-4 roll-up, self-verify sweep and lane PR | S | all above |

---

## 6. TASKS

### L2-T500 — Phase-4 branch and the `tools/evidence` module skeleton

**Size:** S  **Depends on:** `L2-T001` (charter — owned-path skeleton exists)

**Creates:**
- `tools/evidence/lib/common.sh`
- `tools/evidence/README.md`

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/phase4-evidence-chain
test -d tools/evidence || { echo "tools/evidence ABSENT — L2-T001 NOT DONE — STOP"; exit 1; }
mkdir -p tools/evidence/lib tools/evidence/fixtures

cat > tools/evidence/lib/common.sh <<'EOF'
#!/usr/bin/env bash
# Lane 2 / subsystem F shared library.
# Spec: MultiProduct_MasterSpec_v4.0.md Section 32 (lines 2803-2828).
# RULE (PARTITION.md rule 4): nothing in tools/evidence/ may reference a path
# under schemas/**, registries/**, reconciler/**, metrics/** or access/**.
# Every foreign path is resolved from contracts/ at runtime.
set -euo pipefail

EV_FAIL_PREFIX="EVIDENCE-FAIL"
EV_OK_PREFIX="EVIDENCE-OK"

ev_die() {            # ev_die <EXACT_TOKEN> <human text>
  printf '%s %s: %s\n' "$EV_FAIL_PREFIX" "$1" "$2" >&2
  exit 1
}

ev_ok() {             # ev_ok <EXACT_TOKEN>
  printf '%s %s\n' "$EV_OK_PREFIX" "$1"
}

ev_require_file() {   # ev_require_file <path> <TOKEN>
  [ -f "$1" ] || ev_die "$2" "required file absent: $1"
}

ev_require_cmd() {    # ev_require_cmd <binary>
  command -v "$1" >/dev/null 2>&1 || ev_die "MISSING_TOOL" "$1 not on PATH"
}

# UTC with offset, per Section 97.1 (line 8838): "Every record and event
# timestamp is stored in UTC with its offset".
ev_now_utc() { date -u +%Y-%m-%dT%H:%M:%S+00:00; }
EOF
chmod +x tools/evidence/lib/common.sh

cat > tools/evidence/README.md <<'EOF'
# tools/evidence — subsystem F, the production evidence chain

Owner: Lane 2 (PARTITION.md line 18). Spec: Section 32 (lines 2803-2828),
Section 99.2 row F (line 9193), named tool `verify-digest-chain` (line 9215).

Contents:
  eleven-questions.yaml         the Section 32 question-to-store table, as data
  evidence-query                answers all eleven questions for one deployment
  verify-digest-chain           the digest-vs-approval sweep (Section 46.1 gate)
  collect-version.sh            GET /version observation collector
  build-deployment-record.sh    record + event payload builder for the deploy workflows
  deploy-gate.sh                fails closed while the chain is not confirmed closed
  lib/common.sh                 shared helpers
  fixtures/                     synthetic estates: one closed chain, four broken

Hard rule: no file in this tree contains the literal string `schemas/records/`,
`registries/`, `metrics/` or `reconciler/`. Foreign surfaces are reached only
through contracts/ (PARTITION.md rule 4).
EOF

git add tools/evidence/lib/common.sh tools/evidence/README.md
git commit -m "L2-T500: tools/evidence module skeleton for subsystem F"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | On the phase-4 branch | `git rev-parse --abbrev-ref HEAD` | exactly `lane/2/phase4-evidence-chain` |
| A2 | Library sources cleanly | `bash -n tools/evidence/lib/common.sh; echo $?` | exactly `0` |
| A3 | `ev_die` produces the exact failure prefix | `bash -c '. tools/evidence/lib/common.sh; ev_die TESTTOKEN hello' 2>&1; echo "rc=$?"` | line 1 exactly `EVIDENCE-FAIL TESTTOKEN: hello`, line 2 exactly `rc=1` |
| A4 | No foreign path referenced | `grep -rlE 'schemas/records/|registries/|metrics/|reconciler/' tools/evidence/ \| wc -l` | exactly `0` |
| A5 | Nothing outside owned trees changed | `git diff --name-only integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash -n tools/evidence/lib/common.sh \
 && test "$(bash -c '. tools/evidence/lib/common.sh; ev_die TESTTOKEN hello' 2>&1)" = "EVIDENCE-FAIL TESTTOKEN: hello" \
 && test "$(grep -rlE 'schemas/records/|registries/|metrics/|reconciler/' tools/evidence/ | wc -l | tr -d ' ')" = "0" \
 && test "$(git diff --name-only integration...HEAD | grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)')" = "0" \
 && echo "L2-T500 OK" || echo "L2-T500 FAIL"
```
Correct output: the single line `L2-T500 OK`.

**STOP rule:** if `tools/evidence/` does not exist, `L2-T001` has not run — STOP, do not create it here. File the blocker with STOP RULE `S1`, TASK `L2-T500`.

---

### L2-T501 — Pin the phase-4 consumed contract surface

**Size:** S  **Depends on:** `L2-T500`

**Creates:** `tools/evidence/PHASE4-CONTRACTS.lock`

This task records which contract files exist *right now*, so every later task fails with a named token rather than a guess when one is missing.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test -d contracts || { echo "contracts/ ABSENT — STOP"; exit 1; }
{
  echo "# Lane 2 phase 4 consumed contract surface — generated, do not hand-edit."
  echo "# Spec: Section 32 (2803-2828), Section 97.1-97.3 (8836-8953), Section 41.2 (3717-3730)."
  echo "lane: L2"
  echo "phase: 4"
  echo "contracts_commit: $(git log -1 --format=%H -- contracts)"
  echo "recorded_at_utc: $(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
  echo "required:"
  for f in \
    contracts/evidence/eleven-question-map.yaml \
    contracts/records/stores.yaml \
    contracts/records/write-interface.yaml \
    contracts/events/event-types.yaml \
    contracts/product/conformance-profiles.yaml \
    contracts/evidence/version-observation.yaml
  do
    if [ -f "$f" ]; then echo "  - path: $f"; echo "    present: true"; else echo "  - path: $f"; echo "    present: false"; fi
  done
} > tools/evidence/PHASE4-CONTRACTS.lock
git add tools/evidence/PHASE4-CONTRACTS.lock
git commit -m "L2-T501: pin phase-4 consumed contract surface"
grep -B1 'present: false' tools/evidence/PHASE4-CONTRACTS.lock || echo "ALL PHASE-4 CONTRACTS PRESENT"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Lock file exists | `test -f tools/evidence/PHASE4-CONTRACTS.lock; echo $?` | exactly `0` |
| A2 | Records a 40-char contracts SHA | `grep -cE '^contracts_commit: [0-9a-f]{40}$' tools/evidence/PHASE4-CONTRACTS.lock` | exactly `1` |
| A3 | Exactly six contract rows recorded | `grep -c '^  - path: ' tools/evidence/PHASE4-CONTRACTS.lock` | exactly `6` |
| A4 | Every row carries a presence verdict | `grep -cE '^    present: (true|false)$' tools/evidence/PHASE4-CONTRACTS.lock` | exactly `6` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(grep -c '^  - path: ' tools/evidence/PHASE4-CONTRACTS.lock)" = "6" \
 && test "$(grep -cE '^    present: (true|false)$' tools/evidence/PHASE4-CONTRACTS.lock)" = "6" \
 && grep -qE '^contracts_commit: [0-9a-f]{40}$' tools/evidence/PHASE4-CONTRACTS.lock \
 && echo "L2-T501 OK" || echo "L2-T501 FAIL"
```
Correct output: the single line `L2-T501 OK`.

**STOP rule:** a `present: false` row is **not** a reason to stop this task — recording absence is this task's job. It **is** the trigger for the STOP rule of whichever later task consumes that file. Never create a file under `contracts/**` to make a row read `true` (PARTITION.md rule 2). If `contracts/` itself is absent, STOP with charter STOP RULE `S1`.

---

### L2-T502 — Author `tools/evidence/eleven-questions.yaml`

**Size:** M  **Depends on:** `L2-T500`

**Creates:** `tools/evidence/eleven-questions.yaml`

This is section 2 of this document, transcribed to data. Write it with exactly this content. Do not add, remove, reorder or reword a row.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/eleven-questions.yaml <<'EOF'
# The Section 32 Production Evidence Chain, as data.
# Spec: MultiProduct_MasterSpec_v4.0.md Section 32, lines 2803-2828.
# Source column transcribed verbatim from the Section 32 table (lines 2811-2821).
# Store column resolved against Section 97.2 (lines 8843-8926).
# BINDING: Section 32 line 2827 - "the chain above is assembled from them and
# from the platform's own records, never from hand-maintained state."
# Field names are NOT declared here: they come from
# contracts/evidence/eleven-question-map.yaml (DECISION REQUIRED D-L2-07).
schema: eleven-questions/v1
spec_section: "32"
spec_lines: "2803-2828"
invariant:
  text: "item 5 and item 11 must match, and the digest deployed to production must be byte-identical to the one verified in staging"
  spec_line: "2823"
  restated_as_invariant: 22
  invariant_spec_line: "9484"
questions:
  - n: 1
    question: "Which git commit?"
    source: "Artifact label and deployment record"
    store: "records/deployments/"
    kind: record
  - n: 2
    question: "Which pull request?"
    source: "Commit-to-PR association"
    store: "github-api"
    kind: platform
  - n: 3
    question: "Who approved it at Gate 2, and in which role?"
    source: "PR review record cross-referenced with the assignment registry"
    store: "github-api+assignment-registry"
    kind: platform
  - n: 4
    question: "Which CI run produced it?"
    source: "Workflow run linked to the commit"
    store: "github-api"
    kind: platform
  - n: 5
    question: "What is the artifact digest?"
    source: "Registry digest, recorded at build"
    store: "records/deployments/"
    kind: record
  - n: 6
    question: "When was it deployed to staging?"
    source: "Staging deployment record"
    store: "records/deployments/"
    kind: record
  - n: 7
    question: "Did staging verification pass?"
    source: "Smoke result and UAT record in the workflow run"
    store: "records/deployments/+records/uat/"
    kind: record
  - n: 8
    question: "Who approved production?"
    source: "Production-approval record in the records store (Section 97), verified by the workflow-identity gate (Section 27.2)"
    store: "records/deployments/"
    kind: record
  - n: 9
    question: "When was it deployed to production?"
    source: "Production deployment record"
    store: "records/deployments/"
    kind: record
  - n: 10
    question: "Did post-deployment smoke pass?"
    source: "Smoke result attached to the deployment"
    store: "records/deployments/"
    kind: record
    profile_substituted: true
  - n: 11
    question: "What digest is running right now?"
    source: "GET /version on the live service"
    store: "live-observation+events/"
    kind: observation
    profile_substituted: true
EOF
git add tools/evidence/eleven-questions.yaml
git commit -m "L2-T502: publish the Section 32 question-to-store table as data"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Exactly eleven questions | `grep -c '^  - n: ' tools/evidence/eleven-questions.yaml` | exactly `11` |
| A2 | Numbered 1..11 in order, no gaps | `grep '^  - n: ' tools/evidence/eleven-questions.yaml \| sed 's/.*n: //' \| tr '\n' ' '` | exactly `1 2 3 4 5 6 7 8 9 10 11 ` |
| A3 | Every question carries a store | `grep -c '^    store: ' tools/evidence/eleven-questions.yaml` | exactly `11` |
| A4 | Exactly two questions are profile-substituted (§32 L2825) | `grep -c '^    profile_substituted: true$' tools/evidence/eleven-questions.yaml` | exactly `2` |
| A5 | Question text matches the spec byte for byte | see SELF-VERIFY below | `11` |
| A6 | No record field name is declared here | `grep -c 'record_field' tools/evidence/eleven-questions.yaml` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
# A5: every question string in the file must appear in the spec's Section 32 table.
HITS=0
while IFS= read -r q; do
  if sed -n '2809,2822p' "$SPEC" | grep -qF "$q"; then HITS=$((HITS+1)); fi
done < <(grep '^    question: ' tools/evidence/eleven-questions.yaml | sed 's/^    question: "//; s/"$//')
test "$HITS" = "11" \
 && test "$(grep -c '^  - n: ' tools/evidence/eleven-questions.yaml)" = "11" \
 && test "$(grep '^  - n: ' tools/evidence/eleven-questions.yaml | sed 's/.*n: //' | tr '\n' ' ')" = "1 2 3 4 5 6 7 8 9 10 11 " \
 && test "$(grep -c '^    profile_substituted: true$' tools/evidence/eleven-questions.yaml)" = "2" \
 && test "$(grep -c 'record_field' tools/evidence/eleven-questions.yaml)" = "0" \
 && echo "L2-T502 OK" || echo "L2-T502 FAIL"
```
Correct output: the single line `L2-T502 OK`. `HITS` printing anything other than 11 means a question string was reworded — restore it verbatim from `sed -n '2809,2822p' "$SPEC"`.

**STOP rule:** if any question string fails the A5 spec comparison and you cannot make it match by copying from `sed -n '2809,2822p' "$SPEC"`, STOP — do not paraphrase. File the blocker with STOP RULE `S4`, TASK `L2-T502`, citing spec lines 2809–2822.

---

### L2-T503 — Author the fixture estate: one closed chain and four broken variants

**Size:** M  **Depends on:** `L2-T502`

**Creates:**
- `tools/evidence/fixtures/map.fixture.yaml`
- `tools/evidence/fixtures/closed/` (4 files)
- `tools/evidence/fixtures/broken-digest-mismatch/` (2 files)
- `tools/evidence/fixtures/broken-missing-approval/` (1 file)
- `tools/evidence/fixtures/broken-self-approved/` (1 file)
- `tools/evidence/fixtures/broken-no-record/` (1 file)

The fixtures are the negative-test estate. §95.4's philosophy, applied here: a check that has never been shown to fail is not a check. Fixtures are synthetic; no real product, person or digest appears (invariant 111 / §38.3 fixture-provenance discipline, L3468).

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
mkdir -p tools/evidence/fixtures/closed \
         tools/evidence/fixtures/broken-digest-mismatch \
         tools/evidence/fixtures/broken-missing-approval \
         tools/evidence/fixtures/broken-self-approved \
         tools/evidence/fixtures/broken-no-record

cat > tools/evidence/fixtures/map.fixture.yaml <<'EOF'
# LANE-OWNED FIXTURE ONLY. Not a contract.
# Stands in for contracts/evidence/eleven-question-map.yaml (DECISION REQUIRED D-L2-07)
# so the query engine can be built and tested before L0 publishes the real map.
# Shape is identical; field names here are fixture names and bind to nothing real.
schema: eleven-question-map/v1
provenance: synthetic
map:
  1:  { store: "records/deployments/", record_field: "commit" }
  2:  { store: "github-api", api: "repos/{owner}/{repo}/commits/{sha}/pulls" }
  3:  { store: "github-api", api: "repos/{owner}/{repo}/pulls/{number}/reviews" }
  4:  { store: "github-api", api: "repos/{owner}/{repo}/actions/runs" }
  5:  { store: "records/deployments/", record_field: "digest" }
  6:  { store: "records/deployments/", record_field: "deployed_at", filter_field: "environment", filter_value: "staging" }
  7:  { store: "records/deployments/", record_field: "staging_verified", also: ["smoke_result", "uat_record"] }
  8:  { store: "records/deployments/", record_field: "approved_by", also: ["approval_event"] }
  9:  { store: "records/deployments/", record_field: "deployed_at", filter_field: "environment", filter_value: "production" }
  10: { store: "records/deployments/", record_field: "smoke_result", filter_field: "environment", filter_value: "production" }
  11: { store: "live-observation", record_field: "observed_digest" }
EOF

# --- the closed chain -------------------------------------------------------
cat > tools/evidence/fixtures/closed/staging.yaml <<'EOF'
record_schema_version: 1
id: DEP-2026-01-05-001
product: fixture-product
environment: staging
commit: 1111111111111111111111111111111111111111
digest: sha256:aaaa000000000000000000000000000000000000000000000000000000000001
deployed_at: 2026-01-05T09:00:00+00:00
staging_verified: true
smoke_result: pass
uat_record: records/uat/2026-01-05-fixture-product-001.yaml
approved_by: null
approval_event: null
rollback_of: null
EOF
cat > tools/evidence/fixtures/closed/production.yaml <<'EOF'
record_schema_version: 1
id: DEP-2026-01-05-002
product: fixture-product
environment: production
commit: 1111111111111111111111111111111111111111
digest: sha256:aaaa000000000000000000000000000000000000000000000000000000000001
deployed_at: 2026-01-05T14:30:00+00:00
staging_verified: true
smoke_result: pass
uat_record: records/uat/2026-01-05-fixture-product-001.yaml
approved_by: fixture-approver
approval_event: https://example.invalid/runs/1
deployed_by: fixture-deployer
rollback_of: null
EOF
cat > tools/evidence/fixtures/closed/observations.jsonl <<'EOF'
{"product":"fixture-product","observed_digest":"sha256:aaaa000000000000000000000000000000000000000000000000000000000001","observed_at":"2026-01-05T15:00:00+00:00","source":"fixture","conformance_profile":"service"}
EOF
cat > tools/evidence/fixtures/closed/platform.yaml <<'EOF'
product: fixture-product
conformance_profile: service
pull_request: 42
ci_run: https://example.invalid/actions/runs/9001
gate2_approver: fixture-reviewer
gate2_role: cross-reviewer
EOF

# --- broken variant 1: item 5 != item 11 (the Section 32 invariant, line 2823)
cp tools/evidence/fixtures/closed/production.yaml tools/evidence/fixtures/broken-digest-mismatch/production.yaml
cat > tools/evidence/fixtures/broken-digest-mismatch/observations.jsonl <<'EOF'
{"product":"fixture-product","observed_digest":"sha256:bbbb000000000000000000000000000000000000000000000000000000000009","observed_at":"2026-01-05T15:00:00+00:00","source":"fixture","conformance_profile":"service"}
EOF

# --- broken variant 2: question 8 unanswerable (no approval record)
sed 's/^approved_by: .*/approved_by: null/; s#^approval_event: .*#approval_event: null#' \
  tools/evidence/fixtures/closed/production.yaml \
  > tools/evidence/fixtures/broken-missing-approval/production.yaml

# --- broken variant 3: approver == deployer (Section 27.2, lines 2567-2576)
sed 's/^deployed_by: .*/deployed_by: fixture-approver/' \
  tools/evidence/fixtures/closed/production.yaml \
  > tools/evidence/fixtures/broken-self-approved/production.yaml

# --- broken variant 4: a live digest with no deployment record at all
cat > tools/evidence/fixtures/broken-no-record/observations.jsonl <<'EOF'
{"product":"fixture-product","observed_digest":"sha256:cccc000000000000000000000000000000000000000000000000000000000007","observed_at":"2026-01-05T15:00:00+00:00","source":"fixture","conformance_profile":"service"}
EOF

git add tools/evidence/fixtures
git commit -m "L2-T503: fixture estate - one closed chain, four broken variants"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Five fixture estates exist | `ls -d tools/evidence/fixtures/*/ \| wc -l` | exactly `5` |
| A2 | The closed estate has four files | `ls tools/evidence/fixtures/closed \| wc -l` | exactly `4` |
| A3 | Closed staging and production digests are identical | `test "$(grep '^digest:' tools/evidence/fixtures/closed/staging.yaml)" = "$(grep '^digest:' tools/evidence/fixtures/closed/production.yaml)"; echo $?` | exactly `0` |
| A4 | The mismatch estate genuinely mismatches | `grep -q "$(grep '^digest: ' tools/evidence/fixtures/broken-digest-mismatch/production.yaml \| cut -d' ' -f2)" tools/evidence/fixtures/broken-digest-mismatch/observations.jsonl; echo $?` | exactly `1` |
| A5 | Self-approved estate has approver == deployer | `test "$(grep '^approved_by: ' .../broken-self-approved/production.yaml \| cut -d' ' -f2)" = "$(grep '^deployed_by: ' .../broken-self-approved/production.yaml \| cut -d' ' -f2)"; echo $?` | exactly `0` |
| A6 | Every fixture is synthetic — no real digest, product or person | `grep -rniE 'sha256:[0-9a-f]{8}(?!0000)' tools/evidence/fixtures \| wc -l` (or manual read) | fixture digests are all `sha256:aaaa…`, `sha256:bbbb…`, `sha256:cccc…` |
| A7 | Timestamps carry the UTC offset (§97.1 L8838) | `grep -rhoE '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:]{8}\+00:00' tools/evidence/fixtures \| wc -l` | `9` or more; **zero** timestamps without `+00:00` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
B=tools/evidence/fixtures
test "$(ls -d $B/*/ | wc -l | tr -d ' ')" = "5" \
 && test "$(ls $B/closed | wc -l | tr -d ' ')" = "4" \
 && test "$(grep '^digest:' $B/closed/staging.yaml)" = "$(grep '^digest:' $B/closed/production.yaml)" \
 && ! grep -q "$(grep '^digest: ' $B/broken-digest-mismatch/production.yaml | cut -d' ' -f2)" $B/broken-digest-mismatch/observations.jsonl \
 && test "$(grep '^approved_by: ' $B/broken-self-approved/production.yaml | cut -d' ' -f2)" = "$(grep '^deployed_by: ' $B/broken-self-approved/production.yaml | cut -d' ' -f2)" \
 && test "$(grep -rhoE 'T[0-9:]{8}[^+]' $B | wc -l | tr -d ' ')" = "0" \
 && echo "L2-T503 OK" || echo "L2-T503 FAIL"
```
Correct output: the single line `L2-T503 OK`.

**STOP rule:** if any fixture would need a real product name, a real person identity or a real artifact digest to be useful, STOP. §38.3 (L3468) forbids real data in fixtures without a declared provenance, and this lane has no authority to declare one. File the blocker with STOP RULE `S4`, TASK `L2-T503`.

---

### L2-T504 — Implement `tools/evidence/evidence-query`

**Size:** L  **Depends on:** `L2-T502`, `L2-T503`

**Creates:** `tools/evidence/evidence-query`

This is the tool that makes §98.2's Phase 6 completion check (L9078) provable: *"the eleven-item evidence chain answerable for one real deployment"*. It answers all eleven questions for one product + digest, from the stores named in `eleven-questions.yaml`, using the field binding from the map file.

Runtime contract, fixed — do not vary it:

```
evidence-query --map <map.yaml> --records <dir> --observations <file.jsonl> \
               --platform <file.yaml> --product <name> --digest <sha256:...> \
               [--json]
exit 0  → all eleven answered; prints "EVIDENCE-OK CHAIN_CLOSED"
exit 1  → one or more unanswered; prints "EVIDENCE-FAIL CHAIN_OPEN: q=<n>,<n>"
exit 2  → input error; prints "EVIDENCE-FAIL <TOKEN>: <text>"
```

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/evidence-query <<'PYEOF'
#!/usr/bin/env python3
"""Answer the eleven questions of Section 32 (spec lines 2803-2828) for one
production artifact.

Stores are named by tools/evidence/eleven-questions.yaml; field names come from
the map file (contracts/evidence/eleven-question-map.yaml in production, the
lane fixture in test). This file NEVER hard-codes a records/** path or a record
field name - PARTITION.md rule 4.
"""
import argparse, json, os, sys

try:
    import yaml
except ImportError:
    print("EVIDENCE-FAIL MISSING_TOOL: python3 yaml module not installed", file=sys.stderr)
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
QUESTIONS = os.path.join(HERE, "eleven-questions.yaml")


def die(token, text):
    print("EVIDENCE-FAIL %s: %s" % (token, text), file=sys.stderr)
    sys.exit(2)


def load_yaml(path, token):
    if not os.path.isfile(path):
        die(token, "required file absent: %s" % path)
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_records(directory):
    recs = []
    if not os.path.isdir(directory):
        die("RECORDS_DIR_ABSENT", directory)
    for root, _dirs, files in os.walk(directory):
        for name in sorted(files):
            if name.endswith((".yaml", ".yml")):
                path = os.path.join(root, name)
                doc = load_yaml(path, "RECORD_UNREADABLE")
                if isinstance(doc, dict):
                    doc["__path"] = path
                    recs.append(doc)
    return recs


def pick(records, product, digest, env=None):
    out = []
    for r in records:
        if r.get("product") != product:
            continue
        if r.get("digest") != digest:
            continue
        if env is not None and r.get("environment") != env:
            continue
        out.append(r)
    return out


def answer(n, entry, ctx):
    store = entry.get("store", "")
    field = entry.get("record_field")
    env = entry.get("filter_value")
    if store.startswith("github-api") or store == "github-api":
        return ctx["platform"].get({2: "pull_request", 3: "gate2_approver", 4: "ci_run"}[n])
    if store == "live-observation":
        obs = ctx["observations"].get(ctx["product"])
        return None if obs is None else obs.get(field)
    rows = pick(ctx["records"], ctx["product"], ctx["digest"], env)
    if not rows:
        return None
    row = rows[-1]
    value = row.get(field)
    if value is None or value == "" or value == "null":
        return None
    return value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True)
    ap.add_argument("--records", required=True)
    ap.add_argument("--observations", required=True)
    ap.add_argument("--platform", required=True)
    ap.add_argument("--product", required=True)
    ap.add_argument("--digest", required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    questions = load_yaml(QUESTIONS, "QUESTIONS_ABSENT")
    if len(questions.get("questions", [])) != 11:
        die("QUESTIONS_NOT_ELEVEN", "eleven-questions.yaml must carry exactly 11 rows")

    mapping = load_yaml(a.map, "MAP_ABSENT").get("map", {})
    missing_map = [q["n"] for q in questions["questions"] if q["n"] not in mapping]
    if missing_map:
        die("MAP_INCOMPLETE", "no binding for questions %s" % missing_map)

    observations = {}
    if os.path.isfile(a.observations):
        with open(a.observations, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    o = json.loads(line)
                    observations[o["product"]] = o

    ctx = {
        "records": load_records(a.records),
        "observations": observations,
        "platform": load_yaml(a.platform, "PLATFORM_ABSENT") or {},
        "product": a.product,
        "digest": a.digest,
    }

    answers, unanswered = {}, []
    for q in questions["questions"]:
        n = q["n"]
        val = answer(n, mapping[n], ctx)
        answers[n] = {"question": q["question"], "store": q["store"], "answer": val}
        if val in (None, "", "null"):
            unanswered.append(n)

    # The Section 32 invariant, line 2823: item 5 and item 11 must match.
    inv_ok = (answers[5]["answer"] is not None
              and answers[5]["answer"] == answers[11]["answer"])
    answers["invariant_5_equals_11"] = inv_ok

    if a.json:
        print(json.dumps(answers, indent=2, sort_keys=True, default=str))

    if unanswered:
        print("EVIDENCE-FAIL CHAIN_OPEN: q=%s" % ",".join(str(x) for x in unanswered))
        return 1
    if not inv_ok:
        print("EVIDENCE-FAIL DIGEST_MISMATCH: q5=%s q11=%s"
              % (answers[5]["answer"], answers[11]["answer"]))
        return 1
    print("EVIDENCE-OK CHAIN_CLOSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF
chmod +x tools/evidence/evidence-query
git add tools/evidence/evidence-query
git commit -m "L2-T504: evidence-query - the Section 32 eleven-question assembler"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Compiles | `python3 -m py_compile tools/evidence/evidence-query; echo $?` | exactly `0` |
| A2 | Closed chain answers all eleven | see SELF-VERIFY line 1 | exactly `EVIDENCE-OK CHAIN_CLOSED`, exit `0` |
| A3 | Missing-approval estate names question 8 | see SELF-VERIFY line 2 | exactly `EVIDENCE-FAIL CHAIN_OPEN: q=8`, exit `1` |
| A4 | Digest-mismatch estate fails on the §32 L2823 invariant | see SELF-VERIFY line 3 | a line starting `EVIDENCE-FAIL DIGEST_MISMATCH:`, exit `1` |
| A5 | No-record estate fails, never returns a partial pass | see SELF-VERIFY line 4 | exit `1` |
| A6 | `--json` emits all eleven answers plus the invariant verdict | `… --json \| python3 -c 'import json,sys;d=json.load(sys.stdin);print(len([k for k in d if k.isdigit()]))'` | exactly `11` |
| A7 | No hard-coded store path or field name | `grep -cE 'records/(deployments|uat)/' tools/evidence/evidence-query` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
Q=tools/evidence/evidence-query; F=tools/evidence/fixtures; M=$F/map.fixture.yaml
D=sha256:aaaa000000000000000000000000000000000000000000000000000000000001
python3 -m py_compile "$Q" || { echo "L2-T504 FAIL compile"; exit 1; }
R1=$("$Q" --map $M --records $F/closed --observations $F/closed/observations.jsonl --platform $F/closed/platform.yaml --product fixture-product --digest $D); RC1=$?
R2=$("$Q" --map $M --records $F/broken-missing-approval --observations $F/closed/observations.jsonl --platform $F/closed/platform.yaml --product fixture-product --digest $D); RC2=$?
R3=$("$Q" --map $M --records $F/broken-digest-mismatch --observations $F/broken-digest-mismatch/observations.jsonl --platform $F/closed/platform.yaml --product fixture-product --digest $D); RC3=$?
"$Q" --map $M --records $F/closed --observations $F/broken-no-record/observations.jsonl --platform $F/closed/platform.yaml --product fixture-product --digest sha256:cccc000000000000000000000000000000000000000000000000000000000007 >/dev/null 2>&1; RC4=$?
test "$R1" = "EVIDENCE-OK CHAIN_CLOSED" && test "$RC1" = "0" \
 && test "$R2" = "EVIDENCE-FAIL CHAIN_OPEN: q=8" && test "$RC2" = "1" \
 && case "$R3" in "EVIDENCE-FAIL DIGEST_MISMATCH:"*) true;; *) false;; esac && test "$RC3" = "1" \
 && test "$RC4" = "1" \
 && test "$(grep -cE 'records/(deployments|uat)/' "$Q")" = "0" \
 && echo "L2-T504 OK" || echo "L2-T504 FAIL"
```
Correct output: the single line `L2-T504 OK`.

**STOP rule:** if `python3 -c "import yaml"` fails and you cannot install PyYAML with `python3 -m pip install --user pyyaml`, STOP — do not hand-roll a YAML parser and do not change the record format to JSON. File the blocker with STOP RULE `S4`, TASK `L2-T504`, quoting the exact `MISSING_TOOL` line. If `contracts/evidence/eleven-question-map.yaml` was recorded `present: false` by `L2-T501`, this task still completes against the fixture map — the blocker for the real map is filed by `L2-T514`, not here.

---

### L2-T505 — Conformance-profile substitution and S18 equivalence

**Size:** M  **Depends on:** `L2-T504`

**Creates:** `tools/evidence/profile-substitution.yaml`
**Edits:** `tools/evidence/evidence-query` (adds `--profile` handling)

§32 (L2825): *"Items 10 and 11 are the evidence of the service conformance profile. A product declaring a different profile (Section 15.7…) substitutes its equivalent evidence for them … and the chain closes on that evidence instead."* The substitution table below is transcribed from §15.7 (L1591–1600). Do not add a profile, do not reword an entry.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/profile-substitution.yaml <<'EOF'
# Equivalent evidence for Section 32 questions 10 and 11, per conformance profile.
# Spec: Section 15.7 table, lines 1591-1600; Section 32 line 2825.
# Section 15.7 line 1601: "the evidence chain (Section 32) ... validate against the
# declared profile: a client-app product is not failed for lacking a health endpoint,
# and a service product cannot escape availability evidence by mis-declaring its profile."
schema: profile-substitution/v1
profiles:
  service:
    substitutes: false
    q10: "post-deployment smoke result"
    q11: "GET /version digest"
  client-app:
    substitutes: true
    q10: "crash-free-session telemetry"
    q11: "store version adoption"
  library:
    substitutes: true
    q10: "consumer contract tests"
    q11: "published registry version"
  batch:
    substitutes: true
    q10: "job success record"
    q11: "data-freshness signal"
  customer-hosted:
    substitutes: true
    q10: "customer-attested deploy record"
    q11: "customer-attested deploy record"
  white-label:
    substitutes: false
    q10: "post-deployment smoke result, per deployment"
    q11: "GET /version digest, per deployment in the declared environment list"
  static-site:
    substitutes: true
    q10: "build reproducibility evidence"
    q11: "build reproducibility evidence"
# Section 32 line 2823 / Section 96.6 S18 (line 8825) / D78 (line 10161):
# for an S18 platform-rebuild deployment the recorded identity stands in for the
# digest THROUGHOUT the chain. The invariant is not waived; the identity is substituted.
s18_equivalence:
  applies_when_intake_finding: S18
  identity_components: [commit_sha, lockfile_hash, build_configuration]
  substitutes_for_question: 5
  and_for_question: 11
  waives_invariant: false
EOF
```

Then add profile handling to `evidence-query`. Apply exactly this edit — insert immediately **before** the line `    if a.json:`:

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python3 - <<'PYEOF'
import io, sys
p = "tools/evidence/evidence-query"
src = io.open(p, encoding="utf-8").read()
anchor = "    if a.json:"
if anchor not in src:
    print("EVIDENCE-FAIL ANCHOR_ABSENT: '    if a.json:' not found in evidence-query")
    sys.exit(1)
block = '''    # Section 32 line 2825 + Section 15.7 (lines 1591-1600): questions 10 and 11
    # are the evidence of the service conformance profile; a different profile
    # substitutes its equivalent evidence and the chain closes on that instead.
    subs = load_yaml(os.path.join(HERE, "profile-substitution.yaml"), "SUBSTITUTION_ABSENT")
    profile = ctx["platform"].get("conformance_profile", "service")
    if profile not in subs["profiles"]:
        die("UNKNOWN_PROFILE", profile)
    if subs["profiles"][profile]["substitutes"]:
        for n in (10, 11):
            answers[n]["substituted_for_profile"] = profile
            answers[n]["equivalent_evidence"] = subs["profiles"][profile]["q%d" % n]
        unanswered = [n for n in unanswered if n not in (10, 11)]
        inv_ok = True
        answers["invariant_5_equals_11"] = "substituted:%s" % profile

'''
io.open(p, "w", encoding="utf-8").write(src.replace(anchor, block + anchor, 1))
print("PATCH_APPLIED")
PYEOF
git add tools/evidence/profile-substitution.yaml tools/evidence/evidence-query
git commit -m "L2-T505: conformance-profile substitution for questions 10 and 11; S18 equivalence recorded"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Patch applied once | the patch command above | exactly `PATCH_APPLIED` |
| A2 | Still compiles | `python3 -m py_compile tools/evidence/evidence-query; echo $?` | exactly `0` |
| A3 | Exactly the seven §15.7 profiles, no more | `grep -cE '^  [a-z-]+:$' tools/evidence/profile-substitution.yaml` | exactly `7` |
| A4 | Every §15.7 profile name appears | see SELF-VERIFY | `7` |
| A5 | A `service` product is unchanged by this task | closed-chain run from `L2-T504` | still exactly `EVIDENCE-OK CHAIN_CLOSED` |
| A6 | A `client-app` product closes on substituted evidence | see SELF-VERIFY | exactly `EVIDENCE-OK CHAIN_CLOSED` |
| A7 | S18 does not waive the invariant | `grep -c '^  waives_invariant: false$' tools/evidence/profile-substitution.yaml` | exactly `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
Q=tools/evidence/evidence-query; F=tools/evidence/fixtures; M=$F/map.fixture.yaml
D=sha256:aaaa000000000000000000000000000000000000000000000000000000000001
HITS=0
for p in service client-app library batch customer-hosted white-label static-site; do
  grep -q "^  $p:$" tools/evidence/profile-substitution.yaml && HITS=$((HITS+1))
  sed -n '1591,1600p' "$SPEC" | grep -q "\`$p\`" && true
done
mkdir -p /tmp/ev505 && sed 's/^conformance_profile: .*/conformance_profile: client-app/' $F/closed/platform.yaml > /tmp/ev505/platform.yaml
R=$("$Q" --map $M --records $F/broken-digest-mismatch --observations $F/broken-digest-mismatch/observations.jsonl --platform /tmp/ev505/platform.yaml --product fixture-product --digest $D)
test "$HITS" = "7" \
 && python3 -m py_compile "$Q" \
 && test "$R" = "EVIDENCE-OK CHAIN_CLOSED" \
 && test "$("$Q" --map $M --records $F/closed --observations $F/closed/observations.jsonl --platform $F/closed/platform.yaml --product fixture-product --digest $D)" = "EVIDENCE-OK CHAIN_CLOSED" \
 && test "$(grep -c '^  waives_invariant: false$' tools/evidence/profile-substitution.yaml)" = "1" \
 && echo "L2-T505 OK" || echo "L2-T505 FAIL"
```
Correct output: the single line `L2-T505 OK`.

**STOP rule:** if the anchor `    if a.json:` is not found, the patch prints `EVIDENCE-FAIL ANCHOR_ABSENT` — STOP, do not edit `evidence-query` by hand and do not re-run `L2-T504`'s heredoc over a modified file. File the blocker with STOP RULE `S5`, TASK `L2-T505`. If a profile name in `contracts/product/conformance-profiles.yaml` is absent from the §15.7 table, STOP with STOP RULE `S4` — the profile set is L1's and the substitution is the spec's; neither is this lane's to extend.

---

### L2-T506 — Implement `tools/evidence/verify-digest-chain` — the comparison core

**Size:** L  **Depends on:** `L2-T503`

**Creates:** `tools/evidence/verify-digest-chain`

The named build-surface tool of §99.2 (L9215): *"Scheduled sweep comparing every production `/version` digest against its approval record; any mismatch is a P0 investigation."* Also the §46.1 recovery gate (L4126): *"Completion of step 3 — the digest-vs-approval verification, executed by the named build-surface script `verify-digest-chain` — **gates resumption of production deploys**."*

Runtime contract, fixed:

```
verify-digest-chain --records <dir> --observations <file.jsonl> [--product <name>] \
                    --findings-out <file.json>
exit 0 → every observed digest matches an approved production deployment record
         prints "EVIDENCE-OK SWEEP_CLEAN products=<N>"
exit 3 → at least one mismatch; prints one "EVIDENCE-FAIL DIGEST_MISMATCH: product=…" line
         per finding, then "EVIDENCE-FAIL SWEEP_BLOCKING findings=<N>"
exit 2 → input error
```

Exit code **3**, not 1, so a caller can tell a mismatch from a broken sweep. A broken sweep is not a clean sweep (§53.1 seeded-canary philosophy, L4674).

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/verify-digest-chain <<'PYEOF'
#!/usr/bin/env python3
"""verify-digest-chain - the digest-vs-approval audit script.

Spec: Section 99.2 named tools, line 9215. Section 46.1 line 4126 (the
outage-recovery gate). Section 32 line 2823 (item 5 must equal item 11).
Section 41.2 line 3728 ("any mismatch is a P0 investigation").
Section 53.2 Level 4, line 4697: "artifact digest mismatch" is Blocking-class
drift - "Fail CI or block the deployment path until resolved."
"""
import argparse, json, os, sys

try:
    import yaml
except ImportError:
    print("EVIDENCE-FAIL MISSING_TOOL: python3 yaml module not installed", file=sys.stderr)
    sys.exit(2)


def die(token, text):
    print("EVIDENCE-FAIL %s: %s" % (token, text), file=sys.stderr)
    sys.exit(2)


def load_records(directory):
    if not os.path.isdir(directory):
        die("RECORDS_DIR_ABSENT", directory)
    recs = []
    for root, _d, files in os.walk(directory):
        for name in sorted(files):
            if name.endswith((".yaml", ".yml")):
                with open(os.path.join(root, name), "r", encoding="utf-8") as fh:
                    doc = yaml.safe_load(fh)
                if isinstance(doc, dict):
                    recs.append(doc)
    return recs


def approved_production_digests(records, product):
    """Digests with a production deployment record carrying an approval.
    Section 97.2 line 8897: approved_by is "never the deploying actor once armed".
    """
    out = {}
    for r in records:
        if r.get("product") != product:
            continue
        if r.get("environment") != "production":
            continue
        approver = r.get("approved_by")
        deployer = r.get("deployed_by")
        digest = r.get("digest")
        if not digest:
            continue
        reason = None
        if approver in (None, "", "null"):
            reason = "NO_APPROVAL_RECORD"
        elif deployer is not None and approver == deployer:
            reason = "APPROVER_EQUALS_DEPLOYER"
        elif r.get("staging_verified") is not True:
            reason = "NOT_STAGING_VERIFIED"
        out[digest] = {"record_id": r.get("id"), "reject_reason": reason,
                       "approved_by": approver, "approval_event": r.get("approval_event")}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True)
    ap.add_argument("--observations", required=True)
    ap.add_argument("--product")
    ap.add_argument("--findings-out", required=True)
    a = ap.parse_args()

    if not os.path.isfile(a.observations):
        die("OBSERVATIONS_ABSENT", a.observations)
    observations = []
    with open(a.observations, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                observations.append(json.loads(line))
    if a.product:
        observations = [o for o in observations if o.get("product") == a.product]
    if not observations:
        die("NO_OBSERVATIONS", "sweep with zero observations is not a clean sweep")

    records = load_records(a.records)
    findings = []
    for obs in observations:
        product = obs.get("product")
        observed = obs.get("observed_digest")
        approved = approved_production_digests(records, product)
        if observed not in approved:
            findings.append({
                "product": product, "observed_digest": observed,
                "observed_at": obs.get("observed_at"), "source": obs.get("source"),
                "finding": "NO_APPROVED_RECORD_FOR_RUNNING_DIGEST",
                "drift_class": "Blocking", "reconciliation_level": 4,
                "spec": "Section 32 line 2823; Section 53.2 line 4697",
            })
        elif approved[observed]["reject_reason"]:
            findings.append({
                "product": product, "observed_digest": observed,
                "observed_at": obs.get("observed_at"), "source": obs.get("source"),
                "finding": approved[observed]["reject_reason"],
                "record_id": approved[observed]["record_id"],
                "drift_class": "Blocking", "reconciliation_level": 4,
                "spec": "Section 27.2 lines 2567-2576; Section 53.2 line 4697",
            })

    result = {
        "tool": "verify-digest-chain",
        "products_swept": sorted({o.get("product") for o in observations}),
        "observations_compared": len(observations),
        "findings": findings,
    }
    with open(a.findings_out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)

    if findings:
        for f in findings:
            print("EVIDENCE-FAIL DIGEST_MISMATCH: product=%s digest=%s finding=%s"
                  % (f["product"], f["observed_digest"], f["finding"]))
        print("EVIDENCE-FAIL SWEEP_BLOCKING findings=%d" % len(findings))
        return 3
    print("EVIDENCE-OK SWEEP_CLEAN products=%d" % len(result["products_swept"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF
chmod +x tools/evidence/verify-digest-chain
git add tools/evidence/verify-digest-chain
git commit -m "L2-T506: verify-digest-chain comparison core (Section 99.2 line 9215)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Compiles | `python3 -m py_compile tools/evidence/verify-digest-chain; echo $?` | exactly `0` |
| A2 | Clean estate → exit 0 | SELF-VERIFY line 1 | exactly `EVIDENCE-OK SWEEP_CLEAN products=1`, exit `0` |
| A3 | Mismatch estate → exit 3 with the named finding | SELF-VERIFY line 2 | last line exactly `EVIDENCE-FAIL SWEEP_BLOCKING findings=1`, exit `3` |
| A4 | Self-approved estate is rejected (§27.2) | SELF-VERIFY line 3 | a line containing `finding=APPROVER_EQUALS_DEPLOYER`, exit `3` |
| A5 | Missing-approval estate is rejected | SELF-VERIFY line 4 | a line containing `finding=NO_APPROVAL_RECORD` or `NO_APPROVED_RECORD_FOR_RUNNING_DIGEST`, exit `3` |
| A6 | Zero observations is an error, never a pass (§53.1 L4674) | run with an empty observations file | exactly `EVIDENCE-FAIL NO_OBSERVATIONS: …`, exit `2` |
| A7 | Every finding carries `drift_class: Blocking` and level 4 | `python3 -c "import json;d=json.load(open('/tmp/ev506/f2.json'));print(all(x['drift_class']=='Blocking' and x['reconciliation_level']==4 for x in d['findings']))"` | exactly `True` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
V=tools/evidence/verify-digest-chain; F=tools/evidence/fixtures; mkdir -p /tmp/ev506
R1=$("$V" --records $F/closed --observations $F/closed/observations.jsonl --findings-out /tmp/ev506/f1.json); RC1=$?
"$V" --records $F/broken-digest-mismatch --observations $F/broken-digest-mismatch/observations.jsonl --findings-out /tmp/ev506/f2.json > /tmp/ev506/o2.txt 2>&1; RC2=$?
R2=$(tail -1 /tmp/ev506/o2.txt)
"$V" --records $F/broken-self-approved --observations $F/closed/observations.jsonl --findings-out /tmp/ev506/f3.json > /tmp/ev506/o3.txt 2>&1; RC3=$?
"$V" --records $F/broken-missing-approval --observations $F/closed/observations.jsonl --findings-out /tmp/ev506/f4.json > /tmp/ev506/o4.txt 2>&1; RC4=$?
: > /tmp/ev506/empty.jsonl
"$V" --records $F/closed --observations /tmp/ev506/empty.jsonl --findings-out /tmp/ev506/f5.json > /tmp/ev506/o5.txt 2>&1; RC5=$?
test "$R1" = "EVIDENCE-OK SWEEP_CLEAN products=1" && test "$RC1" = "0" \
 && test "$RC2" = "3" \
 && grep -q 'finding=APPROVER_EQUALS_DEPLOYER' /tmp/ev506/o3.txt && test "$RC3" = "3" \
 && test "$RC4" = "3" \
 && grep -q 'EVIDENCE-FAIL NO_OBSERVATIONS' /tmp/ev506/o5.txt && test "$RC5" = "2" \
 && test "$(python3 -c "import json;d=json.load(open('/tmp/ev506/f2.json'));print(all(x['drift_class']=='Blocking' and x['reconciliation_level']==4 for x in d['findings']))")" = "True" \
 && echo "L2-T506 OK" || echo "L2-T506 FAIL"
```
Correct output: the single line `L2-T506 OK`.

**STOP rule:** if a fixture estate makes the sweep exit `0` where the acceptance table says `3`, STOP — do not relax the comparison to make the test pass. A sweep that reports clean when it is not is exactly the failure §53.1 (L4674) forbids. File the blocker with STOP RULE `S4`, TASK `L2-T506`, quoting the fixture and the exit code.

---

### L2-T507 — Implement `tools/evidence/collect-version.sh` — the `/version` observation collector

**Size:** M  **Depends on:** `L2-T501`

**Creates:**
- `tools/evidence/collect-version.sh`
- `tools/evidence/lib/emit-observation.py`
- `tools/evidence/lib/read-targets.py`
- `tools/evidence/fixtures/targets.fixture.yaml`
- `tools/evidence/fixtures/targets-no-field.fixture.yaml`
- `tools/evidence/fixtures/stub-fetch.sh`

Question 11 of §32 is the only answer in the chain that is **not** a record read: *"What digest is running right now? — `GET /version` on the live service"* (§32 L2821). §41.2 (L3729) fixes what that answer means: *"`/version` closes the production evidence chain (Section 32, Production Evidence Chain): the digest it reports must equal the approved digest, and any mismatch is a P0 investigation."*

This collector turns live observations into the JSONL file that `verify-digest-chain` (`L2-T506`) already consumes. It is deliberately transport-agnostic: the **transport** — which runner, under which credential — is DECISION REQUIRED **D-L2-09** and is supplied by `L2-T511`'s workflow, not by this script. The script is therefore fully testable offline today.

**Two rules this script exists to enforce, both from §53.1 (L4680):**

1. A target that could not be reached still produces a line, carrying `observed_digest: null` and a non-null `collect_error`. Dropping the line would shrink the comparison set silently, and a silently narrowed comparison set is itself drift.
2. `--strict` makes an incomplete collection exit `4` — distinct from `L2-T506`'s exit `3` (mismatch) and exit `2` (input error), so a caller can never read "we could not look" as "we looked and it matched".

**The JSON key carrying the digest inside a `/version` body is not a spec value.** §41.2 (L3722) declares the endpoint and what it *provides* — "Deployed artifact digest and build metadata" — and never names a body key. The script therefore refuses to guess: every target declares its own `digest_field`, and a target without one is an input error, not a default.

Runtime contract, fixed — do not vary it:

```
collect-version.sh --targets <file.yaml> --out <file.jsonl> [--product <name>] [--strict]
exit 0 → every target in scope produced a line; every line carries a digest
exit 4 → --strict, and at least one target produced a line with collect_error
exit 2 → input error; prints "EVIDENCE-FAIL <TOKEN>: <text>"
```

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/lib/emit-observation.py <<'EOF'
#!/usr/bin/env python3
"""Emit one JSONL observation line. Called once per target by collect-version.sh.

Argv: product digest_field conformance_profile observed_at collect_error url
Stdin: the raw /version body (empty when the fetch failed).

Spec: Section 41.2 (lines 3717-3730) names the endpoint and what it provides,
and never names a body key - so the key is read from the target declaration,
never assumed. Section 53.1 (line 4680): an unreachable target still emits a
line, because a silently narrowed comparison set is itself drift.
"""
import json, sys

product, field, profile, observed_at, err, url = sys.argv[1:7]
body = sys.stdin.read()
digest = None
if not err:
    try:
        doc = json.loads(body)
        digest = doc.get(field)
    except Exception:
        err = "unparseable /version body"
    if digest in (None, ""):
        digest = None
        if not err:
            err = "digest field %r absent from /version body" % field
print(json.dumps({
    "product": product,
    "observed_digest": digest,
    "observed_at": observed_at,
    "source": url,
    "conformance_profile": profile,
    "collect_error": err or None,
}, sort_keys=True))
EOF

cat > tools/evidence/lib/read-targets.py <<'EOF'
#!/usr/bin/env python3
"""Flatten a version-targets file to TAB-separated rows for collect-version.sh.

Argv: targets.yaml [product-filter]
Emits: product<TAB>url<TAB>digest_field<TAB>conformance_profile

A target that declares no digest_field is an input error, never a default:
Section 41.2 (line 3722) declares the endpoint, not the shape of its body.
"""
import sys, yaml

doc = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
only = sys.argv[2] if len(sys.argv) > 2 else ""
targets = doc.get("targets") or []
if not targets:
    print("EVIDENCE-FAIL NO_TARGETS: target list is empty", file=sys.stderr)
    sys.exit(2)
rows = []
for t in targets:
    product = str(t.get("product", "")).strip()
    url = str(t.get("url", "")).strip()
    field = str(t.get("digest_field", "")).strip()
    profile = str(t.get("conformance_profile", "service")).strip()
    if not product or not url:
        print("EVIDENCE-FAIL TARGET_INCOMPLETE: %s" % (product or url or "<empty>"),
              file=sys.stderr)
        sys.exit(2)
    if not field:
        print("EVIDENCE-FAIL DIGEST_FIELD_UNDECLARED: %s" % product, file=sys.stderr)
        sys.exit(2)
    if only and product != only:
        continue
    rows.append("\t".join([product, url, field, profile]))
if not rows:
    print("EVIDENCE-FAIL NO_TARGETS: no target matched the product filter",
          file=sys.stderr)
    sys.exit(2)
print("\n".join(rows))
EOF

cat > tools/evidence/collect-version.sh <<'EOF'
#!/usr/bin/env bash
# collect-version.sh - the GET /version observation collector.
#
# Spec: Section 32 question 11 (line 2821); Section 41.2 (lines 3717-3730) -
# "the digest it reports must equal the approved digest, and any mismatch is a
# P0 investigation". Section 53.1 (line 4680) - a run whose comparison set
# silently narrowed is itself drift, so an unreachable target still emits a line.
#
# TRANSPORT IS NOT DECIDED HERE. The runner and the scrape credential are
# DECISION REQUIRED D-L2-09; the caller supplies them. This script reads a
# bearer token, if any, from EV_VERSION_TOKEN and names no secret at all.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/lib/common.sh"

TARGETS=""; OUT=""; ONLY=""; STRICT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --targets)  TARGETS="${2:-}"; shift 2 ;;
    --out)      OUT="${2:-}";     shift 2 ;;
    --product)  ONLY="${2:-}";    shift 2 ;;
    --strict)   STRICT=1;         shift ;;
    *) ev_die "BAD_ARG" "unknown argument: $1" ;;
  esac
done
[ -n "$TARGETS" ] || ev_die "BAD_ARG" "--targets is required"
[ -n "$OUT" ]     || ev_die "BAD_ARG" "--out is required"
ev_require_file "$TARGETS" "TARGETS_ABSENT"
ev_require_cmd python3

# EV_FETCH lets the fixture suite substitute a deterministic stand-in for the
# network. Unset, the real transport is curl.
ev_fetch() {   # ev_fetch <url>  -> body on stdout, non-zero on transport failure
  if [ -n "${EV_FETCH:-}" ]; then "$EV_FETCH" "$1"; return $?; fi
  ev_require_cmd curl
  local -a auth=()
  if [ -n "${EV_VERSION_TOKEN:-}" ]; then
    auth=(--header "Authorization: Bearer ${EV_VERSION_TOKEN}")
  fi
  curl --fail --silent --show-error --max-time 10 ${auth[@]+"${auth[@]}"} "$1"
}

ROWS="$(python3 "$HERE/lib/read-targets.py" "$TARGETS" "$ONLY")" || exit 2

: > "$OUT"
INCOMPLETE=0
ERRFILE="$(mktemp)"
trap 'rm -f "$ERRFILE"' EXIT
while IFS=$'\t' read -r PRODUCT URL FIELD PROFILE; do
  [ -n "$PRODUCT" ] || continue
  BODY=""
  ERR=""
  : > "$ERRFILE"
  if ! BODY="$(ev_fetch "$URL" 2>"$ERRFILE")"; then
    ERR="$(head -c 200 "$ERRFILE" | tr '\n' ' ')"
    [ -n "$ERR" ] || ERR="transport failure"
    BODY=""
  fi
  printf '%s' "$BODY" | python3 "$HERE/lib/emit-observation.py" \
      "$PRODUCT" "$FIELD" "$PROFILE" "$(ev_now_utc)" "$ERR" "$URL" >> "$OUT"
  if [ -n "$ERR" ]; then INCOMPLETE=$((INCOMPLETE+1)); fi
done <<< "$ROWS"

if [ "$INCOMPLETE" -gt 0 ]; then
  printf '%s OBSERVATION_INCOMPLETE: %d target(s) unobserved\n' \
    "$EV_FAIL_PREFIX" "$INCOMPLETE" >&2
  if [ "$STRICT" = "1" ]; then exit 4; fi
fi
ev_ok "OBSERVATIONS_COLLECTED count=$(wc -l < "$OUT" | tr -d ' ')"
EOF
chmod +x tools/evidence/collect-version.sh

cat > tools/evidence/fixtures/stub-fetch.sh <<'EOF'
#!/usr/bin/env bash
# Deterministic stand-in for the /version network fetch. Selected by EV_FETCH.
# Synthetic only: every host is under .invalid (RFC 2606), every digest is a
# fixture digest. Section 38.3 line 3468 - fixtures carry no real data.
set -euo pipefail
case "${1:-}" in
  https://ok.invalid/version)
    printf '{"digest":"sha256:aaaa000000000000000000000000000000000000000000000000000000000001","build":"fixture"}' ;;
  https://drift.invalid/version)
    printf '{"digest":"sha256:bbbb000000000000000000000000000000000000000000000000000000000009","build":"fixture"}' ;;
  https://down.invalid/version)
    echo "stub: connection refused" >&2; exit 7 ;;
  *)
    echo "stub: unknown target ${1:-}" >&2; exit 6 ;;
esac
EOF
chmod +x tools/evidence/fixtures/stub-fetch.sh

cat > tools/evidence/fixtures/targets.fixture.yaml <<'EOF'
# LANE-OWNED FIXTURE ONLY. Not a contract, not a live target list.
# The live target list is generated by provisioning (Lane 3) from the product
# registries (Lane 1); Lane 2 never hand-maintains one - Section 32 line 2827.
schema: version-targets/v1
provenance: synthetic
targets:
  - product: fixture-product
    url: https://ok.invalid/version
    digest_field: digest
    conformance_profile: service
  - product: fixture-drift
    url: https://drift.invalid/version
    digest_field: digest
    conformance_profile: service
  - product: fixture-down
    url: https://down.invalid/version
    digest_field: digest
    conformance_profile: service
EOF

cat > tools/evidence/fixtures/targets-no-field.fixture.yaml <<'EOF'
# LANE-OWNED FIXTURE ONLY. Negative case: a target declaring no digest_field.
schema: version-targets/v1
provenance: synthetic
targets:
  - product: fixture-product
    url: https://ok.invalid/version
    conformance_profile: service
EOF

bash -n tools/evidence/collect-version.sh || { echo "SYNTAX FAILED — STOP"; exit 1; }
python3 -m py_compile tools/evidence/lib/emit-observation.py tools/evidence/lib/read-targets.py
git add tools/evidence/collect-version.sh \
        tools/evidence/lib/emit-observation.py tools/evidence/lib/read-targets.py \
        tools/evidence/fixtures/stub-fetch.sh \
        tools/evidence/fixtures/targets.fixture.yaml \
        tools/evidence/fixtures/targets-no-field.fixture.yaml
git commit -m "L2-T507: collect-version.sh - the GET /version observation collector"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Script parses | `bash -n tools/evidence/collect-version.sh; echo $?` | exactly `0` |
| A2 | Three targets produce three lines | see SELF-VERIFY | exactly `3` |
| A3 | The reachable target carries its digest | `grep -c 'sha256:aaaa000000000000000000000000000000000000000000000000000000000001' /tmp/ev507/obs.jsonl` | exactly `1` |
| A4 | The unreachable target still produces a line, with `observed_digest` null | `python3 -c "import json;print([l for l in map(json.loads,open('/tmp/ev507/obs.jsonl')) if l['product']=='fixture-down'][0]['observed_digest'])"` | exactly `None` |
| A5 | The unreachable target carries a non-null `collect_error` | `python3 -c "import json;print(bool([l for l in map(json.loads,open('/tmp/ev507/obs.jsonl')) if l['product']=='fixture-down'][0]['collect_error']))"` | exactly `True` |
| A6 | `--strict` exits `4` on an incomplete collection, and still writes every line | see SELF-VERIFY | exit `4`, file still holds `3` lines |
| A7 | A target with no `digest_field` is an input error, never a default | see SELF-VERIFY | exit `2`, stderr contains `DIGEST_FIELD_UNDECLARED` |
| A8 | Every `observed_at` carries the UTC offset (§97.1 L8838) | `grep -c '+00:00' /tmp/ev507/obs.jsonl` | exactly `3` |
| A9 | The script names no secret and no runner | `grep -cE 'secrets\.|runs-on|RECORDS_WRITER|ghcr\.io' tools/evidence/collect-version.sh` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
C=tools/evidence/collect-version.sh; F=tools/evidence/fixtures; mkdir -p /tmp/ev507
bash -n "$C" || { echo "L2-T507 FAIL syntax"; exit 1; }
EV_FETCH=$F/stub-fetch.sh "$C" --targets $F/targets.fixture.yaml --out /tmp/ev507/obs.jsonl >/dev/null 2>&1; RC1=$?
EV_FETCH=$F/stub-fetch.sh "$C" --targets $F/targets.fixture.yaml --out /tmp/ev507/obs2.jsonl --strict >/dev/null 2>&1; RC2=$?
EV_FETCH=$F/stub-fetch.sh "$C" --targets $F/targets-no-field.fixture.yaml --out /tmp/ev507/obs3.jsonl >/tmp/ev507/e3.txt 2>&1; RC3=$?
test "$RC1" = "0" \
 && test "$(wc -l < /tmp/ev507/obs.jsonl | tr -d ' ')" = "3" \
 && test "$RC2" = "4" && test "$(wc -l < /tmp/ev507/obs2.jsonl | tr -d ' ')" = "3" \
 && test "$RC3" = "2" && grep -q 'DIGEST_FIELD_UNDECLARED' /tmp/ev507/e3.txt \
 && test "$(grep -c 'sha256:aaaa000000000000000000000000000000000000000000000000000000000001' /tmp/ev507/obs.jsonl)" = "1" \
 && test "$(python3 -c "import json;print([l for l in map(json.loads,open('/tmp/ev507/obs.jsonl')) if l['product']=='fixture-down'][0]['observed_digest'])")" = "None" \
 && test "$(grep -c '+00:00' /tmp/ev507/obs.jsonl)" = "3" \
 && test "$(grep -cE 'secrets\.|runs-on|RECORDS_WRITER|ghcr\.io' "$C")" = "0" \
 && echo "L2-T507 OK" || echo "L2-T507 FAIL"
```
Correct output: the single line `L2-T507 OK`.

**STOP rule:** if making A6 pass appears to require dropping the unobserved target's line, STOP — that is the exact failure §53.1 (L4680) names, and it converts an outage into a clean sweep. If completing this task appears to require naming a runner label or a scrape secret, STOP under STOP RULE `S1` and cite DECISION REQUIRED **D-L2-09**: the transport is supplied by `L2-T511`, never by this script.

---

### L2-T508 — Implement `tools/evidence/build-deployment-record.sh`

**Size:** M  **Depends on:** `L2-T501`

**Creates:**
- `tools/evidence/build-deployment-record.sh`
- `tools/evidence/fixtures/write-interface.fixture.yaml`
- `tools/evidence/fixtures/event-types.fixture.yaml`

§97.2 (L8926) makes this half of the chain mandatory, not decorative: *"the deployment-record and event writes are **required, failing steps** of `deploy-production.yml` rather than trailing best-effort ones: a deploy whose record cannot be written is a deploy whose evidence chain does not close, and the eleven questions of Section 32 are unanswerable for it afterwards."*

This script builds the two payloads. It does **not** write them — the write path is L4's records-writer (§97.1, L8841), reached in `L2-T509` through the entrypoint named in `contracts/records/write-interface.yaml`.

**Three things this script refuses to invent, and where each comes from:**

| Refused | Comes from | Token on absence |
|---|---|---|
| Record and event **id** values (§97.2 example `DEP-2026-09-12-014`, L8896; §97.3 example `EVT-2026-09-14-000317`, L8933) | passed in with `--record-id` / `--event-id`; minted by the allocator named in `contracts/records/write-interface.yaml` | `ID_MALFORMED` |
| The **field names** on the deployment record beyond the nine §97.2 prints | `contracts/evidence/eleven-question-map.yaml` (D-L2-07); the fixture map in test | `MAP_ABSENT` |
| The two **`event_type`** identifiers | `contracts/events/event-types.yaml` (D-L2-08), under keys `version_digest_confirmed` and `drift_detected` | `EVENT_TYPE_UNRESOLVED` |

The writer writes exactly the field names the reader of `L2-T504` reads, because both take the same map. That is what makes the chain closeable rather than merely populated.

Runtime contract, fixed:

```
build-deployment-record.sh --map <map.yaml> --event-types <types.yaml> \
    --record-id <DEP-...> --event-id <EVT-...> \
    --product <name> --environment <staging|production> --digest <value> \
    --commit <sha> --run-url <url> --actor <id> --approved-by <id|none> \
    --staging-verified <true|false> --smoke-result <pass|fail|none> \
    --uat-record <path|none> --out-dir <dir>
exit 0 → writes <out-dir>/record.yaml and <out-dir>/event.yaml
exit 2 → input error; prints "EVIDENCE-FAIL <TOKEN>: <text>"
```

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/build-deployment-record.sh <<'EOF'
#!/usr/bin/env bash
# build-deployment-record.sh - deployment record and event payload builder.
#
# Spec: Section 97.2 (lines 8843-8926) - the record store and its representative
# schema; line 8926 - "the deployment-record and event writes are required,
# failing steps". Section 97.3 (lines 8927-8953) - the binding event envelope.
# Section 97.1 line 8838 - every timestamp in UTC with its offset.
#
# This script BUILDS payloads. It never writes to a records store, never names a
# secret and never constructs a path under records/ or events/ - those are Lane
# 4's (PARTITION.md line 20) and are reached only through the write interface
# named in contracts/records/write-interface.yaml.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/lib/common.sh"
ev_require_cmd python3

MAP=""; TYPES=""; RECORD_ID=""; EVENT_ID=""; PRODUCT=""; ENVIRONMENT=""
DIGEST=""; COMMIT=""; RUN_URL=""; ACTOR=""; APPROVED_BY=""
STAGING_VERIFIED=""; SMOKE_RESULT=""; UAT_RECORD=""; OUT_DIR=""
while [ $# -gt 0 ]; do
  case "$1" in
    --map)              MAP="${2:-}";              shift 2 ;;
    --event-types)      TYPES="${2:-}";            shift 2 ;;
    --record-id)        RECORD_ID="${2:-}";        shift 2 ;;
    --event-id)         EVENT_ID="${2:-}";         shift 2 ;;
    --product)          PRODUCT="${2:-}";          shift 2 ;;
    --environment)      ENVIRONMENT="${2:-}";      shift 2 ;;
    --digest)           DIGEST="${2:-}";           shift 2 ;;
    --commit)           COMMIT="${2:-}";           shift 2 ;;
    --run-url)          RUN_URL="${2:-}";          shift 2 ;;
    --actor)            ACTOR="${2:-}";            shift 2 ;;
    --approved-by)      APPROVED_BY="${2:-}";      shift 2 ;;
    --staging-verified) STAGING_VERIFIED="${2:-}"; shift 2 ;;
    --smoke-result)     SMOKE_RESULT="${2:-}";     shift 2 ;;
    --uat-record)       UAT_RECORD="${2:-}";       shift 2 ;;
    --out-dir)          OUT_DIR="${2:-}";          shift 2 ;;
    *) ev_die "BAD_ARG" "unknown argument: $1" ;;
  esac
done
for pair in MAP:--map TYPES:--event-types RECORD_ID:--record-id EVENT_ID:--event-id \
            PRODUCT:--product ENVIRONMENT:--environment DIGEST:--digest COMMIT:--commit \
            RUN_URL:--run-url ACTOR:--actor OUT_DIR:--out-dir; do
  var="${pair%%:*}"; flag="${pair##*:}"
  [ -n "${!var}" ] || ev_die "BAD_ARG" "$flag is required"
done
ev_require_file "$MAP" "MAP_ABSENT"
ev_require_file "$TYPES" "EVENT_TYPES_ABSENT"

case "$ENVIRONMENT" in
  staging|production) ;;
  *) ev_die "ENVIRONMENT_UNRECOGNISED" "$ENVIRONMENT" ;;
esac

# Section 97.2 line 8896 prints DEP-2026-09-12-014; Section 97.3 line 8933
# prints EVT-2026-09-14-000317. The FORMAT is transcribed; the VALUE is minted
# by the allocator named in contracts/records/write-interface.yaml, never here.
printf '%s' "$RECORD_ID" | grep -qE '^DEP-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}$' \
  || ev_die "ID_MALFORMED" "record id must match DEP-YYYY-MM-DD-NNN: $RECORD_ID"
printf '%s' "$EVENT_ID" | grep -qE '^EVT-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}$' \
  || ev_die "ID_MALFORMED" "event id must match EVT-YYYY-MM-DD-NNNNNN: $EVENT_ID"

mkdir -p "$OUT_DIR"
NOW="$(ev_now_utc)"

python3 "$HERE/lib/build-payloads.py" \
  --map "$MAP" --event-types "$TYPES" \
  --record-id "$RECORD_ID" --event-id "$EVENT_ID" \
  --product "$PRODUCT" --environment "$ENVIRONMENT" --digest "$DIGEST" \
  --commit "$COMMIT" --run-url "$RUN_URL" --actor "$ACTOR" \
  --approved-by "${APPROVED_BY:-none}" \
  --staging-verified "${STAGING_VERIFIED:-false}" \
  --smoke-result "${SMOKE_RESULT:-none}" \
  --uat-record "${UAT_RECORD:-none}" \
  --now "$NOW" --out-dir "$OUT_DIR"

ev_ok "PAYLOADS_BUILT record=$OUT_DIR/record.yaml event=$OUT_DIR/event.yaml"
EOF
chmod +x tools/evidence/build-deployment-record.sh

cat > tools/evidence/lib/build-payloads.py <<'EOF'
#!/usr/bin/env python3
"""Build the deployment-record and event payloads for one deploy.

Spec: Section 97.2 lines 8892-8903 (the representative deployment record);
Section 97.3 lines 8931-8944 (the binding event envelope).

The record's field NAMES come from the eleven-question map, so the writer of
this phase writes exactly the names the reader of L2-T504 reads. Nothing here
hard-codes a path under records/ or events/ - PARTITION.md rule 4.
"""
import argparse, os, sys

try:
    import yaml
except ImportError:
    print("EVIDENCE-FAIL MISSING_TOOL: python3 yaml module not installed", file=sys.stderr)
    sys.exit(2)


def die(token, text):
    print("EVIDENCE-FAIL %s: %s" % (token, text), file=sys.stderr)
    sys.exit(2)


def field_for(mapping, n, token):
    entry = mapping.get(n) or mapping.get(str(n))
    if not entry or not entry.get("record_field"):
        die(token, "map declares no record_field for question %s" % n)
    return entry["record_field"]


def main():
    ap = argparse.ArgumentParser()
    for flag in ("--map", "--event-types", "--record-id", "--event-id", "--product",
                 "--environment", "--digest", "--commit", "--run-url", "--actor",
                 "--approved-by", "--staging-verified", "--smoke-result",
                 "--uat-record", "--now", "--out-dir"):
        ap.add_argument(flag, required=True)
    a = ap.parse_args()

    mapping = (yaml.safe_load(open(a.map, encoding="utf-8")) or {}).get("map") or {}
    if not mapping:
        die("MAP_ABSENT", "no map: block in %s" % a.map)

    types_doc = yaml.safe_load(open(a.event_types, encoding="utf-8")) or {}
    types = types_doc.get("map") or {}
    event_type = types.get("version_digest_confirmed")
    if not event_type:
        die("EVENT_TYPE_UNRESOLVED",
            "no identifier under map.version_digest_confirmed in %s "
            "(DECISION REQUIRED D-L2-08)" % a.event_types)

    f_commit = field_for(mapping, 1, "MAP_INCOMPLETE")
    f_digest = field_for(mapping, 5, "MAP_INCOMPLETE")
    f_deployed_at = field_for(mapping, 9, "MAP_INCOMPLETE")
    f_staging_verified = field_for(mapping, 7, "MAP_INCOMPLETE")
    f_approved_by = field_for(mapping, 8, "MAP_INCOMPLETE")
    f_smoke = field_for(mapping, 10, "MAP_INCOMPLETE")
    entry9 = mapping.get(9) or mapping.get("9")
    f_environment = entry9.get("filter_field")
    if not f_environment:
        die("MAP_INCOMPLETE", "map declares no filter_field for question 9")

    def opt(v):
        return None if v in (None, "", "none", "null") else v

    record = {
        "record_schema_version": 1,
        "id": a.record_id,
        "product": a.product,
        f_environment: a.environment,
        f_commit: a.commit,
        f_digest: a.digest,
        f_deployed_at: a.now,
        f_staging_verified: (a.staging_verified == "true"),
        f_approved_by: opt(a.approved_by),
        f_smoke: opt(a.smoke_result),
        "approval_event": a.run_url,
        "uat_record": opt(a.uat_record),
        "deployed_by": a.actor,
        "rollback_of": None,
    }

    # Section 97.3 lines 8931-8944: the envelope is binding and an event missing
    # any envelope field is rejected at write time.
    event = {
        "event_schema_version": 1,
        "event_id": a.event_id,
        "event_type": event_type,
        "occurred_at": a.now,
        "recorded_at": a.now,
        "actor": a.actor,
        "product": a.product,
        "subject_ref": a.record_id,
        "payload": {
            "environment": a.environment,
            "digest": a.digest,
            "commit": a.commit,
            "run_url": a.run_url,
            "approved_by": opt(a.approved_by),
            "smoke_result": opt(a.smoke_result),
        },
    }

    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "record.yaml"), "w", encoding="utf-8") as fh:
        yaml.safe_dump(record, fh, default_flow_style=False, sort_keys=True)
    with open(os.path.join(a.out_dir, "event.yaml"), "w", encoding="utf-8") as fh:
        yaml.safe_dump(event, fh, default_flow_style=False, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
EOF

cat > tools/evidence/fixtures/event-types.fixture.yaml <<'EOF'
# LANE-OWNED FIXTURE ONLY. Not a contract. Stands in for
# contracts/events/event-types.yaml (DECISION REQUIRED D-L2-08).
# The identifiers below are DELIBERATELY prefixed `fixture_` so that shipping
# one by accident fails control-plane CI immediately (Section 97.3 line 8948:
# "control-plane CI rejects any event whose event_type is absent from it").
schema: event-types/v1
provenance: synthetic
map:
  version_digest_confirmed: fixture_version_digest_confirmed
  drift_detected: fixture_drift_detected
EOF

cat > tools/evidence/fixtures/write-interface.fixture.yaml <<'EOF'
# LANE-OWNED FIXTURE ONLY. Not a contract. Stands in for
# contracts/records/write-interface.yaml (charter DECISION REQUIRED D-L2-03).
# Shape only: every value here is a fixture value and binds to nothing real.
schema: records-write-interface/v1
provenance: synthetic
writer_entrypoint: ./tools/evidence/fixtures/stub-writer.sh
record_read_entrypoint: ./tools/evidence/fixtures/stub-reader.sh
record_id_allocator: ./tools/evidence/fixtures/stub-allocate-record-id.sh
event_id_allocator: ./tools/evidence/fixtures/stub-allocate-event-id.sh
writer_secret_name: FIXTURE_RECORDS_WRITER_TOKEN
records_repository: fixture-org/fixture-records
EOF

git add tools/evidence/build-deployment-record.sh tools/evidence/lib/build-payloads.py \
        tools/evidence/fixtures/event-types.fixture.yaml \
        tools/evidence/fixtures/write-interface.fixture.yaml
git commit -m "L2-T508: build-deployment-record.sh - record and event payload builder"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Script parses and the builder compiles | `bash -n tools/evidence/build-deployment-record.sh && python3 -m py_compile tools/evidence/lib/build-payloads.py; echo $?` | exactly `0` |
| A2 | A well-formed call writes both payloads | see SELF-VERIFY | `record.yaml` and `event.yaml` both exist |
| A3 | The record uses the map's field names, not invented ones | `grep -c '^digest:\|^commit:\|^environment:\|^deployed_at:' /tmp/ev508/out/record.yaml` | exactly `4` |
| A4 | The event carries all nine §97.3 envelope fields | see SELF-VERIFY | exactly `9` |
| A5 | A malformed record id is refused | `… --record-id DEP-BAD …; echo $?` | stderr contains `ID_MALFORMED`, exit `2` |
| A6 | An event-types file with no `version_digest_confirmed` is refused | see SELF-VERIFY | stderr contains `EVENT_TYPE_UNRESOLVED`, exit `2` |
| A7 | Timestamps carry the UTC offset (§97.1 L8838) | `grep -c '+00:00' /tmp/ev508/out/event.yaml` | `2` or more |
| A8 | The script constructs no store path and names no secret | `grep -cE "records/|events/|secrets\.|tools/records" tools/evidence/build-deployment-record.sh tools/evidence/lib/build-payloads.py \| paste -sd+ \| bc` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
B=tools/evidence/build-deployment-record.sh; F=tools/evidence/fixtures
mkdir -p /tmp/ev508/out && rm -rf /tmp/ev508/out && mkdir -p /tmp/ev508/out
bash -n "$B" && python3 -m py_compile tools/evidence/lib/build-payloads.py || { echo "L2-T508 FAIL compile"; exit 1; }
"$B" --map $F/map.fixture.yaml --event-types $F/event-types.fixture.yaml \
     --record-id DEP-2026-01-05-002 --event-id EVT-2026-01-05-000002 \
     --product fixture-product --environment production \
     --digest sha256:aaaa000000000000000000000000000000000000000000000000000000000001 \
     --commit 1111111111111111111111111111111111111111 \
     --run-url https://example.invalid/runs/1 --actor fixture-deployer \
     --approved-by fixture-approver --staging-verified true --smoke-result pass \
     --uat-record records-uat-fixture --out-dir /tmp/ev508/out >/dev/null; RC1=$?
"$B" --map $F/map.fixture.yaml --event-types $F/event-types.fixture.yaml \
     --record-id DEP-BAD --event-id EVT-2026-01-05-000002 \
     --product p --environment production --digest d --commit c \
     --run-url u --actor a --out-dir /tmp/ev508/bad >/tmp/ev508/e2.txt 2>&1; RC2=$?
printf 'schema: event-types/v1\nmap: {}\n' > /tmp/ev508/empty-types.yaml
"$B" --map $F/map.fixture.yaml --event-types /tmp/ev508/empty-types.yaml \
     --record-id DEP-2026-01-05-002 --event-id EVT-2026-01-05-000002 \
     --product p --environment production --digest d --commit c \
     --run-url u --actor a --out-dir /tmp/ev508/bad2 >/tmp/ev508/e3.txt 2>&1; RC3=$?
ENV_FIELDS=$(python3 -c "import yaml;d=yaml.safe_load(open('/tmp/ev508/out/event.yaml'));print(len([k for k in ('event_schema_version','event_id','event_type','occurred_at','recorded_at','actor','product','subject_ref','payload') if k in d]))")
test "$RC1" = "0" && test -f /tmp/ev508/out/record.yaml && test -f /tmp/ev508/out/event.yaml \
 && test "$ENV_FIELDS" = "9" \
 && test "$RC2" = "2" && grep -q 'ID_MALFORMED' /tmp/ev508/e2.txt \
 && test "$RC3" = "2" && grep -q 'EVENT_TYPE_UNRESOLVED' /tmp/ev508/e3.txt \
 && test "$(grep -c '+00:00' /tmp/ev508/out/event.yaml)" -ge 2 \
 && test "$(grep -chE "records/|events/|secrets\.|tools/records" "$B" tools/evidence/lib/build-payloads.py | paste -sd+ - | bc)" = "0" \
 && echo "L2-T508 OK" || echo "L2-T508 FAIL"
```
Correct output: the single line `L2-T508 OK`.

**STOP rule:** if `contracts/records/write-interface.yaml` was recorded `present: false` by `L2-T501`, this task still completes — it consumes only the map and the event-type file, and both have fixtures. If completing it appears to require minting a record or event id, STOP under STOP RULE `S4` and cite charter DECISION REQUIRED **D-L2-03**: allocating an id is the write interface's act, and a lane-local counter is a shared mutable index (PARTITION.md rule 3). If completing it appears to require a real `event_type` string, STOP under **D-L2-08** — a guessed identifier is rejected at write time by control-plane CI (§97.3 L8948) and fails every deploy that carries it.

---

### L2-T509 — Author `.github/workflows/emit-deployment-record.yml`

**Size:** M  **Depends on:** `L2-T508`

**Creates:** `.github/workflows/emit-deployment-record.yml`

§97.2 (L8926) is the whole specification of this workflow: the record and event writes are **required, failing steps**. Three properties follow, and each is separately asserted below:

1. **No step may be optional.** No `continue-on-error`, no `if: always()`, no `|| true`. A record that could not be written fails the calling deploy job.
2. **The write is verified by reading it back.** A writer that exits 0 without landing the record leaves the chain open exactly as if it had failed, and §97.2's write-freshness paragraph (L8905) exists because that failure is invisible.
3. **One file per event, never an append** (§97.3 L8929, PARTITION.md rule 3). The workflow asserts the event path did not already exist.

The reusable workflow declares its own secret **parameter** named `RECORDS_WRITER_TOKEN`. That is this workflow's input name, not a repository secret name: the caller maps whatever `contracts/records/write-interface.yaml` declares under `writer_secret_name` onto it. Lane 2 never names a repository secret (charter §4.4).

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > .github/workflows/emit-deployment-record.yml <<'EOF'
name: emit-deployment-record
# =====================================================================
# THE REQUIRED, FAILING RECORD AND EVENT WRITE
# Spec: Section 97.2 line 8926 - "the deployment-record and event writes are
# required, failing steps of deploy-production.yml rather than trailing
# best-effort ones: a deploy whose record cannot be written is a deploy whose
# evidence chain does not close, and the eleven questions of Section 32 are
# unanswerable for it afterwards."
# Section 97.1 line 8841 - the write path is the records-writer credential into
# the records repository. Section 97.3 line 8929 - one file per event, never a
# concurrent append to a shared period file.
# Lane 2 owns this workflow. It owns NO record shape and NO store path: both are
# resolved at run time from contracts/records/write-interface.yaml (Lane 4's
# published interface, PARTITION.md rule 4).
# =====================================================================
on:
  workflow_call:
    inputs:
      product:
        description: 'The product whose deployment is being recorded.'
        required: true
        type: string
      environment_name:
        description: 'staging | production'
        required: true
        type: string
      digest:
        description: 'The artifact digest deployed, or the S18 recorded identity.'
        required: true
        type: string
      commit:
        description: 'The git commit the artifact was built from.'
        required: true
        type: string
      run_url:
        description: 'The URL of the run that performed the deployment.'
        required: true
        type: string
      approved_by:
        description: 'The approving identity, or the literal none for staging.'
        required: true
        type: string
      staging_verified:
        description: 'true | false'
        required: true
        type: string
      smoke_result:
        description: 'pass | fail | none'
        required: true
        type: string
      uat_record:
        description: 'The UAT record reference, or the literal none.'
        required: true
        type: string
    secrets:
      RECORDS_WRITER_TOKEN:
        required: true

permissions:
  contents: read

jobs:
  emit-deployment-record:
    name: emit-deployment-record
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Check out the control plane
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683

      - name: Resolve the write interface — fail closed on any absent key
        id: iface
        run: |
          set -euo pipefail
          IFACE=contracts/records/write-interface.yaml
          test -f "$IFACE" || { echo "RECORD_WRITE_INTERFACE_ABSENT"; exit 1; }
          python3 -c 'import yaml' 2>/dev/null || pip3 install --quiet 'pyyaml==6.0.2'
          python3 - "$IFACE" <<'PYEOF' >> "$GITHUB_OUTPUT"
          import sys, yaml
          doc = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
          required = ["writer_entrypoint", "record_read_entrypoint",
                      "record_id_allocator", "event_id_allocator"]
          missing = [k for k in required if not doc.get(k)]
          if missing:
              print("RECORD_WRITE_INTERFACE_INCOMPLETE %s" % ",".join(missing))
              sys.exit(1)
          for k in required:
              print("%s=%s" % (k, doc[k]))
          PYEOF
          echo "WRITE_INTERFACE_RESOLVED"

      - name: Resolve the event-type identifier — fail closed if unenumerated
        id: etype
        run: |
          set -euo pipefail
          TYPES=contracts/events/event-types.yaml
          test -f "$TYPES" || { echo "EVENT_TYPE_ENUM_ABSENT"; exit 1; }
          grep -q 'version_digest_confirmed' "$TYPES" \
            || { echo "EVENT_TYPE_UNRESOLVED"; exit 1; }
          echo "EVENT_TYPE_RESOLVED"

      - name: Allocate the record and event identifiers
        id: ids
        env:
          RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
          PRODUCT: ${{ inputs.product }}
        run: |
          set -euo pipefail
          RECORD_ID="$(${{ steps.iface.outputs.record_id_allocator }} --product "${PRODUCT}" --kind deployment)"
          EVENT_ID="$(${{ steps.iface.outputs.event_id_allocator }} --product "${PRODUCT}")"
          test -n "${RECORD_ID}" || { echo "RECORD_ID_UNALLOCATED"; exit 1; }
          test -n "${EVENT_ID}"  || { echo "EVENT_ID_UNALLOCATED"; exit 1; }
          echo "record_id=${RECORD_ID}" >> "$GITHUB_OUTPUT"
          echo "event_id=${EVENT_ID}"   >> "$GITHUB_OUTPUT"

      - name: Build the record and event payloads
        env:
          PRODUCT: ${{ inputs.product }}
          ENVIRONMENT_NAME: ${{ inputs.environment_name }}
          DIGEST: ${{ inputs.digest }}
          COMMIT: ${{ inputs.commit }}
          RUN_URL: ${{ inputs.run_url }}
          APPROVED_BY: ${{ inputs.approved_by }}
          STAGING_VERIFIED: ${{ inputs.staging_verified }}
          SMOKE_RESULT: ${{ inputs.smoke_result }}
          UAT_RECORD: ${{ inputs.uat_record }}
          RECORD_ID: ${{ steps.ids.outputs.record_id }}
          EVENT_ID: ${{ steps.ids.outputs.event_id }}
        run: |
          set -euo pipefail
          test -f contracts/evidence/eleven-question-map.yaml \
            || { echo "ELEVEN_QUESTION_MAP_ABSENT"; exit 1; }
          ./tools/evidence/build-deployment-record.sh \
            --map contracts/evidence/eleven-question-map.yaml \
            --event-types contracts/events/event-types.yaml \
            --record-id "${RECORD_ID}" --event-id "${EVENT_ID}" \
            --product "${PRODUCT}" --environment "${ENVIRONMENT_NAME}" \
            --digest "${DIGEST}" --commit "${COMMIT}" --run-url "${RUN_URL}" \
            --actor "${GITHUB_ACTOR}" --approved-by "${APPROVED_BY}" \
            --staging-verified "${STAGING_VERIFIED}" \
            --smoke-result "${SMOKE_RESULT}" --uat-record "${UAT_RECORD}" \
            --out-dir ./.evidence-out
          test -f ./.evidence-out/record.yaml || { echo "RECORD_PAYLOAD_ABSENT"; exit 1; }
          test -f ./.evidence-out/event.yaml  || { echo "EVENT_PAYLOAD_ABSENT"; exit 1; }
          echo "PAYLOADS_BUILT"

      - name: Write the record and the event — this step is required and fails closed
        env:
          RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
          PRODUCT: ${{ inputs.product }}
          RECORD_ID: ${{ steps.ids.outputs.record_id }}
          EVENT_ID: ${{ steps.ids.outputs.event_id }}
        run: |
          set -euo pipefail
          ${{ steps.iface.outputs.writer_entrypoint }} \
            --kind deployment --product "${PRODUCT}" --id "${RECORD_ID}" \
            --payload ./.evidence-out/record.yaml --create-only \
            || { echo "RECORD_WRITE_FAILED"; exit 1; }
          ${{ steps.iface.outputs.writer_entrypoint }} \
            --kind event --product "${PRODUCT}" --id "${EVENT_ID}" \
            --payload ./.evidence-out/event.yaml --create-only \
            || { echo "EVENT_WRITE_FAILED"; exit 1; }
          echo "WRITES_SUBMITTED"

      - name: Read both back — a writer that exits 0 without landing is a failure
        env:
          RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
          PRODUCT: ${{ inputs.product }}
          DIGEST: ${{ inputs.digest }}
          RECORD_ID: ${{ steps.ids.outputs.record_id }}
          EVENT_ID: ${{ steps.ids.outputs.event_id }}
        run: |
          set -euo pipefail
          ${{ steps.iface.outputs.record_read_entrypoint }} \
            --kind deployment --id "${RECORD_ID}" > readback-record.yaml \
            || { echo "RECORD_READBACK_FAILED"; exit 1; }
          ${{ steps.iface.outputs.record_read_entrypoint }} \
            --kind event --id "${EVENT_ID}" > readback-event.yaml \
            || { echo "EVENT_READBACK_FAILED"; exit 1; }
          grep -qF "${DIGEST}" readback-record.yaml \
            || { echo "RECORD_READBACK_MISMATCH"; exit 1; }
          grep -qF "${EVENT_ID}" readback-event.yaml \
            || { echo "EVENT_READBACK_MISMATCH"; exit 1; }
          echo "EVIDENCE_CHAIN_WRITE_CONFIRMED ${RECORD_ID} ${EVENT_ID}"
EOF
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/emit-deployment-record.yml'))" \
  || { echo "YAML PARSE FAILED — STOP"; exit 1; }
git add .github/workflows/emit-deployment-record.yml
git commit -m "L2-T509: emit-deployment-record.yml - the required, failing record and event write"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Valid YAML | `python3 -c "import yaml;yaml.safe_load(open('.github/workflows/emit-deployment-record.yml'))"; echo $?` | exactly `0` |
| A2 | No step is optional (§97.2 L8926) | `grep -cE 'continue-on-error|if: always\(\)|\|\| true' .github/workflows/emit-deployment-record.yml` | exactly `0` |
| A3 | Every failure token is present | `for t in RECORD_WRITE_INTERFACE_ABSENT RECORD_WRITE_INTERFACE_INCOMPLETE EVENT_TYPE_ENUM_ABSENT EVENT_TYPE_UNRESOLVED RECORD_ID_UNALLOCATED EVENT_ID_UNALLOCATED ELEVEN_QUESTION_MAP_ABSENT RECORD_WRITE_FAILED EVENT_WRITE_FAILED RECORD_READBACK_FAILED RECORD_READBACK_MISMATCH; do grep -q "$t" .github/workflows/emit-deployment-record.yml \|\| echo "MISSING $t"; done` | prints nothing |
| A4 | The write is verified by reading back | `grep -c 'EVIDENCE_CHAIN_WRITE_CONFIRMED' .github/workflows/emit-deployment-record.yml` | exactly `1` |
| A5 | Writes are create-only — never an append to a shared file (PARTITION rule 3, §97.3 L8929) | `grep -c -- '--create-only' .github/workflows/emit-deployment-record.yml` | exactly `2` |
| A6 | No store path is hard-coded | `grep -cE 'records/(deployments|uat|incidents)/|^\s*events/' .github/workflows/emit-deployment-record.yml` | exactly `0` |
| A7 | No repository secret is named — only the workflow's own parameter | `grep -oE 'secrets\.[A-Z_]+' .github/workflows/emit-deployment-record.yml \| sort -u` | exactly `secrets.RECORDS_WRITER_TOKEN` |
| A8 | The one Action used is SHA-pinned (§48.1) | `grep -oE 'uses: [^ ]+' .github/workflows/emit-deployment-record.yml \| grep -cE '@[0-9a-f]{40}$'` | exactly `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
W=.github/workflows/emit-deployment-record.yml
python3 -c "import yaml;yaml.safe_load(open('$W'))" \
 && test "$(grep -cE 'continue-on-error|if: always\(\)|\|\| true' "$W")" = "0" \
 && test "$(grep -c -- '--create-only' "$W")" = "2" \
 && test "$(grep -c 'EVIDENCE_CHAIN_WRITE_CONFIRMED' "$W")" = "1" \
 && test "$(grep -cE 'records/(deployments|uat|incidents)/' "$W")" = "0" \
 && test "$(grep -oE 'secrets\.[A-Z_]+' "$W" | sort -u | tr '\n' ' ')" = "secrets.RECORDS_WRITER_TOKEN " \
 && test "$(grep -oE 'uses: [^ ]+' "$W" | grep -cE '@[0-9a-f]{40}$')" = "1" \
 && for t in RECORD_WRITE_INTERFACE_ABSENT RECORD_WRITE_INTERFACE_INCOMPLETE \
             EVENT_TYPE_ENUM_ABSENT EVENT_TYPE_UNRESOLVED RECORD_ID_UNALLOCATED \
             EVENT_ID_UNALLOCATED ELEVEN_QUESTION_MAP_ABSENT RECORD_WRITE_FAILED \
             EVENT_WRITE_FAILED RECORD_READBACK_FAILED RECORD_READBACK_MISMATCH; do \
      grep -q "$t" "$W" || exit 1; done \
 && echo "L2-T509 OK" || echo "L2-T509 FAIL"
```
Correct output: the single line `L2-T509 OK`.

**STOP rule:** if the `actions/checkout` commit SHA above does not resolve in the target organisation's allowed-actions configuration, STOP — §48.1 (L4300–4308) forbids substituting a tag. File the blocker with STOP RULE `S4`. If making this workflow green in a live run appears to require adding `continue-on-error` to the write step, STOP under STOP RULE `S4` and quote §97.2 L8926 in the blocker: a best-effort record write is precisely the thing that paragraph forbids, and the correct fix is upstream — in the write interface or its credential — never here.

---

### L2-T510 — Wire the emitter into `deploy-staging.yml` and `deploy-production.yml`

**Size:** S  **Depends on:** `L2-T509`

**Edits (at a named anchor only):**
- `.github/workflows/deploy-staging.yml`
- `.github/workflows/deploy-production.yml`

Both files are subsystem E's, in the same lane and the same owned tree. This task edits them **only** at the anchor line `# EVIDENCE-CHAIN-ANCHOR: emit-deployment-record`, which subsystem E places. If the anchor is absent, subsystem E has not reached the point where the emitter can be wired, and this task STOPs — it never invents a job placement inside another phase's workflow, and it never creates either file.

The patch is idempotent: run twice, it prints `ALREADY_WIRED` and changes nothing.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for W in .github/workflows/deploy-staging.yml .github/workflows/deploy-production.yml; do
  test -f "$W" || { echo "EVIDENCE-FAIL DEPLOY_WORKFLOW_ABSENT: $W — SUBSYSTEM E NOT DONE — STOP"; exit 1; }
  grep -q '# EVIDENCE-CHAIN-ANCHOR: emit-deployment-record' "$W" \
    || { echo "EVIDENCE-FAIL ANCHOR_ABSENT: $W — STOP"; exit 1; }
done

python3 - <<'PYEOF'
import io, sys

ANCHOR = "  # EVIDENCE-CHAIN-ANCHOR: emit-deployment-record"
BLOCK = """  emit-deployment-record:
    # Section 97.2 line 8926: the deployment-record and event writes are
    # required, failing steps of this workflow. This job is not optional and
    # carries no `if:` — a deploy whose record cannot be written is a deploy
    # whose evidence chain does not close.
    needs: [deploy]
    uses: ./.github/workflows/emit-deployment-record.yml
    with:
      product: ${{ inputs.product }}
      environment_name: ${{ inputs.environment_name }}
      digest: ${{ inputs.digest }}
      commit: ${{ inputs.commit }}
      run_url: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
      approved_by: ${{ inputs.approved_by }}
      staging_verified: ${{ inputs.staging_verified }}
      smoke_result: ${{ needs.deploy.outputs.smoke_result }}
      uat_record: ${{ inputs.uat_record }}
    secrets:
      RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
"""

changed = 0
for path in (".github/workflows/deploy-staging.yml",
             ".github/workflows/deploy-production.yml"):
    src = io.open(path, encoding="utf-8").read()
    if "emit-deployment-record:" in src and "uses: ./.github/workflows/emit-deployment-record.yml" in src:
        print("ALREADY_WIRED %s" % path)
        continue
    if ANCHOR not in src:
        print("EVIDENCE-FAIL ANCHOR_ABSENT: %s" % path)
        sys.exit(1)
    io.open(path, "w", encoding="utf-8").write(src.replace(ANCHOR, BLOCK + ANCHOR, 1))
    print("WIRED %s" % path)
    changed += 1
print("CHANGED=%d" % changed)
PYEOF

for W in .github/workflows/deploy-staging.yml .github/workflows/deploy-production.yml; do
  python3 -c "import yaml,sys;yaml.safe_load(open('$W'))" \
    || { echo "YAML PARSE FAILED after patch: $W — git checkout -- $W and STOP"; exit 1; }
done
git add .github/workflows/deploy-staging.yml .github/workflows/deploy-production.yml
git commit -m "L2-T510: wire emit-deployment-record into both deploy workflows at the named anchor"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Both deploy workflows still parse | `for W in deploy-staging deploy-production; do python3 -c "import yaml;yaml.safe_load(open('.github/workflows/$W.yml'))"; done; echo $?` | exactly `0` |
| A2 | The emitter is called from both | `grep -lc 'uses: ./.github/workflows/emit-deployment-record.yml' .github/workflows/deploy-staging.yml .github/workflows/deploy-production.yml \| wc -l` | exactly `2` |
| A3 | The emitter job carries no `if:` (§97.2 L8926 — required, not conditional) | `python3 -c "import yaml;print(sum(1 for w in ('deploy-staging','deploy-production') for j,v in yaml.safe_load(open('.github/workflows/%s.yml'%w))['jobs'].items() if j=='emit-deployment-record' and 'if' in v))"` | exactly `0` |
| A4 | Re-running the patch changes nothing | run the patch block a second time | prints `ALREADY_WIRED` twice and `CHANGED=0` |
| A5 | Only the two deploy workflows were modified | `git diff --name-only HEAD~1 HEAD` | exactly the two `deploy-*.yml` paths |
| A6 | The anchor line is still present for a future phase | `grep -c 'EVIDENCE-CHAIN-ANCHOR' .github/workflows/deploy-production.yml` | exactly `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
S=.github/workflows/deploy-staging.yml; P=.github/workflows/deploy-production.yml
python3 -c "import yaml;yaml.safe_load(open('$S'));yaml.safe_load(open('$P'))" \
 && test "$(grep -lc 'uses: ./.github/workflows/emit-deployment-record.yml' "$S" "$P" | wc -l | tr -d ' ')" = "2" \
 && test "$(python3 -c "import yaml;print(sum(1 for w in ('$S','$P') for j,v in yaml.safe_load(open(w))['jobs'].items() if j=='emit-deployment-record' and 'if' in v))")" = "0" \
 && test "$(grep -c 'EVIDENCE-CHAIN-ANCHOR' "$P")" = "1" \
 && test "$(git diff --name-only HEAD~1 HEAD | grep -vcE '^\.github/workflows/deploy-(staging|production)\.yml$')" = "0" \
 && echo "L2-T510 OK" || echo "L2-T510 FAIL"
```
Correct output: the single line `L2-T510 OK`.

**STOP rule:** if either deploy workflow is absent, or the anchor line is absent from either, STOP — do **not** create the workflow, do **not** choose a job placement, and do **not** append the block to the end of the file. File the blocker with STOP RULE `S4`, TASK `L2-T510`, naming the file and asking subsystem E to place the anchor line `# EVIDENCE-CHAIN-ANCHOR: emit-deployment-record`. If the patch lands but the YAML no longer parses, run `git checkout -- <file>` and STOP under STOP RULE `S5` — the anchor's indentation in that file differs from the two-space job indentation this patch assumes, and the correct fix is a corrected anchor from subsystem E, not a hand-edit here.

---

### L2-T511 — Author `.github/workflows/verify-digest-chain.yml` — the scheduled sweep

**Size:** M  **Depends on:** `L2-T506`, `L2-T507`

**Creates:**
- `.github/workflows/verify-digest-chain.yml`
- `tools/evidence/canary/observations.jsonl`
- `tools/evidence/canary/records/production.yaml`
- `tools/evidence/canary/README.md`

§99.2's named build-surface tool (L9215) is *"Scheduled sweep comparing every production `/version` digest against its approval record; any mismatch is a P0 investigation."* This workflow is that schedule. It has three triggers and one shape:

| Trigger | Why it exists | Spec |
|---|---|---|
| `schedule` | the sweep itself | §99.2 L9215 |
| `workflow_dispatch` | run on demand as the outage-recovery gate | §46.1 L4126 |
| `workflow_call` | so `L2-T513`'s deploy gate can run it in-line | §46.1 L4126 |

**Cadence.** §51.2's control-plane objective table (L4457) fixes drift-detection freshness at *"Security-class checks at least hourly"*, and §53.1 (L4688) states *"P0 for the blocking rows, which are security controls."* Artifact digest mismatch is a blocking row (§53.2 Level 4, L4697). The sweep therefore runs hourly. The minute-of-hour is not a spec value; this task fixes it at `:20` so the schedule is deterministic and reproducible, and changing it is an ordinary edit inside an owned path, never a decision.

**The seeded canary, and why the sweep is not trusted without it.** §53.1 (L4680): *"A permanent seeded drift record — a deliberately planted, clearly labelled mismatch in the comparison set — exists at all times, and every reconciliation run MUST find it. A run that reports zero findings, including the canary, is a FAILED run, not a clean one: it proves the instrument stopped looking."* This workflow therefore runs the sweep **twice**: once over the canary estate, where a clean result means the instrument is blind and the run fails with `CANARY_NOT_FOUND`; and once over the live estate, where a finding means a mismatch. The canary estate lives at `tools/evidence/canary/` and is separate from `tools/evidence/fixtures/` so that `L2-T503`'s five-estate count is unchanged.

**Transport.** The runner label and the scrape credential come from `contracts/evidence/version-observation.yaml` (DECISION REQUIRED **D-L2-09**). This workflow reads them at run time and fails closed with `VERSION_OBSERVATION_TRANSPORT_UNRESOLVED` if the file or either key is absent. Lane 2 never writes that file and never guesses the label.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
mkdir -p tools/evidence/canary/records

cat > tools/evidence/canary/README.md <<'EOF'
# The seeded canary for the digest-chain sweep

Spec: Section 53.1 line 4680 - "A permanent seeded drift record - a deliberately
planted, clearly labelled mismatch in the comparison set - exists at all times,
and every reconciliation run MUST find it. A run that reports zero findings,
including the canary, is a FAILED run, not a clean one: it proves the instrument
stopped looking, not that nothing drifted."

DO NOT REMEDIATE. DO NOT DELETE. DO NOT MAKE THESE TWO DIGESTS MATCH.

The estate below is a permanent, synthetic, deliberately mismatched pair: a
production deployment record for one digest, and an observation of a different
digest. `verify-digest-chain` MUST exit 3 over it on every run. If it exits 0,
the sweep has stopped comparing and `.github/workflows/verify-digest-chain.yml`
fails the whole run with CANARY_NOT_FOUND before it ever reports on the live
estate.

Nothing here is counted as a live finding: the canary sweep writes its own
findings file and that file is never escalated (L2-T512 escalates the live
findings file only).
EOF

cat > tools/evidence/canary/records/production.yaml <<'EOF'
# SEEDED CANARY - deliberate permanent mismatch (Section 53.1, line 4680).
# Do not remediate. Do not delete. Synthetic product, synthetic digest.
record_schema_version: 1
id: DEP-2026-01-01-999
product: canary-sentinel-do-not-provision
environment: production
commit: 9999999999999999999999999999999999999999
digest: sha256:dddd000000000000000000000000000000000000000000000000000000000001
deployed_at: 2026-01-01T00:00:00+00:00
staging_verified: true
smoke_result: pass
uat_record: canary-uat-reference
approved_by: canary-approver
approval_event: https://example.invalid/runs/canary
deployed_by: canary-deployer
rollback_of: null
EOF

cat > tools/evidence/canary/observations.jsonl <<'EOF'
{"product":"canary-sentinel-do-not-provision","observed_digest":"sha256:eeee000000000000000000000000000000000000000000000000000000000002","observed_at":"2026-01-01T00:00:00+00:00","source":"seeded-canary","conformance_profile":"service","collect_error":null}
EOF

cat > .github/workflows/verify-digest-chain.yml <<'EOF'
name: verify-digest-chain
# =====================================================================
# THE DIGEST-VS-APPROVAL SCHEDULED SWEEP
# Spec: Section 99.2 named tools, line 9215 - "Scheduled sweep comparing every
# production /version digest against its approval record; any mismatch is a P0
# investigation." Section 41.2 line 3729. Section 32 line 2823 (item 5 must
# equal item 11). Section 46.1 line 4126 - completion of recovery step 3,
# executed by this script, gates resumption of production deploys.
# Cadence: Section 51.2 line 4457, "Security-class checks at least hourly",
# with Section 53.1 line 4688 - the blocking rows are security controls.
# Section 53.1 line 4680 - the seeded canary must be found on every run.
# Lane 2 owns this workflow. It presents nothing: the digest-match view is
# subsystem H's (Lane 5) and the metric is subsystem I's (Lane 4).
# =====================================================================
on:
  schedule:
    - cron: '20 * * * *'
  workflow_dispatch:
    inputs:
      product:
        description: 'Sweep one product only. Leave empty to sweep the estate.'
        required: false
        type: string
  workflow_call:
    inputs:
      product:
        description: 'Sweep one product only. Leave empty to sweep the estate.'
        required: false
        type: string
    outputs:
      findings_count:
        description: 'Number of blocking findings in the live sweep.'
        value: ${{ jobs.sweep.outputs.findings_count }}

permissions:
  contents: read

jobs:
  sweep:
    name: verify-digest-chain
    runs-on: ubuntu-latest
    timeout-minutes: 20
    outputs:
      findings_count: ${{ steps.live.outputs.findings_count }}
    steps:
      - name: Check out the control plane
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683

      - name: Install PyYAML
        run: |
          set -euo pipefail
          python3 -c 'import yaml' 2>/dev/null || pip3 install --quiet 'pyyaml==6.0.2'
          echo "PYYAML_READY"

      - name: Prove the instrument still looks — the seeded canary
        run: |
          set -euo pipefail
          # Section 53.1 line 4680: a run that reports zero findings, including
          # the canary, is a FAILED run. Exit 3 here is the CORRECT outcome.
          set +e
          ./tools/evidence/verify-digest-chain \
            --records tools/evidence/canary/records \
            --observations tools/evidence/canary/observations.jsonl \
            --findings-out canary-findings.json > canary.log 2>&1
          RC=$?
          set -e
          cat canary.log
          if [ "$RC" != "3" ]; then
            echo "CANARY_NOT_FOUND rc=${RC}"
            exit 1
          fi
          echo "CANARY_FOUND"

      - name: Resolve the /version observation transport — fail closed
        id: transport
        run: |
          set -euo pipefail
          OBS=contracts/evidence/version-observation.yaml
          test -f "$OBS" || { echo "VERSION_OBSERVATION_TRANSPORT_UNRESOLVED"; exit 1; }
          python3 - "$OBS" <<'PYEOF' >> "$GITHUB_OUTPUT"
          import sys, yaml
          doc = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
          missing = [k for k in ("runner_label", "credential_secret_name", "targets_file")
                     if not doc.get(k)]
          if missing:
              print("VERSION_OBSERVATION_TRANSPORT_UNRESOLVED %s" % ",".join(missing))
              sys.exit(1)
          for k in ("runner_label", "credential_secret_name", "targets_file"):
              print("%s=%s" % (k, doc[k]))
          PYEOF
          echo "TRANSPORT_RESOLVED"

      - name: Collect the live /version observations
        env:
          EV_VERSION_TOKEN: ${{ secrets[steps.transport.outputs.credential_secret_name] }}
          ONLY_PRODUCT: ${{ inputs.product }}
        run: |
          set -euo pipefail
          TARGETS='${{ steps.transport.outputs.targets_file }}'
          test -f "${TARGETS}" || { echo "VERSION_TARGETS_ABSENT ${TARGETS}"; exit 1; }
          ARGS=(--targets "${TARGETS}" --out live-observations.jsonl --strict)
          if [ -n "${ONLY_PRODUCT}" ]; then ARGS+=(--product "${ONLY_PRODUCT}"); fi
          ./tools/evidence/collect-version.sh "${ARGS[@]}" \
            || { echo "OBSERVATION_INCOMPLETE"; exit 1; }
          echo "OBSERVATIONS_READY lines=$(wc -l < live-observations.jsonl | tr -d ' ')"

      - name: Resolve the records store and sweep the live estate
        id: live
        env:
          RECORDS_READ_TOKEN: ${{ secrets.RECORDS_READ_TOKEN }}
          ONLY_PRODUCT: ${{ inputs.product }}
        run: |
          set -euo pipefail
          IFACE=contracts/records/write-interface.yaml
          test -f "$IFACE" || { echo "RECORD_WRITE_INTERFACE_ABSENT"; exit 1; }
          READER="$(python3 -c "import yaml,sys;print((yaml.safe_load(open('$IFACE',encoding='utf-8')) or {}).get('record_read_entrypoint',''))")"
          test -n "${READER}" || { echo "RECORD_WRITE_INTERFACE_INCOMPLETE record_read_entrypoint"; exit 1; }
          ${READER} --kind deployment --environment production --export-dir ./live-records \
            || { echo "RECORDS_UNREADABLE"; exit 1; }
          set +e
          ARGS=(--records ./live-records --observations live-observations.jsonl --findings-out live-findings.json)
          if [ -n "${ONLY_PRODUCT}" ]; then ARGS+=(--product "${ONLY_PRODUCT}"); fi
          ./tools/evidence/verify-digest-chain "${ARGS[@]}" > live.log 2>&1
          RC=$?
          set -e
          cat live.log
          COUNT="$(python3 -c "import json;print(len(json.load(open('live-findings.json'))['findings']))")"
          echo "findings_count=${COUNT}" >> "$GITHUB_OUTPUT"
          case "${RC}" in
            0) echo "SWEEP_CLEAN"; ;;
            3) echo "SWEEP_BLOCKING findings=${COUNT}"; ;;
            *) echo "SWEEP_BROKEN rc=${RC}"; exit 1 ;;
          esac
          echo "sweep_rc=${RC}" >> "$GITHUB_OUTPUT"

      - name: Publish the findings file for the escalation job
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02
        with:
          name: digest-chain-findings
          path: live-findings.json
          if-no-files-found: error

      - name: Fail the run on any blocking finding — Section 53.2 Level 4
        run: |
          set -euo pipefail
          # Section 53.2 line 4697: artifact digest mismatch is Blocking-class
          # drift - "Fail CI or block the deployment path until resolved."
          test "${{ steps.live.outputs.sweep_rc }}" = "0" \
            || { echo "DIGEST_CHAIN_BLOCKING"; exit 1; }
          echo "DIGEST_CHAIN_CLEAN"
EOF
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/verify-digest-chain.yml'))" \
  || { echo "YAML PARSE FAILED — STOP"; exit 1; }
git add .github/workflows/verify-digest-chain.yml tools/evidence/canary
git commit -m "L2-T511: verify-digest-chain.yml - the hourly sweep with its seeded canary"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Valid YAML | `python3 -c "import yaml;yaml.safe_load(open('.github/workflows/verify-digest-chain.yml'))"; echo $?` | exactly `0` |
| A2 | All three triggers present (§99.2 L9215, §46.1 L4126) | `python3 -c "import yaml;print(sorted(yaml.safe_load(open('.github/workflows/verify-digest-chain.yml'))[True].keys()))"` | exactly `['schedule', 'workflow_call', 'workflow_dispatch']` |
| A3 | Hourly cadence (§51.2 L4457) | `grep -c "cron: '20 \* \* \* \*'" .github/workflows/verify-digest-chain.yml` | exactly `1` |
| A4 | The canary estate genuinely mismatches | see SELF-VERIFY | `verify-digest-chain` over `tools/evidence/canary` exits `3` |
| A5 | A blind sweep fails the run | `grep -c 'CANARY_NOT_FOUND' .github/workflows/verify-digest-chain.yml` | exactly `1` |
| A6 | Unresolved transport fails closed, never defaults | `grep -c 'VERSION_OBSERVATION_TRANSPORT_UNRESOLVED' .github/workflows/verify-digest-chain.yml` | exactly `2` |
| A7 | A broken sweep is never a clean sweep | `grep -c 'SWEEP_BROKEN' .github/workflows/verify-digest-chain.yml` | exactly `1` |
| A8 | No step is optional | `grep -cE 'continue-on-error|if: always\(\)' .github/workflows/verify-digest-chain.yml` | exactly `0` |
| A9 | Both Actions are SHA-pinned (§48.1) | `grep -oE 'uses: [^ ]+' .github/workflows/verify-digest-chain.yml \| grep -cE '@[0-9a-f]{40}$'` | exactly `2` |
| A10 | No runner label is hard-coded beyond the ubuntu default, and no scrape secret is named | `grep -cE 'self-hosted|SCRAPE_|VERSION_TOKEN_' .github/workflows/verify-digest-chain.yml` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
W=.github/workflows/verify-digest-chain.yml; V=tools/evidence/verify-digest-chain
mkdir -p /tmp/ev511
"$V" --records tools/evidence/canary/records \
     --observations tools/evidence/canary/observations.jsonl \
     --findings-out /tmp/ev511/canary.json > /tmp/ev511/canary.log 2>&1; RCC=$?
python3 -c "import yaml;yaml.safe_load(open('$W'))" \
 && test "$RCC" = "3" \
 && test "$(python3 -c "import yaml;print(sorted(yaml.safe_load(open('$W'))[True].keys()))")" = "['schedule', 'workflow_call', 'workflow_dispatch']" \
 && test "$(grep -c "cron: '20 \* \* \* \*'" "$W")" = "1" \
 && test "$(grep -c 'CANARY_NOT_FOUND' "$W")" = "1" \
 && test "$(grep -c 'VERSION_OBSERVATION_TRANSPORT_UNRESOLVED' "$W")" = "2" \
 && test "$(grep -c 'SWEEP_BROKEN' "$W")" = "1" \
 && test "$(grep -cE 'continue-on-error|if: always\(\)' "$W")" = "0" \
 && test "$(grep -oE 'uses: [^ ]+' "$W" | grep -cE '@[0-9a-f]{40}$')" = "2" \
 && test "$(grep -cE 'self-hosted|SCRAPE_|VERSION_TOKEN_' "$W")" = "0" \
 && echo "L2-T511 OK" || echo "L2-T511 FAIL"
```
Correct output: the single line `L2-T511 OK`.

**STOP rule:** if `contracts/evidence/version-observation.yaml` was recorded `present: false` by `L2-T501`, this task still completes — the workflow file is authored and self-verified statically, and its first live run fails closed with `VERSION_OBSERVATION_TRANSPORT_UNRESOLVED`, which is the correct behaviour. Do **not** substitute `runs-on: self-hosted`, a guessed label, or a public `/version` URL to make a live run pass: §41.2 (L3728) declares the estate posture `private-authenticated`, and choosing the transport is DECISION REQUIRED **D-L2-09**. File the blocker with STOP RULE `S1`, TASK `L2-T511`. If the canary sweep ever exits `0`, STOP under STOP RULE `S4` and quote §53.1 L4680 — the instrument has stopped comparing, and no live result from that run may be believed.

---

### L2-T512 — Implement the P0 escalation path

**Size:** M  **Depends on:** `L2-T511`

**Creates:**
- `tools/evidence/escalate-digest-mismatch.sh`
- `tools/evidence/lib/build-drift-event.py`

**Edits:** `.github/workflows/verify-digest-chain.yml` (adds the escalation job at its own anchor)

§41.2 (L3729): *"any mismatch is a P0 investigation."* This task builds the mechanism that starts one. Three things it does, and three it must not:

**Does.**
1. Blocks the deployment path — already done by `L2-T511`'s final step and by `L2-T513`. §53.2 Level 4 (L4697): Blocking-class drift means *"Fail CI or block the deployment path until resolved."*
2. Writes the **drift event** through the same records write interface as `L2-T509`. §92.11 (L8276) puts *"Blocking-class drift"* on the closed push list and states: *"Every push event exists in the Section 97 event taxonomy — an event absent from the taxonomy cannot page anyone."* Writing the event **is** the paging mechanism; the routing is subsystem R's.
3. Carries the classification the spec already assigns — `drift_class: Blocking`, `reconciliation_level: 4` — which `L2-T506` already writes into every finding.

**Does not.**
1. **Does not choose a severity.** The incident record's `severity` field takes values like `SEV-2` (§97.2 example, L8880) and the incident record shape is L4's (PARTITION.md line 20). Nothing in the spec maps digest mismatch onto a SEV value.
2. **Does not write an incident record.** §97.2 (L8846) names the writer of `records/incidents/`: *"Incident workflow, from the incident issue template"*. That is not this workflow.
3. **Does not name a messaging channel.** §92.11 (L8274): the destination is *"a configuration value, never a hard-coded destination"*, and notification routing is subsystem R (L5).

Runtime contract, fixed:

```
escalate-digest-mismatch.sh --findings <live-findings.json> \
    --event-types <types.yaml> --event-id <EVT-...> --actor <id> \
    --run-url <url> --out-dir <dir>
exit 0 → no findings; prints "EVIDENCE-OK NO_ESCALATION"
exit 3 → findings present; writes <out-dir>/drift-event.yaml and
         prints "EVIDENCE-FAIL P0_ESCALATION_REQUIRED findings=<N>"
exit 2 → input error
```

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/lib/build-drift-event.py <<'EOF'
#!/usr/bin/env python3
"""Build the Blocking-class drift event for a digest-chain mismatch.

Spec: Section 92.11 line 8276 - "Blocking-class drift" is on the closed push
list, and "Every push event exists in the Section 97 event taxonomy - an event
absent from the taxonomy cannot page anyone." Section 97.3 lines 8931-8944 -
the binding event envelope. Section 53.2 line 4697 - Level 4, Block.
Section 41.2 line 3729 - "any mismatch is a P0 investigation".

This module chooses NO severity and writes NO incident record: the incident
record store is written by the incident workflow (Section 97.2 line 8846) and
its shape is Lane 4's.
"""
import argparse, json, os, sys

try:
    import yaml
except ImportError:
    print("EVIDENCE-FAIL MISSING_TOOL: python3 yaml module not installed", file=sys.stderr)
    sys.exit(2)


def die(token, text):
    print("EVIDENCE-FAIL %s: %s" % (token, text), file=sys.stderr)
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser()
    for flag in ("--findings", "--event-types", "--event-id", "--actor",
                 "--run-url", "--now", "--out-dir"):
        ap.add_argument(flag, required=True)
    a = ap.parse_args()

    if not os.path.isfile(a.findings):
        die("FINDINGS_ABSENT", a.findings)
    result = json.load(open(a.findings, encoding="utf-8"))
    findings = result.get("findings") or []
    if not findings:
        print("EVIDENCE-OK NO_ESCALATION")
        return 0

    types = (yaml.safe_load(open(a.event_types, encoding="utf-8")) or {}).get("map") or {}
    event_type = types.get("drift_detected")
    if not event_type:
        die("EVENT_TYPE_UNRESOLVED",
            "no identifier under map.drift_detected in %s "
            "(DECISION REQUIRED D-L2-08)" % a.event_types)

    products = sorted({f.get("product") for f in findings if f.get("product")})
    event = {
        "event_schema_version": 1,
        "event_id": a.event_id,
        "event_type": event_type,
        "occurred_at": a.now,
        "recorded_at": a.now,
        "actor": a.actor,
        "product": products[0] if len(products) == 1 else "estate",
        "subject_ref": a.run_url,
        "payload": {
            # Section 53.4 line 4715: this is the only severity vocabulary that
            # exists anywhere in this system. No SEV value is chosen here.
            "drift_class": "Blocking",
            "reconciliation_level": 4,
            "detector": "verify-digest-chain",
            "spec": "Section 32 line 2823; Section 41.2 line 3729; "
                    "Section 53.2 line 4697",
            "push_list_entry": "Blocking-class drift (Section 92.11 line 8276)",
            "products_affected": products,
            "findings_count": len(findings),
            "findings": findings,
        },
    }
    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "drift-event.yaml"), "w", encoding="utf-8") as fh:
        yaml.safe_dump(event, fh, default_flow_style=False, sort_keys=True)
    print("EVIDENCE-FAIL P0_ESCALATION_REQUIRED findings=%d" % len(findings))
    return 3


if __name__ == "__main__":
    sys.exit(main())
EOF

cat > tools/evidence/escalate-digest-mismatch.sh <<'EOF'
#!/usr/bin/env bash
# escalate-digest-mismatch.sh - turn sweep findings into the Blocking-drift
# event that Section 92.11 (line 8276) requires before anything may page anyone.
#
# Spec: Section 41.2 line 3729 ("any mismatch is a P0 investigation");
# Section 53.2 line 4697 (Level 4, Block); Section 92.11 line 8276 (the closed
# push list); Section 97.3 lines 8931-8944 (the event envelope).
#
# Chooses no severity. Writes no incident record. Names no channel.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/lib/common.sh"
ev_require_cmd python3

FINDINGS=""; TYPES=""; EVENT_ID=""; ACTOR=""; RUN_URL=""; OUT_DIR=""
while [ $# -gt 0 ]; do
  case "$1" in
    --findings)    FINDINGS="${2:-}"; shift 2 ;;
    --event-types) TYPES="${2:-}";    shift 2 ;;
    --event-id)    EVENT_ID="${2:-}"; shift 2 ;;
    --actor)       ACTOR="${2:-}";    shift 2 ;;
    --run-url)     RUN_URL="${2:-}";  shift 2 ;;
    --out-dir)     OUT_DIR="${2:-}";  shift 2 ;;
    *) ev_die "BAD_ARG" "unknown argument: $1" ;;
  esac
done
for pair in FINDINGS:--findings TYPES:--event-types EVENT_ID:--event-id \
            ACTOR:--actor RUN_URL:--run-url OUT_DIR:--out-dir; do
  var="${pair%%:*}"; flag="${pair##*:}"
  [ -n "${!var}" ] || ev_die "BAD_ARG" "$flag is required"
done
ev_require_file "$FINDINGS" "FINDINGS_ABSENT"
ev_require_file "$TYPES" "EVENT_TYPES_ABSENT"
printf '%s' "$EVENT_ID" | grep -qE '^EVT-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}$' \
  || ev_die "ID_MALFORMED" "event id must match EVT-YYYY-MM-DD-NNNNNN: $EVENT_ID"

python3 "$HERE/lib/build-drift-event.py" \
  --findings "$FINDINGS" --event-types "$TYPES" --event-id "$EVENT_ID" \
  --actor "$ACTOR" --run-url "$RUN_URL" --now "$(ev_now_utc)" --out-dir "$OUT_DIR"
EOF
chmod +x tools/evidence/escalate-digest-mismatch.sh
python3 -m py_compile tools/evidence/lib/build-drift-event.py
bash -n tools/evidence/escalate-digest-mismatch.sh
git add tools/evidence/escalate-digest-mismatch.sh tools/evidence/lib/build-drift-event.py
git commit -m "L2-T512: P0 escalation path - the Blocking-class drift event for a digest mismatch"
```

Then add the escalation job to the sweep workflow. Apply exactly this edit — it appends a second job, and refuses if the first job is not present:

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python3 - <<'PYEOF'
import io, sys
p = ".github/workflows/verify-digest-chain.yml"
src = io.open(p, encoding="utf-8").read()
if "  escalate:" in src:
    print("ALREADY_WIRED")
    sys.exit(0)
if "  sweep:" not in src:
    print("EVIDENCE-FAIL SWEEP_JOB_ABSENT: L2-T511 did not run")
    sys.exit(1)
block = '''
  escalate:
    name: escalate-digest-mismatch
    needs: sweep
    if: ${{ always() && needs.sweep.outputs.findings_count != '0' }}
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Check out the control plane
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683

      - name: Download the findings file
        uses: actions/download-artifact@fa0a91b85d4f404e444e00e005971372dc801d16
        with:
          name: digest-chain-findings

      - name: Build and write the Blocking-class drift event
        env:
          RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
        run: |
          set -euo pipefail
          python3 -c 'import yaml' 2>/dev/null || pip3 install --quiet 'pyyaml==6.0.2'
          IFACE=contracts/records/write-interface.yaml
          TYPES=contracts/events/event-types.yaml
          test -f "$IFACE" || { echo "RECORD_WRITE_INTERFACE_ABSENT"; exit 1; }
          test -f "$TYPES" || { echo "EVENT_TYPE_ENUM_ABSENT"; exit 1; }
          ALLOC="$(python3 -c "import yaml;print((yaml.safe_load(open('$IFACE',encoding='utf-8')) or {}).get('event_id_allocator',''))")"
          WRITER="$(python3 -c "import yaml;print((yaml.safe_load(open('$IFACE',encoding='utf-8')) or {}).get('writer_entrypoint',''))")"
          test -n "${ALLOC}" && test -n "${WRITER}" \\
            || { echo "RECORD_WRITE_INTERFACE_INCOMPLETE"; exit 1; }
          EVENT_ID="$(${ALLOC} --product estate)"
          test -n "${EVENT_ID}" || { echo "EVENT_ID_UNALLOCATED"; exit 1; }
          set +e
          ./tools/evidence/escalate-digest-mismatch.sh \\
            --findings live-findings.json --event-types "$TYPES" \\
            --event-id "${EVENT_ID}" --actor "${GITHUB_ACTOR}" \\
            --run-url "${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}" \\
            --out-dir ./.escalation
          RC=$?
          set -e
          if [ "${RC}" = "0" ]; then echo "NO_ESCALATION"; exit 0; fi
          if [ "${RC}" != "3" ]; then echo "ESCALATION_BUILD_FAILED rc=${RC}"; exit 1; fi
          ${WRITER} --kind event --product estate --id "${EVENT_ID}" \\
            --payload ./.escalation/drift-event.yaml --create-only \\
            || { echo "DRIFT_EVENT_WRITE_FAILED"; exit 1; }
          echo "P0_ESCALATION_RECORDED ${EVENT_ID}"
          # Section 53.2 Level 4: the deployment path stays blocked until resolved.
          exit 1
'''
io.open(p, "w", encoding="utf-8").write(src.rstrip("\n") + "\n" + block)
print("ESCALATION_JOB_ADDED")
PYEOF
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/verify-digest-chain.yml'))" \
  || { echo "YAML PARSE FAILED — git checkout -- .github/workflows/verify-digest-chain.yml and STOP"; exit 1; }
git add .github/workflows/verify-digest-chain.yml
git commit -m "L2-T512: wire the escalation job into the digest-chain sweep"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Both files compile | `bash -n tools/evidence/escalate-digest-mismatch.sh && python3 -m py_compile tools/evidence/lib/build-drift-event.py; echo $?` | exactly `0` |
| A2 | A clean findings file escalates nothing | see SELF-VERIFY | exactly `EVIDENCE-OK NO_ESCALATION`, exit `0` |
| A3 | A findings file with a mismatch escalates | see SELF-VERIFY | `EVIDENCE-FAIL P0_ESCALATION_REQUIRED findings=1`, exit `3` |
| A4 | The event carries all nine §97.3 envelope fields | see SELF-VERIFY | exactly `9` |
| A5 | The event carries `drift_class: Blocking` and level 4, and no SEV value | `grep -c 'Blocking' /tmp/ev512/out/drift-event.yaml; grep -c 'SEV-' /tmp/ev512/out/drift-event.yaml` | `1` or more, then exactly `0` |
| A6 | The escalation names no channel and no incident store | `grep -cE 'slack|teams|webhook|records/incidents' tools/evidence/escalate-digest-mismatch.sh tools/evidence/lib/build-drift-event.py \| paste -sd+ - \| bc` | exactly `0` |
| A7 | The workflow now has exactly two jobs | `python3 -c "import yaml;print(sorted(yaml.safe_load(open('.github/workflows/verify-digest-chain.yml'))['jobs'].keys()))"` | exactly `['escalate', 'sweep']` |
| A8 | The escalation job leaves the run failed (§53.2 Level 4) | `grep -c 'P0_ESCALATION_RECORDED' .github/workflows/verify-digest-chain.yml` | exactly `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
E=tools/evidence/escalate-digest-mismatch.sh; F=tools/evidence/fixtures; V=tools/evidence/verify-digest-chain
mkdir -p /tmp/ev512/out
"$V" --records $F/closed --observations $F/closed/observations.jsonl \
     --findings-out /tmp/ev512/clean.json >/dev/null 2>&1 || true
"$V" --records $F/broken-digest-mismatch --observations $F/broken-digest-mismatch/observations.jsonl \
     --findings-out /tmp/ev512/dirty.json >/dev/null 2>&1 || true
R1=$("$E" --findings /tmp/ev512/clean.json --event-types $F/event-types.fixture.yaml \
          --event-id EVT-2026-01-05-000010 --actor fixture-bot \
          --run-url https://example.invalid/runs/2 --out-dir /tmp/ev512/out); RC1=$?
R2=$("$E" --findings /tmp/ev512/dirty.json --event-types $F/event-types.fixture.yaml \
          --event-id EVT-2026-01-05-000011 --actor fixture-bot \
          --run-url https://example.invalid/runs/3 --out-dir /tmp/ev512/out); RC2=$?
ENV_FIELDS=$(python3 -c "import yaml;d=yaml.safe_load(open('/tmp/ev512/out/drift-event.yaml'));print(len([k for k in ('event_schema_version','event_id','event_type','occurred_at','recorded_at','actor','product','subject_ref','payload') if k in d]))")
test "$R1" = "EVIDENCE-OK NO_ESCALATION" && test "$RC1" = "0" \
 && test "$R2" = "EVIDENCE-FAIL P0_ESCALATION_REQUIRED findings=1" && test "$RC2" = "3" \
 && test "$ENV_FIELDS" = "9" \
 && test "$(grep -c 'SEV-' /tmp/ev512/out/drift-event.yaml)" = "0" \
 && grep -q 'Blocking' /tmp/ev512/out/drift-event.yaml \
 && test "$(grep -chE 'slack|teams|webhook|records/incidents' "$E" tools/evidence/lib/build-drift-event.py | paste -sd+ - | bc)" = "0" \
 && test "$(python3 -c "import yaml;print(sorted(yaml.safe_load(open('.github/workflows/verify-digest-chain.yml'))['jobs'].keys()))")" = "['escalate', 'sweep']" \
 && test "$(grep -c 'P0_ESCALATION_RECORDED' .github/workflows/verify-digest-chain.yml)" = "1" \
 && echo "L2-T512 OK" || echo "L2-T512 FAIL"
```
Correct output: the single line `L2-T512 OK`.

**STOP rule:** if completing this task appears to require choosing a `SEV-` value, writing into `records/incidents/`, or naming a messaging destination, STOP. All three are foreign acts: the incident record shape and store are L4's (PARTITION.md line 20), the incident workflow is its named writer (§97.2 L8846), and the destination is a configuration value owned by subsystem R (§92.11 L8274). File the blocker with STOP RULE `S2`, TASK `L2-T512`. If `contracts/events/event-types.yaml` declares no `drift_detected` identifier, STOP under **D-L2-08** — §97.3 (L8948) has control-plane CI reject an unenumerated `event_type`, so a guess makes every escalation fail at write time, which is the one moment it must not.

---

### L2-T513 — Implement `tools/evidence/deploy-gate.sh`

**Size:** M  **Depends on:** `L2-T506`

**Creates:** `tools/evidence/deploy-gate.sh`

Two callers, one script:

1. **Deploy mode** (`--mode deploy`). §53.2 Level 4 (L4697) — Blocking-class drift *"blocks the deployment path until resolved."* Before a production deploy proceeds, the running digest for that product must already reconcile against an approved production record.
2. **Recovery mode** (`--mode recovery`). §46.1 (L4126) — *"Completion of step 3 — the digest-vs-approval verification, executed by the named build-surface script `verify-digest-chain` — **gates resumption of production deploys**: nothing new deploys until the evidence chain is confirmed closed."* Recovery mode sweeps the **whole estate**, not one product, and additionally requires the caller to name the capability it holds.

**Freshness needs no threshold.** The gate runs the sweep itself, in the same invocation, over the observations it is given. There is no "how old may a sweep result be" question to answer, and therefore no number to invent.

**Capabilities are read, never chosen.** §37.3 (L3268) names exactly three: `production-approval`, `incident-response`, `devops`. Recovery mode requires the caller's declared capability to be one that `contracts/product/capabilities.yaml` publishes; the gate refuses an unpublished name rather than defaulting.

Runtime contract, fixed:

```
deploy-gate.sh --mode <deploy|recovery> --records <dir> --observations <file.jsonl> \
               [--product <name>] [--capability <name>] [--capabilities-contract <file>]
exit 0 → the chain is confirmed closed; prints "EVIDENCE-OK DEPLOY_PERMITTED"
         or "EVIDENCE-OK RESUMPTION_PERMITTED"
exit 3 → blocked; prints "EVIDENCE-FAIL DEPLOY_BLOCKED: <reason>"
exit 2 → input error
```

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/deploy-gate.sh <<'EOF'
#!/usr/bin/env bash
# deploy-gate.sh - fails closed while the evidence chain is not confirmed closed.
#
# Spec:
#   Section 53.2 line 4697 - Level 4, Block: "Fail CI or block the deployment
#     path until resolved." Artifact digest mismatch is a Level 4 row.
#   Section 46.1 line 4126 - "Completion of step 3 - the digest-vs-approval
#     verification, executed by the named build-surface script
#     verify-digest-chain - gates resumption of production deploys: nothing new
#     deploys until the evidence chain is confirmed closed."
#   Section 37.3 line 3268 - the three capabilities: production-approval,
#     incident-response, devops. This script READS the capability name from the
#     published contract; it never chooses one and never grants one.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/lib/common.sh"

MODE=""; RECORDS=""; OBSERVATIONS=""; PRODUCT=""; CAPABILITY=""
CAP_CONTRACT="contracts/product/capabilities.yaml"
while [ $# -gt 0 ]; do
  case "$1" in
    --mode)                   MODE="${2:-}";         shift 2 ;;
    --records)                RECORDS="${2:-}";      shift 2 ;;
    --observations)           OBSERVATIONS="${2:-}"; shift 2 ;;
    --product)                PRODUCT="${2:-}";      shift 2 ;;
    --capability)             CAPABILITY="${2:-}";   shift 2 ;;
    --capabilities-contract)  CAP_CONTRACT="${2:-}"; shift 2 ;;
    *) ev_die "BAD_ARG" "unknown argument: $1" ;;
  esac
done
case "$MODE" in
  deploy|recovery) ;;
  *) ev_die "MODE_UNRECOGNISED" "--mode must be deploy or recovery" ;;
esac
[ -n "$RECORDS" ]      || ev_die "BAD_ARG" "--records is required"
[ -n "$OBSERVATIONS" ] || ev_die "BAD_ARG" "--observations is required"
ev_require_file "$OBSERVATIONS" "OBSERVATIONS_ABSENT"

if [ "$MODE" = "deploy" ]; then
  [ -n "$PRODUCT" ] || ev_die "BAD_ARG" "--product is required in deploy mode"
fi

if [ "$MODE" = "recovery" ]; then
  # Section 46.1: the escalation role owns the six recovery steps. The gate
  # refuses to run for a capability the contract does not publish.
  [ -n "$CAPABILITY" ] || ev_die "CAPABILITY_UNDECLARED" \
    "--capability is required in recovery mode (Section 37.3 line 3268)"
  ev_require_file "$CAP_CONTRACT" "CAPABILITIES_CONTRACT_ABSENT"
  grep -qE "(^|[^a-z-])${CAPABILITY}([^a-z-]|$)" "$CAP_CONTRACT" \
    || ev_die "CAPABILITY_UNPUBLISHED" \
       "$CAPABILITY is not published in $CAP_CONTRACT"
  # Recovery sweeps the estate. A per-product sweep would resume deploys on the
  # strength of one product's chain, which Section 46.1 does not permit.
  PRODUCT=""
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
ARGS=(--records "$RECORDS" --observations "$OBSERVATIONS" --findings-out "$TMP/findings.json")
if [ -n "$PRODUCT" ]; then ARGS+=(--product "$PRODUCT"); fi

set +e
"$HERE/verify-digest-chain" "${ARGS[@]}" > "$TMP/sweep.log" 2>&1
RC=$?
set -e
cat "$TMP/sweep.log"

case "$RC" in
  0)
    if [ "$MODE" = "deploy" ]; then ev_ok "DEPLOY_PERMITTED product=$PRODUCT";
    else ev_ok "RESUMPTION_PERMITTED capability=$CAPABILITY"; fi
    exit 0 ;;
  3)
    COUNT="$(python3 -c "import json;print(len(json.load(open('$TMP/findings.json'))['findings']))")"
    printf '%s DEPLOY_BLOCKED: Blocking-class drift, %s finding(s); Section 53.2 Level 4\n' \
      "$EV_FAIL_PREFIX" "$COUNT" >&2
    exit 3 ;;
  *)
    # A broken sweep is not a clean sweep (Section 53.1 line 4680).
    printf '%s DEPLOY_BLOCKED: sweep did not complete (rc=%s)\n' "$EV_FAIL_PREFIX" "$RC" >&2
    exit 3 ;;
esac
EOF
chmod +x tools/evidence/deploy-gate.sh
bash -n tools/evidence/deploy-gate.sh
git add tools/evidence/deploy-gate.sh
git commit -m "L2-T513: deploy-gate.sh - block-on-mismatch and the Section 46.1 recovery gate"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Script parses | `bash -n tools/evidence/deploy-gate.sh; echo $?` | exactly `0` |
| A2 | Clean estate permits the deploy | see SELF-VERIFY | exactly `EVIDENCE-OK DEPLOY_PERMITTED product=fixture-product`, exit `0` |
| A3 | Mismatch blocks the deploy (§53.2 L4697) | see SELF-VERIFY | stderr contains `DEPLOY_BLOCKED`, exit `3` |
| A4 | A broken sweep blocks, never permits (§53.1 L4680) | run with a nonexistent records dir | exit `3`, stderr contains `DEPLOY_BLOCKED` |
| A5 | Recovery mode without `--capability` is refused | see SELF-VERIFY | stderr contains `CAPABILITY_UNDECLARED`, exit `2` |
| A6 | Recovery mode refuses an unpublished capability | see SELF-VERIFY | stderr contains `CAPABILITY_UNPUBLISHED`, exit `2` |
| A7 | Recovery mode with a published capability and a clean estate permits resumption (§46.1 L4126) | see SELF-VERIFY | exactly `EVIDENCE-OK RESUMPTION_PERMITTED capability=incident-response`, exit `0` |
| A8 | The script grants no capability and names no role holder | `grep -cE 'people\.yaml|assignments|grant' tools/evidence/deploy-gate.sh` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
G=tools/evidence/deploy-gate.sh; F=tools/evidence/fixtures; mkdir -p /tmp/ev513
printf 'schema: capabilities/v1\nprovenance: synthetic\ncapabilities:\n  - production-approval\n  - incident-response\n  - devops\n' > /tmp/ev513/caps.yaml
"$G" --mode deploy --records $F/closed --observations $F/closed/observations.jsonl --product fixture-product 2>/dev/null > /tmp/ev513/o1.txt; RC1=$?
R1=$(tail -1 /tmp/ev513/o1.txt)
"$G" --mode deploy --records $F/broken-digest-mismatch --observations $F/broken-digest-mismatch/observations.jsonl --product fixture-product >/tmp/ev513/o2.txt 2>&1; RC2=$?
"$G" --mode deploy --records /tmp/ev513/nonexistent --observations $F/closed/observations.jsonl --product fixture-product >/tmp/ev513/o3.txt 2>&1; RC3=$?
"$G" --mode recovery --records $F/closed --observations $F/closed/observations.jsonl >/tmp/ev513/o4.txt 2>&1; RC4=$?
"$G" --mode recovery --records $F/closed --observations $F/closed/observations.jsonl --capability not-a-capability --capabilities-contract /tmp/ev513/caps.yaml >/tmp/ev513/o5.txt 2>&1; RC5=$?
"$G" --mode recovery --records $F/closed --observations $F/closed/observations.jsonl --capability incident-response --capabilities-contract /tmp/ev513/caps.yaml 2>/dev/null > /tmp/ev513/o6.txt; RC6=$?
R6=$(tail -1 /tmp/ev513/o6.txt)
bash -n "$G" \
 && test "$R1" = "EVIDENCE-OK DEPLOY_PERMITTED product=fixture-product" && test "$RC1" = "0" \
 && test "$RC2" = "3" && grep -q 'DEPLOY_BLOCKED' /tmp/ev513/o2.txt \
 && test "$RC3" = "3" && grep -q 'DEPLOY_BLOCKED' /tmp/ev513/o3.txt \
 && test "$RC4" = "2" && grep -q 'CAPABILITY_UNDECLARED' /tmp/ev513/o4.txt \
 && test "$RC5" = "2" && grep -q 'CAPABILITY_UNPUBLISHED' /tmp/ev513/o5.txt \
 && test "$R6" = "EVIDENCE-OK RESUMPTION_PERMITTED capability=incident-response" && test "$RC6" = "0" \
 && test "$(grep -cE 'people\.yaml|assignments|grant' "$G")" = "0" \
 && echo "L2-T513 OK" || echo "L2-T513 FAIL"
```
Correct output: the single line `L2-T513 OK`.

**STOP rule:** if `contracts/product/capabilities.yaml` is absent in the live control plane, recovery mode fails closed with `CAPABILITIES_CONTRACT_ABSENT` — that is correct behaviour, not a task failure. Do **not** hard-code the three capability names as a fallback list: §37.3 (L3268) names them, but the published set is L1's registry surface (PARTITION.md line 17) and a lane-local copy silently diverges on the first change. If a live gate must be run before that contract exists, STOP under STOP RULE `S1`, TASK `L2-T513`, and cite §37.3 L3261–3268. Do **not** add a "sweep result younger than N hours" allowance — the gate sweeps in-line precisely so no such number has to be chosen.

---

### L2-T514 — Author `.github/workflows/evidence-selftest.yml`

**Size:** M  **Depends on:** `L2-T504`, `L2-T506`, `L2-T513`

**Creates:**
- `.github/workflows/evidence-selftest.yml`
- `tools/evidence/selftest.sh`

§95.4's philosophy, stated in this lane's own terms by `L2-T503`: a check that has never been shown to fail is not a check. This task turns the whole fixture estate into one command and one workflow, so that a pull request weakening any part of subsystem F fails visibly.

It is also the task that files the **D-L2-07** blocker. `L2-T504`'s STOP rule defers it here: the engine is built and proven against the lane fixture map, and the blocker is filed for the *real* map only when the selftest is in place to consume it.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/selftest.sh <<'EOF'
#!/usr/bin/env bash
# The subsystem-F negative-test suite. Section 95.4: a check that has never been
# shown to fail is not a check.
#
# Every case below asserts an EXIT CODE, not a log line, so a reworded message
# never silently turns a failing case into a passing one.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
F="$HERE/fixtures"
M="$F/map.fixture.yaml"
D="sha256:aaaa000000000000000000000000000000000000000000000000000000000001"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PASS=0; FAIL=0

check() {   # check <name> <expected-rc> <command...>
  local name="$1" want="$2"; shift 2
  "$@" > "$WORK/out.txt" 2>&1
  local got=$?
  if [ "$got" = "$want" ]; then
    printf 'PASS %-42s rc=%s\n' "$name" "$got"; PASS=$((PASS+1))
  else
    printf 'FAIL %-42s want=%s got=%s\n' "$name" "$want" "$got"; sed 's/^/     | /' "$WORK/out.txt"; FAIL=$((FAIL+1))
  fi
}

# --- the eleven-question assembler (Section 32) ------------------------------
check "query/closed-chain-closes"        0 "$HERE/evidence-query" --map "$M" \
  --records "$F/closed" --observations "$F/closed/observations.jsonl" \
  --platform "$F/closed/platform.yaml" --product fixture-product --digest "$D"
check "query/missing-approval-opens"     1 "$HERE/evidence-query" --map "$M" \
  --records "$F/broken-missing-approval" --observations "$F/closed/observations.jsonl" \
  --platform "$F/closed/platform.yaml" --product fixture-product --digest "$D"
check "query/digest-mismatch-opens"      1 "$HERE/evidence-query" --map "$M" \
  --records "$F/broken-digest-mismatch" --observations "$F/broken-digest-mismatch/observations.jsonl" \
  --platform "$F/closed/platform.yaml" --product fixture-product --digest "$D"

# --- the sweep (Section 99.2 line 9215) --------------------------------------
check "sweep/clean-estate"               0 "$HERE/verify-digest-chain" \
  --records "$F/closed" --observations "$F/closed/observations.jsonl" \
  --findings-out "$WORK/f1.json"
check "sweep/digest-mismatch-blocks"     3 "$HERE/verify-digest-chain" \
  --records "$F/broken-digest-mismatch" --observations "$F/broken-digest-mismatch/observations.jsonl" \
  --findings-out "$WORK/f2.json"
check "sweep/self-approved-blocks"       3 "$HERE/verify-digest-chain" \
  --records "$F/broken-self-approved" --observations "$F/closed/observations.jsonl" \
  --findings-out "$WORK/f3.json"
check "sweep/missing-approval-blocks"    3 "$HERE/verify-digest-chain" \
  --records "$F/broken-missing-approval" --observations "$F/closed/observations.jsonl" \
  --findings-out "$WORK/f4.json"
: > "$WORK/empty.jsonl"
check "sweep/zero-observations-is-error" 2 "$HERE/verify-digest-chain" \
  --records "$F/closed" --observations "$WORK/empty.jsonl" --findings-out "$WORK/f5.json"

# --- the seeded canary (Section 53.1 line 4680) ------------------------------
check "canary/must-be-found"             3 "$HERE/verify-digest-chain" \
  --records "$HERE/canary/records" --observations "$HERE/canary/observations.jsonl" \
  --findings-out "$WORK/f6.json"

# --- the collector (Section 41.2) --------------------------------------------
check "collect/strict-flags-unobserved"  4 env EV_FETCH="$F/stub-fetch.sh" \
  "$HERE/collect-version.sh" --targets "$F/targets.fixture.yaml" \
  --out "$WORK/obs.jsonl" --strict
check "collect/no-digest-field-refused"  2 env EV_FETCH="$F/stub-fetch.sh" \
  "$HERE/collect-version.sh" --targets "$F/targets-no-field.fixture.yaml" \
  --out "$WORK/obs2.jsonl"

# --- the gate (Section 46.1 line 4126; Section 53.2 line 4697) ---------------
check "gate/clean-permits"               0 "$HERE/deploy-gate.sh" --mode deploy \
  --records "$F/closed" --observations "$F/closed/observations.jsonl" --product fixture-product
check "gate/mismatch-blocks"             3 "$HERE/deploy-gate.sh" --mode deploy \
  --records "$F/broken-digest-mismatch" --observations "$F/broken-digest-mismatch/observations.jsonl" \
  --product fixture-product
check "gate/broken-sweep-blocks"         3 "$HERE/deploy-gate.sh" --mode deploy \
  --records "$WORK/does-not-exist" --observations "$F/closed/observations.jsonl" \
  --product fixture-product

# --- the escalation (Section 92.11 line 8276) --------------------------------
check "escalate/clean-does-nothing"      0 "$HERE/escalate-digest-mismatch.sh" \
  --findings "$WORK/f1.json" --event-types "$F/event-types.fixture.yaml" \
  --event-id EVT-2026-01-05-000020 --actor selftest \
  --run-url https://example.invalid/runs/selftest --out-dir "$WORK/esc"
check "escalate/mismatch-escalates"      3 "$HERE/escalate-digest-mismatch.sh" \
  --findings "$WORK/f2.json" --event-types "$F/event-types.fixture.yaml" \
  --event-id EVT-2026-01-05-000021 --actor selftest \
  --run-url https://example.invalid/runs/selftest --out-dir "$WORK/esc"

printf 'SELFTEST pass=%d fail=%d\n' "$PASS" "$FAIL"
if [ "$FAIL" != "0" ]; then echo "SELFTEST_FAIL"; exit 1; fi
if [ "$PASS" != "16" ]; then echo "SELFTEST_CASE_COUNT_CHANGED pass=$PASS"; exit 1; fi
echo "SELFTEST_PASS"
EOF
chmod +x tools/evidence/selftest.sh

cat > .github/workflows/evidence-selftest.yml <<'EOF'
name: evidence-selftest
# =====================================================================
# THE SUBSYSTEM-F NEGATIVE-TEST SUITE
# Spec: Section 95.4 - a check never shown to fail is not a check.
# Section 53.1 line 4680 - the seeded canary must be found on every run.
# This workflow proves that the evidence chain still refuses. It is the
# mechanical guard on charter DoD-13 and DoD-14.
# Adding this context to branch protection is Lane 5's act, not Lane 2's
# (charter section 4.4); this workflow only emits it.
# =====================================================================
on:
  pull_request:
  push:
    branches: [integration, main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  evidence-selftest:
    name: evidence-selftest
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Check out the control plane
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683

      - name: Install PyYAML
        run: |
          set -euo pipefail
          python3 -c 'import yaml' 2>/dev/null || pip3 install --quiet 'pyyaml==6.0.2'
          echo "PYYAML_READY"

      - name: Run the fixture suite
        run: |
          set -euo pipefail
          ./tools/evidence/selftest.sh | tee selftest.log
          tail -1 selftest.log | grep -qx 'SELFTEST_PASS' \
            || { echo "SELFTEST_DID_NOT_PASS"; exit 1; }

      - name: Assert no foreign path is referenced from tools/evidence
        run: |
          set -euo pipefail
          # PARTITION.md rule 4. tools/evidence/ reaches other lanes only
          # through contracts/.
          HITS="$(grep -rlE 'schemas/records/|registries/|metrics/|reconciler/|access/' \
                    tools/evidence/ | wc -l | tr -d ' ')"
          test "${HITS}" = "0" || { echo "FOREIGN_PATH_REFERENCED count=${HITS}"; exit 1; }
          echo "NO_FOREIGN_PATH"

      - name: Report whether the real eleven-question map is available yet
        run: |
          set -euo pipefail
          # The suite above runs against the lane fixture map. The real map is
          # DECISION REQUIRED D-L2-07 and is L0's to publish.
          if [ -f contracts/evidence/eleven-question-map.yaml ]; then
            echo "ELEVEN_QUESTION_MAP_PRESENT"
          else
            echo "ELEVEN_QUESTION_MAP_PENDING_D-L2-07"
          fi
EOF
python3 -c "import yaml;yaml.safe_load(open('.github/workflows/evidence-selftest.yml'))" \
  || { echo "YAML PARSE FAILED — STOP"; exit 1; }
bash tools/evidence/selftest.sh
git add tools/evidence/selftest.sh .github/workflows/evidence-selftest.yml
git commit -m "L2-T514: evidence-selftest - the subsystem-F negative-test suite"
```

If `contracts/evidence/eleven-question-map.yaml` is absent, file the D-L2-07 blocker now — this is the task that owes it:

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
if [ ! -f contracts/evidence/eleven-question-map.yaml ]; then
gh issue create \
  --title "BLOCKER L2-T514: contracts/evidence/eleven-question-map.yaml absent" \
  --label "blocker,lane-2" \
  --body "$(cat <<'EOF'
LANE: L2 Pipeline & Evidence
TASK: L2-T514
STOP RULE TRIGGERED: S1

WHAT I WAS DOING:
test -f contracts/evidence/eleven-question-map.yaml

WHAT HAPPENED:
The file does not exist. The subsystem-F engine is complete and green against
tools/evidence/fixtures/map.fixture.yaml, a lane-owned fixture of identical
shape. It cannot be pointed at the live records store without the real map.

WHAT I NEED TO PROCEED:
contracts/evidence/eleven-question-map.yaml, one entry per Section 32 question
1-11, each carrying `store`, and either `record_field` (naming the field on
Lane 4's deployment or UAT record schema) or `source: github-api` with the API
path, plus `required: true|false`. Question 9 must additionally carry
`filter_field` naming the environment discriminator. This is DECISION REQUIRED
D-L2-07 in lanes/L2-04-evidence-chain.md section 4.

SPEC CITATION:
MultiProduct_MasterSpec_v4.0.md lines 2803-2828, Section 32
MultiProduct_MasterSpec_v4.0.md lines 8843-8926, Section 97.2

I HAVE NOT: guessed a value, written outside owned paths, edited contracts/**,
            resolved a foreign-path conflict, or continued past this point.
EOF
)"
else
  echo "ELEVEN_QUESTION_MAP_PRESENT — no blocker needed"
fi
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Valid YAML | `python3 -c "import yaml;yaml.safe_load(open('.github/workflows/evidence-selftest.yml'))"; echo $?` | exactly `0` |
| A2 | The suite passes | `bash tools/evidence/selftest.sh \| tail -1` | exactly `SELFTEST_PASS` |
| A3 | The suite has sixteen cases, all asserted on exit code | `bash tools/evidence/selftest.sh \| grep -c '^PASS '` | exactly `16` |
| A4 | Removing a negative case is detected | temporarily delete one `check` line and re-run | last line exactly `SELFTEST_CASE_COUNT_CHANGED pass=15`; restore the line |
| A5 | A weakened sweep fails the suite | temporarily edit `verify-digest-chain` to `return 0` on findings and re-run | contains `FAIL sweep/digest-mismatch-blocks`; `git checkout -- tools/evidence/verify-digest-chain` afterwards |
| A6 | The foreign-path assertion is present | `grep -c 'FOREIGN_PATH_REFERENCED' .github/workflows/evidence-selftest.yml` | exactly `1` |
| A7 | No `if:` and no path filter on the job (charter DoD-06) | `grep -cE '^\s*(if:|paths:|paths-ignore:)' .github/workflows/evidence-selftest.yml` | exactly `0` |
| A8 | The Action is SHA-pinned (§48.1) | `grep -oE 'uses: [^ ]+' .github/workflows/evidence-selftest.yml \| grep -cE '@[0-9a-f]{40}$'` | exactly `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
W=.github/workflows/evidence-selftest.yml
python3 -c "import yaml;yaml.safe_load(open('$W'))" \
 && test "$(bash tools/evidence/selftest.sh | tail -1)" = "SELFTEST_PASS" \
 && test "$(bash tools/evidence/selftest.sh | grep -c '^PASS ')" = "16" \
 && test "$(grep -c 'FOREIGN_PATH_REFERENCED' "$W")" = "1" \
 && test "$(grep -cE '^\s*(if:|paths:|paths-ignore:)' "$W")" = "0" \
 && test "$(grep -oE 'uses: [^ ]+' "$W" | grep -cE '@[0-9a-f]{40}$')" = "1" \
 && test "$(grep -rlE 'schemas/records/|registries/|metrics/|reconciler/|access/' tools/evidence/ | wc -l | tr -d ' ')" = "0" \
 && echo "L2-T514 OK" || echo "L2-T514 FAIL"
```
Correct output: the single line `L2-T514 OK`.

**STOP rule:** if a case fails, fix the tool, never the case. Relaxing an expected exit code to make the suite green is the exact failure §95.4 describes and §53.1 (L4680) forbids in the instrument itself. If a case cannot be made to pass, STOP under STOP RULE `S4`, TASK `L2-T514`, and quote the failing line of `selftest.sh` verbatim. Do **not** add `evidence-selftest` to `templates/workflows/required-checks.yaml` — that registry is frozen by `L2-T003` and its STOP rule forbids Lane 2 adding a context name; requiring this check is a request to L0 and L5, filed the same way as D-L2-08 in `L2-02-digest-invariant.md`.

---

### L2-T515 — Append-only and effective-dating assertion

**Size:** S  **Depends on:** `L2-T506`

**Creates:**
- `tools/evidence/assert-append-only.sh`
- `tools/evidence/fixtures/diff-append-only.txt`
- `tools/evidence/fixtures/diff-in-place-edit.txt`

This is deliverable **F-c** of §99.2 row F (L9193): *"append-only history with effective dating."*

Two spec rules, both mechanical:

1. **Never overwritten destructively** (§63.1, L5409): *"state transitions with `start_date` and `end_date` — effective-dating, never in-place mutation — plus git history in the control-plane repository as the durable record."* §97.2 restates it for records: *"never edits in place (corrections are follow-up records)"* (L8888). §97.6 (L8990) confirms the scope: *"Append-only permanence applies to state, decisions, approvals and canonical records."*
2. **One file per event, never a shared append** (§97.3, L8929; PARTITION.md rule 3).

The assertion is over a `git diff --name-status` listing, so it runs identically in CI on a pull request and locally on a range. A record path that appears with status `M`, `D` or `R` fails.

Runtime contract, fixed:

```
assert-append-only.sh --diff <name-status file> --store-prefix <prefix> [--store-prefix <prefix>]...
exit 0 → every touched path under every prefix is status A; prints "EVIDENCE-OK APPEND_ONLY"
exit 5 → an in-place edit, delete or rename; prints one line per offending path
exit 2 → input error
```

Exit code **5**, distinct from every other tool in this phase, so a caller can tell an append-only violation from a digest mismatch.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/assert-append-only.sh <<'EOF'
#!/usr/bin/env bash
# assert-append-only.sh - Section 99.2 row F deliverable F-c, "append-only
# history with effective dating".
#
# Spec:
#   Section 63.1 line 5409 - "state transitions with start_date and end_date -
#     effective-dating, never in-place mutation - plus git history in the
#     control-plane repository as the durable record."
#   Section 97.2 line 8888 - records "never edit in place (corrections are
#     follow-up records)".
#   Section 97.3 line 8929 - one file per event, "never a concurrent append to a
#     shared period file".
#   Section 97.6 line 8990 - the scope of append-only permanence.
#   D107 - the no-bypass ruleset on the records repository is the enforcement;
#     this script is the check that runs before the ruleset ever has to.
#
# Store prefixes are PASSED IN. This script hard-codes no path under records/
# or events/ - PARTITION.md rule 4.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/lib/common.sh"

DIFF=""
PREFIXES=()
while [ $# -gt 0 ]; do
  case "$1" in
    --diff)         DIFF="${2:-}";        shift 2 ;;
    --store-prefix) PREFIXES+=("${2:-}"); shift 2 ;;
    *) ev_die "BAD_ARG" "unknown argument: $1" ;;
  esac
done
[ -n "$DIFF" ] || ev_die "BAD_ARG" "--diff is required"
[ "${#PREFIXES[@]}" -gt 0 ] || ev_die "BAD_ARG" "at least one --store-prefix is required"
ev_require_file "$DIFF" "DIFF_ABSENT"

VIOLATIONS=0
CHECKED=0
while IFS=$'\t' read -r STATUS PATH1 PATH2; do
  [ -n "${STATUS:-}" ] || continue
  for P in "${PREFIXES[@]}"; do
    case "$PATH1" in
      "$P"*)
        CHECKED=$((CHECKED+1))
        case "$STATUS" in
          A) ;;
          M) printf '%s APPEND_ONLY_VIOLATION: in-place edit of %s\n' "$EV_FAIL_PREFIX" "$PATH1" >&2
             VIOLATIONS=$((VIOLATIONS+1)) ;;
          D) printf '%s APPEND_ONLY_VIOLATION: deletion of %s\n' "$EV_FAIL_PREFIX" "$PATH1" >&2
             VIOLATIONS=$((VIOLATIONS+1)) ;;
          R*) printf '%s APPEND_ONLY_VIOLATION: rename of %s to %s\n' "$EV_FAIL_PREFIX" "$PATH1" "${PATH2:-?}" >&2
             VIOLATIONS=$((VIOLATIONS+1)) ;;
          *) printf '%s APPEND_ONLY_VIOLATION: status %s on %s\n' "$EV_FAIL_PREFIX" "$STATUS" "$PATH1" >&2
             VIOLATIONS=$((VIOLATIONS+1)) ;;
        esac ;;
    esac
  done
done < "$DIFF"

if [ "$VIOLATIONS" -gt 0 ]; then
  printf '%s APPEND_ONLY_FAILED violations=%d\n' "$EV_FAIL_PREFIX" "$VIOLATIONS" >&2
  exit 5
fi
ev_ok "APPEND_ONLY checked=$CHECKED"
EOF
chmod +x tools/evidence/assert-append-only.sh

printf 'A\trecords/deployments/2026-01-05/DEP-2026-01-05-002.yaml\nA\tevents/2026-01-05/EVT-2026-01-05-000002.yaml\nA\tdocs/unrelated.md\n' \
  > tools/evidence/fixtures/diff-append-only.txt
printf 'A\trecords/deployments/2026-01-05/DEP-2026-01-05-003.yaml\nM\trecords/deployments/2026-01-05/DEP-2026-01-05-002.yaml\nD\tevents/2026-01-05/EVT-2026-01-05-000002.yaml\n' \
  > tools/evidence/fixtures/diff-in-place-edit.txt

bash -n tools/evidence/assert-append-only.sh
git add tools/evidence/assert-append-only.sh tools/evidence/fixtures/diff-append-only.txt \
        tools/evidence/fixtures/diff-in-place-edit.txt
git commit -m "L2-T515: append-only and effective-dating assertion (Section 63.1, Section 97.6)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Script parses | `bash -n tools/evidence/assert-append-only.sh; echo $?` | exactly `0` |
| A2 | An append-only diff passes | see SELF-VERIFY | exactly `EVIDENCE-OK APPEND_ONLY checked=2`, exit `0` |
| A3 | An in-place edit fails with exit 5 (§97.2 L8888) | see SELF-VERIFY | stderr contains `in-place edit of records/deployments/`, exit `5` |
| A4 | A deletion fails (§63.1 L5409) | same run as A3 | stderr contains `deletion of events/` |
| A5 | Paths outside every prefix are ignored | A2's `checked=2`, not `checked=3` | exactly `checked=2` |
| A6 | The script hard-codes no store path | `grep -cE '"records/|"events/|= *records/' tools/evidence/assert-append-only.sh` | exactly `0` |
| A7 | Exit 5 is unique to this failure across the phase | `grep -c 'exit 5' tools/evidence/*.sh tools/evidence/verify-digest-chain tools/evidence/evidence-query \| grep -vc ':0$'` | exactly `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
A=tools/evidence/assert-append-only.sh; F=tools/evidence/fixtures; mkdir -p /tmp/ev515
R1=$("$A" --diff $F/diff-append-only.txt --store-prefix records/ --store-prefix events/ 2>/dev/null); RC1=$?
"$A" --diff $F/diff-in-place-edit.txt --store-prefix records/ --store-prefix events/ >/tmp/ev515/o2.txt 2>&1; RC2=$?
bash -n "$A" \
 && test "$R1" = "EVIDENCE-OK APPEND_ONLY checked=2" && test "$RC1" = "0" \
 && test "$RC2" = "5" \
 && grep -q 'in-place edit of records/deployments/' /tmp/ev515/o2.txt \
 && grep -q 'deletion of events/' /tmp/ev515/o2.txt \
 && test "$(grep -cE '"records/|"events/' "$A")" = "0" \
 && echo "L2-T515 OK" || echo "L2-T515 FAIL"
```
Correct output: the single line `L2-T515 OK`.

**STOP rule:** if a real records-repository diff shows an `M` on a record path and the fix appears to be relaxing this check, STOP. §97.2 (L8888) and §63.1 (L5409) both state the rule the same way — a correction is a follow-up record, never an edit — and D107 backs it with the no-bypass ruleset on the records repository. Relaxing the assertion hides a violation that the ruleset will reject anyway. File the blocker with STOP RULE `S4`, TASK `L2-T515`, naming the path and its status letter. Do **not** attempt to add or alter that ruleset: rulesets are L5's (`access/**`, PARTITION.md line 21).

---

### L2-T516 — Phase-4 roll-up, self-verify sweep and lane PR

**Size:** S  **Depends on:** `L2-T500`, `L2-T501`, `L2-T502`, `L2-T503`, `L2-T504`, `L2-T505`, `L2-T506`, `L2-T507`, `L2-T508`, `L2-T509`, `L2-T510`, `L2-T511`, `L2-T512`, `L2-T513`, `L2-T514`, `L2-T515`

**Creates:** `tools/evidence/PHASE4-MANIFEST.md`

This task creates no capability. It proves the phase is whole, proves nothing outside the owned trees was touched, and opens the lane pull request onto `integration`.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/PHASE4-MANIFEST.md <<'EOF'
# Lane 2, phase 4 — subsystem F, the evidence chain

Spec: Section 32 (lines 2803-2828); Section 99.2 row F (line 9193) and the named
tool `verify-digest-chain` (line 9215); Section 97.2 (lines 8843-8926);
Section 97.3 (lines 8927-8953); Section 46.1 (lines 4090-4131).

Section 32 line 2807 fixes the ceiling on this subsystem: the eleven questions
are answered "using only GitHub, GitHub Actions and Grafana. No additional
evidence platform is required." Nothing in this tree introduces a fourth.

| Task | Artifact |
|---|---|
| L2-T500 | tools/evidence/lib/common.sh, tools/evidence/README.md |
| L2-T501 | tools/evidence/PHASE4-CONTRACTS.lock |
| L2-T502 | tools/evidence/eleven-questions.yaml |
| L2-T503 | tools/evidence/fixtures/ — one closed chain, four broken variants |
| L2-T504 | tools/evidence/evidence-query |
| L2-T505 | tools/evidence/profile-substitution.yaml |
| L2-T506 | tools/evidence/verify-digest-chain |
| L2-T507 | tools/evidence/collect-version.sh, lib/emit-observation.py, lib/read-targets.py |
| L2-T508 | tools/evidence/build-deployment-record.sh, lib/build-payloads.py |
| L2-T509 | .github/workflows/emit-deployment-record.yml |
| L2-T510 | the emitter wired into both deploy workflows at their named anchor |
| L2-T511 | .github/workflows/verify-digest-chain.yml, tools/evidence/canary/ |
| L2-T512 | tools/evidence/escalate-digest-mismatch.sh, lib/build-drift-event.py |
| L2-T513 | tools/evidence/deploy-gate.sh |
| L2-T514 | tools/evidence/selftest.sh, .github/workflows/evidence-selftest.yml |
| L2-T515 | tools/evidence/assert-append-only.sh |

Charter Definition of Done rows this phase closes:
  DoD-13  verify-digest-chain exits non-zero on any digest/approval mismatch
          and 0 on a clean estate — both directions, tools/evidence/selftest.sh
  DoD-14  the eleven questions of Section 32 are answerable — evidence-query,
          proven against the fixture estate; live wiring blocked on D-L2-07
  DoD-15  deployment-record and event writes are required, failing steps —
          .github/workflows/emit-deployment-record.yml

Open DECISION REQUIRED at the close of this phase: D-L2-07, D-L2-08, D-L2-09.
Each is filed as a Contract Change Request; none is resolved in this lane.
EOF

MISSING=0
for f in \
  tools/evidence/lib/common.sh \
  tools/evidence/README.md \
  tools/evidence/PHASE4-CONTRACTS.lock \
  tools/evidence/eleven-questions.yaml \
  tools/evidence/fixtures/map.fixture.yaml \
  tools/evidence/evidence-query \
  tools/evidence/profile-substitution.yaml \
  tools/evidence/verify-digest-chain \
  tools/evidence/collect-version.sh \
  tools/evidence/lib/emit-observation.py \
  tools/evidence/lib/read-targets.py \
  tools/evidence/build-deployment-record.sh \
  tools/evidence/lib/build-payloads.py \
  tools/evidence/escalate-digest-mismatch.sh \
  tools/evidence/lib/build-drift-event.py \
  tools/evidence/deploy-gate.sh \
  tools/evidence/assert-append-only.sh \
  tools/evidence/selftest.sh \
  tools/evidence/canary/observations.jsonl \
  tools/evidence/canary/records/production.yaml \
  .github/workflows/emit-deployment-record.yml \
  .github/workflows/verify-digest-chain.yml \
  .github/workflows/evidence-selftest.yml ; do
  test -f "$f" || { echo "MISSING $f"; MISSING=$((MISSING+1)); }
done
echo "MISSING=$MISSING"
test "$MISSING" = "0" || { echo "PHASE 4 INCOMPLETE — STOP"; exit 1; }

git add tools/evidence/PHASE4-MANIFEST.md
git commit -m "L2-T516: phase-4 manifest for subsystem F"
git fetch origin
git rebase origin/integration
gh pr create --base integration --head lane/2/phase4-evidence-chain \
  --title "L2 phase 4: subsystem F — the evidence chain" \
  --body "Implements Section 99.2 row F (line 9193) and the named build-surface tool verify-digest-chain (line 9215). Tasks L2-T500 through L2-T516. Owned paths only: tools/evidence/**, .github/workflows/**. Open decisions handed to L0: D-L2-07, D-L2-08, D-L2-09."
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Every phase-4 artifact exists | the `MISSING` loop above | exactly `MISSING=0` |
| A2 | The fixture suite passes | `bash tools/evidence/selftest.sh \| tail -1` | exactly `SELFTEST_PASS` |
| A3 | Nothing outside the owned trees was touched | `git diff --name-only origin/integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |
| A4 | No foreign path is referenced from `tools/evidence/` | `grep -rlE 'schemas/records/|registries/|metrics/|reconciler/|access/' tools/evidence/ \| wc -l` | exactly `0` |
| A5 | The frozen required-check registry was not edited (`L2-T003` STOP rule) | `git diff --name-only origin/integration...HEAD \| grep -c 'required-checks.yaml'` | exactly `0` |
| A6 | `contracts/**` was not edited (PARTITION rule 2) | `git diff --name-only origin/integration...HEAD \| grep -c '^contracts/'` | exactly `0` |
| A7 | Every workflow this phase authored parses | see SELF-VERIFY | exactly `3` |
| A8 | Every Action used across the three workflows is SHA-pinned (§48.1) | `grep -rhoE 'uses: [^ ]+' .github/workflows/emit-deployment-record.yml .github/workflows/verify-digest-chain.yml .github/workflows/evidence-selftest.yml \| grep -vcE '@[0-9a-f]{40}$'` | exactly `0` |
| A9 | The PR targets `integration` | `gh pr view --json baseRefName --jq .baseRefName` | exactly `integration` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
PARSED=0
for W in emit-deployment-record verify-digest-chain evidence-selftest; do
  python3 -c "import yaml;yaml.safe_load(open('.github/workflows/$W.yml'))" && PARSED=$((PARSED+1))
done
test "$PARSED" = "3" \
 && test "$(bash tools/evidence/selftest.sh | tail -1)" = "SELFTEST_PASS" \
 && test "$(git diff --name-only origin/integration...HEAD | grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)')" = "0" \
 && test "$(grep -rlE 'schemas/records/|registries/|metrics/|reconciler/|access/' tools/evidence/ | wc -l | tr -d ' ')" = "0" \
 && test "$(git diff --name-only origin/integration...HEAD | grep -c 'required-checks.yaml')" = "0" \
 && test "$(git diff --name-only origin/integration...HEAD | grep -c '^contracts/')" = "0" \
 && test "$(grep -rhoE 'uses: [^ ]+' .github/workflows/emit-deployment-record.yml .github/workflows/verify-digest-chain.yml .github/workflows/evidence-selftest.yml | grep -vcE '@[0-9a-f]{40}$')" = "0" \
 && test "$(gh pr view --json baseRefName --jq .baseRefName)" = "integration" \
 && echo "L2-T516 OK" || echo "L2-T516 FAIL"
```
Correct output: `MISSING=0` from the roll-up block, then the single line `L2-T516 OK`.

**STOP rule:** if `git rebase origin/integration` conflicts in any file outside the three owned trees, run `git rebase --abort` and STOP. Do not resolve it — a foreign-path conflict means path ownership was violated (PARTITION.md rule 1). File the blocker with STOP RULE `S3`, TASK `L2-T516`. If A3 reports anything other than `0`, do not amend the diff by deleting the foreign file; STOP under STOP RULE `S2` and name the path in the blocker.

---

## 7. REQUIREMENTS THIS PHASE PLACES ON OTHER LANES

Lane 2 states these; Lane 2 does not implement them (L2-00 charter §4.4). Each is a consequence of an artifact built above, not a wish.

| Requirement | Owner | Spec | Which task needs it |
|---|---|---|---|
| `contracts/evidence/eleven-question-map.yaml` — one entry per §32 question, each with `store` and either `record_field` or `source: github-api`; question 9 additionally with `filter_field` | L0 (D-L2-07) | §32 L2803–2828; §97.2 L8843–8926 | `L2-T504` live wiring, `L2-T509` |
| The `event_type` identifiers for "`/version` digest confirmed" and "drift detected by severity", published under keys `version_digest_confirmed` and `drift_detected` | L0 + L1 (D-L2-08) | §97.3 L8948 | `L2-T508`, `L2-T512` |
| `contracts/evidence/version-observation.yaml` carrying `runner_label`, `credential_secret_name` and `targets_file` | L0 (D-L2-09) | §41.2 L3728–3730 | `L2-T511` |
| A records write interface publishing `writer_entrypoint`, `record_read_entrypoint`, `record_id_allocator` and `event_id_allocator`, and allocating ids in the §97.2 / §97.3 printed formats | L4 (charter D-L2-03) | §97.1 L8836–8842; §97.2 L8896; §97.3 L8933 | `L2-T509`, `L2-T512` |
| The deployment-record schema accepting the field names published in the eleven-question map, including the environment discriminator and the deploy timestamp | L4 | §97.2 L8892–8903 | `L2-T508`, `L2-T509` |
| The `records-writer` credential provisioned to the control-plane repository, `contents: write` scoped to the records repository alone | L5 | §40.1; §97.1 L8841; D89 | `L2-T509` |
| A read-only records credential available to the sweep runner | L5 | §40.1; §97.1 | `L2-T511` |
| The `/version` observation transport: a runner able to reach the private path, and a per-product scrape credential | L5 (`ops-vm/**`, `infra/**`) | §41.2 L3728 | `L2-T511` |
| The no-bypass ruleset on the records repository blocking force-push and delete, so the append-only assertion of `L2-T515` is backed by enforcement and not only by a check | L5 (`access/**`) | D107; §63.1 L5409 | `L2-T515` |
| Branch-protection placement of the `evidence-selftest` context, if L0 rules it required | L0 + L5 | §33.2 L2854–2869 | `L2-T514` |
| The anchor line `# EVIDENCE-CHAIN-ANCHOR: emit-deployment-record` in `deploy-staging.yml` and `deploy-production.yml`, at job indentation | L2 subsystem E | §97.2 L8926 | `L2-T510` |
| The `/version` digest-match metric derived from the events this phase writes, and its 100% target | L4 (`metrics/**`, subsystem I) | §99.2 row F L9193, row I L9200 | consumes `L2-T509`, `L2-T512` |
| The Grafana panel presenting digest-match, provisioned from JSON in git | L5 (subsystem H) | §99.2 row H L9195; §32 L2807 | consumes the L4 metric |
| Routing the Blocking-drift push event to the designated messaging channel | L5 (subsystem R) | §92.11 L8274–8276 | consumes `L2-T512` |
| The incident record for a digest mismatch, written by the incident workflow from the incident issue template | L4 store + the incident workflow | §97.2 L8846; §41.2 L3729 | follows `L2-T512` |

---

## 8. WHAT THIS PHASE DELIBERATELY DOES NOT DO

Naming these prevents scope drift and prevents a collision with a sibling Lane 2 document.

| Not here | Where it belongs | Why |
|---|---|---|
| Any file under `schemas/records/**`, `metrics/**`, `registries/**`, `reconciler/**`, `access/**` | L1, L3, L4, L5 | PARTITION.md rule 1; asserted mechanically by `L2-T514` |
| Choosing a `SEV-` value for a digest mismatch | L4 record shape + the incident workflow | §97.2 L8880; no spec text maps digest mismatch onto a SEV |
| Writing into `records/incidents/` | the incident workflow | §97.2 L8846 names its writer, and it is not this workflow |
| Naming or routing to a messaging channel | L5 subsystem R | §92.11 L8274 — the destination is a configuration value |
| A SIG identifier for digest mismatch | nowhere — none exists | §52.2 L4520–4587 assigns none; section 4 above forbids inventing one |
| The Grafana digest-match panel | L5 subsystem H | §99.2 L9195; L2 publishes, L2 does not present |
| Prometheus scrape configuration for `/version` | L4 subsystem I / L5 `infra/**` | §99.2 L9200; PARTITION.md lines 20–21 |
| Creating `deploy-staging.yml` or `deploy-production.yml` | L2 subsystem E | `L2-T510` edits them at a named anchor only, and STOPs if it is absent |
| The workflow-identity gate (approver ≠ deployer) itself | L2 subsystem E | §27.2 L2567–2576; this phase *reads* its outcome from the record |
| The actor gate as the first step of privileged workflows | L2 subsystem E | §37.3 L3261–3268; `L2-T513` reads capability names, it does not gate on actor |
| Adding any context name to `templates/workflows/required-checks.yaml` | L0 | `L2-T003`'s STOP rule freezes that registry |
| A "sweep result younger than N hours" allowance | nowhere — the gate sweeps in-line | inventing a threshold is STOP RULE `S4` |
| Branch protection, rulesets, environments, secret provisioning | L5 | PARTITION.md line 21 |

---

## 9. SPEC CITATION INDEX FOR THIS FILE

Every rule this document imposes traces to one of these. Nothing else was used, and nothing here was invented.

| Cited as | Where in `MultiProduct_MasterSpec_v4.0.md` | What it fixes here |
|---|---|---|
| §15.7 | Conformance profiles, lines 1587–1606 | the seven profiles and the equivalent evidence substituted for questions 10 and 11 |
| §27.2 | No-self-approval mechanics, lines 2567–2576 | `APPROVER_EQUALS_DEPLOYER` as a sweep finding |
| §32 | Production Evidence Chain, lines 2803–2828 | the eleven questions and their sources; item 5 must equal item 11; the S18 equivalence; "using only GitHub, GitHub Actions and Grafana"; "never from hand-maintained state" |
| §37.3 | Prohibited by architecture, lines 3258–3268 | the three capability names `production-approval`, `incident-response`, `devops` |
| §38.3 | Fixture provenance, line 3468 | every fixture in this phase is synthetic |
| §41.2 | The three required endpoints, lines 3717–3730 | `/version` closes the chain; the digest must equal the approved digest; any mismatch is a P0 investigation; the `private-authenticated` posture that makes the transport a decision |
| §46.1 | Degraded engineering mode, lines 4090–4131 | recovery step 3 executed by `verify-digest-chain` gates resumption of production deploys |
| §48.1 | Pinning and provenance, lines 4300–4308 | every Action in this phase is SHA-pinned |
| §51.2 | Control-plane reliability objectives, line 4457 | "Security-class checks at least hourly" — the sweep cadence |
| §52.2 | The unified signal table, lines 4520–4587 | assigns no SIG to digest mismatch; none is invented |
| §53.1 | Declared versus actual, lines 4653–4689 | the seeded-canary rule; a run reporting zero findings is a FAILED run; the blocking rows are security controls |
| §53.2 | The five reconciliation levels, lines 4690–4699 | Level 4 Block; "artifact digest mismatch" named as Blocking-class drift |
| §53.4 | Drift classes, lines 4704–4715 | "No other severity vocabulary exists anywhere in this system" |
| §63.1 | Immutable history, lines 5403–5413 | effective dating; never in-place mutation; git history as the durable record |
| §92.11 | The notification contract, lines 8272–8280 | Blocking-class drift is on the closed push list; an event absent from the taxonomy cannot page anyone; the destination is a configuration value |
| §95.4 | Negative-test philosophy | a check never shown to fail is not a check — the fixture estate and `selftest.sh` |
| §96.6 | S18, line 8825 | the platform-rebuild identity that stands in for the digest |
| §97.1 | The record convention, lines 8836–8842 | UTC with offset on every timestamp; the records-writer write path |
| §97.2 | Canonical record stores, lines 8843–8926 | the deployment record; "never edits in place"; the record and event writes as required, failing steps; the incident store's named writer |
| §97.3 | The event log, lines 8927–8953 | the binding event envelope; one file per event; `event_type` is a closed enum declared in `platform.yaml` |
| §97.6 | Retention, lines 8988–8990 | the scope of append-only permanence |
| §98.2 | Phase 6, lines 9070–9078 | "the eleven-item evidence chain answerable for one real deployment" |
| §99.2 | Subsystem architecture, lines 9188–9226 | row F's three deliverables; the named tool `verify-digest-chain`; the dependency spine E → F → H/I |
| §101.5 | Invariant 22, line 9484 | "The production artifact is the same digest verified in staging. Never rebuilt." |
| D78 | Appendix A, line 10161 | the S18 recorded-identity equivalence |
| D89 | Appendix A, line 10182 | the records-writer credential scoped to the records repository alone |
| D107 | Appendix A | the no-bypass ruleset backing the append-only assertion |

---

## 10. PHASE-4 EXIT CONDITION

Phase 4 is complete when, on the branch `lane/2/phase4-evidence-chain`, all three of these hold at once and each is proved by one command:

| # | Condition | Command | Correct output |
|---|---|---|---|
| 1 | Every task from `L2-T500` to `L2-T516` has run and its SELF-VERIFY printed `OK` | run the seventeen SELF-VERIFY blocks in task order | seventeen lines, each `L2-T5NN OK` |
| 2 | The negative-test estate still refuses | `bash tools/evidence/selftest.sh \| tail -1` | exactly `SELFTEST_PASS` |
| 3 | Nothing outside `.github/workflows/**`, `templates/workflows/**` and `tools/evidence/**` was touched | `git diff --name-only origin/integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |

Three DECISION REQUIRED items — **D-L2-07**, **D-L2-08** and **D-L2-09** — remain open at the end of this phase by design. Each is filed as a Contract Change Request against L0 using the charter's blocker template (L2-00 §10). None of them blocks the construction of a single artifact above: every tool in `tools/evidence/` is built, tested and green against lane-owned fixtures of identical shape, and each one fails closed with a named token the moment it is pointed at a live estate whose contract is not yet published. That is the intended end state of this phase, and it is the correct one — a subsystem that cannot yet close the chain must say so with an exit code, never by returning a chain that looks closed.
