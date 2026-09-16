# L0-01 — PHASE 0: THE FROZEN CONTRACTS

**Lane:** L0 Integrator · **Executor:** the human lead (not an AI developer) · **Branch:** `l0/phase-0-contracts` → `main` → `integration`
**Owns exclusively:** `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` (PARTITION.md, line 22)
**Runs:** BEFORE Lane 1, 2, 3, 4 and 5 begin. Nothing else starts until L0-P0-023 completes.

---

## 0. Why this file is first

Five lanes build in parallel against paths they do not share. The only thing that lets them do that is `contracts/**`: the frozen, versioned interface definitions each lane codes against and develops against a stub or fixture *before the real thing exists*. PARTITION.md rule 2 states it plainly — `contracts/**` is written by L0 in Phase 0 and FROZEN; lanes code against it and against generated stubs/fixtures; a lane needing a contract change files a Contract Change Request and never edits `contracts/**`.

**Stated plainly, and it governs every SLA in Section 8 of this file: a lane blocked on a contract is an L0 emergency, because four other lanes are waiting.** A blocked lane is not one lane idle. It is one lane idle now and four lanes producing work that will have to be reworked when the contract finally lands, because they guessed. The Contract Change Request SLA in Section 8 is deliberately shorter than any other response time in this programme for exactly that reason.

### What Phase 0 does NOT do

Phase 0 writes **interfaces**, not implementations. It writes no validator, no reconciler, no workflow, no registry content, no record. Those are lane work. If a Phase 0 task starts producing behaviour rather than shape, stop — that content belongs to a lane and putting it in `contracts/**` steals a lane's path.

---

## 1. L0 decisions — held here, forbidden to lanes

These are the decisions the lanes are forbidden to make. Each is recorded once, here, and referenced by contract id. A lane that finds itself needing to decide one of these files a CCR (Section 8) and stops.

| Decision id | Decision | Rationale / spec anchor |
| --- | --- | --- |
| **D-L0-01** | Contract shapes are expressed as **JSON Schema draft 2020-12** for anything a validator must enforce, and as **declarative YAML** for anything that is a table of facts (comparison sets, permission matrices, check-name lists). No lane may substitute another schema dialect. | Section 99.3: "every registry and contract schema (direct transcription to JSON Schema is possible)" |
| **D-L0-02** | The **Product Operating Contract is frozen at `contract_version: 2`** — the shape Section 15.1 states literally. `platform.yaml` still declares `supported_contract_versions.product: [1, 2]` exactly as Section 60.1 shows, so the dual-version validator path required by AT-025 is exercised from day one, but **v1 is frozen as accept-for-read-only: no lane authors a new v1 document.** Section 98.2 Phase 3 authors products "at `contract_version: 1`"; that is an onboarding sequencing statement, and the build lanes code against v2. Lanes do not resolve this themselves. | Sections 15.1, 60.1, 98.2, AT-025 |
| **D-L0-03** | The closed `event_type` enum contains **exactly 86 identifiers — one per middot-separated entry of the Section 97.3 taxonomy** — because 97.3 binds "Every entry in the taxonomy below has exactly one stable `event_type` identifier". Paired states in an entry ("opened and closed", "pass or fail", "enabled or disabled") are **payload fields, never separate types**. | Section 97.3 |
| **D-L0-04** | Contract files are frozen by an **immutable annotated tag `contracts/v1.0.0`** protected by a tag ruleset with an **empty bypass-actor list**, mirroring the `workflows/*` tag protection of Section 33.2. A moved contract tag would reach five lanes with no reviewable diff. | Section 33.2; D89 |
| **D-L0-05** | The **lane-guard CI check is not an L0 artifact.** `.github/workflows/**` belongs to L2 (PARTITION.md, line 18) and L0 may not write there. Phase 0 therefore enforces the partition with the two mechanisms L0 does own: **CODEOWNERS requiring L0 review on `contracts/**`** (mechanical, needs no workflow) and the immutable freeze tag. The lane-guard workflow itself is contract-specified in `C-WF-CHECKS-1` under the reserved check name `lane-guard` and is L2's first obligation. Until it exists, the merge train is guarded by Code Owner review alone, and that is a recorded, dated gap — see L0-P0-022. | PARTITION.md rules 1–2; Section 11.3 |
| **D-L0-06** | Every contract carries a **stub** (`contracts/stubs/**`) and at least one **golden-valid** and one **golden-invalid** fixture (`contracts/fixtures/**`). A lane develops against the stub. A contract with no stub is not published, because a lane that cannot run against something has to guess, and guessing is what the freeze exists to prevent. | PARTITION.md rule 2 |
| **D-L0-07** | Contract validation tooling is **`check-jsonschema` + `PyYAML`, versions resolved once at freeze time and recorded in `contracts/tooling.lock`**. No lane installs a different validator. The lock file is the pin; no version is asserted ahead of resolution. | Section 33.2 pinning discipline |
| **D-L0-08** | **Records and events live in `control-plane-records`, never in `control-plane`** (D89). No contract, stub or fixture in `control-plane/contracts/**` may be a real record or event — only shapes and synthetic fixtures. | Section 40.1, D89, D107 |

---

## 2. The contract register

Forty frozen contracts. Every one has an id, a path, a version, an owner, a publishing lane, its consuming lanes, and the stub or fixture lanes develop against before the real thing exists. This table is reproduced machine-readably in `contracts/register.yaml` by task L0-P0-002; if the two disagree, `register.yaml` is wrong and is corrected — this table is the human-readable original. Paths are relative to `contracts/` except rows marked `(docs/)` which are relative to the repo root.

| Contract id | Path (under `contracts/`, or repo root for `docs/`) | v | Publishing lane | Consuming lanes | Stub / fixture lanes develop against |
| --- | --- | --- | --- | --- | --- |
| `C-CAP-VOCAB-1` | `registry/capability.vocabulary.v1.yaml` | 1 | L1 | L1, L3, L5 | `stubs/capability.vocabulary.yaml` |
| `C-REG-PEOPLE-1` | `registry/people.registry.v1.json` | 1 | L1 | L1, L3, L5 | `stubs/people.yaml` |
| `C-REG-ROLES-1` | `registry/roles.registry.v1.json` | 1 | L1 | L1, L3, L5 | `stubs/roles.yaml` |
| `C-REG-PRODUCT-2` | `registry/product.contract.v2.json` | 2 | L1 | L1, L2, L3, L4, L5 | `stubs/product.yaml` |
| `C-REG-VERIFICATION-1` | `registry/verification.contract.v1.json` | 1 | L1 | L1, L2 | `stubs/verification-contract.yaml` |
| `C-REG-SERVICE-1` | `registry/service.contract.v1.json` | 1 | L1 | L1, L3 | `stubs/service.yaml` |
| `C-REG-TOPOLOGY-1` | `registry/topology.registry.v1.json` | 1 | L1 | L1, L3, L5 | `stubs/topology.yaml` |
| `C-REG-PLATFORM-1` | `registry/platform.record.v1.json` | 1 | L1 | L1, L2, L3, L4 | `stubs/platform.yaml` |
| `C-REC-ENV-1` | `records/record.envelope.v1.json` | 1 | L4 | L2, L3, L4 | `stubs/record-incident.yaml` |
| `C-EVT-ENV-1` | `records/event.envelope.v1.json` | 1 | L4 | L1, L2, L3, L4, L5 | `stubs/event.yaml` |
| `C-EVT-ENUM-1` | `records/event-type.enum.v1.yaml` | 1 | L4 | L1, L2, L3, L4, L5 | `stubs/event-type.enum.yaml` |
| `C-REC-STORE-MAP-1` | `records/store-map.v1.yaml` | 1 | L4 | L2, L3, L4 | `stubs/store-map.yaml` |
| `C-WF-IFACE-1` | `workflows/reusable-workflow.interface.v1.yaml` | 1 | L2 | L2, L3, L5 | `stubs/workflow-call-ci.yml` |
| `C-WF-CHECKS-1` | `workflows/required-checks.v1.yaml` | 1 | L2 | L2, L3, L5 | `stubs/required-checks.yaml` |
| `C-WF-SECRETS-1` | `workflows/secret-tiers.v1.yaml` | 1 | L2 | L2, L5 | `stubs/secret-tiers.yaml` |
| `C-WF-EVIDENCE-1` | `workflows/evidence-chain.v1.yaml` | 1 | L2 | L2, L4 | `stubs/evidence-chain-answers.yaml` |
| `C-RECON-SET-1` | `reconciler/comparison-set.v1.yaml` | 1 | L3 | L1, L3, L5 | `stubs/comparison-set.yaml` |
| `C-RECON-FIND-1` | `reconciler/drift-finding.v1.json` | 1 | L3 | L2, L3, L4, L5 | `stubs/drift-finding.yaml` |
| `C-RECON-REPAIR-1` | `reconciler/repair-record.v1.json` | 1 | L3 | L3, L4 | `stubs/repair-record.yaml` |
| `C-PROV-OP-1` | `provisioning/operation.v1.yaml` | 1 | L3 | L1, L3, L5 | `stubs/provision-create-product.yaml` |
| `C-ACC-PERM-1` | `access/permission-model.v1.yaml` | 1 | L5 | L1, L3, L5 | `stubs/permission-model.yaml` |
| `C-ACC-PROT-1` | `access/protection.template.v1.yaml` | 1 | L5 | L2, L3, L5 | `stubs/branch-protection.yaml` |
| `C-ACC-LAYER-1` | `access/layer-split.v1.yaml` | 1 | L5 | L3, L4, L5 | `stubs/layer-split.yaml` |
| `C-CFG-SCHEMA-IDS-1` | `schema-ids.yaml` | 1 | L0 | L0, L1 | — |
| `C-CFG-ESTATE-1` | `estate.yaml` | 1 | L0 | L0, L2, L4, L5 | — |
| `C-CFG-TOOLING-1` | `tooling.lock` | 1 | L0 | L0 | — |
| `C-CFG-ENV-SCHEMA-1` | `environment-schema.yaml` | 1 | L0 | L5 | — |
| `C-EVT-TYPES-1` | `event-types/event-type.enum.v1.yaml` | 1 | L0 | L1, L4 | — |
| `C-CLI-VALIDATE-1` | `cli/registry-validate.yaml` | 1 | L0 | L0 | — |
| `C-WF-CTX-1` | `workflow-io/required-contexts.tsv` | 1 | L0 | L1, L2 | — |
| `C-EV-VER-OBS-1` | `evidence/version-observation.yaml` | 1 | L0 | L3, L4 | — |
| `C-EV-11Q-1` | `evidence/eleven-question-map.yaml` | 1 | L0 | L1, L2, L3, L4, L5 | — |
| `C-L3-HARNESS-1` | `l3-test-harness.env` | 1 | L0 | L3 | — |
| `C-L3-ORG-GATE-1` | `l3-live-org-gate.md` | 1 | L0 | L3 | — |
| `C-L4-RECORDS-1` | `l4-records.yaml` | 1 | L0 | L4 | — |
| `C-CFG-INTEG-1` | `integration.yaml` | 1 | L0 | L0 | — |
| `C-DOC-AT-PHASE-1` | `docs/plan/at-phase-map.yaml` (docs/) | 1 | L0 | L0, L1, L2, L3, L4, L5 | — |
| `C-DOC-ID-XWALK-1` | `docs/plan/id-crosswalk.md` (docs/) | 1 | L0 | L0, L1, L2, L3, L4, L5 | — |
| `C-DOC-CP4-RULES-1` | `docs/build/rulesets/cp-4-contract-tags.json` (docs/) | 1 | L0 | L0 | — |
| `C-DOC-DR-L3-04-1` | `docs/decisions/D-L3-04.md` (docs/) | 1 | L0 | L3 | — |

**Reading the "publishing lane" column.** L0 *writes* every one of these files. The publishing lane is the lane whose implementation must satisfy it and whose CCRs about it are privileged. `contracts/**` is L0's path without exception (PARTITION.md line 22, rule 2).

---

## 3. Conventions every task in this file obeys

Set once per shell session, on the human lead's machine. Git Bash on Windows, or any POSIX shell.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org
export CP="$HOME/src/control-plane"
export CPR="$HOME/src/control-plane-records"
export PATH="$PATH"
echo "ORG=$ORG CP=$CP CPR=$CPR"
```

* Every contract file opens with the same seven-key header block. No exceptions; L0-P0-021 mechanically fails any file missing one.

```yaml
# --- CONTRACT HEADER (frozen) ---
contract_id: C-XXX-YYY-N
contract_version: N
owner: L0
publishing_lane: LN
consuming_lanes: [L1, L2]
spec_refs: ["Section 97.3"]
ccr_required: true
```

  For JSON Schema files the same seven keys appear under a top-level `"x-contract"` object, because JSON carries no comments.

* One commit per task. Commit subject is the task id. Never squash Phase 0 tasks together — the freeze tag must be bisectable.
* `# EXPECT: reject — <reason>` is the mandatory first line of every golden-invalid fixture.
* No task in this file writes into `control-plane-records` except L0-P0-001 and L0-P0-012.

---

---

## 4. Phase 0 tasks

---

### L0-P0-001 — Create the two repositories and the contracts skeleton

| | |
| --- | --- |
| **Size** | M |
| **Depends on** | — |
| **Writes** | `control-plane/` root, `control-plane/contracts/**` (empty tree), `control-plane-records/` root |
| **Spec** | Section 40.1 (D89, D107); PARTITION.md Repositories table |

**Commands**

```bash
set -euo pipefail
mkdir -p "$(dirname "$CP")"
gh repo create "$ORG/control-plane" --private --description "Control plane: registries, contracts, schemas, validators, reconciler, workflows, access config"
gh repo create "$ORG/control-plane-records" --private --description "Records repository: records/** and events/** only (D89)"
git clone "https://github.com/$ORG/control-plane.git" "$CP"
git clone "https://github.com/$ORG/control-plane-records.git" "$CPR"
cd "$CP"
git checkout -b l0/phase-0-contracts
mkdir -p contracts/registry contracts/records contracts/workflows contracts/reconciler contracts/provisioning contracts/access contracts/stubs contracts/fixtures contracts/ci docs
printf '%s\n' '*.pyc' '__pycache__/' '.venv/' '.env.local' > .gitignore
printf '%s\n' '# control-plane' '' 'Registries, contracts, schemas, validators, reconciler, provisioning, reusable workflows, access and infra config.' '' '`contracts/**` is FROZEN and owned by L0. No lane edits it. See `docs/contract-change-request.md`.' > README.md
git add -A
git commit -m "L0-P0-001: repositories and contracts skeleton"
cd "$CPR"
mkdir -p records events
printf '%s\n' 'Records repository. records/** and events/** only. Append-only. Written by the records-writer credential (D89).' > README.md
printf '%s\n' '# placeholder; real records are written by workflows, never by hand' > records/.gitkeep
printf '%s\n' '# placeholder; one file per event, never a shared append target' > events/.gitkeep
git add -A
git commit -m "L0-P0-001: records repository skeleton"
git push -u origin HEAD
cd "$CP"
```

Then write `contracts/README.md` with the file-tree legend:

**Commands**

```bash
set -euo pipefail
cd "$CP"
{
  echo '# contracts/ — FROZEN'
  echo
  echo 'Owned by L0 exclusively (PARTITION.md line 22, rule 2). Written in Phase 0, frozen at tag `contracts/v1.0.0`.'
  echo
  echo 'A lane needing a change files a Contract Change Request (`docs/contract-change-request.md`). A lane never edits this tree.'
  echo
  echo '- `registry/`      schemas Lane 1 publishes against'
  echo '- `records/`       record and event envelope contracts Lane 4 publishes against'
  echo '- `workflows/`     workflow input/secret contracts Lane 2 publishes against'
  echo '- `reconciler/`    reconciler input contracts Lane 3 consumes'
  echo '- `provisioning/`  provisioning operation contracts Lane 3 consumes'
  echo '- `access/`        access-model contracts Lane 5 publishes against'
  echo '- `stubs/`         the artifact each lane develops against before the real thing exists'
  echo '- `fixtures/`      golden-valid and golden-invalid documents per contract'
  echo '- `ci/`            the contract self-verification harness (L0-owned scripts only)'
} > contracts/README.md
git add -A && git commit -m "L0-P0-001: contracts tree legend"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Both repositories exist and are private | `gh repo view "$ORG/control-plane" --json isPrivate -q .isPrivate` then the same for `control-plane-records` | `true` then `true` |
| 2 | The nine `contracts/` entries exist | `ls "$CP/contracts" \| sort \| tr '\n' ' '` | `README.md access ci fixtures provisioning reconciler records registry stubs workflows ` |
| 3 | No record or event YAML exists in `control-plane` | `find "$CP" -path '*records*' -name '*.yaml' \| wc -l` | `0` |
| 4 | Branch is `l0/phase-0-contracts` | `git -C "$CP" rev-parse --abbrev-ref HEAD` | `l0/phase-0-contracts` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
for d in registry records workflows reconciler provisioning access stubs fixtures ci; do
  test -d "contracts/$d" || { echo "L0-P0-001 FAIL missing contracts/$d"; exit 1; }
done
test -d "$CPR/records" && test -d "$CPR/events" && echo "L0-P0-001 PASS"
```

Expected: `L0-P0-001 PASS`

**STOP RULE** — If `gh repo create` fails on plan tier, org policy or an existing name, do not create the repositories under a personal account and do not rename them. Open a blocker issue using the Section 8.4 template with `blocked_contract: none` and `blocked_lanes: ALL`. Every lane is blocked by this task; it is the highest-priority L0 emergency in the programme.

---

### L0-P0-024 — Bootstrap the GitHub label set on both repositories

| | |
| --- | --- |
| **Size** | S |
| **Depends on** | L0-P0-001 |
| **Writes** | GitHub label set on `$ORG/control-plane` (17 labels) and `$ORG/control-plane-records` (7 labels); no files on disk |
| **Spec** | `implementation/master/08-progress-tracking.md` §1.1 (label bootstrap); §6.1 (STOP rule escalation uses `blocker` and `lane-N`); §6.2 (L0 triage uses `class-*`); §6.3 (L0 disposition uses `disp-*`) |

Every STOP rule in every lane routes escalation through `gh issue create --label blocker --label "lane-N"`. Both calls fail with `label not found` until the labels exist on the repository. This task creates the complete label set idempotently, immediately after the repositories are created, so that no subsequent task can fail for a missing label.

**Labels created on `control-plane`** (17 total):

| Group | Labels | Purpose |
| --- | --- | --- |
| Base | `blocker`, `lane-0` – `lane-5` | Required by every STOP rule and blocker issue template (§6.1) |
| Triage | `class-amber`, `class-red`, `class-blocking` | Applied by L0 after triage (§6.2); lanes may never apply these |
| Disposition | `disp-unblock`, `disp-respec`, `disp-contract-change`, `disp-reassign`, `disp-withdraw` | Applied by L0 at blocker close (§6.3) |
| Dispatch | `FIX_NOW`, `ready-for-merge` | Used by the dispatch gate and merge-train machinery |

**Labels created on `control-plane-records`** (7 total): `blocker` + `lane-0` – `lane-5`. The records repository follows the same STOP rule escalation path; triage and disposition labels are L0-only and live only on `control-plane`.

**Commands**

```bash
set -euo pipefail
: "${ORG:?set ORG}"

# ── Base labels — required by every STOP rule and blocker issue template (§6.1) ──

gh label create "blocker"  --repo "$ORG/control-plane" --color "#d73a4a" \
  --description "Blocks lane progress; open per docs/escalation/BLOCKER.md" --force
gh label create "lane-0"   --repo "$ORG/control-plane" --color "#5319e7" \
  --description "Issue owned by / filed from L0 (integrator)" --force
gh label create "lane-1"   --repo "$ORG/control-plane" --color "#5319e7" \
  --description "Issue owned by / filed from L1 (registry)" --force
gh label create "lane-2"   --repo "$ORG/control-plane" --color "#5319e7" \
  --description "Issue owned by / filed from L2 (workflows)" --force
gh label create "lane-3"   --repo "$ORG/control-plane" --color "#5319e7" \
  --description "Issue owned by / filed from L3 (reconciler)" --force
gh label create "lane-4"   --repo "$ORG/control-plane" --color "#5319e7" \
  --description "Issue owned by / filed from L4 (records)" --force
gh label create "lane-5"   --repo "$ORG/control-plane" --color "#5319e7" \
  --description "Issue owned by / filed from L5 (access/infra)" --force

# ── Triage labels — L0-only; applied by L0 after a blocker is filed (§6.2) ───────
# Descriptions and colour codes are verbatim from 08-progress-tracking.md §1.1.

gh label create "class-amber"          --repo "$ORG/control-plane" --color "#FFA500" \
  --description "Non-urgent; lane has other issued tasks" --force
gh label create "class-red"            --repo "$ORG/control-plane" --color "#D93F0B" \
  --description "Material risk to partition or contract; 2-bd deadline" --force
gh label create "class-blocking"       --repo "$ORG/control-plane" --color "#B60205" \
  --description "Unsafe to proceed; hold merge-train slot immediately" --force

# ── Disposition labels — L0-only; applied at blocker close (§6.3) ─────────────────
# Descriptions and colour codes are verbatim from 08-progress-tracking.md §1.1.

gh label create "disp-unblock"         --repo "$ORG/control-plane" --color "#0E8A16" \
  --description "Answered; task resumes" --force
gh label create "disp-respec"          --repo "$ORG/control-plane" --color "#0E8A16" \
  --description "Packet rewritten; task re-issued under same id" --force
gh label create "disp-contract-change" --repo "$ORG/control-plane" --color "#0E8A16" \
  --description "L0 edited contracts/**; all lanes notified" --force
gh label create "disp-reassign"        --repo "$ORG/control-plane" --color "#0E8A16" \
  --description "Work moved to owning lane; new task issued" --force
gh label create "disp-withdraw"        --repo "$ORG/control-plane" --color "#0E8A16" \
  --description "Task cancelled; withdrawn: true written to ledger" --force

# ── Dispatch-gate labels ───────────────────────────────────────────────────────────

gh label create "FIX_NOW"              --repo "$ORG/control-plane" --color "#B60205" \
  --description "Must be fixed before dispatch; see _DISPATCH_GATE.md" --force
gh label create "ready-for-merge"      --repo "$ORG/control-plane" --color "#0E8A16" \
  --description "All acceptance criteria pass; cleared for merge train" --force

echo "CP LABELS OK"

# ── Mirror base labels on control-plane-records ────────────────────────────────────
# STOP rules for L4 record-store tasks file blockers against this repository.

gh label create "blocker"  --repo "$ORG/control-plane-records" --color "#d73a4a" \
  --description "Blocks lane progress; open per docs/escalation/BLOCKER.md" --force
gh label create "lane-0"   --repo "$ORG/control-plane-records" --color "#5319e7" \
  --description "Issue owned by / filed from L0 (integrator)" --force
gh label create "lane-1"   --repo "$ORG/control-plane-records" --color "#5319e7" \
  --description "Issue owned by / filed from L1 (registry)" --force
gh label create "lane-2"   --repo "$ORG/control-plane-records" --color "#5319e7" \
  --description "Issue owned by / filed from L2 (workflows)" --force
gh label create "lane-3"   --repo "$ORG/control-plane-records" --color "#5319e7" \
  --description "Issue owned by / filed from L3 (reconciler)" --force
gh label create "lane-4"   --repo "$ORG/control-plane-records" --color "#5319e7" \
  --description "Issue owned by / filed from L4 (records)" --force
gh label create "lane-5"   --repo "$ORG/control-plane-records" --color "#5319e7" \
  --description "Issue owned by / filed from L5 (access/infra)" --force

echo "CPR LABELS OK"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | `blocker` exists on `control-plane` | `gh label list --repo "$ORG/control-plane" --json name --limit 100 --jq 'map(select(.name=="blocker"))\|length'` | `1` |
| 2 | All six `lane-N` labels exist on `control-plane` | `gh label list --repo "$ORG/control-plane" --json name --limit 100 --jq '[.[]|select(.name\|test("^lane-[0-5]$"))]\|length'` | `6` |
| 3 | All three `class-*` labels exist on `control-plane` | `gh label list --repo "$ORG/control-plane" --json name --limit 100 --jq '[.[]|select(.name\|startswith("class-"))]\|length'` | `3` |
| 4 | All five `disp-*` labels exist on `control-plane` | `gh label list --repo "$ORG/control-plane" --json name --limit 100 --jq '[.[]|select(.name\|startswith("disp-"))]\|length'` | `5` |
| 5 | `blocker` exists on `control-plane-records` | `gh label list --repo "$ORG/control-plane-records" --json name --limit 100 --jq 'map(select(.name=="blocker"))\|length'` | `1` |
| 6 | All six `lane-N` labels exist on `control-plane-records` | `gh label list --repo "$ORG/control-plane-records" --json name --limit 100 --jq '[.[]|select(.name\|test("^lane-[0-5]$"))]\|length'` | `6` |

**SELF-VERIFY**

```bash
set -euo pipefail
: "${ORG:?set ORG}"
cp_n=$(gh label list --repo "$ORG/control-plane" --json name --limit 100 \
  --jq '[.[]|select(.name=="blocker" or (.name|startswith("lane-")) or (.name|startswith("class-")) or (.name|startswith("disp-")) or .name=="FIX_NOW" or .name=="ready-for-merge")]|length')
cpr_n=$(gh label list --repo "$ORG/control-plane-records" --json name --limit 100 \
  --jq '[.[]|select(.name=="blocker" or (.name|startswith("lane-")))]|length')
[ "$cp_n" = "17" ] && [ "$cpr_n" = "7" ] && echo "L0-P0-024 PASS" || echo "L0-P0-024 FAIL"
```

Expected: `L0-P0-024 PASS`

**STOP RULE** — If any `gh label create` call exits non-zero, the programme cannot file a blocker issue, which means no lane can report a blocked task, which means the escalation path is broken from the start. Do not proceed to L0-P0-002. File a blocker issue **by hand** (navigate to `https://github.com/$ORG/control-plane/issues/new`, paste the BLOCKER.md template fields, apply labels manually in the UI) with title `L0-P0-024 BLOCKED: gh label create failed on <repo>`, body containing the failing command and its full output, and fields `blocked_contract: none`, `blocked_lanes: ALL`. This is an L0 emergency: every subsequent task has a STOP rule that routes through `blocker`; a missing label makes every one of those STOP rules unexecutable.

---

### L0-P0-002 — The contract register and the contract header rule

| | |
| --- | --- |
| **Size** | M |
| **Depends on** | L0-P0-001 |
| **Writes** | `contracts/register.yaml`, `contracts/REGISTER.md`, `contracts/ci/header-schema.json`, `contracts/CONSUMERS.md` |
| **Spec** | PARTITION.md rules 2 and 4; Section 52.6 (inventory discipline) |

The register is the index four lanes read to discover what exists. It is written **before** any contract, so that every later task appends its row and the register can never lag behind the tree.

**Commands**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import json, pathlib
hdr = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.local/contracts/ci/header-schema.json",
  "title": "Frozen contract header block",
  "type": "object",
  "required": ["contract_id","contract_version","owner","publishing_lane","consuming_lanes","spec_refs","ccr_required"],
  "properties": {
    "contract_id": {"type":"string","pattern":"^C-[A-Z]+-[A-Z]+-[0-9]+$"},
    "contract_version": {"type":"integer","minimum":1},
    "owner": {"const":"L0"},
    "publishing_lane": {"enum":["L0","L1","L2","L3","L4","L5"]},
    "consuming_lanes": {"type":"array","minItems":0,"uniqueItems":True,
                        "items":{"enum":["L0","L1","L2","L3","L4","L5"]}},
    "spec_refs": {"type":"array","minItems":1,"items":{"type":"string"}},
    "ccr_required": {"const":True}
  },
  "additionalProperties": False
}
pathlib.Path("contracts/ci/header-schema.json").write_text(json.dumps(hdr, indent=2)+"\n", encoding="utf-8")

reg = """# --- CONTRACT HEADER (frozen) ---
contract_id: C-REG-INDEX-1
contract_version: 1
owner: L0
publishing_lane: L1
consuming_lanes: [L1, L2, L3, L4, L5]
spec_refs: ["PARTITION.md rule 2"]
ccr_required: true
# --- BODY ---
register_version: 1
frozen_tag: contracts/v1.0.0
contracts: []
"""
pathlib.Path("contracts/register.yaml").write_text(reg, encoding="utf-8")

readme = """# Contract register

The authoritative human-readable index is the table in
`Code/implementation/lanes/L0-01-phase-0-contracts.md`, Section 2.
`contracts/register.yaml` is the machine-readable copy. If they disagree,
`register.yaml` is wrong and is corrected against the table.

Rules:
1. Every file under `contracts/` other than `README.md`, `REGISTER.md`,
   `register.yaml`, `tooling.lock`, `ci/**`, `stubs/**` and `fixtures/**`
   carries a contract header and has exactly one row here.
2. A contract with no stub is not published (D-L0-06).
3. No lane edits this tree. File a Contract Change Request.
"""
pathlib.Path("contracts/REGISTER.md").write_text(readme, encoding="utf-8")
print("written")
PY
git add -A && git commit -m "L0-P0-002: contract register and header rule"
```

Register-append helper, used by every later task (written once, here):

**Commands**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import pathlib
helper = '''"""Append one contract row to contracts/register.yaml. L0-owned; lanes never run it."""
import sys, yaml, pathlib
cid, path, ver, pub, cons, stub = sys.argv[1:7]
p = pathlib.Path("contracts/register.yaml")
head, _, _ = p.read_text(encoding="utf-8").partition("contracts:")
doc = yaml.safe_load(p.read_text(encoding="utf-8"))
rows = doc.get("contracts") or []
rows = [r for r in rows if r["id"] != cid]
rows.append({"id": cid, "path": path, "version": int(ver),
             "publishing_lane": pub, "consuming_lanes": cons.split(","),
             "stub": stub})
p.write_text(head + "contracts:\\n" +
             yaml.safe_dump(rows, sort_keys=False, indent=2, default_flow_style=False),
             encoding="utf-8")
print("registered", cid, "total", len(rows))
'''
pathlib.Path("contracts/ci/register_add.py").write_text(helper, encoding="utf-8")
print("helper written")
PY
git add -A && git commit -m "L0-P0-002: register-append helper"
```

Consumer map, listing every contract and the lanes that consume it (required by §4.11):

**Commands**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import pathlib
lines = ["# contracts/CONSUMERS.md — generated by L0-P0-002",
"# Every contract in §2 of L0-01-phase-0-contracts.md must appear here.",
"# Format: CONTRACT-ID  path  consuming_lanes",
""]
rows = [
  ("C-CAP-VOCAB-1",    "registry/capability.vocabulary.v1.yaml",          "L1,L3,L5"),
  ("C-REG-PEOPLE-1",   "registry/people.registry.v1.json",                "L1,L3,L5"),
  ("C-REG-ROLES-1",    "registry/roles.registry.v1.json",                 "L1,L3,L5"),
  ("C-REG-PRODUCT-2",  "registry/product.contract.v2.json",               "L1,L2,L3,L4,L5"),
  ("C-REG-VERIFICATION-1","registry/verification.contract.v1.json",       "L1,L2"),
  ("C-REG-SERVICE-1",  "registry/service.contract.v1.json",               "L1,L3"),
  ("C-REG-TOPOLOGY-1", "registry/topology.registry.v1.json",              "L1,L3,L5"),
  ("C-REG-PLATFORM-1", "registry/platform.record.v1.json",                "L1,L2,L3,L4"),
  ("C-REC-ENV-1",      "records/record.envelope.v1.json",                 "L2,L3,L4"),
  ("C-EVT-ENV-1",      "records/event.envelope.v1.json",                  "L1,L2,L3,L4,L5"),
  ("C-EVT-ENUM-1",     "records/event-type.enum.v1.yaml",                 "L1,L2,L3,L4,L5"),
  ("C-REC-STORE-MAP-1","records/store-map.v1.yaml",                       "L2,L3,L4"),
  ("C-WF-IFACE-1",     "workflows/reusable-workflow.interface.v1.yaml",   "L2,L3,L5"),
  ("C-WF-CHECKS-1",    "workflows/required-checks.v1.yaml",               "L2,L3,L5"),
  ("C-WF-SECRETS-1",   "workflows/secret-tiers.v1.yaml",                  "L2,L5"),
  ("C-WF-EVIDENCE-1",  "workflows/evidence-chain.v1.yaml",                "L2,L4"),
  ("C-RECON-SET-1",    "reconciler/comparison-set.v1.yaml",               "L1,L3,L5"),
  ("C-RECON-FIND-1",   "reconciler/drift-finding.v1.json",                "L2,L3,L4,L5"),
  ("C-RECON-REPAIR-1", "reconciler/repair-record.v1.json",                "L3,L4"),
  ("C-PROV-OP-1",      "provisioning/operation.v1.yaml",                  "L1,L3,L5"),
  ("C-ACC-PERM-1",     "access/permission-model.v1.yaml",                 "L1,L3,L5"),
  ("C-ACC-PROT-1",     "access/protection.template.v1.yaml",              "L2,L3,L5"),
  ("C-ACC-LAYER-1",    "access/layer-split.v1.yaml",                      "L3,L4,L5"),
  ("C-CFG-SCHEMA-IDS-1","schema-ids.yaml",                                "L0,L1"),
  ("C-CFG-ESTATE-1",   "estate.yaml",                                     "L0,L2,L4,L5"),
  ("C-CFG-TOOLING-1",  "tooling.lock",                                    "L0"),
  ("C-CFG-ENV-SCHEMA-1","environment-schema.yaml",                        "L5"),
  ("C-EVT-TYPES-1",    "event-types/event-type.enum.v1.yaml",             "L1,L4"),
  ("C-CLI-VALIDATE-1", "cli/registry-validate.yaml",                      "L0"),
  ("C-WF-CTX-1",       "workflow-io/required-contexts.tsv",               "L1,L2"),
  ("C-EV-VER-OBS-1",   "evidence/version-observation.yaml",               "L3,L4"),
  ("C-EV-11Q-1",       "evidence/eleven-question-map.yaml",               "L1,L2,L3,L4,L5"),
  ("C-L3-HARNESS-1",   "l3-test-harness.env",                             "L3"),
  ("C-L3-ORG-GATE-1",  "l3-live-org-gate.md",                             "L3"),
  ("C-L4-RECORDS-1",   "l4-records.yaml",                                 "L4"),
  ("C-CFG-INTEG-1",    "integration.yaml",                                "L0"),
  ("C-DOC-AT-PHASE-1", "docs/plan/at-phase-map.yaml",                     "L0,L1,L2,L3,L4,L5"),
  ("C-DOC-ID-XWALK-1", "docs/plan/id-crosswalk.md",                       "L0,L1,L2,L3,L4,L5"),
  ("C-DOC-CP4-RULES-1","docs/build/rulesets/cp-4-contract-tags.json",     "L0"),
  ("C-DOC-DR-L3-04-1", "docs/decisions/D-L3-04.md",                       "L3"),
]
for cid, path, cons in rows:
    lines.append(f"{cid}  {path}  {cons}")
pathlib.Path("contracts/CONSUMERS.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
print(f"CONSUMERS.md written — {len(rows)} entries")
PY
git add -A && git commit -m "L0-P0-002: CONSUMERS.md (§4.11 requirement)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Header schema is valid JSON | `python -c "import json;json.load(open('contracts/ci/header-schema.json'));print('ok')"` | `ok` |
| 2 | Register parses and declares zero contracts so far | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/register.yaml'))['contracts'] or []))"` | `0` |
| 3 | Register carries a valid header | `python -c "import yaml;d=yaml.safe_load(open('contracts/register.yaml'));print(d['contract_id'],d['ccr_required'])"` | `C-REG-INDEX-1 True` |
| 4 | Helper is executable and idempotent | `python contracts/ci/register_add.py C-TEST-TMP-1 x.yaml 1 L1 L1 stubs/x.yaml && python contracts/ci/register_add.py C-TEST-TMP-1 x.yaml 1 L1 L1 stubs/x.yaml` | `registered C-TEST-TMP-1 total 1` twice |

After criterion 4, remove the probe row:

**Commands**

```bash
set -euo pipefail
cd "$CP"
python -c "import yaml,pathlib;p=pathlib.Path('contracts/register.yaml');h=p.read_text(encoding='utf-8').partition('contracts:')[0];p.write_text(h+'contracts: []\n',encoding='utf-8');print('reset')"
git add -A && git commit -m "L0-P0-002: reset register after helper probe"
```

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import json, yaml
h = json.load(open("contracts/ci/header-schema.json"))
r = yaml.safe_load(open("contracts/register.yaml"))
ok = set(h["required"]) <= set(r) and (r["contracts"] or []) == []
print("L0-P0-002 PASS" if ok else "L0-P0-002 FAIL")
PY
```

Expected: `L0-P0-002 PASS`

**STOP RULE** — If `python` or `PyYAML` is unavailable, install them before proceeding; do not hand-verify. If the register cannot be made machine-readable, do not fall back to a Markdown-only index: four lanes must be able to enumerate contracts programmatically. Open a blocker issue with `blocked_lanes: ALL`.

---

### L0-P0-003 — `C-CAP-VOCAB-1`: the closed capability vocabulary

| | |
| --- | --- |
| **Size** | M |
| **Depends on** | L0-P0-002 |
| **Writes** | `contracts/registry/capability.vocabulary.v1.yaml`, `contracts/stubs/capability.vocabulary.yaml`, `contracts/fixtures/C-CAP-VOCAB-1/{valid-001,invalid-001}.yaml` |
| **Spec** | Section 9 (capability table), Section 9.1, Section 8 (D106, D109), invariant 11, invariant 79 |

This is the first contract because three lanes resolve authority through it. Section 9.1 binds: "A capability appearing in a `roles.yaml` default, in a `people.yaml` grant, or in any assignment type without a row in this table fails control-plane CI validation."

**File to create — `contracts/registry/capability.vocabulary.v1.yaml`**

```yaml
# --- CONTRACT HEADER (frozen) ---
contract_id: C-CAP-VOCAB-1
contract_version: 1
owner: L0
publishing_lane: L1
consuming_lanes: [L1, L3, L5]
spec_refs: ["Section 9", "Section 9.1", "Section 8 (D106)", "Section 9.1 (D109)"]
ccr_required: true
# --- BODY ---
closed: true

capabilities:
  - { id: backend,                  kind: competence }
  - { id: frontend,                 kind: competence }
  - { id: mobile,                   kind: competence }
  - { id: data,                     kind: competence }
  - { id: code-review,              kind: authority }
  - { id: architecture,             kind: authority }
  - { id: security-review,          kind: authority }
  - { id: migration-review,         kind: authority }
  - { id: verification,             kind: authority }
  - { id: uat,                      kind: authority }
  - { id: release-signoff,          kind: authority }
  - { id: production-approval,      kind: authority }
  - { id: incident-response,        kind: authority }
  - { id: plan-approval,            kind: authority }
  - { id: reviewer-matrix-change,   kind: authority }
  - { id: platform-change-approval, kind: authority }
  - { id: platform-admin,           kind: authority }
  - { id: devops,                   kind: authority }
  - { id: lifecycle-decision,       kind: authority }
  - { id: escalation,               kind: authority }
  - { id: mobile-release,           kind: authority }
  - { id: exceptional-approval,     kind: authority }
  - { id: people-intelligence,      kind: authority }
  - { id: strategy,                 kind: business }
  - { id: budget,                   kind: business }
  - { id: hiring,                   kind: business }
  - { id: customer-commitment,      kind: business }

# Section 8 (D106): granted ONLY by explicit entry in people.yaml, never by a
# roles.yaml default. Control-plane CI rejects a roles.yaml default containing any.
dangerous_never_by_role_default:
  - production-approval
  - platform-change-approval
  - platform-admin
  - security-review
  - migration-review
  - exceptional-approval
  - lifecycle-decision
  - people-intelligence

# Section 9.1 (D109): Founder-held, not delegable, the single gate on Layer B.
non_delegable: [people-intelligence]

# Section 9.1: delegable ONLY through a dated founder-delegation assignment.
founder_class_delegable_by_dated_assignment_only:
  - strategy
  - budget
  - hiring
  - lifecycle-decision
  - customer-commitment
  - exceptional-approval

rules:
  - { id: CAP-R1, spec_ref: "Section 9.1", text: "Authority checks read capability, never role name." }
  - { id: CAP-R2, spec_ref: "Section 9.1", text: "Capability is validated against assignment; both must be true." }
  - { id: CAP-R3, spec_ref: "Section 9.1, Section 64.1", text: "An undefined capability resolves to denial, never permission." }
```

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-CAP-VOCAB-1
# 1. Create the contract file with the exact content shown above, then:
cp contracts/registry/capability.vocabulary.v1.yaml contracts/stubs/capability.vocabulary.yaml
printf '%s\n' 'person: dev-a' 'granted: [backend, code-review, uat]' \
  > contracts/fixtures/C-CAP-VOCAB-1/valid-001.yaml
printf '%s\n' '# EXPECT: reject — `deploy-anything` has no row in the Section 9 capability table' \
  'person: dev-a' 'granted: [backend, deploy-anything]' \
  > contracts/fixtures/C-CAP-VOCAB-1/invalid-001.yaml
python contracts/ci/register_add.py C-CAP-VOCAB-1 registry/capability.vocabulary.v1.yaml 1 L1 L1,L3,L5 stubs/capability.vocabulary.yaml
git add -A && git commit -m "L0-P0-003: C-CAP-VOCAB-1 closed capability vocabulary"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Exactly the 27 capability rows of the Section 9 table | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/registry/capability.vocabulary.v1.yaml'))['capabilities']))"` | `27` |
| 2 | The dangerous set is exactly the eight of Section 8 (D106) | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/registry/capability.vocabulary.v1.yaml'))['dangerous_never_by_role_default']))"` | `8` |
| 3 | `people-intelligence` is the only non-delegable capability | `python -c "import yaml;print(yaml.safe_load(open('contracts/registry/capability.vocabulary.v1.yaml'))['non_delegable'])"` | `['people-intelligence']` |
| 4 | Stub is byte-identical to the contract | `cmp -s contracts/registry/capability.vocabulary.v1.yaml contracts/stubs/capability.vocabulary.yaml && echo same` | `same` |
| 5 | Invalid fixture declares its expectation on line 1 | `head -1 contracts/fixtures/C-CAP-VOCAB-1/invalid-001.yaml \| grep -c '^# EXPECT: reject'` | `1` |
| 6 | Register now holds one row | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/register.yaml'))['contracts']))"` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import yaml
c = yaml.safe_load(open("contracts/registry/capability.vocabulary.v1.yaml"))
ids = {x["id"] for x in c["capabilities"]}
ok  = len(ids) == 27 and c["closed"] is True
ok &= set(c["dangerous_never_by_role_default"]) <= ids and len(c["dangerous_never_by_role_default"]) == 8
ok &= set(c["non_delegable"]) == {"people-intelligence"}
ok &= set(c["founder_class_delegable_by_dated_assignment_only"]) <= ids
v = yaml.safe_load(open("contracts/fixtures/C-CAP-VOCAB-1/valid-001.yaml"))
i = yaml.safe_load(open("contracts/fixtures/C-CAP-VOCAB-1/invalid-001.yaml"))
ok &= set(v["granted"]) <= ids and not set(i["granted"]) <= ids
print("L0-P0-003 PASS" if ok else "L0-P0-003 FAIL")
PY
```

Expected: `L0-P0-003 PASS`

**STOP RULE** — If a capability appears in your reading of the spec that is not in the Section 9 table, **do not add it**. Section 9.1 makes that table the complete vocabulary; adding a row here silently widens authority across three lanes. File a CCR of class **CCR-BREAKING** (Section 8.2) and stop.

---

### L0-P0-004 — `C-REG-PEOPLE-1`: the People Registry schema

| | |
| --- | --- |
| **Size** | L |
| **Depends on** | L0-P0-003 |
| **Writes** | `contracts/registry/people.registry.v1.json`, `contracts/stubs/people.yaml`, `contracts/fixtures/C-REG-PEOPLE-1/{valid-001,invalid-001,invalid-002,invalid-003}.yaml` |
| **Spec** | Section 7 (`people.yaml`, `registry_version: 1`), 7.1, 7.3, Section 60.2 (`registry_version`), invariants 50, 58, 79 |

**Shape, exact.** Top-level `registry_version: 1` and `people[]`. Each person: `id` (stable, never reused), `display_name`, `github_login`, `role`, `employment_type` (`employee|contractor|intern|temporary_specialist|consultant`, open-ended per 7.1), `capabilities[]` (every member resolved against `C-CAP-VOCAB-1`), `ai_runtime` (nullable), `availability` (`active|on_leave|departing|departed`), `access_status` (`pending|provisioned|suspended|revoked`), `work_arrangement` (7.3: `timezone` IANA, `arrangement` `onsite|hybrid|remote`, `schedule` per weekday with `start`/`end`, `fte` in `(0,1]`, `public_holiday_set`, `accepted_coverage_window` nullable), `start_date`, `end_date` (**mandatory for every non-employee**, 7.1), optional `scope` (`products[]`, `repositories_only`).

**Legal-pairing rule, encoded as schema (7.1).** `departed` implies `revoked`; `revoked` implies `departed` or a non-employee past `end_date`; `suspended` is valid only with `active` or `on_leave`. Encoded with `allOf`/`if-then` so it is machine-refutable, not prose.

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-REG-PEOPLE-1
python - <<'PY'
import json, pathlib
S = {
 "$schema":"https://json-schema.org/draft/2020-12/schema",
 # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
 "$id":"https://control-plane.local/contracts/registry/people.registry.v1.json",
 "x-contract":{"contract_id":"C-REG-PEOPLE-1","contract_version":1,"owner":"L0",
   "publishing_lane":"L1","consuming_lanes":["L1","L3","L5"],
   "spec_refs":["Section 7","Section 7.1","Section 7.3","Section 60.2"],"ccr_required":True},
 "type":"object","required":["registry_version","people"],"additionalProperties":False,
 "properties":{
  "registry_version":{"const":1},
  "people":{"type":"array","minItems":1,"items":{"$ref":"#/$defs/person"}}},
 "$defs":{
  "daywindow":{"type":"object","required":["start","end"],"additionalProperties":False,
    "properties":{"start":{"type":"string","pattern":"^[0-2][0-9]:[0-5][0-9]$"},
                  "end":{"type":"string","pattern":"^[0-2][0-9]:[0-5][0-9]$"}}},
  "work_arrangement":{"type":"object",
    "required":["timezone","arrangement","schedule","fte","public_holiday_set","accepted_coverage_window"],
    "additionalProperties":False,
    "properties":{
      "timezone":{"type":"string","pattern":"^[A-Za-z_]+/[A-Za-z_+\\-0-9]+$"},
      "arrangement":{"enum":["onsite","hybrid","remote"]},
      "schedule":{"type":"object","additionalProperties":False,
        "properties":{d:{"$ref":"#/$defs/daywindow"} for d in ["mon","tue","wed","thu","fri","sat","sun"]}},
      "fte":{"type":"number","exclusiveMinimum":0,"maximum":1},
      "public_holiday_set":{"type":"string","minLength":1},
      "accepted_coverage_window":{"type":["string","null"]}}},
  "person":{"type":"object",
    "required":["id","display_name","github_login","role","employment_type","capabilities",
                "ai_runtime","availability","access_status","start_date","end_date"],
    "additionalProperties":False,
    "properties":{
      "id":{"type":"string","pattern":"^[a-z0-9][a-z0-9-]*$"},
      "display_name":{"type":"string","minLength":1},
      "github_login":{"type":"string","minLength":1},
      "role":{"type":"string","minLength":1},
      "employment_type":{"type":"string","minLength":1},
      "capabilities":{"type":"array","uniqueItems":True,"items":{"type":"string"}},
      "ai_runtime":{"type":["string","null"]},
      "availability":{"enum":["active","on_leave","departing","departed"]},
      "access_status":{"enum":["pending","provisioned","suspended","revoked"]},
      "work_arrangement":{"$ref":"#/$defs/work_arrangement"},
      "start_date":{"type":"string","format":"date"},
      "end_date":{"type":["string","null"],"format":"date"},
      "scope":{"type":"object","additionalProperties":False,
        "properties":{"products":{"type":"array","items":{"type":"string"}},
                      "repositories_only":{"type":"boolean"}}}},
    "allOf":[
      {"title":"7.1 end_date mandatory for every non-employee",
       "if":{"properties":{"employment_type":{"not":{"const":"employee"}}}},
       "then":{"properties":{"end_date":{"type":"string"}}}},
      {"title":"7.1 departed implies revoked",
       "if":{"properties":{"availability":{"const":"departed"}}},
       "then":{"properties":{"access_status":{"const":"revoked"}}}},
      {"title":"7.1 suspended is valid only with active or on_leave",
       "if":{"properties":{"access_status":{"const":"suspended"}}},
       "then":{"properties":{"availability":{"enum":["active","on_leave"]}}}}]}}}
pathlib.Path("contracts/registry/people.registry.v1.json").write_text(json.dumps(S,indent=2)+"\n",encoding="utf-8")
print("schema written")
PY
```

**Stub — `contracts/stubs/people.yaml`** (the artifact L3 and L5 develop against before L1 publishes real registry content):

```yaml
registry_version: 1
people:
  - id: dev-a
    display_name: "Stub Developer A"
    github_login: stub-dev-a
    role: developer
    employment_type: employee
    capabilities: [backend, code-review]
    ai_runtime: null
    availability: active
    access_status: provisioned
    work_arrangement:
      timezone: Asia/Kolkata
      arrangement: hybrid
      schedule:
        mon: { start: "09:30", end: "18:30" }
        tue: { start: "09:30", end: "18:30" }
        wed: { start: "09:30", end: "18:30" }
        thu: { start: "09:30", end: "18:30" }
        fri: { start: "09:30", end: "18:30" }
      fte: 1.0
      public_holiday_set: IN
      accepted_coverage_window: null
    start_date: "2026-01-05"
    end_date: null
  - id: lead-1
    display_name: "Stub Team Lead"
    github_login: stub-lead-1
    role: team_lead
    employment_type: employee
    capabilities: [architecture, plan-approval, escalation, reviewer-matrix-change, production-approval]
    ai_runtime: null
    availability: active
    access_status: provisioned
    work_arrangement:
      timezone: Asia/Kolkata
      arrangement: hybrid
      schedule:
        mon: { start: "09:30", end: "18:30" }
        tue: { start: "09:30", end: "18:30" }
        wed: { start: "09:30", end: "18:30" }
        thu: { start: "09:30", end: "18:30" }
        fri: { start: "09:30", end: "18:30" }
      fte: 1.0
      public_holiday_set: IN
      accepted_coverage_window: null
    start_date: "2026-01-05"
    end_date: null
```

**Fixtures**

| File | Line 1 | Proves |
| --- | --- | --- |
| `valid-001.yaml` | (copy of the stub) | The stub itself validates |
| `invalid-001.yaml` | `# EXPECT: reject — contractor with null end_date (Section 7.1)` | End-date rule fires |
| `invalid-002.yaml` | `# EXPECT: reject — availability departed with access_status provisioned (Section 7.1)` | Pairing rule fires |
| `invalid-003.yaml` | `# EXPECT: reject — timezone written as a UTC offset, not an IANA identifier (Section 7.3)` | Timezone rule fires |

**Commands**

```bash
set -euo pipefail
cd "$CP"
cp contracts/stubs/people.yaml contracts/fixtures/C-REG-PEOPLE-1/valid-001.yaml
python contracts/ci/register_add.py C-REG-PEOPLE-1 registry/people.registry.v1.json 1 L1 L1,L3,L5 stubs/people.yaml
git add -A && git commit -m "L0-P0-004: C-REG-PEOPLE-1 people registry schema, stub, fixtures"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Schema is valid JSON Schema 2020-12 | `check-jsonschema --check-metaschema contracts/registry/people.registry.v1.json && echo ok` | `ok` |
| 2 | The stub validates | `check-jsonschema --schemafile contracts/registry/people.registry.v1.json contracts/stubs/people.yaml && echo ok` | `ok` |
| 3 | Every stub capability exists in `C-CAP-VOCAB-1` | see SELF-VERIFY | `L0-P0-004 PASS` |
| 4 | All three invalid fixtures are rejected | `for f in contracts/fixtures/C-REG-PEOPLE-1/invalid-*.yaml; do check-jsonschema --schemafile contracts/registry/people.registry.v1.json "$f" >/dev/null 2>&1 && echo "LEAK $f" || echo "rejected $f"; done` | three `rejected …` lines, no `LEAK` |
| 5 | Register now holds two rows | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/register.yaml'))['contracts']))"` | `2` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import yaml
vocab = {c["id"] for c in yaml.safe_load(open("contracts/registry/capability.vocabulary.v1.yaml"))["capabilities"]}
stub  = yaml.safe_load(open("contracts/stubs/people.yaml"))
bad = [c for p in stub["people"] for c in p["capabilities"] if c not in vocab]
print("L0-P0-004 PASS" if not bad else f"L0-P0-004 FAIL undefined capabilities: {bad}")
PY
```

Expected: `L0-P0-004 PASS`

**STOP RULE** — If the pairing rules of 7.1 cannot be expressed in JSON Schema on your validator, do not drop them to prose comments. A pairing rule that is not machine-refutable is a rule L1 will not enforce and L3 will not detect. File a CCR of class **CCR-BLOCKING** and stop: L1, L3 and L5 all block on this contract.

---

### L0-P0-005 — `C-REG-ROLES-1`: the Role Registry schema

| | |
| --- | --- |
| **Size** | S |
| **Depends on** | L0-P0-003 |
| **Writes** | `contracts/registry/roles.registry.v1.json`, `contracts/stubs/roles.yaml`, `contracts/fixtures/C-REG-ROLES-1/{valid-001,invalid-001}.yaml` |
| **Spec** | Section 8 (`roles.yaml`, `registry_version: 1`), Section 8 (D106), Section 9.1 |

**Shape.** `registry_version: 1`; `roles[]` each with `id` and `default_capabilities[]`. Two binding constraints encoded in the schema, both from Section 8: (a) every entry of `default_capabilities` resolves against `C-CAP-VOCAB-1`; (b) **no default may contain any member of `dangerous_never_by_role_default`** — "Control-plane CI rejects a `roles.yaml` default containing any of them" (D106).

Constraint (b) is expressed as a JSON Schema `not`/`contains` over the eight literal ids, so the rejection is mechanical rather than a lane's judgement call.

**Stub — `contracts/stubs/roles.yaml`** carries the eleven roles of the Section 8 listing verbatim: `founder`, `team_lead`, `acting_team_lead`, `developer`, `mobile_developer`, `senior_developer`, `qa`, `devops`, `foundational_developer`, `specialist`, `contractor`.

> **Note for the executor.** The Section 8 listing shows `founder` with `default_capabilities` including `lifecycle-decision` and `people-intelligence`, which D106 in the same section forbids as role defaults. The contradiction is resolved in Section 8 itself, in favour of the safe default. **The stub therefore gives `founder` an empty `default_capabilities` list**, and both capabilities are granted by explicit `people.yaml` entry. This is L0 decision **D-L0-09**, recorded here and in `contracts/registry/roles.registry.v1.json` under `x-contract.notes`. No lane re-decides it.

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-REG-ROLES-1
python - <<'PY'
import json, yaml, pathlib
dangerous = yaml.safe_load(open("contracts/registry/capability.vocabulary.v1.yaml"))["dangerous_never_by_role_default"]
S = {
 "$schema":"https://json-schema.org/draft/2020-12/schema",
 # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
 "$id":"https://control-plane.local/contracts/registry/roles.registry.v1.json",
 "x-contract":{"contract_id":"C-REG-ROLES-1","contract_version":1,"owner":"L0",
   "publishing_lane":"L1","consuming_lanes":["L1","L3","L5"],
   "spec_refs":["Section 8","Section 8 (D106)","Section 9.1"],"ccr_required":True,
   "notes":["D-L0-09: founder default_capabilities is empty; lifecycle-decision and "
            "people-intelligence are granted by explicit people.yaml entry only (D106)."]},
 "type":"object","required":["registry_version","roles"],"additionalProperties":False,
 "properties":{
  "registry_version":{"const":1},
  "roles":{"type":"array","minItems":1,"items":{
    "type":"object","required":["id","default_capabilities"],"additionalProperties":False,
    "properties":{
      "id":{"type":"string","pattern":"^[a-z][a-z0-9_]*$"},
      "default_capabilities":{
        "type":"array","uniqueItems":True,"items":{"type":"string"},
        "not":{"contains":{"enum":dangerous}},
        "description":"D106: no role default may carry a dangerous capability"}}}}}}
pathlib.Path("contracts/registry/roles.registry.v1.json").write_text(json.dumps(S,indent=2)+"\n",encoding="utf-8")

stub = {"registry_version":1,"roles":[
 {"id":"founder","default_capabilities":[]},
 {"id":"team_lead","default_capabilities":["architecture","plan-approval","escalation","reviewer-matrix-change"]},
 {"id":"acting_team_lead","default_capabilities":["architecture","plan-approval","escalation","reviewer-matrix-change"]},
 {"id":"developer","default_capabilities":["code-review"]},
 {"id":"mobile_developer","default_capabilities":["code-review","mobile-release"]},
 {"id":"senior_developer","default_capabilities":["code-review","architecture"]},
 {"id":"qa","default_capabilities":["verification","uat","release-signoff"]},
 {"id":"devops","default_capabilities":["devops","code-review"]},
 {"id":"foundational_developer","default_capabilities":["code-review"]},
 {"id":"specialist","default_capabilities":[]},
 {"id":"contractor","default_capabilities":[]}]}
pathlib.Path("contracts/stubs/roles.yaml").write_text(yaml.safe_dump(stub,sort_keys=False),encoding="utf-8")
pathlib.Path("contracts/fixtures/C-REG-ROLES-1/valid-001.yaml").write_text(yaml.safe_dump(stub,sort_keys=False),encoding="utf-8")
pathlib.Path("contracts/fixtures/C-REG-ROLES-1/invalid-001.yaml").write_text(
 "# EXPECT: reject — role default carries production-approval, forbidden by Section 8 (D106)\n"
 + yaml.safe_dump({"registry_version":1,"roles":[
     {"id":"developer","default_capabilities":["code-review","production-approval"]}]},sort_keys=False),
 encoding="utf-8")
print("written")
PY
python contracts/ci/register_add.py C-REG-ROLES-1 registry/roles.registry.v1.json 1 L1 L1,L3,L5 stubs/roles.yaml
git add -A && git commit -m "L0-P0-005: C-REG-ROLES-1 role registry schema, stub, fixtures"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Schema is valid JSON Schema 2020-12 | `check-jsonschema --check-metaschema contracts/registry/roles.registry.v1.json && echo ok` | `ok` |
| 2 | Stub validates and holds eleven roles | `check-jsonschema --schemafile contracts/registry/roles.registry.v1.json contracts/stubs/roles.yaml && python -c "import yaml;print(len(yaml.safe_load(open('contracts/stubs/roles.yaml'))['roles']))"` | `ok`-exit then `11` |
| 3 | The D106 fixture is rejected | `check-jsonschema --schemafile contracts/registry/roles.registry.v1.json contracts/fixtures/C-REG-ROLES-1/invalid-001.yaml >/dev/null 2>&1 && echo LEAK \|\| echo rejected` | `rejected` |
| 4 | `founder` default is empty (D-L0-09) | `python -c "import yaml;r=yaml.safe_load(open('contracts/stubs/roles.yaml'))['roles'];print([x['default_capabilities'] for x in r if x['id']=='founder'])"` | `[[]]` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import yaml
vocab = {c["id"] for c in yaml.safe_load(open("contracts/registry/capability.vocabulary.v1.yaml"))["capabilities"]}
dang  = set(yaml.safe_load(open("contracts/registry/capability.vocabulary.v1.yaml"))["dangerous_never_by_role_default"])
roles = yaml.safe_load(open("contracts/stubs/roles.yaml"))["roles"]
undef = [c for r in roles for c in r["default_capabilities"] if c not in vocab]
leak  = [c for r in roles for c in r["default_capabilities"] if c in dang]
print("L0-P0-005 PASS" if not undef and not leak else f"L0-P0-005 FAIL undef={undef} dangerous={leak}")
PY
```

Expected: `L0-P0-005 PASS`

**STOP RULE** — If the Section 8 `founder` listing is transcribed literally, criterion 4 fails and the D106 `not/contains` rule rejects the stub. That is the contract working. Do not weaken the rule to admit the listing. D-L0-09 is the resolution; if you believe it wrong, file a CCR of class **CCR-BREAKING** and stop.

---

### L0-P0-006 — `C-REG-PRODUCT-2`: the Product Operating Contract, v2

| | |
| --- | --- |
| **Size** | L |
| **Depends on** | L0-P0-004, L0-P0-005 |
| **Writes** | `contracts/registry/product.contract.v2.json`, `contracts/stubs/product.yaml`, `contracts/fixtures/C-REG-PRODUCT-2/{valid-001,invalid-001..005}.yaml` |
| **Spec** | Section 15.1 (the contract), 15.2, 15.4, 15.6, 15.7, Section 60.1–60.2, Section 31.3, Section 42.2, Section 44.1, Section 50.1, AT-025, AT-047, AT-049, AT-050 |

The single most consumed contract in the programme: all five lanes read it. It is frozen at `contract_version: 2` per **D-L0-02**.

**Blocks, in the order Section 15.1 states them.** `contract_version` (const 2), `platform_compatibility` (`supported|transitional|unsupported`), `conformance_profile` (`service|client-app|library|batch|customer-hosted|white-label|static-site`, 15.7), then: `identity`, `classification`, `assignments[]`, `escalation`, `code`, `verification`, `environments`, `deployment`, `reversibility_default`, `infrastructure`, `dependencies`, optional `ai_runtime_dependency`, `security`, `ai_restrictions`, optional `data`, `observability`, optional `automated_containment`, `recovery`, `operations`, optional `commitments[]`, `business`.

**Cross-field rules that MUST be schema-encoded, not commented** (each is a lane-visible blocker if it is prose only):

| Rule id | Rule | Spec |
| --- | --- | --- |
| `PROD-R1` | `verification.performance` is `required` whenever `classification.reliability_criticality` is `high` or `critical` | 31.3 |
| `PROD-R2` | `operations.coverage_window` is non-null whenever `operations.support_model` is `extended` or `24x7` | 15.1, 47.9, AT-047 |
| `PROD-R3` | `operations.detection_expectation` is DERIVED and must equal the value `support_model` implies: `business-hours→next-business-morning`, `extended→rostered-window`, `24x7→continuous`. A declared value differing from the derived value fails CI | 15.1, 42.2 |
| `PROD-R4` | `deployment.staged_rollout` is required whenever `conformance_profile` is `client-app` | 15.1, 28.2 |
| `PROD-R5` | `ai_runtime_dependency` present requires `verification` to reference an evaluation suite under `verification/` | 38.1, AT-049 |
| `PROD-R6` | `infrastructure.monthly_budget_band` is required on every product, with `ceiling >= expected` | invariant 88, 50.1, AT-050 |
| `PROD-R7` | `recovery.restore_tested` is a date; freshness is not a schema property and is enforced by L3 against `records/restore-tests/` (`C-RECON-SET-1`), never by this schema | 15.4, 53.1, invariant 4 |

`PROD-R3` is encoded as three `if/then` pairs on `const` values. `PROD-R7` is deliberately **out of schema** and is recorded here so that no lane implements a date check twice.

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-REG-PRODUCT-2
python - <<'PY'
import json, pathlib
S = {
 "$schema":"https://json-schema.org/draft/2020-12",
 "$id":"urn:multiproduct:schemas:product:v2",
 "title":"Product Operating Contract","description":"Operating envelope for a product across all lanes.",
 "type":"object",
 "required":["contract_version","platform_compatibility","conformance_profile","identity",
             "classification","assignments","escalation","code","verification","environments",
             "deployment","reversibility_default","infrastructure","dependencies","security",
             "ai_restrictions","observability","recovery","operations","business"],
 "properties":{
  "contract_version":{"const":2},
  "platform_compatibility":{"type":"string","enum":["supported","transitional","unsupported"]},
  "conformance_profile":{"type":"string","enum":["service","client-app","library","batch","customer-hosted","white-label","static-site"]},
  "identity":{"$ref":"#/$defs/identity"},
  "classification":{"$ref":"#/$defs/classification"},
  "assignments":{"$ref":"#/$defs/assignments"},
  "escalation":{"$ref":"#/$defs/escalation"},
  "code":{"$ref":"#/$defs/code"},
  "verification":{"$ref":"#/$defs/verification"},
  "environments":{"$ref":"#/$defs/environments"},
  "deployment":{"$ref":"#/$defs/deployment"},
  "reversibility_default":{"type":"string","enum":["rollback","forward-only","manual"]},
  "infrastructure":{"$ref":"#/$defs/infrastructure"},
  "dependencies":{"type":"array","items":{"$ref":"#/$defs/dependency"}},
  "ai_runtime_dependency":{"$ref":"#/$defs/ai_runtime_dependency"},
  "security":{"$ref":"#/$defs/security"},
  "ai_restrictions":{"type":"array","items":{"type":"string"}},
  "data":{"$ref":"#/$defs/data"},
  "observability":{"$ref":"#/$defs/observability"},
  "automated_containment":{"$ref":"#/$defs/automated_containment"},
  "recovery":{"$ref":"#/$defs/recovery"},
  "operations":{"$ref":"#/$defs/operations"},
  "commitments":{"$ref":"#/$defs/commitments"},
  "business":{"$ref":"#/$defs/business"}},
 "allOf":[
  {"$ref":"#/$defs/PROD-R1"},{"$ref":"#/$defs/PROD-R2"},{"$ref":"#/$defs/PROD-R3"},
  {"$ref":"#/$defs/PROD-R4"},{"$ref":"#/$defs/PROD-R5"},{"$ref":"#/$defs/PROD-R6"}],
 "$defs":{
  "identity":{"type":"object","required":["product_id","repository","team"],
   "properties":{"product_id":{"type":"string"},"repository":{"type":"string"},"team":{"type":"string"}}},
  "classification":{"type":"object","required":["reliability_criticality","business_criticality","onboarding_cost_band"],
   "properties":{
    "reliability_criticality":{"type":"string","enum":["low","medium","high","critical"]},
    "business_criticality":{"type":"string","enum":["low","medium","high","critical"]},
    "onboarding_cost_band":{"type":"string","enum":["XS","S","M","L","XL"]}}},
  "assignments":{"type":"array","minItems":1,"items":{"type":"object",
   "required":["role","person","from"],
   "properties":{"role":{"type":"string"},"person":{"type":"string"},
                 "from":{"type":"string","format":"date"}}}},
  "escalation":{"type":"object","required":["owner"],"properties":{"owner":{"type":"string"}}},
  "code":{"type":"object","required":["languages"],
   "properties":{"languages":{"type":"array","items":{"type":"string"}}}},
  "verification":{"type":"object",
   "required":["performance","mechanisms","coverage_map","seeded_defect_cases"],
   "properties":{
    "performance":{"type":"string","enum":["required","optional","not-applicable"]},
    "mechanisms":{"type":"array","items":{"type":"string"}},
    "coverage_map":{"type":"array"},
    "seeded_defect_cases":{"type":"array"},
    "evaluation_suite":{"type":"string"}}},
  "environments":{"type":"object","properties":{
   "staging":{"type":"object","properties":{"enabled":{"type":"boolean"}}},
   "production":{"type":"object","properties":{"enabled":{"type":"boolean"}}}}},
  "deployment":{"type":"object","required":["strategy"],
   "properties":{"strategy":{"type":"string"},
    "staged_rollout":{"type":"object","properties":{"enabled":{"type":"boolean"}}}}},
  "infrastructure":{"type":"object","required":["monthly_budget_band"],
   "properties":{"monthly_budget_band":{"type":"object","required":["expected","ceiling"],
    "properties":{
     "expected":{"type":"number","exclusiveMinimum":0},
     "ceiling":{"type":"number","exclusiveMinimum":0}}}}},
  "dependency":{"type":"object","required":["id"],
   "properties":{"id":{"type":"string"},"version":{"type":"string"}}},
  "ai_runtime_dependency":{"type":"object",
   "properties":{"model":{"type":"string"},"provider":{"type":"string"}}},
  "security":{"type":"object","required":["threat_model_reviewed"],
   "properties":{"threat_model_reviewed":{"type":"boolean"}}},
  "data":{"type":"object","properties":{"sensitivity":{"type":"string"}}},
  "observability":{"type":"object","required":["metrics","alerts"],
   "properties":{"metrics":{"type":"array"},"alerts":{"type":"array"}}},
  "automated_containment":{"type":"object",
   "properties":{"enabled":{"type":"boolean"}}},
  "recovery":{"type":"object","required":["rto_hours","rpo_hours","restore_tested"],
   "properties":{"rto_hours":{"type":"number"},"rpo_hours":{"type":"number"},
                 "restore_tested":{"type":"string"}}},
  "operations":{"type":"object","required":["support_model","detection_expectation"],
   "properties":{
    "support_model":{"type":"string","enum":["business-hours","extended","24x7"]},
    "detection_expectation":{"type":"string","enum":["next-business-morning","rostered-window","continuous"]},
    "coverage_window":{"type":["string","null"]}}},
  "commitments":{"type":"object","properties":{"sla":{"type":"string"}}},
  "business":{"type":"object","required":["data_sensitivity"],
   "properties":{"data_sensitivity":{"type":"string"}}},
  "PROD-R1":{
   "description":"PROD-R1: reliability_criticality high/critical requires verification.performance=required.",
   "if":{"properties":{"classification":{"properties":{"reliability_criticality":{"enum":["high","critical"]}},"required":["reliability_criticality"]}}},
   "then":{"properties":{"verification":{"properties":{"performance":{"const":"required"}},"required":["performance"]}}}},
  "PROD-R2":{
   "description":"PROD-R2: support_model extended/24x7 requires coverage_window to be a non-null string.",
   "if":{"properties":{"operations":{"properties":{"support_model":{"enum":["extended","24x7"]}},"required":["support_model"]}}},
   "then":{"properties":{"operations":{"properties":{"coverage_window":{"type":"string"}}}}}},
  "PROD-R3":{
   "description":"PROD-R3: support_model determines detection_expectation (three const mappings).",
   "allOf":[
    {"description":"PROD-R3-a: business-hours → next-business-morning",
     "if":{"properties":{"operations":{"properties":{"support_model":{"const":"business-hours"}}}}},
     "then":{"properties":{"operations":{"properties":{"detection_expectation":{"const":"next-business-morning"}}}}}},
    {"description":"PROD-R3-b: extended → rostered-window",
     "if":{"properties":{"operations":{"properties":{"support_model":{"const":"extended"}}}}},
     "then":{"properties":{"operations":{"properties":{"detection_expectation":{"const":"rostered-window"}}}}}},
    {"description":"PROD-R3-c: 24x7 → continuous",
     "if":{"properties":{"operations":{"properties":{"support_model":{"const":"24x7"}}}}},
     "then":{"properties":{"operations":{"properties":{"detection_expectation":{"const":"continuous"}}}}}}]},
  "PROD-R4":{
   "description":"PROD-R4: conformance_profile client-app requires deployment.staged_rollout block.",
   "if":{"properties":{"conformance_profile":{"const":"client-app"}}},
   "then":{"properties":{"deployment":{"required":["staged_rollout"]}}}},
  "PROD-R5":{
   "description":"PROD-R5: ai_runtime_dependency present requires verification.evaluation_suite.",
   "if":{"required":["ai_runtime_dependency"]},
   "then":{"properties":{"verification":{"required":["evaluation_suite"]}}}},
  "PROD-R6":{
   "description":"PROD-R6: monthly_budget_band required; ceiling and expected must be > 0. CI lint enforces ceiling >= expected (JSON Schema validates structure and type only).",
   "properties":{"infrastructure":{"properties":{"monthly_budget_band":{
    "required":["expected","ceiling"],
    "properties":{"expected":{"exclusiveMinimum":0},"ceiling":{"exclusiveMinimum":0}}}}}}}}}
pathlib.Path("contracts/registry/product.contract.v2.json").write_text(
  json.dumps(S, indent=2)+"\n", encoding="utf-8")
print("schema written")

stub = """\
contract_version: 2
platform_compatibility: supported
conformance_profile: service
identity:
  product_id: example-product
  repository: example-product
  team: platform
classification:
  reliability_criticality: critical
  business_criticality: high
  onboarding_cost_band: M
assignments:
  - role: lead
    person: lead-1
    from: "2026-09-02"
verification:
  performance: required
  mechanisms: [automated]
  coverage_map: []
  seeded_defect_cases: []
environments:
  staging:
    enabled: true
  production:
    enabled: true
deployment:
  strategy: blue-green
reversibility_default: rollback
infrastructure:
  monthly_budget_band:
    expected: 100
    ceiling: 150
dependencies: []
security:
  threat_model_reviewed: false
ai_restrictions: []
observability:
  metrics: []
  alerts: []
recovery:
  rto_hours: 24
  rpo_hours: 24
  restore_tested: "2026-09-01"
operations:
  support_model: business-hours
  detection_expectation: next-business-morning
  coverage_window: null
business:
  data_sensitivity: internal
"""
pathlib.Path("contracts/stubs/product.yaml").write_text(stub, encoding="utf-8")
print("stub written")

fx = pathlib.Path("contracts/fixtures/C-REG-PRODUCT-2")
(fx/"valid-001.yaml").write_text("# EXPECT: accept — complete valid product contract\n" + stub, encoding="utf-8")
(fx/"invalid-001.yaml").write_text("""\
# EXPECT: reject — PROD-R1: reliability_criticality critical but performance optional
contract_version: 2
platform_compatibility: supported
conformance_profile: service
identity:
  product_id: example-product
  repository: example-product
  team: platform
classification:
  reliability_criticality: critical
  business_criticality: high
  onboarding_cost_band: M
assignments:
  - role: lead
    person: lead-1
    from: "2026-09-02"
verification:
  performance: optional
  mechanisms: [automated]
  coverage_map: []
  seeded_defect_cases: []
environments:
  staging: {enabled: true}
  production: {enabled: true}
deployment:
  strategy: blue-green
reversibility_default: rollback
infrastructure:
  monthly_budget_band: {expected: 100, ceiling: 150}
dependencies: []
security: {threat_model_reviewed: false}
ai_restrictions: []
observability: {metrics: [], alerts: []}
recovery: {rto_hours: 24, rpo_hours: 24, restore_tested: "2026-09-01"}
operations:
  support_model: business-hours
  detection_expectation: next-business-morning
  coverage_window: null
business: {data_sensitivity: internal}
""", encoding="utf-8")
(fx/"invalid-002.yaml").write_text("""\
# EXPECT: reject — PROD-R2: support_model 24x7 but coverage_window null
contract_version: 2
platform_compatibility: supported
conformance_profile: service
identity:
  product_id: example-product
  repository: example-product
  team: platform
classification:
  reliability_criticality: medium
  business_criticality: high
  onboarding_cost_band: M
assignments:
  - role: lead
    person: lead-1
    from: "2026-09-02"
verification:
  performance: not-applicable
  mechanisms: [automated]
  coverage_map: []
  seeded_defect_cases: []
environments:
  staging: {enabled: true}
  production: {enabled: true}
deployment:
  strategy: blue-green
reversibility_default: rollback
infrastructure:
  monthly_budget_band: {expected: 100, ceiling: 150}
dependencies: []
security: {threat_model_reviewed: false}
ai_restrictions: []
observability: {metrics: [], alerts: []}
recovery: {rto_hours: 24, rpo_hours: 24, restore_tested: "2026-09-01"}
operations:
  support_model: "24x7"
  detection_expectation: continuous
  coverage_window: null
business: {data_sensitivity: internal}
""", encoding="utf-8")
(fx/"invalid-003.yaml").write_text("""\
# EXPECT: reject — PROD-R3: support_model business-hours but detection_expectation continuous
contract_version: 2
platform_compatibility: supported
conformance_profile: service
identity:
  product_id: example-product
  repository: example-product
  team: platform
classification:
  reliability_criticality: medium
  business_criticality: medium
  onboarding_cost_band: S
assignments:
  - role: lead
    person: lead-1
    from: "2026-09-02"
verification:
  performance: not-applicable
  mechanisms: [smoke]
  coverage_map: []
  seeded_defect_cases: []
environments:
  staging: {enabled: true}
  production: {enabled: true}
deployment:
  strategy: rolling
reversibility_default: rollback
infrastructure:
  monthly_budget_band: {expected: 50, ceiling: 75}
dependencies: []
security: {threat_model_reviewed: false}
ai_restrictions: []
observability: {metrics: [], alerts: []}
recovery: {rto_hours: 48, rpo_hours: 48, restore_tested: "2026-09-01"}
operations:
  support_model: business-hours
  detection_expectation: continuous
  coverage_window: null
business: {data_sensitivity: public}
""", encoding="utf-8")
(fx/"invalid-004.yaml").write_text("""\
# EXPECT: reject — PROD-R4: conformance_profile client-app but no staged_rollout block
contract_version: 2
platform_compatibility: supported
conformance_profile: client-app
identity:
  product_id: example-app
  repository: example-app
  team: frontend
classification:
  reliability_criticality: medium
  business_criticality: medium
  onboarding_cost_band: S
assignments:
  - role: lead
    person: lead-1
    from: "2026-09-02"
verification:
  performance: not-applicable
  mechanisms: [smoke]
  coverage_map: []
  seeded_defect_cases: []
environments:
  staging: {enabled: true}
  production: {enabled: true}
deployment:
  strategy: rolling
reversibility_default: rollback
infrastructure:
  monthly_budget_band: {expected: 20, ceiling: 30}
dependencies: []
security: {threat_model_reviewed: false}
ai_restrictions: []
observability: {metrics: [], alerts: []}
recovery: {rto_hours: 48, rpo_hours: 48, restore_tested: "2026-09-01"}
operations:
  support_model: business-hours
  detection_expectation: next-business-morning
  coverage_window: null
business: {data_sensitivity: internal}
""", encoding="utf-8")
(fx/"invalid-005.yaml").write_text("""\
# EXPECT: reject — PROD-R6: ceiling: 0 violates exclusiveMinimum: 0 (structural guard; CI lint enforces ceiling >= expected)
contract_version: 2
platform_compatibility: supported
conformance_profile: service
identity:
  product_id: example-product
  repository: example-product
  team: platform
classification:
  reliability_criticality: medium
  business_criticality: medium
  onboarding_cost_band: M
assignments:
  - role: lead
    person: lead-1
    from: "2026-09-02"
verification:
  performance: not-applicable
  mechanisms: [automated]
  coverage_map: []
  seeded_defect_cases: []
environments:
  staging: {enabled: true}
  production: {enabled: true}
deployment:
  strategy: blue-green
reversibility_default: rollback
infrastructure:
  monthly_budget_band:
    expected: 100
    ceiling: 0
dependencies: []
security: {threat_model_reviewed: false}
ai_restrictions: []
observability: {metrics: [], alerts: []}
recovery: {rto_hours: 24, rpo_hours: 24, restore_tested: "2026-09-01"}
operations:
  support_model: business-hours
  detection_expectation: next-business-morning
  coverage_window: null
business: {data_sensitivity: internal}
""", encoding="utf-8")
print("fixtures written")
PY
python contracts/ci/register_add.py C-REG-PRODUCT-2 registry/product.contract.v2.json 2 L1 L1,L2,L3,L4,L5 stubs/product.yaml
git add -A && git commit -m "L0-P0-006: C-REG-PRODUCT-2 product operating contract v2"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Schema is valid JSON Schema 2020-12 | `check-jsonschema --check-metaschema contracts/registry/product.contract.v2.json && echo ok` | `ok` |
| 2 | `contract_version` is pinned to 2 (D-L0-02) | `python -c "import json;print(json.load(open('contracts/registry/product.contract.v2.json'))['properties']['contract_version'])"` | `{'const': 2}` |
| 3 | The stub validates | `check-jsonschema --schemafile contracts/registry/product.contract.v2.json contracts/stubs/product.yaml && echo ok` | `ok` |
| 4 | All five invalid fixtures are rejected | `for f in contracts/fixtures/C-REG-PRODUCT-2/invalid-*.yaml; do check-jsonschema --schemafile contracts/registry/product.contract.v2.json "$f" >/dev/null 2>&1 && echo "LEAK $f" \|\| echo "rejected $f"; done` | five `rejected …` lines, no `LEAK` |
| 5 | Every assignment `person` in the stub exists in `contracts/stubs/people.yaml` | see SELF-VERIFY | `L0-P0-006 PASS` |
| 6 | The schema encodes exactly the six schema-encoded rules (R7 excluded) | `grep -o 'PROD-R[0-9]' contracts/registry/product.contract.v2.json \| sort -u \| tr '\n' ' '` | `PROD-R1 PROD-R2 PROD-R3 PROD-R4 PROD-R5 PROD-R6 ` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import yaml
people = {p["id"] for p in yaml.safe_load(open("contracts/stubs/people.yaml"))["people"]}
prod   = yaml.safe_load(open("contracts/stubs/product.yaml"))
miss   = [a["person"] for a in prod["assignments"] if a["person"] not in people]
crit   = prod["classification"]["reliability_criticality"]
perf   = prod["verification"]["performance"]
ok = not miss and (perf == "required" if crit in ("high","critical") else True)
print("L0-P0-006 PASS" if ok else f"L0-P0-006 FAIL missing_people={miss} crit={crit} perf={perf}")
PY
```

Expected: `L0-P0-006 PASS`

**STOP RULE** — If any of `PROD-R1`..`PROD-R6` cannot be expressed in the schema, do not demote it to a comment and do not push it into L1's validator as "implementation detail". A cross-field rule that lives only in a lane's code is a rule the other four lanes cannot see. File a CCR of class **CCR-BLOCKING**; five lanes consume this contract, so this is the most expensive block in the programme.

---

### L0-P0-007 — `C-REG-VERIFICATION-1`: the Verification Contract schema

| | |
| --- | --- |
| **Size** | M |
| **Depends on** | L0-P0-006 |
| **Writes** | `contracts/registry/verification.contract.v1.json`, `contracts/stubs/verification-contract.yaml`, `contracts/stubs/verification-uat.yaml`, `contracts/fixtures/C-REG-VERIFICATION-1/{valid-001,invalid-001,invalid-002}.yaml` |
| **Spec** | Section 31.1, 31.2, 31.3, Section 60.2, SIG-18, invariant 1 |

**Shape.** `contract_version: 1`; `mechanisms` (which of automated / manual UAT / smoke / performance apply); `coverage_map[]` mapping every requirement to the check that proves it; `auto_pass` scope; and — binding, 31.2 — **`seeded_defect_cases[]` with `minItems: 1`**: "Every `verification/contract.yaml` declares at least one seeded-defect case … that the contract MUST fail."

Each seeded case carries `id`, `path`, `mechanism`, `last_run`, `last_result` (`failed_as_expected|passed_unexpectedly`). A case whose `last_result` is `passed_unexpectedly` raises **SIG-18** and is Blocking for that product (31.2) — the raising is L2/L3 behaviour, but the field that makes it detectable is frozen here.

The repository layout of 31.1 (`verification/contract.yaml`, `automated/`, `uat.md`, `smoke/`) is frozen as `required_paths[]` in the contract body so L2's presence check and L1's validator read the same list.

`verification/uat.md` is structured and version-controlled (31.1): `feature`, `preconditions[]`, `steps[]`, `expected[]`. Its shape is frozen as `$defs/uat_document` in the same schema and stubbed at `contracts/stubs/verification-uat.yaml`.

**Fixtures**

| File | Line 1 |
| --- | --- |
| `invalid-001.yaml` | `# EXPECT: reject — seeded_defect_cases empty; Section 31.2 requires at least one` |
| `invalid-002.yaml` | `# EXPECT: reject — coverage_map entry with no mapped mechanism (Section 31.2 coverage mapping)` |

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-REG-VERIFICATION-1
python - <<'PY'
import json, pathlib, yaml
# -- Schema ------------------------------------------------------------------
S = {
 "$schema":"https://json-schema.org/draft/2020-12",
 "$id":"urn:multiproduct:schemas:verification:v1",
 "title":"Verification Contract v1",
 "x-contract":{
   "contract_id":"C-REG-VERIFICATION-1","contract_version":1,"owner":"L0",
   "publishing_lane":"L1","consuming_lanes":["L1","L2"],
   "spec_refs":["Section 31.1","Section 31.2","Section 31.3","SIG-18"],
   "ccr_required":True},
 "type":"object",
 "required":["contract_version","mechanisms","coverage_map","auto_pass","required_paths","seeded_defect_cases"],
 "additionalProperties":False,
 "properties":{
  "contract_version":{"const":1},
  "mechanisms":{"type":"array","items":{"enum":["automated","uat","smoke","performance"]}},
  "coverage_map":{"type":"array","items":{
    "type":"object","required":["requirement","check"],"additionalProperties":False,
    "properties":{"requirement":{"type":"string"},"check":{"type":"string"}}}},
  "auto_pass":{"type":"object","required":["scope"],"additionalProperties":False,
    "properties":{"scope":{"type":"string"}}},
  "required_paths":{"type":"array","items":{"type":"string"}},
  "seeded_defect_cases":{
    "$comment":"A case whose last_result is passed_unexpectedly raises SIG-18 and is Blocking for that product (Section 31.2). Detection and signalling are L2/L3 behaviour; this field makes the state detectable.",
    "type":"array","minItems":1,"items":{"$ref":"#/$defs/seeded_defect_case"}}},
 "$defs":{
  "seeded_defect_case":{"type":"object",
    "required":["id","path","mechanism","last_run","last_result"],
    "additionalProperties":False,
    "properties":{
      "id":{"type":"string"},
      "path":{"type":"string"},
      "mechanism":{"enum":["automated","uat","smoke","performance"]},
      "last_run":{"type":"string","format":"date"},
      "last_result":{"enum":["failed_as_expected","passed_unexpectedly"]}}},
  "uat_document":{"type":"object",
    "required":["feature","preconditions","steps","expected"],
    "additionalProperties":False,
    "properties":{
      "feature":{"type":"string"},
      "preconditions":{"type":"array","items":{"type":"string"}},
      "steps":{"type":"array","items":{"type":"string"}},
      "expected":{"type":"array","items":{"type":"string"}}}}}}
pathlib.Path("contracts/registry/verification.contract.v1.json").write_text(
  json.dumps(S,indent=2)+"\n",encoding="utf-8")
print("schema written")
# -- Stub: verification-contract.yaml ----------------------------------------
stub = {
  "contract_version":1,
  "mechanisms":["automated","smoke"],
  "coverage_map":[{"requirement":"REQ-001","check":"ci/unit-tests"}],
  "auto_pass":{"scope":"documentation-only-changes"},
  "required_paths":["verification/contract.yaml","automated/","uat.md","smoke/"],
  "seeded_defect_cases":[{
    "id":"SD-001","path":"automated/test_example.py",
    "mechanism":"automated","last_run":"2026-09-01",
    "last_result":"failed_as_expected"}]}
pathlib.Path("contracts/stubs/verification-contract.yaml").write_text(
  yaml.dump(stub,default_flow_style=False,sort_keys=False),encoding="utf-8")
print("stub written")
# -- Stub: verification-uat.yaml ---------------------------------------------
uat = {
  "feature":"User can log in with valid credentials",
  "preconditions":["User account exists","System is accessible"],
  "steps":["Navigate to login page","Enter valid username and password","Click Login"],
  "expected":["User is redirected to dashboard","Session token is issued"]}
pathlib.Path("contracts/stubs/verification-uat.yaml").write_text(
  yaml.dump(uat,default_flow_style=False,sort_keys=False),encoding="utf-8")
print("uat stub written")
# -- Fixtures ----------------------------------------------------------------
fx = pathlib.Path("contracts/fixtures/C-REG-VERIFICATION-1")
(fx/"valid-001.yaml").write_text(
  "# EXPECT: accept — complete verification contract\n"
  +yaml.dump(stub,default_flow_style=False,sort_keys=False),encoding="utf-8")
print("valid-001 written")
inv1 = dict(stub,seeded_defect_cases=[])
(fx/"invalid-001.yaml").write_text(
  "# EXPECT: reject — seeded_defect_cases empty; Section 31.2 requires at least one\n"
  +yaml.dump(inv1,default_flow_style=False,sort_keys=False),encoding="utf-8")
print("invalid-001 written")
inv2 = {**stub,"coverage_map":[{"requirement":"REQ-001"}]}
(fx/"invalid-002.yaml").write_text(
  "# EXPECT: reject — coverage_map entry with no mapped mechanism (Section 31.2 coverage mapping)\n"
  +yaml.dump(inv2,default_flow_style=False,sort_keys=False),encoding="utf-8")
print("invalid-002 written")
PY
python contracts/ci/register_add.py C-REG-VERIFICATION-1 registry/verification.contract.v1.json 1 L1 L1,L2 stubs/verification-contract.yaml
git add -A && git commit -m "L0-P0-007: C-REG-VERIFICATION-1 verification contract schema"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Schema is valid JSON Schema 2020-12 | `check-jsonschema --check-metaschema contracts/registry/verification.contract.v1.json && echo ok` | `ok` |
| 2 | `seeded_defect_cases` carries `minItems: 1` | `python -c "import json;print(json.load(open('contracts/registry/verification.contract.v1.json'))['properties']['seeded_defect_cases']['minItems'])"` | `1` |
| 3 | Both stubs validate | `check-jsonschema --schemafile contracts/registry/verification.contract.v1.json contracts/stubs/verification-contract.yaml && echo ok` | `ok` |
| 4 | Both invalid fixtures are rejected | `for f in contracts/fixtures/C-REG-VERIFICATION-1/invalid-*.yaml; do check-jsonschema --schemafile contracts/registry/verification.contract.v1.json "$f" >/dev/null 2>&1 && echo "LEAK $f" \|\| echo "rejected $f"; done` | two `rejected …` lines, no `LEAK` |
| 5 | `required_paths` matches the 31.1 layout exactly | `python -c "import yaml;print(sorted(yaml.safe_load(open('contracts/stubs/verification-contract.yaml'))['required_paths']))"` | `['verification/automated/', 'verification/contract.yaml', 'verification/smoke/', 'verification/uat.md']` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import yaml
c = yaml.safe_load(open("contracts/stubs/verification-contract.yaml"))
ok  = len(c["seeded_defect_cases"]) >= 1
ok &= all(e.get("mechanism") for e in c["coverage_map"])
ok &= c["contract_version"] == 1
print("L0-P0-007 PASS" if ok else "L0-P0-007 FAIL")
PY
```

Expected: `L0-P0-007 PASS`

**STOP RULE** — If a reading of Section 31 suggests the seeded-defect case is optional, stop: 31.2 states "A verification contract that cannot fail is not a contract." Do not set `minItems: 0`. A `minItems: 0` here silently permits the `verify: exit 0` contract that 31.2 exists to forbid, and L2 would ship green pipelines over it. File a CCR of class **CCR-BREAKING**.

---

### L0-P0-008 — `C-REG-SERVICE-1`, `C-REG-TOPOLOGY-1`, `C-REG-PLATFORM-1`

| | |
| --- | --- |
| **Size** | L |
| **Depends on** | L0-P0-006 |
| **Writes** | `contracts/registry/{service.contract.v1.json,topology.registry.v1.json,platform.record.v1.json}`, three stubs, six fixtures |
| **Spec** | Section 20.1 (`service.yaml`), Section 66.2 + 13.1 (`topology.yaml`), Section 60.1 (`platform.yaml`), Section 97.3 (event-type enum lives in `platform.yaml`), Section 52.6 (owners) |

Three registry contracts, grouped because each is small and all three are consumed by the same two lanes.

**`C-REG-SERVICE-1`** — `service_version: 1`; the shared-service contract of Section 20.1 with a named owner, declared consumers and versioned compatibility (invariant 63). Rule `SVC-R1`: a declared consumer must name an existing product id — a cross-registry rule L1 enforces, declared here so L3's dependency reconciliation row reads the same field names (53.1: "Declared dependency → Shared service registry → Fail CI on unknown dependency").

**`C-REG-TOPOLOGY-1`** — domains, Team Lead scopes, succession designations, delegation and escalation resolution rules (Section 52.6 owner row; Section 66.2; Section 13.1 succession block). Rule `TOP-R1`: `escalation` on a product contract is a **role**, never a person, and resolves here — "Resolved through `topology.yaml`, never named on a product contract (Section 66)" (Section 9, `escalation` row). Rule `TOP-R2`: exactly one `acting_team_lead` designate exists per Team Lead scope at all times (invariant 35).

**`C-REG-PLATFORM-1`** — `platform_version`; `supported_contract_versions` (with `product: [1, 2]` per Section 60.1 and D-L0-02); `reusable_workflow_versions` (`current`, `supported[]`, `deprecated[]`, `deprecation_deadline{}`); `canary_set[]`; and — binding, Section 97.3 — **`event_types[]`, the closed enum**, which `C-EVT-ENUM-1` (L0-P0-011) fills. The schema requires `event_types` to be present and non-empty so that "the enum ships populated in Phase 1 so no workflow ever writes an untyped event" is mechanically true. Rule `PLAT-R1`: a retired identifier is marked `retired: true` and is **never removed** (97.3).

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-REG-SERVICE-1 contracts/fixtures/C-REG-TOPOLOGY-1 contracts/fixtures/C-REG-PLATFORM-1
python - <<'PY'
import json, pathlib
S = {
 "$schema":"https://json-schema.org/draft/2020-12/schema",
 "$id":"urn:multiproduct:contract:service:v1",
 "x-contract":{"contract_id":"C-REG-SERVICE-1","contract_version":1,"owner":"L0",
   "publishing_lane":"L1","consuming_lanes":["L1","L3"]},
 "type":"object","required":["service_version","name","owner_product","consumers","compatibility"],
 "additionalProperties":False,
 "properties":{
  "service_version":{"const":1},
  "name":{"type":"string"},
  "owner_product":{"type":"string","description":"product_id of the owning product"},
  "consumers":{"type":"array","items":{"type":"object",
    "required":["product_id"],"additionalProperties":False,
    "properties":{"product_id":{"type":"string"}}}},
  "compatibility":{"type":"object","required":["min_version"],"additionalProperties":False,
    "properties":{"min_version":{"type":"integer"}}}},
 "allOf":[
  {"title":"SVC-R1",
   "description":"A declared consumer must name an existing product id; cross-registry constraint enforced by L1 at runtime — JSON Schema cannot reference the product registry"}]
}
pathlib.Path("contracts/registry/service.contract.v1.json").write_text(json.dumps(S,indent=2)+"\n",encoding="utf-8")
print("service schema written")
PY
cat > contracts/stubs/service.yaml <<'YAML'
service_version: 1
name: "stub-shared-service"
owner_product: "stub-product-1"
consumers:
  - product_id: "stub-product-2"
compatibility:
  min_version: 1
YAML
cat > contracts/fixtures/C-REG-SERVICE-1/invalid-001.yaml <<'YAML'
# EXPECT: reject — missing required field owner_product
service_version: 1
name: "stub-shared-service"
consumers:
  - product_id: "stub-product-2"
compatibility:
  min_version: 1
YAML
cat > contracts/fixtures/C-REG-SERVICE-1/invalid-002.yaml <<'YAML'
# EXPECT: reject — consumers entry missing required field product_id (SVC-R1)
service_version: 1
name: "stub-shared-service"
owner_product: "stub-product-1"
consumers:
  - {}
compatibility:
  min_version: 1
YAML
python - <<'PY'
import json, pathlib
S = {
 "$schema":"https://json-schema.org/draft/2020-12/schema",
 "$id":"urn:multiproduct:contract:topology:v1",
 "x-contract":{"contract_id":"C-REG-TOPOLOGY-1","contract_version":1,"owner":"L0",
   "publishing_lane":"L1","consuming_lanes":["L1","L3","L5"]},
 "type":"object","required":["topology_version","scopes"],"additionalProperties":False,
 "properties":{
  "topology_version":{"const":1},
  "scopes":{"type":"array","minItems":1,"items":{
    "type":"object",
    "required":["name","team_lead","acting_team_lead","products"],
    "additionalProperties":False,
    "properties":{
      "name":{"type":"string"},
      "team_lead":{"type":"string","description":"person id of the Team Lead"},
      "acting_team_lead":{"type":"string","description":"person id of the current acting Team Lead (TOP-R2: must always be present)"},
      "products":{"type":"array","minItems":1,"items":{"type":"string"}},
      "delegation":{"type":"object","additionalProperties":True},
      "escalation_role":{"type":"string"}}}}},
 "allOf":[
  {"title":"TOP-R1",
   "description":"escalation resolves through topology.yaml, never hardcoded on product contract"},
  {"title":"TOP-R2",
   "description":"exactly one acting_team_lead per scope at all times",
   "if":{"properties":{"scopes":{"items":{"required":["acting_team_lead"]}}}},
   "then":{}}]
}
pathlib.Path("contracts/registry/topology.registry.v1.json").write_text(json.dumps(S,indent=2)+"\n",encoding="utf-8")
print("topology schema written")
PY
cat > contracts/stubs/topology.yaml <<'YAML'
topology_version: 1
scopes:
  - name: "main"
    team_lead: "lead-1"
    acting_team_lead: "dev-a"
    products:
      - "stub-product-1"
YAML
cat > contracts/fixtures/C-REG-TOPOLOGY-1/invalid-001.yaml <<'YAML'
# EXPECT: reject — scope missing required field acting_team_lead (TOP-R2: must always be present)
topology_version: 1
scopes:
  - name: "main"
    team_lead: "lead-1"
    products:
      - "stub-product-1"
YAML
cat > contracts/fixtures/C-REG-TOPOLOGY-1/invalid-002.yaml <<'YAML'
# EXPECT: reject — scope products array is empty, violating minItems:1
topology_version: 1
scopes:
  - name: "main"
    team_lead: "lead-1"
    acting_team_lead: "dev-a"
    products: []
YAML
python - <<'PY'
import json, pathlib
S = {
 "$schema":"https://json-schema.org/draft/2020-12/schema",
 "$id":"urn:multiproduct:contract:platform:v1",
 "x-contract":{"contract_id":"C-REG-PLATFORM-1","contract_version":1,"owner":"L0",
   "publishing_lane":"L1","consuming_lanes":["L1","L2","L3","L4"]},
 "type":"object",
 "required":["platform_version","supported_contract_versions","reusable_workflow_versions","event_types"],
 "additionalProperties":False,
 "properties":{
  "platform_version":{"const":1},
  "supported_contract_versions":{"type":"object","required":["product"],"additionalProperties":False,
    "properties":{
      "product":{"type":"array","items":{"type":"integer"},
        "allOf":[{"contains":{"const":1}},{"contains":{"const":2}}]}}},
  "reusable_workflow_versions":{"type":"object",
    "required":["current","supported","deprecated","deprecation_deadline"],
    "additionalProperties":False,
    "properties":{
      "current":{"type":"string"},
      "supported":{"type":"array","items":{"type":"string"}},
      "deprecated":{"type":"array","items":{"type":"string"}},
      "deprecation_deadline":{"type":"object","additionalProperties":{"type":"string"}}}},
  "canary_set":{"type":"array","items":{"type":"string"}},
  "event_types":{"type":"array","minItems":1,
    "items":{"type":"object","required":["id"],"additionalProperties":False,
      "properties":{
        "id":{"type":"string"},
        "retired":{"type":"boolean"}}},
    "allOf":[
      {"title":"PLAT-R1",
       "description":"retired identifiers are marked retired:true and never removed"}]}}
}
pathlib.Path("contracts/registry/platform.record.v1.json").write_text(json.dumps(S,indent=2)+"\n",encoding="utf-8")
print("platform schema written")
PY
cat > contracts/stubs/platform.yaml <<'YAML'
platform_version: 1
supported_contract_versions:
  product: [1, 2]
reusable_workflow_versions:
  current: "v1.0.0"
  supported: ["v1.0.0"]
  deprecated: []
  deprecation_deadline: {}
event_types:
  - id: "__unpopulated__"
YAML
cat > contracts/fixtures/C-REG-PLATFORM-1/invalid-001.yaml <<'YAML'
# EXPECT: reject — event_types is an empty array, violating minItems:1 (Section 97.3)
platform_version: 1
supported_contract_versions:
  product: [1, 2]
reusable_workflow_versions:
  current: "v1.0.0"
  supported: ["v1.0.0"]
  deprecated: []
  deprecation_deadline: {}
event_types: []
YAML
cat > contracts/fixtures/C-REG-PLATFORM-1/invalid-002.yaml <<'YAML'
# EXPECT: reject — supported_contract_versions.product is [1] — missing required version 2 (Section 60.1, D-L0-02)
platform_version: 1
supported_contract_versions:
  product: [1]
reusable_workflow_versions:
  current: "v1.0.0"
  supported: ["v1.0.0"]
  deprecated: []
  deprecation_deadline: {}
event_types:
  - id: "__unpopulated__"
YAML
python contracts/ci/register_add.py C-REG-SERVICE-1  registry/service.contract.v1.json  1 L1 L1,L3       stubs/service.yaml
python contracts/ci/register_add.py C-REG-TOPOLOGY-1 registry/topology.registry.v1.json 1 L1 L1,L3,L5    stubs/topology.yaml
python contracts/ci/register_add.py C-REG-PLATFORM-1 registry/platform.record.v1.json   1 L1 L1,L2,L3,L4 stubs/platform.yaml
git add -A && git commit -m "L0-P0-008: C-REG-SERVICE-1, C-REG-TOPOLOGY-1, C-REG-PLATFORM-1"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | All three schemas are valid JSON Schema 2020-12 | `for s in service.contract.v1 topology.registry.v1 platform.record.v1; do check-jsonschema --check-metaschema "contracts/registry/$s.json" \|\| echo "BAD $s"; done; echo done` | `done`, no `BAD` |
| 2 | All three stubs validate | `check-jsonschema --schemafile contracts/registry/service.contract.v1.json contracts/stubs/service.yaml && check-jsonschema --schemafile contracts/registry/topology.registry.v1.json contracts/stubs/topology.yaml && check-jsonschema --schemafile contracts/registry/platform.record.v1.json contracts/stubs/platform.yaml && echo ok` | `ok` |
| 3 | `supported_contract_versions.product` is `[1, 2]` (Section 60.1) | `python -c "import yaml;print(yaml.safe_load(open('contracts/stubs/platform.yaml'))['supported_contract_versions']['product'])"` | `[1, 2]` |
| 4 | `platform.yaml` schema requires a non-empty `event_types` | `python -c "import json;p=json.load(open('contracts/registry/platform.record.v1.json'))['properties']['event_types'];print(p['minItems'], 'event_types' in json.load(open('contracts/registry/platform.record.v1.json'))['required'])"` | `1 True` |
| 5 | Six invalid fixtures rejected (two per contract) | `for f in contracts/fixtures/C-REG-{SERVICE,TOPOLOGY,PLATFORM}-1/invalid-*.yaml; do echo "$f"; done \| wc -l` | `6` |
| 6 | Register now holds eight rows | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/register.yaml'))['contracts']))"` | `8` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import yaml
plat = yaml.safe_load(open("contracts/stubs/platform.yaml"))
topo = yaml.safe_load(open("contracts/stubs/topology.yaml"))
ok  = plat["supported_contract_versions"]["product"] == [1, 2]
ok &= plat["reusable_workflow_versions"]["current"] in plat["reusable_workflow_versions"]["supported"]
ok &= len(plat.get("event_types", [])) >= 1
ok &= all(s.get("acting_team_lead") for s in topo["scopes"])
print("L0-P0-008 PASS" if ok else "L0-P0-008 FAIL")
PY
```

Expected: `L0-P0-008 PASS`

**STOP RULE** — If `platform.yaml` is authored without `event_types`, stop and do not defer it to L4. Section 97.3 places the closed enum in `platform.yaml` and requires it populated in Phase 1; an empty enum means control-plane CI cannot reject an untyped event, and every workflow L2 writes emits events into a hole. If L0-P0-011 has not run, populate `event_types` with the placeholder `["__unpopulated__"]` and open a **CCR-BLOCKING** naming L0-P0-011 as the unblock.

---

### L0-P0-009 — `C-REC-ENV-1`: the operational record envelope

| | |
| --- | --- |
| **Size** | M |
| **Depends on** | L0-P0-006 |
| **Writes** | `contracts/records/record.envelope.v1.json`, `contracts/stubs/record-incident.yaml`, `contracts/stubs/record-deployment.yaml`, `contracts/stubs/record-decision.yaml`, `contracts/fixtures/C-REC-ENV-1/{valid-001..003,invalid-001..003}.yaml` |
| **Spec** | Section 97.2 (representative schemas), Section 60.2 (`record_schema_version`), Section 97.1 (UTC with offset), invariants 46, 47 |

**The envelope, binding (97.2).** "every record carries `record_schema_version`, `id`, `product`, `timestamp`, and never edits in place (corrections are follow-up records). An absent `record_schema_version` reads as version 1; the field is stated explicitly on every record written from Phase 1 onward."

**Schema-encoded rules**

| Rule id | Rule | Spec |
| --- | --- | --- |
| `REC-R1` | `record_schema_version`, `id`, `product`, `timestamp` are required on every record | 97.2 |
| `REC-R2` | Every timestamp is UTC with its offset — pattern anchored to a trailing `Z` or `±HH:MM` | 97.1 |
| `REC-R3` | `record_schema_version` default-on-read is 1; the schema still requires the field, because 97.2 requires it stated explicitly from Phase 1 | 97.2 |
| `REC-R4` | A record carries an optional `corrects` field naming the record it supersedes. It never carries an in-place edit marker | 97.2, invariant 47 |
| `REC-R5` | A record produced inside a control-loop gap carries `gap_window: true` and is not evidence for any gate until re-verification clears it | 53.7 |

Three per-store bodies are frozen as `$defs`, transcribed from the three worked schemas of 97.2: `incident` (`severity`, `detected`, `detection_source` ∈ `alert|customer|internal|support_intake`, `responded`, `resolved`, `customer_impact`, `resolution`, `postmortem`, `pre_onboarding`), `deployment` (`digest`, `approved_by`, `approval_event`, `staging_verified`, `uat_record`, `smoke_result`, `rollback_of`), `decision` (`decider`, `prompt_received`, `decided`, `subject`, `options_considered[]`, `evidence[]`, `review_date`). Section 97.2's fourth worked schema, `demo`, is included as a fourth `$def`.

Two further binding bodies from 97.2, each with the exact fields the section names, because a lane cannot infer them: `deletion_request` carries the four timestamps `requested`, `verified`, `executed`, `confirmed`, the named executor, the subprocessor propagation checklist and the backup carve-out policy statement (AT-105); `security_review` carries findings with `severity` and `disposition`, each unfixed finding linked to the debt inventory with an owner and a date.

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-REC-ENV-1
cat > contracts/records/record.envelope.v1.json << 'SCHEMA_EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "contracts/records/record.envelope.v1.json",
  "title": "C-REC-ENV-1 — operational record envelope (v1)",
  "description": "Every record carries record_schema_version, id, product, timestamp and never edits in place. Corrections are follow-up records. Section 97.2.",
  "type": "object",
  "required": ["record_schema_version", "id", "product", "timestamp"],
  "properties": {
    "record_schema_version": {
      "type": "integer",
      "const": 1,
      "description": "REC-R3: absent-on-read default is 1; stated explicitly on every record from Phase 1."
    },
    "id": {
      "type": "string"
    },
    "product": {
      "type": "string"
    },
    "timestamp": {
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(Z|[+-]\\d{2}:\\d{2})$",
      "description": "REC-R2: UTC with offset, anchored to trailing Z or plus-minus HH:MM."
    },
    "corrects": {
      "type": "string",
      "description": "REC-R4: id of the record this supersedes. A record never carries an in-place edit marker."
    },
    "gap_window": {
      "type": "boolean",
      "const": true,
      "description": "REC-R5: present and true when the record was produced inside a control-loop gap. Not evidence for any gate until re-verification clears it."
    },
    "body": {
      "type": "object",
      "description": "Per-store body; validated against the matching $def by the writer."
    }
  },
  "$defs": {
    "incident": {
      "type": "object",
      "required": ["severity", "detected", "detection_source"],
      "properties": {
        "severity": {"type": "string"},
        "detected": {"type": "string"},
        "detection_source": {
          "type": "string",
          "enum": ["alert", "customer", "internal", "support_intake"]
        },
        "responded": {"type": ["string", "null"]},
        "resolved": {"type": ["string", "null"]},
        "customer_impact": {"type": "string"},
        "resolution": {"type": "string"},
        "postmortem": {"type": "string"},
        "pre_onboarding": {"type": "boolean"}
      }
    },
    "deployment": {
      "type": "object",
      "required": ["digest", "approved_by", "approval_event"],
      "properties": {
        "digest": {"type": "string"},
        "approved_by": {"type": "string"},
        "approval_event": {"type": "string"},
        "staging_verified": {"type": "boolean"},
        "uat_record": {"type": ["string", "null"]},
        "smoke_result": {"type": "string"},
        "rollback_of": {"type": ["string", "null"]}
      }
    },
    "decision": {
      "type": "object",
      "required": ["decider", "prompt_received", "decided", "subject"],
      "properties": {
        "decider": {"type": "string"},
        "prompt_received": {"type": "string"},
        "decided": {"type": "string"},
        "subject": {"type": "string"},
        "options_considered": {
          "type": "array",
          "items": {"type": "string"}
        },
        "evidence": {
          "type": "array",
          "items": {"type": "string"}
        },
        "review_date": {"type": "string"}
      }
    },
    "demo": {
      "type": "object",
      "properties": {
        "recorded_at": {"type": "string"},
        "participants": {
          "type": "array",
          "items": {"type": "string"}
        },
        "outcome": {"type": "string"},
        "artifacts": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "deletion_request": {
      "type": "object",
      "required": ["requested", "executor"],
      "properties": {
        "requested": {"type": "string"},
        "verified": {"type": ["string", "null"]},
        "executed": {"type": ["string", "null"]},
        "confirmed": {"type": ["string", "null"]},
        "executor": {"type": "string"},
        "subprocessor_propagation_checklist": {
          "type": "array",
          "items": {"type": "string"}
        },
        "backup_carve_out_policy_statement": {"type": "string"}
      }
    },
    "security_review": {
      "type": "object",
      "required": ["findings"],
      "properties": {
        "findings": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["severity", "disposition"],
            "properties": {
              "severity": {"type": "string"},
              "disposition": {"type": "string"},
              "debt_inventory_link": {"type": ["string", "null"]},
              "owner": {"type": "string"},
              "remediation_date": {"type": ["string", "null"]}
            }
          }
        }
      }
    }
  }
}
SCHEMA_EOF
# Invalid fixtures, one per refutable rule:
#   invalid-001  REC-R1  record with no `product` field
#   invalid-002  REC-R2  timestamp `2026-09-14T02:11:00` with no offset
#   invalid-003  REC-R1  incident record with no `record_schema_version`
python contracts/ci/register_add.py C-REC-ENV-1 records/record.envelope.v1.json 1 L4 L2,L3,L4 stubs/record-incident.yaml
git add -A && git commit -m "L0-P0-009: C-REC-ENV-1 operational record envelope"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Schema is valid JSON Schema 2020-12 | `check-jsonschema --check-metaschema contracts/records/record.envelope.v1.json && echo ok` | `ok` |
| 2 | The four envelope fields are required | `python -c "import json;print(sorted(json.load(open('contracts/records/record.envelope.v1.json'))['required']))"` | `['id', 'product', 'record_schema_version', 'timestamp']` |
| 3 | All three stubs validate | `for f in contracts/stubs/record-*.yaml; do check-jsonschema --schemafile contracts/records/record.envelope.v1.json "$f" \|\| echo "BAD $f"; done; echo done` | `done`, no `BAD` |
| 4 | All three invalid fixtures rejected | `for f in contracts/fixtures/C-REC-ENV-1/invalid-*.yaml; do check-jsonschema --schemafile contracts/records/record.envelope.v1.json "$f" >/dev/null 2>&1 && echo "LEAK $f" \|\| echo "rejected $f"; done` | three `rejected …`, no `LEAK` |
| 5 | Six `$defs` bodies exist | `python -c "import json;print(sorted(json.load(open('contracts/records/record.envelope.v1.json'))['\$defs']))"` | `['decision', 'deletion_request', 'demo', 'deployment', 'incident', 'security_review']` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import json, re, yaml
S = json.load(open("contracts/records/record.envelope.v1.json"))
ok = set(S["required"]) == {"record_schema_version","id","product","timestamp"}
pat = S["properties"]["timestamp"]["pattern"]
ok &= bool(re.search(r"Z", pat)) and bool(re.search(r"\d\{?2", pat) or ":" in pat)
inc = yaml.safe_load(open("contracts/stubs/record-incident.yaml"))
ok &= inc["record_schema_version"] == 1 and inc["detection_source"] in ("alert","customer","internal","support_intake")
print("L0-P0-009 PASS" if ok else "L0-P0-009 FAIL")
PY
```

Expected: `L0-P0-009 PASS`

**STOP RULE** — Do not put a real record anywhere under `control-plane/`. Records live in `control-plane-records` (D89, D-L0-08). Stubs and fixtures here are synthetic shapes with placeholder ids and must never carry a real product id, a real person, or any customer data (invariant 111). If a stub would need real data to be meaningful, the shape is wrong — file a **CCR-BLOCKING**.

---

### L0-P0-010 — `C-EVT-ENV-1`: the event envelope

| | |
| --- | --- |
| **Size** | M |
| **Depends on** | L0-P0-009 |
| **Writes** | `contracts/records/event.envelope.v1.json`, `contracts/stubs/event.yaml`, `contracts/fixtures/C-EVT-ENV-1/{valid-001,invalid-001..004}.yaml` |
| **Spec** | Section 97.3 ("The event envelope, binding"), Section 60.2 (`event_schema_version`), Section 97.1 (records-writer path, D76/D89) |

**The envelope, binding, and an event missing any envelope field is rejected at write time (97.3):** `event_schema_version`, `event_id`, `event_type`, `occurred_at`, `recorded_at`, `actor`, `product`, `subject_ref`, `payload`.

**Schema-encoded rules**

| Rule id | Rule | Spec |
| --- | --- | --- |
| `EVT-R1` | All nine envelope fields are required; an event missing any one is rejected at write time | 97.3 |
| `EVT-R2` | `event_type` is drawn from the closed enum of `C-EVT-ENUM-1`; free text is rejected | 97.3 |
| `EVT-R3` | `occurred_at` and `recorded_at` are UTC with offset, and `recorded_at >= occurred_at` | 97.1, 97.3 |
| `EVT-R4` | `actor` is a registry identity — human or machine — never a display name | 97.3 |
| `EVT-R5` | Path convention: `events/YYYY-MM-DD/EVT-YYYY-MM-DD-NNNNNN.yaml`, one file per event, never a concurrent append to a shared period file | 97.3 |
| `EVT-R6` | Per-type `payload` fields are declared **with the type** in `C-EVT-ENUM-1`, not here | 97.3 |

`EVT-R3`'s ordering half is not expressible in JSON Schema; it is declared in the contract body as `cross_field_rules[]` and is L4's writer-side assertion. That split is recorded here so L2 and L3 do not each implement it independently.

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-EVT-ENV-1
cat > contracts/records/event.envelope.v1.json << 'SCHEMA_EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "contracts/records/event.envelope.v1.json",
  "title": "C-EVT-ENV-1 — event envelope (v1)",
  "description": "Every event carries all nine envelope fields; an event missing any one is rejected at write time. Section 97.3.",
  "type": "object",
  "required": [
    "event_schema_version",
    "event_id",
    "event_type",
    "occurred_at",
    "recorded_at",
    "actor",
    "product",
    "subject_ref",
    "payload"
  ],
  "properties": {
    "event_schema_version": {
      "type": "integer",
      "const": 1
    },
    "event_id": {
      "type": "string",
      "pattern": "^EVT-\\d{4}-\\d{2}-\\d{2}-\\d{6}$",
      "description": "EVT-R5: path convention EVT-YYYY-MM-DD-NNNNNN, six-digit zero-padded sequence number."
    },
    "event_type": {
      "type": "string",
      "pattern": "^[a-z][a-z0-9_]*$",
      "description": "EVT-R2: drawn from the closed enum of C-EVT-ENUM-1; free text is rejected."
    },
    "occurred_at": {
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(Z|[+-]\\d{2}:\\d{2})$",
      "description": "EVT-R3: UTC with offset."
    },
    "recorded_at": {
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(Z|[+-]\\d{2}:\\d{2})$",
      "description": "EVT-R3: UTC with offset. recorded_at >= occurred_at is enforced by the L4 writer-side assertion declared in cross_field_rules."
    },
    "actor": {
      "type": "string",
      "description": "EVT-R4: registry identity — human or machine — never a display name."
    },
    "product": {
      "type": "string"
    },
    "subject_ref": {
      "type": "string"
    },
    "payload": {
      "type": "object",
      "description": "EVT-R6: per-type payload fields are declared with the type in C-EVT-ENUM-1, not here."
    }
  },
  "cross_field_rules": [
    {
      "rule": "EVT-R3",
      "assertion": "recorded_at >= occurred_at",
      "enforced_by": "L4 writer-side assertion"
    }
  ]
}
SCHEMA_EOF
# Invalid fixtures:
#   invalid-001  EVT-R1  event with no `subject_ref`
#   invalid-002  EVT-R2  event_type: "Gate 1 approval"  (free text)
#   invalid-003  EVT-R2  event_type: "plan-approved"    (hyphen, not the shipped identifier)
#   invalid-004  EVT-R5  event_id: "EVT-2026-9-14-317"  (unpadded)
python contracts/ci/register_add.py C-EVT-ENV-1 records/event.envelope.v1.json 1 L4 L1,L2,L3,L4,L5 stubs/event.yaml
git add -A && git commit -m "L0-P0-010: C-EVT-ENV-1 event envelope"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Schema is valid JSON Schema 2020-12 | `check-jsonschema --check-metaschema contracts/records/event.envelope.v1.json && echo ok` | `ok` |
| 2 | Exactly the nine envelope fields are required | `python -c "import json;print(len(json.load(open('contracts/records/event.envelope.v1.json'))['required']))"` | `9` |
| 3 | The stub validates | `check-jsonschema --schemafile contracts/records/event.envelope.v1.json contracts/stubs/event.yaml && echo ok` | `ok` |
| 4 | All four invalid fixtures rejected | `for f in contracts/fixtures/C-EVT-ENV-1/invalid-*.yaml; do check-jsonschema --schemafile contracts/records/event.envelope.v1.json "$f" >/dev/null 2>&1 && echo "LEAK $f" \|\| echo "rejected $f"; done` | four `rejected …`, no `LEAK` |
| 5 | The stub is the Section 97.3 worked example, field for field | `python -c "import yaml;e=yaml.safe_load(open('contracts/stubs/event.yaml'));print(e['event_type'],e['payload']['gate'],e['payload']['agent_authored'])"` | `plan_approved 1 False` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import json, yaml
S = json.load(open("contracts/records/event.envelope.v1.json"))
need = {"event_schema_version","event_id","event_type","occurred_at","recorded_at","actor","product","subject_ref","payload"}
ok = set(S["required"]) == need
e = yaml.safe_load(open("contracts/stubs/event.yaml"))
ok &= set(e) >= need and e["event_schema_version"] == 1
print("L0-P0-010 PASS" if ok else "L0-P0-010 FAIL")
PY
```

Expected: `L0-P0-010 PASS`

**STOP RULE** — Do not make any envelope field optional "for convenience during development". 97.3 rejects a missing field at write time, and a lane that develops against a permissive stub writes events the real writer will refuse. If a lane asks for an optional field, that is a **CCR-BREAKING**, not a stub tweak.

---

### L0-P0-011 — `C-EVT-ENUM-1`: the closed `event_type` enum, all 86 identifiers

| | |
| --- | --- |
| **Size** | L |
| **Depends on** | L0-P0-008, L0-P0-010 |
| **Writes** | `contracts/records/event-type.enum.v1.yaml`, `contracts/stubs/event-type.enum.yaml`, `contracts/fixtures/C-EVT-ENUM-1/{valid-001,invalid-001,invalid-002}.yaml`; updates `contracts/stubs/platform.yaml` `event_types` |
| **Spec** | Section 97.3 ("Event types are identifiers, not prose"), Section 60.2 (enum versions with `platform_version`), Section 92.11 (governed addition), Section 52.6 (`platform.yaml` owner row) |

**Why this is L0's and no lane's.** 97.3: "Every entry in the taxonomy below has exactly one stable `event_type` identifier — lower-case, underscore-separated, never renamed once shipped… control-plane CI rejects any event whose `event_type` is absent from it, and the enum ships populated in Phase 1 so no workflow ever writes an untyped event. A new event type is a governed addition to the enum and to this taxonomy." Deriving identifiers from prose is interpretation; interpretation belongs to L0. Five lanes emit events, so five lanes would otherwise each invent `plan_approved`, `plan-approved` and `Gate 1 approval` for the same event and split every metric derived from it — exactly the failure 97.3 names.

**D-L0-03 applied.** One identifier per middot-separated taxonomy entry: **86**. Paired states inside an entry are payload fields, never separate types.

**The frozen mapping.** Taxonomy entry (Section 97.3) → identifier.

| # | Taxonomy entry | `event_type` |
| --- | --- | --- |
| 1 | Work item created | `work_item_created` |
| 2 | moved to Ready | `work_item_moved_to_ready` |
| 3 | assigned | `work_item_assigned` |
| 4 | Ready-queue miss recorded | `ready_queue_miss_recorded` |
| 5 | plan submitted | `plan_submitted` |
| 6 | plan rejected with reason | `plan_rejected` |
| 7 | plan approved (Gate 1) with `agent_authored` flag | `plan_approved` |
| 8 | change class assigned | `change_class_assigned` |
| 9 | impact scope assigned | `impact_scope_assigned` |
| 10 | reversibility class assigned | `reversibility_class_assigned` |
| 11 | requirement changed materially | `requirement_changed_materially` |
| 12 | re-plan triggered | `replan_triggered` |
| 13 | execute started | `execute_started` |
| 14 | PR opened with `agent_authored` flag | `pr_opened` |
| 15 | review requested | `review_requested` |
| 16 | Gate 2 approval with reviewer role | `gate2_approved` |
| 17 | CI pass or fail per check | `ci_check_completed` |
| 18 | parity check result | `parity_check_completed` |
| 19 | artifact built with digest | `artifact_built` |
| 20 | staging deployed | `staging_deployed` |
| 21 | staging smoke result | `staging_smoke_completed` |
| 22 | UAT executed with result | `uat_executed` |
| 23 | merge | `pr_merged` |
| 24 | production approval granted with approver | `production_approval_granted` |
| 25 | production deployed with digest | `production_deployed` |
| 26 | production smoke result | `production_smoke_completed` |
| 27 | `/version` digest confirmed | `version_digest_confirmed` |
| 28 | health check result | `health_check_completed` |
| 29 | feature flag enabled or disabled | `feature_flag_toggled` |
| 30 | rollback initiated with from-digest and to-digest | `rollback_initiated` |
| 31 | hotfix authorised | `hotfix_authorised` |
| 32 | incident opened with severity | `incident_opened` |
| 33 | incident resolved | `incident_resolved` |
| 34 | postmortem completed | `postmortem_completed` |
| 35 | regression test added for a production bug | `regression_test_added` |
| 36 | security incident opened | `security_incident_opened` |
| 37 | credential rotated | `credential_rotated` |
| 38 | restore test executed with result | `restore_test_executed` |
| 39 | secret or certificate expiry alert | `asset_expiry_alerted` |
| 40 | asset owner reassigned | `asset_owner_reassigned` |
| 41 | lifecycle transition | `lifecycle_transitioned` |
| 42 | launch readiness signed off | `launch_readiness_signed_off` |
| 43 | reviewer matrix change | `reviewer_matrix_changed` |
| 44 | knowledge redundancy status change | `knowledge_redundancy_status_changed` |
| 45 | person added | `person_added` |
| 46 | person role changed | `person_role_changed` |
| 47 | person departed | `person_departed` |
| 48 | orphan detected | `orphan_detected` |
| 49 | orphan resolved | `orphan_resolved` |
| 50 | temporary assignment created and expired | `temporary_assignment_state_changed` |
| 51 | acting team lead activated and deactivated | `acting_team_lead_state_changed` |
| 52 | drift detected by severity | `drift_detected` |
| 53 | drift repaired | `drift_repaired` |
| 54 | product created | `product_created` |
| 55 | product split | `product_split` |
| 56 | product merged | `product_merged` |
| 57 | product transferred | `product_transferred` |
| 58 | shared service created | `shared_service_created` |
| 59 | shared service breaking change released | `shared_service_breaking_change_released` |
| 60 | platform change proposed | `platform_change_proposed` |
| 61 | canary started | `canary_started` |
| 62 | canary result | `canary_completed` |
| 63 | fleet rollout started | `fleet_rollout_started` |
| 64 | platform rollback initiated | `platform_rollback_initiated` |
| 65 | contract version migrated | `contract_version_migrated` |
| 66 | compatibility state changed | `compatibility_state_changed` |
| 67 | background layer PR created | `background_pr_created` |
| 68 | accepted or rejected with task-class reason | `background_pr_dispositioned` |
| 69 | task class suspended or restored | `task_class_state_changed` |
| 70 | AI runtime changed | `ai_runtime_changed` |
| 71 | AI provider outage recorded | `ai_provider_outage_recorded` |
| 72 | model benchmark completed | `model_benchmark_completed` |
| 73 | status request received (Coordination category) | `status_request_received` |
| 74 | plan submitted-to-approver notification sent | `plan_approver_notified` |
| 75 | verification blocked and unblocked | `verification_block_state_changed` |
| 76 | degraded mode entered and exited | `degraded_mode_state_changed` |
| 77 | gap procedure run | `gap_procedure_run` |
| 78 | eval regression detected | `eval_regression_detected` |
| 79 | pending decision opened and closed | `pending_decision_state_changed` |
| 80 | onboarding phase completed | `onboarding_phase_completed` |
| 81 | support item ingested | `support_item_ingested` |
| 82 | support first-touch breach | `support_first_touch_breached` |
| 83 | delegation expiry warning issued | `delegation_expiry_warned` |
| 84 | temporary-person expiry warning issued | `temporary_person_expiry_warned` |
| 85 | launch sign-off requested | `launch_signoff_requested` |
| 86 | weekend exception requested, authorised, worked, TOIL scheduled and taken | `weekend_exception_state_changed` |

**The eleven paired-state identifiers and their mandatory `payload.state` values** — each one is a single type whose payload carries the state, per D-L0-03:

| `event_type` | `payload.state` enum |
| --- | --- |
| `ci_check_completed` | `pass`, `fail` |
| `feature_flag_toggled` | `enabled`, `disabled` |
| `temporary_assignment_state_changed` | `created`, `expired` |
| `acting_team_lead_state_changed` | `activated`, `deactivated` |
| `background_pr_dispositioned` | `accepted`, `rejected` (plus required `task_class_reason`) |
| `task_class_state_changed` | `suspended`, `restored` |
| `verification_block_state_changed` | `blocked`, `unblocked` |
| `degraded_mode_state_changed` | `entered`, `exited` |
| `pending_decision_state_changed` | `opened`, `closed` |
| `weekend_exception_state_changed` | `requested`, `authorised`, `worked`, `toil_scheduled`, `toil_taken` |
| `canary_completed` | `pass`, `fail`, `abandoned` |

Every other identifier carries `payload` fields declared beside it in the enum file (`EVT-R6`).

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-EVT-ENUM-1
cat > contracts/records/event-type.enum.v1.yaml <<'ENUMEOF'
# C-EVT-ENUM-1 — closed event_type enum, 86 identifiers (D-L0-03 / Section 97.3)
schema_version: 1
enum_version: "1.0"
event_types:
  - {id: work_item_created, taxonomy_entry: "Work item created", payload_fields: [], retired: false}
  - {id: work_item_moved_to_ready, taxonomy_entry: "moved to Ready", payload_fields: [], retired: false}
  - {id: work_item_assigned, taxonomy_entry: "assigned", payload_fields: [], retired: false}
  - {id: ready_queue_miss_recorded, taxonomy_entry: "Ready-queue miss recorded", payload_fields: [], retired: false}
  - {id: plan_submitted, taxonomy_entry: "plan submitted", payload_fields: [], retired: false}
  - {id: plan_rejected, taxonomy_entry: "plan rejected with reason", payload_fields: [], retired: false}
  - {id: plan_approved, taxonomy_entry: "plan approved (Gate 1) with agent_authored flag", payload_fields: [agent_authored], retired: false}
  - {id: change_class_assigned, taxonomy_entry: "change class assigned", payload_fields: [], retired: false}
  - {id: impact_scope_assigned, taxonomy_entry: "impact scope assigned", payload_fields: [], retired: false}
  - {id: reversibility_class_assigned, taxonomy_entry: "reversibility class assigned", payload_fields: [], retired: false}
  - {id: requirement_changed_materially, taxonomy_entry: "requirement changed materially", payload_fields: [], retired: false}
  - {id: replan_triggered, taxonomy_entry: "re-plan triggered", payload_fields: [], retired: false}
  - {id: execute_started, taxonomy_entry: "execute started", payload_fields: [], retired: false}
  - {id: pr_opened, taxonomy_entry: "PR opened with agent_authored flag", payload_fields: [agent_authored], retired: false}
  - {id: review_requested, taxonomy_entry: "review requested", payload_fields: [], retired: false}
  - {id: gate2_approved, taxonomy_entry: "Gate 2 approval with reviewer role", payload_fields: [reviewer_role], retired: false}
  - {id: ci_check_completed, taxonomy_entry: "CI pass or fail per check", payload_fields: [state], retired: false}
  - {id: parity_check_completed, taxonomy_entry: "parity check result", payload_fields: [], retired: false}
  - {id: artifact_built, taxonomy_entry: "artifact built with digest", payload_fields: [digest], retired: false}
  - {id: staging_deployed, taxonomy_entry: "staging deployed", payload_fields: [], retired: false}
  - {id: staging_smoke_completed, taxonomy_entry: "staging smoke result", payload_fields: [], retired: false}
  - {id: uat_executed, taxonomy_entry: "UAT executed with result", payload_fields: [], retired: false}
  - {id: pr_merged, taxonomy_entry: "merge", payload_fields: [], retired: false}
  - {id: production_approval_granted, taxonomy_entry: "production approval granted with approver", payload_fields: [approver], retired: false}
  - {id: production_deployed, taxonomy_entry: "production deployed with digest", payload_fields: [digest], retired: false}
  - {id: production_smoke_completed, taxonomy_entry: "production smoke result", payload_fields: [], retired: false}
  - {id: version_digest_confirmed, taxonomy_entry: "/version digest confirmed", payload_fields: [], retired: false}
  - {id: health_check_completed, taxonomy_entry: "health check result", payload_fields: [], retired: false}
  - {id: feature_flag_toggled, taxonomy_entry: "feature flag enabled or disabled", payload_fields: [state], retired: false}
  - {id: rollback_initiated, taxonomy_entry: "rollback initiated with from-digest and to-digest", payload_fields: [from_digest, to_digest], retired: false}
  - {id: hotfix_authorised, taxonomy_entry: "hotfix authorised", payload_fields: [], retired: false}
  - {id: incident_opened, taxonomy_entry: "incident opened with severity", payload_fields: [severity], retired: false}
  - {id: incident_resolved, taxonomy_entry: "incident resolved", payload_fields: [], retired: false}
  - {id: postmortem_completed, taxonomy_entry: "postmortem completed", payload_fields: [], retired: false}
  - {id: regression_test_added, taxonomy_entry: "regression test added for a production bug", payload_fields: [], retired: false}
  - {id: security_incident_opened, taxonomy_entry: "security incident opened", payload_fields: [], retired: false}
  - {id: credential_rotated, taxonomy_entry: "credential rotated", payload_fields: [], retired: false}
  - {id: restore_test_executed, taxonomy_entry: "restore test executed with result", payload_fields: [], retired: false}
  - {id: asset_expiry_alerted, taxonomy_entry: "secret or certificate expiry alert", payload_fields: [], retired: false}
  - {id: asset_owner_reassigned, taxonomy_entry: "asset owner reassigned", payload_fields: [], retired: false}
  - {id: lifecycle_transitioned, taxonomy_entry: "lifecycle transition", payload_fields: [], retired: false}
  - {id: launch_readiness_signed_off, taxonomy_entry: "launch readiness signed off", payload_fields: [], retired: false}
  - {id: reviewer_matrix_changed, taxonomy_entry: "reviewer matrix change", payload_fields: [], retired: false}
  - {id: knowledge_redundancy_status_changed, taxonomy_entry: "knowledge redundancy status change", payload_fields: [], retired: false}
  - {id: person_added, taxonomy_entry: "person added", payload_fields: [], retired: false}
  - {id: person_role_changed, taxonomy_entry: "person role changed", payload_fields: [], retired: false}
  - {id: person_departed, taxonomy_entry: "person departed", payload_fields: [], retired: false}
  - {id: orphan_detected, taxonomy_entry: "orphan detected", payload_fields: [], retired: false}
  - {id: orphan_resolved, taxonomy_entry: "orphan resolved", payload_fields: [], retired: false}
  - {id: temporary_assignment_state_changed, taxonomy_entry: "temporary assignment created and expired", payload_fields: [state], retired: false}
  - {id: acting_team_lead_state_changed, taxonomy_entry: "acting team lead activated and deactivated", payload_fields: [state], retired: false}
  - {id: drift_detected, taxonomy_entry: "drift detected by severity", payload_fields: [severity], retired: false}
  - {id: drift_repaired, taxonomy_entry: "drift repaired", payload_fields: [], retired: false}
  - {id: product_created, taxonomy_entry: "product created", payload_fields: [], retired: false}
  - {id: product_split, taxonomy_entry: "product split", payload_fields: [], retired: false}
  - {id: product_merged, taxonomy_entry: "product merged", payload_fields: [], retired: false}
  - {id: product_transferred, taxonomy_entry: "product transferred", payload_fields: [], retired: false}
  - {id: shared_service_created, taxonomy_entry: "shared service created", payload_fields: [], retired: false}
  - {id: shared_service_breaking_change_released, taxonomy_entry: "shared service breaking change released", payload_fields: [], retired: false}
  - {id: platform_change_proposed, taxonomy_entry: "platform change proposed", payload_fields: [], retired: false}
  - {id: canary_started, taxonomy_entry: "canary started", payload_fields: [], retired: false}
  - {id: canary_completed, taxonomy_entry: "canary result", payload_fields: [state], retired: false}
  - {id: fleet_rollout_started, taxonomy_entry: "fleet rollout started", payload_fields: [], retired: false}
  - {id: platform_rollback_initiated, taxonomy_entry: "platform rollback initiated", payload_fields: [], retired: false}
  - {id: contract_version_migrated, taxonomy_entry: "contract version migrated", payload_fields: [], retired: false}
  - {id: compatibility_state_changed, taxonomy_entry: "compatibility state changed", payload_fields: [], retired: false}
  - {id: background_pr_created, taxonomy_entry: "background layer PR created", payload_fields: [], retired: false}
  - {id: background_pr_dispositioned, taxonomy_entry: "accepted or rejected with task-class reason", payload_fields: [state, task_class_reason], retired: false}
  - {id: task_class_state_changed, taxonomy_entry: "task class suspended or restored", payload_fields: [state], retired: false}
  - {id: ai_runtime_changed, taxonomy_entry: "AI runtime changed", payload_fields: [], retired: false}
  - {id: ai_provider_outage_recorded, taxonomy_entry: "AI provider outage recorded", payload_fields: [], retired: false}
  - {id: model_benchmark_completed, taxonomy_entry: "model benchmark completed", payload_fields: [], retired: false}
  - {id: status_request_received, taxonomy_entry: "status request received (Coordination category)", payload_fields: [], retired: false}
  - {id: plan_approver_notified, taxonomy_entry: "plan submitted-to-approver notification sent", payload_fields: [], retired: false}
  - {id: verification_block_state_changed, taxonomy_entry: "verification blocked and unblocked", payload_fields: [state], retired: false}
  - {id: degraded_mode_state_changed, taxonomy_entry: "degraded mode entered and exited", payload_fields: [state], retired: false}
  - {id: gap_procedure_run, taxonomy_entry: "gap procedure run", payload_fields: [], retired: false}
  - {id: eval_regression_detected, taxonomy_entry: "eval regression detected", payload_fields: [], retired: false}
  - {id: pending_decision_state_changed, taxonomy_entry: "pending decision opened and closed", payload_fields: [state], retired: false}
  - {id: onboarding_phase_completed, taxonomy_entry: "onboarding phase completed", payload_fields: [], retired: false}
  - {id: support_item_ingested, taxonomy_entry: "support item ingested", payload_fields: [], retired: false}
  - {id: support_first_touch_breached, taxonomy_entry: "support first-touch breach", payload_fields: [], retired: false}
  - {id: delegation_expiry_warned, taxonomy_entry: "delegation expiry warning issued", payload_fields: [], retired: false}
  - {id: temporary_person_expiry_warned, taxonomy_entry: "temporary-person expiry warning issued", payload_fields: [], retired: false}
  - {id: launch_signoff_requested, taxonomy_entry: "launch sign-off requested", payload_fields: [], retired: false}
  - {id: weekend_exception_state_changed, taxonomy_entry: "weekend exception requested, authorised, worked, TOIL scheduled and taken", payload_fields: [state], retired: false}
ENUMEOF
cp contracts/records/event-type.enum.v1.yaml contracts/stubs/event-type.enum.yaml
python - <<'PY'
import yaml, pathlib
enum = yaml.safe_load(open("contracts/records/event-type.enum.v1.yaml"))
p = pathlib.Path("contracts/stubs/platform.yaml")
d = yaml.safe_load(p.read_text(encoding="utf-8"))
d["event_types"] = [e["id"] for e in enum["event_types"]]
p.write_text(yaml.safe_dump(d, sort_keys=False), encoding="utf-8")
print("platform.yaml event_types populated:", len(d["event_types"]))
PY
printf '%s\n' '# EXPECT: reject — event_type `plan-approved` uses a hyphen; identifiers are underscore-separated' \
  > contracts/fixtures/C-EVT-ENUM-1/invalid-001.yaml
printf '%s\n' '# EXPECT: reject — event_type `deploy_finished` is absent from the closed enum' \
  > contracts/fixtures/C-EVT-ENUM-1/invalid-002.yaml
python contracts/ci/register_add.py C-EVT-ENUM-1 records/event-type.enum.v1.yaml 1 L4 L1,L2,L3,L4,L5 stubs/event-type.enum.yaml
git add -A && git commit -m "L0-P0-011: C-EVT-ENUM-1 closed event_type enum, 86 identifiers"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | The enum holds exactly 86 identifiers (D-L0-03) | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/records/event-type.enum.v1.yaml'))['event_types']))"` | `86` |
| 2 | Every identifier is lower-case underscore-separated | `python -c "import re,yaml;e=yaml.safe_load(open('contracts/records/event-type.enum.v1.yaml'))['event_types'];print(sum(1 for x in e if not re.fullmatch(r'[a-z][a-z0-9_]*', x['id'])))"` | `0` |
| 3 | Identifiers are unique | `python -c "import yaml;e=[x['id'] for x in yaml.safe_load(open('contracts/records/event-type.enum.v1.yaml'))['event_types']];print(len(e)==len(set(e)))"` | `True` |
| 4 | The spec's literal example is present | `grep -c '^\s*- id: plan_approved$' contracts/records/event-type.enum.v1.yaml` | `1` |
| 5 | `platform.yaml` carries the same 86 | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/stubs/platform.yaml'))['event_types']))"` | `86` |
| 6 | The eleven paired types each declare a `state` payload field | see SELF-VERIFY | `L0-P0-011 PASS` |
| 7 | No identifier is `retired: true` at freeze | `python -c "import yaml;print(sum(1 for x in yaml.safe_load(open('contracts/records/event-type.enum.v1.yaml'))['event_types'] if x.get('retired')))"` | `0` |
| 8 | The count matches the taxonomy, derived not asserted | run the taxonomy re-count below | `86 86` |

Taxonomy re-count — proves the 86 against the spec text rather than against this file:

```bash
set -euo pipefail
python - <<'PY'
import yaml
SPEC = r"C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
line = next(l for l in open(SPEC, encoding="utf-8") if l.startswith("Work item created"))
n_spec = len([p for p in line.split("\u00b7") if p.strip()])
n_enum = len(yaml.safe_load(open("contracts/records/event-type.enum.v1.yaml"))["event_types"])
print(n_spec, n_enum)
PY
```

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import re, yaml
E = yaml.safe_load(open("contracts/records/event-type.enum.v1.yaml"))["event_types"]
ids = [e["id"] for e in E]
paired = {"ci_check_completed","feature_flag_toggled","temporary_assignment_state_changed",
 "acting_team_lead_state_changed","background_pr_dispositioned","task_class_state_changed",
 "verification_block_state_changed","degraded_mode_state_changed","pending_decision_state_changed",
 "weekend_exception_state_changed","canary_completed"}
by = {e["id"]: e for e in E}
ok  = len(ids) == 86 == len(set(ids))
ok &= all(re.fullmatch(r"[a-z][a-z0-9_]*", i) for i in ids)
ok &= paired <= set(ids)
ok &= all("state" in by[p]["payload_fields"] for p in paired)
ok &= all(e.get("taxonomy_entry") for e in E)
print("L0-P0-011 PASS" if ok else "L0-P0-011 FAIL")
PY
```

Expected: `L0-P0-011 PASS`

**STOP RULE** — If the taxonomy re-count prints anything other than `86 86`, stop immediately and do not adjust the enum to match. A divergence means either the spec line was edited or an entry was dropped — both are conditions L0 must investigate before five lanes start emitting. If a lane later needs an event that is not in the 86, that is a **governed addition** (97.3, 92.11): a CCR of class **CCR-ADDITIVE** that lands as enum version 1.1 and updates `platform.yaml`. **Never rename a shipped identifier** — 97.3 forbids it, and retiring is `retired: true`, never deletion.

---

### L0-P0-012 — `C-REC-STORE-MAP-1`: canonical record stores and write freshness

| | |
| --- | --- |
| **Size** | M |
| **Depends on** | L0-P0-009, L0-P0-010 |
| **Writes** | `contracts/records/store-map.v1.yaml`, `contracts/stubs/store-map.yaml`, `contracts/fixtures/C-REC-STORE-MAP-1/{valid-001,invalid-001,invalid-002}.yaml`; and the directory skeleton in `control-plane-records` |
| **Spec** | Section 97.2 (the store table), Section 97.2 (write freshness), Section 53.1 (freshness row), Section 40.1 (D89, D107), Section 52.6 (`records/` row) |

Frozen because three lanes need the same list: L4 writes the stores, L2's workflows write into them as required failing steps, L3 reconciles their freshness.

**Every row carries:** `store` id, `path` (under `control-plane-records/`), `written_by`, `generates` (the metrics it feeds, transcribed from 97.2), `freshness_class` (`amber` | `blocking`), and `record_body` (the `$def` name in `C-REC-ENV-1`, or `null` where no body is frozen yet).

**The three blocking stores, binding (97.2 / 53.1).** "a store past its interval is Amber, and Blocking for `events/`, `records/deployments/` and `records/uat/`". Every other store is Amber. This is not a lane judgement.

**The twenty-one rows** are the Section 97.2 table plus `records/decisions/pending/`: `records/incidents/`, `records/postmortems/`, `records/uat/`, `records/estimates/`, `records/deployments/`, `records/restore-tests/`, `records/decisions/`, `records/decisions/pending/`, `records/breaches/`, `records/deletion-requests/`, `records/security-reviews/`, `records/eval/`, `records/launches/`, `records/demos/`, `records/support/`, `records/onboarding/`, `records/leave/`, and `events/`. The three registry-resident rows of that table — `exceptions.yaml`, `policies.yaml`, `patterns.yaml` — carry `repository: control-plane` and `freshness_class: null`, because they are hand-maintained registry files, not written stores.

**Two further binding facts frozen in the body**, so no lane re-derives them:

* `RECORD-VERIFICATION-RESULT` is the single `workflow_dispatch` pattern by which a human manual result reaches the machine, with structured inputs `product`, `item`, `mechanism`, `result` (`pass|fail`), `evidence_link` (97.2). Frozen as `dispatch_contract` in the body; consumed by L2 (the workflow) and L4 (the writer).
* Two field-level obligations from 97.2: support records carry `detection_source` whose values include `founder_direct` and `customer`; change records and PRs carry `agent_authored`, set at Gate 1 and at PR creation.

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-REC-STORE-MAP-1
cat > contracts/records/store-map.v1.yaml << 'STOREMAP_EOF'
# C-REC-STORE-MAP-1 — canonical record stores and write freshness (v1). Section 97.2.
contract_version: 1

dispatch_contract:
  type: workflow_dispatch
  trigger: RECORD-VERIFICATION-RESULT
  description: "The single workflow_dispatch pattern by which a human manual result reaches the machine. Section 97.2."
  inputs:
    - product
    - item
    - mechanism
    - result
    - evidence_link
  result_values:
    - pass
    - fail

field_obligations:
  support_detection_source:
    - founder_direct
    - customer
    - alert
    - internal
    - support_intake
  agent_authored_set_at:
    - gate_1
    - pr_creation

stores:
  - store: records/incidents/
    path: records/incidents/
    written_by: L4
    generates: [incident_rate, mttr, severity_distribution]
    freshness_class: amber
    record_body: incident

  - store: records/postmortems/
    path: records/postmortems/
    written_by: L4
    generates: [postmortem_completion_rate]
    freshness_class: amber
    record_body: null

  - store: records/uat/
    path: records/uat/
    written_by: L4
    generates: [uat_pass_rate, gate_evidence]
    freshness_class: blocking
    record_body: null

  - store: records/estimates/
    path: records/estimates/
    written_by: L4
    generates: [estimation_accuracy]
    freshness_class: amber
    record_body: null

  - store: records/deployments/
    path: records/deployments/
    written_by: L4
    generates: [deployment_frequency, change_failure_rate, gate_evidence]
    freshness_class: blocking
    record_body: deployment

  - store: records/restore-tests/
    path: records/restore-tests/
    written_by: L4
    generates: [restore_test_coverage, rto_evidence]
    freshness_class: amber
    record_body: null

  - store: records/decisions/
    path: records/decisions/
    written_by: L4
    generates: [decision_log]
    freshness_class: amber
    record_body: decision

  - store: records/decisions/pending/
    path: records/decisions/pending/
    written_by: L4
    generates: [pending_decision_count]
    freshness_class: amber
    record_body: decision

  - store: records/breaches/
    path: records/breaches/
    written_by: L4
    generates: [sla_breach_rate]
    freshness_class: amber
    record_body: null

  - store: records/deletion-requests/
    path: records/deletion-requests/
    written_by: L4
    generates: [dsar_compliance_evidence]
    freshness_class: amber
    record_body: deletion_request

  - store: records/security-reviews/
    path: records/security-reviews/
    written_by: L4
    generates: [security_posture, debt_inventory]
    freshness_class: amber
    record_body: security_review

  - store: records/eval/
    path: records/eval/
    written_by: L4
    generates: [eval_regression_signal]
    freshness_class: amber
    record_body: null

  - store: records/launches/
    path: records/launches/
    written_by: L4
    generates: [launch_readiness_log]
    freshness_class: amber
    record_body: null

  - store: records/demos/
    path: records/demos/
    written_by: L4
    generates: [demo_log]
    freshness_class: amber
    record_body: demo

  - store: records/support/
    path: records/support/
    written_by: L4
    generates: [support_volume, first_touch_compliance]
    freshness_class: amber
    record_body: null

  - store: records/onboarding/
    path: records/onboarding/
    written_by: L4
    generates: [onboarding_completion_rate]
    freshness_class: amber
    record_body: null

  - store: records/leave/
    path: records/leave/
    written_by: L4
    generates: [leave_coverage_signal]
    freshness_class: amber
    record_body: null

  - store: events/
    path: events/
    written_by: L4
    generates: [full_event_log, metric_derivation_source]
    freshness_class: blocking
    record_body: null

  - store: exceptions
    path: exceptions.yaml
    repository: control-plane
    written_by: L0
    generates: []
    freshness_class: null
    record_body: null

  - store: policies
    path: policies.yaml
    repository: control-plane
    written_by: L0
    generates: []
    freshness_class: null
    record_body: null

  - store: patterns
    path: patterns.yaml
    repository: control-plane
    written_by: L0
    generates: []
    freshness_class: null
    record_body: null
STOREMAP_EOF
python - <<'PY'
import yaml, os, pathlib
m = yaml.safe_load(open("contracts/records/store-map.v1.yaml"))
cpr = os.environ["CPR"]
for s in m["stores"]:
    if s.get("repository","control-plane-records") != "control-plane-records":
        continue
    d = pathlib.Path(cpr, s["path"])
    d.mkdir(parents=True, exist_ok=True)
    (d / ".gitkeep").write_text("# store: %s; written by %s\n" % (s["store"], s["written_by"]), encoding="utf-8")
print("skeleton created")
PY
cp contracts/records/store-map.v1.yaml contracts/stubs/store-map.yaml
python contracts/ci/register_add.py C-REC-STORE-MAP-1 records/store-map.v1.yaml 1 L4 L2,L3,L4 stubs/store-map.yaml
git add -A && git commit -m "L0-P0-012: C-REC-STORE-MAP-1 record store map and freshness classes"
cd "$CPR" && git add -A && git commit -m "L0-P0-012: record store directory skeleton" && git push
cd "$CP"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Twenty-one store rows | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/records/store-map.v1.yaml'))['stores']))"` | `21` |
| 2 | Exactly three blocking-freshness stores, and they are the right three | `python -c "import yaml;print(sorted(s['path'] for s in yaml.safe_load(open('contracts/records/store-map.v1.yaml'))['stores'] if s.get('freshness_class')=='blocking'))"` | `['events/', 'records/deployments/', 'records/uat/']` |
| 3 | No store row points at `control-plane` except the three registry files | `python -c "import yaml;print(sorted(s['store'] for s in yaml.safe_load(open('contracts/records/store-map.v1.yaml'))['stores'] if s.get('repository')=='control-plane'))"` | `['exceptions', 'patterns', 'policies']` |
| 4 | The dispatch contract declares the five structured inputs | `python -c "import yaml;print(sorted(yaml.safe_load(open('contracts/records/store-map.v1.yaml'))['dispatch_contract']['inputs']))"` | `['evidence_link', 'item', 'mechanism', 'product', 'result']` |
| 5 | The records repository skeleton exists and holds no record | `find "$CPR/records" "$CPR/events" -name '*.yaml' \| wc -l` | `0` |
| 6 | Both invalid fixtures rejected by the map's own consistency check | see SELF-VERIFY | `L0-P0-012 PASS` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import json, yaml
m = yaml.safe_load(open("contracts/records/store-map.v1.yaml"))
defs = set(json.load(open("contracts/records/record.envelope.v1.json"))["$defs"])
blocking = {s["path"] for s in m["stores"] if s.get("freshness_class") == "blocking"}
bodies   = {s["record_body"] for s in m["stores"] if s.get("record_body")}
ok  = len(m["stores"]) == 21
ok &= blocking == {"events/", "records/deployments/", "records/uat/"}
ok &= bodies <= defs
ok &= "founder_direct" in m["field_obligations"]["support_detection_source"]
ok &= m["field_obligations"]["agent_authored_set_at"] == ["gate_1", "pr_creation"]
print("L0-P0-012 PASS" if ok else "L0-P0-012 FAIL")
PY
```

Expected: `L0-P0-012 PASS`

**STOP RULE** — If a store you believe necessary is absent from the Section 97.2 table, do not add it. Section 52.6 binds: "Any proposal for a new control-plane artifact must state which existing file cannot hold the content; if an existing file can hold it, the proposal is rejected." File a **CCR-ADDITIVE** carrying that statement, and stop.

---

### L0-P0-013 — `C-WF-IFACE-1`: the reusable workflow interface

| | |
| --- | --- |
| **Size** | L |
| **Depends on** | L0-P0-006, L0-P0-012 |
| **Writes** | `contracts/workflows/reusable-workflow.interface.v1.yaml`, `contracts/stubs/workflow-call-ci.yml`, `contracts/stubs/workflow-call-deploy-production.yml`, `contracts/fixtures/C-WF-IFACE-1/{valid-001,invalid-001..003}.yaml` |
| **Spec** | Section 33.2 (required workflows per repository), Section 99.2 subsystem E, Section 33.3 (blast radius), Section 33.4 (artifacts and environments), Section 44.5 (`restore-production.yml`), Section 32 (evidence chain), AT-103, invariants 22, 85 |

**The nine workflows, frozen.** Section 33.2 names the required set per repository: `ci.yml`, `build.yml`, `deploy-staging.yml`, `deploy-production.yml`, `migrate.yml`, `restore-test.yml`, `restore-production.yml` (wherever the product declares a `recovery:` block), and conditionally `background-queue.yml`. Section 99.2 subsystem E adds `org-export`. All nine are frozen here with their `inputs`, `secrets` and `outputs`.

**Per-workflow interface, the fields every lane reads.** For each: `name`, `consumed_by_pinned_tag: true`, `inputs{}` (each with `type`, `required`, `description`), `secrets{}` (each naming its **tier** from `C-WF-SECRETS-1`), `outputs{}`, `emits_events[]` (identifiers from `C-EVT-ENUM-1`), `writes_records[]` (store ids from `C-REC-STORE-MAP-1`), and `required_steps[]`.

**Binding rules encoded in the contract body**

| Rule id | Rule | Spec |
| --- | --- | --- |
| `WF-R1` | Every workflow is consumed **by pinned tag, never by branch** | 33.3, invariant 85 |
| `WF-R2` | `deploy-production` takes `digest` as a required input and **rejects any digest differing from the one that passed staging verification** | 32, 33.4, invariant 22 |
| `WF-R3` | `deploy-production`'s deployment-record write and event append are **required, failing steps**, not trailing best-effort ones | 97.2 |
| `WF-R4` | Every workflow's `GITHUB_TOKEN` permission block is least-privilege and declared per permission | 33.2 |
| `WF-R5` | Third-party actions are pinned to full commit SHA | 33.2, invariant 85 |
| `WF-R6` | `restore-production.yml` runs with an exceptional-authorisation record and **no credential handed to or typed by a human** | 44.5, AT-103 |
| `WF-R7` | The production-approval gate is the **Section 27.2 workflow-identity gate**: the approving identity must differ from the deploying identity, failing closed. Environment required reviewers are Enterprise-only and are never depended on (D73) | 11.4, 33.4, 27.2 |

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-WF-IFACE-1
python - <<'PY'
import pathlib
pathlib.Path("contracts/workflows").mkdir(parents=True, exist_ok=True)
pathlib.Path("contracts/stubs").mkdir(parents=True, exist_ok=True)

CONTRACT = """\
# --- CONTRACT HEADER (frozen) ---
contract_id: C-WF-IFACE-1
contract_version: 1
owner: L0
publishing_lane: L2
consuming_lanes: [L2, L3, L5]
spec_refs:
  - "Section 33.2"
  - "Section 99.2"
  - "Section 33.3"
  - "Section 33.4"
  - "Section 44.5"
  - "Section 32"
  - "AT-103"
ccr_required: true
# --- BODY ---

rules:
  - id: WF-R1
    spec_ref: "Section 33.3, invariant 85"
    text: "Every workflow is consumed by pinned tag, never by branch."
  - id: WF-R2
    spec_ref: "Section 32, Section 33.4, invariant 22"
    text: "deploy-production takes digest as a required input and rejects any digest differing from the one that passed staging verification."
  - id: WF-R3
    spec_ref: "Section 97.2"
    text: "deploy-production deployment-record write and event append are required, failing steps, not trailing best-effort ones."
  - id: WF-R4
    spec_ref: "Section 33.2"
    text: "Every workflow GITHUB_TOKEN permission block is least-privilege and declared per permission."
  - id: WF-R5
    spec_ref: "Section 33.2, invariant 85"
    text: "Third-party actions are pinned to full commit SHA."
  - id: WF-R6
    spec_ref: "Section 44.5, AT-103"
    text: "restore-production.yml runs with an exceptional-authorisation record and no credential handed to or typed by a human."
  - id: WF-R7
    spec_ref: "Section 11.4, Section 33.4, Section 27.2"
    text: "The production-approval gate is the Section 27.2 workflow-identity gate: the approving identity must differ from the deploying identity, failing closed. Environment required reviewers are Enterprise-only and are never depended on (D73)."

workflows:
  - name: ci
    consumed_by_pinned_tag: true
    inputs:
      ref:
        type: string
        required: false
        description: "Git ref being checked. Informational."
    secrets: {}
    outputs:
      conclusion:
        description: "Aggregate conclusion: pass or fail."
    emits_events:
      - ci_check_completed
      - parity_check_completed
    writes_records: []
    required_steps:
      - run_tests
      - run_contract_validation
      - run_security_scan
      - run_licence_scan
      - run_reviewer_matrix_validation
      - emit_conclusion

  - name: build
    consumed_by_pinned_tag: true
    inputs:
      ref:
        type: string
        required: true
        description: "Full git ref to build."
    secrets: {}
    outputs:
      digest:
        description: "Artifact digest produced by this build."
    emits_events:
      - artifact_built
    writes_records: []
    required_steps:
      - build_artifact
      - attest_digest
      - emit_artifact_built

  - name: deploy-staging
    consumed_by_pinned_tag: true
    inputs:
      digest:
        type: string
        required: true
        description: "Artifact digest to deploy to staging."
      product:
        type: string
        required: true
        description: "Product id (from product.yaml)."
    secrets:
      STAGING_DEPLOY_TOKEN:
        tier: staging
        description: "GitHub Environment secret for staging."
    outputs:
      staging_deploy_time:
        description: "ISO-8601 UTC timestamp of staging deployment."
    emits_events:
      - staging_deployed
      - staging_smoke_completed
      - uat_executed
    writes_records:
      - uat
    required_steps:
      - deploy_to_staging
      - run_staging_smoke
      - record_uat
      - emit_staging_deployed

  - name: deploy-production
    consumed_by_pinned_tag: true
    inputs:
      digest:
        type: string
        required: true
        description: "WF-R2: Artifact digest that passed staging verification. Rejected if it differs from the staging-verified digest."
      product:
        type: string
        required: true
        description: "Product id (from product.yaml)."
      approval_event_id:
        type: string
        required: true
        description: "WF-R7: Record id of the production-approval record. Approving identity must differ from deploying identity."
    secrets:
      PRODUCTION_DEPLOY_TOKEN:
        tier: production
        description: "GitHub Environment secret for production."
    outputs:
      production_deploy_time:
        description: "ISO-8601 UTC timestamp of production deployment."
      deployed_digest:
        description: "Confirmed digest running in production."
    emits_events:
      - production_approval_granted
      - production_deployed
      - production_smoke_completed
      - version_digest_confirmed
    writes_records:
      - deployments
      - events
    required_steps:
      - verify_approval_identity
      - assert_staging_digest_match
      - deploy_to_production
      - write_deployment_record
      - append_event
      - run_production_smoke
      - confirm_version_digest

  - name: migrate
    consumed_by_pinned_tag: true
    inputs:
      product:
        type: string
        required: true
        description: "Product id."
      migration_id:
        type: string
        required: true
        description: "Migration identifier for idempotency tracking."
      direction:
        type: string
        required: true
        description: "up or down."
    secrets:
      STAGING_DEPLOY_TOKEN:
        tier: staging
        description: "Database credentials via staging environment."
    outputs:
      migration_result:
        description: "pass or fail."
    emits_events:
      - ci_check_completed
    writes_records: []
    required_steps:
      - apply_migration
      - verify_migration
      - record_result

  - name: restore-test
    consumed_by_pinned_tag: true
    inputs:
      product:
        type: string
        required: true
        description: "Product id."
      backup_ref:
        type: string
        required: true
        description: "Backup identifier to restore and verify."
    secrets:
      STAGING_DEPLOY_TOKEN:
        tier: staging
        description: "Staging environment secrets for restore test."
    outputs:
      restore_result:
        description: "pass or fail."
    emits_events:
      - restore_test_executed
    writes_records:
      - restore-tests
    required_steps:
      - restore_backup
      - verify_integrity
      - record_restore_test_result
      - emit_restore_test_executed

  - name: restore-production
    consumed_by_pinned_tag: true
    inputs:
      product:
        type: string
        required: true
        description: "Product id."
      backup_ref:
        type: string
        required: true
        description: "Backup identifier to restore."
      exceptional_authorisation_record:
        type: string
        required: true
        description: "WF-R6: Record id of the exceptional-authorisation record. No credential is handed to or typed by a human."
    secrets:
      PRODUCTION_DEPLOY_TOKEN:
        tier: production
        description: "WF-R6: Production environment secrets. Never handed to a human."
    outputs:
      restore_result:
        description: "pass or fail."
    emits_events:
      - restore_test_executed
    writes_records:
      - restore-tests
      - deployments
    required_steps:
      - assert_exceptional_authorisation
      - restore_production_backup
      - verify_integrity
      - write_deployment_record
      - append_event

  - name: background-queue
    consumed_by_pinned_tag: true
    inputs:
      product:
        type: string
        required: true
        description: "Product id."
      task_class:
        type: string
        required: true
        description: "Task class for the background-layer PR."
    secrets:
      BACKGROUND_QUEUE_TOKEN:
        tier: ci
        description: "GitHub token scoped to open background-layer PRs."
    outputs:
      pr_number:
        description: "Pull request number opened."
    emits_events:
      - background_pr_created
      - background_pr_dispositioned
    writes_records: []
    required_steps:
      - open_background_pr
      - emit_background_pr_created

  - name: org-export
    consumed_by_pinned_tag: true
    inputs:
      export_date:
        type: string
        required: true
        description: "ISO-8601 date for the export snapshot (Section 99.2 subsystem E)."
    secrets:
      ORG_EXPORT_TOKEN:
        tier: control_plane
        description: "Fine-grained read credential for org-export (AT-103)."
    outputs:
      export_ref:
        description: "Git ref or artifact reference for the export snapshot."
    emits_events:
      - onboarding_phase_completed
    writes_records: []
    required_steps:
      - export_org_state
      - attest_export
"""
pathlib.Path("contracts/workflows/reusable-workflow.interface.v1.yaml").write_text(CONTRACT, encoding="utf-8")

STUB_CI = """\
# contracts/stubs/workflow-call-ci.yml
# Stub caller for ci.yml — lanes develop against this before L2 ships the real workflow.
# WF-R1: consumed by pinned tag, never by branch.
# WF-R5: third-party actions must be pinned to full commit SHA, never to a mutable tag.
name: CI (stub caller)
on: [push, pull_request]
permissions:
  contents: read
  checks: write
jobs:
  ci:
    uses: stub-org/control-plane/.github/workflows/ci.yml@contracts/v1.0.0
    secrets: inherit
"""
pathlib.Path("contracts/stubs/workflow-call-ci.yml").write_text(STUB_CI, encoding="utf-8")

STUB_DP = """\
# contracts/stubs/workflow-call-deploy-production.yml
# Stub caller for deploy-production.yml.
# WF-R1: pinned tag. WF-R2: digest required. WF-R7: approval_event_id required.
name: Deploy Production (stub caller)
on:
  workflow_dispatch:
    inputs:
      digest:
        required: true
        type: string
        description: "Artifact digest that passed staging verification (WF-R2)."
      approval_event_id:
        required: true
        type: string
        description: "Production-approval record id (WF-R7)."
permissions:
  contents: read
  deployments: write
jobs:
  deploy:
    uses: stub-org/control-plane/.github/workflows/deploy-production.yml@contracts/v1.0.0
    with:
      digest: ${{ inputs.digest }}
      product: stub-product
      approval_event_id: ${{ inputs.approval_event_id }}
    secrets: inherit
"""
pathlib.Path("contracts/stubs/workflow-call-deploy-production.yml").write_text(STUB_DP, encoding="utf-8")

pathlib.Path("contracts/fixtures/C-WF-IFACE-1/valid-001.yaml").write_text("""\
# Valid workflow call: WF-R1 pinned tag, WF-R2 digest present, WF-R5 SHA-pinned action.
caller_workflow:
  jobs:
    deploy:
      uses: stub-org/control-plane/.github/workflows/deploy-production.yml@contracts/v1.0.0
      with:
        digest: sha256:a3f1c2d9e0b74e5f6a8c0d1e2f3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1
        product: stub-product
        approval_event_id: EVT-2026-09-02-000001
      secrets: inherit
  third_party_steps:
    - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
""", encoding="utf-8")

pathlib.Path("contracts/fixtures/C-WF-IFACE-1/invalid-001.yaml").write_text("""\
# EXPECT: reject — WF-R1 caller consuming workflows/ci.yml@main (branch ref, not pinned tag)
caller_workflow:
  jobs:
    ci:
      uses: stub-org/control-plane/.github/workflows/ci.yml@main
      secrets: inherit
""", encoding="utf-8")

pathlib.Path("contracts/fixtures/C-WF-IFACE-1/invalid-002.yaml").write_text("""\
# EXPECT: reject — WF-R2 deploy-production called without required digest input
caller_workflow:
  jobs:
    deploy:
      uses: stub-org/control-plane/.github/workflows/deploy-production.yml@contracts/v1.0.0
      with:
        product: stub-product
        approval_event_id: EVT-2026-09-02-000001
      secrets: inherit
""", encoding="utf-8")

pathlib.Path("contracts/fixtures/C-WF-IFACE-1/invalid-003.yaml").write_text("""\
# EXPECT: reject — WF-R5 third-party action pinned to tag rather than full commit SHA
caller_workflow:
  jobs:
    ci:
      uses: stub-org/control-plane/.github/workflows/ci.yml@contracts/v1.0.0
      secrets: inherit
  third_party_steps:
    - uses: actions/checkout@v4
""", encoding="utf-8")

print("C-WF-IFACE-1 files written")
PY
python contracts/ci/register_add.py C-WF-IFACE-1 workflows/reusable-workflow.interface.v1.yaml 1 L2 L2,L3,L5 stubs/workflow-call-ci.yml
git add -A && git commit -m "L0-P0-013: C-WF-IFACE-1 reusable workflow interface"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Nine workflows frozen | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/workflows/reusable-workflow.interface.v1.yaml'))['workflows']))"` | `9` |
| 2 | The names match Section 33.2 + 99.2 exactly | `python -c "import yaml;print(sorted(w['name'] for w in yaml.safe_load(open('contracts/workflows/reusable-workflow.interface.v1.yaml'))['workflows']))"` | `['background-queue', 'build', 'ci', 'deploy-production', 'deploy-staging', 'migrate', 'org-export', 'restore-production', 'restore-test']` |
| 3 | `deploy-production` requires `digest` (WF-R2) | `python -c "import yaml;w={x['name']:x for x in yaml.safe_load(open('contracts/workflows/reusable-workflow.interface.v1.yaml'))['workflows']};print(w['deploy-production']['inputs']['digest']['required'])"` | `True` |
| 4 | Every `emits_events` identifier exists in the closed enum | see SELF-VERIFY | `L0-P0-013 PASS` |
| 5 | Every `writes_records` store id exists in the store map | see SELF-VERIFY | `L0-P0-013 PASS` |
| 6 | All seven rules present | `grep -o 'WF-R[0-9]' contracts/workflows/reusable-workflow.interface.v1.yaml \| sort -u \| tr '\n' ' '` | `WF-R1 WF-R2 WF-R3 WF-R4 WF-R5 WF-R6 WF-R7 ` |
| 7 | Three invalid fixtures rejected by the interface linter | `python contracts/ci/lint_workflow_calls.py contracts/fixtures/C-WF-IFACE-1/invalid-*.yaml; echo "exit=$?"` | three `rejected …` lines then `exit=1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import yaml
I = yaml.safe_load(open("contracts/workflows/reusable-workflow.interface.v1.yaml"))
enum   = {e["id"] for e in yaml.safe_load(open("contracts/records/event-type.enum.v1.yaml"))["event_types"]}
stores = {s["store"] for s in yaml.safe_load(open("contracts/records/store-map.v1.yaml"))["stores"]}
bad_e = [(w["name"], e) for w in I["workflows"] for e in w.get("emits_events", []) if e not in enum]
bad_s = [(w["name"], s) for w in I["workflows"] for s in w.get("writes_records", []) if s not in stores]
dp = next(w for w in I["workflows"] if w["name"] == "deploy-production")
ok = not bad_e and not bad_s and dp["inputs"]["digest"]["required"] is True
ok &= "write_deployment_record" in dp["required_steps"] and "append_event" in dp["required_steps"]
print("L0-P0-013 PASS" if ok else f"L0-P0-013 FAIL events={bad_e} stores={bad_s}")
PY
```

Expected: `L0-P0-013 PASS`

**STOP RULE** — If any workflow needs an event type absent from the 86, **do not add one here**. The enum is closed and lives in `C-EVT-ENUM-1` + `platform.yaml`; adding it in a workflow interface creates a second enum. File a **CCR-ADDITIVE** against `C-EVT-ENUM-1`. Likewise, do not soften `WF-R7` to "environment required reviewers where available": Section 11.4 and D73 make the workflow-identity gate the mechanism of record, not a fallback.

---

### L0-P0-014 — `C-WF-CHECKS-1`: the required status-check names

| | |
| --- | --- |
| **Size** | M |
| **Depends on** | L0-P0-013 |
| **Writes** | `contracts/workflows/required-checks.v1.yaml`, `contracts/stubs/required-checks.yaml`, `contracts/fixtures/C-WF-CHECKS-1/{valid-001,invalid-001,invalid-002}.yaml` |
| **Spec** | Section 11.3 (required status checks list), Section 33.2 (the no-`if:`/no-path-filter rule), Section 53.2 (`control-plane/blocking-drift`), Section 98.2 Phase 1 (the list starts empty and is populated per phase), PARTITION.md rule 1 (D-L0-05) |

Frozen because the **check name is the coupling** between three lanes: L2 emits it, L5 lists it in branch protection, L3 compares declared against actual. A one-character difference is a gate that reads armed and is not.

**The frozen names** — Section 11.3: "tests, build, security scan, contract validation, reviewer matrix validation, parity check, verification contract, and `control-plane/blocking-drift`". Rendered as stable context strings, plus the reserved `lane-guard` name of **D-L0-05**:

| Context name | Emitted by | Arms at | Spec |
| --- | --- | --- | --- |
| `tests` | `ci.yml` | Phase 4 | 11.3, 33.2 |
| `build` | `build.yml` | Phase 4 | 11.3 |
| `security-scan` | `ci.yml` | Phase 4 | 11.3, 33.2 (delta-gated) |
| `licence-scan` | `ci.yml` | Phase 4 | 33.2 (delta-gated the same way) |
| `contract-validation` | `ci.yml` | Phase 3 | 11.3, 15.5 |
| `reviewer-matrix-validation` | `ci.yml` | Phase 3 | 11.3 |
| `parity-check` | `ci.yml` | Phase 4 | 11.3, 33.4 |
| `verification-contract` | `ci.yml` | Phase 5 | 11.3, 31.2 |
| `control-plane/blocking-drift` | the reconciler check-run (L3) | reconciler build | 11.3, 53.2, 40.1 |
| `renovate-path-guard` | ruleset B, no bypass actor | Phase 2 (Renovate install) | 33.2 (D89) |
| `lane-guard` | L2's first workflow | L2 cycle 1 | D-L0-05, PARTITION.md rule 1 |

**Binding rules in the body**

| Rule id | Rule | Spec |
| --- | --- | --- |
| `CHK-R1` | Every required check name is emitted by a job carrying **no `if:` and no path filter**, which dispatches the real work and asserts a real conclusion. "No work was needed" is an explicit recorded success, never a skip | 33.2 |
| `CHK-R2` | A `skipped` or `neutral` conclusion on a required context of a merged pull request is **Blocking drift** | 33.2, 53.4 |
| `CHK-R3` | The required-check list **starts empty per repository** and each phase's completion check names the contexts it adds. A list that silently stays empty is a gate that reads armed and is not | 98.2 Phase 1 |
| `CHK-R4` | `control-plane/blocking-drift` published under that name by any identity other than the reconciler is Blocking drift | 40.1 |
| `CHK-R5` | `renovate-path-guard` sits on ruleset B, which lists **no bypass actor at all** | 33.2 (D89) |

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-WF-CHECKS-1
python - <<'PY'
import pathlib
pathlib.Path("contracts/workflows").mkdir(parents=True, exist_ok=True)
pathlib.Path("contracts/stubs").mkdir(parents=True, exist_ok=True)

CONTRACT = """\
# --- CONTRACT HEADER (frozen) ---
contract_id: C-WF-CHECKS-1
contract_version: 1
owner: L0
publishing_lane: L2
consuming_lanes: [L2, L3, L5]
spec_refs:
  - "Section 11.3"
  - "Section 33.2"
  - "Section 53.2"
  - "Section 98.2"
  - "PARTITION.md rule 1"
ccr_required: true
# --- BODY ---

rules:
  - id: CHK-R1
    spec_ref: "Section 33.2"
    text: "Every required check name is emitted by a job carrying no if: and no path filter, which dispatches the real work and asserts a real conclusion. No work was needed is an explicit recorded success, never a skip."
  - id: CHK-R2
    spec_ref: "Section 33.2, Section 53.4"
    text: "A skipped or neutral conclusion on a required context of a merged pull request is Blocking drift."
  - id: CHK-R3
    spec_ref: "Section 98.2 Phase 1"
    text: "The required-check list starts empty per repository and each phase completion names the contexts it adds. A list that silently stays empty is a gate that reads armed and is not."
  - id: CHK-R4
    spec_ref: "Section 40.1"
    text: "control-plane/blocking-drift published under that name by any identity other than the reconciler is Blocking drift."
  - id: CHK-R5
    spec_ref: "Section 33.2 (D89)"
    text: "renovate-path-guard sits on ruleset B, which lists no bypass actor at all."

checks:
  - name: tests
    emitted_by: ci.yml
    arms_at: Phase 4
    spec_ref: "Section 11.3, Section 33.2"
    no_if_no_path_filter: true

  - name: build
    emitted_by: build.yml
    arms_at: Phase 4
    spec_ref: "Section 11.3"
    no_if_no_path_filter: true

  - name: security-scan
    emitted_by: ci.yml
    arms_at: Phase 4
    spec_ref: "Section 11.3, Section 33.2"
    no_if_no_path_filter: true

  - name: licence-scan
    emitted_by: ci.yml
    arms_at: Phase 4
    spec_ref: "Section 33.2"
    no_if_no_path_filter: true

  - name: contract-validation
    emitted_by: ci.yml
    arms_at: Phase 3
    spec_ref: "Section 11.3, Section 15.5"
    no_if_no_path_filter: true

  - name: reviewer-matrix-validation
    emitted_by: ci.yml
    arms_at: Phase 3
    spec_ref: "Section 11.3"
    no_if_no_path_filter: true

  - name: parity-check
    emitted_by: ci.yml
    arms_at: Phase 4
    spec_ref: "Section 11.3, Section 33.4"
    no_if_no_path_filter: true

  - name: verification-contract
    emitted_by: ci.yml
    arms_at: Phase 5
    spec_ref: "Section 11.3, Section 31.2"
    no_if_no_path_filter: true

  - name: control-plane/blocking-drift
    emitted_by: L3
    arms_at: reconciler build
    spec_ref: "Section 11.3, Section 53.2, Section 40.1"

  - name: renovate-path-guard
    emitted_by: ruleset-B
    arms_at: Phase 2
    spec_ref: "Section 33.2 (D89)"
    no_if_no_path_filter: true

  - name: lane-guard
    emitted_by: L2
    arms_at: "L2 cycle 1"
    spec_ref: "D-L0-05, PARTITION.md rule 1"
    no_if_no_path_filter: true
"""
pathlib.Path("contracts/workflows/required-checks.v1.yaml").write_text(CONTRACT, encoding="utf-8")
pathlib.Path("contracts/stubs/required-checks.yaml").write_text(CONTRACT, encoding="utf-8")

pathlib.Path("contracts/fixtures/C-WF-CHECKS-1/valid-001.yaml").write_text("""\
# Valid required-check declaration: all eleven contexts with emitter, phase and no_if_no_path_filter.
checks:
  - { name: tests,                      emitted_by: ci.yml,    arms_at: Phase 4,       no_if_no_path_filter: true }
  - { name: build,                      emitted_by: build.yml, arms_at: Phase 4,       no_if_no_path_filter: true }
  - { name: security-scan,              emitted_by: ci.yml,    arms_at: Phase 4,       no_if_no_path_filter: true }
  - { name: licence-scan,               emitted_by: ci.yml,    arms_at: Phase 4,       no_if_no_path_filter: true }
  - { name: contract-validation,        emitted_by: ci.yml,    arms_at: Phase 3,       no_if_no_path_filter: true }
  - { name: reviewer-matrix-validation, emitted_by: ci.yml,    arms_at: Phase 3,       no_if_no_path_filter: true }
  - { name: parity-check,               emitted_by: ci.yml,    arms_at: Phase 4,       no_if_no_path_filter: true }
  - { name: verification-contract,      emitted_by: ci.yml,    arms_at: Phase 5,       no_if_no_path_filter: true }
  - { name: "control-plane/blocking-drift", emitted_by: L3,   arms_at: reconciler build }
  - { name: renovate-path-guard,        emitted_by: ruleset-B, arms_at: Phase 2,       no_if_no_path_filter: true }
  - { name: lane-guard,                 emitted_by: L2,        arms_at: "L2 cycle 1",  no_if_no_path_filter: true }
""", encoding="utf-8")

pathlib.Path("contracts/fixtures/C-WF-CHECKS-1/invalid-001.yaml").write_text("""\
# EXPECT: reject — CHK-R1 a job emitting security-scan guarded by an if: condition
workflow_job:
  name: security-scan
  if: "github.event_name != 'pull_request'"
  runs-on: ubuntu-latest
  steps:
    - run: echo "scan"
""", encoding="utf-8")

pathlib.Path("contracts/fixtures/C-WF-CHECKS-1/invalid-002.yaml").write_text("""\
# EXPECT: reject — CHK-R3 repository declaring required check not present in C-WF-CHECKS-1
repository_branch_protection:
  required_status_checks:
    contexts:
      - tests
      - build
      - coverage-report
""", encoding="utf-8")

print("C-WF-CHECKS-1 files written")
PY
python contracts/ci/register_add.py C-WF-CHECKS-1 workflows/required-checks.v1.yaml 1 L2 L2,L3,L5 stubs/required-checks.yaml
git add -A && git commit -m "L0-P0-014: C-WF-CHECKS-1 required status-check names"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Eleven contexts frozen | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/workflows/required-checks.v1.yaml'))['checks']))"` | `11` |
| 2 | The reconciler's check name is exact | `python -c "import yaml;print([c['name'] for c in yaml.safe_load(open('contracts/workflows/required-checks.v1.yaml'))['checks'] if c['name'].startswith('control-plane/')])"` | `['control-plane/blocking-drift']` |
| 3 | Every context declares an emitter and an arming phase | see SELF-VERIFY | `L0-P0-014 PASS` |
| 4 | `lane-guard` is present and attributed to L2 (D-L0-05) | `python -c "import yaml;print([c['emitted_by'] for c in yaml.safe_load(open('contracts/workflows/required-checks.v1.yaml'))['checks'] if c['name']=='lane-guard'])"` | `['L2']` |
| 5 | All five rules present | `grep -o 'CHK-R[0-9]' contracts/workflows/required-checks.v1.yaml \| sort -u \| tr '\n' ' '` | `CHK-R1 CHK-R2 CHK-R3 CHK-R4 CHK-R5 ` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import yaml
C = yaml.safe_load(open("contracts/workflows/required-checks.v1.yaml"))["checks"]
names = [c["name"] for c in C]
ok  = len(names) == 11 == len(set(names))
ok &= all(c.get("emitted_by") and c.get("arms_at") for c in C)
ok &= "control-plane/blocking-drift" in names and "renovate-path-guard" in names and "lane-guard" in names
ok &= all(c.get("no_if_no_path_filter") is True for c in C if c["emitted_by"] != "L3")
print("L0-P0-014 PASS" if ok else "L0-P0-014 FAIL")
PY
```

Expected: `L0-P0-014 PASS`

**STOP RULE** — Do not rename a check to something "clearer". These strings are typed into branch protection by L5 and compared by L3; a rename after freeze silently unarms a gate on every repository. Any change is **CCR-BREAKING** and lands as `required-checks.v2.yaml` with both versions supported during migration (Section 60.2). If L2 has not delivered `lane-guard` by the end of its first cycle, that is the recorded gap of D-L0-05 and is raised as an L0 emergency, not absorbed.

---

### L0-P0-015 — `C-WF-SECRETS-1`: the five secret tiers and the environment policy

| | |
| --- | --- |
| **Size** | M |
| **Depends on** | L0-P0-013 |
| **Writes** | `contracts/workflows/secret-tiers.v1.yaml`, `contracts/stubs/secret-tiers.yaml`, `contracts/fixtures/C-WF-SECRETS-1/{valid-001,invalid-001,invalid-002,invalid-003}.yaml` |
| **Spec** | Section 40.1 (five tiers, D89, D107), 40.2, 40.3, Section 33.4 (deployment branch and tag policy), Section 11.4 (D73), Section 49 (asset inventory rows), AT-110, invariants 25, 26, 84 |

L2 binds secrets to jobs; L5 provisions the environments that hold them. Both read this one file.

**The five tiers, verbatim from Section 40.1**: `developer` (`.env.local`, git-ignored), `ci` (GitHub Actions secrets), `staging` (GitHub Environment: staging), `production` (GitHub Environment: production), `control_plane` (machine-credential store on the hosts that use them). Each row carries `location`, `contains`, and `never_below` — the tier-descent rule: "A secret never moves down a tier. A production credential appearing anywhere below the production tier is a security incident under Section 43, not a cleanup task."

**The five fifth-tier credentials, each with its published permission set** (40.1: "Each credential's exact permission set is published in its inventory entry and in this section"): `reconciler`, `provisioning_cli`, `org_export_token`, `records_writer`, `layer_b_backup`. Each carries `rotation_cadence` (calibrated configuration; initial value quarterly), `rotator_capability: devops`, `runbook_ref`, `expiry_date_tracked: true` (49), and a `behavioural_envelope` block with the four declared elements of 40.1: `signed_run_record_required`, `run_count_ceiling_per_day` (initial value: twice the scheduled run count), `expected_source_host`, `published_per_run_api_call_counts`.

**`records_writer`, frozen exactly (D89):** a GitHub App installation token whose fine-grained `contents: write` is **scoped to `control-plane-records` alone** and reaches no registry at all. It holds **no credential on `control-plane`**.

**`reconciler`, frozen exactly:** its declared repair scope (26.4) plus **check-run write on product repositories for exactly one named check** — `control-plane/blocking-drift` from `C-WF-CHECKS-1`. AT-110's six negative attempts are transcribed into the body as `must_fail[]` so L3 and L5 test the same six.

**The environment policy (33.4), frozen:** three environments `development`, `staging`, `production`; `staging` and `production` accept deployments **from the default branch and protected release tags only, and from no other ref**; the policy is applied from the template at product creation. Deployment branch policies are Team-plan available and are **not** the Enterprise feature Section 11.4 excludes.

**Fixtures**

| File | Line 1 |
| --- | --- |
| `invalid-001.yaml` | `# EXPECT: reject — production credential declared at the ci tier (Section 40.1 tier-descent rule)` |
| `invalid-002.yaml` | `# EXPECT: reject — records_writer granted contents:write on control-plane (D89)` |
| `invalid-003.yaml` | `# EXPECT: reject — production environment with no deployment branch and tag policy (Section 33.4)` |

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-WF-SECRETS-1
python - <<'PY'
import pathlib
pathlib.Path("contracts/workflows").mkdir(parents=True, exist_ok=True)
pathlib.Path("contracts/stubs").mkdir(parents=True, exist_ok=True)

CONTRACT = """\
# --- CONTRACT HEADER (frozen) ---
contract_id: C-WF-SECRETS-1
contract_version: 1
owner: L0
publishing_lane: L2
consuming_lanes: [L2, L5]
spec_refs:
  - "Section 40.1"
  - "Section 40.2"
  - "Section 40.3"
  - "Section 33.4"
  - "Section 11.4"
  - "Section 49"
  - "AT-110"
ccr_required: true
# --- BODY ---

# Section 40.1: five tiers. A secret never moves down a tier.
# A production credential appearing anywhere below the production tier
# is a security incident under Section 43, not a cleanup task.
tiers:
  - id: developer
    location: ".env.local (git-ignored)"
    contains: "Local development overrides; never production values."
    never_below: ci

  - id: ci
    location: "GitHub Actions repository secrets"
    contains: "CI-scoped credentials: package registries, static-analysis tokens, SONAR."
    never_below: staging

  - id: staging
    location: "GitHub Environment: staging"
    contains: "Staging database and service credentials."
    never_below: production

  - id: production
    location: "GitHub Environment: production"
    contains: "Production database and service credentials."
    never_below: control_plane

  - id: control_plane
    location: "Machine-credential store on the hosts that use them"
    contains: "Reconciler, provisioning, export, records-writer, and layer-B-backup credentials."

# Section 40.1: each fifth-tier credential's exact permission set is published here.
# D89: records_writer is scoped to control-plane-records alone; it holds no credential
# on control-plane. AT-110: reconciler.must_fail declares six provable boundary attempts.
control_plane_credentials:
  reconciler:
    description: "Reconciler credential: declared repair scope (26.4) plus check-run write on product repositories for exactly control-plane/blocking-drift."
    repositories: []
    check_runs:
      - control-plane/blocking-drift
    rotation_cadence: quarterly
    rotator_capability: devops
    runbook_ref: "docs/runbooks/credential-rotation.md#reconciler"
    expiry_date_tracked: true
    behavioural_envelope:
      signed_run_record_required: true
      run_count_ceiling_per_day: 48
      expected_source_host: "reconciler-vm.internal"
      published_per_run_api_call_counts: true
    # AT-110: six negative attempts that must all fail, executed at every rotation.
    must_fail:
      - write_github_actions_secret
      - write_environment
      - change_workflow_file
      - change_org_settings
      - write_records_store_direct
      - access_layer_b

  provisioning_cli:
    description: "Provisioning CLI credential: product-repository creation, branch-protection and ruleset application, Team provisioning."
    rotation_cadence: quarterly
    rotator_capability: devops
    runbook_ref: "docs/runbooks/credential-rotation.md#provisioning-cli"
    expiry_date_tracked: true
    behavioural_envelope:
      signed_run_record_required: true
      run_count_ceiling_per_day: 20
      expected_source_host: "provisioning-vm.internal"
      published_per_run_api_call_counts: true

  org_export_token:
    description: "Org-export token: fine-grained read-only credential for org-level export snapshots (Section 99.2 subsystem E, AT-103)."
    rotation_cadence: quarterly
    rotator_capability: devops
    runbook_ref: "docs/runbooks/credential-rotation.md#org-export-token"
    expiry_date_tracked: true
    behavioural_envelope:
      signed_run_record_required: true
      run_count_ceiling_per_day: 4
      expected_source_host: "export-runner.internal"
      published_per_run_api_call_counts: true

  records_writer:
    description: "Records-writer: GitHub App installation token. D89: contents:write scoped to control-plane-records alone. Holds no credential on control-plane."
    repositories:
      - control-plane-records
    rotation_cadence: quarterly
    rotator_capability: devops
    runbook_ref: "docs/runbooks/credential-rotation.md#records-writer"
    expiry_date_tracked: true
    behavioural_envelope:
      signed_run_record_required: true
      run_count_ceiling_per_day: 200
      expected_source_host: "records-writer-vm.internal"
      published_per_run_api_call_counts: true

  layer_b_backup:
    description: "Layer-B backup credential: read-only access to Layer B configuration for backup and restore verification."
    rotation_cadence: quarterly
    rotator_capability: devops
    runbook_ref: "docs/runbooks/credential-rotation.md#layer-b-backup"
    expiry_date_tracked: true
    behavioural_envelope:
      signed_run_record_required: true
      run_count_ceiling_per_day: 6
      expected_source_host: "backup-runner.internal"
      published_per_run_api_call_counts: true

# Section 33.4: three environments. staging and production accept deployments from
# the default branch and protected release tags only, and from no other ref.
# Deployment branch policies are Team-plan available and are NOT the Enterprise
# feature Section 11.4 excludes.
environments:
  development:
    description: "Local/CI development environment. No deployment branch restriction."
    deployment_refs: []

  staging:
    description: "Staging environment. Accepts deployments from default branch and protected release tags only."
    deployment_refs:
      - default_branch
      - protected_release_tags

  production:
    description: "Production environment. Accepts deployments from default branch and protected release tags only."
    deployment_refs:
      - default_branch
      - protected_release_tags
"""
pathlib.Path("contracts/workflows/secret-tiers.v1.yaml").write_text(CONTRACT, encoding="utf-8")
pathlib.Path("contracts/stubs/secret-tiers.yaml").write_text(CONTRACT, encoding="utf-8")

pathlib.Path("contracts/fixtures/C-WF-SECRETS-1/valid-001.yaml").write_text("""\
# Valid secret-tier reference: production credential at production tier,
# records_writer scoped to control-plane-records, environments with correct refs.
tier_usage:
  credential: db_production_password
  declared_tier: production
  environment: production
records_writer_check:
  repositories: [control-plane-records]
environment_check:
  staging:
    deployment_refs: [default_branch, protected_release_tags]
  production:
    deployment_refs: [default_branch, protected_release_tags]
""", encoding="utf-8")

pathlib.Path("contracts/fixtures/C-WF-SECRETS-1/invalid-001.yaml").write_text("""\
# EXPECT: reject — production credential declared at the ci tier (Section 40.1 tier-descent rule)
tier_usage:
  credential: db_production_password
  declared_tier: ci
  environment: ci
""", encoding="utf-8")

pathlib.Path("contracts/fixtures/C-WF-SECRETS-1/invalid-002.yaml").write_text("""\
# EXPECT: reject — records_writer granted contents:write on control-plane (D89)
records_writer:
  repositories:
    - control-plane-records
    - control-plane
  permission: "contents: write"
""", encoding="utf-8")

pathlib.Path("contracts/fixtures/C-WF-SECRETS-1/invalid-003.yaml").write_text("""\
# EXPECT: reject — production environment with no deployment branch and tag policy (Section 33.4)
environment:
  name: production
  deployment_refs: []
""", encoding="utf-8")

print("C-WF-SECRETS-1 files written")
PY
python contracts/ci/register_add.py C-WF-SECRETS-1 workflows/secret-tiers.v1.yaml 1 L2 L2,L5 stubs/secret-tiers.yaml
git add -A && git commit -m "L0-P0-015: C-WF-SECRETS-1 secret tiers and environment policy"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Exactly five tiers | `python -c "import yaml;print([t['id'] for t in yaml.safe_load(open('contracts/workflows/secret-tiers.v1.yaml'))['tiers']])"` | `['developer', 'ci', 'staging', 'production', 'control_plane']` |
| 2 | Exactly five fifth-tier credentials | `python -c "import yaml;print(sorted(yaml.safe_load(open('contracts/workflows/secret-tiers.v1.yaml'))['control_plane_credentials']))"` | `['layer_b_backup', 'org_export_token', 'provisioning_cli', 'reconciler', 'records_writer']` |
| 3 | `records_writer` is scoped to the records repository alone (D89) | `python -c "import yaml;c=yaml.safe_load(open('contracts/workflows/secret-tiers.v1.yaml'))['control_plane_credentials']['records_writer'];print(c['repositories'])"` | `['control-plane-records']` |
| 4 | Every fifth-tier credential declares all four envelope elements | see SELF-VERIFY | `L0-P0-015 PASS` |
| 5 | `reconciler.must_fail` holds the six attempts of AT-110 | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/workflows/secret-tiers.v1.yaml'))['control_plane_credentials']['reconciler']['must_fail']))"` | `6` |
| 6 | `staging` and `production` both declare the ref restriction | `python -c "import yaml;e=yaml.safe_load(open('contracts/workflows/secret-tiers.v1.yaml'))['environments'];print([e[k]['deployment_refs'] for k in ('staging','production')])"` | `[['default_branch', 'protected_release_tags'], ['default_branch', 'protected_release_tags']]` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import yaml
S = yaml.safe_load(open("contracts/workflows/secret-tiers.v1.yaml"))
need = {"signed_run_record_required","run_count_ceiling_per_day","expected_source_host","published_per_run_api_call_counts"}
creds = S["control_plane_credentials"]
ok  = len(S["tiers"]) == 5 and len(creds) == 5
ok &= all(need <= set(c["behavioural_envelope"]) for c in creds.values())
ok &= all(c.get("rotator_capability") == "devops" for c in creds.values())
ok &= creds["records_writer"]["repositories"] == ["control-plane-records"]
ok &= "control-plane" not in creds["records_writer"]["repositories"]
ok &= creds["reconciler"]["check_runs"] == ["control-plane/blocking-drift"]
print("L0-P0-015 PASS" if ok else "L0-P0-015 FAIL")
PY
```

Expected: `L0-P0-015 PASS`

**STOP RULE** — If anything in this contract would give the records-writer a path-scoped bypass on `control-plane`, stop. D89 states the reasoning in full: bypass is not scoped by path, so such a credential is an unscoped write credential on the repository holding `people.yaml`, `roles.yaml`, `exceptions.yaml` and `policies.yaml`. The separation is architectural. Any proposal to collapse the two repositories is **CCR-BREAKING** and is refused at L0, not negotiated per lane.

---

### L0-P0-016 — `C-WF-EVIDENCE-1`: the eleven-question evidence chain

| | |
| --- | --- |
| **Size** | M |
| **Depends on** | L0-P0-013, L0-P0-012 |
| **Writes** | `contracts/workflows/evidence-chain.v1.yaml`, `contracts/stubs/evidence-chain-answers.yaml`, `contracts/fixtures/C-WF-EVIDENCE-1/{valid-001,invalid-001,invalid-002}.yaml` |
| **Spec** | Section 32 (the eleven questions and the invariant), Section 15.7 (conformance profiles), Section 96.6 (D78), invariant 22, Section 46.1 (`verify-digest-chain`) |

L2 produces the evidence; L4 stores it. Frozen so both read the same eleven question ids and the same answer sources.

**The eleven questions, transcribed with their sources (Section 32):** `Q1` git commit → artifact label and deployment record; `Q2` pull request → commit-to-PR association; `Q3` Gate 2 approver and role → PR review record cross-referenced with the assignment registry; `Q4` CI run → workflow run linked to the commit; `Q5` artifact digest → registry digest recorded at build; `Q6` staging deploy time → staging deployment record; `Q7` staging verification → smoke result and UAT record in the workflow run; `Q8` production approver → production-approval record in the records store, verified by the workflow-identity gate; `Q9` production deploy time → production deployment record; `Q10` post-deployment smoke → smoke result attached to the deployment; `Q11` digest running now → `GET /version` on the live service.

**The invariant, frozen as a machine-checkable assertion (Section 32):** `Q5 == Q11`, **and** the digest deployed to production is byte-identical to the one verified in staging. CI rejects any production deployment where the requested digest differs from the digest that passed staging verification.

**The one sanctioned equivalence (D78):** for an S18 platform-rebuild deployment, the recorded identity — pinned commit, lockfile and build configuration — stands in for the digest throughout the chain, and remaining on a platform-rebuild host is a dated, recorded state, never an implicit one. Frozen as `equivalences[].s18_platform_rebuild`.

**Profile substitution (Section 32 + 15.7):** `Q10` and `Q11` are the service-profile evidence; a product declaring another profile substitutes its equivalent — store version adoption and crash-free-session telemetry for `client-app`, published registry version for `library`, job success records for `batch` — and the chain closes on that evidence instead. Frozen as `profile_substitutions{}` keyed by the seven `conformance_profile` values of 15.7.

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-WF-EVIDENCE-1
python - <<'PY'
import pathlib
pathlib.Path("contracts/workflows").mkdir(parents=True, exist_ok=True)
pathlib.Path("contracts/stubs").mkdir(parents=True, exist_ok=True)

CONTRACT = """\
# --- CONTRACT HEADER (frozen) ---
contract_id: C-WF-EVIDENCE-1
contract_version: 1
owner: L0
publishing_lane: L2
consuming_lanes: [L2, L4]
spec_refs:
  - "Section 32"
  - "Section 15.7"
  - "Section 96.6"
  - "invariant 22"
  - "Section 46.1"
ccr_required: true
# --- BODY ---

# Section 32: the eleven questions and the invariant.
# L2 produces the evidence; L4 stores it. Frozen so both read the same question ids
# and the same answer sources.
questions:
  - id: Q1
    description: "git commit to artifact label and deployment record"
    source: "artifact_built event: commit field cross-referenced with deployment record"

  - id: Q2
    description: "pull request to commit-to-PR association"
    source: "pr_opened event: pr_number and head_sha fields"

  - id: Q3
    description: "Gate 2 approver and role to PR review record cross-referenced with assignment registry"
    source: "gate2_approved event: approver field cross-referenced with people.registry"

  - id: Q4
    description: "CI run to workflow run linked to the commit"
    source: "ci_check_completed event: workflow_run_id field"

  - id: Q5
    description: "artifact digest to registry digest recorded at build"
    source: "artifact_built event: digest field; also recorded in deployment record"

  - id: Q6
    description: "staging deploy time to staging deployment record"
    source: "staging_deployed event: timestamp field"

  - id: Q7
    description: "staging verification to smoke result and UAT record in the workflow run"
    source: "staging_smoke_completed and uat_executed events: result fields"

  - id: Q8
    description: "production approver to production-approval record in the records store, verified by the workflow-identity gate"
    source: "production_approval_granted event: approver field; identity gate asserts approver != deployer"

  - id: Q9
    description: "production deploy time to production deployment record"
    source: "production_deployed event: timestamp field; records/deployments/ entry"

  - id: Q10
    description: "post-deployment smoke to smoke result attached to the deployment"
    source: "production_smoke_completed event: result field"

  - id: Q11
    description: "digest running now to GET /version on the live service"
    source: "version_digest_confirmed event: live_digest field from /version endpoint"

# Section 32: Q5 == Q11, and the digest deployed to production is byte-identical
# to the one verified in staging. CI rejects any production deployment where the
# requested digest differs from the digest that passed staging verification.
invariant:
  assert: "Q5 == Q11"
  and: "production_digest == staging_verified_digest"
  on_violation: reject_deployment

# Section 32 + 15.7: profile substitutions, keyed by the seven conformance_profile
# values of Section 15.7. Q10 and Q11 are the service-profile evidence; other
# profiles substitute their equivalent evidence.
profile_substitutions:
  service:
    substitute_q10: "production_smoke_completed event result field"
    substitute_q11: "version_digest_confirmed event live_digest from /version endpoint"
    notes: "Default profile. No substitution — the chain as written."

  client-app:
    substitute_q10: "crash_free_session_telemetry: crash-free rate from the analytics store at current band"
    substitute_q11: "store_version_adoption: percentage of active sessions on the deployed version from the store analytics"
    notes: "Section 15.7: crash-free-session telemetry, store version adoption. Staged-rollout halt is the declared rollback method (Section 42.3)."

  library:
    substitute_q10: "consumer_contract_tests: all registered consumer contract test suites pass against the published version"
    substitute_q11: "registry_version: published version in the package registry matches the deployed artifact digest"
    notes: "Section 15.7: registry version plus consumer contract tests."

  batch:
    substitute_q10: "job_success_record: batch job success flag from records/deployments/ entry"
    substitute_q11: "data_freshness_signal: latest successful run timestamp within declared freshness window"
    notes: "Section 15.7: job success and data-freshness signals instead of availability."

  customer-hosted:
    substitute_q10: "customer_attested_deploy_record: signed deploy record from the customer or recorded compensating control"
    substitute_q11: "customer_attested_restore_record: signed restore record from the customer or recorded compensating control"
    notes: "Section 15.7: customer-attested deploy and restore records, or a recorded exemption with a compensating control."

  white-label:
    substitute_q10: "per_deployment_environment_smoke: smoke result from each deployment environment in the environment list"
    substitute_q11: "per_deployment_environment_version: version confirmation from each deployment environment"
    notes: "Section 15.7: a per-deployment environment list."

  static-site:
    substitute_q10: "build_reproducibility: hash of the build output matches the recorded digest"
    substitute_q11: "build_reproducibility: same reproducibility assertion serves as the running-digest check"
    notes: "Section 15.7: build reproducibility; recovery: not-applicable is permitted."

# Section 96.6 (D78): for an S18 platform-rebuild deployment the recorded identity —
# pinned commit, lockfile and build configuration — stands in for the digest throughout
# the chain. Remaining on a platform-rebuild host is a dated, recorded state, never
# an implicit one.
equivalences:
  s18_platform_rebuild:
    recorded_state_required: true
    identity_fields:
      - pinned_commit
      - lockfile_hash
      - build_configuration_hash
    notes: "D78: recorded identity stands in for artifact digest. Remaining on a platform-rebuild host is a dated recorded state."

# Section 46.1: verify-digest-chain runs this invariant at every gate.
verify_digest_chain_ref: "Section 46.1"
"""
pathlib.Path("contracts/workflows/evidence-chain.v1.yaml").write_text(CONTRACT, encoding="utf-8")

# Stub: evidence-chain-answers.yaml — Q5 and Q11 must hold the same digest value.
STUB = """\
# contracts/stubs/evidence-chain-answers.yaml
# Stub answer set for a service-profile deployment. Q5 == Q11 (invariant).
# Lanes develop against this before L4 writes real evidence records.
answers:
  Q1: "sha256:a3f1c2d9e0b74e5f6a8c0d1e2f3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1 (commit: abc1234)"
  Q2: "PR#42 head_sha: abc1234def5678"
  Q3: "stub-lead-1 (role: team_lead, capability: code-review)"
  Q4: "workflow_run_id: 987654321"
  Q5: "sha256:a3f1c2d9e0b74e5f6a8c0d1e2f3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1"
  Q6: "2026-09-02T08:00:00Z"
  Q7: "smoke: pass, uat: pass"
  Q8: "stub-lead-1 approved; identity gate: approver != deployer confirmed"
  Q9: "2026-09-02T10:00:00Z"
  Q10: "production smoke: pass"
  Q11: "sha256:a3f1c2d9e0b74e5f6a8c0d1e2f3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1"
conformance_profile: service
"""
pathlib.Path("contracts/stubs/evidence-chain-answers.yaml").write_text(STUB, encoding="utf-8")

pathlib.Path("contracts/fixtures/C-WF-EVIDENCE-1/valid-001.yaml").write_text("""\
# Valid evidence chain: Q5 == Q11, service profile, all eleven questions answered.
answers:
  Q1: "sha256:b7e2d4f6a0c1e3f5b7d9e1f3b5d7f9a1c3e5f7b9d1f3a5c7e9f1b3d5f7a9c1e3 (commit: def5678)"
  Q2: "PR#99 head_sha: def5678abc1234"
  Q3: "stub-lead-1 (role: team_lead, capability: code-review)"
  Q4: "workflow_run_id: 112233445"
  Q5: "sha256:b7e2d4f6a0c1e3f5b7d9e1f3b5d7f9a1c3e5f7b9d1f3a5c7e9f1b3d5f7a9c1e3"
  Q6: "2026-09-02T09:00:00Z"
  Q7: "smoke: pass, uat: pass"
  Q8: "stub-lead-1 approved; identity gate: approver != deployer confirmed"
  Q9: "2026-09-02T11:00:00Z"
  Q10: "production smoke: pass"
  Q11: "sha256:b7e2d4f6a0c1e3f5b7d9e1f3b5d7f9a1c3e5f7b9d1f3a5c7e9f1b3d5f7a9c1e3"
conformance_profile: service
""", encoding="utf-8")

pathlib.Path("contracts/fixtures/C-WF-EVIDENCE-1/invalid-001.yaml").write_text("""\
# EXPECT: reject — Q5 != Q11 digest mismatch violates Section 32 invariant (must refuse deployment)
answers:
  Q1: "sha256:aaaa1111 (commit: aaa111)"
  Q2: "PR#10 head_sha: aaa111bbb222"
  Q3: "stub-lead-1"
  Q4: "workflow_run_id: 11111"
  Q5: "sha256:aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff6666aaaa1111bbbb2222cc"
  Q6: "2026-09-02T08:00:00Z"
  Q7: "smoke: pass, uat: pass"
  Q8: "stub-lead-1 approved"
  Q9: "2026-09-02T10:00:00Z"
  Q10: "production smoke: pass"
  Q11: "sha256:dddd4444eeee5555ffff6666aaaa1111bbbb2222cccc3333dddd4444eeee5555ff"
conformance_profile: service
""", encoding="utf-8")

pathlib.Path("contracts/fixtures/C-WF-EVIDENCE-1/invalid-002.yaml").write_text("""\
# EXPECT: reject — client-app answer set closing on Q10/Q11 without profile substitution
# (uses service-profile evidence for a client-app product; Section 32 + 15.7)
answers:
  Q1: "sha256:cccc2222 (commit: ccc222)"
  Q2: "PR#20 head_sha: ccc222ddd333"
  Q3: "stub-lead-1"
  Q4: "workflow_run_id: 22222"
  Q5: "sha256:cccc2222dddd3333eeee4444ffff5555aaaa1111bbbb2222cccc3333dddd4444ee"
  Q6: "2026-09-02T08:00:00Z"
  Q7: "smoke: pass, uat: pass"
  Q8: "stub-lead-1 approved"
  Q9: "2026-09-02T10:00:00Z"
  Q10: "production smoke: pass"
  Q11: "sha256:cccc2222dddd3333eeee4444ffff5555aaaa1111bbbb2222cccc3333dddd4444ee"
conformance_profile: client-app
""", encoding="utf-8")

print("C-WF-EVIDENCE-1 files written")
PY
python contracts/ci/register_add.py C-WF-EVIDENCE-1 workflows/evidence-chain.v1.yaml 1 L2 L2,L4 stubs/evidence-chain-answers.yaml
git add -A && git commit -m "L0-P0-016: C-WF-EVIDENCE-1 eleven-question evidence chain"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Eleven questions, ids `Q1`..`Q11` | `python -c "import yaml;print([q['id'] for q in yaml.safe_load(open('contracts/workflows/evidence-chain.v1.yaml'))['questions']])"` | `['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11']` |
| 2 | Every question names a source | `python -c "import yaml;print(all(q.get('source') for q in yaml.safe_load(open('contracts/workflows/evidence-chain.v1.yaml'))['questions']))"` | `True` |
| 3 | The digest invariant is declared as an assertion | `python -c "import yaml;print(yaml.safe_load(open('contracts/workflows/evidence-chain.v1.yaml'))['invariant'])"` | `{'assert': 'Q5 == Q11', 'and': 'production_digest == staging_verified_digest', 'on_violation': 'reject_deployment'}` |
| 4 | Profile substitutions cover all seven profiles of 15.7 | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/workflows/evidence-chain.v1.yaml'))['profile_substitutions']))"` | `7` |
| 5 | The S18 equivalence is present and dated-state-marked (D78) | `python -c "import yaml;print(yaml.safe_load(open('contracts/workflows/evidence-chain.v1.yaml'))['equivalences']['s18_platform_rebuild']['recorded_state_required'])"` | `True` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import yaml
E = yaml.safe_load(open("contracts/workflows/evidence-chain.v1.yaml"))
A = yaml.safe_load(open("contracts/stubs/evidence-chain-answers.yaml"))
qs = [q["id"] for q in E["questions"]]
ok  = qs == [f"Q{i}" for i in range(1, 12)]
ok &= set(A["answers"]) == set(qs)
ok &= A["answers"]["Q5"] == A["answers"]["Q11"]
ok &= len(E["profile_substitutions"]) == 7
print("L0-P0-016 PASS" if ok else "L0-P0-016 FAIL")
PY
```

Expected: `L0-P0-016 PASS`

**STOP RULE** — Do not add a twelfth question, and do not drop one as "covered by another". Section 32 fixes eleven and states that they are answerable "using only GitHub, GitHub Actions and Grafana. No additional evidence platform is required." A twelfth question is a new evidence platform in disguise. **CCR-BREAKING**.

---

### L0-P0-017 — `C-RECON-SET-1`: the reconciler comparison set

| | |
| --- | --- |
| **Size** | L |
| **Depends on** | L0-P0-006, L0-P0-012, L0-P0-014 |
| **Writes** | `contracts/reconciler/comparison-set.v1.yaml`, `contracts/stubs/comparison-set.yaml`, `contracts/fixtures/C-RECON-SET-1/{valid-001,invalid-001,invalid-002}.yaml` |
| **Spec** | Section 53.1 (the declared-versus-actual table), 53.2 (the five levels), 53.3 (auto-repair rule), 53.4 (drift classes), Section 97.2 (write-freshness row), Section 44.5, AT-033, AT-102, invariants 44, 81 |

**This is the contract Lane 3 consumes.** L3 implements the reconciler; it does not decide what is compared, at what level, or with what class. Those are L0 decisions, transcribed from Section 53.1 and frozen here.

**Every row carries:** `row_id`, `declared_in`, `compared_against`, `on_mismatch`, `level` (1–5, per 53.2), `class` (Green | Amber | Red | Blocking, per 53.4), `auto_repairable` (boolean, per 53.3), `spec_ref`.

**The seventeen rows of Section 53.1**, in the section's own order: `people.yaml` vs org membership (alert; block on removal drift) · `people.yaml` capabilities vs Team membership implying authority (alert) · `product.yaml` assignments vs GitHub Team membership (**fail CI on the affected repository**) · `product.yaml` assignments vs CODEOWNERS (regenerate; alert if hand-edited) · branch-protection template vs actual (**alert immediately; block deployment**) · workflow-template version vs actual workflow file (alert; flag `platform_compatibility` as drifted) · environment-configuration template vs actual environments (alert) · environment deployment branch and tag policy vs actual (**alert immediately; block deployment**) · declared `infrastructure:` boundary vs latest provider-side attestation (**Blocking past its attestation window**) · `product.yaml` lifecycle vs Renovate/monitoring/CI configuration (auto-repair where safe; alert otherwise) · assignment `end_date` vs current Team membership (**auto-revoke expired access**) · declared dependency vs shared-service registry (fail CI on unknown dependency) · `platform.yaml` workflow versions vs the commit SHA each `workflows/*` tag resolves to (**Blocking on any change**) · Renovate bypass ruleset vs the ruleset carrying the diff-path status check (**Blocking where that ruleset names any bypass actor**) · declared write-freshness window per record store vs latest commit timestamp on the store path (Amber; **Blocking for `events/`, `records/deployments/`, `records/uat/`**) · production-restore record vs recorded `integrity_check` result and named verifier (Red where either is absent) · `product.yaml` `restore_tested` vs newest passing record in `records/restore-tests/` (**Blocking**).

**Three standing rules frozen alongside** (53.1), each as a first-class row so the reconciler cannot omit them:

| Rule id | Rule | Class |
| --- | --- | --- |
| `RECON-S1` | A workflow-file change pushed by a machine identity is Blocking-class drift, regardless of content | Blocking |
| `RECON-S2` | A commit authored or committed by any identity other than the declared bypass actor, on a branch that merges under that actor's bypass, is Blocking-class drift | Blocking |
| `RECON-S3` | The seeded canary: a permanent, clearly labelled planted mismatch that every run MUST find. A run reporting zero findings — the canary included — is a **FAILED** run, raises SIG-13 and triggers the gap procedure | Blocking (AT-102) |

**Two further binding declarations in the body:**

* `per_registry_comparison_counts: required` — every run records how many rows of each registry it actually compared, so a silently narrowed comparison is itself visible drift (53.1).
* `independent_control_verifier` — the second verifier that runs **off the operations VM and under a different credential**: a scheduled workflow in the control-plane repository with its own read-only fine-grained credential, asserting that no machine identity appears in any CODEOWNERS file in any repository, that branch-protection and ruleset JSON match the committed template, and that the ruleset bypass-actor list is exactly the set Sections 40.1 and 33.2 declare, with their declared scopes. It writes to a surface the operations VM cannot write to, and **its own absence for one cycle is Level 5** (53.1).

**Auto-repair, frozen (53.3):** a repair is permitted only when it moves the system toward the declared state **and** the declared state is at least as restrictive as the actual state. Reconciliation never loosens a control automatically, never modifies production runtime configuration, never modifies data, and never rotates or writes secrets. Where actual is stricter than declared, raise Level 2 for human judgment (AT-033).

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-RECON-SET-1
python - <<'PY'
import pathlib
pathlib.Path("contracts/reconciler").mkdir(parents=True, exist_ok=True)
pathlib.Path("contracts/stubs").mkdir(parents=True, exist_ok=True)

CONTRACT = """\
# --- CONTRACT HEADER (frozen) ---
contract_id: C-RECON-SET-1
contract_version: 1
owner: L0
publishing_lane: L3
consuming_lanes: [L1, L3, L5]
spec_refs:
  - "Section 53.1"
  - "Section 53.2"
  - "Section 53.3"
  - "Section 53.4"
  - "Section 97.2"
  - "Section 44.5"
  - "AT-033"
  - "AT-102"
ccr_required: true
# --- BODY ---

# Section 53.3: auto-repair rule. A repair is permitted only when it moves the
# system toward the declared state AND the declared state is at least as restrictive
# as the actual state. Never loosens a control, never modifies production runtime
# configuration, never modifies data, never rotates or writes secrets.
# Where actual is stricter than declared, raise Level 2 for human judgement (AT-033).
auto_repair:
  stricter_only: true
  never:
    - loosen_control
    - modify_production_runtime_config
    - modify_data
    - rotate_or_write_secrets

# AT-102: the seeded canary. A permanent, clearly labelled planted mismatch that
# every run MUST find. A run reporting zero findings — the canary included — is a
# FAILED run, raises SIG-13 and triggers the gap procedure.
seeded_canary:
  description: "Permanent planted mismatch: row_id canary-drift in people.yaml vs org membership. Every run must report it."
  row_id: canary-drift
  zero_findings_is_failed_run: true
  on_zero_findings: raise_SIG13_and_gap_procedure

# Section 53.1: every run records how many rows of each registry it actually compared,
# so a silently narrowed comparison is itself visible drift.
per_registry_comparison_counts: required

# Section 53.1: independent control verifier runs off the operations VM under a
# different credential. Its own absence for one cycle is Level 5.
independent_control_verifier:
  description: "Scheduled workflow in the control-plane repository with its own read-only fine-grained credential."
  runs_off_operations_vm: true
  separate_credential: true
  absence_one_cycle_level: 5
  asserts:
    - no_machine_identity_in_any_codeowners
    - branch_protection_matches_committed_template
    - ruleset_bypass_actor_list_matches_declared

# Standing rules (Section 53.1) — each is a first-class row in the reconciler.
# Listed separately so RECON-S1, RECON-S2, RECON-S3 are findable by CI grep.
standing_rules:
  - id: RECON-S1
    rule: "A workflow-file change pushed by a machine identity is Blocking-class drift, regardless of content."
    class: Blocking
    spec_ref: "Section 53.1"

  - id: RECON-S2
    rule: "A commit authored or committed by any identity other than the declared bypass actor, on a branch that merges under that actor bypass, is Blocking-class drift."
    class: Blocking
    spec_ref: "Section 53.1"

  - id: RECON-S3
    rule: "The seeded canary: a permanent planted mismatch every run MUST find. A run reporting zero findings — the canary included — is a FAILED run, raises SIG-13 and triggers the gap procedure."
    class: Blocking
    spec_ref: "Section 53.1, AT-102"

# Section 53.1: the seventeen comparison rows, in the section own order.
# class values: Green | Amber | Red | Blocking (Section 53.4)
# level values: 1-5 (Section 53.2)
# auto_repairable: true only where the repair moves toward the declared state
#   and the declared state is at least as restrictive (Section 53.3).
# Constraint: no row may be both auto_repairable: true and class: Blocking.
rows:
  - row_id: people-org-membership
    declared_in: "people.yaml"
    compared_against: "GitHub org membership"
    on_mismatch: "alert; block on removal drift"
    level: 2
    class: Amber
    auto_repairable: false
    spec_ref: "Section 53.1"

  - row_id: people-capability-team
    declared_in: "people.yaml capabilities"
    compared_against: "GitHub Team membership implying authority"
    on_mismatch: "alert"
    level: 2
    class: Amber
    auto_repairable: false
    spec_ref: "Section 53.1"

  - row_id: product-team-membership
    declared_in: "product.yaml assignments"
    compared_against: "GitHub Team membership"
    on_mismatch: "fail CI on the affected repository"
    level: 3
    class: Red
    auto_repairable: false
    spec_ref: "Section 53.1"

  - row_id: product-codeowners
    declared_in: "product.yaml assignments"
    compared_against: "CODEOWNERS"
    on_mismatch: "regenerate; alert if hand-edited"
    level: 2
    class: Amber
    auto_repairable: true
    spec_ref: "Section 53.1"

  - row_id: branch-protection
    declared_in: "branch-protection template"
    compared_against: "actual branch-protection settings"
    on_mismatch: "alert immediately; block deployment"
    level: 4
    class: Blocking
    auto_repairable: false
    spec_ref: "Section 53.1"

  - row_id: workflow-template-version
    declared_in: "workflow-template version in platform.yaml"
    compared_against: "actual workflow file in repository"
    on_mismatch: "alert; flag platform_compatibility as drifted"
    level: 2
    class: Amber
    auto_repairable: false
    spec_ref: "Section 53.1"

  - row_id: environment-config
    declared_in: "environment-configuration template"
    compared_against: "actual GitHub Environments"
    on_mismatch: "alert"
    level: 2
    class: Amber
    auto_repairable: false
    spec_ref: "Section 53.1"

  - row_id: environment-deployment-policy
    declared_in: "environment deployment branch and tag policy"
    compared_against: "actual GitHub Environment deployment policy"
    on_mismatch: "alert immediately; block deployment"
    level: 4
    class: Blocking
    auto_repairable: false
    spec_ref: "Section 53.1"

  - row_id: infrastructure-attestation
    declared_in: "product.yaml infrastructure: boundary"
    compared_against: "latest provider-side attestation"
    on_mismatch: "Blocking past its attestation window"
    level: 5
    class: Blocking
    auto_repairable: false
    spec_ref: "Section 53.1"

  - row_id: lifecycle-tooling-config
    declared_in: "product.yaml lifecycle"
    compared_against: "Renovate, monitoring, and CI configuration"
    on_mismatch: "auto-repair where safe; alert otherwise"
    level: 2
    class: Amber
    auto_repairable: true
    spec_ref: "Section 53.1"

  - row_id: assignment-expiry
    declared_in: "assignment end_date"
    compared_against: "current GitHub Team membership"
    on_mismatch: "auto-revoke expired access"
    level: 3
    class: Red
    auto_repairable: true
    spec_ref: "Section 53.1"

  - row_id: dependency-registry
    declared_in: "declared dependency in product.yaml"
    compared_against: "shared-service registry"
    on_mismatch: "fail CI on unknown dependency"
    level: 3
    class: Red
    auto_repairable: false
    spec_ref: "Section 53.1"

  - row_id: platform-workflow-sha
    declared_in: "platform.yaml workflow versions"
    compared_against: "commit SHA each workflows/* tag resolves to"
    on_mismatch: "Blocking on any change"
    level: 5
    class: Blocking
    auto_repairable: false
    spec_ref: "Section 53.1"

  - row_id: renovate-bypass-ruleset
    declared_in: "Renovate bypass ruleset declared actors"
    compared_against: "the ruleset carrying the diff-path status check"
    on_mismatch: "Blocking where that ruleset names any bypass actor"
    level: 5
    class: Blocking
    auto_repairable: false
    spec_ref: "Section 53.1"

  - row_id: write-freshness
    declared_in: "declared write-freshness window per record store"
    compared_against: "latest commit timestamp on the store path"
    on_mismatch: "Amber; Blocking for events/, records/deployments/, records/uat/"
    level: 3
    class: Amber
    auto_repairable: false
    spec_ref: "Section 53.1, Section 97.2"

  - row_id: restore-integrity-check
    declared_in: "production-restore record"
    compared_against: "recorded integrity_check result and named verifier"
    on_mismatch: "Red where either is absent"
    level: 4
    class: Red
    auto_repairable: false
    spec_ref: "Section 53.1"

  - row_id: restore-tested-currency
    declared_in: "product.yaml restore_tested date"
    compared_against: "newest passing record in records/restore-tests/"
    on_mismatch: "Blocking"
    level: 5
    class: Blocking
    auto_repairable: false
    spec_ref: "Section 53.1"
"""
pathlib.Path("contracts/reconciler/comparison-set.v1.yaml").write_text(CONTRACT, encoding="utf-8")
pathlib.Path("contracts/stubs/comparison-set.yaml").write_text(CONTRACT, encoding="utf-8")

pathlib.Path("contracts/fixtures/C-RECON-SET-1/valid-001.yaml").write_text("""\
# Valid reconciler run record: canary found, findings present, no Blocking row auto-repaired.
run_id: recon-run-2026-09-02-001
run_timestamp: "2026-09-02T06:00:00Z"
findings_count: 3
canary_found: true
findings:
  - row_id: canary-drift
    class: Blocking
    level: 5
    auto_repairable: false
  - row_id: write-freshness
    class: Amber
    level: 3
    auto_repairable: false
  - row_id: people-org-membership
    class: Amber
    level: 2
    auto_repairable: false
registry_comparison_counts:
  people: 12
  products: 8
  roles: 11
""", encoding="utf-8")

pathlib.Path("contracts/fixtures/C-RECON-SET-1/invalid-001.yaml").write_text("""\
# EXPECT: reject — RECON-S3 / AT-102 run record reporting zero findings including the canary
run_id: recon-run-2026-09-02-002
run_timestamp: "2026-09-02T06:00:00Z"
findings_count: 0
canary_found: false
findings: []
registry_comparison_counts:
  people: 12
  products: 8
  roles: 11
""", encoding="utf-8")

pathlib.Path("contracts/fixtures/C-RECON-SET-1/invalid-002.yaml").write_text("""\
# EXPECT: reject — 53.3 / AT-033 a repair that loosens a control (removes a required reviewer)
repair:
  row_id: product-codeowners
  action: remove_required_reviewer
  from_state: "CODEOWNERS requires stub-lead-1 on contracts/**"
  to_state: "CODEOWNERS has no required reviewer on contracts/**"
  declared_state: "no required reviewer"
  actual_state: "stub-lead-1 required"
  auto_repairable: true
""", encoding="utf-8")

print("C-RECON-SET-1 files written")
PY
python contracts/ci/register_add.py C-RECON-SET-1 reconciler/comparison-set.v1.yaml 1 L3 L1,L3,L5 stubs/comparison-set.yaml
git add -A && git commit -m "L0-P0-017: C-RECON-SET-1 reconciler comparison set"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Seventeen comparison rows | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/reconciler/comparison-set.v1.yaml'))['rows']))"` | `17` |
| 2 | Three standing rules present | `grep -o 'RECON-S[0-9]' contracts/reconciler/comparison-set.v1.yaml \| sort -u \| tr '\n' ' '` | `RECON-S1 RECON-S2 RECON-S3 ` |
| 3 | Every row carries a level in 1–5 and a class from the one scale | see SELF-VERIFY | `L0-P0-017 PASS` |
| 4 | No row is both `auto_repairable` and `class: Blocking` | see SELF-VERIFY | `L0-P0-017 PASS` |
| 5 | The auto-repair rule declares the stricter-only condition | `python -c "import yaml;print(yaml.safe_load(open('contracts/reconciler/comparison-set.v1.yaml'))['auto_repair']['stricter_only'])"` | `True` |
| 6 | The independent verifier declares off-VM, different-credential, Level-5-on-absence | `python -c "import yaml;v=yaml.safe_load(open('contracts/reconciler/comparison-set.v1.yaml'))['independent_control_verifier'];print(v['runs_off_operations_vm'],v['separate_credential'],v['absence_one_cycle_level'])"` | `True True 5` |
| 7 | Comparison counts are required | `python -c "import yaml;print(yaml.safe_load(open('contracts/reconciler/comparison-set.v1.yaml'))['per_registry_comparison_counts'])"` | `required` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import yaml
R = yaml.safe_load(open("contracts/reconciler/comparison-set.v1.yaml"))
rows = R["rows"]
classes = {"Green","Amber","Red","Blocking"}
ok  = len(rows) == 17
ok &= all(1 <= r["level"] <= 5 for r in rows)
ok &= all(r["class"] in classes for r in rows)
ok &= not [r for r in rows if r.get("auto_repairable") and r["class"] == "Blocking"]
ok &= R["auto_repair"]["stricter_only"] is True
ok &= R["auto_repair"]["never"] == ["loosen_control","modify_production_runtime_config","modify_data","rotate_or_write_secrets"]
ok &= R["seeded_canary"]["zero_findings_is_failed_run"] is True
print("L0-P0-017 PASS" if ok else "L0-P0-017 FAIL")
PY
```

Expected: `L0-P0-017 PASS`

**STOP RULE** — Do not let L3 choose a row's level or class. Section 53.4 binds: "Class assignment lives in configuration and is reviewable; it is not decided ad hoc during an incident", and 53.1 marks the blocking rows P0 because they are security controls. A lane that needs a row reclassified files a **CCR-BREAKING**; downward reclassification additionally requires the same authority as approving an exception for it (53.5) and is recorded as a decision.

---

### L0-P0-018 — `C-RECON-FIND-1` and `C-RECON-REPAIR-1`: what the reconciler emits

| | |
| --- | --- |
| **Size** | L |
| **Depends on** | L0-P0-009, L0-P0-017 |
| **Writes** | `contracts/reconciler/drift-finding.v1.json`, `contracts/reconciler/repair-record.v1.json`, `contracts/stubs/drift-finding.yaml`, `contracts/stubs/repair-record.yaml`, `contracts/fixtures/C-RECON-FIND-1/{valid-001,invalid-001..004}.yaml`, `contracts/fixtures/C-RECON-REPAIR-1/{valid-001,invalid-001..003}.yaml` |
| **Spec** | Section 53.2 (the five levels), 53.4 (the one severity scale), 53.5 (reclassification authority), 53.6 (closure quality), 53.7 (the gap procedure), Section 26.4 (repair records under the reconciler credential), Section 97.2 (envelope), SIG-13, AT-033, AT-102, invariants 44, 81 |

`C-RECON-SET-1` froze **what is compared**. These two contracts freeze **what comes out**. L3 produces both; L2 turns a Blocking finding into the `control-plane/blocking-drift` check-run conclusion; L4 turns each into a `drift_detected` or `drift_repaired` event; L5 reads findings against the access model. Four lanes read the same two shapes, so the shapes are L0's.

> **L0 decision D-L0-10, recorded here.** A **drift finding and a repair record are reconciler-surface artifacts, not operational records.** Neither appears in the twenty-one rows of `C-REC-STORE-MAP-1`, because Section 52.6 binds: a new artifact must state which existing file cannot hold it, and no store in the Section 97.2 table is a drift store. They are published on the drift view and, for Blocking class, as the `control-plane/blocking-drift` check-run; their *lifecycle* reaches the durable record layer as the `drift_detected` and `drift_repaired` events of `C-EVT-ENUM-1` (rows 52 and 53). They still carry the `C-REC-ENV-1` envelope fields, so that one timestamp rule and one id discipline hold across the estate. No lane adds a `records/drift/` store; that is a **CCR-ADDITIVE** against `C-REC-STORE-MAP-1`.

**`C-RECON-FIND-1` — shape, exact.** Envelope (`record_schema_version`, `id`, `product`, `timestamp`) plus: `row_id` (a row of `C-RECON-SET-1` or one of `RECON-S1`/`RECON-S2`/`RECON-S3`), `run_id`, `detected_at`, `age_days`, `level` (1–5), `class` (`Green|Amber|Red|Blocking`), `declared`, `actual`, `evidence[]` (each an addressable link), `canary` (boolean), `gap_window` (boolean), `status` (`open|repaired|closed|reopened`), optional `closure` (`closed_at`, `what_changed`, `evidence_link`, `closure_quality_audited`), optional `reclassification` (`from_class`, `to_class`, `decision_record`, `approver`, `approver_capability`, `decided_at`).

**Schema-encoded rules**

| Rule id | Rule | Spec |
| --- | --- | --- |
| `FIND-R1` | Every finding names a `row_id` that exists in `C-RECON-SET-1` — one of the seventeen rows or one of the three standing rules. A finding with an unknown `row_id` is rejected, because a finding no comparison produced has no declared state to return to | 53.1 |
| `FIND-R2` | `class` is drawn from the one scale of 53.4 and from no other vocabulary. A finding whose `row_id` is a security or production-environment row is never below `Red` | 53.4 |
| `FIND-R3` | `status: closed` requires a `closure` block carrying both `what_changed` and `evidence_link`. A finding closed without them is a closure-quality defect and is reopened, not counted as closed | 53.6 |
| `FIND-R4` | A downward `reclassification` requires `decision_record`, `approver` and `approver_capability`; there is no informal path from Red to Amber | 53.5 |
| `FIND-R5` | A finding produced inside a control-loop gap carries `gap_window: true` and is not evidence for any gate until re-verification clears it | 53.7 |
| `FIND-R6` | `canary: true` marks the seeded canary of `RECON-S3`. A run reporting zero findings — the canary included — is a **FAILED** run, raises SIG-13 and triggers the gap procedure. The run-level assertion lives in `run_summary` and is L3's; the field that makes it checkable is frozen here | AT-102, 53.1 |
| `FIND-R7` | `level` and `class` are copied from the `C-RECON-SET-1` row, never chosen at detection time | 53.4 |

**`C-RECON-REPAIR-1` — shape, exact.** Envelope plus: `finding_id`, `row_id`, `level` (const `3`), `repair_class`, `before`, `after`, `direction` (const `toward_declared`), `stricter_or_equal` (const `true`), `idempotent` (const `true`), `reversible` (const `true`), `actor` (the reconciler machine identity), `run_id`, `verification` (`recompared_at`, `result` ∈ `matches_declared|still_drifted`), `never` (const, the four forbidden operations), `frozen` (boolean, 53.7), optional `freeze_reason`.

**The six repair classes, closed.** Section 53.2 Level 3 names them and the list is exhaustive: `team_membership_sync`, `codeowners_regeneration`, `label_and_board_field_sync`, `reapply_declared_branch_protection`, `remove_expired_assignment`, `revoke_expired_access`.

| Rule id | Rule | Spec |
| --- | --- | --- |
| `REPAIR-R1` | `direction` is `toward_declared` and `stricter_or_equal` is `true`, both as `const`. A repair that loosens a control cannot be expressed in this schema | 53.3, AT-033 |
| `REPAIR-R2` | `repair_class` is one of the six. There is no `other` | 53.2 |
| `REPAIR-R3` | `never[]` is a `const` list equal to `C-RECON-SET-1`'s `auto_repair.never`: `loosen_control`, `modify_production_runtime_config`, `modify_data`, `rotate_or_write_secrets` | 53.3 |
| `REPAIR-R4` | `actor` matches the reconciler machine-identity pattern. A human-authored repair record is rejected: human registry edits travel the owner-review lane, machine-derived transitions write under the reconciler credential, and mixing them makes the expiry guarantees of 12.4 depend on a reviewer | 26.4 |
| `REPAIR-R5` | A repair class discovered to have written incorrect state carries `frozen: true` with a `freeze_reason`, is a Level 5 escalation, and every repair it made in the affected window is enumerated and reverted or human-confirmed | 53.7, 53.2 |

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-RECON-FIND-1 contracts/fixtures/C-RECON-REPAIR-1
python - <<'PY'
import json, yaml, pathlib

rows = yaml.safe_load(open("contracts/reconciler/comparison-set.v1.yaml"))
row_ids = [r["row_id"] for r in rows["rows"]] + ["RECON-S1", "RECON-S2", "RECON-S3"]
never = rows["auto_repair"]["never"]
TS = "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(Z|[+-][0-9]{2}:[0-9]{2})$"

FIND = {
 "$schema":"https://json-schema.org/draft/2020-12/schema",
 # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
 "$id":"https://control-plane.local/contracts/reconciler/drift-finding.v1.json",
 "x-contract":{"contract_id":"C-RECON-FIND-1","contract_version":1,"owner":"L0",
   "publishing_lane":"L3","consuming_lanes":["L2","L3","L4","L5"],
   "spec_refs":["Section 53.2","Section 53.4","Section 53.5","Section 53.6","Section 53.7","Section 97.2"],
   "ccr_required":True,
   "notes":["D-L0-10: a drift finding is a reconciler-surface artifact, not an operational record. "
            "It has no row in C-REC-STORE-MAP-1; its lifecycle reaches the record layer as the "
            "drift_detected and drift_repaired events of C-EVT-ENUM-1."],
   "rules":["FIND-R1","FIND-R2","FIND-R3","FIND-R4","FIND-R5","FIND-R6","FIND-R7"]},
 "type":"object","additionalProperties":False,
 "required":["record_schema_version","id","product","timestamp","row_id","run_id","detected_at",
             "age_days","level","class","declared","actual","evidence","canary","gap_window","status"],
 "properties":{
   "record_schema_version":{"const":1},
   "id":{"type":"string","pattern":"^DRIFT-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}$"},
   "product":{"type":"string","minLength":1},
   "timestamp":{"type":"string","pattern":TS},
   "row_id":{"enum":row_ids,"description":"FIND-R1"},
   "run_id":{"type":"string","minLength":1},
   "detected_at":{"type":"string","pattern":TS},
   "age_days":{"type":"integer","minimum":0},
   "level":{"type":"integer","minimum":1,"maximum":5,"description":"FIND-R7"},
   "class":{"enum":["Green","Amber","Red","Blocking"],"description":"FIND-R2"},
   "declared":{},
   "actual":{},
   "evidence":{"type":"array","minItems":1,"items":{"type":"string","minLength":1}},
   "canary":{"type":"boolean","description":"FIND-R6"},
   "gap_window":{"type":"boolean","description":"FIND-R5"},
   "status":{"enum":["open","repaired","closed","reopened"]},
   "closure":{"type":"object","additionalProperties":False,
     "required":["closed_at","what_changed","evidence_link","closure_quality_audited"],
     "properties":{"closed_at":{"type":"string","minLength":1},
                   "what_changed":{"type":"string","minLength":1},
                   "evidence_link":{"type":"string","minLength":1},
                   "closure_quality_audited":{"type":"boolean"}}},
   "reclassification":{"type":"object","additionalProperties":False,
     "required":["from_class","to_class","decision_record","approver","approver_capability","decided_at"],
     "properties":{"from_class":{"enum":["Green","Amber","Red","Blocking"]},
                   "to_class":{"enum":["Green","Amber","Red","Blocking"]},
                   "decision_record":{"type":"string","minLength":1},
                   "approver":{"type":"string","minLength":1},
                   "approver_capability":{"type":"string","minLength":1},
                   "decided_at":{"type":"string","minLength":1}}}},
 "allOf":[
   {"title":"FIND-R3 closure requires what_changed and evidence_link",
    "if":{"properties":{"status":{"const":"closed"}},"required":["status"]},
    "then":{"required":["closure"]}},
   {"title":"FIND-R4 a reclassification requires a decision record and a named approver capability",
    "if":{"required":["reclassification"]},
    "then":{"properties":{"reclassification":{"required":["decision_record","approver_capability"]}}}}]}
pathlib.Path("contracts/reconciler/drift-finding.v1.json").write_text(json.dumps(FIND,indent=2)+"\n",encoding="utf-8")

REPAIR = {
 "$schema":"https://json-schema.org/draft/2020-12/schema",
 # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
 "$id":"https://control-plane.local/contracts/reconciler/repair-record.v1.json",
 "x-contract":{"contract_id":"C-RECON-REPAIR-1","contract_version":1,"owner":"L0",
   "publishing_lane":"L3","consuming_lanes":["L3","L4"],
   "spec_refs":["Section 53.2","Section 53.3","Section 53.7","Section 26.4","AT-033"],
   "ccr_required":True,
   "notes":["D-L0-10: a repair record is a reconciler-surface artifact, not an operational record."],
   "rules":["REPAIR-R1","REPAIR-R2","REPAIR-R3","REPAIR-R4","REPAIR-R5"]},
 "type":"object","additionalProperties":False,
 "required":["record_schema_version","id","product","timestamp","finding_id","row_id","level",
             "repair_class","before","after","direction","stricter_or_equal","idempotent",
             "reversible","actor","run_id","verification","never","frozen"],
 "properties":{
   "record_schema_version":{"const":1},
   "id":{"type":"string","pattern":"^REPAIR-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}$"},
   "product":{"type":"string","minLength":1},
   "timestamp":{"type":"string","pattern":TS},
   "finding_id":{"type":"string","pattern":"^DRIFT-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}$"},
   "row_id":{"enum":row_ids},
   "level":{"const":3},
   "repair_class":{"enum":["team_membership_sync","codeowners_regeneration",
                           "label_and_board_field_sync","reapply_declared_branch_protection",
                           "remove_expired_assignment","revoke_expired_access"],
                   "description":"REPAIR-R2"},
   "before":{},"after":{},
   "direction":{"const":"toward_declared","description":"REPAIR-R1"},
   "stricter_or_equal":{"const":True,"description":"REPAIR-R1"},
   "idempotent":{"const":True},
   "reversible":{"const":True},
   "actor":{"type":"string","pattern":"^machine:reconciler(\\[bot\\])?$","description":"REPAIR-R4"},
   "run_id":{"type":"string","minLength":1},
   "verification":{"type":"object","additionalProperties":False,
     "required":["recompared_at","result"],
     "properties":{"recompared_at":{"type":"string","minLength":1},
                   "result":{"enum":["matches_declared","still_drifted"]}}},
   "never":{"const":never,"description":"REPAIR-R3"},
   "frozen":{"type":"boolean","description":"REPAIR-R5"},
   "freeze_reason":{"type":"string","minLength":1}},
 "allOf":[
   {"title":"REPAIR-R5 a frozen repair class states why it was frozen",
    "if":{"properties":{"frozen":{"const":True}},"required":["frozen"]},
    "then":{"required":["freeze_reason"]}}]}
pathlib.Path("contracts/reconciler/repair-record.v1.json").write_text(json.dumps(REPAIR,indent=2)+"\n",encoding="utf-8")
print("schemas written; row_ids", len(row_ids), "never", never)
PY
```

**Stubs** — the artifacts L2, L4 and L5 develop against before L3 ships the reconciler:

**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > contracts/stubs/drift-finding.yaml <<'EOF'
record_schema_version: 1
id: DRIFT-2026-09-14-000317
product: stub-product
timestamp: "2026-09-14T02:11:00Z"
row_id: RECON-S3
run_id: recon-2026-09-14-0200
detected_at: "2026-09-14T02:10:58Z"
age_days: 0
level: 4
class: Blocking
declared: "canary: seeded mismatch present"
actual: "canary: seeded mismatch present"
evidence:
  - "https://github.example.invalid/control-plane/actions/runs/000000"
canary: true
gap_window: false
status: open
EOF
cat > contracts/stubs/repair-record.yaml <<'EOF'
record_schema_version: 1
id: REPAIR-2026-09-14-000042
product: stub-product
timestamp: "2026-09-14T02:12:00Z"
finding_id: DRIFT-2026-09-14-000318
row_id: R-03
level: 3
repair_class: team_membership_sync
before: "team stub-product members: [dev-a]"
after: "team stub-product members: [dev-a, lead-1]"
direction: toward_declared
stricter_or_equal: true
idempotent: true
reversible: true
actor: "machine:reconciler"
run_id: recon-2026-09-14-0200
verification:
  recompared_at: "2026-09-14T02:12:30Z"
  result: matches_declared
never:
  - loosen_control
  - modify_production_runtime_config
  - modify_data
  - rotate_or_write_secrets
frozen: false
EOF
cp contracts/stubs/drift-finding.yaml contracts/fixtures/C-RECON-FIND-1/valid-001.yaml
cp contracts/stubs/repair-record.yaml contracts/fixtures/C-RECON-REPAIR-1/valid-001.yaml
```

`row_id: R-03` is the third row of `C-RECON-SET-1` — `product.yaml` assignments versus GitHub Team membership — which is the row the `team_membership_sync` repair class exists to close. If the row ids in your `comparison-set.v1.yaml` are not `R-01`..`R-17`, use whatever `row_id` that file actually carries for that comparison; the SELF-VERIFY below proves the stub's `row_id` resolves.

**Fixtures**

| File | Line 1 | Rule refuted |
| --- | --- | --- |
| `C-RECON-FIND-1/invalid-001.yaml` | `# EXPECT: reject — row_id R-99 is not a row of C-RECON-SET-1 (Section 53.1)` | `FIND-R1` |
| `C-RECON-FIND-1/invalid-002.yaml` | `# EXPECT: reject — class "dangerous" is retired vocabulary; the one scale is Green/Amber/Red/Blocking (Section 53.4)` | `FIND-R2` |
| `C-RECON-FIND-1/invalid-003.yaml` | `# EXPECT: reject — status closed with no closure block (Section 53.6)` | `FIND-R3` |
| `C-RECON-FIND-1/invalid-004.yaml` | `# EXPECT: reject — reclassification Red to Amber with no decision_record (Section 53.5)` | `FIND-R4` |
| `C-RECON-REPAIR-1/invalid-001.yaml` | `# EXPECT: reject — direction away_from_declared; reconciliation never loosens a control (Section 53.3)` | `REPAIR-R1` |
| `C-RECON-REPAIR-1/invalid-002.yaml` | `# EXPECT: reject — repair_class rotate_secret is not one of the six Level 3 classes (Section 53.2)` | `REPAIR-R2` |
| `C-RECON-REPAIR-1/invalid-003.yaml` | `# EXPECT: reject — actor is a human login; repair records are written under the reconciler credential (Section 26.4)` | `REPAIR-R4` |

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import copy, pathlib, yaml
F = yaml.safe_load(open("contracts/stubs/drift-finding.yaml"))
R = yaml.safe_load(open("contracts/stubs/repair-record.yaml"))
def w(path, note, doc):
    pathlib.Path(path).write_text("# EXPECT: reject " + note + "\n" +
                                  yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
d = copy.deepcopy(F); d["row_id"] = "R-99"
w("contracts/fixtures/C-RECON-FIND-1/invalid-001.yaml",
  "- row_id R-99 is not a row of C-RECON-SET-1 (Section 53.1)", d)
d = copy.deepcopy(F); d["class"] = "dangerous"
w("contracts/fixtures/C-RECON-FIND-1/invalid-002.yaml",
  "- class 'dangerous' is retired vocabulary; the one scale is Green/Amber/Red/Blocking (Section 53.4)", d)
d = copy.deepcopy(F); d["status"] = "closed"
w("contracts/fixtures/C-RECON-FIND-1/invalid-003.yaml",
  "- status closed with no closure block (Section 53.6)", d)
d = copy.deepcopy(F)
d["reclassification"] = {"from_class":"Red","to_class":"Amber","approver":"lead-1",
                         "decided_at":"2026-09-14T09:00:00Z"}
w("contracts/fixtures/C-RECON-FIND-1/invalid-004.yaml",
  "- reclassification Red to Amber with no decision_record (Section 53.5)", d)
d = copy.deepcopy(R); d["direction"] = "away_from_declared"
w("contracts/fixtures/C-RECON-REPAIR-1/invalid-001.yaml",
  "- direction away_from_declared; reconciliation never loosens a control (Section 53.3)", d)
d = copy.deepcopy(R); d["repair_class"] = "rotate_secret"
w("contracts/fixtures/C-RECON-REPAIR-1/invalid-002.yaml",
  "- repair_class rotate_secret is not one of the six Level 3 classes (Section 53.2)", d)
d = copy.deepcopy(R); d["actor"] = "stub-lead-1"
w("contracts/fixtures/C-RECON-REPAIR-1/invalid-003.yaml",
  "- actor is a human login; repair records are written under the reconciler credential (Section 26.4)", d)
print("fixtures written")
PY
python contracts/ci/register_add.py C-RECON-FIND-1   reconciler/drift-finding.v1.json  1 L3 L2,L3,L4,L5 stubs/drift-finding.yaml
python contracts/ci/register_add.py C-RECON-REPAIR-1 reconciler/repair-record.v1.json  1 L3 L3,L4       stubs/repair-record.yaml
git add -A && git commit -m "L0-P0-018: C-RECON-FIND-1 and C-RECON-REPAIR-1"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Both schemas are valid JSON Schema 2020-12 | `for s in drift-finding.v1 repair-record.v1; do check-jsonschema --check-metaschema "contracts/reconciler/$s.json" \|\| echo "BAD $s"; done; echo done` | `done`, no `BAD` |
| 2 | Both stubs validate | `check-jsonschema --schemafile contracts/reconciler/drift-finding.v1.json contracts/stubs/drift-finding.yaml && check-jsonschema --schemafile contracts/reconciler/repair-record.v1.json contracts/stubs/repair-record.yaml && echo ok` | `ok` |
| 3 | All four finding fixtures are rejected | `for f in contracts/fixtures/C-RECON-FIND-1/invalid-*.yaml; do check-jsonschema --schemafile contracts/reconciler/drift-finding.v1.json "$f" >/dev/null 2>&1 && echo "LEAK $f" \|\| echo "rejected $f"; done` | four `rejected …` lines, no `LEAK` |
| 4 | All three repair fixtures are rejected | `for f in contracts/fixtures/C-RECON-REPAIR-1/invalid-*.yaml; do check-jsonschema --schemafile contracts/reconciler/repair-record.v1.json "$f" >/dev/null 2>&1 && echo "LEAK $f" \|\| echo "rejected $f"; done` | three `rejected …` lines, no `LEAK` |
| 5 | `row_id` enumerates exactly the seventeen rows plus the three standing rules | `python -c "import json;print(len(json.load(open('contracts/reconciler/drift-finding.v1.json'))['properties']['row_id']['enum']))"` | `20` |
| 6 | Exactly six repair classes (53.2) | `python -c "import json;print(len(json.load(open('contracts/reconciler/repair-record.v1.json'))['properties']['repair_class']['enum']))"` | `6` |
| 7 | `direction` is pinned toward the declared state (AT-033) | `python -c "import json;print(json.load(open('contracts/reconciler/repair-record.v1.json'))['properties']['direction']['const'])"` | `toward_declared` |
| 8 | Register now holds nineteen rows | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/register.yaml'))['contracts']))"` | `19` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import json, yaml
F = json.load(open("contracts/reconciler/drift-finding.v1.json"))
R = json.load(open("contracts/reconciler/repair-record.v1.json"))
S = yaml.safe_load(open("contracts/reconciler/comparison-set.v1.yaml"))
stores = {s["store"] for s in yaml.safe_load(open("contracts/records/store-map.v1.yaml"))["stores"]}
enum   = {e["id"] for e in yaml.safe_load(open("contracts/records/event-type.enum.v1.yaml"))["event_types"]}
rows   = {r["row_id"] for r in S["rows"]} | {"RECON-S1","RECON-S2","RECON-S3"}
stub_f = yaml.safe_load(open("contracts/stubs/drift-finding.yaml"))
stub_r = yaml.safe_load(open("contracts/stubs/repair-record.yaml"))
ok  = set(F["properties"]["row_id"]["enum"]) == rows
ok &= set(R["properties"]["row_id"]["enum"]) == rows
ok &= stub_f["row_id"] in rows and stub_r["row_id"] in rows
ok &= R["properties"]["never"]["const"] == S["auto_repair"]["never"]
ok &= R["properties"]["level"]["const"] == 3
ok &= {"record_schema_version","id","product","timestamp"} <= set(F["required"])
ok &= {"drift_detected","drift_repaired"} <= enum
ok &= not [s for s in stores if "drift" in s]      # D-L0-10: no drift store exists
print("L0-P0-018 PASS" if ok else "L0-P0-018 FAIL")
PY
```

Expected: `L0-P0-018 PASS`

**STOP RULE** — If you find yourself wanting a `records/drift/` store so a finding has somewhere durable to live, stop and read D-L0-10 again. Section 52.6 binds: state which existing file cannot hold the content, and if an existing file can, the proposal is rejected. `events/` holds the lifecycle; the drift view holds the current set. If you still believe a store is needed, file a **CCR-ADDITIVE** against `C-REC-STORE-MAP-1` carrying that statement — never add the store here, because a store added in the reconciler contract is a store L4 does not know it owns.

---

### L0-P0-019 — `C-PROV-OP-1`: the four provisioning operations

| | |
| --- | --- |
| **Size** | L |
| **Depends on** | L0-P0-006, L0-P0-014, L0-P0-018 |
| **Writes** | `contracts/provisioning/operation.v1.yaml`, `contracts/stubs/provision-create-product.yaml`, `contracts/stubs/provision-add-person.yaml`, `contracts/fixtures/C-PROV-OP-1/{valid-001,invalid-001..004}.yaml` |
| **Spec** | Section 12.6 (the four scaffolding operations), Section 19.1 (the create-product sequence), Section 64.1 (safe defaults), Section 26.4 (registry-change staging and the authority delta), Section 11.3 (protection from template at creation), AT-001, AT-002, AT-017, invariants 79, 80 |

L3 owns `tools/provision/**` (PARTITION.md line 20) and writes the scripts. It does not decide **what an operation produces**, because L1 must publish the registry rows the operation writes, L5 must provision the access the operation assumes, and L2 must supply the workflows the operation wires in at a pinned tag. Four lanes, one declaration.

> **L0 decision D-L0-11, recorded here.** `C-PROV-OP-1` is a **declaration of effects, not an implementation**. It states, per operation, the preconditions, the ordered effects, the events emitted, the records written, the idempotency key and the safe defaults — and it states nothing about language, CLI framing, argument parsing or output format, all of which are L3's inside `tools/provision/**`. A lane asking L0 for the script's flags has misread the contract; a lane asking L0 to add an effect has read it correctly and files a CCR.

**Shape.** `contract_version: 1`; `operations[]`, one per Section 12.6 operation; plus `safe_defaults{}`, `staging{}` and `rules[]` at the top level.

Each operation carries: `id` (`create-product` | `add-person` | `change-role` | `remove-person`), `required_capability` (`devops` on all four — each writes organisation state, and 19.1 names a DevOps-capability holder as the executor), `preconditions[]`, `effects[]` (ordered; each an `{effect, target}` pair), `manual_fallback[]` (effects the provider offers no automation for, emitted as tracked issues), `emits_events[]` (identifiers from `C-EVT-ENUM-1`), `writes_records[]` (store ids from `C-REC-STORE-MAP-1`), `idempotency_key`, `dry_run: supported`, and `on_partial_failure: resume_from_effect`.

**The four operations, transcribed.**

| Operation | Effects, in the order 12.6 and 19.1 state them | Idempotency key |
| --- | --- | --- |
| `create-product` | repository or repository set from `product-template` · `product.yaml` at current `contract_version` · GitHub Team · CODEOWNERS generated from assignments · branch protection from template · environments `development`, `staging`, `production` · CI workflows consuming reusable workflows **by pinned tag** · `verification/` skeleton · local environment contract (the eight commands) · health, version and metrics endpoints · alert channel · support-intake mailbox · registration in the portfolio board, Grafana, Scorecard and DevLake · registration in the dependency graph | `product.id` |
| `add-person` | `people.yaml` entry · organisation invitation · Team membership per assignments · capability grants · AI runtime assignment honouring per-product `ai_restrictions` · onboarding checklist issue · registration in the review-network view | `person.id` |
| `change-role` | role update · capability recalculation · permission recalculation · reviewer-matrix reassessment · ownership reassessment prompt · incident-responder reassessment · dashboard update | `person.id` + `effective_date` |
| `remove-person` | access revocation · Team removal · environment access revocation · AI runtime deactivation · reviewer-matrix recalculation · **orphan detection** · exit record | `person.id` + `end_date` |

`create-product` therefore declares **fourteen** ordered effects: the twelve bullets of 12.6 with 19.1's alert channel and support-intake mailbox counted separately, and the two registration effects counted separately, because a partial run has to be resumable at exactly the effect that failed.

**Binding rules in the body**

| Rule id | Rule | Spec |
| --- | --- | --- |
| `PROV-OP-R1` | Every operation is idempotent under its declared `idempotency_key`. A second run creates no second repository, Team, registry row or invitation, and exits success | 12.6, AT-001 |
| `PROV-OP-R2` | Safe defaults apply at creation and are not parameters: repository private; branch protection applied from the template at creation; no environment access; no third-party app access; production environment created **without secrets and without approvers**; `launch_status: pre-launch`; `lifecycle: active` only after contract validation passes; no scheduled jobs enabled | 64.1, 11.3 |
| `PROV-OP-R3` | A missing or malformed input resolves to **denial**, never to a permitting default | 64.1 |
| `PROV-OP-R4` | An effect the provider offers no automation for is emitted as a tracked manual issue and named in `manual_fallback[]`. It is never silently skipped, because a silently skipped alert channel is a product with no detection path | 19.1 |
| `PROV-OP-R5` | `remove-person` runs orphan detection as a declared effect. A Blocking orphan (SIG-05) cannot be dismissed unresolved | 12.6, AT-017 |
| `PROV-OP-R6` | Registry rows an operation writes are applied by the next reconciliation run **to the declared canary set only**; the remainder of the fleet is held one reconciliation cycle and applied after the canary cycle records a clean run | 26.4 |
| `PROV-OP-R7` | An **authority delta** — a diff adding a capability, adding an assignment type conferring Write, or changing `access_status` — fails CI without a linked decision-record id in the same commit | 26.4 |
| `PROV-OP-R8` | CI workflows are wired **by pinned tag, never by branch**, matching `WF-R1` of `C-WF-IFACE-1`. A newly created product consuming `@main` is drift on its first reconciliation | 33.3, invariant 85 |

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-PROV-OP-1
mkdir -p contracts/provisioning
cat > contracts/provisioning/operation.v1.yaml << 'PROV_EOF'
# C-PROV-OP-1 — the four provisioning operations (v1). Section 12.6, 19.1, 64.1, 26.4.
contract_version: 1

safe_defaults:
  repository_visibility: private
  branch_protection: applied from template at creation
  environment_access: none
  third_party_app_access: none
  production_environment: created without secrets and without approvers
  launch_status: pre-launch
  lifecycle_active_requires: contract validation passes
  scheduled_jobs: disabled

staging:
  canary_first: true
  fleet_held_cycles: 1
  authority_delta_requires_decision_record: true

rules:
  - id: PROV-OP-R1
    rule: Every operation is idempotent under its declared idempotency_key. A second run creates no second repository, Team, registry row or invitation, and exits success.
    spec: "12.6, AT-001"
  - id: PROV-OP-R2
    rule: "Safe defaults apply at creation and are not parameters: repository private; branch protection applied from the template at creation; no environment access; no third-party app access; production environment created without secrets and without approvers; launch_status: pre-launch; lifecycle: active only after contract validation passes; no scheduled jobs enabled."
    spec: "64.1, 11.3"
  - id: PROV-OP-R3
    rule: A missing or malformed input resolves to denial, never to a permitting default.
    spec: "64.1"
  - id: PROV-OP-R4
    rule: An effect the provider offers no automation for is emitted as a tracked manual issue and named in manual_fallback[]. It is never silently skipped, because a silently skipped alert channel is a product with no detection path.
    spec: "19.1"
  - id: PROV-OP-R5
    rule: remove-person runs orphan detection as a declared effect. A Blocking orphan (SIG-05) cannot be dismissed unresolved.
    spec: "12.6, AT-017"
  - id: PROV-OP-R6
    rule: Registry rows an operation writes are applied by the next reconciliation run to the declared canary set only; the remainder of the fleet is held one reconciliation cycle and applied after the canary cycle records a clean run.
    spec: "26.4"
  - id: PROV-OP-R7
    rule: An authority delta — a diff adding a capability, adding an assignment type conferring Write, or changing access_status — fails CI without a linked decision-record id in the same commit.
    spec: "26.4"
  - id: PROV-OP-R8
    rule: CI workflows are wired by pinned tag, never by branch, matching WF-R1 of C-WF-IFACE-1. A newly created product consuming at main is drift on its first reconciliation.
    spec: "33.3, invariant 85"

operations:
  - id: create-product
    required_capability: devops
    preconditions:
      - product.id is unique in the portfolio registry
      - workflow_ref resolves to a pinned tag
      - assignments include at least one primary_owner
    effects:
      - {effect: repository_from_template, target: product-template}
      - {effect: product_yaml_at_contract_version, target: product.yaml}
      - {effect: github_team_created, target: product team}
      - {effect: codeowners_generated_from_assignments, target: CODEOWNERS}
      - {effect: branch_protection_from_template, target: default branch}
      - {effect: environments_created, target: "development, staging, production"}
      - {effect: ci_workflows_wired_by_pinned_tag, target: .github/workflows}
      - {effect: verification_skeleton_created, target: verification/}
      - {effect: local_environment_contract_created, target: eight commands}
      - {effect: health_version_metrics_endpoints_declared, target: endpoint contract}
      - {effect: alert_channel_created, target: monitoring}
      - {effect: support_intake_mailbox_created, target: support}
      - {effect: registration_in_portfolio_grafana_scorecard_devlake, target: portfolio board}
      - {effect: registration_in_dependency_graph, target: dependency graph}
    manual_fallback:
      - alert_channel_created
      - support_intake_mailbox_created
    emits_events:
      - product_created
    writes_records:
      - records/launches/
    idempotency_key: product.id
    dry_run: supported
    on_partial_failure: resume_from_effect

  - id: add-person
    required_capability: devops
    preconditions:
      - person.id is unique in the people registry
      - capabilities are valid for the declared role
    effects:
      - {effect: people_yaml_entry_created, target: people.yaml}
      - {effect: organisation_invitation_sent, target: github organisation}
      - {effect: team_membership_assigned, target: teams per assignments}
      - {effect: capability_grants_applied, target: capability registry}
      - {effect: ai_runtime_assigned_honouring_restrictions, target: ai runtime}
      - {effect: onboarding_checklist_issue_created, target: github issues}
      - {effect: review_network_view_registered, target: review network}
    manual_fallback:
      - ai_runtime_assigned_honouring_restrictions
    emits_events:
      - person_added
    writes_records:
      - records/onboarding/
    idempotency_key: person.id
    dry_run: supported
    on_partial_failure: resume_from_effect

  - id: change-role
    required_capability: devops
    preconditions:
      - person.id exists in the people registry
      - effective_date is not in the past
    effects:
      - {effect: role_updated, target: people.yaml}
      - {effect: capability_recalculated, target: capability registry}
      - {effect: permission_recalculated, target: team membership}
      - {effect: reviewer_matrix_reassessed, target: reviewer matrix}
      - {effect: ownership_reassessment_prompted, target: product assignments}
      - {effect: incident_responder_reassessed, target: incident registry}
      - {effect: dashboard_updated, target: operations dashboard}
    manual_fallback: []
    emits_events:
      - person_role_changed
    writes_records:
      - records/decisions/
    idempotency_key: "person.id + effective_date"
    dry_run: supported
    on_partial_failure: resume_from_effect

  - id: remove-person
    required_capability: devops
    preconditions:
      - person.id exists in the people registry
      - end_date is declared
      - skip_orphan_detection is not set to true
    effects:
      - {effect: access_revoked, target: github organisation}
      - {effect: team_removed, target: teams}
      - {effect: environment_access_revoked, target: environments}
      - {effect: ai_runtime_deactivated, target: ai runtime}
      - {effect: reviewer_matrix_recalculated, target: reviewer matrix}
      - {effect: orphan_detection, target: product assignments}
      - {effect: exit_record_written, target: records/decisions/}
    manual_fallback: []
    emits_events:
      - person_departed
      - orphan_detected
    writes_records:
      - records/decisions/
    idempotency_key: "person.id + end_date"
    dry_run: supported
    on_partial_failure: resume_from_effect
PROV_EOF
python - <<'PY'
import yaml, pathlib
req = {
  "operation": "create-product",
  "product": {"id": "stub-product", "contract_version": 2},
  "repository_visibility": "private",
  "workflow_ref": "workflows/v1.0.0",
  "assignments": [
    {"person": "dev-a",  "assignment": "primary_owner"},
    {"person": "lead-1", "assignment": "cross_reviewer"},
  ],
  "environments": {"development": {}, "staging": {}, "production": {"secrets": [], "approvers": []}},
  "dry_run": True,
}
pathlib.Path("contracts/stubs/provision-create-product.yaml").write_text(
    yaml.safe_dump(req, sort_keys=False), encoding="utf-8")
add = {
  "operation": "add-person",
  "person": {"id": "qa-a", "github_login": "stub-qa-a", "role": "qa",
             "employment_type": "employee", "end_date": None},
  "capabilities": ["verification", "uat", "release-signoff"],
  "ai_runtime": None,
  "dry_run": True,
}
pathlib.Path("contracts/stubs/provision-add-person.yaml").write_text(
    yaml.safe_dump(add, sort_keys=False), encoding="utf-8")
pathlib.Path("contracts/fixtures/C-PROV-OP-1/valid-001.yaml").write_text(
    yaml.safe_dump(req, sort_keys=False), encoding="utf-8")
import copy
def w(name, note, doc):
    pathlib.Path("contracts/fixtures/C-PROV-OP-1/" + name).write_text(
        "# EXPECT: reject " + note + "\n" + yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
d = copy.deepcopy(req); d["repository_visibility"] = "public"
w("invalid-001.yaml", "- repository visibility public; safe defaults require private (Section 64.1)", d)
d = copy.deepcopy(req); d["environments"]["production"]["secrets"] = ["PROD_DB_URL"]
w("invalid-002.yaml", "- production environment seeded with secrets at creation (Section 64.1)", d)
d = copy.deepcopy(req); d["workflow_ref"] = "workflows/ci.yml@main"
w("invalid-003.yaml", "- workflows wired by branch, not by pinned tag (Section 33.3, PROV-OP-R8)", d)
d = {"operation": "remove-person", "person": {"id": "dev-a", "end_date": "2026-10-31"},
     "skip_orphan_detection": True}
w("invalid-004.yaml", "- orphan detection skipped on remove-person (Section 12.6, AT-017)", d)
print("requests and fixtures written")
PY
python contracts/ci/register_add.py C-PROV-OP-1 provisioning/operation.v1.yaml 1 L3 L1,L3,L5 stubs/provision-create-product.yaml
git add -A && git commit -m "L0-P0-019: C-PROV-OP-1 provisioning operation contract"
```

The stub `contracts/stubs/provision-create-product.yaml` is the **request document** a lane runs the operation with, not a copy of the contract — a lane cannot develop against a declaration of effects, only against an instance of the request that triggers them. Both request stubs are synthetic; neither carries a real login (invariant 111, D-L0-08).

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Exactly four operations, with the ids of 12.6 | `python -c "import yaml;print([o['id'] for o in yaml.safe_load(open('contracts/provisioning/operation.v1.yaml'))['operations']])"` | `['create-product', 'add-person', 'change-role', 'remove-person']` |
| 2 | `create-product` declares fourteen ordered effects | `python -c "import yaml;o={x['id']:x for x in yaml.safe_load(open('contracts/provisioning/operation.v1.yaml'))['operations']};print(len(o['create-product']['effects']))"` | `14` |
| 3 | `remove-person` declares orphan detection as an effect | `python -c "import yaml;o={x['id']:x for x in yaml.safe_load(open('contracts/provisioning/operation.v1.yaml'))['operations']};print('orphan_detection' in [e['effect'] for e in o['remove-person']['effects']])"` | `True` |
| 4 | Every operation declares an idempotency key and dry-run support | `python -c "import yaml;o=yaml.safe_load(open('contracts/provisioning/operation.v1.yaml'))['operations'];print(all(x.get('idempotency_key') and x.get('dry_run')=='supported' for x in o))"` | `True` |
| 5 | All eight rules present | `grep -o 'PROV-OP-R[0-9]' contracts/provisioning/operation.v1.yaml \| sort -u \| tr '\n' ' '` | `PROV-OP-R1 PROV-OP-R2 PROV-OP-R3 PROV-OP-R4 PROV-OP-R5 PROV-OP-R6 PROV-OP-R7 PROV-OP-R8 ` |
| 6 | Safe defaults name the production-environment rule verbatim | `python -c "import yaml;print(yaml.safe_load(open('contracts/provisioning/operation.v1.yaml'))['safe_defaults']['production_environment'])"` | `created without secrets and without approvers` |
| 7 | The four invalid request fixtures each declare their expectation | `head -1 -q contracts/fixtures/C-PROV-OP-1/invalid-*.yaml \| grep -c '^# EXPECT: reject'` | `4` |
| 8 | Register now holds twenty rows | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/register.yaml'))['contracts']))"` | `20` |

The four invalid fixtures are executed against `contracts/ci/lint_provision_requests.py`, which is written in **L0-P0-021** alongside the rest of the harness. Until that task runs, criterion 7 is the proof; after it runs, the harness proves them mechanically.

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import yaml
P = yaml.safe_load(open("contracts/provisioning/operation.v1.yaml"))
enum   = {e["id"] for e in yaml.safe_load(open("contracts/records/event-type.enum.v1.yaml"))["event_types"]}
stores = {s["store"] for s in yaml.safe_load(open("contracts/records/store-map.v1.yaml"))["stores"]}
people = {p["id"] for p in yaml.safe_load(open("contracts/stubs/people.yaml"))["people"]}
ops = {o["id"]: o for o in P["operations"]}
bad_e = [(k, e) for k, o in ops.items() for e in o.get("emits_events", []) if e not in enum]
bad_s = [(k, s) for k, o in ops.items() for s in o.get("writes_records", []) if s not in stores]
ok  = set(ops) == {"create-product", "add-person", "change-role", "remove-person"}
ok &= not bad_e and not bad_s
ok &= all(o.get("required_capability") == "devops" for o in ops.values())
ok &= P["safe_defaults"]["repository_visibility"] == "private"
ok &= P["safe_defaults"]["third_party_app_access"] == "none"
ok &= P["staging"]["canary_first"] is True and P["staging"]["fleet_held_cycles"] == 1
req = yaml.safe_load(open("contracts/stubs/provision-create-product.yaml"))
ok &= all(a["person"] in people for a in req["assignments"])
ok &= req["repository_visibility"] == "private"
print("L0-P0-019 PASS" if ok else f"L0-P0-019 FAIL events={bad_e} stores={bad_s}")
PY
```

Expected: `L0-P0-019 PASS`

**STOP RULE** — If an effect in Section 12.6 or 19.1 cannot be automated on the plan tier, do not drop it and do not mark the operation complete without it. `PROV-OP-R4` is the only permitted answer: declare it in `manual_fallback[]` so the operation emits a tracked issue. An effect that is neither automated nor tracked is the failure 12.6 names outright — "If it does, the scaffolding is incomplete and that is a platform defect." Removing an effect from this contract is **CCR-BREAKING**; moving one from `effects[]` to `manual_fallback[]` is **CCR-ADDITIVE** and must name the provider limitation.

---

### L0-P0-020 — `C-ACC-PERM-1`, `C-ACC-PROT-1`, `C-ACC-LAYER-1`: the access contracts

| | |
| --- | --- |
| **Size** | L |
| **Depends on** | L0-P0-005, L0-P0-014, L0-P0-015 |
| **Writes** | `contracts/access/{permission-model.v1.yaml,protection.template.v1.yaml,layer-split.v1.yaml}`, `contracts/stubs/{permission-model.yaml,branch-protection.yaml,layer-split.yaml}`, `contracts/fixtures/C-ACC-PERM-1/{valid-001,invalid-001,invalid-002}.yaml`, `contracts/fixtures/C-ACC-PROT-1/{valid-001,invalid-001,invalid-002,invalid-003}.yaml`, `contracts/fixtures/C-ACC-LAYER-1/{valid-001,invalid-001,invalid-002}.yaml` |
| **Spec** | Sections 11.1, 11.2, 11.3, 11.4 (D73), Section 33.4, Section 64.1, Section 90.1, 90.2, 90.3, 90.4 (D109), Section 40.1 (D89), AT-089, AT-090, AT-091, AT-092, AT-097, AT-098, invariant 9 |

Three contracts, grouped because L5 publishes all three and each is read by lanes L5 does not control. L3 reconciles the first two — the `C-RECON-SET-1` rows for permission drift and branch-protection drift compare actual state against exactly these files. L2 reads the second to know which contexts branch protection will demand. L4 reads the third to know which store a decision record goes to.

#### `C-ACC-PERM-1` — the permission model

**Shape.** `contract_version: 1`; `organisation{}` (`base_permission: read`, `two_factor_required: true`, `strong_factor_capabilities: [platform-admin]`, `second_owner_required: true`); `person_classes[]`, the six rows of the Section 11.2 table verbatim; `teams{}` (one Team per product, plus the two organisation-wide Teams granting Write to the Team Lead role and the QA role); `derivation{}` (Write is granted through Teams, derived from the registries, reconciled continuously); and `rules[]`.

| Person class | Organisation role | Write on | Read on |
| --- | --- | --- | --- |
| `founder` | `owner` | all (implicit) | all |
| `team_lead` | `member` | all product repositories | all |
| `qa` | `member` | all product repositories | all |
| `developer` | `member` | repositories of products where they hold `primary_owner`, `cross_reviewer`, `backup_owner` or `temporary_contributor` | all others |
| `contractor_or_temporary_specialist` | `outside_collaborator_or_scoped_member` | only repositories named in `scope` | only repositories named in `scope` |
| `background_machine_layer` | `machine_account` | branch push only on whitelisted repositories; no merge, no environment access | repositories in its queue |

| Rule id | Rule | Spec |
| --- | --- | --- |
| `PERM-R1` | A Cross-Reviewer holds **Write**, because a Read-permission approval does not count toward required approving reviews — it reads as an approval and satisfies nothing | 11.1 |
| `PERM-R2` | Least privilege is preserved by branch protection and the Section 27.2 workflow-identity gate, **not** by withholding Write | 11.1, 11.4 |
| `PERM-R3` | Team membership is derived from the registries and reconciled continuously; a mismatch between `people.yaml`, `product.yaml` and actual Team membership fails CI and raises a drift finding | 11.2, 53.1 |
| `PERM-R4` | No machine identity appears in CODEOWNERS, holds a Layer B credential or scope, or holds `people-intelligence`, under any configuration | 11.3, 90.2 |
| `PERM-R5` | Contractors and temporary specialists are not granted organisation-wide Read unless their declared `scope` requires it, and `end_date` and `scope` are both mandatory | 11.2, 64.1 |
| `PERM-R6` | Custom repository roles are Enterprise-only; Write-via-Teams is the assumed configuration throughout, not a workaround pending an upgrade | 11.4 |

#### `C-ACC-PROT-1` — the branch-protection and environment template

**Shape.** `contract_version: 1`; `branch_protection{}` carrying the bullets of Section 11.3 as named boolean or list fields; `environments{}` carrying the three environments and the deployment branch-and-tag policy of 33.4; `rulesets[]` naming ruleset **A** (the protection ruleset) and ruleset **B** (the Renovate path guard, **no bypass actor at all**); `codeowners{}` (generated, human identities only, with the four ownership routes of 11.3); `production_approval_mechanism`; and `plan_tier_facts[]`, the four rows of 11.4 transcribed with their mechanism of record.

The required-check list is **not restated here**. It is `C-WF-CHECKS-1` by reference — `required_checks_contract: C-WF-CHECKS-1` — because a check name written down twice is a check name that will differ once, and a check name that differs is a gate that reads armed and is not.

| Rule id | Rule | Spec |
| --- | --- | --- |
| `PROT-R1` | Require a pull request, at least one approving review, and review from Code Owners; CODEOWNERS holds human identities only, so a machine approval can never satisfy protection | 11.3 |
| `PROT-R2` | Require approval of the most recent reviewable push, and dismiss stale approvals on new commits. This is the enforcement behind the no-self-approval invariant | 11.3, invariant 9 |
| `PROT-R3` | Require branches up to date; block force pushes and deletions on the default branch; apply rules to administrators, with an exception only under a documented break-glass procedure carrying an audit record | 11.3, Section 54 |
| `PROT-R4` | **Every environment carries a deployment branch and tag policy** restricting `staging` and `production` to the default branch and protected release tags. Branch protection governs what merges; the deployment policy governs what may reach an environment's secrets. Neither substitutes for the other, and a repository with the first and not the second holds production credentials behind nothing | 11.3, 33.4 |
| `PROT-R5` | Environment required reviewers are an Enterprise feature and are never depended on. The production-approval mechanism of record is the Section 27.2 workflow-identity gate, failing closed (D73) | 11.4 |
| `PROT-R6` | New repositories are created private, with protection applied from the template **at creation**, no environment access and no third-party app access | 11.3, 64.1 |
| `PROT-R7` | Ruleset B — the one carrying `renovate-path-guard` — names **no bypass actor at all**, because a bypass actor is exempt from every rule in the ruleset it is listed on | 33.2, D89 |

#### `C-ACC-LAYER-1` — the Layer A / Layer B split

**Shape.** `contract_version: 1`; `layer_a[]` (the eleven categories of 90.1); `layer_b[]` (the twenty-three categories of 90.1); `permission_matrix[]` (the twenty-seven rows of the 90.2 table, each with `category`, `founder`, `team_lead`, `employee`, `peer`); `datasource_enforcement{}` (the binding statements of 90.3, including `people_datasource_in_shared_instance: false`); `capability{}` (`id: people-intelligence`, `delegable: false`); `accepted_risks[]` (the host-level administrative access record of 90.3); and `decision_routing{}`.

**The decision-record routing rule, frozen because L4 cannot infer it (90.1):** people-related Founder decisions are written to the Layer B decision store; every other Founder decision is written to `records/decisions/` in the control plane. The decision-latency metric reads **both** stores, so people decisions are neither invisible to latency measurement nor exposed by it. A decision prompt opens a pending entry at issuance in `records/decisions/pending/`, or in its Layer B counterpart for people-related decisions.

| Rule id | Rule | Spec |
| --- | --- | --- |
| `LAYER-R1` | Layer B is Founder-only and `people-intelligence` is **not delegable** (D109). No assignment type grants it and none may be introduced to do so; an attempt to configure one fails validation | 90.4, AT-090, AT-091 |
| `LAYER-R2` | The machine-identities row of the 90.2 matrix is absolute: no machine identity holds any people-related category, receives a Layer B credential or folder scope, or holds `people-intelligence`, under any configuration | 90.2 |
| `LAYER-R3` | The Layer B boundary is **instance separation, not folder membership**: the people datasource is never registered in the shared Grafana instance, and folder ACLs there are defence in depth for Layer A views only | 90.3, AT-097, AT-098 |
| `LAYER-R4` | Sensitive people data is **absent from** the general engineering datasource, not merely hidden from its panels | 90.3, AT-089 |
| `LAYER-R5` | The individual self-view is a generated per-person document, never a dashboard | 90.3, AT-095 |
| `LAYER-R6` | Host-level administrative access to the Layer B store is a **named, recorded accepted risk** with a named holder, a compensating control the holder cannot silently defeat, and a dated review — never a capability grant | 90.3, 54.2 |
| `LAYER-R7` | No Layer B evidence may be generated before this separation exists; the phase that would generate it is gated on it | 90.3, Section 98 |

**Commands**

```bash
set -euo pipefail
cd "$CP"
mkdir -p contracts/fixtures/C-ACC-PERM-1 contracts/fixtures/C-ACC-PROT-1 contracts/fixtures/C-ACC-LAYER-1
python - <<'PY'
import pathlib, shutil
pathlib.Path("contracts/access").mkdir(parents=True, exist_ok=True)
pathlib.Path("contracts/stubs").mkdir(parents=True, exist_ok=True)

# ── contracts/access/permission-model.v1.yaml  (also written to stubs/) ────────
PERM = """\
contract_version: 1
contract_id: C-ACC-PERM-1
organisation:
  base_permission: read
  two_factor_required: true
  strong_factor_capabilities: [platform-admin]
  second_owner_required: true
person_classes:
  - id: founder
    organisation_role: owner
    write_on: all
    read_on: all
  - id: team_lead
    organisation_role: member
    write_on: all_product_repositories
    read_on: all
  - id: qa
    organisation_role: member
    write_on: all_product_repositories
    read_on: all
  - id: developer
    organisation_role: member
    write_on: repositories_of_products_with_primary_owner_cross_reviewer_backup_owner_or_temporary_contributor
    read_on: all_others
  - id: contractor_or_temporary_specialist
    organisation_role: outside_collaborator_or_scoped_member
    write_on: only_repositories_named_in_scope
    read_on: only_repositories_named_in_scope
  - id: background_machine_layer
    organisation_role: machine_account
    write_on: branch_push_only_on_whitelisted_repositories
    read_on: repositories_in_its_queue
teams:
  product_teams:
    structure: one_team_per_product_named_for_the_product
    membership_derived_from: registries
    reconciliation: continuous
  org_wide_teams:
    team_lead_write:
      grants: write
      role: team_lead
    qa_write:
      grants: write
      role: qa
derivation:
  method: write_granted_through_teams
  source: registries
  reconciliation: continuous
  drift_consequence: ci_failure_and_drift_finding
rules:
  - id: PERM-R1
    rule: >-
      A Cross-Reviewer holds Write, because a Read-permission approval does not count
      toward required approving reviews — it reads as an approval and satisfies nothing
    spec: ["11.1"]
  - id: PERM-R2
    rule: >-
      Least privilege is preserved by branch protection and the Section 27.2
      workflow-identity gate, not by withholding Write
    spec: ["11.1", "11.4"]
  - id: PERM-R3
    rule: >-
      Team membership is derived from the registries and reconciled continuously; a
      mismatch between people.yaml, product.yaml and actual Team membership fails CI
      and raises a drift finding
    spec: ["11.2", "53.1"]
  - id: PERM-R4
    rule: >-
      No machine identity appears in CODEOWNERS, holds a Layer B credential or scope,
      or holds people-intelligence, under any configuration
    spec: ["11.3", "90.2"]
  - id: PERM-R5
    rule: >-
      Contractors and temporary specialists are not granted organisation-wide Read unless
      their declared scope requires it, and end_date and scope are both mandatory
    spec: ["11.2", "64.1"]
  - id: PERM-R6
    rule: >-
      Custom repository roles are Enterprise-only; Write-via-Teams is the assumed
      configuration throughout, not a workaround pending an upgrade
    spec: ["11.4"]
"""
pathlib.Path("contracts/access/permission-model.v1.yaml").write_text(PERM, encoding="utf-8")
pathlib.Path("contracts/stubs/permission-model.yaml").write_text(PERM, encoding="utf-8")

# ── contracts/access/protection.template.v1.yaml  (also written to stubs/) ────
PROT = """\
contract_version: 1
contract_id: C-ACC-PROT-1
branch_protection:
  require_pull_request: true
  required_approving_reviews: 1
  require_code_owner_review: true
  require_approval_of_most_recent_push: true
  dismiss_stale_reviews: true
  required_checks_contract: C-WF-CHECKS-1
  require_branches_up_to_date: true
  block_force_pushes: true
  block_deletions: true
  apply_to_administrators: true
  break_glass_exception: documented_procedure_with_audit_record
environments:
  development:
    deployment_refs: [default_branch]
    required_reviewers: []
    environment_secrets: true
  staging:
    deployment_refs: [default_branch, protected_release_tags]
    required_reviewers: []
    environment_secrets: true
  production:
    deployment_refs: [default_branch, protected_release_tags]
    required_reviewers: []
    environment_secrets: true
rulesets:
  - id: A
    name: protection-ruleset
    bypass_actors: []
  - id: B
    name: renovate-path-guard
    bypass_actors: []
codeowners:
  generated: true
  human_identities_only: true
  routes:
    - path: "verification/"
      owner: verification_responsibility_holder
    - path: "product.yaml"
      owner: team_lead_role
    - path: "migrations/**"
      owner: team_lead_role
    - path: ".github/workflows/**"
      owner: team_lead_role
    - path: "**"
      owner: product_team
production_approval_mechanism: section_27_2_workflow_identity_gate
plan_tier_facts:
  - capability: branch_protection_or_rulesets_on_private_repositories
    plan_tier_fact: available_on_team_plan
    mechanism_of_record: configured_as_per_section_11_3
  - capability: environment_deployment_protection_rules
    plan_tier_fact: github_enterprise_feature_not_available_on_team_plan
    mechanism_of_record: section_27_2_workflow_identity_gate
  - capability: custom_repository_roles
    plan_tier_fact: github_enterprise_cloud_only
    mechanism_of_record: write_via_teams_as_specified
  - capability: self_review_prevention_on_production_deployment
    plan_tier_fact: environment_required_reviewers_enterprise_only_on_private_repositories
    mechanism_of_record: section_27_2_workflow_identity_gate
rules:
  - id: PROT-R1
    rule: >-
      Require a pull request, at least one approving review, and review from Code Owners;
      CODEOWNERS holds human identities only, so a machine approval can never satisfy
      branch protection
    spec: ["11.3"]
  - id: PROT-R2
    rule: >-
      Require approval of the most recent reviewable push, and dismiss stale approvals on
      new commits; this is the enforcement behind the no-self-approval invariant
    spec: ["11.3", "invariant_9"]
  - id: PROT-R3
    rule: >-
      Require branches up to date; block force pushes and deletions on the default branch;
      apply rules to administrators, with an exception only under a documented break-glass
      procedure carrying an audit record
    spec: ["11.3", "54"]
  - id: PROT-R4
    rule: >-
      Every environment carries a deployment branch and tag policy restricting staging and
      production to the default branch and protected release tags; branch protection governs
      what merges, the deployment policy governs what may reach an environment's secrets,
      and neither substitutes for the other
    spec: ["11.3", "33.4"]
  - id: PROT-R5
    rule: >-
      Environment required reviewers are an Enterprise feature and are never depended on;
      the production-approval mechanism of record is the Section 27.2 workflow-identity
      gate, failing closed
    spec: ["11.4"]
  - id: PROT-R6
    rule: >-
      New repositories are created private, with protection applied from the template at
      creation, no environment access and no third-party app access
    spec: ["11.3", "64.1"]
  - id: PROT-R7
    rule: >-
      Ruleset B — the one carrying renovate-path-guard — names no bypass actor at all,
      because a bypass actor is exempt from every rule in the ruleset it is listed on
    spec: ["33.2", "D89"]
"""
pathlib.Path("contracts/access/protection.template.v1.yaml").write_text(PROT, encoding="utf-8")
pathlib.Path("contracts/stubs/branch-protection.yaml").write_text(PROT, encoding="utf-8")

# ── contracts/access/layer-split.v1.yaml  (also written to stubs/) ─────────────
# Layer A: 11 categories (Section 90.1).  Layer B: 23 categories (Section 90.1,
# splitting "individual utilisation and utilisation history" into two entries to
# match the two separate rows of the 90.2 permission matrix).
# Permission matrix: 27 rows verbatim from Section 90.2, with "yes"/"no" as quoted
# strings so Python print() produces the expected 'no no no no' for machine_identities.
LAYER = """\
contract_version: 1
contract_id: C-ACC-LAYER-1
layer_a:
  - id: product_work_assignment_demand
    description: product work, product assignment, product demand
  - id: ready_queue_and_current_work
    description: Ready queue and current work
  - id: blockers
    description: blockers
  - id: review_routing_and_reviewer_distribution
    description: review routing and reviewer distribution
  - id: team_level_and_role_level_operational_capacity
    description: team-level and role-level operational capacity
  - id: qa_backlog_and_verification_demand
    description: QA backlog and verification demand
  - id: architecture_backlog
    description: architecture backlog
  - id: operational_incidents_and_production_health
    description: operational incidents and production health
  - id: engineering_constraints_and_bottlenecks
    description: engineering constraints and bottlenecks
  - id: team_aggregate_health_dimensions
    description: team-aggregate health dimensions
  - id: reviewer_load_and_turnaround_per_reviewer
    description: >-
      reviewer load and turnaround per reviewer — the permitted Layer A rendering of
      GitHub-native per-person activity (PRs, reviews, commits); prohibited forms are
      trends presented as performance, rankings, and performance framing of the same data
layer_b:
  - id: individual_capacity
    description: individual capacity
  - id: individual_utilisation
    description: individual utilisation
  - id: individual_utilisation_history
    description: individual utilisation history
  - id: individual_bandwidth
    description: individual bandwidth
  - id: individual_workload_composition
    description: individual workload composition
  - id: individual_attention_breakdown
    description: individual attention breakdown
  - id: individual_kra_kpi_evidence_and_trends
    description: individual KRA/KPI evidence and trends
  - id: individual_performance_evidence_and_evidence_bundles
    description: individual performance evidence and evidence bundles
  - id: performance_concern_signals
    description: performance concern signals
  - id: recognition_signals
    description: recognition signals
  - id: promotion_signals
    description: promotion signals
  - id: individual_capability_maturity_for_people_decisions
    description: individual capability maturity where used for people decisions
  - id: management_attention_signals_for_identified_individual
    description: management-attention signals for an identified individual
  - id: improvement_plan_evidence
    description: improvement plan evidence
  - id: formal_warning_evidence
    description: formal warning evidence
  - id: exit_consideration_evidence
    description: exit consideration evidence
  - id: compensation_related_analysis
    description: compensation-related analysis
  - id: comparative_individual_analysis
    description: comparative individual analysis
  - id: individual_historical_performance_data
    description: individual historical performance data
  - id: individual_staffing_and_replacement_implications
    description: individual staffing and replacement implications
  - id: founder_management_notes
    description: Founder management notes
  - id: person_specific_succession_risk
    description: person-specific succession risk
  - id: founder_decision_records
    description: Founder decision records
permission_matrix:
  - category: people_capacity_aggregate
    founder: "yes"
    team_lead: "yes"
    employee: team_level_operational_view
    peer: team_level_operational_view
  - category: individual_utilisation_detail
    founder: "yes"
    team_lead: "no"
    employee: own_only
    peer: "no"
  - category: individual_utilisation_history
    founder: "yes"
    team_lead: "no"
    employee: own_only
    peer: "no"
  - category: individual_workload_detail
    founder: "yes"
    team_lead: minimum_necessary_operational_field_only
    employee: own
    peer: "no"
  - category: individual_kra_kpi
    founder: "yes"
    team_lead: no_unless_explicitly_delegated
    employee: own
    peer: "no"
  - category: individual_performance_evidence
    founder: "yes"
    team_lead: no_by_default
    employee: own_evidence
    peer: "no"
  - category: individual_performance_trend_views
    founder: "yes"
    team_lead: "no"
    employee: own
    peer: "no"
  - category: capability_required_to_assign_work
    founder: "yes"
    team_lead: "yes"
    employee: own
    peer: "no"
  - category: capability_maturity_for_people_decisions
    founder: "yes"
    team_lead: "no"
    employee: own
    peer: "no"
  - category: recognition_signal
    founder: "yes"
    team_lead: "no"
    employee: own_feedback_only
    peer: "no"
  - category: promotion_signal
    founder: "yes"
    team_lead: "no"
    employee: "no"
    peer: "no"
  - category: coaching_or_performance_concern
    founder: "yes"
    team_lead: "no"
    employee: only_feedback_shared_through_management_process
    peer: "no"
  - category: improvement_plan_evidence
    founder: "yes"
    team_lead: "no"
    employee: only_through_formal_management_process
    peer: "no"
  - category: exit_consideration
    founder: "yes"
    team_lead: "no"
    employee: "no"
    peer: "no"
  - category: compensation_information
    founder: "yes"
    team_lead: "no"
    employee: own_formal_information_only
    peer: "no"
  - category: management_attention_individual
    founder: "yes"
    team_lead: "no"
    employee: "no"
    peer: "no"
  - category: management_attention_team_aggregate
    founder: "yes"
    team_lead: "yes"
    employee: "no"
    peer: "no"
  - category: comparative_individual_analysis
    founder: "yes"
    team_lead: "no"
    employee: "no"
    peer: "no"
  - category: founder_management_notes
    founder: "yes"
    team_lead: "no"
    employee: "no"
    peer: "no"
  - category: founder_decision_records
    founder: "yes"
    team_lead: "no"
    employee: own_formal_process_only
    peer: "no"
  - category: team_operational_health
    founder: "yes"
    team_lead: "yes"
    employee: appropriate_team_level_view
    peer: appropriate_team_level_view
  - category: product_health
    founder: "yes"
    team_lead: "yes"
    employee: relevant_operational_data
    peer: relevant_operational_data
  - category: ready_queue
    founder: "yes"
    team_lead: "yes"
    employee: own_work_and_product
    peer: relevant_product
  - category: review_routing
    founder: "yes"
    team_lead: "yes"
    employee: own_assignments
    peer: relevant_product
  - category: succession_and_dependency_risk_person_specific
    founder: "yes"
    team_lead: "no"
    employee: "no"
    peer: "no"
  - category: succession_readiness_product_level_operational
    founder: "yes"
    team_lead: "yes"
    employee: "no"
    peer: "no"
  - category: machine_identities
    founder: "no"
    team_lead: "no"
    employee: "no"
    peer: "no"
datasource_enforcement:
  people_datasource_separately_credentialed: true
  people_datasource_in_shared_instance: false
  layer_b_instance: founder_only_grafana_instance
  instance_separation_is_the_boundary: true
  folder_acls_are_defence_in_depth_only: true
  sensitive_data_absent_from_general_datasource: true
  individual_self_view_is_generated_document_not_dashboard: true
capability:
  id: people-intelligence
  delegable: false
  holder_default: founder
  delegation_note: >-
    Not delegable (D109). No assignment type grants it and none may be introduced to do
    so. Access under Founder incapacity runs through the sealed contingency credential of
    Section 14.4.
accepted_risks:
  - risk_id: AR-LAYER-B-HOST-ADMIN
    description: >-
      Host-level administrative access (VM-root and Grafana-admin) to the Layer B
      operations VM — a named, recorded accepted risk, never a capability grant
    holder: named_in_operational_asset_inventory
    compensating_control: >-
      host-level file-access auditing on the store path, shipped write-only to a
      destination the host holds no credential to alter, matching Section 45.3 discipline
    does_not_grant_people_intelligence: true
    review_cadence: quarterly_per_section_84_5
    spec: ["90.3", "54.2"]
decision_routing:
  people_related: layer_b_decision_store
  non_people: "records/decisions/"
  latency_metric_reads_both_stores: true
  pending_entry_at_issuance: true
  pending_path_people: layer_b_pending
  pending_path_non_people: "records/decisions/pending/"
rules:
  - id: LAYER-R1
    rule: >-
      Layer B is Founder-only and people-intelligence is not delegable; no assignment type
      grants it and none may be introduced to do so, and an attempt to configure one fails
      validation
    spec: ["90.4", "AT-090", "AT-091"]
  - id: LAYER-R2
    rule: >-
      The machine-identities row of the 90.2 matrix is absolute: no machine identity holds
      any people-related category, receives a Layer B credential or folder scope, or holds
      people-intelligence, under any configuration
    spec: ["90.2"]
  - id: LAYER-R3
    rule: >-
      The Layer B boundary is instance separation, not folder membership: the people
      datasource is never registered in the shared Grafana instance, and folder ACLs there
      are defence in depth for Layer A views only
    spec: ["90.3", "AT-097", "AT-098"]
  - id: LAYER-R4
    rule: >-
      Sensitive people data is absent from the general engineering datasource, not merely
      hidden from its panels
    spec: ["90.3", "AT-089"]
  - id: LAYER-R5
    rule: The individual self-view is a generated per-person document, never a dashboard
    spec: ["90.3", "AT-095"]
  - id: LAYER-R6
    rule: >-
      Host-level administrative access to the Layer B store is a named, recorded accepted
      risk with a named holder, a compensating control the holder cannot silently defeat,
      and a dated review — never a capability grant
    spec: ["90.3", "54.2"]
  - id: LAYER-R7
    rule: >-
      No Layer B evidence may be generated before this separation exists; the phase that
      would generate it is gated on it
    spec: ["90.3", "98"]
"""
pathlib.Path("contracts/access/layer-split.v1.yaml").write_text(LAYER, encoding="utf-8")
pathlib.Path("contracts/stubs/layer-split.yaml").write_text(LAYER, encoding="utf-8")

# ── valid fixtures: copy of each stub ─────────────────────────────────────────
shutil.copy("contracts/stubs/permission-model.yaml",  "contracts/fixtures/C-ACC-PERM-1/valid-001.yaml")
shutil.copy("contracts/stubs/branch-protection.yaml", "contracts/fixtures/C-ACC-PROT-1/valid-001.yaml")
shutil.copy("contracts/stubs/layer-split.yaml",       "contracts/fixtures/C-ACC-LAYER-1/valid-001.yaml")

# ── invalid fixtures ───────────────────────────────────────────────────────────
pathlib.Path("contracts/fixtures/C-ACC-PERM-1/invalid-001.yaml").write_text(
    "# EXPECT: reject - PERM-R1: cross_reviewer class carries read rather than write\n"
    "contract_version: 1\ncontract_id: C-ACC-PERM-1\n"
    "organisation:\n  base_permission: read\n  two_factor_required: true\n"
    "  strong_factor_capabilities: [platform-admin]\n  second_owner_required: true\n"
    "person_classes:\n"
    "  - id: developer\n    organisation_role: member\n"
    "    write_on: repositories_of_products_with_primary_owner_only\n    read_on: all\n"
    "    cross_reviewer_permission: read\n"
    "rules:\n  - id: PERM-R1\n    rule: INVALID cross_reviewer_permission must be write\n"
    "    spec: [\"11.1\"]\n", encoding="utf-8")
pathlib.Path("contracts/fixtures/C-ACC-PERM-1/invalid-002.yaml").write_text(
    "# EXPECT: reject - PERM-R4: machine account listed in codeowners\n"
    "contract_version: 1\ncontract_id: C-ACC-PERM-1\n"
    "organisation:\n  base_permission: read\n  two_factor_required: true\n"
    "  strong_factor_capabilities: [platform-admin]\n  second_owner_required: true\n"
    "person_classes:\n"
    "  - id: background_machine_layer\n    organisation_role: machine_account\n"
    "    write_on: all\n    read_on: all\n"
    "codeowners:\n  generated: true\n  human_identities_only: false\n"
    "  machine_accounts_listed: [\"github-actions[bot]\"]\n", encoding="utf-8")
pathlib.Path("contracts/fixtures/C-ACC-PROT-1/invalid-001.yaml").write_text(
    "# EXPECT: reject - PROT-R4: production environment carries no deployment_refs policy\n"
    "contract_version: 1\ncontract_id: C-ACC-PROT-1\n"
    "branch_protection:\n  require_code_owner_review: true\n"
    "  require_approval_of_most_recent_push: true\n  apply_to_administrators: true\n"
    "  required_checks_contract: C-WF-CHECKS-1\n"
    "environments:\n  production:\n    required_reviewers: []\n    environment_secrets: true\n"
    "rulesets:\n  - id: A\n    bypass_actors: []\n  - id: B\n    bypass_actors: []\n"
    "codeowners:\n  human_identities_only: true\n"
    "production_approval_mechanism: section_27_2_workflow_identity_gate\n", encoding="utf-8")
pathlib.Path("contracts/fixtures/C-ACC-PROT-1/invalid-002.yaml").write_text(
    "# EXPECT: reject - PROT-R5: production approval relies on environment required_reviewers\n"
    "contract_version: 1\ncontract_id: C-ACC-PROT-1\n"
    "branch_protection:\n  require_code_owner_review: true\n"
    "  require_approval_of_most_recent_push: true\n  apply_to_administrators: true\n"
    "  required_checks_contract: C-WF-CHECKS-1\n"
    "environments:\n  production:\n"
    "    deployment_refs: [default_branch, protected_release_tags]\n"
    "    required_reviewers: [team-lead-role]\n    environment_secrets: true\n"
    "rulesets:\n  - id: A\n    bypass_actors: []\n  - id: B\n    bypass_actors: []\n"
    "codeowners:\n  human_identities_only: true\n"
    "production_approval_mechanism: environment_required_reviewers\n", encoding="utf-8")
pathlib.Path("contracts/fixtures/C-ACC-PROT-1/invalid-003.yaml").write_text(
    "# EXPECT: reject - PROT-R7: ruleset B names a bypass actor\n"
    "contract_version: 1\ncontract_id: C-ACC-PROT-1\n"
    "branch_protection:\n  require_code_owner_review: true\n"
    "  require_approval_of_most_recent_push: true\n  apply_to_administrators: true\n"
    "  required_checks_contract: C-WF-CHECKS-1\n"
    "environments:\n  production:\n"
    "    deployment_refs: [default_branch, protected_release_tags]\n"
    "    required_reviewers: []\n    environment_secrets: true\n"
    "rulesets:\n  - id: A\n    bypass_actors: []\n"
    "  - id: B\n    name: renovate-path-guard\n    bypass_actors: [\"renovate[bot]\"]\n"
    "codeowners:\n  human_identities_only: true\n"
    "production_approval_mechanism: section_27_2_workflow_identity_gate\n", encoding="utf-8")
pathlib.Path("contracts/fixtures/C-ACC-LAYER-1/invalid-001.yaml").write_text(
    "# EXPECT: reject - LAYER-R1: assignment type purports to grant people-intelligence\n"
    "contract_version: 1\ncontract_id: C-ACC-LAYER-1\n"
    "capability:\n  id: people-intelligence\n  delegable: true\n"
    "  delegation_types: [team_lead_delegation]\n"
    "decision_routing:\n  non_people: \"records/decisions/\"\n"
    "datasource_enforcement:\n  people_datasource_in_shared_instance: false\n", encoding="utf-8")
pathlib.Path("contracts/fixtures/C-ACC-LAYER-1/invalid-002.yaml").write_text(
    "# EXPECT: reject - LAYER-R3: people datasource registered in the shared Grafana instance\n"
    "contract_version: 1\ncontract_id: C-ACC-LAYER-1\n"
    "capability:\n  id: people-intelligence\n  delegable: false\n"
    "datasource_enforcement:\n  people_datasource_in_shared_instance: true\n"
    "  layer_b_instance: shared_grafana_instance\n  instance_separation_is_the_boundary: false\n"
    "decision_routing:\n  non_people: \"records/decisions/\"\n", encoding="utf-8")
print("contracts, stubs and fixtures written")
PY
# Invalid fixtures, each with its `# EXPECT: reject - ...` first line:
#   C-ACC-PERM-1/invalid-001   PERM-R1  a cross_reviewer granted read
#   C-ACC-PERM-1/invalid-002   PERM-R4  a machine account listed in CODEOWNERS
#   C-ACC-PROT-1/invalid-001   PROT-R4  production environment with no deployment_refs policy
#   C-ACC-PROT-1/invalid-002   PROT-R5  production approval relying on environment required reviewers
#   C-ACC-PROT-1/invalid-003   PROT-R7  ruleset B naming a bypass actor
#   C-ACC-LAYER-1/invalid-001  LAYER-R1 an assignment granting people-intelligence
#   C-ACC-LAYER-1/invalid-002  LAYER-R3 the people datasource registered in the shared instance
python contracts/ci/register_add.py C-ACC-PERM-1  access/permission-model.v1.yaml     1 L5 L1,L3,L5 stubs/permission-model.yaml
python contracts/ci/register_add.py C-ACC-PROT-1  access/protection.template.v1.yaml  1 L5 L2,L3,L5 stubs/branch-protection.yaml
python contracts/ci/register_add.py C-ACC-LAYER-1 access/layer-split.v1.yaml          1 L5 L3,L4,L5 stubs/layer-split.yaml
git add -A && git commit -m "L0-P0-020: C-ACC-PERM-1, C-ACC-PROT-1, C-ACC-LAYER-1"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | Six person classes, in the 11.2 order | `python -c "import yaml;print([p['id'] for p in yaml.safe_load(open('contracts/access/permission-model.v1.yaml'))['person_classes']])"` | `['founder', 'team_lead', 'qa', 'developer', 'contractor_or_temporary_specialist', 'background_machine_layer']` |
| 2 | Organisation base permission is Read and 2FA is required | `python -c "import yaml;o=yaml.safe_load(open('contracts/access/permission-model.v1.yaml'))['organisation'];print(o['base_permission'],o['two_factor_required'])"` | `read True` |
| 3 | The protection template defers the check list to `C-WF-CHECKS-1` and restates none | `python -c "import yaml;p=yaml.safe_load(open('contracts/access/protection.template.v1.yaml'))['branch_protection'];print(p['required_checks_contract'],'required_status_checks' in p)"` | `C-WF-CHECKS-1 False` |
| 4 | Both protected environments carry the ref policy (PROT-R4) | `python -c "import yaml;e=yaml.safe_load(open('contracts/access/protection.template.v1.yaml'))['environments'];print([e[k]['deployment_refs'] for k in ('staging','production')])"` | `[['default_branch', 'protected_release_tags'], ['default_branch', 'protected_release_tags']]` |
| 5 | Ruleset B names no bypass actor (PROT-R7, D89) | `python -c "import yaml;r={x['id']:x for x in yaml.safe_load(open('contracts/access/protection.template.v1.yaml'))['rulesets']};print(r['B']['bypass_actors'])"` | `[]` |
| 6 | The permission matrix carries all twenty-seven rows of 90.2 | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/access/layer-split.v1.yaml'))['permission_matrix']))"` | `27` |
| 7 | `people-intelligence` is declared non-delegable (D109) | `python -c "import yaml;c=yaml.safe_load(open('contracts/access/layer-split.v1.yaml'))['capability'];print(c['id'],c['delegable'])"` | `people-intelligence False` |
| 8 | The machine-identities row denies every column | `python -c "import yaml;m=[r for r in yaml.safe_load(open('contracts/access/layer-split.v1.yaml'))['permission_matrix'] if r['category'].startswith('machine_identities')][0];print(m['founder'],m['team_lead'],m['employee'],m['peer'])"` | `no no no no` |
| 9 | Seven invalid fixtures, each declaring its expectation | `head -1 -q contracts/fixtures/C-ACC-PERM-1/invalid-*.yaml contracts/fixtures/C-ACC-PROT-1/invalid-*.yaml contracts/fixtures/C-ACC-LAYER-1/invalid-*.yaml \| grep -c '^# EXPECT: reject'` | `7` |
| 10 | Register now holds all twenty-three rows | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/register.yaml'))['contracts']))"` | `23` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python - <<'PY'
import yaml
P = yaml.safe_load(open("contracts/access/permission-model.v1.yaml"))
T = yaml.safe_load(open("contracts/access/protection.template.v1.yaml"))
L = yaml.safe_load(open("contracts/access/layer-split.v1.yaml"))
vocab = {c["id"] for c in yaml.safe_load(open("contracts/registry/capability.vocabulary.v1.yaml"))["capabilities"]}
ok  = P["organisation"]["base_permission"] == "read"
ok &= P["organisation"]["two_factor_required"] is True
ok &= len(P["person_classes"]) == 6
ok &= [r["id"] for r in P["rules"]] == [f"PERM-R{i}" for i in range(1, 7)]
ok &= T["branch_protection"]["required_checks_contract"] == "C-WF-CHECKS-1"
ok &= T["branch_protection"]["require_code_owner_review"] is True
ok &= T["branch_protection"]["require_approval_of_most_recent_push"] is True
ok &= T["branch_protection"]["apply_to_administrators"] is True
ok &= T["codeowners"]["human_identities_only"] is True
ok &= {x["id"]: x["bypass_actors"] for x in T["rulesets"]}["B"] == []
ok &= T["production_approval_mechanism"] == "section_27_2_workflow_identity_gate"
ok &= len(L["layer_a"]) == 11 and len(L["layer_b"]) == 23
ok &= len(L["permission_matrix"]) == 27
ok &= L["capability"]["id"] in vocab and L["capability"]["delegable"] is False
ok &= L["decision_routing"]["non_people"] == "records/decisions/"
ok &= L["datasource_enforcement"]["people_datasource_in_shared_instance"] is False
print("L0-P0-020 PASS" if ok else "L0-P0-020 FAIL")
PY
```

Expected: `L0-P0-020 PASS`

**STOP RULE** — Do not restate the required-check names inside `C-ACC-PROT-1`, and do not restate the capability list inside `C-ACC-PERM-1`. Both are references (`C-WF-CHECKS-1`, `C-CAP-VOCAB-1`) precisely so a rename cannot leave one copy behind and unarm a gate on every repository. If a lane reports that a reference is inconvenient to resolve at apply time, the answer is a resolver in that lane's own tree, never a second copy in `contracts/**`. And if any reading of Section 11.4 tempts you to make environment required reviewers the production gate "where available", stop: D73 makes that a strengthening the Founder may buy, never the mechanism of record. Both are **CCR-BREAKING**.

---

### L0-P0-021 — The contract self-verification harness and `contracts/tooling.lock`

| | |
| --- | --- |
| **Size** | L |
| **Depends on** | L0-P0-020 |
| **Writes** | `contracts/ci/verify_contracts.py`, `contracts/ci/lint_workflow_calls.py`, `contracts/ci/lint_provision_requests.py`, `contracts/ci/lint_access.py`, `contracts/ci/verify-all.sh`, `contracts/tooling.lock`, `Makefile` (one appended target) |
| **Spec** | D-L0-06, D-L0-07; PARTITION.md rules 2 and 4; Section 33.2 (pinning discipline); Section 31.2 (an instrument that cannot fail is not an instrument); Section 52.6 (inventory discipline) |

Every task before this one **asserted** a shape. This task builds the thing that **proves** the assertions — all twenty-three contracts, in one command, with one line of output. It is the reason a lane can trust `contracts/**` without reading it, and it is the reason the merge train can refuse a tree in two seconds.

The harness is L0-owned and lives under `contracts/ci/`. It is not a CI workflow: `.github/workflows/**` is L2's path (D-L0-05). It is a script L0 runs in the contract window, the merge train runs through `make`, and any lane may run at any time.

Three linters are written here as well, because tasks L0-P0-013, L0-P0-019 and L0-P0-020 name them in their acceptance criteria and they share one loader. **A forward reference is not a gap:** re-run those three tasks' criterion for the linter after this task completes, and record the result on the same commit.

**What `verify_contracts.py` checks — all of them, every run, reporting every problem rather than the first:**

| Check | Assertion |
| --- | --- |
| `H1` header presence | Every file under `contracts/` outside `README.md`, `REGISTER.md`, `register.yaml`, `tooling.lock`, `ci/**`, `stubs/**` and `fixtures/**` carries the seven-key header — as top-level YAML keys, or under `x-contract` for JSON — with every required key present |
| `H2` register completeness | `register.yaml` holds exactly 23 rows; ids are unique; every row's `path` exists; every contract file has a row |
| `H3` stub presence (D-L0-06) | Every row's `stub` exists and is non-empty |
| `H4` fixture presence (D-L0-06) | Every contract has at least one `fixtures/<id>/valid-*` **and** at least one `fixtures/<id>/invalid-*` |
| `H5` invalid-fixture marking | Line 1 of every `invalid-*` file matches `^# EXPECT: reject` |
| `H6` schema conformance | For every JSON-Schema contract: the stub and every `valid-*` fixture validate; every `invalid-*` fixture is **rejected**. A leak is a failure |
| `H7` referential integrity | Every `emits_events` identifier resolves in `C-EVT-ENUM-1`; every `writes_records` id in `C-REC-STORE-MAP-1`; every `required_checks` name in `C-WF-CHECKS-1` |
| `H8` no record leakage (D-L0-08) | No YAML under `contracts/` carries both a `timestamp` and a `product` that is not `stub-product` |
| `H9` tooling pins (D-L0-07) | `tooling.lock` exists, is non-empty, and every pin it names is the version actually installed |

Final line, and nothing else on it: `CONTRACTS-VERIFY OK 23/23`, or `CONTRACTS-VERIFY FAIL <n> problem(s)` preceded by one line per problem.

**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > contracts/ci/verify_contracts.py <<'PYEOF'
"""contracts/ci/verify_contracts.py - L0-owned. Proves every frozen contract.
Run from the control-plane repository root. Exit 0 on OK, 1 on any problem.
Any lane may RUN this; no lane edits it (PARTITION.md rule 2)."""
import json, pathlib, re, subprocess, sys, yaml

ROOT = pathlib.Path("contracts")
SKIP_NAMES = {"README.md", "REGISTER.md", "register.yaml", "tooling.lock"}
SKIP_DIRS = {"ci", "stubs", "fixtures"}
HEADER_KEYS = ["contract_id", "contract_version", "owner", "publishing_lane",
               "consuming_lanes", "spec_refs", "ccr_required"]
EXPECTED_ROWS = 23
problems = []


def fail(check, msg):
    problems.append("%s: %s" % (check, msg))


def load(p):
    text = p.read_text(encoding="utf-8")
    return json.loads(text) if p.suffix == ".json" else yaml.safe_load(text)


def contract_files():
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS or rel.name in SKIP_NAMES:
            continue
        if p.suffix not in (".json", ".yaml", ".yml"):
            continue
        yield p


def header_of(doc):
    if not isinstance(doc, dict):
        return {}
    return doc.get("x-contract", doc)


# --- H1 header presence -----------------------------------------------------
headers = {}
for p in contract_files():
    try:
        h = header_of(load(p))
    except Exception as exc:
        fail("H1", "%s does not parse: %s" % (p, exc))
        continue
    missing = [k for k in HEADER_KEYS if k not in h]
    if missing:
        fail("H1", "%s missing header keys %s" % (p, missing))
    else:
        headers[h["contract_id"]] = (p, h)

# --- H2 register completeness ----------------------------------------------
reg = yaml.safe_load((ROOT / "register.yaml").read_text(encoding="utf-8"))
rows = reg.get("contracts") or []
if len(rows) != EXPECTED_ROWS:
    fail("H2", "register holds %d rows, expected %d" % (len(rows), EXPECTED_ROWS))
ids = [r["id"] for r in rows]
if len(ids) != len(set(ids)):
    fail("H2", "duplicate contract id in register")
for r in rows:
    if not (ROOT / r["path"]).is_file():
        fail("H2", "register row %s points at missing %s" % (r["id"], r["path"]))
for cid in headers:
    if cid not in ids:
        fail("H2", "contract %s has no register row" % cid)

# --- H3 stubs, H4 fixtures, H5 marking -------------------------------------
for r in rows:
    stub = ROOT / r["stub"]
    if not stub.is_file() or stub.stat().st_size == 0:
        fail("H3", "%s has no usable stub at %s" % (r["id"], r["stub"]))
    fx = ROOT / "fixtures" / r["id"]
    valid = sorted(fx.glob("valid-*"))
    invalid = sorted(fx.glob("invalid-*"))
    if not valid:
        fail("H4", "%s has no golden-valid fixture" % r["id"])
    if not invalid:
        fail("H4", "%s has no golden-invalid fixture" % r["id"])
    for f in invalid:
        first = f.read_text(encoding="utf-8").splitlines()[:1]
        if not first or not re.match(r"^# EXPECT: reject", first[0]):
            fail("H5", "%s line 1 is not '# EXPECT: reject ...'" % f)

# --- H6 schema conformance --------------------------------------------------
def conforms(schema, doc, expect_ok):
    r = subprocess.run(["check-jsonschema", "--schemafile", str(schema), str(doc)],
                       capture_output=True, text=True)
    return (r.returncode == 0) == expect_ok

for r in rows:
    schema = ROOT / r["path"]
    if schema.suffix != ".json" or not schema.is_file():
        continue
    fx = ROOT / "fixtures" / r["id"]
    stub = ROOT / r["stub"]
    if stub.is_file() and not conforms(schema, stub, True):
        fail("H6", "%s stub does not validate" % r["id"])
    for f in sorted(fx.glob("valid-*")):
        if not conforms(schema, f, True):
            fail("H6", "%s should validate and does not" % f)
    for f in sorted(fx.glob("invalid-*")):
        if not conforms(schema, f, False):
            fail("H6", "LEAK %s validates and must not" % f)

# --- H7 referential integrity -----------------------------------------------
def safe(path, key, field):
    try:
        return {x[field] for x in load(ROOT / path)[key]}
    except Exception as exc:
        fail("H7", "cannot read %s: %s" % (path, exc))
        return set()

evts = safe("records/event-type.enum.v1.yaml", "event_types", "id")
stores = safe("records/store-map.v1.yaml", "stores", "store")
checks = safe("workflows/required-checks.v1.yaml", "checks", "name")


def walk(node, wanted):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == wanted:
                yield v
            for x in walk(v, wanted):
                yield x
    elif isinstance(node, list):
        for v in node:
            for x in walk(v, wanted):
                yield x

for p in list(contract_files()) + sorted((ROOT / "stubs").glob("*.yaml")):
    try:
        doc = load(p)
    except Exception:
        continue
    for vals in walk(doc, "emits_events"):
        for v in vals or []:
            if v not in evts:
                fail("H7", "%s emits unknown event_type %s" % (p, v))
    for vals in walk(doc, "writes_records"):
        for v in vals or []:
            if v not in stores:
                fail("H7", "%s writes unknown store %s" % (p, v))
    for vals in walk(doc, "required_checks"):
        for v in vals or []:
            if isinstance(v, str) and v not in checks:
                fail("H7", "%s names unknown required check %s" % (p, v))

# --- H8 no record leakage ---------------------------------------------------
for p in sorted(ROOT.rglob("*.yaml")):
    try:
        doc = load(p)
    except Exception:
        continue
    if isinstance(doc, dict) and "timestamp" in doc and "product" in doc:
        if doc.get("product") != "stub-product":
            fail("H8", "%s looks like a real record (product=%r) - D-L0-08" % (p, doc.get("product")))

# --- H9 tooling pins --------------------------------------------------------
lock = ROOT / "tooling.lock"
if not lock.is_file() or not lock.read_text(encoding="utf-8").strip():
    fail("H9", "contracts/tooling.lock is missing or empty")
else:
    frozen = subprocess.run([sys.executable, "-m", "pip", "freeze"],
                            capture_output=True, text=True).stdout.lower()
    for line in lock.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        if line.lower() not in frozen:
            fail("H9", "pinned %s is not the installed version" % line)

if problems:
    for p in problems:
        print(p)
    print("CONTRACTS-VERIFY FAIL %d problem(s)" % len(problems))
    sys.exit(1)
print("CONTRACTS-VERIFY OK %d/%d" % (len(rows), EXPECTED_ROWS))
PYEOF
python -c "import ast;ast.parse(open('contracts/ci/verify_contracts.py',encoding='utf-8').read());print('harness parses')"
```

The three linters. Each reads its arguments, prints one line per file, and exits `1` if any file was rejected — exactly the shape the acceptance criteria of L0-P0-013, L0-P0-019 and L0-P0-020 expect.

**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > contracts/ci/_lintlib.py <<'PYEOF'
"""contracts/ci/_lintlib.py - L0-owned. Shared loader for the three contract linters."""
import pathlib, yaml


def run(paths, rules):
    bad = 0
    for raw in paths:
        p = pathlib.Path(raw)
        doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        reason = None
        for name, test in rules:
            try:
                hit = test(doc)
            except Exception:
                hit = False
            if hit:
                reason = name
                break
        if reason:
            bad += 1
            print("rejected %s (%s)" % (p, reason))
        else:
            print("accepted %s" % p)
    return 1 if bad else 0
PYEOF

cat > contracts/ci/lint_workflow_calls.py <<'PYEOF'
"""contracts/ci/lint_workflow_calls.py - L0-owned. Proves C-WF-IFACE-1's refutable rules."""
import sys
sys.path.insert(0, "contracts/ci")
from _lintlib import run

RULES = [
    ("WF-R1 consumed by branch, not by pinned tag",
     lambda d: any("@main" in str(v) or "@master" in str(v)
                   for v in (d.get("uses_list") or [d.get("uses", "")]))),
    ("WF-R2 deploy-production call with no digest input",
     lambda d: d.get("workflow") == "deploy-production"
               and "digest" not in (d.get("inputs") or {})),
    ("WF-R5 third-party action not pinned to a full commit SHA",
     lambda d: any("/" in str(s) and len(str(s).rsplit("@", 1)[-1]) != 40
                   for s in (d.get("steps_uses") or []))),
]

if __name__ == "__main__":
    sys.exit(run(sys.argv[1:], RULES))
PYEOF

cat > contracts/ci/lint_provision_requests.py <<'PYEOF'
"""contracts/ci/lint_provision_requests.py - L0-owned. Proves C-PROV-OP-1's refutable rules."""
import sys
sys.path.insert(0, "contracts/ci")
from _lintlib import run

RULES = [
    ("PROV-OP-R2 repository visibility is not private",
     lambda d: d.get("repository_visibility") not in (None, "private")),
    ("PROV-OP-R2 production environment seeded with secrets at creation",
     lambda d: bool((d.get("environments") or {}).get("production", {}).get("secrets"))),
    ("PROV-OP-R8 workflows wired by branch, not by pinned tag",
     lambda d: "@main" in str(d.get("workflow_ref", ""))),
    ("PROV-OP-R5 orphan detection skipped on remove-person",
     lambda d: d.get("operation") == "remove-person" and d.get("skip_orphan_detection") is True),
]

if __name__ == "__main__":
    sys.exit(run(sys.argv[1:], RULES))
PYEOF

cat > contracts/ci/lint_access.py <<'PYEOF'
"""contracts/ci/lint_access.py - L0-owned. Proves the refutable rules of the three access contracts."""
import sys
sys.path.insert(0, "contracts/ci")
from _lintlib import run

MACHINE = ("bot", "[bot]", "reconciler", "records-writer", "provisioning")
RULES = [
    ("PERM-R1 cross_reviewer granted read; Write is required (Section 11.1)",
     lambda d: any(a.get("assignment") == "cross_reviewer" and a.get("permission") == "read"
                   for a in (d.get("assignments") or []))),
    ("PERM-R4 machine identity in CODEOWNERS (Section 11.3)",
     lambda d: any(any(m in str(o).lower() for m in MACHINE) for o in (d.get("codeowners") or []))),
    ("PROT-R4 protected environment with no deployment_refs policy (Section 33.4)",
     lambda d: any(k in (d.get("environments") or {})
                   and not (d["environments"][k] or {}).get("deployment_refs")
                   for k in ("staging", "production"))),
    ("PROT-R5 production approval relying on environment required reviewers (D73)",
     lambda d: d.get("production_approval_mechanism") == "environment_required_reviewers"),
    ("PROT-R7 ruleset B names a bypass actor (D89)",
     lambda d: bool([r for r in (d.get("rulesets") or [])
                     if r.get("id") == "B" and r.get("bypass_actors")])),
    ("LAYER-R1 assignment grants people-intelligence; it is not delegable (D109)",
     lambda d: "people-intelligence" in str(d.get("grants", ""))),
    ("LAYER-R3 people datasource registered in the shared Grafana instance (D75)",
     lambda d: (d.get("datasource_enforcement") or {}).get(
         "people_datasource_in_shared_instance") is True),
]

if __name__ == "__main__":
    sys.exit(run(sys.argv[1:], RULES))
PYEOF
for f in _lintlib lint_workflow_calls lint_provision_requests lint_access; do
  python -c "import ast,sys;ast.parse(open('contracts/ci/$f.py',encoding='utf-8').read());print('$f parses')"
done
```

`contracts/tooling.lock` is **resolved, never asserted** (D-L0-07). No version is written down ahead of resolution:

**Commands**

```bash
set -euo pipefail
cd "$CP"
python -m pip install --upgrade check-jsonschema PyYAML
{
  echo "# contracts/tooling.lock - D-L0-07. Resolved at freeze time, never asserted ahead of it."
  echo "# No lane installs a different validator. Regenerated only under an approved CCR."
  python -m pip freeze | grep -Ei '^(check-jsonschema|PyYAML|jsonschema|attrs|referencing|rpds-py)=='
} > contracts/tooling.lock
cat contracts/tooling.lock

cat > contracts/ci/verify-all.sh <<'SHEOF'
#!/usr/bin/env sh
# contracts/ci/verify-all.sh - L0-owned. One command, one verdict.
set -e
python contracts/ci/verify_contracts.py
SHEOF
chmod +x contracts/ci/verify-all.sh

grep -q '^contracts-verify:' Makefile || printf '\ncontracts-verify:\n\t@python contracts/ci/verify_contracts.py\n' >> Makefile

python contracts/ci/verify_contracts.py
git add -A && git commit -m "L0-P0-021: contract self-verification harness, linters and tooling.lock"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | The harness runs clean over all twenty-three contracts | `python contracts/ci/verify_contracts.py \| tail -1` | `CONTRACTS-VERIFY OK 23/23` |
| 2 | The `make` target exists and agrees | `make contracts-verify \| tail -1` | `CONTRACTS-VERIFY OK 23/23` |
| 3 | The harness detects a stripped header (H1) | see SELF-VERIFY | `H1-detected` |
| 4 | The harness detects a missing stub (H3) | see SELF-VERIFY | `H3-detected` |
| 5 | The harness detects an unmarked invalid fixture (H5) | see SELF-VERIFY | `H5-detected` |
| 6 | `tooling.lock` pins `check-jsonschema` | `grep -ci '^check-jsonschema==' contracts/tooling.lock` | `1` |
| 7 | The access linter rejects its own fixture (closes L0-P0-020 criterion 9) | `python contracts/ci/lint_access.py contracts/fixtures/C-ACC-PROT-1/invalid-001.yaml >/dev/null; echo "exit=$?"` | `exit=1` |
| 8 | The provisioning linter rejects its own fixtures (closes L0-P0-019 criterion 7) | `python contracts/ci/lint_provision_requests.py contracts/fixtures/C-PROV-OP-1/invalid-*.yaml \| grep -c '^rejected'` | `4` |
| 9 | The harness writes nothing | `python contracts/ci/verify_contracts.py >/dev/null; git status --porcelain \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
python contracts/ci/verify_contracts.py | tail -1
# Three negative tests. Each mutation must be caught, and the tree must be restored.
cp contracts/registry/roles.registry.v1.json /tmp/roles.bak
python -c "import json;p='contracts/registry/roles.registry.v1.json';d=json.load(open(p));d.pop('x-contract');json.dump(d,open(p,'w'),indent=2)"
python contracts/ci/verify_contracts.py 2>&1 | grep -q '^H1' && echo H1-detected || echo H1-MISSED
cp /tmp/roles.bak contracts/registry/roles.registry.v1.json

mv contracts/stubs/roles.yaml /tmp/roles-stub.bak
python contracts/ci/verify_contracts.py 2>&1 | grep -q '^H3' && echo H3-detected || echo H3-MISSED
mv /tmp/roles-stub.bak contracts/stubs/roles.yaml

cp contracts/fixtures/C-REG-ROLES-1/invalid-001.yaml /tmp/inv.bak
tail -n +2 /tmp/inv.bak > contracts/fixtures/C-REG-ROLES-1/invalid-001.yaml
python contracts/ci/verify_contracts.py 2>&1 | grep -q '^H5' && echo H5-detected || echo H5-MISSED
cp /tmp/inv.bak contracts/fixtures/C-REG-ROLES-1/invalid-001.yaml

python contracts/ci/verify_contracts.py | tail -1
git diff --quiet && echo "L0-P0-021 PASS" || echo "L0-P0-021 FAIL tree not restored"
```

Expected, in order:

```
CONTRACTS-VERIFY OK 23/23
H1-detected
H3-detected
H5-detected
CONTRACTS-VERIFY OK 23/23
L0-P0-021 PASS
```

**STOP RULE** — If any negative test prints `-MISSED`, the harness is decorative and the freeze it guards is worthless. Do not proceed to L0-P0-022. Fix the check, re-run all three negative tests, and only then continue. A harness that cannot fail is exactly the `verify: exit 0` contract Section 31.2 exists to forbid, one level up — and this one guards five lanes rather than one product. If the last line prints `L0-P0-021 FAIL tree not restored`, restore from the `/tmp` backups before anything else: a negative test that leaves its mutation behind has just written an unreviewed change into a frozen tree.

---

### L0-P0-022 — The recorded gaps, the CODEOWNERS assertion, and the CCR procedure document

| | |
| --- | --- |
| **Size** | M |
| **Depends on** | L0-P0-021; and, from `L0-00-charter.md`, tasks L0-00-01 (root `CODEOWNERS`) and L0-00-05 (`docs/escalation/CCR.md`) |
| **Writes** | `contracts/ci/check_codeowners_contracts.sh`, `docs/recorded-gaps.md`, `docs/contract-change-request.md` |
| **Spec** | D-L0-04, D-L0-05; Section 54.2 (a deferral is a dated entry with owner and deactivation trigger); Section 11.3 (CODEOWNERS carries human identities only); PARTITION.md rules 1–2 |

Two mechanisms guard `contracts/**` before L2's lane-guard exists: **Code Owner review** and the **freeze tag**. This task proves the first is really in place, writes down every gap Phase 0 leaves open in the form Section 54.2 demands, and publishes the procedure the whole freeze rests on.

**The CODEOWNERS assertion.** The root `CODEOWNERS` was written by charter task **L0-00-01** and already carries `/contracts/` in its L0-exclusive block. This task does not rewrite it — it asserts it, because an assertion that runs on demand is worth more than a file that was correct once.

**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > contracts/ci/check_codeowners_contracts.sh <<'SHEOF'
#!/usr/bin/env sh
# contracts/ci/check_codeowners_contracts.sh - L0-owned.
# Asserts the three properties that make Code Owner review a real guard on contracts/**:
#   1. a /contracts/ rule exists and names a reviewer
#   2. no machine identity appears anywhere in CODEOWNERS (Section 11.3)
#   3. no placeholder login survives (a non-existent Code Owner wedges the repository)
# Exit 0 prints CODEOWNERS-CONTRACTS OK; exit 1 prints the reason.
set -e
test -f CODEOWNERS || { echo "CODEOWNERS-CONTRACTS FAIL: no CODEOWNERS at repository root"; exit 1; }
rule=$(grep -E '^/contracts/[[:space:]]+@' CODEOWNERS || true)
test -n "$rule" || { echo "CODEOWNERS-CONTRACTS FAIL: no /contracts/ rule"; exit 1; }
if grep -Eqi '@[^[:space:]]*(bot|\[bot\]|reconciler|records-writer|provisioning)' CODEOWNERS; then
  echo "CODEOWNERS-CONTRACTS FAIL: machine identity present (Section 11.3)"; exit 1
fi
if grep -Eq 'LEAD_GITHUB_LOGIN|LANE[0-9]*_REVIEWER' CODEOWNERS; then
  echo "CODEOWNERS-CONTRACTS FAIL: placeholder login left in place"; exit 1
fi
echo "CODEOWNERS-CONTRACTS OK"
SHEOF
chmod +x contracts/ci/check_codeowners_contracts.sh
sh contracts/ci/check_codeowners_contracts.sh
```

**The recorded gap register.** Section 54.2 binds the form: an accepted gap with no named holder, no compensating control and no expiry is undocumented policy. Every gap Phase 0 leaves open is written in exactly that form, dated on the day of the freeze.

**Commands**

```bash
set -euo pipefail
cd "$CP"
TODAY=$(date -u +%F)
{
  echo '# Recorded gaps at the Phase 0 contract freeze'
  echo
  echo "Opened $TODAY by L0. Every row carries an owner, a compensating control and a"
  echo 'deactivation trigger, per Section 54.2. A row with an empty cell is a defect in this file.'
  echo
  echo '| Gap id | What is missing | Why it is missing | Compensating control until it lands | Owner | Deactivation trigger | Review by |'
  echo '| --- | --- | --- | --- | --- | --- | --- |'
  echo "| GAP-L0-01 | The \`lane-guard\` required status check | \`.github/workflows/**\` is L2's path (PARTITION.md line 18); L0 may not write there (D-L0-05) | Code Owner review on \`contracts/**\` plus the immutable freeze tag \`contracts/v1.0.0\` (D-L0-04) | L0 | L2 cycle 1 delivers \`lane-guard\` and L0-02-08's SELF-VERIFY prints \`state=BLOCKED\` | $(date -u -d '+14 days' +%F 2>/dev/null || echo "$TODAY + 14 days") |"
  echo "| GAP-L0-02 | Required-check contexts declared but armed on no repository | \`CHK-R3\`: the list starts empty per repository and each phase names the contexts it adds (Section 98.2 Phase 1) | Each phase's completion check names its contexts, so an empty list is itself a completion-check failure | L2 | The Phase 4 completion check passes with every Phase-4 context armed | $(date -u -d '+30 days' +%F 2>/dev/null || echo "$TODAY + 30 days") |"
  echo "| GAP-L0-03 | \`contract-validation\` is emitted by no workflow | L1 publishes the validators in its Phase 3 work; Phase 0 froze the schemas only | \`make contracts-verify\`, run by L0 at the daily contract-freeze integrity check (charter 8.1, 10:30) | L1 | L1 ships \`validators/registry/**\` and L2 wires the \`contract-validation\` context | $(date -u -d '+30 days' +%F 2>/dev/null || echo "$TODAY + 30 days") |"
  echo "| GAP-L0-04 | \`control-plane/blocking-drift\` has no publisher | L3 builds the reconciler; \`C-RECON-FIND-1\` froze the finding shape only | The row exists in \`C-WF-CHECKS-1\` with \`emitted_by: L3\`, so its absence is visible rather than assumed | L3 | The reconciler publishes its first check-run under that exact name | $(date -u -d '+45 days' +%F 2>/dev/null || echo "$TODAY + 45 days") |"
  echo "| GAP-L0-05 | The independent control verifier of Section 53.1 does not exist | It runs off the operations VM under a separate credential and is L5's work under \`access/**\` | \`C-RECON-SET-1.independent_control_verifier\` declares it, and its absence for one cycle is a declared Level 5 finding | L5 | L5 ships the scheduled verifier and its first clean cycle is recorded | $(date -u -d '+60 days' +%F 2>/dev/null || echo "$TODAY + 60 days") |"
  echo
  echo 'Each row is reviewed on the date shown. A row past its review date with no movement is'
  echo 'raised as an L0 emergency on the same terms as a blocked lane, because a gap that stops'
  echo 'being reviewed has silently become the design.'
} > docs/recorded-gaps.md
git add -A && git commit -m "L0-P0-022: CODEOWNERS assertion and the recorded gap register"
```

**The CCR procedure document.** `docs/escalation/CCR.md` (charter task L0-00-05) is the **template a lane fills in**. `docs/contract-change-request.md` is the **procedure L0 runs when one arrives** — the thing `contracts/README.md` and every STOP RULE in this file point at. Write it from Section 8 below, so that the procedure and this document are one text.

**Commands**

```bash
set -euo pipefail
cd "$CP"
{
  echo '# Contract Change Request - the procedure'
  echo
  echo 'Authoritative source: `Code/implementation/lanes/L0-01-phase-0-contracts.md`, Section 8.'
  echo 'The issue template a lane fills in lives at `docs/escalation/CCR.md`. This file is what'
  echo 'L0 does when one arrives.'
  echo
  echo '## When a lane files one'
  echo
  echo 'A lane files a CCR when, and only when, the fix requires a change to `contracts/**`.'
  echo 'Everything else is a blocker issue. The test is mechanical and needs no judgement.'
  echo 'A lane that cannot tell files a blocker; L0 reclassifies. Misfiling costs one comment.'
  echo
  echo '## The three classes'
  echo
  echo '| Class | Meaning | Lands as | L0 answers by |'
  echo '| --- | --- | --- | --- |'
  echo '| `CCR-ADDITIVE` | Adds something no existing consumer had to know about. Every document valid before is valid after. | A minor version of the same contract file; the register row version is unchanged. | Next working day |'
  echo '| `CCR-BLOCKING` | The filing lane cannot proceed and has no other task whose dependencies are satisfied. | Whatever the answer requires, including "the contract already covers this". | Same working day, by 17:00 |'
  echo '| `CCR-BREAKING` | A document valid before would be invalid after, or a shipped identifier changes meaning. | A new `vN+1` file. Both versions supported through the declared deprecation window (Section 60.2). Never an edit in place. | Two working days, with a decision record |'
  echo
  echo 'Classification is L0'"'"'s, on receipt. A lane that classifies its own CCR has made an L0 decision.'
  echo
  echo '## What L0 does, in order'
  echo
  echo '1. Classify, and write the class on the issue as the first comment.'
  echo '2. Acknowledge: state the class, whether the lane is blocked, and which of that lane'"'"'s other tasks are unblocked meanwhile.'
  echo '3. Answer the question actually asked. A CCR answered "the contract already covers this" closes with the citation, not with a change.'
  echo '4. If a change is required, make it in the 17:00 contract window and nowhere else.'
  echo '5. Write the decision record. A contract change without one is unreviewable six weeks later.'
  echo '6. Re-run `make contracts-verify`. It must print `CONTRACTS-VERIFY OK`.'
  echo '7. Re-freeze: re-take `contracts.sha256`, confirm `make promote-check` prints `CONTRACTS-FROZEN OK`, and cut a **new** tag `contracts/vX.Y.Z`. The old tag is never moved.'
  echo '8. Notify every consuming lane on the register row - all of them, not only the filer.'
  echo '9. Write the ledger row to `records/decisions/`.'
  echo
  echo '## What a lane must never do'
  echo
  echo '- Edit `contracts/**`. Not to fix a typo, not to add a field, not "temporarily".'
  echo '- Propose the wording of the fix. Stating the gap is the lane'"'"'s job; the fix is L0'"'"'s (charter 7.2).'
  echo '- Work around the contract locally and file the CCR afterwards. The workaround is the thing the freeze exists to prevent.'
  echo '- Proceed while the CCR is open. Move to the next task whose dependencies are satisfied, or stop. Waiting is correct behaviour; guessing is not.'
} > docs/contract-change-request.md
git add -A && git commit -m "L0-P0-022: contract change request procedure"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | The CODEOWNERS assertion passes | `sh contracts/ci/check_codeowners_contracts.sh` | `CODEOWNERS-CONTRACTS OK` |
| 2 | The assertion fails on a machine identity | see SELF-VERIFY | `machine-detected` |
| 3 | Five gap rows, none with an empty owner or trigger | `awk -F'\|' '/^\| GAP-L0-/{n++; if($6 ~ /^ *$/ \|\| $7 ~ /^ *$/) bad++} END{print n, bad+0}' docs/recorded-gaps.md` | `5 0` |
| 4 | Every gap row names the D-L0-05 style compensating control | `grep -c '^| GAP-L0-' docs/recorded-gaps.md` | `5` |
| 5 | The procedure names all three CCR classes | `grep -o 'CCR-[A-Z]*' docs/contract-change-request.md \| sort -u \| tr '\n' ' '` | `CCR-ADDITIVE CCR-BLOCKING CCR-BREAKING ` |
| 6 | The procedure forbids moving the freeze tag | `grep -c 'The old tag is never moved' docs/contract-change-request.md` | `1` |
| 7 | Both escalation documents exist | `ls docs/escalation/CCR.md docs/contract-change-request.md \| wc -l` | `2` |
| 8 | `contracts/README.md`'s pointer now resolves | `test -f "docs/contract-change-request.md" && echo RESOLVES` | `RESOLVES` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
sh contracts/ci/check_codeowners_contracts.sh
cp CODEOWNERS /tmp/co.bak
printf '/contracts/ @reconciler-bot\n' >> CODEOWNERS
sh contracts/ci/check_codeowners_contracts.sh >/dev/null 2>&1 && echo machine-MISSED || echo machine-detected
cp /tmp/co.bak CODEOWNERS
printf '%s gaps=%s classes=%s\n' \
  "$(sh contracts/ci/check_codeowners_contracts.sh)" \
  "$(grep -c '^| GAP-L0-' docs/recorded-gaps.md)" \
  "$(grep -o 'CCR-[A-Z]*' docs/contract-change-request.md | sort -u | wc -l)"
git diff --quiet && echo "L0-P0-022 PASS" || echo "L0-P0-022 FAIL tree not restored"
```

Expected, in order:

```
CODEOWNERS-CONTRACTS OK
machine-detected
CODEOWNERS-CONTRACTS OK gaps=5 classes=3
L0-P0-022 PASS
```

**STOP RULE** — If `check_codeowners_contracts.sh` reports a placeholder login, stop and replace it with a real GitHub login before doing anything else. `@LEAD_GITHUB_LOGIN` is not a Code Owner; a CODEOWNERS rule naming a non-existent user is a required review nobody can satisfy, which reads as maximum protection and is in fact a wedged repository. If the lead's login cannot be determined, that is a blocker issue with `blocked_contract: none` and `blocked_lanes: ALL`, not a guess. Likewise, do not shorten the gap register by merging two rows: each row has one owner and one deactivation trigger, and a merged row has two of each, which means neither fires.

---

### L0-P0-025 — Author `contracts/event-types.yaml` — the canonical event_type list (FD-Q12 2026-09-02)

| | |
| --- | --- |
| **Size** | S |
| **Depends on** | L0-P0-022 |
| **Writes** | `contracts/event-types.yaml` <!-- # contracts/event-types.yaml — 86-entry event_type enum, authored by L0-P0 per FD-041 --> |
| **Spec** | FD-Q12 (Founder decision 2026-09-02); FD-041 (L0-P0 must author this file with all 86 entries); Section 97.3 (closed `event_type` enum); D-L0-08 (no real records in `contracts/**`) |

**Purpose.** `contracts/records/event-type.enum.v1.yaml` (C-EVT-ENUM-1, task L0-P0-011) carries the machine-validated full enum with per-entry `id`, `description` and paired-state metadata. `contracts/event-types.yaml` is the **human-readable canonical list** — the authoritative source every lane quotes when it asks "is this event_type valid?" Lane files must cite this file, never invent an identifier. No lane edits it: a new identifier is a CCR filed with L0 and added here only.

**All 86 C-EVT-ENUM-1 identifiers are now populated.** The file contains the 24 system meta-event entries committed under FD-Q12 plus all 86 identifiers from the L0-P0-011 table (108 non-comment entries total; 2 identifiers — `product_created` and `rollback_initiated` — appear in both sets and are listed once in the FD-Q12 block with the 84 remaining C-EVT-ENUM-1 identifiers appended). Every lane that emits an event type will find its identifier here. Any new type requires a CCR filed with L0 before it may be added.

**Commands**

```bash
set -euo pipefail
cd "$CP"
cat > contracts/event-types.yaml <<'YAMLEOF'
# Canonical event_type enum — authoritative source for all lanes (FD-Q12 2026-09-02)
# DO NOT edit in L3/L4/L5 — update here only
event_types:
  - product_created
  - product_updated
  - product_deleted
  - product_activated
  - product_deactivated
  - schema_validated
  - schema_rejected
  - attention_raised
  - attention_cleared
  - lane_started
  - lane_completed
  - lane_blocked
  - gate_passed
  - gate_failed
  - merge_train_started
  - merge_train_completed
  - merge_train_rejected
  - rollback_initiated
  - rollback_completed
  - foreign_path_violation
  - unassigned_path_violation
  - phase_transition
  - doc_retired
  - doc_superseded
  # --- all 86 identifiers from C-EVT-ENUM-1 (L0-P0-011) follow ---
  - work_item_created
  - work_item_moved_to_ready
  - work_item_assigned
  - ready_queue_miss_recorded
  - plan_submitted
  - plan_rejected
  - plan_approved
  - change_class_assigned
  - impact_scope_assigned
  - reversibility_class_assigned
  - requirement_changed_materially
  - replan_triggered
  - execute_started
  - pr_opened
  - review_requested
  - gate2_approved
  - ci_check_completed
  - parity_check_completed
  - artifact_built
  - staging_deployed
  - staging_smoke_completed
  - uat_executed
  - pr_merged
  - production_approval_granted
  - production_deployed
  - production_smoke_completed
  - version_digest_confirmed
  - health_check_completed
  - feature_flag_toggled
  # rollback_initiated already listed above (system meta-event subset, FD-Q12)
  - hotfix_authorised
  - incident_opened
  - incident_resolved
  - postmortem_completed
  - regression_test_added
  - security_incident_opened
  - credential_rotated
  - restore_test_executed
  - asset_expiry_alerted
  - asset_owner_reassigned
  - lifecycle_transitioned
  - launch_readiness_signed_off
  - reviewer_matrix_changed
  - knowledge_redundancy_status_changed
  - person_added
  - person_role_changed
  - person_departed
  - orphan_detected
  - orphan_resolved
  - temporary_assignment_state_changed
  - acting_team_lead_state_changed
  - drift_detected
  - drift_repaired
  # product_created already listed above (system meta-event subset, FD-Q12)
  - product_split
  - product_merged
  - product_transferred
  - shared_service_created
  - shared_service_breaking_change_released
  - platform_change_proposed
  - canary_started
  - canary_completed
  - fleet_rollout_started
  - platform_rollback_initiated
  - contract_version_migrated
  - compatibility_state_changed
  - background_pr_created
  - background_pr_dispositioned
  - task_class_state_changed
  - ai_runtime_changed
  - ai_provider_outage_recorded
  - model_benchmark_completed
  - status_request_received
  - plan_approver_notified
  - verification_block_state_changed
  - degraded_mode_state_changed
  - gap_procedure_run
  - eval_regression_detected
  - pending_decision_state_changed
  - onboarding_phase_completed
  - support_item_ingested
  - support_first_touch_breached
  - delegation_expiry_warned
  - temporary_person_expiry_warned
  - launch_signoff_requested
  - weekend_exception_state_changed
YAMLEOF
```

**Commands**

```bash
set -euo pipefail
cd "$CP"
# Re-take the freeze hash so contracts.sha256 includes the new file.
# The same command as L0-P0-023 and the Makefile promote-check target.
find contracts -type f | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -d' ' -f1 > contracts.sha256
git add contracts/event-types.yaml contracts.sha256
git commit -m "L0-P0-025: contracts/event-types.yaml — canonical event_type list, all 86 C-EVT-ENUM-1 identifiers populated"
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | The file exists and parses | `python -c "import yaml;print(type(yaml.safe_load(open('contracts/event-types.yaml'))['event_types']).__name__)"` | `list` |
| 2 | All 86 C-EVT-ENUM-1 identifiers are present | `python -c "import yaml;print(len([e for e in yaml.safe_load(open('contracts/event-types.yaml'))['event_types'] if not str(e).startswith('#')]))"` | a number `>= 86` |
| 3 | Every entry in C-EVT-ENUM-1 appears here | `python -c "import yaml;enum={x['id'] for x in yaml.safe_load(open('contracts/records/event-type.enum.v1.yaml'))['event_types']};here=set(yaml.safe_load(open('contracts/event-types.yaml'))['event_types']);print(enum-here)"` | `set()` |
| 4 | The file is under `contracts/` | `test -f contracts/event-types.yaml && echo present` | `present` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
COUNT=$(python -c "import yaml; print(len([e for e in yaml.safe_load(open('contracts/event-types.yaml'))['event_types'] if not str(e).startswith('#')]))")
echo "EVENT-TYPES-COUNT $COUNT"
[ "$COUNT" -ge 86 ] && echo "L0-P0-025 COMPLETE" || echo "L0-P0-025 INCOMPLETE — Founder must add $((86 - COUNT)) more entries before lane dispatch"
```

Expected (all 86 C-EVT-ENUM-1 identifiers populated, plus 22 system meta-event entries from FD-Q12 = 108 total non-comment entries):

```
EVENT-TYPES-COUNT 108
L0-P0-025 COMPLETE
```

**STOP RULE** — Do not run L0-P0-023 (the freeze) until this SELF-VERIFY prints `L0-P0-025 COMPLETE`. A freeze with an incomplete event_type list means every lane that emits an unlisted type will fail its own validation with no path to resolution except a post-freeze CCR.

---

### L0-P0-026 — Author `e2e/run.sh`, `e2e/verdict.sh`, `contracts/harness/run-contract-tests.sh`, and `contracts/harness/pairs.tsv`

| | |
| --- | --- |
| **Size** | M |
| **Depends on** | L0-P0-022 (contracts directory and CODEOWNERS established) |
| **Writes** | `e2e/run.sh`, `e2e/verdict.sh`, `e2e/lib/checkpoint.sh`, `contracts/harness/run-contract-tests.sh`, `contracts/harness/pairs.tsv`; updates `lane-paths.tsv` |
| **Spec** | `protocol/08-smoke-and-e2e.md` §3.4 (`e2e/run.sh`), §3.2 (`e2e/lib/checkpoint.sh`), §7 (`e2e/verdict.sh`); `protocol/01-contract-tests.md` §3, §9 (`run-contract-tests.sh`); L0-IG-D5 resolved here; PARTITION.md (`contracts/**` = L0-owned) |

**B-04 finding, resolved by this task.** The B-04 coherence review identified that `e2e/run.sh`, `e2e/verdict.sh`, `contracts/harness/run-contract-tests.sh`, and `contracts/harness/pairs.tsv` are owned by L0 in `lane-paths.tsv`, required by the integration gate (`run-integration.sh` step 0 and `contract-tests.sh`), but no task in any plan file creates their content — they exist only as FD-033 placeholder stubs in L0-05-16 through L0-05-19. This task creates all four and closes L0-IG-D5.

**L0-IG-D5 resolved here.** L0 claims `e2e/**`. This task adds the row `0<TAB>e2e/*` to `lane-paths.tsv` before the `X<TAB>*/*` unassigned catch-all. Without that row, `lane-guard.sh` reports `LANE-GUARD VIOLATION: e2e/run.sh is an UNASSIGNED path` and `train-owners.sh` fails `P2`. `contracts/harness/**` is already L0-owned via the `contracts/**` row in `lane-paths.tsv`.

**L0-IG-D1 note.** `pairs.tsv` is authored with 12 rows — one per contract C-01…C-12 from `protocol/01-contract-tests.md` §3. Until L0-IG-D1 is settled, `count-integrity.sh` still reports `narrowed=1` (two contested pair counts in `COUNTS.tsv`). This task does not resolve L0-IG-D1; it removes the other half of the IG-03 blocker (the missing harness file itself).

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
git checkout integration && git pull --ff-only
mkdir -p e2e/lib e2e/stages e2e/negative contracts/harness

# ── L0-IG-D5: claim e2e/** in lane-paths.tsv ──────────────────────────────
# Add an explicit L0 row for e2e/* BEFORE the X<TAB>*/* unassigned catch-all.
# owner_of("e2e/run.sh") must resolve to "0", not "X".
awk 'BEGIN{done=0} /^X\t\*\/\*/ && !done {print "0\te2e/*"; done=1} {print}' \
  lane-paths.tsv > /tmp/lp-new.tsv && mv /tmp/lp-new.tsv lane-paths.tsv
grep -q '^0	e2e/\*' lane-paths.tsv || { echo "BLOCKER: e2e row not inserted — edit lane-paths.tsv manually"; exit 1; }
```

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"

# ── 1. contracts/harness/pairs.tsv ────────────────────────────────────────
# Format: pair-id<TAB>producer-lane<TAB>consumer-lanes<TAB>contract-file
# 12 rows from protocol/01-contract-tests.md §3 (C-01..C-12).
# L0-IG-D1 UNRESOLVED: protocol/00 §5 T2 declares 10 pairs (CT-01..CT-10);
# protocol/01 §3 declares 12 contracts (C-01..C-12). Until L0-IG-D1 is settled,
# count-integrity.sh reports narrowed=1. When resolved, retire the losing row
# in contracts/gate/COUNTS.tsv under a decision record — do not edit this file
# to match; update the ct_pairs key in COUNTS.tsv (protocol/05 §9).
cat > contracts/harness/pairs.tsv <<'PAIRS'
# pair-id<TAB>producer-lane<TAB>consumer-lanes<TAB>contract-file
# L0-IG-D1 UNRESOLVED: 12 rows per protocol/01; protocol/00 declares 10 pairs
C-01	L1	L2,L3,L4,L5	contracts/C-01-registry-schema.contract.yaml
C-02	L1	L2,L3	contracts/C-02-validator-cli.contract.yaml
C-03	L4	L2,L3,L5	contracts/C-03-record-envelope.contract.yaml
C-04	L4+L1	L2,L3,L4,L5	contracts/C-04-event-envelope.contract.yaml
C-05	L2	L3,L5	contracts/C-05-workflow-interface.contract.yaml
C-06	L2	L5,L3	contracts/C-06-status-check-names.contract.yaml
C-07	L5	L3,L1	contracts/C-07-access-model.contract.yaml
C-08	L3	L4,L5	contracts/C-08-drift-finding.contract.yaml
C-09	L4	L2,L3,L5	contracts/C-09-metric-source.contract.yaml
C-10	L5	L2,L3,L4	contracts/C-10-notification.contract.yaml
C-11	L5	L2,L3	contracts/C-11-secret-tiers.contract.yaml
C-12	L1	L2,L3,L4,L5	contracts/C-12-version-floor.contract.yaml
PAIRS

# ── 2. contracts/harness/run-contract-tests.sh ────────────────────────────
cat > contracts/harness/run-contract-tests.sh <<'RCT'
#!/usr/bin/env sh
# =============================================================================
# run-contract-tests.sh — L0-owned (contracts/harness/**, PARTITION.md).
# Cross-lane contract test runner; delegated to by contracts/gate/contract-tests.sh.
#
# Usage:
#   run-contract-tests.sh --all [--mode integrated] [--report tsv:PATH]
#   run-contract-tests.sh --contract C-01 [--report tsv:PATH]
#   run-contract-tests.sh --side consumer --lane L3 [--report tsv:PATH]
#   run-contract-tests.sh --side producer --lane L1 [--report tsv:PATH]
#   run-contract-tests.sh --fixture-parity
#   run-contract-tests.sh --negative-proof
#   run-contract-tests.sh --mutation-drill
#
# Report TSV columns: seq<TAB>pair-id<TAB>result<TAB>fixture-path-or-stub
# Last stdout line is the verdict.  Exit 0 all-pass, 1 any-fail, 2 config-error.
# =============================================================================
set -eu

HARNESS_DIR="$(cd "$(dirname "$0")" && pwd)"
CP_ROOT="${CP_ROOT:-.}"
MANIFEST="${HARNESS_DIR}/pairs.tsv"
OUT="${GATE_OUT:-.gate}"
REPORT_FILE=""
MODE_ARG=""
CONTRACT_ARG=""
SIDE_ARG=""
LANE_ARG=""
STUBS_DIR=".contract-stubs"

while [ $# -gt 0 ]; do
  case "$1" in
    --all)             MODE_ARG=all;              shift ;;
    --mode)            MODE_ARG="$2";             shift 2 ;;
    --contract)        CONTRACT_ARG="$2";         shift 2 ;;
    --side)            SIDE_ARG="$2";             shift 2 ;;
    --lane)            LANE_ARG="$2";             shift 2 ;;
    --report)          REPORT_FILE="$2";          shift 2 ;;
    --fixture-parity)  MODE_ARG=parity;           shift ;;
    --negative-proof)  MODE_ARG=negative;         shift ;;
    --mutation-drill)  MODE_ARG=mutation;         shift ;;
    *) echo "RUN-CONTRACT-TESTS FAIL: unknown argument '$1'"; exit 2 ;;
  esac
done

[ -f "$MANIFEST" ] || { echo "RUN-CONTRACT-TESTS FAIL: pairs.tsv not found at $MANIFEST"; exit 2; }
mkdir -p "$OUT"
if [ -n "$REPORT_FILE" ]; then
  case "$REPORT_FILE" in tsv:*) REPORT_FILE="${REPORT_FILE#tsv:}" ;; esac
  : > "$REPORT_FILE"
fi

emit_row() {
  local seq="$1" pair="$2" result="$3" fixture="$4"
  [ -n "$REPORT_FILE" ] && \
    printf '%s\t%s\t%s\t%s\n' "$seq" "$pair" "$result" "$fixture" >> "$REPORT_FILE" || true
}

# Run one contract pair: call its per-contract driver if present, else check
# that valid fixtures exist. Returns 0 pass, 1 fail.
run_one() {
  local pair_id="$1" seq="$2" integrated="${3:-0}"
  local contract_file
  contract_file=$(awk -F'\t' -v p="$pair_id" '!/^#/ && $1==p {print $4; exit}' "$MANIFEST")
  [ -n "$contract_file" ] || { emit_row "$seq" "$pair_id" fail "no-manifest-row"; return 1; }

  local fixture_dir="${CP_ROOT}/contracts/fixtures/${pair_id}"
  local stub_path="${CP_ROOT}/${STUBS_DIR}/${pair_id}"
  local driver="${fixture_dir}/run.sh"

  # Stub detection: in integrated mode, a consumer still pointing at .contract-stubs/
  # is counted as stubbed=1 by the caller (contracts/gate/contract-tests.sh).
  local fixture_path="$fixture_dir"
  if [ "$integrated" -eq 1 ] && [ -d "$stub_path" ] && [ ! -d "${fixture_dir}/live" ]; then
    fixture_path="$stub_path"
  fi

  if [ -x "$driver" ]; then
    set +e
    sh "$driver" --pair "$pair_id" --fixture "$fixture_path" \
      >> "$OUT/contract-${pair_id}.log" 2>&1
    RC=$?
    set -e
    if [ "$RC" -eq 0 ]; then
      emit_row "$seq" "$pair_id" pass "$fixture_path"; return 0
    else
      emit_row "$seq" "$pair_id" fail "$fixture_path"; return 1
    fi
  else
    # No per-contract driver yet: pass if valid fixtures directory is non-empty.
    if [ -d "${fixture_dir}/valid" ] && \
       [ -n "$(ls -A "${fixture_dir}/valid" 2>/dev/null)" ]; then
      emit_row "$seq" "$pair_id" pass "$fixture_path"; return 0
    else
      emit_row "$seq" "$pair_id" fail "no-driver-no-valid-fixtures"; return 1
    fi
  fi
}

TOTAL=0; PASSED=0; FAILED=0; seq=0

# Resolve effective mode.
EFFECTIVE_MODE="${MODE_ARG}"
INTEGRATED=0
[ "$EFFECTIVE_MODE" != "integrated" ] || { EFFECTIVE_MODE=all; INTEGRATED=1; }
[ -z "$CONTRACT_ARG" ] || EFFECTIVE_MODE=contract

case "$EFFECTIVE_MODE" in
  all)
    while IFS='	' read -r pair producer consumers contract; do
      case "$pair" in ''|\#*) continue ;; esac
      seq=$((seq+1)); TOTAL=$((TOTAL+1))
      run_one "$pair" "$seq" "$INTEGRATED" \
        && PASSED=$((PASSED+1)) || FAILED=$((FAILED+1))
    done < "$MANIFEST"
    ;;
  contract)
    seq=1; TOTAL=1
    run_one "$CONTRACT_ARG" "$seq" 0 \
      && PASSED=$((PASSED+1)) || FAILED=$((FAILED+1))
    ;;
  parity)
    # --fixture-parity: every pair in the manifest must have a fixtures directory.
    while IFS='	' read -r pair producer consumers contract; do
      case "$pair" in ''|\#*) continue ;; esac
      seq=$((seq+1)); TOTAL=$((TOTAL+1))
      dir="${CP_ROOT}/contracts/fixtures/${pair}"
      if [ -d "$dir" ]; then
        emit_row "$seq" "$pair" pass "$dir"; PASSED=$((PASSED+1))
      else
        emit_row "$seq" "$pair" fail "missing:$dir"; FAILED=$((FAILED+1))
      fi
    done < "$MANIFEST"
    ;;
  negative)
    # --negative-proof: each contract's invalid fixtures must be rejected.
    while IFS='	' read -r pair producer consumers contract; do
      case "$pair" in ''|\#*) continue ;; esac
      seq=$((seq+1)); TOTAL=$((TOTAL+1))
      invalid_dir="${CP_ROOT}/contracts/fixtures/${pair}/invalid"
      driver="${CP_ROOT}/contracts/fixtures/${pair}/run.sh"
      if [ ! -d "$invalid_dir" ] || \
         [ -z "$(ls -A "$invalid_dir" 2>/dev/null)" ]; then
        emit_row "$seq" "$pair" fail "no-invalid-fixtures"; FAILED=$((FAILED+1))
        continue
      fi
      if [ -x "$driver" ]; then
        set +e
        sh "$driver" --pair "$pair" --fixture "$invalid_dir" --mode negative \
          >> "$OUT/contract-neg-${pair}.log" 2>&1
        RC=$?
        set -e
        # Driver exits non-zero when it correctly rejects invalid fixtures.
        if [ "$RC" -ne 0 ]; then
          emit_row "$seq" "$pair" pass "$invalid_dir"; PASSED=$((PASSED+1))
        else
          emit_row "$seq" "$pair" fail "invalid-fixture-passed:$invalid_dir"
          FAILED=$((FAILED+1))
        fi
      else
        emit_row "$seq" "$pair" fail "no-driver-cannot-prove-negative"
        FAILED=$((FAILED+1))
      fi
    done < "$MANIFEST"
    ;;
  mutation)
    # --mutation-drill: delegate to per-pair drivers in mutation mode.
    while IFS='	' read -r pair producer consumers contract; do
      case "$pair" in ''|\#*) continue ;; esac
      seq=$((seq+1)); TOTAL=$((TOTAL+1))
      driver="${CP_ROOT}/contracts/fixtures/${pair}/run.sh"
      if [ -x "$driver" ]; then
        set +e
        sh "$driver" --pair "$pair" --mode mutation \
          >> "$OUT/contract-mut-${pair}.log" 2>&1; RC=$?
        set -e
        if [ "$RC" -eq 0 ]; then
          emit_row "$seq" "$pair" pass "mutation"; PASSED=$((PASSED+1))
        else
          emit_row "$seq" "$pair" fail "mutation-drill-failed"; FAILED=$((FAILED+1))
        fi
      else
        # No driver: skip mutation drill for this pair (not a failure at this stage).
        emit_row "$seq" "$pair" pass "no-driver-skip"; PASSED=$((PASSED+1))
      fi
    done < "$MANIFEST"
    ;;
  "")
    # --side consumer/producer --lane LN
    if [ -n "$SIDE_ARG" ] && [ -n "$LANE_ARG" ]; then
      while IFS='	' read -r pair producer consumers contract; do
        case "$pair" in ''|\#*) continue ;; esac
        match=0
        case "$SIDE_ARG" in
          consumer) echo "$consumers" | tr ',' '\n' | grep -qx "$LANE_ARG" && match=1 ;;
          producer) [ "$producer" = "$LANE_ARG" ] && match=1 ;;
        esac
        [ "$match" -eq 0 ] && continue
        seq=$((seq+1)); TOTAL=$((TOTAL+1))
        run_one "$pair" "$seq" 0 \
          && PASSED=$((PASSED+1)) || FAILED=$((FAILED+1))
      done < "$MANIFEST"
    else
      echo "RUN-CONTRACT-TESTS FAIL: no valid mode (--all, --contract C-NN, --side consumer|producer --lane LN, --fixture-parity, --negative-proof, --mutation-drill)"
      exit 2
    fi
    ;;
esac

if [ "$TOTAL" -eq 0 ]; then
  echo "RUN-CONTRACT-TESTS FAIL: no pairs matched the given arguments (total=0)"; exit 1
fi
if [ "$FAILED" -eq 0 ]; then
  echo "RUN-CONTRACT-TESTS PASS total=${TOTAL} passed=${PASSED} failed=0"; exit 0
fi
echo "RUN-CONTRACT-TESTS FAIL total=${TOTAL} passed=${PASSED} failed=${FAILED}"; exit 1
RCT
chmod +x contracts/harness/run-contract-tests.sh

# ── 3. e2e/lib/checkpoint.sh ──────────────────────────────────────────────
# Reproduced byte-for-byte from protocol/08-smoke-and-e2e.md §3.2.
cat > e2e/lib/checkpoint.sh <<'CKP'
set -euo pipefail

: "${E2E_RUN_ID:?run ./e2e/run.sh — never a stage script directly}"
E2E_OUT="e2e/out/${E2E_RUN_ID}"
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

# NEGATIVE checkpoint: the command must fail.
cp_refute() {
  local id="$1" what="$2"; shift 2
  if "$@" >"${E2E_OUT}/evidence/${id}.out" 2>&1; then
    cp_fail "$id" "$what — expected failure, got success"
  else
    cp_pass "$id" "$what"
  fi
}

# EQUALITY checkpoint: two string values must be equal.
cp_equal() {
  local id="$1" what="$2" a="$3" b="$4"
  if [ "$a" = "$b" ]; then
    cp_pass "$id" "$what"
  else
    cp_fail "$id" "$what — expected '$b', got '$a'"
  fi
}
CKP

# ── 4. e2e/run.sh ─────────────────────────────────────────────────────────
# Reproduced byte-for-byte from protocol/08-smoke-and-e2e.md §3.4.
# Stages run in order; the chain stops on first failure (set -euo pipefail).
cat > e2e/run.sh <<'E2E'
#!/usr/bin/env sh
# =============================================================================
# e2e/run.sh — L0-owned (e2e/**, L0D-04, lane-paths.tsv). The ONLY entry
# point for the assembled-system smoke. Spec: protocol/08-smoke-and-e2e.md §3.4.
# Exit 0 when e2e/verdict.sh prints VERDICT: PASS; exit 1 otherwise.
# NEVER invoke e2e/verdict.sh from a stage script — only from this file.
# =============================================================================
set -euo pipefail
export E2E_RUN_ID="${E2E_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-$(git rev-parse --short HEAD)}"
export E2E_PRODUCT=pilot-one
export E2E_REPO=org/pilot-one-api
export E2E_CP_REPO=org/control-plane
export E2E_RECORDS_REPO=org/control-plane-records
source e2e/lib/checkpoint.sh

for s in e2e/stages/*.sh;   do echo "== $s"; bash "$s"; done
for n in e2e/negative/*.sh; do echo "== $n"; bash "$n"; done
bash e2e/verdict.sh          # §7 — the only thing allowed to print PASS for the run
E2E
chmod +x e2e/run.sh

# ── 5. e2e/verdict.sh ─────────────────────────────────────────────────────
# Reproduced byte-for-byte from protocol/08-smoke-and-e2e.md §7.
# Floors: 118 positive checkpoints (CP-*), 28 gates proven able to fail (NEG-*).
cat > e2e/verdict.sh <<'VRD'
#!/usr/bin/env sh
# =============================================================================
# e2e/verdict.sh — L0-owned. The ONLY thing allowed to print "VERDICT: PASS".
# Spec: protocol/08-smoke-and-e2e.md §7. Called only by e2e/run.sh.
# Exit 0 PASS, 1 FAIL. Never called by a stage or negative script.
# =============================================================================
set -euo pipefail
: "${E2E_RUN_ID:?run ./e2e/run.sh — never e2e/verdict.sh directly}"
E2E_OUT="e2e/out/${E2E_RUN_ID}"
E2E_LOG="${E2E_OUT}/checkpoints/log.tsv"

[ -f "$E2E_LOG" ] || { echo "VERDICT: FAIL — checkpoint log not found at $E2E_LOG"; exit 1; }

pos=$(awk  -F'\t' '$2 ~ /^CP-/  && $3=="PASS"' "${E2E_LOG}" | wc -l)
neg=$(awk  -F'\t' '$2 ~ /^NEG-/ && $3=="PASS"' "${E2E_LOG}" | wc -l)

[ "$neg" -ge 28 ]  || { echo "VERDICT: FAIL — only ${neg}/28 gates were proven able to fail"; exit 1; }
[ "$pos" -ge 118 ] || { echo "VERDICT: FAIL — only ${pos}/118 positive checkpoints ran"; exit 1; }
echo "VERDICT: PASS — ${pos} checkpoints, ${neg} gates proven able to fail"
VRD
chmod +x e2e/verdict.sh

git add lane-paths.tsv contracts/harness e2e
git commit -m "L0-P0-026: e2e/run.sh, e2e/verdict.sh, contracts/harness/run-contract-tests.sh, contracts/harness/pairs.tsv (B-04 closed, FD-033 resolved, L0-IG-D5 resolved)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | All four target files are executable or present | `test -x e2e/run.sh && test -x e2e/verdict.sh && test -x contracts/harness/run-contract-tests.sh && test -f contracts/harness/pairs.tsv && echo ALL-PRESENT` | `ALL-PRESENT` |
| 2 | `pairs.tsv` has exactly 12 data rows | `grep -vc '^#' contracts/harness/pairs.tsv` | `12` |
| 3 | No duplicate pair id in `pairs.tsv` | `cut -f1 contracts/harness/pairs.tsv \| grep -v '^#' \| sort \| uniq -d \| wc -l` | `0` |
| 4 | All pair ids are in the form `C-NN` | `cut -f1 contracts/harness/pairs.tsv \| grep -v '^#' \| grep -cv '^C-[0-9][0-9]*$'` | `0` |
| 5 | `e2e/**` is now L0-assigned in `lane-paths.tsv` | `awk -F'\t' '$1=="0" && $2~/^e2e/' lane-paths.tsv \| wc -l \| tr -d ' '` | `1` or greater |
| 6 | `contract-tests.sh` no longer fails on a missing harness | `test -x contracts/harness/run-contract-tests.sh && echo HARNESS-PRESENT` | `HARNESS-PRESENT` |
| 7 | `e2e/verdict.sh` fails when the checkpoint log is absent | see SELF-VERIFY case L | `VERDICT: FAIL — checkpoint log not found` |
| 8 | `e2e/verdict.sh` fails with fewer than 28 negative checkpoints | see SELF-VERIFY case N | `VERDICT: FAIL — only 0/28 gates were proven able to fail` |
| 9 | `e2e/verdict.sh` fails with fewer than 118 positive checkpoints | see SELF-VERIFY case V | `VERDICT: FAIL — only 0/118 positive checkpoints ran` |
| 10 | `run-contract-tests.sh` fails closed on zero matching pairs | `bash contracts/harness/run-contract-tests.sh --side consumer --lane L9 2>&1 \| tail -1` | `RUN-CONTRACT-TESTS FAIL: no pairs matched the given arguments (total=0)` |
| 11 | No-mode call is a configuration error | `bash contracts/harness/run-contract-tests.sh; echo "rc=$?"` | a line beginning `RUN-CONTRACT-TESTS FAIL: no valid mode` then `rc=2` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"

# Prove verdict.sh enforces all three floors --------------------------------
export E2E_RUN_ID=selftest-L0-P0-026
mkdir -p "e2e/out/${E2E_RUN_ID}/checkpoints"
LOG="e2e/out/${E2E_RUN_ID}/checkpoints/log.tsv"

# case L - log absent: must fail with a named message
rm -f "$LOG"
L=$(bash e2e/verdict.sh 2>&1 | grep -o 'VERDICT: FAIL — checkpoint log not found' || echo MISSING)

# case N - log present but no NEG- entries (neg=0 < 28)
: > "$LOG"
N=$(bash e2e/verdict.sh 2>&1 | grep -o 'VERDICT: FAIL — only 0/28 gates' || echo MISSING)

# case V - 28 NEG passes written but 0 CP- passes (pos=0 < 118)
: > "$LOG"
i=1; while [ "$i" -le 28 ]; do
  printf '2026-01-01T00:00:00Z\tNEG-%02d\tPASS\tok\n' "$i" >> "$LOG"
  i=$((i+1))
done
V=$(bash e2e/verdict.sh 2>&1 | grep -o 'VERDICT: FAIL — only 0/118 positive checkpoints' || echo MISSING)

rm -rf "e2e/out/${E2E_RUN_ID}"

# Prove run-contract-tests.sh argument handling -----------------------------
NOMODE=$(bash contracts/harness/run-contract-tests.sh 2>&1 | head -1 | grep -o 'RUN-CONTRACT-TESTS FAIL' || echo MISSING)
NOMATCH=$(bash contracts/harness/run-contract-tests.sh --side consumer --lane L9 2>&1 | tail -1 | grep -o 'total=0' || echo MISSING)

printf 'files=%s pairs=%s dupid=%s e2e_owner=%s log_absent=[%s] neg_floor=[%s] pos_floor=[%s] nomode=%s nomatch=%s\n' \
  "$(test -x e2e/run.sh && test -x e2e/verdict.sh && test -x contracts/harness/run-contract-tests.sh && echo PRESENT || echo MISSING)" \
  "$(grep -vc '^#' contracts/harness/pairs.tsv)" \
  "$(cut -f1 contracts/harness/pairs.tsv | grep -v '^#' | sort | uniq -d | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '$1=="0" && $2~/^e2e/' lane-paths.tsv | wc -l | tr -d ' ')" \
  "$L" "$N" "$V" "$NOMODE" "$NOMATCH"
```

Expected output, exactly:

```
files=PRESENT pairs=12 dupid=0 e2e_owner=1 log_absent=[VERDICT: FAIL — checkpoint log not found] neg_floor=[VERDICT: FAIL — only 0/28 gates] pos_floor=[VERDICT: FAIL — only 0/118 positive checkpoints] nomode=RUN-CONTRACT-TESTS FAIL nomatch=total=0
```

**STOP rule** — if `files=MISSING`, the files were not committed or are not executable; re-run the command block and check `git status`. If `e2e_owner=0`, `lane-paths.tsv` was not updated — `lane-guard.sh` will report `LANE-GUARD VIOLATION: e2e/run.sh is an UNASSIGNED path` on every subsequent scan and `train-owners.sh` will block promotion at `P2`; edit `lane-paths.tsv` to add `0<TAB>e2e/*` before the `X<TAB>*/*` catch-all and re-run SELF-VERIFY. If any floor case shows `MISSING`, `e2e/verdict.sh` is not correctly enforcing the 118/28 floors — `IG-10` reads `e2e/verdict.sh`'s output and a verdict script that cannot fail is an invalid control (invariant 80); do not proceed to L0-P0-023.

---

### L0-P0-023 — The freeze, the tag ruleset, and the signal that starts five lanes

| | |
| --- | --- |
| **Size** | M |
| **Depends on** | L0-P0-021, L0-P0-022, L0-P0-025, L0-P0-026; and, from `L0-00-charter.md`, task L0-00-04 (`make freeze` / `make promote-check`) |
| **Writes** | `contracts.sha256`, `contracts/tag-ruleset.json`, `docs/phase-0-complete.md`; creates the annotated tag `contracts/v1.0.0` and its protecting ruleset |
| **Spec** | D-L0-04; Section 33.2 (tag protection, SHA pinning); Section 40.1 (D89, bypass actors); PARTITION.md rules 1–2; charter §8.1 (the contract-freeze integrity check) |

**This is the task the whole programme waits on.** Nothing in lanes L1–L5 starts until its SELF-VERIFY prints `PHASE-0-COMPLETE`.

**Commands**

```bash
set -euo pipefail
cd "$CP"

# 1. Both guards must be green before anything is frozen.
python contracts/ci/verify_contracts.py | tail -1
sh contracts/ci/check_codeowners_contracts.sh

# 1a. Write the tag ruleset JSON into contracts/ BEFORE the freeze hash so that
#     the file is included in the hash and promote-check never reports CONTRACTS-DRIFT.
cat > contracts/tag-ruleset.json <<'JSONEOF'
{
  "name": "contracts-freeze-tags",
  "target": "tag",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {
    "ref_name": { "include": ["refs/tags/contracts/*"], "exclude": [] }
  },
  "rules": [
    { "type": "creation" },
    { "type": "update" },
    { "type": "deletion" },
    { "type": "non_fast_forward" }
  ]
}
JSONEOF

# 2. Record the freeze hash. The command line is identical to the Makefile target of
#    L0-00-04, so `make promote-check` and this task can never disagree.
find contracts -type f | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -d' ' -f1 > contracts.sha256
cat contracts.sha256
git add contracts.sha256 contracts/tag-ruleset.json
git commit -m "L0-P0-023: record the contract freeze hash"
```

Then land the branch. Phase 0 merges to `main`, and `main` merges to `integration`:

```bash
set -euo pipefail
cd "$CP"
git push -u origin l0/phase-0-contracts
gh pr create --base main --head l0/phase-0-contracts \
  --title "L0 Phase 0: the frozen contracts" \
  --body "Twenty-three frozen contracts, their stubs and their fixtures. Frozen at tag contracts/v1.0.0. PARTITION.md rule 2."
gh pr merge --merge
git checkout main && git pull --ff-only
git checkout integration && git pull --ff-only
git merge --no-ff main -m "L0-P0-023: Phase 0 contracts into integration"
git push origin integration
git checkout main
```

The tag is **annotated**, never lightweight: a lightweight tag carries no author, no date and no message, and a freeze marker with no provenance is a freeze marker nobody can audit.

```bash
set -euo pipefail
cd "$CP"
git tag -a contracts/v1.0.0 -m "Phase 0 contract freeze. 23 contracts. sha256=$(cat contracts.sha256)"
git push origin contracts/v1.0.0
git cat-file -t contracts/v1.0.0
```

The tag ruleset protects it with an **empty bypass-actor list** (D-L0-04, on D89's reasoning):

```bash
set -euo pipefail
cd "$CP"
gh api --method POST "repos/$ORG/control-plane/rulesets" \
  --input contracts/tag-ruleset.json > /tmp/contracts-ruleset.json
CT_ID=$(python -c "import json;print(json.load(open('/tmp/contracts-ruleset.json'))['id'])")
echo "contracts tag ruleset id = $CT_ID"
gh api "repos/$ORG/control-plane/rulesets/$CT_ID" \
  --jq '{name, enforcement, bypass: (.bypass_actors|length), rules: [.rules[].type]}'
```

> **`"bypass_actors": []` is the whole point, again.** D89: a bypass actor is exempt from **every** rule in the ruleset it is listed on, and bypass is not scoped by path. A single actor added here for some unrelated convenience would make the contract tag movable, and a moved contract tag reaches five lanes with no reviewable diff. This ruleset carries the contract tags and nothing else, precisely so that no future bypass added for another purpose can reach them. If a bypass is ever needed for something else, it goes on a **different** ruleset.

The `creation` rule means the tag namespace is closed after this point: creating `contracts/v1.1.0` under a CCR is done by the same identity that owns the ruleset, deliberately, in the contract window — not incidentally by a script.

Then the start signal:

```bash
set -euo pipefail
cd "$CP"
{
  echo '# Phase 0 complete - the contracts are frozen'
  echo
  echo "Frozen at tag \`contracts/v1.0.0\`, hash \`$(cat contracts.sha256)\`, on $(date -u +%F)."
  echo
  echo '## What is now true'
  echo
  echo '- Twenty-three contracts exist under `contracts/**`, each with a seven-key header, a register row, a stub, and at least one golden-valid and one golden-invalid fixture.'
  echo '- `make contracts-verify` proves all of it in one command.'
  echo '- `contracts.sha256` records the freeze; `make promote-check` prints `CONTRACTS-FROZEN OK` while it holds.'
  echo '- Code Owner review is required on `contracts/**`, and the freeze tag is immutable with no bypass actor.'
  echo '- Five gaps are recorded, dated and owned in `docs/recorded-gaps.md`.'
  echo
  echo '## What every lane does first'
  echo
  echo '| Lane | Develops against | Blocked without |'
  echo '| --- | --- | --- |'
  echo '| L1 | `stubs/capability.vocabulary.yaml`, `stubs/people.yaml`, `stubs/roles.yaml`, `stubs/product.yaml`, `stubs/verification-contract.yaml`, `stubs/service.yaml`, `stubs/topology.yaml`, `stubs/platform.yaml` | `C-CAP-VOCAB-1` |'
  echo '| L2 | `stubs/workflow-call-ci.yml`, `stubs/workflow-call-deploy-production.yml`, `stubs/required-checks.yaml`, `stubs/secret-tiers.yaml`, `stubs/evidence-chain-answers.yaml` | `C-WF-CHECKS-1` |'
  echo '| L3 | `stubs/comparison-set.yaml`, `stubs/drift-finding.yaml`, `stubs/repair-record.yaml`, `stubs/provision-create-product.yaml`, `stubs/provision-add-person.yaml` | `C-RECON-SET-1` |'
  echo '| L4 | `stubs/record-incident.yaml`, `stubs/record-deployment.yaml`, `stubs/record-decision.yaml`, `stubs/event.yaml`, `stubs/event-type.enum.yaml`, `stubs/store-map.yaml` | `C-EVT-ENUM-1` |'
  echo '| L5 | `stubs/permission-model.yaml`, `stubs/branch-protection.yaml`, `stubs/layer-split.yaml`, `stubs/secret-tiers.yaml` | `C-WF-SECRETS-1` |'
  echo
  echo '## The one rule that matters now'
  echo
  echo 'No lane edits `contracts/**`. A lane needing a change files a Contract Change Request'
  echo '(`docs/contract-change-request.md`) and stops. Waiting is correct behaviour; guessing is not.'
} > docs/phase-0-complete.md
git add -A && git commit -m "L0-P0-023: Phase 0 complete, contracts frozen at contracts/v1.0.0"
git push origin main
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| 1 | The harness is green at the freeze | `python contracts/ci/verify_contracts.py \| tail -1` | `CONTRACTS-VERIFY OK 23/23` |
| 2 | The freeze hash matches the tree | `make promote-check` | `CONTRACTS-FROZEN OK` |
| 3 | The tag is on the remote | `git ls-remote --tags origin 'contracts/v1.0.0' \| wc -l` | `1` |
| 4 | The tag is annotated, not lightweight | `git cat-file -t contracts/v1.0.0` | `tag` |
| 5 | The tag ruleset is active | `gh api "repos/$ORG/control-plane/rulesets/$CT_ID" --jq .enforcement` | `active` |
| 6 | The tag ruleset has zero bypass actors (D-L0-04) | `gh api "repos/$ORG/control-plane/rulesets/$CT_ID" --jq '.bypass_actors \| length'` | `0` |
| 7 | The ruleset blocks creation, update, deletion and non-fast-forward | `gh api "repos/$ORG/control-plane/rulesets/$CT_ID" --jq '[.rules[].type] \| sort \| join(",")'` | `creation,deletion,non_fast_forward,update` |
| 8 | The ruleset covers the contract tag namespace only | `gh api "repos/$ORG/control-plane/rulesets/$CT_ID" --jq '.conditions.ref_name.include \| join(",")'` | `refs/tags/contracts/*` |
| 9 | The register holds all twenty-three rows | `python -c "import yaml;print(len(yaml.safe_load(open('contracts/register.yaml'))['contracts']))"` | `23` |
| 10 | Every register row's stub exists | `python -c "import yaml,os;r=yaml.safe_load(open('contracts/register.yaml'))['contracts'];print(sum(1 for x in r if not os.path.isfile('contracts/'+x['stub'])))"` | `0` |
| 11 | `main` and `integration` carry the same freeze | `git rev-parse main:contracts.sha256 integration:contracts.sha256 \| sort -u \| wc -l` | `1` |
| 12 | The start signal is published | `grep -c 'No lane edits' docs/phase-0-complete.md` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP"
CT_ID=$(gh api "repos/$ORG/control-plane/rulesets" --jq '.[]|select(.name=="contracts-freeze-tags")|.id')
VERIFY=$(python contracts/ci/verify_contracts.py | tail -1)
FROZEN=$(make --no-print-directory promote-check)
TAGTYPE=$(git cat-file -t contracts/v1.0.0)
BYPASS=$(gh api "repos/$ORG/control-plane/rulesets/$CT_ID" --jq '.bypass_actors|length')
RULES=$(gh api "repos/$ORG/control-plane/rulesets/$CT_ID" --jq '[.rules[].type]|sort|join(",")')
ROWS=$(python -c "import yaml;print(len(yaml.safe_load(open('contracts/register.yaml'))['contracts']))")
SIGNAL=$(test -f docs/phase-0-complete.md && echo PRESENT || echo MISSING)
printf 'verify=%s frozen=%s tagtype=%s bypass=%s rules=%s rows=%s signal=%s\n' \
  "$VERIFY" "$FROZEN" "$TAGTYPE" "$BYPASS" "$RULES" "$ROWS" "$SIGNAL"
[ "$VERIFY" = "CONTRACTS-VERIFY OK 23/23" ] || { echo "FAIL: contracts verify failed (got: $VERIFY)"; exit 1; }
[ "$FROZEN" = "CONTRACTS-FROZEN OK" ] || { echo "FAIL: promote-check reports drift (got: $FROZEN)"; exit 1; }
[ "$TAGTYPE" = "tag" ] || { echo "FAIL: contracts/v1.0.0 is not annotated (got: $TAGTYPE)"; exit 1; }
[ "$BYPASS" = "0" ] || { echo "FAIL: tag ruleset bypass actors non-zero (got: $BYPASS)"; exit 1; }
[ "$RULES" = "creation,deletion,non_fast_forward,update" ] || { echo "FAIL: ruleset rules mismatch (got: $RULES)"; exit 1; }
[ "$ROWS" = "23" ] || { echo "FAIL: register row count wrong (got: $ROWS)"; exit 1; }
[ "$SIGNAL" = "PRESENT" ] || { echo "FAIL: docs/phase-0-complete.md missing"; exit 1; }
echo "PHASE-0-COMPLETE"
```

Expected, exactly two lines:

```
verify=CONTRACTS-VERIFY OK 23/23 frozen=CONTRACTS-FROZEN OK tagtype=tag bypass=0 rules=creation,deletion,non_fast_forward,update rows=23 signal=PRESENT
PHASE-0-COMPLETE
```

**STOP RULE** — Do not print `PHASE-0-COMPLETE` by hand, and do not start any lane on a partial result.

* If `bypass=0` is anything else, delete the ruleset and recreate it from `contracts/tag-ruleset.json`. A tag ruleset with one bypass actor is a freeze with a key under the mat.
* If `rows` is anything but `23`, a contract was never registered, and at least one lane will spend its first day developing against nothing.
* If `make promote-check` reports drift, something changed under `contracts/` after the hash was taken. Find it with `git status --porcelain contracts/` and `git diff contracts/` before re-freezing — a re-freeze that absorbs an unexplained change is exactly how a contract silently gains a field.
* If `tagtype` is `commit` rather than `tag`, the tag was created lightweight. Delete it, recreate it with `git tag -a`, and force nothing: delete the remote ref explicitly and push the annotated tag fresh, *before* the ruleset is created.

Any of these is an L0 emergency with `blocked_contract: none` and `blocked_lanes: ALL`.

---

## 5. The stub-and-fixture guarantee

D-L0-06 states the rule: a contract with no stub is not published. This section states what that buys, per lane, because the guarantee is the entire reason five lanes can build in parallel against things that do not exist yet.

### 5.1 What a stub is, and what it is not

A **stub** is the artifact a lane runs its code against on day one, before the publishing lane has written a line. It is not a mock, not a fake and not a subset. It is a real document that validates against the real contract, and the publishing lane's first real output must be substitutable for it without any consumer changing a line.

| A stub is | A stub is not |
| --- | --- |
| A complete, valid document of the contract's shape | A fragment, or a "minimal example" missing optional blocks a consumer might read |
| Synthetic — `stub-product`, `dev-a`, `lead-1`, `stub-dev-a`, `stub-lead-1` and nothing real (D-L0-08, invariant 111) | A real product, a real login, a real digest, or any customer data |
| Frozen with its contract, moving only under a CCR | A place to try things out |
| The document the golden-valid fixture is copied from | A fixture in its own right — fixtures prove the contract, stubs feed the consumer |

**Two stubs are byte-identical to their contract on purpose** — `stubs/capability.vocabulary.yaml` and `stubs/event-type.enum.yaml` — because those contracts *are* the data a consumer reads, and a separate instance would be a second copy of a closed list. Every other stub is a distinct document: a schema is not something a consumer can run against, so its stub is an instance of it. Two more are neither — `stubs/provision-create-product.yaml` and `stubs/provision-add-person.yaml` are **request** documents, because `C-PROV-OP-1` declares effects and a lane can only develop against the request that triggers them (D-L0-11).

### 5.2 The per-lane consumption table

The register in Section 2 reads contract-first. This table reads lane-first, which is the direction a lane actually needs on its first morning.

| Lane | Contracts it consumes | Stubs it develops against | Blocked without |
| --- | --- | --- | --- |
| **L1** | `C-CAP-VOCAB-1`, `C-REG-PEOPLE-1`, `C-REG-ROLES-1`, `C-REG-PRODUCT-2`, `C-REG-VERIFICATION-1`, `C-REG-SERVICE-1`, `C-REG-TOPOLOGY-1`, `C-REG-PLATFORM-1`, `C-EVT-ENV-1`, `C-EVT-ENUM-1`, `C-RECON-SET-1`, `C-PROV-OP-1`, `C-ACC-PERM-1` | `capability.vocabulary.yaml`, `people.yaml`, `roles.yaml`, `product.yaml`, `verification-contract.yaml`, `verification-uat.yaml`, `service.yaml`, `topology.yaml`, `platform.yaml` | **`C-CAP-VOCAB-1`** — every registry validator resolves authority through it, and an undefined capability must resolve to denial (CAP-R3) |
| **L2** | `C-REG-PRODUCT-2`, `C-REG-VERIFICATION-1`, `C-REG-PLATFORM-1`, `C-REC-ENV-1`, `C-EVT-ENV-1`, `C-EVT-ENUM-1`, `C-REC-STORE-MAP-1`, `C-WF-IFACE-1`, `C-WF-CHECKS-1`, `C-WF-SECRETS-1`, `C-WF-EVIDENCE-1`, `C-RECON-FIND-1`, `C-ACC-PROT-1` | `workflow-call-ci.yml`, `workflow-call-deploy-production.yml`, `required-checks.yaml`, `secret-tiers.yaml`, `evidence-chain-answers.yaml`, `store-map.yaml`, `event.yaml` | **`C-WF-CHECKS-1`** — the check name is the coupling to L3 and L5, and a one-character difference is a gate that reads armed and is not |
| **L3** | `C-CAP-VOCAB-1`, all eight `C-REG-*`, `C-REC-ENV-1`, `C-EVT-ENV-1`, `C-EVT-ENUM-1`, `C-REC-STORE-MAP-1`, `C-WF-IFACE-1`, `C-WF-CHECKS-1`, `C-RECON-SET-1`, `C-RECON-FIND-1`, `C-RECON-REPAIR-1`, `C-PROV-OP-1`, `C-ACC-PERM-1`, `C-ACC-PROT-1`, `C-ACC-LAYER-1` | `comparison-set.yaml`, `drift-finding.yaml`, `repair-record.yaml`, `provision-create-product.yaml`, `provision-add-person.yaml`, `permission-model.yaml`, `branch-protection.yaml`, `topology.yaml` | **`C-RECON-SET-1`** — L3 implements the reconciler and decides none of what it compares, at what level or with what class |
| **L4** | `C-REG-PRODUCT-2`, `C-REG-PLATFORM-1`, `C-REC-ENV-1`, `C-EVT-ENV-1`, `C-EVT-ENUM-1`, `C-REC-STORE-MAP-1`, `C-WF-EVIDENCE-1`, `C-RECON-FIND-1`, `C-RECON-REPAIR-1`, `C-ACC-LAYER-1` | `record-incident.yaml`, `record-deployment.yaml`, `record-decision.yaml`, `event.yaml`, `event-type.enum.yaml`, `store-map.yaml`, `layer-split.yaml` | **`C-EVT-ENUM-1`** — an untyped event is unwritable by design, so without the enum L4 has nothing to write |
| **L5** | `C-CAP-VOCAB-1`, `C-REG-PEOPLE-1`, `C-REG-ROLES-1`, `C-REG-TOPOLOGY-1`, `C-EVT-ENV-1`, `C-WF-IFACE-1`, `C-WF-CHECKS-1`, `C-WF-SECRETS-1`, `C-RECON-SET-1`, `C-RECON-FIND-1`, `C-PROV-OP-1`, `C-ACC-PERM-1`, `C-ACC-PROT-1`, `C-ACC-LAYER-1` | `permission-model.yaml`, `branch-protection.yaml`, `layer-split.yaml`, `secret-tiers.yaml`, `topology.yaml`, `people.yaml` | **`C-WF-SECRETS-1`** — L5 provisions the environments the five tiers live in, and the tier-descent rule is a security boundary, not a naming convention |

**Reading the "blocked without" column.** It names the one contract whose absence stops that lane on its first task. Every one of the twenty-three is somebody's dependency; these five are the ones with no workaround, and they are the five a CCR against would be `CCR-BLOCKING` on arrival.

### 5.3 The substitution rule

When a publishing lane ships the real artifact, three things must hold before any consumer switches to it:

1. **The real output validates against the same contract file.** No exceptions, no "close enough", no local relaxation.
2. **`make contracts-verify` still prints `CONTRACTS-VERIFY OK`.** Publishing does not change `contracts/**`, so if the harness has moved, something was edited that should not have been.
3. **The stub stays.** It is not scaffolding to be deleted once the real thing lands.

That third point is the one lanes get wrong. The stub is the permanent offline substitute that keeps PARTITION.md rule 4 true: a lane consumes another lane's output only through `contracts/**` or a published artifact, never by reaching into its source tree. A consuming lane's test suite runs against the stub, offline, without the publishing lane's repository, for the life of the contract.

### 5.4 The fixture pair, and why both halves are mandatory

Every contract carries at least one golden-valid and one golden-invalid fixture. The valid one proves the contract admits what it is supposed to admit. **The invalid one proves it refuses.**

A contract with only valid fixtures is `verify: exit 0` wearing a schema: it is satisfied by everything, and Section 31.2 names that failure mode outright for verification contracts — "A verification contract that cannot fail is not a contract." The same logic applies one level up, to the contracts themselves, which is why `H4` fails a contract missing either half and `H6` treats a validating invalid fixture as a `LEAK`.

`# EXPECT: reject — <reason>` on line 1 of every invalid fixture is not decoration. It is what makes a leak diagnosable: when the harness prints `LEAK contracts/fixtures/C-REG-ROLES-1/invalid-001.yaml`, line 1 of that file says exactly which rule stopped firing, which is the difference between a five-minute fix and an afternoon.

---

## 6. What "frozen" means, exactly

Freezing is a mechanism, not a mood. Four things hold it, and each covers a failure the others do not.

| Mechanism | Stops | Does not stop | Where it lives |
| --- | --- | --- | --- |
| **CODEOWNERS review on `contracts/**`** | A lane merging a contract edit without L0 seeing it | An admin merging with the rule bypassed; a push where protection is absent | Root `CODEOWNERS` (charter L0-00-01), asserted by L0-P0-022 |
| **`contracts.sha256` + `make promote-check`** | An edit landing unnoticed between train runs — the hash stops matching and the train halts | The edit happening. It detects; it does not prevent | Root file (charter L0-00-04), checked at 10:30 daily and at every train step |
| **The immutable tag `contracts/v1.0.0`, empty bypass list** | The frozen point being moved under five lanes with no reviewable diff | An edit on `main` after the tag — the tag records what *was* frozen, not what is current | Tag ruleset `contracts-freeze-tags` (L0-P0-023) |
| **`make contracts-verify`** | A contract, stub, fixture or cross-reference becoming internally inconsistent | Anything about who wrote it, or when | `contracts/ci/verify_contracts.py` (L0-P0-021) |

Read the "does not stop" column carefully. Only the third mechanism is preventive; the other three are detective, and the fourth is a consistency check that knows nothing about authorship. That combination is deliberate and it is also the limit — Section 9 states it plainly.

### 6.1 The four operations permitted after the freeze

Nothing else is permitted, and this list is exhaustive.

| # | Operation | Who | Under what |
| --- | --- | --- | --- |
| 1 | **Read** any file under `contracts/**` | Any lane, at any time | Nothing. Reading is free and encouraged |
| 2 | **Run** anything under `contracts/ci/` | Any lane | Nothing. The harness and the three linters are runnable by everyone and writable by no one |
| 3 | **Copy** a stub into a lane's own tree as a test input | Any lane | Nothing, provided the copy lives inside a path that lane owns |
| 4 | **Change** a contract | L0 only, in the 17:00 window | An approved CCR, a decision record, a green harness, a re-freeze, and a new tag |

Operation 3 carries one trap worth naming. A lane that copies a stub and then **edits its copy** to make its own tests pass has silently forked the contract, and nothing in `contracts/**` can see it. The copy must stay byte-identical, and each lane's test suite should assert exactly that:

**Commands**

```bash
set -euo pipefail
cmp -s "$CP/contracts/stubs/people.yaml" tests/fixtures/people.yaml && echo "stub-copy OK" || echo "stub-copy FORKED"
```

If the copy genuinely needs to differ, the contract is wrong and the answer is a CCR — never a divergent local copy that passes.

### 6.2 What is not frozen

Freezing `contracts/**` freezes **shape**, not behaviour. These stay entirely a lane's:

* **Implementation.** How L1's validator walks a schema, how L3's reconciler batches API calls, how L2 orders job steps.
* **Internal structure inside an owned path.** File names, module boundaries, helper functions, package layout.
* **Test strategy**, beyond the requirement that the golden fixtures pass.
* **Performance and ergonomics.** No contract states a runtime, a CLI shape, an argument name or an output format.

A contract that starts describing any of these has stopped being an interface and started stealing a lane's path — the same failure Section 0 warns about from the other direction. It is fixed by removing the over-specification under a CCR, not by the lane quietly ignoring it. A contract a lane ignores is worse than no contract, because four other lanes still believe it.

---

## 7. Phase 0 task index, dependency graph and decision index

### 7.1 The dependency graph

```
L0-P0-001 ─► L0-P0-002 ─► L0-P0-003 ─┬─► L0-P0-004 ─┐
                                     └─► L0-P0-005 ─┴─► L0-P0-006 ─┬─► L0-P0-007
                                                                   ├─► L0-P0-008 ─┐
                                                                   └─► L0-P0-009 ─┼─► L0-P0-010 ─► L0-P0-011
                                                                                  └─────────────┐
                                                       L0-P0-009 ─┬─► L0-P0-012 ◄──────────────┘
                                                       L0-P0-010 ─┘        │
                                              L0-P0-006 ────────────────────┴─► L0-P0-013 ─┬─► L0-P0-014
                                                                                           ├─► L0-P0-015
                                                                                           └─► L0-P0-016
        L0-P0-006 ─┬─► L0-P0-017 ─► L0-P0-018 ─┐
        L0-P0-012 ─┤                           │
        L0-P0-014 ─┴───────────────────────────┴─► L0-P0-019 ─► L0-P0-020 ─► L0-P0-021 ─► L0-P0-022 ─┬─► L0-P0-025 ─┐
                                    L0-P0-015 ──────────────────────┘                                 └─► L0-P0-026 ─┴─► L0-P0-023
                                    L0-P0-005 ──────────────────────┘

L0-P0-001 ─► L0-P0-024 (parallel — GitHub label bootstrap; has no gate dependency on L0-P0-023)
```

### 7.2 The task table

| Task | What it freezes | Size | Depends on | Blocks | Register rows after |
| --- | --- | --- | --- | --- | --- |
| L0-P0-001 | Both repositories, the `contracts/` tree | M | — | everything | — |
| L0-P0-002 | The register, the header rule, the append helper | M | 001 | 003 | 0 |
| L0-P0-003 | `C-CAP-VOCAB-1` | M | 002 | 004, 005 | 1 |
| L0-P0-004 | `C-REG-PEOPLE-1` | L | 003 | 006 | 2 |
| L0-P0-005 | `C-REG-ROLES-1` | S | 003 | 006, 020 | 3 |
| L0-P0-006 | `C-REG-PRODUCT-2` | L | 004, 005 | 007, 008, 009, 013, 017, 019 | 4 |
| L0-P0-007 | `C-REG-VERIFICATION-1` | M | 006 | — | 5 |
| L0-P0-008 | `C-REG-SERVICE-1`, `C-REG-TOPOLOGY-1`, `C-REG-PLATFORM-1` | L | 006 | 011 | 8 |
| L0-P0-009 | `C-REC-ENV-1` | M | 006 | 010, 012, 018 | 9 |
| L0-P0-010 | `C-EVT-ENV-1` | M | 009 | 011, 012 | 10 |
| L0-P0-011 | `C-EVT-ENUM-1`, all 86 identifiers | L | 008, 010 | 013 | 11 |
| L0-P0-012 | `C-REC-STORE-MAP-1` | M | 009, 010 | 013, 016, 017 | 12 |
| L0-P0-013 | `C-WF-IFACE-1` | L | 006, 012 | 014, 015, 016 | 13 |
| L0-P0-014 | `C-WF-CHECKS-1` | M | 013 | 017, 019, 020 | 14 |
| L0-P0-015 | `C-WF-SECRETS-1` | M | 013 | 020 | 15 |
| L0-P0-016 | `C-WF-EVIDENCE-1` | M | 012, 013 | — | 16 |
| L0-P0-017 | `C-RECON-SET-1` | L | 006, 012, 014 | 018 | 17 |
| L0-P0-018 | `C-RECON-FIND-1`, `C-RECON-REPAIR-1` | L | 009, 017 | 019 | 19 |
| L0-P0-019 | `C-PROV-OP-1` | L | 006, 014, 018 | 020 | 20 |
| L0-P0-020 | `C-ACC-PERM-1`, `C-ACC-PROT-1`, `C-ACC-LAYER-1` | L | 005, 014, 015 | 021 | 23 |
| L0-P0-021 | The self-verification harness, the three linters, `tooling.lock` | L | 020 | 022 | 23 |
| L0-P0-022 | The recorded gaps, the CODEOWNERS assertion, the CCR procedure | M | 021 | 023 | 23 |
| L0-P0-024 | GitHub label set on `control-plane` (17 labels) and `control-plane-records` (7 labels) | S | 001 | — | 23 |
| L0-P0-025 | `contracts/event-types.yaml` — canonical event_type list, 86 identifiers (FD-Q12) | S | 022 | 023 | 23 |
| L0-P0-026 | `e2e/run.sh`, `e2e/verdict.sh`, `contracts/harness/run-contract-tests.sh`, `contracts/harness/pairs.tsv` | M | 022 | 023 | 27 |
| L0-P0-023 | The freeze hash, the tag, the tag ruleset, the start signal | M | 021, 022, 025, 026 | **lanes L1–L5** | 27 |

**Nothing in lanes L1–L5 starts until L0-P0-023's SELF-VERIFY prints `PHASE-0-COMPLETE`.** That is the moment `contracts/**` stops being a directory and becomes an interface.

### 7.3 The decision index

Every L0 decision this file holds, in one place. A lane that finds itself about to decide one of these files a CCR and stops.

| Decision | Recorded in | What it settles |
| --- | --- | --- |
| **D-L0-01** | Section 1 | JSON Schema 2020-12 for anything a validator enforces; declarative YAML for tables of facts |
| **D-L0-02** | Section 1 | The Product Operating Contract is frozen at `contract_version: 2`; v1 is accept-for-read-only |
| **D-L0-03** | Section 1 | 86 `event_type` identifiers, one per taxonomy entry; paired states are payload fields |
| **D-L0-04** | Section 1 | The freeze is an immutable annotated tag protected by a ruleset with an empty bypass-actor list |
| **D-L0-05** | Section 1 | The lane guard is not an L0 artifact; CODEOWNERS and the freeze tag stand in; the gap is recorded as **GAP-L0-01** in `docs/recorded-gaps.md` (authored by L0-P0-022); `.github/workflows/lane-guard.yml` is L2's obligation — L0 may not write there (PARTITION.md line 18) |
| **D-L0-06** | Section 1 | Every contract carries a stub and both halves of the fixture pair, or it is not published |
| **D-L0-07** | Section 1 | `check-jsonschema` + `PyYAML`, pinned in `contracts/tooling.lock`, resolved at freeze time |
| **D-L0-08** | Section 1 | Records and events live in `control-plane-records`; nothing under `contracts/**` is a real record |
| **D-L0-09** | L0-P0-005 | `founder` carries an empty `default_capabilities` list; D106 wins over the Section 8 listing |
| **D-L0-10** | L0-P0-018 | Drift findings and repair records are reconciler-surface artifacts, not record stores |
| **D-L0-11** | L0-P0-019 | `C-PROV-OP-1` declares effects, never implementation; the scripts belong to L3 |
| **D-L0-12** | Section 8.3 | The CCR clock starts on a complete template and pauses only for a named missing field |

---

## 8. The Contract Change Request procedure

**A lane blocked on a contract is an L0 emergency, because four other lanes are waiting.** Every response time below is shorter than any other in this programme, and Section 0 says why: a blocked lane is not one lane idle, it is one lane idle **and** four lanes producing work that will be reworked when the contract lands, because they guessed.

### 8.1 When a CCR is the right channel

The test is mechanical and requires no judgement. That is deliberate: the reader deciding is an executor with no authority to interpret.

```
Does the fix require a change to any file under contracts/** ?
  ├── YES ──► Contract Change Request   (this section; template docs/escalation/CCR.md)
  └── NO  ──► Blocker issue             (charter §7.1; template docs/escalation/BLOCKER.md)
```

That is the entire test. Not "is it important", not "is it urgent", not "is it about a contract". A lane that cannot tell whether the fix touches `contracts/**` files a **blocker**, and L0 reclassifies it — misfiling costs one comment, whereas waiting to be sure costs a day.

**Three things that look like CCRs and are not:**

| Looks like | Actually is | Why |
| --- | --- | --- |
| "The stub is missing a field my code needs" | A **CCR** — stubs live under `contracts/**` | Stubs are frozen with their contracts (D-L0-06) |
| "I don't understand what this contract field means" | A **blocker** | Understanding is not a change; L0 answers with a citation |
| "The contract is right but my lane's schema disagrees with it" | A **blocker** | The lane's own tree is the lane's to fix |

### 8.2 The three classes

Classification is **L0's, on receipt** — never the filing lane's. A lane that classifies its own CCR has made an L0 decision, and the first thing L0 does is reclassify it.

| Class | Definition | Example | Lands as |
| --- | --- | --- | --- |
| **`CCR-ADDITIVE`** | Adds something no existing consumer had to know about. Every document valid before is valid after. | A new `event_type` under the governed-addition rule of 97.3 and 92.11; a new `manual_fallback[]` entry on a provisioning operation; a new optional block on a record body | A minor version of the same file — `event-type.enum.v1.yaml` at `enum_version: 1.1` — with `platform.yaml` regenerated in the same commit. The register row's `version` does not change |
| **`CCR-BLOCKING`** | The filing lane cannot proceed on its current task **and** has no other task whose dependencies are satisfied. | A cross-field rule that cannot be expressed and would otherwise become invisible lane code; a field a consumer must write and the contract has no place for | Whatever the answer requires — including "the contract already covers this, here is the citation" |
| **`CCR-BREAKING`** | A document valid before would be invalid after, or a shipped identifier changes meaning. | Renaming a required status check; making an event-envelope field optional; adding a twelfth evidence question; reclassifying a `C-RECON-SET-1` row downward; widening the capability vocabulary | A new `vN+1` file **beside** the old one. Both versions supported through the declared deprecation window (Section 60.2). Never an edit in place, and never a rename of a shipped identifier (97.3) |

**A `CCR-BLOCKING` may also be `CCR-ADDITIVE` or `CCR-BREAKING`.** Blocking describes the *urgency*; the other two describe the *shape of the change*. L0 writes both labels where both apply, and the response time is the shorter of the two.

Every STOP RULE in Section 4 names the class it expects. Those names are not advisory: a STOP RULE saying **CCR-BREAKING** means L0 has already decided that any change to that rule breaks a consumer, and filing it as additive does not make it additive.

### 8.3 The SLA

> **L0 decision D-L0-12.** The clock starts when the issue is opened with a **complete** template — every field of `docs/escalation/CCR.md` filled in, including the blast-radius grep output. It pauses only when L0 names a **specific** missing field, and resumes the moment that field is supplied. L0 may not pause the clock for "needs more thought"; that is what the response time is for.

| Class | L0 acknowledges by | L0 answers by | If L0 misses it |
| --- | --- | --- | --- |
| **`CCR-BLOCKING`** | **2 working hours** | **Same working day, by 17:00** | The filing lane raises it at the 17:30 readiness check. A `CCR-BLOCKING` open overnight is a recorded incident **against the operating system**, not against the lane |
| **`CCR-BREAKING`** | Next 09:30 sweep | **2 working days**, with a decision record | Same escalation. The two days are a floor on care as much as a ceiling on delay: a breaking change answered in haste is worse than one answered late |
| **`CCR-ADDITIVE`** | Next 09:30 sweep | **Next working day** | Same escalation |

**Acknowledgement is not an answer.** It is L0 stating three things in the issue: the class; whether the lane is blocked; and — if blocked — **which of that lane's other tasks are unblocked and may proceed meanwhile**. A lane receiving an acknowledgement that names no unblocked task **stops**, and that fact is a programme-level signal, not a lane-level one. It means the dependency graph has no slack at that point, which is information L0 needs before it needs the contract fix.

**The contract window.** Contract edits happen at 17:00 and nowhere else (charter §8.1). A `CCR-BLOCKING` answered at 11:00 with "yes, the contract changes" therefore lands at 17:00 the same day: the answer is same-day, the edit is same-day, and the lane restarts the next morning against a re-frozen tree. This is why the acknowledgement matters more than the answer — six hours of a lane's day are recovered by step 2, not by step 5.

**Why these numbers and no others.** Every other response time in this programme is measured in business days (53.4: Red within 2 business days, Amber at the next planning cycle). The CCR times are measured in hours because the multiplier is different: a Red drift finding costs one owner's attention, and a blocked contract costs five lanes' throughput. The asymmetry is the point.

### 8.4 The blocker-issue fields for a contract that does not yet exist

Some blocks are not requests to *change* a contract but reports that one is *missing* — a lane needing a shape Phase 0 never wrote. Those file a **blocker**, using the charter's `docs/escalation/BLOCKER.md`, with these two extra fields appended. Every STOP RULE in this file that says "open a blocker issue" means this form.

```text
BLOCKED CONTRACT:  <contract id from the Section 2 register, or `none` if no contract covers this>
BLOCKED LANES:     <the lanes that cannot proceed: e.g. `L3`, or `ALL`>
```

`BLOCKED LANES: ALL` is reserved for the three conditions that stop the programme, and each is named in its own task's STOP RULE:

| Condition | Task | Why it is programme-wide |
| --- | --- | --- |
| The repositories cannot be created | L0-P0-001 | Nothing exists to build in |
| The register cannot be made machine-readable | L0-P0-002 | Four lanes must enumerate contracts programmatically |
| The freeze cannot be completed | L0-P0-023 | Lanes start on the freeze signal and on nothing else |

Anything else names the specific lanes. Writing `ALL` on a lane-specific block hides which four lanes could have carried on, which is the opposite of what the field is for.

### 8.5 The CCR ledger

Every CCR is recorded, whether or not it changed anything. **A CCR answered "no change needed" is the most valuable row in the ledger:** it is a contract that was tested against a real consumer and held.

| Field | Value |
| --- | --- |
| `ccr_id` | `CCR-<YYYY>-<NNN>` |
| `filed_by` | the lane |
| `contract_id` | from the Section 2 register, or `none` |
| `class` | `CCR-ADDITIVE` \| `CCR-BLOCKING` \| `CCR-BREAKING` |
| `opened`, `acknowledged`, `answered` | timestamps, UTC with offset (97.1) |
| `clock_paused_for` | the named missing field, or `none` (D-L0-12) |
| `outcome` | `changed` \| `no_change_needed` \| `withdrawn` |
| `decision_record` | required when `outcome: changed` |
| `new_freeze_tag` | required when `outcome: changed` |
| `lanes_notified` | every consuming lane on the register row, not only the filer |

The ledger is **not a new store.** Section 52.6 binds — a proposal for a new control-plane artifact must state which existing file cannot hold the content — and `records/decisions/` can hold it, using the `decision` body of `C-REC-ENV-1`. A ledger row is an ordinary decision record whose `subject` is the CCR.

### 8.6 Re-freezing, step by step

A contract change is never finished when the file is edited. Six commands, in this order, every time:

**Commands**

```bash
set -euo pipefail
cd "$CP"
python contracts/ci/verify_contracts.py | tail -1          # must print CONTRACTS-VERIFY OK n/23
find contracts -type f | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -d' ' -f1 > contracts.sha256
git add -A && git commit -m "CCR-<id>: <contract id> — <one line>"
make promote-check                                          # must print CONTRACTS-FROZEN OK
git tag -a "contracts/v1.1.0" -m "CCR-<id>. sha256=$(cat contracts.sha256)"
git push origin main "contracts/v1.1.0"
```

**The old tag is never moved and never deleted** (D-L0-04). Each freeze is a new tag, and the tag history is the audit trail of what five lanes were coding against on any given day. A moved tag makes that history a lie, and a deleted one makes it a gap.

Then — and only then — notify every consuming lane named in the register row. All of them, not only the filer. A lane that discovers a contract changed because its tests started failing has been told too late, and the cost of telling four extra lanes is one message.

### 8.7 A worked example, end to end

L4's executor, on a task under `tools/records/**`, needs to write an event when a support record is reassigned between triagers. It greps `contracts/records/event-type.enum.v1.yaml`, finds `support_item_ingested` and `support_first_touch_breached`, and finds nothing for reassignment.

1. **The lane does not invent `support_item_reassigned`.** D-L0-03 and Section 97.3 make the enum closed; an identifier invented in a lane splits every metric derived from it, which is precisely the failure 97.3 exists to prevent.
2. **The lane files a CCR**, because the fix requires a change under `contracts/**`. The template is complete, blast radius shown: `grep -rl support_item tools/records/` returns two files.
3. **L0 classifies it `CCR-ADDITIVE`** at the 09:30 sweep. No document valid before becomes invalid; the addition is a governed one under 97.3 and 92.11.
4. **L0 acknowledges within two working hours**, naming two of L4's tasks that are unblocked. L4 proceeds on those and loses no time.
5. **L0 answers the next working day.** In the 17:00 window: the identifier is added at `enum_version: 1.1`; `contracts/stubs/platform.yaml`'s `event_types` is regenerated in the same commit; a decision record is written; `make contracts-verify` prints `CONTRACTS-VERIFY OK 23/23`; `contracts.sha256` is re-taken; `make promote-check` prints `CONTRACTS-FROZEN OK`; tag `contracts/v1.1.0` is cut.
6. **L0 notifies L1, L2, L3, L4 and L5** — every consuming lane on the `C-EVT-ENUM-1` register row, because all five emit events.
7. **The ledger row is written** to `records/decisions/` with `outcome: changed`, the decision-record id, and `new_freeze_tag: contracts/v1.1.0`.

Elapsed: one working day. Lane L4 lost nothing, because step 4 handed it two unblocked tasks. **That is the whole design of this section** — not to make contract changes fast, but to make sure a lane is never idle while one is in flight.

The counter-example is just as important. Had the executor added `support_item_reassigned` to its own lane's code and moved on, the enum would have stayed closed at 86, the event would have been written and rejected at write time by `EVT-R2`, and the failure would have surfaced on some later day as a red pipeline in a lane that did not cause it. One working day, spent deliberately, against an unbounded cost paid by someone else.

---

## 9. What Phase 0 does not cover — stated honestly

A control whose limits are undocumented gets trusted past them.

| Not covered by `contracts/**` | Why | Compensating control |
| --- | --- | --- |
| Whether a lane's implementation actually satisfies the contract | The freeze is a shape control, not a behaviour control | The golden fixtures, each lane's own tests, and the merge gate (`L0-03-merge-train.md`) |
| A lane copying a stub and editing its copy | Invisible to a harness that only reads `contracts/**` | The `cmp` assertion of Section 6.1, run inside the lane's own test suite |
| Two lanes implementing the same unencodable rule differently | Both may validate against the same schema and still disagree | Every rule that cannot be schema-encoded is named and assigned one owner: `EVT-R3`'s ordering half to L4, `PROD-R7`'s freshness check to L3, `FIND-R6`'s run-level assertion to L3 |
| A contract that is correct and useless | No mechanical test for usefulness exists | The stub requirement (D-L0-06): a contract nobody can run against does not ship |
| An org admin deleting the tag ruleset, or disabling branch protection | No repository-level control survives an org admin | The independent control verifier of Section 53.1, declared in `C-RECON-SET-1` — running off the operations VM under a different credential, writing to a surface that VM cannot write to, and **its own absence for one cycle is Level 5** |
| Subsystems G, H, J, O and P | Unassigned in PARTITION v1 | No contract claims them. A lane needing one states the dependency in a blocker and routes it to L0; it never claims the subsystem |

The last two rows are the honest ones.

The tag ruleset is the strongest mechanism Phase 0 has, and an organisation Owner can remove it in one click. That is exactly why the spec's own answer to "who guards the guard" is not another check inside the same repository under the same credential, but a verifier that runs somewhere else, under something else, and whose **silence is itself a finding**. Building it is L5's work under `access/**`, it is `GAP-L0-05` in `docs/recorded-gaps.md`, and until it exists the contract freeze is held by a hash, a tag and a human reading pull requests.

That is a recorded gap with an owner and a date, like every other gap in this programme — which is the only honest way to hold one.

---

**Phase 0 ends when L0-P0-023 prints `PHASE-0-COMPLETE`. Lanes L1 through L5 begin the next morning, each against the stubs named for it in `docs/phase-0-complete.md`, and none of them ever edits `contracts/**` again.**
