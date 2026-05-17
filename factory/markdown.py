from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from .models import AgentOutput, BoardStatus, TicketCard
from .rules import DEFAULT_MARKDOWN_SECTIONS

TICKET_TITLE_RE = re.compile(r"^#\s+(?P<ticket_id>[A-Z]+-\d+)\s+-\s+(?P<title>.+?)\s*$")
META_RE = re.compile(
    r"^-\s+(?P<key>Estado|Execution state|Rol actual|Prioridad|Agente activo|Último run|Doc canvas|Automation mode):\s*(?P<value>.*)$"
)
SECTION_RE = re.compile(r"^##\s+(?P<section>.+?)\s*$")


def parse_ticket_markdown(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {"path": str(path)}
    lines = path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if "ticket_id" not in data:
            match = TICKET_TITLE_RE.match(line.strip())
            if match:
                data["ticket_id"] = match.group("ticket_id")
                data["title"] = match.group("title")
                continue
        meta = META_RE.match(line.strip())
        if meta:
            data[meta.group("key")] = meta.group("value").strip()
    return data


def ensure_ticket_markdown(path: Path, ticket: TicketCard, board: BoardStatus) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {ticket.ticket_id} - {ticket.title}", "", "## Metadata", ""]
    lines.extend(
        [
            f"- Estado: {ticket.functional_state}",
            f"- Execution state: {ticket.execution_state}",
            f"- Rol actual: {ticket.current_role}",
            f"- Prioridad: {ticket.priority}",
            "- Agente activo: ",
            "- Último run: ",
            f"- Doc canvas: {board.canvas_path.name}",
            "- Automation mode: semi-auto",
            "",
        ]
    )
    for section in DEFAULT_MARKDOWN_SECTIONS:
        lines.append(f"## {section}")
        lines.append("- ")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def sync_ticket_markdown(ticket: TicketCard, board: BoardStatus, automation_mode: str = "semi-auto") -> bool:
    path = (board.canvas_path.parent / ticket.doc_path).resolve()
    ensure_ticket_markdown(path, ticket, board)
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()

    header = f"# {ticket.ticket_id} - {ticket.title}"
    if lines:
        if TICKET_TITLE_RE.match(lines[0].strip()):
            lines[0] = header
        else:
            lines.insert(0, header)
            lines.insert(1, "")
    else:
        lines = [header, "", "## Metadata"]

    metadata_index = None
    for idx, line in enumerate(lines):
        if line.strip() == "## Metadata":
            metadata_index = idx
            break
    if metadata_index is None:
        insert_at = 2 if len(lines) >= 2 else len(lines)
        lines[insert_at:insert_at] = ["## Metadata", ""]
        metadata_index = insert_at

    next_section = len(lines)
    for idx in range(metadata_index + 1, len(lines)):
        if lines[idx].startswith("## "):
            next_section = idx
            break

    desired = {
        "Estado": ticket.functional_state,
        "Execution state": ticket.execution_state,
        "Rol actual": ticket.current_role,
        "Prioridad": ticket.priority,
        "Doc canvas": board.canvas_path.name,
        "Automation mode": automation_mode,
    }

    section_lines = lines[metadata_index + 1 : next_section]
    existing: Dict[str, int] = {}
    for rel_idx, line in enumerate(section_lines):
        meta = META_RE.match(line.strip())
        if meta:
            existing[meta.group("key")] = metadata_index + 1 + rel_idx

    insertion_point = next_section
    for key, value in desired.items():
        rendered = f"- {key}: {value}"
        if key in existing:
            lines[existing[key]] = rendered
        else:
            lines.insert(insertion_point, rendered)
            insertion_point += 1

    new_content = "\n".join(lines).rstrip() + "\n"
    if new_content == original:
        return False
    path.write_text(new_content, encoding="utf-8")
    return True


def _get_section_bounds(lines: List[str], section: str) -> tuple[int | None, int | None]:
    start = None
    end = None
    for idx, line in enumerate(lines):
        match = SECTION_RE.match(line.strip())
        if not match:
            continue
        if match.group("section") == section:
            start = idx
            end = len(lines)
            for inner in range(idx + 1, len(lines)):
                if SECTION_RE.match(lines[inner].strip()):
                    end = inner
                    break
            return start, end
    return None, None


def replace_section(lines: List[str], section: str, block_lines: List[str]) -> List[str]:
    start, end = _get_section_bounds(lines, section)
    rendered = [f"## {section}"] + block_lines + [""]
    if start is None:
        if lines and lines[-1] != "":
            lines = lines + [""]
        return lines + rendered
    return lines[:start] + rendered + lines[end:]


def append_bullets(lines: List[str], section: str, bullets: List[str]) -> List[str]:
    if not bullets:
        return lines
    start, end = _get_section_bounds(lines, section)
    if start is None:
        return replace_section(lines, section, [f"- {item}" for item in bullets])
    section_lines = lines[start:end]
    existing = set(line.strip() for line in section_lines[1:])
    insertion = lines[:end]
    for item in bullets:
        rendered = f"- {item}"
        if rendered.strip() not in existing:
            insertion.append(rendered)
    return insertion + lines[end:]


def apply_agent_output_to_markdown(ticket: TicketCard, board: BoardStatus, output: AgentOutput) -> bool:
    path = (board.canvas_path.parent / ticket.doc_path).resolve()
    ensure_ticket_markdown(path, ticket, board)
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()

    lines = replace_section(lines, "Next Expected Step", [f"- {output.next_step or 'Review latest changes and continue.'}"])
    if output.implementation_notes:
        lines = replace_section(lines, "Implementation", [f"- Summary: {output.implementation_notes}"] + [f"- Artifact: {item}" for item in output.artifacts])
    elif output.artifacts:
        lines = append_bullets(lines, "Implementation", [f"Artifact: {item}" for item in output.artifacts])
    if output.qa_notes:
        lines = replace_section(lines, "QA / Security", [f"- {output.qa_notes}"])
    if output.decisions:
        lines = append_bullets(lines, "Decisions", output.decisions)
    history_lines = [
        f"- {entry}" for entry in (
            output.transition_history
            or [f"{output.engine} moved {ticket.ticket_id} from {output.from_state} to {output.to_state}: {output.summary}"]
        )
    ]
    lines = append_bullets(lines, "Transition History", [item[2:] for item in history_lines])

    if output.blockers:
        lines = replace_section(lines, "Dependencies", [f"- Blocker: {item}" for item in output.blockers])

    new_content = "\n".join(lines).rstrip() + "\n"
    if new_content == original:
        return False
    path.write_text(new_content, encoding="utf-8")
    return True
