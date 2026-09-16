"""L3-P0-06: GitHubState port and fixture adapter."""

import pytest

from reconciler.state.fixture_adapter import FixtureState
from reconciler.state.live_adapter import LiveAdapterDisabled, LiveState
from reconciler.state.port import GitHubState, assert_read_only

_WRITE_PREFIXES = ("set_", "write_", "create_", "delete_", "update_", "put_")


def test_no_write_methods_on_the_port():
    names = [n for n in dir(GitHubState) if not n.startswith("_")]
    offenders = [n for n in names if n.startswith(_WRITE_PREFIXES)]
    assert offenders == []


def test_no_write_methods_on_fixture_adapter():
    assert_read_only(FixtureState)


def test_no_write_methods_on_live_adapter():
    assert_read_only(LiveState)


def test_fixture_state_counts():
    state = FixtureState("fixture-a")
    assert len(state.org_members()) == 5
    assert len(state.team_members("alpha")) == 5
    assert len(state.team_members("beta")) == 1


def test_live_adapter_refuses_without_explicit_live_flag():
    with pytest.raises(LiveAdapterDisabled):
        LiveState("some-org", live=False)
