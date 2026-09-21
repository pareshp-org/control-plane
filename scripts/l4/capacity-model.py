#!/usr/bin/env python3
"""
L4 Capacity Model — FD-089/FD-090 (PFD-018/PFD-019)
Working calendar: business days only; public holidays NOT yet integrated (Phase 1, FD-089)
FTE application: sum(fte) from people registry * working-day availability

Usage: python scripts/l4/capacity-model.py --period YYYY-MM [--output json|text]
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import date, timedelta

IMPL_ROOT = Path(__file__).parent.parent.parent


def business_days_in_month(year: int, month: int) -> list:
    """Return list of business days (Mon-Fri) in the given month."""
    result = []
    d = date(year, month, 1)
    while d.month == month:
        if d.weekday() < 5:  # Mon=0 ... Fri=4
            result.append(d)
        d += timedelta(days=1)
    return result


def load_people_registry() -> list:
    """Load all person records from registries/people/ (FD-090/PFD-019)."""
    people_dir = IMPL_ROOT / "registries" / "people"
    if not people_dir.exists():
        return []
    try:
        import yaml
    except ImportError:
        print("WARNING: pyyaml not installed — returning empty people registry", file=sys.stderr)
        return []

    people = []
    for person_file in sorted(people_dir.glob("*.yaml")):
        if person_file.name.startswith("_"):
            continue
        try:
            data = yaml.safe_load(person_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                people.append(data)
            else:
                print(f"WARNING: {person_file} did not parse to a mapping — skipped", file=sys.stderr)
        except Exception as exc:
            print(f"WARNING: {person_file} failed to parse ({exc}) — skipped", file=sys.stderr)
    return people


def compute_capacity(period: str) -> dict:
    """Compute capacity for a given YYYY-MM period."""
    year, month = int(period[:4]), int(period[5:7])
    business_days = business_days_in_month(year, month)
    people = load_people_registry()

    for p in people:
        if not p.get("id", "").startswith("_") and "fte" not in p:
            print(
                f"WARNING: person {p.get('id', '<unknown>')} has no 'fte' field — defaulting to 1.0",
                file=sys.stderr,
            )

    total_fte = sum(p.get("fte", 1.0) for p in people if not p.get("id", "").startswith("_"))
    person_days = len(business_days) * total_fte
    person_hours = person_days * 8  # 8 hours per business day

    return {
        "period": period,
        "business_days": len(business_days),
        "people_count": len(people),
        "total_fte": round(total_fte, 2),
        "person_days": round(person_days, 1),
        "person_hours": round(person_hours, 1),
        "working_calendar": "business-days-only",  # FD-089/PFD-018
        "note": "Public holidays not yet integrated (implement per FD-089 in Phase 1)",
    }


def main():
    p = argparse.ArgumentParser(description="L4 Capacity Model (FD-089/FD-090)")
    p.add_argument("--period", required=True, help="Period YYYY-MM")
    p.add_argument("--output", choices=["json", "text"], default="text")
    args = p.parse_args()

    result = compute_capacity(args.period)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"=== L4 Capacity Model: {result['period']} ===")
        print(f"Business days:  {result['business_days']}")
        print(f"People:         {result['people_count']} ({result['total_fte']} FTE)")
        print(f"Person-days:    {result['person_days']}")
        print(f"Person-hours:   {result['person_hours']}")
        print(f"Calendar:       {result['working_calendar']}")
        if result.get("note"):
            print(f"Note: {result['note']}")


if __name__ == "__main__":
    main()
