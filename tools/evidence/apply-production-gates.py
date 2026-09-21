#!/usr/bin/env python3
"""Idempotently wire the Phase 3 production gates into a workflow template.

Spec: Section 27.2 (2567-2576), 37.3 (3261-3268), 39.5 (3589-3596), 33.4 (2911).
Decisions D52, D73, D87, D91.

STOP RULE S8: this tool is the ONLY sanctioned way to modify a workflow template
authored by another phase. A hand edit that reorders or drops a key is
undetectable and is exactly the failure Section 53.1's template comparison
cannot see.

Mechanism: anchor-delimited region replacement, then a structural re-parse.
  # >>> RUNNER-TIER-ASSERT v1 ... # <<< RUNNER-TIER-ASSERT v1
  # >>> PRODUCTION-GATE-CHAIN v1 ... # <<< PRODUCTION-GATE-CHAIN v1

Running twice produces a byte-identical file. Comments outside the regions are
never touched, because the document is never round-tripped through a dumper.

Exit codes: 0 wrote or already current; 1 refused (fail closed).
"""
import argparse
import os
import sys

try:
    import yaml
except ImportError:
    print("APPLY_GATES_PYYAML_ABSENT")
    sys.exit(1)

FRAGMENT_PATH = "templates/workflows/runner-tier-assert.step.yml"
STEP_ANCHOR = "RUNNER-TIER-ASSERT v1"
CHAIN_ANCHOR = "PRODUCTION-GATE-CHAIN v1"


def fail(token, detail=""):
    print(("%s %s" % (token, detail)).strip())
    sys.exit(1)


def read(path):
    try:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            return fh.read()
    except OSError:
        fail("APPLY_GATES_FILE_UNREADABLE", path)


def find_region(lines, anchor, path):
    """Return (open_index, close_index, indent) for one anchor pair."""
    opens = [i for i, ln in enumerate(lines) if (">>> " + anchor) in ln]
    closes = [i for i, ln in enumerate(lines) if ("<<< " + anchor) in ln]
    if len(opens) != 1 or len(closes) != 1:
        fail("GATE_ANCHOR_ABSENT", "%s %s" % (path, anchor))
    if closes[0] < opens[0]:
        fail("GATE_ANCHOR_INVERTED", "%s %s" % (path, anchor))
    indent = len(lines[opens[0]]) - len(lines[opens[0]].lstrip())
    return opens[0], closes[0], indent


def load_fragment(indent):
    """The canonical RUNNER-TIER-ASSERT v1 step, re-indented, comments kept."""
    raw = read(FRAGMENT_PATH)
    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError:
        fail("APPLY_GATES_FRAGMENT_UNPARSEABLE", FRAGMENT_PATH)
    if not isinstance(doc, list) or len(doc) != 1 or not isinstance(doc[0], dict):
        fail("APPLY_GATES_FRAGMENT_MALFORMED", FRAGMENT_PATH)
    if doc[0].get("name") != STEP_ANCHOR:
        fail("APPLY_GATES_FRAGMENT_MALFORMED", FRAGMENT_PATH)
    body = []
    for ln in raw.splitlines():
        if ln.startswith("#"):
            continue          # the fragment file's own header, not part of the step
        body.append((" " * indent + ln) if ln.strip() else "")
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    return body


def replace_region(lines, open_i, close_i, body):
    return lines[: open_i + 1] + body + lines[close_i:]


def apply_file(path, chain_body):
    original = read(path)
    lines = original.splitlines()

    o, c, indent = find_region(lines, STEP_ANCHOR, path)
    lines = replace_region(lines, o, c, load_fragment(indent))

    if chain_body is not None:
        o, c, indent = find_region(lines, CHAIN_ANCHOR, path)
        body = [(" " * indent + ln) if ln.strip() else "" for ln in chain_body]
        lines = replace_region(lines, o, c, body)

    out = "\n".join(lines) + "\n"

    # YAML-AWARE: never write a file that does not parse.
    try:
        doc = yaml.safe_load(out)
    except yaml.YAMLError as exc:
        fail("APPLY_GATES_RESULT_UNPARSEABLE", "%s %s" % (path, exc.__class__.__name__))
    if not isinstance(doc, dict) or "jobs" not in doc:
        fail("APPLY_GATES_RESULT_MALFORMED", path)

    # Section 33.2 line 2860: no `if:` and no path filter may be introduced.
    for ln in lines:
        s = ln.strip()
        if s.startswith("if:") or s.startswith("paths:") or s.startswith("paths-ignore:"):
            fail("APPLY_GATES_SKIP_INTRODUCED", path)

    if out == original:
        print("APPLY_GATES_UNCHANGED %s" % path)
        return False
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)
    print("APPLY_GATES_WROTE %s" % path)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("templates", nargs="+", help="template files to wire")
    ap.add_argument("--chain-body", default=None,
                    help="file holding the gate-chain job block; omit to leave that region as-is")
    args = ap.parse_args()

    if not os.path.isfile(FRAGMENT_PATH):
        fail("APPLY_GATES_FRAGMENT_ABSENT", FRAGMENT_PATH)

    chain_body = None
    if args.chain_body:
        chain_body = read(args.chain_body).splitlines()

    for path in args.templates:
        if not os.path.isfile(path):
            fail("APPLY_GATES_FILE_UNREADABLE", path)
        apply_file(path, chain_body)

    print("APPLY_GATES_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
