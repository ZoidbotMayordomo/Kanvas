from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from .io import save_canvas, update_board_ticket
from .markdown import sync_ticket_markdown
from .models import BoardStatus, DispatchDecision, TicketCard
from .rules import ACTIVE_EXECUTION_STATES, BLOCKING_STATES, STATE_TO_ROLE, TERMINAL_STATES


def dependencies_met(ticket: TicketCard, tickets_by_id: Dict[str, TicketCard]) -> bool:
    for dep in ticket.depends_on:
        dep_ticket = tickets_by_id.get(dep)
        if not dep_ticket or dep_ticket.functional_state != "Done":
            return False
    return True


def find_actionable(board: BoardStatus) -> List[DispatchDecision]:
    tickets_by_id = {ticket.ticket_id: ticket for ticket in board.tickets}
    actionable: List[DispatchDecision] = []

    for ticket in sorted(board.tickets, key=lambda t: t.ticket_id):
        if ticket.functional_state in TERMINAL_STATES:
            continue
        if ticket.execution_state in ACTIVE_EXECUTION_STATES:
            continue
        if ticket.functional_state in BLOCKING_STATES:
            continue
        if not dependencies_met(ticket, tickets_by_id):
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
    return actionable


def claim_dispatch(board: BoardStatus, limit: int = 1) -> dict:
    actionable = find_actionable(board)[:limit]
    claimed: List[Dict[str, str]] = []
    changed_docs: List[str] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    tickets_by_id = {ticket.ticket_id: ticket for ticket in board.tickets}

    for decision in actionable:
        ticket = tickets_by_id[decision.ticket_id]
        ticket.execution_state = "running"
        ticket.current_role = decision.role
        update_board_ticket(board, ticket)
        if sync_ticket_markdown(ticket, board):
            changed_docs.append(ticket.ticket_id)
        claimed.append(
            {
                "ticket_id": ticket.ticket_id,
                "role": decision.role,
                "functional_state": ticket.functional_state,
                "execution_state": ticket.execution_state,
                "claimed_at": now,
            }
        )

    if claimed:
        save_canvas(board)

    return {
        "claimed": claimed,
        "claimed_count": len(claimed),
        "updated_docs": changed_docs,
    }
