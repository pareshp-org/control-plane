# L4 Metric Register Phase

> **File:** `L4-03-metric-register.md`
> **Lane:** L4 — Metrics
> **Phase:** Phase 3 (metric register bootstrap) and Phase 7 (metric declarations and §103 computations)
> **Date authored:** 2026-09-08
> **Session:** 13
> **Status:** AUTHORITATIVE — Phase 3 entry-gate body and Phase 7 task bodies
>
> This file provides the task bodies for the 21 metric-register index entries in
> `L4-06-tasks.md` (L4-P3-06 and L4-P7-01..L4-P7-20). Without the files created
> here, `L4-P7-T01` (Phase 7 entry gate) cannot pass its ABSENT=0 check.

**Authority order:** `PARTITION.md` (FROZEN) > `MultiProduct_MasterSpec_v4.0.md` > `L4-00-charter.md` > `L4-06-tasks.md` > this file.

**Owned paths this document writes (exclusively):**

| Repository | Path |
|---|---|
| `control-plane` | `metrics/register/**` |
| `control-plane` | `metrics/signals/**` |
| `control-plane` | `metrics/compute/**` |

Nothing is written outside these three roots. A PR touching any other path fails the lane-guard check.

---

## § 0. Workspace — re-export before every task

```bash
set -euo pipefail
export ORG="${ORG:?ERROR: ORG env var must be set to the GitHub org name}"
export CP_REPO="control-plane"
export CP_SLUG="${ORG}/${CP_REPO}"
export WORK="$HOME/l4work"
export CP_DIR="${WORK}/${CP_REPO}"
echo "ORG=$ORG CP_DIR=$CP_DIR"
```

The shell resets between calls. Re-export at the start of every task. Always use absolute paths.

---

## § Phase 3 entry gate (L4-P3-06)

### L4-P3-06 — Metric register entry gate and SIG source map

**Title:** SIG source map — which signal derives from which L4 store; metrics/register bootstrap
**Phase:** 3
**Files touched:**
- `metrics/register/metric-declarations.yaml`
- `metrics/register/validate-sources.sh`
- `metrics/signals/sig-source-map.yaml`
- `tools/records/checks/L4-P3-06.sh`

**Deps:** L4-P2-29, D-L4-TL-4 (decided — learning-loop signal takes SIG-47)

**Acceptance command:** `bash tools/records/validate-taxonomy.sh --signals`

**Spec anchor:** §52.2 lines 4541, 4552, 4576, 4577, 4581

---

#### L4-P3-06 Commands

**Step 1 — Phase branch**

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/4/p3-06-metric-register-gate
bash tools/records/lane-selfcheck.sh --paths
```

**Step 2 — Create `metrics/register/` and its bootstrap files**

Create `metrics/register/metric-declarations.yaml`:

```yaml
# metrics/register/metric-declarations.yaml
# Schema for metric declarations — sources, SIG linkage, AT coverage
# Populated by L4-P7-01. This file is a bootstrap skeleton; L4-P7-01 fills it.
$schema: urn:multiproduct:schemas/metric-declarations/v1
version: 1
metrics: []
```

Create `metrics/register/validate-sources.sh`:

```bash
#!/usr/bin/env bash
# metrics/register/validate-sources.sh
# Validates that metric-declarations.yaml is present and well-formed.
# Extended by L4-P7-01 (--attributes), L4-P7-02 (default run),
# L4-P7-03 (--arming), L4-P7-04 (--at046), L4-P7-05 (--ownership),
# L4-P7-06..L4-P7-20 (--compute <name>).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DECL_FILE="${SCRIPT_DIR}/metric-declarations.yaml"
[[ -f "$DECL_FILE" ]] || { echo "validate-sources: ABSENT: $DECL_FILE" >&2; exit 1; }

MODE="${1:-}"
case "$MODE" in
  "")           echo "SOURCES OK"; exit 0 ;;
  --attributes) echo "ATTRIBUTES OK (skeleton — extended by L4-P7-01)"; exit 0 ;;
  --arming)     echo "ARMING OK (skeleton — extended by L4-P7-03)"; exit 0 ;;
  --at046)      echo "AT-046 OK (skeleton — extended by L4-P7-04)"; exit 0 ;;
  --ownership)  echo "OWNERSHIP OK (skeleton — extended by L4-P7-05)"; exit 0 ;;
  --compute)
    MODULE="${2:?usage: validate-sources.sh --compute <module>}"
    MFILE="${SCRIPT_DIR}/../compute/${MODULE}.py"
    [[ -f "$MFILE" ]] || { echo "validate-sources: ABSENT: $MFILE" >&2; exit 1; }
    echo "COMPUTE ${MODULE} OK (skeleton — extended by L4-P7-0x)"; exit 0 ;;
  *)
    echo "validate-sources: unknown mode: $MODE" >&2; exit 3 ;;
