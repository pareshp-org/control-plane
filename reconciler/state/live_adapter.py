"""Live GitHub REST implementation of GitHubState (L3-P0-06).

This adapter issues real, read-only calls against api.github.com. It is
never exercised by any acceptance command in this repository — every
SELF-VERIFY and test in lanes/L3-06-tasks.md runs against
FixtureState. It exists so the eventual live reconciler run has
something to instantiate, gated behind the CLI's explicit ``--live``
flag (spec 0.4).

Every method here issues a GET only. There is no method whose name
begins ``set_``, ``write_``, ``create_``, ``delete_``, ``update_`` or
``put_`` — enforced the same way as FixtureState, by inheriting the
GitHubState abstract base and nothing else.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from reconciler.state.port import GitHubState

API_ROOT = "https://api.github.com"


class LiveAdapterDisabled(RuntimeError):
    """Raised when LiveState is constructed without explicit opt-in.

    The reconciler CLI only opts in when the operator passes --live;
    nothing in this codebase does so implicitly.
    """


class LiveState(GitHubState):
    def __init__(self, org: str, *, live: bool, token: str | None = None, timeout: float = 10.0):
        if not live:
            raise LiveAdapterDisabled(
                "LiveState requires live=True (set only by the CLI's --live flag); "
                "refusing to make network calls implicitly"
            )
        self._org = org
        self._token = token or os.environ.get("GITHUB_TOKEN")
        if not self._token:
            raise LiveAdapterDisabled("GITHUB_TOKEN is not set; refusing to call the GitHub API with no credential")
        self._timeout = timeout

    # -- transport ---------------------------------------------------------

    def _get(self, path: str) -> Any:
        req = urllib.request.Request(
            f"{API_ROOT}{path}",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:  # noqa: S310 - read-only GET
                return json.loads(resp.read().decode("utf-8") or "null")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"GitHub API GET {path} failed: {exc.code} {exc.reason}") from exc

    # -- GitHubState ---------------------------------------------------------

    def org_members(self) -> list[str]:
        return [m["login"] for m in self._get(f"/orgs/{self._org}/members?per_page=100")]

    def team_members(self, product: str) -> list[str]:
        return [m["login"] for m in self._get(f"/orgs/{self._org}/teams/{product}/members?per_page=100")]

    def branch_protection(self, repo: str) -> dict[str, Any]:
        try:
            return self._get(f"/repos/{self._org}/{repo}/branches/main/protection")
        except RuntimeError:
            return {}

    def environments(self, repo: str) -> dict[str, Any]:
        data = self._get(f"/repos/{self._org}/{repo}/environments")
        return {e["name"]: e for e in data.get("environments", [])}

    def codeowners(self, repo: str) -> str:
        data = self._get(f"/repos/{self._org}/{repo}/contents/.github/CODEOWNERS")
        import base64

        return base64.b64decode(data["content"]).decode("utf-8")

    def workflow_files(self, repo: str) -> dict[str, Any]:
        data = self._get(f"/repos/{self._org}/{repo}/actions/workflows")
        return {w["path"].rsplit("/", 1)[-1]: w for w in data.get("workflows", [])}

    def resolve_tag(self, tag: str) -> str | None:
        try:
            ref = self._get(f"/repos/{self._org}/workflows/git/ref/tags/{tag}")
        except RuntimeError:
            return None
        return ref.get("object", {}).get("sha")

    def rulesets(self) -> list[dict[str, Any]]:
        return self._get(f"/orgs/{self._org}/rulesets")

    def bypass_branches(self) -> list[dict[str, Any]]:
        # No single GitHub endpoint enumerates historical bypass usage;
        # a live run derives this from ruleset insight logs out of band.
        return []

    def check_runs(self, repo: str) -> dict[str, Any]:
        data = self._get(f"/repos/{self._org}/{repo}/commits/HEAD/check-runs")
        return {c["name"]: c for c in data.get("check_runs", [])}

    def store_last_write(self) -> dict[str, str]:
        # The record store lives outside this org's control-plane repo
        # (Lane 4's territory); a live run reads this from the records
        # repository's own commit history, not the GitHub org API.
        return {}

    def restore_test_records(self) -> list[dict[str, Any]]:
        return []
