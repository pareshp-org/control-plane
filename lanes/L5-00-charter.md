# L5 — ACCESS, INFRA AND OPS — LANE CHARTER

**File:** `Code/implementation/lanes/L5-00-charter.md`
**Lane:** L5 (Access, Infra & Ops)
**Branch prefix:** `lane/5/*`
**Subsystems:** K, L, M, Q, R (spec §99.2, lines 9184–9231)
**Merge-train position:** LAST (L1 → L4 → L2 → L3 → **L5**)
**Authority above this file:** `Code/implementation/PARTITION.md` (FROZEN, v1) and `Research/MultiProduct_MasterSpec_v4.0.md` (v4.0, 10,214 lines).
**This file contains:** the lane mandate, path ownership, subsystem mapping, spec coverage map, consumption and publication contracts, merge-train obligations, the lane Definition of Done, the mandatory task-authoring contract for every other `L5-*` file, and exactly one task (`L5-00-01`).

> This charter never overrides `PARTITION.md`. Where this file and `PARTITION.md` appear to disagree, `PARTITION.md` wins and the disagreement is a blocker issue, not a judgement call.

---

## 0. Prerequisites

All lane executors must have the following tools available in `PATH` before running any command in this charter or any `L5-*` task file.

- gh >= 2.0.0
- git >= 2.34.0
- python3 >= 3.9
- yq >= 4.0 (YAML processor) — required by L5-03 and L5-07  
  Install: `brew install yq` (macOS) / `snap install yq` (Linux) / `scoop install yq` (Windows)  
  Verify: `yq --version`

### 0.1 Environment variables

| Variable | Required / Optional | Purpose |
|---|---|---|
| `CONTROL_PLANE_ROOT` | required | Absolute path to the `control-plane` repository checkout |
| `REPO_ROOT` | required | Alias for `CONTROL_PLANE_ROOT` used in phase files; set alongside it |
| `SPEC` | required | Absolute path to `MultiProduct_MasterSpec_v4.0.md` (read-only) |
| `L5PY` | required | Python interpreter; set by `infra/tools/bootstrap_venv.sh` |
| `L5_ROUTING_CHANNEL` | optional | Routing channel for integration tests (default: `engineering-alerts`) |

---

## 1. Mandate

L5 builds **the enforcement substrate every other lane assumes**: who may do what (Subsystem L), what an AI runtime is permitted to be and to load (K), the host that runs every scheduled control-plane job (M), the calendar-failure inventory that nothing else watches (Q), and the one path by which a machine is allowed to interrupt a human (R).

L5 does not build registries (L1), workflows (L2), the reconciler or the provisioning CLI (L3), or the record stores (L4). L5 **declares** the state those lanes enforce, provision and reconcile, and publishes those declarations as machine-readable artifacts.

The governing sentence for the whole lane is spec §64.1 (lines 5433–5447):

> **Rule:** a configuration error must never grant excess authority. Where a value is missing or malformed, the resolution is denial, not a default that permits.

---

## 2. Owned paths — exclusive

Per `PARTITION.md` line 21, L5 owns exactly these five top-level trees in the `control-plane` repository. No other lane writes them; L5 writes nothing else.

| Owned path | Subsystem | Holds |
|---|---|---|
| `access/**` | L, K | Permission model, branch-protection profile, secret-tier declarations, Layer B separation config, fail-closed control register, AI runtime/extension/MCP allowlists, constitution source |
| `infra/**` | L, M | GitHub organisation settings, runner groups and privileged-workflow isolation, network/egress declarations, L5 validation tooling |
| `ops-vm/**` | M | Operations-VM composition, scheduled-job declarations, rebuild runbook and drill, post-patch smoke checklist, off-VM detection leg |
| `notify/**` | R | Push-event routing map, channel configuration values, phone-escalation path, messaging-outage fallback |
| `assets/**` | Q | Operational asset inventory (one file per asset), external-deadline entries, expiry-watch configuration |

### 2.1 Fixed internal layout

This layout is fixed **here**, in the charter, precisely so that no downstream L5 task has to choose a path. Task files place files only at these paths.

```
# layout per FD-047; layerb/ matches L5-01 through L5-05
access/
  model/                 # §11.2 permission model, person-class → Team → Write derivation
  branch-protection/     # §11.3 profile, required-check list, CODEOWNERS human-only rule
  secrets/               # §40.1 five tiers; one file per fifth-tier credential
  layerb/                # §90.3–90.6 instance separation, allowlist, access log, self-view keys
  fail-closed/           # §64.2 control classification register (one file per control)
  ai-runtime/
    runtimes/            # §35.2 approved runtimes (one file per runtime)
    extensions/          # §36.3 approved extensions (one file per component)
    mcp-servers/         # §36.3 approved MCP servers (one file per component)
    checks/              # §36.6 no-API-keys check, secret-stripping pre-flight
    constitution/        # §36.1 constitution source text + reference-presence checker
    benchmark/           # §35.5 model-regression benchmark process; §35.6 vendor checklist
  published/             # artifacts consumed by other lanes (§9 of this charter)
infra/
  github-org/            # §11.2 base Read, 2FA, Actions-approve-PR disabled
  runners/               # §39.5 runner groups, privileged-workflow labels, ephemeral rule
  network/               # §51.4 private path; §37.8/§49.1 egress allowlist declarations
  tools/                 # l5-validate.sh — the lane's own validation entrypoint
  published/
ops-vm/
  compose/               # §99.2 M — Grafana, DevLake, Prometheus, job runtime
  jobs/                  # one file per scheduled job (§99.2 M row, line 9224)
  rebuild/               # §45.4 under-4-hour rebuild runbook + quarterly drill record shape
  smoke/                 # §51.4 post-patch smoke checklist
  offvm/                 # §51.5 external uptime check + dead-man's-switch heartbeat
  published/
notify/
  routing/               # §92.11 closed push list → destination map (one file per event class)
  channels/              # §92.11 designated messaging channel as a configuration value
  escalation/            # §42.2 phone-escalation path; §47.5 channel membership rules
  published/
assets/
  inventory/             # one file per asset (§49.1)
  deadlines/             # one file per external-deadline entry (§49.2)
  watch/                 # alert lead-time configuration and sweep cadence
  published/
```

### 2.2 The no-shared-file rule beats the spec's illustrative filenames

`PARTITION.md` line 27 is absolute: *"No shared mutable file, ever… Directory-per-item only (one file per event, per record, per schema)."*

The spec shows illustrative aggregate files — `assets.yaml` (§39.1, line 3520) and `ai-toolchain.yaml` (§36.3, line 3183). L5 resolves this without contradicting either document:

* The **authored** form is directory-per-item: `assets/inventory/<asset-id>.yaml`, `access/ai-runtime/runtimes/<runtime-id>.yaml`.
* The **aggregate** form is a *generated, never hand-edited* published artifact: `assets/published/assets.yaml`, `access/published/ai-toolchain.yaml`.
* A hand-authored aggregate at any path in an owned tree is a Definition-of-Done failure (DoD-05).

### 2.3 Forbidden paths

L5 never writes, and a PR touching any of these fails the lane-guard check (`PARTITION.md` line 25):

`contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` (L0) · `schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**` (L1) · `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**` (L2) · `reconciler/**`, `tools/provision/**`, `validators/drift/**` (L3) · all of `control-plane-records`, `schemas/records/**`, `metrics/**`, `tools/records/**` (L4).

**Consequence that matters and is not optional:** L5 owns no path under `.github/workflows/**`. Every scheduled job, expiry sweep, notification dispatch and check that L5 *declares* is *executed* by an L2-owned workflow reading an L5 published artifact. L5 declares; L2 executes; L3 reconciles.

---

## 3. Subsystem mapping to spec §99.2

Source table: spec §99.2, lines 9184–9231. Columns "What must exist", "Cx" and "Depends on" are the spec's own.