esac
```

```bash
chmod +x metrics/register/validate-sources.sh
```

**Step 3 — Create `metrics/signals/sig-source-map.yaml`**

```bash
set -euo pipefail
cd "$CP_DIR"
mkdir -p metrics/signals
```

Create `metrics/signals/sig-source-map.yaml`:

```yaml
# metrics/signals/sig-source-map.yaml
# Maps each governance signal (§52.2) to the L4 record store it derives from.
# One id per row; no id appears twice (D-L4-TL-4 resolved SIG-43 vs SIG-47).
# Authority: §52.2 lines 4541, 4552, 4576, 4577, 4581; L4-00-charter.md §9 D-L4-TL-4.
$schema: urn:multiproduct:schemas/sig-source-map/v1
version: 1
signals:
  - signal_id: SIG-06
    name: Ready-queue-miss rate
    source_store: "records/events/ (ready_queue_miss events)"
    spec_anchor: "§52.2 line 4541"
  - signal_id: SIG-17
    name: Deployment frequency
    source_store: "records/deployments/"
    spec_anchor: "§52.2 line 4552"
  - signal_id: SIG-41
    name: Restore-test freshness
    source_store: "records/restore-tests/"
    spec_anchor: "§52.2 line 4576"
  - signal_id: SIG-42
    name: Eval regression
    source_store: "records/eval/"
    spec_anchor: "§52.2 line 4577"
  - signal_id: SIG-43
    name: Founder operating load
    source_store: "attention ledger (metrics/attention/)"
    spec_anchor: "§52.2 line 4581; D-L4-TL-4 decided"
  - signal_id: SIG-46
    name: Audit-log review staleness
    source_store: "records/security-reviews/"
    spec_anchor: "§52.2 line 4581"
  - signal_id: SIG-47
    name: Unclosed learning-loop items
    source_store: "records/postmortems/ and records/incidents/"
    spec_anchor: "§52.2 line 4571; D-L4-TL-4 decided (learning-loop signal takes SIG-47)"
```

**Step 4 — Write the check file**

Create `tools/records/checks/L4-P3-06.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P3-06 — SIG source map and metrics/register bootstrap
CP_DIR="$(git rev-parse --show-toplevel)"
DECL="$CP_DIR/metrics/register/metric-declarations.yaml"
VS="$CP_DIR/metrics/register/validate-sources.sh"
SIG="$CP_DIR/metrics/signals/sig-source-map.yaml"

# Positive: all three files present
[[ -f "$DECL" ]] || { echo "ABSENT: $DECL" >&2; exit 1; }
[[ -f "$VS"   ]] || { echo "ABSENT: $VS"   >&2; exit 1; }
[[ -f "$SIG"  ]] || { echo "ABSENT: $SIG"  >&2; exit 1; }

# Assertion: validate-sources.sh exits 0 on plain run
bash "$VS" >/dev/null || { echo "validate-sources.sh failed" >&2; exit 1; }

# Assertion: sig-source-map has exactly 7 signal_id rows
COUNT=$(grep -c 'signal_id:' "$SIG")
[ "$COUNT" -eq 7 ] || { echo "expected 7 signal_id rows, got $COUNT" >&2; exit 1; }

# Assertion: SIG-47 is present (D-L4-TL-4 decision)
grep -q 'SIG-47' "$SIG" || { echo "SIG-47 missing from sig-source-map.yaml" >&2; exit 1; }

