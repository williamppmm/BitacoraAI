"""Batch terminal history readers."""

from __future__ import annotations

import os
from pathlib import Path

from workspace_memory.storage.schemas import Event


def powershell_history_path(appdata: str | None = None) -> Path:
    base = Path(appdata or os.environ.get("APPDATA", ""))
    return base / "Microsoft" / "Windows" / "PowerShell" / "PSReadLine" / "ConsoleHost_history.txt"


def read_powershell_history(max_lines: int = 200, appdata: str | None = None) -> list[str]:
    history_path = powershell_history_path(appdata=appdata)
    if not history_path.exists():
        return []
    lines = history_path.read_text(encoding="utf-8", errors="replace").splitlines()
    return [line.strip() for line in lines[-max_lines:] if line.strip()]


def command_events_from_history(lines: list[str], seen_commands: set[str]) -> tuple[list[Event], set[str]]:
    events: list[Event] = []
    for command in lines:
        if command in seen_commands:
            continue
        events.append(
            Event(
                source="terminal",
                type="command",
                summary=f"Comando ejecutado: {command[:100]}",
                content_preview=command,
                raw_content=command,
            )
        )
        seen_commands.add(command)
    return events, seen_commands
