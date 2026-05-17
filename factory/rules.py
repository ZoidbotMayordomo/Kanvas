from __future__ import annotations

ALLOWED_FUNCTIONAL_STATES = {
    "Backlog",
    "Ready for refinement",
    "Ready for architecture review",
    "Ready for implementation",
    "Ready for QA",
    "Ready for PO review",
    "Ready for human review",
    "Done",
    "Blocked",
}

ALLOWED_EXECUTION_STATES = {"idle", "running", "waiting_human", "failed"}

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
ACTIVE_EXECUTION_STATES = {"running"}

STATE_TO_COLOR = {
    "Backlog": "6",
    "Ready for refinement": "1",
    "Ready for architecture review": "1",
    "Ready for implementation": "1",
    "Ready for QA": "5",
    "Ready for PO review": "5",
    "Ready for human review": "5",
    "Done": "4",
    "Blocked": "0",
}

CANVAS_AUTHORITY_FIELDS = {
    "title",
    "functional_state",
    "execution_state",
    "current_role",
    "priority",
    "doc_path",
    "depends_on",
    "blocked_reason",
}

MARKDOWN_AUTHORITY_SECTIONS = {
    "Descripción",
    "Criterios de aceptación",
    "Dependencias",
    "Contexto relevante",
    "Decisiones",
    "Implementación",
    "QA / Security",
    "Historial de transiciones",
    "Próximo paso esperado",
}
