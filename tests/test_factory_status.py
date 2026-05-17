from pathlib import Path
import shutil
import tempfile
import unittest

from factory.dispatch import claim_dispatch
from factory.markdown import parse_ticket_markdown
from factory.parser import parse_board
from factory.status import summarize_board
from factory.sync import inspect_sync, write_sync


class FactoryStatusTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent.parent
        self.canvas = self.repo_root / "examples" / "factory-sample.canvas"
        self.board = parse_board(self.canvas)

    def test_sample_board_has_one_actionable_ticket(self) -> None:
        summary = summarize_board(self.board)

        self.assertEqual(summary["ticket_count"], 4)
        self.assertEqual(summary["anomalies"], [])
        self.assertEqual(len(summary["actionable"]), 1)
        self.assertEqual(summary["actionable"][0]["ticket_id"], "SF-01")
        self.assertEqual(summary["actionable"][0]["role"], "Product Owner")

    def test_sample_board_sync_has_no_mismatches(self) -> None:
        sync = inspect_sync(self.board)

        self.assertEqual(sync["checked_docs"], 4)
        self.assertEqual(sync["missing_docs"], [])
        self.assertEqual(sync["mismatches"], [])

    def test_sync_write_updates_markdown_from_canvas_authority_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            shutil.copy2(self.canvas, tmp_root / "factory-sample.canvas")
            shutil.copytree(self.repo_root / "examples" / "factory-tickets", tmp_root / "factory-tickets")

            doc = tmp_root / "factory-tickets" / "SF-01.md"
            doc.write_text(
                "# SF-01 - Título viejo\n\n## Metadata\n- Estado: Backlog\n- Execution state: failed\n- Rol actual: Nadie\n- Prioridad: Baja\n\n## Description\nDo not touch this section.\n",
                encoding="utf-8",
            )

            board = parse_board(tmp_root / "factory-sample.canvas")
            result = write_sync(board)
            updated = parse_ticket_markdown(doc)
            content = doc.read_text(encoding="utf-8")

            self.assertIn("SF-01", result["changed_docs"])
            self.assertEqual(updated["title"], "Definir workflow canónico")
            self.assertEqual(updated["Estado"], "Ready for refinement")
            self.assertEqual(updated["Execution state"], "idle")
            self.assertEqual(updated["Rol actual"], "Product Owner")
            self.assertIn("Do not touch this section.", content)

    def test_dispatch_claim_marks_ticket_running_and_syncs_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            shutil.copy2(self.canvas, tmp_root / "factory-sample.canvas")
            shutil.copytree(self.repo_root / "examples" / "factory-tickets", tmp_root / "factory-tickets")

            board = parse_board(tmp_root / "factory-sample.canvas")
            result = claim_dispatch(board, limit=1)
            reloaded = parse_board(tmp_root / "factory-sample.canvas")
            updated = parse_ticket_markdown(tmp_root / "factory-tickets" / "SF-01.md")

            self.assertEqual(result["claimed_count"], 1)
            self.assertEqual(result["claimed"][0]["ticket_id"], "SF-01")
            sf01 = next(ticket for ticket in reloaded.tickets if ticket.ticket_id == "SF-01")
            self.assertEqual(sf01.execution_state, "running")
            self.assertEqual(updated["Execution state"], "running")


if __name__ == "__main__":
    unittest.main()
