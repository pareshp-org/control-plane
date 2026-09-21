#!/usr/bin/env python3
"""Estimate capture at Ready confirmation. Master Spec 29.3 line 2665; D79 line 10162.

Single capture point. Reads the band vocabulary from registries/economics.yaml
(L1-owned, read-only here). Fails closed when it cannot be read.
Never infers the item class; --item-class is required.
"""
import argparse, json, sys, yaml

READY_DEF = "metrics/boards/ready-definition.yaml"
ECONOMICS = "registries/economics.yaml"
CAPTURE_TRANSITION = "ready_confirmation"


def err(reason):
    print("ESTIMATE ERROR %s" % reason)
    sys.exit(3)


def fail(reason):
    print("ESTIMATE FAIL %s" % reason)
    sys.exit(1)


def load_ready():
    try:
        return yaml.safe_load(open(READY_DEF, encoding="utf-8"))["estimate_capture"]
    except Exception:
        err("ready-definition-unreadable")


def load_bands():
    """Band vocabulary lives in registries/economics.yaml - L1's file. Fail closed."""
    try:
        e = yaml.safe_load(open(ECONOMICS, encoding="utf-8"))
    except Exception:
        err("economics-unreachable")
    bands = (e or {}).get("estimate_bands")
    if not bands:
        err("economics-declares-no-estimate-bands")
    out = {}
    for b in bands:
        label, pv = b.get("label"), b.get("point_value_days")
        if not label or pv is None:
            err("band-without-label-or-point-value")
        out[label] = pv
    return out, (e or {}).get("estimate_bands_version")


def capture(args):
    cfg = load_ready()
    if args.transition != CAPTURE_TRANSITION:
        fail("not-the-capture-point:%s" % args.transition)
    if args.item_class is None:
        err("missing-item-class")
    exempt = cfg["estimate_exempt_classes"]
    if args.item_class in exempt:
        print(json.dumps({"captured": False, "reason": "exempt", "item_class": args.item_class}))
        print("ESTIMATE OK exempt=%s" % args.item_class)
        return 0
    if args.item_class != "normal_planned_work":
        err("unknown-item-class:%s" % args.item_class)
    if args.band is None:
        err("missing-band")
    bands, version = load_bands()
    if args.band not in bands:
        fail("band-not-in-economics-vocabulary:%s" % args.band)
    rec = {
        "band": args.band,
        "point_value_days": bands[args.band],
        "band_vocabulary_version": version,
        "captured_at_transition": CAPTURE_TRANSITION,
        "item": args.item,
        "product": args.product,
        "elapsed": None,
        "elapsed_net_blocked": None,
    }
    print(json.dumps(rec, sort_keys=True))
    print("ESTIMATE OK band=%s point=%s" % (args.band, bands[args.band]))
    return 0


def selftest():
    cfg = load_ready()
    if cfg.get("capture_point") != CAPTURE_TRANSITION:
        fail("capture-point-drifted")
    if cfg.get("item_class_inferred") is not False:
        fail("class-inference-permitted")
    if cfg.get("band_vocabulary_home") != ECONOMICS:
        fail("vocabulary-home-drifted")
    if cfg.get("hours_precise") is not False:
        fail("hours-precise-permitted")
    if len(cfg.get("estimate_exempt_classes") or []) != 3:
        fail("exempt-classes-not-three")
    print("BOARDS OK estimate-capture=1 exempt=3")
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--transition")
    p.add_argument("--item-class", dest="item_class")
    p.add_argument("--band")
    p.add_argument("--item")
    p.add_argument("--product")
    a = p.parse_args()
    return selftest() if a.selftest else capture(a)


if __name__ == "__main__":
    sys.exit(main())
