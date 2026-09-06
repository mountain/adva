import copy
import unittest

from experiments.prefix_frontier.coverage_gate import (
    Budget, Exhausted, build_witness, coverage_gate, fixtures,
    interval_only, mass, oracle, state, verify_witness,
)


class PrefixCoverageGateTests(unittest.TestCase):
    def test_missing_coverage_refuses_false_close_and_retains_counterexample(self):
        s = fixtures()["missing_eighth"]
        safe = coverage_gate(s, 2)
        self.assertEqual(safe["coverage_missing"], ["011"])
        self.assertEqual(safe["verdict"], "CertificateObstruction")
        self.assertIsNone(safe["U"])
        self.assertEqual(interval_only(s, 2)["verdict"], "FeatureClosed")
        self.assertEqual(oracle(s, 2, Budget())["values"], [1, 2])

    def test_feature_closure_reopens_on_finer_observer_and_new_instance(self):
        for name, precision in (("feature_not_object", 3), ("fresh_reuse", 4)):
            s = fixtures()[name]
            closed = coverage_gate(s, 2)
            self.assertEqual(closed["verdict"], "FeatureClosed")
            self.assertFalse(closed["object_closed"])
            self.assertTrue(closed["residual"])
            self.assertEqual(coverage_gate(s, precision)["verdict"], "Open")
            self.assertGreater(len(oracle(s, precision, Budget())["values"]), 1)

    def test_refinement_conserves_bounds_but_not_history(self):
        a = state(3, ["00"], ["1"], ["01"], ["start"])
        b = state(3, ["00"], ["1"], ["010", "011"], ["start", "refine:01"])
        self.assertEqual(mass(a["A"]), mass(b["A"]))
        x, y = coverage_gate(a, 2), coverage_gate(b, 2)
        self.assertEqual((x["L"], x["U"]), (y["L"], y["U"]))
        self.assertNotEqual(x["history"], y["history"])

    def test_invalid_prefixes_overlap_and_types_rejected(self):
        invalid = [state(2, ["0"], [], ["00"]), state(2, [], [], ["1", "1"]),
                   state(2, [], [], ["2"]), state(True, [], [], [""]),
                   state(2, [], [], ["000"]), state(9, [], [], [])]
        for s in invalid:
            with self.assertRaises(ValueError):
                coverage_gate(s, 2)

    def test_inclusive_dyadic_boundary_and_mass_one(self):
        self.assertEqual(coverage_gate(fixtures()["restored_eighth"], 2)["verdict"], "Open")
        closed = coverage_gate(state(2, [""], [], []), 2)
        self.assertEqual(closed["feature"], 4)  # Endpoint 1 is not an in-range two-bit string.
        self.assertTrue(closed["object_closed"])

    def test_budget_exhaustion_does_not_produce_a_verdict(self):
        with self.assertRaises(Exhausted):
            oracle(fixtures()["missing_eighth"], 2, Budget(nodes=0))

    def test_complete_finite_family_and_tamper_replay(self):
        witness = build_witness()
        self.assertEqual(witness["counts"]["observer_checks"], 512)
        self.assertGreater(witness["counts"]["unsafe_false_closes"], 0)
        changed = copy.deepcopy(witness)
        changed["cases"]["missing_eighth"]["safe"]["verdict"] = "FeatureClosed"
        self.assertFalse(verify_witness(changed))


if __name__ == "__main__":
    unittest.main()
