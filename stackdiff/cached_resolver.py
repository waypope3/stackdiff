"""Resolver wrapper that adds caching to stackdiff.resolver."""

from pathlib import Path
from typing import Optional

from stackdiff import cache as _cache
from stackdiff.resolver import resolve_source

DEFAULT_TTL = _cache.DEFAULT_TTL


def resolve_with_cache(
    uri: str,
    ttl: int = DEFAULT_TTL,
    cache_dir: Path = _cache.DEFAULT_CACHE_DIR,
    force_refresh: bool = False,
) -> dict:
    """Resolve a stack source, using a local cache to avoid redundant fetches.

    Parameters
    ----------
    uri:            Local path or s3:// URI.
    ttl:            Cache time-to-live in seconds (default 300).
    cache_dir:      Directory used for cache files.
    force_refresh:  If True, bypass the cache and re-fetch unconditionally.
    """
    if not force_refresh:
        cached = _cache.get(uri, ttl=ttl, cache_dir=cache_dir)
        if cached is not None:
            return cached

    payload = resolve_source(uri)
    # Only cache remote (S3) sources; local files are cheap to re-read.
    if uri.startswith("s3://"):
        _cache.put(uri, payload, cache_dir=cache_dir)
    return payload


def invalidate(uri: str, cache_dir: Path = _cache.DEFAULT_CACHE_DIR) -> bool:
    """Invalidate the cache entry for a specific URI."""
    return _cache.invalidate(uri, cache_dir=cache_dir)


def clear_all(cache_dir: Path = _cache.DEFAULT_CACHE_DIR) -> int:
    """Clear all cached entries."""
    return _cache.clear(cache_dir=cache_dir)
