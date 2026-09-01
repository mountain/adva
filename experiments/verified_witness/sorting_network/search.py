from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import cast

from .model import (
    PROGRAM_ORDER,
    RESULT_SCHEMA,
    DepthReport,
    ProgramName,
    ResourceLimitError,
    SearchCandidate,
    SearchCheckpoint,
    SearchConfig,
    SearchResult,
    SearchStep,
    SortingNetwork,
    VerificationReport,
)
from .oracle import BitParallelZeroOneOracle
from .programs import (
    ConstructionProgram,
    Proposal,
    SpatialProgram,
    TemporalProgram,
    network_rank,
)


def candidate_from_proposal(
    parent: SearchCandidate,
    proposal: Proposal,
    oracle: BitParallelZeroOneOracle,
) -> SearchCandidate:
    if proposal.parent != parent.network:
        raise ValueError("proposal parent does not match candidate")
    before = oracle.evaluate(parent.network)
    after = oracle.evaluate(proposal.network)
    step = SearchStep(
        program=proposal.program,
        operation=proposal.operation,
        parent_sha256=parent.network.digest,
        candidate_sha256=proposal.network.digest,
        depth_before=parent.network.depth,
        depth_after=proposal.network.depth,
        residual_before=before.residual_count,
        residual_after=after.residual_count,
        weighted_inversions_after=after.weighted_inversions,
        size_after=proposal.network.size,
    )
    return SearchCandidate(proposal.network, parent.lineage + (step,))


def deduplicate_candidates(
    candidates: Iterable[SearchCandidate],
    oracle: BitParallelZeroOneOracle,
) -> tuple[SearchCandidate, ...]:
    unique: dict[SortingNetwork, SearchCandidate] = {}
    for candidate in candidates:
        existing = unique.get(candidate.network)
        if existing is None or len(candidate.lineage) < len(existing.lineage):
            unique[candidate.network] = candidate
    return tuple(sorted(unique.values(), key=lambda item: network_rank(item.network, oracle)))


def make_depth_report(
    depth: int,
    generated: Mapping[ProgramName, int],
    unique_candidates: int,
    beam: tuple[SearchCandidate, ...],
    oracle: BitParallelZeroOneOracle,
) -> DepthReport:
    best = beam[0]
    evaluation = oracle.evaluate(best.network)
    return DepthReport(
        depth=depth,
        generated_temporal=generated.get("temporal", 0),
        generated_spatial=generated.get("spatial", 0),
        generated_construction=generated.get("construction", 0),
        unique_candidates=unique_candidates,
        selected_candidates=len(beam),
        best_residual_count=evaluation.residual_count,
        best_weighted_inversions=evaluation.weighted_inversions,
        best_size=best.network.size,
        best_sha256=best.network.digest,
    )


def oracle_memory_plan(config: SearchConfig) -> tuple[int, int]:
    base_estimate = BitParallelZeroOneOracle.estimated_base_storage_bytes(config.channels)
    state_estimate = BitParallelZeroOneOracle.estimated_state_bytes(config.channels)
    if base_estimate > config.max_oracle_bytes and not config.allow_large_oracle:
        raise ResourceLimitError(
            "exact bit-parallel oracle estimate "
            f"{base_estimate} bytes exceeds declared limit {config.max_oracle_bytes}; "
            "raise the limit or pass allow_large_oracle=True explicitly"
        )

    remaining = max(0, config.max_oracle_bytes - base_estimate)
    memory_bound = remaining // max(state_estimate, 1)
    cache_entries = min(config.evaluation_cache_entries, memory_bound)
    return base_estimate, cache_entries


