<!-- PARTIAL-SUPERSEDED (FD-B1-L2 + FD-044, 2026-09-02):
     The L2-P1-Txx namespace tasks and actor-gate implementation in this file are superseded by L2-05-tasks.md.
     The task bodies in this file for IDs that L2-05 §2.1 directs you here are STILL AUTHORITATIVE — execute from this file.
     Do NOT execute any L2-P1-Txx or actor-gate tasks from this file. -->

# L2-02 — PHASE 2: THE DIGEST INVARIANT AND THE ARTIFACT CHAIN

**Lane:** L2 Pipeline & Evidence (subsystems E, F)
**Branch for this phase:** `lane/2/phase2-digest-invariant`
**Authority:** subordinate to `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` (FROZEN) and to `C:/D_Drive/PS/MultiProduct/Code/implementation/lanes/L2-00-charter.md`. Where this document and PARTITION.md appear to disagree, PARTITION.md wins and this document is defective.
**Spec of record:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines).

---

## 0. WHAT THIS PHASE BUILDS, AND WHY IT IS THE LOAD-BEARING ONE

Section 32 (lines 2803–2828) states the rule the whole evidence chain rests on:

> item 5 and item 11 must match, and the digest deployed to production must be byte-identical to the one verified in staging. CI rejects any production deployment where the requested digest differs from the digest that passed staging verification.

Section 33.4 (lines 2887–2912) restates it as a P0 pipeline property: *"The digest verified in staging is the digest deployed to production. CI rejects any deployment where the digest differs from the one staging verified."* Invariant 22 (line 9483) and invariant 23 (line 9484) make it non-negotiable and add the outage case: *never rebuild an artifact to work around registry unavailability* (Section 46.2, lines 4132–4149).

Section 32 also names the single sanctioned exception: for an **S18 platform-rebuild deployment** (Section 96.6 row S18, L8835; D78, L10172) — a product deploying by git-push to a PaaS that rebuilds per environment, where the byte-identical digest is structurally unavailable — the recorded identity of *pinned commit SHA plus lockfile plus recorded build configuration* stands in for the digest throughout the chain.

Section 48.3 (lines 4317–4320) attaches the SBOM to the same step: *"Every production artifact build emits a Software Bill of Materials beside the artifact digest — same pipeline step, same storage discipline, same immutability."*

This phase writes that machinery as executable code. Nothing here is documentation of an intention.

### 0.1 Files this phase creates — the complete list

Every path is inside a Lane 2 owned tree (`PARTITION.md` line 18).

| # | Path | Owned tree |
|---|---|---|
| 1 | `tools/evidence/lib/record-read.sh` | `tools/evidence/**` |
| 2 | `tools/evidence/lib/identity.sh` | `tools/evidence/**` |
| 3 | `tools/evidence/compute-platform-identity.sh` | `tools/evidence/**` |
| 4 | `tools/evidence/assert-staging-verified-identity.sh` | `tools/evidence/**` |
| 5 | `tools/evidence/assert-artifact-published.sh` | `tools/evidence/**` |
| 6 | `tools/evidence/assert-sbom-beside-digest.sh` | `tools/evidence/**` |
| 7 | `tools/evidence/build-artifact.sh` | `tools/evidence/**` |
| 8 | `tools/evidence/test/stub/docker` | `tools/evidence/**` |
| 9 | `tools/evidence/test/fixtures/**` (5 record sets) | `tools/evidence/**` |
| 10 | `tools/evidence/test/run-all.sh` | `tools/evidence/**` |
| 11 | `.github/workflows/build.yml` | `.github/workflows/**` |
| 12 | `.github/workflows/digest-gate.yml` | `.github/workflows/**` |
| 13 | `.github/workflows/digest-invariant-selftest.yml` | `.github/workflows/**` |
| 14 | `templates/workflows/artifact-conventions.yaml` | `templates/workflows/**` |
| 15 | `templates/workflows/build.yml` | `templates/workflows/**` |
| 16 | `templates/workflows/build-platform-rebuild.yml` | `templates/workflows/**` |
| 17 | `templates/workflows/digest-gate.call.yml` | `templates/workflows/**` |

This phase creates **no other file** and edits **no existing file**, including `templates/workflows/required-checks.yaml`, which task `L2-T003` froze.

### 0.2 Task-id block reserved by this phase

The charter (`L2-00-charter.md` section 12) reserves ranges per subsystem. Within them, **this phase uses exactly these ids and no others**:

| Range used here | Tree |
|---|---|
| `L2-T200`–`L2-T202` | `.github/workflows/**` |
| `L2-T400`–`L2-T405` | `templates/workflows/**` |
| `L2-T520`–`L2-T528` | `tools/evidence/**` |

**This file is authoritative for `L2-T520`–`L2-T528`.** Six of them — `L2-T520`–`L2-T525` — were also carrying bodies in `L2-05-tasks.md` for different units of work (`L2-99-review.md` defect **B2**). The bodies in §3 below are the definitions of record; `L2-05-tasks.md` §2.1 now carries an index entry for each and has renumbered its own, different work to `L2-T550`–`L2-T555`.

### 0.3 Two rules that apply to every task in this phase

**Rule P2-A — no third-party GitHub Action other than the one already SHA-verified.**
Section 48.1 (lines 4300–4308) and Section 33.2 (lines 2854–2869) require every third-party Action pinned to a full commit SHA, no tags, no exceptions. The only SHA verified for this estate is `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2` (established in `L2-T004`). Every other capability in this phase is achieved with shell against tooling preinstalled on `ubuntu-latest` (`docker`, `docker buildx`, `jq`, `sha256sum`). **Do not add any other `uses:` line. Do not invent a SHA.** If a task appears to need one, STOP under charter rule `S4`.

**Rule P2-B — fail closed, never fall through.**
Every assertion in this phase exits non-zero on doubt and prints one of the fixed verdict strings registered in `templates/workflows/artifact-conventions.yaml`. A missing input, an unparseable record, an unreachable registry and a mismatched identity are all failures. There is no "assume ok" branch anywhere in this phase, and no task may add one.

---

## 1. SESSION SETUP — RUN ONCE BEFORE ANY TASK

**Commands**

```bash
set -euo pipefail
export CONTROL_PLANE_ROOT="<absolute path to the control-plane repo working copy>"
cd "$CONTROL_PLANE_ROOT"
git rev-parse --is-inside-work-tree || { echo "NOT A GIT REPO — STOP"; exit 1; }
test -f templates/workflows/required-checks.yaml || { echo "PHASE 0 NOT MERGED — STOP"; exit 1; }
test -f .github/workflows/lane-guard.yml || { echo "PHASE 0 NOT MERGED — STOP"; exit 1; }
```

If either `test -f` fails, phase 0 (`L2-00-charter.md`, tasks `L2-T001`–`L2-T006`) has not merged to `integration`. **STOP** and file the blocker with STOP RULE `S1`.

---

## 2. TASK TABLE

| Task | Creates | Size | Depends on |
|---|---|---|---|
| `L2-T520` | branch + `tools/evidence/lib/record-read.sh` | S | `L2-T006` |
| `L2-T521` | `tools/evidence/lib/identity.sh` | S | `L2-T520` |
| `L2-T522` | `tools/evidence/compute-platform-identity.sh` | M | `L2-T521` |
| `L2-T523` | `tools/evidence/assert-staging-verified-identity.sh` | L | `L2-T520`, `L2-T521` |
| `L2-T524` | `tools/evidence/assert-artifact-published.sh` | S | `L2-T521` |
| `L2-T525` | `tools/evidence/assert-sbom-beside-digest.sh` | S | `L2-T521` |
| `L2-T526` | `tools/evidence/build-artifact.sh` | M | `L2-T521`, `L2-T522`, `L2-T525` |
| `L2-T527` | `tools/evidence/test/stub/docker` + `tools/evidence/test/fixtures/**` | M | `L2-T523`, `L2-T524`, `L2-T525` |
| `L2-T528` | `tools/evidence/test/run-all.sh` | M | `L2-T527` |
| `L2-T200` | `.github/workflows/build.yml` | M | `L2-T526`, `L2-T528` |
| `L2-T201` | `.github/workflows/digest-gate.yml` | L | `L2-T523`, `L2-T524`, `L2-T528` |
| `L2-T202` | `.github/workflows/digest-invariant-selftest.yml` | S | `L2-T528` |
| `L2-T400` | `templates/workflows/artifact-conventions.yaml` | M | `L2-T521`, `L2-T522` |
| `L2-T401` | `templates/workflows/build.yml` | M | `L2-T200`, `L2-T400` |
| `L2-T402` | `templates/workflows/build-platform-rebuild.yml` | M | `L2-T200`, `L2-T400`, `L2-T522` |
| `L2-T403` | `templates/workflows/digest-gate.call.yml` | S | `L2-T201` |
| `L2-T404` | no files — files blocker D-L2-07 | S | `L2-T401`, `L2-T402` |
| `L2-T405` | no files — rebase and open the PR | S | all above |

---

## 3. TASKS

### L2-T520 — Branch, and the flat-record reader

**Size:** S  **Depends on:** `L2-T006`

**Creates:** `tools/evidence/lib/record-read.sh`

Records in `records/deployments/` are flat top-level YAML key/value documents (Section 97.2, lines 8843–8926, which prints the deployment-record shape). This reader is deliberately dependency-free — no `yq`, no `python` — because it runs inside the production gate and a missing interpreter must never be the reason the gate cannot answer. A record it cannot read unambiguously is a **failure**, never a default.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/2/phase2-digest-invariant
mkdir -p tools/evidence/lib
cat > tools/evidence/lib/record-read.sh <<'EOF'
#!/usr/bin/env bash
# Lane 2 — flat-record key reader.
# Records are flat top-level YAML key/value documents; the deployment-record
# shape is printed in MultiProduct_MasterSpec_v4.0.md Section 97.2 (lines 8843-8926).
# Dependency-free by design: this runs inside the production digest gate, and a
# missing interpreter must never be the reason the gate cannot answer.
# Contract: record_key <file> <key>
#   exit 0 -> the single value is printed on stdout with no trailing newline
#   exit 3 -> the file is unreadable, or the key is absent or repeated
# There is no default-value path. Ambiguity is failure (Lane 2 rule P2-B).

record_key() {
  local f="$1" k="$2" n raw
  if [ ! -f "$f" ]; then
    printf 'RECORD_UNREADABLE file=%s\n' "$f" >&2
    return 3
  fi
  n="$(grep -cE "^${k}:[[:space:]]" "$f" 2>/dev/null || true)"
  if [ "$n" != "1" ]; then
    printf 'RECORD_UNPARSEABLE file=%s key=%s occurrences=%s\n' "$f" "$k" "$n" >&2
    return 3
  fi
  raw="$(grep -E "^${k}:[[:space:]]" "$f" | sed -E "s/^${k}:[[:space:]]+//")"
  raw="$(printf '%s' "$raw" | sed -E 's/[[:space:]]+#.*$//')"
  raw="$(printf '%s' "$raw" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')"
  raw="$(printf '%s' "$raw" | sed -E 's/^"(.*)"$/\1/; s/^'"'"'(.*)'"'"'$/\1/')"
  printf '%s' "$raw"
  return 0
}

# record_has_no_whitespace_filename <path>
# A record filename carrying whitespace is rejected rather than word-split.
record_filename_ok() {
  case "$1" in
    *[[:space:]]*) printf 'RECORD_FILENAME_INVALID file=%s\n' "$1" >&2; return 3 ;;
    *) return 0 ;;
  esac
}
EOF
git add tools/evidence/lib/record-read.sh
git commit -m "L2-T520: flat-record key reader for the digest gate"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | On the phase branch | `git rev-parse --abbrev-ref HEAD` | exactly `lane/2/phase2-digest-invariant` |
| A2 | File exists | `test -f tools/evidence/lib/record-read.sh; echo $?` | exactly `0` |
| A3 | Script parses | `bash -n tools/evidence/lib/record-read.sh; echo $?` | exactly `0` |
| A4 | Single value read works | see SELF-VERIFY | exactly `sha256:aa` |
| A5 | Duplicate key is a failure | see SELF-VERIFY | exactly `3` |
| A6 | Absent key is a failure | see SELF-VERIFY | exactly `3` |
| A7 | No `yq` or `python` dependency | `grep -cE '(yq|python)' tools/evidence/lib/record-read.sh` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
T="$(mktemp -d)"
printf 'product: alpha\ndigest: sha256:aa\n' > "$T/ok.yaml"
printf 'product: alpha\ndigest: sha256:aa\ndigest: sha256:bb\n' > "$T/dup.yaml"
printf 'product: alpha\n' > "$T/missing.yaml"
. tools/evidence/lib/record-read.sh
V="$(record_key "$T/ok.yaml" digest)"; E1=$?
record_key "$T/dup.yaml" digest >/dev/null 2>&1; E2=$?
record_key "$T/missing.yaml" digest >/dev/null 2>&1; E3=$?
test "$V" = "sha256:aa" && test "$E1" = "0" && test "$E2" = "3" && test "$E3" = "3" \
 && echo "L2-T520 OK" || echo "L2-T520 FAIL"
```
Correct output: the single line `L2-T520 OK`.

**STOP rule:** if `git checkout integration` fails, or `templates/workflows/required-checks.yaml` is absent, phase 0 has not merged. STOP — do not create `integration` and do not re-create phase-0 files. File the blocker with STOP RULE `S1` using the charter's verbatim template.

---

### L2-T521 — The artifact-identity format library

**Size:** S  **Depends on:** `L2-T520`

**Creates:** `tools/evidence/lib/identity.sh`

Two identity modes exist and no third. `digest` is Section 32 item 5 — the registry digest recorded at build. `platform-rebuild` is the single sanctioned equivalence of Section 32 for an S18 product (Section 96.6 L8835; D78 L10172). The literal strings below are fixed by this task; the executor types them and never varies them.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/lib/identity.sh <<'EOF'
#!/usr/bin/env bash
# Lane 2 — artifact identity formats.
# Section 32 (L2825): the registry digest is the artifact identity.
# Section 96.6 row S18 (L8835) and D78 (L10172): for a platform-rebuild
# deployment the recorded identity - pinned commit, lockfile and build
# configuration - stands in for the digest throughout the chain.
# Two modes exist. There is no third, and no default.

IDENTITY_MODE_DIGEST="digest"
IDENTITY_MODE_PLATFORM_REBUILD="platform-rebuild"
IDENTITY_RE_DIGEST='^sha256:[0-9a-f]{64}$'
IDENTITY_RE_PLATFORM='^platform-rebuild:v1:[0-9a-f]{64}$'

# identity_mode_valid <mode>
identity_mode_valid() {
  case "$1" in
    "$IDENTITY_MODE_DIGEST") return 0 ;;
    "$IDENTITY_MODE_PLATFORM_REBUILD") return 0 ;;
    *) return 1 ;;
  esac
}

# identity_format_valid <mode> <value>
identity_format_valid() {
  case "$1" in
    "$IDENTITY_MODE_DIGEST")
      printf '%s' "$2" | grep -qE "$IDENTITY_RE_DIGEST" ;;
    "$IDENTITY_MODE_PLATFORM_REBUILD")
      printf '%s' "$2" | grep -qE "$IDENTITY_RE_PLATFORM" ;;
    *) return 1 ;;
  esac
}

# identity_guard <mode> <value>
# The single entry point every Lane 2 tool uses. Prints the fixed verdict
# string and returns non-zero on any doubt (Lane 2 rule P2-B).
identity_guard() {
  if ! identity_mode_valid "$1"; then
    printf 'IDENTITY_MODE_UNDECLARED mode=%s\n' "$1"
    return 1
  fi
  if ! identity_format_valid "$1" "$2"; then
    printf 'IDENTITY_FORMAT_INVALID mode=%s value=%s\n' "$1" "$2"
    return 1
  fi
  return 0
}
EOF
git add tools/evidence/lib/identity.sh
git commit -m "L2-T521: artifact identity format library (digest and S18 platform-rebuild)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Script parses | `bash -n tools/evidence/lib/identity.sh; echo $?` | exactly `0` |
| A2 | Exactly two modes declared | `grep -cE '^IDENTITY_MODE_[A-Z_]+=' tools/evidence/lib/identity.sh` | exactly `2` |
| A3 | Digest regex is the 64-hex sha256 form | `grep -c "IDENTITY_RE_DIGEST='\^sha256:\[0-9a-f\]{64}\$'" tools/evidence/lib/identity.sh` | exactly `1` |
| A4 | Platform regex is the versioned form | `grep -c 'platform-rebuild:v1:' tools/evidence/lib/identity.sh` | exactly `1` |
| A5 | Valid digest accepted | see SELF-VERIFY | `0` |
| A6 | Digest value rejected in platform mode | see SELF-VERIFY | `1` |
| A7 | Unknown mode rejected | see SELF-VERIFY | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
. tools/evidence/lib/identity.sh
D="sha256:$(printf 'a%.0s' $(seq 1 64))"
P="platform-rebuild:v1:$(printf 'b%.0s' $(seq 1 64))"
identity_guard digest "$D" >/dev/null; R1=$?
identity_guard platform-rebuild "$P" >/dev/null; R2=$?
identity_guard platform-rebuild "$D" >/dev/null; R3=$?
identity_guard container "$D" >/dev/null; R4=$?
test "$R1" = "0" && test "$R2" = "0" && test "$R3" = "1" && test "$R4" = "1" \
 && echo "L2-T521 OK" || echo "L2-T521 FAIL"
```
Correct output: the single line `L2-T521 OK`.

