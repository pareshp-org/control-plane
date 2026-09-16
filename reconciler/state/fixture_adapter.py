"""Fixture-backed implementation of GitHubState (L3-P0-06).

Reads exclusively from reconciler/fixtures/<name>/actual/ — never from
the network, never from anywhere else in the repository. This is the
adapter every comparator test and every non-``--live`` CLI run uses.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reconciler.state.port import GitHubState

_FIXTURES_ROOT = Path(__file__).resolve().parent.parent / "fixtures"


class FixtureState(GitHubState):
    def __init__(self, name: str, fixtures_root: Path | None = None):
        root = (fixtures_root or _FIXTURES_ROOT) / name / "actual"
        org_path = root / "org.json"
        if not org_path.is_file():
            raise FileNotFoundError(f"fixture has no actual/org.json: {org_path}")
        self._root = root
        self._org: dict[str, Any] = json.loads(org_path.read_text(encoding="utf-8"))

    # -- GitHubState -----------------------------------------------------

    def org_members(self) -> list[str]:
        return list(self._org.get("members", []))

    def team_members(self, product: str) -> list[str]:
        return list(self._org.get("teams", {}).get(product, []))

    def branch_protection(self, repo: str) -> dict[str, Any]:
        return dict(self._org.get("branch_protection", {}).get(repo, {}))

    def environments(self, repo: str) -> dict[str, Any]:
        return dict(self._org.get("environments", {}).get(repo, {}))

    def codeowners(self, repo: str) -> str:
        path = self._root / "codeowners" / f"{repo}.CODEOWNERS"
        if not path.is_file():
            raise FileNotFoundError(f"no CODEOWNERS fixture for repo {repo!r}: {path}")
        return path.read_text(encoding="utf-8")

    def workflow_files(self, repo: str) -> dict[str, Any]:
        return dict(self._org.get("workflow_files", {}).get(repo, {}))

    def resolve_tag(self, tag: str) -> str | None:
        return self._org.get("tag_resolution", {}).get(tag)

    def rulesets(self) -> list[dict[str, Any]]:
        return list(self._org.get("rulesets", []))

    def bypass_branches(self) -> list[dict[str, Any]]:
        return list(self._org.get("bypass_branches", []))

    def check_runs(self, repo: str) -> dict[str, Any]:
        return dict(self._org.get("check_runs", {}).get(repo, {}))

    def store_last_write(self) -> dict[str, str]:
        return dict(self._org.get("store_last_write", {}))

    def restore_test_records(self) -> list[dict[str, Any]]:
        return list(self._org.get("restore_test_records", []))
