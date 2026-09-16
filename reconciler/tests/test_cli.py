"""L3-P1-01: comparator registry and reconciler.cli."""

from __future__ import annotations

import contextlib
import io

from reconciler.cli import main
from reconciler.registry import COMPARATORS, FAIL_CLASS


def _run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    return code, buf.getvalue()


def test_list_exits_zero():
    code, _ = _run(["list"])
    assert code == 0


def test_list_prints_every_registered_id_sorted_one_per_line():
    code, out = _run(["list"])
    printed = out.splitlines()
    assert printed == sorted(COMPARATORS)


def test_every_registered_comparator_declares_a_fail_class():
    # spec 64.2 / L3-P1-19: "Unclassified controls fail CI." The
    # registry only ever gains entries via the @comparator decorator,
    # which requires fail_class - this test guards that invariant.
    assert set(COMPARATORS) <= set(FAIL_CLASS)


def test_run_without_fixture_or_live_is_an_error():
    code, _ = _run(["run"])
    assert code != 0


def test_as_of_is_parsed_from_the_flag_not_the_wall_clock():
    from datetime import date

    from reconciler.cli import _parse_as_of

    assert _parse_as_of("2026-08-27") == date(2026, 8, 27)
