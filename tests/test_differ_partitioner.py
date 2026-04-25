"""Tests for stackdiff.differ_partitioner."""
import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_partitioner import (
    PartitionResult,
    PartitionedDiff,
    partition_diffs,
)


@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="VpcId", baseline_value="vpc-aaa", target_value="vpc-bbb"),
        KeyDiff(key="SubnetId", baseline_value="subnet-1", target_value="subnet-1"),
        KeyDiff(key="DbEndpoint", baseline_value="old.db", target_value="new.db"),
        KeyDiff(key="BucketName", baseline_value="bkt", target_value="bkt"),
        KeyDiff(key="LambdaArn", baseline_value=None, target_value="arn:aws:lambda:x"),
    ]


PATTERNS = {
    "network": ["vpc*", "subnet*"],
    "database": ["db*"],
    "storage": ["bucket*"],
}


def test_returns_partition_result(mixed_diffs):
    result = partition_diffs(mixed_diffs, PATTERNS)
    assert isinstance(result, PartitionResult)


def test_all_diffs_length(mixed_diffs):
    result = partition_diffs(mixed_diffs, PATTERNS)
    assert len(result.all_diffs()) == len(mixed_diffs)


def test_network_bucket(mixed_diffs):
    result = partition_diffs(mixed_diffs, PATTERNS)
    keys = [d.key for d in result.buckets["network"]]
    assert "VpcId" in keys
    assert "SubnetId" in keys


def test_database_bucket(mixed_diffs):
    result = partition_diffs(mixed_diffs, PATTERNS)
    keys = [d.key for d in result.buckets["database"]]
    assert "DbEndpoint" in keys


def test_fallback_bucket(mixed_diffs):
    result = partition_diffs(mixed_diffs, PATTERNS, fallback="misc")
    keys = [d.key for d in result.buckets["misc"]]
    assert "LambdaArn" in keys


def test_changed_flag_set_when_values_differ(mixed_diffs):
    result = partition_diffs(mixed_diffs, PATTERNS)
    vpc = next(d for d in result.all_diffs() if d.key == "VpcId")
    assert vpc.changed is True


def test_changed_flag_clear_when_values_equal(mixed_diffs):
    result = partition_diffs(mixed_diffs, PATTERNS)
    subnet = next(d for d in result.all_diffs() if d.key == "SubnetId")
    assert subnet.changed is False


def test_changed_in_returns_only_changed(mixed_diffs):
    result = partition_diffs(mixed_diffs, PATTERNS)
    changed = result.changed_in("network")
    assert all(d.changed for d in changed)
    assert any(d.key == "VpcId" for d in changed)


def test_predicate_overrides_patterns(mixed_diffs):
    result = partition_diffs(mixed_diffs, PATTERNS, predicate=lambda _: "custom")
    assert set(result.buckets.keys()) == {"custom"}
    assert len(result.buckets["custom"]) == len(mixed_diffs)


def test_as_dict_structure(mixed_diffs):
    result = partition_diffs(mixed_diffs, PATTERNS)
    d = result.as_dict()
    assert isinstance(d, dict)
    for bucket_list in d.values():
        for entry in bucket_list:
            assert "key" in entry
            assert "bucket" in entry
            assert "changed" in entry


def test_partitioned_diff_as_dict():
    pd = PartitionedDiff(
        key="Foo", baseline_value="a", target_value="b", changed=True, bucket="test"
    )
    d = pd.as_dict()
    assert d["key"] == "Foo"
    assert d["bucket"] == "test"
    assert d["changed"] is True


def test_empty_diffs():
    result = partition_diffs([], PATTERNS)
    assert result.all_diffs() == []
    assert result.buckets == {}
