# ASSISTED — messaging webhook creation and secret storage

**L0 EXECUTES.** This document is the handoff; it is not the webhook.

## Why this is not the executor's to do

Section 92.11 requires the designated messaging channel to be "a
configuration value, never a hard-coded destination." `notify/channels/*.yaml`
(L5-05-13) already declares the three configuration keys that need a real
webhook behind them — see the table below — and
`destination_value_owner: "L0 — L5-00-charter.md escalation E-05"` on each.
Creating the incoming webhook in the messaging platform, and storing its URL
as a secret, requires:

- an account with admin rights on the messaging workspace (not this session's
  to hold or exercise), and
- writing a **repository or organisation secret**, which is an account/
  settings change this lane never performs on its own authority (see the
  Explicit-permission rules this session operates under).

`notify/check_channels.py` (C2, C3) already proves no literal webhook URL is
ever committed to this repository — it fails the channel-guard check on any
`https?://` literal under `notify/channels/` or `notify/escalation/`. This
task's job is the request, not the value.

## What to create

One incoming webhook in the organisation's chosen messaging platform (Slack,
Teams, or Discord — the platform choice is itself an L0 decision this
document does not make), routed as follows:

| Configuration key | Consumer | Channel purpose | Spec |
|---|---|---|---|
| `NOTIFY_DESIGNATED_CHANNEL` | `notify/channels/designated-messaging-channel.yaml` | Every Section 92.11 push event | 92.11, 92.1, 99.2 row R |
| `NOTIFY_OUT_OF_HOURS_CHANNEL` | `notify/channels/out-of-hours-channel.yaml` | Founder + Team Lead out-of-hours channel | 47.5, 99.2 row R, 42.2 |
| `NOTIFY_PRODUCT_ALERT_CHANNEL` | `notify/channels/per-product-alert-channel-template.yaml` | One per product, created at onboarding | 92.1, 99.2 row R, 51.5 |

`NOTIFY_DESIGNATED_CHANNEL` and `NOTIFY_OUT_OF_HOURS_CHANNEL` may point at the
same webhook if the org runs one channel for both purposes — that choice is
L0's, not this document's.

## Storage

Store each webhook URL as a **repository or organisation secret** under the
literal configuration key named above (never a different name — L2's Actions
workflow step, which is the only thing that ever delivers a push event
per boundary rule B-2, reads it by that exact name). Never commit the value
to `notify/**` or anywhere else in this repository.

## Checklist for whoever executes this

- [ ] Messaging platform chosen (Slack / Teams / Discord / other) and recorded
      as a decision
- [ ] `NOTIFY_DESIGNATED_CHANNEL` webhook created; URL stored as a secret
      under that exact name
- [ ] `NOTIFY_OUT_OF_HOURS_CHANNEL` webhook created (or the same webhook
      reused, recorded as such); URL stored as a secret under that exact name
- [ ] First `NOTIFY_PRODUCT_ALERT_CHANNEL`-shaped webhook created for the
      first onboarded product; URL stored as a secret under that exact name
- [ ] `python3 notify/check_channels.py` still reports `CHANNEL-CHECK: PASS`
      after storage (proves no literal leaked back into the repository)
- [ ] The three secret names, and which channel each backs, are recorded
      wherever this lane's secret inventory is reviewed (Section 49.1)

## STOP rule

If asked to pick the messaging platform, or to decide whether the
out-of-hours channel reuses the designated channel's webhook — do not decide.
Both are operational decisions Section 92.11 and `L5-00-charter.md`
escalation E-05 already route to L0. Record the question, not an answer.
