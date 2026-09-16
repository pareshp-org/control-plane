"""L3-P3-04: drift budget counters (spec 53.4 budget rules).

Amber scales with the portfolio - `amber_per_product` open Amber
findings per product, so the ceiling reads 4 at two products, 16 at
eight, 40 at twenty (spec 53.4's own three figures) - "because Amber
is routine remediation debt and a fixed ceiling would tighten
silently as products are added." Red is deliberately held flat at
`red_portfolio_flat` portfolio-wide and does not scale, "because Red
is the volume of material unremediated risk the team can actually
hold in attention at once; that number is a property of the team, not
of the portfolio." Green is unlimited. Blocking has no budget - it
already blocks work outright, so a count against it would be
meaningless.

Canary findings and prospective-orphan findings are excluded from
every count in this module (spec 53.1's own canary-exclusion rule;
see reconciler.canary's docstring: "Any future drift-budget aggregator
must filter on `comparator == 'display_name'` ... before summing").
"""

from __future__ import annotations

import dataclasses
from typing import Any, Iterable

from reconciler.canary import CANARY_ID
from reconciler.model import DriftClass, Finding

DEFAULT_AMBER_PER_PRODUCT = 2
DEFAULT_RED_PORTFOLIO_FLAT = 3

# spec 53.4's own worked figures, transcribed literally: "the ceiling
# reads 16 at eight products and 40 at twenty."
_AMBER_PER_PRODUCT_KEY = "amber_per_product"
_RED_PORTFOLIO_FLAT_KEY = "red_portfolio_flat"


def ceilings(product_count: int, config: dict[str, Any] | None = None) -> dict[str, int | None]:
    """Return {"green": None, "amber": int, "red": int, "blocking": None}
    for `product_count` products, under `config` (a mapping shaped like
    os-health.yaml's `drift_budget:` block) or this module's own
    defaults where `config` omits a key.

    Green and Blocking carry no ceiling (`None`): Green because it is
    unlimited by spec, Blocking because it has no budget at all - it
    is not that its ceiling is high, it is that counting against one
    is not the mechanism spec 53.4 uses for Blocking.
    """
    config = config or {}
    amber_per_product = config.get(_AMBER_PER_PRODUCT_KEY, DEFAULT_AMBER_PER_PRODUCT)
    red_flat = config.get(_RED_PORTFOLIO_FLAT_KEY, DEFAULT_RED_PORTFOLIO_FLAT)
    return {
        "green": None,
        "amber": amber_per_product * product_count,
        "red": red_flat,
        "blocking": None,
    }


def _is_excluded(finding: Finding) -> bool:
    """Canary findings (id == CANARY_ID) and prospective-orphan
    findings are excluded from every drift-budget count. A
    prospective-orphan finding is one whose comparator id contains
    "prospective" - the naming convention this task establishes for
    the `availability: departing` prospective mode (L3-P2-05); any
    orphan detector emitting prospective findings must carry that
    substring in its registered comparator id for this exclusion to
    apply to it.
    """
    if finding.id == CANARY_ID:
        return True
    if "prospective" in finding.comparator:
        return True
    return False


@dataclasses.dataclass(frozen=True)
class BudgetReport:
    open_counts: dict[str, int]
    ceilings: dict[str, int | None]
    breaches: dict[str, bool]
    # "about the operating system, not about any individual product"
    # (spec 53.4) - the fixed scope an Amber breach is ever attributed
    # to; never a product name.
    amber_breach_scope: str | None


def evaluate(
    findings: Iterable[Finding],
    product_count: int,
    config: dict[str, Any] | None = None,
) -> BudgetReport:
    counted = [f for f in findings if not _is_excluded(f)]

    open_counts: dict[str, int] = {cls.value: 0 for cls in DriftClass}
    for f in counted:
        open_counts[f.drift_class.value] += 1

    ceiling = ceilings(product_count, config)

    amber_breach = ceiling["amber"] is not None and open_counts[DriftClass.AMBER.value] > ceiling["amber"]
    red_breach = ceiling["red"] is not None and open_counts[DriftClass.RED.value] > ceiling["red"]

    breaches = {
        "green": False,  # unlimited: never breaches
        "amber": amber_breach,
        "red": red_breach,
        "blocking": False,  # no budget: not a breach concept
    }

    return BudgetReport(
        open_counts=open_counts,
        ceilings=ceiling,
        breaches=breaches,
        amber_breach_scope="operating_system" if amber_breach else None,
    )
