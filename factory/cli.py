from __future__ import annotations

import argparse
import json
from pathlib import Path

from .apply_output import ApplyOutputError, apply_output
from .codex_adapter import write_codex_task_file
from .dispatch import claim_dispatch
from .output_contract import AgentOutputError, load_agent_output, validate_agent_output
from .parser import CanvasParseError, parse_board
from .rules import LEGAL_TRANSITIONS, STATE_TO_ROLE
from .status import summarize_board
from .sync import inspect_sync, write_sync


def cmd_status(args: argparse.Namespace) -> int:
    try:
        board = parse_board(Path(args.canvas))
    except CanvasParseError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    payload = summarize_board(board)
    payload["legal_transitions"] = {key: sorted(value) for key, value in LEGAL_TRANSITIONS.items()}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_dispatch(args: argparse.Namespace) -> int:
    try:
        board = parse_board(Path(args.canvas))
    except CanvasParseError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    if board.anomalies and not args.force:
        print(json.dumps({"error": "Board has anomalies; fix them or use --force", "anomalies": board.anomalies}, ensure_ascii=False, indent=2))
        return 1

    payload = summarize_board(board)
    payload["dry_run"] = args.dry_run
    payload["routing_table"] = STATE_TO_ROLE
    payload["max_tickets"] = args.max_tickets
    payload["automation_mode"] = args.automation_mode
    if not args.dry_run:
        payload["dispatch"] = claim_dispatch(board, limit=args.max_tickets, force=args.force, automation_mode=args.automation_mode)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    try:
        board = parse_board(Path(args.canvas))
    except CanvasParseError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    payload = {
        "canvas": args.canvas,
        "ticket_count": len(board.tickets),
        "anomalies": board.anomalies,
        "sync": inspect_sync(board),
        "write": args.write,
        "diff": args.diff,
        "message": "Factory sync inspection complete.",
    }
    if args.write:
        payload["write_result"] = write_sync(board, automation_mode=args.automation_mode)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_validate_output(args: argparse.Namespace) -> int:
    try:
        payload = load_agent_output(Path(args.output))
        issues = validate_agent_output(payload)
    except AgentOutputError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps({"valid": not issues, "issues": issues}, ensure_ascii=False, indent=2))
    return 0


def cmd_apply_output(args: argparse.Namespace) -> int:
    try:
        board = parse_board(Path(args.canvas))
        payload = load_agent_output(Path(args.output))
        result = apply_output(board, payload, force=args.force)
    except (CanvasParseError, AgentOutputError, ApplyOutputError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_codex_prepare(args: argparse.Namespace) -> int:
    try:
        board = parse_board(Path(args.canvas))
        path = write_codex_task_file(board, args.ticket_id, Path(args.output), automation_mode=args.automation_mode)
    except (CanvasParseError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps({"prepared": str(path), "ticket_id": args.ticket_id, "automation_mode": args.automation_mode}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="factory-tool", description="Factory extension CLI for Kanvas")
    parser.add_argument("canvas", help="Path to the canvas file")
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Show factory-aware status")
    p_status.set_defaults(func=cmd_status)

    p_dispatch = sub.add_parser("dispatch", help="Resolve next dispatch actions")
    p_dispatch.add_argument("--dry-run", action="store_true", default=False)
    p_dispatch.add_argument("--max-tickets", type=int, default=1)
    p_dispatch.add_argument("--force", action="store_true", default=False)
    p_dispatch.add_argument("--automation-mode", choices=["semi-auto", "full-auto", "manual"], default="semi-auto")
    p_dispatch.set_defaults(func=cmd_dispatch)

    p_sync = sub.add_parser("sync", help="Sync canvas and markdown tickets")
    p_sync.add_argument("--write", action="store_true", default=False)
    p_sync.add_argument("--diff", action="store_true", default=False)
    p_sync.add_argument("--automation-mode", choices=["semi-auto", "full-auto", "manual"], default="semi-auto")
    p_sync.set_defaults(func=cmd_sync)

    p_validate = sub.add_parser("validate-output", help="Validate a structured agent output JSON file")
    p_validate.add_argument("output", help="Path to agent output JSON")
    p_validate.set_defaults(func=cmd_validate_output)

    p_apply = sub.add_parser("apply-output", help="Apply a structured agent output JSON file to canvas and markdown")
    p_apply.add_argument("output", help="Path to agent output JSON")
    p_apply.add_argument("--force", action="store_true", default=False)
    p_apply.set_defaults(func=cmd_apply_output)

    p_codex = sub.add_parser("codex-prepare", help="Prepare a Codex-first task payload file")
    p_codex.add_argument("ticket_id", help="Ticket ID to prepare")
    p_codex.add_argument("output", help="Path to write the Codex task payload JSON")
    p_codex.add_argument("--automation-mode", choices=["semi-auto", "full-auto", "manual"], default="semi-auto")
    p_codex.set_defaults(func=cmd_codex_prepare)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
