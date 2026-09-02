"""Reusable distributivity character over Rust-checked finite instances.

This module is a nonauthoritative research companion.  A historical character
retains a checked polynomial law, both process residuals, its finite scope, and
a handle for observer-relative reopening.  Typed instantiation emits fresh
Lisp source and sends every finite instance through the existing Rust-backed
characteristic calibration.  It never allocates a semantic identity, equation
cell, right to forget, or geometric lift.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from hashlib import sha256
from math import prod

from .characteristic_research import (
    CharacteristicDirectionV0,
    CharacteristicResultKindV0,
    CharacteristicTaskArtifactV0,
    DistributivityCharacteristicMachineV0,
    DistributivityTaskRequestV0,
    PolynomialCharacteristicV0,
    ProcessResidualV0,
    RationalMonomialV0,
)
from .research import ExperimentVerdictV0


class HistoricalObserverV0(StrEnum):
    """The two ordered observations used by the reopen calibration."""

    POLYNOMIAL = "polynomial"
    OCCURRENCE = "occurrence"


class HistoricalClosureReadingV0(StrEnum):
    """Only the marked correspondence is admitted by this experiment."""

    MARKED_CORRESPONDENCE = "marked_correspondence"
    SOURCE_QUOTIENT = "source_quotient"


class HistoricalCharacterResultKindV0(StrEnum):
    """Finite research outcomes for construction, reuse, and reopening."""

    CREATED = "created"
    INSTANTIATED = "instantiated"
    REOPENED = "reopened"
    NOT_REPRESENTABLE = "not_representable"
    FUEL_EXHAUSTED = "fuel_exhausted"


@dataclass(frozen=True, slots=True)
class HistoricalCharacterScopeV0:
    """The exact fragment in which the finite character may be reused."""

    observer: HistoricalObserverV0
    variables: tuple[str, ...]
    value_type: str
    max_degree: int
    allowed_operations: tuple[str, ...]
    substitution_policy: str
    rule_has_fixed_semantic_depth: bool = False


@dataclass(frozen=True, slots=True)
class HistoricalCharacterCertificateV0:
    """A scoped Python witness referencing prior Rust-derived artifacts."""

    rule: str
    common_characteristic: PolynomialCharacteristicV0
    checked_core_names: tuple[str, ...]
    source_validation_layers: tuple[str, ...]
    exact_polynomial_identity: bool
    residuals_retained: bool
    rust_certificate: bool = False
    equation_cell_authorized: bool = False
    program_identity_authorized: bool = False


@dataclass(frozen=True, slots=True)
class HistoricalCharacterHistoryV0:
    """The finite process history that sealing is not allowed to erase."""

    left_qualified_name: str
    right_qualified_name: str
    left_residual: ProcessResidualV0
    right_residual: ProcessResidualV0
    feature_policy: str


@dataclass(frozen=True, slots=True)
class HistoricalReopenHandleV0:
    """The declared observer refinement and the residuals it can expose."""

    from_observer: HistoricalObserverV0
    to_observer: HistoricalObserverV0
    left_residual: ProcessResidualV0
    right_residual: ProcessResidualV0


@dataclass(frozen=True, slots=True)
class HistoricalCharacterV0:
    """One reusable, reopenable, research-local distributivity character."""

    label: str
    body: PolynomialCharacteristicV0
    certificate: HistoricalCharacterCertificateV0
    scope: HistoricalCharacterScopeV0
    history: HistoricalCharacterHistoryV0
    reopen_handle: HistoricalReopenHandleV0
    semantic_identity_authorized: bool = False
    provenance_erasure_authorized: bool = False
    deck_transformation_authorized: bool = False
    hyperbolic_axis_authorized: bool = False


@dataclass(frozen=True, slots=True)
class HistoricalCharacterBuildArtifactV0:
    """The result of attempting to seal the original finite calibration."""

    kind: HistoricalCharacterResultKindV0
    verdict: ExperimentVerdictV0
    reason: str
    source_artifact: CharacteristicTaskArtifactV0
    character: HistoricalCharacterV0 | None = None
    semantic_authority: bool = False


@dataclass(frozen=True, slots=True)
class TypedDistributivitySubstitutionV0:
    """A typed placement of factor, left addend, and right addend."""

    factor: str
    left_addend: str
    right_addend: str
    value_type: str = "Real"

    @property
    def ordered_slots(self) -> tuple[str, ...]:
        return (self.factor, self.left_addend, self.right_addend)


@dataclass(frozen=True, slots=True)
class HistoricalInstantiationRequestV0:
    """One finite typed reuse in an optional multiplicative context."""

    character: HistoricalCharacterV0
    instance_name: str
    substitution: TypedDistributivitySubstitutionV0
    context_scalars: tuple[int, ...] = ()
    context_operation: str = "mul"
    closure_reading: HistoricalClosureReadingV0 = (
        HistoricalClosureReadingV0.MARKED_CORRESPONDENCE
    )
    max_degree: int = 2
    fuel: int | None = None
    retain_residual: bool = True

    def __post_init__(self) -> None:
        if re.fullmatch(r"[a-z][a-z0-9-]*", self.instance_name) is None:
            raise ValueError("instance_name must be a lowercase Lisp identifier")
        if not isinstance(self.character, HistoricalCharacterV0):
            raise ValueError("character must be a HistoricalCharacterV0")
        if not isinstance(self.substitution, TypedDistributivitySubstitutionV0):
            raise ValueError("substitution must be typed")
        if not isinstance(self.closure_reading, HistoricalClosureReadingV0):
            raise ValueError("closure_reading must be explicit")
        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in self.context_scalars
        ):
            raise ValueError("context scalars must be exact integers")
        if isinstance(self.max_degree, bool) or not isinstance(self.max_degree, int):
            raise ValueError("max_degree must be an integer")
        if self.max_degree < 0:
            raise ValueError("max_degree must be non-negative")
        if self.fuel is not None and (
            isinstance(self.fuel, bool)
            or not isinstance(self.fuel, int)
            or self.fuel < 0
        ):
            raise ValueError("fuel must be a non-negative integer or None")

    @property
    def finite_depth(self) -> int:
        return 1 + len(self.context_scalars)


@dataclass(frozen=True, slots=True)
class HistoricalInstantiationEvidenceV0:
    """Provenance for one fresh checked program pair."""

    character_label: str
    rule: str
    substitution: TypedDistributivitySubstitutionV0
    context_scalars: tuple[int, ...]
    finite_depth: int
    generated_module: str
    generated_source: str
    generated_source_sha256: str
    source_programs: tuple[str, ...]
    checked_programs: tuple[str, ...]
    common_characteristic: PolynomialCharacteristicV0
    left_residual: ProcessResidualV0
    right_residual: ProcessResidualV0
    character_certificate_reused: bool
    instance_feature_rechecked: bool
    rust_programs_rechecked: bool
    rule_has_fixed_semantic_depth: bool = False
    program_identity_authorized: bool = False
    equation_cell_authorized: bool = False
    semantic_authority: bool = False


@dataclass(frozen=True, slots=True)
class HistoricalInstantiationArtifactV0:
    """The finite result of one typed historical-character reuse."""

    kind: HistoricalCharacterResultKindV0
    verdict: ExperimentVerdictV0
    reason: str
    request: HistoricalInstantiationRequestV0
    characteristic_artifact: CharacteristicTaskArtifactV0 | None = None
    evidence: HistoricalInstantiationEvidenceV0 | None = None
    semantic_authority: bool = False


@dataclass(frozen=True, slots=True)
class CopyHistoryWitnessV0:
    """A concrete occurrence-observer witness for the expanded presentation."""

    left_program: str
    right_program: str
    left_copy_event_ids: tuple[int, ...]
    right_copy_event_ids: tuple[int, ...]
    left_occurrence_ids: tuple[str, ...]
    right_occurrence_ids: tuple[str, ...]
    extra_left_operations: tuple[tuple[str, int], ...]
    extra_right_operations: tuple[tuple[str, int], ...]


@dataclass(frozen=True, slots=True)
class HistoricalReopenEvidenceV0:
    """A refinement witness that restores hidden process distinctions."""

    character_label: str
    from_observer: HistoricalObserverV0
    to_observer: HistoricalObserverV0
    copy_history: CopyHistoryWitnessV0
    common_characteristic: PolynomialCharacteristicV0
    polynomial_law_remains_reusable: bool
    program_identity_refuted: bool
    residuals_retained: bool
    historical_inverse_authorized: bool = False
    provenance_erasure_authorized: bool = False
    semantic_authority: bool = False


@dataclass(frozen=True, slots=True)
class HistoricalReopenArtifactV0:
    """The result of refining one sealed instance to occurrence observation."""

    kind: HistoricalCharacterResultKindV0
    verdict: ExperimentVerdictV0
    reason: str
    evidence: HistoricalReopenEvidenceV0 | None = None
    semantic_authority: bool = False


class HistoricalDistributivityMachineV0:
    """Create, instantiate, and reopen one bounded historical character."""

    _VARIABLES = ("a", "x", "y")

    def create(
        self,
        request: DistributivityTaskRequestV0,
    ) -> HistoricalCharacterBuildArtifactV0:
        source = DistributivityCharacteristicMachineV0().run(request)
        return self.create_from_artifact(source)

    @staticmethod
    def create_from_artifact(
        source: CharacteristicTaskArtifactV0,
    ) -> HistoricalCharacterBuildArtifactV0:
        if source.kind is CharacteristicResultKindV0.FUEL_EXHAUSTED:
            return HistoricalCharacterBuildArtifactV0(
                kind=HistoricalCharacterResultKindV0.FUEL_EXHAUSTED,
                verdict=ExperimentVerdictV0.FUEL_EXHAUSTED,
                reason="fuel ended before the historical character could be sealed",
                source_artifact=source,
            )
        complete = (
            source.kind is CharacteristicResultKindV0.PROVED
            and source.left is not None
            and source.right is not None
            and source.common_characteristic is not None
            and source.proof_witness is not None
            and source.forget_evidence is not None
            and source.left.residual.retained
            and source.right.residual.retained
        )
        if not complete:
            return HistoricalCharacterBuildArtifactV0(
                kind=HistoricalCharacterResultKindV0.NOT_REPRESENTABLE,
                verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
                reason=(
                    "sealing requires the proved bounded law and both complete "
                    "process residuals"
                ),
                source_artifact=source,
            )
        witness = source.proof_witness
        assert witness is not None
        left = source.left
        right = source.right
        common = source.common_characteristic
        assert left is not None and right is not None and common is not None
        certificate = HistoricalCharacterCertificateV0(
            rule=witness.rule,
            common_characteristic=common,
            checked_core_names=source.checked_core_names,
            source_validation_layers=tuple(
                record.layer.value for record in source.validation
            ),
            exact_polynomial_identity=witness.exact_polynomial_identity,
            residuals_retained=witness.residuals_retained,
        )
        character = HistoricalCharacterV0(
            label="historical-distributivity-v0",
            body=common,
            certificate=certificate,
            scope=HistoricalCharacterScopeV0(
                observer=HistoricalObserverV0.POLYNOMIAL,
                variables=common.variables,
                value_type="Real",
                max_degree=source.request.max_degree,
                allowed_operations=("add", "mul", "copy", "discard", "constant", "id"),
                substitution_policy="typed-variable-permutation-with-mul-context-v0",
            ),
            history=HistoricalCharacterHistoryV0(
                left_qualified_name=left.qualified_name,
                right_qualified_name=right.qualified_name,
                left_residual=left.residual,
                right_residual=right.residual,
                feature_policy=common.feature_policy,
            ),
            reopen_handle=HistoricalReopenHandleV0(
                from_observer=HistoricalObserverV0.POLYNOMIAL,
                to_observer=HistoricalObserverV0.OCCURRENCE,
                left_residual=left.residual,
                right_residual=right.residual,
            ),
        )
        return HistoricalCharacterBuildArtifactV0(
            kind=HistoricalCharacterResultKindV0.CREATED,
            verdict=ExperimentVerdictV0.SUPPORTED,
            reason=(
                "one scoped historical character retains the common law, "
                "both process histories, and an occurrence-reopen handle"
            ),
            source_artifact=source,
            character=character,
        )

    def instantiate(
        self,
        request: HistoricalInstantiationRequestV0,
    ) -> HistoricalInstantiationArtifactV0:
        refusal = self._request_refusal(request)
        if refusal is not None:
            return HistoricalInstantiationArtifactV0(
                kind=HistoricalCharacterResultKindV0.NOT_REPRESENTABLE,
                verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
                reason=refusal,
                request=request,
            )
        source, module = self._source(request)
        task = DistributivityTaskRequestV0(
            sources=(source,),
            module=module,
            left_function="factored",
            right_function="expanded",
            direction=CharacteristicDirectionV0.PROVE,
            max_degree=request.max_degree,
            fuel=request.fuel,
            retain_residual=request.retain_residual,
        )
        result = DistributivityCharacteristicMachineV0().run(task)
        if result.kind is CharacteristicResultKindV0.FUEL_EXHAUSTED:
            return HistoricalInstantiationArtifactV0(
                kind=HistoricalCharacterResultKindV0.FUEL_EXHAUSTED,
                verdict=ExperimentVerdictV0.FUEL_EXHAUSTED,
                reason="fuel ended while checking the fresh finite instance",
                request=request,
                characteristic_artifact=result,
            )
        if result.kind not in {
            CharacteristicResultKindV0.PROVED,
            CharacteristicResultKindV0.OBSERVATIONALLY_EQUAL,
        }:
            return HistoricalInstantiationArtifactV0(
                kind=HistoricalCharacterResultKindV0.NOT_REPRESENTABLE,
                verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
                reason=f"the fresh instance was refused: {result.reason}",
                request=request,
                characteristic_artifact=result,
            )
        if (
            result.left is None
            or result.right is None
            or result.common_characteristic is None
        ):
            return HistoricalInstantiationArtifactV0(
                kind=HistoricalCharacterResultKindV0.NOT_REPRESENTABLE,
                verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
                reason="the fresh instance did not retain both checked atlases",
                request=request,
                characteristic_artifact=result,
            )
        expected = self._expected_characteristic(request)
        if result.common_characteristic != expected:
            return HistoricalInstantiationArtifactV0(
                kind=HistoricalCharacterResultKindV0.NOT_REPRESENTABLE,
                verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
                reason="the fresh checked feature does not instantiate the sealed rule",
                request=request,
                characteristic_artifact=result,
            )
        evidence = HistoricalInstantiationEvidenceV0(
            character_label=request.character.label,
            rule=request.character.certificate.rule,
            substitution=request.substitution,
            context_scalars=request.context_scalars,
            finite_depth=request.finite_depth,
            generated_module=module,
            generated_source=source,
            generated_source_sha256=sha256(source.encode("utf-8")).hexdigest(),
            source_programs=request.character.certificate.checked_core_names,
            checked_programs=result.checked_core_names,
            common_characteristic=result.common_characteristic,
            left_residual=result.left.residual,
            right_residual=result.right.residual,
            character_certificate_reused=True,
            instance_feature_rechecked=True,
            rust_programs_rechecked=True,
        )
        return HistoricalInstantiationArtifactV0(
            kind=HistoricalCharacterResultKindV0.INSTANTIATED,
            verdict=ExperimentVerdictV0.SUPPORTED,
            reason=(
                "the historical rule generated one fresh finite Rust-checked "
                "instance with explicit substitution provenance"
            ),
            request=request,
            characteristic_artifact=result,
            evidence=evidence,
        )

    @staticmethod
    def reopen(
        instance: HistoricalInstantiationArtifactV0,
        observer: HistoricalObserverV0,
    ) -> HistoricalReopenArtifactV0:
        if (
            observer is not HistoricalObserverV0.OCCURRENCE
            or instance.kind is not HistoricalCharacterResultKindV0.INSTANTIATED
            or instance.evidence is None
            or instance.characteristic_artifact is None
            or instance.characteristic_artifact.left is None
            or instance.characteristic_artifact.right is None
        ):
            return HistoricalReopenArtifactV0(
                kind=HistoricalCharacterResultKindV0.NOT_REPRESENTABLE,
                verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
                reason=(
                    "reopening requires a supported instance and refinement "
                    "from the polynomial observer to the occurrence observer"
                ),
            )
        left = instance.characteristic_artifact.left
        right = instance.characteristic_artifact.right
        left_counts = Counter(left.residual.operation_names)
        right_counts = Counter(right.residual.operation_names)
        left_copy_ids = tuple(
            int(node["id"])
            for node in left.core_ir["nodes"]
            if node["operation"]["name"] == "copy"
        )
        right_copy_ids = tuple(
            int(node["id"])
            for node in right.core_ir["nodes"]
            if node["operation"]["name"] == "copy"
        )
        extra_left = tuple(sorted((left_counts - right_counts).items()))
        extra_right = tuple(sorted((right_counts - left_counts).items()))
        witness = CopyHistoryWitnessV0(
            left_program=left.qualified_name,
            right_program=right.qualified_name,
            left_copy_event_ids=left_copy_ids,
            right_copy_event_ids=right_copy_ids,
            left_occurrence_ids=left.residual.occurrence_ids,
            right_occurrence_ids=right.residual.occurrence_ids,
            extra_left_operations=extra_left,
            extra_right_operations=extra_right,
        )
        if left_copy_ids or not right_copy_ids:
            return HistoricalReopenArtifactV0(
                kind=HistoricalCharacterResultKindV0.NOT_REPRESENTABLE,
                verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
                reason="the occurrence observer did not recover the expected copy distinction",
            )
        evidence = HistoricalReopenEvidenceV0(
            character_label=instance.evidence.character_label,
            from_observer=HistoricalObserverV0.POLYNOMIAL,
            to_observer=HistoricalObserverV0.OCCURRENCE,
            copy_history=witness,
            common_characteristic=instance.evidence.common_characteristic,
            polynomial_law_remains_reusable=True,
            program_identity_refuted=left.core_ir != right.core_ir,
            residuals_retained=(
                left.residual.retained and right.residual.retained
            ),
        )
        return HistoricalReopenArtifactV0(
            kind=HistoricalCharacterResultKindV0.REOPENED,
            verdict=ExperimentVerdictV0.SUPPORTED,
            reason=(
                "occurrence refinement re-exposed copy and process history "
                "without refuting the polynomial law"
            ),
            evidence=evidence,
        )

    def _request_refusal(
        self,
        request: HistoricalInstantiationRequestV0,
    ) -> str | None:
        if request.character.scope.observer is not HistoricalObserverV0.POLYNOMIAL:
            return "V0 instantiates only a polynomial-observer historical character"
        if request.substitution.value_type != request.character.scope.value_type:
            return "the substitution value type does not match the Real character scope"
        if set(request.substitution.ordered_slots) != set(self._VARIABLES):
            return "the three substitution slots must be a permutation of a, x, and y"
        if len(set(request.substitution.ordered_slots)) != 3:
            return "the typed substitution may not identify two linear input slots"
        if request.context_operation != "mul":
            return "the historical character does not represent that context operation"
        if any(value == 0 for value in request.context_scalars):
            return "zero contexts are excluded because they erase the calibrated law"
        if request.closure_reading is HistoricalClosureReadingV0.SOURCE_QUOTIENT:
            return "source-quotient closure has no right-to-forget witness"
        if not request.retain_residual:
            return "historical reuse is unavailable when process residuals would be dropped"
        return None

    @staticmethod
    def _wrap_context(expression: str, scalars: tuple[int, ...]) -> str:
        for scalar in reversed(scalars):
            expression = f"(mul (frontier {scalar} {expression}))"
        return expression

    def _source(
        self,
        request: HistoricalInstantiationRequestV0,
    ) -> tuple[str, str]:
        substitution = request.substitution
        factored_base = (
            f"(mul (frontier (use {substitution.factor}) "
            f"(add (frontier (use {substitution.left_addend}) "
            f"(use {substitution.right_addend})))))"
        )
        factored_expression = self._wrap_context(
            factored_base,
            request.context_scalars,
        )
        expanded_left = "(mul (frontier (use factor-left) (use left-addend)))"
        expanded_right = "(mul (frontier (use factor-right) (use right-addend)))"
        expanded_left = self._wrap_context(expanded_left, request.context_scalars)
        expanded_right = self._wrap_context(expanded_right, request.context_scalars)
        expanded_expression = (
            f"(add (frontier {expanded_left} {expanded_right}))"
        )
        module = f"historical-dist-{request.instance_name}"
        source = f"""(module {module}
  (export factored expanded)

  (def factored-body
    (fn ((a Real) (x Real) (y Real)) Real
      {factored_expression}))

  (def expanded-body
    (fn ((factor-left Real) (factor-right Real)
         (left-addend Real) (right-addend Real)) Real
      {expanded_expression}))

  (def factored
    (fn ((a Real) (x Real) (y Real)) Real
      (call factored-body (use a) (use x) (use y))))

  (def expanded
    (fn ((a Real) (x Real) (y Real)) Real
      (call expanded-body
        (copy (use {substitution.factor}))
        (use {substitution.left_addend})
        (use {substitution.right_addend}))))
)
"""
        return source, module

    @staticmethod
    def _expected_characteristic(
        request: HistoricalInstantiationRequestV0,
    ) -> PolynomialCharacteristicV0:
        variables = ("a", "x", "y")
        coefficient = Fraction(prod(request.context_scalars, start=1))
        terms: Counter[tuple[int, ...]] = Counter()
        substitution = request.substitution
        for addend in (substitution.left_addend, substitution.right_addend):
            exponents = [0, 0, 0]
            exponents[variables.index(substitution.factor)] += 1
            exponents[variables.index(addend)] += 1
            terms[tuple(exponents)] += coefficient
        monomials = tuple(
            RationalMonomialV0(
                exponents=exponents,
                numerator=terms[exponents].numerator,
                denominator=terms[exponents].denominator,
            )
            for exponents in sorted(terms, reverse=True)
        )
        return PolynomialCharacteristicV0(
            variables=variables,
            terms=monomials,
            total_degree=2,
        )
