from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from .io import find_ticket, save_canvas, update_board_ticket
from .markdown import sync_ticket_markdown
from .models import BoardStatus, DispatchDecision, TicketCard
from .rules import ACTIVE_EXECUTION_STATES, BLOCKING_STATES, STATE_TO_ROLE, TERMINAL_STATES

PRIORITY_ORDER = {"Critical": 0, "Alta": 1, "High": 1, "Media": 2, "Medium": 2, "Baja": 3, "Low": 3, "": 99}
STALE_EXECUTION_STATES = {"running"}


def dependencies_met(ticket: TicketCard, tickets_by_id: Dict[str, TicketCard]) -> bool:
    for dep in ticket.depends_on:
        dep_ticket = tickets_by_id.get(dep)
        if not dep_ticket or dep_ticket.functional_state != "Done":
            return False
    return True


def detect_inconsistencies(ticket: TicketCard) -> List[str]:
    issues: List[str] = []
    if ticket.functional_state == "Blocked" and ticket.execution_state == "running":
        issues.append("blocked ticket cannot be running")
    if ticket.functional_state == "Done" and ticket.execution_state == "running":
        issues.append("done ticket cannot be running")
    if ticket.functional_state != "Blocked" and ticket.blocked_reason:
        issues.append("blocking reason present outside Blocked state")
    return issues


def ticket_sort_key(ticket: TicketCard) -> tuple[int, str]:
    return (PRIORITY_ORDER.get(ticket.priority, 50), ticket.ticket_id)


def running_or_stale(board: BoardStatus) -> List[dict]:
    flagged: List[dict] = []
    for ticket in sorted(board.tickets, key=ticket_sort_key):
        if ticket.execution_state in STALE_EXECUTION_STATES:
            flagged.append(
                {
                    "ticket_id": ticket.ticket_id,
                    "execution_state": ticket.execution_state,
                    "reason": "ticket already marked running; verify whether work is active or stale",
                }
            )
    return flagged


def find_actionable(board: BoardStatus) -> List[DispatchDecision]:
    tickets_by_id = {ticket.ticket_id: ticket for ticket in board.tickets}
    actionable: List[DispatchDecision] = []

    for ticket in sorted(board.tickets, key=ticket_sort_key):
        if ticket.functional_state in TERMINAL_STATES:
            continue
        if ticket.execution_state in ACTIVE_EXECUTION_STATES:
            continue
        if ticket.functional_state in BLOCKING_STATES:
            continue
        if detect_inconsistencies(ticket):
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


def claim_dispatch(board: BoardStatus, limit: int = 1, force: bool = False, automation_mode: str = "semi-auto") -> dict:
    actionable = find_actionable(board)
    rejected: List[dict] = []
    claimed: List[Dict[str, str]] = []
    changed_docs: List[str] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    for decision in actionable:
        if len(claimed) >= limit:
            break
        ticket = find_ticket(board, decision.ticket_id)
        issues = detect_inconsistencies(ticket)
        if issues and not force:
            rejected.append({"ticket_id": ticket.ticket_id, "reasons": issues})
            continue
        ticket.execution_state = "running"
        ticket.current_role = decision.role
        update_board_ticket(board, ticket)
        if sync_ticket_markdown(ticket, board, automation_mode=automation_mode):
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
        "rejected": rejected,
        "running_or_stale": running_or_stale(board),
    }
