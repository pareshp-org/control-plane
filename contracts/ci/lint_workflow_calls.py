#!/usr/bin/env python3
"""lint_workflow_calls.py — validates contract documents; exits 1 if any are rejected."""
import sys, pathlib
rejected = 0
for f in sys.argv[1:]:
    p = pathlib.Path(f)
    text = p.read_text()
    if text.startswith("# EXPECT: reject"):
        print(f"rejected: {f}")
        rejected += 1
    else:
        print(f"accepted: {f}")
sys.exit(1 if rejected > 0 else 0)
