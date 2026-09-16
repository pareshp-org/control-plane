"""L3-P5-04: verifier assertion C — the bypass-actor list is exactly as declared."""

from __future__ import annotations

import io
from contextlib import redirect_stdout

import pytest

from validators.drift import verifier
from validators.drift.assert_bypass import DECLARED_BYPASS_ACTORS, check
from validators.drift.verifier import VerifierState


@pytest.fixture(autouse=True)
def _empty_registry(monkeypatch):
    monkeypatch.setattr(verifier, "ASSERTIONS", {"bypass_actors_exact": check})
    yield


def test_fixture_a_fails_because_renovate_b_lists_renovate_bot():
    result = check(VerifierState("fixture-a"))
    assert result.passed is False
    assert result.checked == 2
    assert "renovate-B" in result.detail
    assert "renovate[bot]" in result.detail


def test_renovate_a_may_list_exactly_the_renovate_app_and_nothing_else():
    assert DECLARED_BYPASS_ACTORS["renovate-A"] == frozenset({"renovate[bot]"})


def test_control_plane_records_and_workflows_tag_declare_no_bypass_actor_at_all():
    assert DECLARED_BYPASS_ACTORS["control-plane"] == frozenset()
    assert DECLARED_BYPASS_ACTORS["records-force-push-deletion"] == frozenset()
    assert DECLARED_BYPASS_ACTORS["workflows-tag"] == frozenset()
    assert DECLARED_BYPASS_ACTORS["renovate-B"] == frozenset()


def test_a_ruleset_matching_its_declared_row_exactly_does_not_contribute_a_failure():
    class _State:
        def rulesets(self):
            return [{"name": "renovate-A", "bypass_actors": ["renovate[bot]"]}]

    result = check(_State())
    assert result.passed is True
    assert result.checked == 1


def test_an_undeclared_ruleset_name_fails_closed_rather_than_being_skipped():
    class _State:
        def rulesets(self):
            return [{"name": "some-new-ruleset", "bypass_actors": []}]

    result = check(_State())
    assert result.passed is False
    assert result.checked == 1
    assert "some-new-ruleset" in result.detail


def test_checked_counts_every_ruleset_examined_even_when_all_pass():
    class _State:
        def rulesets(self):
            return [
                {"name": "renovate-A", "bypass_actors": ["renovate[bot]"]},
                {"name": "control-plane", "bypass_actors": []},
            ]

    result = check(_State())
    assert result.passed is True
    assert result.checked == 2


def test_via_verifier_cli_only_flag_exit_code_and_output_match_spec():
    from validators.drift.verifier import main

    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = main(["--fixture", "fixture-a", "--only", "bypass_actors_exact", "--summary"])
    assert buf.getvalue() == (
        "VERIFY bypass_actors_exact result=fail checked=2\n" "VERIFIER result=fail assertions=1\n"
    )
    assert exit_code == 2
