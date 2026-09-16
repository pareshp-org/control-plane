"""validators.drift.verifier — the independent second verifier (spec 53.1).

Spec 53.1: "A second verifier therefore runs off the operations VM and
under a different credential ... holding its own read-only fine-grained
credential", asserting a short list of facts about the *actual* GitHub
state and "writ[ing] its result to a surface the operations VM cannot
write to" — that surface is Lane 2's workflow output, not this lane's to
create; this module only ever prints and returns an exit code.

Three hard constraints, each load-bearing and each enforced by
test_verifier.py:

* This module — and everything under ``validators/drift/`` — imports
  nothing from ``reconciler/**``. Spec 53.1: "no control that can be
  rewritten by the credential it is checking is a control." A verifier
  that reused the reconciler's comparison helpers would inherit the
  reconciler's blind spots and could be silenced by whatever silences
  the reconciler. Where an assertion needs the same *kind* of read the
  reconciler's comparators perform (parsing CODEOWNERS, reading
  org.json), that reading is reimplemented here, deliberately, on
  purpose, as its own small reader (``VerifierState`` below) rather than
  imported.
* The credential comes from ``DRIFT_VERIFIER_TOKEN`` only — never from
  ``GITHUB_TOKEN``, the reconciler's own variable (reconciler/state/
  live_adapter.py). Two credentials, two blast radii.
* No write of any kind, anywhere, in any mode. Every method on
  ``VerifierState`` and ``LiveVerifierState`` below is a read.

Assertions register themselves with ``@assertion("<id>")`` from sibling
``assert_*.py`` modules (L3-P5-02, L3-P5-04, ...); this module supplies
only the registry, the state readers, and the ``--fixture``/``--only``/
``--summary``/``--live`` CLI (spec 53.1's own acceptance list).
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import pkgutil
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

import validators.drift as _drift_pkg

# Deliberately NOT `reconciler.fixtures` — this points at the same
# on-disk fixture *data* the reconciler reads (fixture-a is test data,
# not instrument logic), via this module's own reader below rather than
# reconciler.state.fixture_adapter.FixtureState.
_FIXTURES_ROOT = Path(__file__).resolve().parent.parent.parent / "reconciler" / "fixtures"

CREDENTIAL_ENV_VAR = "DRIFT_VERIFIER_TOKEN"
API_ROOT = "https://api.github.com"


@dataclass(frozen=True)
class AssertionResult:
    """What one assertion function returns.

    ``checked`` is the number of things the assertion actually examined
    (repositories, rulesets, ...) — printed on every VERIFY line so a
    silently narrowed check is visible the same way spec 53.1's
    comparison-count floor makes a narrowed comparator visible.
    """

    passed: bool
    checked: int
    detail: str = ""


AssertionFn = Callable[["VerifierState"], AssertionResult]

# assertion id -> its check(state) function. Populated purely as an
# import-time side effect of _discover_assertion_modules() below.
ASSERTIONS: dict[str, AssertionFn] = {}


def assertion(assertion_id: str) -> Callable[[AssertionFn], AssertionFn]:
    """Register `fn` under `assertion_id`.

    Raises ValueError on a duplicate id — a collision is a programming
    error, never a runtime condition to paper over.
    """

    def _register(fn: AssertionFn) -> AssertionFn:
        if assertion_id in ASSERTIONS:
            raise ValueError(f"assertion id {assertion_id!r} is already registered")
        ASSERTIONS[assertion_id] = fn
        return fn

    return _register


class CredentialMissing(RuntimeError):
    """Raised when --live is given but DRIFT_VERIFIER_TOKEN is unset."""


def read_credential() -> str | None:
    """The verifier's only credential source (spec 53.1). Never reads
    GITHUB_TOKEN or any other variable — a verifier that could fall back
    to the instrument's own credential would not be independent of it."""
    return os.environ.get(CREDENTIAL_ENV_VAR)