**STOP rule:** do not add a third identity mode. Section 32 sanctions exactly one equivalence (line 2823: *"One sanctioned equivalence exists"*). If a later task appears to need a third, STOP under charter rule `S4`.

---

### L2-T522 — Compute the S18 platform-rebuild identity (D78)

**Size:** M  **Depends on:** `L2-T521`

**Creates:** `tools/evidence/compute-platform-identity.sh`

D78 (L10172) and Section 96.6 row S18 (L8835) define the equivalent evidence as *"the pinned commit SHA plus lockfile plus recorded build configuration"*. This script turns those three inputs into one deterministic identity string. Both path lists are **required inputs with no default**: an undeclared build configuration would silently weaken the identity, which is the exact failure Section 32 forbids.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/compute-platform-identity.sh <<'EOF'
#!/usr/bin/env bash
# Lane 2 - S18 platform-rebuild identity (Section 96.6 L8835; D78 L10172).
# The byte-identical digest is structurally unavailable on a git-push PaaS that
# rebuilds per environment, so the recorded identity stands in for the digest
# throughout the Section 32 chain: pinned commit SHA + lockfile + build config.
#
# usage: compute-platform-identity.sh <repo_root> <commit_sha> <lockfile_paths_csv> <build_config_paths_csv>
# stdout on success: platform-rebuild:v1:<64 hex>
set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "USAGE_ERROR compute-platform-identity.sh <repo_root> <commit_sha> <lockfile_paths_csv> <build_config_paths_csv>"
  exit 2
fi
ROOT="$1"; COMMIT="$2"; LOCKS="$3"; CONFS="$4"

[ -d "$ROOT" ] || { echo "PLATFORM_INPUT_MISSING repo_root=$ROOT"; exit 1; }

printf '%s' "$COMMIT" | grep -qE '^[0-9a-f]{40}$' \
  || { echo "COMMIT_SHA_INVALID value=$COMMIT"; exit 1; }

[ -n "$LOCKS" ] || { echo "PLATFORM_LOCKFILE_UNDECLARED"; exit 1; }
[ -n "$CONFS" ] || { echo "PLATFORM_BUILD_CONFIG_UNDECLARED"; exit 1; }

BLOCK="$(mktemp)"
LINES="$(mktemp)"
trap 'rm -f "$BLOCK" "$LINES"' EXIT

