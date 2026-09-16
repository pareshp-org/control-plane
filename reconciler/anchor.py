"""L3-P5-08: records-repository head SHA anchor (spec 40.1 "History is
anchored where it cannot be rewritten" (D107); spec 53.2 Level 5;
§101 invariant 47).

Once per reconciliation run, `anchor()` records the records
repository's default-branch head SHA and commit count. D107: "a head
that does not descend from the last anchored SHA is proof of
rewriting rather than evidence of it" — such a head is Blocking drift
at Level 5, not a lesser finding graded down for the possibility of an
innocent explanation; D107 rules that possibility out by definition.

Descent is checked by real ancestry, not by comparing commit counts (a
force-push replacing history with a same-length or longer chain would
pass a count-only check while still being exactly the rewrite D107
names): the caller supplies `ancestor_shas`, the full set of commit
SHAs reachable from `records_head_sha` (as a real `git rev-list
<records_head_sha>` against the records repository would produce).
The new head descends from the previous anchor when the previous
anchor's SHA is itself among that set, or when the head has simply not
moved.

The anchor value this module produces is hand-off data for the
control-plane write path (a different module's job, spec 40.1's own
demarcation) — this module performs no write of any kind, to that
store or to the drift-events store, anywhere: the reconciler credential
cannot reach either (AT-110's fifth attempt), so a write attempt here
would not even be a control-plane concern, it would be a credential
violation.
"""

from __future__ import annotations

from dataclasses import dataclass

from reconciler.model import DriftClass, Finding, Level


@dataclass(frozen=True)
class Anchor:
    """One anchored (sha, commit_count) pair — both the previous
    anchor `anchor()` is given and the new one it returns."""

    sha: str
    commit_count: int


class NonDescendantHead(RuntimeError):
    """Not raised by `anchor()` itself — `anchor()` reports a
    non-descendant head as a Finding, never a crash, so the run that
    discovers it can still complete and surface the finding (spec 53.1:
    a reconciler that cannot report drift is itself the failure).
    Defined here for callers that want to treat the condition as
    exceptional in their own control flow.
    """


def _descends(previous: Anchor, records_head_sha: str, ancestor_shas: frozenset[str]) -> bool:
    if previous.sha == records_head_sha:
        return True
    return previous.sha in ancestor_shas


def anchor(
    records_head_sha: str,
    commit_count: int,
    previous_anchor: Anchor | None,
    *,
    ancestor_shas: frozenset[str] = frozenset(),
) -> tuple[Anchor, Finding | None]:
    """Anchor `records_head_sha`/`commit_count` as this run's record.

    `previous_anchor` is `None` only for the very first anchor a
    reconciler ever records — there is nothing to check descent against
    yet, so the first call always anchors cleanly. On every later call,
    `ancestor_shas` must be the ancestry set described in this module's
    docstring; a `previous_anchor.sha` absent from it (and different
    from `records_head_sha` itself) is Blocking drift at Level 5.

    Returns `(new_anchor, finding)` — `finding` is `None` on a clean
    anchor, or a Blocking/ESCALATE `Finding` naming the non-descendant
    head. The new anchor is returned either way: a broken chain is
    itself worth anchoring, so the next run has something to compare
    against rather than silently repeating the same first-detection
    forever.
    """
    new_anchor = Anchor(sha=records_head_sha, commit_count=commit_count)

    if previous_anchor is None:
        return new_anchor, None

    if _descends(previous_anchor, records_head_sha, ancestor_shas):
        return new_anchor, None

    finding = Finding(
        id=f"records_anchor:non_descendant:{records_head_sha}",
        comparator="records_anchor",
        scope="records_repository",
        drift_class=DriftClass.BLOCKING,
        level=Level.ESCALATE,
        evidence=(
            f"the records repository's head moved from {previous_anchor.sha} to "
            f"{records_head_sha}, and {previous_anchor.sha} is not among the new head's "
            "ancestors — a head that does not descend from the last anchored SHA is proof "
            "of rewriting rather than evidence of it (D107)"
        ),
        first_seen="",
    )
    return new_anchor, finding
