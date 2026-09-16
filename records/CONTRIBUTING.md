# Contributing to control-plane-records

This repository holds `records/**` and `events/**` and nothing else.
Master Spec v4.0 Section 97 (lines 8834-8991) and Section 40.1 (lines 3644-3686) govern it.

## The one rule

**Nobody edits a record file by hand to report a result.** (Section 97.2, line 8871.)

A manual result reaches this repository through **RECORD-VERIFICATION-RESULT** — a
`workflow_dispatch` with five structured inputs (product, item, mechanism, pass or fail,
evidence link) that writes the record and appends the event in one commit. Manual UAT and
verification results (Section 31.2, line 2790), restore-test confirmations (Section 44.3,
line 4008) and support-loop closures (Section 22.5, line 2256) all arrive this way.

If you find yourself opening a text editor on a file under `records/` to say that something
passed, failed, completed or was confirmed: stop. Use the dispatch.

## Records are never edited in place

Section 97.2, line 8890: a record never edits in place; **corrections are follow-up records**.
Invariant 48 (line 9516): historical records are never silently overwritten.
A pull request that modifies or deletes an existing file under `records/` or `events/` is
rejected by `tools/records/validate-human-record.sh` in the control-plane repository.

## Which stores accept a hand-authored record

Six stores accept hand-authored records, and only these six. Every other store is written by
a machine path and a hand-authored file there is rejected.

| Store | Who authors | Spec line |
| --- | --- | --- |
| `records/postmortems/` | Human, from template; closure tracked | 8848 |
| `records/decisions/` | Human, at the moment of decision (normally through the record-decision CLI) | 8852 |
| `records/security-reviews/` | Security reviewer, from template | 8856 |
| `records/demos/` | Human, brief, after each client demo or UAT walkthrough | 8859 |
| `records/onboarding/` | Onboarding workflow at phase completion; **human for judgment steps only** | 8861 |
| `records/leave/` | Founder or delegate on approval | 8862 |

Machine-written stores, for reference: incidents, uat, estimates, deployments, restore-tests,
decisions/pending, breaches, deletion-requests, eval, launches, support, and `events/`.
The full register with the writing actor and the write path for every store is
`tools/records/write-paths.yaml` in the control-plane repository.

## How to add a hand-authored record

1. Branch from the default branch.
2. Add **one new file** under the store's directory. Do not touch any existing file.
3. Every record carries `record_schema_version`, `id`, `product` and `timestamp`
   (Section 97.2, line 8890). Every timestamp is UTC **with its offset**
   (Section 97.1, line 8839) — for example `2026-08-27T09:31:04+00:00`.
4. Open a pull request. `validate-human-record.sh` runs against the diff.
5. A reviewer merges. Merges are fast-forward appends; the repository ruleset blocks
   force pushes, branch deletion and tag deletion, with no bypass actor (Section 40.1,
   line 3675, D107).

## Deployment operations

Accepted deviation: this repository uses `make deploy` and `make restore` for deployment operations (Q14=B). See `docs/decisions/D-L4-P3-03.md`.

## What lane L4 does not configure

L4 declares; it does not configure GitHub. The protection posture this repository requires is
recorded in `PROTECTION-REQUEST.md` for L0. No file exists under `.github/` here until charter
decision **D-L4-03** resolves.

## Commit signing

The records-writer signs every commit it makes on the default branch, and a default-branch
commit that is unsigned or signed by another identity is Blocking drift (Section 40.1,
line 3676). Configuring that identity is a credential matter, not something this file or any
L4 script performs.
