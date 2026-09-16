---
last_mapped_commit: c23a01076c25ff0b3f48404c5dbd702db1e8c9a1
last_mapped_at: 2026-09-16
---
<!-- refreshed: 2026-09-16 -->

# Codebase Concerns

**Analysis Date:** 2026-09-16

## Tech Debt

**Empty policy registry:**

- Issue: `registries/policies.yaml` is empty with just an empty `policies: []` list. This is documented as a placeholder until Phase G2, but blocks downstream consumers.
- Files: `registries/policies.yaml`
- Impact: Any code that expects policies to be present will fail silently or skip validation. R-rules that check policy references (R10: PolicyEnforcedByValid) handle empty policies but may mask real configuration issues.
- Fix approach: Either remove the file until Phase G2, or create a fixture with sample policies for development/testing and document the phase constraint clearly.

**Schema validation duplication:**

- Issue: `scripts/l1/jsonschema-conform.py` validates registries/** against schemas/registry/*.json in production, while `tests/integration/test_registries_schema_independent.py` re-implements the entire Draft-07 validator subset independently to catch bugs in the production validator.
- Files: `scripts/l1/jsonschema-conform.py`, `tests/integration/test_registries_schema_independent.py`
- Impact: Maintenance burden — changes to schema validation logic must be mirrored in two places, and subtle bugs could slip through if the hand-rolled validator diverges from production logic.
- Fix approach: Extract the independent validator to a shared module that both the production script and tests can import, or document the deliberate duplication in a constraint comment at the top of both files with a reference to why the duplication exists (spec 53.1 second-instrument rule).

## Known Bugs

**Policies registry missing required fields (pre-existing):**

- Symptoms: `registries/policies.yaml` is missing `id`, `name`, and `enforced_by` fields that are required by the schema.
- Files: `registries/policies.yaml`, `schemas/registry/policies.v1.schema.json`
- Trigger: Run schema conformance checks when policies registry is populated.
- Workaround: The policies list is currently empty, so validation passes; this will fail when actual policies are added unless the missing fields are populated.

**Integration test gaps surface after multi-lane merges:**

- Symptoms: Commit faa8f19 documents that merging 19 independent backlog branches surfaced real integration-level test gaps that single-task self-verify could not catch.
- Files: `tests/integration/test_registries_schema_independent.py`, `registries/INVENTORY.yaml`, `schemas/registry/INVENTORY.v1.schema.json`
- Trigger: Multi-lane merges where independent branches have schema/registry changes that conflict or overlap.
- Workaround: The specific gaps (INVENTORY schema missing, topology.yaml ambiguous schema lookup) were fixed in faa8f19 but indicate the test harness may not catch similar schema-registration issues.

## Security Considerations

**Credential bounds validator is security-critical (AT-110 probe):**

- Risk: `validators/drift/credential_bounds.py` implements AT-110 — six negative attempts to exercise the reconciler's own credential scope. Any PERMITTED result is a security incident. The module uses a Protocol with six `try_*()` methods and relies on correct return values from `FixtureCredential` and `LiveCredential` implementations.
- Files: `validators/drift/credential_bounds.py`, `reconciler/state/live_adapter.py`
- Current mitigation: The probe raises `SecurityIncident` immediately on any PERMITTED result, halting before further attempts or reconciliation. The module correctly distinguishes fixture mode (testing) from live mode (production). Test coverage exists for both modes.
- Recommendations: Continue treating any PERMITTED result as a hard stop. Ensure the six AT-110 attempt shapes (`try_actions_secret_write`, `try_environment_write`, `try_workflow_file_change`, `try_org_settings_change`, `try_records_write`, `try_layer_b_access`) remain in sync with spec 40.1 and spec 43. Add integration testing that exercises live-mode credential bounds after any token rotation.

**Repair guards enforce security invariants at import time:**

- Risk: `reconciler/repair/guards.py` audits the entire `reconciler.repair` package at import time to ensure: (1) every `Repair()` construction is preceded by a `permitted()` call, and (2) five absolute-refusal categories never appear as call shapes. A bug in the AST inspection could allow a forbidden repair to ship.
- Files: `reconciler/repair/guards.py`, `reconciler/repair/*.py`
- Current mitigation: Guards use pure AST inspection (no execution), so import-time failures don't run any repair code. Discovery is dynamic via `pkgutil.iter_modules`, so new repair classes are picked up automatically. Unit tests (`reconciler/tests/test_repair_guards.py`) verify both positive (guards pass) and negative (guards detect violations) cases.
- Recommendations: The hand-rolled AST inspection is brittle — a variable rename in a repair class or a minor syntax change could break guard detection. Consider adding a secondary check that imports each repair class and introspects its `repair()` method signature to ensure it calls `stricter.permitted()`. Document the AST patterns in a constraint comment in guards.py.

**Reconciler credential separation (two independent credentials):**

- Risk: The reconciler uses `GITHUB_TOKEN` for live reconciliation, while `validators/drift/verifier.py` uses `DRIFT_VERIFIER_TOKEN` as a second instrument. If the two tokens become confused (e.g., via environment variable collision or credential manager mixup), the verifier's independence is compromised.
- Files: `reconciler/state/live_adapter.py`, `validators/drift/verifier.py`, `validators/drift/credential_bounds.py`
- Current mitigation: Each module explicitly documents which token it reads (`GITHUB_TOKEN` vs `DRIFT_VERIFIER_TOKEN`). Credential bounds testing ensures the reconciler credential cannot reach certain surfaces.
- Recommendations: Add a pre-flight check in CI/CD that verifies both tokens are present and distinct (non-equal) before running any reconciliation or verification. Document the credential separation requirement in a top-level architecture document.

## Performance Bottlenecks

**Orphan detection framework processes 16 detector types sequentially:**

- Problem: `reconciler/orphans/__init__.py` and seven sibling modules (assets, dismissal, governance, ownership, prospective, types, plus one more) total ~654 lines of logic. The `run_group()` dispatcher calls detectors sequentially against a single `OrphanContext` loaded from disk. Prospective mode re-runs detectors for each login variation.
- Files: `reconciler/orphans/__init__.py`, `reconciler/orphans/assets.py`, `reconciler/orphans/governance.py`, `reconciler/orphans/ownership.py`, `reconciler/orphans/dismissal.py`, `reconciler/orphans/prospective.py`, `reconciler/orphans/types.py`
- Cause: No caching of OrphanContext between detector calls, and no memoization of computed properties (e.g., `is_inactive_login()` predicates re-computed for every orphan candidate).
- Improvement path: Profile the orphans CLI with `--fixture fixture-a` and measure time-per-detector. If fixture-a is small and latency is acceptable, defer optimization. If latency becomes a concern with larger fixtures, batch common computations (e.g., pre-compute departed/revoked login sets) and cache them in the context.

**Schema validation by independent test involves hand-rolled Draft-07 subset:**

- Problem: `tests/integration/test_registries_schema_independent.py` implements a Draft-07-subset validator from scratch (lines 98–200+) to avoid sharing the production validator's bugs. This includes nested schema resolution, `$ref` handling, and type checking.
- Files: `tests/integration/test_registries_schema_independent.py`
- Cause: Deliberate choice per spec 53.1 (second instrument independence), but adds runtime cost: every test invocation re-compiles the validator logic.
- Improvement path: Extract the independent validator to a loadable module (`validators/registry/draft07_subset.py`) that tests import. This avoids re-implementing the logic in each test run, though it does add a module that must be kept in sync with Draft-07 changes.

## Fragile Areas

**Reconciler comparator registry populated at import time:**

- Files: `reconciler/registry.py`, `reconciler/comparators/*.py`, `reconciler/cli.py`
- Why fragile: The registry (dicts `COMPARATORS` and `FAIL_CLASS`) is populated purely as a side-effect of importing `reconciler.comparators.*`. If a comparator module fails to import (parse error, missing dependency, circular import), the entire registry is silently incomplete. The `list` command in `reconciler/cli.py` enforces that every comparator has a matching fail-class entry, but this check runs after import succeeds.
- Safe modification: Before adding a new comparator, verify the module parses cleanly in isolation (`python -m py_compile`). Add unit tests for the new comparator that exercise both the success and failure paths. Verify that `reconciler list` shows the new comparator in the output.
- Test coverage: Gaps exist for circular imports between comparators (unlikely but not explicitly tested). No test covers what happens if a comparator module raises an exception at import time.

**Gap detection and replay expiries assume fixture-a's declared state is complete:**

- Files: `reconciler/gap/detect.py`, `reconciler/repair/expiry_revoke.py`
- Why fragile: `replay_expiries()` revokes expired assignments/exceptions without querying live state — it assumes the declared side (assignments, exceptions from the fixture) is authoritative. If an assignment exists in live state but not in declared state, it cannot be revoked during gap recovery.
- Safe modification: Document this assumption clearly in `replay_expiries()`'s docstring. Add a pre-gap check that compares declared-side assignments/exceptions counts against live state and warns if discrepancies exist.
- Test coverage: Tests exist for replay_expiries (reconciler/tests/test_repair_expiry.py) but they use fixtures with complete declared state. No test covers the scenario where declared state is missing an assignment that is live.

**Orphan dismissal logic uses weak predicate for "inactive login":**

- Files: `reconciler/orphans/dismissal.py`, `reconciler/orphans/__init__.py`
- Why fragile: `is_inactive_login()` returns `True` if login status is `departed` or `revoked`, but explicitly excludes `departing` (prospective). The predicate is shared across all 16 orphan detectors, so a change to this predicate affects all of them simultaneously. If a detector needs a different definition of "inactive" (e.g., including `departing`), it must override the predicate or re-implement the check.
- Safe modification: Add a new predicate (e.g., `is_inactive_or_departing_login()`) for detectors that need prospective handling, rather than modifying the shared predicate. Document which detectors use which predicate.
- Test coverage: Tests exist for dismissal (reconciler/tests/test_orphan_dismissal.py) but focus on the dismissal mechanism itself. No test covers prospective orphan detection against various login status values.

**Strict enforcement of repair permission checks via AST inspection:**

- Files: `reconciler/repair/guards.py`, `reconciler/repair/stricter.py`
- Why fragile: The guard system uses AST pattern matching to verify that `permitted()` is called before every `Repair()` construction. A minor refactor (extracting permission checks to a helper variable or wrapping them in a function) could break the pattern match without breaking the actual permission logic.
- Safe modification: When refactoring repair classes, run `reconciler/repair/guards.py` directly to re-audit the package. Add a comment in the refactored code explaining the guard requirement. Consider adding a secondary check that imports the repair class and verifies it has a `repair()` method.
- Test coverage: `reconciler/tests/test_repair_guards.py` tests that guards detect violations, but it patches AST inspection. No real-world end-to-end test verifies that a repair actually checks permissions before running.

## Test Coverage Gaps

**Orphan detection lacks isolated unit tests for each detector:**

- What's not tested: Individual orphan detectors (assets, governance, ownership, dismissal, prospective) are tested, but the integration between `load_context()` and each detector is not systematically covered. The test suite does not verify that each detector correctly identifies all 16 orphan types.
- Files: `reconciler/tests/test_orphan_*.py`, `reconciler/orphans/types.py`
- Risk: A change to the `OrphanContext` structure or the `is_inactive_login()` predicate could silently break one detector while others continue to pass. The 16 orphan types are defined in `types.py` but no test verifies that all 16 are detected at least once across the fixture.
- Priority: Medium — orphan detection is less critical than comparator drift detection, but a silent failure to detect an orphan type could leave responsibility gaps undetected.

**Repair operations lack end-to-end tests with live GitHub state:**

- What's not tested: The eight repair classes (codeowners_regen, escalation, expiry_revoke, label_sync, protection_reapply, records, team_sync, and the implicit write to check runs) are tested with fixtures and mocks, but no test exercises a real repair against a live test organization.
- Files: `reconciler/repair/*.py`, `reconciler/tests/test_repair_*.py`
- Risk: A bug in the repair logic (e.g., field name mismatch in the GitHub API call) could ship undetected because fixtures don't replicate the full GitHub API response shape. Mock objects may allow attributes that don't exist in reality.
- Priority: High — repairs are the system's means of correcting drift. A silent repair failure is worse than a loud detection failure.

**Reclassification logic has limited test coverage for edge cases:**

- What's not tested: `reconciler/reclassify.py` handles downward reclassification (to a lower-severity class) with `ReclassificationRefused` exceptions, but tests (if any exist) don't cover the full transition matrix (BLOCK → WARN → PASS and all invalid directions).
- Files: `reconciler/reclassify.py`, `reconciler/tests/test_*.py`
- Risk: A caller that attempts to reclassify a finding in an unexpected direction could raise an unhandled exception or produce a silent no-op.
- Priority: Low — reclassification is a narrow feature, but missing edge-case tests indicate it may not have been thoroughly validated.

## Scaling Limits

**Reconciler comparator registry has no size limit or performance monitoring:**

- Current capacity: The registry can hold an unlimited number of comparators. The test fixtures are small (fixture-a has ~140 lines of YAML).
- Limit: No measured limit, but as the number of comparators grows, the import-time registry population and the `reconciler run` command's per-comparator overhead (disk I/O, API calls to GitHub) will increase. With 20+ comparators running against an organization with 100+ repositories, execution time could grow from seconds to minutes.
- Scaling path: Implement optional comparator filtering (`reconciler run --only-comparator-id <id>`) to allow selective runs. Add per-comparator timing to the run output. Consider implementing comparator result caching to avoid re-fetching the same GitHub API response twice.

**Orphan detection scales with people + products + assets count:**

- Current capacity: Fixture-a has ~22 people, ~2 products, ~13 assets, and 16 orphan types = ~400 potential detections. The framework runs all detectors sequentially.
- Limit: With 1000+ people and 50+ products, the nested loop in some detectors (e.g., checking each person against each product) could become O(n²) and slow.
- Scaling path: Profile `reconciler orphans --fixture fixture-a` and measure scaling as fixture size increases. If latency becomes an issue, batch processing by orphan type or implement early-exit conditions (e.g., stop checking once one orphan is found for a slot).

## Dependencies at Risk

**PyYAML dependency used for all fixture loading:**

- Risk: All fixture loading in `reconciler/fixtures/verify.py`, `reconciler/orphans/__init__.py`, and dozens of tests use `yaml.safe_load()`. A vulnerability in PyYAML or a parse error in a fixture YAML file would break the entire system.
- Impact: If PyYAML becomes unmaintained or a critical vulnerability is discovered, pinned versions must be rotated quickly. Fixture files with accidental YAML syntax errors (e.g., trailing whitespace, invalid nesting) will fail at runtime.
- Migration plan: No alternative YAML parser is in use. Consider adopting a YAML schema validator (e.g., yamale) to catch syntax errors during CI/CD before they reach runtime.

**Protocol-based credential abstraction in validators/drift/credential_bounds.py is not enforced:**

- Risk: The `Credential` protocol defines six methods (`try_actions_secret_write`, etc.) that `FixtureCredential` and `LiveCredential` must implement. If a third credential implementation forgets one method, Python will raise an `AttributeError` at runtime (in the `probe()` function), not at class definition time.
- Impact: New credential types (e.g., for testing with a different CI/CD system) would need to manually verify they implement all six methods.
- Migration plan: Upgrade to Python 3.13+ and use `@runtime_checkable` protocols, or wrap the `probe()` call with a type check that verifies all six methods exist before calling the probe.

## Missing Critical Features

**Policy registry is not yet populated:**

- Problem: `registries/policies.yaml` is empty with just metadata. Per the docstring, this is waiting for Phase G2 to populate it from the rulebook, but downstream code that assumes policies exist will fail silently.
- Blocks: Any access-control rules that reference policies by ID, any reports or dashboards that show policy coverage, any reconciler comparators that validate policy conformance against actual runtime behavior.

**Orphan dismissal audit trail is not persisted:**

- Problem: When an orphan is dismissed via `reconciler/orphans/dismissal.py`, the decision is recorded in a finding but there is no durable log of who dismissed it, when, or why (other than the finding text itself).
- Blocks: Future audits to trace responsibility decisions, ability to undo dismissals, or to report dismissal metrics.

---

*Concerns audit: 2026-09-16*
