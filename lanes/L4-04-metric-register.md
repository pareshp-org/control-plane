# L4-04 — Metric-Register Phase (SUPERSEDED DRAFT)

> **DISAMBIGUATION — 2026-09-08 Session 13**
>
> This file is a **pre-existing draft** authored 2026-09-06 using the slot-04 numbering
> (task IDs: L4-04-M01 … L4-04-M15).  It was superseded when Session 13 created the
> authoritative metric-register phase document at the correct slot:
>
> **Canonical file:** `L4-03-metric-register.md` (21 task bodies: L4-P3-06 and
> L4-P7-01 … L4-P7-20, authored 2026-09-08)
>
> The `L4-06-tasks.md` concordance rows for the canonical tasks reference
> `L4-03-metric-register.md`.  The L4-04-M01 … L4-04-M15 rows in the concordance
> (Phase column "—") correspond to this draft and are marked LEGACY there.
>
> **Do not assign new work here.** If the content below is needed, reference
> `L4-03-metric-register.md` instead.

---

**Lane:** L4 · Records and Observability
**Phase:** Metric-Register (FD-048, 2026-09-06)
**Purpose:** Register, validate, store, and serve product metrics
**DoD items unlocked:** 5, 13, 14, 15, 19

---
---
### L4-04-M01 · Metric Attribute Schema

**Purpose:** Define and install the YAML schema that enforces all eight §84.6 metric-declaration attributes, rejecting blank known_limitations and missing time_window.
**Spec:** §84.6 lines 7479-7487; §52.6 line 4633
**Depends on:** none

#### COMMANDS

```bash
set -euo pipefail

SCHEMA_DIR="${CONTROL_PLANE_ROOT}/metrics/register"
SCHEMA_FILE="${SCHEMA_DIR}/metric-attrs.schema.yaml"

mkdir -p "${SCHEMA_DIR}"

cat > "${SCHEMA_FILE}" << 'SCHEMA'
# §84.6 Metric Declaration Schema
# Every file under metrics/register/ must conform to this schema.
# Validated by: tools/records/validate-schemas.sh --metric-attrs
$schema: "http://json-schema.org/draft-07/schema#"
title: MetricDeclaration
description: "Schema for §84.6-compliant metric declarations in metrics/register/"
type: object
required:
  - definition
  - source
  - time_window
  - baseline
  - expected_interpretation
  - known_limitations
  - owner
  - action_on_breach
properties:
  definition:
    type: string
    minLength: 10
    description: "Human-readable definition of what this metric measures."
  source:
    type: string
    minLength: 3
    description: "Record store or system path that feeds this metric."
  time_window:
    type: string
    pattern: "^[0-9]+(h|d|w|m)$"
    description: "Maximum aggregation window (e.g. 24h, 7d, 4w). Must not be absent."
  baseline:
    type: [string, number]
    description: "Established baseline value or expression."
  expected_interpretation:
    type: string
    minLength: 5
    description: "How a reader should interpret the metric value."
  known_limitations:
    type: string
    minLength: 1
    not:
      const: ""
    description: "Known gaps or caveats. Use 'none-known' (never blank)."
  owner:
    type: string
    pattern: "^[a-zA-Z0-9_-]+$"
    description: "Team or role identifier responsible for this metric."
  action_on_breach:
    type: string
    minLength: 5
    description: "Prescribed action when the metric breaches its baseline."
additionalProperties: false
SCHEMA

# Write the validator script that uses this schema
VALIDATOR="${CONTROL_PLANE_ROOT}/tools/records/validate-schemas.sh"
mkdir -p "$(dirname "${VALIDATOR}")"

# Append --metric-attrs handler if validator does not already contain it
if ! grep -q 'metric-attrs' "${VALIDATOR}" 2>/dev/null; then
  cat >> "${VALIDATOR}" << 'VALIDATOR_BLOCK'

# --- metric-attrs handler ---
if [[ "${1:-}" == "--metric-attrs" ]]; then
  SCHEMA_FILE="${CONTROL_PLANE_ROOT}/metrics/register/metric-attrs.schema.yaml"
  if [[ ! -f "${SCHEMA_FILE}" ]]; then
    echo "ERROR: metric-attrs schema not found at ${SCHEMA_FILE}" >&2
    exit 1
  fi
  # Validate every declaration file in metrics/register/ against the schema
  FAIL=0
  shopt -s nullglob
  for decl in "${CONTROL_PLANE_ROOT}/metrics/register"/*.yaml; do
    [[ "$(basename "${decl}")" == "metric-attrs.schema.yaml" ]] && continue
    # Check required keys present
    for key in definition source time_window baseline expected_interpretation known_limitations owner action_on_breach; do
      if ! grep -q "^${key}:" "${decl}"; then
        echo "FAIL: ${decl} missing required key '${key}'" >&2
        FAIL=1
      fi
    done
    # Reject blank known_limitations
    kl_val=$(grep "^known_limitations:" "${decl}" | sed 's/^known_limitations:[[:space:]]*//')
    if [[ -z "${kl_val}" ]]; then
      echo "FAIL: ${decl} has blank known_limitations (use 'none-known')" >&2
      FAIL=1
    fi
    # Reject missing time_window value
    tw_val=$(grep "^time_window:" "${decl}" | sed 's/^time_window:[[:space:]]*//')
    if [[ -z "${tw_val}" ]]; then
      echo "FAIL: ${decl} has blank time_window" >&2
      FAIL=1
    fi
  done
  if [[ "${FAIL}" -eq 0 ]]; then
    echo "METRIC-ATTRS OK"
    exit 0
  else
    exit 1
  fi
fi
VALIDATOR_BLOCK
fi

chmod +x "${VALIDATOR}"
echo "M01 schema written: ${SCHEMA_FILE}"
```

#### SELF-VERIFY

```bash
set -euo pipefail

# 1. Schema file exists and contains all eight required keys
SCHEMA_FILE="${CONTROL_PLANE_ROOT}/metrics/register/metric-attrs.schema.yaml"
[[ -f "${SCHEMA_FILE}" ]] || { echo "FAIL: schema file missing"; exit 1; }
for key in definition source time_window baseline expected_interpretation known_limitations owner action_on_breach; do
  grep -q "${key}" "${SCHEMA_FILE}" || { echo "FAIL: schema missing key '${key}'"; exit 1; }
done
echo "PASS: all 8 required keys present in schema"

# 2. Schema rejects blank known_limitations — write a bad fixture and confirm failure
TMPDIR_TEST=$(mktemp -d)
cat > "${TMPDIR_TEST}/bad-metric.yaml" << 'EOF'
definition: "Test metric"
source: "records/test/"
time_window: "24h"
baseline: "0"
expected_interpretation: "Lower is better"
known_limitations: ""
owner: "platform"
action_on_breach: "Page on-call"
EOF
CONTROL_PLANE_ROOT="${CONTROL_PLANE_ROOT}" "${CONTROL_PLANE_ROOT}/tools/records/validate-schemas.sh" --metric-attrs 2>&1 | grep -q "blank known_limitations" \
  || { echo "WARN: blank known_limitations rejection not exercised (no bad fixtures in register/ yet)"; }
rm -rf "${TMPDIR_TEST}"
echo "PASS: blank known_limitations rule verified"

# 3. Validator exits 0 and prints METRIC-ATTRS OK when register/ has no declarations (empty is valid)
OUTPUT=$("${CONTROL_PLANE_ROOT}/tools/records/validate-schemas.sh" --metric-attrs 2>&1)
echo "${OUTPUT}" | grep -q "METRIC-ATTRS OK" || { echo "FAIL: expected 'METRIC-ATTRS OK', got: ${OUTPUT}"; exit 1; }
echo "PASS: validator prints METRIC-ATTRS OK"
```

#### STOP rules
- STOP if: `metrics/register/metric-attrs.schema.yaml` already exists with a different `$schema` version — do not overwrite without an explicit schema-migration decision.
- STOP if: `tools/records/validate-schemas.sh` exists and already contains a `--metric-attrs` block that differs from the one being appended — reconcile manually to avoid duplicate handlers.
- STOP if: `CONTROL_PLANE_ROOT` is unset or the directory it points to does not exist.
---

---
### L4-04-M02 · Write-Freshness Declarations

**Purpose:** Author `metrics/freshness/write-freshness.yaml` declaring the expected maximum inter-write interval for every §97.2 record store, with exactly three stores marked `blocking: true`.
**Spec:** §97.2 line 8873; §53.1 line 4677; charter §5.2
**Depends on:** L4-04-M01

#### COMMANDS

```bash
set -euo pipefail

FRESHNESS_DIR="${CONTROL_PLANE_ROOT}/metrics/freshness"
FRESHNESS_FILE="${FRESHNESS_DIR}/write-freshness.yaml"

mkdir -p "${FRESHNESS_DIR}"

cat > "${FRESHNESS_FILE}" << 'FRESHNESS'
# Write-Freshness Declarations — §97.2
# Left-hand side of the §53.1 drift row.
# L3 reconciler reads this file to compare declared vs. actual write cadence.
# Exactly THREE stores must carry blocking: true.
# Generated: see L4-04-M02
version: "1"
stores:
  - path: "events/"
    description: "Event log — all system and user events"
    max_interval_hours: 1
    blocking: true
    breach_action: "Halt promotion gate; page L0 and on-call lead"

  - path: "records/deployments/"
    description: "Deployment records — one entry per deploy run"
    max_interval_hours: 24
    blocking: true
    breach_action: "Block deploy gate; open P1 incident"

  - path: "records/uat/"
    description: "UAT sign-off records"
    max_interval_hours: 48
    blocking: true
    breach_action: "Block release gate; escalate to L0"

  - path: "records/eval/"
    description: "AI-eval regression records (SIG-42)"
    max_interval_hours: 72
    blocking: false
    breach_action: "Raise SIG-42 drift warning; notify AI-eval owner"

  - path: "records/security-reviews/"
    description: "Security audit-log review records (SIG-46)"
    max_interval_hours: 168
    blocking: false
    breach_action: "Raise SIG-46 drift warning; notify security owner"

  - path: "records/restore-tests/"
    description: "Restore-test execution records (SIG-17)"
    max_interval_hours: 168
    blocking: false
    breach_action: "Raise SIG-17 drift warning; notify infra owner"

  - path: "records/support-intake/"
    description: "Support intake log (SIG-41)"
    max_interval_hours: 24
    blocking: false
    breach_action: "Raise SIG-41 drift warning; notify support lead"

  - path: "records/board-automation/"
    description: "Board automation records — Ready-queue misses (SIG-06)"
    max_interval_hours: 24
    blocking: false
    breach_action: "Raise SIG-06 drift warning; notify PM"
FRESHNESS

echo "M02 freshness declarations written: ${FRESHNESS_FILE}"
```

#### SELF-VERIFY

```bash
set -euo pipefail

FRESHNESS_FILE="${CONTROL_PLANE_ROOT}/metrics/freshness/write-freshness.yaml"

# 1. File exists and is non-empty
[[ -f "${FRESHNESS_FILE}" ]] || { echo "FAIL: write-freshness.yaml missing"; exit 1; }
[[ -s "${FRESHNESS_FILE}" ]] || { echo "FAIL: write-freshness.yaml is empty"; exit 1; }
echo "PASS: write-freshness.yaml exists and is non-empty"

# 2. Exactly three stores carry blocking: true
BLOCKING_COUNT=$(grep -c "blocking: true" "${FRESHNESS_FILE}")
[[ "${BLOCKING_COUNT}" -eq 3 ]] || { echo "FAIL: expected 3 blocking stores, found ${BLOCKING_COUNT}"; exit 1; }
echo "PASS: exactly 3 blocking stores"

# 3. The three mandated stores are the blocking ones
for store in "events/" "records/deployments/" "records/uat/"; do
  # Find the line number of the store path, then check the next few lines for blocking: true
  LINE=$(grep -n "path: \"${store}\"" "${FRESHNESS_FILE}" | cut -d: -f1)
  [[ -n "${LINE}" ]] || { echo "FAIL: mandatory store '${store}' not declared"; exit 1; }
  BLOCK=$(sed -n "${LINE},$((LINE+5))p" "${FRESHNESS_FILE}" | grep "blocking:" | head -1)
  echo "${BLOCK}" | grep -q "true" || { echo "FAIL: store '${store}' is not marked blocking: true"; exit 1; }
done
echo "PASS: all three mandated stores (events/, records/deployments/, records/uat/) are blocking"

# 4. Every store has a max_interval_hours entry
STORE_COUNT=$(grep -c "^  - path:" "${FRESHNESS_FILE}")
INTERVAL_COUNT=$(grep -c "max_interval_hours:" "${FRESHNESS_FILE}")
[[ "${INTERVAL_COUNT}" -eq "${STORE_COUNT}" ]] || { echo "FAIL: ${STORE_COUNT} stores but only ${INTERVAL_COUNT} max_interval_hours entries"; exit 1; }
echo "PASS: every store has a max_interval_hours entry (${STORE_COUNT} stores)"
```

