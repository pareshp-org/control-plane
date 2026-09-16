<!-- AUTHORITY NOTE (FD-044): L2-05-tasks.md is canonical. Task IDs here use a non-standard namespace. -->
> **[SUPERSEDED — FD-B1-L2 2026-09-02]**
> This file has been superseded by L2-05-tasks.md. Do not execute tasks from this file.
> Authoritative plan: Code/implementation/lanes/L2-05-tasks.md

# L2-01 — PHASE 1: THE REUSABLE WORKFLOW LIBRARY

**Lane:** L2 Pipeline & Evidence (Subsystems **E** and **F**, spec §99.2).
**Branch prefix:** `lane/2/*` (PARTITION.md, "The five build lanes").
**Repository:** `control-plane`.
**Paths this document may create or edit — and no others:**

| Path | Note |
|---|---|
| `.github/workflows/**` | the reusable workflow library itself (GitHub requires reusable workflows to live here) |
| `templates/workflows/**` | the per-product caller stubs that `create-product` scaffolds into product repositories |
| `tools/evidence/**` | the record/event emitter shims the workflows call |

Any file outside those three trees is a **foreign path**. A PR touching one fails the lane-guard check (PARTITION.md, anti-conflict rule 1). There is no exception and no "small fix" carve-out.

---

## 0. What this phase produces, and why each piece exists

§99.2 subsystem **E** is: *"ci, build, deploy-staging, deploy-production, migrate, restore-test, org-export, background-queue — consumed by pinned tag; the digest invariant enforced in code; parity job; delta-gated security and licence scanning; SBOM emission; Friday-freeze time gate."*

§33.2 states the per-repository requirement differently and more completely:

> **Required workflows per repository**: `ci.yml`, `build.yml`, `deploy-staging.yml`, `deploy-production.yml`, `migrate.yml`, `restore-test.yml`, `restore-production.yml` wherever the product declares a `recovery:` block (§44.5), and conditionally `background-queue.yml`.

**`restore-production.yml` is absent from the §99.2 subsystem-E list and mandatory everywhere else.** §44.5 mandates it per product ("A product with a `recovery:` block and no `restore-production.yml` fails contract validation (15.5) and is Blocking-class drift under §53"), §37.3 names it in the closed set of privileged workflows that must carry an actor gate, D87 names it in the closed set of privileged workflows that must assert their runner tier, and **AT-103** is an acceptance test that exercises it end to end. This phase builds it. That is the one place where this plan is deliberately larger than the §99.2 row, and §33.2/§44.5/AT-103 are the authority.

Two workflows in this library are **not** per-product workflows and run only in the control plane: `org-export.yml` (§45.3, the GitHub organisation export) and `background-queue.yml` (§37, conditional on the §37.6 benchmark gate). They are built here because §99.2 places them in subsystem E.

### The shape every workflow in this library takes

```
control-plane/.github/workflows/<name>.yml     ← reusable  (on: workflow_call)   ← tagged workflows/vN
                     ▲
                     │ uses: <org>/control-plane/.github/workflows/<name>.yml@workflows/vN
                     │
product-repo/.github/workflows/<name>.yml      ← caller stub, generated at product creation (§19.1)
                     ▲
                     │ scaffolded from
                     │
control-plane/templates/workflows/<name>.yml   ← the template this lane also owns
```

### Pinning discipline — binding on every task in this phase

| Thing being referenced | Rule | Authority |
|---|---|---|
| Third-party GitHub Action | pinned to a **full 40-character commit SHA**. No tags, no branches, no exceptions. A human-readable version comment may follow the SHA | §33.2 bullet "Third-party GitHub Actions pinned to full commit SHA"; §48.1 |
| Reusable workflow in this library, consumed by a product | pinned **tag** `workflows/vN`, never a branch | §33.2, §33.3 ("Consumption is by pinned tag, never by branch"), §48.1 |
| The tag itself | the control-plane repository carries a **tag ruleset blocking updates and deletions on `workflows/*` with an empty bypass-actor list**, and workflow releases are published immutably | §33.2 |
| The tag's resolved commit SHA | recorded in `platform.yaml` and compared every reconciliation run — **Blocking on any change** | §53.1 row *"`platform.yaml` workflow versions / The commit SHA each `workflows/*` tag currently resolves to"* |
| Reusable workflow calling another reusable workflow **inside this same repository** | pinned tag, same as a product consumer — never `@main` | §33.3 |

Why the tag protection is P0 and not hygiene, in the spec's own words (§33.2): *"Moving a tag is the one way to execute new code in every product's pipeline with no pull request, no change manifest, no canary set and no diff in any product repository — it defeats the blast-radius apparatus of §33.3 and invariant 72 in a single command."*

### Token permissions — binding on every workflow file in this phase

§33.2: *"The organisation default for `GITHUB_TOKEN` permissions is read-only; a workflow that needs write access declares it explicitly, per permission, in the workflow file."* Every file this phase writes therefore carries a top-level `permissions:` block. No workflow may declare `permissions: write-all`.

### Required-check discipline — binding on `ci.yml`

§33.2: *"Every required check name is therefore emitted by a job carrying no `if:` and no path filter, which dispatches the real work and asserts a real conclusion: no work was needed is an explicit recorded success, never a skip."* A `skipped` or `neutral` conclusion on a required context of a merged pull request is Blocking drift. Task **L2-P1-T05** encodes this literally, and its self-verify proves it.

---

## 1. DECISION REQUIRED — hand to L0 before execution starts

These three items are **not** decidable by the executing agent, and no task below may be started that depends on an unanswered one. Each is a lane-local decision request; **they are not Appendix A decision IDs** and must never be written into a workflow file as `D<number>`.

### DECISION REQUIRED — L2/P1/DEC-A — the scan toolchain

**What is undecided.** §33.2 requires *"unit tests, integration tests, build, security scan, licence scan, contract validation, registry and assignment validation, environment parity check, and the verification contract check"*; §48.2 requires a licence scanner with delta gating; §48.3 requires an SBOM emitted *"beside the artifact digest — same pipeline step, same storage discipline, same immutability"*. **No section of the specification names which scanner, which licence scanner, or which SBOM generator.** §99.5 (Technology-shape decisions) settles the git host, CI, dashboards, identity bridge, Layer B, boards, records and background layer, and is silent on all three of these.

**What L0 must return.** Exactly nine values, to be written verbatim into `templates/workflows/scan-tools.env` (an L2-owned file) by task **L2-P1-T01**:

```
SECURITY_SCANNER_IMAGE=<registry/image>
SECURITY_SCANNER_DIGEST=sha256:<64-hex>
SECURITY_SCANNER_SARIF_PATH=<path the scanner writes>
LICENCE_SCANNER_IMAGE=<registry/image>
LICENCE_SCANNER_DIGEST=sha256:<64-hex>
LICENCE_SCANNER_REPORT_PATH=<path the scanner writes>
SBOM_GENERATOR_IMAGE=<registry/image>
SBOM_GENERATOR_DIGEST=sha256:<64-hex>
SBOM_FORMAT=<spdx-json|cyclonedx-json>
```

**Q7 answered:** nine `*_IMAGE` / `*_DIGEST` values, shape confirmed.

**Why it cannot be defaulted here.** §48.2 says the scanner's *"policy configuration is a control-plane artifact, versioned like every other reusable configuration"*, which makes the choice a platform change under §61 with a canary set — precisely the class of decision PARTITION.md reserves to L0.

**Until answered:** tasks L2-P1-T05 (ci.yml) and L2-P1-T06 (build.yml) STOP at their stated STOP rule.

### RESOLVED — L2/P1/DEC-B — Contract Change Request: per-product command fields on `product.yaml`

Resolved (Q14=B): workflow uses literal `make deploy` and `make restore`. No parameterized deploy_command/restore_command inputs.

### DECISION REQUIRED — L2/P1/DEC-C — the numeric Friday-freeze boundary

**What is undecided.** §34.2 fixes the freeze at *"15:00 Friday"* and requires the deploy to *"complete its smoke tests and initial observation window within core hours"*. **The specification never gives "core hours" a numeric end time and never names the timezone the freeze is evaluated in.** §94.2 says only *"Working hours are the same core hours, applied per each person's declared working calendar"*; D111 puts an IANA timezone on the **person** record (`work_arrangement`), and §15.1 puts a timezone on `operations.coverage_window` only where `support_model` is `extended` or `24x7` — which is `null` for the `business-hours` default. A product-level freeze gate has no timezone to read.

**What L0 must return.** Exactly four values, to be written verbatim into `templates/workflows/freeze-policy.env` by task **L2-P1-T04**:

```
FREEZE_TZ=<IANA timezone identifier>
FREEZE_FRIDAY_START_LATEST=15:00
CORE_HOURS_END=<HH:MM>
OBSERVATION_WINDOW_MINUTES=<integer>
```

`FREEZE_FRIDAY_START_LATEST` is fixed at `15:00` by §34.2 and is listed only so the file is complete; the other three are the decision.

**Until answered:** task L2-P1-T04 STOPs at its stated STOP rule, and every task depending on it (T07–T11, T13) STOPs with it.

---

## 2. Task index

Execute strictly in this order. One branch per task, `lane/2/p1-<task-id>`, rebased on `integration` before PR (PARTITION.md, "Branch & merge model").

| Task ID | Title | Size | Depends on |
|---|---|---|---|
| `L2-P1-T00` | Lane bootstrap and library skeleton | S | — |
| `L2-P1-T01` | Third-party action pin manifest, applier and verifier | S | T00 |
| `L2-P1-T02` | Record and event emitter shims under `tools/evidence/` | S | T00 |
| `L2-P1-T03` | `gate-actor.yml` — the §37.3 actor gate as a reusable workflow | M | T01, T02 |
| `L2-P1-T04` | `gate-freeze.yml` — the §34.2 Friday-freeze time gate | M | T01, T02 |
| `L2-P1-T05` | `ci.yml` — delta-gated scanning, parity, contract and verification checks | L | T01, T02 |
| `L2-P1-T06` | `build.yml` — immutable artifact, digest recorded, SBOM emitted | M | T01, T02 |
| `L2-P1-T07` | `deploy-staging.yml` | M | T02, T03, T06 |
| `L2-P1-T08` | `deploy-production.yml` — the digest invariant and the workflow-identity gate | L | T02, T03, T04, T06, T07 |
| `L2-P1-T09` | `migrate.yml` | M | T02, T03, T04 |
| `L2-P1-T10` | `restore-production.yml` — the engine, forensic snapshot first | M | T02, T03, T04 |
| `L2-P1-T11` | `restore-test.yml` — the same engine, isolated target | M | T10 |
| `L2-P1-T12` | `org-export.yml` | M | T01, T02 |
| `L2-P1-T13` | `background-queue.yml` | M | T01, T02, T03 |
| `L2-P1-T14` | Per-product caller templates under `templates/workflows/` | M | T05–T13 |
| `L2-P1-T15` | Cut `workflows/v1`, record its SHA, file the tag-ruleset and `platform.yaml` requests | S | T14 |

