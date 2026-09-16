"""L3-P1-10: platform.yaml workflow tag to resolved SHA (spec 53.1 row 13).

Every declared workflow tag in platform.yaml must resolve, on the
actual side, to the SHA platform.yaml declares. Any difference is
Blocking with no Amber gradation - §53.1 row 13: "Blocking on any
change - a moved tag reaches every consumer with no reviewable diff."
"""

from __future__ import annotations

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator


@comparator("workflow_tag_sha", fail_class=DriftClass.BLOCKING)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    first_seen = f"{as_of.isoformat()}T00:00:00Z"
    tags = declared.platform.get("workflow_tags") or []

    for entry in tags:
        tag = entry.get("tag")
        declared_sha = entry.get("sha")
        actual_sha = actual.resolve_tag(tag)
        if actual_sha != declared_sha:
            findings.append(
                Finding(
                    id=f"workflow_tag_sha:{tag}",
                    comparator="workflow_tag_sha",
                    scope=tag,
                    drift_class=DriftClass.BLOCKING,
                    level=Level.BLOCK,
                    evidence=(
                        f"{tag} declared sha={declared_sha!r} but resolves to "
                        f"{actual_sha!r} - a moved tag with no reviewable diff"
                    ),
                    first_seen=first_seen,
                )
            )

    return findings, len(tags)
