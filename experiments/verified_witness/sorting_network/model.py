from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal, TypeAlias, cast

Comparator: TypeAlias = tuple[int, int]
Layer: TypeAlias = tuple[Comparator, ...]
ProgramName: TypeAlias = Literal["temporal", "spatial", "construction"]
SearchStatus: TypeAlias = Literal["Found", "Unknown"]

RESULT_SCHEMA = "adva.research.sorting-network-result.v1"
CHECKPOINT_SCHEMA = "adva.research.sorting-network-checkpoint.v1"
PROGRAM_ORDER: tuple[ProgramName, ...] = ("temporal", "spatial", "construction")


class ResourceLimitError(RuntimeError):
    """Raised before allocating an exact oracle larger than the declared budget."""


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def make_layer(channels: int, comparators: Iterable[Comparator]) -> Layer:
    """Return a canonical layer and reject overlapping or malformed comparators."""

    occupied: set[int] = set()
    normalized: list[Comparator] = []
    for raw_left, raw_right in comparators:
        left, right = sorted((raw_left, raw_right))
        if not 0 <= left < right < channels:
            raise ValueError(
                f"comparator {(raw_left, raw_right)!r} is outside {channels} channels"
            )
        if left in occupied or right in occupied:
            raise ValueError(f"layer reuses channel in comparator {(left, right)!r}")
        occupied.update((left, right))
        normalized.append((left, right))
    return tuple(sorted(normalized))


@dataclass(frozen=True, slots=True)
class SortingNetwork:
    """A finite comparator network with canonical, pairwise-disjoint layers."""

    channels: int
    layers: tuple[Layer, ...] = ()

    def __post_init__(self) -> None:
        if self.channels < 2:
            raise ValueError("a sorting network requires at least two channels")
        canonical_layers = tuple(make_layer(self.channels, layer) for layer in self.layers)
        if canonical_layers != self.layers:
            object.__setattr__(self, "layers", canonical_layers)

    @property
    def depth(self) -> int:
        return len(self.layers)

    @property
    def size(self) -> int:
        return sum(len(layer) for layer in self.layers)

    def append(self, layer: Layer) -> SortingNetwork:
        return SortingNetwork(self.channels, self.layers + (make_layer(self.channels, layer),))

    def replace_layer(self, index: int, layer: Layer) -> SortingNetwork:
        if not 0 <= index < self.depth:
            raise IndexError(index)
        layers = list(self.layers)
        layers[index] = make_layer(self.channels, layer)
        return SortingNetwork(self.channels, tuple(layers))

    def swap_layers(self, left_index: int, right_index: int) -> SortingNetwork:
        if not 0 <= left_index < self.depth or not 0 <= right_index < self.depth:
            raise IndexError((left_index, right_index))
        layers = list(self.layers)
        layers[left_index], layers[right_index] = layers[right_index], layers[left_index]
        return SortingNetwork(self.channels, tuple(layers))

    def prefix(self, depth: int) -> SortingNetwork:
        if not 0 <= depth <= self.depth:
            raise ValueError(depth)
        return SortingNetwork(self.channels, self.layers[:depth])

    def to_data(self) -> dict[str, object]:
        return {
            "channels": self.channels,
            "layers": [
                [[left, right] for left, right in layer]
                for layer in self.layers
            ],
        }

    @classmethod
    def from_data(cls, data: Mapping[str, object]) -> SortingNetwork:
        channels = int(cast(int, data["channels"]))
        raw_layers = cast(Sequence[Sequence[Sequence[int]]], data["layers"])
        layers = tuple(
            make_layer(channels, ((int(pair[0]), int(pair[1])) for pair in raw_layer))
            for raw_layer in raw_layers
        )
        return cls(channels, layers)

    @property
    def digest(self) -> str:
        payload = canonical_json(self.to_data()).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class NetworkEvaluation:
    """Exact output state and residual statistics for all binary inputs."""

    output_channels: tuple[int, ...] = field(repr=False)
    residual_mask: int = field(repr=False)
    residual_count: int
    adjacent_inversions: tuple[int, ...]
    weighted_inversions: int


