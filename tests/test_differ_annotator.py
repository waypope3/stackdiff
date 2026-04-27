"""Tests for stackdiff.differ_annotator."""
from __future__ import annotations

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.differ_annotator import AnnotatedDiff2, annotate_diffs2


@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="VpcId", baseline_value="vpc-aaa", target_value="vpc-bbb"),
        KeyDiff(key="DbEndpoint", baseline_value=None, target_value="db.example.com"),
        KeyDiff(key="BucketArn", baseline_value="arn:aws:s3:::old", target_value=None),
        KeyDiff(key="ApiUrl", baseline_value="https://old.example.com", target_value="https://new.example.com"),
        KeyDiff(key="SomeStableKey", baseline_value="same", target_value="same"),
    ]


def test_returns_annotated_diff2_instances(mixed_diffs):
    result = annotate_diffs2(mixed_diffs)
    assert all(isinstance(r, AnnotatedDiff2) for r in result)


def test_same_length_as_input(mixed_diffs):
    result = annotate_diffs2(mixed_diffs)
    assert len(result) == len(mixed_diffs)


def test_changed_flag_set_when_values_differ(mixed_diffs):
    result = annotate_diffs2(mixed_diffs)
    changed = {r.key: r.changed for r in result}
    assert changed["VpcId"] is True
    assert changed["ApiUrl"] is True


def test_changed_flag_clear_when_values_equal(mixed_diffs):
    result = annotate_diffs2(mixed_diffs)
    stable = next(r for r in result if r.key == "SomeStableKey")
    assert stable.changed is False


def test_added_key_marked_changed(mixed_diffs):
    result = annotate_diffs2(mixed_diffs)
    added = next(r for r in result if r.key == "DbEndpoint")
    assert added.changed is True
    assert "added" in added.notes


def test_removed_key_marked_changed(mixed_diffs):
    result = annotate_diffs2(mixed_diffs)
    removed = next(r for r in result if r.key == "BucketArn")
    assert removed.changed is True
    assert "removed" in removed.notes


def test_domain_network_inferred_for_vpc(mixed_diffs):
    result = annotate_diffs2(mixed_diffs)
    vpc = next(r for r in result if r.key == "VpcId")
    assert vpc.domain == "network"


def test_domain_database_inferred_for_db_endpoint(mixed_diffs):
    result = annotate_diffs2(mixed_diffs)
    db = next(r for r in result if r.key == "DbEndpoint")
    assert db.domain == "database"


def test_value_hint_arn_detected(mixed_diffs):
    result = annotate_diffs2(mixed_diffs)
    arn_diff = next(r for r in result if r.key == "BucketArn")
    assert arn_diff.value_hint == "arn"


def test_value_hint_url_detected(mixed_diffs):
    result = annotate_diffs2(mixed_diffs)
    url_diff = next(r for r in result if r.key == "ApiUrl")
    assert url_diff.value_hint == "url"


def test_no_hint_for_plain_value():
    diffs = [KeyDiff(key="PlainKey", baseline_value="foo", target_value="bar")]
    result = annotate_diffs2(diffs)
    assert result[0].value_hint is None


def test_as_dict_contains_expected_keys(mixed_diffs):
    result = annotate_diffs2(mixed_diffs)
    d = result[0].as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "target_value", "changed", "domain", "value_hint", "notes"}


def test_str_contains_key(mixed_diffs):
    result = annotate_diffs2(mixed_diffs)
    assert "VpcId" in str(result[0])


def test_empty_list_returns_empty():
    assert annotate_diffs2([]) == []