| # | Subsystem | Spec "what must exist" (§99.2) | Cx | Depends on | L5 deliverable cluster | Owned path |
|---|---|---|---|---|---|---|
| **K** | AI runtime contract enforcement | Approved-runtime and approved-extension lists as configuration; API-key-free checks at onboarding and quarterly; secret-stripping pre-flight; constitution referenced from every context file; model-regression benchmark process | M | A | Runtime/extension/MCP allowlists, no-API-keys check, Repomix pre-flight, constitution source + reference check, benchmark + vendor-checklist process | `access/ai-runtime/**` |
| **L** | Access-control architecture | Org base Read plus Teams-derived Write; branch and environment protection as the enforcement boundary; five secret tiers; fail-closed classification; the Layer B split — a second Founder-only Grafana instance carrying the separately-credentialed people datasource (D75), three-state field, generated self-view documents | M–L | A, D | Permission model, branch-protection profile, secret tiers + fifth-tier envelopes, fail-closed register, Layer B instance separation, `allocation_state` derivation, self-view key registry | `access/**`, `infra/github-org/**` |
| **M** | Operations VM | DevLake, Grafana, reconciliation, health computation, Scorecard, Renovate, expiry checks, restore rotation, org export; disposable (rebuild under 4 hours from GitHub, tested quarterly); never in any product's runtime path; patched on the declared cadence of Section 62 | M | — | VM composition, job declarations, rebuild runbook + drill, patch cadence, post-patch smoke checklist, off-VM detection leg | `ops-vm/**`, `infra/network/**` |
| **Q** | Asset inventory and deadline watch | Certificates, domains, OAuth, signing, vendor contracts and announced vendor deprecations — each with owner, expiry and configurable-lead alert; owners in orphan detection | S–M | A | Asset entry schema-conforming records, external-deadline entries, expiry-watch config, asset-owner export for orphan detection | `assets/**` |
| **R** | Notification routing | Actions webhook to messaging channel; per-product alert channels; documented phone-escalation path; Founder and Team Lead out-of-hours channel; no paging apps for developers | S | — | Closed push-list routing map, channel config values, phone path, messaging-outage fallback | `notify/**` |

### 3.1 §99.2 named-tool rows in L5 scope

The §99.2 named-tools table (lines 9212–9231) attributes small tools to subsystems. L5 owns the K/M/Q/R halves only:

| Tool (spec §99.2) | Attributed | L5 scope | Owned path |
|---|---|---|---|
| AI-eval scheduled runner | K | **Whole row.** L5 declares the schedule, the pin-change trigger and the SIG-42 tolerance; L2 executes the workflow; L4 writes `records/eval/` | `access/ai-runtime/benchmark/` |
| Hermes instance configurations (three cage configuration files, D69) | J, K | **K half only** — the version-controlled configuration files and their pinned-SHA/approved-list conformance | `access/ai-runtime/runtimes/` |
| Local inference endpoint service | J, K | **K half only** — the `model.provider: custom` / no-vendor-key declaration and the pinned model checksum entry | `access/ai-runtime/runtimes/`, `assets/inventory/` |
| Restore-rotation scheduler | E, M | **M half only** — the job declaration and its freshness objective; the workflow is L2 | `ops-vm/jobs/` |
| Support email-ingest hook | N, R | **R half only** — the first-touch-breach push route (§92.11) | `notify/routing/` |
| Background-host egress override / Background-window stop unit | J | **Not L5.** Declared as owned controls on the asset entry only (§49.1, line 4344) | `assets/inventory/` (entry field, not implementation) |

### 3.2 Subsystems L5 does not claim

`PARTITION.md` assigns A, B (L1); E, F (L2); C, D (L3); I, N (L4); K, L, M, Q, R (L5). Subsystems **G, H, J, O, P are assigned to no lane in PARTITION v1.** L5 does not claim them, does not build them, and does not create paths for them. Any work that resolves into G, H, J, O or P is an L0 escalation (§14 of this charter), never an L5 task.

---

## 4. Spec coverage map — every section L5 implements, with line ranges

Every row is a section or subsection of `Research/MultiProduct_MasterSpec_v4.0.md` that L5 turns into a file. Line ranges are inclusive and were read directly.

### 4.1 Subsystem L — access-control architecture

| Spec ref | Lines | What L5 builds | Owned path |
|---|---|---|---|
| §11 preamble — single organisation, dynamic repo enumeration, access removal | 808–816 | Org-level declaration: one organisation, no hard-coded repo lists | `infra/github-org/` |
| §11.1 GitHub permission semantics — verified, not assumed | 817–838 | The verified capability matrix as machine-readable reference; the "Cross-Reviewers require Write" rule | `access/model/` |
| §11.2 The permission model | 839–859 | Base Read; mandatory org 2FA; hardware-key rule for Founder/Owners/`platform-admin`; person-class → Write matrix; one Team per product + two org-wide Teams | `access/model/`, `infra/github-org/` |
| §11.3 Branch protection configuration, per repository | 860–875 | The full protection profile: PR required, ≥1 approving review, Code Owner review, **approval of the most recent reviewable push**, dismiss-stale, required status checks incl. `control-plane/blocking-drift`, up-to-date branches, force-push/deletion block, apply-to-administrators, environment deployment branch/tag policy | `access/branch-protection/` |
| §11.4 Implementation dependencies — plan-tier facts | 876–887 | Declared plan-tier posture: Team plan; **no** dependence on environment required reviewers (D73); Write-via-Teams as the assumed configuration | `access/model/` |
| §9.1 Capability rules | 717–724 | Capability → access mapping input | `access/model/` |
| §40.1 Five secret tiers | 3644–3686 | Tier declarations; one file per fifth-tier credential carrying its rotation cadence, named rotator, runbook link, **behavioural envelope** (signed run record, run-count ceiling, expected source host, published per-run API-call counts) and published permission set; the records-repository/control-plane split (D89) and the append-only ruleset facts (D107) as declarations | `access/secrets/` |
| §40.2 Boundary rules | 3687–3694 | `security.production_db_access: ci-only` default; provider-SSO-federation rule; the monthly attestation shape run with the §49 sweep; OIDC reservation | `access/secrets/`, `infra/network/` |
| §40.3 The workstation trust boundary | 3695–3704 | Both boundary statements as fail-closed declarations; separate-OS-user / second-factor requirements for fifth-tier storage on the ops VM | `access/secrets/`, `infra/network/` |
| §64.1 Safe defaults | 5433–5447 | Safe-default declarations for people, products, repositories, tools/integrations, machine accounts, non-employees | `access/model/` |
| §64.2 Fail-closed versus fail-open | 5448–5468 | The control classification register — one file per control, every control classified; the register is the input to the "unclassified controls fail CI" gate | `access/fail-closed/` |
| §90.1 Two layers, not one | 7893–7940 | Layer A / Layer B category lists; the decision-record routing rule (people → Layer B store, all others → `records/decisions/`) | `access/layer-b/` |
| §90.2 The permission matrix | 7941–7974 | The matrix as machine-readable policy, including the absolute machine-identities row | `access/layer-b/` |
| §90.3 Datasource-level enforcement | 7975–7989 | Second Founder-only Grafana instance (D75); people datasource never registered in the shared instance; at-rest encryption; the **named accepted-risk record** for host-level admin access with its holder, compensating off-host file-access audit, and dated review; the Layer B access log | `access/layer-b/`, `ops-vm/compose/` |
| §90.4 The people-intelligence capability | 7990–7999 | `people-intelligence` as **not delegable** (D109); the exact comparison scope reconciliation must run: instance credential, authentication allowlist, host OS accounts, sudoers, SSH authorised keys, backup-store read list | `access/layer-b/` |
| §90.5 Team Lead minimum-necessary access | 8000–8028 | `allocation_state` three-state field, **derived never entered**, with the §83.2 workload-state → field projection table and the `availability`-is-not-this-field rule | `access/layer-b/` |
| §90.6 Own-data transparency | 8029–8057 | Self-view delivery rules; **per-person public-key registry** (public half only), annual re-key, immediate re-key on §43.4 report; contest-note path | `access/layer-b/` |
| §90.7 Founder override | 8058–8065 | Override record shape | `access/layer-b/` |
| §92.1 The surface inventory | 8191–8209 | Layer assignment per surface (rows 6 and 7 are Layer B); the B-M / B-S split (D110) | `access/layer-b/` |
| §43.3 Compromised person account | 3900–3927 | `access_status: suspended` semantics and the containment-before-investigation access actions L5 must make configurable | `access/model/` |
| §43.4 Compromised workstation | 3928–3931 | Trigger for immediate self-view re-key (§90.6) | `access/layer-b/` |
| §45.3 The organisation export — loss is not outage | 4064–4077 | Append-only write-only credential, object-locked versioned storage, key held outside GitHub with its own asset entry, named owner + read-access list — declared as access configuration | `access/secrets/`, `assets/inventory/` |
| §14.4 Incapacity and death plan | 1256–1267 | Escrow as the re-issue source for fifth-tier credentials and the Layer B / backup key custody | `access/secrets/` |
| §54 Exception Registry and Break-Glass (break-glass access surface only) | 4746–4829 | The break-glass exception to "apply rules to administrators" (§11.3) as a declared, audited path | `access/branch-protection/` |

