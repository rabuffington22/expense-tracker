"""Process-safe coordination for Plaid synchronization entry points.

The stable file is only a rendezvous inode. Lock state lives in the open file
description and is released by the kernel when the final descriptor closes,
including after process death. Never unlink the lock file, and never replace
``fcntl.flock`` with per-process ``lockf``/``F_SETLK`` record locks.
"""

from __future__ import annotations

import fcntl
import os
from typing import IO

from core.db import get_data_dir


_LOCK_FILENAME = ".plaid-sync.lock"


class SyncLease:
    """Own an acquired cross-process sync lease until explicitly closed."""

    def __init__(self, lock_file: IO[str]):
        self._lock_file = lock_file

    def close(self) -> None:
        lock_file = self._lock_file
        if lock_file is None:
            return
        self._lock_file = None
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        finally:
            lock_file.close()

    def __enter__(self) -> SyncLease:
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def try_acquire_sync_lease() -> SyncLease | None:
    """Return a non-blocking process-safe lease, or ``None`` on contention."""
    lock_path = get_data_dir() / _LOCK_FILENAME
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    lock_file = os.fdopen(fd, "a+", encoding="utf-8")
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_file.close()
        return None
    except Exception:
        lock_file.close()
        raise
    return SyncLease(lock_file)
