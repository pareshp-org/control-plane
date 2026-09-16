"""L3-P5-04: verifier assertion C — the bypass-actor list is exactly as
declared (spec 53.1: "that the ruleset bypass-actor list is exactly the
set Sections 40.1 and 33.2 declare, with their declared scopes"; §40.1
D89: "no machine identity is a bypass actor" on the control plane;
§33.2).

Registers assertion id ``bypass_actors_exact``. The declared set below
is a literal table transcribed from the spec, each row citing its
section — never inferred from the actual state the assertion checks it
against (spec 53.1's own acceptance rule for this assertion). Any
ruleset whose actual bypass-actor set differs from its declared row, in
either direction, fails; a ruleset present in the actual state under a
name this table does not recognise fails closed rather than being
skipped — an unrecognised ruleset is exactly the kind of undeclared
surface this assertion exists to catch, not a case to wave through.
``checked`` is the number of rulesets examined.
"""

from __future__ import annotations

from validators.drift.verifier import AssertionResult, VerifierState, assertion

# Transcribed cell for cell from spec 40.1 and 33.2 — see this module's
# docstring on why this table is literal rather than derived.
DECLARED_BYPASS_ACTORS: dict[str, frozenset[str]] = {
    # §40.1: "No bypass actor exists" on the control-plane repository;
    # D89 makes this "literally true rather than true-by-convention."
    "control-plane": frozenset(),
    # D107: the records repository's force-push/deletion ruleset has no
    # bypass actor.
    "records-force-push-deletion": frozenset(),
    # §33.2: the workflows/* tag ruleset carries an empty bypass-actor
    # list.
    "workflows-tag": frozenset(),
    # §33.2: Renovate ruleset A (the pull-request rules) may list the
    # Renovate app and nothing else.
    "renovate-A": frozenset({"renovate[bot]"}),
    # §33.2, D89: Renovate ruleset B (the renovate-path-guard check) has
    # no bypass actor at all.
    "renovate-B": frozenset(),
}


@assertion("bypass_actors_exact")
def check(state: VerifierState) -> AssertionResult:
    rulesets = state.rulesets()

    offending: list[str] = []
    for ruleset in rulesets:
        name = ruleset.get("name")
        actual = frozenset(ruleset.get("bypass_actors", []))

        if name not in DECLARED_BYPASS_ACTORS:
            # STOP (this task's own instruction): a live ruleset naming
            # a bypass actor outside the declared table is the finding
            # itself — never a reason to widen the table.
            offending.append(f"{name}: no declared bypass-actor set for this ruleset (fail-closed)")
            continue

        declared = DECLARED_BYPASS_ACTORS[name]
        if actual != declared:
            offending.append(
                f"{name}: actual bypass actors {sorted(actual)} != declared {sorted(declared)}"
            )

    return AssertionResult(
        passed=not offending,
        checked=len(rulesets),
        detail="; ".join(offending),
    )
