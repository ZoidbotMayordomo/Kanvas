from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


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


@dataclass
class DispatchDecision:
    ticket_id: str
    functional_state: str
    role: str
    reason: str
