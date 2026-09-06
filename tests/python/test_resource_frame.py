import copy
import json
from pathlib import Path
import unittest

from experiments.resource_frame import calibration as c

ROOT = Path(__file__).resolve().parents[2]


class ResourceFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads((ROOT / "examples/verified_witness/resource-frame.json").read_text())
        cls.meter = c.Meter()

    def trace(self, label):
        for i, trace in enumerate(self.artifact["traces"]):
            if trace["input"]["label"] == label:
                return copy.deepcopy(trace), c.cases()[i]
        raise AssertionError(label)

    def reject(self, trace, q):
        with self.assertRaises(c.Invalid):
            c.check_trace(trace, q, self.meter)

    def test_full_replay_and_fresh_roundtrip(self):
        c.verify(self.artifact, self.meter)
        for label, capacity in [("main", 24), ("fresh", 16)]:
            trace, q = self.trace(label)
            self.assertEqual(trace["final"]["frame"], c.initial(q)["frame"])
            self.assertEqual(trace["final"]["capacity_bits"], capacity)
            self.assertEqual(trace["final"]["remaining"], 2)
            self.assertEqual(trace["final"]["spent"], 6)
            self.assertEqual(len(trace["events"]), 4)
            self.assertNotEqual(trace["final"], c.initial(q))

    def test_all_bijections_and_collision(self):
        records = [t for t in self.artifact["traces"] if t["input"]["label"].startswith("rename-") and t["input"]["label"] != "rename-cycle"]
        self.assertEqual(len(records), 12)
        for trace in records:
            self.assertEqual(trace["events"][0]["status"], "Committed")
            self.assertEqual(trace["final"]["remaining"], 2)
        trace, q = self.trace("collision")
        self.assertEqual(trace["events"][0]["status"], "Rejected")
        self.assertEqual(trace["final"]["frame"], c.initial(q)["frame"])
        self.assertEqual(trace["final"]["spent"], 1)
        trace["final"]["spent"] = 0
        self.reject(trace, q)

    def test_unit_forgery_and_inexact_residual(self):
        trace, q = self.trace("forged-width")
        self.assertEqual(trace["events"][0]["residual"], {"claimed_bits": 48, "available_bits": 24})
        trace["events"][0]["status"] = "Committed"
        self.reject(trace, q)
        trace, q = self.trace("inexact")
        self.assertEqual(trace["events"][0]["status"], "Unknown")
        self.assertEqual(trace["events"][0]["residual"], {"unrepresented_bits": 4})
        self.assertEqual(trace["final"]["frame"], c.initial(q)["frame"])
        trace["events"][0]["residual"] = None
        self.reject(trace, q)

    def test_finite_names_do_not_refill_fuel(self):
        trace, q = self.trace("reset-control")
        self.assertEqual(trace["events"][1]["after"]["remaining"], 0)
        self.assertEqual(trace["events"][2]["status"], "Unknown")
        self.assertEqual(trace["next_action_index"], 2)
        self.assertEqual(trace["final"]["spent"], 3)
        unsafe = self.artifact["unsafe_control"]
        self.assertEqual(unsafe["events"][-1]["total_spent"], 4)
        self.assertEqual(unsafe["overspend"], 1)
        c.check_unsafe(unsafe, self.meter)
        trace["events"][1]["after"]["remaining"] = 3
        self.reject(trace, q)

    def test_zero_fuel_and_cycle_stop(self):
        zero, _ = self.trace("zero-fuel")
        self.assertEqual(zero["events"][0]["debit"], 0)
        self.assertEqual(zero["events"][0]["status"], "Unknown")
        self.assertEqual(zero["next_action_index"], 0)
        trace, q = self.trace("rename-cycle")
        self.assertEqual([e["debit"] for e in trace["events"]], [1, 1, 0])
        self.assertEqual(trace["events"][-1]["status"], "Unknown")
        self.assertEqual(trace["next_action_index"], 2)
        trace["events"].append(copy.deepcopy(trace["events"][-1]))
        self.reject(trace, q)

    def test_history_scope_and_account_cannot_be_erased(self):
        trace, q = self.trace("main")
        trace["events"].pop(1)
        self.reject(trace, q)
        trace, q = self.trace("main")
        trace["events"][0]["after"]["account_label"] = "new-budget"
        self.reject(trace, q)
        trace, q = self.trace("main")
        trace["input"]["grant"] = 9
        self.reject(trace, q)

    def test_unsupplied_task_and_boolean_metadata(self):
        trace, q = self.trace("main")
        trace["task"] = {"status": "Close", "content": "invented task"}
        self.reject(trace, q)
        trace, q = self.trace("main")
        trace["events"][0]["debit"] = True
        self.reject(trace, q)


if __name__ == "__main__":
    unittest.main()
