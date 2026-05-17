from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TicketCard:
    ticket_id: str
    title: str
    functional_state: str
    execution_state: str
    current_role: str
    priority: str
    doc_path: str
    depends_on: List[str] = field(default_factory=list)
    blocked_reason: Optional[str] = None
    node_id: str = ""
    color: str = ""


@dataclass
class DispatchDecision:
    ticket_id: str
    functional_state: str
    role: str
    reason: str


@dataclass
class BoardStatus:
    canvas_path: Path
    tickets: List[TicketCard] = field(default_factory=list)
    anomalies: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
