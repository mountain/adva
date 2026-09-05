from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiments.knowledge_geometry.interface_witness import (
    COARSE_MASKS, FIXTURE, NODES, apply_operation, build_report, check_fixture, coordinates,
    encoded_report, mismatches, paths, search_refinement,
)


class KnowledgeInterfaceTests(unittest.TestCase):
    def test_complete_search_matches_analytic_two_coordinate_bound(self):
        result = search_refinement()
        self.assertEqual(result["status"], "Found")
        self.assertEqual(result["minimum_added_coordinates"], 2)
        self.assertEqual(result["added_masks"], [10, 12])
        self.assertEqual(len(result["checked"]), 4)
        self.assertEqual(mismatches(COARSE_MASKS + (10, 12)), [])

    def test_one_new_bit_distinguishes_objects_but_invents_order(self):
        for mask in (10, 12):
            self.assertEqual(len(set(coordinates(COARSE_MASKS + (mask,)))), 4)
            errors = mismatches(COARSE_MASKS + (mask,))
            self.assertEqual(len(errors), 1)
            self.assertFalse(errors[0]["declared_order"])
            self.assertTrue(errors[0]["coordinate_order"])
            self.assertEqual({errors[0]["left"], errors[0]["right"]}, {"b", "c"})

    def test_fuel_exhaustion_retains_unknown_and_next_candidate(self):
        for fuel in range(4):
            result = search_refinement(fuel)
            self.assertEqual(result["status"], "Unknown")
            self.assertEqual(len(result["checked"]), fuel)
            self.assertGreater(result["remaining_families"], 0)
        self.assertEqual(search_refinement(3)["next_family"], [10, 12])
        with self.assertRaises(ValueError):
            search_refinement(-1)

    def test_scalar_oracle_checks_both_execution_routes(self):
        report = build_report()
        for record in report["execution"]["commutation"]:
            a, b, c, d = record["input"]
            reference = sorted((a, b)) + sorted((c, d))
            self.assertEqual(record["B_then_C"][-1], reference)
            self.assertEqual(record["C_then_B"][-1], reference)
        self.assertEqual(len(report["execution"]["commutation"]), 16)

    def test_equal_endpoints_preserve_both_paths_and_budget(self):
        routes = [p for p in paths() if p["source"] == "a" and p["target"] == "d"]
        self.assertEqual({tuple(p["operations"]) for p in routes}, {("B", "C"), ("C", "B")})
        self.assertEqual({p["cost_in_operations"] for p in routes}, {2})
        report = build_report()
        self.assertEqual(report["execution"]["path_count"], 10)
        self.assertEqual(report["execution"]["endpoint_pair_count"], 9)
        self.assertNotIn(["a", "d"], report["budget"]["reachable_pairs_at_one"])
        self.assertIn(["a", "d"], report["budget"]["reachable_pairs_at_two"])

    def test_duality_is_not_an_inverse_or_a_sorting_proof(self):
        report = build_report()
        views = report["views"]
        for node in NODES:
            self.assertEqual([1 - v for v in views["opposite"][node]], list(views["refined"][node]))
        self.assertEqual(apply_operation((0, 1, 0, 0), "B"), apply_operation((1, 0, 0, 0), "B"))
        output = report["execution"]["whole_network_sorting_counterexample"]["output"]
        self.assertNotEqual(output, sorted(output))
        with self.assertRaises(ValueError):
            apply_operation((False, 1, 0, 0), "B")

    def test_frozen_fixture_replays_every_field(self):
        self.assertEqual(FIXTURE.read_bytes(), encoded_report().encode("utf-8"))
        check_fixture(FIXTURE)
        record = json.loads(FIXTURE.read_text())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            for section in ("execution", "views", "open_obligations"):
                forged = dict(record)
                forged[section] = None
                path.write_text(json.dumps(forged), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "differs"):
                    check_fixture(path)


if __name__ == "__main__":
    unittest.main()
