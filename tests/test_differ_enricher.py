"""Tests for stackdiff.differ_enricher."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_enricher import (
    EnrichedDiff,
    _infer_value_type,
    _infer_key_domain,
    enrich_diffs,
)


# ---------------------------------------------------------------------------
# _infer_value_type
# ---------------------------------------------------------------------------

def test_value_type_arn():
    assert _infer_value_type("arn:aws:iam::123456789012:role/MyRole") == "arn"


def test_value_type_url():
    assert _infer_value_type("https://example.com/path") == "url"


def test_value_type_cidr():
    assert _infer_value_type("10.0.0.0/16") == "cidr"


def test_value_type_account_id():
    assert _infer_value_type("123456789012") == "account_id"


def test_value_type_plain_string():
    assert _infer_value_type("my-stack-name") == "string"


def test_value_type_none():
    assert _infer_value_type(None) == "null"


# ---------------------------------------------------------------------------
# _infer_key_domain
# ---------------------------------------------------------------------------

def test_domain_network():
    assert _infer_key_domain("VpcId") == "network"


def test_domain_storage():
    assert _infer_key_domain("S3BucketName") == "storage"


def test_domain_iam():
    assert _infer_key_domain("ExecutionRoleArn") == "iam"


def test_domain_database():
    assert _infer_key_domain("RdsClusterEndpoint") == "database"


def test_domain_compute():
    assert _infer_key_domain("LambdaFunctionArn") == "compute"


def test_domain_general():
    assert _infer_key_domain("StackVersion") == "general"


# ---------------------------------------------------------------------------
# enrich_diffs
# ---------------------------------------------------------------------------

@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="VpcId", baseline_value="vpc-aaa", target_value="vpc-bbb"),
        KeyDiff(key="BucketArn", baseline_value="arn:aws:s3:::my-bucket", target_value="arn:aws:s3:::my-bucket"),
        KeyDiff(key="NewKey", baseline_value=None, target_value="added-value"),
        KeyDiff(key="RemovedKey", baseline_value="old", target_value=None),
    ]


def test_returns_enriched_diff_instances(mixed_diffs):
    result = enrich_diffs(mixed_diffs)
    assert all(isinstance(r, EnrichedDiff) for r in result)


def test_same_length_as_input(mixed_diffs):
    assert len(enrich_diffs(mixed_diffs)) == len(mixed_diffs)


def test_changed_flag_true_when_values_differ(mixed_diffs):
    result = enrich_diffs(mixed_diffs)
    assert result[0].changed is True


def test_changed_flag_false_when_values_equal(mixed_diffs):
    result = enrich_diffs(mixed_diffs)
    assert result[1].changed is False


def test_type_change_note_added(mixed_diffs):
    # NewKey: baseline is null, target is string -> type changed note
    result = enrich_diffs(mixed_diffs)
    new_key_result = next(r for r in result if r.key == "NewKey")
    assert any("type changed" in n for n in new_key_result.notes)


def test_no_note_when_types_match(mixed_diffs):
    result = enrich_diffs(mixed_diffs)
    bucket_result = next(r for r in result if r.key == "BucketArn")
    assert bucket_result.notes == []


def test_domain_assigned(mixed_diffs):
    result = enrich_diffs(mixed_diffs)
    vpc_result = next(r for r in result if r.key == "VpcId")
    assert vpc_result.domain == "network"


def test_as_dict_keys(mixed_diffs):
    result = enrich_diffs(mixed_diffs)
    d = result[0].as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "target_value", "changed",
                             "baseline_type", "target_type", "domain", "notes"}


def test_empty_input():
    assert enrich_diffs([]) == []
