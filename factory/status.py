from __future__ import annotations

from typing import Dict, List

from .dispatch import find_actionable
from .models import BoardStatus, TicketCard
from .parser import count_by_state
from .rules import ACTIVE_EXECUTION_STATES, BLOCKING_STATES, TERMINAL_STATES


def dependencies_met(ticket: TicketCard, tickets_by_id: Dict[str, TicketCard]) -> bool:
    for dep in ticket.depends_on:
        dep_ticket = tickets_by_id.get(dep)
        if not dep_ticket or dep_ticket.functional_state != "Done":
            return False
    return True


def summarize_board(board: BoardStatus) -> dict:
    tickets_by_id = {ticket.ticket_id: ticket for ticket in board.tickets}
    actionable = find_actionable(board)
    waiting: List[dict] = []

    actionable_ids = {decision.ticket_id for decision in actionable}

    for ticket in sorted(board.tickets, key=lambda t: t.ticket_id):
        if ticket.functional_state in TERMINAL_STATES:
            continue
        if ticket.execution_state in ACTIVE_EXECUTION_STATES:
            waiting.append(
                {
                    "ticket_id": ticket.ticket_id,
                    "reason": "already running",
                    "state": ticket.functional_state,
                    "role": ticket.current_role,
                }
            )
            continue
        if ticket.functional_state in BLOCKING_STATES:
            waiting.append(
                {
                    "ticket_id": ticket.ticket_id,
                    "reason": ticket.blocked_reason or "blocked",
                    "state": ticket.functional_state,
                    "role": ticket.current_role,
                }
            )
            continue
        if not dependencies_met(ticket, tickets_by_id):
            waiting.append(
                {
                    "ticket_id": ticket.ticket_id,
                    "reason": "dependencies not done",
                    "state": ticket.functional_state,
                    "role": ticket.current_role,
                }
            )
            continue

        if ticket.ticket_id in actionable_ids:
            continue
        waiting.append(
            {
                "ticket_id": ticket.ticket_id,
                "reason": "awaiting human or no routing rule",
                "state": ticket.functional_state,
                "role": ticket.current_role,
            }
        )

    return {
        "canvas": str(board.canvas_path),
        "ticket_count": len(board.tickets),
        "counts_by_state": count_by_state(board.tickets),
        "anomalies": board.anomalies,
        "actionable": [decision.__dict__ for decision in actionable],
        "waiting": waiting,
    }
