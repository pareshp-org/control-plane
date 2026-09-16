# 05 — Entry and Exit Criteria

**Scope of this file.** For every phase in every lane of the FROZEN partition (`implementation/PARTITION.md`): what must be true to *start* the phase, what must be true to *finish* it, and the exact command that proves finishing. Every exit criterion here is machine-checkable — a command whose output is `PASS <id>` or `FAIL <id>` and nothing else. Where a spec acceptance test (Section 100, AT-001…AT-110) proves a criterion, the real AT id is cited. Where no AT applies, the phase says so explicitly and names the standing evidence that substitutes.

**Authority.** `PARTITION.md` is frozen and is never redesigned here. `Research/MultiProduct_MasterSpec_v4.0.md` is the specification. Where the spec leaves something design-open (Section 99.3) or where the partition leaves something unassigned, this file raises an **L0 DECISION REQUIRED** block and stops. It never invents.

**Reader.** A Sonnet-4.6-class AI developer with no repo context and no judgment authority. Every command below is copy-pasteable. If a command is missing a value you do not have, that is a blocker, not an invitation to guess — see the STOP rule on the phase.

---

## 0. How to read this file

### 0.1 Two phase axes, deliberately distinct

The spec has phases. The build has phases. They are not the same thing and must never be conflated.

| Axis | Owner | Named | Meaning |
|---|---|---|---|
| **Spec/operating phases** — Foundation 1–7, early hardening, scale activation, G1–G8, P1–P8 (spec §98.2–§98.6) | L0 | `G-F1`…`G-F7`, `G-G1`, `G-G2` in this file | An *operating* milestone of the company. Its completion check (quoted verbatim from §98.2) is satisfied by the union of several lane build phases plus human/drill evidence. |
| **Lane build phases** — `L1-P1`…`L5-P5` | the five AI developers | this file, §3–§7 | A *build* milestone on one branch, inside one lane's owned paths. Short-lived branch, one PR, one merge into `integration`. |

A lane developer executes lane build phases only. L0 executes `L0-P0`, the per-cycle integration gate `G-INT`, and the spec-phase gates `G-F*` / `G-G*`.

### 0.2 Phase id scheme

`L<lane>-P<n>` — e.g. `L3-P4` is lane 3's fourth build phase. Branch name for it is `lane/3/p4-<task>` (PARTITION: `lane/N/<phase>-<task>`). Criterion ids are `L3P4-E1` (exit) and `L3P4-N1` (entry).

### 0.3 The verification vocabulary — read this once, it is used everywhere

Every exit gate is a single bash block. Paste it whole. It prints one line per criterion and exits non-zero on the first failure.

```bash
set -euo pipefail
# ---- PREAMBLE. Paste once per shell session, before any gate command. ----
# POSIX shell. On Windows use Git Bash (paths and /tmp resolve correctly there).
set -o pipefail
export CP="$HOME/src/control-plane"            # control-plane checkout
export CPR="$HOME/src/control-plane-records"   # control-plane-records checkout
ok(){ echo "PASS $1"; }
no(){ echo "FAIL $1"; exit 1; }
cd "$CP" || no PREAMBLE-CP
export ORG="$(python -c "import yaml;print(yaml.safe_load(open('contracts/estate.yaml'))['org'])")"
test -n "$ORG" || no PREAMBLE-ORG
gh auth status >/dev/null 2>&1 || no PREAMBLE-GH
ok PREAMBLE
```

Rules, binding:

1. A phase is **exited** only when its gate block prints `PASS` for every criterion id listed in its exit table and prints no `FAIL`.
2. Any `FAIL`, any non-zero exit, any missing tool → **stop**. Open a blocker issue titled `blocker/lane-<N>/<phase-id>/<criterion-id>` with the full command output pasted. Do not "fix around" it, do not widen the command, do not edit another lane's path.
3. A gate command is never edited to make it pass. If the command is wrong, that is a Contract Change Request to L0 (PARTITION rule 2), not a lane edit.
4. Negative tests are executed for real, never asserted. Where a criterion says "rejects X", the gate feeds a real malformed fixture and requires the rejection. This mirrors spec §98.2 Phase 1, which requires its completion checks be "executed negatively".

### 0.4 The universal entry gate — every lane phase, no exceptions

Before starting **any** `L<n>-P<k>`, all five hold. This block is the entry proof; it is not repeated in each phase.

```bash
set -euo pipefail
# ---- UNIVERSAL ENTRY GATE. LANE=1..5, PHASE=p1..p6 ----
LANE=1; PHASE=p1; TASK=core-registry-schemas   # <-- set these three
git -C "$CP" fetch origin
git -C "$CP" rev-parse --verify origin/integration >/dev/null 2>&1 || no UEG-1
# Requires L0-00-03 to have emitted contracts/lane-paths.yaml before this gate passes
git -C "$CP" show origin/integration:contracts/lane-paths.yaml >/dev/null 2>&1 || no UEG-2
git -C "$CP" log origin/integration -1 --format=%H > /tmp/int-head.txt && ok UEG-3
git -C "$CP" checkout -b "lane/$LANE/$PHASE-$TASK" origin/integration && ok UEG-4
gh issue list --repo "$ORG/control-plane" --label "blocker/lane-$LANE" --state open \
  --json number --jq 'length' | grep -qx 0 && ok UEG-5 || no UEG-5
```

| id | Entry condition | Why |
|---|---|---|
| UEG-1 | `origin/integration` exists and is fetched | PARTITION: lanes branch from and rebase onto `integration` |
| UEG-2 | `contracts/lane-paths.yaml` exists on `integration` | Contract-first (PARTITION rule 2); the lane-guard reads `lane-paths.tsv` and `L0-00-03` emits **both** `contracts/lane-paths.yaml` and `lane-paths.tsv` from one generator block with identical prefix sets. **This gate fails for all lanes until `L0-00-03` has run.** |
| UEG-3 | The `integration` head SHA is recorded before work starts | Rebase base is provable at PR time |
| UEG-4 | Branch created as `lane/<N>/<phase>-<task>` | PARTITION branch model |
| UEG-5 | Zero open blocker issues for this lane | A lane with an open blocker does not start new work |

### 0.5 The universal exit gate — every lane phase, no exceptions

Runs in addition to the phase's own criteria.

```bash
set -euo pipefail
# ---- UNIVERSAL EXIT GATE. Set LANE and PATHS_RE to the lane's row below. ----
LANE=1
PATHS_RE='^(schemas/registry/|schemas/product/|registries/|validators/registry/)'
git -C "$CP" fetch origin
git -C "$CP" diff --name-only origin/integration...HEAD > /tmp/changed.txt
test -s /tmp/changed.txt || no UXG-1; ok UXG-1
grep -vE "$PATHS_RE" /tmp/changed.txt > /tmp/foreign.txt || true
test ! -s /tmp/foreign.txt && ok UXG-2 || { cat /tmp/foreign.txt; no UXG-2; }
git -C "$CP" merge-base --is-ancestor origin/integration HEAD && ok UXG-3 || no UXG-3
git -C "$CP" log origin/integration..HEAD --format='%H %G?' | grep -qv ' G$' && no UXG-4 || ok UXG-4
```

| Lane | `PATHS_RE` (the only paths the lane may appear in) |
|---|---|
| L1 | `^(schemas/registry/\|schemas/product/\|registries/\|validators/registry/)` |
| L2 | `^(\.github/workflows/\|templates/workflows/\|tools/evidence/)` |
| L3 | `^(reconciler/\|tools/provision/\|validators/drift/)` |
| L4 | in `control-plane`: `^(schemas/records/\|metrics/\|tools/records/)`; in `control-plane-records`: `^(records/\|events/)` |
| L5 | `^(access/\|infra/\|ops-vm/\|notify/\|assets/)` |
| L0 | `^(contracts/\|docs/\|CODEOWNERS\|Makefile\|[^/]+$)` |

| id | Exit condition | Enforces |
|---|---|---|
| UXG-1 | The branch actually changed something | No empty phases |
| UXG-2 | Zero foreign paths in the diff | PARTITION rule 1, one owner per path |
| UXG-3 | Branch is rebased on current `integration` | PARTITION branch model |
| UXG-4 | Every commit is signature-verified | Spec §101 invariant 47 / D107 commit-signing discipline |

---

## 1. L0 DECISION REQUIRED — five open items that gate criteria in this file

These are recorded, not resolved. No lane may proceed past the phases named in each block until L0 records the decision in `contracts/` and this file is amended by L0.

### D-EE-1 — Toolchain binding for validators, reconciler and CLIs

**Why open.** Spec §99.5 fixes the *substrate* (GitHub, Actions, Grafana, DevLake, Prometheus, YAML in git). It does not name an implementation language for subsystems B, C, D, F, I. Section 99.3 does not list it either — it is unbound, not design-open, and this file will not bind it silently.

| Option | Stack | Consequence |
|---|---|---|
| **T-A (recommended)** | Python 3.12, `jsonschema`, `check-jsonschema`, `PyYAML`, `pytest` | One runtime for validators, reconciler, provisioning CLI and metrics jobs; matches the ops-VM job substrate (§99.2 M) |
| T-B | Node 20, `ajv-cli`, `js-yaml`, `vitest` | Closer to Actions-native tooling; second runtime on the ops VM |
| T-C | Go, single static binaries | Best for the reconciler's privileged credential; slowest to author with AI assistance |

**Every command in this file is written against T-A.** If L0 selects T-B or T-C, apply this substitution table and change nothing else:

| T-A form | T-B form | T-C form |
|---|---|---|
| `python -m validators.registry.cli <args>` | `node validators/registry/cli.js <args>` | `./bin/registry-validate <args>` |
| `python -m reconciler.cli <args>` | `node reconciler/cli.js <args>` | `./bin/reconcile <args>` |
| `python -m tools.provision.cli <args>` | `node tools/provision/cli.js <args>` | `./bin/provision <args>` |
| `pytest <path>` | `npx vitest run <path>` | `go test ./<path>/...` |

**Blocks:** L1-P1 onward, L3-P1 onward, L4-P3 onward. Nothing starts until this is recorded.

### D-EE-2 — Five subsystems have no lane in the frozen partition

Spec §99.2 defines subsystems A–R. `PARTITION.md` assigns A, B (L1), E, F (L2), C, D (L3), I, N (L4), K, L, M, Q, R (L5). **G, H, J, O and P are assigned to no lane.** This is a fact about the frozen partition, not a defect this file may repair.

| Subsystem | §99.2 scope | Paths it would need | Constraint |
|---|---|---|---|
| G | Plan-checker and Gate 1 tooling | none owned | §99.2 rates it "L if built in-house"; §99.3 item 3 and §99.6 risk 4 make in-house a *contingent* build |
| H | Dashboards and views (Grafana JSON in git, every §92 surface) | would sit in `infra/**` or `ops-vm/**` (L5) or `metrics/**` (L4) | Depends on I, F, C — i.e. on three lanes |
| J | Background machine layer (Hermes cage, egress override, systemd stop) | artifacts land in `ops-vm/**` (L5) but J is absent from L5's subsystem list | Conditional on the §98.2 Phase 3 CPU benchmark; a failed benchmark parks it (§99.5) |
| O | Governance registries and *jobs* (exception lifecycle, policy stages, pattern detector, change budget, exit checklists, tool register) | the *files* are `registries/**` (L1); the *jobs* have no home | Split between L1 (schema) and nobody (job) |
| P | People intelligence engine | none owned | §98.6 P4 is hard-gated on L5-P5 anyway |

**Options for L0, each preserving the partition's one-owner rule:**

- **Option 1 — Assign into existing lanes by path:** H → L5 (`infra/grafana/**`), J → L5 (`ops-vm/hermes/**`), O-jobs → L3 (`reconciler/jobs/**`, since exception expiry is already a reconciliation behaviour per §99.2 C), G → out of build scope until §99.3 item 3 verification completes, P → deferred to the People tier with its own lane opened later.
- **Option 2 — Open a sixth lane L6** for H + O-jobs + P, with its own path set. Contradicts nothing in PARTITION (which fixes five *build* lanes) but changes the merge train.
- **Option 3 — L0 builds H, J, O-jobs, G, P itself** as integrator work, outside the five parallel branches.

**Consequence while unresolved:** the acceptance tests listed as `unclaimed` in §9 of this file have no owning phase and therefore no exit criterion. They are AT-014, AT-015 (schema half only; full test unclaimed), AT-023, AT-026, AT-040, AT-041, AT-042, AT-043, AT-045, AT-052…AT-070, AT-073, AT-076, AT-077, AT-079…AT-086, AT-088, AT-099 (view half), AT-100 (bundle half), AT-108, AT-109.

### D-EE-3 — Where the acceptance-test harness lives, and how an AT id maps to a command

**Why open.** Every exit criterion in this file that cites an AT must be executable. `PARTITION.md` assigns no path for a cross-lane acceptance-test harness, and rule 4 forbids a lane reaching into another lane's tree.

| Option | Shape | Cost |
|---|---|---|
| **O-3A (recommended)** | L0 owns `tests/acceptance/**` as a root path; one file per AT, named `AT-0NN_<slug>`; each lane delivers its AT checks as a CLI subcommand in its own tree and L0's harness only invokes CLIs | Adds one L0 path; keeps rule 4 intact |
| O-3B | Each lane owns `tests/acceptance/lane-<N>/**` under its own tree; L0's `Makefile` aggregates | No new shared path; AT ids are then split across five trees and no single command runs the catalogue |
| O-3C | The harness is a workflow only (`.github/workflows/acceptance.yml`, L2) | Puts every lane's AT logic in L2's tree — violates rule 4 in spirit |

**Until decided,** every AT-citing criterion in this file is expressed as the underlying literal check (the `gh api` call, the fixture rejection, the CLI invocation), so the criterion is executable without the harness. The harness only aggregates.

### D-EE-4 — The seven design-open items of spec §99.3, each mapped to the phase it gates

Spec §99.3 states these are for the implementer to invent and to log at build time. This file logs them and hands each to L0. **No lane invents any of them.**

| §99.3 item | Gates | What L0 must record before that phase's exit criterion can be authored |
|---|---|---|
| 1. Attention classifier and constraint diagnosis | `L4-P5` exit | The Healthy/Watch/Action-Required rule set and the "which constraint binds" precedence order, as a config file under `registries/` (L1-owned) that L4 reads |
| 2. `make parity` declaration format | `L2-P2` exit criterion `L2P2-E4` | The environment-schema format (one file, reused by local/staging/production) — spec §33.1 requires the comparison but not the format |
| 3. Plan-checker internals | subsystem G, see D-EE-2 | Verify every §30.2 capability against the exact pinned GSD release; if verification fails, budget the in-house build (§99.6 risk 4) |
| 4. DevLake field coverage | `L4-P4` exit criterion `L4P4-E3` | Which of the §79 measures DevLake serves natively and which need bespoke computation — spec says "confirm coverage before Phase G3" |
| 5. Machine sources for context checks (§80) | People tier (subsystem P, D-EE-2) | The computable boundary: which of the fifteen §80 checks the engine may propose |
| 6. KPI instrumentation projects | People tier (subsystem P, D-EE-2) | Each §79 row marked "available after instrumentation" is its own mini-project with its own owner |
| 7. Calibration methods (PLU fit, forecast scoring, sustainable-utilisation bands, §97.4 session parameters, §72.3 confidence table) | `L4-P5`, People tier | Deliberately left as quarterly refits; the *initial* values must still be recorded as configuration so the exit command has something to assert against |

### D-EE-5 — "Detection has run clean for weeks" needs a number

**Why open.** Spec §98.3 and §99.4 item 6 gate reconciliation auto-repair on detect-only "running clean for weeks". `L3-P4`'s entry criterion cannot be machine-checked against "weeks".

| Option | Threshold | Note |
|---|---|---|
| O-5A | 14 consecutive days, zero unexplained findings, canary found on every run | Fastest; thinnest evidence |
| **O-5B (recommended)** | 28 consecutive days, zero unexplained findings, canary found on every run, ≥1 real Blocking finding correctly raised and closed | Matches "weeks" plural and proves the detector fires, not just runs |
| O-5C | 42 days plus a full restore-test rotation cycle | Safest; delays the highest-value repair classes |

