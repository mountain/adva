from __future__ import annotations

import cmath
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import pytest
from adva import link_modules

REAL_PARAXIAL_OPTICS_KERNEL = r"""
(module real-paraxial-optics
  (export
    direct-quarter
    factorized-quarter
    inverse-quarter
    half-turn
    full-turn
    stable-cell
    parabolic-cell
    hyperbolic-cell
    parameter-cell
    oriented-readout
    parameter-objective
    direct-parameter-objective)

  ; Unit free propagation: (x, s) |-> (x + s, s).
  (def drift-plus-core
    (fn ((x Real) (s-position Real) (s-output Real)) (outputs Real Real)
      (frontier
        (add
          (frontier
            (use x)
            (use s-position)))
        (use s-output))))

  (def drift-plus
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call drift-plus-core
        (frontier
          (use x)
          (copy (use s))))))

  ; Inverse unit propagation: (x, s) |-> (x - s, s).
  (def drift-minus-core
    (fn ((x Real) (s-position Real) (s-output Real)) (outputs Real Real)
      (frontier
        (add
          (frontier
            (use x)
            (neg (use s-position))))
        (use s-output))))

  (def drift-minus
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call drift-minus-core
        (frontier
          (use x)
          (copy (use s))))))

  ; Unit focusing power: (x, s) |-> (x, s - x).
  (def focus-core
    (fn ((x-output Real) (x-slope Real) (s Real)) (outputs Real Real)
      (frontier
        (use x-output)
        (add
          (frontier
            (use s)
            (neg (use x-slope)))))))

  (def focus
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call focus-core
        (frontier
          (copy (use x))
          (use s)))))

  ; Tunable focusing: kappa is an explicit source-bearing program input.
  (def focus-parameter-core
    (fn ((x-output Real) (x-product Real) (s Real) (kappa Real))
        (outputs Real Real)
      (frontier
        (use x-output)
        (add
          (frontier
            (use s)
            (neg
              (mul
                (frontier
                  (use kappa)
                  (use x-product)))))))))

  (def focus-parameter
    (fn ((x Real) (s Real) (kappa Real)) (outputs Real Real)
      (call focus-parameter-core
        (frontier
          (copy (use x))
          (use s)
          (use kappa)))))

  ; Inverse focusing power: (x, s) |-> (x, s + x).
  (def defocus-core
    (fn ((x-output Real) (x-slope Real) (s Real)) (outputs Real Real)
      (frontier
        (use x-output)
        (add
          (frontier
            (use s)
            (use x-slope))))))

  (def defocus
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call defocus-core
        (frontier
          (copy (use x))
          (use s)))))

  ; A compiled value shadow of the normalized quarter-turn.
  (def direct-quarter
    (fn ((x Real) (s Real)) (outputs Real Real)
      (frontier
        (use s)
        (neg (use x)))))

  ; The physical device history P(1) L(1) P(1).
  (def factorized-quarter
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call drift-plus
        (call focus
          (call drift-plus
            (frontier
              (use x)
              (use s)))))))

  ; The inverse physical history P(-1) L(-1) P(-1).
  (def inverse-quarter
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call drift-minus
        (call defocus
          (call drift-minus
            (frontier
              (use x)
              (use s)))))))

  (def half-turn
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call factorized-quarter
        (call factorized-quarter
          (frontier
            (use x)
            (use s))))))

  (def full-turn
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call half-turn
        (call half-turn
          (frontier
            (use x)
            (use s))))))

  ; Three repeatable real optical cells with determinant one.
  (def stable-cell
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call drift-plus
        (call focus
          (frontier
            (use x)
            (use s))))))

  (def parabolic-cell
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call drift-plus
        (frontier
          (use x)
          (use s)))))

  (def hyperbolic-cell
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call drift-plus
        (call defocus
          (frontier
            (use x)
            (use s))))))

  ; One program template crosses all three determinant-one regimes:
  ; p_kappa = P(1) L(kappa).
  (def parameter-cell
    (fn ((x Real) (s Real) (kappa Real)) (outputs Real Real)
      (call drift-plus
        (call focus-parameter
          (frontier
            (use x)
            (use s)
            (use kappa))))))

  ; Declared oriented output probe ell(x', s') = x' + 2 s'.
  (def oriented-readout
    (fn ((x-output Real) (s-output Real)) Real
      (add
        (frontier
          (use x-output)
          (scale 2 (use s-output))))))

  ; Device-history realization of L_kappa = ell(p_kappa(x, s)).
  (def parameter-objective
    (fn ((x Real) (s Real) (kappa Real)) Real
      (call oriented-readout
        (call parameter-cell
          (frontier
            (use x)
            (use s)
            (use kappa))))))

  ; A different checked history with the same oriented scalar shadow
  ; x + 3 s - 3 kappa x.
  (def direct-parameter-objective-core
    (fn ((x-readout Real) (x-product Real) (s Real) (kappa Real)) Real
      (add
        (frontier
          (add
            (frontier
              (use x-readout)
              (scale 3 (use s))))
          (scale -3
            (mul
              (frontier
                (use kappa)
                (use x-product))))))))

  (def direct-parameter-objective
    (fn ((x Real) (s Real) (kappa Real)) Real
      (call direct-parameter-objective-core
        (frontier
          (copy (use x))
          (use s)
          (use kappa)))))
)
"""

