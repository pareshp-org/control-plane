# metrics/attention/lib/reconcile.py
# DR-7 daily reconciliation, and the instrument-defect rule.
# MasterSpec v4.0 Section 97.4 lines 8975 and 8976. Section 83.1 line 7280; Section 93.
# The truncation order arrives through load_calibration(); it is never written here.
from config import load_calibration, value

EPS = 1e-9


def reconcile(hours_by_category, cap, cal=None):
    """Returns (post_hours, truncation_detail, instrument_defect).

    instrument_defect is decided on the PRE-truncation total, per line 8976.
    """
    cal = cal or load_calibration()
    if value(cal, "truncation_order") != "reverse_precedence":
        raise SystemExit("ATTN ERROR unsupported-truncation-order:%s"
                         % value(cal, "truncation_order"))
    sequence = cal["truncation_order"]["expanded"]
    order = value(cal, "precedence_order")
    if sequence != list(reversed(order)):
        raise SystemExit("ATTN ERROR truncation-order-not-reverse-precedence")
    post = {k: round(float(v), 10) for k, v in hours_by_category.items()}
    pre_total = round(sum(post.values()), 10)
    cap = round(float(cap), 10)
    defect = pre_total > cap + EPS
    excess = round(pre_total - cap, 10)
    detail = []
    for category in sequence:
        if excess <= EPS:
            break
        have = post.get(category, 0.0)
        if have <= EPS:
            continue
        take = round(have if have < excess else excess, 10)
        post[category] = round(have - take, 10)
        detail.append({"category": category, "hours_removed": take})
        excess = round(excess - take, 10)
    return post, detail, defect


def eligibility(instrument_defect):
    """Section 97.4 line 8976: a defect day enters none of the three surfaces."""
    ok = not instrument_defect
    return {"capacity_profile_eligible": ok,
            "workload_state_eligible": ok,
            "founder_view_eligible": ok}
