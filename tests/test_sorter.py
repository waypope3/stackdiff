"""Tests for stackdiff.sorter."""
import pytest
from stackdiff.sorter import SortOrder, sort_keys


@pytest.fixture()
def sample_diff():
    return {
        "ZoneId": {"status": "unchanged", "baseline": "Z1", "target": "Z1"},
        "BucketName": {"status": "changed", "baseline": "old", "target": "new"},
        "ApiUrl": {"status": "added", "baseline": None, "target": "https://x"},
        "LegacyKey": {"status": "removed", "baseline": "v", "target": None},
    }


def test_alpha_order(sample_diff):
    result = sort_keys(sample_diff, SortOrder.ALPHA)
    assert list(result.keys()) == ["ApiUrl", "BucketName", "LegacyKey", "ZoneId"]


def test_alpha_desc_order(sample_diff):
    result = sort_keys(sample_diff, SortOrder.ALPHA_DESC)
    assert list(result.keys()) == ["ZoneId", "LegacyKey", "BucketName", "ApiUrl"]


def test_changed_first_order(sample_diff):
    result = sort_keys(sample_diff, SortOrder.CHANGED_FIRST)
    keys = list(result.keys())
    changed = {"ApiUrl", "BucketName", "LegacyKey"}
    unchanged = {"ZoneId"}
    changed_positions = [i for i, k in enumerate(keys) if k in changed]
    unchanged_positions = [i for i, k in enumerate(keys) if k in unchanged]
    assert max(changed_positions) < min(unchanged_positions)


def test_unchanged_first_order(sample_diff):
    result = sort_keys(sample_diff, SortOrder.UNCHANGED_FIRST)
    keys = list(result.keys())
    assert keys[0] == "ZoneId"


def test_changed_first_secondary_alpha(sample_diff):
    result = sort_keys(sample_diff, SortOrder.CHANGED_FIRST)
    changed_keys = [k for k, v in result.items() if v["status"] != "unchanged"]
    assert changed_keys == sorted(changed_keys)


def test_empty_diff():
    assert sort_keys({}, SortOrder.ALPHA) == {}


def test_default_order_is_alpha(sample_diff):
    assert sort_keys(sample_diff) == sort_keys(sample_diff, SortOrder.ALPHA)