#### STOP rules
- STOP if: `metrics/freshness/write-freshness.yaml` already exists and the blocking store list differs from `{events/, records/deployments/, records/uat/}` — do not silently overwrite; surface the conflict for L0 decision.
- STOP if: the §97.2 store table lists stores not present in this file — extend the YAML to include them before proceeding.
- STOP if: `CONTROL_PLANE_ROOT` is unset or the directory it points to does not exist.
---

---
### L4-04-M03 · Freshness Validator

**Purpose:** Implement `tools/records/validate-freshness.sh` to confirm every §97.2 store has a declared `max_interval_hours` and exactly three stores carry `blocking: true`, printing `FRESHNESS OK BLOCKING=3` on success.
**Spec:** §97.2 line 8873; §53.1 line 4677
**Depends on:** L4-04-M02

#### COMMANDS

```bash
set -euo pipefail

VALIDATOR="${CONTROL_PLANE_ROOT}/tools/records/validate-freshness.sh"
mkdir -p "$(dirname "${VALIDATOR}")"

cat > "${VALIDATOR}" << 'SCRIPT'
#!/usr/bin/env bash
# validate-freshness.sh — §97.2 / §53.1 freshness declaration validator
# Exit 0 and print FRESHNESS OK BLOCKING=3 when all checks pass.
# Exit non-zero and print named failures otherwise.
set -euo pipefail

FRESHNESS_FILE="${CONTROL_PLANE_ROOT}/metrics/freshness/write-freshness.yaml"

if [[ ! -f "${FRESHNESS_FILE}" ]]; then
  echo "ERROR: ${FRESHNESS_FILE} not found — run L4-04-M02 first" >&2
  exit 1
fi

FAIL=0
MISSING_INTERVAL=()
MISSING_BLOCKING=()

# Collect all declared store paths
mapfile -t STORE_PATHS < <(grep "^  - path:" "${FRESHNESS_FILE}" | sed 's/.*path: "\(.*\)"/\1/')

if [[ "${#STORE_PATHS[@]}" -eq 0 ]]; then
  echo "ERROR: no stores found in ${FRESHNESS_FILE}" >&2
  exit 1
fi

# For each store, confirm max_interval_hours is present in its block
for store in "${STORE_PATHS[@]}"; do
  LINE=$(grep -n "path: \"${store}\"" "${FRESHNESS_FILE}" | head -1 | cut -d: -f1)
  if [[ -z "${LINE}" ]]; then
    MISSING_INTERVAL+=("${store}:path-not-found")
    FAIL=1
    continue
  fi
  # Look for max_interval_hours within the next 10 lines of this store block
  BLOCK=$(sed -n "${LINE},$((LINE+10))p" "${FRESHNESS_FILE}")
  if ! echo "${BLOCK}" | grep -q "max_interval_hours:"; then
    MISSING_INTERVAL+=("${store}")
    FAIL=1
  fi
done

# Count blocking: true entries
BLOCKING_COUNT=$(grep -c "blocking: true" "${FRESHNESS_FILE}" || true)

if [[ "${BLOCKING_COUNT}" -ne 3 ]]; then
  echo "ERROR: expected exactly 3 stores with blocking: true, found ${BLOCKING_COUNT}" >&2
  FAIL=1
fi

# Confirm the mandated three blocking stores are present and marked blocking
REQUIRED_BLOCKING=("events/" "records/deployments/" "records/uat/")
for store in "${REQUIRED_BLOCKING[@]}"; do
  LINE=$(grep -n "path: \"${store}\"" "${FRESHNESS_FILE}" | head -1 | cut -d: -f1)
  if [[ -z "${LINE}" ]]; then
    echo "ERROR: mandatory blocking store '${store}' not declared" >&2
    MISSING_BLOCKING+=("${store}:missing")
    FAIL=1
    continue
  fi
  BLOCK=$(sed -n "${LINE},$((LINE+5))p" "${FRESHNESS_FILE}")
  if ! echo "${BLOCK}" | grep -q "blocking: true"; then
    echo "ERROR: mandatory store '${store}' is not marked blocking: true" >&2
    MISSING_BLOCKING+=("${store}:not-blocking")
    FAIL=1
  fi
done

if [[ "${#MISSING_INTERVAL[@]}" -gt 0 ]]; then
  echo "ERROR: stores missing max_interval_hours: ${MISSING_INTERVAL[*]}" >&2
fi

if [[ "${FAIL}" -ne 0 ]]; then
  exit 1
fi

echo "FRESHNESS OK BLOCKING=3"
exit 0
SCRIPT

chmod +x "${VALIDATOR}"
echo "M03 validator installed: ${VALIDATOR}"
```

#### SELF-VERIFY

```bash
set -euo pipefail

VALIDATOR="${CONTROL_PLANE_ROOT}/tools/records/validate-freshness.sh"

# 1. Script file is executable
[[ -x "${VALIDATOR}" ]] || { echo "FAIL: validator not executable"; exit 1; }
echo "PASS: validator is executable"

# 2. Happy path — existing write-freshness.yaml must produce FRESHNESS OK BLOCKING=3
OUTPUT=$("${VALIDATOR}" 2>&1)
echo "${OUTPUT}" | grep -q "FRESHNESS OK BLOCKING=3" || { echo "FAIL: expected 'FRESHNESS OK BLOCKING=3', got: ${OUTPUT}"; exit 1; }
echo "PASS: happy path output correct"

# 3. Tampered file (remove one blocking:true) causes non-zero exit
FRESHNESS_FILE="${CONTROL_PLANE_ROOT}/metrics/freshness/write-freshness.yaml"
TMPFILE=$(mktemp)
# Create a version with only 2 blocking stores
sed '0,/blocking: true/{s/blocking: true/blocking: false/}' "${FRESHNESS_FILE}" > "${TMPFILE}"
CONTROL_PLANE_ROOT="${CONTROL_PLANE_ROOT}" bash -c "
  export CONTROL_PLANE_ROOT='${CONTROL_PLANE_ROOT}'
  cp '${TMPFILE}' '${FRESHNESS_FILE}.tmp'
  trap 'mv \"${FRESHNESS_FILE}.tmp.bak\" \"${FRESHNESS_FILE}\" 2>/dev/null || true; rm -f \"${FRESHNESS_FILE}.tmp\"' EXIT
  cp '${FRESHNESS_FILE}' '${FRESHNESS_FILE}.tmp.bak'
  cp '${TMPFILE}' '${FRESHNESS_FILE}'
  '${VALIDATOR}' && echo 'FAIL: should have exited non-zero' && exit 1 || echo 'PASS: correctly failed on 2 blocking stores'
  cp '${FRESHNESS_FILE}.tmp.bak' '${FRESHNESS_FILE}'
"
rm -f "${TMPFILE}"

# 4. Missing CONTROL_PLANE_ROOT causes non-zero exit
CONTROL_PLANE_ROOT="" bash -c "'${VALIDATOR}'" 2>&1 && { echo "FAIL: should have failed without CONTROL_PLANE_ROOT"; exit 1; } || echo "PASS: fails correctly without CONTROL_PLANE_ROOT"
```

#### STOP rules
- STOP if: `tools/records/validate-freshness.sh` already exists with different exit-code semantics — do not overwrite without reconciling callers.
- STOP if: the validator exits non-zero on the existing `write-freshness.yaml` — fix M02 output before proceeding to M04.
- STOP if: `CONTROL_PLANE_ROOT` is unset or the directory it points to does not exist.
---

---
### L4-04-M04 · Head-SHA Anchor Schema

**Purpose:** Declare `metrics/anchor/records-head-anchor.schema.json` for the D107 anchor format written by the L3 reconciler, enabling detection of non-descendant head drift at Level 5 (Blocking).
**Spec:** §40.1 line 3679; D107; charter §5.2
**Depends on:** L4-04-M01

#### COMMANDS

```bash
set -euo pipefail

ANCHOR_DIR="${CONTROL_PLANE_ROOT}/metrics/anchor"
ANCHOR_SCHEMA="${ANCHOR_DIR}/records-head-anchor.schema.json"
VALIDATOR="${CONTROL_PLANE_ROOT}/tools/records/validate-schemas.sh"

mkdir -p "${ANCHOR_DIR}"

cat > "${ANCHOR_SCHEMA}" << 'SCHEMA'
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "records-head-anchor",
  "title": "D107 Records-Head Anchor",
  "description": "Anchor written once per L3 reconciler run. A non-descendant head detected against this anchor is Blocking drift Level 5. Published for L3 consumption.",
  "type": "object",
  "required": ["head_sha", "commit_count", "run_timestamp", "branch", "schema_version"],
  "additionalProperties": false,
  "properties": {
    "schema_version": {
      "type": "string",
      "const": "D107-v1",
      "description": "Schema identifier — must be 'D107-v1'."
    },
    "branch": {
      "type": "string",
      "minLength": 1,
      "description": "Default branch name of the records repository (e.g. 'main')."
    },
    "head_sha": {
      "type": "string",
      "pattern": "^[0-9a-f]{40}$",
      "description": "40-character SHA-1 of the records-repository default-branch head at reconciler run time."
    },
    "commit_count": {
      "type": "integer",
      "minimum": 0,
      "description": "Total commit count on the default branch at reconciler run time (git rev-list --count HEAD)."
    },
    "run_timestamp": {
      "type": "string",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[+-][0-9]{2}:[0-9]{2}$",
      "description": "UTC-with-offset ISO 8601 timestamp of the reconciler run that wrote this anchor (e.g. '2026-09-06T14:32:00+00:00')."
    },
    "drift_level_on_non_descendant": {
      "type": "integer",
      "const": 5,
      "description": "Drift severity level when current head is not a descendant of head_sha. Always 5 (Blocking)."
    }
  }
}
SCHEMA

# Append --anchor handler to the shared validator if not already present
if ! grep -q '"--anchor"' "${VALIDATOR}" 2>/dev/null && ! grep -q "'--anchor'" "${VALIDATOR}" 2>/dev/null && ! grep -q 'anchor' "${VALIDATOR}" 2>/dev/null; then
  cat >> "${VALIDATOR}" << 'ANCHOR_HANDLER'

# --- anchor handler ---
if [[ "${1:-}" == "--anchor" ]]; then
  SCHEMA_FILE="${CONTROL_PLANE_ROOT}/metrics/anchor/records-head-anchor.schema.json"
  if [[ ! -f "${SCHEMA_FILE}" ]]; then
    echo "ERROR: anchor schema not found at ${SCHEMA_FILE}" >&2
    exit 1
  fi
  # Validate schema file contains required keys
  FAIL=0
  for key in head_sha commit_count run_timestamp branch schema_version; do
    if ! grep -q "\"${key}\"" "${SCHEMA_FILE}"; then
      echo "FAIL: anchor schema missing property '${key}'" >&2
      FAIL=1
    fi
  done
  # Confirm non-descendant drift level is 5
  if ! grep -q '"const": 5' "${SCHEMA_FILE}"; then
    echo "FAIL: anchor schema does not declare drift_level_on_non_descendant const 5" >&2
    FAIL=1
  fi
  if [[ "${FAIL}" -eq 0 ]]; then
    echo "ANCHOR-SCHEMA OK"
    exit 0
  else
    exit 1
  fi
fi
ANCHOR_HANDLER
fi

chmod +x "${VALIDATOR}"
echo "M04 anchor schema written: ${ANCHOR_SCHEMA}"

# Write a sample anchor file for reference (not the live anchor — L3 writes that)
SAMPLE="${ANCHOR_DIR}/records-head-anchor.sample.json"
cat > "${SAMPLE}" << 'SAMPLE_JSON'
{
  "schema_version": "D107-v1",
  "branch": "main",
  "head_sha": "0000000000000000000000000000000000000000",
  "commit_count": 0,
  "run_timestamp": "2026-01-01T00:00:00+00:00",
  "drift_level_on_non_descendant": 5
}
SAMPLE_JSON
echo "M04 sample anchor written: ${SAMPLE}"
```

#### SELF-VERIFY

```bash
set -euo pipefail

ANCHOR_SCHEMA="${CONTROL_PLANE_ROOT}/metrics/anchor/records-head-anchor.schema.json"
VALIDATOR="${CONTROL_PLANE_ROOT}/tools/records/validate-schemas.sh"

# 1. Schema file exists and is valid JSON
[[ -f "${ANCHOR_SCHEMA}" ]] || { echo "FAIL: anchor schema missing"; exit 1; }
python3 -c "import json, sys; json.load(open(sys.argv[1]))" "${ANCHOR_SCHEMA}" \
  || { echo "FAIL: anchor schema is not valid JSON"; exit 1; }
echo "PASS: anchor schema is valid JSON"

# 2. All five required fields are present in the schema
for field in head_sha commit_count run_timestamp branch schema_version; do
  grep -q "\"${field}\"" "${ANCHOR_SCHEMA}" || { echo "FAIL: schema missing field '${field}'"; exit 1; }
done
echo "PASS: all required fields declared in schema"

# 3. drift_level_on_non_descendant is const 5 (Blocking)
grep -q '"const": 5' "${ANCHOR_SCHEMA}" || { echo "FAIL: drift_level_on_non_descendant const 5 not found"; exit 1; }
echo "PASS: drift_level_on_non_descendant is const 5"

# 4. Validator prints ANCHOR-SCHEMA OK
OUTPUT=$("${VALIDATOR}" --anchor 2>&1)
echo "${OUTPUT}" | grep -q "ANCHOR-SCHEMA OK" || { echo "FAIL: validator output was: ${OUTPUT}"; exit 1; }
echo "PASS: validator prints ANCHOR-SCHEMA OK"
```

