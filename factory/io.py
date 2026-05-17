from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .models import BoardStatus, TicketCard
from .rules import STATE_TO_COLOR

FIELD_ORDER = ["Estado", "Execution", "Rol actual", "Prioridad", "Doc", "Depends on", "Bloqueo"]


def render_ticket_text(ticket: TicketCard) -> str:
    values: Dict[str, str] = {
        "Estado": ticket.functional_state,
        "Execution": ticket.execution_state,
        "Rol actual": ticket.current_role,
        "Prioridad": ticket.priority,
        "Doc": ticket.doc_path,
        "Depends on": ", ".join(ticket.depends_on),
        "Bloqueo": ticket.blocked_reason or "",
    }
    lines = [f"## {ticket.ticket_id} {ticket.title}"]
    for field in FIELD_ORDER:
        lines.append(f"{field}: {values[field]}")
    return "\n".join(lines)


def update_board_ticket(board: BoardStatus, ticket: TicketCard) -> None:
    if not board.payload:
        raise ValueError("Board payload is not loaded")
    for node in board.payload.get("nodes", []):
        if node.get("id") == ticket.node_id:
            node["text"] = render_ticket_text(ticket)
            node["color"] = STATE_TO_COLOR.get(ticket.functional_state, node.get("color", "0"))
            return
    raise KeyError(f"Node not found for ticket {ticket.ticket_id}")


def find_ticket(board: BoardStatus, ticket_id: str) -> TicketCard:
    for ticket in board.tickets:
        if ticket.ticket_id == ticket_id:
            return ticket
    raise KeyError(f"Ticket not found: {ticket_id}")


def save_canvas(board: BoardStatus) -> None:
    if not board.payload:
        raise ValueError("Board payload is not loaded")
    board.canvas_path.write_text(json.dumps(board.payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
