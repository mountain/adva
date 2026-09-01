"""Typed-hole opening and closing over existing checked research carriers.

This module is a nonauthoritative research companion.  It treats one exact
through relation as the finite filling fibre of a typed aperture.  Every
coordinate is derived from unchanged Rust-owned wires, sources, occurrences,
cuts, and slices.  Closing selects an already present filling; reopening keeps
that selection in the trace and residual.  No operation here allocates a
semantic identity, creates a new vocabulary, authorizes forgetting, or turns
an aperture into a stable singularity object.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, ClassVar

from .core import ProgramSliceView, TriadicDomainV0
from .research import (
    CandidateThroughPresentationV0,
    ExperimentVerdictV0,
    MultiHoleThroughArtifactV0,
)
from .triangular_research import TriangularThroughArtifactV0


class HoleOperationV0(StrEnum):
    """The two tested operations; neither is a historical inverse."""

    CLOSE = "close"
    REOPEN = "reopen"


class HoleObstructionV0(StrEnum):
    """Why a finite aperture operation was refused."""

    NONE = "none"
    UNGROUNDED_CARRIER = "ungrounded_carrier"
    WRONG_DOMAIN = "wrong_domain"
    NO_FILLING = "no_filling"
    MULTIPLE_FILLINGS = "multiple_fillings"
    UNKNOWN_FILLING = "unknown_filling"
    RESIDUAL_ERASURE = "residual_erasure"


@dataclass(frozen=True, slots=True)
class HoleFillingV0:
    """One exact relation element read as a possible aperture filling.

    ``filling_index`` and the incidence indices are research coordinates into
    one unchanged artifact.  The occurrence and source strings are copied
    from Rust-owned observations and are not newly allocated identities.
    """

    filling_index: int
    left_domain: TriadicDomainV0
    right_domain: TriadicDomainV0
    left_incidence_index: int
    right_incidence_index: int
    left_occurrence_id: str
    right_occurrence_id: str
    left_source_id: str
    right_source_id: str
    left_occurrence_path: tuple[int, ...]
    right_occurrence_path: tuple[int, ...]
    middle_upper_wire_index: int


@dataclass(frozen=True, slots=True)
class TypedOpenHoleV0:
    """One typed aperture and its finite observed filling fibre."""

    domain: TriadicDomainV0
    surface: str
    frame_id: str
    middle_upper_wire_index: int
    fillings: tuple[HoleFillingV0, ...]
    residual: ProgramSliceView
    semantic_authority: bool = False
    vocabulary_creation_authorized: bool = False
    singularity_identification_authorized: bool = False

    @property
    def research_coordinate(self) -> tuple[str, str, int]:
        return (self.frame_id, self.domain.value, self.middle_upper_wire_index)


@dataclass(frozen=True, slots=True)
class HoleOperationEventV0:
    """A nonsemantic trace event retained across close/reopen."""

    ordinal: int
    operation: HoleOperationV0
    hole_coordinate: tuple[str, str, int]
    filling_index: int


@dataclass(frozen=True, slots=True)
class ClosedHoleV0:
    """A selected filling together with every unselected alternative."""

    aperture: TypedOpenHoleV0
    selected_filling: HoleFillingV0
    unselected_fillings: tuple[HoleFillingV0, ...]
    residual: ProgramSliceView
    trace: tuple[HoleOperationEventV0, ...]
    forgetting_authorized: bool = False
    historical_inverse_authorized: bool = False


@dataclass(frozen=True, slots=True)
class TriadicOpenBoundaryV0:
    """Exactly one construction, space, and time aperture over one residual."""

    holes: tuple[TypedOpenHoleV0, ...]
    residual: ProgramSliceView

    _ORDER: ClassVar[tuple[TriadicDomainV0, ...]] = (
        TriadicDomainV0.CONSTRUCTION,
        TriadicDomainV0.SPACE,
        TriadicDomainV0.TIME,
    )

    @property
    def surface(self) -> str:
        return "".join(hole.surface for hole in self.holes)

    def hole(self, domain: TriadicDomainV0) -> TypedOpenHoleV0:
        return next(hole for hole in self.holes if hole.domain is domain)


@dataclass(frozen=True, slots=True)
class HoleBoundaryArtifactV0:
    """A finite aperture presentation derived from an existing carrier."""

    verdict: ExperimentVerdictV0
    reason: str
    obstruction: HoleObstructionV0
    hole: TypedOpenHoleV0 | None
    boundary: TriadicOpenBoundaryV0 | None
    semantic_authority: bool = False


@dataclass(frozen=True, slots=True)
class HoleCloseRequestV0:
    """Select at most one member of an already observed filling fibre."""

    domain: TriadicDomainV0
    selected_filling_index: int | None = None
    retain_residual: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.domain, TriadicDomainV0):
            raise ValueError("a close request requires one TriadicDomainV0")
        if self.selected_filling_index is not None and (
            isinstance(self.selected_filling_index, bool)
            or not isinstance(self.selected_filling_index, int)
            or self.selected_filling_index < 0
        ):
            raise ValueError("selected_filling_index must be a non-negative integer")


@dataclass(frozen=True, slots=True)
class HoleCloseArtifactV0:
    """Result of one bounded close attempt."""

    verdict: ExperimentVerdictV0
    reason: str
    obstruction: HoleObstructionV0
    aperture: TypedOpenHoleV0
    closed: ClosedHoleV0 | None


@dataclass(frozen=True, slots=True)
class HoleReopenArtifactV0:
    """A reopened aperture with the released filling and trace retained."""

    verdict: ExperimentVerdictV0
    reason: str
    hole: TypedOpenHoleV0
    released_filling: HoleFillingV0
    residual: ProgramSliceView
    trace: tuple[HoleOperationEventV0, ...]
    historical_inverse_authorized: bool = False
    forgetting_authorized: bool = False


class HoleOpenCloseMachineV0:
    """Calibrate typed apertures without promoting a stable hole calculus."""

    _DOMAIN_ORDER: ClassVar[tuple[TriadicDomainV0, ...]] = (
        TriadicDomainV0.CONSTRUCTION,
        TriadicDomainV0.SPACE,
        TriadicDomainV0.TIME,
    )
    _SURFACES: ClassVar[dict[TriadicDomainV0, str]] = {
        TriadicDomainV0.CONSTRUCTION: "{}",
        TriadicDomainV0.SPACE: "[]",
        TriadicDomainV0.TIME: "()",
    }

    def from_through(
        self,
        source: MultiHoleThroughArtifactV0,
    ) -> HoleBoundaryArtifactV0:
        """Expose one interface aperture even when its filling fibre is empty."""

        if source.cell is None or source.candidate is None:
            return HoleBoundaryArtifactV0(
                verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
                reason="the through result contains no grounded cell and aperture candidate",
                obstruction=HoleObstructionV0.UNGROUNDED_CARRIER,
                hole=None,
                boundary=None,
            )
        try:
            hole = self._build_hole(source.candidate, source.cell.lower_interface.incidences)
        except (IndexError, KeyError, TypeError, ValueError) as error:
            return HoleBoundaryArtifactV0(
                verdict=ExperimentVerdictV0.OBSTRUCTION,
                reason=f"the grounded aperture was malformed: {error}",
                obstruction=HoleObstructionV0.UNGROUNDED_CARRIER,
                hole=None,
                boundary=None,
            )
        if hole.residual is not source.cell.carrier:
            return HoleBoundaryArtifactV0(
                verdict=ExperimentVerdictV0.OBSTRUCTION,
                reason="the aperture detached from its complete exact ProgramSlice residual",
                obstruction=HoleObstructionV0.RESIDUAL_ERASURE,
                hole=None,
                boundary=None,
            )
        return HoleBoundaryArtifactV0(
            verdict=ExperimentVerdictV0.SUPPORTED,
            reason="one typed aperture and its finite filling fibre remain grounded",
            obstruction=HoleObstructionV0.NONE,
            hole=hole,
            boundary=None,
        )

    def from_triangle(
        self,
        source: TriangularThroughArtifactV0,
    ) -> HoleBoundaryArtifactV0:
        """Read the three local interface angles as ``{}[]()`` apertures."""

        if (
            source.verdict is not ExperimentVerdictV0.SUPPORTED
            or not source.cells
            or len(source.angles) != 3
        ):
            return HoleBoundaryArtifactV0(
                verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
                reason="a triadic aperture boundary requires one supported three-angle carrier",
                obstruction=HoleObstructionV0.UNGROUNDED_CARRIER,
                hole=None,
                boundary=None,
            )
        primary = source.cells[0]
        try:
            holes = tuple(
                sorted(
                    (
                        self._build_hole(angle, primary.lower_interface.incidences)
                        for angle in source.angles
                    ),
                    key=lambda hole: self._DOMAIN_ORDER.index(hole.domain),
                )
            )
        except (IndexError, KeyError, TypeError, ValueError) as error:
            return HoleBoundaryArtifactV0(
                verdict=ExperimentVerdictV0.OBSTRUCTION,
                reason=f"one triadic aperture was malformed: {error}",
                obstruction=HoleObstructionV0.UNGROUNDED_CARRIER,
                hole=None,
                boundary=None,
            )
        if (
            tuple(hole.domain for hole in holes) != self._DOMAIN_ORDER
            or any(hole.residual is not primary.carrier for hole in holes)
        ):
            return HoleBoundaryArtifactV0(
                verdict=ExperimentVerdictV0.OBSTRUCTION,
                reason="the three apertures do not share one complete exact residual",
                obstruction=HoleObstructionV0.RESIDUAL_ERASURE,
                hole=None,
                boundary=None,
            )
        boundary = TriadicOpenBoundaryV0(holes=holes, residual=primary.carrier)
        return HoleBoundaryArtifactV0(
            verdict=ExperimentVerdictV0.SUPPORTED,
            reason="one unchanged carrier exposes exactly the typed boundary {}[]()",
            obstruction=HoleObstructionV0.NONE,
            hole=None,
            boundary=boundary,
        )

    @staticmethod
    def close(
        aperture: TypedOpenHoleV0,
        request: HoleCloseRequestV0,
    ) -> HoleCloseArtifactV0:
        """Close only by an exact filling selection and retained residual."""

        if request.domain is not aperture.domain:
            return HoleCloseArtifactV0(
                verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
                reason="the requested close domain does not match the aperture type",
                obstruction=HoleObstructionV0.WRONG_DOMAIN,
                aperture=aperture,
                closed=None,
            )
        if not request.retain_residual:
            return HoleCloseArtifactV0(
                verdict=ExperimentVerdictV0.OBSTRUCTION,
                reason="closing cannot erase the aperture filling fibre or process residual",
                obstruction=HoleObstructionV0.RESIDUAL_ERASURE,
                aperture=aperture,
                closed=None,
            )
        if not aperture.fillings:
            return HoleCloseArtifactV0(
                verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
                reason="the typed aperture exists but has no observed admissible filling",
                obstruction=HoleObstructionV0.NO_FILLING,
                aperture=aperture,
                closed=None,
            )

        selected_index = request.selected_filling_index
        if selected_index is None:
            if len(aperture.fillings) != 1:
                return HoleCloseArtifactV0(
                    verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
                    reason="a multivalued filling fibre requires an explicit selection witness",
                    obstruction=HoleObstructionV0.MULTIPLE_FILLINGS,
                    aperture=aperture,
                    closed=None,
                )
            selected = aperture.fillings[0]
        else:
            selected = next(
                (
                    filling
                    for filling in aperture.fillings
                    if filling.filling_index == selected_index
                ),
                None,
            )
            if selected is None:
                return HoleCloseArtifactV0(
                    verdict=ExperimentVerdictV0.NOT_REPRESENTABLE,
                    reason="the selected filling is not a member of this exact aperture fibre",
                    obstruction=HoleObstructionV0.UNKNOWN_FILLING,
                    aperture=aperture,
                    closed=None,
                )

        alternatives = tuple(
            filling for filling in aperture.fillings if filling != selected
        )
        event = HoleOperationEventV0(
            ordinal=0,
            operation=HoleOperationV0.CLOSE,
            hole_coordinate=aperture.research_coordinate,
            filling_index=selected.filling_index,
        )
        closed = ClosedHoleV0(
            aperture=aperture,
            selected_filling=selected,
            unselected_fillings=alternatives,
            residual=aperture.residual,
            trace=(event,),
        )
        return HoleCloseArtifactV0(
            verdict=ExperimentVerdictV0.SUPPORTED,
            reason="one existing exact filling closed the aperture without erasing alternatives",
            obstruction=HoleObstructionV0.NONE,
            aperture=aperture,
            closed=closed,
        )

    @staticmethod
    def reopen(closed: ClosedHoleV0) -> HoleReopenArtifactV0:
        """Re-expose the aperture while retaining the earlier close event."""

        event = HoleOperationEventV0(
            ordinal=len(closed.trace),
            operation=HoleOperationV0.REOPEN,
            hole_coordinate=closed.aperture.research_coordinate,
            filling_index=closed.selected_filling.filling_index,
        )
        return HoleReopenArtifactV0(
            verdict=ExperimentVerdictV0.SUPPORTED,
            reason=(
                "the aperture state reopened while its selected filling remained "
                "historical residual"
            ),
            hole=closed.aperture,
            released_filling=closed.selected_filling,
            residual=closed.residual,
            trace=(*closed.trace, event),
        )

    def _build_hole(
        self,
        candidate: CandidateThroughPresentationV0,
        incidences: tuple[Mapping[str, Any], ...],
    ) -> TypedOpenHoleV0:
        middle_wires = candidate.middle_upper_wire_indices
        relation_wires = {
            wire
            for pair in candidate.relation
            for wire in pair.middle_upper_wire_indices
        }
        if len(middle_wires) != 1:
            raise ValueError("V0 requires one exact middle wire per aperture")
        middle_wire = middle_wires[0]
        if relation_wires and relation_wires != {middle_wire}:
            raise ValueError("the filling relation does not land in the aperture wire")

        fillings: list[HoleFillingV0] = []
        for index, pair in enumerate(candidate.relation):
            if pair.middle_upper_wire_indices != (middle_wire,):
                raise ValueError("one filling must land in exactly the aperture wire")
            left = self._incidence(incidences, pair.left_incidence_index)
            right = self._incidence(incidences, pair.right_incidence_index)
            left_domain = TriadicDomainV0(left["domain"])
            right_domain = TriadicDomainV0(right["domain"])
            if (
                left_domain is not candidate.left_domain
                or right_domain is not candidate.right_domain
            ):
                raise ValueError("one filling endpoint has the wrong observer domain")
            left_occurrence = self._occurrence(left)
            right_occurrence = self._occurrence(right)
            fillings.append(
                HoleFillingV0(
                    filling_index=index,
                    left_domain=left_domain,
                    right_domain=right_domain,
                    left_incidence_index=pair.left_incidence_index,
                    right_incidence_index=pair.right_incidence_index,
                    left_occurrence_id=str(left_occurrence["id"]),
                    right_occurrence_id=str(right_occurrence["id"]),
                    left_source_id=str(left_occurrence["source"]),
                    right_source_id=str(right_occurrence["source"]),
                    left_occurrence_path=self._path(left_occurrence),
                    right_occurrence_path=self._path(right_occurrence),
                    middle_upper_wire_index=middle_wire,
                )
            )
        return TypedOpenHoleV0(
            domain=candidate.interface_domain,
            surface=self._SURFACES[candidate.interface_domain],
            frame_id=candidate.frame_id,
            middle_upper_wire_index=middle_wire,
            fillings=tuple(fillings),
            residual=candidate.residual,
        )

    @staticmethod
    def _incidence(
        incidences: tuple[Mapping[str, Any], ...],
        index: int,
    ) -> Mapping[str, Any]:
        incidence = incidences[index]
        if not isinstance(incidence, Mapping):
            # The frozen facade currently supplies dict-like mappings.  Refuse
            # an unrecognized reconstruction rather than coercing it.
            raise TypeError("an aperture filling incidence must be a checked mapping")
        return incidence

    @staticmethod
    def _occurrence(incidence: Mapping[str, Any]) -> Mapping[str, Any]:
        occurrence = incidence["occurrence"]
        if not isinstance(occurrence, Mapping):
            raise TypeError("an aperture filling must retain one checked occurrence")
        return occurrence

    @staticmethod
    def _path(occurrence: Mapping[str, Any]) -> tuple[int, ...]:
        path = occurrence["path"]
        if not isinstance(path, (list, tuple)) or any(
            isinstance(item, bool) or not isinstance(item, int) or item < 0
            for item in path
        ):
            raise ValueError("an aperture filling has an invalid checked copy path")
        return tuple(path)
