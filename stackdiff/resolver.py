"""Resolve stack files from various sources (local path, S3, SSM)."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional


class ResolveError(Exception):
    """Raised when a stack source cannot be resolved."""


def _resolve_s3(uri: str) -> Path:
    """Download an S3 object to a temp file and return its path."""
    try:
        import boto3  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ResolveError("boto3 is required for S3 sources") from exc

    # s3://bucket/key
    without_scheme = uri[len("s3://"):]
    bucket, _, key = without_scheme.partition("/")
    if not bucket or not key:
        raise ResolveError(f"Invalid S3 URI: {uri!r}")

    suffix = Path(key).suffix or ".json"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        s3 = boto3.client("s3")
        s3.download_fileobj(bucket, key, tmp)
    except Exception as exc:
        os.unlink(tmp.name)
        raise ResolveError(f"Failed to fetch {uri}: {exc}") from exc
    finally:
        tmp.close()

    return Path(tmp.name)


def _resolve_local(path_str: str) -> Path:
    p = Path(path_str)
    if not p.exists():
        raise ResolveError(f"File not found: {path_str!r}")
    return p


def resolve_source(source: str, *, delete_after: Optional[list] = None) -> Path:
    """Return a local Path for *source*, which may be a local path or S3 URI.

    If *delete_after* is a list, temp files that should be cleaned up are
    appended to it so the caller can remove them when done.
    """
    if source.startswith("s3://"):
        path = _resolve_s3(source)
        if delete_after is not None:
            delete_after.append(path)
        return path

    return _resolve_local(source)
