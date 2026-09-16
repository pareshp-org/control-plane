"""L3-P1-09: assignment end_date vs current Team membership (spec 53.1 row 11).

For each `temporary_assignments` row: an already-expired row whose
holder is still on the product Team is Blocking (§101 invariant 58;
AT-008; AT-018), tagged with `repair_class=expiry_revoke` in evidence
for Phase 6 to consume - this comparator never revokes anything itself
(§98.2 Phase 3: detect only). A row within 14 days of expiry and not
yet expired is Amber - §10.1: "Delegation expiry is warned, never
silent." `temporary_assignments` is the only delegation-shaped
structure product.yaml exposes, so every row in it is in scope for
both checks; there is no second, broader "delegation" registry this
comparator must additionally consult (that broader taxonomy question
is DR-L3-05-B, open and scoped to L3-05's daily sweep, not to this
narrower per-product comparator).

`compared` counts the temporary_assignments rows examined across every
product - the comparator's only declared input.
"""

from __future__ import annotations

from datetime import date, timedelta

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator

WARNING_WINDOW_DAYS = 14


@comparator("expiry", fail_class=DriftClass.BLOCKING)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    compared = 0
    first_seen = f"{as_of.isoformat()}T00:00:00Z"

    for product_name, product_yaml in declared.products.items():
        rows = product_yaml.get("temporary_assignments") or []
        if not rows:
            continue
        team_members = set(actual.team_members(product_name))
        for row in rows:
            end_date_raw = row.get("end_date")
            if end_date_raw is None:
                continue
            compared += 1
            person = row.get("person")
            end_date = date.fromisoformat(end_date_raw)
            expired = end_date < as_of

            if expired and person in team_members:
                findings.append(
                    Finding(
                        id=f"expiry:{product_name}:{person}:expired",
                        comparator="expiry",
                        scope=f"{product_name}:{person}",
                        drift_class=DriftClass.BLOCKING,
                        level=Level.BLOCK,
                        evidence=(
                            f"{person}'s {row.get('type')} assignment on {product_name} "
                            f"expired {end_date_raw} but they remain on the Team "
                            "repair_class=expiry_revoke"
                        ),
                        first_seen=first_seen,
                    )
                )
            elif not expired and (end_date - as_of) <= timedelta(days=WARNING_WINDOW_DAYS):
                findings.append(
                    Finding(
                        id=f"expiry:{product_name}:{person}:expiring_soon",
                        comparator="expiry",
                        scope=f"{product_name}:{person}",
                        drift_class=DriftClass.AMBER,
                        level=Level.WARN,
                        evidence=(
                            f"{person}'s {row.get('type')} assignment on {product_name} "
                            f"expires {end_date_raw}, within the {WARNING_WINDOW_DAYS}-day "
                            "advance warning window"
                        ),
                        first_seen=first_seen,
                    )
                )

    return findings, compared