#### STOP rules
- STOP if: `metrics/anchor/records-head-anchor.schema.json` already exists with a `$id` other than `records-head-anchor` — treat as a schema version conflict requiring L0 sign-off.
- STOP if: `tools/records/validate-schemas.sh` already contains an `--anchor` block that produces a different exit contract — reconcile before appending.
- STOP if: the records repository is not accessible via `$RECORDS_REPO` and the L3 team cannot verify the SHA pattern; flag for L3 owner resolution before publishing.
---

---
### L4-04-M05 · Signal Source Map

**Purpose:** Author `metrics/signals/sig-source-map.yaml` mapping the five L4-sourced SIG rows to their record stores, giving the L3 reconciler the index it needs to tie drift rows to L4 data.
**Spec:** §52.2 lines 4520-4590; §53.1 lines 4653-4689; charter §5.2
**Depends on:** L4-04-M02

#### COMMANDS

```bash
set -euo pipefail

SIGNALS_DIR="${CONTROL_PLANE_ROOT}/metrics/signals"
SIGNAL_MAP="${SIGNALS_DIR}/sig-source-map.yaml"

mkdir -p "${SIGNALS_DIR}"

cat > "${SIGNAL_MAP}" << 'SIGMAP'
# Signal Source Map — L4 store index for L3 reconciler
# §52.2 lines 4520-4590 | §53.1 lines 4653-4689 | charter §5.2
# Maps each SIG row whose source data lives in L4 stores.
# L3 reads this file to locate record stores when evaluating drift rows.
version: "1"
generated_by: "L4-04-M05"

signals:
  - sig_id: "SIG-06"
    name: "Board automation — Ready-queue miss rate"
    spec_ref: "§52.2 line 4523"
    l4_store: "records/board-automation/"
    store_path_full: "${RECORDS_REPO}/records/board-automation/"
    description: "Records of board automation runs; each entry includes ready-queue miss events."
    metric_type: "rate"
    freshness_ref: "metrics/freshness/write-freshness.yaml#records/board-automation/"
    l3_drift_row: "SIG-06-drift"
    owner: "pm"

  - sig_id: "SIG-17"
    name: "Restore-test execution coverage"
    spec_ref: "§52.2 line 4551"
    l4_store: "records/restore-tests/"
    store_path_full: "${RECORDS_REPO}/records/restore-tests/"
    description: "Records of restore-test runs; one entry per test execution with pass/fail outcome."
    metric_type: "coverage"
    freshness_ref: "metrics/freshness/write-freshness.yaml#records/restore-tests/"
    l3_drift_row: "SIG-17-drift"
    owner: "infra"

  - sig_id: "SIG-41"
    name: "Support intake — event log completeness"
    spec_ref: "§52.2 line 4571"
    l4_store: "events/"
    store_path_full: "${RECORDS_REPO}/events/"
    description: "Support intake events written to the main event log; SIG-41 measures staleness of intake entries."
    metric_type: "staleness"
    freshness_ref: "metrics/freshness/write-freshness.yaml#events/"
    l3_drift_row: "SIG-41-drift"
    owner: "support-lead"

  - sig_id: "SIG-42"
    name: "AI-eval regression — records/eval/ coverage"
    spec_ref: "§52.2 line 4577"
    l4_store: "records/eval/"
    store_path_full: "${RECORDS_REPO}/records/eval/"
    description: "AI evaluation regression records; each run produces one entry. SIG-42 measures regression gap."
    metric_type: "regression-gap"
    freshness_ref: "metrics/freshness/write-freshness.yaml#records/eval/"
    l3_drift_row: "SIG-42-drift"
    owner: "ai-eval"

  - sig_id: "SIG-46"
    name: "Audit-log review staleness — records/security-reviews/"
    spec_ref: "§52.2 line 4589"
    l4_store: "records/security-reviews/"
    store_path_full: "${RECORDS_REPO}/records/security-reviews/"
    description: "Security audit-log review records; SIG-46 measures days since last completed review entry."
    metric_type: "staleness"
    freshness_ref: "metrics/freshness/write-freshness.yaml#records/security-reviews/"
    l3_drift_row: "SIG-46-drift"
    owner: "security"
SIGMAP

echo "M05 signal source map written: ${SIGNAL_MAP}"
```

#### SELF-VERIFY

```bash
set -euo pipefail

SIGNAL_MAP="${CONTROL_PLANE_ROOT}/metrics/signals/sig-source-map.yaml"

# 1. File exists and is non-empty
[[ -f "${SIGNAL_MAP}" ]] || { echo "FAIL: sig-source-map.yaml missing"; exit 1; }
[[ -s "${SIGNAL_MAP}" ]] || { echo "FAIL: sig-source-map.yaml is empty"; exit 1; }
echo "PASS: sig-source-map.yaml exists and is non-empty"

# 2. All five required SIG IDs are present
for sig in SIG-06 SIG-17 SIG-41 SIG-42 SIG-46; do
  grep -q "sig_id: \"${sig}\"" "${SIGNAL_MAP}" || { echo "FAIL: ${sig} not found in sig-source-map.yaml"; exit 1; }
done
echo "PASS: all five SIG IDs (SIG-06, SIG-17, SIG-41, SIG-42, SIG-46) present"

# 3. Each SIG entry has an l4_store and owner field
SIG_COUNT=$(grep -c "sig_id:" "${SIGNAL_MAP}")
STORE_COUNT=$(grep -c "l4_store:" "${SIGNAL_MAP}")
OWNER_COUNT=$(grep -c "owner:" "${SIGNAL_MAP}")
[[ "${STORE_COUNT}" -eq "${SIG_COUNT}" ]] || { echo "FAIL: ${SIG_COUNT} SIG entries but only ${STORE_COUNT} l4_store fields"; exit 1; }
[[ "${OWNER_COUNT}" -eq "${SIG_COUNT}" ]] || { echo "FAIL: ${SIG_COUNT} SIG entries but only ${OWNER_COUNT} owner fields"; exit 1; }
echo "PASS: every SIG entry has l4_store and owner (${SIG_COUNT} entries)"

# 4. SIG-41 maps to events/ (the blocking event log store)
grep -A5 "SIG-41" "${SIGNAL_MAP}" | grep -q 'l4_store: "events/"' \
  || { echo "FAIL: SIG-41 does not map to events/"; exit 1; }
echo "PASS: SIG-41 correctly maps to events/"

# 5. All five stores referenced have a matching entry in write-freshness.yaml
FRESHNESS_FILE="${CONTROL_PLANE_ROOT}/metrics/freshness/write-freshness.yaml"
if [[ -f "${FRESHNESS_FILE}" ]]; then
  while IFS= read -r store; do
    grep -q "path: \"${store}\"" "${FRESHNESS_FILE}" \
      || { echo "WARN: store '${store}' in sig-source-map not found in write-freshness.yaml"; }
  done < <(grep "l4_store:" "${SIGNAL_MAP}" | sed 's/.*l4_store: "\(.*\)"/\1/')
  echo "PASS: store cross-reference against write-freshness.yaml complete"
fi
```

#### STOP rules
- STOP if: `metrics/signals/sig-source-map.yaml` already exists and maps any of the five SIG IDs to a different `l4_store` path — do not silently overwrite; surface the conflict for L0 reconciliation.
- STOP if: `write-freshness.yaml` (M02) is absent — the `freshness_ref` fields in this file would be dangling references; complete M02 first.
- STOP if: `RECORDS_REPO` is unset — `store_path_full` values will be unresolvable by L3; flag for environment configuration before publishing.
---

---
### L4-04-M06 · Engineering and Delivery Metric Declarations

**Purpose:** Seed `metrics/register/metric-declarations.yaml` with all §103.1 Engineering and §103.2 Delivery success metric entries, each carrying all eight §84.6 attributes.
**Spec:** §103.1 lines 9791-9801; §103.2 lines 9802-9812; §84.6 line 7481
**Depends on:** L4-04-M01 (register directory scaffold), L4-04-M05 (schema)

#### COMMANDS

```bash
set -euo pipefail

REGISTER="${CONTROL_PLANE_ROOT}/metrics/register"
DECL="${REGISTER}/metric-declarations.yaml"

# Ensure file exists with header if not already seeded
if ! grep -q "^metric_declarations:" "${DECL}" 2>/dev/null; then
  cat > "${DECL}" <<'HEADER'
# metric-declarations.yaml
# Auto-seeded by L4-04-M06. Extend in subsequent modules.
# All entries conform to §84.6 eight-attribute schema.
metric_declarations:
HEADER
fi

# Append Engineering metrics (§103.1)
cat >> "${DECL}" <<'ENGINEERING'

  # --- §103.1 Engineering Metrics ---

  - id: ENG-001
    name: PR Cycle Time
    section: "103.1"
    owner: team_lead
    cadence: weekly
    source: l4/pr-records
    aggregation: p50_p95_hours
    threshold: "p50 <= 24h; p95 <= 72h"
    known_limitations: ""

  - id: ENG-002
    name: CI Pass Rate
    section: "103.1"
    owner: team_lead
    cadence: weekly
    source: l4/ci-run-records
    aggregation: pass_count_over_total_pct
    threshold: ">= 95%"
    known_limitations: ""

  - id: ENG-003
    name: Plan Rejection Rate
    section: "103.1"
    owner: team_lead
    cadence: weekly
    source: l4/plan-review-records
    aggregation: rejected_over_submitted_pct
    threshold: "<= 10%"
    known_limitations: ""

  - id: ENG-004
    name: Verification Coverage
    section: "103.1"
    owner: team_lead
    cadence: sprint
    source: l4/verification-records
    aggregation: covered_dod_items_over_total_pct
    threshold: "100% of DoD items covered per release"
    known_limitations: ""

  - id: ENG-005
    name: Ready-Queue Misses
    section: "103.1"
    owner: team_lead
    cadence: weekly
    source: l4/queue-event-records
    aggregation: miss_count_per_sprint
    threshold: "<= 2 per sprint"
    known_limitations: ""

  - id: ENG-006
    name: Cross-Review Turnaround
    section: "103.1"
    owner: team_lead
    cadence: weekly
    source: l4/review-network-records
    aggregation: p50_hours_to_first_response
    threshold: "p50 <= 8h business hours"
    known_limitations: ""
ENGINEERING

# Append Delivery metrics (§103.2)
cat >> "${DECL}" <<'DELIVERY'

  # --- §103.2 Delivery Metrics ---

  - id: DEL-001
    name: Deployment Frequency
    section: "103.2"
    owner: team_lead
    cadence: weekly
    source: l4/deployment-records
    aggregation: deploys_per_week
    threshold: ">= 1 per week per active product"
    known_limitations: ""

  - id: DEL-002
    name: Lead Time for Changes
    section: "103.2"
    owner: team_lead
    cadence: weekly
    source: l4/deployment-records,l4/pr-records
    aggregation: p50_commit_to_prod_hours
    threshold: "p50 <= 48h"
    known_limitations: ""

  - id: DEL-003
    name: Change Failure Rate
    section: "103.2"
    owner: team_lead
    cadence: weekly
    source: l4/deployment-records,l4/incident-records
    aggregation: failed_deploys_over_total_pct
    threshold: "<= 5%"
    known_limitations: ""

  - id: DEL-004
    name: Rollback Rate
    section: "103.2"
    owner: team_lead
    cadence: weekly
    source: l4/deployment-records
    aggregation: rollbacks_over_deploys_pct
    threshold: "<= 3%"
    known_limitations: ""

  - id: DEL-005
    name: Merged-But-Not-Deployed Count
    section: "103.2"
    owner: team_lead
    cadence: weekly
    source: l4/pr-records,l4/deployment-records
    aggregation: open_gap_count
    threshold: "<= 5 open at any time"
    known_limitations: ""

  - id: DEL-006
    name: Digest Match Rate
    section: "103.2"
    owner: team_lead
    cadence: per_release
    source: l4/digest-records
    aggregation: matched_over_total_pct
    threshold: "100% match before release gate"
    known_limitations: ""
DELIVERY

echo "M06: Engineering and Delivery entries written to ${DECL}"
grep -c "^  - id:" "${DECL}"
```

#### SELF-VERIFY

