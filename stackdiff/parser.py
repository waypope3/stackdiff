"""Load stack output documents from JSON or YAML files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
    _YAML_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover
    _YAML_AVAILABLE = False

from stackdiff.validator import ValidationError, validate_stack


class StackParseError(Exception):
    """Raised when a stack file cannot be parsed or is structurally invalid."""


def _load_raw(path: Path) -> Any:
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    if suffix == ".json":
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise StackParseError(f"Invalid JSON in {path}: {exc}") from exc
    if suffix in (".yaml", ".yml"):
        if not _YAML_AVAILABLE:  # pragma: no cover
            raise StackParseError("PyYAML is not installed; cannot parse YAML files.")
        try:
            return yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise StackParseError(f"Invalid YAML in {path}: {exc}") from exc
    raise StackParseError(
        f"Unsupported file extension '{path.suffix}'. Use .json, .yaml, or .yml."
    )


def _normalise(data: Any, path: Path) -> dict[str, Any]:
    """Accept either a bare outputs mapping or a full stack document."""
    if not isinstance(data, dict):
        raise StackParseError(
            f"{path}: top-level value must be a mapping, got {type(data).__name__}."
        )
    # Bare outputs mapping — wrap it.
    if "outputs" not in data:
        return {"outputs": data}
    return data


def load_stack(path: str | Path) -> dict[str, Any]:
    """Parse and validate a stack output file.

    Returns the normalised document with at least an ``outputs`` key.

    Raises
    ------
    StackParseError
        For I/O, parse, or schema errors.
    """
    p = Path(path)
    if not p.exists():
        raise StackParseError(f"File not found: {p}")
    raw = _load_raw(p)
    doc = _normalise(raw, p)
    try:
        validate_stack(doc)
    except ValidationError as exc:
        raise StackParseError(f"Validation failed for {p}: {exc}") from exc
    return doc
