"""Tests for differ_transformer."""

from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_transformer import (
    TransformedDiff,
    BUILTIN_TRANSFORMS,
    transform_diffs,
)


@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="VpcId", baseline_value="vpc-abc123", target_value="vpc-abc123"),
        KeyDiff(key="SubnetId", baseline_value="subnet-AAA", target_value="subnet-aaa"),
        KeyDiff(key="BucketName", baseline_value=" my-bucket ", target_value="my-bucket"),
        KeyDiff(key="RoleArn", baseline_value=None, target_value="arn:aws:iam::123:role/R"),
        KeyDiff(key="OldKey", baseline_value="old", target_value=None),
    ]


def test_returns_transformed_diff_instances(mixed_diffs):
    result = transform_diffs(mixed_diffs, [])
    assert all(isinstance(r, TransformedDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    result = transform_diffs(mixed_diffs, [])
    assert len(result) == len(mixed_diffs)


def test_no_transforms_changed_reflects_raw_diff(mixed_diffs):
    result = transform_diffs(mixed_diffs, [])
    by_key = {r.key: r for r in result}
    assert not by_key["VpcId"].changed
    assert by_key["SubnetId"].changed


def test_lower_transform_makes_case_equal(mixed_diffs):
    result = transform_diffs(mixed_diffs, ["lower"])
    by_key = {r.key: r for r in result}
    assert not by_key["SubnetId"].changed


def test_strip_transform_removes_whitespace(mixed_diffs):
    result = transform_diffs(mixed_diffs, ["strip"])
    by_key = {r.key: r for r in result}
    assert not by_key["BucketName"].changed


def test_none_baseline_stays_none(mixed_diffs):
    result = transform_diffs(mixed_diffs, ["lower"])
    by_key = {r.key: r for r in result}
    assert by_key["RoleArn"].transformed_baseline is None
    assert by_key["RoleArn"].changed  # None != lowercased arn


def test_none_target_stays_none(mixed_diffs):
    result = transform_diffs(mixed_diffs, ["lower"])
    by_key = {r.key: r for r in result}
    assert by_key["OldKey"].transformed_target is None
    assert by_key["OldKey"].changed


def test_chained_transforms(mixed_diffs):
    result = transform_diffs(mixed_diffs, ["strip", "lower"])
    by_key = {r.key: r for r in result}
    assert not by_key["SubnetId"].changed
    assert not by_key["BucketName"].changed


def test_transforms_applied_recorded(mixed_diffs):
    result = transform_diffs(mixed_diffs, ["strip", "lower"])
    assert result[0].transforms_applied == ["strip", "lower"]


def test_remove_hyphens_transform():
    diffs = [KeyDiff(key="K", baseline_value="a-b-c", target_value="abc")]
    result = transform_diffs(diffs, ["remove_hyphens"])
    assert not result[0].changed


def test_unknown_transform_raises(mixed_diffs):
    with pytest.raises(ValueError, match="Unknown transforms"):
        transform_diffs(mixed_diffs, ["nonexistent"])


def test_extra_custom_transform():
    diffs = [KeyDiff(key="K", baseline_value="hello world", target_value="helloworld")]
    result = transform_diffs(diffs, ["squish"], extra={"squish": lambda v: v.replace(" ", "")})
    assert not result[0].changed


def test_as_dict_keys(mixed_diffs):
    result = transform_diffs(mixed_diffs, ["lower"])
    d = result[0].as_dict()
    expected_keys = {
        "key", "baseline_value", "target_value",
        "transformed_baseline", "transformed_target",
        "changed", "transforms_applied",
    }
    assert set(d.keys()) == expected_keys


def test_builtin_transforms_registered():
    for name in ("strip", "lower", "upper", "remove_hyphens", "remove_whitespace"):
        assert name in BUILTIN_TRANSFORMS
