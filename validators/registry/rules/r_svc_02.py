"""R-SVC-02 -- a shared service with no active primary_owner or no active
cross_reviewer assignment.

Section 20.1, invariant 63: "A shared service has the same four ownership
relationships as a product. It is not ownerless infrastructure."

Standalone, directly-tested rule function -- see the module docstring of
r_svc_01.py for why this is not wired into the frozen Option B (FD-094)
dispatch engine.
"""
from __future__ import annotations

import datetime

RULE_ID = "R-SVC-02"
SPEC = "Section 20.1, invariant 63"
APPLIES_TO = ["service"]

_REQUIRED_ACTIVE_ROLES = (
    ("primary_owner", "active primary_owner"),
    ("cross_reviewer", "active cross_reviewer"),
)


def _as_date(value) -> datetime.date:
    if isinstance(value, datetime.date):
        return value
    return datetime.date.fromisoformat(str(value))


def _is_active(assignment: dict, today: datetime.date) -> bool:
    end = assignment.get("end_date")
    if end is None:
        return True
    return _as_date(end) >= today


def check(service_doc: dict, today: datetime.date) -> list[str]:
    """Return one finding per role in ``_REQUIRED_ACTIVE_ROLES`` for which
    no assignment of that ``type`` has ``end_date`` null or ``>= today``.
    """
    assignments = service_doc.get("assignments") or []
    service_id = (service_doc.get("identity") or {}).get("id", "<unknown>")
    findings = []
    for role_type, label in _REQUIRED_ACTIVE_ROLES:
        has_active = any(
            a.get("type") == role_type and _is_active(a, today) for a in assignments
        )
        if not has_active:
            findings.append(
                f"shared service '{service_id}' has no {label}; Section 20.1, invariant 63"
            )
    return findings
