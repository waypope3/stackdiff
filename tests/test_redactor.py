"""Tests for stackdiff.redactor."""

import pytest

from stackdiff.differ import KeyDiff
from stackdiff.redactor import (
    REDACTED,
    redact_diffs,
    redact_stack,
    redact_value,
)


def test_redact_value_safe_key():
    assert redact_value("DatabaseHost", "db.example.com", []) == "db.example.com"


def test_redact_value_sensitive_key():
    assert redact_value("DbPassword", "s3cr3t", [r"(?i)password"]) == REDACTED


def test_redact_value_non_string_raises():
    with pytest.raises(TypeError):
        redact_value("Key", 123, [])  # type: ignore[arg-type]


def test_redact_stack_leaves_safe_keys():
    outputs = {"Host": "example.com", "Port": "5432"}
    result = redact_stack(outputs)
    assert result == outputs


def test_redact_stack_redacts_password():
    outputs = {"DbPassword": "hunter2", "Host": "db.local"}
    result = redact_stack(outputs)
    assert result["DbPassword"] == REDACTED
    assert result["Host"] == "db.local"


def test_redact_stack_redacts_token():
    outputs = {"AuthToken": "abc123"}
    result = redact_stack(outputs)
    assert result["AuthToken"] == REDACTED


def test_redact_stack_custom_patterns():
    outputs = {"MySecret": "val", "Normal": "ok"}
    result = redact_stack(outputs, patterns=[r"(?i)secret"])
    assert result["MySecret"] == REDACTED
    assert result["Normal"] == "ok"


def test_redact_stack_returns_copy():
    outputs = {"Key": "val"}
    result = redact_stack(outputs, patterns=[])
    result["Key"] = "changed"
    assert outputs["Key"] == "val"


def test_redact_diffs_safe_key_unchanged():
    diffs = [KeyDiff(key="Host", baseline="a", target="b", changed=True)]
    result = redact_diffs(diffs, patterns=[])
    assert result[0].baseline == "a"
    assert result[0].target == "b"


def test_redact_diffs_sensitive_key_redacted():
    diffs = [KeyDiff(key="ApiKey", baseline="old", target="new", changed=True)]
    result = redact_diffs(diffs)
    assert result[0].baseline == REDACTED
    assert result[0].target == REDACTED
    assert result[0].changed is True


def test_redact_diffs_none_values_preserved():
    diffs = [KeyDiff(key="SecretToken", baseline=None, target="new", changed=True)]
    result = redact_diffs(diffs)
    assert result[0].baseline is None
    assert result[0].target == REDACTED


def test_redact_diffs_preserves_key_and_changed():
    diffs = [KeyDiff(key="Password", baseline="x", target="x", changed=False)]
    result = redact_diffs(diffs)
    assert result[0].key == "Password"
    assert result[0].changed is False
