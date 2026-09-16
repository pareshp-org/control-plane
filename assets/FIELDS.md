# Operational asset inventory — field table

One file per asset under `assets/inventory/<asset_id>.yaml` (PARTITION.md rule 3:
directory-per-item, never a shared mutable list). This realises the `assets.yaml`
artifact named in Spec Sections 39.1 and 52 with the same field set.

Enforced by `assets/validate_assets.py`.

## Common fields — required on every asset file

| Field | Type | Rule |
|---|---|---|
| `asset_id` | string | lower-case `[a-z0-9-]+`, equal to the filename stem |
| `asset_class` | string | one of the closed set below |
| `owner` | string | a person id; never empty, never `unassigned` |
| `expiry_date` | string | ISO-8601 `YYYY-MM-DD` |
| `alert_days` | integer | **>= 30** (Section 49.1) |
| `cost_band` | string | band label, or `none` |
| `spec_reference` | string | the Section number mandating the entry |

Closed `asset_class` set: `machine_credential`, `encryption_key`, `host`,
`ci_runner`, `ai_subscription_seat`, `detection_leg`, `certificate`, `domain`,
`oauth_credential`, `signing_certificate`, `vendor_contract`, `founder_account`,
`intake_channel`.

## Class-conditional required fields

| `asset_class` | Additional required fields |
|---|---|
| `machine_credential` | `rotation_cadence`, `rotator`, `runbook`, `behavioural_envelope`, `envelope_alert_config_owner` |
| `encryption_key` | `holder`, `rotation_cadence`, `escrow_row`, `read_access_list` |
| `host` | `hostname`, `machine_account`, `owned_controls`, `patch_cadence`, `site`, `power`, `network` |
| `ci_runner` | `hostname`, `patch_cadence`, `site`, `power`, `network`, `runner_group`, `on_operations_vm` |
| `ai_subscription_seat` | `vendor`, `runtime`, `holder`, `renewal_date`, `billing_cycle`, `tier` |
| `detection_leg` | `mechanism`, `runs_off_operations_vm`, `routes_to` |

Asset owners participate in orphan detection (Section 49.1): a departing person
who owned a certificate or a domain leaves an orphaned asset. `owner` is always a
person id resolving in the people registry (`registries/people/`, directory-per-item),
never a team name.

## Known cross-task schema collision — not resolved by this task

Some `assets/inventory/*.yaml` entries are written by `L5-03` tasks (a
different task family in this lane) under an incompatible field set —
observed examples include `layer-b-backup-credential.yaml`,
`layer-b-backup-encryption-key.yaml` and `layer-b-selfview-pubkey-registry.yaml`,
which use `owner_capability` instead of `owner`, `alert_threshold_days`
instead of `alert_days`, `expiry_tracked: true` instead of a real
`expiry_date`, and `asset_class` values (`control-plane-machine-credential`,
`encryption-key`, `registered-key-material`) that are not in the closed set
above. `assets/validate_assets.py` correctly reports each as non-conforming;
this is a real, pre-existing defect in the committed tree, not a defect in
this validator. Rewriting L5-03's files is outside this task's ownership
(L5-05-01 names no such file) and outside this lane's authority to resolve
unilaterally: L5-98-DEEP-REVIEW.md finding **B-13** already names this exact
collision and its fix ("L0 fixes one entry schema, one `id` key and one
filename set for `assets/inventory/**`, applied to L5-03, L5-05 and L5-06 in
a single change") as an L0 decision. Until that decision lands,
`python3 assets/validate_assets.py` reports `ASSET-VALIDATE: FAIL` on the
committed tree because of these pre-existing entries, even when every entry
this lane's L5-05-* tasks write is individually conforming. A related
consequence: the Layer B backup credential now carries two inventory entries
under two different names (`layer-b-backup-credential` from L5-03-06 and
`machine-credential-layer-b-backup` from L5-05-02), which the same B-13
finding names as a double-count risk in the Section 49 expiry sweep — also
an L0 fix, not a local one.