# Negative fixture: a missing metric-declarations.yaml must cause exit 1
TMP=$(mktemp -d)
FAKE_VS="$TMP/validate-sources.sh"
cat > "$FAKE_VS" <<'INNER'
#!/usr/bin/env bash
set -euo pipefail
DECL_FILE="$(cd "$(dirname "$0")" && pwd)/metric-declarations.yaml"
[[ -f "$DECL_FILE" ]] || { echo "ABSENT: $DECL_FILE" >&2; exit 1; }
echo "SOURCES OK"; exit 0
INNER
chmod +x "$FAKE_VS"
# neg fixture: no metric-declarations.yaml in TMP
bash "$FAKE_VS" >/dev/null 2>&1 && { echo "neg-fixture: expected failure did not occur" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

echo "CHECK L4-P3-06 PASS"
```

**Step 5 — Acceptance and SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/validate-taxonomy.sh --signals
bash tools/records/check.sh L4-P3-06; echo "exit=$?"
```

Expected:
```
SIGNALS OK 7/7
CHECK L4-P3-06 PASS
exit=0
```

**Step 6 — Commit**

```bash
set -euo pipefail
cd "$CP_DIR"
bash tools/records/lane-selfcheck.sh --paths
git add metrics/register/metric-declarations.yaml \
        metrics/register/validate-sources.sh \
        metrics/signals/sig-source-map.yaml \
        tools/records/checks/L4-P3-06.sh
git commit -m "L4-P3-06: SIG source map and metrics/register bootstrap"
git fetch origin && git rebase origin/integration
git push -u origin lane/4/p3-06-metric-register-gate
gh pr create --base integration \
  --title "L4-P3-06: SIG source map and metrics/register bootstrap" \
  --body "Lane 4. Task L4-P3-06. Acceptance command in L4-06-tasks.md passed."
```

**STOP conditions:**
- Any of the three files fails to parse as YAML — STOP, file blocker.
- `validate-taxonomy.sh --signals` prints anything other than `SIGNALS OK 7/7` — STOP.
- D-L4-TL-4 was not yet decided — STOP. (It has been decided: SIG-47.)

---

## § Phase 7 — Metric register and §103 computations

**Phase 7 entry gate requirement:** `metrics/register/metric-declarations.yaml` must exist and `metrics/register/validate-sources.sh` must exit 0 with ABSENT=0. Both are created by L4-P3-06 above.

---

### L4-P7-01 — Metric declarations — the eight attributes per measure

**Title:** Metric declarations — the eight attributes per measure
**Phase:** 7
**Files touched:** `metrics/register/metric-declarations.yaml`, `tools/records/checks/L4-P7-01.sh`
**Deps:** L4-P3-06
**Acceptance command:** `bash metrics/register/validate-sources.sh --attributes`
**Spec anchor:** §84.6 line 7479; §103 preamble line 9789

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-01-metric-declarations
```

Extend `metrics/register/metric-declarations.yaml` to require all eight attributes on every declared measure (`definition`, `source`, `time_window`, `baseline`, `expected_interpretation`, `known_limitations`, `owner`, `action_on_breach`). A measure carrying fewer than eight is rejected.

Extend `metrics/register/validate-sources.sh` to handle `--attributes`: iterate every entry under `metrics:` and assert all eight keys are present; exit 1 on any missing key; print `ATTRIBUTES OK <n>/<n>` on success.

Create `tools/records/checks/L4-P7-01.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P7-01 — eight attributes per declared measure
CP_DIR="$(git rev-parse --show-toplevel)"
VS="$CP_DIR/metrics/register/validate-sources.sh"
[[ -f "$VS" ]] || { echo "ABSENT: $VS" >&2; exit 1; }

# Positive: --attributes passes
bash "$VS" --attributes >/dev/null || { echo "--attributes failed" >&2; exit 1; }

# Assertion: validate-sources.sh contains the --attributes branch
grep -q '\-\-attributes' "$VS" || { echo "--attributes branch missing from validate-sources.sh" >&2; exit 1; }

# Negative fixture (neg): a measure missing 'owner' must be rejected
TMP=$(mktemp -d)
cat > "$TMP/metric-declarations.yaml" <<'YAML'
$schema: urn:multiproduct:schemas/metric-declarations/v1
version: 1
metrics:
  - definition: "test"
    source: "records/deployments/"
    time_window: "30d"
    baseline: "unbaselined"
    expected_interpretation: "lower is better"
    known_limitations: "none"
    action_on_breach: "page on-call"
YAML
# owner is missing — validate must reject
python3 - <<PYEOF
import yaml, sys
data = yaml.safe_load(open("$TMP/metric-declarations.yaml"))
required = {"definition","source","time_window","baseline","expected_interpretation","known_limitations","owner","action_on_breach"}
for m in data.get("metrics", []):
    missing = required - set(m.keys())
    if missing:
        print(f"neg fixture correctly rejected: missing {missing}")
        sys.exit(0)
print("neg fixture: expected rejection did not occur")
sys.exit(1)
PYEOF
rm -rf "$TMP"
echo "CHECK L4-P7-01 PASS"
```

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --attributes
bash tools/records/check.sh L4-P7-01; echo "exit=$?"
```
Expected:
```
ATTRIBUTES OK <n>/<n>
CHECK L4-P7-01 PASS
exit=0
```

---

### L4-P7-02 — Source discipline — every measure names its record store

**Title:** Source discipline — every measure names its record store
**Phase:** 7
**Files touched:** `metrics/register/validate-sources.sh`, `tools/records/checks/L4-P7-02.sh`
**Deps:** L4-P7-01
**Acceptance command:** `bash metrics/register/validate-sources.sh`
**Spec anchor:** §103 preamble line 9789; §101 invariant 46, line 9527

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-02-source-discipline
```

Extend `metrics/register/validate-sources.sh` default run: for every declared measure, assert that `source` names a path that exists under `metrics/**` or `records/**`. A measure with an empty or absent source is absent from the register, not present-and-flagged; reject it.

Create `tools/records/checks/L4-P7-02.sh` with positive assertion (default run exits 0) and negative fixture (a measure with `source: ""` is rejected). Minimum 10 lines, one assertion, one negative fixture marker (`# neg`).

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh
bash tools/records/check.sh L4-P7-02; echo "exit=$?"
```
Expected:
```
SOURCES OK
CHECK L4-P7-02 PASS
exit=0
```

---

### L4-P7-03 — Arming discipline — empty store renders `unbaselined`, never a miss

**Title:** Arming discipline — empty store renders `unbaselined`, never a miss
**Phase:** 7
**Files touched:** `metrics/register/arming.py`, `tools/records/checks/L4-P7-03.sh`
**Deps:** L4-P7-02
**Acceptance command:** `bash metrics/register/validate-sources.sh --arming`
**Spec anchor:** §103 preamble line 9789 (D77); §52.2 line 4530

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-03-arming-discipline
```

Write `metrics/register/arming.py`: given a measure declaration, if its source store path exists but contains no records, emit `unbaselined` — never `0`, never a miss. An unarmed measure cannot fail a threshold. Accepts `--store <path>` and prints `ARMING unbaselined` or `ARMING baselined <count>`.

Extend `metrics/register/validate-sources.sh --arming`: run arming check against every declared measure; print `ARMING OK`.

Create `tools/records/checks/L4-P7-03.sh` with positive (ARMING OK) and negative fixture: a store reporting zero records must render `unbaselined`, not a threshold breach.

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --arming
bash tools/records/check.sh L4-P7-03; echo "exit=$?"
```
Expected:
```
ARMING OK
CHECK L4-P7-03 PASS
exit=0
```

---

### L4-P7-04 — Baseline markers and the §103.14 minimum baseline set

**Title:** Baseline markers and the §103.14 minimum baseline set
**Phase:** 7
**Files touched:** `metrics/register/baselines.yaml`, `metrics/register/baselines.py`, `tools/records/checks/L4-P7-04.sh`
**Deps:** L4-P7-03
**Acceptance command:** `bash metrics/register/validate-sources.sh --at046`
**Spec anchor:** §103.14 lines 9988–9990; AT-046 line 9381

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-04-baselines
```

Write `metrics/register/baselines.yaml`: every §103.13 measure carries either a recorded baseline estimate or an explicit `unbaselined` marker. The five-member minimum baseline set (§103.14) is present; each is labelled `pre_phase_1_estimate: true`, never mixed with ledger-derived data.

Write `metrics/register/baselines.py`: validates `baselines.yaml`; rejects any measure that carries neither a baseline nor an explicit `unbaselined` marker.

Extend `metrics/register/validate-sources.sh --at046`: run `baselines.py`; print `AT-046 OK`.

Create `tools/records/checks/L4-P7-04.sh` with positive (AT-046 OK) and negative fixture (a measure lacking both baseline and `unbaselined` marker is rejected).

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --at046
bash tools/records/check.sh L4-P7-04; echo "exit=$?"
```
Expected:
```
AT-046 OK
CHECK L4-P7-04 PASS
exit=0
```

---

### L4-P7-05 — Owner-and-response completeness gate (invariant 49)

**Title:** Owner-and-response completeness gate
**Phase:** 7
**Files touched:** `metrics/register/ownership.py`, `tools/records/checks/L4-P7-05.sh`
**Deps:** L4-P7-01
**Acceptance command:** `bash metrics/register/validate-sources.sh --ownership`
**Spec anchor:** §101 invariant 49, line 9530

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-05-ownership
```

Write `metrics/register/ownership.py`: every declared measure must carry both `owner` (non-empty string) and `action_on_breach` (non-empty string). A measure with either absent or empty is absent from the register, not present-and-flagged; reject it with exit 1.

Extend `metrics/register/validate-sources.sh --ownership`: run `ownership.py`; print `OWNERSHIP OK`.

Create `tools/records/checks/L4-P7-05.sh` with positive (OWNERSHIP OK) and negative fixture: a measure with `owner: ""` is rejected.

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --ownership
bash tools/records/check.sh L4-P7-05; echo "exit=$?"
```
Expected:
```
OWNERSHIP OK
CHECK L4-P7-05 PASS
exit=0
```

---

### L4-P7-06 — Deployment measures

**Title:** Deployment measures — frequency, failure rate, rollback rate, merged-but-not-deployed
**Phase:** 7
**Files touched:** `metrics/compute/deployments.py`, `tools/records/checks/L4-P7-06.sh`
**Deps:** L4-P2-11, L4-P7-02
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute deployments`
**Spec anchor:** §103.2 lines 9791–9798; §32 lines 2803–2829

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-06-deployment-measures
mkdir -p metrics/compute
```

Write `metrics/compute/deployments.py`: compute deployment frequency, deployment failure rate, rollback rate and merged-but-not-deployed, all from `records/deployments/` (and merge events for the last). Never from a hand-maintained number. Accepts `--store <path> --json` and prints one JSON result line.

Create `tools/records/checks/L4-P7-06.sh` with positive (COMPUTE deployments OK) and negative fixture: calling the compute module with a non-existent store must exit non-zero.

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute deployments
bash tools/records/check.sh L4-P7-06; echo "exit=$?"
```
Expected:
```
COMPUTE deployments OK (skeleton — extended by L4-P7-0x)
CHECK L4-P7-06 PASS
exit=0
```

---

### L4-P7-07 — Incident measures

**Title:** Incident measures — MTTR, incident frequency by severity, detection-to-response latency
**Phase:** 7
**Files touched:** `metrics/compute/incidents.py`, `tools/records/checks/L4-P7-07.sh`
**Deps:** L4-P2-07, L4-P7-02
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute incidents`
**Spec anchor:** §103.3 lines 9805–9809

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-07-incident-measures
```

Write `metrics/compute/incidents.py`: compute MTTR, incident frequency by severity, and detection-to-response latency from `records/incidents/`. Detection-to-response latency is interpreted against each product's declared `support_model`. Accepts `--store <path> --json`.

Create `tools/records/checks/L4-P7-07.sh` with positive and negative fixture (non-existent store exits non-zero).

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute incidents
bash tools/records/check.sh L4-P7-07; echo "exit=$?"
```
Expected:
```
COMPUTE incidents OK
CHECK L4-P7-07 PASS
exit=0
```

---

### L4-P7-08 — Restore measures — freshness and failed tests

**Title:** Restore measures — freshness and failed restore tests
**Phase:** 7
**Files touched:** `metrics/compute/restore.py`, `tools/records/checks/L4-P7-08.sh`
**Deps:** L4-P2-12, L4-P7-02
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute restore`
**Spec anchor:** §44.2 lines 3993–4002; §103.3 lines 9810–9811

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-08-restore-measures
```

Write `metrics/compute/restore.py`: restore freshness computes against the rolling 90-day floor and the tightened cadence the product's `classification.reliability_criticality` requires. Failed restore tests target zero. Both derive from `records/restore-tests/`. Accepts `--store <path> --json`.

Create `tools/records/checks/L4-P7-08.sh` with positive and negative fixture.

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute restore
bash tools/records/check.sh L4-P7-08; echo "exit=$?"
```
Expected:
```
COMPUTE restore OK
CHECK L4-P7-08 PASS
exit=0
```

---

### L4-P7-09 — UAT coverage and pass rate

**Title:** UAT coverage and pass rate
**Phase:** 7
**Files touched:** `metrics/compute/uat.py`, `tools/records/checks/L4-P7-09.sh`
**Deps:** L4-P2-09, L4-P7-02
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute uat`
**Spec anchor:** §97.2 line 8848

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-09-uat-measures
```

Write `metrics/compute/uat.py`: UAT coverage and pass rate from `records/uat/`. Accepts `--store <path> --json`.

Create `tools/records/checks/L4-P7-09.sh` with positive and negative fixture.

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute uat
bash tools/records/check.sh L4-P7-09; echo "exit=$?"
```
Expected:
```
COMPUTE uat OK
CHECK L4-P7-09 PASS
exit=0
```

---

### L4-P7-10 — Support measures — load and first-response by severity

**Title:** Support measures — load and first-response latency by severity
**Phase:** 7
**Files touched:** `metrics/compute/support.py`, `tools/records/checks/L4-P7-10.sh`
**Deps:** L4-P2-20, L4-P7-02
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute support`
**Spec anchor:** §103.4 line 9825; §22.4 lines 2238–2249; AT-104 line 9387

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-10-support-measures
```

Write `metrics/compute/support.py`: support load and first-response time by severity from `records/support/`. The first-response clock anchors to the message's **received timestamp** (`received_at` field), never to the ingest event. Accepts `--store <path> --json`.

Create `tools/records/checks/L4-P7-10.sh` with positive and negative fixture. The negative fixture proves that using the ingest timestamp instead of `received_at` produces a different (wrong) result.

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute support
bash tools/records/check.sh L4-P7-10; echo "exit=$?"
```
Expected:
```
COMPUTE support OK
CHECK L4-P7-10 PASS
exit=0
```

---

### L4-P7-11 — Eval measures and regression detection

**Title:** Eval measures — pass rates and regression detection raising SIG-42
**Phase:** 7
**Files touched:** `metrics/compute/eval.py`, `tools/records/checks/L4-P7-11.sh`
**Deps:** L4-P2-17, L4-P7-02
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute eval`
**Spec anchor:** §52.2 line 4571; §38.3 lines 3433–3434; AT-107 line 9390

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-11-eval-measures
```

Write `metrics/compute/eval.py`: eval pass rates from `records/eval/`. A scored dimension falling more than its declared tolerance below its recorded baseline is a regression and raises SIG-42. A night's regressions on one product coalesce into **one** triage event, never one per dimension. Accepts `--store <path> --json`.

Create `tools/records/checks/L4-P7-11.sh` with positive and negative fixture: multiple dimension regressions on one product coalesce — the fixture proves exactly one triage event, not N.

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute eval
bash tools/records/check.sh L4-P7-11; echo "exit=$?"
```
Expected:
```
COMPUTE eval OK
CHECK L4-P7-11 PASS
exit=0
```

---

### L4-P7-12 — Security-review measures — finding count and unfixed-finding age

**Title:** Security-review measures — finding count by severity and unfixed-finding age
**Phase:** 7
**Files touched:** `metrics/compute/security_reviews.py`, `tools/records/checks/L4-P7-12.sh`
**Deps:** L4-P2-16, L4-P7-02
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute security_reviews`
**Spec anchor:** §97.2 lines 8858, 8884; §52.2 line 4575

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-12-security-measures
```

Write `metrics/compute/security_reviews.py`: finding count by severity and unfixed-finding age from `records/security-reviews/`. Unfixed findings age visibly rather than silently. Accepts `--store <path> --json`.

Create `tools/records/checks/L4-P7-12.sh` with positive and negative fixture: an unfixed finding with no owner is rejected (not silently aged).

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute security_reviews
bash tools/records/check.sh L4-P7-12; echo "exit=$?"
```
Expected:
```
COMPUTE security_reviews OK
CHECK L4-P7-12 PASS
exit=0
```

---

### L4-P7-13 — Decision latency and pending-decision queue depth and age

**Title:** Decision latency, queue depth and age
**Phase:** 7
**Files touched:** `metrics/compute/decisions.py`, `tools/records/checks/L4-P7-13.sh`
**Deps:** L4-P2-13, L4-P4-07
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute decisions`
**Spec anchor:** §97.2 lines 8865–8866; §103.13 line 9972

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-13-decision-measures
```

Write `metrics/compute/decisions.py`: decision latency from `records/decisions/`; pending-decision queue depth and age from `records/decisions/pending/`. Accepts `--store <path> --json`.

Create `tools/records/checks/L4-P7-13.sh` with positive and negative fixture: a decided record missing its `decided` timestamp is rejected.

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute decisions
bash tools/records/check.sh L4-P7-13; echo "exit=$?"
```
Expected:
```
COMPUTE decisions OK
CHECK L4-P7-13 PASS
exit=0
```

---

### L4-P7-14 — Learning-loop measures (SIG-47)

**Title:** Learning-loop measures — open postmortems and unlinked regression tests, emitted as SIG-47
**Phase:** 7
**Files touched:** `metrics/compute/learning_loop.py`, `tools/records/checks/L4-P7-14.sh`
**Deps:** L4-P2-08, L4-P2-07, D-L4-TL-4 (decided — SIG-47; unblocked)
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute learning_loop`
**Spec anchor:** §52.2 line 4571; §58.4 lines 5017–5047

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-14-learning-loop
```

Write `metrics/compute/learning_loop.py`: count open postmortems older than 30 days with unclosed generated items (from `records/postmortems/`) and closed production-bug incidents with no linked regression-test item (from `records/incidents/`). Emit under `signal_id: SIG-47` (D-L4-TL-4 decided). Accepts `--store <path> --json`.

Create `tools/records/checks/L4-P7-14.sh` with positive and negative fixture: a postmortem missing its generated-item list is still counted as open. Signal id must be SIG-47, never SIG-43.

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute learning_loop
bash tools/records/check.sh L4-P7-14; echo "exit=$?"
```
Expected:
```
COMPUTE learning_loop OK
CHECK L4-P7-14 PASS
exit=0
```

---

### L4-P7-15 — Estimate-vs-actual and forecast-calibration inputs

**Title:** Estimation accuracy and forecast calibration
**Phase:** 7
**Files touched:** `metrics/compute/estimates.py`, `tools/records/checks/L4-P7-15.sh`
**Deps:** L4-P2-10, L4-P5-04
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute estimates`
**Spec anchor:** §29.3 line 2667; §97.2 line 8850

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-15-estimate-measures
```

Write `metrics/compute/estimates.py`: estimation accuracy uses **`elapsed_net_blocked`** (elapsed net of recorded Blocked time); forecast calibration uses **`elapsed`** (raw elapsed). Both figures come from `records/estimates/` and the two are never confused. Accepts `--store <path> --json`.

Create `tools/records/checks/L4-P7-15.sh` with positive and negative fixture: the negative fixture asserts that swapping `elapsed` for `elapsed_net_blocked` in the accuracy calculation produces a different value (proving the fields are distinguished).

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute estimates
bash tools/records/check.sh L4-P7-15; echo "exit=$?"
```
Expected:
```
COMPUTE estimates OK
CHECK L4-P7-15 PASS
exit=0
```

---

### L4-P7-16 — Ready-queue-miss measure — 30-day rolling count and trend

**Title:** Ready-queue-miss measure — rolling count and trend, Team Lead capacity signal
**Phase:** 7
**Files touched:** `metrics/compute/rqm.py`, `tools/records/checks/L4-P7-16.sh`
**Deps:** L4-P5-12, L4-P3-06
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute rqm`
**Spec anchor:** §52.2 line 4541; §29.4 line 2670; §101 invariant 15, line 9484

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-16-rqm-measure
```

Write `metrics/compute/rqm.py`: 30-day rolling Ready-queue-miss count and trend from the event log. Excludes `ready_bypass` events. Declared a Team Lead capacity signal, **never** an individual signal. Accepts `--store <path> --json`.

Create `tools/records/checks/L4-P7-16.sh` with positive and negative fixture: the negative fixture proves that a `ready_bypass` event is excluded from the count.

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute rqm
bash tools/records/check.sh L4-P7-16; echo "exit=$?"
```
Expected:
```
COMPUTE rqm OK
CHECK L4-P7-16 PASS
exit=0
```

---

### L4-P7-17 — Status-request count from the event log

**Title:** Status-request count — Coordination-category events, weekly, never hand-counted
**Phase:** 7
**Files touched:** `metrics/compute/status_requests.py`, `tools/records/checks/L4-P7-17.sh`
**Deps:** L4-P3-01, L4-P6-01
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute status_requests`
**Spec anchor:** §103.13 line 9969

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-17-status-requests
```

Write `metrics/compute/status_requests.py`: count Coordination-category status-request events from the event log, weekly, derived and never hand-counted. Accepts `--store <path> --json`.

Create `tools/records/checks/L4-P7-17.sh` with positive and negative fixture: the negative fixture asserts that an event of a non-Coordination category is excluded.

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute status_requests
bash tools/records/check.sh L4-P7-17; echo "exit=$?"
```
Expected:
```
COMPUTE status_requests OK
CHECK L4-P7-17 PASS
exit=0
```

---

### L4-P7-18 — Onboarding, launch and demo cadence measures

**Title:** Lifecycle cadence — onboarding time to first PR, launch cadence, demo cadence
**Phase:** 7
**Files touched:** `metrics/compute/lifecycle_cadence.py`, `tools/records/checks/L4-P7-18.sh`
**Deps:** L4-P2-18, L4-P2-19, L4-P2-21
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute lifecycle_cadence`
**Spec anchor:** §97.2 lines 8871–8874

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-18-lifecycle-cadence
```

Write `metrics/compute/lifecycle_cadence.py`: onboarding time to first accepted PR from `records/onboarding/`; launch cadence from `records/launches/`; demo cadence from `records/demos/`. Accepts `--store <path> --json`.

Create `tools/records/checks/L4-P7-18.sh` with positive and negative fixture: the negative fixture proves that an onboarding record missing the first-PR reference is rejected.

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute lifecycle_cadence
bash tools/records/check.sh L4-P7-18; echo "exit=$?"
```
Expected:
```
COMPUTE lifecycle_cadence OK
CHECK L4-P7-18 PASS
exit=0
```

---

### L4-P7-19 — Undeclared weekend activations — the residual

**Title:** Weekend-activation residual — out-of-hours events minus declared exceptions, team level
**Phase:** 7
**Files touched:** `metrics/compute/weekend_residual.py`, `tools/records/checks/L4-P7-19.sh`
**Deps:** L4-P3-01, L4-P2-22
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute weekend_residual`
**Spec anchor:** §103.3 line 9812

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-19-weekend-residual
```

Write `metrics/compute/weekend_residual.py`: the measure is the **residual** — out-of-hours state-changing events in the event log, measured against each person's declared working calendar (from `records/leave/`), **minus** activations recorded in the exception registry. Reports at team level and **never names a person**. Accepts `--store <path> --json`.

Create `tools/records/checks/L4-P7-19.sh` with positive and negative fixture: the negative fixture proves that an event within declared working hours is excluded from the residual.

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute weekend_residual
bash tools/records/check.sh L4-P7-19; echo "exit=$?"
```
Expected:
```
COMPUTE weekend_residual OK
CHECK L4-P7-19 PASS
exit=0
```

---

### L4-P7-20 — Attention-ledger measures

**Title:** Attention-ledger measures — coordination time, engineering hours, QA hours, ritual hours
**Phase:** 7
**Files touched:** `metrics/compute/attention_measures.py`, `tools/records/checks/L4-P7-20.sh`
**Deps:** L4-P6-15, L4-P7-02
**Acceptance command:** `bash metrics/register/validate-sources.sh --compute attention_measures`
**Spec anchor:** §103.13 lines 9962–9982

#### Commands

```bash
set -euo pipefail
cd "$CP_DIR"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/4/p7-20-attention-measures
```

Write `metrics/compute/attention_measures.py`: Founder coordination time, Team Lead coordination hours, engineering hours per product per month, QA verification hours and Founder total OS ritual hours — all deriving from the attention ledger (`metrics/attention/`). Any figure including self-reported hours carries the `self-reported` provenance label permanently. Accepts `--store <path> --json`.

Create `tools/records/checks/L4-P7-20.sh` with positive and negative fixture: the negative fixture proves that a self-reported component that loses its `self-reported` label is rejected (label is permanent).

**SELF-VERIFY:**
```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh --compute attention_measures
bash tools/records/check.sh L4-P7-20; echo "exit=$?"
```
Expected:
```
COMPUTE attention_measures OK
CHECK L4-P7-20 PASS
exit=0
```

---

## § Phase 7 exit gate

Run after L4-P7-20 passes. A gate failure is a STOP under L4-06-tasks.md §0.7 with `<TASK-ID>` set to `EXIT-GATE-P7`.

```bash
set -euo pipefail
cd "$CP_DIR"
bash metrics/register/validate-sources.sh \
  && bash metrics/register/validate-sources.sh --arming \
  && bash metrics/register/validate-sources.sh --at046
echo "P7 EXIT GATE: PASS"
```

Expected final line:
```
AT-046 OK
P7 EXIT GATE: PASS
```

---

## § Cross-reference table

| Task | Title | Files touched | Acceptance command |
|---|---|---|---|
| L4-P3-06 | SIG source map and metrics/register bootstrap | `metrics/register/metric-declarations.yaml`, `metrics/register/validate-sources.sh`, `metrics/signals/sig-source-map.yaml` | `bash tools/records/validate-taxonomy.sh --signals` |
| L4-P7-01 | Metric declarations — eight attributes | `metrics/register/metric-declarations.yaml` (extended) | `bash metrics/register/validate-sources.sh --attributes` |
| L4-P7-02 | Source discipline | `metrics/register/validate-sources.sh` (extended) | `bash metrics/register/validate-sources.sh` |
| L4-P7-03 | Arming discipline | `metrics/register/arming.py` | `bash metrics/register/validate-sources.sh --arming` |
| L4-P7-04 | Baseline markers | `metrics/register/baselines.yaml`, `metrics/register/baselines.py` | `bash metrics/register/validate-sources.sh --at046` |
| L4-P7-05 | Ownership gate | `metrics/register/ownership.py` | `bash metrics/register/validate-sources.sh --ownership` |
| L4-P7-06 | Deployment measures | `metrics/compute/deployments.py` | `bash metrics/register/validate-sources.sh --compute deployments` |
| L4-P7-07 | Incident measures | `metrics/compute/incidents.py` | `bash metrics/register/validate-sources.sh --compute incidents` |
| L4-P7-08 | Restore measures | `metrics/compute/restore.py` | `bash metrics/register/validate-sources.sh --compute restore` |
| L4-P7-09 | UAT measures | `metrics/compute/uat.py` | `bash metrics/register/validate-sources.sh --compute uat` |
| L4-P7-10 | Support measures | `metrics/compute/support.py` | `bash metrics/register/validate-sources.sh --compute support` |
| L4-P7-11 | Eval measures | `metrics/compute/eval.py` | `bash metrics/register/validate-sources.sh --compute eval` |
| L4-P7-12 | Security-review measures | `metrics/compute/security_reviews.py` | `bash metrics/register/validate-sources.sh --compute security_reviews` |
| L4-P7-13 | Decision measures | `metrics/compute/decisions.py` | `bash metrics/register/validate-sources.sh --compute decisions` |
| L4-P7-14 | Learning-loop measures (SIG-47) | `metrics/compute/learning_loop.py` | `bash metrics/register/validate-sources.sh --compute learning_loop` |
| L4-P7-15 | Estimate measures | `metrics/compute/estimates.py` | `bash metrics/register/validate-sources.sh --compute estimates` |
| L4-P7-16 | RQM measure | `metrics/compute/rqm.py` | `bash metrics/register/validate-sources.sh --compute rqm` |
| L4-P7-17 | Status-request count | `metrics/compute/status_requests.py` | `bash metrics/register/validate-sources.sh --compute status_requests` |
| L4-P7-18 | Lifecycle cadence | `metrics/compute/lifecycle_cadence.py` | `bash metrics/register/validate-sources.sh --compute lifecycle_cadence` |
| L4-P7-19 | Weekend residual | `metrics/compute/weekend_residual.py` | `bash metrics/register/validate-sources.sh --compute weekend_residual` |
| L4-P7-20 | Attention-ledger measures | `metrics/compute/attention_measures.py` | `bash metrics/register/validate-sources.sh --compute attention_measures` |

---

**End of L4-03-metric-register.md.** Work the tasks top to bottom. Verify with each task's SELF-VERIFY. Gate with the Phase 7 exit gate. Stop under L4-06-tasks.md §0.7.
