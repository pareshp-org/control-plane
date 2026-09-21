---
last_mapped_commit: c23a01076c25ff0b3f48404c5dbd702db1e8c9a1
last_mapped_at: 2026-09-16
---
# Testing Patterns

**Analysis Date:** 2026-09-16

## Test Framework

**Runner:**

- pytest [version in pyproject.toml: >=7.0]
- Config: `pytest.ini` and `pyproject.toml` [tool.pytest.ini_options]

**Assertion Library:**

- Standard Python `assert` statements
- pytest's advanced assertion rewriting handles detailed output
- pytest.raises() for exception testing

**Run Commands:**

```bash

# Run all tests

python -m pytest tests/ -v --tb=short

# Watch mode

# Not configured; use pytest-watch or run manually

# Coverage

python -m pytest tests/ --cov=. --cov-report=html

# With Makefile

make test  # Runs: python -m pytest tests/ -v --tb=short
```

## Test File Organization

**Location:**

- Tests co-located with source in `tests/` subdirectories: `reconciler/tests/`, `validators/drift/tests/`, `tools/provision/tests/`
- Alternative: `tests/` directory at repo root for integration tests: `tests/integration/conftest.py`
- Main test configuration via `pytest.ini` at repo root

**Naming:**

- Test files: `test_<module>.py` (e.g., `test_anchor.py`, `test_model.py`, `test_checkrun.py`)
- Test functions: `test_<behavior>()` (e.g., `test_the_first_ever_anchor_call_always_anchors_cleanly()`)
- Test classes: `Test<Name>` (if grouping tests, rare in this codebase)

**Structure:**

```
reconciler/
├── anchor.py
├── model.py
└── tests/
    ├── test_anchor.py
    ├── test_model.py
    └── test_checkrun.py

validators/drift/
├── assert_protection.py
└── tests/
    └── test_assert_protection.py
```

## Test Structure

**Suite Organization:**

Tests are flat functions in test modules, not grouped in classes. Each test file focuses on one module.

From `reconciler/tests/test_anchor.py`:

```python
"""L3-P5-08: records-repository head SHA anchor."""

from __future__ import annotations

from reconciler.anchor import Anchor, anchor
from reconciler.model import DriftClass, Level

def test_the_first_ever_anchor_call_always_anchors_cleanly():
    new_anchor, finding = anchor("sha-1", 10, None)
    assert new_anchor == Anchor(sha="sha-1", commit_count=10)
    assert finding is None

def test_a_head_that_simply_has_not_moved_anchors_cleanly():
    previous = Anchor(sha="sha-1", commit_count=10)
    new_anchor, finding = anchor("sha-1", 10, previous)
    assert finding is None
    assert new_anchor == previous
```

**Patterns:**

- **Module docstring:** Every test file begins with `"""L<N>-<FF>-<NN>: short description."""` naming the spec section
- **Setup:** Inline in test functions or via helper functions like `_finding()`, `_run()`, `_fake_declared()`
- **Teardown:** Via pytest fixtures with `yield` or test functions that clean up in `finally` blocks (rare)
- **Assertion:** Direct `assert` statements; no helper methods

From `reconciler/tests/test_checkrun.py`:

```python
def _finding(drift_class: DriftClass, scope: str = "beta") -> Finding:
    """Helper to construct test findings with default values."""
    return Finding(
        id=f"x:{scope}",
        comparator="x",
        scope=scope,
        drift_class=drift_class,
        level=Level.BLOCK if drift_class == DriftClass.BLOCKING else Level.WARN,
        evidence="test",
        first_seen="2026-08-27T00:00:00Z",
    )

def test_one_blocking_finding_yields_failure_conclusion():
    result = publish("beta", [_finding(DriftClass.BLOCKING)])
    assert result.conclusion == "failure"
    assert result.name == CHECK_NAME
```

## Mocking

**Framework:** No external mocking library; uses inline fake/mock classes

**Patterns:**

Fakes are defined as simple classes in test functions:

```python
class FakeActual:
    def branch_protection(self, repo):
        return dict(_TEMPLATE)

declared = _fake_declared({"solo": {}})
findings, compared = compare(declared, FakeActual(), date(2026, 8, 27))
```

Or as minimal Protocol implementations:

```python
class _FakeClient:
    def __init__(self):
        self.calls = []

    def create_check_run(self, *, repo, name, conclusion):
        self.calls.append((repo, name, conclusion))

# Then in test:

client = _FakeClient()
result = publish("beta", [_finding(DriftClass.BLOCKING)], dry_run=False, client=client)
assert client.calls == [("beta", CHECK_NAME, "failure")]
```

**What to Mock:**

- External system adapters (GitHub API, file storage, databases)
- Dependencies injected via parameters (see `client: CheckRunClient | None` in `reconciler.checkrun.publish()`)
- Comparator sources (actual state, declared state)

**What NOT to Mock:**

