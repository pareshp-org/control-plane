"""L3-P0-AT001: create-product scaffold conformance verifier.

Spec basis: Section 19.1 ("Automatic discovery is mandatory ... If a
human must edit a dashboard to add a product, that is a defect in the
operating system, not a task"); Section 11 (no hard-coded repository
list); invariant 52; AT-001 ("No dashboard, workflow or script
contains a product list"); Section 20.2; Section 92.3.

Two checks, neither of which needs a registration call to exist --
"this task adds no registration call; registration is a consequence
of the registry entry":

* **Static** (always runs, no live infrastructure needed). For every
  product id currently declared under `registries/products/`, scan
  the whole control-plane tree -- excluding the registry directory
  itself, `records/`, `events/` and `.git/` -- for a literal
  occurrence of that id. Any hit is a defect:
  `HARD-CODED-PRODUCT: <path>:<line> contains product id '<id>'`,
  exit 3.
* **Live** (`--live`). Probe each declared surface. An unreachable
  surface prints `SURFACE <id> UNREACHABLE` and the run exits 3 --
  never a silent pass for a surface nothing was actually reached on
  (Section 92.3, Section 64.2: visible degradation, always).

(Layout note: see `surfaces.py` -- the flat `tools/provision/` layout
is authoritative per FD-045/FD-B1-L3; the entry point here is
`python -m tools.provision.verify_surfaces`, not the superseded
`python -m provision verify-surfaces`.)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable, Iterable

from tools.provision.surfaces import Surface, load_surfaces

# Section 19.1's static check runs "outside the registry directory
# itself and outside records/ / events/" -- and outside .git, which
# is not a control-plane surface of any kind.
_EXCLUDED_TOP_LEVEL = ("registries", "records", "events", ".git")


def declared_product_ids(root: Path) -> list[str]:
    """Every product id currently declared under
    `registries/products/<id>/`. Empty if the directory does not
    exist yet -- a bootstrap fact, not an error: there is nothing to
    hard-code a reference to until a first product is declared."""
    products_dir = root / "registries" / "products"
    if not products_dir.is_dir():
        return []
    return sorted(p.name for p in products_dir.iterdir() if p.is_dir())


def _iter_scannable_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            rel_parts = path.relative_to(root).parts
        except ValueError:
            continue
        if rel_parts and rel_parts[0] in _EXCLUDED_TOP_LEVEL:
            continue
        yield path


def static_check(root: Path, product_ids: list[str] | None = None) -> list[str]:
    """Return one `HARD-CODED-PRODUCT: ...` line per literal hit of a
    declared product id outside the excluded directories. An empty
    list means compliant -- including, honestly, when there are
    simply no product ids declared yet to search for."""
    ids = product_ids if product_ids is not None else declared_product_ids(root)
    if not ids:
        return []
    hits: list[str] = []
    for path in _iter_scannable_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for product_id in ids:
                if product_id in line:
                    rel = path.relative_to(root).as_posix()
                    hits.append(f"HARD-CODED-PRODUCT: {rel}:{lineno} contains product id '{product_id}'")
    return hits


def run_static(root: Path) -> int:
    hits = static_check(root)
    for hit in hits:
        print(hit)
    print(f"SURFACES-STATIC: {len(hits)} HARD-CODED")
    return 3 if hits else 0


LiveProbe = Callable[[Surface], bool]


def _no_live_infrastructure(surface: Surface) -> bool:
    """The default prober: no portfolio board, Grafana, Scorecard,
    DevLake, reviewer-matrix or dependency-graph deployment exists in
    this environment to reach. Every surface is honestly unreachable
    rather than a fabricated pass."""
    return False


def run_live(surfaces: list[Surface], prober: LiveProbe = _no_live_infrastructure) -> int:
    exit_code = 0
    for surface in surfaces:
        if prober(surface):
            print(f"SURFACE {surface.id} OK")
        else:
            print(f"SURFACE {surface.id} UNREACHABLE")
            exit_code = 3
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.provision.verify_surfaces")
    parser.add_argument("--list", action="store_true", help="print each of the six declared surface ids")
    parser.add_argument("--static", action="store_true", help="scan --root for a hard-coded product id")
    parser.add_argument("--live", action="store_true", help="probe every surface for reachability")
    parser.add_argument("--root", default=None, help="control-plane root to scan (required with --static)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    surfaces = load_surfaces()

    if args.list:
        for surface in surfaces:
            print(surface.id)
        return 0

    if args.static:
        if not args.root:
            print("error: --static requires --root", file=sys.stderr)
            return 1
        return run_static(Path(args.root))

    if args.live:
        return run_live(surfaces)

    print("error: one of --list, --static or --live is required", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
