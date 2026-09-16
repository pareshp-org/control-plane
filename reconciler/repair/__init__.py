"""reconciler.repair - Phase 6 auto-repair (spec 53.2 Level 3; spec 99.6 risk 6).

Every repair class under this package is built against the same
three-part contract set out in lanes/L3-06-tasks.md's Phase 6 preamble:
it consumes a finding produced by Phase 1 or 2, it asks stricter.py's
`permitted()` for permission before writing anything, and it produces
a `Repair`. No repair class may bypass any of the three -
reconciler/repair/guards.py enforces the first at import time once it
lands.

`Repair` is the one record shape every class returns, so a future
uniform emitter (L3-P6-08, reconciler/repair/records.py) can consume
any class's output without a per-class adapter. It intentionally
carries no `performed_at` or `run_id` - those are run-level metadata
the caller has in scope, not the repair class itself; L3-P6-08 adds
them (plus a schema-conformant shape) when a Repair becomes a full
repair_record.

No module in this package holds a write method against live GitHub -
reconciler.state.port.GitHubState stays read-only (spec 0.3, 0.4).
Every class here therefore computes the change it is permitted to make
and returns it as a Repair; the actual GitHub-side write, "under the
reconciler credential" (spec 26.4), is a runtime step outside this
lane's current build - no task in lanes/L3-06-tasks.md's Phase 6 names
a live write client, and none is invented here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Repair:
    """One repair a Phase 6 class computed permission for and would
    perform. `before`/`after` describe the one control's state on
    either side of the change; `permitted_reason` records why
    stricter.py's `permitted()` allowed it; `compensating_action`
    names the tested revert path spec 53.7/28.1 requires every change
    plan to carry.
    """

    repair_class: str
    finding_id: str
    scope: str
    before: Any
    after: Any
    permitted_reason: str
    compensating_action: str
