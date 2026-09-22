#!/usr/bin/env python3
"""tools/records/read_across.py -- fail-closed cross-repository reader.

Lane 4 task L4-P4-08. Charter DoD-16. Master Spec v4.0 Section 40.1 line
3671: "a check that cannot reach the records repository fails closed
rather than reporting zero." Section 97.2 line 8867 explains why: a zero
count must never be indistinguishable from a healthy, empty store, so
unreachability of the records repository is reported as a distinct,
non-zero-exit failure and is never folded into a count of zero.

Usage:
    read-across --count <store>

<store> is a path relative to the records repository root, for example
"events" or "records/uat". The root itself is taken from the RECORDS_ROOT
environment variable if set, else from CPR_ROOT (the variable
tools/records/lib/emit.sh and every writer in this lane already use for
the same repository). Neither variable resolving to an existing,
listable directory is unreachability, and this tool fails closed:

    FAIL-CLOSED <reason>            exit 2

A reachable root whose named store directory does not exist yet, or
exists and is empty, is a legitimate zero -- the whole point of the
fail-closed rule is that only unreachability of the repository itself
produces the failure path, never an empty-but-reachable store:

    COUNT <n> store=<store> root=<root>   exit 0
"""
import argparse
import os
import sys


def resolve_root():
    """Return the records-repository root the caller configured, or None.

    RECORDS_ROOT takes precedence so this tool can be pointed at an
    arbitrary root (as the charter's own fail-closed test does); CPR_ROOT
    is the fallback so read-across also works unmodified wherever the
    rest of this lane's tooling already exports it.
    """
    root = os.environ.get("RECORDS_ROOT")
    if root:
        return root
    root = os.environ.get("CPR_ROOT")
    if root:
        return root
    return None


def count_store(root, store):
    """Return (count, error). error is set only when the root itself,
    once resolved to an existing directory, cannot be read for the named
    store -- the "cannot reach" condition Section 40.1 describes. A
    missing store directory under a reachable root is not an error."""
    store_dir = os.path.join(root, store)
    if not os.path.isdir(store_dir):
        return 0, None
    try:
        n = sum(
            1
            for entry in os.scandir(store_dir)
            if entry.is_file() and entry.name.endswith(".yaml")
        )
    except OSError as exc:
        return None, str(exc)
    return n, None


def main(argv):
    parser = argparse.ArgumentParser(prog="read-across", add_help=True)
    parser.add_argument(
        "--count",
        metavar="STORE",
        required=True,
        help="store path relative to the records repository root, e.g. 'events'",
    )
    args = parser.parse_args(argv)

    root = resolve_root()
    if not root:
        print("FAIL-CLOSED no-root-configured (set RECORDS_ROOT or CPR_ROOT)")
        return 2

    if not os.path.isdir(root):
        print("FAIL-CLOSED records-repository-unreachable root=%s" % root)
        return 2

    count, error = count_store(root, args.count)
    if error is not None:
        print(
            "FAIL-CLOSED store-unreadable store=%s root=%s error=%s"
            % (args.count, root, error)
        )
        return 2

    print("COUNT %d store=%s root=%s" % (count, args.count, root))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
