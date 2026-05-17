from __future__ import annotations

from typing import Dict, List

from .models import BoardStatus, DispatchDecision, TicketCard
from .parser import count_by_state
from .rules import ACTIVE_EXECUTION_STATES, BLOCKING_STATES, STATE_TO_ROLE, TERMINAL_STATES


def dependencies_met(ticket: TicketCard, tickets_by_id: Dict[str, TicketCard]) -> bool:
    for dep in ticket.depends_on:
        dep_ticket = tickets_by_id.get(dep)
        if not dep_ticket or dep_ticket.functional_state != "Done":
            return False
    return True


def summarize_board(board: BoardStatus) -> dict:
    tickets_by_id = {ticket.ticket_id: ticket for ticket in board.tickets}
    actionable: List[DispatchDecision] = []
    waiting: List[dict] = []

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

        role = STATE_TO_ROLE.get(ticket.functional_state)
        if role and role != "Human":
            actionable.append(
                DispatchDecision(
                    ticket_id=ticket.ticket_id,
                    functional_state=ticket.functional_state,
                    role=role,
                    reason="state is actionable and dependencies are satisfied",
                )
            )
        else:
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
