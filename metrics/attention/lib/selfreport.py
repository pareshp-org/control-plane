# metrics/attention/lib/selfreport.py
# The weekly banded self-report. MasterSpec v4.0 Section 97.4 line 8980.
# "one band per category, unattributed to any product"; apportioned by machine-derived share;
# "to the portfolio where no share exists"; the self-reported provenance label is permanent.
# The ritual flag is NEVER self-reported (Section 67.2 line 5592) - a self-report carrying it
# is rejected, not cleaned. The cap and the band table come through load_calibration().
from config import load_calibration, value

PORTFOLIO = "portfolio"


def apportion(doc, cal=None):
    cal = cal or load_calibration()
    if value(cal, "self_report_per_product_attribution"):
        raise SystemExit("ATTN ERROR per-product-self-report-enabled")
    shares = doc.get("machine_activity_shares") or {}
    out = []
    for entry in doc.get("self_reports") or []:
        if "ritual" in entry:
            # Section 67.2 line 5592: set by the workflow that opens the ritual, never self-reported.
            raise SystemExit("ATTN ERROR ritual-self-reported:%s" % entry.get("person"))
        if entry.get("product") not in (None, "", PORTFOLIO):
            raise SystemExit("ATTN ERROR self-report-carries-product:%s" % entry.get("person"))
        person = entry["person"]
        hours = float(entry["hours"])
        mine = shares.get(person) or {}
        if not mine:
            out.append({"person": person, "product": PORTFOLIO, "category": entry["category"],
                        "hours": round(hours, 10), "provenance": "self-reported"})
            continue
        for product, share in mine.items():
            out.append({"person": person, "product": product, "category": entry["category"],
                        "hours": round(hours * float(share), 10), "provenance": "self-reported"})
    return out
