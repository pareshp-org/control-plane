"""L3-P1-13: declared infrastructure boundary vs attestation window (spec 53.1 row 9; §40.2).

For each product declaring an `infrastructure:` block, staleness of its
`attestation_date` past `platform.yaml.attestation_window_days` is
Blocking - §53.1 row 9: "Blocking past its attestation window." §40.2:
the provider side is verified "by attestation rather than
reconciliation" - this comparator checks only the attestation's
freshness and issues no provider-side call of any kind.
"""

from __future__ import annotations

from datetime import date

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator


@comparator("infra_attestation", fail_class=DriftClass.BLOCKING)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    first_seen = f"{as_of.isoformat()}T00:00:00Z"
    window_days = declared.platform.get("attestation_window_days")
    compared = 0

    for product_name, product_yaml in declared.products.items():
        infra = product_yaml.get("infrastructure")
        if not infra:
            continue
        compared += 1
        attestation_date = infra.get("attestation_date")
        if attestation_date is None:
            continue
        age_days = (as_of - date.fromisoformat(attestation_date)).days
        if window_days is not None and age_days > window_days:
            findings.append(
                Finding(
                    id=f"infra_attestation:{product_name}",
                    comparator="infra_attestation",
                    scope=product_name,
                    drift_class=DriftClass.BLOCKING,
                    level=Level.BLOCK,
                    evidence=(
                        f"{product_name} attested {attestation_date} is {age_days} days "
                        f"old, past the {window_days}-day attestation window"
                    ),
                    first_seen=first_seen,
                )
            )

    return findings, compared
