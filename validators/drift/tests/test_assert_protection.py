"""L3-P5-03: verifier assertion B — branch protection and ruleset JSON
match the committed template."""

from __future__ import annotations

import pytest

from validators.drift import verifier
from validators.drift.assert_protection import _canonical, check
from validators.drift.verifier import VerifierState


@pytest.fixture(autouse=True)
def _empty_registry(monkeypatch):
    monkeypatch.setattr(verifier, "ASSERTIONS", {"protection_matches_template": check})
    yield


def test_fixture_a_fails_because_beta_disables_code_owner_review():
    result = check(VerifierState("fixture-a"))
    assert result.passed is False
    assert result.checked == 2
    assert "beta" in result.detail
    assert "alpha" not in result.detail


def test_checked_counts_every_repository_examined():
    result = check(VerifierState("fixture-a"))
    assert result.checked == len(VerifierState("fixture-a").repos())


def test_alpha_alone_matches_the_committed_template():
    state = VerifierState("fixture-a")
    template = state.committed_template("branch-protection")
    assert _canonical(state.branch_protection("alpha")) == _canonical(template)


def test_canonical_ignores_key_order():
    a = {"b": 1, "a": {"y": 2, "x": 1}}
    b = {"a": {"x": 1, "y": 2}, "b": 1}
    assert _canonical(a) == _canonical(b)


def test_canonical_does_not_ignore_a_value_difference():
    a = {"require_code_owner_reviews": True}
    b = {"require_code_owner_reviews": False}
    assert _canonical(a) != _canonical(b)


def test_a_stricter_than_declared_repository_still_fails_this_assertion():
    """Unlike the reconciler's own comparator, this verifier assertion
    has no stricter-than-declared carve-out - any difference fails."""

    class StricterState:
        def repos(self):
            return ["solo"]

        def committed_template(self, name):
            return {"required_approving_review_count": 1}

        def branch_protection(self, repo):
            return {"required_approving_review_count": 2}

    result = check(StricterState())
    assert result.passed is False
    assert result.checked == 1


def test_via_verifier_cli_only_flag_exit_code_and_output_match_spec():
    import io
    from contextlib import redirect_stdout

    from validators.drift.verifier import main

    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = main(["--fixture", "fixture-a", "--only", "protection_matches_template", "--summary"])
    assert buf.getvalue() == (
        "VERIFY protection_matches_template result=fail checked=2\n"
        "VERIFIER result=fail assertions=1\n"
    )
    assert exit_code == 2
