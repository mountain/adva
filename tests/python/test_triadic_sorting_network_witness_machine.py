from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.verified_witness.sorting_network import (
    BitParallelZeroOneOracle,
    ConstructionProgram,
    ResourceLimitError,
    SearchCandidate,
    SearchCheckpoint,
    SearchConfig,
    SortingNetwork,
    SpatialProgram,
    TemporalProgram,
    make_layer,
    run_search,
    scalar_verify,
    verify_result_file,
)


def four_channel_optimal_network() -> SortingNetwork:
    return SortingNetwork(
        4,
        (
            make_layer(4, ((0, 1), (2, 3))),
            make_layer(4, ((0, 2), (1, 3))),
            make_layer(4, ((1, 2),)),
        ),
    )


def test_bit_parallel_zero_one_verifier_matches_independent_scalar_oracle() -> None:
    network = four_channel_optimal_network()
    oracle = BitParallelZeroOneOracle(4)
    report = oracle.verify(network)

    assert report.sorted
    assert report.patterns_checked == 16
    assert report.depth == 3
    assert report.size == 5
    assert report.residual_count == 0
    assert report.scalar_cross_check is True
    assert scalar_verify(network)

    incomplete = SortingNetwork(4, network.layers[:-1])
    incomplete_report = oracle.verify(incomplete)
    assert not incomplete_report.sorted
    assert incomplete_report.residual_count == 4
    assert incomplete_report.scalar_cross_check is False
    assert incomplete_report.counterexamples


def test_three_programs_have_distinct_search_actions() -> None:
    config = SearchConfig(
        channels=4,
        max_depth=3,
        beam_width=16,
        spatial_branching=8,
        construction_branching=8,
        temporal_branching=8,
    )
    oracle = BitParallelZeroOneOracle(4)
    empty = SearchCandidate(SortingNetwork(4))

    spatial = SpatialProgram().propose(empty, oracle, config)
    construction = ConstructionProgram().propose(empty, oracle, config)
    assert spatial
    assert construction
    assert all(proposal.network.depth == 1 for proposal in spatial)
    assert all(proposal.network.depth == 1 for proposal in construction)
    assert {proposal.program for proposal in spatial} == {"spatial"}
    assert {proposal.program for proposal in construction} == {"construction"}

    one_layer = SearchCandidate(spatial[0].network)
    temporal = TemporalProgram().propose(one_layer, oracle, config)
    assert temporal
    assert all(proposal.network.depth == 1 for proposal in temporal)
    assert {proposal.program for proposal in temporal} == {"temporal"}
    assert all("replace" in proposal.operation for proposal in temporal)


def test_triadic_search_recovers_a_depth_three_size_five_network() -> None:
    result = run_search(
        SearchConfig(
            channels=4,
            max_depth=3,
            beam_width=32,
            spatial_branching=16,
            construction_branching=8,
            temporal_branching=8,
        )
    )

    assert result.status == "Found"
    assert result.verification.sorted
    assert result.network.depth == 3
    assert result.network.size == 5
    assert result.verification.patterns_checked == 16
    assert len(result.depth_reports) == 3
    assert all(report.generated_spatial > 0 for report in result.depth_reports)
    assert all(report.generated_construction > 0 for report in result.depth_reports)
    assert all(report.generated_temporal > 0 for report in result.depth_reports)


def test_seven_channel_search_improves_the_construction_only_baseline() -> None:
    shared = dict(
        channels=7,
        max_depth=6,
        beam_width=8,
        spatial_branching=12,
        construction_branching=8,
        temporal_branching=6,
    )
    construction_only = run_search(
        SearchConfig(**shared, enabled_programs=("construction",))
    )
    triadic = run_search(SearchConfig(**shared))

    assert construction_only.status == "Found"
    assert construction_only.network.depth == 6
    assert construction_only.network.size == 18
    assert triadic.status == "Found"
    assert triadic.network.depth == 6
    assert triadic.network.size == 17
    assert triadic.verification.patterns_checked == 128


def test_result_and_checkpoint_round_trip(tmp_path: Path) -> None:
    checkpoint_path = tmp_path / "checkpoint.json"
    first = run_search(
        SearchConfig(
            channels=5,
            max_depth=3,
            beam_width=16,
            spatial_branching=12,
            construction_branching=8,
            temporal_branching=6,
        ),
        checkpoint_path=checkpoint_path,
    )
    assert first.status == "Unknown"
    assert checkpoint_path.exists()

    checkpoint = SearchCheckpoint.read(checkpoint_path)
    resumed = run_search(
        SearchConfig(
            channels=5,
            max_depth=5,
            beam_width=16,
            spatial_branching=12,
            construction_branching=8,
            temporal_branching=6,
        ),
        checkpoint=checkpoint,
        checkpoint_path=checkpoint_path,
    )
    assert resumed.status == "Found"

    result_path = tmp_path / "result.json"
    resumed.write(result_path)
    stored = json.loads(result_path.read_text())
    assert stored["schema"] == "adva.research.sorting-network-result.v1"
    assert stored["claim_scope"].endswith("It is not an optimality proof.")

    verified = verify_result_file(result_path)
    assert verified.sorted
    assert verified.network_sha256 == resumed.network.digest


def test_large_exact_oracle_requires_an_explicit_resource_override() -> None:
    config = SearchConfig(
        channels=24,
        max_depth=1,
        max_oracle_bytes=1,
    )
    with pytest.raises(ResourceLimitError, match="exceeds declared limit"):
        run_search(config)


def test_result_verification_applies_the_same_resource_guard(tmp_path: Path) -> None:
    artifact = tmp_path / "large-network.json"
    artifact.write_text(json.dumps({"channels": 24, "layers": []}))

    with pytest.raises(ResourceLimitError, match="verification oracle estimate"):
        verify_result_file(artifact, max_oracle_bytes=1)


def test_committed_five_channel_witness_artifact_is_exact() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    artifact = repository_root / "examples/verified_witness/sorting-network-5ch-depth5.json"
    report = verify_result_file(artifact)

    assert report.sorted
    assert report.channels == 5
    assert report.depth == 5
    assert report.size == 9
    assert report.patterns_checked == 32
