from copy import deepcopy
from pathlib import Path
import unittest

from experiments.structural_adjustment import calibration as c


class StructuralAdjustmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # No process-wide limits in shared pytest; standalone CLI owns those.
        root = Path(__file__).resolve().parents[2]
        cls.a = c.load_file(root / "examples/verified_witness/structural-adjustment-f7.json")
        cls.meter = c.Meter()

    def test_complete_artifact_replay(self):
        c.verify_artifact(self.a, self.meter)
        self.assertEqual(self.a["cases"][0]["receipt"]["status"], "AcceptedAdjustment")

    def test_coordinate_transport_and_blind_copy_counterexample(self):
        first = self.a["cases"][0]
        p = first["proposal"]
        self.assertEqual(p["observation_location"], 6)
        self.assertEqual(p["rows"][22]["claimed"], 1)
        self.assertEqual(p["rows"][22]["actual"], 6)
        self.assertEqual(p["rows"][22]["verdict"], "Refuted")
        bad = deepcopy(p)
        bad["observation_location"] = 1
        with self.assertRaises(ValueError):
            c.judge(bad, first["before"], 24, self.meter)

    def test_reorganization_retains_expression_and_history(self):
        case = self.a["cases"][0]
        p, receipt = case["proposal"], case["receipt"]
        self.assertEqual(p["expanded_coefficients"], [2,0,6])
        self.assertEqual([r["before"] for r in p["rows"][8:15]],
                         [r["after"] for r in p["rows"][8:15]])
        history = receipt["state"]["history"]
        self.assertEqual([h["event"] for h in history],
                         ["source_observation", "switch", "reorganize", "revise"])
        self.assertNotEqual(history[2]["from"], history[2]["to"])
        bad = deepcopy(p)
        bad["expanded_coefficients"][2] = 5
        with self.assertRaises(ValueError):
            c.judge(bad, case["before"], 24, self.meter)

    def test_revision_changes_applicability_not_old_truth(self):
        case = self.a["cases"][0]
        observations = case["receipt"]["state"]["observations"]
        self.assertEqual([(o["x"],o["value"]) for o in observations], [(0,1),(6,1),(6,1),(6,2)])
        self.assertEqual(observations[:1], case["before"]["observations"])
        self.assertEqual(case["proposal"]["rows"][23]["actual"], 2)
        self.assertEqual(case["before"], c.initial(case["proposal"]["spec"]))
        self.assertEqual(len({o["task"] for o in observations}), 4)

    def test_fresh_instance_uses_same_recipe(self):
        first, second = self.a["cases"]
        self.assertEqual(first["proposal"]["recipe"], second["proposal"]["recipe"])
        self.assertNotEqual(first["proposal"]["source_state"], second["proposal"]["source_state"])
        self.assertEqual(second["proposal"]["expanded_coefficients"], [1,6,4])
        observations = second["receipt"]["state"]["observations"]
        self.assertEqual([(o["x"],o["value"]) for o in observations], [(0,3),(5,3),(5,3),(5,5)])

    def test_pending_never_commits_and_forged_receipt_is_rejected(self):
        first = self.a["cases"][0]
        for r, fuel in zip(self.a["pending"], (0,2)):
            self.assertEqual(r["status"], "Unknown")
            self.assertEqual(r["state"], first["before"])
            self.assertEqual(r["checked_rows"], fuel)
            self.assertEqual(r["pending"]["remaining_rows"], list(range(fuel,24)))
        expected = c.judge(first["proposal"], first["before"], 2, self.meter)
        bad = deepcopy(expected)
        bad["status"] = "AcceptedAdjustment"
        with self.assertRaises(ValueError):
            c.equal(bad, expected, "forged acceptance")

    def test_missing_rows_scalar_tamper_and_stale_binding(self):
        case = self.a["cases"][0]
        bad = deepcopy(case["proposal"])
        bad["rows"].pop()
        with self.assertRaises(ValueError):
            c.judge(bad, case["before"], 24, self.meter)
        bad = deepcopy(case["proposal"])
        bad["rows"][1]["target"] = 0
        with self.assertRaises(ValueError):
            c.judge(bad, case["before"], 24, self.meter)
        with self.assertRaises(ValueError):
            c.judge(case["proposal"], self.a["cases"][1]["before"], 24, self.meter)

    def test_invalid_fields_and_budget_rejected(self):
        case = self.a["cases"][0]
        for invalid in (True, 7, -1, 1.0):
            bad = deepcopy(case["proposal"])
            bad["spec"]["shift"] = invalid
            with self.assertRaises(ValueError):
                c.judge(bad, case["before"], 24, self.meter)
        with self.assertRaises(ValueError):
            c.judge(case["proposal"], case["before"], 25, self.meter)


if __name__ == "__main__":
    unittest.main()
