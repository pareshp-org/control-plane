# metrics/attention/lib/sessions.py
# DR-1 activity session, DR-2 idle gap, DR-3 session duration, DR-4 granularity.
# MasterSpec v4.0 Section 97.4 lines 8969, 8971, 8972.
# Every threshold arrives through load_calibration(); calibration.yaml is the only authority.
import datetime
import math
from config import load_calibration, value


def parse_ts(raw):
    text = str(raw).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.datetime.fromisoformat(text)
    except ValueError:
        raise SystemExit("ATTN ERROR unparseable-timestamp:%s" % raw)


def normalise_events(window):
    """An event is a bare timestamp (product from the window) or {at: ..., product: ...}."""
    default_product = window.get("product")
    out = []
    for ev in window.get("events") or []:
        if isinstance(ev, dict):
            out.append((parse_ts(ev["at"]), ev.get("product", default_product)))
        else:
            out.append((parse_ts(ev), default_product))
    bounds = window.get("bounds")
    if bounds:
        # Section 97.4 line 8969: the interval bounds the SEARCH, never the duration.
        low, high = parse_ts(bounds[0]), parse_ts(bounds[1])
        out = [e for e in out if low <= e[0] <= high]
    out.sort(key=lambda e: e[0])
    return out


def sessionise(events, cal=None):
    """DR-1 and DR-2. A gap EQUAL to the idle gap continues the session; a wider gap ends it."""
    cal = cal or load_calibration()
    gap = datetime.timedelta(minutes=value(cal, "idle_gap_minutes"))
    sessions = []
    for ev in events:
        if sessions and (ev[0] - sessions[-1][-1][0]) <= gap:
            sessions[-1].append(ev)
        else:
            sessions.append([ev])
    return sessions


def round_units(span_hours, cal=None):
    """DR-4. Round half AWAY FROM ZERO - Python's round() is half-to-even and is wrong here."""
    cal = cal or load_calibration()
    grain = value(cal, "granularity_hours")
    units = int(math.floor(abs(float(span_hours)) / grain + 0.5))
    if value(cal, "granularity_never_zero") and units < 1:
        units = 1
    return round(units * grain, 10)


def session_hours(session, cal=None):
    """DR-3 then DR-4. A single-event session has span zero and becomes one grain."""
    span = (session[-1][0] - session[0][0]).total_seconds() / 3600.0
    return round_units(span, cal)
