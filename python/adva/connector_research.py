"""Compare three same-domain connector readings over one triangular artifact.

This module is a nonauthoritative research companion. It reads exact Rust
occurrence, source, path, slice, and graft artifacts through the existing
triangular calibration. It allocates no semantic identity and promotes no
connector, quotient, circular execution, or right-to-forget rule.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, ClassVar

from .core import TriadicDomainV0
from .research import ExperimentVerdictV0, LayerOutcomeV0, ResearchCodeV0
from .triangular_research import (
    TriangularThroughArtifactV0,
    TriangularThroughMachineV0,
    TriangularThroughRequestV0,
)


class ConnectorReadingV0(StrEnum):
    """The three deliberately distinct connector readings under calibration."""

    EXACT_IDENTITY = "exact_identity"
    DIRECT_SIBLING_COMPARISON = "direct_sibling_comparison"
    SOURCE_QUOTIENT = "source_quotient"


class ConnectorCalibrationLayerV0(StrEnum):
    """Ordered gates for the connector trichotomy experiment."""

    TRIANGLE_CARRIER = "triangle_carrier"
    TYPED_BOUNDARIES = "typed_boundaries"
    EXACT_IDENTITY = "exact_identity"
    SIBLING_COMPARISON = "sibling_comparison"
    SOURCE_QUOTIENT = "source_quotient"
    RESIDUAL_RETENTION = "residual_retention"
    PROMOTION_BOUNDARY = "promotion_boundary"


@dataclass(frozen=True, slots=True)
class ConnectorCalibrationRecordV0:
    """One Python research gate outcome; never a Rust certificate."""

    layer: ConnectorCalibrationLayerV0
    outcome: LayerOutcomeV0
    reason: str


@dataclass(frozen=True, slots=True)
class SameDomainBoundaryV0:
    """The exact adjacent endpoints that one typed connector would have to join."""

    domain: TriadicDomainV0
    exit_incidence_index: int
    entry_incidence_index: int
    exit_occurrence_id: str
    entry_occurrence_id: str
    source_id: str
    exit_path: tuple[int, ...]
    entry_path: tuple[int, ...]
    common_parent_path: tuple[int, ...]
    direct_copy_siblings: bool


@dataclass(frozen=True, slots=True)
class TypedConnectorCandidateV0:
    """One finite occurrence relation proposed over a checked domain boundary."""

    reading: ConnectorReadingV0
    boundary: SameDomainBoundaryV0
    relation: tuple[tuple[int, int], ...]
    symmetric: bool
    preserves_occurrence_identity: bool
    semantic_authority: bool = False


@dataclass(frozen=True, slots=True)
class SourceQuotientClassV0:
    """A many-to-one observation class using an already checked SourceId."""

    domain: TriadicDomainV0
    source_id: str
    incidence_indices: tuple[int, ...]
    occurrence_ids: tuple[str, ...]
    occurrence_paths: tuple[tuple[int, ...], ...]


@dataclass(frozen=True, slots=True)
class ConnectorTrialV0:
    """One reading's finite composition result and promotion boundary."""

    reading: ConnectorReadingV0
    connectors: tuple[TypedConnectorCandidateV0, ...]
    occurrence_cycle_relation: tuple[tuple[int, int], ...]
    source_cycle_relation: tuple[tuple[str, str], ...]
    finite_composition_verdict: ExperimentVerdictV0
    promotion_verdict: ExperimentVerdictV0
    preserves_occurrence_identity: bool
    requires_forgetting: bool
    residual_retained: bool
    forgetting_authorized: bool = False
    global_closure_authorized: bool = False
    semantic_authority: bool = False


@dataclass(frozen=True, slots=True)
class ConnectorCalibrationArtifactV0:
    """All bounded evidence from the connector trichotomy."""

    code: ResearchCodeV0
    request: TriangularThroughRequestV0
    verdict: ExperimentVerdictV0
    reason: str
    validation: tuple[ConnectorCalibrationRecordV0, ...]
    triangle: TriangularThroughArtifactV0
    boundaries: tuple[SameDomainBoundaryV0, ...]
    quotient_classes: tuple[SourceQuotientClassV0, ...]
    trials: tuple[ConnectorTrialV0, ...]


