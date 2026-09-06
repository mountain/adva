"""Targeted boundary tests; no broad repository regression rerun."""
from copy import deepcopy
import unittest

from experiments.finite_learner import calibration as c


class FiniteLearnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Process limits belong to the standalone CLI/outer timeout only.
        # Setting RLIMIT_CPU or SIGALRM here would affect unrelated pytest tests.
        c.WORK.clear()
        cls.a = c.build()

    def test_success_and_fresh_reuse(self):
        a = self.a
        c.verify_artifact(a)
        self.assertEqual(len(a["success"]["search"]["rows"]), 121)
        self.assertEqual(len(a["reuse"]["search_baseline"]["rows"]), 105)
        self.assertEqual(a["reuse"]["checked"]["expanded_coefficients"], [2, 0, 6])
        self.assertEqual(a["reuse"]["ordinary"], a["reuse"]["checked"]["trial"])
        self.assertNotEqual(a["task"], a["reuse_task"])

    def test_failure_changes_next_proposal_without_removing_solution(self):
        f = self.a["failure"]
        self.assertEqual(f["trial"]["observations"], [[0, 1, 0]])
        self.assertEqual(f["state"]["constraints"], [[0, 1]])
        self.assertEqual(f["proposal_before"], [0, 0, 0])
        self.assertEqual(f["proposal_after"], [0, 0, 1])
        survivors = []
        for i in range(343):
            coefficients = c.candidate_at(i)
            if c.oracle(coefficients, 0) == 1:
                survivors.append(coefficients)
        self.assertEqual(len(survivors), 49)
        self.assertIn([2, 3, 1], survivors)
        self.assertEqual(f["state"]["words"], [])

    def test_timeout_does_not_become_refutation_and_resume_keeps_history(self):
        a = self.a
        z, k = a["zero_fuel"], a["continuation"]
        self.assertEqual(z["search"]["status"], "Unknown")
        for key in ("cursor", "constraints", "words"):
            self.assertEqual(z["state"][key], a["initial"][key])
        self.assertEqual(len(z["state"]["ledger"]), 1)
        self.assertEqual(k["prefix"]["cursor"], 3)
        self.assertEqual(k["suffix"]["start"], 3)
        self.assertEqual(k["state"]["cursor"], 121)
        self.assertEqual(k["state"]["ledger"][:1], k["prefix_state"]["ledger"])
        bad = deepcopy(k["suffix"])
        bad["start"] = 2
        with self.assertRaises(ValueError):
            c.update(a["task"], k["prefix_state"], bad, "search")

    def test_zero_is_equality_but_not_unit_ratio(self):
        rows = self.a["arithmetic_boundary"]
        self.assertEqual([r["x"] for r in rows if r["ratio"] is None], [3, 6])
        self.assertTrue(all(r["difference"] == 0 for r in rows))
        self.assertEqual([r["ratio"] for r in rows if r["ratio"] is not None], [1]*5)
        bad = deepcopy(self.a)
        bad["arithmetic_boundary"][3]["ratio"] = 1
        with self.assertRaises(ValueError):
            c.verify_artifact(bad)

    def test_missing_coverage_and_false_acceptance_rejected(self):
        q = self.a["task"]
        r = deepcopy(self.a["success"]["search"]["rows"][-1])
        r["observations"].pop()
        with self.assertRaises(ValueError):
            c.verify_trial(q, r)
        r = deepcopy(self.a["failure"]["trial"])
        r["status"] = "Accepted"
        with self.assertRaises(ValueError):
            c.update(q, c.initial(q), r, "trial")

    def test_stale_scope_and_corrupted_word_rejected(self):
        q, q2 = self.a["task"], self.a["reuse_task"]
        word = deepcopy(self.a["success"]["state"]["words"][0])
        with self.assertRaises(ValueError):
            c.update(q2, self.a["initial"], self.a["failure"]["trial"], "trial")
        word["coefficients"][0] = 3
        with self.assertRaises(ValueError):
            c.reuse(q, word, q2)
        word = self.a["success"]["state"]["words"][0]
        incompatible = c.task([2, 0, 5])
        self.assertEqual(c.reuse(q, word, incompatible)["trial"]["status"], "Refuted")

    def test_invalid_grammar_and_altered_domain_rejected(self):
        for coeffs in ([True, 3, 1], [2, 3], [7, 0, 0], [2.0, 3, 1]):
            with self.assertRaises(ValueError):
                c.task(coeffs)
        q = deepcopy(self.a["task"])
        q["domain"][0] = False
        with self.assertRaises(ValueError):
            c.search(q, 1)
        with self.assertRaises(ValueError):
            c.search(self.a["task"], 344)


if __name__ == "__main__":
    unittest.main()