def run_search(
    config: SearchConfig,
    *,
    checkpoint: SearchCheckpoint | None = None,
    checkpoint_path: Path | None = None,
    progress: Callable[[DepthReport], None] | None = None,
) -> SearchResult:
    """Run deterministic level-synchronous triadic beam search."""

    oracle_estimate, oracle_cache_entries = oracle_memory_plan(config)
    oracle = BitParallelZeroOneOracle(
        config.channels,
        cache_entries=oracle_cache_entries,
    )

    if checkpoint is None:
        beam = (SearchCandidate(SortingNetwork(config.channels)),)
        reports: tuple[DepthReport, ...] = ()
        start_depth = 1
    else:
        if checkpoint.config.channels != config.channels:
            raise ValueError("checkpoint channel count differs from requested config")
        if checkpoint.completed_depth > config.max_depth:
            raise ValueError("checkpoint is deeper than requested max_depth")
        beam = checkpoint.beam
        reports = checkpoint.depth_reports
        start_depth = checkpoint.completed_depth + 1

    initial = beam[0]
    initial_verification = oracle.verify(
        initial.network,
        counterexample_limit=config.counterexample_limit,
        scalar_cross_check_limit=config.scalar_cross_check_limit,
    )
    if initial_verification.sorted:
        return SearchResult(
            "Found",
            config,
            initial.network,
            initial_verification,
            initial.lineage,
            reports,
            oracle_estimate,
            oracle_cache_entries,
        )

    spatial_program = SpatialProgram()
    construction_program = ConstructionProgram()
    temporal_program = TemporalProgram()

    for depth in range(start_depth, config.max_depth + 1):
        generated: dict[ProgramName, int] = {name: 0 for name in PROGRAM_ORDER}
        appended: list[SearchCandidate] = []

        for candidate in beam:
            if "spatial" in config.enabled_programs:
                proposals = spatial_program.propose(candidate, oracle, config)
                generated["spatial"] += len(proposals)
                appended.extend(
                    candidate_from_proposal(candidate, proposal, oracle)
                    for proposal in proposals
                )
            if "construction" in config.enabled_programs:
                proposals = construction_program.propose(candidate, oracle, config)
                generated["construction"] += len(proposals)
                appended.extend(
                    candidate_from_proposal(candidate, proposal, oracle)
                    for proposal in proposals
                )

        appended_beam = deduplicate_candidates(appended, oracle)
        if not appended_beam:
            break

        temporal_candidates: list[SearchCandidate] = []
        if "temporal" in config.enabled_programs:
            temporal_seed_width = min(len(appended_beam), max(config.beam_width * 2, 16))
            for candidate in appended_beam[:temporal_seed_width]:
                proposals = temporal_program.propose(candidate, oracle, config)
                generated["temporal"] += len(proposals)
                temporal_candidates.extend(
                    candidate_from_proposal(candidate, proposal, oracle)
                    for proposal in proposals
                )

        combined = deduplicate_candidates((*appended_beam, *temporal_candidates), oracle)
        sorted_candidates = tuple(
            candidate
            for candidate in combined
            if oracle.evaluate(candidate.network).residual_count == 0
        )
        if sorted_candidates:
            found = min(
                sorted_candidates,
                key=lambda item: (item.network.size, item.network.digest),
            )
            selected = deduplicate_candidates(
                (*combined[: max(config.beam_width - 1, 0)], found),
                oracle,
            )[: config.beam_width]
            report = make_depth_report(depth, generated, len(combined), selected, oracle)
            reports += (report,)
            if progress is not None:
                progress(report)
            verification = oracle.verify(
                found.network,
                counterexample_limit=config.counterexample_limit,
                scalar_cross_check_limit=config.scalar_cross_check_limit,
            )
            result = SearchResult(
                "Found",
                config,
                found.network,
                verification,
                found.lineage,
                reports,
                oracle_estimate,
                oracle_cache_entries,
            )
            if checkpoint_path is not None:
                SearchCheckpoint(config, depth, selected, reports).write(checkpoint_path)
            return result

        beam = combined[: config.beam_width]
        report = make_depth_report(depth, generated, len(combined), beam, oracle)
        reports += (report,)
        if progress is not None:
            progress(report)
        if checkpoint_path is not None:
            SearchCheckpoint(config, depth, beam, reports).write(checkpoint_path)

    best = beam[0]
    verification = oracle.verify(
        best.network,
        counterexample_limit=config.counterexample_limit,
        scalar_cross_check_limit=config.scalar_cross_check_limit,
    )
    return SearchResult(
        "Unknown",
        config,
        best.network,
        verification,
        best.lineage,
        reports,
        oracle_estimate,
        oracle_cache_entries,
    )


def verify_result_file(
    path: Path,
    *,
    max_oracle_bytes: int = 512 * 1024 * 1024,
    allow_large_oracle: bool = False,
) -> VerificationReport:
    data = cast(Mapping[str, object], json.loads(path.read_text()))
    if data.get("schema") == RESULT_SCHEMA:
        network_data = cast(Mapping[str, object], data["network"])
    elif "channels" in data and "layers" in data:
        network_data = data
    else:
        raise ValueError("file is neither a result artifact nor a network object")
    network = SortingNetwork.from_data(network_data)
    estimate = BitParallelZeroOneOracle.estimated_base_storage_bytes(network.channels)
    if estimate > max_oracle_bytes and not allow_large_oracle:
        raise ResourceLimitError(
            "exact verification oracle estimate "
            f"{estimate} bytes exceeds declared limit {max_oracle_bytes}; "
            "raise the limit or pass allow_large_oracle=True explicitly"
        )
    return BitParallelZeroOneOracle(network.channels).verify(network)
