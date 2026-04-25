"""Tests for stackdiff.differ_splitter."""
import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_splitter import SplitPartition, SplitResult, split_diffs


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="VpcId", baseline="vpc-aaa", target="vpc-bbb"),
        KeyDiff(key="SubnetId", baseline="sub-1", target="sub-1"),
        KeyDiff(key="DbEndpoint", baseline="old.db", target="new.db"),
        KeyDiff(key="BucketName", baseline=None, target="my-bucket"),
        KeyDiff(key="IamRoleArn", baseline="arn:old", target="arn:new"),
        KeyDiff(key="UnknownKey", baseline="x", target="x"),
    ]


SPEC = {
    "network": ["Vpc*", "Subnet*"],
    "database": ["Db*"],
    "storage": ["Bucket*"],
    "iam": ["Iam*"],
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_returns_split_result(mixed_diffs):
    result = split_diffs(mixed_diffs, SPEC)
    assert isinstance(result, SplitResult)


def test_partition_count_matches_spec(mixed_diffs):
    result = split_diffs(mixed_diffs, SPEC)
    assert len(result.partitions) == len(SPEC)


def test_network_partition_contains_vpc_and_subnet(mixed_diffs):
    result = split_diffs(mixed_diffs, SPEC)
    network = result.by_name("network")
    assert network is not None
    keys = [d.key for d in network.diffs]
    assert "VpcId" in keys
    assert "SubnetId" in keys


def test_database_partition_contains_db_endpoint(mixed_diffs):
    result = split_diffs(mixed_diffs, SPEC)
    db = result.by_name("database")
    assert db is not None
    assert len(db.diffs) == 1
    assert db.diffs[0].key == "DbEndpoint"


def test_storage_partition_contains_bucket(mixed_diffs):
    result = split_diffs(mixed_diffs, SPEC)
    storage = result.by_name("storage")
    assert storage is not None
    assert storage.diffs[0].key == "BucketName"


def test_iam_partition_contains_iam_role(mixed_diffs):
    result = split_diffs(mixed_diffs, SPEC)
    iam = result.by_name("iam")
    assert iam is not None
    assert iam.diffs[0].key == "IamRoleArn"


def test_unmatched_contains_unknown_key(mixed_diffs):
    result = split_diffs(mixed_diffs, SPEC)
    unmatched_keys = [d.key for d in result.unmatched]
    assert "UnknownKey" in unmatched_keys


def test_unmatched_not_in_any_partition(mixed_diffs):
    result = split_diffs(mixed_diffs, SPEC)
    all_partitioned = {
        d.key for p in result.partitions for d in p.diffs
    }
    for d in result.unmatched:
        assert d.key not in all_partitioned


def test_empty_diffs_returns_empty_partitions():
    result = split_diffs([], SPEC)
    assert result.unmatched == []
    for p in result.partitions:
        assert p.diffs == []


def test_empty_spec_all_unmatched(mixed_diffs):
    result = split_diffs(mixed_diffs, {})
    assert result.partitions == []
    assert len(result.unmatched) == len(mixed_diffs)


def test_first_matching_partition_wins():
    """A key matching two partitions should land in the first one."""
    spec = {
        "first": ["VpcId"],
        "second": ["Vpc*"],
    }
    diffs = [KeyDiff(key="VpcId", baseline="a", target="b")]
    result = split_diffs(diffs, spec)
    first = result.by_name("first")
    second = result.by_name("second")
    assert len(first.diffs) == 1
    assert len(second.diffs) == 0


def test_as_dict_structure(mixed_diffs):
    result = split_diffs(mixed_diffs, SPEC)
    d = result.as_dict()
    assert "partitions" in d
    assert "unmatched" in d
    assert isinstance(d["partitions"], list)
    assert d["partitions"][0]["name"] == "network"


def test_partition_as_dict_fields(mixed_diffs):
    result = split_diffs(mixed_diffs, SPEC)
    p_dict = result.partitions[0].as_dict()
    assert "name" in p_dict
    assert "patterns" in p_dict
    assert "keys" in p_dict
    assert "count" in p_dict


def test_by_name_missing_returns_none(mixed_diffs):
    result = split_diffs(mixed_diffs, SPEC)
    assert result.by_name("nonexistent") is None
