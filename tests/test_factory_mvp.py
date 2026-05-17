from pathlib import Path
import json
import shutil
import tempfile
import unittest

from factory.apply_output import apply_output
from factory.codex_adapter import build_codex_task_payload
from factory.dispatch import claim_dispatch, find_actionable
from factory.markdown import parse_ticket_markdown
from factory.output_contract import parse_agent_output, validate_agent_output
from factory.parser import parse_board
from factory.sync import inspect_sync, write_sync
from factory.transitions import allowed_next_states, validate_transition


class FactoryMvpTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent.parent
        self.canvas = self.repo_root / "examples" / "factory-sample.canvas"

    def make_tmp_project(self) -> Path:
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp_root = Path(tmp_dir.name)
        shutil.copy2(self.canvas, tmp_root / "factory-sample.canvas")
        shutil.copytree(self.repo_root / "examples" / "factory-tickets", tmp_root / "factory-tickets")
        return tmp_root

    def test_transitions_allow_rework_paths(self) -> None:
        self.assertIn("Ready for implementation", allowed_next_states("Done"))
        self.assertEqual(validate_transition(parse_board(self.canvas).tickets[0], "Ready for architecture review"), [])

    def test_dispatch_respects_priority_and_max_claims(self) -> None:
        tmp_root = self.make_tmp_project()
        canvas_path = tmp_root / "factory-sample.canvas"
        board = parse_board(canvas_path)
        sf04 = next(ticket for ticket in board.tickets if ticket.ticket_id == "SF-04")
        sf04.functional_state = "Ready for QA"
        sf04.execution_state = "idle"
        sf04.priority = "Baja"
        result = claim_dispatch(board, limit=1)
        self.assertEqual(result["claimed_count"], 1)
        self.assertEqual(result["claimed"][0]["ticket_id"], "SF-01")

    def test_sync_preserves_narrative_sections(self) -> None:
        tmp_root = self.make_tmp_project()
        doc = tmp_root / "factory-tickets" / "SF-01.md"
        doc.write_text(
            "# SF-01 - Old title\n\n## Metadata\n- Estado: Backlog\n\n## Description\nKeep this narrative.\n",
            encoding="utf-8",
        )
        board = parse_board(tmp_root / "factory-sample.canvas")
        result = write_sync(board)
        self.assertIn("SF-01", result["changed_docs"])
        content = doc.read_text(encoding="utf-8")
        self.assertIn("Keep this narrative.", content)
        self.assertIn("Automation mode: semi-auto", content)

    def test_output_contract_validation(self) -> None:
        issues = validate_agent_output({"ticket_id": "SF-01"})
        self.assertTrue(issues)
        payload = {
            "ticket_id": "SF-01",
            "engine": "codex",
            "automation_mode": "semi-auto",
            "from_state": "Ready for refinement",
            "to_state": "Ready for implementation",
            "summary": "Refined and ready",
        }
        parsed = parse_agent_output(payload)
        self.assertEqual(parsed.ticket_id, "SF-01")

    def test_apply_output_updates_canvas_and_markdown(self) -> None:
        tmp_root = self.make_tmp_project()
        board = parse_board(tmp_root / "factory-sample.canvas")
        payload = {
            "ticket_id": "SF-01",
            "engine": "codex",
            "automation_mode": "semi-auto",
            "from_state": "Ready for refinement",
            "to_state": "Ready for implementation",
            "summary": "Refinement completed",
            "next_step": "Implementation agent can start",
            "implementation_notes": "Acceptance criteria clarified.",
            "decisions": ["Skip architecture review for MVP scope."],
            "artifacts": ["docs/factory/workflow.md"],
        }
        result = apply_output(board, payload)
        self.assertEqual(result["transition"]["to_state"], "Ready for implementation")
        reloaded = parse_board(tmp_root / "factory-sample.canvas")
        ticket = next(ticket for ticket in reloaded.tickets if ticket.ticket_id == "SF-01")
        self.assertEqual(ticket.functional_state, "Ready for implementation")
        content = (tmp_root / "factory-tickets" / "SF-01.md").read_text(encoding="utf-8")
        self.assertIn("Implementation agent can start", content)
        self.assertIn("Skip architecture review for MVP scope.", content)

    def test_blocked_inconsistent_cases(self) -> None:
        tmp_root = self.make_tmp_project()
        board = parse_board(tmp_root / "factory-sample.canvas")
        sf03 = next(ticket for ticket in board.tickets if ticket.ticket_id == "SF-03")
        sf03.execution_state = "running"
        self.assertEqual(find_actionable(board), [decision for decision in find_actionable(board) if decision.ticket_id != "SF-03"])

    def test_end_to_end_flow(self) -> None:
        tmp_root = self.make_tmp_project()
        canvas_path = tmp_root / "factory-sample.canvas"
        board = parse_board(canvas_path)
        dispatch = claim_dispatch(board, limit=1)
        self.assertEqual(dispatch["claimed"][0]["ticket_id"], "SF-01")

        task_payload = build_codex_task_payload(parse_board(canvas_path), "SF-01")
        self.assertEqual(task_payload["adapter"], "codex")

        result = apply_output(
            parse_board(canvas_path),
            {
                "ticket_id": "SF-01",
                "engine": "codex",
                "automation_mode": "semi-auto",
                "from_state": "Ready for refinement",
                "to_state": "Ready for implementation",
                "summary": "Refinement done",
                "next_step": "Take implementation ticket",
            },
        )
        self.assertEqual(result["ticket_id"], "SF-01")
        sync = inspect_sync(parse_board(canvas_path))
        self.assertEqual(sync["missing_docs"], [])


if __name__ == "__main__":
    unittest.main()
