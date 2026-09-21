"""reconciler.gap - the control-loop gap procedure (spec 53.7; spec 46.1).

Section 53.7: "The control loop can fail in two directions. It can go
dark - a reconciliation gap, an export gap, or a health-report gap. It
can also run and repair against a wrongly-computed declared state."
This package covers the first direction. `detect.py` (L3-P8-01) is the
first module in it: it finds the missed-cycle window and replays every
expiry that should have fired inside it.
"""

from __future__ import annotations
