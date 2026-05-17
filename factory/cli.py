from __future__ import annotations

import argparse
import json
from pathlib import Path

from .parser import CanvasParseError, parse_board
from .rules import STATE_TO_ROLE
from .status import summarize_board
from .sync import inspect_sync


def cmd_status(args: argparse.Namespace) -> int:
    try:
        board = parse_board(Path(args.canvas))
    except CanvasParseError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    payload = summarize_board(board)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_dispatch(args: argparse.Namespace) -> int:
    try:
        board = parse_board(Path(args.canvas))
    except CanvasParseError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    payload = summarize_board(board)
    payload["dry_run"] = args.dry_run
    payload["routing_table"] = STATE_TO_ROLE
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
        "message": "Factory sync inspection complete.",
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="factory-tool", description="Factory extension CLI for Kanvas")
    parser.add_argument("canvas", help="Path to the canvas file")
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Show factory-aware status")
    p_status.set_defaults(func=cmd_status)

    p_dispatch = sub.add_parser("dispatch", help="Resolve next dispatch actions")
    p_dispatch.add_argument("--dry-run", action="store_true", default=False)
    p_dispatch.set_defaults(func=cmd_dispatch)

    p_sync = sub.add_parser("sync", help="Sync canvas and markdown tickets")
    p_sync.set_defaults(func=cmd_sync)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
