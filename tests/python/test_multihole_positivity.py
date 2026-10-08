"""Semantic countercontrols for the fixed external four-point calibration."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest


EXPERIMENT = Path(__file__).resolve().parents[2] / "experiments/multihole_positivity"


def load(name):
    spec = importlib.util.spec_from_file_location(name, EXPERIMENT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


checker, verifier = load("checker"), load("verifier")
EVIDENCE_PATH = Path(os.environ.get("MULTIHOLE_EVIDENCE", EXPERIMENT / "evidence.json"))


class MultiholePositivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = json.loads(EVIDENCE_PATH.read_text())
        cls.models = cls.evidence["models"]["source"]["basic"]

    def test_two_requests_require_an_extra_realizer_policy(self):
        basic = checker.decide(4, (12, 5), models=self.models)
        joint = checker.decide(4, (12, 5), policy="joint", models=self.models)
        self.assertEqual((basic["classification"], basic["model_count"]), ("Underdetermined", 3))
        self.assertEqual((joint["classification"], joint["model_count"]), ("ForcedPositive", 1))
        self.assertEqual(joint["realizing_points"][0]["indices"], [2])

    def test_inhabited_positive_regions_can_lack_a_common_realizer(self):
        basic = checker.decide(9, (12, 5, 9), models=self.models)
        joint = checker.decide(9, (12, 5, 9), policy="joint", models=self.models)
        self.assertEqual((basic["classification"], basic["model_count"]), ("ForcedPositive", 1))
        self.assertEqual(joint["classification"], "Inconsistent")
        self.assertTrue(joint["inhabited"])
        self.assertEqual(self.evidence["controls"]["triangle"]["common_filling_indices"], [])

    def test_conflict_is_inconsistency_before_entailment(self):
        result = checker.decide(5, (5,), (5,), models=self.models)
        self.assertEqual(result["classification"], "Inconsistent")
        self.assertIsNone(result["positive_model"])
        self.assertIsNone(result["negative_model"])

    def test_budget_and_malformed_cache_never_prove_nonexistence(self):
        exhausted = checker.decide(4, fuel=0)
        invalid = checker.decide(True, models=self.models)
        incomplete = checker.decide(4, models=self.models[:1])
        self.assertEqual(exhausted["classification"], "Unknown")
        self.assertIsNone(exhausted["model_count"])
        self.assertEqual(invalid["classification"], "InvalidInput")
        self.assertEqual(incomplete["classification"], "InvalidInput")

    def test_independent_receiver_accepts_complete_evidence(self):
        self.assertEqual(verifier.verify(self.evidence)["status"], "Verified")

    def test_independent_receiver_rejects_geometry_models_and_witness_mutations(self):
        changed_geometry = copy.deepcopy(self.evidence)
        changed_geometry["geometry"]["source_outputs"][0][2] = "0"
        missing_model = copy.deepcopy(self.evidence)
        missing_model["models"]["source"]["basic"].pop()
        changed_witness = copy.deepcopy(self.evidence)
        case = next(c for c in changed_witness["cases"] if c["name"] == "two_positive_observations"
                    and c["policy"] == "basic" and c["chart"] == "source")
        case["queries"][4]["positive_model"] = []
        for evidence in (changed_geometry, missing_model, changed_witness):
            self.assertEqual(verifier.verify(evidence)["status"], "Rejected")


if __name__ == "__main__":
    unittest.main()
