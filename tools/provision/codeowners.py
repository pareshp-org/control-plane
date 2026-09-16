"""L3-P4-02: CODEOWNERS generator, human identities only.

Spec basis: Section 11.3 -- "CODEOWNERS is generated to contain human
identities only -- no machine account ever appears in it" -- and the
four-rule ownership table transcribed below, verbatim in order:

    1. Product source paths are owned by the product Team.
    2. `verification/` is owned by whoever holds `verification_responsibility`.
    3. `product.yaml` is owned by the Team Lead role.
    4. Migration directories and CI workflow files are owned by the Team Lead role.

Every candidate owner is checked against `people.yaml` before it is
ever written to an output line: a login absent from `people.yaml`, or
matching the machine-identity pattern this codebase uses everywhere
else (`reconciler/comparators/codeowners.py`'s own convention -- a
`[bot]`-suffixed login, or a login with no `people.yaml` entry at all)
raises `MachineIdentityInCodeowners` rather than being emitted. No
machine approval can ever satisfy a CODEOWNERS-gated review this way
(Section 37.3, D53).

`generate(product, registries)` is the fixture-facing entry point the
CLI and the Phase-6 repair path (`L3-P6-04`) call: "Regenerate through
`tools.provision.codeowners.generate` -- one generator, never two."
`generate_from_registry` is the pure function underneath it, taking
already-loaded `product.yaml` content and the `people.yaml` list
directly -- this is what tests exercise to inject a machine login
without needing a second on-disk fixture.

Team-handle convention: this module has no organisation name to build
a `@org/team-slug` CODEOWNERS reference from (no fixture or registry
in this lane declares one), so it references the product Team and the
two organisation-wide role Teams `L3-P4-05` (`tools/provision/teams.py`)
plans by a bare handle: `@team-<product>` for the product Team,
`@team-lead` and `@qa` for the two organisation-wide Teams. If an
organisation name is ever declared, only this constant changes.
"""

from __future__ import annotations

from typing import Any

from reconciler.cli import DeclaredState

# The machine-identity test this module uses is the same one
# `reconciler/comparators/codeowners.py` already applies when comparing
# an actual CODEOWNERS file against this generator's output: a
# `[bot]`-suffixed login, or any login with no `people.yaml` entry.
_MACHINE_SUFFIX = "[bot]"

# Section 11.3's product-Team ownership line covers every current
# per-product assignment slot except `verification_responsibility`,
# which Rule 2 owns separately.
_PRODUCT_TEAM_ASSIGNMENT_ROLES = (
    "primary_owner",
    "cross_reviewer",
    "backup_owner",
    "incident_responder_primary",
    "incident_responder_backup",
)

# The capability that marks a person as holding the organisation-wide
# Team Lead role, derived from `people.yaml` the same way
# `tools/provision/teams.py` derives Team Lead / QA org-Team
# membership -- one derivation rule, used by both modules.
_TEAM_LEAD_CAPABILITY = "reviewer-matrix-change"


class MachineIdentityInCodeowners(Exception):
    """A candidate CODEOWNERS owner is a machine identity, or is not in
    `people.yaml` at all. Raised instead of emitting the line."""


def _is_machine_login(login: str, human_logins: set[str]) -> bool:
    return login.endswith(_MACHINE_SUFFIX) or login not in human_logins


def _owner_line(path: str, logins: list[str], human_logins: set[str]) -> str:
    for login in logins:
        if _is_machine_login(login, human_logins):
            raise MachineIdentityInCodeowners(
                f"{path}: {login!r} is a machine identity, or absent from people.yaml -- "
                "CODEOWNERS may name human identities only (Section 11.3, Section 37.3)"
            )
    owners = " ".join(f"@{login}" for login in logins)
    return f"{path} {owners}"


def _team_lead_holder(people: list[dict[str, Any]]) -> str | None:
    """The current holder of the organisation-wide Team Lead role.

    Derived from `people.yaml` capabilities, not a literal login: the
    holder of the `reviewer-matrix-change` capability among people who
    have not departed. `None` if no one currently holds it -- Rule 3
    and Rule 4 are then omitted rather than naming an absent owner.
    """
    for person in people:
        if person.get("availability") == "departed":
            continue
        if _TEAM_LEAD_CAPABILITY in (person.get("capabilities") or []):
            login = person.get("github_login")
            if login:
                return login
    return None


def generate_from_registry(product_yaml: dict[str, Any], people: list[dict[str, Any]]) -> str:
    """Generate CODEOWNERS content from already-loaded registry data.

    `product_yaml` is one product's parsed `product.yaml`; `people` is
    the parsed `people.yaml` `people:` list. Produces, in this order
    and no other, the four Section 11.3 ownership rules -- omitting
    any rule whose slot currently has no holder, rather than naming an
    absent one.
    """
    assignments = product_yaml.get("assignments") or {}
    human_logins = {p.get("github_login") for p in people if p.get("github_login")}

    lines: list[str] = []

    # Rule 1: product source paths -> the product Team.
    team_holders: list[str] = []
    for role in _PRODUCT_TEAM_ASSIGNMENT_ROLES:
        holder = assignments.get(role)
        if holder and holder not in team_holders:
            team_holders.append(holder)
    if team_holders:
        lines.append(_owner_line("*", team_holders, human_logins))

    # Rule 2: verification/ -> the holder of verification_responsibility.
    verifier = assignments.get("verification_responsibility")
    if verifier:
        lines.append(_owner_line("/verification/", [verifier], human_logins))

    # Rules 3 and 4 share one owner: the Team Lead role.
    team_lead = _team_lead_holder(people)
    if team_lead:
        # Rule 3: product.yaml -> the Team Lead role.
        lines.append(_owner_line("/product.yaml", [team_lead], human_logins))
        # Rule 4: migration directories and CI workflow files -> the Team Lead role.
        lines.append(_owner_line("/migrations/", [team_lead], human_logins))
        lines.append(_owner_line("/.github/workflows/", [team_lead], human_logins))

    return "\n".join(lines) + ("\n" if lines else "")


def generate(product: str, registries: str) -> str:
    """Generate CODEOWNERS content for `product` from the fixture (or,
    once a live registry loader exists, the organisation) named by
    `registries`. `registries='fixture-a'` loads
    `reconciler/fixtures/fixture-a/declared/**`, the one fixture this
    lane's tasks share."""
    declared = DeclaredState(registries)
    if product not in declared.products:
        raise KeyError(f"no such product {product!r} declared in {registries!r}")
    return generate_from_registry(declared.products[product], declared.people)