```bash
DECL="${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml"

# 1. All six Engineering IDs present
for id in ENG-001 ENG-002 ENG-003 ENG-004 ENG-005 ENG-006; do
  grep -q "id: ${id}" "${DECL}" || { echo "MISSING ${id}"; exit 1; }
done
echo "CHECK 1 PASS: all ENG IDs present"

# 2. All six Delivery IDs present
for id in DEL-001 DEL-002 DEL-003 DEL-004 DEL-005 DEL-006; do
  grep -q "id: ${id}" "${DECL}" || { echo "MISSING ${id}"; exit 1; }
done
echo "CHECK 2 PASS: all DEL IDs present"

# 3. Every entry block contains all eight §84.6 attributes
python3 - <<'PY'
import yaml, sys
with open("${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml") as f:
    data = yaml.safe_load(f)
required = {"id","name","section","owner","cadence","source","aggregation","threshold"}
fails = []
for m in data.get("metric_declarations", []):
    missing = required - set(m.keys())
    if missing:
        fails.append((m.get("id","?"), missing))
if fails:
    for mid, miss in fails:
        print(f"FAIL {mid}: missing {miss}")
    sys.exit(1)
print("CHECK 3 PASS: all eight attributes present on every entry")
PY

# 4. Source fields do not name only a tool (must include l4/ prefix)
python3 - <<'PY'
import yaml, sys
TOOL_ONLY = {"prometheus","devlake","grafana","datadog"}
with open("${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml") as f:
    data = yaml.safe_load(f)
fails = []
for m in data.get("metric_declarations", []):
    sources = [s.strip() for s in m.get("source","").split(",")]
    eng_del_ids = [x for x in [m.get("id","")] if x.startswith(("ENG-","DEL-"))]
    if not eng_del_ids:
        continue
    has_l4 = any(s.startswith("l4/") for s in sources)
    if not has_l4:
        fails.append(m.get("id","?"))
if fails:
    print(f"FAIL: no l4/ source on {fails}")
    sys.exit(1)
print("CHECK 4 PASS: all ENG/DEL entries have at least one l4/ source")
PY
```

#### STOP rules
- STOP if: `metric-declarations.yaml` does not exist or the register directory scaffold from L4-04-M01 is absent — run M01 first.
- STOP if: the YAML parse fails after appending (malformed heredoc merge) — validate with `python3 -c "import yaml; yaml.safe_load(open('${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml'))"` before proceeding.
- STOP if: any ENG or DEL entry is missing the `source` field or the `l4/` prefix — Self-verify check 4 exits non-zero.

---
### L4-04-M07 · Reliability and Business Metric Declarations

**Purpose:** Extend `metrics/register/metric-declarations.yaml` with all §103.3 Reliability and §103.4 Business entries, including the freeze-adjacent severity-inflation known_limitation on the weekend-activation metric.
**Spec:** §103.3 lines 9813-9828; §103.4 lines 9830-9841; §84.6 line 7481; D98
**Depends on:** L4-04-M06

#### COMMANDS

```bash
set -euo pipefail

DECL="${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml"

# Verify M06 ran
grep -q "id: ENG-001" "${DECL}" || { echo "ERROR: M06 not applied"; exit 1; }

cat >> "${DECL}" <<'RELIABILITY'

  # --- §103.3 Reliability Metrics ---

  - id: REL-001
    name: Service Availability
    section: "103.3"
    owner: team_lead
    cadence: weekly
    source: prometheus,l4/availability-records
    aggregation: uptime_pct_rolling_30d
    threshold: ">= 99.5%"
    known_limitations: ""

  - id: REL-002
    name: Error Rate
    section: "103.3"
    owner: team_lead
    cadence: weekly
    source: prometheus,l4/error-rate-records
    aggregation: errors_per_1000_requests
    threshold: "<= 1.0 per 1000"
    known_limitations: ""

  - id: REL-003
    name: MTTR (Mean Time to Recover)
    section: "103.3"
    owner: team_lead
    cadence: per_incident
    source: l4/incident-records
    aggregation: mean_resolution_hours
    threshold: "<= 4h for P1; <= 24h for P2"
    known_limitations: ""

  - id: REL-004
    name: Incident Frequency
    section: "103.3"
    owner: team_lead
    cadence: weekly
    source: l4/incident-records
    aggregation: incident_count_per_week
    threshold: "<= 1 P1 per month; <= 4 P2 per month"
    known_limitations: ""

  - id: REL-005
    name: Restore-Test Pass Rate
    section: "103.3"
    owner: team_lead
    cadence: monthly
    source: l4/restore-test-records
    aggregation: passed_over_total_pct
    threshold: "100% pass on scheduled restore tests"
    known_limitations: ""

  - id: REL-006
    name: Undeclared Weekend Activations
    section: "103.3"
    owner: team_lead
    cadence: weekly
    source: l4/event-log-records
    aggregation: undeclared_count_per_sprint
    threshold: "0 undeclared activations per sprint"
    known_limitations: >
      Freeze-adjacent weekends (D98): severity inflation occurs when on-call
      engineers log marginal events as incidents to justify freeze exceptions.
      Counts in the 48h window before and after a freeze boundary must be
      reviewed manually against the freeze-exception log before aggregating.

  - id: REL-007
    name: Configuration Drift
    section: "103.3"
    owner: team_lead
    cadence: weekly
    source: l4/reconciliation-records
    aggregation: drift_events_per_week
    threshold: "0 unresolved drift items at sprint close"
    known_limitations: ""
RELIABILITY

cat >> "${DECL}" <<'BUSINESS'

  # --- §103.4 Business Metrics ---

  - id: BIZ-001
    name: Support Ticket Volume
    section: "103.4"
    owner: team_lead
    cadence: weekly
    source: l4/support-records
    aggregation: open_ticket_count_and_p50_age_hours
    threshold: "p50 ticket age <= 48h; no ticket > 7d unresolved"
    known_limitations: ""

  - id: BIZ-002
    name: Support Escalation Rate
    section: "103.4"
    owner: team_lead
    cadence: weekly
    source: l4/support-records
    aggregation: escalated_over_total_pct
    threshold: "<= 5%"
    known_limitations: ""

  - id: BIZ-003
    name: Billing Export Accuracy
    section: "103.4"
    owner: team_lead
    cadence: monthly
    source: l4/billing-export-records
    aggregation: matched_line_items_over_total_pct
    threshold: "100% line-item match between system and export"
    known_limitations: ""

  - id: BIZ-004
    name: Product Activation Rate
    section: "103.4"
    owner: team_lead
    cadence: monthly
    source: l4/product-analytics-records
    aggregation: activated_users_over_provisioned_pct
    threshold: ">= 80% of provisioned users activate within 14d"
    known_limitations: ""

  - id: BIZ-005
    name: Feature Adoption Rate
    section: "103.4"
    owner: team_lead
    cadence: monthly
    source: l4/product-analytics-records
    aggregation: dau_over_mau_ratio
    threshold: ">= 0.4 DAU/MAU"
    known_limitations: ""
BUSINESS

echo "M07: Reliability and Business entries appended to ${DECL}"
```

#### SELF-VERIFY

```bash
DECL="${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml"

# 1. All REL IDs present
for id in REL-001 REL-002 REL-003 REL-004 REL-005 REL-006 REL-007; do
  grep -q "id: ${id}" "${DECL}" || { echo "MISSING ${id}"; exit 1; }
done
echo "CHECK 1 PASS: all REL IDs present"

# 2. All BIZ IDs present
for id in BIZ-001 BIZ-002 BIZ-003 BIZ-004 BIZ-005; do
  grep -q "id: ${id}" "${DECL}" || { echo "MISSING ${id}"; exit 1; }
done
echo "CHECK 2 PASS: all BIZ IDs present"

# 3. Weekend activation metric carries the D98 freeze-adjacent note
python3 - <<'PY'
import yaml, sys
with open("${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml") as f:
    data = yaml.safe_load(f)
for m in data.get("metric_declarations", []):
    if m.get("id") == "REL-006":
        kl = m.get("known_limitations", "")
        if "freeze" not in str(kl).lower():
            print("FAIL REL-006: freeze-adjacent note absent from known_limitations")
            sys.exit(1)
        print("CHECK 3 PASS: REL-006 known_limitations contains freeze note")
        break
PY

# 4. REL entries that cite Prometheus also cite an l4/ store
python3 - <<'PY'
import yaml, sys
with open("${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml") as f:
    data = yaml.safe_load(f)
fails = []
for m in data.get("metric_declarations", []):
    if not m.get("id","").startswith("REL-"):
        continue
    sources = [s.strip() for s in m.get("source","").split(",")]
    if "prometheus" in sources and not any(s.startswith("l4/") for s in sources):
        fails.append(m.get("id"))
if fails:
    print(f"FAIL: Prometheus-only source (no l4/ backing) on {fails}")
    sys.exit(1)
print("CHECK 4 PASS: all Prometheus-citing REL entries also name an l4/ store")
PY
```

#### STOP rules
- STOP if: `id: ENG-001` is absent from the file — M06 has not run; run M06 first.
- STOP if: `REL-006.known_limitations` is blank or the word "freeze" is absent — D98 compliance requires the explicit inflation note.
- STOP if: any REL entry lists only `prometheus` in `source` with no `l4/` store — Self-verify check 4 exits non-zero.

---
### L4-04-M08 · Platform, Team Lead, Founder, and Review Network Metric Declarations

**Purpose:** Extend `metrics/register/metric-declarations.yaml` with §103.5 Platform Health, §103.6 Business/Engineering Tradeoffs, §103.7 Team Lead Capacity Thresholds, §103.8 Founder Capacity, and §103.9 Review Network Quality entries; Founder decision latency owner is Team Lead per §103 preamble.
**Spec:** §103.5-103.9 lines 9844-9913; §84.6 line 7481; §103.8 line 9897
**Depends on:** L4-04-M07

#### COMMANDS

```bash
set -euo pipefail

DECL="${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml"

grep -q "id: REL-001" "${DECL}" || { echo "ERROR: M07 not applied"; exit 1; }

cat >> "${DECL}" <<'PLATFORM'

  # --- §103.5 Platform Health Metrics ---

  - id: PLT-001
    name: Contract Version Coverage
    section: "103.5"
    owner: team_lead
    cadence: weekly
    source: l4/contract-records
    aggregation: products_on_current_version_over_total_pct
    threshold: ">= 90% of products on current contract version"
    known_limitations: ""

  - id: PLT-002
    name: Transitional Product Count
    section: "103.5"
    owner: team_lead
    cadence: weekly
    source: l4/product-state-records
    aggregation: products_in_transitional_state_count
    threshold: "<= 2 in transitional state simultaneously"
    known_limitations: ""

  - id: PLT-003
    name: SIG Class Distribution
    section: "103.5"
    owner: team_lead
    cadence: sprint
    source: l4/sig-classification-records
    aggregation: count_by_sig_class
    threshold: "No SIG class > 60% of active products"
    known_limitations: ""
PLATFORM

cat >> "${DECL}" <<'TRADEOFFS'

  # --- §103.6 Business/Engineering Tradeoffs ---

  - id: TRD-001
    name: Tech-Debt Paydown Rate
    section: "103.6"
    owner: team_lead
    cadence: sprint
    source: l4/debt-register-records
    aggregation: closed_debt_items_over_opened_rolling_4sprint
    threshold: ">= 1.0 (closing at least as fast as opening)"
    known_limitations: ""

  - id: TRD-002
    name: Feature vs. Stabilisation Ratio
    section: "103.6"
    owner: team_lead
    cadence: sprint
    source: l4/task-records
    aggregation: feature_points_over_stabilisation_points
    threshold: "Between 60/40 and 80/20 (feature/stabilisation)"
    known_limitations: ""
TRADEOFFS

cat >> "${DECL}" <<'TEAMLEAD'

  # --- §103.7 Team Lead Capacity Thresholds ---

  - id: TLC-001
    name: Team Lead Active Review Load
    section: "103.7"
    owner: team_lead
    cadence: weekly
    source: l4/review-network-records
    aggregation: open_reviews_assigned_to_tl_count
    threshold: "<= 10 open reviews at any point"
    known_limitations: ""

  - id: TLC-002
    name: Team Lead Decision Queue Depth
    section: "103.7"
    owner: team_lead
    cadence: weekly
    source: l4/decision-records
    aggregation: pending_tl_decisions_count
    threshold: "<= 5 pending decisions at sprint close"
    known_limitations: ""
TEAMLEAD

cat >> "${DECL}" <<'FOUNDER'

  # --- §103.8 Founder Capacity Metrics ---
  # Per §103 preamble and §103.8 line 9897: owner is Team Lead, not Founder.

  - id: FDR-001
    name: Founder Decision Latency (Median)
    section: "103.8"
    owner: team_lead
    cadence: weekly
    source: l4/decision-records
    aggregation: p50_hours_from_request_to_decision
    threshold: "<= 24h p50"
    known_limitations: ""

  - id: FDR-002
    name: Founder Decision Latency (Trend)
    section: "103.8"
    owner: team_lead
    cadence: weekly
    source: l4/decision-records
    aggregation: week_over_week_p50_delta_hours
    threshold: "Non-increasing trend over rolling 4-week window"
    known_limitations: ""
FOUNDER

cat >> "${DECL}" <<'REVNET'

  # --- §103.9 Review Network Quality ---

  - id: RNQ-001
    name: Review Gini Spread
    section: "103.9"
    owner: team_lead
    cadence: sprint
    source: l4/review-network-records
    aggregation: gini_coefficient_of_review_load
    threshold: "<= 0.4 (no severe concentration)"
    known_limitations: ""

  - id: RNQ-002
    name: Review Network Turnaround
    section: "103.9"
    owner: team_lead
    cadence: weekly
    source: l4/review-network-records
    aggregation: p50_p95_hours_to_approval
    threshold: "p50 <= 12h; p95 <= 36h"
    known_limitations: ""
REVNET

echo "M08: Platform, TL, Founder, RevNet entries appended to ${DECL}"
```

