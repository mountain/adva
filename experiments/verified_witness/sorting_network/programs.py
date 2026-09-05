from __future__ import annotations

from dataclasses import dataclass

from .model import (
    Comparator,
    Layer,
    NetworkEvaluation,
    ProgramName,
    SearchCandidate,
    SearchConfig,
    SortingNetwork,
    make_layer,
)
from .oracle import BitParallelZeroOneOracle, enumerate_nonempty_layers


@dataclass(frozen=True, slots=True)
class Proposal:
    program: ProgramName
    parent: SortingNetwork
    network: SortingNetwork
    operation: str


class SpatialProgram:
    """Append a layer selected by exact contraction of the residual input set."""

    name: ProgramName = "spatial"

    def propose(
        self,
        candidate: SearchCandidate,
        oracle: BitParallelZeroOneOracle,
        config: SearchConfig,
    ) -> tuple[Proposal, ...]:
        evaluation = oracle.evaluate(candidate.network)
        layers = spatial_layer_pool(oracle, evaluation, config)
        proposals = tuple(
            Proposal(
                self.name,
                candidate.network,
                candidate.network.append(layer),
                "append residual-contracting layer",
            )
            for layer in layers
        )
        return rank_proposals(proposals, oracle, config.spatial_branching)


class ConstructionProgram:
    """Append one layer from a small, named library of reusable motifs."""

    name: ProgramName = "construction"

    def propose(
        self,
        candidate: SearchCandidate,
        oracle: BitParallelZeroOneOracle,
        config: SearchConfig,
    ) -> tuple[Proposal, ...]:
        del oracle
        named_layers = construction_layers(candidate.network.channels, candidate.network.depth)
        proposals = tuple(
            Proposal(
                self.name,
                candidate.network,
                candidate.network.append(layer),
                f"graft motif {name}",
            )
            for name, layer in named_layers
        )
        return proposals[: config.construction_branching]


class TemporalProgram:
    """Revise recent history by bounded replay rather than only appending."""

    name: ProgramName = "temporal"

    def propose(
        self,
        candidate: SearchCandidate,
        oracle: BitParallelZeroOneOracle,
        config: SearchConfig,
    ) -> tuple[Proposal, ...]:
        network = candidate.network
        if network.depth == 0:
            return ()

        proposals: list[Proposal] = []
        first_cut = max(0, network.depth - config.temporal_backtrack)
        for cut in range(first_cut, network.depth):
            prefix = network.prefix(cut)
            prefix_evaluation = oracle.evaluate(prefix)
            alternatives = spatial_layer_pool(oracle, prefix_evaluation, config)
            for layer in alternatives[: config.temporal_branching]:
                if layer == network.layers[cut]:
                    continue
                proposals.append(
                    Proposal(
                        self.name,
                        network,
                        network.replace_layer(cut, layer),
                        f"replace layer {cut} and replay suffix",
                    )
                )

        for right_index in range(max(1, first_cut + 1), network.depth):
            left_index = right_index - 1
            swapped = network.swap_layers(left_index, right_index)
            if swapped != network:
                proposals.append(
                    Proposal(
                        self.name,
                        network,
                        swapped,
                        f"exchange recent layers {left_index} and {right_index}",
                    )
                )

        return rank_proposals(tuple(proposals), oracle, config.temporal_branching)


def network_rank(
    network: SortingNetwork,
    oracle: BitParallelZeroOneOracle,
) -> tuple[int, int, int, str]:
    evaluation = oracle.evaluate(network)
    return (
        evaluation.residual_count,
        evaluation.weighted_inversions,
        network.size,
        network.digest,
    )


def rank_proposals(
    proposals: tuple[Proposal, ...],
    oracle: BitParallelZeroOneOracle,
    limit: int,
) -> tuple[Proposal, ...]:
    unique: dict[SortingNetwork, Proposal] = {}
    for proposal in proposals:
        unique.setdefault(proposal.network, proposal)
    ranked = sorted(unique.values(), key=lambda proposal: network_rank(proposal.network, oracle))
    return tuple(ranked[:limit])