class VerifierState:
    """Read-only view over one fixture's actual/ state, plus the sliver
    of declared/ state assertions need to tell a human identity from a
    machine one (people.yaml).

    This is a deliberate, from-scratch reader — see this module's
    docstring on why it does not import reconciler.state.fixture_adapter.
    """

    def __init__(self, fixture: str, fixtures_root: Path | None = None):
        root = (fixtures_root or _FIXTURES_ROOT) / fixture
        actual_root = root / "actual"
        org_path = actual_root / "org.json"
        if not org_path.is_file():
            raise FileNotFoundError(f"fixture has no actual/org.json: {org_path}")
        self._actual_root = actual_root
        self._org: dict[str, Any] = json.loads(org_path.read_text(encoding="utf-8"))
        people_path = root / "declared" / "people.yaml"
        self._people: list[dict[str, Any]] = []
        if people_path.is_file():
            data = yaml.safe_load(people_path.read_text(encoding="utf-8")) or {}
            self._people = list(data.get("people", []))

    # -- reads used by assert_*.py modules ---------------------------------

    def known_logins(self) -> set[str]:
        """Every login people.yaml declares — the human side of the
        machine/human line every assertion here checks against."""
        return {p.get("github_login") for p in self._people if p.get("github_login")}

    def repos(self) -> list[str]:
        """Every repository with an actual CODEOWNERS file on disk —
        this is "every repository in any repository" (spec 53.1) as far
        as this fixture models it."""
        codeowners_dir = self._actual_root / "codeowners"
        if not codeowners_dir.is_dir():
            return []
        return sorted(p.stem for p in codeowners_dir.glob("*.CODEOWNERS"))

    def codeowners(self, repo: str) -> str:
        """The actual CODEOWNERS text — re-read from disk every call,
        never cached against a generator's output (spec 53.1: the
        verifier "re-reads CODEOWNERS from the actual state")."""
        path = self._actual_root / "codeowners" / f"{repo}.CODEOWNERS"
        if not path.is_file():
            raise FileNotFoundError(f"no CODEOWNERS fixture for repo {repo!r}: {path}")
        return path.read_text(encoding="utf-8")

    def rulesets(self) -> list[dict[str, Any]]:
        """Every ruleset in the actual org state, each carrying its own
        `name` and `bypass_actors` list."""
        return list(self._org.get("rulesets", []))

    def branch_protection(self, repo: str) -> dict[str, Any]:
        return dict(self._org.get("branch_protection", {}).get(repo, {}))


class LiveVerifierState:
    """Live GitHub REST reader, gated behind --live (spec 53.1's read-only
    fine-grained credential). Every method here issues a GET only — there
    is no method whose name begins ``set_``, ``write_``, ``create_``,
    ``delete_`` or ``update_``, the same discipline reconciler.state.
    live_adapter.LiveState follows, reimplemented independently here
    against DRIFT_VERIFIER_TOKEN rather than shared with it."""

    def __init__(self, org: str, *, live: bool, token: str | None = None, timeout: float = 10.0):
        if not live:
            raise CredentialMissing("LiveVerifierState requires live=True (set only by --live)")
        self._org = org
        self._token = token or read_credential()
        if not self._token:
            raise CredentialMissing(
                f"{CREDENTIAL_ENV_VAR} is not set; refusing to probe GitHub with no credential"
            )
        self._timeout = timeout

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
        with urllib.request.urlopen(req, timeout=self._timeout) as resp:  # noqa: S310 - read-only GET
            return json.loads(resp.read().decode("utf-8") or "null")

    def known_logins(self) -> set[str]:
        try:
            members = self._get(f"/orgs/{self._org}/members?per_page=100")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"GitHub API org members GET failed: {exc.code} {exc.reason}") from exc
        return {m["login"] for m in members}

    def repos(self) -> list[str]:
        try:
            repos = self._get(f"/orgs/{self._org}/repos?per_page=100")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"GitHub API repos GET failed: {exc.code} {exc.reason}") from exc
        return sorted(r["name"] for r in repos)

    def codeowners(self, repo: str) -> str:
        import base64

        try:
            data = self._get(f"/repos/{self._org}/{repo}/contents/.github/CODEOWNERS")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"GitHub API CODEOWNERS GET failed: {exc.code} {exc.reason}") from exc
        return base64.b64decode(data["content"]).decode("utf-8")

    def rulesets(self) -> list[dict[str, Any]]:
        try:
            return self._get(f"/orgs/{self._org}/rulesets")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"GitHub API rulesets GET failed: {exc.code} {exc.reason}") from exc

    def branch_protection(self, repo: str) -> dict[str, Any]:
        try:
            return self._get(f"/repos/{self._org}/{repo}/branches/main/protection")
        except urllib.error.HTTPError:
            return {}