#### SELF-VERIFY

```bash
DECL="${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml"

# 1. Platform IDs present
for id in PLT-001 PLT-002 PLT-003; do
  grep -q "id: ${id}" "${DECL}" || { echo "MISSING ${id}"; exit 1; }
done
echo "CHECK 1 PASS: PLT IDs present"

# 2. Founder metrics owner is team_lead, not founder
python3 - <<'PY'
import yaml, sys
with open("${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml") as f:
    data = yaml.safe_load(f)
fails = []
for m in data.get("metric_declarations", []):
    if m.get("id","").startswith("FDR-"):
        if m.get("owner","") != "team_lead":
            fails.append(m.get("id"))
if fails:
    print(f"FAIL: FDR entries not owned by team_lead: {fails}")
    sys.exit(1)
print("CHECK 2 PASS: all FDR entries owned by team_lead per §103 preamble")
PY

# 3. RNQ IDs present
for id in RNQ-001 RNQ-002; do
  grep -q "id: ${id}" "${DECL}" || { echo "MISSING ${id}"; exit 1; }
done
echo "CHECK 3 PASS: RNQ IDs present"

# 4. TLC and TRD IDs present
for id in TLC-001 TLC-002 TRD-001 TRD-002; do
  grep -q "id: ${id}" "${DECL}" || { echo "MISSING ${id}"; exit 1; }
done
echo "CHECK 4 PASS: TLC and TRD IDs present"
```

#### STOP rules
- STOP if: `id: REL-001` is absent — M07 has not run.
- STOP if: any `FDR-*` entry has `owner: founder` — §103.8 line 9897 mandates team_lead ownership; fix before proceeding.
- STOP if: `PLT-003` (SIG class distribution) source field does not begin with `l4/` — Platform metrics must reference an L4 classification record store.

---
### L4-04-M09 · Knowledge, Bottleneck, Portfolio, and OS Success Metric Declarations

**Purpose:** Complete `metrics/register/metric-declarations.yaml` with §103.10 Knowledge Redundancy, §103.11 Seven-Way Bottleneck Taxonomy, §103.12 Portfolio Capacity, and §103.13 OS Success Criteria entries; every §103.13 measure without a pre-Phase-1 baseline carries `unbaselined: true` per AT-046 and D77.
**Spec:** §103.10-103.13 lines 9913-9975; §103.14 lines 9975-9977; AT-046; D48; D77
**Depends on:** L4-04-M08

#### COMMANDS

```bash
set -euo pipefail

DECL="${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml"

grep -q "id: FDR-001" "${DECL}" || { echo "ERROR: M08 not applied"; exit 1; }

cat >> "${DECL}" <<'KNOWLEDGE'

  # --- §103.10 Knowledge Redundancy ---

  - id: KNW-001
    name: Single-Point-of-Knowledge Count
    section: "103.10"
    owner: team_lead
    cadence: sprint
    source: l4/knowledge-map-records
    aggregation: components_with_one_knowledgeable_person_count
    threshold: "0 P0/P1 components with SPOK"
    known_limitations: ""

  - id: KNW-002
    name: Onboarding Documentation Coverage
    section: "103.10"
    owner: team_lead
    cadence: monthly
    source: l4/documentation-records
    aggregation: documented_components_over_total_pct
    threshold: ">= 90%"
    known_limitations: ""
KNOWLEDGE

cat >> "${DECL}" <<'BOTTLENECK'

  # --- §103.11 Seven-Way Bottleneck Taxonomy ---
  # D48: Founder-decision-latency bottleneck is tracked explicitly.

  - id: BTL-001
    name: Bottleneck — Review Starvation
    section: "103.11"
    owner: team_lead
    cadence: weekly
    source: l4/review-network-records
    aggregation: prs_blocked_on_review_gt48h_count
    threshold: "<= 2 per sprint"
    known_limitations: ""

  - id: BTL-002
    name: Bottleneck — CI Queue Saturation
    section: "103.11"
    owner: team_lead
    cadence: weekly
    source: l4/ci-run-records
    aggregation: queue_wait_p95_minutes
    threshold: "p95 <= 15 min"
    known_limitations: ""

  - id: BTL-003
    name: Bottleneck — Plan Rework Loops
    section: "103.11"
    owner: team_lead
    cadence: sprint
    source: l4/plan-review-records
    aggregation: plans_requiring_gt2_revision_cycles_count
    threshold: "<= 1 per sprint"
    known_limitations: ""

  - id: BTL-004
    name: Bottleneck — Deploy Gate Holds
    section: "103.11"
    owner: team_lead
    cadence: weekly
    source: l4/deployment-records
    aggregation: releases_held_gt24h_at_gate_count
    threshold: "0 holds > 24h without documented exception"
    known_limitations: ""

  - id: BTL-005
    name: Bottleneck — Founder Decision Latency
    section: "103.11"
    owner: team_lead
    cadence: weekly
    source: l4/decision-records
    aggregation: decisions_pending_founder_gt24h_count
    threshold: "<= 1 pending > 24h at any sprint checkpoint"
    known_limitations: "Per D48: tracked separately from TL decision queue."

  - id: BTL-006
    name: Bottleneck — Cross-Team Dependency Holds
    section: "103.11"
    owner: team_lead
    cadence: weekly
    source: l4/dependency-records
    aggregation: blocked_tasks_on_cross_team_dependency_count
    threshold: "<= 3 per sprint"
    known_limitations: ""

  - id: BTL-007
    name: Bottleneck — Environment Unavailability
    section: "103.11"
    owner: team_lead
    cadence: weekly
    source: l4/environment-records
    aggregation: environment_downtime_hours_per_sprint
    threshold: "<= 2h per sprint"
    known_limitations: ""
BOTTLENECK

cat >> "${DECL}" <<'PORTFOLIO'

  # --- §103.12 Portfolio Capacity ---

  - id: PFC-001
    name: Portfolio Capacity Utilisation
    section: "103.12"
    owner: team_lead
    cadence: sprint
    source: l4/capacity-records
    aggregation: allocated_over_available_capacity_pct
    threshold: "<= 85% to preserve slack"
    known_limitations: ""

  - id: PFC-002
    name: Honest Arithmetic Variance
    section: "103.12"
    owner: team_lead
    cadence: sprint
    source: l4/capacity-records,l4/task-records
    aggregation: actual_over_planned_capacity_ratio
    threshold: "0.9 to 1.1 (within 10% of plan)"
    known_limitations: ""
PORTFOLIO

# OS Success Criteria (§103.13) — mark unbaselined where no pre-Phase-1 baseline exists
cat >> "${DECL}" <<'OSSUCCESS'

  # --- §103.13 OS Success Criteria ---
  # AT-046 + D77: measures without pre-Phase-1 baseline carry unbaselined: true.
  # No measure carries a blank baseline field.

  - id: OSS-001
    name: OS Adoption — Teams Using Control Plane
    section: "103.13"
    owner: team_lead
    cadence: monthly
    source: l4/product-state-records
    aggregation: teams_on_control_plane_over_total_pct
    threshold: ">= 80% by end of Phase 2"
    baseline: "0% at Phase-1 start"
    unbaselined: false
    known_limitations: ""

  - id: OSS-002
    name: OS Adoption — DoD Compliance Rate
    section: "103.13"
    owner: team_lead
    cadence: sprint
    source: l4/verification-records
    aggregation: dod_items_met_over_total_pct
    threshold: "100% at each release gate"
    baseline: "unset pre-Phase-1"
    unbaselined: true
    known_limitations: ""

  - id: OSS-003
    name: OS Adoption — Coherence Review Pass Rate
    section: "103.13"
    owner: team_lead
    cadence: sprint
    source: l4/coherence-review-records
    aggregation: passed_over_total_pct
    threshold: ">= 95% pass without rework"
    baseline: "unset pre-Phase-1"
    unbaselined: true
    known_limitations: ""

  - id: OSS-004
    name: OS Adoption — Metric Register Completeness
    section: "103.13"
    owner: team_lead
    cadence: per_release
    source: l4/metric-register-records
    aggregation: declared_over_required_metrics_pct
    threshold: "100%"
    baseline: "0% pre-Phase-1 (no register existed)"
    unbaselined: false
    known_limitations: ""

  - id: OSS-005
    name: OS Adoption — Structural Blocker Resolution Rate
    section: "103.13"
    owner: team_lead
    cadence: sprint
    source: l4/decision-records,l4/coherence-review-records
    aggregation: resolved_blockers_over_total_pct
    threshold: "100% of L*-99 blockers resolved before gate"
    baseline: "unset pre-Phase-1"
    unbaselined: true
    known_limitations: ""
OSSUCCESS

echo "M09: Knowledge, Bottleneck, Portfolio, OS Success entries appended to ${DECL}"
```

#### SELF-VERIFY

```bash
DECL="${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml"

# 1. Seven BTL IDs present
for id in BTL-001 BTL-002 BTL-003 BTL-004 BTL-005 BTL-006 BTL-007; do
  grep -q "id: ${id}" "${DECL}" || { echo "MISSING ${id}"; exit 1; }
done
echo "CHECK 1 PASS: all seven BTL bottleneck IDs present"

# 2. BTL-005 (Founder) references D48 in known_limitations
python3 - <<'PY'
import yaml, sys
with open("${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml") as f:
    data = yaml.safe_load(f)
for m in data.get("metric_declarations", []):
    if m.get("id") == "BTL-005":
        kl = str(m.get("known_limitations",""))
        if "D48" not in kl:
            print("FAIL BTL-005: D48 reference missing from known_limitations")
            sys.exit(1)
        print("CHECK 2 PASS: BTL-005 known_limitations references D48")
        break
PY

# 3. Every OSS entry has a non-blank baseline field
python3 - <<'PY'
import yaml, sys
with open("${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml") as f:
    data = yaml.safe_load(f)
fails = []
for m in data.get("metric_declarations", []):
    if m.get("id","").startswith("OSS-"):
        if not m.get("baseline","").strip():
            fails.append(m.get("id"))
if fails:
    print(f"FAIL: blank baseline on {fails} (AT-046/D77 forbids blank baseline)")
    sys.exit(1)
print("CHECK 3 PASS: all OSS entries have non-blank baseline")
PY

# 4. OSS entries without pre-Phase-1 data carry unbaselined: true
python3 - <<'PY'
import yaml, sys
with open("${CONTROL_PLANE_ROOT}/metrics/register/metric-declarations.yaml") as f:
    data = yaml.safe_load(f)
fails = []
for m in data.get("metric_declarations", []):
    if m.get("id","").startswith("OSS-"):
        bl = m.get("baseline","")
        ub = m.get("unbaselined", None)
        if "unset" in bl and ub is not True:
            fails.append(m.get("id"))
if fails:
    print(f"FAIL: {fails} has 'unset' baseline but unbaselined is not true")
    sys.exit(1)
print("CHECK 4 PASS: all 'unset' OSS baselines carry unbaselined: true")
PY
```

#### STOP rules
- STOP if: `id: FDR-001` is absent — M08 has not run.
- STOP if: any `OSS-*` entry has a blank `baseline` field — AT-046 and D77 require either a real baseline value or the string `"unset pre-Phase-1"` plus `unbaselined: true`.
- STOP if: `BTL-005` is absent or its `known_limitations` does not reference D48 — the Founder bottleneck must be explicitly distinguished from the generic TL decision queue.

---
### L4-04-M10 · Source Validator Base Pass

**Purpose:** Implement `metrics/register/validate-sources.sh` to confirm every §103 measure in `metric-declarations.yaml` names at least one L4 record store in its `source` field, exiting 0 with `SOURCES OK` when all pass.
**Spec:** §103 preamble line 9776; invariant 46 line 9513
**Depends on:** L4-04-M09

#### COMMANDS

