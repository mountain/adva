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