Ray = tuple[float, float]
RealizedAction = tuple[tuple[float, float], tuple[float, float]]
SixState = tuple[float, float, float, float, float, float]
SourceIncidence = tuple[tuple[int, int], tuple[int, int]]
ProgramAwareObservation = tuple[RealizedAction, SourceIncidence, tuple[str, ...]]
MappingView = Mapping[str, Any]

ASPECT_OPPOSITE_PAIRS = ((0, 3), (1, 4), (2, 5))
BOUNDED_BACKWARD_OPERATIONS = frozenset(
    {"constant", "copy", "add", "mul", "scale", "neg"}
)


@dataclass(frozen=True, order=True, slots=True)
class WireEndpoint:
    """Canonical endpoint coordinates read from a Rust-checked wire."""

    producer_kind: str
    producer_id: int
    output_index: int


@dataclass(frozen=True, slots=True)
class ProbeDemand:
    """One numerical demand attached to an existing checked lineage."""

    endpoint: WireEndpoint
    coefficient: float
    lineage: tuple[str, ...]
    sources: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NodeDemand:
    node_id: int
    operation: str
    output_demands: tuple[float, ...]
    input_demands: tuple[float, ...]
    input_lineages: tuple[tuple[str, ...], ...]


@dataclass(frozen=True, slots=True)
class BackwardProbeWitness:
    """Research-local numerical witness; not a stable pullback certificate."""

    outputs: tuple[float, ...]
    input_demands: tuple[tuple[str, float], ...]
    demands: tuple[ProbeDemand, ...]
    node_demands: tuple[NodeDemand, ...]
    operation_rules: tuple[str, ...]

    @property
    def input_demand_map(self) -> dict[str, float]:
        return dict(self.input_demands)

    @property
    def demand_by_endpoint(self) -> dict[WireEndpoint, ProbeDemand]:
        return {record.endpoint: record for record in self.demands}


def _functions() -> dict[str, Any]:
    workspace = link_modules([REAL_PARAXIAL_OPTICS_KERNEL])
    names = (
        "direct-quarter",
        "factorized-quarter",
        "inverse-quarter",
        "half-turn",
        "full-turn",
        "stable-cell",
        "parabolic-cell",
        "hyperbolic-cell",
        "parameter-cell",
        "oriented-readout",
        "parameter-objective",
        "direct-parameter-objective",
    )
    return {
        name: workspace.function("real-paraxial-optics", name)
        for name in names
    }


def _evaluate(function: Any, ray: Ray) -> Ray:
    result = function.evaluate({"x": ray[0], "s": ray[1]})
    if not isinstance(result, tuple) or len(result) != 2:
        raise TypeError("a paraxial optical program must have two ordered Real outputs")
    return result


def _evaluate_parameter_cell(function: Any, ray: Ray, kappa: float) -> Ray:
    result = function.evaluate({"x": ray[0], "s": ray[1], "kappa": kappa})
    if not isinstance(result, tuple) or len(result) != 2:
        raise TypeError("a parameterized optical program must have two Real outputs")
    return result


def _parameterized_action(function: Any, kappa: float) -> RealizedAction:
    x_column = _evaluate_parameter_cell(function, (1.0, 0.0), kappa)
    s_column = _evaluate_parameter_cell(function, (0.0, 1.0), kappa)
    return (
        (x_column[0], s_column[0]),
        (x_column[1], s_column[1]),
    )


def _oriented_readout(function: Any, ray: Ray) -> float:
    result = function.evaluate({"x-output": ray[0], "s-output": ray[1]})
    if isinstance(result, tuple):
        raise TypeError("the oriented optical readout must be scalar")
    return result


def _evaluate_parameter_objective(
    function: Any, ray: Ray, kappa: float
) -> float:
    result = function.evaluate({"x": ray[0], "s": ray[1], "kappa": kappa})
    if isinstance(result, tuple):
        raise TypeError("the parameterized optical objective must be scalar")
    return result