`L3P4-N2` below is written against **O-5B** and carries the number in one variable. Change the variable, nothing else.

---

## 2. L0 — Integrator phases and gates

L0 owns `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` and both branch targets.

### L0-P0 — Contract freeze (spec §98.2 Phase 1 precondition; PARTITION rule 2)

**Entry**

| id | Condition | Proof |
|---|---|---|
| L0P0-N1 | The three repositories exist: `control-plane`, `control-plane-records`, `product-template` | `gh repo view "$ORG/control-plane" --json name` etc. |
| L0P0-N2 | Organisation base permission is Read | `gh api "orgs/$ORG" --jq .default_repository_permission` returns `read` |
| L0P0-N3 | Teams granting Write exist **before** branch protection is armed (spec §98.2 Phase 1, verbatim: arming a gate while no Team grants Write "leaves nobody whose approval counts") | `gh api "orgs/$ORG/teams" --jq 'length'` > 0 |
| L0P0-N4 | D-EE-1 recorded in `contracts/estate.yaml` | key `toolchain` present |

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L0P0-E1 | `contracts/` contains `estate.yaml`, `lane-paths.yaml`, and one interface file per producing lane; every file carries `contract_version: 1` (`lane-paths.yaml` is emitted by `L0-00-03` from `lane-paths.tsv`; both files carry identical prefix sets) | — | Spec §60.2 versioned contracts; PARTITION rule 2 |
| L0P0-E2 | `contracts/lane-paths.yaml` maps every path prefix in PARTITION to exactly one lane; no prefix appears twice; no owned prefix is missing (`contracts/lane-paths.yaml` is generated by `L0-00-03` from `lane-paths.tsv`; the acceptance criterion for `L0-00-03` requires an empty symmetric difference between the two prefix sets) | — | PARTITION rule 1, executed as a set-comparison |
| L0P0-E3 | `CODEOWNERS` names a lane team for every prefix in `lane-paths.yaml` (generated by `L0-00-03` from `lane-paths.tsv`; both files carry identical prefix sets), and names **human identities only** for review-bearing paths | AT-110 (adjacent); spec §98.2 Phase 1 "CODEOWNERS is generated to contain human identities only, and the check is executed negatively" | — |
| L0P0-E4 | The required-status-check list on every repository starts **empty** | — | Spec §98.2 Phase 1, verbatim: "The required-status-check list starts empty per repository"; a required check no workflow emits blocks every PR indefinitely |
| L0P0-E5 | No direct human push to a default branch succeeds on `control-plane`, and **no machine identity is a bypass actor** on it | — | Spec §98.2 Phase 1 completion check; D89 |
| L0P0-E6 | All Phase 0-gated decisions closed — `make decisions-gate PHASE=Ph0` prints `DECISIONS-GATE OK` (zero open P0/P1 entries gating at or before `Ph0`) (see `master/00-MASTER-PLAN.md` EC-16; register built by `lanes/L0-04-decisions-register.md` §3) | — | `lanes/L0-04-decisions-register.md` §3 Ph0-gated entries each carry a dated closure record in `docs/decisions/closed/` |

```bash
set -euo pipefail
# ---- L0-P0 EXIT GATE ----
python - <<'PY' && ok L0P0-E1 || no L0P0-E1
import sys,yaml,pathlib
# lane-paths.yaml is generated by L0-00-03 from lane-paths.tsv; both files carry identical prefix sets
req={"estate.yaml","lane-paths.yaml","l1-schemas.yaml","l2-workflows.yaml",
     "l3-reconciler.yaml","l4-records.yaml","l5-access.yaml"}
have={p.name for p in pathlib.Path("contracts").glob("*.yaml")}
missing=req-have
if missing: print("missing:",sorted(missing)); sys.exit(1)
for n in req:
    d=yaml.safe_load(open("contracts/"+n))
    if d.get("contract_version")!=1: print("no contract_version:",n); sys.exit(1)
PY
python - <<'PY' && ok L0P0-E2 || no L0P0-E2
import sys,yaml,collections
# Generated by L0-00-03 from lane-paths.tsv; both files carry identical prefix sets
m=yaml.safe_load(open("contracts/lane-paths.yaml"))["lanes"]
seen=collections.Counter(p for l in m.values() for p in l)
dupe=[p for p,c in seen.items() if c>1]
need={"schemas/registry/","schemas/product/","registries/","validators/registry/",
      ".github/workflows/","templates/workflows/","tools/evidence/",
      "reconciler/","tools/provision/","validators/drift/",
      "schemas/records/","metrics/","tools/records/",
      "access/","infra/","ops-vm/","notify/","assets/","contracts/"}
gap=need-set(seen)
if dupe or gap: print("dupe:",dupe,"gap:",sorted(gap)); sys.exit(1)
PY
python - <<'PY' && ok L0P0-E3 || no L0P0-E3
import sys,yaml,re
# Generated by L0-00-03 from lane-paths.tsv; both files carry identical prefix sets
prefixes={p for l in yaml.safe_load(open("contracts/lane-paths.yaml"))["lanes"].values() for p in l}
co=open("CODEOWNERS").read().splitlines()
covered={ln.split()[0].lstrip("/") for ln in co if ln.strip() and not ln.startswith("#")}
if not prefixes <= covered: print("uncovered:",sorted(prefixes-covered)); sys.exit(1)
PY
gh api "repos/$ORG/control-plane/branches/main/protection" \
  --jq '.required_status_checks.contexts | length' | grep -qx 0 && ok L0P0-E4 || no L0P0-E4
for id in $(gh api "/repos/$ORG/control-plane/rulesets" --jq '.[].id'); do
  gh api "/repos/$ORG/control-plane/rulesets/$id"
done | jq -s '[.[].bypass_actors // [] | .[]] | length' | grep -qx 0 \
  && ok L0P0-E5 || no L0P0-E5
make decisions-gate PHASE=Ph0 | grep -q "^DECISIONS-GATE OK" && ok L0P0-E6 || no L0P0-E6
```

**SELF-VERIFY L0P0-E5 (negative test — DF-0139).** Before relying on this gate in a real cycle, confirm the two-step check can return a non-zero count. Seed a temporary branch ruleset with a machine bypass actor, run the check, assert the result is non-zero, then delete the test ruleset:

```bash
set -euo pipefail
# Seed a ruleset with one bypass actor on control-plane
TEST_RS=$(gh api -X POST "/repos/$ORG/control-plane/rulesets" --input - --jq '.id' <<'JSON'
{
  "name": "drill-bypass-test",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [{"actor_id": 1, "actor_type": "Integration", "bypass_mode": "always"}],
  "conditions": {"ref_name": {"include": ["refs/heads/drill-*"], "exclude": []}},
  "rules": []
}
JSON
)
COUNT=$(for id in $(gh api "/repos/$ORG/control-plane/rulesets" --jq '.[].id'); do
  gh api "/repos/$ORG/control-plane/rulesets/$id"
done | jq -s '[.[].bypass_actors // [] | .[]] | length')
[ "$COUNT" -gt 0 ] \
  && echo "NEGATIVE TEST PASS: gate returns $COUNT (non-zero as expected)" \
  || { echo "NEGATIVE TEST FAIL: gate returned 0 with a seeded bypass actor — bypass_actors not being read"; exit 1; }
gh api -X DELETE "/repos/$ORG/control-plane/rulesets/$TEST_RS"
```

**Asserts:** `$COUNT` must be ≥ 1. A result of 0 means `bypass_actors` is still not being fetched from the individual-ruleset endpoint — the old list-endpoint silent-miss bug persists.

**STOP rule.** If `L0P0-E5` fails because a machine identity is listed as a bypass actor on `control-plane`, do not remove it and continue — D89 makes this a design question about where the records-writer credential lives. Open `blocker/lane-0/L0-P0/E5`.

### G-INT — the per-cycle integration gate (run once per merge-train cycle, in order L1 → L4 → L2 → L3 → L5)

**Entry:** every lane PR in this cycle is rebased on `integration`, its universal exit gate printed all `PASS`, and its own phase gate printed all `PASS`.

```bash
set -euo pipefail
# ---- G-INT ----
git -C "$CP" checkout integration && git -C "$CP" pull --ff-only && ok GINT-1 || no GINT-1
python -m validators.registry.cli validate --all --strict && ok GINT-2 || no GINT-2
python -m reconciler.cli run --dry-run --require-canary --format json > /tmp/rec.json \
  && python -c "import json,sys;d=json.load(open('/tmp/rec.json'));sys.exit(0 if d['canary_found'] and d['blocking']==0 else 1)" \
  && ok GINT-3 || no GINT-3        # AT-102: a run finding nothing is a FAILED run
gh run list --repo "$ORG/control-plane" --branch integration --limit 1 \
  --json conclusion --jq '.[0].conclusion' | grep -qx success && ok GINT-4 || no GINT-4
```

| id | Criterion | AT |
|---|---|---|
| GINT-1 | `integration` fast-forwards cleanly — no lane produced a conflicting edit | — (PARTITION rule 3 is the design that guarantees it; this is its test) |
| GINT-2 | Full registry validator suite green across every registry and contract | — (spec §99.2 B) |
| GINT-3 | Reconciler dry-run finds the seeded canary and reports zero Blocking drift | **AT-102** |
| GINT-4 | Latest `integration` CI run concluded `success` | — |

### G-F1 … G-F7 and G-G1, G-G2 — spec phase completion gates (L0)

Each row's "completion check" is quoted from spec §98.2 / §98.5. The gate passes only when **every** lane phase in the middle column has exited and the extra evidence in the right column exists.

| Gate | Spec completion check (§) | Requires lane phases | Extra evidence L0 must hold |
|---|---|---|---|
| **G-F1** Foundation | §98.2 Phase 1 | L0-P0, L1-P1, L5-P1 | 2FA enforced org-wide with hardware keys/passkeys for Founder, Owners, platform-admin holders; `env \| grep -i api_key` empty on every machine; second org Owner or escrowed break-glass credential with a **named escrow custodian**; a workflow on a non-default branch declaring `environment: production` obtains no secret (executed negatively); org-export first run scheduled in Phase 2 **or** its absence recorded as a dated accepted risk (D80) |
| **G-F2** Visibility | §98.2 Phase 2 | L5-P2, L4-P4 | Every product visible in Grafana with a Scorecard score; control-plane surfaces reachable only over the §51.4 private path **or** a dated `policy_waiver` in `exceptions.yaml`; every live product onboarding or in declared pre-onboarding mode with a deadline |
| **G-F3** Registries & Standards | §98.2 Phase 3 | L1-P2, L1-P3, L1-P4, L3-P1, L3-P5 | Constitution file written incl. untrusted-input and unattended-agent rules; Repomix installed; background-layer benchmark **run and decided** (go/park) before any local-inference slot activates; Hermes cage registered in `tools.yaml` before first use (D69) |
| **G-F4** Environments (per product) | §98.2 Phase 4 | L2-P1, L2-P2, L5-P1 | A person unfamiliar with the product runs `make setup && make dev && make test` successfully; `make parity` reports no divergence; the required-status-check contexts **this phase adds** are listed in branch protection and actually reported by a run |
| **G-F5** Verification (per product) | §98.2 Phase 5 | L2-P2 | Verification contract present and passing; QA signed off within the §96.6 QA-takeover SLA (initial: two weeks from the AI-drafted suite landing); a breach is a QA-capacity signal, never a personal one |
| **G-F6** Delivery Pipeline (per product) | §98.2 Phase 6 | L2-P3, L2-P4, L2-P5, L2-P6, L4-P2 | A deliberate rollback succeeded in staging; restore test recorded and entered into the rolling 90-day rotation; the eleven-item evidence chain answerable for one real deployment; production-approval test verifies the workflow-identity gate and fails closed when approver == deployer (D73) |
| **G-F7** GSD Activation (per product) | §98.2 Phase 7 | — (subsystem G, see D-EE-2) | A first plan passes the plan-checker and is approved at Gate 1 |
| **G-G1** OS observability | §98.5 G1 | L3-P3, L4-P4, L5-P2 | Founder answers "is the operating system healthy?" from one screen; zero Blocking drift open; pre-Phase-1 baselines verified and **re-recorded**, never mixed with ledger-derived figures |
| **G-G2** Exception & policy governance | §98.5 G2 | L1-P4, L3-P1, L3-P3 | Every existing exception has a record and an expiry; every policy has an owner and a review date; **AT-036** and the break-glass test pass |

```bash
set -euo pipefail
# ---- G-F1 (the parts that are machine-checkable from a shell) ----
gh api "orgs/$ORG" --jq .two_factor_requirement_enabled | grep -qx true && ok GF1-2FA || no GF1-2FA
gh api "orgs/$ORG/members?role=admin" --jq 'length' | awk '$1>=2{exit 0}{exit 1}' \
  && ok GF1-OWNERS || no GF1-OWNERS
env | grep -i 'api_key' && no GF1-KEYS || ok GF1-KEYS      # invariant 84
python -m validators.registry.cli validate --file registries/exceptions.yaml --strict \
  && ok GF1-EXC || no GF1-EXC
```

**STOP rule for every `G-*` gate.** A gate is never partially passed. If any row's evidence is missing, the spec phase is *not* complete; record the shortfall as a dated accepted risk in `exceptions.yaml` with an expiry, an owner and a deactivation trigger (spec §54.2, invariant 77) — or stop. There is no third option, and a decision record with no clock is not a substitute (§98.2 Phase 2, verbatim).

---

## 3. Lane L1 — Registries & Contracts (subsystems A, B)

Owns `schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**`.

> **Derivation from PARTITION rule 1, stated so no lane collides:** `os-health.yaml`, `policies.yaml`, `patterns.yaml`, `economics.yaml`, `platform-roadmap.yaml`, `tools.yaml`, `topology.yaml` and `exceptions.yaml` all live under `registries/**` and are therefore **L1-owned files**, even where the spec discusses them under a governance or metrics heading. L3, L4 and L5 read them; none of them writes them. Anything else is a Contract Change Request to L0.

### L1-P1 — Core registry schemas and the validator engine skeleton

Spec: §7 (people), §8 (roles), §60.1 (platform.yaml), §54.1 (exceptions), §97.3 (the `event_type` enum ships populated in Phase 1, declared in `platform.yaml`).

**Entry**

| id | Condition | Proof |
|---|---|---|
| L1P1-N1 | Universal entry gate passed | §0.4 |
| L1P1-N2 | D-EE-1 recorded | `python -c "import yaml;print(yaml.safe_load(open('contracts/estate.yaml'))['toolchain'])"` prints a value |
| L1P1-N3 | `contracts/l1-schemas.yaml` exists and names the schema `$id` namespace | `test -f contracts/l1-schemas.yaml` |

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L1P1-E1 | JSON Schemas exist for `people.yaml`, `roles.yaml`, `platform.yaml`, `exceptions.yaml`; each has a stable `$id` from `contracts/l1-schemas.yaml` | — | Spec §99.2 subsystem B; §99.3 "direct transcription to JSON Schema is possible" |
| L1P1-E2 | The validator **rejects** a deliberately malformed exception missing expiry, owner or deactivation trigger | — | Spec §98.2 Phase 1 completion check, verbatim: "rejects a deliberately malformed exception"; invariant 77 |
| L1P1-E3 | `platform.yaml` carries the populated `event_type` enum and the validator rejects an event type absent from it | — | Spec §97.3, verbatim: "the enum ships populated in Phase 1 so no workflow ever writes an untyped event" |
| L1P1-E4 | People and role records are effective-dated and append-only-shaped (a change adds a record, never overwrites) | — | Invariant 47; §99.4 item 1 ("retrofitting history is impossible by definition") |

```bash
set -euo pipefail
# ---- L1-P1 EXIT GATE ----
for s in people roles platform exceptions; do
  test -f "schemas/registry/$s.schema.json" || no L1P1-E1
  python -c "import json,sys;d=json.load(open('schemas/registry/$s.schema.json'));sys.exit(0 if d.get('\$id') else 1)" || no L1P1-E1
done; ok L1P1-E1
python -m validators.registry.cli validate \
  --file validators/registry/fixtures/invalid/exception-no-expiry.yaml \
  --schema schemas/registry/exceptions.schema.json && no L1P1-E2 || ok L1P1-E2
python -m validators.registry.cli check-event-enum --platform registries/platform.yaml \
  --reject-unknown --probe not_a_real_event_type && no L1P1-E3 || ok L1P1-E3
python -m validators.registry.cli check-effective-dating \
  --files registries/people.yaml registries/roles.yaml && ok L1P1-E4 || no L1P1-E4
```

