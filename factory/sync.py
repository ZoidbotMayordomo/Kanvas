from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .markdown import parse_ticket_markdown
from .models import BoardStatus


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
        if doc.get("ticket_id") and doc.get("ticket_id") != ticket.ticket_id:
            mismatches.append(
                {
                    "ticket_id": ticket.ticket_id,
                    "field": "ticket_id",
                    "canvas": ticket.ticket_id,
                    "markdown": doc.get("ticket_id", ""),
                }
            )
        if doc.get("Estado") and doc.get("Estado") != ticket.functional_state:
            mismatches.append(
                {
                    "ticket_id": ticket.ticket_id,
                    "field": "Estado",
                    "canvas": ticket.functional_state,
                    "markdown": doc.get("Estado", ""),
                }
            )
        if doc.get("Execution state") and doc.get("Execution state") != ticket.execution_state:
            mismatches.append(
                {
                    "ticket_id": ticket.ticket_id,
                    "field": "Execution state",
                    "canvas": ticket.execution_state,
                    "markdown": doc.get("Execution state", ""),
                }
            )

    return {
        "checked_docs": checked,
        "missing_docs": missing_docs,
        "mismatches": mismatches,
    }
