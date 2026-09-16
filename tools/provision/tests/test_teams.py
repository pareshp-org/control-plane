"""Tests for L3-P4-05: Team creator derived from the registries."""

from __future__ import annotations

import pytest

from tools.provision.teams import (
    CallerSuppliedMembership,
    QA_TEAM,
    TEAM_LEAD_TEAM,
    Team,
    plan_teams,
)


def test_fixture_a_plans_four_teams():
    teams = plan_teams("fixture-a")
    assert len(teams) == 4
    assert set(teams) == {"alpha", "beta", TEAM_LEAD_TEAM, QA_TEAM}


def test_alpha_membership_is_exactly_its_four_current_assignment_holders():
    teams = plan_teams("fixture-a")
    assert len(teams["alpha"]) == 4
    assert set(teams["alpha"]) == {"lead-1", "dev-1", "founder-1", "qa-1"}


def test_dev_2_is_absent_from_every_team():
    teams = plan_teams("fixture-a")
    for name, members in teams.items():
        assert "dev-2" not in members, f"dev-2 holds no assignment and no role capability; found in {name}"


def test_org_wide_teams_are_named_team_lead_and_qa():
    teams = plan_teams("fixture-a")
    assert teams[TEAM_LEAD_TEAM] == ["lead-1"]
    assert teams[QA_TEAM] == ["qa-1"]


def test_direct_team_construction_with_a_member_list_raises():
    with pytest.raises(CallerSuppliedMembership):
        Team("rogue", ["dev-1", "dev-2"])


def test_derived_construction_is_the_only_way_to_build_a_team():
    team = Team.derived("rogue", ["dev-1"])
    assert team.name == "rogue"
    assert len(team) == 1
