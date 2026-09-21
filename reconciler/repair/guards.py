"""L3-P6-09: prohibited-repair guards (spec 53.3, transcribed verbatim:
"never modifies production runtime configuration, never modifies data,
and never rotates or writes secrets"; spec 40.1; AT-110).

`reconciler/repair/__init__.py`'s module docstring names the contract
every Phase 6 class in this package is built against: it "asks
stricter.py's `permitted()` for permission before writing anything,
and it produces a `Repair`... No repair class may bypass any of the
three - reconciler/repair/guards.py enforces the first at import time
once it lands." This module is that enforcement.

Two independent things `audit_package()` asserts about every module it
finds:

1. **Permission precedes the write.** Every `Repair(...)` construction
   in a function is preceded, within that same function, by a call
   named (bare or via an attribute, e.g. `stricter.permitted(...)`)
   `permitted` - the one gate every shipped class calls before
   deciding whether to produce a `Repair` at all.
2. **The five absolute refusals never appear as a call shape.** Spec
   53.3's and AT-110's prohibited writes - a GitHub Actions secret
   write, an environment write, a workflow-file change, an
   organisation-settings change, and a `records/**` write - are
   refused unconditionally in this package, regardless of direction or
   permission. (AT-110's sixth attempt, Layer B access, has no call
   shape to guard against here at all:
   `validators/drift/credential_bounds.py`'s own
   `FixtureCredential.try_layer_b_access` docstring makes the same
   point - Layer B is off GitHub entirely, so a module in this
   GitHub-scoped package has no network path to it to write a guard
   against.)

Both checks are pure source/AST inspection. This module never executes
a byte of the code it audits beyond a plain `import` (needed only to
read `inspect.getsource()` off the loaded module) - a class that
raises at import time does not stop the audit of *other* classes, and
nothing here calls into any repair class's `repair()` function.

**Discovery is dynamic, not a hand-maintained list** (task acceptance
1). `audit_package()` walks every submodule of `reconciler.repair`
with `pkgutil.iter_modules` - the same package `enablement.py`'s
registry describes, but nothing here imports or reads that registry;
this module answers the "is it a repair class?" question the same way
`reconciler/repair/__init__.py` itself defines the term - "every
repair class... produces a `Repair`" - by keeping only the modules
whose source constructs at least one `Repair(...)`. `stricter.py`
(defines `permitted()`, never calls it), `enablement.py` (a registry,
constructs no `Repair`) and `escalation.py` (emits a
`RepairEscalation`, not a `Repair`) are excluded by that same rule,
with no module named anywhere in this file. A sixth class added under
`reconciler/repair/` later, by construction, is picked up the next
time `audit_package()` runs.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import pkgutil
import re
from dataclasses import dataclass, field

# spec 53.3's absolute-refusal categories, plus AT-110's shape for
# each (validators/drift/credential_bounds.py's ATTEMPT_ORDER, minus
# layer_b_access - see module docstring). A call's identifier tokens
# (see `_tokens()`) must contain at least one of these mutating-verb
# tokens *and* every token of one alternative below to be flagged -
# a read-shaped call ("get_secret", "list_environments") never
# matches on its own.
_MUTATING_VERBS: frozenset[str] = frozenset(
    {
        "write",
        "writes",
        "written",
        "set",
        "rotate",
        "rotates",
        "create",
        "creates",
        "delete",
        "deletes",
        "remove",
        "removes",
        "patch",
        "patches",
        "put",
        "post",
        "update",
        "updates",
        "apply",
        "applies",
        "revoke",
        "revokes",
        "change",
        "changes",
    }
)

# Each key is one AT-110 / spec 53.3 prohibited-write category; each
# value is a tuple of token sets, any one of which - combined with a
# mutating verb above - is enough to flag a call.
_CATEGORY_TOKENS: dict[str, tuple[frozenset[str], ...]] = {
    "actions_secret_write": (frozenset({"secret"}), frozenset({"secrets"})),
    "environment_write": (frozenset({"environment"}), frozenset({"environments"})),
    "workflow_file_change": (frozenset({"workflow"}), frozenset({"workflows"})),
    "org_settings_change": (
        frozenset({"org", "settings"}),
        frozenset({"organisation", "settings"}),
        frozenset({"organization", "settings"}),
        frozenset({"orgs"}),
    ),
    "records_write": (frozenset({"records"}),),
}

_CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_WORD = re.compile(r"[a-z]+")


def _tokens(text: str) -> frozenset[str]:
    """Lower-case word tokens out of an identifier or a whole call's
    source text. Snake_case, camelCase, hyphens and path separators
    all split into separate tokens - "rotate_secret", "rotateSecret"
    and "/orgs/{org}/actions/secrets" all yield a "secret"-shaped
    token distinct from the verb around it."""
    spaced = _CAMEL_BOUNDARY.sub("_", text)
    return frozenset(_WORD.findall(spaced.lower()))


def _call_name(call: ast.Call) -> str:
    """The dotted callee name of a Call node - "permitted" for a bare
    call, "stricter.permitted" for an attribute call, "" when the
    callee is neither a Name nor an Attribute chain (e.g. a call on a
    call's return value)."""
    parts: list[str] = []
    func = call.func
    while isinstance(func, ast.Attribute):
        parts.append(func.attr)
        func = func.value
    if isinstance(func, ast.Name):
        parts.append(func.id)
    else:
        return ""
    return ".".join(reversed(parts))


def _is_permitted_call(call: ast.Call) -> bool:
    name = _call_name(call)
    return name == "permitted" or name.endswith(".permitted")


def _is_repair_construction(call: ast.Call) -> bool:
    name = _call_name(call)
    return name == "Repair" or name.endswith(".Repair")


def _forbidden_categories(tokens: frozenset[str]) -> list[str]:
    if not (tokens & _MUTATING_VERBS):
        return []
    return [
        category
        for category, alternatives in _CATEGORY_TOKENS.items()
        if any(required <= tokens for required in alternatives)
    ]


def _calls_by_scope(tree: ast.AST) -> list[list[ast.Call]]:
    """Group every Call node in `tree` by the innermost function (def
    or async def) it textually appears in; calls made at module level,
    outside any function, form their own group. Grouping - rather than
    a single flat list - is what lets the ordering check in
    `_ordering_violations()` below reason about one function's own
    `permitted()` call gating that same function's own `Repair(...)`
    construction, and not, say, one function's `permitted()` call
    being credited to a different function's write."""
    scopes: dict[object, list[ast.Call]] = {}

    def visit(node: ast.AST, scope_key: object) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                visit(child, child)
                continue
            if isinstance(child, ast.Call):
                scopes.setdefault(scope_key, []).append(child)
            visit(child, scope_key)

    visit(tree, None)
    return list(scopes.values())


def _ordering_violations(tree: ast.AST) -> list[str]:
    violations: list[str] = []
    for calls in _calls_by_scope(tree):
        ordered = sorted(calls, key=lambda c: (c.lineno, c.col_offset))
        seen_permitted = False
        for call in ordered:
            if _is_permitted_call(call):
                seen_permitted = True
                continue
            if _is_repair_construction(call) and not seen_permitted:
                violations.append(
                    f"line {call.lineno}: Repair(...) is constructed with no preceding "
                    "permitted() call in its own function"
                )
    return violations


def _forbidden_write_violations(tree: ast.AST, source: str) -> list[str]:
    violations: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        segment = ast.get_source_segment(source, node) or _call_name(node)
        categories = _forbidden_categories(_tokens(segment))
        for category in categories:
            violations.append(f"line {node.lineno}: call shaped like a prohibited {category} ({segment!r})")
    return violations


def _constructs_repair(tree: ast.AST) -> bool:
    return any(isinstance(node, ast.Call) and _is_repair_construction(node) for node in ast.walk(tree))


@dataclass(frozen=True)
class ModuleAudit:
    """One module's audit result. `violations` is empty exactly when
    the module passes both checks described in this module's
    docstring."""

    name: str
    violations: tuple[str, ...] = field(default_factory=tuple)


def audit_source(name: str, source: str) -> ModuleAudit:
    """Run both guard checks over `source` (a module's Python text)
    without importing or executing it. Exposed separately from
    `audit_package()` so a test can exercise a deliberately
    non-compliant module's source directly, without writing a sixth
    file into `reconciler/repair/**` and disturbing the five-class
    count `audit_package()` reports."""
    tree = ast.parse(source, filename=name)
    violations = _ordering_violations(tree) + _forbidden_write_violations(tree, source)
    return ModuleAudit(name=name, violations=tuple(violations))


def audit_package(package_name: str = "reconciler.repair") -> list[ModuleAudit]:
    """Enumerate every submodule of `package_name` with
    `pkgutil.iter_modules` (no hard-coded module list - see module
    docstring), keep only the ones whose source constructs at least
    one `Repair(...)` (this package's own definition of "is a repair
    class"), and audit each of those with `audit_source()`."""
    package = importlib.import_module(package_name)
    results: list[ModuleAudit] = []

    for module_info in sorted(pkgutil.iter_modules(package.__path__), key=lambda m: m.name):
        if module_info.ispkg:
            # A subpackage (e.g. a future reconciler/repair/tests/) is
            # not itself a repair-class module.
            continue
        full_name = f"{package_name}.{module_info.name}"
        module = importlib.import_module(full_name)
        source = inspect.getsource(module)
        tree = ast.parse(source, filename=full_name)
        if not _constructs_repair(tree):
            continue
        violations = _ordering_violations(tree) + _forbidden_write_violations(tree, source)
        results.append(ModuleAudit(name=full_name, violations=tuple(violations)))

    return results


if __name__ == "__main__":
    audits = audit_package()
    for audit in audits:
        status = "OK" if not audit.violations else "VIOLATIONS"
        print(f"{status} {audit.name}")
        for violation in audit.violations:
            print(f"  - {violation}")
    print(f"modules {len(audits)} violations {sum(1 for a in audits if a.violations)}")
