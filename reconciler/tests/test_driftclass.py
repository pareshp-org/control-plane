"""Tests for reconciler.driftclass (L3-P3-01)."""

from __future__ import annotations

import inspect

from reconciler.driftclass import (
    DEFAULT_CLASSES,
    SECURITY_OR_PROD_ENV_COMPARATORS,
    load_classes,
)
from reconciler.model import DriftClass


def _write_os_health(tmp_path, drift_classes):
    path = tmp_path / "os-health.yaml"
    lines = ["drift_classes:"]
    for comparator_id, cls in drift_classes.items():
        lines.append(f"  {comparator_id}: {cls}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_configured_override_wins_for_non_security_comparator(tmp_path):
    assert "capability_authority" not in SECURITY_OR_PROD_ENV_COMPARATORS
    assert DEFAULT_CLASSES["capability_authority"] == DriftClass.AMBER
    path = _write_os_health(tmp_path, {"capability_authority": "Green"})

    classes = load_classes(path)

    assert classes["capability_authority"] == DriftClass.GREEN


def test_code_default_used_when_file_declares_no_override(tmp_path):
    path = _write_os_health(tmp_path, {})  # no drift_classes entries at all

    classes = load_classes(path)

    assert classes["codeowners"] == DEFAULT_CLASSES["codeowners"] == DriftClass.AMBER


def test_security_floor_refuses_downward_config_and_emits_finding(tmp_path):
    assert "branch_protection" in SECURITY_OR_PROD_ENV_COMPARATORS
    path = _write_os_health(tmp_path, {"branch_protection": "Green"})
    findings: list = []

    classes = load_classes(path, findings=findings, first_seen="2026-08-27T00:00:00Z")

    assert classes["branch_protection"] == DriftClass.RED
    assert len(findings) == 1
    refusal = findings[0]
    assert refusal.drift_class == DriftClass.BLOCKING
    assert refusal.comparator == "driftclass"
    assert refusal.scope == "branch_protection"
    assert "branch_protection" in refusal.evidence
    assert "Green" in refusal.evidence


def test_security_floor_applies_even_when_findings_arg_is_omitted(tmp_path):
    path = _write_os_health(tmp_path, {"environments": "Amber"})

    classes = load_classes(path)  # findings=None: no crash, floor still applies

    assert classes["environments"] == DriftClass.RED


def test_module_performs_no_write_operation():
    import reconciler.driftclass as m

    src = inspect.getsource(m)
    for forbidden in ('"w")', "'w')", '"w+"', "'w+'", "os.remove", "unlink(", "Path.write"):
        assert forbidden not in src, f"driftclass.py must never write: found {forbidden!r}"
