---
last_mapped_commit: c23a01076c25ff0b3f48404c5dbd702db1e8c9a1
last_mapped_at: 2026-09-16
---
# Coding Conventions

**Analysis Date:** 2026-09-16

## Naming Patterns

**Files:**

- Snake case: `reconciler/checkrun.py`, `reconciler/tests/test_anchor.py`
- Tool/script files use hyphens or underscores: `tools/provision/change_role.py`, `tools/evidence/apply-production-gates.py`
- Test files: `test_*.py` (e.g., `reconciler/tests/test_model.py`, `validators/drift/tests/test_assert_protection.py`)

**Functions:**

- Snake case throughout: `def anchor()`, `def compare()`, `def _descends()` (underscore prefix for internal helpers)
- Private/internal functions prefixed with `_`: `_canonical()`, `_diff()`, `_get()`
- Public API functions exported from modules without underscore prefix

**Variables:**

- Snake case for local variables and instance attributes: `records_head_sha`, `ancestor_shas`, `new_anchor`
- Parameters use snake case: `drift_class`, `is_security_or_prod_env`

**Types:**

- Classes: PascalCase: `Finding`, `Anchor`, `DriftClass`, `CheckRunClient`
- Enums: PascalCase with UPPER_CASE members: `class DriftClass(str, Enum)` with `GREEN`, `AMBER`, `RED`, `BLOCKING`
- Type aliases use existing patterns

**Constants:**

- UPPER_CASE for module-level constants: `CHECK_NAME`, `RESPONSE_TIME`, `BLOCKS_WORK`
- Data structures as constants at module level: `CONFIGURE_ITEMS`, `CREATE_PRODUCT_MANUAL_STEPS`
- In dataclasses, fields are lowercase: `sha: str`, `commit_count: int`

## Code Style

**Formatting:**

- No explicit formatter configured (no .flake8, .pylintrc, or black config found)
- Default Python conventions observed: 4-space indentation, PEP 8 line length
- Import statements use `from __future__ import annotations` at the top of every file

**Linting:**

- Makefile target `make lint` runs `python -m py_compile` on key files
- Entry point: `validators/registry/cli.py` and `validators/registry/rules/registry.py` are checked
- No strict linter config enforced; relies on manual review

## Import Organization

**Order:**

1. Future imports: `from __future__ import annotations` (always first)
2. Standard library: `import json`, `from dataclasses import dataclass`, `import inspect`
3. Third-party: `import pytest`, `import pyyaml`, `import jsonschema`
4. Local/relative: `from reconciler.model import Finding`, `from validators.drift.verifier import assertion`

**Path Aliases:**

- No path aliases configured; absolute imports from repo root (e.g., `from reconciler.model import Finding`)
- Local modules imported relative to codebase root, not relative paths

**Example from `reconciler/anchor.py`:**

```python
from __future__ import annotations

from dataclasses import dataclass

from reconciler.model import DriftClass, Finding, Level
```

## Error Handling

**Patterns:**

- Custom exception classes defined at module level with clear docstrings:
  ```python
  class InvalidCheckName(ValueError):
      """Raised when asked to publish under any name other than CHECK_NAME.
      
      Spec 40.1: "the reconciler credential additionally holds check-run
      write on product repositories, used for exactly one named check."
      """
  ```

- Exceptions document both WHEN they're raised and WHY:
  ```python
  class NonDescendantHead(RuntimeError):
      """Not raised by `anchor()` itself — `anchor()` reports a
      non-descendant head as a Finding, never a crash, so the run that
      discovers it can still complete and surface the finding (spec 53.1:
      a reconciler that cannot report drift is itself the failure).
      """
  ```

- Raise early with clear messages:
  ```python
  if name != CHECK_NAME:
      raise InvalidCheckName(
          f"the publisher may emit only {CHECK_NAME!r} (spec 40.1: "
          f"'exactly one named check'); got {name!r}"
      )
  ```

- Return results tuples instead of raising when errors are expected business logic:
  ```python
  def anchor(...) -> tuple[Anchor, Finding | None]:
      """Returns `(new_anchor, finding)` — `finding` is `None` on a clean
      anchor, or a Blocking/ESCALATE `Finding` naming the non-descendant
      head. The new anchor is returned either way..."""
  ```

- Use `SystemExit` for script termination errors (in metrics/tools):
  ```python
  raise SystemExit("ATTN ERROR unsupported-rounding-order:%s" % order)
  ```

## Logging

**Framework:** None configured; uses standard Python `print()` for CLI output

**Patterns:**

- CLI output captured in tests with `io.StringIO()` and `contextlib.redirect_stdout()`
- From `reconciler/tests/test_cli.py`:
  ```python
  buf = io.StringIO()
  with contextlib.redirect_stdout(buf):
      code = main(argv)
  ```

