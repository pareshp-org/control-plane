"""L3-P1-14: record-store write freshness (spec 53.1; §97.2 "zero is the good value").

For each store declared in os-health.yaml's write_freshness_max_hours,
staleness past the declared window is Amber - except `events/`,
`records/deployments/` and `records/uat/`, which are Blocking (§53.1,
§97.2). `as_of` is a date with no time-of-day; the comparison uses
midnight UTC of that date, clamped to zero hours elapsed when the
actual last-write timestamp falls later the same day (a same-day write
is never "stale" for want of clock resolution finer than a day).
"""

from __future__ import annotations

from datetime import datetime, timezone

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator

_BLOCKING_STORES = frozenset({"events/", "records/deployments/", "records/uat/"})


def _hours_elapsed(as_of, last_write_iso: str) -> float:
    last_write = datetime.fromisoformat(last_write_iso.replace("Z", "+00:00"))
    as_of_midnight = datetime(as_of.year, as_of.month, as_of.day, tzinfo=timezone.utc)
    return max((as_of_midnight - last_write).total_seconds() / 3600.0, 0.0)


@comparator("write_freshness", fail_class=DriftClass.BLOCKING)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    first_seen = f"{as_of.isoformat()}T00:00:00Z"
    max_hours = declared.os_health.get("write_freshness_max_hours") or {}
    last_writes = actual.store_last_write()

    for store, limit_hours in max_hours.items():
        last_write_iso = last_writes.get(store)
        if last_write_iso is None:
            continue
        elapsed = _hours_elapsed(as_of, last_write_iso)
        if elapsed > limit_hours:
            drift_class = DriftClass.BLOCKING if store in _BLOCKING_STORES else DriftClass.AMBER
            level = Level.BLOCK if drift_class == DriftClass.BLOCKING else Level.WARN
            findings.append(
                Finding(
                    id=f"write_freshness:{store}",
                    comparator="write_freshness",
                    scope=store,
                    drift_class=drift_class,
                    level=level,
                    evidence=(
                        f"{store} last wrote {last_write_iso}, {elapsed:.1f}h ago, past "
                        f"its {limit_hours}h freshness window"
                    ),
                    first_seen=first_seen,
                )
            )

    return findings, len(max_hours)
