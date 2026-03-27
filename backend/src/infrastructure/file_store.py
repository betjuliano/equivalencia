"""Infrastructure — Atomic JSON file store with mutex locking (Spec.md sections 4.5, 4.6)"""
from __future__ import annotations
import asyncio
import json
import os
import tempfile
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional


# Per-path asyncio locks to prevent concurrent writes
_locks: Dict[str, asyncio.Lock] = {}
_global_lock = asyncio.Lock()


async def _get_lock(path: str) -> asyncio.Lock:
    async with _global_lock:
        if path not in _locks:
            _locks[path] = asyncio.Lock()
        return _locks[path]


async def write_json_atomic(path: Path, data: Any) -> None:
    """Write JSON atomically: write to .tmp then rename."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = await _get_lock(str(path))
    async with lock:
        content = json.dumps(data, ensure_ascii=False, indent=2)
        # Validate JSON before writing
        json.loads(content)
        tmp_path = path.with_suffix(".tmp")
        try:
            tmp_path.write_text(content, encoding="utf-8")
            tmp_path.replace(path)
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
            raise


async def read_json(path: Path) -> Optional[Any]:
    """Read and parse a JSON file, return None if not found."""
    path = Path(path)
    if not path.exists():
        return None
    lock = await _get_lock(str(path))
    async with lock:
        content = path.read_text(encoding="utf-8")
        return json.loads(content)


def read_json_sync(path: Path) -> Optional[Any]:
    """Synchronous read for startup/indexing operations."""
    path = Path(path)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def short_hash(text: str, length: int = 6) -> str:
    """Generate a short hash for use in file IDs."""
    return hashlib.sha256(text.encode()).hexdigest()[:length]


def list_json_files(directory: Path) -> list[Path]:
    """List all .json files in a directory (non-recursive)."""
    directory = Path(directory)
    if not directory.exists():
        return []
    return sorted(directory.glob("*.json"))
