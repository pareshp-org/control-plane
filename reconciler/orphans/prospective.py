"""L3-P2-05: prospective orphan mode on `availability: departing`.

Spec §12.2 ("Orphan detection runs immediately when `availability`
becomes `departing`, in prospective mode against the declared
`end_date`: it emits the transfer worklist"); AT-017.

Rule, exactly: for each person whose `availability` is `departing`,
re-run every detector with that person treated as inactive **as of
their `end_date`**, and emit the resulting findings as a transfer
worklist, each carrying `prospective=True` and `orphans_on=<end_date>`.

A finding is only part of the worklist when treating the departing
person as inactive is *what causes it* - a slot already orphaned today
for an unrelated reason is not this module's finding to report a
second time (it belongs to the current-mode run that already reported
it). This is computed by diffing each group's "person forced inactive"
run against the same group's current-mode run and keeping only the
`(index, subject)` pairs that are new.

Prospective findings never enter drift-budget counts and never block
(L3-P2-05's own STOP rule: blocking on a future state would freeze the
estate for every notice period) - `reconciler.cli`'s `orphans
--prospective` always exits 0, regardless of severity.

`compared` = number of people rows examined.
"""

from __future__ import annotations

from dataclasses import replace

from reconciler.orphans import OrphanContext, OrphanFinding, run_group
from reconciler.orphans.types import GROUPS


def _findings_by_key(ctx: OrphanContext, *, prospective_login: str | None) -> dict[tuple[int, str], OrphanFinding]:
    keyed: dict[tuple[int, str], OrphanFinding] = {}
    for group in GROUPS:
        findings, _ = run_group(group, ctx, prospective_login=prospective_login)
        for finding in findings:
            keyed[(finding.index, finding.subject)] = finding
    return keyed


def detect(ctx: OrphanContext) -> tuple[list[OrphanFinding], int]:
    baseline = _findings_by_key(ctx, prospective_login=None)

    worklist: list[OrphanFinding] = []
    seen: set[tuple[int, str]] = set()

    departing = [p for p in ctx.people if p.get("availability") == "departing"]
    for person in departing:
        login = person.get("github_login")
        end_date = person.get("end_date")
        projected = _findings_by_key(ctx, prospective_login=login)
        for key, finding in projected.items():
            if key in baseline or key in seen:
                continue  # already orphaned today, or already added for another departing person
            seen.add(key)
            worklist.append(replace(finding, prospective=True, orphans_on=end_date))

    return worklist, len(ctx.people)
