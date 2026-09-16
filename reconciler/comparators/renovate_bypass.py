"""L3-P1-11: Renovate bypass ruleset split (spec 53.1 row 14; D89).

The ruleset carrying the `renovate-path-guard` required status check is
the compensating control for Renovate's pull-request ruleset. If its
bypass_actors list is non-empty, the compensating control compensates
for nothing - D89: "a bypass actor is exempt from every rule in the
ruleset it is listed on" - so that is Blocking. The pull-request
ruleset itself may legitimately list the Renovate app as a bypass actor
and is never a finding here.
"""

from __future__ import annotations

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator

_GUARD_CHECK = "renovate-path-guard"


@comparator("renovate_bypass", fail_class=DriftClass.BLOCKING)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    first_seen = f"{as_of.isoformat()}T00:00:00Z"
    rulesets = actual.rulesets()

    for ruleset in rulesets:
        rules = ruleset.get("rules") or []
        if not any(_GUARD_CHECK in str(rule) for rule in rules):
            continue
        bypass_actors = ruleset.get("bypass_actors") or []
        if bypass_actors:
            findings.append(
                Finding(
                    id=f"renovate_bypass:{ruleset.get('name')}",
                    comparator="renovate_bypass",
                    scope=ruleset.get("name"),
                    drift_class=DriftClass.BLOCKING,
                    level=Level.BLOCK,
                    evidence=(
                        f"ruleset {ruleset.get('name')!r} carries the {_GUARD_CHECK} "
                        f"required check but lists bypass_actors={bypass_actors}, which "
                        "exempts them from that check too"
                    ),
                    first_seen=first_seen,
                )
            )

    return findings, len(rulesets)