def _trajectory(function: Any, initial: Ray, steps: int) -> tuple[Ray, ...]:
    states = [initial]
    for _ in range(steps):
        states.append(_evaluate(function, states[-1]))
    return tuple(states)


def _realized_action(function: Any) -> RealizedAction:
    """Observe a two-port numerical action after the program has been checked."""

    x_column = _evaluate(function, (1.0, 0.0))
    s_column = _evaluate(function, (0.0, 1.0))
    return (
        (x_column[0], s_column[0]),
        (x_column[1], s_column[1]),
    )


def _trace(action: RealizedAction) -> float:
    return action[0][0] + action[1][1]


def _determinant(action: RealizedAction) -> float:
    return action[0][0] * action[1][1] - action[0][1] * action[1][0]


def _classification(action: RealizedAction) -> str:
    discriminant = _trace(action) ** 2 - 4.0 * _determinant(action)
    if discriminant < 0.0:
        return "elliptic"
    if discriminant > 0.0:
        return "hyperbolic"
    return "parabolic"


def _finite_projective_fixed_points(action: RealizedAction) -> tuple[complex, ...]:
    """Solve z=(a z+b)/(c z+d) only after observing the real action."""

    (a, b), (c, d) = action
    linear = d - a
    constant = -b
    if c == 0.0:
        if linear == 0.0:
            return ()
        return (complex(-constant / linear),)

    discriminant = complex(linear * linear - 4.0 * c * constant)
    root = cmath.sqrt(discriminant)
    return (
        (-linear + root) / (2.0 * c),
        (-linear - root) / (2.0 * c),
    )


def _output_source_support(function: Any) -> tuple[frozenset[str], ...]:
    diagram = function.ir
    occurrence_sources = {
        occurrence["id"]: occurrence["source"] for occurrence in diagram["occurrences"]
    }
    return tuple(
        frozenset(occurrence_sources[occurrence] for occurrence in output["lineage"])
        for output in diagram["outputs"]
    )


def _six_state_orientation(value: SixState) -> SixState:
    """The already derived Omega action, used here as a prior bounded witness."""

    t, s, r, sr, rt, ts = value
    return (-sr, -rt, -ts, t, s, r)


def _six_state_basis(index: int) -> SixState:
    return tuple(float(position == index) for position in range(6))  # type: ignore[return-value]


def _optical_closure(value: SixState, pair: tuple[int, int]) -> Ray:
    """Observe one aspect--opposite-face plane in the optical orientation."""

    aspect, opposite_face = pair
    return value[aspect], -value[opposite_face]


def _source_incidence(function: Any) -> SourceIncidence:
    supports = _output_source_support(function)
    return (
        (len(supports[0]), len(supports[0] & supports[1])),
        (len(supports[1] & supports[0]), len(supports[1])),
    )


def _program_aware_observation(function: Any) -> ProgramAwareObservation:
    return (
        _realized_action(function),
        _source_incidence(function),
        tuple(event["kind"] for event in function.history["prefix"]),
    )


def _forget_program_geometry(observation: ProgramAwareObservation) -> RealizedAction:
    return observation[0]


def _projectivize(action: RealizedAction) -> RealizedAction:
    """Quotient the two determinant-one oriented lifts by their central sign."""

    flattened = tuple(coordinate for row in action for coordinate in row)
    leading = next(coordinate for coordinate in flattened if coordinate != 0.0)
    sign = 1.0 if leading > 0.0 else -1.0
    return tuple(
        tuple(sign * coordinate for coordinate in row) for row in action
    )  # type: ignore[return-value]


def _wire_endpoint(wire: MappingView) -> WireEndpoint:
    producer = wire["producer"]
    producer_id = producer.get("node", producer.get("index"))
    if not isinstance(producer_id, int):
        raise TypeError("a checked wire producer must have an integer identifier")
    return WireEndpoint(
        producer_kind=producer["kind"],
        producer_id=producer_id,
        output_index=wire["output_index"],
    )


def _bounded_forward_node(
    operation: str,
    arguments: tuple[float, ...],
    parameters: MappingView,
) -> tuple[float, ...]:
    if operation == "constant":
        value = parameters["value"]
        return (value["numerator"] / value["denominator"],)
    if operation == "copy":
        return (arguments[0], arguments[0])
    if operation == "add":
        return (arguments[0] + arguments[1],)
    if operation in {"mul", "scale"}:
        return (arguments[0] * arguments[1],)
    if operation == "neg":
        return (-arguments[0],)
    raise TypeError(f"operation outside the bounded backward witness: {operation!r}")


