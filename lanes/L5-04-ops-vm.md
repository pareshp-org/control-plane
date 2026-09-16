<!-- Task IDs renamed to charter format L5-FF-TT by Session 12 (FD-037 corollary) -->
> **[AUTHORITATIVE — FD-B1-L5 2026-09-02]**
> This is the authoritative task plan for Lane 5. All competing plans are superseded.

# L5 — PHASE 4: THE OPERATIONS VM AND ESTATE

**Lane:** L5 Access, Infra & Ops · **Subsystems:** M (Operations VM), with the estate-side parts of Q (asset inventory) and R (notification routing) that the VM depends on · Spec Section 99.2.
**Owned paths used by this file (exclusively L5, per the FROZEN `PARTITION.md`):** `ops-vm/**`, `infra/**`, `assets/**`, `notify/**`.
**Repository:** `control-plane` (see PARTITION "Repositories"). No task in this file writes `control-plane-records`, `.github/workflows/**`, `reconciler/**`, `registries/**`, `schemas/**`, `metrics/**`, `contracts/**`, `docs/**`, `CODEOWNERS`, `Makefile` or any root file. Where Phase 4 output must land in a foreign path, the task ends in a **handoff issue**, never an edit (PARTITION rule 2 and rule 4).

---

## 0. What this phase builds and why

Section 51.5 makes the operations VM **deliberately disposable**: everything it runs is provisioned from the control-plane repository, everything durable it stores is backed up on the product discipline, and its complete loss is a tested under-4-hour rebuild (Section 45.4), not a catastrophe. Subsystem M's line in the Section 99.2 table is the scope: *"DevLake, Grafana, reconciliation, health computation, Scorecard, Renovate, expiry checks, restore rotation, org export; disposable (rebuild under 4 hours from GitHub, tested quarterly); never in any product's runtime path; patched on the declared cadence."*

Four things this phase must not get wrong, each stated by the spec and each carried by named tasks below:

| Requirement | Spec | Tasks |
| --- | --- | --- |
| Rebuild is a **replay** of the control-plane repository, not an operator's memory. Under 4 hours, clock from provision-start to dashboards-green **including the Layer B restore**; drilled quarterly; the runbook is executed *as written* and an omitted step is a test failure | 45.4, 51.5 | T16, T17 |
| Patch cadence with **elevated Layer B priority** and the **post-patch smoke checklist**; the singleton shape `snapshot → upgrade → verify → revert-on-fail`; staleness feeds SIG-36 | 51.4, 62.1, 52.2 | T15 |
| **Private network path** (VPN or mesh) with SSO in front of every control-plane surface; no public exposure, including the Founder's phone access | 51.4 | T02 |
| **D94 external dead-man switch** — off the VM, outside GitHub and outside the product providers — because Section 45.2's earlier claim of responder-source independence was false: Prometheus, Grafana alerting and health computation all die with the host | D94, 45.2, 51.5, 46.6 (Monitoring stack unavailable), 51.2 | T14 |

Plus the estate the VM must never absorb: the **self-hosted runner estate** (Section 49.1 — no runner is ever located on the operations VM, because Section 45.2's "CI keeps running" depends on that placement) and the **D87 privileged/build pool separation**.

Two invariants bound every task here: **75/76** — the control plane observes products and is never in their runtime path (Section 51.3) — and **47** — history is append-only. Every job this phase provisions writes its result; a clean run is recorded as clean (Section 53.1).

---

## 1. Conventions every task in this file obeys

### 1.1 Environment

Run every command block from a POSIX shell (Git Bash on Windows is fine). Set these once per session:

```bash
set -euo pipefail
export CONTROL_PLANE_ROOT="$HOME/work/control-plane"     # local clone of the control-plane repository
export LANE="5"
export PHASE="04"
cd "$CONTROL_PLANE_ROOT"
git --version && gh --version && python3 --version
python3 -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 12) else 1)" \
  || { echo "STOP: Python 3.12 required (FD-005); got $(python3 --version 2>&1)"; exit 1; }
```

If any of `git`, `gh` or `python3` is missing, **STOP** and open a blocker issue (template in §1.4).

### 1.2 Branch, commit and PR shape — identical for every task

Replace `<TID>` with the lowercase task id (e.g. `t01`) and `<slug>` with the slug named in the task.

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b "lane/${LANE}/${PHASE}-<TID>-<slug>"
```

After the files are created and the SELF-VERIFY block passes:

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add <exact paths listed in the task, no wildcards outside them>
git commit -m "L5-04-<TID>: <task title>"
git push -u origin "lane/${LANE}/${PHASE}-<TID>-<slug>"
gh pr create --base integration \
  --title "L5-04-<TID>: <task title>" \
  --body "Lane L5 phase 4 task L5-04-<TID>. Paths: ops-vm/**, infra/**, assets/**, notify/** only. Spec: <sections cited in the task>."
```

**Lane-guard rule (PARTITION rule 1):** if `git status --porcelain` shows any staged path outside `ops-vm/`, `infra/`, `assets/`, `notify/`, **do not push**. Unstage it and STOP.

```bash
set -euo pipefail
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
```
Expected output: `PATHS OK`

### 1.3 Rebase before PR

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git rebase origin/integration
git push --force-with-lease
```

### 1.4 Blocker-issue template — used by every STOP rule

When a STOP rule fires, do not improvise, do not choose a value, do not proceed to the next task. Open this issue and stop work on the task:

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
gh issue create \
  --title "BLOCKER L5-04-<TID>: <one-line symptom>" \
  --label "blocker,lane-5,phase-4" \
  --body "$(cat <<'BLOCKER'
## Task
L5-04-<TID> — <task title>

## STOP rule that fired
<quote the exact STOP rule text from the task>

## What I ran
```
<the exact command>
```

## What I got
```
<verbatim output>
```

## What the task expected
<quote the expected output from the SELF-VERIFY block>

## Decision required from L0
<one sentence naming the single missing fact, value or approval — no proposed answer>

## Blocked tasks
<task ids that declare this task as a dependency>
BLOCKER
)"
```

Then post the issue URL as a comment on the lane's phase-4 tracking issue and **stop**. A lane task never designs, chooses or interprets (PARTITION §"AI developer profile").

### 1.5 Dependency id convention

* Intra-file dependencies are given as `L5-04-Tnn`.
* Cross-phase dependencies inside lane L5 are given as the phase gate id `L5-01-COMPLETE`, `L5-02-COMPLETE`, `L5-03-COMPLETE` — meaning *every task in that lane phase file has merged to `integration`*.
* Cross-lane dependencies are given as `L0-P0-CONTRACTS` (contracts frozen by L0 in Phase 0), `L1-COMPLETE`, `L2-COMPLETE`, `L3-COMPLETE`, `L4-COMPLETE`, each meaning that lane's merge into `integration` on the current merge train (PARTITION "Merge train": L1 → L4 → L2 → L3 → L5).

### 1.6 Values this phase never invents

Every one of the following is **calibrated configuration or a named decision** in the spec, not a value an executor picks. Each appears in this phase only as an **empty key in a `.example` file** plus a STOP rule that fires when the real file is absent or the key is empty:

| Value | Spec home |
| --- | --- |
| The private-network mechanism (VPN or mesh) and the SSO provider in front of it | 51.4 — "decided and implemented at Phase 2"; network exposure of any control-plane surface is a named security decision with the Founder as decider |
| The designated messaging channel | 92.11 — "a configuration value, never a hard-coded destination" |
| The dead-man watchdog provider and the second-host location | 51.5, D94 — must be outside the VM, outside GitHub, outside the product providers |
| Object-lock storage provider, bucket and retention for the org export and the Layer B backup | 45.3, 51.4 — a different provider and credential domain |
| Encryption-key custody | 45.3, 45.4, 14.4 escrow |
| Patch cadence values per component | 51.4, 62.1 — declared in the tool register |
| Alert lead times on inventory entries | 49.1 — "at least 30 days"; 49.2 — configurable lead, owner-set at entry creation |
| Runner estate hosts, owners, cost bands and site/power/network dependencies | 49.1, 46.6 (CI execution estate outage) |

---

## 2. Task index

| Task | Title | Size | Depends on |
| --- | --- | --- | --- |
| L5-04-01 | Ops-VM tree, pinned component manifest and shared shell library | S | L0-P0-CONTRACTS |
| L5-04-02 | Base provisioning, the private network path and the SSO front door | M | T01 |
| L5-04-03 | Shared stack compose: Grafana, Prometheus, DevLake | M | T01, T02 |
| L5-04-04 | Grafana provisioning from git: datasource, dashboard provider, stack dashboard | M | T03 |
| L5-04-05 | Layer B second Grafana instance: host placement and encryption at rest | M | T03, L5-02-COMPLETE |
| L5-04-06 | Layer B backup: append-only credential to object-locked storage | M | T05 |
| L5-04-07 | Reconciliation host: units, credential store, freshness telemetry | M | T03, L3-COMPLETE |
| L5-04-08 | Health computation job and report freshness | S | T04, T07, L4-COMPLETE |
| L5-04-09 | Scorecard scheduled scan runner | S | T03 |
| L5-04-10 | Renovate self-hosted runner | M | T03 |
| L5-04-11 | Asset inventory store and the expiry-check job | M | T01, T03 |
| L5-04-12 | Restore-rotation scheduler | S | T03, L2-COMPLETE |
| L5-04-13 | Organisation export runner and staleness telemetry | L | T03, T11 |
| L5-04-14 | D94 external dead-man switch and the off-VM liveness leg | L | T04, T11, L5-03-COMPLETE |
| L5-04-15 | Patch cadence, singleton patch driver and the post-patch smoke checklist | L | T04, T05, T07, T14 |
| L5-04-16 | Rebuild driver, step manifest and the generated runbook | L | T02–T13, T15 |
| L5-04-17 | Quarterly rebuild drill: 4-hour clock, VM-stop verification, zero-resources evidence | L | T14, T16 |
| L5-04-18 | Self-hosted runner estate: groups, placement rule, inventory entries | M | T11 |
| L5-04-19 | D87 privileged/build pool separation and its three Blocking drift checks | L | T18 |

---

## L5-04-01 — Ops-VM tree, pinned component manifest and shared shell library

**Size:** S · **Depends on:** L0-P0-CONTRACTS · **Slug:** `layout`
**Spec:** 51.5 (everything the VM runs is provisioned from the control-plane repository), 45.1 (minimum reconstruction set), invariant 85 (pinning), invariant 79 (minimum privilege by default).

Create the directory tree, the single pinned-version manifest every later task reads, and the shared shell library. **No component version is chosen here** — the manifest ships with empty values and a STOP rule.

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/README.md` | What the VM is, what it is not, and the invariants it obeys |
| `ops-vm/stack/versions.env.example` | Pinned image digests for every stack component (empty values) |
| `ops-vm/stack/network.env.example` | Private-path and SSO keys (empty values) — consumed by T02 |
| `ops-vm/lib/common.sh` | `require_env`, `require_file`, `log`, `record_run`, `fail_closed` |
| `ops-vm/checks/versions-pinned.sh` | Fails when any component is unpinned or pinned by tag alone |
| `ops-vm/.gitignore` | Keeps real `versions.env` / `network.env` out of git |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t01-layout"
mkdir -p ops-vm/stack ops-vm/lib ops-vm/checks ops-vm/jobs ops-vm/systemd ops-vm/provision
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/README.md <<'MDDOC'
# Operations VM

Subsystem M (spec Section 99.2). Runs: DevLake, Grafana, reconciliation, health
computation, Scorecard, Renovate, expiry checks, restore rotation, org export.

Binding rules, taken from the specification — none is negotiable here:

* Disposable. Everything on this host is provisioned from this repository. Its
  complete loss is a tested under-4-hour rebuild (Section 45.4), not a
  catastrophe (Section 51.5).
* Never in a product runtime path. Invariants 75 and 76; Section 51.3.
* No production credentials, no deploy keys, no environment access. It does hold
  the fifth-tier machine-credential store of Section 40.1 - the reconciler
  credential and the organisation-export token among them - which is why shell
  access to this host is not an infrastructure detail (Section 40.3).
* Not its own witness. Prometheus, alert evaluation and Grafana all die with the
  host, so machine detection carries an off-VM leg: the external per-product
  uptime check and the dead-man's-switch heartbeat of Section 51.5 and D94.
* No CI runner lives here (Section 49.1): Section 45.2's "CI keeps running when
  the VM is lost" depends on that placement.
* The background machine layer does not run here. It has its own dedicated host
  (Section 37) and the two hosts share no credentials (Section 51.5).
MDDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/stack/versions.env.example <<'ENVDOC'
# Pinned component versions for the operations VM stack.
# Every *_DIGEST is a full image digest (sha256:...), never a floating tag.
# Invariant 85. Values come from the L0 platform record; never chosen here.
GRAFANA_IMAGE=
GRAFANA_DIGEST=
PROMETHEUS_IMAGE=
PROMETHEUS_DIGEST=
DEVLAKE_IMAGE=
DEVLAKE_DIGEST=
DEVLAKE_DB_IMAGE=
DEVLAKE_DB_DIGEST=
DEVLAKE_CONFIGUI_IMAGE=
DEVLAKE_CONFIGUI_DIGEST=
GRAFANA_LAYERB_IMAGE=
GRAFANA_LAYERB_DIGEST=
PROXY_IMAGE=
PROXY_DIGEST=
ENVDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/stack/network.env.example <<'ENVDOC'
# Private network path and SSO front door (Section 51.4).
# Mechanism and provider are a named security decision with the Founder as
# decider. An implementer never fills this file.
PRIVATE_PATH_MECHANISM=
PRIVATE_PATH_INTERFACE=
PRIVATE_PATH_CIDR=
PRIVATE_PATH_BIND_ADDR=
SSO_PROVIDER=
SSO_ISSUER_URL=
SSO_CLIENT_ID=
SSO_CLIENT_ID_LAYERB=
OPS_VM_DOMAIN=
OPS_VM_DECISION_RECORD=
ENVDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/lib/common.sh <<'SHDOC'
#!/usr/bin/env bash
# Shared library for every operations-VM job. Fail closed (invariant 80).
set -euo pipefail

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >&2; }

fail_closed() { log "FAIL-CLOSED: $*"; exit 1; }

require_env() {
  local missing=0 k
  for k in "$@"; do
    if [ -z "${!k:-}" ]; then log "missing required key: $k"; missing=1; fi
  done
  [ "$missing" -eq 0 ] || fail_closed "required configuration is absent"
}

require_file() { [ -f "$1" ] || fail_closed "required file absent: $1"; }

# Every job writes its result; a clean run is recorded as clean (Section 53.1).
record_run() {
  local job="$1" status="$2" detail="${3:-}"
  local out="${OPS_VM_RUN_DIR:-/var/lib/ops-vm/runs}"
  mkdir -p "$out"
  printf 'job: %s\nstatus: %s\nat: %s\nhost: %s\ndetail: %s\n' \
    "$job" "$status" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(hostname)" "$detail" \
    > "$out/$(date -u +%Y%m%dT%H%M%SZ)-$job.yaml"
}
SHDOC
chmod +x ops-vm/lib/common.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/versions-pinned.sh <<'SHDOC'
#!/usr/bin/env bash
# Every stack component is pinned by digest. Invariant 85.
set -euo pipefail
ENVFILE="${1:-ops-vm/stack/versions.env}"
[ -f "$ENVFILE" ] || { echo "VERSIONS-PINNED: FAIL (no $ENVFILE)"; exit 1; }
bad=0
while IFS='=' read -r k v; do
  case "$k" in
    ''|\#*) continue ;;
    *_DIGEST) case "$v" in sha256:*) ;; *) echo "unpinned: $k"; bad=1 ;; esac ;;
    *_IMAGE)  [ -n "$v" ] || { echo "empty: $k"; bad=1; } ;;
  esac
done < "$ENVFILE"
if [ "$bad" -eq 0 ]; then echo "VERSIONS-PINNED: PASS"; else echo "VERSIONS-PINNED: FAIL"; exit 1; fi
SHDOC
chmod +x ops-vm/checks/versions-pinned.sh
printf 'stack/versions.env\nstack/network.env\n' > ops-vm/.gitignore
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add ops-vm/README.md ops-vm/stack/versions.env.example ops-vm/stack/network.env.example ops-vm/lib/common.sh ops-vm/checks/versions-pinned.sh ops-vm/.gitignore
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-01: ops-vm layout, pinned component manifest and shared shell library"
git push -u origin "lane/5/04-t01-layout"
gh pr create --base integration --title "L5-04-01: ops-vm layout and pinned component manifest" --body "Lane L5 phase 4 task L5-04-01. Paths: ops-vm/** only. Spec: 51.5, 45.1, invariants 79, 85."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | The six files exist | `ls ops-vm/README.md ops-vm/stack/versions.env.example ops-vm/stack/network.env.example ops-vm/lib/common.sh ops-vm/checks/versions-pinned.sh ops-vm/.gitignore \| wc -l` | `6` |
| 2 | `common.sh` parses | `bash -n ops-vm/lib/common.sh && echo SYNTAX-OK` | `SYNTAX-OK` |
| 3 | The pin checker rejects an empty manifest | `ops-vm/checks/versions-pinned.sh ops-vm/stack/versions.env.example; echo "rc=$?"` | last two lines `VERSIONS-PINNED: FAIL` then `rc=1` |
| 4 | The pin checker accepts a fully pinned manifest | SELF-VERIFY line 1 | `VERSIONS-PINNED: PASS` |
| 5 | No real env file is tracked | `git ls-files ops-vm/stack \| grep -Ec '^ops-vm/stack/(versions|network)\.env$'` | `0` |
| 6 | No foreign path staged | `git diff --cached --name-only \| grep -Evc '^(ops-vm|infra|assets|notify)/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
sed -e 's|^\(.*_IMAGE\)=$|\1=example/img|' \
    -e 's|^\(.*_DIGEST\)=$|\1=sha256:0000000000000000000000000000000000000000000000000000000000000000|' \
    ops-vm/stack/versions.env.example > /tmp/v-full.env
ops-vm/checks/versions-pinned.sh /tmp/v-full.env
ops-vm/checks/versions-pinned.sh ops-vm/stack/versions.env.example || echo "empty-manifest-rejected"
bash -n ops-vm/lib/common.sh && echo SYNTAX-OK
git ls-files ops-vm/stack | grep -Ec '^ops-vm/stack/(versions|network)\.env$'
```

Expected output — first line, then the `empty:`/`FAIL` block, then the last three lines exactly:

```
VERSIONS-PINNED: PASS
empty: GRAFANA_IMAGE
... (one "empty:" line per *_IMAGE key, then "unpinned:" per *_DIGEST key)
VERSIONS-PINNED: FAIL
empty-manifest-rejected
SYNTAX-OK
0
```

### STOP rule

If the repository already contains a tracked `ops-vm/stack/versions.env` or `ops-vm/stack/network.env` with real values, **do not read, copy, edit or delete it**: a tracked `network.env` means credentials or a network topology are in git. STOP and open a blocker (§1.4) with the decision line: *"A real ops-vm env file is tracked in git; Section 40.1 forbids secret values in the repository and L0 must decide the removal and rotation path."*

---

## L5-04-02 — Base provisioning, the private network path and the SSO front door

> **BLOCKED-PENDING-E-08 (FD-063):** private-path value is set at Phase 1 deployment.
> This task cannot proceed until the deployment configuration establishes the private-path.
> Resolution: set `PRIVATE_PATH` env var or equivalent at deployment time.

**Size:** M · **Depends on:** L5-04-01 · **Slug:** `private-path`
**Spec:** 51.4 — every control-plane surface (Grafana, Layer B, the restricted record stores) is reachable **only over a private network path (VPN or mesh) with SSO in front of it**; the Founder's phone access uses the same private path, never a public exposure; network exposure of any control-plane surface is a **named security decision with the Founder as decider**, recorded like any other decision. Also 40.3 (second trust boundary), invariant 80 (fail-closed), 45.1 (infrastructure definitions are in the reconstruction set).

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/provision/00-base.sh` | Idempotent host base: service user, state dirs, firewall default-deny |
| `ops-vm/provision/10-private-path.sh` | Brings up the mechanism named in `network.env`; refuses to guess one |
| `ops-vm/provision/20-sso-proxy.sh` | Renders and restarts the SSO reverse proxy from the template |
| `ops-vm/proxy/proxy.conf.tmpl` | Reverse-proxy template: every upstream behind SSO, bound to the private address |
| `ops-vm/checks/no-public-listener.sh` | Fails if any stack port is bound to a wildcard address |
| `ops-vm/checks/sso-in-front.sh` | Fails if any surface answers an unauthenticated request |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t02-private-path"
mkdir -p ops-vm/provision ops-vm/proxy ops-vm/checks
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/provision/00-base.sh <<'SHDOC'
#!/usr/bin/env bash
# Idempotent host base. Re-runnable: a rebuild is a replay, not a fresh design.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"

log "base: service user and state directories"
id ops-vm >/dev/null 2>&1 || useradd --system --home /var/lib/ops-vm --shell /usr/sbin/nologin ops-vm
install -d -o ops-vm -g ops-vm -m 0750 /var/lib/ops-vm /var/lib/ops-vm/runs
install -d -o ops-vm -g ops-vm -m 0700 /var/lib/ops-vm/creds

log "base: firewall default-deny inbound (invariant 80, fail closed)"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw --force enable
log "base: no port opened here; ports are opened only by 10-private-path.sh"
record_run base ok "host base applied"
SHDOC
chmod +x ops-vm/provision/00-base.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/provision/10-private-path.sh <<'SHDOC'
#!/usr/bin/env bash
# Private network path. The mechanism is a recorded decision, never a default.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/stack/network.env
set -a; . ops-vm/stack/network.env; set +a
require_env PRIVATE_PATH_MECHANISM PRIVATE_PATH_INTERFACE PRIVATE_PATH_CIDR OPS_VM_DECISION_RECORD

case "$PRIVATE_PATH_MECHANISM" in
  vpn|mesh) ;;
  *) fail_closed "PRIVATE_PATH_MECHANISM must be 'vpn' or 'mesh' from the recorded decision; got '$PRIVATE_PATH_MECHANISM'" ;;
esac

log "private-path: admitting 443 on $PRIVATE_PATH_INTERFACE from $PRIVATE_PATH_CIDR only"
ufw allow in on "$PRIVATE_PATH_INTERFACE" from "$PRIVATE_PATH_CIDR" to any port 443 proto tcp
systemctl enable --now "ops-vm-${PRIVATE_PATH_MECHANISM}.service"
record_run private-path ok "mechanism=$PRIVATE_PATH_MECHANISM decision=$OPS_VM_DECISION_RECORD"
SHDOC
chmod +x ops-vm/provision/10-private-path.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/proxy/proxy.conf.tmpl <<'TMPLDOC'
# Rendered by 20-sso-proxy.sh. Every control-plane surface sits behind SSO and
# binds to the private address only (Section 51.4). Publishing an upstream on a
# public address is a named security decision, not an edit to this file.
bind ${PRIVATE_PATH_BIND_ADDR}

grafana.${OPS_VM_DOMAIN} {
  sso { issuer ${SSO_ISSUER_URL}; client_id ${SSO_CLIENT_ID} }
  reverse_proxy 127.0.0.1:3000
}

layerb.${OPS_VM_DOMAIN} {
  # Founder-only instance (Section 90, D75). Separately credentialed: a shared
  # instance session grants nothing here (AT-098).
  sso { issuer ${SSO_ISSUER_URL}; client_id ${SSO_CLIENT_ID_LAYERB} }
  reverse_proxy 127.0.0.1:3001
}

devlake.${OPS_VM_DOMAIN} {
  sso { issuer ${SSO_ISSUER_URL}; client_id ${SSO_CLIENT_ID} }
  reverse_proxy 127.0.0.1:4000
}
TMPLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/provision/20-sso-proxy.sh <<'SHDOC'
#!/usr/bin/env bash
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/stack/network.env
set -a; . ops-vm/stack/network.env; set +a
require_env SSO_PROVIDER SSO_ISSUER_URL SSO_CLIENT_ID SSO_CLIENT_ID_LAYERB OPS_VM_DOMAIN PRIVATE_PATH_BIND_ADDR
case "$PRIVATE_PATH_BIND_ADDR" in
  0.0.0.0|::|"") fail_closed "PRIVATE_PATH_BIND_ADDR must be the private interface address, never a wildcard" ;;
esac
install -d -m 0750 /etc/ops-vm
envsubst < ops-vm/proxy/proxy.conf.tmpl > /etc/ops-vm/proxy.conf
systemctl restart ops-vm-proxy.service
record_run sso-proxy ok "provider=$SSO_PROVIDER"
SHDOC
chmod +x ops-vm/provision/20-sso-proxy.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/no-public-listener.sh <<'SHDOC'
#!/usr/bin/env bash
# No control-plane surface listens on a wildcard address (Section 51.4).
set -euo pipefail
bad=$(ss -Hltn 2>/dev/null | awk '{print $4}' | grep -E '^(0\.0\.0\.0|\[::\]):(443|3000|3001|4000|9090|8080)$' || true)
if [ -n "$bad" ]; then echo "PUBLIC-LISTENER: FAIL"; echo "$bad"; exit 1; fi
echo "PUBLIC-LISTENER: PASS"
SHDOC
chmod +x ops-vm/checks/no-public-listener.sh

cat > ops-vm/checks/sso-in-front.sh <<'SHDOC'
#!/usr/bin/env bash
# Every surface refuses an unauthenticated request. Fail closed (invariant 80).
set -euo pipefail
rc=0
for u in "$@"; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$u" || echo 000)
  case "$code" in
    302|303|401|403) echo "$u -> $code OK" ;;
    *) echo "$u -> $code NOT-GATED"; rc=1 ;;
  esac
