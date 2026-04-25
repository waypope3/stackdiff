"""Tests for stackdiff.differ_dispatcher."""
from __future__ import annotations

from typing import Optional

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_dispatcher import (
    DispatchRule,
    DispatchedDiff,
    dispatch_diffs,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _d(key: str, baseline: Optional[str], target: Optional[str]) -> KeyDiff:
    return KeyDiff(key=key, baseline_value=baseline, target_value=target)


def _echo_handler(d: KeyDiff) -> str:
    return f"echo:{d.key}"


def _upper_handler(d: KeyDiff) -> Optional[str]:
    if d.target_value is None:
        return None
    return d.target_value.upper()


@pytest.fixture()
def mixed_diffs():
    return [
        _d("VpcId", "vpc-old", "vpc-new"),
        _d("SubnetId", "subnet-1", "subnet-1"),
        _d("DbEndpoint", None, "db.example.com"),
        _d("BucketName", "my-bucket", None),
        _d("ApiUrl", "https://old.example.com", "https://new.example.com"),
    ]


# ---------------------------------------------------------------------------
# basic structure
# ---------------------------------------------------------------------------

def test_returns_dispatched_diff_instances(mixed_diffs):
    result = dispatch_diffs(mixed_diffs, [])
    assert all(isinstance(r, DispatchedDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    result = dispatch_diffs(mixed_diffs, [])
    assert len(result) == len(mixed_diffs)


def test_no_rules_handler_name_none(mixed_diffs):
    result = dispatch_diffs(mixed_diffs, [])
    assert all(r.handler_name is None for r in result)


def test_no_rules_handler_result_none(mixed_diffs):
    result = dispatch_diffs(mixed_diffs, [])
    assert all(r.handler_result is None for r in result)


# ---------------------------------------------------------------------------
# changed flag
# ---------------------------------------------------------------------------

def test_changed_flag_set_when_values_differ(mixed_diffs):
    result = dispatch_diffs(mixed_diffs, [])
    by_key = {r.key: r for r in result}
    assert by_key["VpcId"].changed is True


def test_changed_flag_clear_when_values_equal(mixed_diffs):
    result = dispatch_diffs(mixed_diffs, [])
    by_key = {r.key: r for r in result}
    assert by_key["SubnetId"].changed is False


def test_added_key_is_changed(mixed_diffs):
    result = dispatch_diffs(mixed_diffs, [])
    by_key = {r.key: r for r in result}
    assert by_key["DbEndpoint"].changed is True


def test_removed_key_is_changed(mixed_diffs):
    result = dispatch_diffs(mixed_diffs, [])
    by_key = {r.key: r for r in result}
    assert by_key["BucketName"].changed is True


# ---------------------------------------------------------------------------
# dispatch rules
# ---------------------------------------------------------------------------

def test_exact_pattern_matches(mixed_diffs):
    rules = [DispatchRule(pattern="VpcId", handler_name="vpc", handler=_echo_handler)]
    result = dispatch_diffs(mixed_diffs, rules)
    by_key = {r.key: r for r in result}
    assert by_key["VpcId"].handler_name == "vpc"


def test_glob_pattern_matches_multiple(mixed_diffs):
    rules = [DispatchRule(pattern="*Id", handler_name="id_handler", handler=_echo_handler)]
    result = dispatch_diffs(mixed_diffs, rules)
    by_key = {r.key: r for r in result}
    assert by_key["VpcId"].handler_name == "id_handler"
    assert by_key["SubnetId"].handler_name == "id_handler"


def test_non_matching_key_unhandled(mixed_diffs):
    rules = [DispatchRule(pattern="VpcId", handler_name="vpc", handler=_echo_handler)]
    result = dispatch_diffs(mixed_diffs, rules)
    by_key = {r.key: r for r in result}
    assert by_key["ApiUrl"].handler_name is None


def test_first_rule_wins():
    diffs = [_d("VpcId", "a", "b")]
    rules = [
        DispatchRule(pattern="Vpc*", handler_name="first", handler=lambda d: "first"),
        DispatchRule(pattern="VpcId", handler_name="second", handler=lambda d: "second"),
    ]
    result = dispatch_diffs(diffs, rules)
    assert result[0].handler_name == "first"
    assert result[0].handler_result == "first"


def test_handler_receives_diff_and_returns_result(mixed_diffs):
    rules = [DispatchRule(pattern="ApiUrl", handler_name="upper", handler=_upper_handler)]
    result = dispatch_diffs(mixed_diffs, rules)
    by_key = {r.key: r for r in result}
    assert by_key["ApiUrl"].handler_result == "HTTPS://NEW.EXAMPLE.COM"


def test_handler_returning_none_stored_as_none():
    diffs = [_d("BucketName", "b", None)]
    rules = [DispatchRule(pattern="BucketName", handler_name="upper", handler=_upper_handler)]
    result = dispatch_diffs(diffs, rules)
    assert result[0].handler_result is None


# ---------------------------------------------------------------------------
# as_dict / __str__
# ---------------------------------------------------------------------------

def test_as_dict_contains_expected_keys(mixed_diffs):
    result = dispatch_diffs(mixed_diffs, [])
    d = result[0].as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "target_value", "changed", "handler_name", "handler_result"}


def test_str_changed_marker():
    d = DispatchedDiff("VpcId", "old", "new", True, None, None)
    assert str(d).startswith("~")


def test_str_unchanged_marker():
    d = DispatchedDiff("SubnetId", "same", "same", False, None, None)
    assert str(d).startswith("=")


def test_str_includes_handler_name():
    d = DispatchedDiff("VpcId", "old", "new", True, "vpc", "result")
    assert "[vpc]" in str(d)


def test_str_includes_handler_result():
    d = DispatchedDiff("VpcId", "old", "new", True, "vpc", "processed")
    assert "processed" in str(d)
