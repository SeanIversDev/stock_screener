"""
backend/data/cache.py
---------------------
Simple in-memory cache with per-entry TTL.
No dependencies beyond the standard library.

Usage:
    from data.cache import Cache

    cache = Cache(ttl_seconds=300)   # 5-minute TTL

    result = cache.get("aapl_bars")
    if result is None:
        result = fetch_something_expensive()
        cache.set("aapl_bars", result)
"""

import time
import threading
from typing import Any


class Cache:
    """
    Thread-safe in-memory key/value cache with TTL expiry.

    -Data lives in process memory - restarting the server clears it.
    -A background thread prunes expired entries every `sweep_interval` seconds
    so memory doesn't grow unbounded during long sessions.
    """

    def __init__(self, ttl_seconds: int = 300, sweep_interval: int = 60):
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[Any, float]] = {}  # key -> (value, expires_at)
        self._lock = threading.Lock()

        # Background sweep thread
        self._sweeper = threading.Thread(target=self._sweep_loop,
                                        args=(sweep_interval,),
                                        daemon=True)
        self._sweeper.start()

    # -- Public API --------------------------------------------------------------

    def get(self, key: str) -> Any | None:
        """Return cached value or None if missing / expired."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value. Optionally override the default TTL for this entry."""
        expires_at = time.monotonic() + (ttl if ttl is not None else self._ttl)
        with self._lock:
            self._store[key] = (value, expires_at)

    def delete(self, key: str) -> None:
        """Remove a single entry."""
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        """Wipe everything - useful in tests."""
        with self._lock:
            self._store.clear()

    def stats(self) -> dict:
        """Return basic cache stats for the /health or /debug endpoint."""
        with self._lock:
            now = time.monotonic()
            total = len(self._store)
            alive = sum(1 for _, exp in self._store.values() if exp > now)
            return {"total_keys": total, "live_keys": alive, "ttl_seconds": self._ttl}

    # -- Internal ---------------------------------------------------------------

    def _sweep_loop(self, interval: int) -> None:
        """Periodically remove expired entries to prevent memory leaks."""
        while True:
            time.sleep(interval)
            now = time.monotonic()
            with self._lock:
                expired = [k for k, (_, exp) in self._store.items() if exp <= now]
                for key in expired:
                    del self._store[key]


# -------------------------------------------------------------------------
# Module-level singleton - import and use directly anywhere in the backend
# -------------------------------------------------------------------------

# Screener results: 10-minute TTL (market data doesn't change that fast)
screener_cache = Cache(ttl_seconds=600)

# Price bars: 15-minute TTL
bars_cache = Cache(ttl_seconds=900)

# Fundamentals: 1-hour TTL (changes at most daily)
fundamentals_cache = Cache(ttl_seconds=3600)