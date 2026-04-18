"""Tests for stackdiff.cache."""

import json
import time
from pathlib import Path

import pytest

from stackdiff.cache import CacheError, clear, get, invalidate, put

SAMPLE = {"Outputs": {"BucketName": "my-bucket", "Region": "us-east-1"}}
URI = "s3://my-bucket/stack.json"


@pytest.fixture()
def cache_dir(tmp_path):
    return tmp_path / "cache"


def test_miss_on_empty(cache_dir):
    assert get(URI, cache_dir=cache_dir) is None


def test_put_then_get(cache_dir):
    put(URI, SAMPLE, cache_dir=cache_dir)
    result = get(URI, cache_dir=cache_dir)
    assert result == SAMPLE


def test_expired_returns_none(cache_dir):
    put(URI, SAMPLE, cache_dir=cache_dir)
    result = get(URI, ttl=0, cache_dir=cache_dir)
    assert result is None


def test_expired_removes_file(cache_dir):
    put(URI, SAMPLE, cache_dir=cache_dir)
    get(URI, ttl=0, cache_dir=cache_dir)
    assert list(cache_dir.glob("*.json")) == []


def test_invalidate_existing(cache_dir):
    put(URI, SAMPLE, cache_dir=cache_dir)
    removed = invalidate(URI, cache_dir=cache_dir)
    assert removed is True
    assert get(URI, cache_dir=cache_dir) is None


def test_invalidate_missing(cache_dir):
    assert invalidate(URI, cache_dir=cache_dir) is False


def test_clear_removes_all(cache_dir):
    put(URI, SAMPLE, cache_dir=cache_dir)
    put("s3://other/stack.json", SAMPLE, cache_dir=cache_dir)
    count = clear(cache_dir=cache_dir)
    assert count == 2
    assert list(cache_dir.glob("*.json")) == []


def test_clear_nonexistent_dir(tmp_path):
    assert clear(cache_dir=tmp_path / "no_such_dir") == 0


def test_corrupt_cache_raises(cache_dir):
    cache_dir.mkdir()
    from stackdiff.cache import _cache_path
    path = _cache_path(cache_dir, URI)
    path.write_text("not-json")
    with pytest.raises(CacheError):
        get(URI, cache_dir=cache_dir)


def test_different_uris_independent(cache_dir):
    other = "s3://other-bucket/prod.json"
    put(URI, SAMPLE, cache_dir=cache_dir)
    assert get(other, cache_dir=cache_dir) is None
