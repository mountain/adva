"""Meaningful positive, negative and orientation controls for the obstruction.

Authored by ChatGPT (OpenAI), through Mingli Yuan's account as proxy.
Project-original contribution under Unknown v0.3.
"""
import unittest

from experiments.pascal_spectre_patch.obstruction import (
    DEFAULT_CANDIDATE, DEFAULT_SHA256, check_polygon, load_points,
)


class PascalSpectreObstructionTests(unittest.TestCase):
    def test_candidate_and_reversed_orientation(self):
        points, digest = load_points(DEFAULT_CANDIDATE)
        self.assertEqual(digest, DEFAULT_SHA256)
        result = check_polygon(points)
        self.assertTrue(result["obstructed"])
        self.assertEqual(result["certificate"]["corner"], 4)
        self.assertTrue(result["all_edge_lengths_distinct"])
        self.assertTrue(all(c["strictly_greater_than_complement"]
                            for c in result["certificate"]["comparisons"]))
        reversed_result = check_polygon(list(reversed(points)))
        self.assertTrue(reversed_result["obstructed"])
        self.assertEqual(reversed_result["certificate"]["corner"], len(points) - 1 - 4)
        self.assertNotEqual(result["input_orientation"], reversed_result["input_orientation"])

    def test_square_does_not_trigger_sufficient_obstruction(self):
        result = check_polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        self.assertFalse(result["obstructed"])
        self.assertEqual(result["status"], "NoObstructionFound")
        self.assertIsNone(result["certificate"])
        self.assertFalse(result["all_edge_lengths_distinct"])
        # Equality cannot be accepted as a strictly unfillable wedge.
        equal_angle = check_polygon([(0, 0), (2, 0), (2, 1), (1, 1), (1, 2), (0, 2)])
        self.assertFalse(equal_angle["obstructed"])
        self.assertIsNotNone(equal_angle["certificate"])

    def test_invalid_geometry_and_inexact_input_are_rejected(self):
        for points in (
            [(0, 0), (1, 0), (2, 0), (1, 1)],  # Collinear corner.
            [(0, 0), (1, 1), (0, 1), (1, 0)],  # Crossing boundary.
            [(0, 0), (1.0, 0), (1, 1), (0, 1)],
            [(0, 0), (True, 0), (1, 1), (0, 1)],
        ):
            with self.subTest(points=points), self.assertRaises(ValueError):
                check_polygon(points)


if __name__ == "__main__":
    unittest.main()