done
if [ "$rc" -eq 0 ]; then echo "SSO-IN-FRONT: PASS"; else echo "SSO-IN-FRONT: FAIL"; exit 1; fi
SHDOC
chmod +x ops-vm/checks/sso-in-front.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add ops-vm/provision ops-vm/proxy ops-vm/checks/no-public-listener.sh ops-vm/checks/sso-in-front.sh
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-02: base provisioning, private network path and SSO front door"
git push -u origin "lane/5/04-t02-private-path"
gh pr create --base integration --title "L5-04-02: private network path and SSO front door" --body "Lane L5 phase 4 task L5-04-02. Paths: ops-vm/** only. Spec: 51.4, 40.3, invariant 80."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Every script parses | `for f in ops-vm/provision/*.sh ops-vm/checks/no-public-listener.sh ops-vm/checks/sso-in-front.sh; do bash -n "$f" \|\| exit 1; done; echo ALL-PARSE-OK` | `ALL-PARSE-OK` |
| 2 | The private-path script refuses an unnamed mechanism | SELF-VERIFY step 2 | `FAIL-CLOSED: PRIVATE_PATH_MECHANISM must be 'vpn' or 'mesh' …` then `rc=1` |
| 3 | The template binds no wildcard | `grep -Ec '0\.0\.0\.0|\[::\]' ops-vm/proxy/proxy.conf.tmpl` | `0` |
| 4 | All three upstreams are behind SSO | `grep -c '^  sso {' ops-vm/proxy/proxy.conf.tmpl` | `3` |
| 5 | Upstream count equals SSO-block count | `grep -c 'reverse_proxy' ops-vm/proxy/proxy.conf.tmpl` | `3` |
| 6 | `network.env.example` still carries no value | `grep -Ec '^[A-Z_]+=.+$' ops-vm/stack/network.env.example` | `0` |
| 7 | The public-listener check fails on a wildcard bind | SELF-VERIFY step 4 (host only) | `PUBLIC-LISTENER: FAIL` then `rc=1` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for f in ops-vm/provision/*.sh ops-vm/checks/no-public-listener.sh ops-vm/checks/sso-in-front.sh; do bash -n "$f" || exit 1; done; echo ALL-PARSE-OK
rm -rf /tmp/t02 && mkdir -p /tmp/t02/ops-vm/stack /tmp/t02/ops-vm/lib
cp "$CONTROL_PLANE_ROOT/ops-vm/lib/common.sh" /tmp/t02/ops-vm/lib/
cp "$CONTROL_PLANE_ROOT/ops-vm/stack/network.env.example" /tmp/t02/ops-vm/stack/network.env
printf 'PRIVATE_PATH_MECHANISM=guess\nPRIVATE_PATH_INTERFACE=eth0\nPRIVATE_PATH_CIDR=10.0.0.0/24\nOPS_VM_DECISION_RECORD=records/decisions/x.yaml\n' >> /tmp/t02/ops-vm/stack/network.env
( cd /tmp/t02 && bash "$CONTROL_PLANE_ROOT/ops-vm/provision/10-private-path.sh"; echo "rc=$?" )
grep -Ec '0\.0\.0\.0|\[::\]' ops-vm/proxy/proxy.conf.tmpl
grep -c '^  sso {' ops-vm/proxy/proxy.conf.tmpl
grep -c 'reverse_proxy' ops-vm/proxy/proxy.conf.tmpl
grep -Ec '^[A-Z_]+=.+$' ops-vm/stack/network.env.example
```

Expected output:

```
ALL-PARSE-OK
<timestamp> FAIL-CLOSED: PRIVATE_PATH_MECHANISM must be 'vpn' or 'mesh' from the recorded decision; got 'guess'
rc=1
0
3
3
0
```

Step 4, on the provisioned host only, after T03 has started the stack:

```bash
set -euo pipefail
python3 -m http.server 3000 --bind 0.0.0.0 >/dev/null 2>&1 & sleep 1
ops-vm/checks/no-public-listener.sh; echo "rc=$?"
kill %1
```
Expected: `PUBLIC-LISTENER: FAIL` … then `rc=1`.

### STOP rule

`ops-vm/stack/network.env` is never created by this task. If the host has no `network.env`, or `OPS_VM_DECISION_RECORD` is empty, or `PRIVATE_PATH_MECHANISM` is neither `vpn` nor `mesh`, or `PRIVATE_PATH_BIND_ADDR` is a wildcard: **do not choose a mechanism, do not open a port, do not proceed to T03.** Open a blocker (§1.4) with the decision line: *"Section 51.4 requires the private-path mechanism and the SSO provider to be a named security decision with the Founder as decider; no such decision record is present."*

---

## L5-04-03 — Shared stack compose: Grafana, Prometheus

**Size:** M · **Depends on:** L5-04-01, L5-04-02 · **Slug:** `stack-compose`
**Spec:** 99.5 (Grafana + DevLake + Prometheus, self-hosted on the operations VM, dashboards as provisioned JSON; confirm DevLake's required database engine and version for the pinned release before install — it determines the compose file and the control-plane backup procedure), 51.5 (metrics volume is backed up on the product discipline), 45.1 (DevLake configuration is in the reconstruction set), invariant 85.

**FD-112 (2026-09-08, PFD-032):** DevLake is deferred from V1 scope. This task's build scope is reduced to Grafana + Prometheus (3 services: proxy, grafana, prometheus) — no DevLake service blocks, no DevLake DB engine/version declaration, no `devlake-db-declared.sh` check. Re-adding DevLake to this file is gated on the trigger condition recorded in `contracts/v1-scope.yaml` (`devlake.trigger: to_be_determined_by_L0`) — an explicit future L0 decision, not something this task or a later rebuild does on its own.

Every service binds to `127.0.0.1` only; the SSO proxy from T02 is the sole ingress.

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/stack/compose.shared.yml` | The shared (Layer A) stack: proxy, Grafana, Prometheus (FD-112: DevLake deferred) |
| `ops-vm/prometheus/prometheus.yml.tmpl` | Scrape config template for `/health`, `/version`, `/metrics` |
| `ops-vm/provision/30-stack-up.sh` | Renders config, pulls by digest, brings the stack up |
| `ops-vm/checks/stack-loopback-only.sh` | Fails if any published port is not on `127.0.0.1` |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t03-stack-compose"
mkdir -p ops-vm/prometheus
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/stack/compose.shared.yml <<'YAMLDOC'
# Shared (Layer A) operations-VM stack. Provisioned from this repository only.
# Every port is published on 127.0.0.1; the SSO proxy of T02 is the sole ingress
# and it binds to the private address (Section 51.4).
# FD-112/PFD-032 (2026-09-08): DevLake deferred from V1 scope, not included here.
# Trigger for re-adding: contracts/v1-scope.yaml devlake.trigger (to_be_determined_by_L0).
name: ops-vm-shared

services:
  proxy:
    image: ${PROXY_IMAGE}@${PROXY_DIGEST}
    restart: always
    network_mode: host
    volumes:
      - /etc/ops-vm/proxy.conf:/etc/proxy/proxy.conf:ro

  grafana:
    image: ${GRAFANA_IMAGE}@${GRAFANA_DIGEST}
    restart: always
    ports: ["127.0.0.1:3000:3000"]
    environment:
      GF_SERVER_HTTP_ADDR: "127.0.0.1"
      GF_USERS_ALLOW_SIGN_UP: "false"
      GF_AUTH_ANONYMOUS_ENABLED: "false"
    volumes:
      - grafana-data:/var/lib/grafana
      - ../grafana/provisioning:/etc/grafana/provisioning:ro
      - ../grafana/dashboards:/var/lib/grafana/dashboards:ro

  prometheus:
    image: ${PROMETHEUS_IMAGE}@${PROMETHEUS_DIGEST}
    restart: always
    ports: ["127.0.0.1:9090:9090"]
    volumes:
      - /etc/ops-vm/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus

volumes:
  grafana-data:
  prometheus-data:
YAMLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/prometheus/prometheus.yml.tmpl <<'YAMLDOC'
# Prometheus scrapes the three required endpoints of Section 41.2 across the
# portfolio. Targets are generated from the product registry, never hand-listed
# (invariant 52: product count is never hard-coded).
global:
  scrape_interval: 30s
  external_labels:
    plane: control
scrape_configs:
  - job_name: product-health
    metrics_path: /metrics
    file_sd_configs:
      - files: ["/etc/ops-vm/targets/*.json"]
  - job_name: ops-vm-self
    static_configs:
      - targets: ["127.0.0.1:9090"]
YAMLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/provision/30-stack-up.sh <<'SHDOC'
#!/usr/bin/env bash
# Bring up the shared stack from pinned digests. Idempotent; a rebuild replays it.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/stack/versions.env
require_file ops-vm/stack/network.env
ops-vm/checks/versions-pinned.sh ops-vm/stack/versions.env
set -a; . ops-vm/stack/versions.env; . ops-vm/stack/network.env; set +a

install -d -m 0750 /etc/ops-vm /etc/ops-vm/targets
envsubst < ops-vm/prometheus/prometheus.yml.tmpl > /etc/ops-vm/prometheus.yml

docker compose -f ops-vm/stack/compose.shared.yml --env-file ops-vm/stack/versions.env pull
docker compose -f ops-vm/stack/compose.shared.yml --env-file ops-vm/stack/versions.env up -d
ops-vm/checks/stack-loopback-only.sh
record_run stack-up ok
SHDOC
chmod +x ops-vm/provision/30-stack-up.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/stack-loopback-only.sh <<'SHDOC'
#!/usr/bin/env bash
# Every published stack port is on 127.0.0.1 (Section 51.4).
set -euo pipefail
bad=$(grep -oE '"[0-9.:]+:[0-9]+:[0-9]+"' ops-vm/stack/compose.shared.yml | grep -v '"127\.0\.0\.1:' || true)
if [ -n "$bad" ]; then echo "STACK-LOOPBACK: FAIL"; echo "$bad"; exit 1; fi
echo "STACK-LOOPBACK: PASS"
SHDOC
chmod +x ops-vm/checks/stack-loopback-only.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add ops-vm/stack/compose.shared.yml ops-vm/stack/versions.env.example ops-vm/prometheus ops-vm/provision/30-stack-up.sh ops-vm/checks/stack-loopback-only.sh
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-03: shared stack compose for Grafana and Prometheus (DevLake deferred, FD-112)"
git push -u origin "lane/5/04-t03-stack-compose"
gh pr create --base integration --title "L5-04-03: shared stack compose" --body "Lane L5 phase 4 task L5-04-03. Paths: ops-vm/** only. Spec: 99.5, 51.5, 45.1, invariant 85."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Compose file is valid YAML | `python3 -c "import yaml,sys;yaml.safe_load(open('ops-vm/stack/compose.shared.yml'));print('YAML-OK')"` | `YAML-OK` |
| 2 | Every published port is loopback | `ops-vm/checks/stack-loopback-only.sh` | `STACK-LOOPBACK: PASS` |
| 3 | Every image is referenced by digest variable | `grep -c 'image: \${[A-Z_]*_IMAGE}@\${[A-Z_]*_DIGEST}' ops-vm/stack/compose.shared.yml` | `3` |
| 4 | Grafana anonymous auth is off and sign-up disabled | `grep -c 'GF_AUTH_ANONYMOUS_ENABLED: "false"\|GF_USERS_ALLOW_SIGN_UP: "false"' ops-vm/stack/compose.shared.yml` | `2` |
| 5 | Prometheus targets come from file-SD, not a hard-coded product list | `grep -c 'file_sd_configs' ops-vm/prometheus/prometheus.yml.tmpl` | `1` |
| 6 | No product name appears anywhere in the stack config | `grep -Eic '<any product name from registries/products>' ops-vm/stack/compose.shared.yml ops-vm/prometheus/prometheus.yml.tmpl` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python3 -c "import yaml;yaml.safe_load(open('ops-vm/stack/compose.shared.yml'));print('YAML-OK')"
ops-vm/checks/stack-loopback-only.sh
grep -c 'image: \${[A-Z_]*_IMAGE}@\${[A-Z_]*_DIGEST}' ops-vm/stack/compose.shared.yml
grep -c 'file_sd_configs' ops-vm/prometheus/prometheus.yml.tmpl
bash -n ops-vm/provision/30-stack-up.sh && echo SYNTAX-OK
```

Expected output:

```
YAML-OK
STACK-LOOPBACK: PASS
3
1
SYNTAX-OK
```

### Note — DevLake re-add trigger (FD-112)

Section 99.5's original STOP rule for this task required DevLake's database engine and version to be confirmed before install. That requirement is suspended for V1: DevLake is deferred (FD-112, 2026-09-08; PFD-032) and no DevLake service is built by this task. Do not add DevLake service blocks, `DEVLAKE_DB_ENGINE`/`DEVLAKE_DB_VERSION`, or a DevLake-DB-declared check back into this task's output on your own judgment. Re-adding DevLake — and with it the original Section 99.5 database-engine-confirmation STOP rule — is gated on the trigger condition recorded in `contracts/v1-scope.yaml` (`devlake.trigger: to_be_determined_by_L0`), an explicit future L0 decision.

---

## L5-04-04 — Grafana provisioning from git: datasource, dashboard provider, stack dashboard

**Size:** M · **Depends on:** L5-04-03 · **Slug:** `grafana-provisioning`
**Spec:** 99.5 (dashboards as provisioned JSON), 45.1 (Grafana dashboard JSON is in the reconstruction set), 52.1 (the Operating System Health Report renders in the Grafana instance the platform already requires), D75 / AT-097 (**no people datasource in the shared instance — verified in the provisioned configuration, not inferred from panel visibility**), 92.11 (the designated messaging channel is a configuration value, never hard-coded).

This task provisions the **shared (Layer A)** instance only. The Layer B instance is T05.

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/grafana/provisioning/datasources/layer-a.yaml` | Prometheus + DevLake datasources for the shared instance |
| `ops-vm/grafana/provisioning/dashboards/provider.yaml` | File provider pointing at `ops-vm/grafana/dashboards` |
| `ops-vm/grafana/provisioning/alerting/contact-points.yaml.tmpl` | Contact point rendered from the designated-channel config value |
| `ops-vm/grafana/dashboards/control-plane-stack.json` | The stack's own dashboard — the "dashboards-green" target of the 4-hour clock |
| `ops-vm/checks/no-people-datasource-in-shared.sh` | AT-097 host-side check |
| `ops-vm/checks/grafana-provisioned.sh` | Asserts datasources connect and dashboards loaded |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t04-grafana-provisioning"
mkdir -p ops-vm/grafana/provisioning/datasources ops-vm/grafana/provisioning/dashboards ops-vm/grafana/provisioning/alerting ops-vm/grafana/dashboards
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/grafana/provisioning/datasources/layer-a.yaml <<'YAMLDOC'
# Shared (Layer A) instance datasources ONLY.
# The people datasource is NEVER registered here - it exists only in the
# separately credentialed Founder-only instance (D75, AT-097, Section 90).
apiVersion: 1
datasources:
  - name: prometheus
    type: prometheus
    access: proxy
    url: http://127.0.0.1:9090
    isDefault: true
  - name: devlake
    type: mysql
    access: proxy
    url: 127.0.0.1:3306
    database: lake
    user: ${DEVLAKE_RO_USER}
    secureJsonData:
      password: ${DEVLAKE_RO_PASSWORD}
YAMLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/grafana/provisioning/dashboards/provider.yaml <<'YAMLDOC'
apiVersion: 1
providers:
  - name: control-plane
    type: file
    updateIntervalSeconds: 60
    allowUiUpdates: false     # dashboards are provisioned from git, never edited in the UI
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
YAMLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/grafana/provisioning/alerting/contact-points.yaml.tmpl <<'YAMLDOC'
# The designated messaging channel is a configuration value, never a hard-coded
# destination (Section 92.11). Rendered by 30-stack-up.sh from notify config.
apiVersion: 1
contactPoints:
  - orgId: 1
    name: designated-channel
    receivers:
      - uid: designated-channel
        type: webhook
        settings:
          url: ${DESIGNATED_CHANNEL_WEBHOOK_URL}
YAMLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/grafana/dashboards/control-plane-stack.json <<'JSONDOC'
{
  "uid": "control-plane-stack",
  "title": "Control-plane stack",
  "tags": ["control-plane", "rebuild-target"],
  "timezone": "utc",
  "schemaVersion": 39,
  "panels": [
    {
      "id": 1,
      "type": "stat",
      "title": "Prometheus up",
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "targets": [{"expr": "up{job=\"ops-vm-self\"}", "refId": "A"}],
      "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0}
    },
    {
      "id": 2,
      "type": "stat",
      "title": "Product targets scraped",
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "targets": [{"expr": "count(up{job=\"product-health\"})", "refId": "A"}],
      "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0}
    },
    {
      "id": 3,
      "type": "stat",
      "title": "DevLake ingest age (hours)",
      "datasource": {"type": "mysql", "uid": "devlake"},
      "targets": [{"rawSql": "SELECT TIMESTAMPDIFF(HOUR, MAX(updated_at), UTC_TIMESTAMP()) AS age FROM _devlake_collector_latest_state", "format": "table", "refId": "A"}],
      "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0}
    },
    {
      "id": 4,
      "type": "stat",
      "title": "Reconciliation freshness (hours)",
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "targets": [{"expr": "time() - ops_vm_job_last_success_timestamp{job_name=\"reconcile\"}", "refId": "A"}],
      "gridPos": {"h": 4, "w": 6, "x": 18, "y": 0}
    }
  ]
}
JSONDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/no-people-datasource-in-shared.sh <<'SHDOC'
#!/usr/bin/env bash
# AT-097: no people datasource entry and no dashboard reference exists in the
# shared instance's provisioning - verified in the provisioned configuration,
# never inferred from panel visibility (D75).
set -euo pipefail
hits=$(grep -RniE 'layer-?b|people|person|performance-evidence' \
        ops-vm/grafana/provisioning ops-vm/grafana/dashboards \
        --include='*.yaml' --include='*.yml' --include='*.json' \
        | grep -v 'NEVER registered here' || true)
if [ -n "$hits" ]; then echo "NO-PEOPLE-DATASOURCE-SHARED: FAIL"; echo "$hits"; exit 1; fi
echo "NO-PEOPLE-DATASOURCE-SHARED: PASS"
SHDOC
chmod +x ops-vm/checks/no-people-datasource-in-shared.sh

cat > ops-vm/checks/grafana-provisioned.sh <<'SHDOC'
#!/usr/bin/env bash
# Post-provision / post-patch assertion: dashboards provision from JSON and the
# instance's datasources connect (Section 51.4 post-patch smoke checklist).
set -euo pipefail
BASE="${1:?usage: grafana-provisioned.sh <base-url> <api-token>}"
TOKEN="${2:?}"
ds=$(curl -sf -H "Authorization: Bearer $TOKEN" "$BASE/api/datasources" | python3 -c 'import sys,json;print(len(json.load(sys.stdin)))')
[ "$ds" -ge 1 ] || { echo "GRAFANA-PROVISIONED: FAIL (no datasources)"; exit 1; }
for uid in $(curl -sf -H "Authorization: Bearer $TOKEN" "$BASE/api/datasources" | python3 -c 'import sys,json;[print(d["uid"]) for d in json.load(sys.stdin)]'); do
  st=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $TOKEN" "$BASE/api/datasources/uid/$uid/health")
  [ "$st" = "200" ] || { echo "GRAFANA-PROVISIONED: FAIL (datasource $uid health $st)"; exit 1; }
done
curl -sf -H "Authorization: Bearer $TOKEN" "$BASE/api/dashboards/uid/control-plane-stack" >/dev/null \
  || { echo "GRAFANA-PROVISIONED: FAIL (control-plane-stack dashboard absent)"; exit 1; }
echo "GRAFANA-PROVISIONED: PASS"
SHDOC
chmod +x ops-vm/checks/grafana-provisioned.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add ops-vm/grafana ops-vm/checks/no-people-datasource-in-shared.sh ops-vm/checks/grafana-provisioned.sh
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-04: Grafana provisioned from git with the AT-097 shared-instance check"
git push -u origin "lane/5/04-t04-grafana-provisioning"
gh pr create --base integration --title "L5-04-04: Grafana provisioning from git" --body "Lane L5 phase 4 task L5-04-04. Paths: ops-vm/** only. Spec: 99.5, 45.1, 52.1, 92.11, D75, AT-097."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | All provisioning YAML parses | `for f in ops-vm/grafana/provisioning/datasources/layer-a.yaml ops-vm/grafana/provisioning/dashboards/provider.yaml; do python3 -c "import yaml,sys;yaml.safe_load(open(sys.argv[1]))" "$f" \|\| exit 1; done; echo YAML-OK` | `YAML-OK` |
| 2 | Dashboard JSON parses and has the fixed uid | `python3 -c "import json;print(json.load(open('ops-vm/grafana/dashboards/control-plane-stack.json'))['uid'])"` | `control-plane-stack` |
| 3 | AT-097 host-side check passes on the shared tree | `ops-vm/checks/no-people-datasource-in-shared.sh` | `NO-PEOPLE-DATASOURCE-SHARED: PASS` |
| 4 | AT-097 check actually detects a violation | SELF-VERIFY step 4 | `NO-PEOPLE-DATASOURCE-SHARED: FAIL` then `rc=1` |
| 5 | UI edits cannot replace provisioned dashboards | `grep -c 'allowUiUpdates: false' ops-vm/grafana/provisioning/dashboards/provider.yaml` | `1` |
| 6 | The messaging channel is a variable, not a literal URL | `grep -Ec 'https?://' ops-vm/grafana/provisioning/alerting/contact-points.yaml.tmpl` | `0` |
| 7 | Datasource credentials are variables, not literals | `grep -Ec '\$\{DEVLAKE_RO_(USER|PASSWORD)\}' ops-vm/grafana/provisioning/datasources/layer-a.yaml` | `2` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for f in ops-vm/grafana/provisioning/datasources/layer-a.yaml ops-vm/grafana/provisioning/dashboards/provider.yaml; do python3 -c "import yaml,sys;yaml.safe_load(open(sys.argv[1]))" "$f" || exit 1; done; echo YAML-OK
python3 -c "import json;print(json.load(open('ops-vm/grafana/dashboards/control-plane-stack.json'))['uid'])"
ops-vm/checks/no-people-datasource-in-shared.sh
# step 4 - negative test, then revert
printf 'apiVersion: 1\ndatasources:\n  - name: people\n    type: mysql\n' > ops-vm/grafana/provisioning/datasources/ZZ-negative-test.yaml
ops-vm/checks/no-people-datasource-in-shared.sh; echo "rc=$?"
rm -f ops-vm/grafana/provisioning/datasources/ZZ-negative-test.yaml
ops-vm/checks/no-people-datasource-in-shared.sh
grep -c 'allowUiUpdates: false' ops-vm/grafana/provisioning/dashboards/provider.yaml
grep -Ec 'https?://' ops-vm/grafana/provisioning/alerting/contact-points.yaml.tmpl
```

Expected output:

```
YAML-OK
control-plane-stack
NO-PEOPLE-DATASOURCE-SHARED: PASS
NO-PEOPLE-DATASOURCE-SHARED: FAIL
ops-vm/grafana/provisioning/datasources/ZZ-negative-test.yaml:3:  - name: people
rc=1
NO-PEOPLE-DATASOURCE-SHARED: PASS
1
0
```

### STOP rule

If the AT-097 check fails on the committed tree — that is, a people/Layer B datasource or dashboard reference already exists under `ops-vm/grafana/` — **do not delete it and do not proceed.** D75 makes instance-level separation the mechanism and panel-hiding explicitly insufficient; a Layer B reference in the shared instance is a live access-control failure, not a tidy-up. Open a blocker (§1.4) with the decision line: *"A Layer B datasource or dashboard reference is present in the shared Grafana provisioning; AT-097 fails and Section 90 requires L0 to decide the containment and disclosure path."*

---

## L5-04-05 — Layer B second Grafana instance: host placement and encryption at rest

**Size:** M · **Depends on:** L5-04-03, L5-02-COMPLETE · **Slug:** `layerb-host`
**Spec:** 51.4 — *"Layer B carries explicit at-rest protections on the operations VM. The separately credentialed people-data store — database plus generated documents — is **encrypted at rest**"*; a **named owner and an explicit read-access list** reviewed with the asset inventory (Section 49); an entry in the fifth-tier credential inventory of Section 40.1 with its rotation cadence and named rotator; custody of the store's encryption key is the Section 14.4 escrow; **no Layer B content ever lives in an organisation-readable repository**. Also 99.5 / D75 (second Founder-only Grafana instance, separately credentialed, panel-hiding explicitly insufficient), AT-098, 90.3 (host-level administrative access is the single named, bounded accepted risk), 90.4 (credential and authentication allowlist match the capability holders).

**Scope boundary:** the instance-level access model, the three-state field handling, the generated self-view documents and the AT-090/AT-097/AT-098 access tests are subsystem L and belong to the lane's access-control phase (`L5-02-COMPLETE`). This task builds only what is VM-side: the second instance's compose project, its encrypted volume, and the at-rest and access-list controls Section 51.4 places on the operations VM.

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/stack/compose.layerb.yml` | Second Grafana instance, separate compose project, port `3001`, loopback only |
| `ops-vm/provision/40-layerb-volume.sh` | Creates and mounts the encrypted volume; refuses an unencrypted mount |
| `ops-vm/layerb/provisioning/datasources/layer-b.yaml.example` | Layer B datasource shape with empty credential keys |
| `ops-vm/layerb/access-list.yaml.example` | Named owner and explicit read-access list (Section 51.4) |
| `ops-vm/checks/layerb-at-rest.sh` | Fails when the Layer B volume is not an encrypted device |
| `ops-vm/checks/layerb-instance-separate.sh` | Fails when the two instances share a volume, database or credential |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t05-layerb-host"
mkdir -p ops-vm/layerb/provisioning/datasources
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/stack/compose.layerb.yml <<'YAMLDOC'
# Founder-only Layer B instance. A SEPARATE compose project, a separate volume
# and a separate credential domain from the shared stack (D75, AT-098).
# Panel-hiding is explicitly insufficient; separation is at instance level.
name: ops-vm-layerb

services:
  grafana-layerb:
    image: ${GRAFANA_LAYERB_IMAGE}@${GRAFANA_LAYERB_DIGEST}
    restart: always
    ports: ["127.0.0.1:3001:3000"]
    environment:
      GF_SERVER_HTTP_ADDR: "127.0.0.1"
      GF_USERS_ALLOW_SIGN_UP: "false"
      GF_AUTH_ANONYMOUS_ENABLED: "false"
    volumes:
      - /mnt/layerb/grafana:/var/lib/grafana
      - ../layerb/provisioning:/etc/grafana/provisioning:ro

  layerb-db:
    image: ${LAYERB_DB_IMAGE}@${LAYERB_DB_DIGEST}
    restart: always
    ports: ["127.0.0.1:5433:5432"]
    volumes:
      - /mnt/layerb/db:/var/lib/postgresql/data
YAMLDOC
cat >> ops-vm/stack/versions.env.example <<'ENVDOC'
LAYERB_DB_IMAGE=
LAYERB_DB_DIGEST=
ENVDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/provision/40-layerb-volume.sh <<'SHDOC'
#!/usr/bin/env bash
# Layer B at-rest protection on the operations VM (Section 51.4).
# The people-data store - database plus generated documents - is encrypted at
# rest. Key custody is the Section 14.4 escrow; this script never creates a key.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/layerb/layerb.env
set -a; . ops-vm/layerb/layerb.env; set +a
require_env LAYERB_BLOCK_DEVICE LAYERB_KEY_ESCROW_RECORD LAYERB_OWNER

[ -b "$LAYERB_BLOCK_DEVICE" ] || fail_closed "LAYERB_BLOCK_DEVICE is not a block device: $LAYERB_BLOCK_DEVICE"
cryptsetup isLuks "$LAYERB_BLOCK_DEVICE" \
  || fail_closed "device is not LUKS-formatted; Section 51.4 requires encryption at rest and key custody is the Section 14.4 escrow - this script never creates a key"

cryptsetup status layerb >/dev/null 2>&1 || cryptsetup open "$LAYERB_BLOCK_DEVICE" layerb
mkdir -p /mnt/layerb
mountpoint -q /mnt/layerb || mount /dev/mapper/layerb /mnt/layerb
install -d -m 0700 /mnt/layerb/grafana /mnt/layerb/db
record_run layerb-volume ok "owner=$LAYERB_OWNER escrow=$LAYERB_KEY_ESCROW_RECORD"
SHDOC
chmod +x ops-vm/provision/40-layerb-volume.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/layerb/provisioning/datasources/layer-b.yaml.example <<'YAMLDOC'
# Layer B datasource - registered ONLY in the Founder-only instance (D75).
# Credentials are a separate credential domain from the shared instance and are
# never copied into it. Values are supplied on the host, never committed.
apiVersion: 1
datasources:
  - name: people
    type: postgres
    access: proxy
    url: 127.0.0.1:5433
    database: ${LAYERB_DB_NAME}
    user: ${LAYERB_DB_USER}
    secureJsonData:
      password: ${LAYERB_DB_PASSWORD}
YAMLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/layerb/access-list.yaml.example <<'YAMLDOC'
# Section 51.4: the Layer B store carries a named owner and an explicit
# read-access list, reviewed with the asset inventory (Section 49).
# Section 90.4: the instance's credential and authentication allowlist must
# match the capability holders - asserted by the post-patch smoke checklist.
owner:                      # named person, never a role alias
key_escrow_record:          # Section 14.4 escrow row for the store's key
read_access:                # explicit list; empty is a valid, stricter value
  - login:
    granted_on:
    reviewed_on:
host_admin_accepted_risk:   # Section 90.3 record id: the single named, bounded
                            # accepted risk with holder, compensating control
                            # and dated review
credential_inventory_entry: # Section 40.1 fifth-tier entry id (assets/**)
YAMLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/layerb-at-rest.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 51.4: the Layer B store is encrypted at rest on the operations VM.
set -euo pipefail
src=$(findmnt -no SOURCE /mnt/layerb 2>/dev/null || true)
[ -n "$src" ] || { echo "LAYERB-AT-REST: FAIL (not mounted)"; exit 1; }
case "$src" in
  /dev/mapper/*) ;;
  *) echo "LAYERB-AT-REST: FAIL (not a mapper device: $src)"; exit 1 ;;
esac
cryptsetup status "$(basename "$src")" | grep -q '^\s*type:\s*LUKS' \
  || { echo "LAYERB-AT-REST: FAIL (mapper is not LUKS)"; exit 1; }
echo "LAYERB-AT-REST: PASS"
SHDOC
chmod +x ops-vm/checks/layerb-at-rest.sh

cat > ops-vm/checks/layerb-instance-separate.sh <<'SHDOC'
#!/usr/bin/env bash
# D75 / AT-098: the two Grafana instances share no volume, no database and no
# credential. Verified in the provisioned configuration, not by panel visibility.
set -euo pipefail
fail=0
shared_vols=$(grep -oE '^\s+- [^:]+:' ops-vm/stack/compose.shared.yml | tr -d ' -:' | sort -u)
layerb_vols=$(grep -oE '^\s+- [^:]+:' ops-vm/stack/compose.layerb.yml | tr -d ' -:' | sort -u)
overlap=$(comm -12 <(echo "$shared_vols") <(echo "$layerb_vols") || true)
[ -z "$overlap" ] || { echo "shared volume path: $overlap"; fail=1; }
grep -q '127.0.0.1:3001:3000' ops-vm/stack/compose.layerb.yml || { echo "layerb not on its own port"; fail=1; }
grep -q '^name: ops-vm-layerb' ops-vm/stack/compose.layerb.yml || { echo "layerb not its own compose project"; fail=1; }
if grep -v '^ *#' ops-vm/grafana/provisioning/datasources/layer-a.yaml | grep -qE '^ *- name: (people|layer-?b)'; then echo "people datasource in shared instance"; fail=1; fi
if [ "$fail" -eq 0 ]; then echo "LAYERB-INSTANCE-SEPARATE: PASS"; else echo "LAYERB-INSTANCE-SEPARATE: FAIL"; exit 1; fi
SHDOC
chmod +x ops-vm/checks/layerb-instance-separate.sh
printf 'layerb/layerb.env\nlayerb/access-list.yaml\nlayerb/provisioning/datasources/layer-b.yaml\n' >> ops-vm/.gitignore
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add ops-vm/stack/compose.layerb.yml ops-vm/stack/versions.env.example ops-vm/provision/40-layerb-volume.sh ops-vm/layerb ops-vm/checks/layerb-at-rest.sh ops-vm/checks/layerb-instance-separate.sh ops-vm/.gitignore
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-05: Layer B instance host placement and encryption at rest"
git push -u origin "lane/5/04-t05-layerb-host"
gh pr create --base integration --title "L5-04-05: Layer B host placement and at-rest encryption" --body "Lane L5 phase 4 task L5-04-05. Paths: ops-vm/** only. Spec: 51.4, 90.3, 90.4, D75, AT-098."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Layer B compose is a separate project on its own port | `grep -c '^name: ops-vm-layerb' ops-vm/stack/compose.layerb.yml; grep -c '127.0.0.1:3001:3000' ops-vm/stack/compose.layerb.yml` | `1` then `1` |
| 2 | The two instances share no volume path | `ops-vm/checks/layerb-instance-separate.sh` | `LAYERB-INSTANCE-SEPARATE: PASS` |
| 3 | The volume script refuses a non-LUKS device | SELF-VERIFY step 3 | `FAIL-CLOSED: LAYERB_BLOCK_DEVICE is not a block device…` then `rc=1` |
| 4 | No Layer B credential value is committed | `git ls-files ops-vm/layerb \| grep -Evc '\.example$'` | `0` |
| 5 | The access list demands owner, escrow, read list, 90.3 risk and the 40.1 entry | `grep -Ec '^(owner|key_escrow_record|read_access|host_admin_accepted_risk|credential_inventory_entry):' ops-vm/layerb/access-list.yaml.example` | `5` |
| 6 | The at-rest check fails when nothing is mounted | `ops-vm/checks/layerb-at-rest.sh; echo "rc=$?"` (on a host without `/mnt/layerb`) | `LAYERB-AT-REST: FAIL (not mounted)` then `rc=1` |
| 7 | The script never generates a key | `grep -Ec 'cryptsetup (luksFormat|luksAddKey)' ops-vm/provision/40-layerb-volume.sh` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
grep -c '^name: ops-vm-layerb' ops-vm/stack/compose.layerb.yml
grep -c '127.0.0.1:3001:3000' ops-vm/stack/compose.layerb.yml
ops-vm/checks/layerb-instance-separate.sh
# step 3 - negative test with a non-device path
rm -rf /tmp/t05 && mkdir -p /tmp/t05/ops-vm/layerb /tmp/t05/ops-vm/lib
cp "$CONTROL_PLANE_ROOT/ops-vm/lib/common.sh" /tmp/t05/ops-vm/lib/
printf 'LAYERB_BLOCK_DEVICE=/tmp/not-a-device\nLAYERB_KEY_ESCROW_RECORD=e1\nLAYERB_OWNER=founder\n' > /tmp/t05/ops-vm/layerb/layerb.env
( cd /tmp/t05 && bash "$CONTROL_PLANE_ROOT/ops-vm/provision/40-layerb-volume.sh"; echo "rc=$?" )
git ls-files ops-vm/layerb | grep -Evc '\.example$'
grep -Ec '^(owner|key_escrow_record|read_access|host_admin_accepted_risk|credential_inventory_entry):' ops-vm/layerb/access-list.yaml.example
grep -Ec 'cryptsetup (luksFormat|luksAddKey)' ops-vm/provision/40-layerb-volume.sh
```

Expected output:

```
1
1
LAYERB-INSTANCE-SEPARATE: PASS
<timestamp> FAIL-CLOSED: LAYERB_BLOCK_DEVICE is not a block device: /tmp/not-a-device
rc=1
0
5
0
```

### STOP rule

If `ops-vm/layerb/layerb.env` names a device that is **not** LUKS-formatted, or `LAYERB_KEY_ESCROW_RECORD` is empty: **do not format the device, do not create a key, do not start the Layer B instance.** Section 51.4 requires encryption at rest and Section 45.4 places custody of the decryption key in the Section 14.4 escrow — creating a key here would create an unescrowed key. Open a blocker (§1.4) with the decision line: *"The Layer B volume is unencrypted or its key has no Section 14.4 escrow row; Section 51.4 requires L0 to provide the escrowed key before the store is created."*

---

## L5-04-06 — Layer B backup: append-only credential to object-locked storage

**Size:** M · **Depends on:** L5-04-05 · **Slug:** `layerb-backup`
**Spec:** 51.4 — Layer B backups carry the controls Section 45.3 gives the organisation export, *"because the more sensitive copy may not be the less protected one"*: an **append-only, write-only backup credential** writing to **object-locked, versioned storage** in a **different provider and credential domain than the operations VM**, so the party who can write the backup can neither read nor destroy backup history; a named owner and an explicit read-access list reviewed with the asset inventory (Section 49); an entry in the fifth-tier credential inventory of Section 40.1 with its rotation cadence and named rotator; **backup failure alerts on the product discipline of Section 44.3**.

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/layerb/backup/backup-layerb.sh` | Encrypt-then-write backup; asserts the credential cannot read or delete |
| `ops-vm/layerb/backup/storage.env.example` | Provider, bucket, object-lock and retention keys (empty) |
| `ops-vm/systemd/layerb-backup.service` | One-shot unit |
| `ops-vm/systemd/layerb-backup.timer` | Cadence timer |
| `ops-vm/checks/layerb-backup-credential.sh` | Negative test: the write credential must fail a read and a delete |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t06-layerb-backup"
mkdir -p ops-vm/layerb/backup ops-vm/systemd
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/layerb/backup/storage.env.example <<'ENVDOC'
# Layer B backup target (Section 51.4, on the Section 45.3 controls).
# MUST be a different provider AND a different credential domain than the
# operations VM. Values come from the recorded decision; never chosen here.
LAYERB_BACKUP_PROVIDER=
LAYERB_BACKUP_ENDPOINT=
LAYERB_BACKUP_BUCKET=
LAYERB_BACKUP_OBJECT_LOCK=          # must be "on"
LAYERB_BACKUP_VERSIONING=           # must be "on"
LAYERB_BACKUP_RETENTION_DAYS=
LAYERB_BACKUP_ACCESS_KEY_ID=        # append-only, write-only credential
LAYERB_BACKUP_SECRET_ACCESS_KEY=
LAYERB_BACKUP_ENCRYPTION_KEY_ESCROW= # Section 14.4 escrow row
LAYERB_BACKUP_OWNER=
LAYERB_BACKUP_ROTATOR=              # DevOps-capability holder (Section 40.1)
LAYERB_BACKUP_ROTATION_CADENCE=     # initial value: quarterly (Section 40.1)
ENVDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/layerb/backup/backup-layerb.sh <<'SHDOC'
#!/usr/bin/env bash
# Layer B backup. Encrypt locally, then write with an append-only, write-only
# credential to object-locked, versioned storage in a different provider and
# credential domain than this host (Section 51.4 on the Section 45.3 controls).
set -euo pipefail
. "$(dirname "$0")/../../lib/common.sh"
require_file ops-vm/layerb/backup/storage.env
set -a; . ops-vm/layerb/backup/storage.env; set +a
require_env LAYERB_BACKUP_PROVIDER LAYERB_BACKUP_ENDPOINT LAYERB_BACKUP_BUCKET \
            LAYERB_BACKUP_OBJECT_LOCK LAYERB_BACKUP_VERSIONING \
            LAYERB_BACKUP_RETENTION_DAYS LAYERB_BACKUP_ACCESS_KEY_ID \
            LAYERB_BACKUP_SECRET_ACCESS_KEY LAYERB_BACKUP_ENCRYPTION_KEY_ESCROW \
            LAYERB_BACKUP_OWNER LAYERB_BACKUP_ROTATOR LAYERB_BACKUP_ROTATION_CADENCE

[ "$LAYERB_BACKUP_OBJECT_LOCK" = "on" ] || fail_closed "object lock must be on (Section 51.4)"
[ "$LAYERB_BACKUP_VERSIONING" = "on" ] || fail_closed "versioning must be on (Section 51.4)"

ops-vm/checks/layerb-backup-credential.sh || fail_closed "backup credential is not append-only/write-only"

stamp=$(date -u +%Y%m%dT%H%M%SZ)
work=$(mktemp -d); trap 'rm -rf "$work"' EXIT
pg_dump --host 127.0.0.1 --port 5433 --format=custom --file "$work/layerb-$stamp.dump" "$LAYERB_DB_NAME"
tar -C /mnt/layerb -cf "$work/layerb-docs-$stamp.tar" ./documents
sha256sum "$work"/* > "$work/manifest-$stamp.sha256"
age --encrypt --recipients-file /etc/ops-vm/layerb-backup.recipients \
    --output "$work/layerb-$stamp.age" \
    <(tar -C "$work" -cf - "layerb-$stamp.dump" "layerb-docs-$stamp.tar" "manifest-$stamp.sha256")

AWS_ACCESS_KEY_ID="$LAYERB_BACKUP_ACCESS_KEY_ID" \
AWS_SECRET_ACCESS_KEY="$LAYERB_BACKUP_SECRET_ACCESS_KEY" \
aws --endpoint-url "$LAYERB_BACKUP_ENDPOINT" s3api put-object \
    --bucket "$LAYERB_BACKUP_BUCKET" --key "layerb/$stamp.age" \
    --body "$work/layerb-$stamp.age" \
    --object-lock-mode COMPLIANCE \
    --object-lock-retain-until-date "$(date -u -d "+$LAYERB_BACKUP_RETENTION_DAYS days" +%Y-%m-%dT%H:%M:%SZ)"

record_run layerb-backup ok "key=layerb/$stamp.age owner=$LAYERB_BACKUP_OWNER"
SHDOC
chmod +x ops-vm/layerb/backup/backup-layerb.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/layerb-backup-credential.sh <<'SHDOC'
#!/usr/bin/env bash
# Negative test: the party who can write the backup can neither read it nor
# destroy backup history (Section 51.4). A credential that can read or delete
# FAILS this check.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/layerb/backup/storage.env
set -a; . ops-vm/layerb/backup/storage.env; set +a
export AWS_ACCESS_KEY_ID="$LAYERB_BACKUP_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$LAYERB_BACKUP_SECRET_ACCESS_KEY"
probe="layerb/_credential-probe-$(date -u +%s)"
fail=0
aws --endpoint-url "$LAYERB_BACKUP_ENDPOINT" s3api put-object \
    --bucket "$LAYERB_BACKUP_BUCKET" --key "$probe" --body /dev/null >/dev/null \
  || { echo "write DENIED - the credential cannot write"; fail=1; }
if aws --endpoint-url "$LAYERB_BACKUP_ENDPOINT" s3api get-object \
      --bucket "$LAYERB_BACKUP_BUCKET" --key "$probe" /dev/null >/dev/null 2>&1; then
  echo "read ALLOWED - credential is not write-only"; fail=1
else echo "read denied OK"; fi
if aws --endpoint-url "$LAYERB_BACKUP_ENDPOINT" s3api delete-object \
      --bucket "$LAYERB_BACKUP_BUCKET" --key "$probe" >/dev/null 2>&1; then
  echo "delete ALLOWED - credential is not append-only"; fail=1
else echo "delete denied OK"; fi
if [ "$fail" -eq 0 ]; then echo "LAYERB-BACKUP-CREDENTIAL: PASS"; else echo "LAYERB-BACKUP-CREDENTIAL: FAIL"; exit 1; fi
SHDOC
chmod +x ops-vm/checks/layerb-backup-credential.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/systemd/layerb-backup.service <<'UNITDOC'
[Unit]
Description=Layer B encrypted backup to object-locked storage (Section 51.4)
After=network-online.target
[Service]
Type=oneshot
User=root
WorkingDirectory=/opt/control-plane
ExecStart=/opt/control-plane/ops-vm/layerb/backup/backup-layerb.sh
# Backup failure alerts on the product discipline of Section 44.3.
ExecStopPost=/opt/control-plane/notify/bin/notify-job-result.sh layerb-backup %i
UNITDOC

cat > ops-vm/systemd/layerb-backup.timer <<'UNITDOC'
[Unit]
Description=Layer B backup cadence
[Timer]
OnCalendar=${LAYERB_BACKUP_ONCALENDAR}
Persistent=true
[Install]
WantedBy=timers.target
UNITDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add ops-vm/layerb/backup ops-vm/systemd/layerb-backup.service ops-vm/systemd/layerb-backup.timer ops-vm/checks/layerb-backup-credential.sh
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-06: Layer B append-only backup to object-locked storage"
git push -u origin "lane/5/04-t06-layerb-backup"
gh pr create --base integration --title "L5-04-06: Layer B backup to object-locked storage" --body "Lane L5 phase 4 task L5-04-06. Paths: ops-vm/** only. Spec: 51.4, 45.3, 44.3, 40.1."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Both scripts parse | `bash -n ops-vm/layerb/backup/backup-layerb.sh && bash -n ops-vm/checks/layerb-backup-credential.sh && echo SYNTAX-OK` | `SYNTAX-OK` |
| 2 | Object lock and versioning are hard requirements | `grep -Ec 'must be on \(Section 51.4\)' ops-vm/layerb/backup/backup-layerb.sh` | `2` |
| 3 | The backup runs the credential negative test before writing | `grep -n 'layerb-backup-credential.sh' ops-vm/layerb/backup/backup-layerb.sh \| head -1 \| cut -d: -f1` — compare with the line number of `put-object` | credential-check line number is **lower** than the `put-object` line number |
| 4 | Storage config carries owner, rotator and cadence (Section 40.1) | `grep -Ec '^LAYERB_BACKUP_(OWNER|ROTATOR|ROTATION_CADENCE)=' ops-vm/layerb/backup/storage.env.example` | `3` |
| 5 | No storage credential value is committed | `git ls-files ops-vm/layerb/backup \| grep -Evc '(\.example|\.sh)$'` | `0` |
| 6 | The service unit routes failure to the notification path (Section 44.3) | `grep -c 'notify-job-result.sh layerb-backup' ops-vm/systemd/layerb-backup.service` | `1` |
| 7 | Backup is encrypted before it leaves the host | `grep -c 'age --encrypt' ops-vm/layerb/backup/backup-layerb.sh` | `1` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash -n ops-vm/layerb/backup/backup-layerb.sh && bash -n ops-vm/checks/layerb-backup-credential.sh && echo SYNTAX-OK
grep -Ec 'must be on \(Section 51.4\)' ops-vm/layerb/backup/backup-layerb.sh
CRED=$(grep -n 'layerb-backup-credential.sh' ops-vm/layerb/backup/backup-layerb.sh | head -1 | cut -d: -f1)
PUT=$(grep -n 'put-object' ops-vm/layerb/backup/backup-layerb.sh | head -1 | cut -d: -f1)
[ "$CRED" -lt "$PUT" ] && echo "CREDENTIAL-CHECK-BEFORE-WRITE: PASS" || echo "CREDENTIAL-CHECK-BEFORE-WRITE: FAIL"
grep -Ec '^LAYERB_BACKUP_(OWNER|ROTATOR|ROTATION_CADENCE)=' ops-vm/layerb/backup/storage.env.example
git ls-files ops-vm/layerb/backup | grep -Evc '(\.example|\.sh)$'
grep -c 'notify-job-result.sh layerb-backup' ops-vm/systemd/layerb-backup.service
grep -c 'age --encrypt' ops-vm/layerb/backup/backup-layerb.sh
```

Expected output:

```
SYNTAX-OK
2
CREDENTIAL-CHECK-BEFORE-WRITE: PASS
3
0
1
1
```

### STOP rule

If `ops-vm/checks/layerb-backup-credential.sh` reports `read ALLOWED` or `delete ALLOWED`, or the backup target resolves to the **same provider or the same credential domain** as the operations VM: **do not run a backup, do not relax the check.** Section 51.4 requires that the party who can write the backup can neither read nor destroy backup history, in a different provider and credential domain. Open a blocker (§1.4) with the decision line: *"The Layer B backup credential is not write-only/append-only, or the target shares a provider or credential domain with the operations VM; Section 51.4 requires L0 to provision a conforming target."*

---

## L5-04-07 — Reconciliation host: units, credential store, freshness telemetry

**Size:** M · **Depends on:** L5-04-03, L3-COMPLETE · **Slug:** `reconcile-host`
**Spec:** 99.2 subsystem M (reconciliation runs on the operations VM), 51.2 — *"Reconciliation freshness: full reconciliation completes at least daily… Red at 48 hours, Level 5 escalation at 72"* and *"Drift detection freshness: security-class checks at least hourly… Red"*; 40.1 fifth-tier operations (each control-plane machine credential carries an inventory entry with rotation cadence, named rotator, runbook link, declared behavioural envelope and the named owner of that envelope's alert configuration; **expected source host** is part of the envelope); 51.5 (the VM holds the fifth-tier machine-credential store, which is why the second trust boundary of Section 40.3 exists); 53.1 (every reconciliation run writes its result; a clean run is recorded as clean); SIG-13.

**Boundary:** the reconciler program itself is L3 (`reconciler/**`). This task provisions **where and how it runs** and the freshness telemetry the SLO reads. It invokes the reconciler by the CLI contract L3 publishes; it does not import or edit `reconciler/**`.

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/jobs/run-reconcile.sh` | Wrapper: loads the fifth-tier credential, runs the reconciler, emits telemetry |
| `ops-vm/systemd/reconcile-full.service` / `.timer` | Daily full reconciliation |
| `ops-vm/systemd/reconcile-security.service` / `.timer` | Hourly security-class checks |
| `ops-vm/credentials/README.md` | The fifth-tier store's placement, permissions and envelope keys |
| `ops-vm/credentials/store.env.example` | Credential handles and envelope keys (empty) |
| `ops-vm/checks/reconcile-freshness.sh` | Emits Amber/Red/Level-5 per the 51.2 thresholds |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t07-reconcile-host"
mkdir -p ops-vm/credentials ops-vm/jobs ops-vm/systemd
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/credentials/README.md <<'MDDOC'
# Fifth-tier machine-credential store (Section 40.1)

The operations VM holds the fifth secrets tier - the reconciler credential, the
provisioning CLI credential, the organisation-export token, the records-writer
credential and the Layer B backup credential. It holds NO production
credentials, NO deploy keys and NO environment access (Section 51.5). This is
why shell access to this host is a trust boundary, not an infrastructure detail
(Section 40.3, second trust boundary).

Placement: /var/lib/ops-vm/creds, mode 0700, owner ops-vm.
Never in git. Never in an environment file committed to this repository.

Each credential carries an entry in the operational asset inventory
(assets/inventory/, Section 49) recording:

* rotation cadence (initial value: quarterly)
* named rotator (a holder of the DevOps capability)
* a link to the one-page rotation runbook
* its declared behavioural envelope
* the named owner of that envelope's alert configuration

The behavioural envelope (Section 40.1) is four things, and a run outside it is
Blocking drift: a required signed run record naming the scheduled trigger; a
run-count ceiling per day (calibrated configuration, initial value twice the
scheduled run count, recalibrated whenever the schedule changes); an expected
source host; and published per-run API-call counts.

After any rotation, a manual reconciliation run must complete clean before the
rotation is recorded as done: a credential that rotates but no longer reconciles
has not been rotated, it has been broken (Section 40.1).

Should this VM be lost, the re-issue source is the Section 14.4 escrow.
MDDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/credentials/store.env.example <<'ENVDOC'
# Handles only - never values. Values live in /var/lib/ops-vm/creds (0700).
RECONCILER_CREDENTIAL_FILE=
RECONCILER_ENVELOPE_EXPECTED_HOST=
RECONCILER_ENVELOPE_RUN_CEILING_PER_DAY=
RECONCILER_ENVELOPE_ALERT_CONFIG_OWNER=
RECONCILER_ROTATION_CADENCE=
RECONCILER_ROTATOR=
RECONCILER_ROTATION_RUNBOOK=
ORG_EXPORT_TOKEN_FILE=
ORG_EXPORT_ENVELOPE_EXPECTED_HOST=
ORG_EXPORT_ENVELOPE_RUN_CEILING_PER_DAY=
ORG_EXPORT_ENVELOPE_ALERT_CONFIG_OWNER=
ENVDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/jobs/run-reconcile.sh <<'SHDOC'
#!/usr/bin/env bash
# Runs the reconciler (built by lane L3) on the operations VM.
# Usage: run-reconcile.sh full|security
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
MODE="${1:?usage: run-reconcile.sh full|security}"
case "$MODE" in full|security) ;; *) fail_closed "unknown mode: $MODE" ;; esac

require_file ops-vm/credentials/store.env
set -a; . ops-vm/credentials/store.env; set +a
require_env RECONCILER_CREDENTIAL_FILE RECONCILER_ENVELOPE_EXPECTED_HOST

# Behavioural envelope: expected source host (Section 40.1).
[ "$(hostname)" = "$RECONCILER_ENVELOPE_EXPECTED_HOST" ] \
  || fail_closed "host $(hostname) is not the declared expected source host for the reconciler credential"

# Signed run record naming the scheduled trigger (Section 40.1 envelope).
TRIGGER="${OPS_VM_TRIGGER:-}"
[ -n "$TRIGGER" ] || fail_closed "no scheduled trigger recorded for this run"

start=$(date -u +%s)
set +e
RECONCILER_CREDENTIAL_FILE="$RECONCILER_CREDENTIAL_FILE" \
  reconcile --mode "$MODE" --emit-metrics /var/lib/ops-vm/metrics/reconcile-$MODE.prom
rc=$?
set -e
end=$(date -u +%s)

if [ "$rc" -eq 0 ]; then
  record_run "reconcile-$MODE" ok "trigger=$TRIGGER seconds=$((end-start))"
  printf 'ops_vm_job_last_success_timestamp{job_name="reconcile-%s"} %s\n' "$MODE" "$end" \
    > "/var/lib/ops-vm/metrics/reconcile-$MODE-freshness.prom"
else
  # SIG-13: reconciliation job failures are Red; the job itself failing is
  # Level 5 escalation (Section 53.2).
  record_run "reconcile-$MODE" failed "trigger=$TRIGGER rc=$rc"
  notify/bin/notify-job-result.sh "reconcile-$MODE" failed
fi
exit "$rc"
SHDOC
chmod +x ops-vm/jobs/run-reconcile.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/systemd/reconcile-full.service <<'UNITDOC'
[Unit]
Description=Full reconciliation (Section 53); freshness SLO in Section 51.2
[Service]
Type=oneshot
User=ops-vm
WorkingDirectory=/opt/control-plane
Environment=OPS_VM_TRIGGER=reconcile-full.timer
ExecStart=/opt/control-plane/ops-vm/jobs/run-reconcile.sh full
UNITDOC

cat > ops-vm/systemd/reconcile-full.timer <<'UNITDOC'
[Unit]
Description=Full reconciliation at least daily (Section 51.2)
[Timer]
OnCalendar=daily
Persistent=true
[Install]
WantedBy=timers.target
UNITDOC

cat > ops-vm/systemd/reconcile-security.service <<'UNITDOC'
[Unit]
Description=Security-class drift checks (Section 51.2: at least hourly)
[Service]
Type=oneshot
User=ops-vm
WorkingDirectory=/opt/control-plane
Environment=OPS_VM_TRIGGER=reconcile-security.timer
ExecStart=/opt/control-plane/ops-vm/jobs/run-reconcile.sh security
UNITDOC

cat > ops-vm/systemd/reconcile-security.timer <<'UNITDOC'
[Unit]
Description=Security-class drift checks hourly
[Timer]
OnCalendar=hourly
Persistent=true
[Install]
WantedBy=timers.target
UNITDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/reconcile-freshness.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 51.2: full reconciliation at least daily; Red at 48h; Level 5 at 72h.
# Security-class checks at least hourly; Red on breach.
set -euo pipefail
now=$(date -u +%s)
state() {
  local mode="$1" red="$2" esc="$3" f="/var/lib/ops-vm/metrics/reconcile-$1-freshness.prom"
  if [ ! -f "$f" ]; then echo "$mode: NO-RUN-RECORDED -> LEVEL-5"; return 5; fi
  local ts age
  ts=$(awk '{print $2}' "$f"); age=$(( (now - ts) / 3600 ))
  if   [ "$age" -ge "$esc" ]; then echo "$mode: age=${age}h -> LEVEL-5"; return 5
  elif [ "$age" -ge "$red" ]; then echo "$mode: age=${age}h -> RED";     return 2
  else echo "$mode: age=${age}h -> OK"; return 0; fi
}
rc=0
state full 48 72 || rc=$?
state security 1 24 || rc=$?
[ "$rc" -eq 0 ] && echo "RECONCILE-FRESHNESS: PASS" || echo "RECONCILE-FRESHNESS: BREACH"
exit "$rc"
SHDOC
chmod +x ops-vm/checks/reconcile-freshness.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add ops-vm/jobs/run-reconcile.sh ops-vm/systemd/reconcile-full.service ops-vm/systemd/reconcile-full.timer ops-vm/systemd/reconcile-security.service ops-vm/systemd/reconcile-security.timer ops-vm/credentials ops-vm/checks/reconcile-freshness.sh
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-07: reconciliation host units, credential store and freshness telemetry"
git push -u origin "lane/5/04-t07-reconcile-host"
gh pr create --base integration --title "L5-04-07: reconciliation host and freshness telemetry" --body "Lane L5 phase 4 task L5-04-07. Paths: ops-vm/** only. Spec: 51.2, 51.5, 40.1, 40.3, 53.1, 53.2, SIG-13."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Scripts parse; units are well-formed | `bash -n ops-vm/jobs/run-reconcile.sh && bash -n ops-vm/checks/reconcile-freshness.sh && echo SYNTAX-OK` | `SYNTAX-OK` |
| 2 | Both cadences exist and match 51.2 | `grep -h '^OnCalendar' ops-vm/systemd/reconcile-full.timer ops-vm/systemd/reconcile-security.timer` | `OnCalendar=daily` then `OnCalendar=hourly` |
| 3 | The wrapper enforces the expected-source-host envelope | `grep -c 'is not the declared expected source host' ops-vm/jobs/run-reconcile.sh` | `1` |
| 4 | The wrapper refuses a run with no recorded trigger | SELF-VERIFY step 4 | `FAIL-CLOSED: no scheduled trigger recorded for this run` then `rc=1` |
| 5 | Freshness check reports Level 5 when no run is recorded | SELF-VERIFY step 5 | `full: NO-RUN-RECORDED -> LEVEL-5` … `RECONCILE-FRESHNESS: BREACH` |
| 6 | The credential store carries every Section 40.1 envelope key | `grep -Ec '^RECONCILER_(ENVELOPE_EXPECTED_HOST|ENVELOPE_RUN_CEILING_PER_DAY|ENVELOPE_ALERT_CONFIG_OWNER|ROTATION_CADENCE|ROTATOR|ROTATION_RUNBOOK)=' ops-vm/credentials/store.env.example` | `6` |
| 7 | No credential value is committed | `git ls-files ops-vm/credentials \| grep -Evc '(README.md|\.example)$'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash -n ops-vm/jobs/run-reconcile.sh && bash -n ops-vm/checks/reconcile-freshness.sh && echo SYNTAX-OK
grep -h '^OnCalendar' ops-vm/systemd/reconcile-full.timer ops-vm/systemd/reconcile-security.timer
grep -c 'is not the declared expected source host' ops-vm/jobs/run-reconcile.sh
# step 4 - no trigger recorded
rm -rf /tmp/t07 && mkdir -p /tmp/t07/ops-vm/credentials /tmp/t07/ops-vm/lib
cp "$CONTROL_PLANE_ROOT/ops-vm/lib/common.sh" /tmp/t07/ops-vm/lib/
printf 'RECONCILER_CREDENTIAL_FILE=/dev/null\nRECONCILER_ENVELOPE_EXPECTED_HOST=%s\n' "$(hostname)" > /tmp/t07/ops-vm/credentials/store.env
( cd /tmp/t07 && OPS_VM_TRIGGER= bash "$CONTROL_PLANE_ROOT/ops-vm/jobs/run-reconcile.sh" full; echo "rc=$?" )
# step 5 - no freshness file
( OPS_VM_METRICS=/tmp/nonexistent ops-vm/checks/reconcile-freshness.sh; echo "rc=$?" )
grep -Ec '^RECONCILER_(ENVELOPE_EXPECTED_HOST|ENVELOPE_RUN_CEILING_PER_DAY|ENVELOPE_ALERT_CONFIG_OWNER|ROTATION_CADENCE|ROTATOR|ROTATION_RUNBOOK)=' ops-vm/credentials/store.env.example
git ls-files ops-vm/credentials | grep -Evc '(README.md|\.example)$'
```

Expected output:

```
SYNTAX-OK
OnCalendar=daily
OnCalendar=hourly
1
<timestamp> FAIL-CLOSED: no scheduled trigger recorded for this run
rc=1
full: NO-RUN-RECORDED -> LEVEL-5
security: NO-RUN-RECORDED -> LEVEL-5
RECONCILE-FRESHNESS: BREACH
rc=5
6
0
```

### STOP rule

If the reconciler CLI contract published by lane L3 does not accept `--mode full|security` and `--emit-metrics <path>`: **do not modify `reconciler/**`, do not guess flags.** PARTITION rule 4 forbids reaching into another lane's source tree. Open a blocker (§1.4) with the decision line: *"The L3 reconciler CLI contract does not expose the mode and metrics flags this task's units invoke; L0 must arbitrate the published interface."* Separately, if the fifth-tier credential store on the host is world-readable or group-readable (`stat -c '%a' /var/lib/ops-vm/creds` is not `700`), STOP: Section 40.3 makes shell access to this host a trust boundary.

---

## L5-04-08 — Health computation job and report freshness

**Size:** S · **Depends on:** L5-04-04, L5-04-07, L4-COMPLETE · **Slug:** `health-report`
**Spec:** 52.1 — a single generated Operating System Health Report, **refreshed daily**, one headline state (Healthy / Degrading / Impaired), rendering **in the Grafana instance the platform already requires**; the headline is computed from **budget consumption, not the presence of a class**, with tolerances declared in `os-health.yaml` (Section 53.4) so it is calibratable without a code change; 51.2 — *"Health report freshness: refreshed daily… Amber; degrade openly rather than show stale data as current"*; AT-032 (self-observability).

**Boundary:** the signal definitions, the tolerances and the computation live in `os-health.yaml` and the metrics tier (L1/L4). This task provisions the **scheduled execution, the staleness banner and the freshness telemetry** on the VM. It never encodes a threshold.

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/jobs/run-health-report.sh` | Invokes the health-report generator; writes freshness telemetry |
| `ops-vm/systemd/health-report.service` / `.timer` | Daily refresh |
| `ops-vm/checks/health-report-freshness.sh` | Amber when older than 24h; renders the "stale" banner state |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t08-health-report"
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/jobs/run-health-report.sh <<'SHDOC'
#!/usr/bin/env bash
# Generates the Operating System Health Report (Section 52.1) on the schedule of
# Section 51.2. Thresholds and tolerances are read from os-health.yaml by the
# generator; this wrapper encodes none of them.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
OUT=/var/lib/ops-vm/health
install -d -m 0750 "$OUT"
start=$(date -u +%s)
set +e
os-health-report --output "$OUT/report.json" --emit-metrics "$OUT/health.prom"
rc=$?
set -e
now=$(date -u +%s)
if [ "$rc" -eq 0 ]; then
  printf 'ops_vm_job_last_success_timestamp{job_name="health-report"} %s\n' "$now" > "$OUT/health-freshness.prom"
  record_run health-report ok "seconds=$((now-start))"
else
  record_run health-report failed "rc=$rc"
  notify/bin/notify-job-result.sh health-report failed
fi
exit "$rc"
SHDOC
chmod +x ops-vm/jobs/run-health-report.sh

cat > ops-vm/systemd/health-report.service <<'UNITDOC'
[Unit]
Description=Operating System Health Report (Section 52.1)
[Service]
Type=oneshot
User=ops-vm
WorkingDirectory=/opt/control-plane
Environment=OPS_VM_TRIGGER=health-report.timer
ExecStart=/opt/control-plane/ops-vm/jobs/run-health-report.sh
UNITDOC

cat > ops-vm/systemd/health-report.timer <<'UNITDOC'
[Unit]
Description=Health report refreshed daily (Section 51.2)
[Timer]
OnCalendar=daily
Persistent=true
[Install]
WantedBy=timers.target
UNITDOC

cat > ops-vm/checks/health-report-freshness.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 51.2: health report refreshed daily; Amber on staleness. Degrade
# openly rather than show stale data as current.
set -euo pipefail
F=/var/lib/ops-vm/health/health-freshness.prom
if [ ! -f "$F" ]; then echo "HEALTH-REPORT: NO-RUN-RECORDED -> AMBER (render stale banner)"; exit 1; fi
ts=$(awk '{print $2}' "$F"); age=$(( ( $(date -u +%s) - ts ) / 3600 ))
if [ "$age" -ge 24 ]; then
  echo "HEALTH-REPORT: age=${age}h -> AMBER (render stale banner)"; exit 1
fi
echo "HEALTH-REPORT: age=${age}h -> OK"
SHDOC
chmod +x ops-vm/checks/health-report-freshness.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add ops-vm/jobs/run-health-report.sh ops-vm/systemd/health-report.service ops-vm/systemd/health-report.timer ops-vm/checks/health-report-freshness.sh
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-08: health computation job and report freshness"
git push -u origin "lane/5/04-t08-health-report"
gh pr create --base integration --title "L5-04-08: health computation job and report freshness" --body "Lane L5 phase 4 task L5-04-08. Paths: ops-vm/** only. Spec: 52.1, 51.2, AT-032."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Scripts parse | `bash -n ops-vm/jobs/run-health-report.sh && bash -n ops-vm/checks/health-report-freshness.sh && echo SYNTAX-OK` | `SYNTAX-OK` |
| 2 | Refresh is daily | `grep '^OnCalendar' ops-vm/systemd/health-report.timer` | `OnCalendar=daily` |
| 3 | No threshold or tolerance is hard-coded in the wrapper | `grep -Eic '(healthy|degrading|impaired|tolerance|amber_limit)' ops-vm/jobs/run-health-report.sh` | `0` |
| 4 | Staleness renders openly rather than as current | `grep -c 'render stale banner' ops-vm/checks/health-report-freshness.sh` | `2` |
| 5 | Missing report is Amber, not silence | SELF-VERIFY step 5 | `HEALTH-REPORT: NO-RUN-RECORDED -> AMBER (render stale banner)` then `rc=1` |
| 6 | Failure routes to the notification path | `grep -c 'notify-job-result.sh health-report failed' ops-vm/jobs/run-health-report.sh` | `1` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash -n ops-vm/jobs/run-health-report.sh && bash -n ops-vm/checks/health-report-freshness.sh && echo SYNTAX-OK
grep '^OnCalendar' ops-vm/systemd/health-report.timer
grep -Eic '(healthy|degrading|impaired|tolerance|amber_limit)' ops-vm/jobs/run-health-report.sh
grep -c 'render stale banner' ops-vm/checks/health-report-freshness.sh
sudo rm -f /var/lib/ops-vm/health/health-freshness.prom 2>/dev/null || true
ops-vm/checks/health-report-freshness.sh; echo "rc=$?"
grep -c 'notify-job-result.sh health-report failed' ops-vm/jobs/run-health-report.sh
```

Expected output:

```
SYNTAX-OK
OnCalendar=daily
0
2
HEALTH-REPORT: NO-RUN-RECORDED -> AMBER (render stale banner)
rc=1
1
```

### STOP rule

If the `os-health-report` generator published by lane L4 does not accept `--output` and `--emit-metrics`, or if it requires a threshold argument: **do not pass a threshold value and do not edit `metrics/**`.** Section 52.1 places the tolerances in `os-health.yaml` precisely so the headline is calibratable without a code change; a threshold supplied on the command line would move calibration onto this host. Open a blocker (§1.4) with the decision line: *"The health-report generator requires a threshold argument the operations VM must not supply; L0 must confirm the os-health.yaml-sourced interface."*

---

## L5-04-09 — Scorecard scheduled scan runner

**Size:** S · **Depends on:** L5-04-03 · **Slug:** `scorecard`
**Spec:** 99.2 subsystem M (Scorecard on the operations VM) and subsystem I (*"Scorecard scheduled scan with drop detection"*), 45.1 (**Scorecard configuration** is part of the minimum reconstruction set), 93.2 (a Scorecard score drop never sends the Founder to browse raw scores — it arrives as a decision prompt or as an owned line on the Reliability dimension, naming the product, the drop and the owner already acting on it).

**Boundary:** drop detection and the metric it feeds belong to the metrics tier. This task provisions the scan execution and writes the raw results where the metrics tier reads them. Repository targets come from the registry — never a hand-maintained list (invariant 52).

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/scorecard/config.env.example` | Scan cadence handle and output location (empty values) |
| `ops-vm/jobs/run-scorecard.sh` | Enumerates repositories from the registry and scans each |
| `ops-vm/systemd/scorecard.service` / `.timer` | Scheduled scan |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t09-scorecard"
mkdir -p ops-vm/scorecard
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/scorecard/config.env.example <<'ENVDOC'
# Scorecard scan configuration. Part of the minimum reconstruction set (45.1).
SCORECARD_OUTPUT_DIR=
SCORECARD_ONCALENDAR=
SCORECARD_TOKEN_FILE=          # read-only credential handle; never a value
ENVDOC

cat > ops-vm/jobs/run-scorecard.sh <<'SHDOC'
#!/usr/bin/env bash
# Scheduled Scorecard scan. Repositories are enumerated from the registry, never
# from a list in this file (invariant 52: product count is never hard-coded).
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/scorecard/config.env
set -a; . ops-vm/scorecard/config.env; set +a
require_env SCORECARD_OUTPUT_DIR SCORECARD_TOKEN_FILE
install -d -m 0750 "$SCORECARD_OUTPUT_DIR"

repos=$(list-repositories --from-registry)   # published by lane L1/L3 provisioning
[ -n "$repos" ] || fail_closed "registry returned no repositories; refusing to scan an empty set"

rc=0
for r in $repos; do
  GITHUB_AUTH_TOKEN="$(cat "$SCORECARD_TOKEN_FILE")" \
    scorecard --repo="$r" --format=json > "$SCORECARD_OUTPUT_DIR/${r//\//_}.json" || rc=1
done
if [ "$rc" -eq 0 ]; then
  record_run scorecard ok "repos=$(echo "$repos" | wc -w)"
else
  record_run scorecard failed "one or more scans failed"
  notify/bin/notify-job-result.sh scorecard failed
fi
exit "$rc"
SHDOC
chmod +x ops-vm/jobs/run-scorecard.sh

cat > ops-vm/systemd/scorecard.service <<'UNITDOC'
[Unit]
Description=Scorecard scheduled scan (Section 99.2 subsystem I; hosted per subsystem M)
[Service]
Type=oneshot
User=ops-vm
WorkingDirectory=/opt/control-plane
Environment=OPS_VM_TRIGGER=scorecard.timer
ExecStart=/opt/control-plane/ops-vm/jobs/run-scorecard.sh
UNITDOC

cat > ops-vm/systemd/scorecard.timer <<'UNITDOC'
[Unit]
Description=Scorecard scan cadence
[Timer]
OnCalendar=${SCORECARD_ONCALENDAR}
Persistent=true
[Install]
WantedBy=timers.target
UNITDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add ops-vm/scorecard ops-vm/jobs/run-scorecard.sh ops-vm/systemd/scorecard.service ops-vm/systemd/scorecard.timer
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-09: Scorecard scheduled scan runner"
git push -u origin "lane/5/04-t09-scorecard"
gh pr create --base integration --title "L5-04-09: Scorecard scheduled scan runner" --body "Lane L5 phase 4 task L5-04-09. Paths: ops-vm/** only. Spec: 99.2 subsystems I and M, 45.1, invariant 52."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Script parses | `bash -n ops-vm/jobs/run-scorecard.sh && echo SYNTAX-OK` | `SYNTAX-OK` |
| 2 | Repositories come from the registry | `grep -c 'list-repositories --from-registry' ops-vm/jobs/run-scorecard.sh` | `1` |
| 3 | No repository or product name is hard-coded | `grep -Ec '(github\.com/|owner/)' ops-vm/jobs/run-scorecard.sh` | `0` |
| 4 | An empty registry result fails closed rather than scanning nothing silently | `grep -c 'refusing to scan an empty set' ops-vm/jobs/run-scorecard.sh` | `1` |
| 5 | The token is a file handle, never a value | `grep -Ec '^SCORECARD_TOKEN_FILE=$' ops-vm/scorecard/config.env.example` | `1` |
| 6 | No real config committed | `git ls-files ops-vm/scorecard \| grep -Evc '\.example$'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash -n ops-vm/jobs/run-scorecard.sh && echo SYNTAX-OK
grep -c 'list-repositories --from-registry' ops-vm/jobs/run-scorecard.sh
grep -Ec '(github\.com/|owner/)' ops-vm/jobs/run-scorecard.sh
grep -c 'refusing to scan an empty set' ops-vm/jobs/run-scorecard.sh
grep -Ec '^SCORECARD_TOKEN_FILE=$' ops-vm/scorecard/config.env.example
git ls-files ops-vm/scorecard | grep -Evc '\.example$'
```

Expected output:

```
SYNTAX-OK
1
0
1
1
0
```

### STOP rule

If `list-repositories --from-registry` does not exist on the host, or returns repositories that are not in the registry: **do not write a repository list into this script and do not scan a set you assembled yourself.** Invariant 52 forbids a hard-coded product list and AT-001 tests it. Open a blocker (§1.4) with the decision line: *"The registry-driven repository enumeration published by lane L1/L3 is unavailable on the operations VM; L0 must confirm the published enumeration interface."*

---

## L5-04-10 — Renovate self-hosted runner

**Size:** M · **Depends on:** L5-04-03 · **Slug:** `renovate`
**Spec:** 99.2 subsystem M (Renovate runs on the operations VM), 45.1 (**Renovate configuration** is part of the minimum reconstruction set), 94.7 (Renovate: nightly, dependency PRs, free — the fixed-cost line of invariant 83), 30.3 (**Renovate self-hosted repository limits** are a named unverified capability assumption, confirmed before the phase that depends on them), 33.2 / D74 / D89 (the auto-merge-on-green class and the two-ruleset bypass split live in the repository's rulesets and in `policies.yaml` — never on this host), invariant 52 (product count is never hard-coded), invariant 85 (pinning).

**Boundary:** the ruleset bypass actor, the `renovate-path-guard` required status check and the per-product disposition policy are repository-protection and workflow surfaces owned by L0 and L2. This task provisions **where and how Renovate executes**. It writes no ruleset, no bypass actor and no fleet-wide auto-merge default.

**One shared file is created here.** `notify/bin/notify-job-result.sh` is the single job-result notifier that L5-04-06, L5-04-07, L5-04-08 and L5-04-09 already invoke. No earlier task in this file writes under `notify/`, so it is created here — the first task in this phase that owns a `notify/**` path — and every later task uses it unchanged.

### Files created

| Path | Purpose |
| --- | --- |
| `notify/bin/notify-job-result.sh` | The one job-result notifier; destination is configuration (Section 92.11) |
| `notify/bin/notify.env.example` | The designated-channel webhook key (empty value) |
| `ops-vm/renovate/renovate.env.example` | Token handle, confirmed repository limit, log dir, cadence (empty values) |
| `ops-vm/renovate/config.js` | Self-hosted Renovate configuration; autodiscover off |
| `ops-vm/jobs/run-renovate.sh` | Enumerates repositories from the registry and runs one pass |
| `ops-vm/systemd/renovate.service` / `.timer` | Scheduled run |
| `ops-vm/checks/renovate-no-bypass-config.sh` | Fails if this host carries a ruleset, bypass actor or auto-merge default |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t10-renovate"
mkdir -p notify/bin ops-vm/renovate ops-vm/jobs ops-vm/systemd ops-vm/checks
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > notify/bin/notify.env.example <<'ENVDOC'
# The designated messaging channel is a configuration value, never a hard-coded
# destination (Section 92.11). The real notify.env is supplied on the host.
DESIGNATED_CHANNEL_WEBHOOK_URL=
ENVDOC

cat > notify/bin/notify-job-result.sh <<'SHDOC'
#!/usr/bin/env bash
# The single job-result notifier every operations-VM job calls.
# Section 92.11: a push event is delivered to the designated messaging channel,
# which is a configuration value and never a hard-coded destination.
# Section 44.3: job and backup failures alert on the product discipline.
# Usage: notify-job-result.sh <job-name> <ok|failed> [detail]
set -euo pipefail
JOB="${1:?usage: notify-job-result.sh <job-name> <ok|failed> [detail]}"
STATUS="${2:?usage: notify-job-result.sh <job-name> <ok|failed> [detail]}"
DETAIL="${3:-}"
case "$STATUS" in
  ok|failed) ;;
  *) echo "NOTIFY: FAIL-CLOSED (status must be ok or failed; got '$STATUS')"; exit 1 ;;
esac
CFG="${NOTIFY_ENV_FILE:-notify/bin/notify.env}"
[ -f "$CFG" ] || { echo "NOTIFY: FAIL-CLOSED (no $CFG)"; exit 1; }
set -a; . "$CFG"; set +a
[ -n "${DESIGNATED_CHANNEL_WEBHOOK_URL:-}" ] \
  || { echo "NOTIFY: FAIL-CLOSED (DESIGNATED_CHANNEL_WEBHOOK_URL is empty)"; exit 1; }
body=$(printf '{"job":"%s","status":"%s","host":"%s","at":"%s","detail":"%s"}' \
  "$JOB" "$STATUS" "$(hostname)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$DETAIL")
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 \
  -H 'Content-Type: application/json' --data "$body" "$DESIGNATED_CHANNEL_WEBHOOK_URL" || echo 000)
case "$code" in
  2*) echo "NOTIFY: SENT $JOB $STATUS" ;;
  *)  echo "NOTIFY: FAIL-CLOSED (webhook http $code)"; exit 1 ;;
esac
SHDOC
chmod +x notify/bin/notify-job-result.sh
printf 'bin/notify.env\n' > notify/.gitignore
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/renovate/renovate.env.example <<'ENVDOC'
# Self-hosted Renovate on the operations VM. Part of the minimum reconstruction
# set (Section 45.1). Repository targets never appear here (invariant 52).
RENOVATE_TOKEN_FILE=
RENOVATE_REPO_LIMIT=
RENOVATE_LOG_DIR=
RENOVATE_ONCALENDAR=
ENVDOC

cat > ops-vm/renovate/config.js <<'JSDOC'
// Self-hosted Renovate configuration for the operations VM.
// Part of the minimum reconstruction set (Section 45.1): a rebuild replays this
// file; it is never re-derived by hand.
// The repository list is supplied by run-renovate.sh from the registry at run
// time (invariant 52). Discovery is off, so no repository the registry does not
// name is ever picked up.
// Auto-merge-on-green is a repository-side policy exception carried by two
// rulesets and a policies.yaml entry (D74, D89). This host configures none of
// it, and the fleet default here is closed (invariant 79, invariant 80).
module.exports = {
  platform: 'github',
  autodiscover: false,
  onboarding: false,
  requireConfig: 'optional',
  dependencyDashboard: true,
  automerge: false,
  ignoreScripts: true,
};
JSDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/jobs/run-renovate.sh <<'SHDOC'
#!/usr/bin/env bash
# One self-hosted Renovate pass. Repositories are enumerated from the registry,
# never listed in this file or in config.js (invariant 52).
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/renovate/renovate.env
set -a; . ops-vm/renovate/renovate.env; set +a
require_env RENOVATE_TOKEN_FILE RENOVATE_REPO_LIMIT RENOVATE_LOG_DIR
require_file "$RENOVATE_TOKEN_FILE"

repos=$(list-repositories --from-registry)   # published by lane L1/L3 provisioning
[ -n "$repos" ] || fail_closed "registry returned no repositories; refusing to run Renovate over an empty set"
count=$(echo "$repos" | wc -w)
[ "$count" -le "$RENOVATE_REPO_LIMIT" ] \
  || fail_closed "registry returned $count repositories, above the confirmed self-hosted repository limit $RENOVATE_REPO_LIMIT (Section 30.3 unverified-capability list)"

install -d -m 0750 "$RENOVATE_LOG_DIR"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
set +e
RENOVATE_TOKEN="$(cat "$RENOVATE_TOKEN_FILE")" \
RENOVATE_CONFIG_FILE=ops-vm/renovate/config.js \
RENOVATE_REPOSITORIES="$(echo "$repos" | tr ' ' ',')" \
  renovate > "$RENOVATE_LOG_DIR/renovate-$stamp.log" 2>&1
rc=$?
set -e
if [ "$rc" -eq 0 ]; then
  record_run renovate ok "repos=$count"
else
  record_run renovate failed "repos=$count rc=$rc"
  notify/bin/notify-job-result.sh renovate failed "rc=$rc"
fi
exit "$rc"
SHDOC
chmod +x ops-vm/jobs/run-renovate.sh

cat > ops-vm/systemd/renovate.service <<'UNITDOC'
[Unit]
Description=Self-hosted Renovate dependency pass (Section 99.2 subsystem M)
[Service]
Type=oneshot
User=ops-vm
WorkingDirectory=/opt/control-plane
Environment=OPS_VM_TRIGGER=renovate.timer
ExecStart=/opt/control-plane/ops-vm/jobs/run-renovate.sh
UNITDOC

cat > ops-vm/systemd/renovate.timer <<'UNITDOC'
[Unit]
Description=Renovate cadence (Section 94.7: nightly)
[Timer]
OnCalendar=${RENOVATE_ONCALENDAR}
Persistent=true
[Install]
WantedBy=timers.target
UNITDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/renovate-no-bypass-config.sh <<'SHDOC'
#!/usr/bin/env bash
# D89: the Renovate auto-merge bypass is split across two repository rulesets and
# lives in the repository's protection configuration. The operations VM never
# carries a ruleset, a bypass actor or a fleet-wide auto-merge default.
set -euo pipefail
bad=$(for f in ops-vm/renovate/*; do
        sed 's|//.*||' "$f" | grep -En 'bypass|ruleset|automerge: *true' | sed "s|^|$f:|" || true
      done)
if [ -n "$bad" ]; then echo "RENOVATE-NO-BYPASS: FAIL"; echo "$bad"; exit 1; fi
echo "RENOVATE-NO-BYPASS: PASS"
SHDOC
chmod +x ops-vm/checks/renovate-no-bypass-config.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add notify/bin/notify-job-result.sh notify/bin/notify.env.example notify/.gitignore ops-vm/renovate ops-vm/jobs/run-renovate.sh ops-vm/systemd/renovate.service ops-vm/systemd/renovate.timer ops-vm/checks/renovate-no-bypass-config.sh
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-10: self-hosted Renovate runner and the shared job-result notifier"
git push -u origin "lane/5/04-t10-renovate"
gh pr create --base integration --title "L5-04-10: Renovate self-hosted runner" --body "Lane L5 phase 4 task L5-04-10. Paths: ops-vm/**, notify/** only. Spec: 99.2 subsystem M, 45.1, 94.7, 30.3, 92.11, D74, D89, invariants 52, 83, 85."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Both scripts parse | `bash -n notify/bin/notify-job-result.sh && bash -n ops-vm/jobs/run-renovate.sh && echo SYNTAX-OK` | `SYNTAX-OK` |
| 2 | The notifier hard-codes no destination | `grep -Ec 'https?://' notify/bin/notify-job-result.sh` | `0` |
| 3 | The notifier refuses an unknown status | SELF-VERIFY, the `probe bogus` line | `NOTIFY: FAIL-CLOSED (status must be ok or failed; got 'bogus')` then `rc=1` |
| 4 | The notifier fails closed with no channel configured | SELF-VERIFY, the `NOTIFY_ENV_FILE=/tmp/empty-notify.env` line | `NOTIFY: FAIL-CLOSED (DESIGNATED_CHANNEL_WEBHOOK_URL is empty)` then `rc=1` |
| 5 | Repositories come from the registry | `grep -c 'list-repositories --from-registry' ops-vm/jobs/run-renovate.sh` | `1` |
| 6 | No repository is discovered outside the registry | `grep -c 'autodiscover: false' ops-vm/renovate/config.js` | `1` |
| 7 | No ruleset, bypass actor or auto-merge default on this host | `ops-vm/checks/renovate-no-bypass-config.sh` | `RENOVATE-NO-BYPASS: PASS` |
| 8 | The self-hosted repository limit is declared, never assumed | `grep -Ec '^RENOVATE_REPO_LIMIT=$' ops-vm/renovate/renovate.env.example` | `1` |
| 9 | No real Renovate env or notify env is tracked | `git ls-files ops-vm/renovate notify/bin \| grep -Evc '(\.example|\.js|\.sh)$'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
bash -n notify/bin/notify-job-result.sh && bash -n ops-vm/jobs/run-renovate.sh && echo SYNTAX-OK
grep -Ec 'https?://' notify/bin/notify-job-result.sh
notify/bin/notify-job-result.sh probe bogus; echo "rc=$?"
NOTIFY_ENV_FILE=/tmp/absent-notify.env notify/bin/notify-job-result.sh probe failed; echo "rc=$?"
printf 'DESIGNATED_CHANNEL_WEBHOOK_URL=\n' > /tmp/empty-notify.env
NOTIFY_ENV_FILE=/tmp/empty-notify.env notify/bin/notify-job-result.sh probe failed; echo "rc=$?"
grep -c 'list-repositories --from-registry' ops-vm/jobs/run-renovate.sh
grep -c 'autodiscover: false' ops-vm/renovate/config.js
ops-vm/checks/renovate-no-bypass-config.sh
grep -Ec '^RENOVATE_REPO_LIMIT=$' ops-vm/renovate/renovate.env.example
git ls-files ops-vm/renovate notify/bin | grep -Evc '(\.example|\.js|\.sh)$'
```

Expected output:

```
SYNTAX-OK
0
NOTIFY: FAIL-CLOSED (status must be ok or failed; got 'bogus')
rc=1
NOTIFY: FAIL-CLOSED (no /tmp/absent-notify.env)
rc=1
NOTIFY: FAIL-CLOSED (DESIGNATED_CHANNEL_WEBHOOK_URL is empty)
rc=1
1
1
RENOVATE-NO-BYPASS: PASS
1
0
```

### STOP rule

Section 30.3 lists **Renovate self-hosted repository limits** among the capability assumptions that are confirmed before the phase depending on them. If `RENOVATE_REPO_LIMIT` is absent from the host `renovate.env`, or the registry returns more repositories than it declares: **do not raise the limit, do not split the run into batches you invented, do not shard the registry.** Open a blocker (§1.4) with the decision line: *"The confirmed self-hosted Renovate repository limit is absent or is exceeded by the registry's repository count; Section 30.3 requires the limit to be confirmed before the dependent phase runs."*

Separately, if anything in this task would add a ruleset, a bypass actor or a fleet-wide `automerge: true` on this host, **stop.** D89 states the compensating check must not sit inside the ruleset it compensates for, and neither the ruleset nor its bypass is an operations-VM surface. Open a blocker with the decision line: *"A Renovate bypass or auto-merge default was requested on the operations VM; D74 and D89 place both in repository rulesets and `policies.yaml`, which lane L5 does not own."*

---

## L5-04-11 — Asset inventory store and the expiry-check job

**Size:** M · **Depends on:** L5-04-01, L5-04-03 · **Slug:** `expiry-check`
**Spec:** 49.1 — every inventory entry carries *"an expiry date, a named owner, and an alert threshold of at least 30 days"*; the inventory also carries an entry for **each control-plane machine credential** per Section 40.1, the two Hermes hosts, and the **self-hosted CI runner estate** as a named asset class. 49.2 — external-deadline entries carry a named owner, the announced deadline and a **configurable alert lead time, 30 days minimum by default, set longer for anything requiring a large migration**, and the owner sets it when the entry is created. 94.7 — *"Asset expiry check | Daily | 30-day expiry and vendor-deadline alerts"*. 92.11 — the push list is closed; the expiry sweep is a **wait surface**, and only its own failure is a push event. Invariant 47 (every run writes its result); Section 53.1 (a clean run is recorded as clean).

**Boundary:** the entry schema, the field table, the validator and every entry file are subsystem Q and are built by the lane's asset phase under `assets/inventory/**`, `assets/deadlines/**`, `assets/FIELDS.md` and `assets/validate_assets.py`. **This task creates no entry file, no field table and no validator.** It provisions the VM-side daily execution that reads them, plus the floor check that Section 49.1's "at least 30 days" is mechanical rather than remembered.

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/inventory/README.md` | How the VM reads `assets/**`, read-only, and what it never writes |
| `ops-vm/inventory/inventory.env.example` | Inventory and deadline directory handles, report output (empty values) |
| `ops-vm/jobs/expiry_check.py` | Computes days-to-expiry per entry; emits report and Prometheus text |
| `ops-vm/jobs/run-expiry-check.sh` | Wrapper: runs the sweep, records the run, notifies only on failure |
| `ops-vm/systemd/expiry-check.service` / `.timer` | Daily sweep (Section 94.7) |
| `ops-vm/checks/inventory-alert-lead-floor.sh` | Fails when any entry declares `alert_days` below 30 |
| `ops-vm/checks/expiry-check-freshness.sh` | Amber when the sweep is older than 24 hours |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t11-expiry-check"
mkdir -p ops-vm/inventory ops-vm/jobs ops-vm/systemd ops-vm/checks
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/inventory/README.md <<'MDDOC'
# The operations VM and the asset inventory

The inventory itself lives at `assets/inventory/` (one file per asset) and
`assets/deadlines/` (one file per announced external deadline). Its schema, its
field table and its validator are built by the lane's asset phase. The
operations VM is a **reader**: the daily sweep in `ops-vm/jobs/` opens those
files, computes days-to-expiry, and writes a report and Prometheus text under
`/var/lib/ops-vm/inventory/`. It never creates, edits or deletes an entry.

Field names used by the sweep are the binding common fields of Section 49.1:
`asset_id`, `asset_class`, `owner`, `expiry_date`, `alert_days`, `cost_band`,
`spec_reference`.

Two rules the sweep enforces rather than assumes:

* `alert_days` is at least 30 (Section 49.1). The floor is a specification
  constant; the value above the floor is owner-set at entry creation and is
  longer wherever the migration behind the deadline is large (Section 49.2).
* The sweep is a **wait surface** (Section 92.11). Reaching an alert threshold
  renders on the report and in the metric; it does not page anyone. Only the
  sweep's own failure is a push event, on the job-failure discipline of
  Section 44.3.

Every run writes its result and a clean run is recorded as clean (Section 53.1).
MDDOC

cat > ops-vm/inventory/inventory.env.example <<'ENVDOC'
# Where the sweep reads and writes. Directory handles only; no asset data here.
INVENTORY_DIR=
DEADLINES_DIR=
INVENTORY_REPORT_DIR=
ENVDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/jobs/expiry_check.py <<'PYDOC'
#!/usr/bin/env python3
"""Daily expiry-and-deadline sweep on the operations VM (Section 94.7).

Reads the asset inventory and the deadline watch as data (never as source),
computes days-to-expiry per entry against the entry's own owner-set alert lead,
and writes a report plus Prometheus text. Wait surface only: this program never
sends a notification (Section 92.11).

Exit codes:
  0  sweep completed; entries within their alert lead are listed on the report
  1  sweep could not run (missing directory, unreadable or malformed entry)
"""
import datetime
import os
import sys

import yaml

FLOOR_DAYS = 30  # Section 49.1: "an alert threshold of at least 30 days"


def load(directory):
    out = []
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".yaml"):
            continue
        path = os.path.join(directory, name)
        with open(path, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle)
        if not isinstance(doc, dict):
            raise ValueError("%s is not a mapping" % path)
        out.append((path, doc))
    return out


def main():
    inv = os.environ.get("INVENTORY_DIR", "")
    dea = os.environ.get("DEADLINES_DIR", "")
    rep = os.environ.get("INVENTORY_REPORT_DIR", "")
    for key, value in (("INVENTORY_DIR", inv), ("DEADLINES_DIR", dea),
                       ("INVENTORY_REPORT_DIR", rep)):
        if not value:
            print("EXPIRY-SWEEP: FAIL-CLOSED (%s is empty)" % key)
            return 1
        if key != "INVENTORY_REPORT_DIR" and not os.path.isdir(value):
            print("EXPIRY-SWEEP: FAIL-CLOSED (%s is not a directory: %s)"
                  % (key, value))
            return 1
    os.makedirs(rep, exist_ok=True)
    today = datetime.date.today()
    rows, due, bad = [], 0, 0
    try:
        entries = load(inv) + load(dea)
    except Exception as exc:                      # malformed entry: fail closed
        print("EXPIRY-SWEEP: FAIL-CLOSED (%s)" % exc)
        return 1
    for path, doc in entries:
        aid = doc.get("asset_id") or doc.get("deadline_id") or path
        owner = doc.get("owner", "")
        raw = str(doc.get("expiry_date", doc.get("deadline_date", "")))
        lead = doc.get("alert_days", doc.get("alert_lead_days"))
        if not owner or owner == "unassigned":
            print("EXPIRY-SWEEP: FAIL-CLOSED (%s has no named owner)" % aid)
            bad += 1
            continue
        try:
            when = datetime.date.fromisoformat(raw)
        except ValueError:
            print("EXPIRY-SWEEP: FAIL-CLOSED (%s expiry %r is not ISO-8601)"
                  % (aid, raw))
            bad += 1
            continue
        try:
            lead = int(lead)
        except (TypeError, ValueError):
            print("EXPIRY-SWEEP: FAIL-CLOSED (%s has no integer alert lead)" % aid)
            bad += 1
            continue
        if lead < FLOOR_DAYS:
            print("EXPIRY-SWEEP: FAIL-CLOSED (%s alert lead %d is below the "
                  "Section 49.1 floor of %d)" % (aid, lead, FLOOR_DAYS))
            bad += 1
            continue
        days = (when - today).days
        rows.append((aid, owner, raw, lead, days))
        if days <= lead:
            due += 1
    if bad:
        print("EXPIRY-SWEEP: FAIL (%d unusable entries)" % bad)
        return 1
    stamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    with open(os.path.join(rep, "expiry-report.txt"), "w", encoding="utf-8") as fh:
        fh.write("# expiry sweep %s\n" % stamp)
        for aid, owner, raw, lead, days in rows:
            state = "DUE" if days <= lead else "ok"
            fh.write("%s\t%s\t%s\tlead=%d\tdays=%d\t%s\n"
                     % (aid, owner, raw, lead, days, state))
    with open(os.path.join(rep, "expiry.prom"), "w", encoding="utf-8") as fh:
        for aid, owner, raw, lead, days in rows:
            fh.write('ops_vm_asset_days_to_expiry{asset_id="%s",owner="%s"} %d\n'
                     % (aid, owner, days))
        fh.write("ops_vm_assets_within_alert_lead %d\n" % due)
    print("EXPIRY-SWEEP: PASS (%d entries, %d within alert lead)"
          % (len(rows), due))
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYDOC
chmod +x ops-vm/jobs/expiry_check.py
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/jobs/run-expiry-check.sh <<'SHDOC'
#!/usr/bin/env bash
# Daily expiry-and-deadline sweep (Section 94.7). Wait surface only: reaching an
# alert threshold renders on the report; only the sweep's own failure pushes
# (Sections 92.11, 44.3).
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/inventory/inventory.env
set -a; . ops-vm/inventory/inventory.env; set +a
require_env INVENTORY_DIR DEADLINES_DIR INVENTORY_REPORT_DIR
set +e
python3 ops-vm/jobs/expiry_check.py
rc=$?
set -e
now=$(date -u +%s)
if [ "$rc" -eq 0 ]; then
  printf 'ops_vm_job_last_success_timestamp{job_name="expiry-check"} %s\n' "$now" \
    > "$INVENTORY_REPORT_DIR/expiry-freshness.prom"
  record_run expiry-check ok "report=$INVENTORY_REPORT_DIR/expiry-report.txt"
else
  record_run expiry-check failed "rc=$rc"
  notify/bin/notify-job-result.sh expiry-check failed "rc=$rc"
fi
exit "$rc"
SHDOC
chmod +x ops-vm/jobs/run-expiry-check.sh

cat > ops-vm/systemd/expiry-check.service <<'UNITDOC'
[Unit]
Description=Asset expiry and vendor-deadline sweep (Sections 49.1, 49.2, 94.7)
[Service]
Type=oneshot
User=ops-vm
WorkingDirectory=/opt/control-plane
Environment=OPS_VM_TRIGGER=expiry-check.timer
ExecStart=/opt/control-plane/ops-vm/jobs/run-expiry-check.sh
UNITDOC

cat > ops-vm/systemd/expiry-check.timer <<'UNITDOC'
[Unit]
Description=Asset expiry check daily (Section 94.7)
[Timer]
OnCalendar=daily
Persistent=true
[Install]
WantedBy=timers.target
UNITDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/inventory-alert-lead-floor.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 49.1: every entry carries an alert threshold of at least 30 days.
# The floor is a specification constant and is checked, never remembered.
set -euo pipefail
DIR="${1:?usage: inventory-alert-lead-floor.sh <inventory-dir>}"
bad=0
for f in "$DIR"/*.yaml; do
  [ -e "$f" ] || continue
  v=$(awk -F': *' '/^alert_days:/{print $2}' "$f" | tr -d '"' | head -1)
  case "$v" in
    ''|*[!0-9]*) echo "no integer alert_days: $f"; bad=1; continue ;;
  esac
  if [ "$v" -lt 30 ]; then echo "alert_days $v below the Section 49.1 floor: $f"; bad=1; fi
done
if [ "$bad" -eq 0 ]; then echo "ALERT-LEAD-FLOOR: PASS"; else echo "ALERT-LEAD-FLOOR: FAIL"; exit 1; fi
SHDOC
chmod +x ops-vm/checks/inventory-alert-lead-floor.sh

cat > ops-vm/checks/expiry-check-freshness.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 94.7: the sweep runs daily. Degrade openly rather than show a stale
# sweep as current (Section 51.2).
set -euo pipefail
F="${1:-/var/lib/ops-vm/inventory/expiry-freshness.prom}"
if [ ! -f "$F" ]; then echo "EXPIRY-CHECK: NO-RUN-RECORDED -> AMBER (render stale banner)"; exit 1; fi
ts=$(awk '{print $2}' "$F"); age=$(( ( $(date -u +%s) - ts ) / 3600 ))
if [ "$age" -ge 24 ]; then echo "EXPIRY-CHECK: age=${age}h -> AMBER (render stale banner)"; exit 1; fi
echo "EXPIRY-CHECK: age=${age}h -> OK"
SHDOC
chmod +x ops-vm/checks/expiry-check-freshness.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add ops-vm/inventory ops-vm/jobs/expiry_check.py ops-vm/jobs/run-expiry-check.sh ops-vm/systemd/expiry-check.service ops-vm/systemd/expiry-check.timer ops-vm/checks/inventory-alert-lead-floor.sh ops-vm/checks/expiry-check-freshness.sh
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-11: VM-side asset inventory reader and the daily expiry-check job"
git push -u origin "lane/5/04-t11-expiry-check"
gh pr create --base integration --title "L5-04-11: asset inventory reader and expiry-check job" --body "Lane L5 phase 4 task L5-04-11. Paths: ops-vm/** only. Spec: 49.1, 49.2, 94.7, 92.11, 44.3, 53.1, invariant 47."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Sweep and wrapper parse | `python3 -m py_compile ops-vm/jobs/expiry_check.py && bash -n ops-vm/jobs/run-expiry-check.sh && echo SYNTAX-OK` | `SYNTAX-OK` |
| 2 | The sweep passes on a conforming fixture | SELF-VERIFY, the first `expiry_check.py` run | `EXPIRY-SWEEP: PASS (1 entries, 0 within alert lead)` |
| 3 | The sweep fails closed on a sub-floor alert lead | SELF-VERIFY, the run after `alert_days: 7` | `EXPIRY-SWEEP: FAIL-CLOSED (fixture-cert alert lead 7 is below the Section 49.1 floor of 30)` then `rc=1` |
| 4 | The sweep fails closed on an unowned entry | SELF-VERIFY, the run after `owner: unassigned` | `EXPIRY-SWEEP: FAIL-CLOSED (fixture-cert has no named owner)` then `rc=1` |
| 5 | The floor check rejects the same entry | SELF-VERIFY, the second `inventory-alert-lead-floor.sh` line | `ALERT-LEAD-FLOOR: FAIL` then `rc=1` |
| 6 | The sweep never notifies | `grep -c 'notify-job-result' ops-vm/jobs/expiry_check.py` | `0` |
| 7 | Only sweep failure pushes | `grep -c 'notify/bin/notify-job-result.sh expiry-check failed' ops-vm/jobs/run-expiry-check.sh` | `1` |
| 8 | This task writes no inventory entry | `git diff --cached --name-only \| grep -c '^assets/'` | `0` |
| 9 | The sweep is daily | `grep '^OnCalendar' ops-vm/systemd/expiry-check.timer` | `OnCalendar=daily` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python3 -m py_compile ops-vm/jobs/expiry_check.py && bash -n ops-vm/jobs/run-expiry-check.sh && echo SYNTAX-OK
rm -rf /tmp/t11 && mkdir -p /tmp/t11/inv /tmp/t11/dea /tmp/t11/rep
cat > /tmp/t11/inv/fixture-cert.yaml <<'EOF'
asset_id: fixture-cert
asset_class: certificate
owner: fixture-person
expiry_date: "2099-01-01"
alert_days: 30
cost_band: none
spec_reference: "49.1"
EOF
INVENTORY_DIR=/tmp/t11/inv DEADLINES_DIR=/tmp/t11/dea INVENTORY_REPORT_DIR=/tmp/t11/rep python3 ops-vm/jobs/expiry_check.py
ops-vm/checks/inventory-alert-lead-floor.sh /tmp/t11/inv
sed -i 's/^alert_days: 30$/alert_days: 7/' /tmp/t11/inv/fixture-cert.yaml
INVENTORY_DIR=/tmp/t11/inv DEADLINES_DIR=/tmp/t11/dea INVENTORY_REPORT_DIR=/tmp/t11/rep python3 ops-vm/jobs/expiry_check.py; echo "rc=$?"
ops-vm/checks/inventory-alert-lead-floor.sh /tmp/t11/inv; echo "rc=$?"
sed -i -e 's/^alert_days: 7$/alert_days: 30/' -e 's/^owner: fixture-person$/owner: unassigned/' /tmp/t11/inv/fixture-cert.yaml
INVENTORY_DIR=/tmp/t11/inv DEADLINES_DIR=/tmp/t11/dea INVENTORY_REPORT_DIR=/tmp/t11/rep python3 ops-vm/jobs/expiry_check.py; echo "rc=$?"
grep -c 'notify-job-result' ops-vm/jobs/expiry_check.py
grep -c 'notify/bin/notify-job-result.sh expiry-check failed' ops-vm/jobs/run-expiry-check.sh
grep '^OnCalendar' ops-vm/systemd/expiry-check.timer
```

Expected output:

```
SYNTAX-OK
EXPIRY-SWEEP: PASS (1 entries, 0 within alert lead)
ALERT-LEAD-FLOOR: PASS
EXPIRY-SWEEP: FAIL-CLOSED (fixture-cert alert lead 7 is below the Section 49.1 floor of 30)
EXPIRY-SWEEP: FAIL (1 unusable entries)
rc=1
alert_days 7 below the Section 49.1 floor: /tmp/t11/inv/fixture-cert.yaml
ALERT-LEAD-FLOOR: FAIL
rc=1
EXPIRY-SWEEP: FAIL-CLOSED (fixture-cert has no named owner)
EXPIRY-SWEEP: FAIL (1 unusable entries)
rc=1
0
1
OnCalendar=daily
```

### STOP rule

If `assets/inventory/` or `assets/deadlines/` does not exist on the branch, or the lane's asset phase has not merged its validator: **do not create an entry, a directory of entries or a second validator here.** PARTITION rule 5 is additive-only within a lane and rule 3 forbids a second copy of a shared surface; an inventory entry is operational data with a named owner, and inventing one puts a fabricated owner and a fabricated expiry date into a store that drives alerts. Open a blocker (§1.4) with the decision line: *"The Section 49 asset inventory is not present on `integration`; the operations VM's daily sweep has nothing to read and L0 must confirm the merge order of the lane's asset phase."*

If the sweep reports `FAIL-CLOSED (… alert lead … is below the Section 49.1 floor …)` on a real entry, **do not raise that entry's `alert_days` to clear the sweep.** The lead is owner-set at entry creation and is longer, never shorter, where the migration behind it is large (Section 49.2). Open a blocker with the decision line: *"An inventory entry declares an alert lead below the Section 49.1 30-day floor; the entry's named owner must set the lead, not the operations VM."*

---

## L5-04-12 — Restore-rotation scheduler

**Size:** S · **Depends on:** L5-04-03, L2-COMPLETE · **Slug:** `restore-rotation`
**Spec:** 94.7 — *"Restore-rotation scheduler | Nightly | Advances the rolling restore rotation and opens the restore-verification task for the next product due"*; 44.2 and invariant 4 — restore tests run **monthly on a rotating subset**, and **every product is successfully restore-tested within any rolling 90-day window**; `classification.reliability_criticality` may tighten the cadence and never loosens it; a `restore_tested` date older than the window fails CI. SIG-17 (restore-test currency: **Amber approaching, Blocking past**). Section 53.1 — `product.yaml` `restore_tested` compared against the newest passing record in `records/restore-tests/` is **Blocking**: a declared date with no matching record is an unevidenced reliability claim. Invariant 3 (an untested backup is treated as no backup).

**Boundary:** `restore-production.yml` and the restore-test workflow are lane L2's (`.github/workflows/**`, `templates/workflows/**`); `records/restore-tests/` is lane L4's. This task schedules the rotation and opens the verification task through the **published CLI**; it invokes those surfaces and edits neither.

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/jobs/restore_rotation.py` | Computes the next-due set from declared data; never chooses a cadence |
| `ops-vm/jobs/run-restore-rotation.sh` | Wrapper: runs the computation, opens the task, records the run |
| `ops-vm/systemd/restore-rotation.service` / `.timer` | Nightly advance (Section 94.7) |
| `ops-vm/checks/restore-rotation-coverage.sh` | SIG-17 states: Amber approaching, Blocking past |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t12-restore-rotation"
mkdir -p ops-vm/jobs ops-vm/systemd ops-vm/checks
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/jobs/restore_rotation.py <<'PYDOC'
#!/usr/bin/env python3
"""Advance the rolling restore rotation (Section 94.7).

Reads, as data and read-only:
  * the product registry, for each product's id and
    classification.reliability_criticality
  * the newest passing record per product under the restore-test record store

Computes days since each product's newest passing restore test and compares it
against that product's required window. The windows are the ones Section 44.2
and invariant 4 state literally: a 90-day floor for every product, tightened to
30 days where reliability_criticality is critical. No window is chosen here and
none is loosened (invariant 4).

Emits the next-due product id per line on stdout, most overdue first.
Exit codes: 0 computed; 1 fail-closed (missing input, unknown criticality).
"""
import datetime
import json
import os
import sys

import yaml

FLOOR_DAYS = 90        # invariant 4: the rolling 90-day floor for every product
CRITICAL_DAYS = 30     # Section 44.2: critical tightens to 30 days


def window_for(criticality):
    if criticality == "critical":
        return CRITICAL_DAYS
    if criticality in ("high", "medium", "low"):
        return FLOOR_DAYS
    raise ValueError("unknown reliability_criticality %r" % criticality)


def main():
    reg = os.environ.get("PRODUCT_REGISTRY_FILE", "")
    recs = os.environ.get("RESTORE_RECORD_DIR", "")
    if not reg or not os.path.isfile(reg):
        print("RESTORE-ROTATION: FAIL-CLOSED (PRODUCT_REGISTRY_FILE absent)")
        return 1
    if not recs or not os.path.isdir(recs):
        print("RESTORE-ROTATION: FAIL-CLOSED (RESTORE_RECORD_DIR absent)")
        return 1
    with open(reg, "r", encoding="utf-8") as fh:
        products = yaml.safe_load(fh) or {}
    rows = products.get("products", [])
    if not rows:
        print("RESTORE-ROTATION: FAIL-CLOSED (registry lists no products)")
        return 1
    newest = {}
    for name in os.listdir(recs):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(recs, name), "r", encoding="utf-8") as fh:
            rec = json.load(fh)
        if rec.get("result") != "pass":
            continue
        pid, when = rec.get("product"), rec.get("at", "")[:10]
        if not pid or not when:
            continue
        if pid not in newest or when > newest[pid]:
            newest[pid] = when
    today = datetime.date.today()
    due = []
    for row in rows:
        pid = row.get("id")
        try:
            win = window_for(row.get("classification", {}).get("reliability_criticality"))
        except ValueError as exc:
            print("RESTORE-ROTATION: FAIL-CLOSED (%s: %s)" % (pid, exc))
            return 1
        last = newest.get(pid)
        if last is None:
            due.append((10 ** 6, pid, "no-passing-record", win))
            continue
        age = (today - datetime.date.fromisoformat(last)).days
        if age >= win:
            due.append((age, pid, last, win))
    for age, pid, last, win in sorted(due, reverse=True):
        print("%s\tlast=%s\twindow=%dd\tage=%s" % (pid, last, win, age))
    print("RESTORE-ROTATION: %d due of %d products" % (len(due), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYDOC
chmod +x ops-vm/jobs/restore_rotation.py
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/jobs/run-restore-rotation.sh <<'SHDOC'
#!/usr/bin/env bash
# Nightly: advance the rolling restore rotation and open the restore-verification
# task for the next product due (Section 94.7). The task is opened through the
# published CLI; this host never edits .github/workflows/** or records/**.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_env PRODUCT_REGISTRY_FILE RESTORE_RECORD_DIR
OUT=/var/lib/ops-vm/restore-rotation
install -d -m 0750 "$OUT"
set +e
python3 ops-vm/jobs/restore_rotation.py > "$OUT/due.txt"
rc=$?
set -e
if [ "$rc" -ne 0 ]; then
  cat "$OUT/due.txt"
  record_run restore-rotation failed "rc=$rc"
  notify/bin/notify-job-result.sh restore-rotation failed "rc=$rc"
  exit "$rc"
fi
next=$(grep -v '^RESTORE-ROTATION:' "$OUT/due.txt" | head -1 | cut -f1 || true)
if [ -n "$next" ]; then
  open-restore-verification --product "$next" --due "$(date -u +%F)"
  record_run restore-rotation ok "opened=$next"
else
  # Section 53.1: a clean run is recorded as clean.
  record_run restore-rotation ok "no product outside its window"
fi
exit 0
SHDOC
chmod +x ops-vm/jobs/run-restore-rotation.sh

cat > ops-vm/systemd/restore-rotation.service <<'UNITDOC'
[Unit]
Description=Rolling restore-rotation scheduler (Sections 44.2, 94.7)
[Service]
Type=oneshot
User=ops-vm
WorkingDirectory=/opt/control-plane
Environment=OPS_VM_TRIGGER=restore-rotation.timer
ExecStart=/opt/control-plane/ops-vm/jobs/run-restore-rotation.sh
UNITDOC

cat > ops-vm/systemd/restore-rotation.timer <<'UNITDOC'
[Unit]
Description=Restore rotation advances nightly (Section 94.7)
[Timer]
OnCalendar=daily
Persistent=true
[Install]
WantedBy=timers.target
UNITDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/restore-rotation-coverage.sh <<'SHDOC'
#!/usr/bin/env bash
# SIG-17 restore-test currency: Amber approaching, Blocking past (Section 52.2).
# Reads the rotation's own output; encodes no window of its own.
set -euo pipefail
F="${1:-/var/lib/ops-vm/restore-rotation/due.txt}"
[ -f "$F" ] || { echo "RESTORE-COVERAGE: NO-RUN-RECORDED -> BLOCKING"; exit 4; }
past=$(grep -vc '^RESTORE-ROTATION:' "$F" || true)
if [ "$past" -gt 0 ]; then
  echo "RESTORE-COVERAGE: $past product(s) past window -> BLOCKING"
  grep -v '^RESTORE-ROTATION:' "$F"
  exit 4
fi
echo "RESTORE-COVERAGE: 0 past window -> OK"
SHDOC
chmod +x ops-vm/checks/restore-rotation-coverage.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add ops-vm/jobs/restore_rotation.py ops-vm/jobs/run-restore-rotation.sh ops-vm/systemd/restore-rotation.service ops-vm/systemd/restore-rotation.timer ops-vm/checks/restore-rotation-coverage.sh
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-12: restore-rotation scheduler and SIG-17 coverage check"
git push -u origin "lane/5/04-t12-restore-rotation"
gh pr create --base integration --title "L5-04-12: restore-rotation scheduler" --body "Lane L5 phase 4 task L5-04-12. Paths: ops-vm/** only. Spec: 44.2, 94.7, 53.1, SIG-17, invariants 3 and 4."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Scheduler and wrapper parse | `python3 -m py_compile ops-vm/jobs/restore_rotation.py && bash -n ops-vm/jobs/run-restore-rotation.sh && echo SYNTAX-OK` | `SYNTAX-OK` |
| 2 | The 90-day floor and the 30-day critical window are the only windows | `grep -Ec '^(FLOOR_DAYS = 90|CRITICAL_DAYS = 30) ' ops-vm/jobs/restore_rotation.py` | `2` |
| 3 | An unknown criticality fails closed rather than defaulting | `grep -c 'unknown reliability_criticality' ops-vm/jobs/restore_rotation.py` | `1` |
| 4 | A product with no passing record is due | SELF-VERIFY, the first `restore_rotation.py` run | `p-none	last=no-passing-record	window=90d	age=1000000` then `RESTORE-ROTATION: 1 due of 2 products` |
| 5 | A product inside its window is not due | SELF-VERIFY, the second `restore_rotation.py` run | `RESTORE-ROTATION: 0 due of 2 products` |
| 6 | Past-window products are Blocking, not Amber | SELF-VERIFY, the `restore-rotation-coverage.sh` line | `RESTORE-COVERAGE: 1 product(s) past window -> BLOCKING` then `rc=4` |
| 7 | The scheduler never writes a workflow or a record | `git diff --cached --name-only \| grep -Ec '^(\.github|records|templates)/'` | `0` |
| 8 | The rotation advances nightly | `grep '^OnCalendar' ops-vm/systemd/restore-rotation.timer` | `OnCalendar=daily` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python3 -m py_compile ops-vm/jobs/restore_rotation.py && bash -n ops-vm/jobs/run-restore-rotation.sh && echo SYNTAX-OK
rm -rf /tmp/t12 && mkdir -p /tmp/t12/recs
cat > /tmp/t12/registry.yaml <<'EOF'
products:
  - id: p-fresh
    classification:
      reliability_criticality: high
  - id: p-none
    classification:
      reliability_criticality: high
EOF
printf '{"product":"p-fresh","result":"pass","at":"%s"}\n' "$(date -u +%F)" > /tmp/t12/recs/r1.json
PRODUCT_REGISTRY_FILE=/tmp/t12/registry.yaml RESTORE_RECORD_DIR=/tmp/t12/recs python3 ops-vm/jobs/restore_rotation.py
printf '{"product":"p-none","result":"pass","at":"%s"}\n' "$(date -u +%F)" > /tmp/t12/recs/r2.json
PRODUCT_REGISTRY_FILE=/tmp/t12/registry.yaml RESTORE_RECORD_DIR=/tmp/t12/recs python3 ops-vm/jobs/restore_rotation.py
rm /tmp/t12/recs/r2.json
mkdir -p /tmp/t12/out
PRODUCT_REGISTRY_FILE=/tmp/t12/registry.yaml RESTORE_RECORD_DIR=/tmp/t12/recs python3 ops-vm/jobs/restore_rotation.py > /tmp/t12/out/due.txt
ops-vm/checks/restore-rotation-coverage.sh /tmp/t12/out/due.txt; echo "rc=$?"
grep -Ec '^(FLOOR_DAYS = 90|CRITICAL_DAYS = 30) ' ops-vm/jobs/restore_rotation.py
grep '^OnCalendar' ops-vm/systemd/restore-rotation.timer
```

Expected output:

```
SYNTAX-OK
p-none	last=no-passing-record	window=90d	age=1000000
RESTORE-ROTATION: 1 due of 2 products
RESTORE-ROTATION: 0 due of 2 products
RESTORE-COVERAGE: 1 product(s) past window -> BLOCKING
p-none	last=no-passing-record	window=90d	age=1000000
rc=4
2
OnCalendar=daily
```

### STOP rule

If `open-restore-verification` does not exist on the host, or the restore-test record store is unreadable from it: **do not open a task by hand, do not write a record, do not skip the product and continue the rotation.** Section 53.1 makes a declared `restore_tested` date with no matching record Blocking drift, and invariant 3 treats an untested backup as no backup — a silently skipped product converts a Blocking condition into a clean-looking run. Open a blocker (§1.4) with the decision line: *"The published restore-verification task opener or the restore-test record store is unavailable to the operations VM; L0 must confirm the interface lanes L2 and L4 publish."*

If a product's `classification.reliability_criticality` is a value outside `critical`, `high`, `medium`, `low`: **do not assign it a window.** Invariant 4 permits tightening only, and picking a window for an unknown class is exactly the loosening it forbids. Open a blocker with the decision line: *"A product declares a `reliability_criticality` outside the closed set the restore-window rule of Section 44.2 covers; L0 must resolve the contract value before the rotation includes it."*

---

## L5-04-13 — Organisation export runner and staleness telemetry

**Size:** L · **Depends on:** L5-04-03, L5-04-11 · **Slug:** `org-export`
**Spec:** 45.3 in full — a **scheduled export job** capturing repositories, issues, pull requests and review records **through the migrations REST API**, Projects v2 boards **through a separate GraphQL dump** (they are not in migration archives), and, on the Team plan, **no audit log** (its API is Enterprise-only; the absence is a recorded accepted risk with a manual audit-log review as its compensating cadence); an **append-only, write-only credential** to **object-locked, versioned storage** in a **different provider and credential domain than GitHub**; **encrypted with a key held outside GitHub**, that key carrying its own asset-inventory entry with a named holder and a rotation cadence (initial value annually) and its own Section 14.4 escrow row; a **named owner and an explicit read-access list**; **restore-tested quarterly** with the environment wiped after each test; export failure alerts like a backup failure and a stale export is **Red** (SIG-34). Also 45.1 (**secret references only, never values**), 51.5 (the VM holds the organisation-export token), 40.1 (that token's behavioural envelope), 94.7, AT-035, D80, D54.

**Boundary:** the org-export **workflow** is lane L2's; L2 has published the contract for the one primitive it needs from this lane — `ops-vm/export/put.sh`, taking one argument (a local file), writing to object-locked versioned storage using `WRITE_TOKEN`, and exiting non-zero on failure. This task creates that primitive to that contract, plus the VM-side scheduled runner and the staleness telemetry. It writes no workflow and no record.

> **DECISION REQUIRED — routed to L0, not resolved here.**
> Section 45.3 makes the audit log's absence from the Team-plan export a **recorded accepted risk** whose compensating control is a **manual audit-log review** — calibrated configuration, initial value weekly, owned by the escalation role, written to `records/security-reviews/`, booked in the Section 94.8 cadence table, and raising SIG-44 when it goes stale. The accepted-risk record, the policy entry and the cadence booking are **subsystem O (governance registries and jobs)**, which is **unassigned in PARTITION v1**. This task therefore ships the export runner with the audit log excluded and named as excluded, and opens a handoff issue. It does not create the accepted-risk record, does not pick the review cadence, and does not claim subsystem O.

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/export/put.sh` | The object-lock write primitive published to lane L2 (one file argument, `WRITE_TOKEN`) |
| `ops-vm/export/storage.env.example` | Provider, endpoint, bucket, object-lock, versioning, retention, owner, read list (empty) |
| `ops-vm/export/projects.graphql` | The Projects v2 board query — boards are not in migration archives (D80) |
| `ops-vm/export/run-org-export.sh` | Migrations-API archive + Projects GraphQL dump + encrypt + put |
| `ops-vm/export/EXCLUSIONS.md` | What the export does not carry, and why, naming the dependent controls |
| `ops-vm/systemd/org-export.service` / `.timer` | Scheduled export |
| `ops-vm/checks/export-credential.sh` | Negative test: the write credential must fail a read and a delete |
| `ops-vm/checks/export-no-secret-values.sh` | Fails if the staged export carries a secret value rather than a reference |
| `ops-vm/checks/export-staleness.sh` | SIG-34 feed: missing, failed, or not restore-tested in 90 days is Red |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t13-org-export"
mkdir -p ops-vm/export ops-vm/systemd ops-vm/checks
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/export/storage.env.example <<'ENVDOC'
# Organisation-export target (Section 45.3). MUST be a different provider AND a
# different credential domain than GitHub itself, so that the event that takes
# the organisation does not take the export. Values come from the recorded
# decision; never chosen here.
GITHUB_ORG=
EXPORT_PROVIDER=
EXPORT_ENDPOINT=
EXPORT_BUCKET=
EXPORT_OBJECT_LOCK=                 # must be "on"
EXPORT_VERSIONING=                  # must be "on"
EXPORT_RETENTION_DAYS=
EXPORT_ACCESS_KEY_ID=               # append-only, write-only credential
EXPORT_SECRET_ACCESS_KEY=
EXPORT_ENCRYPTION_RECIPIENTS_FILE=  # key held OUTSIDE GitHub (Section 45.3)
EXPORT_ENCRYPTION_KEY_ESCROW=       # Section 14.4 escrow row, distinct from the credential rows
EXPORT_ENCRYPTION_KEY_ASSET_ID=     # assets/inventory entry id (Section 49, D54)
EXPORT_OWNER=
EXPORT_READ_ACCESS_LIST=            # explicit list; empty is a valid, stricter value
EXPORT_ONCALENDAR=
ENVDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/export/put.sh <<'SHDOC'
#!/usr/bin/env bash
# Published to lane L2 as the object-lock write primitive of the org-export
# workflow. Contract, exactly as L2 declared it:
#   one argument: a local file
#   writes to object-locked, versioned storage using WRITE_TOKEN
#   exits non-zero on failure
# Section 45.3: the credential that writes cannot read, overwrite or delete what
# previous runs wrote, and object lock means the event that compromises the
# exporter cannot destroy the history.
set -euo pipefail
SRC="${1:?usage: put.sh <local-file>}"
[ -f "$SRC" ] || { echo "EXPORT-PUT: FAIL (no such file: $SRC)"; exit 1; }
[ -n "${WRITE_TOKEN:-}" ] || { echo "EXPORT-PUT: FAIL-CLOSED (WRITE_TOKEN is empty)"; exit 1; }
: "${EXPORT_ENDPOINT:?EXPORT_ENDPOINT is required}"
: "${EXPORT_BUCKET:?EXPORT_BUCKET is required}"
: "${EXPORT_RETENTION_DAYS:?EXPORT_RETENTION_DAYS is required}"
key="org-export/$(date -u +%Y%m%dT%H%M%SZ)-$(basename "$SRC")"
AWS_ACCESS_KEY_ID="${EXPORT_ACCESS_KEY_ID:-}" \
AWS_SECRET_ACCESS_KEY="$WRITE_TOKEN" \
aws --endpoint-url "$EXPORT_ENDPOINT" s3api put-object \
    --bucket "$EXPORT_BUCKET" --key "$key" --body "$SRC" \
    --object-lock-mode COMPLIANCE \
    --object-lock-retain-until-date "$(date -u -d "+$EXPORT_RETENTION_DAYS days" +%Y-%m-%dT%H:%M:%SZ)" \
  || { echo "EXPORT-PUT: FAIL (write refused)"; exit 1; }
echo "EXPORT-PUT: OK $key"
SHDOC
chmod +x ops-vm/export/put.sh

cat > ops-vm/export/projects.graphql <<'GQLDOC'
# Projects v2 boards are NOT included in migration archives and are captured by
# this separate GraphQL dump (Section 45.3, D80). The organisation login is
# supplied by the caller; no organisation or product name is written here.
query($org: String!, $cursor: String) {
  organization(login: $org) {
    projectsV2(first: 20, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes {
        id
        title
        number
        closed
        items(first: 100) {
          nodes {
            id
            type
            content { ... on Issue { number } ... on PullRequest { number } }
          }
        }
      }
    }
  }
}
GQLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/export/EXCLUSIONS.md <<'MDDOC'
# What the organisation export does not carry

Stated here so a responder discovers it before the restore, not during one.

| Excluded | Why | Dependent control |
| --- | --- | --- |
| The organisation audit log | Its API is Enterprise-only; on the Team plan it cannot be exported (Section 45.3, D80) | A recorded accepted risk whose compensating cadence is the manual audit-log review of Section 45.3 - owned by the escalation role, written to `records/security-reviews/`, raising SIG-44 when stale. That record and that policy entry are subsystem O and are not created by this lane |
| Layer B people data | The export is organisation-readable in restore; Section 51.4 forbids Layer B content in an organisation-readable repository | The Layer B recovery baseline is the Section 45.4 restore, recorded as a decision |
| Secret values | Section 45.1: the reconstruction set carries secret *references* - names, scopes and locations - never values | `ops-vm/checks/export-no-secret-values.sh` fails the run rather than shipping a value |

Two classes travel by their own mechanism, not by the migrations archive:

* Projects v2 boards are **not** included in migration archives and are captured
  by a separate GraphQL dump (Section 45.3, D80).
* Issues, pull requests and review records travel through the migrations REST
  API alongside the repositories.
MDDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/export/run-org-export.sh <<'SHDOC'
#!/usr/bin/env bash
# Scheduled organisation export (Section 45.3). Encrypt locally with a key held
# outside GitHub, then write with an append-only, write-only credential to
# object-locked, versioned storage in a different provider and credential domain.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/export/storage.env
set -a; . ops-vm/export/storage.env; set +a
require_env GITHUB_ORG EXPORT_PROVIDER EXPORT_ENDPOINT EXPORT_BUCKET EXPORT_OBJECT_LOCK \
            EXPORT_VERSIONING EXPORT_RETENTION_DAYS EXPORT_ACCESS_KEY_ID \
            EXPORT_SECRET_ACCESS_KEY EXPORT_ENCRYPTION_RECIPIENTS_FILE \
            EXPORT_ENCRYPTION_KEY_ESCROW EXPORT_ENCRYPTION_KEY_ASSET_ID \
            EXPORT_OWNER

[ "$EXPORT_OBJECT_LOCK" = "on" ] || fail_closed "object lock must be on (Section 45.3)"
[ "$EXPORT_VERSIONING" = "on" ] || fail_closed "versioning must be on (Section 45.3)"
require_file "$EXPORT_ENCRYPTION_RECIPIENTS_FILE"

ops-vm/checks/export-credential.sh || fail_closed "export credential is not append-only/write-only"

stamp=$(date -u +%Y%m%dT%H%M%SZ)
work=$(mktemp -d); trap 'rm -rf "$work"' EXIT

# Repositories, issues, pull requests and review records: migrations REST API.
# The repository list is generated from the registry at run time, never listed
# in this repository (invariant 52).
repos=$(list-repositories --from-registry)
[ -n "$repos" ] || fail_closed "registry returned no repositories; refusing to export an empty set"
python3 -c 'import json,sys;print(json.dumps({"repositories":sys.argv[1].split(),"lock_repositories":False}))' \
  "$repos" > "$work/repos.json"
gh api --method POST "/orgs/$GITHUB_ORG/migrations" --input "$work/repos.json" > "$work/migration.json"
mig=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["id"])' "$work/migration.json")
gh api "/orgs/$GITHUB_ORG/migrations/$mig/archive" > "$work/migration-$stamp.tar.gz"

# Projects v2 boards: NOT in migration archives; separate GraphQL dump (D80).
gh api graphql -F org="$GITHUB_ORG" -f query="$(cat ops-vm/export/projects.graphql)" \
  > "$work/projects-$stamp.json"

# Audit log: Enterprise-only API; excluded on the Team plan and named as excluded.
cp ops-vm/export/EXCLUSIONS.md "$work/EXCLUSIONS.md"

sha256sum "$work"/* > "$work/manifest-$stamp.sha256"
ops-vm/checks/export-no-secret-values.sh "$work" || fail_closed "a secret value reached the export staging area (Section 45.1)"

age --encrypt --recipients-file "$EXPORT_ENCRYPTION_RECIPIENTS_FILE" \
    --output "$work/org-export-$stamp.age" \
    <(tar -C "$work" -cf - "migration-$stamp.tar.gz" "projects-$stamp.json" "manifest-$stamp.sha256" "EXCLUSIONS.md")

WRITE_TOKEN="$EXPORT_SECRET_ACCESS_KEY" ops-vm/export/put.sh "$work/org-export-$stamp.age"

now=$(date -u +%s)
printf 'ops_vm_job_last_success_timestamp{job_name="org-export"} %s\n' "$now" \
  > /var/lib/ops-vm/metrics/org-export-freshness.prom
record_run org-export ok "owner=$EXPORT_OWNER key_asset=$EXPORT_ENCRYPTION_KEY_ASSET_ID"
SHDOC
chmod +x ops-vm/export/run-org-export.sh

cat > ops-vm/systemd/org-export.service <<'UNITDOC'
[Unit]
Description=Scheduled GitHub organisation export (Section 45.3)
After=network-online.target
[Service]
Type=oneshot
User=root
WorkingDirectory=/opt/control-plane
Environment=OPS_VM_TRIGGER=org-export.timer
ExecStart=/opt/control-plane/ops-vm/export/run-org-export.sh
# Export job failure alerts like a backup failure (Sections 45.3, 44.3).
ExecStopPost=/opt/control-plane/notify/bin/notify-job-result.sh org-export failed
UNITDOC

cat > ops-vm/systemd/org-export.timer <<'UNITDOC'
[Unit]
Description=Organisation export cadence (Section 94.7)
[Timer]
OnCalendar=${EXPORT_ONCALENDAR}
Persistent=true
[Install]
WantedBy=timers.target
UNITDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/export-credential.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 45.3 negative test: the credential that writes the export cannot read,
# overwrite or delete what previous runs wrote. A credential that can read or
# delete FAILS this check.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/export/storage.env
set -a; . ops-vm/export/storage.env; set +a
export AWS_ACCESS_KEY_ID="$EXPORT_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$EXPORT_SECRET_ACCESS_KEY"
probe="org-export/_credential-probe-$(date -u +%s)"
fail=0
aws --endpoint-url "$EXPORT_ENDPOINT" s3api put-object \
    --bucket "$EXPORT_BUCKET" --key "$probe" --body /dev/null >/dev/null \
  || { echo "write DENIED - the credential cannot write"; fail=1; }
if aws --endpoint-url "$EXPORT_ENDPOINT" s3api get-object \
      --bucket "$EXPORT_BUCKET" --key "$probe" /dev/null >/dev/null 2>&1; then
  echo "read ALLOWED - credential is not write-only"; fail=1
else echo "read denied OK"; fi
if aws --endpoint-url "$EXPORT_ENDPOINT" s3api delete-object \
      --bucket "$EXPORT_BUCKET" --key "$probe" >/dev/null 2>&1; then
  echo "delete ALLOWED - credential is not append-only"; fail=1
else echo "delete denied OK"; fi
if [ "$fail" -eq 0 ]; then echo "EXPORT-CREDENTIAL: PASS"; else echo "EXPORT-CREDENTIAL: FAIL"; exit 1; fi
SHDOC
chmod +x ops-vm/checks/export-credential.sh

cat > ops-vm/checks/export-no-secret-values.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 45.1: the export carries secret REFERENCES - names, scopes and
# locations - never values. Fails the run rather than shipping a value.
set -euo pipefail
DIR="${1:?usage: export-no-secret-values.sh <staging-dir>}"
hits=$(grep -RIlE '(-----BEGIN [A-Z ]*PRIVATE KEY-----|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{22,})' "$DIR" || true)
if [ -n "$hits" ]; then echo "EXPORT-NO-SECRET-VALUES: FAIL"; echo "$hits"; exit 1; fi
echo "EXPORT-NO-SECRET-VALUES: PASS"
SHDOC
chmod +x ops-vm/checks/export-no-secret-values.sh

cat > ops-vm/checks/export-staleness.sh <<'SHDOC'
#!/usr/bin/env bash
# SIG-34: the scheduled organisation export missing, failed, or not
# restore-tested within its 90-day window is RED (Section 52.2).
set -euo pipefail
F="${1:-/var/lib/ops-vm/metrics/org-export-freshness.prom}"
R="${2:-/var/lib/ops-vm/metrics/org-export-restore-test.prom}"
now=$(date -u +%s)
rc=0
if [ ! -f "$F" ]; then echo "export: NO-RUN-RECORDED -> RED"; rc=2
else
  ts=$(awk '{print $2}' "$F"); age=$(( (now - ts) / 86400 ))
  if [ "$age" -ge 1 ]; then echo "export: last success ${age}d ago -> RED"; rc=2
  else echo "export: last success ${age}d ago -> OK"; fi
fi
if [ ! -f "$R" ]; then echo "restore-test: NO-RUN-RECORDED -> RED"; rc=2
else
  ts=$(awk '{print $2}' "$R"); age=$(( (now - ts) / 86400 ))
  if [ "$age" -ge 90 ]; then echo "restore-test: ${age}d ago -> RED"; rc=2
  else echo "restore-test: ${age}d ago -> OK"; fi
fi
[ "$rc" -eq 0 ] && echo "EXPORT-STALENESS: PASS" || echo "EXPORT-STALENESS: RED"
exit "$rc"
SHDOC
chmod +x ops-vm/checks/export-staleness.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add ops-vm/export ops-vm/systemd/org-export.service ops-vm/systemd/org-export.timer ops-vm/checks/export-credential.sh ops-vm/checks/export-no-secret-values.sh ops-vm/checks/export-staleness.sh
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-13: organisation export runner, object-lock write primitive and SIG-34 telemetry"
git push -u origin "lane/5/04-t13-org-export"
gh pr create --base integration --title "L5-04-13: organisation export runner and staleness telemetry" --body "Lane L5 phase 4 task L5-04-13. Paths: ops-vm/** only. Publishes ops-vm/export/put.sh to the contract lane L2 declared. Spec: 45.3, 45.1, 51.5, 40.1, 94.7, SIG-34, AT-035, D80, D54."
```

Then the two handoff issues this task ends in — never an edit to a foreign path:

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
gh issue create \
  --title "HANDOFF L5-04-13 -> L2: ops-vm/export/put.sh is available" \
  --label "handoff,lane-5,lane-2,phase-4" \
  --body "L5 has published ops-vm/export/put.sh to the contract L2-01 declared: one argument (a local file), writes to object-locked versioned storage using WRITE_TOKEN, exits non-zero on failure. The org-export workflow and AT-035's execution task are unblocked. L5 does not edit .github/workflows/**."

gh issue create \
  --title "DECISION REQUIRED L5-04-13 -> L0: audit-log accepted risk and its review cadence" \
  --label "blocker,lane-5,phase-4,l0-decision" \
  --body "Section 45.3 excludes the organisation audit log from the Team-plan export and requires a recorded accepted risk whose compensating control is a manual audit-log review - calibrated configuration, initial value weekly, owned by the escalation role, written to records/security-reviews/, booked in the Section 94.8 cadence table, raising SIG-44 when stale. The accepted-risk record and the policy entry are subsystem O (governance registries and jobs), which is UNASSIGNED in PARTITION v1. L5 has shipped the export with the audit log excluded and named as excluded in ops-vm/export/EXCLUSIONS.md. L0 must assign subsystem O and decide the review cadence and its owner. L5 claims neither."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Every script parses | `for f in ops-vm/export/put.sh ops-vm/export/run-org-export.sh ops-vm/checks/export-credential.sh ops-vm/checks/export-no-secret-values.sh ops-vm/checks/export-staleness.sh; do bash -n "$f" \|\| exit 1; done; echo ALL-PARSE-OK` | `ALL-PARSE-OK` |
| 2 | `put.sh` takes exactly one file argument and fails without it | `bash -c 'ops-vm/export/put.sh >/dev/null 2>&1; echo "rc=$?"'` | `rc=1` |
| 3 | `put.sh` fails closed with no `WRITE_TOKEN` | SELF-VERIFY, the `WRITE_TOKEN=` line | `EXPORT-PUT: FAIL-CLOSED (WRITE_TOKEN is empty)` then `rc=1` |
| 4 | Object lock and versioning are hard requirements | `grep -Ec 'must be on \(Section 45.3\)' ops-vm/export/run-org-export.sh` | `2` |
| 5 | Boards are captured by their own mechanism, not assumed in the archive | `grep -c 'projects.graphql' ops-vm/export/run-org-export.sh` | `1` |
| 6 | The audit-log exclusion is named, not silent | `grep -c 'organisation audit log' ops-vm/export/EXCLUSIONS.md` | `1` |
| 7 | A secret value never leaves the host | SELF-VERIFY, the `export-no-secret-values.sh` line | `EXPORT-NO-SECRET-VALUES: FAIL` then `rc=1` |
| 8 | The credential negative test runs before any write | `CRED=$(grep -n 'export-credential.sh' ops-vm/export/run-org-export.sh \| head -1 \| cut -d: -f1); PUT=$(grep -n 'export/put.sh' ops-vm/export/run-org-export.sh \| head -1 \| cut -d: -f1); [ "$CRED" -lt "$PUT" ] && echo BEFORE-WRITE-OK` | `BEFORE-WRITE-OK` |
| 9 | A missing export is Red, not silence | SELF-VERIFY, the `export-staleness.sh` line | `export: NO-RUN-RECORDED -> RED` … `EXPORT-STALENESS: RED` then `rc=2` |
| 10 | No storage credential value is committed | `git ls-files ops-vm/export \| grep -Evc '(\.example|\.sh|\.md|\.graphql|\.json)$'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for f in ops-vm/export/put.sh ops-vm/export/run-org-export.sh ops-vm/checks/export-credential.sh ops-vm/checks/export-no-secret-values.sh ops-vm/checks/export-staleness.sh; do bash -n "$f" || exit 1; done; echo ALL-PARSE-OK
rm -rf /tmp/t13 && mkdir -p /tmp/t13/stage
: > /tmp/t13/body
bash -c 'ops-vm/export/put.sh >/dev/null 2>&1; echo "rc=$?"'
WRITE_TOKEN= ops-vm/export/put.sh /tmp/t13/body; echo "rc=$?"
grep -Ec 'must be on \(Section 45.3\)' ops-vm/export/run-org-export.sh
grep -c 'projects.graphql' ops-vm/export/run-org-export.sh
grep -c 'organisation audit log' ops-vm/export/EXCLUSIONS.md
printf -- '-----BEGIN RSA PRIVATE KEY-----\n' > /tmp/t13/stage/leak.pem
ops-vm/checks/export-no-secret-values.sh /tmp/t13/stage; echo "rc=$?"
ops-vm/checks/export-staleness.sh /tmp/t13/absent-a.prom /tmp/t13/absent-b.prom; echo "rc=$?"
CRED=$(grep -n 'export-credential.sh' ops-vm/export/run-org-export.sh | head -1 | cut -d: -f1)
PUT=$(grep -n 'export/put.sh' ops-vm/export/run-org-export.sh | head -1 | cut -d: -f1)
[ "$CRED" -lt "$PUT" ] && echo BEFORE-WRITE-OK || echo BEFORE-WRITE-FAIL
git ls-files ops-vm/export | grep -Evc '(\.example|\.sh|\.md|\.graphql|\.json)$'
```

Expected output:

```
ALL-PARSE-OK
rc=1
EXPORT-PUT: FAIL-CLOSED (WRITE_TOKEN is empty)
rc=1
2
1
1
EXPORT-NO-SECRET-VALUES: FAIL
/tmp/t13/stage/leak.pem
rc=1
export: NO-RUN-RECORDED -> RED
restore-test: NO-RUN-RECORDED -> RED
EXPORT-STALENESS: RED
rc=2
BEFORE-WRITE-OK
0
```

### STOP rule

If `ops-vm/checks/export-credential.sh` reports `read ALLOWED` or `delete ALLOWED`, or the export target resolves to **GitHub itself, to the same provider as the operations VM, or to the same credential domain**: **do not run an export, do not relax the check.** Section 45.3 exists for the event that takes the organisation; an export the same event can reach is not an export. Open a blocker (§1.4) with the decision line: *"The organisation-export credential is not write-only/append-only, or the target shares a provider or credential domain with GitHub or the operations VM; Section 45.3 requires L0 to provision a conforming target."*

If `EXPORT_ENCRYPTION_KEY_ESCROW` is empty, or the asset-inventory entry named by `EXPORT_ENCRYPTION_KEY_ASSET_ID` is absent: **do not generate a key, do not run an export without one.** Section 45.3 states plainly that a key with no custodian and no second copy leaves an undeletable, unreadable archive the company then pays to store forever. Open a blocker with the decision line: *"The organisation-export encryption key has no Section 14.4 escrow row or no Section 49 inventory entry; D54 requires both before an encrypted export exists."*

If the migrations API returns an archive and the Projects GraphQL dump fails, **do not ship the archive alone and record the run as successful.** D80 records that boards are not in migration archives; a partial export recorded as complete is exactly the assumption AT-035 exists to break. Open a blocker with the decision line: *"The Projects v2 GraphQL dump failed while the migrations archive succeeded; Section 45.3 requires every data class through its own recorded mechanism before the run is recorded as an export."*

---

## L5-04-14 — D94 external dead-man switch and the off-VM liveness leg

**Size:** L · **Depends on:** L5-04-04, L5-04-11, L5-03-COMPLETE · **Slug:** `deadman`
**Spec:** **D94** — *"An external dead-man's-switch outside the VM, outside GitHub and outside the product providers pages the phone-escalation path directly"*, because Section 45.2's earlier claim of responder-source independence was false: Prometheus, Grafana alerting and health computation all run on the operations VM. 51.5 — machine detection carries an **off-VM leg**, registered in the Section 49 asset inventory with a **named owner**: an external uptime check per product hitting `/health` from outside the VM, and a dead-man's-switch heartbeat from the monitoring stack itself, **both routing to the Actions-webhook alert channel (Section 92.11) and to the Section 42.2 phone path rather than through the VM**. 45.2 (control-plane outage: machine detection stops for every product simultaneously; the outage is raised by the off-VM leg and by nothing on the VM). 46.6 *Monitoring stack unavailable* — until that leg reports, the estate is **undetected, not healthy**; entry and exit are recorded events naming the products whose declared window it voids. 51.2 (operations-VM liveness observed off-VM: Red, routed to the messaging channel and the phone path **directly, never through the VM**). 42.2 (the documented phone-escalation path).

**Boundary:** the two legs' **inventory entries** are subsystem Q entries of `asset_class: detection_leg`, carrying `mechanism`, `runs_off_operations_vm` and `routes_to`; they are authored by the lane's asset phase. This task provisions the VM-side heartbeat emitter, the estate-side declaration of both legs, and the checks that neither leg resolves back to the VM. It authors no inventory entry.

> **DECISION REQUIRED — routed to L0, not resolved here.**
> The **dead-man watchdog provider and the second-host location** are already listed in §1.6 as values this phase never invents (51.5, D94). Separately, the Section 92 rendering of the off-VM legs on the Founder and operator surfaces is **subsystem H (dashboards and views)**, which is **unassigned in PARTITION v1**. This task emits the metric and the declaration; it does not build a Section 92 surface and does not claim subsystem H.

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/deadman/heartbeat.sh` | Emits the check-in from the VM to the external watchdog |
| `ops-vm/systemd/deadman-heartbeat.service` / `.timer` | Heartbeat cadence |
| `ops-vm/checks/deadman-heartbeat-fresh.sh` | Local view of the last successful check-in |
| `infra/deadman/watchdog.yaml.example` | Provider, check-in handle, grace period, escalation targets (empty) |
| `infra/deadman/uptime-checks.yaml.example` | Per-product external `/health` check, generated from the registry |
| `infra/deadman/second-host.yaml.example` | The second host the legs run from (empty) |
| `infra/deadman/check-off-vm.sh` | Fails if any leg resolves to the VM, to GitHub or to a product provider |
| `infra/deadman/check-routes-direct.sh` | Fails if any leg routes through the operations VM |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t14-deadman"
mkdir -p ops-vm/deadman infra/deadman ops-vm/systemd ops-vm/checks
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > infra/deadman/watchdog.yaml.example <<'YAMLDOC'
# D94: the dead-man's switch is outside the VM, outside GitHub and outside the
# product providers, and it pages the Section 42.2 phone path directly.
# The provider and the second-host location are a recorded decision (Section
# 51.5, and this file's §1.6). An implementer never fills this file.
# provider: NOT the operations VM's provider, NOT github, and NOT any product's
# declared infrastructure.provider.
provider:
# checkin_url_handle: a handle only; the real URL is a host secret.
checkin_url_handle:
# grace_period_minutes: missed check-ins before the switch fires. This value is
# evaluated on the watchdog, never on this host.
grace_period_minutes:
# runs_off_operations_vm is asserted by check-off-vm.sh, never assumed.
runs_off_operations_vm: true
# routes_to: the Section 92.11 Actions-webhook alert channel and the Section
# 42.2 phone path, each reached directly and never via the operations VM.
routes_to:
  - messaging_channel
  - phone_escalation_path
# asset_inventory_entry: the assets/inventory entry id, asset_class detection_leg.
asset_inventory_entry:
# owner: a named person (Section 49.1); never a role alias.
owner:
# decision_record: the recorded decision naming the provider and the second host.
decision_record:
YAMLDOC

cat > infra/deadman/second-host.yaml.example <<'YAMLDOC'
# The host the off-VM legs execute from (Section 51.5). It is not the operations
# VM and shares no credential with it.
host:
provider:
owner:
shares_credentials_with_ops_vm: false
decision_record:
YAMLDOC

cat > infra/deadman/uptime-checks.yaml.example <<'YAMLDOC'
# One external uptime check per product, hitting /health from OUTSIDE the VM
# (Section 51.5). The product list is generated from the registry at render
# time - never enumerated here (invariant 52).
generated_from: registry
endpoint_path: /health
runs_off_operations_vm: true
routes_to:
  - messaging_channel
  - phone_escalation_path
asset_inventory_entry:
owner:
YAMLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/deadman/heartbeat.sh <<'SHDOC'
#!/usr/bin/env bash
# The monitoring stack's own heartbeat to the external watchdog (D94, 51.5).
# This host EMITS the heartbeat; it never evaluates it. Evaluation is the whole
# point of putting the watchdog elsewhere: a dead observer emits exactly what a
# healthy estate emits (Section 46.6, Monitoring stack unavailable).
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_file ops-vm/deadman/deadman.env
set -a; . ops-vm/deadman/deadman.env; set +a
require_env DEADMAN_CHECKIN_URL DEADMAN_METRICS_DIR
install -d -m 0750 "$DEADMAN_METRICS_DIR"
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$DEADMAN_CHECKIN_URL" || echo 000)
case "$code" in
  2*) printf 'ops_vm_deadman_last_checkin_timestamp %s\n' "$(date -u +%s)" \
        > "$DEADMAN_METRICS_DIR/deadman.prom"
      record_run deadman-heartbeat ok "http=$code" ;;
  *)  record_run deadman-heartbeat failed "http=$code"
      fail_closed "watchdog check-in failed with http $code; the switch will fire on its own grace period" ;;
esac
SHDOC
chmod +x ops-vm/deadman/heartbeat.sh
printf 'deadman/deadman.env\n' >> ops-vm/.gitignore

cat > ops-vm/systemd/deadman-heartbeat.service <<'UNITDOC'
[Unit]
Description=Dead-man's-switch heartbeat to the external watchdog (D94, Section 51.5)
[Service]
Type=oneshot
User=ops-vm
WorkingDirectory=/opt/control-plane
Environment=OPS_VM_TRIGGER=deadman-heartbeat.timer
ExecStart=/opt/control-plane/ops-vm/deadman/heartbeat.sh
UNITDOC

cat > ops-vm/systemd/deadman-heartbeat.timer <<'UNITDOC'
[Unit]
Description=Heartbeat cadence; the grace period lives on the watchdog, not here
[Timer]
OnCalendar=minutely
Persistent=false
[Install]
WantedBy=timers.target
UNITDOC

cat > ops-vm/checks/deadman-heartbeat-fresh.sh <<'SHDOC'
#!/usr/bin/env bash
# Local view only. A stale value here is informative; the authoritative decision
# is the watchdog's, off this host (D94).
set -euo pipefail
F="${1:-/var/lib/ops-vm/metrics/deadman.prom}"
[ -f "$F" ] || { echo "DEADMAN-LOCAL: NO-CHECKIN-RECORDED (authoritative view is off-VM)"; exit 1; }
ts=$(awk '{print $2}' "$F"); age=$(( $(date -u +%s) - ts ))
echo "DEADMAN-LOCAL: last check-in ${age}s ago (authoritative view is off-VM)"
SHDOC
chmod +x ops-vm/checks/deadman-heartbeat-fresh.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > infra/deadman/check-off-vm.sh <<'SHDOC'
#!/usr/bin/env bash
# D94: outside the VM, outside GitHub, outside the product providers.
# Each leg's declared provider is compared against the operations VM's provider,
# against github, and against every infrastructure.provider the product registry
# declares. The registry is read as DATA, read-only.
set -euo pipefail
WD="${1:?usage: check-off-vm.sh <watchdog.yaml> <ops-vm-provider> <product-registry.yaml>}"
OPSP="${2:?}"
REG="${3:?}"
[ -f "$WD" ] || { echo "DEADMAN-OFF-VM: FAIL (no $WD)"; exit 1; }
[ -f "$REG" ] || { echo "DEADMAN-OFF-VM: FAIL-CLOSED (product registry unreadable: $REG)"; exit 1; }
prov=$(awk -F': *' '/^provider:/{print $2}' "$WD" | tr -d '"' | head -1)
[ -n "$prov" ] || { echo "DEADMAN-OFF-VM: FAIL (watchdog declares no provider)"; exit 1; }
grep -q '^runs_off_operations_vm: true$' "$WD" \
  || { echo "DEADMAN-OFF-VM: FAIL (runs_off_operations_vm is not true)"; exit 1; }
fail=0
[ "$prov" != "$OPSP" ] || { echo "provider equals the operations VM provider: $prov"; fail=1; }
[ "$prov" != "github" ] || { echo "provider is github"; fail=1; }
if python3 -c '
import sys, yaml
reg = yaml.safe_load(open(sys.argv[1])) or {}
prov = sys.argv[2]
names = {(p.get("infrastructure") or {}).get("provider") for p in reg.get("products", [])}
sys.exit(0 if prov in names else 1)' "$REG" "$prov"; then
  echo "provider is a product infrastructure provider: $prov"; fail=1
fi
if [ "$fail" -eq 0 ]; then echo "DEADMAN-OFF-VM: PASS"; else echo "DEADMAN-OFF-VM: FAIL"; exit 1; fi
SHDOC
chmod +x infra/deadman/check-off-vm.sh

cat > infra/deadman/check-routes-direct.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 51.2: the off-VM liveness leg routes to the messaging channel and the
# Section 42.2 phone path DIRECTLY, never through the operations VM.
set -euo pipefail
fail=0
for f in "$@"; do
  [ -f "$f" ] || { echo "missing: $f"; fail=1; continue; }
  grep -q '^  - messaging_channel$'      "$f" || { echo "$f: no messaging_channel route"; fail=1; }
  grep -q '^  - phone_escalation_path$'  "$f" || { echo "$f: no phone_escalation_path route"; fail=1; }
  grep -q '^runs_off_operations_vm: true$' "$f" || { echo "$f: runs_off_operations_vm is not true"; fail=1; }
  if grep -qiE 'via_ops_vm|through_ops_vm|relay: *ops-vm' "$f"; then echo "$f: routes through the operations VM"; fail=1; fi
done
if [ "$fail" -eq 0 ]; then echo "DEADMAN-ROUTES-DIRECT: PASS"; else echo "DEADMAN-ROUTES-DIRECT: FAIL"; exit 1; fi
SHDOC
chmod +x infra/deadman/check-routes-direct.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add ops-vm/deadman ops-vm/.gitignore ops-vm/systemd/deadman-heartbeat.service ops-vm/systemd/deadman-heartbeat.timer ops-vm/checks/deadman-heartbeat-fresh.sh infra/deadman
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-14: D94 external dead-man switch and the off-VM liveness leg"
git push -u origin "lane/5/04-t14-deadman"
gh pr create --base integration --title "L5-04-14: D94 dead-man switch and off-VM liveness leg" --body "Lane L5 phase 4 task L5-04-14. Paths: ops-vm/**, infra/** only. Spec: D94, 51.5, 51.2, 45.2, 46.6 (Monitoring stack unavailable), 42.2, 92.11, 49.1."
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
gh issue create \
  --title "DECISION REQUIRED L5-04-14 -> L0: Section 92 rendering of the off-VM legs" \
  --label "blocker,lane-5,phase-4,l0-decision" \
  --body "L5-04-14 emits ops_vm_deadman_last_checkin_timestamp and declares both off-VM legs under infra/deadman/. Rendering those legs on the Section 92 surfaces is subsystem H (dashboards and views), which is UNASSIGNED in PARTITION v1. L5 does not claim subsystem H and builds no Section 92 surface here. L0 must assign H. Until the leg is rendered and reporting, Section 46.6 says the estate is undetected, not healthy - that statement is the reason this issue exists."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Every script parses | `for f in ops-vm/deadman/heartbeat.sh ops-vm/checks/deadman-heartbeat-fresh.sh infra/deadman/check-off-vm.sh infra/deadman/check-routes-direct.sh; do bash -n "$f" \|\| exit 1; done; echo ALL-PARSE-OK` | `ALL-PARSE-OK` |
| 2 | The VM emits the heartbeat and never evaluates it | `grep -Eic '(grace_period|fire_after|threshold)' ops-vm/deadman/heartbeat.sh` | `0` |
| 3 | The watchdog template names no provider | `grep -Ec '^provider:[[:space:]]*[^[:space:]#]' infra/deadman/watchdog.yaml.example` | `0` |
| 4 | Both routes are declared on both legs | `infra/deadman/check-routes-direct.sh infra/deadman/watchdog.yaml.example infra/deadman/uptime-checks.yaml.example` | `DEADMAN-ROUTES-DIRECT: PASS` |
| 5 | The off-VM check rejects the operations VM's own provider | SELF-VERIFY, the `wd-opsvm.yaml` line | `provider equals the operations VM provider: acme-cloud` then `DEADMAN-OFF-VM: FAIL` then `rc=1` |
| 6 | The off-VM check rejects a product provider | SELF-VERIFY, the `wd-product.yaml` line | `provider is a product infrastructure provider: hetzner` then `DEADMAN-OFF-VM: FAIL` then `rc=1` |
| 7 | The off-VM check passes only for a third provider | SELF-VERIFY, the `wd-ok.yaml` line | `DEADMAN-OFF-VM: PASS` |
| 8 | The uptime checks are generated from the registry, not enumerated | `grep -c '^generated_from: registry$' infra/deadman/uptime-checks.yaml.example` | `1` |
| 9 | No check-in URL is committed | `git ls-files ops-vm/deadman infra/deadman \| grep -Evc '(\.example|\.sh)$'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for f in ops-vm/deadman/heartbeat.sh ops-vm/checks/deadman-heartbeat-fresh.sh infra/deadman/check-off-vm.sh infra/deadman/check-routes-direct.sh; do bash -n "$f" || exit 1; done; echo ALL-PARSE-OK
grep -Eic '(grace_period|fire_after|threshold)' ops-vm/deadman/heartbeat.sh
grep -Ec '^provider:[[:space:]]*[^[:space:]#]' infra/deadman/watchdog.yaml.example
infra/deadman/check-routes-direct.sh infra/deadman/watchdog.yaml.example infra/deadman/uptime-checks.yaml.example
rm -rf /tmp/t14 && mkdir -p /tmp/t14
cat > /tmp/t14/registry.yaml <<'EOF'
products:
  - id: p-one
    infrastructure:
      provider: hetzner
EOF
sed -e 's|^provider: .*|provider: acme-cloud|' infra/deadman/watchdog.yaml.example > /tmp/t14/wd-opsvm.yaml
infra/deadman/check-off-vm.sh /tmp/t14/wd-opsvm.yaml acme-cloud /tmp/t14/registry.yaml; echo "rc=$?"
sed -e 's|^provider: .*|provider: hetzner|' infra/deadman/watchdog.yaml.example > /tmp/t14/wd-product.yaml
infra/deadman/check-off-vm.sh /tmp/t14/wd-product.yaml acme-cloud /tmp/t14/registry.yaml; echo "rc=$?"
sed -e 's|^provider: .*|provider: third-party-watchdog|' infra/deadman/watchdog.yaml.example > /tmp/t14/wd-ok.yaml
infra/deadman/check-off-vm.sh /tmp/t14/wd-ok.yaml acme-cloud /tmp/t14/registry.yaml
grep -c '^generated_from: registry$' infra/deadman/uptime-checks.yaml.example
git ls-files ops-vm/deadman infra/deadman | grep -Evc '(\.example|\.sh)$'
```

Expected output:

```
ALL-PARSE-OK
0
0
DEADMAN-ROUTES-DIRECT: PASS
provider equals the operations VM provider: acme-cloud
DEADMAN-OFF-VM: FAIL
rc=1
provider is a product infrastructure provider: hetzner
DEADMAN-OFF-VM: FAIL
rc=1
DEADMAN-OFF-VM: PASS
1
0
```

### STOP rule

If `infra/deadman/watchdog.yaml` names no provider, or names the operations VM's provider, GitHub, or any product's `infrastructure.provider`: **do not pick a provider, do not host the watchdog on the second host to "get the leg working", do not point the heartbeat at Grafana alerting on this VM.** D94 exists precisely because Section 45.2's claim of responder-source independence was false; a watchdog inside any of those three domains reproduces the failure the decision was written to close. Open a blocker (§1.4) with the decision line: *"The dead-man watchdog provider and the second-host location are unset or fall inside the VM, GitHub or a product provider; D94 and Section 51.5 require L0 and the Founder to record that decision."*

If the off-VM legs are not registered in the Section 49 asset inventory with a named owner: **do not create the entries here.** Section 51.5 names the registration and Section 49.1 names the owner; the entry is subsystem Q data with a real person on it. Open a blocker with the decision line: *"The two off-VM detection legs have no `detection_leg` inventory entry with a named owner; Section 51.5 requires the registration before the leg is relied on."*

Until the leg reports, Section 46.6 states the estate is **undetected, not healthy**. Do not record the phase as complete on the strength of a heartbeat this host emitted and nothing off this host confirmed.

---

## L5-04-15 — Patch cadence, singleton patch driver and the post-patch smoke checklist

**Size:** L · **Depends on:** L5-04-04, L5-04-05, L5-04-07, L5-04-14 · **Slug:** `patch-cadence`
**Spec:** 51.4 — *"Renovate patches what lives in repositories; the control-plane stack itself — Grafana, DevLake, the operations VM operating system, and the rest of the self-hosted estate — needs its own declared patch cadence, tracked through the tool register (Section 62)"*; each entry records **current version, declared patch cadence and the date last patched**; **staleness beyond the cadence is Amber**, and **a known-exploited vulnerability in a deployed version is Red**; security patches for Grafana and the VM OS run on an **expedited path, not batched**; the cadence carries **elevated priority because the people-intelligence layer raises the stakes**, and the separately-credentialed **Layer B datasource is patched and reviewed on the tightest cadence in the stack**; **the post-patch smoke checklist** runs after every stack patch — dashboards provision from JSON, both instances' datasources connect, alert rules fire a test alert, and the Founder-only Layer B instance's credential and authentication allowlist match the capability holders (90.4) — followed by a **mandated immediate reconciliation run**, and *"the patch is not recorded as complete until the checklist and the reconciliation run both pass clean"*; patching follows the change process of Section 61 scoped to the control plane, with the rollback answer known before the upgrade starts; **the singleton change shape** is `snapshot → upgrade → verify → revert-on-fail`, carrying the Section 61 change manifest and approval **but no canary stage**. Also 62.1 (the tool register), SIG-36 (Amber; **Red beyond twice the cadence**), invariant 82, invariant 85.

> **DECISION REQUIRED — routed to L0, not resolved here.**
> The cadence values per component are already listed in §1.6 as values this phase never invents. Beyond that, `tools.yaml` — the **tool register** Section 62.1 names as the home of each control-plane tool's `current_version`, `upgrade_policy`, `last_reviewed` and `criticality` — is **subsystem O (governance registries and jobs)**, **unassigned in PARTITION v1**, and it is a root-level control-plane registry that lane L5 does not own in any case. This task ships the cadence file as an **empty-valued example under `ops-vm/`** and a staleness computation that reads it, and hands the register rows to L0. It creates no `tools.yaml` row and claims no subsystem O work.

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/patch/cadence.yaml.example` | Per component: current version, declared cadence, last patched (empty values) |
| `ops-vm/patch/smoke-checklist.yaml` | The four Section 51.4 checks plus the mandated reconciliation run |
| `ops-vm/patch/patch-driver.sh` | `snapshot → upgrade → verify → revert-on-fail`; no canary stage |
| `ops-vm/checks/post-patch-smoke.sh` | Executes the checklist; the patch is complete only when it passes clean |
| `ops-vm/checks/patch_staleness.py` | SIG-36: Amber beyond cadence, Red beyond twice the cadence |
| `ops-vm/patch/L0-HANDOFF.md` | The tool-register rows this lane does not write |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t15-patch-cadence"
mkdir -p ops-vm/patch ops-vm/checks
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/patch/cadence.yaml.example <<'YAMLDOC'
# Control-plane patch cadence (Section 51.4), tracked through the tool register
# of Section 62.1. Every value below is calibrated configuration owned by L0.
# An implementer never fills this file.
#
# Grading, from the specification and not from this file:
#   staleness beyond the declared cadence is Amber on operating-system health;
#   SIG-36 is Amber, and Red beyond twice the cadence (Section 52.2);
#   a known-exploited vulnerability in a deployed version is Red (Section 51.4).
#
# expedited: true means security patches for that component are applied on the
# expedited path and are never batched to the routine window (Section 51.4).
# tightest_in_stack: true marks the Layer B Grafana component, which Section
# 51.4 requires to carry the tightest cadence in the stack. The staleness
# computation asserts that; it does not assume it.
components:
  - id: grafana-shared
    current_version:
    cadence_days:
    last_patched:
    expedited: true
    tightest_in_stack: false
  - id: grafana-layerb
    current_version:
    cadence_days:
    last_patched:
    expedited: true
    tightest_in_stack: true
  - id: devlake
    current_version:
    cadence_days:
    last_patched:
    expedited: false
    tightest_in_stack: false
  - id: devlake-db
    current_version:
    cadence_days:
    last_patched:
    expedited: false
    tightest_in_stack: false
  - id: prometheus
    current_version:
    cadence_days:
    last_patched:
    expedited: false
    tightest_in_stack: false
  - id: proxy
    current_version:
    cadence_days:
    last_patched:
    expedited: true
    tightest_in_stack: false
  - id: ops-vm-os
    current_version:
    cadence_days:
    last_patched:
    expedited: true
    tightest_in_stack: false
YAMLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/patch/smoke-checklist.yaml <<'YAMLDOC'
# The post-patch smoke checklist of Section 51.4. It runs after EVERY stack
# patch. The patch is not recorded as complete until every item and the
# reconciliation run below pass clean.
checklist:
  - id: SMOKE-1
    statement: "Dashboards provision from JSON"
    command: "ops-vm/checks/grafana-provisioned.sh $GRAFANA_SHARED_URL $GRAFANA_SHARED_TOKEN"
    expect: "GRAFANA-PROVISIONED: PASS"
  - id: SMOKE-2
    statement: "Both instances' datasources connect"
    command: "ops-vm/checks/grafana-provisioned.sh $GRAFANA_LAYERB_URL $GRAFANA_LAYERB_TOKEN"
    expect: "GRAFANA-PROVISIONED: PASS"
  - id: SMOKE-3
    statement: "Alert rules fire a test alert"
    command: "ops-vm/checks/alert-test-fires.sh"
    expect: "ALERT-TEST: PASS"
  - id: SMOKE-4
    statement: "The Founder-only Layer B instance's credential and authentication allowlist match the capability holders (Section 90.4)"
    command: "ops-vm/checks/layerb-allowlist-matches-holders.sh"
    expect: "LAYERB-ALLOWLIST: PASS"
mandated_reconciliation:
  id: SMOKE-5
  statement: "An immediate reconciliation run follows, mandated (Section 51.4)"
  command: "ops-vm/jobs/run-reconcile.sh full"
  expect: "exit 0"
completion_rule: >-
  The patch is not recorded as complete until the checklist and the
  reconciliation run both pass clean (Section 51.4).
YAMLDOC
```

`SMOKE-3` and `SMOKE-4` name two checks this task also creates, so the checklist has no dangling command:

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/alert-test-fires.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 51.4 post-patch item: alert rules fire a test alert. Fires the rule and
# asserts the designated channel accepted it; asserts nothing about content.
set -euo pipefail
BASE="${1:?usage: alert-test-fires.sh <grafana-base-url> <api-token>}"
TOKEN="${2:?}"
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 \
  -H "Authorization: Bearer $TOKEN" -X POST "$BASE/api/alertmanager/grafana/config/api/v1/receivers/test" \
  -H 'Content-Type: application/json' \
  --data '{"receivers":[{"name":"designated-channel"}]}')
case "$code" in
  2*) echo "ALERT-TEST: PASS" ;;
  *)  echo "ALERT-TEST: FAIL (http $code)"; exit 1 ;;
esac
SHDOC
chmod +x ops-vm/checks/alert-test-fires.sh

cat > ops-vm/checks/layerb-allowlist-matches-holders.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 90.4 post-patch item: the Founder-only Layer B instance's credential
# and authentication allowlist match the capability holders. Both sides are read
# as declared data; this check never edits either.
set -euo pipefail
ALLOW="${1:-ops-vm/layerb/access-list.yaml}"
HOLDERS="${2:?usage: layerb-allowlist-matches-holders.sh <access-list.yaml> <holders-file>}"
[ -f "$ALLOW" ]   || { echo "LAYERB-ALLOWLIST: FAIL (no $ALLOW)"; exit 1; }
[ -f "$HOLDERS" ] || { echo "LAYERB-ALLOWLIST: FAIL-CLOSED (no capability-holder list: $HOLDERS)"; exit 1; }
a=$(awk '/^ *- login: */{print $3}' "$ALLOW" | sort -u)
h=$(sort -u "$HOLDERS")
if [ "$a" = "$h" ]; then echo "LAYERB-ALLOWLIST: PASS"; exit 0; fi
echo "LAYERB-ALLOWLIST: FAIL"
echo "in allowlist, not a holder:"; comm -23 <(echo "$a") <(echo "$h")
echo "holder, not in allowlist:";   comm -13 <(echo "$a") <(echo "$h")
exit 1
SHDOC
chmod +x ops-vm/checks/layerb-allowlist-matches-holders.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/patch_staleness.py <<'PYDOC'
#!/usr/bin/env python3
"""SIG-36 control-plane patch staleness (Sections 51.4, 52.2, 62.1).

Grading, taken literally from the specification:
  Amber  when a component is beyond its declared cadence
  Red    when it is beyond twice its declared cadence (SIG-36)

Two structural rules of Section 51.4 are asserted rather than assumed:
  * every component declares current_version, cadence_days and last_patched;
    a component missing any of them cannot be graded and fails closed
  * the component marked tightest_in_stack carries the tightest cadence in the
    stack - no other component may declare a shorter cadence

Exit codes: 0 all within cadence; 2 Amber; 3 Red; 1 fail-closed.
"""
import datetime
import sys