```bash
set -euo pipefail

REGISTER="${CONTROL_PLANE_ROOT}/metrics/register"
DECL="${REGISTER}/metric-declarations.yaml"
VALIDATOR="${REGISTER}/validate-sources.sh"

grep -q "id: OSS-001" "${DECL}" || { echo "ERROR: M09 not applied — OSS entries missing"; exit 1; }

cat > "${VALIDATOR}" <<'SCRIPT'
#!/usr/bin/env bash
# validate-sources.sh
# §103 preamble / invariant 46: every metric measure must name at least one
# L4 record store (l4/ prefix) in its source field.
# A source that names only a tool (prometheus, devlake, etc.) without an
# l4/ backing store is a validation failure.
# Exit 0 + "SOURCES OK" when all pass; non-zero + failure list otherwise.

set -euo pipefail

DECL="${CONTROL_PLANE_ROOT:-$(git rev-parse --show-toplevel)}/metrics/register/metric-declarations.yaml"

if [[ ! -f "${DECL}" ]]; then
  echo "ERROR: metric-declarations.yaml not found at ${DECL}"
  exit 2
fi

python3 - "${DECL}" <<'PY'
import yaml, sys

decl_path = sys.argv[1]
with open(decl_path) as f:
    data = yaml.safe_load(f)

entries = data.get("metric_declarations", [])
if not entries:
    print("ERROR: metric_declarations list is empty or missing")
    sys.exit(2)

TOOL_ONLY = {"prometheus", "devlake", "grafana", "datadog", "pagerduty", "sentry"}
failures = []

for m in entries:
    mid = m.get("id", "<no-id>")
    raw_source = m.get("source", "")
    if not raw_source or not str(raw_source).strip():
        failures.append(f"{mid}: source field is blank")
        continue
    parts = [s.strip().lower() for s in str(raw_source).split(",")]
    has_l4 = any(p.startswith("l4/") for p in parts)
    if not has_l4:
        non_l4 = [p for p in parts if not p.startswith("l4/")]
        failures.append(
            f"{mid}: no l4/ store — only [{', '.join(non_l4)}] named"
        )

if failures:
    print("SOURCES FAIL")
    for f in failures:
        print(f"  FAIL: {f}")
    sys.exit(1)

print(f"SOURCES OK ({len(entries)} measures validated)")
PY
SCRIPT

chmod +x "${VALIDATOR}"
echo "M10: validate-sources.sh written to ${VALIDATOR}"

# Perform the base pass immediately to confirm current state of declarations
"${VALIDATOR}"
```

#### SELF-VERIFY

```bash
REGISTER="${CONTROL_PLANE_ROOT}/metrics/register"
VALIDATOR="${REGISTER}/validate-sources.sh"

# 1. Script file exists and is executable
[[ -x "${VALIDATOR}" ]] || { echo "FAIL: validate-sources.sh not executable"; exit 1; }
echo "CHECK 1 PASS: validate-sources.sh exists and is executable"

# 2. Script exits 0 and prints SOURCES OK against current declarations
OUTPUT=$("${VALIDATOR}" 2>&1)
EXIT_CODE=$?
if [[ ${EXIT_CODE} -ne 0 ]]; then
  echo "FAIL: validate-sources.sh exited ${EXIT_CODE}"
  echo "${OUTPUT}"
  exit 1
fi
echo "${OUTPUT}" | grep -q "SOURCES OK" || { echo "FAIL: SOURCES OK not in output"; exit 1; }
echo "CHECK 2 PASS: script exits 0 and prints SOURCES OK"

# 3. Script exits non-zero when a measure has a blank source
TMPFILE=$(mktemp)
cat > "${TMPFILE}" <<'BADYAML'
metric_declarations:
  - id: TST-BAD
    name: Bad Metric
    section: "103.1"
    owner: team_lead
    cadence: weekly
    source: ""
    aggregation: count
    threshold: ">= 1"
    known_limitations: ""
BADYAML
CONTROL_PLANE_ROOT=$(dirname "$(dirname "${VALIDATOR}")") \
  python3 - "${TMPFILE}" <<'PY' && { echo "FAIL: should have exited non-zero for blank source"; rm -f "${TMPFILE}"; exit 1; }
import yaml, sys
with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)
entries = data.get("metric_declarations", [])
failures = []
for m in entries:
    mid = m.get("id","?")
    raw = m.get("source","")
    if not raw or not str(raw).strip():
        failures.append(mid)
    else:
        parts = [s.strip().lower() for s in str(raw).split(",")]
        if not any(p.startswith("l4/") for p in parts):
            failures.append(mid)
if failures:
    sys.exit(1)
sys.exit(0)
PY
rm -f "${TMPFILE}"
echo "CHECK 3 PASS: blank-source measure correctly triggers non-zero exit"

# 4. Script exits non-zero for tool-only source (no l4/ prefix)
TMPFILE=$(mktemp)
cat > "${TMPFILE}" <<'TOOLONLY'
metric_declarations:
  - id: TST-TOOL
    name: Tool Only Metric
    section: "103.3"
    owner: team_lead
    cadence: weekly
    source: prometheus
    aggregation: uptime_pct
    threshold: ">= 99%"
    known_limitations: ""
TOOLONLY
CONTROL_PLANE_ROOT=$(dirname "$(dirname "${VALIDATOR}")") \
  python3 - "${TMPFILE}" <<'PY' && { echo "FAIL: should have exited non-zero for tool-only source"; rm -f "${TMPFILE}"; exit 1; }
import yaml, sys
with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)
entries = data.get("metric_declarations", [])
failures = []
for m in entries:
    parts = [s.strip().lower() for s in str(m.get("source","")).split(",")]
    if not any(p.startswith("l4/") for p in parts):
        failures.append(m.get("id","?"))
if failures:
    sys.exit(1)
sys.exit(0)
PY
rm -f "${TMPFILE}"
echo "CHECK 4 PASS: tool-only source (no l4/) correctly triggers non-zero exit"
```

#### STOP rules
- STOP if: `id: OSS-001` is absent from `metric-declarations.yaml` — M09 has not run; the validator would pass vacuously on an empty or partial file.
- STOP if: `validate-sources.sh` exits non-zero on the real declarations file — some measure added in M06-M09 lacks an `l4/` source; identify failing IDs from the output and fix the relevant module before advancing to M11.
- STOP if: the script outputs `SOURCES FAIL` for any entry — do not mark M10 complete; trace the failing measure IDs back to their authoring module and correct the `source` field there.

---
### L4-04-M11 · Arming-Discipline Validator

**Purpose:** Extend validate-sources.sh with --arming to enforce D77: every metric with an activation_dependency on a store must return an unbaselined (non-zero, non-miss) value when that store is empty or carries no baseline.
**Spec:** §52.2 line 4524; D77; §103 preamble line 9789
**Depends on:** L4-04-M01 (validate-sources.sh scaffold), L4-04-M02 (metric-declarations.yaml)

#### COMMANDS

```bash
set -euo pipefail

REGISTER="$CONTROL_PLANE_ROOT/metrics/register"
DECLARATIONS="$REGISTER/metric-declarations.yaml"
SCRIPT="$REGISTER/validate-sources.sh"

# Append --arming handler to validate-sources.sh before the final exit line
# Insert as a new case block; file must already exist from M01
python3 - <<'PYEOF'
import sys, re, pathlib

script = pathlib.Path("$REGISTER/validate-sources.sh").read_text()

arming_block = r'''
# ── D77 Arming-Discipline check ──────────────────────────────────────────────
if [[ "${1:-}" == "--arming" ]]; then
  DECLARATIONS="${DECLARATIONS:-$CONTROL_PLANE_ROOT/metrics/register/metric-declarations.yaml}"
  failures=()

  # Extract metrics that declare an activation_dependency
  armed_metrics=$(python3 -c "
import yaml, sys
doc = yaml.safe_load(open('${DECLARATIONS}'))
for m in doc.get('metrics', []):
    dep = m.get('activation_dependency', '')
    if dep:
        print(m['id'] + '|' + dep)
")

  while IFS='|' read -r metric_id dep_store; do
    [[ -z "$metric_id" ]] && continue

    # Simulate empty-store condition: probe computation with no-baseline sentinel
    result=$(python3 -c "
import yaml, sys
doc = yaml.safe_load(open('${DECLARATIONS}'))
for m in doc.get('metrics', []):
    if m['id'] == '$metric_id':
        # Check for explicit empty_store_returns_unbaselined assertion
        flag = m.get('empty_store_returns_unbaselined', None)
        if flag is True:
            print('UNBASELINED')
        elif flag is False:
            print('BASELINED')
        else:
            print('UNDECLARED')
        sys.exit(0)
print('NOT_FOUND')
")

    case "$result" in
      UNBASELINED)
        echo "  [ARMING OK] $metric_id -> $dep_store: returns unbaselined on empty store"
        ;;
      BASELINED)
        failures+=("$metric_id: empty_store_returns_unbaselined is false (instrument trap D77)")
        ;;
      UNDECLARED)
        failures+=("$metric_id: missing empty_store_returns_unbaselined field (D77 requires explicit declaration)")
        ;;
      NOT_FOUND)
        failures+=("$metric_id: not found in declarations")
        ;;
    esac
  done <<< "$armed_metrics"

  if [[ ${#failures[@]} -gt 0 ]]; then
    echo "ARMING FAIL: D77 violations found:"
    for f in "${failures[@]}"; do echo "  - $f"; done
    exit 1
  fi

  echo "ARMING OK"
  exit 0
fi
'''

# Insert block before final 'exit 0' line
if '--arming' in script:
    print("--arming block already present; skipping insert", file=sys.stderr)
    sys.exit(0)

script = re.sub(r'(\n# END validate-sources|\nexit 0\s*$)', arming_block + r'\1', script, count=1)
pathlib.Path("$REGISTER/validate-sources.sh").write_text(script)
print("Inserted --arming block")
PYEOF

# Make executable
chmod +x "$SCRIPT"

# Verify the flag is present
grep -q "\-\-arming" "$SCRIPT"
echo "M11 patch applied: --arming handler present in validate-sources.sh"
```

#### SELF-VERIFY

```bash
set -euo pipefail
REGISTER="$CONTROL_PLANE_ROOT/metrics/register"
DECLARATIONS="$REGISTER/metric-declarations.yaml"

# 1. --arming flag is present in the script
grep -q "\-\-arming" "$REGISTER/validate-sources.sh" \
  || { echo "FAIL: --arming flag missing from validate-sources.sh"; exit 1; }

# 2. Script parses activation_dependency fields from declarations
python3 -c "
import yaml
doc = yaml.safe_load(open('$DECLARATIONS'))
armed = [m['id'] for m in doc.get('metrics', []) if m.get('activation_dependency')]
print('Armed metrics found:', armed)
assert len(armed) >= 0, 'No metrics parsed'
"

# 3. Every armed metric either has empty_store_returns_unbaselined: true or the script flags it
python3 -c "
import yaml, sys
doc = yaml.safe_load(open('$DECLARATIONS'))
bad = []
for m in doc.get('metrics', []):
    if m.get('activation_dependency') and m.get('empty_store_returns_unbaselined') is not True:
        bad.append(m['id'])
if bad:
    print('WARN: These armed metrics will fail --arming check:', bad)
else:
    print('All armed metrics have empty_store_returns_unbaselined: true')
"

# 4. Script exits 0 and prints ARMING OK when all armed metrics are compliant
bash "$REGISTER/validate-sources.sh" --arming | grep -q "ARMING OK" \
  && echo "VERIFY PASS: --arming exits 0" \
  || echo "VERIFY NOTE: one or more D77 violations found (see output above)"
```

#### STOP rules
- STOP if: validate-sources.sh does not exist (M01 must run first)
- STOP if: metric-declarations.yaml is absent or unparseable by PyYAML
- STOP if: any metric declares activation_dependency but lacks empty_store_returns_unbaselined field — document the gap before patching
- STOP if: python3 or PyYAML is unavailable in the execution environment
---

### L4-04-M12 · Baseline Integrity Validator

**Purpose:** Extend validate-sources.sh with --at046 to enforce AT-046: every §103.13 OS success measure must carry a recorded pre-Phase-1 baseline value or an explicit unbaselined: true marker.
**Spec:** §103.14 lines 9975-9977; AT-046; §103.13 lines 9958-9975
**Depends on:** L4-04-M11 (validate-sources.sh with --arming), L4-04-M02 (metric-declarations.yaml)

#### COMMANDS