def _bounded_reverse_node(
    operation: str,
    arguments: tuple[float, ...],
    output_demands: tuple[float, ...],
) -> tuple[float, ...]:
    if operation == "constant":
        return ()
    if operation == "copy":
        return (output_demands[0] + output_demands[1],)
    if operation == "add":
        return (output_demands[0], output_demands[0])
    if operation in {"mul", "scale"}:
        return (
            output_demands[0] * arguments[1],
            output_demands[0] * arguments[0],
        )
    if operation == "neg":
        return (-output_demands[0],)
    raise TypeError(f"operation outside the bounded backward witness: {operation!r}")


def _research_backward_probe(
    function: Any,
    inputs: Mapping[str, float],
    output_probe: Sequence[float],
) -> BackwardProbeWitness:
    """Propagate a numerical probe over existing checked endpoints and lineage."""

    if function.validation_certificate["graph"] != "checked":
        raise ValueError("the research witness requires a Rust-checked diagram")

    diagram = function.ir
    input_ports = tuple(diagram["signature"]["inputs"])
    if set(inputs) != {port["name"] for port in input_ports}:
        raise TypeError("backward witness inputs differ from the checked domain")
    if len(output_probe) != len(diagram["outputs"]):
        raise TypeError("output probe arity differs from the checked codomain")

    occurrence_sources = {
        occurrence["id"]: occurrence["source"]
        for occurrence in diagram["occurrences"]
    }
    consumer_wires = (
        *(wire for node in diagram["nodes"] for wire in node["inputs"]),
        *diagram["outputs"],
    )
    wire_metadata: dict[WireEndpoint, tuple[tuple[str, ...], tuple[str, ...]]] = {}
    for wire in consumer_wires:
        endpoint = _wire_endpoint(wire)
        lineage = tuple(wire["lineage"])
        metadata = (
            lineage,
            tuple(occurrence_sources[occurrence] for occurrence in lineage),
        )
        if endpoint in wire_metadata:
            raise AssertionError("Rust-checked linear use exposed an aliased endpoint")
        wire_metadata[endpoint] = metadata

    endpoint_values = {
        WireEndpoint("input", index, 0): float(inputs[port["name"]])
        for index, port in enumerate(input_ports)
    }
    operation_rules = set()
    for node in diagram["nodes"]:
        operation_ref = node["operation"]
        operation = operation_ref["name"]
        if (
            operation_ref["namespace"] != "adva.builtin"
            or operation_ref["version"] != 1
            or operation not in BOUNDED_BACKWARD_OPERATIONS
        ):
            raise TypeError("the diagram leaves the bounded builtin research fragment")
        arguments = tuple(
            endpoint_values[_wire_endpoint(wire)] for wire in node["inputs"]
        )
        outputs = _bounded_forward_node(
            operation,
            arguments,
            operation_ref.get("parameters", {}),
        )
        if len(outputs) != len(node["output_types"]):
            raise AssertionError("bounded oracle output arity differs from checked IR")
        for output_index, value in enumerate(outputs):
            endpoint_values[
                WireEndpoint("node", node["id"], output_index)
            ] = value
        operation_rules.add(
            f'{operation_ref["namespace"]}:{operation}@{operation_ref["version"]}'
        )

    outputs = tuple(
        endpoint_values[_wire_endpoint(wire)] for wire in diagram["outputs"]
    )
    native_outputs = function.evaluate(inputs)
    native_tuple = native_outputs if isinstance(native_outputs, tuple) else (native_outputs,)
    if outputs != native_tuple:
        raise AssertionError("bounded forward oracle differs from Rust execution")

    demands: dict[WireEndpoint, float] = {}
    for wire, coefficient in zip(diagram["outputs"], output_probe, strict=True):
        endpoint = _wire_endpoint(wire)
        demands[endpoint] = demands.get(endpoint, 0.0) + float(coefficient)

    reversed_node_demands = []
    for node in reversed(diagram["nodes"]):
        operation = node["operation"]["name"]
        output_endpoints = tuple(
            WireEndpoint("node", node["id"], output_index)
            for output_index in range(len(node["output_types"]))
        )
        output_demands = tuple(demands.get(endpoint, 0.0) for endpoint in output_endpoints)
        arguments = tuple(
            endpoint_values[_wire_endpoint(wire)] for wire in node["inputs"]
        )
        input_demands = _bounded_reverse_node(operation, arguments, output_demands)
        for wire, coefficient in zip(node["inputs"], input_demands, strict=True):
            endpoint = _wire_endpoint(wire)
            demands[endpoint] = demands.get(endpoint, 0.0) + coefficient
        reversed_node_demands.append(
            NodeDemand(
                node_id=node["id"],
                operation=operation,
                output_demands=output_demands,
                input_demands=input_demands,
                input_lineages=tuple(tuple(wire["lineage"]) for wire in node["inputs"]),
            )
        )

    demand_records = tuple(
        ProbeDemand(
            endpoint=endpoint,
            coefficient=demands.get(endpoint, 0.0),
            lineage=wire_metadata[endpoint][0],
            sources=wire_metadata[endpoint][1],
        )
        for endpoint in sorted(wire_metadata)
    )
    input_demands = tuple(
        (
            port["name"],
            demands.get(WireEndpoint("input", index, 0), 0.0),
        )
        for index, port in enumerate(input_ports)
    )
    return BackwardProbeWitness(
        outputs=outputs,
        input_demands=input_demands,
        demands=demand_records,
        node_demands=tuple(reversed(reversed_node_demands)),
        operation_rules=tuple(sorted(operation_rules)),
    )


