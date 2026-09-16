# metrics/attention/lib/attribute.py
# DR-6 product attribution. MasterSpec v4.0 Section 97.4 line 8974.
# rounding_order arrives through load_calibration() and carries decided: D-L4-P7-03 (round-then-split).
# This module implements exactly the declared value and refuses any other; it never chooses.
from config import load_calibration, value

PORTFOLIO = "portfolio"


def split(session, hours, cal=None):
    """Returns {product: hours}. A session touching no product goes to the portfolio."""
    cal = cal or load_calibration()
    if value(cal, "rounding_order") != "round_then_split":
        raise SystemExit("ATTN ERROR unsupported-rounding-order:%s"
                         % value(cal, "rounding_order"))
    named = [product for _, product in session if product]
    if not named:
        return {PORTFOLIO: round(float(hours), 10)}
    counts = {}
    for product in named:
        counts[product] = counts.get(product, 0) + 1
    total = float(len(named))
    return {p: round(float(hours) * counts[p] / total, 10) for p in counts}
