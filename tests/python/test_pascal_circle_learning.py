"""Exact witness replay and adversarial boundary checks; no native admission.

Original contribution by ChatGPT (OpenAI), through Mingli Yuan's account.
"""
from copy import deepcopy
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import tempfile
import unittest

from experiments.pascal_circle_learning import check as checker

ROOT = Path(__file__).resolve().parents[2]
WITNESS = ROOT / "experiments/pascal_circle_learning/evidence/candidate.json"


class PascalCircleLearningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = checker.load_candidate(WITNESS)

    def test_complete_exact_witness_replay(self):
        report = checker.check_candidate(self.candidate)
        self.assertEqual(report["status"], "Verified", report)
        self.assertTrue(all(report["checks"].values()))
        self.assertEqual(report["failures"], [])
        self.assertEqual(sum(p[2] == "0" for p in report["intersections"]["red"]), 1)
        self.assertTrue(all(p[2] == "1" for p in report["intersections"]["blue"]))

    def test_old_profile_witness_fails_only_new_center_incidence(self):
        old = checker.load_candidate(WITNESS.with_name("v0-candidate.json"))
        report = checker.check_candidate(old)
        self.assertEqual(report["status"], "Refuted")
        self.assertEqual(report["failures"], ["circle_center_incidence"])
        self.assertEqual(len(report["checks"]), 26)

    def test_moving_external_point_is_not_rescued_by_pascal_identity(self):
        bad = deepcopy(self.candidate)
        bad["points"][11][0] = str(Fraction(bad["points"][11][0]) + Fraction(1, 97))
        report = checker.check_candidate(bad)
        self.assertEqual(report["status"], "Refuted")
        self.assertTrue(report["checks"]["red.pascal_collinearity"])
        self.assertTrue(report["checks"]["red.circle_membership"])
        self.assertTrue(any(code.startswith("red.binding.") for code in report["failures"]))

    def test_circle_and_radius_tampering(self):
        for name in ("red", "blue"):
            for value in ("0", "-1"):
                bad = deepcopy(self.candidate)
                bad["circles"][name]["radius_squared"] = value
                report = checker.check_candidate(bad)
                self.assertEqual(report["status"], "Refuted")
                self.assertIn(name + ".positive_radius_squared", report["failures"])
            bad = deepcopy(self.candidate)
            old = bad["circles"][name]["center"][0]
            bad["circles"][name]["center"][0] = str(Fraction(old) + Fraction(1, 97))
            report = checker.check_candidate(bad)
            self.assertEqual(report["status"], "Refuted")
            self.assertIn(name + ".circle_membership", report["failures"])

    def test_wrong_role_binding_and_false_success_flag_are_rejected(self):
        bad = deepcopy(self.candidate)
        targets = bad["bindings"]["red"]["intersections"]
        finite = [i for i, target in enumerate(targets) if target is not None]
        left, right = finite
        targets[left], targets[right] = targets[right], targets[left]
        report = checker.check_candidate(bad)
        self.assertEqual(report["status"], "Refuted")
        self.assertIn("red.binding." + str(left), report["failures"])
        self.assertIn("red.binding." + str(right), report["failures"])
        bad = deepcopy(self.candidate)
        bad["status"] = "Verified"
        self.assertEqual(checker.check_candidate(bad)["status"], "Refuted")

    def test_collapsed_points_and_missing_tangent_pattern_are_rejected(self):
        bad = deepcopy(self.candidate)
        bad["points"][0] = list(bad["points"][6])
        report = checker.check_candidate(bad)
        self.assertEqual(report["status"], "Refuted")
        self.assertIn("fourteen_distinct_points", report["failures"])
        bad = deepcopy(self.candidate)
        bad["bindings"]["red"]["sequence"] = [1, 3, 1, 5, 7, 9]
        self.assertEqual(checker.check_candidate(bad)["status"], "Refuted")
        with self.assertRaisesRegex(ValueError, "coincident endpoints"):
            checker._line((Fraction(1), Fraction(0)), (Fraction(1), Fraction(0)))
        tangent = checker._line((Fraction(1), Fraction(0)), (Fraction(1), Fraction(0)),
                                (Fraction(0), Fraction(0)))
        self.assertEqual(tangent, (1, 0, -1))
        with self.assertRaisesRegex(ValueError, "coincident"):
            checker._intersection(tangent, tuple(2 * v for v in tangent))

    def test_exact_geometry_does_not_authorize_crossed_polygon(self):
        # Reassign a pair of circle labels and also transport its Pascal sequence.
        # The exact incidence construction is unchanged, but the boundary order is not.
        for name in ("red", "blue"):
            for first, second in combinations(checker.VERTICES[name], 2):
                bad = deepcopy(self.candidate)
                bad["points"][first], bad["points"][second] = bad["points"][second], bad["points"][first]
                bad["bindings"][name]["sequence"] = [
                    second if i == first else first if i == second else i
                    for i in bad["bindings"][name]["sequence"]]
                report = checker.check_candidate(bad)
                if report["failures"] == ["simple_polygon"]:
                    self.assertEqual(report["status"], "Refuted")
                    return
        self.fail("no geometry-preserving crossed-boundary control was found")

    def test_rational_and_json_admission(self):
        for value in (True, 0.5, "0.5", "2/4", "1/1", "-0", "01", "1/0", "1/-2"):
            with self.subTest(value=value):
                bad = deepcopy(self.candidate)
                bad["points"][0][0] = value
                self.assertEqual(checker.check_candidate(bad)["status"], "Refuted")
        with self.assertRaisesRegex(ValueError, "bit limit"):
            checker.rational(str(1 << checker.MAX_BITS))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.json"
            path.write_text('{"schema":"a","schema":"b"}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON"):
                checker.load_candidate(path)
            path.write_bytes(b" " * (checker.MAX_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "byte limit"):
                checker.load_candidate(path)


if __name__ == "__main__":
    unittest.main()
