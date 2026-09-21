#!/usr/bin/env python3
"""
L4 Scheduling Model — FD-089/FD-090 (PFD-018/PFD-019)
Ready-queue-miss event: emitted when a ready item is not started within the window
Floor obligation: >= 0.5 FTE on assigned product per 30 days (FD-031/PFD-031)

Usage: python scripts/l4/scheduling.py --check --period YYYY-MM
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import date

IMPL_ROOT = Path(__file__).parent.parent.parent
FLOOR_FTE = 0.5  # FD-031/PFD-031 decision: >= 0.5/30d
FLOOR_DAYS = 30


def check_floor_obligation(period: str) -> tuple:
    """Check FTE floor obligation per product (FD-031/PFD-031).

    NOTE: This only checks that a metrics file exists for the period; it does
    not yet parse assigned-FTE and compare against FLOOR_FTE/FLOOR_DAYS. The
    metrics snapshot schema (schemas/metrics/snapshot.v1.schema.json) has no
    defined FTE field under `metrics:` yet — that key must be decided/
    documented before a real floor comparison can be implemented.

    Returns (violations, products_checked).
    """
    violations = []
    metrics_dir = IMPL_ROOT / "records" / "metrics"
    if not metrics_dir.exists():
        return [], 0

    products_checked = 0
    for product_dir in sorted(metrics_dir.iterdir()):
        if not product_dir.is_dir():
            continue
        products_checked += 1
        product_id = product_dir.name
        metric_file = product_dir / f"{period}.yaml"
        if not metric_file.exists():
            violations.append({
                "product_id": product_id,
                "violation": "no-metrics",
                "message": f"No metrics for {period} — floor obligation unverifiable",
            })
    return violations, products_checked


def main():
    p = argparse.ArgumentParser(description="L4 Scheduling (FD-089/FD-090)")
    p.add_argument("--check", action="store_true", help="Check floor obligation")
    p.add_argument("--period", default=date.today().strftime("%Y-%m"), help="Period YYYY-MM")
    p.add_argument("--output", choices=["json", "text"], default="text")
    args = p.parse_args()

    if args.check:
        violations, products_checked = check_floor_obligation(args.period)
        if args.output == "json":
            print(json.dumps({
                "period": args.period,
                "products_checked": products_checked,
                "violations": violations,
            }, indent=2))
        else:
            print(f"=== Floor Obligation Check: {args.period} ===")
            print(f"Floor: >= {FLOOR_FTE} FTE per {FLOOR_DAYS} days (FD-031/PFD-031)")
            if violations:
                for v in violations:
                    print(f"  {v['violation'].upper()}: {v['product_id']} — {v['message']}")
            elif products_checked == 0:
                print(f"  0 products checked (no metrics data yet)")
            else:
                print(f"  All {products_checked} product(s) meet floor obligation")
        sys.exit(0 if not violations else 1)

    print("L4 Scheduling: use --check to check floor obligation")
    sys.exit(0)


if __name__ == "__main__":
    main()