- Core business logic (e.g., the function under test always calls real validators)
- Data structures and models (`Finding`, `Anchor`, etc.)
- Pure functions (`_canonical()`, `_diff()`)
- Test-only helpers (they're lightweight and deterministic)

## Fixtures and Factories

**Test Data:**

Fixture state loaded from disk. From `validators/drift/tests/test_assert_protection.py`:

```python
@pytest.fixture(autouse=True)
def _empty_registry(monkeypatch):
    monkeypatch.setattr(verifier, "ASSERTIONS", {"protection_matches_template": check})
    yield
```

Helper functions construct test objects:

```python
def _finding(drift_class: DriftClass, scope: str = "beta") -> Finding:
    return Finding(
        id=f"x:{scope}",
        comparator="x",
        scope=scope,
        drift_class=drift_class,
        level=Level.BLOCK if drift_class == DriftClass.BLOCKING else Level.WARN,
        evidence="test",
        first_seen="2026-08-27T00:00:00Z",
    )

def _run(findings):
    return RunRecord(
        run_id="R1",
        started_at="2026-08-27T00:00:00Z",
        finished_at="2026-08-27T00:01:00Z",
        status="OK",
        findings=findings,
        comparison_counts={"write_freshness": 3},
        canary_found=True,
        external_cause=None,
    )
```

**Location:**

- Fixtures in test files: simple `@pytest.fixture` functions in the same file as tests
- Shared conftest: `tests/integration/conftest.py` for integration-level setup
- Named fixture state: Loaded from `fixture-a`, `fixture-b` directories by test constructors (e.g., `VerifierState("fixture-a")`)

From `tests/integration/conftest.py`:

```python
"""pytest configuration for integration tests"""
import sys
from pathlib import Path

# Add implementation root to Python path so validators.registry can be imported

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
```

## Coverage

**Requirements:** Not enforced in CI; coverage is measured but optional

**View Coverage:**

```bash
python -m pytest tests/ -v --cov=reconciler --cov=validators --cov-report=html

# Open htmlcov/index.html in a browser

```

**Coverage Conventions:**

- pytest-cov optional dependency: listed in `pyproject.toml` under `[project.optional-dependencies] dev`
- No `.coveragerc` config; uses defaults
- Internal helper functions (`_canonical()`, `_diff()`, etc.) and tests are all expected to be covered
- Generated or test-only code may be excluded with `# pragma: no cover` if needed (not observed in this codebase)

## Test Types

**Unit Tests:**

- Scope: One function or class at a time
- Approach: Test the public API of a module with inline fakes for dependencies
- Example: `test_the_first_ever_anchor_call_always_anchors_cleanly()` tests `anchor()` in isolation
- No real I/O, no database, no network

**Integration Tests:**

- Scope: Multiple modules working together, often with fixture data
- Approach: Use real fixture state from disk (e.g., `fixture-a/` directories)
- Location: `tests/integration/` or ad-hoc in module test files
- Example: `test_fixture_a_fails_because_beta_disables_code_owner_review()` in `validators/drift/tests/test_assert_protection.py` loads actual fixture state and verifies the assertion behaves correctly

**E2E Tests:**

- Framework: Not used
- Alternative: Integration tests with fixture state serve as end-to-end verification

## Common Patterns

**Async Testing:**
Not used; no async code in the codebase. Tests are synchronous.

**Error Testing:**

```python
def test_invalid_name_raises_before_anything_else():
    with pytest.raises(InvalidCheckName):
        publish("beta", [], name="some-other-check")
```

```python
def test_second_acknowledge_raises_rather_than_overwrites():
    finding = _finding(DriftClass.AMBER)
    acked = acknowledge(finding, by="lead-1", at="2026-08-27T12:00:00Z")
    with pytest.raises(AlreadyAcknowledged):
        acknowledge(acked, by="dev-1", at="2026-08-27T13:00:00Z")
```

**Behavioral Testing:**

Test functions are named after BEHAVIOR, not implementation:

- ✅ `test_dry_run_is_the_default_and_makes_no_client_call()`
- ✅ `test_one_blocking_finding_yields_failure_conclusion()`
- ✅ `test_a_head_that_simply_has_not_moved_anchors_cleanly()`

Not after methods:

- ❌ `test_publish()`
- ❌ `test_anchor()`

**Invariant Testing:**

Tests verify that invariants are maintained:

```python
def test_module_performs_no_write_to_the_records_repository_or_the_drift_events_store():
    """Verify that reconciler.anchor has no I/O side effects per spec requirement."""
    import inspect

    import reconciler.anchor as anchor_module

    source = inspect.getsource(anchor_module)
    for banned_prefix in ("records/", "events/"):
        assert banned_prefix not in source
    for banned_call in ("open(", "Path(", ".write_text(", ".write(", "write_bytes"):
        assert banned_call not in source
```

**Spec-Driven Testing:**

Every test references the spec it validates:

```python
def test_checked_counts_every_repository_examined():
    """Mirrors reconciler.comparators.branch_protection's own 'every
    repository is read even after the first bad one is found' rule."""
    result = check(VerifierState("fixture-a"))
    assert result.checked == len(VerifierState("fixture-a").repos())
```

## Test Discovery

**Configuration:**

From `pytest.ini`:

```
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

- Test paths: `tests/` directory and any `tests/` subdirectories in modules (auto-discovered)
- File pattern: `test_*.py`
- Class pattern: `Test*` (rarely used; most tests are functions)
- Function pattern: `test_*`
- Command-line options: Always `-v` (verbose) and `--tb=short` (short traceback format)

**Running Tests:**

```bash

# All tests

make test

# Specific test file

python -m pytest reconciler/tests/test_anchor.py -v --tb=short

# Specific test function

python -m pytest reconciler/tests/test_anchor.py::test_the_first_ever_anchor_call_always_anchors_cleanly -v

# With coverage

python -m pytest --cov=reconciler --cov=validators -v --tb=short
```

---

*Testing analysis: 2026-09-16*