def test_real_optical_programs_cross_the_checked_two_port_boundary() -> None:
    functions = _functions()

    fixed_two_port_names = (
        "direct-quarter",
        "factorized-quarter",
        "inverse-quarter",
        "half-turn",
        "full-turn",
        "stable-cell",
        "parabolic-cell",
        "hyperbolic-cell",
    )
    for name in fixed_two_port_names:
        function = functions[name]
        assert function.validation_certificate["graph"] == "checked"
        assert function.signature.inputs == (("x", "real"), ("s", "real"))
        assert function.signature.outputs == ("real", "real")

    assert _evaluate(functions["direct-quarter"], (2.0, 3.0)) == (3.0, -2.0)
    assert _evaluate(functions["factorized-quarter"], (2.0, 3.0)) == (3.0, -2.0)
    assert _evaluate(functions["inverse-quarter"], (2.0, 3.0)) == (-3.0, 2.0)
    assert _evaluate(functions["half-turn"], (2.0, 3.0)) == (-2.0, -3.0)
    assert _evaluate(functions["full-turn"], (2.0, 3.0)) == (2.0, 3.0)


def test_real_device_chain_derives_negative_reciprocal_and_complex_fixed_points() -> None:
    functions = _functions()
    direct = functions["direct-quarter"]
    factorized = functions["factorized-quarter"]
    inverse = functions["inverse-quarter"]
    fixtures: tuple[Ray, ...] = (
        (1.0, 0.0),
        (0.0, 1.0),
        (2.0, -3.0),
        (-5.0, 7.0),
    )

    for ray in fixtures:
        forward = _evaluate(factorized, ray)
        assert forward == _evaluate(direct, ray)
        assert _evaluate(factorized, forward) == (-ray[0], -ray[1])
        assert _evaluate(inverse, forward) == ray
        assert _evaluate(inverse, ray) == (-forward[0], -forward[1])

    for z in (-3.0, -0.5, 0.25, 2.0, 5.0):
        forward = _evaluate(factorized, (z, 1.0))
        backward = _evaluate(inverse, (z, 1.0))
        assert forward[0] / forward[1] == pytest.approx(-1.0 / z)
        assert backward[0] / backward[1] == pytest.approx(-1.0 / z)

    action = _realized_action(factorized)
    assert action == ((0.0, 1.0), (-1.0, 0.0))
    assert _determinant(action) == 1.0
    assert _trace(action) == 0.0
    roots = _finite_projective_fixed_points(action)
    assert set(roots) == {1j, -1j}


def test_real_program_iteration_recovers_the_three_projective_regimes() -> None:
    functions = _functions()
    stable = functions["stable-cell"]
    parabolic = functions["parabolic-cell"]
    hyperbolic = functions["hyperbolic-cell"]

    actions = tuple(_realized_action(function) for function in (stable, parabolic, hyperbolic))
    assert actions == (
        ((0.0, 1.0), (-1.0, 1.0)),
        ((1.0, 1.0), (0.0, 1.0)),
        ((2.0, 1.0), (1.0, 1.0)),
    )
    assert tuple(_determinant(action) for action in actions) == (1.0, 1.0, 1.0)
    assert tuple(_trace(action) for action in actions) == (1.0, 2.0, 3.0)
    assert tuple(_classification(action) for action in actions) == (
        "elliptic",
        "parabolic",
        "hyperbolic",
    )

    stable_roots = _finite_projective_fixed_points(actions[0])
    parabolic_roots = _finite_projective_fixed_points(actions[1])
    hyperbolic_roots = _finite_projective_fixed_points(actions[2])
    assert len(stable_roots) == 2
    assert stable_roots[0].conjugate() == stable_roots[1]
    assert {root.imag > 0.0 for root in stable_roots} == {False, True}
    assert parabolic_roots == ()
    assert len(hyperbolic_roots) == 2
    assert all(root.imag == 0.0 for root in hyperbolic_roots)

    initial = (1.0, 1.0)
    stable_orbit = _trajectory(stable, initial, 6)
    parabolic_orbit = _trajectory(parabolic, initial, 12)
    hyperbolic_orbit = _trajectory(hyperbolic, initial, 12)
    assert stable_orbit == (
        (1.0, 1.0),
        (1.0, 0.0),
        (0.0, -1.0),
        (-1.0, -1.0),
        (-1.0, 0.0),
        (0.0, 1.0),
        (1.0, 1.0),
    )
    assert parabolic_orbit[-1] == (13.0, 1.0)
    assert hyperbolic_orbit[-1] == (121393.0, 75025.0)