**STOP rule.** If `L1P1-E3` cannot run because the `event_type` enum has no agreed contents, do **not** invent event types — the taxonomy is spec §97.3 and is transcribed, never authored. Open `blocker/lane-1/L1-P1/E3`.

### L1-P2 — Product contract schema at `contract_version: 1`

Spec: §15.1 (the contract), §15.2 (two criticality fields, D4), §15.7 (conformance profiles), §21.1 (commitments block), §50.1 (budget band), §96.2 (pre-onboarding stub block), §38.1 (`ai_runtime_dependency`).

**Entry**

| id | Condition | Proof |
|---|---|---|
| L1P2-N1 | L1-P1 exited (all `PASS`) | Re-run L1-P1 gate |
| L1P2-N2 | Universal entry gate passed | §0.4 |

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L1P2-E1 | `schemas/product/product.schema.json` requires **both** criticality fields (`business.criticality`, `classification.reliability_criticality`) and rejects a contract carrying only one | — (D4) | Spec §6.1, §15.2; the two fields are "deliberately distinct" |
| L1P2-E2 | A product declaring an `ai_runtime_dependency` block with **no** evaluation suite under `verification/` fails validation | **AT-049** | — |
| L1P2-E3 | The schema admits the §15.7 conformance profiles and validates a non-`service` profile without change to the operating system | **AT-009** | — |
| L1P2-E4 | The Phase-2 pre-onboarding stub shape validates (identity + onboarding block only) and the full contract validates after completion; a breached onboarding deadline is representable | **AT-051** | — |
| L1P2-E5 | The commitments block and `infrastructure.monthly_budget_band` are required fields | **AT-050** (schema half); invariant 88 | — |

```bash
set -euo pipefail
# ---- L1-P2 EXIT GATE ----
V="python -m validators.registry.cli validate --schema schemas/product/product.schema.json --file"
$V validators/registry/fixtures/invalid/product-one-criticality.yaml && no L1P2-E1 || ok L1P2-E1
$V validators/registry/fixtures/invalid/product-ai-dep-no-evalsuite.yaml && no L1P2-E2 || ok L1P2-E2
for p in service client-app library batch-pipeline; do
  $V "validators/registry/fixtures/valid/product-profile-$p.yaml" || no L1P2-E3
done; ok L1P2-E3
$V validators/registry/fixtures/valid/product-preonboarding-stub.yaml \
  && $V validators/registry/fixtures/valid/product-onboarded-full.yaml && ok L1P2-E4 || no L1P2-E4
$V validators/registry/fixtures/invalid/product-no-budget-band.yaml && no L1P2-E5 || ok L1P2-E5
```

**STOP rule.** If the §15.7 profile list in the spec and the fixture set disagree, transcribe the spec and open `blocker/lane-1/L1-P2/E3`. Never add a profile.

### L1-P3 — Referential integrity, date rules and the two hard blockers

Spec: §99.2 subsystem B (verbatim scope), §10.2 (assignment rules), §12.4 (non-employee end dates), §44.2 (restore window), §21.4 (commitments conflict), §15.6 (the 24x7 blocker), §20.2 (dependency graph).

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L1P3-E1 | An assignment naming a non-existent or departed person fails validation | **AT-017** (precondition half); invariant 7 | — |
| L1P3-E2 | A non-employee entry with no `end_date` fails validation; an expired assignment fails validation | **AT-008**, **AT-018** (validation half); invariant 58 | — |
| L1P3-E3 | `restore_tested` older than the rolling 90-day window fails CI; a tighter per-product cadence is honoured, a looser one rejected | — | Invariant 4 verbatim; D5. No AT covers the *validator*; AT-035/AT-103 cover restore execution |
| L1P3-E4 | A product declaring an extended or 24x7 `coverage_window` not fully covered by the accepted windows of active rota members fails validation | **AT-047** | — |
| L1P3-E5 | A proposed commitment conflicting with the commitments/SLA registry is rejected before signature | — | Spec §21.4; §99.2 named tool `check-commitment CLI`. No AT. Evidence: the CLI rejects a seeded conflicting commitment in under 5 seconds |
| L1P3-E6 | A dependency naming a non-existent service fails validation | — | Invariant 64; §99.2 subsystem B verbatim |

```bash
set -euo pipefail
# ---- L1-P3 EXIT GATE ----
V="python -m validators.registry.cli validate --all --strict --registries registries/ --fixture"
$V invalid/assignment-departed-person.yaml   && no L1P3-E1 || ok L1P3-E1
$V invalid/contractor-no-end-date.yaml       && no L1P3-E2 || ok L1P3-E2
$V invalid/restore-tested-91-days.yaml       && no L1P3-E3 || ok L1P3-E3
$V invalid/24x7-rota-uncovered.yaml          && no L1P3-E4 || ok L1P3-E4
python -m validators.registry.cli check-commitment \
  --proposed validators/registry/fixtures/invalid/commitment-conflict.yaml \
  --registry registries/commitments.yaml && no L1P3-E5 || ok L1P3-E5
$V invalid/dependency-unknown-service.yaml   && no L1P3-E6 || ok L1P3-E6
```

**STOP rule.** `L1P3-E3` reads the window from `registries/` configuration, never from a literal 90 in code — invariant 4 permits tightening only. If you are about to hard-code 90, stop and open `blocker/lane-1/L1-P3/E3`.

### L1-P4 — Governance registry schemas and the invariant-classification check

Spec: §54.1 (exceptions), §55.1 (policies), §62.1 (tools), §68.1 (economics), §52.2 (os-health signal table), §58.2 (patterns), §59.3 (platform-roadmap), §66.2 (topology), §101 preamble (the enforcement classification), §103.14 (baselines).

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L1P4-E1 | Closing an exception and re-opening one for the same scope increments the renewal count; a fresh ID does not reset it | **AT-038**; invariant 77 | — |
| L1P4-E2 | A new policy starting at `Enforce` is rejected unless it is a critical security control | — | Invariant 78; §55.3. No AT. Evidence: negative fixture rejected |
| L1P4-E3 | Every control in the registry carries an explicit fail-closed / fail-open classification; an unclassified control is rejected | — | Invariant 80; §64.2; §99.2 subsystem B verbatim ("unclassified-control rejection"). No AT |
| L1P4-E4 | An assignment granting the `people-intelligence` capability to anyone other than the Founder fails validation | **AT-090** (validation half); invariant 106 | — |
| L1P4-E5 | Any attempt to configure an automated improvement plan, termination, promotion, compensation change or formal warning fails validation | **AT-071**; invariant 37 | — |
| L1P4-E6 | Banned surveillance measurements are absent from the schema and rejected if introduced | **AT-075**; invariants 96, 97, 98, 99 | — |
| L1P4-E7 | Every "sustained" threshold is configuration, refittable without code change | **AT-074** | — |
| L1P4-E8 | Every Section 103 measure has a recorded pre-Phase-1 baseline **or** is explicitly marked `unbaselined` | **AT-046**; §103.14 | — |
| L1P4-E9 | Control-plane CI fails when an invariant classified `mechanical` names no live check or AT id, when one classified `policy` names no live `policies.yaml` entry, or when any invariant carries no classification | — | Spec §101 preamble, verbatim, authored at G2. No AT covers it |
| L1P4-E10 | The removable governance artifacts can be removed and the delivery core still validates; `reconciler` and `exceptions.yaml` are **not** removable | **AT-034** | — |

```bash
set -euo pipefail
# ---- L1-P4 EXIT GATE ----
V="python -m validators.registry.cli validate --all --strict --fixture"
python -m validators.registry.cli exception-renewal-count \
  --closed EXC-0007 --reopened-scope 'org:write:contractor' | grep -qx 2 && ok L1P4-E1 || no L1P4-E1
$V invalid/policy-starts-at-enforce.yaml        && no L1P4-E2 || ok L1P4-E2
$V invalid/control-unclassified.yaml            && no L1P4-E3 || ok L1P4-E3
$V invalid/assignment-people-intelligence-delegate.yaml && no L1P4-E4 || ok L1P4-E4
$V invalid/automated-personnel-action.yaml      && no L1P4-E5 || ok L1P4-E5
$V invalid/surveillance-metric.yaml             && no L1P4-E6 || ok L1P4-E6
python -m validators.registry.cli thresholds-are-config --registries registries/ \
  && ok L1P4-E7 || no L1P4-E7
python -m validators.registry.cli baseline-coverage --section-103 --require-marked \
  && ok L1P4-E8 || no L1P4-E8
python -m validators.registry.cli invariant-classification --all-111 --require-live-target \
  && ok L1P4-E9 || no L1P4-E9
rm -rf /tmp/layer && git worktree add -f /tmp/layer HEAD >/dev/null && \
  rm -f /tmp/layer/registries/{os-health,policies,patterns,economics,platform-roadmap}.yaml && \
  (cd /tmp/layer && python -m validators.registry.cli validate --core-only --strict) \
  && ok L1P4-E10 || no L1P4-E10
```

**STOP rule.** `L1P4-E9` requires a live target per invariant. Where an invariant is `review-held`, the classification names the standing review and the chairing role — it is **not** a way to leave a target blank. If more than a handful land as `review-held`, stop and open `blocker/lane-1/L1-P4/E9` for L0: an invariant with no owner and no cadence is the failure §101's preamble exists to prevent.

### L1-P5 — Versioned contracts and multi-version validation

Spec: §60.2 (versioned contracts), §60.3 (compatibility states), §97.2 (`record_schema_version`), §84.4 (framework versioning rules), §15.5.

**Entry:** L1-P2, L1-P3, L1-P4 exited. Spec §98.3 places this in early hardening ("needs a reason to change a schema") — L0 confirms at least one real schema change exists before this phase starts.

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L1P5-E1 | Two contract versions validate simultaneously; no simultaneous fleet migration is required | **AT-025**; invariant 73 | — |
| L1P5-E2 | A removed KPI leaves historical periods intact under the old configuration | **AT-015** (schema half — full test needs subsystem P, D-EE-2) | — |
| L1P5-E3 | A framework version change is non-retroactive: the effective date is honoured and a mid-period change segments the period | **AT-078**, **AT-005** (effective-date half); invariant 61 | — |
| L1P5-E4 | An absent `record_schema_version` reads as version 1, and every record written from Phase 1 onward states it explicitly | — | Spec §97.2 verbatim. No AT |
| L1P5-E5 | A transitional product carries a named migration owner and a deadline; transitional never becomes permanent | — | Invariant 74; SIG-10. No AT. Evidence: a transitional entry with no owner or no deadline is rejected |

```bash
set -euo pipefail
# ---- L1-P5 EXIT GATE ----
python -m validators.registry.cli validate --contract-version 1 --all --strict \
  && python -m validators.registry.cli validate --contract-version 2 --all --strict \
  && ok L1P5-E1 || no L1P5-E1
python -m validators.registry.cli kpi-removal-replay \
  --removed-kpi KPI-DEV-04 --period 2026-Q1 --expect-preserved && ok L1P5-E2 || no L1P5-E2
python -m validators.registry.cli framework-version-replay \
  --effective 2026-07-01 --period 2026-Q3 --expect-segments 2 && ok L1P5-E3 || no L1P5-E3
python -m validators.registry.cli record-version-default \
  --fixture validators/registry/fixtures/valid/record-no-version.yaml --expect 1 \
  && ok L1P5-E4 || no L1P5-E4
python -m validators.registry.cli validate --fixture invalid/transitional-no-owner.yaml \
  && no L1P5-E5 || ok L1P5-E5
```

**STOP rule.** If `L1P5-E1` cannot pass because only one contract version exists, the phase has not been entered legitimately — spec §98.3 gates it on a real reason to change a schema. Return the branch and tell L0.

---

## 4. Lane L4 — Records, Events & Metrics (subsystems I, N)

Owns **all** of `control-plane-records`, plus `schemas/records/**`, `metrics/**`, `tools/records/**` in `control-plane`. L4 merges second in the train.

### L4-P1 — Records repository bootstrap and the append-only ruleset

Spec: §97.1 (write path split by author and repository), D89 (records live in their own repository; no machine bypass actor on control-plane), D107 (append-only enforced, not asserted), §40.1 (fifth secrets tier), invariant 47.

**Entry**

| id | Condition | Proof |
|---|---|---|
| L4P1-N1 | `control-plane-records` exists and is empty of protection *review* rules | `gh api "repos/$ORG/control-plane-records" --jq .name` |
| L4P1-N2 | The records-writer GitHub App installation is scoped to that repository alone | `gh api "orgs/$ORG/installations" --jq '.installations[] \| {app:.app_slug,repos:.repository_selection}'` |

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L4P1-E1 | A ruleset with **no bypass actor** blocks force-push and deletion on `control-plane-records` while permitting fast-forward commits | — | D107 verbatim. No AT. Evidence: a force-push attempt is refused server-side |
| L4P1-E1b | A real force-push attempt against `control-plane-records` is refused server-side (behavioural confirmation of L4P1-E1, not a separate ruleset-config check) | — | D107 verbatim. No AT |
| L4P1-E2 | An unsigned or foreign-signed commit on the records repository is detectable as Blocking drift | — | D107; invariant 47. Detection lands at L3-P3 |
| L4P1-E3 | The records-writer credential reaches **no registry at all** — a write to `control-plane` from it is refused | **AT-110** (precondition half); D89 | — |
| L4P1-E4 | Directory-per-item layout only: `records/<store>/` and `events/<date>/`, one file per item, no shared append target | — | Spec §97.3 verbatim; PARTITION rule 3. No AT. Evidence: no file in the repo is written twice by two workflows |

```bash
set -euo pipefail
# ---- L4-P1 EXIT GATE ----
for id in $(gh api "/repos/$ORG/control-plane-records/rulesets" --jq '.[].id'); do
  gh api "/repos/$ORG/control-plane-records/rulesets/$id"
done | jq -s '[.[] | select(.target=="branch") | {by: (.bypass_actors // [] | length),
   fp: ([.rules[]?.type] | index("non_fast_forward")),
   del: ([.rules[]?.type] | index("deletion"))}]' \
 | python -c "import json,sys;r=json.load(sys.stdin);sys.exit(0 if any(x['by']==0 and x['fp'] is not None and x['del'] is not None for x in r) else 1)" \
 && ok L4P1-E1 || no L4P1-E1
git -C "$CPR" push --force origin HEAD:refs/heads/main 2>&1 | grep -qi 'protected\|denied\|rejected' \
  && ok L4P1-E1b || no L4P1-E1b
git -C "$CPR" log -20 --format='%H %G?' | grep -qv ' G$' && no L4P1-E2 || ok L4P1-E2
GH_TOKEN="$RECORDS_WRITER_TOKEN" gh api -X PUT "repos/$ORG/control-plane/contents/probe.txt" \
  -f message=probe -f content=$(printf probe|base64) 2>&1 | grep -qi 'not accessible\|403' \
  && ok L4P1-E3 || no L4P1-E3
python -m tools.records.cli check-layout --repo "$CPR" --one-file-per-item \
  && ok L4P1-E4 || no L4P1-E4
```

**SELF-VERIFY L4P1-E1 (negative test — DF-0139).** Confirm the two-step check correctly detects a bypass actor before relying on it. Seed a temporary ruleset on `control-plane-records` with a machine bypass actor, run the check, assert the bypass count is non-zero, then delete the test ruleset:

```bash
set -euo pipefail
# Seed a ruleset with one bypass actor on control-plane-records
TEST_RS=$(gh api -X POST "/repos/$ORG/control-plane-records/rulesets" --input - --jq '.id' <<'JSON'
{
  "name": "drill-bypass-test",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [{"actor_id": 1, "actor_type": "Integration", "bypass_mode": "always"}],
  "conditions": {"ref_name": {"include": ["refs/heads/drill-*"], "exclude": []}},
  "rules": []
}
JSON
)
BYPASS_COUNT=$(for id in $(gh api "/repos/$ORG/control-plane-records/rulesets" --jq '.[].id'); do
  gh api "/repos/$ORG/control-plane-records/rulesets/$id"
done | jq -s '[.[] | .bypass_actors // [] | .[]] | length')
[ "$BYPASS_COUNT" -gt 0 ] \
  && echo "NEGATIVE TEST PASS: bypass count $BYPASS_COUNT (non-zero)" \
  || { echo "NEGATIVE TEST FAIL: bypass count 0 with seeded bypass actor — bypass_actors not read from individual endpoint"; exit 1; }
gh api -X DELETE "/repos/$ORG/control-plane-records/rulesets/$TEST_RS"
```

