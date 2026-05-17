from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from .io import find_ticket, save_canvas, update_board_ticket
from .markdown import apply_agent_output_to_markdown, sync_ticket_markdown
from .models import BoardStatus
from .output_contract import AgentOutputError, parse_agent_output
from .transitions import TransitionError, apply_transition


class ApplyOutputError(ValueError):
    pass


def apply_output(board: BoardStatus, payload: Dict[str, object], *, force: bool = False) -> dict:
    try:
        output = parse_agent_output(payload)
    except AgentOutputError as exc:
        raise ApplyOutputError(str(exc)) from exc

    ticket = find_ticket(board, output.ticket_id)
    if output.from_state != ticket.functional_state and not force:
        raise ApplyOutputError(
            f"Ticket {ticket.ticket_id} is in state {ticket.functional_state}, but output expects {output.from_state}"
        )

    block_reason = "; ".join(output.blockers) if output.blockers else None
    try:
        transition = apply_transition(
            ticket,
            output.to_state,
            force=force,
            reason=block_reason,
            execution_state="waiting_human" if output.automation_mode == "semi-auto" else "idle",
        )
    except TransitionError as exc:
        raise ApplyOutputError(str(exc)) from exc

    update_board_ticket(board, ticket)
    sync_ticket_markdown(ticket, board, automation_mode=output.automation_mode)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if not output.transition_history:
        output.transition_history = [
            f"{timestamp} | {output.engine} | {output.from_state} -> {output.to_state} | {output.summary}"
        ]
    apply_agent_output_to_markdown(ticket, board, output)
    save_canvas(board)

    return {
        "ticket_id": ticket.ticket_id,
        "transition": transition,
        "automation_mode": output.automation_mode,
        "engine": output.engine,
        "summary": output.summary,
    }
