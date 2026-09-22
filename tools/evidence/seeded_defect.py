#!/usr/bin/env python3
"""
tools.evidence.seeded_defect
L2-T517: Seeded-defect execution and SIG-18 (§31.2)

A passing seeded case is a FAILED run — the inversion.
SIG-18 is raised when the seeded case passes.

Exit codes per §0.4: 0=OK, 2=FAIL, 3=ERROR
"""
from __future__ import annotations

import argparse
import json
import os
import sys

TOOL_ID = "seeded_defect"


def _summary(status: str, checked: int, failed: int) -> None:
    print(f"{status} {TOOL_ID} checked={checked} failed={failed}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate seeded-defect case results under the §31.2 Inversion rule")
    parser.add_argument("--result", required=True, help="Path to seeded case result JSON")
    parser.add_argument("--summary", action="store_true", help="Print summary line per §0.4")
    args = parser.parse_args()

    if not os.path.exists(args.result):
        print(f"ERROR: result file not found: {args.result}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    try:
        with open(args.result, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot parse result JSON: {exc}", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    if not isinstance(data, dict):
        print("ERROR: result JSON is not a mapping", file=sys.stderr)
        _summary("ERROR", 0, 0)
        sys.exit(3)

    cases = data.get("seeded_cases", [])
    if not cases and "seeded_case" in data:
        sc = data["seeded_case"]
        cases = [sc] if isinstance(sc, dict) else sc

    if not cases:
        print(
            "ERROR: result file declares no seeded cases — absence is not a pass (§31.2)",
            file=sys.stderr,
        )
        _summary("ERROR", 0, 0)
        sys.exit(3)

    checked = len(cases)
    # The Inversion (§31.2): a seeded case that PASSED is an unhealthy failure of discrimination
    bad = [c for c in cases if c.get("passed", False) is True]
    failed_count = len(bad)

    if failed_count > 0:
        # SIG-18: a seeded case that passes proves the contract stopped discriminating
        print("SIG-18", file=sys.stderr)
        for c in bad:
            print(
                f"FAIL: seeded case '{c.get('id', 'unknown')}' PASSED — "
                "the contract stopped discriminating (SIG-18, §31.2)",
                file=sys.stderr,
            )
        _summary("FAIL", checked, failed_count)
        sys.exit(2)

    _summary("OK", checked, 0)
    sys.exit(0)


if __name__ == "__main__":
    main()
