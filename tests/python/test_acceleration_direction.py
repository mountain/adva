"""Integrity and independent arithmetic checks for the external witness."""
import copy
import importlib.util
import itertools
import json
from pathlib import Path
import random
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "acceleration_direction", ROOT / "experiments/knowledge_geometry/acceleration_direction.py")
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)


class AccelerationDirectionTests(unittest.TestCase):
    def test_full_symbolic_replay_and_retained_bytes(self):
        stored = (ROOT / "examples/verified_witness/acceleration-direction.json").read_text()
        self.assertEqual(stored, A.canonical(A.witness()))
        document = json.loads(stored)
        self.assertTrue(A.verify_witness(document))
        self.assertEqual(document["proof"]["f_terms"], 720)
        self.assertEqual(document["proof"]["residual_terms"], 0)

    def test_independent_permutation_determinant_and_pivoting(self):
        rng = random.Random(812)
        for _ in range(12):
            points = [[rng.randint(-4, 4) for _ in range(3)] for _ in range(6)]
            matrix = A.conic_rows(points)
            expected = A.permutation_det(matrix)
            self.assertEqual(A.bareiss(matrix), expected)
            self.assertEqual(A.incidence(points), expected)
        for matrix in ([[0, 1], [2, 3]], [[0, 0], [2, 3]],
                       [[0, 0, 1], [2, 0, 3], [4, 5, 6]],
                       [[1, 2, 3], [2, 4, 6], [3, 6, 9]]):
            self.assertEqual(A.bareiss(matrix), A.permutation_det(matrix))

    def test_counterexample_and_geometric_side_conditions(self):
        good = [(i, i*i, 1) for i in range(6)]
        bad = good[:-1] + [(5, 26, 1)]
        self.assertEqual(A.geometric_status(good), "pascal-collinear")
        self.assertEqual(A.pascal_points(good)[2], (30, 150, 0))
        self.assertEqual(A.evaluate(bad, "incidence"), 288)
        self.assertEqual(A.geometric_status(bad), "not-on-a-conic")
        degenerate = [(1, 1, 1)] * 6
        self.assertEqual(A.evaluate(degenerate, "incidence"), 0)
        self.assertEqual(A.geometric_status(degenerate), "outside-six-distinct-no-three-collinear-scope")
        infinity = [A.veronese((1, 0))] + [A.veronese((i, 1)) for i in range(5)]
        self.assertEqual(A.geometric_status(infinity), "pascal-collinear")

    def test_bad_inputs_and_witness_tampering(self):
        points = [(i, i*i, 1) for i in range(6)]
        for bad in [points[:-1], [(0, 0, 0)] + points[1:],
                    [(True, 0, 1)] + points[1:], [(1.0, 0, 1)] + points[1:]]:
            with self.assertRaises(ValueError):
                A.evaluate(bad, "incidence")
        good = A.witness()
        for mutate in [lambda w: w.update(name="another-question"),
                       lambda w: w["proof"]["common_normal_form"][0].__setitem__(1, 99),
                       lambda w: w["proof"].update(residual_terms=False),
                       lambda w: w["problem_formation"]["retained_counterexample"].update(G=0)]:
            bad = copy.deepcopy(good)
            mutate(bad)
            with self.assertRaises(ValueError):
                A.verify_witness(bad)

    def test_projective_rescaling_and_plane_covariance(self):
        points = [(i, i*i, 1) for i in range(5)] + [(5, 26, 1)]
        scales = [-2, 3, -1, 4, 2, -3]
        scaled = [tuple(k*x for x in p) for k, p in zip(scales, points)]
        self.assertEqual(A.incidence(scaled), 288 * __import__("math").prod(scales)**2)
        h = ((2, 1, 3), (0, 3, 2), (0, 0, 1))
        transformed = [A.matvec(h, p) for p in points]
        self.assertEqual(A.incidence(transformed), A.det3(h)**4 * 288)
        for entries in itertools.product((-1, 0, 1), repeat=4):
            a, b, c, d = entries
            if a*d == b*c:
                continue
            m = ((a, b), (c, d))
            for p in ((1, 0), (0, 1), (2, 3)):
                self.assertEqual(A.veronese(A.matvec(m, p)), A.matvec(A.lift(m), A.veronese(p)))

    def test_strict_amortization_and_missing_enterprise_data(self):
        self.assertEqual(A.robust_direction(None, 3, 1, 10)["status"], "Unknown")
        self.assertEqual(A.robust_direction(20, 3, 1, 10)["status"], "not-certified")
        result = A.robust_direction(20, 3, 1, 11)
        self.assertEqual(result["status"], "conditional-cost-improvement")
        self.assertEqual(result["minimum_reuses_for_strict_improvement"], 11)
        self.assertEqual(A.robust_direction(0, 2, 3, 10)["status"], "not-certified")
        for values in ((True, 3, 1, 10), (-1, 3, 1, 10)):
            with self.assertRaises(ValueError):
                A.robust_direction(*values)

    def test_entire_declared_workload_and_retained_digest(self):
        tasks = A.workload()
        self.assertEqual(len(tasks), 320)
        left = [A.evaluate(p, "bareiss") for p in tasks]
        right = [A.evaluate(p, "incidence") for p in tasks]
        self.assertEqual(left, right)
        report = json.loads((ROOT / "examples/verified_witness/acceleration-direction-local-benchmark.json").read_text())
        self.assertEqual(report["workload_sha256"], A.digest(tasks))
        self.assertEqual(report["answers_sha256"], A.digest(left))
        # Timing values are observations; CI does not assert a speedup.


if __name__ == "__main__":
    unittest.main()