import yaml


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "ops-vm/patch/cadence.yaml"
    try:
        doc = yaml.safe_load(open(path, "r", encoding="utf-8")) or {}
    except OSError as exc:
        print("PATCH-STALENESS: FAIL-CLOSED (%s)" % exc)
        return 1
    comps = doc.get("components") or []
    if not comps:
        print("PATCH-STALENESS: FAIL-CLOSED (no components declared)")
        return 1
    today = datetime.date.today()
    graded, tightest = [], None
    for c in comps:
        cid = c.get("id", "<unnamed>")
        for key in ("current_version", "cadence_days", "last_patched"):
            if c.get(key) in (None, ""):
                print("PATCH-STALENESS: FAIL-CLOSED (%s has no %s)" % (cid, key))
                return 1
        try:
            cad = int(c["cadence_days"])
            last = datetime.date.fromisoformat(str(c["last_patched"]))
        except (TypeError, ValueError):
            print("PATCH-STALENESS: FAIL-CLOSED (%s has an unreadable cadence "
                  "or last_patched date)" % cid)
            return 1
        if c.get("tightest_in_stack"):
            tightest = (cid, cad)
        graded.append((cid, cad, (today - last).days))
    if tightest is None:
        print("PATCH-STALENESS: FAIL-CLOSED (no component is marked "
              "tightest_in_stack; Section 51.4 requires the Layer B datasource "
              "to carry the tightest cadence in the stack)")
        return 1
    for cid, cad, _age in graded:
        if cid != tightest[0] and cad < tightest[1]:
            print("PATCH-STALENESS: FAIL-CLOSED (%s declares a cadence of %dd, "
                  "tighter than the Layer B cadence of %dd; Section 51.4 makes "
                  "Layer B the tightest in the stack)" % (cid, cad, tightest[1]))
            return 1
    rc = 0
    for cid, cad, age in sorted(graded):
        if age >= 2 * cad:
            print("%s: %dd since patch, cadence %dd -> RED" % (cid, age, cad))
            rc = 3
        elif age >= cad:
            print("%s: %dd since patch, cadence %dd -> AMBER" % (cid, age, cad))
            rc = max(rc, 2)
        else:
            print("%s: %dd since patch, cadence %dd -> OK" % (cid, age, cad))
    print("PATCH-STALENESS: %s" % {0: "PASS", 2: "AMBER", 3: "RED"}[rc])
    return rc


