# The closed push list — Spec Section 92.11

> Every surface in this Part is one of two things, and nothing else may page a
> person.

**Push events** go to the designated messaging channel, whose value is
configuration (`notify/channels/`, L5-05-13). **Wait surfaces** are
everything else — dashboards, boards and generated reports — and send nothing
unsolicited.

One file per route under `notify/routing/<route-id>.yaml` (PARTITION.md
rule 3). Enforced by `notify/check_push_list.py` and, end to end, by
`notify/check_closed_list.py` (L5-05-16).

## The eight closed classes, and the eleven routes that realise them

| `push_class` | Section 92.11 wording | Route files |
|---|---|---|
| `gate_1_submission` | a Gate 1 submission, pushed to its approver | `gate-1-submission` |
| `gate_2_request` | a Gate 2 request and any reroute to the Backup Owner or Cross-Reviewer | `gate-2-request`, `gate-2-reroute` |
| `verification_block_unblock` | a verification block or unblock | `verification-block`, `verification-unblock` |
| `blocking_class_drift` | Blocking-class drift | `blocking-class-drift` |
| `expiry_warning` | delegation expiry and temporary-person expiry warnings | `delegation-expiry-warning`, `temporary-person-expiry-warning` |
| `launch_sign_off_request` | a launch sign-off request | `launch-sign-off-request` |
| `pending_founder_decision` | a pending Founder decision | `pending-founder-decision` |
| `support_first_touch_breach` | a support first-touch breach | `support-first-touch-breach` |

Eight classes. Eleven routes. The guard asserts both numbers, so the list
cannot silently grow.

## The taxonomy rule

> Every push event exists in the Section 97 event taxonomy — an event absent
> from the taxonomy cannot page anyone.

Every route names an `event_type` and the Section 97.3 taxonomy line it comes
from. The closed `event_type` enum lives in `platform.yaml` (Section 97.3),
which is **L1's** — read as data, never edited from this lane (boundary rule
B-4). A route whose `event_type` is absent from the enum is an **L1 enum
entry** blocker issue. It is never fixed by editing a registry, and it is
never fixed by deleting the route.

## The D79 coalescing rule

Pending-decision prompts that carry **no** legal or notification clock coalesce
into the morning digest rather than pushing individually. Immediate push is
reserved for prompts carrying a clock (Sections 43.1, 21.3) and for the rest of
the closed push list.

## Adding to this list

> If something appears urgent enough to page a person and is not on the push
> list, the correct response is a governed addition to the push list and the
> event taxonomy, never an ad-hoc alert.

A governed addition is an L0 decision plus an L1 enum entry. It is never a new
file dropped into `notify/routing/` by an executor.
