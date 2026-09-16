"""The comparator registry (spec 53.1; consumed by L3-P1-19's fail-closed matrix).

Every comparator module under reconciler/comparators/ registers itself
here with the @comparator decorator, declaring both its string id and
the DriftClass that governs what happens when the comparator itself
cannot execute (L3-P1-19, spec 64.2): a BLOCKING/RED comparator fails
closed - an execution failure becomes a Blocking finding rather than a
silent skip; an AMBER/GREEN comparator fails open with an alert.

COMPARATORS and FAIL_CLASS are populated purely as an import-time side
effect of loading reconciler/comparators/*.py - see cli.py's
_load_comparators() for the discovery step that makes this happen. This
module defines the registration mechanism only; it holds no comparator
logic itself.
"""

from __future__ import annotations

from typing import Callable

from reconciler.model import DriftClass, Finding

CompareFn = Callable[..., "tuple[list[Finding], int]"]

# comparator id -> its compare(declared, actual, as_of) function.
COMPARATORS: dict[str, CompareFn] = {}

# comparator id -> the DriftClass governing its fail-open/fail-closed
# behaviour on an execution failure (L3-P1-19). Every entry in
# COMPARATORS must have a matching entry here - reconciler.cli's `list`
# command enforces that (spec 64.2: "Unclassified controls fail CI").
FAIL_CLASS: dict[str, DriftClass] = {}


def comparator(comparator_id: str, *, fail_class: DriftClass) -> Callable[[CompareFn], CompareFn]:
    """Register `fn` under `comparator_id` with its fail-mode class.

    Raises ValueError on a duplicate id - a comparator id collision is a
    programming error (two modules claiming the same registry slot),
    never a runtime condition to paper over silently.
    """

    if not isinstance(fail_class, DriftClass):
        raise TypeError(f"fail_class must be a DriftClass, got {fail_class!r}")

    def _register(fn: CompareFn) -> CompareFn:
        if comparator_id in COMPARATORS:
            raise ValueError(f"comparator id {comparator_id!r} is already registered")
        COMPARATORS[comparator_id] = fn
        FAIL_CLASS[comparator_id] = fail_class
        return fn

    return _register
