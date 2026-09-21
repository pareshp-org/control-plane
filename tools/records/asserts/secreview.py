#!/usr/bin/env python3
"""tools/records/asserts/secreview.py

Lane 4 task L4-P2-25 (see lanes/L4-06-tasks.md, superseded master table row 44,
and lanes/L4-CONCORDANCE.md Phase-2 mapping row L4-P2-25 -> L4-T216, MED confidence).

Master Spec v4.0 Section 97.2 line 8869: findings carry severity and disposition;
an unfixed finding is linked into the Portfolio Debt Inventory with an owner and
a date. schemas/records/security-review.schema.json (L4-T216) requires severity
and disposition unconditionally but leaves owner/due schema-optional on every
finding, because the owner+date requirement is CONDITIONAL -- it applies only
when disposition == "unfixed" -- and this store's schema carries no if/then to
express that. This module is that conditional assertion, run at read time over
one or more security-review record files.

This is exactly the residual gap L4-CONCORDANCE.md records for L4-P2-25: "there
is no separate asserts/secreview.py module ... " This file closes it. It is
deliberately independent of tools/records/validate-schemas.sh's pre-existing
--at046-secreview mode (a PII/no-secrets scan over an unrelated contracts file,
already credited against charter DoD-12) and of --at046 in metrics/register/
validate-sources.sh (the unrelated baseline-integrity acceptance test, AT-046
proper, Section 100.4 line 9368) -- neither of those two modes is edited here.

Deterministic output contract, L4-06-tasks.md Section 0.5: exactly one final
line on stdout, exit 0 (assertion held), 1 (assertion failed), or 3 (could not
execute). Diagnostic detail goes to stderr so the stdout contract holds under
direct invocation as well as under tools/records/checks/L4-P2-25.sh.

Usage: secreview.py <file-or-dir> [<file-or-dir> ...]
"""
import pathlib
import sys

import yaml


class _NoImplicitDatesLoader(yaml.SafeLoader):
    """PyYAML's SafeLoader auto-converts ISO8601-looking scalars into datetime
    objects. security-review records carry a plain-string 'due' date (record.
    base.schema.json $defs.date_utc); strip the implicit timestamp resolver so
    'due' and 'timestamp' come back as strings, matching every other read-time
    tool in this lane (see tools/records/lib/validate_instance.py)."""


_NoImplicitDatesLoader.yaml_implicit_resolvers = {
    key: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load(path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=_NoImplicitDatesLoader)


def check_record(doc, path):
    """Return the list of Section-97.2-line-8869 violations in one record.

    An absent or malformed 'findings' key is not this rule's business -- the
    envelope/schema layer (L4-T216, tools/records/lib/validate_instance.py)
    already rejects those. This module only ever adds a NEW rejection reason:
    an unfixed finding missing its owner, its due date, or both.
    """
    violations = []
    findings = doc.get("findings") if isinstance(doc, dict) else None
    if not isinstance(findings, list):
        return violations
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue
        if finding.get("disposition") != "unfixed":
            continue
        if not finding.get("owner"):
            violations.append("%s: findings[%d]-unfixed-no-owner" % (path, index))
        if not finding.get("due"):
            violations.append("%s: findings[%d]-unfixed-no-due" % (path, index))
    return violations


def gather_files(targets):
    files = []
    for target in targets:
        candidate = pathlib.Path(target)
        if candidate.is_dir():
            files.extend(sorted(candidate.glob("*.yaml")))
            files.extend(sorted(candidate.glob("*.yml")))
        elif candidate.is_file():
            files.append(candidate)
        else:
            raise FileNotFoundError(target)
    return files


def main(argv):
    if not argv:
        print("SECREVIEW ERROR usage: secreview.py <file-or-dir> [...]", file=sys.stderr)
        print("SECREVIEW ERROR no-input")
        return 3
    try:
        files = gather_files(argv)
    except FileNotFoundError as exc:
        print("SECREVIEW ERROR unreachable-path:%s" % exc, file=sys.stderr)
        print("SECREVIEW ERROR unreachable-path")
        return 3

    violations = []
    record_count = 0
    finding_count = 0
    for path in files:
        try:
            doc = load(path)
        except Exception as exc:  # fail closed: an unreadable input is never a silent pass
            print("SECREVIEW ERROR unreadable:%s:%s" % (path, exc), file=sys.stderr)
            print("SECREVIEW ERROR unreadable")
            return 3
        if not isinstance(doc, dict):
            print("SECREVIEW ERROR not-a-mapping:%s" % path, file=sys.stderr)
            print("SECREVIEW ERROR not-a-mapping")
            return 3
        record_count += 1
        finding_count += len(doc.get("findings") or [])
        violations.extend(check_record(doc, path))

    if violations:
        for violation in violations:
            print("SECREVIEW VIOLATION %s" % violation, file=sys.stderr)
        print("SECREVIEW FAIL records=%d findings=%d violations=%d"
              % (record_count, finding_count, len(violations)))
        return 1

    print("SECREVIEW OK records=%d findings=%d" % (record_count, finding_count))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
