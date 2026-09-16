"""L3-P2-02: orphan detectors 1-5 (ownership slots and shared services).

Spec §12.2 rows 1-5; §52.2 SIG-05; §101 invariant 7.

Rule, exactly: a slot is orphaned when it is empty **or** held by a
person whose `availability` is `departed` or whose `access_status` is
`revoked`. `availability: departing` is **not** yet an orphan here -
that is prospective mode's trigger (L3-P2-05), never a current-mode
condition; `is_inactive_login()` in `reconciler.orphans` already
encodes that distinction, and this module never re-derives it.

`compared` = number of products plus number of shared services (spec
§12.2 acceptance: every ownership-bearing surface examined, not every
slot on it).
"""

from __future__ import annotations

from reconciler.orphans import OrphanContext, OrphanFinding, slot_orphaned
from reconciler.orphans.types import BY_INDEX

# Types 1-4 are per-product assignment-registry slots; type 3 (Backup
# Owner) is High, not Blocking, but is examined by this same detector -
# §12.2 groups it with the other product-ownership rows under
# `ownership`, distinct from its severity.
_PRODUCT_SLOT_FIELDS: dict[int, str] = {
    1: "primary_owner",
    2: "cross_reviewer",
    3: "backup_owner",
    4: "incident_responder_primary",
}


def _finding(index: int, subject: str, value: object) -> OrphanFinding:
    t = BY_INDEX[index]
    held = "empty" if value in (None, "") else str(value)
    return OrphanFinding(
        index=index,
        name=t.name,
        orphan_severity=t.orphan_severity,
        subject=subject,
        detail=f"{subject}: {t.name} (holder: {held})",
    )


def detect(ctx: OrphanContext, *, prospective_login: str | None = None) -> tuple[list[OrphanFinding], int]:
    findings: list[OrphanFinding] = []

    for product_name in sorted(ctx.products):
        assignments = ctx.products[product_name].get("assignments", {}) or {}
        for index, field in _PRODUCT_SLOT_FIELDS.items():
            value = assignments.get(field, "")
            if slot_orphaned(ctx, value, prospective_login=prospective_login):
                findings.append(_finding(index, product_name, value))

    for service in ctx.shared_services:
        name = service.get("name", "<unnamed shared service>")
        owner = service.get("owner", "")
        if slot_orphaned(ctx, owner, prospective_login=prospective_login):
            findings.append(_finding(5, name, owner))

    compared = len(ctx.products) + len(ctx.shared_services)
    return findings, compared
