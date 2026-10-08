#!/usr/bin/env python3
"""Independent bounded receiver for one external four-point calibration.

No producer import and no native semantic authority. One immutable independently
derived family cache, one process-wide fuel account, and one global deadline.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import time

SCHEMA = "adva.external-multihole-positivity-evidence.v0"
REPORT_SCHEMA = "adva.external-multihole-positivity-verification.v0"
HERE = Path(__file__).resolve().parent
MAX_FUEL = 10_000_000
MAX_WALL = 12.0
MAX_BYTES = 1_048_576
POLICIES = ("basic", "joint", "marked")
POINTS = frozenset(range(4))
REGIONS = tuple(frozenset(i for i in range(4) if n & (1 << i)) for n in range(16))
_budget = None
_families = None
_cache_hits = 0

class Rejected(Exception):
    pass

class Limit(Exception):
    pass

class Budget:
    def __init__(self, fuel=MAX_FUEL, wall=MAX_WALL):
        if type(fuel) is not int or not 0 <= fuel <= MAX_FUEL:
            raise Rejected("invalid receiver fuel limit")
        if not isinstance(wall, (int, float)) or not 0 <= wall <= MAX_WALL:
            raise Rejected("invalid receiver wall limit")
        self.limit = fuel
        self.consumed = 0
        self.deadline = time.monotonic() + wall
        self.candidates = 0

    def tick(self, cost=1):
        if self.consumed + cost > self.limit:
            raise Limit("receiver fuel exhausted")
        if time.monotonic() >= self.deadline:
            raise Limit("receiver deadline exhausted")
        self.consumed += cost

def require(condition, message):
    if not condition:
        raise Rejected(message)

def keys(value, names, location):
    require(type(value) is dict and set(value) == set(names),
            location + ": unexpected fields")

def exact(value, expected, location):
    def same(left, right):
        _budget.tick()
        if type(left) is not type(right):
            return False
        if type(right) in (list, tuple):
            return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
        if type(right) is dict:
            return set(left) == set(right) and all(same(left[k], right[k]) for k in right)
        return left == right
    require(same(value, expected), location + ": incorrect value")

def integers(value, expected, location):
    require(type(value) is list and all(type(x) is int for x in value),
            location + ": integer list required")
    exact(value, list(expected), location)

def unique_object(pairs):
    result = {}
    for name, value in pairs:
        require(name not in result, "duplicate JSON field")
        result[name] = value
    return result

def bad_constant(value):
    raise Rejected("nonfinite JSON number")

def load_bytes(path):
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, "input exceeds fixed byte limit")
    return data

def decode_json(data):
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique_object,
                      parse_constant=bad_constant)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def mask(region):
    return sum(1 << i for i in region)

def independent_families():
    global _families, _cache_hits
    if _families is not None:
        _cache_hits += 1
        return _families
    accepted = []
    for choice in range(65_536):
        _budget.tick()
        _budget.candidates += 1
        family = frozenset(REGIONS[j] for j in range(16) if choice & (1 << j))
        upward = True
        for lower in REGIONS:
            for upper in REGIONS:
                if lower.issubset(upper):
                    _budget.tick()
                    if lower in family and upper not in family:
                        upward = False
                        break
            if not upward:
                break
        if not upward:
            continue
        complete = True
        for region in REGIONS:
            _budget.tick()
            if (region in family) == ((POINTS - region) in family):
                complete = False
                break
        if complete:
            accepted.append(tuple(sorted(mask(region) for region in family)))
    accepted.sort()
    require(len(accepted) == 12, "independent four-point family count differs")
    _families = tuple(accepted)
    return _families

def intersection(family):
    shared = set(POINTS)
    for region in family:
        _budget.tick()
        shared.intersection_update(REGIONS[region])
    return sorted(shared)

def policy_families(families, policy, marked):
    if policy == "basic":
        return tuple(families)
    if policy == "joint":
        return tuple(f for f in families if intersection(f))
    if policy == "marked":
        return tuple(f for f in families if marked in intersection(f))
    raise Rejected("unknown policy")

def eligible(families, positive, negative):
    return tuple(f for f in families if all(p in f for p in positive)
                 and all(n not in f for n in negative))

def family_list(value, expected, location):
    require(type(value) is list, location + ": list required")
    for family in value:
        require(type(family) is list and len(family) == 8
                and all(type(r) is int and 0 <= r < 16 for r in family),
                location + ": invalid family")
        require(family == sorted(set(family)), location + ": family not canonical")
    exact(value, [list(f) for f in expected], location)

def check_query(result, query, policy, surviving, location, unknown=False):
    _budget.tick()
    keys(result, ("query_mask", "policy", "classification", "model_count",
                  "positive_model", "negative_model", "realizing_points",
                  "inhabited", "filling_indices"), location)
    exact(result["query_mask"], query, location + ".query_mask")
    exact(result["policy"], policy, location + ".policy")
    exact(result["inhabited"], bool(REGIONS[query]), location + ".inhabited")
    integers(result["filling_indices"], sorted(REGIONS[query]), location + ".fillings")
    if unknown:
        exact(result["classification"], "Unknown", location + ".classification")
        for name in ("model_count", "positive_model", "negative_model"):
            exact(result[name], None, location + "." + name)
        exact(result["realizing_points"], [], location + ".realizing_points")
        return
    positives = tuple(f for f in surviving if query in f)
    negatives = tuple(f for f in surviving if query not in f)
    if not surviving:
        classification = "Inconsistent"
    elif not negatives:
        classification = "ForcedPositive"
    elif not positives:
        classification = "ForcedNegative"
    else:
        classification = "Underdetermined"
    exact(result["classification"], classification, location + ".classification")
    exact(result["model_count"], len(surviving), location + ".model_count")
    for name, choices in (("positive_model", positives), ("negative_model", negatives)):
        expected = list(choices[0]) if choices else None
        actual = result[name]
        if actual is not None:
            require(type(actual) is list and all(type(r) is int for r in actual),
                    location + "." + name + ": invalid family witness")
        exact(actual, expected, location + "." + name)
    witnesses = result["realizing_points"]
    require(type(witnesses) is list and len(witnesses) == len(surviving),
            location + ": missing realization entries")
    for entry, family in zip(witnesses, surviving):
        keys(entry, ("model", "indices"), location + ".realizing_points")
        integers(entry["model"], family, location + ".realization.model")
        integers(entry["indices"], intersection(family), location + ".realization.indices")

def rational_rows(value, expected, location):
    require(type(value) is list and len(value) == len(expected),
            location + ": wrong row count")
    for row, want in zip(value, expected):
        require(type(row) is list and len(row) == len(want),
                location + ": wrong coordinate count")
        for text, number in zip(row, want):
            require(type(text) is str and len(text) <= 64, location + ": rational string required")
            try:
                actual = Fraction(text)
            except (ValueError, ZeroDivisionError):
                raise Rejected(location + ": invalid rational") from None
            require(text == str(actual) and actual == number,
                    location + ": incorrect or noncanonical coordinate")

def reciprocal_output(point, source=True):
    a, b, left, right = point
    require(a > 0 and right > 0, "illegal regular-domain point")
    p, q = (a * left + b, a * right) if source else (left, right)
    # Complex reciprocal through its slope, not the producer's p*p+q*q expression.
    if p == 0:
        r, s = Fraction(0), 1 / q
    else:
        slope = q / p
        scale = p + q * slope
        require(scale != 0, "reciprocal guard violated")
        r, s = -1 / scale, slope / scale
    return (a, b, r, s)

def transport(region, order):
    points = REGIONS[region]
    return mask(frozenset(j for j, original in enumerate(order) if original in points))

def check_geometry(geometry, contract):
    keys(geometry, ("source_fillings", "target_fillings", "source_outputs",
                    "target_outputs", "inverse_fillings", "source_observations",
                    "target_observations", "target_order"), "geometry")
    programs = contract["programs"]
    source = tuple(tuple(Fraction(v) for v in row) for row in programs["fillings"])
    require(len(source) == 4 and all(len(row) == 4 for row in source), "contract carrier changed")
    order = programs["target_order"]
    require(type(order) is list and all(type(i) is int for i in order)
            and sorted(order) == list(range(4)), "contract permutation invalid")
    mapped = tuple((a, b, a*x+b, a*y) for a, b, x, y in source)
    target = tuple(mapped[i] for i in order)
    outputs = tuple(reciprocal_output(point) for point in source)
    target_outputs = tuple(reciprocal_output(point, False) for point in target)
    inverse = tuple((a, b, (p-b)/a, q/a) for a, b, p, q in target)
    require(inverse == tuple(source[i] for i in order), "inverse calculation failed")
    require(target_outputs == tuple(outputs[i] for i in order), "program transport failed")
    for field, rows in (("source_fillings", source), ("target_fillings", target),
                        ("source_outputs", outputs), ("target_outputs", target_outputs),
                        ("inverse_fillings", inverse)):
        rational_rows(geometry[field], rows, "geometry." + field)
    integers(geometry["target_order"], order, "geometry.target_order")
    observations = {}
    for chart, chart_points, chart_outputs in (("source", mapped, outputs),
                                               ("target", target, target_outputs)):
        B, H = set(), set()
        for i, (point, output) in enumerate(zip(chart_points, chart_outputs)):
            _budget.tick()
            p, q = point[2:]
            r, s = output[2:]
            in_B = r*r + (s-Fraction(1, 2))**2 < Fraction(1, 4)
            in_H = s > Fraction(1, 4)
            require(in_B == (q > 1), "B pullback calculation failed")
            require(in_H == (p*p+(q-2)**2 < 4), "H pullback calculation failed")
            if in_B:
                B.add(i)
            if in_H:
                H.add(i)
        observations[chart] = {"B": mask(B), "H": mask(H)}
        keys(geometry[chart + "_observations"], ("B", "H"), "geometry.observations")
        for name in ("B", "H"):
            exact(geometry[chart + "_observations"][name], observations[chart][name],
                  "geometry." + chart + "." + name)
    require(observations["source"] == {"B": 12, "H": 5}, "frozen masks changed")
    for name in ("B", "H"):
        require(transport(observations["source"][name], order)
                == observations["target"][name], "observation permutation failed")
    return source, outputs, order

def check_controls(controls, families, joint, source, outputs):
    keys(controls, ("triangle", "forgotten_parameters", "division_guard",
                   "zero_fuel", "conflicting_assumptions"), "controls")
    triangle = controls["triangle"]
    keys(triangle, ("positive_regions", "individual_filling_indices",
                    "common_filling_indices", "basic_result", "joint_result"), "triangle")
    integers(triangle["positive_regions"], (12, 5, 9), "triangle.regions")
    exact(triangle["individual_filling_indices"], [[2, 3], [0, 2], [0, 3]], "triangle.fillings")
    integers(triangle["common_filling_indices"], (), "triangle.common")
    check_query(triangle["basic_result"], 12, "basic", eligible(families, (12,5,9), ()),
                "triangle.basic")
    check_query(triangle["joint_result"], 12, "joint", eligible(joint, (12,5,9), ()),
                "triangle.joint")
    forgotten = controls["forgotten_parameters"]
    keys(forgotten, ("left_source", "right_source", "left_output", "right_output",
                     "forgotten_output", "distinct_retained_parameters",
                     "marked_point_membership", "descends_after_forgetting"), "forgotten")
    other = (Fraction(2), Fraction(1), Fraction(0), Fraction(1))
    other_output = reciprocal_output(other)
    require(outputs[2][2:] == other_output[2:] and source[2] != other,
            "fixed forgetting collision failed")
    for field, row in (("left_source", source[2]), ("right_source", other),
                       ("left_output", outputs[2]), ("right_output", other_output),
                       ("forgotten_output", outputs[2][2:])):
        rational_rows([forgotten[field]], [row], "forgotten." + field)
    exact(forgotten["distinct_retained_parameters"], True, "forgotten.distinct")
    exact(forgotten["marked_point_membership"], [True, False], "forgotten.membership")
    exact(forgotten["descends_after_forgetting"], False, "forgotten.descent")
    guard = controls["division_guard"]
    keys(guard, ("dividend", "divisor", "tested_y", "cross_products", "distinct_preimages",
                 "guarded_status"), "division_guard")
    exact(guard["dividend"], "0", "division_guard.dividend")
    exact(guard["divisor"], "0", "division_guard.divisor")
    exact(guard["tested_y"], ["0", "1"], "division_guard.tested_y")
    exact(guard["cross_products"], ["0", "0"], "division_guard.products")
    require(Fraction(0)*Fraction(0) == Fraction(0)*Fraction(1), "guard control failed")
    try:
        Fraction(0) / Fraction(0)
    except ZeroDivisionError:
        pass
    else:
        raise Rejected("independent zero-division guard failed")
    exact(guard["distinct_preimages"], True, "division_guard.distinct")
    exact(guard["guarded_status"], "InvalidInput", "division_guard.status")
    check_query(controls["zero_fuel"], 0, "basic", (), "zero_fuel", unknown=True)
    check_query(controls["conflicting_assumptions"], 5, "basic", (), "conflict")

def _verify(evidence):
    _budget.tick()
    keys(evidence, ("schema", "status", "native_status", "bindings", "geometry",
                    "models", "cases", "controls", "fuel"), "evidence")
    exact(evidence["schema"], SCHEMA, "schema")
    exact(evidence["status"], "ExternalExactPass", "status")
    exact(evidence["native_status"], "Unavailable", "native_status")
    contract_bytes = load_bytes(HERE / "contract.json")
    contract = decode_json(contract_bytes)
    exact(contract["schema"], "adva.external-multihole-positivity-contract.v0", "contract.schema")
    require(contract["budget"]["independent_family_candidates"] == 65_536
            and contract["budget"]["independent_fuel"] == MAX_FUEL
            and contract["budget"]["each_child_wall_seconds"] == MAX_WALL,
            "frozen receiver budget changed")
    keys(evidence["bindings"], ("checker_sha256", "contract_sha256"), "bindings")
    exact(evidence["bindings"]["contract_sha256"], digest(contract_bytes), "bindings.contract")
    exact(evidence["bindings"]["checker_sha256"], digest(load_bytes(HERE / "checker.py")),
          "bindings.checker")
    source, outputs, order = check_geometry(evidence["geometry"], contract)
    families = independent_families()
    expected = {chart: {policy: policy_families(families, policy, marked)
                         for policy in POLICIES}
                for chart, marked in (("source", 2), ("target", order.index(2)))}
    require(len(expected["source"]["joint"]) == 4
            and len(expected["source"]["marked"]) == 1, "realizer theorem failed")
    keys(evidence["models"], ("source", "target"), "models")
    for chart, marked in (("source", 2), ("target", order.index(2))):
        entry = evidence["models"][chart]
        keys(entry, (*POLICIES, "marked_index"), "models." + chart)
        exact(entry["marked_index"], marked, "models." + chart + ".marked_index")
        for policy in POLICIES:
            family_list(entry[policy], expected[chart][policy], "models." + chart + "." + policy)
            transported = sorted(tuple(sorted(transport(r, order) for r in f))
                                 for f in expected["source"][policy])
            require(tuple(transported) == expected["target"][policy], "family transport failed")
    cases = evidence["cases"]
    require(type(cases) is list and len(cases) == 24, "case coverage incomplete")
    seen = set()
    declared = {c["name"]: c for c in contract["cases"]}
    require(len(declared) == 4, "contract case count changed")
    for case in cases:
        keys(case, ("name", "policy", "chart", "positive", "negative", "queries"), "case")
        name, policy, chart = case["name"], case["policy"], case["chart"]
        require(type(name) is str and name in declared and policy in POLICIES
                and chart in ("source", "target"), "unknown case")
        identity = (name, policy, chart)
        require(identity not in seen, "duplicate case")
        seen.add(identity)
        positive, negative = declared[name]["positive"], declared[name]["negative"]
        if chart == "target":
            positive = [transport(r, order) for r in positive]
            negative = [transport(r, order) for r in negative]
        positive, negative = sorted(positive), sorted(negative)
        integers(case["positive"], positive, "case.positive")
        integers(case["negative"], negative, "case.negative")
        surviving = eligible(expected[chart][policy], positive, negative)
        queries = case["queries"]
        require(type(queries) is list and len(queries) == 16, "query coverage incomplete")
        for query, result in enumerate(queries):
            check_query(result, query, policy, surviving, "case." + name + ".query")
    require(seen == {(name, policy, chart) for name in declared for policy in POLICIES
                     for chart in ("source", "target")}, "case identities incomplete")
    check_controls(evidence["controls"], families, expected["source"]["joint"], source, outputs)
    fuel = evidence["fuel"]
    keys(fuel, ("limit", "consumed", "remaining"), "fuel")
    require(all(type(fuel[k]) is int for k in fuel), "integer producer fuel required")
    require(fuel["limit"] == contract["budget"]["producer_fuel_per_run"]
            and fuel["consumed"] == 2*256*81 + 2*(4*3*2*16 + 3)*12
            and fuel["remaining"] == fuel["limit"]-fuel["consumed"],
            "producer fuel accounting invalid")
    _budget.tick()
    return {"schema": REPORT_SCHEMA, "status": "Verified", "native_status": "Unavailable",
            "work": _budget.consumed, "family_candidates": _budget.candidates,
            "derived_basic_families": len(families), "derived_joint_families": 4,
            "queries_checked": 384, "cache_hits": _cache_hits,
            "verifier_sha256": digest(load_bytes(Path(__file__).resolve()))}

def verify(evidence):
    """Verify parsed evidence using the shared process fuel/deadline and derived cache."""
    global _budget
    if _budget is None:
        _budget = Budget()
    try:
        return _verify(evidence)
    except Limit as error:
        status, reason = "Unknown", str(error)
    except (Rejected, KeyError, TypeError, ValueError, ZeroDivisionError, OSError,
            RecursionError, UnicodeError) as error:
        status, reason = "Rejected", str(error)
    return {"schema": REPORT_SCHEMA, "status": status, "native_status": "Unavailable",
            "reason": reason, "work": _budget.consumed,
            "family_candidates": _budget.candidates, "cache_hits": _cache_hits}

def main():
    import argparse
    global _budget
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence_path", type=Path)
    parser.add_argument("--fuel", type=int, default=MAX_FUEL)
    parser.add_argument("--wall-seconds", type=float, default=MAX_WALL)
    args = parser.parse_args()
    try:
        _budget = Budget(args.fuel, args.wall_seconds)
        evidence = decode_json(load_bytes(args.evidence_path))
        report = verify(evidence)
    except Limit as error:
        report = {"schema": REPORT_SCHEMA, "status": "Unknown", "reason": str(error), "work": 0}
    except (Rejected, UnicodeError, ValueError, OSError, RecursionError) as error:
        report = {"schema": REPORT_SCHEMA, "status": "Rejected", "reason": str(error), "work": 0}
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return {"Verified": 0, "Rejected": 2, "Unknown": 3}[report["status"]]

if __name__ == "__main__":
    raise SystemExit(main())
