"""The read-only GitHub state port (spec 0.4, 53.1, 53.3).

``GitHubState`` is the only surface any comparator is allowed to read
GitHub-side state through. It exposes exactly twelve read methods and no
write method of any kind — the mechanical half of safety rule 2 (spec
0.3): the detect path physically cannot write, because there is nothing
on this interface to write with.

If a comparator seems to need a write method here, that is a design
error: writes belong only to reconciler/repair/** behind the Phase 6
enablement registry, never to this port.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class GitHubState(ABC):
    """Abstract read-only view of one GitHub organisation's control-plane
    state, as needed by the Phase 1 comparator set."""

    @abstractmethod
    def org_members(self) -> list[str]:
        """Every login that is a member of the organisation."""

    @abstractmethod
    def team_members(self, product: str) -> list[str]:
        """Every login on the GitHub Team backing ``product``."""

    @abstractmethod
    def branch_protection(self, repo: str) -> dict[str, Any]:
        """The branch-protection configuration actually applied to ``repo``."""

    @abstractmethod
    def environments(self, repo: str) -> dict[str, Any]:
        """Every deployment environment configured on ``repo``, keyed by name."""

    @abstractmethod
    def codeowners(self, repo: str) -> str:
        """The raw CODEOWNERS file content for ``repo``."""

    @abstractmethod
    def workflow_files(self, repo: str) -> dict[str, Any]:
        """Every workflow file on ``repo``, keyed by filename."""

    @abstractmethod
    def resolve_tag(self, tag: str) -> str | None:
        """The commit SHA a workflow-reference tag currently resolves to."""

    @abstractmethod
    def rulesets(self) -> list[dict[str, Any]]:
        """Every organisation-level ruleset."""

    @abstractmethod
    def bypass_branches(self) -> list[dict[str, Any]]:
        """Every branch that used a ruleset bypass, with its commit authors."""

    @abstractmethod
    def check_runs(self, repo: str) -> dict[str, Any]:
        """Every named check run last published on ``repo``."""

    @abstractmethod
    def store_last_write(self) -> dict[str, str]:
        """The last-write timestamp for every monitored record-store prefix."""

    @abstractmethod
    def restore_test_records(self) -> list[dict[str, Any]]:
        """Every recorded restore-test result."""


_FORBIDDEN_PREFIXES = ("set_", "write_", "create_", "delete_", "update_", "put_")


def assert_read_only(cls: type) -> None:
    """Raise AssertionError if ``cls`` defines any method whose name begins
    with a write-shaped prefix. Used by tests to keep this port honest as
    it grows."""
    offenders = [name for name in vars(cls) if name.startswith(_FORBIDDEN_PREFIXES)]
    if offenders:
        raise AssertionError(f"{cls.__name__} declares write-shaped method(s): {offenders}")
