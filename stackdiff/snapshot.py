"""Snapshot: save and load named diff snapshots for later comparison."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from stackdiff.differ import DiffResult

DEFAULT_SNAPSHOT_DIR = Path.home() / ".stackdiff" / "snapshots"


class SnapshotError(Exception):
    pass


def _snapshot_path(name: str, directory: Path) -> Path:
    safe = name.replace("/", "_").replace(" ", "_")
    return directory / f"{safe}.json"


def save_snapshot(result: DiffResult, name: str, directory: Optional[Path] = None) -> Path:
    """Persist a DiffResult under *name*. Returns the file path written."""
    directory = directory or DEFAULT_SNAPSHOT_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = _snapshot_path(name, directory)
    payload = {
        "name": name,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "diff": {
            key: {
                "baseline": entry.baseline,
                "target": entry.target,
                "status": entry.status,
            }
            for key, entry in result.items()
        },
    }
    path.write_text(json.dumps(payload, indent=2))
    return path


def load_snapshot(name: str, directory: Optional[Path] = None) -> DiffResult:
    """Load a previously saved snapshot by *name*."""
    directory = directory or DEFAULT_SNAPSHOT_DIR
    path = _snapshot_path(name, directory)
    if not path.exists():
        raise SnapshotError(f"Snapshot '{name}' not found at {path}")
    raw = json.loads(path.read_text())
    from stackdiff.differ import KeyDiff
    return {
        key: KeyDiff(baseline=v["baseline"], target=v["target"], status=v["status"])
        for key, v in raw["diff"].items()
    }


def list_snapshots(directory: Optional[Path] = None) -> list[str]:
    """Return names of all saved snapshots."""
    directory = directory or DEFAULT_SNAPSHOT_DIR
    if not directory.exists():
        return []
    return [p.stem for p in sorted(directory.glob("*.json"))]


def delete_snapshot(name: str, directory: Optional[Path] = None) -> bool:
    """Delete a snapshot. Returns True if deleted, False if not found."""
    directory = directory or DEFAULT_SNAPSHOT_DIR
    path = _snapshot_path(name, directory)
    if path.exists():
        path.unlink()
        return True
    return False
