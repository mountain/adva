"""Finite scope and adversarial receipt checks; no process limits on import."""
import copy
import json
from pathlib import Path
import unittest

from experiments.revise_cycle import calibration as c

ROOT = Path(__file__).resolve().parents[2]


class ReviseCycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads((ROOT / "examples/verified_witness/three-turn-revise-f7.json").read_text())
        cls.meter = c.Meter()

    def record(self, i):
        return copy.deepcopy(self.artifact["records"][i])

    def check(self, r, i):
        c.verify_record(r, c.frozen_queries()[i], self.meter)

    def reject(self, r, i):
        with self.assertRaises(c.Invalid):
            self.check(r, i)

    def test_replay_and_fresh_reuse(self):
        c.verify_artifact(self.artifact, self.meter)
        for cached, baseline in [(0, 1), (2, 3)]:
            a, b = self.record(cached), self.record(baseline)
            self.assertEqual(a["judgment"], b["judgment"])
            self.assertEqual(len(a["new_rows"]), 1)
            self.assertEqual(len(b["new_rows"]), 2)
            self.assertEqual(len(a["unvisited"]), 5)

    def test_three_turns_do_not_force_close(self):
        for i in [0, 4, 5, 6]:
            r = self.record(i)
            self.assertEqual(len(r["turns"]), 3)
            self.check(r, i)
            self.assertEqual(r["turns"][0]["from"], r["turns"][-1]["to"])
            self.assertNotEqual(r["old_spec"], r["new_spec"])
        for i in [4, 5, 6]:
            r = self.record(i)
            self.assertEqual(r["judgment"]["status"], "Unknown")
            r["judgment"]["status"] = "Close"
            self.reject(r, i)

    def test_stale_completion_and_revised_scope(self):
        r = self.record(4)
        r["judgment"] = {"task_version": 1, "goal": "exists", "status": "Close", "answer": True, "witnesses": [1], "obligations": []}
        self.reject(r, 4)
        for field, value in [("coefficients", [2, 0, 5]), ("rhs", 2), ("domain", [0, 1, 2]), ("goal", "exists"), ("version", 1)]:
            r = self.record(0)
            r["new_spec"][field] = value
            self.reject(r, 0)

    def test_compiler_mutation_and_coverage(self):
        r = self.record(0)
        r["code"][0][1] = 3
        self.reject(r, 0)
        r = self.record(0)
        r["compiler_rows"].pop()
        self.reject(r, 0)
        r = self.record(0)
        r["compiler_rows"][0][1] = 0
        self.reject(r, 0)

    def test_history_binding_and_duplicate_witness(self):
        r = self.record(0)
        r["old_evidence"]["spec"]["coefficients"] = [1, 0, 6]
        self.reject(r, 0)
        r = self.record(0)
        r["old_evidence"]["observations"] = []
        self.reject(r, 0)
        r = self.record(0)
        r["new_rows"] = [[1, 1]]
        self.reject(r, 0)
        r = self.record(0)
        r["new_rows"][0][1] = 2
        self.reject(r, 0)

    def test_fuel_cursor_and_retained_obligation(self):
        r = self.record(6)
        self.assertEqual(r["new_rows"], [[2, 0]])
        self.assertEqual(r["remaining_schedule"], [6])
        self.assertEqual(r["stop"], "fuel_exhausted")
        self.assertTrue(r["judgment"]["obligations"])
        r["cursor"] = 0
        self.reject(r, 6)
        r = self.record(4)
        r["new_rows"] = [[6, 1]]
        self.reject(r, 4)

    def test_learner_action_and_frontier_cannot_be_forged(self):
        r = self.record(4)
        self.assertNotEqual(r["learn"]["next_action"], self.record(0)["learn"]["next_action"])
        r["learn"] = self.record(0)["learn"]
        self.reject(r, 4)
        r = self.record(0)
        r["unvisited"] = []
        self.reject(r, 0)
        r = self.record(4)
        r["turns"][2]["owed"] = []
        self.reject(r, 4)

    def test_boolean_and_malformed_scalars(self):
        r = self.record(0)
        r["unvisited"][0] = False
        self.reject(r, 0)
        r = self.record(0)
        r["query"]["fuel"] = True
        self.reject(r, 0)
        for change in ["old_value", "new_value", "version", "constant"]:
            r = self.record(0)
            if change == "old_value":
                r["old_evidence"]["observations"][0][1] = True
            elif change == "new_value":
                r["new_rows"][0][1] = True
            elif change == "version":
                r["old_spec"]["version"] = True
            else:
                r["code"][0][1] = True
            self.reject(r, 0)


if __name__ == "__main__":
    unittest.main()