**Asserts:** `$BYPASS_COUNT` must be ≥ 1. A count of 0 confirms the list-endpoint bug is still present — `bypass_actors` is absent on summary objects and `// []` is resolving to empty rather than to the seeded actor.

**STOP rule.** Never obtain `RECORDS_WRITER_TOKEN` by copying it into a file, a shell history line you commit, or a workflow input. If you cannot run `L4P1-E3` without handling the token in plaintext, stop and open `blocker/lane-4/L4-P1/E3` — spec §40.1 and invariant 84 are absolute here.

### L4-P2 — Record store schemas and the binding event envelope

Spec: §97.2 (the store table), §97.3 (event envelope, every field mandatory), D80 (support clock anchored to received timestamp), §51.1 + AT-105 (deletion-request four timestamps).

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L4P2-E1 | A schema exists for every store in the §97.2 table; each requires `record_schema_version`, `id`, `product`, `timestamp` | — | Spec §97.2 verbatim. No AT. Evidence: store-list equality against the spec table |
| L4P2-E2 | An event missing any envelope field is rejected at write time | — | Spec §97.3 verbatim ("rejected at write time"). No AT |
| L4P2-E3 | A deletion-request record carries `requested`, `verified`, `executed`, `confirmed`, the named executor and the subprocessor propagation checklist | **AT-105** (record half) | — |
| L4P2-E4 | A support record carries `detection_source` and anchors first response to the message received timestamp | **AT-104** (record half); D80 | — |
| L4P2-E5 | Records never edit in place — a correction is a follow-up record and the validator rejects an in-place edit | — | Invariant 47; §97.2 verbatim. No AT |

```bash
set -euo pipefail
# ---- L4-P2 EXIT GATE ----
python -m tools.records.cli store-coverage --spec-stores contracts/l4-records.yaml \
  --schemas schemas/records/ --require-common-fields && ok L4P2-E1 || no L4P2-E1
python -m tools.records.cli validate-event \
  --file schemas/records/fixtures/invalid/event-missing-actor.yaml && no L4P2-E2 || ok L4P2-E2
python -m tools.records.cli validate-record --store deletion-requests \
  --file schemas/records/fixtures/invalid/deletion-three-timestamps.yaml && no L4P2-E3 || ok L4P2-E3
python -m tools.records.cli validate-record --store support \
  --file schemas/records/fixtures/valid/support-received-anchored.yaml && ok L4P2-E4 || no L4P2-E4
python -m tools.records.cli detect-in-place-edit --repo "$CPR" --since 30.days \
  && ok L4P2-E5 || no L4P2-E5
```

**STOP rule.** `contracts/l4-records.yaml` is the transcription of the §97.2 store table and is L0-owned. If a store you need is absent from it, that is a Contract Change Request — never add a store schema whose store is not in the contract.

### L4-P3 — Record and event writer tools, and write-freshness

Spec: §97.2 (`RECORD-VERIFICATION-RESULT` is the single pattern by which a human result reaches the machine), §97.2 write-freshness paragraph, §99.2 named tools (`record-decision CLI`, support email-ingest hook), §22.2.

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L4P3-E1 | `RECORD-VERIFICATION-RESULT` is the only path by which a manual result reaches a store — a hand-edited record file is rejected | — | Spec §97.2 verbatim ("nobody edits a record file by hand to report a result"). No AT |
| L4P3-E2 | `record-decision` turns the decision template into a validated record in `records/decisions/` or `records/decisions/pending/`, usable from a phone | — | Spec §99.2 named tools. No AT. Evidence: CLI run from a minimal input produces a schema-valid record |
| L4P3-E3 | Every store declares an expected maximum inter-write interval in `os-health.yaml`; a store past its interval is Amber, and Blocking for `events/`, `records/deployments/`, `records/uat/` | **AT-032** (self-observability half) | — |
| L4P3-E4 | An inbound support email becomes a structured board item with the first-response clock started, and the record closes only when the customer loop is closed | **AT-104**, **AT-048** | — |

```bash
set -euo pipefail
# ---- L4-P3 EXIT GATE ----
python -m tools.records.cli reject-hand-edit --repo "$CPR" \
  --probe records/uat/2026-01-01-probe.yaml && no L4P3-E1 || ok L4P3-E1
python -m tools.records.cli record-decision --title "probe" --owner founder --dry-run \
  --emit /tmp/dec.yaml && python -m tools.records.cli validate-record --store decisions \
  --file /tmp/dec.yaml && ok L4P3-E2 || no L4P3-E2
python -m metrics.cli write-freshness --config registries/os-health.yaml \
  --blocking events,records/deployments,records/uat --format json > /tmp/fresh.json \
  && python -c "import json,sys;d=json.load(open('/tmp/fresh.json'));sys.exit(0 if d['declared_for_all_stores'] else 1)" \
  && ok L4P3-E3 || no L4P3-E3
python -m tools.records.cli support-ingest --fixture schemas/records/fixtures/valid/support-email.eml \
  --expect-clock-anchor received --expect-open-until customer_reply && ok L4P3-E4 || no L4P3-E4
```

**STOP rule.** If `L4P3-E3` finds a store with no declared interval, do not choose one — the interval is a calibrated value and belongs in `os-health.yaml`, an L1-owned file. Open a Contract Change Request.

### L4-P4 — Metrics pipeline (DevLake, Prometheus, Scorecard)

Spec: §99.2 subsystem I, §41.2 (the three required endpoints), §50.2 (cost anomaly), §42.2 (detection latency), invariant 46 (derived data computed, never hand-maintained), invariant 49 (every metric has an owner and a defined response, or it is deleted).

**Entry**

| id | Condition | Proof |
|---|---|---|
| L4P4-N1 | L4-P2 and L4-P3 exited | Re-run their gates |
| L4P4-N2 | **D-EE-4 item 4 recorded** — DevLake field coverage confirmed by L0 | `python -c "import yaml;print(yaml.safe_load(open('contracts/estate.yaml'))['devlake_field_coverage'])"` |
| L4P4-N3 | Ops VM reachable and DevLake/Prometheus/Grafana running (L5-P2 exited) | `curl -fsS "$OPSVM/api/health"` |

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L4P4-E1 | Every dashboard metric names the record store it derives from; a metric that cannot name its store does not ship | — | Spec §97.1 verbatim; invariant 46. No AT |
| L4P4-E2 | Every metric has an owner and a defined response, or it is absent | — | Invariant 49. No AT. Evidence: the metric register has zero ownerless rows |
| L4P4-E3 | Spend outside a product's `infrastructure.monthly_budget_band` raises a Red health signal (SIG-35) classifiable as a cost incident with a named owner | **AT-050** | — |
| L4P4-E4 | Detection-to-response latency is recorded per incident | **AT-047** (measurement half) | — |
| L4P4-E5 | Prometheus scrapes `/health`, `/version`, `/metrics` on every onboarded product; Scorecard runs on schedule with drop detection | — | Spec §41.2, §99.2 subsystem I. No AT. Evidence: three targets `up == 1` per product |

```bash
set -euo pipefail
# ---- L4-P4 EXIT GATE ----
python -m metrics.cli metric-register --require-store --require-owner --require-response \
  --format json > /tmp/mr.json
python -c "import json,sys;d=json.load(open('/tmp/mr.json'));sys.exit(0 if d['metrics_without_store']==0 else 1)" \
  && ok L4P4-E1 || no L4P4-E1
python -c "import json,sys;d=json.load(open('/tmp/mr.json'));sys.exit(0 if d['metrics_without_owner']==0 and d['metrics_without_response']==0 else 1)" \
  && ok L4P4-E2 || no L4P4-E2
python -m metrics.cli cost-anomaly-probe --product probe-product --spend-multiplier 2.0 \
  --expect-signal SIG-35 --expect-severity red --expect-owner-named && ok L4P4-E3 || no L4P4-E3
python -m metrics.cli detection-latency --store incidents --require-per-incident \
  && ok L4P4-E4 || no L4P4-E4
python -m metrics.cli scrape-coverage --endpoints /health,/version,/metrics --all-onboarded \
  --require-up \
  && bash tools/records/checks/L4-P5-20.sh \
  && ok L4P4-E5 || no L4P4-E5
```

