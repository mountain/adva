"""Ergonomic adapters over opaque, checked Rust programs.

This module may realize or translate an already checked diagram. It never
allocates semantic source or occurrence identities.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import json
from numbers import Real
from typing import TYPE_CHECKING, Any

from ._native import Program as _NativeProgram
from ._native import Workspace as _NativeWorkspace
from ._native import compile_module as _compile_module
from ._native import link_modules as _link_modules
from ._native import load_program_json as _load_program_json

if TYPE_CHECKING:
    import numpy as np


@dataclass(frozen=True, slots=True)
class TypedFrontier:
    """Orientation-free ordered port types checked by Rust."""

    types: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DomainFrontier:
    """Named input orientation of a typed frontier."""

    ports: tuple[tuple[str, str], ...]

    @property
    def typed(self) -> TypedFrontier:
        return TypedFrontier(tuple(value_type for _, value_type in self.ports))

    @property
    def input_names(self) -> tuple[str, ...]:
        return tuple(name for name, _ in self.ports)


@dataclass(frozen=True, slots=True)
class CodomainFrontier:
    """Output orientation of a typed frontier."""

    typed: TypedFrontier


@dataclass(frozen=True, slots=True)
class FunctionSignature:
    """Python view of the Rust-checked domain and codomain frontiers."""

    domain: DomainFrontier
    codomain: CodomainFrontier

    @property
    def inputs(self) -> tuple[tuple[str, str], ...]:
        return self.domain.ports

    @property
    def outputs(self) -> tuple[str, ...]:
        return self.codomain.typed.types

    @property
    def input_names(self) -> tuple[str, ...]:
        return self.domain.input_names


@dataclass(frozen=True, slots=True)
class Evaluation:
    """A realized value paired with the Rust evaluation certificate."""

    values: tuple[float, ...]
    certificate: Mapping[str, Any]

    @property
    def scalar(self) -> float:
        if len(self.values) != 1:
            raise TypeError(f"expected one output, got {len(self.values)}")
        return self.values[0]


@dataclass(frozen=True, slots=True)
class CausalCutAnalysis:
    """A Rust-certified completed past and its occurrence-decorated frontier."""

    completed: tuple[int, ...]
    frontier: tuple[Mapping[str, Any], ...]
    certificate: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class CausalStepAnalysis:
    """One certified operation crossing between two causal cuts."""

    event: int
    before: Mapping[str, Any]
    after: Mapping[str, Any]
    consumed: tuple[Mapping[str, Any], ...]
    produced: tuple[Mapping[str, Any], ...]
    certificate: Mapping[str, Any]


class Workspace:
    """A finite, acyclic set of modules linked and checked in Rust."""

    __slots__ = ("_native",)

    def __init__(self, native: _NativeWorkspace) -> None:
        self._native = native

    @property
    def module_names(self) -> tuple[str, ...]:
        return tuple(self._native.module_names())

    def function(self, module: str, function: str) -> KernelFunction:
        return KernelFunction(self._native.function(module, function))


class KernelFunction:
    """Typed facade for one immutable `SharedProgramDiagram`."""

    __slots__ = ("_native", "_signature")

    def __init__(self, native: _NativeProgram) -> None:
        self._native = native
        raw = json.loads(native.signature_json())
        self._signature = FunctionSignature(
            domain=DomainFrontier(
                tuple((item["name"], item["value_type"]) for item in raw["inputs"])
            ),
            codomain=CodomainFrontier(TypedFrontier(tuple(raw["outputs"]))),
        )

    @property
    def qualified_name(self) -> str:
        return self._native.qualified_name

    @property
    def signature(self) -> FunctionSignature:
        return self._signature

    @property
    def ir(self) -> Mapping[str, Any]:
        return json.loads(self._native.ir_json())

    @property
    def compilation_certificate(self) -> Mapping[str, Any] | None:
        encoded = self._native.compilation_certificate_json()
        return None if encoded is None else json.loads(encoded)

    @property
    def validation_certificate(self) -> Mapping[str, Any]:
        return json.loads(self._native.validation_certificate_json())

    @property
    def history(self) -> Mapping[str, Any]:
        return json.loads(self._native.history_json())

    @property
    def source_partition(self) -> Mapping[str, tuple[str, ...]]:
        raw = json.loads(self._native.source_partition_json())
        return {source: tuple(occurrences) for source, occurrences in raw.items()}

    def causal_cut(self, completed: Sequence[int]) -> CausalCutAnalysis:
        """Read a spatial cut from a completed causal past without evaluation."""

        checked = self._check_node_ids(completed)
        result_json, certificate_json = self._native.causal_cut(checked)
        result = json.loads(result_json)
        return CausalCutAnalysis(
            completed=tuple(result["completed"]),
            frontier=tuple(result["frontier"]),
            certificate=json.loads(certificate_json),
        )

    def advance_causal_cut(
        self, completed: Sequence[int], event: int
    ) -> CausalStepAnalysis:
        """Move one enabled event across a causal cut."""

        checked = self._check_node_ids(completed)
        if isinstance(event, bool) or not isinstance(event, int) or event < 0:
            raise TypeError("event must be a non-negative node id")
        result_json, certificate_json = self._native.advance_causal_cut(
            checked, event
        )
        result = json.loads(result_json)
        return CausalStepAnalysis(
            event=result["event"],
            before=result["before"],
            after=result["after"],
            consumed=tuple(result["consumed"]),
            produced=tuple(result["produced"]),
            certificate=json.loads(certificate_json),
        )

    def evaluate_checked(self, inputs: Mapping[str, Real]) -> Evaluation:
        checked = self._check_inputs(inputs)
        values, certificate = self._native.evaluate(checked)
        return Evaluation(tuple(values), json.loads(certificate))

    def evaluate(self, inputs: Mapping[str, Real]) -> float | tuple[float, ...]:
        result = self.evaluate_checked(inputs)
        return result.scalar if len(result.values) == 1 else result.values

    def value_and_gradient(
        self, inputs: Mapping[str, Real]
    ) -> tuple[
        float | tuple[float, ...],
        Mapping[str, float] | tuple[Mapping[str, float], ...],
        Mapping[str, Any],
    ]:
        checked = self._check_inputs(inputs)
        values, jacobian, certificate = self._native.value_and_gradient(checked)
        value_view: float | tuple[float, ...]
        gradient_view: Mapping[str, float] | tuple[Mapping[str, float], ...]
        if len(values) == 1:
            value_view = values[0]
            gradient_view = jacobian[0]
        else:
            value_view = tuple(values)
            gradient_view = tuple(jacobian)
        return value_view, gradient_view, json.loads(certificate)

    def to_sympy(self) -> Any:
        """Translate checked IR to SymPy without changing native identities."""

        try:
            import sympy
        except ImportError as error:  # pragma: no cover - depends on optional install
            raise ImportError("install adva[scientific] for SymPy integration") from error

        document = self.ir
        inputs = {
            index: sympy.Symbol(port["name"], real=True)
            for index, port in enumerate(document["signature"]["inputs"])
        }
        nodes: dict[int, tuple[Any, ...]] = {}

        def wire_value(wire: Mapping[str, Any]) -> Any:
            producer = wire["producer"]
            if producer["kind"] == "input":
                return inputs[producer["index"]]
            return nodes[producer["node"]][wire["output_index"]]

        for node in document["nodes"]:
            name = node["operation"]["name"]
            arguments = tuple(wire_value(wire) for wire in node["inputs"])
            parameters = node["operation"].get("parameters", {})
            if name == "constant":
                rational = parameters["value"]
                outputs = (sympy.Rational(rational["numerator"], rational["denominator"]),)
            elif name == "id":
                outputs = (arguments[0],)
            elif name == "copy":
                outputs = (arguments[0], arguments[0])
            elif name == "discard":
                outputs = ()
            elif name == "swap":
                outputs = (arguments[1], arguments[0])
            elif name == "add":
                outputs = (arguments[0] + arguments[1],)
            elif name in {"mul", "scale"}:
                outputs = (arguments[0] * arguments[1],)
            elif name == "neg":
                outputs = (-arguments[0],)
            elif name == "sin":
                outputs = (sympy.sin(arguments[0]),)
            elif name == "cos":
                outputs = (sympy.cos(arguments[0]),)
            elif name == "exp":
                outputs = (sympy.exp(arguments[0]),)
            elif name == "log":
                outputs = (sympy.log(arguments[0]),)
            else:  # pragma: no cover - Rust registry rejects this first
                raise TypeError(f"no SymPy adapter for checked operation {name!r}")
            nodes[node["id"]] = outputs

        results = tuple(wire_value(wire) for wire in document["outputs"])
        return results[0] if len(results) == 1 else results

    def numpy_callable(self) -> Callable[..., Any]:
        """Return a NumPy-compatible callable ordered by the typed input frontier."""

        try:
            import sympy
        except ImportError as error:  # pragma: no cover
            raise ImportError("install adva[scientific] for NumPy integration") from error
        symbols = [sympy.Symbol(name, real=True) for name in self.signature.input_names]
        return sympy.lambdify(symbols, self.to_sympy(), modules="numpy")

    def scipy_objective(self, input_order: Sequence[str] | None = None) -> ScipyObjective:
        """Expose one-output value and Jacobian callables for `scipy.optimize`."""

        return ScipyObjective(self, input_order or self.signature.input_names)

    def _check_inputs(self, inputs: Mapping[str, Real]) -> dict[str, float]:
        expected = set(self.signature.input_names)
        actual = set(inputs)
        if actual != expected:
            raise TypeError(f"expected inputs {sorted(expected)}, got {sorted(actual)}")
        checked: dict[str, float] = {}
        for name in self.signature.input_names:
            value = inputs[name]
            if isinstance(value, bool) or not isinstance(value, Real):
                raise TypeError(f"input {name!r} must be a real scalar, got {type(value).__name__}")
            checked[name] = float(value)
        return checked

    @staticmethod
    def _check_node_ids(nodes: Sequence[int]) -> list[int]:
        checked: list[int] = []
        for node in nodes:
            if isinstance(node, bool) or not isinstance(node, int) or node < 0:
                raise TypeError("completed nodes must be non-negative node ids")
            checked.append(node)
        return checked


class ScipyObjective:
    """Typed SciPy objective whose values and Jacobian come from Rust."""

    __slots__ = ("function", "input_order")

    def __init__(self, function: KernelFunction, input_order: Sequence[str]) -> None:
        order = tuple(input_order)
        if set(order) != set(function.signature.input_names) or len(order) != len(set(order)):
            raise TypeError("input_order must contain each typed input exactly once")
        if len(function.signature.outputs) != 1:
            raise TypeError("SciPy objectives require exactly one output")
        self.function = function
        self.input_order = order

    def fun(self, vector: Sequence[Real]) -> float:
        inputs = self._inputs(vector)
        result = self.function.evaluate(inputs)
        if not isinstance(result, float):  # pragma: no cover - guarded in constructor
            raise TypeError("SciPy objective did not produce a scalar")
        return result

    def jac(self, vector: Sequence[Real]) -> np.ndarray[Any, Any]:
        try:
            import numpy as np
        except ImportError as error:  # pragma: no cover
            raise ImportError("install adva[scientific] for SciPy integration") from error
        inputs = self._inputs(vector)
        _, gradient, _ = self.function.value_and_gradient(inputs)
        if not isinstance(gradient, Mapping):  # pragma: no cover
            raise TypeError("SciPy objective did not produce one gradient")
        return np.asarray([gradient[name] for name in self.input_order], dtype=float)

    def _inputs(self, vector: Sequence[Real]) -> dict[str, float]:
        if len(vector) != len(self.input_order):
            raise TypeError(f"expected vector length {len(self.input_order)}, got {len(vector)}")
        return {name: float(value) for name, value in zip(self.input_order, vector, strict=True)}


def compile_module(source: str) -> Workspace:
    return Workspace(_compile_module(source))


def link_modules(sources: Sequence[str]) -> Workspace:
    return Workspace(_link_modules(list(sources)))


def load_program(document: str | Mapping[str, Any]) -> KernelFunction:
    """Import only a diagram accepted by the Rust semantic validator."""

    source = document if isinstance(document, str) else json.dumps(document)
    return KernelFunction(_load_program_json(source))
