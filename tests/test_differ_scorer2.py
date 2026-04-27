"""Tests for differ_scorer2: extended weighted scoring."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_scorer2 import (
    ExtendedScore,
    WeightedScore,
    _infer_domain,
    score_diffs_extended,
)


@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="VpcId", baseline="vpc-old", target="vpc-new"),
        KeyDiff(key="DbEndpoint", baseline="old.rds", target="old.rds"),
        KeyDiff(key="BucketName", baseline="bucket-a", target="bucket-b"),
        KeyDiff(key="InstanceType", baseline="t3.micro", target="t3.micro"),
        KeyDiff(key="RoleArn", baseline="arn:old", target="arn:new"),
        KeyDiff(key="PlainKey", baseline="x", target="y"),
    ]


def test_returns_extended_score(mixed_diffs):
    result = score_diffs_extended(mixed_diffs)
    assert isinstance(result, ExtendedScore)


def test_entries_length_matches_input(mixed_diffs):
    result = score_diffs_extended(mixed_diffs)
    assert len(result.entries) == len(mixed_diffs)


def test_all_entries_are_weighted_score(mixed_diffs):
    result = score_diffs_extended(mixed_diffs)
    assert all(isinstance(e, WeightedScore) for e in result.entries)


def test_infer_domain_network():
    assert _infer_domain("VpcId") == "network"


def test_infer_domain_database():
    assert _infer_domain("DbEndpoint") == "database"


def test_infer_domain_storage():
    assert _infer_domain("BucketName") == "storage"


def test_infer_domain_iam():
    assert _infer_domain("RoleArn") == "iam"


def test_infer_domain_default():
    assert _infer_domain("SomeRandomKey") == "default"


def test_changed_flag_set_when_values_differ(mixed_diffs):
    result = score_diffs_extended(mixed_diffs)
    vpc_entry = next(e for e in result.entries if e.key == "VpcId")
    assert vpc_entry.changed is True


def test_changed_flag_clear_when_values_equal(mixed_diffs):
    result = score_diffs_extended(mixed_diffs)
    db_entry = next(e for e in result.entries if e.key == "DbEndpoint")
    assert db_entry.changed is False


def test_unchanged_entry_has_zero_impact(mixed_diffs):
    result = score_diffs_extended(mixed_diffs)
    db_entry = next(e for e in result.entries if e.key == "DbEndpoint")
    assert db_entry.weighted_impact == 0.0


def test_changed_entry_has_nonzero_impact(mixed_diffs):
    result = score_diffs_extended(mixed_diffs)
    vpc_entry = next(e for e in result.entries if e.key == "VpcId")
    assert vpc_entry.weighted_impact > 0.0


def test_iam_weight_higher_than_default(mixed_diffs):
    result = score_diffs_extended(mixed_diffs)
    iam_entry = next(e for e in result.entries if e.key == "RoleArn")
    default_entry = next(e for e in result.entries if e.key == "PlainKey")
    assert iam_entry.weight > default_entry.weight


def test_total_weight_is_sum_of_entry_weights(mixed_diffs):
    result = score_diffs_extended(mixed_diffs)
    expected = sum(e.weight for e in result.entries)
    assert abs(result.total_weight - expected) < 1e-9


def test_impact_weight_is_sum_of_impacts(mixed_diffs):
    result = score_diffs_extended(mixed_diffs)
    expected = sum(e.weighted_impact for e in result.entries)
    assert abs(result.impact_weight - expected) < 1e-9


def test_impact_ratio_between_zero_and_one(mixed_diffs):
    result = score_diffs_extended(mixed_diffs)
    assert 0.0 <= result.impact_ratio <= 1.0


def test_empty_list_returns_zero_score():
    result = score_diffs_extended([])
    assert result.total_weight == 0.0
    assert result.impact_weight == 0.0
    assert result.impact_ratio == 0.0


def test_custom_domain_weights_applied():
    diffs = [KeyDiff(key="VpcId", baseline="a", target="b")]
    result = score_diffs_extended(diffs, domain_weights={"network": 99.0})
    vpc_entry = result.entries[0]
    assert vpc_entry.weight == 99.0


def test_as_dict_contains_required_keys(mixed_diffs):
    result = score_diffs_extended(mixed_diffs)
    d = result.as_dict()
    assert {"entries", "total_weight", "impact_weight", "impact_ratio"} <= d.keys()


def test_str_contains_percentage(mixed_diffs):
    result = score_diffs_extended(mixed_diffs)
    assert "%" in str(result)
