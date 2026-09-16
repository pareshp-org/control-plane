"""L3-P0-04: load and sanity-check a reconciler fixture set.

``fixture-a`` is the single source of every expected number transcribed
across lanes/L3-06-tasks.md — every later SELF-VERIFY count derives from
its sixteen data files. This module loads them, asserts each exists and
parses, and reports how many it found.

Usage: ``python -m reconciler.fixtures.verify <fixture-name>``
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

# The sixteen fixture data files fixture-a defines (Files 1-16 of L3-P0-04),
# relative to reconciler/fixtures/<name>/. This list is fixed by the task
# spec; do not add or remove entries without also correcting the expected
# files=16 count in every task that reads this fixture.
FIXTURE_FILES = [
    "declared/people.yaml",
    "declared/products/alpha.yaml",
    "declared/products/beta.yaml",
    "declared/platform.yaml",
    "declared/os-health.yaml",
    "declared/assets.yaml",
    "declared/policies.yaml",
    "declared/exceptions.yaml",
    "declared/shared-services.yaml",
    "declared/board.yaml",
    "declared/templates/branch-protection.json",
    "declared/templates/environment.json",
    "actual/org.json",
    "actual/codeowners/alpha.CODEOWNERS",
    "actual/codeowners/beta.CODEOWNERS",
    "canary.yaml",
]


def _parse(path: Path):
    """Parse one fixture file according to its extension.

    CODEOWNERS files have no structured format; "parsing" them means
    reading their text and confirming it is non-empty, which is the only
    property any consumer of a CODEOWNERS fixture relies on.
    """
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    if path.name.endswith(".CODEOWNERS"):
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            raise ValueError(f"{path}: CODEOWNERS fixture is empty")
        return text
    raise ValueError(f"{path}: unrecognised fixture file type")


def load_fixture(name: str, base: Path | None = None) -> dict:
    """Load and parse every file in FIXTURE_FILES for fixture ``name``.

    Returns a dict of relative-path -> parsed content. Raises
    FileNotFoundError naming the missing file if any is absent, and
    propagates the underlying parse error (with the path prefixed) if any
    file fails to parse.
    """
    root = (base or Path(__file__).parent) / name
    if not root.is_dir():
        raise FileNotFoundError(f"fixture root does not exist: {root}")

    parsed: dict[str, object] = {}
    for rel in FIXTURE_FILES:
        path = root / rel
        if not path.is_file():
            raise FileNotFoundError(f"missing fixture file: {rel} (under {root})")
        parsed[rel] = _parse(path)
    return parsed


def summarize(name: str, base: Path | None = None) -> str:
    """Return the FIXTURE summary line for L3-P0-04's SELF-VERIFY."""
    parsed = load_fixture(name, base=base)

    people_doc = parsed["declared/people.yaml"]
    people_count = len(people_doc.get("people", [])) if isinstance(people_doc, dict) else 0

    product_files = [rel for rel in FIXTURE_FILES if rel.startswith("declared/products/")]
    products_count = len(product_files)

    return f"FIXTURE {name} files={len(FIXTURE_FILES)} people={people_count} products={products_count}"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: python -m reconciler.fixtures.verify <fixture-name>", file=sys.stderr)
        return 2

    print(summarize(argv[0]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
