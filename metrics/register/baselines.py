#!/usr/bin/env python3
"""metrics/register/baselines.py

AT-046 (L4-P7-04): validates metrics/register/baselines.yaml against
metric-declarations.yaml. Every declared measure must have a matching
baselines.yaml row that carries EXACTLY ONE of:
  - baseline: <recorded value>          (a real captured measurement), or
  - unbaselined: true                   (D77: an empty store renders this,
                                          never a synthetic 0 or a miss)
never both, never neither. A row labelled with a pre-Phase-1 estimate
(pre_phase_1_estimate: true) must carry `baseline`, never `unbaselined` -
an estimate IS the recorded baseline, not an admission of no data.

This deliberately does not hard-code any fixed "minimum baseline set":
lanes/L4-98-DEEP-REVIEW.md item B33/11 already found an earlier five-member
"§103.14 minimum baseline set" elsewhere in this lane's own documents to be
fabricated (the cited spec paragraph names no measure ids). Do not
reintroduce that fabrication here.

Usage: baselines.py <baselines.yaml> [<metric-declarations.yaml>]
Exit 0 and print nothing extra on success (the caller prints AT-046 OK);
exit 1 with one BASELINE FAIL line per problem on failure.
"""
import os
import sys

import yaml


def main(argv):
    if not argv:
        print("usage: baselines.py <baselines.yaml> [<metric-declarations.yaml>]")
        return 2
    baselines_path = argv[0]
    decl_path = argv[1] if len(argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(baselines_path)), "metric-declarations.yaml"
    )

    try:
        bdoc = yaml.safe_load(open(baselines_path, encoding="utf-8")) or {}
    except Exception as exc:
        print("BASELINE FAIL: baselines.yaml unreadable: %s" % exc)
        return 1
    rows = bdoc.get("baselines") or []

    errs = []
    seen = set()
    for row in rows:
        mid = row.get("measure_id", "<unnamed>")
        if mid in seen:
            errs.append("duplicate measure_id %s" % mid)
        seen.add(mid)
        has_baseline = "baseline" in row and row["baseline"] not in (None, "")
        is_unbaselined = row.get("unbaselined") is True
        if has_baseline and is_unbaselined:
            errs.append("measure %s carries both baseline and unbaselined" % mid)
        elif not has_baseline and not is_unbaselined:
            errs.append("measure %s carries neither baseline nor unbaselined" % mid)
        if row.get("pre_phase_1_estimate") is True and not has_baseline:
            errs.append(
                "measure %s is marked pre_phase_1_estimate but carries no baseline value" % mid
            )

    if os.path.exists(decl_path):
        try:
            ddoc = yaml.safe_load(open(decl_path, encoding="utf-8")) or {}
            declared_ids = {m.get("id") for m in (ddoc.get("metrics") or [])}
        except Exception as exc:
            print("BASELINE FAIL: metric-declarations.yaml unreadable: %s" % exc)
            return 1
        missing = declared_ids - seen
        for mid in sorted(m for m in missing if m):
            errs.append("declared measure %s has no baselines.yaml row" % mid)

    if errs:
        for e in errs:
            print("BASELINE FAIL: %s" % e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
