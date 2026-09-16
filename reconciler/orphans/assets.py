"""L3-P2-03: orphan detectors 6-10 (assets and customer commitments).

Spec §12.2 rows 6-10; §49.1 ("Asset owners participate in orphan
detection"); §21.1.

Rule, exactly: an asset row (`certificate`, `domain`, `vendor`,
`operational`) with an empty `owner`, or an owner who is
`departed`/`revoked`, is an orphan of the matching type. A `commitments`
entry with an empty `owner` (or a departed/revoked one) is type 10.

`compared` = number of asset rows plus number of commitment rows across
every product (spec §12.2 acceptance: every asset-bearing and
commitment-bearing row examined).
"""

from __future__ import annotations

from reconciler.orphans import OrphanContext, OrphanFinding, slot_orphaned
from reconciler.orphans.types import BY_INDEX

# Asset `kind` -> the orphan type it maps to (spec §12.2 rows 6-9).
_ASSET_KIND_INDEX: dict[str, int] = {
    "certificate": 6,
    "domain": 7,
    "vendor": 8,
    "operational": 9,
}

_COMMITMENT_INDEX = 10


def _finding(index: int, subject: str, value: object) -> OrphanFinding:
    t = BY_INDEX[index]
    held = "empty" if value in (None, "") else str(value)
    return OrphanFinding(
        index=index,
        name=t.name,
        orphan_severity=t.orphan_severity,
        subject=subject,
        detail=f"{subject}: {t.name} (owner: {held})",
    )


def detect(ctx: OrphanContext, *, prospective_login: str | None = None) -> tuple[list[OrphanFinding], int]:
    findings: list[OrphanFinding] = []
    compared = 0

    for asset in ctx.assets:
        kind = asset.get("kind")
        index = _ASSET_KIND_INDEX.get(kind)
        if index is None:
            # Not one of the four asset orphan types this detector
            # covers - never silently counted as "compared" either.
            continue
        compared += 1
        owner = asset.get("owner", "")
        if slot_orphaned(ctx, owner, prospective_login=prospective_login):
            findings.append(_finding(index, asset.get("id", "<unknown asset>"), owner))

    for product_name in sorted(ctx.products):
        for commitment in ctx.products[product_name].get("commitments", []) or []:
            compared += 1
            owner = commitment.get("owner", "")
            if slot_orphaned(ctx, owner, prospective_login=prospective_login):
                findings.append(_finding(_COMMITMENT_INDEX, commitment.get("id", "<unknown commitment>"), owner))

    return findings, compared
