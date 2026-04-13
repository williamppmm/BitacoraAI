"""Clipboard polling monitor."""

from __future__ import annotations

import hashlib
import logging
import threading
import time
from collections.abc import Callable

from workspace_memory.storage.schemas import Event

logger = logging.getLogger(__name__)

try:
    import pyperclip
except ImportError:  # pragma: no cover - depends on optional runtime dependency
    pyperclip = None


def _hash_text(content: str) -> str:
    return hashlib.md5(content.encode("utf-8", errors="replace")).hexdigest()


class ClipboardMonitor:
    def __init__(
        self,
        on_event: Callable[[Event], None],
        interval_seconds: float = 2.0,
    ) -> None:
        self.on_event = on_event
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, name="clipboard-monitor", daemon=True)
        self._last_hash: str | None = None

    def start(self) -> None:
        if pyperclip is None:
            logger.warning("pyperclip no está instalado; se omite el monitor de portapapeles.")
            return
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join(timeout=self.interval_seconds + 0.5)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                content = pyperclip.paste()
                current_hash = _hash_text(content)
                if content.strip() and current_hash != self._last_hash:
                    self._last_hash = current_hash
                    preview = content[:500]
                    self.on_event(
                        Event(
                            source="clipboard",
                            type="clipboard_text",
                            summary=f"Texto copiado ({len(content)} chars)",
                            content_preview=preview,
                            raw_content=content,
                        )
                    )
            except Exception as exc:  # pragma: no cover - clipboard access is OS-specific
                logger.debug("No se pudo leer el portapapeles: %s", exc)
            self._stop_event.wait(self.interval_seconds)
