"""L3-P7-03: registry-edit canary staging (spec 26.4, 61.5).

Section 26.4, "Registry edits stage before they reach the fleet," names
two rules, transcribed:

  Rule one: "a merged registry change is applied by the next
  reconciliation run to the declared canary set only; the remainder of
  the fleet is held for one reconciliation cycle and applied only after
  the canary cycle records a clean run."

  Rule two (an authority-delta CI gate on registry pull requests, not a
  reconciliation-time staging concern) is out of scope here - it is
  L3-P7-04, `validators/drift/authority_delta.py` (FD-025).

"Clean" is not redefined here: it is the run-record status the Phase 1
instrument already produces (reconciler.runrecord.RunRecord.status is
"OK" or "FAILED"). A FAILED canary cycle - including a canary-missing
run, which reconciler.cli's full-run path and L3-P1-17's zero-findings
FAIL rule (AT-102) already force to FAILED - is never clean, so this
module does not re-derive canary-presence itself; it simply reads
`.status` off the RunRecord the caller passes as `last_canary_run`.

§61.3 ("The canary set is configurable in `platform.yaml`"; "An
unexercised canary is not a passed canary") is honoured by failing
closed on an empty canary set rather than silently treating "no
canary declared" as "no canary needed."

§26.4 also says "Both rules remain binding in bootstrap." `stage()`
accepts a `bootstrap` flag purely so callers can name that mode - it
never changes the return value; there is no bootstrap branch in the
logic below to bypass.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from reconciler.runrecord import RunRecord


class StagingError(RuntimeError):
    """The declared staging configuration is absent or unusable."""


@dataclass(frozen=True)
class RegistryChange:
    """A merged registry change, named by the products it touches.

    `affected_products` is the change's own declared scope - the set of
    products (or shared services) whose declared state this change
    edits. It is not the fleet; the fleet is whatever wider set the
    caller is reconciling this cycle.
    """

    id: str
    affected_products: frozenset[str]

    def __post_init__(self) -> None:
        object.__setattr__(self, "affected_products", frozenset(self.affected_products))


def stage(
    change: RegistryChange,
    canary_set: Iterable[str],
    last_canary_run: RunRecord | None,
    *,
    bootstrap: bool = False,
) -> frozenset[str]:
    """Return the set of `change.affected_products` this run may apply to.

    - No prior canary run recorded for this change (`last_canary_run`
      is None): this is wave 1. Apply to the canary set only.
    - The immediately preceding canary cycle was not clean (`status !=
      "OK"` - FAILED, including a canary-missing run): hold the fleet;
      apply to the canary set only, again.
    - The immediately preceding canary cycle was clean (`status ==
      "OK"`): release the fleet - apply to every affected product.

    `bootstrap` is accepted and does nothing: §26.4 binds both rules in
    bootstrap mode too, so there is no bypass branch to write.
    """
    del bootstrap  # named for callers; never changes the outcome (§26.4)

    canary = frozenset(canary_set)
    if not canary:
        raise StagingError(
            "declared canary set is empty - an unexercised canary is not a "
            "passed canary (spec 61.3); refusing to stage anything"
        )

    affected = change.affected_products
    canary_wave = affected & canary

    if last_canary_run is None:
        return canary_wave
    if last_canary_run.status != "OK":
        return canary_wave
    return affected
