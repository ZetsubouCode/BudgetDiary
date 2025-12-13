import asyncio
import json
from pathlib import Path
from typing import Any, Callable, Dict


class JsonStore:
    """Async-safe JSON file wrapper with per-file locks."""

    _locks: Dict[str, asyncio.Lock] = {}

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        JsonStore._locks.setdefault(str(self.path), asyncio.Lock())
        self._lock = JsonStore._locks[str(self.path)]
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    async def read(self) -> Dict[str, Any]:
        async with self._lock:
            try:
                with self.path.open("r", encoding="utf-8") as handle:
                    return json.load(handle)
            except json.JSONDecodeError:
                return {}

    async def write(self, data: Dict[str, Any]) -> Dict[str, Any]:
        async with self._lock:
            with self.path.open("w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2)
            return data

    async def update(self, updater: Callable[[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
        """Read-modify-write helper to avoid races."""
        async with self._lock:
            try:
                with self.path.open("r", encoding="utf-8") as handle:
                    data = json.load(handle)
            except json.JSONDecodeError:
                data = {}

            new_data = updater(data) or data
            with self.path.open("w", encoding="utf-8") as handle:
                json.dump(new_data, handle, indent=2)
            return new_data
