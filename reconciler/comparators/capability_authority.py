"""L3-P1-03: capabilities vs team-implied authority (spec 53.1 row 2).

Team membership implies Write access (§11.2). Anyone holding a seat on
a product Team but no capability implying that authority is drift -
Amber, per §53.1 row 2 ("Alert"); §53.4 reserves class assignment for
configuration, not ad hoc escalation, so this stays Amber even though a
write-authority gap sounds severe.
"""

from __future__ import annotations

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator

# Capabilities that imply the write authority a Team seat grants.
AUTHORITY_CAPABILITIES = frozenset(
    {"code-review", "verification", "devops", "platform-admin", "escalation"}
)


@comparator("capability_authority", fail_class=DriftClass.AMBER)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    people = declared.people
    first_seen = f"{as_of.isoformat()}T00:00:00Z"

    team_logins: set[str] = set()
    for product_name in declared.products:
        team_logins.update(actual.team_members(product_name))

    for person in people:
        login = person.get("github_login")
        if login not in team_logins:
            continue
        capabilities = set(person.get("capabilities") or [])
        if not capabilities & AUTHORITY_CAPABILITIES:
            findings.append(
                Finding(
                    id=f"capability_authority:{login}",
                    comparator="capability_authority",
                    scope=login,
                    drift_class=DriftClass.AMBER,
                    level=Level.WARN,
                    evidence=(
                        f"{login} holds a product Team seat but no capability implying "
                        f"write authority (declared capabilities: {sorted(capabilities)})"
                    ),
                    first_seen=first_seen,
                )
            )

    return findings, len(people)
