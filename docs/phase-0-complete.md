# Phase 0 complete - the contracts are frozen

Frozen at tag `contracts/v1.0.0`, hash `07232bd31808ca03c289e69cb7b660d4b67bbdb253f7bc13cca04e0f67eb631b`, on 2026-09-16.

## What is now true

- Twenty-four contracts exist under `contracts/**`, each with a seven-key header, a register row, a stub, and at least one golden-valid and one golden-invalid fixture.
- `make contracts-verify` proves all of it in one command.
- `contracts.sha256` records the freeze; `make promote-check` prints `CONTRACTS-FROZEN OK` while it holds.
- Code Owner review is required on `contracts/**`, and the freeze tag is immutable with no bypass actor.
- Five gaps are recorded, dated and owned in `docs/recorded-gaps.md`.

## The one rule that matters now

No lane edits `contracts/**`. A lane needing a change files a Contract Change Request
(`docs/contract-change-request.md`) and stops. Waiting is correct behaviour; guessing is not.
