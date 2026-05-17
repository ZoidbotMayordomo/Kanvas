from pathlib import Path
import unittest

from factory.parser import parse_board
from factory.status import summarize_board
from factory.sync import inspect_sync


class FactoryStatusTest(unittest.TestCase):
    def setUp(self) -> None:
        self.canvas = Path(__file__).resolve().parent.parent / "examples" / "factory-sample.canvas"
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


if __name__ == "__main__":
    unittest.main()
