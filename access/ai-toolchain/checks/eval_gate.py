#!/usr/bin/env python3
"""AI-eval pin-adoptability arithmetic (Section 38.3, SIG-42, AT-107).

This is Lane 5's slice of the AI-eval scheduled runner named in Section
99.2's tool table: "Executes each declared product evaluation suite on
schedule and on pin change, writing records/eval/ and raising SIG-42 on
regression." Per the boundary access/tests/at-107-eval-regression-blocks-
pin.sh already states: the run history and the category-five incident
record are L4's (metrics/compute/eval.py, records/eval/); this script never
reads or writes either. What it owns is the pure arithmetic: given a
baseline score document and a candidate score document (each a JSON object
mapping scored dimension -> percentage score, the shape
`access/ai-toolchain/benchmark/*` scenario runs already produce), decide
whether the candidate is adoptable.

Tolerance (access/ai-toolchain/checks/eval-tolerance.yaml, spec line 4577):
a candidate is a regression on any dimension that falls more than 5
percentage points below its recorded baseline.

Usage:
  eval_gate.py <baseline.json> <candidate.json>
  eval_gate.py --selftest

Exit 0 ADOPT (no dimension regressed beyond tolerance)
Exit 1 BLOCK (SIG-42: at least one dimension regressed beyond tolerance)
Exit 2 fail-closed (either score document missing, unreadable, or malformed)
"""
import json
import os
import sys

TOLERANCE_PP = 5


def load_scores(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, ValueError):
        return None
    dims = doc.get("scored_dimensions")
    if not isinstance(dims, dict) or not dims:
        return None
    for value in dims.values():
        if not isinstance(value, (int, float)):
            return None
    return dims


def decide(baseline, candidate):
    """Return (adoptable, regressions) where regressions is a list of
    (dimension, baseline_value, candidate_value, drop) tuples for every
    dimension the candidate regressed on beyond tolerance. A dimension
    present in baseline but absent from candidate is treated as a full
    regression (fail-closed: a vanished dimension is not evidence of
    improvement)."""
    regressions = []
    for dim, base_value in sorted(baseline.items()):
        if dim not in candidate:
            regressions.append((dim, base_value, None, None))
            continue
        cand_value = candidate[dim]
        drop = base_value - cand_value
        if drop > TOLERANCE_PP:
            regressions.append((dim, base_value, cand_value, drop))
    return (len(regressions) == 0, regressions)


def selftest():
    fixtures_dir = os.path.join("access", "tests", "fixtures")
    baseline_path = os.path.join(fixtures_dir, "at-107-eval-baseline.json")
    regression_path = os.path.join(fixtures_dir, "at-107-eval-regression.json")
    within_path = os.path.join(fixtures_dir, "at-107-eval-within-tolerance.json")

    baseline = load_scores(baseline_path)
    if baseline is None:
        print("SELFTEST FAIL: %s unreadable or malformed" % baseline_path)
        return 2

    regression = load_scores(regression_path)
    within = load_scores(within_path)
    if regression is None or within is None:
        print("SELFTEST FAIL: fixture score documents unreadable or malformed")
        return 2

    adoptable, regs = decide(baseline, regression)
    if adoptable:
        print("SELFTEST FAIL: the regression fixture was wrongly ruled adoptable")
        return 1

    adoptable2, regs2 = decide(baseline, within)
    if not adoptable2:
        print("SELFTEST FAIL: the within-tolerance fixture was wrongly blocked: %r" % regs2)
        return 1

    # Negative fixture: exactly at the tolerance boundary is NOT a
    # regression ("more than 5 percentage points", not "5 or more").
    boundary_baseline = {"accuracy": 90.0}
    boundary_candidate = {"accuracy": 85.0}  # exactly 5pp drop
    boundary_adoptable, _ = decide(boundary_baseline, boundary_candidate)
    if not boundary_adoptable:
        print("SELFTEST FAIL: a drop of exactly 5.0pp was blocked; spec says "
              "'more than 5', so exactly 5 must adopt")
        return 1

    # Negative fixture: a vanished dimension must fail closed, not silently pass.
    vanished_baseline = {"accuracy": 90.0, "groundedness": 88.0}
    vanished_candidate = {"accuracy": 91.0}
    vanished_adoptable, vanished_regs = decide(vanished_baseline, vanished_candidate)
    if vanished_adoptable or not any(r[0] == "groundedness" for r in vanished_regs):
        print("SELFTEST FAIL: a vanished scored dimension was not treated as a regression")
        return 1

    print("L5-T30 SELF-VERIFY PASS")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if len(argv) != 2:
        print("USAGE: eval_gate.py <baseline.json> <candidate.json>")
        return 2

    baseline = load_scores(argv[0])
    candidate = load_scores(argv[1])
    if baseline is None or candidate is None:
        print("EVAL-GATE: FAIL-CLOSED (unreadable or malformed score document)")
        return 2

    adoptable, regressions = decide(baseline, candidate)
    if not adoptable:
        for dim, base_value, cand_value, drop in regressions:
            if cand_value is None:
                print("SIG-42 REGRESSION %s: present in baseline (%.1f), "
                      "absent from candidate" % (dim, base_value))
            else:
                print("SIG-42 REGRESSION %s: %.1f -> %.1f (drop %.1fpp, "
                      "tolerance %dpp)" % (dim, base_value, cand_value, drop, TOLERANCE_PP))
        print("EVAL-GATE: BLOCK (SIG-42 raised, pin not adopted)")
        return 1
    print("EVAL-GATE: ADOPT (0 dimensions regressed beyond %dpp)" % TOLERANCE_PP)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
