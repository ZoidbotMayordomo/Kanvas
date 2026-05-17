# Factory Extension for Kanvas

## Goal
Extend Kanvas to support a Kanvas-based multi-agent software factory while staying:
- agent-agnostic
- git-friendly
- file-based only (`.canvas` + `.md`)
- English-first in code and docs

## Design choice
Kanvas stays the visual workflow base. The factory layer adds:
- richer functional states
- role routing
- Markdown ticket files by ID
- structured agent output contract
- supervisor/orchestrator commands
- canvas <-> markdown synchronization
- a first semi-auto Codex adapter

## Principles
- **No hidden backend**: source of truth stays in repo files.
- **Canvas for global operational state**.
- **Markdown for detail and traceability**.
- **The supervisor validates transitions; agents propose outputs**.
- **Do not lock architecture to Codex even if Codex is the first adapter**.

## MVP commands
```bash
python3 factory-tool.py examples/factory-sample.canvas status
python3 factory-tool.py examples/factory-sample.canvas dispatch --dry-run
python3 factory-tool.py examples/factory-sample.canvas dispatch --automation-mode semi-auto
python3 factory-tool.py examples/factory-sample.canvas sync
python3 factory-tool.py examples/factory-sample.canvas sync --write
python3 factory-tool.py examples/factory-sample.canvas codex-prepare SF-01 /tmp/sf01-task.json
python3 factory-tool.py examples/factory-sample.canvas validate-output /tmp/agent-output.json
python3 factory-tool.py examples/factory-sample.canvas apply-output /tmp/agent-output.json
python3 -m unittest discover -s tests
```

## Current MVP coverage
- canonical `.canvas` ticket parsing
- state-machine validation with rollback / rework paths
- dispatch with priority, max claims, inconsistent-ticket rejection, and running/stale surfacing
- sync that fully mirrors canvas-authoritative metadata into markdown while preserving narrative sections
- structured agent output contract parsing + validation
- `apply-output` to validate and apply agent results back into repo files
- Codex-first semi-auto task payload generation
- unit/integration tests and sample end-to-end flow

## Key docs
- `docs/factory/workflow.md`
- `docs/factory/source-of-truth.md`
- `docs/factory/ticket-template.md`
