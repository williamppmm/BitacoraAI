from pathlib import Path

from workspace_memory.capture.filesystem import detect_file_events, is_relevant_file
from workspace_memory.capture.manual_notes import create_manual_note_event
from workspace_memory.capture.terminal import command_events_from_history, read_powershell_history
from workspace_memory.storage.event_log import EventLog
from workspace_memory.storage.schemas import Event


def test_manual_note_event_uses_manual_source() -> None:
    event = create_manual_note_event("  resolver bug del scraper  ")

    assert event.source == "manual"
    assert event.type == "note"
    assert event.raw_content == "resolver bug del scraper"


def test_event_log_reads_latest_events(tmp_path: Path) -> None:
    log = EventLog(tmp_path / "events.jsonl")
    first = Event(source="manual", type="note", summary="uno")
    second = Event(source="manual", type="note", summary="dos")

    log.append(first)
    log.append(second)

    recent = log.read_recent(limit=1)

    assert [item.summary for item in recent] == ["dos"]


def test_terminal_history_reader_returns_tail(tmp_path: Path) -> None:
    appdata = tmp_path / "Roaming"
    history_file = appdata / "Microsoft" / "Windows" / "PowerShell" / "PSReadLine" / "ConsoleHost_history.txt"
    history_file.parent.mkdir(parents=True)
    history_file.write_text("one\n\ntwo\nthree\n", encoding="utf-8")

    result = read_powershell_history(max_lines=2, appdata=str(appdata))

    assert result == ["two", "three"]


def test_command_events_skip_previously_seen_commands() -> None:
    events, seen = command_events_from_history(["git status", "pytest"], {"git status"})

    assert len(events) == 1
    assert events[0].content_preview == "pytest"
    assert "pytest" in seen


def test_filesystem_detects_modifications() -> None:
    previous = {Path("main.py"): type("Snapshot", (), {"modified_time": 1.0, "size": 10})()}
    current = {Path("main.py"): type("Snapshot", (), {"modified_time": 2.0, "size": 10})()}

    events = detect_file_events(previous, current)

    assert len(events) == 1
    assert events[0].type == "file_modified"


def test_is_relevant_file_respects_extension_and_exclusions() -> None:
    allowed = {".py", ".md"}
    excluded = {".git", "node_modules"}

    assert is_relevant_file(Path("src/app.py"), allowed, excluded) is True
    assert is_relevant_file(Path("node_modules/pkg/index.js"), allowed, excluded) is False
