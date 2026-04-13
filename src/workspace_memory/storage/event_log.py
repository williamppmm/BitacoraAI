"""Append-only JSONL event log used before SQLite lands."""

from __future__ import annotations

import json
from pathlib import Path

from workspace_memory.storage.schemas import Event


class EventLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: Event) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(event.model_dump_json())
            handle.write("\n")

    def read_recent(self, limit: int = 20) -> list[Event]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        records = [json.loads(line) for line in lines[-limit:] if line.strip()]
        return [Event.model_validate(record) for record in reversed(records)]
