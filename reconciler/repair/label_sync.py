"""L3-P6-07: repair class: label and board field sync (spec 53.2
Level 3: "label and board field sync").

The lowest-risk class in the set: labels and project-board custom
fields are metadata, not access, protection, or membership - drift
here confers no authority in either direction. There is no Phase-1
comparator for label/board-field drift yet in this lane's registry
(reconciler/comparators/**), so this class is driven directly by a
declared-vs-actual field-value diff rather than by a pre-existing
Finding list the way team_sync and expiry_revoke are; `diff_and_repair`
is the shape a future comparator's findings would be adapted into.

Confers-no-authority does not mean exempt from the contract: every
sync here still goes through `permitted()` and still produces a
`Repair` the same way every other Phase 6 class does (module docstring
of reconciler/repair/__init__.py) - there is no low-risk shortcut.
"""

from __future__ import annotations

from typing import Any, Mapping

from reconciler.repair import Repair
from reconciler.repair.stricter import permitted

CONTROL_KIND = "label_and_board_field_set"


def diff_and_repair(
    scope: str,
    declared_fields: Mapping[str, Any],
    actual_fields: Mapping[str, Any],
    *,
    enabled: bool,
) -> list[Repair]:
    """Sync every field of one labelled/board-tracked item (an issue's
    label set, or one custom board field) toward `declared_fields`."""
    repairs: list[Repair] = []
    if not enabled:
        return repairs

    for field in sorted(set(declared_fields) | set(actual_fields)):
        declared_value = declared_fields.get(field)
        actual_value = actual_fields.get(field)
        if declared_value == actual_value:
            continue

        ok, reason = permitted(declared_value, actual_value, CONTROL_KIND)
        if not ok:
            continue

        repairs.append(
            Repair(
                repair_class="label_sync",
                finding_id=f"label_sync:{scope}:{field}",
                scope=scope,
                before={field: actual_value},
                after={field: declared_value},
                permitted_reason=reason or f"{field} on {scope} synced to its declared value",
                compensating_action=f"restore {field}={actual_value!r} on {scope} from the repair record",
            )
        )
    return repairs


def repair(
    items: Mapping[str, tuple[Mapping[str, Any], Mapping[str, Any]]], *, enabled: bool
) -> list[Repair]:
    """`items` maps scope -> (declared_fields, actual_fields) for every
    labelled/board-tracked item in this run."""
    repairs: list[Repair] = []
    for scope, (declared_fields, actual_fields) in items.items():
        repairs.extend(diff_and_repair(scope, declared_fields, actual_fields, enabled=enabled))
    return repairs
