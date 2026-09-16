"""R-SVC-03 -- a service's escalation naming a person instead of a role.

Section 10.2: escalation is declared as a role, never a person.

Standalone, directly-tested rule function -- see the module docstring of
r_svc_01.py for why this is not wired into the frozen Option B (FD-094)
dispatch engine.
"""
from __future__ import annotations

RULE_ID = "R-SVC-03"
SPEC = "Section 10.2"
APPLIES_TO = ["service", "people"]


def check(service_doc: dict, known_person_ids) -> list[str]:
    """Return a finding when ``escalation`` names a known person id.

    ``known_person_ids`` is the set of person ids loaded from people.yaml
    in context, or ``None`` when no people document is present at all --
    in which case this rule is silent, exactly as R-PPL-04 is silent when
    its counterpart document is absent from ctx.docs.
    """
    if known_person_ids is None:
        return []
    escalation = service_doc.get("escalation")
    if escalation in set(known_person_ids):
        return [
            f"escalation '{escalation}' names a person; Section 10.2 declares "
            f"escalation as a role, never a person"
        ]
    return []
