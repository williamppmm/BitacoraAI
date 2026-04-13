"""Command-line entrypoints for local capture and event inspection."""

from __future__ import annotations

from pathlib import Path

import typer

from workspace_memory.capture.manual_notes import create_manual_note_event
from workspace_memory.config.settings import settings
from workspace_memory.daemon import run_daemon
from workspace_memory.storage.event_log import EventLog

app = typer.Typer(help="Workspace Memory command line interface.")


@app.command()
def recent(limit: int = typer.Option(20, min=1, max=200)) -> None:
    """Show recently captured events from the local event log."""
    event_log = EventLog(settings.event_log_path)
    events = event_log.read_recent(limit=limit)

    if not events:
        typer.echo("No hay eventos capturados todavía.")
        return

    for event in events:
        location = f" [{event.path}]" if event.path else ""
        typer.echo(f"{event.timestamp.isoformat()} | {event.source}:{event.type} | {event.summary}{location}")


@app.command()
def note(text: str) -> None:
    """Append a manual note event to the local event log."""
    event_log = EventLog(settings.event_log_path)
    event = create_manual_note_event(text=text)
    event_log.append(event)
    typer.echo(f"Nota guardada como {event.id}")


@app.command()
def daemon(
    once: bool = typer.Option(False, help="Run a single polling cycle and exit."),
    duration_seconds: int | None = typer.Option(None, min=1, help="Optional max runtime for the daemon."),
) -> None:
    """Run the local capture daemon."""
    run_daemon(run_once=once, duration_seconds=duration_seconds)


if __name__ == "__main__":
    app()
