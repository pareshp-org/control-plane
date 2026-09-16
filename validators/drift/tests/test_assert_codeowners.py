"""L3-P5-02: verifier assertion A — no machine identity in any CODEOWNERS."""

from __future__ import annotations

import pytest

from validators.drift import verifier
from validators.drift.assert_codeowners import _is_machine_identity, _owners, check
from validators.drift.verifier import VerifierState


@pytest.fixture(autouse=True)
def _empty_registry(monkeypatch):
    monkeypatch.setattr(verifier, "ASSERTIONS", {"codeowners_human_only": check})
    yield


def test_fixture_a_fails_because_alpha_names_ci_bot():
    result = check(VerifierState("fixture-a"))
    assert result.passed is False
    assert result.checked == 2
    assert "alpha" in result.detail
    assert "ci-bot" in result.detail


def test_checked_counts_every_repository_examined_not_just_the_failing_one():
    result = check(VerifierState("fixture-a"))
    assert result.checked == len(VerifierState("fixture-a").repos())


def test_beta_alone_has_no_machine_identity_and_passes():
    # beta.CODEOWNERS names only human logins from people.yaml.
    text = VerifierState("fixture-a").codeowners("beta")
    known = VerifierState("fixture-a").known_logins()
    assert all(not _is_machine_identity(o, known) for o in _owners(text))


def test_owners_parses_multiple_owners_per_line_and_skips_comments_and_blanks():
    text = "# a comment\n\n* @a @b\n/verification/ @c\n"
    assert _owners(text) == ["a", "b", "c"]


def test_a_login_absent_from_people_yaml_is_treated_as_a_machine_identity():
    known = {"lead-1", "dev-1"}
    assert _is_machine_identity("some-unregistered-login", known) is True
    assert _is_machine_identity("lead-1", known) is False


def test_a_bot_suffixed_login_is_a_machine_identity_even_if_it_were_in_people_yaml():
    known = {"lead-1", "sneaky[bot]"}
    assert _is_machine_identity("sneaky[bot]", known) is True


def test_via_verifier_cli_only_flag_exit_code_and_output_match_spec():
    import io
    from contextlib import redirect_stdout

    from validators.drift.verifier import main

    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = main(["--fixture", "fixture-a", "--only", "codeowners_human_only", "--summary"])
    assert buf.getvalue() == (
        "VERIFY codeowners_human_only result=fail checked=2\n"
        "VERIFIER result=fail assertions=1\n"
    )
    assert exit_code == 2
