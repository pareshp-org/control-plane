"""L3-P3-01: drift-class configuration loader from `os-health.yaml`
(spec 53.4: "Class assignment lives in configuration and is
reviewable; it is not decided ad hoc during an incident."; spec 52.2;
spec 53.6: "Class definitions and tolerances are themselves
calibration-reviewed.")

`os-health.yaml` lives under `registries/**` and is owned by Lane 1.
This module reads it and writes to nothing - not to `os-health.yaml`,
not to `registries/**`, not to any path outside this lane's three
owned roots (`reconciler/**`, `tools/provision/**`, `validators/drift/**`,
per PARTITION.md). If a field this loader needs is absent from the
file, the fix is a Contract Change Request to Lane 1, never a local
edit to their registry.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from reconciler.model import DriftClass, Finding, Level, security_floor

# The code's own default drift class per comparator id - used only
# where os-health.yaml's `drift_classes:` map declares no override for
# that id (spec 53.4). A comparator with no entry here and no
# configured override defaults to Green, the scale's own
# least-urgent, "recorded only" class.
DEFAULT_CLASSES: dict[str, DriftClass] = {
    "org_membership": DriftClass.AMBER,
    "team_membership": DriftClass.BLOCKING,
    "capability_authority": DriftClass.AMBER,
    "codeowners": DriftClass.AMBER,
    "branch_protection": DriftClass.RED,
    "workflow_version": DriftClass.AMBER,
    "environments": DriftClass.RED,
    "expiry": DriftClass.BLOCKING,
    "workflow_tag_sha": DriftClass.BLOCKING,
    "renovate_bypass": DriftClass.BLOCKING,
    "machine_authorship": DriftClass.BLOCKING,
    "infra_attestation": DriftClass.BLOCKING,
    "write_freshness": DriftClass.AMBER,
    "restore_tested": DriftClass.BLOCKING,
    "checkrun_identity": DriftClass.BLOCKING,
    "display_name": DriftClass.GREEN,
}

# Comparators covering security controls or production-environment
# drift (spec 53.4: "Security drift and production environment drift
# are never classified below Red, regardless of apparent impact.").
# No configuration, in os-health.yaml or anywhere else, can move these
# below Red - security_floor() enforces that mechanically, last, after
# both the configured override and the code default have been resolved.
SECURITY_OR_PROD_ENV_COMPARATORS = frozenset(
    {
        "branch_protection",
        "environments",
        "renovate_bypass",
        "machine_authorship",
        "infra_attestation",
        "workflow_tag_sha",
        "checkrun_identity",
    }
)

_ORDER: dict[DriftClass, int] = {
    DriftClass.GREEN: 0,
    DriftClass.AMBER: 1,
    DriftClass.RED: 2,
    DriftClass.BLOCKING: 3,
}


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_classes(
    os_health_path: str | Path,
    *,
    findings: list[Finding] | None = None,
    first_seen: str = "",
) -> dict[str, DriftClass]:
    """Read-only: never writes to `os_health_path` or anywhere else.

    Returns comparator id -> its effective DriftClass: the configured
    override from `drift_classes:` in the file at `os_health_path`
    where one is declared, else this module's own DEFAULT_CLASSES
    entry (or Green, absent both), with security_floor() applied last
    so a security/production-environment comparator can never be
    configured below Red (spec 53.4).

    When a configured override for a security/production-environment
    comparator is refused by that floor, and `findings` is given, the
    refusal is itself appended to `findings` as a Blocking Finding -
    the floor overriding a configured value is a fact this instrument
    must surface, not a value silently substituted (spec 53.4's own
    framing: tolerances are calibration-reviewed, not overridden ad
    hoc during an incident).
    """
    doc = _load_yaml(Path(os_health_path))
    configured_raw = doc.get("drift_classes") or {}

    configured: dict[str, DriftClass] = {}
    for comparator_id, raw_value in configured_raw.items():
        try:
            configured[comparator_id] = DriftClass(raw_value)
        except ValueError as exc:
            raise ValueError(
                f"os-health.yaml drift_classes.{comparator_id!r} names unknown "
                f"drift class {raw_value!r}"
            ) from exc

    classes: dict[str, DriftClass] = {}
    for comparator_id in sorted(set(DEFAULT_CLASSES) | set(configured)):
        requested = configured.get(
            comparator_id, DEFAULT_CLASSES.get(comparator_id, DriftClass.GREEN)
        )
        is_floored = comparator_id in SECURITY_OR_PROD_ENV_COMPARATORS
        effective = security_floor(requested, is_floored)

        if is_floored and effective != requested and findings is not None:
            findings.append(
                Finding(
                    id=f"driftclass:refused:{comparator_id}",
                    comparator="driftclass",
                    scope=comparator_id,
                    drift_class=DriftClass.BLOCKING,
                    level=Level.BLOCK,
                    evidence=(
                        f"os-health.yaml configured {comparator_id!r} at "
                        f"{requested.value}, below the Red floor spec 53.4 sets for "
                        "security/production-environment comparators; refused, "
                        f"held at {effective.value}"
                    ),
                    first_seen=first_seen,
                )
            )

        classes[comparator_id] = effective

    return classes
