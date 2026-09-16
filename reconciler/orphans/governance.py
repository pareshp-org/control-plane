"""L3-P2-04: orphan detectors 11-16 (migration, verification, H1, temporary
expiry, policy, exception).

Spec §12.2 rows 11-16; §12.2 ("Temporary-person expiry is an exit");
§54; §55.

Rule, exactly, one detector per type:

* 11 - migration with empty `owner`.
* 12 - product with empty `verification_responsibility`.
* 13 - board item at `horizon: H1` with empty `assignee`.
* 14 - an expired temporary assignment whose holder still appears in
  `open_gate_items` ("the fourteenth orphan type"). Expiry is by
  `end_date < ctx.as_of` - strictly in the past, not on the boundary
  day itself, which is still covered.
* 15 - policy with empty `owner`.
* 16 - open exception whose `requester` or `authority` is `departed`.

`compared` = 6, one per type examined - a structural count, not a
data-driven one (spec §12.2 acceptance: every type gets a look even
when its input list is empty).
"""

from __future__ import annotations

from datetime import date

from reconciler.orphans import OrphanContext, OrphanFinding, is_inactive_login, slot_orphaned
from reconciler.orphans.types import BY_INDEX

_COMPARED = 6


def _finding(index: int, subject: str, detail_suffix: str) -> OrphanFinding:
    t = BY_INDEX[index]
    return OrphanFinding(
        index=index,
        name=t.name,
        orphan_severity=t.orphan_severity,
        subject=subject,
        detail=f"{subject}: {t.name} ({detail_suffix})",
    )


def _detect_migrations(ctx: OrphanContext, prospective_login: str | None) -> list[OrphanFinding]:
    findings = []
    for migration in ctx.migrations:
        owner = migration.get("owner", "")
        if slot_orphaned(ctx, owner, prospective_login=prospective_login):
            findings.append(_finding(11, migration.get("id", "<unknown migration>"), f"owner: {owner or 'empty'}"))
    return findings


def _detect_verification(ctx: OrphanContext, prospective_login: str | None) -> list[OrphanFinding]:
    findings = []
    for product_name in sorted(ctx.products):
        value = (ctx.products[product_name].get("assignments", {}) or {}).get("verification_responsibility", "")
        if slot_orphaned(ctx, value, prospective_login=prospective_login):
            findings.append(_finding(12, product_name, f"holder: {value or 'empty'}"))
    return findings


def _detect_h1_work(ctx: OrphanContext, prospective_login: str | None) -> list[OrphanFinding]:
    findings = []
    for item in ctx.board_items:
        if item.get("horizon") != "H1":
            continue
        value = item.get("assignee", "")
        if slot_orphaned(ctx, value, prospective_login=prospective_login):
            findings.append(_finding(13, item.get("id", "<unknown board item>"), f"assignee: {value or 'empty'}"))
    return findings


def _detect_temp_expiry(ctx: OrphanContext) -> list[OrphanFinding]:
    open_holders = {item.get("holder") for item in ctx.open_gate_items if item.get("holder")}
    findings = []
    for product_name in sorted(ctx.products):
        for assignment in ctx.products[product_name].get("temporary_assignments", []) or []:
            end_date_raw = assignment.get("end_date")
            if not end_date_raw:
                continue
            if date.fromisoformat(end_date_raw) >= ctx.as_of:
                continue  # not yet expired as of this run
            holder = assignment.get("person")
            if holder in open_holders:
                findings.append(
                    _finding(
                        14,
                        holder,
                        f"expired {assignment.get('type', 'temporary')} assignment on {product_name} "
                        f"ended {end_date_raw}, still holding open gate-relevant work",
                    )
                )
    return findings


def _detect_policies(ctx: OrphanContext, prospective_login: str | None) -> list[OrphanFinding]:
    findings = []
    for policy in ctx.policies:
        owner = policy.get("owner", "")
        if slot_orphaned(ctx, owner, prospective_login=prospective_login):
            findings.append(_finding(15, policy.get("id", "<unknown policy>"), f"owner: {owner or 'empty'}"))
    return findings


def _detect_exceptions(ctx: OrphanContext, prospective_login: str | None) -> list[OrphanFinding]:
    findings = []
    for exception in ctx.exceptions:
        requester = exception.get("requester", "")
        authority = exception.get("authority", "")
        requester_gone = bool(requester) and is_inactive_login(ctx, requester, prospective_login=prospective_login)
        authority_gone = bool(authority) and is_inactive_login(ctx, authority, prospective_login=prospective_login)
        if requester_gone or authority_gone:
            who = requester if requester_gone else authority
            findings.append(_finding(16, exception.get("id", "<unknown exception>"), f"{who} has departed"))
    return findings


def detect(ctx: OrphanContext, *, prospective_login: str | None = None) -> tuple[list[OrphanFinding], int]:
    findings: list[OrphanFinding] = []
    findings.extend(_detect_migrations(ctx, prospective_login))
    findings.extend(_detect_verification(ctx, prospective_login))
    findings.extend(_detect_h1_work(ctx, prospective_login))
    findings.extend(_detect_temp_expiry(ctx))
    findings.extend(_detect_policies(ctx, prospective_login))
    findings.extend(_detect_exceptions(ctx, prospective_login))
    return findings, _COMPARED