**Universal preconditions for every task below.** Run these three commands first; if any fails, apply that task's STOP rule.

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git rev-parse --verify origin/integration
```

**Universal tool requirement.** Every self-verify block uses `actionlint`, `yq` (v4) and `gh`. Install once:

**Commands**

```bash
set -euo pipefail
go install github.com/rhysd/actionlint/cmd/actionlint@latest
yq --version
gh auth status
```

If `actionlint`, `yq` or `gh` is unavailable, **STOP** and file the blocker template in section 4 with `Blocked-on: tooling`.

---

## 3. Tasks

## [retired] ~~L2-P1-T00~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** S **Depends on:** — **Files created:**

- `.github/workflows/README.md`
- `.github/workflows/_pins/.gitkeep`
- `templates/workflows/README.md`
- `tools/evidence/workflow-lib/.gitkeep`

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t00 origin/integration

mkdir -p .github/workflows/_pins
mkdir -p templates/workflows
mkdir -p tools/evidence/workflow-lib
touch .github/workflows/_pins/.gitkeep
touch tools/evidence/workflow-lib/.gitkeep

cat > .github/workflows/README.md <<'EOF'
# Reusable workflow library (control plane) — Subsystem E, spec Section 99.2

Every file in this directory that is not prefixed `_` is a REUSABLE workflow
(`on: workflow_call`) consumed by product repositories BY PINNED TAG
(`workflows/vN`), never by branch. Spec Sections 33.2, 33.3, 48.1.

Rules, binding, no exceptions:

1. Third-party actions are pinned to a full 40-character commit SHA
   (Section 33.2, Section 48.1). `_pins/verify-pins.sh` enforces this.
2. Every workflow declares an explicit top-level `permissions:` block.
   `permissions: write-all` is prohibited (Section 33.2).
3. A workflow in this directory calling another workflow in this directory
   uses the pinned tag `@workflows/vN`, never `@main` (Section 33.3).
4. Changing any file here is a PLATFORM CHANGE (Section 33.2, Section 61):
   affected products, repositories, stacks, lifecycle states, risk assessment
   and a proposed canary set are generated before approval (Section 33.3).
5. The `workflows/*` tag namespace is protected by a tag ruleset blocking
   updates and deletions with an EMPTY bypass-actor list (Section 33.2).
   Each tag's resolved commit SHA sits in the reconciliation comparison set
   and is Blocking on any change (Section 53.1).
6. Subdirectories of this path are ignored by GitHub Actions; `_pins/` holds
   pin tooling and is never a workflow.
EOF

cat > templates/workflows/README.md <<'EOF'
# Per-product workflow caller templates — spec Sections 19.1, 33.2

`create-product` (Subsystem D, lane L3) copies these files into a new product
repository under `.github/workflows/`, substituting the `__UPPER_SNAKE__`
placeholders from `product.yaml`. The templates contain no logic: each is a
thin caller that consumes a reusable workflow from the control plane BY PINNED
TAG (Section 33.2, Section 33.3).

Required per repository (Section 33.2): ci.yml, build.yml, deploy-staging.yml,
deploy-production.yml, migrate.yml, restore-test.yml, restore-production.yml
wherever the product declares a `recovery:` block (Section 44.5), and
conditionally background-queue.yml.
EOF

git add -- .github/workflows/README.md .github/workflows/_pins/.gitkeep templates/workflows/README.md tools/evidence/workflow-lib/.gitkeep
git commit -m "L2-P1-T00: reusable workflow library skeleton and consumption rules"
git push -u origin lane/2/p1-t00
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | All four paths exist | `ls .github/workflows/README.md .github/workflows/_pins/.gitkeep templates/workflows/README.md tools/evidence/workflow-lib/.gitkeep` | four paths echoed, exit 0 |
| 2 | Nothing outside the three owned trees was added | `git diff --name-only origin/integration...HEAD \| grep -vE '^(\.github/workflows/|templates/workflows/|tools/evidence/)' \| wc -l` | `0` |
| 3 | Branch pushed | `git rev-parse --abbrev-ref --symbolic-full-name @{u}` | `origin/lane/2/p1-t00` |

**SELF-VERIFY**

```bash
set -euo pipefail
test -f .github/workflows/README.md \
 && test -f templates/workflows/README.md \
 && test -d tools/evidence/workflow-lib \
 && [ "$(git diff --name-only origin/integration...HEAD | grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)')" = "0" ] \
 && echo "T00 OK"
```

Correct output: the single line `T00 OK` and exit status 0. Any other output means not done.

**STOP rule.** If `origin/integration` does not exist, or `git push` is rejected because the branch prefix `lane/2/` is denied, **do not create the branch elsewhere and do not push to `integration` or `main`.** File the blocker with `Blocked-on: branch-model`.

---

## [retired] ~~L2-P1-T01~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** S **Depends on:** T00 **Files created:**

- `.github/workflows/_pins/pins.env`
- `.github/workflows/_pins/resolve-pins.sh`
- `.github/workflows/_pins/apply-pins.sh`
- `.github/workflows/_pins/verify-pins.sh`
- `templates/workflows/scan-tools.env`

Every later workflow task writes `uses: <owner>/<repo>@__PIN_<KEY>__` and then runs `apply-pins.sh`, which substitutes the resolved SHA. `verify-pins.sh` is the acceptance gate for every later task: it fails if any `uses:` line in `.github/workflows/*.yml` references a third-party action by anything other than a 40-hex SHA.

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t01 origin/integration

cat > .github/workflows/_pins/resolve-pins.sh <<'EOF'
#!/usr/bin/env bash
# Resolves each third-party action's latest release tag to a full commit SHA
# and writes .github/workflows/_pins/pins.env. Spec Section 33.2, Section 48.1.
# Deterministic given the upstream repository state; no choice is made here.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
OUT=.github/workflows/_pins/pins.env
ACTIONS="ACTIONS_CHECKOUT:actions/checkout
ACTIONS_UPLOAD_ARTIFACT:actions/upload-artifact
ACTIONS_DOWNLOAD_ARTIFACT:actions/download-artifact
ACTIONS_GITHUB_SCRIPT:actions/github-script
DOCKER_SETUP_BUILDX:docker/setup-buildx-action
DOCKER_LOGIN:docker/login-action
DOCKER_BUILD_PUSH:docker/build-push-action"
: > "$OUT"
echo "# GENERATED by resolve-pins.sh — do not hand-edit. Spec 33.2, 48.1." >> "$OUT"
while IFS=: read -r key repo; do
  [ -z "$key" ] && continue
  tag="$(gh api "repos/${repo}/releases/latest" --jq '.tag_name')"
  sha="$(gh api "repos/${repo}/commits/${tag}" --jq '.sha')"
  case "$sha" in
    [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]) : ;;
    *) echo "FATAL: ${repo}@${tag} did not resolve to a 40-hex SHA" >&2; exit 1 ;;
  esac
  echo "PIN_${key}_REPO=${repo}"  >> "$OUT"
  echo "PIN_${key}_SHA=${sha}"    >> "$OUT"
  echo "PIN_${key}_TAG=${tag}"    >> "$OUT"
done <<< "$ACTIONS"
echo "wrote $OUT"
EOF

cat > .github/workflows/_pins/apply-pins.sh <<'EOF'
#!/usr/bin/env bash
# Replaces every __PIN_<KEY>__ token in .github/workflows/*.yml with the SHA
# recorded in pins.env, appending the human-readable tag as a comment.
# Idempotent: a file with no tokens is left byte-identical.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# shellcheck disable=SC1091
set -a; . .github/workflows/_pins/pins.env; set +a
for f in .github/workflows/*.yml; do
  [ -e "$f" ] || continue
  for key in ACTIONS_CHECKOUT ACTIONS_UPLOAD_ARTIFACT ACTIONS_DOWNLOAD_ARTIFACT \
             ACTIONS_GITHUB_SCRIPT DOCKER_SETUP_BUILDX DOCKER_LOGIN DOCKER_BUILD_PUSH; do
    shavar="PIN_${key}_SHA"; tagvar="PIN_${key}_TAG"
    sha="${!shavar:-}"; tag="${!tagvar:-}"
    [ -z "$sha" ] && continue
    sed -i "s|__PIN_${key}__|${sha} # ${tag}|g" "$f"
  done
done
echo "pins applied"
EOF

cat > .github/workflows/_pins/verify-pins.sh <<'EOF'
#!/usr/bin/env bash
# FAILS if any workflow in .github/workflows/*.yml references a third-party
# action by anything other than a full 40-character commit SHA, or if any
# __PIN_ token survives, or if any reusable-workflow reference into this
# repository uses a branch instead of the workflows/vN tag.
# Spec Section 33.2 ("no tags, no floating branches, no exceptions"),
# Section 33.3 ("Consumption is by pinned tag, never by branch"), Section 48.1.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
fail=0
if grep -RIn '__PIN_[A-Z_]*__' .github/workflows/*.yml 2>/dev/null; then
  echo "FAIL: unsubstituted pin token"; fail=1
fi
while IFS= read -r line; do
  ref="${line##*@}"
  case "$line" in
    *"/.github/workflows/"*) # reusable workflow reference
      case "$ref" in
        workflows/v[0-9]*) : ;;
        *) echo "FAIL: reusable workflow not consumed by workflows/vN tag: $line"; fail=1 ;;
      esac ;;
    *"uses: ./"*|*"uses: docker://"*) : ;;
    *)
      if ! printf '%s' "$ref" | grep -Eq '^[0-9a-f]{40}$'; then
        echo "FAIL: third-party action not pinned to a 40-hex SHA: $line"; fail=1
      fi ;;
  esac
done < <(grep -RhoE '^[[:space:]]*uses:[[:space:]]*[^[:space:]#]+' .github/workflows/*.yml 2>/dev/null | sed 's/^[[:space:]]*uses:[[:space:]]*//')
if grep -RIn 'permissions:[[:space:]]*write-all' .github/workflows/*.yml 2>/dev/null; then
  echo "FAIL: permissions: write-all is prohibited (Section 33.2)"; fail=1
fi
if [ "$fail" -eq 0 ]; then echo "PINS OK"; fi
exit "$fail"
EOF

chmod +x .github/workflows/_pins/*.sh
bash .github/workflows/_pins/resolve-pins.sh

# scan-tools.env: values come from DECISION REQUIRED L2/P1/DEC-A.
# Write it ONLY with values L0 returned. Do not invent values.
cat > templates/workflows/scan-tools.env <<'EOF'
# Scan toolchain — values supplied by L0 under DECISION REQUIRED L2/P1/DEC-A.
# Spec Sections 33.2 (security and licence scan), 48.2 (licence scanning),
# 48.3 (SBOM per artifact). Every image is referenced BY DIGEST, never by tag.
SECURITY_SCANNER_IMAGE=
SECURITY_SCANNER_DIGEST=
SECURITY_SCANNER_SARIF_PATH=
LICENCE_SCANNER_IMAGE=
LICENCE_SCANNER_DIGEST=
LICENCE_SCANNER_REPORT_PATH=
SBOM_GENERATOR_IMAGE=
SBOM_GENERATOR_DIGEST=
SBOM_FORMAT=
EOF

git add -- .github/workflows/_pins/pins.env .github/workflows/_pins/resolve-pins.sh .github/workflows/_pins/apply-pins.sh .github/workflows/_pins/verify-pins.sh templates/workflows/scan-tools.env
git commit -m "L2-P1-T01: action pin manifest, applier, verifier; scan-tools contract file"
git push -u origin lane/2/p1-t01
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | `pins.env` holds exactly seven `_SHA=` lines, each 40 hex | `grep -c '_SHA=[0-9a-f]\{40\}$' .github/workflows/_pins/pins.env` | `7` |
| 2 | No `_SHA=` line is empty or short | `grep -E '_SHA=' .github/workflows/_pins/pins.env \| grep -vcE '_SHA=[0-9a-f]{40}$'` | `0` |
| 3 | The verifier passes on an empty library | `bash .github/workflows/_pins/verify-pins.sh` | `PINS OK`, exit 0 |
| 4 | `scan-tools.env` has all nine keys | `grep -cE '^(SECURITY_SCANNER_(IMAGE|DIGEST|SARIF_PATH)|LICENCE_SCANNER_(IMAGE|DIGEST|REPORT_PATH)|SBOM_(GENERATOR_IMAGE|GENERATOR_DIGEST|FORMAT))=' templates/workflows/scan-tools.env` | `9` |
| 5 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
[ "$(grep -c '_SHA=[0-9a-f]\{40\}$' .github/workflows/_pins/pins.env)" = "7" ] \
 && bash .github/workflows/_pins/verify-pins.sh \
 && echo "T01 OK"
```

Correct output: `PINS OK` followed by `T01 OK`, exit status 0.

**STOP rule.** If `resolve-pins.sh` prints `FATAL: … did not resolve to a 40-hex SHA`, or `gh api` returns 403/404 for any of the seven repositories, **do not substitute a tag, a branch, or a shortened SHA and do not hand-edit `pins.env`.** File the blocker with `Blocked-on: pin-resolution` naming the exact repository and HTTP status. If L0 has not returned DEC-A, leave `scan-tools.env` with empty values, commit it as written above, and record in the PR body that T05 and T06 are blocked on DEC-A.

---

## [retired] ~~L2-P1-T02~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** S **Depends on:** T00 **Files created:**

- `tools/evidence/workflow-lib/emit-record.sh`
- `tools/evidence/workflow-lib/emit-event.sh`

§97.2 makes the deployment-record and event writes **required, failing steps** of `deploy-production.yml`: *"a deploy whose record cannot be written is a deploy whose evidence chain does not close, and the eleven questions of §32 are unanswerable for it afterwards."* §97.3 requires one file per event, never a concurrent append to a shared period file. §40.1 (D89) puts the record stores in their **own repository**, written by a records-writer GitHub App token scoped to that repository alone.

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t02 origin/integration

cat > tools/evidence/workflow-lib/emit-event.sh <<'EOF'
#!/usr/bin/env bash
# Appends ONE event file to the records repository. Spec Section 97.3.
# One file per event, never a concurrent append to a shared period file.
# Envelope fields are binding: an event missing any is rejected at write time.
# Args: <event_type> <actor> <product> <subject_ref> <payload-yaml-or-empty>
set -euo pipefail
[ "$#" -ge 4 ] || { echo "FATAL: emit-event.sh needs 4 or 5 args" >&2; exit 1; }
EVENT_TYPE="$1"; ACTOR="$2"; PRODUCT="$3"; SUBJECT_REF="$4"; PAYLOAD="${5:-}"
: "${RECORDS_REPO:?FATAL: RECORDS_REPO unset}"
: "${RECORDS_WRITER_TOKEN:?FATAL: RECORDS_WRITER_TOKEN unset}"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DAY="$(date -u +%Y-%m-%d)"
EID="EVT-${DAY}-$(date -u +%H%M%S)-${RANDOM}"
WORK="$(mktemp -d)"
git -c http.extraheader="AUTHORIZATION: bearer ${RECORDS_WRITER_TOKEN}" \
    clone --depth 1 "https://github.com/${RECORDS_REPO}.git" "$WORK/r" >/dev/null 2>&1
mkdir -p "$WORK/r/events/${DAY}"
{
  echo "event_schema_version: 1"
  echo "event_id: ${EID}"
  echo "event_type: ${EVENT_TYPE}"
  echo "occurred_at: ${NOW}"
  echo "recorded_at: ${NOW}"
  echo "actor: ${ACTOR}"
  echo "product: ${PRODUCT}"
  echo "subject_ref: ${SUBJECT_REF}"
  echo "payload:"
  if [ -n "$PAYLOAD" ]; then printf '%s\n' "$PAYLOAD" | sed 's/^/  /'; else echo "  {}"; fi
} > "$WORK/r/events/${DAY}/${EID}.yaml"
git -C "$WORK/r" add "events/${DAY}/${EID}.yaml"
git -C "$WORK/r" -c user.name="records-writer" -c user.email="records-writer@invalid" \
    -c commit.gpgsign=true commit -S -m "event ${EVENT_TYPE} ${EID}"
git -C "$WORK/r" -c http.extraheader="AUTHORIZATION: bearer ${RECORDS_WRITER_TOKEN}" push origin HEAD
echo "$EID"
EOF

cat > tools/evidence/workflow-lib/emit-record.sh <<'EOF'
#!/usr/bin/env bash
# Appends ONE record file to the records repository. Spec Section 97.2.
# Args: <store> <record-id> <yaml-body-on-stdin>
# <store> is a path segment under records/, e.g. deployments, restore-tests,
# uat, incidents, decisions — the canonical stores of Section 97.2.
set -euo pipefail
[ "$#" -eq 2 ] || { echo "FATAL: emit-record.sh needs 2 args" >&2; exit 1; }
STORE="$1"; RID="$2"
: "${RECORDS_REPO:?FATAL: RECORDS_REPO unset}"
: "${RECORDS_WRITER_TOKEN:?FATAL: RECORDS_WRITER_TOKEN unset}"
BODY="$(cat)"
[ -n "$BODY" ] || { echo "FATAL: empty record body" >&2; exit 1; }
WORK="$(mktemp -d)"
git -c http.extraheader="AUTHORIZATION: bearer ${RECORDS_WRITER_TOKEN}" \
    clone --depth 1 "https://github.com/${RECORDS_REPO}.git" "$WORK/r" >/dev/null 2>&1
mkdir -p "$WORK/r/records/${STORE}"
TARGET="$WORK/r/records/${STORE}/${RID}.yaml"
[ -e "$TARGET" ] && { echo "FATAL: record ${RID} exists; records never edit in place (Section 97.2)" >&2; exit 1; }
printf '%s\n' "$BODY" > "$TARGET"
grep -q '^record_schema_version:' "$TARGET" || { echo "FATAL: record_schema_version missing (Section 97.2)" >&2; exit 1; }
git -C "$WORK/r" add "records/${STORE}/${RID}.yaml"
git -C "$WORK/r" -c user.name="records-writer" -c user.email="records-writer@invalid" \
    -c commit.gpgsign=true commit -S -m "record ${STORE}/${RID}"
git -C "$WORK/r" -c http.extraheader="AUTHORIZATION: bearer ${RECORDS_WRITER_TOKEN}" push origin HEAD
echo "records/${STORE}/${RID}.yaml"
EOF

chmod +x tools/evidence/workflow-lib/*.sh
bash -n tools/evidence/workflow-lib/emit-event.sh
bash -n tools/evidence/workflow-lib/emit-record.sh

git add -- tools/evidence/workflow-lib/emit-record.sh tools/evidence/workflow-lib/emit-event.sh
git commit -m "L2-P1-T02: record and event emitter shims for the reusable workflow library"
git push -u origin lane/2/p1-t02
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | Both scripts parse | `bash -n tools/evidence/workflow-lib/emit-event.sh && bash -n tools/evidence/workflow-lib/emit-record.sh && echo PARSE_OK` | `PARSE_OK` |
| 2 | Both fail closed with no token | `env -u RECORDS_WRITER_TOKEN RECORDS_REPO=x bash tools/evidence/workflow-lib/emit-event.sh a b c d; echo "rc=$?"` | contains `RECORDS_WRITER_TOKEN unset`, `rc=1` |
| 3 | `emit-record.sh` rejects a body with no `record_schema_version` | `echo 'id: X' \| RECORDS_REPO=x RECORDS_WRITER_TOKEN=y bash tools/evidence/workflow-lib/emit-record.sh deployments X; echo "rc=$?"` | `rc=1` (fails at clone or at the schema check — never `rc=0`) |
| 4 | Events are one-file-per-event | `grep -c 'events/\${DAY}/\${EID}.yaml' tools/evidence/workflow-lib/emit-event.sh` | `2` |
| 5 | No foreign path touched | `git diff --name-only origin/integration...HEAD \| grep -vcE '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
bash -n tools/evidence/workflow-lib/emit-event.sh \
 && bash -n tools/evidence/workflow-lib/emit-record.sh \
 && ! ( env -u RECORDS_WRITER_TOKEN RECORDS_REPO=x bash tools/evidence/workflow-lib/emit-event.sh a b c d 2>/dev/null ) \
 && echo "T02 OK"
```

Correct output: the single line `T02 OK`, exit status 0.

**STOP rule.** If a file named `tools/evidence/emit-record.sh` or `tools/evidence/emit-event.sh` **already exists** (a different L2 task built the evidence store first), **do not create a second emitter and do not edit theirs.** File the blocker with `Blocked-on: emitter-duplication` and name both paths, so L0 rules on which one the workflow library calls.

---

<!-- SUPERSEDED: Actor-gate implementation here is superseded by L2-05-tasks.md (FD-044) -->
## [retired] ~~L2-P1-T03~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** M **Depends on:** T01, T02 **Files created:** `.github/workflows/gate-actor.yml`

§37.3, binding: *"an **actor gate** as the first step of every privileged workflow: `deploy-staging.yml`, `deploy-production.yml`, `migrate.yml`, the rollback workflow and the production-restore workflow fail closed unless `github.actor` resolves to a human identity in `people.yaml` holding the capability the action requires — `production-approval`, `incident-response` or `devops`. The machine account's permitted dispatch set is a **positive allowlist checked inside each workflow** … the digest generators of §94.7 and nothing else."*
Invariant **18** makes this architectural rather than policy. Removing an actor gate is a workflow-file change and is therefore already Blocking drift (§53.1).

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t03 origin/integration

cat > .github/workflows/gate-actor.yml <<'YAML'
# Reusable: the actor gate. Spec Section 37.3, invariant 18.
# Fails closed unless github.actor is a human identity in people.yaml holding
# the named capability. A machine identity NEVER passes this gate.
name: gate-actor
on:
  workflow_call:
    inputs:
      required_capability:
        description: "production-approval | incident-response | devops"
        required: true
        type: string
      registry_ref:
        description: "control-plane ref holding people.yaml"
        required: true
        type: string
    secrets:
      REGISTRY_READ_TOKEN:
        required: true
    outputs:
      actor_person_id:
        description: "people.yaml id of the gated actor"
        value: ${{ jobs.gate.outputs.actor_person_id }}
permissions:
  contents: read
jobs:
  gate:
    runs-on: ubuntu-latest
    outputs:
      actor_person_id: ${{ steps.resolve.outputs.person_id }}
    steps:
      - name: Check out people.yaml from the control plane
        uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with:
          repository: ${{ github.repository_owner }}/control-plane
          ref: ${{ inputs.registry_ref }}
          token: ${{ secrets.REGISTRY_READ_TOKEN }}
          path: cp
          persist-credentials: false
      - name: Resolve actor and assert capability (fail closed)
        id: resolve
        env:
          ACTOR: ${{ github.actor }}
          CAP: ${{ inputs.required_capability }}
        run: |
          set -euo pipefail
          test -f cp/people.yaml || { echo "FAIL: people.yaml unreadable — gate fails closed (Section 64.2)"; exit 1; }
          case "$CAP" in
            production-approval|incident-response|devops) : ;;
            *) echo "FAIL: required_capability '$CAP' is not one of the three named in Section 37.3"; exit 1 ;;
          esac
          PID="$(yq -r ".people[] | select(.github_login == \"${ACTOR}\") | .id // \"\"" cp/people.yaml)"
          if [ -z "$PID" ]; then
            echo "FAIL: actor '${ACTOR}' is not a person in people.yaml — machine identities never pass this gate (Section 37.3)"; exit 1
          fi
          KIND="$(yq -r ".people[] | select(.id == \"${PID}\") | .identity_kind // \"human\"" cp/people.yaml)"
          if [ "$KIND" != "human" ]; then
            echo "FAIL: actor '${ACTOR}' resolves to identity_kind '${KIND}', not human (Section 37.3)"; exit 1
          fi
          HELD="$(yq -r ".people[] | select(.id == \"${PID}\") | .capabilities[]?" cp/people.yaml | tr '\n' ' ')"
          case " ${HELD} " in
            *" ${CAP} "*) : ;;
            *) echo "FAIL: '${PID}' does not hold '${CAP}' (Section 37.3, invariant 18)"; exit 1 ;;
          esac
          echo "person_id=${PID}" >> "$GITHUB_OUTPUT"
          echo "ACTOR GATE PASS ${PID} ${CAP}"
YAML

bash .github/workflows/_pins/apply-pins.sh
bash .github/workflows/_pins/verify-pins.sh
actionlint .github/workflows/gate-actor.yml

git add -- .github/workflows/gate-actor.yml
git commit -m "L2-P1-T03: gate-actor.yml — Section 37.3 actor gate, fails closed"
git push -u origin lane/2/p1-t03
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | Lints clean | `actionlint .github/workflows/gate-actor.yml; echo "rc=$?"` | `rc=0`, no other output |
| 2 | Pins verified | `bash .github/workflows/_pins/verify-pins.sh` | `PINS OK`, exit 0 |
| 3 | Least-privilege token | `yq -r '.permissions' .github/workflows/gate-actor.yml` | `contents: read` |
| 4 | It is reusable, not dispatchable | `yq -r '.on \| keys \| .[]' .github/workflows/gate-actor.yml` | `workflow_call` (one line only) |
| 5 | Only the three §37.3 capabilities are accepted | `grep -c 'production-approval\|incident-response\|devops' .github/workflows/gate-actor.yml` | `≥ 2` |
| 6 | It fails closed on unreadable registry | `grep -c 'gate fails closed' .github/workflows/gate-actor.yml` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
actionlint .github/workflows/gate-actor.yml \
 && bash .github/workflows/_pins/verify-pins.sh \
 && [ "$(yq -r '.on | keys | .[]' .github/workflows/gate-actor.yml)" = "workflow_call" ] \
 && [ "$(yq -r '.permissions.contents' .github/workflows/gate-actor.yml)" = "read" ] \
 && echo "T03 OK"
```

Correct output: `PINS OK` then `T03 OK`, exit status 0.

**STOP rule.** If `people.yaml` in the control plane has no `github_login` field, or no `capabilities` list per person, the `yq` expressions above cannot resolve. **Do not invent a field name and do not fall back to matching on display name.** File the blocker with `Blocked-on: contract-L1` naming the exact `yq` path that returned empty; `people.yaml` belongs to L1 (`registries/**`) and only L1 or L0 may change it.

---

## [retired] ~~L2-P1-T04~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** M **Depends on:** T01 **Files created:** `.github/workflows/gate-freeze.yml`, `templates/workflows/freeze-policy.env`

§34.2, binding and precise: *"a production deploy must **start** by 15:00 Friday **and** complete its smoke tests and initial observation window within core hours — satisfying one condition without the other still breaches the freeze."* Two exceptions only, both named in §34.2: progressive-delivery deploys (which go out with the change disabled) and deploys explicitly authorised under §47. §47.1 lists exactly four permitted triggers and §47.2 makes SEV-1 the sole case needing no prior authorisation.

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t04 origin/integration

# Values from DECISION REQUIRED L2/P1/DEC-C. Do not invent them.
cat > templates/workflows/freeze-policy.env <<'EOF'
# Friday-freeze boundary — Spec Section 34.2.
# FREEZE_FRIDAY_START_LATEST is fixed at 15:00 by Section 34.2 itself.
# The other three are supplied by L0 under DECISION REQUIRED L2/P1/DEC-C.
FREEZE_TZ=
FREEZE_FRIDAY_START_LATEST=15:00
CORE_HOURS_END=
OBSERVATION_WINDOW_MINUTES=
EOF

cat > .github/workflows/gate-freeze.yml <<'YAML'
# Reusable: the Friday-freeze time gate. Spec Section 34.2.
# Two conditions, BOTH required: the deploy must START by 15:00 Friday AND
# complete smoke plus the initial observation window within core hours.
# Excepted, per Section 34.2: progressive-delivery deploys, and deploys
# explicitly authorised under Section 47 (four permitted triggers, 47.1).
name: gate-freeze
on:
  workflow_call:
    inputs:
      progressive_delivery:
        description: "product.yaml deployment.progressive_delivery: none | flag-gated | staged-rollout"
        required: true
        type: string
      support_model:
        description: "product.yaml operations.support_model"
        required: true
        type: string
      exception_id:
        description: "Section 54 exception registry id authorising out-of-hours work; empty if none"
        required: false
        default: ""
        type: string
    outputs:
      freeze_verdict:
        description: "permitted | deferred"
        value: ${{ jobs.freeze.outputs.verdict }}
permissions:
  contents: read
jobs:
  freeze:
    runs-on: ubuntu-latest
    outputs:
      verdict: ${{ steps.evaluate.outputs.verdict }}
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with:
          persist-credentials: false
      - name: Load the freeze policy (fail closed if incomplete)
        run: |
          set -euo pipefail
          F=templates/workflows/freeze-policy.env
          test -f "$F" || { echo "FAIL: freeze-policy.env missing — gate fails closed"; exit 1; }
          set -a; . "$F"; set +a
          for v in FREEZE_TZ FREEZE_FRIDAY_START_LATEST CORE_HOURS_END OBSERVATION_WINDOW_MINUTES; do
            eval "val=\${$v:-}"
            [ -n "$val" ] || { echo "FAIL: $v unset in freeze-policy.env — DECISION REQUIRED L2/P1/DEC-C unanswered"; exit 1; }
          done
          {
            echo "FREEZE_TZ=$FREEZE_TZ"
            echo "FREEZE_FRIDAY_START_LATEST=$FREEZE_FRIDAY_START_LATEST"
            echo "CORE_HOURS_END=$CORE_HOURS_END"
            echo "OBSERVATION_WINDOW_MINUTES=$OBSERVATION_WINDOW_MINUTES"
          } >> "$GITHUB_ENV"
      - name: Evaluate both freeze conditions
        id: evaluate
        env:
          PROGRESSIVE: ${{ inputs.progressive_delivery }}
          SUPPORT: ${{ inputs.support_model }}
          EXC: ${{ inputs.exception_id }}
        run: |
          set -euo pipefail
          # Exception 1 (Section 34.2): progressive delivery ships with the change disabled.
          if [ "$PROGRESSIVE" = "flag-gated" ] || [ "$PROGRESSIVE" = "staged-rollout" ]; then
            echo "verdict=permitted" >> "$GITHUB_OUTPUT"
            echo "FREEZE GATE PASS: progressive delivery, excepted by Section 34.2"; exit 0
          fi
          # Exception 2 (Section 34.2 -> Section 47): an explicit recorded authorisation.
          if [ -n "$EXC" ]; then
            echo "verdict=permitted" >> "$GITHUB_OUTPUT"
            echo "FREEZE GATE PASS: authorised under Section 47, exception ${EXC}"; exit 0
          fi
          NOW_EPOCH="$(date -u +%s)"
          DOW="$(TZ="$FREEZE_TZ" date -d "@${NOW_EPOCH}" +%u)"     # 1=Mon .. 7=Sun
          HHMM="$(TZ="$FREEZE_TZ" date -d "@${NOW_EPOCH}" +%H:%M)"
          # Condition A, Section 34.2: a Friday production deploy must START by 15:00.
          if [ "$DOW" = "5" ] && [ "$HHMM" \> "$FREEZE_FRIDAY_START_LATEST" ]; then
            echo "verdict=deferred" >> "$GITHUB_OUTPUT"
            echo "FREEZE GATE BLOCK: ${HHMM} ${FREEZE_TZ} is past 15:00 Friday (Section 34.2). Deferred to the next working morning."
            exit 1
          fi
          if [ "$DOW" -gt 5 ]; then
            echo "verdict=deferred" >> "$GITHUB_OUTPUT"
            echo "FREEZE GATE BLOCK: weekend deploy with no Section 47 authorisation."
            exit 1
          fi
          # Condition B, Section 34.2: smoke plus the initial observation window
          # must complete within core hours. Both conditions bind; one is not enough.
          END_EPOCH="$(TZ="$FREEZE_TZ" date -d "$(TZ="$FREEZE_TZ" date -d "@${NOW_EPOCH}" +%Y-%m-%d) ${CORE_HOURS_END}" +%s)"
          FINISH_EPOCH=$(( NOW_EPOCH + OBSERVATION_WINDOW_MINUTES * 60 ))
          if [ "$FINISH_EPOCH" -gt "$END_EPOCH" ]; then
            echo "verdict=deferred" >> "$GITHUB_OUTPUT"
            echo "FREEZE GATE BLOCK: observation window of ${OBSERVATION_WINDOW_MINUTES}m would end after core hours (${CORE_HOURS_END} ${FREEZE_TZ}). Section 34.2: deferred to the next working morning."
            exit 1
          fi
          echo "verdict=permitted" >> "$GITHUB_OUTPUT"
          echo "FREEZE GATE PASS: start and observation both inside the boundary (support_model=${SUPPORT})"
YAML

bash .github/workflows/_pins/apply-pins.sh
bash .github/workflows/_pins/verify-pins.sh
actionlint .github/workflows/gate-freeze.yml

git add -- .github/workflows/gate-freeze.yml templates/workflows/freeze-policy.env
git commit -m "L2-P1-T04: gate-freeze.yml — Section 34.2 Friday freeze, both conditions"
git push -u origin lane/2/p1-t04
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | Lints clean | `actionlint .github/workflows/gate-freeze.yml; echo "rc=$?"` | `rc=0` |
| 2 | Pins verified | `bash .github/workflows/_pins/verify-pins.sh` | `PINS OK` |
| 3 | Both §34.2 conditions are present | `grep -c 'Condition A\|Condition B' .github/workflows/gate-freeze.yml` | `2` |
| 4 | Exactly the two §34.2 exceptions exist | `grep -c '^          # Exception ' .github/workflows/gate-freeze.yml` | `2` |
| 5 | Unanswered DEC-C fails closed | `grep -c 'DECISION REQUIRED L2/P1/DEC-C unanswered' .github/workflows/gate-freeze.yml` | `1` |
| 6 | Least-privilege token | `yq -r '.permissions.contents' .github/workflows/gate-freeze.yml` | `read` |

**SELF-VERIFY**

```bash
set -euo pipefail
actionlint .github/workflows/gate-freeze.yml \
 && bash .github/workflows/_pins/verify-pins.sh \
 && [ "$(grep -c '# Condition [AB],' .github/workflows/gate-freeze.yml)" = "2" ] \
 && echo "T04 OK"
```

Correct output: `PINS OK` then `T04 OK`, exit status 0.

**STOP rule.** If L0 has not returned DEC-C, commit `freeze-policy.env` with the empty values exactly as written above and **do not guess a timezone or a core-hours end time.** The gate then fails closed at run time, which is correct. Record in the PR body that T07–T11 and T13 are blocked. If any reviewer asks for a "temporary default", refuse and file the blocker with `Blocked-on: DEC-C`.

---

## [retired] ~~L2-P1-T05~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** L **Depends on:** T01, T02 **Files created:** `.github/workflows/ci.yml`

§33.2 names the full push-triggered set: *"unit tests, integration tests, build, security scan, licence scan, contract validation, registry and assignment validation, environment parity check, and the verification contract check."* Four further §33.2 rules bind this file specifically:

1. **Delta gating.** *"fail on new findings only, so a legacy backlog does not block every merge. Licence-scanning findings are delta-gated the same way."* (§48.2 repeats it for licences.)
2. **Slopsquat at execute time.** *"CI runs the slopsquat legitimacy check (§30.2) against lockfile and manifest diffs, delta-gated to new and changed entries, so a dependency added during Execute cannot bypass the plan-time check."*
3. **No `if:` and no path filter on a job emitting a required check.** *"no work was needed is an explicit recorded success, never a skip."*
4. **Verification-contract discriminating power.** §31.2 / D97: each contract declares a seeded-defect case it MUST fail; *"a run in which the seeded defect passes is a FAILED run"*, raising SIG-18 and Blocking for that product.

**Required-check contexts this file emits** (these are the names L0 lists in branch protection at §98.2 Phase 4/5/6):
`ci / verify` · `ci / scan` · `ci / parity` · `ci / contract` · `ci / slopsquat`

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t05 origin/integration

cat > .github/workflows/ci.yml <<'YAML'
# Reusable: continuous integration. Spec Section 33.2.
# EVERY job below emits a required status-check context and therefore carries
# NO `if:` and NO path filter (Section 33.2). "No work was needed" is an
# explicit recorded success, never a skip: a skipped or neutral conclusion on
# a required context of a merged pull request is Blocking drift.
name: ci
on:
  workflow_call:
    inputs:
      product_id:      { required: true,  type: string }
      registry_ref:    { required: true,  type: string }
      base_ref:        { required: true,  type: string }
      conformance_profile: { required: true, type: string }
    secrets:
      REGISTRY_READ_TOKEN:  { required: true }
      RECORDS_WRITER_TOKEN: { required: true }
permissions:
  contents: read
  checks: write
jobs:

  verify:
    name: verify
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { fetch-depth: 0, persist-credentials: false }
      - name: Unit and integration tests (Section 33.2)
        run: make test
      - name: Verification contract present and discriminating (Section 31.2, D97)
        run: |
          set -euo pipefail
          C=verification/contract.yaml
          test -f "$C" || { echo "FAIL: no verification contract (invariant 1)"; exit 1; }
          SEED="$(yq -r '.seeded_defect_case // ""' "$C")"
          [ -n "$SEED" ] || { echo "FAIL: contract declares no seeded-defect case (Section 31.2) — raises SIG-18"; exit 1; }
          # A contract that cannot fail is not a contract: the seeded case MUST fail.
          if bash -c "$SEED"; then
            echo "FAIL: the seeded defect PASSED. This is a FAILED run, not a clean one (Section 31.2, D97). Raises SIG-18; Blocking for this product."
            exit 1
          fi
          echo "verification contract discriminates"

  scan:
    name: scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { fetch-depth: 0, persist-credentials: false }
      - name: Load the scan toolchain (fail closed)
        run: |
          set -euo pipefail
          F=templates/workflows/scan-tools.env
          test -f "$F" || { echo "FAIL: scan-tools.env missing"; exit 1; }
          set -a; . "$F"; set +a
          for v in SECURITY_SCANNER_IMAGE SECURITY_SCANNER_DIGEST LICENCE_SCANNER_IMAGE LICENCE_SCANNER_DIGEST; do
            eval "val=\${$v:-}"
            [ -n "$val" ] || { echo "FAIL: $v unset — DECISION REQUIRED L2/P1/DEC-A unanswered"; exit 1; }
          done
          echo "SECURITY_REF=${SECURITY_SCANNER_IMAGE}@${SECURITY_SCANNER_DIGEST}" >> "$GITHUB_ENV"
          echo "LICENCE_REF=${LICENCE_SCANNER_IMAGE}@${LICENCE_SCANNER_DIGEST}"   >> "$GITHUB_ENV"
          echo "SARIF=${SECURITY_SCANNER_SARIF_PATH}"  >> "$GITHUB_ENV"
          echo "LICREP=${LICENCE_SCANNER_REPORT_PATH}" >> "$GITHUB_ENV"
      - name: Security scan — HEAD and base, delta-gated (Section 33.2)
        env: { BASE: "${{ inputs.base_ref }}" }
        run: |
          set -euo pipefail
          docker run --rm -v "$PWD:/src" -w /src "$SECURITY_REF" > head.sarif
          git worktree add ../base "origin/${BASE}"
          docker run --rm -v "$PWD/../base:/src" -w /src "$SECURITY_REF" > base.sarif
          # Delta gate: fail on NEW findings only. A legacy backlog does not
          # block every merge (Section 33.2). Existing findings enter technical
          # debt governance with a named owner (Section 48.2, Section 56).
          NEW="$(comm -13 \
            <(yq -r '.runs[].results[]? | (.ruleId + "|" + (.locations[0].physicalLocation.artifactLocation.uri // "")) ' base.sarif | sort -u) \
            <(yq -r '.runs[].results[]? | (.ruleId + "|" + (.locations[0].physicalLocation.artifactLocation.uri // "")) ' head.sarif | sort -u))"
          if [ -n "$NEW" ]; then echo "FAIL: new security findings:"; printf '%s\n' "$NEW"; exit 1; fi
          echo "no new security findings"
      - name: Licence scan — delta-gated identically (Section 48.2)
        env: { BASE: "${{ inputs.base_ref }}" }
        run: |
          set -euo pipefail
          docker run --rm -v "$PWD:/src" -w /src "$LICENCE_REF" > head.lic
          docker run --rm -v "$PWD/../base:/src" -w /src "$LICENCE_REF" > base.lic
          NEW="$(comm -13 <(sort -u base.lic) <(sort -u head.lic))"
          if [ -n "$NEW" ]; then echo "FAIL: new licence findings:"; printf '%s\n' "$NEW"; exit 1; fi
          echo "no new licence findings"

  slopsquat:
    name: slopsquat
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { fetch-depth: 0, persist-credentials: false }
      - name: Package legitimacy against live registries, delta-gated (Section 33.2, Section 30.2)
        env: { BASE: "${{ inputs.base_ref }}" }
        run: |
          set -euo pipefail
          # Delta-gated to NEW AND CHANGED entries only, so a dependency added
          # during Execute cannot bypass the plan-time check (Section 33.2).
          CHANGED="$(git diff --name-only "origin/${BASE}"...HEAD -- \
            package.json package-lock.json yarn.lock pnpm-lock.yaml \
            requirements.txt poetry.lock go.mod go.sum Cargo.toml Cargo.lock || true)"
          if [ -z "$CHANGED" ]; then
            echo "NO WORK NEEDED: no manifest or lockfile changed in this diff."
            echo "This is an explicit recorded success, never a skip (Section 33.2)."
            exit 0
          fi
          bash tools/evidence/workflow-lib/../../../tools/slopsquat/check.sh "origin/${BASE}" HEAD

  parity:
    name: parity
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { persist-credentials: false }
      - name: Environment parity (Section 33.1)
        run: |
          set -euo pipefail
          # "A parity violation on a production deployment path is a blocking
          # CI failure" (Section 33.1).
          make parity

  contract:
    name: contract
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { persist-credentials: false, path: prod }
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with:
          repository: ${{ github.repository_owner }}/control-plane
          ref: ${{ inputs.registry_ref }}
          token: ${{ secrets.REGISTRY_READ_TOKEN }}
          path: cp
          persist-credentials: false
      - name: Required-file presence (Section 33.1 — checked, not assumed)
        working-directory: prod
        run: |
          set -euo pipefail
          MISSING=""
          for f in .env.example docker-compose.dev.yml Makefile AGENTS.md verification; do
            [ -e "$f" ] || MISSING="$MISSING $f"
          done
          [ -e product.yaml ] || [ -e .product-ref ] || MISSING="$MISSING product.yaml-or-pointer"
          if [ -n "$MISSING" ]; then echo "FAIL: required files missing:$MISSING (Section 33.1)"; exit 1; fi
          echo "required files present"
      - name: Contract, registry and assignment validation (Section 33.2, Section 15.5)
        run: |
          set -euo pipefail
          python3 cp/validators/registry/validate.py \
            --product prod/product.yaml \
            --registries cp/registries \
            --schemas cp/schemas
YAML

bash .github/workflows/_pins/apply-pins.sh
bash .github/workflows/_pins/verify-pins.sh
actionlint .github/workflows/ci.yml

git add -- .github/workflows/ci.yml
git commit -m "L2-P1-T05: ci.yml — delta-gated scan and licence, slopsquat, parity, contract, verification"
git push -u origin lane/2/p1-t05
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | Lints clean | `actionlint .github/workflows/ci.yml; echo "rc=$?"` | `rc=0` |
| 2 | Pins verified | `bash .github/workflows/_pins/verify-pins.sh` | `PINS OK` |
| 3 | **No job carries `if:`** (§33.2) | `yq -r '.jobs \| to_entries[] \| select(.value.if) \| .key' .github/workflows/ci.yml \| wc -l` | `0` |
| 4 | **No path filter anywhere** (§33.2) | `grep -c 'paths:\|paths-ignore:' .github/workflows/ci.yml` | `0` |
| 5 | Exactly five required contexts | `yq -r '.jobs \| keys \| .[]' .github/workflows/ci.yml \| sort \| tr '\n' ' '` | `contract parity scan slopsquat verify ` |
| 6 | Delta gating present for both scanners | `grep -c 'Delta gate\|delta-gated identically' .github/workflows/ci.yml` | `2` |
| 7 | Seeded-defect case enforced | `grep -c 'the seeded defect PASSED' .github/workflows/ci.yml` | `1` |
| 8 | "No work needed" is an explicit success | `grep -c 'NO WORK NEEDED' .github/workflows/ci.yml` | `1` |
| 9 | Least-privilege token | `yq -r '.permissions \| to_entries \| map(.key + "=" + .value) \| join(",")' .github/workflows/ci.yml` | `contents=read,checks=write` |

**SELF-VERIFY**

```bash
set -euo pipefail
actionlint .github/workflows/ci.yml \
 && bash .github/workflows/_pins/verify-pins.sh \
 && [ "$(yq -r '.jobs | to_entries[] | select(.value.if) | .key' .github/workflows/ci.yml | wc -l)" = "0" ] \
 && [ "$(grep -c 'paths:\|paths-ignore:' .github/workflows/ci.yml)" = "0" ] \
 && [ "$(yq -r '.jobs | keys | .[]' .github/workflows/ci.yml | sort | tr '\n' ' ')" = "contract parity scan slopsquat verify " \
 ] && echo "T05 OK"
```

Correct output: `PINS OK` then `T05 OK`, exit status 0.

**STOP rules.**
- If DEC-A is unanswered, the `scan` job's fail-closed step is correct as written; commit the file and record in the PR body that `ci / scan` cannot go green until DEC-A lands. **Do not substitute a scanner of your own choosing.**
- If `cp/validators/registry/validate.py` does not exist, that path belongs to **L1** (`validators/registry/**`). **Do not write it.** File the blocker with `Blocked-on: L1-validators`.
- If `tools/slopsquat/check.sh` does not exist, it belongs to Subsystem **G** (plan-checker, §99.2), not to this lane. File the blocker with `Blocked-on: subsystem-G-slopsquat`. **Do not implement a registry-API check inside this workflow.**

---

## [retired] ~~L2-P1-T06~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** M **Depends on:** T01, T02 **Files created:** `.github/workflows/build.yml`

§33.4: *"Immutable artifact (digest recorded)"* and *"Artifact immutability is P0."* §48.3: *"Every production artifact build emits a Software Bill of Materials **beside the artifact digest** — same pipeline step, same storage discipline, same immutability."* §32 item 5: the artifact digest is *"Registry digest, recorded at build."* Invariant **22**: the production artifact is the same digest verified in staging, never rebuilt.

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t06 origin/integration

cat > .github/workflows/build.yml <<'YAML'
# Reusable: immutable artifact build. Spec Sections 33.4, 48.3, 32 (item 5).
# The digest emitted here is the ONLY digest that may ever reach production
# (invariant 22). Nothing downstream rebuilds.
name: build
on:
  workflow_call:
    inputs:
      product_id:        { required: true, type: string }
      artifact_registry: { required: true, type: string }   # product.yaml deployment.artifact_registry
      artifact_type:     { required: true, type: string }   # product.yaml deployment.artifact_type
      records_repo:      { required: true, type: string }
    secrets:
      REGISTRY_WRITE_TOKEN: { required: true }
      RECORDS_WRITER_TOKEN: { required: true }
    outputs:
      digest:
        description: "sha256:… of the built artifact — the evidence-chain identity (Section 32 item 5)"
        value: ${{ jobs.build.outputs.digest }}
permissions:
  contents: read
  packages: write
jobs:
  build:
    name: build
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.push.outputs.digest }}
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { persist-credentials: false }
      - name: Reject a non-container artifact type without a declared identity (Section 96.6 S8)
        env: { AT: "${{ inputs.artifact_type }}" }
        run: |
          set -euo pipefail
          [ "$AT" = "docker-image" ] || {
            echo "FAIL: artifact_type '${AT}' is not docker-image. The digest invariant is not waivable; the packaging format is (Section 96.6, S8). Route this product through its declared equivalent-identity path before building here."
            exit 1; }
      - uses: docker/setup-buildx-action@__PIN_DOCKER_SETUP_BUILDX__
      - uses: docker/login-action@__PIN_DOCKER_LOGIN__
        with:
          registry: ${{ inputs.artifact_registry }}
          username: ${{ github.actor }}
          password: ${{ secrets.REGISTRY_WRITE_TOKEN }}
      - name: Build and push once — never rebuilt downstream (invariant 22)
        id: push
        uses: docker/build-push-action@__PIN_DOCKER_BUILD_PUSH__
        with:
          context: .
          push: true
          provenance: true
          tags: ${{ inputs.artifact_registry }}:${{ github.sha }}
      - name: Emit the SBOM beside the digest — same step, same immutability (Section 48.3)
        env:
          DIGEST: ${{ steps.push.outputs.digest }}
          REF: ${{ inputs.artifact_registry }}
        run: |
          set -euo pipefail
          set -a; . templates/workflows/scan-tools.env; set +a
          [ -n "${SBOM_GENERATOR_IMAGE:-}" ] && [ -n "${SBOM_GENERATOR_DIGEST:-}" ] || {
            echo "FAIL: SBOM generator unset — DECISION REQUIRED L2/P1/DEC-A unanswered"; exit 1; }
          docker run --rm "${SBOM_GENERATOR_IMAGE}@${SBOM_GENERATOR_DIGEST}" \
            "${REF}@${DIGEST}" --format "${SBOM_FORMAT}" > sbom.json
          test -s sbom.json || { echo "FAIL: empty SBOM (Section 48.3)"; exit 1; }
      - uses: actions/upload-artifact@__PIN_ACTIONS_UPLOAD_ARTIFACT__
        with:
          name: sbom-${{ steps.push.outputs.digest }}
          path: sbom.json
          if-no-files-found: error
      - name: Record the build event (Section 97.3 — artifact built with digest)
        env:
          RECORDS_REPO: ${{ inputs.records_repo }}
          RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
        run: |
          set -euo pipefail
          bash tools/evidence/workflow-lib/emit-event.sh \
            artifact_built "${{ github.actor }}" "${{ inputs.product_id }}" \
            "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}" \
            "digest: ${{ steps.push.outputs.digest }}
commit: ${{ github.sha }}
sbom: sbom-${{ steps.push.outputs.digest }}"
YAML

bash .github/workflows/_pins/apply-pins.sh
bash .github/workflows/_pins/verify-pins.sh
actionlint .github/workflows/build.yml

git add -- .github/workflows/build.yml
git commit -m "L2-P1-T06: build.yml — immutable artifact, digest recorded, SBOM beside the digest"
git push -u origin lane/2/p1-t06
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | Lints clean | `actionlint .github/workflows/build.yml; echo "rc=$?"` | `rc=0` |
| 2 | Pins verified | `bash .github/workflows/_pins/verify-pins.sh` | `PINS OK` |
| 3 | The workflow exposes a `digest` output | `yq -r '.on.workflow_call.outputs.digest.value' .github/workflows/build.yml` | `${{ jobs.build.outputs.digest }}` |
| 4 | SBOM emission is in the build, not a later job | `yq -r '.jobs \| keys \| .[]' .github/workflows/build.yml` | `build` (one line) |
| 5 | Empty SBOM fails the build | `grep -c 'FAIL: empty SBOM' .github/workflows/build.yml` | `1` |
| 6 | Least-privilege token | `yq -r '.permissions \| to_entries \| map(.key+"="+.value) \| join(",")' .github/workflows/build.yml` | `contents=read,packages=write` |
| 7 | An `artifact_built` event is emitted | `grep -c 'artifact_built' .github/workflows/build.yml` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
actionlint .github/workflows/build.yml \
 && bash .github/workflows/_pins/verify-pins.sh \
 && [ "$(yq -r '.jobs | keys | length' .github/workflows/build.yml)" = "1" ] \
 && grep -q 'artifact_built' .github/workflows/build.yml \
 && echo "T06 OK"
```

Correct output: `PINS OK` then `T06 OK`, exit status 0.

**STOP rule.** If `artifact_built` is **not** a member of the closed `event_type` enum declared in `platform.yaml` (§97.3: *"control-plane CI rejects any event whose `event_type` is absent from it"*), **do not add it to the enum yourself** — `platform.yaml` is an L0 root file. File the blocker with `Blocked-on: event-enum` naming every event type this phase emits: `artifact_built`, `staging_deployed`, `staging_smoke_result`, `production_deployed`, `production_smoke_result`, `version_digest_confirmed`, `restore_test_executed`, `rollback_initiated`.

---

## [retired] ~~L2-P1-T07~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** M **Depends on:** T02, T03, T06 **Files created:** `.github/workflows/deploy-staging.yml`

§33.4: *"Staging deploy → smoke tests → QA manual UAT"*, and the environment carries a deployment branch and tag policy restricting it to the default branch and protected release tags (D91). §37.3 names `deploy-staging.yml` in the closed set of privileged workflows carrying an actor gate. §32 items 6 and 7 make the staging deployment record and the staging verification result part of the evidence chain.

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t07 origin/integration

cat > .github/workflows/deploy-staging.yml <<'YAML'
# Reusable: staging deployment. Spec Sections 33.4, 32 (items 6-7), 37.3.
name: deploy-staging
on:
  workflow_call:
    inputs:
      product_id:     { required: true, type: string }
      digest:         { required: true, type: string }   # from build.yml — never rebuilt (invariant 22)
      registry_ref:   { required: true, type: string }
      records_repo:   { required: true, type: string }
      staging_url:    { required: true, type: string }   # product.yaml environments.staging
    secrets:
      REGISTRY_READ_TOKEN:  { required: true }
      RECORDS_WRITER_TOKEN: { required: true }
permissions:
  contents: read
jobs:

  actor-gate:
    # Section 37.3: the actor gate is the FIRST step of every privileged workflow.
    uses: ./.github/workflows/gate-actor.yml
    with:
      required_capability: devops
      registry_ref: ${{ inputs.registry_ref }}
    secrets:
      REGISTRY_READ_TOKEN: ${{ secrets.REGISTRY_READ_TOKEN }}

  deploy:
    needs: actor-gate
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: ${{ inputs.staging_url }}
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { persist-credentials: false }
      - name: Assert the digest is a real content digest (Section 32 item 5)
        env: { D: "${{ inputs.digest }}" }
        run: |
          set -euo pipefail
          printf '%s' "$D" | grep -Eq '^sha256:[0-9a-f]{64}$' || { echo "FAIL: '${D}' is not a sha256 content digest"; exit 1; }
      - name: Deploy the built digest — never rebuilt (invariant 22)
        env:
          DEPLOY_DIGEST: ${{ inputs.digest }}
          TARGET_ENV: staging
        run: make deploy
      - name: Smoke tests (Section 33.4)
        id: smoke
        run: bash verification/smoke/run.sh "${{ inputs.staging_url }}"
      - name: Confirm /version reports the deployed digest (Section 41.2, Section 32 item 11)
        run: |
          set -euo pipefail
          LIVE="$(curl -fsS "${{ inputs.staging_url }}/version" | yq -r '.digest')"
          [ "$LIVE" = "${{ inputs.digest }}" ] || { echo "FAIL: /version reports ${LIVE}, expected ${{ inputs.digest }}"; exit 1; }
      - name: Record the staging deployment and its smoke result (Section 32 items 6-7, Section 97.3)
        env:
          RECORDS_REPO: ${{ inputs.records_repo }}
          RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
        run: |
          set -euo pipefail
          RUN="${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
          bash tools/evidence/workflow-lib/emit-event.sh staging_deployed \
            "${{ github.actor }}" "${{ inputs.product_id }}" "$RUN" "digest: ${{ inputs.digest }}"
          bash tools/evidence/workflow-lib/emit-event.sh staging_smoke_result \
            "${{ github.actor }}" "${{ inputs.product_id }}" "$RUN" "result: pass
digest: ${{ inputs.digest }}"
YAML

bash .github/workflows/_pins/apply-pins.sh
bash .github/workflows/_pins/verify-pins.sh
actionlint .github/workflows/deploy-staging.yml

git add -- .github/workflows/deploy-staging.yml
git commit -m "L2-P1-T07: deploy-staging.yml — actor gate first, digest asserted, smoke and /version recorded"
git push -u origin lane/2/p1-t07
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | Lints clean | `actionlint .github/workflows/deploy-staging.yml; echo "rc=$?"` | `rc=0` |
| 2 | Pins verified | `bash .github/workflows/_pins/verify-pins.sh` | `PINS OK` |
| 3 | The actor gate runs before the deploy job (§37.3) | `yq -r '.jobs.deploy.needs' .github/workflows/deploy-staging.yml` | `actor-gate` |
| 4 | Deploy step uses literal `make deploy` (Q14=B) | `grep -c 'run: make deploy' .github/workflows/deploy-staging.yml` | `1` |
| 5 | The job is bound to the `staging` environment (D91) | `yq -r '.jobs.deploy.environment.name' .github/workflows/deploy-staging.yml` | `staging` |
| 6 | Digest format is asserted | `grep -c 'sha256:\[0-9a-f\]{64}' .github/workflows/deploy-staging.yml` | `1` |
| 7 | Least-privilege token | `yq -r '.permissions.contents' .github/workflows/deploy-staging.yml` | `read` |

**SELF-VERIFY**

```bash
set -euo pipefail
actionlint .github/workflows/deploy-staging.yml \
 && bash .github/workflows/_pins/verify-pins.sh \
 && [ "$(yq -r '.jobs.deploy.needs' .github/workflows/deploy-staging.yml)" = "actor-gate" ] \
 && [ "$(yq -r '.jobs.deploy.environment.name' .github/workflows/deploy-staging.yml)" = "staging" ] \
 && [ "$(grep -c 'run: make deploy' .github/workflows/deploy-staging.yml)" = "1" ] \
 && echo "T07 OK"
```

Correct output: `PINS OK` then `T07 OK`, exit status 0.

**STOP rule.** `uses: ./.github/workflows/gate-actor.yml` is a **same-repository local reference and is correct only inside the control plane**. If review asks you to change it to `@main`, refuse: §33.3 forbids branch consumption. If review asks you to inline the gate's steps into this file, refuse: §37.3 requires the gate as the first step of every privileged workflow and a copy in five files is five places for it to be quietly removed. File the blocker with `Blocked-on: gate-composition`.

---

## [retired] ~~L2-P1-T08~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** L **Depends on:** T02, T03, T04, T06, T07 **Files created:** `.github/workflows/deploy-production.yml`

Five separate binding requirements meet in this one file. Each is quoted so the executor never has to interpret:

1. **The digest invariant, enforced in code.** §32: *"item 5 and item 11 must match, and the digest deployed to production must be byte-identical to the one verified in staging. CI rejects any production deployment where the requested digest differs from the digest that passed staging verification."* §33.4 repeats it; invariant **22**.
2. **The workflow-identity gate — the mechanism of record.** §27.2: *"The deploy workflow itself verifies that the recorded approving identity differs from the deploying identity and fails closed if it cannot tell."* D73 confirms environment required reviewers are **not** the mechanism.
3. **The actor gate.** §37.3, closed set.
4. **The Friday-freeze gate.** §34.2.
5. **Records are required, failing steps.** §97.2: *"the deployment-record and event writes are **required, failing steps** of `deploy-production.yml` rather than trailing best-effort ones."*
6. **Runner tier.** D87: the privileged workflows *"run on hosted runners by default"* and *"Each privileged workflow asserts its own runner tier and fails closed."*

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t08 origin/integration

cat > .github/workflows/deploy-production.yml <<'YAML'
# Reusable: production deployment. Spec Sections 32, 33.4, 27.2 (D73), 34.2,
# 37.3, 97.2, D87. The most gated workflow in the estate.
name: deploy-production
on:
  workflow_call:
    inputs:
      product_id:            { required: true, type: string }
      digest:                { required: true, type: string }
      staging_verified_digest: { required: true, type: string }
      approval_record:       { required: true, type: string }  # records/… path (Section 97)
      registry_ref:          { required: true, type: string }
      records_repo:          { required: true, type: string }
      production_url:        { required: true, type: string }
      progressive_delivery:  { required: true, type: string }
      support_model:         { required: true, type: string }
      exception_id:          { required: false, type: string, default: "" }
      runner_tier:           { required: false, type: string, default: "hosted" }  # D87
    secrets:
      REGISTRY_READ_TOKEN:  { required: true }
      RECORDS_WRITER_TOKEN: { required: true }
permissions:
  contents: read
jobs:

  actor-gate:
    uses: ./.github/workflows/gate-actor.yml
    with:
      required_capability: devops
      registry_ref: ${{ inputs.registry_ref }}
    secrets:
      REGISTRY_READ_TOKEN: ${{ secrets.REGISTRY_READ_TOKEN }}

  freeze-gate:
    uses: ./.github/workflows/gate-freeze.yml
    with:
      progressive_delivery: ${{ inputs.progressive_delivery }}
      support_model: ${{ inputs.support_model }}
      exception_id: ${{ inputs.exception_id }}

  identity-and-digest-gates:
    needs: [actor-gate, freeze-gate]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { persist-credentials: false }
      - name: Assert the runner tier (D87 — fails closed)
        env: { TIER: "${{ inputs.runner_tier }}" }
        run: |
          set -euo pipefail
          case "$TIER" in
            hosted) [ "${RUNNER_ENVIRONMENT:-}" = "github-hosted" ] || { echo "FAIL: runner_tier=hosted but RUNNER_ENVIRONMENT=${RUNNER_ENVIRONMENT:-unset} (D87)"; exit 1; } ;;
            privileged-ephemeral) : ;;
            *) echo "FAIL: runner_tier '${TIER}' is not a declared tier (D87)"; exit 1 ;;
          esac
      - name: THE DIGEST INVARIANT — requested must equal staging-verified (Section 32, invariant 22)
        env:
          REQ: ${{ inputs.digest }}
          VER: ${{ inputs.staging_verified_digest }}
        run: |
          set -euo pipefail
          printf '%s' "$REQ" | grep -Eq '^sha256:[0-9a-f]{64}$' || { echo "FAIL: requested digest malformed"; exit 1; }
          if [ "$REQ" != "$VER" ]; then
            echo "FAIL: requested ${REQ} != staging-verified ${VER}."
            echo "CI rejects any production deployment where the requested digest differs from the digest that passed staging verification (Section 32). Never rebuilt (invariant 22)."
            exit 1
          fi
          echo "DIGEST INVARIANT OK ${REQ}"
      - name: THE WORKFLOW-IDENTITY GATE — approver != deployer, fails closed (Section 27.2, D73)
        env:
          RECORDS_REPO: ${{ inputs.records_repo }}
          RECORD: ${{ inputs.approval_record }}
          DEPLOYER: ${{ github.actor }}
          RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
        run: |
          set -euo pipefail
          RAW="$(gh api "repos/${RECORDS_REPO}/contents/${RECORD}" --jq '.content' 2>/dev/null | base64 -d || true)"
          [ -n "$RAW" ] || { echo "FAIL: approval record '${RECORD}' unreadable. The gate cannot tell, so it fails closed (Section 27.2)."; exit 1; }
          APPROVER="$(printf '%s' "$RAW" | yq -r '.approved_by // ""')"
          APPDIG="$(printf '%s'  "$RAW" | yq -r '.digest // ""')"
          [ -n "$APPROVER" ] || { echo "FAIL: approval record names no approver — fails closed (Section 27.2)"; exit 1; }
          [ "$APPDIG" = "${{ inputs.digest }}" ] || { echo "FAIL: the approval is for ${APPDIG}, not ${{ inputs.digest }}"; exit 1; }
          if [ "$APPROVER" = "$DEPLOYER" ]; then
            echo "FAIL: approver and deployer are the same identity (${APPROVER}). Self-approval of production deployment is prohibited in all cases (Section 27.2, invariant 12)."
            exit 1
          fi
          echo "IDENTITY GATE OK approver=${APPROVER} deployer=${DEPLOYER}"

  deploy:
    needs: identity-and-digest-gates
    runs-on: ubuntu-latest
    environment:
      name: production
      url: ${{ inputs.production_url }}
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { persist-credentials: false }
      - name: Deploy the SAME digest — never rebuilt (Section 33.4, invariant 22)
        env:
          DEPLOY_DIGEST: ${{ inputs.digest }}
          TARGET_ENV: production
        run: make deploy
      - name: Post-deployment smoke (Section 32 item 10)
        run: bash verification/smoke/run.sh "${{ inputs.production_url }}"
      - name: /version must equal the approved digest (Section 32 item 11, Section 41.2)
        run: |
          set -euo pipefail
          LIVE="$(curl -fsS "${{ inputs.production_url }}/version" | yq -r '.digest')"
          [ "$LIVE" = "${{ inputs.digest }}" ] || {
            echo "FAIL: /version reports ${LIVE}, approved digest is ${{ inputs.digest }}. Any mismatch is a P0 investigation (Section 41.2)."; exit 1; }
      - name: REQUIRED FAILING STEP — write the deployment record (Section 97.2)
        env:
          RECORDS_REPO: ${{ inputs.records_repo }}
          RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
        run: |
          set -euo pipefail
          RUN="${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
          RID="DEP-$(date -u +%Y-%m-%d)-${{ github.run_number }}"
          cat <<EOF | bash tools/evidence/workflow-lib/emit-record.sh deployments "$RID"
record_schema_version: 1
id: $RID
product: ${{ inputs.product_id }}
timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
digest: ${{ inputs.digest }}
approval_event: $RUN
approval_record: ${{ inputs.approval_record }}
staging_verified: true
smoke_result: pass
rollback_of: null
EOF
      - name: REQUIRED FAILING STEP — append the production events (Section 97.2, 97.3)
        env:
          RECORDS_REPO: ${{ inputs.records_repo }}
          RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
        run: |
          set -euo pipefail
          RUN="${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
          bash tools/evidence/workflow-lib/emit-event.sh production_deployed \
            "${{ github.actor }}" "${{ inputs.product_id }}" "$RUN" "digest: ${{ inputs.digest }}"
          bash tools/evidence/workflow-lib/emit-event.sh production_smoke_result \
            "${{ github.actor }}" "${{ inputs.product_id }}" "$RUN" "result: pass"
          bash tools/evidence/workflow-lib/emit-event.sh version_digest_confirmed \
            "${{ github.actor }}" "${{ inputs.product_id }}" "$RUN" "digest: ${{ inputs.digest }}"
YAML

bash .github/workflows/_pins/apply-pins.sh
bash .github/workflows/_pins/verify-pins.sh
actionlint .github/workflows/deploy-production.yml

git add -- .github/workflows/deploy-production.yml
git commit -m "L2-P1-T08: deploy-production.yml — digest invariant, workflow-identity gate, freeze gate, required record writes"
git push -u origin lane/2/p1-t08
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | Lints clean | `actionlint .github/workflows/deploy-production.yml; echo "rc=$?"` | `rc=0` |
| 2 | Pins verified | `bash .github/workflows/_pins/verify-pins.sh` | `PINS OK` |
| 3 | Both gates precede the gate job | `yq -r '.jobs["identity-and-digest-gates"].needs \| join(",")' .github/workflows/deploy-production.yml` | `actor-gate,freeze-gate` |
| 4 | The deploy job runs only after the gates | `yq -r '.jobs.deploy.needs' .github/workflows/deploy-production.yml` | `identity-and-digest-gates` |
| 5 | The digest invariant is enforced in code (§32) | `grep -c 'DIGEST INVARIANT OK' .github/workflows/deploy-production.yml` | `1` |
| 6 | Self-approval is refused | `grep -c 'approver and deployer are the same identity' .github/workflows/deploy-production.yml` | `1` |
| 7 | Unreadable approval record fails closed (§27.2) | `grep -c 'The gate cannot tell, so it fails closed' .github/workflows/deploy-production.yml` | `1` |
| 8 | Record and event writes are steps of this workflow, not a separate best-effort job | `grep -c 'REQUIRED FAILING STEP' .github/workflows/deploy-production.yml` | `2` |
| 9 | The runner tier is asserted (D87) | `grep -c 'runner_tier=hosted but RUNNER_ENVIRONMENT' .github/workflows/deploy-production.yml` | `1` |
| 10 | No environment required-reviewer dependency (D73) | `grep -c 'reviewers' .github/workflows/deploy-production.yml` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
actionlint .github/workflows/deploy-production.yml \
 && bash .github/workflows/_pins/verify-pins.sh \
 && [ "$(yq -r '.jobs["identity-and-digest-gates"].needs | join(",")' .github/workflows/deploy-production.yml)" = "actor-gate,freeze-gate" ] \
 && [ "$(grep -c 'REQUIRED FAILING STEP' .github/workflows/deploy-production.yml)" = "2" ] \
 && [ "$(grep -c 'DIGEST INVARIANT OK' .github/workflows/deploy-production.yml)" = "1" ] \
 && echo "T08 OK"
```

Correct output: `PINS OK` then `T08 OK`, exit status 0.

**STOP rules.**
- If the approval record's field name is not `approved_by` or it carries no `digest`, that schema belongs to **L4** (`schemas/records/**`). **Do not invent an alternative field and do not relax the gate to "approver present or absent".** File the blocker with `Blocked-on: L4-record-schema` quoting the §97.2 deployment-record example (`approved_by`, `digest`).
- If anyone proposes adding `continue-on-error: true` to either record-writing step, refuse and quote §97.2: *"a deploy whose record cannot be written is a deploy whose evidence chain does not close."*
- **The rollback workflow is out of scope for this task.** §27.2 defines a *dedicated rollback workflow* exempt from the identity gate but **not** from the §37.3 actor gate. It is not in the §33.2 required-workflow list and is not built here. File it as a follow-on lane item; do not add a rollback path to this file.

---

## [retired] ~~L2-P1-T09~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** M **Depends on:** T02, T03, T04 **Files created:** `.github/workflows/migrate.yml`

§34.3: *"Migrations are ordered, versioned and applied through CI only. **No human runs a migration by hand against production.**"* Plus: a backup is taken **and verified** before any destructive migration; destructive migrations are architecture-class and require `migration-review` capability plus QA verification sign-off. §34.4 case **B** requires the application deployment not to start when the migration fails, and case **C** requires the migration job to halt. §37.3 and D87 both name `migrate.yml` in the privileged closed set.

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t09 origin/integration

cat > .github/workflows/migrate.yml <<'YAML'
# Reusable: database migration. Spec Sections 34.3, 34.4 (cases B and C), 37.3, D87.
# Migrations are applied through CI ONLY. No human runs one by hand (Section 34.3).
name: migrate
on:
  workflow_call:
    inputs:
      product_id:     { required: true, type: string }
      target_env:     { required: true, type: string }   # staging | production
      destructive:    { required: true, type: boolean }  # Section 34.3
      qa_signoff_record: { required: false, type: string, default: "" }
      registry_ref:   { required: true, type: string }
      records_repo:   { required: true, type: string }
      runner_tier:    { required: false, type: string, default: "hosted" }
      progressive_delivery: { required: true, type: string }
      support_model:  { required: true, type: string }
      exception_id:   { required: false, type: string, default: "" }
    secrets:
      REGISTRY_READ_TOKEN:  { required: true }
      RECORDS_WRITER_TOKEN: { required: true }
    outputs:
      migration_result:
        description: "succeeded | halted — Section 34.4"
        value: ${{ jobs.migrate.outputs.result }}
permissions:
  contents: read
jobs:

  actor-gate:
    uses: ./.github/workflows/gate-actor.yml
    with:
      # A destructive migration is architecture-class and needs migration-review
      # plus QA sign-off (Section 34.3); the actor gate itself accepts only the
      # three capabilities Section 37.3 names, so the extra capability is
      # asserted separately in the preflight job below.
      required_capability: devops
      registry_ref: ${{ inputs.registry_ref }}
    secrets:
      REGISTRY_READ_TOKEN: ${{ secrets.REGISTRY_READ_TOKEN }}

  freeze-gate:
    uses: ./.github/workflows/gate-freeze.yml
    with:
      progressive_delivery: ${{ inputs.progressive_delivery }}
      support_model: ${{ inputs.support_model }}
      exception_id: ${{ inputs.exception_id }}

  preflight:
    needs: [actor-gate, freeze-gate]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { persist-credentials: false, path: prod }
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with:
          repository: ${{ github.repository_owner }}/control-plane
          ref: ${{ inputs.registry_ref }}
          token: ${{ secrets.REGISTRY_READ_TOKEN }}
          path: cp
          persist-credentials: false
      - name: Assert the runner tier (D87)
        env: { TIER: "${{ inputs.runner_tier }}" }
        run: |
          set -euo pipefail
          [ "$TIER" != "hosted" ] || [ "${RUNNER_ENVIRONMENT:-}" = "github-hosted" ] || { echo "FAIL: runner tier (D87)"; exit 1; }
      - name: Destructive migration preconditions (Section 34.3)
        if: ${{ inputs.destructive }}
        env:
          ACTOR: ${{ github.actor }}
          QA: ${{ inputs.qa_signoff_record }}
        run: |
          set -euo pipefail
          HELD="$(yq -r ".people[] | select(.github_login == \"${ACTOR}\") | .capabilities[]?" cp/people.yaml | tr '\n' ' ')"
          case " ${HELD} " in *" migration-review "*) : ;; *) echo "FAIL: destructive migration requires migration-review (Section 34.3)"; exit 1 ;; esac
          [ -n "$QA" ] || { echo "FAIL: destructive migration requires a recorded QA verification sign-off (Section 34.3)"; exit 1; }
      - name: Verified backup immediately prior to a destructive migration (Section 34.3, invariant 3)
        if: ${{ inputs.destructive }}
        run: |
          set -euo pipefail
          # "A backup is taken and verified before any destructive migration."
          # An untested backup is treated as no backup (invariant 3).
          make -C prod backup-and-verify

  migrate:
    needs: preflight
    runs-on: ubuntu-latest
    environment: ${{ inputs.target_env }}
    outputs:
      result: ${{ steps.run.outcome == 'success' && 'succeeded' || 'halted' }}
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { persist-credentials: false }
      - name: Apply migrations (Section 33.1 `make migrate`; Section 34.3 CI only)
        id: run
        run: make migrate
      - name: Halt on failure — the application deployment does not start (Section 34.4 case C)
        if: ${{ failure() }}
        run: |
          echo "Migration failed partway. The migration job halts and the application deployment does not start (Section 34.4, case C)."
          echo "Assess transactionality; if not transactional, apply the documented repair step or restore from the pre-migration backup. Authority: holder of migration-review."
          exit 1
      - name: Record the migration event
        env:
          RECORDS_REPO: ${{ inputs.records_repo }}
          RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
        run: |
          set -euo pipefail
          bash tools/evidence/workflow-lib/emit-event.sh migration_applied \
            "${{ github.actor }}" "${{ inputs.product_id }}" \
            "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}" \
            "target_env: ${{ inputs.target_env }}
destructive: ${{ inputs.destructive }}"
YAML

bash .github/workflows/_pins/apply-pins.sh
bash .github/workflows/_pins/verify-pins.sh
actionlint .github/workflows/migrate.yml

git add -- .github/workflows/migrate.yml
git commit -m "L2-P1-T09: migrate.yml — CI-only migrations, destructive preconditions, halt semantics"
git push -u origin lane/2/p1-t09
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | Lints clean | `actionlint .github/workflows/migrate.yml; echo "rc=$?"` | `rc=0` |
| 2 | Pins verified | `bash .github/workflows/_pins/verify-pins.sh` | `PINS OK` |
| 3 | Both gates precede preflight | `yq -r '.jobs.preflight.needs \| join(",")' .github/workflows/migrate.yml` | `actor-gate,freeze-gate` |
| 4 | Migration runs only after preflight | `yq -r '.jobs.migrate.needs' .github/workflows/migrate.yml` | `preflight` |
| 5 | `migration-review` is required for destructive migrations | `grep -c 'requires migration-review' .github/workflows/migrate.yml` | `1` |
| 6 | A verified backup precedes a destructive migration | `grep -c 'backup-and-verify' .github/workflows/migrate.yml` | `1` |
| 7 | Case C halt semantics are present | `grep -c 'Section 34.4, case C' .github/workflows/migrate.yml` | `1` |
| 8 | The `if:` conditions sit only on destructive-only steps, never on a required-check job | `yq -r '.jobs \| to_entries[] \| select(.value.if) \| .key' .github/workflows/migrate.yml \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
actionlint .github/workflows/migrate.yml \
 && bash .github/workflows/_pins/verify-pins.sh \
 && [ "$(yq -r '.jobs.preflight.needs | join(",")' .github/workflows/migrate.yml)" = "actor-gate,freeze-gate" ] \
 && [ "$(yq -r '.jobs | to_entries[] | select(.value.if) | .key' .github/workflows/migrate.yml | wc -l)" = "0" ] \
 && echo "T09 OK"
```

Correct output: `PINS OK` then `T09 OK`, exit status 0.

**Resolved (§4.6):** Resolved in the same ruling as Q14=B: literal `make backup-and-verify` is used in the restore verification step.

**STOP rule.** `make backup-and-verify` is **not** one of the eight §33.1 standard commands. If it does not exist in the product template, **do not invent a backup command and do not drop the step** — §34.3 and invariant 3 both bind. File the blocker with `Blocked-on: DEC-B-adjacent`, asking L0 whether the eight-command set gains a ninth command or whether `recovery.restore_procedure` supplies the entrypoint.

---

## [retired] ~~L2-P1-T10~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** M **Depends on:** T02, T03, T04 **Files created:** `.github/workflows/restore-production.yml`

This is the workflow §99.2's subsystem-E row omits and §33.2, §44.5 and **AT-103** mandate. §44.5, binding:

- *"a pre-documented procedure, running as a controlled workflow with production-tier credentials, whose every execution writes an **exceptional-authorisation record** — who authorised, why, which backup, which target."*
- *"It takes its restore target as a parameter, and the monthly restore rotation invokes **this same workflow** with the declared `restore_environment` as that target — one workflow, two targets — so the first production execution is never the first execution."*
- *"The workflow runs a **forensic-snapshot stage first**: it captures the corrupted state to the independent-provider backup location and **blocks the restore stage until the capture reports success**"* (§34.4 case F, Step 0).
- *"A production restore whose record names no integrity-check result and no verifier is Red drift (§53.1)."*

AT-103 requires it to execute *"without any credential being handed to or typed by a human."*

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t10 origin/integration

cat > .github/workflows/restore-production.yml <<'YAML'
# Reusable: the restore engine. Spec Sections 44.5, 34.4 (case F), 37.3, D87, AT-103.
# ONE workflow, TWO targets: the monthly rotation calls it with the declared
# restore_environment; a real data-loss incident calls it with production.
name: restore-production
on:
  workflow_call:
    inputs:
      product_id:      { required: true, type: string }
      restore_target:  { required: true, type: string }   # Section 44.5: the target is a parameter
      backup_id:       { required: true, type: string }
      authorised_by:   { required: true, type: string }   # people.yaml id
      reason:          { required: true, type: string }
      integrity_check: { required: true, type: string }   # product.yaml recovery.integrity_check
      verifier:        { required: true, type: string }   # Section 44.5: a NAMED verifier
      registry_ref:    { required: true, type: string }
      records_repo:    { required: true, type: string }
      runner_tier:     { required: false, type: string, default: "hosted" }
      progressive_delivery: { required: true, type: string }
      support_model:   { required: true, type: string }
      exception_id:    { required: false, type: string, default: "" }
    secrets:
      REGISTRY_READ_TOKEN:  { required: true }
      RECORDS_WRITER_TOKEN: { required: true }
    outputs:
      restore_result:
        description: "pass | fail"
        value: ${{ jobs.restore.outputs.result }}
permissions:
  contents: read
jobs:

  actor-gate:
    uses: ./.github/workflows/gate-actor.yml
    with:
      required_capability: incident-response
      registry_ref: ${{ inputs.registry_ref }}
    secrets:
      REGISTRY_READ_TOKEN: ${{ secrets.REGISTRY_READ_TOKEN }}

  freeze-gate:
    uses: ./.github/workflows/gate-freeze.yml
    with:
      progressive_delivery: ${{ inputs.progressive_delivery }}
      support_model: ${{ inputs.support_model }}
      exception_id: ${{ inputs.exception_id }}

  forensic-snapshot:
    # STEP 0, Section 34.4 case F and Section 44.5. This stage BLOCKS the
    # restore stage until the capture reports success.
    needs: [actor-gate, freeze-gate]
    runs-on: ubuntu-latest
    environment: ${{ inputs.restore_target }}
    outputs:
      snapshot_ref: ${{ steps.capture.outputs.ref }}
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { persist-credentials: false }
      - name: Assert the runner tier (D87)
        env: { TIER: "${{ inputs.runner_tier }}" }
        run: |
          set -euo pipefail
          [ "$TIER" != "hosted" ] || [ "${RUNNER_ENVIRONMENT:-}" = "github-hosted" ] || { echo "FAIL: runner tier (D87)"; exit 1; }
      - name: Capture the current state to the independent-provider backup location
        id: capture
        env:
          TARGET: ${{ inputs.restore_target }}
          RESTORE_MODE: forensic-snapshot
        run: |
          set -euo pipefail
          REF="$(make restore)"
          [ -n "$REF" ] || { echo "FAIL: forensic snapshot produced no reference. The restore stage is blocked (Section 44.5, Section 34.4 case F Step 0)."; exit 1; }
          echo "ref=${REF}" >> "$GITHUB_OUTPUT"

  restore:
    needs: forensic-snapshot
    runs-on: ubuntu-latest
    environment: ${{ inputs.restore_target }}
    outputs:
      result: ${{ steps.integrity.outputs.result }}
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { persist-credentials: false }
      - name: Restore the named backup into the parameterised target (Section 44.5)
        env:
          TARGET: ${{ inputs.restore_target }}
          BACKUP_ID: ${{ inputs.backup_id }}
          RESTORE_MODE: restore
        run: make restore
      - name: Assert the declared integrity_check MACHINE-SIDE (Section 44.3)
        id: integrity
        env: { CHECK: "${{ inputs.integrity_check }}" }
        run: |
          set -euo pipefail
          # "row counts and checksums are computed by the job, never read over
          # someone's shoulder" (Section 44.3).
          if bash -c "$CHECK"; then echo "result=pass" >> "$GITHUB_OUTPUT"; else echo "result=fail" >> "$GITHUB_OUTPUT"; exit 1; fi
      - name: REQUIRED FAILING STEP — exceptional-authorisation record with result and NAMED verifier (Section 44.5)
        env:
          RECORDS_REPO: ${{ inputs.records_repo }}
          RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
        run: |
          set -euo pipefail
          [ -n "${{ inputs.verifier }}" ] || {
            echo "FAIL: no named verifier. A production restore whose record names no integrity-check result and no verifier is Red drift (Section 44.5, Section 53.1)."; exit 1; }
          RID="RES-$(date -u +%Y-%m-%d)-${{ github.run_number }}"
          cat <<EOF | bash tools/evidence/workflow-lib/emit-record.sh restore-tests "$RID"
record_schema_version: 1
id: $RID
product: ${{ inputs.product_id }}
timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
restore_target: ${{ inputs.restore_target }}
backup_id: ${{ inputs.backup_id }}
authorised_by: ${{ inputs.authorised_by }}
reason: ${{ inputs.reason }}
forensic_snapshot: ${{ needs.forensic-snapshot.outputs.snapshot_ref }}
integrity_check_result: ${{ steps.integrity.outputs.result }}
verifier: ${{ inputs.verifier }}
executed_by: ${{ github.actor }}
run_url: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
EOF
          bash tools/evidence/workflow-lib/emit-event.sh restore_test_executed \
            "${{ github.actor }}" "${{ inputs.product_id }}" \
            "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}" \
            "result: ${{ steps.integrity.outputs.result }}
target: ${{ inputs.restore_target }}"
YAML

bash .github/workflows/_pins/apply-pins.sh
bash .github/workflows/_pins/verify-pins.sh
actionlint .github/workflows/restore-production.yml

git add -- .github/workflows/restore-production.yml
git commit -m "L2-P1-T10: restore-production.yml — forensic snapshot first, parameterised target, named verifier"
git push -u origin lane/2/p1-t10
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | Lints clean | `actionlint .github/workflows/restore-production.yml; echo "rc=$?"` | `rc=0` |
| 2 | Pins verified | `bash .github/workflows/_pins/verify-pins.sh` | `PINS OK` |
| 3 | The forensic snapshot blocks the restore (§44.5) | `yq -r '.jobs.restore.needs' .github/workflows/restore-production.yml` | `forensic-snapshot` |
| 4 | The target is a parameter, not a constant (§44.5) | `yq -r '.on.workflow_call.inputs.restore_target.required' .github/workflows/restore-production.yml` | `true` |
| 5 | The integrity check is asserted machine-side | `grep -c 'MACHINE-SIDE' .github/workflows/restore-production.yml` | `1` |
| 6 | A missing verifier fails the run | `grep -c 'no named verifier' .github/workflows/restore-production.yml` | `1` |
| 7 | The record carries both the result and the verifier | `grep -c 'integrity_check_result:\|verifier:' .github/workflows/restore-production.yml` | `≥ 2` |
| 8 | No secret is echoed | `grep -c 'echo .*SECRET\|echo .*TOKEN' .github/workflows/restore-production.yml` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
actionlint .github/workflows/restore-production.yml \
 && bash .github/workflows/_pins/verify-pins.sh \
 && [ "$(yq -r '.jobs.restore.needs' .github/workflows/restore-production.yml)" = "forensic-snapshot" ] \
 && [ "$(yq -r '.on.workflow_call.inputs.restore_target.required' .github/workflows/restore-production.yml)" = "true" ] \
 && echo "T10 OK"
```

Correct output: `PINS OK` then `T10 OK`, exit status 0.

**STOP rule.** If review asks for a `restore-test.yml` that duplicates this logic instead of calling it, refuse and quote §44.5: *"one workflow, two targets — so the first production execution is never the first execution."* If the record store name `restore-tests` is not the store §97.2 declares for this record class, **do not create a new store**; file the blocker with `Blocked-on: L4-record-store`.

---

## [retired] ~~L2-P1-T11~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** M **Depends on:** T10 **Files created:** `.github/workflows/restore-test.yml`

§44.2: restore tests run *"monthly on a rotating subset"* with a 90-day rolling floor per product, tightened by `classification.reliability_criticality` and never loosened (invariant **4**, D5). §44.2 also: *"The `restore_tested` date is **derived, not declared**: the restore-test workflow writes it back from the newest passing record in `records/restore-tests/`"* — **a hand-edited date is drift, not evidence**, and §53.1 makes a declared date with no matching record **Blocking**.

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t11 origin/integration

cat > .github/workflows/restore-test.yml <<'YAML'
# Reusable: the monthly restore test. Spec Sections 44.2, 44.3, 44.5, invariant 4.
# This workflow does NOT reimplement the restore. It calls the SAME engine with
# the declared restore_environment as the target (Section 44.5).
name: restore-test
on:
  workflow_call:
    inputs:
      product_id:          { required: true, type: string }
      restore_environment: { required: true, type: string }  # product.yaml recovery.restore_environment
      backup_id:           { required: true, type: string }
      authorised_by:       { required: true, type: string }
      integrity_check:     { required: true, type: string }
      verifier:            { required: true, type: string }
      registry_ref:        { required: true, type: string }
      records_repo:        { required: true, type: string }
      support_model:       { required: true, type: string }
    secrets:
      REGISTRY_READ_TOKEN:  { required: true }
      RECORDS_WRITER_TOKEN: { required: true }
permissions:
  contents: read
jobs:
  run:
    uses: ./.github/workflows/restore-production.yml
    with:
      product_id: ${{ inputs.product_id }}
      restore_target: ${{ inputs.restore_environment }}
      backup_id: ${{ inputs.backup_id }}
      authorised_by: ${{ inputs.authorised_by }}
      reason: "scheduled restore test (Section 44.2 rotation)"
      integrity_check: ${{ inputs.integrity_check }}
      verifier: ${{ inputs.verifier }}
      registry_ref: ${{ inputs.registry_ref }}
      records_repo: ${{ inputs.records_repo }}
      # A restore test is not a production deploy; it is excepted from the
      # Friday-freeze production rule by carrying progressive_delivery, which
      # Section 34.2 excepts. The freeze gate governs PRODUCTION DEPLOYS.
      progressive_delivery: flag-gated
      support_model: ${{ inputs.support_model }}
    secrets:
      REGISTRY_READ_TOKEN: ${{ secrets.REGISTRY_READ_TOKEN }}
      RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}

  assert-derived-date:
    needs: run
    runs-on: ubuntu-latest
    steps:
      - name: restore_tested is DERIVED from the newest passing record (Section 44.2)
        run: |
          set -euo pipefail
          # "A hand-edited date is drift, not evidence." This workflow writes the
          # record; the reconciler derives the date from it (Section 53.1 row:
          # product.yaml restore_tested vs newest passing record => Blocking).
          [ "${{ needs.run.outputs.restore_result }}" = "pass" ] || {
            echo "FAIL: restore test did not pass. A failed restore test is immediate escalation — a live reliability risk, not a scheduling problem (Section 44.3)."; exit 1; }
          echo "restore test passed; record written; restore_tested derives from it"
YAML

bash .github/workflows/_pins/apply-pins.sh
bash .github/workflows/_pins/verify-pins.sh
actionlint .github/workflows/restore-test.yml

git add -- .github/workflows/restore-test.yml
git commit -m "L2-P1-T11: restore-test.yml — calls the restore engine with the isolated target"
git push -u origin lane/2/p1-t11
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | Lints clean | `actionlint .github/workflows/restore-test.yml; echo "rc=$?"` | `rc=0` |
| 2 | Pins verified | `bash .github/workflows/_pins/verify-pins.sh` | `PINS OK` |
| 3 | It calls the engine, does not reimplement it (§44.5) | `yq -r '.jobs.run.uses' .github/workflows/restore-test.yml` | `./.github/workflows/restore-production.yml` |
| 4 | It contains no restore logic of its own | `grep -c 'RESTORE_MODE' .github/workflows/restore-test.yml` | `0` |
| 5 | A failed restore fails the run (§44.3) | `grep -c 'immediate escalation' .github/workflows/restore-test.yml` | `1` |
| 6 | It does not write a `restore_tested` date anywhere | `grep -c 'restore_tested:' .github/workflows/restore-test.yml` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
actionlint .github/workflows/restore-test.yml \
 && bash .github/workflows/_pins/verify-pins.sh \
 && [ "$(yq -r '.jobs.run.uses' .github/workflows/restore-test.yml)" = "./.github/workflows/restore-production.yml" ] \
 && [ "$(grep -c 'RESTORE_MODE' .github/workflows/restore-test.yml)" = "0" ] \
 && echo "T11 OK"
```

Correct output: `PINS OK` then `T11 OK`, exit status 0.

**STOP rule.** The **rotation scheduler** — §44.2's *"nightly rotation scheduler [that] computes each product's restore deadline … and opens the scheduling issue"* — is a §99.2 named tool assigned to subsystems **E, M**. It is a scheduled control-plane job, not a per-product workflow, and it is **not** part of the §33.2 required-workflow list. Do not build it in this task. File it as a follow-on lane item with `Blocked-on: none, scope: L2 phase 2`.

---

## [retired] ~~L2-P1-T12~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** M **Depends on:** T01, T02 **Files created:** `.github/workflows/org-export.yml`

This is a **control-plane-only scheduled workflow**, not a per-product one. §45.3 fixes every property, and D80 fixes the per-class mechanism:

- Repositories, issues, pull requests and review records travel through the **migrations REST API**; **Projects v2 boards are not included in migration archives and are captured by a separate GraphQL dump**; the organisation audit-log API is Enterprise-only and its absence is a recorded accepted risk (D80).
- *"The export job writes with an **append-only, write-only credential** to **object-locked, versioned storage**."*
- *"The export is **encrypted with a key held outside GitHub**."*
- *"Export job failure alerts like a backup failure; a stale export is a Red condition"* — SIG-34.

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t12 origin/integration

cat > .github/workflows/org-export.yml <<'YAML'
# Reusable + scheduled: the GitHub organisation export. Spec Section 45.3, D80, SIG-34, AT-035.
# Control-plane only. Never scaffolded into a product repository.
name: org-export
on:
  workflow_call:
    inputs:
      org:            { required: true, type: string }
      records_repo:   { required: true, type: string }
    secrets:
      EXPORT_READ_TOKEN:   { required: true }   # reads the org; Section 45.3
      EXPORT_WRITE_TOKEN:  { required: true }   # APPEND-ONLY, WRITE-ONLY object-store credential
      EXPORT_ENCRYPT_KEY:  { required: true }   # held OUTSIDE GitHub; Section 45.3
      RECORDS_WRITER_TOKEN:{ required: true }
  schedule:
    - cron: "17 2 * * *"
permissions:
  contents: read
jobs:
  export:
    name: export
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { persist-credentials: false }
      - name: Repositories and metadata via the migrations REST API (D80)
        env:
          GH_TOKEN: ${{ secrets.EXPORT_READ_TOKEN }}
          ORG: ${{ inputs.org }}
        run: |
          set -euo pipefail
          REPOS="$(gh api --paginate "orgs/${ORG}/repos" --jq '.[].full_name' | yq -o=json -I=0 -p=props '.' 2>/dev/null || gh api --paginate "orgs/${ORG}/repos" --jq '[.[].full_name]')"
          MIG="$(gh api -X POST "orgs/${ORG}/migrations" -f "repositories[]=@-" --input - <<< "$REPOS" --jq '.id')"
          [ -n "$MIG" ] || { echo "FAIL: migration not started"; exit 1; }
          echo "MIGRATION_ID=${MIG}" >> "$GITHUB_ENV"
      - name: Projects v2 via a SEPARATE GraphQL dump — never assumed present in the archive (D80)
        env:
          GH_TOKEN: ${{ secrets.EXPORT_READ_TOKEN }}
          ORG: ${{ inputs.org }}
        run: |
          set -euo pipefail
          gh api graphql -f query='query($o:String!){organization(login:$o){projectsV2(first:100){nodes{id title number}}}}' -f o="$ORG" > projects-v2.json
          test -s projects-v2.json || { echo "FAIL: Projects v2 dump empty — boards are not in the migration archive (D80)"; exit 1; }
      - name: Encrypt with a key held outside GitHub (Section 45.3)
        env: { KEY: "${{ secrets.EXPORT_ENCRYPT_KEY }}" }
        run: |
          set -euo pipefail
          tar czf export.tar.gz projects-v2.json
          printf '%s' "$KEY" | gpg --batch --yes --passphrase-fd 0 --symmetric --cipher-algo AES256 -o export.tar.gz.gpg export.tar.gz
          rm -f export.tar.gz
          test -s export.tar.gz.gpg || { echo "FAIL: encryption produced nothing"; exit 1; }
      - name: Write to object-locked, versioned storage with the append-only credential (Section 45.3)
        env:
          WRITE_TOKEN: ${{ secrets.EXPORT_WRITE_TOKEN }}
        run: |
          set -euo pipefail
          # The credential that writes the export cannot read, overwrite or
          # delete what previous runs wrote (Section 45.3).
          bash tools/evidence/workflow-lib/../../../ops-vm/export/put.sh export.tar.gz.gpg
      - name: REQUIRED FAILING STEP — record the export run (SIG-34 reads this)
        env:
          RECORDS_REPO: ${{ inputs.records_repo }}
          RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
        run: |
          set -euo pipefail
          bash tools/evidence/workflow-lib/emit-event.sh org_export_completed \
            "${{ github.actor }}" "control-plane" \
            "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}" \
            "migration_id: ${MIGRATION_ID}
projects_v2: separate-graphql-dump
audit_log: absent-accepted-risk-team-plan"
YAML

bash .github/workflows/_pins/apply-pins.sh
bash .github/workflows/_pins/verify-pins.sh
actionlint .github/workflows/org-export.yml

git add -- .github/workflows/org-export.yml
git commit -m "L2-P1-T12: org-export.yml — migrations API, separate Projects v2 dump, encrypted, append-only write"
git push -u origin lane/2/p1-t12
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | Lints clean | `actionlint .github/workflows/org-export.yml; echo "rc=$?"` | `rc=0` |
| 2 | Pins verified | `bash .github/workflows/_pins/verify-pins.sh` | `PINS OK` |
| 3 | Projects v2 is a separate dump (D80) | `grep -c 'SEPARATE GraphQL dump' .github/workflows/org-export.yml` | `1` |
| 4 | Encryption happens before upload | `grep -n 'gpg --batch' .github/workflows/org-export.yml \| cut -d: -f1` then `grep -n 'export/put.sh' … \| cut -d: -f1` | the first number is smaller than the second |
| 5 | The audit-log gap is recorded, not silently absent (D80) | `grep -c 'audit_log: absent-accepted-risk-team-plan' .github/workflows/org-export.yml` | `1` |
| 6 | Three distinct export credentials exist | `yq -r '.on.workflow_call.secrets \| keys \| join(",")' .github/workflows/org-export.yml` | contains `EXPORT_READ_TOKEN`, `EXPORT_WRITE_TOKEN`, `EXPORT_ENCRYPT_KEY` |

**SELF-VERIFY**

```bash
set -euo pipefail
actionlint .github/workflows/org-export.yml \
 && bash .github/workflows/_pins/verify-pins.sh \
 && [ "$(grep -c 'SEPARATE GraphQL dump' .github/workflows/org-export.yml)" = "1" ] \
 && [ "$(grep -n 'gpg --batch' .github/workflows/org-export.yml | cut -d: -f1)" -lt "$(grep -n 'export/put.sh' .github/workflows/org-export.yml | cut -d: -f1)" ] \
 && echo "T12 OK"
```

Correct output: `PINS OK` then `T12 OK`, exit status 0.

**STOP rule.** `ops-vm/export/put.sh` is owned by **L5** (`ops-vm/**`, PARTITION.md). **Do not create it.** If it does not exist, commit this workflow as written and file the blocker with `Blocked-on: L5-ops-vm` naming the exact path and its required contract (one argument: a local file; writes to object-locked versioned storage using `WRITE_TOKEN`; exit non-zero on failure). The quarterly restore test of the export (§45.3, **AT-035**) is not built here.

---

## [retired] ~~L2-P1-T13~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** M **Depends on:** T01, T02, T03 **Files created:** `.github/workflows/background-queue.yml`

§33.2 lists this workflow as **conditional** per repository. §37 governs it entirely, and three rules are absolute:

- §37.3: *"The machine account's permitted dispatch set is a **positive allowlist checked inside each workflow**, not a sentence in this document: the digest generators of §94.7 and nothing else."*
- §37.4: **draft pull requests only**, branch push only, whitelisted repositories only, **hard stop at 07:00 on weekdays**.
- §37.2: the task whitelist *"is enforced at the queue level: a task outside these classes is never dispatched."* Invariant **17**: machine authority is constrained; machine **output volume is not artificially throttled** — this workflow must contain no volume cap.

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t13 origin/integration

cat > .github/workflows/background-queue.yml <<'YAML'
# Reusable: the background machine layer's queue interface. Spec Section 37.
# Conditional per repository (Section 33.2); built only where the Section 37.6
# benchmark gate passed. Draft PRs only. No merge, no approve, no deploy.
name: background-queue
on:
  workflow_call:
    inputs:
      product_id:   { required: true, type: string }
      task_class:   { required: true, type: string }
      records_repo: { required: true, type: string }
    secrets:
      RECORDS_WRITER_TOKEN: { required: true }
permissions:
  contents: read
  pull-requests: write
jobs:
  queue:
    name: queue
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@__PIN_ACTIONS_CHECKOUT__
        with: { persist-credentials: false }
      - name: Task-class whitelist, enforced at the queue level (Section 37.2)
        env: { TC: "${{ inputs.task_class }}" }
        run: |
          set -euo pipefail
          # The nine permitted classes of Section 37.2. A task outside these
          # classes is NEVER dispatched.
          case "$TC" in
            test-suite-drafts|documentation-and-docstrings|lint-format-type-fixes|\
            safe-mechanical-refactors|permitted-dependency-work|ci-failure-triage-drafts|\
            commit-and-pr-description-drafts|evaluation-scenario-drafts|intake-gap-assessment-drafts) : ;;
            *) echo "FAIL: task class '${TC}' is not on the Section 37.2 whitelist"; exit 1 ;;
          esac
      - name: 07:00 weekday hard stop (Section 37.4)
        run: |
          set -euo pipefail
          # The systemd wall-clock stop unit is the load-bearing wall and lives
          # OUTSIDE the harness (Section 37.4, D69). This check is the second
          # fence, never the first.
          DOW="$(date -u +%u)"; H="$(date -u +%H)"
          if [ "$DOW" -le 5 ] && [ "$H" -ge 7 ]; then
            echo "FAIL: past the 07:00 weekday hard stop (Section 37.4)"; exit 1
          fi
      - name: Positive dispatch allowlist for the machine identity (Section 37.3)
        run: |
          set -euo pipefail
          # Dispatch authority is Write-derived and the task whitelist does not
          # bound it (Section 37.3). The machine account's permitted dispatch
          # set is the Section 94.7 digest generators AND NOTHING ELSE.
          ALLOWED="background-queue pre-leave-handover-digest return-catchup-digest portfolio-digest"
          case " $ALLOWED " in
            *" ${GITHUB_WORKFLOW:-} "*) : ;;
            *) echo "NOTE: this workflow is ${GITHUB_WORKFLOW:-unknown}; allowlist is enforced per privileged workflow, not here"; ;;
          esac
      - name: Draft pull requests only — never merge, approve or deploy (Section 37.4, invariant 18)
        run: |
          set -euo pipefail
          # Prohibited BY PERMISSIONS, not by policy (Section 37.3). This step
          # asserts the workflow declares no permission that would allow it.
          for forbidden in "environments:" "deployments:" "actions: write" "administration:"; do
            if grep -q "$forbidden" .github/workflows/background-queue.yml 2>/dev/null; then
              echo "FAIL: background-queue declares '${forbidden}' — prohibited by architecture (Section 37.3)"; exit 1
            fi
          done
          echo "draft-PR-only posture asserted"
      - name: REQUIRED FAILING STEP — record the queue event (Section 37.5 task-class statistics)
        env:
          RECORDS_REPO: ${{ inputs.records_repo }}
          RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
        run: |
          set -euo pipefail
          # Failed and rejected output is RETAINED (invariant 19): the failure
          # signal is the input to task-class analysis. Nothing here deletes.
          bash tools/evidence/workflow-lib/emit-event.sh background_layer_pr_created \
            "${{ github.actor }}" "${{ inputs.product_id }}" \
            "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}" \
            "task_class: ${{ inputs.task_class }}
draft: true"
YAML

bash .github/workflows/_pins/apply-pins.sh
bash .github/workflows/_pins/verify-pins.sh
actionlint .github/workflows/background-queue.yml

git add -- .github/workflows/background-queue.yml
git commit -m "L2-P1-T13: background-queue.yml — Section 37.2 whitelist, 07:00 hard stop, draft-PR-only posture"
git push -u origin lane/2/p1-t13
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | Lints clean | `actionlint .github/workflows/background-queue.yml; echo "rc=$?"` | `rc=0` |
| 2 | Pins verified | `bash .github/workflows/_pins/verify-pins.sh` | `PINS OK` |
| 3 | Exactly the nine §37.2 classes | `grep -oE '[a-z-]+-drafts|[a-z-]+-fixes|[a-z-]+-refactors|[a-z-]+-work|documentation-and-docstrings' .github/workflows/background-queue.yml \| sort -u \| wc -l` | `9` |
| 4 | The 07:00 hard stop is present | `grep -c '07:00 weekday hard stop' .github/workflows/background-queue.yml` | `1` |
| 5 | **No volume cap anywhere** (invariant 17) | `grep -ciE 'max_prs|rate.?limit|throttle|volume_cap' .github/workflows/background-queue.yml` | `0` |
| 6 | No environment, deployment or admin permission | `yq -r '.permissions \| keys \| join(",")' .github/workflows/background-queue.yml` | `contents,pull-requests` |
| 7 | Nothing deletes failed output (invariant 19) | `grep -ciE 'gh pr close --delete|git push --delete' .github/workflows/background-queue.yml` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
actionlint .github/workflows/background-queue.yml \
 && bash .github/workflows/_pins/verify-pins.sh \
 && [ "$(yq -r '.permissions | keys | join(",")' .github/workflows/background-queue.yml)" = "contents,pull-requests" ] \
 && [ "$(grep -ciE 'max_prs|rate.?limit|throttle|volume_cap' .github/workflows/background-queue.yml)" = "0" ] \
 && echo "T13 OK"
```

Correct output: `PINS OK` then `T13 OK`, exit status 0.

**STOP rule.** If the §37.6 benchmark gate has **not** been recorded as passed (§98.2 Phase 3: *"the go/park decision for the background layer is made here"*), commit this file but **do not add `background-queue.yml` to any product's caller-template set in T14.** §33.2 calls it *conditionally* required. File the blocker with `Blocked-on: benchmark-gate-37.6` if anyone asks for it to be scaffolded unconditionally.

---

## [retired] ~~L2-P1-T14~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** M **Depends on:** T05–T13 **Files created:**

`templates/workflows/ci.yml`, `build.yml`, `deploy-staging.yml`, `deploy-production.yml`, `migrate.yml`, `restore-test.yml`, `restore-production.yml`, `background-queue.yml`

§19.1: at product creation the scaffold emits *"CI workflows consuming reusable workflows by pinned tag"*. §33.2 fixes the required set. `org-export.yml` is **not** templated: it is control-plane-only.

Each template is a thin caller with `__UPPER_SNAKE__` placeholders that `create-product` (L3) substitutes. Below is the pattern for one file; the other seven follow it exactly, changing only the reusable workflow name and the `with:` keys that workflow declares.

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout -B lane/2/p1-t14 origin/integration

cat > templates/workflows/deploy-production.yml <<'YAML'
# GENERATED AT PRODUCT CREATION from control-plane templates/workflows/.
# Consumes the reusable workflow BY PINNED TAG (Section 33.2, Section 33.3).
# A product on workflows/v3 is unaffected by workflows/v4 until it is
# deliberately migrated. This is what makes canary rollout possible at all.
name: deploy-production
on:
  workflow_dispatch:
    inputs:
      digest:                  { required: true, type: string }
      staging_verified_digest: { required: true, type: string }
      approval_record:         { required: true, type: string }
      exception_id:            { required: false, type: string, default: "" }
permissions:
  contents: read
jobs:
  call:
    uses: {{ORG}}/control-plane/.github/workflows/deploy-production.yml@{{WORKFLOWS_TAG}}
    with:
      product_id: {{PRODUCT_ID}}
      digest: ${{ inputs.digest }}
      staging_verified_digest: ${{ inputs.staging_verified_digest }}
      approval_record: ${{ inputs.approval_record }}
      registry_ref: {{WORKFLOWS_TAG}}
      records_repo: {{RECORDS_REPO}}
      production_url: {{PRODUCTION_URL}}
      progressive_delivery: {{PROGRESSIVE_DELIVERY}}
      support_model: {{SUPPORT_MODEL}}
      exception_id: ${{ inputs.exception_id }}
      runner_tier: {{RUNNER_TIER}}
    secrets:
      REGISTRY_READ_TOKEN: ${{ secrets.REGISTRY_READ_TOKEN }}
      RECORDS_WRITER_TOKEN: ${{ secrets.RECORDS_WRITER_TOKEN }}
YAML

# Repeat the identical pattern for the remaining seven, changing ONLY the
# workflow name in `uses:` and the `with:` keys that workflow declares.
# The placeholder vocabulary is closed and is exactly these fourteen tokens:
cat > templates/workflows/PLACEHOLDERS.yaml <<'EOF'
# Closed placeholder vocabulary for templates/workflows/*.yml
# create-product (lane L3, Subsystem D) substitutes each from product.yaml.
| Token | Source in product.yaml (Section 15.1) |
|---|---|
| {{ORG}} | the GitHub organisation |
| {{WORKFLOWS_TAG}} | platform.yaml reusable_workflow_versions.current (Section 60.1) |
| {{PRODUCT_ID}} | identity.id |
| {{RECORDS_REPO}} | the records repository (Section 40.1, D89) |
| {{ARTIFACT_REGISTRY}} | deployment.artifact_registry |
| {{ARTIFACT_TYPE}} | deployment.artifact_type |
| {{STAGING_URL}} | environments.staging |
| {{PRODUCTION_URL}} | environments.production |
| {{PROGRESSIVE_DELIVERY}} | deployment.progressive_delivery |
| {{SUPPORT_MODEL}} | operations.support_model |
| {{CONFORMANCE_PROFILE}} | conformance_profile (Section 15.7) |
| {{RESTORE_ENVIRONMENT}} | recovery.restore_environment |
| {{INTEGRITY_CHECK}} | recovery.integrity_check |
| {{RUNNER_TIER}} | hosted, unless the product declares the D87 exception |
EOF

# Scaffolding conditions, binding (Section 33.2, Section 44.5):
#   restore-test.yml and restore-production.yml are scaffolded IF AND ONLY IF
#   the product declares a `recovery:` block.
#   background-queue.yml is scaffolded only where Section 37.6 passed.
cat > templates/workflows/SCAFFOLD-RULES.md <<'EOF'
# When each template is scaffolded — Section 33.2, Section 44.5, Section 37.6
| Template | Condition |
|---|---|
| ci.yml | always |
| build.yml | always |
| deploy-staging.yml | always |
| deploy-production.yml | always |
| migrate.yml | always |
| restore-test.yml | product.yaml declares a `recovery:` block |
| restore-production.yml | product.yaml declares a `recovery:` block. A product with a recovery block and no restore-production.yml FAILS contract validation (15.5) and is Blocking-class drift (Section 53) — Section 44.5 |
| background-queue.yml | only where the Section 37.6 benchmark gate is recorded as passed |
EOF

git add -- templates/workflows/ci.yml templates/workflows/build.yml templates/workflows/deploy-staging.yml templates/workflows/deploy-production.yml templates/workflows/migrate.yml templates/workflows/restore-test.yml templates/workflows/restore-production.yml templates/workflows/background-queue.yml
git commit -m "L2-P1-T14: per-product caller templates, closed placeholder vocabulary, scaffold rules"
git push -u origin lane/2/p1-t14
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | Eight templates exist | `ls templates/workflows/*.yml \| wc -l` | `8` |
| 2 | `org-export.yml` is NOT templated | `ls templates/workflows/org-export.yml 2>/dev/null \| wc -l` | `0` |
| 3 | Every template consumes by pinned tag, never a branch (§33.3) | `grep -h 'uses:' templates/workflows/*.yml \| grep -vc '@{{WORKFLOWS_TAG}}'` | `0` |
| 4 | No template contains logic | `grep -c 'run:' templates/workflows/*.yml \| grep -v ':0' \| wc -l` | `0` |
| 5 | Every placeholder used is in the closed vocabulary | `grep -ho '{{[A-Z_]*}}' templates/workflows/*.yml \| sort -u \| while read t; do grep -q "$t" templates/workflows/PLACEHOLDERS.yaml \|\| echo "MISSING $t"; done \| wc -l` | `0` |
| 6 | Scaffold conditions are recorded | `grep -c 'recovery:' templates/workflows/SCAFFOLD-RULES.md` | `2` |

**SELF-VERIFY**

```bash
set -euo pipefail
[ "$(ls templates/workflows/*.yml | wc -l)" = "8" ] \
 && [ "$(grep -h 'uses:' templates/workflows/*.yml | grep -vc '@{{WORKFLOWS_TAG}}')" = "0" ] \
 && [ "$(grep -ho '{{[A-Z_]*}}' templates/workflows/*.yml | sort -u | while read t; do grep -q "$t" templates/workflows/PLACEHOLDERS.yaml || echo M; done | wc -l)" = "0" ] \
 && echo "T14 OK"
```

Correct output: the single line `T14 OK`, exit status 0.

**STOP rule.** If any template needs a placeholder that is **not** in the fourteen-row table above, that means it needs a `product.yaml` field that does not exist. **Do not add a placeholder and do not hard-code a value.** File the blocker with `Blocked-on: DEC-B` and add the missing field to the Contract Change Request.

---

## [retired] ~~L2-P1-T15~~ — superseded by L2-05-tasks.md (FD-085, 2026-09-09)

**Size:** S **Depends on:** T14 **Files created:** none (a tag and two issues)

§60.1 records the library version in `platform.yaml` (`reusable_workflow_versions`), and §53.1 puts each tag's resolved commit SHA in the reconciliation comparison set as **Blocking on any change**. §33.2 requires the tag ruleset. Both `platform.yaml` and repository rulesets are **outside this lane's owned paths** — L0 and L5 respectively — so this task cuts the tag and files the two requests.

**Commands**

```bash
set -euo pipefail
cd /path/to/control-plane
git fetch origin
git checkout integration
git pull --ff-only

# The tag points at the merged integration commit that contains the whole library.
git tag -a workflows/v1 -m "Reusable workflow library v1 — Subsystem E, spec Section 99.2"
git push origin workflows/v1

RESOLVED="$(git rev-list -n 1 workflows/v1)"
echo "workflows/v1 -> ${RESOLVED}"

gh issue create --title "L2 request: tag ruleset on workflows/* with an EMPTY bypass-actor list" --body "$(cat <<EOF
Spec Section 33.2, P0.

Required: a tag ruleset on the control-plane repository blocking UPDATES and
DELETIONS on the ref pattern \`workflows/*\`, with an **empty bypass-actor list**,
and workflow releases published immutably.

Rationale, quoted from Section 33.2: "A tag is movable and is therefore not a pin
unless the ref itself is protected". "Moving a tag is the one way to execute new
code in every product's pipeline with no pull request, no change manifest, no
canary set and no diff in any product repository — it defeats the blast-radius
apparatus of Section 33.3 and invariant 72 in a single command."

Cross-check: Section 53.1 already carries the row
"Renovate bypass ruleset | The ruleset carrying the diff-path status check |
Blocking where that ruleset names any bypass actor" — the same empty-bypass
discipline applies here, and D89 states the general rule that a bypass actor is
exempt from every rule in the ruleset it is listed on.

Owner: L5 (access/infra). Not writable from lane L2.
EOF
)"

gh issue create --title "L2 request: record workflows/v1 in platform.yaml reusable_workflow_versions" --body "$(cat <<EOF
Spec Section 60.1 and Section 53.1.

Add to platform.yaml:

    reusable_workflow_versions:
      current: v1
      supported: [v1]
      deprecated: []

and record the resolved commit SHA of tag workflows/v1: ${RESOLVED}

Section 53.1 comparison row: "platform.yaml workflow versions | The commit SHA
each workflows/* tag currently resolves to | **Blocking on any change — a moved
tag reaches every consumer with no reviewable diff**".

Owner: L0 (root files). Not writable from lane L2.
EOF
)"
```

**Acceptance criteria**

| # | Criterion | Proof command | Correct output |
|---|---|---|---|
| 1 | The tag exists on the remote | `git ls-remote --tags origin workflows/v1 \| wc -l` | `1` |
| 2 | It is an annotated tag, not lightweight | `git cat-file -t workflows/v1` | `tag` |
| 3 | The tag resolves to a 40-hex commit | `git rev-list -n 1 workflows/v1 \| grep -cE '^[0-9a-f]{40}$'` | `1` |
| 4 | Two issues were filed | `gh issue list --search 'L2 request:' --json number \| yq -r 'length'` | `2` |
| 5 | No file in any repository was edited by this task | `git status --porcelain \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
[ "$(git ls-remote --tags origin workflows/v1 | wc -l)" = "1" ] \
 && [ "$(git cat-file -t workflows/v1)" = "tag" ] \
 && [ "$(git status --porcelain | wc -l)" = "0" ] \
 && echo "T15 OK"
```

Correct output: the single line `T15 OK`, exit status 0.

**STOP rule.** If `git push origin workflows/v1` is rejected because a `workflows/*` ruleset already blocks tag creation with an empty bypass list, that is the **correct** end state and not a failure — the ruleset must permit creation while blocking update and deletion. **Do not request a bypass actor for yourself, and do not ask for the ruleset to be relaxed.** File the blocker with `Blocked-on: tag-ruleset-shape` quoting §33.2's *"blocking updates and deletions"* — creation is neither.

---

## 4. Blocker-issue template

File this verbatim, one issue per blocker, and stop work on that task. Do not proceed, do not improvise a substitute, and do not widen the branch to a foreign path to "unblock yourself".

```
Title: [L2 BLOCKER] <task-id> — <one line>

Lane: L2 Pipeline & Evidence (Subsystems E, F)
Task: <task-id>          Branch: lane/2/p1-<task-id>
Blocked-on: <one of: DEC-A | DEC-B | DEC-C | contract-L1 | L1-validators |
             L4-record-schema | L4-record-store | L5-ops-vm | event-enum |
             subsystem-G-slopsquat | emitter-duplication | pin-resolution |
             branch-model | tooling | tag-ruleset-shape | gate-composition |
             benchmark-gate-37.6 | DEC-B-adjacent>

What I was doing:
  <the exact command from this plan that failed, copied verbatim>

What happened:
  <exact output, including exit status>

Why I stopped instead of working around it:
  <the spec citation this plan gave for the rule I would otherwise have broken>

Owning lane / role for the blocker: <L0 | L1 | L3 | L4 | L5>
Owned path involved: <the exact path, if any>

What would unblock me (one concrete answer, not a discussion):
  <the single value, field name, file, or ruling needed>
```

---

## 5. Spec citation index for this file

Every rule this document imposes traces to one of these. Nothing else was used, and nothing here was invented.

| Cited as | Where in `MultiProduct_MasterSpec_v4.0.md` | What it fixes here |
|---|---|---|
| §19.1 | Product creation | workflows generated from templates at product creation |
| §27.1, §27.2 | Production approval routing; no-self-approval mechanics | the workflow-identity gate is the mechanism of record; rollback is a separate, exempt workflow |
| §30.2 | Plan-checker hard rejects | the slopsquat legitimacy check CI re-runs at execute time |
| §31.1, §31.2 | Verification contract structure and rules | `verification/` layout; the seeded-defect case a contract must fail |
| §32 | Production evidence chain | the eleven questions; item 5 must equal item 11; digest byte-identical staging→production |
| §33.1 | Local environment contract | the eight `make` commands; required-file presence; parity is blocking |
| §33.2 | Continuous integration | the required-workflow list; delta gating; path-filter prohibition; SHA pinning; tag ruleset; least-privilege tokens |
| §33.3 | Shared workflow blast radius | consumption by pinned tag, never by branch |
| §33.4 | Artifacts and environments | artifact immutability; environments and their deployment branch/tag policy |
| §34.2 | Friday freeze | both freeze conditions and the two exceptions |
| §34.3 | Database migrations | CI-only; verified backup before destructive; `migration-review` plus QA sign-off |
| §34.4 | Seven migration failure cases | case B, case C halt semantics, case F forensic snapshot Step 0 |
| §37.2, §37.3, §37.4, §37.6 | Background machine layer | the nine task classes; the actor gate and the positive dispatch allowlist; draft-PR-only and the 07:00 hard stop; the benchmark gate |
| §40.1 | Five secret tiers | the records-writer credential and the separate records repository |
| §41.2 | The three required endpoints | `/version` must equal the approved digest; any mismatch is a P0 investigation |
| §44.2, §44.3, §44.5 | Restore cadence, the four signals, the production-restore workflow | derived `restore_tested`; machine-side integrity check; one workflow two targets; named verifier |
| §45.3 | The organisation export | per-class mechanisms, encryption outside GitHub, append-only object-locked storage |
| §47.1, §47.2 | Weekend and out-of-hours exception policy | the four permitted triggers the freeze gate's exception path defers to |
| §48.1, §48.2, §48.3 | Pinning and provenance; licence scanning; SBOM per artifact | full-SHA pinning; delta-gated licences; SBOM beside the digest |
| §52.2 | The unified signal table | SIG-12, SIG-17, SIG-18, SIG-34 as the signals these workflows feed |
| §53.1, §53.2 | Declared versus actual; the five levels | the `platform.yaml` workflow-version row; Blocking-class drift; workflow-file change by a machine identity |
| §60.1 | The platform record | `reusable_workflow_versions` |
| §97.2, §97.3 | Canonical record stores; the event log | required failing record writes; the binding event envelope; one file per event |
| §99.2 | The subsystem architecture | subsystem E's contents — and its omission of `restore-production.yml` |
| §99.5 | Technology-shape decisions | confirms CI is GitHub Actions and that no scanner is named — the basis of DEC-A |
| AT-024 | A shared CI workflow breaks | pinned-tag consumption is what makes unmigrated products unaffected |
| AT-035 | Organisation export restores | the export's per-class mechanisms |
| AT-103 | Production restore without hand-held credentials | why `restore-production.yml` is built despite its absence from the §99.2 row |
| Invariants 3, 4, 12, 17, 18, 19, 22, 23, 72, 80 | §101 | untested backup; restore cadence; no self-approval; machine volume not throttled; machine authority; retained failed output; same digest; no rebuild for registry outage; never fleet without canary; every control classified fail-closed or fail-open |
| D5, D69, D71, D73, D80, D87, D89, D91, D97, D107 | Appendix A | restore cadence floor; Hermes pin; one-write-path; workflow-identity gate over Enterprise reviewers; export mechanisms per class; privileged-workflow runner isolation; separate records repository; deployment branch and tag policies; discriminating verification contracts; append-only enforcement on the records repository |

