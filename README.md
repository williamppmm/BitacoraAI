# workspace-memory-rag

Base scaffold for a local workspace memory and RAG assistant.

## Current phase

Phase 2 includes:

- local JSONL event log
- polling filesystem capture
- clipboard monitoring
- batch PowerShell history capture
- `wme note`, `wme recent`, and `wme daemon`

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -U pip
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m pytest -v
.\.venv\Scripts\wme note "primera nota"
.\.venv\Scripts\wme recent
.\.venv\Scripts\python -m workspace_memory.cli daemon --once
```
