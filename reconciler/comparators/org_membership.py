"""L3-P1-02: people.yaml vs organisation membership (spec 53.1 row 1).

Removal drift - a person the control plane has revoked or marked
departed who is still an organisation member - is Blocking (§11.2,
§12.2: "Alert; block on removal drift"). An active person absent from
the organisation is Amber; the org side simply has not caught up yet.
"""

from __future__ import annotations

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator


@comparator("org_membership", fail_class=DriftClass.BLOCKING)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    members = set(actual.org_members())
    people = declared.people
    first_seen = f"{as_of.isoformat()}T00:00:00Z"

    for person in people:
        login = person.get("github_login")
        access_status = person.get("access_status")
        availability = person.get("availability")
        is_member = login in members

        if (access_status == "revoked" or availability == "departed") and is_member:
            findings.append(
                Finding(
                    id=f"org_membership:{login}:removal_drift",
                    comparator="org_membership",
                    scope=login,
                    drift_class=DriftClass.BLOCKING,
                    level=Level.BLOCK,
                    evidence=(
                        f"{login} access_status={access_status!r} availability={availability!r} "
                        "but is still an organisation member (removal drift)"
                    ),
                    first_seen=first_seen,
                )
            )
        elif access_status == "active" and not is_member:
            findings.append(
                Finding(
                    id=f"org_membership:{login}:missing_from_org",
                    comparator="org_membership",
                    scope=login,
                    drift_class=DriftClass.AMBER,
                    level=Level.WARN,
                    evidence=f"{login} is declared active but is absent from the organisation",
                    first_seen=first_seen,
                )
            )

    return findings, len(people)
