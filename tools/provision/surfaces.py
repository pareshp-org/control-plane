"""L3-P0-AT001: the `cp-10-surfaces` step -- surface registration is read-only.

Spec basis: Section 19.1 ("Automatic discovery is mandatory ... every
one of those surfaces enumerates from the product registry"); Section
11 (no hard-coded repository/product list); invariant 52; AT-001.

This module loads the six declared surfaces (`surfaces.yaml`) and
exposes the one step a `create-product` orchestrator runs against
them: **confirm**, never register. "This task adds no registration
call. Registration is a consequence of the registry entry" -- once a
product's directory exists under `registries/products/`, every
compliant surface already enumerates it on its own next read. The
step therefore issues no surface-specific write call of any kind (not
even a `POST` to "register" the product on a dashboard) -- the only
network-shaped call any surface probe may ever make is a `GET`, and
only from `verify_surfaces.py`'s `--live` path, never from here.

(Layout note: `L3-P0-AT001`'s own text, ported from the superseded
`lanes/L3-04-provisioning.md` task `L3-04-12`, names a nested
`tools/provision/provision/steps/surfaces.py` path. FD-045/FD-B1-L3
makes the flat `tools/provision/` layout -- the one every other
L3-06-tasks.md task in this lane already uses -- authoritative for any
re-implementation; this module lives at the flat path accordingly.)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_SURFACES_PATH = Path(__file__).resolve().parent / "surfaces.yaml"


@dataclass(frozen=True)
class Surface:
    id: str
    enumerates_from: str
    live_probe: str


def load_surfaces(path: Path | None = None) -> list[Surface]:
    """Load the declared surface list. Six entries, always -- Section
    19.1 names exactly six surfaces and this file never grows a
    product-specific row."""
    data: dict[str, Any] = yaml.safe_load((path or _SURFACES_PATH).read_text(encoding="utf-8")) or {}
    return [Surface(**entry) for entry in data.get("surfaces", [])]


@dataclass(frozen=True)
class StepResult:
    step_id: str
    kind: str  # "read" -- this step never writes
    surfaces_confirmed: tuple[str, ...]
    note: str


def run(surfaces: list[Surface] | None = None) -> StepResult:
    """The `cp-10-surfaces` step: read the declared surfaces and confirm
    each enumerates from the product registry. No API call of any
    kind is made here -- confirming a surface's *declared*
    configuration needs nothing beyond `surfaces.yaml` itself; only
    `verify_surfaces.py --live` reaches out (read-only, `GET` only) to
    check a surface's *actual* configuration.
    """
    loaded = surfaces if surfaces is not None else load_surfaces()
    non_registry = [s.id for s in loaded if s.enumerates_from != "product_registry"]
    if non_registry:
        raise ValueError(
            f"surface(s) {non_registry} do not enumerate from product_registry -- "
            "Section 19.1 requires every surface to (a defect, not a task)"
        )
    return StepResult(
        step_id="cp-10-surfaces",
        kind="read",
        surfaces_confirmed=tuple(s.id for s in loaded),
        note="registration is a consequence of the registry entry; no write performed",
    )