**STOP rule.** If a required §79 measure has no DevLake field and no bespoke computation recorded under D-EE-4 item 4, mark it **Not yet instrumented** (AT-087's rule) and stop. Never invent a proxy — invariant 87's counterpart AT-087 exists precisely to catch that.

### L4-P5 — Attention ledger, ready-queue-miss detector, board conventions

Spec: §97.4 (attention-hour derivation), §97.5 (ready-queue-miss recording), §29.1–§29.3 (boards, horizons, Ready-to-Execute), §99.2 subsystem N, D79 (self-report staged to Founder and Team Lead until a named consumer activates).

**Entry**

| id | Condition | Proof |
|---|---|---|
| L4P5-N1 | L4-P4 exited | Re-run its gate |
| L4P5-N2 | **D-EE-4 items 1 and 7 recorded** — attention classifier rules and initial calibration values exist as configuration | `python -m validators.registry.cli validate --file registries/os-health.yaml --require attention_classifier` |

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L4P5-E1 | Machine-derived attention flows for every person at zero collection cost; the weekly banded self-report is armed for Founder and Team Lead **only** until a named consumer activates | — (D79; §98.5 G3 exit) | No AT. Evidence: the ledger reports a per-person machine-derived total and the self-report scope equals `{founder, team_lead}` |
| L4P5-E2 | Attention hours, utilisation, PLU and output volume are never emitted as individual performance evidence | — | Invariant 90; D6. No AT at this layer (AT-061 lives in subsystem P). Evidence: the ledger's export refuses a per-person performance projection |
| L4P5-E3 | A ready-queue miss is recorded automatically per §97.5 | — | Invariant 15; §29.4. No AT. Evidence: a seeded miss appears as an event of the declared type |
| L4P5-E4 | Boards conform: one project per product plus portfolio aggregate, **or** the single-Project fallback of §29 | — | Spec §98.2 Phase 1, §99.5 Boards. No AT. Evidence: the board topology check reports one of the two sanctioned shapes and no third |
| L4P5-E5 | A lifecycle decision can be evidenced with actual attention-hour data | **AT-044** | — |

```bash
set -euo pipefail
# ---- L4-P5 EXIT GATE ----
python -m metrics.cli attention-ledger --scope machine-derived --all-people --format json \
  > /tmp/att.json && python -c "import json,sys;d=json.load(open('/tmp/att.json'));sys.exit(0 if d['people_covered']==d['people_total'] and set(d['self_report_scope'])=={'founder','team_lead'} else 1)" \
  && ok L4P5-E1 || no L4P5-E1
python -m metrics.cli attention-ledger --project-per-person-performance 2>&1 \
  | grep -qi 'refused\|not permitted' && ok L4P5-E2 || no L4P5-E2
python -m metrics.cli ready-queue-miss --replay --fixture metrics/fixtures/rqm-seed.json \
  --expect-events 1 && ok L4P5-E3 || no L4P5-E3
python -m metrics.cli board-topology --expect-one-of per-product-plus-aggregate,single-project \
  && ok L4P5-E4 || no L4P5-E4
python -m metrics.cli evidence-pack --decision-type lifecycle --product probe-product \
  --require attention_hours && ok L4P5-E5 || no L4P5-E5
```

**STOP rule.** `L4P5-E1` is calendar-gated downstream: spec §98.5 G5 needs "at least two quarters of G3 attention data". Building the ledger is in scope; producing a forecast from it is not. If you are asked to forecast, stop — that is subsystem P / G5, and it is not yours.

---

## 5. Lane L2 — Pipeline & Evidence (subsystems E, F)

Owns `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**`. L2 merges third.

> **Note on the lane-guard.** The lane-guard *check* is an L2 workflow (`.github/workflows/lane-guard.yml`), but the *ownership map* it reads is `contracts/lane-paths.yaml` (L0) and the *review routing* is `CODEOWNERS` (L0). The guard logic is inline in the workflow's `run:` block — there is no `.github/scripts/**` path in the partition, so nothing may be placed there.

### L2-P1 — Control-plane CI and the lane-guard

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L2P1-E1 | A PR touching a foreign path FAILS the lane-guard check | — | PARTITION rule 1, verbatim. No AT. Evidence: a deliberate foreign-path PR is failed |
| L2P1-E2 | Control-plane CI fails a repository missing any required file of §33.1, `AGENTS.md` included | — | Spec §33.1 verbatim ("Required-file presence is checked, not assumed"). No AT |
| L2P1-E3 | Contract, registry and assignment validation run on every push | — | Spec §33.2. No AT. Evidence: the check contexts appear on a real run |
| L2P1-E4 | The invariant-classification check runs in control-plane CI | — | Spec §101 preamble. Pairs with `L1P4-E9` |

```bash
set -euo pipefail
# ---- L2-P1 EXIT GATE ----
gh pr create --repo "$ORG/control-plane" --draft --base integration \
  --head lane/2/p1-guard-negative --title "negative: foreign path" --body "expected to fail" >/dev/null
sleep 30
gh pr checks lane/2/p1-guard-negative --repo "$ORG/control-plane" --json name,state \
  --jq '.[]|select(.name=="lane-guard")|.state' | grep -qx FAILURE && ok L2P1-E1 || no L2P1-E1
python - <<'PY' && ok L2P1-E2 || no L2P1-E2
import sys,subprocess
need=[".env.example","docker-compose.dev.yml","Makefile","verification","AGENTS.md"]
out=subprocess.run(["gh","workflow","view","required-files.yml","--repo",
  __import__("os").environ["ORG"]+"/control-plane"],capture_output=True,text=True).stdout
sys.exit(0 if all(n in out for n in need) else 1)
PY
gh api "repos/$ORG/control-plane/commits/integration/check-runs" \
  --jq '[.check_runs[].name]' | grep -q 'contract-validate' && ok L2P1-E3 || no L2P1-E3
gh api "repos/$ORG/control-plane/commits/integration/check-runs" \
  --jq '[.check_runs[].name]' | grep -q 'invariant-classification' && ok L2P1-E4 || no L2P1-E4
```

**STOP rule.** Close the negative PR from `L2P1-E1` immediately after the check fails. Leaving it open blocks the merge train.

### L2-P2 — The reusable `ci.yml`

Spec: §33.2 (what every push triggers), §48.1–§48.2 (pinning, delta-gated licence scan), §30.2 + §33.2 (slopsquat at execute time), §33.1 (parity), §31 (verification contract), §38.3 (eval suite where declared).

**Entry**

| id | Condition | Proof |
|---|---|---|
| L2P2-N1 | L2-P1 exited; L1-P2 merged to `integration` | `git -C "$CP" log origin/integration --oneline -- schemas/product/ \| head -1` non-empty |
| L2P2-N2 | **D-EE-4 item 2 recorded** — the `make parity` declaration format exists | `test -f contracts/environment-schema.yaml` |

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L2P2-E1 | Security and licence findings are **delta-gated** — fail on new findings only | — | Spec §33.2 verbatim. No AT. Evidence: a seeded legacy finding does not fail; a seeded new one does |
| L2P2-E2 | The slopsquat legitimacy check runs against lockfile and manifest diffs at execute time | — | Spec §33.2, §30.2. No AT. Evidence: a seeded non-existent package fails the run |
| L2P2-E3 | A product declaring `ai_runtime_dependency` without an eval suite fails CI, and a pin change cannot merge without the suite passing | **AT-049** | — |
| L2P2-E4 | `make parity` and the CI parity job detect env-var, dependency, runtime-version and secret-reference divergence; a parity violation on a production path is a blocking failure | **AT-009** (interface half) | — |
| L2P2-E5 | Third-party Actions are pinned to full commit SHAs; reusable workflows are consumed by pinned tag | — | Invariant 85. No AT. Evidence: zero unpinned refs across all workflow files |
| L2P2-E6 | The `renovate-path-guard` sits in a ruleset with **no bypass actor**, and fails any Renovate PR whose diff leaves declared manifest/lockfile paths **or** whose branch carries a commit authored by another identity | — | Spec §33.2 verbatim; D89. No AT. Evidence: both negative cases fail the guard |

```bash
set -euo pipefail
# ---- L2-P2 EXIT GATE ----
gh workflow run ci.yml --repo "$ORG/product-template" -f scenario=legacy-finding && sleep 60 && \
gh run list --repo "$ORG/product-template" --workflow ci.yml --limit 1 --json conclusion \
  --jq '.[0].conclusion' | grep -qx success && ok L2P2-E1a || no L2P2-E1a
gh workflow run ci.yml --repo "$ORG/product-template" -f scenario=new-finding && sleep 60 && \
gh run list --repo "$ORG/product-template" --workflow ci.yml --limit 1 --json conclusion \
  --jq '.[0].conclusion' | grep -qx failure && ok L2P2-E1b || no L2P2-E1b
ok L2P2-E1
gh workflow run ci.yml --repo "$ORG/product-template" -f scenario=slopsquat && sleep 60 && \
gh run list --repo "$ORG/product-template" --workflow ci.yml --limit 1 --json conclusion \
  --jq '.[0].conclusion' | grep -qx failure && ok L2P2-E2 || no L2P2-E2
gh workflow run ci.yml --repo "$ORG/product-template" -f scenario=ai-dep-no-eval && sleep 60 && \
gh run list --repo "$ORG/product-template" --workflow ci.yml --limit 1 --json conclusion \
  --jq '.[0].conclusion' | grep -qx failure && ok L2P2-E3 || no L2P2-E3
make -C "$HOME/src/product-template" parity && ok L2P2-E4 || no L2P2-E4
grep -rhoE 'uses: [^ ]+@[^ ]+' .github/workflows templates/workflows \
  | grep -vE '@[0-9a-f]{40}$|@v[0-9]+\.[0-9]+\.[0-9]+$' > /tmp/unpinned.txt || true
test ! -s /tmp/unpinned.txt && ok L2P2-E5 || { cat /tmp/unpinned.txt; no L2P2-E5; }
for id in $(gh api "/repos/$ORG/control-plane/rulesets" --jq '.[].id'); do
  gh api "/repos/$ORG/control-plane/rulesets/$id"
done | jq -s '[.[] | select(any(.rules[]?; .type=="required_status_checks" and
   (.parameters.required_status_checks[]?.context=="renovate-path-guard"))) |
   (.bypass_actors // [] | length)]' \
 | grep -qx '\[0\]' && ok L2P2-E6 || no L2P2-E6
```

**SELF-VERIFY L2P2-E6 (negative test — DF-0139).** Confirm the two-step check can detect a bypass actor on a renovate-path-guard ruleset before relying on it. Seed a temporary ruleset on `control-plane` that includes the `required_status_checks` rule for `renovate-path-guard` and carries a machine bypass actor, run the check, assert the bypass count is non-zero, then delete the test ruleset:

```bash
set -euo pipefail
# Seed a renovate-path-guard ruleset with one bypass actor
TEST_RS=$(gh api -X POST "/repos/$ORG/control-plane/rulesets" --input - --jq '.id' <<'JSON'
{
  "name": "drill-bypass-rsc-test",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [{"actor_id": 1, "actor_type": "Integration", "bypass_mode": "always"}],
  "conditions": {"ref_name": {"include": ["refs/heads/drill-*"], "exclude": []}},
  "rules": [{"type": "required_status_checks", "parameters": {"required_status_checks": [{"context": "renovate-path-guard", "integration_id": 0}], "strict_required_status_checks_policy": false}}]
}
JSON
)
RESULT=$(for id in $(gh api "/repos/$ORG/control-plane/rulesets" --jq '.[].id'); do
  gh api "/repos/$ORG/control-plane/rulesets/$id"
done | jq -s '[.[] | select(any(.rules[]?; .type=="required_status_checks" and
   (.parameters.required_status_checks[]?.context=="renovate-path-guard"))) |
   (.bypass_actors // [] | length)]')
echo "$RESULT" | grep -qx '\[0\]' \
  && { echo "NEGATIVE TEST FAIL: gate matched [0] with a seeded bypass actor — bypass_actors not read from individual endpoint"; exit 1; } \
  || echo "NEGATIVE TEST PASS: gate did not match [0] (bypass actor detected as expected)"
gh api -X DELETE "/repos/$ORG/control-plane/rulesets/$TEST_RS"
```

**Asserts:** the gate must NOT match `[0]` (i.e., `grep -qx '\[0\]'` must fail). A match of `[0]` with a seeded bypass actor means `bypass_actors` is still being read from the summary list endpoint where the field is absent.

**STOP rule.** If `contracts/environment-schema.yaml` does not exist, `L2P2-E4` is unauthorable — spec §99.3 item 2 leaves the format design-open and it is L0's to define. Do not invent a parity format. Open `blocker/lane-2/L2-P2/E4`.

### L2-P3 — `build.yml`: immutable artifact, digest, SBOM

Spec: §32 (evidence chain items 5 and 11), §33.4 (artifacts and environments), §48.3 (SBOM per artifact), invariants 22 and 23.

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L2P3-E1 | The build emits a digest and records it beside the artifact | — | Spec §32 item 5. No AT. Evidence: the deployment record carries a digest that matches the registry |
| L2P3-E2 | Every built artifact emits an SBOM recorded beside its digest | — | Spec §33.2, §48.3. No AT |
| L2P3-E3 | No path exists that rebuilds an artifact to work around registry unavailability | — | Invariant 23. No AT. Evidence: the workflow has no rebuild-on-registry-error branch |

```bash
set -euo pipefail
# ---- L2-P3 EXIT GATE ----
gh workflow run build.yml --repo "$ORG/product-template" && sleep 120
RUN=$(gh run list --repo "$ORG/product-template" --workflow build.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run view "$RUN" --repo "$ORG/product-template" --json jobs --jq '.jobs[].steps[].name' \
  | grep -q 'record digest' && ok L2P3-E1 || no L2P3-E1
gh run download "$RUN" --repo "$ORG/product-template" --name sbom --dir /tmp/sbom \
  && test -s /tmp/sbom/*.json && ok L2P3-E2 || no L2P3-E2
grep -riE 'rebuild|retry-build' templates/workflows/build.yml && no L2P3-E3 || ok L2P3-E3
```

**STOP rule.** If a retry mechanism is needed for a flaky registry, it retries the **push of the same digest**, never a rebuild. Invariant 22 is not negotiable. Open a blocker rather than reinterpreting it.

### L2-P4 — `deploy-staging.yml`, `deploy-production.yml`, rollback, Friday freeze

Spec: §27.1–§27.2 (production approval routing, workflow-identity gate), D73, §34.1 (ship redefined), §34.2 (Friday freeze), §32 (the digest invariant), §97.1 (time resolves against the declared working calendar, never runner-local time), invariants 9, 12, 22, 27.

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L2P4-E1 | The deploy fails closed when the recorded approving identity equals the deploying identity | — (D73) | Spec §98.2 Phase 6 completion check verbatim. No AT id; this is the mechanism AT-103 and the evidence chain rely on |
| L2P4-E2 | CI rejects a production deployment whose requested digest differs from the digest that passed staging verification | — | Spec §32 verbatim; invariant 22. No AT |
| L2P4-E3 | The Friday-freeze gate resolves against the declared working calendar and operating timezone, never the runner's local time | — | Spec §97.1 verbatim ("which is how a Friday-freeze gate silently admits the deployments it exists to prevent"). No AT |
| L2P4-E4 | A rollback executes with no prior approval during a SEV-1, and the deployment-record and event writes are **required, failing steps** | — | Invariant 27; §97.2 verbatim. No AT |
| L2P4-E5 | A documented manual production-rollback path exists and has been executed once | **AT-029** | — |

```bash
set -euo pipefail
# ---- L2-P4 EXIT GATE ----
gh workflow run deploy-production.yml --repo "$ORG/product-template" \
  -f approver=self -f digest=sha256:deadbeef && sleep 60
gh run list --repo "$ORG/product-template" --workflow deploy-production.yml --limit 1 \
  --json conclusion --jq '.[0].conclusion' | grep -qx failure && ok L2P4-E1 || no L2P4-E1
gh workflow run deploy-production.yml --repo "$ORG/product-template" \
  -f approver=other -f digest=sha256:notthestagingone && sleep 60
gh run list --repo "$ORG/product-template" --workflow deploy-production.yml --limit 1 \
  --json conclusion --jq '.[0].conclusion' | grep -qx failure && ok L2P4-E2 || no L2P4-E2
grep -q 'working_calendar' templates/workflows/deploy-production.yml \
  && ! grep -qE 'date \+%u|TZ=UTC.*friday' templates/workflows/deploy-production.yml \
  && ok L2P4-E3 || no L2P4-E3
python -m tools.evidence.cli check-required-steps --workflow templates/workflows/deploy-production.yml \
  --require record-deployment,append-event --must-fail-run-on-error && ok L2P4-E4 || no L2P4-E4
test -f docs/runbooks/manual-production-rollback.md \
  && python -m tools.evidence.cli drill-recorded --drill manual-rollback --within 90.days \
  && ok L2P4-E5 || no L2P4-E5
```

**STOP rule.** `L2P4-E1` and `L2P4-E2` are negative tests run against `product-template`, never against a live product. If you cannot run them against the template, stop — do not "verify by reading the YAML".

### L2-P5 — Evidence chain store and query (`verify-digest-chain`)

Spec: §32 (the eleven questions and their sources), §99.2 subsystem F, §99.2 named tool `verify-digest-chain`, §46.1 (run on demand as the outage-recovery gate).

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L2P5-E1 | All eleven questions of §32 are answerable for one real deployment from GitHub, Actions and Grafana alone | — | Spec §98.2 Phase 6 completion check verbatim. **No AT covers the evidence chain directly**; the standing evidence is an eleven-of-eleven answer for a named production deployment, re-run on demand |
| L2P5-E2 | `verify-digest-chain` runs as a scheduled sweep; any `/version` mismatch is raised as a P0 investigation | — | Spec §99.2 subsystem F ("100%; any mismatch is a P0 investigation"). No AT |
| L2P5-E3 | For a non-`service` conformance profile, items 10 and 11 are substituted by that profile's declared equivalent evidence and the chain still closes | **AT-009** (profile half) | — |

```bash
set -euo pipefail
# ---- L2-P5 EXIT GATE ----
python -m tools.evidence.cli chain --product probe-product --deployment latest --format json \
  > /tmp/chain.json
python -c "import json,sys;d=json.load(open('/tmp/chain.json'));sys.exit(0 if d['answered']==11 else 1)" \
  && ok L2P5-E1 || no L2P5-E1
python -m tools.evidence.cli verify-digest-chain --all-products --format json > /tmp/vdc.json
python -c "import json,sys;d=json.load(open('/tmp/vdc.json'));sys.exit(0 if d['mismatches']==0 and d['scheduled'] else 1)" \
  && ok L2P5-E2 || no L2P5-E2
python -m tools.evidence.cli chain --product probe-client-app --profile client-app \
  --format json | python -c "import json,sys;d=json.load(sys.stdin);sys.exit(0 if d['answered']==11 else 1)" \
  && ok L2P5-E3 || no L2P5-E3
```

**STOP rule.** If a question cannot be answered because a record was never written, that is not an evidence-chain bug — it is a missing required workflow step (see `L2P4-E4`). Fix it there, not by hand-writing the record.

### L2-P6 — `migrate`, `restore-test`, `restore-production`, `org-export`, `background-queue`

Spec: §34.3–§34.4 (migrations and the seven failure cases), §44 (backup, restore testing, the production-restore workflow), §45.3 (organisation export, D80), §37 (background queue), AT-103, AT-105, AT-035, invariants 3 and 4.

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L2P6-E1 | Every product declaring a `recovery:` block carries `restore-production.yml` generated from the template; it runs end to end with an exceptional-authorisation record and **without any credential handed to or typed by a human** | **AT-103** | — |
| L2P6-E2 | The scheduled organisation export restores to an independent environment, each data class through its own recorded mechanism, Projects boards via their GraphQL dump | **AT-035**; D80 | — |
| L2P6-E3 | A restore test is recorded and enters the rolling 90-day rotation; an untested backup counts as no backup | — | Invariants 3 and 4. No AT for the *scheduler*; evidence is a `records/restore-tests/` entry per product inside the window |
| L2P6-E4 | A deletion request executes through the runbook via CI with the four timestamps, the named executor and the subprocessor checklist, inside `deletion_sla_days` | **AT-105** | — |
| L2P6-E5 | Each of the seven migration failure cases has defined behaviour exercised by a test | — | Spec §34.4. No AT. Evidence: seven named test cases, all passing |

```bash
set -euo pipefail
# ---- L2-P6 EXIT GATE ----
python -m tools.evidence.cli restore-production-dryrun --product probe-product \
  --require-auth-record --forbid-human-credential && ok L2P6-E1 || no L2P6-E1
gh workflow run org-export.yml --repo "$ORG/control-plane" -f mode=restore-verify && sleep 300
gh run list --repo "$ORG/control-plane" --workflow org-export.yml --limit 1 --json conclusion \
  --jq '.[0].conclusion' | grep -qx success && ok L2P6-E2 || no L2P6-E2
python -m tools.evidence.cli restore-rotation --window 90 --all-products --require-record \
  && ok L2P6-E3 || no L2P6-E3
python -m tools.evidence.cli deletion-runbook --dry-run --product probe-product \
  --require-timestamps requested,verified,executed,confirmed --require-subprocessor-checklist \
  && ok L2P6-E4 || no L2P6-E4
pytest templates/workflows/tests/test_migration_failure_cases.py -q \
  && test "$(pytest templates/workflows/tests/test_migration_failure_cases.py --collect-only -q | grep -c '::')" = 7 \
  && ok L2P6-E5 || no L2P6-E5
```

**STOP rule.** `L2P6-E1` is `--dry-run` in this lane. The real run is an L0 gate (`G-F6`) executed against a real product with a real exceptional-authorisation record. Never execute a production restore from a lane branch.

---

## 6. Lane L3 — Reconciler & Provisioning (subsystems C, D)

Owns `reconciler/**`, `tools/provision/**`, `validators/drift/**`. L3 merges fourth.

### L3-P1 — Reconciliation v0: detect and block only, plus the seeded canary

Spec: §98.2 Phase 3 (verbatim scope: "detect and block only: Teams versus registries, expiry revocation, protection drift, and orphan detection at blocking severity"), §99.4 item 6, §53.2 Levels 1 and 4, §53.3 (the auto-repair rule), AT-102, EC-109.

**Entry**

| id | Condition | Proof |
|---|---|---|
| L3P1-N1 | L1-P1…L1-P3 merged to `integration` | `python -m validators.registry.cli validate --all --strict` on `integration` |
| L3P1-N2 | L5-P1 merged (the access model the reconciler diffs against) | `test -f access/permission-model.yaml` on `integration` |
| L3P1-N3 | Universal entry gate passed | §0.4 |

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L3P1-E1 | Every run finds the deliberately seeded canary drift; a run reporting zero findings **including** the canary is a FAILED run, raises SIG-13 and triggers the gap procedure | **AT-102**; EC-109 | — |
| L3P1-E2 | Teams-versus-registries divergence is detected and blocked | — | Spec §98.2 Phase 3; invariant 44. No AT id; nearest downstream is AT-002/AT-017 |
| L3P1-E3 | A temporary access exception past expiry is revoked with **no human action** | **AT-036**, **AT-018**; invariant 58 | — |
| L3P1-E4 | A bootstrap-mode gate exception carries an expiry and an activation checklist; at the headcount trigger or the expiry the gate arms or the exception surfaces as Blocking drift (SIG-39) | **AT-039** | — |
| L3P1-E5 | Orphan detection runs at blocking severity; a blocking orphan cannot be dismissed unresolved | **AT-017** (orphan half); invariant 57 | — |
| L3P1-E6 | Expiry revocation is the only write class enabled at v0, and it is strictly tightening | — | Invariant 81; §53.3. No AT. Evidence: the enabled-repair-class list has exactly one entry |

```bash
set -euo pipefail
# ---- L3-P1 EXIT GATE ----
python -m reconciler.cli run --dry-run --require-canary --format json > /tmp/r1.json
python -c "import json,sys;d=json.load(open('/tmp/r1.json'));sys.exit(0 if d['canary_found'] else 1)" \
  && ok L3P1-E1a || no L3P1-E1a
python -m reconciler.cli run --dry-run --suppress-canary --format json > /tmp/r2.json
python -c "import json,sys;d=json.load(open('/tmp/r2.json'));sys.exit(0 if d['run_status']=='failed' and d['signal']=='SIG-13' else 1)" \
  && ok L3P1-E1b || no L3P1-E1b
ok L3P1-E1
python -m reconciler.cli probe --scenario team-registry-divergence --expect-level 4 \
  && ok L3P1-E2 || no L3P1-E2
python -m reconciler.cli probe --scenario exception-expired --expect-revoked --expect-human-actions 0 \
  && ok L3P1-E3 || no L3P1-E3
python -m reconciler.cli probe --scenario bootstrap-exception-expired \
  --expect-signal SIG-39 --expect-class blocking && ok L3P1-E4 || no L3P1-E4
python -m reconciler.cli probe --scenario orphan-unowned-product --expect-class blocking \
  --expect-dismissable false && ok L3P1-E5 || no L3P1-E5
python -m reconciler.cli repair-classes --list --format json \
  | python -c "import json,sys;d=json.load(sys.stdin);sys.exit(0 if d==['expiry_revocation'] else 1)" \
  && ok L3P1-E6 || no L3P1-E6
```

**STOP rule.** If a probe wants a repair class beyond `expiry_revocation`, stop. Auto-repair is `L3-P4` and is gated on D-EE-5. Spec §99.6 risk 6 calls auto-repair "the most dangerous code" in the system; enabling a class early is not a shortcut, it is the failure.

### L3-P2 — Bounding the reconciler credential, and anchoring the records head

Spec: §26.4 (declared repair scope), §40.1 (top secrets tier), D89, D107 (per-run SHA anchor), §99.6 risk 6, AT-110.

**Entry:** L3-P1 exited; L4-P1 merged (the records repo and its ruleset must exist to anchor against).

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L3P2-E1 | From the reconciler's own credential, **six** attempts fail: a GitHub Actions secret write, an environment write, a workflow-file change, an organisation-settings change, a `records/**` write, and any Layer B access — and the credential then still completes a normal reconciliation run | **AT-110** | — |
| L3P2-E2 | A reconciler write outside its declared repair scope is Blocking drift | — | Spec §98.2 Phase 1 completion check verbatim. No AT |
| L3P2-E3 | The reconciler anchors the records head SHA into the protected control-plane repository each run; a head not descending from the last anchor is Level 5 | — (D107) | No AT. Evidence: a rewritten records history is detected at Level 5 in a rehearsal |

```bash
set -euo pipefail
# ---- L3-P2 EXIT GATE ----
python -m reconciler.cli credential-bounds-test --attempts \
  actions-secret,environment,workflow-file,org-settings,records-write,layer-b \
  --expect-all-denied --then-run-normal --format json > /tmp/b.json
python -c "import json,sys;d=json.load(open('/tmp/b.json'));sys.exit(0 if d['denied']==6 and d['normal_run']=='success' else 1)" \
  && ok L3P2-E1 || no L3P2-E1
python -m reconciler.cli probe --scenario write-outside-declared-scope --expect-class blocking \
  && ok L3P2-E2 || no L3P2-E2
python -m reconciler.cli anchor-check --records-repo "$ORG/control-plane-records" \
  --rehearse-rewrite --expect-level 5 && ok L3P2-E3 || no L3P2-E3
```

**STOP rule.** AT-110 says this is "executed for real at the phase that builds the reconciler and re-executed at every rotation". A passing *unit test* does not satisfy it. If you cannot execute against the real credential, stop and open `blocker/lane-3/L3-P2/E1`.

### L3-P3 — Drift classification, Levels 2/4/5, drift budget, gap procedure, self-observability

Spec: §53.4 (drift classes and response times), §53.6 (calibration and closure quality), §53.7 (the control-loop gap procedure), §52.2 (signal table and arming discipline), §98.5 G1.

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L3P3-E1 | Every finding carries exactly one drift class with the §53.4 response time; there is exactly one drift severity scale | — | Spec §6.7, §53.4. No AT. Evidence: class enumeration equals the spec table exactly |
| L3P3-E2 | The operating system detects and reports a failure in its own reconciliation, health job or dashboard freshness | **AT-032** | — |
| L3P3-E3 | An exception that cannot be auto-revoked becomes Blocking drift on its expiry date and appears on the Founder view | **AT-037** | — |
| L3P3-E4 | A breached pre-onboarding deadline surfaces as drift | **AT-051** (drift half) | — |
| L3P3-E5 | The gap procedure runs after a vacuous or failed run and records what the window may have missed | — | Spec §53.7; EC-109. No AT. Evidence: a `gap procedure run` event exists for the rehearsed failure |
| L3P3-E6 | Zero Blocking drift open at the moment the gate runs | — | Spec §98.5 G1 exit verbatim. No AT |

```bash
set -euo pipefail
# ---- L3-P3 EXIT GATE ----
python -m validators.drift.cli classes --format json \
  | python -c "import json,sys;d=json.load(sys.stdin);sys.exit(0 if [x['class'] for x in d]==['green','amber','blocking'] and all(x.get('response_time') for x in d if x['class']!='green') else 1)" \
  && ok L3P3-E1 || no L3P3-E1
python -m reconciler.cli self-check --probe health-job-stalled,dashboard-stale,recon-failed \
  --expect-reported 3 && ok L3P3-E2 || no L3P3-E2
python -m reconciler.cli probe --scenario exception-unrevokable-at-expiry \
  --expect-class blocking --expect-surface founder-view && ok L3P3-E3 || no L3P3-E3
python -m reconciler.cli probe --scenario preonboarding-deadline-breached --expect-drift \
  && ok L3P3-E4 || no L3P3-E4
python -m reconciler.cli gap-procedure --rehearse --expect-event 'gap procedure run' \
  && ok L3P3-E5 || no L3P3-E5
python -m reconciler.cli run --dry-run --format json \
  | python -c "import json,sys;d=json.load(sys.stdin);sys.exit(0 if d['blocking']==0 else 1)" \
  && ok L3P3-E6 || no L3P3-E6
```

**STOP rule.** Do not add a fourth drift class, and do not add a per-subsystem severity scale. Spec §6.7 states there is exactly one scale, used identically everywhere.

### L3-P4 — Auto-repair, Level 3, stricter-only, one class at a time

Spec: §53.2 Level 3 (the permitted repair list, verbatim), §53.3 (the binding rule), §98.3 (early hardening), §99.4 item 6, §99.6 risk 6, AT-033, invariant 81.

**Entry — this is the most heavily gated entry in the plan**

| id | Condition | Proof command |
|---|---|---|
| L3P4-N1 | L3-P1, L3-P2, L3-P3 all exited | Re-run their gates |
| L3P4-N2 | Detection has run clean for the D-EE-5 threshold (**O-5B: 28 consecutive days**, zero unexplained findings, canary found every run, ≥1 real Blocking finding correctly raised and closed) | see block below |
| L3P4-N3 | L0 has recorded the enable order of repair classes, one at a time | `python -c "import yaml;print(yaml.safe_load(open('contracts/l3-reconciler.yaml'))['repair_class_enable_order'])"` |

```bash
set -euo pipefail
# ---- L3-P4 ENTRY GATE ----
CLEAN_DAYS=28   # D-EE-5 option O-5B. Change only if L0 records a different option.
python -m reconciler.cli history --days "$CLEAN_DAYS" --format json > /tmp/h.json
python -c "import json,sys;d=json.load(open('/tmp/h.json'));sys.exit(0 if d['runs_failed']==0 and d['canary_missed']==0 and d['unexplained_findings']==0 and d['blocking_raised_and_closed']>=1 else 1)" \
  && ok L3P4-N2 || no L3P4-N2
```

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L3P4-E1 | Reconciliation presented with a stricter-than-declared production control raises it for human review and does **not** relax it | **AT-033**; invariant 81 | — |
| L3P4-E2 | The stricter-only rule is enforced in code and tested — not documented | — | Spec §99.4 item 6 verbatim; §99.6 risk 6. No AT beyond AT-033. Evidence: a property test over generated declared/actual pairs |
| L3P4-E3 | Repair classes are enabled one at a time in the recorded order; the live enabled set is a prefix of that order | — | Spec §98.3, §99.6 risk 6. No AT |
| L3P4-E4 | Reconciliation never modifies production runtime configuration, never modifies data, and never rotates or writes secrets | — | Spec §53.3 verbatim. No AT (AT-110 covers the credential; this covers the behaviour) |
| L3P4-E5 | Repeated failed auto-repair escalates to Level 5 with an incident | — | Spec §53.2 Level 5. No AT |

```bash
set -euo pipefail
# ---- L3-P4 EXIT GATE ----
python -m reconciler.cli probe --scenario actual-stricter-than-declared \
  --expect-level 2 --expect-no-write && ok L3P4-E1 || no L3P4-E1
pytest reconciler/tests/test_stricter_only_property.py -q && ok L3P4-E2 || no L3P4-E2
python - <<'PY' && ok L3P4-E3 || no L3P4-E3
import json,subprocess,yaml,sys
order=yaml.safe_load(open("contracts/l3-reconciler.yaml"))["repair_class_enable_order"]
live=json.loads(subprocess.check_output(["python","-m","reconciler.cli","repair-classes","--list","--format","json"]))
sys.exit(0 if live==order[:len(live)] else 1)
PY
python -m reconciler.cli capability-report --format json \
  | python -c "import json,sys;d=json.load(sys.stdin);sys.exit(0 if not (d['can_write_runtime_config'] or d['can_write_data'] or d['can_write_secrets']) else 1)" \
  && ok L3P4-E4 || no L3P4-E4
python -m reconciler.cli probe --scenario repeated-failed-repair --expect-level 5 --expect-incident \
  && ok L3P4-E5 || no L3P4-E5
```

**STOP rule.** If `L3P4-N2` fails, the phase does not start — not "starts with a smaller class". Report the shortfall to L0 and wait. This is the single highest-risk phase in the build (spec §99.6 risk 6).

### L3-P5 — Provisioning v0: `create-product`, `add-person`

Spec: §98.2 Phase 3 (verbatim: "generating repository, Teams, CODEOWNERS, branch protection and registry entries with zero hand-editing"), §12.1 (new person lifecycle), §19.1 (product creation), §99.4 item 3, §64.1 (safe defaults), AT-001, AT-002.

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L3P5-E1 | `create-product` produces repo-from-template, Teams, generated CODEOWNERS, branch protection and registry entries with **zero hand-editing**; every surface enumerates from the registry and no dashboard, workflow or script contains a product list | **AT-001**; invariants 52, 53 | — |
| L3P5-E2 | `add-person` produces registry entry, role assignment, capability grant, lifecycle start; reconciliation grants access; capacity profile and the Insufficient Evidence state initialise; no workflow, architecture or dashboard change | **AT-002**; invariant 100 | — |
| L3P5-E3 | New people, products and tools default to minimum privilege and draft state | — | Invariant 79; §64.1. No AT. Evidence: a freshly provisioned product's permissions equal the minimum profile exactly |
| L3P5-E4 | One product with three repositories yields one contract, one owner set, one dashboard entry, with protection and CI applied to all three | **AT-010** | — |
| L3P5-E5 | The model scales without redesign under a doubled fixture: 16 products, 18 people | **AT-012**, **AT-013** (fixture-proved; the real doubling is calendar-gated) | — |

```bash
set -euo pipefail
# ---- L3-P5 EXIT GATE ----
python -m tools.provision.cli create-product --name probe-21 --template product-template \
  --dry-run=false --format json > /tmp/cp.json
python -c "import json,sys;d=json.load(open('/tmp/cp.json'));sys.exit(0 if d['hand_edits_required']==0 and d['teams'] and d['codeowners_generated'] and d['branch_protection_applied'] else 1)" \
  && ok L3P5-E1a || no L3P5-E1a
grep -rInE '\b(solvox|probe-21)\b' metrics/ .github/workflows/ templates/workflows/ \
  | grep -v fixtures > /tmp/hardcoded.txt || true
test ! -s /tmp/hardcoded.txt && ok L3P5-E1b || { cat /tmp/hardcoded.txt; no L3P5-E1b; }
ok L3P5-E1
python -m tools.provision.cli add-person --login probe-user --role developer --dry-run=false \
  --format json | python -c "import json,sys;d=json.load(sys.stdin);sys.exit(0 if d['capacity_profile_initialised'] and d['evidence_state']=='insufficient_evidence' else 1)" \
  && ok L3P5-E2 || no L3P5-E2
python -m tools.provision.cli permissions-diff --product probe-21 --against minimum-privilege \
  --expect-empty && ok L3P5-E3 || no L3P5-E3
python -m tools.provision.cli create-product --name probe-multi --repos 3 --dry-run=false \
  --format json | python -c "import json,sys;d=json.load(sys.stdin);sys.exit(0 if d['contracts']==1 and d['owner_sets']==1 and d['protected_repos']==3 else 1)" \
  && ok L3P5-E4 || no L3P5-E4
python -m tools.provision.cli scale-fixture --products 16 --people 18 --expect-no-code-change \
  && ok L3P5-E5 || no L3P5-E5
# clean up every probe artifact before opening the PR
python -m tools.provision.cli teardown --names probe-21,probe-multi --people probe-user
```

**STOP rule.** Probe artifacts are torn down in the same session that creates them. A probe product left in the org becomes an orphan at the next reconciliation run and will fail `L3P3-E6` for everyone.

### L3-P6 — Provisioning remainder: `change-role`, `remove-person`, template evolution

Spec: §98.3 (early hardening: "the rest follow the first role change and the first departure"), §12.2 (exit lifecycle), §12.3 (role transition), §13.1 (Acting Team Lead), §17.4 (who changes ownership), AT-003…AT-005, AT-007, AT-017, AT-021.

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L3P6-E1 | `remove-person` runs the exit lifecycle: access revoked by reconciliation, every unowned responsibility surfaced, blocking orphans undismissable, succession activated, evidence archived, history retained | **AT-017**; invariants 57, 47 | — |
| L3P6-E2 | `change-role` applies an effective date, recalculates capabilities, permissions and assignments, applies the new role's evidence model from that date, and segments the period with no retroactive evaluation | **AT-005**, **AT-004**; invariant 56 | — |
| L3P6-E3 | An Acting Team Lead is pre-designated, holds dormant capability, and activates by configuration alone | **AT-003**; invariant 35 | — |
| L3P6-E4 | A new role is introduced as a role profile plus framework mapping, with no architecture change | **AT-007**; invariant 54 | — |
| L3P6-E5 | A permanent ownership change is executed by the Team Lead under the reviewer-matrix-change capability, recorded as a decision, and generates a Founder-view notification — with no Founder approval step | **AT-021**; invariant 13 | — |

```bash
set -euo pipefail
# ---- L3-P6 EXIT GATE ----
python -m tools.provision.cli remove-person --login probe-user --dry-run --format json \
  | python -c "import json,sys;d=json.load(sys.stdin);sys.exit(0 if d['orphans_surfaced']>=1 and d['blocking_dismissable'] is False and d['history_retained'] else 1)" \
  && ok L3P6-E1 || no L3P6-E1
python -m tools.provision.cli change-role --login probe-user --to team_lead \
  --effective 2026-07-01 --dry-run --format json \
  | python -c "import json,sys;d=json.load(sys.stdin);sys.exit(0 if d['period_segments']==2 and d['retroactive']==False and d['capabilities_recalculated'] else 1)" \
  && ok L3P6-E2 || no L3P6-E2
python -m reconciler.cli probe --scenario acting-team-lead-activate --expect-config-only \
  --expect-code-changes 0 && ok L3P6-E3 || no L3P6-E3
python -m tools.provision.cli add-role --name probe-role --profile registries/roles.yaml \
  --dry-run --expect-architecture-changes 0 && ok L3P6-E4 || no L3P6-E4
python -m tools.provision.cli ownership-change --product probe-product --new-primary probe-user \
  --actor team_lead --dry-run --format json \
  | python -c "import json,sys;d=json.load(sys.stdin);sys.exit(0 if d['capability_checked']=='reviewer-matrix-change' and d['decision_record'] and d['founder_notification'] and not d['founder_approval_required'] else 1)" \
  && ok L3P6-E5 || no L3P6-E5
```

**STOP rule.** `L3P6-E5` must not add a Founder approval step, however cautious that feels. Invariant 13 and AT-021 both state it: visibility, not approval.

---

## 7. Lane L5 — Access, Infra & Ops (subsystems K, L, M, Q, R)

Owns `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**`. L5 merges last.

### L5-P1 — The access model as configuration

Spec: §11.1 (verified GitHub permission semantics), §11.2–§11.3 (permission model, branch protection per repository), §33.4 (environments), §40.1 (five secret tiers), §64.2 (fail-closed), §98.2 Phase 1 completion check, D73, D89.

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L5P1-E1 | An approval from a Read-only account does **not** satisfy branch protection; an approval from a Write-holding Cross-Reviewer does | — | Spec §98.2 Phase 1 completion check verbatim; §11.1. No AT. Evidence: both cases executed for real |
| L5P1-E2 | An approval from a machine account does **not** satisfy branch protection | — | Spec §98.2 Phase 1 ("executed negatively"); D53/D74. No AT |
| L5P1-E3 | A workflow pushed to a non-default branch declaring `environment: production` obtains no environment secret | — | Spec §98.2 Phase 1 verbatim. No AT. Evidence: executed negatively, the run gets no secret |
| L5P1-E4 | Environment deployment-branch and tag policies are applied from the template on every environment | — | Spec §33.4, §98.2 Phase 1. No AT |
| L5P1-E5 | Every secret is placed in one of the five declared tiers; production secrets are environment-scoped and never present locally | — | Invariants 25, 26; §40.1. No AT. Evidence: the tier report has zero untiered secrets |
| L5P1-E6 | A second organisation Owner or an escrowed break-glass Owner credential exists with a **named escrow custodian** | **AT-022** (precondition half); invariant 39 | — |

```bash
set -euo pipefail
# ---- L5-P1 EXIT GATE ----
python -m validators.drift.cli approval-semantics-probe --repo "$ORG/product-template" \
  --readonly-approver probe-read --write-approver probe-write \
  --expect readonly=insufficient,write=sufficient && ok L5P1-E1 || no L5P1-E1
python -m validators.drift.cli approval-semantics-probe --repo "$ORG/product-template" \
  --machine-approver "$RECONCILER_APP_SLUG" --expect machine=insufficient && ok L5P1-E2 || no L5P1-E2
gh workflow run env-secret-negative.yml --repo "$ORG/product-template" --ref probe-branch && sleep 45
gh run list --repo "$ORG/product-template" --workflow env-secret-negative.yml --limit 1 \
  --json conclusion --jq '.[0].conclusion' | grep -qx failure && ok L5P1-E3 || no L5P1-E3
python -m validators.drift.cli env-policy-coverage --all-repos --template access/environments.yaml \
  --expect-complete && ok L5P1-E4 || no L5P1-E4
python -m validators.drift.cli secret-tier-report --format json \
  | python -c "import json,sys;d=json.load(sys.stdin);sys.exit(0 if d['untiered']==0 and d['local_production_secrets']==0 else 1)" \
  && ok L5P1-E5 || no L5P1-E5
python -c "import yaml,sys;d=yaml.safe_load(open('access/continuity.yaml'));sys.exit(0 if d.get('escrow_custodian') and (d.get('second_owner') or d.get('break_glass_credential')) else 1)" \
  && ok L5P1-E6 || no L5P1-E6
```

**STOP rule.** Do not depend on environment required reviewers. D73 is settled: they are Enterprise-only on private repositories and are an optional strengthening, never the mechanism. The mechanism is the §27.2 workflow-identity gate, built at `L2-P4`.

### L5-P2 — The operations VM

Spec: §51.4 (control-plane patching and the private path), §51.5 (the disposable operations VM), §99.2 subsystem M (verbatim: "rebuild under 4 hours from GitHub, tested quarterly"), §46 (degraded modes), §45.3 (organisation export), invariants 75, 76.

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L5P2-E1 | The VM rebuilds from GitHub in under 4 hours, tested; the drill is recorded | — | Spec §99.2 subsystem M verbatim; §99.6 risk 10. No AT. Evidence: a timed rebuild record inside the quarter |
| L5P2-E2 | The ops VM is never in any product's runtime path; a control-plane outage does not stop a running product | **AT-029**; invariants 75, 76 | — |
| L5P2-E3 | GitHub unavailable for several hours: Degraded Engineering Mode holds, products keep serving, state is reconciled on recovery and never assumed | **AT-028** | — |
| L5P2-E4 | Control-plane surfaces are reachable only over the §51.4 private path, **or** a dated `policy_waiver` with expiry, owner and deactivation trigger exists | — | Spec §98.2 Phase 2 verbatim; invariant 77. No AT |
| L5P2-E5 | Removing a named external integration changes nothing in the operating system; its declared exit condition executes cleanly (the git host is exempt by the §62.5 carve-out) | **AT-031**, **AT-030** | — |
| L5P2-E6 | The ops VM has a named owner, an SLO, a declared patch cadence and a tool-register entry | — | Spec §99.6 risk 10. No AT. Evidence: four fields non-empty in `tools.yaml` |

```bash
set -euo pipefail
# ---- L5-P2 EXIT GATE ----
python -m validators.drift.cli drill-record --drill ops-vm-rebuild --within 90.days \
  --max-minutes 240 && ok L5P2-E1 || no L5P2-E1
python -m validators.drift.cli runtime-path-audit --products all --expect-opsvm-references 0 \
  && ok L5P2-E2 || no L5P2-E2
python -m validators.drift.cli drill-record --drill degraded-engineering-mode --within 180.days \
  --require-outcome products-served && ok L5P2-E3 || no L5P2-E3
python -m validators.drift.cli private-path-check --targets grafana,devlake,prometheus \
  --or-waiver registries/exceptions.yaml --require-waiver-expiry && ok L5P2-E4 || no L5P2-E4
python -m validators.drift.cli integration-removal-drill --integration work-management \
  --expect-os-changes 0 --require-exit-condition && ok L5P2-E5 || no L5P2-E5
python -c "import yaml,sys;t=yaml.safe_load(open('registries/tools.yaml'))['tools'];v=[x for x in t if x['name']=='operations-vm'];sys.exit(0 if v and all(v[0].get(k) for k in ('owner','slo','patch_cadence')) else 1)" \
  && ok L5P2-E6 || no L5P2-E6
```

**STOP rule.** `L5P2-E6` reads `registries/tools.yaml`, an **L1-owned** file. L5 does not edit it. If the entry is missing, file a Contract Change Request to L0 — do not add the entry from an L5 branch, it will fail the lane guard.

### L5-P3 — AI runtime contract enforcement (subsystem K)

Spec: §35.1–§35.2 (required capabilities, approved runtime list as configuration), §36.1–§36.3 (constitutional rule, approved extension/MCP list), §36.6 (pre-flight secret stripping, the no-API-keys check), §38.3 (eval suites), §39 (seats), D69, D80, invariants 83, 84, 85, 86, AT-011, AT-107.

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L5P3-E1 | Changing the AI provider changes nothing in GSD, verification, GitHub, CI, production, ownership or review routing | **AT-011**; invariant 86 | — |
| L5P3-E2 | `env \| grep -i api_key` returns empty on every machine, including shell profiles and repository `.env` files | — | Spec §98.2 Phase 1 verbatim; invariant 84. No AT |
| L5P3-E3 | A scheduled eval regression creates the category-five incident, raises SIG-42, and blocks adoption of the new model pin until the suite passes or a recorded exception accepts the change | **AT-107** | — |
| L5P3-E4 | Engineering tooling runs at fixed cost — no metered LLM APIs and no free cloud LLM tiers in engineering tooling | — | Invariant 83. No AT. Evidence: the approved-runtime list contains no metered engineering entry |
| L5P3-E5 | GSD Core is pinned to a tagged release; the Hermes pin is a pinned checkout with the self-update path never run | — | Invariant 85; D69, D80. No AT |
| L5P3-E6 | The constitution is referenced from every context file | — | Spec §36.1, §98.2 Phase 7. No AT. Evidence: zero context files without the reference |

```bash
set -euo pipefail
# ---- L5-P3 EXIT GATE ----
python -m validators.drift.cli provider-swap-dryrun --from runtime-a --to runtime-b \
  --expect-changed-files 1 --expect-changed registries/ai-toolchain.yaml && ok L5P3-E1 || no L5P3-E1
env | grep -i 'api_key' && no L5P3-E2 || { grep -rIl 'API_KEY' "$HOME"/.bashrc "$HOME"/.profile 2>/dev/null && no L5P3-E2 || \
  { find "$CP" "$CPR" -type f -name '.env' 2>/dev/null | xargs -r grep -il 'API_KEY' 2>/dev/null && no L5P3-E2 || ok L5P3-E2; }; }
python -m validators.drift.cli eval-regression-probe --product probe-ai --drop 6 \
  --expect-signal SIG-42 --expect-incident-category 5 --expect-pin-blocked && ok L5P3-E3 || no L5P3-E3
python -c "import yaml,sys;d=yaml.safe_load(open('registries/ai-toolchain.yaml'));sys.exit(0 if all(r.get('billing') in ('flat_per_person','self_hosted','free_fixed') for r in d['engineering_runtimes']) else 1)" \
  && ok L5P3-E4 || no L5P3-E4
python -c "import yaml,sys;d=yaml.safe_load(open('registries/tools.yaml'))['tools'];g=[x for x in d if x['name'] in ('gsd-core','hermes-agent')];sys.exit(0 if g and all(x.get('pin') for x in g) else 1)" \
  && ok L5P3-E5 || no L5P3-E5
python -m validators.drift.cli constitution-reference-check --all-context-files --expect-missing 0 \
  && ok L5P3-E6 || no L5P3-E6
```

**STOP rule.** If any machine has an API key in a shell profile or `.env`, that is not a lane finding to note — it is a Phase 1 completion-check failure (spec §98.2) and a security matter. Open the blocker immediately and stop work on the branch.

### L5-P4 — Notification routing (R) and asset inventory with deadline watch (Q)

Spec: §92.11 (the notification contract — a governed addition before anything may page a person), §22.2 (intake channels), §42.3 (response flow), §49.1–§49.2 (expiry-tracked assets, vendor deadline watch), §47.5 (out-of-hours notification model), AT-106.

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L5P4-E1 | Actions webhook to the messaging channel works; per-product alert channels resolve; no paging apps for developers | — | Spec §99.2 subsystem R verbatim. No AT. Evidence: a test event lands in the declared channel and the paging-app list is empty |
| L5P4-E2 | A Gate 1 submission notifies its resolved approver as a push event; a breached turnaround auto-raises the item's Blocked flag routed to the escalation role; re-request to an active `plan_approval_delegate` or the Acting Team Lead designate is a recorded routing event | **AT-106** (notification half; the Gate 1 tooling half is subsystem G — D-EE-2) | — |
| L5P4-E3 | Every expiry-tracked asset (certificates, domains, OAuth, signing, vendor contracts, announced deprecations) has an owner, an expiry and a configurable-lead alert; a seeded 30-day expiry fires | — | Spec §49.1; §97.2 credential-expiry paragraph. No AT. Evidence: the seeded alert fires at the declared lead |
| L5P4-E4 | Asset owners participate in orphan detection | — | Spec §99.2 subsystem Q verbatim ("owners in orphan detection"). No AT. Evidence: an ownerless asset appears in the reconciler's orphan output |
| L5P4-E5 | A documented phone-escalation path and a Founder/Team Lead out-of-hours channel exist | — | Spec §99.2 subsystem R; §47.5. No AT |

```bash
set -euo pipefail
# ---- L5-P4 EXIT GATE ----
python -m validators.drift.cli notify-probe --channel default --expect-delivered \
  && python -c "import yaml,sys;d=yaml.safe_load(open('notify/routing.yaml'));sys.exit(0 if not d.get('paging_apps') else 1)" \
  && ok L5P4-E1 || no L5P4-E1
python -m validators.drift.cli gate1-notify-probe --submit probe-plan --breach-turnaround \
  --expect-push-notification --expect-blocked-flag --expect-route escalation \
  && ok L5P4-E2 || no L5P4-E2
python -m validators.drift.cli asset-expiry-probe --seed-days 30 --expect-alert \
  --require-fields owner,expiry,lead_days && ok L5P4-E3 || no L5P4-E3
python -m reconciler.cli probe --scenario asset-without-owner --expect-orphan \
  && ok L5P4-E4 || no L5P4-E4
test -f docs/runbooks/phone-escalation.md \
  && python -c "import yaml,sys;d=yaml.safe_load(open('notify/routing.yaml'));sys.exit(0 if d.get('out_of_hours_channel') else 1)" \
  && ok L5P4-E5 || no L5P4-E5
```

**STOP rule.** `L5P4-E2` depends on Gate 1 tooling that has no lane (D-EE-2, subsystem G). Build and prove the **notification** half only. If asked to build the plan-checker, stop — spec §99.3 item 3 makes it contingent on verification against the pinned GSD release, which is L0's call.

### L5-P5 — The Layer B datasource separation

Spec: §90.1–§90.3 (two layers, the permission matrix, datasource-level enforcement), §90.4 (`people-intelligence` capability), §90.6 (own-data transparency), §92.8 (self-view), §99.5 (Layer B mechanism), D75, invariants 106–109, §98.6 P4 sequencing rule.

**This phase is the hard gate for the entire People tier.** Spec §98.6, verbatim: "P4 must not begin before the Layer B datasource separation is implemented and verified… *verified* means AT-089, AT-091, AT-097 and AT-098 pass and invariant 109 holds."

**Exit criteria**

| id | Criterion | AT / invariant | Evidence if no AT |
|---|---|---|---|
| L5P5-E1 | Peers and general dashboards cannot reach Layer B data by any path | **AT-089** | — |
| L5P5-E2 | The people datasource is **absent** from the shared Grafana instance's provisioning — no datasource entry, no dashboard reference — verified in the provisioned configuration, not inferred from panel visibility | **AT-097**; D75; invariant 109 | — |
| L5P5-E3 | Reaching the Founder-only instance requires its own credential; a shared-instance login grants nothing there and a direct query without that credential is denied | **AT-098**; D75 | — |
| L5P5-E4 | Access follows the `people-intelligence` capability, not the role name; granting the dated delegate assignment opens access through reconciliation and revoking or expiring it closes access the same way | **AT-091** | — |
| L5P5-E5 | The Team Lead is denied at both dashboard and datasource level, and can still perform allocation fully from the three-state `allocation_state` field | **AT-092**, **AT-093**, **AT-094**; invariant 107 | — |
| L5P5-E6 | A person's own generated self-view document shows their evidence and nothing about peers; peer-to-peer access is denied | **AT-095**, **AT-096**; invariant 108 | — |
| L5P5-E7 | Host-level administrative access is the single named, recorded accepted risk of §90.3: holder named in the asset inventory, compensating audit trail live and shipping off-host, review within cadence | **AT-090** (scope carve-out); invariant 106 | — |

```bash
set -euo pipefail
# ---- L5-P5 EXIT GATE ----
python -m validators.drift.cli layerb-reachability --from shared-grafana,peer-account \
  --expect-denied-all && ok L5P5-E1 || no L5P5-E1
python -c "import yaml,sys,glob;bad=[f for f in glob.glob('infra/grafana/shared/**/*.y*ml',recursive=True) if 'people' in open(f).read()];sys.exit(0 if not bad else 1)" \
  && ok L5P5-E2 || no L5P5-E2
python -m validators.drift.cli founder-instance-auth --with shared-credential --expect-denied \
  --with founder-credential --expect-allowed && ok L5P5-E3 || no L5P5-E3
python -m validators.drift.cli capability-gate --capability people-intelligence \
  --grant-then-expire --expect-open-then-closed && ok L5P5-E4 || no L5P5-E4
python -m validators.drift.cli role-probe --role team_lead --expect-denied dashboard,datasource \
  --then-allocate --using allocation_state --expect-success && ok L5P5-E5 || no L5P5-E5
python -m validators.drift.cli selfview-probe --person probe-user --expect-own-only \
  --peer-probe --expect-denied && ok L5P5-E6 || no L5P5-E6
python -c "import yaml,sys;d=yaml.safe_load(open('assets/inventory.yaml'));h=[a for a in d['assets'] if a.get('type')=='host_admin_access'];sys.exit(0 if h and h[0].get('holder') and h[0].get('compensating_audit_offhost') and h[0].get('review_due') else 1)" \
  && ok L5P5-E7 || no L5P5-E7
```

**STOP rule.** Panel hiding is explicitly insufficient (spec §99.5, D75). If `L5P5-E2` passes only because a panel is hidden, it has not passed. And AT-089's own text warns that "a reinterpreted access-control test is how the boundary erodes" — never soften these criteria to make them pass.

---

## 8. Phases with no acceptance test — the standing evidence, in one place

Every phase below has at least one criterion no AT covers. Section 100 does not claim to cover the build surface; it covers the *operating* properties. Where there is no AT, the evidence is named here and is itself machine-checkable.

| Phase | Uncovered criteria | Standing evidence that substitutes |
|---|---|---|
| L0-P0 | E1, E2, E4 | PARTITION rules 1–2 executed as set comparisons; the spec §98.2 Phase 1 "required-status-check list starts empty" check |
| L1-P1 | E1–E4 | Negative fixture rejection for the exception schema (spec §98.2 Phase 1, verbatim requirement); §97.3 event-enum rejection; effective-dating check |
| L1-P3 | E3, E5, E6 | Invariant 4 (restore window), §21.4 `check-commitment` CLI rejecting a seeded conflict, invariant 64 |
| L1-P4 | E2, E3, E9 | Invariants 78, 80 and the §101 preamble classification check — the only mechanism that detects an invariant with no owner |
| L1-P5 | E4, E5 | §97.2 `record_schema_version` default rule; invariant 74 with SIG-10 |
| L4-P1 | E1, E2, E4 | D107 executed (a real force-push refused), commit-signature scan, §97.3 one-file-per-event layout |
| L4-P2 | E1, E2, E5 | Store-list equality against the §97.2 table; write-time envelope rejection; invariant 47 in-place-edit detection |
| L4-P3 | E1, E2 | §97.2 RECORD-VERIFICATION-RESULT single-path rule; the `record-decision` CLI producing a schema-valid record |
| L4-P4 | E1, E2, E5 | Invariants 46 and 49 as register queries (zero storeless, zero ownerless metrics); three-endpoint scrape coverage |
| L4-P5 | E1–E4 | D79 self-report scoping; invariant 90 refusal; §97.5 miss detector; §29 board-shape check |
| L2-P1 | E1–E4 | PARTITION rule 1 executed as a failing PR; §33.1 required-file check; §101 preamble check present in CI |
| L2-P2 | E1, E2, E5, E6 | §33.2 delta-gating both directions; slopsquat negative; invariant 85 pin scan; D89 two-ruleset Renovate split |
| L2-P3 | E1–E3 | §32 item 5, §48.3 SBOM artifact, invariant 23 (no rebuild path in the workflow source) |
| L2-P4 | E1–E4 | D73 workflow-identity gate executed negatively; invariant 22 digest mismatch rejected; §97.1 calendar-resolved freeze; §97.2 required failing steps |
| L2-P5 | E1, E2 | Eleven-of-eleven answers for a real deployment; `verify-digest-chain` scheduled with zero mismatches |
| L2-P6 | E3, E5 | Invariants 3 and 4 via `records/restore-tests/`; seven named migration-failure tests |
| L3-P1 | E2, E6 | Invariant 44 detection; invariant 81 with exactly one enabled repair class |
| L3-P2 | E2, E3 | §98.2 Phase 1 out-of-scope-write rule; D107 anchor rehearsal at Level 5 |
| L3-P3 | E1, E5, E6 | §6.7 single severity scale; §53.7 gap-procedure event; §98.5 G1 zero-Blocking exit |
| L3-P4 | E2–E5 | §53.3 property test; recorded enable order as a prefix; capability report; Level 5 escalation |
| L3-P5 | E3 | Invariant 79 minimum-privilege diff empty |
| L5-P1 | E1–E5 | The five §98.2 Phase 1 completion checks executed negatively for real |
| L5-P2 | E1, E4, E6 | Timed rebuild record under 4 hours; §51.4 private-path or dated waiver; §99.6 risk 10 four fields |
| L5-P3 | E2, E4, E5, E6 | Invariant 84 empty-grep; invariant 83 billing-class check; invariant 85 pins; §36.1 constitution reference |
| L5-P4 | E1, E3, E4, E5 | §92.11 governed notification addition; §49 seeded expiry alert; orphan participation; §47.5 channel |

---

## 9. AT coverage map — all 110 acceptance tests

`Status` values: **build** = a lane phase's exit criterion proves it; **drill** = proved by a recorded, dated drill an L0 gate requires; **unclaimed** = no lane owns the subsystem (D-EE-2); **deferred** = spec §98.4 scale-activation, built on its trigger, not in this plan; **calendar** = spec §98.1 calendar-gating, needs elapsed operating data.

| AT | Proved at | Status |
|---|---|---|
| AT-001 | L3P5-E1 | build |
| AT-002 | L3P5-E2 | build |
| AT-003 | L3P6-E3 | build |
| AT-004 | L3P6-E2 | build |
| AT-005 | L3P6-E2 + L1P5-E3 | build |
| AT-006 | L3P5-E2 (fixture: two QA) | build |
| AT-007 | L3P6-E4 | build |
| AT-008 | L1P3-E2 + L3P1-E3 | build |
| AT-009 | L1P2-E3 + L2P2-E4 + L2P5-E3 | build |
| AT-010 | L3P5-E4 | build |
| AT-011 | L5P3-E1 | build |
| AT-012 | L3P5-E5 (18-person fixture) | build |
| AT-013 | L3P5-E5 (16-product fixture) | build |
| AT-014 | — subsystem P | unclaimed |
| AT-015 | L1P5-E2 (schema half only) | build (partial) / unclaimed |
| AT-016 | L1P4 topology + L3P1 routing while dormant | build |
| AT-017 | L3P6-E1 + L3P1-E5 | build |
| AT-018 | L3P1-E3 | build |
| AT-019 | — §98.4 first split | deferred |
| AT-020 | — §98.4 first merge | deferred |
| AT-021 | L3P6-E5 | build |
| AT-022 | L5P1-E6 + periodic drill | drill |
| AT-023 | — subsystem G + platform-change process (O) | unclaimed |
| AT-024 | L2P2-E5 (pinned-tag half); canary half unclaimed | build (partial) |
| AT-025 | L1P5-E1 | build |
| AT-026 | — subsystem O | unclaimed |
| AT-027 | L1P4 (policies) + L2P2 (reusable workflow) | build |
| AT-028 | L5P2-E3 | drill |
| AT-029 | L5P2-E2 + L2P4-E5 | build + drill |
| AT-030 | L5P2-E5 | drill |
| AT-031 | L5P2-E5 | drill |
| AT-032 | L3P3-E2 + L4P3-E3 | build |
| AT-033 | L3P4-E1 | build |
| AT-034 | L1P4-E10 | build |
| AT-035 | L2P6-E2 | build |
| AT-036 | L3P1-E3 | build |
| AT-037 | L3P3-E3 | build |
| AT-038 | L1P4-E1 | build |
| AT-039 | L3P1-E4 | build |
| AT-040 | — subsystem O (pattern detector) | unclaimed + calendar (two quarters, §98.5 G4) |
| AT-041 | L4P5 (attention data) + view half subsystem H | unclaimed (view) |
| AT-042 | — G5 | unclaimed + calendar |
| AT-043 | — G5 | unclaimed + calendar |
| AT-044 | L4P5-E5 | build |
| AT-045 | — subsystem O, quarterly review | unclaimed + calendar |
| AT-046 | L1P4-E8 | build |
| AT-047 | L1P3-E4 + L4P4-E4 | build |
| AT-048 | L4P3-E4 | build |
| AT-049 | L1P2-E2 + L2P2-E3 | build |
| AT-050 | L1P2-E5 + L4P4-E3 | build |
| AT-051 | L1P2-E4 + L3P3-E4 | build |
| AT-052 | — subsystem P | unclaimed |
| AT-053 | — subsystem P | unclaimed |
| AT-054 | — subsystem P | unclaimed |
| AT-055 | — subsystem P | unclaimed + calendar |
| AT-056 | — subsystem P | unclaimed + calendar |
| AT-057 | — subsystem P (§99.3 item 5 open) | unclaimed |
| AT-058 | — subsystem P | unclaimed |
| AT-059 | — subsystem P | unclaimed |
| AT-060 | — subsystem P | unclaimed |
| AT-061 | — subsystem P | unclaimed |
| AT-062 | — subsystem P | unclaimed |
| AT-063 | — subsystem P | unclaimed |
| AT-064 | — subsystem P | unclaimed |
| AT-065 | — subsystem P | unclaimed |
| AT-066 | — subsystem P | unclaimed |
| AT-067 | — subsystem P | unclaimed |
| AT-068 | — subsystem P | unclaimed |
| AT-069 | — subsystem P | unclaimed |
| AT-070 | — subsystem P | unclaimed |
| AT-071 | L1P4-E5 | build |
| AT-072 | L3P5-E2 (Insufficient Evidence init); full test subsystem P | build (partial) |
| AT-073 | — subsystem P | unclaimed |
| AT-074 | L1P4-E7 | build |
| AT-075 | L1P4-E6 | build |
| AT-076 | — subsystem P / G6 | unclaimed + calendar |
| AT-077 | — subsystem P (§99.3 item 6 open) | unclaimed |
| AT-078 | L1P5-E3 | build |
| AT-079 | — subsystem P | unclaimed |
| AT-080 | — subsystem P | unclaimed |
| AT-081 | — subsystem P | unclaimed |
| AT-082 | — subsystem P | unclaimed |
| AT-083 | — subsystem P | unclaimed |
| AT-084 | — subsystem P | unclaimed |
| AT-085 | — subsystem P + G6 automation ledger | unclaimed + calendar |
| AT-086 | — subsystem P / H | unclaimed |
| AT-087 | L1P4 (marker schema) + L4P4 STOP rule | build (partial) |
| AT-088 | — subsystem P | unclaimed |
| AT-089 | L5P5-E1 | build |
| AT-090 | L1P4-E4 + L5P5-E7 | build |
| AT-091 | L5P5-E4 | build |
| AT-092 | L5P5-E5 | build |
| AT-093 | L5P5-E5 | build |
| AT-094 | L5P5-E5 (+ `allocation_state` schema at L1P4) | build |
| AT-095 | L5P5-E6 | build |
| AT-096 | L5P5-E6 | build |
| AT-097 | L5P5-E2 | build |
| AT-098 | L5P5-E3 | build |
| AT-099 | L5P5 (access half); view half subsystem H | unclaimed (view) |
| AT-100 | L5P5 (separation half); bundle half subsystem P | unclaimed (bundle) |
| AT-101 | — operating drill, requires headcount | drill |
| AT-102 | L3P1-E1 + GINT-3 | build |
| AT-103 | L2P6-E1 (dry-run) + G-F6 (real) | build |
| AT-104 | L4P2-E4 + L4P3-E4 | build |
| AT-105 | L4P2-E3 + L2P6-E4 | build |
| AT-106 | L5P4-E2 (notification half); Gate 1 half subsystem G | build (partial) |
| AT-107 | L5P3-E3 | build |
| AT-108 | — subsystem J | unclaimed |
| AT-109 | — subsystem J | unclaimed |
| AT-110 | L3P2-E1 | build |

**Totals.** 55 build-provable in the five lanes, 6 drill-proved at L0 gates, 2 deferred to §98.4 triggers, 48 unclaimed pending **D-EE-2** (AT-029 is proved by both a build criterion and a drill, so it is counted in both the build-provable and drill-proved figures; the remaining 48 rows are neither fully build-provable, drill-proved, nor deferred). The unclaimed set is not a gap in this plan; it is the visible consequence of five subsystems having no lane in the frozen partition, and it is L0's to close before those ATs can be scheduled.

---

## 10. One-page summary — phase ledger

| Phase | Lane | Entry depends on | Exit gate id prefix | Headline AT |
|---|---|---|---|---|
| L0-P0 | L0 | repos exist, base Read, Teams grant Write | `L0P0-E*` | — (spec §98.2 Phase 1) |
| L1-P1 | L1 | L0-P0, D-EE-1 | `L1P1-E*` | — (§98.2 Phase 1 exception validator) |
| L1-P2 | L1 | L1-P1 | `L1P2-E*` | AT-049, AT-009 |
| L1-P3 | L1 | L1-P2 | `L1P3-E*` | AT-047, AT-008 |
| L1-P4 | L1 | L1-P2 | `L1P4-E*` | AT-034, AT-071, AT-075 |
| L1-P5 | L1 | L1-P2…P4 + a real schema change | `L1P5-E*` | AT-025, AT-078 |
| L4-P1 | L4 | records repo + scoped App | `L4P1-E*` | AT-110 (precondition) |
| L4-P2 | L4 | L4-P1 | `L4P2-E*` | AT-105, AT-104 |
| L4-P3 | L4 | L4-P2 | `L4P3-E*` | AT-032, AT-048 |
| L4-P4 | L4 | L4-P3, L5-P2, D-EE-4#4 | `L4P4-E*` | AT-050, AT-047 |
| L4-P5 | L4 | L4-P4, D-EE-4#1 and #7 | `L4P5-E*` | AT-044 |
| L2-P1 | L2 | L0-P0 | `L2P1-E*` | — (PARTITION rule 1) |
| L2-P2 | L2 | L2-P1, L1-P2, D-EE-4#2 | `L2P2-E*` | AT-049, AT-009 |
| L2-P3 | L2 | L2-P2 | `L2P3-E*` | — (§32 item 5) |
| L2-P4 | L2 | L2-P3, L4-P2 | `L2P4-E*` | AT-029 |
| L2-P5 | L2 | L2-P4 | `L2P5-E*` | — (§32 eleven questions) |
| L2-P6 | L2 | L2-P4, L4-P2 | `L2P6-E*` | AT-103, AT-035, AT-105 |
| L3-P1 | L3 | L1-P1…P3, L5-P1 | `L3P1-E*` | AT-102, AT-036, AT-039 |
| L3-P2 | L3 | L3-P1, L4-P1 | `L3P2-E*` | AT-110 |
| L3-P3 | L3 | L3-P2 | `L3P3-E*` | AT-032, AT-037 |
| L3-P4 | L3 | L3-P3 + D-EE-5 threshold met | `L3P4-E*` | AT-033 |
| L3-P5 | L3 | L3-P1, L1-P2, L5-P1 | `L3P5-E*` | AT-001, AT-002, AT-010 |
| L3-P6 | L3 | L3-P5 | `L3P6-E*` | AT-017, AT-005, AT-021 |
| L5-P1 | L5 | L0-P0 | `L5P1-E*` | AT-022 (precondition) |
| L5-P2 | L5 | L5-P1 | `L5P2-E*` | AT-028, AT-029, AT-031 |
| L5-P3 | L5 | L5-P1, L1-P2 | `L5P3-E*` | AT-011, AT-107 |
| L5-P4 | L5 | L5-P2 | `L5P4-E*` | AT-106 (partial) |
| L5-P5 | L5 | L5-P2, L1-P4 | `L5P5-E*` | AT-089, AT-091, AT-097, AT-098 |

**The five open decisions, restated for L0's convenience:** D-EE-1 toolchain binding (blocks L1-P1, L3-P1, L4-P3); D-EE-2 five unassigned subsystems (blocks 47 ATs); D-EE-3 acceptance-harness location (blocks nothing today, blocks the catalogue run); D-EE-4 the seven §99.3 design-open items (blocks L2P2-E4, L4P4-E3, L4P5 entry); D-EE-5 the auto-repair clean-detection threshold (blocks L3-P4 entry).
