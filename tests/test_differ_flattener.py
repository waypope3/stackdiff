"""Tests for stackdiff.differ_flattener."""
import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_flattener import FlattenedDiff, flatten_diffs


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _diff(key, baseline, target):
    return KeyDiff(key=key, baseline_value=baseline, target_value=target)


@pytest.fixture()
def simple_diffs():
    return [
        _diff("VpcId", "vpc-aaa", "vpc-bbb"),
        _diff("Region", "us-east-1", "us-east-1"),
    ]


# ---------------------------------------------------------------------------
# basic behaviour
# ---------------------------------------------------------------------------

def test_returns_flattened_diffs(simple_diffs):
    result = flatten_diffs(simple_diffs)
    assert all(isinstance(r, FlattenedDiff) for r in result)


def test_changed_flag_set_when_values_differ(simple_diffs):
    result = flatten_diffs(simple_diffs)
    vpc = next(r for r in result if r.key == "VpcId")
    assert vpc.changed is True


def test_changed_flag_clear_when_values_equal(simple_diffs):
    result = flatten_diffs(simple_diffs)
    region = next(r for r in result if r.key == "Region")
    assert region.changed is False


def test_depth_zero_for_top_level_keys(simple_diffs):
    result = flatten_diffs(simple_diffs)
    assert all(r.depth == 0 for r in result)


# ---------------------------------------------------------------------------
# nested dict expansion
# ---------------------------------------------------------------------------

def test_nested_dict_expands_to_dot_notation():
    diffs = [_diff("Config", {"port": 80}, {"port": 443})]
    result = flatten_diffs(diffs)
    assert len(result) == 1
    assert result[0].key == "Config.port"


def test_nested_depth_incremented():
    diffs = [_diff("Config", {"port": 80}, {"port": 443})]
    result = flatten_diffs(diffs)
    assert result[0].depth == 1


def test_deeply_nested_keys():
    diffs = [_diff("A", {"b": {"c": 1}}, {"b": {"c": 2}})]
    result = flatten_diffs(diffs)
    assert result[0].key == "A.b.c"
    assert result[0].depth == 2


def test_missing_key_in_target_flattened():
    diffs = [_diff("Config", {"port": 80, "host": "x"}, {"port": 80})]
    result = flatten_diffs(diffs)
    keys = {r.key for r in result}
    assert "Config.host" in keys
    host = next(r for r in result if r.key == "Config.host")
    assert host.target_value is None
    assert host.changed is True


def test_missing_key_in_baseline_flattened():
    diffs = [_diff("Config", {"port": 80}, {"port": 80, "host": "y"})]
    result = flatten_diffs(diffs)
    host = next(r for r in result if r.key == "Config.host")
    assert host.baseline_value is None
    assert host.changed is True


# ---------------------------------------------------------------------------
# as_dict
# ---------------------------------------------------------------------------

def test_as_dict_contains_expected_keys(simple_diffs):
    result = flatten_diffs(simple_diffs)
    d = result[0].as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "target_value", "changed", "depth"}


# ---------------------------------------------------------------------------
# empty input
# ---------------------------------------------------------------------------

def test_empty_input_returns_empty_list():
    assert flatten_diffs([]) == []
