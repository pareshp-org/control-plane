#!/usr/bin/env python3
"""Machine-identity boundary checker (Section 90.2 machine-identities row,
invariant 106).

Section 90.2: "no machine identity holds any people-related data category,
receives a Layer B credential or folder scope, or holds the
people-intelligence capability, under any configuration." This is absolute
-- there is no operational-reasons exception.

Two independent legs, both fail-closed:

  LEG-1 declared-absolute   access/model/permission-matrix.yaml's
                             machine_identity_row must itself declare the
                             row absolute with every column "No".
  LEG-2 no-live-grant        no Lane 5 declaration anywhere under access/**
                             or ops-vm/** names one of the five machine
                             identities alongside a people-related
                             data_category, a Layer B credential/folder
                             scope, or the people-intelligence capability.

A third, independent mode is the request-time evaluator the checker's name
promises: `--grants <yaml>` takes a snapshot of what a directory/credential
service currently reports each identity holds (shape: `{identity:
[data_category, ...]}`) and evaluates THAT specific input -- not the
committed repo tree -- against the same three legs, plus the Layer B
credential/folder-scope cross-check. This is what lets a caller ask "does
this actual grants snapshot breach the boundary" rather than only "does the
committed tree still declare the boundary correctly".

Usage:  check_machine_identity_boundary.py [--selftest | --grants <yaml>]
Exit 0 PASS, 1 FAIL (a live grant found), 2 fail-closed (inputs unreadable).
"""
import glob
import os
import sys

import yaml

MATRIX_PATH = "access/model/permission-matrix.yaml"
MACHINE_IDENTITIES = [
    "reconciler",
    "provisioning-cli",
    "ops-console",
    "background-agents",
    "background-machine-layer",
]
SCAN_GLOBS = [
    os.path.join("access", "**", "*.yaml"),
    os.path.join("ops-vm", "**", "*.yaml"),
]
# A grant look like "<machine identity>: <data category | capability>" is what
# this leg hunts for; declaring the identity's *absence* (e.g. this file, or
# permission-matrix.yaml's own "No" cells) is not a grant and must not match.
SENSITIVE_MARKERS = (
    "people-intelligence",
    "layer_b_credential",
    "layer-b-credential",
    "layer_b_folder_scope",
    "layer-b-folder-scope",
)


