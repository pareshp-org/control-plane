"""L3-P1-19: fail-closed matrix for Blocking-class checks."""

from __future__ import annotations

import contextlib
import io

from reconciler.cli import main
from reconciler.failmode import FAIL_MODE, on_comparator_error
from reconciler.model import DriftClass, Level
from reconciler.registry import FAIL_CLASS


def test_fail_mode_matches_spec_64_2_exactly():
    assert FAIL_MODE == {
        DriftClass.BLOCKING: "closed",
        DriftClass.RED: "closed",
        DriftClass.AMBER: "open_with_alert",
        DriftClass.GREEN: "open_with_alert",
    }


def test_blocking_class_error_yields_a_blocking_finding_never_a_silent_skip():
    finding = on_comparator_error("some_comparator", DriftClass.BLOCKING, RuntimeError("boom"))
    assert finding.drift_class == DriftClass.BLOCKING
    assert finding.level == Level.BLOCK
    assert "boom" in finding.evidence


def test_red_class_error_also_fails_closed():
    finding = on_comparator_error("some_comparator", DriftClass.RED, RuntimeError("boom"))
    assert finding.drift_class == DriftClass.BLOCKING
    assert finding.level == Level.BLOCK


def test_amber_class_error_fails_open_with_a_visible_alert():
    finding = on_comparator_error("some_comparator", DriftClass.AMBER, RuntimeError("boom"))
    assert finding.drift_class == DriftClass.AMBER
    assert finding.level == Level.WARN
    assert "some_comparator" in finding.evidence


def test_green_class_error_also_fails_open():
    finding = on_comparator_error("some_comparator", DriftClass.GREEN, RuntimeError("boom"))
    assert finding.drift_class == DriftClass.AMBER
    assert finding.level == Level.WARN


def test_undeclared_fail_class_makes_list_exit_nonzero(monkeypatch):
    from reconciler.cli import _load_comparators
    from reconciler.registry import COMPARATORS

    _load_comparators()
    assert COMPARATORS  # sanity: at least one real comparator is registered
    some_id = next(iter(COMPARATORS))
    stripped = dict(FAIL_CLASS)
    del stripped[some_id]
    monkeypatch.setattr("reconciler.cli.FAIL_CLASS", stripped)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(["list"])
    assert code != 0
