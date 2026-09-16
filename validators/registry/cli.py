#!/usr/bin/env python3
"""
L1 Validator Registry CLI — Option B design (FD-094, 2026-09-09)
Entry point: python -m validators.registry.cli
Usage: python -m validators.registry.cli --root <p> --as-of <d> --records-root <p> --format json [--rule Rnn]
Exit codes: 0=pass, 1=fail, 2=input-error
Rules: R01-R18 (validators/registry/rules/)
"""
import argparse
import json
import sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(
        description="Multi-Product Registry Validator (Option B, FD-094)"
    )
    p.add_argument("--root", required=True, help="Registry root path")
    p.add_argument(
        "--as-of", required=True, dest="as_of", help="Validation date (YYYY-MM-DD)"
    )
    p.add_argument(
        "--records-root",
        required=False,
        dest="records_root",
        help="Records root path",
    )
    p.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    p.add_argument("--rule", help="Run single rule (e.g. R01, R07)")
    return p.parse_args()


def main():
    args = parse_args()
    registry_root = args.root
    as_of = args.as_of
    records_root = args.records_root

    if not Path(registry_root).is_dir():
        msg = f"--root path does not exist or is not a directory: {registry_root}"
        if args.format == "json":
            print(json.dumps({"status": "ERROR", "error": msg}, indent=2))
        else:
            print(f"ERROR: {msg}")
        sys.exit(2)

    try:
        from validators.registry.rules.registry import load_rule, run_all

        if args.rule:
            mod = load_rule(args.rule)
            passed, findings = mod.check(registry_root, as_of, records_root)
            results = [(args.rule, passed, findings)]
        else:
            results = run_all(registry_root, as_of, records_root)
    except Exception as e:
        if args.format == "json":
            print(json.dumps({"status": "ERROR", "error": str(e)}, indent=2))
        else:
            print(f"ERROR: {e}")
        sys.exit(2)

    all_passed = all(r[1] for r in results)
    findings_flat = [f for _, _, fs in results for f in fs]

    if args.format == "json":
        print(
            json.dumps(
                {
                    "status": "PASS" if all_passed else "FAIL",
                    "rules_run": len(results),
                    "findings": findings_flat,
                },
                indent=2,
            )
        )
    else:
        for name, passed, findings in results:
            icon = "PASS" if passed else "FAIL"
            print(f"[{icon}] {name}")
            for f in findings:
                print(f"  - {f}")
        print(f"\nOverall: {'PASS' if all_passed else 'FAIL'} ({len(results)} rules)")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
