"""Tests for stackdiff.parser."""

import json
import textwrap
from pathlib import Path

import pytest

from stackdiff.parser import StackParseError, load_stack


@pytest.fixture()
def tmp_json(tmp_path):
    def _write(data: dict, name: str = "stack.json") -> Path:
        p = tmp_path / name
        p.write_text(json.dumps(data))
        return p
    return _write


@pytest.fixture()
def tmp_yaml(tmp_path):
    def _write(content: str, name: str = "stack.yaml") -> Path:
        p = tmp_path / name
        p.write_text(textwrap.dedent(content))
        return p
    return _write


def test_load_flat_json(tmp_json):
    p = tmp_json({"BucketName": "my-bucket", "Region": "us-east-1"})
    result = load_stack(p)
    assert result == {"BucketName": "my-bucket", "Region": "us-east-1"}


def test_load_flat_yaml(tmp_yaml):
    p = tmp_yaml("""
        BucketName: my-bucket
        Region: us-east-1
    """)
    result = load_stack(p)
    assert result == {"BucketName": "my-bucket", "Region": "us-east-1"}


def test_load_cloudformation_style(tmp_json):
    data = {
        "Outputs": {
            "BucketName": {"Value": "my-bucket", "Description": "S3 bucket"},
            "Region": {"Value": "us-east-1"},
        }
    }
    p = tmp_json(data)
    result = load_stack(p)
    assert result == {"BucketName": "my-bucket", "Region": "us-east-1"}


def test_file_not_found(tmp_path):
    with pytest.raises(StackParseError, match="File not found"):
        load_stack(tmp_path / "missing.json")


def test_invalid_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not valid json")
    with pytest.raises(StackParseError):
        load_stack(p)


def test_non_mapping_raises(tmp_json):
    p = tmp_json.__wrapped__ if hasattr(tmp_json, "__wrapped__") else None
    # Write a JSON list directly
    from pathlib import Path
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        f.write("[1, 2, 3]")
        name = f.name
    try:
        with pytest.raises(StackParseError, match="Expected a mapping"):
            load_stack(name)
    finally:
        os.unlink(name)
