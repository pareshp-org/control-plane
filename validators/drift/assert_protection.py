"""L3-P5-03: verifier assertion B — branch protection and ruleset JSON
match the committed template (spec 53.1: "that branch protection and
ruleset JSON match the committed template"; §11.3).

Registers assertion id ``protection_matches_template``. For every
repository the verifier's own state knows about, this byte-normalises
the actual branch-protection JSON (``VerifierState.branch_protection`` —
GitHub's REST branch-protection representation, which is what a
repository's ruleset-backed protection also serialises to) and compares
it against the **committed** template
(``VerifierState.committed_template("branch-protection")`` —
``declared/templates/branch-protection.json`` read fresh from disk,
never the reconciler's in-memory copy).

This is deliberately not the reconciler's stricter-only comparator
(``reconciler/comparators/branch_protection.py``, L3-P1-06): there is
no "actual stricter than declared is fine" carve-out here. This
assertion asks only whether the wall matches the committed template,
in either direction — any difference, weaker or stricter, fails. A
verifier that let "stricter" through unexamined could be blinded by
the exact same class of bug (a repository quietly drifting away from
what was reviewed and committed) that the reconciler's own comparator
exists to catch on the other side of §53.3's line.

``checked`` is the number of repositories examined, regardless of
outcome — mirrors ``assert_codeowners.py``'s own "every repository is
read even after the first bad one is found" rule.
"""

from __future__ import annotations

import json
from typing import Any

from validators.drift.verifier import AssertionResult, VerifierState, assertion


def _canonical(value: Any) -> str:
    """Byte-normalised form used for the comparison: canonical key
    order, canonical separators — the same document compares equal
    regardless of how its keys happened to be ordered on either side."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


@assertion("protection_matches_template")
def check(state: VerifierState) -> AssertionResult:
    template = state.committed_template("branch-protection")
    expected = _canonical(template)

    repos = state.repos()
    mismatched: list[str] = []
    for repo in repos:
        actual = state.branch_protection(repo)
        if _canonical(actual) != expected:
            mismatched.append(repo)

    return AssertionResult(
        passed=not mismatched,
        checked=len(repos),
        detail=(
            f"{sorted(mismatched)} do not byte-match "
            "declared/templates/branch-protection.json"
            if mismatched
            else ""
        ),
    )
