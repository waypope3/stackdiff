"""Simple file-based cache for resolved stack sources."""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "stackdiff"
DEFAULT_TTL = 300  # seconds


class CacheError(Exception):
    pass


def _cache_key(uri: str) -> str:
    return hashlib.sha256(uri.encode()).hexdigest()


def _cache_path(cache_dir: Path, uri: str) -> Path:
    return cache_dir / (_cache_key(uri) + ".json")


def get(uri: str, ttl: int = DEFAULT_TTL, cache_dir: Path = DEFAULT_CACHE_DIR) -> Optional[dict]:
    """Return cached stack data for uri if present and not expired, else None."""
    path = _cache_path(cache_dir, uri)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        if time.time() - data["ts"] > ttl:
            path.unlink(missing_ok=True)
            return None
        return data["payload"]
    except (KeyError, json.JSONDecodeError) as exc:
        raise CacheError(f"Corrupt cache entry for {uri}: {exc}") from exc


def put(uri: str, payload: dict, cache_dir: Path = DEFAULT_CACHE_DIR) -> None:
    """Write stack data to cache."""
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        path = _cache_path(cache_dir, uri)
        path.write_text(json.dumps({"ts": time.time(), "payload": payload}))
    except OSError as exc:
        raise CacheError(f"Failed to write cache for {uri}: {exc}") from exc


def invalidate(uri: str, cache_dir: Path = DEFAULT_CACHE_DIR) -> bool:
    """Remove a cached entry. Returns True if something was removed."""
    path = _cache_path(cache_dir, uri)
    if path.exists():
        path.unlink()
        return True
    return False


def clear(cache_dir: Path = DEFAULT_CACHE_DIR) -> int:
    """Remove all cache entries. Returns count removed."""
    if not cache_dir.exists():
        return 0
    removed = 0
    for entry in cache_dir.glob("*.json"):
        entry.unlink()
        removed += 1
    return removed


def purge_expired(ttl: int = DEFAULT_TTL, cache_dir: Path = DEFAULT_CACHE_DIR) -> int:
    """Remove all expired cache entries. Returns count removed."""
    if not cache_dir.exists():
        return 0
    removed = 0
    now = time.time()
    for entry in cache_dir.glob("*.json"):
        try:
            data = json.loads(entry.read_text())
            if now - data["ts"] > ttl:
                entry.unlink(missing_ok=True)
                removed += 1
        except (KeyError, json.JSONDecodeError, OSError):
            # Remove unreadable or corrupt entries
            entry.unlink(missing_ok=True)
            removed += 1
    return removed


def stats(cache_dir: Path = DEFAULT_CACHE_DIR, ttl: int = DEFAULT_TTL) -> dict:
    """Return summary statistics about the cache directory.

    Returns a dict with:
      - ``total``: total number of cache entries
      - ``expired``: number of entries that have exceeded the TTL
      - ``size_bytes``: combined size of all cache files in bytes
    """
    if not cache_dir.exists():
        return {"total": 0, "expired": 0, "size_bytes": 0}
    total = expired = size_bytes = 0
    now = time.time()
    for entry in cache_dir.glob("*.json"):
        total += 1
        size_bytes += entry.stat().st_size
        try:
            data = json.loads(entry.read_text())
            if now - data["ts"] > ttl:
                expired += 1
        except (KeyError, json.JSONDecodeError, OSError):
            expired += 1
    return {"total": total, "expired": expired, "size_bytes": size_bytes}
