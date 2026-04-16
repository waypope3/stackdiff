"""Tests for stackdiff.filter."""
import pytest
from stackdiff.filter import filter_keys, apply_filters


STACK = {
    "AppVersion": "1.0",
    "AppUrl": "https://example.com",
    "DbHost": "db.internal",
    "DbPort": "5432",
    "SecretKey": "s3cr3t",
}


def test_no_filters_returns_copy():
    result = filter_keys(STACK)
    assert result == STACK
    assert result is not STACK


def test_include_exact():
    result = filter_keys(STACK, include=["DbHost"])
    assert result == {"DbHost": "db.internal"}


def test_include_glob():
    result = filter_keys(STACK, include=["App*"])
    assert set(result.keys()) == {"AppVersion", "AppUrl"}


def test_include_multiple_patterns():
    result = filter_keys(STACK, include=["App*", "DbPort"])
    assert set(result.keys()) == {"AppVersion", "AppUrl", "DbPort"}


def test_exclude_exact():
    result = filter_keys(STACK, exclude=["SecretKey"])
    assert "SecretKey" not in result
    assert len(result) == 4


def test_exclude_glob():
    result = filter_keys(STACK, exclude=["Db*"])
    assert set(result.keys()) == {"AppVersion", "AppUrl", "SecretKey"}


def test_include_then_exclude():
    # include all App* then exclude AppUrl
    result = filter_keys(STACK, include=["App*"], exclude=["AppUrl"])
    assert result == {"AppVersion": "1.0"}


def test_include_no_match_returns_empty():
    result = filter_keys(STACK, include=["Nonexistent*"])
    assert result == {}


def test_apply_filters_symmetric():
    baseline = {"AppVersion": "1.0", "DbHost": "db1"}
    target = {"AppVersion": "2.0", "DbHost": "db2"}
    fb, ft = apply_filters(baseline, target, include=["App*"])
    assert fb == {"AppVersion": "1.0"}
    assert ft == {"AppVersion": "2.0"}


def test_apply_filters_exclude_both():
    baseline = {"SecretKey": "old", "AppVersion": "1"}
    target = {"SecretKey": "new", "AppVersion": "2"}
    fb, ft = apply_filters(baseline, target, exclude=["Secret*"])
    assert "SecretKey" not in fb
    assert "SecretKey" not in ft
