"""Literal graph expectations: catches reuse, skipped augmentation and bad empties."""
import unittest
from validation.graph_oracle import max_cardinality


class GraphOracleTests(unittest.TestCase):
    def test_trap_needs_reassignment(self):
        self.assertEqual(max_cardinality([[0, 1], [0]], 2), 2)

    def test_duplicate_predictions_are_one_to_one(self):
        self.assertEqual(max_cardinality([[0], [0], [0]], 1), 1)
        self.assertEqual(max_cardinality([[0, 1, 2]], 3), 1)

    def test_empty_and_isolated(self):
        for graph, count in [([], 0), ([], 3), ([[]], 0), ([[], []], 3)]:
            with self.subTest(graph=graph, predictions=count):
                self.assertEqual(max_cardinality(graph, count), 0)
        self.assertEqual(max_cardinality([[], [1], [], [0, 1]], 3), 2)

    def test_complete_rectangles(self):
        self.assertEqual(max_cardinality([[0, 1]] * 3, 2), 2)
        self.assertEqual(max_cardinality([[0, 1, 2]] * 2, 3), 2)

    def test_hall_deficiency_despite_nonempty_rows(self):
        self.assertEqual(max_cardinality([[0], [0], [1, 2]], 3), 2)

    def test_longer_reassignment(self):
        self.assertEqual(max_cardinality([[0, 1], [1, 2], [2, 3], [0]], 4), 4)
