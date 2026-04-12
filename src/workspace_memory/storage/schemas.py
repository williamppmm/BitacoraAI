"""Core data contracts for workspace memory events and retrieval."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


EventSource = Literal["filesystem", "clipboard", "terminal", "manual"]


def _prefixed_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


class Event(BaseModel):
    id: str = Field(default_factory=lambda: _prefixed_id("evt"))
    timestamp: datetime = Field(default_factory=datetime.now)
    source: EventSource
    type: str
    project: str | None = None
    path: str | None = None
    summary: str
    content_preview: str | None = None
    raw_content: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("content_preview")
    @classmethod
    def truncate_preview(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value[:500]


class MemoryDocument(BaseModel):
    id: str = Field(default_factory=lambda: _prefixed_id("mem"))
    event_ids: list[str]
    text: str
    tags: list[str] = Field(default_factory=list)
    project: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    embedding_id: str | None = None
    importance_score: float = 0.5


class QueryContext(BaseModel):
    question: str
    recent_events: list[Event] = Field(default_factory=list)
    relevant_memories: list[MemoryDocument] = Field(default_factory=list)
    active_project: str | None = None
    suggested_prompt: str | None = None
    retrieval_explanation: str | None = None
