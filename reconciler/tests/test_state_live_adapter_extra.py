"""Extra coverage for reconciler/state beyond L3-P0-06's frozen five-test
SELF-VERIFY count in test_state.py - kept separate so that file's exact
`5 passed` acceptance line stays byte-stable."""

import pytest

from reconciler.state.fixture_adapter import FixtureState
from reconciler.state.live_adapter import LiveAdapterDisabled, LiveState


def test_fixture_state_codeowners_and_resolve_tag():
    state = FixtureState("fixture-a")
    assert "@lead-1" in state.codeowners("alpha")
    assert state.resolve_tag("workflows/v3") == "b" * 40
    assert state.resolve_tag("workflows/does-not-exist") is None


def test_fixture_state_missing_repo_codeowners_raises():
    state = FixtureState("fixture-a")
    with pytest.raises(FileNotFoundError):
        state.codeowners("gamma")


def test_live_adapter_refuses_without_a_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(LiveAdapterDisabled):
        LiveState("some-org", live=True, token=None)
