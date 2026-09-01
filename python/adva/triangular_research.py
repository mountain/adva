"""One-compilation calibration of all three local through angles.

This module remains a nonauthoritative research companion.  It reuses exact
Rust cut, slice, graft, occurrence, and ancestry artifacts.  Its refusal to
close the three local relations without same-domain connectors is evidence,
not a stable global-closure theorem.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, ClassVar

from .core import KernelFunction, TriadicDomainV0, link_modules
from .research import (
    CandidateThroughPresentationV0,
    ExperimentVerdictV0,
    InterpretationCellV0,
    LayerOutcomeV0,
    MultiHoleThroughMachineV0,
    ResearchCodeV0,
    ResearchMachineV0,
    ThroughPairV0,
)


class TriangleValidationLayerV0(StrEnum):
    """Ordered gates for the first single-diagram three-angle calibration."""

    RUST_ORIGIN = "rust_origin"
    SIX_HOLE_CONFIGURATION = "six_hole_configuration"
    THREE_ANGLES = "three_angles"
    OCCURRENCE_CONSERVATION = "occurrence_conservation"
    SCHEDULE_INDEPENDENCE = "schedule_independence"
    RESIDUAL_RETENTION = "residual_retention"
    LOCAL_DUALITY = "local_duality"
    GLOBAL_CLOSURE = "global_closure"
    PROMOTION_BOUNDARY = "promotion_boundary"


@dataclass(frozen=True, slots=True)
class TriangleValidationRecordV0:
    """One Python research gate outcome; never a Rust certificate."""

    layer: TriangleValidationLayerV0
    outcome: LayerOutcomeV0
    reason: str


@dataclass(frozen=True, slots=True)
class TriangularThroughRequestV0:
    """Select the six-hole parent, its pair gates, and alternative schedules."""

    configuration_callee_module: str
    configuration_callee_function: str
    pair_callee_module: str
    pair_callee_function: str
    alternative_schedules: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        names = (
            self.configuration_callee_module,
            self.configuration_callee_function,
            self.pair_callee_module,
            self.pair_callee_function,
        )
        if any(not isinstance(name, str) or not name for name in names):
            raise ValueError("triangle calibration requires two qualified callees")
        if (
            not isinstance(self.alternative_schedules, tuple)
            or not self.alternative_schedules
            or any(not isinstance(schedule, tuple) for schedule in self.alternative_schedules)
        ):
            raise ValueError("triangle calibration requires alternative schedule tuples")
        for schedule in self.alternative_schedules:
            if any(
                isinstance(event, bool) or not isinstance(event, int) or event < 0
                for event in schedule
            ):
                raise ValueError("alternative schedules require non-negative node ids")
            if len(set(schedule)) != len(schedule):
                raise ValueError("an alternative schedule repeats an event")


@dataclass(frozen=True, slots=True)
class GlobalClosureObstructionV0:
    """Exact reason the three local angles do not yet form a circular map."""

    verdict: ExperimentVerdictV0
    raw_cycle_relation: tuple[tuple[int, int], ...]
    missing_connector_domains: tuple[TriadicDomainV0, ...]
    same_domain_connectors_authorized: bool = False
    global_closure_authorized: bool = False


@dataclass(frozen=True, slots=True)
class TriangularThroughArtifactV0:
    """All bounded evidence from one compilation of the triangular fixture."""

    code: ResearchCodeV0
    request: TriangularThroughRequestV0
    verdict: ExperimentVerdictV0
    reason: str
    validation: tuple[TriangleValidationRecordV0, ...]
    cells: tuple[InterpretationCellV0, ...]
    configuration_frame_id: str | None
    angles: tuple[CandidateThroughPresentationV0, ...]
    used_lower_incidence_indices: tuple[int, ...]
    closure: GlobalClosureObstructionV0 | None


class TriangularThroughMachineV0:
    """Derive all three local angles from one function and one exact slice."""

    _LAYERS: ClassVar[tuple[TriangleValidationLayerV0, ...]] = tuple(
        TriangleValidationLayerV0
    )
    _ANGLE_ORDER: ClassVar[
        tuple[tuple[TriadicDomainV0, TriadicDomainV0, TriadicDomainV0], ...]
    ] = (
        (
            TriadicDomainV0.CONSTRUCTION,
            TriadicDomainV0.SPACE,
            TriadicDomainV0.TIME,
        ),
        (
            TriadicDomainV0.SPACE,
            TriadicDomainV0.TIME,
            TriadicDomainV0.CONSTRUCTION,
        ),
        (
            TriadicDomainV0.TIME,
            TriadicDomainV0.CONSTRUCTION,
            TriadicDomainV0.SPACE,
        ),
    )

    def run(
        self,
        code: ResearchCodeV0,
        request: TriangularThroughRequestV0,
    ) -> TriangularThroughArtifactV0:
        validation: list[TriangleValidationRecordV0] = []
        if code.feedback is not None:
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                "the triangle consumes one static interval, not replay feedback",
                validation,
                TriangleValidationLayerV0.RUST_ORIGIN,
            )
        if code.fuel is not None and code.fuel < len(code.schedule):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.FUEL_EXHAUSTED,
                "fuel ended before the triangular interval completed",
                validation,
                TriangleValidationLayerV0.RUST_ORIGIN,
            )

        try:
            function = link_modules(code.sources).function(code.module, code.function)
            primary = ResearchMachineV0._run_epoch(function, code, 0, code.schedule)
        except (TypeError, ValueError) as error:
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                f"Rust rejected the triangular fixture: {error}",
                validation,
                TriangleValidationLayerV0.RUST_ORIGIN,
            )

        trace = function.graft_trace
        transition_checks = (
            "diagram_integrity",
            "slice_revalidated",
            "total_triadic_policy",
            "exact_incidence_partition",
            "lineage_ancestry",
            "complete_slice_residual",
            "original_id_preservation",
            "graft_frame_consistency",
        )
        graft_checks = (
            "diagram_integrity",
            "deterministic_frame_ids",
            "parent_child_nesting",
            "ordered_hole_bindings",
            "argument_body_regions",
            "boundary_maps",
            "call_history_links",
        )
        if (
            trace is None
            or any(
                primary.transition_certificate.get(field) != "checked"
                for field in transition_checks
            )
            or any(trace.certificate.get(field) != "checked" for field in graft_checks)
        ):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                "the fixture lacks a complete Rust transition and graft trace",
                validation,
                TriangleValidationLayerV0.RUST_ORIGIN,
                cells=(primary,),
            )
        validation.append(
            self._satisfied(
                TriangleValidationLayerV0.RUST_ORIGIN,
                "one KernelFunction supplied every exact interface, slice, and graft identity",
            )
        )

        configurations = tuple(
            frame
            for frame in trace.result.frames
            if frame.get("kind") == "call"
            and self._matches(
                frame,
                request.configuration_callee_module,
                request.configuration_callee_function,
            )
        )
        if len(configurations) != 1:
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                "the six-hole configuration callee must select exactly one frame",
                validation,
                TriangleValidationLayerV0.SIX_HOLE_CONFIGURATION,
                cells=(primary,),
            )
        configuration = configurations[0]
        pair_frames = tuple(
            frame
            for frame in trace.result.frames
            if frame.get("kind") == "call"
            and frame.get("parent") == configuration["id"]
            and self._matches(
                frame,
                request.pair_callee_module,
                request.pair_callee_function,
            )
        )
        holes = tuple(
            sorted(configuration["holes"], key=lambda hole: int(hole["hole_index"]))
        )
        lower_wires = tuple(
            item["wire"] for item in primary.lower_interface.cut["frontier"]
        )
        entry_matches = tuple(
            sum(wire == hole["entry_wire"] for wire in lower_wires) for hole in holes
        )
        pair_body_sets = tuple(
            frozenset(int(event) for event in frame["body_region"]) for frame in pair_frames
        )
        configuration_body = frozenset(
            int(event) for event in configuration["body_region"]
        )
        pair_body_union = frozenset().union(*pair_body_sets) if pair_body_sets else frozenset()
        pair_bodies_disjoint = sum(len(events) for events in pair_body_sets) == len(
            pair_body_union
        )
        if (
            len(holes) != 6
            or tuple(int(hole["hole_index"]) for hole in holes) != tuple(range(6))
            or entry_matches != (1, 1, 1, 1, 1, 1)
            or len(pair_frames) != 3
            or any(len(frame["holes"]) != 2 for frame in pair_frames)
            or any(not events for events in pair_body_sets)
            or not pair_bodies_disjoint
            or pair_body_union != configuration_body
        ):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                "one six-hole parent must contain three disjoint active two-hole bodies",
                validation,
                TriangleValidationLayerV0.SIX_HOLE_CONFIGURATION,
                cells=(primary,),
                configuration_frame_id=str(configuration["id"]),
            )
        validation.append(
            self._satisfied(
                TriangleValidationLayerV0.SIX_HOLE_CONFIGURATION,
                "six exact copy outputs fill one parent whose body is three pair gates",
            )
        )

        try:
            angles = tuple(
                sorted(
                    (self._build_angle(frame, primary) for frame in pair_frames),
                    key=self._angle_key,
                )
            )
        except (TypeError, ValueError, IndexError) as error:
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                f"an exact pair frame did not form its angle: {error}",
                validation,
                TriangleValidationLayerV0.THREE_ANGLES,
                cells=(primary,),
                configuration_frame_id=str(configuration["id"]),
            )
        actual_types = tuple(
            (angle.left_domain, angle.right_domain, angle.interface_domain)
            for angle in angles
        )
        if actual_types != self._ANGLE_ORDER or any(
            len(angle.relation) != 1 for angle in angles
        ):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                "the three pair frames do not realize the three circular angle types",
                validation,
                TriangleValidationLayerV0.THREE_ANGLES,
                cells=(primary,),
                configuration_frame_id=str(configuration["id"]),
                angles=angles,
            )
        validation.append(
            self._satisfied(
                TriangleValidationLayerV0.THREE_ANGLES,
                "all three opposite-domain fibre products are nonempty exact relations",
            )
        )

        used = tuple(
            incidence
            for angle in angles
            for incidence in (
                *angle.left_incidence_indices,
                *angle.right_incidence_indices,
            )
        )
        use_counts = Counter(used)
        domain_counts = Counter(
            TriadicDomainV0(incidence["domain"])
            for incidence in primary.lower_interface.incidences
        )
        occurrence_ids = tuple(
            str(incidence["occurrence"]["id"])
            for incidence in primary.lower_interface.incidences
        )
        if (
            len(primary.lower_interface.incidences) != 6
            or set(used) != set(range(6))
            or set(use_counts.values()) != {1}
            or domain_counts
            != Counter(
                {
                    TriadicDomainV0.CONSTRUCTION: 2,
                    TriadicDomainV0.SPACE: 2,
                    TriadicDomainV0.TIME: 2,
                }
            )
            or len(set(occurrence_ids)) != 6
        ):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                "the three angles must consume all six copied occurrences exactly once",
                validation,
                TriangleValidationLayerV0.OCCURRENCE_CONSERVATION,
                cells=(primary,),
                configuration_frame_id=str(configuration["id"]),
                angles=angles,
                used_lower_incidence_indices=used,
            )
        validation.append(
            self._satisfied(
                TriangleValidationLayerV0.OCCURRENCE_CONSERVATION,
                "each domain contributes two distinct occurrences and no angle duplicates one",
            )
        )

        schedules = (code.schedule, *request.alternative_schedules)
        if (
            len(set(schedules)) != len(schedules)
            or any(set(schedule) != set(code.schedule) for schedule in schedules)
        ):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                "all schedule controls must be distinct permutations of one event set",
                validation,
                TriangleValidationLayerV0.SCHEDULE_INDEPENDENCE,
                cells=(primary,),
                configuration_frame_id=str(configuration["id"]),
                angles=angles,
                used_lower_incidence_indices=used,
            )
        cells: list[InterpretationCellV0] = [primary]
        try:
            for epoch, schedule in enumerate(request.alternative_schedules, start=1):
                cells.append(ResearchMachineV0._run_epoch(function, code, epoch, schedule))
        except (TypeError, ValueError) as error:
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                f"Rust rejected an alternative schedule: {error}",
                validation,
                TriangleValidationLayerV0.SCHEDULE_INDEPENDENCE,
                cells=tuple(cells),
                configuration_frame_id=str(configuration["id"]),
                angles=angles,
                used_lower_incidence_indices=used,
            )
        if (
            any(cell.observer_transition != primary.observer_transition for cell in cells)
            or any(cell.carrier != primary.carrier for cell in cells)
            or len({cell.trace.event_ids for cell in cells}) != len(cells)
        ):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.COUNTEREXAMPLE,
                "legal schedules failed to share one canonical outer carrier",
                validation,
                TriangleValidationLayerV0.SCHEDULE_INDEPENDENCE,
                cells=tuple(cells),
                configuration_frame_id=str(configuration["id"]),
                angles=angles,
                used_lower_incidence_indices=used,
            )
        validation.append(
            self._satisfied(
                TriangleValidationLayerV0.SCHEDULE_INDEPENDENCE,
                "distinct checked traces inhabit one equal observer transition and slice",
            )
        )

        residual_event_ids = {
            int(event["id"]) for event in primary.carrier.events
        }
        outside_ids = residual_event_ids - set(pair_body_union)
        outside_operations = {
            str(event["operation"]["name"])
            for event in primary.carrier.events
            if int(event["id"]) in outside_ids
        }
        if (
            any(angle.residual is not primary.carrier for angle in angles)
            or not outside_ids
            or not {"constant", "discard"} <= outside_operations
        ):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                "local angle projections did not retain the source-free outer residual",
                validation,
                TriangleValidationLayerV0.RESIDUAL_RETENTION,
                cells=tuple(cells),
                configuration_frame_id=str(configuration["id"]),
                angles=angles,
                used_lower_incidence_indices=used,
            )
        validation.append(
            self._satisfied(
                TriangleValidationLayerV0.RESIDUAL_RETENTION,
                "all angles retain one complete slice with constant-discard outside them",
            )
        )

        if any(
            tuple(
                sorted(
                    (pair.reversed() for pair in angle.converse_relation),
                    key=MultiHoleThroughMachineV0._pair_key,
                )
            )
            != angle.relation
            for angle in angles
        ):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                "one local relational converse failed involutivity",
                validation,
                TriangleValidationLayerV0.LOCAL_DUALITY,
                cells=tuple(cells),
                configuration_frame_id=str(configuration["id"]),
                angles=angles,
                used_lower_incidence_indices=used,
            )
        validation.append(
            self._satisfied(
                TriangleValidationLayerV0.LOCAL_DUALITY,
                "each local angle has an involutive converse without inverse execution",
            )
        )

        kx = self._find_angle(
            angles, TriadicDomainV0.CONSTRUCTION, TriadicDomainV0.SPACE
        )
        xt = self._find_angle(angles, TriadicDomainV0.SPACE, TriadicDomainV0.TIME)
        tk = self._find_angle(
            angles, TriadicDomainV0.TIME, TriadicDomainV0.CONSTRUCTION
        )
        raw_cycle = self._compose_edges(
            self._edges(tk),
            self._compose_edges(self._edges(xt), self._edges(kx)),
        )
        connector_pairs = (
            (
                TriadicDomainV0.SPACE,
                kx.right_incidence_indices,
                xt.left_incidence_indices,
            ),
            (
                TriadicDomainV0.TIME,
                xt.right_incidence_indices,
                tk.left_incidence_indices,
            ),
            (
                TriadicDomainV0.CONSTRUCTION,
                tk.right_incidence_indices,
                kx.left_incidence_indices,
            ),
        )
        missing = tuple(
            domain
            for domain, previous, following in connector_pairs
            if set(previous).isdisjoint(following)
        )
        connector_sources_checked = all(
            self._same_source_distinct_occurrence(primary, previous[0], following[0])
            for _domain, previous, following in connector_pairs
        )
        if raw_cycle or set(missing) != set(TriadicDomainV0) or not connector_sources_checked:
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.COUNTEREXAMPLE,
                "the raw cycle did not expose exactly the three expected sibling connectors",
                validation,
                TriangleValidationLayerV0.GLOBAL_CLOSURE,
                cells=tuple(cells),
                configuration_frame_id=str(configuration["id"]),
                angles=angles,
                used_lower_incidence_indices=used,
            )
        closure = GlobalClosureObstructionV0(
            verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
            raw_cycle_relation=raw_cycle,
            missing_connector_domains=missing,
        )
        validation.append(
            self._satisfied(
                TriangleValidationLayerV0.GLOBAL_CLOSURE,
                "raw exact-incidence composition is empty and refuses three undeclared connectors",
            )
        )

        if (
            closure.same_domain_connectors_authorized
            or closure.global_closure_authorized
            or any(angle.semantic_authority for angle in angles)
            or any(angle.forgetting_authorized for angle in angles)
            or any(angle.through_relation_composition_authorized for angle in angles)
        ):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                "the triangular research artifact crossed its promotion boundary",
                validation,
                TriangleValidationLayerV0.PROMOTION_BOUNDARY,
                cells=tuple(cells),
                configuration_frame_id=str(configuration["id"]),
                angles=angles,
                used_lower_incidence_indices=used,
                closure=closure,
            )
        validation.append(
            self._satisfied(
                TriangleValidationLayerV0.PROMOTION_BOUNDARY,
                "no sibling connector, global closure, forgetting, or stable semantics is authorized",
            )
        )
        return self._finish(
            code,
            request,
            ExperimentVerdictV0.SUPPORTED,
            "three local angles passed while their ungrounded circular closure was refused",
            validation,
            cells=tuple(cells),
            configuration_frame_id=str(configuration["id"]),
            angles=angles,
            used_lower_incidence_indices=used,
            closure=closure,
        )

    def _build_angle(
        self,
        frame: Mapping[str, Any],
        cell: InterpretationCellV0,
    ) -> CandidateThroughPresentationV0:
        holes = tuple(
            sorted(frame["holes"], key=lambda hole: int(hole["hole_index"]))
        )
        if (
            len(holes) != 2
            or tuple(int(hole["hole_index"]) for hole in holes) != (0, 1)
        ):
            raise ValueError("a local angle requires two ordered holes")
        lower_wires = tuple(
            item["wire"] for item in cell.lower_interface.cut["frontier"]
        )
        hole_domains: dict[int, TriadicDomainV0] = {}
        hole_incidences: dict[int, int] = {}
        for hole in holes:
            hole_index = int(hole["hole_index"])
            matches = tuple(
                index
                for index, wire in enumerate(lower_wires)
                if wire == hole["entry_wire"]
            )
            if len(matches) != 1:
                raise ValueError("an angle hole does not reuse one exact lower wire")
            incidences = tuple(
                index
                for index, incidence in enumerate(cell.lower_interface.incidences)
                if int(incidence["cut_wire_index"]) == matches[0]
            )
            if len(incidences) != 1:
                raise ValueError("an angle hole requires one exact occurrence incidence")
            hole_domains[hole_index] = TriadicDomainV0(
                cell.lower_interface.incidences[incidences[0]]["domain"]
            )
            hole_incidences[hole_index] = incidences[0]
        domain_set = set(hole_domains.values())
        specifications = tuple(
            specification
            for specification in self._ANGLE_ORDER
            if {specification[0], specification[1]} == domain_set
        )
        if len(specifications) != 1:
            raise ValueError("two hole domains do not determine one opposite interface")
        left_domain, right_domain, interface_domain = specifications[0]
        left_holes = tuple(
            index for index, domain in hole_domains.items() if domain is left_domain
        )
        right_holes = tuple(
            index for index, domain in hole_domains.items() if domain is right_domain
        )
        left_incidences = tuple(hole_incidences[index] for index in left_holes)
        right_incidences = tuple(hole_incidences[index] for index in right_holes)

        body_events = {int(event) for event in frame["body_region"]}
        residual_events = {int(event["id"]) for event in cell.carrier.events}
        intersections = cell.carrier.graft_intersections
        matching_intersections = (
            ()
            if intersections is None
            else tuple(item for item in intersections if item["frame"] == frame["id"])
        )
        upper_wires = tuple(
            item["wire"] for item in cell.upper_interface.cut["frontier"]
        )
        exit_indices = tuple(
            index
            for exit_wire in frame["exit_wires"]
            for index, wire in enumerate(upper_wires)
            if wire == exit_wire
        )
        if (
            not body_events
            or not body_events <= residual_events
            or len(matching_intersections) != 1
            or {
                int(event) for event in matching_intersections[0]["body_events"]
            }
            != body_events
            or len(exit_indices) != 1
        ):
            raise ValueError("angle body and exit do not inhabit the common slice")

        left_specialization = MultiHoleThroughMachineV0._specialization(
            left_incidences, exit_indices, cell
        )
        right_specialization = MultiHoleThroughMachineV0._specialization(
            right_incidences, exit_indices, cell
        )
        relation = MultiHoleThroughMachineV0._fibre_product(
            left_incidences,
            right_incidences,
            left_specialization,
            right_specialization,
        )
        if (
            not left_specialization
            or not right_specialization
            or len(relation) != 1
        ):
            raise ValueError("angle specializations do not meet on one exact exit")
        middle_indices = tuple(
            sorted(
                {wire for _incidence, wire in left_specialization}
                | {wire for _incidence, wire in right_specialization}
            )
        )
        return CandidateThroughPresentationV0(
            left_domain=left_domain,
            right_domain=right_domain,
            interface_domain=interface_domain,
            frame_id=str(frame["id"]),
            ordered_holes=holes,
            left_hole_indices=left_holes,
            right_hole_indices=right_holes,
            left_incidence_indices=left_incidences,
            right_incidence_indices=right_incidences,
            left_specialization=left_specialization,
            right_specialization=right_specialization,
            middle_upper_wire_indices=middle_indices,
            relation=relation,
            residual=cell.carrier,
        )

    @staticmethod
    def _matches(
        frame: Mapping[str, Any],
        module: str,
        function: str,
    ) -> bool:
        callee = frame.get("callee")
        return (
            isinstance(callee, Mapping)
            and callee.get("module") == module
            and callee.get("function") == function
        )

    @classmethod
    def _angle_key(cls, angle: CandidateThroughPresentationV0) -> int:
        return cls._ANGLE_ORDER.index(
            (angle.left_domain, angle.right_domain, angle.interface_domain)
        )

    @staticmethod
    def _find_angle(
        angles: tuple[CandidateThroughPresentationV0, ...],
        left: TriadicDomainV0,
        right: TriadicDomainV0,
    ) -> CandidateThroughPresentationV0:
        return next(
            angle
            for angle in angles
            if angle.left_domain is left and angle.right_domain is right
        )

    @staticmethod
    def _edges(
        angle: CandidateThroughPresentationV0,
    ) -> tuple[tuple[int, int], ...]:
        return tuple(
            (pair.left_incidence_index, pair.right_incidence_index)
            for pair in angle.relation
        )

    @staticmethod
    def _compose_edges(
        after: tuple[tuple[int, int], ...],
        before: tuple[tuple[int, int], ...],
    ) -> tuple[tuple[int, int], ...]:
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
    def _same_source_distinct_occurrence(
        cell: InterpretationCellV0,
        left_index: int,
        right_index: int,
    ) -> bool:
        left = cell.lower_interface.incidences[left_index]["occurrence"]
        right = cell.lower_interface.incidences[right_index]["occurrence"]
        return left["source"] == right["source"] and left["id"] != right["id"]

    @staticmethod
    def _satisfied(
        layer: TriangleValidationLayerV0,
        reason: str,
    ) -> TriangleValidationRecordV0:
        return TriangleValidationRecordV0(
            layer=layer,
            outcome=LayerOutcomeV0.SATISFIED,
            reason=reason,
        )

    def _finish(
        self,
        code: ResearchCodeV0,
        request: TriangularThroughRequestV0,
        verdict: ExperimentVerdictV0,
        reason: str,
        validation: list[TriangleValidationRecordV0],
        failed_layer: TriangleValidationLayerV0 | None = None,
        *,
        cells: tuple[InterpretationCellV0, ...] = (),
        configuration_frame_id: str | None = None,
        angles: tuple[CandidateThroughPresentationV0, ...] = (),
        used_lower_incidence_indices: tuple[int, ...] = (),
        closure: GlobalClosureObstructionV0 | None = None,
    ) -> TriangularThroughArtifactV0:
        if failed_layer is not None:
            validation.append(
                TriangleValidationRecordV0(
                    layer=failed_layer,
                    outcome=LayerOutcomeV0.FAILED,
                    reason=reason,
                )
            )
        present = {record.layer for record in validation}
        for layer in self._LAYERS:
            if layer not in present:
                validation.append(
                    TriangleValidationRecordV0(
                        layer=layer,
                        outcome=LayerOutcomeV0.BLOCKED,
                        reason="blocked by an earlier triangular validation gate",
                    )
                )
        validation.sort(key=lambda record: self._LAYERS.index(record.layer))
        return TriangularThroughArtifactV0(
            code=code,
            request=request,
            verdict=verdict,
            reason=reason,
            validation=tuple(validation),
            cells=cells,
            configuration_frame_id=configuration_frame_id,
            angles=angles,
            used_lower_incidence_indices=used_lower_incidence_indices,
            closure=closure,
        )
