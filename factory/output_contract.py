from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .models import AgentOutput
from .rules import ALLOWED_FUNCTIONAL_STATES

ALLOWED_AUTOMATION_MODES = {"semi-auto", "full-auto", "manual"}
REQUIRED_FIELDS = {
    "ticket_id",
    "engine",
    "automation_mode",
    "from_state",
    "to_state",
    "summary",
}


class AgentOutputError(ValueError):
    pass


def load_agent_output(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AgentOutputError(f"Agent output file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AgentOutputError(f"Invalid agent output JSON: {path}: {exc}") from exc


def validate_agent_output(payload: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    missing = sorted(REQUIRED_FIELDS - payload.keys())
    if missing:
        issues.append(f"Missing required fields: {', '.join(missing)}")

    automation_mode = payload.get("automation_mode")
    if automation_mode and automation_mode not in ALLOWED_AUTOMATION_MODES:
        issues.append(f"Invalid automation_mode '{automation_mode}'")

    for key in ("from_state", "to_state"):
        state = payload.get(key)
        if state and state not in ALLOWED_FUNCTIONAL_STATES:
            issues.append(f"Invalid {key} '{state}'")

    for list_field in ("decisions", "artifacts", "blockers", "transition_history"):
        value = payload.get(list_field, [])
        if value is not None and not isinstance(value, list):
            issues.append(f"Field '{list_field}' must be a list")

    return issues


def parse_agent_output(payload: Dict[str, Any]) -> AgentOutput:
    issues = validate_agent_output(payload)
    if issues:
        raise AgentOutputError("; ".join(issues))

    return AgentOutput(
        ticket_id=str(payload["ticket_id"]),
        engine=str(payload["engine"]),
        automation_mode=str(payload["automation_mode"]),
        from_state=str(payload["from_state"]),
        to_state=str(payload["to_state"]),
        summary=str(payload["summary"]),
        next_step=str(payload.get("next_step", "")),
        implementation_notes=str(payload.get("implementation_notes", "")),
        qa_notes=str(payload.get("qa_notes", "")),
        decisions=[str(item) for item in payload.get("decisions", [])],
        artifacts=[str(item) for item in payload.get("artifacts", [])],
        blockers=[str(item) for item in payload.get("blockers", [])],
        transition_history=[str(item) for item in payload.get("transition_history", [])],
        raw_payload=payload,
    )
