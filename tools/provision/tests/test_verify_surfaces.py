"""Tests for L3-P0-AT001: create-product scaffold conformance verifier."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.provision.surfaces import Surface, StepResult, load_surfaces, run as run_step
from tools.provision.verify_surfaces import (
    declared_product_ids,
    run_live,
    run_static,
    static_check,
)


def test_exactly_six_surfaces_are_declared():
    surfaces = load_surfaces()
    assert len(surfaces) == 6
    assert {s.id for s in surfaces} == {
        "portfolio-board",
        "grafana",
        "scorecard",
        "devlake",
        "reviewer-matrix",
        "dependency-graph",
    }


def test_every_surface_enumerates_from_the_product_registry():
    surfaces = load_surfaces()
    assert all(s.enumerates_from == "product_registry" for s in surfaces)


def test_step_confirms_without_any_write(monkeypatch):
    result = run_step(load_surfaces())
    assert isinstance(result, StepResult)
    assert result.kind == "read"
    assert len(result.surfaces_confirmed) == 6


def test_step_rejects_a_surface_that_does_not_enumerate_from_the_registry():
    poisoned = [Surface(id="rogue", enumerates_from="hard-coded-list", live_probe="none")]
    with pytest.raises(ValueError):
        run_step(poisoned)


def _make_control_plane(tmp_path: Path, *, product_id: str, hardcoded_in: str | None) -> Path:
    root = tmp_path / "control-plane"
    (root / "registries" / "products" / product_id).mkdir(parents=True)
    (root / "registries" / "products" / product_id / "product.yaml").write_text(
        f"identity:\n  id: {product_id}\n", encoding="utf-8"
    )
    if hardcoded_in is not None:
        target = root / hardcoded_in
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"products: [{product_id}]\n", encoding="utf-8")
    return root


def test_seeded_hardcode_detected(tmp_path):
    root = _make_control_plane(tmp_path, product_id="delta", hardcoded_in="dashboards/board.json")
    hits = static_check(root)
    assert len(hits) == 1
    assert "dashboards/board.json" in hits[0]
    assert "delta" in hits[0]
    assert run_static(root) == 3


def test_clean_tree_reports_zero_hardcoded(tmp_path):
    root = _make_control_plane(tmp_path, product_id="delta", hardcoded_in=None)
    hits = static_check(root)
    assert hits == []
    assert run_static(root) == 0


def test_no_declared_products_yet_is_vacuously_clean(tmp_path):
    root = tmp_path / "control-plane"
    root.mkdir()
    assert declared_product_ids(root) == []
    assert static_check(root) == []


def test_static_check_excludes_the_registry_directory_itself(tmp_path):
    # The hit inside registries/products/<id>/product.yaml itself must
    # never be reported -- that is the declaration, not a leak.
    root = _make_control_plane(tmp_path, product_id="delta", hardcoded_in=None)
    hits = static_check(root)
    assert hits == []


def test_static_check_excludes_records_and_events(tmp_path):
    root = _make_control_plane(tmp_path, product_id="delta", hardcoded_in="records/deployments/delta.json")
    assert static_check(root) == []
    root2 = _make_control_plane(tmp_path / "other", product_id="delta", hardcoded_in="events/delta.json")
    assert static_check(root2) == []


def test_unreachable_is_failure():
    surfaces = load_surfaces()
    # No prober override: the default reports every surface honestly
    # unreachable, because no live dashboard/board/Grafana/etc.
    # infrastructure exists to probe in this environment.
    assert run_live(surfaces) == 3


def test_unreachable_surface_never_prints_a_pass(capsys):
    run_live(load_surfaces())
    out = capsys.readouterr().out
    assert "OK" not in out
    assert out.count("UNREACHABLE") == 6


def test_reachable_surface_reports_ok():
    surfaces = load_surfaces()
    assert run_live(surfaces, prober=lambda surface: True) == 0
