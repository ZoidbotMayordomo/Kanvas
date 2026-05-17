from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List, Optional

from .models import TicketCard
from .rules import LEGAL_TRANSITIONS, STATE_TO_ROLE


class TransitionError(ValueError):
    pass


def infer_role_for_state(state: str, current_role: str = "") -> str:
    return STATE_TO_ROLE.get(state, current_role or "Human")


def allowed_next_states(state: str) -> List[str]:
    return sorted(LEGAL_TRANSITIONS.get(state, set()))


def validate_transition(ticket: TicketCard, to_state: str, *, force: bool = False, reason: Optional[str] = None) -> List[str]:
    issues: List[str] = []
    if to_state == ticket.functional_state:
        return issues

    allowed = LEGAL_TRANSITIONS.get(ticket.functional_state, set())
    if to_state not in allowed and not force:
        issues.append(
            f"Illegal transition for {ticket.ticket_id}: {ticket.functional_state} -> {to_state}; allowed: {', '.join(sorted(allowed)) or 'none'}"
        )

    if to_state == "Blocked" and not (reason or ticket.blocked_reason):
        issues.append(f"{ticket.ticket_id}: blocking reason is required when transitioning to Blocked")

    if to_state == "Done" and ticket.execution_state == "running" and not force:
        issues.append(f"{ticket.ticket_id}: cannot move directly to Done while execution is running")

    return issues


def apply_transition(
    ticket: TicketCard,
    to_state: str,
    *,
    force: bool = False,
    reason: Optional[str] = None,
    execution_state: Optional[str] = None,
    current_role: Optional[str] = None,
) -> Dict[str, str]:
    issues = validate_transition(ticket, to_state, force=force, reason=reason)
    if issues:
        raise TransitionError("; ".join(issues))

    before = asdict(ticket)
    ticket.functional_state = to_state
    ticket.current_role = current_role if current_role is not None else infer_role_for_state(to_state, ticket.current_role)
    ticket.execution_state = execution_state if execution_state is not None else ("waiting_human" if to_state in {"Done", "Ready for human review", "Ready for PO review"} else "idle")
    ticket.blocked_reason = reason if to_state == "Blocked" else None
    return {
        "ticket_id": ticket.ticket_id,
        "from_state": before["functional_state"],
        "to_state": ticket.functional_state,
        "from_execution_state": before["execution_state"],
        "to_execution_state": ticket.execution_state,
        "role": ticket.current_role,
    }
