#!/usr/bin/env python3
"""people-intelligence non-delegability checker (D109, AT-091).

Invariant 106 (spec Section 101 #106): "Individual people-performance
intelligence on the management surface (Layer B-M) is Founder-only, gated by
the `people-intelligence` capability, and not delegable; the individual
self-view (Layer B-S) carries one person's own evidence to that person and
is outside this rule."

This gate checks three things, every one of them read-only over already
committed Lane 5 declarations -- it grants nothing and holds no credential:

  1. capability-founder-only   access/model/permission-matrix.yaml's
                                machine_identity_row is absolute (reuses
                                L5-T13's leg-1 logic: a non-delegable
                                capability that a machine identity could
                                hold would not be non-delegable).
  2. not-delegable             no Lane 5 YAML declares a delegate, an
                                assignment_type, or any other assignment
                                mechanism for `people-intelligence`.
                                Non-delegable means exactly zero such
                                declarations exist, not that they exist and
                                are denied.
  3. self-view-carve-out       Layer B-S (the self-view) is declared as
                                outside this rule, i.e. no self-view
                                declaration requires the capability to view
                                one's own evidence (AT-090's other half).

A fourth, independent mode is the request-time evaluator: `--request <yaml>`
takes a single concrete request -- an assignment record being validated, or
an access attempt being made -- and answers "does THIS request pass the
gate", per §90.4 / D109 / AT-090 / AT-091:

  kind: assignment    a record naming grants_capability: people-intelligence
                       always fails (D109: no assignment type grants it).
  kind: access         {viewer, target, dataset: self-view|peer-data|
                       conduct-record, holder: true|false} --
                         - dataset conduct-record always fails, holder or
                           not (§90.4/§88: holding the capability never
                           grants conduct-record access);
                         - dataset self-view with viewer == target passes
                           regardless of holder (AT-090's self-view
                           carve-out, invariant 106);
                         - any other viewer/target pair requires holder:
                           true, else it fails (the peer block).

On failure this prints `PI GATE FAIL: <reason>` and exits 1. This mode holds
no credential and grants nothing; it evaluates the request object it is
handed, which the caller is responsible for sourcing honestly (this gate
never models the people registry itself -- see the L5-T14 STOP condition).

Usage:  check_people_intelligence_gate.py [--selftest | --request <yaml>]
Exit 0 PASS, 1 FAIL, 2 fail-closed (inputs unreadable).
"""
import glob
import os
import re
import sys

import yaml

MATRIX_PATH = "access/model/permission-matrix.yaml"
SCAN_GLOB = os.path.join("access", "**", "*.yaml")
DELEGATION_MARKERS = re.compile(r"delegat|assignment_type", re.IGNORECASE)
# A line naming the capability next to a delegation word is only a finding if
# it asserts delegation exists. The same line prohibiting, removing or
# denying delegation ("is not delegable", "is removed", "prohibited", "never
# delegable") is the compliant statement invariant 106 requires, and must not
# be mistaken for the breach it describes.
NEGATION_MARKERS = re.compile(
    r"not[\s_-]*delegab|non[\s_-]*delegab|is\s+removed|prohibit|never|"
    r"no\s+delegat|must\s+not|outside\s+this\s+rule",
    re.IGNORECASE)
CAPABILITY_NAME = "people-intelligence"
CAPABILITY_KEY = "people_intelligence"


def load_yaml(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except (OSError, yaml.YAMLError):
        return None


def check_capability_founder_only():
    matrix = load_yaml(MATRIX_PATH)
    if matrix is None:
        return (["matrix-unreadable %s" % MATRIX_PATH], True)
    mi = (matrix or {}).get("machine_identity_row")
    if not isinstance(mi, dict) or mi.get("absolute") is not True:
        return (["machine_identity_row is not declared absolute in %s" % MATRIX_PATH], False)
    return ([], False)


def scan_for_delegation(paths):
    """A real defect looks like a line naming the capability alongside a
    delegation marker in the *same file* (a grep -rn on the two independently
    would false-positive on any file that discusses both topics separately,
    e.g. this checker's own docstring). Line-scoped co-occurrence is the
    honest signal."""
    findings = []
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                lines = handle.readlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, start=1):
            lower = line.lower()
            if CAPABILITY_NAME in lower or CAPABILITY_KEY in lower:
                if DELEGATION_MARKERS.search(line) and not NEGATION_MARKERS.search(line):
                    findings.append(
                        "%s:%d names %s alongside a delegation marker: %s"
                        % (path, lineno, CAPABILITY_NAME, line.strip()[:160]))
    return findings


def check_not_delegable():
    paths = [p for p in glob.glob(SCAN_GLOB, recursive=True)
             if os.path.abspath(p) != os.path.abspath(__file__)]
    return scan_for_delegation(paths)


def check_self_view_carve_out():
    """AT-090's self-view leg: a self-view declaration must not itself
    require the people-intelligence capability to view one's own evidence.
    Absence of any Layer B declaration at all is reported as INDETERMINATE
    upstream (by whichever check owns Layer B provisioning, e.g. L5-03's
    AT-095); this gate only refuses a self-view declaration that gets the
    carve-out backwards."""
    findings = []
    for path in glob.glob(os.path.join("access", "layer-b", "*.yaml")):
        doc = load_yaml(path)
        if not isinstance(doc, dict):
            continue
        text = yaml.safe_dump(doc).lower()
        if "self" in text and ("selfview" in text.replace("-", "").replace("_", "")
                                or "self_view" in text or "self-view" in text):
            if "requires_capability: people_intelligence" in text.replace("-", "_"):
                findings.append(
                    "%s requires people_intelligence for the self-view, "
                    "breaking the AT-090 carve-out" % path)
    return findings


