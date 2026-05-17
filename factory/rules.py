from __future__ import annotations

STATE_TO_ROLE = {
    "Ready for refinement": "Product Owner",
    "Ready for architecture review": "Architect",
    "Ready for implementation": "Implementation Engineer",
    "Ready for QA": "Quality + Security Gate",
    "Ready for PO review": "Product Owner",
    "Ready for human review": "Human",
}

TERMINAL_STATES = {"Done"}
BLOCKING_STATES = {"Blocked"}
INACTIVE_EXECUTION_STATES = {"idle", "failed", "waiting_human"}