@dataclass(frozen=True, slots=True)
class Counterexample:
    input_bits: tuple[int, ...]
    output_bits: tuple[int, ...]

    def to_data(self) -> dict[str, object]:
        return {
            "input": list(self.input_bits),
            "output": list(self.output_bits),
        }


@dataclass(frozen=True, slots=True)
class VerificationReport:
    channels: int
    patterns_checked: int
    depth: int
    size: int
    sorted: bool
    residual_count: int
    adjacent_inversions: tuple[int, ...]
    weighted_inversions: int
    network_sha256: str
    scalar_cross_check: bool | None
    counterexamples: tuple[Counterexample, ...]

    def to_data(self) -> dict[str, object]:
        return {
            "channels": self.channels,
            "patterns_checked": self.patterns_checked,
            "depth": self.depth,
            "size": self.size,
            "sorted": self.sorted,
            "residual_count": self.residual_count,
            "adjacent_inversions": list(self.adjacent_inversions),
            "weighted_inversions": self.weighted_inversions,
            "network_sha256": self.network_sha256,
            "scalar_cross_check": self.scalar_cross_check,
            "counterexamples": [item.to_data() for item in self.counterexamples],
        }


@dataclass(frozen=True, slots=True)
class SearchConfig:
    channels: int
    max_depth: int
    beam_width: int = 64
    spatial_branching: int = 32
    construction_branching: int = 16
    temporal_branching: int = 16
    temporal_backtrack: int = 2
    exhaustive_layer_channels: int = 8
    counterexample_limit: int = 8
    scalar_cross_check_limit: int = 12
    enabled_programs: tuple[ProgramName, ...] = PROGRAM_ORDER
    max_oracle_bytes: int = 512 * 1024 * 1024
    evaluation_cache_entries: int = 4096
    allow_large_oracle: bool = False

    def __post_init__(self) -> None:
        if self.channels < 2:
            raise ValueError("channels must be at least two")
        if self.max_depth < 0:
            raise ValueError("max_depth must be non-negative")
        for name, value in (
            ("beam_width", self.beam_width),
            ("spatial_branching", self.spatial_branching),
            ("construction_branching", self.construction_branching),
            ("temporal_branching", self.temporal_branching),
            ("temporal_backtrack", self.temporal_backtrack),
        ):
            if value <= 0:
                raise ValueError(f"{name} must be positive")
        if self.exhaustive_layer_channels < 2:
            raise ValueError("exhaustive_layer_channels must be at least two")
        if self.counterexample_limit < 0:
            raise ValueError("counterexample_limit must be non-negative")
        if self.scalar_cross_check_limit < 0:
            raise ValueError("scalar_cross_check_limit must be non-negative")
        invalid = set(self.enabled_programs) - set(PROGRAM_ORDER)
        if invalid:
            raise ValueError(f"unknown programs: {sorted(invalid)!r}")
        if len(set(self.enabled_programs)) != len(self.enabled_programs):
            raise ValueError("enabled_programs contains duplicates")
        if not {"spatial", "construction"}.intersection(self.enabled_programs):
            raise ValueError("at least one append program must be enabled")
        if self.max_oracle_bytes <= 0:
            raise ValueError("max_oracle_bytes must be positive")
        if self.evaluation_cache_entries < 0:
            raise ValueError("evaluation_cache_entries must be non-negative")

    def to_data(self) -> dict[str, object]:
        data = asdict(self)
        data["enabled_programs"] = list(self.enabled_programs)
        return cast(dict[str, object], data)

    @classmethod
    def from_data(cls, data: Mapping[str, object]) -> SearchConfig:
        values = dict(data)
        raw_programs = cast(Sequence[str], values.get("enabled_programs", PROGRAM_ORDER))
        values["enabled_programs"] = tuple(cast(ProgramName, item) for item in raw_programs)
        return cls(**cast(dict[str, Any], values))


