"""L3-P3-02: `control-plane/blocking-drift` check-run publisher
(spec 11.3: the required status check "the reconciler holds at
failure while Blocking-class drift is open against the product";
spec 40.1: "the reconciler credential additionally holds check-run
write on product repositories, used for exactly one named check ...
That is not a further machine write path: a check run carries status
only - it writes no repository content, approves nothing, and
satisfies no gate a human is required to satisfy."; spec 53.2 Level 4).

`publish()` never touches any of the other machine write paths named
by spec 40 (credential material, deployment environments, workflow
definitions) - the only side effect this module is capable of, on its
live path, is naming a check-run conclusion through an injected
`client`, and that path is reached only with `dry_run=False` supplied
explicitly.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Iterable, Protocol

from reconciler.model import DriftClass, Finding

# The one name spec 40.1 authorises: "used for exactly one named
# check." No other string is ever emitted by this module.
CHECK_NAME = "control-plane/blocking-drift"


class InvalidCheckName(ValueError):
    """Raised when asked to publish under any name other than CHECK_NAME.

    Spec 40.1: "the reconciler credential additionally holds check-run
    write on product repositories, used for exactly one named check."
    """


class CheckRunClient(Protocol):
    """The minimal live-write surface this module is allowed to call.
    Deliberately narrower than a full GitHub client: one method, one
    named check, status only."""

    def create_check_run(self, *, repo: str, name: str, conclusion: str) -> Any: ...


@dataclasses.dataclass(frozen=True)
class CheckRunResult:
    repo: str
    name: str
    conclusion: str  # "failure" | "success"
    dry_run: bool
    published: bool  # True only once a live client call actually happened


def _conclusion_for(findings: Iterable[Finding]) -> str:
    """spec 11.3: failure while any Blocking-class finding is open
    against the product; success otherwise. `findings` is the caller's
    already-scoped set for one repository/product - this module makes
    no assumption about how a Finding names the repository it belongs
    to, since that convention varies by comparator (spec 53.1)."""
    any_blocking = any(f.drift_class == DriftClass.BLOCKING for f in findings)
    return "failure" if any_blocking else "success"


def publish(
    repo: str,
    findings: Iterable[Finding],
    dry_run: bool = True,
    *,
    name: str = CHECK_NAME,
    client: CheckRunClient | None = None,
) -> CheckRunResult:
    """Compute (and, only if `dry_run=False`, actually publish) the
    `control-plane/blocking-drift` check-run conclusion for `repo`.

    `dry_run=True` is the default; the live path - the one call this
    module makes to `client.create_check_run()` - is reached only when
    the caller explicitly passes `dry_run=False` together with a
    `client`. Passing any `name` other than CHECK_NAME raises
    InvalidCheckName before anything else runs: this publisher may
    emit only that one check name (spec 40.1), so a second name is
    refused rather than silently accepted.
    """
    if name != CHECK_NAME:
        raise InvalidCheckName(
            f"the publisher may emit only {CHECK_NAME!r} (spec 40.1: "
            f"'exactly one named check'); got {name!r}"
        )

    conclusion = _conclusion_for(findings)
    published = False

    if not dry_run:
        if client is None:
            raise ValueError("publish(dry_run=False) requires a `client`")
        client.create_check_run(repo=repo, name=name, conclusion=conclusion)
        published = True

    return CheckRunResult(
        repo=repo, name=name, conclusion=conclusion, dry_run=dry_run, published=published
    )
