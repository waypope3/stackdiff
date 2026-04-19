"""Tests for differ_classifier."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_classifier import (
    classify_diffs,
    group_by_category,
    ClassifiedDiff,
    _classify,
)


@pytest.fixture
def mixed_diffs():
    return [
        KeyDiff(key="VpcId", baseline="vpc-aaa", current="vpc-bbb", changed=True),
        KeyDiff(key="BucketName", baseline="my-bucket", current="my-bucket", changed=False),
        KeyDiff(key="DbEndpoint", baseline="old.rds", current="new.rds", changed=True),
        KeyDiff(key="IamRoleArn", baseline="arn:aws:iam::1", current="arn:aws:iam::2", changed=True),
        KeyDiff(key="AppVersion", baseline="1.0", current="2.0", changed=True),
    ]


def test_classify_network():
    assert _classify("VpcId") == "network"


def test_classify_storage():
    assert _classify("BucketName") == "storage"


def test_classify_database():
    assert _classify("DbEndpoint") == "database"


def test_classify_iam():
    assert _classify("IamRoleArn") == "iam"


def test_classify_general():
    assert _classify("AppVersion") == "general"


def test_classify_diffs_length(mixed_diffs):
    result = classify_diffs(mixed_diffs)
    assert len(result) == len(mixed_diffs)


def test_classify_diffs_types(mixed_diffs):
    result = classify_diffs(mixed_diffs)
    assert all(isinstance(r, ClassifiedDiff) for r in result)


def test_classify_diffs_changed_flag(mixed_diffs):
    result = classify_diffs(mixed_diffs)
    changed = {r.key: r.changed for r in result}
    assert changed["VpcId"] is True
    assert changed["BucketName"] is False


def test_group_by_category(mixed_diffs):
    classified = classify_diffs(mixed_diffs)
    grouped = group_by_category(classified)
    assert "network" in grouped
    assert "storage" in grouped
    assert any(i.key == "VpcId" for i in grouped["network"])


def test_as_dict(mixed_diffs):
    item = classify_diffs(mixed_diffs)[0]
    d = item.as_dict()
    assert set(d.keys()) == {"key", "baseline", "current", "changed", "category"}
