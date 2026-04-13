"""Filesystem polling watcher for relevant project files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from workspace_memory.storage.schemas import Event


@dataclass(slots=True)
class FileSnapshot:
    modified_time: float
    size: int


def is_relevant_file(path: Path, allowed_extensions: set[str], excluded_dirs: set[str]) -> bool:
    if path.suffix.lower() not in allowed_extensions:
        return False
    normalized = path.as_posix().lower()
    parts = {part.lower() for part in path.parts}
    return not any(
        excluded.lower() in parts or excluded.lower().replace("\\", "/") in normalized
        for excluded in excluded_dirs
    )


def snapshot_paths(
    roots: Iterable[Path],
    allowed_extensions: set[str],
    excluded_dirs: set[str],
) -> dict[Path, FileSnapshot]:
    snapshot: dict[Path, FileSnapshot] = {}
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if not is_relevant_file(path, allowed_extensions, excluded_dirs):
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            snapshot[path] = FileSnapshot(modified_time=stat.st_mtime, size=stat.st_size)
    return snapshot


def detect_file_events(
    previous: dict[Path, FileSnapshot],
    current: dict[Path, FileSnapshot],
) -> list[Event]:
    events: list[Event] = []

    for path, current_item in current.items():
        old_item = previous.get(path)
        if old_item is None:
            events.append(
                Event(
                    source="filesystem",
                    type="file_created",
                    path=str(path),
                    summary=f"Archivo creado: {path.name}",
                )
            )
            continue
        if (
            old_item.modified_time != current_item.modified_time
            or old_item.size != current_item.size
        ):
            events.append(
                Event(
                    source="filesystem",
                    type="file_modified",
                    path=str(path),
                    summary=f"Archivo modificado: {path.name}",
                )
            )

    for path in previous:
        if path not in current:
            events.append(
                Event(
                    source="filesystem",
                    type="file_deleted",
                    path=str(path),
                    summary=f"Archivo eliminado: {path.name}",
                )
            )

    return events
