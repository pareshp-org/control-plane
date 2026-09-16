"""L3-P4-08: CONFIGURE checklist and manual-step issue emitter.

Spec basis: Section 19.1 CONFIGURE stage -- "the scaffold emits a CONFIGURE
checklist issue enumerating every item below" -- and the CREATE PRODUCT
manual-step note: "or, where the provider offers no automation, tracked
manual steps emitted as issues so neither is silently missing." The two
manual steps this module renders issues for -- `alert_channel` and
`support_intake_mailbox` -- are the ones L3-P4-07's create-product plan
names.

This module only renders issue bodies as strings. It never calls GitHub:
posting is always a separate, explicit act gated on --apply and --live
(mirroring L3-P4-01's CLI-level gate) -- `post_issue` below exists only to
make that refusal mechanically checkable; nothing in this module performs
a network call under any argument combination.
"""

from __future__ import annotations

from dataclasses import dataclass

# Section 19.1 CONFIGURE stage: exactly these seven items, verbatim, in this
# order, no more, no fewer.
CONFIGURE_ITEMS: tuple[str, ...] = (
    "environments",
    "verification contract",
    "observability",
    "backups",
    "classification",
    "budget band",
    "support intake",
)

# Section 19.1: "set by the Founder as a provisional estimate, refined at
# the first cost review" -- attached to the budget-band row verbatim.
BUDGET_BAND_NOTE = "set by the Founder as a provisional estimate, refined at the first cost review"

# The two manual steps L3-P4-07's create-product plan declares (Section
# 19.1: "or, where the provider offers no automation, tracked manual steps
# emitted as issues so neither is silently missing").
CREATE_PRODUCT_MANUAL_STEPS: tuple[str, ...] = ("alert_channel", "support_intake_mailbox")


@dataclass(frozen=True)
class ManualStep:
    """A manual step from a plan (e.g. L3-P4-07's create-product plan)."""

    id: str
    description: str


class PostingRefused(Exception):
    """Raised whenever an issue post is attempted without --apply and --live."""


def configure_checklist(product: str) -> str:
    """Render the CONFIGURE checklist issue body for `product`.

    Enumerates exactly the seven Section 19.1 CONFIGURE items, verbatim, in
    order. The budget-band row carries the Founder-provisional-estimate
    note verbatim, as Section 19.1 requires.
    """
    lines = [f"# CONFIGURE checklist -- {product}", ""]
    for item in CONFIGURE_ITEMS:
        if item == "budget band":
            lines.append(f"- [ ] {item} ({BUDGET_BAND_NOTE})")
        else:
            lines.append(f"- [ ] {item}")
    return "\n".join(lines) + "\n"


def manual_step_issue(step: ManualStep) -> str:
    """Render one manual-step issue body for `step`.

    One issue per manual step named by the create-product orchestrator
    (L3-P4-07) so a step with no available provider automation is tracked,
    never silently missing (Section 19.1).
    """
    return (
        f"# Manual step -- {step.id}\n\n"
        f"{step.description}\n\n"
        "This step has no automation on the current provider. It is tracked "
        "here as a manual step so it is never silently missing (Section 19.1).\n"
    )


def manual_step_issues(steps) -> list[str]:
    """Render one issue per manual step in `steps`, in the order given."""
    return [manual_step_issue(step) for step in steps]


def post_issue(body: str, *, apply: bool, live: bool) -> None:
    """Would post `body` as a GitHub issue -- but only ever under --apply --live.

    Rendering a checklist or a manual-step issue never touches GitHub;
    posting one is always gated on both flags being explicit (Section
    64.1 safe defaults, mirroring L3-P4-01's --apply/--live gate). Neither
    flag alone is sufficient.
    """
    if not (apply and live):
        raise PostingRefused("issue post refused: requires both --apply and --live")
    raise NotImplementedError("live issue posting is not implemented by this lane task")
