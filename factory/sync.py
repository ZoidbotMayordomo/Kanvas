from __future__ import annotations

from typing import Dict, List

from .markdown import parse_ticket_markdown, sync_ticket_markdown
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
                    "authority": "canvas",
                    "canvas": ticket.ticket_id,
                    "markdown": doc.get("ticket_id", ""),
                }
            )
        if doc.get("title") and doc.get("title") != ticket.title:
            mismatches.append(
                {
                    "ticket_id": ticket.ticket_id,
                    "field": "title",
                    "authority": "canvas",
                    "canvas": ticket.title,
                    "markdown": doc.get("title", ""),
                }
            )
        if doc.get("Estado") and doc.get("Estado") != ticket.functional_state:
            mismatches.append(
                {
                    "ticket_id": ticket.ticket_id,
                    "field": "Estado",
                    "authority": "canvas",
                    "canvas": ticket.functional_state,
                    "markdown": doc.get("Estado", ""),
                }
            )
        if doc.get("Execution state") and doc.get("Execution state") != ticket.execution_state:
            mismatches.append(
                {
                    "ticket_id": ticket.ticket_id,
                    "field": "Execution state",
                    "authority": "canvas",
                    "canvas": ticket.execution_state,
                    "markdown": doc.get("Execution state", ""),
                }
            )
        if doc.get("Rol actual") and doc.get("Rol actual") != ticket.current_role:
            mismatches.append(
                {
                    "ticket_id": ticket.ticket_id,
                    "field": "Rol actual",
                    "authority": "canvas",
                    "canvas": ticket.current_role,
                    "markdown": doc.get("Rol actual", ""),
                }
            )
        if doc.get("Prioridad") and doc.get("Prioridad") != ticket.priority:
            mismatches.append(
                {
                    "ticket_id": ticket.ticket_id,
                    "field": "Prioridad",
                    "authority": "canvas",
                    "canvas": ticket.priority,
                    "markdown": doc.get("Prioridad", ""),
                }
            )

    return {
        "checked_docs": checked,
        "missing_docs": missing_docs,
        "mismatches": mismatches,
    }


def write_sync(board: BoardStatus) -> dict:
    changed: List[str] = []
    missing_docs: List[str] = []
    for ticket in board.tickets:
        doc_path = (board.canvas_path.parent / ticket.doc_path).resolve()
        if not doc_path.exists():
            missing_docs.append(ticket.ticket_id)
            continue
        if sync_ticket_markdown(ticket, board):
            changed.append(ticket.ticket_id)

    return {
        "changed_docs": changed,
        "missing_docs": missing_docs,
        "updated_count": len(changed),
    }