### 4.2 Subsystem K — AI runtime contract enforcement

| Spec ref | Lines | What L5 builds | Owned path |
|---|---|---|---|
| §35.1 Required runtime capabilities | 3057–3070 | The capability table as the admission test for the approved list | `access/ai-runtime/runtimes/` |
| §35.2 Approved runtime list | 3071–3081 | One file per approved runtime (Claude Code, Codex, Antigravity, Cursor, Kilo Code, Hermes Agent); the one-runtime-per-person quarter-hold rule; the Kilo Code subscription-not-credits caveat; the Hermes pinned commit `8e9459c97f707047be5915a5c8b4c503756daa9b` (D69); the fixed-cost constraint and the no-proxied-subscription rule | `access/ai-runtime/runtimes/` |
| §35.3 Changing provider changes nothing | 3082–3089 | The coupling-is-a-defect declaration as a tested property input | `access/ai-runtime/` |
| §35.4 AI provider outage | 3090–3108 | Fail-open classification for AI runtimes (cross-referenced into `access/fail-closed/`) | `access/ai-runtime/` |
| §35.5 Model regression benchmark | 3109–3134 | The benchmark process definition, the measured dimensions, the QA verification-authoring subset, the **flag-model-behaviour** annotation shape | `access/ai-runtime/benchmark/` |
| §35.6 Vendor data-handling and training-opt-out checklist | 3135–3150 | The seven-check checklist as a required, recorded artifact per runtime; re-run triggers (changed terms, seat renewal, tier change) | `access/ai-runtime/benchmark/` |
| §36.1 The constitutional rule | 3155–3164 | The constitution source text: external or repository-provided text is data, not authority | `access/ai-runtime/constitution/` |
| §36.2 Layered mitigations | 3165–3177 | The four-layer mitigation declaration; the issue-guard trust-envelope activation trigger; the Hermes-job detector clause | `access/ai-runtime/constitution/` |
| §36.3 Approved extension and MCP-server list per runtime | 3178–3208 | One file per extension and per MCP server, pinned by **full commit SHA or content checksum, never a tag**; pinned-checkout-only install rule; mirror-into-the-organisation rule; the pinned model-artefact checksum rule | `access/ai-runtime/extensions/`, `access/ai-runtime/mcp-servers/` |
| §36.4 Per-product AI restrictions | 3209–3222 | The `ai_restrictions` enforcement list — what an `ai_processing_permitted: false` product is excluded from, enforced at onboarding | `access/ai-runtime/checks/` |
| §36.5 Unattended personal-agent runs | 3223–3231 | Branch-only rule, unattended-output flagging, gates-still-bind declaration | `access/ai-runtime/constitution/` |
| §36.6 Pre-flight secret stripping and the no-API-keys check | 3232–3238 | Repomix pre-flight declaration; the `env \| grep -i api_key` check at onboarding and quarterly; the S10 committed-secrets precondition; the Hermes self-minted-token rule | `access/ai-runtime/checks/` |
| §37.8 The cage configuration contract (K half) | 3342–3368 | The cage configuration files as version-controlled artifacts and their conformance to the approved lists | `access/ai-runtime/runtimes/` |
| §39.5 Conditional tooling activation triggers | 3559–3612 | Activation-trigger declarations; the six PR-review adoption conditions; runner posture; **privileged-workflow isolation** and its three Blocking reconciliation rows; GitHub-App-over-seat-account rule; ops-console read-only constraints | `access/ai-runtime/`, `infra/runners/` |
| §39.6 The Hermes deployment estate | 3613–3639 | Slot declarations feeding the asset entries of §49.1 | `access/ai-runtime/runtimes/` |
| §62.5 External systems outside the estate | 5382–5400 | Every named runtime carries an exit condition; removal changes nothing (D49) | `access/ai-runtime/runtimes/` |

### 4.3 Subsystem M — operations VM

