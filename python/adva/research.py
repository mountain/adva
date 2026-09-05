"""Bounded replay machine over Rust-owned process and observer artifacts.

This module is deliberately a research companion.  It never allocates or
identifies semantic sources, occurrences, wires, cuts, or program events.
`InterpretationCellV0` packages Rust judgments with an explicit schedule;
`FeedbackWitnessV0` records finite replay epochs only and is not a stable
feedback, recursion, trace, or universal-computation semantics.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from enum import StrEnum
from hashlib import sha256
from typing import Any, ClassVar

from .core import (
    KernelFunction,
    ProgramSliceView,
    TriadicCutObservationViewV0,
    TriadicDomainV0,
    TriadicObserverPolicyV0,
    TriadicObserverTransitionViewV0,
    link_modules,
)


class BoundaryMatchV0(StrEnum):
    """The explicitly chosen endpoint comparison for bounded replay."""

    EXACT_FRONTIER = "exact_frontier"
    EXACT_CUT = "exact_cut"


class ExperimentVerdictV0(StrEnum):
    """Finite research outcomes; exhaustion is never a proof of impossibility."""

    SUPPORTED = "supported"
    COUNTEREXAMPLE = "counterexample"
    OBSTRUCTION = "obstruction"
    NOT_REPRESENTABLE = "not_representable"
    FUEL_EXHAUSTED = "fuel_exhausted"


class ThroughValidationLayerV0(StrEnum):
    """Ordered research gates for one grounded multi-hole through candidate."""

    RUST_ORIGIN = "rust_origin"
    INTERFACE_TYPING = "interface_typing"
    ORDERED_HOLES = "ordered_holes"
    SAME_DIAGRAM_IDENTITY = "same_diagram_identity"
    MIDDLE_QUOTIENT = "middle_quotient"
    FIBRE_PRODUCT = "fibre_product"
    RESIDUAL_RETENTION = "residual_retention"
    RELATIONAL_DUALITY = "relational_duality"
    ADJACENT_COMPOSITION = "adjacent_composition"
    PROMOTION_BOUNDARY = "promotion_boundary"


class LayerOutcomeV0(StrEnum):
    """Nonauthoritative outcome of one Python research validation gate."""

    SATISFIED = "satisfied"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class ThroughValidationRecordV0:
    """One auditable gate result; it is not a Rust certificate."""

    layer: ThroughValidationLayerV0
    outcome: LayerOutcomeV0
    reason: str


@dataclass(frozen=True, slots=True)
class MultiHoleThroughRequestV0:
    """Select one checked call frame and one typed circular interface."""

    callee_module: str
    callee_function: str
    left_domain: TriadicDomainV0
    right_domain: TriadicDomainV0
    interface_domain: TriadicDomainV0
    composition_middle: tuple[int, ...] | None = None

    def __post_init__(self) -> None:
        if not self.callee_module or not self.callee_function:
            raise ValueError("a multi-hole through request requires a qualified callee")
        if any(
            not isinstance(domain, TriadicDomainV0)
            for domain in (self.left_domain, self.right_domain, self.interface_domain)
        ):
            raise ValueError("through request domains must be TriadicDomainV0 values")
        if self.composition_middle is not None:
            ResearchCodeV0._check_node_ids(self.composition_middle, "composition_middle")
            if len(set(self.composition_middle)) != len(self.composition_middle):
                raise ValueError("composition_middle repeats a node id")


@dataclass(frozen=True, slots=True)
class ThroughPairV0:
    """One fibre-product pair indexed only into an unchanged Rust artifact."""

    left_incidence_index: int
    right_incidence_index: int
    middle_upper_wire_indices: tuple[int, ...]

    def reversed(self) -> ThroughPairV0:
        return ThroughPairV0(
            left_incidence_index=self.right_incidence_index,
            right_incidence_index=self.left_incidence_index,
            middle_upper_wire_indices=self.middle_upper_wire_indices,
        )


@dataclass(frozen=True, slots=True)
class CandidateThroughPresentationV0:
    """A declared fibre product over one exact upper-cut wire quotient.

    The incidence and wire numbers are coordinates into `cell` and `residual`;
    they are not newly allocated semantic identities.
    """

    left_domain: TriadicDomainV0
    right_domain: TriadicDomainV0
    interface_domain: TriadicDomainV0
    frame_id: str
    ordered_holes: tuple[Mapping[str, Any], ...]
    left_hole_indices: tuple[int, ...]
    right_hole_indices: tuple[int, ...]
    left_incidence_indices: tuple[int, ...]
    right_incidence_indices: tuple[int, ...]
    left_specialization: tuple[tuple[int, int], ...]
    right_specialization: tuple[tuple[int, int], ...]
    middle_upper_wire_indices: tuple[int, ...]
    relation: tuple[ThroughPairV0, ...]
    residual: ProgramSliceView
    middle_quotient: str = "upper_cut_wire_index"
    semantic_authority: bool = False
    forgetting_authorized: bool = False
    active_normalization_authorized: bool = False
    through_relation_composition_authorized: bool = False
    universal_computation_authorized: bool = False

    @property
    def converse_relation(self) -> tuple[ThroughPairV0, ...]:
        return tuple(
            sorted(
                (pair.reversed() for pair in self.relation),
                key=lambda pair: (
                    pair.left_incidence_index,
                    pair.right_incidence_index,
                    pair.middle_upper_wire_indices,
                ),
            )
        )

    @property
    def is_total_function_from_left(self) -> bool:
        return all(
            sum(pair.left_incidence_index == incidence for pair in self.relation) == 1
            for incidence in self.left_incidence_indices
        )


@dataclass(frozen=True, slots=True)
class MultiHoleThroughArtifactV0:
    """Layered finite evidence for one candidate through presentation."""

    code: ResearchCodeV0
    request: MultiHoleThroughRequestV0
    verdict: ExperimentVerdictV0
    reason: str
    validation: tuple[ThroughValidationRecordV0, ...]
    cell: InterpretationCellV0 | None
    candidate: CandidateThroughPresentationV0 | None
    adjacent_composition_certificate: Mapping[str, Any] | None


@dataclass(frozen=True, slots=True)
class FeedbackRequestV0:
    """Request repeated finite replay after one declared boundary comparison."""

    epochs: int
    boundary_match: BoundaryMatchV0 = BoundaryMatchV0.EXACT_FRONTIER

    def __post_init__(self) -> None:
        if isinstance(self.epochs, bool) or not isinstance(self.epochs, int) or self.epochs < 2:
            raise ValueError("feedback replay requires at least two epochs")
        if not isinstance(self.boundary_match, BoundaryMatchV0):
            raise ValueError("boundary_match must be a BoundaryMatchV0 value")


@dataclass(frozen=True, slots=True)
class ResearchCodeV0:
    """Serializable input for one bounded, Rust-grounded research run."""

    SCHEMA: ClassVar[str] = "adva.research-code"
    VERSION: ClassVar[int] = 0

    sources: tuple[str, ...]
    module: str
    function: str
    input_domains: tuple[TriadicDomainV0, ...]
    schedule: tuple[int, ...]
    initial_completed: tuple[int, ...] = ()
    fuel: int | None = None
    feedback: FeedbackRequestV0 | None = None

    def __post_init__(self) -> None:
        if (
            not isinstance(self.sources, tuple)
            or not self.sources
            or any(not isinstance(source, str) for source in self.sources)
        ):
            raise ValueError("research code requires at least one Lisp source")
        if not isinstance(self.module, str) or not isinstance(self.function, str):
            raise ValueError("research code module and function must be strings")
        if not self.module or not self.function:
            raise ValueError("research code requires a module and function name")
        TriadicObserverPolicyV0(self.input_domains)
        if not isinstance(self.initial_completed, tuple) or not isinstance(self.schedule, tuple):
            raise ValueError("initial_completed and schedule must be tuples")
        self._check_node_ids(self.initial_completed, "initial_completed")
        self._check_node_ids(self.schedule, "schedule")
        if len(set(self.initial_completed)) != len(self.initial_completed):
            raise ValueError("initial_completed repeats a node id")
        if len(set(self.schedule)) != len(self.schedule):
            raise ValueError("one replay epoch cannot cross the same event twice")
        if self.fuel is not None and (
            isinstance(self.fuel, bool) or not isinstance(self.fuel, int) or self.fuel < 0
        ):
            raise ValueError("fuel must be a non-negative integer or None")
        if self.feedback is not None and not isinstance(self.feedback, FeedbackRequestV0):
            raise ValueError("feedback must be a FeedbackRequestV0 value or None")
        if self.feedback is not None and not self.schedule:
            raise ValueError("feedback replay requires a nonempty schedule")

    @staticmethod
    def _check_node_ids(nodes: tuple[int, ...], field: str) -> None:
        if any(isinstance(node, bool) or not isinstance(node, int) or node < 0 for node in nodes):
            raise ValueError(f"{field} must contain non-negative node ids")

    @property
    def policy(self) -> TriadicObserverPolicyV0:
        return TriadicObserverPolicyV0(self.input_domains)

    def to_dict(self) -> dict[str, Any]:
        feedback = None
        if self.feedback is not None:
            feedback = {
                "epochs": self.feedback.epochs,
                "boundary_match": self.feedback.boundary_match.value,
            }
        return {
            "schema": self.SCHEMA,
            "version": self.VERSION,
            "sources": list(self.sources),
            "module": self.module,
            "function": self.function,
            "input_domains": [domain.value for domain in self.input_domains],
            "schedule": list(self.schedule),
            "initial_completed": list(self.initial_completed),
            "fuel": self.fuel,
            "feedback": feedback,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    @classmethod
    def from_json(cls, encoded: str) -> ResearchCodeV0:
        raw = json.loads(encoded)
        if not isinstance(raw, dict):
            raise ValueError("research code must be a JSON object")
        expected = {
            "schema",
            "version",
            "sources",
            "module",
            "function",
            "input_domains",
            "schedule",
            "initial_completed",
            "fuel",
            "feedback",
        }
        if set(raw) != expected:
            raise ValueError("research code fields do not match schema version 0")
        if raw["schema"] != cls.SCHEMA or raw["version"] != cls.VERSION:
            raise ValueError("unsupported research code schema or version")
        feedback_raw = raw["feedback"]
        feedback = None
        if feedback_raw is not None:
            if not isinstance(feedback_raw, dict) or set(feedback_raw) != {
                "epochs",
                "boundary_match",
            }:
                raise ValueError("feedback fields do not match schema version 0")
            epochs_raw = feedback_raw["epochs"]
            boundary_match_raw = feedback_raw["boundary_match"]
            if isinstance(epochs_raw, bool) or not isinstance(epochs_raw, int):
                raise ValueError("feedback epochs must be a JSON integer")
            if not isinstance(boundary_match_raw, str):
                raise ValueError("feedback boundary_match must be a JSON string")
            feedback = FeedbackRequestV0(
                epochs=epochs_raw,
                boundary_match=BoundaryMatchV0(boundary_match_raw),
            )
        sources = raw["sources"]
        domains = raw["input_domains"]
        schedule = raw["schedule"]
        initial_completed = raw["initial_completed"]
        sequence_values = (sources, domains, schedule, initial_completed)
        if not all(isinstance(items, list) for items in sequence_values):
            raise ValueError("research code sequence fields must be JSON arrays")
        if any(not isinstance(source, str) for source in sources):
            raise ValueError("research code sources must be JSON strings")
        if any(not isinstance(domain, str) for domain in domains):
            raise ValueError("input_domains must be JSON strings")
        for field, values in (
            ("schedule", schedule),
            ("initial_completed", initial_completed),
        ):
            if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
                raise ValueError(f"{field} must contain JSON integers")
        if not isinstance(raw["module"], str) or not isinstance(raw["function"], str):
            raise ValueError("research code module and function must be JSON strings")
        fuel_raw = raw["fuel"]
        if fuel_raw is not None and (isinstance(fuel_raw, bool) or not isinstance(fuel_raw, int)):
            raise ValueError("fuel must be a JSON integer or null")
        return cls(
            sources=tuple(sources),
            module=raw["module"],
            function=raw["function"],
            input_domains=tuple(TriadicDomainV0(domain) for domain in domains),
            schedule=tuple(schedule),
            initial_completed=tuple(initial_completed),
            fuel=fuel_raw,
            feedback=feedback,
        )


@dataclass(frozen=True, slots=True)
class TriadicInterfaceV0:
    """A named endpoint view copied without relabeling from one Rust artifact."""

    cut: Mapping[str, Any]
    incidences: tuple[Mapping[str, Any], ...]
    source_free_wire_indices: tuple[int, ...]
    opposite_pair_views: tuple[Mapping[str, Any], ...]

    @classmethod
    def from_checked(cls, observation: TriadicCutObservationViewV0) -> TriadicInterfaceV0:
        return cls(
            cut=observation.cut,
            incidences=observation.incidences,
            source_free_wire_indices=observation.source_free_wire_indices,
            opposite_pair_views=observation.opposite_pair_views,
        )


@dataclass(frozen=True, slots=True)
class EpochEventRefV0:
    """Research-run occurrence of one unchanged static Rust event."""

    epoch: int
    ordinal: int
    event: int


@dataclass(frozen=True, slots=True)
class ThroughStepV0:
    """One Rust-certified causal advance plus its nonsemantic epoch reference."""

    ref: EpochEventRefV0
    before: Mapping[str, Any]
    after: Mapping[str, Any]
    consumed: tuple[Mapping[str, Any], ...]
    produced: tuple[Mapping[str, Any], ...]
    certificate: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class ThroughTraceV0:
    """A chosen linear schedule, kept separate from the canonical slice."""

    epoch: int
    steps: tuple[ThroughStepV0, ...]

    @property
    def event_ids(self) -> tuple[int, ...]:
        return tuple(step.ref.event for step in self.steps)


@dataclass(frozen=True, slots=True)
class InterpretationCellV0:
    """One triadic interface transition with exact carrier and chosen trace."""

    epoch: int
    lower_interface: TriadicInterfaceV0
    carrier: ProgramSliceView
    trace: ThroughTraceV0
    upper_interface: TriadicInterfaceV0
    observer_transition: TriadicObserverTransitionViewV0
    transition_certificate: Mapping[str, Any]

    @property
    def residual_event_ids(self) -> tuple[int, ...]:
        return tuple(int(node["id"]) for node in self.carrier.events)


@dataclass(frozen=True, slots=True)
class FeedbackWitnessV0:
    """Finite endpoint-matched replay, never stable semantic feedback."""

    boundary_match: BoundaryMatchV0
    epoch_count: int
    epoch_event_refs: tuple[tuple[EpochEventRefV0, ...], ...]
    residual_event_ids: tuple[int, ...]
    semantic_feedback_authorized: bool = False


@dataclass(frozen=True, slots=True)
class RunArtifactV0:
    """Replayable research result containing every exact Rust residual."""

    SCHEMA: ClassVar[str] = "adva.research-run"
    VERSION: ClassVar[int] = 0

    code: ResearchCodeV0
    verdict: ExperimentVerdictV0
    reason: str
    cells: tuple[InterpretationCellV0, ...]
    feedback: FeedbackWitnessV0 | None
    remaining_schedule: tuple[int, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "version": self.VERSION,
            "artifact": asdict(self),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    @property
    def replay_digest(self) -> str:
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return sha256(canonical.encode("utf-8")).hexdigest()


class ResearchMachineV0:
    """Run finite schedules through Rust and package the three-layer evidence."""

    def run(self, code: ResearchCodeV0) -> RunArtifactV0:
        try:
            function = link_modules(code.sources).function(code.module, code.function)
        except (TypeError, ValueError) as error:
            return self._artifact(
                code,
                ExperimentVerdictV0.OBSTRUCTION,
                f"Rust rejected the research program: {error}",
            )

        epoch_target = code.feedback.epochs if code.feedback is not None else 1
        fuel = code.fuel
        cells: list[InterpretationCellV0] = []
        for epoch in range(epoch_target):
            available = len(code.schedule) if fuel is None else min(fuel, len(code.schedule))
            attempted = code.schedule[:available]
            try:
                cell = self._run_epoch(function, code, epoch, attempted)
            except (TypeError, ValueError) as error:
                return self._artifact(
                    code,
                    ExperimentVerdictV0.OBSTRUCTION,
                    f"Rust rejected the schedule: {error}",
                    cells=tuple(cells),
                    remaining_schedule=code.schedule,
                )
            cells.append(cell)
            if fuel is not None:
                fuel -= available
            if available < len(code.schedule):
                return self._artifact(
                    code,
                    ExperimentVerdictV0.FUEL_EXHAUSTED,
                    "fuel ended before the declared schedule completed",
                    cells=tuple(cells),
                    remaining_schedule=code.schedule[available:],
                )
            if code.feedback is not None:
                verdict, reason = self._check_feedback_boundary(cell, code.feedback)
                if verdict is not ExperimentVerdictV0.SUPPORTED:
                    return self._artifact(
                        code,
                        verdict,
                        reason,
                        cells=tuple(cells),
                    )

        feedback = None
        if code.feedback is not None:
            feedback = FeedbackWitnessV0(
                boundary_match=code.feedback.boundary_match,
                epoch_count=len(cells),
                epoch_event_refs=tuple(
                    tuple(step.ref for step in cell.trace.steps) for cell in cells
                ),
                residual_event_ids=cells[0].residual_event_ids,
            )
        return self._artifact(
            code,
            ExperimentVerdictV0.SUPPORTED,
            "the declared finite run is backed by Rust cuts, steps, slices, and observations",
            cells=tuple(cells),
            feedback=feedback,
        )

    @staticmethod
    def _run_epoch(
        function: KernelFunction,
        code: ResearchCodeV0,
        epoch: int,
        schedule: tuple[int, ...],
    ) -> InterpretationCellV0:
        completed = tuple(code.initial_completed)
        steps: list[ThroughStepV0] = []
        for ordinal, event in enumerate(schedule):
            step = function.advance_causal_cut(completed, event)
            steps.append(
                ThroughStepV0(
                    ref=EpochEventRefV0(epoch=epoch, ordinal=ordinal, event=event),
                    before=step.before,
                    after=step.after,
                    consumed=step.consumed,
                    produced=step.produced,
                    certificate=step.certificate,
                )
            )
            completed = tuple(step.after["completed"])

        transition = function.triadic_observer_transition_v0(
            code.policy, code.initial_completed, completed
        )
        trace = ThroughTraceV0(epoch=epoch, steps=tuple(steps))
        carrier_ids = tuple(int(node["id"]) for node in transition.result.slice.events)
        if set(carrier_ids) != set(trace.event_ids):
            raise ValueError("chosen schedule and exact slice residual disagree")
        return InterpretationCellV0(
            epoch=epoch,
            lower_interface=TriadicInterfaceV0.from_checked(transition.result.lower),
            carrier=transition.result.slice,
            trace=trace,
            upper_interface=TriadicInterfaceV0.from_checked(transition.result.upper),
            observer_transition=transition.result,
            transition_certificate=transition.certificate,
        )

    @staticmethod
    def _check_feedback_boundary(
        cell: InterpretationCellV0, request: FeedbackRequestV0
    ) -> tuple[ExperimentVerdictV0, str]:
        lower_cut = cell.lower_interface.cut
        upper_cut = cell.upper_interface.cut
        if request.boundary_match is BoundaryMatchV0.EXACT_CUT:
            if lower_cut != upper_cut:
                return (
                    ExperimentVerdictV0.NOT_REPRESENTABLE,
                    "a nonempty finite DAG interval cannot return to the same exact cut",
                )
            return (
                ExperimentVerdictV0.OBSTRUCTION,
                "the only exact cut return is an empty identity interval",
            )
        if lower_cut["frontier"] != upper_cut["frontier"]:
            return (
                ExperimentVerdictV0.OBSTRUCTION,
                "the declared schedule does not return under exact-frontier observation",
            )
        return (
            ExperimentVerdictV0.SUPPORTED,
            "exact frontiers match while the complete ProgramSlice remains residual",
        )

    @staticmethod
    def _artifact(
        code: ResearchCodeV0,
        verdict: ExperimentVerdictV0,
        reason: str,
        *,
        cells: tuple[InterpretationCellV0, ...] = (),
        feedback: FeedbackWitnessV0 | None = None,
        remaining_schedule: tuple[int, ...] = (),
    ) -> RunArtifactV0:
        return RunArtifactV0(
            code=code,
            verdict=verdict,
            reason=reason,
            cells=cells,
            feedback=feedback,
            remaining_schedule=remaining_schedule,
        )


class MultiHoleThroughMachineV0:
    """Test one multi-hole angle form against exact same-diagram evidence.

    This adapter derives candidates only.  The Rust transition, graft trace,
    and slice remain the authorities; a successful Python report is not a
    certificate and cannot be submitted to the kernel as semantic input.
    """

    _LAYERS: ClassVar[tuple[ThroughValidationLayerV0, ...]] = tuple(ThroughValidationLayerV0)

    def run(
        self,
        code: ResearchCodeV0,
        request: MultiHoleThroughRequestV0,
    ) -> MultiHoleThroughArtifactV0:
        validation: list[ThroughValidationRecordV0] = []
        if code.feedback is not None:
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                "a through adapter consumes one finite cell, not replay feedback",
                validation,
                ThroughValidationLayerV0.RUST_ORIGIN,
            )
        if code.fuel is not None and code.fuel < len(code.schedule):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.FUEL_EXHAUSTED,
                "fuel ended before the complete candidate interval was available",
                validation,
                ThroughValidationLayerV0.RUST_ORIGIN,
            )

        try:
            function = link_modules(code.sources).function(code.module, code.function)
            cell = ResearchMachineV0._run_epoch(function, code, 0, code.schedule)
        except (TypeError, ValueError) as error:
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                f"Rust rejected the candidate experiment: {error}",
                validation,
                ThroughValidationLayerV0.RUST_ORIGIN,
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
                cell.transition_certificate.get(field) != "checked" for field in transition_checks
            )
            or any(trace.certificate.get(field) != "checked" for field in graft_checks)
        ):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                "the candidate lacks a complete Rust transition and compiler graft trace",
                validation,
                ThroughValidationLayerV0.RUST_ORIGIN,
                cell=cell,
            )
        validation.append(
            self._satisfied(
                ThroughValidationLayerV0.RUST_ORIGIN,
                "Rust rederived the cut, slice, ancestry, and certified graft trace",
            )
        )

        if len({request.left_domain, request.right_domain, request.interface_domain}) != 3:
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                "the interface type must be the unique domain opposite its two charts",
                validation,
                ThroughValidationLayerV0.INTERFACE_TYPING,
                cell=cell,
            )
        validation.append(
            self._satisfied(
                ThroughValidationLayerV0.INTERFACE_TYPING,
                "the two chart domains are distinct and the interface has the unique opposite type",
            )
        )

        frames = tuple(
            frame
            for frame in trace.result.frames
            if frame.get("kind") == "call" and self._matches_callee(frame, request)
        )
        if len(frames) != 1:
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                "the qualified callee must select exactly one checked call frame",
                validation,
                ThroughValidationLayerV0.ORDERED_HOLES,
                cell=cell,
            )
        frame = frames[0]
        holes = tuple(sorted(frame["holes"], key=lambda hole: int(hole["hole_index"])))
        if len(holes) < 2 or tuple(int(hole["hole_index"]) for hole in holes) != tuple(
            range(len(holes))
        ):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                "the selected frame does not expose a finite contiguous ordered-hole boundary",
                validation,
                ThroughValidationLayerV0.ORDERED_HOLES,
                cell=cell,
            )

        lower_wires = tuple(item["wire"] for item in cell.lower_interface.cut["frontier"])
        hole_domains: dict[int, TriadicDomainV0] = {}
        hole_incidences: dict[int, tuple[int, ...]] = {}
        for hole in holes:
            hole_index = int(hole["hole_index"])
            matches = tuple(
                index for index, wire in enumerate(lower_wires) if wire == hole["entry_wire"]
            )
            if len(matches) != 1:
                return self._finish(
                    code,
                    request,
                    ExperimentVerdictV0.NOT_REPRESENTABLE,
                    "every ordered hole must reuse exactly one lower-cut wire",
                    validation,
                    ThroughValidationLayerV0.ORDERED_HOLES,
                    cell=cell,
                )
            cut_wire_index = matches[0]
            incidences = tuple(
                index
                for index, incidence in enumerate(cell.lower_interface.incidences)
                if int(incidence["cut_wire_index"]) == cut_wire_index
            )
            domains = {
                TriadicDomainV0(cell.lower_interface.incidences[index]["domain"])
                for index in incidences
            }
            if not incidences or len(domains) != 1:
                return self._finish(
                    code,
                    request,
                    ExperimentVerdictV0.NOT_REPRESENTABLE,
                    "one selected hole must carry a nonempty incidence fibre from one chart domain",
                    validation,
                    ThroughValidationLayerV0.ORDERED_HOLES,
                    cell=cell,
                )
            hole_domains[hole_index] = domains.pop()
            hole_incidences[hole_index] = incidences

        if set(hole_domains.values()) != {request.left_domain, request.right_domain}:
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                "the selected holes must be filled by both and only the two interface charts",
                validation,
                ThroughValidationLayerV0.ORDERED_HOLES,
                cell=cell,
            )
        left_holes = tuple(
            index for index, domain in hole_domains.items() if domain is request.left_domain
        )
        right_holes = tuple(
            index for index, domain in hole_domains.items() if domain is request.right_domain
        )
        left_incidences = tuple(
            incidence for hole in left_holes for incidence in hole_incidences[hole]
        )
        right_incidences = tuple(
            incidence for hole in right_holes for incidence in hole_incidences[hole]
        )
        validation.append(
            self._satisfied(
                ThroughValidationLayerV0.ORDERED_HOLES,
                "exact graft bindings classify every ordered hole into one of the "
                "two chart carriers",
            )
        )

        residual_event_ids = {int(event["id"]) for event in cell.carrier.events}
        body_event_ids = {int(event) for event in frame["body_region"]}
        intersections = cell.carrier.graft_intersections
        frame_intersections = (
            ()
            if intersections is None
            else tuple(item for item in intersections if item["frame"] == frame["id"])
        )
        upper_wires = tuple(item["wire"] for item in cell.upper_interface.cut["frontier"])
        exit_wire_indices = tuple(
            index
            for exit_wire in frame["exit_wires"]
            for index, wire in enumerate(upper_wires)
            if wire == exit_wire
        )
        if (
            not body_event_ids
            or not body_event_ids <= residual_event_ids
            or len(frame_intersections) != 1
            or set(int(event) for event in frame_intersections[0]["body_events"]) != body_event_ids
            or len(exit_wire_indices) != len(frame["exit_wires"])
        ):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                "the frame boundary and active body must remain literal parts of the same slice",
                validation,
                ThroughValidationLayerV0.SAME_DIAGRAM_IDENTITY,
                cell=cell,
            )
        validation.append(
            self._satisfied(
                ThroughValidationLayerV0.SAME_DIAGRAM_IDENTITY,
                "hole wires, body events, exit wires, and graft intersection reuse "
                "one checked diagram",
            )
        )

        left_specialization = self._specialization(left_incidences, exit_wire_indices, cell)
        right_specialization = self._specialization(right_incidences, exit_wire_indices, cell)
        middle_wire_indices = tuple(
            sorted(
                {wire for _incidence, wire in left_specialization}
                | {wire for _incidence, wire in right_specialization}
            )
        )
        relation = self._fibre_product(
            left_incidences,
            right_incidences,
            left_specialization,
            right_specialization,
        )
        candidate = CandidateThroughPresentationV0(
            left_domain=request.left_domain,
            right_domain=request.right_domain,
            interface_domain=request.interface_domain,
            frame_id=str(frame["id"]),
            ordered_holes=holes,
            left_hole_indices=left_holes,
            right_hole_indices=right_holes,
            left_incidence_indices=left_incidences,
            right_incidence_indices=right_incidences,
            left_specialization=left_specialization,
            right_specialization=right_specialization,
            middle_upper_wire_indices=middle_wire_indices,
            relation=relation,
            residual=cell.carrier,
        )
        if not left_specialization or not right_specialization:
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                "discard or separation leaves one chart without a justified image "
                "in the declared middle",
                validation,
                ThroughValidationLayerV0.MIDDLE_QUOTIENT,
                cell=cell,
                candidate=candidate,
            )
        validation.append(
            self._satisfied(
                ThroughValidationLayerV0.MIDDLE_QUOTIENT,
                "ancestry reaches frame exits and the declared quotient forgets "
                "only upper lineage position",
            )
        )

        expected_relation = self._fibre_product(
            left_incidences,
            right_incidences,
            left_specialization,
            right_specialization,
        )
        if not relation or relation != expected_relation:
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.NOT_REPRESENTABLE,
                "the two chart specializations have no common exact upper-cut wire",
                validation,
                ThroughValidationLayerV0.FIBRE_PRODUCT,
                cell=cell,
                candidate=candidate,
            )
        validation.append(
            self._satisfied(
                ThroughValidationLayerV0.FIBRE_PRODUCT,
                "the relation is exactly the finite fibre product of the two "
                "specialization relations",
            )
        )

        if (
            candidate.residual is not cell.carrier
            or cell.observer_transition.slice is not cell.carrier
        ):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                "the candidate did not retain the complete exact ProgramSlice object",
                validation,
                ThroughValidationLayerV0.RESIDUAL_RETENTION,
                cell=cell,
                candidate=candidate,
            )
        validation.append(
            self._satisfied(
                ThroughValidationLayerV0.RESIDUAL_RETENTION,
                "the complete slice, including events outside the selected frame, remains attached",
            )
        )

        round_trip = tuple(
            sorted(
                (pair.reversed() for pair in candidate.converse_relation),
                key=self._pair_key,
            )
        )
        if round_trip != candidate.relation:
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                "relational converse failed involutivity",
                validation,
                ThroughValidationLayerV0.RELATIONAL_DUALITY,
                cell=cell,
                candidate=candidate,
            )
        validation.append(
            self._satisfied(
                ThroughValidationLayerV0.RELATIONAL_DUALITY,
                "duality is the involutive converse of the unresolved relation, "
                "not inverse execution",
            )
        )

        composition_certificate: Mapping[str, Any] | None = None
        if request.composition_middle is None:
            validation.append(
                ThroughValidationRecordV0(
                    layer=ThroughValidationLayerV0.ADJACENT_COMPOSITION,
                    outcome=LayerOutcomeV0.BLOCKED,
                    reason="no adjacent middle cut was declared",
                )
            )
        else:
            try:
                composition = function.compose_triadic_observer_transitions_v0(
                    code.policy,
                    code.initial_completed,
                    request.composition_middle,
                    tuple(int(node) for node in cell.upper_interface.cut["completed"]),
                )
            except (TypeError, ValueError) as error:
                return self._finish(
                    code,
                    request,
                    ExperimentVerdictV0.OBSTRUCTION,
                    f"Rust rejected adjacent composition: {error}",
                    validation,
                    ThroughValidationLayerV0.ADJACENT_COMPOSITION,
                    cell=cell,
                    candidate=candidate,
                )
            composition_certificate = composition.certificate
            composition_checks = (
                "inputs_revalidated",
                "middle_observation_agreement",
                "slice_composition",
                "lineage_relation_composition",
                "exact_composition",
            )
            if composition.result != cell.observer_transition or any(
                composition.certificate.get(field) != "checked" for field in composition_checks
            ):
                return self._finish(
                    code,
                    request,
                    ExperimentVerdictV0.OBSTRUCTION,
                    "direct and exact adjacent Rust transitions disagree",
                    validation,
                    ThroughValidationLayerV0.ADJACENT_COMPOSITION,
                    cell=cell,
                    candidate=candidate,
                    adjacent_composition_certificate=composition_certificate,
                )
            validation.append(
                self._satisfied(
                    ThroughValidationLayerV0.ADJACENT_COMPOSITION,
                    "the carrier transition composes exactly across the declared middle cut",
                )
            )

        boundary_flags = (
            candidate.semantic_authority,
            candidate.forgetting_authorized,
            candidate.active_normalization_authorized,
            candidate.through_relation_composition_authorized,
            candidate.universal_computation_authorized,
        )
        if any(boundary_flags):
            return self._finish(
                code,
                request,
                ExperimentVerdictV0.OBSTRUCTION,
                "a research candidate crossed its explicit promotion boundary",
                validation,
                ThroughValidationLayerV0.PROMOTION_BOUNDARY,
                cell=cell,
                candidate=candidate,
                adjacent_composition_certificate=composition_certificate,
            )
        validation.append(
            self._satisfied(
                ThroughValidationLayerV0.PROMOTION_BOUNDARY,
                "no forgetting, active normalization, through-composition, or "
                "universality is authorized",
            )
        )
        return self._finish(
            code,
            request,
            ExperimentVerdictV0.SUPPORTED,
            "one grounded relation-valued through form passed every declared finite gate",
            validation,
            cell=cell,
            candidate=candidate,
            adjacent_composition_certificate=composition_certificate,
        )

    @staticmethod
    def _matches_callee(frame: Mapping[str, Any], request: MultiHoleThroughRequestV0) -> bool:
        callee = frame.get("callee")
        return (
            isinstance(callee, Mapping)
            and callee.get("module") == request.callee_module
            and callee.get("function") == request.callee_function
        )

    @staticmethod
    def _specialization(
        lower_incidences: tuple[int, ...],
        exit_wire_indices: tuple[int, ...],
        cell: InterpretationCellV0,
    ) -> tuple[tuple[int, int], ...]:
        selected = set(lower_incidences)
        exits = set(exit_wire_indices)
        pairs: set[tuple[int, int]] = set()
        for link in cell.observer_transition.lineage_links:
            lower_index = int(link["lower_incidence_index"])
            if lower_index not in selected:
                continue
            upper_index = int(link["upper_incidence_index"])
            upper_incidence = cell.upper_interface.incidences[upper_index]
            upper_wire_index = int(upper_incidence["cut_wire_index"])
            if upper_wire_index in exits:
                pairs.add((lower_index, upper_wire_index))
        return tuple(sorted(pairs))

    @classmethod
    def _fibre_product(
        cls,
        left_incidences: tuple[int, ...],
        right_incidences: tuple[int, ...],
        left_specialization: tuple[tuple[int, int], ...],
        right_specialization: tuple[tuple[int, int], ...],
    ) -> tuple[ThroughPairV0, ...]:
        left_images = {
            incidence: {wire for candidate, wire in left_specialization if candidate == incidence}
            for incidence in left_incidences
        }
        right_images = {
            incidence: {wire for candidate, wire in right_specialization if candidate == incidence}
            for incidence in right_incidences
        }
        pairs = tuple(
            ThroughPairV0(left, right, tuple(sorted(common)))
            for left in left_incidences
            for right in right_incidences
            if (common := left_images[left] & right_images[right])
        )
        return tuple(sorted(pairs, key=cls._pair_key))

    @staticmethod
    def _pair_key(pair: ThroughPairV0) -> tuple[int, int, tuple[int, ...]]:
        return (
            pair.left_incidence_index,
            pair.right_incidence_index,
            pair.middle_upper_wire_indices,
        )

    @staticmethod
    def _satisfied(layer: ThroughValidationLayerV0, reason: str) -> ThroughValidationRecordV0:
        return ThroughValidationRecordV0(
            layer=layer,
            outcome=LayerOutcomeV0.SATISFIED,
            reason=reason,
        )

    def _finish(
        self,
        code: ResearchCodeV0,
        request: MultiHoleThroughRequestV0,
        verdict: ExperimentVerdictV0,
        reason: str,
        validation: list[ThroughValidationRecordV0],
        failed_layer: ThroughValidationLayerV0 | None = None,
        *,
        cell: InterpretationCellV0 | None = None,
        candidate: CandidateThroughPresentationV0 | None = None,
        adjacent_composition_certificate: Mapping[str, Any] | None = None,
    ) -> MultiHoleThroughArtifactV0:
        if failed_layer is not None:
            validation.append(
                ThroughValidationRecordV0(
                    layer=failed_layer,
                    outcome=LayerOutcomeV0.FAILED,
                    reason=reason,
                )
            )
        present = {record.layer for record in validation}
        for layer in self._LAYERS:
            if layer not in present:
                validation.append(
                    ThroughValidationRecordV0(
                        layer=layer,
                        outcome=LayerOutcomeV0.BLOCKED,
                        reason="blocked by an earlier validation gate",
                    )
                )
        validation.sort(key=lambda record: self._LAYERS.index(record.layer))
        return MultiHoleThroughArtifactV0(
            code=code,
            request=request,
            verdict=verdict,
            reason=reason,
            validation=tuple(validation),
            cell=cell,
            candidate=candidate,
            adjacent_composition_certificate=adjacent_composition_certificate,
        )
