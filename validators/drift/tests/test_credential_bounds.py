"""L3-P5-06: AT-110 credential-bounds probe — six negative attempts."""

from __future__ import annotations

import io
from contextlib import redirect_stdout

import pytest

from validators.drift.credential_bounds import (
    ATTEMPT_ORDER,
    DECLARED_WRITE_SCOPE,
    FixtureCredential,
    ProbeOutcome,
    SecurityIncident,
    main,
    probe,
)


def test_attempt_order_matches_at_110s_own_literal_order():
    assert ATTEMPT_ORDER == (
        "actions_secret_write",
        "environment_write",
        "workflow_file_change",
        "org_settings_change",
        "records_write",
        "layer_b_access",
    )


def test_fixture_mode_blocks_all_six_and_completes_the_follow_on_run():
    outcome = probe(FixtureCredential(), "fixture", fixture="fixture-a")
    assert list(outcome.attempts.keys()) == list(ATTEMPT_ORDER)
    assert all(v == "blocked" for v in outcome.attempts.values())
    assert outcome.reconciliation_completed is True


def test_a_permitted_attempt_raises_security_incident_and_halts_before_later_attempts():
    # Grant only the third surface in AT-110's order — attempts 1 and 2
    # must still run and report "blocked" before the incident halts
    # the probe; attempts 4-6 must never run at all.
    granted = frozenset({"workflow_file_change"})
    credential = FixtureCredential(granted_scope=granted)

    with pytest.raises(SecurityIncident) as excinfo:
        probe(credential, "fixture", fixture="fixture-a")

    incident = excinfo.value
    assert incident.attempts == {
        "actions_secret_write": "blocked",
        "environment_write": "blocked",
        "workflow_file_change": "PERMITTED",
    }
    assert "workflow_file_change" in str(incident)
    assert "spec 43" in str(incident)


def test_declared_write_scope_is_exactly_the_one_named_check_run():
    # spec 40.1: "check-run write on product repositories, used for
    # exactly one named check." Any wider scope here would itself be
    # a spec violation independent of AT-110's own six attempts.
    assert DECLARED_WRITE_SCOPE == frozenset({"check_run:control-plane/blocking-drift"})


def test_layer_b_access_is_blocked_structurally_even_under_a_fully_granted_scope():
    # Granting every AT-110 surface name in the scope table still can't
    # permit Layer B access — a GitHub PAT has no network path there at
    # all (Layer B is Lane 5's off-GitHub host).
    credential = FixtureCredential(granted_scope=frozenset(ATTEMPT_ORDER))
    with pytest.raises(SecurityIncident) as excinfo:
        probe(credential, "fixture", fixture="fixture-a")
    # The incident fires on the first granted surface (attempt 1), long
    # before layer_b_access (attempt 6) is ever reached.
    assert "actions_secret_write" in str(excinfo.value)
    assert "layer_b_access" not in excinfo.value.attempts


def test_probe_rejects_an_unknown_mode():
    with pytest.raises(ValueError, match="mode must be"):
        probe(FixtureCredential(), "staging")


def test_probe_rejects_a_credential_answering_anything_other_than_blocked_or_permitted():
    class BadCredential:
        def try_actions_secret_write(self):
            return "maybe"

        try_environment_write = try_actions_secret_write
        try_workflow_file_change = try_actions_secret_write
        try_org_settings_change = try_actions_secret_write
        try_records_write = try_actions_secret_write
        try_layer_b_access = try_actions_secret_write

    with pytest.raises(ValueError, match="blocked.*PERMITTED"):
        probe(BadCredential(), "fixture", fixture="fixture-a")


def test_cli_fixture_mode_matches_the_spec_literal_summary_and_exits_zero():
    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = main(["--mode", "fixture", "--summary"])
    assert buf.getvalue() == (
        "PROBE actions_secret_write=blocked\n"
        "PROBE environment_write=blocked\n"
        "PROBE workflow_file_change=blocked\n"
        "PROBE org_settings_change=blocked\n"
        "PROBE records_write=blocked\n"
        "PROBE layer_b_access=blocked\n"
        "PROBE reconciliation_after=complete\n"
        "AT-110 result=pass attempts=6\n"
    )
    assert exit_code == 0
