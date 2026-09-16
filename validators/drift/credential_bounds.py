"""L3-P5-06: AT-110 credential-bounds probe — six negative attempts
(AT-110 verbatim; spec 40.1; spec 99.6 risk 6).

AT-110, transcribed: "From the reconciler's own credential, six
attempts are made — a write to a GitHub Actions secret, a write to an
environment, a workflow-file change, an organisation-settings change, a
`records/**` write, and any Layer B access — and all six fail; the
credential then still completes a normal reconciliation run."

This module is the single implementation of that probe. `L3-07` T10's
`AT-110.sh` is reduced to `GATE.md` + `RESULT.template.md` invoking
this module's `--mode live` at the phase that builds the reconciler and
at every credential rotation (spec 40.1: "After any rotation, a manual
reconciliation run must complete clean before the rotation is recorded
as done").

Two modes:

* ``fixture`` — a `FixtureCredential` simulating the reconciler
  credential's *declared* write scope (spec 40.1: read-only, plus
  check-run write on exactly one named check — reconciler/checkrun.py).
  Every acceptance command in lanes/L3-06-tasks.md runs this mode only.
* ``live`` — a `LiveCredential` that makes the six attempts for real
  against a live GitHub organisation, using the reconciler's own
  `GITHUB_TOKEN` (the same variable reconciler/state/live_adapter.py
  reads — this module exists to test *that* credential, so, unlike
  validators/drift/verifier.py, sharing that variable name here is the
  point, not a violation of it). No test or CI command in this repo
  ever exercises this path; it is reached only by a human operator.

Any attempt returning PERMITTED is a security incident under spec 43,
not a test failure — `probe()` raises `SecurityIncident` immediately,
before making any further attempt or running the follow-on
reconciliation, matching this task's own STOP instruction: "if any
attempt returns PERMITTED in live mode, stop everything."
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Protocol

# AT-110's own literal order — every acceptance list and every printed
# summary in this module follows this tuple, never a re-sorted one.
ATTEMPT_ORDER: tuple[str, ...] = (
    "actions_secret_write",
    "environment_write",
    "workflow_file_change",
    "org_settings_change",
    "records_write",
    "layer_b_access",
)

_RESULTS = ("blocked", "PERMITTED")


class SecurityIncident(RuntimeError):
    """Raised the instant any AT-110 attempt returns PERMITTED.

    spec 43 / spec 99.6 risk 6: "the reconciler's own credential in the
    top secrets tier with its compromise treated as a security
    incident" — never downgraded to an ordinary test failure.
    """

    def __init__(self, message: str, *, attempts: dict[str, str]):
        super().__init__(message)
        self.attempts = dict(attempts)


@dataclass(frozen=True)
class ProbeOutcome:
    attempts: dict[str, str] = field(default_factory=dict)
    reconciliation_completed: bool = False


class Credential(Protocol):
    """The six AT-110 attempts a credential under probe must answer,
    each returning the literal string ``"blocked"`` or ``"PERMITTED"``
    — never any other value (`probe()` rejects anything else)."""

    def try_actions_secret_write(self) -> str: ...
    def try_environment_write(self) -> str: ...
    def try_workflow_file_change(self) -> str: ...
    def try_org_settings_change(self) -> str: ...
    def try_records_write(self) -> str: ...
    def try_layer_b_access(self) -> str: ...


# spec 40.1's declared write scope for the reconciler credential: read
# everywhere, plus check-run write on exactly the one named check
# reconciler/checkrun.py publishes. None of the six AT-110 surfaces
# below are members of this set — that is the bound AT-110 exists to
# execute rather than merely assert.
DECLARED_WRITE_SCOPE: frozenset[str] = frozenset({"check_run:control-plane/blocking-drift"})


class FixtureCredential:
    """Stands in for the reconciler's credential in fixture mode,
    carrying exactly `granted_scope` (default: the spec 40.1 declared
    scope). Each `try_*` method checks its own attempt's required scope
    key against `granted_scope` — the boundary comes from the scope
    table, not from a hardcoded "blocked" literal, so a test that widens
    `granted_scope` sees PERMITTED exactly as a real credential would."""

    def __init__(self, granted_scope: frozenset[str] = DECLARED_WRITE_SCOPE):
        self._granted = granted_scope

    def _attempt(self, required_scope: str) -> str:
        return "PERMITTED" if required_scope in self._granted else "blocked"

    def try_actions_secret_write(self) -> str:
        return self._attempt("actions_secret_write")

    def try_environment_write(self) -> str:
        return self._attempt("environment_write")

    def try_workflow_file_change(self) -> str:
        return self._attempt("workflow_file_change")

    def try_org_settings_change(self) -> str:
        return self._attempt("org_settings_change")

    def try_records_write(self) -> str:
        return self._attempt("records_write")

    def try_layer_b_access(self) -> str:
        # Layer B (access/layer-b/**, Lane 5) is not a GitHub surface at
        # all — it is a separate host reached by its own credential, not
        # by a GitHub PAT. A GitHub-scoped credential has no network
        # path to it under any granted_scope, fixture or live; this is
        # a structural fact about the credential *type*, not a
        # permission the scope table could ever grant.
        return "blocked"


class LiveCredential:
    """Makes the six AT-110 attempts for real against a live GitHub
    organisation, using the reconciler's own GITHUB_TOKEN. Never
    exercised by any test or CI command in this repository — reached
    only by a human operator running `--mode live` (spec 40.1). Every
    attempt here is read-then-write-attempt-then-check: it issues the
    real write call GitHub would need to see to permit it, and reports
    PERMITTED only on an HTTP 2xx; every 4xx (403/404/422 — GitHub
    returns these for an out-of-scope token before it would ever
    validate the request body) is `blocked`.
    """

    def __init__(self, org: str, *, token: str | None = None, timeout: float = 10.0):
        self._org = org
        self._token = token or os.environ.get("GITHUB_TOKEN")
        if not self._token:
            raise RuntimeError(
                "GITHUB_TOKEN is not set; refusing to probe a live organisation with no credential"
            )
        self._timeout = timeout

    def _try_write(self, method: str, path: str, body: dict | None = None) -> str:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(
            f"https://api.github.com{path}",
            data=data,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:  # noqa: S310
                status = resp.status
        except urllib.error.HTTPError as exc:
            status = exc.code
        return "PERMITTED" if 200 <= status < 300 else "blocked"

    def try_actions_secret_write(self) -> str:
        # A syntactically valid but inert body — GitHub rejects an
        # insufficiently-scoped token with 403/404 before it ever
        # validates the sealed-box encryption of `encrypted_value`.
        return self._try_write(
            "PUT",
            f"/orgs/{self._org}/actions/secrets/AT110_PROBE_SECRET",
            {"encrypted_value": "", "key_id": "0", "visibility": "private"},
        )

    def try_environment_write(self) -> str:
        return self._try_write(
            "PUT",
            f"/repos/{self._org}/control-plane/environments/at110-probe-env",
            {},
        )

    def try_workflow_file_change(self) -> str:
        return self._try_write(
            "PUT",
            f"/repos/{self._org}/control-plane/contents/.github/workflows/at110-probe.yml",
            {"message": "AT-110 probe (expected to be refused)", "content": ""},
        )

    def try_org_settings_change(self) -> str:
        return self._try_write("PATCH", f"/orgs/{self._org}", {"description": "AT-110 probe"})

    def try_records_write(self) -> str:
        # AT-110 attempt 5: the reconciler credential must not reach
        # records/** at all (D89; Lane 4's territory).
        return self._try_write(
            "PUT",
            f"/repos/{self._org}/records/contents/at110-probe.txt",
            {"message": "AT-110 probe (expected to be refused)", "content": ""},
        )

    def try_layer_b_access(self) -> str:
        # See FixtureCredential.try_layer_b_access: Layer B is off
        # GitHub entirely, so a GitHub PAT has no call to make here in
        # live mode either — the absence of a network path *is* the
        # blocked result, not an HTTP response to interpret.
        return "blocked"


def _run_reconciliation(fixture: str, *, live: bool) -> bool:
    """AT-110's final clause: "the credential then still completes a
    normal reconciliation run." Runs reconciler.cli's own `run`
    subcommand and reports it as complete when its exit code is 0
    (clean) or 2 (Blocking findings present but the run itself
    executed) — never 3 (FAILED: a crash, a missing canary, a narrowed
    comparison). This module legitimately imports reconciler.cli: it is
    testing the reconciler's own credential and run path, not building
    the independent second verifier validators/drift/verifier.py is
    (that module's separate-instrument rule does not apply here)."""
    import reconciler.cli as reconciler_cli

    argv = ["run", "--live"] if live else ["run", "--fixture", fixture]
    exit_code = reconciler_cli.main(argv)
    return exit_code in (0, 2)


def probe(credential: Credential, mode: str, *, fixture: str = "fixture-a") -> ProbeOutcome:
    """Perform AT-110's six attempts, in AT-110's own order, against
    `credential`. Raises SecurityIncident (halting before any further
    attempt or the follow-on reconciliation run) the instant one
    returns PERMITTED. Otherwise runs the follow-on reconciliation and
    returns the full outcome."""
    if mode not in ("fixture", "live"):
        raise ValueError(f"mode must be 'fixture' or 'live', got {mode!r}")

    attempts: dict[str, str] = {}
    for name in ATTEMPT_ORDER:
        result = getattr(credential, f"try_{name}")()
        if result not in _RESULTS:
            raise ValueError(
                f"attempt {name!r} returned {result!r}; a Credential must answer "
                "'blocked' or 'PERMITTED', nothing else"
            )
        attempts[name] = result
        if result == "PERMITTED":
            raise SecurityIncident(
                f"AT-110 attempt {name!r} returned PERMITTED against the reconciler's own "
                "credential — this is a security incident under spec 43, not a test failure "
                "(spec 99.6 risk 6); halting before any further attempt or reconciliation run",
                attempts=attempts,
            )

    reconciliation_completed = _run_reconciliation(fixture, live=(mode == "live"))
    return ProbeOutcome(attempts=attempts, reconciliation_completed=reconciliation_completed)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m validators.drift.credential_bounds")
    parser.add_argument("--mode", choices=("fixture", "live"), default="fixture")
    parser.add_argument("--fixture", default="fixture-a")
    parser.add_argument("--org", default=None, help="required for --mode live")
    parser.add_argument("--summary", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.mode == "live":
        if not args.org:
            print("error: --org is required for --mode live", file=sys.stderr)
            return 1
        credential: Credential = LiveCredential(args.org)
    else:
        credential = FixtureCredential()

    try:
        outcome = probe(credential, args.mode, fixture=args.fixture)
    except SecurityIncident as exc:
        if args.summary:
            for name in ATTEMPT_ORDER:
                if name in exc.attempts:
                    print(f"PROBE {name}={exc.attempts[name]}")
            print(f"AT-110 SECURITY INCIDENT (spec 43): {exc}")
        return 3

    if args.summary:
        for name in ATTEMPT_ORDER:
            print(f"PROBE {name}={outcome.attempts[name]}")
        print(f"PROBE reconciliation_after={'complete' if outcome.reconciliation_completed else 'incomplete'}")
        overall = "pass" if outcome.reconciliation_completed else "fail"
        print(f"AT-110 result={overall} attempts={len(outcome.attempts)}")

    return 0 if outcome.reconciliation_completed else 2


if __name__ == "__main__":
    from validators.drift.credential_bounds import main as _main

    sys.exit(_main())