- Structured output format for check results: `VERIFY <id> result=<pass|fail> checked=<count>`

## Comments

**When to Comment:**

- Comments explain SPEC REFERENCES, not code flow:
  ```python
  # Transcribed cell for cell from the spec 53.4 table.
  RESPONSE_TIME: dict[DriftClass, str | None] = {
      DriftClass.GREEN: None,
      DriftClass.AMBER: "next_planning_cycle_h2",
      ...
  }
  ```

- Comments explain CONSTRAINTS and INVARIANTS:
  ```python
  # Boolean fields where True is the stricter setting.
  _STRICTER_WHEN_TRUE = (...)
  
  # Boolean fields where False is the stricter setting.
  _STRICTER_WHEN_FALSE = (...)
  ```

- Comments explain WHY a field or function exists:
  ```python
  # D107: "a head that does not descend from the last anchored SHA is
  # proof of rewriting rather than evidence of it" — such a head is
  # Blocking drift at Level 5...
  ```

- Inline comments are minimal; docstrings carry the explanation

**Docstrings:**

Every module has a docstring explaining:

1. The spec section it implements (e.g., "L3-P5-03")
2. The exact rule or requirement
3. Edge cases and special behavior

From `validators/drift/assert_protection.py`:

```python
"""L3-P5-03: verifier assertion B — branch protection and ruleset JSON
match the committed template (spec 53.1: "that branch protection and
ruleset JSON match the committed template"; §11.3).

Registers assertion id ``protection_matches_template``. For every
repository the verifier's own state knows about, this byte-normalises
the actual branch-protection JSON...
"""
```

Every function has a docstring explaining:

- Preconditions (what the caller must ensure)
- Postconditions (what the function guarantees)
- Special behavior or side effects
- Return value meaning

From `reconciler/anchor.py`:

```python
def anchor(
    records_head_sha: str,
    commit_count: int,
    previous_anchor: Anchor | None,
    *,
    ancestor_shas: frozenset[str] = frozenset(),
) -> tuple[Anchor, Finding | None]:
    """Anchor `records_head_sha`/`commit_count` as this run's record.
    
    `previous_anchor` is `None` only for the very first anchor a
    reconciler ever records — there is nothing to check descent against
    yet, so the first call always anchors cleanly. On every later call,
    `ancestor_shas` must be the ancestry set described in this module's
    docstring...
    
    Returns `(new_anchor, finding)` — `finding` is `None` on a clean
    anchor, or a Blocking/ESCALATE `Finding` naming the non-descendant
    head. The new anchor is returned either way: a broken chain is
    itself worth anchoring, so the next run has something to compare
    against...
    """
```

## Function Design

**Size:** 

- Functions are concise: 10-30 lines typical
- Complex logic extracted to smaller helpers (e.g., `_descends()`, `_canonical()`, `_diff()`)
- Helpers prefixed with `_` to mark them as internal

**Parameters:**

- Use keyword-only parameters for optional/configurable behavior: `*, ancestor_shas=frozenset()`
- Type hints always present: `records_head_sha: str`, `ancestor_shas: frozenset[str]`
- Default parameters documented in docstring

**Return Values:**

- Explicitly typed in function signature: `-> tuple[Anchor, Finding | None]`
- Use tuples for multiple return values
- Return dataclass instances or frozen dataclasses for structured results
- Functions return results rather than raising when the condition is expected

## Module Design

**Exports:**

- Public API functions and classes are not prefixed with underscore
- Internal helpers prefixed with `_`
- Module docstring documents what the module exports and how to use it
- From `reconciler/comparators/__init__.py`:
  ```python
  """Every module in this package registers exactly one comparator with
  reconciler.registry.comparator and exposes one function:
  
      compare(declared, actual, as_of) -> tuple[list[Finding], int]
  """
  ```

**Barrel Files:**

- Package `__init__.py` files document the package's role and interface
- No import statements in `__init__.py` files; they're documentation only
- From `reconciler/comparators/__init__.py`: Pure docstring, no imports

**Data Structures:**

- Use frozen dataclasses for immutable data: `@dataclass(frozen=True)`
- Example from `reconciler/model.py`:
  ```python
  @dataclass(frozen=True)
  class Finding:
      """One drift finding produced by a comparator's compare()."""
      
      id: str
      comparator: str
      scope: str
      drift_class: DriftClass
      level: Level
      evidence: str
      first_seen: str
      acknowledged_by: str | None = None
      acknowledged_at: str | None = None
      external_cause: str | None = None
      gap_window: bool = False
  ```

- Frozen dataclasses prevent accidental mutation and make intent clear

---

*Convention analysis: 2026-09-16*
