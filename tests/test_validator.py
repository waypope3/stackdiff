"""Tests for stackdiff.validator."""
import pytest

from stackdiff.validator import ValidationError, validate_stack


def test_valid_minimal():
    validate_stack({"outputs": {"Key": "value"}})


def test_valid_full():
    validate_stack(
        {
            "stack_name": "my-stack",
            "region": "us-east-1",
            "metadata": {"env": "prod"},
            "outputs": {"BucketName": "my-bucket", "Count": 3},
        }
    )


def test_not_a_mapping():
    with pytest.raises(ValidationError, match="mapping"):
        validate_stack(["outputs"])


def test_missing_outputs_key():
    with pytest.raises(ValidationError, match="missing required key"):
        validate_stack({"stack_name": "x"})


def test_outputs_not_a_mapping():
    with pytest.raises(ValidationError, match="'outputs' must be a mapping"):
        validate_stack({"outputs": ["a", "b"]})


def test_nested_value_rejected():
    with pytest.raises(ValidationError, match="Non-scalar"):
        validate_stack({"outputs": {"Key": {"nested": "value"}}})


def test_list_value_rejected():
    with pytest.raises(ValidationError, match="Non-scalar"):
        validate_stack({"outputs": {"Key": [1, 2, 3]}})


def test_none_value_allowed():
    validate_stack({"outputs": {"Key": None}})


def test_bool_value_allowed():
    validate_stack({"outputs": {"Enabled": True}})


def test_unknown_top_level_key():
    with pytest.raises(ValidationError, match="Unknown top-level keys"):
        validate_stack({"outputs": {}, "unexpected": "field"})


def test_empty_outputs_valid():
    validate_stack({"outputs": {}})
