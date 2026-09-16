# Lane 5 integration readiness

**Merge-train position:** last. `PARTITION.md`'s branch-and-merge model runs
L1 → L4 → L2 → L3 → **L5**, once per cycle, because L5 (access/infra) is
independent at build time and integrates last. That position obliges this
report: nothing downstream absorbs a Lane 5 defect, so this document states
the truth about what is green, what is not, and why.

Run `bash infra/tools/readiness.sh` for the current state in one command.

## Gates

Every gate below runs from the repository alone — no live host, no network,
no GitHub API call. Each has an unambiguous PASS line; a gate this lane can
only prove against real infrastructure (the AT-097/AT-098/AT-108/AT-109/
AT-110 family, the live Layer B-M and shared Grafana instances, the ops VM
itself) is out of `readiness.sh`'s reach from here and is exercised instead
by the host-side scripts already committed under `access/tests/`,
`ops-vm/tests/`, `infra/tests/` and `notify/tests/`, per
`access/tests/coverage.yaml`.

| Gate | Command | Expected output |
|---|---|---|
| owned-roots | `bash access/layer-b/check-owned-roots.sh` | `OWNED_ROOTS_OK` |
| test-coverage | `bash access/tests/check-coverage.sh` | `COVERAGE OK` |
| ai-toolchain-pins | `python3 access/ai-toolchain/validate_toolchain.py` | `TOOLCHAIN-VALIDATE: PASS (6 runtimes)` |
| notify-channels | `python3 notify/check_channels.py` | `CHANNEL-CHECK: PASS` |
| notify-closed-list | `python3 notify/check_closed_list.py` | `CLOSED-LIST-GUARD: PASS` |
| notify-push-list | `python3 notify/check_push_list.py` | `PUSH-LIST: PASS` |
| layerb-post-patch | `bash access/layer-b/check-post-patch.sh` | `POST_PATCH_DECL_OK 8/8` |
| team-derivation | `python3 access/tools/check_team_derivation.py` | `TEAM-DERIVATION: PASS (6 assertions)` |
| arming-order | `python3 access/tools/check_arming_order.py` | `ARMING-ORDER: PASS (5 assertions)` |
| secret-tiers | `python3 access/secrets/tools/validate_tiers.py` | `RESULT PASS 5` |
| deadline-watch | `python3 assets/validate_deadlines.py` | `DEADLINE-VALIDATE: PASS (0 files)` |
| seat-check | `python3 assets/check_seats.py` | `SEAT-CHECK: PASS` |
| runner-estate | `python3 assets/check_runner_estate.py` | `RUNNER-CHECK: PASS` |
| asset-inventory | `python3 assets/validate_assets.py` | `ASSET-VALIDATE: PASS (n files)` — **currently FAILS, see below** |
| invariant-map | `python3 access/tools/validate_invariant_map.py` | `INVARIANT MAP OK: 12 invariants, 12 mechanical, 0 unresolved` |
| l2-handoff | `python3 infra/tools/validate_handoff.py` | `HANDOFF OK: 5 request(s), 0 foreign path(s)` |

Current state: **15/16 PASS.**

## The one open gate: asset-inventory

`assets/validate_assets.py` reports `ASSET-VALIDATE: FAIL (27 errors)`. This
is `lanes/L5-98-DEEP-REVIEW.md` finding **B-13**, already documented in
`assets/FIELDS.md` under "Known cross-task schema collision — not resolved
by this task": three inventory entries written under a different phase's
field set (`layer-b-backup-credential.yaml`,
`layer-b-backup-encryption-key.yaml`,
`layer-b-selfview-pubkey-registry.yaml` — `owner_capability` instead of
`owner`, `alert_threshold_days` instead of `alert_days`, `expiry_tracked:
true` instead of a real `expiry_date`, and `asset_class` values outside the
closed set) fail the closed Section 49.1 schema this lane's validator
enforces. B-13's own fix is named there too: *"L0 fixes one entry schema,
one `id` key and one filename set for `assets/inventory/**`, applied to
L5-03, L5-05 and L5-06 in a single change."* This report does not fabricate
a pass over that finding; it surfaces it, exactly as it already stood before
this readiness report existed.

## DECISION REQUIRED — routed to L0 (5 items)

| # | Item | Raised by |
|---|---|---|
| 1 | The private VPN/tunnel path to the operations VM, and who holds it | (ops-vm provisioning) |
| 2 | The off-VM dead-man witness — outside the VM, outside GitHub, outside the product providers (D94) | `ops-vm/offvm/deadman.yaml`, `notify` routing for the off-VM leg |
| 3 | The background-inference host's real hardware, site and power/network provider fields | Hermes background-inference asset entry |
| 4 | The severity a departing asset owner's orphaned certificate/domain carries when no successor is named | Asset-owner orphan feed |
| 5 | Custody of the Section 42.2 phone-escalation numbers (they are never committed to this repository) | `notify/escalation/phone-path.yaml`, `notify/assisted/webhook-request.md` |

Two further, narrower contract gaps sit underneath the Layer B gates above
and are not counted against the 16 readiness gates because their own
canonical bodies (`lanes/L5-03-layer-b.md`, tasks L5-03-08 and L5-03-09)
correctly stop rather than invent a value: `contracts/access/access-inputs.yaml`
— L0's own Phase-0 frozen input — does not exist yet, so the Layer B
session-lifetime renderer (`ops-vm/layer-b/session/render-session-ini.sh`)
and the capability-derived allowlist sync
(`ops-vm/layer-b/allowlist/sync-allowlist.sh`) both correctly report a
blocked state (exit 2) rather than a duration or a holder list this lane is
not authorised to choose.

## ASSISTED tasks whose human half is outstanding

| Task | What only a human can do |
|---|---|
| Messaging webhook creation and secret storage | `notify/assisted/webhook-request.md` — create the incoming webhook, store its URL as `NOTIFY_DESIGNATED_CHANNEL` / `NOTIFY_OUT_OF_HOURS_CHANNEL` / `NOTIFY_PRODUCT_ALERT_CHANNEL` |
| Per-person public-key registration and annual re-key | `access/layer-b/assisted/key-registration-request.md` — exchange each person's public key half at onboarding and annually |
| Org-settings arming and evidence capture | `access/runbooks/apply-organisation.sh` et al. — apply against the live GitHub organisation and capture evidence |
| Ops-VM image, version lock and provisioning | `ops-vm/provision/30-stack-up.sh` and the host itself — stand up the real VM |
| AT-110 reconciler-credential bound execution | `access/tests/human-actions/L5-07-09-AT-110.md` — run the six AT-110 attempts with the live reconciler credential |
| AT-022 break-glass Owner drill | `access/tests/human-actions/L5-07-09-AT-022.md` — exercise the real continuity path |

## Lane 5 claims no part of subsystems G, H, J, O or P

Consistent with `PARTITION.md` and this lane's own charter, Lane 5 builds no
part of subsystem G (repository/product provisioning logic itself — D
provisions, L5 declares the model it provisions from), H (the reconciler —
L3's), J, O (audit-log-gap accepted risk, left to L0 in `EXCLUSIONS.md`), or
P (the People-intelligence engine — L5 builds only the gate, per §99.2 "P is
hard-gated on L's datasource separation").