def test_same_numerical_shadow_retains_a_program_geometry_residual() -> None:
    functions = _functions()
    direct = functions["direct-quarter"]
    factorized = functions["factorized-quarter"]

    assert _realized_action(direct) == _realized_action(factorized)
    assert direct.ir != factorized.ir
    assert direct.history != factorized.history
    assert len(factorized.history["prefix"]) > len(direct.history["prefix"])

    direct_support = _output_source_support(direct)
    factorized_support = _output_source_support(factorized)
    assert tuple(map(len, direct_support)) == (1, 1)
    assert direct_support[0].isdisjoint(direct_support[1])
    assert tuple(map(len, factorized_support)) == (2, 2)
    assert factorized_support[0] == factorized_support[1]


def test_each_aspect_plane_has_an_explicit_commuting_optical_closure() -> None:
    optical_action = _functions()["factorized-quarter"]

    for pair in ASPECT_OPPOSITE_PAIRS:
        images = {_optical_closure(_six_state_basis(index), pair) for index in range(6)}
        assert (1.0, 0.0) in images
        assert (0.0, -1.0) in images

        forgotten = tuple(index for index in range(6) if index not in pair)
        assert len(forgotten) == 4
        assert all(
            _optical_closure(_six_state_basis(index), pair) == (0.0, 0.0)
            for index in forgotten
        )

        for index in range(6):
            value = _six_state_basis(index)
            observed_after_orientation = _optical_closure(
                _six_state_orientation(value),
                pair,
            )
            propagated_after_observation = _evaluate(
                optical_action,
                _optical_closure(value, pair),
            )
            assert observed_after_orientation == propagated_after_observation


def test_observer_tower_separates_program_orientation_and_projective_levels() -> None:
    functions = _functions()
    direct = _program_aware_observation(functions["direct-quarter"])
    factorized = _program_aware_observation(functions["factorized-quarter"])
    inverse = _program_aware_observation(functions["inverse-quarter"])

    # Program-aware observation retains construction and source incidence.
    assert direct != factorized
    assert direct[1] == ((1, 0), (0, 1))
    assert factorized[1] == ((2, 2), (2, 2))

    # Forgetting program geometry identifies the direct and factorized value
    # actions but still distinguishes the two oriented lifts.
    direct_oriented = _forget_program_geometry(direct)
    factorized_oriented = _forget_program_geometry(factorized)
    inverse_oriented = _forget_program_geometry(inverse)
    assert direct_oriented == factorized_oriented
    assert factorized_oriented != inverse_oriented
    assert inverse_oriented == tuple(
        tuple(-coordinate for coordinate in row) for row in factorized_oriented
    )

    # The projective quotient then forgets the central sign as a second,
    # strictly coarser observation.
    assert _projectivize(direct_oriented) == _projectivize(factorized_oriented)
    assert _projectivize(factorized_oriented) == _projectivize(inverse_oriented)


def test_one_parameter_program_crosses_the_three_optical_regimes() -> None:
    parameter_cell = _functions()["parameter-cell"]

    assert parameter_cell.validation_certificate["graph"] == "checked"
    assert parameter_cell.signature.inputs == (
        ("x", "real"),
        ("s", "real"),
        ("kappa", "real"),
    )
    assert parameter_cell.signature.outputs == ("real", "real")
    assert len(parameter_cell.source_partition) == 3
    assert tuple(map(len, _output_source_support(parameter_cell))) == (3, 3)

    kappas = (-1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0)
    actions = tuple(_parameterized_action(parameter_cell, kappa) for kappa in kappas)
    assert actions == tuple(
        ((1.0 - kappa, 1.0), (-kappa, 1.0)) for kappa in kappas
    )
    assert tuple(_determinant(action) for action in actions) == (1.0,) * len(kappas)
    assert tuple(_trace(action) for action in actions) == tuple(
        2.0 - kappa for kappa in kappas
    )
    assert tuple(
        _trace(action) ** 2 - 4.0 * _determinant(action) for action in actions
    ) == tuple(kappa * (kappa - 4.0) for kappa in kappas)
    assert tuple(_classification(action) for action in actions) == (
        "hyperbolic",
        "parabolic",
        "elliptic",
        "elliptic",
        "elliptic",
        "parabolic",
        "hyperbolic",
    )


