"""L3-P5-02: verifier assertion A — no machine identity in any CODEOWNERS
(spec 53.1: "asserting that no machine identity appears in any CODEOWNERS
file in any repository"; §11.3; §37.3).

Registers assertion id ``codeowners_human_only``. For every repository
the verifier's own state knows about, this re-reads the *actual*
CODEOWNERS file from disk (VerifierState.codeowners — never the
reconciler's in-memory or generated copy) and fails if any owner entry
is a machine identity: a login ending ``[bot]``, or a login not present
in ``people.yaml`` at all. ``checked`` is the number of repositories
examined, regardless of outcome — every repository is read even after
the first bad one is found, so a partial run never under-reports what
it looked at.
"""

from __future__ import annotations

from validators.drift.verifier import AssertionResult, VerifierState, assertion

_MACHINE_SUFFIX = "[bot]"


def _owners(codeowners_text: str) -> list[str]:
    owners: list[str] = []
    for line in codeowners_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        owners.extend(o.lstrip("@") for o in parts[1:])
    return owners


def _is_machine_identity(login: str, known_human_logins: set[str]) -> bool:
    return login.endswith(_MACHINE_SUFFIX) or login not in known_human_logins


@assertion("codeowners_human_only")
def check(state: VerifierState) -> AssertionResult:
    repos = state.repos()
    known = state.known_logins()

    offending: list[str] = []
    for repo in repos:
        text = state.codeowners(repo)
        machine_owners = sorted({o for o in _owners(text) if _is_machine_identity(o, known)})
        if machine_owners:
            offending.append(f"{repo}: {machine_owners}")

    return AssertionResult(
        passed=not offending,
        checked=len(repos),
        detail="; ".join(offending),
    )