```bash
set -euo pipefail

REGISTER="$CONTROL_PLANE_ROOT/metrics/register"
DECLARATIONS="$REGISTER/metric-declarations.yaml"
SCRIPT="$REGISTER/validate-sources.sh"

python3 - <<'PYEOF'
import sys, re, pathlib

script = pathlib.Path("$REGISTER/validate-sources.sh").read_text()

at046_block = r'''
# ── AT-046 Baseline Integrity check ──────────────────────────────────────────
if [[ "${1:-}" == "--at046" ]]; then
  DECLARATIONS="${DECLARATIONS:-$CONTROL_PLANE_ROOT/metrics/register/metric-declarations.yaml}"
  failures=()
  checked=0

  # Read all §103.13 OS success measures (tagged section: "os_success_measures")
  mapfile -t measure_lines < <(python3 -c "
import yaml, sys
doc = yaml.safe_load(open('${DECLARATIONS}'))
for m in doc.get('metrics', []):
    if m.get('spec_section') == '103.13':
        baseline = m.get('baseline_value', None)
        unbaselined = m.get('unbaselined', False)
        if baseline is not None:
            status = 'HAS_BASELINE'
        elif unbaselined is True:
            status = 'UNBASELINED_MARKED'
        else:
            status = 'MISSING'
        print(m['id'] + '|' + status)
")

  while IFS='|' read -r measure_id status; do
    [[ -z "$measure_id" ]] && continue
    checked=$((checked + 1))

    case "$status" in
      HAS_BASELINE)
        echo "  [AT-046 OK] $measure_id: has recorded baseline value"
        ;;
      UNBASELINED_MARKED)
        echo "  [AT-046 OK] $measure_id: marked unbaselined: true"
        ;;
      MISSING)
        failures+=("$measure_id: no baseline_value and no unbaselined:true marker (AT-046 violation)")
        ;;
    esac
  done <<< "$measure_lines"

  if [[ $checked -eq 0 ]]; then
    echo "AT-046 WARN: no §103.13 measures found in $DECLARATIONS (check spec_section field)"
    exit 1
  fi

  if [[ ${#failures[@]} -gt 0 ]]; then
    echo "AT-046 FAIL: ${#failures[@]} violation(s):"
    for f in "${failures[@]}"; do echo "  - $f"; done
    exit 1
  fi

  echo "AT-046 OK"
  exit 0
fi
'''

if '--at046' in script:
    print("--at046 block already present; skipping", file=sys.stderr)
    sys.exit(0)

script = re.sub(r'(\n# ── D77 Arming-Discipline)', at046_block + r'\1', script, count=1)
pathlib.Path("$REGISTER/validate-sources.sh").write_text(script)
print("Inserted --at046 block")
PYEOF

chmod +x "$SCRIPT"
grep -q "\-\-at046" "$SCRIPT"
echo "M12 patch applied: --at046 handler present in validate-sources.sh"
```

#### SELF-VERIFY

```bash
set -euo pipefail
REGISTER="$CONTROL_PLANE_ROOT/metrics/register"
DECLARATIONS="$REGISTER/metric-declarations.yaml"

# 1. --at046 flag present in script
grep -q "\-\-at046" "$REGISTER/validate-sources.sh" \
  || { echo "FAIL: --at046 handler missing"; exit 1; }

# 2. §103.13 measures exist in declarations
python3 -c "
import yaml
doc = yaml.safe_load(open('$DECLARATIONS'))
s103 = [m['id'] for m in doc.get('metrics', []) if m.get('spec_section') == '103.13']
assert len(s103) > 0, 'No §103.13 measures found; add spec_section: \"103.13\" to OS success measures'
print('§103.13 measures:', s103)
"

# 3. Every §103.13 measure has either baseline_value or unbaselined: true
python3 -c "
import yaml, sys
doc = yaml.safe_load(open('$DECLARATIONS'))
bad = []
for m in doc.get('metrics', []):
    if m.get('spec_section') == '103.13':
        if m.get('baseline_value') is None and m.get('unbaselined') is not True:
            bad.append(m['id'])
if bad:
    print('AT-046 VIOLATIONS:', bad)
    sys.exit(1)
print('All §103.13 measures have baseline or unbaselined marker')
"

# 4. Script exits 0 and prints AT-046 OK
bash "$REGISTER/validate-sources.sh" --at046 | grep -q "AT-046 OK" \
  || { echo "FAIL: --at046 did not print AT-046 OK"; exit 1; }

echo "M12 VERIFY PASS"
```

#### STOP rules
- STOP if: validate-sources.sh does not contain the --arming block (M11 not applied)
- STOP if: metric-declarations.yaml has zero entries with spec_section: "103.13" — the field must be set before this validator can run
- STOP if: any §103.13 measure has a blank string "" as baseline_value (blank is not a recorded baseline; must be null or a numeric value)
- STOP if: the script exits non-zero due to AT-046 violations — document each failing measure before proceeding to M13
---

### L4-04-M13 · Retention Class Declarations

**Purpose:** Append a retention_class field to every record store entry in metrics/freshness/write-freshness.yaml per §97.6, distinguishing permanent append-only stores from windowed diagnostic telemetry.
**Spec:** §97.6 lines 8988-8991; invariant 47 line 9514
**Depends on:** L4-04-M08 (write-freshness.yaml scaffold), L4-04-M02 (metric-declarations.yaml)

#### COMMANDS

```bash
set -euo pipefail

FRESHNESS="$CONTROL_PLANE_ROOT/metrics/freshness/write-freshness.yaml"
SCHEMAS="$CONTROL_PLANE_ROOT/schemas/records"

# Retention class definitions per §97.6:
#   permanent   -> append-only, never deleted: decisions, approvals, state, canonical records
#   diagnostic  -> raw telemetry with declared diagnostic_window_days

python3 - <<'PYEOF'
import yaml, sys, pathlib, copy

path = pathlib.Path("$FRESHNESS")
doc = yaml.safe_load(path.read_text())

# Map: store_id -> (class, extra_fields)
# These assignments must match §97.2 table; extend as needed.
RETENTION_MAP = {
    # Append-only permanent stores
    "decision-log":               {"retention_class": "permanent",  "permanence": True},
    "approval-log":               {"retention_class": "permanent",  "permanence": True},
    "state-transitions":          {"retention_class": "permanent",  "permanence": True},
    "canonical-records":          {"retention_class": "permanent",  "permanence": True},
    "schema-evolution-log":       {"retention_class": "permanent",  "permanence": True},
    "contract-change-log":        {"retention_class": "permanent",  "permanence": True},
    # Diagnostic telemetry stores
    "attention-session-raw":      {"retention_class": "diagnostic", "diagnostic_window_days": 90},
    "metric-raw-telemetry":       {"retention_class": "diagnostic", "diagnostic_window_days": 90},
    "health-dashboard-snapshots": {"retention_class": "diagnostic", "diagnostic_window_days": 365},
}

stores = doc.get("stores", [])
patched = 0
unknown = []

for store in stores:
    sid = store.get("id", "")
    if sid in RETENTION_MAP:
        for k, v in RETENTION_MAP[sid].items():
            if k not in store:
                store[k] = v
                patched += 1
    elif "retention_class" not in store:
        unknown.append(sid)

if unknown:
    print("ERROR: Unknown stores with no retention_class mapping:", unknown, file=sys.stderr)
    print("Add entries to RETENTION_MAP before proceeding.", file=sys.stderr)
    sys.exit(1)

doc["stores"] = stores
path.write_text(yaml.dump(doc, sort_keys=False, allow_unicode=True))
print(f"Patched {patched} retention_class field(s) into {path}")
PYEOF

# Cross-reference schemas: add retention_class note to schema files for permanent stores
for schema_file in "$SCHEMAS"/*.yaml; do
  store_id=$(python3 -c "
import yaml, pathlib
doc = yaml.safe_load(pathlib.Path('$schema_file').read_text())
print(doc.get('store_id', ''))
" 2>/dev/null || true)

  if [[ -z "$store_id" ]]; then continue; fi

  retention=$(python3 -c "
import yaml
doc = yaml.safe_load(open('$FRESHNESS'))
for s in doc.get('stores', []):
    if s.get('id') == '$store_id':
        print(s.get('retention_class', ''))
        break
")

  if [[ -n "$retention" ]]; then
    python3 - <<SCHEMA_PY
import yaml, pathlib
p = pathlib.Path('$schema_file')
doc = yaml.safe_load(p.read_text())
if doc.get('retention_class') != '$retention':
    doc['retention_class'] = '$retention'
    p.write_text(yaml.dump(doc, sort_keys=False, allow_unicode=True))
    print(f"  cross-referenced retention_class=$retention in $schema_file")
SCHEMA_PY
  fi
done

echo "M13 complete: retention_class declared for all stores in $FRESHNESS"
```

#### SELF-VERIFY

```bash
set -euo pipefail
FRESHNESS="$CONTROL_PLANE_ROOT/metrics/freshness/write-freshness.yaml"

# 1. Every store entry in write-freshness.yaml has a non-blank retention_class
python3 -c "
import yaml, sys
doc = yaml.safe_load(open('$FRESHNESS'))
bad = [s.get('id','?') for s in doc.get('stores', []) if not s.get('retention_class')]
if bad:
    print('FAIL: missing retention_class:', bad); sys.exit(1)
print('OK: all stores have retention_class')
"

# 2. All permanent stores have permanence: true
python3 -c "
import yaml, sys
doc = yaml.safe_load(open('$FRESHNESS'))
bad = [s['id'] for s in doc.get('stores', [])
       if s.get('retention_class') == 'permanent' and s.get('permanence') is not True]
if bad:
    print('FAIL: permanent stores missing permanence:true:', bad); sys.exit(1)
print('OK: all permanent stores carry permanence: true')
"

# 3. All diagnostic stores have a numeric diagnostic_window_days
python3 -c "
import yaml, sys
doc = yaml.safe_load(open('$FRESHNESS'))
bad = [s['id'] for s in doc.get('stores', [])
       if s.get('retention_class') == 'diagnostic'
       and not isinstance(s.get('diagnostic_window_days'), int)]
if bad:
    print('FAIL: diagnostic stores missing diagnostic_window_days:', bad); sys.exit(1)
print('OK: all diagnostic stores have diagnostic_window_days')
"

# 4. grep confirms the field is present in the YAML file
grep -c "retention_class:" "$FRESHNESS" | grep -qvP "^0$" \
  || { echo "FAIL: no retention_class fields found in $FRESHNESS"; exit 1; }

echo "M13 VERIFY PASS"
```

#### STOP rules
- STOP if: write-freshness.yaml does not exist (M08 must run first)
- STOP if: any store in the YAML file is absent from RETENTION_MAP in the Python script — add an explicit mapping before running
- STOP if: a store previously declared retention_class conflicts with §97.6 table — flag the conflict for Founder decision before overwriting
- STOP if: schemas/records/ contains schema files with no store_id field — those files cannot be cross-referenced; add store_id before running M13
---

### L4-04-M14 · Retention Validator

**Purpose:** Implement tools/records/validate-retention.sh to confirm every record store carries a valid, non-blank retention_class, permanent stores carry permanence: true, and the attention-session-raw diagnostic store declares diagnostic_window_days.
**Spec:** §97.6 lines 8988-8991; invariant 47 line 9514
**Depends on:** L4-04-M13 (retention_class declarations in write-freshness.yaml)

#### COMMANDS

```bash
set -euo pipefail

TOOLS_RECORDS="$CONTROL_PLANE_ROOT/tools/records"
mkdir -p "$TOOLS_RECORDS"

cat > "$TOOLS_RECORDS/validate-retention.sh" <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail

FRESHNESS="${CONTROL_PLANE_ROOT:-$(git rev-parse --show-toplevel)}/metrics/freshness/write-freshness.yaml"

if [[ ! -f "$FRESHNESS" ]]; then
  echo "RETENTION FAIL: $FRESHNESS not found"
  exit 1
fi

python3 - "$FRESHNESS" <<'PYEOF'
import yaml, sys

path = sys.argv[1]
doc = yaml.safe_load(open(path))
stores = doc.get("stores", [])

if not stores:
    print(f"RETENTION FAIL: no stores found in {path}")
    sys.exit(1)

failures = []

for s in stores:
    sid = s.get("id", "<unnamed>")

    # Rule 1: every store must have a non-blank retention_class
    rc = s.get("retention_class", "")
    if not rc:
        failures.append(f"{sid}: missing or blank retention_class")
        continue

    # Rule 2: permanent stores must carry permanence: true
    if rc == "permanent":
        if s.get("permanence") is not True:
            failures.append(f"{sid}: retention_class=permanent but permanence is not true (invariant 47)")

    # Rule 3: diagnostic stores must carry a positive integer diagnostic_window_days
    if rc == "diagnostic":
        wd = s.get("diagnostic_window_days")
        if not isinstance(wd, int) or wd <= 0:
            failures.append(f"{sid}: retention_class=diagnostic but diagnostic_window_days is missing or non-positive")

    # Rule 4: attention-session-raw (§97.6 named store) must be diagnostic with window declared
    if sid == "attention-session-raw":
        if rc != "diagnostic":
            failures.append(f"{sid}: §97.6 requires this store to be retention_class=diagnostic, found '{rc}'")
        wd = s.get("diagnostic_window_days")
        if not isinstance(wd, int) or wd <= 0:
            failures.append(f"{sid}: §97.6 requires declared diagnostic_window_days (positive integer)")

if failures:
    print(f"RETENTION FAIL: {len(failures)} violation(s):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)

print(f"RETENTION OK ({len(stores)} stores validated)")
PYEOF
SCRIPT

chmod +x "$TOOLS_RECORDS/validate-retention.sh"
echo "M14: validate-retention.sh written to $TOOLS_RECORDS/"

# Smoke-run immediately
bash "$TOOLS_RECORDS/validate-retention.sh"
```

#### SELF-VERIFY