def test_rust_parameter_differential_matches_formula_and_finite_difference() -> None:
    functions = _functions()
    device_objective = functions["parameter-objective"]
    direct_objective = functions["direct-parameter-objective"]
    fixtures = (
        {"x": 2.0, "s": 3.0, "kappa": 1.0},
        {"x": -1.0, "s": 2.0, "kappa": 0.5},
        {"x": 0.0, "s": 4.0, "kappa": 3.0},
    )

    assert device_objective.ir != direct_objective.ir
    assert device_objective.history != direct_objective.history
    assert len(_output_source_support(device_objective)[0]) == 3

    for inputs in fixtures:
        value, gradient, certificate = device_objective.value_and_gradient(inputs)
        direct_value, direct_gradient, direct_certificate = (
            direct_objective.value_and_gradient(inputs)
        )
        expected_value = (
            inputs["x"]
            + 3.0 * inputs["s"]
            - 3.0 * inputs["kappa"] * inputs["x"]
        )
        expected_gradient = {
            "x": 1.0 - 3.0 * inputs["kappa"],
            "s": 3.0,
            "kappa": -3.0 * inputs["x"],
        }

        assert value == pytest.approx(expected_value)
        assert gradient == pytest.approx(expected_gradient)
        assert direct_value == pytest.approx(value)
        assert direct_gradient == pytest.approx(gradient)

        step = 1.0e-6
        forward = _evaluate_parameter_objective(
            device_objective,
            (inputs["x"], inputs["s"]),
            inputs["kappa"] + step,
        )
        backward = _evaluate_parameter_objective(
            device_objective,
            (inputs["x"], inputs["s"]),
            inputs["kappa"] - step,
        )
        assert gradient["kappa"] == pytest.approx(
            (forward - backward) / (2.0 * step),
            abs=1.0e-8,
        )

        assert certificate["method"] == "forward-mode structural differential"
        assert certificate["diagram_integrity"] == "checked"
        assert set(certificate["operation_rules"]) == {
            "adva.builtin:add@1",
            "adva.builtin:constant@1",
            "adva.builtin:copy@1",
            "adva.builtin:mul@1",
            "adva.builtin:neg@1",
            "adva.builtin:scale@1",
        }
        assert direct_certificate["diagram_integrity"] == "checked"


def test_oriented_objective_does_not_descend_to_the_projective_level() -> None:
    functions = _functions()
    parameter_cell = functions["parameter-cell"]
    readout = functions["oriented-readout"]
    ray = _evaluate_parameter_cell(parameter_cell, (2.0, 3.0), 1.0)
    opposite_lift = (-ray[0], -ray[1])

    # The two nonzero lifts determine the same projective ray.
    assert ray != opposite_lift
    assert ray[0] * opposite_lift[1] == ray[1] * opposite_lift[0]

    # The declared scalar readout retains the lift orientation.
    value = _oriented_readout(readout, ray)
    opposite_value = _oriented_readout(readout, opposite_lift)
    assert value == 5.0
    assert opposite_value == -value


def test_backward_probe_satisfies_the_forward_pairing_law() -> None:
    functions = _functions()
    parameter_cell = functions["parameter-cell"]
    inputs = {"x": 2.0, "s": 3.0, "kappa": 1.0}
    output_probe = (1.0, 2.0)
    witness = _research_backward_probe(parameter_cell, inputs, output_probe)

    values, jacobian, certificate = parameter_cell.value_and_gradient(inputs)
    assert isinstance(values, tuple)
    assert isinstance(jacobian, tuple)
    assert witness.outputs == values == (3.0, 1.0)
    assert witness.input_demand_map == pytest.approx(
        {"x": -2.0, "s": 3.0, "kappa": -6.0}
    )
    assert witness.operation_rules == (
        "adva.builtin:add@1",
        "adva.builtin:copy@1",
        "adva.builtin:mul@1",
        "adva.builtin:neg@1",
    )
    assert certificate["diagram_integrity"] == "checked"

    tangent_directions = (
        {"x": 1.0, "s": 0.0, "kappa": 0.0},
        {"x": 0.0, "s": 1.0, "kappa": 0.0},
        {"x": 0.0, "s": 0.0, "kappa": 1.0},
        {"x": 2.0, "s": -1.0, "kappa": 0.5},
    )
    for tangent in tangent_directions:
        forward_tangent = tuple(
            sum(output_gradient[name] * tangent[name] for name in tangent)
            for output_gradient in jacobian
        )
        codomain_pairing = sum(
            coefficient * component
            for coefficient, component in zip(
                output_probe,
                forward_tangent,
                strict=True,
            )
        )
        domain_pairing = sum(
            witness.input_demand_map[name] * tangent[name] for name in tangent
        )
        assert codomain_pairing == pytest.approx(domain_pairing)

    _, objective_gradient, _ = functions["parameter-objective"].value_and_gradient(
        inputs
    )
    assert witness.input_demand_map == pytest.approx(objective_gradient)

    input_records = tuple(
        record
        for record in witness.demands
        if record.endpoint.producer_kind == "input"
    )
    assert len(input_records) == 3
    assert all(len(record.lineage) == len(record.sources) == 1 for record in input_records)
    assert len({record.sources[0] for record in input_records}) == 3


