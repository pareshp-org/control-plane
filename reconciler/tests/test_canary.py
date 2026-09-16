"""L3-P1-17: seeded canary and the zero-findings FAIL rule."""

from __future__ import annotations

import contextlib
import io
from datetime import date

from reconciler.canary import CANARY_ID, assert_canary
from reconciler.cli import DeclaredState, main
from reconciler.comparators.display_name import compare as display_name_compare
from reconciler.model import DriftClass, Finding, Level
from reconciler.state.fixture_adapter import FixtureState


def _canary_finding():
    return Finding(
        id=CANARY_ID,
        comparator="display_name",
        scope="alpha",
        drift_class=DriftClass.GREEN,
        level=Level.DETECT,
        evidence="seeded canary",
        first_seen="2026-08-27T00:00:00Z",
    )


def test_normal_fixture_a_run_prints_canary_found():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, compared = display_name_compare(declared, actual, date(2026, 8, 27))
    assert compared == 1
    assert assert_canary(findings) is True


def test_assert_canary_true_only_with_the_canary_id_present():
    assert assert_canary([_canary_finding()]) is True
    assert assert_canary([]) is False

    other = Finding(
        id="not-the-canary",
        comparator="org_membership",
        scope="x",
        drift_class=DriftClass.BLOCKING,
        level=Level.BLOCK,
        evidence="e",
        first_seen="2026-08-27T00:00:00Z",
    )
    assert assert_canary([other]) is False


def test_cli_full_run_prints_canary_found_and_exits_zero_or_two():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(["run", "--fixture", "fixture-a", "--as-of", "2026-08-27", "--summary"])
    out = buf.getvalue().splitlines()
    assert out[-1] == "CANARY found"
    assert code in (0, 2)


def test_cli_full_run_fails_with_exit_3_when_canary_is_suppressed(monkeypatch, tmp_path):
    # Suppress the canary by pointing the run at a fixture copy whose
    # canary.yaml declares matching names (so display_name.compare
    # never emits the canary finding), even though other comparators
    # still produce real findings.
    import shutil

    from reconciler.cli import FIXTURES_ROOT

    src = FIXTURES_ROOT / "fixture-a"
    dst = tmp_path / "fixture-a"
    shutil.copytree(src, dst)
    canary_path = dst / "canary.yaml"
    canary_path.write_text(
        "canary:\n"
        "  id: CANARY-001\n"
        "  comparator: display_name\n"
        "  product: alpha\n"
        '  declared_display_name: "Alpha"\n'
        '  actual_display_name: "Alpha"\n'
        "  drift_class: Green\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("reconciler.cli.FIXTURES_ROOT", tmp_path)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(["run", "--fixture", "fixture-a", "--as-of", "2026-08-27", "--summary"])
    out = buf.getvalue().splitlines()
    assert out[-1] == "CANARY missing"
    assert code == 3
    # other comparators still found real drift in this run
    assert any("findings=1" in line or "findings=2" in line for line in out[:-1])


def test_cli_full_run_fails_with_exit_3_when_all_findings_are_suppressed(monkeypatch):
    # The canary stays registered (so the rule is active) but every
    # comparator, including display_name itself, reports no findings
    # this run - AT-102 fails this run too, not just a missing canary.
    from reconciler.cli import _load_comparators
    from reconciler.registry import COMPARATORS

    _load_comparators()

    def _no_findings(declared, actual, as_of):
        return [], 1

    fake = {cid: _no_findings for cid in COMPARATORS}
    monkeypatch.setattr("reconciler.cli.COMPARATORS", fake)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(["run", "--fixture", "fixture-a", "--as-of", "2026-08-27", "--summary"])
    out = buf.getvalue().splitlines()
    assert out[-1] == "CANARY missing"
    assert code == 3
