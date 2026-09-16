"""L3-P4-05: Team creator derived from the registries.

Spec basis: Section 11.2 -- "One Team per product ... Two
organisation-wide Teams grant Write to the Team Lead role and the QA
role. Team membership is derived from the registries" -- and Section
98.2 Phase 1.

`plan_teams(registries)` plans:

* one Team per product, named for the product, containing every
  person who holds a current assignment on it;
* exactly two organisation-wide Teams, `team-lead` and `qa`, one per
  role.

Membership is always **derived** from `people.yaml` / `product.yaml`,
never accepted from a caller: `Team()` itself refuses to be
constructed with an explicit member list (`CallerSuppliedMembership`)
and can only be built through `Team.derived(...)`, the constructor
`plan_teams` itself uses. This mirrors `tools/provision/codeowners.py`
(L3-P4-02)'s own "no caller-supplied identity list" discipline and
uses the *same* Team-Lead/QA derivation rule that module documents:
the current holder of the `reviewer-matrix-change` capability is
Team Lead; the current holder of the `verification` capability is QA.
Neither role name is a literal in `people.yaml` -- both are read off
capabilities, which is what "derived from the registries" means here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from reconciler.cli import DeclaredState

# Section 11.2's two organisation-wide Team names.
TEAM_LEAD_TEAM = "team-lead"
QA_TEAM = "qa"

# The per-product assignment slots that name a *current* assignment
# holder (Section 11.2: "every holder of a current assignment").
_ASSIGNMENT_ROLES = (
    "primary_owner",
    "cross_reviewer",
    "backup_owner",
    "incident_responder_primary",
    "incident_responder_backup",
    "verification_responsibility",
)

# The capability that identifies the current holder of each
# organisation-wide role -- the same pair `tools/provision/codeowners.py`
# uses for its Team Lead rule.
_ROLE_CAPABILITY = {
    TEAM_LEAD_TEAM: "reviewer-matrix-change",
    QA_TEAM: "verification",
}


class CallerSuppliedMembership(TypeError):
    """Team membership must be derived from the registries by
    `plan_teams`; a caller-supplied member list is refused (Section
    11.2)."""


@dataclass(frozen=True)
class Team:
    """One planned GitHub Team and its derived membership.

    Never construct this directly with a member list you computed
    yourself -- that is exactly the caller-supplied path Section 11.2
    forbids. Use `Team.derived(...)`, which `plan_teams` calls once it
    has actually derived membership from the registries.
    """

    name: str
    members: tuple[str, ...]

    def __init__(self, name: str, members: Any = None) -> None:  # noqa: D401
        raise CallerSuppliedMembership(
            f"Team({name!r}, ...) was called directly with a member list. "
            "Team membership is derived from the registries by plan_teams(); "
            "use Team.derived(...) only from within that derivation."
        )

    @classmethod
    def derived(cls, name: str, members: list[str]) -> "Team":
        self = object.__new__(cls)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "members", tuple(members))
        return self

    def __len__(self) -> int:
        return len(self.members)


def _is_current(person: dict[str, Any]) -> bool:
    return person.get("availability") != "departed"


def _product_team_members(product_yaml: dict[str, Any], current_logins: set[str]) -> list[str]:
    assignments = product_yaml.get("assignments") or {}
    members: list[str] = []
    for role in _ASSIGNMENT_ROLES:
        holder = assignments.get(role)
        if holder and holder in current_logins and holder not in members:
            members.append(holder)
    return members


def _role_team_members(people: list[dict[str, Any]], capability: str) -> list[str]:
    return [
        person["github_login"]
        for person in people
        if _is_current(person)
        and capability in (person.get("capabilities") or [])
        and person.get("github_login")
    ]


def plan_teams(registries: str) -> dict[str, list[str]]:
    """Plan every Team Section 11.2 requires, membership fully derived.

    `registries='fixture-a'` loads `reconciler/fixtures/fixture-a/declared/**`.
    Returns a plain ``{team_name: [member, ...]}`` mapping -- one entry
    per product, plus `team-lead` and `qa`.
    """
    declared = DeclaredState(registries)
    current_logins = {p["github_login"] for p in declared.people if _is_current(p) and p.get("github_login")}

    teams: dict[str, Team] = {}
    for product_name, product_yaml in declared.products.items():
        members = _product_team_members(product_yaml, current_logins)
        teams[product_name] = Team.derived(product_name, members)

    for team_name, capability in _ROLE_CAPABILITY.items():
        teams[team_name] = Team.derived(team_name, _role_team_members(declared.people, capability))

    return {name: list(team.members) for name, team in teams.items()}
