#!/usr/bin/env python3
# metrics/attention/scheduled-availability.py
# The daily cap's input. MasterSpec v4.0 Section 97.4 line 8975 -> Section 69.2 line 5720
# -> Section 7.3 work_arrangement (D111, line 10209).
# The resolution order R1-R7 is fixed by L4-04-attention-ledger.md section 3.5. Never a default
# number: an input that cannot be read is SCHEDAVAIL ERROR exit 3, never zero and never a guess.
# fte_application is read through load_calibration(); D-L4-P4-01 is open and this file does not
# decide it. No calibration.yaml threshold is written as a literal here.
import datetime, json, os, sys, yaml
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
from config import load_calibration, value  # noqa: E402

WEEKDAY = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def fail(reason):
    print("SCHEDAVAIL ERROR %s" % reason)
    sys.exit(3)


def load(path, what):
    if not os.path.exists(path):
        fail("no-%s:%s" % (what, path))
    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:
        fail("unparseable-%s:%s" % (what, path))


def minutes(hhmm):
    try:
        hours, mins = str(hhmm).split(":")
        return int(hours) * 60 + int(mins)
    except Exception:
        fail("unparseable-time:%s" % hhmm)


def main(argv):
    args = {}
    i = 0
    while i < len(argv):
        if not argv[i].startswith("--"):
            fail("unknown-argument:%s" % argv[i])
        key = argv[i][2:]
        if key == "json":
            args["json"] = True
            i += 1
            continue
        i += 1
        if i >= len(argv):
            fail("missing-value-for:%s" % key)
        args[key] = argv[i]
        i += 1
    for key in ("person", "date", "people", "calendar", "absence"):
        if key not in args:
            fail("missing-argument:%s" % key)         # R7; --calendar per D-L4-P4-03
    cal = load_calibration()

    # R1 - the person must be in the registry.
    registry = load(args["people"], "people-registry")
    person = None
    for entry in registry.get("people") or []:
        if entry.get("id") == args["person"]:
            person = entry
    if person is None:
        fail("person-not-in-registry")

    # R2 - fail closed where the declared working calendar is absent (Section 7.3, D111).
    wa = person.get("work_arrangement")
    if not wa:
        fail("no-work-arrangement")
    tz = str(wa.get("timezone", ""))
    if not tz or tz[0] in "+-" or tz.upper().startswith("UTC") or "/" not in tz:
        fail("timezone-not-iana:%s" % tz)             # Section 7.3 line 628

    try:
        day_date = datetime.date.fromisoformat(args["date"])
    except ValueError:
        fail("unparseable-date:%s" % args["date"])

    # R3 - a recorded absence covering the date.
    absence = load(args["absence"], "absence-document")
    if absence.get("person") != args["person"]:
        fail("absence-document-person-mismatch")
    if args["date"] in [str(x) for x in (absence.get("dates") or [])]:
        hours, rule = 0.0, "R3-recorded-absence"
    else:
        # R4 - the public-holiday list for this person's declared set.
        calendar = load(args["calendar"], "calendar")
        holiday_sets = calendar.get("public_holiday_sets") or {}
        set_name = wa.get("public_holiday_set")
        if set_name not in holiday_sets:
            fail("unknown-holiday-set:%s" % set_name)
        if args["date"] in [str(x) for x in (holiday_sets[set_name] or [])]:
            hours, rule = 0.0, "R4-public-holiday"
        else:
            # R5 - a weekday absent from the declared schedule is non-working.
            weekday = WEEKDAY[day_date.weekday()]
            schedule = wa.get("schedule") or {}
            if weekday not in schedule:
                hours, rule = 0.0, "R5-non-working-day"    # Section 7.3 line 571
            else:
                # R6 - the declared span, in declared local clock time.
                span = minutes(schedule[weekday].get("end")) - minutes(schedule[weekday].get("start"))
                if span <= 0:
                    fail("schedule-span-nonpositive:%s" % weekday)
                hours = span / 60.0
                applied = value(cal, "fte_application")    # D-L4-P4-01, declared default "none"
                if applied == "multiply":
                    hours = hours * float(wa.get("fte", 1.0))
                elif applied != "none":
                    fail("unsupported-fte-application:%s" % applied)
                rule = "R6-declared-schedule"
    hours = round(hours, 10)
    if args.get("json"):
        print(json.dumps({"person": args["person"], "date": args["date"],
                          "scheduled_availability_hours": hours, "rule": rule,
                          "timezone": tz,
                          "fte_application": value(cal, "fte_application")}, sort_keys=True))
    else:
        print("SCHEDAVAIL OK %s %s %s" % (args["person"], args["date"], hours))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
