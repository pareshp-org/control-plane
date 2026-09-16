"""L3-P1-12: machine workflow-file change and bypass-branch authorship (spec 53.1; §33.2; §40.3).

Two checks, one comparator:

* **A.** Any workflow file last pushed by a machine identity is
  Blocking regardless of the change's content - workflow files define
  the enforcement path itself, and no machine credential is authorised
  to alter it. Check A has no declared-vs-actual gray area (there is no
  configuration under which a machine push is acceptable), so every
  file it flags is, by definition, also every file "compared" under it
  - `compared` for this half is the count of machine-pushed files.
* **B.** For each bypass branch, any commit author other than the
  branch's declared_bypass_actor is Blocking - a bypass is a grant to
  one identity, and a branch merging under it must carry that
  identity's work only. Every bypass branch is genuinely compared under
  this half (a clean branch is still examined, just not flagged), so
  `compared` for this half is the count of bypass branches examined.

`compared` is the sum of the two.
"""

from __future__ import annotations

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator


@comparator("machine_authorship", fail_class=DriftClass.BLOCKING)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    compared = 0
    first_seen = f"{as_of.isoformat()}T00:00:00Z"

    for product_name in declared.products:
        for filename, info in actual.workflow_files(product_name).items():
            if not info.get("pusher_is_machine"):
                continue
            compared += 1
            findings.append(
                Finding(
                    id=f"machine_authorship:{product_name}:{filename}:machine_push",
                    comparator="machine_authorship",
                    scope=f"{product_name}/{filename}",
                    drift_class=DriftClass.BLOCKING,
                    level=Level.BLOCK,
                    evidence=(
                        f"{product_name}/{filename} was last pushed by "
                        f"{info.get('last_pusher')!r}, a machine identity - no machine "
                        "credential may alter a workflow file, regardless of content"
                    ),
                    first_seen=first_seen,
                )
            )

    for branch in actual.bypass_branches():
        compared += 1
        declared_actor = branch.get("declared_bypass_actor")
        offenders = [a for a in branch.get("commit_authors", []) if a != declared_actor]
        if offenders:
            findings.append(
                Finding(
                    id=f"machine_authorship:{branch.get('branch')}:bypass_authorship",
                    comparator="machine_authorship",
                    scope=branch.get("branch"),
                    drift_class=DriftClass.BLOCKING,
                    level=Level.BLOCK,
                    evidence=(
                        f"branch {branch.get('branch')!r} merged under a bypass granted to "
                        f"{declared_actor!r} but carries commits by {offenders} as well"
                    ),
                    first_seen=first_seen,
                )
            )

    return findings, compared
