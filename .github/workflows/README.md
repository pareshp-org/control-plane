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

## Current status (Session 16)

The action pins in `_pins/pins.env` (L2-P1-T01) are not yet applied to the
live reusable workflows in this directory (`reusable-ci.yml`,
`reusable-promote.yml`, `reusable-release.yml`, `security-scan.yml`) — those
files still reference third-party actions by floating tag
(`actions/checkout@v4` etc). `_pins/verify-pins.sh` will FAIL against this
directory until that migration lands; that migration is tracked separately
and is not blocked by anything Founder-side.
