# Closed-list guard — what each rule proves

Spec Section 92.11: "Every surface in this Part is one of two things, and
nothing else may page a person."

Run: `python3 notify/check_closed_list.py`

| Rule | Proves | A failure means |
|---|---|---|
| G1 | Every route's `push_class` is one of the eight closed Section 92.11 classes | The push list has grown outside the contract |
| G2 | The class set is exactly those eight, and there are exactly eleven routes | A class was added or lost |
| G3 | No literal destination in `notify/channels`, `notify/escalation` or `notify/routing` | Section 92.11's "a configuration value, never a hard-coded destination" is broken, or a phone number was committed |
| G4 | Every route's `destination_channel` resolves to a declared channel carrying a `configuration_key` | A route points at nothing, or at a hard-coded destination |
| G5 | `notify/route.py` refuses every off-list probe event | Something outside the closed list can page a person |
| G6 | No `push_class` is declared outside `notify/routing/` | A second, ungoverned push surface exists |
| G7 | No route mentions a detection leg or an expiry finding | Alert traffic or a wait surface has been promoted to a push event without the governed addition |
| G8 | `notify/published/routing.v1.json` matches a fresh regeneration | The published artifact — the only thing the Actions webhook step reads — was hand-edited |

## The two deliberate exclusions

**Off-VM detection legs** (L5-05-05, Section 51.5) route to the
Actions-webhook **alert channel** and the Section 42.2 phone path. Alert
traffic is not the Section 92.11 push list.

**The expiry-and-deadline scan** (Sections 49.1, 92.6) is a wait
surface — the platform operations queue — and emits zero push events. Expiring
assets are not on the closed list.

Both are intentional. Neither is a gap.

## Adding something to the push list

Section 92.11: "If something appears urgent enough to page a person and is not
on the push list, the correct response is a **governed addition to the push
list and the event taxonomy**, never an ad-hoc alert."

A governed addition is an L0 decision plus an L1 entry in the `platform.yaml`
`event_type` enum. It is never a file dropped into `notify/routing/`, never a
loosened rule in this guard, and never a direct message sent from a job.