class ConnectorCalibrationMachineV0:
    """Test identity, sibling comparison, and source quotient without promotion."""

    _LAYERS: ClassVar[tuple[ConnectorCalibrationLayerV0, ...]] = tuple(
        ConnectorCalibrationLayerV0
    )
    _DOMAIN_ORDER: ClassVar[tuple[TriadicDomainV0, ...]] = (
        TriadicDomainV0.SPACE,
        TriadicDomainV0.TIME,
        TriadicDomainV0.CONSTRUCTION,
    )

    def run(
        self,
        code: ResearchCodeV0,
        request: TriangularThroughRequestV0,
    ) -> ConnectorCalibrationArtifactV0:
        validation: list[ConnectorCalibrationRecordV0] = []
        triangle = TriangularThroughMachineV0().run(code, request)
        if (
            triangle.verdict is not ExperimentVerdictV0.SUPPORTED
            or not triangle.cells
            or triangle.closure is None
            or triangle.closure.verdict is not ExperimentVerdictV0.NOT_REPRESENTABLE
            or triangle.closure.raw_cycle_relation
        ):
            return self._finish(
                code,
                request,
                triangle,
                ExperimentVerdictV0.OBSTRUCTION,
                "connector calibration requires the checked local triangle and raw closure no-go",
                validation,
                ConnectorCalibrationLayerV0.TRIANGLE_CARRIER,
            )
        validation.append(
            self._satisfied(
                ConnectorCalibrationLayerV0.TRIANGLE_CARRIER,
                "one supported triangular artifact supplies the unchanged exact carrier",
            )
        )

        primary = triangle.cells[0]
        incidences = primary.lower_interface.incidences
        kx = self._find_angle(
            triangle,
            TriadicDomainV0.CONSTRUCTION,
            TriadicDomainV0.SPACE,
        )
        xt = self._find_angle(
            triangle,
            TriadicDomainV0.SPACE,
            TriadicDomainV0.TIME,
        )
        tk = self._find_angle(
            triangle,
            TriadicDomainV0.TIME,
            TriadicDomainV0.CONSTRUCTION,
        )
        specifications = (
            (
                TriadicDomainV0.SPACE,
                kx.right_incidence_indices[0],
                xt.left_incidence_indices[0],
            ),
            (
                TriadicDomainV0.TIME,
                xt.right_incidence_indices[0],
                tk.left_incidence_indices[0],
            ),
            (
                TriadicDomainV0.CONSTRUCTION,
                tk.right_incidence_indices[0],
                kx.left_incidence_indices[0],
            ),
        )
        try:
            boundaries = tuple(
                self._boundary(domain, exit_index, entry_index, incidences)
                for domain, exit_index, entry_index in specifications
            )
        except (IndexError, KeyError, TypeError, ValueError) as error:
            return self._finish(
                code,
                request,
                triangle,
                ExperimentVerdictV0.OBSTRUCTION,
                f"an adjacent typed boundary was malformed: {error}",
                validation,
                ConnectorCalibrationLayerV0.TYPED_BOUNDARIES,
            )
        if (
            tuple(boundary.domain for boundary in boundaries) != self._DOMAIN_ORDER
            or not all(boundary.direct_copy_siblings for boundary in boundaries)
            or len({boundary.source_id for boundary in boundaries}) != 3
        ):
            return self._finish(
                code,
                request,
                triangle,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                "all three adjacent endpoints must be exact direct copy siblings",
                validation,
                ConnectorCalibrationLayerV0.TYPED_BOUNDARIES,
                boundaries=boundaries,
            )
        validation.append(
            self._satisfied(
                ConnectorCalibrationLayerV0.TYPED_BOUNDARIES,
                "three domains expose distinct occurrence pairs with exact common copy parents",
            )
        )

        angle_edges = {
            "kx": self._angle_edges(kx),
            "xt": self._angle_edges(xt),
            "tk": self._angle_edges(tk),
        }
        identity_connectors = tuple(
            TypedConnectorCandidateV0(
                reading=ConnectorReadingV0.EXACT_IDENTITY,
                boundary=boundary,
                relation=tuple(
                    (index, index)
                    for index, incidence in enumerate(incidences)
                    if TriadicDomainV0(incidence["domain"]) is boundary.domain
                ),
                symmetric=True,
                preserves_occurrence_identity=True,
            )
            for boundary in boundaries
        )
        identity_cycle = self._cycle(
            angle_edges,
            {connector.boundary.domain: connector.relation for connector in identity_connectors},
        )
        if identity_cycle:
            return self._finish(
                code,
                request,
                triangle,
                ExperimentVerdictV0.COUNTEREXAMPLE,
                "strict occurrence identity unexpectedly crossed distinct siblings",
                validation,
                ConnectorCalibrationLayerV0.EXACT_IDENTITY,
                boundaries=boundaries,
            )
        identity_trial = ConnectorTrialV0(
            reading=ConnectorReadingV0.EXACT_IDENTITY,
            connectors=identity_connectors,
            occurrence_cycle_relation=identity_cycle,
            source_cycle_relation=(),
            finite_composition_verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
            promotion_verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
            preserves_occurrence_identity=True,
            requires_forgetting=False,
            residual_retained=True,
        )
        validation.append(
            self._satisfied(
                ConnectorCalibrationLayerV0.EXACT_IDENTITY,
                "diagonal identity relations preserve occurrences and leave the cycle empty",
            )
        )

        sibling_connectors = tuple(
            TypedConnectorCandidateV0(
                reading=ConnectorReadingV0.DIRECT_SIBLING_COMPARISON,
                boundary=boundary,
                relation=tuple(
                    sorted(
                        {
                            (
                                boundary.exit_incidence_index,
                                boundary.entry_incidence_index,
                            ),
                            (
                                boundary.entry_incidence_index,
                                boundary.exit_incidence_index,
                            ),
                        }
                    )
                ),
                symmetric=True,
                preserves_occurrence_identity=True,
            )
            for boundary in boundaries
        )
        sibling_cycle = self._cycle(
            angle_edges,
            {connector.boundary.domain: connector.relation for connector in sibling_connectors},
        )
        expected_occurrence_cycle = (
            (
                kx.left_incidence_indices[0],
                kx.left_incidence_indices[0],
            ),
        )
        if (
            sibling_cycle != expected_occurrence_cycle
            or any(
                connector.relation
                != tuple(sorted((target, source) for source, target in connector.relation))
                for connector in sibling_connectors
            )
        ):
            return self._finish(
                code,
                request,
                triangle,
                ExperimentVerdictV0.COUNTEREXAMPLE,
                "direct sibling comparison failed its exact finite circular composition",
                validation,
                ConnectorCalibrationLayerV0.SIBLING_COMPARISON,
                boundaries=boundaries,
                trials=(identity_trial,),
            )
        sibling_trial = ConnectorTrialV0(
            reading=ConnectorReadingV0.DIRECT_SIBLING_COMPARISON,
            connectors=sibling_connectors,
            occurrence_cycle_relation=sibling_cycle,
            source_cycle_relation=(),
            finite_composition_verdict=ExperimentVerdictV0.SUPPORTED,
            promotion_verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
            preserves_occurrence_identity=True,
            requires_forgetting=False,
            residual_retained=True,
        )
        validation.append(
            self._satisfied(
                ConnectorCalibrationLayerV0.SIBLING_COMPARISON,
                "explicit symmetric sibling witnesses close one occurrence-indexed candidate relation",
            )
        )

        quotient_classes = tuple(
            self._quotient_class(domain, incidences) for domain in self._DOMAIN_ORDER
        )
        source_edges = {
            "kx": self._source_edges(kx, incidences),
            "xt": self._source_edges(xt, incidences),
            "tk": self._source_edges(tk, incidences),
        }
        source_cycle = self._compose(
            source_edges["tk"],
            self._compose(source_edges["xt"], source_edges["kx"]),
        )
        construction_source = next(
            item.source_id
            for item in quotient_classes
            if item.domain is TriadicDomainV0.CONSTRUCTION
        )
        if (
            source_cycle != ((construction_source, construction_source),)
            or any(len(item.incidence_indices) != 2 for item in quotient_classes)
            or any(len(set(item.occurrence_ids)) != 2 for item in quotient_classes)
        ):
            return self._finish(
                code,
                request,
                triangle,
                ExperimentVerdictV0.COUNTEREXAMPLE,
                "source projection failed to expose exactly three two-occurrence fibres",
                validation,
                ConnectorCalibrationLayerV0.SOURCE_QUOTIENT,
                boundaries=boundaries,
                trials=(identity_trial, sibling_trial),
                quotient_classes=quotient_classes,
            )
        quotient_trial = ConnectorTrialV0(
            reading=ConnectorReadingV0.SOURCE_QUOTIENT,
            connectors=(),
            occurrence_cycle_relation=(),
            source_cycle_relation=source_cycle,
            finite_composition_verdict=ExperimentVerdictV0.SUPPORTED,
            promotion_verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
            preserves_occurrence_identity=False,
            requires_forgetting=True,
            residual_retained=True,
        )
        validation.append(
            self._satisfied(
                ConnectorCalibrationLayerV0.SOURCE_QUOTIENT,
                "projection to checked SourceIds closes only after erasing sibling distinction",
            )
        )

        trials = (identity_trial, sibling_trial, quotient_trial)
        if (
            any(angle.residual is not primary.carrier for angle in triangle.angles)
            or any(not trial.residual_retained for trial in trials)
            or not {"constant", "discard"}
            <= {
                str(event["operation"]["name"])
                for event in primary.carrier.events
            }
        ):
            return self._finish(
                code,
                request,
                triangle,
                ExperimentVerdictV0.OBSTRUCTION,
                "one connector reading lost the common complete process residual",
                validation,
                ConnectorCalibrationLayerV0.RESIDUAL_RETENTION,
                boundaries=boundaries,
                trials=trials,
                quotient_classes=quotient_classes,
            )
        validation.append(
            self._satisfied(
                ConnectorCalibrationLayerV0.RESIDUAL_RETENTION,
                "all three readings remain attached to the same complete constant-discard residual",
            )
        )

        if (
            any(trial.forgetting_authorized for trial in trials)
            or any(trial.global_closure_authorized for trial in trials)
            or any(trial.semantic_authority for trial in trials)
            or any(
                connector.semantic_authority
                for trial in trials
                for connector in trial.connectors
            )
            or quotient_trial.promotion_verdict
            is not ExperimentVerdictV0.NOT_REPRESENTABLE
            or sibling_trial.promotion_verdict
            is not ExperimentVerdictV0.NOT_REPRESENTABLE
        ):
            return self._finish(
                code,
                request,
                triangle,
                ExperimentVerdictV0.OBSTRUCTION,
                "the connector calibration crossed its promotion boundary",
                validation,
                ConnectorCalibrationLayerV0.PROMOTION_BOUNDARY,
                boundaries=boundaries,
                trials=trials,
                quotient_classes=quotient_classes,
            )
        validation.append(
            self._satisfied(
                ConnectorCalibrationLayerV0.PROMOTION_BOUNDARY,
                "finite relational closure remains separate from semantic closure and forgetting rights",
            )
        )
        return self._finish(
            code,
            request,
            triangle,
            ExperimentVerdictV0.SUPPORTED,
            "the connector trichotomy passed with two distinct closure mechanisms and no promotion",
            validation,
            boundaries=boundaries,
            trials=trials,
            quotient_classes=quotient_classes,
        )

    @staticmethod
    def _find_angle(
        triangle: TriangularThroughArtifactV0,
        left: TriadicDomainV0,
        right: TriadicDomainV0,
    ) -> Any:
        return next(
            angle
            for angle in triangle.angles
            if angle.left_domain is left and angle.right_domain is right
        )

    @classmethod
    def _boundary(
        cls,
        domain: TriadicDomainV0,
        exit_index: int,
        entry_index: int,
        incidences: tuple[Any, ...],
    ) -> SameDomainBoundaryV0:
        exit_incidence = incidences[exit_index]
        entry_incidence = incidences[entry_index]
        if (
            TriadicDomainV0(exit_incidence["domain"]) is not domain
            or TriadicDomainV0(entry_incidence["domain"]) is not domain
        ):
            raise ValueError("connector endpoints have the wrong observer domain")
        exit_occurrence = exit_incidence["occurrence"]
        entry_occurrence = entry_incidence["occurrence"]
        exit_path = cls._path(exit_occurrence)
        entry_path = cls._path(entry_occurrence)
        same_source = exit_occurrence["source"] == entry_occurrence["source"]
        distinct_ids = exit_occurrence["id"] != entry_occurrence["id"]
        direct_siblings = (
            same_source
            and distinct_ids
            and len(exit_path) == len(entry_path)
            and len(exit_path) > 0
            and exit_path[:-1] == entry_path[:-1]
            and {exit_path[-1], entry_path[-1]} == {0, 1}
        )
        return SameDomainBoundaryV0(
            domain=domain,
            exit_incidence_index=exit_index,
            entry_incidence_index=entry_index,
            exit_occurrence_id=str(exit_occurrence["id"]),
            entry_occurrence_id=str(entry_occurrence["id"]),
            source_id=str(exit_occurrence["source"]),
            exit_path=exit_path,
            entry_path=entry_path,
            common_parent_path=exit_path[:-1] if direct_siblings else (),
            direct_copy_siblings=direct_siblings,
        )

    @staticmethod
    def _path(occurrence: Any) -> tuple[int, ...]:
        path = occurrence["path"]
        if not isinstance(path, (list, tuple)) or any(
            isinstance(index, bool) or not isinstance(index, int) or index < 0
            for index in path
        ):
            raise ValueError("occurrence has an invalid checked copy path")
        return tuple(path)

    @staticmethod
    def _angle_edges(angle: Any) -> tuple[tuple[int, int], ...]:
        return tuple(
            sorted(
                (
                    pair.left_incidence_index,
                    pair.right_incidence_index,
                )
                for pair in angle.relation
            )
        )

    @staticmethod
    def _source_edges(
        angle: Any,
        incidences: tuple[Any, ...],
    ) -> tuple[tuple[str, str], ...]:
        return tuple(
            sorted(
                {
                    (
                        str(
                            incidences[pair.left_incidence_index]["occurrence"][
                                "source"
                            ]
                        ),
                        str(
                            incidences[pair.right_incidence_index]["occurrence"][
                                "source"
                            ]
                        ),
                    )
                    for pair in angle.relation
                }
            )
        )

    @classmethod
    def _cycle(
        cls,
        angles: dict[str, tuple[tuple[int, int], ...]],
        connectors: dict[TriadicDomainV0, tuple[tuple[int, int], ...]],
    ) -> tuple[tuple[int, int], ...]:
        return cls._compose(
            connectors[TriadicDomainV0.CONSTRUCTION],
            cls._compose(
                angles["tk"],
                cls._compose(
                    connectors[TriadicDomainV0.TIME],
                    cls._compose(
                        angles["xt"],
                        cls._compose(
                            connectors[TriadicDomainV0.SPACE],
                            angles["kx"],
                        ),
                    ),
                ),
            ),
        )

    @staticmethod
    def _compose(
        after: tuple[tuple[Any, Any], ...],
        before: tuple[tuple[Any, Any], ...],
    ) -> tuple[tuple[Any, Any], ...]:
        return tuple(
            sorted(
                {
                    (source, target)
                    for source, middle in before
                    for candidate, target in after
                    if middle == candidate
                }
            )
        )

    @staticmethod
    def _quotient_class(
        domain: TriadicDomainV0,
        incidences: tuple[Any, ...],
    ) -> SourceQuotientClassV0:
        selected = tuple(
            (index, incidence)
            for index, incidence in enumerate(incidences)
            if TriadicDomainV0(incidence["domain"]) is domain
        )
        sources = {
            str(incidence["occurrence"]["source"])
            for _index, incidence in selected
        }
        if len(selected) != 2 or len(sources) != 1:
            raise ValueError("source quotient requires one two-occurrence domain fibre")
        return SourceQuotientClassV0(
            domain=domain,
            source_id=next(iter(sources)),
            incidence_indices=tuple(index for index, _incidence in selected),
            occurrence_ids=tuple(
                str(incidence["occurrence"]["id"])
                for _index, incidence in selected
            ),
            occurrence_paths=tuple(
                tuple(int(item) for item in incidence["occurrence"]["path"])
                for _index, incidence in selected
            ),
        )

    @staticmethod
    def _satisfied(
        layer: ConnectorCalibrationLayerV0,
        reason: str,
    ) -> ConnectorCalibrationRecordV0:
        return ConnectorCalibrationRecordV0(
            layer=layer,
            outcome=LayerOutcomeV0.SATISFIED,
            reason=reason,
        )

    def _finish(
        self,
        code: ResearchCodeV0,
        request: TriangularThroughRequestV0,
        triangle: TriangularThroughArtifactV0,
        verdict: ExperimentVerdictV0,
        reason: str,
        validation: list[ConnectorCalibrationRecordV0],
        failed_layer: ConnectorCalibrationLayerV0 | None = None,
        *,
        boundaries: tuple[SameDomainBoundaryV0, ...] = (),
        trials: tuple[ConnectorTrialV0, ...] = (),
        quotient_classes: tuple[SourceQuotientClassV0, ...] = (),
    ) -> ConnectorCalibrationArtifactV0:
        if failed_layer is not None:
            validation.append(
                ConnectorCalibrationRecordV0(
                    layer=failed_layer,
                    outcome=LayerOutcomeV0.FAILED,
                    reason=reason,
                )
            )
        present = {record.layer for record in validation}
        for layer in self._LAYERS:
            if layer not in present:
                validation.append(
                    ConnectorCalibrationRecordV0(
                        layer=layer,
                        outcome=LayerOutcomeV0.BLOCKED,
                        reason="blocked by an earlier connector validation gate",
                    )
                )
        validation.sort(key=lambda record: self._LAYERS.index(record.layer))
        return ConnectorCalibrationArtifactV0(
            code=code,
            request=request,
            verdict=verdict,
            reason=reason,
            validation=tuple(validation),
            triangle=triangle,
            boundaries=boundaries,
            quotient_classes=quotient_classes,
            trials=trials,
        )