def test_copy_demands_follow_checked_occurrence_branches_before_recombining() -> None:
    parameter_cell = _functions()["parameter-cell"]
    inputs = {"x": 2.0, "s": 3.0, "kappa": 1.0}
    witness = _research_backward_probe(parameter_cell, inputs, (1.0, 2.0))
    diagram = parameter_cell.ir
    records = witness.demand_by_endpoint
    occurrence_sources = {
        occurrence["id"]: occurrence["source"]
        for occurrence in diagram["occurrences"]
    }
    copy_nodes = tuple(
        node for node in diagram["nodes"] if node["operation"]["name"] == "copy"
    )
    assert len(copy_nodes) == 2

    branches_by_parent_count = {}
    for node in copy_nodes:
        parent_endpoint = _wire_endpoint(node["inputs"][0])
        parent_lineage = tuple(node["inputs"][0]["lineage"])
        branches = tuple(
            records[WireEndpoint("node", node["id"], branch)] for branch in range(2)
        )
        children_by_parent = {
            event["parent"]: tuple(event["children"])
            for event in diagram["history"]["prefix"]
            if event["kind"] == "copy" and event["node"] == node["id"]
        }
        for branch, record in enumerate(branches):
            expected_lineage = tuple(
                children_by_parent[parent][branch] for parent in parent_lineage
            )
            assert record.lineage == expected_lineage
            assert record.sources == tuple(
                occurrence_sources[occurrence] for occurrence in expected_lineage
            )
        assert records[parent_endpoint].coefficient == pytest.approx(
            sum(record.coefficient for record in branches)
        )
        branches_by_parent_count[len(parent_lineage)] = branches

    single_source_branches = branches_by_parent_count[1]
    merged_lineage_branches = branches_by_parent_count[3]
    assert tuple(record.coefficient for record in single_source_branches) == (1.0, -3.0)
    assert tuple(record.coefficient for record in merged_lineage_branches) == (1.0, 2.0)
    assert single_source_branches[0].lineage != single_source_branches[1].lineage
    assert set(merged_lineage_branches[0].lineage).isdisjoint(
        merged_lineage_branches[1].lineage
    )
    assert merged_lineage_branches[0].sources == merged_lineage_branches[1].sources
    assert len(set(merged_lineage_branches[0].sources)) == 3


def test_equal_root_gradients_retain_distinct_internal_demand_fields() -> None:
    functions = _functions()
    inputs = {"x": 2.0, "s": 3.0, "kappa": 1.0}
    device = _research_backward_probe(functions["parameter-objective"], inputs, (1.0,))
    direct = _research_backward_probe(
        functions["direct-parameter-objective"],
        inputs,
        (1.0,),
    )

    assert device.outputs == direct.outputs == (5.0,)
    assert device.input_demand_map == direct.input_demand_map == {
        "x": -2.0,
        "s": 3.0,
        "kappa": -6.0,
    }
    assert len(device.node_demands) > len(direct.node_demands)
    assert tuple(record.operation for record in device.node_demands) != tuple(
        record.operation for record in direct.node_demands
    )

    def copy_lineage_sizes(function: Any, witness: BackwardProbeWitness) -> list[int]:
        copy_node_ids = {
            node["id"]
            for node in function.ir["nodes"]
            if node["operation"]["name"] == "copy"
        }
        return sorted(
            len(record.lineage)
            for record in witness.demands
            if record.endpoint.producer_kind == "node"
            and record.endpoint.producer_id in copy_node_ids
        )

    assert copy_lineage_sizes(functions["parameter-objective"], device) == [1, 1, 3, 3]
    assert copy_lineage_sizes(functions["direct-parameter-objective"], direct) == [1, 1]
