# metrics/attention/lib/config.py
# The ONLY reader of calibration.yaml, taxonomy.yaml and sources.yaml in this phase.
# No other module opens them, and no module holds a threshold as a literal (D102, line 10195).
# There is deliberately no __init__.py: callers put this directory on sys.path.
import os
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _load(name):
    path = os.path.join(ROOT, name)
    if not os.path.exists(path):
        raise SystemExit("ATTN ERROR missing-config:%s" % name)
    with open(path, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    if not doc:
        raise SystemExit("ATTN ERROR empty-config:%s" % name)
    return doc


def load_calibration():
    return _load("calibration.yaml")


def load_taxonomy():
    return _load("taxonomy.yaml")


def load_sources():
    return _load("sources.yaml")


def value(cal, key):
    if key not in cal or "value" not in cal[key]:
        raise SystemExit("ATTN ERROR unknown-calibration-key:%s" % key)
    return cal[key]["value"]
