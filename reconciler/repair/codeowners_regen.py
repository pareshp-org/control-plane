"""L3-P6-04: repair class: CODEOWNERS regeneration (spec 53.1 row 4;
spec 53.2 Level 3; spec 11.3).

Consumes `codeowners` findings (both `machine_identity_present` and
`hand_edited` - the fix is identical for either: replace the actual
file with what `tools.provision.codeowners.generate` produces from the
declared registries) and regenerates through that one generator, never
a second implementation of the same four ownership rules.

generate()'s machine-identity refusal (L3-P4-02) covers the repair
path automatically, by construction: if the *declared* assignments
themselves would put a machine identity in the file, `generate()`
raises `MachineIdentityInCodeowners` before returning any string at
all. This module does not catch that - it propagates, so a poisoned
registry raises rather than silently producing (or writing) anything.
"""

from __future__ import annotations

from typing import Any

from reconciler.model import Finding
from reconciler.repair import Repair
from reconciler.repair.stricter import permitted
from tools.provision.codeowners import generate

CONTROL_KIND = "codeowners_content"


def repair(findings: list[Finding], actual: Any, registries: str, *, enabled: bool) -> list[Repair]:
    """`findings` is the Phase-1 `codeowners` comparator's output for
    one run; `actual` is the same GitHubState that run compared
    against (read here only for the pre-repair file text); `registries`
    is the fixture (or, once one exists, live org) name `generate()`
    reads declared state from - the same name the run itself used."""
    repairs: list[Repair] = []
    if not enabled:
        return repairs

    for finding in findings:
        if finding.comparator != "codeowners":
            continue
        product = finding.scope
        before = actual.codeowners(product)
        # Raises MachineIdentityInCodeowners here, uncaught, if the
        # declared assignments would emit one - nothing is written or
        # returned in that case (see module docstring).
        after = generate(product, registries)

        ok, reason = permitted(after, before, CONTROL_KIND)
        if not ok:
            continue

        repairs.append(
            Repair(
                repair_class="codeowners_regen",
                finding_id=finding.id,
                scope=product,
                before=before,
                after=after,
                permitted_reason=reason
                or f"{product} CODEOWNERS regenerated from its declared assignments (spec 11.3)",
                compensating_action=f"restore the pre-repair CODEOWNERS blob for {product} from the repair record",
            )
        )

    return repairs
