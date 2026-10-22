"""Finite joint-model controls, Codex/OpenAI, Unknown v0.3, Mingli Yuan proxy."""

import copy
import importlib.util
import itertools
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parents[2] / "experiments/program_positivity/epistemic"


def load(name):
    spec = importlib.util.spec_from_file_location("test_epistemic_"+name, HERE / (name+".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


producer, receiver, runner = load("model"), load("checker"), load("run")


class EpistemicPositivity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = runner.campaign()
        if cls.evidence["status"] != "Passed":
            raise RuntimeError(cls.evidence.get("failure"))

    def test_scott_axioms_and_nonknowledge_coexist(self):
        r = self.evidence["results"]["equal_reply"]
        self.assertTrue(r["ontology_satisfied"])
        self.assertEqual(r["godlike"], [[0], [0]])
        self.assertEqual(r["necessarily_exists"], [True, True])
        self.assertEqual(r["knows_exists"], [True, True])
        self.assertEqual(r["sender_godlike"], [True, False])
        self.assertEqual(r["knows_sender_godlike"], [False, False])
        self.assertEqual(r["knows_sender_not_godlike"], [False, False])
        self.assertEqual(r["non_saturation_witness"], [0, 1])

    def test_complete_property_domain_and_formula_counts(self):
        r = self.evidence["results"]["equal_reply"]
        self.assertEqual(r["property_count"], 16)
        self.assertEqual(sum(v["instances"] for v in r["checks"].values()), 626)
        self.assertTrue(all(v["holds"] for v in r["checks"].values()))
        self.assertEqual(r["necessary_existence"], [[0, 1], [0, 1]])
        self.assertEqual(r["essences"], [[[1, 5, 9, 13], [2, 6, 10, 14]], [[4, 5, 6, 7], [8, 9, 10, 11]]])

    def test_one_change_controls(self):
        r = self.evidence["results"]
        for name in ("equal_reply", "repeated_reply", "spoofed_claim", "swapped_positive"):
            self.assertEqual(r[name]["identity_status"], ["Underdetermined"]*2)
        self.assertEqual(r["trusted_binding"]["identity_status"], ["KnownTrue", "KnownFalse"])
        self.assertEqual(r["fixed_sender"]["identity_status"], ["KnownTrue"]*2)
        self.assertEqual(r["swapped_positive"]["sender_godlike"], [False, True])
        base = self.evidence["models"]["equal_reply"]
        for name, model in self.evidence["models"].items():
            if name != "equal_reply":
                self.assertEqual(sum(model[k] != base[k] for k in base), 1)

    def test_relation_conflation_fails_axioms(self):
        r = self.evidence["results"]["conflated_relations"]
        self.assertTrue(r["modal_s5"])
        self.assertFalse(r["ontology_satisfied"])
        self.assertFalse(r["checks"]["A4"]["holds"])
        self.assertFalse(r["checks"]["A5"]["holds"])
        self.assertFalse(r["checks"]["modal_collapse"]["holds"])

    def test_legacy_policies_not_confused_with_knowledge(self):
        r = self.evidence["static_reports"]
        self.assertEqual(len(r["joint"]["models"]), 2)
        self.assertEqual(r["marked_zero"]["models"][0]["realizers"], [0])
        self.assertEqual(r["conflict"]["models"], [])
        self.assertTrue(r["conflict"]["census"]["complete"])
        self.assertFalse(r["zero_fuel"]["census"]["complete"])
        self.assertEqual(self.evidence["static_receiving"]["zero_fuel"]["status"], "NoClaim")

    def test_full_small_profile_crosscheck(self):
        relations = ([[True, False], [False, True]], [[True, True], [True, True]])
        valid, ambiguous = 0, 0
        for modal, sender, generators, split in itertools.product(
                relations, itertools.product(range(2), repeat=2),
                itertools.product(range(2), repeat=2), (False, True)):
            model = {"modal": modal, "sender": list(sender),
                     "positive_extensions": [[m for m in range(4) if m & (1 << g)] for g in generators],
                     "transcripts": [["same"], ["different" if split else "same"]]}
            result = producer.evaluate(model)
            self.assertEqual(receiver.verify(model, result)["status"], "Verified")
            self.assertEqual(result["identity_descends"], all(a or b for a, b in zip(
                result["knows_sender_godlike"], result["knows_sender_not_godlike"])))
            if result["ontology_satisfied"]:
                valid += 1
                ambiguous += not result["identity_descends"]
        self.assertEqual((valid, ambiguous), (32, 8))

    def test_receiver_rejects_evidence_corruption(self):
        model = self.evidence["models"]["equal_reply"]
        mutations = [
            lambda r: r.update(identity_descends=True),
            lambda r: r.update(knows_sender_godlike=[True, True]),
            lambda r: r.update(property_count=4),
            lambda r: r.update(non_saturation_witness=None),
            lambda r: r["checks"]["A2"].update(instances=1),
            lambda r: r["essences"][0][0].pop(),
            lambda r: r.update(ontology_satisfied=1),
        ]
        for mutate in mutations:
            result = copy.deepcopy(self.evidence["results"]["equal_reply"])
            mutate(result)
            self.assertEqual(receiver.verify(model, result)["status"], "Rejected")

    def test_input_binding_and_profile_rejection(self):
        result = self.evidence["results"]["equal_reply"]
        altered = copy.deepcopy(self.evidence["models"]["equal_reply"])
        altered["sender"] = [0, 0]
        self.assertEqual(receiver.verify(altered, result)["status"], "Rejected")
        malformed = copy.deepcopy(altered)
        malformed["modal"][0][0] = 1
        self.assertEqual(receiver.verify(malformed, result)["status"], "Rejected")
        with self.assertRaises(ValueError):
            producer.evaluate(malformed)
        malformed = copy.deepcopy(altered)
        malformed["sender"].append(0)
        self.assertEqual(receiver.verify(malformed, result)["status"], "Rejected")


if __name__ == "__main__":
    unittest.main()
