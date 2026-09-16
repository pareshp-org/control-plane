"""L3-P6-01: the stricter-only predicate and its proof suite (spec 53.3
verbatim; spec 101 invariant 81; AT-033).

Invariant 81: "Auto-repair may only move the system toward the
declared, stricter state." Spec 53.3 gives the rule and its four
absolute refusals: a repair class may write only when it moves actual
toward declared *and* declared is at least as restrictive as actual;
it may never touch production runtime configuration, data, or secrets
(regardless of direction), and it may never loosen any control.

`permitted()` is the single predicate every repair class in this
package must call before writing anything (asserted at import time by
reconciler/repair/guards.py, L3-P6-09). It takes one control's
declared and actual value plus a `control_kind` tag and returns
`(True, "")` only when both halves of the rule hold; otherwise it
returns `(False, reason)`.

Two shapes of control need a different reading of "stricter" than a
plain security toggle:

* **Whitelist/membership controls** (`NO_GRADIENT_KINDS`, e.g.
  `team_membership`, `label_and_board_field_set`) have no
  more-permissive/less-permissive axis to rank - membership in a
  registry-declared set is either right or wrong, not graduated. For
  these, the declared registry is definitionally the authoritative
  correct state (spec 26.4's registries are the human-governed
  decision; the repair only re-applies it), so moving toward declared
  - in *either* direction, adding a declared holder missing from a
  Team or removing an actual member holding no declared assignment -
  satisfies invariant 81 by construction. This is a deliberate,
  narrow exemption from the graduated-strictness comparison below, not
  a bypass of the rule: it still refuses every absolute-refusal
  category, and it is still gated by enablement (L3-P6-02) and audited
  by guards.py like every other repair.
* Everything else (booleans, numbers, lists, and dicts built from
  them, e.g. a branch-protection configuration) is ranked by
  `_stricter_or_equal()` below.
"""

from __future__ import annotations

from typing import Any

from reconciler.model import Level

# spec 53.3's three category-based absolute refusals. The fourth
# absolute refusal named by spec 53.3 - "any control the repair would
# loosen" - is not a fixed category: every control_kind not listed
# here is still subject to the stricter-or-equal check below, which
# refuses a loosening move regardless of what the control is.
ABSOLUTE_REFUSAL_KINDS = frozenset({"production_runtime_config", "data", "secret"})

# See the module docstring: no meaningful strictness gradient exists
# for these control kinds, so `permitted()` treats "moves toward
# declared" as sufficient on its own. `codeowners_content` joins this
# set for the same reason as `team_membership`: the generator this
# lane's provisioning path and Phase-6 repair share
# (tools.provision.codeowners.generate) already refuses - by raising,
# before it ever returns a string - to produce content that would
# introduce a machine identity (L3-P4-02); a call that gets this far
# already carries human-only, declared-derived text, so there is no
# separate loosening direction left to guard against here.
NO_GRADIENT_KINDS = frozenset({"team_membership", "label_and_board_field_set", "codeowners_content"})

# Boolean fields where True means "more permissive" rather than "more
# protected" - the default polarity (True = stricter, used for
# security toggles such as require_code_owner_reviews) is inverted for
# these specific branch-protection-style fields.
_LOOSER_WHEN_TRUE_FIELDS = frozenset({"allow_force_pushes", "allow_deletions", "custom_branch_policies"})


def _bool_stricter_or_equal(declared: bool, actual: bool, field: str | None) -> bool:
    def rank(value: bool) -> int:
        if field in _LOOSER_WHEN_TRUE_FIELDS:
            return 0 if value else 1
        return 1 if value else 0

    return rank(declared) >= rank(actual)


def _num_stricter_or_equal(declared: float, actual: float) -> bool:
    # A higher threshold (more required approvals, a longer window) is
    # the stricter reading for every numeric control this lane knows
    # about; no numeric control here runs the other way.
    return declared >= actual


def _list_stricter_or_equal(declared: list | tuple, actual: list | tuple) -> bool:
    # Stricter means "requires everything actual already required, and
    # possibly more" - actual's requirements must be a subset of
    # declared's. Dropping a required context to make a repository
    # green is exactly the loosening this refuses.
    return set(actual) <= set(declared)


def _dict_stricter_or_equal(declared: dict, actual: dict) -> bool:
    for key in sorted(set(declared) | set(actual)):
        d, a = declared.get(key), actual.get(key)
        if d == a:
            continue
        if isinstance(d, dict) and isinstance(a, dict):
            if not _dict_stricter_or_equal(d, a):
                return False
        elif isinstance(d, bool) and isinstance(a, bool):
            if not _bool_stricter_or_equal(d, a, key):
                return False
        elif (
            isinstance(d, (int, float))
            and isinstance(a, (int, float))
            and not isinstance(d, bool)
            and not isinstance(a, bool)
        ):
            if not _num_stricter_or_equal(d, a):
                return False
        elif isinstance(d, (list, tuple)) and isinstance(a, (list, tuple)):
            if not _list_stricter_or_equal(d, a):
                return False
        else:
            # Mismatched or unrecognised shapes for the same key: this
            # predicate refuses rather than guesses at a rule.
            return False
    return True


def permitted(declared: Any, actual: Any, control_kind: str) -> tuple[bool, str]:
    """Return (True, "") only when the repair moves actual toward
    declared *and* declared is at least as restrictive as actual for
    `control_kind`. Otherwise return (False, reason)."""

    if control_kind in ABSOLUTE_REFUSAL_KINDS:
        return False, (
            f"{control_kind!r} is one of spec 53.3's three category-based absolute "
            "refusals (production runtime configuration, data, secrets) - never "
            "subject to auto-repair, regardless of direction"
        )

    if declared == actual:
        return False, "declared and actual already match; there is nothing to repair"

    if control_kind in NO_GRADIENT_KINDS:
        # See the module docstring: for a whitelist/membership-shaped
        # control, declared *is* the stricter state by definition.
        return True, ""

    if isinstance(declared, dict) and isinstance(actual, dict):
        stricter = _dict_stricter_or_equal(declared, actual)
    elif isinstance(declared, bool) and isinstance(actual, bool):
        stricter = _bool_stricter_or_equal(declared, actual, None)
    elif (
        isinstance(declared, (int, float))
        and isinstance(actual, (int, float))
        and not isinstance(declared, bool)
        and not isinstance(actual, bool)
    ):
        stricter = _num_stricter_or_equal(declared, actual)
    elif isinstance(declared, (list, tuple)) and isinstance(actual, (list, tuple)):
        stricter = _list_stricter_or_equal(declared, actual)
    else:
        return False, (
            f"no stricter-only rule is defined for {type(declared).__name__} values "
            f"under control_kind {control_kind!r}; refusing rather than guessing at one"
        )

    if stricter:
        return True, ""
    return False, (
        "actual is stricter than declared for this control; reconciliation raises "
        "this for human review and never relaxes it (AT-033)"
    )


def classify_level(declared: Any, actual: Any, control_kind: str) -> Level:
    """The spec 53.2 response level that follows from `permitted()`'s
    verdict for this (declared, actual, control_kind) triple: DETECT
    when there is no drift to act on, AUTO_REPAIR when the repair is
    permitted, and WARN otherwise - including the AT-033
    actual-stricter-than-declared case, which is raised for human
    judgement and never turned into a repair."""
    if declared == actual:
        return Level.DETECT
    ok, _ = permitted(declared, actual, control_kind)
    return Level.AUTO_REPAIR if ok else Level.WARN
