"""Parser for infrastructure stack output files (JSON/YAML)."""

import json
import yaml
from pathlib import Path
from typing import Any


class StackParseError(Exception):
    """Raised when a stack output file cannot be parsed."""


def load_stack(path: str | Path) -> dict[str, Any]:
    """Load a stack output file and return its key-value outputs.

    Supports JSON and YAML formats. The file may either be a flat
    key/value mapping or contain an 'Outputs' key (CloudFormation style).

    Args:
        path: Path to the stack output file.

    Returns:
        A flat dictionary of output key -> value.

    Raises:
        StackParseError: If the file cannot be read or parsed.
    """
    path = Path(path)
    if not path.exists():
        raise StackParseError(f"File not found: {path}")

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise StackParseError(f"Could not read {path}: {exc}") from exc

    try:
        if path.suffix in (".yaml", ".yml"):
            data = yaml.safe_load(raw)
        elif path.suffix == ".json":
            data = json.loads(raw)
        else:
            # Try JSON first, then YAML
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = yaml.safe_load(raw)
    except Exception as exc:
        raise StackParseError(f"Failed to parse {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise StackParseError(f"Expected a mapping at the top level in {path}")

    # CloudFormation-style: {Outputs: {Key: {Value: ..., Description: ...}}}
    if "Outputs" in data and isinstance(data["Outputs"], dict):
        outputs = {}
        for key, meta in data["Outputs"].items():
            if isinstance(meta, dict) and "Value" in meta:
                outputs[key] = meta["Value"]
            else:
                outputs[key] = meta
        return outputs

    return data
