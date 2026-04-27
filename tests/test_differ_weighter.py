"""Tests for stackdiff.differ_weighter."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_weighter import (
    WeightedDiff,
    _change_type,
    _resolve_weight,
    weight_diffs,
)


@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="DbPassword", baseline_value="old", target_value="new"),
        KeyDiff(key="VpcId", baseline_value="vpc-1", target_value="vpc-1"),
        KeyDiff(key="ApiToken", baseline_value=None, target_value="tok-abc"),
        KeyDiff(key="BucketArn", baseline_value="arn:aws:s3:::b", target_value=None),
        KeyDiff(key="PlainKey", baseline_value="a", target_value="b"),
    ]


# --- _change_type ---

def test_change_type_changed():
    d = KeyDiff(key="k", baseline_value="a", target_value="b")
    assert _change_type(d) == "changed"


def test_change_type_added():
    d = KeyDiff(key="k", baseline_value=None, target_value="b")
    assert _change_type(d) == "added"


def test_change_type_removed():
    d = KeyDiff(key="k", baseline_value="a", target_value=None)
    assert _change_type(d) == "removed"


def test_change_type_unchanged():
    d = KeyDiff(key="k", baseline_value="x", target_value="x")
    assert _change_type(d) == "unchanged"


# --- _resolve_weight ---

def test_resolve_weight_matches_pattern():
    rules = [("*password*", 3.0)]
    w, matched = _resolve_weight("DbPassword", rules, 1.0)
    assert w == pytest.approx(3.0)
    assert matched == "*password*"


def test_resolve_weight_no_match_returns_base():
    rules = [("*password*", 3.0)]
    w, matched = _resolve_weight("VpcId", rules, 1.0)
    assert w == pytest.approx(1.0)
    assert matched is None


def test_resolve_weight_case_insensitive():
    rules = [("*TOKEN*", 2.5)]
    w, matched = _resolve_weight("apitoken", rules, 1.0)
    assert w == pytest.approx(2.5)
    assert matched == "*TOKEN*"


# --- weight_diffs ---

def test_returns_weighted_diff_instances(mixed_diffs):
    result = weight_diffs(mixed_diffs)
    assert all(isinstance(r, WeightedDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    assert len(weight_diffs(mixed_diffs)) == len(mixed_diffs)


def test_unchanged_key_has_zero_weight(mixed_diffs):
    result = weight_diffs(mixed_diffs)
    vpc = next(r for r in result if r.key == "VpcId")
    assert vpc.weight == 0.0
    assert not vpc.changed


def test_password_key_has_high_weight(mixed_diffs):
    result = weight_diffs(mixed_diffs)
    pwd = next(r for r in result if r.key == "DbPassword")
    assert pwd.weight > 1.0
    assert pwd.changed


def test_removed_key_uses_removed_multiplier():
    diffs = [KeyDiff(key="BucketArn", baseline_value="arn:x", target_value=None)]
    result = weight_diffs(diffs)
    assert result[0].changed
    # arn pattern weight=1.5, removed multiplier=1.2 => 1.8
    assert result[0].weight == pytest.approx(1.8, rel=1e-3)


def test_added_key_uses_added_multiplier():
    diffs = [KeyDiff(key="ApiToken", baseline_value=None, target_value="tok")]
    result = weight_diffs(diffs)
    # token pattern weight=2.5, added multiplier=0.8 => 2.0
    assert result[0].weight == pytest.approx(2.0, rel=1e-3)


def test_custom_rules_override_defaults():
    custom_rules = [("*vpc*", 5.0)]
    diffs = [KeyDiff(key="VpcId", baseline_value="a", target_value="b")]
    result = weight_diffs(diffs, rules=custom_rules)
    assert result[0].weight == pytest.approx(5.0)
    assert result[0].matched_rule == "*vpc*"


def test_as_dict_contains_expected_keys(mixed_diffs):
    result = weight_diffs(mixed_diffs)
    d = result[0].as_dict()
    assert {"key", "baseline_value", "target_value", "changed", "weight", "matched_rule"} == set(d.keys())


def test_empty_list_returns_empty():
    assert weight_diffs([]) == []
