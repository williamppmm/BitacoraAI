from datetime import datetime

import pytest
from pydantic import ValidationError

from workspace_memory.storage.schemas import Event, MemoryDocument, QueryContext


def test_event_defaults() -> None:
    event = Event(source="filesystem", type="file_modified", summary="main.py editado")

    assert event.id.startswith("evt_")
    assert isinstance(event.timestamp, datetime)
    assert event.project is None
    assert event.metadata == {}


def test_event_rejects_invalid_source() -> None:
    with pytest.raises(ValidationError):
        Event(source="pantalla", type="file_modified", summary="test")


def test_event_truncates_preview() -> None:
    event = Event(
        source="clipboard",
        type="clipboard_text",
        summary="texto copiado",
        content_preview="x" * 800,
    )

    assert len(event.content_preview or "") == 500


def test_memory_document_defaults() -> None:
    memory = MemoryDocument(event_ids=["evt_123"], text="Resumen técnico")

    assert memory.id.startswith("mem_")
    assert memory.tags == []
    assert memory.importance_score == 0.5


def test_query_context_defaults() -> None:
    context = QueryContext(question="¿Qué hice hoy?")

    assert context.recent_events == []
    assert context.relevant_memories == []
    assert context.retrieval_explanation is None
