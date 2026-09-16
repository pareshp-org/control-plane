"""L3-P6-06: repair class: expired assignment and expired access
removal (spec 53.1 row 11; spec 53.2 Level 3; spec 101 invariant 58;
AT-008, AT-018, AT-036).

Two inputs, both time-bounded grants that must not survive their own
expiry through inaction (spec 10.2):

* `revoke_expired_assignments()` consumes the Phase-1 `expiry`
  comparator's `:expired` findings (a temporary_assignments row whose
  end_date has passed but whose holder is still on the product Team)
  and removes the Team access it conferred - AT-018: "Reconciliation
  removes it without human action; access is revoked and capacity
  recalculated."
* `revoke_expired_exceptions()` consumes declared exception entries
  directly (there is no Phase-1 comparator for exceptions in this
  lane's registry) and revokes any that are past `expires` - AT-036:
  "Reconciliation revokes it with no human action." An exception whose
  entry does not declare what access it granted cannot be
  mechanically revoked; per AT-037 that becomes a Blocking finding on
  its expiry date rather than a silent skip.

Both revocations are modelled through `permitted()`'s `team_membership`
control kind: removing an access grant nobody currently declares is
the same whitelist-membership correction team_sync.py performs for
Team drift, and it is exempt from the graduated strictness comparison
for the same reason (reconciler/repair/stricter.py's module docstring).

Per spec 26.4, this class writes directly under the reconciler
credential and bypasses the human owner-review lane deliberately -
"routing these machine-derived transitions through human reviewers
would queue the 'no human action required' expiry guarantees behind
the very people they are designed not to need."
"""

from __future__ import annotations

from datetime import date
from typing import Any, Mapping, Sequence

from reconciler.model import DriftClass, Finding, Level
from reconciler.repair import Repair
from reconciler.repair.stricter import permitted

CONTROL_KIND = "team_membership"


def revoke_expired_assignments(findings: Sequence[Finding], *, enabled: bool) -> list[Repair]:
    """`findings` is the Phase-1 `expiry` comparator's output for one
    run. Only its Blocking `:expired` findings are in scope here - the
    Amber `:expiring_soon` warnings are not yet actionable (spec 10.1's
    advance-warning window) and are left untouched."""
    repairs: list[Repair] = []
    if not enabled:
        return repairs

    for finding in findings:
        if finding.comparator != "expiry" or not finding.id.endswith(":expired"):
            continue
        product, person = finding.scope.split(":", 1)
        ok, reason = permitted(False, True, CONTROL_KIND)
        if not ok:
            continue
        repairs.append(
            Repair(
                repair_class="expiry_revoke",
                finding_id=finding.id,
                scope=finding.scope,
                before={"team_member": True},
                after={"team_member": False},
                permitted_reason=reason
                or f"{person}'s expired temporary assignment on {product} revoked without human action (AT-018)",
                compensating_action=(
                    f"re-grant {person} access to {product} only through the registry-change lane "
                    "of spec 26.4 - the reconciler never re-grants"
                ),
            )
        )
    return repairs


def revoke_expired_exceptions(
    exceptions: Sequence[Mapping[str, Any]], as_of: date, *, enabled: bool
) -> tuple[list[Repair], list[Finding]]:
    """`exceptions` is every declared exception entry (fixture-a's
    declared/exceptions.yaml shape: id, requester, authority, expires,
    and - when the exception actually grants something mechanically
    revocable - a `grants` field). Returns (repairs, escalations):
    escalations are Blocking findings for an expired exception this
    class cannot mechanically revoke (AT-037), never a silent skip.
    """
    repairs: list[Repair] = []
    escalations: list[Finding] = []
    if not enabled:
        return repairs, escalations

    first_seen = f"{as_of.isoformat()}T00:00:00Z"

    for exc in exceptions:
        expires_raw = exc.get("expires")
        if not expires_raw or date.fromisoformat(expires_raw) >= as_of:
            continue
        exc_id = exc.get("id", "unknown")
        scope = str(exc.get("requester") or exc_id)
        grants = exc.get("grants")

        if not grants:
            escalations.append(
                Finding(
                    id=f"exception:{exc_id}:cannot_auto_revoke",
                    comparator="expiry_revoke",
                    scope=scope,
                    drift_class=DriftClass.BLOCKING,
                    level=Level.BLOCK,
                    evidence=(
                        f"exception {exc_id} expired {expires_raw} and declares no `grants` field "
                        "for this class to revoke mechanically; escalated to Blocking drift on its "
                        "expiry date rather than skipped silently (AT-037)"
                    ),
                    first_seen=first_seen,
                )
            )
            continue

        ok, reason = permitted(False, True, CONTROL_KIND)
        if not ok:
            continue
        repairs.append(
            Repair(
                repair_class="expiry_revoke",
                finding_id=f"exception:{exc_id}",
                scope=scope,
                before={"grants": grants},
                after={"grants": None},
                permitted_reason=reason or f"exception {exc_id} expired {expires_raw}; revoked with no human action (AT-036)",
                compensating_action=(
                    f"re-grant {grants!r} to {scope} only through the registry-change lane of "
                    "spec 26.4 - the reconciler never re-grants"
                ),
            )
        )

    return repairs, escalations


def repair(
    assignment_findings: Sequence[Finding],
    exceptions: Sequence[Mapping[str, Any]],
    as_of: date,
    *,
    enabled: bool,
) -> tuple[list[Repair], list[Finding]]:
    repairs = list(revoke_expired_assignments(assignment_findings, enabled=enabled))
    exception_repairs, escalations = revoke_expired_exceptions(exceptions, as_of, enabled=enabled)
    repairs.extend(exception_repairs)
    return repairs, escalations
