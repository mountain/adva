"""External receipt snapshots and the existing finite composition contract.

Standard-library unittest, also collectable by pytest. One fresh checker per
class keeps the existing shared 100000-work-unit/15-second budget; tests never
reset it between cases. This suite creates no native Adva identities.
"""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/mobius_transport_receipt"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TransportReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        checker = load_module("_mobius_review_checker", EXPERIMENT / "check.py")
        # The historical composer imports a sibling named check. Keep that
        # binding local to this import rather than contaminating other tests.
        with patch.dict(sys.modules, {"check": checker}):
            cls.machine = load_module("_mobius_review_composer", EXPERIMENT / "compose.py")

    @classmethod
    def tearDownClass(cls):
        print(json.dumps({"shared_work_units": cls.machine.C.UNITS,
                          "work_cap": cls.machine.C.CAP}))

    def test_accepted_record_survives_caller_input_mutation(self):
        m = self.machine
        for p in (5, 7):
            for name in ("route_ids", "first_H", "second_H", "middle_probes"):
                with self.subTest(p=p, input=name):
                    receipts, expected = m.inputs(p)
                    routes = ["A-B", "B-C"]
                    result = m.compose(receipts, expected, routes)
                    self.assertEqual(result["status"], "AcceptedComposition")
                    snapshot = copy.deepcopy(result)
                    if name == "route_ids":
                        routes.reverse()
                    elif name == "first_H":
                        expected[0]["H"][0] = (expected[0]["H"][0] + 1) % p
                    elif name == "second_H":
                        expected[1]["H"][0] = (expected[1]["H"][0] + 1) % p
                    else:
                        receipts[0]["target_probes"].reverse()
                    self.assertEqual(result, snapshot)

    def test_returned_record_mutation_does_not_modify_caller_inputs(self):
        m = self.machine
        for p in (5, 7):
            for name in ("route_ids", "first_H", "second_H", "middle_probes"):
                with self.subTest(p=p, output=name):
                    receipts, expected = m.inputs(p)
                    routes = ["A-B", "B-C"]
                    original = copy.deepcopy((receipts, expected, routes))
                    result = m.compose(receipts, expected, routes)
                    self.assertEqual(result["status"], "AcceptedComposition")
                    self.assertEqual((receipts, expected, routes), original)
                    if name == "route_ids":
                        result["history"]["route_ids"].reverse()
                    elif name == "first_H":
                        result["history"]["coordinate_changes"][0][0] = 0
                    elif name == "second_H":
                        result["history"]["coordinate_changes"][1][0] = 0
                    else:
                        result["intermediate_frame"]["ordered_probes"].reverse()
                    self.assertEqual((receipts, expected, routes), original)

    def test_declared_composition_suite_matches_retained_evidence(self):
        fresh = self.machine.suite()
        retained = json.loads((EXPERIMENT / "composition-evidence/primary.json").read_text())
        body = lambda r: {k: v for k, v in r.items() if k != "cost"}
        self.assertEqual(fresh["status"], "Passed")
        self.assertEqual(len(fresh["cases"]), 24)
        self.assertEqual(body(fresh), body(retained))


if __name__ == "__main__":
    unittest.main(verbosity=2)
