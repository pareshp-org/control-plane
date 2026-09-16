"""L3-P6-03: repair class: Team membership sync from the registries
(spec 53.2 Level 3; spec 11.2; spec 26.4: "reconciliation Level-3
auto-repairs ... write directly under the reconciler credential,
logged as repair records").

Consumes the Phase-1 `team_membership` comparator's findings. Each
finding names one login's drift against one product Team in exactly
one direction, by its id suffix:

* `:unassigned` - an actual Team member who holds no current or
  unexpired assignment. Removal is the stricter direction: fewer
  people with access than the registry declares is never a loosening.
* `:missing` - a declared assignment holder absent from the Team.
  Adding this person is permitted *only* because the registry (a
  separately governed, human-approved decision - spec 26.4) already
  declares the assignment; this class is syncing GitHub's actual state
  to match a decision that was already made, not making a new one.

No membership is ever added from actual state - both directions read
their target value from `declared`, never from `actual`. Both go
through `permitted()`'s `team_membership` control kind, which treats
matching the declared registry as the invariant in either direction
(reconciler/repair/stricter.py's module docstring explains why this
control kind has no separate strictness gradient to compare).
"""

from __future__ import annotations

from typing import Sequence

from reconciler.model import Finding
from reconciler.repair import Repair
from reconciler.repair.stricter import permitted

CONTROL_KIND = "team_membership"


def repair(findings: Sequence[Finding], *, enabled: bool) -> list[Repair]:
    repairs: list[Repair] = []
    if not enabled:
        return repairs

    for finding in findings:
        if finding.comparator != "team_membership":
            continue
        product, login = finding.scope.split(":", 1)

        if finding.id.endswith(":unassigned"):
            declared, actual, action = False, True, "remove"
        elif finding.id.endswith(":missing"):
            declared, actual, action = True, False, "add"
        else:
            continue

        ok, reason = permitted(declared, actual, CONTROL_KIND)
        if not ok:
            continue

        if action == "remove":
            permitted_reason = reason or (
                f"{login} holds no current or unexpired assignment on {product}; removed "
                "from the Team to match the registry"
            )
            compensating_action = f"re-add {login} to the {product} Team if this was removed in error"
        else:
            permitted_reason = reason or (
                f"{login} holds a declared assignment on {product} the registry already "
                "authorises; added to the Team to match it"
            )
            compensating_action = f"remove {login} from the {product} Team if this was added in error"

        repairs.append(
            Repair(
                repair_class="team_sync",
                finding_id=finding.id,
                scope=finding.scope,
                before={"team_member": actual},
                after={"team_member": declared},
                permitted_reason=permitted_reason,
                compensating_action=compensating_action,
            )
        )

    return repairs
