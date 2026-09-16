"""L3-P4-10: Pre-provisioning (T-minus-one-week) checklist emitter.

Spec basis: Section 12.1 -- "At one week before the start date the operator
works a pre-provisioning checklist: GitHub account confirmed, hardware
ready, email account created, AI-runtime choice asked of the joiner, the
runtime seat purchased, and an asset-inventory entry recorded for issued
hardware (Section 49)." Section 49 owns the asset-inventory destination and
is the destination this checklist names; `assets/**` is L5-owned data
(PARTITION.md rule 4) and this lane never writes it.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

LEAD_DAYS = 7

# Section 12.1: exactly these six items, verbatim, in order.
PREPROVISION_ITEMS: tuple[str, ...] = (
    "GitHub account confirmed",
    "hardware ready",
    "email account created",
    "AI-runtime choice asked of the joiner",
    "the runtime seat purchased",
    "an asset-inventory entry recorded for issued hardware",
)

# The sixth item is the asset-inventory item. Its destination is Section 49
# (assets/**, owned by lane 5) -- this lane declares the checklist row, it
# never writes the asset-inventory entry itself.
ASSET_INVENTORY_ITEM = PREPROVISION_ITEMS[5]
ASSET_INVENTORY_DESTINATION_NOTE = (
    "recorded in the Section 49 asset inventory (assets/**, owned by lane 5 -- "
    "not written by this lane)"
)


@dataclass(frozen=True)
class PreprovisionChecklist:
    """The T-minus-one-week checklist for one incoming joiner."""

    login: str
    start_date: date
    due_date: date
    items: tuple[str, ...]

    def render(self) -> str:
        lines = [
            f"# Pre-provisioning -- {self.login} -- due {self.due_date.isoformat()} "
            f"(start date {self.start_date.isoformat()})",
            "",
        ]
        for item in self.items:
            if item == ASSET_INVENTORY_ITEM:
                lines.append(f"- [ ] {item} ({ASSET_INVENTORY_DESTINATION_NOTE})")
            else:
                lines.append(f"- [ ] {item}")
        return "\n".join(lines) + "\n"


def preprovision_checklist(login: str, start_date) -> PreprovisionChecklist:
    """Build the T-minus-one-week pre-provisioning checklist for `login`.

    `start_date` may be a `date` or an ISO `YYYY-MM-DD` string. Exactly the
    six Section 12.1 items are enumerated, verbatim, in order; the due date
    is exactly seven days before `start_date`.
    """
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)
    due_date = start_date - timedelta(days=LEAD_DAYS)
    return PreprovisionChecklist(
        login=login,
        start_date=start_date,
        due_date=due_date,
        items=PREPROVISION_ITEMS,
    )
