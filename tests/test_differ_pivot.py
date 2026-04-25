"""Tests for stackdiff.differ_pivot."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_pivot import PivotBucket, PivotResult, pivot_diffs


@pytest.fixture()
def mixed_diffs() -> list[KeyDiff]:
    return [
        KeyDiff(key="VpcId", baseline_value="vpc-aaa", target_value="vpc-bbb"),
        KeyDiff(key="SubnetId", baseline_value=None, target_value="subnet-111"),
        KeyDiff(key="DbEndpoint", baseline_value="db.old", target_value=None),
        KeyDiff(key="Region", baseline_value="us-east-1", target_value="us-east-1"),
        KeyDiff(key="BucketArn", baseline_value="arn:aws:s3:::b", target_value="arn:aws:s3:::b"),
    ]


def test_returns_pivot_result(mixed_diffs):
    result = pivot_diffs(mixed_diffs, "status")
    assert isinstance(result, PivotResult)


def test_dimension_stored(mixed_diffs):
    result = pivot_diffs(mixed_diffs, "status")
    assert result.dimension == "status"


def test_status_changed_bucket(mixed_diffs):
    result = pivot_diffs(mixed_diffs, "status")
    assert "changed" in result.buckets
    assert any(d.key == "VpcId" for d in result.buckets["changed"].diffs)


def test_status_added_bucket(mixed_diffs):
    result = pivot_diffs(mixed_diffs, "status")
    assert "added" in result.buckets
    assert result.buckets["added"].diffs[0].key == "SubnetId"


def test_status_removed_bucket(mixed_diffs):
    result = pivot_diffs(mixed_diffs, "status")
    assert "removed" in result.buckets
    assert result.buckets["removed"].diffs[0].key == "DbEndpoint"


def test_status_unchanged_bucket(mixed_diffs):
    result = pivot_diffs(mixed_diffs, "status")
    assert "unchanged" in result.buckets
    keys = [d.key for d in result.buckets["unchanged"].diffs]
    assert "Region" in keys


def test_prefix_dimension(mixed_diffs):
    result = pivot_diffs(mixed_diffs, "prefix")
    assert result.dimension == "prefix"
    # VpcId -> "vpc", SubnetId -> "subnetid" (no underscore) -> "other"
    assert "vpc" in result.buckets


def test_value_type_arn(mixed_diffs):
    result = pivot_diffs(mixed_diffs, "value_type")
    assert "arn" in result.buckets
    assert any(d.key == "BucketArn" for d in result.buckets["arn"].diffs)


def test_value_type_string(mixed_diffs):
    result = pivot_diffs(mixed_diffs, "value_type")
    assert "string" in result.buckets


def test_unknown_dimension_raises(mixed_diffs):
    with pytest.raises(ValueError, match="Unknown pivot dimension"):
        pivot_diffs(mixed_diffs, "bogus")  # type: ignore[arg-type]


def test_empty_input():
    result = pivot_diffs([], "status")
    assert result.buckets == {}


def test_bucket_as_dict(mixed_diffs):
    result = pivot_diffs(mixed_diffs, "status")
    d = result.buckets["changed"].as_dict()
    assert d["label"] == "changed"
    assert "keys" in d
    assert d["count"] >= 1


def test_result_as_dict(mixed_diffs):
    result = pivot_diffs(mixed_diffs, "status")
    d = result.as_dict()
    assert d["dimension"] == "status"
    assert "buckets" in d