def spatial_layer_pool(
    oracle: BitParallelZeroOneOracle,
    evaluation: NetworkEvaluation,
    config: SearchConfig,
) -> tuple[Layer, ...]:
    if oracle.channels <= config.exhaustive_layer_channels:
        layers = enumerate_nonempty_layers(oracle.channels)
    else:
        layers = heuristic_residual_layers(oracle, evaluation, config.spatial_branching * 8)

    scored: list[tuple[tuple[int, int, int, Layer], Layer]] = []
    for layer in layers:
        next_state = oracle.apply_layer(evaluation.output_channels, layer)
        next_evaluation = oracle.evaluate_state(next_state)
        scored.append(
            (
                (
                    next_evaluation.residual_count,
                    next_evaluation.weighted_inversions,
                    len(layer),
                    layer,
                ),
                layer,
            )
        )
    scored.sort(key=lambda item: item[0])
    return tuple(layer for _, layer in scored[: max(config.spatial_branching * 4, 16)])


def heuristic_residual_layers(
    oracle: BitParallelZeroOneOracle,
    evaluation: NetworkEvaluation,
    pool_limit: int,
) -> tuple[Layer, ...]:
    ranked_pairs = sorted(
        (
            (
                oracle.pair_inversion_count(evaluation, lower, upper),
                upper - lower,
                lower,
                upper,
            )
            for lower in range(oracle.channels)
            for upper in range(lower + 1, oracle.channels)
        ),
        key=lambda item: (-item[0], -item[1], item[2], item[3]),
    )
    positive_pairs = [(lower, upper) for score, _, lower, upper in ranked_pairs if score > 0]
    if not positive_pairs:
        positive_pairs = [(lower, upper) for _, _, lower, upper in ranked_pairs]

    layers: set[Layer] = set()
    for pair in positive_pairs[:pool_limit]:
        layers.add((pair,))

    variant_count = min(pool_limit, max(oracle.channels * 4, 16))
    for offset in range(variant_count):
        rotated = positive_pairs[offset:] + positive_pairs[:offset]
        occupied: set[int] = set()
        matching: list[Comparator] = []
        for lower, upper in rotated:
            if lower in occupied or upper in occupied:
                continue
            occupied.update((lower, upper))
            matching.append((lower, upper))
        if matching:
            layers.add(make_layer(oracle.channels, matching))

    for _, layer in construction_layers(oracle.channels, 0):
        layers.add(layer)
    return tuple(sorted(layers, key=lambda layer: (len(layer), layer))[:pool_limit])


def construction_layers(channels: int, depth: int) -> tuple[tuple[str, Layer], ...]:
    named: list[tuple[str, Layer]] = []

    preferred_parity = depth % 2
    for parity in (preferred_parity, 1 - preferred_parity):
        layer = make_layer(
            channels,
            ((index, index + 1) for index in range(parity, channels - 1, 2)),
        )
        if layer:
            named.append((f"odd-even-parity-{parity}", layer))

    mirror = make_layer(
        channels,
        ((index, channels - 1 - index) for index in range(channels // 2)),
    )
    if mirror:
        named.append(("mirror", mirror))

    stride = 1
    while stride < channels:
        pairs: list[Comparator] = []
        block = stride * 2
        for base in range(0, channels, block):
            for offset in range(stride):
                lower = base + offset
                upper = base + stride + offset
                if upper < channels:
                    pairs.append((lower, upper))
        layer = make_layer(channels, pairs)
        if layer:
            named.append((f"block-stride-{stride}", layer))
        stride *= 2

    unique: dict[Layer, str] = {}
    for name, layer in named:
        unique.setdefault(layer, name)
    return tuple((name, layer) for layer, name in unique.items())
