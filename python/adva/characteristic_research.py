"""Bounded distributivity learning/proof calibration over checked programs.

This module is a nonauthoritative research companion.  Rust remains the sole
owner of program identities, diagrams, occurrences, cuts, slices, triadic
observer transitions, and certificates.  Python derives one exact rational
polynomial presentation from each checked core and always retains the complete
process residual.  Equality of polynomial features never identifies programs
or creates an equation cell.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from itertools import product
from typing import Any, ClassVar

from .core import (
    GraftTraceView,
    KernelFunction,
    ProgramSliceView,
    TriadicDomainV0,
    TriadicObserverPolicyV0,
    TriadicObserverTransitionViewV0,
    link_modules,
)
from .research import ExperimentVerdictV0, LayerOutcomeV0


class CharacteristicDirectionV0(StrEnum):
    """Two readouts of the same bounded polynomial characteristic kernel."""

    LEARN = "learn"
    PROVE = "prove"


class CharacteristicResultKindV0(StrEnum):
    """Task outcomes kept distinct from stable logical judgments."""

    PROVED = "proved"
    REFUTED = "refuted"
    OBSERVATIONALLY_EQUAL = "observationally_equal"
    NOT_REPRESENTABLE = "not_representable"
    FUEL_EXHAUSTED = "fuel_exhausted"


class CharacteristicLayerV0(StrEnum):
    """The common validation protocol specialized to this finite task."""

    TYPE = "type"
    IDENTITY = "identity"
    PRESENTATION_CORRESPONDENCE = "presentation_correspondence"
    LOCAL_COMPOSITION = "local_composition"
    RESIDUAL = "residual"
    CHARACTERISTIC = "characteristic"
    DUAL_READOUT = "dual_readout"
    PROMOTION_BOUNDARY = "promotion_boundary"


@dataclass(frozen=True, slots=True)
class CharacteristicValidationRecordV0:
    """One Python research gate outcome; never a Rust certificate."""

    layer: CharacteristicLayerV0
    outcome: LayerOutcomeV0
    reason: str


@dataclass(frozen=True, slots=True)
class DistributivityTaskRequestV0:
    """A finite comparison request over two Rust-checked scalar programs."""

    sources: tuple[str, ...]
    module: str
    left_function: str
    right_function: str
    direction: CharacteristicDirectionV0
    input_domains: tuple[TriadicDomainV0, ...] = (
        TriadicDomainV0.CONSTRUCTION,
        TriadicDomainV0.SPACE,
        TriadicDomainV0.TIME,
    )
    variables: tuple[str, ...] = ("a", "x", "y")
    max_degree: int = 2
    fuel: int | None = None
    retain_residual: bool = True

    def __post_init__(self) -> None:
        if not self.sources or any(not isinstance(source, str) for source in self.sources):
            raise ValueError("a distributivity task requires Lisp source strings")
        if not self.module or not self.left_function or not self.right_function:
            raise ValueError("the module and both function names must be nonempty")
        if not isinstance(self.direction, CharacteristicDirectionV0):
            raise ValueError("direction must be a CharacteristicDirectionV0 value")
        TriadicObserverPolicyV0(self.input_domains)
        if self.variables != ("a", "x", "y"):
            raise ValueError("V0 calibrates exactly the ordered variables a, x, y")
        if (
            isinstance(self.max_degree, bool)
            or not isinstance(self.max_degree, int)
            or self.max_degree < 0
        ):
            raise ValueError("max_degree must be a non-negative integer")
        if self.fuel is not None and (
            isinstance(self.fuel, bool)
            or not isinstance(self.fuel, int)
            or self.fuel < 0
        ):
            raise ValueError("fuel must be a non-negative integer or None")

    @property
    def policy(self) -> TriadicObserverPolicyV0:
        return TriadicObserverPolicyV0(self.input_domains)


@dataclass(frozen=True, slots=True)
class RationalMonomialV0:
    """One exact term in the declared ordered variable basis."""

    exponents: tuple[int, ...]
    numerator: int
    denominator: int

    @property
    def coefficient(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)


@dataclass(frozen=True, slots=True)
class PolynomialCharacteristicV0:
    """Canonical exact feature in Q[a,x,y] for the bounded fragment."""

    variables: tuple[str, ...]
    terms: tuple[RationalMonomialV0, ...]
    total_degree: int
    feature_policy: str = "expanded-rational-polynomial-v0"

    def evaluate(self, assignment: Mapping[str, int | Fraction]) -> Fraction:
        if set(assignment) != set(self.variables):
            raise ValueError("an exact characteristic assignment must cover a, x, and y")
        total = Fraction(0)
        for term in self.terms:
            value = term.coefficient
            for name, exponent in zip(self.variables, term.exponents, strict=True):
                value *= Fraction(assignment[name]) ** exponent
            total += value
        return total


@dataclass(frozen=True, slots=True)
class BoundaryPresentationV0:
    """The fixed triadic boundary read from one exact observer transition."""

    public_form: str
    policy: TriadicObserverPolicyV0
    transition: TriadicObserverTransitionViewV0
    certificate: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class ThroughPresentationV0:
    """Three relation-valued opposite-pair transition presentations."""

    forms: tuple[Mapping[str, Any], ...]
    exact_lineage_links: tuple[Mapping[str, Any], ...]
    relational_converse_authorized: bool = True
    inverse_execution_authorized: bool = False


@dataclass(frozen=True, slots=True)
class MultiHolePresentationV0:
    """The checked call-hole presentation and complete canonical slice."""

    graft: GraftTraceView
    carrier: ProgramSliceView
    composition_middle: tuple[int, ...]
    composition_certificate: Mapping[str, Any]
    observer_composition_certificate: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class CorrespondenceEvidenceV0:
    """Evidence that all presentations read one unchanged checked core."""

    exact_slice_shared: bool
    original_ids_checked: bool
    lineage_checked: bool
    graft_checked: bool
    slice_composition_checked: bool
    observer_composition_checked: bool
    characteristic_is_projection: bool = True
    semantic_authority: bool = False


@dataclass(frozen=True, slots=True)
class ProcessResidualV0:
    """All process distinctions hidden from the polynomial feature."""

    event_ids: tuple[int, ...]
    operation_names: tuple[str, ...]
    occurrence_ids: tuple[str, ...]
    event_history: tuple[Mapping[str, Any], ...]
    graft_frame_ids: tuple[str, ...]
    retained: bool = True


@dataclass(frozen=True, slots=True)
class ProgramAtlasV0:
    """One checked core with three presentations, correspondence, and residual."""

    qualified_name: str
    core_ir: Mapping[str, Any]
    validation_certificate: Mapping[str, Any]
    compilation_certificate: Mapping[str, Any]
    boundary: BoundaryPresentationV0
    through: ThroughPresentationV0
    multi_hole: MultiHolePresentationV0
    characteristic: PolynomialCharacteristicV0
    correspondence: CorrespondenceEvidenceV0
    residual: ProcessResidualV0


@dataclass(frozen=True, slots=True)
class TaskRelativeForgetEvidenceV0:
    """A scoped projection permission, never permission to erase the residual."""

    policy: str
    hidden_from_feature: tuple[str, ...]
    left_residual_event_ids: tuple[int, ...]
    right_residual_event_ids: tuple[int, ...]
    feature_comparison_authorized: bool
    program_identification_authorized: bool = False
    equation_cell_authorized: bool = False
    provenance_erasure_authorized: bool = False
    semantic_authority: bool = False


@dataclass(frozen=True, slots=True)
class DistributivityWitnessV0:
    """A finite polynomial-identity witness, not a program equation cell."""

    rule: str
    substitution: tuple[tuple[str, str], ...]
    common_characteristic: PolynomialCharacteristicV0
    left_operation_profile: tuple[tuple[str, int], ...]
    right_operation_profile: tuple[tuple[str, int], ...]
    exact_polynomial_identity: bool
    residuals_retained: bool
    equation_cell_authorized: bool = False
    program_identity_authorized: bool = False
    semantic_authority: bool = False


@dataclass(frozen=True, slots=True)
class PolynomialCounterexampleV0:
    """One exact rational valuation separating two polynomial features."""

    assignment: tuple[tuple[str, int], ...]
    left_value: Fraction
    right_value: Fraction


@dataclass(frozen=True, slots=True)
class CharacteristicTaskArtifactV0:
    """The complete bounded result of one learning/proof dual-read request."""

    request: DistributivityTaskRequestV0
    kind: CharacteristicResultKindV0
    verdict: ExperimentVerdictV0
    reason: str
    validation: tuple[CharacteristicValidationRecordV0, ...]
    checked_core_names: tuple[str, ...]
    left: ProgramAtlasV0 | None = None
    right: ProgramAtlasV0 | None = None
    common_characteristic: PolynomialCharacteristicV0 | None = None
    forget_evidence: TaskRelativeForgetEvidenceV0 | None = None
    proof_witness: DistributivityWitnessV0 | None = None
    counterexample: PolynomialCounterexampleV0 | None = None
    remaining_fuel_cost: int = 0
    learning_proof_self_duality_authorized: bool = False
    program_equivalence_authorized: bool = False
    semantic_authority: bool = False


class _NotRepresentable(ValueError):
    pass


class DistributivityCharacteristicMachineV0:
    """Run the bounded exact characteristic kernel in learning or proof mode."""

    _LAYERS: ClassVar[tuple[CharacteristicLayerV0, ...]] = tuple(
        CharacteristicLayerV0
    )
    _ALLOWED_OPERATIONS: ClassVar[frozenset[str]] = frozenset(
        {"add", "mul", "copy", "discard", "constant", "id"}
    )

    def run(self, request: DistributivityTaskRequestV0) -> CharacteristicTaskArtifactV0:
        validation: list[CharacteristicValidationRecordV0] = []
        try:
            workspace = link_modules(request.sources)
            left_function = workspace.function(request.module, request.left_function)
            right_function = workspace.function(request.module, request.right_function)
            self._check_type(left_function, request)
            self._check_type(right_function, request)
        except (TypeError, ValueError) as error:
            return self._finish(
                request,
                CharacteristicResultKindV0.NOT_REPRESENTABLE,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                f"Rust or the V0 task boundary rejected the program pair: {error}",
                validation,
                CharacteristicLayerV0.TYPE,
            )
        checked_names = (left_function.qualified_name, right_function.qualified_name)
        validation.append(
            self._satisfied(
                CharacteristicLayerV0.TYPE,
                "both Rust-checked cores have the ordered Real boundary (a,x,y)->Real",
            )
        )

        left_cost = len(left_function.ir["nodes"])
        right_cost = len(right_function.ir["nodes"])
        total_cost = left_cost + right_cost
        if request.fuel is not None and request.fuel < total_cost:
            return self._finish(
                request,
                CharacteristicResultKindV0.FUEL_EXHAUSTED,
                ExperimentVerdictV0.FUEL_EXHAUSTED,
                "fuel ended before both checked cores could be characterized",
                validation,
                CharacteristicLayerV0.IDENTITY,
                checked_core_names=checked_names,
                remaining_fuel_cost=total_cost - request.fuel,
            )

        if not request.retain_residual:
            return self._finish(
                request,
                CharacteristicResultKindV0.NOT_REPRESENTABLE,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                "the polynomial projection is unavailable without complete process residuals",
                validation,
                CharacteristicLayerV0.RESIDUAL,
                checked_core_names=checked_names,
            )

        validation.append(
            self._satisfied(
                CharacteristicLayerV0.IDENTITY,
                "the two qualified cores remain distinct identities across comparison",
            )
        )
        try:
            left = self._atlas(left_function, request)
            right = self._atlas(right_function, request)
        except _NotRepresentable as error:
            return self._finish(
                request,
                CharacteristicResultKindV0.NOT_REPRESENTABLE,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                str(error),
                validation,
                CharacteristicLayerV0.PRESENTATION_CORRESPONDENCE,
                checked_core_names=checked_names,
            )
        except (TypeError, ValueError) as error:
            return self._finish(
                request,
                CharacteristicResultKindV0.NOT_REPRESENTABLE,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                f"the checked core lacks one required V0 presentation: {error}",
                validation,
                CharacteristicLayerV0.PRESENTATION_CORRESPONDENCE,
                checked_core_names=checked_names,
            )

        if left.core_ir == right.core_ir or left.qualified_name == right.qualified_name:
            return self._finish(
                request,
                CharacteristicResultKindV0.NOT_REPRESENTABLE,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                "V0 requires two distinct checked programs, not one duplicated core",
                validation,
                CharacteristicLayerV0.IDENTITY,
                checked_core_names=checked_names,
                left=left,
                right=right,
            )
        validation.extend(
            (
                self._satisfied(
                    CharacteristicLayerV0.PRESENTATION_CORRESPONDENCE,
                    "each core supplies one boundary, through, multi-hole, "
                    "feature, and residual atlas",
                ),
                self._satisfied(
                    CharacteristicLayerV0.LOCAL_COMPOSITION,
                    "Rust exact slice and triadic observer composition agree "
                    "with each direct outer view",
                ),
                self._satisfied(
                    CharacteristicLayerV0.RESIDUAL,
                    "both complete event, occurrence, history, and graft residuals remain attached",
                ),
                self._satisfied(
                    CharacteristicLayerV0.CHARACTERISTIC,
                    "the same exact Q[a,x,y] characteristic kernel analyzed both cores",
                ),
            )
        )

        forget = TaskRelativeForgetEvidenceV0(
            policy=left.characteristic.feature_policy,
            hidden_from_feature=(
                "NodeId",
                "OccurrenceId",
                "OccurrencePath",
                "copy/discard ledger",
                "event history",
                "graft frames",
            ),
            left_residual_event_ids=left.residual.event_ids,
            right_residual_event_ids=right.residual.event_ids,
            feature_comparison_authorized=True,
        )

        if left.characteristic != right.characteristic:
            counterexample = self._counterexample(
                left.characteristic,
                right.characteristic,
                request.max_degree,
            )
            if counterexample is None:
                return self._finish(
                    request,
                    CharacteristicResultKindV0.NOT_REPRESENTABLE,
                    ExperimentVerdictV0.NOT_REPRESENTABLE,
                    "unequal features had no witness inside the declared finite separation grid",
                    validation,
                    CharacteristicLayerV0.DUAL_READOUT,
                    checked_core_names=checked_names,
                    left=left,
                    right=right,
                    forget_evidence=forget,
                )
            validation.append(
                self._satisfied(
                    CharacteristicLayerV0.DUAL_READOUT,
                    "the common kernel produced an exact finite counterexample "
                    "rather than a false proof",
                )
            )
            return self._success_boundary(
                request,
                CharacteristicResultKindV0.REFUTED,
                ExperimentVerdictV0.COUNTEREXAMPLE,
                "the two checked programs have different exact polynomial characteristics",
                validation,
                checked_names,
                left,
                right,
                forget,
                counterexample=counterexample,
            )

        common = left.characteristic
        if request.direction is CharacteristicDirectionV0.LEARN:
            validation.append(
                self._satisfied(
                    CharacteristicLayerV0.DUAL_READOUT,
                    "learning extracted one common feature while retaining "
                    "two unequal process residuals",
                )
            )
            return self._success_boundary(
                request,
                CharacteristicResultKindV0.OBSERVATIONALLY_EQUAL,
                ExperimentVerdictV0.SUPPORTED,
                "the checked cores share one task feature but remain different programs",
                validation,
                checked_names,
                left,
                right,
                forget,
                common_characteristic=common,
            )

        witness = self._distributivity_witness(left, right, common)
        if witness is None:
            validation.append(
                self._satisfied(
                    CharacteristicLayerV0.DUAL_READOUT,
                    "feature equality was retained without fabricating a distributivity witness",
                )
            )
            return self._success_boundary(
                request,
                CharacteristicResultKindV0.OBSERVATIONALLY_EQUAL,
                ExperimentVerdictV0.SUPPORTED,
                "the features agree, but the requested distributivity shapes "
                "were not both witnessed",
                validation,
                checked_names,
                left,
                right,
                forget,
                common_characteristic=common,
            )
        validation.append(
            self._satisfied(
                CharacteristicLayerV0.DUAL_READOUT,
                "proof readout reconstructed one bounded distributivity witness "
                "from the shared feature",
            )
        )
        return self._success_boundary(
            request,
            CharacteristicResultKindV0.PROVED,
            ExperimentVerdictV0.SUPPORTED,
            "exact polynomial normalization supports the declared distributivity witness",
            validation,
            checked_names,
            left,
            right,
            forget,
            common_characteristic=common,
            proof_witness=witness,
        )

    def _atlas(
        self,
        function: KernelFunction,
        request: DistributivityTaskRequestV0,
    ) -> ProgramAtlasV0:
        ir = function.ir
        node_ids = tuple(int(node["id"]) for node in ir["nodes"])
        operations = tuple(str(node["operation"]["name"]) for node in ir["nodes"])
        unsupported = sorted(set(operations) - self._ALLOWED_OPERATIONS)
        if unsupported:
            raise _NotRepresentable(
                f"the exact polynomial V0 does not represent operations {unsupported}"
            )
        if not node_ids:
            raise _NotRepresentable("the V0 characteristic task requires a nonempty process")
        direct_slice = function.program_slice([], node_ids)
        direct_observer = function.triadic_observer_transition_v0(
            request.policy, [], node_ids
        )
        if direct_observer.result.slice != direct_slice.result:
            raise ValueError("the triadic boundary and polynomial core lost their common slice")
        graft = function.graft_trace
        if graft is None:
            raise _NotRepresentable("the multi-hole presentation requires compiler graft evidence")
        middle = self._middle(function, node_ids)
        slice_composition = function.compose_program_slices([], middle, node_ids)
        observer_composition = function.compose_triadic_observer_transitions_v0(
            request.policy, [], middle, node_ids
        )
        if slice_composition.result != direct_slice.result:
            raise ValueError("adjacent ProgramSlice composition disagrees with the direct carrier")
        if observer_composition.result != direct_observer.result:
            raise ValueError("adjacent triadic composition disagrees with the direct presentation")
        feature = self._feature(function, request.variables, request.max_degree)
        slice_certificate = direct_slice.certificate
        correspondence = CorrespondenceEvidenceV0(
            exact_slice_shared=True,
            original_ids_checked=slice_certificate.get("original_id_preservation") == "checked",
            lineage_checked=slice_certificate.get("lineage_preservation") == "checked",
            graft_checked=slice_certificate.get("graft_frame_consistency") == "checked",
            slice_composition_checked=(
                slice_composition.certificate.get("exact_composition") == "checked"
            ),
            observer_composition_checked=(
                observer_composition.certificate.get("exact_composition") == "checked"
                and observer_composition.certificate.get("lineage_relation_composition")
                == "checked"
            ),
        )
        if not all(
            (
                correspondence.exact_slice_shared,
                correspondence.original_ids_checked,
                correspondence.lineage_checked,
                correspondence.graft_checked,
                correspondence.slice_composition_checked,
                correspondence.observer_composition_checked,
            )
        ):
            raise ValueError("one Rust correspondence or composition certificate is absent")
        compilation = function.compilation_certificate
        if compilation is None:
            raise _NotRepresentable("imported diagrams without compilation evidence are excluded")
        occurrence_ids = tuple(
            sorted(str(item["id"]) for item in ir.get("occurrences", ()))
        )
        residual = ProcessResidualV0(
            event_ids=node_ids,
            operation_names=operations,
            occurrence_ids=occurrence_ids,
            event_history=direct_slice.result.event_history,
            graft_frame_ids=tuple(str(frame["id"]) for frame in graft.result.frames),
        )
        return ProgramAtlasV0(
            qualified_name=function.qualified_name,
            core_ir=ir,
            validation_certificate=function.validation_certificate,
            compilation_certificate=compilation,
            boundary=BoundaryPresentationV0(
                public_form="{}[]()",
                policy=request.policy,
                transition=direct_observer.result,
                certificate=direct_observer.certificate,
            ),
            through=ThroughPresentationV0(
                forms=direct_observer.result.opposite_pair_transitions,
                exact_lineage_links=direct_observer.result.lineage_links,
            ),
            multi_hole=MultiHolePresentationV0(
                graft=graft.result,
                carrier=direct_slice.result,
                composition_middle=middle,
                composition_certificate=slice_composition.certificate,
                observer_composition_certificate=observer_composition.certificate,
            ),
            characteristic=feature,
            correspondence=correspondence,
            residual=residual,
        )

    @staticmethod
    def _check_type(
        function: KernelFunction,
        request: DistributivityTaskRequestV0,
    ) -> None:
        if function.signature.input_names != request.variables:
            raise _NotRepresentable("the input names must be exactly a, x, y")
        if function.signature.inputs != tuple((name, "real") for name in request.variables):
            raise _NotRepresentable("all three inputs must have type Real")
        if function.signature.outputs != ("real",):
            raise _NotRepresentable("the task requires exactly one Real output")

    @staticmethod
    def _middle(function: KernelFunction, node_ids: tuple[int, ...]) -> tuple[int, ...]:
        for size in range(1, len(node_ids)):
            candidate = node_ids[:size]
            try:
                function.causal_cut(candidate)
            except ValueError:
                continue
            return candidate
        raise _NotRepresentable("the checked process has no nontrivial adjacent composition cut")

    @staticmethod
    def _feature(
        function: KernelFunction,
        variables: tuple[str, ...],
        max_degree: int,
    ) -> PolynomialCharacteristicV0:
        try:
            import sympy
        except ImportError as error:  # pragma: no cover - test extra supplies SymPy
            raise _NotRepresentable("SymPy is unavailable for the research projection") from error
        expression = function.to_sympy()
        if isinstance(expression, tuple):
            raise _NotRepresentable("the polynomial characteristic requires one scalar output")
        by_name = {str(symbol): symbol for symbol in expression.free_symbols}
        symbols = tuple(
            by_name.get(name, sympy.Symbol(name, real=True)) for name in variables
        )
        if {str(symbol) for symbol in expression.free_symbols} - set(variables):
            raise _NotRepresentable("the characteristic contains an undeclared symbol")
        try:
            polynomial = sympy.Poly(sympy.expand(expression), *symbols, domain=sympy.QQ)
        except (sympy.PolynomialError, TypeError, ValueError) as error:
            raise _NotRepresentable("the output is not in exact Q[a,x,y]") from error
        degree = int(polynomial.total_degree())
        if degree > max_degree:
            raise _NotRepresentable(
                f"polynomial degree {degree} exceeds the declared bound {max_degree}"
            )
        terms = tuple(
            RationalMonomialV0(
                exponents=tuple(int(exponent) for exponent in exponents),
                numerator=int(coefficient.p),
                denominator=int(coefficient.q),
            )
            for exponents, coefficient in polynomial.terms()
        )
        return PolynomialCharacteristicV0(
            variables=variables,
            terms=terms,
            total_degree=degree,
        )

    @staticmethod
    def _counterexample(
        left: PolynomialCharacteristicV0,
        right: PolynomialCharacteristicV0,
        degree_bound: int,
    ) -> PolynomialCounterexampleV0 | None:
        grid = range(degree_bound + 1)
        for point in product(grid, repeat=len(left.variables)):
            assignment = dict(zip(left.variables, point, strict=True))
            left_value = left.evaluate(assignment)
            right_value = right.evaluate(assignment)
            if left_value != right_value:
                return PolynomialCounterexampleV0(
                    assignment=tuple(zip(left.variables, point, strict=True)),
                    left_value=left_value,
                    right_value=right_value,
                )
        return None

    @staticmethod
    def _profile(atlas: ProgramAtlasV0) -> tuple[tuple[str, int], ...]:
        return tuple(sorted(Counter(atlas.residual.operation_names).items()))

    def _distributivity_witness(
        self,
        left: ProgramAtlasV0,
        right: ProgramAtlasV0,
        common: PolynomialCharacteristicV0,
    ) -> DistributivityWitnessV0 | None:
        left_counts = Counter(left.residual.operation_names)
        right_counts = Counter(right.residual.operation_names)
        factored = (
            left_counts["add"] == 1
            and left_counts["mul"] == 1
            and left_counts["copy"] == 0
        )
        expanded = (
            right_counts["add"] == 1
            and right_counts["mul"] == 2
            and right_counts["copy"] == 1
        )
        if not factored or not expanded:
            return None
        return DistributivityWitnessV0(
            rule="left-distributivity-over-addition-v0",
            substitution=(("factor", "a"), ("left_addend", "x"), ("right_addend", "y")),
            common_characteristic=common,
            left_operation_profile=self._profile(left),
            right_operation_profile=self._profile(right),
            exact_polynomial_identity=True,
            residuals_retained=left.residual.retained and right.residual.retained,
        )

    def _success_boundary(
        self,
        request: DistributivityTaskRequestV0,
        kind: CharacteristicResultKindV0,
        verdict: ExperimentVerdictV0,
        reason: str,
        validation: list[CharacteristicValidationRecordV0],
        checked_names: tuple[str, ...],
        left: ProgramAtlasV0,
        right: ProgramAtlasV0,
        forget: TaskRelativeForgetEvidenceV0,
        *,
        common_characteristic: PolynomialCharacteristicV0 | None = None,
        proof_witness: DistributivityWitnessV0 | None = None,
        counterexample: PolynomialCounterexampleV0 | None = None,
    ) -> CharacteristicTaskArtifactV0:
        validation.append(
            self._satisfied(
                CharacteristicLayerV0.PROMOTION_BOUNDARY,
                "feature comparison authorizes neither program identity, an "
                "equation cell, nor provenance erasure",
            )
        )
        return CharacteristicTaskArtifactV0(
            request=request,
            kind=kind,
            verdict=verdict,
            reason=reason,
            validation=tuple(validation),
            checked_core_names=checked_names,
            left=left,
            right=right,
            common_characteristic=common_characteristic,
            forget_evidence=forget,
            proof_witness=proof_witness,
            counterexample=counterexample,
        )

    def _finish(
        self,
        request: DistributivityTaskRequestV0,
        kind: CharacteristicResultKindV0,
        verdict: ExperimentVerdictV0,
        reason: str,
        validation: list[CharacteristicValidationRecordV0],
        failed_layer: CharacteristicLayerV0,
        **kwargs: Any,
    ) -> CharacteristicTaskArtifactV0:
        validation.append(
            CharacteristicValidationRecordV0(
                layer=failed_layer,
                outcome=LayerOutcomeV0.FAILED,
                reason=reason,
            )
        )
        completed = {record.layer for record in validation}
        validation.extend(
            CharacteristicValidationRecordV0(
                layer=layer,
                outcome=LayerOutcomeV0.BLOCKED,
                reason=f"blocked after {failed_layer.value}",
            )
            for layer in self._LAYERS
            if layer not in completed
        )
        return CharacteristicTaskArtifactV0(
            request=request,
            kind=kind,
            verdict=verdict,
            reason=reason,
            validation=tuple(validation),
            checked_core_names=kwargs.pop("checked_core_names", ()),
            **kwargs,
        )

    @staticmethod
    def _satisfied(
        layer: CharacteristicLayerV0,
        reason: str,
    ) -> CharacteristicValidationRecordV0:
        return CharacteristicValidationRecordV0(
            layer=layer,
            outcome=LayerOutcomeV0.SATISFIED,
            reason=reason,
        )
