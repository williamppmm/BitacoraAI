"""Local capture daemon orchestration."""

from __future__ import annotations

import logging
import time
from pathlib import Path

from workspace_memory.capture.clipboard import ClipboardMonitor
from workspace_memory.capture.filesystem import detect_file_events, snapshot_paths
from workspace_memory.capture.terminal import command_events_from_history, read_powershell_history
from workspace_memory.config.settings import settings
from workspace_memory.runtime.logging import configure_logging
from workspace_memory.storage.event_log import EventLog
from workspace_memory.storage.schemas import Event

logger = logging.getLogger(__name__)


def run_daemon(run_once: bool = False, duration_seconds: int | None = None) -> None:
    configure_logging(settings.log_level)
    event_log = EventLog(settings.event_log_path)

    def persist_event(event: Event) -> None:
        event_log.append(event)
        logger.info("captured_event source=%s type=%s summary=%s", event.source, event.type, event.summary)

    clipboard_monitor = ClipboardMonitor(
        on_event=persist_event,
        interval_seconds=settings.clipboard_poll_seconds,
    )
    clipboard_monitor.start()

    roots = [Path(root) for root in settings.capture_roots]
    allowed_extensions = {ext.lower() for ext in settings.filesystem_extensions}
    excluded_dirs = {item.lower() for item in settings.excluded_dirs}
    previous_snapshot = snapshot_paths(roots, allowed_extensions, excluded_dirs)
    seen_commands = set(read_powershell_history(settings.terminal_history_max_lines))
    started_at = time.monotonic()

    try:
        while True:
            current_snapshot = snapshot_paths(roots, allowed_extensions, excluded_dirs)
            for event in detect_file_events(previous_snapshot, current_snapshot):
                persist_event(event)
            previous_snapshot = current_snapshot

            history_lines = read_powershell_history(settings.terminal_history_max_lines)
            terminal_events, seen_commands = command_events_from_history(history_lines, seen_commands)
            for event in terminal_events:
                persist_event(event)

            if run_once:
                break
            if duration_seconds is not None and time.monotonic() - started_at >= duration_seconds:
                break
            time.sleep(settings.daemon_poll_seconds)
    finally:
        clipboard_monitor.stop()
