"""R-PRD-11, R-PRD-27, R-PRD-28 -- the coverage-window rota union rule.

Section 47.9, AT-047, invariant 31 (task L1-311; unblocked by L1-D03 /
REG-042 -- see ``lanes/L0-04-decisions-register.md``).

Standalone, directly-tested rule functions -- see the module docstring of
``r_svc_01.py`` for why these are not wired into the frozen Option B
(FD-094) ``R01``..``R18`` dispatch table in
``validators/registry/rules/registry.py``. The CLI grammar and per-fixture
``echo "AT047_EXIT=$?"`` acceptance command written into
``lanes/L1-05-tasks.md`` predate FD-094 and are superseded by it, exactly
as ``validators/registry/tests/test_service_schema.py`` documents for
R-SVC-01..03: fixtures still live where the task says
(``validators/registry/fixtures/product/rota/<case>/``), but they are
exercised by calling these functions directly against parsed
``product.yaml`` / ``people.yaml`` documents, not through
``validators/registry/cli.py``.

L1-D03 (REG-042) closed on Option B of the three choices it posed: a
per-product rota block that is its *own* source of truth, named
``rotas[]`` in ``people.yaml``, with ``work_arrangement.
accepted_coverage_window`` left as the unrelated person-wide default
(Section 7.3) that this rule never reads. The field names below --
``product``, ``members[].person``, ``members[].accepted_window``,
``members[].paging_path``, ``members[].funding_decision_record`` -- are
the ones ``lanes/L1-02-schemas.md`` §"rotas[] (Section 47.9)" transcribes
for that shape; ``schemas/registry/people.registry.v1.schema.json`` does
not yet declare a ``rotas`` property (checked directly -- L1-02's own
schema-authoring task has not landed it), so this rule reads ``rotas``
from the parsed YAML directly, the same way ``r_svc_01.check`` reads a
service's ``consumers[]`` against a raw ``product.yaml`` sibling rather
than requiring it to validate against a shared schema first.

Window arithmetic (§7.3: "against the *product*'s declared window") is
resolved by converting every window -- the product's ``coverage_window``
and each active member's ``accepted_window`` -- into hour-of-week buckets
in UTC, using a fixed, DST-free reference week (2026-01-05, a Monday).
Only whole-hour ``HH:00`` boundaries are supported; every fixture here
uses timezones with a whole-hour UTC offset that does not shift across
that reference week, so the bucket comparison is exact.
"""
from __future__ import annotations

import datetime
from zoneinfo import ZoneInfo

RULE_ID_COVERAGE = "R-PRD-11"
RULE_ID_MEMBER = "R-PRD-27"
RULE_ID_ONBOARDING = "R-PRD-28"
SPEC = "Section 47.9; Section 15.5; Section 15.6; Section 7.3; AT-047; invariant 31"
APPLIES_TO = ["product", "people"]

_WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
_REF_MONDAY = datetime.date(2026, 1, 5)
_EXTENDED_SUPPORT_MODELS = ("extended", "24x7")


def _product_id(product_doc: dict) -> str:
    return (product_doc.get("identity") or {}).get("id", "<unknown-product>")


def _parse_hour(value: str) -> int:
    hh, mm = str(value).split(":")
    if mm != "00":
        raise ValueError(f"window arithmetic here only supports HH:00 boundaries, got {value!r}")
    return int(hh)


def _window_utc_hours(window: dict) -> set:
    """Convert a ``{days, start, end, timezone}`` window into the set of
    ``(utc_weekday, utc_hour)`` buckets it covers, resolved against the
    fixed reference week.

    ``end <= start`` is an overnight span that wraps past midnight
    (e.g. ``22:00``..``06:00``); ``end == "24:00"`` is the literal end of
    the day.
    """
    tz = ZoneInfo(window["timezone"])
    start_hour = _parse_hour(window["start"])
    end_hour = _parse_hour(window["end"])
    span = end_hour - start_hour
    if span <= 0:
        span += 24
    buckets = set()
    for day in window.get("days") or []:
        day_idx = _WEEKDAYS.index(day)
        base_date = _REF_MONDAY + datetime.timedelta(days=day_idx)
        for offset in range(span):
            total_hour = start_hour + offset
            extra_days, hour_in_day = divmod(total_hour, 24)
            local_dt = datetime.datetime(
                base_date.year, base_date.month, base_date.day, hour_in_day, tzinfo=tz
            ) + datetime.timedelta(days=extra_days)
            utc_dt = local_dt.astimezone(datetime.timezone.utc)
            buckets.add((utc_dt.weekday(), utc_dt.hour))
    return buckets