if __name__ == "__main__":
    sys.exit(main())
PYDOC
chmod +x ops-vm/checks/patch_staleness.py
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/post-patch-smoke.sh <<'SHDOC'
#!/usr/bin/env bash
# The post-patch smoke checklist of Section 51.4, followed by the mandated
# immediate reconciliation run. The patch is not recorded as complete until both
# pass clean. This script records no completion; it prints a verdict.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
require_env GRAFANA_SHARED_URL GRAFANA_SHARED_TOKEN GRAFANA_LAYERB_URL \
            GRAFANA_LAYERB_TOKEN CAPABILITY_HOLDERS_FILE
fail=0
ops-vm/checks/grafana-provisioned.sh "$GRAFANA_SHARED_URL" "$GRAFANA_SHARED_TOKEN" || fail=1
ops-vm/checks/grafana-provisioned.sh "$GRAFANA_LAYERB_URL" "$GRAFANA_LAYERB_TOKEN" || fail=1
ops-vm/checks/alert-test-fires.sh "$GRAFANA_SHARED_URL" "$GRAFANA_SHARED_TOKEN" || fail=1
ops-vm/checks/layerb-allowlist-matches-holders.sh ops-vm/layerb/access-list.yaml "$CAPABILITY_HOLDERS_FILE" || fail=1
if [ "$fail" -ne 0 ]; then echo "POST-PATCH-SMOKE: FAIL (checklist)"; exit 1; fi
OPS_VM_TRIGGER=post-patch-smoke ops-vm/jobs/run-reconcile.sh full \
  || { echo "POST-PATCH-SMOKE: FAIL (mandated reconciliation run)"; exit 1; }