CONDUCT_DATASET = "conduct-record"
SELF_VIEW_DATASET = "self-view"


def evaluate_request(doc, source):
    """Evaluate a single concrete request against §90.4 / D109 / AT-090 /
    AT-091. Returns a list of `PI GATE FAIL: <reason>` strings -- empty
    means the request passes. `doc` is the parsed request object; `source`
    is only used for error messages."""
    if not isinstance(doc, dict):
        return ["PI GATE FAIL: fail-closed: %s does not contain a mapping" % source]

    kind = str(doc.get("kind", "")).strip().lower()

    if kind == "assignment":
        granted = doc.get("grants_capability")
        if isinstance(granted, list):
            names = [str(g).strip().lower() for g in granted]
        elif granted is None:
            names = []
        else:
            names = [str(granted).strip().lower()]
        if CAPABILITY_NAME in names or CAPABILITY_KEY in names:
            return ["PI GATE FAIL: assignment '%s' grants people-intelligence, which is "
                    "not delegable (D109, invariant 106, AT-090)"
                    % doc.get("assignment_type", "<unnamed>")]
        return []

    if kind == "access":
        viewer = doc.get("viewer")
        target = doc.get("target")
        dataset = str(doc.get("dataset", "")).strip().lower()
        holder = bool(doc.get("holder", False))

        if not viewer or not target or not dataset:
            return ["PI GATE FAIL: fail-closed: access request in %s is missing "
                    "viewer, target or dataset" % source]

        if dataset == CONDUCT_DATASET:
            # Section 90.4/88: holding people-intelligence never grants
            # conduct-record access, holder or not.
            return ["PI GATE FAIL: %s requested conduct-record access for %s; "
                    "people-intelligence never grants conduct-record access "
                    "(Section 90.4, Section 88)" % (viewer, target)]

        if dataset == SELF_VIEW_DATASET and viewer == target:
            # AT-090's self-view carve-out (invariant 106): a person's own
            # Layer B-S self-view passes without holding the capability.
            return []

        if not holder:
            # The peer block: any non-self, non-conduct Layer B data
            # requires the people-intelligence capability.
            return ["PI GATE FAIL: %s is not a people-intelligence holder and "
                    "requested %s's Layer B data (%s)" % (viewer, target, dataset)]

        return []

    return ["PI GATE FAIL: fail-closed: %s has unrecognised kind %r "
            "(expected 'assignment' or 'access')" % (source, doc.get("kind"))]


def run_request(path):
    if not path or not os.path.isfile(path):
        print("PI GATE FAIL: fail-closed: --request path missing or unreadable: %s" % path)
        return 1
    doc = load_yaml(path)
    if doc is None:
        print("PI GATE FAIL: fail-closed: --request file unreadable or unparseable: %s" % path)
        return 1
    findings = evaluate_request(doc, path)
    for f in findings:
        print(f)
    if findings:
        return 1
    print("RESULT PASS (request permitted under Section 90.4 / D109 / invariant 106)")
    return 0


def selftest():
    findings, fail_closed = check_capability_founder_only()
    if findings or fail_closed:
        print("SELFTEST FAIL: capability-founder-only leg fails against the committed tree:")
        for f in findings:
            print("  - %s" % f)
        return 1

    live_delegation = check_not_delegable()
    if live_delegation:
        print("SELFTEST FAIL: a live delegation declaration exists in the committed tree:")
        for f in live_delegation:
            print("  - %s" % f)
        return 1

    live_selfview = check_self_view_carve_out()
    if live_selfview:
        print("SELFTEST FAIL: the self-view carve-out is broken in the committed tree:")
        for f in live_selfview:
            print("  - %s" % f)
        return 1

    # Negative fixture: prove the delegation scanner actually catches a
    # co-occurrence, using a throwaway file so the real tree is untouched.
    fixture_dir = os.path.join("access", "tests", "fixtures")
    os.makedirs(fixture_dir, exist_ok=True)
    fixture_path = os.path.join(fixture_dir, "at-091-delegation-fixture.yaml")
    with open(fixture_path, "w", encoding="utf-8") as handle:
        handle.write("capability: people-intelligence  delegate: some-team-lead"
                      "   # this line must be caught\n")
    try:
        caught = scan_for_delegation([fixture_path])
    finally:
        os.remove(fixture_path)
    if not caught:
        print("SELFTEST FAIL: a synthetic people-intelligence/delegate co-occurrence "
              "was not caught")
        return 1

    print("L5-T14 SELF-VERIFY PASS")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()

    if "--request" in argv:
        idx = argv.index("--request")
        request_path = argv[idx + 1] if idx + 1 < len(argv) else None
        return run_request(request_path)

    findings, fail_closed = check_capability_founder_only()
    findings += check_not_delegable()
    findings += check_self_view_carve_out()

    for f in findings:
        print("FINDING %s" % f)
    if findings:
        print("RESULT FAIL")
        print("CLASS invariant-106-breach")
        print("AUTHORITY Section 101 invariant 106; D109")
        return 2 if fail_closed else 1
    print("RESULT PASS (people-intelligence remains founder-only and non-delegable)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