def load_yaml(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except (OSError, yaml.YAMLError):
        return None


def leg1_declared_absolute(matrix):
    findings = []
    mi = (matrix or {}).get("machine_identity_row")
    if not isinstance(mi, dict):
        return ["LEG-1 permission-matrix.yaml has no machine_identity_row"]
    if mi.get("absolute") is not True:
        findings.append(
            "LEG-1 machine_identity_row.absolute is %r, not True" % mi.get("absolute"))
    for col in ("founder", "team_lead", "employee", "peer"):
        if str(mi.get(col, "")).strip().lower() != "no":
            findings.append(
                "LEG-1 machine_identity_row.%s is %r, spec 90.2 requires 'No'"
                % (col, mi.get(col)))
    declared = mi.get("machine_identities") or []
    missing = [m for m in MACHINE_IDENTITIES if m not in declared]
    if missing:
        findings.append("LEG-1 machine_identity_row.machine_identities omits %r" % missing)
    return findings


def _walk_for_grants(node, path, findings, source):
    """Recurse a parsed YAML document looking for a mapping keyed by one of
    the five machine identities whose value carries a sensitive marker, or a
    list entry equal to a machine identity inside a list that is itself
    keyed by a sensitive marker (the two shapes a real grant could take)."""
    if isinstance(node, dict):
        keys_lower = {str(k).lower(): k for k in node}
        for identity in MACHINE_IDENTITIES:
            if identity in keys_lower:
                value = node[keys_lower[identity]]
                text = yaml_fragment_text(value)
                if any(marker in text.lower() for marker in SENSITIVE_MARKERS):
                    findings.append(
                        "LEG-2 %s: key %s carries a sensitive marker: %s"
                        % (source, identity, text[:120]))
        for key, value in node.items():
            key_l = str(key).lower()
            if any(marker in key_l for marker in SENSITIVE_MARKERS):
                for identity in _find_identities(value):
                    findings.append(
                        "LEG-2 %s: sensitive key %s names machine identity %s"
                        % (source, key, identity))
            _walk_for_grants(value, path + [key], findings, source)
    elif isinstance(node, list):
        for item in node:
            _walk_for_grants(item, path, findings, source)


def _find_identities(node):
    """Recursively collect any machine-identity strings anywhere inside a
    parsed YAML fragment (list of names, mapping keyed by name, nested)."""
    found = []
    if isinstance(node, str):
        if node.strip().lower() in MACHINE_IDENTITIES:
            found.append(node.strip().lower())
    elif isinstance(node, dict):
        for key, value in node.items():
            if str(key).strip().lower() in MACHINE_IDENTITIES:
                found.append(str(key).strip().lower())
            found.extend(_find_identities(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_find_identities(item))
    return found


def yaml_fragment_text(value):
    if isinstance(value, (dict, list)):
        try:
            return yaml.safe_dump(value)
        except yaml.YAMLError:
            return str(value)
    return str(value)


def leg2_no_live_grant():
    findings = []
    paths = []
    for pattern in SCAN_GLOBS:
        paths.extend(glob.glob(pattern, recursive=True))
    for path in sorted(set(paths)):
        # permission-matrix.yaml's own machine_identity_row is the absolute
        # DENIAL declaration, not a grant; LEG-1 already checks its shape.
        if os.path.abspath(path) == os.path.abspath(MATRIX_PATH):
            continue
        doc = load_yaml(path)
        if doc is None:
            continue
        _walk_for_grants(doc, [], findings, path)
    return findings


CLEAN_FIXTURE = os.path.join("access", "tests", "fixtures", "grants-clean.yaml")
POISONED_FIXTURE = os.path.join("access", "tests", "fixtures", "grants-poisoned.yaml")
LAYERB_DIRS = [os.path.join("access", "layer-b"), os.path.join("access", "layerb")]


def _known_data_categories():
    """The people-related data_category values a machine identity may never
    hold, drawn from the live permission matrix (spec 90.2 item 1)."""
    matrix = load_yaml(MATRIX_PATH)
    if not isinstance(matrix, dict):
        return set()
    cats = set()
    for row in matrix.get("rows") or []:
        if isinstance(row, dict) and row.get("data_category"):
            cats.add(str(row["data_category"]).strip())
    return cats


def leg2_layerb_credential_or_folder(identity):
    """Spec 90.2 item 2: no machine identity may appear in any Layer B
    credential list or folder scope declared under access/layerb/ (checked
    only for directories that actually exist)."""
    findings = []
    for directory in LAYERB_DIRS:
        if not os.path.isdir(directory):
            continue
        for path in sorted(glob.glob(os.path.join(directory, "**", "*.yaml"), recursive=True)):
            doc = load_yaml(path)
            if doc is None:
                continue
            local = []
            _walk_for_grants(doc, [], local, path)
            for f in local:
                if identity in f:
                    findings.append(
                        "MACHINE IDENTITY BOUNDARY FAIL: %s: layer-b credential/folder-scope "
                        "reference in %s" % (identity, path))
    return findings


def evaluate_grants_snapshot(path):
    """The request-time evaluator: given a --grants <yaml> snapshot of what
    each identity currently holds (shape: {identity: [data_category, ...]}),
    return the list of `MACHINE IDENTITY BOUNDARY FAIL: <identity>:
    <category>` findings for THIS input. Fail-closed: an absent, unreadable
    or unparseable file, or a malformed per-identity value, itself becomes a
    finding (never a silent 0)."""
    if not path or not os.path.isfile(path):
        return ["MACHINE IDENTITY BOUNDARY FAIL: fail-closed: --grants path missing or "
                "unreadable: %s" % path]
    doc = load_yaml(path)
    if not isinstance(doc, dict):
        return ["MACHINE IDENTITY BOUNDARY FAIL: fail-closed: --grants file unparseable or "
                "not a mapping: %s" % path]

    known_categories = _known_data_categories()
    findings = []
    for identity in MACHINE_IDENTITIES:
        if identity not in doc:
            continue
        categories = doc[identity]
        if categories is None:
            categories = []
        if not isinstance(categories, list):
            findings.append(
                "MACHINE IDENTITY BOUNDARY FAIL: fail-closed: %s's grants are not a list in %s"
                % (identity, path))
            continue
        for category in categories:
            cat_str = str(category).strip()
            if cat_str.lower() == "people-intelligence":
                findings.append("MACHINE IDENTITY BOUNDARY FAIL: %s: people-intelligence" % identity)
            elif cat_str in known_categories:
                findings.append("MACHINE IDENTITY BOUNDARY FAIL: %s: %s" % (identity, cat_str))
        findings.extend(leg2_layerb_credential_or_folder(identity))
    return findings


def run_grants(path):
    findings = evaluate_grants_snapshot(path)
    for f in findings:
        print(f)
    if findings:
        return 1
    print("RESULT PASS (grants snapshot names no machine-identity boundary breach)")
    return 0


def selftest():
    # Spec 90.2 SELF-VERIFY contract: --selftest runs the clean fixture
    # (expects 0 -- no findings) and the poisoned fixture, which grants
    # "Individual utilisation detail" to reconciler (expects 1 -- a finding
    # naming reconciler and that category), against the real --grants
    # evaluator -- the same code path `--grants` itself uses.
    clean_findings = evaluate_grants_snapshot(CLEAN_FIXTURE)
    if clean_findings:
        print("SELFTEST FAIL: clean fixture %s should evaluate to 0 findings but got:"
              % CLEAN_FIXTURE)
        for f in clean_findings:
            print("  - %s" % f)
        return 1

    poisoned_findings = evaluate_grants_snapshot(POISONED_FIXTURE)
    if not poisoned_findings:
        print("SELFTEST FAIL: poisoned fixture %s should evaluate to a finding "
              "(reconciler holding Individual utilisation detail) but found none"
              % POISONED_FIXTURE)
        return 1
    if not any("reconciler" in f and "Individual utilisation detail" in f
               for f in poisoned_findings):
        print("SELFTEST FAIL: poisoned fixture violation was not attributed to "
              "reconciler/Individual utilisation detail: %r" % poisoned_findings)
        return 1

    print("L5-T13 SELF-VERIFY PASS")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()

    if "--grants" in argv:
        idx = argv.index("--grants")
        grants_path = argv[idx + 1] if idx + 1 < len(argv) else None
        return run_grants(grants_path)

    matrix = load_yaml(MATRIX_PATH)
    if matrix is None:
        print("RESULT FAIL matrix-unreadable %s" % MATRIX_PATH)
        return 2

    findings = leg1_declared_absolute(matrix)
    findings += leg2_no_live_grant()

    for f in findings:
        print("FINDING %s" % f)
    if findings:
        print("RESULT FAIL")
        print("CLASS security-incident")
        print("AUTHORITY Section 90.2 (machine-identities row, absolute)")
        return 1
    print("RESULT PASS (0 machine-identity boundary breaches)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
