"""Meaningful checks for the bounded external program receiver.

One frozen suite makes 19 producer calls and 12 independent receiver calls.
These checks execute program data, compare transported semantics, and reject
mutated claims; they make no native Adva or outside-carrier assertion.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "experiments" / "program_positivity"


def load(name):
    # Other experiment suites register generic names such as "verifier".
    # Bind this suite to its exact source even when collected in one process.
    module_name = "adva_program_positivity_test_" + name
    spec = importlib.util.spec_from_file_location(module_name, ENGINE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


meta, verifier = load("meta"), load("verifier")


def query(report, name):
    return next(item for item in report["queries"] if item["name"] == name)


def reverse_mask(mask, n=4):
    return sum(1 << (n - 1 - point) for point in range(n) if mask & (1 << point))


class ProgramPositivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((ENGINE / "cases.json").read_text(encoding="utf-8"))
        cls.reports = {name: meta.analyze(request) for name, request in cls.cases.items()}

    def test_01_expected_outcome_boundaries(self):
        exceptional = {
            "division_zero": "UndefinedOnCarrier",
            "zero_fuel": "Unknown",
            "unsupported_loop": "Unsupported",
            "forward_reference": "InvalidInput",
        }
        self.assertEqual(len(self.cases), 14)
        for name, report in self.reports.items():
            with self.subTest(case=name):
                self.assertEqual(report["status"], exceptional.get(name, "Analyzed"))
                self.assertLessEqual(report["fuel"]["used"], report["fuel"]["limit"])
        conflict = self.reports["direct_conflict"]
        self.assertEqual(conflict["models"], [])
        self.assertTrue(conflict["census"]["complete"])
        self.assertTrue(all(item["classification"] == "Inconsistent" for item in conflict["queries"]))

    def test_02_static_ambiguity_and_joint_realizer(self):
        joint, basic = self.reports["mobius_joint"], self.reports["mobius_basic"]
        self.assertEqual({name: joint["regions"][name] for name in ("B", "H", "both", "triangle")},
                         {"B": 12, "H": 5, "both": 4, "triangle": 9})
        self.assertEqual(len(joint["models"]), 1)
        self.assertEqual(joint["models"][0]["realizers"], [2])
        self.assertEqual(query(joint, "both")["classification"], "ForcedPositive")
        self.assertEqual(len(basic["models"]), 3)
        undecided = query(basic, "both")
        self.assertEqual(undecided["classification"], "Underdetermined")
        self.assertIsNotNone(undecided["positive_witness"])
        self.assertIsNotNone(undecided["negative_witness"])
        self.assertNotEqual(undecided["positive_witness"], undecided["negative_witness"])
        triangle = self.reports["triangle_basic"]
        self.assertEqual(len(triangle["models"]), 1)
        self.assertEqual(triangle["models"][0]["realizers"], [])
        self.assertEqual(query(triangle, "both")["classification"], "ForcedNegative")
        self.assertTrue(query(triangle, "both")["inhabited"]["value"])
        self.assertEqual(self.reports["triangle_joint"]["models"], [])
        self.assertTrue(all(item["classification"] == "Inconsistent"
                            for item in self.reports["triangle_joint"]["queries"]))

    def test_03_equivalent_program_chart_transport(self):
        source, target = self.reports["mobius_joint"], self.reports["mobius_target"]
        for point in range(4):
            self.assertEqual(source["trace"][point]["outputs"], target["trace"][3 - point]["outputs"])
            self.assertEqual(source["trace"][point]["observations"],
                             target["trace"][3 - point]["observations"])
        for name, mask in source["regions"].items():
            self.assertEqual(target["regions"][name], reverse_mask(mask))
        for item in source["queries"]:
            other = query(target, item["name"])
            self.assertEqual(other["classification"], item["classification"])
            self.assertEqual(other["positive_model_count"], item["positive_model_count"])
            self.assertEqual(other["negative_model_count"], item["negative_model_count"])
        transported = [{"positive_masks": sorted(reverse_mask(mask) for mask in model["positive_masks"]),
                        "realizers": sorted(3 - point for point in model["realizers"])}
                       for model in source["models"]]
        self.assertEqual(target["models"], transported)
        self.assertEqual(target["models"][0]["realizers"], [1])

    def test_04_different_programs_change_observation_and_decision(self):
        square = self.reports["square_marked"]
        negative = self.reports["negative_identity"]
        self.assertEqual(square["regions"]["positive"], 15)
        self.assertEqual(negative["regions"]["positive"], 3)
        self.assertEqual(query(square, "positive")["classification"], "ForcedPositive")
        self.assertEqual(query(negative, "positive")["classification"], "ForcedNegative")
        changed = copy.deepcopy(self.cases["square_marked"])
        changed["program"]["steps"][0]["op"] = "add"
        report = meta.analyze(changed)
        self.assertEqual(report["status"], "Analyzed")
        self.assertEqual([entry["outputs"]["y"] for entry in report["trace"]], ["-4", "-2", "2", "4"])
        self.assertEqual(report["regions"]["positive"], 12)
        self.assertEqual(report["regions"]["large"], 12)
        self.assertEqual(query(square, "large")["classification"], "ForcedNegative")
        self.assertEqual(query(report, "large")["classification"], "ForcedPositive")

    def test_05_carrier_size_and_computational_unknown(self):
        one, two = self.reports["one_point"], self.reports["two_points"]
        self.assertEqual(one["n"], 1)
        self.assertEqual(len(one["models"]), 1)
        self.assertEqual(query(one, "positive")["classification"], "ForcedPositive")
        self.assertEqual(two["n"], 2)
        self.assertEqual(len(two["models"]), 2)
        self.assertEqual(query(two, "positive")["classification"], "Underdetermined")
        for name in ("division_zero", "zero_fuel", "unsupported_loop", "forward_reference"):
            report = self.reports[name]
            self.assertEqual(report["models"], [])
            self.assertFalse(report["census"]["complete"])
            self.assertTrue(all(item["classification"] == "Unknown" for item in report["queries"]))
        failure = self.reports["division_zero"]["failure"]
        self.assertEqual(failure["code"], "division_by_zero")
        self.assertEqual(failure["filling_index"], 0)
        self.assertEqual(failure["step"], "y")
        self.assertEqual(failure["denominator"], "0")
        self.assertEqual(self.reports["zero_fuel"]["fuel"], {"limit": 0, "used": 0, "remaining": 0})
        self.assertEqual(self.reports["unsupported_loop"]["failure"]["code"], "operation")
        self.assertEqual(self.reports["forward_reference"]["failure"]["code"], "reference")

    def test_06_independent_receiver_accepts_and_withholds(self):
        for name in ("mobius_joint", "mobius_target", "square_marked", "division_zero"):
            with self.subTest(case=name):
                self.assertEqual(verifier.verify(self.cases[name], self.reports[name])["status"], "Verified")
        for name in ("zero_fuel", "unsupported_loop", "forward_reference"):
            with self.subTest(case=name):
                self.assertEqual(verifier.verify(self.cases[name], self.reports[name])["status"], "NoClaim")

    def test_07_independent_receiver_rejects_semantic_mutations(self):
        request, original = self.cases["mobius_joint"], self.reports["mobius_joint"]
        mutations = []
        output = copy.deepcopy(original)
        output["trace"][0]["outputs"]["r"] = "999"
        mutations.append(("output", output))
        region = copy.deepcopy(original)
        region["regions"]["both"] ^= 1
        mutations.append(("region", region))
        model = copy.deepcopy(original)
        model["models"][0]["positive_masks"].remove(model["full_mask"])
        mutations.append(("model", model))
        witness = copy.deepcopy(original)
        query(witness, "both")["positive_witness"] = 99
        mutations.append(("query_witness", witness))
        for label, report in mutations:
            with self.subTest(mutation=label):
                self.assertEqual(verifier.verify(request, report)["status"], "Rejected")
        self.assertEqual(verifier.verify(self.cases["square_marked"], original)["status"], "Rejected")

    def test_08_domain_guards_do_not_discard_supplied_fillings(self):
        guarded = copy.deepcopy(self.cases["two_points"])
        guarded["domain"] = [{"op": "gt", "args": ["x", "0"]}]
        report = meta.analyze(guarded)
        self.assertEqual(report["status"], "InvalidInput")
        self.assertEqual(report["models"], [])
        self.assertTrue(all(item["classification"] == "Unknown" for item in report["queries"]))
        undefined = copy.deepcopy(self.cases["division_zero"])
        undefined["domain"] = [{"op": "ne", "args": ["x", "0"]}]
        report = meta.analyze(undefined)
        self.assertEqual(report["status"], "UndefinedOnCarrier")
        self.assertEqual(report["failure"]["filling_index"], 0)

    def test_09_named_region_dependencies_are_acyclic(self):
        aliased = copy.deepcopy(self.cases["mobius_joint"])
        aliased["properties"] = {"alias": "both", **aliased["properties"]}
        aliased["query"] = ["alias"]
        report = meta.analyze(aliased)
        self.assertEqual(report["status"], "Analyzed")
        self.assertEqual(report["regions"]["alias"], 4)
        self.assertEqual(query(report, "alias")["classification"], "ForcedPositive")
        cyclic = copy.deepcopy(self.cases["mobius_joint"])
        cyclic["properties"].update({"cycle_a": "cycle_b", "cycle_b": "cycle_a"})
        report = meta.analyze(cyclic)
        self.assertEqual(report["status"], "InvalidInput")
        self.assertEqual(report["failure"]["code"], "property_cycle")


if __name__ == "__main__":
    unittest.main()
