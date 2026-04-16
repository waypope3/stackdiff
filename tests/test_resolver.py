"""Tests for stackdiff.resolver."""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from stackdiff.resolver import ResolveError, resolve_source


# ---------------------------------------------------------------------------
# Local path resolution
# ---------------------------------------------------------------------------

def test_local_existing_file(tmp_path):
    f = tmp_path / "stack.json"
    f.write_text(json.dumps({"key": "value"}))
    result = resolve_source(str(f))
    assert result == f


def test_local_missing_file():
    with pytest.raises(ResolveError, match="File not found"):
        resolve_source("/nonexistent/path/stack.json")


# ---------------------------------------------------------------------------
# S3 resolution
# ---------------------------------------------------------------------------

def _make_boto_mock(content: bytes = b'{"a": 1}'):
    """Return a mock boto3 module whose s3 client writes *content*."""
    def download_fileobj(bucket, key, fh):
        fh.write(content)

    mock_client = MagicMock()
    mock_client.download_fileobj.side_effect = download_fileobj

    mock_boto3 = MagicMock()
    mock_boto3.client.return_value = mock_client
    return mock_boto3


def test_s3_valid_uri(tmp_path):
    mock_boto3 = _make_boto_mock(b'{"env": "prod"}')
    with patch.dict("sys.modules", {"boto3": mock_boto3}):
        cleanup = []
        path = resolve_source("s3://my-bucket/stacks/prod.json", delete_after=cleanup)
        assert path.exists()
        assert path.suffix == ".json"
        assert cleanup == [path]
        # cleanup
        os.unlink(path)


def test_s3_invalid_uri():
    mock_boto3 = _make_boto_mock()
    with patch.dict("sys.modules", {"boto3": mock_boto3}):
        with pytest.raises(ResolveError, match="Invalid S3 URI"):
            resolve_source("s3://bucket-only")


def test_s3_download_failure():
    mock_client = MagicMock()
    mock_client.download_fileobj.side_effect = RuntimeError("network error")
    mock_boto3 = MagicMock()
    mock_boto3.client.return_value = mock_client

    with patch.dict("sys.modules", {"boto3": mock_boto3}):
        with pytest.raises(ResolveError, match="Failed to fetch"):
            resolve_source("s3://bucket/key.json")


def test_delete_after_not_populated_for_local(tmp_path):
    f = tmp_path / "stack.yaml"
    f.write_text("key: val")
    cleanup: list = []
    resolve_source(str(f), delete_after=cleanup)
    assert cleanup == []
