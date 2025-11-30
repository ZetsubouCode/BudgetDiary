from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class JsonStore(Generic[T]):
    """Small helper around reading and writing JSON files."""

    def __init__(self, file_path: Path, default_factory: Callable[[], T]):
        self.file_path = file_path
        self.default_factory = default_factory
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.write(self.default_factory())

    def read(self) -> T:
        with self.file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def write(self, payload: T) -> None:
        with self.file_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)

    def update(self, mutator: Callable[[T], T]) -> T:
        payload = self.read()
        updated = mutator(payload)
        self.write(updated)
        return updated
