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
    "Description",
    "Acceptance Criteria",
    "Dependencies",
    "Relevant Context",
    "Decisions",
    "Implementation",
    "QA / Security",
    "Transition History",
    "Next Expected Step",
}

DEFAULT_MARKDOWN_SECTIONS = [
    "Description",
    "Acceptance Criteria",
    "Dependencies",
    "Relevant Context",
    "Decisions",
    "Implementation",
    "QA / Security",
    "Transition History",
    "Next Expected Step",
]

LEGAL_TRANSITIONS = {
    "Backlog": {"Ready for refinement", "Blocked"},
    "Ready for refinement": {"Ready for architecture review", "Ready for implementation", "Blocked", "Backlog"},
    "Ready for architecture review": {"Ready for implementation", "Ready for refinement", "Blocked"},
    "Ready for implementation": {"Ready for QA", "Ready for architecture review", "Ready for refinement", "Blocked"},
    "Ready for QA": {"Ready for PO review", "Ready for implementation", "Blocked"},
    "Ready for PO review": {"Done", "Ready for implementation", "Ready for refinement", "Blocked"},
    "Ready for human review": {"Done", "Ready for implementation", "Ready for refinement", "Blocked"},
    "Blocked": {
        "Backlog",
        "Ready for refinement",
        "Ready for architecture review",
        "Ready for implementation",
        "Ready for QA",
        "Ready for PO review",
        "Ready for human review",
    },
    "Done": {"Ready for implementation", "Ready for QA", "Ready for PO review", "Ready for human review", "Blocked"},
}

TRANSITION_NOTES = {
    "Backlog": "Planned but not yet routed to an agent workflow.",
    "Ready for refinement": "Needs product framing or clarification.",
    "Ready for architecture review": "Needs technical design review before implementation.",
    "Ready for implementation": "Ready for an implementation agent to execute.",
    "Ready for QA": "Implementation is complete; needs verification.",
    "Ready for PO review": "QA passed; awaiting product acceptance.",
    "Ready for human review": "Needs explicit human validation before completion.",
    "Done": "Accepted and complete.",
    "Blocked": "Cannot move forward until blocker is resolved.",
}