def _find_rota(product_doc: dict, people_doc: dict) -> dict | None:
    pid = _product_id(product_doc)
    for rota in (people_doc or {}).get("rotas") or []:
        if rota.get("product") == pid:
            return rota
    return None


def _people_by_id(people_doc: dict) -> dict:
    return {p.get("id"): p for p in (people_doc or {}).get("people") or []}


def _is_active_member(member: dict, people_index: dict) -> bool:
    person = people_index.get(member.get("person"))
    return person is not None and person.get("availability") == "active"


def check_r_prd_28(product_doc: dict, people_doc: dict) -> list[str]:
    """R-PRD-28 -- 24x7 support cannot be onboarded without a funded rota."""
    support_model = (product_doc.get("operations") or {}).get("support_model")
    if support_model != "24x7":
        return []
    rota = _find_rota(product_doc, people_doc)
    members = (rota or {}).get("members") or []
    if members:
        return []
    pid = _product_id(product_doc)
    return [
        f"R-PRD-28 {pid}: 24x7 support cannot be onboarded without a funded rota; "
        f"Section 15.6 onboarding blocker, invariant 31"
    ]


def check_r_prd_27(product_doc: dict, people_doc: dict) -> list[str]:
    """R-PRD-27 -- a rota member with no work_arrangement, no accepted
    window, or an accepted window not covering the segment assigned to
    them (Section 7.3: "fails closed where a member has no work
    arrangement")."""
    rota = _find_rota(product_doc, people_doc)
    members = (rota or {}).get("members") or []
    people_index = _people_by_id(people_doc)
    pid = _product_id(product_doc)
    findings = []
    for member in members:
        person_id = member.get("person", "<unknown-person>")
        person = people_index.get(person_id)
        work_arrangement = (person or {}).get("work_arrangement")
        accepted_window = member.get("accepted_window")
        if work_arrangement is None:
            findings.append(
                f"R-PRD-27 {pid}: rota member '{person_id}' has no work_arrangement; "
                f"Section 7.3 fails closed where a member has no work arrangement"
            )
            continue
        if accepted_window is None:
            findings.append(
                f"R-PRD-27 {pid}: rota member '{person_id}' has no accepted_window; "
                f"Section 47.9 fails closed where a member has no accepted window"
            )
            continue
        try:
            covers_own_segment = len(_window_utc_hours(accepted_window)) > 0
        except (KeyError, ValueError):
            covers_own_segment = False
        if not covers_own_segment:
            findings.append(
                f"R-PRD-27 {pid}: rota member '{person_id}' has an accepted_window that "
                f"does not cover the segment assigned to them; Section 7.3 fails closed"
            )
    return findings


def check_r_prd_11(product_doc: dict, people_doc: dict) -> list[str]:
    """R-PRD-11 -- an extended/24x7 support model whose declared
    coverage_window is not fully covered by the union of accepted windows
    of active rota members."""
    support_model = (product_doc.get("operations") or {}).get("support_model")
    if support_model not in _EXTENDED_SUPPORT_MODELS:
        return []
    coverage_window = (product_doc.get("operations") or {}).get("coverage_window")
    if coverage_window is None:
        return []
    rota = _find_rota(product_doc, people_doc)
    members = (rota or {}).get("members") or []
    if support_model == "24x7" and not members:
        # R-PRD-28 already reports the funded-rota onboarding blocker for
        # this exact combination; do not double-report it here.
        return []

    people_index = _people_by_id(people_doc)
    covered = set()
    for member in members:
        if not _is_active_member(member, people_index):
            continue
        window = member.get("accepted_window")
        if window is None:
            continue
        covered |= _window_utc_hours(window)

    required = _window_utc_hours(coverage_window)
    if required.issubset(covered):
        return []

    pid = _product_id(product_doc)
    days = ",".join(coverage_window.get("days") or [])
    hours = f"{coverage_window.get('start')}-{coverage_window.get('end')}"
    tz = coverage_window.get("timezone")
    return [
        f"R-PRD-11 {pid}: coverage_window {days} {hours} {tz} is not fully covered "
        f"by active rota members; Section 47.9 fails closed"
    ]


def check(product_doc: dict, people_doc: dict) -> list[str]:
    """Run all three rules and return the combined findings, R-PRD-11
    first, matching the order the task names them in."""
    findings = []
    findings.extend(check_r_prd_11(product_doc, people_doc))
    findings.extend(check_r_prd_27(product_doc, people_doc))
    findings.extend(check_r_prd_28(product_doc, people_doc))
    return findings
