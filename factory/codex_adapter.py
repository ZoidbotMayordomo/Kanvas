from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .io import find_ticket
from .models import BoardStatus


def build_codex_task_payload(board: BoardStatus, ticket_id: str, automation_mode: str = "semi-auto") -> Dict[str, object]:
    ticket = find_ticket(board, ticket_id)
    return {
        "adapter": "codex",
        "automation_mode": automation_mode,
        "ticket": {
            "ticket_id": ticket.ticket_id,
            "title": ticket.title,
            "functional_state": ticket.functional_state,
            "execution_state": ticket.execution_state,
            "current_role": ticket.current_role,
            "priority": ticket.priority,
            "depends_on": ticket.depends_on,
            "doc_path": ticket.doc_path,
        },
        "instructions": [
            "Work only from repository files (.canvas + .md) and code in repo.",
            "Return a JSON object matching the factory agent output contract.",
            "Do not edit canvas directly; propose the next functional state in output JSON.",
            "For semi-auto mode, leave final review to a human and set realistic next_step.",
        ],
        "output_contract": {
            "ticket_id": "string",
            "engine": "string",
            "automation_mode": "semi-auto | full-auto | manual",
            "from_state": "current functional state",
            "to_state": "next functional state",
            "summary": "short human-readable summary",
            "next_step": "next expected step",
            "implementation_notes": "optional",
            "qa_notes": "optional",
            "decisions": ["optional list entries"],
            "artifacts": ["files changed, commits, notes"],
            "blockers": ["optional blockers"],
            "transition_history": ["optional trace entries"],
        },
    }


def write_codex_task_file(board: BoardStatus, ticket_id: str, output_path: Path, automation_mode: str = "semi-auto") -> Path:
    payload = build_codex_task_payload(board, ticket_id, automation_mode=automation_mode)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path
