from __future__ import annotations

import cmath
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Any

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
    exp-two-port-readout
    exp-parameter-cell
    exp-readout
    parameter-objective
    exp-parameter-objective
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

  ; Keep two output ports so independent symbolic probes can expose the
  ; expression-valued matrix-like shadow without making it the ontology.
  (def exp-two-port-readout
    (fn ((x-output Real) (s-output Real)) (outputs Real Real)
      (frontier
        (exp (use x-output))
        (use s-output))))

  (def exp-parameter-cell
    (fn ((x Real) (s Real) (kappa Real)) (outputs Real Real)
      (call exp-two-port-readout
        (call parameter-cell
          (frontier
            (use x)
            (use s)
            (use kappa))))))

  ; Nonlinear readout whose backward cut demand contains an exponential
  ; intermediate expression rather than a fitted numerical coefficient.
  (def exp-readout
    (fn ((x-output Real) (s-output Real)) Real
      (add
        (frontier
          (exp (use x-output))
          (use s-output)))))

  ; Device-history realization of L_kappa = ell(p_kappa(x, s)).
  (def parameter-objective
    (fn ((x Real) (s Real) (kappa Real)) Real
      (call oriented-readout
        (call parameter-cell
          (frontier
            (use x)
            (use s)
            (use kappa))))))

  ; exp((1-kappa)x+s) + (-kappa x+s), factorized through the device.
  (def exp-parameter-objective
    (fn ((x Real) (s Real) (kappa Real)) Real
      (call exp-readout
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
    {"constant", "copy", "add", "mul", "scale", "neg", "exp"}
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


@dataclass(frozen=True, slots=True)
class DemandExpression:
    """Unsimplified arithmetic expression used only by the research witness."""

    kind: str
    data: tuple[Any, ...] = ()
    arguments: tuple[DemandExpression, ...] = ()

    @classmethod
    def constant(cls, numerator: int, denominator: int = 1) -> DemandExpression:
        value = Fraction(numerator, denominator)
        return cls("constant", (value.numerator, value.denominator))

    @classmethod
    def input(
        cls,
        name: str,
        occurrence: str,
        source: str,
    ) -> DemandExpression:
        return cls("input", (name, occurrence, source))

    @classmethod
    def probe(cls, name: str) -> DemandExpression:
        return cls("probe", (name,))

    @classmethod
    def add(
        cls,
        left: DemandExpression,
        right: DemandExpression,
    ) -> DemandExpression:
        return cls("add", arguments=(left, right))

    @classmethod
    def multiply(
        cls,
        left: DemandExpression,
        right: DemandExpression,
    ) -> DemandExpression:
        return cls("mul", arguments=(left, right))

    @classmethod
    def negate(cls, argument: DemandExpression) -> DemandExpression:
        return cls("neg", arguments=(argument,))

    @classmethod
    def exponential(cls, argument: DemandExpression) -> DemandExpression:
        return cls("exp", arguments=(argument,))

    def evaluate(
        self,
        inputs: Mapping[str, float],
        probes: Mapping[str, float] | None = None,
    ) -> float:
        if self.kind == "constant":
            return self.data[0] / self.data[1]
        if self.kind == "input":
            return float(inputs[self.data[0]])
        if self.kind == "probe":
            if probes is None:
                raise TypeError("a symbolic probe expression needs probe values")
            return float(probes[self.data[0]])
        if self.kind == "add":
            return self.arguments[0].evaluate(
                inputs, probes
            ) + self.arguments[1].evaluate(inputs, probes)
        if self.kind == "mul":
            return self.arguments[0].evaluate(
                inputs, probes
            ) * self.arguments[1].evaluate(inputs, probes)
        if self.kind == "neg":
            return -self.arguments[0].evaluate(inputs, probes)
        if self.kind == "exp":
            return math.exp(self.arguments[0].evaluate(inputs, probes))
        raise TypeError(f"unknown demand expression kind: {self.kind!r}")

    def to_lisp(self) -> str:
        if self.kind == "constant":
            numerator, denominator = self.data
            return str(numerator) if denominator == 1 else f"{numerator}/{denominator}"
        if self.kind == "input":
            return f"(use {self.data[0]})"
        if self.kind == "probe":
            return f"(probe {self.data[0]})"
        if self.kind == "add":
            left, right = self.arguments
            return f"(add (frontier {left.to_lisp()} {right.to_lisp()}))"
        if self.kind == "mul":
            left, right = self.arguments
            return f"(mul (frontier {left.to_lisp()} {right.to_lisp()}))"
        if self.kind == "neg":
            return f"(neg {self.arguments[0].to_lisp()})"
        if self.kind == "exp":
            return f"(exp {self.arguments[0].to_lisp()})"
        raise TypeError(f"unknown demand expression kind: {self.kind!r}")

    def input_uses(self) -> tuple[str, ...]:
        if self.kind == "input":
            return (self.data[0],)
        return tuple(
            name for argument in self.arguments for name in argument.input_uses()
        )

    def probe_uses(self) -> tuple[str, ...]:
        if self.kind == "probe":
            return (self.data[0],)
        return tuple(
            name for argument in self.arguments for name in argument.probe_uses()
        )

    def input_audit(self) -> tuple[tuple[str, str, str], ...]:
        if self.kind == "input":
            return (self.data,)  # type: ignore[return-value]
        return tuple(
            item for argument in self.arguments for item in argument.input_audit()
        )

    def operation_kinds(self) -> frozenset[str]:
        return frozenset(
            {self.kind}
            | {
                kind
                for argument in self.arguments
                for kind in argument.operation_kinds()
            }
        )


@dataclass(frozen=True, slots=True)
class SymbolicProbeDemand:
    endpoint: WireEndpoint
    coefficient: DemandExpression
    lineage: tuple[str, ...]
    sources: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SymbolicBackwardProbeWitness:
    outputs: tuple[DemandExpression, ...]
    input_demands: tuple[tuple[str, DemandExpression], ...]
    demands: tuple[SymbolicProbeDemand, ...]
    operation_rules: tuple[str, ...]

    @property
    def input_demand_map(self) -> dict[str, DemandExpression]:
        return dict(self.input_demands)

    @property
    def demand_by_endpoint(self) -> dict[WireEndpoint, SymbolicProbeDemand]:
        return {record.endpoint: record for record in self.demands}


@dataclass(frozen=True, slots=True)
class ProbeLinearForm:
    """Sparse probe coefficients with a probe-free expression constant."""

    constant: DemandExpression | None
    coefficients: tuple[tuple[str, DemandExpression], ...]

    @property
    def coefficient_map(self) -> dict[str, DemandExpression]:
        return dict(self.coefficients)


@dataclass(frozen=True, slots=True)
class SymbolicCutCompositionWitness:
    """One exact factorization through two nested cuts of the same checked IR."""

    lower_completed: frozenset[int]
    upper_completed: frozenset[int]
    lower_cut_demands: tuple[tuple[WireEndpoint, DemandExpression], ...]
    upper_cut_demands: tuple[tuple[WireEndpoint, DemandExpression], ...]
    direct_demands: tuple[tuple[WireEndpoint, DemandExpression], ...]
    staged_demands: tuple[tuple[WireEndpoint, DemandExpression], ...]

    @property
    def direct_demand_map(self) -> dict[WireEndpoint, DemandExpression]:
        return dict(self.direct_demands)

    @property
    def staged_demand_map(self) -> dict[WireEndpoint, DemandExpression]:
        return dict(self.staged_demands)


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
        "exp-two-port-readout",
        "exp-parameter-cell",
        "exp-readout",
        "parameter-objective",
        "exp-parameter-objective",
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
    if operation == "exp":
        return (math.exp(arguments[0]),)
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
    if operation == "exp":
        return (output_demands[0] * math.exp(arguments[0]),)
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
            or operation_ref["version"] != (2 if operation == "constant" else 1)
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


def _symbolic_forward_node(
    operation: str,
    arguments: tuple[DemandExpression, ...],
    parameters: MappingView,
) -> tuple[DemandExpression, ...]:
    if operation == "constant":
        value = parameters["value"]
        return (DemandExpression.constant(value["numerator"], value["denominator"]),)
    if operation == "copy":
        return (arguments[0], arguments[0])
    if operation == "add":
        return (DemandExpression.add(arguments[0], arguments[1]),)
    if operation in {"mul", "scale"}:
        return (DemandExpression.multiply(arguments[0], arguments[1]),)
    if operation == "neg":
        return (DemandExpression.negate(arguments[0]),)
    if operation == "exp":
        return (DemandExpression.exponential(arguments[0]),)
    raise TypeError(f"operation outside the symbolic backward witness: {operation!r}")


def _symbolic_reverse_node(
    operation: str,
    arguments: tuple[DemandExpression, ...],
    output_demands: tuple[DemandExpression, ...],
) -> tuple[DemandExpression, ...]:
    if operation == "constant":
        return ()
    if operation == "copy":
        return (DemandExpression.add(output_demands[0], output_demands[1]),)
    if operation == "add":
        return (output_demands[0], output_demands[0])
    if operation in {"mul", "scale"}:
        return (
            DemandExpression.multiply(output_demands[0], arguments[1]),
            DemandExpression.multiply(output_demands[0], arguments[0]),
        )
    if operation == "neg":
        return (DemandExpression.negate(output_demands[0]),)
    if operation == "exp":
        return (
            DemandExpression.multiply(
                output_demands[0],
                DemandExpression.exponential(arguments[0]),
            ),
        )
    raise TypeError(f"operation outside the symbolic backward witness: {operation!r}")


def _research_symbolic_backward_probe(
    function: Any,
    output_probe: Sequence[DemandExpression],
) -> SymbolicBackwardProbeWitness:
    """Lift the bounded numerical demand coefficients to unsimplified terms."""

    if function.validation_certificate["graph"] != "checked":
        raise ValueError("the symbolic witness requires a Rust-checked diagram")

    diagram = function.ir
    input_ports = tuple(diagram["signature"]["inputs"])
    if len(output_probe) != len(diagram["outputs"]):
        raise TypeError("symbolic output probe arity differs from the checked codomain")

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

    endpoint_values: dict[WireEndpoint, DemandExpression] = {}
    for index, port in enumerate(input_ports):
        endpoint = WireEndpoint("input", index, 0)
        lineage, sources = wire_metadata[endpoint]
        if len(lineage) != 1 or len(sources) != 1:
            raise AssertionError("a checked input endpoint must have one root occurrence")
        endpoint_values[endpoint] = DemandExpression.input(
            port["name"],
            lineage[0],
            sources[0],
        )

    operation_rules = set()
    for node in diagram["nodes"]:
        operation_ref = node["operation"]
        operation = operation_ref["name"]
        if (
            operation_ref["namespace"] != "adva.builtin"
            or operation_ref["version"] != (2 if operation == "constant" else 1)
            or operation not in BOUNDED_BACKWARD_OPERATIONS
        ):
            raise TypeError("the diagram leaves the symbolic builtin research fragment")
        arguments = tuple(
            endpoint_values[_wire_endpoint(wire)] for wire in node["inputs"]
        )
        outputs = _symbolic_forward_node(
            operation,
            arguments,
            operation_ref.get("parameters", {}),
        )
        if len(outputs) != len(node["output_types"]):
            raise AssertionError("symbolic output arity differs from checked IR")
        for output_index, expression in enumerate(outputs):
            endpoint_values[
                WireEndpoint("node", node["id"], output_index)
            ] = expression
        operation_rules.add(
            f'{operation_ref["namespace"]}:{operation}@{operation_ref["version"]}'
        )

    outputs = tuple(
        endpoint_values[_wire_endpoint(wire)] for wire in diagram["outputs"]
    )
    demands: dict[WireEndpoint, DemandExpression] = {}

    def add_demand(endpoint: WireEndpoint, coefficient: DemandExpression) -> None:
        existing = demands.get(endpoint)
        demands[endpoint] = (
            coefficient
            if existing is None
            else DemandExpression.add(existing, coefficient)
        )

    for wire, coefficient in zip(diagram["outputs"], output_probe, strict=True):
        add_demand(_wire_endpoint(wire), coefficient)

    zero = DemandExpression.constant(0)
    for node in reversed(diagram["nodes"]):
        operation = node["operation"]["name"]
        output_demands = tuple(
            demands.get(WireEndpoint("node", node["id"], output_index), zero)
            for output_index in range(len(node["output_types"]))
        )
        arguments = tuple(
            endpoint_values[_wire_endpoint(wire)] for wire in node["inputs"]
        )
        input_demands = _symbolic_reverse_node(operation, arguments, output_demands)
        for wire, coefficient in zip(node["inputs"], input_demands, strict=True):
            add_demand(_wire_endpoint(wire), coefficient)

    demand_records = tuple(
        SymbolicProbeDemand(
            endpoint=endpoint,
            coefficient=demands.get(endpoint, zero),
            lineage=wire_metadata[endpoint][0],
            sources=wire_metadata[endpoint][1],
        )
        for endpoint in sorted(wire_metadata)
    )
    input_demands = tuple(
        (
            port["name"],
            demands.get(WireEndpoint("input", index, 0), zero),
        )
        for index, port in enumerate(input_ports)
    )
    return SymbolicBackwardProbeWitness(
        outputs=outputs,
        input_demands=input_demands,
        demands=demand_records,
        operation_rules=tuple(sorted(operation_rules)),
    )


def _compile_symbolic_input_demands(
    original_function: Any,
    witness: SymbolicBackwardProbeWitness,
) -> Any:
    """Ask Rust to compile the root demand terms as a fresh checked program."""

    input_ports = tuple(original_function.ir["signature"]["inputs"])
    expressions = tuple(expression for _, expression in witness.input_demands)
    if any(expression.probe_uses() for expression in expressions):
        raise TypeError("the fresh replay compiler does not declare probe generators")
    input_uses = tuple(
        name for expression in expressions for name in expression.input_uses()
    )
    if len(input_uses) != len(set(input_uses)):
        raise TypeError("the bounded replay fixture would require an undeclared copy")
    input_names = tuple(port["name"] for port in input_ports)
    if not set(input_uses) <= set(input_names):
        raise TypeError("a demand expression references an unknown input")

    inputs_source = " ".join(
        f'({port["name"]} Real)' for port in input_ports
    )
    outputs_source = " ".join("Real" for _ in expressions)
    frontier_terms = [expression.to_lisp() for expression in expressions]
    frontier_terms.extend(
        f'(discard (use {name}))' for name in input_names if name not in input_uses
    )
    body_source = "\n          ".join(frontier_terms)
    module_source = f"""
(module symbolic-optical-backward
  (export probe)
  (def probe
    (fn ({inputs_source}) (outputs {outputs_source})
      (frontier
          {body_source}))))
"""
    workspace = link_modules([module_source])
    return workspace.function("symbolic-optical-backward", "probe")


def _probe_linear_form(expression: DemandExpression) -> ProbeLinearForm:
    """Extract a sparse probe-linear shadow without normalizing coefficients."""

    if not expression.probe_uses():
        return ProbeLinearForm(expression, ())
    if expression.kind == "probe":
        return ProbeLinearForm(
            None,
            ((expression.data[0], DemandExpression.constant(1)),),
        )
    if expression.kind == "exp":
        raise TypeError("the bounded probe-linear fragment forbids probes inside exp")

    arguments = tuple(_probe_linear_form(argument) for argument in expression.arguments)
    if expression.kind == "add":
        left, right = arguments
        if left.constant is None:
            constant = right.constant
        elif right.constant is None:
            constant = left.constant
        else:
            constant = DemandExpression.add(left.constant, right.constant)
        left_coefficients = left.coefficient_map
        right_coefficients = right.coefficient_map
        coefficients = []
        for name in sorted(left_coefficients.keys() | right_coefficients.keys()):
            left_coefficient = left_coefficients.get(name)
            right_coefficient = right_coefficients.get(name)
            if left_coefficient is None:
                coefficient = right_coefficient
            elif right_coefficient is None:
                coefficient = left_coefficient
            else:
                coefficient = DemandExpression.add(
                    left_coefficient,
                    right_coefficient,
                )
            if coefficient is None:
                raise AssertionError("probe coefficient union lost both operands")
            coefficients.append((name, coefficient))
        return ProbeLinearForm(constant, tuple(coefficients))

    if expression.kind == "neg":
        argument = arguments[0]
        return ProbeLinearForm(
            None
            if argument.constant is None
            else DemandExpression.negate(argument.constant),
            tuple(
                (name, DemandExpression.negate(coefficient))
                for name, coefficient in argument.coefficients
            ),
        )

    if expression.kind == "mul":
        left, right = arguments
        if left.coefficients and right.coefficients:
            raise TypeError("the demand expression is nonlinear in probe generators")
        if left.coefficients:
            if right.constant is None:
                return ProbeLinearForm(None, ())
            return ProbeLinearForm(
                None
                if left.constant is None
                else DemandExpression.multiply(left.constant, right.constant),
                tuple(
                    (
                        name,
                        DemandExpression.multiply(coefficient, right.constant),
                    )
                    for name, coefficient in left.coefficients
                ),
            )
        if right.coefficients:
            if left.constant is None:
                return ProbeLinearForm(None, ())
            return ProbeLinearForm(
                None
                if right.constant is None
                else DemandExpression.multiply(left.constant, right.constant),
                tuple(
                    (
                        name,
                        DemandExpression.multiply(left.constant, coefficient),
                    )
                    for name, coefficient in right.coefficients
                ),
            )
        if left.constant is None or right.constant is None:
            return ProbeLinearForm(None, ())
        return ProbeLinearForm(
            DemandExpression.multiply(left.constant, right.constant),
            (),
        )

    raise TypeError(
        f"operation {expression.kind!r} is outside the probe-linear extractor"
    )


def _symbolic_causal_opens(function: Any) -> tuple[frozenset[int], ...]:
    """Enumerate every completed event past of one finite checked diagram."""

    nodes = tuple(function.ir["nodes"])
    ordered = tuple(node["id"] for node in nodes)
    predecessors = {
        node["id"]: frozenset(
            wire["producer"]["node"]
            for wire in node["inputs"]
            if wire["producer"]["kind"] == "node"
        )
        for node in nodes
    }
    return tuple(
        completed
        for size in range(len(ordered) + 1)
        for selected in combinations(ordered, size)
        for completed in (frozenset(selected),)
        if all(predecessors[node_id] <= completed for node_id in completed)
    )


def _symbolic_cut_endpoints(
    diagram: MappingView,
    completed: frozenset[int],
) -> tuple[WireEndpoint, ...]:
    """Read the raw endpoints crossing one completed-past boundary."""

    consumers = (
        *(
            wire
            for node in diagram["nodes"]
            if node["id"] not in completed
            for wire in node["inputs"]
        ),
        *diagram["outputs"],
    )
    crossing = []
    for wire in consumers:
        producer = wire["producer"]
        if producer["kind"] == "input" or producer["node"] in completed:
            crossing.append(_wire_endpoint(wire))
    if len(crossing) != len(set(crossing)):
        raise AssertionError("Rust-checked linear use exposed an aliased cut endpoint")
    return tuple(sorted(crossing))


def _symbolic_forward_endpoint_values(
    function: Any,
    metadata: Mapping[WireEndpoint, SymbolicProbeDemand],
) -> dict[WireEndpoint, DemandExpression]:
    """Replay forward expressions while retaining original root input audit data."""

    diagram = function.ir
    values: dict[WireEndpoint, DemandExpression] = {}
    for index, port in enumerate(diagram["signature"]["inputs"]):
        endpoint = WireEndpoint("input", index, 0)
        record = metadata[endpoint]
        if len(record.lineage) != 1 or len(record.sources) != 1:
            raise AssertionError("a checked input endpoint must have one root occurrence")
        values[endpoint] = DemandExpression.input(
            port["name"],
            record.lineage[0],
            record.sources[0],
        )

    for node in diagram["nodes"]:
        operation_ref = node["operation"]
        operation = operation_ref["name"]
        if (
            operation_ref["namespace"] != "adva.builtin"
            or operation_ref["version"] != (2 if operation == "constant" else 1)
            or operation not in BOUNDED_BACKWARD_OPERATIONS
        ):
            raise TypeError("the diagram leaves the symbolic cut fragment")
        arguments = tuple(values[_wire_endpoint(wire)] for wire in node["inputs"])
        outputs = _symbolic_forward_node(
            operation,
            arguments,
            operation_ref.get("parameters", {}),
        )
        for output_index, expression in enumerate(outputs):
            values[WireEndpoint("node", node["id"], output_index)] = expression
    return values


def _symbolic_reverse_segment(
    diagram: MappingView,
    endpoint_values: Mapping[WireEndpoint, DemandExpression],
    active_nodes: frozenset[int],
    seeds: Sequence[tuple[WireEndpoint, DemandExpression]],
) -> dict[WireEndpoint, DemandExpression]:
    """Transport demands through one causally contiguous node segment."""

    node_ids = frozenset(node["id"] for node in diagram["nodes"])
    if not active_nodes <= node_ids:
        raise ValueError("a symbolic reverse segment contains an unknown node")

    demands: dict[WireEndpoint, DemandExpression] = {}

    def add_demand(endpoint: WireEndpoint, coefficient: DemandExpression) -> None:
        existing = demands.get(endpoint)
        demands[endpoint] = (
            coefficient
            if existing is None
            else DemandExpression.add(existing, coefficient)
        )

    for endpoint, coefficient in seeds:
        add_demand(endpoint, coefficient)

    zero = DemandExpression.constant(0)
    for node in reversed(diagram["nodes"]):
        if node["id"] not in active_nodes:
            continue
        output_demands = tuple(
            demands.get(WireEndpoint("node", node["id"], output_index), zero)
            for output_index in range(len(node["output_types"]))
        )
        arguments = tuple(
            endpoint_values[_wire_endpoint(wire)] for wire in node["inputs"]
        )
        input_demands = _symbolic_reverse_node(
            node["operation"]["name"],
            arguments,
            output_demands,
        )
        for wire, coefficient in zip(node["inputs"], input_demands, strict=True):
            add_demand(_wire_endpoint(wire), coefficient)
    return demands


def _research_symbolic_cut_composition(
    function: Any,
    lower_completed: frozenset[int],
    upper_completed: frozenset[int],
    output_probe: Sequence[DemandExpression],
) -> SymbolicCutCompositionWitness:
    """Factor one backward field through two nested cuts of the same diagram."""

    opens = frozenset(_symbolic_causal_opens(function))
    if (
        lower_completed not in opens
        or upper_completed not in opens
        or not lower_completed <= upper_completed
    ):
        raise ValueError("symbolic cut composition requires nested causal opens")

    direct = _research_symbolic_backward_probe(function, output_probe)
    diagram = function.ir
    metadata = direct.demand_by_endpoint
    endpoint_values = _symbolic_forward_endpoint_values(function, metadata)
    all_nodes = frozenset(node["id"] for node in diagram["nodes"])
    zero = DemandExpression.constant(0)

    output_seeds = tuple(
        (_wire_endpoint(wire), coefficient)
        for wire, coefficient in zip(diagram["outputs"], output_probe, strict=True)
    )
    outer = _symbolic_reverse_segment(
        diagram,
        endpoint_values,
        all_nodes - upper_completed,
        output_seeds,
    )
    upper_frontier = _symbolic_cut_endpoints(diagram, upper_completed)
    upper_seeds = tuple(
        (endpoint, outer.get(endpoint, zero)) for endpoint in upper_frontier
    )

    middle = _symbolic_reverse_segment(
        diagram,
        endpoint_values,
        upper_completed - lower_completed,
        upper_seeds,
    )
    lower_frontier = _symbolic_cut_endpoints(diagram, lower_completed)
    lower_seeds = tuple(
        (endpoint, middle.get(endpoint, zero)) for endpoint in lower_frontier
    )

    inner = _symbolic_reverse_segment(
        diagram,
        endpoint_values,
        lower_completed,
        lower_seeds,
    )
    for endpoint, coefficient in upper_seeds:
        if middle.get(endpoint, zero) != coefficient:
            raise AssertionError("upper cut changed while seeding its middle segment")
    for endpoint, coefficient in lower_seeds:
        if inner.get(endpoint, zero) != coefficient:
            raise AssertionError("lower cut changed while seeding its inner segment")

    direct_demands = tuple(
        (record.endpoint, record.coefficient) for record in direct.demands
    )
    staged_demands = []
    for endpoint, _ in direct_demands:
        if endpoint.producer_kind == "input" or endpoint.producer_id in lower_completed:
            coefficient = inner.get(endpoint, zero)
        elif endpoint.producer_id in upper_completed:
            coefficient = middle.get(endpoint, zero)
        else:
            coefficient = outer.get(endpoint, zero)
        staged_demands.append((endpoint, coefficient))

    return SymbolicCutCompositionWitness(
        lower_completed=lower_completed,
        upper_completed=upper_completed,
        lower_cut_demands=lower_seeds,
        upper_cut_demands=upper_seeds,
        direct_demands=direct_demands,
        staged_demands=tuple(staged_demands),
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
            "adva.builtin:constant@2",
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


def test_symbolic_backward_field_recovers_every_numerical_endpoint_demand() -> None:
    parameter_cell = _functions()["parameter-cell"]
    output_probe = (DemandExpression.constant(1), DemandExpression.constant(2))
    symbolic = _research_symbolic_backward_probe(parameter_cell, output_probe)
    fixtures = (
        {"x": 2.0, "s": 3.0, "kappa": 1.0},
        {"x": -1.0, "s": 2.0, "kappa": 0.5},
        {"x": 4.0, "s": -2.0, "kappa": 3.0},
    )

    for inputs in fixtures:
        numerical = _research_backward_probe(parameter_cell, inputs, (1.0, 2.0))
        assert tuple(
            expression.evaluate(inputs) for expression in symbolic.outputs
        ) == pytest.approx(
            numerical.outputs
        )
        assert symbolic.demand_by_endpoint.keys() == numerical.demand_by_endpoint.keys()
        for endpoint, symbolic_record in symbolic.demand_by_endpoint.items():
            numerical_record = numerical.demand_by_endpoint[endpoint]
            assert symbolic_record.coefficient.evaluate(inputs) == pytest.approx(
                numerical_record.coefficient
            )
            assert symbolic_record.lineage == numerical_record.lineage
            assert symbolic_record.sources == numerical_record.sources

    root_demands = symbolic.input_demand_map
    assert root_demands["x"].input_uses() == ("kappa",)
    assert root_demands["s"].input_uses() == ()
    assert root_demands["kappa"].input_uses() == ("x",)
    assert root_demands["s"].to_lisp() == "(add (frontier 1 2))"
    assert root_demands["x"].operation_kinds() == frozenset(
        {"constant", "input", "add", "mul", "neg"}
    )
    assert root_demands["s"].operation_kinds() == frozenset({"constant", "add"})
    assert root_demands["kappa"].operation_kinds() == frozenset(
        {"constant", "input", "add", "mul", "neg"}
    )

    input_metadata = {
        record.endpoint.producer_id: (record.lineage[0], record.sources[0])
        for record in symbolic.demands
        if record.endpoint.producer_kind == "input"
    }
    assert root_demands["x"].input_audit() == (
        ("kappa", *input_metadata[2]),
    )
    assert root_demands["s"].input_audit() == ()
    assert root_demands["kappa"].input_audit() == (
        ("x", *input_metadata[0]),
    )


def test_symbolic_root_demands_recompile_as_a_fresh_checked_program() -> None:
    parameter_cell = _functions()["parameter-cell"]
    symbolic = _research_symbolic_backward_probe(
        parameter_cell,
        (DemandExpression.constant(1), DemandExpression.constant(2)),
    )
    replay = _compile_symbolic_input_demands(parameter_cell, symbolic)
    fixtures = (
        {"x": 2.0, "s": 3.0, "kappa": 1.0},
        {"x": -1.0, "s": 2.0, "kappa": 0.5},
        {"x": 4.0, "s": -2.0, "kappa": 3.0},
    )

    assert replay.validation_certificate["graph"] == "checked"
    assert replay.signature.inputs == (
        ("x", "real"),
        ("s", "real"),
        ("kappa", "real"),
    )
    assert replay.signature.outputs == ("real", "real", "real")
    assert replay.ir != parameter_cell.ir
    assert tuple(map(len, _output_source_support(replay))) == (1, 0, 1)
    assert _output_source_support(replay)[0].isdisjoint(
        _output_source_support(replay)[2]
    )

    for inputs in fixtures:
        replayed = replay.evaluate(inputs)
        expected = tuple(
            symbolic.input_demand_map[name].evaluate(inputs)
            for name in ("x", "s", "kappa")
        )
        assert replayed == pytest.approx(expected)
        assert replayed == pytest.approx(
            (1.0 - 3.0 * inputs["kappa"], 3.0, -3.0 * inputs["x"])
        )


def test_symbolic_replay_satisfies_pairing_across_inputs_and_tangents() -> None:
    parameter_cell = _functions()["parameter-cell"]
    output_probe = (1.0, 2.0)
    symbolic = _research_symbolic_backward_probe(
        parameter_cell,
        tuple(DemandExpression.constant(int(value)) for value in output_probe),
    )
    replay = _compile_symbolic_input_demands(parameter_cell, symbolic)
    fixtures = (
        {"x": 2.0, "s": 3.0, "kappa": 1.0},
        {"x": -1.0, "s": 2.0, "kappa": 0.5},
        {"x": 4.0, "s": -2.0, "kappa": 3.0},
    )
    tangent_directions = (
        {"x": 1.0, "s": 0.0, "kappa": 0.0},
        {"x": 0.0, "s": 1.0, "kappa": 0.0},
        {"x": 0.0, "s": 0.0, "kappa": 1.0},
        {"x": 2.0, "s": -1.0, "kappa": 0.5},
    )

    for inputs in fixtures:
        _, jacobian, certificate = parameter_cell.value_and_gradient(inputs)
        root_demands = dict(
            zip(("x", "s", "kappa"), replay.evaluate(inputs), strict=True)
        )
        assert certificate["diagram_integrity"] == "checked"
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
                root_demands[name] * tangent[name] for name in tangent
            )
            assert codomain_pairing == pytest.approx(domain_pairing)


def test_symbolic_backward_transport_composes_through_every_nested_cut() -> None:
    parameter_cell = _functions()["parameter-cell"]
    output_probe = (DemandExpression.constant(1), DemandExpression.constant(2))
    opens = _symbolic_causal_opens(parameter_cell)
    all_nodes = frozenset(node["id"] for node in parameter_cell.ir["nodes"])
    direct = _research_symbolic_backward_probe(parameter_cell, output_probe)
    nested_pairs = 0
    strict_three_segment_pairs = 0

    assert frozenset() in opens
    assert all_nodes in opens
    for lower_completed in opens:
        for upper_completed in opens:
            if not lower_completed <= upper_completed:
                continue
            witness = _research_symbolic_cut_composition(
                parameter_cell,
                lower_completed,
                upper_completed,
                output_probe,
            )
            nested_pairs += 1
            if lower_completed and lower_completed < upper_completed < all_nodes:
                strict_three_segment_pairs += 1

            assert witness.direct_demands == witness.staged_demands
            assert witness.direct_demands == tuple(
                (record.endpoint, record.coefficient) for record in direct.demands
            )
            assert tuple(endpoint for endpoint, _ in witness.lower_cut_demands) == (
                _symbolic_cut_endpoints(parameter_cell.ir, lower_completed)
            )
            assert tuple(endpoint for endpoint, _ in witness.upper_cut_demands) == (
                _symbolic_cut_endpoints(parameter_cell.ir, upper_completed)
            )
            for endpoint, _ in (
                *witness.lower_cut_demands,
                *witness.upper_cut_demands,
            ):
                record = direct.demand_by_endpoint[endpoint]
                assert len(record.lineage) == len(record.sources)

    assert nested_pairs > len(opens)
    assert strict_three_segment_pairs > 0


def test_focus_drift_cut_exposes_and_recomposes_expression_demands() -> None:
    parameter_cell = _functions()["parameter-cell"]
    output_probe = (DemandExpression.constant(1), DemandExpression.constant(2))
    nodes = tuple(parameter_cell.ir["nodes"])
    opens = _symbolic_causal_opens(parameter_cell)
    upper_candidates = tuple(
        completed
        for completed in opens
        if tuple(
            node["operation"]["name"]
            for node in nodes
            if node["id"] not in completed
        )
        == ("copy", "add")
    )
    root_copies = tuple(
        node
        for node in nodes
        if node["operation"]["name"] == "copy"
        and not any(
            wire["producer"]["kind"] == "node" for wire in node["inputs"]
        )
    )

    assert len(upper_candidates) == 1
    assert len(root_copies) == 1
    lower_completed = frozenset({root_copies[0]["id"]})
    upper_completed = upper_candidates[0]
    assert lower_completed < upper_completed

    witness = _research_symbolic_cut_composition(
        parameter_cell,
        lower_completed,
        upper_completed,
        output_probe,
    )
    direct = _research_symbolic_backward_probe(parameter_cell, output_probe)
    upper_terms = tuple(
        expression.to_lisp() for _, expression in witness.upper_cut_demands
    )
    assert set(upper_terms) == {"1", "(add (frontier 1 2))"}

    upper_records = tuple(
        direct.demand_by_endpoint[endpoint]
        for endpoint, _ in witness.upper_cut_demands
    )
    assert sorted(len(record.lineage) for record in upper_records) == [1, 3]
    assert sorted(len(set(record.sources)) for record in upper_records) == [1, 3]

    staged_roots = {
        name: witness.staged_demand_map[WireEndpoint("input", index, 0)]
        for index, name in enumerate(("x", "s", "kappa"))
    }
    assert staged_roots["x"].input_uses() == ("kappa",)
    assert staged_roots["s"].input_uses() == ()
    assert staged_roots["kappa"].input_uses() == ("x",)

    fixtures = (
        {"x": 2.0, "s": 3.0, "kappa": 1.0},
        {"x": -1.0, "s": 2.0, "kappa": 0.5},
        {"x": 4.0, "s": -2.0, "kappa": 3.0},
    )
    for inputs in fixtures:
        numerical = _research_backward_probe(parameter_cell, inputs, (1.0, 2.0))
        for endpoint, expression in witness.staged_demands:
            assert expression.evaluate(inputs) == pytest.approx(
                numerical.demand_by_endpoint[endpoint].coefficient
            )


def test_exponential_demand_field_matches_native_differential_and_numerical_probe() -> None:
    objective = _functions()["exp-parameter-objective"]
    output_probe = (DemandExpression.constant(1),)
    symbolic = _research_symbolic_backward_probe(objective, output_probe)
    fixtures = (
        {"x": 0.5, "s": -0.25, "kappa": 1.0},
        {"x": -1.0, "s": 0.5, "kappa": 0.5},
        {"x": 1.5, "s": -1.0, "kappa": 2.0},
    )

    assert "adva.builtin:exp@1" in symbolic.operation_rules
    assert all(
        "exp" in expression.operation_kinds()
        for expression in symbolic.input_demand_map.values()
    )
    for inputs in fixtures:
        position = (1.0 - inputs["kappa"]) * inputs["x"] + inputs["s"]
        slope = -inputs["kappa"] * inputs["x"] + inputs["s"]
        exponential = math.exp(position)
        expected_gradient = {
            "x": (1.0 - inputs["kappa"]) * exponential - inputs["kappa"],
            "s": exponential + 1.0,
            "kappa": -inputs["x"] * (exponential + 1.0),
        }
        value, gradient, certificate = objective.value_and_gradient(inputs)
        numerical = _research_backward_probe(objective, inputs, (1.0,))

        assert value == pytest.approx(exponential + slope)
        assert gradient == pytest.approx(expected_gradient)
        assert certificate["diagram_integrity"] == "checked"
        assert "adva.builtin:exp@1" in certificate["operation_rules"]
        assert numerical.input_demand_map == pytest.approx(expected_gradient)
        assert {
            name: expression.evaluate(inputs)
            for name, expression in symbolic.input_demands
        } == pytest.approx(expected_gradient)
        for endpoint, symbolic_record in symbolic.demand_by_endpoint.items():
            numerical_record = numerical.demand_by_endpoint[endpoint]
            assert symbolic_record.coefficient.evaluate(inputs) == pytest.approx(
                numerical_record.coefficient
            )
            assert symbolic_record.lineage == numerical_record.lineage
            assert symbolic_record.sources == numerical_record.sources


def test_exponential_backward_transport_composes_through_every_nested_cut() -> None:
    objective = _functions()["exp-parameter-objective"]
    output_probe = (DemandExpression.constant(1),)
    opens = _symbolic_causal_opens(objective)
    all_nodes = frozenset(node["id"] for node in objective.ir["nodes"])
    nested_pairs = 0
    strict_three_segment_pairs = 0

    for lower_completed in opens:
        for upper_completed in opens:
            if not lower_completed <= upper_completed:
                continue
            witness = _research_symbolic_cut_composition(
                objective,
                lower_completed,
                upper_completed,
                output_probe,
            )
            nested_pairs += 1
            if lower_completed and lower_completed < upper_completed < all_nodes:
                strict_three_segment_pairs += 1
            assert witness.direct_demands == witness.staged_demands

    assert nested_pairs > len(opens)
    assert strict_three_segment_pairs > 0


def test_exponential_readout_cut_has_an_expression_dependent_probe() -> None:
    objective = _functions()["exp-parameter-objective"]
    output_probe = (DemandExpression.constant(1),)
    nodes = tuple(objective.ir["nodes"])
    opens = _symbolic_causal_opens(objective)
    upper_candidates = tuple(
        completed
        for completed in opens
        if tuple(
            node["operation"]["name"]
            for node in nodes
            if node["id"] not in completed
        )
        == ("exp", "add")
    )
    root_copies = tuple(
        node
        for node in nodes
        if node["operation"]["name"] == "copy"
        and not any(
            wire["producer"]["kind"] == "node" for wire in node["inputs"]
        )
    )

    assert len(upper_candidates) == 1
    assert len(root_copies) == 1
    lower_completed = frozenset({root_copies[0]["id"]})
    upper_completed = upper_candidates[0]
    witness = _research_symbolic_cut_composition(
        objective,
        lower_completed,
        upper_completed,
        output_probe,
    )
    direct = _research_symbolic_backward_probe(objective, output_probe)
    upper_expressions = tuple(
        expression for _, expression in witness.upper_cut_demands
    )
    exponential_demands = tuple(
        expression
        for expression in upper_expressions
        if "exp" in expression.operation_kinds()
    )
    constant_demands = tuple(
        expression
        for expression in upper_expressions
        if expression.operation_kinds() == frozenset({"constant"})
    )

    assert len(exponential_demands) == 1
    assert len(constant_demands) == 1
    assert exponential_demands[0].kind == "mul"
    assert exponential_demands[0].arguments[0].to_lisp() == "1"
    assert exponential_demands[0].arguments[1].kind == "exp"
    assert set(exponential_demands[0].input_uses()) == {"x", "s", "kappa"}
    assert constant_demands[0].to_lisp() == "1"

    upper_records = tuple(
        direct.demand_by_endpoint[endpoint]
        for endpoint, _ in witness.upper_cut_demands
    )
    assert sorted(len(record.lineage) for record in upper_records) == [3, 4]
    assert sorted(len(set(record.sources)) for record in upper_records) == [3, 3]

    fixtures = (
        {"x": 0.5, "s": -0.25, "kappa": 1.0},
        {"x": -1.0, "s": 0.5, "kappa": 0.5},
        {"x": 1.5, "s": -1.0, "kappa": 2.0},
    )
    for inputs in fixtures:
        position = (1.0 - inputs["kappa"]) * inputs["x"] + inputs["s"]
        cut_values = tuple(
            expression.evaluate(inputs) for expression in upper_expressions
        )
        assert sorted(cut_values) == pytest.approx(sorted((math.exp(position), 1.0)))

        numerical = _research_backward_probe(objective, inputs, (1.0,))
        for endpoint, expression in witness.staged_demands:
            assert expression.evaluate(inputs) == pytest.approx(
                numerical.demand_by_endpoint[endpoint].coefficient
            )


def test_symbolic_probe_coefficients_recover_the_native_matrix_like_shadow() -> None:
    cell = _functions()["exp-parameter-cell"]
    probe_names = ("lambda-position", "lambda-slope")
    output_probe = tuple(DemandExpression.probe(name) for name in probe_names)
    symbolic = _research_symbolic_backward_probe(cell, output_probe)
    root_forms = {
        name: _probe_linear_form(expression)
        for name, expression in symbolic.input_demands
    }
    fixtures = (
        {"x": 0.5, "s": -0.25, "kappa": 1.0},
        {"x": -1.0, "s": 0.5, "kappa": 0.5},
        {"x": 1.5, "s": -1.0, "kappa": 2.0},
    )

    for form in root_forms.values():
        assert form.constant is None
        assert set(form.coefficient_map) == set(probe_names)
        assert all(
            not coefficient.probe_uses()
            for coefficient in form.coefficient_map.values()
        )
        assert "exp" in form.coefficient_map[probe_names[0]].operation_kinds()
        assert "exp" not in form.coefficient_map[probe_names[1]].operation_kinds()

    probe_values = {"lambda-position": 2.0, "lambda-slope": -0.5}
    for inputs in fixtures:
        values, jacobian, certificate = cell.value_and_gradient(inputs)
        position = (1.0 - inputs["kappa"]) * inputs["x"] + inputs["s"]
        slope = -inputs["kappa"] * inputs["x"] + inputs["s"]
        assert values == pytest.approx((math.exp(position), slope))
        assert certificate["diagram_integrity"] == "checked"

        for input_name, form in root_forms.items():
            for output_index, probe_name in enumerate(probe_names):
                coefficient = form.coefficient_map[probe_name]
                assert coefficient.evaluate(inputs) == pytest.approx(
                    jacobian[output_index][input_name]
                )
            expected_demand = sum(
                jacobian[output_index][input_name] * probe_values[probe_name]
                for output_index, probe_name in enumerate(probe_names)
            )
            assert symbolic.input_demand_map[input_name].evaluate(
                inputs,
                probe_values,
            ) == pytest.approx(expected_demand)


def test_symbolic_probe_transport_is_linear_at_every_checked_endpoint() -> None:
    cell = _functions()["exp-parameter-cell"]
    probe_names = ("lambda-position", "lambda-slope")
    symbolic = _research_symbolic_backward_probe(
        cell,
        tuple(DemandExpression.probe(name) for name in probe_names),
    )
    inputs = {"x": -1.0, "s": 0.5, "kappa": 0.5}
    left = {"lambda-position": 1.25, "lambda-slope": -0.75}
    right = {"lambda-position": -0.5, "lambda-slope": 2.0}
    added = {name: left[name] + right[name] for name in probe_names}
    scale = -1.5
    scaled = {name: scale * left[name] for name in probe_names}
    zero = {name: 0.0 for name in probe_names}

    for record in symbolic.demands:
        expression = record.coefficient
        form = _probe_linear_form(expression)
        assert form.constant is None
        assert set(form.coefficient_map) <= set(probe_names)
        assert expression.evaluate(inputs, zero) == pytest.approx(0.0)
        assert expression.evaluate(inputs, added) == pytest.approx(
            expression.evaluate(inputs, left)
            + expression.evaluate(inputs, right)
        )
        assert expression.evaluate(inputs, scaled) == pytest.approx(
            scale * expression.evaluate(inputs, left)
        )
        assert expression.evaluate(inputs, left) == pytest.approx(
            sum(
                coefficient.evaluate(inputs) * left[name]
                for name, coefficient in form.coefficients
            )
        )


def test_symbolic_probe_cut_transport_composes_over_all_nested_causal_opens() -> None:
    cell = _functions()["exp-parameter-cell"]
    output_probe = (
        DemandExpression.probe("lambda-position"),
        DemandExpression.probe("lambda-slope"),
    )
    opens = _symbolic_causal_opens(cell)
    nested_pairs = 0

    for lower_completed in opens:
        for upper_completed in opens:
            if not lower_completed <= upper_completed:
                continue
            witness = _research_symbolic_cut_composition(
                cell,
                lower_completed,
                upper_completed,
                output_probe,
            )
            nested_pairs += 1
            assert witness.direct_demands == witness.staged_demands
            for _, expression in (
                *witness.lower_cut_demands,
                *witness.upper_cut_demands,
            ):
                assert _probe_linear_form(expression).constant is None

    assert nested_pairs > len(opens)


def test_optical_cut_lifts_probe_basis_to_exp_polynomial_coefficients() -> None:
    cell = _functions()["exp-parameter-cell"]
    probe_names = ("lambda-position", "lambda-slope")
    output_probe = tuple(DemandExpression.probe(name) for name in probe_names)
    nodes = tuple(cell.ir["nodes"])
    upper_candidates = tuple(
        completed
        for completed in _symbolic_causal_opens(cell)
        if tuple(
            node["operation"]["name"]
            for node in nodes
            if node["id"] not in completed
        )
        == ("exp",)
    )

    assert len(upper_candidates) == 1
    witness = _research_symbolic_cut_composition(
        cell,
        frozenset(),
        upper_candidates[0],
        output_probe,
    )
    cut_forms = tuple(
        _probe_linear_form(expression)
        for _, expression in witness.upper_cut_demands
    )
    position_forms = tuple(
        form for form in cut_forms if "lambda-position" in form.coefficient_map
    )
    slope_forms = tuple(
        form for form in cut_forms if "lambda-slope" in form.coefficient_map
    )

    assert len(position_forms) == 1
    assert len(slope_forms) == 1
    assert set(position_forms[0].coefficient_map) == {"lambda-position"}
    assert set(slope_forms[0].coefficient_map) == {"lambda-slope"}
    position_coefficient = position_forms[0].coefficient_map["lambda-position"]
    slope_coefficient = slope_forms[0].coefficient_map["lambda-slope"]
    assert "exp" in position_coefficient.operation_kinds()
    assert not position_coefficient.probe_uses()
    assert slope_coefficient.to_lisp() == "1"

    direct = _research_symbolic_backward_probe(cell, output_probe)
    cut_records = tuple(
        direct.demand_by_endpoint[endpoint]
        for endpoint, _ in witness.upper_cut_demands
    )
    assert sorted(len(record.lineage) for record in cut_records) == [3, 4]
    assert sorted(len(set(record.sources)) for record in cut_records) == [3, 3]
