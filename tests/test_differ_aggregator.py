"""Tests for stackdiff.differ_aggregator."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_aggregator import AggregatedDiff, aggregate_diffs
from stackdiff.aggregator_formatter import format_aggregated, format_aggregated_table


def _d(key: str, baseline=None, target=None) -> KeyDiff:
    return KeyDiff(key=key, baseline=baseline, target=target)


@pytest.fixture
def baseline():
    return [
        _d("VpcId", "vpc-aaa", "vpc-aaa"),
        _d("SubnetId", "subnet-111", "subnet-222"),
        _d("OnlyInBaseline", "x", None),
    ]


@pytest.fixture
def sources(baseline):
    return {
        "staging": [
            _d("VpcId", "vpc-aaa", "vpc-aaa"),
            _d("SubnetId", "subnet-111", "subnet-999"),
        ],
        "prod": [
            _d("VpcId", "vpc-aaa", "vpc-aaa"),
            _d("SubnetId", "subnet-111", "subnet-999"),
            _d("ExtraKey", None, "extra-val"),
        ],
    }


def test_returns_aggregated_diff_instances(baseline, sources):
    result = aggregate_diffs(baseline, sources)
    assert all(isinstance(r, AggregatedDiff) for r in result)


def test_all_keys_present(baseline, sources):
    result = aggregate_diffs(baseline, sources)
    keys = {r.key for r in result}
    assert "VpcId" in keys
    assert "SubnetId" in keys
    assert "OnlyInBaseline" in keys
    assert "ExtraKey" in keys


def test_consistent_key(baseline, sources):
    result = aggregate_diffs(baseline, sources)
    vpc = next(r for r in result if r.key == "VpcId")
    assert vpc.is_consistent is True


def test_diverged_key(baseline, sources):
    # staging and prod have different SubnetId targets
    sources_div = {
        "staging": [_d("SubnetId", "subnet-111", "subnet-AAA")],
        "prod": [_d("SubnetId", "subnet-111", "subnet-BBB")],
    }
    result = aggregate_diffs(baseline, sources_div)
    subnet = next(r for r in result if r.key == "SubnetId")
    assert subnet.is_consistent is False


def test_sources_list_populated(baseline, sources):
    result = aggregate_diffs(baseline, sources)
    assert result[0].sources == ["staging", "prod"]


def test_baseline_value_stored(baseline, sources):
    result = aggregate_diffs(baseline, sources)
    vpc = next(r for r in result if r.key == "VpcId")
    assert vpc.baseline_value == "vpc-aaa"


def test_as_dict_keys(baseline, sources):
    result = aggregate_diffs(baseline, sources)
    d = result[0].as_dict()
    assert set(d.keys()) == {"key", "baseline_value", "is_consistent", "sources", "values"}


def test_empty_sources_returns_baseline_keys():
    bl = [_d("A", "1", "1"), _d("B", "2", "3")]
    result = aggregate_diffs(bl, {})
    assert len(result) == 2


def test_format_aggregated_contains_key(baseline, sources):
    result = aggregate_diffs(baseline, sources)
    output = format_aggregated(result, colour=False)
    assert "VpcId" in output
    assert "SubnetId" in output


def test_format_aggregated_empty():
    assert format_aggregated([]) == "No keys to display."


def test_format_aggregated_table_markdown(baseline, sources):
    result = aggregate_diffs(baseline, sources)
    table = format_aggregated_table(result)
    assert table.startswith("|")
    assert "Key" in table
    assert "staging" in table
    assert "prod" in table


def test_format_aggregated_table_empty():
    assert format_aggregated_table([]) == "_No data._"
