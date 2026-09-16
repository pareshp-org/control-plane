# Founder Decisions Summary

112 decisions recorded (FD-001..112). All DECIDED.
See `_FOUNDER_DECISIONS.md` for full text.

## By Session
- Sessions 1-12: FD-001..081 (architecture, lane design, Phase 0)
- Session 13: FD-082..093 (PFD resolutions, L1/L4 specifics)
- Session 14: FD-094..112 (validator, schemas, registries, governance)
- Session 15 additions (no new FDs — implementation/hardening only): all 18
  validator rules (R01-R18) implemented with full YAML parsing, replacing
  stubs (validator CLI: 18/18 rules PASS, 6/6 integration tests pass);
  concordance check fixed post-normalization (T-infix restored for L3-03,
  body_ids patterns/EXPECT updated after FD-082/FD-095); protocol mechanical
  unfailable-check defects fixed per B-09 (_98-DEEP-REVIEW.md), plus local
  CI gate-check and push-guard scripts added and stale docs refreshed.
- Session 16 additions (no new FDs — final hardening only): multiple
  run-phase-0.sh crash bugs found and fixed via empirical testing
  (L0-P0-001 export/re-anchor, L0-P0-012 CPR skeleton, L0-P0-021 pip
  install); L1-05-tasks.md JSON-comment bug fixed; security scan scripts
  upgraded from stub to real tooling.

## Key Clusters
### Identity & Org
- FD-067: L0_LOGIN = bendrohit-eng
- FD-069: ORG = pareshp-org (Free plan)
- FD-050: Schema URN prefix = urn:multiproduct:schemas

### Architecture
- FD-082: Task ID format L<N>-<FF>-<NN>
- FD-094: Validator CLI Option B
- FD-096: Schema flat layout
- FD-100: Registry dir-per-item

### Operations
- FD-086: Actor gate (bendrohit-eng only)
- FD-102: Branch protection (PRs required)
- FD-106: Canary sentinel
- FD-109: Bootstrap exception (single owner)

## Open Items
- PFD-006: Break-glass second owner (DEFERRED — decide before Phase 1 go-live)
- 8 product names: Replace Product-1..8 in facts.tsv
