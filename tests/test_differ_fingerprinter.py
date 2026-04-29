"""Tests for stackdiff.differ_fingerprinter."""
import hashlib
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_fingerprinter import (
    FingerprintedDiff,
    fingerprint_diffs,
    stack_fingerprint,
    _sha256,
    _combined,
)


@pytest.fixture
def mixed_diffs():
    return [
        KeyDiff(key="VpcId", baseline_value="vpc-aaa", target_value="vpc-bbb"),
        KeyDiff(key="SubnetId", baseline_value="subnet-1", target_value="subnet-1"),
        KeyDiff(key="NewKey", baseline_value=None, target_value="new-val"),
        KeyDiff(key="OldKey", baseline_value="old-val", target_value=None),
    ]


def test_returns_fingerprinted_diff_instances(mixed_diffs):
    result = fingerprint_diffs(mixed_diffs)
    assert all(isinstance(d, FingerprintedDiff) for d in result)


def test_same_length_as_input(mixed_diffs):
    result = fingerprint_diffs(mixed_diffs)
    assert len(result) == len(mixed_diffs)


def test_changed_flag_set_when_values_differ(mixed_diffs):
    result = fingerprint_diffs(mixed_diffs)
    vpc = next(d for d in result if d.key == "VpcId")
    assert vpc.changed is True


def test_changed_flag_clear_when_values_equal(mixed_diffs):
    result = fingerprint_diffs(mixed_diffs)
    subnet = next(d for d in result if d.key == "SubnetId")
    assert subnet.changed is False


def test_added_key_is_changed(mixed_diffs):
    result = fingerprint_diffs(mixed_diffs)
    new = next(d for d in result if d.key == "NewKey")
    assert new.changed is True
    assert new.baseline_fingerprint is None


def test_removed_key_is_changed(mixed_diffs):
    result = fingerprint_diffs(mixed_diffs)
    old = next(d for d in result if d.key == "OldKey")
    assert old.changed is True
    assert old.target_fingerprint is None


def test_sha256_helper_none_returns_none():
    assert _sha256(None) is None


def test_sha256_helper_string():
    expected = hashlib.sha256(b"hello").hexdigest()
    assert _sha256("hello") == expected


def test_combined_fingerprint_deterministic():
    fp1 = _combined("key", "a", "b")
    fp2 = _combined("key", "a", "b")
    assert fp1 == fp2


def test_combined_fingerprint_differs_on_value_change():
    fp1 = _combined("key", "a", "b")
    fp2 = _combined("key", "a", "c")
    assert fp1 != fp2


def test_stack_fingerprint_is_string(mixed_diffs):
    fps = fingerprint_diffs(mixed_diffs)
    sfp = stack_fingerprint(fps)
    assert isinstance(sfp, str) and len(sfp) == 64


def test_stack_fingerprint_changes_when_diffs_change():
    d1 = [KeyDiff(key="K", baseline_value="a", target_value="b")]
    d2 = [KeyDiff(key="K", baseline_value="a", target_value="c")]
    assert stack_fingerprint(fingerprint_diffs(d1)) != stack_fingerprint(fingerprint_diffs(d2))


def test_as_dict_keys(mixed_diffs):
    result = fingerprint_diffs(mixed_diffs)
    d = result[0].as_dict()
    expected_keys = {
        "key", "baseline_value", "target_value", "changed",
        "baseline_fingerprint", "target_fingerprint", "combined_fingerprint",
    }
    assert expected_keys == set(d.keys())


def test_str_representation(mixed_diffs):
    result = fingerprint_diffs(mixed_diffs)
    s = str(result[0])
    assert "VpcId" in s
    assert "fp=" in s
