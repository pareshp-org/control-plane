#!/usr/bin/env python3
"""metrics/compute/weekend_residual.py (L4-P7-19)

The undeclared-weekend-activation RESIDUAL: state-changing events in the
event log that fall outside the company's declared working calendar
(records/leave/, the calendar-shape record: operating_timezone,
working_days, core_hours_start/end), MINUS activations already declared
through a weekend_exception_state_changed event whose state is
"authorised" (Master Spec v4.0 event taxonomy n=86; the exception
registry this measure reads against). Master Spec v4.0 §103.3 line 9812.

Reports at TEAM level only - a per-actor breakdown would name a person,
which this measure is explicitly forbidden from doing. The result is one
aggregate count, never a per-actor list.

Usage: weekend_residual.py --store <events path> --calendar <records/leave calendar record path> --json
"""
import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import emit, fail, load_yaml, parse_ts, read_store, unbaselined  # noqa: E402

STATE_CHANGING_TYPES_EXCLUDED = {
    "weekend_exception_state_changed",  # the declaration mechanism itself, never residual
}


def is_out_of_hours(occurred, calendar):
    weekday_name = occurred.strftime("%A")
    working_days = set(calendar.get("working_days") or [])
    if weekday_name not in working_days:
        return True
    start = calendar.get("core_hours_start")
    end = calendar.get("core_hours_end")
    if start and end:
        hhmm = occurred.strftime("%H:%M")
        if not (start <= hhmm <= end):
            return True
    return False


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--store", required=True)
    p.add_argument("--calendar", required=True)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        rows = read_store(args.store)
    except FileNotFoundError:
        fail(args.store, "store-absent")
        return 1
    if not os.path.isfile(args.calendar):
        fail(args.calendar, "calendar-record-absent")
        return 1
    calendar = load_yaml(args.calendar)
    if not isinstance(calendar, dict) or not calendar.get("working_days"):
        fail(args.calendar, "calendar-record-malformed")
        return 1

    authorised_keys = set()
    for _p, doc in rows:
        if not isinstance(doc, dict):
            continue
        if doc.get("event_type") == "weekend_exception_state_changed":
            payload = doc.get("payload") or {}
            if payload.get("state") == "authorised":
                actor = doc.get("actor")
                occurred = parse_ts(doc.get("occurred_at"))
                if actor and occurred:
                    authorised_keys.add((actor, occurred.date()))

    out_of_hours_count = 0
    declared_count = 0
    for _p, doc in rows:
        if not isinstance(doc, dict):
            continue
        if doc.get("event_type") in STATE_CHANGING_TYPES_EXCLUDED:
            continue
        occurred = parse_ts(doc.get("occurred_at"))
        if not occurred:
            continue
        if not is_out_of_hours(occurred, calendar):
            continue
        out_of_hours_count += 1
        actor = doc.get("actor")
        if actor and (actor, occurred.date()) in authorised_keys:
            declared_count += 1

    residual = out_of_hours_count - declared_count

    if not rows:
        emit(unbaselined(args.store, "weekend_residual_measures"))
        return 0

    emit({
        "store": args.store,
        "measure": "weekend_residual_measures",
        "scope": "team",
        "out_of_hours_events": out_of_hours_count,
        "declared_exceptions": declared_count,
        "residual": residual,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
