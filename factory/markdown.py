from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

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
