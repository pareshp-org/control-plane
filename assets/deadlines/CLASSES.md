# Vendor deadline watch — class and field table

One file per external-deadline entry under `assets/deadlines/<deadline_id>.yaml`
(PARTITION.md rule 3: directory-per-item, never a shared mutable list).

Enforced by `assets/validate_deadlines.py`. Floor configuration in
`assets/watch/lead-time-policy.yaml`.

## The four closed classes — Spec Section 49.2

| `deadline_class` | Covers |
|---|---|
| `api_sunset` | Announced API sunsets, deprecations and versioning deadlines for any declared dependency |
| `app_store_policy` | App-store policy deadlines: target-API requirements, review-guideline changes, signing and privacy-declaration deadlines |
| `auth_mechanism_change` | OAuth, webhook and authentication-mechanism changes announced by identity or platform providers |
| `vendor_contract_change` | Vendor contract changes requiring migration (pricing-model changes, plan sunsets) |

## Required fields

| Field | Type | Rule |
|---|---|---|
| `deadline_id` | string | lower-case `[a-z0-9-]+`, equal to the filename stem |
| `deadline_class` | string | one of the four values above |
| `vendor` | string | non-empty |
| `owner` | string | a person id; never empty, never `unassigned`; defaults to the affected product's Primary Owner |
| `product` | string | a product id, or the literal `portfolio` |
| `announced_deadline` | string | ISO-8601 `YYYY-MM-DD` |
| `alert_lead_days` | integer | **>= 30** (Section 49.2 floor) |
| `lead_time_rationale` | string | required and non-empty whenever `alert_lead_days` is greater than `30` |
| `migration_effort_estimate_days` | integer | `>= 0` |
| `announcement_reference` | string | non-empty |
| `pattern_class` | string | the literal `vendor-deprecation` |
| `spec_reference` | string | the Section number mandating the entry |

## What this directory never contains

An invented vendor announcement. A deadline entry records a real external
event with a real date and a real reference; the roster is operational data
supplied by the entry's owner, exactly as the runner roster of
`infra/runners/hosts.list` is (L5-05-04).

Any `alert_lead_days` above `30` is calibrated configuration set by the owner
while the effort estimate is fresh (Section 49.2). L5 records it; L5 never
chooses it.

The `pattern_class` field feeds the vendor-deprecation pattern class of the
failure-pattern register (Section 49.2). That register is subsystem **O**,
which PARTITION v1 assigns to no lane. This file names the dependency and
claims nothing.
