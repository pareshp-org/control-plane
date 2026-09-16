"""reconciler.orphans - the sixteen-type orphan detection framework (spec §12.2; §101 invariant 57).

Orphan detection answers a different question than reconciler.cli's
comparator `run`: not "does declared state match actual state" but
"does every responsibility §12.2 names have a live holder". The two
pipelines share nothing at runtime (spec 0.4: declared state is always
local control-plane content; orphan detection never reaches `--live`
in this cluster) but share the same severity vocabulary in spirit -
`OrphanFinding.orphan_severity` uses the same four-word scale as
`reconciler.model.DriftClass`, transcribed as plain strings here
because §12.2's table prints them that way and L3-P2-01's acceptance
criterion 3 forbids rewording the table.

This module holds the framework three things share:

* `OrphanContext` / `load_context()` - the one place fixture-a's
  declared/** documents an orphan detector needs (people, products,
  shared services, assets, board, policies, exceptions) are read off
  disk. Detector modules take a context, never a path.
* `OrphanFinding` - the one record shape every detector emits.
* `is_empty()` / `is_inactive_login()` - the two predicates spec §12.2
  repeats for every slot: empty, or held by someone `departed`/
  `revoked`. `availability: departing` is deliberately **not** treated
  as inactive here (L3-P2-02's STOP rule) - it is prospective mode's
  trigger (L3-P2-05), not a current-mode orphan condition. Prospective
  mode overrides the predicate for exactly one login at a time via
  `prospective_login`, never by mutating the fixture or the context.
* `run_group()` - the `--group` dispatcher `reconciler.cli`'s `orphans`
  subcommand calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

FIXTURES_ROOT = Path(__file__).resolve().parent.parent / "fixtures"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


@dataclass(frozen=True)
class OrphanFinding:
    """One instance of an orphaned responsibility (spec §12.2).

    `subject` names the concrete thing that is orphaned (a product id,
    an asset id, a shared-service name, a policy id, ...) - it is the
    dedup key prospective mode (L3-P2-05) compares against the current
    run's findings, paired with `index`.
    """

    index: int
    name: str
    orphan_severity: str
    subject: str
    detail: str
    prospective: bool = False
    orphans_on: str | None = None


@dataclass(frozen=True)
class OrphanContext:
    """Every declared-state document a §12.2 detector reads, loaded
    once per invocation from one fixture's declared/** tree.
    """

    fixture_name: str
    as_of: date
    people: list[dict[str, Any]]
    products: dict[str, dict[str, Any]]
    shared_services: list[dict[str, Any]]
    assets: list[dict[str, Any]]
    board_items: list[dict[str, Any]]
    open_gate_items: list[dict[str, Any]]
    migrations: list[dict[str, Any]]
    policies: list[dict[str, Any]]
    exceptions: list[dict[str, Any]]

    def person(self, login: str) -> dict[str, Any] | None:
        for candidate in self.people:
            if candidate.get("github_login") == login:
                return candidate
        return None


def load_context(fixture_name: str, as_of: date, fixtures_root: Path | None = None) -> OrphanContext:
    declared_root = (fixtures_root or FIXTURES_ROOT) / fixture_name / "declared"

    products: dict[str, dict[str, Any]] = {}
    products_dir = declared_root / "products"
    if products_dir.is_dir():
        for path in sorted(products_dir.glob("*.yaml")):
            products[path.stem] = _load_yaml(path)

    board = _load_yaml(declared_root / "board.yaml")

    return OrphanContext(
        fixture_name=fixture_name,
        as_of=as_of,
        people=_load_yaml(declared_root / "people.yaml").get("people", []),
        products=products,
        shared_services=_load_yaml(declared_root / "shared-services.yaml").get("services", []),
        assets=_load_yaml(declared_root / "assets.yaml").get("assets", []),
        board_items=board.get("items", []),
        open_gate_items=board.get("open_gate_items", []),
        migrations=board.get("migrations", []),
        policies=_load_yaml(declared_root / "policies.yaml").get("policies", []),
        exceptions=_load_yaml(declared_root / "exceptions.yaml").get("exceptions", []),
    )


def is_empty(value: Any) -> bool:
    return value is None or value == ""


def is_inactive_login(ctx: OrphanContext, login: str, *, prospective_login: str | None = None) -> bool:
    """True when `login` is not a live holder.

    Current mode (`prospective_login=None`): true only for
    `availability: departed` or `access_status: revoked`.
    `availability: departing` is active - it is not this predicate's
    concern (L3-P2-02's STOP rule).

    Prospective mode: additionally true when `login == prospective_login`
    - the one departing person being projected forward to their own
    `end_date`, per L3-P2-05. This never mutates the fixture or the
    context; it is a per-call override of this one predicate.
    """
    if prospective_login is not None and login == prospective_login:
        return True
    person = ctx.person(login)
    if person is None:
        return False
    return person.get("availability") == "departed" or person.get("access_status") == "revoked"


def slot_orphaned(ctx: OrphanContext, value: Any, *, prospective_login: str | None = None) -> bool:
    """The one rule repeated for every §12.2 slot: orphaned when empty
    **or** held by an inactive login (spec §12.2; L3-P2-02)."""
    if is_empty(value):
        return True
    return is_inactive_login(ctx, value, prospective_login=prospective_login)


def run_group(
    group: str, ctx: OrphanContext, *, prospective_login: str | None = None
) -> tuple[list[OrphanFinding], int]:
    """Dispatch to the detector module for one `--group` value.

    Imported lazily (inside the function body, not at module scope) so
    that `ownership.py` / `assets.py` / `governance.py` can themselves
    `from reconciler.orphans import ...` without a circular import at
    package-init time.
    """
    from reconciler.orphans import assets as _assets
    from reconciler.orphans import governance as _governance
    from reconciler.orphans import ownership as _ownership

    detectors = {
        "ownership": _ownership.detect,
        "assets": _assets.detect,
        "governance": _governance.detect,
    }
    if group not in detectors:
        raise ValueError(f"unknown orphan group {group!r} (expected one of {sorted(detectors)})")
    return detectors[group](ctx, prospective_login=prospective_login)
