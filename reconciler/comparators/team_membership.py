"""L3-P1-04: product.yaml assignments vs GitHub Team membership (spec 53.1 row 3).

The declared Team for a product is the set of logins holding any
current assignment plus any unexpired temporary_assignments. Any
actual Team member outside that set, or any declared holder missing
from the Team, is Blocking - §53.1 row 3: "Fail CI on the affected
repository."
"""

from __future__ import annotations

from datetime import date

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator


def _declared_team(product_yaml: dict, as_of: date) -> set[str]:
    holders: set[str] = set()
    for holder in (product_yaml.get("assignments") or {}).values():
        if holder:
            holders.add(holder)
    for temp in product_yaml.get("temporary_assignments") or []:
        person = temp.get("person")
        end_date = temp.get("end_date")
        expired = end_date is not None and date.fromisoformat(end_date) < as_of
        if person and not expired:
            holders.add(person)
    return holders


@comparator("team_membership", fail_class=DriftClass.BLOCKING)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    first_seen = f"{as_of.isoformat()}T00:00:00Z"

    for product_name, product_yaml in declared.products.items():
        declared_team = _declared_team(product_yaml, as_of)
        actual_team = set(actual.team_members(product_name))

        for login in sorted(actual_team - declared_team):
            findings.append(
                Finding(
                    id=f"team_membership:{product_name}:{login}:unassigned",
                    comparator="team_membership",
                    scope=f"{product_name}:{login}",
                    drift_class=DriftClass.BLOCKING,
                    level=Level.BLOCK,
                    evidence=(
                        f"{login} is a member of the {product_name} Team but holds no "
                        "current or unexpired assignment on that product"
                    ),
                    first_seen=first_seen,
                )
            )
        for login in sorted(declared_team - actual_team):
            findings.append(
                Finding(
                    id=f"team_membership:{product_name}:{login}:missing",
                    comparator="team_membership",
                    scope=f"{product_name}:{login}",
                    drift_class=DriftClass.BLOCKING,
                    level=Level.BLOCK,
                    evidence=(
                        f"{login} holds an assignment on {product_name} but is missing "
                        "from its Team"
                    ),
                    first_seen=first_seen,
                )
            )

    return findings, len(declared.products)
