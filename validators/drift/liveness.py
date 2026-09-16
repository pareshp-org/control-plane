"""L3-P5-05: verifier absence for one cycle is Level 5
(spec 53.1: "its own absence for one cycle is Level 5"; spec 53.2 Level 5;
AT-032 — self-observability, "detects and reports a failure in its own
reconciliation").

``check_liveness()`` is a plain function ``reconciler/signals.py`` may
import so a dead independent verifier (validators/drift/verifier.py) is
visible from *both* sides of the wall it audits — the verifier side
cannot report its own absence once it is actually dead, so the
reconciler side runs this same check independently over the last
recorded verifier result, catching exactly that case.

Pure by construction: no clock read, no write, no notification. Every
timestamp is an argument; the caller owns "now."
"""

from __future__ import annotations

from datetime import datetime, timedelta

from reconciler.model import DriftClass, Finding, Level


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def check_liveness(last_verifier_result_at: str, as_of: str, cycle_hours: float) -> Finding | None:
    """Returns a Level.ESCALATE / Blocking Finding once the gap between
    `last_verifier_result_at` and `as_of` exceeds one verifier cycle
    (`cycle_hours` hours); returns None while the gap is within one
    cycle (a gap exactly equal to one cycle has not yet *exceeded* it).
    """
    gap = _parse(as_of) - _parse(last_verifier_result_at)
    cycle = timedelta(hours=cycle_hours)
    if gap <= cycle:
        return None
    return Finding(
        id="drift_verifier:absent",
        comparator="drift_verifier_liveness",
        scope="drift_verifier",
        drift_class=DriftClass.BLOCKING,
        level=Level.ESCALATE,
        evidence=(
            f"the independent verifier (validators/drift/verifier.py) has not reported a "
            f"result in {gap} (one cycle is {cycle}) — its own absence for one cycle is "
            "Level 5 (spec 53.1)"
        ),
        first_seen=as_of,
    )