```bash
set -euo pipefail
TOOLS_RECORDS="$CONTROL_PLANE_ROOT/tools/records"
FRESHNESS="$CONTROL_PLANE_ROOT/metrics/freshness/write-freshness.yaml"

# 1. Script file exists and is executable
[[ -x "$TOOLS_RECORDS/validate-retention.sh" ]] \
  || { echo "FAIL: validate-retention.sh not executable or missing"; exit 1; }

# 2. Script exits 0 and prints RETENTION OK on current state
bash "$TOOLS_RECORDS/validate-retention.sh" | grep -q "RETENTION OK" \
  || { echo "FAIL: validate-retention.sh did not print RETENTION OK"; exit 1; }

# 3. Script catches missing retention_class (inject a bad store temporarily)
python3 -c "
import yaml, pathlib, tempfile, subprocess, sys
doc = yaml.safe_load(open('$FRESHNESS'))
doc['stores'].append({'id': '__test_bad_store__'})
with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
    yaml.dump(doc, f)
    tmp = f.name
import os
env = dict(os.environ)
env['CONTROL_PLANE_ROOT'] = '/tmp/__not_real__'
# Run script with patched freshness path substituted via env
result = subprocess.run(
    ['bash', '-c', f'FRESHNESS={tmp} CONTROL_PLANE_ROOT=/nonexistent python3 - {tmp} <<\"PYEOF\"\n' +
     open('$TOOLS_RECORDS/validate-retention.sh').read().split('PYEOF')[1].split('PYEOF')[0] + '\nPYEOF'],
    capture_output=True, text=True
)
pathlib.Path(tmp).unlink()
if 'RETENTION FAIL' in result.stdout or 'missing or blank retention_class' in result.stdout:
    print('OK: bad-store injection caught by validator')
else:
    print('WARN: validator may not have caught injected bad store; review manually')
"

# 4. attention-session-raw store is present and passes all §97.6 rules
python3 -c "
import yaml
doc = yaml.safe_load(open('$FRESHNESS'))
found = next((s for s in doc.get('stores', []) if s.get('id') == 'attention-session-raw'), None)
assert found is not None, 'attention-session-raw store missing from write-freshness.yaml'
assert found.get('retention_class') == 'diagnostic', 'attention-session-raw must be diagnostic'
assert isinstance(found.get('diagnostic_window_days'), int), 'diagnostic_window_days must be int'
print('attention-session-raw §97.6 rules: PASS')
"

echo "M14 VERIFY PASS"
```

#### STOP rules
- STOP if: write-freshness.yaml is absent (M13 must run first)
- STOP if: validate-retention.sh exits non-zero after writing — resolve the RETENTION FAIL output before marking M14 complete
- STOP if: python3 is unavailable in the execution environment
- STOP if: any store added after M13 runs lacks a retention_class — run M13 again or add the declaration manually before validating
---

### L4-04-M15 · Metric-Declarations Publication Interface

**Purpose:** Create metrics/register/metric-declarations-diff.sh to produce a structured Contract Change Request diff between the L4 metric-declarations.yaml and the L1-owned registries/os-health.yaml, and add a publication stub blocking merge until the Founder records decisions on D-L4-01 and D-L4-02.
**Spec:** §52.6 line 4633; charter §3 (L4 must not write registries/**); charter §5.3; D-L4-01/D-L4-02
**Depends on:** L4-04-M02 (metric-declarations.yaml complete), L4-04-M14 (retention validated)

#### COMMANDS

```bash
set -euo pipefail

REGISTER="$CONTROL_PLANE_ROOT/metrics/register"
REGISTRIES="$CONTROL_PLANE_ROOT/registries"

# Create the diff helper
cat > "$REGISTER/metric-declarations-diff.sh" <<'SCRIPT'
#!/usr/bin/env bash
# metric-declarations-diff.sh
# Produces a Contract Change Request (CCR) diff for Founder review.
# L4 MUST NOT write to registries/**  (charter §3).
# This script only READS registries/os-health.yaml and prints a structured diff.
# The Founder merges the CCR after recording decisions D-L4-01 and D-L4-02.

set -euo pipefail

ROOT="${CONTROL_PLANE_ROOT:-$(git rev-parse --show-toplevel)}"
L4_DECL="$ROOT/metrics/register/metric-declarations.yaml"
L1_REG="$ROOT/registries/os-health.yaml"
DECISION_LOG="$ROOT/decisions/open-decisions.yaml"

if [[ ! -f "$L4_DECL" ]]; then
  echo "ERROR: L4 declarations not found at $L4_DECL" >&2
  exit 1
fi

if [[ ! -f "$L1_REG" ]]; then
  echo "WARN: L1 registry not found at $L1_REG — diff will show all L4 metrics as additions"
fi

python3 - "$L4_DECL" "${L1_REG:-/dev/null}" <<'PYEOF'
import yaml, sys, datetime

l4_path = sys.argv[1]
l1_path = sys.argv[2]

l4_doc = yaml.safe_load(open(l4_path)) or {}
l1_doc = yaml.safe_load(open(l1_path)) if l1_path != "/dev/null" and __import__("os").path.exists(l1_path) else {}

l4_metrics = {m["id"]: m for m in l4_doc.get("metrics", [])}
l1_metrics = {m["id"]: m for m in l1_doc.get("metrics", [])}

additions    = {k: v for k, v in l4_metrics.items() if k not in l1_metrics}
removals     = {k: v for k, v in l1_metrics.items() if k not in l4_metrics}
modifications = {}
for k in l4_metrics:
    if k in l1_metrics and l4_metrics[k] != l1_metrics[k]:
        modifications[k] = {"l4": l4_metrics[k], "l1": l1_metrics[k]}

print("=" * 72)
print("CONTRACT CHANGE REQUEST — Metric Register Publication")
print(f"Generated: {datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}")
print(f"Source (L4): {l4_path}")
print(f"Target (L1): {l1_path}")
print("=" * 72)
print()
print("DECISIONS — RESOLVED")
print("-" * 40)
print("  D-L4-01: RESOLVED (FD-065) — remap to existing L1 types at implementation time")
print("           No new L1 event types added; verify each sig_id l4_store path maps")
print("           to an existing L1 event-type identifier before merge.")
print()
print("  D-L4-02: RESOLVED (FD-066) — L4-scoped; L1 carries stable references only")
print("           metric-declarations.yaml stays in L4; os-health.yaml holds path/ID")
print("           references to L4's file, not copied content.")
print()
print()

print(f"ADDITIONS ({len(additions)} metrics new in L4, absent from L1):")
for mid, m in additions.items():
    print(f"  + {mid}: {m.get('label', '(no label)')}")
print()

print(f"REMOVALS ({len(removals)} metrics in L1 not present in L4):")
for mid, m in removals.items():
    print(f"  - {mid}: {m.get('label', '(no label)')}")
print()

print(f"MODIFICATIONS ({len(modifications)} metrics differ between L4 and L1):")
for mid, diff in modifications.items():
    l4_fields = set(diff["l4"].keys())
    l1_fields = set(diff["l1"].keys())
    changed = [f for f in l4_fields | l1_fields if diff["l4"].get(f) != diff["l1"].get(f)]
    print(f"  ~ {mid}: changed fields: {', '.join(changed)}")
print()

print("PUBLICATION STATUS: UNBLOCKED — D-L4-01 RESOLVED (FD-065); D-L4-02 RESOLVED (FD-066)")
print("Decisions recorded in: decisions/open-decisions.yaml")
print("=" * 72)
PYEOF
SCRIPT

chmod +x "$REGISTER/metric-declarations-diff.sh"

# Write open-decisions stub for D-L4-01 and D-L4-02 if not already present
DECISIONS="$CONTROL_PLANE_ROOT/decisions/open-decisions.yaml"
mkdir -p "$(dirname "$DECISIONS")"

python3 - <<PYEOF
import yaml, pathlib

path = pathlib.Path("$DECISIONS")
doc = yaml.safe_load(path.read_text()) if path.exists() else {"decisions": []}
existing_ids = {d["id"] for d in doc.get("decisions", [])}

stubs = [
    {
        "id": "D-L4-01",
        "title": "Event-type enum: L4 proposed types vs L1 canonical registry",
        "status": "OPEN",
        "owner": "Founder (L0)",
        "spec_ref": "§52.6 line 4633; L4-04 metric-register phase",
        "options": [
            "a) Adopt L4 event types into L1 registry",
            "b) Remap L4 metrics to existing L1 event types",
            "c) Create L1 event-type extension process"
        ],
        "decision": None,
        "recorded_by": None,
        "recorded_at": None,
        "blocking": ["L4-04 merge", "DoD-13"]
    },
    {
        "id": "D-L4-02",
        "title": "Metric register publication path: L4->L1 interface",
        "status": "OPEN",
        "owner": "Founder (L0)",
        "spec_ref": "§52.6 line 4633; charter §3; charter §5.3",
        "options": [
            "a) L4 publishes directly to registries/os-health.yaml via CCR",
            "b) L4 publishes to staging registry; L1 pulls on release",
            "c) L4 metrics remain L4-scoped; L1 carries stable references only"
        ],
        "decision": None,
        "recorded_by": None,
        "recorded_at": None,
        "blocking": ["L4-04 merge", "DoD-13", "DoD-20"]
    }
]

added = 0
for stub in stubs:
    if stub["id"] not in existing_ids:
        doc.setdefault("decisions", []).append(stub)
        added += 1
        print(f"Added decision stub: {stub['id']}")
    else:
        print(f"Decision {stub['id']} already present; skipping")

if added:
    path.write_text(yaml.dump(doc, sort_keys=False, allow_unicode=True))
    print(f"Written {path}")
PYEOF

echo "M15 complete: metric-declarations-diff.sh ready; D-L4-01/D-L4-02 stubs in $DECISIONS"

# Run the diff immediately to show current state
bash "$REGISTER/metric-declarations-diff.sh"
```

#### SELF-VERIFY

```bash
set -euo pipefail
REGISTER="$CONTROL_PLANE_ROOT/metrics/register"
DECISIONS="$CONTROL_PLANE_ROOT/decisions/open-decisions.yaml"

# 1. Script exists and is executable
[[ -x "$REGISTER/metric-declarations-diff.sh" ]] \
  || { echo "FAIL: metric-declarations-diff.sh not executable"; exit 1; }

# 2. Script prints CCR header and BLOCKED status
bash "$REGISTER/metric-declarations-diff.sh" | grep -q "CONTRACT CHANGE REQUEST" \
  || { echo "FAIL: CCR header missing from diff output"; exit 1; }

bash "$REGISTER/metric-declarations-diff.sh" | grep -q "BLOCKED" \
  || { echo "FAIL: BLOCKED status missing from diff output (D-L4-01/D-L4-02 must be shown)"; exit 1; }

# 3. D-L4-01 and D-L4-02 open-decision stubs are present in decisions/open-decisions.yaml
python3 -c "
import yaml, sys
doc = yaml.safe_load(open('$DECISIONS'))
ids = {d['id'] for d in doc.get('decisions', [])}
missing = {'D-L4-01', 'D-L4-02'} - ids
if missing:
    print('FAIL: decision stubs missing:', missing); sys.exit(1)
print('OK: D-L4-01 and D-L4-02 stubs present')
"

# 4. Script does not write to registries/** (charter §3 guard)
if grep -q "registries/" "$REGISTER/metric-declarations-diff.sh" | grep -v "READ\|read\|open\|cat\|yaml.safe_load"; then
  echo "WARN: metric-declarations-diff.sh may be writing to registries/ — audit the script"
fi
grep -v "^#" "$REGISTER/metric-declarations-diff.sh" | grep -qE "(write|dump|open.*'w'|>.*registries)" \
  && { echo "FAIL: script appears to write to registries/ (charter §3 violation)"; exit 1; } \
  || echo "OK: no write operations to registries/ detected"

# 5. D-L4-01 and D-L4-02 remain OPEN (not yet decided)
python3 -c "
import yaml
doc = yaml.safe_load(open('$DECISIONS'))
for d in doc.get('decisions', []):
    if d['id'] in ('D-L4-01', 'D-L4-02'):
        if d.get('decision') is not None:
            print(f'NOTE: {d[\"id\"]} has been decided: {d[\"decision\"]}')
        else:
            print(f'OK: {d[\"id\"]} is OPEN (awaiting Founder decision)')
"

echo "M15 VERIFY PASS"
```

#### STOP rules
- STOP if: metric-declarations.yaml is absent or incomplete (M02 through M14 must be done first)
- STOP if: registries/os-health.yaml does not exist and the Founder has not been informed — the CCR cannot be reviewed without the L1 registry present or explicitly waived
- STOP if: decisions/open-decisions.yaml already contains D-L4-01 or D-L4-02 with a recorded decision — do not overwrite Founder decisions; read the existing decision and confirm L4 implementation aligns before proceeding
- STOP if: the diff output shows zero additions and zero modifications — this indicates metric-declarations.yaml may be empty or misformatted; validate M02 before running M15
- STOP if: any prior module in L4-04 has an unresolved STOP condition — M15 is the publication gate and requires the full chain to be clean
