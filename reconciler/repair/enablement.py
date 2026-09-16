"""L3-P6-02: repair enablement registry, every class default-off
(spec 99.6 risk 6: "repair classes enabled one at a time"; spec 98.3;
spec 64.1).

`REPAIR_CLASSES` transcribes the five spec 53.2 Level-3 repair classes.
Every one of them defaults to `enabled=False` - enabling is a
recorded human decision (`enable()` below), never an implementation
default, and never something ships silently flipped just because
detection has run clean. Enabling more than one class in the same call
raises: spec 99.6 risk 6 asks for classes to be turned on "one at a
time", not as a batch.
"""

from __future__ import annotations

from dataclasses import dataclass

# The five §53.2 Level-3 auto-repair classes, transcribed verbatim
# from their spec phrasing - no sixth class exists (DEC-L3-02-04 in
# lanes/L3-02-levels-and-repair.md left that question to L0 and it is
# not resolved; this registry names only the closed list of five).
_CLASS_LABELS: dict[str, str] = {
    "team_sync": "Team membership sync from the registries",
    "codeowners_regen": "CODEOWNERS regeneration",
    "label_sync": "Label and board field sync",
    "protection_reapply": "Re-applying declared branch protection",
    "expiry_revoke": "Removing expired assignments and expired access",
}


class EnablementError(ValueError):
    """Raised by enable() for any attempt that is not exactly one
    class, carrying a decision-record id, turned on in isolation."""


@dataclass
class RepairClass:
    id: str
    label: str
    enabled: bool = False
    enabled_on: str | None = None
    enabled_by: str | None = None


def _fresh_registry() -> dict[str, RepairClass]:
    return {class_id: RepairClass(id=class_id, label=label) for class_id, label in _CLASS_LABELS.items()}


# The live registry every caller reads and enable() mutates. Every
# entry's declared default is enabled=False (acceptance 1).
REPAIR_CLASSES: dict[str, RepairClass] = _fresh_registry()


def enable(class_ids: str | list[str], *, enabled_on: str, enabled_by: str) -> RepairClass:
    """Turn exactly one repair class on. Requires all three of a class
    id, an `enabled_on` date and an `enabled_by` decision-record id -
    enabling with any of the three missing raises, and enabling more
    than one class in a single call raises (spec 99.6 risk 6)."""
    ids = [class_ids] if isinstance(class_ids, str) else list(class_ids)

    if len(ids) != 1:
        raise EnablementError(
            f"refusing to enable {len(ids)} repair classes in one change; spec 99.6 risk 6 "
            "requires classes to be enabled one at a time"
        )
    if not enabled_by:
        raise EnablementError("enabling a repair class requires an enabled_by decision-record id")
    if not enabled_on:
        raise EnablementError("enabling a repair class requires an enabled_on date")

    class_id = ids[0]
    if class_id not in REPAIR_CLASSES:
        raise EnablementError(f"unknown repair class {class_id!r}; known classes: {sorted(REPAIR_CLASSES)}")

    repair_class = REPAIR_CLASSES[class_id]
    repair_class.enabled = True
    repair_class.enabled_on = enabled_on
    repair_class.enabled_by = enabled_by
    return repair_class


def reset_for_tests() -> None:
    """Restore every class to its declared enabled=False default.
    Exists so test_enablement.py's cases do not leak enablement state
    into each other or into other test modules importing this one -
    REPAIR_CLASSES is process-wide mutable state, by design (a real
    run needs one shared registry), so tests must clean up after
    themselves rather than each getting a fresh import."""
    REPAIR_CLASSES.clear()
    REPAIR_CLASSES.update(_fresh_registry())
