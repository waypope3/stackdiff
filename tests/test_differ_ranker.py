"""Tests for differ_ranker and rank_formatter."""
import pytest
from stackdiff.differ import KeyDiff
from stackdiff.differ_ranker import rank_diffs, RankedDiff, _status
from stackdiff.rank_formatter import format_ranked


@pytest.fixture()
def mixed_diffs():
    return [
        KeyDiff(key="alpha", baseline="x", target="x"),   # unchanged
        KeyDiff(key="beta",  baseline="old", target="new"), # changed
        KeyDiff(key="gamma", baseline="v", target=None),   # removed
        KeyDiff(key="delta", baseline=None, target="v"),   # added
    ]


def test_status_unchanged():
    assert _status(KeyDiff(key="k", baseline="a", target="a")) == "unchanged"

def test_status_changed():
    assert _status(KeyDiff(key="k", baseline="a", target="b")) == "changed"

def test_status_added():
    assert _status(KeyDiff(key="k", baseline=None, target="b")) == "added"

def test_status_removed():
    assert _status(KeyDiff(key="k", baseline="a", target=None)) == "removed"


def test_rank_diffs_returns_ranked_diff_instances(mixed_diffs):
    result = rank_diffs(mixed_diffs)
    assert all(isinstance(r, RankedDiff) for r in result)


def test_rank_diffs_length(mixed_diffs):
    assert len(rank_diffs(mixed_diffs)) == 4


def test_removed_ranked_first(mixed_diffs):
    result = rank_diffs(mixed_diffs)
    assert result[0].key == "gamma"


def test_unchanged_ranked_last(mixed_diffs):
    result = rank_diffs(mixed_diffs)
    assert result[-1].key == "alpha"


def test_rank_values_sequential(mixed_diffs):
    result = rank_diffs(mixed_diffs)
    assert [r.rank for r in result] == [1, 2, 3, 4]


def test_as_dict_keys(mixed_diffs):
    rd = rank_diffs(mixed_diffs)[0]
    d = rd.as_dict()
    assert set(d.keys()) == {"key", "rank", "status"}


def test_type_error_on_non_list():
    with pytest.raises(TypeError):
        rank_diffs("not a list")


def test_empty_list():
    assert rank_diffs([]) == []


def test_format_ranked_no_colour(mixed_diffs):
    ranked = rank_diffs(mixed_diffs)
    output = format_ranked(ranked, colour=False)
    assert "gamma" in output
    assert "removed" in output


def test_format_ranked_empty():
    assert format_ranked([]) == "(no diffs)"


def test_format_ranked_contains_all_keys(mixed_diffs):
    ranked = rank_diffs(mixed_diffs)
    output = format_ranked(ranked, colour=False)
    for key in ("alpha", "beta", "gamma", "delta"):
        assert key in output