echo "POST-PATCH-SMOKE: PASS"
SHDOC
chmod +x ops-vm/checks/post-patch-smoke.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/patch/patch-driver.sh <<'SHDOC'
#!/usr/bin/env bash
# The singleton control-plane change shape of Section 51.4:
#   snapshot -> upgrade -> verify -> revert-on-fail
# There is no canary stage: there is one Grafana, one DevLake, one operations VM
# (Section 51.4). The Section 61 change manifest and approval are carried; the
# snapshot IS the rollback answer, known before the upgrade starts.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
COMPONENT="${1:?usage: patch-driver.sh <component-id>}"
require_env CHANGE_MANIFEST_ID CHANGE_APPROVAL_RECORD SNAPSHOT_CMD UPGRADE_CMD REVERT_CMD

log "patch: component=$COMPONENT manifest=$CHANGE_MANIFEST_ID approval=$CHANGE_APPROVAL_RECORD"

# 1. snapshot - the rollback answer, known before the upgrade starts
snap=$($SNAPSHOT_CMD "$COMPONENT") || fail_closed "snapshot failed; no rollback answer, so no upgrade"
log "patch: snapshot=$snap"

# 2. upgrade
if ! $UPGRADE_CMD "$COMPONENT"; then
  log "patch: upgrade failed; reverting to $snap"
  $REVERT_CMD "$COMPONENT" "$snap"
  record_run "patch-$COMPONENT" failed "upgrade failed; reverted to $snap"
  notify/bin/notify-job-result.sh "patch-$COMPONENT" failed "upgrade failed; reverted"
  exit 1
