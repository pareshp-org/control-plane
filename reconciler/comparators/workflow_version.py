"""L3-P1-07: workflow template version vs actual workflow file (spec 53.1 row 6).

Every workflow file on a repository is expected to reference the
product's declared `workflow_tag`. A mismatch is Amber - §53.1 row 6:
"Alert; flag `platform_compatibility` as drifted" - and the finding's
evidence carries the literal token `platform_compatibility=drifted` so
downstream tooling can grep for it without parsing prose.
"""

from __future__ import annotations

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator


@comparator("workflow_version", fail_class=DriftClass.AMBER)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    first_seen = f"{as_of.isoformat()}T00:00:00Z"

    for product_name, product_yaml in declared.products.items():
        declared_tag = product_yaml.get("workflow_tag")
        for filename, info in actual.workflow_files(product_name).items():
            uses_tag = info.get("uses_tag")
            if uses_tag != declared_tag:
                findings.append(
                    Finding(
                        id=f"workflow_version:{product_name}:{filename}",
                        comparator="workflow_version",
                        scope=f"{product_name}/{filename}",
                        drift_class=DriftClass.AMBER,
                        level=Level.WARN,
                        evidence=(
                            f"{product_name}/{filename} uses_tag={uses_tag!r} declared "
                            f"workflow_tag={declared_tag!r} platform_compatibility=drifted"
                        ),
                        first_seen=first_seen,
                    )
                )

    return findings, len(declared.products)
