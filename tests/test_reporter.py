"""Tests for stackdiff.reporter."""
import json

import pytest

from stackdiff.differ import DiffResult
from stackdiff.reporter import generate_report


@pytest.fixture()
def result_with_diffs() -> DiffResult:
    return DiffResult(
        changed={"Region": ("us-east-1", "eu-west-1")},
        added={"NewBucket": "my-bucket"},
        removed={"OldQueue": "arn:aws:sqs:..."},
        unchanged={"AppName": "demo"},
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(changed={}, added={}, removed={}, unchanged={"AppName": "demo"})


def test_text_changed(result_with_diffs: DiffResult) -> None:
    out = generate_report(result_with_diffs, fmt="text")
    assert "~ Region" in out
    assert "us-east-1" in out
    assert "eu-west-1" in out


def test_text_added(result_with_diffs: DiffResult) -> None:
    out = generate_report(result_with_diffs, fmt="text")
    assert "+ NewBucket" in out


def test_text_removed(result_with_diffs: DiffResult) -> None:
    out = generate_report(result_with_diffs, fmt="text")
    assert "- OldQueue" in out


def test_text_no_diff(empty_result: DiffResult) -> None:
    out = generate_report(empty_result, fmt="text")
    assert out == "No differences found."


def test_json_structure(result_with_diffs: DiffResult) -> None:
    out = generate_report(result_with_diffs, fmt="json")
    data = json.loads(out)
    assert "changed" in data
    assert data["changed"]["Region"] == {"old": "us-east-1", "new": "eu-west-1"}
    assert data["added"]["NewBucket"] == "my-bucket"
    assert data["removed"]["OldQueue"] == "arn:aws:sqs:..."
    assert data["unchanged"]["AppName"] == "demo"


def test_json_empty(empty_result: DiffResult) -> None:
    data = json.loads(generate_report(empty_result, fmt="json"))
    assert data["changed"] == {}
    assert data["added"] == {}
    assert data["removed"] == {}


def test_markdown_headings(result_with_diffs: DiffResult) -> None:
    out = generate_report(result_with_diffs, fmt="markdown")
    assert "## Changed" in out
    assert "## Added" in out
    assert "## Removed" in out


def test_markdown_no_diff(empty_result: DiffResult) -> None:
    out = generate_report(empty_result, fmt="markdown")
    assert "No differences found" in out
    assert "## Changed" not in out


def test_default_format_is_text(result_with_diffs: DiffResult) -> None:
    assert generate_report(result_with_diffs) == generate_report(result_with_diffs, fmt="text")