fi

# 3. verify - the post-patch smoke checklist IS the verify step (Section 51.4)
if ! ops-vm/checks/post-patch-smoke.sh; then
  log "patch: verify failed; reverting to $snap"
  $REVERT_CMD "$COMPONENT" "$snap"
  record_run "patch-$COMPONENT" failed "verify failed; reverted to $snap"
  notify/bin/notify-job-result.sh "patch-$COMPONENT" failed "verify failed; reverted"
  exit 1
fi

# 4. complete - only now, and only because both the checklist and the mandated
#    reconciliation run passed clean (Section 51.4)
record_run "patch-$COMPONENT" ok "manifest=$CHANGE_MANIFEST_ID snapshot=$snap"
echo "PATCH-COMPLETE: $COMPONENT"
SHDOC
chmod +x ops-vm/patch/patch-driver.sh

cat > ops-vm/patch/L0-HANDOFF.md <<'MDDOC'
# Handoff: the tool-register rows for the control-plane stack

Section 51.4 tracks the control-plane patch cadence **through the tool register**
of Section 62.1. The register is `tools.yaml` - a root-level control-plane
registry, and part of **subsystem O (governance registries and jobs)**, which is
**unassigned in PARTITION v1**. Lane L5 owns `ops-vm/**`, `infra/**`,
`assets/**` and `notify/**`, and writes neither.

What L5 has built and where it is:

| Built | Path |
| --- | --- |
| The per-component cadence file the VM reads | `ops-vm/patch/cadence.yaml.example` (empty values; the real file is supplied on the host) |
| The SIG-36 staleness computation | `ops-vm/checks/patch_staleness.py` |
| The post-patch smoke checklist | `ops-vm/patch/smoke-checklist.yaml`, `ops-vm/checks/post-patch-smoke.sh` |
| The singleton patch driver | `ops-vm/patch/patch-driver.sh` |

What L0 must decide and own, and what L5 will not do:

1. Assign subsystem O.
2. Create the `tools.yaml` rows for `grafana-shared`, `grafana-layerb`,
   `devlake`, `devlake-db`, `prometheus`, `proxy` and `ops-vm-os`, each with the
   `current_version`, `upgrade_policy`, `last_reviewed` and `criticality`
   fields Section 62.1 declares.
3. Set the cadence value per component. Section 51.4 requires the Layer B
   Grafana component to carry the tightest cadence in the stack; the staleness
   computation fails closed when it does not, so this is a checked constraint on
   the values, not a preference.
MDDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add ops-vm/patch ops-vm/checks/post-patch-smoke.sh ops-vm/checks/patch_staleness.py ops-vm/checks/alert-test-fires.sh ops-vm/checks/layerb-allowlist-matches-holders.sh
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-15: patch cadence, singleton patch driver and the post-patch smoke checklist"
git push -u origin "lane/5/04-t15-patch-cadence"
gh pr create --base integration --title "L5-04-15: patch cadence and post-patch smoke checklist" --body "Lane L5 phase 4 task L5-04-15. Paths: ops-vm/** only. Spec: 51.4, 62.1, 61, 90.4, SIG-36, invariants 82, 85."
gh issue create \
  --title "DECISION REQUIRED L5-04-15 -> L0: tool-register rows for the control-plane stack" \
  --label "blocker,lane-5,phase-4,l0-decision" \
  --body "$(cat ops-vm/patch/L0-HANDOFF.md)"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Every script parses | `python3 -m py_compile ops-vm/checks/patch_staleness.py && for f in ops-vm/patch/patch-driver.sh ops-vm/checks/post-patch-smoke.sh ops-vm/checks/alert-test-fires.sh ops-vm/checks/layerb-allowlist-matches-holders.sh; do bash -n "$f" \|\| exit 1; done; echo ALL-PARSE-OK` | `ALL-PARSE-OK` |
| 2 | The driver carries the singleton shape and no canary stage | `grep -Ec '^# *(1\. snapshot|2\. upgrade|3\. verify|4\. complete)' ops-vm/patch/patch-driver.sh; grep -ic 'canary' ops-vm/patch/patch-driver.sh` | `4` then `1` (the one line stating there is no canary stage) |
| 3 | The driver refuses to upgrade without a change manifest and approval | SELF-VERIFY, the `patch-driver.sh` line | `FAIL-CLOSED: required configuration is absent` then `rc=1` |
| 4 | The checklist carries all four Section 51.4 items plus the reconciliation run | `grep -c '^  - id: SMOKE-' ops-vm/patch/smoke-checklist.yaml; grep -c '^  id: SMOKE-5$' ops-vm/patch/smoke-checklist.yaml` | `4` then `1` |
| 5 | Staleness grades Amber at the cadence and Red at twice it | SELF-VERIFY, the two `patch_staleness.py` grading runs | `grafana-layerb: 40d since patch, cadence 30d -> AMBER` … `PATCH-STALENESS: AMBER`, then `grafana-layerb: 70d since patch, cadence 30d -> RED` … `PATCH-STALENESS: RED` |
| 6 | Layer B must be the tightest cadence in the stack | SELF-VERIFY, the `looser-layerb` run | `PATCH-STALENESS: FAIL-CLOSED (devlake declares a cadence of 10d, tighter than the Layer B cadence of 30d; Section 51.4 makes Layer B the tightest in the stack)` then `rc=1` |
| 7 | An ungradeable component fails closed rather than reading as clean | SELF-VERIFY, the `ops-vm/patch/cadence.yaml.example` run | `PATCH-STALENESS: FAIL-CLOSED (grafana-shared has no current_version)` then `rc=1` |
| 8 | No cadence value is committed | `grep -Ec '^ +(current_version|cadence_days|last_patched): .+$' ops-vm/patch/cadence.yaml.example` | `0` |
| 9 | The patch completes only after the checklist and the reconciliation run | `grep -c 'post-patch-smoke.sh' ops-vm/patch/patch-driver.sh; grep -c 'run-reconcile.sh full' ops-vm/checks/post-patch-smoke.sh` | `1` then `1` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
python3 -m py_compile ops-vm/checks/patch_staleness.py && for f in ops-vm/patch/patch-driver.sh ops-vm/checks/post-patch-smoke.sh ops-vm/checks/alert-test-fires.sh ops-vm/checks/layerb-allowlist-matches-holders.sh; do bash -n "$f" || exit 1; done; echo ALL-PARSE-OK
grep -Ec '^# *(1\. snapshot|2\. upgrade|3\. verify|4\. complete)' ops-vm/patch/patch-driver.sh
grep -ic 'canary' ops-vm/patch/patch-driver.sh
grep -c '^  - id: SMOKE-' ops-vm/patch/smoke-checklist.yaml
grep -c '^  id: SMOKE-5$' ops-vm/patch/smoke-checklist.yaml
( cd /tmp && CHANGE_MANIFEST_ID= CHANGE_APPROVAL_RECORD= SNAPSHOT_CMD= UPGRADE_CMD= REVERT_CMD= \
    bash "$CONTROL_PLANE_ROOT/ops-vm/patch/patch-driver.sh" grafana-shared; echo "rc=$?" )
python3 ops-vm/checks/patch_staleness.py ops-vm/patch/cadence.yaml.example; echo "rc=$?"
rm -rf /tmp/t15 && mkdir -p /tmp/t15
python3 - <<'PY'
import datetime
def w(path, layerb_age, layerb_cad, devlake_cad):
    d = datetime.date.today()
    open(path, "w").write(
        "components:\n"
        "  - id: grafana-layerb\n    current_version: v1\n"
        "    cadence_days: %d\n    last_patched: \"%s\"\n"
        "    expedited: true\n    tightest_in_stack: true\n"
        "  - id: devlake\n    current_version: v1\n"
        "    cadence_days: %d\n    last_patched: \"%s\"\n"
        "    expedited: false\n    tightest_in_stack: false\n"
        % (layerb_cad, d - datetime.timedelta(days=layerb_age),
           devlake_cad, d))
