"""L3-P0-CMP10 - product.yaml lifecycle versus Renovate, monitoring and
CI configuration.

Spec 53.1 row 10: "Auto-repair where safe; alert otherwise" (Amber;
Level-3 repair proposed where safe, Level-2 alert otherwise). Ported
from lanes/L3-01-diff-engine.md task L3-01-12 by Session 12
(FD-B1-L3 corollary) - see the L3-P0-CMP10 block in lanes/L3-06-tasks.md,
which is the authoritative version of this task.

The safe/unsafe split is read from lifecycle-expectations.yaml, never
decided here - spec 53.4: "Class assignment lives in configuration and
is reviewable; it is not decided ad hoc during an incident." A safe row
proposes a Level-3 repair - proposed only, rule R1; nothing is ever
applied in this phase. An unsafe row raises a Level-2 (Amber) alert and
proposes nothing. Exactly two checks are unsafe: `repository-archived-
flag` and `ci-workflow-present` - neither is on spec 53.2's closed
Level-3 "Applies to" list.

Read-surface note: reconciler/state/port.py's GitHubState (L3-P0-06)
exposes exactly twelve read methods and has no literal `repo.archived`
field or arbitrary-file-content read - both post-date this port's
closed method list. `repository-archived-flag` therefore reads
published check-run activity (`check_runs`) as the available proxy for
"does this repository still look alive", the same directional question
the spec's archived-flag row asks, rather than a GitHub `archived`
field this phase's port does not expose. `ci-workflow-present` and the
Renovate-schedule check both read `workflow_files`, which is on the
port. `alert-channel-declared` reads the product's own declared
`observability.alert_channel`. If a future task adds a literal
`repo.archived` read to GitHubState, `repository-archived-flag` should
be repointed at it - this is called out here so that repointing is not
mistaken for scope creep when it happens.
"""

from __future__ import annotations

import pathlib
from typing import Any

import yaml

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator

TABLE_PATH = pathlib.Path(__file__).resolve().parent / "lifecycle-expectations.yaml"

_RENOVATE_WORKFLOW = "renovate.yml"
_CI_WORKFLOW = "ci.yml"


def load_table() -> dict[str, Any]:
    """The CMP-10 lifecycle-to-expected-configuration table (spec 53.1
    row 10 / 53.4: class assignment lives in configuration, not code)."""
    return yaml.safe_load(TABLE_PATH.read_text(encoding="utf-8"))


def _observe(actual: Any, product_yaml: dict[str, Any], product: str) -> dict[str, Any]:
    """The four observed facts CMP-10's checks compare against the
    table, each read through the twelve-method GitHubState port or the
    product's own declared configuration - see the module docstring's
    read-surface note for `repo_archived`."""
    workflows = actual.workflow_files(product)
    has_check_run_activity = bool(actual.check_runs(product))
    alert_channel = (product_yaml.get("observability") or {}).get("alert_channel")
    return {
        "renovate_schedule": "present" if _RENOVATE_WORKFLOW in workflows else "absent",
        "repo_archived": not has_check_run_activity,
        "alert_channel": "present" if alert_channel else "absent",
        "ci_workflow": "present" if _CI_WORKFLOW in workflows else "absent",
    }


def _propose_repair(check_id: str, product: str, target: Any) -> dict[str, Any]:
    """Build a Level-3 repair proposal (rule R1): logged in evidence,
    never executed - this phase applies nothing, ever."""
    return {
        "class": "lifecycle_configuration_sync",
        "check": check_id,
        "product": product,
        "target": target,
        "applied": False,
    }


@comparator("cmp_10_lifecycle", fail_class=DriftClass.AMBER)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    first_seen = f"{as_of.isoformat()}T00:00:00Z"
    table = load_table()
    states = table["states"]
    compared = 0

    for product_name, product_yaml in declared.products.items():
        state = product_yaml.get("lifecycle")
        if state not in states:
            # Spec 18.1's five states are closed. An out-of-vocabulary
            # declared value is a registry-conformance problem for the
            # owning lane, not a reason for this comparator to invent a
            # sixth state - see the STOP note on L3-P0-CMP10.
            continue
        compared += 1
        observed = _observe(actual, product_yaml, product_name)

        for check in table["checks"]:
            want = check["expected_by_state"][state]
            got = observed[check["reads"]]
            if got == want:
                continue

            if check["safe"]:
                repair = _propose_repair(check["id"], product_name, want)
                findings.append(
                    Finding(
                        id=f"cmp_10_lifecycle:{product_name}:{check['id']}",
                        comparator="cmp_10_lifecycle",
                        scope=product_name,
                        drift_class=DriftClass.AMBER,
                        level=Level.AUTO_REPAIR,
                        evidence=(
                            f"{product_name} lifecycle={state!r} check={check['id']!r} "
                            f"expected={want!r} observed={got!r} "
                            f"repair_class=lifecycle_configuration_sync "
                            f"proposed_repair={repair!r}"
                        ),
                        first_seen=first_seen,
                    )
                )
            else:
                findings.append(
                    Finding(
                        id=f"cmp_10_lifecycle:{product_name}:{check['id']}",
                        comparator="cmp_10_lifecycle",
                        scope=product_name,
                        drift_class=DriftClass.AMBER,
                        level=Level.WARN,
                        evidence=(
                            f"{product_name} lifecycle={state!r} check={check['id']!r} "
                            f"expected={want!r} observed={got!r} - alert only, not on "
                            "the spec 53.2 Level-3 list"
                        ),
                        first_seen=first_seen,
                    )
                )

    return findings, compared