emit_lines() { # kind csv
  local kind="$1" csv="$2" p h
  local IFS=','
  for p in $csv; do
    p="$(printf '%s' "$p" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')"
    [ -n "$p" ] || continue
    case "$p" in
      /*|*..*) echo "PLATFORM_INPUT_PATH_INVALID path=$p"; exit 1 ;;
    esac
    [ -f "$ROOT/$p" ] || { echo "PLATFORM_INPUT_MISSING path=$p"; exit 1; }
    h="$(sha256sum "$ROOT/$p" | cut -d' ' -f1)"
    printf '%s %s=%s\n' "$kind" "$p" "$h" >> "$LINES"
  done
}

: > "$LINES"
emit_lines lockfile "$LOCKS"
emit_lines buildconfig "$CONFS"

[ -s "$LINES" ] || { echo "PLATFORM_INPUT_MISSING reason=no-lines-emitted"; exit 1; }

{
  printf 'commit=%s\n' "$COMMIT"
  LC_ALL=C sort "$LINES"
} > "$BLOCK"

H="$(sha256sum "$BLOCK" | cut -d' ' -f1)"
printf 'platform-rebuild:v1:%s\n' "$H"
exit 0
EOF
chmod +x tools/evidence/compute-platform-identity.sh
git add tools/evidence/compute-platform-identity.sh
git update-index --chmod=+x tools/evidence/compute-platform-identity.sh
git commit -m "L2-T522: S18 platform-rebuild identity (D78)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Script parses | `bash -n tools/evidence/compute-platform-identity.sh; echo $?` | exactly `0` |
| A2 | Executable bit set in the index | `git ls-files -s tools/evidence/compute-platform-identity.sh \| cut -d' ' -f1` | exactly `100755` |
| A3 | Deterministic: same inputs, same identity | see SELF-VERIFY | `0` |
| A4 | Lockfile change changes the identity | see SELF-VERIFY | `0` |
| A5 | Undeclared build config fails closed | see SELF-VERIFY | prints `PLATFORM_BUILD_CONFIG_UNDECLARED`, exit `1` |
| A6 | Undeclared lockfile fails closed | see SELF-VERIFY | prints `PLATFORM_LOCKFILE_UNDECLARED`, exit `1` |
| A7 | Short or non-hex commit fails closed | see SELF-VERIFY | prints `COMMIT_SHA_INVALID`, exit `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
T="$(mktemp -d)"
printf 'lock-v1\n' > "$T/pnpm-lock.yaml"
printf 'conf-v1\n' > "$T/vercel.json"
C="$(printf 'c%.0s' $(seq 1 40))"
S="tools/evidence/compute-platform-identity.sh"
I1="$(bash "$S" "$T" "$C" 'pnpm-lock.yaml' 'vercel.json')"
I2="$(bash "$S" "$T" "$C" 'pnpm-lock.yaml' 'vercel.json')"
printf 'lock-v2\n' > "$T/pnpm-lock.yaml"
I3="$(bash "$S" "$T" "$C" 'pnpm-lock.yaml' 'vercel.json')"
O1="$(bash "$S" "$T" "$C" 'pnpm-lock.yaml' '' || true)"
O2="$(bash "$S" "$T" "$C" '' 'vercel.json' || true)"
O3="$(bash "$S" "$T" "deadbeef" 'pnpm-lock.yaml' 'vercel.json' || true)"
test "$I1" = "$I2" \
 && test "$I1" != "$I3" \
 && printf '%s' "$I1" | grep -qE '^platform-rebuild:v1:[0-9a-f]{64}$' \
 && test "$O1" = "PLATFORM_BUILD_CONFIG_UNDECLARED" \
 && test "$O2" = "PLATFORM_LOCKFILE_UNDECLARED" \
 && test "$O3" = "COMMIT_SHA_INVALID value=deadbeef" \
 && echo "L2-T522 OK" || echo "L2-T522 FAIL"
```
Correct output: the single line `L2-T522 OK`.

**STOP rule:** if `sha256sum` is not on `PATH`, STOP — do not substitute `shasum`, `openssl dgst` or any other hasher, because the identity must be reproducible byte-for-byte across the runner and the gate. File the blocker with STOP RULE `S4`, naming the missing binary.

---

### L2-T523 — THE DIGEST INVARIANT

**Size:** L  **Depends on:** `L2-T520`, `L2-T521`

**Creates:** `tools/evidence/assert-staging-verified-identity.sh`

This is the rule of Section 32 line 2823 in code. It takes a checked-out records tree, a product, an identity mode and the identity a production deploy is *requesting*, and it answers only whether a deployment record exists proving that identity passed staging verification. The record shape — `product`, `digest`, `staging_verified`, `smoke_result` — is printed verbatim in Section 97.2 (lines 8843–8926).

The semantics are **existence**, exactly as Section 32 words it (*"the digest that passed staging verification"*), not recency: an identity that once passed staging verification and carries its record remains deployable, which is what makes the Section 27.2 rollback path possible without weakening this gate.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/assert-staging-verified-identity.sh <<'EOF'
#!/usr/bin/env bash
# ===========================================================================
# THE DIGEST INVARIANT
# MultiProduct_MasterSpec_v4.0.md Section 32 (lines 2803-2828):
#   "the digest deployed to production must be byte-identical to the one
#    verified in staging. CI rejects any production deployment where the
#    requested digest differs from the digest that passed staging verification."
# Section 33.4 (lines 2887-2912) restates it as a P0 pipeline property.
# Invariant 22 (line 9483): the production artifact is the same digest
#   verified in staging. Never rebuilt.
# Section 96.6 row S18 (L8835) / D78 (L10172): for a platform-rebuild
#   product the recorded identity stands in for the digest here.
# Record shape: Section 97.2 (L8907).
#
# usage: assert-staging-verified-identity.sh <records_dir> <product> <identity_mode> <requested_identity>
#   exit 0 -> DIGEST_INVARIANT_OK
#   exit 1 -> any refusal; the first token of stdout is the verdict string
#   exit 2 -> usage error
# There is no third outcome and no "assume ok" branch.
# ===========================================================================
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/lib/identity.sh"
. "$HERE/lib/record-read.sh"

if [ "$#" -ne 4 ]; then
  echo "USAGE_ERROR assert-staging-verified-identity.sh <records_dir> <product> <identity_mode> <requested_identity>"
  exit 2
fi
RECORDS_DIR="$1"; PRODUCT="$2"; MODE="$3"; REQ="$4"

VERDICT="$(identity_guard "$MODE" "$REQ")" || { echo "$VERDICT"; exit 1; }

STORE="$RECORDS_DIR/records/deployments"
if [ ! -d "$STORE" ]; then
  echo "RECORDS_STORE_ABSENT path=$STORE"
  exit 1
fi

MATCH=""
CANDIDATES=""
SEEN=0

while IFS= read -r f; do
  [ -n "$f" ] || continue
  record_filename_ok "$f" || { echo "RECORD_FILENAME_INVALID file=$f"; exit 1; }
  p="$(record_key "$f" product)" || { echo "RECORD_UNPARSEABLE file=$f key=product"; exit 1; }
  [ "$p" = "$PRODUCT" ] || continue
  SEEN=$((SEEN + 1))
  sv="$(record_key "$f" staging_verified)" || { echo "RECORD_UNPARSEABLE file=$f key=staging_verified"; exit 1; }
  sr="$(record_key "$f" smoke_result)"     || { echo "RECORD_UNPARSEABLE file=$f key=smoke_result"; exit 1; }
  id="$(record_key "$f" digest)"           || { echo "RECORD_UNPARSEABLE file=$f key=digest"; exit 1; }
  [ "$sv" = "true" ] || continue
  [ "$sr" = "pass" ] || continue
  CANDIDATES="$CANDIDATES $id"
  if [ "$id" = "$REQ" ]; then
    MATCH="$f"
  fi
done < <(find "$STORE" -type f -name '*.yaml' | LC_ALL=C sort)

if [ -n "$MATCH" ]; then
  echo "DIGEST_INVARIANT_OK product=$PRODUCT mode=$MODE identity=$REQ record=$MATCH"
  exit 0
fi

if [ -z "$CANDIDATES" ]; then
  echo "NO_STAGING_VERIFIED_RECORD product=$PRODUCT requested=$REQ records_for_product=$SEEN"
  exit 1
fi

echo "DIGEST_INVARIANT_VIOLATION product=$PRODUCT requested=$REQ staging_verified=[$CANDIDATES ]"
exit 1
EOF
chmod +x tools/evidence/assert-staging-verified-identity.sh
git add tools/evidence/assert-staging-verified-identity.sh
git update-index --chmod=+x tools/evidence/assert-staging-verified-identity.sh
git commit -m "L2-T523: the digest invariant (Section 32) as an executable gate"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Script parses | `bash -n tools/evidence/assert-staging-verified-identity.sh; echo $?` | exactly `0` |
| A2 | Executable in the index | `git ls-files -s tools/evidence/assert-staging-verified-identity.sh \| cut -d' ' -f1` | exactly `100755` |
| A3 | Cites Section 32 by line range | `grep -c 'Section 32 (lines 2803-2828)' tools/evidence/assert-staging-verified-identity.sh` | exactly `1` |
| A4 | Matching identity passes | see SELF-VERIFY | exit `0`, stdout begins `DIGEST_INVARIANT_OK` |
| A5 | Differing identity is refused | see SELF-VERIFY | exit `1`, stdout begins `DIGEST_INVARIANT_VIOLATION` |
| A6 | Unverified staging record is refused | see SELF-VERIFY | exit `1`, stdout begins `NO_STAGING_VERIFIED_RECORD` |
| A7 | Absent store is refused | see SELF-VERIFY | exit `1`, stdout begins `RECORDS_STORE_ABSENT` |
| A8 | No branch of the script can exit 0 without a match | `grep -cE '^[[:space:]]*exit 0$' tools/evidence/assert-staging-verified-identity.sh` | exactly `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
S="tools/evidence/assert-staging-verified-identity.sh"
T="$(mktemp -d)"; mkdir -p "$T/records/deployments"
GOOD="sha256:$(printf 'a%.0s' $(seq 1 64))"
BAD="sha256:$(printf 'b%.0s' $(seq 1 64))"
cat > "$T/records/deployments/DEP-2026-08-01-001.yaml" <<YML
record_schema_version: 1
id: DEP-2026-08-01-001
product: alpha
timestamp: 2026-08-01T09:00:00Z
digest: $GOOD
approved_by: primary_owner
approval_event: https://example/run/1
staging_verified: true
uat_record: records/uat/2026-08-01-alpha.yaml
smoke_result: pass
rollback_of: null
YML
O1="$(bash "$S" "$T" alpha digest "$GOOD")"; E1=$?
set +e
O2="$(bash "$S" "$T" alpha digest "$BAD")"; E2=$?
sed -i 's/^staging_verified: true$/staging_verified: false/' "$T/records/deployments/DEP-2026-08-01-001.yaml"
O3="$(bash "$S" "$T" alpha digest "$GOOD")"; E3=$?
O4="$(bash "$S" "$(mktemp -d)" alpha digest "$GOOD")"; E4=$?
set -e
test "$E1" = "0" && case "$O1" in DIGEST_INVARIANT_OK*) : ;; *) false ;; esac \
 && test "$E2" = "1" && case "$O2" in DIGEST_INVARIANT_VIOLATION*) : ;; *) false ;; esac \
 && test "$E3" = "1" && case "$O3" in NO_STAGING_VERIFIED_RECORD*) : ;; *) false ;; esac \
 && test "$E4" = "1" && case "$O4" in RECORDS_STORE_ABSENT*) : ;; *) false ;; esac \
 && echo "L2-T523 OK" || echo "L2-T523 FAIL"
```
Correct output: the single line `L2-T523 OK`.

**STOP rule:** if any change to this script would make it exit `0` on a path other than a matched record, do not make that change. If a caller reports that the gate is "too strict" because a record is missing, that is the gate working: STOP and file the blocker with STOP RULE `S4`, quoting Section 32 line 2823. Never add a bypass flag, an override environment variable, or a "warn-only" mode.

---

### L2-T524 — Artifact publication check, and the never-rebuild rule

**Size:** S  **Depends on:** `L2-T521`

**Creates:** `tools/evidence/assert-artifact-published.sh`

Invariant 23 (line 9484): *never rebuild an artifact to work around registry unavailability*. Section 46.2 (lines 4132–4149) explains why: *"Rebuilding produces a different digest that was never verified in staging."* This script refuses, and prints the refusal in a form a responder cannot misread.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/assert-artifact-published.sh <<'EOF'
#!/usr/bin/env bash
# Lane 2 - artifact publication check.
# Invariant 23 (line 9484) and Section 46.2 (lines 4132-4149): never rebuild an
# artifact to work around registry unavailability. This script therefore has no
# success path other than "the requested digest resolves in the registry".
# usage: assert-artifact-published.sh <image_repo> <digest>
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/lib/identity.sh"

if [ "$#" -ne 2 ]; then
  echo "USAGE_ERROR assert-artifact-published.sh <image_repo> <digest>"
  exit 2
fi
REPO="$1"; DIGEST="$2"

[ -n "$REPO" ] || { echo "IMAGE_REPO_UNDECLARED"; exit 1; }
VERDICT="$(identity_guard digest "$DIGEST")" || { echo "$VERDICT"; exit 1; }

if docker buildx imagetools inspect "${REPO}@${DIGEST}" >/dev/null 2>&1; then
  echo "ARTIFACT_PUBLISHED ref=${REPO}@${DIGEST}"
  exit 0
fi

echo "ARTIFACT_NOT_RESOLVABLE ref=${REPO}@${DIGEST}"
echo "DO_NOT_REBUILD invariant=23 spec=Section-46.2 action=wait-for-the-registry"
exit 1
EOF
chmod +x tools/evidence/assert-artifact-published.sh
git add tools/evidence/assert-artifact-published.sh
git update-index --chmod=+x tools/evidence/assert-artifact-published.sh
git commit -m "L2-T524: artifact publication check with the never-rebuild refusal"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Script parses | `bash -n tools/evidence/assert-artifact-published.sh; echo $?` | exactly `0` |
| A2 | Executable in the index | `git ls-files -s tools/evidence/assert-artifact-published.sh \| cut -d' ' -f1` | exactly `100755` |
| A3 | Contains no build or push command | `grep -cE '(buildx build|docker build|--push)' tools/evidence/assert-artifact-published.sh` | exactly `0` |
| A4 | Emits the never-rebuild refusal | `grep -c 'DO_NOT_REBUILD invariant=23' tools/evidence/assert-artifact-published.sh` | exactly `1` |
| A5 | Exactly one success path | `grep -cE '^[[:space:]]*exit 0$' tools/evidence/assert-artifact-published.sh` | exactly `1` |

**SELF-VERIFY** (uses the stub created in `L2-T527`; run this after `L2-T527`, or skip to A1–A5 now and re-run then)

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash -n tools/evidence/assert-artifact-published.sh \
 && test "$(grep -cE '(buildx build|docker build|--push)' tools/evidence/assert-artifact-published.sh)" = "0" \
 && test "$(grep -c 'DO_NOT_REBUILD invariant=23' tools/evidence/assert-artifact-published.sh)" = "1" \
 && test "$(grep -cE '^[[:space:]]*exit 0$' tools/evidence/assert-artifact-published.sh)" = "1" \
 && echo "L2-T524 OK" || echo "L2-T524 FAIL"
```
Correct output: the single line `L2-T524 OK`.

**STOP rule:** if asked, in any form, to add a rebuild fallback when the registry is unreachable, refuse and STOP. Invariant 23 is one line of the spec and admits no exception. File the blocker with STOP RULE `S4`.

---

### L2-T525 — SBOM beside the digest

**Size:** S  **Depends on:** `L2-T521`

**Creates:** `tools/evidence/assert-sbom-beside-digest.sh`

Section 48.3 (lines 4317–4320): *"Every production artifact build emits a Software Bill of Materials beside the artifact digest — same pipeline step, same storage discipline, same immutability."* In `digest` mode the SBOM is the builder's own attestation, stored in the registry against the same digest, and is retrieved by digest — which is literally *beside the digest*.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/assert-sbom-beside-digest.sh <<'EOF'
#!/usr/bin/env bash
# Lane 2 - SBOM presence beside the artifact digest.
# Section 48.3 (lines 4317-4320): every production artifact build emits an SBOM
# beside the artifact digest, same pipeline step, same storage discipline, same
# immutability. Retrieval is by digest, so the SBOM cannot drift from the
# artifact it describes.
# usage: assert-sbom-beside-digest.sh <image_ref_with_digest> <out_file>
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "USAGE_ERROR assert-sbom-beside-digest.sh <image_ref_with_digest> <out_file>"
  exit 2
fi
REF="$1"; OUT="$2"

printf '%s' "$REF" | grep -qE '@sha256:[0-9a-f]{64}$' \
  || { echo "IDENTITY_FORMAT_INVALID mode=digest value=$REF"; exit 1; }

if ! docker buildx imagetools inspect "$REF" --format '{{ json .SBOM }}' > "$OUT" 2>/dev/null; then
  echo "ARTIFACT_NOT_RESOLVABLE ref=$REF"
  echo "DO_NOT_REBUILD invariant=23 spec=Section-46.2 action=wait-for-the-registry"
  exit 1
fi

CONTENT="$(tr -d ' \t\r\n' < "$OUT")"
case "$CONTENT" in
  ''|'null'|'{}'|'[]')
    echo "SBOM_MISSING ref=$REF"
    exit 1
    ;;
esac

BYTES="$(wc -c < "$OUT" | tr -d ' ')"
echo "SBOM_PRESENT ref=$REF file=$OUT bytes=$BYTES"
exit 0
EOF
chmod +x tools/evidence/assert-sbom-beside-digest.sh
git add tools/evidence/assert-sbom-beside-digest.sh
git update-index --chmod=+x tools/evidence/assert-sbom-beside-digest.sh
git commit -m "L2-T525: SBOM emitted and asserted beside the artifact digest (Section 48.3)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Script parses | `bash -n tools/evidence/assert-sbom-beside-digest.sh; echo $?` | exactly `0` |
| A2 | Executable in the index | `git ls-files -s tools/evidence/assert-sbom-beside-digest.sh \| cut -d' ' -f1` | exactly `100755` |
| A3 | Cites Section 48.3 | `grep -c 'Section 48.3 (lines 4317-4320)' tools/evidence/assert-sbom-beside-digest.sh` | exactly `1` |
| A4 | Reference must carry a digest, not a tag | `grep -c "grep -qE '@sha256:\[0-9a-f\]{64}\$'" tools/evidence/assert-sbom-beside-digest.sh` | exactly `1` |
| A5 | Empty, `null`, `{}` and `[]` all count as missing | `grep -c "''\|'null'\|'{}'\|'\[\]'" tools/evidence/assert-sbom-beside-digest.sh` | at least `1` |
| A6 | Exactly one success path | `grep -c '^exit 0$' tools/evidence/assert-sbom-beside-digest.sh` | exactly `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash -n tools/evidence/assert-sbom-beside-digest.sh \
 && test "$(grep -c 'Section 48.3 (lines 4317-4320)' tools/evidence/assert-sbom-beside-digest.sh)" = "1" \
 && test "$(grep -c '^exit 0$' tools/evidence/assert-sbom-beside-digest.sh)" = "1" \
 && echo "L2-T525 OK" || echo "L2-T525 FAIL"
```
Correct output: the single line `L2-T525 OK`.

**STOP rule:** do not add an SBOM *generator* to this script. It asserts; it does not produce. If the assertion fails because the builder produced no attestation, that is a build defect, not an assertion defect. STOP under charter rule `S4`.

---

### L2-T526 — The single build script: build once, record the digest, emit the SBOM

**Size:** M  **Depends on:** `L2-T521`, `L2-T522`, `L2-T525`

**Creates:** `tools/evidence/build-artifact.sh`

Section 33.4's pipeline (lines 2887–2912) says the artifact is built once and its digest recorded, and Section 32 item 5 names the recording point: *"Registry digest, recorded at build."* This is the one place in Lane 2 where an artifact is produced. Every workflow calls it; none reimplements it.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/build-artifact.sh <<'EOF'
#!/usr/bin/env bash
# ===========================================================================
# Lane 2 - build the artifact once, record its identity, emit its SBOM.
# Section 33.4 (lines 2887-2912): immutable artifact, digest recorded, SAME
#   digest deployed to production, never rebuilt.
# Section 32 item 5 (L2825): the registry digest is recorded at build.
# Section 48.3 (lines 4317-4320): the SBOM is emitted in the same pipeline step.
# Section 96.6 row S18 (L8835) / D78 (L10172): a platform-rebuild
#   product records the equivalent identity instead of a digest.
#
# Environment contract (all read, none defaulted silently):
#   PRODUCT              required
#   IDENTITY_MODE        required: digest | platform-rebuild
#   OUT_DIR              required: directory the identity and SBOM are written to
#   COMMIT_SHA           required: 40 hex
#   IMAGE_REPO           required when IDENTITY_MODE=digest
#   DOCKERFILE           optional, default Dockerfile        (digest mode)
#   BUILD_CONTEXT        optional, default .                 (digest mode)
#   LOCKFILE_PATHS       required when IDENTITY_MODE=platform-rebuild (csv)
#   BUILD_CONFIG_PATHS   required when IDENTITY_MODE=platform-rebuild (csv)
#   SBOM_FILE            required when IDENTITY_MODE=platform-rebuild
#   REPO_ROOT            optional, default .
# ===========================================================================
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/lib/identity.sh"

: "${PRODUCT:?PRODUCT_UNDECLARED}"
: "${IDENTITY_MODE:?IDENTITY_MODE_UNDECLARED}"
: "${OUT_DIR:?OUT_DIR_UNDECLARED}"
: "${COMMIT_SHA:?COMMIT_SHA_UNDECLARED}"
DOCKERFILE="${DOCKERFILE:-Dockerfile}"
BUILD_CONTEXT="${BUILD_CONTEXT:-.}"
REPO_ROOT="${REPO_ROOT:-.}"
IMAGE_REPO="${IMAGE_REPO:-}"
LOCKFILE_PATHS="${LOCKFILE_PATHS:-}"
BUILD_CONFIG_PATHS="${BUILD_CONFIG_PATHS:-}"
SBOM_FILE="${SBOM_FILE:-}"

identity_mode_valid "$IDENTITY_MODE" || { echo "IDENTITY_MODE_UNDECLARED mode=$IDENTITY_MODE"; exit 1; }
mkdir -p "$OUT_DIR"

case "$IDENTITY_MODE" in

  digest)
    [ -n "$IMAGE_REPO" ] || { echo "IMAGE_REPO_UNDECLARED"; exit 1; }
    [ -f "$REPO_ROOT/$DOCKERFILE" ] || { echo "DOCKERFILE_MISSING path=$DOCKERFILE"; exit 1; }
    META="$OUT_DIR/build-metadata.json"
    # --sbom=true makes the builder emit the SBOM in this same step and store it
    # in the registry against this same digest (Section 48.3).
    docker buildx build \
      --file "$REPO_ROOT/$DOCKERFILE" \
      --tag "${IMAGE_REPO}:${COMMIT_SHA}" \
      --label "org.opencontainers.image.revision=${COMMIT_SHA}" \
      --sbom=true \
      --provenance=mode=max \
      --metadata-file "$META" \
      --push \
      "$REPO_ROOT/$BUILD_CONTEXT"
    DIGEST="$(jq -r '."containerimage.digest" // empty' "$META")"
    VERDICT="$(identity_guard digest "$DIGEST")" || { echo "$VERDICT"; exit 1; }
    IDENTITY="$DIGEST"
    bash "$HERE/assert-sbom-beside-digest.sh" "${IMAGE_REPO}@${DIGEST}" "$OUT_DIR/sbom.json"
    SBOM_OUT="$OUT_DIR/sbom.json"
    ;;

  platform-rebuild)
    # D78: the byte-identical digest is structurally unavailable on a git-push
    # PaaS. The recorded identity stands in for it. The SBOM still has to exist,
    # so the caller supplies the one its own build produced; an absent file is a
    # failure, never a skip (Section 33.2 forbids a silent skip on a gate).
    [ -n "$SBOM_FILE" ] || { echo "SBOM_UNDECLARED mode=platform-rebuild"; exit 1; }
    [ -s "$REPO_ROOT/$SBOM_FILE" ] || { echo "SBOM_MISSING path=$SBOM_FILE"; exit 1; }
    IDENTITY="$(bash "$HERE/compute-platform-identity.sh" \
                 "$REPO_ROOT" "$COMMIT_SHA" "$LOCKFILE_PATHS" "$BUILD_CONFIG_PATHS")"
    VERDICT="$(identity_guard platform-rebuild "$IDENTITY")" || { echo "$VERDICT"; exit 1; }
    cp "$REPO_ROOT/$SBOM_FILE" "$OUT_DIR/sbom.json"
    SBOM_OUT="$OUT_DIR/sbom.json"
    echo "SBOM_PRESENT ref=$IDENTITY file=$SBOM_OUT bytes=$(wc -c < "$SBOM_OUT" | tr -d ' ')"
    ;;

  *)
    echo "IDENTITY_MODE_UNDECLARED mode=$IDENTITY_MODE"
    exit 1
    ;;
esac

printf '%s' "$IDENTITY" > "$OUT_DIR/identity.txt"
{
  printf 'product=%s\n'       "$PRODUCT"
  printf 'identity_mode=%s\n' "$IDENTITY_MODE"
  printf 'identity=%s\n'      "$IDENTITY"
  printf 'image_repo=%s\n'    "$IMAGE_REPO"
  printf 'commit=%s\n'        "$COMMIT_SHA"
  printf 'sbom_file=%s\n'     "$SBOM_OUT"
  printf 'run_id=%s\n'        "${GITHUB_RUN_ID:-local}"
  printf 'run_url=%s\n'       "${GITHUB_SERVER_URL:-local}/${GITHUB_REPOSITORY:-local}/actions/runs/${GITHUB_RUN_ID:-local}"
} > "$OUT_DIR/artifact.env"

echo "DIGEST_RECORDED product=$PRODUCT mode=$IDENTITY_MODE identity=$IDENTITY"
exit 0
EOF
chmod +x tools/evidence/build-artifact.sh
git add tools/evidence/build-artifact.sh
git update-index --chmod=+x tools/evidence/build-artifact.sh
git commit -m "L2-T526: build once, record the digest, emit the SBOM in the same step"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Script parses | `bash -n tools/evidence/build-artifact.sh; echo $?` | exactly `0` |
| A2 | Executable in the index | `git ls-files -s tools/evidence/build-artifact.sh \| cut -d' ' -f1` | exactly `100755` |
| A3 | Exactly one `docker buildx build` in the whole tree | `grep -rc 'docker buildx build' tools/evidence \| grep -c ':1$'` | exactly `1` |
| A4 | SBOM emitted by the same command as the digest | `grep -c -- '--sbom=true' tools/evidence/build-artifact.sh` | exactly `1` |
| A5 | Platform-rebuild mode requires an SBOM file | `grep -c 'SBOM_UNDECLARED mode=platform-rebuild' tools/evidence/build-artifact.sh` | exactly `1` |
| A6 | Missing required env fails immediately | see SELF-VERIFY | exit non-zero |
| A7 | Platform-rebuild path produces a valid identity with the stub | see SELF-VERIFY | exit `0`, final line begins `DIGEST_RECORDED` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
T="$(mktemp -d)"; O="$(mktemp -d)"
printf 'lock\n' > "$T/pnpm-lock.yaml"
printf 'conf\n' > "$T/vercel.json"
printf '{"bomFormat":"CycloneDX"}\n' > "$T/sbom.json"
C="$(printf 'c%.0s' $(seq 1 40))"
set +e
( PRODUCT=alpha IDENTITY_MODE=platform-rebuild OUT_DIR="$O" COMMIT_SHA="$C" \
  REPO_ROOT="$T" LOCKFILE_PATHS='pnpm-lock.yaml' BUILD_CONFIG_PATHS='vercel.json' \
  SBOM_FILE='sbom.json' bash tools/evidence/build-artifact.sh ) > "$O/log" 2>&1
E1=$?
( PRODUCT=alpha OUT_DIR="$O" COMMIT_SHA="$C" bash tools/evidence/build-artifact.sh ) >/dev/null 2>&1
E2=$?
set -e
test "$E1" = "0" \
 && test "$E2" != "0" \
 && tail -1 "$O/log" | grep -q '^DIGEST_RECORDED product=alpha mode=platform-rebuild identity=platform-rebuild:v1:' \
 && grep -qE '^platform-rebuild:v1:[0-9a-f]{64}$' "$O/identity.txt" \
 && grep -q '^identity_mode=platform-rebuild$' "$O/artifact.env" \
 && test -s "$O/sbom.json" \
 && echo "L2-T526 OK" || echo "L2-T526 FAIL"
```
Correct output: the single line `L2-T526 OK`.

**STOP rule:** if `jq` is absent when running the `digest` path, STOP — do not parse the metadata JSON with `grep`/`sed`, because a misparsed digest is a silently wrong identity, which is the one outcome Section 32 cannot tolerate. File the blocker with STOP RULE `S4`.

---

### L2-T527 — Test doubles and record fixtures

**Size:** M  **Depends on:** `L2-T523`, `L2-T524`, `L2-T525`

**Creates:**
- `tools/evidence/test/stub/docker`
- `tools/evidence/test/fixtures/records-ok/records/deployments/DEP-2026-08-01-001.yaml`
- `tools/evidence/test/fixtures/records-violation/records/deployments/DEP-2026-08-02-001.yaml`
- `tools/evidence/test/fixtures/records-unverified/records/deployments/DEP-2026-08-03-001.yaml`
- `tools/evidence/test/fixtures/records-unparseable/records/deployments/DEP-2026-08-04-001.yaml`
- `tools/evidence/test/fixtures/records-platform/records/deployments/DEP-2026-08-05-001.yaml`

The record shape below is transcribed from Section 97.2 (lines 8843–8926) plus the mandatory `record_schema_version`, `id`, `product` and `timestamp` fields that the same section requires of every record. Do not add or rename a field.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
mkdir -p tools/evidence/test/stub
cat > tools/evidence/test/stub/docker <<'EOF'
#!/usr/bin/env bash
# Lane 2 test double for `docker`. Used only by tools/evidence/test/run-all.sh.
# Behaviour is selected by STUB_DOCKER_MODE so the registry-facing assertions can
# be proved offline. This file is never on PATH outside the test harness.
case "${STUB_DOCKER_MODE:-ok}" in
  ok)
    for a in "$@"; do
      if [ "$a" = "--format" ]; then
        printf '{"SPDX":{"name":"stub-sbom","packages":[]}}\n'
        exit 0
      fi
    done
    printf 'Name: stub\n'
    exit 0
    ;;
  empty-sbom)
    printf 'null\n'
    exit 0
    ;;
  unreachable)
    printf 'stub: registry unreachable\n' >&2
    exit 1
    ;;
  *)
    printf 'stub: unknown STUB_DOCKER_MODE=%s\n' "${STUB_DOCKER_MODE}" >&2
    exit 1
    ;;
esac
EOF
chmod +x tools/evidence/test/stub/docker

GOOD="sha256:$(printf 'a%.0s' $(seq 1 64))"
OTHER="sha256:$(printf 'b%.0s' $(seq 1 64))"
PLAT="platform-rebuild:v1:$(printf 'c%.0s' $(seq 1 64))"

mk() { mkdir -p "tools/evidence/test/fixtures/$1/records/deployments"; }
mk records-ok; mk records-violation; mk records-unverified; mk records-unparseable; mk records-platform

cat > tools/evidence/test/fixtures/records-ok/records/deployments/DEP-2026-08-01-001.yaml <<YML
record_schema_version: 1
id: DEP-2026-08-01-001
product: alpha
timestamp: 2026-08-01T09:00:00Z
digest: ${GOOD}
approved_by: primary_owner
approval_event: https://example/run/1001
staging_verified: true
uat_record: records/uat/2026-08-01-alpha.yaml
smoke_result: pass
rollback_of: null
YML

cat > tools/evidence/test/fixtures/records-violation/records/deployments/DEP-2026-08-02-001.yaml <<YML
record_schema_version: 1
id: DEP-2026-08-02-001
product: alpha
timestamp: 2026-08-02T09:00:00Z
digest: ${OTHER}
approved_by: primary_owner
approval_event: https://example/run/1002
staging_verified: true
uat_record: records/uat/2026-08-02-alpha.yaml
smoke_result: pass
rollback_of: null
YML

cat > tools/evidence/test/fixtures/records-unverified/records/deployments/DEP-2026-08-03-001.yaml <<YML
record_schema_version: 1
id: DEP-2026-08-03-001
product: alpha
timestamp: 2026-08-03T09:00:00Z
digest: ${GOOD}
approved_by: primary_owner
approval_event: https://example/run/1003
staging_verified: false
uat_record: records/uat/2026-08-03-alpha.yaml
smoke_result: fail
rollback_of: null
YML

cat > tools/evidence/test/fixtures/records-unparseable/records/deployments/DEP-2026-08-04-001.yaml <<YML
record_schema_version: 1
id: DEP-2026-08-04-001
product: alpha
timestamp: 2026-08-04T09:00:00Z
digest: ${GOOD}
digest: ${OTHER}
approved_by: primary_owner
approval_event: https://example/run/1004
staging_verified: true
uat_record: records/uat/2026-08-04-alpha.yaml
smoke_result: pass
rollback_of: null
YML

cat > tools/evidence/test/fixtures/records-platform/records/deployments/DEP-2026-08-05-001.yaml <<YML
record_schema_version: 1
id: DEP-2026-08-05-001
product: bravo
timestamp: 2026-08-05T09:00:00Z
digest: ${PLAT}
approved_by: primary_owner
approval_event: https://example/run/1005
staging_verified: true
uat_record: records/uat/2026-08-05-bravo.yaml
smoke_result: pass
rollback_of: null
YML

git add tools/evidence/test
git update-index --chmod=+x tools/evidence/test/stub/docker
git commit -m "L2-T527: test double for docker and five deployment-record fixtures"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Five fixture record sets exist | `find tools/evidence/test/fixtures -name '*.yaml' \| wc -l \| tr -d ' '` | exactly `5` |
| A2 | Stub parses and is executable in the index | `bash -n tools/evidence/test/stub/docker && git ls-files -s tools/evidence/test/stub/docker \| cut -d' ' -f1` | exactly `100755` |
| A3 | Every fixture carries `record_schema_version` | `grep -lc '^record_schema_version: 1$' $(find tools/evidence/test/fixtures -name '*.yaml') \| wc -l \| tr -d ' '` | exactly `5` |
| A4 | The unparseable fixture really has a duplicate key | `grep -c '^digest: ' tools/evidence/test/fixtures/records-unparseable/records/deployments/DEP-2026-08-04-001.yaml` | exactly `2` |
| A5 | The platform fixture carries a platform identity | `grep -cE '^digest: platform-rebuild:v1:[0-9a-f]{64}$' tools/evidence/test/fixtures/records-platform/records/deployments/DEP-2026-08-05-001.yaml` | exactly `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(find tools/evidence/test/fixtures -name '*.yaml' | wc -l | tr -d ' ')" = "5" \
 && bash -n tools/evidence/test/stub/docker \
 && test "$(git ls-files -s tools/evidence/test/stub/docker | cut -d' ' -f1)" = "100755" \
 && test "$(grep -c '^digest: ' tools/evidence/test/fixtures/records-unparseable/records/deployments/DEP-2026-08-04-001.yaml)" = "2" \
 && echo "L2-T527 OK" || echo "L2-T527 FAIL"
```
Correct output: the single line `L2-T527 OK`.

**STOP rule:** if any fixture field name differs from the record shape printed in Section 97.2 (lines 8843–8926), STOP. Record shapes are Lane 4's (`schemas/records/**`, `PARTITION.md` line 20) and Lane 2 must not invent one. File the blocker with STOP RULE `S1`, quoting the field in question.

---

### L2-T528 — The negative-test harness

**Size:** M  **Depends on:** `L2-T527`

**Creates:** `tools/evidence/test/run-all.sh`

Charter DoD-03 requires that a production deploy requesting a digest other than the staging-verified one *"exits non-zero"*. A gate that has never been observed refusing is a gate nobody has tested. This harness observes each refusal by its exact verdict string.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > tools/evidence/test/run-all.sh <<'EOF'
#!/usr/bin/env bash
# Lane 2 - digest invariant and artifact chain: the negative-test harness.
# Every case asserts BOTH an exact exit code AND an exact leading verdict token.
# A case that passes for the wrong reason is a failed harness (the same
# discipline Section 31.2 applies to seeded-defect cases, lines 2787-2794).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
EV="$(cd "$HERE/.." && pwd)"
FIX="$HERE/fixtures"
PASS=0
FAIL=0

GOOD="sha256:$(printf 'a%.0s' $(seq 1 64))"
OTHER="sha256:$(printf 'b%.0s' $(seq 1 64))"
PLAT="platform-rebuild:v1:$(printf 'c%.0s' $(seq 1 64))"

check() { # label expected_exit expected_first_token  -- command...
  local label="$1" xc="$2" tok="$3"; shift 4
  local out rc first
  out="$("$@" 2>&1)"; rc=$?
  first="$(printf '%s' "$out" | head -1 | cut -d' ' -f1)"
  if [ "$rc" = "$xc" ] && [ "$first" = "$tok" ]; then
    printf 'PASS %s\n' "$label"; PASS=$((PASS+1))
  else
    printf 'FAIL %s expected_exit=%s got_exit=%s expected_token=%s got_token=%s\n' \
      "$label" "$xc" "$rc" "$tok" "$first"; FAIL=$((FAIL+1))
  fi
}

G="$EV/assert-staging-verified-identity.sh"

# --- the invariant itself (Section 32, lines 2803-2828) ---------------------
check inv-match-passes            0 DIGEST_INVARIANT_OK          -- bash "$G" "$FIX/records-ok"          alpha digest "$GOOD"
check inv-different-digest-refused 1 DIGEST_INVARIANT_VIOLATION  -- bash "$G" "$FIX/records-violation"   alpha digest "$GOOD"
check inv-unverified-staging-refused 1 NO_STAGING_VERIFIED_RECORD -- bash "$G" "$FIX/records-unverified" alpha digest "$GOOD"
check inv-unknown-product-refused  1 NO_STAGING_VERIFIED_RECORD  -- bash "$G" "$FIX/records-ok"          zulu  digest "$GOOD"
check inv-unparseable-record-refused 1 RECORD_UNPARSEABLE        -- bash "$G" "$FIX/records-unparseable" alpha digest "$GOOD"
check inv-absent-store-refused     1 RECORDS_STORE_ABSENT        -- bash "$G" "$HERE/nonexistent"        alpha digest "$GOOD"
check inv-bad-mode-refused         1 IDENTITY_MODE_UNDECLARED    -- bash "$G" "$FIX/records-ok"          alpha container "$GOOD"
check inv-bad-format-refused       1 IDENTITY_FORMAT_INVALID     -- bash "$G" "$FIX/records-ok"          alpha digest "sha256:short"

# --- the S18 equivalence (Section 96.6 L8835; D78 L10172) -----------
check s18-match-passes             0 DIGEST_INVARIANT_OK         -- bash "$G" "$FIX/records-platform" bravo platform-rebuild "$PLAT"
check s18-digest-in-platform-mode-refused 1 IDENTITY_FORMAT_INVALID -- bash "$G" "$FIX/records-platform" bravo platform-rebuild "$OTHER"
check s18-platform-id-in-digest-mode-refused 1 IDENTITY_FORMAT_INVALID -- bash "$G" "$FIX/records-ok" alpha digest "$PLAT"

# --- never rebuild (invariant 23, line 9484; Section 46.2, lines 4132-4149) --
export PATH="$HERE/stub:$PATH"
P="$EV/assert-artifact-published.sh"
STUB_DOCKER_MODE=ok          check reg-published-passes  0 ARTIFACT_PUBLISHED     -- env STUB_DOCKER_MODE=ok          bash "$P" ghcr.io/org/alpha "$GOOD"
STUB_DOCKER_MODE=unreachable check reg-unreachable-refused 1 ARTIFACT_NOT_RESOLVABLE -- env STUB_DOCKER_MODE=unreachable bash "$P" ghcr.io/org/alpha "$GOOD"

# --- SBOM beside the digest (Section 48.3, lines 4317-4320) ----------------
S="$EV/assert-sbom-beside-digest.sh"
TMP="$(mktemp -d)"
check sbom-present-passes  0 SBOM_PRESENT           -- env STUB_DOCKER_MODE=ok          bash "$S" "ghcr.io/org/alpha@${GOOD}" "$TMP/s1.json"
check sbom-empty-refused   1 SBOM_MISSING           -- env STUB_DOCKER_MODE=empty-sbom  bash "$S" "ghcr.io/org/alpha@${GOOD}" "$TMP/s2.json"
check sbom-unreachable-refused 1 ARTIFACT_NOT_RESOLVABLE -- env STUB_DOCKER_MODE=unreachable bash "$S" "ghcr.io/org/alpha@${GOOD}" "$TMP/s3.json"
check sbom-tag-ref-refused 1 IDENTITY_FORMAT_INVALID -- env STUB_DOCKER_MODE=ok         bash "$S" "ghcr.io/org/alpha:latest" "$TMP/s4.json"

# --- S18 identity computation (D78) ----------------------------------------
C="$EV/compute-platform-identity.sh"
W="$(mktemp -d)"; printf 'l\n' > "$W/lock"; printf 'b\n' > "$W/conf"
SHA40="$(printf 'd%.0s' $(seq 1 40))"
check s18-no-buildconfig-refused 1 PLATFORM_BUILD_CONFIG_UNDECLARED -- bash "$C" "$W" "$SHA40" lock ''
check s18-no-lockfile-refused    1 PLATFORM_LOCKFILE_UNDECLARED     -- bash "$C" "$W" "$SHA40" ''   conf
check s18-bad-commit-refused     1 COMMIT_SHA_INVALID               -- bash "$C" "$W" "nothex"  lock conf
check s18-missing-input-refused  1 PLATFORM_INPUT_MISSING           -- bash "$C" "$W" "$SHA40" absent conf

printf '\nL2 DIGEST-INVARIANT SUITE: pass=%s fail=%s\n' "$PASS" "$FAIL"
if [ "$FAIL" -ne 0 ]; then echo "SUITE_FAIL"; exit 1; fi
if [ "$PASS" -lt 21 ]; then echo "SUITE_UNDERRAN expected_at_least=21 got=$PASS"; exit 1; fi
echo "SUITE_PASS"
exit 0
EOF
chmod +x tools/evidence/test/run-all.sh
git add tools/evidence/test/run-all.sh
git update-index --chmod=+x tools/evidence/test/run-all.sh
git commit -m "L2-T528: negative-test harness for the digest invariant and artifact chain"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Harness parses | `bash -n tools/evidence/test/run-all.sh; echo $?` | exactly `0` |
| A2 | Executable in the index | `git ls-files -s tools/evidence/test/run-all.sh \| cut -d' ' -f1` | exactly `100755` |
| A3 | Whole suite passes | `bash tools/evidence/test/run-all.sh \| tail -1` | exactly `SUITE_PASS` |
| A4 | At least 21 cases run | `bash tools/evidence/test/run-all.sh \| grep -c '^PASS '` | at least `21` |
| A5 | No case is reported `FAIL` | `bash tools/evidence/test/run-all.sh \| grep -c '^FAIL '` | exactly `0` |
| A6 | A deliberately broken gate makes the suite fail | see SELF-VERIFY | exactly `SUITE_FAIL` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash tools/evidence/test/run-all.sh > /tmp/l2-suite.txt 2>&1; R=$?
cp tools/evidence/assert-staging-verified-identity.sh /tmp/l2-gate.bak
sed -i 's/^VERDICT="$(identity_guard "$MODE" "$REQ")".*$/true/' tools/evidence/assert-staging-verified-identity.sh
bash tools/evidence/test/run-all.sh > /tmp/l2-suite-broken.txt 2>&1; B=$?
cp /tmp/l2-gate.bak tools/evidence/assert-staging-verified-identity.sh
test "$R" = "0" \
 && test "$(tail -1 /tmp/l2-suite.txt)" = "SUITE_PASS" \
 && test "$B" != "0" \
 && test "$(tail -1 /tmp/l2-suite-broken.txt)" = "SUITE_FAIL" \
 && test -z "$(git diff --name-only tools/evidence/assert-staging-verified-identity.sh)" \
 && echo "L2-T528 OK" || echo "L2-T528 FAIL"
```
Correct output: the single line `L2-T528 OK`.

**STOP rule:** if a case fails, fix the **script under test**, never the expectation. Editing an expected exit code or verdict string to make the suite green is prohibited: it is the exact failure mode Section 31.2 (lines 2787–2794) names, where *a run in which the seeded case passes is a failed run*. If you believe an expectation is genuinely wrong, STOP and file the blocker with STOP RULE `S4`.

---

### L2-T200 — The reusable `build` workflow

**Size:** M  **Depends on:** `L2-T526`, `L2-T528`

**Creates:** `.github/workflows/build.yml`

Section 33.2 (lines 2854–2869): reusable workflows live in the control-plane repository, are versioned by tag and are consumed by pinned tag. This workflow contains **one job**, deliberately: a required status check must never be able to report `skipped`, and a single job that does the work and asserts the conclusion cannot skip. It uses exactly one third-party Action, at the SHA already verified in `L2-T004` (Rule P2-A).

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > .github/workflows/build.yml <<'EOF'
name: build
# Reusable build workflow. Section 33.2 (lines 2854-2869): reusable workflows
# live in the control plane, are versioned by tag, consumed by pinned tag, and
# changing one is a platform change.
# Section 33.4 (lines 2887-2912): immutable artifact, digest recorded.
# Section 48.3 (lines 4317-4320): SBOM emitted in the same pipeline step.
# ONE job by design: Section 33.2 forbids a required context that can report a
# `skipped` or `neutral` conclusion, so there is no `if:`, no `needs:` and no
# path filter anywhere in this file.
on:
  workflow_call:
    inputs:
      product:
        required: true
        type: string
      identity_mode:
        required: true
        type: string
      control_plane_ref:
        required: true
        type: string
      image_repo:
        required: false
        type: string
        default: ''
      dockerfile:
        required: false
        type: string
        default: Dockerfile
      build_context:
        required: false
        type: string
        default: '.'
      lockfile_paths:
        required: false
        type: string
        default: ''
      build_config_paths:
        required: false
        type: string
        default: ''
      sbom_file:
        required: false
        type: string
        default: ''
    secrets:
      control_plane_read_token:
        required: true
    outputs:
      identity:
        description: The recorded artifact identity (digest, or S18 platform-rebuild identity)
        value: ${{ jobs.artifact.outputs.identity }}
      identity_mode:
        description: The identity mode this artifact was recorded under
        value: ${{ jobs.artifact.outputs.identity_mode }}
permissions:
  contents: read
  packages: write
jobs:
  artifact:
    runs-on: ubuntu-latest
    outputs:
      identity: ${{ steps.build.outputs.identity }}
      identity_mode: ${{ steps.build.outputs.identity_mode }}
    steps:
      - name: Checkout product repository
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          fetch-depth: 0
          path: product
      - name: Guard the control-plane read credential
        shell: bash
        env:
          CP_TOKEN: ${{ secrets.control_plane_read_token }}
        run: |
          set -euo pipefail
          if [ -z "${CP_TOKEN}" ]; then
            echo "CONTROL_PLANE_ACCESS_UNAVAILABLE"
            exit 1
          fi
          echo "CONTROL_PLANE_ACCESS_PRESENT"
      - name: Checkout the control-plane build surface at the pinned ref
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          repository: ${{ github.repository_owner }}/control-plane
          ref: ${{ inputs.control_plane_ref }}
          token: ${{ secrets.control_plane_read_token }}
          path: control-plane
          sparse-checkout: tools/evidence
      - name: Log in to the artifact registry
        shell: bash
        env:
          REGISTRY_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          set -euo pipefail
          printf '%s' "${REGISTRY_TOKEN}" \
            | docker login ghcr.io -u "${GITHUB_ACTOR}" --password-stdin
          echo "REGISTRY_LOGIN_OK"
      - name: Build the artifact, record the digest, emit the SBOM
        id: build
        shell: bash
        env:
          PRODUCT: ${{ inputs.product }}
          IDENTITY_MODE: ${{ inputs.identity_mode }}
          IMAGE_REPO: ${{ inputs.image_repo }}
          DOCKERFILE: ${{ inputs.dockerfile }}
          BUILD_CONTEXT: ${{ inputs.build_context }}
          LOCKFILE_PATHS: ${{ inputs.lockfile_paths }}
          BUILD_CONFIG_PATHS: ${{ inputs.build_config_paths }}
          SBOM_FILE: ${{ inputs.sbom_file }}
          COMMIT_SHA: ${{ github.sha }}
          REPO_ROOT: product
          OUT_DIR: artifact-out
        run: |
          set -euo pipefail
          bash control-plane/tools/evidence/build-artifact.sh
          IDENTITY="$(cat artifact-out/identity.txt)"
          echo "identity=${IDENTITY}" >> "$GITHUB_OUTPUT"
          echo "identity_mode=${IDENTITY_MODE}" >> "$GITHUB_OUTPUT"
          {
            echo "### Artifact recorded"
            echo ""
            echo "- product: ${PRODUCT}"
            echo "- identity_mode: ${IDENTITY_MODE}"
            echo "- identity: \`${IDENTITY}\`"
            echo "- run: ${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"
          } >> "$GITHUB_STEP_SUMMARY"
      - name: Assert the identity was recorded
        shell: bash
        env:
          IDENTITY: ${{ steps.build.outputs.identity }}
        run: |
          set -euo pipefail
          if [ -z "${IDENTITY}" ]; then
            echo "DIGEST_NOT_RECORDED"
            exit 1
          fi
          echo "DIGEST_RECORDED identity=${IDENTITY}"
      - name: Assert the SBOM sits beside the identity
        shell: bash
        run: |
          set -euo pipefail
          if [ ! -s artifact-out/sbom.json ]; then
            echo "SBOM_MISSING file=artifact-out/sbom.json"
            exit 1
          fi
          echo "SBOM_PRESENT file=artifact-out/sbom.json bytes=$(wc -c < artifact-out/sbom.json | tr -d ' ')"
EOF
git add .github/workflows/build.yml
git commit -m "L2-T200: reusable build workflow — immutable artifact, digest recorded, SBOM emitted"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | File exists | `test -f .github/workflows/build.yml; echo $?` | exactly `0` |
| A2 | Reusable, not directly triggerable | `grep -c '^  workflow_call:$' .github/workflows/build.yml` | exactly `1` |
| A3 | Exactly one job | `grep -cE '^  [a-z][a-z0-9-]*:$' .github/workflows/build.yml \| head -1` — then confirm with A4 | see A4 |
| A4 | The job is `artifact` and there is no second job | `awk '/^jobs:$/{f=1;next} f&&/^  [a-z]/{print}' .github/workflows/build.yml \| wc -l \| tr -d ' '` | exactly `1` |
| A5 | No `if:`, no path filter | `grep -cE '^\s+(if:|paths:|paths-ignore:)' .github/workflows/build.yml` | exactly `0` |
| A6 | No `needs:` | `grep -cE '^[[:space:]]+needs:' .github/workflows/build.yml` | exactly `0` |
| A7 | Only the one verified Action SHA is used | `grep -oE 'uses: [^ ]+' .github/workflows/build.yml \| sort -u \| tr '\n' ' '` | exactly `uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 ` |
| A8 | Least-privilege permissions declared | `grep -c '^permissions:$' .github/workflows/build.yml` | exactly `1` |
| A9 | Fails closed on a missing control-plane token | `grep -c 'CONTROL_PLANE_ACCESS_UNAVAILABLE' .github/workflows/build.yml` | exactly `1` |
| A10 | No `latest`, no floating tag anywhere | `grep -cE '@(main|master|v[0-9]+)$' .github/workflows/build.yml` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(awk '/^jobs:$/{f=1;next} f&&/^  [a-z]/{print}' .github/workflows/build.yml | wc -l | tr -d ' ')" = "1" \
 && test "$(grep -cE '^\s+(if:|paths:|paths-ignore:)' .github/workflows/build.yml)" = "0" \
 && test "$(grep -cE '^[[:space:]]+needs:' .github/workflows/build.yml)" = "0" \
 && test "$(grep -oE 'uses: [^ ]+' .github/workflows/build.yml | sort -u | wc -l | tr -d ' ')" = "1" \
 && test "$(grep -cE 'uses: actions/checkout@[0-9a-f]{40}' .github/workflows/build.yml)" = "2" \
 && test "$(grep -cE '@(main|master|v[0-9]+)$' .github/workflows/build.yml)" = "0" \
 && test "$(grep -c 'CONTROL_PLANE_ACCESS_UNAVAILABLE' .github/workflows/build.yml)" = "1" \
 && echo "L2-T200 OK" || echo "L2-T200 FAIL"
```
Correct output: the single line `L2-T200 OK`.

**STOP rule:** do not add a second job, an `if:`, a `needs:`, a path filter or a second `uses:`. If the build genuinely needs a capability that only a third-party Action provides, STOP under Rule P2-A and charter rule `S4` — the SHA must be verified by L0 before any Action enters this estate (Section 48.1, lines 4300–4308).

---

### L2-T201 — The reusable `digest-gate` workflow

**Size:** L  **Depends on:** `L2-T523`, `L2-T524`, `L2-T528`

**Creates:** `.github/workflows/digest-gate.yml`

This is the gate Section 32 line 2823 requires. It is a standalone reusable workflow so that the `deploy-production` workflow of a later phase composes it as its first job rather than reimplementing it. It fails closed on every input it cannot verify.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > .github/workflows/digest-gate.yml <<'EOF'
name: digest-gate
# THE PRODUCTION DIGEST GATE.
# Section 32 (lines 2803-2828): "CI rejects any production deployment where the
#   requested digest differs from the digest that passed staging verification."
# Section 33.4 (lines 2887-2912): artifact immutability is P0.
# Invariant 22 (line 9483) and invariant 23 (line 9484).
# Section 96.6 row S18 (L8835) / D78 (L10172): a platform-rebuild
#   product is gated on its recorded equivalent identity instead.
# Composed as the FIRST job of deploy-production. It has no `if:`, no `needs:`
# and no path filter, so it can never report a skipped conclusion.
on:
  workflow_call:
    inputs:
      product:
        required: true
        type: string
      identity_mode:
        required: true
        type: string
      requested_identity:
        required: true
        type: string
      records_repo:
        required: true
        type: string
      control_plane_ref:
        required: true
        type: string
      image_repo:
        required: false
        type: string
        default: ''
      records_ref:
        required: false
        type: string
        default: main
    secrets:
      control_plane_read_token:
        required: true
      records_read_token:
        required: true
permissions:
  contents: read
  packages: read
jobs:
  digest-gate:
    runs-on: ubuntu-latest
    steps:
      - name: Guard the read credentials
        shell: bash
        env:
          CP_TOKEN: ${{ secrets.control_plane_read_token }}
          RC_TOKEN: ${{ secrets.records_read_token }}
          RECORDS_REPO: ${{ inputs.records_repo }}
        run: |
          set -euo pipefail
          if [ -z "${CP_TOKEN}" ]; then echo "CONTROL_PLANE_ACCESS_UNAVAILABLE"; exit 1; fi
          if [ -z "${RC_TOKEN}" ]; then echo "RECORDS_ACCESS_UNAVAILABLE"; exit 1; fi
          if [ -z "${RECORDS_REPO}" ]; then echo "RECORDS_REPO_UNDECLARED"; exit 1; fi
          echo "GATE_INPUTS_PRESENT"
      - name: Checkout the control-plane build surface at the pinned ref
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          repository: ${{ github.repository_owner }}/control-plane
          ref: ${{ inputs.control_plane_ref }}
          token: ${{ secrets.control_plane_read_token }}
          path: control-plane
          sparse-checkout: tools/evidence
      - name: Checkout the records store
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          repository: ${{ inputs.records_repo }}
          ref: ${{ inputs.records_ref }}
          token: ${{ secrets.records_read_token }}
          path: records
          sparse-checkout: records/deployments
      - name: Assert the requested identity passed staging verification
        shell: bash
        env:
          PRODUCT: ${{ inputs.product }}
          IDENTITY_MODE: ${{ inputs.identity_mode }}
          REQUESTED_IDENTITY: ${{ inputs.requested_identity }}
        run: |
          set -euo pipefail
          bash control-plane/tools/evidence/assert-staging-verified-identity.sh \
            records "${PRODUCT}" "${IDENTITY_MODE}" "${REQUESTED_IDENTITY}" | tee gate-verdict.txt
          {
            echo "### Digest gate"
            echo ""
            echo '```'
            cat gate-verdict.txt
            echo '```'
          } >> "$GITHUB_STEP_SUMMARY"
      - name: Assert the artifact is resolvable, and never rebuild
        shell: bash
        env:
          IDENTITY_MODE: ${{ inputs.identity_mode }}
          IMAGE_REPO: ${{ inputs.image_repo }}
          REQUESTED_IDENTITY: ${{ inputs.requested_identity }}
          REGISTRY_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          set -euo pipefail
          case "${IDENTITY_MODE}" in
            digest)
              if [ -z "${IMAGE_REPO}" ]; then echo "IMAGE_REPO_UNDECLARED"; exit 1; fi
              printf '%s' "${REGISTRY_TOKEN}" \
                | docker login ghcr.io -u "${GITHUB_ACTOR}" --password-stdin
              bash control-plane/tools/evidence/assert-artifact-published.sh \
                "${IMAGE_REPO}" "${REQUESTED_IDENTITY}"
              ;;
            platform-rebuild)
              echo "ARTIFACT_CHECK_NOT_APPLICABLE mode=platform-rebuild spec=Section-96.6-S18"
              ;;
            *)
              echo "IDENTITY_MODE_UNDECLARED mode=${IDENTITY_MODE}"
              exit 1
              ;;
          esac
      - name: Gate verdict
        shell: bash
        run: |
          set -euo pipefail
          grep -q '^DIGEST_INVARIANT_OK ' gate-verdict.txt || {
            echo "DIGEST_INVARIANT_VIOLATION verdict-file-did-not-confirm"
            exit 1
          }
          echo "PRODUCTION_DEPLOY_PERMITTED"
EOF
git add .github/workflows/digest-gate.yml
git commit -m "L2-T201: reusable production digest gate (Section 32 invariant, in code)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | File exists | `test -f .github/workflows/digest-gate.yml; echo $?` | exactly `0` |
| A2 | Reusable only | `grep -c '^  workflow_call:$' .github/workflows/digest-gate.yml` | exactly `1` |
| A3 | Exactly one job, named `digest-gate` | `awk '/^jobs:$/{f=1;next} f&&/^  [a-z]/{print}' .github/workflows/digest-gate.yml \| tr -d ' :'` | exactly `digest-gate` |
| A4 | No `if:`, no path filter, no `needs:` | `grep -cE '^\s+(if:|paths:|paths-ignore:|needs:)' .github/workflows/digest-gate.yml` | exactly `0` |
| A5 | Only the one verified Action SHA | `grep -oE 'uses: [^ ]+' .github/workflows/digest-gate.yml \| sort -u \| wc -l \| tr -d ' '` | exactly `1` |
| A6 | It calls the gate script, not an inline copy | `grep -c 'assert-staging-verified-identity.sh' .github/workflows/digest-gate.yml` | exactly `1` |
| A7 | Both credentials fail closed | `grep -cE '(CONTROL_PLANE|RECORDS)_ACCESS_UNAVAILABLE' .github/workflows/digest-gate.yml` | exactly `2` |
| A8 | The workflow contains no build or push | `grep -cE '(buildx build|docker build|--push)' .github/workflows/digest-gate.yml` | exactly `0` |
| A9 | Least-privilege permissions | `grep -A2 '^permissions:$' .github/workflows/digest-gate.yml \| grep -c 'write'` | exactly `0` |
| A10 | Final verdict string present | `grep -c 'PRODUCTION_DEPLOY_PERMITTED' .github/workflows/digest-gate.yml` | exactly `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(awk '/^jobs:$/{f=1;next} f&&/^  [a-z]/{print}' .github/workflows/digest-gate.yml | tr -d ' :')" = "digest-gate" \
 && test "$(grep -cE '^\s+(if:|paths:|paths-ignore:|needs:)' .github/workflows/digest-gate.yml)" = "0" \
 && test "$(grep -oE 'uses: [^ ]+' .github/workflows/digest-gate.yml | sort -u | wc -l | tr -d ' ')" = "1" \
 && test "$(grep -cE '(buildx build|docker build|--push)' .github/workflows/digest-gate.yml)" = "0" \
 && test "$(grep -cE '(CONTROL_PLANE|RECORDS)_ACCESS_UNAVAILABLE' .github/workflows/digest-gate.yml)" = "2" \
 && test "$(grep -c 'PRODUCTION_DEPLOY_PERMITTED' .github/workflows/digest-gate.yml)" = "1" \
 && echo "L2-T201 OK" || echo "L2-T201 FAIL"
```
Correct output: the single line `L2-T201 OK`.

**STOP rule:** do not add a `workflow_dispatch` trigger to this file. A gate a human can run in isolation is a gate that reports green without a deploy behind it. If a standalone sweep is needed, that is `verify-digest-chain` (§99.2 named tools, line 9214), which belongs to subsystem F in a later phase — STOP under charter rule `S4` rather than adding it here.

---

### L2-T202 — Control-plane self-test workflow

**Size:** S  **Depends on:** `L2-T528`

**Creates:** `.github/workflows/digest-invariant-selftest.yml`

The gate is only trustworthy if a change to it that weakens it fails the control plane's own CI.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > .github/workflows/digest-invariant-selftest.yml <<'EOF'
name: digest-invariant-selftest
# Runs the Lane 2 negative-test harness on every pull request into integration.
# Section 32 (lines 2803-2828) is the rule; tools/evidence/test/run-all.sh is the
# proof that the rule still refuses. A weakened gate fails here first.
# No `if:`, no path filter: this job runs on every pull request, and "no work was
# needed" is not a state it can be in (Section 33.2, lines 2854-2869).
on:
  pull_request:
    branches: [integration]
permissions:
  contents: read
jobs:
  digest-invariant-selftest:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - name: Run the digest-invariant suite
        shell: bash
        run: |
          set -euo pipefail
          bash tools/evidence/test/run-all.sh | tee suite.txt
          tail -1 suite.txt | grep -qx 'SUITE_PASS'
      - name: Assert the gate has no bypass
        shell: bash
        run: |
          set -euo pipefail
          BAD="$(grep -rniE '(force|skip|bypass|override|allow_unverified|WARN_ONLY)' \
                 tools/evidence/assert-staging-verified-identity.sh || true)"
          if [ -n "${BAD}" ]; then
            echo "GATE_BYPASS_SUSPECTED"
            printf '%s\n' "${BAD}"
            exit 1
          fi
          echo "GATE_HAS_NO_BYPASS"
EOF
git add .github/workflows/digest-invariant-selftest.yml
git commit -m "L2-T202: control-plane self-test for the digest invariant"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | File exists | `test -f .github/workflows/digest-invariant-selftest.yml; echo $?` | exactly `0` |
| A2 | Triggered on pull requests into `integration` | `grep -c 'branches: \[integration\]' .github/workflows/digest-invariant-selftest.yml` | exactly `1` |
| A3 | No `if:`, no path filter | `grep -cE '^\s+(if:|paths:|paths-ignore:)' .github/workflows/digest-invariant-selftest.yml` | exactly `0` |
| A4 | Asserts the exact suite verdict | `grep -c "grep -qx 'SUITE_PASS'" .github/workflows/digest-invariant-selftest.yml` | exactly `1` |
| A5 | Bypass scan present | `grep -c 'GATE_BYPASS_SUSPECTED' .github/workflows/digest-invariant-selftest.yml` | exactly `1` |
| A6 | The bypass scan does not fire on the current gate | `bash -c "grep -rniE '(force|skip|bypass|override|allow_unverified|WARN_ONLY)' tools/evidence/assert-staging-verified-identity.sh \| wc -l \| tr -d ' '"` | exactly `0` |
| A7 | `required-checks.yaml` untouched | `git diff --name-only integration...HEAD \| grep -c 'required-checks.yaml'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(grep -cE '^\s+(if:|paths:|paths-ignore:)' .github/workflows/digest-invariant-selftest.yml)" = "0" \
 && test "$(grep -c "grep -qx 'SUITE_PASS'" .github/workflows/digest-invariant-selftest.yml)" = "1" \
 && test "$(grep -rniE '(force|skip|bypass|override|allow_unverified|WARN_ONLY)' tools/evidence/assert-staging-verified-identity.sh | wc -l | tr -d ' ')" = "0" \
 && test "$(git diff --name-only integration...HEAD | grep -c 'required-checks.yaml')" = "0" \
 && echo "L2-T202 OK" || echo "L2-T202 FAIL"
```
Correct output: the single line `L2-T202 OK`.

**STOP rule:** do **not** add `digest-invariant-selftest` to `templates/workflows/required-checks.yaml`. That file was frozen by `L2-T003`, whose STOP rule is explicit. Whether this context becomes a required check is **DECISION REQUIRED D-L2-08** below; file it, do not decide it.

---

### L2-T400 — The artifact registry conventions

**Size:** M  **Depends on:** `L2-T521`, `L2-T522`

**Creates:** `templates/workflows/artifact-conventions.yaml`

Every value below is either transcribed from the spec or fixed by an earlier task in this phase. The executor types the file; the executor chooses nothing.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > templates/workflows/artifact-conventions.yaml <<'EOF'
# Lane 2 published interface: artifact registry and identity conventions.
# Spec: MultiProduct_MasterSpec_v4.0.md
#   Section 32   lines 2803-2828  the eleven questions and the digest invariant
#   Section 33.4 lines 2887-2912  immutable artifact, digest recorded, same digest to production
#   Section 46.2 lines 4132-4149  registry outage: never rebuild
#   Section 48.3 lines 4317-4320  SBOM beside the digest
#   Section 96.6 L8835        intake row S18, platform-rebuild deployment
#   D78          L10172       the S18 equivalence
#   invariant 22 line 9483, invariant 23 line 9484
# CONSUMERS: Lane 3 create-product (templates), Lane 5 (registry and environment
# configuration), Lane 4 (record readers). Consumers copy from this file and
# never invent a value.
schema: artifact-conventions/v1

registry:
  host: ghcr.io
  # product.yaml deployment.artifact_registry, printed at spec line 1377
  repository_source_field: deployment.artifact_registry
  repository_pattern: ghcr.io/<org>/<product>
  deploy_reference_form: <repository>@<digest>
  tags_are_identity: false
  tag_policy: >-
    A tag may be applied for human navigation only. No workflow in this estate
    resolves a deploy target from a tag; every deploy target is a digest, because
    a tag is movable and a movable reference is not an identity (Section 33.2,
    lines 2854-2869, states the same rule for reusable-workflow tags).
  build_tag_applied: <commit_sha>

identity:
  modes:
    - digest
    - platform-rebuild
  digest:
    regex: ^sha256:[0-9a-f]{64}$
    source: docker buildx build --metadata-file, key containerimage.digest
    spec: Section 32 item 5, lines 2803-2828
  platform-rebuild:
    regex: ^platform-rebuild:v1:[0-9a-f]{64}$
    spec: Section 96.6 row S18 L8835; D78 L10172
    composition: >-
      sha256 of the canonical identity block. The block is one
      'commit=<40 hex>' line, followed by the LC_ALL=C-sorted set of
      'lockfile <path>=<sha256>' and 'buildconfig <path>=<sha256>' lines,
      each LF terminated. Both path sets are required inputs with no default.
    producer: tools/evidence/compute-platform-identity.sh
    applies_when: >-
      The product deploys by git-push to a PaaS that rebuilds per environment,
      so staging and production are separate platform builds and the
      byte-identical-digest invariant is structurally unsatisfiable there.
    remediation: >-
      Replatforming to the container pipeline is the onboarding step wherever
      the product's classification.reliability_criticality demands the true
      digest chain (D78). Remaining on a platform-rebuild host is a dated,
      recorded state - an accepted risk or a declared profile - never an
      implicit one (Section 32, line 2823).

sbom:
  spec: Section 48.3, lines 4317-4320
  emission_rule: same pipeline step as the digest, same storage discipline, same immutability
  digest_mode:
    producer: docker buildx build --sbom=true
    storage: registry attestation against the same digest
    retrieval: docker buildx imagetools inspect <repo>@<digest> --format '{{ json .SBOM }}'
  platform_rebuild_mode:
    producer: the product's own build
    input: sbom_file
    absent_input_behaviour: fail the build with SBOM_UNDECLARED
  assertion: tools/evidence/assert-sbom-beside-digest.sh

immutability:
  rebuild_for_production: forbidden
  rebuild_on_registry_outage: forbidden
  registry_outage_action: wait for the registry
  spec: invariant 22 line 9483; invariant 23 line 9484; Section 46.2 lines 4132-4149
  gate: tools/evidence/assert-staging-verified-identity.sh
  gate_semantics: >-
    A production deploy is permitted only where a deployment record exists for
    that product carrying staging_verified true, smoke_result pass, and the
    requested identity. Existence, not recency - which is what keeps the
    Section 27.2 rollback path open without weakening the gate.

verdict_strings:
  ok: DIGEST_INVARIANT_OK
  violation: DIGEST_INVARIANT_VIOLATION
  no_record: NO_STAGING_VERIFIED_RECORD
  mode_undeclared: IDENTITY_MODE_UNDECLARED
  format_invalid: IDENTITY_FORMAT_INVALID
  store_absent: RECORDS_STORE_ABSENT
  record_unparseable: RECORD_UNPARSEABLE
  record_filename_invalid: RECORD_FILENAME_INVALID
  artifact_published: ARTIFACT_PUBLISHED
  artifact_unresolvable: ARTIFACT_NOT_RESOLVABLE
  never_rebuild: DO_NOT_REBUILD
  sbom_present: SBOM_PRESENT
  sbom_missing: SBOM_MISSING
  sbom_undeclared: SBOM_UNDECLARED
  digest_recorded: DIGEST_RECORDED
  deploy_permitted: PRODUCTION_DEPLOY_PERMITTED
  control_plane_unavailable: CONTROL_PLANE_ACCESS_UNAVAILABLE
  records_unavailable: RECORDS_ACCESS_UNAVAILABLE
EOF
git add templates/workflows/artifact-conventions.yaml
git commit -m "L2-T400: publish the artifact registry and identity conventions"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | File exists | `test -f templates/workflows/artifact-conventions.yaml; echo $?` | exactly `0` |
| A2 | Declares the schema line | `grep -c '^schema: artifact-conventions/v1$' templates/workflows/artifact-conventions.yaml` | exactly `1` |
| A3 | Exactly two identity modes | `awk '/^  modes:$/{f=1;next} f&&/^    - /{c++} f&&!/^    - /{exit} END{print c}' templates/workflows/artifact-conventions.yaml` | exactly `2` |
| A4 | Tags are explicitly not identity | `grep -c '^  tags_are_identity: false$' templates/workflows/artifact-conventions.yaml` | exactly `1` |
| A5 | Rebuild-on-outage forbidden | `grep -c '^  rebuild_on_registry_outage: forbidden$' templates/workflows/artifact-conventions.yaml` | exactly `1` |
| A6 | Every verdict string in the file is emitted by a Lane 2 script or workflow | see SELF-VERIFY | exactly `0` unmatched |
| A7 | `required-checks.yaml` untouched | `git diff --name-only integration...HEAD \| grep -c 'required-checks.yaml'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
UNMATCHED=0
for s in $(awk '/^verdict_strings:$/{f=1;next} f&&/^  [a-z_]+: /{print $2} f&&/^[a-z]/{exit}' templates/workflows/artifact-conventions.yaml); do
  grep -rq -- "$s" tools/evidence .github/workflows || { echo "UNEMITTED $s"; UNMATCHED=$((UNMATCHED+1)); }
done
test "$UNMATCHED" = "0" \
 && test "$(grep -c '^schema: artifact-conventions/v1$' templates/workflows/artifact-conventions.yaml)" = "1" \
 && test "$(grep -c '^  rebuild_on_registry_outage: forbidden$' templates/workflows/artifact-conventions.yaml)" = "1" \
 && test "$(git diff --name-only integration...HEAD | grep -c 'required-checks.yaml')" = "0" \
 && echo "L2-T400 OK" || echo "L2-T400 FAIL"
```
Correct output: the single line `L2-T400 OK`.

**STOP rule:** if the SELF-VERIFY prints an `UNEMITTED <string>` line, do not delete the string from this file to make the check pass. A convention naming a verdict nothing emits is a lie in a published cross-lane interface. Fix the emitting script, or STOP and file the blocker with STOP RULE `S4`.

---

### L2-T401 — Per-product build template, container products

**Size:** M  **Depends on:** `L2-T200`, `L2-T400`

**Creates:** `templates/workflows/build.yml`

Section 33.2 (lines 2854–2869) lists `build.yml` among the required per-product workflows, all *"generated from templates at product creation ... and consume reusable workflows by pinned tag"*. The placeholders below are substituted by Lane 3's `create-product`; Lane 2 supplies the template and never fills them in.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > templates/workflows/build.yml <<'EOF'
# GENERATED AT PRODUCT CREATION FROM templates/workflows/build.yml
# Do not hand-edit in the product repository. Section 33.2, lines 2854-2869.
#
# Placeholders substituted by create-product (Lane 3, tools/provision/**):
#   {{ORG}}                organisation login
#   {{PRODUCT}}            product id from product.yaml
#   {{IMAGE_REPO}}         product.yaml deployment.artifact_registry (spec line 1377)
#   {{WORKFLOWS_TAG}}      the pinned reusable-workflow tag, e.g. workflows/v1
#
# Consumption is by PINNED TAG, never by branch (Section 33.3, lines 2870-2886).
# The tag is a pin only because the control plane carries a tag ruleset blocking
# updates and deletions on workflows/* with an empty bypass-actor list
# (Section 33.2). That ruleset is Lane 5's; this template depends on it.
name: build
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  packages: write
jobs:
  build:
    uses: {{ORG}}/control-plane/.github/workflows/build.yml@{{WORKFLOWS_TAG}}
    with:
      product: {{PRODUCT}}
      identity_mode: digest
      image_repo: {{IMAGE_REPO}}
      dockerfile: Dockerfile
      build_context: .
      control_plane_ref: {{WORKFLOWS_TAG}}
    secrets:
      control_plane_read_token: ${{ secrets.CONTROL_PLANE_READ_TOKEN }}
EOF
git add templates/workflows/build.yml
git commit -m "L2-T401: per-product build template, container products"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | File exists | `test -f templates/workflows/build.yml; echo $?` | exactly `0` |
| A2 | Consumes by pinned tag, never a branch | `grep -cE 'uses: {{ORG}}/control-plane/\.github/workflows/build\.yml@{{WORKFLOWS_TAG}}$' templates/workflows/build.yml` | exactly `1` |
| A3 | No `@main`, `@master` or floating ref | `grep -cE '@(main|master|HEAD)$' templates/workflows/build.yml` | exactly `0` |
| A4 | Identity mode is `digest` | `grep -c '^      identity_mode: digest$' templates/workflows/build.yml` | exactly `1` |
| A5 | Exactly one job, id `build` | `awk '/^jobs:$/{f=1;next} f&&/^  [a-z]/{print}' templates/workflows/build.yml \| tr -d ' :'` | exactly `build` |
| A6 | No `if:`, no path filter | `grep -cE '^\s+(if:|paths:|paths-ignore:)' templates/workflows/build.yml` | exactly `0` |
| A7 | Every placeholder is documented in the header | see SELF-VERIFY | exactly `0` undocumented |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
UND=0
for p in $(grep -oE '__[A-Z_]+__' templates/workflows/build.yml | sort -u); do
  test "$(grep -c "#   $p" templates/workflows/build.yml)" -ge 1 || { echo "UNDOCUMENTED $p"; UND=$((UND+1)); }
done
test "$UND" = "0" \
 && test "$(awk '/^jobs:$/{f=1;next} f&&/^  [a-z]/{print}' templates/workflows/build.yml | tr -d ' :')" = "build" \
 && test "$(grep -cE '@(main|master|HEAD)$' templates/workflows/build.yml)" = "0" \
 && test "$(grep -c '^      identity_mode: digest$' templates/workflows/build.yml)" = "1" \
 && echo "L2-T401 OK" || echo "L2-T401 FAIL"
```
Correct output: the single line `L2-T401 OK`.

**STOP rule:** do not substitute a placeholder with a real organisation, product or tag value. Templates are consumed by Lane 3's `create-product` (`PARTITION.md` line 19); a template carrying a real value is a template that has already been used once and will be wrong for every other product. STOP under charter rule `S4`.

---

### L2-T402 — Per-product build template, S18 platform-rebuild products

**Size:** M  **Depends on:** `L2-T200`, `L2-T400`, `L2-T522`

**Creates:** `templates/workflows/build-platform-rebuild.yml`

Section 96.6 row S18 (L8835) describes a product whose staging and production are separate platform builds. D78 (L10172) names the equivalent identity and names replatforming as the onboarding remedy. This template records that identity so the chain of Section 32 still closes on evidence rather than on nothing.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > templates/workflows/build-platform-rebuild.yml <<'EOF'
# GENERATED AT PRODUCT CREATION FROM templates/workflows/build-platform-rebuild.yml
# For an S18 platform-rebuild product only (Section 96.6 L8835; D78 L10172):
# the product deploys by git-push to a PaaS that rebuilds per environment, so the
# byte-identical-digest invariant of Section 32 is structurally unsatisfiable and
# the recorded identity - pinned commit, lockfile, build configuration - stands in
# for the digest throughout the evidence chain.
#
# Remaining on a platform-rebuild host is a dated, recorded state - an accepted
# risk or a declared profile - never an implicit one (Section 32, line 2823).
# Replatforming to the container pipeline is the onboarding step wherever the
# product's classification.reliability_criticality demands the true digest chain.
#
# Placeholders substituted by create-product (Lane 3, tools/provision/**):
#   {{ORG}}                  organisation login
#   {{PRODUCT}}              product id from product.yaml
#   {{WORKFLOWS_TAG}}        the pinned reusable-workflow tag, e.g. workflows/v1
#   {{LOCKFILE_PATHS}}       comma-separated, repo-relative; REQUIRED, no default
#   {{BUILD_CONFIG_PATHS}}   comma-separated, repo-relative; REQUIRED, no default
#   {{SBOM_FILE}}            repo-relative path to the SBOM this build produced; REQUIRED
name: build
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  packages: read
jobs:
  build:
    uses: {{ORG}}/control-plane/.github/workflows/build.yml@{{WORKFLOWS_TAG}}
    with:
      product: {{PRODUCT}}
      identity_mode: platform-rebuild
      lockfile_paths: {{LOCKFILE_PATHS}}
      build_config_paths: {{BUILD_CONFIG_PATHS}}
      sbom_file: {{SBOM_FILE}}
      control_plane_ref: {{WORKFLOWS_TAG}}
    secrets:
      control_plane_read_token: ${{ secrets.CONTROL_PLANE_READ_TOKEN }}
EOF
git add templates/workflows/build-platform-rebuild.yml
git commit -m "L2-T402: per-product build template for S18 platform-rebuild products (D78)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | File exists | `test -f templates/workflows/build-platform-rebuild.yml; echo $?` | exactly `0` |
| A2 | Identity mode is `platform-rebuild` | `grep -c '^      identity_mode: platform-rebuild$' templates/workflows/build-platform-rebuild.yml` | exactly `1` |
| A3 | Cites S18 and D78 by line | `grep -c 'Section 96.6 L8835; D78 L10172' templates/workflows/build-platform-rebuild.yml` | exactly `1` |
| A4 | Both path inputs present | `grep -cE '^      (lockfile_paths|build_config_paths): __' templates/workflows/build-platform-rebuild.yml` | exactly `2` |
| A5 | SBOM input present | `grep -c '^      sbom_file: {{SBOM_FILE}}$' templates/workflows/build-platform-rebuild.yml` | exactly `1` |
| A6 | No `image_repo` — there is no container | `grep -c 'image_repo' templates/workflows/build-platform-rebuild.yml` | exactly `0` |
| A7 | Pinned tag, no floating ref | `grep -cE '@(main|master|HEAD)$' templates/workflows/build-platform-rebuild.yml` | exactly `0` |
| A8 | States the replatforming remedy | `grep -c 'Replatforming to the container pipeline' templates/workflows/build-platform-rebuild.yml` | exactly `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(grep -c '^      identity_mode: platform-rebuild$' templates/workflows/build-platform-rebuild.yml)" = "1" \
 && test "$(grep -cE '^      (lockfile_paths|build_config_paths): __' templates/workflows/build-platform-rebuild.yml)" = "2" \
 && test "$(grep -c 'image_repo' templates/workflows/build-platform-rebuild.yml)" = "0" \
 && test "$(grep -c 'Replatforming to the container pipeline' templates/workflows/build-platform-rebuild.yml)" = "1" \
 && test "$(grep -cE '@(main|master|HEAD)$' templates/workflows/build-platform-rebuild.yml)" = "0" \
 && echo "L2-T402 OK" || echo "L2-T402 FAIL"
```
Correct output: the single line `L2-T402 OK`.

**STOP rule:** if a product would need this template but cannot declare a lockfile path or a build-configuration path, STOP. An S18 identity computed from fewer than all three inputs is not the identity D78 specifies, and a weaker identity presented as the equivalent evidence is worse than none. File the blocker with STOP RULE `S4`, quoting spec L8835.

---

### L2-T403 — The canonical digest-gate call fragment

**Size:** S  **Depends on:** `L2-T201`

**Creates:** `templates/workflows/digest-gate.call.yml`

The `deploy-production` workflow belongs to a later Lane 2 phase. This file is the exact fragment that phase composes as its **first job**, so the gate is wired identically for every product and no phase reimplements the invariant.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > templates/workflows/digest-gate.call.yml <<'EOF'
# CANONICAL DIGEST-GATE CALL FRAGMENT — Lane 2 published interface.
#
# The deploy-production workflow composes this as its FIRST job. Every other job
# in that workflow declares `needs: digest-gate`, so no deploy step can run
# before the Section 32 invariant has been proved for the requested identity.
#
# Section 32, line 2823:
#   "CI rejects any production deployment where the requested digest differs
#    from the digest that passed staging verification."
# Section 33.4, lines 2887-2912: artifact immutability is P0.
# Invariant 22 (line 9483), invariant 23 (line 9484).
#
# Placeholders substituted by create-product (Lane 3, tools/provision/**):
#   {{ORG}}                organisation login
#   {{PRODUCT}}            product id from product.yaml
#   {{IMAGE_REPO}}         product.yaml deployment.artifact_registry (spec line 1377)
#   {{IDENTITY_MODE}}      digest | platform-rebuild
#   {{RECORDS_REPO}}       the records repository, per PARTITION.md line 8
#   {{WORKFLOWS_TAG}}      the pinned reusable-workflow tag, e.g. workflows/v1
#
# This fragment is not a workflow on its own. It is copied verbatim under the
# `jobs:` key of deploy-production.yml.

  digest-gate:
    uses: {{ORG}}/control-plane/.github/workflows/digest-gate.yml@{{WORKFLOWS_TAG}}
    with:
      product: {{PRODUCT}}
      identity_mode: {{IDENTITY_MODE}}
      requested_identity: ${{ inputs.requested_identity }}
      image_repo: {{IMAGE_REPO}}
      records_repo: {{RECORDS_REPO}}
      records_ref: main
      control_plane_ref: {{WORKFLOWS_TAG}}
    secrets:
      control_plane_read_token: ${{ secrets.CONTROL_PLANE_READ_TOKEN }}
      records_read_token: ${{ secrets.RECORDS_READ_TOKEN }}
EOF
git add templates/workflows/digest-gate.call.yml
git commit -m "L2-T403: canonical digest-gate call fragment for deploy-production"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | File exists | `test -f templates/workflows/digest-gate.call.yml; echo $?` | exactly `0` |
| A2 | Job id is `digest-gate` | `grep -c '^  digest-gate:$' templates/workflows/digest-gate.call.yml` | exactly `1` |
| A3 | Pinned-tag consumption | `grep -cE 'digest-gate\.yml@{{WORKFLOWS_TAG}}$' templates/workflows/digest-gate.call.yml` | exactly `1` |
| A4 | Both secrets passed | `grep -cE '^      (control_plane_read_token|records_read_token):' templates/workflows/digest-gate.call.yml` | exactly `2` |
| A5 | Quotes the invariant verbatim | `grep -c 'CI rejects any production deployment where the requested digest differs' templates/workflows/digest-gate.call.yml` | exactly `1` |
| A6 | States the `needs:` composition rule | `grep -c 'needs: digest-gate' templates/workflows/digest-gate.call.yml` | exactly `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test "$(grep -c '^  digest-gate:$' templates/workflows/digest-gate.call.yml)" = "1" \
 && test "$(grep -cE 'digest-gate\.yml@{{WORKFLOWS_TAG}}$' templates/workflows/digest-gate.call.yml)" = "1" \
 && test "$(grep -cE '^      (control_plane_read_token|records_read_token):' templates/workflows/digest-gate.call.yml)" = "2" \
 && test "$(grep -c 'needs: digest-gate' templates/workflows/digest-gate.call.yml)" = "1" \
 && echo "L2-T403 OK" || echo "L2-T403 FAIL"
```
Correct output: the single line `L2-T403 OK`.

**STOP rule:** do not create `templates/workflows/deploy-production.yml` in this phase. That file belongs to the later Lane 2 phase that implements Section 34 and the workflow-identity gate of Section 27.2, and is additionally blocked on charter decisions D-L2-03 and D-L2-05. STOP under charter rule `S4` if tempted.

---

### L2-T404 — File the required-context composition blocker

**Size:** S  **Depends on:** `L2-T401`, `L2-T402`

**Creates:** no files. Files one blocker issue.

The required-status-check registry frozen by `L2-T003` lists plain context names — `build`, `artifact-digest-recorded`, `sbom-emitted`. A job that calls a reusable workflow does not emit a plain context name; GitHub composes it as `<caller job> / <called job>`, so `L2-T401`'s template emits `build / artifact`, not `build`. That mismatch is a cross-lane interface question, not an executor's choice. This task's whole output is the blocker.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
gh issue create \
  --title "BLOCKER L2-T404: reusable-workflow check names do not match the frozen required-checks registry" \
  --label "blocker,lane-2" \
  --body "$(cat <<'EOF'
LANE: L2 Pipeline & Evidence
TASK: L2-T404
STOP RULE TRIGGERED: S4
DECISION REQUIRED: D-L2-07

WHAT I WAS DOING:
Authoring templates/workflows/build.yml (L2-T401) and
templates/workflows/build-platform-rebuild.yml (L2-T402), which consume the
control-plane reusable workflow .github/workflows/build.yml by pinned tag as
Section 33.2 (lines 2854-2869) requires.

WHAT HAPPENED:
templates/workflows/required-checks.yaml, frozen by L2-T003, lists the plain
context names `build` (phase_4), `artifact-digest-recorded` and `sbom-emitted`
(phase_6). GitHub composes the check-run name of a reusable-workflow call as
`<caller job id> / <called job id>`. The template's caller job id is `build` and
the reusable workflow's job id is `artifact`, so the emitted context is
`build / artifact`. None of the three frozen names is emitted by any job in
this estate.

WHY THIS MATTERS:
Section 33.2 states that a required check name no workflow emits blocks every
pull request indefinitely, and that a list which silently stays empty is a gate
that reads armed and is not. Section 98.2 Phase 1 (line 9024) makes each phase's
completion check name the contexts it adds. Lane 5 copies context names from
required-checks.yaml into branch protection and Lane 3 compares them in the
Section 53.1 template comparison, so a mismatch desynchronises three lanes.

WHAT I NEED TO PROCEED:
One of:
  (a) amend templates/workflows/required-checks.yaml to the composed names
      actually emitted, and state the composition rule so future templates
      stay consistent; or
  (b) direct that required-context jobs must be normal jobs in the product
      workflow rather than reusable-workflow calls, and state how those jobs
      obtain the control-plane build surface without a reusable-workflow call.

I HAVE NOT: guessed a value, written outside owned paths, edited contracts/**,
            edited templates/workflows/required-checks.yaml, resolved a
            foreign-path conflict, or continued past this point.

SPEC CITATION:
MultiProduct_MasterSpec_v4.0.md lines 2854-2869, Section 33.2
MultiProduct_MasterSpec_v4.0.md line 9024, Section 98.2 Phase 1
EOF
)"
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | The issue exists | `gh issue list --label blocker --search "L2-T404" --json title --jq '.[0].title'` | begins `BLOCKER L2-T404:` |
| A2 | No file was created or edited by this task | `git status --porcelain` | empty output |
| A3 | `required-checks.yaml` still untouched on this branch | `git diff --name-only integration...HEAD \| grep -c 'required-checks.yaml'` | exactly `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
test -z "$(git status --porcelain)" \
 && test "$(git diff --name-only integration...HEAD | grep -c 'required-checks.yaml')" = "0" \
 && gh issue list --label blocker --search "L2-T404" --json title --jq '.[0].title' | grep -q '^BLOCKER L2-T404:' \
 && echo "L2-T404 OK" || echo "L2-T404 FAIL"
```
Correct output: the single line `L2-T404 OK`.

**STOP rule:** this task is the STOP. Do not resolve D-L2-07 yourself in either direction, and specifically do not edit `templates/workflows/required-checks.yaml`. Continue to `L2-T405`; the phase merges with the blocker open, because every artifact in it is correct under either resolution.

---

### L2-T405 — Phase gate: prove everything, rebase, open the PR

**Size:** S  **Depends on:** every task above

**Creates/edits:** no files. Publishes the branch.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"

# 1. Every self-verify, in one pass.
bash tools/evidence/test/run-all.sh | tail -1

# 2. Path ownership — PARTITION.md rule 1.
git diff --name-only integration...HEAD \
  | grep -vE '^(\.github/workflows/|templates/workflows/|tools/evidence/)' \
  | tee /tmp/l2-foreign.txt
test ! -s /tmp/l2-foreign.txt || { echo "FOREIGN PATHS TOUCHED — STOP"; exit 1; }

# 3. The frozen registry is untouched.
git diff --name-only integration...HEAD | grep -c 'required-checks.yaml'

# 4. No unpinned Action anywhere this phase added.
grep -rhoE 'uses: [^ ]+' .github/workflows | sort -u

# 5. Preflight from the charter.
bash tools/evidence/preflight.sh | tail -1

# 6. Rebase and publish.
git fetch origin
git rebase origin/integration
bash tools/evidence/test/run-all.sh | tail -1
git push -u origin lane/2/phase2-digest-invariant
gh pr create \
  --base integration \
  --head lane/2/phase2-digest-invariant \
  --title "L2 phase2: the digest invariant, the artifact chain, SBOM and the S18 equivalence" \
  --body "Lane 2 (Pipeline & Evidence), phase 2. Tasks L2-T520..L2-T528, L2-T200..L2-T202, L2-T400..L2-T404.

Implements:
- Section 32 (lines 2803-2828) the digest invariant, in code, fail-closed
- Section 33.4 (lines 2887-2912) immutable artifact, digest recorded
- Section 48.3 (lines 4317-4320) SBOM emitted beside the digest, same step
- Section 46.2 (lines 4132-4149) / invariant 23 never rebuild on registry outage
- Section 96.6 row S18 (L8835) / D78 (L10172) platform-rebuild equivalence

Owned paths only: .github/workflows/**, templates/workflows/**, tools/evidence/**.
templates/workflows/required-checks.yaml is unmodified (frozen by L2-T003).
OPEN BLOCKER: D-L2-07 (see issue BLOCKER L2-T404) — required-context name composition."
```

**Acceptance criteria**

| # | Criterion | Proving command | Correct output |
|---|---|---|---|
| A1 | Suite passes after the rebase | `bash tools/evidence/test/run-all.sh \| tail -1` | exactly `SUITE_PASS` |
| A2 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | exactly `0` |
| A3 | Frozen registry untouched | `git diff --name-only origin/integration...HEAD \| grep -c 'required-checks.yaml'` | exactly `0` |
| A4 | Exactly one distinct Action, SHA-pinned | `grep -rhoE 'uses: [^ ]+' .github/workflows \| sort -u \| wc -l \| tr -d ' '` | exactly `1` |
| A5 | Charter preflight passes | `bash tools/evidence/preflight.sh \| tail -1` | exactly `PREFLIGHT_PASS` |
| A6 | Branch is a descendant of `integration` | `git merge-base --is-ancestor origin/integration HEAD; echo $?` | exactly `0` |
| A7 | PR is open against `integration` | `gh pr view --json baseRefName --jq .baseRefName` | exactly `integration` |
| A8 | All 17 phase files present | see SELF-VERIFY | exactly `MISSING=0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
MISSING=0
for f in \
  tools/evidence/lib/record-read.sh \
  tools/evidence/lib/identity.sh \
  tools/evidence/compute-platform-identity.sh \
  tools/evidence/assert-staging-verified-identity.sh \
  tools/evidence/assert-artifact-published.sh \
  tools/evidence/assert-sbom-beside-digest.sh \
  tools/evidence/build-artifact.sh \
  tools/evidence/test/stub/docker \
  tools/evidence/test/run-all.sh \
  .github/workflows/build.yml \
  .github/workflows/digest-gate.yml \
  .github/workflows/digest-invariant-selftest.yml \
  templates/workflows/artifact-conventions.yaml \
  templates/workflows/build.yml \
  templates/workflows/build-platform-rebuild.yml \
  templates/workflows/digest-gate.call.yml ; do
  test -f "$f" || { echo "MISSING $f"; MISSING=$((MISSING+1)); }
done
test "$(find tools/evidence/test/fixtures -name '*.yaml' | wc -l | tr -d ' ')" = "5" || MISSING=$((MISSING+1))
echo "MISSING=$MISSING"
test "$MISSING" = "0" \
 && test "$(bash tools/evidence/test/run-all.sh | tail -1)" = "SUITE_PASS" \
 && test "$(bash tools/evidence/preflight.sh | tail -1)" = "PREFLIGHT_PASS" \
 && test "$(git diff --name-only origin/integration...HEAD | grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)')" = "0" \
 && test "$(git diff --name-only origin/integration...HEAD | grep -c 'required-checks.yaml')" = "0" \
 && test "$(grep -rhoE 'uses: [^ ]+' .github/workflows | sort -u | wc -l | tr -d ' ')" = "1" \
 && test "$(gh pr view --json baseRefName --jq .baseRefName)" = "integration" \
 && echo "L2-T405 OK" || echo "L2-T405 FAIL"
```
Correct output: `MISSING=0` followed by the single line `L2-T405 OK`.

**STOP rule:** if `git rebase origin/integration` conflicts in any file outside the three owned trees, run `git rebase --abort` and STOP. Do not resolve it — a foreign-path conflict means path ownership was violated (`PARTITION.md` rule 1). File the blocker with STOP RULE `S3`. If A4 reports more than `1`, another phase added an Action; STOP under Rule P2-A and report it in the same blocker.

---

## 4. DECISION REQUIRED — HANDED TO L0

<!-- DECISIONS SUPERSEDED (FD-044): Decision IDs D-L2-07/08/09 in this file are superseded by L2-05-tasks.md §1. Do not reference these IDs in new work. -->

These continue the charter's numbering (`L2-00-charter.md` section 9 ends at D-L2-06). Lane 2 must not resolve any of them. File each as a Contract Change Request; never edit `contracts/**` and never edit another lane's tree.

### DECISION REQUIRED D-L2-07 — Required-context name composition for reusable-workflow calls

**Question.** `templates/workflows/required-checks.yaml`, frozen by `L2-T003`, lists the plain context names `build`, `artifact-digest-recorded` and `sbom-emitted`. GitHub composes a reusable-workflow call's check-run name as `<caller job id> / <called job id>`, so the templates of `L2-T401` and `L2-T402` emit `build / artifact` and nothing named `build`.

**Why L2 cannot decide.** Section 33.2 (lines 2854–2869) states that a required check name no workflow emits blocks every pull request indefinitely, and Section 98.2 Phase 1 (line 9024) makes each phase's completion check name the contexts it adds. Lane 5 copies these names into branch protection and Lane 3 compares them in the Section 53.1 template comparison (lines 4653–4689). Changing either side unilaterally desynchronises three lanes, and `L2-T003`'s STOP rule forbids Lane 2 from touching the registry.

**Options for L0.** (a) Amend `required-checks.yaml` to the composed names and record the composition rule. (b) Direct that required-context jobs be normal jobs in the product workflow, and state how such a job obtains the control-plane build surface without a reusable-workflow call.

**Blocks.** Adding the phase-4 and phase-6 pipeline contexts to branch protection; charter DoD-06 and DoD-09 for these three contexts. **Does not block** any file in this phase: every artifact here is correct under either resolution.

**Filed by.** `L2-T404`.

---

### DECISION REQUIRED D-L2-08 — Required-check status of `digest-invariant-selftest`

**Question.** `L2-T202` creates `.github/workflows/digest-invariant-selftest.yml`, which runs the negative-test harness proving the Section 32 gate still refuses. Should its context be a required status check on the control-plane repository?

**Why L2 cannot decide.** `L2-T003`'s STOP rule forbids Lane 2 adding a context name to the frozen registry, and Section 98.2 Phase 1 (line 9024) makes the required-check list a per-phase, explicitly named addition rather than something a lane grows on its own.

**Consequence of leaving it unrequired.** A pull request weakening `assert-staging-verified-identity.sh` fails the run but does not fail the merge gate. Given Section 32 line 2823 and invariant 22 (line 9483), leaving the estate's only mechanical proof of the digest invariant advisory is a material posture decision, and belongs to L0.

**Blocks.** Nothing in this phase. Raise before the first product reaches Section 98.2 Phase 6.

---

### DECISION REQUIRED D-L2-09 — The record field carrying an S18 platform-rebuild identity

**Question.** Section 32 (line 2823) says the S18 recorded identity *"stands in for the digest throughout this chain"*, so this phase writes it into the deployment record's `digest:` field, in the form `platform-rebuild:v1:<64 hex>` (fixed by `L2-T521`, published in `templates/workflows/artifact-conventions.yaml`). Does Lane 4's deployment-record schema accept that value in `digest:`, or does it require a separate field?

**Why L2 cannot decide.** Record shapes are Lane 4's (`schemas/records/**`, `PARTITION.md` line 20). Section 97.2 (lines 8843–8926) prints `digest: sha256:...` and does not print an S18 variant. If Lane 4's schema constrains `digest` to `^sha256:`, every S18 deployment record fails validation and the chain does not close for that product.

**Options for L0.** (a) Confirm `digest:` accepts both value forms and record the regex union in Lane 4's schema. (b) Direct a distinct field, in which case `tools/evidence/assert-staging-verified-identity.sh` reads that field in `platform-rebuild` mode — a one-line change to a task already written.

**Blocks.** Validation of S18 deployment records; charter DoD-14 for any S18 product. **Does not block** this phase.

---

## 5. REQUIREMENTS THIS PHASE PLACES ON OTHER LANES

Lane 2 states these; Lane 2 does not implement them (charter section 4.4).

| Requirement | Owner | Spec |
|---|---|---|
| Tag ruleset blocking updates and deletions on `workflows/*` with an **empty** bypass-actor list — without it `@workflows/vN` in the templates is not a pin | L5 | §33.2, lines 2854–2869; D89, line 10182 |
| `CONTROL_PLANE_READ_TOKEN` provisioned in every product repository, read-only, scoped to the control-plane repository | L5 | §40.1, lines 3644–3686 |
| `RECORDS_READ_TOKEN` provisioned in every product repository, read-only, scoped to the records repository | L5 | §40.1; §97.1, lines 8836–8842 |
| `packages: write` available to the product's build workflow on `ghcr.io`, and `packages: read` to the gate | L5 | §33.2 least-privilege paragraph |
| Deployment records carrying `staging_verified`, `smoke_result` and `digest` exactly as Section 97.2 prints them | L4 | §97.2, lines 8843–8926 |
| `create-product` substituting the placeholders of `templates/workflows/build.yml`, `build-platform-rebuild.yml` and `digest-gate.call.yml`, and choosing between the two build templates from the product's declared deployment shape | L3 | §19.1, lines 1826–1882; §33.2 |

---

## 6. WHAT THIS PHASE DELIBERATELY DOES NOT DO

Naming these prevents scope drift and prevents a collision with a sibling Lane 2 phase document.

| Not here | Where it belongs | Why |
|---|---|---|
| `deploy-staging.yml`, `deploy-production.yml`, `migrate.yml` | later L2 phase | §33.2 required workflows; blocked additionally on charter D-L2-03, D-L2-05 |
| The workflow-identity gate (approver ≠ deployer) | later L2 phase | §27.2, lines 2567–2576; charter E-4 |
| The actor gate as first step of privileged workflows | later L2 phase | §37.3, lines 3261–3268; charter E-5 |
| The Friday-freeze time gate | later L2 phase | §34.2, lines 2930–2935; charter E-7 |
| `verify-digest-chain`, the scheduled sweep and the §46.1 recovery gate | subsystem F, later L2 phase | §99.2 named tools, line 9214; §46.1, lines 4090–4131 |
| The eleven-question evidence assembler | subsystem F, later L2 phase | §32, lines 2803–2828; charter F-1 |
| Delta-gated security and licence scanning, slopsquat check, parity job | later L2 phase | §33.2; §48.2; charter E-6; parity blocked on charter D-L2-04 |
| Writing deployment records and events | later L2 phase | §97.2, §97.3; blocked on charter D-L2-03 |
| Branch protection, rulesets, environments, secret provisioning | L5 | `PARTITION.md` line 21 |
| The deployment-record schema | L4 | `PARTITION.md` line 20 |

---

## 7. READING ORDER FOR THE EXECUTOR

1. `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` — in full, first, always.
2. `C:/D_Drive/PS/MultiProduct/Code/implementation/lanes/L2-00-charter.md` sections 2, 6, 9, 10 — owned paths, merge train, decisions, STOP rules and the verbatim blocker template.
3. Spec Section 32, lines 2803–2828 — read the whole section before `L2-T523`.
4. Spec Section 33.4, lines 2887–2912 — the pipeline this phase enforces.
5. Spec Section 48.3, lines 4317–4320 — one paragraph, and `L2-T525` implements all of it.
6. Spec Section 96.6, L8835 (row S18) and Section 106 L10172 (D78) — before `L2-T522` and `L2-T402`.
7. Spec Section 46.2, lines 4132–4149, and invariants 22 and 23, lines 9483–9484 — before `L2-T524`.

Nothing in this phase requires interpretation. Every literal string, regex, path and exit code is fixed by the task that creates it. Where a value is not stated in the spec or fixed by a task above, it is a DECISION REQUIRED for L0 — never a judgment call for the executor.
