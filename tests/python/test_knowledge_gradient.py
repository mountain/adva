from __future__ import annotations

import copy
from itertools import combinations, permutations
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from experiments.knowledge_geometry.gradient import (
    Evaluator, Task, all_tasks, check_table, encoded, exact_minimum,
    fixture_report, make_table, scalar_energy, search,
)


class KnowledgeGradientTests(unittest.TestCase):
    def test_universe_matches_independent_dag_transitive_closures(self):
        # Every finite poset admits a linear extension; enumerate every forward
        # edge subset in all 24 vertex orders and take its transitive closure.
        observed = set()
        for order in permutations(range(4)):
            edges = list(combinations(order, 2))
            for bits in range(64):
                relation = [[i == j for j in range(4)] for i in range(4)]
                for index, (i, j) in enumerate(edges):
                    if bits & (1 << index):
                        relation[i][j] = True
                for k in range(4):
                    for i in range(4):
                        for j in range(4):
                            relation[i][j] |= relation[i][k] and relation[k][j]
                observed.add(sum(1 << (4 * i + j) for i in range(4) for j in range(4)
                                 if relation[i][j]))
        self.assertEqual({t.relation for t in all_tasks()}, observed)
        self.assertEqual(len(observed), 219)

    def test_cached_and_checked_coverage_match_scalar_on_entire_query_family(self):
        for task in all_tasks():
            cached, checked = Evaluator(task, "cached"), Evaluator(task, "checked")
            for size in range(4):
                for family in combinations(task.words, size):
                    expected = scalar_energy(task, family)
                    self.assertEqual(cached.energy(family), expected)
                    self.assertEqual(checked.energy(family), expected)

    def test_coverage_checker_rejects_tampering_and_stale_task(self):
        task = Task(33831)
        good = json.loads(make_table(task))
        changes = []
        bad = copy.deepcopy(good)
        bad["rows"][0][1] ^= 1
        changes.append(bad)
        bad = copy.deepcopy(good)
        bad["rows"].pop()
        changes.append(bad)
        bad = copy.deepcopy(good)
        bad["relation"] = 33825
        changes.append(bad)
        bad = copy.deepcopy(good)
        bad["coarse"] = [0]
        changes.append(bad)
        bad = copy.deepcopy(good)
        bad["rows"][0][0] = True
        changes.append(bad)
        bad = copy.deepcopy(good)
        bad["schema"] = "unknown"
        changes.append(bad)
        for value in changes:
            with self.assertRaises(ValueError):
                check_table(task, encoded(value))
        with self.assertRaises(ValueError):
            check_table(task, b" " * 65537)

    def test_gradient_has_a_checked_nonoptimal_path_and_a_beam_failure(self):
        task = Task(33831)  # Only strict comparisons are 0<1 and 0<2.
        greedy = search(task, "greedy", max_words=14)
        self.assertEqual(greedy["status"], "Found")
        self.assertEqual(len(greedy["selected"]), 5)
        exact = exact_minimum(task)
        self.assertEqual(exact["selected"], [7, 10, 12])
        self.assertEqual(exact["minimum_words"], 3)
        self.assertEqual(search(task, "beam")["status"], "Unknown")
        self.assertEqual([scalar_energy(task, f) for f in
                          ((), (6,), (6, 8), (2, 6, 8), (2, 4, 6, 8), (2, 4, 6, 7, 8))],
                         [10, 6, 3, 2, 1, 0])
        self.assertEqual([scalar_energy(task, f) for f in ((), (7,), (7, 10), (7, 10, 12))],
                         [10, 7, 3, 0])

    def test_terminal_plateau_differs_from_relation_residual(self):
        task = Task(33831)
        terminal = search(task, "terminal")
        greedy = search(task, "greedy")
        self.assertEqual(terminal["reason"], "no_strict_descent")
        self.assertEqual(terminal["selected"], [])
        self.assertLess(greedy["energy"], terminal["energy"])

    def test_candidate_fuel_charges_every_energy_query_and_zero_is_unknown(self):
        original = Evaluator.energy
        for fuel in (0, 1, 2, 10, 100):
            calls = []

            def counted(evaluator, family):
                calls.append(family)
                return original(evaluator, family)

            with patch.object(Evaluator, "energy", counted):
                result = search(Task(33831), "beam", fuel=fuel)
            self.assertEqual(len(calls), result["evaluations"])
            self.assertLessEqual(len(calls), fuel)
            if fuel == 0:
                self.assertEqual(result["status"], "Unknown")
                self.assertIsNone(result["energy"])
        with self.assertRaises(ValueError):
            Evaluator(Task(33831), cache_limit=0)

    def test_coarse_interface_is_preserved_and_illegal_coordinates_rejected(self):
        # Diamond a<b<d and a<c<d, in the previous interface fixture.
        pairs = ((0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 3),
                 (2, 2), (2, 3), (3, 3))
        relation = sum(1 << (4 * i + j) for i, j in pairs)
        task = Task(relation, (14, 8))
        self.assertEqual([scalar_energy(task, f) for f in ((), (10,), (10, 12))], [2, 1, 0])
        self.assertEqual(exact_minimum(task)["minimum_words"], 2)
        with self.assertRaises(ValueError):
            Task(relation, (1,))
        with self.assertRaises(ValueError):
            Evaluator(task).energy((1,))

    def test_committed_report_is_a_complete_finite_replay(self):
        path = Path(__file__).resolve().parents[2] / "examples/verified_witness/knowledge-gradient-four-states.json"
        self.assertEqual(path.read_bytes(), encoded(fixture_report()))


if __name__ == "__main__":
    unittest.main()