w("/tmp/t15/amber.yaml", 40, 30, 90)
w("/tmp/t15/red.yaml", 70, 30, 90)
w("/tmp/t15/looser-layerb.yaml", 1, 30, 10)
PY
python3 ops-vm/checks/patch_staleness.py /tmp/t15/amber.yaml; echo "rc=$?"
python3 ops-vm/checks/patch_staleness.py /tmp/t15/red.yaml; echo "rc=$?"
python3 ops-vm/checks/patch_staleness.py /tmp/t15/looser-layerb.yaml; echo "rc=$?"
grep -Ec '^ +(current_version|cadence_days|last_patched): .+$' ops-vm/patch/cadence.yaml.example
grep -c 'post-patch-smoke.sh' ops-vm/patch/patch-driver.sh
grep -c 'run-reconcile.sh full' ops-vm/checks/post-patch-smoke.sh
```

Expected output:

```
ALL-PARSE-OK
4
1
4
1
missing required key: CHANGE_MANIFEST_ID
missing required key: CHANGE_APPROVAL_RECORD
missing required key: SNAPSHOT_CMD
missing required key: UPGRADE_CMD
missing required key: REVERT_CMD
<timestamp> FAIL-CLOSED: required configuration is absent
rc=1
PATCH-STALENESS: FAIL-CLOSED (grafana-shared has no current_version)
rc=1
devlake: 0d since patch, cadence 90d -> OK
grafana-layerb: 40d since patch, cadence 30d -> AMBER
PATCH-STALENESS: AMBER
rc=2
devlake: 0d since patch, cadence 90d -> OK
grafana-layerb: 70d since patch, cadence 30d -> RED
PATCH-STALENESS: RED
rc=3
PATCH-STALENESS: FAIL-CLOSED (devlake declares a cadence of 10d, tighter than the Layer B cadence of 30d; Section 51.4 makes Layer B the tightest in the stack)
rc=1
0
1
1
```

### STOP rule

If any component's cadence, current version or last-patched date is absent from the host `cadence.yaml`: **do not pick a cadence, do not treat an ungraded component as within cadence.** The values are calibrated configuration in the tool register (§1.6, Sections 51.4 and 62.1). Open a blocker (§1.4) with the decision line: *"A control-plane component has no declared patch cadence, current version or last-patched date; Section 62.1 places those values in the tool register and L0 must supply them."*

If any component declares a cadence tighter than the Layer B Grafana component's: **do not loosen the other component to make the check pass.** Section 51.4 requires the separately-credentialed Layer B datasource to be patched and reviewed on the **tightest cadence in the stack**; the correct movement is to tighten Layer B, and that is L0's value to set. Open a blocker with the decision line: *"A control-plane component declares a cadence tighter than Layer B's; Section 51.4 makes Layer B the tightest in the stack and L0 must reset the values."*

If `post-patch-smoke.sh` or the mandated reconciliation run does not pass clean: **do not record the patch as complete, do not re-run the checklist until it passes, do not skip the reconciliation run.** Section 51.4 states the completion rule without an exception. The driver has already reverted to the snapshot; open a blocker with the decision line: *"A control-plane patch verified dirty and was reverted to its snapshot; Section 51.4 forbids recording it complete and L0 must decide the next attempt."*

---

## L5-04-16 — Rebuild driver, step manifest and the generated runbook

**Size:** L · **Depends on:** L5-04-02 through L5-04-13, L5-04-15 · **Slug:** `rebuild-driver`
**Spec:** 45.4 — the reconstruction runbook is a **first-class artifact**, `docs/control-plane-rebuild.md` in the control-plane repository, and the quarterly restore test **executes it as written**: *"a step the runbook omits is a test failure, not an operator improvisation"*; the 4-hour clock **starts at provision-start and stops at dashboards-green, including the Layer B restore** — *"a rebuild that leaves Layer B unrestored has not finished"*; the clock assumes GitHub is reachable, and where the organisation is unavailable the rebuild runs from the organisation export instead and carries the separate target declared in 45.2. Also 45.1 (the minimum reconstruction set), 51.5 (everything the VM runs is provisioned from the control-plane repository), 51.2 (control-plane recovery time: restorable within 4 hours, quarterly restore test), invariant 3.

**Boundary:** `docs/**` is **L0's** (PARTITION lane table). This task generates `ops-vm/rebuild-driver/runbook.generated.md` inside an owned path and ends in a **handoff issue** asking L0 to install it as `docs/control-plane-rebuild.md`. It never writes under `docs/`.

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/rebuild-driver/steps.yaml` | The ordered step manifest — every provisioning script and every unit |
| `ops-vm/rebuild-driver/rebuild.sh` | Executes the manifest in order, timestamping each step |
| `ops-vm/rebuild-driver/generate-runbook.sh` | Renders `steps.yaml` to markdown |
| `ops-vm/rebuild-driver/runbook.generated.md` | The generated runbook, committed so a rebuild has it in git |
| `ops-vm/checks/rebuild-steps-complete.sh` | Fails when any provisioning script or unit is missing from the manifest |
| `ops-vm/rebuild-driver/L0-HANDOFF.md` | The `docs/control-plane-rebuild.md` handoff |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t16-rebuild-driver"
mkdir -p ops-vm/rebuild-driver ops-vm/checks
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/rebuild-driver/steps.yaml <<'YAMLDOC'
# The ordered control-plane rebuild manifest (Section 45.4).
# The quarterly drill executes this as written. A step this manifest omits is a
# test failure, not an operator improvisation - which is why
# ops-vm/checks/rebuild-steps-complete.sh fails when any provisioning script or
# any systemd unit in this repository is absent from the list below.
#
# Clock semantics (Section 45.4): the clock starts at PROVISION-START and stops
# at DASHBOARDS-GREEN, and DASHBOARDS-GREEN is not reached until the Layer B
# restore has completed. A rebuild that leaves Layer B unrestored has not
# finished.
clock:
  starts_at: provision-start
  stops_at: dashboards-green
  includes_layer_b_restore: true
  target_hours: 4
  github_reachable_assumption: true
steps:
  - id: R01
    marker: provision-start
    run: "ops-vm/provision/00-base.sh"
  - id: R02
    run: "ops-vm/provision/10-private-path.sh"
  - id: R03
    run: "ops-vm/provision/20-sso-proxy.sh"
  - id: R04
    run: "ops-vm/provision/30-stack-up.sh"
  - id: R05
    run: "ops-vm/provision/40-layerb-volume.sh"
  - id: R06
    run: "systemctl enable --now reconcile-full.timer"
    unit: "reconcile-full.service"
  - id: R07
    run: "systemctl enable --now reconcile-security.timer"
    unit: "reconcile-security.service"
  - id: R08
    run: "systemctl enable --now health-report.timer"
    unit: "health-report.service"
  - id: R09
    run: "systemctl enable --now scorecard.timer"
    unit: "scorecard.service"
  - id: R10
    run: "systemctl enable --now renovate.timer"
    unit: "renovate.service"
  - id: R11
    run: "systemctl enable --now expiry-check.timer"
    unit: "expiry-check.service"
  - id: R12
    run: "systemctl enable --now restore-rotation.timer"
    unit: "restore-rotation.service"
  - id: R13
    run: "systemctl enable --now org-export.timer"
    unit: "org-export.service"
  - id: R14
    run: "systemctl enable --now layerb-backup.timer"
    unit: "layerb-backup.service"
  - id: R15
    run: "systemctl enable --now deadman-heartbeat.timer"
    unit: "deadman-heartbeat.service"
  - id: R16
    run: "LAYER-B RESTORE - performed by the Founder or a named written designate only (Section 45.4); no machine identity and no other person touches the people-data store"
    human_only: true
  - id: R17
    marker: dashboards-green
    run: "ops-vm/checks/post-patch-smoke.sh"
YAMLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/rebuild-steps-complete.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 45.4: the drill executes the runbook AS WRITTEN, and a step the runbook
# omits is a test failure. This check makes that mechanical: every provisioning
# script and every systemd service unit in this repository must appear in the
# rebuild manifest.
set -euo pipefail
M="${1:-ops-vm/rebuild-driver/steps.yaml}"
[ -f "$M" ] || { echo "REBUILD-STEPS: FAIL (no $M)"; exit 1; }
missing=0
for f in ops-vm/provision/*.sh; do
  grep -qF "$f" "$M" || { echo "not in manifest: $f"; missing=1; }
done
for u in ops-vm/systemd/*.service; do
  b=$(basename "$u")
  grep -qF "$b" "$M" || { echo "not in manifest: $b"; missing=1; }
done
grep -q '^  starts_at: provision-start$'        "$M" || { echo "clock does not start at provision-start"; missing=1; }
grep -q '^  stops_at: dashboards-green$'        "$M" || { echo "clock does not stop at dashboards-green"; missing=1; }
grep -q '^  includes_layer_b_restore: true$'    "$M" || { echo "clock excludes the Layer B restore"; missing=1; }
grep -q '^  target_hours: 4$'                   "$M" || { echo "clock target is not 4 hours"; missing=1; }
if [ "$missing" -eq 0 ]; then echo "REBUILD-STEPS: PASS"; else echo "REBUILD-STEPS: FAIL"; exit 1; fi
SHDOC
chmod +x ops-vm/checks/rebuild-steps-complete.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/rebuild-driver/rebuild.sh <<'SHDOC'
#!/usr/bin/env bash
# Execute the rebuild manifest in order, timestamping every step.
# The clock starts at the provision-start marker and stops at dashboards-green,
# and dashboards-green is not reached until the Layer B restore has completed
# (Section 45.4). Human-only steps are NOT executed here: the script stops and
# waits for the confirmation record.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
M="${1:-ops-vm/rebuild-driver/steps.yaml}"
require_file "$M"
ops-vm/checks/rebuild-steps-complete.sh "$M"
OUT=/var/lib/ops-vm/rebuild
install -d -m 0750 "$OUT"
start=$(date -u +%s)
printf 'provision-start %s\n' "$start" > "$OUT/clock.txt"
python3 - "$M" > "$OUT/plan.txt" <<'PY'
import sys, yaml
doc = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
for s in doc["steps"]:
    print("%s\t%s\t%s" % (s["id"], "human" if s.get("human_only") else "machine", s["run"]))
PY
while IFS=$'\t' read -r id kind cmd; do
  if [ "$kind" = "human" ]; then
    log "rebuild: $id is human-only and is not executed by this script"
    [ -n "${LAYERB_RESTORE_CONFIRMATION_RECORD:-}" ] \
      || fail_closed "$id requires the Layer B restore confirmation record; the rebuild is not finished without it (Section 45.4)"
    printf '%s human-confirmed %s %s\n' "$id" "$LAYERB_RESTORE_CONFIRMATION_RECORD" "$(date -u +%s)" >> "$OUT/clock.txt"
    continue
  fi
  log "rebuild: $id -> $cmd"
  eval "$cmd" || fail_closed "$id failed: $cmd"
  printf '%s done %s\n' "$id" "$(date -u +%s)" >> "$OUT/clock.txt"
done < "$OUT/plan.txt"
end=$(date -u +%s)
printf 'dashboards-green %s\n' "$end" >> "$OUT/clock.txt"
elapsed=$(( (end - start) / 60 ))
record_run rebuild ok "elapsed_minutes=$elapsed"
echo "REBUILD-COMPLETE: elapsed_minutes=$elapsed"
SHDOC
chmod +x ops-vm/rebuild-driver/rebuild.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/rebuild-driver/generate-runbook.sh <<'SHDOC'
#!/usr/bin/env bash
# Render the manifest to the runbook markdown. The runbook is generated, never
# hand-written, so that an added provisioning script cannot silently fail to
# reach it (Section 45.4).
set -euo pipefail
M="${1:-ops-vm/rebuild-driver/steps.yaml}"
O="${2:-ops-vm/rebuild-driver/runbook.generated.md}"
python3 - "$M" > "$O" <<'PY'
import sys, yaml
doc = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
c = doc["clock"]
print("# Control-plane rebuild runbook (generated)")
print()
print("Generated from `ops-vm/rebuild-driver/steps.yaml` by")
print("`ops-vm/rebuild-driver/generate-runbook.sh`. Do not hand-edit: edit the")
print("manifest and regenerate. Section 45.4 makes this runbook a first-class")
print("artifact and requires the quarterly drill to execute it *as written* - a")
print("step this file omits is a test failure, not an operator improvisation.")
print()
print("## The clock")
print()
print("* Starts at **%s**." % c["starts_at"])
print("* Stops at **%s**." % c["stops_at"])
print("* Includes the Layer B restore: **%s**. A rebuild that leaves Layer B"
      % str(c["includes_layer_b_restore"]).lower())
print("  unrestored has not finished (Section 45.4).")
print("* Target: **under %d hours** (Sections 45.4, 51.2)." % c["target_hours"])
print("* Assumes GitHub is reachable, because the reconstruction set lives there")
print("  (Section 45.1). Where the organisation is unavailable the rebuild runs")
print("  from the organisation export instead and carries the separate target")
print("  declared in Section 45.2.")
print()
print("## Steps, in order")
print()
print("| # | Step | Run |")
print("| --- | --- | --- |")
for s in doc["steps"]:
    marker = " *(%s)*" % s["marker"] if s.get("marker") else ""
    who = "**HUMAN ONLY** - " if s.get("human_only") else ""
    print("| %s%s | %s | `%s` |" % (s["id"], marker, who or "machine", s["run"]))
PY
echo "RUNBOOK-GENERATED: $O"
SHDOC
chmod +x ops-vm/rebuild-driver/generate-runbook.sh
ops-vm/rebuild-driver/generate-runbook.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/rebuild-driver/L0-HANDOFF.md <<'MDDOC'
# Handoff: `docs/control-plane-rebuild.md`

Section 45.4 names the reconstruction runbook a first-class artifact at
`docs/control-plane-rebuild.md` in the control-plane repository. `docs/**` is
**L0's** path under the FROZEN PARTITION lane table; lane L5 does not write it.

L5 has produced the runbook inside an owned path:

* Manifest: `ops-vm/rebuild-driver/steps.yaml`
* Generator: `ops-vm/rebuild-driver/generate-runbook.sh`
* Generated artifact: `ops-vm/rebuild-driver/runbook.generated.md`
* Completeness check: `ops-vm/checks/rebuild-steps-complete.sh`

L0 installs the generated artifact at `docs/control-plane-rebuild.md`. Because
Section 45.4 requires the drill to execute the runbook **as written**, the
installed copy must remain a copy of the generated file: a hand-edit to
`docs/control-plane-rebuild.md` that is not in the manifest is exactly the
omission the section calls a test failure. The completeness check above is the
detector, and it lives in `ops-vm/`, so it runs on every L5 pull request.
MDDOC

git add ops-vm/rebuild-driver ops-vm/checks/rebuild-steps-complete.sh
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-16: rebuild driver, step manifest and the generated runbook"
git push -u origin "lane/5/04-t16-rebuild-driver"
gh pr create --base integration --title "L5-04-16: rebuild driver and generated runbook" --body "Lane L5 phase 4 task L5-04-16. Paths: ops-vm/** only. Spec: 45.4, 45.1, 45.2, 51.2, 51.5, invariant 3."
gh issue create \
  --title "HANDOFF L5-04-16 -> L0: install the generated control-plane rebuild runbook" \
  --label "handoff,lane-5,phase-4,l0-decision" \
  --body "$(cat ops-vm/rebuild-driver/L0-HANDOFF.md)"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Driver, generator and check parse | `for f in ops-vm/rebuild-driver/rebuild.sh ops-vm/rebuild-driver/generate-runbook.sh ops-vm/checks/rebuild-steps-complete.sh; do bash -n "$f" \|\| exit 1; done; echo ALL-PARSE-OK` | `ALL-PARSE-OK` |
| 2 | The manifest is valid YAML | `python3 -c "import yaml;print(len(yaml.safe_load(open('ops-vm/rebuild-driver/steps.yaml'))['steps']))"` | `17` |
| 3 | Every provisioning script and unit is in the manifest | `ops-vm/checks/rebuild-steps-complete.sh` | `REBUILD-STEPS: PASS` |
| 4 | An added provisioning script fails the check until it is listed | SELF-VERIFY, the `ZZ-negative.sh` block | `not in manifest: ops-vm/provision/ZZ-negative.sh` then `REBUILD-STEPS: FAIL` then `rc=1` |
| 5 | The clock starts, stops and scopes exactly as 45.4 states | `grep -Ec '^  (starts_at: provision-start|stops_at: dashboards-green|includes_layer_b_restore: true|target_hours: 4)$' ops-vm/rebuild-driver/steps.yaml` | `4` |
| 6 | The Layer B restore is human-only and is not executed by the driver | `grep -c 'human_only: true' ops-vm/rebuild-driver/steps.yaml; grep -c 'is human-only and is not executed by this script' ops-vm/rebuild-driver/rebuild.sh` | `1` then `1` |
| 7 | The driver refuses to finish without the Layer B restore confirmation | `grep -c 'the rebuild is not finished without it (Section 45.4)' ops-vm/rebuild-driver/rebuild.sh` | `1` |
| 8 | The runbook is generated, and regenerating it changes nothing | SELF-VERIFY, the regenerate-and-diff block | `RUNBOOK-GENERATED: ops-vm/rebuild-driver/runbook.generated.md` then `RUNBOOK-STABLE` |
| 9 | This task writes nothing under `docs/` | `git diff --cached --name-only \| grep -c '^docs/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for f in ops-vm/rebuild-driver/rebuild.sh ops-vm/rebuild-driver/generate-runbook.sh ops-vm/checks/rebuild-steps-complete.sh; do bash -n "$f" || exit 1; done; echo ALL-PARSE-OK
python3 -c "import yaml;print(len(yaml.safe_load(open('ops-vm/rebuild-driver/steps.yaml'))['steps']))"
ops-vm/checks/rebuild-steps-complete.sh
printf '#!/usr/bin/env bash\ntrue\n' > ops-vm/provision/ZZ-negative.sh
ops-vm/checks/rebuild-steps-complete.sh; echo "rc=$?"
rm -f ops-vm/provision/ZZ-negative.sh
ops-vm/checks/rebuild-steps-complete.sh
grep -Ec '^  (starts_at: provision-start|stops_at: dashboards-green|includes_layer_b_restore: true|target_hours: 4)$' ops-vm/rebuild-driver/steps.yaml
grep -c 'human_only: true' ops-vm/rebuild-driver/steps.yaml
grep -c 'the rebuild is not finished without it (Section 45.4)' ops-vm/rebuild-driver/rebuild.sh
cp ops-vm/rebuild-driver/runbook.generated.md /tmp/runbook-before.md
ops-vm/rebuild-driver/generate-runbook.sh
diff -q /tmp/runbook-before.md ops-vm/rebuild-driver/runbook.generated.md && echo RUNBOOK-STABLE
```

Expected output:

```
ALL-PARSE-OK
17
REBUILD-STEPS: PASS
not in manifest: ops-vm/provision/ZZ-negative.sh
REBUILD-STEPS: FAIL
rc=1
REBUILD-STEPS: PASS
4
1
1
RUNBOOK-GENERATED: ops-vm/rebuild-driver/runbook.generated.md
RUNBOOK-STABLE
```

### STOP rule

If `ops-vm/checks/rebuild-steps-complete.sh` reports a provisioning script or a unit missing from the manifest: **add it to `steps.yaml` and regenerate the runbook; never delete the script, never relax the check, never hand-edit `runbook.generated.md`.** Section 45.4 is explicit that a step the runbook omits is a **test failure**, so a check made to pass by removing its subject is the failure it exists to detect.

If the rebuild must run while the GitHub organisation is unavailable: **do not run this manifest against the 4-hour target.** Section 45.4 states the clock assumes GitHub is reachable because the reconstruction set lives there, and Section 45.2 gives that scenario its **own** target — calibrated configuration, initial value 24 hours, because an export restore precedes the rebuild. Open a blocker (§1.4) with the decision line: *"A rebuild is required while the GitHub organisation is unavailable; Section 45.2 gives that scenario a separate target and L0 must confirm the export-restore path before the clock is started."*

If anyone asks for `docs/control-plane-rebuild.md` to be written from this lane: **refuse.** `docs/**` is L0's under the FROZEN partition (rule 1). The handoff issue above is the whole of this lane's action.

---

## L5-04-17 — Quarterly rebuild drill: 4-hour clock, VM-stop verification, zero-resources evidence

**Size:** L · **Depends on:** L5-04-14, L5-04-16 · **Slug:** `rebuild-drill`
**Spec:** 45.4 — the rebuild is exercised by a **quarterly restore test**; the runbook is executed **as written**; **each drill writes a drill record to `records/`**; **the Layer B restore protocol** — *"The Founder — or a named person the Founder designates in writing — performs the Layer B restore personally; no machine identity and no other person touches the people-data store during a drill"*; the integrity check is **decrypt-plus-checksum-manifest**, verified *"without opening any document"*; the drill copy runs on a host and volumes **provisioned for the drill and tagged as such**, and is **destroyed on evidence rather than on attestation** — the drill record carries the provider's post-drill resource listing for that tag showing **zero resources**, and names the explicit deletion of the drill host's **volume snapshots and provider-side backups**, which a filesystem wipe does not reach; the confirmation lands through the **RECORD-VERIFICATION-RESULT dispatch (Section 97.2)** with a named executor; **a drill record filed without its zero-resources evidence is Blocking drift**. 51.5 — *"The quarterly drill (Section 45.4) verifies both fire by stopping the VM, not merely by rebuilding it."* 45.2 (the GitHub-unavailable variant is exercised at least annually). 51.2, AT-035, invariant 3.

**Boundary:** `records/**` is lane **L4's** (PARTITION: L4 owns all of `control-plane-records`). This task produces the drill record **content** under an owned path and ends in a handoff; it never writes `records/`.

### Files created

| Path | Purpose |
| --- | --- |
| `ops-vm/drill/drill.sh` | Runs the drill in order: stop the VM, verify the legs, rebuild, verify the clock |
| `ops-vm/drill/drill-record.template.yaml` | The drill record content, with every 45.4 evidence field |
| `ops-vm/checks/drill-clock.sh` | Asserts the clock semantics and the 4-hour target |
| `ops-vm/checks/drill-offvm-legs-fired.sh` | Asserts both off-VM legs fired **while the VM was stopped** |
| `ops-vm/checks/drill-zero-resources.sh` | Asserts the zero-resources listing and the named snapshot/backup deletions |
| `ops-vm/drill/L4-HANDOFF.md` | The `records/` handoff |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t17-rebuild-drill"
mkdir -p ops-vm/drill ops-vm/checks
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/drill/drill-record.template.yaml <<'YAMLDOC'
# Quarterly control-plane rebuild drill record (Section 45.4).
# Every field below is evidence, not attestation. A drill record filed without
# its zero-resources evidence is Blocking drift (Section 45.4).
drill_id:
quarter:
executed_by:                 # named person
runbook_executed_as_written: # true only if no step was improvised
omitted_steps:               # any value other than an empty list is a TEST FAILURE
clock:
  provision_start:           # ISO-8601 UTC
  dashboards_green:          # ISO-8601 UTC
  elapsed_minutes:
  target_minutes: 240
  layer_b_restored: false
vm_stop_verification:
  vm_stopped_at:
  vm_restarted_at:
  external_uptime_check_fired: false
  dead_mans_switch_fired: false
  routed_to_messaging_channel: false
  routed_to_phone_path: false
layer_b_restore:
  performed_by:              # the Founder, or the person designated IN WRITING
  written_designation_record:
  integrity_check: decrypt-plus-checksum-manifest
  documents_opened: 0        # any value other than 0 is a protocol breach
drill_copy_destruction:
  resource_tag:
  provider_resource_listing:  # path to the provider's post-drill listing
  resources_remaining:        # must be 0
  volume_snapshots_deleted:   # explicitly named; a filesystem wipe does not reach these
  provider_side_backups_deleted:
verification_dispatch:
  mechanism: RECORD-VERIFICATION-RESULT   # Section 97.2
  named_executor:
  result:
github_unavailable_variant: false          # exercised at least annually (Section 45.2)
YAMLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/checks/drill-clock.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 45.4 clock semantics: starts at provision-start, stops at
# dashboards-green, INCLUDING the Layer B restore, target under 4 hours.
set -euo pipefail
R="${1:?usage: drill-clock.sh <drill-record.yaml>}"
[ -f "$R" ] || { echo "DRILL-CLOCK: FAIL (no $R)"; exit 1; }
g() { awk -F': *' -v k="$1" '$0 ~ "^ *"k":" {print $2; exit}' "$R" | tr -d '"'; }
lb=$(g layer_b_restored); el=$(g elapsed_minutes); tg=$(g target_minutes)
om=$(g omitted_steps)
fail=0
[ "$lb" = "true" ] || { echo "layer_b_restored is not true - a rebuild that leaves Layer B unrestored has not finished"; fail=1; }
case "$el" in ''|*[!0-9]*) echo "elapsed_minutes is not an integer"; fail=1 ;; esac
[ "$tg" = "240" ] || { echo "target_minutes is not 240"; fail=1; }
case "$om" in ''|'[]') ;; *) echo "omitted_steps is not empty - an omitted step is a test failure"; fail=1 ;; esac
if [ "$fail" -eq 0 ] && [ "$el" -ge "$tg" ]; then echo "elapsed ${el}m is not under the ${tg}m target"; fail=1; fi
if [ "$fail" -eq 0 ]; then echo "DRILL-CLOCK: PASS"; else echo "DRILL-CLOCK: FAIL"; exit 1; fi
SHDOC
chmod +x ops-vm/checks/drill-clock.sh

cat > ops-vm/checks/drill-offvm-legs-fired.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 51.5: the quarterly drill verifies both off-VM legs fire BY STOPPING
# THE VM, not merely by rebuilding it. Both legs must route to the messaging
# channel and to the Section 42.2 phone path.
set -euo pipefail
R="${1:?usage: drill-offvm-legs-fired.sh <drill-record.yaml>}"
[ -f "$R" ] || { echo "DRILL-OFFVM-LEGS: FAIL (no $R)"; exit 1; }
fail=0
for k in vm_stopped_at vm_restarted_at; do
  v=$(awk -F': *' -v k="$k" '$0 ~ "^ *"k":" {print $2; exit}' "$R" | tr -d '"')
  [ -n "$v" ] || { echo "$k is empty - the VM was not stopped, so the legs were not verified"; fail=1; }
done
for k in external_uptime_check_fired dead_mans_switch_fired routed_to_messaging_channel routed_to_phone_path; do
  v=$(awk -F': *' -v k="$k" '$0 ~ "^ *"k":" {print $2; exit}' "$R" | tr -d '"')
  [ "$v" = "true" ] || { echo "$k is not true"; fail=1; }
done
if [ "$fail" -eq 0 ]; then echo "DRILL-OFFVM-LEGS: PASS"; else echo "DRILL-OFFVM-LEGS: FAIL"; exit 1; fi
SHDOC
chmod +x ops-vm/checks/drill-offvm-legs-fired.sh

cat > ops-vm/checks/drill-zero-resources.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 45.4: the drill copy is destroyed ON EVIDENCE, never on attestation.
# The record carries the provider's post-drill resource listing for the drill tag
# showing zero resources, and names the explicit deletion of the drill host's
# volume snapshots and provider-side backups, which a filesystem wipe does not
# reach. A drill record filed without this evidence is Blocking drift.
set -euo pipefail
R="${1:?usage: drill-zero-resources.sh <drill-record.yaml>}"
[ -f "$R" ] || { echo "DRILL-ZERO-RESOURCES: FAIL (no $R)"; exit 1; }
g() { awk -F': *' -v k="$1" '$0 ~ "^ *"k":" {print $2; exit}' "$R" | tr -d '"'; }
fail=0
tag=$(g resource_tag);      [ -n "$tag" ] || { echo "resource_tag is empty"; fail=1; }
lst=$(g provider_resource_listing)
[ -n "$lst" ] || { echo "provider_resource_listing is empty - attestation is not evidence"; fail=1; }
[ -z "$lst" ] || [ -f "$lst" ] || { echo "provider_resource_listing does not exist: $lst"; fail=1; }
rem=$(g resources_remaining)
[ "$rem" = "0" ] || { echo "resources_remaining is '$rem', not 0"; fail=1; }
for k in volume_snapshots_deleted provider_side_backups_deleted; do
  v=$(g "$k"); [ -n "$v" ] || { echo "$k is empty - a filesystem wipe does not reach these"; fail=1; }
done
docs=$(g documents_opened)
[ "$docs" = "0" ] || { echo "documents_opened is '$docs', not 0 - the integrity check opens no document"; fail=1; }
if [ "$fail" -eq 0 ]; then echo "DRILL-ZERO-RESOURCES: PASS"; else echo "DRILL-ZERO-RESOURCES: FAIL (Blocking drift)"; exit 4; fi
SHDOC
chmod +x ops-vm/checks/drill-zero-resources.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > ops-vm/drill/drill.sh <<'SHDOC'
#!/usr/bin/env bash
# Quarterly control-plane rebuild drill (Sections 45.4, 51.2, 51.5).
# Order matters and is not an implementation choice:
#   1. stop the VM and verify the off-VM legs fire (Section 51.5)
#   2. rebuild from the manifest, executed as written (Section 45.4)
#   3. the Layer B restore is performed by a human, never by this script
#   4. verify the clock, the legs and the zero-resources evidence
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
REC="${1:?usage: drill.sh <drill-record.yaml>}"
require_file "$REC"
require_env DRILL_VM_STOP_CMD DRILL_VM_START_CMD

log "drill: stopping the operations VM - the legs are verified by stopping it, not by rebuilding it"
$DRILL_VM_STOP_CMD
log "drill: the VM is stopped; both off-VM legs must now fire off this host"
$DRILL_VM_START_CMD

log "drill: rebuilding from the manifest, executed as written"
ops-vm/rebuild-driver/rebuild.sh ops-vm/rebuild-driver/steps.yaml

ops-vm/checks/drill-offvm-legs-fired.sh "$REC"
ops-vm/checks/drill-clock.sh "$REC"
ops-vm/checks/drill-zero-resources.sh "$REC"
record_run rebuild-drill ok "record=$REC"
echo "DRILL: PASS"
SHDOC
chmod +x ops-vm/drill/drill.sh

cat > ops-vm/drill/L4-HANDOFF.md <<'MDDOC'
# Handoff: the drill record lands in `records/`

Section 45.4 requires each drill to write a drill record to `records/`. The
records repository is **lane L4's** in full under the FROZEN partition; lane L5
does not write it.

L5 produces the record **content** at `ops-vm/drill/drill-record.template.yaml`
and three checks that grade it:

| Check | What it enforces |
| --- | --- |
| `ops-vm/checks/drill-clock.sh` | Clock starts at provision-start, stops at dashboards-green, includes the Layer B restore, under 4 hours, no omitted step |
| `ops-vm/checks/drill-offvm-legs-fired.sh` | Both off-VM legs fired **while the VM was stopped**, routed to the messaging channel and the phone path |
| `ops-vm/checks/drill-zero-resources.sh` | Provider listing for the drill tag shows zero resources; volume snapshots and provider-side backups are explicitly named as deleted; no document was opened |

L4 owns the write path and the record schema. The confirmation lands through the
**RECORD-VERIFICATION-RESULT dispatch (Section 97.2)** with a named executor -
never as free text a person writes about their own actions. A drill record filed
without its zero-resources evidence is **Blocking drift** (Section 45.4), which
is why `drill-zero-resources.sh` exits 4 rather than 1.
MDDOC

git add ops-vm/drill ops-vm/checks/drill-clock.sh ops-vm/checks/drill-offvm-legs-fired.sh ops-vm/checks/drill-zero-resources.sh
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-17: quarterly rebuild drill, VM-stop verification and zero-resources evidence"
git push -u origin "lane/5/04-t17-rebuild-drill"
gh pr create --base integration --title "L5-04-17: quarterly rebuild drill" --body "Lane L5 phase 4 task L5-04-17. Paths: ops-vm/** only. Spec: 45.4, 45.2, 51.2, 51.5, 97.2, AT-035, invariant 3."
gh issue create \
  --title "HANDOFF L5-04-17 -> L4: drill record write path and schema" \
  --label "handoff,lane-5,lane-4,phase-4" \
  --body "$(cat ops-vm/drill/L4-HANDOFF.md)"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Every script parses | `for f in ops-vm/drill/drill.sh ops-vm/checks/drill-clock.sh ops-vm/checks/drill-offvm-legs-fired.sh ops-vm/checks/drill-zero-resources.sh; do bash -n "$f" \|\| exit 1; done; echo ALL-PARSE-OK` | `ALL-PARSE-OK` |
| 2 | The template is valid YAML | `python3 -c "import yaml;print(sorted(yaml.safe_load(open('ops-vm/drill/drill-record.template.yaml')))[0])"` | `clock` |
| 3 | The empty template fails every evidence check | SELF-VERIFY, the three template runs (output suppressed; only the codes are compared) | `rc=1` then `rc=1` then `rc=4` |
| 4 | A conforming record passes all three | SELF-VERIFY, the three `/tmp/t17/good.yaml` runs | `DRILL-CLOCK: PASS`, `DRILL-OFFVM-LEGS: PASS`, `DRILL-ZERO-RESOURCES: PASS` |
| 5 | A record with resources still standing is Blocking, not a warning | SELF-VERIFY, the `standing.yaml` run | `resources_remaining is '3', not 0` then `DRILL-ZERO-RESOURCES: FAIL (Blocking drift)` then `rc=4` |
| 6 | A rebuild that leaves Layer B unrestored fails the clock | SELF-VERIFY, the `nolayerb.yaml` run | `layer_b_restored is not true - a rebuild that leaves Layer B unrestored has not finished` then `DRILL-CLOCK: FAIL` then `rc=1` |
| 7 | The drill verifies the legs by stopping the VM | `grep -c 'DRILL_VM_STOP_CMD' ops-vm/drill/drill.sh` | `2` |
| 8 | The script never performs the Layer B restore | `grep -Eic '(cryptsetup|pg_restore|age --decrypt|open any document)' ops-vm/drill/drill.sh` | `0` |
| 9 | This task writes nothing under `records/` | `git diff --cached --name-only \| grep -c '^records/'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for f in ops-vm/drill/drill.sh ops-vm/checks/drill-clock.sh ops-vm/checks/drill-offvm-legs-fired.sh ops-vm/checks/drill-zero-resources.sh; do bash -n "$f" || exit 1; done; echo ALL-PARSE-OK
python3 -c "import yaml;print(sorted(yaml.safe_load(open('ops-vm/drill/drill-record.template.yaml')))[0])"
T=ops-vm/drill/drill-record.template.yaml
ops-vm/checks/drill-clock.sh "$T" >/dev/null; echo "rc=$?"
ops-vm/checks/drill-offvm-legs-fired.sh "$T" >/dev/null; echo "rc=$?"
ops-vm/checks/drill-zero-resources.sh "$T" >/dev/null; echo "rc=$?"
rm -rf /tmp/t17 && mkdir -p /tmp/t17 && : > /tmp/t17/listing.txt
sed -e 's|^  elapsed_minutes:.*|  elapsed_minutes: 200|' \
    -e 's|^  layer_b_restored:.*|  layer_b_restored: true|' \
    -e 's|^omitted_steps:.*|omitted_steps: []|' \
    -e 's|^  vm_stopped_at:.*|  vm_stopped_at: "2026-09-01T09:00:00Z"|' \
    -e 's|^  vm_restarted_at:.*|  vm_restarted_at: "2026-09-01T09:20:00Z"|' \
    -e 's|^  external_uptime_check_fired:.*|  external_uptime_check_fired: true|' \
    -e 's|^  dead_mans_switch_fired:.*|  dead_mans_switch_fired: true|' \
    -e 's|^  routed_to_messaging_channel:.*|  routed_to_messaging_channel: true|' \
    -e 's|^  routed_to_phone_path:.*|  routed_to_phone_path: true|' \
    -e 's|^  resource_tag:.*|  resource_tag: drill-2026Q3|' \
    -e 's|^  provider_resource_listing:.*|  provider_resource_listing: /tmp/t17/listing.txt|' \
    -e 's|^  resources_remaining:.*|  resources_remaining: 0|' \
    -e 's|^  volume_snapshots_deleted:.*|  volume_snapshots_deleted: snap-1,snap-2|' \
    -e 's|^  provider_side_backups_deleted:.*|  provider_side_backups_deleted: bkp-1|' \
    "$T" > /tmp/t17/good.yaml
ops-vm/checks/drill-clock.sh /tmp/t17/good.yaml
ops-vm/checks/drill-offvm-legs-fired.sh /tmp/t17/good.yaml
ops-vm/checks/drill-zero-resources.sh /tmp/t17/good.yaml
sed 's|^  resources_remaining: 0|  resources_remaining: 3|' /tmp/t17/good.yaml > /tmp/t17/standing.yaml
ops-vm/checks/drill-zero-resources.sh /tmp/t17/standing.yaml; echo "rc=$?"
sed 's|^  layer_b_restored: true|  layer_b_restored: false|' /tmp/t17/good.yaml > /tmp/t17/nolayerb.yaml
ops-vm/checks/drill-clock.sh /tmp/t17/nolayerb.yaml; echo "rc=$?"
grep -c 'DRILL_VM_STOP_CMD' ops-vm/drill/drill.sh
grep -Eic '(cryptsetup|pg_restore|age --decrypt|open any document)' ops-vm/drill/drill.sh
```

Expected output:

```
ALL-PARSE-OK
clock
rc=1
rc=1
rc=4
DRILL-CLOCK: PASS
DRILL-OFFVM-LEGS: PASS
DRILL-ZERO-RESOURCES: PASS
resources_remaining is '3', not 0
DRILL-ZERO-RESOURCES: FAIL (Blocking drift)
rc=4
layer_b_restored is not true - a rebuild that leaves Layer B unrestored has not finished
DRILL-CLOCK: FAIL
rc=1
2
0
```

### STOP rule

The executor **never performs the Layer B restore.** Section 45.4 is absolute: the Founder, or a named person the Founder designates **in writing**, performs it personally, and no machine identity and no other person touches the people-data store during a drill. If no written designation exists, **stop the drill at that step.** Open a blocker (§1.4) with the decision line: *"A rebuild drill reached the Layer B restore with no Founder-performed restore and no written designation; Section 45.4 forbids any other party performing it."*

The integrity check is **decrypt-plus-checksum-manifest, without opening any document.** If the checksum manifest does not verify, **do not open a document to see whether the data looks right.** Open a blocker with the decision line: *"The Layer B drill copy failed its checksum manifest; Section 45.4 forbids opening a document to diagnose it and L0 must decide the next step."*

If `ops-vm/checks/drill-zero-resources.sh` exits `4`: **do not file the drill record.** Section 45.4 makes a drill record filed without its zero-resources evidence **Blocking drift**, and states why — a complete second copy of the people layer left standing is the largest single exposure in the system's calendar. Delete the drill resources on evidence, re-run the check, and only then file. If the resources cannot be deleted, open a blocker with the decision line: *"A rebuild drill left resources standing under its drill tag and they cannot be deleted; Section 45.4 makes the record Blocking drift until the provider listing shows zero."*

If the drill did not **stop the VM**: it did not verify the legs. Section 51.5 says so in those words. Re-run the drill; do not record a rebuild-only exercise as a quarterly drill.

---

## L5-04-18 — Self-hosted runner estate: groups, placement rule, inventory entries

> **Note (§4.10):** this task survives unamended and wins REG-034.

**Size:** M · **Depends on:** L5-04-11 · **Slug:** `runner-estate`
**Spec:** 49.1 — *"The self-hosted CI runner estate is a named asset class in the inventory: each runner host carries a named owner, a fixed cost band and a declared patch cadence, and **no runner is ever located on the operations VM** — Section 45.2's statement that CI keeps running when the VM is lost depends on that placement"*; GitHub-hosted Actions minutes on private repositories are metered beyond the plan quota, so the self-hosted estate is what keeps CI inside the fixed-cost doctrine (D80). 39.5 runner posture — *"All self-hosted runners … live in an organisation runner group restricted to named private repositories, with public-repository access off"* (D80). 46.6 **CI execution estate outage** — loss of the estate is an **entry condition into degraded engineering mode**, declared and announced by the escalation role, and each runner host's site, power and network dependency is declared beside it. 45.2 (control-plane outage: CI keeps running). Invariant 83 (fixed cost).

**Boundary:** the runner **group definitions** (`infra/runners/groups/ci.yaml`, `infra/runners/groups/privileged.yaml`), the host roster (`infra/runners/hosts.list`) and the entry generator and estate validator (`assets/new_runner_entry.sh`, `assets/check_runner_estate.py`) are built by the lane's asset phase. **This task authors no group file, no roster line and no inventory entry by hand.** It creates the placement rule, the checks that enforce it from both sides, and the outage declaration; where an inventory entry is needed it is produced by **invoking the published generator**.

### Files created

| Path | Purpose |
| --- | --- |
| `infra/runners/placement-rule.yaml` | The Section 49.1 placement rule, stated once |
| `infra/runners/check-placement.sh` | Estate-side: no `ci_runner` entry sits on the operations VM |
| `infra/runners/estate-outage.yaml` | The 46.6 declaration: entry condition, declarer, per-host dependencies |
| `infra/runners/check-estate-dependencies.sh` | Every `ci_runner` entry declares site, power and network |
| `ops-vm/checks/no-runner-on-ops-vm.sh` | Host-side: no runner service is installed on this VM |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t18-runner-estate"
mkdir -p infra/runners ops-vm/checks
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > infra/runners/placement-rule.yaml <<'YAMLDOC'
# The runner placement rule (Section 49.1), stated once so no host has to
# remember it.
#
# "no runner is ever located on the operations VM - Section 45.2's statement
#  that CI keeps running when the VM is lost depends on that placement"
#
# This is not a preference about tidiness. Section 45.2's control-plane-outage
# row promises that products keep running, CI keeps running and deployment keeps
# running when the operations VM is lost. A runner on that VM converts a
# control-plane outage into a CI outage and makes the promise false.
rule:
  id: RUNNER-PLACEMENT-1
  statement: "No self-hosted runner is located on the operations VM."
  depends_on_spec: "49.1, 45.2"
  enforced_by:
    - "infra/runners/check-placement.sh (estate side: the inventory)"
    - "ops-vm/checks/no-runner-on-ops-vm.sh (host side: the VM itself)"
  inventory_field: on_operations_vm      # every ci_runner entry declares it
  required_value: false
posture:
  # Section 39.5 / D80. The group files themselves are authored by the lane's
  # asset phase; this rule names what they must say.
  organisation_runner_group_required: true
  restricted_to_named_private_repositories: true
  public_repository_access: false
YAMLDOC

cat > infra/runners/estate-outage.yaml <<'YAMLDOC'
# Section 46.6, CI execution estate outage.
# "loss of the CI execution estate is an entry condition into degraded
#  engineering mode (Section 46.1), declared and announced by the escalation
#  role on the same terms"
degraded_mode_entry:
  is_entry_condition: true
  declared_by: escalation-role
  announced_on: designated-messaging-channel
  triggers_rollback_readiness_verification: true   # the five-minute check of 46.1
per_host_declaration_required:
  # Section 46.6: the runner site, power and network dependency is declared
  # beside each host. The values live on each ci_runner inventory entry; this
  # file names the requirement, and check-estate-dependencies.sh enforces it.
  - site
  - power
  - network
YAMLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > infra/runners/check-placement.sh <<'SHDOC'
#!/usr/bin/env bash
# Estate side of RUNNER-PLACEMENT-1 (Section 49.1): no ci_runner inventory entry
# sits on the operations VM.
set -euo pipefail
DIR="${1:-assets/inventory}"
[ -d "$DIR" ] || { echo "RUNNER-PLACEMENT: FAIL-CLOSED (no inventory directory: $DIR)"; exit 1; }
found=0; bad=0
for f in "$DIR"/*.yaml; do
  [ -e "$f" ] || continue
  grep -q '^asset_class: ci_runner$' "$f" || continue
  found=$((found + 1))
  v=$(awk -F': *' '/^on_operations_vm:/{print $2; exit}' "$f" | tr -d '"')
  case "$v" in
    false) ;;
    true) echo "runner located on the operations VM: $f"; bad=1 ;;
    *) echo "no on_operations_vm declaration: $f"; bad=1 ;;
  esac
done
if [ "$bad" -eq 0 ]; then echo "RUNNER-PLACEMENT: PASS ($found ci_runner entries)"; else echo "RUNNER-PLACEMENT: FAIL"; exit 1; fi
SHDOC
chmod +x infra/runners/check-placement.sh

cat > infra/runners/check-estate-dependencies.sh <<'SHDOC'
#!/usr/bin/env bash
# Section 46.6: the runner site, power and network dependency is declared beside
# each host, so a CI execution estate outage has a cause on the record rather
# than a discovery during one.
set -euo pipefail
DIR="${1:-assets/inventory}"
[ -d "$DIR" ] || { echo "RUNNER-DEPENDENCIES: FAIL-CLOSED (no inventory directory: $DIR)"; exit 1; }
found=0; bad=0
for f in "$DIR"/*.yaml; do
  [ -e "$f" ] || continue
  grep -q '^asset_class: ci_runner$' "$f" || continue
  found=$((found + 1))
  for k in site power network patch_cadence owner cost_band; do
    grep -qE "^${k}: *[^ ]" "$f" || { echo "missing $k: $f"; bad=1; }
  done
done
if [ "$bad" -eq 0 ]; then echo "RUNNER-DEPENDENCIES: PASS ($found ci_runner entries)"; else echo "RUNNER-DEPENDENCIES: FAIL"; exit 1; fi
SHDOC
chmod +x infra/runners/check-estate-dependencies.sh

cat > ops-vm/checks/no-runner-on-ops-vm.sh <<'SHDOC'
#!/usr/bin/env bash
# Host side of RUNNER-PLACEMENT-1 (Section 49.1): this VM runs no CI runner.
# Section 45.2's "CI keeps running when the VM is lost" depends on it.
set -euo pipefail
bad=0
if systemctl list-units --type=service --all --no-legend 2>/dev/null \
   | grep -Eq 'actions\.runner|github-runner'; then
  echo "a GitHub Actions runner service is installed on the operations VM"; bad=1
fi
if [ -d /opt/actions-runner ] || [ -d /home/runner/actions-runner ]; then
  echo "a runner installation directory exists on the operations VM"; bad=1
fi
if [ "$bad" -eq 0 ]; then echo "NO-RUNNER-ON-OPS-VM: PASS"; else echo "NO-RUNNER-ON-OPS-VM: FAIL"; exit 1; fi
SHDOC
chmod +x ops-vm/checks/no-runner-on-ops-vm.sh
```

Inventory entries are produced by the published generator, never authored here. Run this only when the roster supplies real host values; if it does not, the STOP rule below fires instead:

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
# One invocation per rostered host. Arguments come from infra/runners/hosts.list
# and from the entry's owner; none of them is invented here.
# bash assets/new_runner_entry.sh <hostname> <owner> <site> <power> <network> <group> <cost_band> <expiry_date>
python3 assets/validate_assets.py | tail -1
infra/runners/check-placement.sh assets/inventory
infra/runners/check-estate-dependencies.sh assets/inventory
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git add infra/runners/placement-rule.yaml infra/runners/estate-outage.yaml infra/runners/check-placement.sh infra/runners/check-estate-dependencies.sh ops-vm/checks/no-runner-on-ops-vm.sh
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-18: runner placement rule, estate-outage declaration and both-side checks"
git push -u origin "lane/5/04-t18-runner-estate"
gh pr create --base integration --title "L5-04-18: self-hosted runner estate placement rule" --body "Lane L5 phase 4 task L5-04-18. Paths: infra/**, ops-vm/** only. Spec: 49.1, 39.5, 45.2, 46.6, D80, invariant 83."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Every script parses | `for f in infra/runners/check-placement.sh infra/runners/check-estate-dependencies.sh ops-vm/checks/no-runner-on-ops-vm.sh; do bash -n "$f" \|\| exit 1; done; echo ALL-PARSE-OK` | `ALL-PARSE-OK` |
| 2 | Both YAML files parse | `for f in infra/runners/placement-rule.yaml infra/runners/estate-outage.yaml; do python3 -c "import yaml,sys;yaml.safe_load(open(sys.argv[1]))" "$f" \|\| exit 1; done; echo YAML-OK` | `YAML-OK` |
| 3 | The placement rule names both enforcement sides | `grep -c 'check-placement.sh\|no-runner-on-ops-vm.sh' infra/runners/placement-rule.yaml` | `2` |
| 4 | A runner declared on the operations VM is rejected | SELF-VERIFY, the `on_operations_vm: true` run | `runner located on the operations VM: /tmp/t18/inv/ci-runner-bad.yaml` then `RUNNER-PLACEMENT: FAIL` then `rc=1` |
| 5 | A runner with no placement declaration is rejected | SELF-VERIFY, the `undeclared` run | `no on_operations_vm declaration: /tmp/t18/inv/ci-runner-bad.yaml` then `RUNNER-PLACEMENT: FAIL` then `rc=1` |
| 6 | A conforming runner entry passes both estate checks | SELF-VERIFY, the `ci-runner-good.yaml` runs | `RUNNER-PLACEMENT: PASS (1 ci_runner entries)` then `RUNNER-DEPENDENCIES: PASS (1 ci_runner entries)` |
| 7 | A runner missing its site, power or network dependency is rejected | SELF-VERIFY, the `nosite` run | `missing site: /tmp/t18/inv/ci-runner-good.yaml` then `RUNNER-DEPENDENCIES: FAIL` then `rc=1` |
| 8 | Estate loss is declared an entry condition into degraded engineering mode | `grep -c '^  is_entry_condition: true$' infra/runners/estate-outage.yaml` | `1` |
| 9 | This task authors no group file, roster line or inventory entry | `git diff --cached --name-only \| grep -Ec '^(assets/|infra/runners/groups/|infra/runners/hosts.list)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for f in infra/runners/check-placement.sh infra/runners/check-estate-dependencies.sh ops-vm/checks/no-runner-on-ops-vm.sh; do bash -n "$f" || exit 1; done; echo ALL-PARSE-OK
for f in infra/runners/placement-rule.yaml infra/runners/estate-outage.yaml; do python3 -c "import yaml,sys;yaml.safe_load(open(sys.argv[1]))" "$f" || exit 1; done; echo YAML-OK
grep -c 'check-placement.sh\|no-runner-on-ops-vm.sh' infra/runners/placement-rule.yaml
rm -rf /tmp/t18 && mkdir -p /tmp/t18/inv
cat > /tmp/t18/inv/ci-runner-good.yaml <<'EOF'
asset_id: ci-runner-good
asset_class: ci_runner
owner: fixture-person
expiry_date: "2099-01-01"
alert_days: 30
cost_band: fixed-band-a
spec_reference: "49.1"
hostname: runner-a
patch_cadence: 30
site: site-a
power: feed-a
network: uplink-a
runner_group: ci
on_operations_vm: false
EOF
infra/runners/check-placement.sh /tmp/t18/inv
infra/runners/check-estate-dependencies.sh /tmp/t18/inv
sed -e 's/^asset_id: ci-runner-good$/asset_id: ci-runner-bad/' -e 's/^on_operations_vm: false$/on_operations_vm: true/' /tmp/t18/inv/ci-runner-good.yaml > /tmp/t18/inv/ci-runner-bad.yaml
rm /tmp/t18/inv/ci-runner-good.yaml
infra/runners/check-placement.sh /tmp/t18/inv; echo "rc=$?"
sed -i '/^on_operations_vm: true$/d' /tmp/t18/inv/ci-runner-bad.yaml
infra/runners/check-placement.sh /tmp/t18/inv; echo "rc=$?"
rm /tmp/t18/inv/ci-runner-bad.yaml
cat > /tmp/t18/inv/ci-runner-good.yaml <<'EOF'
asset_id: ci-runner-good
asset_class: ci_runner
owner: fixture-person
expiry_date: "2099-01-01"
alert_days: 30
cost_band: fixed-band-a
spec_reference: "49.1"
hostname: runner-a
patch_cadence: 30
power: feed-a
network: uplink-a
runner_group: ci
on_operations_vm: false
EOF
infra/runners/check-estate-dependencies.sh /tmp/t18/inv; echo "rc=$?"
grep -c '^  is_entry_condition: true$' infra/runners/estate-outage.yaml
```

Expected output:

```
ALL-PARSE-OK
YAML-OK
2
RUNNER-PLACEMENT: PASS (1 ci_runner entries)
RUNNER-DEPENDENCIES: PASS (1 ci_runner entries)
runner located on the operations VM: /tmp/t18/inv/ci-runner-bad.yaml
RUNNER-PLACEMENT: FAIL
rc=1
no on_operations_vm declaration: /tmp/t18/inv/ci-runner-bad.yaml
RUNNER-PLACEMENT: FAIL
rc=1
missing site: /tmp/t18/inv/ci-runner-good.yaml
RUNNER-DEPENDENCIES: FAIL
rc=1
1
```

### STOP rule

If `infra/runners/hosts.list` is empty, or a host's owner, site, power, network or cost band is not supplied: **do not invent one and do not run the entry generator with placeholder values.** The roster is operational data with a real person and a real site on it; a fabricated owner in the inventory produces a real alert routed at a person who does not hold the asset. Open a blocker (§1.4) with the decision line: *"The self-hosted runner roster carries no host values; Section 49.1 requires a named owner, a fixed cost band and a declared patch cadence per runner host, and L0 must supply them."*

If any `ci_runner` entry declares `on_operations_vm: true`, or `ops-vm/checks/no-runner-on-ops-vm.sh` finds a runner service on this host: **do not proceed and do not simply flip the field.** Section 49.1 states plainly that Section 45.2's *"CI keeps running when the VM is lost"* depends on that placement, so a runner on this VM makes a P0 promise false and the removal is a change with an owner. Open a blocker with the decision line: *"A self-hosted runner is located on the operations VM; Section 49.1 forbids that placement and Section 45.2's control-plane-outage promise depends on its removal."*

If the organisation runner group is not restricted to named private repositories, or public-repository access is on: **do not change the group.** `infra/runners/groups/**` is authored by the lane's asset phase, and D80's posture is a stated rule of the estate. Open a blocker with the decision line: *"The organisation runner group is not restricted to named private repositories with public access off; D80 and Section 39.5 require that posture and the group file is not this task's to edit."*

---

## L5-04-19 — D87 privileged/build pool separation and its three Blocking drift checks

> **Note (§4.10):** this task survives unamended and wins REG-034.

**Size:** L · **Depends on:** L5-04-18 · **Slug:** `d87-separation`
**Spec:** 39.5 **Privileged-workflow isolation (Priority: P0)** and **D87** — the runner-group rule closes the fork attack, which is not the attack this estate has: the machine account holds Write, a branch push executes CI, and a long-lived runner carries whatever that job left behind into the next privileged job; *"Persistence, not provenance, is the exposure."* The **privileged workflows are a closed set** — `deploy-production.yml`, `migrate.yml`, the rollback workflow and the per-product production-restore workflow. **The default is a hosted runner**, destroyed after every job. **The declared exception** is a self-hosted runner registered `--ephemeral` — a fresh container or virtual machine per job, with no writable shared volume — in a runner group labelled `privileged` that **never accepts a branch-push-triggered job**, recorded per product in the contract with its reason, and *"it is the only sanctioned self-hosted path for a privileged workflow."* **The separation is asserted in the workflow, not only in configuration**: each privileged workflow fails closed unless the runner it resolved to carries the `privileged` label or is hosted. **Reconciliation carries three Blocking rows** (Section 53.1): a self-hosted runner in the `privileged` group registered non-ephemerally; a privileged workflow resolving to a shared-pool label; and a branch-push-triggered workflow admitted to the `privileged` group. Also 40.3 (a branch push executes CI), 49.1, invariant 87.

**Boundary, stated plainly:** the three rows are **reconciliation** rows, and `reconciler/**` is lane **L3's**; the privileged workflows themselves are lane **L2's** (`.github/workflows/**`). This task builds the three checks as **standalone executables under an owned path**, with fixture-proven behaviour, and hands them to L3 to wire as reconciliation rows and to L2 for the in-workflow assertion. It edits neither lane's tree (PARTITION rules 1 and 4).

### Files created

| Path | Purpose |
| --- | --- |
| `infra/runners/d87/separation.yaml` | The closed privileged-workflow set, the default, and the one declared exception |
| `infra/runners/d87/check-ephemeral-registration.sh` | Blocking row 1 |
| `infra/runners/d87/check-privileged-workflow-tier.sh` | Blocking row 2 |
| `infra/runners/d87/check-no-branch-push-in-privileged.sh` | Blocking row 3 |
| `infra/runners/d87/run-all-checks.sh` | Runs all three; exits 4 on any Blocking finding |
| `infra/runners/d87/L3-HANDOFF.md` | The reconciliation-row and in-workflow-assertion handoff |

### Commands

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b "lane/5/04-t19-d87-separation"
mkdir -p infra/runners/d87
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > infra/runners/d87/separation.yaml <<'YAMLDOC'
# D87 privileged-workflow isolation (Section 39.5, Priority P0).
# The exposure is persistence, not provenance: the background machine account
# holds Write, a branch push executes CI (Section 40.3), and a long-lived runner
# carries whatever that job left behind into the next privileged job.
privileged_workflows:          # a CLOSED set; adding to it is a decision, not an edit
  - deploy-production.yml
  - migrate.yml
  - rollback
  - production-restore
default_runner_tier: hosted    # destroyed after every job
declared_exception:
  when: "a product's production plane requires a fixed egress address or a private network path a hosted runner cannot reach"
  runner_registration: ephemeral
  writable_shared_volume: false
  runner_group: privileged
  accepts_branch_push_jobs: false
  recorded_per_product_in_contract_with_reason: true
  only_sanctioned_self_hosted_path: true
in_workflow_assertion:
  # "The separation is asserted in the workflow, not only in configuration."
  statement: "Each privileged workflow fails closed unless the runner it resolved to carries the privileged label or is hosted."
  owned_by_lane: L2
blocking_drift_rows:           # Section 53.1; owned by lane L3's reconciler
  - id: D87-ROW-1
    statement: "A self-hosted runner in the privileged group registered non-ephemerally."
    check: "infra/runners/d87/check-ephemeral-registration.sh"
    note: "Under Q9=B, this fires BLOCKING on any `privileged`-group runner at all."
  - id: D87-ROW-2
    statement: "A privileged workflow resolving to a shared-pool label."
    check: "infra/runners/d87/check-privileged-workflow-tier.sh"
  - id: D87-ROW-3
    statement: "A branch-push-triggered workflow admitted to the privileged group."
    check: "infra/runners/d87/check-no-branch-push-in-privileged.sh"
YAMLDOC
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > infra/runners/d87/check-ephemeral-registration.sh <<'SHDOC'
#!/usr/bin/env bash
# D87 Blocking row 1: a self-hosted runner in the privileged group registered
# non-ephemerally. Input is a runner listing in the form
#   <name>\t<group>\t<ephemeral true|false>\t<writable_shared_volume true|false>
# produced read-only from the platform; this check never registers a runner.
set -euo pipefail
L="${1:?usage: check-ephemeral-registration.sh <runner-listing.tsv>}"
[ -f "$L" ] || { echo "D87-ROW-1: FAIL-CLOSED (no runner listing: $L)"; exit 4; }
bad=0
while IFS=$'\t' read -r name group eph vol; do
  [ -n "${name:-}" ] || continue
  [ "$group" = "privileged" ] || continue
  [ "$eph" = "true" ] || { echo "non-ephemeral runner in the privileged group: $name"; bad=1; }
  [ "$vol" = "false" ] || { echo "writable shared volume on a privileged runner: $name"; bad=1; }
done < "$L"
if [ "$bad" -eq 0 ]; then echo "D87-ROW-1: PASS"; else echo "D87-ROW-1: BLOCKING"; exit 4; fi
SHDOC
chmod +x infra/runners/d87/check-ephemeral-registration.sh

cat > infra/runners/d87/check-privileged-workflow-tier.sh <<'SHDOC'
#!/usr/bin/env bash
# D87 Blocking row 2: a privileged workflow resolving to a shared-pool label.
# Input is a resolution listing in the form
#   <workflow-file>\t<resolved runs-on label>
# The closed privileged set comes from separation.yaml; it is never widened here.
set -euo pipefail
L="${1:?usage: check-privileged-workflow-tier.sh <resolution.tsv>}"
S="${2:-infra/runners/d87/separation.yaml}"
[ -f "$L" ] || { echo "D87-ROW-2: FAIL-CLOSED (no resolution listing: $L)"; exit 4; }
[ -f "$S" ] || { echo "D87-ROW-2: FAIL-CLOSED (no separation.yaml)"; exit 4; }
priv=$(awk '/^privileged_workflows:/{f=1;next} /^[a-z_]+:/{f=0} f && /^ *- /{gsub(/^ *- /,"");print}' "$S")
bad=0
while IFS=$'\t' read -r wf label; do
  [ -n "${wf:-}" ] || continue
  echo "$priv" | grep -qxF "$wf" || continue
  case "$label" in
    ubuntu-*|windows-*|macos-*|privileged) ;;
    *) echo "privileged workflow $wf resolved to shared-pool label: $label"; bad=1 ;;
  esac
done < "$L"
if [ "$bad" -eq 0 ]; then echo "D87-ROW-2: PASS"; else echo "D87-ROW-2: BLOCKING"; exit 4; fi
SHDOC
chmod +x infra/runners/d87/check-privileged-workflow-tier.sh

cat > infra/runners/d87/check-no-branch-push-in-privileged.sh <<'SHDOC'
#!/usr/bin/env bash
# D87 Blocking row 3: a branch-push-triggered workflow admitted to the privileged
# group. Input is an admission listing in the form
#   <workflow-file>\t<trigger>\t<runner-group>
set -euo pipefail
L="${1:?usage: check-no-branch-push-in-privileged.sh <admissions.tsv>}"
[ -f "$L" ] || { echo "D87-ROW-3: FAIL-CLOSED (no admission listing: $L)"; exit 4; }
bad=0
while IFS=$'\t' read -r wf trig group; do
  [ -n "${wf:-}" ] || continue
  [ "$group" = "privileged" ] || continue
  [ "$trig" != "push" ] || { echo "branch-push-triggered workflow admitted to the privileged group: $wf"; bad=1; }
done < "$L"
if [ "$bad" -eq 0 ]; then echo "D87-ROW-3: PASS"; else echo "D87-ROW-3: BLOCKING"; exit 4; fi
SHDOC
chmod +x infra/runners/d87/check-no-branch-push-in-privileged.sh

cat > infra/runners/d87/run-all-checks.sh <<'SHDOC'
#!/usr/bin/env bash
# All three D87 Blocking rows in one call. Exits 4 if any row is Blocking, so a
# caller cannot mistake a Blocking finding for an ordinary failure.
set -euo pipefail
RUN="${1:?usage: run-all-checks.sh <runner-listing.tsv> <resolution.tsv> <admissions.tsv>}"
RES="${2:?}"
ADM="${3:?}"
rc=0
infra/runners/d87/check-ephemeral-registration.sh "$RUN" || rc=4
infra/runners/d87/check-privileged-workflow-tier.sh "$RES" || rc=4
infra/runners/d87/check-no-branch-push-in-privileged.sh "$ADM" || rc=4
if [ "$rc" -eq 0 ]; then echo "D87: PASS (3 rows)"; else echo "D87: BLOCKING"; fi
exit "$rc"
SHDOC
chmod +x infra/runners/d87/run-all-checks.sh
```

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
cat > infra/runners/d87/L3-HANDOFF.md <<'MDDOC'
# Handoff: the three D87 Blocking reconciliation rows

Section 39.5 states that *"Reconciliation carries three Blocking rows for this
posture (Section 53.1)."* The reconciler is **lane L3's** (`reconciler/**`), and
the privileged workflows are **lane L2's** (`.github/workflows/**`). Lane L5
owns neither and edits neither (PARTITION rules 1 and 4).

L5 has built the three checks as standalone executables, each proven against a
fixture, each exiting **4** on a Blocking finding:

| Row | Statement | Executable |
| --- | --- | --- |
| D87-ROW-1 | A self-hosted runner in the `privileged` group registered non-ephemerally | `infra/runners/d87/check-ephemeral-registration.sh` |
| D87-ROW-2 | A privileged workflow resolving to a shared-pool label | `infra/runners/d87/check-privileged-workflow-tier.sh` |
| D87-ROW-3 | A branch-push-triggered workflow admitted to the `privileged` group | `infra/runners/d87/check-no-branch-push-in-privileged.sh` |

Each takes one tab-separated listing produced read-only from the platform; the
input shapes are documented in the head comment of each script.

**For L3:** wire the three as Blocking reconciliation rows in Section 53.1's
declared-versus-actual table. The closed privileged-workflow set lives in
`infra/runners/d87/separation.yaml`; read it, do not restate it.

**For L2:** Section 39.5 additionally requires the separation to be *"asserted in
the workflow, not only in configuration"* - each privileged workflow fails closed
unless the runner it resolved to carries the `privileged` label or is hosted.
That assertion belongs inside the workflow files and is not built here.
MDDOC

git add infra/runners/d87
git diff --cached --name-only | grep -Ev '^(ops-vm|infra|assets|notify)/' && echo "FOREIGN PATH STAGED - STOP" || echo "PATHS OK"
git commit -m "L5-04-19: D87 privileged/build pool separation and its three Blocking drift checks"
git push -u origin "lane/5/04-t19-d87-separation"
gh pr create --base integration --title "L5-04-19: D87 privileged pool separation checks" --body "Lane L5 phase 4 task L5-04-19. Paths: infra/** only. Spec: 39.5, D87, 40.3, 53.1, 49.1, invariant 87."
gh issue create \
  --title "HANDOFF L5-04-19 -> L3 and L2: three D87 Blocking rows and the in-workflow assertion" \
  --label "handoff,lane-5,lane-3,lane-2,phase-4" \
  --body "$(cat infra/runners/d87/L3-HANDOFF.md)"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Every script parses | `for f in infra/runners/d87/*.sh; do bash -n "$f" \|\| exit 1; done; echo ALL-PARSE-OK` | `ALL-PARSE-OK` |
| 2 | `separation.yaml` parses and the privileged set is closed at four | `python3 -c "import yaml;print(len(yaml.safe_load(open('infra/runners/d87/separation.yaml'))['privileged_workflows']))"` | `4` |
| 3 | All three rows are declared with their executables | `python3 -c "import yaml;d=yaml.safe_load(open('infra/runners/d87/separation.yaml'));print(len(d['blocking_drift_rows']))"` | `3` |
| 4 | Row 1 detects a non-ephemeral privileged runner | SELF-VERIFY, the `runners-bad.tsv` run | `non-ephemeral runner in the privileged group: r-bad` then `D87-ROW-1: BLOCKING` then `rc=4` |
| 5 | Row 1 detects a writable shared volume | SELF-VERIFY, the `runners-vol.tsv` run | `writable shared volume on a privileged runner: r-vol` then `D87-ROW-1: BLOCKING` then `rc=4` |
| 6 | Row 2 detects a privileged workflow on a shared-pool label | SELF-VERIFY, the `resolution-bad.tsv` run | `privileged workflow deploy-production.yml resolved to shared-pool label: build-pool` then `D87-ROW-2: BLOCKING` then `rc=4` |
| 7 | Row 3 detects a branch-push job admitted to the privileged group | SELF-VERIFY, the `admissions-bad.tsv` run | `branch-push-triggered workflow admitted to the privileged group: ci.yml` then `D87-ROW-3: BLOCKING` then `rc=4` |
| 8 | All three pass on a conforming estate | SELF-VERIFY, the `run-all-checks.sh` clean run | `D87-ROW-1: PASS`, `D87-ROW-2: PASS`, `D87-ROW-3: PASS`, `D87: PASS (3 rows)` |
| 9 | A missing listing is Blocking, not silence | SELF-VERIFY, the absent-file run | `D87-ROW-1: FAIL-CLOSED (no runner listing: /tmp/t19/absent.tsv)` then `rc=4` |
| 10 | This task edits no foreign lane's tree | `git diff --cached --name-only \| grep -Ec '^(reconciler/|\.github/|templates/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
for f in infra/runners/d87/*.sh; do bash -n "$f" || exit 1; done; echo ALL-PARSE-OK
python3 -c "import yaml;print(len(yaml.safe_load(open('infra/runners/d87/separation.yaml'))['privileged_workflows']))"
python3 -c "import yaml;d=yaml.safe_load(open('infra/runners/d87/separation.yaml'));print(len(d['blocking_drift_rows']))"
rm -rf /tmp/t19 && mkdir -p /tmp/t19
printf 'r-ok\tprivileged\ttrue\tfalse\n'  > /tmp/t19/runners-ok.tsv
printf 'r-bad\tprivileged\tfalse\tfalse\n' > /tmp/t19/runners-bad.tsv
printf 'r-vol\tprivileged\ttrue\ttrue\n'   > /tmp/t19/runners-vol.tsv
printf 'deploy-production.yml\tprivileged\n' > /tmp/t19/resolution-ok.tsv
printf 'deploy-production.yml\tbuild-pool\n' > /tmp/t19/resolution-bad.tsv
printf 'deploy-production.yml\tworkflow_dispatch\tprivileged\n' > /tmp/t19/admissions-ok.tsv
printf 'ci.yml\tpush\tprivileged\n'                             > /tmp/t19/admissions-bad.tsv
infra/runners/d87/check-ephemeral-registration.sh /tmp/t19/runners-bad.tsv; echo "rc=$?"
infra/runners/d87/check-ephemeral-registration.sh /tmp/t19/runners-vol.tsv; echo "rc=$?"
infra/runners/d87/check-privileged-workflow-tier.sh /tmp/t19/resolution-bad.tsv; echo "rc=$?"
infra/runners/d87/check-no-branch-push-in-privileged.sh /tmp/t19/admissions-bad.tsv; echo "rc=$?"
infra/runners/d87/run-all-checks.sh /tmp/t19/runners-ok.tsv /tmp/t19/resolution-ok.tsv /tmp/t19/admissions-ok.tsv; echo "rc=$?"
infra/runners/d87/check-ephemeral-registration.sh /tmp/t19/absent.tsv; echo "rc=$?"
```

Expected output:

```
ALL-PARSE-OK
4
3
non-ephemeral runner in the privileged group: r-bad
D87-ROW-1: BLOCKING
rc=4
writable shared volume on a privileged runner: r-vol
D87-ROW-1: BLOCKING
rc=4
privileged workflow deploy-production.yml resolved to shared-pool label: build-pool
D87-ROW-2: BLOCKING
rc=4
branch-push-triggered workflow admitted to the privileged group: ci.yml
D87-ROW-3: BLOCKING
rc=4
D87-ROW-1: PASS
D87-ROW-2: PASS
D87-ROW-3: PASS
D87: PASS (3 rows)
rc=0
D87-ROW-1: FAIL-CLOSED (no runner listing: /tmp/t19/absent.tsv)
rc=4
```

### STOP rule

If any of the three checks reports `BLOCKING` against the real estate: **do not fix it from this lane.** Registering a runner, changing a runner group, editing a privileged workflow's `runs-on`, or changing which triggers a group admits are all platform-configuration changes owned by L2 and L3 and by the runner-group files of the lane's asset phase. Open a blocker (§1.4) with the decision line naming the row that fired: *"D87-ROW-\<n\> is Blocking on the live estate; Section 39.5 makes this posture P0 and the remediation belongs to the lane owning the runner group and the workflow, not to the operations-VM phase."*

If a request arrives to add a workflow to `privileged_workflows`: **refuse.** Section 39.5 calls it a **closed set** — `deploy-production.yml`, `migrate.yml`, the rollback workflow and the per-product production-restore workflow. Open a blocker with the decision line: *"A workflow outside Section 39.5's closed privileged set was proposed for the privileged group; widening that set is an L0 decision, not a configuration edit."*

If a product needs the self-hosted exception: **do not register the runner and do not write the contract entry.** D87 permits exactly one sanctioned self-hosted path — `--ephemeral`, no writable shared volume, a `privileged` group that never accepts a branch-push job — **recorded per product in the contract with its reason**, and product contracts are lane L1's registries. Open a blocker with the decision line: *"A product requires D87's declared self-hosted exception for its privileged workflows; the per-product contract record and its reason are L1 and L0 surfaces, not this lane's."* …and REG-037 forecloses it for V1.

---

## 3. What this phase hands to other lanes, stated once

Nothing below is a gap in this file. Each is a path this phase does not own, or a subsystem PARTITION v1 has not assigned, recorded here so the next reader does not go looking for it under `ops-vm/`, `infra/`, `assets/` or `notify/`.

| Left undone here | Owner | Where this file records it |
| --- | --- | --- |
| `docs/control-plane-rebuild.md` — the first-class rebuild runbook of Section 45.4 | L0 | `L5-04-16`, `ops-vm/rebuild-driver/L0-HANDOFF.md` |
| The drill record in `records/`, its schema and its write path (Section 45.4) | L4 | `L5-04-17`, `ops-vm/drill/L4-HANDOFF.md` |
| The three D87 Blocking reconciliation rows (Sections 39.5, 53.1) | L3 | `L5-04-19`, `infra/runners/d87/L3-HANDOFF.md` |
| The in-workflow privileged-tier assertion, and the org-export workflow that calls `ops-vm/export/put.sh` | L2 | `L5-04-19`, `L5-04-13` |
| The reconciler program itself, and its published CLI contract | L3 | `L5-04-07` boundary note |
| The health-report generator and the `os-health.yaml` tolerances | L1 / L4 | `L5-04-08` boundary note |
| The asset entry schema, the field table, the validator and every inventory entry | L5, the lane's asset phase | `L5-04-11`, `L5-04-14`, `L5-04-18` boundary notes |
| The runner group files and the host roster (`infra/runners/groups/**`, `infra/runners/hosts.list`) | L5, the lane's asset phase | `L5-04-18` boundary note |
| The Layer B access model, three-state fields, self-view documents and the AT-090 / AT-097 / AT-098 access tests | L5, the lane's access-control phase | `L5-04-05` scope boundary |
| `tools.yaml` — the Section 62.1 tool register carrying each component's cadence | **Subsystem O, unassigned in PARTITION v1** | `L5-04-15` DECISION REQUIRED block and `ops-vm/patch/L0-HANDOFF.md` |
| The accepted-risk record and manual audit-log review cadence for the Team-plan export | **Subsystem O, unassigned in PARTITION v1** | `L5-04-13` DECISION REQUIRED block |
| The Section 92 rendering of the off-VM liveness legs on the Founder and operator surfaces | **Subsystem H, unassigned in PARTITION v1** | `L5-04-14` DECISION REQUIRED block |

Subsystems **G, H, J, O and P are unassigned in PARTITION v1**. This file states each dependency where it arises, routes it to L0, and claims none of them.

---

## 4. Phase completion

This phase is complete when all nineteen tasks — `L5-04-01` through `L5-04-19` — have merged to `integration` on the lane's merge-train slot (L1 → L4 → L2 → L3 → L5), and the following four lines print exactly as shown from `$CONTROL_PLANE_ROOT` on the provisioned host:

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
ops-vm/checks/versions-pinned.sh ops-vm/stack/versions.env
ops-vm/checks/rebuild-steps-complete.sh
ops-vm/checks/no-people-datasource-in-shared.sh
infra/deadman/check-routes-direct.sh infra/deadman/watchdog.yaml infra/deadman/uptime-checks.yaml
```

```
VERSIONS-PINNED: PASS
REBUILD-STEPS: PASS
NO-PEOPLE-DATASOURCE-SHARED: PASS
DEADMAN-ROUTES-DIRECT: PASS
```

Those four lines are the phase's own summary of what Section 99.2 asked subsystem M to be: pinned and replayable, complete in its rebuild manifest, carrying no Layer B reference in the shared instance, and watched by a leg that does not die with the host. Until the fourth line prints from the off-VM leg's own configuration, Section 46.6 says the estate is **undetected, not healthy** — and this phase is not finished on a heartbeat this VM emitted and nothing off it confirmed.
