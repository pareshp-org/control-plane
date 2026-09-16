"""L3-P4-06: repo-from-template and required-file assertion.

Spec basis: Section 33.1 (the eight local-environment-contract commands and
the eight required-file items -- "Required-file presence is checked, not
assumed"); Section 11.3 ("New repositories are created private, with branch
protection applied from the template at creation, no environment access and
no third-party app access -- safe defaults, activation explicit"); Section
64.1 ("a configuration error must never grant excess authority").

Two of the eight required items are described by *role*, not by a literal
path -- "seed data" and "migration directory" -- because `product-template`
is not an L3-owned repository and L3 cannot define paths inside it. REG-040
(raised as `D-L3-04-03`) is Closed, "in force": the canonical paths are
`seed/` and `migrations/`. If L0 ever settles differently, only the two
directory entries below change.

This module plans; it never calls the GitHub API. `plan_repo` takes the set
of paths and commands a candidate template tree actually exposes (supplied
by a live template inspection or, in tests, a fixture set) and asserts every
required item is present. A missing item is a hard failure -- it raises,
it never merely warns (Section 33.1).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

# The template every product repository is generated from (Section 19.1
# CREATE PRODUCT step 1: "repository or repository set from the standard
# template"). Never a literal ref elsewhere in this module -- the template
# *ref* (which tag/SHA of this repo) is a contracts-layer concern outside
# L3-P4-06's scope; only its name is fixed here.
TEMPLATE_REPO = "product-template"

# Section 33.1: the eight required items, "Required files in every
# repository". Six are literal paths. The seventh and eighth are:
#   - a role-described pair (seed data, migration directory) pinned to
#     `seed/` and `migrations/` by REG-040 ("in force" default), and
#   - an either/or ("either `product.yaml` or a pointer to the product it
#     belongs to"), represented as a single tuple entry so that satisfying
#     *either* alternative satisfies the one item.
REQUIRED_FILES: tuple[object, ...] = (
    ".env.example",
    "docker-compose.dev.yml",
    "Makefile",
    "seed/",  # "seed data" -- REG-040 / D-L3-04-03, in force
    "migrations/",  # "migration directory" -- REG-040 / D-L3-04-03, in force
    "verification/",
    "AGENTS.md",
    ("product.yaml", ".product-pointer"),
)

# Section 33.1: the eight local-environment-contract commands. (Not to be
# confused with the ten-target decomposition of the superseded L3-04
# phase-file layout -- PFD-014 / FD-088 settled the L3-06 layout, eight
# commands, as authoritative for this task.)
REQUIRED_COMMANDS: tuple[str, ...] = (
    "setup",
    "dev",
    "test",
    "uat-local",
    "migrate",
    "reset",
    "health",
    "parity",
)


class MissingRequiredFile(Exception):
    """A candidate template tree lacks a Section 33.1 required file/directory."""


class MissingRequiredCommand(Exception):
    """A candidate template tree lacks a Section 33.1 local-environment command."""


def _item_label(item: object) -> str:
    if isinstance(item, tuple):
        return " or ".join(item)
    return str(item)


def _item_satisfied(item: object, present: set[str]) -> bool:
    if isinstance(item, tuple):
        return any(alt in present for alt in item)
    return item in present


@dataclass(frozen=True)
class RepoPlan:
    """A dry-run plan for creating one repository from `product-template`.

    Carries only the safe-defaults facts Section 11.3/64.1 make load-bearing
    (private, no environment access, no third-party app access) plus the
    required items that were verified present. Nothing here performs a
    write -- this is a plan, not an API call.
    """

    product: str
    repo: str
    template: str
    private: bool
    environment_access: bool
    third_party_app_access: bool
    files_verified: tuple[str, ...]
    commands_verified: tuple[str, ...]

    def summary_line(self) -> str:
        return (
            f"PLAN repo product={self.product} repo={self.repo} "
            f"private={self.private} files={len(self.files_verified)} "
            f"commands={len(self.commands_verified)}"
        )


def plan_repo(
    product: str,
    template_files: Iterable[str],
    template_commands: Iterable[str],
    *,
    repo: str | None = None,
) -> RepoPlan:
    """Plan repo-from-template creation for `product`.

    `template_files` is the set of paths the candidate template tree
    exposes; `template_commands` is the set of Makefile targets it exposes.
    Both are supplied by the caller (a live template inspection, or a test
    double) -- this function never reaches out to GitHub itself.

    Presence of every Section 33.1 required file and every required command
    is CHECKED, not assumed: any single missing item raises immediately.
    The plan that results is always private, with no environment access and
    no third-party app access (Section 11.3, Section 64.1) -- those are not
    options this function exposes a way to turn on.
    """
    present_files = set(template_files)
    missing_files = [
        _item_label(item) for item in REQUIRED_FILES if not _item_satisfied(item, present_files)
    ]
    if missing_files:
        raise MissingRequiredFile(
            f"{product}: {TEMPLATE_REPO} is missing required item(s): {', '.join(missing_files)}"
        )

    present_commands = set(template_commands)
    missing_commands = [c for c in REQUIRED_COMMANDS if c not in present_commands]
    if missing_commands:
        raise MissingRequiredCommand(
            f"{product}: {TEMPLATE_REPO} is missing required command(s): {', '.join(missing_commands)}"
        )

    return RepoPlan(
        product=product,
        repo=repo or product,
        template=TEMPLATE_REPO,
        private=True,
        environment_access=False,
        third_party_app_access=False,
        files_verified=tuple(_item_label(item) for item in REQUIRED_FILES),
        commands_verified=REQUIRED_COMMANDS,
    )
