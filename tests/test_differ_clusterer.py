"""Tests for stackdiff.differ_clusterer."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_clusterer import ClusteredDiff, ClusterResult, cluster_diffs


@pytest.fixture()
def mixed_diffs() -> list:
    return [
        KeyDiff(key="VpcId", baseline_value="vpc-old", target_value="vpc-new"),
        KeyDiff(key="SubnetId", baseline_value="subnet-1", target_value="subnet-1"),
        KeyDiff(key="DbEndpoint", baseline_value="db.old.local", target_value="db.new.local"),
        KeyDiff(key="BucketName", baseline_value=None, target_value="my-bucket"),
        KeyDiff(key="AppVersion", baseline_value="1.0", target_value="2.0"),
    ]


PATTERNS = {
    "network": ["Vpc*", "Subnet*"],
    "database": ["Db*", "*Endpoint*"],
    "storage": ["Bucket*", "*bucket*"],
}


def test_returns_cluster_result(mixed_diffs):
    result = cluster_diffs(mixed_diffs, PATTERNS)
    assert isinstance(result, ClusterResult)


def test_diffs_length_matches_input(mixed_diffs):
    result = cluster_diffs(mixed_diffs, PATTERNS)
    assert len(result.diffs) == len(mixed_diffs)


def test_all_diffs_are_clustered_diff_instances(mixed_diffs):
    result = cluster_diffs(mixed_diffs, PATTERNS)
    assert all(isinstance(d, ClusteredDiff) for d in result.diffs)


def test_network_cluster_contains_vpc(mixed_diffs):
    result = cluster_diffs(mixed_diffs, PATTERNS)
    keys = [d.key for d in result.clusters.get("network", [])]
    assert "VpcId" in keys


def test_network_cluster_contains_subnet(mixed_diffs):
    result = cluster_diffs(mixed_diffs, PATTERNS)
    keys = [d.key for d in result.clusters.get("network", [])]
    assert "SubnetId" in keys


def test_database_cluster_contains_db_endpoint(mixed_diffs):
    result = cluster_diffs(mixed_diffs, PATTERNS)
    keys = [d.key for d in result.clusters.get("database", [])]
    assert "DbEndpoint" in keys


def test_storage_cluster_contains_bucket(mixed_diffs):
    result = cluster_diffs(mixed_diffs, PATTERNS)
    keys = [d.key for d in result.clusters.get("storage", [])]
    assert "BucketName" in keys


def test_unclustered_contains_app_version(mixed_diffs):
    result = cluster_diffs(mixed_diffs, PATTERNS)
    keys = [d.key for d in result.clusters.get("unclustered", [])]
    assert "AppVersion" in keys


def test_changed_flag_set_when_values_differ(mixed_diffs):
    result = cluster_diffs(mixed_diffs, PATTERNS)
    vpc = next(d for d in result.diffs if d.key == "VpcId")
    assert vpc.changed is True


def test_changed_flag_clear_when_values_equal(mixed_diffs):
    result = cluster_diffs(mixed_diffs, PATTERNS)
    subnet = next(d for d in result.diffs if d.key == "SubnetId")
    assert subnet.changed is False


def test_empty_patterns_all_unclustered(mixed_diffs):
    result = cluster_diffs(mixed_diffs, {})
    assert "unclustered" in result.clusters
    assert len(result.clusters["unclustered"]) == len(mixed_diffs)


def test_empty_diffs_returns_empty_result():
    result = cluster_diffs([], PATTERNS)
    assert result.diffs == []
    # named clusters with no members are stripped
    assert all(len(v) > 0 for v in result.clusters.values())


def test_as_dict_contains_expected_keys(mixed_diffs):
    result = cluster_diffs(mixed_diffs, PATTERNS)
    d = result.as_dict()
    assert "diffs" in d
    assert "clusters" in d


def test_clustered_diff_as_dict_shape(mixed_diffs):
    result = cluster_diffs(mixed_diffs, PATTERNS)
    entry = result.diffs[0].as_dict()
    assert set(entry.keys()) == {"key", "baseline_value", "target_value", "changed", "cluster"}
