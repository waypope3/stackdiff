"""Tests for stackdiff.differ_linker."""
import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_linker import LinkedDiff, link_diffs, _is_cross_stack_ref, _find_linked_stacks


@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="VpcId", baseline_value="vpc-aaa", target_value="vpc-bbb"),
        KeyDiff(key="DbEndpoint", baseline_value="db.example.com", target_value="db.example.com"),
        KeyDiff(key="BucketArn", baseline_value="arn:aws:s3:::my-bucket", target_value="arn:aws:s3:::new-bucket"),
        KeyDiff(key="NewKey", baseline_value=None, target_value="some-value"),
    ]


ALL_STACKS = {
    "networking": {"VpcId": "vpc-aaa", "SubnetId": "subnet-123"},
    "database": {"DbEndpoint": "db.example.com", "DbPort": "5432"},
    "storage": {"BucketArn": "arn:aws:s3:::my-bucket"},
}


def test_returns_linked_diff_instances(mixed_diffs):
    result = link_diffs(mixed_diffs, ALL_STACKS)
    assert all(isinstance(r, LinkedDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    result = link_diffs(mixed_diffs, ALL_STACKS)
    assert len(result) == len(mixed_diffs)


def test_changed_flag_set_when_values_differ(mixed_diffs):
    result = link_diffs(mixed_diffs, ALL_STACKS)
    vpc = next(r for r in result if r.key == "VpcId")
    assert vpc.changed is True


def test_changed_flag_clear_when_values_equal(mixed_diffs):
    result = link_diffs(mixed_diffs, ALL_STACKS)
    db = next(r for r in result if r.key == "DbEndpoint")
    assert db.changed is False


def test_linked_stacks_populated_for_shared_key(mixed_diffs):
    result = link_diffs(mixed_diffs, ALL_STACKS)
    vpc = next(r for r in result if r.key == "VpcId")
    assert "networking" in vpc.linked_stacks


def test_linked_stacks_excludes_current_stack(mixed_diffs):
    result = link_diffs(mixed_diffs, ALL_STACKS, current_stack="networking")
    vpc = next(r for r in result if r.key == "VpcId")
    assert "networking" not in vpc.linked_stacks


def test_is_cross_stack_ref_arn():
    assert _is_cross_stack_ref("arn:aws:s3:::my-bucket") is True


def test_is_cross_stack_ref_fn_import():
    assert _is_cross_stack_ref("Fn::ImportValue") is True


def test_is_cross_stack_ref_double_colon():
    assert _is_cross_stack_ref("some::export") is True


def test_is_cross_stack_ref_plain_string():
    assert _is_cross_stack_ref("vpc-aaa") is False


def test_is_cross_stack_ref_none():
    assert _is_cross_stack_ref(None) is False


def test_arn_value_marked_as_cross_stack_ref(mixed_diffs):
    result = link_diffs(mixed_diffs, ALL_STACKS)
    bucket = next(r for r in result if r.key == "BucketArn")
    assert bucket.is_cross_stack_ref is True


def test_plain_value_not_marked_as_cross_stack_ref(mixed_diffs):
    result = link_diffs(mixed_diffs, ALL_STACKS)
    vpc = next(r for r in result if r.key == "VpcId")
    assert vpc.is_cross_stack_ref is False


def test_as_dict_has_expected_keys(mixed_diffs):
    result = link_diffs(mixed_diffs, ALL_STACKS)
    d = result[0].as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "target_value", "changed", "linked_stacks", "is_cross_stack_ref"}


def test_str_contains_key(mixed_diffs):
    result = link_diffs(mixed_diffs, ALL_STACKS)
    assert "VpcId" in str(result[0])


def test_empty_diffs():
    result = link_diffs([], ALL_STACKS)
    assert result == []
