"""Tests for validators/registry/loader.py (L1-004)."""
import os

from validators.registry.loader import load_registry_file

FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures", "loader")


def _fixture(name):
    return os.path.join(FIXTURES, name)


def test_yml_01_duplicate_key():
    data, errors = load_registry_file(_fixture("bad_yml_01.yaml"))
    assert data == {}
    assert len(errors) == 1
    assert errors[0].rule_id == "L-YML-01"

    good_data, good_errors = load_registry_file(_fixture("good.yaml"))
    assert good_errors == []
    assert good_data == {"registry_version": 1, "items": []}


def test_yml_02_anchor_or_alias():
    data, errors = load_registry_file(_fixture("bad_yml_02.yaml"))
    assert data == {}
    assert len(errors) == 1
    assert errors[0].rule_id == "L-YML-02"


def test_yml_03_merge_key():
    data, errors = load_registry_file(_fixture("bad_yml_03.yaml"))
    assert data == {}
    assert len(errors) == 1
    assert errors[0].rule_id == "L-YML-03"


def test_yml_04_tab_in_indentation():
    data, errors = load_registry_file(_fixture("bad_yml_04.yaml"))
    assert data == {}
    assert len(errors) == 1
    assert errors[0].rule_id == "L-YML-04"


def test_yml_05_byte_order_mark():
    data, errors = load_registry_file(_fixture("bad_yml_05.yaml"))
    assert data == {}
    assert len(errors) == 1
    assert errors[0].rule_id == "L-YML-05"


def test_yml_06_multi_document():
    data, errors = load_registry_file(_fixture("bad_yml_06.yaml"))
    assert data == {}
    assert len(errors) == 1
    assert errors[0].rule_id == "L-YML-06"


def test_yml_07_top_level_not_mapping():
    data, errors = load_registry_file(_fixture("bad_yml_07.yaml"))
    assert data == {}
    assert len(errors) == 1
    assert errors[0].rule_id == "L-YML-07"


def test_yml_08_bad_trailing_newline():
    data, errors = load_registry_file(_fixture("bad_yml_08.yaml"))
    assert data == {}
    assert len(errors) == 1
    assert errors[0].rule_id == "L-YML-08"


def test_yml_09_bad_encoding():
    data, errors = load_registry_file(_fixture("bad_yml_09.yaml"))
    assert data == {}
    assert len(errors) == 1
    assert errors[0].rule_id == "L-YML-09"
