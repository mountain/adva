"""Finite structural controls; no request bytes and no semantic authority."""
import copy
import json
from pathlib import Path
import unittest

from verify import Invalid, validate


ROOT = Path(__file__).resolve().parent


class AdapterObligationControls(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(
            (ROOT / "adapter-obligation-v0.json").read_text(encoding="utf-8"))

    def reject(self, code):
        with self.assertRaises(Invalid) as caught:
            validate(self.document)
        self.assertEqual(caught.exception.code, code)

    def test_00_canonical_contract(self):
        result = validate(self.document)
        self.assertEqual(result["status"], "StructurallyCompleteProposedInterface")
        self.assertEqual(result["native_executions"], 0)

    def test_01_missing_second_diagram(self):
        self.document["ordered_diagrams"].pop()
        self.reject("E_DIAGRAM_COUNT")

    def test_02_duplicate_diagram_role(self):
        self.document["ordered_diagrams"][1]["role"] = "left"
        self.reject("E_DIAGRAM_ROLES")

    def test_03_missing_source_identity(self):
        del self.document["ordered_diagrams"][0]["qualified_endpoint"]["source_id"]
        self.reject("E_ENDPOINT_FIELDS")

    def test_04_swapped_relation_endpoint(self):
        self.document["relation"]["left"] = copy.deepcopy(
            self.document["relation"]["right"])
        self.reject("E_RELATION_LEFT")

    def test_05_missing_wrong_path_control(self):
        self.document["controls"] = [item for item in self.document["controls"]
                                     if item["id"] != "wrong-path"]
        self.reject("E_CONTROL_SET")

    def test_06_same_value_different_origin_accepted(self):
        control = next(item for item in self.document["controls"]
                       if item["id"] == "same-value-different-origin")
        control["expected"] = "Accepted"
        self.reject("E_CONTROL_OUTCOME")

    def test_07_native_boundary_claimed_implemented(self):
        self.document["ordered_diagrams"][0]["native_admission"]["status"] = "Implemented"
        self.reject("E_NATIVE_BOUNDARY_STATUS")

    def test_08_additive_multiplicative_carriers_merged(self):
        self.document["arithmetic_boundaries"]["multiplicative_unit"]["carrier"] = \
            "typed additive carrier"
        self.reject("E_MULTIPLICATIVE_BOUNDARY")

    def test_09_multiplicative_zero_guard_removed(self):
        self.document["arithmetic_boundaries"]["multiplicative_unit"][
            "denominator_nonzero_required"] = False
        self.reject("E_MULTIPLICATIVE_GUARD")

    def test_10_local_image_promoted_to_m6(self):
        self.document["relation"]["local_image_equality_sufficient_for_m6"] = True
        self.reject("E_M6")

    def test_11_accepted_without_recorded_outcome_check(self):
        self.document["outcomes"]["Accepted"]["requires"].pop()
        self.reject("E_ACCEPTED_CHECKS")

    def test_12_adapter_residual_erased(self):
        self.document["residual_obligations"].remove("adapter-implementation")
        self.reject("E_RESIDUALS")


if __name__ == "__main__":
    unittest.main()
