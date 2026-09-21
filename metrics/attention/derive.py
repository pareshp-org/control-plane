#!/usr/bin/env python3
# metrics/attention/derive.py
# THE ATTENTION LEDGER. MasterSpec v4.0 Section 97.4 lines 8955-8981.
# Command line and JSON shape fixed by L4-07-tests-and-runbook.md tasks L4-P7-T09 and L4-P7-T12:
#   derive.py --input <f.yaml> [--input <f.yaml> ...] [--query-product <p>] [--json]
# Every threshold arrives from calibration.yaml through load_calibration(); this file holds none.
import json
import os
import sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
from config import load_calibration  # noqa: E402
import sessions as S                 # noqa: E402
import precedence as P               # noqa: E402
import attribute as A                # noqa: E402
import reconcile as R                # noqa: E402
import selfreport as SR              # noqa: E402

EPS = 1e-9


def q(number):
    return round(float(number), 10)


def derive_windows(doc, cal):
    """DR-1..DR-6. Returns (output, hours) where hours is {category: {product: h}}."""
    pairs = []
    for window in doc.get("windows") or []:
        if "category" not in window:
            raise SystemExit("ATTN ERROR window-without-category")
        for session in S.sessionise(S.normalise_events(window), cal):
            pairs.append((window["category"], session))
    winners, losers = P.resolve(pairs, cal)
    hours = {}
    for category, session in winners:
        earned = S.session_hours(session, cal)
        for product, part in A.split(session, earned, cal).items():
            hours.setdefault(category, {})
            hours[category][product] = q(hours[category].get(product, 0.0) + part)
    for category, session in losers:
        # Section 97.4 line 8973: the losing categories receive nothing - recorded, not omitted.
        for product in A.split(session, 0.0, cal):
            hours.setdefault(category, {})
            hours[category].setdefault(product, 0.0)
    defect = False
    cap = doc.get("scheduled_availability_hours")
    if cap is not None:
        total = q(sum(sum(v.values()) for v in hours.values()))
        defect = total > float(cap) + EPS          # Section 97.4 line 8976, pre-truncation
    out = {"case": doc.get("case"), "sessions": len(winners), "hours": hours,
           "truncations": 0, "instrument_defect": bool(defect)}
    return out, hours


def derive_day(doc, cal):
    """DR-7 plus the instrument-defect rule. Section 97.4 lines 8975 and 8976."""
    if "scheduled_availability_hours" not in doc:
        raise SystemExit("ATTN ERROR day-close-without-cap")
    pre = {k: float(v) for k, v in (doc.get("pre_truncation_hours") or {}).items()}
    post, detail, defect = R.reconcile(pre, doc["scheduled_availability_hours"], cal)
    flags = R.eligibility(defect)
    out = {"case": doc.get("case"),
           "total_hours": q(sum(post.values())),
           "hours_by_category": {k: q(v) for k, v in post.items()},
           "truncations": len(detail)}
    if detail:
        out["truncation_detail"] = detail
    out["instrument_defect"] = bool(defect)
    out["capacity_profile_eligible"] = flags["capacity_profile_eligible"]
    if defect:
        out["workload_state_eligible"] = flags["workload_state_eligible"]
        out["founder_view_eligible"] = flags["founder_view_eligible"]
    return out


def main(argv):
    inputs, query, as_json = [], None, False
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--input":
            i += 1
            if i >= len(argv):
                print("ATTN ERROR missing-value-for:--input", file=sys.stderr)
                return 2
            inputs.append(argv[i])
        elif arg == "--query-product":
            i += 1
            if i >= len(argv):
                print("ATTN ERROR missing-value-for:--query-product", file=sys.stderr)
                return 2
            query = argv[i]
        elif arg == "--json":
            as_json = True
        else:
            print("ATTN ERROR unknown-argument:%s" % arg, file=sys.stderr)
            return 2
        i += 1
    if not inputs:
        print("ATTN ERROR no-input", file=sys.stderr)
        return 2
    cal = load_calibration()
    results, per_product = [], {}
    for path in inputs:
        if not os.path.exists(path):
            print("ATTN ERROR missing-input:%s" % path, file=sys.stderr)
            return 3
        with open(path, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
        if "self_reports" in doc:
            results.append({"case": doc.get("case"), "apportioned": SR.apportion(doc, cal)})
        elif "pre_truncation_hours" in doc:
            results.append(derive_day(doc, cal))
        elif "windows" in doc:
            out, hours = derive_windows(doc, cal)
            results.append(out)
            for product_map in hours.values():
                for product, value_ in product_map.items():
                    per_product[product] = q(per_product.get(product, 0.0) + value_)
        else:
            print("ATTN ERROR unrecognised-input-shape:%s" % path, file=sys.stderr)
            return 3
    if query is not None:
        payload = {"product": query, "hours": q(per_product.get(query, 0.0))}
    elif len(results) == 1:
        payload = results[0]
    else:
        payload = {"results": results}
    if as_json:
        print(json.dumps(payload))
    else:
        print("ATTENTION OK inputs=%d" % len(inputs))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
