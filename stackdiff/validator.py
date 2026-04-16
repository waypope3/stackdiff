"""Schema validation for stack output files."""
from __future__ import annotations

from typing import Any


class ValidationError(Exception):
    """Raised when a stack document fails validation."""


_REQUIRED_TYPES = {
    "outputs": dict,
}


def _check_outputs_values(outputs: dict[str, Any]) -> None:
    """All values in outputs must be scalar (str, int, float, bool, None)."""
    bad = [
        k
        for k, v in outputs.items()
        if not isinstance(v, (str, int, float, bool, type(None)))
    ]
    if bad:
        raise ValidationError(
            f"Non-scalar values found in outputs: {bad}. "
            "Only str, int, float, bool, or null are supported."
        )


def validate_stack(data: dict[str, Any]) -> None:
    """Validate a parsed stack document.

    Parameters
    ----------
    data:
        The top-level mapping returned by ``load_stack``.

    Raises
    ------
    ValidationError
        If the document does not conform to the expected schema.
    """
    if not isinstance(data, dict):
        raise ValidationError(f"Stack document must be a mapping, got {type(data).__name__}.")

    if "outputs" not in data:
        raise ValidationError("Stack document is missing required key 'outputs'.")

    outputs = data["outputs"]
    if not isinstance(outputs, dict):
        raise ValidationError(
            f"'outputs' must be a mapping, got {type(outputs).__name__}."
        )

    _check_outputs_values(outputs)

    extra = set(data.keys()) - {"outputs", "stack_name", "region", "metadata"}
    if extra:
        raise ValidationError(f"Unknown top-level keys: {sorted(extra)}.")
