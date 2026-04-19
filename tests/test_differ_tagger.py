import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_tagger import tag_diffs, TaggedDiff


@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="DatabasePassword", baseline_value="old", target_value="new"),
        KeyDiff(key="BucketName", baseline_value="bucket", target_value="bucket"),
        KeyDiff(key="ApiEndpoint", baseline_value=None, target_value="https://x"),
        KeyDiff(key="OldParam", baseline_value="v", target_value=None),
    ]


RULES = {
    "sensitive": ["*Password", "*Secret"],
    "network": ["*Endpoint", "*Url"],
    "storage": ["Bucket*"],
}


def test_returns_tagged_diffs(mixed_diffs):
    result = tag_diffs(mixed_diffs, RULES)
    assert len(result) == 4
    assert all(isinstance(r, TaggedDiff) for r in result)


def test_sensitive_tag_applied(mixed_diffs):
    result = tag_diffs(mixed_diffs, RULES)
    pw = next(r for r in result if r.key == "DatabasePassword")
    assert "sensitive" in pw.tags


def test_network_tag_applied(mixed_diffs):
    result = tag_diffs(mixed_diffs, RULES)
    ep = next(r for r in result if r.key == "ApiEndpoint")
    assert "network" in ep.tags


def test_storage_tag_applied(mixed_diffs):
    result = tag_diffs(mixed_diffs, RULES)
    b = next(r for r in result if r.key == "BucketName")
    assert "storage" in b.tags


def test_no_matching_tag(mixed_diffs):
    result = tag_diffs(mixed_diffs, RULES)
    old = next(r for r in result if r.key == "OldParam")
    assert old.tags == []


def test_status_changed(mixed_diffs):
    result = tag_diffs(mixed_diffs, RULES)
    pw = next(r for r in result if r.key == "DatabasePassword")
    assert pw.status == "changed"


def test_status_unchanged(mixed_diffs):
    result = tag_diffs(mixed_diffs, RULES)
    b = next(r for r in result if r.key == "BucketName")
    assert b.status == "unchanged"


def test_status_added(mixed_diffs):
    result = tag_diffs(mixed_diffs, RULES)
    ep = next(r for r in result if r.key == "ApiEndpoint")
    assert ep.status == "added"


def test_status_removed(mixed_diffs):
    result = tag_diffs(mixed_diffs, RULES)
    old = next(r for r in result if r.key == "OldParam")
    assert old.status == "removed"


def test_as_dict_keys(mixed_diffs):
    result = tag_diffs(mixed_diffs, RULES)
    d = result[0].as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "target_value", "status", "tags"}


def test_empty_rules(mixed_diffs):
    result = tag_diffs(mixed_diffs, {})
    assert all(r.tags == [] for r in result)


def test_empty_diffs():
    assert tag_diffs([], RULES) == []


def test_tags_sorted(mixed_diffs):
    rules = {"z_tag": ["*"], "a_tag": ["*"]}
    result = tag_diffs(mixed_diffs, rules)
    for r in result:
        assert r.tags == sorted(r.tags)
