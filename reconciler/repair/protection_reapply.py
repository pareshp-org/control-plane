"""L3-P6-05: repair class: re-apply declared branch protection (spec
53.2 Level 3: "re-applying declared branch protection"; spec 53.3;
AT-033).

Consumes the Phase-1 `branch_protection` comparator's (L3-P1-06)
`:weakened` findings only. For each, this asks `stricter.permitted()`
whether re-applying `declared_template` wholesale to that repository
is a stricter-only move; only on approval does it become a `Repair`.

Two things this class deliberately never does, both load-bearing and
both tested below:

* It never touches a `:stricter_than_declared` finding. Those are
  filtered out before `permitted()` is even asked - AT-033: "Where
  actual state is stricter than declared, reconciliation raises Level
  2 for human judgment rather than relaxing the control", and that
  Level 2 finding is left standing untouched by this module, which
  writes nothing back to the finding stream at all.
* It never shortens `required_status_checks.contexts` below what a
  repository's actual state already requires. This falls out of
  `stricter.permitted()`'s whole-object comparison for free: a
  repository whose actual contexts are a superset of declared's (even
  if some *other* field on the same repository is weaker) fails the
  dict-level stricter-or-equal check as a whole, so `permitted()`
  refuses the entire repair rather than applying `declared_template`
  and silently dropping an actual-only context. `test_repair_protection.py`
  proves this for the mixed case explicitly.

`after` is always `declared_template` verbatim - never a partial,
field-by-field patch - so there is no path through this module that
could construct a context list shorter than the declared one either;
the declared template is, by construction, the one file this lane
never writes and the reconciler is themself narrowed away from
loosening (D93).
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from reconciler.model import Finding
from reconciler.repair import Repair
from reconciler.repair.stricter import permitted

CONTROL_KIND = "branch_protection"


def repair(
    findings: Sequence[Finding],
    declared_template: Mapping[str, Any],
    actual_by_repo: Mapping[str, Mapping[str, Any]],
    *,
    enabled: bool,
) -> list[Repair]:
    """`findings` is the `branch_protection` comparator's output for one
    run; `declared_template` is `declared/templates/branch-protection.json`;
    `actual_by_repo` maps repository name to that repository's actual
    branch-protection JSON (the same shape `GitHubState.branch_protection`
    returns)."""
    repairs: list[Repair] = []
    if not enabled:
        return repairs

    for finding in findings:
        if finding.comparator != "branch_protection" or not finding.id.endswith(":weakened"):
            # Not a weakening finding - either a different comparator
            # entirely, or the AT-033 stricter-than-declared finding
            # this class must leave standing untouched.
            continue

        repo = finding.scope
        actual = actual_by_repo.get(repo, {})
        ok, reason = permitted(declared_template, actual, CONTROL_KIND)
        if not ok:
            continue

        repairs.append(
            Repair(
                repair_class="protection_reapply",
                finding_id=finding.id,
                scope=repo,
                before=dict(actual),
                after=dict(declared_template),
                permitted_reason=reason
                or f"{repo} branch protection re-applied to the declared template",
                compensating_action=(
                    f"restore {repo}'s prior branch protection {dict(actual)!r} from the "
                    "repair record - never re-shorten required_status_checks.contexts below "
                    "what declared/templates/branch-protection.json requires"
                ),
            )
        )
    return repairs
