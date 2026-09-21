#!/usr/bin/env python3
"""metrics/register/arming.py

Arming discipline (L4-P7-03). Master Spec v4.0 D77 (§103 preamble line 9789)
and §52.2 line 4530: a measure whose source store exists but holds no
records has produced no evidence yet, and reports that honestly as
"unbaselined" - never a synthetic 0, and never a threshold miss. Zero
records is the ONLY condition this script treats specially: a store that
holds N>0 records is "baselined" regardless of what those records say.

Usage: arming.py --store <path>
Exit 0 and print one of:
    ARMING unbaselined              - the store exists but has no records
    ARMING baselined <count>        - the store holds <count> records
Exit 1 and print ARMING FAIL <reason> if the store path itself is absent -
a missing store is a configuration error, not the same thing as an empty
one, and must not be silently treated as "unbaselined" either.
"""
import argparse
import os
import sys


def count_records(store_path):
    """Count files directly under store_path, excluding directories and
    housekeeping markers (.gitkeep, README.md, CONTRIBUTING.md)."""
    ignored = {".gitkeep", "README.md", "CONTRIBUTING.md"}
    total = 0
    for root, dirs, files in os.walk(store_path):
        for name in files:
            if name in ignored:
                continue
            total += 1
    return total


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", required=True)
    args = parser.parse_args(argv)

    if not os.path.isdir(args.store):
        print("ARMING FAIL store-absent %s" % args.store)
        return 1

    count = count_records(args.store)
    if count == 0:
        print("ARMING unbaselined")
    else:
        print("ARMING baselined %d" % count)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
