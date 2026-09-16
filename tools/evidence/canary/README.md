# The seeded canary for the digest-chain sweep

Spec: Section 53.1 line 4680 - "A permanent seeded drift record - a deliberately
planted, clearly labelled mismatch in the comparison set - exists at all times,
and every reconciliation run MUST find it. A run that reports zero findings,
including the canary, is a FAILED run, not a clean one: it proves the instrument
stopped looking, not that nothing drifted."

DO NOT REMEDIATE. DO NOT DELETE. DO NOT MAKE THESE TWO DIGESTS MATCH.

The estate below is a permanent, synthetic, deliberately mismatched pair: a
production deployment record for one digest, and an observation of a different
digest. `verify-digest-chain` MUST exit 3 over it on every run. If it exits 0,
the sweep has stopped comparing and `.github/workflows/verify-digest-chain.yml`
fails the whole run with CANARY_NOT_FOUND before it ever reports on the live
estate.

Nothing here is counted as a live finding: the canary sweep writes its own
findings file and that file is never escalated (L2-T512 escalates the live
findings file only).
