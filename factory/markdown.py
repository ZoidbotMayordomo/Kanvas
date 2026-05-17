from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

from .models import BoardStatus, TicketCard

TICKET_TITLE_RE = re.compile(r"^#\s+(?P<ticket_id>[A-Z]+-\d+)\s+-\s+(?P<title>.+?)\s*$")
META_RE = re.compile(r"^-\s+(?P<key>Estado|Execution state|Rol actual|Prioridad|Agente activo|Último run|Doc canvas):\s*(?P<value>.*)$")


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


def sync_ticket_markdown(ticket: TicketCard, board: BoardStatus) -> bool:
    path = (board.canvas_path.parent / ticket.doc_path).resolve()
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
