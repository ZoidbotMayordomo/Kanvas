from __future__ import annotations

from typing import Dict, List

from .markdown import parse_ticket_markdown, sync_ticket_markdown
from .models import BoardStatus

CANVAS_TO_MARKDOWN_FIELDS = {
    "ticket_id": "ticket_id",
    "title": "title",
    "functional_state": "Estado",
    "execution_state": "Execution state",
    "current_role": "Rol actual",
    "priority": "Prioridad",
}


def inspect_sync(board: BoardStatus) -> dict:
    checked = 0
    missing_docs: List[str] = []
    mismatches: List[Dict[str, str]] = []

    for ticket in board.tickets:
        doc_path = (board.canvas_path.parent / ticket.doc_path).resolve()
        if not doc_path.exists():
            missing_docs.append(ticket.ticket_id)
            continue

        checked += 1
        doc = parse_ticket_markdown(doc_path)
        expected = {
            "ticket_id": ticket.ticket_id,
            "title": ticket.title,
            "Estado": ticket.functional_state,
            "Execution state": ticket.execution_state,
            "Rol actual": ticket.current_role,
            "Prioridad": ticket.priority,
        }
        for field, expected_value in expected.items():
            actual = doc.get(field)
            if actual and actual != expected_value:
                mismatches.append(
                    {
                        "ticket_id": ticket.ticket_id,
                        "field": field,
                        "authority": "canvas",
                        "canvas": expected_value,
                        "markdown": actual,
                    }
                )

    return {
        "checked_docs": checked,
        "missing_docs": missing_docs,
        "mismatches": mismatches,
    }


def write_sync(board: BoardStatus, automation_mode: str = "semi-auto") -> dict:
    changed: List[str] = []
    missing_docs: List[str] = []
    for ticket in board.tickets:
        doc_path = (board.canvas_path.parent / ticket.doc_path).resolve()
        if not doc_path.exists():
            missing_docs.append(ticket.ticket_id)
        if sync_ticket_markdown(ticket, board, automation_mode=automation_mode):
            changed.append(ticket.ticket_id)

    return {
        "changed_docs": changed,
        "missing_docs": missing_docs,
        "updated_count": len(changed),
    }
