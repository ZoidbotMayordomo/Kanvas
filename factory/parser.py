from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from .models import BoardStatus, TicketCard
from .rules import ALLOWED_EXECUTION_STATES, ALLOWED_FUNCTIONAL_STATES

TICKET_HEADER_RE = re.compile(r"^##\s+(?P<ticket_id>[A-Z]+-\d+)\s+(?P<title>.+?)\s*$")
FIELD_RE = re.compile(r"^(?P<key>Estado|Execution|Rol actual|Prioridad|Doc|Depends on|Bloqueo):\s*(?P<value>.*)$")


class CanvasParseError(ValueError):
    pass


def load_canvas(canvas_path: Path) -> Dict[str, Any]:
    try:
        return json.loads(canvas_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CanvasParseError(f"Canvas file not found: {canvas_path}") from exc
    except json.JSONDecodeError as exc:
        raise CanvasParseError(f"Invalid canvas JSON: {canvas_path}: {exc}") from exc


def parse_ticket_node(node: Dict[str, Any]) -> Tuple[TicketCard | None, List[str]]:
    text = node.get("text", "")
    if not text or not isinstance(text, str):
        return None, []

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None, []

    header_match = TICKET_HEADER_RE.match(lines[0])
    if not header_match:
        return None, []

    fields: Dict[str, str] = {}
    anomalies: List[str] = []

    for line in lines[1:]:
        field_match = FIELD_RE.match(line)
        if field_match:
            fields[field_match.group("key")] = field_match.group("value").strip()

    missing_fields = [key for key in ("Estado", "Execution", "Rol actual", "Prioridad", "Doc", "Depends on") if key not in fields]
    if missing_fields:
        anomalies.append(f"{header_match.group('ticket_id')}: missing fields: {', '.join(missing_fields)}")

    functional_state = fields.get("Estado", "")
    execution_state = fields.get("Execution", "")
    current_role = fields.get("Rol actual", "")
    priority = fields.get("Prioridad", "")
    doc_path = fields.get("Doc", "")
    depends_raw = fields.get("Depends on", "")
    blocked_reason = fields.get("Bloqueo") or None
    depends_on = [item.strip() for item in depends_raw.split(",") if item.strip() and item.strip() != "-"]

    ticket = TicketCard(
        ticket_id=header_match.group("ticket_id"),
        title=header_match.group("title").strip(),
        functional_state=functional_state,
        execution_state=execution_state,
        current_role=current_role,
        priority=priority,
        doc_path=doc_path,
        depends_on=depends_on,
        blocked_reason=blocked_reason,
        node_id=node.get("id", ""),
        color=node.get("color", ""),
    )

    if functional_state and functional_state not in ALLOWED_FUNCTIONAL_STATES:
        anomalies.append(f"{ticket.ticket_id}: invalid functional state '{functional_state}'")
    if execution_state and execution_state not in ALLOWED_EXECUTION_STATES:
        anomalies.append(f"{ticket.ticket_id}: invalid execution state '{execution_state}'")
    if ticket.functional_state == "Blocked" and not ticket.blocked_reason:
        anomalies.append(f"{ticket.ticket_id}: blocked ticket without blocking reason")
    if ticket.functional_state != "Blocked" and ticket.blocked_reason:
        anomalies.append(f"{ticket.ticket_id}: blocking reason present outside Blocked state")
    if not ticket.doc_path:
        anomalies.append(f"{ticket.ticket_id}: missing Doc path")

    return ticket, anomalies


def parse_board(canvas_path: Path) -> BoardStatus:
    payload = load_canvas(canvas_path)
    nodes = payload.get("nodes", [])
    tickets: List[TicketCard] = []
    anomalies: List[str] = []

    for node in nodes:
        ticket, ticket_anomalies = parse_ticket_node(node)
        if ticket:
            tickets.append(ticket)
            anomalies.extend(ticket_anomalies)

    tickets_by_id = {ticket.ticket_id: ticket for ticket in tickets}
    for ticket in tickets:
        for dep in ticket.depends_on:
            if dep not in tickets_by_id:
                anomalies.append(f"{ticket.ticket_id}: dependency '{dep}' not found on canvas")
        if ticket.doc_path:
            doc_full_path = (canvas_path.parent / ticket.doc_path).resolve()
            if not doc_full_path.exists():
                anomalies.append(f"{ticket.ticket_id}: doc file not found '{ticket.doc_path}'")

    return BoardStatus(canvas_path=canvas_path, tickets=tickets, anomalies=sorted(set(anomalies)), payload=payload)


def count_by_state(tickets: Iterable[TicketCard]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for ticket in tickets:
        counts[ticket.functional_state] = counts.get(ticket.functional_state, 0) + 1
    return dict(sorted(counts.items()))
