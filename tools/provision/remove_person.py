"""L3-P7-02: the `remove-person` operation (spec 12.2, 12.6; invariant 57; AT-017).

Composes the plan in exactly the §12.2 RECONCILIATION EXECUTES order,
eleven steps (`REMOVE_PERSON_STEPS` below). Every step is declarative,
matching change-role's own rule (invariant 55) - this operation edits
registry declared state and leaves the GitHub-side mutation to
reconciliation.

Two further rules, both transcribed from §12.2:

1. "the person record is retained, never deleted, and the identifier
   is never reused" - `retire_identifier()` / `identifier_available()`
   below are the only functions this module offers for that ledger, and
   neither can delete a record; there is no delete_person_record()
   anywhere in this file.
2. A departing succession designate in `topology.yaml` "is flagged
   immediately so succession is never left vacant by a departure" -
   `succession_alerts()` below.

Step 10 (`orphan_detection`) invokes the real Phase 2 orphan scan
(`reconciler.orphans.run_group` across all three §12.2 groups) rather
than a placeholder count. `dismiss()` is the enforcement point for
invariant 57 - "Blocking orphans ... cannot be dismissed without
resolution": it raises for any Blocking finding and only ever succeeds
for a non-Blocking one. There is no other function in this module that
drops a finding from the set `run_orphan_detection()` returns.
"""

from __future__ import annotations

from dataclasses import dataclass

from reconciler.orphans import OrphanContext, OrphanFinding, run_group
from reconciler.orphans.types import GROUPS
from tools.provision.plan import Plan, Step, StepKind

# §12.2, RECONCILIATION EXECUTES block, verbatim order.
REMOVE_PERSON_STEPS: tuple[str, ...] = (
    "remove_from_organisation",
    "remove_from_every_team",
    "revoke_every_environment_access",
    "revoke_production_capability",
    "deactivate_ai_runtime",
    "stop_self_view_and_retire_key",
    "remove_from_reviewer_matrix",
    "recalculate_ownership",
    "recalculate_incident_responders",
    "orphan_detection",
    "exit_record",
)

_DESCRIPTIONS: dict[str, str] = {
    "remove_from_organisation": "remove {login} from the organisation",
    "remove_from_every_team": "remove {login} from every GitHub Team",
    "revoke_every_environment_access": "revoke every environment access held by {login}",
    "revoke_production_capability": "revoke {login}'s production capability",
    "deactivate_ai_runtime": "deactivate {login}'s AI runtime",
    "stop_self_view_and_retire_key": (
        "stop self-view generation for {login} and retire their registered "
        "self-view key material (spec 90.6)"
    ),
    "remove_from_reviewer_matrix": "remove {login} from the reviewer matrix",
    "recalculate_ownership": "recalculate ownership for slots {login} held",
    "recalculate_incident_responders": "recalculate incident-responder assignments for slots {login} held",
    "orphan_detection": "run the sixteen-type orphan scan (spec 12.2) following {login}'s removal",
    "exit_record": "complete the exit record for {login}",
}


class BlockingOrphanUnresolved(RuntimeError):
    """Raised by dismiss() for a Blocking orphan - invariant 57 forbids this."""


@dataclass(frozen=True)
class SuccessionAlert:
    """A departing succession designate, flagged immediately (spec 12.2)."""

    login: str
    slot: str
    message: str


def build_remove_person_plan(login: str) -> Plan:
    """Build the eleven-step remove-person plan (spec 12.2), in order.

    Every step is `StepKind.WRITE` (each edits declared registry state
    for reconciliation to apply, per invariant 55); none is `MANUAL`.
    """
    steps = [
        Step(step_id, _DESCRIPTIONS[step_id].format(login=login), StepKind.WRITE)
        for step_id in REMOVE_PERSON_STEPS
    ]
    return Plan(steps=steps)


def run_orphan_detection(ctx: OrphanContext) -> tuple[list[OrphanFinding], int]:
    """Step 10: the full sixteen-type scan, all three §12.2 groups.

    This is the actual Phase 2 orphan detector (`reconciler.orphans`),
    not a placeholder - remove-person's own step 10 runs the same
    detectors `reconciler.cli orphans` does, across `ownership`,
    `assets` and `governance`.
    """
    all_findings: list[OrphanFinding] = []
    total_compared = 0
    for group in sorted(GROUPS):
        findings, compared = run_group(group, ctx)
        all_findings.extend(findings)
        total_compared += compared
    return all_findings, total_compared


def dismiss(finding: OrphanFinding, *, reason: str) -> OrphanFinding:
    """Acknowledge a non-Blocking orphan finding as reviewed.

    Invariant 57: "Blocking orphans ... cannot be dismissed without
    resolution." Every Blocking finding raises here, unconditionally -
    there is no `force=` escape hatch and no caller-supplied bypass.
    """
    if finding.orphan_severity == "Blocking":
        raise BlockingOrphanUnresolved(
            f"orphan {finding.subject!r} ({finding.name}) is Blocking-severity "
            "and cannot be dismissed without resolution (spec 12.2; invariant 57)"
        )
    return finding


# §12.2 final line: "the person record is retained, never deleted, and
# the identifier is never reused." This module offers no function that
# deletes a person record. `retired_logins` is a plain, caller-owned
# set (no hidden global mutable state here) so a real system can back
# it with a persistent ledger without this module needing to change.


def retire_identifier(login: str, retired_logins: set[str]) -> set[str]:
    """Return `retired_logins` with `login` added - never removed."""
    return retired_logins | {login}


def identifier_available(login: str, retired_logins: frozenset[str]) -> bool:
    """False forever, once `login` has been retired - the identifier is
    never reused (spec 12.2)."""
    return login not in retired_logins


def succession_alerts(login: str, topology: dict | None) -> tuple[SuccessionAlert, ...]:
    """Flag every succession slot in `topology` naming `login` as its
    designate, immediately (spec 12.2: "succession is never left vacant
    by a departure"). `topology` is the parsed contents of
    `topology.yaml`'s succession block - `{slot: designate_login}`."""
    if not topology:
        return ()
    succession = topology.get("succession") or {}
    return tuple(
        SuccessionAlert(
            login=login,
            slot=slot,
            message=(
                f"{login} is departing and is the succession designate for "
                f"{slot!r}: flagged immediately so succession is never left "
                "vacant by this departure (spec 12.2)."
            ),
        )
        for slot, designate in succession.items()
        if designate == login
    )