| Spec ref | Lines | What L5 builds | Owned path |
|---|---|---|---|
| §51.2 Platform SLOs | 4447–4465 | The control-plane SLO table as declarations with measurement source and breach response, incl. reconciliation freshness (Red 48h / Level 5 at 72h), drift-detection hourly for security-class checks, DevLake ingest freshness, ops-VM liveness observed off-VM; error-budget linkage | `ops-vm/jobs/` |
| §51.3 Control plane versus data plane — the invariant | 4466–4486 | The quarterly dependency-review declaration; the "control plane is never in a product runtime path" constraint on every VM job | `ops-vm/` |
| §51.4 Control-plane patching | 4487–4499 | Declared patch cadence per stack component; expedited security path; elevated Layer B cadence; Layer B at-rest and backup controls; **remote access only over a private path with SSO**; the post-patch smoke checklist; the singleton snapshot → upgrade → verify → revert-on-fail change shape | `ops-vm/smoke/`, `infra/network/` |
| §51.5 The disposable operations VM | 4500–4505 | VM disposability declaration; **off-VM detection leg** (external per-product `/health` check + dead-man's-switch heartbeat) routed to the Actions-webhook channel and the §42.2 phone path, never through the VM; the no-background-layer-on-this-VM rule | `ops-vm/offvm/`, `ops-vm/compose/` |
| §45.4 Control-plane rebuild | 4078–4085 | The under-4-hour rebuild runbook and the quarterly drill that verifies the off-VM legs fire by **stopping** the VM | `ops-vm/rebuild/` |
| §46.6 Monitoring stack unavailable | 4182–4185 | The declared answer: the off-VM leg is the witness; a dead observer emits what a healthy estate emits | `ops-vm/offvm/` |
| §46.6 CI execution estate outage | 4186–4207 | Runner-estate outage as a declared degraded-mode entry condition; runner site/power/network dependency declared beside each host | `infra/runners/`, `assets/inventory/` |
| §62 Tool Register and Platform Exit (stack entries only) | 5287–5400 | Version, declared patch cadence and date-last-patched per control-plane stack component | `ops-vm/compose/` |
| §99.2 M row — the job set | 9224 | One declaration file per VM-hosted job: DevLake, Grafana, reconciliation, health computation, Scorecard, Renovate, expiry checks, restore rotation, org export | `ops-vm/jobs/` |

### 4.4 Subsystem Q — asset inventory and deadline watch

| Spec ref | Lines | What L5 builds | Owned path |
|---|---|---|---|
| §49.1 Expiry-tracked assets | 4338–4354 | One file per asset: certificates, domains, DNS, OAuth credentials, signing certificates, email/payment/third-party API credentials, vendor contracts, AI subscription seats, **each fifth-tier machine credential**, the two Hermes hosts with their owned controls and host-integrity baseline, the ops-console VPS, the self-hosted CI runner estate. Every entry: expiry date, named owner, alert threshold ≥30 days | `assets/inventory/` |
| §49.2 The vendor deadline watch | 4355–4369 | One file per external-deadline entry (API sunsets, app-store policy deadlines, OAuth/webhook changes, vendor contract changes) with named owner (default: affected product's Primary Owner), announced deadline and **configurable lead time, 30 days minimum**; the vendor-deprecation pattern-class feed (D37) | `assets/deadlines/`, `assets/watch/` |
| §39.1 Seats as operational assets | 3515–3538 | AI subscription seats as an asset class: renewal date, seat cost, assigned person; the three Hermes `tools.yaml`-linked entries and two host entries | `assets/inventory/` |
| §12.2 Person exit lifecycle — asset orphan row | 948–1012 (row at 1002) | The asset-owner export that makes "Operational asset with no owner" a detectable orphan | `assets/published/` |
| §22.2 / §22.6 Intake channels and customer contact lists as owned assets | 2205–2222, 2261–2270 | Asset entries for support intake channels and per-product customer contact lists, incl. the mailbox's retention class, backup arrangement and restore cadence | `assets/inventory/` |
| §45.3 Export encryption key as an asset | 4064–4077 | Key entry with named holder and annual rotation cadence | `assets/inventory/` |
| §46.4 DNS, domain and certificate failure | 4164–4178 | Named owner per certificate/domain; the "investigate why the 30-day alert produced no action" loop | `assets/watch/` |
| §48.4 The compliance-artifact register | 4321–4324 | The register patterned on the asset inventory — owner, date produced, purpose, refresh-by date | `assets/inventory/` |
| §14.4 Founder-account inventory and escrow custodian | 1256–1267 (inventory item at line 1261) | Founder-only accounts as inventory entries with continuity notes; the escrow custodian as a named asset; an unlisted founder-only account discovered later is a drift finding | `assets/inventory/` |

### 4.5 Subsystem R — notification routing

| Spec ref | Lines | What L5 builds | Owned path |
|---|---|---|---|
| §92.11 The notification contract | 8272–8283 | The **closed push list** as a routing map — one file per push-event class: Gate 1 submission, Gate 2 request and reroutes, verification block/unblock, Blocking-class drift, delegation and temporary-person expiry warnings, launch sign-off request, pending Founder decision, support first-touch breach. The taxonomy-membership rule ("an event absent from the taxonomy cannot page anyone"). The D79 coalescing rule: clock-free pending-decision prompts join the morning digest; immediate push is reserved for prompts carrying a clock (§43.1, §21.3) and the rest of the closed list. The channel as a **configuration value**, never a hard-coded destination. Agentless dispatch — no Hermes instance is ever the only pager | `notify/routing/`, `notify/channels/` |
| §47.5 Notification model | 4252–4259 | Channel monitored only by Founder and Team Lead; contact with anyone else is a direct phone call; **no developer is required to install an alerting application**; nobody is unresponsive out of hours; Acting-Team-Lead activation swaps channel membership and phone-path position | `notify/channels/`, `notify/escalation/` |
| §42.2 Detection honesty — the phone-escalation path | 3767–3787 | The documented phone-escalation path: numbers, order and fallback written down, not reconstructed at 03:00; the alert-to-acknowledgement measurement point | `notify/escalation/` |
| §46.5 Messaging channel outage | 4179–4181 | The declared fallback: when the channel is unavailable, the §42.2 phone path **is** the alert path | `notify/escalation/` |
| §51.5 Off-VM alert routing | 4500–4505 | External check and heartbeat route to the Actions-webhook channel and the phone path, never through the VM | `notify/routing/` |
| §22.7 Outbound incident communication | 2271–2280 | Customer-facing incident comms as a routed, owned path distinct from the internal push list | `notify/routing/` |
| §52 signal ownership (routing side) | 4510–4575 | Each routed signal names its owner from the §52 table; a signal with no owner and no defined response is not routed (invariant 49) | `notify/routing/` |

---

## 5. What L5 consumes from `contracts/**`

`contracts/**` is written by L0 in Phase 0 and **FROZEN** (`PARTITION.md` line 26). L5 codes against it and never edits it. A needed change is a **Contract Change Request** to L0, never an edit.

L5 consumes the following subject matter. Each row names the spec-defined key that must be resolvable from `contracts/**`; the probe column is the literal gate an L5 task runs before it starts.

| # | Consumed subject | Spec ref (lines) | Used by | Probe |
|---|---|---|---|---|
| C-01 | Capability identifiers, incl. `people-intelligence`, `platform-admin`, `production-approval`, `incident-response`, `reviewer-matrix-change` | §9.1 (717–724), §90.4 (7990–7999) | L (capability→access map) | `grep -rl "people-intelligence" contracts/` |
| C-02 | Person-record fields: `availability`, `access_status`, `end_date`, `scope` | §6.4 (446–454), §12.4 (1046–1077), §64.1 (5433–5447) | L (safe defaults, suspension) | `grep -rl "access_status" contracts/` |
| C-03 | `allocation_state` three-state field definition | §90.5 (8000–8028) | L (Layer B minimum-necessary) | `grep -rl "allocation_state" contracts/` |
| C-04 | Product-contract `ai_restrictions` block | §36.4 (3209–3222) | K (per-product AI exclusion) | `grep -rl "ai_processing_permitted" contracts/` |
| C-05 | Product-contract `ai_runtime_dependency` block | §38.1 (3373–3414) | K (AI-eval runner scope, SIG-42) | `grep -rl "ai_runtime_dependency" contracts/` |
| C-06 | Product-contract `infrastructure` block incl. `security.production_db_access` and `monthly_budget_band` | §40.2 (3687–3694), §50.1 (4374–4392) | L (boundary attestation), M | `grep -rl "production_db_access" contracts/` |
| C-07 | `support_model` and derived `detection_expectation` | §42.2 (3767–3787) | R (per-product alert channels, phone path) | `grep -rl "detection_expectation" contracts/` |
| C-08 | `classification.reliability_criticality` | §15.2 (1536–1544) | M (restore rotation), Q (alert lead) | `grep -rl "reliability_criticality" contracts/` |
| C-09 | Event-taxonomy identifiers | §97.3 (8927–8953) | R (**hard gate**: an event absent from the taxonomy cannot page anyone, §92.11) | `grep -rl "events/" contracts/` |
| C-10 | Record-store locations and the two-repository split | §40.1 (3644–3686), §97.2 (8843–8926) | L (secret tiers), M (job outputs) | `grep -rl "records/" contracts/` |
| C-11 | The `data:` classification block, used for the Layer B equivalent declaration | §51.1 (4422–4446) | L (Layer B classification, retention, `regulatory_notification_hours`) | `grep -rl "regulatory_notification_hours" contracts/` |
| C-12 | Drift class vocabulary (Green / Amber / Red / Blocking) and reconciliation levels 1–5 | §6.7 (474–482), §53.1–53.2 (4653–4699) | L, M, Q (every declaration that names a drift class) | `grep -rl "Blocking" contracts/` |

**Gate command — run before the first commit of any L5 task:**

**Commands**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
missing=0
for key in people-intelligence access_status allocation_state ai_processing_permitted \
           ai_runtime_dependency production_db_access detection_expectation \
           reliability_criticality regulatory_notification_hours; do
  if ! grep -rql "$key" contracts/ 2>/dev/null; then echo "CONTRACT-MISSING $key"; missing=1; fi
done
if [ "$missing" -eq 0 ]; then echo "L5 CONTRACT GATE PASS"; else echo "L5 CONTRACT GATE FAIL"; fi
```

**STOP rule for the contract gate:** if the output is `L5 CONTRACT GATE FAIL`, do not proceed, do not create the branch, do not invent the key. Open a blocker issue using the template in §11.5 with `Blocker type: Contract Change Request` and stop.

---

## 6. Cross-lane consumption rules

`PARTITION.md` line 28: *"A lane consumes another lane's output only through `contracts/**` or a published artifact — never by reaching into its source tree."*

L5 therefore:

* **Never** reads `registries/**`, `reconciler/**`, `tools/provision/**`, `.github/workflows/**`, `schemas/records/**` or any other lane's source at build time.
* Reads other lanes' outputs only through `contracts/**` (§5) or a published artifact at a stable publication path.
* Publishes its own outputs only at the publication paths in §7, and nowhere else.

---

## 7. What L5 publishes for Lane 2 and Lane 3

Every artifact below is **generated** by `infra/tools/l5-validate.sh --publish` from the directory-per-item sources, is validated before it is written, and is the *only* L5 surface another lane may read.

### 7.1 Publication contract

| Rule | Statement |
|---|---|
| P-1 | A consumer reads `*/published/**` only. Reading any other L5 path is a cross-lane violation. |
| P-2 | Publication paths are versioned in the filename (`.v1.`). A breaking change publishes `.v2.` beside `.v1.`; `.v1.` is never mutated in place, never deleted in the same cycle. |
| P-3 | Every published artifact is byte-reproducible from its sources. `l5-validate.sh --publish` followed by `git diff --exit-code */published` must be clean (DoD-06). |
| P-4 | A published artifact that no consumer reads is deleted, not kept. |
| P-5 | L5 announces a publication change by tagging `l5/publish/vN` on the merge commit into `integration`. |

### 7.2 Artifacts for **Lane 3** (Subsystem C reconciler, Subsystem D provisioning)

| Artifact | Source spec (lines) | Contents Lane 3 needs |
|---|---|---|
| `access/published/permission-model.v1.json` | §11.2 (839–859), §11.1 (817–838) | Org base permission Read; org-enforced 2FA; hardware-key requirement for Founder/Owners/`platform-admin`; person-class → Write matrix; one Team per product + the two org-wide Teams; the "Cross-Reviewers require Write" rule. **D provisions from it; C reconciles Team membership against it (SIG-03).** |
| `access/published/branch-protection-profile.v1.json` | §11.3 (860–875) | The complete protection profile including the required-status-check list, `control-plane/blocking-drift`, most-recent-push approval, CODEOWNERS-human-identities-only, apply-to-administrators, force-push/deletion block, and the environment deployment branch and tag policy. **D applies at repository creation; C detects drift.** |
| `access/published/safe-defaults.v1.json` | §64.1 (5433–5447) | Minimum-authority defaults for person, product, repository, tool/integration, machine account, non-employee. **D's template defaults.** |
| `access/published/capability-access-map.v1.json` | §9.1 (717–724), §90.4 (7990–7999) | Capability → surface/credential map; `people-intelligence` marked non-delegable (D109); the **exact comparison scope** C must run for Layer B: instance credential, authentication allowlist, host OS accounts, sudoers entries, SSH authorised keys, backup-store read list. A holder in neither list is Blocking drift. |
| `access/published/secret-tiers.v1.json` | §40.1 (3644–3686), §40.3 (3695–3704) | Five tiers; per fifth-tier credential: published permission set, rotation cadence, named rotator, runbook link, behavioural envelope (signed run record, run-count ceiling, expected source host, per-run API-call counts). **C's envelope-breach rows and the AT-110 bound set.** |
| `access/published/fail-closed-register.v1.json` | §64.2 (5448–5468) | Every control with its classification. **C fails closed on Blocking-class checks; unclassified controls fail CI.** Also read by L1's validator. |
| `infra/published/org-settings.v1.json` | §11.2 (839–859), §39.5 (3559–3612) | Base Read, 2FA required, "Allow GitHub Actions to create and approve pull requests" disabled. **D sets; C reconciles.** |
| `infra/published/runner-posture.v1.json` | §39.5 (3559–3612), §46.6 (4186–4207) | Organisation runner group restricted to named private repositories; the closed privileged-workflow set (`deploy-production.yml`, `migrate.yml`, rollback, per-product production-restore); `privileged` label rule; `--ephemeral` requirement. **Carries the three Blocking reconciliation rows C must implement.** |
| `assets/published/asset-owners.v1.json` | §49.1 (4338–4354), §12.2 row at 1002 | Asset id → named owner. **C's orphan detection: "Operational asset with no owner" (Medium).** |
| `assets/published/expiry-watch.v1.json` | §49.1–49.2 (4338–4369) | Every expiry date and its configurable lead time (≥30 days). **Feeds C's expiry revocation cadence and the delegation-expiry warning of §10.1 (line 787).** |

### 7.3 Artifacts for **Lane 2** (Subsystem E reusable workflows, Subsystem F evidence chain)

| Artifact | Source spec (lines) | Contents Lane 2 needs |
|---|---|---|
| `notify/published/routing.v1.json` | §92.11 (8272–8283), §47.5 (4252–4259), §42.2 (3767–3787), §46.5 (4179–4181) | The closed push list keyed by event-taxonomy id; the designated messaging channel as a configuration value; per-product alert channels; the D79 coalescing rule; the phone-path fallback. **The Actions webhook step in every workflow reads this and nothing else.** |
| `ops-vm/published/job-schedule.v1.json` | §99.2 M row (9224), §51.2 (4447–4465) | Every scheduled control-plane job, its cadence, its freshness objective and its breach response. **Tells L2 which jobs are `workflow_dispatch`/`schedule` workflows and which are VM-hosted.** |
| `ops-vm/published/offvm-detection.v1.json` | §51.5 (4500–4505), §46.6 (4182–4185) | The external per-product `/health` check targets and the dead-man's-switch heartbeat endpoint, with routing to the webhook channel and the phone path. |
| `access/published/secret-tiers.v1.json` | §40.1 (3644–3686) | Which tier a credential lives in, so a workflow never places a production credential below the production tier. Shared with Lane 3. |
| `infra/published/runner-posture.v1.json` | §39.5 (3559–3612) | `runs-on` labels, the hosted-runner default for privileged workflows, and the in-workflow fail-closed assertion contract. Shared with Lane 3. |
| `access/published/ai-toolchain.yaml` | §36.3 (3178–3208) | Pinned runtimes, extensions and MCP servers by full SHA or content checksum. **The supply-chain pin source for CI checks (§48.1).** |
| `access/published/ai-eval-schedule.v1.json` | §35.5 (3109–3134), §99.2 tools row (9226) | The AI-eval scheduled runner's cadence, its pin-change trigger and its SIG-42 tolerance. **L2 runs it; L4 writes `records/eval/`.** |

---

## 8. Merge-train position — last, and why

`PARTITION.md` line 35 fixes the order: **L1 → L4 → L2 → L3 → L5**, once per cycle. Line 41 states the reason: *"L5 (access/infra) is independent at build time, integrates last."*

### 8.1 Resolving the apparent circularity

`PARTITION.md` line 40 says *"L3 (reconciler) consumes L1 + L5 access model"* while L3 merges **before** L5. This is not a contradiction and L5 must not "fix" it:

* L3 consumes the access model **as a contract-frozen shape**, not as L5's implementation. The schema for `access/published/permission-model.v1.json` and its siblings lives in `contracts/**`, frozen in Phase 0. L3 codes and merges against that shape plus generated fixtures.
* L5 is *independent at build time*: it needs nothing from L2 or L3 to be written, only `contracts/**` (§5) and the L4-published event taxonomy (C-09).
* The runtime binding happens at publication (§7), not at merge.

### 8.2 What "last" obliges L5 to do, every cycle

| Obligation | Command |
|---|---|
| Rebase every open `lane/5/*` branch on `integration` **after** L3's merge lands, before opening the PR (`PARTITION.md` line 34) | `git fetch origin && git rebase origin/integration` |
| Re-run the full lane DoD (§12) against the post-L3 `integration` state, not against the state the branch was cut from | `bash infra/tools/l5-validate.sh --all` |
| Re-publish and confirm byte-reproducibility after the rebase | `bash infra/tools/l5-validate.sh --publish && git diff --exit-code -- '*/published'` |
| Never merge, rebase or touch another lane's branch (`PARTITION.md` line 36) | — |

### 8.3 Why last is the right position for this lane specifically

1. **Enforcement should arrive after the thing it enforces exists.** L5's acceptance criteria are statements about a populated organisation: Teams derived from registries (L1), workflows that carry required checks (L2), a reconciler that can hold a check at failure (L3). Evaluating them against a half-populated `integration` produces false passes — precisely the "gate that appears to be working and is not" failure the spec names in §11.1 (lines 817–838).
2. **L5 is the only lane whose defects are security defects.** Merging last means L5's DoD runs against the freshest possible integration state, so a permission or fail-closed regression introduced by any earlier lane in the same cycle is caught inside the cycle rather than after it.
3. **L5 changes organisation- and host-level state.** Landing base-permission, 2FA, runner-group or branch-protection declarations mid-cycle would destabilise every lane still merging behind it.
4. **The reconciler is the highest-privilege identity in the system** (§99.6 risk 6, lines 9276–9294). Its declared bounds — `access/published/secret-tiers.v1.json` — should land after the reconciler code they bound is in `integration`, so AT-110 can be executed rather than asserted.

---

## 9. Anchors register — real ids only

Every id below was located in the spec. No id is invented.

### 9.1 Acceptance tests L5 provides the configuration under test for (§100.6, lines 9421–9441)

| AT | Test | L5 artifact under test |
|---|---|---|
| AT-089 | Layer B is unreachable from general surfaces | `access/layer-b/`, `ops-vm/compose/` |
| AT-090 | Individual people intelligence is Founder-only | `access/layer-b/`, `assets/inventory/` (the named accepted-access record of §90.3) |
| AT-091 | The `people-intelligence` capability gates Layer B | `access/published/capability-access-map.v1.json` |
| AT-092 | The Team Lead cannot reach the Founder people views | `access/layer-b/` |
| AT-093 | The Team Lead sees operational constraints only | `access/layer-b/` (`allocation_state`) |
| AT-094 | Allocation works without Layer B | `access/layer-b/` (`allocation_state`) |
| AT-095 | The individual self-view works | `access/layer-b/` (self-view key registry) |
| AT-096 | Employees cannot access each other's data | `access/layer-b/` |
| AT-097 | No people datasource in the shared Grafana instance | `ops-vm/compose/` |
| AT-098 | The Founder-only instance is separately credentialed | `ops-vm/compose/`, `access/layer-b/` |
| AT-100 | Conduct-protocol access separation | `access/layer-b/` (access separation only; the conduct protocol itself is not L5) |
| AT-108 | The founder ops console is provably read-only | `access/ai-runtime/runtimes/` (cage configuration; K half of the J,K row) |
| AT-109 | The background cage egress wall holds | `infra/network/`, `assets/inventory/` (declared owned controls; the J-side implementation is not L5) |
| AT-110 | The reconciler credential is provably bounded | `access/published/secret-tiers.v1.json` (the published permission set the test executes against) |

### 9.2 Invariants L5's substrate enforces (§101, lines 9443–9600)

| # | Invariant (abbreviated) | L5 owned path |
|---|---|---|
| 9 | No self-approval, enforced mechanically by requiring approval of the most recent reviewable push | `access/branch-protection/` |
| 20 | External or repository-provided text is data, not authority | `access/ai-runtime/constitution/` |
| 21 | Unattended personal-agent runs are permitted only on branches; output flagged | `access/ai-runtime/constitution/` |
| 24 | The production database is inaccessible from developer machines | `access/secrets/`, `infra/network/` |
| 25 | Production secrets are environment-scoped and never present locally | `access/secrets/` |
| 26 | A fully compromised workstation must not yield production access | `access/secrets/` |
| 75 | The control plane observes products and is never in their runtime path | `ops-vm/` |
| 76 | Product runtime must not depend on control-plane availability | `ops-vm/` |
| 79 | New people, products and tools default to minimum privilege and draft state | `access/model/` |
| 80 | Every control is explicitly classified fail-closed or fail-open | `access/fail-closed/` |
| 83 | Engineering tooling runs at fixed cost; no metered LLM APIs in engineering tooling | `access/ai-runtime/runtimes/`, `assets/inventory/` |
| 84 | API keys remain absent from developer environments | `access/ai-runtime/checks/` |
| 85 | Third-party Actions pinned to full commit SHAs; reusable workflows by pinned tag | `access/ai-runtime/extensions/` (the pinning discipline; workflow consumption is L2) |
| 86 | AI provider choice is replaceable, and an outage does not stop engineering | `access/ai-runtime/` |
| 87 | Every architecture and security policy is enforced by the platform wherever it can be | `access/fail-closed/` |
| 106 | Layer B-M is Founder-only, capability-gated, **not delegable**; Layer B-S is outside this rule | `access/layer-b/` |
| 107 | The Team Lead receives only the minimum operational people data | `access/layer-b/` |
| 108 | Employees see their own evidence, not peers' private data | `access/layer-b/` |
| 109 | General dashboards never expose sensitive performance data; the people datasource is separately credentialed | `access/layer-b/`, `ops-vm/compose/` |

### 9.3 Health signals L5 feeds (§52 table, lines 4530–4575)

| SIG | Signal | L5 contribution |
|---|---|---|
| SIG-03 | Permission drift | `access/published/permission-model.v1.json`, `branch-protection-profile.v1.json` are the declared side of the comparison |
| SIG-05 | Orphan risk | `assets/published/asset-owners.v1.json` extends orphan detection to asset owners (§49.1) |
| SIG-21 | Control-plane SLO burn | `ops-vm/published/job-schedule.v1.json` carries the objectives of §51.2 |
| SIG-34 | Organisation export staleness | `ops-vm/jobs/` org-export declaration; `access/secrets/` export credential |
| SIG-35 | Cloud cost anomaly | `assets/inventory/` fixed cost bands for hosts, runners and seats |
| SIG-36 | Control-plane patch staleness | `ops-vm/compose/` declared patch cadence and date-last-patched |
| SIG-42 | AI-eval regression | `access/published/ai-eval-schedule.v1.json` carries the declared tolerance |
| SIG-46 | Audit-log review staleness | `access/layer-b/` compensating-control review cadence (§90.3), `access/secrets/` (§45.3) |

### 9.4 Decisions L5 implements (Appendix A, lines 10056–10213)

| D | Decision | Where implemented |
|---|---|---|
| D9 | `people-intelligence` gates Layer B; delegation mechanism removed by D109 | `access/layer-b/` |
| D14 | Layer B in a separately credentialed datasource; self-view as a generated per-person document | `access/layer-b/` |
| D16 | No per-person raw-activity drill-downs on general dashboards | `access/layer-b/` |
| D28 | Approved extension/MCP list per runtime; vendor data-terms checklist; `ai_restrictions`; unattended-agent rule | `access/ai-runtime/` |
| D37 | Vendor deprecation watch: announced sunsets enter the asset inventory as owned, alerting entries | `assets/deadlines/` |
| D40 | Declared patch cadence for the control-plane stack, elevated because Layer B raises its sensitivity | `ops-vm/compose/` |
| D49 | Every named third-party system carries an exit condition; its removal changes nothing | `access/ai-runtime/runtimes/`, `ops-vm/compose/` |
| D69 | Hermes Agent pinned at commit `8e9459c97f707047be5915a5c8b4c503756daa9b`; three committed instances as named assets | `access/ai-runtime/runtimes/`, `assets/inventory/` |
| D71 | The one-write-path rule: Hermes proposes; the platform disposes | `access/ai-runtime/constitution/` |
| D72 | Machine-drafted aids are wait-surface conveniences, never surfaces of record | `notify/routing/` |
| D73 | The workflow-identity gate is the production-approval mechanism of record; environment required reviewers are not depended on | `access/branch-protection/`, `access/model/` |
| D75 | Second, Founder-only Grafana instance; the people datasource is never registered in the shared instance | `access/layer-b/`, `ops-vm/compose/` |
| D76 | A records-writer machine credential in the fifth tier — **mechanism superseded by D89** | `access/secrets/` |
| D79 | Clock-free pending-decision prompts coalesce into the morning digest; routine asset-register additions maintained by the Team Lead; founder-only account entries stay Founder-owned | `notify/routing/`, `assets/inventory/` |
| D80 | Self-hosted CI runners are named fixed-cost assets, never on the operations VM, in a restricted organisation runner group; GitHub Apps preferred over seat accounts | `assets/inventory/`, `infra/runners/` |
| D89 | The record stores live in their own repository; **no bypass actor exists on the control-plane repository** | `access/secrets/` |
| D107 | Append-only enforced on the records repository: no-bypass ruleset, signed commits, per-run SHA anchor, object-locked export | `access/secrets/` |
| D109 | Layer B access is not delegable | `access/layer-b/` |
| D110 | Layer B names its two surfaces separately: B-M (management) and B-S (self-view) | `access/layer-b/` |

---

## 10. Lane-level Definition of Done

L5 is DONE for a cycle when every row below returns its PASS token against the current `integration` state, after the §8.2 rebase.

> **FD-060:** DoD proof commands redesigned per FD-060. l5-validate.sh --layout remains for layout checks only.
> All other validation uses the phase-file toolchain built in L5-01..L5-05.

| ID | Criterion | Provable by |
|---|---|---|
| DoD-01 | All five owned trees and the fixed layout of §2.1 exist | `bash infra/tools/l5-validate.sh --layout` → `L5 LAYOUT PASS` |
| DoD-02 | The branch touches no foreign path | command in §10.1 → `DOD-02 PASS` |
| DoD-03 | The contract gate passes | command in §5 → `L5 CONTRACT GATE PASS` |
| DoD-04 | Every §4 spec row has at least one file implementing it, and every file names its spec ref | `bash infra/tools/lane_tree_check.sh` → `L5-T01 SELF-VERIFY PASS` (FD-060: uses phase-file toolchain: lane_tree_check.sh) |
| DoD-05 | No hand-authored aggregate file exists in any owned tree | command in §10.1 → `DOD-05 PASS` |
| DoD-06 | Publication is byte-reproducible from sources | `"$L5PY" infra/tools/validate_handoff.py && git diff --exit-code -- '*/published'` → exit 0 (FD-060: uses phase-file toolchain: validate_handoff.py) |
| DoD-07 | Every published artifact validates against its `contracts/**` schema | `"$L5PY" -m pytest access/tests -q` → all passed (FD-060: uses phase-file toolchain: pytest) |
| DoD-08 | Every control in `access/fail-closed/` carries a classification of exactly `fail-closed` or `fail-open` (§64.2, lines 5448–5468) | `"$L5PY" -m pytest access/tests/test_access_model.py -q` → all passed (FD-060: uses phase-file toolchain: pytest) |
| DoD-09 | Every asset entry carries an expiry date, a named owner and an alert threshold ≥ 30 days (§49.1, line 4342) | `"$L5PY" -m pytest assets/tests/test_inventory.py -q` → all passed (FD-060: uses phase-file toolchain: pytest) |
| DoD-10 | Every push route in `notify/routing/` names an event-taxonomy id present in the L4-published taxonomy, and the route set is a subset of the §92.11 closed list | `"$L5PY" -m pytest notify/tests/test_route.py -q` → all passed (FD-060: uses phase-file toolchain: pytest) |
| DoD-11 | Every approved runtime, extension and MCP server is pinned by full commit SHA or content checksum — never a tag, branch or `latest` (§36.3, lines 3178–3208) | `"$L5PY" -m pytest access/tests/test_extension_pins.py -q` → all passed (FD-060: uses phase-file toolchain: pytest) |
| DoD-12 | Every fifth-tier credential entry carries rotation cadence, named rotator, runbook link, behavioural envelope and published permission set (§40.1, lines 3644–3686) | `"$L5PY" -m pytest access/tests/test_access_model.py -q` → all passed (FD-060: uses phase-file toolchain: pytest) |
| DoD-13 | No file in any owned tree grants a machine identity any people-related data category (§90.2 machine-identities row, lines 7941–7974) | `"$L5PY" -m pytest access/tests/test_machine_identity.py -q` → all passed (FD-060: uses phase-file toolchain: pytest) |
| DoD-14 | `people-intelligence` appears nowhere as delegable, and no assignment type grants it (D109, §90.4 lines 7990–7999) | `"$L5PY" -m pytest access/tests/test_pi_gate.py -q` → all passed (FD-060: uses phase-file toolchain: pytest) |
| DoD-15 | Every VM job declaration states that it is not in any product runtime path (§51.3, lines 4466–4486) | `"$L5PY" -m pytest ops-vm/tests/test_hardening.py -q` → all passed (FD-060: uses phase-file toolchain: pytest) |
| DoD-16 | The lane PR is open against `integration`, rebased after L3's merge, with a green lane-guard check | `gh pr view --json baseRefName,mergeable,statusCheckRollup` |

### 10.1 The two DoD commands that do not live in `l5-validate.sh`

**Commands**

```bash
set -euo pipefail
# DOD-02 — no foreign path touched
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git diff --name-only origin/integration...HEAD \
  | grep -Ev '^(access|infra|ops-vm|notify|assets)/' > /tmp/l5-foreign.txt || true
if [ -s /tmp/l5-foreign.txt ]; then
  echo "DOD-02 FAIL"; cat /tmp/l5-foreign.txt
else
  echo "DOD-02 PASS"
fi
```

```bash
set -euo pipefail
# DOD-05 — no hand-authored aggregate file in an owned tree
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
found=0
for f in assets/assets.yaml access/ai-toolchain.yaml access/access.yaml \
         infra/infra.yaml notify/notify.yaml ops-vm/ops-vm.yaml; do
  if [ -f "$f" ]; then echo "AGGREGATE-FORBIDDEN $f"; found=1; fi
done
if [ "$found" -eq 0 ]; then echo "DOD-05 PASS"; else echo "DOD-05 FAIL"; fi
```

---

## 11. Task-authoring contract for every other `L5-*` file

Every task in every `L5-*` file conforms to this. A task that cannot be written this way is not an L5 task — it is an L0 escalation (§14).

### 11.1 Task id

Format: `L5-<FF>-<TT>`

* `<FF>` — the two-digit L5 file number the task lives in (`00` is this charter).
* `<TT>` — the two-digit sequence within that file, starting at `01`.
* Ids are stable forever. A removed task's id is retired, never reused.
* Cross-lane dependencies are cited as `L1-*`, `L2-*`, `L3-*`, `L4-*` and are satisfied only through `contracts/**` or a published artifact (§6).

### 11.2 Size scale

Bounded by `PARTITION.md` line 34 — a lane branch is short-lived, under one day.

| Size | Bound |
|---|---|
| S | ≤ 1 hour of executor time |
| M | ≤ 4 hours |
| L | ≤ 1 working day. **This is the maximum.** Anything larger is split into multiple tasks before it is written down. |

### 11.3 Mandatory task template

````markdown
### L5-FF-TT — <imperative title>

**Size:** S | M | L
**Depends on:** <task ids, or `none`>
**Subsystem:** K | L | M | Q | R
**Spec:** §<n.n> (lines <A>–<B>)
**Writes:** <exact file paths, all under access/ infra/ ops-vm/ notify/ assets/>

**Commands** (run in order, verbatim):

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/FF-<slug>
```

```bash
set -euo pipefail
# <the task's file-creating commands, literal, no placeholders the executor must fill>
```

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git add <exact paths>
git commit -m "L5-FF-TT: <imperative title>" --trailer "Lane: L5"
git push -u origin lane/5/FF-<slug>
gh pr create --base integration --head lane/5/FF-<slug> \
  --title "L5-FF-TT: <imperative title>" \
  --body "Lane L5. Subsystem <X>. Spec §<n.n> lines <A>-<B>. Task L5-FF-TT."
```

**Acceptance criteria** (each provable by one command with unambiguous output):

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | … | `…` | `…` |

**SELF-VERIFY**

```bash
set -euo pipefail
<single block; prints exactly one PASS or FAIL line>
```

Expected output, exactly:

```
L5-FF-TT SELF-VERIFY PASS
```

**STOP rule**

If <named condition>, or if SELF-VERIFY prints anything other than the expected line:
do not commit, do not push, do not open a PR, do not improvise a fix.
Open a blocker issue using the template in L5-00-charter §11.5 and stop.
````

### 11.4 Rules that make a task executable without judgement

1. No placeholder a Sonnet-class executor must resolve. Every value is literal or read from a file the task names.
2. No "choose", "decide", "if appropriate", "as needed", "consider". If a choice exists, the charter or L0 already made it.
3. Every path is exact and inside an owned tree.
4. Every acceptance criterion is a command plus its exact expected output. "Looks correct" is not a criterion.
5. SELF-VERIFY prints exactly one line. Anything else is a FAIL.
6. Exactly one STOP rule, with the blocker template referenced by section number.
7. Dependencies are task ids, never prose.

### 11.5 Blocker-issue template

````markdown
**Title:** [L5 BLOCKER] L5-FF-TT — <one-line symptom>

**Lane:** L5 (Access, Infra & Ops)
**Task id:** L5-FF-TT
**Blocker type:** Contract Change Request | Missing upstream artifact | Spec ambiguity | Foreign path required | Command failed
**Branch:** lane/5/FF-<slug> (not pushed)

**What I ran**

```bash
set -euo pipefail
<the exact command>
```

**What I expected**

```
<the exact expected output from the task>
```

**What I got**

```
<verbatim actual output>
```

**Spec reference:** §<n.n>, lines <A>–<B> of Research/MultiProduct_MasterSpec_v4.0.md
**Partition reference:** PARTITION.md line <N>
**Owned-path check:** the work requires writing <path>, which L5 <does | does not> own

**What I did NOT do:** I did not edit any foreign path, did not edit contracts/**,
did not invent a value, did not push, did not open a PR.

**Decision needed from L0:** <one sentence>
````

---

## 12. Lane operating rules — restated, binding

| # | Rule | Source |
|---|---|---|
| 1 | One owner per path. A PR touching a foreign path FAILS lane-guard. No exceptions. | `PARTITION.md` 25 |
| 2 | Contract-first. `contracts/**` is L0's and frozen. A needed change is a Contract Change Request, never an edit. | `PARTITION.md` 26 |
| 3 | No shared mutable file, ever. Directory-per-item only. | `PARTITION.md` 27 |
| 4 | No cross-lane imports. Consume via `contracts/**` or a published artifact. | `PARTITION.md` 28 |
| 5 | Additive-only within the lane. Prefer new files; edit only inside owned paths. | `PARTITION.md` 29 |
| 6 | One branch per task, `lane/5/<phase>-<task>`, under a day, rebased on `integration` before the PR. | `PARTITION.md` 34 |
| 7 | L5 never merges or rebases another lane's branch. | `PARTITION.md` 36 |
| 8 | No task may require designing, choosing or interpreting. That belongs to L0. | `PARTITION.md` 47 |

---

## 13. Escalations to L0 — decisions L5 must not make

Each item below is inside L5's owned paths but outside L5's authority. L5 does not resolve them; it files a blocker issue (§11.5) and waits.

| # | Item | Why it is L0's | Spec anchor |
|---|---|---|---|
| E-01 | The `contracts/**` schema for each of the ten publication artifacts in §7 | `contracts/**` is L0-owned and frozen; L5 cannot author or amend it | `PARTITION.md` 22, 26 |
| E-02 | Assignment of subsystems G, H, J, O, P to a lane | PARTITION v1 assigns them to no lane; L5 does not claim them | §99.2 lines 9184–9231; `PARTITION.md` 15–22 |
| E-03 | Whether the background/inference host carries a GPU | Named as a benchmark-gated **Founder budget decision**; L5 records the asset entry once decided | §49.1 line 4344; §37.6 lines 3314–3323 |
| E-04 | The named holder of the §90.3 host-level accepted risk, and its compensating-control owner | A named, recorded accepted risk with a stated holder — a Founder record, not a build artifact | §90.3 lines 7975–7989 |
| E-05 | ~~The concrete value of the designated messaging channel~~ | RESOLVED (FD-062): L5_ROUTING_CHANNEL env var, default engineering-alerts | §92.11 lines 8272–8283 |
| E-06 | Whether the founder ops console is activated at all | Conditional on the §39.5 trigger — "only if free CI notifications prove insufficient" | §39.5 lines 3559–3612 |
| E-07 | Which required status checks are armed per repository at each phase | §98.2 makes the required-check list start empty and grow per phase; arming order is a phase decision | §98.2 lines 9006–9090 |
| E-08 | Whether the private-path remote-access requirement is deferred as a dated `policy_waiver` | **DEFERRED (FD-063):** resolved at Phase 1 deployment configuration. | §51.4 lines 4487–4499; §98.2 Phase 2 |
| E-09 | The calibrated initial values the spec marks "calibrated configuration" (run-count ceilings, review cadences, alert lead times beyond the 30-day floor) | Calibration is explicitly left to quarterly refit against observed data | §99.3 item 7, lines 9232–9247 |
| E-10 | Resolution of the two duplicate headings numbered `46.6` (lines 4182–4185 and 4186–4207) and the duplicate `AT-110` rows in §100.6 | A specification defect; L5 cites by line range and does not renumber | §46.6, §100.6 lines 9421–9441 |

---

## 14. Task

Exactly one task lives in this charter: the lane skeleton every other `L5-*` file depends on.

### L5-00-01 — Create the L5 lane skeleton and publication directories

**Size:** S
**Depends on:** none
**Subsystem:** K, L, M, Q, R (lane-wide)
**Spec:** §99.2 (lines 9184–9231)
**Writes:**
`access/{model,branch-protection,secrets,layer-b,fail-closed,published}/.gitkeep`,
`access/ai-runtime/{runtimes,extensions,mcp-servers,checks,constitution,benchmark}/.gitkeep`,
`infra/{github-org,runners,network,tools,published}/.gitkeep`,
`ops-vm/{compose,jobs,rebuild,smoke,offvm,published}/.gitkeep`,
`notify/{routing,channels,escalation,published}/.gitkeep`,
`assets/{inventory,deadlines,watch,published}/.gitkeep`,
`infra/tools/l5-validate.sh`

**Commands** (run in order, verbatim):

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/00-skeleton
```

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
missing=0
for key in people-intelligence access_status allocation_state ai_processing_permitted \
           ai_runtime_dependency production_db_access detection_expectation \
           reliability_criticality regulatory_notification_hours; do
  if ! grep -rql "$key" contracts/ 2>/dev/null; then echo "CONTRACT-MISSING $key"; missing=1; fi
done
if [ "$missing" -eq 0 ]; then echo "L5 CONTRACT GATE PASS"; else echo "L5 CONTRACT GATE FAIL"; fi
```

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
for d in access/model access/branch-protection access/secrets access/layer-b \
         access/fail-closed access/published \
         access/ai-runtime/runtimes access/ai-runtime/extensions \
         access/ai-runtime/mcp-servers access/ai-runtime/checks \
         access/ai-runtime/constitution access/ai-runtime/benchmark \
         infra/github-org infra/runners infra/network infra/tools infra/published \
         ops-vm/compose ops-vm/jobs ops-vm/rebuild ops-vm/smoke ops-vm/offvm ops-vm/published \
         notify/routing notify/channels notify/escalation notify/published \
         assets/inventory assets/deadlines assets/watch assets/published; do
  mkdir -p "$d"
  : > "$d/.gitkeep"
done
```

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
cat > infra/tools/l5-validate.sh <<'L5EOF'
#!/usr/bin/env bash
# L5 lane validation entrypoint. Owned by lane L5 (PARTITION.md line 21).
# Modes are added by later L5 tasks. --layout is implemented here.
set -u
MODE="${1:---layout}"

l5_dirs() {
  cat <<'DIRS'
access/model
access/branch-protection
access/secrets
access/layer-b
access/fail-closed
access/published
access/ai-runtime/runtimes
access/ai-runtime/extensions
access/ai-runtime/mcp-servers
access/ai-runtime/checks
access/ai-runtime/constitution
access/ai-runtime/benchmark
infra/github-org
infra/runners
infra/network
infra/tools
infra/published
ops-vm/compose
ops-vm/jobs
ops-vm/rebuild
ops-vm/smoke
ops-vm/offvm
ops-vm/published
notify/routing
notify/channels
notify/escalation
notify/published
assets/inventory
assets/deadlines
assets/watch
assets/published
DIRS
}

case "$MODE" in
  --layout)
    missing=0
    while IFS= read -r d; do
      [ -d "$d" ] || { echo "MISSING $d"; missing=1; }
    done < <(l5_dirs)
    if [ "$missing" -eq 0 ]; then echo "L5 LAYOUT PASS"; else echo "L5 LAYOUT FAIL"; fi
    ;;
  *)
    echo "L5 VALIDATE UNIMPLEMENTED-MODE $MODE"
    exit 2
    ;;
esac
L5EOF
chmod +x infra/tools/l5-validate.sh
```

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
git add access infra ops-vm notify assets
git commit -m "L5-00-01: create L5 lane skeleton and publication directories"
git push -u origin lane/5/00-skeleton
gh pr create --base integration --head lane/5/00-skeleton \
  --title "L5-00-01: create L5 lane skeleton and publication directories" \
  --body "Lane L5. Subsystems K, L, M, Q, R. Spec §99.2 lines 9184-9231. Task L5-00-01."
```

**Acceptance criteria**

| # | Criterion | Command | Expected output |
|---|---|---|---|
| 1 | The contract gate passes before any file is created | the second command block above | `L5 CONTRACT GATE PASS` |
| 2 | All 31 lane directories exist | `bash infra/tools/l5-validate.sh --layout` | `L5 LAYOUT PASS` |
| 3 | The validator is executable | `test -x infra/tools/l5-validate.sh && echo EXEC-OK` | `EXEC-OK` |
| 4 | An unknown mode fails loudly rather than silently passing (§64.1 denial-by-default) | `bash infra/tools/l5-validate.sh --nope; echo "exit=$?"` | `L5 VALIDATE UNIMPLEMENTED-MODE --nope` then `exit=2` |
| 5 | No foreign path is touched | the DOD-02 command in §10.1 | `DOD-02 PASS` |
| 6 | No hand-authored aggregate file was created | the DOD-05 command in §10.1 | `DOD-05 PASS` |
| 7 | Exactly 31 `.gitkeep` files were added | `git diff --name-only origin/integration...HEAD -- '*.gitkeep' \| wc -l` | `31` |
| 8 | The branch name matches the lane prefix | `git rev-parse --abbrev-ref HEAD` | `lane/5/00-skeleton` |

**SELF-VERIFY**

```bash
set -euo pipefail
[ -n "$CONTROL_PLANE_ROOT" ] || { echo "ERROR: CONTROL_PLANE_ROOT is not set"; exit 1; }
cd "$CONTROL_PLANE_ROOT"
ok=1
[ "$(bash infra/tools/l5-validate.sh --layout)" = "L5 LAYOUT PASS" ] || ok=0
[ -x infra/tools/l5-validate.sh ] || ok=0
[ "$(git diff --name-only origin/integration...HEAD -- '*.gitkeep' | wc -l | tr -d ' ')" = "31" ] || ok=0
[ "$(git diff --name-only origin/integration...HEAD | grep -Ecv '^(access|infra|ops-vm|notify|assets)/')" = "0" ] || ok=0
[ "$(git rev-parse --abbrev-ref HEAD)" = "lane/5/00-skeleton" ] || ok=0
if [ "$ok" -eq 1 ]; then echo "L5-00-01 SELF-VERIFY PASS"; else echo "L5-00-01 SELF-VERIFY FAIL"; fi
```

Expected output, exactly:

```
L5-00-01 SELF-VERIFY PASS
```

**STOP rule**

If the contract gate prints `L5 CONTRACT GATE FAIL`, or any of the five owned top-level directories already exists with content authored by another lane, or SELF-VERIFY prints anything other than `L5-00-01 SELF-VERIFY PASS`:
do not commit, do not push, do not open a PR, do not create the missing contract key, do not edit any path outside `access/ infra/ ops-vm/ notify/ assets/`.
Open a blocker issue using the template in §11.5 and stop.