def _discover_assertion_modules() -> None:
    """Import every validators/drift/assert_*.py module so its
    @assertion registration runs. Idempotent — re-importing an
    already-imported module is a cheap no-op for importlib. Restricted
    to the assert_ prefix so that sibling modules with their own
    __main__ (credential_bounds.py, liveness.py) are never imported as
    a side effect of running the verifier."""
    for info in pkgutil.iter_modules(_drift_pkg.__path__):
        if info.name.startswith("assert_"):
            importlib.import_module(f"validators.drift.{info.name}")


def run_assertions(
    ids: list[str], state: VerifierState | LiveVerifierState
) -> list[tuple[str, AssertionResult]]:
    """Run each assertion id in `ids` against `state`, in the order
    given. An assertion that raises is fail-closed: the raise becomes a
    failed result rather than a crash, because a verifier that dies
    silently on a bad read is exactly the "gate that appears to be
    working and is not" spec 40.1 warns against."""
    results: list[tuple[str, AssertionResult]] = []
    for assertion_id in ids:
        fn = ASSERTIONS[assertion_id]
        try:
            result = fn(state)
        except Exception as exc:  # noqa: BLE001 - deliberately broad, see docstring
            result = AssertionResult(passed=False, checked=0, detail=f"assertion crashed: {exc}")
        results.append((assertion_id, result))
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m validators.drift.verifier")
    parser.add_argument("--fixture", default=None)
    parser.add_argument("--only", action="append", default=None)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--org", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _discover_assertion_modules()

    if args.live:
        state: VerifierState | LiveVerifierState = LiveVerifierState(args.org or "", live=True)
    else:
        if not args.fixture:
            print("error: --fixture is required unless --live is given", file=sys.stderr)
            return 1
        state = VerifierState(args.fixture)

    if args.only:
        unknown = [a for a in args.only if a not in ASSERTIONS]
        if unknown:
            print(f"error: unknown assertion id(s): {', '.join(unknown)}", file=sys.stderr)
            return 1
        ids_to_run = list(args.only)
    else:
        ids_to_run = sorted(ASSERTIONS)

    results = run_assertions(ids_to_run, state)
    overall_pass = all(result.passed for _, result in results)

    if args.summary:
        for assertion_id, result in results:
            status = "pass" if result.passed else "fail"
            print(f"VERIFY {assertion_id} result={status} checked={result.checked}")
        print(f"VERIFIER result={'pass' if overall_pass else 'fail'} assertions={len(results)}")

    return 0 if overall_pass else 2


if __name__ == "__main__":
    # `python -m validators.drift.verifier` executes this file a second
    # time under the name "__main__" — a *different* module object from
    # "validators.drift.verifier", with its own separate ASSERTIONS
    # dict. Sibling assert_*.py modules always register into the
    # canonically-named module (they import it by its dotted path), so
    # routing execution through that same canonical import here, rather
    # than calling this file's own __main__-namespace main(), is what
    # keeps the registry a single source of truth instead of splitting
    # it in two.
    from validators.drift.verifier import main as _main

    sys.exit(_main())
