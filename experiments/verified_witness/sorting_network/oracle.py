from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterable, Sequence
from functools import lru_cache
from itertools import product

from .model import (
    Counterexample,
    Layer,
    NetworkEvaluation,
    SortingNetwork,
    VerificationReport,
)


class BitParallelZeroOneOracle:
    """Exhaustive zero-one verifier using Python integers as bit vectors."""

    def __init__(self, channels: int, *, cache_entries: int = 4096) -> None:
        if channels < 2:
            raise ValueError("channels must be at least two")
        if cache_entries < 0:
            raise ValueError("cache_entries must be non-negative")
        self.channels = channels
        self.pattern_count = 1 << channels
        self.full_mask = (1 << self.pattern_count) - 1
        self.input_channels = tuple(self._input_channel_mask(index) for index in range(channels))
        self.cache_entries = cache_entries
        self._cache: OrderedDict[SortingNetwork, NetworkEvaluation] = OrderedDict()

    @staticmethod
    def estimated_state_bytes(channels: int) -> int:
        pattern_count = 1 << channels
        return (channels * pattern_count + 7) // 8

    @classmethod
    def estimated_base_storage_bytes(cls, channels: int) -> int:
        """Conservative base estimate before the bounded evaluation cache."""

        pattern_count = 1 << channels
        bit_vectors = 3 * channels + 2
        return (bit_vectors * pattern_count + 7) // 8

    def _input_channel_mask(self, channel: int) -> int:
        run = 1 << channel
        period = run << 1
        one_run = ((1 << run) - 1) << run
        repetitions = self.pattern_count // period
        geometric_series = ((1 << (period * repetitions)) - 1) // ((1 << period) - 1)
        return one_run * geometric_series

    def apply_layer(self, state: tuple[int, ...], layer: Layer) -> tuple[int, ...]:
        next_state = list(state)
        for lower, upper in layer:
            left = state[lower]
            right = state[upper]
            next_state[lower] = left & right
            next_state[upper] = left | right
        return tuple(next_state)

    def evaluate(self, network: SortingNetwork) -> NetworkEvaluation:
        if network.channels != self.channels:
            raise ValueError("network and oracle channel counts differ")
        cached = self._cache.pop(network, None)
        if cached is not None:
            self._cache[network] = cached
            return cached

        state = self.input_channels
        for layer in network.layers:
            state = self.apply_layer(state, layer)
        evaluation = self.evaluate_state(state)
        if self.cache_entries > 0:
            self._cache[network] = evaluation
            while len(self._cache) > self.cache_entries:
                self._cache.popitem(last=False)
        return evaluation

    def evaluate_state(self, state: tuple[int, ...]) -> NetworkEvaluation:
        if len(state) != self.channels:
            raise ValueError("state channel count differs from oracle")

        residual_mask = 0
        adjacent_inversions: list[int] = []
        for index in range(self.channels - 1):
            inversion_mask = state[index] & ~state[index + 1] & self.full_mask
            residual_mask |= inversion_mask
            adjacent_inversions.append(inversion_mask.bit_count())

        weighted_inversions = 0
        for lower in range(self.channels):
            for upper in range(lower + 1, self.channels):
                mask = state[lower] & ~state[upper] & self.full_mask
                weighted_inversions += (upper - lower) * mask.bit_count()

        return NetworkEvaluation(
            output_channels=state,
            residual_mask=residual_mask,
            residual_count=residual_mask.bit_count(),
            adjacent_inversions=tuple(adjacent_inversions),
            weighted_inversions=weighted_inversions,
        )

    def pair_inversion_count(
        self,
        evaluation: NetworkEvaluation,
        lower: int,
        upper: int,
    ) -> int:
        return (
            evaluation.output_channels[lower]
            & ~evaluation.output_channels[upper]
            & evaluation.residual_mask
            & self.full_mask
        ).bit_count()

    def counterexamples(
        self,
        evaluation: NetworkEvaluation,
        limit: int,
    ) -> tuple[Counterexample, ...]:
        if limit < 0:
            raise ValueError("counterexample limit must be non-negative")
        examples: list[Counterexample] = []
        mask = evaluation.residual_mask
        while mask and len(examples) < limit:
            least_bit = mask & -mask
            pattern_index = least_bit.bit_length() - 1
            input_bits = tuple((pattern_index >> channel) & 1 for channel in range(self.channels))
            output_bits = tuple(
                (channel_mask >> pattern_index) & 1
                for channel_mask in evaluation.output_channels
            )
            examples.append(Counterexample(input_bits, output_bits))
            mask ^= least_bit
        return tuple(examples)

    def verify(
        self,
        network: SortingNetwork,
        *,
        counterexample_limit: int = 8,
        scalar_cross_check_limit: int = 12,
    ) -> VerificationReport:
        evaluation = self.evaluate(network)
        scalar_cross_check: bool | None = None
        if self.channels <= scalar_cross_check_limit:
            scalar_cross_check = scalar_verify(network)
            if scalar_cross_check != (evaluation.residual_count == 0):
                raise AssertionError("bit-parallel and scalar verifiers disagree")
        return VerificationReport(
            channels=self.channels,
            patterns_checked=self.pattern_count,
            depth=network.depth,
            size=network.size,
            sorted=evaluation.residual_count == 0,
            residual_count=evaluation.residual_count,
            adjacent_inversions=evaluation.adjacent_inversions,
            weighted_inversions=evaluation.weighted_inversions,
            network_sha256=network.digest,
            scalar_cross_check=scalar_cross_check,
            counterexamples=self.counterexamples(evaluation, counterexample_limit),
        )


def scalar_execute(network: SortingNetwork, values: Sequence[int]) -> tuple[int, ...]:
    """Independent scalar comparator execution used as a small-instance oracle."""

    if len(values) != network.channels:
        raise ValueError("input length differs from network channel count")
    state = list(values)
    for layer in network.layers:
        previous = tuple(state)
        for lower, upper in layer:
            state[lower] = min(previous[lower], previous[upper])
            state[upper] = max(previous[lower], previous[upper])
    return tuple(state)


def scalar_verify(network: SortingNetwork) -> bool:
    for bits in product((0, 1), repeat=network.channels):
        if scalar_execute(network, bits) != tuple(sorted(bits)):
            return False
    return True


@lru_cache(maxsize=None)
def enumerate_nonempty_layers(channels: int) -> tuple[Layer, ...]:
    """Enumerate every non-empty matching on the channel set."""

    if channels < 2:
        return ()

    def recurse(available: tuple[int, ...]) -> Iterable[Layer]:
        if not available:
            yield ()
            return
        first = available[0]
        yield from recurse(available[1:])
        for position in range(1, len(available)):
            second = available[position]
            remaining = available[1:position] + available[position + 1 :]
            for tail in recurse(remaining):
                yield tuple(sorted(((first, second),) + tail))

    layers = {layer for layer in recurse(tuple(range(channels))) if layer}
    return tuple(sorted(layers, key=lambda layer: (len(layer), layer)))
