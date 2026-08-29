from __future__ import annotations

import json
from copy import deepcopy

import numpy as np
import pytest
import sympy
from scipy.optimize import minimize

from adva import link_modules, load_program


ARITHMETIC = """
(module arithmetic
  (export shared-double scale-double square)
  (def shared-double
    (fn ((x Real)) Real
      (add (copy (use x)))))
  (def scale-double
    (fn ((x Real)) Real
      (scale 2 (use x))))
  (def square
    (fn ((x Real)) Real
      (mul (copy (use x))))))
"""

CLIENT = """
(module client
  (import arithmetic shared-double)
  (export quadruple)
  (def quadruple
    (fn ((x Real)) Real
      (call arithmetic/shared-double
        (call arithmetic/shared-double (use x))))))
"""


@pytest.fixture
def workspace():
    return link_modules([ARITHMETIC, CLIENT])


def test_modules_link_and_calls_remain_executable(workspace):
    assert workspace.module_names == ("arithmetic", "client")
    quadruple = workspace.function("client", "quadruple")
    assert quadruple.evaluate({"x": 3.0}) == 12.0
    calls = [event for event in quadruple.history["prefix"] if event["kind"] == "call"]
    assert len(calls) == 2


def test_python_type_guard_matches_rust_boundary(workspace):
    function = workspace.function("arithmetic", "shared-double")
    assert function.signature.inputs == (("x", "real"),)
    assert function.signature.domain.typed.types == ("real",)
    assert function.signature.codomain.typed.types == ("real",)
    assert function.compilation_certificate is not None
    assert function.compilation_certificate["diagram_integrity"] == "checked"
    assert function.validation_certificate["graph"] == "checked"
    with pytest.raises(TypeError, match="expected inputs"):
        function.evaluate({"y": 1.0})
    with pytest.raises(TypeError, match="real scalar"):
        function.evaluate({"x": "1"})


def test_k1_partition_and_ids_survive_python_json_boundary(workspace):
    function = workspace.function("arithmetic", "shared-double")
    partition = function.source_partition
    assert len(partition) == 1
    occurrences = next(iter(partition.values()))
    assert len(occurrences) == len(set(occurrences))
    assert all(item.startswith("occ:") for item in occurrences)


def test_k2_sympy_value_does_not_replace_native_history(workspace):
    shared = workspace.function("arithmetic", "shared-double")
    scaled = workspace.function("arithmetic", "scale-double")
    x = sympy.Symbol("x", real=True)
    assert sympy.simplify(shared.to_sympy() - 2 * x) == 0
    assert sympy.simplify(scaled.to_sympy() - 2 * x) == 0
    assert shared.ir != scaled.ir
    assert shared.history != scaled.history


def test_numpy_adapter_vectorizes_checked_expression(workspace):
    function = workspace.function("arithmetic", "shared-double")
    values = function.numpy_callable()(np.asarray([1.0, 2.0, 3.0]))
    np.testing.assert_allclose(values, [2.0, 4.0, 6.0])


def test_scipy_uses_rust_value_and_jacobian(workspace):
    objective = workspace.function("arithmetic", "square").scipy_objective()
    result = minimize(objective.fun, x0=np.asarray([3.0]), jac=objective.jac, method="BFGS")
    assert result.success
    np.testing.assert_allclose(result.x, [0.0], atol=1e-8)


def test_value_and_gradient_returns_auditable_certificate(workspace):
    square = workspace.function("arithmetic", "square")
    value, gradient, certificate = square.value_and_gradient({"x": 3.0})
    assert value == 9.0
    assert gradient == {"x": 6.0}
    assert certificate["method"] == "forward-mode structural differential"
    assert set(certificate["operation_rules"]) == {
        "adva.builtin:copy@1",
        "adva.builtin:mul@1",
    }
    assert certificate["diagram_integrity"] == "checked"


def test_checked_json_import_has_validation_but_not_compilation_authority(workspace):
    compiled = workspace.function("arithmetic", "shared-double")
    imported = load_program(compiled.ir)

    assert imported.evaluate({"x": 3.0}) == 6.0
    assert imported.ir == compiled.ir
    assert imported.compilation_certificate is None
    assert imported.validation_certificate["linear_use"] == "checked"
    assert imported.validation_certificate["source_partition"] == "checked"


def test_python_cannot_import_an_implicitly_aliased_frontier(workspace):
    compiled = workspace.function("arithmetic", "shared-double")
    tampered = deepcopy(compiled.ir)
    tampered["outputs"].append(deepcopy(tampered["outputs"][0]))
    tampered["signature"]["outputs"].append("real")

    with pytest.raises(ValueError, match="consumed exactly once"):
        load_program(tampered)


def test_python_cannot_reassign_a_copied_occurrence_source(workspace):
    compiled = workspace.function("arithmetic", "shared-double")
    tampered = deepcopy(compiled.ir)
    copy_event = next(
        event for event in tampered["history"]["prefix"] if event["kind"] == "copy"
    )
    child = copy_event["children"][0]
    occurrence = next(item for item in tampered["occurrences"] if item["id"] == child)
    occurrence["source"] = "source:forged"

    with pytest.raises(ValueError, match="does not preserve source"):
        load_program(tampered)


def test_scientific_adapters_do_not_mutate_native_ir(workspace):
    function = workspace.function("arithmetic", "square")
    before = json.dumps(function.ir, sort_keys=True)
    function.to_sympy()
    function.numpy_callable()(np.asarray([2.0]))
    function.scipy_objective().jac([2.0])
    after = json.dumps(function.ir, sort_keys=True)
    assert after == before