@dataclass(frozen=True, slots=True)
class SearchStep:
    program: ProgramName
    operation: str
    parent_sha256: str
    candidate_sha256: str
    depth_before: int
    depth_after: int
    residual_before: int
    residual_after: int
    weighted_inversions_after: int
    size_after: int

    def to_data(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_data(cls, data: Mapping[str, object]) -> SearchStep:
        return cls(**cast(dict[str, Any], dict(data)))


@dataclass(frozen=True, slots=True)
class SearchCandidate:
    network: SortingNetwork
    lineage: tuple[SearchStep, ...] = ()

    def to_data(self) -> dict[str, object]:
        return {
            "network": self.network.to_data(),
            "lineage": [step.to_data() for step in self.lineage],
        }

    @classmethod
    def from_data(cls, data: Mapping[str, object]) -> SearchCandidate:
        network = SortingNetwork.from_data(cast(Mapping[str, object], data["network"]))
        raw_lineage = cast(Sequence[Mapping[str, object]], data["lineage"])
        return cls(network, tuple(SearchStep.from_data(item) for item in raw_lineage))


@dataclass(frozen=True, slots=True)
class DepthReport:
    depth: int
    generated_temporal: int
    generated_spatial: int
    generated_construction: int
    unique_candidates: int
    selected_candidates: int
    best_residual_count: int
    best_weighted_inversions: int
    best_size: int
    best_sha256: str

    def to_data(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_data(cls, data: Mapping[str, object]) -> DepthReport:
        return cls(**cast(dict[str, Any], dict(data)))


def write_json_atomic(path: Path, data: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


@dataclass(frozen=True, slots=True)
class SearchCheckpoint:
    config: SearchConfig
    completed_depth: int
    beam: tuple[SearchCandidate, ...]
    depth_reports: tuple[DepthReport, ...]

    def to_data(self) -> dict[str, object]:
        return {
            "schema": CHECKPOINT_SCHEMA,
            "config": self.config.to_data(),
            "completed_depth": self.completed_depth,
            "beam": [candidate.to_data() for candidate in self.beam],
            "depth_reports": [report.to_data() for report in self.depth_reports],
        }

    @classmethod
    def from_data(cls, data: Mapping[str, object]) -> SearchCheckpoint:
        if data.get("schema") != CHECKPOINT_SCHEMA:
            raise ValueError("unsupported sorting-network checkpoint schema")
        config = SearchConfig.from_data(cast(Mapping[str, object], data["config"]))
        beam = tuple(
            SearchCandidate.from_data(item)
            for item in cast(Sequence[Mapping[str, object]], data["beam"])
        )
        depth_reports = tuple(
            DepthReport.from_data(item)
            for item in cast(Sequence[Mapping[str, object]], data["depth_reports"])
        )
        return cls(config, int(cast(int, data["completed_depth"])), beam, depth_reports)

    @classmethod
    def read(cls, path: Path) -> SearchCheckpoint:
        return cls.from_data(cast(Mapping[str, object], json.loads(path.read_text())))

    def write(self, path: Path) -> None:
        write_json_atomic(path, self.to_data())


@dataclass(frozen=True, slots=True)
class SearchResult:
    status: SearchStatus
    config: SearchConfig
    network: SortingNetwork
    verification: VerificationReport
    lineage: tuple[SearchStep, ...]
    depth_reports: tuple[DepthReport, ...]
    oracle_estimated_bytes: int
    oracle_cache_entries: int

    def to_data(self) -> dict[str, object]:
        return {
            "schema": RESULT_SCHEMA,
            "status": self.status,
            "claim_scope": (
                "Found means that the emitted finite network passed exhaustive zero-one "
                "verification inside the declared depth bound. It is not an optimality proof."
            ),
            "config": self.config.to_data(),
            "oracle": {
                "algorithm": "exhaustive-zero-one-bit-parallel",
                "estimated_base_storage_bytes": self.oracle_estimated_bytes,
                "evaluation_cache_entries": self.oracle_cache_entries,
            },
            "network": self.network.to_data(),
            "verification": self.verification.to_data(),
            "lineage": [step.to_data() for step in self.lineage],
            "depth_reports": [report.to_data() for report in self.depth_reports],
        }

    def write(self, path: Path) -> None:
        write_json_atomic(path, self.to_data())
