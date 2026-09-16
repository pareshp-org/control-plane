"""R-PPL-05, R-PPL-09, R-PPL-10, R-PPL-11, R-PPL-12 -- ``work_arrangement``
shape rules that Section 7.3's JSON Schema (L1-104) cannot express on its
own (task L1-207, SPEC Section 7.3 / D111).

Standalone, directly-tested rule functions -- see the module docstring of
``r_svc_01.py`` for why these are not wired into the frozen Option B
(FD-094) ``R01``..``R18`` dispatch table in
``validators/registry/rules/registry.py``. The CLI grammar and per-fixture
``echo "EXIT=$?"`` acceptance commands written into ``lanes/L1-05-tasks.md``
predate FD-094 and are superseded by it, exactly as
``validators/registry/tests/test_service_schema.py`` documents for
R-SVC-01..03 and ``r_prd_11.py`` documents for R-PRD-11/27/28: fixtures
still live where the task says
(``validators/registry/fixtures/ppl05/<case>/people.yaml``), but they are
exercised by calling ``check()`` directly against a parsed ``people.yaml``
document, not through ``validators/registry/cli.py``.

Rules covered (people-level, per person):

* R-PPL-05 -- ``timezone`` is a UTC/GMT offset, or has no ``/`` at all
  (Section 7.3 requires a real IANA identifier, not an offset).
* R-PPL-09 -- a ``schedule`` weekday whose ``end`` is not strictly after
  its ``start``.
* R-PPL-10 -- ``schedule`` is present but an empty mapping (declares no
  working days at all).
* R-PPL-11 -- ``accepted_coverage_window`` is non-null while ``schedule``
  is empty -- there is no working calendar for the window to resolve
  against. This is the more specific problem when a coverage window *is*
  declared, so it is reported instead of R-PPL-10 for that case (the same
  choice ``r_prd_11.check_r_prd_11`` makes in favour of R-PRD-28 for the
  24x7-empty-rota overlap) -- never both, for one person's one empty
  schedule.
* R-PPL-12 -- an **active** person with no ``work_arrangement`` at all
  (Section 47.9 fails closed without it). Non-active people (e.g. a
  ``departed`` record retained under Section 7.1) never fire this, or
  any of the other four rules here, since ``work_arrangement`` being
  absent is exactly their intended, retained shape.

None of these read ``fte`` or ``arrangement`` as anything but a capacity
input / scheduling context (Section 7.3) -- neither field is inspected by
any check below, by design, per this task's own STOP condition.
"""
from __future__ import annotations

import re

RULE_ID_TIMEZONE = "R-PPL-05"
RULE_ID_SCHEDULE_ORDER = "R-PPL-09"
RULE_ID_EMPTY_SCHEDULE = "R-PPL-10"
RULE_ID_COVERAGE_WITHOUT_SCHEDULE = "R-PPL-11"
RULE_ID_ACTIVE_NO_ARRANGEMENT = "R-PPL-12"
SPEC = "Section 7.3 (D111); Section 47.9"
APPLIES_TO = ["people"]

_WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
_UTC_OFFSET_RE = re.compile(r"^(UTC|GMT)?[+-]\d")


def _person_id(person: dict) -> str:
    return person.get("id", "<unknown-person>")


def _is_utc_offset_or_slashless(timezone: str) -> bool:
    """True when ``timezone`` is a UTC/GMT-style offset, or contains no
    ``/`` at all -- the two shapes Section 7.3 forbids in place of a real
    IANA identifier."""
    if not isinstance(timezone, str):
        return True
    return bool(_UTC_OFFSET_RE.match(timezone)) or "/" not in timezone


def check_r_ppl_05(people_doc: dict) -> list[str]:
    """R-PPL-05 -- ``timezone`` is not an IANA identifier."""
    findings = []
    for person in (people_doc or {}).get("people") or []:
        work_arrangement = person.get("work_arrangement")
        if not work_arrangement:
            continue
        timezone = work_arrangement.get("timezone")
        if _is_utc_offset_or_slashless(timezone):
            findings.append(
                f"R-PPL-05 person '{_person_id(person)}': timezone '{timezone}' is not "
                f"an IANA identifier; Section 7.3 forbids UTC offsets"
            )
    return findings


def check_r_ppl_09(people_doc: dict) -> list[str]:
    """R-PPL-09 -- a schedule weekday whose ``end`` is not strictly after
    its ``start``. Every bad day is reported, not just the first."""
    findings = []
    for person in (people_doc or {}).get("people") or []:
        work_arrangement = person.get("work_arrangement")
        if not work_arrangement:
            continue
        schedule = work_arrangement.get("schedule") or {}
        for day in _WEEKDAYS:
            span = schedule.get(day)
            if not span:
                continue
            start, end = span.get("start"), span.get("end")
            if end is not None and start is not None and end <= start:
                findings.append(
                    f"R-PPL-09 person '{_person_id(person)}': schedule '{day}' ends at "
                    f"or before it starts; Section 7.3"
                )
    return findings


def check_r_ppl_10_and_11(people_doc: dict) -> list[str]:
    """R-PPL-10 -- ``schedule`` is an empty mapping.
    R-PPL-11 -- ``accepted_coverage_window`` is non-null while ``schedule``
    is empty.

    These share one condition (an empty ``schedule``) and are mutually
    exclusive per person: when a coverage window is also declared with
    nothing to resolve it against, R-PPL-11 reports that more specific
    problem instead of the generic "no working days" R-PPL-10 finding.
    """
    findings = []
    for person in (people_doc or {}).get("people") or []:
        work_arrangement = person.get("work_arrangement")
        if not work_arrangement:
            continue
        schedule = work_arrangement.get("schedule")
        if schedule != {}:
            continue
        coverage_window = work_arrangement.get("accepted_coverage_window")
        if coverage_window is not None:
            findings.append(
                f"R-PPL-11 person '{_person_id(person)}': accepted_coverage_window "
                f"declared with no working calendar to resolve it against; Section 7.3"
            )
        else:
            findings.append(
                f"R-PPL-10 person '{_person_id(person)}' declares no working days; "
                f"Section 7.3 requires a working calendar"
            )
    return findings


def check_r_ppl_12(people_doc: dict) -> list[str]:
    """R-PPL-12 -- an active person with no ``work_arrangement`` at all.
    Applies to active people only; a departed record retained under
    Section 7.1 never fires this."""
    findings = []
    for person in (people_doc or {}).get("people") or []:
        if person.get("availability") != "active":
            continue
        if person.get("work_arrangement") is None:
            findings.append(
                f"R-PPL-12 active person '{_person_id(person)}' has no work_arrangement; "
                f"Section 47.9 fails closed without it"
            )
    return findings


def check(people_doc: dict) -> list[str]:
    """Run all five rules and return the combined findings, in the order
    the task's own table names them: R-PPL-05, R-PPL-09, R-PPL-10/11,
    R-PPL-12."""
    findings = []
    findings.extend(check_r_ppl_05(people_doc))
    findings.extend(check_r_ppl_09(people_doc))
    findings.extend(check_r_ppl_10_and_11(people_doc))
    findings.extend(check_r_ppl_12(people_doc))
    return findings
