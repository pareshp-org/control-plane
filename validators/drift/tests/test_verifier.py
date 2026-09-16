"""L3-P5-01: independent verifier skeleton under a separate credential."""

from __future__ import annotations

import os

import pytest

from validators.drift import verifier
from validators.drift.verifier import (
    ASSERTIONS,
    AssertionResult,
    VerifierState,
    assertion,
    main,
    read_credential,
    run_assertions,
)


@pytest.fixture(autouse=True)
def _empty_registry(monkeypatch):
    """Every test here runs against a registry monkeypatch clears to {}
    first — deliberately isolating this test file from whatever
    assert_*.py modules later tasks (L3-P5-02, L3-P5-04, ...) add to the
    real, on-disk registry. This is the skeleton's own test: it must
    pass identically whether it is run the day this file lands or after
    every later assertion module exists.

    Isolation must not depend on import/collection order: main() below
    calls verifier._discover_assertion_modules(), which imports every
    sibling assert_*.py module and — the FIRST time any given module is
    imported in this process — runs its @assertion(...) decorator,
    repopulating whatever dict ASSERTIONS currently points at. If those
    sibling modules happen not to have been imported yet by the time
    this fixture patches ASSERTIONS to {}, main()'s own import inside
    the test refills the freshly-emptied dict and this fixture's
    isolation is silently defeated. Importing them here, before the
    monkeypatch, guarantees their decorators have already fired into
    the *real* registry — so the re-import main() triggers is a cached
    no-op (importlib does not re-run an already-imported module's
    top-level code) and the patched dict stays empty regardless of
    whether this file is run alone or alongside its siblings."""
    verifier._discover_assertion_modules()
    monkeypatch.setattr(verifier, "ASSERTIONS", {})
    yield


def test_no_assertions_registered_prints_pass_zero_and_exits_zero(monkeypatch, capsys):
    monkeypatch.delenv("DRIFT_VERIFIER_TOKEN", raising=False)
    exit_code = main(["--fixture", "fixture-a", "--summary"])
    out = capsys.readouterr().out
    assert out == "VERIFIER result=pass assertions=0\n"
    assert exit_code == 0


def test_registered_assertion_that_fails_drives_exit_code_two(monkeypatch, capsys):
    @assertion("always_fails")
    def _check(state):  # noqa: ARG001 - state unused by this fixture assertion
        return AssertionResult(passed=False, checked=3, detail="deliberately fails")

    exit_code = main(["--fixture", "fixture-a", "--only", "always_fails", "--summary"])
    out = capsys.readouterr().out
    assert out == ("VERIFY always_fails result=fail checked=3\n" "VERIFIER result=fail assertions=1\n")
    assert exit_code == 2


def test_verifier_module_imports_nothing_from_reconciler():
    import validators.drift.verifier as v

    src = open(v.__file__, encoding="utf-8").read()
    for line in src.splitlines():
        stripped = line.strip()
        assert not stripped.startswith("import reconciler"), line
        assert not stripped.startswith("from reconciler"), line


def test_credential_comes_only_from_drift_verifier_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("DRIFT_VERIFIER_TOKEN", raising=False)
    assert read_credential() is None

    monkeypatch.setenv("GITHUB_TOKEN", "reconciler-credential-must-be-ignored")
    assert read_credential() is None

    monkeypatch.setenv("DRIFT_VERIFIER_TOKEN", "verifier-credential")
    assert read_credential() == "verifier-credential"


def test_verifier_state_reads_actual_codeowners_for_every_repo_in_fixture_a():
    state = VerifierState("fixture-a")
    assert state.repos() == ["alpha", "beta"]
    assert "@ci-bot" in state.codeowners("alpha")


def test_run_assertions_fails_closed_on_a_crashing_assertion():
    @assertion("boom")
    def _check(state):  # noqa: ARG001
        raise RuntimeError("simulated read failure")

    results = run_assertions(["boom"], VerifierState("fixture-a"))
    assert len(results) == 1
    assertion_id, result = results[0]
    assert assertion_id == "boom"
    assert result.passed is False
    assert "simulated read failure" in result.detail


def test_only_with_unknown_assertion_id_errors_without_running_anything(monkeypatch, capsys):
    exit_code = main(["--fixture", "fixture-a", "--only", "no-such-assertion", "--summary"])
    err = capsys.readouterr().err
    assert "unknown assertion id" in err
    assert exit_code == 1
