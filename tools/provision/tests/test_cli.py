"""Tests for L3-P4-01: the `provision` CLI skeleton."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools.provision.cli import ApplyRequiresLive, build_parser, main

REPO_ROOT = Path(__file__).resolve().parents[3]
_COMMANDS = ("create-product", "add-person", "change-role", "remove-person")

# Each subcommand's one mandatory identifying flag, so every command can
# be exercised uniformly by the tests below.
_ID_FLAG = {
    "create-product": ["--product", "gamma"],
    "add-person": ["--login", "dev-3"],
    "change-role": ["--login", "dev-1", "--to-role", "qa"],
    "remove-person": ["--login", "dev-1"],
}


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "tools.provision.cli", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_help_mentions_apply_exactly_once():
    result = _run("--help")
    assert result.returncode == 0
    lines_with_apply = [line for line in result.stdout.splitlines() if "--apply" in line]
    assert len(lines_with_apply) == 1


@pytest.mark.parametrize("command", _COMMANDS)
def test_every_subcommand_is_zero_write_without_apply(command):
    result = _run(command, "--fixture", "fixture-a", *_ID_FLAG[command])
    assert result.returncode == 0, result.stderr
    assert f"PLAN {command} steps=" in result.stdout
    assert "writes=0" in result.stdout


@pytest.mark.parametrize("command", _COMMANDS)
def test_dry_run_is_reported_without_apply(command):
    result = _run(command, "--fixture", "fixture-a", *_ID_FLAG[command])
    dry_run_lines = [line for line in result.stdout.splitlines() if "dry-run" in line]
    assert len(dry_run_lines) == 1


def test_apply_without_live_is_refused():
    result = _run("create-product", "--fixture", "fixture-a", "--product", "gamma", "--apply")
    assert result.returncode != 0
    assert "requires --live" in result.stderr


def test_apply_without_live_raises_programmatically():
    parser = build_parser()
    args = parser.parse_args(["create-product", "--fixture", "fixture-a", "--product", "gamma", "--apply"])
    with pytest.raises(ApplyRequiresLive):
        args.func(args)


def test_fixture_and_live_are_mutually_exclusive():
    result = _run("create-product", "--fixture", "fixture-a", "--live", "--product", "gamma")
    assert result.returncode != 0
    assert "not allowed with" in result.stderr


def test_fixture_or_live_is_required():
    result = _run("create-product", "--product", "gamma")
    assert result.returncode != 0
    assert "one of the arguments --fixture --live is required" in result.stderr


def test_apply_with_live_performs_zero_writes_when_plan_is_empty():
    # Skeleton-level: no orchestrator wires real steps into any plan yet
    # (that lands in L3-P4-07/09, L3-P7-01/02), so an --apply --live run
    # has nothing to write and must say so honestly, not report a write
    # that never happened.
    assert main(["create-product", "--live", "--apply", "--product", "gamma"]) == 0


def test_unknown_fixture_is_a_clean_error_not_a_crash():
    result = _run("create-product", "--fixture", "does-not-exist", "--product", "gamma")
    assert result.returncode != 0
    assert "no such fixture" in result.stderr
