#!/usr/bin/env python3
"""Exact external four-hole coordinate and finite positivity calibration.

Indices name points of this declared finite carrier. They are never native
SourceId, OccurrenceId, expression-word identities, or semantic certificates.
The arithmetic chart correspondence is deliberately separate from positivity.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
CONTRACT_PATH = HERE / "contract.json"
SCHEMA = "adva.external-multihole-positivity-evidence.v0"
UNIVERSE = 15
POLICIES = ("basic", "joint", "marked")
EXPECTED_BASIC_MODELS = 12
DEFAULT_FUEL = 100000
INCLUSIONS = tuple((a, b) for a in range(16) for b in range(16)
                   if (a & ~b) == 0)
COMPLEMENT_PAIRS = tuple((a, UNIVERSE ^ a) for a in range(16)
                         if a < (UNIVERSE ^ a))


def require(condition: bool, message: str) -> None:
    """Explicit acceptance checks also remain active under python -O."""
    if not condition:
        raise ValueError(message)


class FuelExhausted(RuntimeError):
    pass


class Fuel:
    """Charge one unit per subset incidence or per queried family.

    The census checks every one of its 81 incidences for every one of 256
    complement choices, including choices already found to fail. A decision
    charges one unit for validating each supplied eight-region family and one
    for querying each family of the complete 12-family cache. Arithmetic,
    serialization, and documentary checks are outside this logical fuel unit.
"""

    def __init__(self, limit: int = DEFAULT_FUEL) -> None:
        require(type(limit) is int and limit >= 0, "fuel must be a nonnegative integer")
        self.limit = limit
        self.consumed = 0

    @property
    def remaining(self) -> int:
        return self.limit - self.consumed

    def consume(self, amount: int = 1) -> None:
        if amount > self.remaining:
            raise FuelExhausted("logical fuel exhausted")
        self.consumed += amount


def _fuel(value: Fuel | int | None) -> Fuel:
    if value is None:
        return Fuel()
    if type(value) is int:
        return Fuel(value)
    if type(value) is Fuel:
        return value
    raise ValueError("fuel must be a nonnegative integer, Fuel, or None")


def _mask(value: Any) -> int:
    require(type(value) is int and 0 <= value <= UNIVERSE,
            "region masks must be integers from 0 through 15")
    return value


def filling_indices(mask: int) -> list[int]:
    return [i for i in range(4) if mask & (1 << i)]


def intersection(family: tuple[int, ...] | list[int]) -> int:
    result = UNIVERSE
    for region in family:
        result &= region
    return result


def _valid_family(family: tuple[int, ...]) -> bool:
    present = frozenset(family)
    return (len(family) == 8 and len(present) == 8
            and all((a in present) != (b in present) for a, b in COMPLEMENT_PAIRS)
            and all(a not in present or b in present for a, b in INCLUSIONS))


def enumerate_models(fuel: Fuel | int | None = None) -> list[tuple[int, ...]]:
    """Enumerate every complementary, inclusion-closed positivity family."""
    counter = _fuel(fuel)
    families: list[tuple[int, ...]] = []
    for choices in product((0, 1), repeat=len(COMPLEMENT_PAIRS)):
        family = tuple(sorted(pair[choice]
                              for pair, choice in zip(COMPLEMENT_PAIRS, choices)))
        present = frozenset(family)
        valid = True
        for a, b in INCLUSIONS:
            counter.consume()
            if a in present and b not in present:
                valid = False
        if valid:
            families.append(family)
    families.sort()
    require(len(INCLUSIONS) == 81, "the four-point inclusion table is not 81 incidences")
    require(len(families) == EXPECTED_BASIC_MODELS, "the basic family census changed")
    return families


def _cached_models(models: Any, counter: Fuel) -> list[tuple[int, ...]]:
    require(type(models) in (list, tuple), "models must be a complete basic family cache")
    require(len(models) == EXPECTED_BASIC_MODELS,
            "models must contain all 12 basic families; a partial cache is invalid")
    families: list[tuple[int, ...]] = []
    for raw in models:
        counter.consume()
        require(type(raw) in (list, tuple), "each model must be a region family")
        require(len(raw) == 8, "each model must contain exactly eight positive regions")
        family = tuple(_mask(item) for item in raw)
        require(family == tuple(sorted(family)), "model regions must be sorted")
        require(_valid_family(family), "model does not satisfy the declared A1/A2")
        families.append(family)
    require(len(families) == EXPECTED_BASIC_MODELS
            and len(set(families)) == EXPECTED_BASIC_MODELS,
            "models must contain all 12 distinct basic families; a partial cache is invalid")
    return sorted(families)


def _requirements(values: Any) -> tuple[int, ...]:
    require(type(values) in (list, tuple), "assumptions must be lists or tuples of masks")
    require(len(values) <= 16, "at most sixteen region assumptions are admitted")
    return tuple(sorted({_mask(value) for value in values}))


def _policy_accepts(family: tuple[int, ...], policy: str, marked: int) -> bool:
    common = intersection(family)
    return (policy == "basic" or (policy == "joint" and common != 0)
            or (policy == "marked" and bool(common & (1 << marked))))


def _result(query: Any, policy: Any, classification: str,
            surviving: list[tuple[int, ...]] | None = None,
            reason: str | None = None) -> dict[str, Any]:
    legal_query = type(query) is int and 0 <= query <= UNIVERSE
    positive = [] if surviving is None else [m for m in surviving if query in m]
    negative = [] if surviving is None else [m for m in surviving if query not in m]
    result = {
        "query_mask": query,
        "policy": policy,
        "classification": classification,
        "model_count": None if surviving is None else len(surviving),
        "positive_model": list(positive[0]) if positive else None,
        "negative_model": list(negative[0]) if negative else None,
        "realizing_points": [] if surviving is None else [
            {"model": list(model), "indices": filling_indices(intersection(model))}
            for model in surviving
        ],
        "inhabited": bool(query) if legal_query else None,
        "filling_indices": filling_indices(query) if legal_query else None,
    }
    if reason is not None:
        result["reason"] = reason
    return result


def decide(query_mask: int, positive_masks: tuple[int, ...] = (),
           negative_masks: tuple[int, ...] = (), policy: str = "basic",
           fuel: Fuel | int | None = None, marked: int = 2,
           models: list[tuple[int, ...]] | None = None) -> dict[str, Any]:
    """Decide positivity in a fixed finite theory, with complete model witnesses.

