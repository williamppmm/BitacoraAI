"""Manual note capture helpers."""

from workspace_memory.storage.schemas import Event


def create_manual_note_event(text: str) -> Event:
    stripped = text.strip()
    return Event(
        source="manual",
        type="note",
        summary=stripped[:120] or "Nota manual",
        content_preview=stripped,
        raw_content=stripped,
    )