An optional cache must contain all 12 basic families. Incomplete caches are
rejected rather than being used to turn missing countermodels into certainty.
Joint and marked policies are applied here, after cache validation. All
model scans must finish before any positive or negative verdict is returned.
Inhabitation of the queried region is reported independently of positivity.
"""
    try:
        query = _mask(query_mask)
        positive = _requirements(positive_masks)
        negative = _requirements(negative_masks)
        require(type(policy) is str and policy in POLICIES, "unknown positivity policy")
        require(type(marked) is int and 0 <= marked < 4,
                "marked point must be an integer from 0 through 3")
        counter = _fuel(fuel)
        families = None if models is None else _cached_models(models, counter)
    except (ValueError, TypeError) as error:
        return _result(query_mask, policy, "InvalidInput", reason=str(error))
    except FuelExhausted:
        return _result(query_mask, policy, "Unknown")

    try:
        if families is None:
            families = enumerate_models(counter)
        surviving: list[tuple[int, ...]] = []
        for family in families:
            counter.consume()
            present = frozenset(family)
            if (all(region in present for region in positive)
                    and all(region not in present for region in negative)
                    and _policy_accepts(family, policy, marked)):
                surviving.append(family)
    except FuelExhausted:
        return _result(query, policy, "Unknown")

    if not surviving:
        classification = "Inconsistent"
    elif all(query in model for model in surviving):
        classification = "ForcedPositive"
    elif all(query not in model for model in surviving):
        classification = "ForcedNegative"
    else:
        classification = "Underdetermined"
    return _result(query, policy, classification, surviving)


def _point(values: list[str] | tuple[str, ...]) -> tuple[Fraction, ...]:
    require(len(values) == 4, "a chart filling must fill all four holes")
    return tuple(Fraction(value) for value in values)


def _strings(point: tuple[Fraction, ...]) -> list[str]:
    return [str(value) for value in point]


def coordinate_map(point: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    a, b, x, y = point
    require(a > 0 and y > 0, "source chart requires a > 0 and y > 0")
    return a, b, a * x + b, a * y


def exact_divide(numerator: Fraction, denominator: Fraction) -> Fraction:
    """Guard the partial arithmetic operation itself, before any division."""
    require(denominator != 0, "division denominator must be nonzero")
    return numerator / denominator


def coordinate_inverse(point: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    a, b, p, q = point
    require(a > 0 and q > 0, "target chart requires a > 0 and q > 0")
    return a, b, exact_divide(p - b, a), exact_divide(q, a)


def target_program(point: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    a, b, p, q = point
    require(a > 0 and q > 0, "target program requires a > 0 and q > 0")
    d = p * p + q * q
    require(d != 0, "reciprocal denominator must be nonzero")
    return a, b, -exact_divide(p, d), exact_divide(q, d)


def source_program(point: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return target_program(coordinate_map(point))


def _observation_masks(outputs: list[tuple[Fraction, ...]]) -> dict[str, int]:
    observations = {"B": 0, "H": 0}
    for i, (_, _, r, s) in enumerate(outputs):
        if r * r + (s - Fraction(1, 2)) ** 2 < Fraction(1, 4):
            observations["B"] |= 1 << i
        if s > Fraction(1, 4):
            observations["H"] |= 1 << i
    return observations


def transport_mask(mask: int, target_order: list[int] | tuple[int, ...]) -> int:
    _mask(mask)
    require(len(target_order) == 4 and sorted(target_order) == list(range(4)),
            "target order must be a four-point permutation")
    return sum(1 << target for target, source in enumerate(target_order)
               if mask & (1 << source))


def _geometry(contract: dict[str, Any]) -> tuple[dict[str, Any], list[int]]:
    program = contract["programs"]
    order = program["target_order"]
    require(order == [3, 2, 1, 0], "the frozen target point order changed")
    sources = [_point(point) for point in program["fillings"]]
    require(len(sources) == 4 and len(set(sources)) == 4,
            "the frozen finite carrier requires four distinct fillings")
    mapped = [coordinate_map(point) for point in sources]
    targets = [mapped[i] for i in order]
    source_outputs = [source_program(point) for point in sources]
    target_outputs = [target_program(point) for point in targets]
    inverses = [coordinate_inverse(point) for point in targets]
    require(inverses == [sources[i] for i in order], "coordinate inverse failed")
    require(target_outputs == [source_outputs[i] for i in order],
            "the four-hole programs failed their retained correspondence")
    source_observations = _observation_masks(source_outputs)
    target_observations = _observation_masks(target_outputs)
    require(source_observations == {"B": 12, "H": 5}, "source incidences changed")
    require(target_observations == {"B": 3, "H": 10}, "target incidences changed")
    require(len({(bool(source_observations["B"] & (1 << i)),
                  bool(source_observations["H"] & (1 << i)))
                 for i in range(4)}) == 4, "the observations do not distinguish four atoms")
    for source, (_, _, p, q) in zip(sources, mapped):
        a, b, x, y = source
        output = source_program(source)
        _, _, r, s = output
        require((r * r + (s - Fraction(1, 2)) ** 2 < Fraction(1, 4)) == (a * y > 1),
                "B observer pullback failed")
        require((s > Fraction(1, 4)) == ((a * x + b) ** 2 + (a * y - 2) ** 2 < 4),
                "H observer pullback failed")
        require(p == a * x + b and q == a * y, "chart incidence binding failed")
    return {
        "source_fillings": [_strings(point) for point in sources],
        "target_fillings": [_strings(point) for point in targets],
        "source_outputs": [_strings(point) for point in source_outputs],
        "target_outputs": [_strings(point) for point in target_outputs],
        "inverse_fillings": [_strings(point) for point in inverses],
        "source_observations": source_observations,
        "target_observations": target_observations,
        "target_order": list(order),
    }, list(order)


def _bindings() -> dict[str, str]:
    return {
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "contract_sha256": hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
    }


def build_evidence() -> dict[str, Any]:
    """Run only the finite producer campaign specified by the frozen contract."""
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    require(contract["schema"] == "adva.external-multihole-positivity-contract.v0",
            "unsupported contract")
    require(contract["budget"]["producer_fuel_per_run"] == DEFAULT_FUEL,
            "producer fuel differs from the frozen scope")
    counter = Fuel(contract["budget"]["producer_fuel_per_run"])
    geometry, order = _geometry(contract)
    source_models = enumerate_models(counter)
    target_models = enumerate_models(counter)
    mapped_models = sorted(tuple(sorted(transport_mask(region, order) for region in family))
                           for family in source_models)
    require(mapped_models == target_models, "complete model families failed chart transport")
    models: dict[str, Any] = {}
    for chart, families, marked in (("source", source_models, 2), ("target", target_models, 1)):
        models[chart] = {
            policy: [list(family) for family in families if _policy_accepts(family, policy, marked)]
            for policy in POLICIES
        }
        models[chart]["marked_index"] = marked
        require([len(models[chart][p]) for p in POLICIES] == [12, 4, 1],
                "the three policy model counts changed")

    cases = []
    for case in contract["cases"]:
        for policy in POLICIES:
            for chart, families, marked in (("source", source_models, 2),
                                           ("target", target_models, 1)):
                convert = (lambda m: m) if chart == "source" else (lambda m: transport_mask(m, order))
                positive = sorted(convert(region) for region in case["positive"])
                negative = sorted(convert(region) for region in case["negative"])
                queries = [decide(query, positive, negative, policy, counter, marked, families)
                           for query in range(16)]
                require(all(q["classification"] not in ("Unknown", "InvalidInput") for q in queries),
                        "the bounded case campaign did not finish decisively")
                cases.append({"name": case["name"], "policy": policy, "chart": chart,
                              "positive": positive, "negative": negative, "queries": queries})

    triangle_regions = [12, 5, 9]
    triangle_basic = decide(12, triangle_regions, (), "basic", counter, models=source_models)
    triangle_joint = decide(12, triangle_regions, (), "joint", counter, models=source_models)
    require(triangle_basic["model_count"] > 0 and triangle_joint["classification"] == "Inconsistent",
            "the joint-realization negative control failed")
    left = _point(["3", "-1", "2/3", "2/3"])
    right = _point(["2", "1", "0", "1"])
    left_output, right_output = source_program(left), source_program(right)
    require(left_output != right_output and left_output[2:] == right_output[2:],
            "forgetting the retained parameters did not produce the intended collision")
    zero_fuel = decide(0, fuel=0)
    require(zero_fuel["classification"] == "Unknown"
            and zero_fuel["model_count"] is None, "zero fuel must not decide inconsistency")
    conflict = decide(5, (5,), (5,), "basic", counter, models=source_models)
    require(conflict["classification"] == "Inconsistent", "direct conflict was not refused")
    guarded_status = "UnexpectedAcceptance"
    try:
        exact_divide(Fraction(0), Fraction(0))
    except ValueError:
        guarded_status = "InvalidInput"
    require(guarded_status == "InvalidInput", "division lost its nonzero guard")
    controls = {
        "triangle": {
            "positive_regions": triangle_regions,
            "individual_filling_indices": [filling_indices(region) for region in triangle_regions],
            "common_filling_indices": filling_indices(intersection(triangle_regions)),
            "basic_result": triangle_basic,
            "joint_result": triangle_joint,
        },
        "forgotten_parameters": {
            "left_source": _strings(left), "right_source": _strings(right),
            "left_output": _strings(left_output), "right_output": _strings(right_output),
            "forgotten_output": _strings(left_output[2:]),
            "distinct_retained_parameters": left_output[:2] != right_output[:2],
            "marked_point_membership": [True, False],
            "descends_after_forgetting": False,
        },
        "division_guard": {
            "dividend": "0", "divisor": "0", "tested_y": ["0", "1"],
            "cross_products": [str(Fraction(0) * y) for y in (Fraction(0), Fraction(1))],
            "distinct_preimages": True, "guarded_status": guarded_status,
        },
        "zero_fuel": zero_fuel,
        "conflicting_assumptions": conflict,
    }
    require(counter.consumed == 2 * 256 * 81 + 2 * (4 * 3 * 2 * 16 + 3) * 12,
            "producer logical fuel accounting changed")
    return {
        "schema": SCHEMA, "status": "ExternalExactPass", "native_status": "Unavailable",
        "bindings": _bindings(), "geometry": geometry, "models": models,
        "cases": cases, "controls": controls,
        "fuel": {"limit": counter.limit, "consumed": counter.consumed,
                 "remaining": counter.remaining},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="new evidence path; existing files are refused")
    args = parser.parse_args(argv)
    if args.output.exists():
        print(json.dumps({"status": "RefusedOutput", "reason": "output path already exists"}, sort_keys=True))
        return 2
    try:
        report = build_evidence()
    except FuelExhausted:
        report = {"schema": SCHEMA, "status": "Unknown", "native_status": "Unavailable",
                  "bindings": _bindings(), "reason": "logical fuel exhausted"}
    serialized = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    require(len(serialized.encode("utf-8")) <= 1048576, "evidence exceeds the frozen output budget")
    try:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(serialized)
    except FileExistsError:
        print(json.dumps({"status": "RefusedOutput", "reason": "output path already exists"}, sort_keys=True))
        return 2
    print(json.dumps({"status": report["status"], "cases": len(report.get("cases", ())),
                      "native_status": report["native_status"]}, sort_keys=True))
    return 0 if report["status"] == "ExternalExactPass" else 3


if __name__ == "__main__":
    raise SystemExit(main())
